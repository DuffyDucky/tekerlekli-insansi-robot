"""Senaryo 1 / 2'nin ortak parçaları: hakem (yol sayaçlı), rastgele bırakma, başlangıç sapması, ölçüm koşucusu."""

import csv
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gezinme import _yol  # noqa: E402
from gezinme.duzenek import HedefHakemi  # noqa: E402

SONUC = os.path.join(_yol.GEZINME, "sonuc")
HAM = os.path.join(SONUC, "ham")
KAYIT = os.path.join(_yol.GEZINME, "kayit")
VARIS_PAYI = 0.3                     # m: başarı ölçütü (yer gerçeği gövde merkezi hedefe)
KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
GOVDE_X, GOVDE_Y = 0.2642, 0.2617    # çarpışma kutusu yarı boyları (lale.xml c_govde)
DONME_X = -0.185
SUPURME_R = 0.52                     # m arka dingil çevresinde yerinde dönüş yarıçapı (BENIOKU)


class SenaryoHakemi(HedefHakemi):
    """HedefHakemi + yer gerçeği yol sayacı (zamanla) + en yakın duvar payı."""

    def __init__(self, hedef, **k):
        super().__init__(hedef, **k)
        self.yol_m = 0.0
        self.yol_zaman = []          # (t, yol) 0,5 s'de bir
        self._onceki = None
        self._son_t = -1e9

    def guncelle(self, t, gercek, temas):
        if self._onceki is not None:
            self.yol_m += math.hypot(gercek[0] - self._onceki[0], gercek[1] - self._onceki[1])
        self._onceki = gercek
        if t - self._son_t >= 0.5:
            self.yol_zaman.append((round(t, 2), round(self.yol_m, 3)))
            self._son_t = t
        super().guncelle(t, gercek, temas)

    def yol_ani(self, t):
        """t (kos'a göreli s) anına dek yer gerçeği yolu."""
        if t is None:
            return None
        en = 0.0
        for tt, y in self.yol_zaman:
            if tt > t:
                break
            en = y
        return en


def baslangic_sapmasi(bas, rng, yan=0.10, yon_derece=3.0):
    """Bilinen başlangıcın gerçeğe göre sapması (deney D gibi): yan ±yan m, yön ±yon_derece (düzgün)."""
    x, y, th = bas
    d = rng.uniform(-yan, yan)
    a = math.radians(rng.uniform(-yon_derece, yon_derece))
    return (x - d * math.sin(th), y + d * math.cos(th), th + a)


def _govde_noktalari(x, y, th, adim=0.05):
    c, s = math.cos(th), math.sin(th)
    out = []
    n = int(2 * GOVDE_X / adim) + 1
    for i in range(n):
        u = -GOVDE_X + 2 * GOVDE_X * i / (n - 1)
        for v in (-GOVDE_Y, GOVDE_Y):
            out.append((x + c * u - s * v, y + s * u + c * v))
    m = int(2 * GOVDE_Y / adim) + 1
    for j in range(m):
        v = -GOVDE_Y + 2 * GOVDE_Y * j / (m - 1)
        for u in (-GOVDE_X, GOVDE_X):
            out.append((x + c * u - s * v, y + s * u + c * v))
    return out


def rastgele_birak(kor, rng, en_az_pay=0.60, deneme=2000):
    """Koridorun orta hat çizgesinde (yan kol dahil) boya göre düzgün bir nokta + yan sapma + rastgele yön.

    Koşul: dönme merkezi (arka dingil) her yüzeyden >= en_az_pay (yerinde dönüş yarıçapı 0,52 + pay), gövde çevresi
    >= 0,05 m. Döner: (x, y, th)."""
    import numpy as np
    from gezinme import rota as R
    from gezinme.beyinler import haritalar
    h = haritalar([kor])[0]
    cz = R.Cizge(R.sahne(kor))
    parca = [(cz.dugum[i], cz.dugum[j]) for i, j in cz.parcalar]
    boy = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in parca]
    top = sum(boy)
    for _ in range(deneme):
        s = rng.uniform(0, top)
        for (a, b), L in zip(parca, boy):
            if s <= L:
                break
            s -= L
        t = s / L
        px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
        yan = rng.uniform(-0.45, 0.45)
        th = rng.uniform(-math.pi, math.pi)
        x, y = px + nx * yan, py + ny * yan
        rx, ry = x + DONME_X * math.cos(th), y + DONME_X * math.sin(th)
        if float(h.geometri_uzakligi(np.array([rx]), np.array([ry]))[0]) < en_az_pay:
            continue
        P = np.array(_govde_noktalari(x, y, th))
        if float(h.geometri_uzakligi(P[:, 0], P[:, 1]).min()) < 0.05:
            continue
        if not bool(h.serbest_mi(np.array([x]), np.array([y]))[0]):
            continue
        return (round(x, 4), round(y, 4), round(th, 4))
    raise RuntimeError("%s: uygun bırakma yeri bulunamadı" % kor)


def ham_yaz(ad, veri):
    os.makedirs(HAM, exist_ok=True)
    with open(os.path.join(HAM, ad + ".json"), "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1, default=str)


def ham_oku(ad):
    yol = os.path.join(HAM, ad + ".json")
    if not os.path.exists(yol):
        return None
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def csv_yaz(yol, satirlar, alanlar):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alanlar, extrasaction="ignore")
        w.writeheader()
        for s in satirlar:
            w.writerow(s)


def gorev_kos(gorevler, kos_fn, sure_dk=None, etiket=""):
    """Görevleri sırayla koş (bitmiş = ham JSON var, atlanır). kos_fn(gorev) -> sonuç sözlüğü (ham_yaz eder)."""
    bas = time.time()
    for i, g in enumerate(gorevler):
        if ham_oku(g["id"]) is not None:
            continue
        if sure_dk is not None and time.time() - bas > sure_dk * 60:
            _yol.durum_yaz("%s: sure doldu, %d / %d" % (etiket, i, len(gorevler)))
            return False
        t0 = time.time()
        try:
            s = kos_fn(g)
        except Exception as hata:          # bir koşunun hatası ölçümü durdurmasın; nedeni ham kayda yazılır
            import traceback
            s = dict(g, hata=repr(hata), iz=traceback.format_exc(), basari=False, neden="istisna: %r" % hata)
        s["duvar_s"] = round(time.time() - t0, 1)
        ham_yaz(g["id"], s)
        _yol.durum_yaz("%s %d/%d %s basari=%s sure=%.0fs duvar=%.0fs" % (etiket, i + 1, len(gorevler), g["id"],
                                                                         s.get("basari"), s.get("sure_s") or -1,
                                                                         s["duvar_s"]))
        print("%s %s basari=%s hata=%s sure=%s neden=%s" % (etiket, g["id"], s.get("basari"), s.get("varis_hatasi_m"),
                                                            s.get("sure_s"), s.get("neden")), flush=True)
    return True
