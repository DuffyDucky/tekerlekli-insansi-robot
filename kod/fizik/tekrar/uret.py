"""Labirent keşif koşularını tarayıcıda tekrar oynatan tek dosyalık HTML raporu üretir.

    py -3 kod\\fizik\\tekrar\\uret.py                 # -> kod/fizik/tekrar/labirent-rapor.html
    py -3 kod\\fizik\\tekrar\\uret.py --lidar-hz 1     # LiDAR'ı daha da seyrelt (boyut)

Yalnız OKUR: kod/fizik/kesif/sonuc/*.csv, kesif/sonuc/ham/mujoco/*.npz (gezinme.duzenek.Kayit), sahne ve harita
JSON'ları, gezinme/kayit/*.npz (koridor). Hiçbir girdiyi değiştirmez. O anda diskte ne varsa onunla çalışır: yazılmakta
olan (son 20 s içinde değişmiş) ya da okunamayan kayıt atlanır ve raporda yazılır. Tek süreç, tek iş parçacığı,
düşük öncelik. Ayrıntı: BENIOKU.md.
"""

import os
import sys

sys.dont_write_bytecode = True          # başka klasörlere (labirent/__pycache__) .pyc yazma
for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_k] = "1"

import argparse
import base64
import csv
import datetime
import glob
import json
import math
import re
import statistics
import time
import zlib

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(BURASI)
KOD = os.path.dirname(FIZIK)
KESIF = os.path.join(FIZIK, "kesif")
SONUC = os.path.join(KESIF, "sonuc")
HAM_MJ = os.path.join(SONUC, "ham", "mujoco")
SAHNELER = os.path.join(FIZIK, "sahneler")
HARITALAR = os.path.join(KOD, "araclar", "haritalar")
GEZ_KAYIT = os.path.join(FIZIK, "gezinme", "kayit")
GEZ_HAM = os.path.join(FIZIK, "gezinme", "sonuc", "ham")
SABLON = os.path.join(BURASI, "sablon.html")
CIKTI = os.path.join(BURASI, "labirent-rapor.html")
DURUM = os.path.join(BURASI, ".durum")

T_SINIR = 900.0
POZ_HZ = 10.0
HARITA_COZ = 0.10
TAZE_S = 20.0            # bu kadar yeni değişmiş kayıt yazılıyor olabilir: atla

MOD_AD = {"": "-", "bos": "boşta", "kesif": "keşif", "izle": "yol izleme", "yerinde": "yerinde dönüş", "bekle": "bekleme",
          "bitti": "bitti", "planla": "planlama", "kayip": "kayıp", "baslangic": "başlangıç", "konumlan": "konumlanma",
          "cikis": "çıkışa gidiş", "hafiza": "hafıza", "kurtarma": "kurtarma", "bak": "etrafa bakış",
          "duvar_izle": "duvar izleme", "tukendi": "sınır tükendi"}
STRATEJI_AD = {"kesif": "keşif (haritalı)", "sag_duvar": "sağ duvar", "rastgele": "rastgele"}
DURUM_AD = {"basari": "başarı", "fail_sure": "süre doldu", "fail_sikisma": "sıkıştı", "fail_start": "START'tan çıktı",
            "hata": "koşu hatası"}


# ------------------------------------------------------------------ yardımcılar
def dusuk_oncelik():
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000)     # BELOW_NORMAL
        except Exception:
            pass
    else:
        try:
            os.nice(10)
        except Exception:
            pass


def durum_yaz(msg):
    satir = "%s %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(satir, flush=True)
    try:
        with open(DURUM, "a", encoding="utf-8") as f:
            f.write(satir + "\n")
    except OSError:
        pass


def fnum(x, nd=1):
    """Türkçe ondalık virgül."""
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "-"
    s = ("%." + str(nd) + "f") % x
    return s.replace(".", ",")


def fsure(s):
    if s is None or not math.isfinite(s):
        return "-"
    s = int(round(s))
    return "%d:%02d" % (s // 60, s % 60)


def ffloat(v):
    try:
        x = float(v)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def boyut_of(sahne):
    m = re.search(r"(\d+)x(\d+)", sahne or "")
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def boyut_ad(b):
    return "%d×%d" % b


def ek(n, tur):
    """Sayının okunuşuna göre kesme işaretli ek: tur 'e' (yönelme) ya da 'de' (bulunma). 9 -> 'a / 'da."""
    son = n % 10 if n % 10 else (n % 100 // 10 * 10 if n % 100 else 100)
    yon = {0: "'a", 1: "'e", 2: "'ye", 3: "'e", 4: "'e", 5: "'e", 6: "'ya", 7: "'ye", 8: "'e", 9: "'a",
           10: "'a", 20: "'ye", 30: "'a", 40: "'a", 50: "'ye", 60: "'a", 70: "'e", 80: "'e", 90: "'a", 100: "'e"}
    bul = {0: "'da", 1: "'de", 2: "'de", 3: "'te", 4: "'te", 5: "'te", 6: "'da", 7: "'de", 8: "'de", 9: "'da",
           10: "'da", 20: "'de", 30: "'da", 40: "'ta", 50: "'de", 60: "'ta", 70: "'te", 80: "'de", 90: "'da", 100: "'de"}
    return (yon if tur == "e" else bul).get(son, "'")


def csv_oku(ad):
    yol = os.path.join(SONUC, ad)
    if not os.path.exists(yol):
        return None, None
    try:
        with open(yol, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:      # yazılırken okunmuş olabilir
        durum_yaz("UYARI %s okunamadi: %s" % (ad, e))
        return None, None
    return rows, os.path.getmtime(yol)


def tekille(rows, anahtar):
    """Ekleme kipinde yazılan CSV'de aynı koşu birden çok kez olabilir: sonuncusu geçerli."""
    d = {}
    for r in rows or []:
        if not r.get("sahne"):
            continue
        d[tuple(r.get(k, "") for k in anahtar)] = r
    return list(d.values())


_SURUM_ANAHTAR = ("surum_etiket", "beyin_surum", "surum_beyin", "beyin_surumu", "etiket", "versiyon", "surum")


def surum_norm(v):
    if v is None:
        return None
    s = str(v).strip().lower()
    m = re.match(r"^v?(\d+)$", s)
    return ("v%s" % m.group(1)) if m else (s or None)


def surum_yoldan(yol):
    """Dosya ya da klasör adındaki sürüm etiketi (…_v2.npz, mujoco_v2/, mujoco_v2.csv); yoksa None."""
    m = re.findall(r"(?:^|[_\-./\\])v(\d+)(?=[_\-./\\]|$)", yol.replace("\\", "/"))
    return ("v%s" % m[-1]) if m else None


def surum_bul(satir=None, meta=None, yol=None):
    """Sürüm etiketi: CSV sütunu > kayıt meta alanı > dosya/klasör adı > 'v1'. Kayıt meta'sındaki 'surum' kayıt
    biçiminin sürümüdür (beyin değil), o yüzden meta'da yalnız açık beyin sürümü anahtarlarına bakılır."""
    for k in _SURUM_ANAHTAR:
        if satir and satir.get(k) not in (None, ""):
            return surum_norm(satir[k])
    for k in _SURUM_ANAHTAR[:-1]:
        if meta and meta.get(k) not in (None, ""):
            return surum_norm(meta[k])
    return (surum_yoldan(yol) if yol else None) or "v1"


KUME_AD = {"sinama": "sınama", "gelistirme": "geliştirme", "uzatilmis": "uzatılmış"}
KUME_SIRA = {"sinama": 0, "gelistirme": 1, "uzatilmis": 2}
KOS_AD = {"ilk": "ilk koşu", "hafiza": "hafızalı koşu"}


def kume_bul(sahne, satir=None, meta=None, yol=None):
    """Küme anahtarı (sinama / gelistirme / uzatilmis): açık 'kume' alanı > yoldaki ad > labirent tohumu (t1–t3
    geliştirme, beyin bunlarla ayarlandı; t4+ sınama)."""
    for src in (satir or {}, meta or {}):
        v = str(src.get("kume") or src.get("küme") or "").strip().lower()
        if v:
            if v.startswith(("sin", "sın", "test")):
                return "sinama"
            if v.startswith(("gel", "dev")):
                return "gelistirme"
            if v.startswith("uza"):
                return "uzatilmis"
            return v
    y = (yol or "").replace("\\", "/").lower()
    for k in ("uzatilmis", "sinama"):
        if k in y:
            return k
    m = re.search(r"_t(\d+)$", sahne or "")
    return "sinama" if (m and int(m.group(1)) >= 4) else "gelistirme"


def kos_bul(satir=None, meta=None, yol=None):
    for src in (satir or {}, meta or {}):
        v = str(src.get("kos") or "").strip().lower()
        if v:
            return "hafiza" if v.startswith("haf") else "ilk"
    return "hafiza" if "_hafiza" in os.path.basename(yol or "") else "ilk"


def kume_T(kume):
    return 2 * T_SINIR if kume == "uzatilmis" else T_SINIR


def ortanca(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


# ------------------------------------------------------------------ sahneler
_SAHNE_ON = {}


def sahne_bilgisi(ad):
    """Gerçek dünya (izleyici için; beyin bunu görmez): duvarlar, START/FINISH, çözüm yolu."""
    if ad in _SAHNE_ON:
        return _SAHNE_ON[ad]
    s3 = json.load(open(os.path.join(SAHNELER, ad + ".json"), encoding="utf-8"))
    h2 = json.load(open(os.path.join(HARITALAR, s3.get("harita", ad) + ".json"), encoding="utf-8"))
    duv = [[round(float(v), 3) for v in d[:4]] for d in h2.get("duvarlar", [])]
    L = s3.get("labirent") or {}
    b = {"ad": ad, "duvarlar": duv, "boyut_m": h2.get("boyut_m"), "engeller": h2.get("engeller", [])}
    if L:
        b.update(labirent=True, satir=L["satir"], sutun=L["sutun"], hucre_m=L["hucre_m"], sinir=L["sinir"],
                 start=L["start"]["cizgi"], start_normal=L["start"]["ic_normal"], start_poz=L["start"]["poz"],
                 finish=L["finish"]["cizgi"], finish_normal=L["finish"]["ic_normal"],
                 cozum=[[round(p[0], 2), round(p[1], 2)] for p in L.get("cozum_yolu", [])],
                 cozum_m=L.get("cozum_uzunlugu_m"))
    else:
        bb = h2.get("baslangic") or s3.get("baslangic") or {}
        b.update(labirent=False, start_poz=[bb.get("x", 0), bb.get("y", 0), math.radians(bb.get("aci_derece", 0))])
        xs = [v for d in duv for v in (d[0], d[2])]
        ys = [v for d in duv for v in (d[1], d[3])]
        b["sinir"] = [min(xs), min(ys), max(xs), max(ys)] if xs else [0, 0] + list(h2.get("boyut_m", [10, 10]))
    _SAHNE_ON[ad] = b
    return b


# ------------------------------------------------------------------ paketleme
class Paket:
    """Tipli dizileri 4 bayt hizalı tek tampona dizer; başlık JSON'u ayrı (sıkıştırılmaz)."""

    def __init__(self):
        self.parcalar, self.baslik, self.n = [], {}, 0

    def ekle(self, ad, dizi, fark=False, olcek=1.0):
        a = np.ascontiguousarray(dizi)
        if a.dtype.kind == "f":
            raise TypeError(ad)
        if fark and a.size:
            a = a.astype(np.int64)
            d = np.empty_like(a)
            d[0] = a[0]
            d[1:] = a[1:] - a[:-1]
            a = d.astype(np.int32)
        tip = {np.dtype(np.int32): "i4", np.dtype(np.uint8): "u1", np.dtype(np.uint16): "u2",
               np.dtype(np.int16): "i2"}[a.dtype]
        b = a.astype(a.dtype.newbyteorder("<")).tobytes()
        self.baslik[ad] = {"t": tip, "o": self.n, "n": int(a.size), "f": 1 if fark else 0, "s": olcek}
        self.parcalar.append(b)
        self.n += len(b)
        pad = (-self.n) % 4
        if pad:
            self.parcalar.append(b"\0" * pad)
            self.n += pad

    def bayt(self):
        ham = b"".join(self.parcalar)
        return ham, zlib.compress(ham, 9)


def q(x, olcek):
    return np.round(np.asarray(x, dtype=float) * olcek).astype(np.int64)


def nan_doldur(a):
    """NaN'leri önceki geçerli değerle (yoksa 0) doldur; geçerlilik maskesi döner."""
    a = np.array(a, dtype=float)
    ok = np.isfinite(a)
    if a.ndim == 2:
        ok = ok.all(axis=1)
    son = np.zeros(a.shape[1:]) if a.ndim == 2 else 0.0
    for i in range(len(a)):
        if ok[i]:
            son = a[i]
        else:
            a[i] = son
    return a, ok


def baslangictan_dunyaya(start, x, y):
    sx, sy, sth = start
    c, s = math.cos(sth), math.sin(sth)
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return sx + c * x - s * y, sy + s * x + c * y


# ------------------------------------------------------------------ harita anlık görüntüleri
def harita_kodla(z, meta, cerceve_dunya, paket):
    """5 cm log-odds anlık görüntüler -> ortak 10 cm çerçeve, 0 bilinmeyen / 1 boş / 2 dolu; XOR farkları."""
    H = meta.get("haritalar") or []
    if not H:
        return None
    coz = float(H[0]["cozunurluk_m"])
    f = max(1, int(round(HARITA_COZ / coz)))
    kutular = []
    for h in H:
        sh = z[h["anahtar"]].shape          # (ny, nx), satır = y
        x0, y0 = h["orijin"]
        kutular.append((x0, y0, x0 + sh[1] * coz, y0 + sh[0] * coz))
    X0 = min(k[0] for k in kutular)
    Y0 = min(k[1] for k in kutular)
    X1 = max(k[2] for k in kutular)
    Y1 = max(k[3] for k in kutular)
    nx5 = int(math.ceil(round((X1 - X0) / coz, 6) / f)) * f
    ny5 = int(math.ceil(round((Y1 - Y0) / coz, 6) / f)) * f
    nx, ny = nx5 // f, ny5 // f
    onceki = np.zeros(ny * nx, np.uint8)
    zaman, sayi, idx_l, val_l = [], [], [], []
    hizasiz = 0
    for h in H:
        iz = z[h["anahtar"]]
        tam = np.full((ny5, nx5), -1, np.int16)
        i0 = int(round((h["orijin"][0] - X0) / coz))
        j0 = int(round((h["orijin"][1] - Y0) / coz))
        tam[j0:j0 + iz.shape[0], i0:i0 + iz.shape[1]] = iz
        if i0 % f or j0 % f:
            hizasiz += 1
        a = tam.reshape(ny, f, nx, f)
        dolu = (a >= 50).any(axis=(1, 3))
        bos = ((a >= 0) & (a < 50)).any(axis=(1, 3))
        kod = np.zeros((ny, nx), np.uint8)
        kod[bos] = 1
        kod[dolu] = 2
        kod = kod.ravel()
        d = np.flatnonzero(kod != onceki).astype(np.int64)
        zaman.append(float(h["t"]))
        sayi.append(len(d))
        if len(d):
            fd = np.empty_like(d)
            fd[0] = d[0]
            fd[1:] = d[1:] - d[:-1]
            idx_l.append(fd)
            val_l.append((kod[d] ^ onceki[d]).astype(np.uint8))
        onceki = kod
    paket.ekle("h_t", q(zaman, 1000), fark=True, olcek=0.001)
    paket.ekle("h_n", np.array(sayi, np.int32))
    paket.ekle("h_i", (np.concatenate(idx_l) if idx_l else np.zeros(0, np.int64)).astype(np.int32))
    paket.ekle("h_v", np.concatenate(val_l) if val_l else np.zeros(0, np.uint8))
    son = onceki.reshape(ny, nx)
    return {"x0": X0, "y0": Y0, "nx": nx, "ny": ny, "coz": coz * f, "adet": len(H), "cerceve": cerceve_dunya,
            "hizasiz": hizasiz, "son_dolu": int((son == 2).sum()), "son_bos": int((son == 1).sum())}


# ------------------------------------------------------------------ hakem yeniden oynatma
_HAKEM = None


def hakem_sinifi():
    global _HAKEM
    if _HAKEM is None:
        sys.path.insert(0, os.path.join(FIZIK, "labirent"))
        from hakem import Hakem
        _HAKEM = Hakem
    return _HAKEM


def hakem_oynat(ad, t, g, temas, T=T_SINIR):
    """Kayıttaki yer gerçeğiyle hakemi yeniden koştur: adım adım p_en, çarpma, gezilen hücre (anlık puan için)."""
    H = hakem_sinifi()(ad, sure_siniri_s=T)
    n = len(t)
    pen = np.zeros(n)
    carp = np.zeros(n, np.int32)
    cs = np.zeros(n)
    hucre = np.zeros(n, np.int32)
    son = n
    for i in range(n):
        H.guncelle(float(t[i]), (float(g[i, 0]), float(g[i, 1]), float(g[i, 2])), bool(temas[i]))
        pen[i], carp[i], cs[i], hucre[i] = H.p_en, H.carpma_sayisi, H.carpma_suresi_s, len(H.ziyaret)
        if H.bitti:
            son = i + 1
            pen[son:], carp[son:], cs[son:], hucre[son:] = pen[i], carp[i], cs[i], hucre[i]
            break
    return H.sonuc, pen, carp, cs, hucre


# ------------------------------------------------------------------ olay ayrıştırma
def beyin_olaylari(s):
    out = []
    for p in (s or "").split(";"):
        p = p.strip()
        m = re.match(r"^([0-9.]+):(.+)$", p)
        if m:
            out.append([round(float(m.group(1)), 1), m.group(2)])
    return out


# ------------------------------------------------------------------ tek kayıt
def kayit_isle(yol, tur, csv_tablo, lidar_adim_s, isin_adim, tani):
    with np.load(yol, allow_pickle=False) as zz:
        z = {k: zz[k] for k in zz.files}
    meta = json.loads(str(z.pop("meta")))
    ad = meta["sahne"]
    sb = sahne_bilgisi(ad)
    goreli = os.path.relpath(yol, os.path.join(SONUC, "ham")) if tur == "labirent" else os.path.basename(yol)
    surum = surum_bul(meta=meta, yol=goreli)
    kume = kume_bul(ad, meta=meta, yol=goreli) if tur == "labirent" else None
    kos = kos_bul(meta=meta, yol=goreli) if tur == "labirent" else None
    T = kume_T(kume)
    csv_satir = None
    if csv_tablo is not None:
        csv_satir = csv_tablo.get((surum, kume, kos, ad, str(meta.get("tohum"))))
        if csv_satir is None:            # 'kayit' sütunu (tam ya da göreli yol) dosya yoluyla eşleşiyorsa
            gy = goreli.replace("\\", "/")
            for r in csv_tablo.values():
                kr = (r.get("kayit") or "").replace("\\", "/")
                if kr and (kr.endswith("/" + gy) or kr == gy):
                    csv_satir = r
                    break
    start = tuple(float(v) for v in (meta.get("baslangic") or sb["start_poz"]))
    if sb.get("labirent"):
        sp = sb["start_poz"]
        fark = math.hypot(sp[0] - start[0], sp[1] - start[1])
        if fark > 0.02 or abs(math.remainder(sp[2] - start[2], 2 * math.pi)) > 0.01:
            tani.append("%s: kayıttaki başlangıç sahne START pozundan farklı (%.3f m)" % (os.path.basename(yol), fark))
    t = z["t"].astype(float)
    g = z["gercek"].astype(float)
    tah = z["tahmin"].astype(float)
    hed = z["hedef"].astype(float)
    temas = z["temas"].astype(np.uint8)
    mod = z["mod"].astype(np.int32)
    modlar = meta.get("modlar") or []
    ek0 = ((meta.get("ekler") or [{}])[0] or {}).get("ek") or {}
    cerceve_bas = (ek0.get("cerceve") == "baslangic") if tur == "labirent" else False
    # beyin çerçevesi -> dünya
    if cerceve_bas:
        tx, ty = baslangictan_dunyaya(start, tah[:, 0], tah[:, 1])
        tth = tah[:, 2] + start[2]
        hx, hy = baslangictan_dunyaya(start, hed[:, 0], hed[:, 1])
    else:
        tx, ty, tth = tah[:, 0], tah[:, 1], tah[:, 2]
        hx, hy = hed[:, 0], hed[:, 1]
    T_ = np.stack([tx, ty, tth], 1)
    T_, tah_ok = nan_doldur(T_)
    Hh, hed_ok = nan_doldur(np.stack([hx, hy], 1))
    # ilk karede robot ile hayalet üst üste mi
    i_ok = np.flatnonzero(tah_ok)
    ilk_fark = float(math.hypot(T_[i_ok[0], 0] - g[i_ok[0], 0], T_[i_ok[0], 1] - g[i_ok[0], 1])) if len(i_ok) else None
    e_all = np.hypot(T_[:, 0] - g[:, 0], T_[:, 1] - g[:, 1])
    e_all[~tah_ok] = np.nan
    # hakem
    hs_kayit = (meta.get("sonuc") or {}).get("hakem") or {}
    if tur == "labirent":
        hs, pen, carp, cs, hucre = hakem_oynat(ad, t, g, temas, T)
    else:
        hs, pen, carp, cs, hucre = {}, np.zeros(len(t)), np.zeros(len(t), np.int32), np.zeros(len(t)), np.zeros(len(t), np.int32)
        k = 0
        onceki = False
        for i in range(len(t)):          # koridor: çarpma = temas başlangıcı (1 s birleştirme yok, yalnız gösterim)
            if temas[i] and not onceki:
                k += 1
            onceki = bool(temas[i])
            carp[i] = k
    # yol (gövde merkezi)
    adim = np.hypot(np.diff(g[:, 0]), np.diff(g[:, 1]))
    yol_m = np.concatenate([[0.0], np.cumsum(adim)])
    # seyreltme: 10 Hz (çarpma bayrağı pencerede en büyük)
    dt = float(np.median(np.diff(t))) if len(t) > 1 else 0.05
    s = max(1, int(round(1.0 / (POZ_HZ * dt))))
    sec = np.arange(0, len(t), s)
    if sec[-1] != len(t) - 1:
        sec = np.append(sec, len(t) - 1)
    tem_s = np.array([temas[a:b].max() if b > a else temas[a] for a, b in zip(sec, np.append(sec[1:], len(t)))], np.uint8)
    P = Paket()
    P.ekle("t", q(t[sec], 1000), fark=True, olcek=0.001)
    P.ekle("gx", q(g[sec, 0], 1000), fark=True, olcek=0.001)
    P.ekle("gy", q(g[sec, 1], 1000), fark=True, olcek=0.001)
    P.ekle("gth", q(np.unwrap(g[sec, 2]), 1000), fark=True, olcek=0.001)
    P.ekle("tx", q(T_[sec, 0], 1000), fark=True, olcek=0.001)
    P.ekle("ty", q(T_[sec, 1], 1000), fark=True, olcek=0.001)
    P.ekle("tth", q(np.unwrap(T_[sec, 2]), 1000), fark=True, olcek=0.001)
    P.ekle("tok", tah_ok[sec].astype(np.uint8))
    P.ekle("hx", q(Hh[sec, 0], 100), fark=True, olcek=0.01)
    P.ekle("hy", q(Hh[sec, 1], 100), fark=True, olcek=0.01)
    P.ekle("hok", hed_ok[sec].astype(np.uint8))
    P.ekle("yol", q(yol_m[sec], 1000), fark=True, olcek=0.001)
    P.ekle("pen", q(pen[sec], 10000), fark=True, olcek=0.0001)
    P.ekle("carp", carp[sec].astype(np.int32), fark=True)
    P.ekle("cs", q(cs[sec], 1000), fark=True, olcek=0.001)
    P.ekle("hucre", hucre[sec].astype(np.int32), fark=True)
    P.ekle("temas", tem_s)
    P.ekle("mod", np.clip(mod[sec], 0, 255).astype(np.uint8))
    # planlanan yollar
    Y = meta.get("yollar") or []
    yt, yn, yx, yy = [], [], [], []
    for ti, pts in Y:
        yt.append(ti)
        yn.append(len(pts))
        if pts:
            p = np.asarray(pts, dtype=float)
            if cerceve_bas:
                wx, wy = baslangictan_dunyaya(start, p[:, 0], p[:, 1])
            else:
                wx, wy = p[:, 0], p[:, 1]
            yx.append(wx)
            yy.append(wy)
    if Y:
        P.ekle("y_t", q(yt, 1000), fark=True, olcek=0.001)
        P.ekle("y_n", np.array(yn, np.int32))
        P.ekle("y_x", q(np.concatenate(yx) if yx else [], 100).astype(np.int32), fark=True, olcek=0.01)
        P.ekle("y_y", q(np.concatenate(yy) if yy else [], 100).astype(np.int32), fark=True, olcek=0.01)
    # çıkış sanısı (beyin; ekler 2 s'de bir)
    cikis = []
    for e in meta.get("ekler") or []:
        c = (e.get("ek") or {}).get("cikis")
        if c is not None and len(c) >= 2:
            cx, cy = (baslangictan_dunyaya(start, c[0], c[1]) if cerceve_bas else (c[0], c[1]))
            if not cikis or abs(cikis[-1][1] - float(cx)) + abs(cikis[-1][2] - float(cy)) > 1e-6:
                cikis.append([round(float(e["t"]), 2), round(float(cx), 2), round(float(cy), 2)])
    # sınırlar (v2 kayıtları): ekler 2 s'de bir, [merkez_x, merkez_y, boy_m, bakış_x, bakış_y, maliyet], başlangıç çerçevesi
    st, sn, sx, sy, sbx, sby, sboy, smal, ssec = [], [], [], [], [], [], [], [], []
    sinir_var = False
    for e in meta.get("ekler") or []:
        ekk = e.get("ek") or {}
        if "sinirlar" not in ekk:
            continue
        sinir_var = True
        L_ = [v for v in (ekk.get("sinirlar") or []) if v is not None and len(v) >= 6]
        sec_ = ekk.get("secilen_sinir")
        si = -1
        if sec_ is not None and len(sec_) >= 2 and L_:
            dd = [math.hypot(v[0] - sec_[0], v[1] - sec_[1]) for v in L_]
            if min(dd) < 0.05:
                si = int(np.argmin(dd))
        st.append(float(e["t"]))
        sn.append(len(L_))
        ssec.append(si)
        for v in L_:
            if cerceve_bas:
                cx, cy = baslangictan_dunyaya(start, v[0], v[1])
                bx, by = baslangictan_dunyaya(start, v[3], v[4])
            else:
                cx, cy, bx, by = v[0], v[1], v[3], v[4]
            sx.append(float(cx)); sy.append(float(cy)); sbx.append(float(bx)); sby.append(float(by))
            sboy.append(float(v[2])); smal.append(float(v[5]))
    if sinir_var and st:
        P.ekle("s_t", q(st, 1000), fark=True, olcek=0.001)
        P.ekle("s_n", np.array(sn, np.int32))
        P.ekle("s_sec", np.array(ssec, np.int32))
        P.ekle("s_x", q(sx, 100).astype(np.int32), fark=True, olcek=0.01)
        P.ekle("s_y", q(sy, 100).astype(np.int32), fark=True, olcek=0.01)
        P.ekle("s_bx", q(sbx, 100).astype(np.int32), fark=True, olcek=0.01)
        P.ekle("s_by", q(sby, 100).astype(np.int32), fark=True, olcek=0.01)
        P.ekle("s_boy", q(sboy, 100).astype(np.int32), olcek=0.01)
        P.ekle("s_mal", q(smal, 100).astype(np.int32), olcek=0.01)
    # harita
    hbilgi = None
    if cerceve_bas or tur == "labirent":
        hbilgi = harita_kodla(z, meta, list(start) if cerceve_bas else [0.0, 0.0, 0.0], P)
    # LiDAR
    lb = None
    if "tarama_mm" in z and "tarama_t" in z and "acilar" in z and len(z["tarama_t"]):
        tt = z["tarama_t"].astype(float)
        mm = z["tarama_mm"]
        ac = z["acilar"].astype(float)
        mon = meta.get("montaj") or [0.19, 0.0, 0.295, 0.0]
        mon3 = [float(mon[0]), float(mon[1]), float(mon[3]) if len(mon) > 3 else 0.0]
        dts = float(np.median(np.diff(tt))) if len(tt) > 1 else 0.1
        # tarama_t mutlak benzetim saati, t koşu başından: kayma kayıtta yok. Gerçek duvara en iyi oturan kaymayı seç.
        kayma, uz_kayma = 0.0, None
        t0d = meta.get("t0_dunya_s")
        try:
            kayma, uz_kayma = lidar_kayma_bul(sb, t, g, tt, mm, ac, mon3, dts, sabit=None if t0d is None else -float(t0d))
        except Exception as e:
            tani.append("lidar kayma hatası %s: %s" % (os.path.basename(yol), e))
        ks = max(1, int(round(lidar_adim_s / dts)))
        sc = np.arange(0, len(tt), ks)
        ri = np.arange(0, len(ac), isin_adim)
        q5 = mm[np.ix_(sc, ri)].astype(np.int32)
        q5 = np.where(q5 > 0, np.clip(np.round(q5 / 50.0), 1, 255), 0).astype(np.uint8)
        tts = tt[sc] + kayma + 0.5 * dts          # koşu saatinde tarama ortası
        P.ekle("l_t", q(tts, 1000), fark=True, olcek=0.001)
        P.ekle("l_d", q5)
        lb = {"adet": int(len(sc)), "isin": int(len(ri)), "acilar": [round(float(a), 5) for a in ac[ri]],
              "montaj": mon3, "hz": round(1.0 / (ks * dts), 2), "birim_m": 0.05, "tarama_hz": round(1.0 / dts, 1),
              "kayma_s": round(kayma, 3), "kayma_kaynak": "kayıt (t0_dunya_s)" if t0d is not None else "tahmin", "duvar_uzaklik_kaymasiz_cm": None if uz_kayma is None else uz_kayma[0],
              "duvar_uzaklik_cm": None if uz_kayma is None else uz_kayma[1]}
    ham, sik = P.bayt()
    hakem_kayit_durum = hs_kayit.get("durum") or ((("fail_sure") if float((meta.get("sonuc") or {}).get("sure_s") or 0) >= T - 0.2 else None) if tur == "labirent" else None)
    bilgi = {
        "tur": tur, "sahne": ad, "tohum": meta.get("tohum"), "dosya": goreli.replace("\\", "/"),
        "surum": surum if tur == "labirent" else None, "kume": kume, "kos": kos, "T": T,
        "kayit_zamani": datetime.datetime.fromtimestamp(os.path.getmtime(yol)).strftime("%Y-%m-%d %H:%M"),
        "baslangic": list(start), "cerceve": "baslangic" if cerceve_bas else "dunya", "modlar": [MOD_AD.get(m, m) for m in modlar],
        "n": int(len(sec)), "sure": round(float(t[-1]), 2), "paket": P.baslik, "harita": hbilgi, "lidar": lb,
        "cikis": cikis, "ilk_kare_hayalet_fark_m": None if ilk_fark is None else round(ilk_fark, 4),
        "poz_hata_maks_m": None if not np.isfinite(e_all).any() else round(float(np.nanmax(e_all)), 3),
        "ham_bayt": len(ham), "sik_bayt": len(sik), "sinir": bool(sinir_var and st),
    }
    if tur == "labirent":
        ol = hs.get("olaylar") or []
        bilgi.update({
            "durum": hs.get("durum") or ("fail_sure" if float(t[-1]) >= T - 0.2 else None),
            "sure_s": hs.get("sure_s"), "yol_m": hs.get("yol_m"), "carpma": hs.get("carpma_sayisi"),
            "carpma_s": hs.get("carpma_suresi_s"), "puan": hs.get("puan"), "dokum": hs.get("puan_dokumu"),
            "p_en": hs.get("p_en"), "hucre": hs.get("kesfedilen_hucre"), "toplam_hucre": hs.get("toplam_hucre"),
            "sebep": hs.get("sikisma_sebebi"),
            "carpmalar": [[o["t"], o.get("x"), o.get("y")] for o in ol if o.get("tur") == "carpma"],
            "hakem_olay": [[o["t"], o["tur"]] for o in ol if o.get("tur") not in ("carpma", "baslangic")],
            "p_en_an": round(float(t[int(np.argmax(pen >= pen.max() - 1e-9))]), 1) if len(pen) else None,
        })
        # yeniden oynatma, kayıttaki hakem sonucu ve CSV ile tutarlı mı
        uy = []
        if hakem_kayit_durum and hakem_kayit_durum != bilgi["durum"]:
            uy.append("kayıttaki hakem durumu %s, yeniden oynatma %s" % (hakem_kayit_durum, bilgi["durum"]))
        if hs_kayit.get("puan") is not None and abs(float(hs_kayit["puan"]) - float(hs.get("puan") or 0)) > 1.0:
            uy.append("puan kayıtta %.1f, yeniden oynatmada %.1f" % (hs_kayit["puan"], hs.get("puan") or 0))
        if csv_satir is not None:
            if csv_satir.get("durum") and csv_satir["durum"] != bilgi["durum"]:
                uy.append("CSV durumu %s, kayıt %s (koşu yeniden üretilmiş olabilir)" % (csv_satir["durum"], bilgi["durum"]))
            bilgi["beyin_olay"] = beyin_olaylari(csv_satir.get("olaylar"))
            bilgi["cozum_m_csv"] = ffloat(csv_satir.get("cozum_uzunlugu_m"))
            bilgi["son_mod_csv"] = csv_satir.get("son_mod")
            bilgi["kurtarma"] = csv_satir.get("kurtarma")
            bilgi["k_don"] = ffloat(csv_satir.get("k_don"))
            bilgi["dogru_duvar"] = ffloat(csv_satir.get("dogru_duvar_orani"))
        else:
            uy.append("CSV'de satırı yok")
        if meta.get("beyin_olaylari"):       # yeni kayıtlarda tam olay listesi (CSV yalnız son 8)
            bilgi["beyin_olay"] = [[round(float(o[0]), 1), str(o[1])] for o in meta["beyin_olaylari"] if len(o) >= 2]
            bilgi["olay_tam"] = True
        bilgi["uyumsuz"] = uy
    return bilgi, sik


def lidar_kayma_bul(sb, t, g, tt, mm, ac, mon, dts, n_tarama=36, sabit=None):
    """LiDAR tarama saatinin koşu saatine kayması (s): noktaları gerçek duvara en iyi oturtan değer (0,05 s adım,
    −1,5…+0,5 s). Döner: (kayma, (kaymasız ortanca cm, seçilen kaymayla ortanca cm)). Yalnız izleyici çizimi ve
    çerçeve denetimi içindir; beyin bunu görmez."""
    D = np.array(sb["duvarlar"], dtype=float)
    if not len(D) or len(tt) < 5:
        return 0.0, None
    A, B = D[:, :2], D[:, 2:4]
    AB = B - A
    L2 = np.maximum((AB ** 2).sum(1), 1e-12)
    th_u = np.unwrap(g[:, 2])
    # dönüş anlarındaki taramalar kaymaya en duyarlı olanlar; yarısı dönüş, yarısı düzenli örnek
    w = np.abs(np.gradient(th_u, t)) if len(t) > 2 else np.zeros(len(t))
    ti = np.clip(np.searchsorted(t, tt), 0, len(t) - 1)
    don = np.flatnonzero(w[ti] > 0.4)
    sec = np.unique(np.concatenate([don[np.linspace(0, len(don) - 1, min(len(don), n_tarama // 2)).astype(int)] if len(don) else [],
                                    np.linspace(0, len(tt) - 1, n_tarama // 2).astype(int)]).astype(int))

    def ortanca_uz(off):
        uz = []
        for k in sec:
            tm = tt[k] + off + 0.5 * dts
            x = np.interp(tm, t, g[:, 0])
            y = np.interp(tm, t, g[:, 1])
            th = np.interp(tm, t, th_u)
            ok = mm[k] > 0
            if ok.sum() < 10:
                continue
            r = mm[k][ok] / 1000.0
            a = ac[ok] + th + mon[2]
            ox = x + mon[0] * math.cos(th) - mon[1] * math.sin(th)
            oy = y + mon[0] * math.sin(th) + mon[1] * math.cos(th)
            P_ = np.stack([ox + r * np.cos(a), oy + r * np.sin(a)], 1)[::4]
            AP = P_[:, None, :] - A[None]
            u = np.clip((AP * AB[None]).sum(2) / L2[None], 0, 1)
            C = A[None] + u[..., None] * AB[None]
            uz.extend(np.sqrt(((P_[:, None, :] - C) ** 2).sum(2)).min(1).tolist())
        return float(np.median(uz)) * 100 if uz else float("inf")

    if sabit is not None:                 # kayıt zaman tabanını veriyor: yalnız denetim için iki değer
        return float(sabit), (round(ortanca_uz(0.0), 1), round(ortanca_uz(float(sabit)), 1))
    adaylar = np.round(np.arange(-1.5, 0.5001, 0.05), 3)
    sonuc = [(ortanca_uz(o), o) for o in adaylar]
    en = min(sonuc)
    sifir = [s for s in sonuc if abs(s[1]) < 1e-9][0][0]
    return float(en[1]), (round(sifir, 1), round(en[0], 1))


# ------------------------------------------------------------------ özet tablolar
def grup_ozet(rows, anahtar_fn):
    G = {}
    for r in rows:
        G.setdefault(anahtar_fn(r), []).append(r)
    out = []
    for k in sorted(G):
        rs = G[k]
        bas = [r for r in rs if r.get("durum") == "basari"]
        sure_b = [ffloat(r.get("sure_s")) for r in bas]
        out.append({
            "anahtar": k, "n": len(rs), "basari": len(bas),
            "ortanca_sure": ortanca(sure_b), "en_uzun": max([x for x in sure_b if x is not None], default=None),
            "carpma_top": int(sum(int(float(r.get("carpma_sayisi") or 0)) for r in rs)),
            "carpma_kosu": sum(1 for r in rs if float(r.get("carpma_sayisi") or 0) > 0),
            "puan_ortanca": ortanca([ffloat(r.get("puan")) for r in rs]),
            "p_en_ortanca": ortanca([ffloat(r.get("p_en")) for r in rs]),
        })
    return out


def boyut_anahtari(r):
    return boyut_of(r.get("sahne"))


def _kaynak(kaynak, ad, rows, tm):
    kaynak[ad] = None if tm is None else {"zaman": datetime.datetime.fromtimestamp(tm).strftime("%Y-%m-%d %H:%M"),
                                          "satir": len(rows or [])}


def ozetler():
    kaynak = {}
    out = {"kaynak": kaynak}
    # MuJoCo: mujoco.csv (v1 geliştirme, eski biçim) + sürüm/küme sütunlu eşleri
    mj = []
    dosyalar = sorted(os.path.basename(p) for p in glob.glob(os.path.join(SONUC, "mujoco*.csv")))
    dosyalar = (["mujoco.csv"] if "mujoco.csv" in dosyalar else []) + [d for d in dosyalar if d != "mujoco.csv"]
    if not dosyalar:
        kaynak["mujoco.csv"] = None
    for ad in dosyalar:
        if ad.startswith("mujoco_2b"):          # 2B karşılaştırma dosyası MuJoCo sonucu değil
            continue
        rows, tm = csv_oku(ad)
        _kaynak(kaynak, ad, rows, tm)
        for r in rows or []:
            r = dict(r)
            r["_dosya"] = ad
            r["_surum"] = surum_bul(satir=r, yol=ad)
            r["_kume"] = kume_bul(r.get("sahne"), satir=r, yol=ad)
            r["_kos"] = kos_bul(satir=r)
            mj.append(r)
    mj = tekille(mj, ("_surum", "_kume", "_kos", "sahne", "tohum"))
    out["mj"] = mj
    out["mj_satir"] = {(r["_surum"], r["_kume"], r["_kos"], r["sahne"], str(r["tohum"])): r for r in mj}
    out["surumler"] = sorted({r["_surum"] for r in mj}, key=lambda s: (len(s), s))
    # 2B ve zaman dökümü
    ilk, it = csv_oku("ilk.csv")
    haf, ht = csv_oku("hafiza.csv")
    odo, ot = csv_oku("odometri.csv")
    v22, vt = csv_oku("v2_2b.csv")
    for ad, tm, rows in (("ilk.csv", it, ilk), ("v2_2b.csv", vt, v22), ("hafiza.csv", ht, haf), ("odometri.csv", ot, odo)):
        _kaynak(kaynak, ad, rows, tm)
    tani = []
    for p in sorted(glob.glob(os.path.join(SONUC, "tani*.csv"))):
        ad = os.path.basename(p)
        rows, tm = csv_oku(ad)
        _kaynak(kaynak, ad, rows, tm)
        for r in rows or []:
            r = dict(r)
            r["_surum"] = surum_bul(satir=r, yol=ad)
            r["_kume"] = kume_bul(r.get("sahne"), satir=r, yol=ad)
            tani.append(r)
    out["tani"] = tekille(tani, ("_surum", "_kume", "sahne", "tohum"))
    ilk = tekille(ilk, ("strateji", "sahne", "tohum", "donus_hata"))
    haf = tekille(haf, ("strateji", "sahne", "tohum", "donus_hata"))
    odo = tekille(odo, ("strateji", "sahne", "tohum", "donus_hata"))
    v22 = tekille(v22, ("strateji", "sahne", "tohum", "donus_hata"))
    kesif2b = [r for r in ilk if r.get("strateji") == "kesif"]
    out["b2_kesif"] = grup_ozet(kesif2b, boyut_anahtari) if kesif2b else None
    out["b2_v1"], out["b2_v2"] = kesif2b, [r for r in v22 if r.get("strateji", "kesif") == "kesif"]
    out["strateji"] = grup_ozet(ilk, lambda r: (r.get("strateji"), boyut_of(r.get("sahne")))) if ilk else None
    odo_tum = list(odo or []) + kesif2b
    out["odometri"] = grup_ozet(odo_tum, lambda r: (ffloat(r.get("donus_hata")) or 0.0, boyut_of(r.get("sahne")))) if odo else None
    hz = []
    for r in haf or []:
        hz.append({"sahne": r["sahne"], "tohum": r["tohum"], "ilk_durum": r.get("durum"), "ilk_sure": ffloat(r.get("sure_s")),
                   "haf_durum": r.get("hafiza_durum") or None, "haf_sure": ffloat(r.get("hafiza_sure_s")),
                   "haf_puan": ffloat(r.get("hafiza_puan"))})
    out["hafiza"] = sorted(hz, key=lambda r: (boyut_of(r["sahne"]), r["sahne"], str(r["tohum"])))
    k2 = {(r["sahne"], str(r["tohum"])): r for r in kesif2b}
    out["eslesik"] = [(r, k2[(r["sahne"], str(r["tohum"]))]) for r in mj
                      if r["_surum"] == "v1" and r["_kume"] == "gelistirme" and r["_kos"] == "ilk"
                      and (r["sahne"], str(r["tohum"])) in k2]
    b2f = []
    for ad, rows in (("ilk.csv", ilk), ("odometri.csv", odo), ("hafiza.csv", haf)):
        for r in rows or []:
            if r.get("durum") and r.get("durum") != "basari":
                b2f.append(dict(r, _dosya=ad))
    out["b2_basarisiz"] = b2f
    return out


def mj_sec(oz, surum=None, kume=None, kos="ilk"):
    return [r for r in oz["mj"] if (surum is None or r["_surum"] == surum) and (kume is None or r["_kume"] == kume)
            and (kos is None or r["_kos"] == kos)]


def basari_ozet(rows):
    bas = [r for r in rows if r.get("durum") == "basari"]
    return {"n": len(rows), "basari": len(bas), "sure": ortanca([ffloat(r.get("sure_s")) for r in bas]),
            "carpma": sum(int(float(r.get("carpma_sayisi") or 0)) for r in rows),
            "puan_ort": (sum(ffloat(r.get("puan")) or 0 for r in rows) / len(rows)) if rows else None}


def cozum_m(sahne):
    try:
        return sahne_bilgisi(sahne).get("cozum_m")
    except Exception:
        return None


# ------------------------------------------------------------------ HTML parçaları
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def hucre_basari(g):
    if not g:
        return '<td class="sag">-</td>'
    oran = g["basari"] / g["n"] if g["n"] else 0
    sinif = "iyi" if oran == 1 else ("orta" if oran > 0 else "kotu")
    return '<td class="sag"><span class="oran %s">%d/%d</span></td>' % (sinif, g["basari"], g["n"])


def tablo_boyut(gruplar, baslik_not):
    if not gruplar:
        return '<p class="yok">Henüz yok: sonuç dosyası bulunamadı.</p>'
    s = ['<div class="tablo-sar"><table><thead><tr><th>Boyut</th><th class="sag">Koşu</th><th class="sag">Başarı</th>'
         '<th class="sag">Ortanca süre<br><small>başarılılar</small></th><th class="sag">15:00\'a<br><small>oranla</small></th>'
         '<th class="sag">En uzun başarı</th><th class="sag">Çarpma<br><small>toplam (koşu)</small></th>'
         '<th class="sag">Ortanca puan</th><th>15 dakikada</th></tr></thead><tbody>']
    for g in gruplar:
        o = g["ortanca_sure"]
        oran = g["basari"] / g["n"] if g["n"] else 0
        hk = "her koşuda çözüldü" if oran == 1 else ("kısmen çözüldü" if oran > 0 else "çözülmedi")
        s.append('<tr><th scope="row">%s</th><td class="sag">%d</td>%s<td class="sag">%s</td><td class="sag">%s</td>'
                 '<td class="sag">%s</td><td class="sag">%d (%d)</td><td class="sag">%s</td><td>%s</td></tr>' % (
                     boyut_ad(g["anahtar"]), g["n"], hucre_basari(g), fsure(o),
                     ("%%%s" % fnum(100 * o / T_SINIR, 0)) if o else "-", fsure(g["en_uzun"]),
                     g["carpma_top"], g["carpma_kosu"], fnum(g["puan_ortanca"], 0), hk))
    s.append("</tbody></table></div>")
    if baslik_not:
        s.append('<p class="not">%s</p>' % baslik_not)
    return "".join(s)


def cozulen_cumle(gruplar, etiket):
    if not gruplar:
        return "%s: henüz yok." % etiket
    parca = []
    tam = None                      # baştan ardışık "hepsi çözüldü" boyutlarının en büyüğü
    for g in gruplar:
        if g["basari"] == g["n"]:
            tam = g
        else:
            break
    if tam:
        parca.append("<b>%s%s kadar her koşu</b> 15 dakikada çözüldü" % (boyut_ad(tam["anahtar"]), ek(tam["anahtar"][1], "e")))
    else:
        parca.append("hiçbir boyutta tüm koşular çözülmedi")
    for g in gruplar:
        if tam and g["anahtar"] <= tam["anahtar"]:
            continue
        parca.append("%s%s %d/%d" % (boyut_ad(g["anahtar"]), ek(g["anahtar"][1], "de"), g["basari"], g["n"]))
    return "%s: %s." % (etiket, ", ".join(parca) if parca else "-")


def tablo_strateji(gr):
    if not gr:
        return '<p class="yok">Henüz yok: <code>ilk.csv</code> bulunamadı.</p>'
    boy = sorted({k[1] for k in (g["anahtar"] for g in gr)})
    st = [s for s in ("kesif", "sag_duvar", "rastgele") if any(g["anahtar"][0] == s for g in gr)]
    st += sorted({g["anahtar"][0] for g in gr} - set(st))
    d = {g["anahtar"]: g for g in gr}
    s = ['<div class="tablo-sar"><table><thead><tr><th>Strateji</th>']
    s += ['<th class="sag">%s</th>' % boyut_ad(b) for b in boy]
    s.append('<th class="sag">Toplam</th></tr></thead><tbody>')
    for x in st:
        s.append('<tr><th scope="row">%s</th>' % STRATEJI_AD.get(x, x))
        tb = tn = 0
        for b in boy:
            g = d.get((x, b))
            if g:
                tb += g["basari"]
                tn += g["n"]
                s.append('<td class="sag"><span class="oran %s">%d/%d</span><br><small>%s</small></td>' % (
                    "iyi" if g["basari"] == g["n"] else ("orta" if g["basari"] else "kotu"), g["basari"], g["n"],
                    fsure(g["ortanca_sure"]) if g["ortanca_sure"] else "&nbsp;"))
            else:
                s.append('<td class="sag">-</td>')
        s.append('<td class="sag"><b>%d/%d</b></td></tr>' % (tb, tn))
    s.append("</tbody></table></div>")
    return "".join(s)


def tablo_odometri(gr):
    if not gr:
        return '<p class="yok">Henüz yok: <code>odometri.csv</code> bulunamadı.</p>'
    boy = sorted({g["anahtar"][1] for g in gr})
    hs = sorted({g["anahtar"][0] for g in gr})
    d = {g["anahtar"]: g for g in gr}
    s = ['<div class="tablo-sar"><table><thead><tr><th>Dönüş fazlası</th>']
    s += ['<th class="sag">%s</th>' % boyut_ad(b) for b in boy]
    s.append("</tr></thead><tbody>")
    for h in hs:
        s.append('<tr><th scope="row">%%%s</th>' % fnum(100 * h, 0))
        for b in boy:
            g = d.get((h, b))
            s.append(hucre_basari(g) if g else '<td class="sag">-</td>')
        s.append("</tr>")
    s.append("</tbody></table></div>")
    return "".join(s)


def tablo_hafiza(hz):
    if not hz:
        return '<p class="yok">Henüz yok: <code>hafiza.csv</code> bulunamadı ya da boş.</p>'
    s = ['<div class="tablo-sar"><table><thead><tr><th>Labirent</th><th class="sag">Tohum</th><th>İlk tur</th>'
         '<th class="sag">İlk süre</th><th>Hafızalı tur</th><th class="sag">Hafızalı süre</th><th class="sag">Kazanç</th>'
         '</tr></thead><tbody>']
    for r in hz:
        kaz = "-"
        if r["ilk_sure"] and r["haf_sure"] and r["ilk_durum"] == "basari" and r["haf_durum"] == "basari":
            kaz = "%%%s" % fnum(100 * (1 - r["haf_sure"] / r["ilk_sure"]), 0)
        s.append('<tr><th scope="row">%s</th><td class="sag">%s</td><td>%s</td><td class="sag">%s</td><td>%s</td>'
                 '<td class="sag">%s</td><td class="sag">%s</td></tr>' % (
                     esc(kisa_sahne(r["sahne"])), esc(r["tohum"]), rozet(r["ilk_durum"]), fsure(r["ilk_sure"]),
                     rozet(r["haf_durum"]) if r["haf_durum"] else '<span class="soluk">koşulmadı</span>',
                     fsure(r["haf_sure"]), kaz))
    s.append("</tbody></table></div>")
    return "".join(s)


def kisa_sahne(ad):
    return (ad or "").replace("labirent_", "").replace("x", "×", 1)


def rozet(d):
    if not d:
        return '<span class="rozet">?</span>'
    return '<span class="rozet %s">%s %s</span>' % ("r-iyi" if d == "basari" else "r-kotu", "✓" if d == "basari" else "✗",
                                                    esc(DURUM_AD.get(d, d)))


def tablo_eslesik(es):
    if not es:
        return '<p class="yok">Henüz yok.</p>'
    G = {}
    for m, b in es:
        G.setdefault(boyut_of(m["sahne"]), []).append((m, b))
    s = ['<div class="tablo-sar"><table><thead><tr><th>Boyut</th><th class="sag">Eş koşu</th><th class="sag">MuJoCo başarı</th>'
         '<th class="sag">2B başarı</th><th class="sag">Süre farkı<br><small>ikisi de başarılı, ortanca</small></th>'
         '<th class="sag">Poz hatası maks<br><small>MuJoCo / 2B, ortanca m</small></th></tr></thead><tbody>']
    for k in sorted(G):
        L = G[k]
        mb = sum(1 for m, b in L if m.get("durum") == "basari")
        bb = sum(1 for m, b in L if b.get("durum") == "basari")
        fr = [ffloat(m["sure_s"]) / ffloat(b["sure_s"]) - 1 for m, b in L
              if m.get("durum") == "basari" and b.get("durum") == "basari" and ffloat(b.get("sure_s"))]
        s.append('<tr><th scope="row">%s</th><td class="sag">%d</td><td class="sag">%d/%d</td><td class="sag">%d/%d</td>'
                 '<td class="sag">%s</td><td class="sag">%s / %s</td></tr>' % (
                     boyut_ad(k), len(L), mb, len(L), bb, len(L),
                     ("%+.0f %%" % (100 * ortanca(fr))).replace("%+", "+").replace(" %", " %") if fr else "-",
                     fnum(ortanca([ffloat(m.get("poz_hata_maks_m")) for m, b in L]), 2),
                     fnum(ortanca([ffloat(b.get("poz_hata_maks_m")) for m, b in L]), 2)))
    s.append("</tbody></table></div>")
    return "".join(s)


def b2_basarisiz_html(rows):
    if not rows:
        return '<p class="yok">2B benzeticide başarısız koşu yok ya da sonuç dosyası yok.</p>'
    G = {}
    for r in rows:
        G.setdefault((r["_dosya"], r.get("strateji")), []).append(r)
    s = []
    for (dosya, st), L in sorted(G.items(), key=lambda kv: (kv[0][0] != "ilk.csv", kv[0][1] != "kesif", kv[0])):
        L.sort(key=lambda r: (boyut_of(r["sahne"]), r["sahne"], ffloat(r.get("donus_hata")) or 0, int(float(r.get("tohum") or 0))))
        acik = " open" if st == "kesif" and dosya == "ilk.csv" else ""
        s.append('<details%s><summary><b>%s</b> · %s · %d başarısız</summary>' % (acik, STRATEJI_AD.get(st, st),
                                                                                  {"ilk.csv": "ilk tur", "odometri.csv": "odometri duyarlılığı",
                                                                                   "hafiza.csv": "hafıza turu"}.get(dosya, dosya), len(L)))
        s.append('<div class="tablo-sar"><table><thead><tr><th>Labirent</th><th class="sag">Tohum</th>'
                 '<th class="sag">Dönüş fazlası</th><th>Sonuç</th><th class="sag">Süre</th><th class="sag">İlerleme</th>'
                 '<th>Neden (sonuç dosyasından)</th></tr></thead><tbody>')
        for r in L:
            s.append('<tr><th scope="row">%s</th><td class="sag">%s</td><td class="sag">%%%s</td><td>%s</td><td class="sag">%s</td>'
                     '<td class="sag">%%%s</td><td>%s</td></tr>' % (
                         esc(kisa_sahne(r["sahne"])), esc(r.get("tohum")), fnum(100 * (ffloat(r.get("donus_hata")) or 0), 0),
                         rozet(r.get("durum")), fsure(ffloat(r.get("sure_s"))), fnum(100 * (ffloat(r.get("p_en")) or 0), 0),
                         esc(neden_2b(r))))
        s.append("</tbody></table></div></details>")
    return "".join(s)


def neden_2b(r):
    d = r.get("durum")
    parca = []
    if d == "fail_sure":
        parca.append("15:00 doldu")
    elif d == "fail_sikisma":
        sb = r.get("sikisma_sebebi") or ""
        parca.append({"ilerlemesiz": "300 s yeni hücreye girmedi", "hareketsiz": "60 s yerinden 0,2 m'den fazla ayrılmadı"}.get(sb, "sıkıştı " + sb))
    elif d == "fail_start":
        parca.append("START çizgisinden geri çıktı")
    if r.get("son_mod"):
        parca.append("son mod: %s" % MOD_AD.get(r["son_mod"], r["son_mod"]))
    c = int(float(r.get("carpma_sayisi") or 0))
    if c:
        parca.append("%d çarpma" % c)
    ol = [o for o in beyin_olaylari(r.get("olaylar")) if "kurtarma" in o[1] or "tukendi" in o[1]]
    if ol:
        parca.append("%d kurtarma/tükenme (ilki %s s)" % (len(ol), fnum(ol[0][0], 0)))
    return "; ".join(parca)


# ------------------------------------------------------------------ üst bölüm (v2 dönemi)
def oyna_link(emb, anahtar, yazi, t=0.0, baslik=None):
    kid = emb.get(anahtar)
    if not kid:
        return '<span class="soluk" title="Bu koşunun kaydı sayfaya gömülmedi">%s</span>' % yazi
    return '<a class="oyna" href="?kosu=%s&amp;t=%.1f#oynatici" data-kosu="%s" data-t="%.1f"%s>%s</a>' % (
        kid, t, kid, t, (' title="%s"' % esc(baslik)) if baslik else "", yazi)


def anahtar_r(r):
    return (r["_surum"], r["_kume"], r["_kos"], r["sahne"], str(r["tohum"]))


def oran_span(b, n, ek_sinif=""):
    if not n:
        return '<span class="soluk">henüz yok</span>'
    sinif = "iyi" if b == n else ("orta" if b else "kotu")
    return '<span class="oran %s%s">%d/%d</span>' % (sinif, ek_sinif, b, n)


def hukum_html(oz):
    sv = "v2" if mj_sec(oz, "v2", "sinama") else (oz["surumler"][-1] if oz["surumler"] else "v2")
    rows = mj_sec(oz, sv, "sinama")
    if not rows:
        return ('<div class="hukum kart"><h3 class="hukum-baslik">Hiç görmediği labirentlerde 15 dakikada</h3>'
                '<p class="yok">Henüz yok: sınama kümesi sonuç dosyası (<code>mujoco_sinama_*.csv</code>) bulunamadı.</p></div>')
    boy = sorted({boyut_of(r["sahne"]) for r in rows})
    kp = []
    for b in boy:
        rb = [r for r in rows if boyut_of(r["sahne"]) == b]
        o = basari_ozet(rb)
        nl = len({r["sahne"] for r in rb})
        kp.append('<div class="kpi"><div class="kpi-d">%s</div><div class="kpi-a">%s: FINISH\'ten çıkan koşu (%d labirent × %d tohum)</div></div>' % (
            oran_span(o["basari"], o["n"], " buyuk"), boyut_ad(b), nl, max(1, o["n"] // max(1, nl))))
    o = basari_ozet(rows)
    kp.append('<div class="kpi"><div class="kpi-d">%s</div><div class="kpi-a">ortanca süre, çıkan %d koşu (15:00\'a oranla %%%s)</div></div>' % (
        fsure(o["sure"]), o["basari"], fnum(100 * o["sure"] / T_SINIR, 0) if o["sure"] else "-"))
    kp.append('<div class="kpi"><div class="kpi-d">%d</div><div class="kpi-a">çarpma, %d koşunun toplamı</div></div>' % (o["carpma"], o["n"]))
    diger = []
    for s2 in oz["surumler"]:
        if s2 == sv:
            continue
        r2 = mj_sec(oz, s2, "sinama")
        if r2:
            diger.append("%s beyni aynı koşularda: %s, çarpma %d" % (s2, ", ".join(
                "%s %d/%d" % (boyut_ad(b), basari_ozet([r for r in r2 if boyut_of(r["sahne"]) == b])["basari"],
                              basari_ozet([r for r in r2 if boyut_of(r["sahne"]) == b])["n"]) for b in boy), basari_ozet(r2)["carpma"]))
    kaynak = ", ".join(sorted({"<code>%s</code>" % r["_dosya"] for r in rows}))
    s = ['<div class="hukum kart">',
         '<div class="hukum-ust"><span class="etiket e-sin">sınama kümesi</span> <span class="etiket e-mj">MuJoCo · %s beyni (varsayılan)</span></div>' % sv,
         '<h3 class="hukum-baslik">Hiç görmediği labirentlerde 15 dakikada</h3>',
         '<div class="kpiler">%s</div>' % "".join(kp),
         '<p class="not">%s. Kaynak: %s. Tohum yalnız LiDAR gürültüsünü değiştirir; aynı labirentin iki koşusu bağımsız iki deneme sayılmamalı.</p>' % (
             "; ".join(diger) if diger else "Başka sürüm yok", kaynak),
         '<p class="neden-ayri"><b>Neden ayrı tutuluyor:</b> beyin geliştirme labirentlerinde ayıklandı ve ayarlandı, orada iyi '
         'çıkması kısmen ezber olabilir. Sınama labirentleri (13×13 ve 17×17, t4–t8) ayar sırasında hiç koşulmadı; asıl hüküm '
         'bu yüzden onlardan.</p>', '</div>']
    gr = {s2: mj_sec(oz, s2, "gelistirme") for s2 in oz["surumler"]}
    gr = {k: v for k, v in gr.items() if v}
    if gr:
        boyg = sorted({boyut_of(r["sahne"]) for v in gr.values() for r in v})
        s.append('<div class="kart gelistirme"><div class="hukum-ust"><span class="etiket e-gel">geliştirme kümesi</span></div>'
                 '<h3 style="margin-top:6px">Geliştirme sırasında kullanılan labirentler</h3>'
                 '<p class="not">11 labirent (5×5 … 17×17, t1–t3) × 3 tohum. Beyin bunlarla geliştirildi; sayılar iyimser okunmalı.</p>'
                 '<div class="tablo-sar"><table><thead><tr><th>Boyut</th>')
        for s2 in gr:
            s.append('<th class="sag">%s başarı</th><th class="sag">%s ortanca süre</th>' % (s2, s2))
        s.append('</tr></thead><tbody>')
        for b in boyg:
            s.append('<tr><th scope="row">%s</th>' % boyut_ad(b))
            for s2, rs in gr.items():
                o2 = basari_ozet([r for r in rs if boyut_of(r["sahne"]) == b])
                s.append('<td class="sag">%s</td><td class="sag">%s</td>' % (oran_span(o2["basari"], o2["n"]), fsure(o2["sure"])))
            s.append('</tr>')
        s.append('<tr class="toplam"><th scope="row">Toplam</th>')
        for s2, rs in gr.items():
            o2 = basari_ozet(rs)
            s.append('<td class="sag"><b>%d/%d</b></td><td class="sag">%s</td>' % (o2["basari"], o2["n"], fsure(o2["sure"])))
        s.append('</tr></tbody></table></div></div>')
    return "".join(s)


def _orta_aralik(xs, nd=1, carp=1.0):
    xs = [x * carp for x in xs if x is not None]
    if not xs:
        return "-"
    a, b = min(xs), max(xs)
    return fnum(a, nd) if abs(a - b) < 10 ** -nd else "%s–%s" % (fnum(a, nd), fnum(b, nd))


def neden_html(oz, emb, uz):
    T_ = oz["tani"]
    if not T_:
        return '<p class="yok">Henüz yok: zaman dökümü (<code>tani_*.csv</code>) bulunamadı.</p>'
    v2 = [r for r in T_ if r["_surum"] == "v2"] or T_

    def pay(R, alan):
        top = sum(ffloat(r.get("sure_s")) or 0 for r in R)
        return 100 * sum(ffloat(r.get(alan)) or 0 for r in R) / top if top else None
    v_or = {sv: ortanca([ffloat(r.get("v_duz_ort")) for r in T_ if r["_surum"] == sv]) for sv in sorted({r["_surum"] for r in T_})}
    F = [r for r in v2 if r["_kume"] == "sinama" and r.get("durum") != "basari" and boyut_of(r["sahne"])[0] >= 17]
    cz = [ffloat(r.get("cozum_m")) for r in F]
    yal = [ffloat(r.get("cozum_m")) / ffloat(r.get("v_duz_ort")) / 60 for r in F if ffloat(r.get("v_duz_ort"))]
    sv_ad = v2[0]["_surum"]
    yol_or = ortanca([ffloat(r.get("yol_orani")) for r in F])
    s = ['<div class="iki neden"><div>',
         '<p>Zaman dökümü (%s beyni, %d MuJoCo koşusu): sürenin <b>%%%s</b> kadarı düz sürüş, %%%s kadarı yerinde dönüş, %%%s kadarı kurtarma. '
         'Ölçülen düz sürüş hızı ortanca <b>%s m/s</b>%s; komut 0,25 m/s.</p>' % (
             sv_ad, len(v2), fnum(pay(v2, "duz_s"), 0), fnum(pay(v2, "donus_s"), 0), fnum(pay(v2, "kurtarma_s"), 0),
             fnum(v_or.get(sv_ad), 3), (" (v1: %s m/s)" % fnum(v_or["v1"], 3)) if "v1" in v_or and sv_ad != "v1" else "")]
    if F:
        s.append('<p>Sınamada çıkamayan %d koşunun hepsi 17×17. Bu labirentlerin çözüm yolu <b>%s m</b>; o hızla '
                 '<b>yalnız çözüm yolunu sürmek %s dakika</b> tutar, yanlış kollara hiç girmeden bile. Yürünen yol / çözüm yolu ortanca %s: '
                 'keşif israf etmiyor, hız yetmiyor.</p>' % (len(F), _orta_aralik(cz, 0), _orta_aralik(yal, 1), fnum(yol_or, 2)))
    if uz["satirlar"]:
        R = uz["satirlar"]
        b = [r for r in R if r.get("durum") == "basari"]
        on = {}
        for r in R:
            for km in ("sinama", "gelistirme"):
                x = oz["mj_satir"].get((r["_surum"], km, "ilk", r["sahne"], str(r["tohum"])))
                if x:
                    on[id(r)] = x
                    break
        kurtulan = [r for r in b if on.get(id(r)) is not None and on[id(r)].get("durum") != "basari"]
        kalan = [r for r in R if r.get("durum") != "basari"]
        s.append('<p><span class="etiket e-uza">kural dışı: 30 dk</span> Aynı beyne 30 dakika verildi (%d koşu, tohum 0). '
                 '15 dakikada çıkamayanlardan <b>%d koşu</b> 30 dakikada çıktı%s.%s%s <a href="#uzatilmis">Ayrıntı</a>.</p>' % (
                     len(R), len(kurtulan),
                     (" (%s)" % ", ".join("%s %s" % (kisa_sahne(r["sahne"]), fsure(ffloat(r.get("sure_s")))) for r in kurtulan)) if kurtulan else "",
                     (" <b>Ama hız tek neden değil:</b> %d koşu 30 dakikada da çıkamadı (%s)." % (len(kalan), ", ".join(
                         "%s %s %s" % (kisa_sahne(r["sahne"]), DURUM_AD.get(r.get("durum"), r.get("durum")), fsure(ffloat(r.get("sure_s"))))
                         for r in kalan))) if kalan else "",
                     "" if uz["bitti"] else " <b>Ölçüm rapor üretilirken bitmemişti</b>; sayılar o anki dosyadan."))
    else:
        s.append('<p class="not"><span class="etiket e-uza">kural dışı: 30 dk</span> Uzatılmış süre ölçümü %s.</p>' % (
            "henüz yok" if not uz["basladi"] else "rapor üretilirken bitmemişti, satır yok"))
    s.append('</div><div>%s</div></div>' % grafik_svg(oz, emb, uz, v_or.get(sv_ad)))
    return "".join(s)


def grafik_svg(oz, emb, uz, v_duz):
    N = []
    for r in mj_sec(oz, "v2", None, "ilk") or mj_sec(oz, None, None, "ilk"):
        c = cozum_m(r["sahne"])
        if c is None:
            continue
        T = kume_T(r["_kume"])
        y = min(ffloat(r.get("sure_s")) or T, T)
        if r["_kume"] == "uzatilmis" and r.get("durum") == "basari" and y <= T_SINIR:
            continue                      # 15 dakikada da çıkan koşunun kopyası: grafiği kalabalıklaştırmasın
        N.append({"x": c, "y": y, "ok": r.get("durum") == "basari", "kume": r["_kume"], "r": r})
    if not N:
        return ""
    W, H, ml, mr, mt, mb = 640, 340, 46, 14, 12, 46
    xmax = max(40.0, math.ceil((max(n["x"] for n in N) + 8) / 20.0) * 20)
    ymax = 32.0 if any(n["kume"] == "uzatilmis" for n in N) else 17.0
    X = lambda x: ml + (W - ml - mr) * x / xmax
    Y = lambda m: H - mb - (H - mt - mb) * m / ymax
    s = ['<figure class="grafik"><svg viewBox="0 0 %d %d" role="img" aria-label="Çözüm yolu uzunluğuna göre bitiş süresi">' % (W, H)]
    for m in range(0, int(ymax) + 1, 5):
        s.append('<line class="g-izgara" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f"/><text class="g-eksen" x="%.1f" y="%.1f" text-anchor="end">%d</text>' % (
            ml, W - mr, Y(m), Y(m), ml - 6, Y(m) + 4, m))
    for x in range(0, int(xmax) + 1, 20 if xmax <= 200 else 40):
        s.append('<line class="g-izgara" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f"/><text class="g-eksen" x="%.1f" y="%.1f" text-anchor="middle">%d</text>' % (
            X(x), X(x), mt, H - mb, X(x), H - mb + 16, x))
    s.append('<text class="g-eksen-ad" x="%.1f" y="%d" text-anchor="middle">çözüm yolu uzunluğu (m)</text>' % ((ml + W - mr) / 2, H - 8))
    s.append('<text class="g-eksen-ad" x="12" y="%.1f" text-anchor="middle" transform="rotate(-90 12 %.1f)">bitiş süresi (dk)</text>' % (
        (mt + H - mb) / 2, (mt + H - mb) / 2))
    if v_duz:
        x2 = min(xmax, v_duz * 60 * ymax)
        s.append('<line class="g-ref" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (X(0), Y(0), X(x2), Y(x2 / v_duz / 60)))
        lx = x2 * 0.5
        s.append('<text class="g-ref-y" x="%.1f" y="%.1f" text-anchor="start">yalnız çözüm yolunu %s m/s ile sürmek</text>' % (
            X(lx) + 6, Y(lx / v_duz / 60) + 14, fnum(v_duz, 2)))
    for m, ad in ((15, "15 dk sınırı"), (30, "30 dk (kural dışı)")):
        if m <= ymax:
            s.append('<line class="g-sinir" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f"/><text class="g-sinir-y" x="%.1f" y="%.1f" text-anchor="start">%s</text>' % (
                ml, W - mr, Y(m), Y(m), ml + 4, Y(m) - 5, ad))
    for n in sorted(N, key=lambda n: n["ok"]):
        r = n["r"]
        x = X(n["x"] + (int(r.get("tohum") or 0) - 1) * xmax * 0.006)
        y = Y(n["y"] / 60.0)
        bas = "%s · %s · tohum %s · çözüm %s m · %s%s" % (KUME_AD.get(n["kume"], n["kume"]), kisa_sahne(r["sahne"]), r.get("tohum"),
                                                     fnum(n["x"], 0), DURUM_AD.get(r.get("durum"), r.get("durum")),
                                                     (" " + fsure(ffloat(r.get("sure_s")))) if n["ok"] else "")
        if not n["ok"]:
            sek = '<path class="g-kotu" d="M%.1f %.1fl8 8m0 -8l-8 8"/>' % (x - 4, y - 4)
        elif n["kume"] == "sinama":
            sek = '<circle class="g-iyi" cx="%.1f" cy="%.1f" r="4.6"/>' % (x, y)
        elif n["kume"] == "uzatilmis":
            sek = '<path class="g-uza" d="M%.1f %.1fl5.5 5.5l-5.5 5.5l-5.5 -5.5z"/>' % (x, y - 5.5)
        else:
            sek = '<rect class="g-gel" x="%.1f" y="%.1f" width="8" height="8"/>' % (x - 4, y - 4)
        kid = emb.get(anahtar_r(r))
        if kid:
            s.append('<a href="?kosu=%s#oynatici" data-kosu="%s" data-t="0"><title>%s</title>%s</a>' % (kid, kid, esc(bas), sek))
        else:
            s.append('<g><title>%s</title>%s</g>' % (esc(bas), sek))
    uzv = any(n["kume"] == "uzatilmis" for n in N)
    s.append('</svg><figcaption class="not"><span class="lj"><svg width="12" height="12"><circle class="g-iyi" cx="6" cy="6" r="4.6"/></svg> sınama, çıktı</span> '
             '<span class="lj"><svg width="12" height="12"><rect class="g-gel" x="2" y="2" width="8" height="8"/></svg> geliştirme, çıktı</span> '
             '%s<span class="lj"><svg width="12" height="12"><path class="g-kotu" d="M2 2l8 8m0 -8l-8 8"/></svg> çıkamadı (bitiş anında)</span> '
             '<span class="lj"><svg width="22" height="12"><line class="g-ref" x1="1" y1="11" x2="21" y2="1"/></svg> yalnız çözüm yolu</span><br>'
             'v2 beyni, ilk koşular; her nokta bir koşu, aynı labirentin tohumları yan yana. Uzatılmışta yalnız 15 dakikayı aşanlar çizildi. Noktaya tıklayınca oynatıcıda açılır.</figcaption></figure>' % (
                 '<span class="lj"><svg width="12" height="12"><path class="g-uza" d="M6 0.5l5.5 5.5l-5.5 5.5l-5.5 -5.5z"/></svg> uzatılmış (30 dk), çıktı</span> '
                 if uzv else ""))
    return "".join(s)


def karsilastirma_html(oz, emb):
    s = []
    satir = []
    for km in ("sinama", "gelistirme"):
        a, b = mj_sec(oz, "v1", km), mj_sec(oz, "v2", km)
        if not a and not b:
            continue
        oa, ob = basari_ozet(a), basari_ozet(b)
        da = {(r["sahne"], str(r["tohum"])): r for r in a}
        cift = [(da[(r["sahne"], str(r["tohum"]))], r) for r in b if (r["sahne"], str(r["tohum"])) in da]
        ora = [ffloat(y.get("sure_s")) / ffloat(x.get("sure_s")) for x, y in cift
               if x.get("durum") == "basari" and y.get("durum") == "basari" and ffloat(x.get("sure_s"))]
        fark = [(x, y) for x, y in cift if x.get("durum") != y.get("durum")]
        satir.append((km, oa, ob, ora, fark))
    if not satir:
        return '<p class="yok">Henüz yok: v1 / v2 sonuç dosyaları bulunamadı.</p>'
    s.append('<div class="tablo-sar"><table><thead><tr><th>Küme</th><th class="sag">v1 başarı</th><th class="sag">v2 başarı</th>'
             '<th class="sag">Çarpma<br><small>v1 / v2</small></th><th class="sag">Ortalama puan<br><small>v1 / v2</small></th>'
             '<th class="sag">Süre v2 / v1<br><small>ikisi de çıktı: ortalama · ortanca</small></th><th>Sonucu değişen koşular</th></tr></thead><tbody>')
    for km, oa, ob, ora, fark in satir:
        fl = []
        for x, y in fark:
            fl.append("%s t%s: v1 %s → v2 %s" % (kisa_sahne(x["sahne"]), x["tohum"],
                                                 oyna_link(emb, anahtar_r(x), DURUM_AD.get(x["durum"], x["durum"])),
                                                 oyna_link(emb, anahtar_r(y), DURUM_AD.get(y["durum"], y["durum"]))))
        s.append('<tr><th scope="row"><span class="etiket e-mj">MuJoCo</span> %s</th><td class="sag">%s</td><td class="sag">%s</td><td class="sag">%d / %d</td>'
                 '<td class="sag">%s / %s</td><td class="sag">%s · %s <small>(%d çift)</small></td><td>%s</td></tr>' % (
                     KUME_AD[km], oran_span(oa["basari"], oa["n"]), oran_span(ob["basari"], ob["n"]), oa["carpma"], ob["carpma"],
                     fnum(oa["puan_ort"], 0), fnum(ob["puan_ort"], 0),
                     fnum(sum(ora) / len(ora), 2) if ora else "-", fnum(ortanca(ora), 2) if ora else "-", len(ora),
                     "; ".join(fl) if fl else '<span class="soluk">yok</span>'))
    if oz.get("b2_v1") and oz.get("b2_v2"):
        a, b = basari_ozet(oz["b2_v1"]), basari_ozet(oz["b2_v2"])
        da = {(r["sahne"], str(r["tohum"])): r for r in oz["b2_v1"]}
        ora = [ffloat(r["sure_s"]) / ffloat(da[(r["sahne"], str(r["tohum"]))]["sure_s"]) for r in oz["b2_v2"]
               if (r["sahne"], str(r["tohum"])) in da and r.get("durum") == "basari" and da[(r["sahne"], str(r["tohum"]))].get("durum") == "basari"]
        s.append('<tr><th scope="row"><span class="etiket e-2b">2B</span> geliştirme</th><td class="sag">%s</td><td class="sag">%s</td>'
                 '<td class="sag">%d / %d</td><td class="sag">%s / %s</td><td class="sag">%s · %s <small>(%d çift)</small></td>'
                 '<td><span class="soluk">2B kaydı yok</span></td></tr>' % (
                     oran_span(a["basari"], a["n"]), oran_span(b["basari"], b["n"]), a["carpma"], b["carpma"],
                     fnum(a["puan_ort"], 0), fnum(b["puan_ort"], 0), fnum(sum(ora) / len(ora), 2) if ora else "-",
                     fnum(ortanca(ora), 2) if ora else "-", len(ora)))
    s.append('</tbody></table></div>')
    sn = [x for x in satir if x[0] == "sinama"]
    if sn:
        km, oa, ob, ora, fark = sn[0]
        kazanc = (1 - ortanca(ora)) * 100 if ora else None
        s.append('<p><b>Kazanç küçük.</b> v2 yalnız hız profilini değiştirir: önü 1 m ve yanları açık, dönüşten 1,5 s geçmişse '
                 '0,39 m/s, değilse v1 gibi 0,25 m/s. Sınamada başarı %d/%d → %d/%d, iki sürümde de çıkan koşularda süre ortanca '
                 '%%%s kısa; çarpma artmadı. Geliştirme kümesinde v2 bir koşu az çıktı. v2\'yi varsayılan yapma kararı sınama '
                 'sonucuna bakılarak verildi (kural: sınamada başarı azalmasın, çarpma artmasın); ayar sınama labirentlerinde yapılmadı.</p>' % (
                     oa["basari"], oa["n"], ob["basari"], ob["n"], fnum(kazanc, 0) if kazanc is not None else "-"))
    return "".join(s)


def hafiza_mj_html(oz, emb):
    H = mj_sec(oz, None, None, "hafiza")
    if not H:
        return '<p class="yok">Henüz yok: hafızalı MuJoCo koşusu bulunamadı.</p>'
    s = ['<div class="tablo-sar"><table><thead><tr><th>Labirent</th><th class="sag">Tohum</th><th class="sag">Çözüm yolu</th>'
         '<th class="sag">İlk koşu</th><th class="sag">Hafızalı koşu</th><th class="sag">Kazanç</th><th>İzle</th></tr></thead><tbody>']
    kz = []
    for r in sorted(H, key=lambda r: (boyut_of(r["sahne"]), r["sahne"], str(r["tohum"]))):
        a = anahtar_r(r)
        i = oz["mj_satir"].get((a[0], a[1], "ilk", a[3], a[4]))
        g = None
        if i and i.get("durum") == "basari" and r.get("durum") == "basari":
            g = 1 - ffloat(r["sure_s"]) / ffloat(i["sure_s"])
            kz.append(g)
        s.append('<tr><th scope="row">%s</th><td class="sag">%s</td><td class="sag">%s m</td><td class="sag">%s</td><td class="sag">%s</td>'
                 '<td class="sag">%s</td><td>%s · %s</td></tr>' % (
                     esc(kisa_sahne(r["sahne"])), esc(r["tohum"]), fnum(cozum_m(r["sahne"]), 0),
                     (rozet(i.get("durum")) + " " + fsure(ffloat(i.get("sure_s")))) if i else "-",
                     rozet(r.get("durum")) + " " + fsure(ffloat(r.get("sure_s"))),
                     (("−%%%s" if g < -0.005 else "%%%s") % fnum(abs(100 * g), 0)) if g is not None else "-",
                     oyna_link(emb, (a[0], a[1], "ilk", a[3], a[4]), "▶ ilk"), oyna_link(emb, a, "▶ hafızalı")))
    s.append('</tbody></table></div>')
    b = basari_ozet(H)
    s.insert(0, '<p>Robot aynı labirente, ilk koşuda çıkardığı harita ve bulduğu çıkışla yeniden girer (yalnız ilk koşusu '
                'başarılı olanlar; v2, sınama kümesi). <b>%d/%d çıktı</b>, çarpma %d; süre kazancı ortalama <b>%%%s</b> (%s). '
                'Oynatıcıda iki koşu arasında tek tıkla geçebilirsin.</p>' % (
                    b["basari"], b["n"], b["carpma"], fnum(100 * sum(kz) / len(kz), 0) if kz else "-",
                    ("%%%s … %%%s" % (fnum(100 * min(kz), 0), fnum(100 * max(kz), 0))).replace("%-", "−%") if kz else "-"))
    return "".join(s)


def uzatilmis_html(oz, emb, uz):
    R = uz["satirlar"]
    if not R:
        return '<p class="yok">%s</p>' % ("Henüz yok: ölçüm rapor üretilirken bitmemişti." if uz["basladi"] else "Henüz yok.")
    s = ['<div class="tablo-sar"><table><thead><tr><th>Labirent</th><th class="sag">Tohum</th><th class="sag">Çözüm yolu</th>'
         '<th>15 dakikalık kuralla</th><th>30 dakika verilince</th><th class="sag">FINISH\'e en çok</th><th>İzle</th></tr></thead><tbody>']
    for r in sorted(R, key=lambda r: (boyut_of(r["sahne"]), r["sahne"], str(r["tohum"]))):
        a = anahtar_r(r)
        on = None
        for km in ("sinama", "gelistirme"):
            on = oz["mj_satir"].get((a[0], km, "ilk", a[3], a[4]))
            if on:
                break
        s.append('<tr><th scope="row">%s</th><td class="sag">%s</td><td class="sag">%s m</td><td>%s</td><td>%s</td><td class="sag">%%%s</td><td>%s</td></tr>' % (
            esc(kisa_sahne(r["sahne"])), esc(r["tohum"]), fnum(cozum_m(r["sahne"]), 0),
            (rozet(on.get("durum")) + " " + fsure(ffloat(on.get("sure_s"))) + " " + oyna_link(emb, anahtar_r(on), "▶")) if on else '<span class="soluk">eşi yok</span>',
            rozet(r.get("durum")) + " " + fsure(ffloat(r.get("sure_s"))) + (
                (' <small>%s</small>' % esc({"ilerlemesiz": "300 s yeni hücreye girmedi", "hareketsiz": "60 s yerinden ayrılmadı"}.get(
                    r.get("sikisma_sebebi"), r.get("sikisma_sebebi")))) if r.get("sikisma_sebebi") else ""),
            fnum(100 * (ffloat(r.get("p_en")) or 0), 0),
            oyna_link(emb, a, "▶ 30 dk koşusu")))
    s.append('</tbody></table></div>')
    b = [r for r in R if r.get("durum") == "basari"]
    on_kotu = []
    for r in R:
        for km in ("sinama", "gelistirme"):
            x = oz["mj_satir"].get((r["_surum"], km, "ilk", r["sahne"], str(r["tohum"])))
            if x:
                if x.get("durum") != "basari":
                    on_kotu.append(r)
                break
    s.insert(0, '<p>v2 beyni, tohum 0, süre sınırı 30:00. 30 dakikada çıkan: <b>%d/%d</b>.%s Bu koşular kuralın dışında: üstteki 15 dakikalık sayılara, '
                'puana ve başarı oranlarına <b>karışmaz</b>. Sorulan yalnız şu: süre yetse bu beyin bu labirentleri çözer mi? '
                '%s</p>' % (
                    len(b), len(R), "" if uz["bitti"] else " <b>Ölçüm rapor üretilirken bitmemişti</b>; tablo o anki dosyadan.",
                    "Yanıt: 15 dakikada çıkamayan %d koşudan %d tanesinde evet; %d tanesinde hayır (%s)." % (
                        len(on_kotu), len([r for r in on_kotu if r.get("durum") == "basari"]),
                        len([r for r in on_kotu if r.get("durum") != "basari"]),
                        ", ".join(sorted({DURUM_AD.get(r.get("durum"), r.get("durum")) for r in on_kotu if r.get("durum") != "basari"})) or "-")
                    if on_kotu else ""))
    return "".join(s)


def ayrinti_html(oz):
    s = []
    for km in ("sinama", "gelistirme"):
        for sv in oz["surumler"]:
            rs = mj_sec(oz, sv, km)
            if rs:
                s.append('<h4><span class="etiket e-mj">MuJoCo %s</span> %s kümesi, boyuta göre</h4>' % (sv, KUME_AD[km]))
                s.append(tablo_boyut(grup_ozet(rs, boyut_anahtari), ""))
    s.append('<h4><span class="etiket e-2b">2B benzetici</span> keşif, v1, boyuta göre</h4>')
    s.append(tablo_boyut(oz["b2_kesif"], "Kaynak: <code>kesif/sonuc/ilk.csv</code>, dönüş fazlası %14, 5 tohum. Bu koşuların kaydı yok."))
    return "".join(s)


# ------------------------------------------------------------------ ana
def uzatilmis_durum(oz):
    satirlar = [r for r in oz["mj"] if r["_kume"] == "uzatilmis"]
    bitti, basladi = False, bool(satirlar) or any(a.startswith("mujoco_uzatilmis") for a in oz["kaynak"])
    try:
        with open(os.path.join(KESIF, ".durum"), encoding="utf-8", errors="replace") as f:
            for satir in f:
                s = satir.lower()
                if "uzatilmis" in s:
                    basladi = True
                    if "uzatilmis bitti" in s:
                        bitti = True
    except OSError:
        pass
    return {"satirlar": satirlar, "bitti": bitti, "basladi": basladi}


def kosu_kimligi(b, ad):
    if b["tur"] != "labirent":
        return "kr-" + re.sub(r"[^A-Za-z0-9_\-]", "_", ad)
    return "%s-%s-%s_t%s%s" % (b["surum"], b["kume"][:3], b["sahne"].replace("labirent_", ""), b["tohum"],
                               "-h" if b["kos"] == "hafiza" else "")


def anahtar_k(k):
    return (k["surum"], k["kume"], k["kos"], k["sahne"], str(k["tohum"]))


def oncelikler(lab):
    """0 zorunlu, 1 v1/v2 farkı, 2 v1 örnekleri, 3 kalan v2, 4 kalan v1."""
    P = {}
    d = {anahtar_k(k): k for k in lab}
    for k in lab:
        if k["kume"] == "uzatilmis" or (k["kume"] == "sinama" and k["surum"] == "v2") or k.get("durum") != "basari":
            P[k["id"]] = 0
        else:
            P[k["id"]] = 3 if k["surum"] != "v1" else 4
    son = "v2" if any(k["surum"] == "v2" for k in lab) else "v1"
    temsil = []
    for b in sorted({boyut_of(k["sahne"]) for k in lab}):
        L = sorted([k for k in lab if k["surum"] == son and k["kume"] == "gelistirme" and k["kos"] == "ilk"
                    and k.get("durum") == "basari" and boyut_of(k["sahne"]) == b], key=lambda k: k["sure_s"] or 0)
        if L:
            k = L[len(L) // 2]
            P[k["id"]] = 0
            temsil.append(k)
    for k in lab:
        if k["surum"] == "v1":
            e = d.get(("v2",) + anahtar_k(k)[1:])
            if e and e.get("durum") != k.get("durum"):
                P[k["id"]] = min(P[k["id"]], 1)
                P[e["id"]] = min(P[e["id"]], 1)
    for k in temsil:
        e = d.get(("v1",) + anahtar_k(k)[1:])
        if e:
            P[e["id"]] = min(P[e["id"]], 2)
    return P


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lidar-hz", type=float, default=2.5, help="gömülen LiDAR tarama sıklığı (Hz)")
    ap.add_argument("--isin-adim", type=int, default=2, help="her kaçıncı ışın")
    ap.add_argument("--butce-mb", type=float, default=19.0, help="sayfa boyutu üst sınırı (MB); sığmayan koşular dışarıda kalır")
    ap.add_argument("--cikti", default=CIKTI)
    ap.add_argument("--onbellek", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    dusuk_oncelik()
    t_bas = time.time()
    durum_yaz("uretim basladi")
    tani = []
    oz = ozetler()
    uz = uzatilmis_durum(oz)
    # ---- kayıtlar
    kayitlar = []
    simdi = time.time()
    atlanan = []
    ham = os.path.join(SONUC, "ham")
    mj_yollar = sorted(y for y in glob.glob(os.path.join(ham, "**", "*.npz"), recursive=True)
                       if "mujoco" in os.path.relpath(y, ham).replace("\\", "/").lower())
    for yol in mj_yollar:
        if simdi - os.path.getmtime(yol) < TAZE_S:
            atlanan.append((os.path.relpath(yol, ham).replace("\\", "/"), "yazılıyor olabilir (çok yeni)"))
            continue
        kayitlar.append(("labirent", yol))
    for yol in sorted(glob.glob(os.path.join(GEZ_KAYIT, "*.npz"))):
        kayitlar.append(("koridor", yol))

    def kos(lidar_hz, isin_adim, yalniz=None):
        kos_list, bloblar = [], {}
        for tur, yol in kayitlar:
            if yalniz is not None and yol not in yalniz:
                continue
            ad = os.path.splitext(os.path.basename(yol))[0]
            try:
                bilgi, sik = kayit_isle(yol, tur, oz["mj_satir"] if tur == "labirent" else None, 1.0 / lidar_hz,
                                        isin_adim, tani)
            except Exception as e:
                atlanan.append((os.path.basename(yol), "okunamadı: %s: %s" % (type(e).__name__, e)))
                continue
            kid = kosu_kimligi(bilgi, ad)
            bilgi["id"] = kid
            bilgi["_yol"] = yol
            if tur == "koridor":
                hj = os.path.join(GEZ_HAM, ad + ".json")
                if os.path.exists(hj):
                    try:
                        bilgi["senaryo"] = json.load(open(hj, encoding="utf-8"))
                    except Exception:
                        pass
            kos_list.append(bilgi)
            bloblar[kid] = base64.b64encode(sik).decode("ascii")
            durum_yaz("kayit %s: %d kare, %.0f kB" % (kid, bilgi["n"], len(sik) / 1024))
        return kos_list, bloblar

    lidar_hz, isin_adim = a.lidar_hz, a.isin_adim
    if a.onbellek and os.path.exists(a.onbellek):          # yalnız geliştirme: şablonu hızlı denemek için
        import pickle
        with open(a.onbellek, "rb") as f:
            kosular, bloblar, tani, atlanan[:], lidar_hz = pickle.load(f)
        durum_yaz("onbellekten okundu (gelistirme)")
    else:
        kosular, bloblar = kos(lidar_hz, isin_adim)
        if a.onbellek:
            import pickle
            with open(a.onbellek, "wb") as f:
                pickle.dump((kosular, bloblar, tani, list(atlanan), lidar_hz), f)
    # ---- bütçe: zorunlu koşular sığmazsa LiDAR seyrelir; sonra öncelik sırasıyla doldurulur
    butce = a.butce_mb * 1e6 - 0.45e6          # şablon, sahneler, tablolar için pay

    def boyut(k):
        return len(bloblar[k["id"]]) + len(json.dumps({x: v for x, v in k.items() if x != "_yol"}, ensure_ascii=False)) + 80

    while True:
        lab = [k for k in kosular if k["tur"] == "labirent"]
        P = oncelikler(lab)
        zorunlu = [k for k in kosular if k["tur"] != "labirent" or P[k["id"]] == 0]
        if sum(boyut(k) for k in zorunlu) <= butce or lidar_hz <= 0.6:
            break
        lidar_hz /= 2
        durum_yaz("zorunlu kosular butceyi asiyor: LiDAR %.2f Hz'e dusuruluyor" % lidar_hz)
        atlanan.clear()
        tani.clear()
        kosular, bloblar = kos(lidar_hz, isin_adim)
    secili = list(zorunlu)
    kullan = sum(boyut(k) for k in secili)
    disarida = []
    for p in (1, 2, 3, 4):
        aday = [k for k in lab if P[k["id"]] == p]
        while aday:
            say = {}
            for k in secili:
                say[(k.get("surum"), k["sahne"])] = say.get((k.get("surum"), k["sahne"]), 0) + 1
            aday.sort(key=lambda k: (say.get((k["surum"], k["sahne"]), 0), -boyut_of(k["sahne"])[0], k["sahne"], str(k["tohum"])))
            k = aday.pop(0)
            if kullan + boyut(k) <= butce:
                secili.append(k)
                kullan += boyut(k)
            else:
                disarida.append(k)
    sec_id = {k["id"] for k in secili}
    kosular = [k for k in kosular if k["id"] in sec_id]
    bloblar = {i: b for i, b in bloblar.items() if i in sec_id}
    for k in kosular:
        k.pop("_yol", None)
    dis_ozet = [{"id": k["id"], "surum": k["surum"], "kume": k["kume"], "kos": k["kos"], "sahne": k["sahne"], "tohum": k["tohum"],
                 "durum": k.get("durum"), "sure_s": k.get("sure_s")} for k in disarida]
    # koridor: ek engeller meta'dan
    for k in kosular:
        if k["tur"] == "koridor":
            try:
                with np.load(os.path.join(GEZ_KAYIT, k["dosya"]), allow_pickle=False) as zz:
                    mm = json.loads(str(zz["meta"]))
                k["ek_engeller"] = mm.get("ek_engeller") or []
                k["koridor_sonuc"] = {kk: mm.get("sonuc", {}).get(kk) for kk in ("sure_s", "yol_m", "temas_olay", "bitis")}
            except Exception:
                pass
    sahneler = {k["sahne"]: sahne_bilgisi(k["sahne"]) for k in kosular}
    lab = [k for k in kosular if k["tur"] == "labirent"]
    emb = {anahtar_k(k): k["id"] for k in lab}
    es2b = {(m["sahne"], str(m["tohum"])): b for m, b in oz["eslesik"]}
    for k in lab:
        k["neden"] = neden_mj(k, es2b.get((k["sahne"], str(k["tohum"]))) if (k["surum"], k["kume"]) == ("v1", "gelistirme") else None)
        e = emb.get((k["surum"], k["kume"], "hafiza" if k["kos"] == "ilk" else "ilk", k["sahne"], str(k["tohum"])))
        if e:
            k["es_kos"] = e
        for s2 in ("v1", "v2"):
            if s2 != k["surum"]:
                e = emb.get((s2,) + anahtar_k(k)[1:])
                if e:
                    k["es_surum"] = e
    # ---- varsayılan koşu ve kısayollar (v2)
    son = "v2" if any(k["surum"] == "v2" for k in lab) else "v1"
    v2l = [k for k in lab if k["surum"] == son and k["kume"] != "uzatilmis"]
    v2i = [k for k in v2l if k["kos"] == "ilk"]
    bas = [k for k in v2i if k.get("durum") == "basari"]
    sin_bas = [k for k in bas if k["kume"] == "sinama"] or bas
    varsayilan = None
    ilginc = []
    if sin_bas:
        k = max(sin_bas, key=lambda k: (boyut_of(k["sahne"]), sahneler[k["sahne"]].get("cozum_m") or 0, -(k["sure_s"] or 0)))
        varsayilan = k["id"]
        ilginc.append({"id": k["id"], "t": 0, "ad": "Hiç görmediği %s'de çıkış" % boyut_ad(boyut_of(k["sahne"])),
                       "not": "%s, çözüm %s m, %s" % (kisa_sahne(k["sahne"]), fnum(sahneler[k["sahne"]].get("cozum_m"), 0), fsure(k["sure_s"]))})
    if bas:
        k = min(bas, key=lambda k: k["sure_s"])
        ilginc.append({"id": k["id"], "t": 0, "ad": "En hızlı başarı", "not": "%s, %s" % (kisa_sahne(k["sahne"]), fsure(k["sure_s"]))})
    hz = []
    for k in v2l:
        if k["kos"] == "hafiza" and k.get("durum") == "basari" and k.get("es_kos"):
            i = next((x for x in lab if x["id"] == k["es_kos"]), None)
            if i and i.get("durum") == "basari" and i.get("sure_s"):
                hz.append((1 - k["sure_s"] / i["sure_s"], k, i))
    if hz:
        g, k, i = max(hz, key=lambda x: x[0])
        ilginc.append({"id": k["id"], "t": 0, "ad": "Hafızalı koşu, en büyük kazanç",
                       "not": "%s: %s → %s (%%%s)" % (kisa_sahne(k["sahne"]), fsure(i["sure_s"]), fsure(k["sure_s"]), fnum(100 * g, 0))})
    for d in ("fail_sure", "fail_sikisma", "fail_start"):
        L = [k for k in v2i if k.get("durum") == d]
        if L:
            k = max(L, key=lambda k: k.get("p_en") or 0)
            ilginc.append({"id": k["id"], "t": max(0, (k.get("p_en_an") or 0) - 20), "ad": "Çıkamadı: " + DURUM_AD[d],
                           "not": "%s, FINISH'e %%%s yaklaştı" % (kisa_sahne(k["sahne"]), fnum(100 * (k.get("p_en") or 0), 0))})
    v1v2 = [k for k in lab if k["surum"] == "v1" and k.get("durum") == "basari" and k.get("es_surum")
            and next((x for x in lab if x["id"] == k["es_surum"]), {}).get("durum") != "basari"]
    if v1v2:
        k = v1v2[0]
        ilginc.append({"id": k["id"], "t": 0, "ad": "v1 çıktı, v2 çıkamadı", "not": "%s t%s, %s" % (kisa_sahne(k["sahne"]), k["tohum"], KUME_AD[k["kume"]])})
    uzb = [k for k in lab if k["kume"] == "uzatilmis" and k.get("durum") == "basari"]
    if uzb:
        k = max(uzb, key=lambda k: k["sure_s"] or 0)
        ilginc.append({"id": k["id"], "t": max(0, T_SINIR - 30), "ad": "30 dakikada çıktı (kural dışı)",
                       "not": "%s, %s; 15:00'tan 30 s önceden" % (kisa_sahne(k["sahne"]), fsure(k["sure_s"]))})
    # ---- tanılar
    ilk_fark = [k["ilk_kare_hayalet_fark_m"] for k in lab if k.get("ilk_kare_hayalet_fark_m") is not None]
    uyumsuz = [(k["id"], u) for k in lab for u in k.get("uyumsuz", [])]
    lidar_uz = [k["lidar"].get("duvar_uzaklik_cm") for k in lab if k.get("lidar") and k["lidar"].get("duvar_uzaklik_cm") is not None]
    lidar_uz0 = [k["lidar"].get("duvar_uzaklik_kaymasiz_cm") for k in lab if k.get("lidar") and k["lidar"].get("duvar_uzaklik_kaymasiz_cm") is not None]
    kay_t = [k["lidar"]["kayma_s"] for k in lab if k.get("lidar") and k["lidar"].get("kayma_kaynak") == "tahmin"]
    kay_k = [k["lidar"]["kayma_s"] for k in lab if k.get("lidar") and k["lidar"].get("kayma_kaynak") != "tahmin"]
    tanilar = {
        "ilk_kare_fark_maks_cm": round(100 * max(ilk_fark), 2) if ilk_fark else None,
        "lidar_duvar_ortanca_cm": round(statistics.median(lidar_uz), 1) if lidar_uz else None,
        "lidar_duvar_kaymasiz_cm": round(statistics.median(lidar_uz0), 1) if lidar_uz0 else None,
        "lidar_duvar_maks_cm": max(lidar_uz) if lidar_uz else None,
        "lidar_kayma_tahmin": ("%d eski kayıtta tahmin: %s…%s s" % (len(kay_t), fnum(min(kay_t), 2), fnum(max(kay_t), 2))) if kay_t else None,
        "lidar_kayma_kayit": ("%d kayıtta kayıttan (t0_dunya_s): %s s" % (len(kay_k), _orta_aralik(kay_k, 2))) if kay_k else None,
        "uyumsuz": uyumsuz, "atlanan": atlanan, "notlar": tani, "lidar_hz": lidar_hz, "isin_adim": isin_adim,
        "hakem_tutan": sum(1 for k in lab if not [u for u in k.get("uyumsuz", []) if "hakem" in u or "puan" in u]),
        "hakem_toplam": len(lab), "sinir_kayit": sum(1 for k in lab if k.get("sinir")),
    }
    # ---- HTML
    say = {}
    for k in lab:
        say[(k["kume"], k["surum"], k["kos"])] = say.get((k["kume"], k["surum"], k["kos"]), 0) + 1
    toplam_csv = {}
    for r in oz["mj"]:
        toplam_csv[(r["_kume"], r["_surum"], r["_kos"])] = toplam_csv.get((r["_kume"], r["_surum"], r["_kos"]), 0) + 1
    gomulu = []
    for key in sorted(set(say) | set(toplam_csv), key=lambda x: (KUME_SIRA.get(x[0], 9), x[1], x[2])):
        gomulu.append({"kume": key[0], "surum": key[1], "kos": key[2], "gomulu": say.get(key, 0), "csv": toplam_csv.get(key, 0)})
    veri = {
        "uretim": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "T": T_SINIR, "kosular": kosular, "sahneler": sahneler, "ilginc": ilginc, "tani": tanilar,
        "strateji_ad": STRATEJI_AD, "durum_ad": DURUM_AD, "kume_ad": KUME_AD, "kos_ad": KOS_AD,
        "varsayilan": varsayilan, "disarida": dis_ozet, "gomulu": gomulu, "uz_bitti": uz["bitti"], "uz_basladi": uz["basladi"],
    }
    kaynak = oz["kaynak"]
    kaynak_html = ", ".join("<code>%s</code> %s" % (ad, ("(%s, %d satır)" % (v["zaman"], v["satir"])) if v else "(yok)")
                            for ad, v in kaynak.items())
    parcalar = {
        "URETIM": veri["uretim"],
        "KAYNAKLAR": kaynak_html,
        "HUKUM": hukum_html(oz),
        "NEDEN": neden_html(oz, emb, uz),
        "KARSILASTIRMA": karsilastirma_html(oz, emb),
        "HAFIZA_MJ": hafiza_mj_html(oz, emb),
        "UZATILMIS": uzatilmis_html(oz, emb, uz),
        "AYRINTI": ayrinti_html(oz),
        "TABLO_STRATEJI": tablo_strateji(oz["strateji"]),
        "TABLO_HAFIZA": tablo_hafiza(oz["hafiza"]),
        "TABLO_ODOMETRI": tablo_odometri(oz["odometri"]),
        "TABLO_ESLESIK": tablo_eslesik(oz["eslesik"]),
        "BASARISIZ_2B": b2_basarisiz_html(oz["b2_basarisiz"]),
    }
    sab = open(SABLON, encoding="utf-8").read()
    for k, v in parcalar.items():
        sab = sab.replace("<!--%s-->" % k, v)
    js_veri = json.dumps(veri, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    sab = sab.replace("/*__VERI__*/null", js_veri)
    blob_html = "\n".join('<script type="application/octet-stream" id="b-%s">%s</script>' % (k, v) for k, v in bloblar.items())
    sab = sab.replace("<!--BLOBLAR-->", blob_html)
    gecici = a.cikti + ".tmp"
    with open(gecici, "w", encoding="utf-8", newline="\n") as f:
        f.write(sab)
    os.replace(gecici, a.cikti)
    mb = os.path.getsize(a.cikti) / 1e6
    durum_yaz("uretim bitti: %s, %.2f MB, %d kosu gomulu (%d labirent, %d koridor), %d disarida, %.0f s, lidar %.2f Hz" % (
        os.path.basename(a.cikti), mb, len(kosular), len(lab), len(kosular) - len(lab), len(disarida), time.time() - t_bas, lidar_hz))
    durum_yaz("gomulu/csv: %s" % ", ".join("%s %s %s %d/%d" % (g["kume"], g["surum"], g["kos"], g["gomulu"], g["csv"]) for g in gomulu))
    if atlanan:
        durum_yaz("atlanan: %s" % atlanan)
    if uyumsuz:
        durum_yaz("uyumsuz: %s" % uyumsuz)
    durum_yaz("tani: ilk kare hayalet farki maks %s cm, lidar-duvar ortanca %s cm (maks %s); uzatilmis %d satir, bitti=%s" % (
        tanilar["ilk_kare_fark_maks_cm"], tanilar["lidar_duvar_ortanca_cm"], tanilar["lidar_duvar_maks_cm"], len(uz["satirlar"]), uz["bitti"]))


def neden_mj(k, b2):
    """Başarısız MuJoCo koşusu için tek satır neden (hakem sonucu + sonuç CSV'sindeki beyin olayları)."""
    d = k.get("durum")
    if d == "basari":
        return ""
    p = []
    if d == "fail_sure":
        p.append("%s doldu, FINISH'ten çıkamadı." % fsure(k.get("T") or T_SINIR))
    elif d == "fail_sikisma":
        p.append({"ilerlemesiz": "Sıkıştı: 300 s boyunca yeni hücreye girmedi.",
                  "hareketsiz": "Sıkıştı: 60 s boyunca yerinden 0,2 m'den fazla ayrılmadı."}.get(k.get("sebep"), "Sıkıştı."))
    elif d == "fail_start":
        p.append("START çizgisinden geri çıktı.")
    else:
        p.append("Durum: %s." % d)
    if k.get("p_en") is not None:
        p.append("FINISH'e en çok %%%s yaklaştı (labirent içi yol uzaklığıyla), en yakın an %s." % (
            fnum(100 * k["p_en"], 0), fsure(k.get("p_en_an"))))
    if k.get("hucre") is not None:
        p.append("%s/%s hücre gezildi, %s m yol." % (k["hucre"], k.get("toplam_hucre"), fnum(k.get("yol_m"), 0)))
    if k.get("son_mod_csv"):
        p.append("Son mod: %s." % MOD_AD.get(k["son_mod_csv"], k["son_mod_csv"]))
    if k.get("kurtarma") not in (None, "", "0"):
        p.append("Kurtarma %s kez." % k["kurtarma"])
    if k.get("carpma"):
        p.append("%d çarpma." % k["carpma"])
    if b2 is not None:
        if b2.get("durum") == "basari":
            p.append("Aynı labirent ve tohum 2B benzeticide %s'te çözüldü." % fsure(ffloat(b2.get("sure_s"))))
        else:
            p.append("2B benzeticide de çözülemedi (%s)." % DURUM_AD.get(b2.get("durum"), b2.get("durum")))
    return " ".join(p)


def kpi_html(rows):
    if not rows:
        return '<div class="kpi yok-kpi"><div class="kpi-d">henüz yok</div><div class="kpi-a">MuJoCo sonuç dosyası bulunamadı</div></div>'
    bas = [r for r in rows if r.get("durum") == "basari"]
    sure = ortanca([ffloat(r.get("sure_s")) for r in bas])
    carp = sum(int(float(r.get("carpma_sayisi") or 0)) for r in rows)
    puan = ortanca([ffloat(r.get("puan")) for r in rows])
    return ('<div class="kpi"><div class="kpi-d">%d/%d</div><div class="kpi-a">MuJoCo koşusu FINISH\'ten çıktı (%%%s)</div></div>'
            % (len(bas), len(rows), fnum(100.0 * len(bas) / len(rows), 0))
            + '<div class="kpi"><div class="kpi-d">%s</div><div class="kpi-a">ortanca süre, başarılı koşular (15:00\'a oranla %%%s)</div></div>'
            % (fsure(sure), fnum(100 * sure / T_SINIR, 0) if sure else "-")
            + '<div class="kpi"><div class="kpi-d">%d</div><div class="kpi-a">çarpma, tüm MuJoCo koşularında toplam</div></div>' % carp
            + '<div class="kpi"><div class="kpi-d">%s</div><div class="kpi-a">ortanca puan (tek tur, en çok 1500)</div></div>' % fnum(puan, 0))


if __name__ == "__main__":
    main()
