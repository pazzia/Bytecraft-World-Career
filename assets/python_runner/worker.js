// Bytecraft Python runner (worker side): loads Pyodide and runs programs.
'use strict';

const OUTPUT_LIMIT = 64 * 1024; // characters per stream

const base = self.location.href.replace(/python_runner\/worker\.js.*$/, '');
importScripts(base + 'pyodide/pyodide.js');

let pyodide = null;


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
    // The runner itself (runner.py) is required; it is a separate file so
    // that CI runs every course program through exactly the same code.
    pyodide.runPython(await (await fetch(base + 'python_runner/runner.py')).text());
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
