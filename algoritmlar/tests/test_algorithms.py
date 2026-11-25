"""Avtomatik testlar:  python -m unittest   (loyiha papkasida)

Standart test vektorlari + har bir algoritm/yordamchi to'g'ri tuzilganini tekshiradi.
Yangi algoritm yozganingizda META to'liq emas bo'lsa yoki misollari xato bersa – shu yerda bilinadi.
"""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from core import registry  # noqa: E402

run = registry.run_algorithm
REQUIRED = ("id", "name", "order", "desc", "formula_enc", "formula_dec", "map", "weak", "explainer", "inputs", "examples")


def res(algo, mode, **vals):
    out = run(algo, mode, vals)
    assert "error" not in out, out
    return out["result"]


class Vectors(unittest.TestCase):
    def test_classical(self):
        self.assertEqual(res("caesar", "enc", pt="HELLO", key=3), "KHOOR")
        self.assertEqual(res("caesar", "dec", pt="KHOOR", key=3), "HELLO")
        self.assertEqual(res("atbash", "enc", pt="HELLO"), "SVOOL")
        self.assertEqual(res("affine", "enc", pt="HELLO", a=5, b=8), "RCLLA")
        self.assertEqual(res("affine", "dec", pt="RCLLA", a=5, b=8), "HELLO")
        self.assertEqual(res("vigenere", "enc", pt="ATTACKATDAWN", key="LEMON"), "LXFOPVEFRNHR")
        self.assertEqual(res("rail", "enc", pt="WEAREDISCOVEREDFLEEATONCE", rails=3), "WECRLTEERDSOEEFEAOCAIVDEN")
        self.assertEqual(res("rail", "dec", pt="WECRLTEERDSOEEFEAOCAIVDEN", rails=3), "WEAREDISCOVEREDFLEEATONCE")
        enc = res("columnar", "enc", pt="THISISATESTMESSAGE", key="3142")
        self.assertEqual(res("columnar", "dec", pt=enc, key="3142"), "THISISATESTMESSAGEXX")   # oxirgi XX – to'ldiruvchi

    def test_hill(self):
        self.assertEqual(res("hill", "enc", pt="ACT", matrix="6 24 1; 13 16 10; 20 17 15"), "POH")   # Wikipedia
        self.assertEqual(res("hill", "enc", pt="HELP", matrix="3 3; 2 5"), "HIAT")                  # Wikipedia
        self.assertEqual(res("hill", "enc", pt="PAYMOREMONEY", matrix="17 17 5; 21 18 21; 2 2 19"), "LNSHDLEWMTRW")
        self.assertEqual(res("hill", "dec", pt="HIAT", matrix="3 3; 2 5"), "HELP")
        self.assertIn("error", run("hill", "enc", {"pt": "ACT", "matrix": "6 24 1 13"}))             # det mod 26 = 2

    def test_xor(self):
        out = run("xor", "enc", {"pt": "HI", "key": "K"})
        self.assertEqual(out["data"]["codes"], [3, 2])
        self.assertTrue(res("xor", "dec", pt="3, 2", key="K", fmt="dec").startswith("Tiklangan matn: HI"))

    def test_des(self):
        self.assertEqual(run("des", "enc", {"pt": "0123456789ABCDEF", "key": "133457799BBCDFF1"})["data"]["hex"], "85E813540F0AB405")
        self.assertEqual(run("des", "dec", {"pt": "85E813540F0AB405", "key": "133457799BBCDFF1"})["data"]["hex"], "0123456789ABCDEF")

    def test_aes(self):   # FIPS-197, Appendix C.1
        k = "000102030405060708090A0B0C0D0E0F"
        self.assertEqual(run("aes", "enc", {"pt": "00112233445566778899AABBCCDDEEFF", "key": k})["data"]["hex"], "69C4E0D86A7B0430D8CDB78070B4C55A")
        self.assertEqual(run("aes", "dec", {"pt": "69C4E0D86A7B0430D8CDB78070B4C55A", "key": k})["data"]["hex"], "00112233445566778899AABBCCDDEEFF")
        e = run("aes", "enc", {"pt": "Fhishing", "key": "Kriptografiya_01"})["data"]["hex"]
        self.assertEqual(run("aes", "dec", {"pt": e, "key": "Kriptografiya_01"})["data"]["text"], "Fhishing")

    def test_aes_keeps_trailing_spaces(self):   # 16 bayt, padding yo'q
        out = run("aes", "enc", {"pt": "SALOM AES DEMO  ", "key": "AABB09182736CCDD1122334455667788"})
        self.assertEqual(out["data"]["hex"], "3668DF9DF994B932902551C81B82E2C2")

    def test_rsa_limits(self):
        self.assertIn("error", run("rsa", "enc", {"primes": "61, 53", "e": "9" * 5000, "pt": "A"}))

    def test_rsa(self):
        for primes, e, text in (("61, 53", "17", "SALOM"), ("137, 139", "5", "Kripto"), ("3, 11, 17", "3", "RSA")):
            enc = run("rsa", "enc", {"primes": primes, "e": e, "pt": text})
            self.assertNotIn("error", enc, enc)
            dec = run("rsa", "dec", {"primes": primes, "e": e, "pt": enc["data"]["cipher"]})
            self.assertEqual(dec["data"]["text"], text)

    def test_elgamal(self):
        vals = {"p": "467", "g": "2", "x": "127", "ks": "53, 89, 101, 151, 177", "pt": "SALOM"}
        enc = run("elgamal", "enc", vals)
        self.assertNotIn("error", enc, enc)
        self.assertEqual(len(enc["data"]["cipher"].split(";")), len(vals["pt"]))
        dec = run("elgamal", "dec", {**vals, "pt": enc["data"]["cipher"]})
        self.assertNotIn("error", dec, dec)
        self.assertEqual(dec["data"]["text"], vals["pt"])

    def test_elgamal_validates_parameters_and_ciphertext(self):
        base = {"p": "467", "g": "2", "x": "127", "ks": "53", "pt": "A"}
        self.assertIn("error", run("elgamal", "enc", {**base, "p": "15"}))
        self.assertIn("error", run("elgamal", "enc", {**base, "g": "4"}))
        self.assertIn("error", run("elgamal", "enc", {**base, "ks": "467"}))
        self.assertIn("error", run("elgamal", "dec", {**base, "pt": "1,2"}))
        self.assertIn("error", run("elgamal", "enc", {**base, "pt": "AB"}))
        self.assertIn("error", run("elgamal", "enc", {**base, "pt": "\x00"}))


class Structure(unittest.TestCase):
    def test_every_algorithm(self):
        self.assertEqual(registry.LOAD_ERRORS, {})
        algos = registry.algorithms()
        self.assertGreaterEqual(len(algos), 12)
        ids = [a["meta"]["id"] for a in algos]
        self.assertEqual(len(ids), len(set(ids)), "algoritm id lari takrorlanmasin")
        for a in algos:
            m = a["meta"]
            for key in REQUIRED:
                self.assertIn(key, m, f"{m['id']}: META['{key}'] yo'q")
            defaults = {f["id"]: f["default"] for f in m["inputs"]}
            out = run(m["id"], "enc", defaults)
            self.assertNotIn("error", out, f"{m['id']} standart qiymatlari xato beradi: {out}")
            self.assertTrue(out["steps"] and out["result"])
            for ex in m["examples"]:
                vals = {f["id"]: ex[i] for i, f in enumerate(m["inputs"]) if i < len(ex)}
                o = run(m["id"], "enc", vals)
                self.assertNotIn("error", o, f"{m['id']} misoli {ex} xato beradi: {o}")

    def test_tools(self):
        for t in registry.tools():
            self.assertIn(t["meta"]["kind"], ("table", "tasks", "quiz", "form"))
        practice = registry.get_tool("practice")["module"]
        for task in practice.handle("list", {})["tasks"]:
            ans = practice.handle("reveal", {"id": task["id"]})["answer"]
            self.assertFalse(ans.startswith("(xatolik"), f"{task['id']}: {ans}")
            self.assertTrue(practice.handle("check", {"id": task["id"], "answer": ans.lower()})["ok"])
        quiz = registry.get_tool("quiz")["module"]
        for i, q in enumerate(quiz.all_questions()):
            self.assertTrue(0 <= q["correct"] < len(q["opts"]), f"quiz #{i + 1}")
        self.assertEqual(len(registry.get_tool("compare")["module"].handle("load", {})["rows"]), len(registry.algorithms()))

    def test_calculator(self):
        calc = registry.get_tool("calculator")["module"]
        ok = calc.handle("run", {"section": "num", "vals": {"value": "255", "from": "10", "to": "2"}})["blocks"][0]
        self.assertEqual(ok["output"], "11111111")
        self.assertEqual(calc.handle("run", {"section": "num", "vals": {"value": "0", "from": "10", "to": "16"}})["blocks"][0]["output"], "0")
        t = calc.handle("run", {"section": "text", "vals": {"value": "Salom", "dir": "text2base", "base": "16", "sep": "space"}})["blocks"][0]
        self.assertEqual(t["value"], "53 61 6C 6F 6D")

    def test_api_handle(self):
        import json
        import api
        cat = json.loads(api.handle("GET", "/api/catalog"))
        self.assertEqual(len(cat["algorithms"]), 13)
        out = json.loads(api.handle("POST", "/api/algo/caesar/run", json.dumps({"mode": "enc", "vals": {"pt": "HELLO", "key": 3}})))
        self.assertEqual(out["result"], "KHOOR")
        for bad in ("[1]", "{xato", '{"mode":"enc","vals":[1]}'):
            self.assertIn("error", json.loads(api.handle("POST", "/api/algo/caesar/run", bad)))

    def test_manifest_fresh(self):
        import json
        import _build_manifest
        with open(os.path.join(ROOT, "manifest.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f), _build_manifest.build(),
                             "manifest.json eskirgan: python algoritmlar/_build_manifest.py ni ishga tushiring")

    def test_templates_work(self):
        for rel in ("algorithms/_template.py",):
            spec = importlib.util.spec_from_file_location("tpl", os.path.join(ROOT, rel))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.assertEqual(mod.run("enc", {"pt": "HELLO"})["result"], "URYYB")


if __name__ == "__main__":
    unittest.main()
