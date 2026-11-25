"""Planlama: 5 cm haritadan 10 cm kaba ızgara, açıklık alanları, numpy dalga cephesi (BFS) ve yol.

Kaba hücre (I, J) = ince (2I..2I+1, 2J..2J+1). Durumlar: engel = herhangi bir ince hücre dolu ya da sanal duvar
(1 hücrelik morfolojik kapamayla: sıyırma açısındaki duvar delikleri kapanır); bilinmeyen = engel değil ve 4 ince
hücrenin en az 3'ü bilinmeyen; geri kalan boş. Yasak = START gerisi.

C-uzayı (geçilebilir) = boş ∧ yasak değil ∧ engele açıklık ≥ r_min ∧ bilinmeyene açıklık ≥ r_bil.
  Bilinmeyen GEÇİLMEZ (gerekçe: LiDAR 12 m görüyor, robot ilerledikçe önü hep bilinir hâle geliyor; bilinmeyenden
  plan, görülmemiş duvara sürmek demek; sınır hedefleri zaten bilinen boşta seçiliyor).
Dalga cephesi: 4 komşulu, eş maliyetli BFS (numpy; cephe başına birkaç dizi işlemi). Uzaklık Manhattan metriğinde.
  4 komşu bilerek: 8 komşuda yol kavşağın iç köşesini 45° kesiyordu; izleyici 60°'den küçük köşeyi yerinde dönmeden
  yayla aldığı ve arka dingili izlediği için gövde duvar ucuna sürtüyordu (5x5'te 6 çarpma). 4 komşuda köşeler kavşak
  ortasında ~90° olur, izleyici dönme merkezini oraya getirip yerinde döner. Eğik koridorda merdiven çıkar, DP
  sadeleştirme (10 cm tolerans) onu düz parçaya çevirir. A* yerine BFS: tek geçiş
  bütün sınırların yol mesafesini verir (WFD, Keidar & Kaminka 2014) ve düz Python heapq'tan ~10x hızlı.
Yol: hedeften başlayarak uzaklığı bir küçük komşulardan açıklığı en büyük olana inilir (koridor ortasına çeker),
  sonra görüş hattı kısaltması: parça boyunca açıklık ≥ min(r_iyi, kısaltılan alt yolun en küçük açıklığı) ise.
"""

import math
from dataclasses import dataclass

import numpy as np

from .izgara import pah_uzakligi

_OFS8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
_OFS4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]


@dataclass
class PlanAyari:
    kaba_kat: int = 2                # 5 cm x 2 = 10 cm
    r_min: float = 0.36              # sert şişirme: yarı genişlik 0,262 + 0,05 (araştırma notu §3) + 0,05 ayrıklaştırma
                                     # (açıklık 10 cm hücre merkezleri arasında ölçülüyor; gerçek duvar ≤ 5 cm yakın)
    r_iyi: float = 0.50              # orta bant: önce yalnız bu açıklıktaki hücrelerde planlanır (köşe noktaları kavşak
                                     # ortasına düşer, izleyicinin yerinde dönüşü sığar); ulaşılamazsa r_min
    r_bil: float = 0.15              # bilinmeyene en az açıklık
    acik_maks_m: float = 1.40        # açıklık alanlarının kırpıldığı en büyük değer (çıkış diski için de)
    kapama: bool = True
    dp_tol_m: float = 0.10           # yol sadeleştirme toleransı


def _kapa(engel):
    """3x3 morfolojik kapama (genişlet + aşındır)."""
    def genislet(b):
        o = b.copy()
        o[1:, :] |= b[:-1, :]
        o[:-1, :] |= b[1:, :]
        o[:, 1:] |= b[:, :-1]
        o[:, :-1] |= b[:, 1:]
        o[1:, 1:] |= b[:-1, :-1]
        o[:-1, :-1] |= b[1:, 1:]
        o[1:, :-1] |= b[:-1, 1:]
        o[:-1, 1:] |= b[1:, :-1]
        return o

    def asindir(b):
        return ~genislet(~b)
    return asindir(genislet(engel)) | engel


class KabaHarita:
    """Bir planlama çevrimi için kaba ızgara + alanlar (bilinen bölgenin sınır kutusuna kırpılır)."""

    def __init__(self, izgara, ayar=None, kutu_pay_m=2.0):
        a = self.ayar = ayar or PlanAyari()
        g = izgara
        k = a.kaba_kat
        bilinen = g.L != 0
        bil_i = np.flatnonzero(bilinen.any(axis=1))
        bil_j = np.flatnonzero(bilinen.any(axis=0))
        if bil_i.size == 0:
            bil_i = np.array([g.nx // 2])
            bil_j = np.array([g.ny // 2])
        pay = int(kutu_pay_m / g.coz)
        i0 = max(0, (bil_i[0] - pay) // k * k)
        j0 = max(0, (bil_j[0] - pay) // k * k)
        i1 = min(g.nx, (bil_i[-1] + pay) // k * k + k)
        j1 = min(g.ny, (bil_j[-1] + pay) // k * k + k)
        ni, nj = (i1 - i0) // k, (j1 - j0) // k
        i1, j1 = i0 + ni * k, j0 + nj * k
        L = g.L[i0:i1, j0:j1]
        dolu = (L > g.esik_dolu) | g.sanal[i0:i1, j0:j1]
        bilm = (L >= g.esik_bos) & (L <= g.esik_dolu) & ~g.sanal[i0:i1, j0:j1]
        yas = g.yasak[i0:i1, j0:j1]
        nanb = g.nan_gecis[i0:i1, j0:j1] > 0

        def havuz(b, fonk):
            return fonk(fonk(b.reshape(ni, k, nj, k), axis=3), axis=1)
        engel = havuz(dolu, np.any)
        if a.kapama:
            engel = _kapa(engel)
        bil_say = bilm.reshape(ni, k, nj, k).sum(axis=(1, 3))
        self.bilinmeyen = (~engel) & (bil_say >= (k * k * 3 + 3) // 4)
        self.yasak = havuz(yas, np.any)
        self.bilinmeyen &= ~self.yasak         # START gerisi bilinmeyen sayılmaz: sınır üretmez
        self.nan = havuz(nanb, np.any)
        self.engel = engel
        self.bos = ~engel & ~self.bilinmeyen
        self.coz = g.coz * k
        self.x0 = g.x0 + i0 * g.coz
        self.y0 = g.y0 + j0 * g.coz
        self.ni, self.nj = ni, nj
        c = self.coz
        self.acik_engel = pah_uzakligi(engel, a.acik_maks_m / c) * np.float32(c)
        # bilinmeyene (ve yasağa) açıklık: kısa menzil yeter; çıkış diski için engel ∪ bilinmeyen uzun menzil
        self.acik_bilinmeyen = pah_uzakligi(self.bilinmeyen | self.yasak, max(a.r_bil, 0.3) / c) * np.float32(c)
        self.gecilir = (self.bos & ~self.yasak & (self.acik_engel >= a.r_min - 1e-6)
                        & (self.acik_bilinmeyen >= a.r_bil - 1e-6))
        self.gecilir_iyi = self.gecilir & (self.acik_engel >= a.r_iyi - 1e-6)
        self._acik_eb = None

    def acik_engel_bilinmeyen(self):
        """Engel ∪ bilinmeyen ∪ yasak'a açıklık (m), acik_maks_m'de kırpılı (çıkış diski)."""
        if self._acik_eb is None:
            self._acik_eb = pah_uzakligi(self.engel | self.bilinmeyen | self.yasak,
                                         self.ayar.acik_maks_m / self.coz) * np.float32(self.coz)
        return self._acik_eb

    # ------------------------------------------------------------ dönüşümler
    def hucre(self, x, y):
        return (np.floor((np.asarray(x) - self.x0) / self.coz).astype(np.int64),
                np.floor((np.asarray(y) - self.y0) / self.coz).astype(np.int64))

    def merkez(self, i, j):
        return self.x0 + (np.asarray(i) + 0.5) * self.coz, self.y0 + (np.asarray(j) + 0.5) * self.coz

    def icinde(self, i, j):
        return (i >= 0) & (i < self.ni) & (j >= 0) & (j < self.nj)

    def acik_oku(self, x, y, alan=None):
        a = self.acik_engel if alan is None else alan
        i, j = self.hucre(x, y)
        ic = self.icinde(i, j)
        out = np.zeros(np.shape(x), dtype=np.float32)
        out[ic] = a[i[ic], j[ic]]
        return out

    # ------------------------------------------------------------ BFS
    def bfs(self, x, y, gevsek_yaricap_m=0.8, gevsek_acik_m=0.18, iyi=False):
        """Robotun bulunduğu yerden dalga cephesi. Robotun hücresi geçilemez bölgedeyse (START önü, dar yer)
        robotun `gevsek_yaricap_m` çevresinde açıklığı ≥ `gevsek_acik_m` olan boş hücreler de geçilir sayılır.
        Dönüş: uzaklık dizisi (int32, -1 = ulaşılmaz), şekil (ni, nj)."""
        ni, nj = self.ni, self.nj
        gec = (self.gecilir_iyi if iyi else self.gecilir).copy()
        i, j = self.hucre(x, y)
        i, j = int(i), int(j)
        if not (0 <= i < ni and 0 <= j < nj):
            return np.full((ni, nj), -1, dtype=np.int32)
        r = int(math.ceil(gevsek_yaricap_m / self.coz))
        a0, a1, b0, b1 = max(0, i - r), min(ni, i + r + 1), max(0, j - r), min(nj, j + r + 1)
        II, JJ = np.meshgrid(np.arange(a0, a1), np.arange(b0, b1), indexing="ij")
        yakin = (II - i) ** 2 + (JJ - j) ** 2 <= r * r
        gev = yakin & ~self.engel[a0:a1, b0:b1] & ~self.yasak[a0:a1, b0:b1] & \
            (self.acik_engel[a0:a1, b0:b1] >= gevsek_acik_m)
        gec[a0:a1, b0:b1] |= gev
        gec[i, j] = True
        # dolgu ile düz dizin
        P = nj + 2
        gp = np.zeros((ni + 2, nj + 2), dtype=bool)
        gp[1:-1, 1:-1] = gec
        gf = gp.ravel()
        dist = np.full(gf.size, -1, dtype=np.int32)
        ofs = np.array([di * P + dj for di, dj in _OFS4], dtype=np.int64)
        bas = (i + 1) * P + (j + 1)
        dist[bas] = 0
        F = np.array([bas], dtype=np.int64)
        k = 0
        while F.size:
            k += 1
            N = (F[:, None] + ofs[None, :]).ravel()
            N = N[gf[N]]
            N = N[dist[N] < 0]
            if N.size == 0:
                break
            N = np.unique(N)
            dist[N] = k
            F = N
        return dist.reshape(ni + 2, nj + 2)[1:-1, 1:-1]

    # ------------------------------------------------------------ yol
    def yol_cikar(self, dist, hedef_ij, r_iyi=None):
        """Hedef hücreden robota inerek hücre yolu, sonra kısaltılmış dünya yolu [(x, y), ...] (robottan hedefe)."""
        r_iyi = self.ayar.r_iyi if r_iyi is None else r_iyi
        i, j = hedef_ij
        if dist[i, j] < 0:
            return None
        hucreler = [(i, j)]
        ac = self.acik_engel
        while dist[i, j] > 0:
            d = dist[i, j]
            en, eni = -1.0, None
            for di, dj in _OFS4:
                a, b = i + di, j + dj
                if 0 <= a < self.ni and 0 <= b < self.nj and dist[a, b] == d - 1:
                    v = float(ac[a, b])
                    if v > en:
                        en, eni = v, (a, b)
            if eni is None:
                break
            i, j = eni
            hucreler.append((i, j))
        hucreler.reverse()
        xs, ys = self.merkez(np.array([h[0] for h in hucreler]), np.array([h[1] for h in hucreler]))
        return self.sadele(list(zip(xs.tolist(), ys.tolist())))

    def sadele(self, noktalar, tol=None):
        """Douglas-Peucker (tolerans `dp_tol_m`): orta eksen yolunun köşeleri kavşak ortasında kalır (izleyici köşede
        dönme merkezini köşeye getirip yerinde döner; süpürme dairesi ancak orada sığar). Sonra her parça geçilebilir
        mi denetlenir; değilse araya ara nokta geri konur."""
        tol = self.ayar.dp_tol_m if tol is None else tol
        if len(noktalar) <= 2:
            return noktalar
        P = np.asarray(noktalar, dtype=float)
        tut = np.zeros(len(P), dtype=bool)
        tut[0] = tut[-1] = True
        yigin = [(0, len(P) - 1)]
        while yigin:
            a, b = yigin.pop()
            if b <= a + 1:
                continue
            ab = P[b] - P[a]
            L = math.hypot(*ab)
            ara = P[a + 1:b] - P[a]
            if L < 1e-9:
                d = np.hypot(ara[:, 0], ara[:, 1])
            else:
                d = np.abs(ab[0] * ara[:, 1] - ab[1] * ara[:, 0]) / L
            k = int(np.argmax(d))
            if d[k] > tol or self.parca_acikligi(P[a], P[b]) < self.ayar.r_min - 0.03:
                m = a + 1 + k
                tut[m] = True
                yigin.append((a, m))
                yigin.append((m, b))
        return [tuple(p) for p in P[tut].tolist()]

    def parca_acikligi(self, p, q):
        """p -> q parçası boyunca engel açıklığının en küçüğü (5 cm örnek)."""
        n = max(2, int(math.hypot(q[0] - p[0], q[1] - p[1]) / (self.coz * 0.5)) + 1)
        t = np.linspace(0.0, 1.0, n)
        xs = p[0] + (q[0] - p[0]) * t
        ys = p[1] + (q[1] - p[1]) * t
        i, j = self.hucre(xs, ys)
        ic = self.icinde(i, j)
        if not ic.all():
            return 0.0
        if (self.yasak[i, j] | ~(self.bos[i, j] | self.gecilir[i, j])).any():
            return 0.0
        return float(self.acik_engel[i, j].min())

    def kisalt(self, noktalar, acik, r_iyi):
        if len(noktalar) <= 2:
            return noktalar
        out = [noktalar[0]]
        i = 0
        n = len(noktalar)
        while i < n - 1:
            en_iyi = i + 1
            alt_min = float(acik[i + 1]) if i + 1 < n else 0.0
            j = i + 2
            while j < n:
                alt_min = min(alt_min, float(acik[j - 1]))
                esik = min(r_iyi, alt_min) - 1e-3
                if self.parca_acikligi(noktalar[i], noktalar[j]) >= esik:
                    en_iyi = j
                    j += 1
                else:
                    break
            out.append(noktalar[en_iyi])
            i = en_iyi
        return out


def iki_katmanli_bfs(kh, x, y, ceza_m=1.5):
    """Orta bant (r_iyi) ve sert sınır (r_min) BFS'i. -> (birleşik uzaklık (m, -1 ulaşılmaz), dist_iyi, dist_min).
    Yalnız sert sınırla ulaşılan hücrelere `ceza_m` eklenir (dar geçit tercih edilmesin)."""
    d_iyi = kh.bfs(x, y, iyi=True)
    d_min = kh.bfs(x, y, iyi=False)
    m = np.where(d_iyi >= 0, d_iyi * kh.coz, np.where(d_min >= 0, d_min * kh.coz + ceza_m, -1.0))
    return m, d_iyi, d_min


def yol_cikar2(kh, d_iyi, d_min, hedef_ij):
    if d_iyi[hedef_ij] >= 0:
        return kh.yol_cikar(d_iyi, hedef_ij)
    if d_min[hedef_ij] >= 0:
        return kh.yol_cikar(d_min, hedef_ij)
    return None


def yol_uzunlugu(yol):
    if not yol or len(yol) < 2:
        return 0.0
    a = np.asarray(yol)
    return float(np.hypot(*(a[1:] - a[:-1]).T).sum())
