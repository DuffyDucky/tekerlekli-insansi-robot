"""Y0f: fizik testleri + Y0s testleri fizik dünyasında + ölçümler, tek komut.

    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/kos_fizik.py            # (LALE_SIM_VENV yoksa %LOCALAPPDATA%\\lale-sim-venv)
    ... kos_fizik.py --olcum-yok                                            # ölçümsüz (≈ 30 s)
    ... kos_fizik.py --cikti <klasör>                                       # ölçüm çıktısı başka yere

Üç bölüm:
  1. kod/fizik/testler/test_*.py (model - CAD, el hesabı, protokol üstünden fizik, belirlenimcilik)
  2. Y0s'un 58 testi `LALE_HEDEF=fizik` ile (kod/testler/kos.py, ayrı süreç). Fiziğin 2B ideal dünyadan BİLEREK farklı
     olduğu yerler doğrulama düzeyinde `kod/testler/duzenek.py` FIZIK_FARKLARI'nda; 58 testin hepsi geçmeli, her kalan
     çıkış 1 (yalnız görünüm testi `test_yalniz_ayni_koken` bir kez yeniden denenir).
  3. olcumler.py (planlama/d158/Y0f-olcum/olcum.json + .md); sayıların özeti (süreler hariç) SHA-256 ile yazılır, üç koşu
     aynı özeti vermeli.
mujoco kurulu değilse: "atlandı" yazar, çıkış 0 (2B simülasyon ve 58 test bundan etkilenmez).
Çıkış: 0 = hepsi beklendiği gibi, 1 = fark var.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(BURASI)
KOK = os.path.dirname(KOD)
sys.path.insert(0, BURASI)
import dunya as D  # noqa: E402

# Fizik 2B'den bilerek farklı olduğu yerde muafiyet TEST düzeyinde değil DOĞRULAMA düzeyinde: kod/testler/duzenek.py
# FIZIK_FARKLARI (anında durma -> sürücü komutu kesik + pay içinde durma, 6 basamak hız eşitliği -> ±0,01 m/s, ...).
# Testin öbür doğrulamaları (bekçi tetiklenmesi, kilit, reset, olay iletileri) fizikte de koşar; Y0s'un 58 testinin
# hepsi fizikte de geçmeli. Test düzeyinde muafiyet yok.
BEKLENEN_FARK = {}
# Yalnız bu test kalırsa bir kez tek başına yeniden koşulur: gerçek zamanlı (duvar saatli) HTTP görünüm testi, yük altında
# zaman aşımı (Y0f-gunluk § 6, Y0f-kontrol § 6; fizikten bağımsız). Başka hiçbir kalan yeniden denenmez.
KARARSIZ_ADAY = {"test_yalniz_ayni_koken"}


def bolum1():
    yukleyici = unittest.TestLoader()
    suite = yukleyici.discover(os.path.join(BURASI, "testler"), pattern="test_*.py",
                               top_level_dir=os.path.join(BURASI, "testler"))
    bas = time.perf_counter()
    r = unittest.TextTestRunner(verbosity=1, stream=sys.stdout).run(suite)
    kalan = len(r.failures) + len(r.errors)
    print("OZET fizik testleri: test %d | gecen %d | kalan %d | atlanan %d | sure %.1f s"
          % (r.testsRun, r.testsRun - kalan - len(r.skipped), kalan, len(r.skipped), time.perf_counter() - bas))
    return kalan == 0


def bolum2():
    env = dict(os.environ, LALE_HEDEF="fizik", PYTHONIOENCODING="utf-8")
    bas = time.perf_counter()
    p = subprocess.run([sys.executable, os.path.join(KOD, "testler", "kos.py")], env=env, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    cikti = p.stdout + p.stderr
    kalan = set(re.findall(r"^(?:FAIL|ERROR): (\w+) ", cikti, flags=re.M))
    ozet = [s for s in cikti.splitlines() if s.startswith("OZET")]
    print("Y0s testleri fizikte: %s (%.1f s)" % (ozet[0] if ozet else "OZET yok", time.perf_counter() - bas))
    beklenen = set(BEKLENEN_FARK)
    yeni = sorted(kalan - beklenen)
    # KARARSIZ_ADAY'daki test kalırsa tek başına bir kez daha koşulur; geçerse "kararsız" yazılır. Öbür kalanlar bozar.
    for t in [t for t in yeni if t in KARARSIZ_ADAY]:
        q = subprocess.run([sys.executable, os.path.join(KOD, "testler", "kos.py"), "-k", t], env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        if q.returncode == 0:
            print("  KARARSIZ (tek başına yeniden koşuda geçti) %s" % t)
            yeni.remove(t)
    gecen_beklenen = sorted(beklenen - kalan)
    for t in sorted(kalan & beklenen):
        print("  beklenen fark  %-58s %s" % (t, BEKLENEN_FARK[t]))
    for t in yeni:
        print("  YENİ KALAN     %s" % t)
    for t in gecen_beklenen:
        print("  BEKLENEN FARK GEÇTİ (listeyi güncelle) %s" % t)
    if KOD not in sys.path:
        sys.path.insert(0, KOD)
    import testler.duzenek as Z  # noqa: E402  (doğrulama düzeyindeki farkların listesi)
    for ad, neden in sorted(Z.FIZIK_FARKLARI.items()):
        print("  doğrulama farkı %-14s %s" % (ad, neden))
    for t in yeni:
        i = cikti.find("FAIL: %s " % t)
        if i < 0:
            i = cikti.find("ERROR: %s " % t)
        print(cikti[i:i + 1200])
    if not ozet:
        print(cikti[-3000:])
        return False
    return not yeni and not gecen_beklenen


def bolum3(cikti):
    bas = time.perf_counter()
    p = subprocess.run([sys.executable, os.path.join(BURASI, "olcumler.py"), "--cikti", cikti],
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print(p.stdout[-2000:] + p.stderr[-3000:])
        return False
    with open(os.path.join(cikti, "olcum.json"), encoding="utf-8") as f:
        o = json.load(f)
    o.pop("_sure_s", None)
    ozet = hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]
    print("Ölçümler: %s (%.1f s) | sayı özeti (SHA-256, süreler hariç) %s"
          % (os.path.relpath(os.path.join(cikti, "olcum.json"), KOK), time.perf_counter() - bas, ozet))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--olcum-yok", action="store_true")
    ap.add_argument("--cikti", default=os.path.join(KOK, "planlama", "d158", "Y0f-olcum"))
    a = ap.parse_args()
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    print("Y0f fizik koşusu | Python %s" % sys.version.split()[0])
    if not D.FIZIK_VAR:
        print("fizik bağımlılığı (mujoco) yok: fizik testleri ve ölçümler ATLANDI (%s)." % D.FIZIK_HATA)
        print("Kurulum: kod/SIMULASYON.md 'Fizik simülasyonu (Y0f)'. 2B simülasyon ve 58 test bundan etkilenmez.")
        return 0
    import mujoco
    print("MuJoCo %s" % mujoco.__version__)
    bas = time.perf_counter()
    ok = bolum1()
    ok = bolum2() and ok
    if not a.olcum_yok:
        ok = bolum3(a.cikti) and ok
    print("SONUÇ: %s | toplam %.1f s" % ("beklendiği gibi" if ok else "FARK VAR", time.perf_counter() - bas))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
