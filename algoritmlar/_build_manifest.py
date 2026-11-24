"""Brauzer uchun fayllar ro'yxatini (manifest.json) yaratadi.

Yangi algoritm/yordamchi qo'shgach (yoki biror .py faylni o'zgartirgach) shuni ishga tushiring:
    python algoritmlar/_build_manifest.py
Test (python -m unittest ...) manifest eskirgan bo'lsa ogohlantiradi.
"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {"__pycache__", "tests"}
SKIP_FILES = {"server.py", "_build_manifest.py", "manifest.json"}


def collect():
    files = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        for fn in sorted(fns):
            if not fn.endswith(".py") or fn in SKIP_FILES or fn.startswith("_template"):
                continue
            files.append(os.path.relpath(os.path.join(dp, fn), ROOT).replace(os.sep, "/"))
    return sorted(files)


def build():
    files = collect()
    h = hashlib.sha256()
    for f in files:
        h.update(f.encode())
        with open(os.path.join(ROOT, f), "rb") as fh:
            h.update(fh.read())
    return {"version": h.hexdigest()[:12], "files": files}


if __name__ == "__main__":
    m = build()
    with open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=1)
    print(f"manifest.json yangilandi: {len(m['files'])} ta fayl, versiya {m['version']}")
