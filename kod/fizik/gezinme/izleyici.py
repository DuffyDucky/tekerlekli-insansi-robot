"""Rota izleyen sürücü (saf mantık: MuJoCo'ya, numpy'a bağlı DEĞİL; Pi'de de koşar).

    from gezinme.izleyici import YolIzleyici, IzleyiciAyar, on_mesafe_hesapla
    iz = YolIzleyici(IzleyiciAyar(v_max=0.25))
    iz.yol_ver([(x0, y0), (x1, y1), ...])          # harita çerçevesi, m; yeni yol eskiyi değiştirir
    k = iz.komut((x, y, th), on_mesafe=on_mesafe_hesapla(tarama, 0.60))
    k.v, k.w, k.bitti, k.durdu                     # m/s, rad/s; sur(v, w) olarak gönderilir

Yöntem: saf takip (pure pursuit) robotun DÖNME MERKEZİNDE (arka çeker dingilin ortası, gövde merkezinin
`donme_merkezi_x` = 0,185 m gerisi; ONERI robotunda ölçülen −0,180). Arka dingil noktası tek tekerlekli (unicycle) gibi
hareket eder: v o noktanın hızıdır (firmware tekerleri v ∓ w·iz/2 ile sürer, enkoder arka tekerde). İleri bakış noktası
arka dingilden `bakis_m` ötede yol üzerinde; eğrilik κ = 2 sin α / L, w = v κ.
- Yol keskin köşelerde (> `kose_esigi_rad`, varsayılan 60°) bacaklara bölünür. Bacak sonunda robot dönme merkezi köşeye
  gelene dek yavaşlayıp durur, yerinde döner, sonraki bacağa geçer: koridorda köşe orta hattın en geniş yeri, yerinde
  dönüşte süpürülen çap 1,04 m (BENIOKU). Yön hatası `donus_gir_rad`'dan büyükse (yolun başında ya da sapınca) de yerinde
  döner, `donus_cik_rad` altına inince ilerler (histerezis).
- Hız sınırı v_max / w_max; ivme sınırı (`a_max`, `a_w`; denetim aralığı `dt_s`); eğrilik w sınırını aşarsa v küçülür.
- Yumuşak varış: v ≤ k_varis · kalan, en az v_min; GÖVDE MERKEZİ son noktanın `varis_payi_m` içine girince ya da son
  noktayı geçince bitti (v = w = 0; firmware `sur 0 0`'ı fren sınırıyla durdurur).
- Engel: `on_mesafe` (gövdenin ön yüzünden öndeki şeritteki en yakın engele, m) `dur_mesafe_m` altındaysa dur ve
  bekle (durdu = True), `kalk_mesafe_m` üstüne çıkınca devam; arada `yavas_mesafe_m`'den başlayarak doğrusal yavaşla.
  Yerinde dönerken yalnız `donus_dur_mesafe_m` altında durur (ön köşe dönüşte ön yüzden ≈ 0,07 m daha dışarı süpürür).
  None = bilinmiyor (engel yok sayılır).
"""

import json
import math
import os

__all__ = ["Komut", "IzleyiciAyar", "YolIzleyici", "on_mesafe_hesapla", "bacaklara_bol", "sar"]


def sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class Komut:
    """İzleyicinin bir adımlık çıktısı. v (m/s), w (rad/s), bitti (yol sonu), durdu (engel nedeniyle bekliyor).
    Ek (bilgi): mod ("bos" | "izle" | "yerinde" | "bekle" | "bitti"), hedef (ileri bakış noktası), kalan_m."""

    __slots__ = ("v", "w", "bitti", "durdu", "mod", "hedef", "kalan_m")

    def __init__(self, v=0.0, w=0.0, bitti=False, durdu=False, mod="", hedef=None, kalan_m=None):
        self.v, self.w, self.bitti, self.durdu = float(v), float(w), bool(bitti), bool(durdu)
        self.mod, self.hedef, self.kalan_m = mod, hedef, kalan_m

    def __repr__(self):
        return "Komut(v=%.3f, w=%.3f, bitti=%s, durdu=%s, mod=%s)" % (self.v, self.w, self.bitti, self.durdu, self.mod)


class IzleyiciAyar:
    """İzleyici ayarları; hepsi anahtar sözcükle değişir: IzleyiciAyar(v_max=0.3)."""

    ALANLAR = dict(
        v_max=0.25,            # m/s seyir (deneyin hızı; teker azamisi 0,39)
        v_min=0.04,            # m/s varışta ve engel yavaşlamasında en düşük ileri hız
        w_max=1.0,             # rad/s (firmware w giriş tavanı 1,0; ONERI gerçekte ≈ 0,89 × komut)
        w_yerinde=0.8,         # rad/s yerinde dönüşün tavanı (deney 0,8)
        w_yerinde_min=0.25,    # rad/s yerinde dönüşün tabanı (küçük hatada sürünmesin)
        k_yerinde=1.6,         # yerinde dönüş oransal kazancı (rad/s / rad)
        a_max=0.5,             # m/s² ileri ivme sınırı (firmware düz sürüş sınırı 0,5)
        a_fren=1.0,            # m/s² izleyicinin kendi yavaşlama sınırı (firmware fren 1,8)
        a_w=3.0,               # rad/s² dönüş ivmesi sınırı
        bakis_m=0.6,           # m ileri bakış (dönme merkezinden)
        varis_payi_m=0.05,     # m gövde merkezi son noktaya bu kadar yaklaşınca bitti
        k_varis=0.8,           # 1/s yumuşak varış: v <= k_varis * kalan
        donus_gir_rad=0.9,     # rad bu yön hatasının üstünde yerinde dön
        donus_cik_rad=0.20,    # rad yerinde dönüşten bu hatanın altında çık
        kose_esigi_rad=math.radians(60.0),   # yolda bu açıdan keskin köşe: dur, yerinde dön
        kose_payi_m=0.06,      # m dönme merkezi köşeye bu kadar kalınca bacak biter
        dur_mesafe_m=0.30,     # m ön yüzden engel bunun altındaysa dur (sonar kuralıyla aynı 30 cm)
        kalk_mesafe_m=0.40,    # m engel bunun üstüne çıkınca devam
        yavas_mesafe_m=0.80,   # m bu mesafeden dur mesafesine dek doğrusal yavaşla
        donus_dur_mesafe_m=0.08,  # m yerinde dönerken ön yüzden engel bunun altındaysa dur
        donme_merkezi_x=-0.185,   # m dönme merkezinin (arka dingil) gövde merkezine göre x'i
        dt_s=0.05,             # s komut çağrıları arası (düzenek denetim_hz'den yazar)
        arama_geri_m=0.4,      # m izdüşüm penceresi (ilerleme tekdüze: geri en çok bu kadar bakılır)
        arama_ileri_m=1.5,     # m
    )

    def __init__(self, **degis):
        for k, v in self.ALANLAR.items():
            setattr(self, k, v)
        for k, v in degis.items():
            if k not in self.ALANLAR:
                raise ValueError("bilinmeyen izleyici ayarı %r" % k)
            setattr(self, k, v)

    def sozluk(self):
        return {k: getattr(self, k) for k in self.ALANLAR}


# ------------------------------------------------------------------ yol geometrisi
def _uzunluk(P):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(P, P[1:]))


def _sadele(P, en_kisa=1e-6):
    out = []
    for p in P:
        p = (float(p[0]), float(p[1]))
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > en_kisa:
            out.append(p)
    return out


def bacaklara_bol(P, esik_rad):
    """Keskin köşelerde (yön değişimi > esik_rad) böl: [[p...], [p...]] (köşe iki bacakta da var)."""
    if len(P) < 3:
        return [list(P)]
    bacaklar, bolum = [], [P[0]]
    for i in range(1, len(P)):
        bolum.append(P[i])
        if i + 1 < len(P):
            a = math.atan2(P[i][1] - P[i - 1][1], P[i][0] - P[i - 1][0])
            b = math.atan2(P[i + 1][1] - P[i][1], P[i + 1][0] - P[i][0])
            if abs(sar(b - a)) > esik_rad:
                bacaklar.append(bolum)
                bolum = [P[i]]
    bacaklar.append(bolum)
    return bacaklar


def _nokta(P, s):
    """Çoklu çizgide baştan s metre (s > L: son parçanın uzantısı; s < 0: ilk parçanın geri uzantısı)."""
    if s <= 0:
        a, b = P[0], P[1]
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        return (a[0] + (b[0] - a[0]) * s / L, a[1] + (b[1] - a[1]) * s / L)
    for a, b in zip(P, P[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if s <= L:
            t = s / L if L else 0.0
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        s -= L
    a, b = P[-2], P[-1]
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    return (b[0] + (b[0] - a[0]) * s / L, b[1] + (b[1] - a[1]) * s / L)


def _izdusum(P, x, y, s_alt=-1e18, s_ust=1e18):
    """(x, y)'nin çoklu çizgiye [s_alt, s_ust] aralığında en yakın izdüşümü: (s, uzaklık). Uçlarda uzantıya izin
    verir (s < 0 ya da s > L: son / ilk parçanın doğrusu)."""
    en = (None, 1e18)
    s0 = 0.0
    n = len(P) - 1
    for i, (a, b) in enumerate(zip(P, P[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        L = math.sqrt(L2)
        if L2 == 0:
            continue
        t = ((x - a[0]) * dx + (y - a[1]) * dy) / L2
        t_lo = max(-1e9 if i == 0 else 0.0, (s_alt - s0) / L)
        t_hi = min(1e9 if i == n - 1 else 1.0, (s_ust - s0) / L)
        if t_lo <= t_hi:
            t = max(t_lo, min(t_hi, t))
            d = math.hypot(a[0] + t * dx - x, a[1] + t * dy - y)
            if d < en[1]:
                en = (s0 + t * L, d)
        s0 += L
    return en


# ------------------------------------------------------------------ izleyici
class YolIzleyici:
    def __init__(self, ayar=None):
        if ayar is None:
            ayar = IzleyiciAyar()
        elif isinstance(ayar, dict):
            ayar = IzleyiciAyar(**ayar)
        self.ayar = ayar
        self.yol = []
        self._bacaklar = []
        self._bi = 0
        self._s = 0.0
        self._yerinde = False
        self._yon = 0
        self._bekliyor = False
        self._v = 0.0
        self._w = 0.0
        self._tek_nokta = False
        self._bitti = True
        self.son = Komut(mod="bos", bitti=True)

    # ------------------------------------------------------------ yol
    def yol_ver(self, noktalar):
        """[(x, y), ...] harita çerçevesi, m. Yeni yol eskiyi değiştirir (hız sürekliliği korunur). Tek nokta: robotun o
        anki yerinden o noktaya düz yol (ilk komutta kurulur). Boş liste: yol yok (dur)."""
        P = _sadele(noktalar or [])
        self.yol = P
        self._bi = 0
        self._s = 0.0
        self._yerinde = False
        self._tek_nokta = len(P) == 1
        self._bitti = len(P) == 0
        self._bacaklar = bacaklara_bol(P, self.ayar.kose_esigi_rad) if len(P) >= 2 else []

    @property
    def bitti(self):
        return self._bitti

    def kalan_yol(self, poz):
        """Gövde merkezinin yol sonuna kalan yolu (m; yaklaşık: izdüşümden)."""
        if self._bitti or not self._bacaklar:
            return 0.0
        L = [_uzunluk(b) for b in self._bacaklar]
        bacak = self._bacaklar[self._bi]
        s, _ = _izdusum(bacak, poz[0], poz[1])
        return max(0.0, L[self._bi] - s) + sum(L[self._bi + 1:])

    # ------------------------------------------------------------ yardımcılar
    def _sinirla(self, v, w):
        a = self.ayar
        dt = a.dt_s
        v = max(-a.v_max, min(a.v_max, v))
        w = max(-a.w_max, min(a.w_max, w))
        dv = v - self._v
        sinir = (a.a_max if abs(v) > abs(self._v) else a.a_fren) * dt
        v = self._v + max(-sinir, min(sinir, dv))
        dw = w - self._w
        w = self._w + max(-a.a_w * dt, min(a.a_w * dt, dw))
        if abs(v) < 1e-4:
            v = 0.0
        if abs(w) < 1e-4:
            w = 0.0
        self._v, self._w = v, w
        return v, w

    def _komut(self, v, w, **k):
        k.setdefault("bitti", False)
        self.son = Komut(v, w, **k)
        return self.son

    def _dur(self, **k):
        """Hemen dur (ivme sınırı yok: firmware fren sınırıyla durdurur)."""
        self._v = self._w = 0.0
        return self._komut(0.0, 0.0, **k)

    # ------------------------------------------------------------ ana döngü
    def komut(self, poz, on_mesafe=None):
        a = self.ayar
        x, y, th = float(poz[0]), float(poz[1]), float(poz[2])
        if self._tek_nokta and self.yol:
            self.yol_ver([(x, y), self.yol[0]])
        if self._bitti or not self._bacaklar:
            self._bitti = True
            return self._dur(bitti=True, mod="bitti" if self.yol else "bos")
        # dönme merkezi (arka dingil ortası)
        c, s_ = math.cos(th), math.sin(th)
        rx, ry = x + a.donme_merkezi_x * c, y + a.donme_merkezi_x * s_
        son_bacak = self._bi == len(self._bacaklar) - 1
        bacak = self._bacaklar[self._bi]
        L = _uzunluk(bacak)
        s_r, _ = _izdusum(bacak, rx, ry, self._s - a.arama_geri_m, self._s + a.arama_ileri_m)
        if s_r is None:
            s_r, _ = _izdusum(bacak, rx, ry)
        self._s = max(self._s, s_r)
        # bitiş / bacak sonu
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
                self._yerinde = True             # köşe: dur, yerinde dön (yön hatası çıkış eşiğine inene dek)
                return self.komut(poz, on_mesafe)
        # ileri bakış noktası (bacak sonunu geçerse doğrultunun uzantısı)
        hx, hy = _nokta(bacak, self._s + a.bakis_m)
        alfa = sar(math.atan2(hy - ry, hx - rx) - th)
        kalan_top = kalan + sum(_uzunluk(b) for b in self._bacaklar[self._bi + 1:])
        om = on_mesafe if (on_mesafe is not None and math.isfinite(on_mesafe)) else None
        onceki = self._yerinde
        if self._yerinde or abs(alfa) > a.donus_gir_rad:
            self._yerinde = abs(alfa) > a.donus_cik_rad
        if self._yerinde:
            # dönüş yönü: hata ±180°'ye yakınken (U dönüşü) poz gürültüsüyle her adımda yön değiştirmesin
            if not onceki or self._yon == 0 or abs(alfa) < 2.6:
                self._yon = 1.0 if alfa >= 0 else -1.0
            if om is not None and om < a.donus_dur_mesafe_m:
                self._bekliyor = True
                return self._dur(durdu=True, mod="bekle", hedef=(hx, hy), kalan_m=kalan_top)
            self._bekliyor = False
            w = self._yon * max(a.w_yerinde_min, min(a.w_yerinde, a.k_yerinde * abs(alfa)))
            if abs(self._v) > 0.02:                 # önce ileri hızı bırak (yay çizmeden)
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
        # saf takip
        Ld = math.hypot(hx - rx, hy - ry) or a.bakis_m
        kappa = 2.0 * math.sin(alfa) / Ld
        v = a.v_max
        if abs(kappa) * v > a.w_max:
            v = a.w_max / abs(kappa)
        # yumuşak varış (son bacakta gövde, ara bacakta dönme merkezi köşeye)
        v = min(v, max(a.v_min, a.k_varis * kalan))
        if om is not None and om < a.yavas_mesafe_m:
            oran = (om - a.dur_mesafe_m) / max(1e-6, a.yavas_mesafe_m - a.dur_mesafe_m)
            v = min(v, max(a.v_min, a.v_max * max(0.0, oran)))
        w = v * kappa
        v, w = self._sinirla(v, w)
        return self._komut(v, w, mod="izle", hedef=(hx, hy), kalan_m=kalan_top)


# ------------------------------------------------------------------ LiDAR'dan ön mesafe
_MONTAJ = None


def _lidar_montaj():
    """lidar_ozellik.json montajı (x, y, yaw rad); dosya yoksa (0,19, 0, 0)."""
    global _MONTAJ
    if _MONTAJ is None:
        yol = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lidar_ozellik.json")
        try:
            with open(yol, encoding="utf-8") as f:
                m = json.load(f).get("montaj", {})
            yaw = m.get("yaw_rad", math.radians(m.get("yaw_derece", 0.0)))
            _MONTAJ = (float(m.get("x_m", 0.19)), float(m.get("y_m", 0.0)), float(yaw))
        except (OSError, ValueError):
            _MONTAJ = (0.19, 0.0, 0.0)
    return _MONTAJ


ON_YUZ_X = 0.2642        # m gövde çarpışma kutusunun ön yüzü (lale.xml c_govde)


def on_mesafe_hesapla(tarama, genislik_m, montaj=None, on_yuz_x=ON_YUZ_X, en_cok_m=4.0):
    """LiDAR taramasından robotun önündeki şeritte (gövde ekseni boyunca, |y| ≤ genislik_m / 2) en yakın dönüşün gövde
    ÖN YÜZÜNE uzaklığı (m). Şeritte dönüş yoksa math.inf; tarama None ise None.

    tarama: sözleşme sözlüğü {"t", "acilar" (gövde çerçevesi rad), "mesafeler" (LiDAR merkezinden m; None / NaN = yok)}.
    montaj: (x, y[, yaw]) LiDAR'ın gövdedeki yeri; verilmezse lidar_ozellik.json. Açılar sözleşme gereği montaj yaw'unu
    zaten içerir. Ön yüzün gerisinde kalan noktalar (gövdenin kendisi, yanlar) sayılmaz."""
    if tarama is None:
        return None
    mx, my = (montaj or _lidar_montaj())[:2]
    yari = genislik_m / 2.0
    en = math.inf
    for a, d in zip(tarama["acilar"], tarama["mesafeler"]):
        if d is None or d != d or d <= 0:
            continue
        px = mx + d * math.cos(a)
        py = my + d * math.sin(a)
        if abs(py) <= yari and px > on_yuz_x - 0.02:
            ileri = px - on_yuz_x
            if ileri < en and ileri <= en_cok_m:
                en = ileri
    return max(0.0, en) if math.isfinite(en) else math.inf
