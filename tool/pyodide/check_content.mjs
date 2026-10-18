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

// Every program goes through the app's own runner (runner.py), so a bug
// there fails CI instead of reaching the phone.
const RUNNER = String.raw`
import contextlib, io, os, sys, tempfile

def _bytecraft_check(code, stdin, quiet):
    out, err = io.StringIO(), io.StringIO()
    old_cwd = os.getcwd()
    os.chdir(tempfile.mkdtemp())
    sys.stdin = io.StringIO(stdin)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = _bytecraft_run(code, quiet)
    finally:
        sys.stdin = sys.__stdin__
        os.chdir(old_cwd)
    error = None if status == "ok" else f"{status}: {err.getvalue()[-400:]}"
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
    items.push({ id: `${task.id}#${i + 1}`, code: task.solution, stdin: test.stdin, expected: test.expected, quiet: true });
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
// The same files, in the same order, as assets/python_runner/worker.js.
pyodide.runPython(readFileSync(new URL('../../assets/python_runner/runner.py', import.meta.url), 'utf8'));
pyodide.runPython(RUNNER);
for (const name of ['sandbox_asyncio.py', 'sandbox_threads.py']) {
  const source = readFileSync(new URL(`../../assets/python_runner/${name}`, import.meta.url), 'utf8');
  pyodide.runPython(source, { globals: pyodide.toPy({ __name__: name.replace('.py', '') }) });
}
const check = pyodide.globals.get('_bytecraft_check');
console.log(`Pyodide ${pyodide.version}, Python ${pyodide.runPython('import sys; sys.version.split()[0]')}`);

const failures = [];
for (const item of items) {
  const result = check(item.code, item.stdin, !!item.quiet);
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
