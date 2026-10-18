"""asyncio for the in-app interpreter.

Pyodide's own event loop runs on the browser's event loop: it can't block,
so asyncio.run() of a regular program never finishes there. This module
installs a plain blocking loop instead: a SelectorEventLoop whose selector
"waits" by sleeping. Coroutines, tasks, gather, sleep, timeouts, queues and
locks work as in CPython; sockets and subprocesses are not available (there
is no network in the sandbox anyway).

Loaded by assets/python_runner/worker.js and by tool/pyodide/check_content.mjs.
"""
import asyncio
import builtins
import selectors
import time


def _deadlock_message(loop):
    lines = ["asyncio: все задачи ждут, и разбудить их некому (взаимная блокировка)."]
    for task in asyncio.all_tasks(loop) if loop is not None else ():
        frames = [f for f in task.get_stack() if f.f_code.co_filename == "main.py"]
        where = f"строка {frames[-1].f_lineno}" if frames else "?"
        lines.append(f"  {task.get_coro().__qualname__}() ждёт: {where}")
    return "\n".join(lines)


class _SleepSelector(selectors.BaseSelector):
    def __init__(self):
        self._keys = {}
        self.loop = None

    def register(self, fileobj, events, data=None):
        fd = fileobj if isinstance(fileobj, int) else fileobj.fileno()
        key = selectors.SelectorKey(fileobj, fd, events, data)
        self._keys[fd] = key
        return key

    def unregister(self, fileobj):
        fd = fileobj if isinstance(fileobj, int) else fileobj.fileno()
        return self._keys.pop(fd)

    def select(self, timeout=None):
        # Emulated threads (sandbox_threads.py) run while the loop waits:
        # asyncio.to_thread and run_in_executor work through them.
        wait_until = getattr(builtins, "_bytecraft_wait_until", None)
        if wait_until is not None:
            deadline = None if timeout is None else time.monotonic() + timeout
            try:
                wait_until(lambda: bool(self.loop._ready), deadline)
            except RuntimeError:
                raise RuntimeError(_deadlock_message(self.loop)) from None
            return []
        if timeout is None:
            # Nothing is scheduled and no I/O can ever arrive: the program
            # waits for an event nobody will set.
            raise RuntimeError(_deadlock_message(self.loop))
        end = time.monotonic() + timeout
        while (left := end - time.monotonic()) > 0:
            time.sleep(min(left, 0.05))  # short naps: the stop button stays responsive
        return []

    def close(self):
        self._keys.clear()

    def get_map(self):
        return self._keys


class _SandboxLoop(asyncio.SelectorEventLoop):
    def __init__(self):
        selector = _SleepSelector()
        super().__init__(selector)
        selector.loop = self

    # No self-pipe (socketpair is not available): wake-ups from other
    # threads are not needed in a single-threaded sandbox.
    def _make_self_pipe(self):
        pass

    def _close_self_pipe(self):
        pass

    def _write_to_self(self):
        pass

    def _process_self_data(self, data):
        pass


class _SandboxPolicy(asyncio.DefaultEventLoopPolicy):
    def new_event_loop(self):
        return _SandboxLoop()


def _cancel_all_tasks(loop):
    tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
    for task in tasks:
        task.cancel()
    if tasks:
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))


def run(main, *, debug=None, loop_factory=None):
    """asyncio.run on the sandbox loop. Pyodide replaces asyncio.run with a
    version that needs JavaScript stack switching (JSPI), which a WebView
    may not support, so the standard behaviour is restored here."""
    outer = asyncio.events._get_running_loop()
    if isinstance(outer, _SandboxLoop):
        raise RuntimeError("asyncio.run() cannot be called from a running event loop")
    if not asyncio.iscoroutine(main):
        raise ValueError(f"a coroutine was expected, got {main!r}")
    # Pyodide marks its browser loop as always running; the program's own
    # loop runs "inside" it, so that mark is lifted for the duration.
    asyncio.events._set_running_loop(None)
    loop = (loop_factory or _SandboxLoop)()
    if debug is not None:
        loop.set_debug(debug)
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(main)
    finally:
        try:
            _cancel_all_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            asyncio.set_event_loop(None)
            loop.close()
            asyncio.events._set_running_loop(outer)


asyncio.set_event_loop_policy(_SandboxPolicy())
asyncio.run = run
asyncio.runners.run = run
