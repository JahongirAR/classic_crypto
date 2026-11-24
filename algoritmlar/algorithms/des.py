"""DES (Data Encryption Standard) – 16 raundli Feistel, har bir raund 5 qadamda ko'rsatiladi."""
import re

from algorithms._des_tables import E_T, IP_INV, IP_T, P_T, PC1, PC2, SB, SHIFTS
from core.helpers import error, step
from core.visual import P, chips, cols, line, panel, table

META = {
    "id": "des",
    "name": "DES (Data Encryption Standard)",
    "order": 100,
    "desc": "64-bitli blokli simmetrik shifr. 56-bitli kalit bilan 16 ta Feistel raundi.",
    "formula_enc": "C = IP⁻¹( R₁₆L₁₆ ),  Lᵢ = Rᵢ₋₁,  Rᵢ = Lᵢ₋₁ ⊕ f(Rᵢ₋₁, Kᵢ)  ·  boshlanishi IP(M)",
    "formula_dec": "P = IP⁻¹( R₁₆L₁₆ ) — xuddi shu sxema, kalitlar teskari tartibda (K₁₆ … K₁)",
    "map": "PLAINTEXT (64-bit)\n   ↓ IP (boshlang'ich almashtirish)\n   ↓ L₀, R₀\n   ↓ 16 × Feistel raundi:\n       E(R) → 48-bit\n       XOR Kᵢ\n       S-box (48→32 bit)\n       P-almashtirish\n       Lᵢ=Rᵢ₋₁, Rᵢ=Lᵢ₋₁⊕f\n   ↓ IP⁻¹ (yakuniy almashtirish)\n   ↓ CIPHERTEXT (64-bit)",
    "weak": "DES 56-bitli kalit bilan 1990-yillardan boshlab ishonchsiz: to'liq kalit qidiruvi (brute-force) "
            "mumkin bo'ldi va Triple DES (3DES) hamda keyin AES bilan almashtirildi. Hozir AES standart.",
    "explainer": {
        "why": "IBMda 1970-yillarda ishlab chiqilgan birinchi standart blok shifr.",
        "how": "16 marta takrorlanuvchi Feistel strukturasi: har raundda E, XOR, S-box, P amallari.",
        "math": "Rᵢ = Lᵢ₋₁ ⊕ f(Rᵢ₋₁, Kᵢ)",
        "weak": "56-bit kalit — brute-force: ≈2⁵⁶ urinish, 1999-yilda EFF Deep Crack 22 soatda buzdi.",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext (16 HEX belgi yoki 8 ta ASCII matn) / Ciphertext (16 HEX)", "type": "text", "default": "0123456789ABCDEF"},
        {"id": "key", "label": "Kalit (16 HEX belgi, 64-bit)", "type": "text", "default": "133457799BBCDFF1"},
    ],
    "examples": [["0123456789ABCDEF", "133457799BBCDFF1"], ["HELLO   ", "0E329232EA6D0D73"], ["SALOM123", "AABB09182736CCDD"]],
    "compare": {"name": "DES", "bold": True, "type": "Block / Symmetric", "operation": "Feistel (16 raund)",
                "key": "56-bit (64-bit kiritiladi)", "feature": "IP → 16×(E,XOR,S,P) → IP⁻¹"},
}

PRACTICE = [
    {"lvl": "Murakkab", "text": "DES: Plaintext=0123456789ABCDEF, Key=133457799BBCDFF1 bilan shifrlang. Natija (HEX) nima?",
     "mode": "enc", "vals": {"pt": "0123456789ABCDEF", "key": "133457799BBCDFF1"}, "answer": lambda out: out["data"]["hex"]},
]


# ---------- bit yordamchilari ----------
def hex_to_bits(h):
    return bin(int(h, 16))[2:].zfill(len(h) * 4)


def bits_to_hex(b):
    return format(int(b, 2), "X").zfill(len(b) // 4)


def permute(bits, tbl):
    return "".join(bits[i - 1] for i in tbl)


def xor(a, b):
    return "".join("0" if x == y else "1" for x, y in zip(a, b))


def lshift(b, n):
    return b[n:] + b[:n]


def groups(s, n):
    return " ".join(s[i:i + n] for i in range(0, len(s), n))


def gen_keys(key_bits):
    k56 = permute(key_bits, PC1)
    c, d = k56[:28], k56[28:]
    keys = []
    for sh in SHIFTS:
        c, d = lshift(c, sh), lshift(d, sh)
        keys.append(permute(c + d, PC2))
    return keys


def sbox(xor48):
    details, out = [], ""
    for n in range(8):
        b = xor48[n * 6:(n + 1) * 6]
        row, col = int(b[0] + b[5], 2), int(b[1:5], 2)
        val = SB[n][row][col]
        o4 = format(val, "04b")
        out += o4
        details.append((b, row, col, val, o4))
    return out, details


def run(mode, vals):
    pt = (vals.get("pt") or "").strip()
    key_raw = (vals.get("key") or "").strip().upper()
    if not re.fullmatch(r"[0-9A-F]{16}", key_raw):
        return error("Kalit aynan 16 ta HEX belgidan iborat bo'lishi kerak (masalan: 133457799BBCDFF1).")
    if re.fullmatch(r"[0-9A-Fa-f]{16}", pt):
        plain_hex = pt.upper()
    elif mode == "dec":
        return error("Deshifrlash uchun shifrmatn aynan 16 ta HEX belgi bo'lishi kerak.")
    else:
        if not pt:
            return error("Plaintext kiriting.")
        if any(ord(ch) > 255 for ch in pt):
            return error("Matn faqat ASCII/Latin-1 belgilardan iborat bo'lishi kerak (yoki 16 HEX kiriting).")
        data = [ord(ch) for ch in pt[:8]]
        data += [32] * (8 - len(data))
        plain_hex = "".join(f"{b:02X}" for b in data)

    key_bits = hex_to_bits(key_raw)
    round_keys = gen_keys(key_bits)
    if mode == "dec":
        round_keys = round_keys[::-1]

    steps = [step(
        panel("KALIT GENERATSIYASI",
              line("Kalit (HEX): ", P(key_raw, None, True)),
              line("PC-1 → 56-bit: ", P(groups(permute(key_bits, PC1), 7), "lime")),
              line("16 ta raund kaliti (K1..K16) hisoblandi.")),
        "DES uchun 64-bitli kalit PC-1 jadvali orqali 56-bitga qisqartiriladi, so'ng siljitishlar va PC-2 "
        "orqali 16 ta 48-bitli raund kalitlari hosil bo'ladi.",
        row=["Kalit (HEX)", key_raw, "16 × 48-bit Kᵢ"])]

    ip = permute(hex_to_bits(plain_hex), IP_T)
    L, R = ip[:32], ip[32:]
    steps.append(step(
        panel("BOSHLANG'ICH ALMASHTIRISH (IP)",
              line("M (HEX): ", P(plain_hex, None, True)),
              line("IP(M) = ", P(groups(ip, 8), "lime")),
              line("L₀ = ", P(bits_to_hex(L), "blue"), "   R₀ = ", P(bits_to_hex(R), "red"))),
        "IP (Initial Permutation) jadvali yordamida 64-bitli blok qayta tartiblanadi va L₀ (chap 32 bit) "
        "va R₀ (o'ng 32 bit) ga bo'linadi.",
        row=["IP", f"L₀={bits_to_hex(L)}", f"R₀={bits_to_hex(R)}"]))

    tag = "🔓 DESHIFR " if mode == "dec" else ""
    for i in range(1, 17):
        K = round_keys[i - 1]
        er = permute(R, E_T)
        xk = xor(er, K)
        sout, det = sbox(xk)
        fR = permute(sout, P_T)
        newR, newL = xor(L, fR), R
        eg = [er[n:n + 6] for n in range(0, 48, 6)]
        kg = [K[n:n + 6] for n in range(0, 48, 6)]
        xg = [xk[n:n + 6] for n in range(0, 48, 6)]

        steps.append(step(
            panel(f"{tag}{i}-RAUND  ·  QADAM 1/5 — E KENGAYTIRISH (32→48 bit)",
                  line(f"R{i - 1} (32 bit): ", P(groups(R, 4), "red")),
                  line("E jadvali bo'yicha har 4-bit blok kengaytiriladi (qo'shni bitlar qo'shiladi):"),
                  chips([(f"B{n + 1}:{g}", "violet") for n, g in enumerate(eg)]),
                  line(f"E(R{i - 1}) = ", P(" ".join(eg), "violet", True), P("  (48 bit)", "dim"))),
            f"Raund {i}, 1-qadam — E kengaytirish: R{i - 1} ning 32 biti 48 bitga kengaytiriladi. "
            f"Chegaradagi bitlar qo'shni bloklarga \"qo'shiladi\" — bu S-boxlarni nonlinear qiladi.",
            row=[f"R{i} — E-kengaytirish", f"R{i - 1}={bits_to_hex(R)}", f"E(R)={bits_to_hex(er)}"]))

        steps.append(step(
            panel(f"{i}-RAUND  ·  QADAM 2/5 — K{i} BILAN XOR",
                  line(f"K{i} (48 bit): ", P(" ".join(kg), "gold")),
                  table([[P("Blok", "dim")] + [P(f"B{n + 1}", "dim") for n in range(8)],
                         [P("E(R)", "violet")] + [P(g, "violet") for g in eg],
                         [P(f"K{i}", "gold")] + [P(g, "gold") for g in kg],
                         [P("XOR", "pink")] + [P(g, "pink", True) for g in xg]])),
            f"Raund {i}, 2-qadam — K{i} bilan XOR: E(R{i - 1}) ning har 6-biti K{i} ning mos 6-biti bilan XOR "
            f"qilinadi. Natija 8 ta 6-bitli blok bo'lib, S-boxlarga kiradi.",
            row=[f"R{i} — XOR", f"K{i}={bits_to_hex(K)}", f"XOR={bits_to_hex(xk)}"]))

        steps.append(step(
            panel(f"{i}-RAUND  ·  QADAM 3/5 — S-BOX ALMASHTIRISH (48→32 bit)",
                  line(P("Qator = 1- va 6-bit, Ustun = o'rtadagi 4-bit", "slate")),
                  table([[P(f"S{n + 1}", "slate"), P(b, "pink", True),
                          P(f"{b[0]} _ _ _ _ {b[5]} → {r}", "gold"), P(f"_ {b[1:5]} _ → {c}", "violet"),
                          P(v, "lime", True), P(o4, "green", True)]
                         for n, (b, r, c, v, o4) in enumerate(det)],
                        head=["S-box", "Kirish (6-bit)", "Qator", "Ustun", "Qiymat", "4-bit chiqish"]),
                  line("S-box chiqishi: ", P(" ".join(d[4] for d in det), "green", True), P("  (32 bit)", "dim"), gap=True)),
            f"Raund {i}, 3-qadam — S-box: har 6-bitli blok uchun 1- va 6-bit → qator (0-3), o'rtadagi 4-bit → "
            f"ustun (0-15). S[qator][ustun] = 4-bitli chiqish. Bu chiziqsiz (qaytarilmas) amal DES xavfsizligining asosi.",
            row=[f"R{i} — S-box", f"Kirish: {bits_to_hex(xk)}", f"Chiqish: {bits_to_hex(sout)}"]))

        steps.append(step(
            panel(f"{i}-RAUND  ·  QADAM 4/5 — P-ALMASHTIRISH (32 bit)",
                  line("S-box chiqishi (32 bit):"),
                  chips([(g, "green") for g in [sout[n:n + 4] for n in range(0, 32, 4)]]),
                  line("P jadvali bit pozitsiyalarini qayta tartiblaydi:"),
                  chips([(g, "lime") for g in [fR[n:n + 4] for n in range(0, 32, 4)]]),
                  line(f"f(R{i - 1}, K{i}) = ", P(bits_to_hex(fR), "lime", True))),
            f"Raund {i}, 4-qadam — P-almashtirish: S-box natijasining 32 biti P jadvali tartibida qayta "
            f"joylashtiriladi. Bu diffuziyani ta'minlaydi — bir S-box chiqishi keyingi raunddagi turli S-boxlarga tarqaladi.",
            row=[f"R{i} — P-almashtirish", f"S-out: {bits_to_hex(sout)}", f"f= {bits_to_hex(fR)}"]))

        steps.append(step(
            panel(f"{i}-RAUND  ·  QADAM 5/5 — FEISTEL ALMASHTIRUVI",
                  cols(dict(title="CHAP (L)", color="blue",
                            lines=[[f"L{i - 1} = ", P(bits_to_hex(L), "blue")], ["f = ", P(bits_to_hex(fR), "lime")]],
                            result=[P(f"L{i} = R{i - 1} = ", None, True), P(bits_to_hex(newL), "blue", True)]),
                       dict(title="O'NG (R)", color="red",
                            lines=[[f"L{i - 1} = ", P(bits_to_hex(L), "blue")], ["f = ", P(bits_to_hex(fR), "lime")]],
                            result=[P(f"R{i} = L{i - 1}⊕f = ", None, True), P(bits_to_hex(newR), "red", True)])),
                  line(P("Feistel: L yangi = R eski; R yangi = L eski XOR f(R,K)", "dim"))),
            f"Raund {i}, 5-qadam — Feistel almashtiruvi: L{i}=R{i - 1} (oddiy ko'chirish), "
            f"R{i}=L{i - 1}⊕f(R{i - 1},K{i}). Raund tugadi. Endi L{i}={bits_to_hex(newL)}, R{i}={bits_to_hex(newR)}.",
            row=[f"R{i} — Natija", f"L{i}={bits_to_hex(newL)}", f"R{i}={bits_to_hex(newR)}"]))
        L, R = newL, newR

    pre = R + L
    result_hex = bits_to_hex(permute(pre, IP_INV))
    label = "Ciphertext" if mode == "enc" else "Plaintext"
    steps.append(step(
        panel("YAKUNIY ALMASHTIRISH (IP⁻¹)",
              line("R16L16 = ", P(bits_to_hex(pre), "violet")),
              line("IP⁻¹ → ", P(result_hex, "green", True))),
        f"IP⁻¹ (Inverse Initial Permutation) orqali R16+L16 yakuniy tartiblanadi. {label}: {result_hex}",
        row=["IP⁻¹ (Natija)", "R16+L16", result_hex]))
    return {"steps": steps, "result": f"{label}: {result_hex}", "data": {"hex": result_hex},
            "table_cols": ["Bosqich", "L / Ma'lumot", "R / Natija"]}
