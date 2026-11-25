"""MuJoCo doğrulaması: aynı bozulmuş dünya (ortak.dunya_kur) gezinme düzeneğinde (`gezinme.duzenek.Duzenek`, ONERI,
sahte ESP32 + enkoder odometrisi + sanal LiDAR). Beyin (AbBeyni) ve tohumları 2B ile aynı; dünya Duzenek'e sahne
sözlüğünün `harita_veri` alanıyla verilir (ortak dosyalara dokunulmaz).

    %V% kos_mujoco.py --kosul taban,kapi_2,kapi_4 [--koridor koridor_5:1,koridor_1:2] [--sure-dk 40]
    %V% kos_mujoco.py --liste

Sensör / odometri bozucuları beyin sarmalayıcısında (`SensorBozucu`) uygulanır: beyin bozulmuş taramayı / artımı görür.
Dönüşsüz yüzey: ışının yer gerçeği pozdan hesaplanan vuruş noktası siyah parçaya 3 cm'den yakınsa NaN (sensör fiziği;
yer gerçeği yalnız bu sensör modelinde kullanılır, beyne gitmez). Cam kapı MuJoCo'da YOK (2B'de var): ışın MuJoCo
geom'undan geçirilemiyor. Menzil ve gürültü sanal LiDAR ayarıyla (`menzil_maks_m`, `gurultu_sigma_m`).
İnsanlar: bacak başına bir ek daire engeli (`engel_tasi` ile her denetim adımında taşınır)."""

import argparse
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ortak  # noqa: E402

ortak.dusuk_oncelik()
import numpy as np  # noqa: E402

# her etken grubundan iki kademe (2 ve 4); koşu: (koridor, tohum)
VARSAYILAN_KOSULLAR = ["taban"]
VARSAYILAN_KOSUAR = [("koridor_5", 1), ("koridor_1", 2)]
HAM_MJ = os.path.join(ortak.HAM, "mujoco")


class SensorBozucu:
    """Beyin sarmalayıcısı: taramaya dönüşsüz yüzey / ek gürültü yok (gürültü LiDAR ayarında), odometriye ölçek, dönüş
    hatası ve ani kayma uygular. Beyin protokolünü aynen iletir."""

    def __init__(self, beyin, p, rng, siyah=None, gercek_fn=None):
        self.b = beyin
        self.rng = rng
        self.olcek = p.get("odo_olcek", 0.0)
        self.donus = p.get("odo_donus", 0.0)
        self.kayma_hiz = p.get("odo_kayma", 0.0) / 60.0
        self.kayma_sayisi = 0
        self.siyah = np.asarray(siyah, dtype=float).reshape(-1, 4) if siyah else None
        self.gercek_fn = gercek_fn
        self.son = (0.0, 0.0)
        self.tarama_geldi = False
        self.nan_isin = self.isin_top = 0

    def __getattr__(self, ad):
        return getattr(self.b, ad)

    def _boz(self, a, dt=0.05):
        dx, dy, dth = a
        k = 1.0 + self.olcek
        dx, dy, dth = dx * k, dy * k, dth * (1.0 + self.donus)
        return dx, dy, dth

    def _siyah_uygula(self, tarama):
        if self.siyah is None or self.gercek_fn is None:
            return tarama
        x, y, th = self.gercek_fn()
        A = np.asarray(tarama["acilar"], dtype=float)
        D = np.asarray([np.nan if d is None else d for d in tarama["mesafeler"]], dtype=float)
        ox, oy = x + 0.19 * math.cos(th), y + 0.19 * math.sin(th)
        hx, hy = ox + D * np.cos(th + A), oy + D * np.sin(th + A)
        S = self.siyah
        x1, y1, x2, y2 = S[:, 0][None, :], S[:, 1][None, :], S[:, 2][None, :], S[:, 3][None, :]
        ex, ey = x2 - x1, y2 - y1
        L2 = ex * ex + ey * ey
        ok = np.isfinite(D)
        px, py = hx[ok][:, None], hy[ok][:, None]
        t = np.clip(((px - x1) * ex + (py - y1) * ey) / L2, 0, 1)
        d = np.hypot(px - (x1 + t * ex), py - (y1 + t * ey)).min(axis=1)
        D2 = D.copy()
        idx = np.flatnonzero(ok)
        D2[idx[d < 0.03]] = np.nan
        out = dict(tarama)
        out["mesafeler"] = D2
        return out

    def adim(self, t, tarama, artim):
        artim = self._boz(artim)
        if self.kayma_hiz and (abs(self.son[0]) > 0.05 or abs(self.son[1]) > 0.1) and \
                self.rng.random() < self.kayma_hiz * 0.05:
            self.kayma_sayisi += 1
            ek = math.copysign(self.rng.uniform(0.10, 0.30), self.son[0] if self.son[0] else 1.0)
            dth = math.radians(self.rng.uniform(3.0, 10.0)) * (1 if self.rng.random() < 0.5 else -1)
            artim = (artim[0] + ek, artim[1], artim[2] + dth)
            self._bekleyen_kayma = (ek, dth)
        else:
            self._bekleyen_kayma = None
        if tarama is not None:
            tarama = self._siyah_uygula(dict(tarama))
            if "artim_once" in tarama:
                once = self._boz(tarama["artim_once"])
                if self._bekleyen_kayma:
                    once = (once[0] + self._bekleyen_kayma[0], once[1], once[2] + self._bekleyen_kayma[1])
                tarama["artim_once"] = once
                tarama["artim_sonra"] = self._boz(tarama["artim_sonra"])
            m = np.asarray(tarama["mesafeler"], dtype=float)
            dd = np.degrees(np.asarray(tarama["acilar"], dtype=float)) % 360.0
            dis = ~((dd >= 134.2) & (dd <= 225.8))           # kör sektör dışı (2B ile aynı sayım)
            self.nan_isin += int(np.isnan(m[dis]).sum())
            self.isin_top += int(dis.sum())
            self.tarama_geldi = True
        self.son = self.b.adim(t, tarama, artim)
        return self.son

    def durum(self):
        return self.b.durum()

    @property
    def poz(self):
        return self.b.poz


def kos(kid, kor, tohum):
    from gezinme import rota as R
    from gezinme import senaryo_ortak as SO
    from gezinme.beyinler import AbBeyni
    from gezinme.duzenek import Duzenek
    from gezinme.senaryo_ab import hedefler
    from kos2b import _baslangicta_insan_cek, _dunya_ve_kalabalik, _tohum
    k = ortak.kosul(kid)
    g = dict(senaryo="ab", koridor=kor, tohum=tohum, kosul=kid)
    dn, kal = _dunya_ve_kalabalik(g, k)
    p = k["p"]
    s = dn["sahne"]
    ki = ortak.KORIDORLAR.index(kor)
    b = s["baslangic"]
    bilinen = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    rng = random.Random(10000 + 31 * tohum + 7 * ki)
    gercek_h = SO.baslangic_sapmasi(bilinen, rng)
    hl = hedefler(kor)
    hedef = hl[1] if tohum == 1 else hl[-1]
    tam, hxy = R.durak_coz(kor, hedef)
    T = dn["T"]
    hxy_d = T.nokta(*hxy)
    _baslangicta_insan_cek(kal, gercek_h)
    ek = []
    if kal is not None:
        B = kal.bacaklar()
        ek = [{"tur": "daire", "x": float(T.nokta(x, y)[0]), "y": float(T.nokta(x, y)[1]), "r": float(r)} for x, y, r in B]
    lidar_ayar = {}
    if "gurultu" in p:
        lidar_ayar["gurultu_sigma_m"] = p["gurultu"]
    if "menzil" in p:
        lidar_ayar["menzil_maks_m"] = p["menzil"]
    sahne = ortak.mujoco_sahnesi(kor, dn)
    dz = Duzenek(sahne, tohum=1000 * tohum + ki, baslangic=T.poz(gercek_h), ek_engeller=ek,
                 lidar_ayar=lidar_ayar or None)
    ic = AbBeyni(kor, bilinen, tam, tohum=500000 + tohum)
    beyin = SensorBozucu(ic, p, np.random.default_rng(_tohum("mjodo", kor, tohum)), siyah=dn["siyah"],
                         gercek_fn=dz.gercek_poz)
    rota_m = R.yol_boyu(ic.yol)
    hakem = SO.SenaryoHakemi(hxy_d, pay_m=ortak.VARIS_PAYI)
    sure = rota_m / 0.25 * 1.8 + 40.0
    st = dict(bekle=0.0, hatalar=[], kesin_yanlis=0, temas_onceki=False, hareketli=0, duran=0, son_temas=-1e9)

    def olay(dz_, t):
        if ic.k is not None and ic.k.durdu:
            st["bekle"] += 0.05
        g_ = dz_.gercek_poz()
        if kal is not None:
            kal.adim(t, 0.05, T.ters_poz(g_))
            B = kal.bacaklar()
            aktif = B.shape[0]
            for i in range(len(ek)):
                if i < aktif:
                    wx, wy = T.nokta(B[i, 0], B[i, 1])
                    dz_.engel_tasi(i, wx, wy)
                else:
                    dz_.engel_tasi(i, 100.0 + i, 100.0)
        if beyin.tarama_geldi and ic.poz is not None:
            beyin.tarama_geldi = False
            gm = T.ters_poz(g_)
            e = math.hypot(ic.poz[0] - gm[0], ic.poz[1] - gm[1])
            st["hatalar"].append(e)
            if ic.tah is not None and not ic.tah.konum_kararsiz and e > 0.5:
                st["kesin_yanlis"] += 1
        tm = dz_.temas_simdi
        if tm and not st["temas_onceki"] and t - st["son_temas"] > 1.0:
            v, w = beyin.son
            if abs(v) > 0.02 or abs(w) > 0.05:
                st["hareketli"] += 1
            else:
                st["duran"] += 1
        if tm:
            st["son_temas"] = t
        st["temas_onceki"] = tm
    r = dz.kos(beyin, sure, hakem=hakem, olay=olay)
    son = r["son_gercek"]
    hata = math.hypot(son[0] - hxy_d[0], son[1] - hxy_d[1])
    basari = hata < ortak.VARIS_PAYI and (hakem.bitti or r["bitis"] == "beyin")
    H = np.array(st["hatalar"]) if st["hatalar"] else np.array([np.nan])
    neden = "" if basari else ("sure doldu (hedefe %.2f m)" % hata if r["bitis"] == "sure" else
                               "beyin bitti dedi, hedefe %.2f m" % hata)
    if r["temas_olay"]:
        neden = (neden + "; " if neden else "") + "temas %d" % r["temas_olay"]
    return dict(id="mj_%s_%s_%d" % (kid, kor, tohum), senaryo="ab", kosul=kid, etken=k["etken"], alt=k["alt"],
                kademe=k["kademe"], deger=k["deger"], koridor=kor, tohum=tohum, hedef=tam, basari=bool(basari),
                neden=neden, sure_s=r["sure_s"], yol_m=round(hakem.yol_m, 3), rota_m=round(rota_m, 3),
                varis_hatasi_m=round(hata, 4), konum_ort_m=round(float(np.nanmean(H)), 4),
                konum_p95_m=round(float(np.nanpercentile(H, 95)), 4), konum_maks_m=round(float(np.nanmax(H)), 4),
                konum_kesin_yanlis=st["kesin_yanlis"], temas_olay=r["temas_olay"], temas_hareketli=st["hareketli"],
                temas_duran=st["duran"], bekleme_s=round(st["bekle"], 2), bitis=r["bitis"],
                nan_orani=round(beyin.nan_isin / max(beyin.isin_top, 1), 4), kayma_olay=beyin.kayma_sayisi,
                rtf=r["rtf"], duvar_s=r["duvar_s"], dunya=dn["kayit"], insan=(kal.sayi() if kal else None))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kosul", default=",".join(VARSAYILAN_KOSULLAR))
    ap.add_argument("--kosu", default=",".join("%s:%d" % k for k in VARSAYILAN_KOSUAR))
    ap.add_argument("--sure-dk", type=float, default=None)
    a = ap.parse_args()
    bas = time.time()
    os.makedirs(HAM_MJ, exist_ok=True)
    for kid in a.kosul.split(","):
        for ks in a.kosu.split(","):
            kor, t = ks.split(":")
            yol = os.path.join(HAM_MJ, "mj_%s_%s_%s.json" % (kid, kor, t))
            if os.path.exists(yol):
                continue
            if a.sure_dk is not None and time.time() - bas > a.sure_dk * 60:
                ortak.durum_yaz("mujoco: sure doldu")
                return 0
            t0 = time.time()
            try:
                s = kos(kid, kor, int(t))
            except Exception as hata:
                import traceback
                s = dict(id="mj_%s_%s_%s" % (kid, kor, t), kosul=kid, koridor=kor, tohum=int(t), basari=False,
                         neden="istisna: %r" % hata, iz=traceback.format_exc())
            s["duvar_toplam_s"] = round(time.time() - t0, 1)
            with open(yol, "w", encoding="utf-8") as f:
                json.dump(s, f, ensure_ascii=False, default=str)
            ortak.durum_yaz("mujoco %s %s:%s basari=%s hata=%s neden=%s duvar=%.0fs" % (
                kid, kor, t, s.get("basari"), s.get("varis_hatasi_m"), s.get("neden"), s["duvar_toplam_s"]))
            print(s.get("id"), s.get("basari"), s.get("varis_hatasi_m"), s.get("neden"), s["duvar_toplam_s"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
