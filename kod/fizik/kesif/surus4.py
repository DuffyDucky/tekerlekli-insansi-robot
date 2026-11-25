"""v4 sürüşü: ölçüye dayalı hız zarfı (sabit zamanlayıcı ve sabit 1,0 m şerit kapısı yerine).

    from kesif.surus4 import ZarfIzleyici, fren_hizi, supurme_carpar
    iz = ZarfIzleyici(IzleyiciAyar(...), a_zarf=0.5, tepki_s=0.15)

`ZarfIzleyici`, `gezinme.izleyici.YolIzleyici`'nin alt sınıfıdır; gezinmedeki dosya değişmez. Yalnız `komut`'taki iki
hız sınırı değişir (geri kalan satırlar YolIzleyici.komut'la aynı):
- Yumuşak varış: YolIzleyici v <= k_varis * kalan (doğrusal; hız kalan yolla orantılı, üstel yaklaşım, köşe başına
  ~1 s 0,10 m/s altı "kuyruk") kullanır. Burada fren zarfı: v <= fren_hizi(kalan), yani v * tepki + v² / (2 a) <= kalan.
- Engel rampası: doğrusal rampa yerine v <= fren_hizi(on_mesafe - dur_mesafe_m). Dur / kalk eşikleri aynı.
`hizala_iste` (beyin koyar, bir adım geçerli): yön hatası donus_cik_rad'ı aşıyorsa yay yerine yerinde hizalan.
Her adımda saf takip açısı (son_alfa), eğriliği (son_kappa) ve bacak sonuna kalan yol (son_kalan) saklanır; beyin hızlı
kip iznini bunlardan verir (beyin._hiz_ayarla_v4).

`supurme_carpar`: gövdenin önündeki yayı (sabit v, eğrilik kappa'ya a_w ivmesiyle yaklaşan w) kısa bir ufukta sürer;
şişirilmiş ayak izi son taramanın bir noktasını içine alırsa ya da çevresi haritada dolu / sanal hücreye değerse True.
Izgara, dik açı ya da hücre boyu varsayımı yok: yalnız tarama noktaları, ızgara olasılıkları ve robot ölçüleri.
"""

import math

import numpy as np

from gezinme.izleyici import YolIzleyici, _izdusum, _nokta, _uzunluk, sar


def fren_hizi(d, a=0.5, tepki_s=0.15):
    """d metrede durabilecek en büyük hız: v * tepki + v² / (2 a) <= d (d <= 0 -> 0)."""
    if d <= 0:
        return 0.0
    at = a * tepki_s
    return -at + math.sqrt(at * at + 2.0 * a * d)


class ZarfIzleyici(YolIzleyici):
    def __init__(self, ayar=None, a_zarf=0.5, tepki_s=0.15):
        super().__init__(ayar)
        self.a_zarf = float(a_zarf)
        self.tepki_s = float(tepki_s)
        self.son_alfa = None
        self.son_kappa = 0.0
        self.son_kalan = None
        self.hizala_iste = False       # beyin: süpürme v_seyir'de de çarpıyor -> önce yerinde hizalan
        self.kappa_iste = None         # v5 beyin: bu adımda saf takip eğriliği yerine bu eğrilik (yay kaçınma)

    def _zarf(self, d):
        return fren_hizi(d, self.a_zarf, self.tepki_s)

    def komut(self, poz, on_mesafe=None):
        a = self.ayar
        self.son_alfa = None
        ki, self.kappa_iste = self.kappa_iste, None      # yalnız bu adım geçerli
        x, y, th = float(poz[0]), float(poz[1]), float(poz[2])
        if self._tek_nokta and self.yol:
            self.yol_ver([(x, y), self.yol[0]])
        if self._bitti or not self._bacaklar:
            self._bitti = True
            return self._dur(bitti=True, mod="bitti" if self.yol else "bos")
        c, s_ = math.cos(th), math.sin(th)
        rx, ry = x + a.donme_merkezi_x * c, y + a.donme_merkezi_x * s_
        son_bacak = self._bi == len(self._bacaklar) - 1
        bacak = self._bacaklar[self._bi]
        L = _uzunluk(bacak)
        s_r, _ = _izdusum(bacak, rx, ry, self._s - a.arama_geri_m, self._s + a.arama_ileri_m)
        if s_r is None:
            s_r, _ = _izdusum(bacak, rx, ry)
        self._s = max(self._s, s_r)
        if son_bacak:
            s_b, _ = _izdusum(bacak, x, y)
            son = bacak[-1]
            d_son = math.hypot(son[0] - x, son[1] - y)
            kalan = max(0.0, L - s_b)
            if d_son < a.varis_payi_m or s_b >= L - 1e-3:
                self._bitti = True
                return self._dur(bitti=True, mod="bitti", kalan_m=0.0)
        else:
            kalan = max(0.0, L - self._s - a.kose_payi_m)
            if kalan <= 0.0:
                self._bi += 1
                self._s = 0.0
                self._yerinde = True
                self.kappa_iste = ki
                return self.komut(poz, on_mesafe)
        hx, hy = _nokta(bacak, self._s + a.bakis_m)
        alfa = sar(math.atan2(hy - ry, hx - rx) - th)
        kalan_top = kalan + sum(_uzunluk(b) for b in self._bacaklar[self._bi + 1:])
        om = on_mesafe if (on_mesafe is not None and math.isfinite(on_mesafe)) else None
        onceki = self._yerinde
        if self.hizala_iste:
            self.hizala_iste = False
            if abs(alfa) > a.donus_cik_rad:
                self._yerinde = True
        if self._yerinde or abs(alfa) > a.donus_gir_rad:
            self._yerinde = abs(alfa) > a.donus_cik_rad
        if self._yerinde:
            if not onceki or self._yon == 0 or abs(alfa) < 2.6:
                self._yon = 1.0 if alfa >= 0 else -1.0
            if om is not None and om < a.donus_dur_mesafe_m:
                self._bekliyor = True
                return self._dur(durdu=True, mod="bekle", hedef=(hx, hy), kalan_m=kalan_top)
            self._bekliyor = False
            w = self._yon * max(a.w_yerinde_min, min(a.w_yerinde, a.k_yerinde * abs(alfa)))
            if abs(self._v) > 0.02:
                v, w = self._sinirla(0.0, 0.0)
            else:
                self._v = 0.0
                v, w = 0.0, self._sinirla(0.0, w)[1]
            return self._komut(v, w, mod="yerinde", hedef=(hx, hy), kalan_m=kalan_top)
        self._yon = 0
        if om is not None:
            if self._bekliyor and om < a.kalk_mesafe_m:
                return self._dur(durdu=True, mod="bekle", hedef=(hx, hy), kalan_m=kalan_top)
            if om < a.dur_mesafe_m:
                self._bekliyor = True
                return self._dur(durdu=True, mod="bekle", hedef=(hx, hy), kalan_m=kalan_top)
        self._bekliyor = False
        Ld = math.hypot(hx - rx, hy - ry) or a.bakis_m
        kappa = 2.0 * math.sin(alfa) / Ld
        self.son_alfa, self.son_kappa, self.son_kalan = alfa, kappa, kalan
        if ki is not None:                       # v5: bir adımlık eğrilik isteği (son_kappa saf takibinki kalır)
            kappa = float(ki)
        v = a.v_max
        if abs(kappa) * v > a.w_max:
            v = a.w_max / abs(kappa)
        # v4: fren zarfı (bacak / yol sonu)
        v = min(v, max(a.v_min, self._zarf(kalan)))
        # v4: öndeki engele fren zarfı (dur eşiği payı korunur)
        if om is not None:
            v = min(v, max(a.v_min, self._zarf(om - a.dur_mesafe_m)))
        w = v * kappa
        v, w = self._sinirla(v, w)
        return self._komut(v, w, mod="izle", hedef=(hx, hy), kalan_m=kalan_top)


def _cevre(robot, pay, adim=0.04):
    """Gövde çerçevesinde şişirilmiş ayak izi çevresi (x, y) dizileri (gövde merkezi orijin)."""
    hx, hy = robot.derinlik_m / 2 + pay, robot.genislik_m / 2 + pay
    ux = np.arange(-hx, hx + 1e-9, adim)
    uy = np.arange(-hy, hy + 1e-9, adim)
    px = np.concatenate([ux, ux, np.full(uy.size, -hx), np.full(uy.size, hx)])
    py = np.concatenate([np.full(ux.size, -hy), np.full(ux.size, hy), uy, uy])
    return px, py


def yay_pozlari(v, w0, kappa, q, ufuk_m, a_w=3.0, w_max=1.0, dt=0.05):
    """Gövde çerçevesinde (başlangıç gövde merkezi orijin, x ileri) öngörülen gövde merkezi pozları [(x, y, th)].
    Arka dingil (gövde x = q) tek tekerlekli gibi v ile gider; w, v * kappa'ya a_w ile yaklaşır."""
    out = []
    if v <= 1e-3:
        return out
    ax, ay, th = q, 0.0, 0.0
    w = float(w0)
    s = 0.0
    while s < ufuk_m:
        hedef = max(-w_max, min(w_max, v * kappa))
        w += max(-a_w * dt, min(a_w * dt, hedef - w))
        ort = th + 0.5 * w * dt
        ax += v * dt * math.cos(ort)
        ay += v * dt * math.sin(ort)
        th += w * dt
        s += v * dt
        out.append((ax - q * math.cos(th), ay - q * math.sin(th), th))
    return out


def supurme_carpar(pozlar, robot, pay, tarama_xy=None, dolu_mu=None, govde_poz=None):
    """pozlar: gövde çerçevesinde öngörülen gövde merkezi pozları. tarama_xy: son tarama (gövde çerçevesi x, y).
    dolu_mu(wx, wy): harita sorgusu (dünya çerçevesi); govde_poz: o anki SLAM gövde pozu. Çarpar -> True."""
    if not pozlar:
        return False
    hx, hy = robot.derinlik_m / 2 + pay, robot.genislik_m / 2 + pay
    P = np.array(pozlar)
    if tarama_xy is not None:
        x, y = tarama_xy
        if x.size:
            # yalnız ufuk içindeki noktalar
            r = math.hypot(np.abs(P[:, 0]).max() + hx, np.abs(P[:, 1]).max() + hy) + 0.1
            m = (x * x + y * y) < r * r
            x, y = x[m], y[m]
            if x.size:
                c, s = np.cos(P[:, 2])[:, None], np.sin(P[:, 2])[:, None]
                dx, dy = x[None, :] - P[:, 0:1], y[None, :] - P[:, 1:2]
                u = c * dx + s * dy
                vv = -s * dx + c * dy
                if bool(((np.abs(u) <= hx) & (np.abs(vv) <= hy)).any()):
                    return True
    if dolu_mu is not None and govde_poz is not None:
        cx, cy = _cevre(robot, pay)
        X, Y, T = govde_poz
        c0, s0 = math.cos(T), math.sin(T)
        c, s = np.cos(P[:, 2])[:, None], np.sin(P[:, 2])[:, None]
        bx = P[:, 0:1] + c * cx[None, :] - s * cy[None, :]
        by = P[:, 1:2] + s * cx[None, :] + c * cy[None, :]
        wx = X + c0 * bx - s0 * by
        wy = Y + s0 * bx + c0 * by
        if dolu_mu(wx.ravel(), wy.ravel()):
            return True
    return False
