"""Hızlı 2B kapalı çevrim benzetici: gezinme beyinlerini (AbBeyni / KayipBeyni, değiştirilmeden) haritadan sapmış
bir dünyada koşturur.

Dünya (ortak.dunya_kur): çarpışma geometrisi, LiDAR geometrisi (cam kapılar arkası görünür), dönüş vermeyen yüzeyler,
insanlar (bacak daireleri), harita -> dünya dönüşümü. Beyin yalnız tarama + odometri artımı görür (Duzenek ile aynı
sözleşme: `artim` arka dingil noktasının enkoder artımı; taramada `artim_once` / `artim_sonra`).

Robot (ONERI ölçüleri, `kod/fizik/gezinme/BENIOKU.md`): dönme merkezi arka dingil (x −0,185), taban 0,528 x 0,523 m,
LiDAR x +0,190. Komut v ±0,39 m/s, w ±1,0 rad/s (firmware giriş tavanı); gerçekleşen w = 0,89 · w (VARSAYIM: ölçülen
0,89 / 1,0 ve 0,53 / 0,6 oranı); ivme 0,5 / fren 1,8 m/s², 3 rad/s²; teker sınırı |v| + |w| 0,213 <= 0,39. Kinematik
(Euler, 10 ms), yerinde dönüşte dingilin yanal kayması N(0, 0,01 m/rad) (odometri görmez). Sonar kuralı, motor /
teker dinamiği, yay dönüşündeki hız kaybı (MuJoCo: v 0,25 + w 1 -> 0,19 / 0,59) YOK.
LiDAR: 500 ışın, 10 Hz dönen tarama (ışın i kendi anındaki pozdan), σ gürültü + 15 mm yuvarlama, 0,05-menzil dışı
NaN, kör sektör [134,2°, 225,8°] NaN. Işın sonsuz ince, 3B etki yok.
Çarpışma: denetim adımı sonunda taban dikdörtgeni bir yüzeye / bacağa değiyorsa adım geri alınır, odometri girilen
hareketin yarısını bildirir (teker kayar)."""

import math
import time

import numpy as np

import ortak  # noqa: F401  (yollar)
from kesif.benzet2b import Dunya2B
from kesif.robot import RobotOlcu

ROBOT = RobotOlcu(genislik_m=0.523, derinlik_m=0.528)
DINGIL_X = -0.185
LIDAR_X = 0.190
V_TAVAN, W_GIRIS, W_KAZANC = 0.39, 1.0, 0.89
IVME, FREN, W_IVME = 0.5, 1.8, 3.0
YARI_IZ = 0.213
KOR = (139.2 - 5.0, 220.8 + 5.0)
TEMAS_BIRLESTIR_S = 1.0


def sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def goreli(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    c, s = math.cos(a[2]), math.sin(a[2])
    return (c * dx + s * dy, -s * dx + c * dy, sar(b[2] - a[2]))


class Benzet2B:
    def __init__(self, dunya, beyin, bas_govde_dunya, tohum, p, kalabalik=None, dt_denetim=0.05, dt_fizik=0.01):
        self.dn = dunya
        self.beyin = beyin
        self.p = p
        self.rng = np.random.default_rng(tohum)
        self.carp = Dunya2B(dunya["veri"])
        self.lid = Dunya2B(dunya["lidar_veri"]) if dunya["lidar_veri"] is not dunya["veri"] else self.carp
        self.siyah = None
        if dunya["siyah"]:
            self.siyah = Dunya2B(dict(dunya["veri"], duvarlar=dunya["siyah"], engeller=[]))
        self.sabit_daire_c = self.carp.daireler.copy()
        self.sabit_daire_l = self.lid.daireler.copy()
        self.kal = kalabalik
        self.T = dunya["T"]
        x, y, th = bas_govde_dunya
        self.px, self.py, self.pth = x + DINGIL_X * math.cos(th), y + DINGIL_X * math.sin(th), th
        self.dt, self.dtf = dt_denetim, dt_fizik
        n = 500
        self.acilar = -math.pi + np.arange(n) * (2 * math.pi / n)
        d = np.degrees(self.acilar)
        self.kor = ((d - KOR[0]) % 360.0) <= ((KOR[1] - KOR[0]) % 360.0)
        self.zaman_ofseti = ((0.0 - self.acilar) % (2 * math.pi)) / (2 * math.pi) * 0.1
        self.gurultu = p.get("gurultu", ortak.TABAN["gurultu"])
        self.menzil = p.get("menzil", ortak.TABAN["menzil"])
        self.odo_olcek = ortak.TABAN["odo_olcek"] + p.get("odo_olcek", 0.0)
        self.odo_donus = ortak.TABAN["odo_donus"] + p.get("odo_donus", 0.0)
        self.kayma_hiz = p.get("odo_kayma", 0.0) / 60.0          # olay / s (hareket hâlinde)
        self.kayma_sayisi = 0
        self.nan_isin = 0
        self.isin_top = 0

    # ---------------------------------------------------------------- dünya durumu
    def govde(self):
        return (self.px - DINGIL_X * math.cos(self.pth), self.py - DINGIL_X * math.sin(self.pth), self.pth)

    def _bacaklar_dunya(self):
        if self.kal is None:
            return np.zeros((0, 3))
        B = self.kal.bacaklar()
        if B.shape[0] and not self.T.kimlik:
            for i in range(B.shape[0]):
                B[i, 0], B[i, 1] = self.T.nokta(B[i, 0], B[i, 1])
        return B

    def _daireleri_kur(self):
        B = self._bacaklar_dunya()
        self.carp.daireler = np.vstack([self.sabit_daire_c, B]) if B.shape[0] else self.sabit_daire_c
        if self.lid is not self.carp:
            self.lid.daireler = np.vstack([self.sabit_daire_l, B]) if B.shape[0] else self.sabit_daire_l

    def _tarama(self, t0, LT, LP):
        zt = t0 + self.zaman_ofseti
        th = np.interp(zt, LT, np.unwrap(LP[:, 2]))
        ax = np.interp(zt, LT, LP[:, 0])
        ay = np.interp(zt, LT, LP[:, 1])
        lx = LIDAR_X - DINGIL_X
        ox, oy = ax + lx * np.cos(th), ay + lx * np.sin(th)
        dirs = th + self.acilar
        d = self.lid.isinlar(ox, oy, dirs, menzil=12.0)
        if self.siyah is not None:
            ds = self.siyah.isinlar(ox, oy, dirs, menzil=12.0)
            with np.errstate(invalid="ignore"):          # inf - inf (ikisi de boşluğa) -> NaN -> karşılaştırma False
                d = np.where(np.abs(ds - d) < 1e-6 * (1 + np.abs(d)), np.inf, d)
        d = d + self.rng.normal(0.0, self.gurultu, d.shape)
        d = np.round(d / 0.015) * 0.015
        d[(~np.isfinite(d)) | (d < 0.05) | (d > self.menzil) | self.kor] = np.nan
        dis = ~self.kor
        self.nan_isin += int(np.isnan(d[dis]).sum())
        self.isin_top += int(dis.sum())
        return {"t": float(t0), "acilar": self.acilar, "mesafeler": d}

    # ---------------------------------------------------------------- koşu
    def kos(self, sure_s, hakem=None, kor=None, konum_olc=None):
        """konum_olc(beyin) -> True ise o taramada konum hatası kaydedilir (kayıpta yalnız doğru karardan sonra)."""
        beyin = self.beyin
        if hasattr(getattr(beyin, "izleyici", None), "ayar"):
            beyin.izleyici.ayar.dt_s = self.dt
        n_alt = int(round(self.dt / self.dtf))
        t = 0.0
        v = w = 0.0
        LT = [0.0]
        LP = [(self.px, self.py, self.pth)]
        odo = (0.0, 0.0, 0.0)
        OT = [0.0]
        OP = [odo]
        son_odo = odo
        tarama_bas = 0.0
        hazir = None
        bitti_s = None
        bitis = "sure"
        temas_olay = temas_hareketli = temas_duran = temas_adim = 0
        temas_son_t = -1e9
        temas_onceki = False
        hatalar, kesin_yanlis = [], 0
        bekleme = 0.0
        t_duvar = time.perf_counter()
        self._daireleri_kur()
        while t < sure_s:
            # ------------------------------------------------ beyin
            if hazir is not None:
                orta = hazir["t"] + 0.05
                o_orta = (np.interp(orta, OT, [q[0] for q in OP]), np.interp(orta, OT, [q[1] for q in OP]),
                          np.interp(orta, OT, np.unwrap([q[2] for q in OP])))
                hazir["artim_once"] = goreli(son_odo, o_orta)
                hazir["artim_sonra"] = goreli(o_orta, odo)
            artim = goreli(son_odo, odo)
            son_odo = odo
            v_k, w_k = beyin.adim(t, hazir, artim)
            if hazir is not None:
                bp = beyin.poz
                if bp is not None and (konum_olc is None or konum_olc(beyin)):
                    g = self.T.ters_poz(self.govde())
                    e = math.hypot(bp[0] - g[0], bp[1] - g[1])
                    hatalar.append(e)
                    tah = getattr(beyin, "tah", None)
                    if tah is not None and not tah.konum_kararsiz and e > 0.5:
                        kesin_yanlis += 1
            hazir = None
            if getattr(beyin, "k", None) is not None and beyin.k.durdu:
                bekleme += self.dt
            v_k = max(-V_TAVAN, min(V_TAVAN, float(v_k)))
            w_k = max(-W_GIRIS, min(W_GIRIS, float(w_k))) * W_KAZANC
            hareket_istegi = abs(v_k) > 0.02 or abs(w_k) > 0.05
            ox_, oy_, oth_ = self.px, self.py, self.pth
            o0 = odo
            yeni_LT, yeni_LP = [], []
            for _ in range(n_alt):
                dt = self.dtf
                dv = v_k - v
                lim = (IVME if abs(v_k) > abs(v) and v_k * v >= 0 else FREN) * dt
                v += max(-lim, min(lim, dv))
                w += max(-W_IVME * dt, min(W_IVME * dt, w_k - w))
                tek = abs(v) + abs(w) * YARI_IZ
                if tek > V_TAVAN:
                    v *= V_TAVAN / tek
                    w *= V_TAVAN / tek
                d = v * dt
                dth = w * dt
                yan = self.rng.normal(0.0, 0.01 * abs(dth)) if dth else 0.0
                ort = self.pth + dth / 2
                self.px += d * math.cos(ort) - yan * math.sin(ort)
                self.py += d * math.sin(ort) + yan * math.cos(ort)
                self.pth = sar(self.pth + dth)
                # odometri (enkoder, arka dingil)
                d_o = d * (1 + self.odo_olcek) + (self.rng.normal(0, 0.02 * abs(d)) if d else 0.0)
                th_o = dth * (1 + self.odo_donus) + (self.rng.normal(0, 0.03 * abs(dth)) if dth else 0.0)
                if self.kayma_hiz and (abs(v) > 0.05 or abs(w) > 0.1) and self.rng.random() < self.kayma_hiz * dt:
                    # ani kayma: teker döner, gövde gitmez (odometri sahte öteleme + dönüş bildirir)
                    self.kayma_sayisi += 1
                    d_o += math.copysign(self.rng.uniform(0.10, 0.30), v if v else 1.0)
                    th_o += math.radians(self.rng.uniform(3.0, 10.0)) * (1 if self.rng.random() < 0.5 else -1)
                c, s = math.cos(odo[2] + th_o / 2), math.sin(odo[2] + th_o / 2)
                odo = (odo[0] + d_o * c, odo[1] + d_o * s, odo[2] + th_o)
                t = round(t + dt, 6)
                yeni_LT.append(t)
                yeni_LP.append((self.px, self.py, self.pth))
                OT.append(t)
                OP.append(odo)
            # insanlar (harita çerçevesinde; robotun harita çerçevesindeki yerini görür: hakem tarafı bilgisi)
            if self.kal is not None:
                self.kal.adim(t, self.dt, self.T.ters_poz(self.govde()))
                self._daireleri_kur()
            temas = self.carp.temas(self.govde(), ROBOT)
            if temas:
                temas_adim += 1
                gecti = self.carp.temas(self.govde(), ROBOT)
                self.px, self.py, self.pth = ox_, oy_, oth_
                # robot geri alınınca da temas sürüyorsa (insan robota girdi) robot duruyordu sayılır
                durgun = self.carp.temas(self.govde(), ROBOT)
                v = w = 0.0
                rel = goreli(o0, odo)
                odo = (o0[0] + 0.5 * (math.cos(o0[2]) * rel[0] - math.sin(o0[2]) * rel[1]),
                       o0[1] + 0.5 * (math.sin(o0[2]) * rel[0] + math.cos(o0[2]) * rel[1]), o0[2] + 0.5 * rel[2])
                OP[-1] = odo
                yeni_LP = [(ox_, oy_, oth_)] * len(yeni_LP)
                if not temas_onceki and t - temas_son_t > TEMAS_BIRLESTIR_S:
                    temas_olay += 1
                    if hareket_istegi and not durgun:
                        temas_hareketli += 1
                    else:
                        temas_duran += 1
                temas_son_t = t
                del gecti
            temas_onceki = temas
            LT.extend(yeni_LT)
            LP.extend(yeni_LP)
            if len(LT) > 80:
                del LT[:len(LT) - 60]
                del LP[:len(LP) - 60]
            if len(OT) > 400:
                del OT[:200]
                del OP[:200]
            if t >= tarama_bas + 0.1 - 1e-9:
                hazir = self._tarama(tarama_bas, np.array(LT), np.array(LP))
                tarama_bas += 0.1
            g = self.govde()
            if hakem is not None:
                hakem.guncelle(t, g, temas)
                if hakem.bitti:
                    bitis = "hakem"
                    break
            mod = (beyin.durum() or {}).get("mod")
            if mod == "bitti":
                if bitti_s is None:
                    bitti_s = t
                elif t - bitti_s >= 1.0:
                    bitis = "beyin"
                    break
            else:
                bitti_s = None
        H = np.array(hatalar) if hatalar else np.array([np.nan])
        return dict(sure_s=round(t, 2), bitis=bitis, son_gercek=[round(z, 4) for z in self.govde()],
                    son_tahmin=([round(z, 4) for z in beyin.poz] if beyin.poz is not None else None),
                    temas_olay=temas_olay, temas_hareketli=temas_hareketli, temas_duran=temas_duran,
                    temas_adim=temas_adim, bekleme_s=round(bekleme, 2),
                    konum_ort_m=round(float(np.nanmean(H)), 4) if hatalar else None,
                    konum_p95_m=round(float(np.nanpercentile(H, 95)), 4) if hatalar else None,
                    konum_maks_m=round(float(np.nanmax(H)), 4) if hatalar else None,
                    konum_n=len(hatalar), konum_kesin_yanlis=kesin_yanlis, kayma_olay=self.kayma_sayisi,
                    nan_orani=round(self.nan_isin / max(self.isin_top, 1), 4),
                    duvar_s=round(time.perf_counter() - t_duvar, 1))
