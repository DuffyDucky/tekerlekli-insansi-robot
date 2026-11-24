"""Gezinme paketinin ortak kurulumu: modül yolları, düşük öncelik, iş parçacığı sınırı.

İçe aktarılınca yalnız `sys.path` ekler (yan etkisiz). `dusuk_oncelik()` ağır betiklerin başında çağrılır: Windows'ta
süreci BELOW_NORMAL önceliğe alır; OMP / OpenBLAS / MKL iş parçacığını 1'e sınırlar (numpy içe aktarılmadan ÖNCE
çağrılmalı ki etkili olsun)."""

import os
import sys

GEZINME = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(GEZINME)
KOD = os.path.dirname(FIZIK)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), FIZIK):
    if _y not in sys.path:
        sys.path.insert(0, _y)

ESKI_KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]


def dusuk_oncelik():
    for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ.setdefault(k, "1")
    if sys.platform == "win32":
        try:
            import ctypes
            k32 = ctypes.windll.kernel32
            # 64 bit Python'da tanıtıcı c_void_p olmalı; tanımsız bırakılınca çağrı 0 döner ve öncelik değişmez
            k32.GetCurrentProcess.restype = ctypes.c_void_p
            k32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)
        except Exception:
            pass


def durum_yaz(satir):
    """İlerleme: kod/fizik/gezinme/.durum (depoya girmez)."""
    import time
    with open(os.path.join(GEZINME, ".durum"), "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), satir))
