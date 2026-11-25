"""Affine shifri: C = (aP + b) mod 26."""
from core.helpers import error, gcd, l2n, mod_inverse, n2l, only_letters, parse_int, step
from core.visual import P, flow, line, panel, table

META = {
    "id": "affine",
    "name": "Affine Cipher",
    "order": 40,
    "desc": "Chiziqli funksiya asosida shifrlash: C=(aP+b) mod 26.",
    "formula_enc": "C = (aP + b) mod 26",
    "formula_dec": "P = a⁻¹(C - b) mod 26",
    "map": "PLAINTEXT\n   ↓\nLETTER → NUMBER (P)\n   ↓\naP + b\n   ↓\nMOD 26\n   ↓\nNUMBER → LETTER\n   ↓\nCIPHERTEXT",
    "weak": "Kichik kalit fazosi (faqat 12 ta mumkin bo'lgan 'a' qiymati) va frequency analysis'ga zaif.",
    "explainer": {
        "why": "Chiziqli (linear) matematik funksiya ishlatiladi.",
        "how": "P songa a ko'paytiriladi, b qo'shiladi, mod 26 olinadi.",
        "math": "C=(aP+b) mod 26",
        "weak": "Kichik kalit fazosi + frequency analysis.",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "HELLO"},
        {"id": "a", "label": "a (gcd(a,26)=1 bo'lishi kerak)", "type": "number", "default": 5},
        {"id": "b", "label": "b (0-25)", "type": "number", "default": 8},
    ],
    "examples": [["HELLO", 5, 8], ["AFFINE", 7, 3]],
    "compare": {"name": "Affine", "type": "Substitution", "operation": "Linear mod", "key": "a, b", "feature": "Matematik"},
}

PRACTICE = [
    {"lvl": "O'rta", "text": "Affine: a=5, b=8 bilan 'HELLO' ni shifrlang.", "mode": "enc", "vals": {"pt": "HELLO", "a": 5, "b": 8}},
]


def _ainv_panel(a, m=26):
    """a⁻¹ mod m ni kengaytirilgan Evklid bilan hisoblash jadvali."""
    r0, r1, s0, s1 = m, a % m, 0, 1
    rows = []
    while r1 > 0:
        q = r0 // r1
        r2 = r0 - q * r1
        s2 = s0 - q * s1
        rows.append([r0, r1, q, r2, s0, s1, s2])
        r0, r1, s0, s1 = r1, r2, s1, s2
    inv = s0 % m
    return panel(
        f"a = {a} uchun a⁻¹ mod {m} (Kengaytirilgan Evklid algoritmi)",
        line(P(f"Tekshiruv: {a} × {inv} mod {m} = {(a * inv) % m}  ✓  (1 bo'lishi kerak)", "lime")),
        table(rows, head=["r₀", "r₁", "q = ⌊r₀/r₁⌋", "r₂ = r₀ − q·r₁", "s₀", "s₁", "s₂ = s₀ − q·s₁"]),
        line(P(f"a⁻¹ = {inv}  →  {a} × {inv} ≡ 1 (mod {m})", "gold", True), gap=True),
    )


def run(mode, vals):
    a, b = parse_int(vals.get("a")), parse_int(vals.get("b"))
    text = only_letters(vals.get("pt"))
    if not text:
        return error("Matn kiriting.")
    if a is None or b is None:
        return error("a va b son bo'lishi kerak.")
    if gcd(a % 26, 26) != 1:
        return error(f"gcd({a},26) ≠ 1 — bu 'a' qiymati yaroqsiz. Faqat 26 bilan o'zaro tub sonlar "
                     f"ishlatiladi (1,3,5,7,9,11,15,17,19,21,23,25).")
    ainv = mod_inverse(a, 26)
    steps, out = [], []
    for ch in text:
        if mode == "enc":
            p = l2n(ch)
            c = (a * p + b) % 26
            rc = n2l(c)
            formula = f"({a}×{p}+{b}) mod 26 = {c}"
            val = p
        else:
            c = l2n(ch)
            p = (ainv * (c - b)) % 26
            rc = n2l(p)
            formula = f"{ainv}×({c}-{b}) mod 26 = {p}"
            val = c
        out.append(rc)
        steps.append(step(flow(ch, (val, "dim"), (formula, "formula"), (rc, "result")),
                          f"'{ch}' → {formula} → '{rc}'.", answer=rc, row=[ch, val, formula, rc]))
    return {"steps": steps, "result": "".join(out), "table_cols": ["Belgi", "Qiymat", "Formula", "Natija"],
            "extra": _ainv_panel(a)}
