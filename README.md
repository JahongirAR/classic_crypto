# Classical Cryptography Visualizer

Server kerak emas: butun Python (`algoritmlar/`) foydalanuvchining brauzerida ishlaydi (Pyodide).
Havolani ochgan har kim — telefon, planshet, kompyuter — hech narsa o'rnatmasdan foydalanadi.
Bir marta ochgach internetsiz ham ishlaydi, va "Bosh ekranga qo'shish" orqali ilova kabi o'rnatiladi.

```
crypto/
├── index.html · css/style.css · js/main.js     frontend (dizayn va interfeys)
├── js/worker.js                                Python'ni brauzerda ishga tushiradi
├── sw.js · manifest.webmanifest · icons/       oflayn ishlash va "ilova sifatida o'rnatish"
├── pyodide/                                    Python interpretatori (WebAssembly), ~13 MB
└── algoritmlar/                                BACKEND (barcha Python kod)
    ├── api.py · core/ · algorithms/ · tools/
    ├── manifest.json                           brauzerga qaysi .py fayllar kerakligi
    └── tests/ · server.py · _build_manifest.py (faqat dasturchi uchun)
```

## Internetga chiqarish (bepul, terminalsiz)

Papkani (`crypto`) shu yerlardan biriga yuklang — sizga `https://…` havola beriladi:

- **Netlify Drop**: app.netlify.com/drop sahifasiga papkani tashlang.
- **GitHub Pages**: papkani repoga yuklab, Settings → Pages → branch tanlang (`.nojekyll` fayli kerak, o'chirmang).
- **Cloudflare Pages**: Direct Upload.

Faylni ikki marta bosib (`file://`) ochib bo'lmaydi: brauzer xavfsizligi Python'ni fayldan yuklashga ruxsat bermaydi. Sayt `https://` yoki `http://localhost` orqali ochiladi.

## Dasturchi uchun

```
python algoritmlar/server.py                                   # mahalliy ko'rish (http://127.0.0.1:8000)
python algoritmlar/_build_manifest.py                          # .py fayl qo'shgach/o'zgartirgach
python -m unittest discover -s algoritmlar/tests -t algoritmlar
```

Yangi algoritm: `algorithms/_template.py` → o'zbekcha CamelCase nomli fayl (masalan, `MeningShifrim.py`), `META` va `run()` ni to'ldiring,
`_build_manifest.py` ni ishga tushiring, yuklang. Karta, o'quv sahifa, taqqoslash qatori, topshiriq va savollar o'zi paydo bo'ladi.
Fayl nomi o'zgarsa ham, `META["id"]` qiymatini o'zgartirmang — u API va ilova uchun doimiy identifikator.
Brauzerlar: Chrome/Edge/Firefox 114+/Safari 15+ (module worker kerak).

ElGamal demo'sida `p` tub son, `g` esa generator bo'lishi kerak. `x` — maxfiy kalit;
shifrlashda har bir matn belgisi uchun alohida `k` kiriting. Shifrmatn `C₁:C₂; C₁:C₂` ko'rinishida
beriladi. Ilovadagi kichik sonli namoyish haqiqiy maxfiy ma'lumotlar uchun mo'ljallanmagan.

Xesh algoritmlar qatorida SHA-256, SHA-512, SHA-1, SHA-224, SHA-384 va MD5 tanlanadi.
Digestni hisoblash yoki matn bilan berilgan digest mosligini tekshirish mumkin.
MD5 va SHA-1 eskirgan va xavfsiz maqsadlar uchun tavsiya etilmaydi.

ECC bo'limida kichik tub maydonlarda egri chiziq nuqtalarini qo'shish va Double-and-Add
orqali kP hisoblanadi. Qadamlar, nuqta tartibi, egri chiziqdagi nuqtalar soni va Hasse chegarasi
ko'rsatiladi. Grafikda kiritilgan a va b koeffitsiyentlari bilan haqiqiy sonlardagi uzluksiz egri
chiziq, uning ostida esa F_p dagi alohida nuqtalar ko'rsatiladi. Bu faqat o'quv namoyishi; haqiqiy
himoya uchun emas.

## API (ichki)

`algoritmlar/api.py` → `handle(method, path, body_json)`: `GET /api/catalog` · `POST /api/algo/<id>/run|live|action` · `POST /api/tool/<id>`
