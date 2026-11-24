"""Koridor karışıklık deneyi: koşucu. Tek komut, kaldığı yerden sürer (bitmiş görev yeniden koşmaz).

    %V% kod\\fizik\\deneyler\\koridor_karisiklik\\kos.py                 # hepsi, 3 işçi
    %V% ...\\kos.py --bolum A,B --isci 2 --sure-dk 9                    # 9 dk sonra yeni görev almaz, çıkar
    %V% ...\\kos.py --liste                                             # görevler ve durumları

Görev sonucu: ham/<bolum>/<id>.json. İlerleme: .durum (10 s'de bir). Kilit: ham/<bolum>/<id>.kilit (işçi görevi
aldığını böyle bildirir; yeni koşucu açılırken eski kilitler silinir). Öncelik: A, B, D, C.
"""

import argparse
import json
import math
import os
import subprocess
import sys
import time
import traceback

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import ortak as O  # noqa: E402

DURUM = os.path.join(BURASI, ".durum")
A_POZ = 36                       # koridor başına rastgele poz
A_PARCA = 12                     # görev başına poz
A_YOGUN_ADIM = 1.0               # benzer çiftte orta hat boyunca yoğun poz aralığı (m)
B_TOHUMLAR = [1, 2, 3, 4, 5]
C_TOHUMLAR = [101]
D_TOHUMLAR = [201, 202, 203]
BASLANGICLAR = ["bas", "son", "orta"]


# ------------------------------------------------------------------ görevler
def gorevler(bolumler):
    g = []
    for b in bolumler:
        if b == "A":
            for k in O.KORIDORLAR:
                for p in range(0, A_POZ, A_PARCA):
                    g.append(dict(bolum="A", id="A_%s_r%02d" % (k, p), kor=k, tur="rastgele", bas=p, son=min(A_POZ, p + A_PARCA)))
            for k in ("koridor_5", "koridor_6"):
                n = len(a_yogun_pozlar(k))
                for p in range(0, n, A_PARCA):
                    g.append(dict(bolum="A", id="A_%s_y%02d" % (k, p), kor=k, tur="yogun", bas=p, son=min(n, p + A_PARCA)))
        elif b == "B":
            for t in B_TOHUMLAR:                          # tohum dışta: yarıda kalırsa her koridor / başlangıç dengeli
                for k in O.KORIDORLAR:
                    for s in BASLANGICLAR:
                        g.append(dict(bolum="B", id="B_%s_%s_t%d" % (k, s, t), kor=k, baslangic=s, tohum=t))
        elif b == "C":
            for t in C_TOHUMLAR:
                for k in O.KORIDORLAR:
                    for s in BASLANGICLAR:
                        g.append(dict(bolum="C", id="C_%s_%s_t%d" % (k, s, t), kor=k, baslangic=s, tohum=t, insan=3))
        elif b == "D":
            for t in D_TOHUMLAR:
                for k in O.KORIDORLAR:
                    g.append(dict(bolum="D", id="D_%s_bas_t%d" % (k, t), kor=k, baslangic="bas", tohum=t, bilinen=True))
    return g


def sonuc_yolu(g):
    return os.path.join(O.HAM, g["bolum"], g["id"] + ".json")


def kilit_yolu(g):
    return os.path.join(O.HAM, g["bolum"], g["id"] + ".kilit")


def bitti_mi(g):
    return os.path.exists(sonuc_yolu(g))


# ------------------------------------------------------------------ A: durağan tek tarama
def _ag(kor):
    """Koridorun orta hat ağı: [çoklu çizgi, ...] (T'de yan kol ayrı)."""
    s = O.sahne(kor)
    ag = [[tuple(p) for p in s["orta_hat"]]]
    if s.get("orta_hat_yan_kol"):
        ag.append([tuple(p) for p in s["orta_hat_yan_kol"]])
    return ag


def _agda(ag, s):
    """Ağ boyunca s: (x, y, teğet açısı, hangi çizgi, çizgide s)."""
    for ci, c in enumerate(ag):
        L = O.cizgi_boyu(c)
        if s <= L or ci == len(ag) - 1:
            s = min(s, L)
            s0 = s
            for a, b in zip(c, c[1:]):
                l = math.hypot(b[0] - a[0], b[1] - a[1])
                if s0 <= l:
                    u = s0 / l
                    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, math.atan2(b[1] - a[1], b[0] - a[0]), ci, s)
                s0 -= l
            a, b = c[-2], c[-1]
            return (b[0], b[1], math.atan2(b[1] - a[1], b[0] - a[0]), ci, L)
        s -= L


def a_rastgele_pozlar(kor):
    """36 poz: ağ boyunca katmanlı (her poz kendi aralığında rastgele), yanal ±0,3 m, yön ±10°, çift sıra ileri / tek ters."""
    ki = O.KORIDORLAR.index(kor)
    rng = np.random.default_rng(7000 + ki)
    ag = _ag(kor)
    L = sum(O.cizgi_boyu(c) for c in ag)
    pozlar = []
    for j in range(A_POZ):
        s = (j + rng.random()) / A_POZ * L
        x, y, tg, ci, sc = _agda(ag, s)
        yan = rng.uniform(-0.3, 0.3)
        sap = math.radians(rng.uniform(-10, 10))
        yon = 0.0 if j % 2 == 0 else math.pi
        pozlar.append(dict(j=j, s=round(s, 3), cizgi=ci, s_cizgi=round(sc, 3), yan=round(yan, 3),
                           ters=bool(j % 2), x=x - math.sin(tg) * yan, y=y + math.cos(tg) * yan,
                           th=O.sar(tg + yon + sap), tohum=70000 + 1000 * ki + j))
    return pozlar


def a_yogun_pozlar(kor):
    """Benzer çift: orta hat boyunca her 1 m, yanal 0, iki yön, yön sapmasız."""
    ki = O.KORIDORLAR.index(kor)
    c = _ag(kor)[0]
    L = O.cizgi_boyu(c)
    pozlar = []
    j = 0
    for s in np.arange(0.0, L + 1e-9, A_YOGUN_ADIM):
        x, y, tg, ci, sc = _agda([c], float(s))
        for ters in (False, True):
            pozlar.append(dict(j=j, s=round(float(s), 3), cizgi=0, s_cizgi=round(float(s), 3), yan=0.0, ters=ters,
                               x=x, y=y, th=O.sar(tg + (math.pi if ters else 0.0)), tohum=90000 + 1000 * ki + j))
            j += 1
    return pozlar


def kos_a(g):
    import lidar as L
    import dunya as D
    from konumlama import tek_taramadan_sinifla
    from sahte_esp32.harita import Harita
    kor = g["kor"]
    pozlar = (a_rastgele_pozlar(kor) if g["tur"] == "rastgele" else a_yogun_pozlar(kor))[g["bas"]:g["son"]]
    s = O.sahne(kor)
    h = Harita(O.harita_veri(s["harita"]), ad=kor)
    w = D.FizikDunya(h, s, (pozlar[0]["x"], pozlar[0]["y"], pozlar[0]["th"]))
    H, oz = O.haritalar(), O.ozellik()
    sonuc = []
    for p in pozlar:
        w.konum_ayarla(p["x"], p["y"], p["th"])
        w.adim(0.05)                                     # oturt (tekerler zemine)
        x, y, _, yaw, _, _ = w.poz()
        lid = L.SanalLidar(w, tohum=p["tohum"])          # varsayılan ayarlar (gürültü 10 mm, 15 mm çözünürlük, kör maske)
        tar = lid.anlik_tarama()
        t0 = time.perf_counter()
        r = tek_taramadan_sinifla(H, tar, ozellik=oz)
        sure = time.perf_counter() - t0
        en = r["pozlar"][r["en_olasi"]]
        dg = r["pozlar"][kor]
        sonuc.append(dict(
            p, gercek=[round(x, 4), round(y, 4), round(yaw, 4)],
            olasiliklar={k: round(v, 5) for k, v in r["olasiliklar"].items()}, en_olasi=r["en_olasi"],
            kararsiz=r["kararsiz"], fark=round(r["fark"], 4),
            en_poz=[round(v, 4) for v in en], dogru_poz=[round(v, 4) for v in dg],
            dogru_poz_hata_m=round(math.hypot(dg[0] - x, dg[1] - y), 3),
            puanlar={k: round(v, 3) for k, v in r["puanlar"].items()}, sure_s=round(sure, 2),
            mesafeler=[None if not np.isfinite(v) else round(v, 3) for v in tar["mesafeler"]]))
    return dict(gorev=g, pozlar=sonuc)


# ------------------------------------------------------------------ B / C / D: hareket hâlinde
def kos_hareket(g):
    kor, bas_ad, tohum = g["kor"], g["baslangic"], g["tohum"]
    ki, si = O.KORIDORLAR.index(kor), BASLANGICLAR.index(bas_ad)
    yol = O.yollar(kor)[bas_ad]
    rng = np.random.default_rng(10000 + 31 * tohum + 7 * ki + si)
    p0, p1 = yol[0], yol[1]
    tg = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    yan = float(rng.uniform(-0.10, 0.10))
    sap = math.radians(float(rng.uniform(-3, 3)))
    bas = (p0[0] - math.sin(tg) * yan, p0[1] + math.cos(tg) * yan, O.sar(tg + sap))
    insanlar = O.insan_yerlestir(kor, yol, np.random.default_rng(50000 + 31 * tohum + 7 * ki + si), g["insan"]) \
        if g.get("insan") else []
    lidar_tohum = 1000 * tohum + 10 * ki + si
    mcl_tohum = 500000 + lidar_tohum
    t0 = time.perf_counter()
    dz = O.Duzenek(kor, bas, lidar_tohum=lidar_tohum, ek_engeller=insanlar)
    surus = O.sur(dz, yol)
    t_fizik = time.perf_counter() - t0
    akis = O.kayittan_akis(dz)
    bilinen = akis[0][2] if g.get("bilinen") else None
    adimlar, gecmis, t_mcl = O.mcl_kos(akis, kor, mcl_tohum, bilinen_bas=bilinen)
    olc = O.olcutler(adimlar, gecmis, kor)
    # kendinden emin yanlış örnekleri: her yanlış dilimin ilk adımının taraması (en çok 3)
    ornekler = []
    for d in olc["yanlis_dilimler"][:3]:
        a = adimlar[d["ilk_i"]]
        tar = akis[d["ilk_i"]][0]
        ornekler.append(dict(adim=a, mesafeler=[None if not np.isfinite(v) else round(v, 3) for v in tar["mesafeler"]]))
    # konumu kesin ama yanlış (doğru harita) ilk örnek
    ky = next((a for a in adimlar if a["en"] == kor and not a["kararsiz"] and not a["konum_kararsiz"]
               and math.hypot(a["ileri"], a["yan"]) > O.ESIK_KONUM_YANLIS), None)
    if ky is not None:
        tar = akis[ky["i"]][0]
        ornekler.append(dict(adim=ky, konum=True,
                             mesafeler=[None if not np.isfinite(v) else round(v, 3) for v in tar["mesafeler"]]))
    sutun = {k: [a[k] for a in adimlar] for k in adimlar[0]}
    return dict(gorev=g, yol=yol, bas_poz=[round(v, 4) for v in bas], insanlar=insanlar, lidar_tohum=lidar_tohum,
                mcl_tohum=mcl_tohum, varyant=O.SURUS_VARYANTI, surus=surus, olcutler=olc, ornekler=ornekler,
                sure_fizik_s=round(t_fizik, 1), sure_mcl_s=round(t_mcl, 1), adimlar=sutun)


# ------------------------------------------------------------------ işçi
def isci(no, bolumler, bitis):
    gl = gorevler(bolumler)
    log = open(os.path.join(O.HAM, "isci_%d.log" % no), "a", encoding="utf-8")

    def yaz(s):
        log.write("%s %s\n" % (time.strftime("%H:%M:%S"), s))
        log.flush()
    yaz("basladi, %d gorev" % len(gl))
    for g in gl:
        if time.time() > bitis:
            yaz("sure doldu")
            break
        if bitti_mi(g):
            continue
        os.makedirs(os.path.dirname(sonuc_yolu(g)), exist_ok=True)
        try:
            fd = os.open(kilit_yolu(g), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
        except FileExistsError:
            continue
        if bitti_mi(g):
            os.remove(kilit_yolu(g))
            continue
        t0 = time.time()
        try:
            r = kos_a(g) if g["bolum"] == "A" else kos_hareket(g)
        except Exception:
            r = dict(gorev=g, hata=traceback.format_exc())
            yaz("HATA %s\n%s" % (g["id"], r["hata"]))
        r["sure_duvar_s"] = round(time.time() - t0, 1)
        r["isci"] = no
        gecici = sonuc_yolu(g) + ".tmp"
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, separators=(",", ":"), allow_nan=False, default=_json)
        os.replace(gecici, sonuc_yolu(g))
        os.remove(kilit_yolu(g))
        yaz("bitti %s %.1f s" % (g["id"], time.time() - t0))
    yaz("cikti")


def _json(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(type(o))


# ------------------------------------------------------------------ koşucu
def durum_yaz(gl, t_bas, isciler, not_=""):
    satir = ["guncelleme %s  gecen %.1f dk  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), (time.time() - t_bas) / 60, not_)]
    toplam = bitmis = 0
    for b in "ABDC":
        bg = [g for g in gl if g["bolum"] == b]
        if not bg:
            continue
        n = sum(bitti_mi(g) for g in bg)
        k = sum(os.path.exists(kilit_yolu(g)) for g in bg)
        satir.append("%s: %d / %d bitti, %d kosuyor" % (b, n, len(bg), k))
        toplam += len(bg)
        bitmis += n
    canli = sum(p.poll() is None for p in isciler)
    satir.append("toplam %d / %d; canli isci %d" % (bitmis, toplam, canli))
    with open(DURUM, "w", encoding="utf-8") as f:
        f.write("\n".join(satir) + "\n")
    return bitmis, toplam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bolum", default="A,B,D,C")
    ap.add_argument("--isci", type=int, default=3)
    ap.add_argument("--sure-dk", type=float, default=0.0, help="0 = sınırsız; dolunca yeni görev alınmaz")
    ap.add_argument("--isci-no", type=int, default=None)
    ap.add_argument("--bitis", type=float, default=None)
    ap.add_argument("--liste", action="store_true")
    a = ap.parse_args()
    bolumler = [b.strip() for b in a.bolum.split(",") if b.strip()]
    os.makedirs(O.HAM, exist_ok=True)
    if a.isci_no is not None:
        isci(a.isci_no, bolumler, a.bitis or 1e18)
        return
    gl = gorevler(bolumler)
    if a.liste:
        for g in gl:
            print(g["id"], "bitti" if bitti_mi(g) else "")
        print(sum(map(bitti_mi, gl)), "/", len(gl))
        return
    for g in gl:                                   # eski kilitler (yarıda kalan koşu)
        if os.path.exists(kilit_yolu(g)):
            os.remove(kilit_yolu(g))
    t_bas = time.time()
    bitis = t_bas + a.sure_dk * 60 if a.sure_dk > 0 else 1e18
    isciler = []
    for i in range(min(a.isci, 3)):                # bellek dar: en çok 3 süreç
        isciler.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), "--isci-no", str(i),
                                         "--bitis", repr(bitis), "--bolum", a.bolum]))
        time.sleep(2)
    while any(p.poll() is None for p in isciler):
        durum_yaz(gl, t_bas, isciler)
        time.sleep(10)
    n, t = durum_yaz(gl, t_bas, isciler, "koşucu bitti")
    print(open(DURUM, encoding="utf-8").read())
    sys.exit(0 if n == t else 3)


if __name__ == "__main__":
    main()
