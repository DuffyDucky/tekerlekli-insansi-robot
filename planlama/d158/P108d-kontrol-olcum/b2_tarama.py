# P10.8d B2: tam carpisma taramasi surucusu. carpisma_kos.kos() ile ayni mantik (modulu ice aktarir; tek kosu kimligi, 9 bolum
# ayri freecadcmd sureclerinde sirayla, sonda birlestir()). Eski B'nin b_tarama.py'sinden; ekler:
#  - gunlukler ve durum depoda kalici klasorde (b2-log/, b2-tarama.durum): 20.11'de gecici klasor + yeniden baslatma isi kaybettirdi
#  - her bolum basi / bitisi saat damgasiyla .durum'a; her 60 s nabiz dosyasi (bolum, son ilerleme satiri, bos bellek)
#  - her bolumden once bos bellek >= 2,5 GB beklenir (en cok 30 dk); kilide bolum satiri yazilir
#  - izlenen kaynak dosyalarin md5 ozeti basta ve sonda karsilastirilir; bolum sonucu yoksa durur (karisik sonuc kabul edilmez)
# Kullanim (depo kokunden): py -3 -B -X utf8 planlama/d158/P108d-kontrol-olcum/b2_tarama.py
import os, sys, time, datetime, subprocess, ctypes, json, threading

BURASI = os.path.dirname(os.path.abspath(__file__))
R = os.path.normpath(os.path.join(BURASI, "..", "..", ".."))
HERE = os.path.join(R, "tasarim", "freecad")
sys.path.insert(0, HERE)
import carpisma_kos as CK

KILIT = os.path.join(R, "planlama", "d158", "FREECAD-KILIT.txt")
DURUM = os.path.join(BURASI, "b2-tarama.durum")
NABIZ = os.path.join(BURASI, "b2-tarama.nabiz")
LOGD = os.path.join(BURASI, "b2-log")
os.makedirs(LOGD, exist_ok=True)


class MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def bos_gb():
    m = MS(); m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2 ** 30


def simdi():
    return datetime.datetime.now().strftime("%H:%M:%S")


def yaz(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def durum(s):
    with open(DURUM, "a", encoding="utf-8") as f:
        f.write("%s %s\n" % (datetime.datetime.now().strftime("%d.%m %H:%M:%S"), s))
        f.flush()


AKTIF = {"bolum": None, "log": None, "bas": None}


def nabiz():
    while True:
        try:
            son = ""
            if AKTIF["log"] and os.path.exists(AKTIF["log"]):
                satir = [x.rstrip() for x in open(AKTIF["log"], encoding="utf-8", errors="replace") if x.strip()]
                son = satir[-1][:120] if satir else ""
            gecen = int(time.time() - AKTIF["bas"]) if AKTIF["bas"] else 0
            yaz(NABIZ, "%s | bolum %s | %d s | bos %.2f GB | son satir: %s\n" % (
                datetime.datetime.now().strftime("%d.%m %H:%M:%S"), AKTIF["bolum"], gecen, bos_gb(), son))
        except Exception as e:  # nabiz hatasi taramayi durdurmaz
            yaz(NABIZ, "%s nabiz hatasi %r\n" % (simdi(), e))
        time.sleep(60)


kosu = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
kaynak_bas = CK.kaynak_ozeti()
json.dump(kaynak_bas, open(os.path.join(BURASI, "b2-kaynak-bas.json"), "w", encoding="utf-8"), indent=1, sort_keys=True)
durum("SURUCU_BASLADI kosu %s pid %d bos %.2f GB izlenen %d dosya" % (kosu, os.getpid(), bos_gb(), len(kaynak_bas)))
print("[%s] kosu %s, bos bellek %.2f GB, kaynak %s" % (simdi(), kosu, bos_gb(), json.dumps(kaynak_bas)), flush=True)
threading.Thread(target=nabiz, daemon=True).start()
os.makedirs(CK.BOLUM_DIZIN, exist_ok=True)
ozet = []
for b in CK.BOLUMLER:
    w = 0
    while bos_gb() < 2.5 and w < 1800:
        time.sleep(30); w += 30
    if w:
        durum("%s bellek bekleme %d s (bos %.2f GB)" % (b, w, bos_gb()))
    yaz(KILIT, "P10.8d B2 (kontrol): tam carpisma taramasi, bolum %s, kosu %s, %s" % (
        b, kosu, datetime.datetime.now().strftime("%d.%m %H:%M")))
    env = dict(os.environ, FC_SCRIPT=os.path.join(HERE, "carpisma.py"), CARPISMA_BOLUM=b, CARPISMA_KOSU=kosu)
    log = os.path.join(LOGD, "carpisma-%s.log" % b)
    t = time.time()
    AKTIF.update(bolum=b, log=log, bas=t)
    durum("%s BASLADI (bos %.2f GB)" % (b, bos_gb()))
    print("[%s] %s basladi (gunluk %s, bos %.2f GB)" % (simdi(), b, log, bos_gb()), flush=True)
    with open(log, "w", encoding="utf-8", errors="replace") as f:
        rc = subprocess.call([CK.FC, CK.BASLATICI], env=env, stdout=f, stderr=subprocess.STDOUT, cwd=HERE)
    v = CK._oku(b)
    ok = v is not None and v.get("kosu") == kosu
    kaynak_ok = bool(v) and v.get("kaynak") == kaynak_bas
    ist = open(log, encoding="utf-8", errors="replace").read().count("Exception while processing")
    sure = round(time.time() - t)
    ozet.append(dict(bolum=b, rc=rc, ok=ok, kaynak_ok=kaynak_ok, istisna=ist, sure_s=sure,
                     tepe_bellek_mb=v and v.get("tepe_bellek_mb")))
    durum("%s BITTI rc %s sonuc %s kaynak_ayni %s istisna %d sure %d s tepe %s MB" % (
        b, rc, "yazildi" if ok else "YOK", kaynak_ok, ist, sure, v and v.get("tepe_bellek_mb")))
    print("[%s] %s bitti: rc %s, sonuc %s, kaynak ayni %s, istisna %d, %d s, tepe bellek %s MB" % (
        simdi(), b, rc, "yazildi" if ok else "YOK", kaynak_ok, ist, sure, v and v.get("tepe_bellek_mb")), flush=True)
    if not ok:
        durum("BOLUM SONUCU YOK (%s), durduruldu" % b)
        break
AKTIF.update(bolum="birlestir", log=None, bas=time.time())
tamam = len(ozet) == len(CK.BOLUMLER) and all(o["ok"] for o in ozet)
if tamam:
    out = CK.birlestir()
    durum("BIRLESTIRILDI tek_kosu %s toplam cakisma %s eklem_araliginda %s" % (
        out["tek_kosu"], out["toplam"]["cakisma"], out["toplam"]["eklem_araliginda"]))
kaynak_son = CK.kaynak_ozeti()
json.dump(kaynak_son, open(os.path.join(BURASI, "b2-kaynak-son.json"), "w", encoding="utf-8"), indent=1, sort_keys=True)
json.dump(dict(kosu=kosu, ozet=ozet, kaynak_bas_son_ayni=kaynak_bas == kaynak_son), open(os.path.join(BURASI, "b2-tarama-ozet.json"),
          "w", encoding="utf-8"), indent=1, ensure_ascii=False)
rc_son = 0 if tamam and kaynak_bas == kaynak_son and all(o["rc"] == 0 and o["istisna"] == 0 and o["kaynak_ok"] for o in ozet) else 1
yaz(KILIT, "P10.8d B2 (kontrol): tarama bitti %s, kontrol / regresyon / rapor (FreeCAD kosmuyor)" % datetime.datetime.now().strftime("%d.%m %H:%M"))
durum("KAYNAK bas=son %s" % (kaynak_bas == kaynak_son))
durum("SURUCU_BITTI rc %d" % rc_son)
print("[%s] OZET %s" % (simdi(), ozet), flush=True)
sys.exit(rc_son)
