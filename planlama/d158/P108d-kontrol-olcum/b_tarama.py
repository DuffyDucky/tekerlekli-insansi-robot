# P10.8d B: tam carpisma taramasi surucusu (carpisma_kos.kos() ile ayni mantik: tek kosu kimligi, 9 bolum sirayla, sonunda
# birlestir()); ek: her bolumden once bos bellek >= 2,5 GB beklenir, FreeCAD kilidine bolum satiri yazilir, .durum dosyasi tutulur.
import os, sys, time, datetime, subprocess, ctypes, json
R = sys.argv[1]
SS = sys.argv[2]
HERE = os.path.join(R, "tasarim", "freecad")
sys.path.insert(0, HERE)
import carpisma_kos as CK
KILIT = os.path.join(R, "planlama", "d158", "FREECAD-KILIT.txt")
DURUM = os.path.join(SS, "tarama.durum")
LOGD = os.path.join(SS, "tarama")
os.makedirs(LOGD, exist_ok=True)


class MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def bos_gb():
    m = MS(); m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2 ** 30


def yaz(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def simdi():
    return datetime.datetime.now().strftime("%H:%M:%S")


kosu = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
print("[%s] kosu %s, bos bellek %.2f GB, kaynak %s" % (simdi(), kosu, bos_gb(), json.dumps(CK.kaynak_ozeti())), flush=True)
os.makedirs(CK.BOLUM_DIZIN, exist_ok=True)
ozet = []
for b in CK.BOLUMLER:
    w = 0
    while bos_gb() < 2.5 and w < 1800:
        time.sleep(30); w += 30
    yaz(KILIT, "P10.8d B (kontrol): tam carpisma taramasi, bolum %s, kosu %s, 20.11 %s" % (b, kosu, simdi()[:5]))
    yaz(DURUM, "%s %s basladi (bos %.2f GB)\n" % (simdi(), b, bos_gb()))
    env = dict(os.environ, FC_SCRIPT=os.path.join(HERE, "carpisma.py"), CARPISMA_BOLUM=b, CARPISMA_KOSU=kosu)
    log = os.path.join(LOGD, "carpisma-%s.log" % b)
    t = time.time()
    print("[%s] %s basladi (gunluk %s, bos %.2f GB)" % (simdi(), b, log, bos_gb()), flush=True)
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        rc = subprocess.call([CK.FC, CK.BASLATICI], env=env, stdout=f, stderr=subprocess.STDOUT, cwd=HERE)
    v = CK._oku(b)
    ok = v is not None and v.get("kosu") == kosu
    ist = open(log, encoding="utf-8", errors="replace").read().count("Exception while processing")
    ozet.append((b, rc, ok, round(time.time() - t), v and v.get("tepe_bellek_mb"), ist))
    print("[%s] %s bitti: rc %s, sonuc %s, istisna %d, %d s, tepe bellek %s MB" % (
        simdi(), b, rc, "yazildi" if ok else "YOK", ist, time.time() - t, v and v.get("tepe_bellek_mb")), flush=True)
    with open(DURUM, "a", encoding="utf-8") as f:
        f.write("%s %s bitti rc %s ok %s\n" % (simdi(), b, rc, ok))
    if not ok:
        print("BOLUM SONUCU YOK, durduruldu", flush=True)
        break
if len(ozet) == len(CK.BOLUMLER) and all(o[2] for o in ozet):
    CK.birlestir()
yaz(KILIT, "boş")
print("[%s] OZET %s" % (simdi(), ozet), flush=True)
sys.exit(0 if all(o[2] and o[1] == 0 and o[5] == 0 for o in ozet) and len(ozet) == len(CK.BOLUMLER) else 1)
