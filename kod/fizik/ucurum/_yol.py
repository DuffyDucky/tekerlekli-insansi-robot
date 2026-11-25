"""ucurum paketinin ortak kurulumu: modül yolları, düşük öncelik, iş parçacığı sınırı, ilerleme dosyası.

İçe aktarılınca yalnız `sys.path` ekler. `dusuk_oncelik()` ağır betiklerin başında (numpy içe aktarılmadan ÖNCE)
çağrılır: OMP / OpenBLAS / MKL 1 iş parçacığı, Windows'ta BELOW_NORMAL öncelik."""

import os
import sys
import time

UCURUM = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(UCURUM)
KOD = os.path.dirname(FIZIK)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), FIZIK):
    if _y not in sys.path:
        sys.path.insert(0, _y)

SONUC = os.path.join(UCURUM, "sonuc")
HAM = os.path.join(SONUC, "ham")
GORSEL = os.path.join(UCURUM, "gorsel")


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


def durum_yaz(satir):
    """İlerleme: kod/fizik/ucurum/.durum (depoya girmez)."""
    with open(os.path.join(UCURUM, ".durum"), "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), satir))
