"""Barcha algoritmlar uchun umumiy matematik yordamchilar."""
from __future__ import annotations

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def mod(n: int, m: int) -> int:
    return n % m  # Python'da m > 0 bo'lsa natija doim manfiy emas


def l2n(ch: str) -> int:
    return ALPHA.index(ch.upper())


def n2l(n: int) -> str:
    return ALPHA[n % 26]


def only_letters(s: str | None) -> str:
    """Faqat A-Z harflarni qoldiradi (katta harfga o'tkazib)."""
    return "".join(ch for ch in (s or "").upper() if "A" <= ch <= "Z")


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def egcd(a: int, b: int):
    """Kengaytirilgan Evklid: (g, x, y), a*x + b*y = g."""
    if b == 0:
        return a, 1, 0
    g, x, y = egcd(b, a % b)
    return g, y, x - (a // b) * y


def mod_inverse(a: int, m: int):
    """a^-1 mod m yoki None (teskari yo'q bo'lsa)."""
    a %= m
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m


def to_bin8(n: int) -> str:
    return format(n, "08b")


def parse_int(value, default=None):
    """'5' -> 5; noto'g'ri bo'lsa default (JS parseInt'dan farqli: qat'iy)."""
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def error(msg: str) -> dict:
    return {"error": msg}


def step(visual, desc: str, answer=None, row=None) -> dict:
    """Bitta animatsiya qadami.
    visual – core.visual dagi spetsifikatsiya, desc – tushuntirish matni,
    answer – 'Amaliy rejim' uchun to'g'ri javob (harf), row – jadval qatori."""
    d = {"visual": visual, "desc": desc, "row": row}
    if answer is not None:
        d["answer"] = answer
    return d
