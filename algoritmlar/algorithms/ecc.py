"""Educational elliptic-curve arithmetic over a small prime field."""
import math
import re

from algorithms.rsa import is_prime
from core.helpers import error, mod_inverse, step
from core.visual import P, line, panel, table

MAX_P = 10_000
MAX_DIGITS = 10
INFINITY = None

META = {
    "id": "ecc",
    "name": "Elliptik egri chiziqlar (ECC)",
    "order": 150,
    "mode_enc_title": "DOUBLE-AND-ADD",
    "mode_dec_title": "NUQTA QO'SHISH",
    "mode_enc_label": "kP ni hisoblash",
    "mode_dec_label": "P + Q ni hisoblash",
    "desc": "Fₚ maydonida nuqta qo'shish, karrali nuqta va Double-and-Add amallarini bosqichma-bosqich o'rganing.",
    "formula_enc": "kP = P + P + ··· + P  (Double-and-Add)",
    "formula_dec": "P≠Q: λ=(y₂−y₁)/(x₂−x₁); P=Q: λ=(3x₁²+a)/(2y₁); P+(−P)=O",
    "map": "E: y² ≡ x³ + ax + b (mod p)\n   ↓\nDISKRIMINANT: 4a³ + 27b² ≢ 0 (mod p)\n   ↓\nNUQTALAR: E(Fₚ) + O\n   ↓\nNUQTA QO'SHISH: P + Q\n   ↓\nKARRALI NUQTA: kP (Double-and-Add)\n   ↓\nELLIPTIK EGRI CHIZIQ GURUHI",
    "weak": "Bu kichik tub sonlarda ishlaydigan o'quv namoyishi; haqiqiy kalitlar yoki himoya uchun yaroqsiz. Amaliy ECC'da standart egri chiziqlar, to'g'ri parametrlar va tekshirilgan kriptografik kutubxonalar ishlatiladi.",
    "explainer": {
        "why": "ECC chekli maydondagi egri chiziq nuqtalarining algebraik guruh xossalaridan foydalanadi.",
        "how": "Nuqtalarni qo'shish formulasi nuqtani egri chiziqda saqlaydi. kP tez hisoblanadi, lekin P va kP dan k ni topish qiyin bo'lishi kerak.",
        "math": "y² = x³ + ax + b (mod p); diskriminant nol emas. Nuqtalar O cheksizlik nuqtasi bilan abel guruhini tashkil qiladi.",
        "weak": "Bu dastur faqat kichik p (≤10 000) uchun o'quv hisoblarini bajaradi, ishlab chiqarish kriptografiyasi emas.",
    },
    "inputs": [
        {"id": "p", "label": "Tub modul p (5–10 000)", "type": "text", "default": "23"},
        {"id": "a", "label": "Egri chiziq koeffitsiyenti a", "type": "text", "default": "1"},
        {"id": "b", "label": "Egri chiziq koeffitsiyenti b", "type": "text", "default": "1"},
        {"id": "px", "label": "P nuqtasi x koordinatasi", "type": "text", "default": "0"},
        {"id": "py", "label": "P nuqtasi y koordinatasi", "type": "text", "default": "1"},
        {"id": "k", "label": "Karrali nuqta uchun k (kP)", "type": "text", "default": "13"},
        {"id": "qx", "label": "Q nuqtasi x koordinatasi (P+Q)", "type": "text", "default": "6"},
        {"id": "qy", "label": "Q nuqtasi y koordinatasi (P+Q)", "type": "text", "default": "19"},
    ],
    "examples": [
        ["23", "1", "1", "0", "1", "13", "6", "19"],
        ["5", "1", "1", "0", "1", "4", "4", "2"],
    ],
    "compare": {
        "name": "ECC",
        "type": "Public-key / Elliptic curve",
        "operation": "Nuqta qo'shish va kP",
        "key": "Egri chiziq nuqtalari",
        "feature": "Kichik kalit bilan yuqori samaradorlik",
    },
}

PRACTICE = [
    {
        "lvl": "O'rta",
        "text": "F₂₃ da y²=x³+x+1 egri chizig'ida P=(0,1) uchun 2P ni hisoblang.",
        "mode": "enc",
        "vals": {"p": "23", "a": "1", "b": "1", "px": "0", "py": "1", "k": "2", "qx": "6", "qy": "19"},
        "answer": lambda out: out["data"]["point"],
    },
]


def _integer(value, name, allow_negative=False):
    text = str(value or "").strip()
    pattern = r"-?[0-9]+" if allow_negative else r"[0-9]+"
    if len(text) > MAX_DIGITS + 1 or not re.fullmatch(pattern, text):
        raise ValueError(f"{name} butun son bo'lishi kerak (ko'pi bilan {MAX_DIGITS} xona)")
    return int(text)


def _format_point(point):
    return "O (cheksizlik nuqtasi)" if point is INFINITY else f"({point[0]}, {point[1]})"


def _curve(vals):
    p = _integer(vals.get("p"), "p")
    if not 5 <= p <= MAX_P:
        raise ValueError(f"O'quv hisoblari uchun 5 ≤ p ≤ {MAX_P} bo'lishi kerak")
    if not is_prime(p):
        raise ValueError(f"p = {p} tub son emas")

    a = _integer(vals.get("a"), "a", allow_negative=True) % p
    b = _integer(vals.get("b"), "b", allow_negative=True) % p
    discriminant = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if discriminant == 0:
        raise ValueError("Egri chiziq singulyar: 4a³ + 27b² ≡ 0 (mod p). Boshqa a yoki b tanlang.")
    return p, a, b, discriminant


def _point(vals, x_key, y_key, p, a, b, name):
    x = _integer(vals.get(x_key), f"{name}.x")
    y = _integer(vals.get(y_key), f"{name}.y")
    if not 0 <= x < p or not 0 <= y < p:
        raise ValueError(f"{name} koordinatalari 0 dan p−1 gacha bo'lishi kerak")
    if (y * y - (x * x * x + a * x + b)) % p:
        raise ValueError(f"{name}=({x}, {y}) egri chiziqda yotmaydi")
    return x, y


def point_add(left, right, p, a):
    if left is INFINITY:
        return right
    if right is INFINITY:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return INFINITY
    if left == right:
        denominator = (2 * y1) % p
        numerator = (3 * x1 * x1 + a) % p
    else:
        denominator = (x2 - x1) % p
        numerator = (y2 - y1) % p
    inverse = mod_inverse(denominator, p)
    if inverse is None:
        raise ValueError("Nuqtalarni qo'shish uchun maxrajning modulyar teskarisi mavjud emas")
    slope = numerator * inverse % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def scalar_multiply(scalar, point, p, a):
    """Return kP and pedagogical Double-and-Add rows, processing MSB first."""
    result = INFINITY
    rows = []
    for index, bit in enumerate(bin(scalar)[2:]):
        before = result
        doubled = point_add(result, result, p, a)
        result = doubled
        added = False
        if bit == "1":
            result = point_add(result, point, p, a)
            added = True
        rows.append([index, bit, _format_point(before), _format_point(doubled),
                     "Ha" if added else "Yo'q", _format_point(result)])
    return result, rows


def curve_order(p, a, b):
    """Count E(F_p) using Euler's criterion, including the point at infinity."""
    count = 1
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            count += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            count += 2
    return count


def point_order(point, group_order, p, a):
    result = INFINITY
    for order in range(1, group_order + 1):
        result = point_add(result, point, p, a)
        if result is INFINITY:
            return order
    raise ValueError("Nuqta tartibini aniqlab bo'lmadi")


def _curve_panel(p, a, b, discriminant, group_size):
    bound = math.isqrt(4 * p)
    lower, upper = p + 1 - bound, p + 1 + bound
    return panel(
        "EGRI CHIZIQ PARAMETRLARI",
        line("E: y² ≡ x³ + ax + b (mod p)"),
        line("p = ", P(p, "gold", True), "  ·  a = ", P(a, "cyan", True),
             "  ·  b = ", P(b, "cyan", True)),
        line("4a³ + 27b² mod p = ", P(discriminant, "green", True),
             "  (≠ 0 — egri chiziq silliq)"),
        line("#E(Fₚ) = ", P(group_size, "violet", True),
             f"  ·  Hasse chegarasi: {lower} ≤ #E ≤ {upper}"),
    )


def _curve_plot(p, a, b, markers):
    """Return all affine F_p points and a few labeled points for the browser plot."""
    roots = {}
    for y in range(p):
        roots.setdefault(y * y % p, []).append(y)
    points = []
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        points.extend([x, y] for y in roots.get(rhs, ()))
    return {
        "type": "ecc-plot",
        "p": p,
        "a": a,
        "b": b,
        "points": points,
        "markers": [
            {"label": label, "x": point[0], "y": point[1], "color": color}
            for label, point, color in markers if point is not INFINITY
        ],
    }


def run(mode, vals):
    if mode not in ("enc", "dec"):
        return error("Amal turi enc yoki dec bo'lishi kerak.")
    try:
        p, a, b, discriminant = _curve(vals)
        point = _point(vals, "px", "py", p, a, b, "P")
        group_size = curve_order(p, a, b)
        order = point_order(point, group_size, p, a)
    except ValueError as exc:
        return error(str(exc))

    steps = [step(
        _curve_panel(p, a, b, discriminant, group_size),
        f"Fₚ dagi silliq egri chiziq y²=x³+{a}x+{b} (mod {p}); guruhda {group_size} ta nuqta bor.",
    ), step(
        panel(
            "NUQTA P",
            line("P = ", P(_format_point(point), "gold", True)),
            line("Tekshiruv: y² mod p = ", P(pow(point[1], 2, p), "cyan", True),
                 "  ·  x³+ax+b mod p = ", P((pow(point[0], 3, p) + a * point[0] + b) % p, "cyan", True)),
            line("P nuqtasining tartibi: ", P(order, "green", True),
                 "  (", P(f"{order}P = O", "green", True), ")"),
        ),
        f"P={_format_point(point)} egri chiziqda yotadi; nuqta tartibi {order}.",
    )]

    if mode == "enc":
        try:
            scalar = _integer(vals.get("k"), "k")
        except ValueError as exc:
            return error(str(exc))
        if scalar > 10**9:
            return error("O'quv namoyishi uchun k 1 000 000 000 dan oshmasligi kerak.")
        result, rows = scalar_multiply(scalar, point, p, a)
        bits = bin(scalar)[2:]
        steps.append(step(
            panel(
                f"DOUBLE-AND-ADD: {scalar}P",
                line("k ning ikkilik yozuvi: ", P(f"{scalar} = {bits}₂", "violet", True)),
                line("Har bitda result ikki baravar qilinadi; bit 1 bo'lsa P qo'shiladi."),
                table(rows, head=["Bit indeksi", "Bit", "Oldingi result", "Ikki baravar", "P qo'shildi?", "Yangi result"]),
                line("Yakuniy nuqta: ", P(_format_point(result), "lime", True), gap=True),
            ),
            f"{scalar}P = {_format_point(result)}. Double-and-Add {len(bits)} ta bitni qayta ishladi.",
            row=["kP", scalar, bits, _format_point(result)],
        ))
        result_text = f"{scalar}P = {_format_point(result)}"
        data = {"point": _format_point(result), "x": result[0] if result else None,
                "y": result[1] if result else None, "point_order": order, "curve_order": group_size}
        return {
            "steps": steps,
            "result": result_text,
            "extra": _curve_plot(p, a, b, [
                ("P", point, "cyan"),
                (f"{scalar}P", result, "gold"),
            ]),
            "data": data,
            "table_cols": ["Amal", "k", "Ikkilik", "Natija"],
        }

    try:
        other = _point(vals, "qx", "qy", p, a, b, "Q")
        denominator = (other[0] - point[0]) % p
        if point == other:
            tangent_denominator = (2 * point[1]) % p
            if tangent_denominator:
                tangent_numerator = (3 * point[0] * point[0] + a) % p
                tangent_inverse = mod_inverse(tangent_denominator, p)
                slope = tangent_numerator * tangent_inverse % p
                slope_text = (f"({tangent_numerator})·{tangent_inverse} mod {p} "
                              f"= {slope}")
            else:
                slope_text, slope = "vertikal urinma → O", None
        elif denominator == 0:
            slope_text = "vertikal chiziq → O"
            slope = None
        else:
            inverse = mod_inverse(denominator, p)
            slope = ((other[1] - point[1]) * inverse) % p
            slope_text = f"({other[1]}−{point[1]})·{inverse} mod {p} = {slope}"
        result = point_add(point, other, p, a)
    except (ValueError, TypeError) as exc:
        return error(str(exc))

    if point == other and slope is None:
        slope_panel = line("P=Q va y=0: urinma vertikal, natija O.")
    elif slope is None:
        slope_panel = line("P va Q qarama-qarshi nuqtalar: P+Q = O.")
    else:
        slope_panel = line("Nishab λ = ", P(slope_text, "cyan", True))
    steps.append(step(
        panel(
            "NUQTALARNI QO'SHISH",
            line("P = ", P(_format_point(point), "gold", True),
                 "  ·  Q = ", P(_format_point(other), "gold", True)),
            slope_panel,
            line("R = P + Q = ", P(_format_point(result), "lime", True)),
        ),
        f"P={_format_point(point)} va Q={_format_point(other)} nuqtalarining yig'indisi {_format_point(result)}.",
        row=["P+Q", _format_point(point), _format_point(other), _format_point(result)],
    ))
    return {
        "steps": steps,
        "result": f"P + Q = {_format_point(result)}",
        "extra": _curve_plot(p, a, b, [
            ("P", point, "cyan"),
            ("Q", other, "violet"),
            ("P + Q", result, "gold"),
        ]),
        "data": {"point": _format_point(result), "x": result[0] if result else None,
                "y": result[1] if result else None, "point_order": order, "curve_order": group_size},
        "table_cols": ["Amal", "P", "Q", "Natija"],
    }
