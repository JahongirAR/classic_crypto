"""Algoritmlarni taqqoslash jadvali.

Jadval qatorlari har bir algoritm faylidagi META["compare"] dan AVTOMATIK yig'iladi –
yangi algoritm qo'shsangiz, u shu yerda o'zi paydo bo'ladi.
"""
from core import registry

META = {"id": "compare", "title": "Algoritmlarni taqqoslash", "subtitle": "Compare Algorithms",
        "order": 10, "kind": "table"}

HEAD = ["Algoritm", "Turi", "Asosiy amal", "Kalit", "Asosiy xususiyat"]


def handle(action, payload):
    rows = []
    for entry in registry.algorithms():
        c = entry["meta"].get("compare")
        if not c:
            continue
        name = {"t": c["name"], "b": True} if c.get("bold") else c["name"]
        rows.append([name, c.get("type", ""), c.get("operation", ""), c.get("key", ""), c.get("feature", "")])
    return {"head": HEAD, "rows": rows}
