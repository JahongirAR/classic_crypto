"""Caesar shifri."""
from core.helpers import error, l2n, n2l, only_letters, parse_int, step
from core.visual import flow

META = {
    "id": "caesar",
    "name": "Caesar Cipher",
    "order": 10,
    "desc": "Har bir harf alifboda k pozitsiyaga siljitiladi.",
    "formula_enc": "C = (P + k) mod 26",
    "formula_dec": "P = (C - k) mod 26",
    "map": "PLAINTEXT\n   ↓\nLETTER → NUMBER\n   ↓\n+ KEY (shift)\n   ↓\nMOD 26\n   ↓\nNUMBER → LETTER\n   ↓\nCIPHERTEXT",
    "weak": "Kalit fazosi atigi 26 ta qiymatdan iborat — brute-force hujumi bilan bir necha soniyada yechiladi.",
    "explainer": {
        "why": "Harflar alifboda siljitiladi.",
        "how": "P qiymatiga k qo'shiladi (yoki ayiriladi).",
        "math": "C=(P+k) mod 26",
        "weak": "Brute-force (26 ta variant).",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "HELLO"},
        {"id": "key", "label": "Key (shift, 0-25)", "type": "number", "default": 3},
    ],
    "examples": [["HELLO", 3], ["ATTACK", 7], ["CRYPTOGRAPHY", 5]],
    "compare": {"name": "Caesar", "type": "Substitution", "operation": "Shift", "key": "Son", "feature": "Juda sodda"},
}

PRACTICE = [
    {"lvl": "Boshlang'ich", "text": "Caesar bilan 'SALOM' ni 3 ga siljiting.", "mode": "enc", "vals": {"pt": "SALOM", "key": 3}},
]


def run(mode, vals):
    k = parse_int(vals.get("key"))
    if k is None:
        return error("Kalit son bo'lishi kerak.")
    text = only_letters(vals.get("pt"))
    if not text:
        return error("Matn kiriting (faqat A-Z harflar ishlatiladi).")
    sign = 1 if mode == "enc" else -1
    steps, out = [], []
    for ch in text:
        p = l2n(ch)
        c = (p + sign * k) % 26
        rc = n2l(c)
        out.append(rc)
        formula = f"({p}+{k}) mod 26" if mode == "enc" else f"({p}-{k}) mod 26"
        steps.append(step(
            flow(ch, (p, "dim"), (f"k={k}", "key"), (formula, "formula"), (c, "dim"), (rc, "result")),
            f"'{ch}' harfi {p} qiymatiga ega. {formula} = {c} → '{rc}'.",
            answer=rc, row=[ch, p, k, formula, c, rc]))
    return {"steps": steps, "result": "".join(out),
            "table_cols": ["Belgi", "P", "Key", "Formula", "Natija (son)", "Natija (harf)"]}
