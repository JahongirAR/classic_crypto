"""Hill shifri (2×2 … 4×4 matritsa, mod 26)."""
import math
import re

from core.helpers import error, gcd, l2n, mod_inverse, n2l, only_letters, step
from core.visual import P, flow, line, panel

META = {
    "id": "hill",
    "name": "Hill Cipher",
    "order": 80,
    "desc": "Matritsa asosida shifrlash. Matn n harfli bloklarga bo'linadi va K (n×n) matritsasiga ko'paytiriladi.",
    "formula_enc": "C = K·P mod 26",
    "formula_dec": "P = K⁻¹·C mod 26",
    "map": "PLAINTEXT\n   ↓\nn HARFLIK BLOK → VEKTOR\n   ↓\nK × P (matrix mult.)\n   ↓\nMOD 26\n   ↓\nVEKTOR → HARFLAR\n   ↓\nCIPHERTEXT",
    "weak": "Known-plaintext hujumga zaif — bir nechta P/C juftligi ma'lum bo'lsa, K matritsasi chiziqli algebra orqali topiladi.",
    "explainer": {
        "why": "Chiziqli algebra (matritsalar) yordamida bir nechta harf birgalikda shifrlanadi.",
        "how": "Matn n harfli bloklarga bo'linib, har bir blok vektor sifatida K matritsasiga ko'paytiriladi.",
        "math": "C=K·P mod 26",
        "weak": "Known-plaintext (chiziqli) hujumlar.",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "ACT"},
        {"id": "matrix", "label": "Matritsa K (qatorlar ';' bilan: '3 3; 2 5'; o'lcham: 2×2, 3×3 yoki 4×4)",
         "type": "text", "default": "3 3; 2 5"},
    ],
    "examples": [["ACT", "3 3; 2 5"], ["HELLO", "3 2; 5 7"], ["ACT", "6 24 1; 13 16 10; 20 17 15"], ["PAYMOREMONEY", "17 17 5; 21 18 21; 2 2 19"]],
    "compare": {"name": "Hill", "type": "Mathematical", "operation": "Matrix", "key": "Matrix", "feature": "Linear algebra"},
}

PRACTICE = [
    {"lvl": "Murakkab", "text": "Hill Cipher: K=[[3,3],[2,5]] uchun 'HI' ni shifrlang.", "mode": "enc",
     "vals": {"pt": "HI", "matrix": "3 3; 2 5"}},
]


# ---------- matritsa matematikasi (mod 26) ----------
def parse_matrix(s):
    s = (s or "").strip()
    if not s:
        raise ValueError("Matritsani kiriting (masalan: 3 3; 2 5).")
    try:
        if ";" in s or "\n" in s:
            rows = [r for r in re.split(r"[;\n]", s) if r.strip()]
            m = [[int(x) for x in re.split(r"[\s,]+", r.strip()) if x] for r in rows]
            n = len(m)
            if any(len(r) != n for r in m):
                raise ValueError("Matritsa kvadrat bo'lishi kerak (n qator × n ustun).")
        else:
            nums = [int(x) for x in re.split(r"[\s,]+", s) if x]
            n = math.isqrt(len(nums))
            if n * n != len(nums):
                raise ValueError("Elementlar soni n² bo'lishi kerak (4, 9 yoki 16).")
            m = [nums[i * n:(i + 1) * n] for i in range(n)]
    except ValueError as e:
        if "Matritsa" in str(e) or "Elementlar" in str(e):
            raise
        raise ValueError("Matritsa elementlari butun son bo'lishi kerak.")
    if not 2 <= n <= 4:
        raise ValueError("Matritsa o'lchami 2×2, 3×3 yoki 4×4 bo'lishi kerak.")
    return m


def minor(m, i, j):
    return [row[:j] + row[j + 1:] for k, row in enumerate(m) if k != i]


def det(m):
    if len(m) == 1:
        return m[0][0]
    return sum(((-1) ** j) * m[0][j] * det(minor(m, 0, j)) for j in range(len(m)))


def adjugate(m):
    n = len(m)
    cof = [[((-1) ** (i + j)) * det(minor(m, i, j)) for j in range(n)] for i in range(n)]
    return [[cof[j][i] for j in range(n)] for i in range(n)]


def inverse_mod26(m):
    dinv = mod_inverse(det(m) % 26, 26)
    if dinv is None:
        return None
    adj = adjugate(m)
    n = len(m)
    return [[(dinv * adj[r][c]) % 26 for c in range(n)] for r in range(n)]


def vec_mul(M, v):
    return [sum(M[r][c] * v[c] for c in range(len(v))) % 26 for r in range(len(M))]


def run(mode, vals):
    try:
        K = parse_matrix(vals.get("matrix"))
    except ValueError as e:
        return error(str(e))
    n = len(K)
    d = det(K)
    dmod = d % 26
    if gcd(dmod, 26) != 1:
        return error(f"det(K) mod 26 = {dmod}. gcd({dmod},26) ≠ 1 — bu matritsaning mod 26 bo'yicha "
                     f"teskari matritsasi mavjud emas. Boshqa matritsa tanlang (masalan: 3 3; 2 5).")
    text = only_letters(vals.get("pt"))
    if not text:
        return error("Matn kiriting.")
    padded = text.ljust(-(-len(text) // n) * n, "X")
    blocks = [[l2n(c) for c in padded[i:i + n]] for i in range(0, len(padded), n)]

    useK = K
    if mode == "dec":
        useK = inverse_mod26(K)
    mat_str = "  ".join("[" + " ".join(map(str, r)) + "]" for r in useK)

    steps = [
        step(panel("DETERMINANT TEKSHIRUVI",
                   line(f"det(K) = {d}   →   det(K) mod 26 = {dmod}"),
                   line(P(f"gcd({dmod}, 26) = 1  ✓  (teskari matritsa mavjud)", "lime"))),
             f"det(K) = {d}, mod 26 = {dmod}. gcd({dmod},26)=1 bo'lgani uchun K⁻¹ mavjud."),
        step(panel("MATRITSA" if mode == "enc" else "K⁻¹ (mod 26) HISOBLANDI", line(P(mat_str, "gold", True))),
             f"K matritsasi: {mat_str}" if mode == "enc" else f"K⁻¹ (mod 26): {mat_str}"),
        step(flow((f'"{padded}"', "dim")), f"Tozalangan matn: {padded} ({n} harfli bloklarga bo'linadi)"),
    ]
    out = []
    for bi, block in enumerate(blocks):
        bl = "".join(n2l(v) for v in block)
        res = vec_mul(useK, block)
        rl = "".join(n2l(v) for v in res)
        out.extend(n2l(v) for v in res)
        steps.append(step(flow(bl, ("[" + ",".join(map(str, block)) + "]", "dim")),
                          f"Blok {bi + 1}: \"{bl}\" → vektor [{', '.join(map(str, block))}]"))
        for ri, row in enumerate(useK):
            terms = "+".join(f"{k}×{block[ci]}" for ci, k in enumerate(row))
            raw = sum(k * block[ci] for ci, k in enumerate(row))
            rv = raw % 26
            letter = n2l(rv)
            last = ri == n - 1
            steps.append(step(
                flow((terms, "formula"), (f"= {raw}, mod 26 = {rv}", "dim"), (letter, "result")),
                f"Blok {bi + 1}, qator {ri + 1}: {terms} = {raw}; mod 26 = {rv} → '{letter}'",
                answer=letter,
                row=[bl, "[" + ",".join(map(str, block)) + "]", rl] if last else None))
    return {"steps": steps, "result": "".join(out), "table_cols": ["Blok", "Vektor P", "Natija bloki"]}
