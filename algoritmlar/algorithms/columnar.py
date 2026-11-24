"""Columnar transposition shifri."""
from core.helpers import error, only_letters, step
from core.visual import big_text, grid

META = {
    "id": "columnar",
    "name": "Columnar Transposition",
    "order": 70,
    "desc": "Matn jadvalga qator-qator yoziladi, so'ng ustunlar kalit tartibida o'qiladi.",
    "formula_enc": "Grid → ustunlarni kalit tartibida o'qish",
    "formula_dec": "Ustunlarni kalit tartibida to'ldirish → qator-qator o'qish",
    "map": "PLAINTEXT\n   ↓\nTABLE (grid)\n   ↓\nREORDER COLUMNS (key)\n   ↓\nREAD COLUMNS\n   ↓\nCIPHERTEXT",
    "weak": "Kalit permutatsiyasini (ustunlar soni kichik bo'lsa) qidirib topish mumkin.",
    "explainer": {
        "why": "Harflar joylashuvi o'zgaradi, qiymati o'zgarmaydi.",
        "how": "Jadvalga yoziladi, ustunlar kalit raqamlari tartibida o'qiladi.",
        "math": "Permutation of columns",
        "weak": "Kalit uzunligi qisqa bo'lsa brute-force mumkin.",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "THISISATESTMESSAGE"},
        {"id": "key", "label": "Kalit (raqamlar, masalan 3142; ko'pi bilan 9 ustun)", "type": "text", "default": "3142"},
    ],
    "examples": [["THISISATESTMESSAGE", "3142"]],
    "compare": {"name": "Columnar", "type": "Transposition", "operation": "Column order", "key": "Permutatsiya", "feature": "Jadval"},
}

PRACTICE = [
    {"lvl": "Murakkab", "text": "Columnar Transposition: 'THISISATESTMESSAGE' ni kalit 3142 bilan shifrlang.",
     "mode": "enc", "vals": {"pt": "THISISATESTMESSAGE", "key": "3142"}},
]


def _render(g, key, cur_r, cur_c, read_col):
    rows = []
    for r in range(len(g)):
        row = []
        for c in range(len(g[r])):
            v = g[r][c]
            cls = "filled" if v else "empty"
            if read_col is not None and c == read_col:
                cls = "readcol"
            elif r == cur_r and c == cur_c:
                cls = "current"
            row.append((v or "·", cls))
        rows.append(row)
    return grid(rows, header=list(key))


def run(mode, vals):
    digits = "".join(ch for ch in (vals.get("key") or "") if ch.isdigit())
    cols = len(digits)
    if cols < 2 or sorted(digits) != sorted(str(i + 1) for i in range(cols)) or cols > 9:
        return error("Kalit 1 dan n gacha bo'lgan raqamlarning permutatsiyasi bo'lishi kerak (masalan: 3142).")
    text = only_letters(vals.get("pt"))
    if not text:
        return error("Matn kiriting.")
    order = sorted(((int(d), i) for i, d in enumerate(digits)))
    steps = []

    if mode == "enc":
        while len(text) % cols:
            text += "X"
        rows = len(text) // cols
        g = [[None] * cols for _ in range(rows)]
        for i, ch in enumerate(text):
            r, c = divmod(i, cols)
            g[r][c] = ch
            steps.append(step(_render(g, digits, r, c, None),
                              f"'{ch}' jadvalning {r + 1}-qator, {c + 1}-ustuniga yozilmoqda."))
        result = ""
        for d, i in order:
            col = "".join(g[r][i] for r in range(rows))
            result += col
            steps.append(step(_render(g, digits, None, i, i),
                              f"Kalit raqami {d}: {i + 1}-ustun o'qilmoqda → \"{col}\"", row=[d, i + 1, col]))
        steps.append(step(big_text(f"Ciphertext: {result}"), "Barcha ustunlar kalit tartibida birlashtirildi."))
        return {"steps": steps, "result": result, "table_cols": ["Kalit raqami", "Ustun", "O'qilgan qator"]}

    if len(text) % cols:
        return error("Ciphertext uzunligi ustunlar soniga karrali bo'lishi kerak.")
    rows = len(text) // cols
    g = [[""] * cols for _ in range(rows)]
    pos = 0
    for d, i in order:
        col = text[pos: pos + rows]
        for r in range(rows):
            g[r][i] = col[r]
        pos += rows
        steps.append(step(_render(g, digits, None, i, i),
                          f"Kalit raqami {d}: {i + 1}-ustunga \"{col}\" yozilmoqda.", row=[d, i + 1, col]))
    result = "".join("".join(row) for row in g)
    steps.append(step(big_text(f"Plaintext: {result}"),
                      "Jadval qator-qator o'qilib, plaintext tiklandi (oxiridagi 'X' lar to'ldiruvchi bo'lishi mumkin)."))
    return {"steps": steps, "result": result, "table_cols": ["Kalit raqami", "Ustun", "Yozilgan qator"]}
