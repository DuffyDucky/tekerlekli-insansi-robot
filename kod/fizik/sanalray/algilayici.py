"""Algılayıcı katmanı (FİZİK / SENSÖR tarafı): kafa kamerası görüntüsü, ön sonar, bozulmuş enkoder odometrisi, kafa
servosu. Yer gerçeğini yalnız sensörün fiziği için kullanır (kameranın gerçek dönüş hızından hareket bulanıklığı, ışının
gerçek duvara çarpması); Beyin'e yalnız piksel, tek mesafe ve enkoder artımı gider. LiDAR düzenekten ayrılır (hiç
hesaplanmaz, `tarama` hep None).

Düzenek döngüsünde sıra (gezinme/duzenek.py `kos`): beyin.adim -> sur -> fizik 50 ms -> olay(dz, t). Kare ve sonar
`olay`'da (adımın sonunda) alınır, Beyin'e bir sonraki `adim`'da verilir; o adımın `artim`'ı karenin alındığı ana dek olan
hareketi taşır (önce tahmin, sonra ölçüm: zaman uyumlu)."""

import math

import numpy as np

from sanalray import kamera as KM

SONAR_ACILAR = (-0.13, 0.0, 0.13)        # rad: HC-SR04 benzeri dar koni (≈ ±7,5°), 3 ışın, en kısası
SONAR_MENZIL = 4.0                       # m
SONAR_YANKI_ACI = math.radians(60)       # bundan eğik gelen ışın yankı vermez (gezinme sonar kuralıyla aynı varsayım)
SONAR_ON_YUZ = 0.2642 - 0.256            # sonar sitesinden gövde ön yüzüne (m)


class Algilayicilar:
    def __init__(self, dz, mercek="std", cozunurluk="1152x648", tohum=0, donus_fazlasi=0.14, dogal_donus=1.0,
                 dogal_oteleme=1.0, oteleme_fazlasi=0.02, donus_std=0.03, oteleme_std=0.02, kare_hz=10.0,
                 bozulma=None, pozlama_s=KM.POZLAMA_S):
        """donus_fazlasi: Beyin'e giden odometrinin GERÇEK dönüşe göre fazlası (0 / 0,14 / 0,25; keşif deneyinin hata
        modeli). dogal_donus: MuJoCo enkoder odometrisinin kendi dönüş oranı (ölçülen; `deney.py odometri`); fazlalık
        buna göre ayarlanır: odometri dth x (1 + donus_fazlasi) / dogal_donus. Ötelemede +%2 yanlılık, %2 / %3 std."""
        self.dz = dz
        W, H = KM.COZUNURLUKLER[cozunurluk]
        self.kam = KM.Kamera(dz.w.m, dz.w.d, mercek, W, H)
        self.K = self.kam.K.copy()
        self.rng = np.random.default_rng(tohum)
        self.k_donus = (1.0 + donus_fazlasi) / dogal_donus
        self.k_oteleme = (1.0 + oteleme_fazlasi) / dogal_oteleme
        self.donus_std, self.oteleme_std = donus_std, oteleme_std
        self.kare_aralik = 1.0 / kare_hz
        self.bozulma = dict(bozulma or {})
        self.pozlama_s = pozlama_s
        self._son_kare_t = -1e9
        self._kare = None
        self.sonar = None
        self._cam_yaw = None
        self._cam_t = None
        self.cam_hiz = 0.0
        self.pan_gonderilen = 0.0
        self.pan_komut_sayisi = 0
        self.kare_sayisi = 0
        self.kare_ms = []
        dz.lidar.ayir()                       # LiDAR kullanılmaz: hesaplanmaz

    # ------------------------------------------------------------ odometri
    def artim_boz(self, artim):
        dx, dy, dth = artim
        n = self.rng.standard_normal(2)
        ko = self.k_oteleme * (1.0 + self.oteleme_std * n[0])
        kd = self.k_donus * (1.0 + self.donus_std * n[1])
        return (dx * ko, dy * ko, dth * kd)

    # ------------------------------------------------------------ sonar
    def _sonar(self):
        w = self.dz.w
        p, R = w.sonar_cercevesi("orta")
        en = None
        for a in SONAR_ACILAR:
            ileri = R[:, 0]
            sol = R[:, 1]
            y = math.cos(a) * ileri + math.sin(a) * sol
            y = y / np.linalg.norm(y)
            r = w.isin(p, y, SONAR_MENZIL)
            if r is None or r[1] > SONAR_YANKI_ACI:
                continue
            d = r[0] * math.cos(a)
            if en is None or d < en:
                en = d
        if en is None:
            return math.inf
        return max(0.0, en - SONAR_ON_YUZ + float(self.rng.normal(0, 0.01)))

    # ------------------------------------------------------------ kamera
    def _kamera_yaw(self):
        Rm = self.dz.w.d.cam_xmat[self.kam.cam].reshape(3, 3)
        f = -Rm[:, 2]
        return math.atan2(f[1], f[0])

    def olay(self, dz, t):
        import time
        self.sonar = self._sonar()
        yaw = self._kamera_yaw()
        if self._cam_yaw is not None and t > self._cam_t:
            self.cam_hiz = (math.atan2(math.sin(yaw - self._cam_yaw), math.cos(yaw - self._cam_yaw))) / (t - self._cam_t)
        self._cam_yaw, self._cam_t = yaw, t
        if t - self._son_kare_t >= self.kare_aralik - 1e-6:
            t0 = time.perf_counter()
            self._son_kare_t = t
            g = self.kam.gri()
            b = self.bozulma
            isik = b.get("isik", 1.0)
            poz = min(0.033, self.pozlama_s / isik) if isik < 1 else self.pozlama_s
            gb = KM.boz(g, self.rng, isik=isik, okuma_gurultu=b.get("okuma_gurultu", 2.0),
                        bulanik_px=abs(self.cam_hiz) * poz * self.K[0, 0])
            self._kare = (t, gb)
            self.kare_sayisi += 1
            self.kare_ms.append((time.perf_counter() - t0) * 1000.0)

    def kare_al(self):
        k, self._kare = self._kare, None
        return k

    # ------------------------------------------------------------ kafa
    def pan_gonder(self, pan_rad):
        """Beyin'in istediği pan açısı (rad, + sola) -> protokol `servo` komutu (servo çerçevesi derece, ev 90)."""
        if pan_rad is None or abs(pan_rad - self.pan_gonderilen) < math.radians(1.0):
            return
        aci = 90.0 + math.degrees(pan_rad)
        c = self.dz.e.istek({"k": "servo", "kanal": "kafa_pan", "aci": round(aci, 1)}, denetle=False)
        self.pan_gonderilen = pan_rad
        self.pan_komut_sayisi += 1
        return c

    def gercek_pan(self):
        w = self.dz.w
        return float(w.d.qpos[w.servo_qpos["kafa_pan"]])

    def kapat(self):
        self.kam.kapat()


class SensorBeyni:
    """Düzenek protokolüne uyarlayıcı: LiDAR taramasını atar, odometriyi bozar, kare / sonar / pan'ı iç Beyin'e taşır."""

    def __init__(self, ic, alg):
        self.ic, self.alg = ic, alg
        self.izleyici = getattr(ic, "izleyici", None)

    def adim(self, t, tarama, artim):
        del tarama                                    # LiDAR kullanılmaz
        v, w = self.ic.adim(t, self.alg.artim_boz(artim), self.alg.kare_al(), self.alg.sonar)
        self.alg.pan_gonder(getattr(self.ic, "pan_istek", None))
        return v, w

    def durum(self):
        return self.ic.durum()
