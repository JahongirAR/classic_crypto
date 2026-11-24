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
Yangi algoritm: `algorithms/_template.py` → `mening_shifrim.py`, `META` va `run()` ni to'ldiring,
`_build_manifest.py` ni ishga tushiring, yuklang. Karta, o'quv sahifa, taqqoslash qatori, topshiriq va savollar o'zi paydo bo'ladi.
Brauzerlar: Chrome/Edge/Firefox 114+/Safari 15+ (module worker kerak).

## API (ichki)
`algoritmlar/api.py` → `handle(method, path, body_json)`: `GET /api/catalog` · `POST /api/algo/<id>/run|live|action` · `POST /api/tool/<id>`
