"""Çok haritalı küresel konumlama: parçacık filtresi (MCL), durum = (harita, x, y, theta).

Ağırlıklar log biçiminde tutulur. Harita olasılığı = o haritadaki parçacıkların toplam ağırlık payı. Yeniden
örnekleme HARİTA İÇİNDE yapılır (hiyerarşik): her haritanın toplam ağırlığı korunur, yalnız parçacık sayısı
olasılığa göre (alt sınırla) yeniden dağıtılır. Böylece harita olasılığı yeniden örneklemenin rastgele kaymasına
uğramaz (iki özdeş haritada pay 0,5 / 0,5 kalır) ve hiçbir harita hipotezi parçacıksız kalmaz.
"""

import math
from dataclasses import dataclass, asdict, replace

import numpy as np

from . import hareket as _hareket
from .harita2b import haritalari_yukle
from .olcum import OlcumParametreleri, log_olasilik
from .sinifla import kafes_puanla
from .tarama import LidarOzellik, tarama_hazirla


@dataclass
class MCLAyarlari:
    parcacik_sayisi: int = 3000
    baslangic: str = "kafes"               # "kafes": ilk tarama serbest alanın düzenli poz kafesinde değerlendirilir,
                                           #   parçacıklar bu sonsaldan çekilir | "rastgele": düzgün rastgele saçma
    kafes_xy: float = 0.20                 # m; başlangıç kafesi aralığı
    kafes_aci_derece: float = 3.0          # başlangıç kafesi yön aralığı
    kafes_sigma: float = 0.25              # m; kafeste ölçüm sigması (kaba kafes için geniş)
    kafes_en_cok_nokta: int = 4000         # harita başına en çok kafes noktası (aşılırsa aralık büyür)
    baslangic_carpani: float = 3.0         # "rastgele": başlangıçta N x bu kadar parçacık; ilk yeniden örneklemede N'e iner
    harita_basina_en_az: float = 0.10      # her haritada en az (bu oran x N / harita sayısı) parçacık
    tavlama_etkin_oran: float = 0.10       # bir taramadan sonra harita içi N_etkin / n bunun altına inecekse
    tavlama_en_az: float = 0.0             #   log-olasılık beta < 1 ile çarpılır (uyarlamalı tavlama)
    onsel: str = "esit"                    # "esit": her harita 1/K | "alan": serbest alanla orantılı
    yeniden_ornekleme_esigi: float = 0.5   # ağırlıklı ortalama N_etkin / n bu oranın altına inince
    guncelleme_min_d: float = 0.05         # m; son ölçüm güncellemesinden beri en az bu kadar yol ...
    guncelleme_min_a: float = 0.10         # rad; ... ya da bu kadar dönüş yoksa tarama işlenmez (ilk tarama hariç)
    rastgele_alfa_yavas: float = 0.05      # artırılmış MCL (Thrun): ışın başına ortalama log-olasılığın
    rastgele_alfa_hizli: float = 0.5       #   yavaş / hızlı ortalaması; hızlı yavaşın altına düşünce
    rastgele_en_cok: float = 0.10          #   bu orana kadar parçacık serbest alana rastgele saçılır
    harita_olasilik_tabani: float = 1e-6   # hiçbir harita bunun altına inmez (geri dönüş olanağı)
    duvar_ici_log: float = -8.0            # hareketle serbest alan dışına çıkan parçacığa log ceza
    karar_esigi: float = 0.5               # p1 - p2 < bu ise "kararsiz"
    konum_esigi: float = 0.8               # en iyi haritada ana modun payı < bu ise "konum_kararsiz"
    konum_std_esigi: float = 0.5           # m; ana modun xy std'si > bu ise "konum_kararsiz"
    mod_hucre: float = 0.5                 # m; mod arama kutusu
    mod_yaricap: float = 0.75              # m; mod kümesi yarıçapı (x ve y ayrı)
    mod_aci: float = 0.6                   # rad; mod kümesi yön payı
    mod_sayisi: int = 4
    izgara_cozunurluk: float = 0.05        # m; olasılık alanı ve serbest alan ızgarası
    serbest_pay: float = 0.20              # m; robot merkezinin yüzeye en az uzaklığı (gövde 520 x 525 mm)
    erisilebilir: bool = True              # serbest alanı başlangıçtan erişilebilen bölgeyle sınırla
    gecmis_tut: bool = True


@dataclass
class Tahmin:
    adim: int
    t: float
    olasiliklar: dict                 # harita adı -> olasılık
    en_olasi: str
    kararsiz: bool                    # en iyi iki harita farkı eşik altında
    fark: float                       # p1 - p2
    x: float
    y: float
    theta: float
    std_x: float
    std_y: float
    std_theta: float
    kovaryans: list                   # 3x3 (ana mod)
    konum_payi: float                 # ana modun en iyi harita içindeki payı
    konum_kararsiz: bool
    modlar: list                      # [{harita, x, y, theta, pay}] (pay tüm olasılığa göre)
    n_etkin: float
    parcacik_sayilari: dict
    gidilen_yol_m: float
    donus_rad: float
    olcum_islendi: bool
    rastgele_oran: float
    tavlama: float                    # son taramada kullanılan beta (1 = tam)

    def sozluk(self):
        return asdict(self)


class CokHaritaliMCL:
    def __init__(self, haritalar, ozellik=None, olcum=None, gurultu=None, ayarlar=None, tohum=None, **degisen):
        """haritalar: ad / yol / dict / Harita2B listesi. `degisen` MCLAyarlari alanlarını ezer."""
        self.haritalar = haritalari_yukle(haritalar)
        self.adlar = [h.ad for h in self.haritalar]
        self.ozellik = ozellik if ozellik is not None else LidarOzellik.varsa_dosyadan()
        self.olcum_p = olcum if olcum is not None else OlcumParametreleri()
        self.gurultu = gurultu if gurultu is not None else _hareket.HareketGurultusu()
        self.ayar = ayarlar if ayarlar is not None else MCLAyarlari()
        for k, v in degisen.items():
            if not hasattr(self.ayar, k):
                raise TypeError("bilinmeyen ayar: %s" % k)
            setattr(self.ayar, k, v)
        self.rng = np.random.default_rng(tohum)
        a = self.ayar
        for h in self.haritalar:
            h.hazirla(a.izgara_cozunurluk, a.serbest_pay, erisilebilir=a.erisilebilir)
        self.gecmis = []
        self.baslat()

    # ------------------------------------------------------------ başlatma

    def baslat(self):
        """Küresel başlatma: parçacıklar bütün haritaların serbest alanına, yön düzgün."""
        K, N = len(self.haritalar), self.ayar.parcacik_sayisi
        if self.ayar.onsel == "alan":
            alan = np.array([h.serbest_alan_m2() for h in self.haritalar])
            onsel = alan / alan.sum()
        else:
            onsel = np.full(K, 1.0 / K)
        self._onsel = onsel
        carpan = self.ayar.baslangic_carpani if self.ayar.baslangic == "rastgele" else 1.0
        sayilar = self._dagit(onsel, int(round(N * max(1.0, carpan))))
        self._doldur(sayilar, np.log(onsel))
        self._sifirla_sayaclar()
        self._kuresel = True

    def _kafesten_baslat(self, hazir):
        """İlk tarama: her haritanın serbest alan kafesi (x, y, theta) puanlanır; harita olasılığı kafes üstünde
        marjinal olabilirlik, parçacıklar harita içinde kafes sonsalından (hücre içi titreşimle) çekilir."""
        a = self.ayar
        p = replace(self.olcum_p, model="alan", sigma_isabet=a.kafes_sigma, bos_isin_sayisi=0)
        kafes = []
        lk = np.empty(len(self.haritalar))
        for k, h in enumerate(self.haritalar):
            X, Y, T, L, adim = kafes_puanla(h, hazir, p, a.kafes_xy, a.kafes_aci_derece, a.kafes_en_cok_nokta)
            kafes.append((X, Y, T, L, adim))
            lk[k] = _lse(L) - math.log(L.size) + math.log(self._onsel[k])
        P = np.exp(lk - _lse(lk))
        sayilar = self._dagit(P, a.parcacik_sayisi)
        ms, xs, ys, ts, lws = [], [], [], [], []
        yarim_a = math.radians(a.kafes_aci_derece) / 2
        for k, n in enumerate(sayilar):
            X, Y, T, L, adim = kafes[k]
            q = np.exp(L - L.max())
            q /= q.sum()
            u = (self.rng.random() + np.arange(n)) / n
            idx = np.minimum(np.searchsorted(np.cumsum(q), u), q.size - 1)
            x = X[idx] + self.rng.uniform(-adim / 2, adim / 2, n)
            y = Y[idx] + self.rng.uniform(-adim / 2, adim / 2, n)
            th = _sar(T[idx] + self.rng.uniform(-yarim_a, yarim_a, n))
            ms.append(np.full(n, k)); xs.append(x); ys.append(y); ts.append(th)
            lws.append(np.full(n, math.log(max(P[k], 1e-300)) - math.log(n)))
        self.m = np.concatenate(ms).astype(np.int64)
        self.x, self.y, self.th = np.concatenate(xs), np.concatenate(ys), np.concatenate(ts)
        self.lw = np.concatenate(lws)
        self.lw -= _lse(self.lw)
        self._harita_tabani_uygula()
        self._son_beta = 1.0

    def baslat_poz(self, harita, x, y, theta, std_xy=0.2, std_theta=0.2):
        """Bilinen başlangıç (izleme kipi): tüm parçacıklar tek haritada, pozun çevresinde."""
        k = self.adlar.index(harita)
        N = self.ayar.parcacik_sayisi
        self.m = np.full(N, k, dtype=np.int64)
        self.x = x + self.rng.normal(0, std_xy, N)
        self.y = y + self.rng.normal(0, std_xy, N)
        self.th = _sar(theta + self.rng.normal(0, std_theta, N))
        self.lw = np.full(N, -math.log(N))
        self._sifirla_sayaclar()
        self._kuresel = False

    def _sifirla_sayaclar(self):
        self.adim = 0
        self.t = 0.0
        self._birikmis = (0.0, 0.0, 0.0)
        self._son_olcumden_d = 0.0
        self._son_olcumden_a = 0.0
        self._ilk_olcum = True
        self.gidilen_yol = 0.0
        self.donus = 0.0
        self._l_yavas = None
        self._l_hizli = None
        self._son_rastgele = 0.0
        self._son_beta = 1.0
        self.gecmis = []

    def _dagit(self, olas, N):
        K = len(olas)
        en_az = max(1, int(self.ayar.harita_basina_en_az * N / K))
        kalan = N - en_az * K
        if kalan < 0:
            return np.full(K, max(1, N // K))
        ham = olas * kalan
        sayi = np.floor(ham).astype(int)
        artik = kalan - sayi.sum()
        if artik > 0:
            sayi[np.argsort(-(ham - sayi))[:artik]] += 1
        return sayi + en_az

    def _doldur(self, sayilar, log_harita):
        ms, xs, ys, ts, lws = [], [], [], [], []
        for k, n in enumerate(sayilar):
            x, y, th = self.haritalar[k].rastgele_serbest(int(n), self.rng)
            ms.append(np.full(n, k)); xs.append(x); ys.append(y); ts.append(th)
            lws.append(np.full(n, log_harita[k] - math.log(n)))
        self.m = np.concatenate(ms).astype(np.int64)
        self.x, self.y, self.th = np.concatenate(xs), np.concatenate(ys), np.concatenate(ts)
        self.lw = np.concatenate(lws)

    # ------------------------------------------------------------ hareket

    def hareket(self, dx, dy, dtheta):
        """Gövde çerçevesinde artımlı odometri. Biriktirilir; gürültüyle bir sonraki ölçümde uygulanır."""
        self._birikmis = _hareket.artim_birlestir(self._birikmis, (dx, dy, dtheta))
        d = math.hypot(dx, dy)
        self._son_olcumden_d += d
        self._son_olcumden_a += abs(dtheta)
        self.gidilen_yol += d
        self.donus += abs(dtheta)

    def hareket_hiz(self, v, w, dt):
        self.hareket(*_hareket.hizdan_artim(v, w, dt))

    def _hareketi_uygula(self):
        if self._birikmis == (0.0, 0.0, 0.0):
            return
        self.x, self.y, self.th = _hareket.uygula(self.x, self.y, self.th, self._birikmis, self.gurultu, self.rng)
        self._birikmis = (0.0, 0.0, 0.0)

    # ------------------------------------------------------------ ölçüm

    def guncelle(self, tarama, artim=None, hiz=None, zorla=False):
        """Bir adım: (isteğe bağlı) odometri + tarama. artim = (dx, dy, dth) ya da hiz = (v, w, dt). -> Tahmin."""
        if artim is not None:
            self.hareket(*artim)
        if hiz is not None:
            self.hareket_hiz(*hiz)
        return self.olcum(tarama, zorla=zorla)

    def olcum(self, tarama, zorla=False):
        a = self.ayar
        self.adim += 1
        if tarama is not None and isinstance(tarama, dict):
            self.t = float(tarama.get("t", self.t))
        hareketli = (self._son_olcumden_d >= a.guncelleme_min_d or self._son_olcumden_a >= a.guncelleme_min_a)
        islendi = False
        if tarama is not None and (zorla or self._ilk_olcum or hareketli):
            self._hareketi_uygula()
            hazir = tarama_hazirla(tarama, self.ozellik, self.olcum_p.isin_sayisi)
            if self._ilk_olcum and self._kuresel and a.baslangic == "kafes":
                self._kafesten_baslat(hazir)
            else:
                self._olcumu_isle(hazir)
            self._son_olcumden_d = self._son_olcumden_a = 0.0
            self._ilk_olcum = False
            islendi = True
        tah = self.tahmin(olcum_islendi=islendi)
        if a.gecmis_tut:
            self.gecmis.append(tah.sozluk())
        return tah

    def _olcumu_isle(self, hazir):
        a = self.ayar
        ll = np.zeros_like(self.lw)
        for k, h in enumerate(self.haritalar):
            sec = self.m == k
            if not sec.any():
                continue
            l = log_olasilik(h, self.x[sec], self.y[sec], self.th[sec], hazir, self.olcum_p)
            disarida = ~h.serbest_mi(self.x[sec], self.y[sec])
            ll[sec] = l + a.duvar_ici_log * disarida
        lort = _lse(self.lw + ll)            # log ortalama olasılık (lw normalize olduğu için)
        # uyarlamalı tavlama: harita içi N_etkin oranı hedefin altına düşmesin (sahte kesinliğe karşı)
        beta = 1.0
        if a.tavlama_etkin_oran > 0 and _ort_etkin(self.m, self.lw + ll, len(self.haritalar)) < a.tavlama_etkin_oran:
            alt, ust = 0.0, 1.0
            for _ in range(14):
                orta = 0.5 * (alt + ust)
                if _ort_etkin(self.m, self.lw + orta * ll, len(self.haritalar)) >= a.tavlama_etkin_oran:
                    alt = orta
                else:
                    ust = orta
            beta = max(alt, a.tavlama_en_az)
        self._son_beta = beta
        yeni = self.lw + beta * ll
        self.lw = yeni - _lse(yeni)
        # artırılmış MCL: ışın başına (tavlanmamış)
        b = max(1, hazir.acilar.size)
        lb = lort / (b * max(self.olcum_p.us, 1e-9))
        if self._l_yavas is None:
            self._l_yavas = self._l_hizli = lb
        else:
            self._l_yavas += a.rastgele_alfa_yavas * (lb - self._l_yavas)
            self._l_hizli += a.rastgele_alfa_hizli * (lb - self._l_hizli)
        rastgele = float(np.clip(1.0 - math.exp(min(0.0, self._l_hizli - self._l_yavas)), 0.0, a.rastgele_en_cok))
        self._son_rastgele = rastgele
        self._harita_tabani_uygula()
        if self._ort_etkin_oran() < a.yeniden_ornekleme_esigi or rastgele > 0.0:
            self._yeniden_ornekle(rastgele)

    def _harita_log(self):
        return np.array([_lse(self.lw[self.m == k]) if (self.m == k).any() else -np.inf
                         for k in range(len(self.haritalar))])

    def _harita_tabani_uygula(self):
        taban = self.ayar.harita_olasilik_tabani
        if taban <= 0:
            return
        lk = self._harita_log()
        lt = math.log(taban)
        for k in np.flatnonzero(lk < lt):
            if np.isfinite(lk[k]):
                self.lw[self.m == k] += lt - lk[k]
        self.lw -= _lse(self.lw)

    def _ort_etkin_oran(self):
        return _ort_etkin(self.m, self.lw, len(self.haritalar))

    def _yeniden_ornekle(self, rastgele):
        lk = self._harita_log()
        P = np.exp(lk - _lse(lk))
        sayilar = self._dagit(P, self.ayar.parcacik_sayisi)
        ms, xs, ys, ts, lws = [], [], [], [], []
        for k, n in enumerate(sayilar):
            sec = np.flatnonzero(self.m == k)
            w = np.exp(self.lw[sec] - lk[k])
            w /= w.sum()
            # sistematik (düşük varyanslı) örnekleme
            u = (self.rng.random() + np.arange(n)) / n
            idx = sec[np.minimum(np.searchsorted(np.cumsum(w), u), sec.size - 1)]
            x, y, th = self.x[idx].copy(), self.y[idx].copy(), self.th[idx].copy()
            r = int(round(rastgele * n))
            if r > 0:
                yer = self.rng.choice(n, size=r, replace=False)
                rx, ry, rt = self.haritalar[k].rastgele_serbest(r, self.rng)
                x[yer], y[yer], th[yer] = rx, ry, rt
            ms.append(np.full(n, k)); xs.append(x); ys.append(y); ts.append(th)
            lws.append(np.full(n, lk[k] - math.log(n)))
        self.m = np.concatenate(ms).astype(np.int64)
        self.x, self.y, self.th = np.concatenate(xs), np.concatenate(ys), np.concatenate(ts)
        self.lw = np.concatenate(lws)
        self.lw -= _lse(self.lw)

    # ------------------------------------------------------------ çıktı

    def harita_olasiliklari(self):
        lk = self._harita_log()
        P = np.exp(lk - _lse(lk))
        return {ad: float(p) for ad, p in zip(self.adlar, P)}

    def modlar(self):
        """Ağırlıklı kümeler (en ağırdan): [{harita, x, y, theta, pay, kume (indeks dizisi)}]."""
        a = self.ayar
        w = np.exp(self.lw - _lse(self.lw))
        kalan = np.ones(w.size, dtype=bool)
        sonuc = []
        nb = 8
        for _ in range(a.mod_sayisi):
            if not kalan.any():
                break
            ix = np.floor(self.x / a.mod_hucre).astype(np.int64)
            iy = np.floor(self.y / a.mod_hucre).astype(np.int64)
            it = np.floor((self.th + math.pi) / (2 * math.pi / nb)).astype(np.int64) % nb
            anahtar = ((self.m * 100003 + ix) * 100019 + iy) * nb + it
            ak = anahtar[kalan]
            tek, ters = np.unique(ak, return_inverse=True)
            top = np.bincount(ters, weights=w[kalan])
            en = tek[np.argmax(top)]
            tohum = kalan & (anahtar == en)
            k = int(self.m[tohum][0])
            cx, cy, ct = _agirlikli_ort(self.x[tohum], self.y[tohum], self.th[tohum], w[tohum])
            for _ in range(3):
                kume = (kalan & (self.m == k) & (np.abs(self.x - cx) < a.mod_yaricap)
                        & (np.abs(self.y - cy) < a.mod_yaricap) & (np.abs(_sar(self.th - ct)) < a.mod_aci))
                if not kume.any():
                    kume = tohum
                cx, cy, ct = _agirlikli_ort(self.x[kume], self.y[kume], self.th[kume], w[kume])
            pay = float(w[kume].sum())
            if sonuc and pay < 0.01:
                break
            sonuc.append(dict(harita=self.adlar[k], x=float(cx), y=float(cy), theta=float(ct), pay=pay,
                              kume=np.flatnonzero(kume)))
            kalan &= ~kume
        return sonuc

    def tahmin(self, olcum_islendi=False):
        a = self.ayar
        olas = self.harita_olasiliklari()
        sirali = sorted(olas.items(), key=lambda kv: -kv[1])
        en_olasi, p1 = sirali[0]
        p2 = sirali[1][1] if len(sirali) > 1 else 0.0
        modlar = self.modlar()
        ana = next((md for md in modlar if md["harita"] == en_olasi), None)
        w = np.exp(self.lw - _lse(self.lw))
        if ana is None:      # en olası haritada belirgin mod yok: haritanın bütün parçacıkları
            idx = np.flatnonzero(self.m == self.adlar.index(en_olasi))
            cx, cy, ct = _agirlikli_ort(self.x[idx], self.y[idx], self.th[idx], w[idx])
            ana = dict(harita=en_olasi, x=cx, y=cy, theta=ct, pay=0.0, kume=idx)
        idx = ana["kume"]
        ww = w[idx] / max(w[idx].sum(), 1e-300)
        d = np.stack([self.x[idx] - ana["x"], self.y[idx] - ana["y"], _sar(self.th[idx] - ana["theta"])])
        kov = (d * ww) @ d.T
        konum_payi = ana["pay"] / max(p1, 1e-300)
        sx, sy, st = (math.sqrt(max(kov[i, i], 0.0)) for i in range(3))
        n_etkin = float(1.0 / np.sum(w * w))
        sayilar = {ad: int((self.m == k).sum()) for k, ad in enumerate(self.adlar)}
        return Tahmin(adim=self.adim, t=self.t, olasiliklar=olas, en_olasi=en_olasi,
                      kararsiz=bool(p1 - p2 < a.karar_esigi), fark=float(p1 - p2),
                      x=float(ana["x"]), y=float(ana["y"]), theta=float(ana["theta"]),
                      std_x=sx, std_y=sy, std_theta=st, kovaryans=kov.tolist(),
                      konum_payi=float(konum_payi),
                      konum_kararsiz=bool(konum_payi < a.konum_esigi or math.hypot(sx, sy) > a.konum_std_esigi),
                      modlar=[{k: v for k, v in md.items() if k != "kume"} for md in modlar],
                      n_etkin=n_etkin, parcacik_sayilari=sayilar, gidilen_yol_m=float(self.gidilen_yol),
                      donus_rad=float(self.donus), olcum_islendi=olcum_islendi,
                      rastgele_oran=float(self._son_rastgele), tavlama=float(self._son_beta))

    def parcaciklar(self):
        """(harita indeksi, x, y, theta, ağırlık) dizileri (görselleştirme için)."""
        return self.m.copy(), self.x.copy(), self.y.copy(), self.th.copy(), np.exp(self.lw - _lse(self.lw))


# ------------------------------------------------------------ geçmiş çözümleme

def karar_ani(gecmis, dogru_harita=None, konum_da=False):
    """Kararın verildiği ve sonuna dek bozulmadığı ilk adım.

    Son adımdaki en olası harita (ya da `dogru_harita`) seçilip `kararsiz` False olduğu ve sonuna dek öyle kaldığı
    ilk kaydı döner: {adim, sira, t, gidilen_yol_m, harita, dogru}. `konum_da` ise `konum_kararsiz` da False olmalı.
    Son kayıt kararsızsa None.
    """
    if not gecmis:
        return None
    hedef = dogru_harita or gecmis[-1]["en_olasi"]

    def kararli(g):
        return (g["en_olasi"] == hedef and not g["kararsiz"] and not (konum_da and g["konum_kararsiz"]))

    if not kararli(gecmis[-1]):
        return None
    i = len(gecmis) - 1
    while i > 0 and kararli(gecmis[i - 1]):
        i -= 1
    g = gecmis[i]
    return dict(adim=g["adim"], sira=i, t=g["t"], gidilen_yol_m=g["gidilen_yol_m"], harita=hedef,
                dogru=(dogru_harita is None or gecmis[-1]["en_olasi"] == dogru_harita))


# ------------------------------------------------------------ yardımcılar

def _ort_etkin(m, lw, K):
    """Harita olasılığıyla ağırlıklı ortalama harita içi N_etkin / n (lw normalize olmak zorunda değil)."""
    toplam = _lse(lw)
    oran = 0.0
    for k in range(K):
        sec = m == k
        n = int(sec.sum())
        if n == 0:
            continue
        l = lw[sec]
        lk = _lse(l)
        if not np.isfinite(lk):
            continue
        w = np.exp(l - lk)
        oran += math.exp(lk - toplam) * (1.0 / np.sum(w * w)) / n
    return oran


def _lse(a):
    a = np.asarray(a, dtype=float)
    if a.size == 0:
        return -np.inf
    m = np.max(a)
    if not np.isfinite(m):
        return m
    return float(m + math.log(np.sum(np.exp(a - m))))


def _sar(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def _agirlikli_ort(x, y, th, w):
    s = w.sum()
    if s <= 0:
        w = np.ones_like(w)
        s = w.sum()
    return (float((w * x).sum() / s), float((w * y).sum() / s),
            float(math.atan2((w * np.sin(th)).sum(), (w * np.cos(th)).sum())))
