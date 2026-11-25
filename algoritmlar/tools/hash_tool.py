"""Selectable teaching tool for common message-digest algorithms."""
import hashlib


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

META = {
    "id": "hash",
    "title": "Xesh funksiyalari",
    "subtitle": "SHA va MD xeshlarini hisoblash",
    "order": 45,
    "kind": "form",
    "heading": "🔐 Xesh funksiyalari",
    "intro": "Matn uchun SHA-256, SHA-512, SHA-1, SHA-224, SHA-384 yoki MD5 xeshini hisoblang. Xesh bir tomonlama: undan asl matnni tiklab bo'lmaydi.",
    "sections": [{
        "id": "main",
        "tab": "Matn → Xesh",
        "button": "= Xesh hisobla",
        "auto": True,
        "fields": [
            {
                "id": "algorithm",
                "label": "XESH ALGORITMI",
                "type": "select",
                "options": [
                    {"value": key, "label": details["label"]}
                    for key, details in ALGORITHMS.items()
                ],
                "default": "sha256",
            },
            {
                "id": "text",
                "label": "KIRUVCHI MATN",
                "type": "textarea",
                "default": "Salom, dunyo!",
                "placeholder": "Xeshlanadigan matnni kiriting",
                "wide": True,
            },
        ],
        "examples": [
            {"label": "SHA-256: abc", "vals": {"algorithm": "sha256", "text": "abc"}},
            {"label": "MD5: abc", "vals": {"algorithm": "md5", "text": "abc"}},
            {"label": "Bo'sh matn", "vals": {"algorithm": "sha256", "text": ""}},
            {"label": "O'zbekcha matn", "vals": {"algorithm": "sha512", "text": "Salom, dunyo!"}},
        ],
    }],
}


def _padding_info(byte_length, block_size, length_size):
    padded_length = ((byte_length + 1 + length_size + block_size - 1) // block_size) * block_size
    zero_bytes = padded_length - byte_length - 1 - length_size
    return padded_length, zero_bytes


def handle(action, payload):
    if action != "run":
        return {"error": f"Noma'lum amal: {action}"}
    if payload.get("section") != "main":
        return {"error": "Noma'lum bo'lim."}

    vals = payload.get("vals") or {}
    algorithm = vals.get("algorithm", "sha256")
    details = ALGORITHMS.get(algorithm)
    if details is None:
        return {"blocks": [{"k": "error", "t": "Tanlangan xesh algoritmi mavjud emas."}]}

    text = vals.get("text", "")
    if not isinstance(text, str):
        return {"blocks": [{"k": "error", "t": "Kirish matni satr bo'lishi kerak."}]}
    message = text.encode("utf-8")
    byte_length = len(message)
    padded_length, zero_bytes = _padding_info(
        byte_length, details["block_size"], details["length_size"]
    )
    bit_length = byte_length * 8
    try:
        digest = hashlib.new(algorithm, message).hexdigest()
    except ValueError:
        return {"blocks": [{
            "k": "error",
            "t": f"{details['name']} bu Python muhitida mavjud emas.",
        }]}

    return {"blocks": [
        {"k": "box", "title": f"NATIJA: {details['name']} xeshi", "value": digest},
        {"k": "boxes", "small": True, "items": [
            {"label": "Algoritm", "value": details["name"]},
            {"label": "Xesh uzunligi", "value": f"{details['digest_bits']} bit"},
            {"label": "UTF-8 kirish uzunligi", "value": f"{byte_length} bayt ({bit_length} bit)"},
        ]},
        {"k": "heading", "t": "📋 Hisoblash bosqichlari"},
        {"k": "step", "num": "1", "lines": [
            f"Kiritilgan matn UTF-8 baytlariga o'tkazildi: {byte_length} bayt.",
        ]},
        {"k": "step", "num": "2", "lines": [
            f"Padding: 0x80 bayti, {zero_bytes} ta nol bayti va {details['length_size'] * 8} bitli uzunlik qo'shiladi.",
            f"Uzunlik maydoni {details['length_endian']} endian tartibida; to'ldirilgan xabar {padded_length} bayt.",
        ]},
        {"k": "step", "num": "3", "lines": [
            f"Xabar {details['block_size']} baytli bloklarga ajratiladi: {padded_length // details['block_size']} blok.",
            f"Har blok {details['rounds']} ta {details['word_bits']}-bitli raunddan o'tkaziladi.",
        ]},
        {"k": "step", "num": "4", "lines": [
            f"{details['name']} yakuniy digestni hosil qildi: {digest}",
        ]},
        {"k": "step", "num": "!", "lines": [
            "MD5 va SHA-1 eskirgan, kolliziyaga chidamsiz algoritmlar. Parol saqlash uchun oddiy xesh emas, Argon2id yoki bcrypt kabi maxsus algoritm ishlating.",
        ]} if algorithm in ("md5", "sha1") else {
            "k": "step", "num": "✓", "lines": [
                "Xesh bir tomonlama; bir xil kirish va algoritm doim bir xil digest beradi.",
            ],
        },
    ]}
