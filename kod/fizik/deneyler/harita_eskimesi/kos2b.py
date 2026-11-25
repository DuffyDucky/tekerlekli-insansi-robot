"""2B ızgara koşucusu: koşul x koridor x tohum, A'dan B'ye (`ab`) ve kayıp robot (`kayip`).

    py -3 kos2b.py --senaryo ab --isci 3 [--sure-dk 60] [--kosul taban,kapi_1]   # sonuc/ham/2b/<senaryo>/<id>.json
    py -3 kos2b.py --tek ab:taban:koridor_5:1                                     # tek koşu, ekrana
    py -3 kos2b.py --liste

Tohumlar: A'dan B'ye gezinme/senaryo_ab.py ile aynı (başlangıç sapması 10000 + 31 t + 7 k, MCL 500000 + t), kayıpta
senaryo_kayip.py ile aynı (bırakma 20000 + 100 k + i, MCL 600000 + 10 k + i). Dünya bozucusu tohumu (etken, koridor,
tohum)'dan: aynı etkenin kademeleri iç içe (kademe 2'nin değiştirdiği kapılar kademe 1'inkileri kapsar), benzetici
gürültüsü kademeden bağımsız (ortak rastgele sayılar: taban ile aynı LiDAR / odometri gürültüsü)."""

import argparse
import json
import math
import os
import random
import sys
import time
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ortak  # noqa: E402

ALANLAR_AB = ["id", "senaryo", "kosul", "etken", "alt", "kademe", "deger", "koridor", "tohum", "hedef", "basari",
              "neden", "sure_s", "yol_m", "rota_m", "varis_hatasi_m", "tahmin_hatasi_m", "konum_ort_m", "konum_p95_m",
              "konum_maks_m", "konum_kesin_yanlis", "temas_olay", "temas_hareketli", "temas_duran", "bekleme_s",
              "bitis", "nan_orani", "kayma_olay", "duvar_s"]
ALANLAR_KAYIP = ALANLAR_AB[:9] + ["birak", "hedef", "basari", "neden", "sure_s", "yol_m", "karar_t_s", "karar_yol_m",
                                  "karar_koridor", "karar_dogru", "yanlis_kesin", "son_koridor", "yeniden_plan",
                                  "kesfe_donus", "varis_hatasi_m", "tahmin_hatasi_m", "konum_ort_m", "konum_p95_m",
                                  "konum_maks_m", "temas_olay", "temas_hareketli", "temas_duran", "bitis",
                                  "nan_orani", "kayma_olay", "duvar_s"]
TOHUMLAR = {"ab": (1, 2), "kayip": (0, 1)}


def _tohum(*parca):
    return zlib.crc32("|".join(map(str, parca)).encode()) & 0x7FFFFFFF


def gorevler(senaryo, kosul_sec=None):
    out = []
    for k in ortak.kosullar():
        if kosul_sec and k["id"] not in kosul_sec:
            continue
        for kor in ortak.KORIDORLAR:
            for t in TOHUMLAR[senaryo]:
                out.append(dict(id="%s_%s_%s_%d" % (senaryo, k["id"], kor, t), senaryo=senaryo, kosul=k["id"],
                                etken=k["etken"], alt=k["alt"], kademe=k["kademe"], deger=k["deger"], koridor=kor,
                                tohum=t))
    if kosul_sec:                          # verilen koşul sırasıyla (kesilirse önce baştakiler biter)
        out.sort(key=lambda g: kosul_sec.index(g["kosul"]))
    return out


def ham_yol(g):
    return os.path.join(ortak.HAM, "2b", g["senaryo"], g["id"] + ".json")


def _dunya_ve_kalabalik(g, k):
    import numpy as np
    from insan import Kalabalik
    from konumlama.harita2b import Harita2B
    kor, t = g["koridor"], g["tohum"]
    p = k["p"]
    rng = np.random.default_rng(_tohum(g["senaryo"], k["etken"], kor, t))
    dn = ortak.dunya_kur(kor, p, rng)
    kal = None
    if p.get("insan") or p.get("grup"):
        h = Harita2B(dict(dn["veri"], duvarlar=[list(d) for d in dn["veri"]["duvarlar"]]))
        T = dn["T"]

        def uz(x, y):
            wx, wy = T.nokta(x, y)
            return float(h.geometri_uzakligi(np.array([wx]), np.array([wy]))[0])
        kal = Kalabalik(dn["sahne"], kor, yogunluk=p.get("insan", 0.0), grup_girinti=p.get("grup", 0.0),
                        rng=np.random.default_rng(_tohum("insan", g["senaryo"], kor, t)), engel_uzaklik=uz)
    return dn, kal


def _baslangicta_insan_cek(kal, bas_harita):
    """Robotun bırakıldığı yere 1 m'den yakın insanı hat boyunca 2 m öteye al."""
    if kal is None:
        return
    for p in kal.kisiler:
        x, y, _ = kal.hatlar[p["h"]].nokta(p["s"], p["yan"])
        if math.hypot(x - bas_harita[0], y - bas_harita[1]) < 1.0:
            p["s"] = min(kal.hatlar[p["h"]].boy - 0.5, p["s"] + 2.0) if p["s"] < kal.hatlar[p["h"]].boy - 2.5 \
                else max(0.5, p["s"] - 2.0)


def kos_ab(g, beyin_ayar=None):
    """beyin_ayar(beyin): isteğe bağlı varyant (kos_varyant.py); None = varsayılan beyin."""
    from benzet2b import Benzet2B
    from gezinme import rota as R
    from gezinme import senaryo_ortak as SO
    from gezinme.beyinler import AbBeyni
    from gezinme.senaryo_ab import hedefler
    k = ortak.kosul(g["kosul"])
    kor, tohum = g["koridor"], int(g["tohum"])
    ki = ortak.KORIDORLAR.index(kor)
    dn, kal = _dunya_ve_kalabalik(g, k)
    s = dn["sahne"]
    b = s["baslangic"]
    bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    rng = random.Random(10000 + 31 * tohum + 7 * ki)
    gercek_h = SO.baslangic_sapmasi(bilinen, rng)
    hl = hedefler(kor)
    hedef = hl[1] if tohum % 2 == 1 else hl[-1]
    tam, hxy = R.durak_coz(kor, hedef)
    hxy_dunya = dn["T"].nokta(*hxy)
    _baslangicta_insan_cek(kal, gercek_h)
    beyin = AbBeyni(kor, bilinen, tam, tohum=500000 + tohum)
    if beyin_ayar is not None:
        beyin_ayar(beyin)
    rota_m = R.yol_boyu(beyin.yol)
    hakem = SO.SenaryoHakemi(hxy_dunya, pay_m=ortak.VARIS_PAYI)
    sure = rota_m / 0.25 * 1.8 + 40.0
    bz = Benzet2B(dn, beyin, dn["T"].poz(gercek_h), _tohum("sim", "ab", kor, tohum), k["p"], kalabalik=kal)
    r = bz.kos(sure, hakem=hakem)
    son = r["son_gercek"]
    hata = math.hypot(son[0] - hxy_dunya[0], son[1] - hxy_dunya[1])
    tah = r["son_tahmin"]
    gh = dn["T"].ters_poz(son)
    tah_h = math.hypot(tah[0] - gh[0], tah[1] - gh[1]) if tah else None
    basari = hata < ortak.VARIS_PAYI and (hakem.bitti or r["bitis"] == "beyin")
    neden = "" if basari else (
        "sure doldu (hedefe %.2f m)" % hata if r["bitis"] == "sure" else
        "beyin bitti dedi, hedefe %.2f m (tahmin hatasi %.2f m)" % (hata, tah_h or -1))
    if r["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % r["temas_olay"]
    return dict(g, hedef=tam, basari=bool(basari), neden=neden, yol_m=round(hakem.yol_m, 3), rota_m=round(rota_m, 3),
                varis_hatasi_m=round(hata, 4), tahmin_hatasi_m=(round(tah_h, 4) if tah_h is not None else None),
                dunya=dn["kayit"], insan=(kal.sayi() if kal else None),
                **{a: r[a] for a in r if a not in ("son_gercek", "son_tahmin", "duvar_s")}, duvar_s=r["duvar_s"])


def _birak_dunyada(kor, rng, dn, en_az_pay=0.60):
    """senaryo_kayip.rastgele_birak (haritada) + dünyada da geçerli mi (eşya / kapı değişimi): değilse yeniden çek."""
    import numpy as np
    from benzet2b import ROBOT
    from gezinme import senaryo_ortak as SO
    from kesif.benzet2b import Dunya2B
    from konumlama.harita2b import Harita2B
    dw = Dunya2B(dn["veri"])
    hw = Harita2B(dict(dn["veri"]))
    for deneme in range(50):
        p = SO.rastgele_birak(kor, rng)
        q = dn["T"].poz(p)
        rx, ry = q[0] - 0.185 * math.cos(q[2]), q[1] - 0.185 * math.sin(q[2])
        if dw.temas(q, ROBOT, pay=0.05):
            continue
        if float(hw.geometri_uzakligi(np.array([rx]), np.array([ry]))[0]) < en_az_pay:
            continue
        return p, deneme
    raise RuntimeError("dunyada birakma yeri yok")


def kos_kayip(g, sure_s=300.0):
    from benzet2b import Benzet2B
    from gezinme import rota as R
    from gezinme import senaryo_ortak as SO
    from gezinme.beyinler import KayipBeyni
    k = ortak.kosul(g["kosul"])
    kor, i = g["koridor"], int(g["tohum"])
    ki = ortak.KORIDORLAR.index(kor)
    dn, kal = _dunya_ve_kalabalik(g, k)
    rng = random.Random(20000 + 100 * ki + i)
    bas, yeniden = _birak_dunyada(kor, rng, dn)
    goreli_h = "kapi_%d" % rng.randint(1, 3)
    tam, hxy = R.durak_coz(kor, goreli_h)
    hxy_dunya = dn["T"].nokta(*hxy)
    _baslangicta_insan_cek(kal, bas)
    beyin = KayipBeyni(hedef=goreli_h, tohum=600000 + 10 * ki + i)
    hakem = SO.SenaryoHakemi(hxy_dunya, pay_m=ortak.VARIS_PAYI)
    bz = Benzet2B(dn, beyin, dn["T"].poz(bas), _tohum("sim", "kayip", kor, i), k["p"], kalabalik=kal)
    yanlis = {"n": 0}

    def olc(b):
        if b.tah is not None and not b.tah.kararsiz and b.tah.en_olasi != kor and b._p() >= 0.9:
            yanlis["n"] += 1
        return b.karar == kor
    r = bz.kos(sure_s, hakem=hakem, konum_olc=olc)
    son = r["son_gercek"]
    hata = math.hypot(son[0] - hxy_dunya[0], son[1] - hxy_dunya[1])
    tah = r["son_tahmin"]
    gh = dn["T"].ters_poz(son)
    tah_h = math.hypot(tah[0] - gh[0], tah[1] - gh[1]) if tah else None
    karar_t = beyin.karar_t
    ilk = beyin.kararlar[0][1] if beyin.kararlar else None
    basari = hata < ortak.VARIS_PAYI and (hakem.bitti or r["bitis"] == "beyin")
    if basari:
        neden = ""
    elif karar_t is None:
        neden = "karar yok (son en olasi %s p %.2f)" % (beyin.tah.en_olasi if beyin.tah else "-", beyin._p())
    elif beyin.karar != kor:
        neden = "yanlis koridor: %s (gercek %s)" % (beyin.karar, kor)
    elif r["bitis"] == "sure":
        neden = "sure doldu (hedefe %.2f m, evre %s)" % (hata, beyin.mod)
    else:
        neden = "beyin bitti dedi, hedefe %.2f m (tahmin hatasi %.2f m)" % (hata, tah_h or -1)
    if r["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % r["temas_olay"]
    return dict(g, birak=i, hedef=tam, basari=bool(basari), neden=neden, yol_m=round(hakem.yol_m, 3),
                karar_t_s=(round(karar_t, 2) if karar_t is not None else None),
                karar_yol_m=hakem.yol_ani(karar_t), karar_koridor=ilk,
                karar_dogru=(ilk == kor) if ilk else None, yanlis_kesin=yanlis["n"], son_koridor=beyin.karar,
                kararlar=beyin.kararlar, yeniden_plan=beyin.yeniden_plan, kesfe_donus=beyin.kesfe_donus,
                varis_hatasi_m=round(hata, 4), tahmin_hatasi_m=(round(tah_h, 4) if tah_h is not None else None),
                birak_yeniden=yeniden, bas=list(bas), dunya=dn["kayit"], insan=(kal.sayi() if kal else None),
                **{a: r[a] for a in r if a not in ("son_gercek", "son_tahmin", "duvar_s")}, duvar_s=r["duvar_s"])


def kos_gorev(g):
    yol = ham_yol(g)
    if os.path.exists(yol):
        return g["id"], "var"
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    try:                                   # iki koşucu aynı anda çalışırsa aynı görevi iki kez koşmasın
        os.close(os.open(yol + ".kilit", os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        return g["id"], "kilitli"
    t0 = time.time()
    try:
        s = kos_ab(g) if g["senaryo"] == "ab" else kos_kayip(g)
    except Exception as hata:
        import traceback
        s = dict(g, basari=False, neden="istisna: %r" % hata, iz=traceback.format_exc())
    s["duvar_toplam_s"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol + ".tmp", "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, default=str)
    os.replace(yol + ".tmp", yol)
    try:
        os.remove(yol + ".kilit")
    except OSError:
        pass
    return g["id"],"basari=%s neden=%s duvar=%.0fs" % (s.get("basari"), s.get("neden"), s["duvar_toplam_s"])


def _isci_baslat():
    ortak.dusuk_oncelik()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--senaryo", default="ab", choices=["ab", "kayip"])
    ap.add_argument("--isci", type=int, default=3)
    ap.add_argument("--sure-dk", type=float, default=None)
    ap.add_argument("--kosul", default=None, help="virgülle koşul kimlikleri")
    ap.add_argument("--tek", default=None, help="senaryo:kosul:koridor:tohum")
    ap.add_argument("--liste", action="store_true")
    a = ap.parse_args()
    ortak.dusuk_oncelik()
    if a.tek:
        sn, ko, kor, t = a.tek.split(":")
        g = gorevler(sn, [ko])
        g = [x for x in g if x["koridor"] == kor and x["tohum"] == int(t)][0]
        s = kos_ab(g) if sn == "ab" else kos_kayip(g)
        s.pop("kararlar", None)
        print(json.dumps(s, ensure_ascii=False, default=str, indent=1))
        return 0
    sec = a.kosul.split(",") if a.kosul else None
    G = gorevler(a.senaryo, sec)
    bekleyen = [g for g in G if not os.path.exists(ham_yol(g))]
    if a.liste:
        print("%d gorev, %d bekliyor" % (len(G), len(bekleyen)))
        return 0
    ortak.durum_yaz("kos2b %s basladi: %d gorev bekliyor, %d isci" % (a.senaryo, len(bekleyen), a.isci))
    bas = time.time()
    import multiprocessing as mp
    with mp.Pool(a.isci, initializer=_isci_baslat, maxtasksperchild=40) as havuz:
        sonuclar = []
        for g in bekleyen:
            sonuclar.append(havuz.apply_async(kos_gorev, (g,)))
        n = 0
        for r in sonuclar:
            gid, msj = r.get()
            n += 1
            if n % 6 == 0 or "False" in msj:
                ortak.durum_yaz("%s %d/%d %s %s" % (a.senaryo, n, len(bekleyen), gid, msj))
            if a.sure_dk is not None and time.time() - bas > a.sure_dk * 60:
                havuz.terminate()
                ortak.durum_yaz("%s sure doldu (%d/%d)" % (a.senaryo, n, len(bekleyen)))
                return 0
    ortak.durum_yaz("kos2b %s bitti (%d)" % (a.senaryo, len(bekleyen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
