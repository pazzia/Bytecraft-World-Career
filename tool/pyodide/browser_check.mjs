// Runs the in-app Python sandbox exactly as the phone does: the page
// assets/python_runner/index.html in a real browser engine (Chromium),
// served with the same headers as lib/features/playground/data/asset_http_server.dart,
// with Pyodide in a Web Worker. Then runs a few programs through it.
//
// Usage: node tool/pyodide/browser_check.mjs assets
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { chromium } from 'playwright';

const root = process.argv[2] || 'assets';
const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.wasm': 'application/wasm',
  '.json': 'application/json', '.zip': 'application/zip',
};

const server = createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^\/+/, '');
  if (!path.startsWith('python_runner/') && !path.startsWith('pyodide/')) {
    res.writeHead(404).end();
    return;
  }
  try {
    const body = await readFile(join(root, path));
    res.writeHead(200, {
      'Content-Type': MIME[extname(path)] || 'application/octet-stream',
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Embedder-Policy': 'require-corp',
      'Cross-Origin-Resource-Policy': 'same-origin',
    });
    res.end(body);
  } catch {
    res.writeHead(404).end();
  }
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const port = server.address().port;

const CASES = [
  {
    name: 'print and input with a prompt',
    code: 'name = input("Имя: ")\nprint("Привет,", name)\nprint(repr("a\\nb"))',
    stdin: 'Ада\n',
    expect: { status: 'ok', stdout: "Имя: Привет, Ада\n'a\\nb'\n" },
  },
  {
    name: 'quiet input (practice tests)',
    code: 'a = int(input("число: "))\nprint(a * 2)',
    stdin: '21\n', quietInput: true,
    expect: { status: 'ok', stdout: '42\n' },
  },
  {
    name: 'error with a short traceback',
    code: 'def f(x):\n    return 1 / x\n\nprint("до")\nf(0)',
    expect: { status: 'error', stdout: 'до\n', stderrIncludes: ['line 2', 'ZeroDivisionError'] },
  },
  {
    name: 'syntax error',
    code: 'print("hi"',
    expect: { status: 'error', stderrIncludes: ['SyntaxError'] },
  },
  {
    name: 'threads and a queue',
    code: [
      'import queue, threading',
      'q = queue.Queue(maxsize=1)',
      'out = []',
      'def worker():',
      '    while (x := q.get()) is not None:',
      '        out.append(x * 10)',
      't = threading.Thread(target=worker)',
      't.start()',
      'for i in range(3):',
      '    q.put(i)',
      'q.put(None)',
      't.join()',
      'print(out, threading.active_count())',
    ].join('\n'),
    expect: { status: 'ok', stdout: '[0, 10, 20] 1\n' },
  },
  {
    name: 'asyncio',
    code: [
      'import asyncio',
      'async def job(n, d):',
      '    await asyncio.sleep(d)',
      '    return n',
      'async def main():',
      '    print(await asyncio.gather(job(1, 0.02), job(2, 0.01)))',
      'asyncio.run(main())',
    ].join('\n'),
    expect: { status: 'ok', stdout: '[1, 2]\n' },
  },
  {
    name: 'endless loop is stopped',
    code: 'while True:\n    pass',
    timeoutMs: 1500,
    expect: { status: 'timeout' },
  },
  {
    name: 'works again after a stop',
    code: 'print(sum(range(10)))',
    expect: { status: 'ok', stdout: '45\n' },
  },
];

const browser = await chromium.launch();
const page = await browser.newPage();
const failures = [];
try {
  page.on('console', (msg) => console.log(`[page] ${msg.text()}`));
  await page.goto(`http://127.0.0.1:${port}/python_runner/index.html`);
  const status = await page.waitForFunction(() => {
    const all = window.__bytecraftMessages || [];
    return all.find((m) => m.type === 'status' && (m.state === 'ready' || m.state === 'failed'));
  }, null, { timeout: 120000 }).then((handle) => handle.jsonValue());
  console.log(`sandbox: ${JSON.stringify(status)}`);
  if (status.state !== 'ready') throw new Error(`sandbox failed: ${status.message}`);

  for (const [index, test] of CASES.entries()) {
    const id = `case-${index}`;
    await page.evaluate((job) => window.bytecraft.run(job), {
      id, code: test.code, stdin: test.stdin || '', quietInput: !!test.quietInput,
      timeoutMs: test.timeoutMs || 10000,
    });
    const result = await page.waitForFunction((runId) => {
      return (window.__bytecraftMessages || []).find((m) => m.type === 'result' && m.id === runId);
    }, id, { timeout: 60000 }).then((handle) => handle.jsonValue());
    if (test.name === 'endless loop is stopped') {
      // Wait until the worker is ready again after a hard stop.
      await page.waitForTimeout(500);
    }
    const problems = [];
    if (result.status !== test.expect.status) problems.push(`status ${result.status}`);
    if (test.expect.stdout !== undefined && result.stdout !== test.expect.stdout) {
      problems.push(`stdout ${JSON.stringify(result.stdout)}`);
    }
    for (const part of test.expect.stderrIncludes || []) {
      if (!result.stderr.includes(part)) problems.push(`stderr lacks ${part}`);
    }
    const line = `${problems.length ? 'FAIL' : 'ok  '} ${test.name} (${result.durationMs} ms)`;
    console.log(line);
    if (problems.length) {
      console.log(`     ${problems.join('; ')}`);
      console.log(`     stderr: ${JSON.stringify(result.stderr).slice(0, 600)}`);
      failures.push(test.name);
    }
  }
} catch (error) {
  console.log(`ERROR: ${error.message}`);
  failures.push('sandbox');
} finally {
  await browser.close();
  server.close();
}
console.log(`${CASES.length - failures.length} of ${CASES.length} passed`);
process.exit(failures.length ? 1 : 0);
