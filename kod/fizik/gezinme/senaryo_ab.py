"""Senaryo 1, A'dan B'ye: bilinen koridor haritası + bilinen başlangıç pozu -> hedef durak (orta hat rotası).

    %V% kod\\fizik\\gezinme\\senaryo_ab.py --koridor koridor_3 --hedef kapi_7 [--tohum 0] [--kayit x.npz]
    %V% kod\\fizik\\gezinme\\senaryo_ab.py --olcum [--sure-dk 30]      # 6 koridor x 3 hedef x 2 tohum -> sonuc/
    %V% kod\\fizik\\gezinme\\senaryo_ab.py --engel                      # dur-bekle gösterimi (yolda 8 s duran insan)

Robot gerçekte bilinen başlangıçtan biraz sapmış konur (yan ±0,10 m, yön ±3°; deney D gibi), Beyin'e sapmasız
başlangıç bildirilir. Beyin (`beyinler.AbBeyni`) yalnız LiDAR + enkoder görür. Başarı: yer gerçeği gövde merkezi
hedefin 0,3 m içinde ve robot durmuş (`HedefHakemi`)."""

import argparse
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gezinme import _yol  # noqa: E402

_yol.dusuk_oncelik()
from gezinme import rota as R  # noqa: E402
from gezinme import senaryo_ortak as SO  # noqa: E402

ALANLAR = ["id", "koridor", "hedef", "tohum", "basari", "neden", "sure_s", "yol_m", "rota_m", "varis_hatasi_m",
           "tahmin_hatasi_m", "en_yakin_m", "temas_olay", "temas_sure_s", "bitis", "rtf", "duvar_s", "bekleme_s"]


def hedefler(kor):
    """Koridor başına 3 hedef durak: kapıların rota sırasıyla ≈ %30 ve %65'i ile en uzak kapı; T'de ortadaki yerine yan
    koldaki kapı, L'de en uzak kapı ikinci koldadır."""
    d = R.duraklar(kor)
    kapilar = [a for a in d if "_kapi_" in a]
    n = len(kapilar)
    sec = [kapilar[max(0, round(n * 0.3) - 1)], kapilar[max(0, round(n * 0.65) - 1)], kapilar[-1]]
    if kor == "koridor_4":
        kol = [a for a in kapilar if d[a]["kapi"].startswith("kol_")]
        sec[1] = kol[-1]
    out = []
    for a in sec:
        if a not in out:
            out.append(a)
    return out


def gorevler():
    g = []
    for kor in SO.KORIDORLAR:
        for h in hedefler(kor):
            for tohum in (1, 2):
                g.append(dict(id="ab_%s_%s_t%d" % (kor, h, tohum), koridor=kor, hedef=h, tohum=tohum))
    return g


def kos(g, kayit=None, ek_engeller=(), olay=None, sure_s=None):
    from gezinme.beyinler import AbBeyni
    from gezinme.duzenek import Duzenek
    import dunya as D
    kor, tohum = g["koridor"], int(g["tohum"])
    s = D.sahne_oku(kor)
    b = s["baslangic"]
    bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    rng = random.Random(10000 + 31 * tohum + 7 * SO.KORIDORLAR.index(kor))
    gercek = SO.baslangic_sapmasi(bilinen, rng)
    tam, hxy = R.durak_coz(kor, g["hedef"])
    dz = Duzenek(kor, tohum=1000 * tohum + SO.KORIDORLAR.index(kor), baslangic=gercek, ek_engeller=ek_engeller)
    beyin = AbBeyni(kor, bilinen, tam, tohum=500000 + tohum)
    rota_m = R.yol_boyu(beyin.yol)
    hakem = SO.SenaryoHakemi(hxy, pay_m=SO.VARIS_PAYI)
    sure = sure_s or rota_m / 0.25 * 1.8 + 40.0
    bekle = {"s": 0.0}

    def _olay(dz_, t):
        if beyin.k is not None and beyin.k.durdu:
            bekle["s"] += 0.05
        if olay is not None:
            olay(dz_, t)
    sonuc = dz.kos(beyin, sure, hakem=hakem, kayit=kayit, olay=_olay)
    son = sonuc["son_gercek"]
    hata = math.hypot(son[0] - hxy[0], son[1] - hxy[1])
    tah = sonuc["son_tahmin"]
    tah_h = math.hypot(tah[0] - son[0], tah[1] - son[1]) if tah else None
    basari = hata < SO.VARIS_PAYI and (hakem.bitti or sonuc["bitis"] == "beyin")
    neden = "" if basari else (
        "sure doldu (hedefe %.2f m)" % hata if sonuc["bitis"] == "sure" else
        "beyin bitti dedi, yer gercegi hedefe %.2f m (tahmin hatasi %.2f m)" % (hata, tah_h or -1))
    if sonuc["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % sonuc["temas_olay"]
    return dict(g, hedef_tam=tam, hedef_xy=hxy, bilinen_bas=bilinen, gercek_bas=gercek, basari=bool(basari), neden=neden,
                sure_s=sonuc["sure_s"], yol_m=round(hakem.yol_m, 3), rota_m=round(rota_m, 3),
                varis_hatasi_m=round(hata, 4), tahmin_hatasi_m=(round(tah_h, 4) if tah_h is not None else None),
                en_yakin_m=round(hakem.en_yakin_m, 4), temas_olay=sonuc["temas_olay"],
                temas_sure_s=sonuc["temas_sure_s"], bitis=sonuc["bitis"], rtf=sonuc["rtf"],
                bekleme_s=round(bekle["s"], 2), mcl_s=round(beyin.mcl_s, 2), sonuc=sonuc)


def ozet():
    satir = [SO.ham_oku(g["id"]) for g in gorevler()]
    satir = [s for s in satir if s]
    SO.csv_yaz(os.path.join(SO.SONUC, "senaryo_ab.csv"), satir, ALANLAR)
    return satir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--koridor", default="koridor_3")
    ap.add_argument("--hedef", default=None, help="durak adı (k3_kapi_7 ya da kapi_7); yoksa koridorun son hedefi")
    ap.add_argument("--tohum", type=int, default=1)
    ap.add_argument("--kayit", default=None)
    ap.add_argument("--olcum", action="store_true")
    ap.add_argument("--sure-dk", type=float, default=None)
    ap.add_argument("--engel", action="store_true", help="dur-bekle gösterimi: rotada duran insan, 8 s sonra çekilir")
    a = ap.parse_args()
    if a.olcum:
        SO.gorev_kos(gorevler(), kos, a.sure_dk, etiket="ab")
        s = ozet()
        print("senaryo 1: %d / %d basari" % (sum(1 for x in s if x["basari"]), len(s)))
        return 0
    if a.engel:
        g = dict(id="ab_engel", koridor="koridor_5", hedef="kapi_6", tohum=1)
        insan = {"tur": "daire", "x": 6.0, "y": 6.2, "r": 0.2}       # orta hatta, başlangıçtan 4,2 m ötede
        s = kos_engel(g, insan, a.kayit or os.path.join(SO.KAYIT, "ab_engel.npz"), {"kalkti": None})
        SO.ham_yaz("ab_engel", s)
        print(s)
        return 0
    hedef = a.hedef or hedefler(a.koridor)[-1]
    g = dict(id="tek", koridor=a.koridor, hedef=hedef, tohum=a.tohum)
    s = kos(g, kayit=a.kayit)
    s.pop("sonuc", None)
    print(s)
    return 0


def kos_engel(g, insan, kayit, durum):
    """Rotada haritada olmayan duran insan; robot önünde durup 8 s bekledikten sonra insan çekilir."""
    ref = {}
    bekle = {"bas": None}

    def olay(dz, t):
        b = ref.get("beyin")
        if durum["kalkti"] is not None or b is None or b.k is None:
            return
        if b.k.durdu:
            if bekle["bas"] is None:
                bekle["bas"] = t
            elif t - bekle["bas"] >= 8.0:
                dz.engel_tasi(0, 100.0, 100.0)
                durum["kalkti"] = round(t, 2)

    import gezinme.beyinler as GB
    asil = GB.AbBeyni.__init__

    def yakala(self, *k, **kw):
        asil(self, *k, **kw)
        ref["beyin"] = self
    GB.AbBeyni.__init__ = yakala
    try:
        s = kos(g, kayit=kayit, ek_engeller=[insan], olay=olay)
    finally:
        GB.AbBeyni.__init__ = asil
    s.pop("sonuc", None)
    s["insan"] = insan
    s["bekleme_basi_s"] = bekle["bas"]
    s["insan_cekildi_s"] = durum["kalkti"]
    return s


if __name__ == "__main__":
    sys.exit(main())
