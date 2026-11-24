"""YANGI YORDAMCHI FUNKSIYA SHABLONI (forma turi – HTML'ni o'zgartirmasdan yangi sahifa).

Qo'shish: bu faylni nusxalang (masalan tools/gcd_hisoblagich.py, '_' bilan boshlanmasin) va to'ldiring.
Bosh sahifada yangi tugma avtomatik paydo bo'ladi.

kind turlari:  "form" (maydonlar + natija bloklari – quyidagi misol),
               "table" (load → {"head":[...], "rows":[[...]]}),
               "tasks" (list/check/reveal), "quiz" (list/answer/finish) – ularga compare.py, practice.py, quiz.py ga qarang.

Natija bloklari ("k"): error, bar, box, boxes, heading, step, table  (calculator.py da namunalar bor).
"""
META = {
    "id": "gcd",
    "title": "GCD hisoblagich (shablon)",
    "subtitle": "Eng katta umumiy bo'luvchi",
    "order": 50,
    "kind": "form",
    "heading": "🧮 GCD hisoblagich",
    "intro": "Ikki sonning eng katta umumiy bo'luvchisini topadi.",
    "sections": [{
        "id": "main", "tab": "GCD", "button": "= Hisobla", "auto": False,
        "fields": [{"id": "a", "label": "BIRINCHI SON", "type": "text", "default": "48"},
                   {"id": "b", "label": "IKKINCHI SON", "type": "text", "default": "18"}],
        "examples": [{"label": "48, 18", "vals": {"a": "48", "b": "18"}}],
    }],
}


def handle(action, payload):
    if action != "run":
        return {"error": "Noma'lum amal."}
    v = payload.get("vals") or {}
    try:
        a, b = int(v["a"]), int(v["b"])
    except (KeyError, ValueError):
        return {"blocks": [{"k": "error", "t": "❌ Ikkala maydonga butun son kiriting."}]}
    x, y, rows = a, b, []
    while y:
        rows.append([str(x), str(y), str(x % y)])
        x, y = y, x % y
    return {"blocks": [
        {"k": "box", "title": "NATIJA", "value": f"gcd({a}, {b}) = {abs(x)}"},
        {"k": "table", "title": "📋 Evklid algoritmi qadamlari:", "head": ["a", "b", "a mod b"], "rows": rows},
    ]}
