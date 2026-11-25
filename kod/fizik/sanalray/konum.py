"""Konumlama: arka dingil enkoder ölü hesabı + etiket ölçümüyle genişletilmiş Kalman süzgeci (EKF). Saf numpy.

Neden EKF (parçacık süzgeci değil): etiket kimliği tekildir (veri eşleme belirsizliği yok), bilinen etiket yeri tek
tepeli bir olabilirlik verir; hareket modeli düzgün ve durum 3 boyutlu. Tek tepeli dağılım için EKF yeterli, ucuz (Pi'de
mikro saniyeler) ve belirsizliği açık bir kovaryansla taşır: etiket görünmezken odometri gürültüsüyle büyür, etiketle
küçülür. Çok tepeli durum yalnız kayıp robotta, ilk etiketten önce vardır; orada süzgeç hiç başlatılmaz (konum
"bilinmiyor"), ilk güvenilir etiketin tam pozundan (solvePnP) başlatılır. Yanlış ölçüme karşı Mahalanobis kapısı.

Durum: arka dingil ortasının pozu (x, y, th) (enkoder artımının noktası; gövde merkezi bunun 0,185 m önü) ve dönüş
ölçeği k (gerçek dönüş = k x odometri dönüşü): odometrinin dönüş yanlılığı (%0 / 14 / 25) bağımsız adım gürültüsü sayılırsa
kovaryans yanlılığın doğrusal birikimini karşılamıyor (geliştirmede 90° köşeden sonra 0,9° std ile 13° gerçek hata,
etiketler kapıdan reddedildi); k durumda kestirilir (keşif deneyinin k_don öğrenmesinin süzgeç içi karşılığı).
Ölçüm (her algılanan etiket): kameradan yatay menzil, kerteriz ve etiket normalinin kamera yönüne göre açısı psi.
Kamera gövdede kafa pan eksenine göre (0,0651, 0) m (CAD), pan açısı phi ile döner."""

import math

import numpy as np

XR = -0.185                    # arka dingil (odometri noktası), gövde merkezine göre
KAMERA_X = 0.0651              # kamera, pan eksenine (gövde merkezi) göre ileri (CAD)


def sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class Ayar:
    ALANLAR = dict(
        a_oteleme=0.04,        # öteleme gürültüsü std / m (odometri)
        a_donus=0.05,          # dönüş std / rad (rastgele kısım; yanlılık ayrı durum: dönüş ölçeği)
        s_olcek=0.15,          # dönüş ölçeğinin ön std'si (1 ± 0,15: %0-25 dönüş fazlasını kapsar)
        olcek_kayma=0.002,     # dönüş ölçeği rastgele yürüyüşü (1 / sqrt(rad))
        a_kayma=0.02,          # yanal kayma std m / rad (yerinde dönüş)
        a_yon_yol=0.02,        # yön std rad / m (düz giderken yön kayması)
        s_menzil_0=0.02, s_menzil_k=0.012,    # menzil std = s0 + k d^2 (m)
        s_kerteriz=math.radians(0.5),         # kerteriz std (rad); görünürlük haritası ortanca 0,03-0,08°, kafa / gövde eğimi payı
        s_psi_0=math.radians(3.0), s_psi_k=math.radians(3.0),   # psi std = s0 + k d (rad); 4 m ötesi ters çözüm (100°+) kapıyla atılır
        kapi=13.8,             # Mahalanobis kapısı (2 sd, %99,9)
        kapi_psi=9.0,          # psi kapısı (1 sd)
        en_cok_menzil=11.0,    # bundan uzak etiket ölçümü kullanılmaz (m); uzakta menzil std büyük: fiilen yalnız kerteriz
        baslat_en_cok_menzil=3.5,   # kayıp robot süzgeci yalnız bu menzil içindeki etiketle başlatır (psi güvenilir)
    )

    def __init__(self, **k):
        for a, v in self.ALANLAR.items():
            setattr(self, a, v)
        for a, v in k.items():
            if a not in self.ALANLAR:
                raise ValueError(a)
            setattr(self, a, v)


class EtiketEKF:
    def __init__(self, etiketler, ayar=None):
        """etiketler: {kimlik: {"x", "y", "yaw", "boy_m", ...}} (etiket planı; harita çerçevesi)."""
        self.E = etiketler
        self.a = ayar or Ayar()
        self.r = None
        self.P = None
        self.son_olcum_t = None
        self.kabul = 0
        self.ret = 0
        self.ardisik_ret = 0

    # ------------------------------------------------------------ durum
    @property
    def hazir(self):
        return self.r is not None

    def baslat(self, govde_poz, std=(0.1, 0.1, math.radians(5))):
        x, y, th = govde_poz
        c = float(self.r[3]) if self.r is not None else 1.0           # öğrenilmiş dönüş ölçeği korunur
        sc = math.sqrt(self.P[3, 3]) if self.P is not None else self.a.s_olcek
        self.r = np.array([x + XR * math.cos(th), y + XR * math.sin(th), th, c], float)
        self.P = np.diag(np.square(list(std) + [sc]))

    def govde(self):
        if self.r is None:
            return None
        x, y, th = self.r[:3]
        return (float(x - XR * math.cos(th)), float(y - XR * math.sin(th)), float(th))

    def olcek(self):
        """Öğrenilen dönüş ölçeği (gerçek dönüş / odometri dönüşü)."""
        return None if self.r is None else float(self.r[3])

    def std(self):
        """(konum std m: büyük eksen, yön std rad)."""
        if self.P is None:
            return None
        ev = np.linalg.eigvalsh(self.P[:2, :2])
        return float(math.sqrt(max(ev.max(), 0.0))), float(math.sqrt(max(self.P[2, 2], 0.0)))

    # ------------------------------------------------------------ hareket
    def tahmin(self, artim):
        if self.r is None:
            return
        dx, dy, dth_o = artim
        x, y, th, k = self.r
        dth = k * dth_o                                   # dönüş ölçeği durumda (odometri dönüş yanlılığı)
        c, s = math.cos(th), math.sin(th)
        wx, wy = c * dx - s * dy, s * dx + c * dy
        self.r = np.array([x + wx, y + wy, sar(th + dth), k])
        F = np.array([[1, 0, -wy, 0], [0, 1, wx, 0], [0, 0, 1.0, dth_o], [0, 0, 0, 1.0]])
        a = self.a
        ds = math.hypot(dx, dy)
        sx = a.a_oteleme * ds
        sy = a.a_oteleme * ds + a.a_kayma * abs(dth)
        st = a.a_donus * abs(dth) + a.a_yon_yol * ds
        G = np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1.0, 0], [0, 0, 0, 1.0]])
        Q = G @ np.diag([sx * sx + 1e-10, sy * sy + 1e-10, st * st + 1e-12, a.olcek_kayma ** 2 * abs(dth_o) + 1e-12]) @ G.T
        self.P = F @ self.P @ F.T + Q

    # ------------------------------------------------------------ ölçüm
    def _kamera(self, r, phi):
        x, y, th = r[:3]
        ox, oy = -XR + KAMERA_X * math.cos(phi), KAMERA_X * math.sin(phi)
        c, s = math.cos(th), math.sin(th)
        return x + c * ox - s * oy, y + s * ox + c * oy, c * ox - s * oy, s * ox + c * oy

    def olcum(self, kimlik, menzil, kerteriz, psi, phi=0.0, t=None):
        """Tek etiket ölçümü. Döner: "kabul" | "ret" | "uzak" | "bilinmeyen" | "hazir_degil"."""
        e = self.E.get(kimlik)
        if e is None:
            return "bilinmeyen"
        if self.r is None:
            return "hazir_degil"
        a = self.a
        if menzil > a.en_cok_menzil:
            return "uzak"
        cx, cy, oxw, oyw = self._kamera(self.r, phi)
        Dx, Dy = e["x"] - cx, e["y"] - cy
        q = Dx * Dx + Dy * Dy
        rr = math.sqrt(q)
        th = self.r[2]
        b_hat = sar(math.atan2(Dy, Dx) - th - phi)
        H = np.array([[-Dx / rr, -Dy / rr, (Dx * oyw - Dy * oxw) / rr, 0.0],
                      [Dy / q, -Dx / q, (-Dx * oxw - Dy * oyw) / q - 1.0, 0.0]])
        sr = a.s_menzil_0 + a.s_menzil_k * menzil * menzil
        R = np.diag([sr * sr, a.s_kerteriz ** 2])
        nu = np.array([menzil - rr, sar(kerteriz - b_hat)])
        S = H @ self.P @ H.T + R
        d2 = float(nu @ np.linalg.solve(S, nu))
        if d2 > a.kapi:
            self.ret += 1
            self.ardisik_ret += 1
            return "ret"
        K = self.P @ H.T @ np.linalg.inv(S)
        self.r = self.r + K @ nu
        self.r[2] = sar(self.r[2])
        self.P = (np.eye(4) - K @ H) @ self.P
        # psi (etiket normaline göre yön): ayrı, kapılı
        psi_hat = sar(e["yaw"] - self.r[2] - phi)
        sp = a.s_psi_0 + a.s_psi_k * menzil
        Hp = np.array([[0.0, 0.0, -1.0, 0.0]])
        Sp = float((Hp @ self.P @ Hp.T)[0, 0]) + sp * sp
        nup = sar(psi - psi_hat)
        if nup * nup / Sp < a.kapi_psi:
            Kp = (self.P @ Hp.T) / Sp
            self.r = self.r + Kp.ravel() * nup
            self.r[2] = sar(self.r[2])
            self.P = (np.eye(4) - Kp @ Hp) @ self.P
        self.P = 0.5 * (self.P + self.P.T)
        self.kabul += 1
        self.ardisik_ret = 0
        self.son_olcum_t = t
        return "kabul"

    def tek_etiketten(self, kimlik, menzil, kerteriz, psi, phi=0.0):
        """Etiketin bilinen yerinden ve tam ölçümden gövde pozu (kayıp robot başlatma). Döner (x, y, th) ya da None."""
        e = self.E.get(kimlik)
        if e is None:
            return None
        th_c = sar(e["yaw"] - psi)
        f, l = menzil * math.cos(kerteriz), menzil * math.sin(kerteriz)
        cx = e["x"] - (math.cos(th_c) * f - math.sin(th_c) * l)
        cy = e["y"] - (math.sin(th_c) * f + math.cos(th_c) * l)
        th = sar(th_c - phi)
        kx, ky = KAMERA_X * math.cos(phi), KAMERA_X * math.sin(phi)
        gx = cx - (math.cos(th) * kx - math.sin(th) * ky)
        gy = cy - (math.sin(th) * kx + math.cos(th) * ky)
        return (gx, gy, th)

    def baslat_etiketten(self, kimlik, menzil, kerteriz, psi, phi=0.0):
        p = self.tek_etiketten(kimlik, menzil, kerteriz, psi, phi)
        if p is None:
            return False
        a = self.a
        sp = a.s_psi_0 + a.s_psi_k * menzil
        sxy = a.s_menzil_0 + a.s_menzil_k * menzil ** 2 + sp * menzil
        self.baslat(p, std=(sxy, sxy, sp))
        return True
