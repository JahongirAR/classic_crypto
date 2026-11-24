"""Plugin registry: algorithms/ va tools/ papkalaridagi fayllarni avtomatik topadi.

* Yangi fayl qo'shsangiz – serverni qayta ishga tushirish shart emas
  (fayl o'zgarganda/yangi qo'shilganda modul avtomatik qayta yuklanadi).
* '_' bilan boshlanadigan fayllar (masalan _template.py) e'tiborga olinmaydi.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_CACHE: dict[str, dict] = {"algorithms": {}, "tools": {}}   # kind -> {id: entry}
_MTIME: dict[str, float] = {}
LOAD_ERRORS: dict[str, str] = {}


def _load_file(path: str):
    name = "plug_" + os.path.basename(os.path.dirname(path)) + "_" + os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _scan(kind: str, required: tuple):
    folder = os.path.join(ROOT, kind)
    if not os.path.isdir(folder):
        return
    seen = set()
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith(".py") or fn.startswith("_"):
            continue
        path = os.path.join(folder, fn)
        seen.add(path)
        mtime = os.path.getmtime(path)
        if _MTIME.get(path) == mtime:
            continue
        _MTIME[path] = mtime
        try:
            mod = _load_file(path)
            meta = getattr(mod, "META")
            for attr in required:
                if not hasattr(mod, attr):
                    raise AttributeError(f"'{attr}' funksiyasi yo'q")
            _CACHE[kind] = {k: v for k, v in _CACHE[kind].items() if v["path"] != path}
            _CACHE[kind][meta["id"]] = {"meta": meta, "module": mod, "path": path}
            LOAD_ERRORS.pop(path, None)
        except Exception:  # noqa: BLE001 – bitta buzuq fayl butun ilovani to'xtatmasin
            LOAD_ERRORS[path] = traceback.format_exc()
            print(f"[registry] {kind}/{fn} yuklanmadi:\n{LOAD_ERRORS[path]}", file=sys.stderr)
    # o'chirilgan fayllarni (va ularning eski xatolarini) olib tashlash
    prefix = folder + os.sep
    for stale in [p for p in LOAD_ERRORS if p.startswith(prefix) and p not in seen]:
        LOAD_ERRORS.pop(stale, None)
    _CACHE[kind] = {k: v for k, v in _CACHE[kind].items() if v["path"] in seen}


def refresh():
    _scan("algorithms", ("run",))
    _scan("tools", ("handle",))


def algorithms() -> list[dict]:
    refresh()
    return sorted(_CACHE["algorithms"].values(), key=lambda e: (e["meta"].get("order", 999), e["meta"]["id"]))


def tools() -> list[dict]:
    refresh()
    return sorted(_CACHE["tools"].values(), key=lambda e: (e["meta"].get("order", 999), e["meta"]["id"]))


def get_algorithm(algo_id: str):
    refresh()
    return _CACHE["algorithms"].get(algo_id)


def get_tool(tool_id: str):
    refresh()
    return _CACHE["tools"].get(tool_id)


def run_algorithm(algo_id: str, mode: str, vals: dict) -> dict:
    """Boshqa modullar (practice va h.k.) algoritmni shu orqali chaqiradi."""
    entry = get_algorithm(algo_id)
    if not entry:
        return {"error": f"Algoritm topilmadi: {algo_id}"}
    return entry["module"].run(mode, vals)
