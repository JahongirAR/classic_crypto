/* Service worker: sayt bir marta ochilgach internetsiz ham ishlaydi.
   - pyodide/ (o'zgarmas, katta) → avval keshdan
   - qolganlari → avval tarmoq (yangilanish darhol ko'rinadi), tarmoq yo'q bo'lsa keshdan */
const CACHE = "kripto-v1";
const SHELL = ["./", "index.html", "css/style.css", "js/main.js", "js/worker.js", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png",
  "pyodide/pyodide.mjs", "pyodide/pyodide.asm.mjs", "pyodide/pyodide.asm.wasm",
  "pyodide/python_stdlib.zip", "pyodide/pyodide-lock.json", "pyodide/package.json",
  "algoritmlar/manifest.json"];

self.addEventListener("install", (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await Promise.allSettled(SHELL.map((u) => c.add(u)));
    try {
      const man = await (await fetch("algoritmlar/manifest.json", { cache: "no-cache" })).json();
      await Promise.allSettled(man.files.map((f) => c.add(`algoritmlar/${f}?v=${man.version}`)));
    } catch (err) { /* oflayn o'rnatish keyinroq to'ldiriladi */ }
    self.skipWaiting();
  })());
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  const isPyodide = new URL(req.url).pathname.includes("/pyodide/");
  e.respondWith((async () => {
    const c = await caches.open(CACHE);
    if (isPyodide) {
      const hit = await c.match(req);
      if (hit) return hit;
    }
    try {
      const res = await fetch(req);
      if (res.ok) c.put(req, res.clone());
      return res;
    } catch (err) {
      const hit = await c.match(req, { ignoreSearch: false }) || await c.match(req, { ignoreSearch: true });
      if (hit) return hit;
      if (req.mode === "navigate") return (await c.match("index.html")) || Response.error();
      return Response.error();
    }
  })());
});
