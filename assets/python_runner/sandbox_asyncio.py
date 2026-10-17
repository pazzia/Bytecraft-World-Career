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
import selectors
import time


class _SleepSelector(selectors.BaseSelector):
    def __init__(self):
        self._keys = {}

    def register(self, fileobj, events, data=None):
        fd = fileobj if isinstance(fileobj, int) else fileobj.fileno()
        key = selectors.SelectorKey(fileobj, fd, events, data)
        self._keys[fd] = key
        return key

    def unregister(self, fileobj):
        fd = fileobj if isinstance(fileobj, int) else fileobj.fileno()
        return self._keys.pop(fd)

    def select(self, timeout=None):
        if timeout is None:
            # Nothing is scheduled and no I/O can ever arrive: the program
            # waits for an event nobody will set.
            raise RuntimeError("asyncio: программа ждёт событие, которое никогда не наступит")
        if timeout > 0:
            time.sleep(timeout)
        return []

    def close(self):
        self._keys.clear()

    def get_map(self):
        return self._keys


class _SandboxLoop(asyncio.SelectorEventLoop):
    def __init__(self):
        super().__init__(_SleepSelector())

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
    if asyncio.events._get_running_loop() is not None:
        raise RuntimeError("asyncio.run() cannot be called from a running event loop")
    if not asyncio.iscoroutine(main):
        raise ValueError(f"a coroutine was expected, got {main!r}")
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
        finally:
            asyncio.set_event_loop(None)
            loop.close()


asyncio.set_event_loop_policy(_SandboxPolicy())
asyncio.run = run
asyncio.runners.run = run
