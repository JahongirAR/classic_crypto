"""Vigenère shifri."""
from core.helpers import error, l2n, n2l, only_letters, step
from core.visual import flow

META = {
    "id": "vigenere",
    "name": "Vigenère Cipher",
    "order": 50,
    "desc": "Polyalphabetic shifr — kalit so'zi takrorlanib, har bir harfga alohida siljish beradi.",
    "formula_enc": "Cᵢ = (Pᵢ + Kᵢ) mod 26",
    "formula_dec": "Pᵢ = (Cᵢ - Kᵢ) mod 26",
    "map": "PLAINTEXT\n   ↓\nKEY takrorlanadi\n   ↓\nPᵢ + Kᵢ (mod 26)\n   ↓\nCIPHERTEXT",
    "weak": "Kalit uzunligi topilsa (Kasiski/Friedman testlari), har bir pozitsiya alohida Caesar sifatida yechiladi.",
    "explainer": {
        "why": "Bir nechta Caesar shifrini kalit yordamida birlashtiradi.",
        "how": "Kalit harfi takrorlanib, har bir harfga mos siljish beriladi.",
        "math": "Cᵢ=(Pᵢ+Kᵢ) mod 26",
        "weak": "Kalit uzunligi aniqlansa zaiflashadi.",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "ATTACKATDAWN"},
        {"id": "key", "label": "Key (so'z)", "type": "text", "default": "LEMON"},
    ],
    "examples": [["ATTACKATDAWN", "LEMON"], ["ATTACK", "KEY"]],
    "compare": {"name": "Vigenère", "type": "Polyalphabetic", "operation": "Addition mod", "key": "So'z", "feature": "Bir nechta alifbo"},
}

PRACTICE = [
    {"lvl": "O'rta", "text": "Vigenère: TEXT=ATTACK, KEY=KEY bilan shifrlang.", "mode": "enc", "vals": {"pt": "ATTACK", "key": "KEY"}},
]


def run(mode, vals):
    text = only_letters(vals.get("pt"))
    key = only_letters(vals.get("key"))
    if not text:
        return error("Matn kiriting.")
    if not key:
        return error("Kalit kiriting (faqat harflar).")
    steps, out = [], []
    for i, ch in enumerate(text):
        kch = key[i % len(key)]
        p, k = l2n(ch), l2n(kch)
        c = (p + k) % 26 if mode == "enc" else (p - k) % 26
        rc = n2l(c)
        out.append(rc)
        formula = f"({p}+{k}) mod 26" if mode == "enc" else f"({p}-{k}) mod 26"
        steps.append(step(
            flow(ch, (kch, "key"), (f"{p},{k}", "dim"), (formula, "formula"), (rc, "result")),
            f"Pozitsiya {i + 1}: '{ch}' (P={p}), kalit harfi '{kch}' (K={k}). {formula} = {c} → '{rc}'.",
            answer=rc, row=[i + 1, ch, kch, p, k, formula, rc]))
    return {"steps": steps, "result": "".join(out),
            "table_cols": ["#", "P", "K", "P qiymati", "K qiymati", "Formula", "C"]}
