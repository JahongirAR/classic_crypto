"""Monoalphabetic substitution (kalit alifbosi bilan)."""
import random

from core.helpers import ALPHA, error, only_letters, step
from core.visual import flow

META = {
    "id": "mono",
    "name": "Monoalphabetic Substitution",
    "order": 30,
    "desc": "Har bir harf o'zboshimcha, lekin barqaror boshqa harfga almashtiriladi (kalit alifbosi orqali).",
    "formula_enc": "C = KeyAlphabet[ index(P) ]",
    "formula_dec": "P = PlainAlphabet[ index(C) ]",
    "map": "PLAINTEXT\n   ↓\nLETTER INDEX (0-25)\n   ↓\nCIPHER ALPHABET[index]\n   ↓\nCIPHERTEXT",
    "weak": "Harflar chastotasi saqlanib qoladi — frequency analysis orqali kalitni tiklash mumkin.",
    "explainer": {
        "why": "Har bir harfga mos, lekin tasodifiy boshqa harf tayinlanadi.",
        "how": "Kalit alifbosidagi mos pozitsiyadagi harf olinadi.",
        "math": "C = KeyAlphabet[index(P)]",
        "weak": "Frequency analysis (harflar chastotasi).",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "HELLO"},
        {"id": "key", "label": "Kalit alifbosi (26 ta noyob A-Z harf)", "type": "text", "default": "QWERTYUIOPASDFGHJKLZXCVBNM"},
    ],
    "examples": [["HELLO", "QWERTYUIOPASDFGHJKLZXCVBNM"]],
    "actions": [{"id": "random_key", "label": "Random key"}],
    "compare": {"name": "Monoalphabetic", "type": "Substitution", "operation": "Mapping", "key": "Alifbo", "feature": "Frequency analysis"},
}


def action_random_key(vals):
    arr = list(ALPHA)
    random.shuffle(arr)
    return {"fill": {"key": "".join(arr)}}


ACTIONS = {"random_key": action_random_key}


def run(mode, vals):
    text = only_letters(vals.get("pt"))
    key = only_letters(vals.get("key"))
    if not text:
        return error("Matn kiriting.")
    if len(key) != 26 or len(set(key)) != 26:
        return error("Kalit alifbosi aynan 26 ta noyob A-Z harfdan iborat bo'lishi kerak.")
    steps, out = [], []
    for ch in text:
        if mode == "enc":
            idx = ALPHA.index(ch)
            rc = key[idx]
            lbl = f"Key[{idx}]"
            desc = f"'{ch}' alifboda {idx}-o'rinda. Kalit alifbosining {idx}-o'rnidagi harfi: '{rc}'."
        else:
            idx = key.index(ch)
            rc = ALPHA[idx]
            lbl = f"Plain[{idx}]"
            desc = f"'{ch}' kalit alifbosida {idx}-o'rinda. Oddiy alifboning {idx}-o'rnidagi harfi: '{rc}'."
        out.append(rc)
        steps.append(step(flow(ch, (f"index={idx}", "dim"), (lbl, "formula"), (rc, "result")),
                          desc, answer=rc, row=[ch, idx, rc]))
    return {"steps": steps, "result": "".join(out), "table_cols": ["Belgi", "Index", "Natija"]}
