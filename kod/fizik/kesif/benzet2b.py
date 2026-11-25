"""Hızlı 2B benzetici: kinematik robot (dönme merkezi arka dingil) + sanal LiDAR ışın izleme + bozuk odometri +
ayak izi-duvar çarpışması + `Beyin` protokolü + takılabilir hakem.

Ne modellenir (aç / kapa `BenzetimAyari`):
- Kinematik: arka dingil noktası (v, w) ile ilerler (Euler, 10 ms alt adım); v / w ivme sınırlı (0,5 / 1,8 m/s^2,
  3 rad/s^2), teker hız sınırı |v| + |w| iz / 2 <= v_tavan. Yerinde dönüşte gövde merkezi 0,185 m yarıçaplı yay çizer.
  Gerçek harekete dönüşte yanal kayma eklenebilir (`yanal_kayma_m_rad`, odometri görmez).
- LiDAR: 500 ışın / 360°, 10 Hz, montaj x 0,190 m; dönen tarama (ışın i, t0 + τ_i anındaki pozdan; τ sanal LiDAR'ın
  TAHMİN modeli: saat yönünde, tur 0°'de başlar) ya da anlık (`donen=False`); Gauss gürültü σ 10 mm + 15 mm yuvarlama;
  0,05-12 m dışı NaN; kör sektör [139,2, 220,8] ± 5° NaN. Tarama turu bitince sonraki denetim adımında verilir.
- Odometri (arka dingil noktası): dönüş (1 + donus_hata) kat (varsayılan %14 fazla) + gürültü; öteleme
  (1 + oteleme_hata) kat + gürültü. Çarpışmada robot ilerlemez ama teker döner: odometri girilen hareketin
  `carpma_odo_orani`'nı bildirir (kayma).
- Çarpışma: taban dikdörtgeni (0,525 x 0,52) ile duvar parçaları / daireler kesişiyorsa adım geri alınır (robot
  durur), `temas_var` True.
Ne modellenmez: tekerlek dinamiği, sürtünme, sonar, 3B (LiDAR düzlemi altındaki / üstündeki engeller), ışın demeti
genişliği, yansıtıcılığa bağlı menzil, gecikme / USB, tur hızı oynaması.

Hakem: `Hakem` sınıfı arayüzü (`guncelle(t, gercek_poz, temas_var)`, `bitti`, `sonuc`). Labirent ajanınınki
(`kod/fizik/labirent/hakem.py`) varsa o kullanılır (`hakem="labirent"`), yoksa `IcHakem` (aynı kurallar + geçici puan).
"""

import math
import time
from dataclasses import dataclass, field

import numpy as np

from .robot import VARSAYILAN
from .sahne import sahne_yukle, dunyadan_beyne


def _sar(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


# ============================================================ dünya geometrisi
class Dunya2B:
    def __init__(self, veri):
        from konumlama.harita2b import Harita2B
        self.harita = Harita2B(veri)
        self.parcalar = self.harita.parcalar.copy()          # (S, 4)
        self.daireler = self.harita.daireler.copy()
        p = self.parcalar
        self._pminx = np.minimum(p[:, 0], p[:, 2])
        self._pmaxx = np.maximum(p[:, 0], p[:, 2])
        self._pminy = np.minimum(p[:, 1], p[:, 3])
        self._pmaxy = np.maximum(p[:, 1], p[:, 3])

    def _yakin(self, x, y, r):
        """Noktaya r'den yakın parçaların dizinleri (sınır kutusu ölçütü)."""
        dx = np.maximum(np.maximum(self._pminx - x, x - self._pmaxx), 0.0)
        dy = np.maximum(np.maximum(self._pminy - y, y - self._pmaxy), 0.0)
        return np.flatnonzero(dx * dx + dy * dy <= r * r)

    @staticmethod
    def _kesis(ox, oy, dx, dy, P):
        """Işınlar (n,) x parçalar (S, 4) -> (n,) en yakın t (yoksa inf)."""
        if P.shape[0] == 0:
            return np.full(ox.shape, np.inf)
        x1, y1, x2, y2 = P[:, 0], P[:, 1], P[:, 2], P[:, 3]
        ex, ey = x2 - x1, y2 - y1
        ax = x1[None, :] - ox[:, None]
        ay = y1[None, :] - oy[:, None]
        dxx, dyy = dx[:, None], dy[:, None]
        pay = dxx * ey[None, :] - dyy * ex[None, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (ax * ey[None, :] - ay * ex[None, :]) / pay
            u = (ax * dyy - ay * dxx) / pay
        ok = (np.abs(pay) > 1e-12) & (t > 1e-9) & (u >= 0.0) & (u <= 1.0)
        return np.where(ok, t, np.inf).min(axis=1)

    def isinlar(self, ox, oy, aci, menzil=12.0, yakin_r=3.0):
        """Her ışın kendi kökeni ve dünya yönüyle. İki aşama: önce yakın parçalar, kalanlar bütün parçalarla."""
        dx, dy = np.cos(aci), np.sin(aci)
        cx, cy = float(np.mean(ox)), float(np.mean(oy))
        yay = float(np.max(np.hypot(ox - cx, oy - cy)))
        yk = self._yakin(cx, cy, yakin_r)
        t = self._kesis(ox, oy, dx, dy, self.parcalar[yk])
        kalan = ~(t < yakin_r - yay - 1e-6)
        if kalan.any():
            uz = self._yakin(cx, cy, menzil + yay + 0.1)
            t2 = self._kesis(ox[kalan], oy[kalan], dx[kalan], dy[kalan], self.parcalar[uz])
            t[kalan] = np.minimum(t[kalan], t2)
        if len(self.daireler):
            for cxx, cyy, r in self.daireler:
                fx, fy = ox - cxx, oy - cyy
                b = fx * dx + fy * dy
                c = fx * fx + fy * fy - r * r
                ay = b * b - c
                k = np.sqrt(np.maximum(ay, 0))
                t1 = -b - k
                tt = np.where((ay >= 0) & (t1 > 1e-9), t1, np.inf)
                t = np.minimum(t, tt)
        return t

    def temas(self, poz, robot=VARSAYILAN, pay=0.0):
        """Gövde merkezi pozunda taban dikdörtgeni bir yüzeye değiyor mu?"""
        x, y, th = poz
        hx, hy = robot.derinlik_m / 2 + pay, robot.genislik_m / 2 + pay
        idx = self._yakin(x, y, math.hypot(hx, hy) + 0.05)
        if idx.size:
            P = self.parcalar[idx]
            c, s = math.cos(th), math.sin(th)
            # parça uçlarını gövde çerçevesine
            ax = c * (P[:, 0] - x) + s * (P[:, 1] - y)
            ay = -s * (P[:, 0] - x) + c * (P[:, 1] - y)
            bx = c * (P[:, 2] - x) + s * (P[:, 3] - y)
            by = -s * (P[:, 2] - x) + c * (P[:, 3] - y)
            # Liang-Barsky: parça [0, 1] ile dikdörtgenin kesişimi boş değil mi
            dx, dy = bx - ax, by - ay
            t0 = np.zeros(idx.size)
            t1 = np.ones(idx.size)
            ok = np.ones(idx.size, dtype=bool)
            for p_, q_ in ((-dx, ax + hx), (dx, hx - ax), (-dy, ay + hy), (dy, hy - ay)):
                paralel = np.abs(p_) < 1e-12
                ok &= ~(paralel & (q_ < 0))
                with np.errstate(divide="ignore", invalid="ignore"):
                    r = np.where(paralel, 0.0, q_ / np.where(paralel, 1.0, p_))
                giris = ~paralel & (p_ < 0)
                cikis = ~paralel & (p_ > 0)
                t0 = np.where(giris, np.maximum(t0, r), t0)
                t1 = np.where(cikis, np.minimum(t1, r), t1)
            if (ok & (t0 <= t1)).any():
                return True
        for cx, cy, r in self.daireler:
            c, s = math.cos(th), math.sin(th)
            lx = c * (cx - x) + s * (cy - y)
            ly = -s * (cx - x) + c * (cy - y)
            qx = max(-hx, min(hx, lx))
            qy = max(-hy, min(hy, ly))
            if math.hypot(lx - qx, ly - qy) < r:
                return True
        return False


# ============================================================ jeodezik uzaklık (puan ilerlemesi için)
def jeodezik_alan(dunya, hedef_xy, coz=0.10, pay=0.20):
    """Gerçek haritada (duvarlara > pay) hedeften 4/8 komşulu BFS uzaklığı (m). Dış alan da dahil."""
    h = dunya.harita
    nx, ny = int(math.ceil(h.genislik / coz)), int(math.ceil(h.yukseklik / coz))
    xs = (np.arange(nx) + 0.5) * coz
    ys = (np.arange(ny) + 0.5) * coz
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    uz = h.geometri_uzakligi(gx.ravel(), gy.ravel()).reshape(nx, ny)
    serbest = uz >= pay
    for x0, y0, x1, y1 in h.kutular:
        serbest &= ~((gx >= x0) & (gx <= x1) & (gy >= y0) & (gy <= y1))
    d = np.full(nx * ny, -1.0)
    i, j = int(hedef_xy[0] / coz), int(hedef_xy[1] / coz)
    i, j = min(max(i, 0), nx - 1), min(max(j, 0), ny - 1)
    P = ny
    sf = serbest.ravel().copy()
    sf[i * P + j] = True
    d[i * P + j] = 0.0
    F = np.array([i * P + j])
    k = 0
    ofs = np.array([P, -P, 1, -1])
    while F.size:
        k += 1
        N = (F[:, None] + ofs[None, :]).ravel()
        N = N[(N >= 0) & (N < nx * ny)]
        N = N[sf[N] & (d[N] < 0)]
        if N.size == 0:
            break
        N = np.unique(N)
        d[N] = k * coz
        F = N
    return {"d": d.reshape(nx, ny), "coz": coz}


def jeodezik_oku(alan, x, y):
    d = alan["d"]
    i = min(max(int(x / alan["coz"]), 0), d.shape[0] - 1)
    j = min(max(int(y / alan["coz"]), 0), d.shape[1] - 1)
    v = d[i, j]
    if v >= 0:
        return float(v)
    # duvara çok yakın hücre: komşulardan en küçüğü
    a = d[max(i - 3, 0):i + 4, max(j - 3, 0):j + 4]
    a = a[a >= 0]
    return float(a.min()) if a.size else float("nan")


# ============================================================ iç hakem
def _taraf(cizgi, x, y):
    """Çizgiye göre (işaretli uzaklık dışarı +, çizgi boyunca parametre u ∈ [0, 1])."""
    (x1, y1), (x2, y2) = cizgi
    tx, ty = x2 - x1, y2 - y1
    L2 = tx * tx + ty * ty
    u = ((x - x1) * tx + (y - y1) * ty) / L2
    return u


class IcHakem:
    """Labirent ajanının hakemi gelene kadar aynı kurallar. Gövde merkezi çizgiyi dışarı doğru geçince:
    FINISH -> "basari", START -> "fail_start". Süre dolunca "fail_sure". `sikisma_s` boyunca `sikisma_m`'den az net
    yer değiştirme -> "fail_sikisma". Çarpma olayı: temasın başladığı an (1 s içinde yeniden sayılmaz).
    Puan (araştırma notu §4, labirent ajanının puan.py'si gelene kadar): başarı 1000 + 500 (1 - t / T); süre 400 p_en;
    sıkışma 400 p_en - 100; START -200; her durumda -50 x çarpma olayı - 10 x sürekli temas saniyesi."""

    def __init__(self, sahne, sure_siniri_s=900.0, ayar=None):
        self.sahne = sahne if not isinstance(sahne, (str, dict)) else sahne_yukle(sahne)
        a = {"sikisma_s": 60.0, "sikisma_m": 0.20, "jeodezik": True}
        a.update(ayar or {})
        self.ayar = a
        self.T = float(sure_siniri_s)
        self.bitti = False
        self.sonuc = {}
        self.carpma = 0
        self.temas_s = 0.0
        self._son_temas_t = -1e9
        self._temasta = False
        self._t_onceki = 0.0
        self.yol_m = 0.0
        self._onceki = None
        self._iz = []
        self.p_en = 0.0
        self._jeo = None
        self._g0 = None
        if a["jeodezik"] and self.sahne.finish_cizgi is not None:
            try:
                d = Dunya2B(self.sahne.veri)
                (x1, y1), (x2, y2) = self.sahne.finish_cizgi
                n = self.sahne.finish_dis
                hx, hy = (x1 + x2) / 2 - 0.3 * n[0], (y1 + y2) / 2 - 0.3 * n[1]
                self._jeo = jeodezik_alan(d, (hx, hy))
                self._g0 = jeodezik_oku(self._jeo, *self.sahne.start_poz[:2])
            except Exception:
                self._jeo = None

    def _gecti(self, cizgi, dis, x, y):
        if cizgi is None:
            return False
        (x1, y1), _ = cizgi
        s = (x - x1) * dis[0] + (y - y1) * dis[1]
        u = _taraf(cizgi, x, y)
        return s > 0.0 and -0.05 <= u <= 1.05 and s < 1.5

    def guncelle(self, t, gercek_poz, temas_var):
        if self.bitti:
            return
        x, y = gercek_poz[0], gercek_poz[1]
        dt = t - self._t_onceki
        self._t_onceki = t
        if self._onceki is not None:
            self.yol_m += math.hypot(x - self._onceki[0], y - self._onceki[1])
        self._onceki = (x, y)
        if temas_var:
            self.temas_s += dt
            if not self._temasta and t - self._son_temas_t > 1.0:
                self.carpma += 1
            self._son_temas_t = t
        self._temasta = bool(temas_var)
        if self._jeo is not None and self._g0:
            g = jeodezik_oku(self._jeo, x, y)
            if g == g:
                self.p_en = max(self.p_en, 1.0 - g / self._g0)
        self._iz.append((t, x, y))
        s = self.sahne
        durum = None
        if self._gecti(s.finish_cizgi, s.finish_dis, x, y):
            durum = "basari"
        elif self._gecti(s.start_cizgi, s.start_dis, x, y):
            durum = "fail_start"
        elif t >= self.T:
            durum = "fail_sure"
        else:
            S = self.ayar["sikisma_s"]
            if t >= S:
                while len(self._iz) > 2 and self._iz[1][0] <= t - S:
                    self._iz.pop(0)
                t0, x0, y0 = self._iz[0]
                if t - t0 >= S - 0.1:
                    pts = np.array([(p[1], p[2]) for p in self._iz])
                    if np.hypot(pts[:, 0] - x0, pts[:, 1] - y0).max() < self.ayar["sikisma_m"]:
                        durum = "fail_sikisma"
        if durum:
            self.bitti = True
            if durum == "basari":
                self.p_en = 1.0
            puan = {"basari": 1000 + 500 * (1 - t / self.T), "fail_sure": 400 * self.p_en,
                    "fail_sikisma": 400 * self.p_en - 100, "fail_start": -200.0}[durum]
            puan -= 50 * self.carpma + 10 * self.temas_s
            self.sonuc = {"durum": durum, "sure_s": round(t, 2), "yol_m": round(self.yol_m, 2),
                          "carpma_sayisi": self.carpma, "temas_s": round(self.temas_s, 2),
                          "p_en": round(self.p_en, 3), "puan": round(puan, 1), "hakem": "ic"}


def hakem_kur(sahne, sure_siniri_s=900.0, tur="otomatik"):
    if tur in ("otomatik", "labirent"):
        try:
            from labirent.hakem import Hakem    # kod/fizik/labirent/hakem.py (labirent ajanı)
            if getattr(sahne, "sahne3b", None) is None:
                raise ValueError("3B sahne yok")
            return Hakem(sahne.sahne3b, sure_siniri_s=sure_siniri_s)
        except Exception:
            if tur == "labirent":
                raise
    return IcHakem(sahne, sure_siniri_s=sure_siniri_s)


# ============================================================ benzetici
@dataclass
class BenzetimAyari:
    sure_siniri_s: float = 900.0
    dt_denetim: float = 0.05
    dt_fizik: float = 0.01
    tarama_hz: float = 10.0
    isin_sayisi: int = 500
    donen: bool = True
    gurultu_m: float = 0.010
    yuvarlama_m: float = 0.015
    menzil_min: float = 0.05
    menzil_maks: float = 12.0
    kor: tuple = (139.2, 220.8)
    kor_pay: float = 5.0
    donus_hata: float = 0.14
    donus_std: float = 0.03          # rad/rad
    oteleme_hata: float = 0.02
    oteleme_std: float = 0.02        # m/m
    yanal_kayma_m_rad: float = 0.01  # gerçek hareket: yerinde dönüşte dingilin yanal kayması (odometri görmez)
    carpma_odo_orani: float = 0.5
    tohum: int = 0
    hakem: str = "otomatik"
    kayit_her: int = 2               # her kaçıncı taramada poz kaydı


class Benzetici:
    def __init__(self, sahne, beyin, ayar=None, robot=VARSAYILAN):
        self.sahne = sahne if not isinstance(sahne, (str, dict)) else sahne_yukle(sahne)
        self.beyin = beyin
        self.ayar = a = ayar or BenzetimAyari()
        self.robot = robot
        self.dunya = Dunya2B(self.sahne.veri)
        self.rng = np.random.default_rng(a.tohum)
        n = a.isin_sayisi
        self.acilar = -math.pi + np.arange(n) * (2 * math.pi / n)
        d = np.degrees(self.acilar)
        bas, bit = a.kor[0] - a.kor_pay, a.kor[1] + a.kor_pay
        self.kor = ((d - bas) % 360.0) <= ((bit - bas) % 360.0)
        donem = 1.0 / a.tarama_hz
        self.zaman_ofseti = ((0.0 - self.acilar) % (2 * math.pi)) / (2 * math.pi) * donem
        self.hakem = hakem_kur(self.sahne, a.sure_siniri_s, a.hakem)

    def _tarama(self, t0, log_t, log_p):
        a = self.ayar
        r = self.robot
        if a.donen:
            zt = t0 + self.zaman_ofseti
            th = np.interp(zt, log_t, np.unwrap(log_p[:, 2]))
            ax = np.interp(zt, log_t, log_p[:, 0])
            ay = np.interp(zt, log_t, log_p[:, 1])
        else:
            # anlık tarama: tur sonundaki (teslim anı) poz
            th = np.full(self.acilar.shape, log_p[-1, 2])
            ax = np.full(self.acilar.shape, log_p[-1, 0])
            ay = np.full(self.acilar.shape, log_p[-1, 1])
        # dingil -> gövde merkezi -> LiDAR
        lx = r.lidar_x_m - r.dingil_x_m
        ox = ax + lx * np.cos(th) - r.lidar_y_m * np.sin(th)
        oy = ay + lx * np.sin(th) + r.lidar_y_m * np.cos(th)
        d = self.dunya.isinlar(ox, oy, th + self.acilar, menzil=a.menzil_maks)
        if a.gurultu_m > 0:
            d = d + self.rng.normal(0.0, a.gurultu_m, d.shape)
        if a.yuvarlama_m > 0:
            d = np.round(d / a.yuvarlama_m) * a.yuvarlama_m
        d[(~np.isfinite(d)) | (d < a.menzil_min) | (d > a.menzil_maks) | self.kor] = np.nan
        return {"t": float(t0), "acilar": self.acilar, "mesafeler": d}

    def kos(self, kayit=True):
        a = self.ayar
        r = self.robot
        sx, sy, sth = self.sahne.start_poz
        # durum: arka dingil pozu (dünya)
        px, py, pth = sx + r.dingil_x_m * math.cos(sth), sy + r.dingil_x_m * math.sin(sth), sth
        v = w = 0.0
        n_alt = int(round(a.dt_denetim / a.dt_fizik))
        donem = 1.0 / a.tarama_hz
        log_t = [0.0]
        log_p = [(px, py, pth)]
        tarama_bas = 0.0
        hazir = None
        artim = (0.0, 0.0, 0.0)
        t = 0.0
        adim_ms = []
        tarama_ms = []
        pozlar = []
        temas = False
        k_tarama = 0
        duvar_sayac = 0
        t_bas = time.perf_counter()
        while not self.hakem.bitti:
            # denetim
            t_a = time.perf_counter()
            v_k, w_k = self.beyin.adim(t, hazir, artim)
            dt_ms = (time.perf_counter() - t_a) * 1000.0
            (tarama_ms if hazir is not None else adim_ms).append(dt_ms)
            if hazir is not None:
                k_tarama += 1
                if kayit and k_tarama % a.kayit_her == 0:
                    bp = self.beyin.durum().get("poz")
                    cx, cy = px - r.dingil_x_m * math.cos(pth), py - r.dingil_x_m * math.sin(pth)
                    gx, gy = dunyadan_beyne(self.sahne, cx, cy)
                    gt = pth - sth
                    pozlar.append((t, float(gx), float(gy), float(_sar(gt)),
                                   *(bp if bp is not None else (np.nan, np.nan, np.nan))))
            hazir = None
            artim = (0.0, 0.0, 0.0)
            v_k = float(np.clip(v_k, -r.v_tavan, r.v_tavan))
            w_k = float(np.clip(w_k, -r.w_tavan, r.w_tavan))
            ox_, oy_, oth_ = px, py, pth
            temas = False
            odo = [0.0, 0.0, 0.0]
            for _ in range(n_alt):
                dt = a.dt_fizik
                # ivme sınırı
                dv = v_k - v
                lim = (r.ivme if abs(v_k) > abs(v) and v_k * v >= 0 else r.fren) * dt
                v += max(-lim, min(lim, dv))
                dw = w_k - w
                w += max(-r.w_ivme * dt, min(r.w_ivme * dt, dw))
                # teker sınırı
                tek = abs(v) + abs(w) * r.iz_m / 2
                if tek > r.v_tavan:
                    v *= r.v_tavan / tek
                    w *= r.v_tavan / tek
                d = v * dt
                dth = w * dt
                # gerçek hareket (dingil): yerinde dönüşte yanal kayma
                yan = self.rng.normal(0.0, a.yanal_kayma_m_rad * abs(dth)) if a.yanal_kayma_m_rad > 0 else 0.0
                ort = pth + dth / 2
                px += d * math.cos(ort) - yan * math.sin(ort)
                py += d * math.sin(ort) + yan * math.cos(ort)
                pth = float(_sar(pth + dth))
                # odometri (dingil çerçevesinde birikim)
                d_o = d * (1 + a.oteleme_hata) + (self.rng.normal(0, a.oteleme_std * abs(d)) if a.oteleme_std else 0)
                th_o = dth * (1 + a.donus_hata) + (self.rng.normal(0, a.donus_std * abs(dth)) if a.donus_std else 0)
                c, s = math.cos(odo[2] + th_o / 2), math.sin(odo[2] + th_o / 2)
                odo[0] += d_o * c
                odo[1] += d_o * s
                odo[2] += th_o
                t = round(t + dt, 6)
                log_t.append(t)
                log_p.append((px, py, pth))
            # çarpışma (denetim adımı sonunda, gövde merkezi pozunda)
            cx, cy = px - r.dingil_x_m * math.cos(pth), py - r.dingil_x_m * math.sin(pth)
            if self.dunya.temas((cx, cy, pth), r):
                temas = True
                duvar_sayac += 1
                # geri al: robot ilerlemez; odometri girilen hareketin bir kısmını bildirir
                px, py, pth = ox_, oy_, oth_
                v = w = 0.0
                odo = [o * a.carpma_odo_orani for o in odo]
                for i in range(1, n_alt + 1):
                    log_p[-i] = (px, py, pth)
            artim = tuple(odo)
            if len(log_t) > 80:
                del log_t[:len(log_t) - 60]
                del log_p[:len(log_p) - 60]
            # LiDAR turu bitti mi
            if t >= tarama_bas + donem - 1e-9:
                hazir = self._tarama(tarama_bas, np.array(log_t), np.array(log_p))
                tarama_bas += donem
            cx, cy = px - r.dingil_x_m * math.cos(pth), py - r.dingil_x_m * math.sin(pth)
            self.hakem.guncelle(t, (cx, cy, pth), temas)
        gercek_s = time.perf_counter() - t_bas
        self.son_poz_dingil = (px, py, pth)
        sonuc = dict(self.hakem.sonuc)
        tm = np.array(tarama_ms) if tarama_ms else np.zeros(1)
        am = np.array(adim_ms) if adim_ms else np.zeros(1)
        sonuc.update({"gercek_sure_s": round(gercek_s, 2), "tarama_ms_ort": round(float(tm.mean()), 2),
                      "tarama_ms_p95": round(float(np.percentile(tm, 95)), 2),
                      "tarama_ms_maks": round(float(tm.max()), 2),
                      "adim_ms_ort": round(float(am.mean()), 3), "temas_adim": duvar_sayac})
        P = np.array(pozlar) if pozlar else np.zeros((0, 7))
        if P.shape[0]:
            e = np.hypot(P[:, 1] - P[:, 4], P[:, 2] - P[:, 5])
            eth = np.abs(_sar(P[:, 3] - P[:, 6]))
            sonuc.update({"poz_hata_maks_m": round(float(np.nanmax(e)), 3), "poz_hata_son_m": round(float(e[-1]), 3),
                          "poz_hata_ort_m": round(float(np.nanmean(e)), 3),
                          "yon_hata_maks_der": round(float(np.degrees(np.nanmax(eth))), 2),
                          "yon_hata_son_der": round(float(np.degrees(eth[-1])), 2)})
        self.poz_kaydi = P
        return sonuc


# ============================================================ harita doğruluğu
def harita_dogrulugu(sahne, durum, esik=0.10):
    """Beynin dolu hücrelerini dünyaya çevirip gerçek yüzeye uzaklığı: ortalama (m) ve esik içindeki oran."""
    h = durum.get("harita") if durum else None
    if not h:
        return {}
    iz = np.asarray(h["izgara"])           # [satır = y, sütun = x]
    coz = h["cozunurluk_m"]
    x0, y0 = h["orijin"]
    jj, ii = np.nonzero(iz == 100)
    if ii.size == 0:
        return {"duvar_hucre": 0}
    bx = x0 + (ii + 0.5) * coz
    by = y0 + (jj + 0.5) * coz
    wx, wy = beyinden_dunyaya_np(sahne, bx, by)
    d = Dunya2B(sahne.veri).harita.geometri_uzakligi(wx, wy)
    sanal = h.get("sanal_maske")
    return {"duvar_hucre": int(ii.size), "duvar_hata_ort_m": round(float(d.mean()), 4),
            "duvar_hata_p95_m": round(float(np.percentile(d, 95)), 4),
            "dogru_duvar_orani": round(float((d <= esik).mean()), 4)}


def beyinden_dunyaya_np(sahne, x, y):
    from .sahne import beyinden_dunyaya
    return beyinden_dunyaya(sahne, x, y)
