"""Nazorat testi.

Savollar shu faylda (QUESTIONS). Algoritm fayllarida ham `QUIZ = [...]` bo'lishi mumkin –
ular avtomatik qo'shiladi. To'g'ri javob mijozga oldindan yuborilmaydi (faqat javob berilgandan keyin).
"""

from core import registry

META = {"id": "quiz", "title": "Nazorat testi", "subtitle": "Quiz", "order": 30, "kind": "quiz"}

# "correct" – opts ichidagi to'g'ri variant indeksi (0 dan boshlanadi)
QUESTIONS = [
    {"q": "DES qancha bitli bloklar bilan ishlaydi?",
     "opts": ["32-bit", "64-bit", "128-bit", "256-bit"],
     "correct": 1},
    {"q": "DES algoritmida nechta Feistel raundi mavjud?",
     "opts": ["8", "12", "16", "32"],
     "correct": 2},
    {"q": "DES kalitining samarali uzunligi necha bit?",
     "opts": ["64-bit", "56-bit", "48-bit", "128-bit"],
     "correct": 1},
    {"q": "DES Feistel raundida f-funksiya ichida qaysi amallar bajariladi?",
     "opts": ["Faqat XOR", "E kengaytirish → XOR → S-box → P-almashtirish", "Matritsa ko'paytirish → mod 26", "Faqat S-box"],
     "correct": 1},
    {"q": "DES deshifrlashda raund kalitlari qanday tartibda ishlatiladi?",
     "opts": ["K1, K2, ..., K16 (xuddi shifrlashdek)", "K16, K15, ..., K1 (teskari tartibda)", "Tasodifiy tartibda", "Faqat bitta kalit ishlatiladi"],
     "correct": 1},
    {"q": "AES-128 nechta raund bilan ishlaydi?",
     "opts": ["8", "10", "12", "16"],
     "correct": 1},
    {"q": "AES har raundida qanday 4 ta amal bajariladi?",
     "opts": ["XOR → S-box → P → Feistel", "SubBytes → ShiftRows → MixColumns → AddRoundKey", "IP → E → S-box → IP⁻¹", "Faqat SubBytes va AddRoundKey"],
     "correct": 1},
    {"q": "AES ning State qanday o'lchamdagi matritsa?",
     "opts": ["2×2 bayt", "8×8 bit", "4×4 bayt", "4×8 bayt"],
     "correct": 2},
    {"q": "AES da ShiftRows amali nima qiladi?",
     "opts": ["Baytlarni S-box orqali almashtiradi", "Ustunlarni GF(2⁸) da ko'paytiradi", "Qatorlarni siklik ravishda siljitadi", "Kalit bilan XOR qiladi"],
     "correct": 2},
    {"q": "AES da MixColumns amali qaysi matematik maydon ustida ishlaydi?",
     "opts": ["Mod 26 arifmetika", "GF(2⁸) Galua maydoni", "Mod 256 butun sonlar", "Kompleks sonlar"],
     "correct": 1},
    {"q": "Caesar shifrining formulasi qaysi?",
     "opts": ["C=(P+k) mod 26", "C=P×k mod 26", "C=P⊕k", "C=(P-k)×26"],
     "correct": 0},
    {"q": "Atbash shifrida A harfi nimaga mos keladi?",
     "opts": ["A", "M", "Z", "N"],
     "correct": 2},
    {"q": "Substitution va transposition shifrlari orasidagi asosiy farq nima?",
     "opts": ["Substitution harflarni almashtiradi, transposition joylashuvni o'zgartiradi", "Ikkalasi bir xil", "Transposition kalit ishlatmaydi", "Substitution faqat raqamlar bilan ishlaydi"],
     "correct": 0},
    {"q": "Affine shifrida 'a' qanday shartga javob berishi kerak?",
     "opts": ["a har doim 1 bo'lishi kerak", "gcd(a,26)=1", "a juft son bo'lishi kerak", "a>26 bo'lishi kerak"],
     "correct": 1},
    {"q": "Vigenère shifrining formulasi qaysi?",
     "opts": ["Cᵢ=(Pᵢ+Kᵢ) mod 26", "Cᵢ=Pᵢ×Kᵢ", "Cᵢ=Pᵢ⊕Kᵢ", "Cᵢ=(Pᵢ-26) mod Kᵢ"],
     "correct": 0},
    {"q": "Vigenère shifrida kalit so'zi qisqa bo'lsa, u nima qilinadi?",
     "opts": ["Bir marta ishlatiladi", "Matn oxirigacha takrorlanadi", "Random to'ldiriladi", "Ishlatilmaydi"],
     "correct": 1},
    {"q": "Rail Fence shifri qaysi turga kiradi?",
     "opts": ["Substitution", "Polyalphabetic", "Transposition", "Bitwise"],
     "correct": 2},
    {"q": "Columnar Transposition'da ustunlar qanday tartibda o'qiladi?",
     "opts": ["Chapdan o'ngga oddiy tartibda", "Kalit raqamlari tartibida", "Tasodifiy tartibda", "Faqat oxirgi ustun o'qiladi"],
     "correct": 1},
    {"q": "Hill Cipher qanday matematik vositadan foydalanadi?",
     "opts": ["Ehtimollik nazariyasi", "Matritsalar (chiziqli algebra)", "Grafiklar nazariyasi", "Differensial tenglamalar"],
     "correct": 1},
    {"q": "Hill Cipher kaliti (matritsasi) uchun qanday shart bajarilishi kerak?",
     "opts": ["Determinant 0 bo'lishi kerak", "gcd(det(K),26)=1", "Matritsa kvadrat bo'lmasligi kerak", "Barcha elementlar manfiy bo'lishi kerak"],
     "correct": 1},
    {"q": "XOR shifrlash formulasi qaysi?",
     "opts": ["C=P+K", "C=P⊕K", "C=P mod K", "C=P×K mod 26"],
     "correct": 1},
    {"q": "XOR shifrida deshifrlash qanday amalga oshiriladi?",
     "opts": ["Ciphertext yana K bilan XOR qilinadi", "Ciphertextdan K ayiriladi", "Ciphertext K ga bo'linadi", "Iloji yo'q, XOR qaytarilmas"],
     "correct": 0},
    {"q": "'Brute-force' hujumi nimani anglatadi?",
     "opts": ["Barcha mumkin bo'lgan kalitlarni ketma-ket sinab ko'rish", "Faqat statistik tahlil", "Kalitni so'rab olish", "Shifrni buzmaslik"],
     "correct": 0},
    {"q": "'Frequency analysis' qaysi shifrlarga qarshi ayniqsa samarali?",
     "opts": ["XOR", "One-Time Pad", "Monoalphabetic substitution", "Hill Cipher (katta matritsa bilan)"],
     "correct": 2},
    {"q": "Qaysi klassik shifr nazariy jihatdan buzilmas hisoblanadi (to'g'ri sharoitda)?",
     "opts": ["Caesar Cipher", "One-Time Pad (tasodifiy, bir martalik kalit bilan XOR)", "Atbash Cipher", "Rail Fence Cipher"],
     "correct": 1},
]


def all_questions():
    qs = list(QUESTIONS)
    for entry in registry.algorithms():
        qs.extend(getattr(entry["module"], "QUIZ", []))
    return qs


def subtitle():
    return f"{len(all_questions())} ta savol"


def handle(action, payload):
    qs = all_questions()
    if action == "list":
        return {"questions": [{"q": x["q"], "opts": x["opts"]} for x in qs]}
    if action == "answer":
        i = payload.get("i")
        if not isinstance(i, int) or not 0 <= i < len(qs):
            return {"error": "Savol topilmadi."}
        return {"correct": qs[i]["correct"]}
    if action == "finish":
        answers = payload.get("answers") or []
        score = sum(1 for i, x in enumerate(qs) if i < len(answers) and answers[i] == x["correct"])
        return {"score": score, "total": len(qs), "pct": round(score / len(qs) * 100, 1) if qs else 0}
    return {"error": f"Noma'lum amal: {action}"}
