"""Log-odds doluluk ızgarası (dinamik büyür) ve kırpılmış uzaklık dönüşümü (pah / chamfer, scipy'siz).

Çerçeve: harita çerçevesi (m), hücre (i, j) = (x, y) dizinleri; `L[i, j]` hücrenin log-odds'u. Hücre (i, j)'nin
merkezi x0 + (i + 0,5) * coz, y0 + (j + 0,5) * coz.

Güncelleme (araştırma notu §2 değerleri; OctoMap varsayılanları): ışın boyunca boş -0,4, uçta dolu +0,85, sınırlar
[-2, 3,5]. Fark: L > 0 olan (dolu ya da dolu eğilimli) hücreye ıska yalnız -0,1 (labirent duvarı 2 mm; sıyırma
açısında duvar satırından geçen ışınlar 1 hücrelik duvarı siliyordu, geçit açılıyordu) ve isabetli ışında boş yazım
uçtan 1,5 hücre önce biter. Aynı taramada bir hücre birden çok ışınla geçilse de bir kez sayılır (numpy süslü atamasında yinelenen
dizinlere aynı değer yazılır: `L[f] = L[f] + d` her hücreyi bir kez değiştirir). Dolu: L > 0,5 (bir isabet yeter);
boş: L < -0,75 (iki ıska). Arada ya da hiç gözlenmemiş: bilinmeyen.
"""

import math

import numpy as np

BILINMEYEN, BOS, DOLU = -1, 0, 100     # durum() çıktısı (ROS OccupancyGrid ile aynı kodlar)


def pah_uzakligi(engel, maks_hucre, uzaklik0=None):
    """Kırpılmış pah uzaklığı (hücre biriminde, 8 komşu, çapraz √2). `engel` True hücrelerde 0.

    Her tur sınırı en az bir hücre ilerletir; `maks_hucre` tur sonra değer `maks_hucre`'de kırpılır. Gerçek Öklid
    uzaklığından en çok ≈ %8 sapar (pah 1 / √2). Dönüş float32, şekil `engel` ile aynı."""
    d = np.where(engel, np.float32(0), np.float32(1e6)).astype(np.float32) if uzaklik0 is None else uzaklik0
    k = np.float32(math.sqrt(2.0))
    bir = np.float32(1.0)
    n = int(math.ceil(maks_hucre)) + 1
    for _ in range(n):
        np.minimum(d[1:, :], d[:-1, :] + bir, out=d[1:, :])
        np.minimum(d[:-1, :], d[1:, :] + bir, out=d[:-1, :])
        np.minimum(d[:, 1:], d[:, :-1] + bir, out=d[:, 1:])
        np.minimum(d[:, :-1], d[:, 1:] + bir, out=d[:, :-1])
        np.minimum(d[1:, 1:], d[:-1, :-1] + k, out=d[1:, 1:])
        np.minimum(d[:-1, :-1], d[1:, 1:] + k, out=d[:-1, :-1])
        np.minimum(d[1:, :-1], d[:-1, 1:] + k, out=d[1:, :-1])
        np.minimum(d[:-1, 1:], d[1:, :-1] + k, out=d[:-1, 1:])
    np.minimum(d, np.float32(maks_hucre), out=d)
    return d


class Izgara:
    def __init__(self, cozunurluk=0.05, boyut_m=16.0, merkez=(0.0, 0.0), l_isabet=0.85, l_iska=-0.4,
                 l_min=-2.0, l_maks=3.5, esik_dolu=0.5, esik_bos=-0.75, pay_m=4.0, l_iska_dolu=-0.1,
                 uc_bosluk_hucre=1.5):
        self.coz = float(cozunurluk)
        self.l_isabet, self.l_iska, self.l_min, self.l_maks = l_isabet, l_iska, l_min, l_maks
        self.esik_dolu, self.esik_bos = esik_dolu, esik_bos
        self.l_iska_dolu = l_iska_dolu          # dolu (L > 0) hücreye ıska: ince duvar sıyırma açısında silinmesin
        self.uc_bosluk_hucre = uc_bosluk_hucre  # isabetli ışında boş yazım uçtan bu kadar hücre önce biter
        self.pay_m = pay_m
        n = int(math.ceil(boyut_m / self.coz))
        self.x0 = merkez[0] - n * self.coz / 2
        self.y0 = merkez[1] - n * self.coz / 2
        self.L = np.zeros((n, n), dtype=np.float32)
        self.yasak = np.zeros((n, n), dtype=bool)      # START gerisi (planlama + sınır dışı; eşleştirmede yok)
        self.sanal = np.zeros((n, n), dtype=bool)      # sanal duvar (planlamada dolu; eşleştirmede yok)
        self.nan_gecis = np.zeros((n, n), dtype=np.uint16)   # dönüşsüz ışınların geçtiği hücre sayacı ("dış" ipucu)
        # hücre başına isabet noktalarının toplamı / sayısı (alt-hücre duvar yeri; eşleştirme nokta-doğru uzaklığı)
        self.Sx = np.zeros((n, n), dtype=np.float32)
        self.Sy = np.zeros((n, n), dtype=np.float32)
        self.N = np.zeros((n, n), dtype=np.float32)
        self.N_tavan = 30.0
        self.surum = 0                                   # her yazmada artar (önbellek anahtarı)

    # ------------------------------------------------------------ geometri
    @property
    def nx(self):
        return self.L.shape[0]

    @property
    def ny(self):
        return self.L.shape[1]

    def hucre(self, x, y):
        i = np.floor((np.asarray(x) - self.x0) / self.coz).astype(np.int64)
        j = np.floor((np.asarray(y) - self.y0) / self.coz).astype(np.int64)
        return i, j

    def merkezler(self, i, j):
        return self.x0 + (np.asarray(i) + 0.5) * self.coz, self.y0 + (np.asarray(j) + 0.5) * self.coz

    def kapsa(self, xmin, ymin, xmax, ymax):
        """Kutu ızgaranın içinde değilse ızgarayı (pay_m payla, 64 hücrelik adımlarla) büyüt."""
        pay = self.pay_m
        x1 = self.x0 + self.nx * self.coz
        y1 = self.y0 + self.ny * self.coz
        if xmin >= self.x0 + 0.5 and ymin >= self.y0 + 0.5 and xmax <= x1 - 0.5 and ymax <= y1 - 0.5:
            return False
        nx0 = min(self.x0, xmin - pay)
        ny0 = min(self.y0, ymin - pay)
        nx1 = max(x1, xmax + pay)
        ny1 = max(y1, ymax + pay)
        di = int(math.ceil((self.x0 - nx0) / self.coz / 64.0)) * 64
        dj = int(math.ceil((self.y0 - ny0) / self.coz / 64.0)) * 64
        ei = int(math.ceil((nx1 - x1) / self.coz / 64.0)) * 64
        ej = int(math.ceil((ny1 - y1) / self.coz / 64.0)) * 64
        enx, eny = self.nx, self.ny
        yeni_n = (enx + di + ei, eny + dj + ej)
        for ad in ("L", "yasak", "sanal", "nan_gecis", "Sx", "Sy", "N"):
            eski = getattr(self, ad)
            yeni = np.zeros(yeni_n, dtype=eski.dtype)
            yeni[di:di + enx, dj:dj + eny] = eski
            setattr(self, ad, yeni)
        self.x0 -= di * self.coz
        self.y0 -= dj * self.coz
        self.surum += 1
        return True

    # ------------------------------------------------------------ güncelleme
    def isin_yaz(self, ox, oy, ux, uy, isabet):
        """Işınları yaz. ox, oy: ışın kökeni (dizi ya da sayı); ux, uy: uç; isabet: uçta yüzey var mı (yoksa ışın
        yalnız boş taşır: dönüşsüz ışının `nan_bos_m`'e kadar olan kısmı)."""
        ux = np.asarray(ux, dtype=float)
        uy = np.asarray(uy, dtype=float)
        n = ux.size
        if n == 0:
            return
        ox = np.broadcast_to(np.asarray(ox, dtype=float), ux.shape)
        oy = np.broadcast_to(np.asarray(oy, dtype=float), ux.shape)
        isabet = np.asarray(isabet, dtype=bool)
        self.kapsa(min(ux.min(), ox.min()), min(uy.min(), oy.min()), max(ux.max(), ox.max()), max(uy.max(), oy.max()))
        dx, dy = ux - ox, uy - oy
        r = np.hypot(dx, dy)
        adim = self.coz * 0.9
        # isabette son hücreyi boşaltma (uç hücresinin bir hücre öncesinde dur)
        bos_boy = np.where(isabet, r - self.uc_bosluk_hucre * self.coz, r)
        m = np.maximum(np.floor(bos_boy / adim).astype(np.int64), 0)
        top = int(m.sum())
        Lf = self.L.reshape(-1)
        if top > 0:
            bas = np.repeat(np.cumsum(m) - m, m)
            k = np.arange(top) - bas
            ray = np.repeat(np.arange(n), m)
            t = (k + 0.5) * adim / np.maximum(r[ray], 1e-9)
            px = ox[ray] + dx[ray] * t
            py = oy[ray] + dy[ray] * t
            i, j = self.hucre(px, py)
            f = i * self.ny + j
            eski = Lf[f]
            Lf[f] = np.maximum(eski + np.where(eski > 0, np.float32(self.l_iska_dolu), np.float32(self.l_iska)),
                               np.float32(self.l_min))
            nanr = ~isabet[ray]
            if nanr.any():
                g = f[nanr]
                Nf = self.nan_gecis.reshape(-1)
                Nf[g] = np.minimum(Nf[g].astype(np.int32) + 1, 60000).astype(np.uint16)
        if isabet.any():
            hx, hy = ux[isabet], uy[isabet]
            i, j = self.hucre(hx, hy)
            f = i * self.ny + j
            Lf[f] = np.minimum(Lf[f] + np.float32(self.l_isabet), np.float32(self.l_maks))
            # ortalama yer (hücre merkezine göre, float32 hassasiyeti için)
            cx, cy = self.merkezler(i, j)
            Sxf, Syf, Nf_ = self.Sx.reshape(-1), self.Sy.reshape(-1), self.N.reshape(-1)
            np.add.at(Sxf, f, (hx - cx).astype(np.float32))
            np.add.at(Syf, f, (hy - cy).astype(np.float32))
            np.add.at(Nf_, f, np.float32(1.0))
            u = np.unique(f)
            fazla = Nf_[u] > self.N_tavan
            if fazla.any():
                uu = u[fazla]
                k = self.N_tavan / Nf_[uu]
                Sxf[uu] *= k
                Syf[uu] *= k
                Nf_[uu] = self.N_tavan
        self.surum += 1

    def bos_yaz(self, xs, ys, deger=None):
        """Verilen noktaların hücrelerini kesin boş yap (robotun kendi ayak izi)."""
        self.kapsa(np.min(xs), np.min(ys), np.max(xs), np.max(ys))
        i, j = self.hucre(xs, ys)
        self.L[i, j] = np.minimum(self.L[i, j], np.float32(self.esik_bos - 0.25 if deger is None else deger))
        self.surum += 1

    # ------------------------------------------------------------ durumlar
    def dolu(self):
        return self.L > self.esik_dolu

    def bos(self):
        return self.L < self.esik_bos

    def bilinmeyen(self):
        return (self.L >= self.esik_bos) & (self.L <= self.esik_dolu)

    def durum_dizisi(self):
        """int8 dizi [i(x), j(y)]: -1 bilinmeyen, 0 boş, 100 dolu (sanal START duvarı dahil DEĞİL)."""
        d = np.full(self.L.shape, BILINMEYEN, dtype=np.int8)
        d[self.bos()] = BOS
        d[self.dolu()] = DOLU
        return d

    def kopya_sozluk(self):
        return {"cozunurluk_m": self.coz, "orijin": (self.x0, self.y0), "L": self.L.copy(),
                "yasak": self.yasak.copy(), "sanal": self.sanal.copy(), "Sx": self.Sx.copy(), "Sy": self.Sy.copy(),
                "N": self.N.copy()}

    @classmethod
    def sozlukten(cls, s, **ayar):
        g = cls(cozunurluk=s["cozunurluk_m"], boyut_m=1.0, **ayar)
        g.x0, g.y0 = s["orijin"]
        g.L = np.array(s["L"], dtype=np.float32)
        g.yasak = np.array(s["yasak"], dtype=bool)
        g.sanal = np.array(s["sanal"], dtype=bool)
        g.nan_gecis = np.zeros(g.L.shape, dtype=np.uint16)
        for ad in ("Sx", "Sy", "N"):
            setattr(g, ad, np.array(s[ad], dtype=np.float32) if ad in s else np.zeros(g.L.shape, dtype=np.float32))
        return g


ALT_HUCRE_M = 0.15   # bu uzaklığın altında alt-hücre (isabet ortalaması) uzaklığı kullanılır; 0 = kapalı


class UzaklikAlani:
    """Bir pencerede dolu hücrelere kırpılmış uzaklık (m) + çift doğrusal ara değer ve eğim. Eşleştirme için."""

    def __init__(self, izgara, cx, cy, yaricap_m=8.0, maks_m=0.30, esik_L=None):
        g = izgara
        c = g.coz
        i0, j0 = g.hucre(cx - yaricap_m, cy - yaricap_m)
        i1, j1 = g.hucre(cx + yaricap_m, cy + yaricap_m)
        i0, j0 = max(int(i0), 0), max(int(j0), 0)
        i1, j1 = min(int(i1), g.nx - 1), min(int(j1), g.ny - 1)
        self.i0, self.j0 = i0, j0
        self.coz = c
        self.x0 = g.x0 + i0 * c
        self.y0 = g.y0 + j0 * c
        dolu = g.L[i0:i1 + 1, j0:j1 + 1] > (g.esik_dolu if esik_L is None else esik_L)
        self.dolu_sayisi = int(dolu.sum())
        self.maks_m = maks_m
        self.d = pah_uzakligi(dolu, maks_m / c) * np.float32(c)
        self.nx, self.ny = self.d.shape
        self.merkez = (cx, cy)
        self.yaricap = yaricap_m
        self.surum = g.surum
        self.izgara = g
        self.esik_L = g.esik_dolu if esik_L is None else esik_L

    def deger_egim(self, px, py):
        """(d, dd/dx, dd/dy, içeride) çift doğrusal (hücre merkezleri arası)."""
        fx = (px - self.x0) / self.coz - 0.5
        fy = (py - self.y0) / self.coz - 0.5
        ic = (fx >= 0) & (fx < self.nx - 1) & (fy >= 0) & (fy < self.ny - 1)
        i = np.clip(np.floor(fx).astype(np.int64), 0, self.nx - 2)
        j = np.clip(np.floor(fy).astype(np.int64), 0, self.ny - 2)
        tx = np.clip(fx - i, 0, 1)
        ty = np.clip(fy - j, 0, 1)
        d = self.d
        a, b, cc, e = d[i, j], d[i + 1, j], d[i, j + 1], d[i + 1, j + 1]
        v = (1 - tx) * (1 - ty) * a + tx * (1 - ty) * b + (1 - tx) * ty * cc + tx * ty * e
        gx = ((1 - ty) * (b - a) + ty * (e - cc)) / self.coz
        gy = ((1 - tx) * (cc - a) + tx * (e - b)) / self.coz
        v = np.where(ic, v, self.maks_m)
        gx = np.where(ic, gx, 0.0)
        gy = np.where(ic, gy, 0.0)
        yakin = ic & (v < ALT_HUCRE_M)
        if yakin.any():
            v2, gx2, gy2, ok = self._alt_hucre(px[yakin], py[yakin])
            idx = np.flatnonzero(yakin)[ok]
            v[idx], gx[idx], gy[idx] = v2[ok], gx2[ok], gy2[ok]
        return v, gx, gy, ic

    def _alt_hucre(self, px, py, r=2):
        """Yakındaki (5x5) dolu hücrelerin isabet ortalamalarına: en yakın iki ortalama 2-12 cm arasındaysa ikisinden
        geçen doğruya, değilse en yakın ortalamaya uzaklık (m) ve eğimi. Hücre merkezli pah uzaklığının duvar içindeki
        düz tabanını (2 satıra yayılmış ince duvarda eğim 0) kaldırır."""
        g = self.izgara
        i, j = g.hucre(px, py)
        o = np.arange(-r, r + 1)
        DI, DJ = np.meshgrid(o, o, indexing="ij")
        I = np.clip(i[:, None] + DI.ravel()[None, :], 0, g.nx - 1)
        J = np.clip(j[:, None] + DJ.ravel()[None, :], 0, g.ny - 1)
        N = g.N[I, J]
        dolu = (g.L[I, J] > self.esik_L) & (N > 0)
        cx, cy = g.merkezler(I, J)
        Nn = np.maximum(N, 1.0)
        mx = cx + g.Sx[I, J] / Nn
        my = cy + g.Sy[I, J] / Nn
        dx = px[:, None] - mx
        dy = py[:, None] - my
        d2 = np.where(dolu, dx * dx + dy * dy, np.inf)
        ok = np.isfinite(d2).any(axis=1)
        k1 = np.argmin(d2, axis=1)
        sat = np.arange(px.size)
        d1 = np.sqrt(d2[sat, k1])
        d2b = d2.copy()
        d2b[sat, k1] = np.inf
        k2 = np.argmin(d2b, axis=1)
        m1x, m1y = mx[sat, k1], my[sat, k1]
        m2x, m2y = mx[sat, k2], my[sat, k2]
        tx, ty = m2x - m1x, m2y - m1y
        tl = np.hypot(tx, ty)
        cizgi = np.isfinite(d2b[sat, k2]) & (tl > 0.02) & (tl < 0.12)
        tl = np.maximum(tl, 1e-9)
        nx_, ny_ = -ty / tl, tx / tl
        sd = (px - m1x) * nx_ + (py - m1y) * ny_
        v = np.where(cizgi, np.abs(sd), d1)
        sg = np.sign(sd)
        sg = np.where(sg == 0, 1.0, sg)
        d1s = np.maximum(d1, 1e-6)
        gx = np.where(cizgi, sg * nx_, (px - m1x) / d1s)
        gy = np.where(cizgi, sg * ny_, (py - m1y) / d1s)
        return v, gx, gy, ok
