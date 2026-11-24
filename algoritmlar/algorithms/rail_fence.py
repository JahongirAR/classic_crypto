"""Rail Fence (zigzag) transposition shifri."""
from core.helpers import error, only_letters, parse_int, step
from core.visual import big_text, grid

META = {
    "id": "rail",
    "name": "Rail Fence Cipher",
    "order": 60,
    "desc": "Transposition — harflar zigzag shaklida qatorlarga joylashtiriladi, keyin qator-qator o'qiladi.",
    "formula_enc": "Zigzag joylashtirish → qatorlar bo'yicha o'qish",
    "formula_dec": "Qatorlarga taqsimlash → zigzag tartibida o'qish",
    "map": "PLAINTEXT\n   ↓\nZIGZAG TABLE (n rail)\n   ↓\nREAD ROW BY ROW\n   ↓\nCIPHERTEXT",
    "weak": "Rail soni kichik bo'lsa (odatda 2-6 oralig'ida), barcha variantlarni brute-force bilan sinab ko'rish oson.",
    "explainer": {
        "why": "Bu substitution emas — belgilar o'zgarmaydi, faqat joylashuvi o'zgaradi.",
        "how": "Harflar zigzag (yuqori-past) tartibda qatorlarga yoziladi, so'ng qator-qator o'qiladi.",
        "math": "Reorder / zigzag pattern",
        "weak": "Kichik rail sonida brute-force oson.",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "HELLOWORLD"},
        {"id": "rails", "label": "Rails soni (2-6)", "type": "number", "default": 3},
    ],
    "examples": [["HELLOWORLD", 3], ["ATTACKATDAWN", 2]],
    "compare": {"name": "Rail Fence", "type": "Transposition", "operation": "Reordering", "key": "Rail soni", "feature": "Joylashuv"},
}

PRACTICE = [
    {"lvl": "O'rta", "text": "Rail Fence: 3 rail yordamida 'HELLOWORLD' ni shifrlang.", "mode": "enc",
     "vals": {"pt": "HELLOWORLD", "rails": 3}},
]


def _render(table_, rails, length, current=None, read_row=None):
    rows = []
    for r in range(rails):
        row = []
        for c in range(length):
            v = table_[r][c]
            if v is None:
                row.append(("·", "empty"))
            elif read_row is not None and r == read_row:
                row.append((v, "readcol"))
            elif c == current:
                row.append((v, "current"))
            else:
                row.append((v, "filled"))
        rows.append(row)
    return grid(rows)


def _pattern(length, rails):
    pat, r, d = [], 0, 1
    for _ in range(length):
        pat.append(r)
        if r == 0:
            d = 1
        elif r == rails - 1:
            d = -1
        r += d
    return pat


def run(mode, vals):
    rails = parse_int(vals.get("rails"))
    if rails is None or rails < 2 or rails > 6:
        return error("Rails soni 2 dan 6 gacha bo'lishi kerak.")
    text = only_letters(vals.get("pt"))
    if not text:
        return error("Matn kiriting.")
    n = len(text)
    pattern = _pattern(n, rails)
    cols = ["#", "Belgi", "Rail"]
    steps = []
    g = [[None] * n for _ in range(rails)]

    if mode == "enc":
        fence = [[] for _ in range(rails)]
        for i, ch in enumerate(text):
            r = pattern[i]
            fence[r].append(ch)
            g[r][i] = ch
            steps.append(step(_render(g, rails, n, current=i),
                              f"'{ch}' harfi {r + 1}-rail (qator)ga joylashtirilmoqda.", row=[i + 1, ch, r + 1]))
        result = ""
        for r in range(rails):
            result += "".join(fence[r])
            steps.append(step(_render(g, rails, n, read_row=r),
                              f"{r + 1}-rail o'qilmoqda: \"{''.join(fence[r])}\""))
        steps.append(step(big_text(f"Ciphertext: {result}"),
                          "Barcha qatorlar birlashtirilib, yakuniy ciphertext hosil bo'ldi."))
        return {"steps": steps, "result": result, "table_cols": cols}

    counts = [pattern.count(r) for r in range(rails)]
    rows_chars, idx = [], 0
    for r in range(rails):
        rows_chars.append(list(text[idx: idx + counts[r]]))
        idx += counts[r]
    pos = [0] * rails
    result = ""
    for i in range(n):
        r = pattern[i]
        ch = rows_chars[r][pos[r]]
        pos[r] += 1
        g[r][i] = ch
        result += ch
        steps.append(step(_render(g, rails, n, current=i),
                          f"Pozitsiya {i + 1}: {r + 1}-raildan '{ch}' harfi olinmoqda.", row=[i + 1, ch, r + 1]))
    steps.append(step(big_text(f"Plaintext: {result}"), "Zigzag tartibida o'qilib, plaintext tiklandi."))
    return {"steps": steps, "result": result, "table_cols": cols}
