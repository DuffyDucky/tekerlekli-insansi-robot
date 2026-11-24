"""Tarama olasılık modeli (karışım). İki seçenek, ikisi de log-olasılık döndürür.

"alan" (olasılık alanı, likelihood field; varsayılan): dönüşü olan her ışının ucu dünyaya konur, ızgaradan en yakın
yüzeye uzaklığı d okunur:
    p(z) = z_isabet * N(d; 0, sigma_isabet) + z_rastgele / menzil_maks
  N tek boyutlu Gauss yoğunluğu. z_rastgele terimi haritada olmayan engeli (insan, açık kapı, masa ayağı), çoklu
  yansımayı ve ızgara dışına düşen uçları karşılar: bir ışın ne kadar kötü olursa olsun olasılık bu tabanın altına
  inmez. Dönüşü olmayan ışınlar (None) `bos_isin_sayisi` > 0 ise ışın izlemeyle değerlendirilir (aşağıda).

"isin" (ışın modeli, beam model): her ışın için beklenen uzaklık r* ışın izlemeyle bulunur:
    p(z) = z_isabet * N(z; r*, sigma_isabet) * [r* < maks]
         + z_kisa * lambda * exp(-lambda z) / (1 - exp(-lambda r*)) * [z < r*]     (beklenmeyen yakın engel)
         + z_rastgele / menzil_maks
  Daha doğru (duvarın arkasını görmez) ama yavaş ve pozda daha sivri.

Dönüş yok (None) ışını, iki modelde aynı:
    p(None) = kayip + (1 - kayip) * [r* >= menzil_maks - sigma]
  "kayip": menzil içinde yüzey varken yankının gelmeme olasılığı (koyu / parlak yüzey, eğik geliş).

Işınlar bağımsız değildir (komşu ışınlar aynı duvarı görür, harita hatası hepsini birlikte etkiler). Aşırı güveni
azaltmak için toplam log-olasılık `us` (0 < us <= 1) ile çarpılır (tavlama) ve ışınlar `isin_sayisi`na seyreltilir.
"""

import math
from dataclasses import dataclass

import numpy as np

from .tarama import sensor_kokeni


@dataclass
class OlcumParametreleri:
    model: str = "alan"            # "alan" | "isin"
    sigma_isabet: float = 0.15     # m; sensör gürültüsü (±3 cm) + harita / poz hatası + ızgara (0,05 m)
    z_isabet: float = 0.80
    z_rastgele: float = 0.20       # beklenmeyen engel / yansıma tabanı (alan modelinde z_kisa da buraya düşer)
    z_kisa: float = 0.10           # yalnız "isin": beklenmeyen yakın engel ağırlığı
    lambda_kisa: float = 0.5       # 1/m; yalnız "isin"
    kayip: float = 0.05            # menzil içinde yüzey varken dönüş gelmeme olasılığı
    isin_sayisi: int = 60          # taramadan kullanılan ışın sayısı (eşit aralıklı)
    bos_isin_sayisi: int = 12      # "alan": ışın izlemeyle değerlendirilecek en çok None ışını (0 = yok say)
    us: float = 0.3                # log-olasılık çarpanı (ışın bağımlılığına karşı tavlama); 0,5 / sigma 0,10 ile
                                   #   koridor_1'de (düzenli kapılar) 121 adımın 15'inde poz kendinden emin yanlıştı
    alan_tavan: float = 2.0        # m; ızgara dışı / uzak uçlar bu uzaklıkta sayılır


def log_olasilik(harita, x, y, th, hazir, p, surekli=False):
    """Parçacıkların (x, y, th dizileri; tek harita) taramaya log-olasılığı (tavlanmış), (P,).

    surekli=True ("alan" modeli): uç noktaların yüzeye uzaklığı en yakın hücreden değil, uzaklık ızgarasının çift
    doğrusal ara değerinden (Harita2B.alan_uzakligi_surekli) gelir. (Analitik geometri de denendi: aynı sonuç,
    6 koridorda adım 18 -> 51 ms.) Tablo hücre başına sabit olduğundan poza göre basamaklıdır; harita kanıtının
    en iyi uyum araması (mcl._en_iyi_uyum) bu basamakta farklı plato yakalayıp her adım ±0,03 nat gürültü üretiyordu.
    Yalnız az sayıda poz için (desen araması) kullanılır; parçacık ağırlıkları tablodan hesaplanmaya devam eder."""
    ox, oy = sensor_kokeni(x, y, th, hazir.montaj)
    isabet = hazir.isabet
    zmax = hazir.menzil_maks
    toplam = np.zeros(np.shape(x))
    taban = p.z_rastgele / zmax
    norm = p.z_isabet / (math.sqrt(2 * math.pi) * p.sigma_isabet)
    if p.model == "alan":
        if isabet.any():
            # uç = köken + z (cos(th + a), sin(th + a)); açı toplamı yerine dönme: cos/sin yalnız P + B kez
            aa = hazir.acilar[isabet]
            z = hazir.mesafeler[isabet]
            bx, by = z * np.cos(aa), z * np.sin(aa)                 # (B,) gövde çerçevesinde uç
            c, s = np.cos(th)[:, None], np.sin(th)[:, None]
            ux = ox[:, None] + c * bx[None, :] - s * by[None, :]
            uy = oy[:, None] + s * bx[None, :] + c * by[None, :]
            if surekli:
                d = harita.alan_uzakligi_surekli(ux, uy, p.alan_tavan)
                toplam += np.log(norm * np.exp(-0.5 * (d / p.sigma_isabet) ** 2) + taban).sum(axis=1)
            else:
                tablo = harita.alan_log_tablosu(p.sigma_isabet, p.z_isabet, p.z_rastgele, zmax, p.alan_tavan)
                toplam += tablo[harita.alan_indeksi(ux, uy)].sum(axis=1, dtype=np.float64)
        bos = np.flatnonzero(~isabet)
        if p.bos_isin_sayisi and bos.size:
            if bos.size > p.bos_isin_sayisi:
                bos = bos[np.linspace(0, bos.size - 1, p.bos_isin_sayisi).round().astype(int)]
            toplam += _bos_log(harita, ox, oy, th, hazir.acilar[bos], zmax, p)
    elif p.model == "isin":
        a = th[:, None] + hazir.acilar[None, :]
        rs = harita.isin_izle(ox, oy, a)                       # (P, B) beklenen
        z = hazir.mesafeler[None, :]
        menzilde = rs < zmax
        with np.errstate(invalid="ignore", over="ignore"):
            hit = np.where(menzilde, norm * np.exp(-0.5 * ((z - rs) / p.sigma_isabet) ** 2), 0.0)
            rs_k = np.minimum(rs, zmax)
            kisa = np.where(z < rs_k, p.z_kisa * p.lambda_kisa * np.exp(-p.lambda_kisa * z)
                            / (1 - np.exp(-p.lambda_kisa * rs_k)), 0.0)
        pz = hit + kisa + taban
        pbos = p.kayip + (1 - p.kayip) * (rs >= zmax - p.sigma_isabet)
        pz = np.where(isabet[None, :], pz, pbos)
        toplam += np.log(np.nan_to_num(pz, nan=taban)).sum(axis=1)
    else:
        raise ValueError("bilinmeyen ölçüm modeli: %r" % p.model)
    return p.us * toplam


def _bos_log(harita, ox, oy, th, acilar, zmax, p):
    a = th[:, None] + acilar[None, :]
    rs = harita.isin_izle(ox, oy, a)
    pbos = p.kayip + (1 - p.kayip) * (rs >= zmax - p.sigma_isabet)
    return np.log(pbos).sum(axis=1)
