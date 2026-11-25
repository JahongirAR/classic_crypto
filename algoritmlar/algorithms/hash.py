"""Selectable cryptographic hash algorithms with a verification mode."""
import hashlib
import hmac
import re

from core.helpers import error, step
from core.visual import P, line, panel


ALGORITHMS = {
    "sha256": {
        "label": "SHA-256 (256 bit)",
        "name": "SHA-256",
        "digest_bits": 256,
        "block_size": 64,
        "length_size": 8,
        "word_bits": 32,
        "rounds": 64,
        "length_endian": "big",
    },
    "sha512": {
        "label": "SHA-512 (512 bit)",
        "name": "SHA-512",
        "digest_bits": 512,
        "block_size": 128,
        "length_size": 16,
        "word_bits": 64,
        "rounds": 80,
        "length_endian": "big",
    },
    "sha1": {
        "label": "SHA-1 (160 bit, eskirgan)",
        "name": "SHA-1",
        "digest_bits": 160,
        "block_size": 64,
        "length_size": 8,
        "word_bits": 32,
        "rounds": 80,
        "length_endian": "big",
    },
    "sha224": {
        "label": "SHA-224 (224 bit)",
        "name": "SHA-224",
        "digest_bits": 224,
        "block_size": 64,
        "length_size": 8,
        "word_bits": 32,
        "rounds": 64,
        "length_endian": "big",
    },
    "sha384": {
        "label": "SHA-384 (384 bit)",
        "name": "SHA-384",
        "digest_bits": 384,
        "block_size": 128,
        "length_size": 16,
        "word_bits": 64,
        "rounds": 80,
        "length_endian": "big",
    },
    "md5": {
        "label": "MD5 (128 bit, eskirgan)",
        "name": "MD5",
        "digest_bits": 128,
        "block_size": 64,
        "length_size": 8,
        "word_bits": 32,
        "rounds": 64,
        "length_endian": "little",
    },
}

_OPTIONS = [{"value": key, "label": data["label"]} for key, data in ALGORITHMS.items()]

META = {
    "id": "hash",
    "name": "Xesh funksiyalari (SHA / MD)",
    "order": 140,
    "desc": "Matn uchun SHA-256, SHA-512, SHA-1, SHA-224, SHA-384 yoki MD5 xeshini hisoblang va digestni tekshiring.",
    "formula_enc": "H = Hash(UTF-8(matn))",
    "formula_dec": "Tekshirish: Hash(matn) ≟ berilgan digest",
    "map": "KIRUVCHI MATN\n   ↓\nUTF-8 BAYTLAR\n   ↓\nPADDING: 1 BIT + NOLLAR + XABAR UZUNLIGI\n   ↓\nBLOKLARGA AJRATISH\n   ↓\nSIQISH RAUNDLARI\n   ↓\nYAKUNIY DIGEST (XESH)",
    "weak": "Xesh shifrlash emas — undan asl matnni qaytarib bo'lmaydi. MD5 va SHA-1 kolliziyalarga zaif va xavfsizlik uchun ishlatilmasligi kerak. Parollar uchun Argon2id yoki bcrypt kabi maxsus algoritm tanlang.",
    "explainer": {
        "why": "Xesh matnning o'zgarganini aniqlash va fayl yaxlitligini tekshirishga yordam beradi.",
        "how": "Matn UTF-8 baytlarga o'tkaziladi, padding qo'shiladi va algoritm bloklarni raundlar orqali qayta ishlab belgilangan uzunlikdagi digest yaratadi.",
        "math": "Deterministik, bir tomonlama o'zgartirish: H = Hash(m). Bir xil algoritm va matn doim bir xil digest beradi.",
        "weak": "Hashing shifrlash emas. MD5/SHA-1 eskirgan; parol xeshlash uchun oddiy SHA yoki MD ishlatmang.",
    },
    "inputs": [
        {"id": "algorithm", "label": "Xesh algoritmi", "type": "select", "options": _OPTIONS, "default": "sha256"},
        {"id": "pt", "label": "Matn (UTF-8)", "type": "text", "default": "abc"},
        {"id": "digest", "label": "Tekshirish uchun digest (ixtiyoriy)", "type": "text", "default": ""},
    ],
    "examples": [
        ["sha256", "abc", ""],
        ["md5", "abc", ""],
        ["sha512", "Salom, dunyo!", ""],
        ["sha256", "", ""],
    ],
    "compare": {
        "name": "SHA / MD",
        "type": "Hash function",
        "operation": "Blokli siqish raundlari",
        "key": "Yo'q",
        "feature": "Bir tomonlama, qat'iy uzunlikdagi digest",
    },
}

PRACTICE = [
    {
        "lvl": "Boshlang'ich",
        "text": "SHA-256 bilan 'abc' matnining xeshini toping.",
        "mode": "enc",
        "vals": {"algorithm": "sha256", "pt": "abc", "digest": ""},
        "answer": lambda out: out["data"]["digest"],
    },
]


def _padding_info(byte_length, block_size, length_size):
    padded_length = ((byte_length + 1 + length_size + block_size - 1) // block_size) * block_size
    zero_bytes = padded_length - byte_length - 1 - length_size
    return padded_length, zero_bytes


def run(mode, vals):
    algorithm = vals.get("algorithm", "sha256")
    details = ALGORITHMS.get(algorithm)
    if details is None:
        return error("Tanlangan xesh algoritmi mavjud emas.")
    if mode not in ("enc", "dec"):
        return error("Amal turi enc yoki dec bo'lishi kerak.")

    text = vals.get("pt", "")
    if not isinstance(text, str):
        return error("Kirish matni satr bo'lishi kerak.")
    message = text.encode("utf-8")
    byte_length = len(message)
    padded_length, zero_bytes = _padding_info(
        byte_length, details["block_size"], details["length_size"]
    )
    bit_length = byte_length * 8
    try:
        digest = hashlib.new(algorithm, message).hexdigest()
    except ValueError:
        return error(f"{details['name']} bu Python muhitida mavjud emas.")

    steps = [
        step(
            panel(
                f"{details['name']} PARAMETRLARI",
                line("Digest uzunligi: ", P(f"{details['digest_bits']} bit", "gold", True)),
                line("Blok: ", P(f"{details['block_size']} bayt", "cyan", True),
                     "  ·  So'z: ", P(f"{details['word_bits']} bit", "cyan", True)),
                line("Siqish raundlari: ", P(details["rounds"], "green", True)),
            ),
            f"{details['name']} tanlandi: {details['digest_bits']}-bitli digest va {details['block_size']}-baytli blok.",
        ),
        step(
            panel(
                "1. MATNNI BAYTLARGA O'TKAZISH",
                line("UTF-8 bayt uzunligi: ", P(f"{byte_length} bayt ({bit_length} bit)", "gold", True)),
                line("Kiritilgan matn (repr): ", P(repr(text), "slate")),
            ),
            f"Kiritilgan matn UTF-8 formatida {byte_length} bayt ({bit_length} bit) ga aylantirildi.",
            row=["UTF-8", byte_length, bit_length],
        ),
        step(
            panel(
                "2. PADDING",
                line("Xabar oxiriga 0x80 bayti qo'shiladi."),
                line("Keyin ", P(zero_bytes, "cyan", True), " ta nol bayti va ",
                     P(f"{details['length_size'] * 8}-bit", "gold", True),
                     " uzunlik qo'shiladi (", details["length_endian"], " endian)."),
                line("To'ldirilgan xabar: ", P(f"{padded_length} bayt", "green", True),
                     " = ", P(f"{padded_length // details['block_size']} blok", "green", True)),
            ),
            f"Paddingdan keyin {padded_length} bayt hosil bo'ldi; bu {details['block_size']}-baytli bloklarga bo'lindi.",
            row=["Padding", byte_length, zero_bytes, padded_length],
        ),
        step(
            panel(
                "3. BLOKLARNI SIQISH",
                line(f"Har bir {details['block_size']}-baytli blok algoritmning siqish funksiyasiga uzatiladi."),
                line(P(f"{details['rounds']} raund", "violet", True), " · ",
                     P(f"{details['word_bits']}-bitli so'zlar", "cyan", True),
                     " · Ichki holat yangilanadi."),
                line(P("Eslatma: raundlarning ichki qiymatlari standart Python hashlib orqali hisoblanadi; bu yerda sxematik ko'rsatilgan.", "slate")),
            ),
            f"{padded_length // details['block_size']} blok siqish funksiyasi orqali qayta ishlanadi.",
        ),
        step(
            panel(
                "4. YAKUNIY DIGEST",
                line(P(digest, "lime", True)),
            ),
            f"{details['name']} natijasi: {digest}",
            row=[details["name"], digest],
        ),
    ]

    if mode == "dec":
        supplied = str(vals.get("digest") or "").strip().lower()
        expected_length = details["digest_bits"] // 4
        if not re.fullmatch(rf"[0-9a-f]{{{expected_length}}}", supplied):
            return error(f"{details['name']} digesti aynan {expected_length} ta HEX belgidan iborat bo'lishi kerak.")
        matches = hmac.compare_digest(digest, supplied)
        verdict = "MOS — matn va digest mos keladi." if matches else "MOS EMAS — matn yoki digest o'zgargan."
        steps.append(step(
            panel(
                "5. DIGESTNI TEKSHIRISH",
                line("Kiritilgan digest: ", P(supplied, "slate")),
                line("Hisoblangan digest: ", P(digest, "cyan", True)),
                line(P(verdict, "green" if matches else "red", True)),
            ),
            verdict,
        ))
        result = verdict
    else:
        result = f"{details['name']}: {digest}"
        if algorithm in ("md5", "sha1"):
            steps.append(step(
                panel("XAVFSIZLIK ESLATMASI",
                      line(P(f"{details['name']} eskirgan; xavfsizlik maqsadida ishlatmang.", "red", True))),
                f"{details['name']} kolliziyalarga zaif va eskirgan.",
            ))

    return {
        "steps": steps,
        "result": result,
        "data": {"digest": digest, "matches": matches if mode == "dec" else None},
        "table_cols": ["Bosqich", "Tafsilot"],
    }
