"""Senaryo 2, kayıp robot: koridorun rastgele bir yerine rastgele yönle bırakılır; hangi koridorda ve nerede olduğunu
bilmez (6 koridor haritası aday). Keşif sürüşüyle konumlayıcı kararlı olana dek yürür, sonra hedef durağa gider.

    %V% kod\\fizik\\gezinme\\senaryo_kayip.py --koridor koridor_5 --birak 0 [--kayit x.npz]
    %V% kod\\fizik\\gezinme\\senaryo_kayip.py --olcum [--sure-dk 40]     # 6 koridor x 5 bırakma -> sonuc/

Hedef göreli verilir ("kapi_<i>", i bırakma tohumundan 1..3): Beyin koridora karar verince "k<N>_kapi_<i>" olur. Yanlış
koridora karar verirse yanlış yere gider (başarısız; neden yazılır). Başarı: yer gerçeği gövde merkezi GERÇEK
koridordaki hedefin 0,3 m içinde ve robot durmuş."""

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

ALANLAR = ["id", "koridor", "birak", "hedef", "basari", "neden", "sure_s", "yol_m", "karar_yol_m", "karar_t_s",
           "karar_koridor", "karar_dogru", "son_koridor", "yeniden_plan", "kesfe_donus", "varis_hatasi_m",
           "tahmin_hatasi_m", "temas_olay", "temas_sure_s", "bitis", "bas_x", "bas_y", "bas_yon_derece", "rtf", "duvar_s"]
SURE_S = 300.0


def gorevler():
    g = []
    for kor in SO.KORIDORLAR:
        for i in range(5):
            g.append(dict(id="kayip_%s_b%d" % (kor, i), koridor=kor, birak=i))
    return g


def kos(g, kayit=None, sure_s=SURE_S):
    from gezinme.beyinler import KayipBeyni
    from gezinme.duzenek import Duzenek
    kor, i = g["koridor"], int(g["birak"])
    k = SO.KORIDORLAR.index(kor)
    rng = random.Random(20000 + 100 * k + i)
    bas = SO.rastgele_birak(kor, rng)
    goreli = "kapi_%d" % rng.randint(1, 3)
    tam, hxy = R.durak_coz(kor, goreli)
    dz = Duzenek(kor, tohum=3000 + 10 * k + i, baslangic=bas)
    beyin = KayipBeyni(hedef=goreli, tohum=600000 + 10 * k + i)
    hakem = SO.SenaryoHakemi(hxy, pay_m=SO.VARIS_PAYI)
    dz.devreye_al()
    t0 = dz.w.zaman_s
    sonuc = dz.kos(beyin, sure_s, hakem=hakem, kayit=kayit)
    son = sonuc["son_gercek"]
    hata = math.hypot(son[0] - hxy[0], son[1] - hxy[1])
    tah = sonuc["son_tahmin"]
    tah_h = math.hypot(tah[0] - son[0], tah[1] - son[1]) if tah else None
    karar_t = (beyin.karar_t - t0) if beyin.karar_t is not None else None
    ilk_karar = beyin.kararlar[0][1] if beyin.kararlar else None
    basari = hata < SO.VARIS_PAYI and (hakem.bitti or sonuc["bitis"] == "beyin")
    if basari:
        neden = ""
    elif beyin.karar_t is None:
        neden = "karar yok (%.0f s kesif; son en olasi %s p %.2f)" % (sonuc["sure_s"], beyin.tah.en_olasi if beyin.tah else "-",
                                                                     beyin._p())
    elif beyin.karar != kor:
        neden = "yanlis koridor: %s (gercek %s)" % (beyin.karar, kor)
    elif sonuc["bitis"] == "sure":
        neden = "sure doldu (hedefe %.2f m, evre %s)" % (hata, beyin.mod)
    else:
        neden = "beyin bitti dedi, hedefe %.2f m (tahmin hatasi %.2f m)" % (hata, tah_h or -1)
    if sonuc["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % sonuc["temas_olay"]
    return dict(g, hedef=tam, hedef_goreli=goreli, hedef_xy=hxy, bas_x=bas[0], bas_y=bas[1],
                bas_yon_derece=round(math.degrees(bas[2]), 1), basari=bool(basari), neden=neden,
                sure_s=sonuc["sure_s"], yol_m=round(hakem.yol_m, 3),
                karar_t_s=(round(karar_t, 2) if karar_t is not None else None),
                karar_yol_m=hakem.yol_ani(karar_t), karar_koridor=ilk_karar, karar_dogru=(ilk_karar == kor) if ilk_karar else None,
                son_koridor=beyin.karar, kararlar=beyin.kararlar, yeniden_plan=beyin.yeniden_plan,
                kesfe_donus=beyin.kesfe_donus, varis_hatasi_m=round(hata, 4),
                tahmin_hatasi_m=(round(tah_h, 4) if tah_h is not None else None), temas_olay=sonuc["temas_olay"],
                temas_sure_s=sonuc["temas_sure_s"], bitis=sonuc["bitis"], rtf=sonuc["rtf"],
                mcl_s=round(beyin.mcl_s, 2), sonuc=sonuc)


def ozet():
    satir = [SO.ham_oku(g["id"]) for g in gorevler()]
    satir = [s for s in satir if s]
    SO.csv_yaz(os.path.join(SO.SONUC, "senaryo_kayip.csv"), satir, ALANLAR)
    return satir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--koridor", default="koridor_5")
    ap.add_argument("--birak", type=int, default=0)
    ap.add_argument("--kayit", default=None)
    ap.add_argument("--olcum", action="store_true")
    ap.add_argument("--sure-dk", type=float, default=None)
    a = ap.parse_args()
    if a.olcum:
        SO.gorev_kos(gorevler(), kos, a.sure_dk, etiket="kayip")
        s = ozet()
        print("senaryo 2: %d / %d basari" % (sum(1 for x in s if x["basari"]), len(s)))
        return 0
    s = kos(dict(id="tek", koridor=a.koridor, birak=a.birak), kayit=a.kayit)
    s.pop("sonuc", None)
    print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
