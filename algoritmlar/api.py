"""API qatlami: brauzer (Pyodide worker) va testlar shu modul orqali algoritmlarni chaqiradi.

HTTP serverga bog'liq EMAS. Kirish nuqtasi:  handle(method, path, body_json) -> json satr
  GET  /api/catalog
  POST /api/algo/<id>/run | live | action
  POST /api/tool/<id>
"""
import json
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import registry  # noqa: E402


def catalog():
    algos = []
    for e in registry.algorithms():
        m = dict(e["meta"])
        m["has_live"] = hasattr(e["module"], "live")
        algos.append(m)
    tools = []
    for e in registry.tools():
        m = dict(e["meta"])
        if hasattr(e["module"], "subtitle"):
            m["subtitle"] = e["module"].subtitle()
        tools.append(m)
    errors = {os.path.basename(p): tb.strip().splitlines()[-1] for p, tb in registry.LOAD_ERRORS.items()}
    return {"algorithms": algos, "tools": tools, "errors": errors}


def api_post(path, body):
    if not isinstance(body, dict):
        return 400, {"error": "So'rov JSON ob'ekt bo'lishi kerak."}
    if not isinstance(body.get("vals", {}), dict) or not isinstance(body.get("payload", {}), dict):
        return 400, {"error": "vals/payload ob'ekt bo'lishi kerak."}
    parts = [p for p in path.split("/") if p]          # ['api', 'algo', 'caesar', 'run']
    if len(parts) == 4 and parts[1] == "algo":
        entry = registry.get_algorithm(parts[2])
        if not entry:
            return 404, {"error": "Algoritm topilmadi."}
        mod, vals = entry["module"], body.get("vals") or {}
        if parts[3] == "run":
            mode = body.get("mode")
            if mode not in ("enc", "dec"):
                return 400, {"error": "mode 'enc' yoki 'dec' bo'lishi kerak."}
            return 200, mod.run(mode, vals)
        if parts[3] == "live" and hasattr(mod, "live"):
            return 200, {"visual": mod.live(vals)}
        if parts[3] == "action":
            fn = getattr(mod, "ACTIONS", {}).get(body.get("action"))
            return (200, fn(vals)) if fn else (404, {"error": "Amal topilmadi."})
    if len(parts) == 3 and parts[1] == "tool":
        entry = registry.get_tool(parts[2])
        if not entry:
            return 404, {"error": "Yordamchi funksiya topilmadi."}
        return 200, entry["module"].handle(body.get("action", ""), body.get("payload") or {})
    return 404, {"error": "Noma'lum so'rov."}


def handle(method, path, body_json="{}"):
    """Bitta so'rovni bajaradi va JSON satr qaytaradi (xatolik bo'lsa ham ilova to'xtamaydi)."""
    try:
        if method == "GET" and path == "/api/catalog":
            return json.dumps(catalog(), ensure_ascii=False)
        if method != "POST":
            return json.dumps({"error": "Noma'lum so'rov."})
        code, out = api_post(path, json.loads(body_json or "{}"))
        return json.dumps(out, ensure_ascii=False)
    except json.JSONDecodeError:
        return json.dumps({"error": "Noto'g'ri JSON."})
    except Exception as e:  # noqa: BLE001
        traceback.print_exc()
        return json.dumps({"error": f"Ichki xatolik: {type(e).__name__}: {e}"})
