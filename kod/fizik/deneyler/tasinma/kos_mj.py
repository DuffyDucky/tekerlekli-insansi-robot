"""MuJoCo doğrulaması: A'dan B'ye (AbBeyni, tek harita) taşınma, gezinme düzeneğinde (`gezinme.duzenek.Duzenek`, ONERI,
sahte ESP32 + enkoder odometrisi + sanal LiDAR). Taşıma: `Duzenek.c.konum_ayarla` (MuJoCo tabanı ışınlanır) + LiDAR'ın
yarım turu atılır; Duzenek'in odometrisi (`dz.odo`, tik sayacı) DEĞİŞMEZ: beyin taşımayı yalnız taramadan görebilir.
(`Duzenek.konum_ayarla` odometriyi de yeni poza kurduğu için kullanılmadı.) Başka koridora taşıma MuJoCo'da yok (sahne
tek). Dünya bozulmamış (taban); yanlış alarm için yalnız `ya_taban`.

    %V% kos_mj.py [--surum v3,algi] [--kosul ayni_uzak,ters180,kucuk,ya_taban] [--kosu koridor_5:1,koridor_1:2,koridor_3:1]
"""

import argparse
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kacirma as KC  # noqa: E402

KC.dusuk_oncelik()
import kos_tasinma as KT  # noqa: E402

VARSAYILAN_KOSUAR = [("koridor_5", 1), ("koridor_1", 2), ("koridor_3", 1), ("koridor_6", 2)]
VARSAYILAN_KOSULLAR = ["ayni_uzak", "ters180", "kucuk", "ya_taban"]


class KaciriciMJ(KT.Kacirici):
    _t0 = None

    def adim(self, t, tarama, artim):
        # Duzenek beyne dünya saatini, hakeme koşu başına göreli saati verir: Kacirici göreli saatle çalışsın
        if self._t0 is None:
            self._t0 = t
        return super().adim(t - self._t0, tarama, artim)

    def _konum_koy(self, p, yeni_kor):
        dz = self.bz
        dz.c.konum_ayarla(p[0], p[1], p[2])
        dz.lidar._sifirla_tur()

    def _temas(self, g):
        return bool(self.bz.temas_simdi)


class _DzYuz:
    """Kacirici'nin beklediği yüz: govde() = MuJoCo yer gerçeği."""

    def __init__(self, dz):
        self.dz = dz

    def __getattr__(self, ad):
        return getattr(self.dz, ad)

    def govde(self):
        return self.dz.gercek_poz()


def kos(g):
    import algi
    from gezinme import rota as R
    from gezinme import senaryo_ortak as SO
    from gezinme.duzenek import Duzenek
    from gezinme.senaryo_ab import hedefler
    kor, t = g["koridor"], int(g["tohum"])
    ki = KC.KORIDORLAR.index(kor)
    sr, kosul = g["surum"], g["kosul"]
    ya = kosul.startswith("ya_")
    s = R.sahne(kor)
    b = s["baslangic"]
    bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    gercek_h = SO.baslangic_sapmasi(bilinen, random.Random(10000 + 31 * t + 7 * ki))
    hl = hedefler(kor)
    hedef = hl[1] if t % 2 == 1 else hl[-1]
    tam, hxy = R.durak_coz(kor, hedef)
    beyin = algi.beyin_kur("ab", sr, kor, bilinen, tam, 500000 + t)
    beyin.hedef_tam = tam
    rota_m = R.yol_boyu(R.rota(kor, bilinen[:2], hxy))
    rng = random.Random(KC.tohum("kacir", "ab", kosul, kor, t))
    s_tasima = None if ya else rng.uniform(0.25, 0.60) * rota_m
    hakem = KT.TasinmaHakemi(hxy, son_t=rota_m / 0.25 * 1.8 + 130.0)
    dn = KC.HO.dunya_kur(kor, {}, __import__("numpy").random.default_rng(0))
    dz = Duzenek(kor, tohum=1000 * t + ki, baslangic=gercek_h)
    kc = KaciriciMJ(beyin, "ab", kor, kosul, rng, s_tasima, hakem, rota_m, dn["veri"])
    kc.hedef_tam = tam
    kc.bz = _DzYuz(dz)
    r = dz.kos(kc, 3000.0, hakem=hakem)
    r.setdefault("bekleme_s", None)
    r.setdefault("konum_kesin_yanlis", None)
    out = KT.ozetle(g, kc, beyin, hakem, r, tam, rota_m, dn, None)
    out["rtf"] = r.get("rtf")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--surum", default="v3,algi")
    ap.add_argument("--kosul", default=",".join(VARSAYILAN_KOSULLAR))
    ap.add_argument("--kosu", default=",".join("%s:%d" % k for k in VARSAYILAN_KOSUAR))
    a = ap.parse_args()
    for kosul in a.kosul.split(","):
        for ks in a.kosu.split(","):
            kor, t = ks.split(":")
            for sr in a.surum.split(","):
                g = dict(id="mj_ab_%s_%s_%s_%s" % (sr, kosul, kor, t), kume="mujoco", senaryo="ab", surum=sr,
                         kosul=kosul, koridor=kor, tohum=int(t))
                yol = KC.ham_yol(g, alt="mujoco")
                if os.path.exists(yol):
                    continue
                t0 = time.time()
                try:
                    s = kos(g)
                except Exception as hata:
                    import traceback
                    s = dict(g, basari=False, neden="istisna: %r" % hata, iz=traceback.format_exc())
                s["duvar_toplam_s"] = round(time.time() - t0, 1)
                KC.json_yaz(yol, s)
                KC.durum_yaz("mujoco %s basari=%s tepki=%s bulma=%s temas=%s duvar=%.0fs" % (
                    g["id"], s.get("basari"), s.get("tepki_s"), s.get("bulma_s"), s.get("temas_sonra"),
                    s["duvar_toplam_s"]))
                print(g["id"], s.get("basari"), s.get("tepki_s"), s.get("bulma_s"), s.get("neden"), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
