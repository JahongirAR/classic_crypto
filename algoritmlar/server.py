#!/usr/bin/env python3
"""FAQAT mahalliy ko'rish uchun oddiy statik server (ishlab chiqish paytida).

Saytning o'zi serverga muhtoj emas: hamma Python brauzerda (Pyodide) ishlaydi.
Faqat web papkani ko'rsatadi:   python algoritmlar/server.py
"""
import argparse
import functools
import http.server
import os
import threading
import webbrowser

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".wasm": "application/wasm", ".mjs": "text/javascript", ".js": "text/javascript",
                      ".webmanifest": "application/manifest+json"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    handler = functools.partial(Handler, directory=WEB)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), handler)
    url = f"http://127.0.0.1:{a.port}/"
    print(f"Mahalliy ko'rish: {url}   (to'xtatish: Ctrl+C)")
    if not a.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
