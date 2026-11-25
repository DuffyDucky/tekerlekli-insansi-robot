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


def kume_bul(sahne, satir=None, meta=None):
    """Küme: açık 'kume' alanı varsa o; yoksa labirent tohumu t1–t3 geliştirme (beyin bunlarla ayarlandı), t4+ sınama."""
    for src in (satir or {}, meta or {}):
        v = str(src.get("kume") or src.get("küme") or "").strip().lower()
        if v:
            return "sınama" if v.startswith(("sin", "sın", "test")) else ("geliştirme" if v.startswith(("gel", "dev")) else v)
    m = re.search(r"_t(\d+)$", sahne or "")
    return "sınama" if (m and int(m.group(1)) >= 4) else "geliştirme"


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


def hakem_oynat(ad, t, g, temas):
    """Kayıttaki yer gerçeğiyle hakemi yeniden koştur: adım adım p_en, çarpma, gezilen hücre (anlık puan için)."""
    H = hakem_sinifi()(ad, sure_siniri_s=T_SINIR)
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
    csv_satir = None
    if csv_tablo is not None:
        csv_satir = csv_tablo.get((surum, ad, str(meta.get("tohum"))))
        if csv_satir is None:            # 'kayit' sütunu (tam ya da göreli yol) dosya adıyla eşleşiyorsa
            for r in csv_tablo.values():
                kr = (r.get("kayit") or "").replace("\\", "/")
                if kr and kr.rsplit("/", 1)[-1] == os.path.basename(yol) and r["_surum"] == surum:
                    csv_satir = r
                    break
        if csv_satir is not None and csv_satir.get("_surum") != surum:
            csv_satir = None
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
        hs, pen, carp, cs, hucre = hakem_oynat(ad, t, g, temas)
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
        try:
            kayma, uz_kayma = lidar_kayma_bul(sb, t, g, tt, mm, ac, mon3, dts)
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
              "kayma_s": round(kayma, 3), "duvar_uzaklik_kaymasiz_cm": None if uz_kayma is None else uz_kayma[0],
              "duvar_uzaklik_cm": None if uz_kayma is None else uz_kayma[1]}
    ham, sik = P.bayt()
    hakem_kayit_durum = hs_kayit.get("durum") or ((("fail_sure") if float((meta.get("sonuc") or {}).get("sure_s") or 0) >= T_SINIR - 0.2 else None) if tur == "labirent" else None)
    bilgi = {
        "tur": tur, "sahne": ad, "tohum": meta.get("tohum"), "dosya": goreli.replace("\\", "/"),
        "surum": surum if tur == "labirent" else None,
        "kume": kume_bul(ad, satir=csv_satir, meta=meta) if tur == "labirent" else None,
        "kayit_zamani": datetime.datetime.fromtimestamp(os.path.getmtime(yol)).strftime("%Y-%m-%d %H:%M"),
        "baslangic": list(start), "cerceve": "baslangic" if cerceve_bas else "dunya", "modlar": [MOD_AD.get(m, m) for m in modlar],
        "n": int(len(sec)), "sure": round(float(t[-1]), 2), "paket": P.baslik, "harita": hbilgi, "lidar": lb,
        "cikis": cikis, "ilk_kare_hayalet_fark_m": None if ilk_fark is None else round(ilk_fark, 4),
        "poz_hata_maks_m": None if not np.isfinite(e_all).any() else round(float(np.nanmax(e_all)), 3),
        "ham_bayt": len(ham), "sik_bayt": len(sik),
    }
    if tur == "labirent":
        ol = hs.get("olaylar") or []
        bilgi.update({
            "durum": hs.get("durum") or ("fail_sure" if float(t[-1]) >= T_SINIR - 0.2 else None),
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
            bilgi["son_mod_csv"] = csv_satir.get("son_mod")
            bilgi["kurtarma"] = csv_satir.get("kurtarma")
            bilgi["k_don"] = ffloat(csv_satir.get("k_don"))
            bilgi["dogru_duvar"] = ffloat(csv_satir.get("dogru_duvar_orani"))
        else:
            uy.append("CSV'de satırı yok")
        bilgi["uyumsuz"] = uy
    return bilgi, sik


def lidar_kayma_bul(sb, t, g, tt, mm, ac, mon, dts, n_tarama=36):
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


def ozetler():
    kaynak = {}
    out = {"kaynak": kaynak}
    # MuJoCo: mujoco.csv (v1) ve varsa sürümlü eşleri (mujoco_v2.csv ya da 'surum' sütunu)
    mj = []
    mj_dosyalar = sorted(os.path.basename(p) for p in glob.glob(os.path.join(SONUC, "mujoco*.csv")))
    if "mujoco.csv" not in mj_dosyalar:
        mj_dosyalar.insert(0, "mujoco.csv")
    for ad in mj_dosyalar:
        rows, tm = csv_oku(ad)
        kaynak[ad] = None if tm is None else {"zaman": datetime.datetime.fromtimestamp(tm).strftime("%Y-%m-%d %H:%M"),
                                              "satir": len(rows or [])}
        for r in rows or []:
            if ad.startswith("mujoco_2b"):         # 2B karşılaştırma dosyası MuJoCo sonucu değil
                continue
            r = dict(r)
            r["_surum"] = surum_bul(satir=r, yol=ad)
            r["_kume"] = kume_bul(r.get("sahne"), satir=r)
            mj.append(r)
    for ad in [a for a in mj_dosyalar if a.startswith("mujoco_2b")]:
        kaynak.pop(ad, None)
    ilk, it = csv_oku("ilk.csv")
    haf, ht = csv_oku("hafiza.csv")
    odo, ot = csv_oku("odometri.csv")
    for ad, tm, rows in (("ilk.csv", it, ilk), ("hafiza.csv", ht, haf), ("odometri.csv", ot, odo)):
        kaynak[ad] = None if tm is None else {"zaman": datetime.datetime.fromtimestamp(tm).strftime("%Y-%m-%d %H:%M"),
                                              "satir": len(rows or [])}
    mj = tekille(mj, ("_surum", "sahne", "tohum"))
    surumler = sorted({r["_surum"] for r in mj}, key=lambda s: (len(s), s))
    out["surumler"] = surumler
    out["mj_surum"] = {s: [r for r in mj if r["_surum"] == s] for s in surumler}
    ilk = tekille(ilk, ("strateji", "sahne", "tohum", "donus_hata"))
    haf = tekille(haf, ("strateji", "sahne", "tohum", "donus_hata"))
    odo = tekille(odo, ("strateji", "sahne", "tohum", "donus_hata"))
    out["mj_satir"] = {(r["_surum"], r["sahne"], str(r["tohum"])): r for r in mj}
    # sürüm -> küme -> boyut grupları (küme sırası: geliştirme, sınama)
    out["mujoco"] = {s: {k: grup_ozet([r for r in rs if r["_kume"] == k], boyut_anahtari)
                         for k in sorted({r["_kume"] for r in rs}, key=lambda k: (k != "geliştirme", k))}
                     for s, rs in out["mj_surum"].items()}
    out["mujoco_n"] = len(mj)
    kesif2b = [r for r in ilk if r.get("strateji") == "kesif"]
    out["b2_kesif"] = grup_ozet(kesif2b, boyut_anahtari) if kesif2b else None
    out["strateji"] = grup_ozet(ilk, lambda r: (r.get("strateji"), boyut_of(r.get("sahne")))) if ilk else None
    # odometri tablosu: %0 / %25 odometri.csv'den, %14 (varsayılan) ilk turun keşif satırlarından
    odo_tum = list(odo or []) + [r for r in ilk if r.get("strateji") == "kesif"]
    out["odometri"] = grup_ozet(odo_tum, lambda r: (ffloat(r.get("donus_hata")) or 0.0, boyut_of(r.get("sahne")))) if odo else None
    # hafızalı ek tur
    hz = []
    for r in haf or []:
        hz.append({"sahne": r["sahne"], "tohum": r["tohum"], "ilk_durum": r.get("durum"), "ilk_sure": ffloat(r.get("sure_s")),
                   "haf_durum": r.get("hafiza_durum") or None, "haf_sure": ffloat(r.get("hafiza_sure_s")),
                   "haf_puan": ffloat(r.get("hafiza_puan"))})
    out["hafiza"] = sorted(hz, key=lambda r: (boyut_of(r["sahne"]), r["sahne"], str(r["tohum"])))
    # 2B'de aynı labirent + tohum (MuJoCo ile karşılaştırma)
    k2 = {(r["sahne"], str(r["tohum"])): r for r in kesif2b}
    es = []
    for r in out["mj_surum"].get("v1", []):          # 2B koşuları v1 beyniyle

        b = k2.get((r["sahne"], str(r["tohum"])))
        if b:
            es.append((r, b))
    out["eslesik"] = es
    # başarısızlıklar (2B, kayıtsız)
    b2f = []
    for ad, rows in (("ilk.csv", ilk), ("odometri.csv", odo), ("hafiza.csv", haf)):
        for r in rows or []:
            if r.get("durum") and r.get("durum") != "basari":
                b2f.append(dict(r, _dosya=ad))
    out["b2_basarisiz"] = b2f
    return out


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


# ------------------------------------------------------------------ ana
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lidar-hz", type=float, default=5.0, help="gömülen LiDAR tarama sıklığı (Hz)")
    ap.add_argument("--isin-adim", type=int, default=2, help="her kaçıncı ışın")
    ap.add_argument("--butce-mb", type=float, default=14.5)
    ap.add_argument("--cikti", default=CIKTI)
    ap.add_argument("--onbellek", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    dusuk_oncelik()
    t_bas = time.time()
    durum_yaz("uretim basladi")
    tani = []
    oz = ozetler()
    # ---- kayıtlar
    kayitlar = []
    simdi = time.time()
    atlanan = []
    ham = os.path.join(SONUC, "ham")
    mj_yollar = sorted(y for y in glob.glob(os.path.join(ham, "**", "*.npz"), recursive=True)
                       if "mujoco" in os.path.relpath(y, ham).replace("\\", "/").lower())
    for yol in mj_yollar:
        if simdi - os.path.getmtime(yol) < TAZE_S:
            atlanan.append((os.path.basename(yol), "yazılıyor olabilir (çok yeni)"))
            continue
        kayitlar.append(("labirent", yol))
    kor = sorted(glob.glob(os.path.join(GEZ_KAYIT, "*.npz")))
    for yol in kor:
        kayitlar.append(("koridor", yol))

    def kos(lidar_hz, isin_adim):
        kos_list, bloblar = [], {}
        for tur, yol in kayitlar:
            ad = os.path.splitext(os.path.basename(yol))[0]
            try:
                bilgi, sik = kayit_isle(yol, tur, oz["mj_satir"] if tur == "labirent" else None, 1.0 / lidar_hz,
                                        isin_adim, tani)
            except Exception as e:
                atlanan.append((os.path.basename(yol), "okunamadı: %s: %s" % (type(e).__name__, e)))
                continue
            kid = ("mj-" + ("" if bilgi.get("surum", "v1") == "v1" else bilgi["surum"] + "-")) if tur == "labirent" else "kr-"
            kid += re.sub(r"[^A-Za-z0-9_\-]", "_", ad.replace("labirent_", ""))
            bilgi["id"] = kid
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
    toplam = sum(len(b) for b in bloblar.values()) / 1e6
    while toplam > a.butce_mb - 0.8 and lidar_hz > 0.26:
        lidar_hz /= 2
        durum_yaz("butce asildi (%.1f MB): LiDAR %.2f Hz'e dusuruluyor" % (toplam, lidar_hz))
        atlanan.clear()
        tani.clear()
        kosular, bloblar = kos(lidar_hz, isin_adim)
        toplam = sum(len(b) for b in bloblar.values()) / 1e6
    if a.onbellek and not os.path.exists(a.onbellek):
        import pickle
        with open(a.onbellek, "wb") as f:
            pickle.dump((kosular, bloblar, tani, list(atlanan), lidar_hz), f)
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
    # sahneler
    sahneler = {k["sahne"]: sahne_bilgisi(k["sahne"]) for k in kosular}
    lab = [k for k in kosular if k["tur"] == "labirent"]
    es2b = {(m["sahne"], str(m["tohum"])): b for m, b in oz["eslesik"]}
    for k in lab:
        k["neden"] = neden_mj(k, es2b.get((k["sahne"], str(k["tohum"]))) if k.get("surum") == "v1" else None)
    surumler_k = sorted({k.get("surum") or "v1" for k in lab}, key=lambda x: (len(x), x))
    son_surum = surumler_k[-1] if surumler_k else "v1"
    cok_surum = len(surumler_k) > 1
    # ---- ilginç koşular (en yeni sürümden)
    ilginc = []
    lab_son = [k for k in lab if (k.get("surum") or "v1") == son_surum]
    bas = [k for k in lab_son if k.get("durum") == "basari"]
    if bas:
        k = min(bas, key=lambda k: k["sure_s"])
        ilginc.append({"id": k["id"], "t": 0, "ad": "En hızlı başarı", "not": "%s, %s" % (kisa_sahne(k["sahne"]), fsure(k["sure_s"]))})
        k = max(bas, key=lambda k: (boyut_of(k["sahne"]), (sahneler[k["sahne"]].get("cozum_m") or 0), k["sure_s"]))
        ilginc.append({"id": k["id"], "t": 0, "ad": "En zor başarı",
                       "not": "%s (çözüm yolu %s m), %s" % (kisa_sahne(k["sahne"]), fnum(sahneler[k["sahne"]].get("cozum_m"), 0), fsure(k["sure_s"]))})
        k = max(bas, key=lambda k: k["sure_s"])
        if k["id"] not in [i["id"] for i in ilginc]:
            ilginc.append({"id": k["id"], "t": 0, "ad": "Son dakika başarısı", "not": "%s, %s" % (kisa_sahne(k["sahne"]), fsure(k["sure_s"]))})
    for d in ("fail_sure", "fail_sikisma", "fail_start"):
        L = [k for k in lab_son if k.get("durum") == d]
        if L:
            k = max(L, key=lambda k: k.get("p_en") or 0)
            tt = k.get("p_en_an") or 0
            ilginc.append({"id": k["id"], "t": max(0, tt - 20), "ad": "Başarısız: " + DURUM_AD[d],
                           "not": "%s, FINISH'e %%%s yaklaştı" % (kisa_sahne(k["sahne"]), fnum(100 * (k.get("p_en") or 0), 0))})
        else:
            ilginc.append({"id": None, "ad": "Başarısız: " + DURUM_AD[d], "not": "MuJoCo'da bu türden yok"})
    if cok_surum:
        for i in ilginc:
            i["not"] = "%s · %s" % (son_surum, i["not"])
    # ---- tanılar
    ilk_fark = [k["ilk_kare_hayalet_fark_m"] for k in lab if k.get("ilk_kare_hayalet_fark_m") is not None]
    uyumsuz = [(k["id"], u) for k in lab for u in k.get("uyumsuz", [])]
    lidar_uz = [k["lidar"].get("duvar_uzaklik_cm") for k in lab if k.get("lidar") and k["lidar"].get("duvar_uzaklik_cm") is not None]
    lidar_uz0 = [k["lidar"].get("duvar_uzaklik_kaymasiz_cm") for k in lab if k.get("lidar") and k["lidar"].get("duvar_uzaklik_kaymasiz_cm") is not None]
    kaymalar = [k["lidar"]["kayma_s"] for k in kosular if k.get("lidar")]
    tanilar = {
        "ilk_kare_fark_maks_cm": round(100 * max(ilk_fark), 2) if ilk_fark else None,
        "lidar_duvar_ortanca_cm": round(statistics.median(lidar_uz), 1) if lidar_uz else None,
        "lidar_duvar_kaymasiz_cm": round(statistics.median(lidar_uz0), 1) if lidar_uz0 else None,
        "lidar_duvar_maks_cm": max(lidar_uz) if lidar_uz else None,
        "lidar_kayma": ("ortanca %s s, aralık %s…%s s" % (fnum(statistics.median(kaymalar), 2), fnum(min(kaymalar), 2), fnum(max(kaymalar), 2))) if kaymalar else None,
        "uyumsuz": uyumsuz, "atlanan": atlanan, "notlar": tani, "lidar_hz": lidar_hz, "isin_adim": isin_adim,
        "hakem_tutan": sum(1 for k in lab if not [u for u in k.get("uyumsuz", []) if "hakem" in u or "puan" in u]),
        "hakem_toplam": len(lab),
    }
    # ---- HTML
    veri = {
        "uretim": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "T": T_SINIR, "kosular": kosular, "sahneler": sahneler, "ilginc": ilginc, "tani": tanilar,
        "strateji_ad": STRATEJI_AD, "durum_ad": DURUM_AD, "surumler": surumler_k, "son_surum": son_surum,
    }
    kaynak = oz["kaynak"]
    kaynak_html = ", ".join("<code>%s</code> %s" % (ad, ("(%s, %d satır)" % (v["zaman"], v["satir"])) if v else "(yok)")
                            for ad, v in kaynak.items())
    mjo = oz["mujoco"]          # sürüm -> küme -> boyut grupları
    sur_csv = oz.get("surumler") or []
    kpi_l, coz_l, tab_l = [], [], []
    for sv in sur_csv:
        et = "MuJoCo" + ((" " + sv) if len(sur_csv) > 1 or sv != "v1" else "")
        rows_sv = oz["mj_surum"][sv]
        if len(sur_csv) > 1:
            kpi_l.append('<div class="kpi-baslik"><span class="etiket e-mj">%s</span></div>' % et)
        kpi_l.append(kpi_html(rows_sv))
        for km, gr in mjo[sv].items():
            km_et = "" if list(mjo[sv]) == ["geliştirme"] else " · %s" % km
            coz_l.append(cozulen_cumle(gr, '<span class="etiket e-mj">%s%s</span>' % (et, km_et)))
            tab_l.append('<h3><span class="etiket e-mj">%s</span> Boyuta göre%s</h3>' % (et, (" · <b>%s kümesi</b>" % km) if km_et else "")
                         + tablo_boyut(gr, ""))
    if not sur_csv:
        kpi_l.append(kpi_html([]))
        tab_l.append('<h3><span class="etiket e-mj">MuJoCo</span> Boyuta göre</h3>' + tablo_boyut(None, ""))
    kume_not = (" Küme: labirent tohumu t1–t3 <b>geliştirme</b> (beyin bunlarla ayarlandı), t4 ve sonrası <b>sınama</b>"
                " (sonuç dosyasında <code>kume</code> sütunu varsa o geçerli).") if any(len(v) > 1 or "sınama" in v for v in mjo.values()) else ""
    kpi = "".join(kpi_l)
    parcalar = {
        "URETIM": veri["uretim"],
        "KAYNAKLAR": kaynak_html + ", <code>sonuc/ham/mujoco*/*.npz</code> (%d kayıt%s)" % (
            len(lab), (": " + ", ".join("%s %d" % (sv, sum(1 for k in lab if k.get("surum") == sv)) for sv in surumler_k)) if cok_surum else ""),
        "KPI": kpi,
        "COZULEN": "<p class=\"cumle\">%s</p>" % "<br>".join(coz_l + [cozulen_cumle(oz["b2_kesif"], "<span class=\"etiket e-2b\">2B benzetici</span>")]),
        "TABLO_MJ": "".join(tab_l) + '<p class="not">Kaynak: %s. Her labirent 3 tohum (LiDAR gürültüsü). Süre ortancası yalnız başarılı koşulardan.%s</p>' % (
            ", ".join("<code>kesif/sonuc/%s</code>" % a for a in kaynak if a.startswith("mujoco")), kume_not),
        "TABLO_2B": tablo_boyut(oz["b2_kesif"], "Kaynak: <code>kesif/sonuc/ilk.csv</code>, strateji keşif, dönüş fazlası %14, 5 tohum. Bu koşuların kaydı yok, oynatılamaz."),
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
    durum_yaz("uretim bitti: %s, %.2f MB, %d kosu (%d labirent, %d koridor), %.0f s, lidar %.2f Hz" % (
        os.path.basename(a.cikti), mb, len(kosular), len(lab), len(kosular) - len(lab), time.time() - t_bas, lidar_hz))
    if atlanan:
        durum_yaz("atlanan: %s" % atlanan)
    if uyumsuz:
        durum_yaz("uyumsuz: %s" % uyumsuz)
    durum_yaz("tani: ilk kare hayalet farki maks %s cm, lidar-duvar ortanca %s cm (maks %s)" % (
        tanilar["ilk_kare_fark_maks_cm"], tanilar["lidar_duvar_ortanca_cm"], tanilar["lidar_duvar_maks_cm"]))


def neden_mj(k, b2):
    """Başarısız MuJoCo koşusu için tek satır neden (hakem sonucu + sonuç CSV'sindeki beyin olayları)."""
    d = k.get("durum")
    if d == "basari":
        return ""
    p = []
    if d == "fail_sure":
        p.append("15:00 doldu, FINISH'ten çıkamadı.")
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
