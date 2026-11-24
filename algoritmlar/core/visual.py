"""Vizual spetsifikatsiya yordamchilari.

Python HECH QANDAY HTML yozmaydi – faqat ma'lumot (dict) qaytaradi.
Brauzer (index.html) shu ma'lumotni chizadi va barcha matnni xavfsiz
(escape qilib) ko'rsatadi. Dizaynni o'zgartirish uchun faqat HTML'ni tahrirlaysiz.

Ranglar nomi bilan beriladi: gold, blue, red, green, lime, violet, pink,
cyan, orange, slate, dim, white.
"""
from __future__ import annotations


def P(t, c=None, b=False) -> dict:
    """Matn bo'lagi (span): rang va qalin."""
    return {"t": str(t), "c": c, "b": b}


def _parts(parts):
    return [p if isinstance(p, dict) else P(p) for p in parts]


def flow(*items) -> dict:
    """[A] → [B] → [C]. item: 'matn' yoki ('matn', 'cls'); cls: dim|key|formula|result."""
    out = []
    for it in items:
        if isinstance(it, (tuple, list)):
            out.append({"text": str(it[0]), "cls": it[1] if len(it) > 1 else ""})
        else:
            out.append({"text": str(it), "cls": ""})
    return {"type": "flow", "items": out}


def grid(rows, header=None) -> dict:
    """rows: [[(matn, cls), ...], ...]; cls: filled|current|readcol|empty."""
    return {
        "type": "grid",
        "header": [str(h) for h in header] if header else None,
        "rows": [[{"v": str(v), "cls": cls} for (v, cls) in row] for row in rows],
    }


def big_text(text) -> dict:
    return {"type": "text", "text": str(text)}


# ---- panel bloklari -------------------------------------------------
def line(*parts, gap=False) -> dict:
    return {"k": "line", "parts": _parts(parts), "gap": gap}


def chips(items) -> dict:
    """items: [(matn, rang), ...]"""
    return {"k": "chips", "items": [{"t": str(t), "c": c} for t, c in items]}


def table(rows, head=None) -> dict:
    """rows: [[P|str, ...], ...]"""
    return {"k": "table", "head": head, "rows": [[c if isinstance(c, dict) else P(c) for c in r] for r in rows]}


def states(*items) -> dict:
    """AES state'lari: state(...) yoki oddiy operator matni ('⊕')."""
    out = []
    for it in items:
        if isinstance(it, str):
            out.append({"op": it})
        else:
            out.append({"label": it["label"], "bytes": list(it["bytes"]), "hl": it.get("hl")})
    return {"k": "states", "items": out}


def state(label, data, hl=None) -> dict:
    return {"label": label, "bytes": list(data), "hl": hl}


def cols(*boxes) -> dict:
    """boxes: dict(title=, color=, lines=[[parts]], result=[parts])"""
    return {"k": "cols", "items": [
        {"title": b["title"], "color": b.get("color"),
         "lines": [_parts(l) for l in b.get("lines", [])],
         "result": _parts(b["result"]) if b.get("result") else None} for b in boxes]}


def note(*lines, color="green") -> dict:
    return {"k": "note", "color": color, "lines": [_parts(l if isinstance(l, (list, tuple)) else [l]) for l in lines]}


def panel(title, *blocks) -> dict:
    return {"type": "panel", "title": title, "blocks": list(blocks)}
