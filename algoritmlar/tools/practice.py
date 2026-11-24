"""O'quv topshiriqlari.

Topshiriqlar algoritm fayllaridagi PRACTICE ro'yxatlaridan avtomatik yig'iladi.
Algoritmga bog'lanmagan topshiriq kerak bo'lsa – quyidagi EXTRA_TASKS ga qo'shing:
    {"lvl": "O'rta", "text": "...", "algo": "caesar", "mode": "enc", "vals": {...}}
"""
import re

from core import registry

META = {"id": "practice", "title": "O'quv topshiriqlari", "subtitle": "Practice Tasks", "order": 20, "kind": "tasks"}

EXTRA_TASKS: list = []
_RANK = {"Boshlang'ich": 0, "O'rta": 1, "Murakkab": 2}


def _norm(s) -> str:
    return re.sub(r"\s+", "", str(s)).upper()


def _collect():
    tasks = []
    for entry in registry.algorithms():
        for k, t in enumerate(getattr(entry["module"], "PRACTICE", [])):
            tasks.append({**t, "algo": entry["meta"]["id"], "id": f"{entry['meta']['id']}#{k}",
                          "_order": entry["meta"].get("order", 999)})
    for k, t in enumerate(EXTRA_TASKS):
        tasks.append({**t, "id": f"extra#{k}", "_order": 9999})
    tasks.sort(key=lambda t: (_RANK.get(t["lvl"], 9), t["_order"]))
    return tasks


def _answer(task) -> str:
    out = registry.run_algorithm(task["algo"], task.get("mode", "enc"), task["vals"])
    if "error" in out:
        return f"(xatolik: {out['error']})"
    fn = task.get("answer")
    return str(fn(out)) if fn else str(out["result"])


def handle(action, payload):
    tasks = _collect()
    if action == "list":
        return {"tasks": [{"id": t["id"], "lvl": t["lvl"], "text": t["text"]} for t in tasks]}
    task = next((t for t in tasks if t["id"] == payload.get("id")), None)
    if task is None:
        return {"error": "Topshiriq topilmadi."}
    if action == "check":
        return {"ok": _norm(payload.get("answer", "")) == _norm(_answer(task))}
    if action == "reveal":
        return {"answer": _answer(task)}
    return {"error": f"Noma'lum amal: {action}"}
