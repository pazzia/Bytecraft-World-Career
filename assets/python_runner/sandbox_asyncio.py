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


asyncio.set_event_loop_policy(_SandboxPolicy())
