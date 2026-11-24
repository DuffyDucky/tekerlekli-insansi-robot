"""LiDAR özellikleri, tarama sözleşmesi ve 2B sentetik tarama.

Tarama sözleşmesi (sensör ajanıyla ortak): `{"t": s, "acilar": [rad...], "mesafeler": [m...]}`.
Açılar robot GÖVDE çerçevesinde (0 = ileri, saat yönü tersi +); ışının çıkış noktası LiDAR'ın gövdedeki yeri
(`montaj` x_m, y_m). Ölçüm yoksa (menzil dışı, kör sektör, yankı yok) mesafe None / NaN.

VARSAYIM (sözleşmede açık değil): `acilar` montaj yaw'u zaten içerir (gövde çerçevesi dendiği için);
`kor_sektorler_derece` da gövde çerçevesindedir. Sensör çerçevesinde gelirse `LidarOzellik(acilar_cerceve="sensor")`
ile montaj yaw'u eklenir (kör sektörler de o zaman sensör çerçevesinde sayılır).
"""

import json
import math
import os
from dataclasses import dataclass, field

import numpy as np

OZELLIK_DOSYASI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lidar_ozellik.json")


@dataclass
class LidarOzellik:
    menzil_min_m: float = 0.15
    menzil_maks_m: float = 12.0
    acisal_cozunurluk_derece: float = 0.72
    tarama_hz: float = 10.0
    mesafe_gurultu_std_m: float = 0.03      # Gauss std (sentetik taramada; "±3 cm" std olarak okunur)
    montaj_x_m: float = 0.0
    montaj_y_m: float = 0.0
    montaj_yaw: float = 0.0                 # rad
    kor_sektorler_derece: list = field(default_factory=list)   # [[bas, bit], ...] saat yönü tersi, bas -> bit
    acilar_cerceve: str = "govde"           # "govde" | "sensor"
    kaynak: str = "gecici"

    @classmethod
    def gecici(cls, **degisen):
        """`lidar_ozellik.json` yokken testler için makul geçici değerler (12 m, 0,72°, 10 Hz, 3 cm)."""
        return cls(**degisen)

    @classmethod
    def sozlukten(cls, v, kaynak="sozluk"):
        m = v.get("montaj", {}) or {}
        if isinstance(m, (list, tuple)):
            m = {"x_m": m[0], "y_m": m[1], "yaw": m[2] if len(m) > 2 else 0.0}
        yaw = m.get("yaw", m.get("yaw_rad"))
        if yaw is None and "yaw_derece" in m:
            yaw = math.radians(float(m["yaw_derece"]))
        return cls(menzil_min_m=float(v.get("menzil_min_m", 0.15)),
                   menzil_maks_m=float(v.get("menzil_maks_m", 12.0)),
                   acisal_cozunurluk_derece=float(v.get("acisal_cozunurluk_derece", 0.72)),
                   tarama_hz=float(v.get("tarama_hz", 10.0)),
                   mesafe_gurultu_std_m=_gurultu_std(v.get("mesafe_gurultu", 0.03)),
                   montaj_x_m=float(m.get("x_m", m.get("x", 0.0))),
                   montaj_y_m=float(m.get("y_m", m.get("y", 0.0))),
                   montaj_yaw=float(yaw or 0.0),
                   kor_sektorler_derece=[list(map(float, s)) for s in (v.get("kor_sektorler_derece") or [])],
                   acilar_cerceve=str(v.get("acilar_cerceve", "govde")),
                   kaynak=kaynak)

    @classmethod
    def dosyadan(cls, yol=OZELLIK_DOSYASI):
        with open(yol, encoding="utf-8") as f:
            return cls.sozlukten(json.load(f), kaynak=yol)

    @classmethod
    def varsa_dosyadan(cls, yol=OZELLIK_DOSYASI):
        """Dosya varsa ondan, yoksa geçici değerler."""
        return cls.dosyadan(yol) if os.path.exists(yol) else cls.gecici()

    def isin_acilari(self):
        """Tam turu `acisal_cozunurluk_derece` ile bölen gövde açıları (-pi'den başlayarak)."""
        n = int(round(360.0 / self.acisal_cozunurluk_derece))
        return -math.pi + np.arange(n) * (2 * math.pi / n)

    def kor_mu(self, acilar):
        """Açı (tarama çerçevesinde) kör sektörde mi?"""
        acilar = np.asarray(acilar, dtype=float)
        kor = np.zeros(acilar.shape, dtype=bool)
        d = np.degrees(acilar)
        for bas, bit in self.kor_sektorler_derece:
            genis = (bit - bas) % 360.0
            kor |= ((d - bas) % 360.0) <= genis
        return kor


def _gurultu_std(v):
    """`mesafe_gurultu` alanı sayı (std m) ya da sözlük olabilir (biçim henüz kesin değil)."""
    if v is None:
        return 0.03
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, dict):
        for a in ("std_m", "sigma_m", "std", "sigma", "mutlak_std_m", "mutlak_m", "sabit_m", "pm_m"):
            if a in v and isinstance(v[a], (int, float)):
                return float(v[a])
    return 0.03


@dataclass
class HazirTarama:
    """Ön işlenmiş tarama: seçilen ışınlar, gövde açıları, mesafeler (NaN = dönüş yok)."""
    t: float
    acilar: np.ndarray        # (B,) gövde çerçevesi, montaj yaw dahil
    mesafeler: np.ndarray     # (B,) NaN = dönüş yok (menzil dışı / yankı yok)
    montaj: tuple             # (x, y) gövdede
    menzil_maks: float

    @property
    def isabet(self):
        return np.isfinite(self.mesafeler)


def tarama_hazirla(tarama, ozellik, isin_sayisi=None):
    """Sözleşme sözlüğünü diziye çevir; kör sektörü at, menzil dışını NaN yap, eşit aralıklı alt örnekle.

    isin_sayisi: kalan ışınlardan en çok bu kadarı (eşit aralıklı) kullanılır; None = hepsi.
    """
    if isinstance(tarama, HazirTarama):
        return tarama
    acilar = np.asarray(tarama["acilar"], dtype=float)
    m = np.array([np.nan if v is None else v for v in tarama["mesafeler"]], dtype=float)
    if acilar.shape != m.shape:
        raise ValueError("acilar ve mesafeler aynı uzunlukta olmalı")
    tut = ~ozellik.kor_mu(acilar)
    acilar, m = acilar[tut], m[tut]
    m[(m < ozellik.menzil_min_m) | (m > ozellik.menzil_maks_m)] = np.nan
    if ozellik.acilar_cerceve == "sensor":
        acilar = acilar + ozellik.montaj_yaw
    if isin_sayisi and acilar.size > isin_sayisi:
        sec = np.unique(np.linspace(0, acilar.size - 1, isin_sayisi).round().astype(int))
        acilar, m = acilar[sec], m[sec]
    return HazirTarama(t=float(tarama.get("t", 0.0)), acilar=acilar, mesafeler=m,
                       montaj=(ozellik.montaj_x_m, ozellik.montaj_y_m), menzil_maks=ozellik.menzil_maks_m)


def sensor_kokeni(x, y, th, montaj):
    """Gövde pozu(ları)ndan LiDAR'ın dünya konumu."""
    mx, my = montaj
    c, s = np.cos(th), np.sin(th)
    return x + c * mx - s * my, y + s * mx + c * my


def sentetik_tarama(harita, poz, ozellik, rng=None, t=0.0, kayip_orani=0.0, ek_engeller=None):
    """2B ışın izlemeyle sözleşme biçiminde tarama üret (test ve deney karşılaştırması için).

    poz         : (x, y, theta) gövde
    rng         : np.random.Generator (gürültü, kayıp); None = gürültüsüz
    kayip_orani : menzil içindeki ışınların bu oranı rastgele "yankı yok" (None) olur
    ek_engeller : haritada olmayan engeller (insan, açık kapı) [{"tur": "daire", ...}] -> geçici harita ile izlenir
    """
    from .harita2b import Harita2B
    if ek_engeller:
        veri = dict(harita.veri)
        veri["engeller"] = list(veri.get("engeller", [])) + list(ek_engeller)
        harita = Harita2B(veri, ad=harita.ad + "+ek")
    x, y, th = poz
    acilar = ozellik.isin_acilari()
    dunya = th + acilar + (ozellik.montaj_yaw if ozellik.acilar_cerceve == "sensor" else 0.0)
    ox, oy = sensor_kokeni(x, y, th, (ozellik.montaj_x_m, ozellik.montaj_y_m))
    d = harita.isin_izle(np.array([ox]), np.array([oy]), dunya[None, :])[0]
    if rng is not None and ozellik.mesafe_gurultu_std_m > 0:
        d = d + rng.normal(0.0, ozellik.mesafe_gurultu_std_m, d.shape)
    gecersiz = ~np.isfinite(d) | (d < ozellik.menzil_min_m) | (d > ozellik.menzil_maks_m)
    if rng is not None and kayip_orani > 0:
        gecersiz |= rng.random(d.shape) < kayip_orani
    gecersiz |= ozellik.kor_mu(acilar)
    mesafeler = [None if g else float(v) for g, v in zip(gecersiz, d)]
    return {"t": float(t), "acilar": acilar.tolist(), "mesafeler": mesafeler}
