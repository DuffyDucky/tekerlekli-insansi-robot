"""sanalray ortak kurulumu: modül yolları, düşük öncelik, tek iş parçacığı, ilerleme dosyası, çıktı klasörleri.

İçe aktarılınca yalnız `sys.path` ekler. `dusuk_oncelik()` ağır betiklerin başında, numpy / cv2 içe aktarılmadan önce
çağrılır (BELOW_NORMAL öncelik; OMP / OpenBLAS / MKL 1 iş parçacığı)."""

import os
import sys
import time

SANALRAY = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(SANALRAY)
KOD = os.path.dirname(FIZIK)
DEPO = os.path.dirname(KOD)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), FIZIK):
    if _y not in sys.path:
        sys.path.insert(0, _y)

SONUC = os.path.join(SANALRAY, "sonuc")
HAM = os.path.join(SONUC, "ham")
ONBELLEK = os.path.join(HAM, "onbellek")       # üretilen doku PNG'leri, kameralı model XML'i (git dışı)
GORSEL = os.path.join(SANALRAY, "gorsel")
PLANLAR = os.path.join(SANALRAY, "planlar")


def dusuk_oncelik():
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    if sys.platform == "win32":
        try:
            import ctypes
            k32 = ctypes.windll.kernel32
            k32.GetCurrentProcess.restype = ctypes.c_void_p
            k32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)
        except Exception:
            pass
    try:
        import cv2
        cv2.setNumThreads(1)
    except Exception:
        pass


def durum_yaz(satir):
    """İlerleme: kod/fizik/sanalray/.durum (git dışı)."""
    with open(os.path.join(SANALRAY, ".durum"), "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), satir))


def goreli(yol):
    """Çıktılara yazılacak yol: depo köküne göre (tam yerel yol yazılmaz)."""
    try:
        return os.path.relpath(yol, DEPO).replace("\\", "/")
    except ValueError:
        return os.path.basename(yol)
