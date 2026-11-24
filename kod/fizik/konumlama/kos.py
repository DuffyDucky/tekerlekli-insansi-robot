"""konumlama testlerini tek komutla koşturur: `py -3 kod\\fizik\\konumlama\\kos.py` (numpy gerekir).

Seçenekler: -k METIN (yalnız adında geçenler), -v (ayrıntılı), --uzun (20 tohumlu benzer çift + MuJoCo kaydı
testleri; MuJoCo sanal ortamı ve kod/fizik/deneyler/koridor_karisiklik gerekir, yoksa atlanır). Sonda testlerin kaydettiği ölçümler (konum hatası,
yakınsama yolu, süre) tablo olarak yazılır. Çıkış kodu: 0 hepsi geçti, 1 kalan / hata.
"""

import argparse
import os
import sys
import time
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(BURASI)
sys.path.insert(0, FIZIK)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", default=None)
    ap.add_argument("-v", action="store_true")
    ap.add_argument("--uzun", action="store_true",
                    help="20 tohumlu benzer çift ve MuJoCo kaydı testleri (≈ 10 dk; MuJoCo + deney klasörü gerekir)")
    a = ap.parse_args()
    if a.uzun:
        os.environ["LALE_KONUM_UZUN"] = "1"
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    import numpy
    from konumlama.testler import ortak
    yukleyici = unittest.TestLoader()
    if a.k:
        yukleyici.testNamePatterns = ["*%s*" % a.k]
    suite = yukleyici.discover(os.path.join(BURASI, "testler"), pattern="test_*.py", top_level_dir=FIZIK)
    print("konumlama testleri | Python %s | numpy %s" % (sys.version.split()[0], numpy.__version__))
    bas = time.perf_counter()
    sonuc = unittest.TextTestRunner(verbosity=2 if a.v else 1, stream=sys.stdout).run(suite)
    sure = time.perf_counter() - bas
    if ortak.OLCUMLER:
        print("\nOLCUMLER")
        for test, ad, deger in ortak.OLCUMLER:
            print("  %-34s %-44s %s" % (test, ad, deger))
    kalan = len(sonuc.failures) + len(sonuc.errors)
    print("OZET: test %d | gecen %d | kalan %d | atlanan %d | sure %.1f s"
          % (sonuc.testsRun, sonuc.testsRun - kalan - len(sonuc.skipped), kalan, len(sonuc.skipped), sure))
    return 0 if sonuc.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
