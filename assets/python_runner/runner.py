"""Runs a learner's program as the file main.py with fresh globals and prints
a traceback with only the program's own frames.

Used by assets/python_runner/worker.js (the app) and by
tool/pyodide/check_content.mjs (CI), so CI checks exactly what the phone runs.
"""
import builtins, sys, traceback

_bytecraft_input = builtins.input

def _bytecraft_quiet_input(prompt=""):
    # Like input(), but the prompt is not printed (practice tests).
    line = sys.stdin.readline()
    if not line:
        raise EOFError("EOF when reading a line")
    return line[:-1] if line.endswith("\n") else line

def _bytecraft_run(code, quiet_input=False):
    builtins.input = _bytecraft_quiet_input if quiet_input else _bytecraft_input
    g = {"__name__": "__main__", "__builtins__": builtins}
    status = "ok"
    compile_program = getattr(builtins, "_bytecraft_compile", None)
    reset = getattr(builtins, "_bytecraft_threads_reset", None)
    finish = getattr(builtins, "_bytecraft_threads_finish", None)
    try:
        if reset:
            reset()
        program = compile_program(code) if compile_program else compile(code, "main.py", "exec")
        exec(program, g)
        if finish:
            finish()  # like CPython at exit: wait for non-daemon threads
    except SystemExit as error:
        if error.code not in (None, 0):
            print(error.code, file=sys.stderr)
            status = "error"
    except KeyboardInterrupt:
        status = "interrupted"
    except BaseException as error:
        status = "error"
        # Only the program's own frames: the sandbox machinery (threads,
        # asyncio) would just be noise for a learner.
        frames = [f for f in traceback.extract_tb(error.__traceback__) if f.filename == "main.py"]
        lines = traceback.format_list(frames)
        if lines:
            lines.insert(0, "Traceback (most recent call last):\n")
        lines += traceback.format_exception_only(type(error), error)
        sys.stderr.write("".join(lines))
        if finish and not isinstance(error, (KeyboardInterrupt,)) and type(error).__name__ != "DeadlockError":
            # Like CPython: other threads still run to the end.
            try:
                finish()
            except BaseException:
                pass
    finally:
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except BaseException:
            pass
    return status
