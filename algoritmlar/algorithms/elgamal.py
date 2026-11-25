"""ElGamal public-key encryption demo over a small prime field."""
import re

from algorithms.rsa import is_prime
from core.helpers import error, mod_inverse, step
from core.visual import P, line, panel

MAX_P = 2_147_483_647
MAX_DIGITS = 10

META = {
    "id": "elgamal",
    "name": "ElGamal Cipher",
    "order": 130,
    "desc": "Ochiq kalitli shifrlash: tub modul, generator va maxfiy kalit asosida matnni shifrlang.",
    "formula_enc": "C₁ = gᵏ mod p;  C₂ = M·yᵏ mod p",
    "formula_dec": "M = C₂·(C₁ˣ)⁻¹ mod p",
    "map": "MATN (har bir belgi M kodi)\n   ↓\nOCHIQ KALIT: y = gˣ mod p\n   ↓\nHAR BELGI UCHUN ALOHIDA k\n   ↓\n(C₁, C₂) = (gᵏ, M·yᵏ) mod p\n   ↓\nDESHIFRLASH: M = C₂·(C₁ˣ)⁻¹ mod p\n   ↓\nMATN TIKLANDI",
    "weak": "Bu kichik sonli o'quv namoyishi, haqiqiy himoya uchun emas. Har bir belgi uchun k alohida va tasodifiy tanlanadi; k ni qayta ishlatish yoki oshkor qilish xavfli. Amaliy tizimlarda ElGamal'ni xavfsiz padding va tasdiqlangan kutubxonalar bilan ishlating.",
    "explainer": {
        "why": "Ochiq kalitli shifrlash: y ochiq kalit, x maxfiy kalit bo'lib, shifrlash va deshifrlash kalitlari turlicha.",
        "how": "y=gˣ mod p. Har bir M belgisi o'zining k qiymati bilan (C₁,C₂) juftligiga o'tadi; x maxfiy kaliti juftlikni qaytaradi.",
        "math": "Modulyar darajaga ko'tarish va ko'paytirishning modular teskarisi.",
        "weak": "Kichik p ni sinab ko'rish oson; k ni takrorlash yoki oshkor qilish plaintext haqidagi ma'lumotni sizdirishi mumkin.",
    },
    "inputs": [
        {"id": "p", "label": "Tub modul p (harf kodidan katta)", "type": "text", "default": "467"},
        {"id": "g", "label": "Generator g (mod p)", "type": "text", "default": "2"},
        {"id": "x", "label": "Maxfiy kalit x (1 dan p−2 gacha)", "type": "text", "default": "127"},
        {"id": "ks", "label": "Alohida k qiymatlari (har bir belgi uchun, vergul bilan)", "type": "text",
         "default": "53, 89, 101, 151, 177"},
        {"id": "pt", "label": "Plaintext / Ciphertext (C₁:C₂; C₁:C₂; ...)", "type": "text", "default": "SALOM"},
    ],
    "examples": [
        ["467", "2", "127", "53, 89, 101, 151, 177", "SALOM"],
        ["467", "2", "127", "53, 89", "HI"],
    ],
    "compare": {
        "name": "ElGamal",
        "type": "Asymmetric / Public-key",
        "operation": "Diffie–Hellman muammosi",
        "key": "(p, g, y) ochiq; x maxfiy",
        "feature": "Har shifrlashda tasodifiy k ishlatadi",
    },
}

PRACTICE = [
    {
        "lvl": "Murakkab",
        "text": "ElGamal: p=467, g=2, x=127 va ko'rsatilgan k qiymatlari bilan 'HI' ni shifrlang.",
        "mode": "enc",
        "vals": {"p": "467", "g": "2", "x": "127", "ks": "53, 89", "pt": "HI"},
        "answer": lambda out: out["data"]["cipher"],
    },
]


def _integer(value, name):
    text = str(value or "").strip()
    if len(text) > MAX_DIGITS or not re.fullmatch(r"[0-9]+", text):
        raise ValueError(f"{name} musbat butun son bo'lishi kerak (ko'pi bilan {MAX_DIGITS} xona)")
    return int(text)


def _prime_factors(n):
    factors = []
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            factors.append(divisor)
            while n % divisor == 0:
                n //= divisor
        divisor += 1 if divisor == 2 else 2
    if n > 1:
        factors.append(n)
    return factors


def _parameters(vals):
    p = _integer(vals.get("p"), "p")
    if p < 5 or p > MAX_P:
        raise ValueError(f"p 5 dan {MAX_P:,} gacha bo'lishi kerak")
    if not is_prime(p):
        raise ValueError(f"p = {p} tub son emas")

    g = _integer(vals.get("g"), "g")
    if not 1 < g < p:
        raise ValueError("Generator g uchun 1 < g < p bo'lishi kerak")
    if any(pow(g, (p - 1) // q, p) == 1 for q in _prime_factors(p - 1)):
        raise ValueError(f"g = {g} soni p = {p} modul bo'yicha generator emas")

    x = _integer(vals.get("x"), "x")
    if not 1 <= x <= p - 2:
        raise ValueError("Maxfiy kalit x uchun 1 ≤ x ≤ p−2 bo'lishi kerak")
    return p, g, x, pow(g, x, p)


def _parse_values(value, name):
    tokens = [part for part in re.split(r"[\s,;]+", str(value or "").strip()) if part]
    if not tokens:
        raise ValueError(f"{name} qiymatlarini kiriting")
    return [_integer(token, f"{i + 1}-{name}") for i, token in enumerate(tokens)]


def _parse_cipher(value, p):
    pairs = [part.strip() for part in str(value or "").split(";") if part.strip()]
    if not pairs:
        raise ValueError("Ciphertext kiriting: C₁:C₂; C₁:C₂; ...")
    result = []
    for i, pair in enumerate(pairs):
        pieces = pair.split(":")
        if len(pieces) != 2:
            raise ValueError(f"{i + 1}-juftlik noto'g'ri. Format: C₁:C₂")
        c1, c2 = (_integer(part.strip(), f"{i + 1}-juftlik") for part in pieces)
        if not 1 <= c1 < p or not 0 <= c2 < p:
            raise ValueError(f"{i + 1}-juftlik uchun 1 ≤ C₁ < p va 0 ≤ C₂ < p bo'lishi kerak")
        result.append((c1, c2))
    return result


def live(vals):
    try:
        p, g, x, y = _parameters(vals)
        return panel(
            "ELGAMAL KALITLARI",
            line("Modul p = ", P(p, "gold", True), "  ·  Generator g = ", P(g, "cyan", True)),
            line("Ochiq kalit y = gˣ mod p = ", P(y, "green", True)),
            line("Maxfiy kalit x = ", P(x, "violet", True), "  ·  ", P("✓ parametrlar to'g'ri", "lime")),
            line(P("Shifrlashda matndagi har bir belgi uchun alohida k qiymati kerak.", "slate")),
        )
    except ValueError as exc:
        return panel("ELGAMAL KALITLARI", line(P(f"✗ {exc}", "red")))


def run(mode, vals):
    try:
        p, g, x, y = _parameters(vals)
    except ValueError as exc:
        return error(str(exc))

    steps = [
        step(
            panel(
                "ELGAMAL KALITLARI",
                line("Tub modul p = ", P(p, "gold", True)),
                line("Generator g = ", P(g, "cyan", True)),
                line("Maxfiy kalit x = ", P(x, "violet", True)),
                line("Ochiq kalit y = gˣ mod p = ", P(f"{g}^{x} mod {p} = {y}", "green", True)),
            ),
            f"Ochiq kalit (p, g, y) = ({p}, {g}, {y}); maxfiy kalit x = {x}.",
        )
    ]

    text = str(vals.get("pt") or "")
    if mode == "enc":
        if not text:
            return error("Shifrlash uchun matn kiriting.")
        codes = [ord(ch) for ch in text]
        if 0 in codes:
            return error("ElGamal uchun har bir belgi kodi 1 dan katta yoki teng bo'lishi kerak.")
        if max(codes) >= p:
            return error(f"Eng katta belgi kodi {max(codes)}. Uni kodlash uchun p > {max(codes)} tub sonini tanlang.")
        try:
            ks = _parse_values(vals.get("ks"), "k")
        except ValueError as exc:
            return error(str(exc))
        if len(ks) != len(text):
            return error(f"Matnda {len(text)} ta belgi bor; har biri uchun alohida k kerak (hozir {len(ks)} ta).")
        pairs = []
        for i, (ch, m, k) in enumerate(zip(text, codes, ks)):
            if not 1 <= k <= p - 2:
                return error(f"{i + 1}-k qiymati 1 ≤ k ≤ p−2 ({p - 2}) oralig'ida bo'lishi kerak.")
            c1 = pow(g, k, p)
            shared = pow(y, k, p)
            c2 = m * shared % p
            pairs.append((c1, c2))
            steps.append(step(
                panel(
                    f"{i + 1}-belgi: '{ch}' (M = {m})",
                    line("Tanlangan nonce k = ", P(k, "violet", True)),
                    line("C₁ = gᵏ mod p = ", P(f"{g}^{k} mod {p} = {c1}", "cyan", True)),
                    line("Umumiy sir s = yᵏ mod p = ", P(f"{y}^{k} mod {p} = {shared}", "gold", True)),
                    line("C₂ = M·s mod p = ", P(f"{m}·{shared} mod {p} = {c2}", "green", True)),
                    line("Shifr juftligi: ", P(f"({c1}, {c2})", "lime", True)),
                ),
                f"'{ch}' (M={m}) uchun k={k}: C₁={c1}, C₂={c2}.",
                row=[i + 1, f"'{ch}'", m, k, c1, shared, c2],
            ))
        cipher = "; ".join(f"{c1}:{c2}" for c1, c2 in pairs)
        return {
            "steps": steps,
            "result": f"Shifrmatn (C₁:C₂): {cipher}",
            "data": {"cipher": cipher},
            "table_cols": ["#", "Belgi", "M kodi", "Nonce k", "C₁", "Sir yᵏ", "C₂"],
        }

    if mode != "dec":
        return error("Amal turi enc yoki dec bo'lishi kerak.")
    try:
        pairs = _parse_cipher(text, p)
    except ValueError as exc:
        return error(str(exc))

    chars = []
    for i, (c1, c2) in enumerate(pairs):
        shared = pow(c1, x, p)
        inverse = mod_inverse(shared, p)
        if inverse is None:
            return error(f"{i + 1}-juftlik uchun modular teskari mavjud emas.")
        m = c2 * inverse % p
        if m > 0x10FFFF or 0xD800 <= m <= 0xDFFF:
            return error(f"{i + 1}-juftlik noto'g'ri: M={m} Unicode belgisi emas.")
        ch = chr(m)
        chars.append(ch)
        steps.append(step(
            panel(
                f"{i + 1}-juftlik: (C₁, C₂) = ({c1}, {c2})",
                line("Umumiy sir s = C₁ˣ mod p = ", P(f"{c1}^{x} mod {p} = {shared}", "gold", True)),
                line("s⁻¹ mod p = ", P(f"{inverse}", "cyan", True)),
                line("M = C₂·s⁻¹ mod p = ", P(f"{c2}·{inverse} mod {p} = {m}", "green", True)),
                line("Tiklangan belgi: ", P(f"'{ch}'", "lime", True)),
            ),
            f"({c1}, {c2}) juftligi deshifrlandi: M={m} → '{ch}'.",
            row=[i + 1, c1, c2, shared, inverse, m, f"'{ch}'"],
        ))
    plaintext = "".join(chars)
    return {
        "steps": steps,
        "result": f"Tiklangan matn: {plaintext}",
        "data": {"text": plaintext},
        "table_cols": ["#", "C₁", "C₂", "Sir C₁ˣ", "Sir⁻¹", "M kodi", "Belgi"],
    }
