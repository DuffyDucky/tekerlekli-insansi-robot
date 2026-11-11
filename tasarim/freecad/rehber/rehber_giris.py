# 3B montaj rehberi: alt montaj giriş yolu (F10c düzeltme turu 1). FreeCAD istemez; parça mesh'leri (rehber_sira.Denetim.P) üstünde
# çalışır, yalnız numpy.
#
# Soru: bir parça kümesi (hareketli: ör. E3'te kafa, E4'te masada hazırlanan kabuk grubu) o ana kadar takılmış parçaların (engel)
# arasından düz bir yönde yerine girebiliyor mu? Ters yönden bakılır: hareketli küme son yerinden d yönünde adım adım çekilir; iki
# kümenin sınır kutuları ayrılana kadar hiçbir adımda ortak hacim yoksa o yön "serbest".
#
# Ortak hacim (yöntem): her parça için üç eksende düzenli ışın ızgarası (aralık h mm, ızgara yarım olmayan bir kaydırmayla, yüzeyle
# aynı düzleme düşmesin). Kapalı mesh'te ışının giriş / çıkış noktaları (parite) parçanın içinde kalan aralıkları verir. Hareketli
# kümenin aralıkları d'nin tam sayı katı kadar (ızgara satırı / ışın boyu) kaydırılır, aynı ışındaki engel aralıklarıyla kesişimi
# ölçülür. Kesişim boyu > ESIK mm olan ışın "çarpışma" sayılır. Temas eden yüzler (ortak düzlem, sıfır boşluklu geçme) ve ESIK'ten
# sığ dokunmalar çarpışma değildir. Bir ortak hacim, üç eksenden en az birinde ESIK'ten uzun ve öbür iki eksende h'den geniş olmalı.
# Kör noktalar: tek ışında tek sayıda kesişim (açık mesh, köşeden geçen ışın) o ışını o parça için düşürür (sayısı raporda);
# adım h (çekme yolu h aralıklı örneklenir; h'den ince bir engel atlanabilir); sürtünme, baskı toleransı, esneme yok.
import math, time
import numpy as np

ESIK = 0.2          # mm: bundan kısa ortak hacim (temas, yüzey yuvarlama) çarpışma sayılmaz
KAYDIR = 0.3713     # ızgara kaydırması (h'nin kesri): ışın yüzeyle aynı düzlemde kalmasın
YONLER6 = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]


class Isinlar:
    """Parça başına, eksen başına içerde kalan ışın aralıkları (i, j, t0, t1); tembel, önbellekli."""

    def __init__(self, P, h, lo, hi):
        self.P, self.h = P, float(h)
        self.lo = np.asarray(lo, float) - 2 * h
        self.n = (np.ceil((np.asarray(hi, float) + 2 * h - self.lo) / h).astype(np.int64) + 1)
        self.cache = {}
        self.tek = 0                                                    # tek sayıda kesişimli (düşürülen) ışın

    def ara(self, k, eks, ofs=None):
        """ofs (mm, 3): parça bu kadar kaydırılmış olarak ışınlanır (önbelleğe girmez; F10d düzeltme 1, gerçek yönde süpürme)."""
        key = (k, eks)
        if ofs is None and key in self.cache:
            return self.cache[key]
        a1, a2 = [a for a in range(3) if a != eks]
        p = self.P[k]
        T = p["v"][p["f"]]
        if ofs is not None:
            T = T + np.asarray(ofs, float)
        h, lo = self.h, self.lo
        X = (T[:, :, a1] - lo[a1]) / h - KAYDIR                        # ışın (i, j): lo + (i + KAYDIR) h
        Y = (T[:, :, a2] - lo[a2]) / h - KAYDIR
        Z = T[:, :, eks]
        d = (Y[:, 1] - Y[:, 2]) * (X[:, 0] - X[:, 2]) + (X[:, 2] - X[:, 1]) * (Y[:, 0] - Y[:, 2])
        ok = np.abs(d) > 1e-12
        X, Y, Z, d = X[ok], Y[ok], Z[ok], d[ok]
        i0 = np.ceil(X.min(1)).astype(np.int64); i1 = np.floor(X.max(1)).astype(np.int64)
        j0 = np.ceil(Y.min(1)).astype(np.int64); j1 = np.floor(Y.max(1)).astype(np.int64)
        ni = np.maximum(i1 - i0 + 1, 0); nj = np.maximum(j1 - j0 + 1, 0)
        cnt = ni * nj
        I, J, Tt = [], [], []
        bas = 0
        cs = np.cumsum(cnt)
        while bas < len(cnt):                                           # parçalı genişletme (bellek)
            son = int(np.searchsorted(cs, (cs[bas - 1] if bas else 0) + 3_000_000, "right"))
            son = max(son, bas + 1)
            sl = slice(bas, son)
            c = cnt[sl]
            tot = int(c.sum())
            if tot:
                tri = np.repeat(np.arange(bas, son), c)
                off = np.arange(tot) - np.repeat(np.cumsum(c) - c, c)
                nj_ = nj[tri]
                ii = i0[tri] + off // np.maximum(nj_, 1); jj = j0[tri] + off % np.maximum(nj_, 1)
                x0, x1, x2 = X[tri, 0], X[tri, 1], X[tri, 2]
                y0, y1, y2 = Y[tri, 0], Y[tri, 1], Y[tri, 2]
                dd = d[tri]
                l0 = ((y1 - y2) * (ii - x2) + (x2 - x1) * (jj - y2)) / dd
                l1 = ((y2 - y0) * (ii - x2) + (x0 - x2) * (jj - y2)) / dd
                l2 = 1.0 - l0 - l1
                m = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
                tt = l0 * Z[tri, 0] + l1 * Z[tri, 1] + l2 * Z[tri, 2]
                I.append(ii[m]); J.append(jj[m]); Tt.append(tt[m])
            bas = son
        if I:
            I = np.concatenate(I); J = np.concatenate(J); Tt = np.concatenate(Tt)
        else:
            I = J = np.zeros(0, np.int64); Tt = np.zeros(0)
        rid = I * self.n[a2] + J
        o = np.lexsort((Tt, rid))
        rid, I, J, Tt = rid[o], I[o], J[o], Tt[o]
        if len(rid):
            yeni = np.r_[True, rid[1:] != rid[:-1]]
            gi = np.cumsum(yeni) - 1
            say = np.bincount(gi)
            cift = (say % 2 == 0)[gi]
            self.tek += int((say % 2 == 1).sum())
            rid, I, J, Tt = rid[cift], I[cift], J[cift], Tt[cift]
        r = (I[0::2], J[0::2], Tt[0::2], Tt[1::2])
        if ofs is None:
            self.cache[key] = r
        return r


def _kutu(P, ks):
    return np.min([P[k]["bmin"] for k in ks], 0), np.max([P[k]["bmax"] for k in ks], 0)


def _kesisir(alo, ahi, blo, bhi, pay=0.0):
    return bool(np.all(ahi >= blo - pay) and np.all(alo <= bhi + pay))


class Giris:
    def __init__(self, P, h=0.25, esik=ESIK):
        self.P, self.h, self.esik = P, float(h), float(esik)
        lo = np.min([p["bmin"] for p in P], 0); hi = np.max([p["bmax"] for p in P], 0)
        self.I = Isinlar(P, h, lo, hi)

    def carpisma(self, H, E, kay, eksler=(0, 1, 2)):
        """H (hareketli indeksler) kay (tam sayı ızgara adımı, 3) kadar kaydırılmışken E ile ortak hacim: {(h, e): (en uzun mm, ışın)}."""
        out = {}
        h = self.h
        for eks in eksler:
            a1, a2 = [a for a in range(3) if a != eks]
            n2 = self.I.n[a2]
            OE = [self.I.ara(e, eks) for e in E]
            if not OE:
                continue
            ek = np.concatenate([np.full(len(x[0]), e) for e, x in zip(E, OE)])
            ei = np.concatenate([x[0] for x in OE]); ej = np.concatenate([x[1] for x in OE])
            e0 = np.concatenate([x[2] for x in OE]); e1 = np.concatenate([x[3] for x in OE])
            key = ei * n2 + ej
            o = np.argsort(key, kind="stable")
            key, ek, e0, e1 = key[o], ek[o], e0[o], e1[o]
            for hk in H:
                hi_, hj, h0, h1 = self.I.ara(hk, eks)
                if not len(hi_):
                    continue
                ii = hi_ + kay[a1]; jj = hj + kay[a2]
                dt = kay[eks] * h
                q = ii * n2 + jj
                L = np.searchsorted(key, q, "left"); R = np.searchsorted(key, q, "right")
                c = R - L
                if not c.any():
                    continue
                src = np.repeat(np.arange(len(q)), c)
                off = np.arange(int(c.sum())) - np.repeat(np.cumsum(c) - c, c)
                tgt = np.repeat(L, c) + off
                ov = np.minimum(h1[src] + dt, e1[tgt]) - np.maximum(h0[src] + dt, e0[tgt])
                m = ov > self.esik
                if m.any():
                    for e in np.unique(ek[tgt[m]]):
                        mm = m & (ek[tgt] == e)
                        x = out.get((int(hk), int(e)), (0.0, 0))
                        out[(int(hk), int(e))] = (max(x[0], float(ov[mm].max())), x[1] + int(mm.sum()))
        return out

    def yon(self, H, E, d, azami_mm=600.0):
        """d (tam sayı yön, ör. (0, 1, 0)) boyunca çekme. Döner: dict(serbest, yol_mm, carpan, dinlenme)."""
        d = np.asarray(d, np.int64)
        adim_mm = self.h * float(np.linalg.norm(d))
        hlo, hhi = _kutu(self.P, H)
        D = d * self.h
        # engel ön seçimi: hareketli kutunun d boyunca süpürdüğü koridor
        n_max = int(azami_mm / adim_mm) + 1
        clo = np.minimum(hlo, hlo + D * n_max); chi = np.maximum(hhi, hhi + D * n_max)
        E = [e for e in E if _kesisir(self.P[e]["bmin"], self.P[e]["bmax"], clo, chi, 1.0)]
        dinlenme = self.carpisma(H, E, np.zeros(3, np.int64))
        if not E:
            return dict(serbest=True, yol_mm=0.0, carpan=[], dinlenme=[], engel_say=0)
        elo, ehi = _kutu(self.P, E)
        # hareketli parçalardan engel kutusuna hiç girmeyecek olanlar (yön boyunca) ölçülmez
        H2 = [k for k in H if _kesisir(np.minimum(self.P[k]["bmin"], self.P[k]["bmin"] + D * n_max),
                                       np.maximum(self.P[k]["bmax"], self.P[k]["bmax"] + D * n_max), elo, ehi, 1.0)]
        for n in range(1, n_max + 1):
            kay = d * n
            if not _kesisir(hlo + kay * self.h, hhi + kay * self.h, elo, ehi, 0.5):
                return dict(serbest=True, yol_mm=round(n * adim_mm, 2), carpan=[], dinlenme=self._liste(dinlenme), engel_say=len(E))
            c = self.carpisma(H2, E, kay)
            c = {k: v for k, v in c.items() if k not in dinlenme}           # dinlenmede zaten ortak olanlar ayrı raporlanır
            if c:
                return dict(serbest=False, yol_mm=round((n - 1) * adim_mm, 2), carpan=self._liste(c), dinlenme=self._liste(dinlenme),
                            engel_say=len(E))
        return dict(serbest=False, yol_mm=round(n_max * adim_mm, 2), carpan=[], dinlenme=self._liste(dinlenme), engel_say=len(E),
                    neden="azami yol")

    # ------------------------------------------------ F10d düzeltme 1 (kontrol B-5): gerçek yönde süpürme
    def _engel(self, E, eks):
        a2 = [a for a in range(3) if a != eks][1]
        n2 = self.I.n[a2]
        OE = [self.I.ara(e, eks) for e in E]
        ek = np.concatenate([np.full(len(x[0]), e) for e, x in zip(E, OE)])
        ei = np.concatenate([x[0] for x in OE]); ej = np.concatenate([x[1] for x in OE])
        e0 = np.concatenate([x[2] for x in OE]); e1 = np.concatenate([x[3] for x in OE])
        key = ei * n2 + ej
        o = np.argsort(key, kind="stable")
        return key[o], ek[o], e0[o], e1[o], n2

    def carpisma_ofs(self, H, EE, ofs):
        """H, ofs (mm) kadar kaydırılmış (ızgaraya yuvarlanmadan: parça kaydırılıp yeniden ışınlanır) iken engellerle ortak hacim.
        EE: eksen -> _engel(). Döner {(h, e): (en uzun mm, ışın)} (carpisma ile aynı)."""
        out = {}
        for eks, (key, ek, e0, e1, n2) in EE.items():
            for hk in H:
                hi_, hj, h0, h1 = self.I.ara(hk, eks, ofs)
                n1 = self.I.n[[a for a in range(3) if a != eks][0]]
                ok = (hi_ >= 0) & (hi_ < n1) & (hj >= 0) & (hj < n2)      # ızgara dışı ışın başka satırla karışmasın
                hi_, hj, h0, h1 = hi_[ok], hj[ok], h0[ok], h1[ok]
                if not len(hi_):
                    continue
                q = hi_ * n2 + hj
                L = np.searchsorted(key, q, "left"); R = np.searchsorted(key, q, "right")
                c = R - L
                if not c.any():
                    continue
                src = np.repeat(np.arange(len(q)), c)
                off = np.arange(int(c.sum())) - np.repeat(np.cumsum(c) - c, c)
                tgt = np.repeat(L, c) + off
                ov = np.minimum(h1[src], e1[tgt]) - np.maximum(h0[src], e0[tgt])
                m = ov > self.esik
                if m.any():
                    for e in np.unique(ek[tgt[m]]):
                        mm = m & (ek[tgt] == e)
                        x = out.get((int(hk), int(e)), (0.0, 0))
                        out[(int(hk), int(e))] = (max(x[0], float(ov[mm].max())), x[1] + int(mm.sum()))
        return out

    def yon_gercek(self, H, E, u, azami_mm=600.0, adim_mm=None):
        """u (birim vektör, yuvarlanmamış) boyunca h mm adımla çekme: hareketli küme her adımda u·t kaydırılıp yeniden ışınlanır
        (tam sayı ızgara adımına yuvarlama yok; uygulamanın uçurduğu eksen). Döner yon() ile aynı."""
        u = np.asarray(u, float)
        u = u / (np.linalg.norm(u) or 1.0)
        adim_mm = float(adim_mm or self.h)
        hlo, hhi = _kutu(self.P, H)
        n_max = int(azami_mm / adim_mm) + 1
        D = u * adim_mm
        clo = np.minimum(hlo, hlo + D * n_max); chi = np.maximum(hhi, hhi + D * n_max)
        E = [e for e in E if _kesisir(self.P[e]["bmin"], self.P[e]["bmax"], clo, chi, 1.0)]
        if not E:
            return dict(serbest=True, yol_mm=0.0, carpan=[], dinlenme=[], engel_say=0, adim_mm=adim_mm)
        EE = {eks: self._engel(E, eks) for eks in (0, 1, 2)}
        dinlenme = self.carpisma_ofs(H, EE, np.zeros(3))
        elo, ehi = _kutu(self.P, E)
        for n in range(1, n_max + 1):
            ofs = D * n
            if not _kesisir(hlo + ofs, hhi + ofs, elo, ehi, 0.5):
                return dict(serbest=True, yol_mm=round(n * adim_mm, 2), carpan=[], dinlenme=self._liste(dinlenme), engel_say=len(E),
                            adim_mm=adim_mm)
            # yalnız kutusu engel kutusuna değen hareketli parçalar
            H2 = [k for k in H if _kesisir(self.P[k]["bmin"] + ofs, self.P[k]["bmax"] + ofs, elo, ehi, 0.5)]
            c = self.carpisma_ofs(H2, EE, ofs)
            c = {k: v for k, v in c.items() if k not in dinlenme}
            if c:
                return dict(serbest=False, yol_mm=round((n - 1) * adim_mm, 2), carpan=self._liste(c), dinlenme=self._liste(dinlenme),
                            engel_say=len(E), adim_mm=adim_mm)
        return dict(serbest=False, yol_mm=round(n_max * adim_mm, 2), carpan=[], dinlenme=self._liste(dinlenme), engel_say=len(E),
                    neden="azami yol", adim_mm=adim_mm)

    def _liste(self, c):
        return [dict(hareketli="%s [%s]" % (self.P[a]["ad"], self.P[a]["id"]), engel="%s [%s]" % (self.P[b]["ad"], self.P[b]["id"]),
                     derinlik_mm=round(v[0], 2), isin=v[1]) for (a, b), v in sorted(c.items(), key=lambda x: -x[1][0])]

    def olc(self, H, E, yonler=YONLER6, azami_mm=600.0):
        t0 = time.time()
        r = []
        for d in yonler:
            x = self.yon(H, E, d, azami_mm)
            x["yon"] = list(d)
            r.append(x)
        return dict(yonler=r, serbest_yon=[x["yon"] for x in r if x["serbest"] and not x["dinlenme"]],
                    sure_s=round(time.time() - t0, 1), h_mm=self.h, esik_mm=self.esik, tek_isin=self.I.tek)
