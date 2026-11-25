"""Keşif paketinin ortak kurulumu: modül yolları, düşük öncelik, iş parçacığı sınırı, ilerleme dosyası.

İçe aktarılınca yalnız `sys.path` ekler. `dusuk_oncelik()` ağır betiklerin başında, numpy içe aktarılmadan ÖNCE
çağrılır: OMP / OpenBLAS / MKL iş parçacığını 1'e sınırlar, Windows'ta süreci BELOW_NORMAL önceliğe alır."""

import os
import sys

KESIF = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(KESIF)
KOD = os.path.dirname(FIZIK)
HARITALAR = os.path.join(KOD, "araclar", "haritalar")
SAHNELER = os.path.join(FIZIK, "sahneler")
for _y in (FIZIK,):
    if _y not in sys.path:
        sys.path.insert(0, _y)


def dusuk_oncelik():
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[k] = "1"
    if sys.platform == "win32":
        try:
            import ctypes
            k32 = ctypes.windll.kernel32
            k32.GetCurrentProcess.restype = ctypes.c_void_p          # 64 bit'te tanıtıcı kırpılmasın
            k32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)    # BELOW_NORMAL
        except Exception:
            pass


def durum_yaz(satir):
    """İlerleme: kod/fizik/kesif/.durum (depoya girmez)."""
    import time
    with open(os.path.join(KESIF, ".durum"), "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), satir))
