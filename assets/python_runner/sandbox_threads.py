"""Threads for the in-app interpreter.

Pyodide (CPython in WebAssembly) can't start OS threads or processes. This
module emulates them with cooperative "green" threads, enough to learn and
run threading / queue / concurrent.futures / multiprocessing programs:

* A program that mentions these modules is rewritten before it runs: for
  every plain function a generator twin is made (`f.__green__`). In the
  twin, every call goes through `_bytecraft_call`, so a blocking call
  (time.sleep, lock.acquire, queue.get, thread.join, future.result...)
  suspends the thread with `yield` and the scheduler runs another one.
* The main program stays ordinary code. When it blocks, the scheduler runs
  other threads right there (nested) until the wait is over. Code that is
  not rewritten (lambdas, callbacks, comprehensions) blocks the same way.
* Time is virtual: when every thread sleeps, the clock jumps forward
  instead of waiting. Programs see consistent time.time()/monotonic().
* Threads switch only at blocking calls and every 1000 iterations of a
  while loop - there is no parallelism and no GIL timeslicing, so only races
  that cross a blocking call (e.g. time.sleep between read and write) show.
* "Processes" are green threads too: memory is shared, functions must be
  picklable-looking (no lambdas / local functions) as in a real pool.

Loaded by assets/python_runner/worker.js and tool/pyodide/check_content.mjs:
  _bytecraft_compile(source) -> code object (rewritten if needed)
  _bytecraft_threads_reset() before a run, _bytecraft_threads_finish() after
  (waits for non-daemon threads like CPython does at exit).
"""
import ast
import builtins
import collections
import heapq
import itertools
import pickle
import re
import sys
import time as _time
import traceback
import types

# --------------------------------------------------------------- clock
_real_monotonic = _time.monotonic
_real_time = _time.time
_real_perf_counter = _time.perf_counter
_real_sleep = _time.sleep
_offset = 0.0  # seconds the virtual clock is ahead of the real one


def _now():
    return _real_monotonic() + _offset


def _advance_to(moment):
    global _offset
    lag = moment - _now()
    if lag > 0:
        _offset += lag


# ----------------------------------------------------------- scheduler
class _Block:
    """Yielded by a green thread: wait until `ready()` is true or until
    `deadline` (virtual monotonic time) passes."""
    __slots__ = ("ready", "deadline")

    def __init__(self, ready=None, deadline=None):
        self.ready = ready
        self.deadline = deadline


class DeadlockError(RuntimeError):
    """Every thread waits and nobody can wake them: the whole program stops
    (real Python would hang forever)."""


class _Scheduler:
    def __init__(self):
        self.reset()

    def reset(self):
        self.ready = collections.deque()
        self.blocked = []  # (thread, block)
        self.current = None  # Thread being stepped, None = main thread
        self.threads = []  # started, not finished
        self.counter = itertools.count(1)
        self.ident = itertools.count(2)
        self.ticks = 0

    def spawn(self, thread, gen):
        thread._gen = gen
        self.threads.append(thread)
        self.ready.append(thread)

    def _wake(self):
        if not self.blocked:
            return
        now = _now()
        still = []
        for thread, block in self.blocked:
            if (block.ready is not None and block.ready()) or (
                    block.deadline is not None and now >= block.deadline):
                self.ready.append(thread)
            else:
                still.append((thread, block))
        self.blocked = still

    def _step(self, thread):
        previous = self.current
        self.current = thread
        try:
            request = thread._gen.send(None)
        except StopIteration:
            self._finish(thread)
        except SystemExit:
            self._finish(thread)
        except (KeyboardInterrupt, DeadlockError):
            self._finish(thread)
            raise
        except BaseException as error:  # noqa: BLE001 - printed like threading.excepthook
            self._finish(thread)
            _report_thread_error(thread, error)
        else:
            if isinstance(request, _Block):
                self.blocked.append((thread, request))
            else:
                self.ready.append(thread)
        finally:
            self.current = previous

    def _finish(self, thread):
        thread._alive = False
        thread._gen = None
        if thread in self.threads:
            self.threads.remove(thread)

    def pump(self, deadline=None):
        """One step of progress. False when nothing can move before
        `deadline` (deadlock, or only the caller's own wait is left)."""
        self._wake()
        if self.ready:
            self._step(self.ready.popleft())
            return True
        moments = [block.deadline for _, block in self.blocked if block.deadline is not None]
        if deadline is not None:
            moments.append(deadline)
        if moments:
            _advance_to(min(moments))
            self._wake()
            return True
        return False

    def run_until(self, ready, deadline=None):
        """Plain (non-generator) wait: runs other threads here until
        `ready()` or the deadline. Returns ready()."""
        while not ready():
            if deadline is not None and _now() >= deadline:
                return ready()
            if not self.pump(deadline):
                raise DeadlockError(_deadlock_message())
        return True

    def tick(self):
        self.ticks += 1
        return self.ticks % 1000 == 0


_sched = _Scheduler()


def _deadlock_message():
    waiting = [t.name for t, _ in _sched.blocked]
    text = ("Взаимная блокировка: все потоки ждут, и разбудить их некому"
            + (f" (ждут: {', '.join(waiting)})." if waiting else "."))
    if _sched.current is not None:
        text += (" Во встроенном Python потоки эмулируются: поток, который ждёт внутри"
                 " включения, генератора или функции с декоратором, не может уступить ход.")
    else:
        text += " В обычном Python программа зависла бы здесь навсегда."
    return text


def _wait(ready, deadline=None):
    """Plain-context wait used by the non-generator API."""
    return _sched.run_until(ready, deadline)


def _gwait(ready, deadline=None):
    """Green-context wait: generator, use with `yield from`."""
    while not ready():
        if deadline is not None and _now() >= deadline:
            return ready()
        yield _Block(ready, deadline)
    return True


def _deadline(timeout):
    if timeout is None or timeout < 0:
        return None
    return _now() + timeout


import weakref, functools
_GREENS = weakref.WeakKeyDictionary()  # plain function -> green twin (not copied by functools.wraps)


def _green(plain_method, green_method):
    _GREENS[plain_method] = green_method
    return plain_method


def _report_thread_error(thread, error):
    import threading
    hook = threading.excepthook
    if hook is not _ORIGINAL_EXCEPTHOOK:
        hook(threading.ExceptHookArgs((type(error), error, error.__traceback__, thread)))
        return
    _print_thread_error(thread, error)


def _print_thread_error(thread, error):
    tb = error.__traceback__
    frames = [f for f in traceback.extract_tb(tb) if f.filename == "main.py"]
    header = f"Process {thread.name}:\n" if isinstance(thread, _Process) else f"Exception in thread {thread.name}:\n"
    lines = [header, "Traceback (most recent call last):\n"]
    lines += traceback.format_list(frames)
    lines += traceback.format_exception_only(type(error), error)
    sys.stderr.write("".join(lines))


# ----------------------------------------------------- calls from green code
def _green_of(func):
    if isinstance(func, functools.partial):
        green = _green_of(func.func)
        if green is None:
            return None
        args, keywords = func.args, func.keywords
        return lambda *a, **k: green(*args, *a, **{**keywords, **k})
    if isinstance(func, types.MethodType):
        green = _GREENS.get(func.__func__)
        if green is None:
            return None
        owner = func.__self__
        return lambda *args, **kwargs: green(owner, *args, **kwargs)
    if isinstance(func, types.FunctionType):
        return _GREENS.get(func)
    return None


class _Done:
    """Already-computed result for `yield from`: no generator frame, and a
    StopIteration from the plain call reaches the caller's frame as is."""
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration(self.value)


def _bytecraft_call(func, /, *args, **kwargs):
    green = _green_of(func)
    if green is None:
        return _Done(func(*args, **kwargs))
    return green(*args, **kwargs)


def _bytecraft_enter(manager):
    cls = type(manager)
    if cls is Lock and not manager._locked:  # fast path: free lock
        return _Done(manager._take())
    enter = cls.__enter__.__get__(manager)
    green = _green_of(enter)
    if green is None:
        return _Done(enter())
    return green()


def _bytecraft_exit(manager, kind, value, tb):
    exit_ = type(manager).__exit__.__get__(manager)
    green = _green_of(exit_)
    if green is None:
        return _Done(exit_(kind, value, tb))
    return green(kind, value, tb)


def _bytecraft_exit_error(manager, error):
    return _bytecraft_exit(manager, type(error), error, error.__traceback__)


def _bytecraft_lambda(plain, green):
    _GREENS[plain] = green
    return plain


def _bytecraft_link(func, green):
    try:
        green.__code__ = green.__code__.replace(co_name=func.__code__.co_name,
                                                co_qualname=func.__code__.co_qualname)
    except (AttributeError, ValueError):
        pass
    green.__name__ = func.__name__
    green.__qualname__ = func.__qualname__
    green.__defaults__ = func.__defaults__
    green.__kwdefaults__ = func.__kwdefaults__
    _GREENS[func] = green


def _bytecraft_tick():
    return _sched.tick()


def _bytecraft_poll():
    if _sched.tick():
        _sched._wake()
        if _sched.ready:
            _sched._step(_sched.ready.popleft())


# ------------------------------------------------------------- rewriting
_FRAME_HELPERS = {"_getframe", "currentframe", "stack", "getouterframes"}
_UNWRAPPED = {"super", "locals", "globals", "vars", "eval", "exec", "dir", "breakpoint",
              "_bytecraft_lambda", "_bytecraft_call", "_bytecraft_tick", "_bytecraft_poll"}
_SCOPES = (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
           ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _own_nodes(node):
    stack = list(ast.iter_child_nodes(node))
    while stack:
        child = stack.pop()
        yield child
        if not isinstance(child, _SCOPES):
            stack.extend(ast.iter_child_nodes(child))


def _is_generator(func):
    return any(isinstance(n, (ast.Yield, ast.YieldFrom, ast.Await)) for n in _own_nodes(func))


class _WrapCalls(ast.NodeTransformer):
    """Inside a green twin: f(x) -> (yield from _bytecraft_call(f, x))."""

    def generic_visit(self, node):
        if isinstance(node, _SCOPES):
            return node
        return super().generic_visit(node)

    def visit_Lambda(self, node):
        return node

    def visit_ListComp(self, node):
        return node

    visit_SetComp = visit_DictComp = visit_GeneratorExp = visit_ListComp

    def visit_Call(self, node):
        node = super().generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in _UNWRAPPED:
            return node
        if isinstance(node.func, ast.Attribute) and node.func.attr in _FRAME_HELPERS:
            return node
        call = ast.Call(func=ast.Name("_bytecraft_call", ast.Load()),
                        args=[node.func, *node.args], keywords=node.keywords)
        return ast.copy_location(ast.YieldFrom(ast.copy_location(call, node)), node)


def _tick_stmt(green, where):
    if green:
        stmt = ast.If(test=ast.Call(ast.Name("_bytecraft_tick", ast.Load()), [], []),
                      body=[ast.Expr(ast.Yield(None))], orelse=[])
    else:
        stmt = ast.Expr(ast.Call(ast.Name("_bytecraft_poll", ast.Load()), [], []))
    return ast.copy_location(stmt, where)


def _process_block(stmts, green):
    out = []
    for stmt in stmts:
        out.extend(_process_stmt(stmt, green))
    return out


_with_counter = itertools.count()


def _green_with(stmt):
    """with A as x, B: body -> manual protocol with yield-from enter/exit,
    so a thread waiting for a lock in `with` can give way."""
    body = stmt.body
    for item in reversed(stmt.items):
        n = next(_with_counter)
        manager, ok, error = f"_bcm{n}", f"_bcok{n}", f"_bce{n}"
        code = f"""
{manager} = MANAGER
TARGET = yield from _bytecraft_enter({manager})
{ok} = True
try:
    pass
except BaseException as {error}:
    {ok} = False
    if not (yield from _bytecraft_exit_error({manager}, {error})):
        raise
finally:
    if {ok}:
        yield from _bytecraft_exit({manager}, None, None, None)
"""
        nodes = ast.parse(code).body
        for node in nodes:
            for child in ast.walk(node):
                if "lineno" in child._attributes:
                    ast.copy_location(child, stmt)
        nodes[0].value = _wrap_expr(item.context_expr)
        if item.optional_vars is not None:
            nodes[1].targets = [item.optional_vars]
        else:
            nodes[1] = ast.copy_location(ast.Expr(nodes[1].value), stmt)
        nodes[3].body = body
        body = nodes
    return body


def _process_stmt(stmt, green):
    if isinstance(stmt, ast.With) and green:
        stmt.body = _process_block(stmt.body, True)
        return _green_with(stmt)
    if isinstance(stmt, ast.FunctionDef):
        return _process_def(stmt)
    if isinstance(stmt, ast.AsyncFunctionDef):
        stmt.body = _process_block(stmt.body, False)
        return [stmt]
    if isinstance(stmt, ast.ClassDef):
        stmt.body = _process_block(stmt.body, False)
        if green:
            stmt.bases = [_wrap_expr(b) for b in stmt.bases]
        return [stmt]
    # Bodies of compound statements.
    for field in ("body", "orelse", "finalbody"):
        block = getattr(stmt, field, None)
        if isinstance(block, list) and block and isinstance(block[0], ast.stmt):
            setattr(stmt, field, _process_block(block, green))
    if isinstance(stmt, (ast.Try, ast.TryStar)):
        for handler in stmt.handlers:
            handler.body = _process_block(handler.body, green)
    if isinstance(stmt, ast.Match):
        for case in stmt.cases:
            case.body = _process_block(case.body, green)
    if isinstance(stmt, ast.While):
        stmt.body.insert(0, _tick_stmt(green, stmt))
    if green:
        stmt = _wrap_header(stmt)
    return [stmt]


def _wrap_expr(expr):
    return _WrapCalls().visit(expr)


def _wrap_header(stmt):
    """Wraps calls in the statement itself, not in its nested blocks."""
    saved = {}
    for field in ("body", "orelse", "finalbody", "handlers", "cases"):
        if hasattr(stmt, field):
            saved[field] = getattr(stmt, field)
            setattr(stmt, field, [])
    stmt = _WrapCalls().visit(stmt)
    for field, value in saved.items():
        setattr(stmt, field, value)
    return stmt


def _process_def(func):
    import copy
    eligible = not _is_generator(func)
    twin = copy.deepcopy(func) if eligible else None
    func.body = _process_block(func.body, False)
    if not eligible:
        return [func]
    # Decorators are evaluated first (as in CPython) and applied after the
    # twin is linked, so the undecorated function gets a green twin too.
    pre, post = [], []
    if func.decorator_list:
        n = next(_with_counter)
        temps = [f"_bcdec{n}_{i}" for i in range(len(func.decorator_list))]
        for temp, dec in zip(temps, func.decorator_list):
            pre.append(ast.Assign([ast.Name(temp, ast.Store())], dec))
        value = ast.Name(func.name, ast.Load())
        for temp in reversed(temps):
            value = ast.Call(ast.Name(temp, ast.Load()), [value], [])
        post = [ast.Assign([ast.Name(func.name, ast.Store())], value),
                ast.Delete([ast.Name(t, ast.Del()) for t in temps])]
        func.decorator_list = []
        twin.decorator_list = []
        for node in pre + post:
            ast.copy_location(node, func)
    name = "_bcg_" + func.name
    twin.name = name
    # Defaults are copied from the original by _bytecraft_link: evaluating
    # them twice would repeat their side effects.
    twin.args.defaults = [ast.copy_location(ast.Constant(None), d) for d in twin.args.defaults]
    twin.args.kw_defaults = [None if d is None else ast.copy_location(ast.Constant(None), d)
                             for d in twin.args.kw_defaults]
    twin.body = _process_block(twin.body, True)
    never = ast.If(test=ast.Constant(False), body=[ast.Expr(ast.Yield(None))], orelse=[])
    twin.body.append(ast.copy_location(never, func))
    link = ast.Expr(ast.Call(ast.Name("_bytecraft_link", ast.Load()),
                             [ast.Name(func.name, ast.Load()), ast.Name(name, ast.Load())], []))
    delete = ast.Delete([ast.Name(name, ast.Del())])
    for node in (link, delete):
        ast.copy_location(node, func)
        node.lineno = node.end_lineno = func.end_lineno or func.lineno
    return [*pre, func, twin, link, delete, *post]


class _Lambdas(ast.NodeTransformer):
    """lambda args: expr -> _bytecraft_lambda(lambda args: expr,
    lambda args: (yield from ...)) when expr calls something."""

    def visit_Lambda(self, node):
        import copy
        self.generic_visit(node)
        if any(isinstance(n, (ast.Yield, ast.YieldFrom, ast.Await)) for n in ast.walk(node.body)):
            return node
        wrapped = _wrap_expr(copy.deepcopy(node.body))
        if not any(isinstance(n, ast.YieldFrom) for n in ast.walk(wrapped)):
            return node
        green = ast.Lambda(args=copy.deepcopy(node.args), body=wrapped)
        call = ast.Call(ast.Name("_bytecraft_lambda", ast.Load()), [node, green], [])
        return ast.copy_location(call, node)


_USES_THREADS = re.compile(r"\b(threading|concurrent|queue|multiprocessing|_thread|to_thread|run_in_executor)\b")


def _bytecraft_compile(source, filename="main.py"):
    if not _USES_THREADS.search(source):
        return compile(source, filename, "exec")
    try:
        tree = ast.parse(source, filename)
    except SyntaxError:
        return compile(source, filename, "exec")  # raises the usual error
    tree = _Lambdas().visit(tree)
    tree.body = _process_block(tree.body, False)
    ast.fix_missing_locations(tree)
    return compile(tree, filename, "exec")


# ------------------------------------------------------------ primitives
class _MainThread:
    name = "MainThread"
    daemon = False
    ident = 1
    native_id = 1

    def is_alive(self):
        return True

    def join(self, timeout=None):
        raise RuntimeError("cannot join current thread")

    def __repr__(self):
        return "<_MainThread(MainThread, started 1)>"


_MAIN = _MainThread()


def current_thread():
    return _sched.current or _MAIN


def main_thread():
    return _MAIN


def get_ident():
    return current_thread().ident


get_native_id = get_ident


def active_count():
    return 1 + len(_sched.threads)


def enumerate_threads():
    return [_MAIN, *_sched.threads]


class Lock:
    def __init__(self):
        self._owner = None
        self._locked = False

    def locked(self):
        return self._locked

    def _take(self):
        self._locked = True
        self._owner = current_thread()
        return True

    def acquire(self, blocking=True, timeout=-1):
        if not self._locked:
            return self._take()
        if not blocking:
            return False
        if _wait(lambda: not self._locked, _deadline(timeout)):
            return self._take()
        return False

    def _acquire_green(self, blocking=True, timeout=-1):
        if not self._locked:
            return self._take()
        if not blocking:
            return False
        if (yield from _gwait(lambda: not self._locked, _deadline(timeout))):
            return self._take()
        return False

    _green(acquire, _acquire_green)

    def release(self):
        if not self._locked:
            raise RuntimeError("release unlocked lock")
        self._locked = False
        self._owner = None

    def __enter__(self):
        return self.acquire()

    def _enter_green(self):
        return (yield from self._acquire_green())

    _green(__enter__, _enter_green)

    def __exit__(self, *exc):
        self.release()

    def __repr__(self):
        return f"<{'locked' if self._locked else 'unlocked'} {type(self).__module__}.Lock object>"


class RLock:
    def __init__(self):
        self._owner = None
        self._count = 0

    def _free_for_me(self):
        return self._count == 0 or self._owner is current_thread()

    def _take(self):
        self._owner = current_thread()
        self._count += 1
        return True

    def acquire(self, blocking=True, timeout=-1):
        if self._free_for_me():
            return self._take()
        if not blocking:
            return False
        if _wait(lambda: self._count == 0, _deadline(timeout)):
            return self._take()
        return False

    def _acquire_green(self, blocking=True, timeout=-1):
        if self._free_for_me():
            return self._take()
        if not blocking:
            return False
        if (yield from _gwait(lambda: self._count == 0, _deadline(timeout))):
            return self._take()
        return False

    _green(acquire, _acquire_green)

    def release(self):
        if self._count == 0 or self._owner is not current_thread():
            raise RuntimeError("cannot release un-acquired lock")
        self._count -= 1
        if self._count == 0:
            self._owner = None

    def __enter__(self):
        return self.acquire()

    def _enter_green(self):
        return (yield from self._acquire_green())

    _green(__enter__, _enter_green)

    def __exit__(self, *exc):
        self.release()


class Condition:
    def __init__(self, lock=None):
        self._lock = lock if lock is not None else RLock()
        self._waiters = []  # list of one-element lists [notified]
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    def __enter__(self):
        return self._lock.__enter__()

    def _enter_green(self):
        return (yield from _bytecraft_enter(self._lock))

    _green(__enter__, _enter_green)

    def __exit__(self, *exc):
        return self._lock.__exit__(*exc)

    def _release_all(self):
        if isinstance(self._lock, RLock):
            saved = self._lock._count
            self._lock._count = 0
            self._lock._owner = None
            return saved
        self._lock.release()
        return 1

    def _restore(self, saved):
        if isinstance(self._lock, RLock):
            self._lock._owner = current_thread()
            self._lock._count = saved

    def _is_owned(self):
        if isinstance(self._lock, RLock):
            return self._lock._count > 0 and self._lock._owner is current_thread()
        return self._lock._locked

    def _check_owned(self, what):
        if not self._is_owned():
            raise RuntimeError(f"cannot {what} on un-acquired lock")

    def _lock_free(self):
        return (self._lock._count == 0) if isinstance(self._lock, RLock) else not self._lock._locked

    def wait(self, timeout=None):
        self._check_owned("wait")
        slot = [False]
        self._waiters.append(slot)
        saved = self._release_all()
        try:
            got = _wait(lambda: slot[0], _deadline(timeout))
        finally:
            if slot in self._waiters:
                self._waiters.remove(slot)
            _wait(self._lock_free)
            if isinstance(self._lock, RLock):
                self._restore(saved)
            else:
                self._lock._take()
        return got

    def _wait_green(self, timeout=None):
        self._check_owned("wait")
        slot = [False]
        self._waiters.append(slot)
        saved = self._release_all()
        try:
            got = yield from _gwait(lambda: slot[0], _deadline(timeout))
        finally:
            if slot in self._waiters:
                self._waiters.remove(slot)
        yield from _gwait(self._lock_free)
        if isinstance(self._lock, RLock):
            self._restore(saved)
        else:
            self._lock._take()
        return got

    _green(wait, _wait_green)

    def wait_for(self, predicate, timeout=None):
        deadline = _deadline(timeout)
        result = predicate()
        while not result:
            left = None if deadline is None else deadline - _now()
            if left is not None and left <= 0:
                break
            self.wait(left)
            result = predicate()
        return result

    def _wait_for_green(self, predicate, timeout=None):
        deadline = _deadline(timeout)
        result = predicate()
        while not result:
            left = None if deadline is None else deadline - _now()
            if left is not None and left <= 0:
                break
            yield from self._wait_green(left)
            result = predicate()
        return result

    _green(wait_for, _wait_for_green)

    def notify(self, n=1):
        self._check_owned("notify")
        for slot in self._waiters[:n]:
            slot[0] = True
        del self._waiters[:n]

    def notify_all(self):
        self.notify(len(self._waiters))

    notifyAll = notify_all


class Semaphore:
    def __init__(self, value=1):
        if value < 0:
            raise ValueError("semaphore initial value must be >= 0")
        self._value = value

    def acquire(self, blocking=True, timeout=None):
        if self._value > 0:
            self._value -= 1
            return True
        if not blocking:
            return False
        if _wait(lambda: self._value > 0, _deadline(timeout)):
            self._value -= 1
            return True
        return False

    def _acquire_green(self, blocking=True, timeout=None):
        if self._value > 0:
            self._value -= 1
            return True
        if not blocking:
            return False
        if (yield from _gwait(lambda: self._value > 0, _deadline(timeout))):
            self._value -= 1
            return True
        return False

    _green(acquire, _acquire_green)

    def release(self, n=1):
        self._value += n

    def __enter__(self):
        return self.acquire()

    def _enter_green(self):
        return (yield from self._acquire_green())

    _green(__enter__, _enter_green)

    def __exit__(self, *exc):
        self.release()


class BoundedSemaphore(Semaphore):
    def __init__(self, value=1):
        super().__init__(value)
        self._initial = value

    def release(self, n=1):
        if self._value + n > self._initial:
            raise ValueError("Semaphore released too many times")
        self._value += n


class Event:
    def __init__(self):
        self._flag = False

    def is_set(self):
        return self._flag

    isSet = is_set

    def set(self):
        self._flag = True

    def clear(self):
        self._flag = False

    def wait(self, timeout=None):
        return _wait(lambda: self._flag, _deadline(timeout))

    def _wait_green(self, timeout=None):
        return (yield from _gwait(lambda: self._flag, _deadline(timeout)))

    _green(wait, _wait_green)


class BrokenBarrierError(RuntimeError):
    pass


class Barrier:
    def __init__(self, parties, action=None, timeout=None):
        self.parties = parties
        self._action = action
        self._timeout = timeout
        self._count = 0
        self._generation = 0
        self.broken = False
        self._reset_generations = set()

    @property
    def n_waiting(self):
        return self._count

    def _arrive(self):
        if self.broken:
            raise BrokenBarrierError
        index = self._count
        self._count += 1
        generation = self._generation
        if self._count == self.parties:
            if self._action:
                try:
                    self._action()
                except BaseException:
                    self.broken = True
                    raise
            self._count = 0
            self._generation += 1
        return index, generation

    def wait(self, timeout=None):
        index, generation = self._arrive()
        timeout = self._timeout if timeout is None else timeout
        if not _wait(lambda: self._generation != generation or self.broken, _deadline(timeout)):
            self.abort()
        if generation in self._reset_generations or (self.broken and self._generation == generation):
            raise BrokenBarrierError
        return index

    def _wait_green(self, timeout=None):
        index, generation = self._arrive()
        timeout = self._timeout if timeout is None else timeout
        if not (yield from _gwait(lambda: self._generation != generation or self.broken, _deadline(timeout))):
            self.abort()
        if generation in self._reset_generations or (self.broken and self._generation == generation):
            raise BrokenBarrierError
        return index

    _green(wait, _wait_green)

    def abort(self):
        self.broken = True

    def reset(self):
        if self._count:
            self._reset_generations.add(self._generation)
        self.broken = False
        self._count = 0
        self._generation += 1


class local:
    """Per-thread attributes. As in CPython, a subclass __init__ runs again
    (with the same arguments) the first time each thread touches it."""

    def __new__(cls, *args, **kwargs):
        if (args or kwargs) and cls.__init__ is object.__init__:
            raise TypeError("Initialization arguments are not supported")
        self = object.__new__(cls)
        data = weakref.WeakKeyDictionary()
        data[current_thread()] = {}
        object.__setattr__(self, "_bytecraft_local", (data, args, kwargs))
        return self

    def _dict(self):
        data, args, kwargs = object.__getattribute__(self, "_bytecraft_local")
        thread = current_thread()
        values = data.get(thread)
        if values is None:
            values = data[thread] = {}
            type(self).__init__(self, *args, **kwargs)
        return values

    def __getattribute__(self, name):
        if name in ("_dict", "__class__"):
            return object.__getattribute__(self, name)
        values = object.__getattribute__(self, "_dict")()
        if name == "__dict__":
            return values
        if name in values:
            return values[name]
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        object.__getattribute__(self, "_dict")()[name] = value

    def __delattr__(self, name):
        try:
            del object.__getattribute__(self, "_dict")()[name]
        except KeyError:
            raise AttributeError(name) from None


_thread_counter = itertools.count(1)


class Thread:
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        self._target = target
        self._args = args
        self._kwargs = dict(kwargs or {})
        if name is None:
            name = f"Thread-{next(_thread_counter)}"
            if target is not None:
                name += f" ({getattr(target, '__name__', 'target')})"
        self._name = str(name)
        self._daemon = current_thread().daemon if daemon is None else bool(daemon)
        self._started = False
        self._alive = False
        self._ident = None
        self._gen = None

    name = property(lambda self: self._name, lambda self, value: setattr(self, "_name", str(value)))
    ident = property(lambda self: self._ident)
    native_id = ident

    @property
    def daemon(self):
        return self._daemon

    @daemon.setter
    def daemon(self, value):
        if self._started:
            raise RuntimeError("cannot set daemon status of active thread")
        self._daemon = bool(value)

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = str(name)

    def isDaemon(self):
        return self._daemon

    def setDaemon(self, value):
        self.daemon = value

    def start(self):
        if self._started:
            raise RuntimeError("threads can only be started once")
        self._started = True
        self._alive = True
        self._ident = next(_sched.ident)
        _sched.spawn(self, self._bootstrap())
        if _sched.current is None:
            # Like CPython: the new thread runs right away until it blocks.
            _sched.ready.remove(self)
            _sched._step(self)

    def _start_green(self):
        self.start()
        yield  # let the new thread go first (it is ahead in the ready queue)

    _green(start, _start_green)

    def _bootstrap(self):
        run = self.run
        green = _green_of(run)
        if green is not None:
            yield from green()
        else:
            run()
        if False:
            yield

    def run(self):
        try:
            if self._target is not None:
                self._target(*self._args, **self._kwargs)
        finally:
            del self._target, self._args, self._kwargs

    def _run_green(self):
        try:
            if self._target is not None:
                yield from _bytecraft_call(self._target, *self._args, **self._kwargs)
        finally:
            del self._target, self._args, self._kwargs

    _green(run, _run_green)

    def is_alive(self):
        return self._alive

    def join(self, timeout=None):
        if not self._started:
            raise RuntimeError("cannot join thread before it is started")
        if self is current_thread():
            raise RuntimeError("cannot join current thread")
        _wait(lambda: not self._alive, _deadline(timeout))

    def _join_green(self, timeout=None):
        if not self._started:
            raise RuntimeError("cannot join thread before it is started")
        if self is current_thread():
            raise RuntimeError("cannot join current thread")
        yield from _gwait(lambda: not self._alive, _deadline(timeout))

    _green(join, _join_green)

    def __repr__(self):
        status = "started" if self._alive else ("stopped" if self._started else "initial")
        if self._daemon:
            status += " daemon"
        if self._ident is not None:
            status += f" {self._ident}"
        return f"<{type(self).__name__}({self._name}, {status})>"


class Timer(Thread):
    def __init__(self, interval, function, args=None, kwargs=None):
        super().__init__()
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        self.finished.set()

    def run(self):
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()

    def _run_green(self):
        yield from self.finished._wait_green(self.interval)
        if not self.finished.is_set():
            yield from _bytecraft_call(self.function, *self.args, **self.kwargs)
        self.finished.set()

    _green(run, _run_green)


def _sleep(seconds):
    if seconds < 0:
        raise ValueError("sleep length must be non-negative")
    _wait(lambda: False, _now() + seconds)


def _sleep_green(seconds):
    if seconds < 0:
        raise ValueError("sleep length must be non-negative")
    yield _Block(None, _now() + seconds)


_green(_sleep, _sleep_green)


# ----------------------------------------------------------------- queue
import queue as _queue_module  # noqa: E402

Empty = _queue_module.Empty
Full = _queue_module.Full


class Queue:
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)
        self.unfinished_tasks = 0
        self.is_shutdown = False
        self.mutex = RLock()
        self.not_empty = Condition(self.mutex)
        self.not_full = Condition(self.mutex)
        self.all_tasks_done = Condition(self.mutex)

    @staticmethod
    def _check_timeout(timeout):
        if timeout is not None and timeout < 0:
            raise ValueError("'timeout' must be a non-negative number")

    def _init(self, maxsize):
        self.queue = collections.deque()

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.popleft()

    def qsize(self):
        return self._qsize()

    def empty(self):
        return not self._qsize()

    def full(self):
        return 0 < self.maxsize <= self._qsize()

    def _has_room(self):
        return not (0 < self.maxsize <= self._qsize())

    def _do_put(self, item):
        self._put(item)
        self.unfinished_tasks += 1

    def put(self, item, block=True, timeout=None):
        self._check_timeout(timeout)
        if not self._has_room():
            if not block or not _wait(self._has_room, _deadline(timeout)):
                raise Full
        self._do_put(item)

    def _put_green(self, item, block=True, timeout=None):
        self._check_timeout(timeout)
        if not self._has_room():
            if not block or not (yield from _gwait(self._has_room, _deadline(timeout))):
                raise Full
        self._do_put(item)

    _green(put, _put_green)

    def get(self, block=True, timeout=None):
        self._check_timeout(timeout)
        if not self._qsize():
            if not block or not _wait(self._qsize, _deadline(timeout)):
                raise Empty
        return self._get()

    def _get_green(self, block=True, timeout=None):
        self._check_timeout(timeout)
        if not self._qsize():
            if not block or not (yield from _gwait(self._qsize, _deadline(timeout))):
                raise Empty
        return self._get()

    _green(get, _get_green)

    def put_nowait(self, item):
        return self.put(item, block=False)

    def get_nowait(self):
        return self.get(block=False)

    def task_done(self):
        if self.unfinished_tasks <= 0:
            raise ValueError("task_done() called too many times")
        self.unfinished_tasks -= 1

    def join(self):
        _wait(lambda: self.unfinished_tasks == 0)

    def _join_green(self):
        yield from _gwait(lambda: self.unfinished_tasks == 0)

    _green(join, _join_green)


class LifoQueue(Queue):
    def _init(self, maxsize):
        self.queue = []

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.pop()


class PriorityQueue(Queue):
    def _init(self, maxsize):
        self.queue = []

    def _put(self, item):
        heapq.heappush(self.queue, item)

    def _get(self):
        return heapq.heappop(self.queue)


class SimpleQueue(Queue):
    def __init__(self):
        super().__init__(0)

    def task_done(self):
        raise AttributeError("'SimpleQueue' object has no attribute 'task_done'")


# --------------------------------------------------------------- futures
import concurrent.futures as _cf  # noqa: E402

_completion = itertools.count()


class Future:
    def __init__(self):
        self._state = "PENDING"
        self._result = None
        self._exception = None
        self._callbacks = []
        self._order = None

    def __repr__(self):
        return f"<Future at {id(self):#x} state={self._state.lower()}>"

    def cancel(self):
        if self._state in ("RUNNING", "FINISHED"):
            return False
        if self._state != "CANCELLED":
            self._state = "CANCELLED"
            self._done()
        return True

    def cancelled(self):
        return self._state == "CANCELLED"

    def running(self):
        return self._state == "RUNNING"

    def done(self):
        return self._state in ("CANCELLED", "FINISHED")

    def set_running_or_notify_cancel(self):
        if self._state == "CANCELLED":
            return False
        self._state = "RUNNING"
        return True

    def set_result(self, result):
        self._result = result
        self._state = "FINISHED"
        self._done()

    def set_exception(self, exception):
        self._exception = exception
        self._state = "FINISHED"
        self._done()

    def _done(self):
        self._order = next(_completion)
        for callback in self._callbacks:
            try:
                callback(self)
            except Exception:  # noqa: BLE001
                traceback.print_exc()

    def add_done_callback(self, fn):
        if self.done():
            fn(self)
        else:
            self._callbacks.append(fn)

    def _outcome(self):
        if self._state == "CANCELLED":
            raise _cf.CancelledError()
        if self._exception is not None:
            raise self._exception
        return self._result

    def result(self, timeout=None):
        if not _wait(self.done, _deadline(timeout)):
            raise TimeoutError()
        return self._outcome()

    def _result_green(self, timeout=None):
        if not (yield from _gwait(self.done, _deadline(timeout))):
            raise TimeoutError()
        return self._outcome()

    _green(result, _result_green)

    def exception(self, timeout=None):
        if not _wait(self.done, _deadline(timeout)):
            raise TimeoutError()
        if self._state == "CANCELLED":
            raise _cf.CancelledError()
        return self._exception

    def _exception_green(self, timeout=None):
        if not (yield from _gwait(self.done, _deadline(timeout))):
            raise TimeoutError()
        if self._state == "CANCELLED":
            raise _cf.CancelledError()
        return self._exception

    _green(exception, _exception_green)


def _run_work(future, fn, args, kwargs):
    if not future.set_running_or_notify_cancel():
        return
    try:
        result = yield from _bytecraft_call(fn, *args, **kwargs)
    except BaseException as error:  # noqa: BLE001
        future.set_exception(error)
    else:
        future.set_result(result)


class ThreadPoolExecutor:
    _counter = itertools.count()

    def __init__(self, max_workers=None, thread_name_prefix="", initializer=None, initargs=()):
        if max_workers is None:
            import os
            max_workers = min(32, (os.cpu_count() or 1) + 4)
        if max_workers <= 0:
            raise ValueError("max_workers must be greater than 0")
        self._max_workers = max_workers
        self._prefix = thread_name_prefix or f"ThreadPoolExecutor-{next(self._counter)}"
        self._initializer = initializer
        self._initargs = initargs
        self._work = collections.deque()
        self._workers = []
        self._idle = 0
        self._shutdown = False
        _executors.append(self)

    def _check(self, fn, args, kwargs):
        pass

    def submit(self, fn, /, *args, **kwargs):
        if self._shutdown:
            raise RuntimeError("cannot schedule new futures after shutdown")
        future = Future()
        try:
            self._check(fn, args, kwargs)
        except Exception as error:  # noqa: BLE001 - reported through the future
            future.set_exception(error)
            return future
        self._work.append((future, fn, args, kwargs))
        if self._idle == 0 and len(self._workers) < self._max_workers:
            worker = Thread(name=f"{self._prefix}_{len(self._workers)}", target=None, daemon=True)
            worker._bytecraft_executor = self
            worker._bootstrap = types.MethodType(_worker_loop, worker)
            self._workers.append(worker)
            worker.start()
        return future

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        deadline = _deadline(timeout)
        futures = [self.submit(fn, *args) for args in zip(*iterables)]

        def results():
            try:
                futures.reverse()
                while futures:
                    left = None if deadline is None else deadline - _now()
                    yield futures.pop().result(left)
            finally:
                for future in futures:
                    future.cancel()
        return results()

    def shutdown(self, wait=True, *, cancel_futures=False):
        self._shutdown = True
        if cancel_futures:
            while self._work:
                self._work.popleft()[0].cancel()
        if wait:
            for worker in list(self._workers):
                worker.join()

    def _shutdown_green(self, wait=True, *, cancel_futures=False):
        self._shutdown = True
        if cancel_futures:
            while self._work:
                self._work.popleft()[0].cancel()
        if wait:
            for worker in list(self._workers):
                yield from worker._join_green()

    _green(shutdown, _shutdown_green)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.shutdown(wait=True)
        return False

    def _exit_green(self, *exc):
        yield from self._shutdown_green(wait=True)
        return False

    _green(__exit__, _exit_green)


_executors = []


def _worker_loop(self):
    executor = self._bytecraft_executor
    if executor._initializer is not None:
        yield from _bytecraft_call(executor._initializer, *executor._initargs)
    while True:
        if executor._work:
            future, fn, args, kwargs = executor._work.popleft()
            yield from _run_work(future, fn, args, kwargs)
            continue
        if executor._shutdown:
            return
        executor._idle += 1
        try:
            yield from _gwait(lambda: bool(executor._work) or executor._shutdown)
        finally:
            executor._idle -= 1


def _check_picklable(obj, what):
    qualname = getattr(obj, "__qualname__", "")
    if "<lambda>" in qualname or "<locals>" in qualname:
        raise pickle.PicklingError(f"Can't pickle {obj!r}: it's not found as {getattr(obj, '__module__', '?')}.{qualname}")


class ProcessPoolExecutor(ThreadPoolExecutor):
    """Green threads that refuse what a real process pool can't send to
    another process (lambdas and local functions)."""

    def __init__(self, max_workers=None, mp_context=None, initializer=None, initargs=(), *,
                 max_tasks_per_child=None):
        super().__init__(max_workers or 4, "ProcessPoolExecutor", initializer, initargs)

    def _check(self, fn, args, kwargs):
        _check_picklable(fn, "function")
        for value in (*args, *kwargs.values()):
            if callable(value):
                _check_picklable(value, "argument")

    def map(self, fn, *iterables, timeout=None, chunksize=1):
        return super().map(fn, *iterables, timeout=timeout)


def as_completed(fs, timeout=None):
    deadline = _deadline(timeout)
    pending = set(fs)
    total = len(pending)
    while pending:
        if not _wait(lambda: any(f.done() for f in pending), deadline):
            raise TimeoutError(f"{len(pending)} (of {total}) futures unfinished")
        done = sorted((f for f in pending if f.done()), key=lambda f: f._order)
        for future in done:
            pending.discard(future)
            yield future


FIRST_COMPLETED = _cf.FIRST_COMPLETED
FIRST_EXCEPTION = _cf.FIRST_EXCEPTION
ALL_COMPLETED = _cf.ALL_COMPLETED
DoneAndNotDoneFutures = collections.namedtuple("DoneAndNotDoneFutures", "done not_done")


def _wait_condition(fs, return_when):
    def ready():
        done = [f for f in fs if f.done()]
        if return_when == FIRST_COMPLETED:
            return bool(done)
        if return_when == FIRST_EXCEPTION and any(
                f._exception is not None and not f.cancelled() for f in done):
            return True
        return len(done) == len(fs)
    return ready


def wait(fs, timeout=None, return_when=ALL_COMPLETED):
    fs = set(fs)
    _wait(_wait_condition(fs, return_when), _deadline(timeout))
    done = {f for f in fs if f.done()}
    return DoneAndNotDoneFutures(done, fs - done)


def _cf_wait_green(fs, timeout=None, return_when=ALL_COMPLETED):
    fs = set(fs)
    yield from _gwait(_wait_condition(fs, return_when), _deadline(timeout))
    done = {f for f in fs if f.done()}
    return DoneAndNotDoneFutures(done, fs - done)


_green(wait, _cf_wait_green)


# ------------------------------------------------------- multiprocessing
class _Process(Thread):
    _counter = itertools.count(1)

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        if target is not None:
            _check_picklable(target, "target")
        super().__init__(group, target, name or f"Process-{next(self._counter)}", args, kwargs,
                         daemon=daemon)
        self.exitcode = None

    pid = property(lambda self: 1000 + (self._ident or 0) if self._started else None)

    def _bootstrap(self):
        try:
            yield from Thread._bootstrap(self)
            self.exitcode = 0
        except SystemExit as stop:
            self.exitcode = stop.code if isinstance(stop.code, int) else 1
        except BaseException:
            self.exitcode = 1
            raise

    def terminate(self):
        if self._alive:
            _sched._finish(self)
            self.exitcode = -15

    kill = terminate

    def close(self):
        pass


class _Pool:
    def __init__(self, processes=None, initializer=None, initargs=(), maxtasksperchild=None):
        self._executor = ProcessPoolExecutor(processes or 4, initializer=initializer, initargs=initargs)

    def apply(self, func, args=(), kwds=None):
        return self._executor.submit(func, *args, **(kwds or {})).result()

    def apply_async(self, func, args=(), kwds=None, callback=None, error_callback=None):
        future = self._executor.submit(func, *args, **(kwds or {}))
        return _AsyncResult(future, callback, error_callback)

    def map(self, func, iterable, chunksize=None):
        return list(self._executor.map(func, iterable))

    def map_async(self, func, iterable, chunksize=None, callback=None, error_callback=None):
        futures = [self._executor.submit(func, item) for item in iterable]
        return _ListResult(futures, callback, error_callback)

    def starmap(self, func, iterable, chunksize=None):
        return [f.result() for f in [self._executor.submit(func, *args) for args in iterable]]

    def imap(self, func, iterable, chunksize=1):
        return self._executor.map(func, iterable)

    def imap_unordered(self, func, iterable, chunksize=1):
        futures = [self._executor.submit(func, item) for item in iterable]
        return (f.result() for f in as_completed(futures))

    def close(self):
        self._executor._shutdown = True

    def terminate(self):
        self._executor.shutdown(wait=False, cancel_futures=True)

    def join(self):
        self._executor.shutdown(wait=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.terminate()


class _AsyncResult:
    def __init__(self, future, callback=None, error_callback=None):
        self._future = future
        if callback or error_callback:
            def done(f):
                if f._exception is None:
                    if callback:
                        callback(f._result)
                elif error_callback:
                    error_callback(f._exception)
            future.add_done_callback(done)

    def get(self, timeout=None):
        return self._future.result(timeout)

    def wait(self, timeout=None):
        _wait(self._future.done, _deadline(timeout))

    def ready(self):
        return self._future.done()

    def successful(self):
        if not self.ready():
            raise ValueError("result is not ready")
        return self._future._exception is None


class _ListResult(_AsyncResult):
    def __init__(self, futures, callback=None, error_callback=None):
        self._futures = futures
        self._callback = callback
        self._future = Future()
        if not futures:
            self._future.set_result([])
        for f in futures:
            f.add_done_callback(self._check)

    def _check(self, _):
        if all(f.done() for f in self._futures) and not self._future.done():
            errors = [f._exception for f in self._futures if f._exception is not None]
            if errors:
                self._future.set_exception(errors[0])
            else:
                values = [f._result for f in self._futures]
                self._future.set_result(values)
                if self._callback:
                    self._callback(values)


class _ThreadPool(_Pool):
    """multiprocessing.pool.ThreadPool: real threads, so lambdas are fine."""

    def __init__(self, processes=None, initializer=None, initargs=()):
        self._executor = ThreadPoolExecutor(processes or 4, initializer=initializer, initargs=initargs)


class _Value:
    def __init__(self, typecode_or_type, value=0, *, lock=True):
        self.value = value
        self._lock = RLock()

    def get_lock(self):
        return self._lock

    def __repr__(self):
        return f"<Synchronized wrapper for {self.value!r}>"


class _Array(list):
    def __init__(self, typecode_or_type, size_or_initializer, *, lock=True):
        if isinstance(size_or_initializer, int):
            super().__init__([0] * size_or_initializer)
        else:
            super().__init__(size_or_initializer)
        self._lock = RLock()

    def get_lock(self):
        return self._lock


class _Manager:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def start(self):
        pass

    def shutdown(self):
        pass

    def list(self, *args):
        return list(*args)

    def dict(self, *args, **kwargs):
        return dict(*args, **kwargs)

    def Queue(self, maxsize=0):
        return Queue(maxsize)

    def Lock(self):
        return Lock()

    def Value(self, typecode, value):
        return _Value(typecode, value)


class _Connection:
    def __init__(self, inbox, outbox):
        self._inbox, self._outbox = inbox, outbox

    def send(self, obj):
        self._outbox.put(obj)

    def recv(self):
        return self._inbox.get()

    def _recv_green(self):
        return (yield from self._inbox._get_green())

    _green(recv, _recv_green)

    def poll(self, timeout=0.0):
        if timeout:
            _wait(lambda: not self._inbox.empty(), _deadline(timeout))
        return not self._inbox.empty()

    def close(self):
        pass


def _pipe(duplex=True):
    a, b = Queue(), Queue()
    return _Connection(a, b), _Connection(b, a)


class _CurrentProcess:
    name = "MainProcess"
    pid = 1000
    daemon = False


def _make_multiprocessing():
    module = types.ModuleType("multiprocessing")
    module.__doc__ = "Bytecraft: processes are emulated by green threads (shared memory)."
    module.Process = _Process
    module.Pool = _Pool
    module.Queue = Queue
    module.JoinableQueue = Queue
    module.SimpleQueue = SimpleQueue
    module.Lock = Lock
    module.RLock = RLock
    module.Event = Event
    module.Semaphore = Semaphore
    module.Condition = Condition
    module.Barrier = Barrier
    module.cpu_count = lambda: 4
    module.current_process = lambda: _sched.current if isinstance(_sched.current, _Process) else _CurrentProcess
    module.Value = _Value
    module.Array = _Array
    module.Manager = _Manager
    module.Pipe = _pipe
    module.pool = types.SimpleNamespace(Pool=_Pool, ThreadPool=_ThreadPool)
    module.parent_process = lambda: None
    module.set_start_method = lambda method, force=False: None
    module.get_start_method = lambda allow_none=False: "spawn"
    module.freeze_support = lambda: None
    module.TimeoutError = TimeoutError
    module.get_context = lambda method=None: module
    return module


# --------------------------------------------------------------- install
_ORIGINAL_EXCEPTHOOK = None


def _install():
    global _ORIGINAL_EXCEPTHOOK
    import threading
    import _thread
    _ORIGINAL_EXCEPTHOOK = threading.excepthook
    builtins._bytecraft_call = _bytecraft_call
    builtins._bytecraft_link = _bytecraft_link
    builtins._bytecraft_tick = _bytecraft_tick
    builtins._bytecraft_poll = _bytecraft_poll

    threading.Thread = Thread
    threading.Timer = Timer
    threading.Lock = Lock
    threading.RLock = RLock
    threading.Condition = Condition
    threading.Semaphore = Semaphore
    threading.BoundedSemaphore = BoundedSemaphore
    threading.Event = Event
    threading.Barrier = Barrier
    threading.BrokenBarrierError = BrokenBarrierError
    threading.local = local
    threading.current_thread = threading.currentThread = current_thread
    threading.main_thread = main_thread
    threading.get_ident = get_ident
    threading.get_native_id = get_native_id
    threading.active_count = threading.activeCount = active_count
    threading.enumerate = enumerate_threads
    threading.setswitchinterval = lambda interval: None

    def start_new_thread(function, args, kwargs=None):
        thread = Thread(target=function, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread.ident
    _thread.start_new_thread = start_new_thread

    for name in ("Queue", "LifoQueue", "PriorityQueue", "SimpleQueue"):
        setattr(_queue_module, name, globals()[name])

    _cf.Future = Future
    _cf.ThreadPoolExecutor = ThreadPoolExecutor
    _cf.ProcessPoolExecutor = ProcessPoolExecutor
    _cf.as_completed = as_completed
    _cf.wait = wait
    for submodule in ("thread", "process"):
        try:
            module = __import__(f"concurrent.futures.{submodule}", fromlist=["x"])
            module.ThreadPoolExecutor = ThreadPoolExecutor
            module.ProcessPoolExecutor = ProcessPoolExecutor
        except Exception:  # noqa: BLE001 - not importable in the browser
            sys.modules[f"concurrent.futures.{submodule}"] = types.SimpleNamespace(
                ThreadPoolExecutor=ThreadPoolExecutor, ProcessPoolExecutor=ProcessPoolExecutor)

    multiprocessing = _make_multiprocessing()
    sys.modules["multiprocessing"] = multiprocessing
    sys.modules["multiprocessing.pool"] = multiprocessing.pool

    import os
    real_getpid = os.getpid
    os.getpid = lambda: _sched.current.pid if isinstance(_sched.current, _Process) else real_getpid()
    for cls, module, name in ((_Pool, "multiprocessing.pool", "Pool"),
                              (_ThreadPool, "multiprocessing.pool", "ThreadPool"),
                              (_Process, "multiprocessing.context", "Process")):
        cls.__module__, cls.__name__, cls.__qualname__ = module, name, name

    _time.sleep = _sleep
    _time.monotonic = lambda: _real_monotonic() + _offset
    _time.perf_counter = lambda: _real_perf_counter() + _offset
    _time.time = lambda: _real_time() + _offset
    _time.monotonic_ns = lambda: int(_time.monotonic() * 1e9)
    _time.perf_counter_ns = lambda: int(_time.perf_counter() * 1e9)
    _time.time_ns = lambda: int(_time.time() * 1e9)


def _bytecraft_threads_reset():
    global _thread_counter, _offset
    import contextlib
    import io
    # Threads left by a stopped program: close them now, quietly, so their
    # finally blocks don't print into the next program.
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        for thread in list(_sched.threads):
            try:
                if thread._gen is not None:
                    thread._gen.close()
            except BaseException:  # noqa: BLE001
                pass
    _offset = 0.0
    _sched.reset()
    _executors.clear()
    _thread_counter = itertools.count(1)
    _Process._counter = itertools.count(1)
    ThreadPoolExecutor._counter = itertools.count()


def _bytecraft_threads_finish():
    """Like CPython at exit: wait for every non-daemon thread, then let
    executors finish the work already submitted (as their atexit hook does)."""
    _sched.run_until(lambda: not any(not t.daemon for t in _sched.threads))
    for executor in _executors:
        executor._shutdown = True
    _sched.run_until(lambda: not any(hasattr(t, "_bytecraft_executor") for t in _sched.threads))


_install()
DeadlockError.__module__ = "builtins"
builtins._bytecraft_wait_until = _sched.run_until
builtins._bytecraft_enter = _bytecraft_enter
builtins._bytecraft_exit_error = _bytecraft_exit_error
builtins._bytecraft_exit = _bytecraft_exit
builtins._bytecraft_lambda = _bytecraft_lambda
builtins._bytecraft_compile = _bytecraft_compile
builtins._bytecraft_threads_reset = _bytecraft_threads_reset
builtins._bytecraft_threads_finish = _bytecraft_threads_finish


import asyncio as _asyncio  # noqa: E402


async def _to_thread(func, /, *args, **kwargs):
    loop = _asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


_asyncio.to_thread = _asyncio.threads.to_thread = _to_thread
