"""Sınır (frontier) bulma, kümeleme, hedef seçimi ve çıkış (dışarı) tanıma. Kaba ızgara (planla.KabaHarita) üzerinde.

Sınır hücresi: boş, yasak değil, 4 komşusundan biri bilinmeyen. Kümeler 8 komşulukla. Elenenler:
- kısa küme (< `min_genislik_m`, robot genişliği; sıyırma açısındaki duvar delikleri, dar aralıklar),
- ulaşılamayan küme (`bakis_m` içinde geçilebilir ve robottan ulaşılabilir hücre yok),
- START gerisi (yasak bölge zaten sınır üretmez; ayrıca robotun ulaşabileceği yerden bakılamaz).
Çıkmaz: ucu duvar olarak görülen kolda boş-bilinmeyen sınırı kalmaz, hedef olmaz: robot girmez.

Maliyet (m biriminde; araştırma notu §1):
    J(f) = d_yol(f) + w_don * |Δθ| - w_dis * dis(f) - w_uzak * min(1, d_START(f) / 10 m)
  d_yol: BFS uzaklığı (bakış noktasına), Δθ: robot yönü ile bakış noktasına yön farkı, dis(f): küme hücrelerinin
  dönüşsüz ışın geçen oranı (FINISH ağzının gerisi dönüşsüz ışın verir), d_START: başlangıca kuş uçuşu uzaklık.
Histerezis: mevcut hedef ancak kaybolursa / ulaşılamaz olursa ya da yeni aday hem %30 hem 2 m daha ucuzsa değişir.

Çıkış (dışarı) tanıma: yarıçapı `dis_yaricap_m` olan, bütünüyle BİLİNEN BOŞ bir disk (engel, bilinmeyen ve yasaktan
uzaklık ≥ r). Hücre ≤ 1,5 m olan bir ızgara labirentinde böyle disk sığmaz (dört koridorun kesiştiği yerde bile
iç köşelere uzaklık ≤ 1,06 m); FINISH ağzından görülen dış alanda sığar. Bu bir VARSAYIMdır: "dışarısı koridor
genişliğinden belirgin geniştir" (kural: FINISH dış sınırda bir açıklık).
"""

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class SinirAyari:
    min_genislik_m: float = 0.50
    bakis_m: float = 1.00
    w_yakin: float = 3.0             # bakış noktasının sınıra uzaklığı cezası (m / m): sınırın önüne kadar git
    w_don: float = 0.30
    w_dis: float = 3.0
    w_uzak: float = 0.5
    w_acik: float = 5.0              # bakış noktası seçiminde düşük açıklık cezası (m / m): yerinde dönüş sığsın
    acik_iyi_m: float = 0.55
    hister_oran: float = 0.30
    hister_m: float = 2.0
    ayni_hedef_m: float = 1.0
    dis_yaricap_m: float = 1.25


@dataclass
class Sinir:
    hucreler: np.ndarray       # (n, 2) kaba (i, j)
    merkez: tuple              # dünya (x, y)
    boy_m: float
    dis: float
    bakis: tuple               # (i, j) bakış hücresi
    bakis_xy: tuple
    d_yol_m: float
    maliyet: float = 0.0


def sinir_hucreleri(kh):
    b = kh.bilinmeyen
    kom = np.zeros_like(b)
    kom[1:, :] |= b[:-1, :]
    kom[:-1, :] |= b[1:, :]
    kom[:, 1:] |= b[:, :-1]
    kom[:, :-1] |= b[:, 1:]
    return kh.bos & ~kh.yasak & kom


def kumele(maske):
    """8 komşulu bağlı bileşenler (düz Python BFS; sınır hücresi sayısı küçük). -> [np.ndarray (n, 2)]"""
    ii, jj = np.nonzero(maske)
    kalan = set(zip(ii.tolist(), jj.tolist()))
    kumeler = []
    while kalan:
        bas = kalan.pop()
        yigin = [bas]
        uye = [bas]
        while yigin:
            i, j = yigin.pop()
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    n = (i + di, j + dj)
                    if n in kalan:
                        kalan.remove(n)
                        yigin.append(n)
                        uye.append(n)
        kumeler.append(np.array(uye, dtype=np.int64))
    return kumeler


def sinirlari_bul(kh, dist, robot_poz, ayar=None, baslangic=(0.0, 0.0)):
    a = ayar or SinirAyari()
    maske = sinir_hucreleri(kh)
    kumeler = kumele(maske)
    ulas = dist >= 0
    r = int(math.ceil(a.bakis_m / kh.coz))
    sonuc = []
    for k in kumeler:
        boy = _kume_boyu(k, kh.coz)
        if boy < a.min_genislik_m:
            continue
        i0, j0 = k.min(axis=0) - r
        i1, j1 = k.max(axis=0) + r + 1
        i0, j0 = max(i0, 0), max(j0, 0)
        i1, j1 = min(i1, kh.ni), min(j1, kh.nj)
        alt = ulas[i0:i1, j0:j1]
        ci, cj = np.nonzero(alt)
        if ci.size == 0:
            continue
        ci, cj = ci + i0, cj + j0
        # adayların kümeye en yakın uzaklığı (hücre)
        if k.shape[0] > 60:
            kk = k[np.linspace(0, k.shape[0] - 1, 60).astype(int)]
        else:
            kk = k
        D2 = (ci[:, None] - kk[None, :, 0]) ** 2 + (cj[:, None] - kk[None, :, 1]) ** 2
        en_k = D2.argmin(axis=1)
        d2 = D2[np.arange(ci.size), en_k]
        yakin = d2 <= r * r
        if not yakin.any():
            continue
        ci, cj, d2, en_k = ci[yakin], cj[yakin], d2[yakin], en_k[yakin]
        # görüş hattı: adaydan en yakın sınır hücresine engel yok (duvarın öbür yanından bakılmaz)
        gor = _gorus(kh.engel, ci, cj, kk[en_k, 0], kk[en_k, 1])
        if not gor.any():
            continue
        ci, cj, d2 = ci[gor], cj[gor], d2[gor]
        dd = (dist[ci, cj] + a.w_yakin * np.sqrt(d2) * kh.coz
              + a.w_acik * np.maximum(0.0, a.acik_iyi_m - kh.acik_engel[ci, cj]))
        en = int(np.argmin(dd))
        bi, bj = int(ci[en]), int(cj[en])
        bx, by = kh.merkez(bi, bj)
        mx, my = kh.merkez(k[:, 0], k[:, 1])
        dis = float(kh.nan[k[:, 0], k[:, 1]].mean())
        sonuc.append(Sinir(hucreler=k, merkez=(float(mx.mean()), float(my.mean())), boy_m=boy, dis=dis,
                           bakis=(bi, bj), bakis_xy=(float(bx), float(by)), d_yol_m=float(dist[bi, bj])))
    for s in sonuc:
        s.maliyet = maliyet(s, robot_poz, a, baslangic) + a.w_acik * max(0.0, a.acik_iyi_m - float(kh.acik_engel[s.bakis]))
    return sonuc


def _gorus(engel, ai, aj, bi, bj, n=12):
    t = np.linspace(0.0, 1.0, n)[None, :]
    pi = np.rint(ai[:, None] + (bi - ai)[:, None] * t).astype(np.int64)
    pj = np.rint(aj[:, None] + (bj - aj)[:, None] * t).astype(np.int64)
    return ~engel[pi, pj].any(axis=1)


def _kume_boyu(k, coz):
    """Kümenin uzunluğu: sınır kutusunun köşegeni ile hücre sayısının küçüğü (dağınık kümeyi şişirmesin)."""
    if k.shape[0] == 1:
        return coz
    kosegen = math.hypot(*(k.max(axis=0) - k.min(axis=0) + 1)) * coz
    return min(kosegen, k.shape[0] * coz)


def maliyet(s, robot_poz, a, baslangic=(0.0, 0.0)):
    x, y, th = robot_poz
    yon = math.atan2(s.bakis_xy[1] - y, s.bakis_xy[0] - x) if math.hypot(s.bakis_xy[0] - x, s.bakis_xy[1] - y) > 0.3 \
        else math.atan2(s.merkez[1] - y, s.merkez[0] - x)
    dth = abs((yon - th + math.pi) % (2 * math.pi) - math.pi)
    d_start = math.hypot(s.merkez[0] - baslangic[0], s.merkez[1] - baslangic[1])
    return s.d_yol_m + a.w_don * dth - a.w_dis * s.dis - a.w_uzak * min(1.0, d_start / 10.0)


def hedef_sec(sinirlar, onceki, ayar=None):
    """Histerezisli seçim. onceki: önceki seçilen Sinir ya da None. -> (Sinir | None, degisti: bool)"""
    a = ayar or SinirAyari()
    if not sinirlar:
        return None, onceki is not None
    en = min(sinirlar, key=lambda s: s.maliyet)
    if onceki is None:
        return en, True
    # önceki hedefin hâlâ var olan karşılığı (merkezi ya da bakışı yakın küme)
    es = None
    for s in sinirlar:
        if (math.hypot(s.merkez[0] - onceki.merkez[0], s.merkez[1] - onceki.merkez[1]) < a.ayni_hedef_m
                or math.hypot(s.bakis_xy[0] - onceki.bakis_xy[0], s.bakis_xy[1] - onceki.bakis_xy[1]) < 0.5):
            if es is None or s.maliyet < es.maliyet:
                es = s
    if es is None:
        return en, True
    if en is es:
        return es, False
    if en.maliyet < es.maliyet - a.hister_m and en.maliyet < es.maliyet * (1 - a.hister_oran) if es.maliyet > 0 \
            else en.maliyet < es.maliyet - a.hister_m:
        return en, True
    return es, False


def cikis_bul(kh, dist, ayar=None):
    """Dış alan disk merkezleri; ulaşılabilir olanlardan BFS'te en yakını. -> ((i, j), (x, y)) | None, aday sayısı"""
    a = ayar or SinirAyari()
    if a.dis_yaricap_m <= 0:
        return None, 0
    ac = kh.acik_engel_bilinmeyen()
    aday = (ac >= a.dis_yaricap_m - 1e-6) & kh.bos & ~kh.yasak
    n = int(aday.sum())
    if n == 0:
        return None, 0
    ul = aday & (dist >= 0)
    if not ul.any():
        # aday var ama BFS'le doğrudan ulaşılamıyor (dar ağız C-uzayında ama disk hücresi pay dışı olabilir):
        # adaylara en yakın ulaşılabilir hücre
        ai, aj = np.nonzero(aday)
        ri, rj = np.nonzero(dist >= 0)
        if ri.size == 0:
            return None, n
        sec = np.linspace(0, ai.size - 1, min(ai.size, 50)).astype(int)
        d2 = (ri[:, None] - ai[None, sec]) ** 2 + (rj[:, None] - aj[None, sec]) ** 2
        en = int(np.argmin(d2.min(axis=1)))
        if d2.min(axis=1)[en] * kh.coz ** 2 > 1.5 ** 2:
            return None, n
        i, j = int(ri[en]), int(rj[en])
    else:
        ii, jj = np.nonzero(ul)
        en = int(np.argmin(dist[ii, jj]))  # m
        i, j = int(ii[en]), int(jj[en])
    x, y = kh.merkez(i, j)
    return ((i, j), (float(x), float(y))), n
