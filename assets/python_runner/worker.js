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
    try:
        exec(compile(code, "main.py", "exec"), g)
    except SystemExit as error:
        if error.code not in (None, 0):
            print(error.code, file=sys.stderr)
            status = "error"
    except KeyboardInterrupt:
        status = "interrupted"
    except BaseException as error:
        status = "error"
        tb = error.__traceback__
        while tb is not None and tb.tb_frame.f_code.co_filename != "main.py":
            tb = tb.tb_next
        traceback.print_exception(type(error), error, tb, file=sys.stderr)
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
    try {
      const asyncioSource = await (await fetch(base + 'python_runner/sandbox_asyncio.py')).text();
      pyodide.runPython(asyncioSource);
    } catch (error) {
      // Everything except asyncio.run() still works.
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
