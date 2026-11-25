"""XOR shifri (bayt darajasida, UTF-8)."""
import re

from core.helpers import error, step, to_bin8
from core.visual import P, line, panel

META = {
    "id": "xor",
    "name": "XOR Cipher",
    "order": 90,
    "desc": "Bitwise XOR amali orqali shifrlash. C = P ⊕ K, va P = C ⊕ K (simmetrik).",
    "formula_enc": "C = P ⊕ K",
    "formula_dec": "P = C ⊕ K",
    "map": "TEXT\n ↓\nASCII\n ↓\nBINARY\n ↓\nXOR KEY\n ↓\nBINARY\n ↓\nRESULT (kod)",
    "weak": "Bir xil kalit qayta ishlatilsa (kalit takrorlansa) statistik tahlil orqali buzish mumkin. "
            "Faqat bir martalik, tasodifiy va matn uzunligidagi kalit (One-Time Pad) nazariy jihatdan buzilmasdir.",
    "explainer": {
        "why": "Bitlar darajasida XOR mantiqiy amali qo'llaniladi.",
        "how": "Har bir belgi ASCII/binary ko'rinishga o'tkaziladi va kalit biti bilan XOR qilinadi.",
        "math": "C=P⊕K, P=C⊕K",
        "weak": "Takroriy kalit → statistik tahlil; OTP bilan taqqoslang.",
    },
    "inputs": [
        {"id": "pt", "label": "Matn (Encrypt) yoki shifr kodlari (Decrypt)", "type": "text", "default": "HI"},
        {"id": "key", "label": "Key (matn)", "type": "text", "default": "K"},
        {"id": "fmt", "label": "Decrypt'da kodlar formati", "type": "select", "default": "dec",
         "options": [{"value": "dec", "label": "Decimal (3, 2)"}, {"value": "hex", "label": "Hex (03 02)"}]},
    ],
    "examples": [["HI", "K", "dec"], ["CRYPTO", "XOR", "dec"], ["3, 2", "K", "dec"]],
    "compare": {"name": "XOR", "type": "Bitwise", "operation": "XOR", "key": "Bit/string", "feature": "Binary"},
}

PRACTICE = [
    {"lvl": "Boshlang'ich", "text": "XOR: 'HI' matnini 'K' kaliti bilan shifrlab, natija kodlarini yozing (vergul bilan, masalan 3,2).",
     "mode": "enc", "vals": {"pt": "HI", "key": "K"}, "answer": lambda out: ",".join(map(str, out["data"]["codes"]))},
    {"lvl": "Murakkab", "text": "XOR: 'CRYPTO' matnini 'XOR' kaliti bilan shifrlang (kodlarni vergul bilan yozing).",
     "mode": "enc", "vals": {"pt": "CRYPTO", "key": "XOR"}, "answer": lambda out: ",".join(map(str, out["data"]["codes"]))},
]


def _label(b):
    return chr(b) if 32 <= b < 127 else f"0x{b:02X}"


def _parse_codes(s, fmt):
    tokens = [t for t in re.split(r"[\s,;]+", s.strip()) if t]
    if not tokens:
        raise ValueError("Shifr kodlarini kiriting.")
    out = []
    for t in tokens:
        try:
            v = int(t, 16) if fmt == "hex" else int(t)
        except ValueError:
            raise ValueError(f"'{t}' {'hex' if fmt == 'hex' else 'decimal'} kod emas. Decrypt uchun shifr kodlarini kiriting "
                             f"(masalan: 3, 2) va kerak bo'lsa formatni tanlang.")
        if not 0 <= v <= 255:
            raise ValueError(f"Kod {v} bayt oralig'idan (0–255) tashqarida.")
        out.append(v)
    return out


def run(mode, vals):
    key = (vals.get("key") or "").encode("utf-8")
    raw = vals.get("pt") or ""
    if not raw.strip():
        return error("Matn kiriting.")
    if not key:
        return error("Kalit kiriting.")
    try:
        data = list(raw.encode("utf-8")) if mode == "enc" else _parse_codes(raw, vals.get("fmt") or "dec")
    except ValueError as e:
        return error(str(e))

    steps, res = [], []
    for i, p in enumerate(data):
        k = key[i % len(key)]
        c = p ^ k
        res.append(c)
        pb, kb, cb = to_bin8(p), to_bin8(k), to_bin8(c)
        steps.append(step(
            panel(f"{i + 1}-BAYT",
                  line(f"'{_label(p)}' → ASCII {p} → ", P(pb, "cyan", True)),
                  line(f"XOR kalit '{_label(k)}' → ASCII {k} → ", P(kb, "pink", True)),
                  line(P("─" * 24, "dim")),
                  line(P(f"{cb}  (decimal {c})", "lime", True))),
            f"'{_label(p)}' ({pb}) XOR '{_label(k)}' ({kb}) = {cb} ({c}).",
            row=[i + 1, _label(p), p, pb, _label(k), kb, cb, c]))
    hexs = " ".join(f"{c:02x}" for c in res)
    if mode == "enc":
        result = f"Kodlar: [{', '.join(map(str, res))}]  |  Hex: {hexs}"
    else:
        text = bytes(res).decode("utf-8", errors="replace")
        result = f"Tiklangan matn: {text}   (kodlar: [{', '.join(map(str, res))}])"
    return {"steps": steps, "result": result, "data": {"codes": res, "hex": hexs},
            "table_cols": ["#", "Belgi", "ASCII", "Binary", "Key belgi", "Key binary", "XOR binary", "Natija (dec)"]}
