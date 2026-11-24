"""Atbash shifri."""
from core.helpers import error, l2n, n2l, only_letters, step
from core.visual import flow

META = {
    "id": "atbash",
    "name": "Atbash Cipher",
    "order": 20,
    "desc": "Alifbo teskarisiga aylantiriladi: A↔Z, B↔Y, ...",
    "formula_enc": "C = (25 - P) mod 26",
    "formula_dec": "P = (25 - C) mod 26 (o'zi bilan simmetrik)",
    "map": "PLAINTEXT\n   ↓\nLETTER → NUMBER (P)\n   ↓\n25 - P\n   ↓\nNUMBER → LETTER\n   ↓\nCIPHERTEXT",
    "weak": "Kalitsiz, deterministik almashtirish — hech qanday xavfsizlik bermaydi, darhol aniqlanadi.",
    "explainer": {
        "why": "Alifbo teskari tartibda almashtiriladi.",
        "how": "Har bir harf o'zining alifbodagi 'oyna' juftligiga aylanadi.",
        "math": "C=(25-P) mod 26",
        "weak": "Kalit yo'q — bir xil natija har doim.",
    },
    "inputs": [{"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "HELLO"}],
    "examples": [["HELLO"], ["ATBASH"], ["CRYPTOGRAPHY"]],
    "compare": {"name": "Atbash", "type": "Substitution", "operation": "Mapping", "key": "Yo'q", "feature": "Teskari alifbo"},
}

PRACTICE = [
    {"lvl": "Boshlang'ich", "text": "Atbash bilan 'HELLO' ni shifrlang.", "mode": "enc", "vals": {"pt": "HELLO"}},
]


def run(mode, vals):
    text = only_letters(vals.get("pt"))
    if not text:
        return error("Matn kiriting (faqat A-Z harflar ishlatiladi).")
    steps, out = [], []
    for ch in text:
        p = l2n(ch)
        c = 25 - p
        rc = n2l(c)
        out.append(rc)
        steps.append(step(
            flow(ch, (p, "dim"), (f"25-{p}", "formula"), (c, "dim"), (rc, "result")),
            f"'{ch}' → {p}. 25-{p}={c} → '{rc}'.", answer=rc, row=[ch, p, f"25-{p}", c, rc]))
    return {"steps": steps, "result": "".join(out),
            "table_cols": ["Belgi", "P", "Formula", "Natija (son)", "Natija (harf)"]}
