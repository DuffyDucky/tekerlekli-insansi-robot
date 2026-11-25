"""Hafif SLAM: odometri tahmini + tarama-harita eşleştirme + log-odds ızgara yazımı. Döngü kapama yok.

Çerçeveler. Harita çerçevesi = başlangıçtaki gövde merkezi pozu (0, 0, 0), x ileri. `poz` gövde merkezi.
Odometri artımı (dx, dy, dth) arka çeker dingilin ortasındadır (gövdede x = `dingil_x_m`); gövde merkezine
a_c = T(-q) ∘ a ∘ T(q), q = (-dingil_x, 0, 0) ile çevrilir (yerinde dönüşte gövde merkezi 0,185 m yarıçaplı yay çizer).

Her LiDAR turunda:
1. Hareket çarpıklığı giderme. Işın i'nin zamanı t + τ_i (`zaman_ofseti` taramada varsa o; yoksa sanal LiDAR'ın
   TAHMİN modeli: saat yönünde, tur 0°'de başlar). O andaki poz yalnız-odometri zincirinden ara değerle bulunur,
   nokta şimdiki gövde çerçevesine taşınır.
2. Önsel = odometriyle ilerletilmiş poz; bilgi matrisi son turdan beri olan hareketten.
3. Eşleştirme (eslestir.py): kaba ilintisel arama + GN. Kalite kapısı: eşleşen oranı `kalite_esik` altındaysa poz
   odometride kalır ve tarama haritaya YAZILMAZ (araştırma notu: tek kötü eşleşme hayalet duvarla geçidi kapatır).
   Tarama çoğunlukla yeni alan görüyorsa (eşleşebilir oranı düşük) eşleştirme sonucu yine kullanılır ve yazılır;
   art arda çok red gelirse (harita yerinde değil) odometri pozuyla yazılır ki harita donmasın.
4. Dönüş ölçeği öğrenme: kabul edilen turlarda k = Σ Δθ_eşleşme / Σ Δθ_odo (unutma çarpanlı); odometri sonraki
   tahminlerde k ile düzeltilir. İleri ölçek de aynı biçimde, yalnız öteleme iyi gözlenebilirken.
5. Yazım: ışın boyunca boş, uçta dolu; dönüşsüz (NaN, kör sektör dışı) ışın `nan_bos_m`'e kadar boş ("dış"
   sayacına da yazılır). |w| > `yaz_w_maks` iken yazılmaz. Robotun ayak izi (kenarından 5 cm içeride) boş yazılır.
"""

import math
import time
from collections import deque
from dataclasses import dataclass, field

import numpy as np

from .eslestir import EslestirmeAyari, eslestir
from .izgara import Izgara, UzaklikAlani
from .robot import VARSAYILAN


def _sar(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def birlestir(a, b):
    """SE(2) a ∘ b (tek poz)."""
    c, s = math.cos(a[2]), math.sin(a[2])
    return (a[0] + c * b[0] - s * b[1], a[1] + s * b[0] + c * b[1], float(_sar(a[2] + b[2])))


def ters(a):
    c, s = math.cos(a[2]), math.sin(a[2])
    return (-c * a[0] - s * a[1], s * a[0] - c * a[1], -a[2])


@dataclass
class SlamAyari:
    cozunurluk: float = 0.05
    nan_bos_m: float = 6.0          # dönüşsüz ışın bu uzaklığa dek boş sayılır (0 = hiç işlenmez)
    kalite_esik: float = 0.35
    yeni_alan_esik: float = 0.30     # eşleşebilir oranı bunun altındaysa tarama "çoğunlukla yeni alan"
    ardisik_red_maks: int = 8
    alan_yaricap_m: float = 8.0
    alan_yenile_tur: int = 4
    alan_yenile_m: float = 0.4
    alan_esik_L: float = 1.5         # eşleştirme alanına yalnız L > bu hücreler (birkaç kez isabet): kayma sırasında
                                     # bir iki kez yanlış yere yazılan hücreler duvarı kalınlaştırıp eğimi düzleştirmesin
    yaz_w_maks: float = 1.2          # rad/s
    donus_olcegi: float = 1.0        # başlangıç (öğrenilir)
    ileri_olcegi: float = 1.0
    ogren: bool = True
    ogren_unutma: float = 0.995
    olcek_sinir: tuple = (0.6, 1.4)
    # önsel std (m, rad): taban + harekete oranlı
    s_t0: float = 0.03
    s_t_d: float = 0.08
    s_t_th: float = 0.05
    s_th0: float = 0.01
    s_th_th: float = 0.20
    s_th_d: float = 0.03
    # sanal LiDAR zaman modeli (tarama `zaman_ofseti` vermezse)
    tur_suresi_s: float = 0.1
    donus_yonu: str = "saat"
    tur_baslangic_rad: float = 0.0
    carpiklik_gider: bool = True
    eslestirme: EslestirmeAyari = field(default_factory=EslestirmeAyari)


class HafifSLAM:
    def __init__(self, ayar=None, robot=VARSAYILAN, ozellik=None, izgara=None, poz=(0.0, 0.0, 0.0)):
        from konumlama.tarama import LidarOzellik
        self.ayar = ayar or SlamAyari()
        self.robot = robot
        self.oz = ozellik or LidarOzellik.varsa_dosyadan()
        self.izgara = izgara or Izgara(cozunurluk=self.ayar.cozunurluk)
        self.poz = tuple(poz)
        self.odo_poz = tuple(poz)           # yalnız odometri zinciri (çarpıklık giderme için)
        self.gecmis = deque(maxlen=40)      # (t, odo_poz)
        self.t = 0.0
        self.q = (-robot.dingil_x_m, 0.0, 0.0)
        self.k_don = self.ayar.donus_olcegi
        self.k_il = self.ayar.ileri_olcegi
        self._don_pay = self._don_payda = 0.0
        self._il_pay = self._il_payda = 0.0
        self._son_poz_tarama = tuple(poz)
        self._odo_son = (0.0, 0.0, 0.0)     # son turdan beri ham odometri (dingil, ölçeksiz)
        self._odo_son_c = (0.0, 0.0, 0.0)   # son turdan beri düzeltilmiş (gövde merkezi)
        self.alan = None
        self._alan_tur = 0
        self.ardisik_red = 0
        self.tur_sayisi = 0
        self.son = {}
        self.istatistik = {"kabul": 0, "red": 0, "yeni_alan": 0, "zorla_yaz": 0, "yazilmadi_w": 0}
        self.w_tahmin = 0.0

    # ------------------------------------------------------------ odometri
    def odometri(self, artim, t):
        dx, dy, dth = (float(v) for v in artim)
        self._odo_son = (self._odo_son[0] + math.hypot(dx, dy) * (1 if dx >= 0 else -1), 0.0, self._odo_son[2] + dth)
        a = (dx * self.k_il, dy * self.k_il, dth * self.k_don)
        q = self.q
        ac = birlestir(birlestir(ters(q), a), q)
        dt = max(t - self.t, 1e-3)
        self.w_tahmin = 0.7 * self.w_tahmin + 0.3 * (a[2] / dt) if t > self.t else self.w_tahmin
        self.t = t
        self.poz = birlestir(self.poz, ac)
        self.odo_poz = birlestir(self.odo_poz, ac)
        self._odo_son_c = birlestir(self._odo_son_c, ac)
        self.gecmis.append((t, self.odo_poz))

    # ------------------------------------------------------------ yardımcılar
    def _zaman_ofseti(self, acilar, tarama):
        z = tarama.get("zaman_ofseti") if isinstance(tarama, dict) else None
        if z is not None:
            return np.asarray(z, dtype=float)
        a = self.ayar
        if a.donus_yonu == "saat":
            f = ((a.tur_baslangic_rad - acilar) % (2 * np.pi)) / (2 * np.pi)
        else:
            f = ((acilar - a.tur_baslangic_rad) % (2 * np.pi)) / (2 * np.pi)
        return f * a.tur_suresi_s

    def _goreli_pozlar(self, zamanlar):
        """Her zaman için (şimdiki odo pozu)^-1 ∘ (o andaki odo pozu): (x, y, th) dizileri."""
        if len(self.gecmis) < 2:
            n = zamanlar.size
            return np.zeros(n), np.zeros(n), np.zeros(n)
        T = np.array([g[0] for g in self.gecmis])
        P = np.array([g[1] for g in self.gecmis])
        th = np.unwrap(P[:, 2])
        z = np.clip(zamanlar, T[0], T[-1])
        x = np.interp(z, T, P[:, 0])
        y = np.interp(z, T, P[:, 1])
        t = np.interp(z, T, th)
        x1, y1, t1 = P[-1, 0], P[-1, 1], th[-1]
        c, s = math.cos(t1), math.sin(t1)
        ddx, ddy = x - x1, y - y1
        return c * ddx + s * ddy, -s * ddx + c * ddy, t - t1

    def _omega(self):
        a = self.ayar
        d = math.hypot(self._odo_son_c[0], self._odo_son_c[1])
        dth = abs(self._odo_son[2])
        st = a.s_t0 + a.s_t_d * d + a.s_t_th * dth
        sth = a.s_th0 + a.s_th_th * dth + a.s_th_d * d
        return np.diag([1 / st ** 2, 1 / st ** 2, 1 / sth ** 2])

    def ayak_izi_noktalari(self, poz, iceri=0.05):
        r = self.robot
        hx, hy = r.derinlik_m / 2 - iceri, r.genislik_m / 2 - iceri
        c = self.izgara.coz
        xs, ys = np.meshgrid(np.arange(-hx, hx + 1e-9, c), np.arange(-hy, hy + 1e-9, c), indexing="ij")
        xs, ys = xs.ravel(), ys.ravel()
        cc, ss = math.cos(poz[2]), math.sin(poz[2])
        return poz[0] + cc * xs - ss * ys, poz[1] + ss * xs + cc * ys

    # ------------------------------------------------------------ tarama
    def tarama_isle(self, tarama, t_simdi):
        t0 = time.perf_counter()
        a = self.ayar
        acilar = np.asarray(tarama["acilar"], dtype=float)
        m = np.array(tarama["mesafeler"], dtype=float)   # None -> nan
        kor = self.oz.kor_mu(acilar)
        isabet = np.isfinite(m) & (m >= self.oz.menzil_min_m) & (m <= self.oz.menzil_maks_m) & ~kor
        donussuz = ~np.isfinite(m) & ~kor
        if a.nan_bos_m <= 0:
            donussuz[:] = False
        kul = isabet | donussuz
        acilar, m, isabet = acilar[kul], np.where(isabet, m, a.nan_bos_m)[kul], isabet[kul]
        lx, ly = self.robot.lidar_x_m, self.robot.lidar_y_m
        if a.carpiklik_gider:
            zam = float(tarama.get("t", t_simdi)) + self._zaman_ofseti(np.asarray(tarama["acilar"], float)[kul], tarama)
            rx, ry, rt = self._goreli_pozlar(zam)
        else:
            rx = ry = rt = np.zeros(acilar.size)
        c, s = np.cos(rt), np.sin(rt)
        # sensör kökeni ve uç, şimdiki gövde çerçevesinde
        ox = rx + c * lx - s * ly
        oy = ry + s * lx + c * ly
        yon = rt + acilar
        ex = ox + m * np.cos(yon)
        ey = oy + m * np.sin(yon)

        onsel = self.poz
        sonuc = None
        kabul = True
        yaz = True
        durum = "ilk"
        if self.tur_sayisi > 0 and isabet.sum() >= 20:
            g = self.izgara
            if (self.alan is None or self._alan_tur >= a.alan_yenile_tur
                    or math.hypot(onsel[0] - self.alan.merkez[0], onsel[1] - self.alan.merkez[1]) > a.alan_yenile_m):
                self.alan = UzaklikAlani(g, onsel[0], onsel[1], a.alan_yaricap_m, a.eslestirme.d_maks, a.alan_esik_L)
                self._alan_tur = 0
            self._alan_tur += 1
            if self.alan.dolu_sayisi >= 30:
                sonuc = eslestir(self.alan, ex[isabet], ey[isabet], onsel, self._omega(), a.eslestirme,
                                 dth_odo=self._odo_son[2])
                buyuk = math.hypot(*sonuc.duzeltme[:2]) > 0.25 or abs(sonuc.duzeltme[2]) > math.radians(12)
                if sonuc.kalite >= a.kalite_esik and not buyuk:
                    durum = "kabul"
                elif sonuc.eslesebilir < a.yeni_alan_esik and not buyuk:
                    durum = "yeni_alan"
                else:
                    durum = "red"
                    kabul = False
                    yaz = False
            else:
                durum = "seyrek"
        if durum == "red":
            self.ardisik_red += 1
            self.istatistik["red"] += 1
            if self.ardisik_red > a.ardisik_red_maks:
                yaz = True
                self.istatistik["zorla_yaz"] += 1
                self.ardisik_red = 0
        else:
            self.ardisik_red = 0
            if durum == "kabul":
                self.istatistik["kabul"] += 1
            elif durum == "yeni_alan":
                self.istatistik["yeni_alan"] += 1
        if kabul and sonuc is not None:
            self._olcek_ogren(sonuc)
            self.poz = sonuc.poz
        if abs(self.w_tahmin) > a.yaz_w_maks and self.tur_sayisi > 0:
            yaz = False
            self.istatistik["yazilmadi_w"] += 1
        if yaz:
            p = self.poz
            cc, ss = math.cos(p[2]), math.sin(p[2])
            wox, woy = p[0] + cc * ox - ss * oy, p[1] + ss * ox + cc * oy
            wex, wey = p[0] + cc * ex - ss * ey, p[1] + ss * ex + cc * ey
            self.izgara.isin_yaz(wox, woy, wex, wey, isabet)
            fx, fy = self.ayak_izi_noktalari(p)
            self.izgara.bos_yaz(fx, fy)
        self._son_poz_tarama = self.poz
        self._odo_son = (0.0, 0.0, 0.0)
        self._odo_son_c = (0.0, 0.0, 0.0)
        self.tur_sayisi += 1
        self.son = {"durum": durum, "kalite": None if sonuc is None else round(sonuc.kalite, 3),
                    "eslesebilir": None if sonuc is None else round(sonuc.eslesebilir, 3),
                    "oz_min": None if sonuc is None else sonuc.oz_min,
                    "duzeltme": None if sonuc is None else sonuc.duzeltme,
                    "ms": (time.perf_counter() - t0) * 1000.0, "yazildi": yaz,
                    "k_don": self.k_don, "k_il": self.k_il}
        # öndeki engel için gövde çerçevesinde noktalar (beyin kullanır)
        self.son_noktalar = (ex[isabet], ey[isabet])
        return self.son

    def _olcek_ogren(self, sonuc):
        a = self.ayar
        if not a.ogren:
            return
        # Δθ_eşleşme: önceki tur pozundan bu tura; ham odometri dönüşü
        dth_es = float(_sar(sonuc.poz[2] - self._son_poz_tarama[2]))
        dth_odo = self._odo_son[2]
        u = a.ogren_unutma
        if abs(dth_odo) > 0.02 and sonuc.H_tarama[2, 2] > 2e4:
            sg = 1.0 if dth_odo > 0 else -1.0
            self._don_pay = u * self._don_pay + dth_es * sg
            self._don_payda = u * self._don_payda + dth_odo * sg
            if self._don_payda > 0.5:
                self.k_don = float(np.clip(self._don_pay / self._don_payda, *a.olcek_sinir))
        d_odo = self._odo_son[0]
        if abs(d_odo) > 0.01 and sonuc.oz_min > 3e3 and abs(dth_odo) < 0.02:
            dx = sonuc.poz[0] - self._son_poz_tarama[0]
            dy = sonuc.poz[1] - self._son_poz_tarama[1]
            th = self._son_poz_tarama[2]
            d_es = dx * math.cos(th) + dy * math.sin(th)
            sg = 1.0 if d_odo > 0 else -1.0
            self._il_pay = u * self._il_pay + d_es * sg
            self._il_payda = u * self._il_payda + d_odo * sg
            if self._il_payda > 1.0:
                self.k_il = float(np.clip(self._il_pay / self._il_payda, *a.olcek_sinir))
