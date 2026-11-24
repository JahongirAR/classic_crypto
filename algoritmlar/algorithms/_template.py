"""YANGI ALGORITM SHABLONI  (fayl nomi '_' bilan boshlangani uchun ilova uni yuklamaydi).

Qanday qo'shiladi:
  1. Bu faylni nusxalang:   algorithms/rot13.py   (nom '_' bilan BOSHLANMASIN)
  2. META va run() ni to'ldiring. Boshqa hech narsani o'zgartirish shart emas:
     bosh sahifada karta, o'quv sahifasi, taqqoslash jadvali va topshiriqlar o'zi paydo bo'ladi.
  3. Serverni qayta ishga tushirish shart emas (fayl avtomatik qayta yuklanadi) – brauzerda F5 bosing.
  4. python -m unittest   — yangi algoritm to'g'ri tuzilganini tekshiradi.

Misol sifatida ishlaydigan ROT13 shifri yozilgan.
"""
from core.helpers import error, l2n, n2l, only_letters, step      # umumiy yordamchilar
from core.visual import flow                                       # chizma turlari: flow, grid, big_text, panel(...)

META = {
    "id": "rot13",                        # noyob nom (URL va ichki identifikator)
    "name": "ROT13 (shablon)",            # kartada ko'rinadigan nom
    "order": 999,                         # kartalar tartibi (kichigi birinchi)
    "desc": "Har bir harf alifboda 13 o'rin siljitiladi.",
    "formula_enc": "C = (P + 13) mod 26",
    "formula_dec": "P = (C + 13) mod 26",
    "map": "PLAINTEXT\n   ↓\n+13 (mod 26)\n   ↓\nCIPHERTEXT",
    "weak": "Kalit yo'q – har kim bir zumda o'qiy oladi.",
    "explainer": {"why": "Sodda siljitish.", "how": "Har harf +13.", "math": "C=(P+13) mod 26", "weak": "Kalit yo'q."},
    # Kirish maydonlari. type: text | number | select (select uchun "options": [{"value","label"}])
    "inputs": [{"id": "pt", "label": "Plaintext / Ciphertext", "type": "text", "default": "HELLO"}],
    # Tayyor misollar: har biri inputs tartibidagi qiymatlar ro'yxati
    "examples": [["HELLO"], ["CRYPTO"]],
    # Ixtiyoriy: "Taqqoslash" jadvaliga qator (bo'lmasa jadvalda ko'rinmaydi)
    "compare": {"name": "ROT13", "type": "Substitution", "operation": "Shift 13", "key": "Yo'q", "feature": "O'z-o'ziga teskari"},
}

# Ixtiyoriy: "O'quv topshiriqlari" ga avtomatik qo'shiladi. "answer" berilmasa out["result"] to'g'ri javob bo'ladi.
PRACTICE = [
    {"lvl": "Boshlang'ich", "text": "ROT13 bilan 'HELLO' ni shifrlang.", "mode": "enc", "vals": {"pt": "HELLO"}},
]

# Ixtiyoriy: "Nazorat testi" ga qo'shiladi ("correct" – to'g'ri variant indeksi, 0 dan)
QUIZ = [
    {"q": "ROT13 ni ikki marta qo'llasak nima bo'ladi?", "opts": ["Asl matn", "Bo'sh matn", "Xatolik", "ROT26"], "correct": 0},
]

# Ixtiyoriy: kiritish maydonlari ostida JONLI panel (masalan, kalit tekshiruvi). Bo'lsa — avtomatik chaqiriladi.
# def live(vals): return panel("SARLAVHA", line("matn ", P("rangli", "green")))

# Ixtiyoriy: qo'shimcha tugmalar (META["actions"] = [{"id": "...", "label": "..."}]) va ularning funksiyalari:
# ACTIONS = {"mening_amalim": lambda vals: {"fill": {"key": "yangi qiymat"}}}   # fill – maydonlarni to'ldiradi


def run(mode, vals):
    """mode: 'enc' yoki 'dec'; vals: {input_id: matn}. Xato bo'lsa error(...) qaytaring.

    Qaytariladigan lug'at:
        steps      – step(visual, desc, answer=None, row=None) ro'yxati
        result     – yakuniy natija matni
        table_cols – jadval ustun nomlari (step(row=[...]) shu ustunlarga mos)
        extra      – ixtiyoriy: natijadan oldin ko'rsatiladigan panel
        data       – ixtiyoriy: boshqa kod ishlatadigan xom ma'lumot (masalan topshiriq javobi uchun)
    """
    text = only_letters(vals.get("pt"))
    if not text:
        return error("Matn kiriting (faqat A-Z harflar).")
    steps, out = [], []
    for ch in text:
        p = l2n(ch)
        c = (p + 13) % 26
        rc = n2l(c)
        out.append(rc)
        steps.append(step(
            flow(ch, (p, "dim"), ("+13 mod 26", "formula"), (c, "dim"), (rc, "result")),   # chizma
            f"'{ch}' → {p}; ({p}+13) mod 26 = {c} → '{rc}'.",                             # tushuntirish
            answer=rc,                                                                     # "Amaliy rejim" uchun
            row=[ch, p, c, rc]))                                                           # jadval qatori
    return {"steps": steps, "result": "".join(out), "table_cols": ["Belgi", "P", "C (son)", "C (harf)"]}
