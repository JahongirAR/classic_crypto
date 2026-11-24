/* Python backend (algoritmlar/) ni brauzerda ishga tushiradi (Pyodide, Web Worker ichida).
   Asosiy oqim (UI) qotib qolmasligi uchun hamma hisob-kitob shu yerda bajariladi. */
import { loadPyodide } from "../pyodide/pyodide.mjs";

const BASE = new URL("../", import.meta.url).href;
const say = (text) => postMessage({ type: "progress", text });
let handle = null;

const ready = (async () => {
  say("Python yuklanmoqda… (birinchi marta 10 MB atrofida)");
  const py = await loadPyodide({ indexURL: BASE + "pyodide/" });

  say("Algoritmlar yuklanmoqda…");
  const res = await fetch(BASE + "algoritmlar/manifest.json", { cache: "no-cache" });
  if (!res.ok) throw new Error("manifest.json topilmadi (HTTP " + res.status + ")");
  const man = await res.json();

  const texts = await Promise.all(man.files.map(async (f) => {
    const r = await fetch(`${BASE}algoritmlar/${f}?v=${man.version}`);
    if (!r.ok) throw new Error(f + " yuklanmadi (HTTP " + r.status + ")");
    return [f, await r.text()];
  }));
  const made = new Set();
  for (const [f, text] of texts) {
    const parts = ("/algo/" + f).split("/");
    for (let i = 2; i < parts.length; i++) {
      const dir = parts.slice(0, i).join("/");
      if (!made.has(dir)) { made.add(dir); try { py.FS.mkdir(dir); } catch (e) { /* mavjud */ } }
    }
    py.FS.writeFile("/algo/" + f, text);
  }
  py.runPython('import sys\nsys.path.insert(0, "/algo")');
  handle = py.pyimport("api").handle;
  postMessage({ type: "ready" });
})().catch((e) => { postMessage({ type: "fatal", error: String(e && e.message || e) }); throw e; });

onmessage = async (ev) => {
  const { id, method, path, body } = ev.data;
  try {
    await ready;
    postMessage({ type: "result", id, out: handle(method, path, body) });
  } catch (e) {
    postMessage({ type: "result", id, out: JSON.stringify({ error: "Ichki xatolik: " + (e && e.message || e) }) });
  }
};
