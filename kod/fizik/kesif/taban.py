"""Karşılaştırma tabanları (haritasız): sağ duvar izleme ve rastgele tepkisel. Aynı `Beyin` protokolü.

Sağ el kuralı: döngüsüz labirentte bütün duvarlar dış duvara bağlıdır; START'ın sağ duvarını izleyen robot dış
duvar bileşenini dolaşır ve FINISH ağzına START'a dönmeden varır (ağaç labirentte garanti). Haritasız, LiDAR'ı yalnız
yakın çevre için kullanır: çıkmaza uzaktan bakıp girmemeyi bilmez.

Denetim (gövde çerçevesindeki tarama noktalarından):
- takip: sağ yan boşluğu `d_ref`'e PD (+ duvar açısı), önde engel < `on_dur` -> sola_don
- sağ açıldı (gövde yanında ve önünde sağda duvar yok) -> ilerle (dönme merkezi ağzın ortasına gelene dek) -> saga_don (90°)
  -> gir (0,6 m, sağ açıklık denetimi kapalı) -> takip
- sola_don: önde ≥ `on_acik` boşluk olana dek yerinde sola dön (çıkmazda 180°)
Rastgele: ileri git, önde engel varsa rastgele yöne rastgele süre dön; yan açıklıklarda olasılıkla dön.
"""

import math
import random

import numpy as np

from .robot import VARSAYILAN


def _sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def tarama_noktalari(tarama, robot=VARSAYILAN):
    a = np.asarray(tarama["acilar"], dtype=float)
    m = np.array(tarama["mesafeler"], dtype=float)
    ok = np.isfinite(m) & (m > 0.05)
    a, m = a[ok], m[ok]
    return robot.lidar_x_m + m * np.cos(a), robot.lidar_y_m + m * np.sin(a)


class SagDuvar:
    def __init__(self, robot=VARSAYILAN, v=0.22, d_ref=0.36, on_dur=0.34, on_acik=0.85):
        self.r = robot
        self.v = v
        self.d_ref = d_ref
        self.on_dur = on_dur
        self.on_acik = on_acik
        self.durum = "takip"
        self.hedef = None          # manevra hedefi (mesafe ya da açı)
        self.bas = None
        self.poz = (0.0, 0.0, 0.0)

    def poz_ver(self, poz):
        self.poz = poz

    def komut(self, x, y, poz=None):
        if poz is not None:
            self.poz = poz
        r = self.r
        on_x, yg = r.on_x, r.yari_genislik
        serit = (np.abs(y) <= yg + 0.04) & (x > on_x - 0.02)
        on = float((x[serit] - on_x).min()) if serit.any() else 9.0
        sag = (y < -0.05) & (x > -0.30) & (x < 0.35) & (y > -1.2)
        sag_d = float((-y[sag]).min() - yg) if sag.any() else 9.0
        sol = (y > 0.05) & (x > -0.30) & (x < 0.35) & (y < 1.2)
        sol_d = float((y[sol]).min() - yg) if sol.any() else 9.0
        sag_on = (y < -0.30) & (y > -1.1) & (x > 0.0) & (x < 0.55)
        p = self.poz
        if self.durum == "sola_don":
            if on > self.on_acik and abs(_sar(p[2] - self.bas[2])) > 1.2 or abs(_sar(p[2] - self.bas[2])) > 3.3:
                self.durum = "gir"
                self.bas = p
                self.hedef = 0.3
            else:
                return 0.0, 0.7
        if self.durum == "ilerle":
            if math.hypot(p[0] - self.bas[0], p[1] - self.bas[1]) >= self.hedef or on < self.on_dur:
                self.durum = "saga_don"
                self.bas = p
            else:
                return min(self.v, 0.18), 0.0
        if self.durum == "saga_don":
            if abs(_sar(p[2] - self.bas[2])) >= math.pi / 2 - 0.08:
                self.durum = "gir"
                self.bas = p
                self.hedef = 0.6
            else:
                return 0.0, -0.7
        if self.durum == "gir":
            if math.hypot(p[0] - self.bas[0], p[1] - self.bas[1]) >= self.hedef:
                self.durum = "takip"
            elif on < self.on_dur:
                self.durum = "sola_don"
                self.bas = p
                return 0.0, 0.7
            else:
                w = 0.0
                if sag_d < 0.8 and sol_d < 0.8:
                    w = 1.2 * (sol_d - sag_d) * 0.5
                return min(self.v, 0.18), max(-0.4, min(0.4, w))
        # takip
        if on < self.on_dur:
            self.durum = "sola_don"
            self.bas = p
            return 0.0, 0.7
        sag_il = (y < -0.05) & (x > -0.05) & (x < 0.35) & (y > -1.2)
        sag_il_d = float((-y[sag_il]).min() - yg) if sag_il.any() else 9.0
        # sağ açıklık gövde merkezinin yanına gelince (arkadaki duvar ucunu beklemeden; beklerse PD sağa kırıp ön
        # duvara giriyor, U dönüşüyle açıklık kaçıyordu)
        if sag_il_d > 0.75:
            # ağzın uzak kenarı: sağda, önde ilk duvar noktası
            uzak = (y < -0.35) & (y > -1.1) & (x > 0.0) & (x < 2.0)
            x_uzak = float(x[uzak].min()) if uzak.any() else 1.3
            self.durum = "ilerle"
            self.bas = p
            self.hedef = max(0.1, x_uzak / 2 + (-r.dingil_x_m) - 0.05)
            return min(self.v, 0.18), 0.0
        # PD: sağ yan boşluğu ve duvar açısı
        yan = (y < -0.05) & (y > -1.0) & (x > -0.3) & (x < 0.7)
        aci = 0.0
        if yan.sum() >= 6:
            px, py = x[yan], y[yan]
            # duvar çizgisine (en yakın bant) doğru uydur
            bant = py > (py.max() - 0.15) if False else (-py) < ((-py).min() + 0.12)
            if bant.sum() >= 4 and np.ptp(px[bant]) > 0.2:
                k = np.polyfit(px[bant], py[bant], 1)[0]
                aci = math.atan(k)
        e = min(sag_d, 0.8) - self.d_ref
        w = -1.6 * e + 1.4 * aci
        if sol_d < 0.18:
            w -= 0.6
        w = max(-0.6, min(0.6, w))
        v = self.v * max(0.35, 1 - abs(w) / 0.8)
        if on < 0.8:
            v = min(v, max(0.06, 0.25 * (on - self.on_dur) / 0.45 + 0.06))
        return v, w


class _Haritasiz:
    """Ortak: tarama noktaları + poz. Karar haritasızdır; poz yalnız START sanal duvarını yerinde tutmak için
    keşif beyniyle aynı HafifSLAM'dan gelir (salt odometride %14 dönüş hatası 2 dakikada sanal duvarı kaydırıyor,
    taban START'tan çıkıyordu: karşılaştırma keşif stratejisini ölçsün, konumlamayı değil)."""

    def __init__(self, robot=VARSAYILAN):
        from .slam import HafifSLAM, SlamAyari
        self.robot = robot
        self.slam = HafifSLAM(SlamAyari(), robot)
        self.poz = (0.0, 0.0, 0.0)
        self.nok = None
        self.mod = "takip"
        self.t = 0.0

    def _odo(self, artim):
        self.slam.odometri(artim, self.t)
        self.poz = self.slam.poz

    def _tarama(self, tarama):
        self.slam.tarama_isle(tarama, self.t)
        self.poz = self.slam.poz
        self.nok = self.slam.son_noktalar

    def durum(self):
        return {"poz": tuple(self.poz), "mod": self.mod, "yol": [], "hedef": None, "harita": None,
                "ek": {"cerceve": "baslangic"}}

    def _noktalar(self):
        """Tarama noktaları + START çizgisi sanal duvarı (kural: çizgi başlangıcın 0,45 m gerisinde; boyu bilinmez,
        ±1,05 m varsayıldı), odometri pozuyla gövde çerçevesine. Tabanlar da START'tan çıkmamayı bilir."""
        x, y = self.nok
        ys = np.linspace(-1.05, 1.05, 43)
        wx, wy = np.full(ys.size, -0.45), ys
        px, py, th = self.poz
        c, s = math.cos(th), math.sin(th)
        bx = c * (wx - px) + s * (wy - py)
        by = -s * (wx - px) + c * (wy - py)
        yakin = np.hypot(bx, by) < 3.0
        return np.concatenate([x, bx[yakin]]), np.concatenate([y, by[yakin]])


class SagDuvarBeyni(_Haritasiz):
    def __init__(self, robot=VARSAYILAN, v=0.22):
        super().__init__(robot)
        self.k = SagDuvar(robot, v=v)

    def adim(self, t, tarama, artim):
        self.t = t
        if artim is not None:
            self._odo(artim)
        if tarama is not None:
            self._tarama(tarama)
        if self.nok is None:
            return 0.0, 0.0
        v, w = self.k.komut(*self._noktalar(), self.poz)
        self.mod = self.k.durum
        return v, w


class RastgeleBeyni(_Haritasiz):
    def __init__(self, robot=VARSAYILAN, v=0.22, tohum=0, sapma_olasiligi=0.35):
        super().__init__(robot)
        self.v = v
        self.rng = random.Random(tohum)
        self.p = sapma_olasiligi
        self.don_bitis = None
        self.don_w = 0.0
        self._son_acik = False
        self._ileri_bitis = 0.0

    def adim(self, t, tarama, artim):
        v, w = self._adim(t, tarama, artim)
        return self._start_filtre(v, w)

    def _start_filtre(self, v, w):
        """Gövde merkezini START çizgisine (başlangıç çerçevesinde x = -0,45) 0,30 m'den yaklaştıracak komutu
        kes; yerine yerinde dönüş (rastgele taban yerinde dönerken arkası çizgiye dönük kalıp ileri sürüyordu)."""
        x, y, th = self.poz
        if abs(y) > 2.0 or x + 0.45 > 0.6:
            return v, w
        q = -self.robot.dingil_x_m
        ax, ay = x - q * math.cos(th), y - q * math.sin(th)
        th1 = th + w * 0.3
        ax1 = ax + v * 0.3 * math.cos(th + w * 0.15)
        x1 = ax1 + q * math.cos(th1)
        if x1 + 0.45 < 0.30 and x1 < x - 1e-4:
            return 0.0, (w if abs(w) > 0.1 else 0.7)
        return v, w

    def _adim(self, t, tarama, artim):
        self.t = t
        if artim is not None:
            self._odo(artim)
        if tarama is not None:
            self._tarama(tarama)
        if self.nok is None:
            return 0.0, 0.0
        x, y = self._noktalar()
        r = self.robot
        serit = (np.abs(y) <= r.yari_genislik + 0.04) & (x > r.on_x - 0.02)
        on = float((x[serit] - r.on_x).min()) if serit.any() else 9.0
        if self.don_bitis is not None:
            if t < self.don_bitis or on < 0.6:
                self.mod = "don"
                return 0.0, self.don_w
            self.don_bitis = None
            self._ileri_bitis = t + 1.5
        if on < 0.34:
            self.don_w = self.rng.choice((-0.7, 0.7))
            self.don_bitis = t + self.rng.uniform(1.0, 3.5)
            return 0.0, self.don_w
        sag = (y < -0.05) & (x > -0.3) & (x < 0.35) & (y > -1.2)
        sol = (y > 0.05) & (x > -0.3) & (x < 0.35) & (y < 1.2)
        sag_d = float((-y[sag]).min() - r.yari_genislik) if sag.any() else 9.0
        sol_d = float((y[sol]).min() - r.yari_genislik) if sol.any() else 9.0
        acik = sag_d > 0.8 or sol_d > 0.8
        if acik and not self._son_acik and t > self._ileri_bitis and self.rng.random() < self.p:
            # açıklığın ortasına gel, sonra dön
            self.don_w = -0.7 if (sag_d > 0.8 and (sol_d <= 0.8 or self.rng.random() < 0.5)) else 0.7
            self.don_bitis = t + 0.9 / 0.7 * 0 + 2.2
            self._son_acik = acik
            self.mod = "sapma"
            return 0.0, self.don_w
        self._son_acik = acik
        w = 0.0
        if sag_d < 0.8 and sol_d < 0.8:
            w = 1.2 * (sol_d - sag_d) * 0.5
        elif sag_d < 0.25:
            w = 0.4
        elif sol_d < 0.25:
            w = -0.4
        self.mod = "ileri"
        return self.v, max(-0.5, min(0.5, w))
