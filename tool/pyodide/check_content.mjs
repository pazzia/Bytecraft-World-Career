// Runs every piece of course code in Pyodide (the interpreter bundled into
// the app) and checks it prints exactly what the content says. The content
// generator computes outputs with CPython; this catches differences between
// the two (missing modules, threads, version-specific messages).
//
// Usage: node tool/pyodide/check_content.mjs assets/content/python
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { loadPyodide } from 'pyodide';

const root = process.argv[2] || 'assets/content/python';
const read = (path) => JSON.parse(readFileSync(join(root, path), 'utf8'));

const RUNNER = `
import contextlib, io, os, sys, tempfile

def _bytecraft_check(code, stdin):
    out = io.StringIO()
    old_cwd = os.getcwd()
    os.chdir(tempfile.mkdtemp())
    sys.stdin = io.StringIO(stdin)
    error = None
    try:
        with contextlib.redirect_stdout(out):
            exec(compile(code, "main.py", "exec"), {"__name__": "__main__"})
    except SystemExit as e:
        if e.code not in (None, 0):
            error = f"SystemExit: {e.code}"
    except BaseException as e:
        error = f"{type(e).__name__}: {e}"
    finally:
        sys.stdin = sys.__stdin__
        os.chdir(old_cwd)
    return [out.getvalue(), error]
`;

const items = [];
for (const file of readdirSync(join(root, 'modules')).sort()) {
  for (const level of read(join('modules', file)).levels) {
    const s = level.solution;
    if (!s || s.nativeOnly) continue;
    items.push({ id: level.id, code: s.code, stdin: s.stdin || '', expected: s.output });
  }
}
for (const topic of read('topics.json').topics) {
  topic.examples.forEach((example, i) => {
    if (example.nativeOnly) return;
    items.push({ id: `${topic.id}#${i + 1}`, code: example.code, stdin: example.stdin || '', expected: example.output });
  });
}
const practice = read('practice.json');
for (const task of practice.tasks) {
  task.tests.forEach((test, i) => {
    items.push({ id: `${task.id}#${i + 1}`, code: task.solution, stdin: test.stdin, expected: test.expected });
  });
  // The requirement checker (run by the app before the tests) must accept
  // the reference solution in Pyodide too.
  items.push({
    id: `${task.id}#requirements`,
    code: practice.checker,
    stdin: JSON.stringify({ code: task.solution, requires: task.requires || {} }),
    expected: '[]\n',
  });
}

const pyodide = await loadPyodide();
pyodide.runPython(RUNNER);
// The same blocking asyncio loop as in the app (assets/python_runner/worker.js).
pyodide.runPython(readFileSync(new URL('../../assets/python_runner/sandbox_asyncio.py', import.meta.url), 'utf8'));
const check = pyodide.globals.get('_bytecraft_check');
console.log(`Pyodide ${pyodide.version}, Python ${pyodide.runPython('import sys; sys.version.split()[0]')}`);

const failures = [];
for (const item of items) {
  const result = check(item.code, item.stdin);
  const [out, error] = result.toJs();
  result.destroy();
  if (error || out !== item.expected) {
    failures.push({ id: item.id, error, got: out, expected: item.expected });
  }
}
console.log(`checked ${items.length} programs, ${failures.length} differ`);
for (const f of failures.slice(0, 40)) {
  console.log(`--- ${f.id}`);
  if (f.error) console.log(`error: ${f.error}`);
  console.log(`expected: ${JSON.stringify(f.expected).slice(0, 300)}`);
  console.log(`got:      ${JSON.stringify(f.got).slice(0, 300)}`);
}
process.exit(failures.length ? 1 : 0);
