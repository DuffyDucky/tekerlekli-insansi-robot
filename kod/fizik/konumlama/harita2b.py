"""2B harita: yükleme, vektörleştirilmiş ışın izleme, uzaklık ve serbest alan ızgaraları.

Biçim `kod/SIMULASYON.md` "Yeni harita" (aynı JSON: `boyut_m`, `cevre_duvari` (varsayılan true), `duvarlar`
[x1, y1, x2, y2], `engeller` kutu (sol alt köşe x, y + g, d) / daire (x, y, r), `baslangic`). Birim metre, x sağa,
y yukarı, açı radyan, saat yönü tersi +. `kod/araclar/sahte_esp32/harita.py` ile aynı geometriyi kurar ama ona
bağlı değildir (yalnız numpy + standart kitaplık; MuJoCo yok).
"""

import json
import math
import os

import numpy as np

# kod/fizik/konumlama -> kod/araclar/haritalar
HARITA_KLASORU = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                              "araclar", "haritalar")

_EPS = 1e-9


class HaritaHatasi(ValueError):
    pass


class Harita2B:
    """Tek harita. Geometri numpy dizilerinde; ızgaralar ilk gerektiğinde (ya da `hazirla`) kurulur.

    parcalar : (S, 4) duvar parçaları (kutuların dört kenarı ve çevre duvarı dahil)
    daireler : (C, 3) x, y, r
    kutular  : (K, 4) x0, y0, x1, y1 (içi dolu sayılır)
    """

    def __init__(self, veri, ad=None):
        self.veri = veri
        self.ad = ad or veri.get("ad", "adsiz")
        try:
            self.genislik, self.yukseklik = (float(v) for v in veri["boyut_m"])
        except (KeyError, TypeError, ValueError):
            raise HaritaHatasi("%s: boyut_m [genislik, yukseklik] gerekli" % self.ad)
        parcalar, daireler, kutular = [], [], []
        for d in veri.get("duvarlar", []):
            if len(d) != 4:
                raise HaritaHatasi("%s: duvar [x1, y1, x2, y2] olmalı: %r" % (self.ad, d))
            parcalar.append([float(v) for v in d])
        for e in veri.get("engeller", []):
            tur = e.get("tur")
            if tur == "kutu":
                x, y, g, h = float(e["x"]), float(e["y"]), float(e["g"]), float(e["d"])
                k = [(x, y), (x + g, y), (x + g, y + h), (x, y + h)]
                for i in range(4):
                    parcalar.append(list(k[i] + k[(i + 1) % 4]))
                kutular.append([min(x, x + g), min(y, y + h), max(x, x + g), max(y, y + h)])
            elif tur == "daire":
                daireler.append([float(e["x"]), float(e["y"]), float(e["r"])])
            else:
                raise HaritaHatasi("%s: bilinmeyen engel türü: %r" % (self.ad, tur))
        w, h = self.genislik, self.yukseklik
        self.cevre_duvari = bool(veri.get("cevre_duvari", True))
        if self.cevre_duvari:
            parcalar += [[0, 0, w, 0], [w, 0, w, h], [w, h, 0, h], [0, h, 0, 0]]
        self.parcalar = np.asarray(parcalar, dtype=float).reshape(-1, 4)
        self.daireler = np.asarray(daireler, dtype=float).reshape(-1, 3)
        self.kutular = np.asarray(kutular, dtype=float).reshape(-1, 4)
        b = veri.get("baslangic", {}) or {}
        self.baslangic = (float(b.get("x", w / 2)), float(b.get("y", h / 2)),
                          math.radians(float(b.get("aci_derece", 0))))
        self._izgara = None      # (cozunurluk, pay, x0, y0, nx, ny, uzaklik, serbest)

    # ------------------------------------------------------------ yükleme

    @classmethod
    def dosyadan(cls, yol):
        """Dosya yolu ya da `kod/araclar/haritalar/` altındaki ad (uzantısız olabilir)."""
        if not os.path.exists(yol):
            aday = os.path.join(HARITA_KLASORU, yol if yol.endswith(".json") else yol + ".json")
            if os.path.exists(aday):
                yol = aday
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
        return cls(veri, ad=veri.get("ad") or os.path.splitext(os.path.basename(yol))[0])

    # ------------------------------------------------------------ ışın izleme

    def isin_izle(self, ox, oy, acilar, menzil=np.inf, parca_boyu=400_000):
        """Vektörleştirilmiş ışın izleme.

        ox, oy : (P,) ışın başlangıçları (dünya)
        acilar : (P, B) ya da (B,) dünya çerçevesinde ışın yönleri (rad)
        menzil : bundan uzak çarpma `inf` döner
        Dönüş  : (P, B) ilk yüzeye uzaklık; yüzey yoksa / menzil dışıysa `np.inf`.
        """
        ox = np.atleast_1d(np.asarray(ox, dtype=float))
        oy = np.atleast_1d(np.asarray(oy, dtype=float))
        acilar = np.asarray(acilar, dtype=float)
        if acilar.ndim == 1:
            acilar = np.broadcast_to(acilar, (ox.shape[0], acilar.shape[0]))
        P, B = acilar.shape
        sonuc = np.full((P, B), np.inf)
        S, C = len(self.parcalar), len(self.daireler)
        if S + C == 0 or P == 0:
            return sonuc
        # bellek sınırı: bir seferde ~parca_boyu (P*B*S) öğe
        adim = max(1, int(parca_boyu // max(1, B * max(S, C, 1))))
        for bas in range(0, P, adim):
            sl = slice(bas, bas + adim)
            sonuc[sl] = self._isin_parca(ox[sl], oy[sl], acilar[sl])
        if np.isfinite(menzil):
            sonuc[sonuc > menzil] = np.inf
        return sonuc

    def _isin_parca(self, ox, oy, acilar):
        dx = np.cos(acilar)[..., None]          # (p, B, 1)
        dy = np.sin(acilar)[..., None]
        en_iyi = np.full(acilar.shape, np.inf)
        if len(self.parcalar):
            x1, y1, x2, y2 = (self.parcalar[:, i] for i in range(4))
            ex, ey = x2 - x1, y2 - y1           # (S,)
            ax = (x1[None, :] - ox[:, None])[:, None, :]      # (p, 1, S)
            ay = (y1[None, :] - oy[:, None])[:, None, :]
            pay = dx * ey - dy * ex                           # (p, B, S)
            with np.errstate(divide="ignore", invalid="ignore"):
                t = (ax * ey - ay * ex) / pay
                u = (ax * dy - ay * dx) / pay
            gecerli = (np.abs(pay) > 1e-12) & (t > _EPS) & (u >= 0.0) & (u <= 1.0)
            t = np.where(gecerli, t, np.inf)
            en_iyi = np.minimum(en_iyi, t.min(axis=2))
        if len(self.daireler):
            cx, cy, r = self.daireler[:, 0], self.daireler[:, 1], self.daireler[:, 2]
            fx = (ox[:, None] - cx[None, :])[:, None, :]      # (p, 1, C)
            fy = (oy[:, None] - cy[None, :])[:, None, :]
            b = fx * dx + fy * dy                             # (p, B, C)
            c = fx * fx + fy * fy - r * r
            ayirt = b * b - c
            kok = np.sqrt(np.maximum(ayirt, 0.0))
            t1 = -b - kok
            t2 = -b + kok
            t = np.where(t1 > _EPS, t1, t2)                   # içerideyse çıkış noktası
            t = np.where((ayirt >= 0) & (t > _EPS), t, np.inf)
            en_iyi = np.minimum(en_iyi, t.min(axis=2))
        return en_iyi

    # ------------------------------------------------------------ uzaklık / doluluk

    def geometri_uzakligi(self, px, py, parca_boyu=2_000_000):
        """Her noktanın en yakın yüzeye (duvar parçası ya da daire çevresi) uzaklığı (analitik)."""
        px = np.asarray(px, dtype=float).ravel()
        py = np.asarray(py, dtype=float).ravel()
        n = px.shape[0]
        sonuc = np.full(n, np.inf)
        S = max(len(self.parcalar), len(self.daireler), 1)
        adim = max(1, parca_boyu // S)
        for bas in range(0, n, adim):
            x = px[bas:bas + adim, None]
            y = py[bas:bas + adim, None]
            d = np.full(x.shape[0], np.inf)
            if len(self.parcalar):
                x1, y1, x2, y2 = (self.parcalar[:, i] for i in range(4))
                ex, ey = x2 - x1, y2 - y1
                boy2 = ex * ex + ey * ey
                with np.errstate(divide="ignore", invalid="ignore"):
                    t = np.where(boy2 > 0, ((x - x1) * ex + (y - y1) * ey) / boy2, 0.0)
                t = np.clip(t, 0.0, 1.0)
                d = np.minimum(d, np.hypot(x - (x1 + t * ex), y - (y1 + t * ey)).min(axis=1))
            if len(self.daireler):
                cx, cy, r = self.daireler[:, 0], self.daireler[:, 1], self.daireler[:, 2]
                d = np.minimum(d, np.abs(np.hypot(x - cx, y - cy) - r).min(axis=1))
            sonuc[bas:bas + adim] = d
        return sonuc

    def dolu_mu(self, px, py):
        """Nokta harita sınırı dışında ya da bir kutu / dairenin içinde mi? (duvar kalınlığı yok)"""
        px = np.asarray(px, dtype=float)
        py = np.asarray(py, dtype=float)
        dolu = (px < 0) | (py < 0) | (px > self.genislik) | (py > self.yukseklik)
        for x0, y0, x1, y1 in self.kutular:
            dolu |= (px >= x0) & (px <= x1) & (py >= y0) & (py <= y1)
        for cx, cy, r in self.daireler:
            dolu |= (px - cx) ** 2 + (py - cy) ** 2 <= r * r
        return dolu

    # ------------------------------------------------------------ ızgaralar

    def hazirla(self, cozunurluk=0.05, serbest_pay=0.20, alan_payi=1.0, erisilebilir=True):
        """Olasılık alanı (uzaklık) ve serbest alan ızgaralarını kur.

        cozunurluk  : hücre kenarı (m)
        serbest_pay : robot merkezinin yüzeylere en az uzaklığı (m); serbest alan = içeride, dolu değil, pay dışı
        alan_payi   : uzaklık ızgarası harita kutusunun dışına bu kadar taşar (ışın uçları dışarı düşebilir)
        erisilebilir: serbest alanı başlangıç noktasından 4-komşulukla erişilebilen bölgeyle sınırla
                      (başlangıç serbest değilse tüm serbest alan kalır)
        """
        anahtar = (cozunurluk, serbest_pay, alan_payi, erisilebilir)
        if self._izgara is not None and self._izgara["anahtar"] == anahtar:
            return self._izgara
        x0, y0 = -alan_payi, -alan_payi
        nx = int(math.ceil((self.genislik + 2 * alan_payi) / cozunurluk))
        ny = int(math.ceil((self.yukseklik + 2 * alan_payi) / cozunurluk))
        xs = x0 + (np.arange(nx) + 0.5) * cozunurluk
        ys = y0 + (np.arange(ny) + 0.5) * cozunurluk
        gx, gy = np.meshgrid(xs, ys, indexing="ij")           # (nx, ny)
        uz = self.geometri_uzakligi(gx, gy).reshape(nx, ny)
        serbest = (~self.dolu_mu(gx, gy)) & (uz >= serbest_pay)
        if erisilebilir:
            serbest = _erisilebilir_bolge(serbest, self.baslangic, x0, y0, cozunurluk)
        self._izgara = dict(anahtar=anahtar, cozunurluk=cozunurluk, x0=x0, y0=y0, nx=nx, ny=ny,
                            uzaklik=uz.astype(np.float32), serbest=serbest,
                            serbest_hucreler=np.flatnonzero(serbest.ravel()))
        if self._izgara["serbest_hucreler"].size == 0:
            raise HaritaHatasi("%s: serbest alan yok (serbest_pay çok büyük?)" % self.ad)
        return self._izgara

    @property
    def izgara(self):
        return self._izgara if self._izgara is not None else self.hazirla()

    def alan_uzakligi(self, px, py, tavan=2.0):
        """Izgaradan (en yakın hücre) yüzeye uzaklık; ızgara dışı = `tavan`."""
        g = self.izgara
        i = np.floor((px - g["x0"]) / g["cozunurluk"]).astype(np.int64)
        j = np.floor((py - g["y0"]) / g["cozunurluk"]).astype(np.int64)
        icinde = (i >= 0) & (i < g["nx"]) & (j >= 0) & (j < g["ny"])
        d = np.full(np.shape(px), tavan, dtype=np.float32)
        d[icinde] = np.minimum(g["uzaklik"][i[icinde], j[icinde]], tavan)
        return d

    def alan_uzakligi_surekli(self, px, py, tavan=2.0):
        """Uzaklık ızgarasının çift doğrusal ara değeri (hücre merkezleri arasında): poza göre sürekli; ızgara dışı = `tavan`."""
        g = self.izgara
        uz = g["uzaklik"]
        fx = (np.asarray(px, dtype=float) - g["x0"]) / g["cozunurluk"] - 0.5
        fy = (np.asarray(py, dtype=float) - g["y0"]) / g["cozunurluk"] - 0.5
        icinde = (fx >= 0) & (fx <= g["nx"] - 1) & (fy >= 0) & (fy <= g["ny"] - 1)
        i = np.clip(np.floor(fx).astype(np.int64), 0, g["nx"] - 2)
        j = np.clip(np.floor(fy).astype(np.int64), 0, g["ny"] - 2)
        tx, ty = np.clip(fx - i, 0.0, 1.0), np.clip(fy - j, 0.0, 1.0)
        d = ((1 - tx) * ((1 - ty) * uz[i, j] + ty * uz[i, j + 1])
             + tx * ((1 - ty) * uz[i + 1, j] + ty * uz[i + 1, j + 1]))
        return np.where(icinde, np.minimum(d, tavan), tavan)

    def alan_log_tablosu(self, sigma, z_isabet, z_rastgele, menzil_maks, tavan):
        """Hücre başına log p(z) = log(z_isabet N(d; 0, sigma) + z_rastgele / menzil_maks) (önbellekli).

        Son öğe ızgara dışı (d = tavan) içindir. Dönüş: (düz tablo float32, dış indeks)."""
        g = self.izgara
        anahtar = (sigma, z_isabet, z_rastgele, menzil_maks, tavan)
        tablolar = g.setdefault("log_tablolar", {})
        if anahtar not in tablolar:
            d = np.minimum(np.append(g["uzaklik"].ravel().astype(float), tavan), tavan)
            norm = z_isabet / (math.sqrt(2 * math.pi) * sigma)
            tablolar[anahtar] = np.log(norm * np.exp(-0.5 * (d / sigma) ** 2) + z_rastgele / menzil_maks).astype(np.float32)
        return tablolar[anahtar]

    def alan_indeksi(self, px, py):
        """Dünya noktalarının düz ızgara indeksi; ızgara dışı = nx * ny (tablonun son öğesi)."""
        g = self.izgara
        ters = 1.0 / g["cozunurluk"]
        i = np.floor((px - g["x0"]) * ters).astype(np.int64)
        j = np.floor((py - g["y0"]) * ters).astype(np.int64)
        icinde = (i >= 0) & (i < g["nx"]) & (j >= 0) & (j < g["ny"])
        return np.where(icinde, i * g["ny"] + j, g["nx"] * g["ny"])

    def serbest_mi(self, px, py):
        g = self.izgara
        i = np.floor((np.asarray(px) - g["x0"]) / g["cozunurluk"]).astype(np.int64)
        j = np.floor((np.asarray(py) - g["y0"]) / g["cozunurluk"]).astype(np.int64)
        icinde = (i >= 0) & (i < g["nx"]) & (j >= 0) & (j < g["ny"])
        s = np.zeros(np.shape(px), dtype=bool)
        s[icinde] = g["serbest"][i[icinde], j[icinde]]
        return s

    def serbest_alan_m2(self):
        g = self.izgara
        return g["serbest_hucreler"].size * g["cozunurluk"] ** 2

    def rastgele_serbest(self, n, rng):
        """Serbest alanda düzgün dağılımlı n poz: (x, y, theta); theta [-pi, pi) düzgün."""
        g = self.izgara
        h = rng.choice(g["serbest_hucreler"], size=n)
        i, j = np.divmod(h, g["ny"])
        x = g["x0"] + (i + rng.random(n)) * g["cozunurluk"]
        y = g["y0"] + (j + rng.random(n)) * g["cozunurluk"]
        th = rng.uniform(-math.pi, math.pi, n)
        return x, y, th

    def serbest_izgara_noktalari(self, adim):
        """Serbest alanda `adim` aralıklı düzenli nokta kafesi (tek tarama sınıflaması için)."""
        g = self.izgara
        xs = np.arange(adim / 2, self.genislik, adim)
        ys = np.arange(adim / 2, self.yukseklik, adim)
        gx, gy = np.meshgrid(xs, ys, indexing="ij")
        gx, gy = gx.ravel(), gy.ravel()
        s = self.serbest_mi(gx, gy)
        return gx[s], gy[s]


def _erisilebilir_bolge(serbest, baslangic, x0, y0, coz):
    i = int((baslangic[0] - x0) / coz)
    j = int((baslangic[1] - y0) / coz)
    nx, ny = serbest.shape
    if not (0 <= i < nx and 0 <= j < ny) or not serbest[i, j]:
        return serbest
    bolge = np.zeros_like(serbest)
    bolge[i, j] = True
    # ardışık genişletme (scipy'siz taşma doldurma); her turda sınır 1 hücre ilerler, 8 adım bir arada
    while True:
        once = bolge.sum()
        for _ in range(8):
            yeni = bolge.copy()
            yeni[1:, :] |= bolge[:-1, :]
            yeni[:-1, :] |= bolge[1:, :]
            yeni[:, 1:] |= bolge[:, :-1]
            yeni[:, :-1] |= bolge[:, 1:]
            bolge = yeni & serbest
        if bolge.sum() == once:
            return bolge


def harita_yukle(kaynak, ad=None):
    """Harita2B | dict (JSON içeriği) | dosya yolu | `kod/araclar/haritalar/` altındaki ad."""
    if isinstance(kaynak, Harita2B):
        return kaynak
    if isinstance(kaynak, dict):
        return Harita2B(kaynak, ad=ad)
    return Harita2B.dosyadan(str(kaynak))


def haritalari_yukle(kaynaklar):
    haritalar = [harita_yukle(k) for k in kaynaklar]
    adlar = [h.ad for h in haritalar]
    if len(set(adlar)) != len(adlar):
        raise HaritaHatasi("harita adları tekil olmalı: %r" % adlar)
    return haritalar


def harita_listesi():
    return sorted(f[:-5] for f in os.listdir(HARITA_KLASORU) if f.endswith(".json"))
