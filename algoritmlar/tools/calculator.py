"""Sanoq sistemasi va matn kalkulyatori (ikki bo'lim: sonlar va matn ⇄ kodlar).

Forma-asosidagi yordamchi funksiya (kind="form"): maydonlar META["sections"] da e'lon qilinadi,
natija "bloklar" ro'yxati sifatida qaytadi. Yangi shunday funksiya yozish uchun
_template_tool.py ga qarang – HTML'ni o'zgartirish shart emas.
"""
import re

META = {
    "id": "calculator",
    "title": "Sanoq sistemasi kalkulyatori",
    "subtitle": "Sanoq & Matn konvertatsiyasi",
    "order": 40,
    "kind": "form",
    "heading": "🔢 Sanoq Sistemasi & Matn Kalkulatori",
    "intro": "Sanoq sistemalari (2, 8, 10, 16) o'rtasida hamda matn va kodlar o'rtasida to'liq o'tkazma",
}

_BASE_OPTS = [
    {"value": "2", "label": "Ikkilik (Binary, 2)"},
    {"value": "8", "label": "Sakkizlik (Octal, 8)"},
    {"value": "10", "label": "O'nlik (Decimal, 10)"},
    {"value": "16", "label": "O'n oltillik (Hex, 16)"},
]

META["sections"] = [
    {
        "id": "num",
        "tab": "🔢 1-bo'lim: Sanoqdan sanoqqa (Sonlar)",
        "button": "= Hisobla",
        "auto": False,
        "fields": [
            {"id": "from", "label": "KIRISH SANOQ SISTEMASI", "type": "select", "options": _BASE_OPTS, "default": "10"},
            {"id": "value", "label": "SON (KIRITILGAN QIYMAT)", "type": "text", "placeholder": "Masalan: 255", "default": "", "wide": True},
            {"type": "arrow"},
            {"id": "to", "label": "CHIQISH SANOQ SISTEMASI", "type": "select", "options": _BASE_OPTS, "default": "2"},
        ],
        "examples": [
            {"label": "255 → Binary", "vals": {"value": "255", "from": "10", "to": "2"}},
            {"label": "255 → Hex", "vals": {"value": "255", "from": "10", "to": "16"}},
            {"label": "FF → Decimal", "vals": {"value": "FF", "from": "16", "to": "10"}},
            {"label": "11111111 → Decimal", "vals": {"value": "11111111", "from": "2", "to": "10"}},
            {"label": "11111111 → Hex", "vals": {"value": "11111111", "from": "2", "to": "16"}},
            {"label": "42 → Octal", "vals": {"value": "42", "from": "10", "to": "8"}},
        ],
    },
    {
        "id": "text",
        "tab": "🔤 2-bo'lim: Matndan sanoqqa (Text ⇄ Kodlar)",
        "button": "= O'tkazish",
        "auto": True,
        "fields": [
            {"id": "dir", "label": "YO'NALISH", "type": "select", "default": "text2base",
             "options": [{"value": "text2base", "label": "🔤 Matn → Sanoq sistemasi"},
                         {"value": "base2text", "label": "🔢 Sanoq sistemasi → Matn"}]},
            {"id": "base", "label": "SANOQ SISTEMASI", "type": "select", "default": "2",
             "options": [{"value": "2", "label": "Ikkilik (Binary, 8-bit)"},
                         {"value": "16", "label": "O'n oltillik (Hex, 2-belgi)"},
                         {"value": "10", "label": "O'nlik (Decimal)"},
                         {"value": "8", "label": "Sakkizlik (Octal)"}]},
            {"id": "sep", "label": "AJRATUVCHI (SEPARATOR)", "type": "select", "default": "space",
             "options": [{"value": "space", "label": "Bo'sh joy (Space)"},
                         {"value": "none", "label": "Ajratmasdan (Yaxlit)"},
                         {"value": "comma", "label": "Vergul (, )"},
                         {"value": "dash", "label": "Chiziqcha (-)"}]},
            {"id": "value", "label": "KIRITILADIGAN MATN YOKI KODLAR", "type": "textarea", "default": "",
             "placeholder": "Matn kiriting (masalan: Salom) yoki kodlar (01010011 01100001 yoki 53 61 6C)…"},
        ],
        "examples": [
            {"label": '"Salom"', "vals": {"value": "Salom", "dir": "text2base"}},
            {"label": '"Kriptografiya"', "vals": {"value": "Kriptografiya", "dir": "text2base"}},
            {"label": '"AES-128"', "vals": {"value": "AES-128", "dir": "text2base"}},
            {"label": '"Hello World!"', "vals": {"value": "Hello World!", "dir": "text2base"}},
            {"label": 'Ikkilik → "Kripto"', "vals": {"value": "01001011 01110010 01101001 01110000 01110100 01101111", "dir": "base2text", "base": "2"}},
            {"label": 'Hex → "Salom"', "vals": {"value": "53 61 6C 6F 6D", "dir": "base2text", "base": "16"}},
        ],
    },
]

DIGITS = "0123456789ABCDEF"
NAMES = {2: "Binary (2)", 8: "Octal (8)", 10: "Decimal (10)", 16: "Hex (16)"}


# ---------- yordamchi funksiyalar ----------
def to_base(n: int, base: int) -> str:
    if n == 0:
        return "0"
    s = ""
    while n > 0:
        s = DIGITS[n % base] + s
        n //= base
    return s


def valid(s: str, base: int) -> bool:
    return bool(s) and all(c in DIGITS[:base] for c in s.upper())


def S(t, cls=None, sup=False):
    return {"t": str(t), "cls": cls, "sup": sup}


def step_block(num, lines, tbl=None):
    return {"k": "step", "num": str(num), "lines": lines, "table": tbl}


# ---------- 1-bo'lim: sanoqdan sanoqqa ----------
def _num_steps(raw, fb, tb, dec):
    if fb == tb:
        return [step_block("ℹ", [["Kirish va chiqish sanoq sistemasi bir xil — o'tkazma kerak emas."],
                                  ["Natija: ", S(raw, "hl-sum")]])]
    blocks = []
    if fb != 10:
        blocks.append({"k": "heading", "t": f"1️⃣  {NAMES[fb]} → O'nlik (Decimal) o'tkazma"})
        digits = list(raw)
        L = len(digits)
        parts = [(d, L - 1 - idx, int(d, 16) * fb ** (L - 1 - idx)) for idx, d in enumerate(digits)]
        expr = []
        for j, (d, i, _) in enumerate(parts):
            if j:
                expr.append(" + ")
            expr += [S(d, "hl-bit"), f"×{fb}", S(i, None, True)]
        rows = [[S(d, "hl-bit"), S(i, "hl-pos"), f"{fb}^{i} = {fb ** i}",
                 [S(d, "hl-div"), f" × {fb ** i} = ", S(pv, "hl-quot")]] for d, i, pv in parts]
        rows.append([{"t": "JAMI =", "colspan": 3, "align": "right", "b": True}, S(dec, "hl-sum")])
        blocks.append(step_block(1, [
            [S("Pozitsion qiymat formulasi:", "hl-div")],
            ["N = Σ (raqam × asos", S("pozitsiya", None, True), ")"],
            ["N = "] + expr + [" = ", S(dec, "hl-sum")],
        ], {"head": ["Raqam", "Pozitsiya (i)", "Qiymat", "Hisob"], "rows": rows}))
    else:
        blocks.append({"k": "heading", "t": f"Kirish soni allaqachon o'nlik sistemada: {dec}"})

    if tb != 10:
        blocks.append({"k": "heading", "t": f"2️⃣  O'nlik → {NAMES[tb]} o'tkazma (ketma-ket bo'lish usuli)", "mt": True})
        div, tmp = [], dec
        if tmp == 0:
            div.append((0, 0, 0))
        while tmp > 0:
            div.append((tmp, tmp // tb, tmp % tb))
            tmp //= tb
        digits_out = "".join(DIGITS[r] for _, _, r in reversed(div))
        rows = [[S(n, "hl-div"), f"÷ {tb}", S(q, "hl-quot"), S(r, "hl-rem"), S(DIGITS[r], "hl-bit")] for n, q, r in div]
        rows.append([{"t": "Natija (qoldiqlar teskari) →", "colspan": 4, "align": "right"}, S(digits_out, "hl-sum")])
        blocks.append(step_block(2, [
            [S(f"Usul: o'nlik sonni {tb} ga ketma-ket bo'lamiz, qoldiqlarni yig'amiz.", "hl-div")],
            ["Qoldiqlar teskari tartibda yoziladi → ", S(digits_out, "hl-sum")],
        ], {"head": ["Son", f"÷ {tb}", "Natija (bo'linma)", "Qoldiq", "Raqam"], "rows": rows}))
    elif fb != 10:
        blocks.append(step_block(2, [["Natija allaqachon o'nlikka aylangan: ", S(dec, "hl-sum")]]))
    return blocks


def run_num(vals):
    raw = (vals.get("value") or "").strip().upper()
    fb, tb = int(vals.get("from", 10)), int(vals.get("to", 2))
    if not raw:
        return {"blocks": [{"k": "error", "t": "❌ Son kiriting."}]}
    if not valid(raw, fb):
        return {"blocks": [{"k": "error", "t": f"❌ \"{raw}\" soni {NAMES[fb]} sistemasida noto'g'ri. "
                                              f"Faqat: {DIGITS[:fb]} raqamlar ishlatiladi."}]}
    dec = int(raw, fb)
    blocks = [
        {"k": "bar", "from": NAMES[fb], "input": raw, "to": NAMES[tb], "output": to_base(dec, tb)},
        {"k": "boxes", "items": [{"label": NAMES[b], "value": to_base(dec, b)} for b in (2, 8, 10, 16)]},
    ]
    return {"blocks": blocks + _num_steps(raw, fb, tb, dec)}


# ---------- 2-bo'lim: matn ⇄ kodlar (UTF-8 baytlari bilan) ----------
_SEP = {"space": " ", "none": "", "comma": ", ", "dash": "-"}


def _fmt(byte: int, base: int) -> str:
    return {2: format(byte, "08b"), 8: format(byte, "03o"), 10: str(byte), 16: format(byte, "02X")}[base]


def _show_char(ch):
    return {" ": "[Bo'sh joy]", "\n": "[Yangi qator]", "\t": "[Tab]"}.get(ch, ch)


def run_text(vals):
    raw = vals.get("value") or ""
    if not raw:
        return {"blocks": []}
    direction = vals.get("dir", "text2base")
    base = int(vals.get("base", 2))
    sep = _SEP.get(vals.get("sep", "space"), " ")

    if direction == "text2base":
        rows, all_bytes = [], []
        idx = 0
        for ch in raw:
            bs = list(ch.encode("utf-8"))
            for k, b in enumerate(bs):
                idx += 1
                all_bytes.append(b)
                shown = _show_char(ch) if k == 0 else f"↳ ({ch} davomi)"
                rows.append([str(idx), shown, S(b, "hl-quot"), S(_fmt(b, 16), "hl-div"), S(_fmt(b, 8), "hl-rem"),
                             S(_fmt(b, 2), "hl-bit"), {"bits": _fmt(b, 2)}])
        note = []
        if len(all_bytes) != len(raw):
            note = [{"k": "heading", "t": "ℹ Ba'zi belgilar (masalan oʻ, kirill) UTF-8 da 2+ bayt egallaydi — jadval bayt-bayt ko'rsatadi."}]
        return {"blocks": [
            {"k": "box", "title": f"NATIJA: Matn → {NAMES[base]}", "value": sep.join(_fmt(b, base) for b in all_bytes)},
            {"k": "boxes", "small": True, "items": [
                {"label": "Binary (8-bit baytlar)", "value": " ".join(_fmt(b, 2) for b in all_bytes)},
                {"label": "Hex (O'n oltillik baytlar)", "value": " ".join(_fmt(b, 16) for b in all_bytes)},
                {"label": "Decimal (bayt kodlari)", "value": " ".join(_fmt(b, 10) for b in all_bytes)},
                {"label": "Octal (Sakkizlik)", "value": " ".join(_fmt(b, 8) for b in all_bytes)}]},
            *note,
            {"k": "table", "title": "📋 Har bir bayt bo'yicha tahlil jadvali:",
             "head": ["#", "Belgi", "Bayt (Dec)", "Hex (16)", "Octal (8)", "Binary (8-bit)", "Bitlar vizualizatsiyasi"],
             "rows": rows},
        ]}

    text = raw.strip()
    if re.search(r"[\s,;\-]", text):
        chunks = [c for c in re.split(r"[\s,;\-]+", text) if c]
    else:
        size = {2: 8, 16: 2, 8: 3}.get(base)
        chunks = [text[i:i + size] for i in range(0, len(text), size)] if size else [text]

    errors, data = [], []
    fixed = None if re.search(r"[\s,;\-]", text) else {2: 8, 16: 2, 8: 3}.get(base)
    for i, ch in enumerate(chunks):
        if fixed and len(ch) != fixed:
            errors.append(f"#{i + 1} \"{ch}\" to'liq emas ({NAMES[base]} da {fixed} belgi kerak; yoki ajratuvchi ishlating)")
            continue
        if not valid(ch, base):
            errors.append(f"#{i + 1} \"{ch}\" {NAMES[base]} uchun yaroqsiz")
            continue
        v = int(ch, base)
        if v > 255:
            errors.append(f"#{i + 1} \"{ch}\" = {v} — bayt 0–255 oralig'ida bo'lishi kerak")
            continue
        data.append((ch, v))
    if errors:
        more = "..." if len(errors) > 3 else ""
        return {"blocks": [{"k": "error", "t": "❌ Xatolik: " + ", ".join(errors[:3]) + more}]}
    decoded = bytes(v for _, v in data).decode("utf-8", errors="replace")
    rows = [[str(i + 1), S(c, "hl-div"), S(v, "hl-quot"),
             {"t": _show_char(chr(v)) if v < 128 else f"bayt 0x{v:02X}", "b": True}] for i, (c, v) in enumerate(data)]
    return {"blocks": [
        {"k": "box", "title": f"NATIJA: {NAMES[base]} → Matn", "value": decoded},
        {"k": "table", "title": "📋 Dekodlangan baytlar jadvali:",
         "head": ["#", f"Kiritilgan kod ({NAMES[base]})", "O'nlik (bayt)", "Bayt belgisi"], "rows": rows},
    ]}


def handle(action, payload):
    if action != "run":
        return {"error": f"Noma'lum amal: {action}"}
    vals = payload.get("vals") or {}
    try:
        if payload.get("section") == "num":
            return run_num(vals)
        if payload.get("section") == "text":
            return run_text(vals)
    except (ValueError, KeyError) as e:
        return {"blocks": [{"k": "error", "t": f"❌ Xatolik: {e}"}]}
    return {"error": "Noma'lum bo'lim."}
