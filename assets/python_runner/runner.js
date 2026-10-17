// Bytecraft Python runner (page side).
//
// Python (Pyodide) runs in a Web Worker so an endless loop never freezes
// the page. Every run gets a time limit: first a soft stop (KeyboardInterrupt
// through a shared interrupt buffer, when the page is cross-origin isolated),
// then a hard stop (the worker is terminated and started again).
//
// Talks to the app through the `BytecraftChannel` JavaScript channel:
//   -> {type: 'status', state: 'loading' | 'ready' | 'failed', message}
//   -> {type: 'result', id, status, stdout, stderr, durationMs, truncated}
// The app calls window.bytecraft.run({id, code, stdin, timeoutMs}).
(function () {
  'use strict';

  const HARD_STOP_GRACE_MS = 1500;

  function send(message) {
    const text = JSON.stringify(message);
    if (window.BytecraftChannel && window.BytecraftChannel.postMessage) {
      window.BytecraftChannel.postMessage(text);
    } else {
      // Browser tests read messages from here.
      (window.__bytecraftMessages = window.__bytecraftMessages || []).push(message);
    }
  }

  const canInterrupt =
    typeof SharedArrayBuffer !== 'undefined' && self.crossOriginIsolated === true;

  let worker = null;
  let interruptBuffer = null;
  let ready = false;
  let current = null; // {id, softTimer, hardTimer}
  const queue = [];

  function startWorker() {
    ready = false;
    send({ type: 'status', state: 'loading' });
    worker = new Worker('worker.js');
    interruptBuffer = canInterrupt ? new Int32Array(new SharedArrayBuffer(4)) : null;
    worker.onmessage = onWorkerMessage;
    worker.onerror = function (event) {
      send({ type: 'status', state: 'failed', message: String(event.message || 'worker error') });
    };
    worker.postMessage({ type: 'init', interruptBuffer: interruptBuffer });
  }

  function onWorkerMessage(event) {
    const data = event.data;
    if (data.type === 'ready') {
      ready = true;
      send({ type: 'status', state: 'ready', canInterrupt: canInterrupt, version: data.version });
      next();
    } else if (data.type === 'failed') {
      send({ type: 'status', state: 'failed', message: data.message });
    } else if (data.type === 'result') {
      if (!current || current.id !== data.id) return;
      finish(data);
    }
  }

  function finish(result) {
    clearTimeout(current.softTimer);
    clearTimeout(current.hardTimer);
    const timedOut = current.timedOut;
    current = null;
    if (timedOut && result.status === 'interrupted') result.status = 'timeout';
    send(Object.assign({ type: 'result' }, result));
    next();
  }

  function next() {
    if (!ready || current || queue.length === 0) return;
    const job = queue.shift();
    current = { id: job.id, timedOut: false, startedAt: Date.now() };
    if (interruptBuffer) Atomics.store(interruptBuffer, 0, 0);
    worker.postMessage({ type: 'run', id: job.id, code: job.code, stdin: job.stdin || '' });
    const limit = Math.max(500, job.timeoutMs || 5000);
    current.softTimer = setTimeout(function () {
      if (!current || current.id !== job.id) return;
      current.timedOut = true;
      if (interruptBuffer) {
        Atomics.store(interruptBuffer, 0, 2); // SIGINT -> KeyboardInterrupt
        current.hardTimer = setTimeout(hardStop, HARD_STOP_GRACE_MS);
      } else {
        hardStop();
      }
    }, limit);
  }

  function hardStop() {
    if (!current) return;
    const id = current.id;
    const durationMs = Date.now() - current.startedAt;
    worker.terminate();
    current = null;
    send({
      type: 'result', id: id, status: 'timeout', stdout: '', stderr: '',
      durationMs: durationMs, truncated: false,
    });
    startWorker();
  }

  window.bytecraft = {
    run: function (job) {
      queue.push(job);
      next();
    },
    restart: function () {
      if (worker) worker.terminate();
      current = null;
      startWorker();
    },
  };

  startWorker();
})();
