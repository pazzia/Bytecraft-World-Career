// Bytecraft Python runner (worker side): loads Pyodide and runs programs.
'use strict';

const OUTPUT_LIMIT = 64 * 1024; // characters per stream

const base = self.location.href.replace(/python_runner\/worker\.js.*$/, '');
importScripts(base + 'pyodide/pyodide.js');

let pyodide = null;

// Runs user code as the file main.py with fresh globals; prints a
// traceback without the runner's own frames.
const RUNNER_PY = `
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
`;

function makeStream() {
  const decoder = new TextDecoder();
  const stream = { text: '', truncated: false };
  stream.write = function (buffer) {
    if (stream.truncated) throw new Error('Output limit exceeded');
    stream.text += decoder.decode(buffer, { stream: true });
    if (stream.text.length > OUTPUT_LIMIT) {
      stream.text = stream.text.slice(0, OUTPUT_LIMIT);
      stream.truncated = true;
      // Fails the print() call, which stops a runaway loop.
      throw new Error('Output limit exceeded');
    }
    return buffer.length;
  };
  return stream;
}

async function init(interruptBuffer) {
  try {
    pyodide = await loadPyodide({ indexURL: base + 'pyodide/' });
    if (interruptBuffer) pyodide.setInterruptBuffer(interruptBuffer);
    pyodide.runPython(RUNNER_PY);
    // A blocking event loop, so that asyncio.run() works (see the file).
    // Blocking asyncio loop and emulated threads (see the files). Without
    // them everything except asyncio.run() / threads still works.
    for (const name of ['sandbox_asyncio.py', 'sandbox_threads.py']) {
      try {
        const source = await (await fetch(base + 'python_runner/' + name)).text();
        pyodide.runPython(source, { globals: pyodide.toPy({ __name__: name.replace('.py', '') }) });
      } catch (error) {
        // Keep going: the rest of Python works without this part.
      }
    }
    const version = pyodide.runPython('import sys; sys.version.split()[0]');
    self.postMessage({ type: 'ready', version: version });
  } catch (error) {
    self.postMessage({ type: 'failed', message: String(error && error.message || error) });
  }
}

function run(job) {
  const started = performance.now();
  const stdout = makeStream();
  const stderr = makeStream();
  let stdinUsed = false;
  pyodide.setStdout({ write: stdout.write, isatty: false });
  pyodide.setStderr({ write: stderr.write, isatty: false });
  pyodide.setStdin({
    stdin: function () {
      if (stdinUsed) return null; // EOF
      stdinUsed = true;
      return job.stdin;
    },
    isatty: false,
  });
  let status;
  try {
    const runner = pyodide.globals.get('_bytecraft_run');
    status = runner(job.code, !!job.quietInput);
    runner.destroy();
  } catch (error) {
    status = 'error';
    stderr.text += String(error && error.message || error);
  }
  if (stdout.truncated || stderr.truncated) status = 'limit';
  self.postMessage({
    type: 'result',
    id: job.id,
    status: status,
    stdout: stdout.text,
    stderr: stderr.text,
    durationMs: Math.round(performance.now() - started),
    truncated: stdout.truncated || stderr.truncated,
  });
}

self.onmessage = function (event) {
  const data = event.data;
  if (data.type === 'init') {
    init(data.interruptBuffer);
  } else if (data.type === 'run') {
    if (!pyodide) {
      self.postMessage({ type: 'result', id: data.id, status: 'error', stdout: '',
        stderr: 'Python ещё загружается', durationMs: 0, truncated: false });
      return;
    }
    run(data);
  }
};
