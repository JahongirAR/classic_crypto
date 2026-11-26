"""RSA (Python butun sonlari, istalgancha tub son: n = p·q·r·…)."""
import re

from core.helpers import error, gcd, mod_inverse, step
from core.visual import P, line, panel, table

META = {
    "id": "rsa",
    "name": "RSA Cipher",
    "order": 120,
    "desc": "Ochiq kalitli kriptotizim: istalgancha tub son va e ni qo'lda kiritib, matnni shifrlash/deshifrlash.",
    "formula_enc": "C ≡ Mᵉ (mod n)",
    "formula_dec": "M ≡ Cᵈ (mod n)",
    "map": "PLAINTEXT (har bir belgi M)\n   ↓\nUNICODE / ASCII KOD (m = codePoint)\n   ↓\nSQUARE-AND-MULTIPLY: C = Mᵉ mod n\n   ↓\nCIPHERTEXT (sonlar ketma-ketligi)\n   ↓\nDECRYPTION: M = Cᵈ mod n\n   ↓\nPLAINTEXT (belgilar tiklandi)",
    "weak": "RSA xavfsizligi n = p × q sonini tub ko'paytuvchilarga ajratishning qiyinligiga asoslangan. "
            "Agar p va q kichik bo'lsa, maxfiy kalit d bir necha millisekundda topiladi.",
    "explainer": {
        "why": "Asimmetrik shifrlash: shifrlash va deshifrlash uchun turli kalitlar (ochiq va maxfiy) ishlatiladi.",
        "how": "Har bir belgi Mᵉ mod n orqali shifrlanadi, Cᵈ mod n orqali o'z holiga qaytariladi.",
        "math": "Square-and-Multiply (tez darajaga ko'tarish) va Kengaytirilgan Evklid algoritmi.",
        "weak": "Agar tub sonlar kichik bo'lsa, n sonini faktorizatsiya qilish (omillarga ajratish) oson bo'ladi.",
    },
    "inputs": [
        {"id": "primes", "label": "Tub sonlar (p, q, … vergul bilan)", "type": "text", "default": "61, 53"},
        {"id": "e", "label": "Ochiq eksponenta (e)", "type": "text", "default": "17"},
        {"id": "pt", "label": "Plaintext (matn) / Ciphertext (sonlar: 2680 2790 …)", "type": "text", "default": "SALOM"},
    ],
    "examples": [["61, 53", "17", "SALOM"], ["137, 139", "5", "Kripto"], ["3, 11, 17", "3", "RSA"]],
    "actions": [{"id": "suggest_e", "label": "e ni tavsiya qilish"}],
    "compare": {"name": "RSA", "type": "Asymmetric / Public-key", "operation": "Modulyar darajaga ko'tarish",
                "key": "(e, n) ochiq; (d, n) maxfiy", "feature": "Faktorizatsiya qiyinligi"},
}

PRACTICE = [
    {"lvl": "Murakkab", "text": "RSA: p=61, q=53, e=17 bilan 'SALOM' ni shifrlang (sonlarni bo'sh joy bilan yozing).",
     "mode": "enc", "vals": {"primes": "61, 53", "e": "17", "pt": "SALOM"}, "answer": lambda out: out["data"]["cipher"]},
]

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)


def is_prime(n: int) -> bool:
    """Miller–Rabin (n < 3.3·10²⁴ uchun aniq, kattaroq sonlar uchun ehtimoliy)."""
    if n < 2:
        return False
    for p in _MR_BASES:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def suggest_e(phi: int):
    if phi > 65537 and gcd(65537, phi) == 1:
        return 65537
    for e in range(3, phi):
        if gcd(e, phi) == 1:
            return e
    return None


def pow_steps(base: int, exp: int, m: int):
    """Square-and-Multiply: [(bit, kvadratdan keyin, ko'paytirishdan keyin)]."""
    result, rows = 1, []
    for bit in bin(exp)[2:]:
        result = result * result % m
        sq = result
        if bit == "1":
            result = result * base % m
        rows.append((bit, sq, result))
    return result, rows


def _tokens(s):
    return [t for t in re.split(r"[\s,;]+", (s or "").strip()) if t]


MAX_DIGITS = 300


def _to_int(t, name):
    if len(t) > MAX_DIGITS:
        raise ValueError(f"{name} juda uzun (ko'pi bilan {MAX_DIGITS} xona)")
    if not re.fullmatch(r"\d+", t):
        raise ValueError(f"{name} musbat butun son bo'lishi kerak (kiritilgan: \"{t}\")")
    return int(t)


def _parse_primes(primes_str):
    toks = _tokens(primes_str)
    if len(toks) < 2:
        raise ValueError("Kamida 2 ta tub son kiritilishi kerak (masalan: 61, 53)")
    ps = [_to_int(t, f"{i + 1}-tub son") for i, t in enumerate(toks)]
    for i, p in enumerate(ps):
        if not is_prime(p):
            raise ValueError(f"{i + 1}-son ({p}) tub son emas")
    if len(set(ps)) != len(ps):
        raise ValueError("Tub sonlar bir-biridan farqli bo'lishi kerak")
    return ps


def generate_keys(primes_str, e_str):
    ps = _parse_primes(primes_str)
    n = 1
    phi = 1
    for p in ps:
        n *= p
        phi *= p - 1
    e = _to_int((e_str or "").strip(), "e")
    if not 1 < e < phi:
        raise ValueError(f"e soni 1 < e < φ(n) = {phi} oralig'ida bo'lishi kerak")
    if gcd(e, phi) != 1:
        raise ValueError(f"e = {e} soni φ(n) = {phi} bilan o'zaro tub emas. Masalan, e = {suggest_e(phi)} ni sinab ko'ring")
    return {"primes": ps, "n": n, "phi": phi, "e": e, "d": mod_inverse(e, phi)}


# ---------- jonli kalit paneli ----------
def live(vals):
    toks = _tokens(vals.get("primes"))
    blocks = []
    ok_primes, all_ok = [], True
    for i, t in enumerate(toks):
        if re.fullmatch(r"\d+", t):
            v = int(t)
            if is_prime(v):
                ok_primes.append(v)
                blocks.append(line(f"{i + 1}-son = {v}  ", P("✓ Tub", "green", True)))
                continue
            blocks.append(line(f"{i + 1}-son = {v}  ", P("✗ tub son emas", "red", True)))
        else:
            blocks.append(line(f"{i + 1}-son = {t}  ", P("✗ butun son emas", "red", True)))
        all_ok = False
    if len(toks) < 2:
        blocks.append(line(P("Kamida 2 ta tub son kiriting.", "gold")))
        return panel("KALITLAR", *blocks)
    try:
        k = generate_keys(vals.get("primes"), vals.get("e"))
        blocks += [
            line("Modul: n = ", P(k["n"], "gold", True), "   φ(n) = ", P(k["phi"], "cyan", True), gap=True),
            line("Maxfiy eksponenta: d = ", P(k["d"], "green", True), "  (e·d ≡ 1 mod φ)"),
            line(P(f"🔓 Ochiq kalit: (e={k['e']}, n={k['n']})   🔐 Maxfiy kalit: (d={k['d']}, n={k['n']})", "slate")),
            line(P("✓ gcd(e, φ(n)) = 1 (mos tanlandi)", "lime")),
        ]
    except ValueError as err:
        if all_ok and len(ok_primes) >= 2:
            n = phi = 1
            for p in ok_primes:
                n *= p
                phi *= p - 1
            blocks.append(line("Modul: n = ", P(n, "gold", True), "   φ(n) = ", P(phi, "cyan", True), gap=True))
        blocks.append(line(P(f"✗ {err}", "red")))
    return panel("KALITLAR", *blocks)


def action_suggest_e(vals):
    try:
        ps = _parse_primes(vals.get("primes"))
        phi = 1
        for p in ps:
            phi *= p - 1
        e = suggest_e(phi)
        if e is None:
            raise ValueError("Mos e topilmadi.")
        return {"fill": {"e": str(e)}}
    except ValueError as err:
        return {"error": str(err)}


ACTIONS = {"suggest_e": action_suggest_e}


def _pow_table(rows):
    if len(rows) > 32:
        return line(P(f"Square-and-Multiply: {len(rows)} bit (jadval ko'rsatilmadi)", "slate"))
    return table([[P(b, "gold", True), P(sq, "cyan"), P(res, "lime", True)] for b, sq, res in rows],
                 head=["Bit", "Kvadrat (mod n)", "Natija (mod n)"])


def run(mode, vals):
    if mode not in ("enc", "dec"):
        return error("Amal turi enc yoki dec bo'lishi kerak.")
    try:
        k = generate_keys(vals.get("primes"), vals.get("e"))
    except ValueError as e:
        return error(str(e))
    n, e_, d = k["n"], k["e"], k["d"]
    text = vals.get("pt") or ""
    steps = []
    keys_step = step(panel("RSA KALITLARI",
                           line("n = ", P(" × ".join(map(str, k["primes"])), "slate"), " = ", P(n, "gold", True)),
                           line("φ(n) = ", P(k["phi"], "cyan", True)),
                           line("e = ", P(e_, "gold", True), "   d = ", P(d, "green", True)),
                           line(P(f"Ochiq kalit (e={e_}, n={n}) · Maxfiy kalit (d={d}, n={n})", "slate"))),
                     f"Kalitlar: n = {n}, φ(n) = {k['phi']}, e = {e_}, d = {d} (e·d ≡ 1 mod φ(n)).")
    steps.append(keys_step)

    if mode == "enc":
        if not text:
            return error("Matn bo'sh")
        chars = list(text)
        codes = [ord(c) for c in chars]
        if max(codes) >= n:
            return error(f"Modul n = {n} juda kichik. Matndagi eng katta belgi kodi {max(codes)}, "
                         f"shuning uchun n > {max(codes)} bo'lishi kerak. Kattaroq tub sonlar tanlang.")
        ciphers = []
        for i, (ch, m) in enumerate(zip(chars, codes)):
            c, rows = pow_steps(m, e_, n)
            ciphers.append(c)
            steps.append(step(
                panel(f"'{ch}' (kod {m})  →  C = {m}^{e_} mod {n}",
                      _pow_table(rows),
                      line("Natija: ", P(f"C = {c}", "green", True), gap=True)),
                f"'{ch}' belgisi (kodi: {m}) shifrlandi → C = {m}^{e_} mod {n} = {c}. "
                f"Square-and-Multiply: {len(rows)} ta bit.",
                row=[i + 1, f"'{ch}'", m, f"{m}^{e_} mod {n}", c]))
        cs = " ".join(map(str, ciphers))
        return {"steps": steps, "result": f"Shifrmatn: {cs}", "data": {"cipher": cs},
                "table_cols": ["#", "Belgi", "Kod (M)", "Formula", "Shifr (C)"]}

    toks = _tokens(text)
    if not toks:
        return error("Shifrlangan matn bo'sh. Decrypt uchun sonlarni kiriting (masalan: 2680 2790 …).")
    out = []
    try:
        cs = [_to_int(t, f"{i + 1}-shifr son") for i, t in enumerate(toks)]
    except ValueError as err:
        return error(f"{err}. Decrypt uchun shifrmatn sonlarini kiriting.")
    for i, c in enumerate(cs):
        if c >= n:
            return error(f"Shifrlangan son ({c}) moduldan ({n}) kichik bo'lishi kerak")
        m, rows = pow_steps(c, d, n)
        try:
            ch = chr(m)
        except (ValueError, OverflowError):
            return error(f"Noto'g'ri kalit yoki shifr matn: {m} belgi kodi emas")
        out.append(ch)
        steps.append(step(
            panel(f"C = {c}  →  M = {c}^{d} mod {n}",
                  _pow_table(rows),
                  line("Natija: ", P(f"M = {m}  ('{ch}')", "green", True), gap=True)),
            f"Shifr {c} deshifrlandi → M = {m} (Belgi: '{ch}')",
            row=[i + 1, c, f"{c}^{d} mod {n}", m, f"'{ch}'"]))
    return {"steps": steps, "result": f"Tiklangan matn: {''.join(out)}", "data": {"text": "".join(out)},
            "table_cols": ["#", "Shifr (C)", "Formula", "Kod (M)", "Tiklandi"]}
