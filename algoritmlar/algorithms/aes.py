"""AES-128 (Rijndael): 10 raund. Shifrlash va deshifrlash bosqichma-bosqich ko'rsatiladi."""
import re

from core.helpers import error, step
from core.visual import P, line, note, panel, state, states

META = {
    "id": "aes",
    "name": "AES (Advanced Encryption Standard - Rijndael)",
    "order": 110,
    "desc": "128-bitli blokli simmetrik shifr (NIST FIPS 197). 10 ta raund: SubBytes, ShiftRows, MixColumns, AddRoundKey.",
    "formula_enc": "C = AES-128(P, K)  ·  10 raund (SubBytes → ShiftRows → MixColumns → AddRoundKey)",
    "formula_dec": "P = InvAES-128(C, K)  ·  Teskari raundlar (InvShiftRows → InvSubBytes → AddRoundKey → InvMixColumns)",
    "map": "PLAINTEXT (128-bit / 16 bayt)\n   ↓ (matn bo'lsa PKCS#7 bilan 16 baytgacha to'ldiriladi)\nState matritsasi (4×4 bayt, ustun bo'yicha: s[ustun*4 + qator])\n   ↓ 0-raund: AddRoundKey (State ⊕ K0)\n   ↓ 1–9 raundlar:\n       SubBytes   (S-box)\n       ShiftRows  (qatorlarni siljitish)\n       MixColumns (GF(2⁸) da ustunlarni aralashtirish)\n       AddRoundKey (raund kaliti bilan XOR)\n   ↓ 10-raund: SubBytes → ShiftRows → AddRoundKey (MixColumns YO'Q)\n   ↓ CIPHERTEXT (128-bit)",
    "weak": "AES hozircha xalqaro miqyosda buzilmagan hisoblanadi (2001-yildan standart). Kiruvchi blokning to'liq "
            "diffuziyasi 2-raunddan keyinoq ta'minlanadi. Amaliy xavflar faqat kalitni noto'g'ri saqlash yoki "
            "Side-Channel hujumlari orqali bo'lishi mumkin.",
    "explainer": {
        "why": "AES (Rijndael) 2000-yilda NIST tanlovida g'olib bo'lgan va 2001-yilda FIPS 197 sifatida standartlashtirilgan; "
               "Feistel emas, SPN (Substitution-Permutation Network) tuzilmasiga asoslangan.",
        "how": "128-bitli blok 4×4 bayt State matritsasiga ustun bo'yicha joylanadi. Har bir raundda 4 ta akslantirish ketma-ket bajariladi.",
        "math": "State ⊕ K0 → 9×(SubBytes → ShiftRows → MixColumns → AddRoundKey) → SubBytes → ShiftRows → AddRoundKey(K10)",
        "weak": "Kriptobardoshlilik: to'liq diffuziya 2-raunddan so'ng yuz beradi. Brute-force: 2¹²⁸ ta urinish kerak (hozirgi superkompyuterlar bilan ham millionlab yil).",
    },
    "inputs": [
        {"id": "pt", "label": "Plaintext / Ciphertext (matn yoki 32 HEX belgi)", "type": "text", "default": "Fhishing"},
        {"id": "key", "label": "Kalit (16 ta ASCII belgi yoki 32 HEX belgi)", "type": "text", "default": "Kriptografiya_01"},
    ],
    "examples": [
        ["Fhishing", "Kriptografiya_01"],
        ["00112233445566778899AABBCCDDEEFF", "000102030405060708090A0B0C0D0E0F"],
        ["KriptoLaboratoriya", "Kriptografiya_01"],
        ["SALOM AES DEMO  ", "AABB09182736CCDD1122334455667788"],
    ],
    "compare": {"name": "AES", "bold": True, "type": "Block / Symmetric", "operation": "SPN (10 raund)",
                "key": "128-bit (AES-128)", "feature": "SubBytes → ShiftRows → MixColumns → AddRoundKey"},
}

PRACTICE = [
    {"lvl": "Murakkab", "text": "AES-128: Plaintext=00112233445566778899AABBCCDDEEFF, Key=000102030405060708090A0B0C0D0E0F bilan shifrlang. Natija (HEX) nima?",
     "mode": "enc", "vals": {"pt": "00112233445566778899AABBCCDDEEFF", "key": "000102030405060708090A0B0C0D0E0F"},
     "answer": lambda out: out["data"]["hex"]},
]


# ---------- S-box (GF(2⁸) da hisoblab hosil qilinadi) ----------
def _rotl8(x, n):
    return ((x << n) | (x >> (8 - n))) & 0xFF


def _build_sbox():
    sb = [0] * 256
    p = q = 1
    while True:
        p = (p ^ (p << 1) ^ (0x11B if p & 0x80 else 0)) & 0xFF      # p *= 3
        q ^= q << 1
        q ^= q << 2
        q ^= q << 4
        q &= 0xFF                                                     # q /= 3
        if q & 0x80:
            q ^= 0x09
        sb[p] = q ^ _rotl8(q, 1) ^ _rotl8(q, 2) ^ _rotl8(q, 3) ^ _rotl8(q, 4) ^ 0x63
        if p == 1:
            break
    sb[0] = 0x63
    return sb


SBOX = _build_sbox()
INV_SBOX = [0] * 256
for _i, _v in enumerate(SBOX):
    INV_SBOX[_v] = _i


def hx(b):
    return f"{b & 0xFF:02X}"


def xtime(x):
    return ((x << 1) ^ (0x1B if x & 0x80 else 0)) & 0xFF


def gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return p


def mul_small(x, n):
    return x if n == 1 else xtime(x) if n == 2 else xtime(x) ^ x


def key_expansion(key):
    w = [list(key[i * 4:i * 4 + 4]) for i in range(4)]
    rcon = 1
    for i in range(4, 44):
        t = list(w[i - 1])
        if i % 4 == 0:
            t = [SBOX[b] for b in (t[1], t[2], t[3], t[0])]
            t[0] ^= rcon
            rcon = xtime(rcon)
        w.append([a ^ b for a, b in zip(w[i - 4], t)])
    round_keys = [sum(w[r * 4:r * 4 + 4], []) for r in range(11)]
    return w, round_keys


# State: s[ustun*4 + qator]
def sub_bytes(s):
    return [SBOX[b] for b in s]


def inv_sub_bytes(s):
    return [INV_SBOX[b] for b in s]


def shift_rows(s):
    return [s[((c + r) % 4) * 4 + r] for c in range(4) for r in range(4)]


def inv_shift_rows(s):
    return [s[((c - r) % 4) * 4 + r] for c in range(4) for r in range(4)]


MATRIX = [[2, 3, 1, 1], [1, 2, 3, 1], [1, 1, 2, 3], [3, 1, 1, 2]]
INV_MATRIX = [[0x0E, 0x0B, 0x0D, 0x09], [0x09, 0x0E, 0x0B, 0x0D], [0x0D, 0x09, 0x0E, 0x0B], [0x0B, 0x0D, 0x09, 0x0E]]


def mix_columns(s):
    o = [0] * 16
    for c in range(4):
        for r in range(4):
            v = 0
            for k in range(4):
                v ^= mul_small(s[c * 4 + k], MATRIX[r][k])
            o[c * 4 + r] = v
    return o


def inv_mix_columns(s):
    o = [0] * 16
    for c in range(4):
        for r in range(4):
            v = 0
            for k in range(4):
                v ^= gmul(s[c * 4 + k], INV_MATRIX[r][k])
            o[c * 4 + r] = v
    return o


def add_round_key(s, k):
    return [a ^ b for a, b in zip(s, k)]


def rows_str(s):
    return " / ".join(" ".join(hx(s[c * 4 + r]) for c in range(4)) for r in range(4))


def hexl(bs):
    return " ".join(hx(b) for b in bs)


def pkcs7(b):
    n = 16 - len(b) % 16
    return b + [n] * n


def unpkcs7(b):
    if b and 1 <= b[-1] <= 16 and all(x == b[-1] for x in b[-b[-1]:]):
        return b[:-b[-1]]
    return b


def _hex32(s):
    c = re.sub(r"[\s:\-]", "", s)
    return c.upper() if re.fullmatch(r"[0-9A-Fa-f]{32}", c) else None


def _printable(text):
    return "".join(ch if ch.isprintable() else "·" for ch in text)


def run(mode, vals):
    pt = vals.get("pt") or ""          # bo'shliqlar matnning bir qismi: kesilmaydi
    key_raw = vals.get("key") or ""
    if not pt.strip():
        return error("Iltimos, Plaintext yoki Ciphertext matnini kiriting.")
    if not key_raw.strip():
        return error("Iltimos, 16 baytli kalitni kiriting (masalan: 'Kriptografiya_01' yoki 32 ta HEX belgi).")

    kh = _hex32(key_raw)
    if kh:
        key = list(bytes.fromhex(kh))
    else:
        key = list(key_raw.encode("utf-8"))
        if len(key) != 16:
            return error(f"Kalit aynan 16 bayt (16 ta belgi) bo'lishi kerak. Hozirgi uzunlik: {len(key)} bayt. "
                         f"Masalan: 'Kriptografiya_01' yoki 32 ta HEX belgi.")

    ph = _hex32(pt)
    padding_info = ""
    if mode == "enc":
        if ph:
            block = list(bytes.fromhex(ph))
            padding_info = "Kiritilgan 32 ta HEX belgi 16 baytli blok sifatida qabul qilindi."
        else:
            raw = list(pt.encode("utf-8"))
            if len(raw) > 16:
                block = raw[:16]
                padding_info = f"Ochiq matn {len(raw)} bayt — bu vizualizator bitta 16 baytli blokni ko'rsatadi, shuning uchun birinchi 16 bayt olindi."
            elif len(raw) == 16:
                block = raw
                padding_info = "Ochiq matn aynan 16 bayt — bitta blok, padding talab qilinmadi."
            else:
                block = pkcs7(raw)
                padding_info = (f"Ochiq matn {len(raw)} bayt. PKCS#7 standarti bo'yicha qolgan {16 - len(raw)} bayt "
                                f"0x{hx(16 - len(raw))} bilan to'ldirildi.")
    else:
        if ph:
            block = list(bytes.fromhex(ph))
            padding_info = "Shifrmatn 32 ta HEX belgi (128-bit) sifatida qabul qilindi."
        else:
            raw = list(pt.encode("utf-8"))
            if len(raw) != 16:
                return error("Deshifrlash uchun 32 ta HEX belgi yoki 16 baytli shifrmatn kiriting.")
            block = raw
            padding_info = "16 baytli blok kiritildi."

    words, rks = key_expansion(key)
    cols_ = ["Raund", "Bosqich", "State (Qatorlar bo'yicha HEX)"]
    steps = []

    if mode == "enc":
        s = block[:]
        steps.append(step(
            panel("1. BOSHLANG'ICH MA'LUMOTLAR VA MATRITSAGA JOYLASHTIRISH",
                  line("Ochiq matn: ", P(f'"{pt}"', "cyan", True), "  ·  Kalit: ", P(f'"{key_raw}"', "pink", True)),
                  line(P(padding_info, "slate")),
                  states(state("Ochiq matn (State)", s), "K0:", state("Kalit K0", rks[0])),
                  note("Matritsalarga joylash: baytlar ustun bo'yicha joylanadi (s[ustun*4 + qator]):",
                       *[f"{c + 1}-ustun: {hexl(s[c * 4:c * 4 + 4])}" for c in range(4)], color="cyan")),
            "Boshlang'ich ma'lumotlar: Ochiq matn (16 bayt) va Kalit K0 (16 bayt) 4×4 baytli State matritsalariga "
            "ustun-major tartibda (1–4-bayt birinchi ustun, 5–8-bayt ikkinchi ustun va h.k.) joylashtirildi.",
            row=["—", "Plaintext & K0", rows_str(s)]))

        a0, k0 = s[0], rks[0][0]
        before = s[:]
        s = add_round_key(s, rks[0])
        steps.append(step(
            panel("2. 0-RAUND: AddRoundKey (Boshlang'ich kalit qo'shish)",
                  states(state("State (Kirish)", before), "⊕", state("K0", rks[0]), "=", state("0-raund natijasi", s, 0)),
                  note("Misol: 0-ustun 0-bayt XOR hisobi (bit darajasida):",
                       f"State[0] = 0x{hx(a0)} = {a0:08b}", f"K0[0]    = 0x{hx(k0)} = {k0:08b}",
                       f"Natija   = 0x{hx(a0 ^ k0)} = {a0 ^ k0:08b}", color="green")),
            "0-raund: State ⊕ K0 amali bajarildi. Har bir bayt K0 kalitining mos bayti bilan bitma-bit XOR qilindi. "
            "Bu \"Key Whitening\" bosqichi.",
            row=["0", "AddRoundKey (K0)", rows_str(s)]))

        w3 = words[3]
        rot = [w3[1], w3[2], w3[3], w3[0]]
        sub = [SBOX[b] for b in rot]
        rc = [sub[0] ^ 1, sub[1], sub[2], sub[3]]
        steps.append(step(
            panel("3. KEY EXPANSION: 1-RAUND KALITI (K1) NI HOSIL QILISH",
                  states(state("K0 (w0, w1, w2, w3)", rks[0]), "→", state("K1 (w4, w5, w6, w7)", rks[1], 3)),
                  note(f"w3 = [{hexl(w3)}] → RotWord(w3) = [{hexl(rot)}]",
                       f"SubWord (S-box) = [{hexl(sub)}]",
                       f"⊕ Rcon[1] (01) = [{hexl(rc)}]",
                       f"w4 = w0 ⊕ [...] = [{hexl(words[0])}] ⊕ [{hexl(rc)}] = [{hexl(words[4])}]",
                       f"w5 = [{hexl(words[5])}]  |  w6 = [{hexl(words[6])}]  |  w7 = [{hexl(words[7])}]", color="violet")),
            "Key Expansion: K0 ni w0–w3 so'zlarga bo'lish → RotWord(w3) → SubWord → Rcon[1]=01 bilan XOR → "
            "w4 = w0 ⊕ (…) → w5, w6, w7 ketma-ket hisoblandi va 1-raund kaliti K1 hosil bo'ldi.",
            row=["—", "Key Expansion (K1)", rows_str(rks[1])]))

        r_in = s[:]
        s = sub_bytes(s)
        steps.append(step(
            panel("4. 1-RAUND: SubBytes (S-box bo'yicha almashtirish)",
                  states(state("Kirish State", r_in), "→", state("SubBytes natijasi", s, 1)),
                  note("S-box hisobi misoli:",
                       f"0x{hx(r_in[0])}: 1-HEX = qator {hx(r_in[0] >> 4)[1]}, 2-HEX = ustun {hx(r_in[0] & 15)[1]}.",
                       f"S-box[0x{hx(r_in[0])}] → 0x{hx(s[0])}.", color="pink")),
            f"1-raund SubBytes: har bir bayt S-box jadvali orqali almashtirildi (masalan, 0x{hx(r_in[0])} → 0x{hx(s[0])}). "
            f"S-box GF(2⁸) da multiplikativ teskari va affin almashtirish yordamida tuzilgan bo'lib, chiziqsizlikni ta'minlaydi.",
            row=["1", "SubBytes", rows_str(s)]))

        r_sb = s[:]
        s = shift_rows(s)
        steps.append(step(
            panel("5. 1-RAUND: ShiftRows (Qatorlarni siljitish)",
                  states(state("SubBytes chiqishi", r_sb), "→", state("ShiftRows natijasi", s, 2)),
                  note("Qatorlarni chapga siklik surish qoidasi:",
                       *[f"{r}-qator: {r} bayt chapga suriladi → {hexl([s[c * 4 + r] for c in range(4)])}" for r in range(4)],
                       color="blue")),
            "1-raund ShiftRows: State qatorlari siklik ravishda chapga surildi: 0-qator o'zgarmaydi, 1-qator 1, "
            "2-qator 2, 3-qator 3 bayt chapga suriladi. Bu baytlar o'rtasida diffuziyani boshlaydi.",
            row=["1", "ShiftRows", rows_str(s)]))

        r_sr = s[:]
        s = mix_columns(s)
        steps.append(step(
            panel("6. 1-RAUND: MixColumns (Ustunlarni aralashtirish)",
                  states(state("ShiftRows chiqishi", r_sr), "×", state("Matritsa", [2, 1, 1, 3, 3, 2, 1, 1, 1, 3, 2, 1, 1, 1, 3, 2]),
                         "=", state("MixColumns natijasi", s, 3)),
                  note("GF(2⁸) dagi ko'paytirish (0-ustun 0-bayti hisobi):",
                       f"2·{hx(r_sr[0])} = {hx(xtime(r_sr[0]))}  (chapga 1 surish, chap bit 1 bo'lsa ⊕ 0x1B)",
                       f"3·{hx(r_sr[1])} = (2·{hx(r_sr[1])}) ⊕ {hx(r_sr[1])} = {hx(mul_small(r_sr[1], 3))}",
                       f"Natija = {hx(xtime(r_sr[0]))} ⊕ {hx(mul_small(r_sr[1], 3))} ⊕ {hx(r_sr[2])} ⊕ {hx(r_sr[3])} = {hx(s[0])}",
                       color="orange")),
            f"1-raund MixColumns: har bir ustun GF(2⁸) maydonida o'zgarmas matritsaga ko'paytirildi. "
            f"2·x = chapga surish (agar chap bit 1 bo'lsa ⊕ 1B), 3·x = (2·x) ⊕ x, yig'ish = XOR. "
            f"0-ustun natijasi: {hexl(s[:4])}.",
            row=["1", "MixColumns", rows_str(s)]))

        r_mc = s[:]
        s = add_round_key(s, rks[1])
        steps.append(step(
            panel("7. 1-RAUND: AddRoundKey (K1 bilan XOR)",
                  states(state("MixColumns chiqishi", r_mc), "⊕", state("K1 kaliti", rks[1]), "=", state("1-raund yakuni", s, 0)),
                  note("0-ustun XOR misoli:",
                       "  |  ".join(f"{hx(r_mc[i])} ⊕ {hx(rks[1][i])} = {hx(s[i])}" for i in range(4)), color="green")),
            f"1-raund yakuni: MixColumns natijasi K1 bilan XOR qilindi (masalan, {hx(r_mc[0])} ⊕ {hx(rks[1][0])} = {hx(s[0])}).",
            row=["1", "AddRoundKey (K1)", rows_str(s)]))

        for r in range(2, 10):
            s = add_round_key(mix_columns(shift_rows(sub_bytes(s))), rks[r])
            steps.append(step(
                panel(f"{r}-RAUND (To'liq raund: SubBytes → ShiftRows → MixColumns → AddRoundKey)",
                      states(state(f"{r}-raund natijasi", s, r % 4), state(f"K{r} kaliti", rks[r])),
                      line(f"K{r}: ", P(hexl(rks[r]), "slate"))),
                f"{r}-raund yakunlandi: SubBytes → ShiftRows → MixColumns → AddRoundKey (K{r}).",
                row=[str(r), f"Raund {r} to'liq", rows_str(s)]))

        s = add_round_key(shift_rows(sub_bytes(s)), rks[10])
        steps.append(step(
            panel("10-RAUND (Oxirgi raund — MixColumns tashlab ketiladi)",
                  states(state("10-raund (Yakuniy State)", s, 2), "⊕", state("K10 kaliti", rks[10])),
                  note("Muhim xususiyat: oxirgi raundda MixColumns bajarilmaydi!",
                       "Faqat: SubBytes → ShiftRows → AddRoundKey(K10).", color="pink")),
            "10-raund (oxirgi): SubBytes → ShiftRows → AddRoundKey (K10). Oxirgi raundda MixColumns o'tkazilmaydi. "
            "Yakuniy shifrmatn hosil bo'ldi.",
            row=["10", "Oxirgi raund (MixColumns-siz)", rows_str(s)]))

        result_hex = "".join(hx(b) for b in s)
        steps.append(step(
            panel("✅ SHIFRLASH MUVAFFAQIYATLI YAKUNLANDI (AES-128)",
                  states(state("Yakuniy Ciphertext State", s, 2)),
                  line("Ciphertext (HEX): ", P(hexl(s), "green", True)),
                  line(P("Uzunligi: 128 bit (16 bayt, 32 ta HEX belgi)", "slate"))),
            f"AES-128 shifrlash yakunlandi. Natijaviy shifrmatn: {result_hex}",
            row=["Yakun", "Ciphertext", hexl(s)]))
        return {"steps": steps, "result": f"Ciphertext: {result_hex}", "data": {"hex": result_hex}, "table_cols": cols_}

    # ---------- DESHIFRLASH ----------
    s = block[:]
    x = add_round_key(s, rks[10])
    steps.append(step(
        panel("🔓 DESHIFRLASH: Boshlang'ich AddRoundKey (K10)",
              states(state("Kiruvchi Ciphertext", s), "⊕", state("K10", rks[10]), "=", state("Natija", x, 1)),
              line(P("Deshifrlash teskari tartibda K10 dan boshlanadi.", "slate"))),
        "Deshifrlash boshlanishi: shifrmatn K10 (oxirgi raund kaliti) bilan XOR qilinadi.",
        row=["10", "AddRoundKey (K10)", rows_str(x)]))
    s = x
    for r in range(9, 0, -1):
        s = inv_mix_columns(add_round_key(inv_sub_bytes(inv_shift_rows(s)), rks[r]))
        steps.append(step(
            panel(f"🔓 TESKARI RAUND {r} (InvShiftRows → InvSubBytes → AddRoundKey(K{r}) → InvMixColumns)",
                  states(state(f"{r}-raund chiqishi", s, r % 4), state(f"K{r}", rks[r]))),
            f"Teskari {r}-raund: InvShiftRows (o'ngga siljitish), InvSubBytes (teskari S-box), AddRoundKey (K{r}) va InvMixColumns bajarildi.",
            row=[str(r), f"Teskari raund {r}", rows_str(s)]))
    s = add_round_key(inv_sub_bytes(inv_shift_rows(s)), rks[0])
    steps.append(step(
        panel("🔓 OXIRGI TESKARI RAUND (InvShiftRows → InvSubBytes → AddRoundKey(K0))",
              states(state("Tiklangan State", s, 0), "⊕", state("K0", rks[0]))),
        "Oxirgi teskari raund yakunlandi: InvShiftRows → InvSubBytes → AddRoundKey (K0). Boshlang'ich ochiq matn to'liq tiklandi.",
        row=["0", "AddRoundKey (K0)", rows_str(s)]))

    unp = unpkcs7(s)
    text = _printable(bytes(unp).decode("utf-8", errors="replace"))
    result_hex = "".join(hx(b) for b in s)
    steps.append(step(
        panel("✅ DESHIFRLASH MUVAFFAQIYATLI YAKUNLANDI",
              states(state("Tiklangan Plaintext State", s, 0)),
              line("Tiklangan matn: ", P(f'"{text}"', "green", True)),
              line(P(f"HEX: {hexl(s)}  (PKCS#7 olib tashlangan: {hexl(unp)})", "slate"))),
        f"Deshifrlash yakunlandi. Asl matn: \"{text}\" (HEX: {result_hex})",
        row=["Yakun", "Plaintext", text]))
    return {"steps": steps, "result": f"Plaintext: {text} (HEX: {result_hex})", "data": {"hex": result_hex, "text": text},
            "table_cols": cols_}
