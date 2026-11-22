"""Y0s testlerini tek komutla koşturur: `py -3 kod/testler/kos.py`.

Seçenekler:
  --liste        testleri dayandıkları plan maddesiyle listele (koşmadan)
  -k METIN       yalnız adında METIN geçen testler
  -v             her testi ayrı satırda yaz
Hedef kart `LALE_HEDEF` ortam değişkeniyle (bellek | tcp | seri:PORT; ayrıntı testler/duzenek.py).
Çıkış kodu: 0 hepsi geçti, 1 kalan ya da hata var.
"""

import argparse
import os
import sys
import time
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(BURASI)
sys.path.insert(0, KOD)
import testler  # noqa: E402,F401  (yol kurulumu)


def _tum(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from _tum(t)
        else:
            yield t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--liste", action="store_true")
    ap.add_argument("-k", default=None)
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")    # Windows konsolu (cp1254) ok / ° gibi işaretlerde çökmesin
        except (AttributeError, ValueError):
            pass
    yukleyici = unittest.TestLoader()
    if a.k:
        yukleyici.testNamePatterns = ["*%s*" % a.k]
    suite = yukleyici.discover(BURASI, pattern="test_*.py", top_level_dir=KOD)
    def bilinen(t):
        return bool(getattr(sys.modules.get(type(t).__module__), "BILINEN_DAVRANIS", False))

    if a.liste:
        for t in _tum(suite):
            doc = (getattr(t, t._testMethodName).__doc__ or "").strip().splitlines()
            isaret = "[BİLİNEN DAVRANIŞ / TASARIM SORUSU; geçmesi sorunun var olduğunu gösterir] " if bilinen(t) else ""
            print("%s\n    %s%s" % (t.id().replace("testler.", ""), isaret, doc[0] if doc else "(dayanak yazılmamış)"))
        return 0
    n_bilinen = sum(1 for t in _tum(suite) if bilinen(t))
    hedef = os.environ.get("LALE_HEDEF", "bellek")
    print("Y0s testleri | hedef: %s | Python %s" % (hedef, sys.version.split()[0]))
    bas = time.perf_counter()
    sonuc = unittest.TextTestRunner(verbosity=2 if a.v else 1, stream=sys.stdout).run(suite)
    sure = time.perf_counter() - bas
    atlanan = len(sonuc.skipped)
    kalan = len(sonuc.failures) + len(sonuc.errors)
    print("OZET: test %d | gecen %d | kalan %d | atlanan %d | sure %.1f s"
          % (sonuc.testsRun, sonuc.testsRun - kalan - atlanan, kalan, atlanan, sure))
    if n_bilinen:
        print("      (bunların %d'i güvenlik testi değil, bilinen davranış / tasarım sorusu: test_tasarim_bulgulari)" % n_bilinen)
    return 0 if sonuc.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
