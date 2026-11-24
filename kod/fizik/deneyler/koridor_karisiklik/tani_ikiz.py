"""Tanı: benzer çiftte farkın görünmediği yolda gelen "kesinlik" veriden mi, parçacık filtresinin rastgeleliğinden mi?

Aynı MuJoCo kaydı (B_koridor_6_bas_t2 ve B_koridor_5_bas_t2 ile aynı sürüş, aynı LiDAR tohumu) konumlayıcıdan
farklı MCL tohumlarıyla geçirilir:
  1) 6 koridor (deneyin kendisi): fark 60 ışına girmeden (yol < 6 m) eşin en büyük olasılığı, yanlış kesin adım
  2) ikiz: yalnız [koridor_5, koridor_5'in birebir kopyası] (ad "ikiz"); geometri aynı, doğru cevap 0,5 / 0,5
Konumlayıcı ayarları varsayılan.

    %V% kod\\fizik\\deneyler\\koridor_karisiklik\\tani_ikiz.py      -> sonuc_v2/tani_ikiz.json  (bugünkü konumlayıcı)
`sonuc/tani_ikiz.json` v1'dir (c34618b konumlayıcısı, yeniden üretilmez).
"""

import json
import math
import os
import sys

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import ortak as O  # noqa: E402
import kos as KO  # noqa: E402

MCL_TOHUMLARI = list(range(1, 11))
FARK_60_YOL = 6.0          # m: B_koridor_5/6_bas koşularında fark 60 ışında 6,0 m'de görünür (analiz.py)


def kayit(kor, tohum=2, bas_ad="bas"):
    ki, si = O.KORIDORLAR.index(kor), KO.BASLANGICLAR.index(bas_ad)
    yol = O.yollar(kor)[bas_ad]
    rng = np.random.default_rng(10000 + 31 * tohum + 7 * ki + si)
    p0, p1 = yol[0], yol[1]
    tg = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    yan = float(rng.uniform(-0.10, 0.10))
    sap = math.radians(float(rng.uniform(-3, 3)))
    bas = (p0[0] - math.sin(tg) * yan, p0[1] + math.cos(tg) * yan, O.sar(tg + sap))
    dz = O.Duzenek(kor, bas, lidar_tohum=1000 * tohum + 10 * ki + si)
    O.sur(dz, yol)
    return O.kayittan_akis(dz)


def kos(akis, haritalar, dogru, es, tohum):
    from konumlama import CokHaritaliMCL
    from konumlama.benzet import goreli
    mcl = CokHaritaliMCL(haritalar, ozellik=O.ozellik(), tohum=tohum)
    onceki = None
    es_max = 0.0
    yanlis = 0
    karar_yol = None
    for tar, o, g, yol in akis:
        tah = mcl.guncelle(tar, artim=goreli(onceki, o) if onceki is not None else None)
        onceki = o
        if yol < FARK_60_YOL:
            es_max = max(es_max, tah.olasiliklar[es])
        if not tah.kararsiz and tah.en_olasi != dogru:
            yanlis += 1
        if karar_yol is None and not tah.kararsiz and tah.en_olasi == dogru:
            karar_yol = yol
    return dict(tohum=tohum, es_max_6m_once=round(es_max, 3), yanlis_kesin_adim=yanlis,
                son_p_dogru=round(tah.olasiliklar[dogru], 4), son_kararsiz=tah.kararsiz, ilk_kesin_dogru_yol=karar_yol)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--etiket", default="v2", choices=["v2", "v3"])
    etiket = ap.parse_args().etiket
    from konumlama.harita2b import Harita2B
    sonuc = {}
    for kor, es in (("koridor_6", "koridor_5"), ("koridor_5", "koridor_6")):
        akis = kayit(kor)
        sonuc[kor] = [kos(akis, O.haritalar(), kor, es, 900 + t) for t in MCL_TOHUMLARI]
        print(kor, sonuc[kor], flush=True)
    # ikiz: koridor_5 ve birebir kopyası, koridor_5 kaydıyla
    veri = O.harita_veri("koridor_5")
    ikiz = [Harita2B(veri, ad="koridor_5"), Harita2B(dict(veri), ad="ikiz")]
    for h in ikiz:
        h.hazirla(0.05, 0.20, erisilebilir=True)
    akis = kayit("koridor_5")
    iz = []
    for t in MCL_TOHUMLARI:
        from konumlama import CokHaritaliMCL
        from konumlama.benzet import goreli
        mcl = CokHaritaliMCL(ikiz, ozellik=O.ozellik(), tohum=900 + t)
        onceki = None
        pmax = 0.0
        kesin = 0
        for tar, o, g, yol in akis:
            tah = mcl.guncelle(tar, artim=goreli(onceki, o) if onceki is not None else None)
            onceki = o
            pmax = max(pmax, tah.olasiliklar["ikiz"], tah.olasiliklar["koridor_5"])
            kesin += 0 if tah.kararsiz else 1
        iz.append(dict(tohum=900 + t, en_buyuk_p=round(pmax, 3), kesin_adim=kesin, adim=len(akis),
                       son_p_ikiz=round(tah.olasiliklar["ikiz"], 3)))
        print("ikiz", iz[-1], flush=True)
    sonuc["ikiz"] = iz
    hedef = os.path.join(BURASI, "sonuc_" + etiket)
    os.makedirs(hedef, exist_ok=True)
    with open(os.path.join(hedef, "tani_ikiz.json"), "w", encoding="utf-8") as f:
        json.dump(sonuc, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
