# 3B montaj rehberi: montaj sırası denetimi (F10c, P10.3). FreeCAD ve tarayıcı istemez; rehber/veri/rehber-veri.json + robot.glb okur.
#   python tasarim/freecad/rehber/rehber_sira.py                  # özet ekrana; çıkış 0 = ulaşılamaz bağlantı yok ve sınama geçti
#   python tasarim/freecad/rehber/rehber_sira.py --el 15          # el payı eşiği (mm; varsayılan 20) duyarlılığı için
#   python tasarim/freecad/rehber/rehber_sira.py --json <dosya>   # sonucu ayrıca JSON'a yaz
# rehber_uret.py her koşuda bunu çağırır; sonuç planlama/rehber/kontrol.json "sira" ve "perdelenme" alanlarına yazılır. numpy yoksa
# iki alan da "atlandı" olur, üretim kırılmaz. Yeni bağımlılık yok: numpy depoda zaten kullanılıyor (tasarim/freecad/carpisma.py).
#
# Kaynak: 10.11.2026 bağımsız sıra kontrolü (mesh üzerinde ışın + voksel, FreeCAD'siz; notu ve betikleri depoda değil). Bu dosya onun
# kalıcı biçimi: ölçü modeli aynı, rehberin adım içi sırasını (sira_grup) bilir ve her üretimde koşar.
#
# 1) Engel kümesi. Alet isteyen her bağlantı elemanı (alyan / yıldız / lokma / açık ağız: kod DIN 912, ISO 7380, DIN 913, horn vidası,
#    PT vida, DIN 985, DIN 934) kendi adımına kadar takılmış parçalarla ölçülür. Robot adımı: önceki adımlarda robota takılanlar (b < s)
#    + bu adımda bağlanan tezgâh alt montajı + adım içi sırada bu grubun ve önceki grupların bütün satırları. Tezgâh adımı: aynı tezgâhın
#    önceki adımları + aynı kural. Adımda sira_grup yoksa adımın bütün parçaları tek grup (10.11 kontrolüyle aynı). "tezgah" işaretli
#    grup (ör. E4 yüz kabuğu + QLED + kamera) masada hazırlanır: o grubun bağlantıları yalnız kendi grubunun parçalarıyla ölçülür,
#    grup sıradaki yerinde robota bağlanır; robota giriş yolu 7)'de ölçülür. Referans parçalar (kablo şemaları) engel değil.
# 2) Alet (ışın): 125 cm M6_erisim.py ölçü modelinin mesh üstünde yeniden yazımı. Alyan ISO 2936 kolları, alet yarıçapı r = 0,58 s + 0,6;
#    baştan eksen boyunca silindir (merkez + 2 halka). DUZ: uzun kol + 20 mm serbest; L: kısa kol + s serbest ve uzun kol ≥ 45° salınım;
#    L_DAR / ACILI (25° eğik küresel uç); YOK. Somun: lokma (eksen, iki yön, ≥ 12 mm) / açık ağız (12 yön) / altıgen cep (köşe
#    çemberinin ≥ %40'ı çevre parçanın içinde, parça başına parite).
# 3) El (voksel, 3 mm): el bölgesi = dışarıya bağlı ve her engelden ≥ EL mm uzak boş hacim. Alet rijit: düz ucunun, L uzun kolunun ya da
#    eğik kolun bir noktası el bölgesine serbest ışın demetiyle ulaşmalı; ulaşmıyorsa "kapalı hacim" (alet yerel olarak sığsa da YOK).
#    Somun: lokma ekseni ya da açık ağız şeridi 150 mm içinde el bölgesine. Uzaklık dönüşümü EL'e kadar kesik ayrılabilir min-artı
#    (kesin karesel Öklid, EL altında), bağlantı ise satır (run) grafiğinde birleşim (numpy; scipy gerekmez).
# 4) Son sınıf: DUZ, L, ACILI, LOKMA, CEP, ACIK_AGIZ, ACIK_AGIZ_DAR (tek yön), POZA_BAGLI (rehberdeki poz şartıyla açılan; G4), YOK.
#    "ulaşılamaz" = YOK; sınır 0 (üstü denetim hatası).
# 5) Sınama (her koşuda): bilinen kapalı örnek E3 yanak-horn cıvataları + E4 parçaları (bağlantısız) → hepsi YOK olmalı; bilinen
#    açık örnek A1 set vidaları + B1 alt plaka cıvataları → hepsi ulaşılır; düzeltmeden önceki E4 sırası (yüz kabuğu takılıyken tabla
#    cıvatası) → YOK. Sınama tutmazsa denetim geçmez (ölçü modeli bozuk demektir).
# 6) Perdelenme (eşik yok, yalnız ölçüm; F10d kabuk adımlarını bölerken kullanır): adımın sonunda (ve sira_grup varsa her grubun
#    sonunda) adımın yeni parçalarından hiçbir yönden görünmeyenler. Voksel ızgarada 26 yönden (6 eksen + 12 kenar + 8 köşe) dik
#    izdüşüm, hücrede en öndeki voksel görünür; yeni parçanın hiçbir vokseli hiçbir yönde önde değilse "tamamen gizli".
# 7) Giriş yolu (F10c düzeltme 1; rehber_giris.py): E3 kafa alt montajı ve sira_grup'ta "tezgah" işaretli her grup (masada hazırlanan)
#    o ana kadar takılmış parçaların arasından 6 eksen yönünden birinde düz girebiliyor mu. Temas eden / aynı düzlemdeki yüzler ve
#    0,2 mm'den sığ ortak hacim çarpışma değil (ızgara E3 0,25 mm, masa grupları 0,5 mm). Sınır: girilemeyen birim 0; sınama:
#    düzeltmeden önceki E3 sırası +y kapalı, yeni sıra +y açık, E4'te sol arka kabuk önce takılınca sağ arka kabuk kapalı.
#
# Kör noktalar (10.11 notundan): düz çizgi süpürme sıfır boşluklu geçmeleri çözemez (giriş yolu temas eden yüzleri çarpışma saymaz,
# ama baskı toleransını bilmez: sıfır boşluklu iniş "girer" görünür); kablo demetleri, fiş boyları, klemens vida yönleri
# modelde yok; mesh sapması büyük parçada 1–2 mm; G4 pozu kaba döndürme (eksenler horn merkezlerinden).
import os, sys, json, math, time, struct, argparse, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
VERI = os.path.join(ROBOT, "rehber", "veri")

try:
    import numpy as np
except ImportError:                                                  # denetim "atlandı" olur, üretim kırılmaz
    np = None

EL = 20.0            # el / parmak zarfı yarıçapı (mm): 10.11 sınamasında 18–30 doğru, 12–15'te boyun açıklığından sızma
H = 3.0              # voksel (mm)
PAY = 60.0           # ızgara payı (mm, > EL: ızgara sınırı el bölgesinde)
ORNEK_ARALIK = 1.5   # yüzey örnekleme aralığı (mm, ≤ H / 2: yüzeyde delik kalmasın)

ALYAN_S = {"M2,5x": 2.0, "M3x": 2.5, "M4x": 3.0, "M5x": 4.0, "M6x": 5.0}
ISO7380_S = {"M3x": 2.0, "M5x": 3.0, "M6x": 4.0}
DIN913_S = {"M6x": 3.0, "M5x": 2.5}
KISA = {1.5: 14.0, 2.0: 16.0, 2.5: 18.0, 3.0: 20.0, 4.0: 25.0, 5.0: 28.0}
UZUN = {1.5: 75.0, 2.0: 80.0, 2.5: 90.0, 3.0: 100.0, 4.0: 110.0, 5.0: 125.0}
SOMUN_S = {"M3": 5.5, "M4": 7.0, "M5": 8.0, "M6": 10.0}
ULASIR = ("DUZ", "L", "ACILI", "LOKMA", "CEP", "ACIK_AGIZ", "ACIK_AGIZ_DAR", "POZA_BAGLI")
# kontrol.json "sira.aciklama" (F10c düzeltme 1, kontrol B-4): F10c'den önceki veriyle bu model 18 ulaşılamaz buldu; düzeltmeden sonra 0.
ACIKLAMA = ("F10c öncesi veriyle ulaşılamaz 18, sonra 0. Kırılım: 4 gerçek sıra düzeltmesi (E4 tabla cıvataları, C5 sırası); 11 adım içi "
            "sırası tanımsız eski verinin yapaylığı (E4 tırnak 4, kamera 4, dizi vidası 3: sira_grup yokken E4'ün bütün parçaları engel "
            "sayılıyordu, eski metin de bunları kabuk kapanmadan yaptırıyordu); 3 metinde zaten yazılı sıranın / pozun veriye eklenmesi "
            "(F3 taşıyıcı M6 1: sira; G4 kaset cıvatası 2: poz S1 -45 / S2 90). Bilinen kapalı örnekler yalnız 20 mm el payında ayrılıyor "
            "(sinama.duyarlilik)")


def alet(k):
    tab = None
    if "DIN 912" in k:
        tab = ALYAN_S
    elif "ISO 7380" in k:
        tab = ISO7380_S
    elif "DIN 913" in k:
        tab = DIN913_S
    if tab:
        for pre, s in tab.items():
            if k.startswith(pre):
                return ("alyan %.1f" % s, s, 0.58 * s + 0.6, KISA[s], UZUN[s])
    if "horn vidas" in k:
        return ("yıldız PH1", 0, 3.0, 60.0, 60.0)
    if "PT vida" in k:
        return ("yıldız PH0", 0, 2.5, 50.0, 50.0)
    return None


def somun_mu(k):
    return "DIN 985" in k or "DIN 934" in k


# ---------------------------------------------------------------- GLB + veri
def glb_oku(yol):
    b = open(yol, "rb").read()
    jl = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + jl])
    o = 20 + jl
    bl = struct.unpack("<I", b[o:o + 4])[0]
    bin_ = b[o + 8:o + 8 + bl]
    acc, views = js["accessors"], js["bufferViews"]

    def oku(ai):
        a = acc[ai]
        v = views[a["bufferView"]]
        dt = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}[a["componentType"]]
        n = a["count"] * (3 if a["type"] == "VEC3" else 1)
        arr = np.frombuffer(bin_, dtype=dt, count=n, offset=v["byteOffset"] + a.get("byteOffset", 0))
        return arr.reshape(-1, 3) if a["type"] == "VEC3" else arr
    meshes = []
    for m in js["meshes"]:
        pr = m["primitives"][0]
        meshes.append((oku(pr["attributes"]["POSITION"]).astype(np.float64), oku(pr["indices"]).astype(np.int64).reshape(-1, 3)))
    nodes = [(n["name"], n["mesh"], np.array(n["matrix"], dtype=np.float64).reshape(4, 4).T) for n in js["nodes"]]
    return meshes, nodes


def dik_taban(u):
    a = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = a - u * a.dot(u)
    e1 /= np.linalg.norm(e1)
    return e1, np.cross(u, e1)


def dik_yonler(u, n):
    e1, e2 = dik_taban(u)
    return [e1 * math.cos(2 * math.pi * k / n) + e2 * math.sin(2 * math.pi * k / n) for k in range(n)]


class Sahne:
    """Parça başına üçgenler (ardışık), parça sınır kutusuyla ön seçim; vektörel Möller–Trumbore."""

    def __init__(self, parts):
        self.np_ = len(parts)
        V0, E1, E2, self.bas = [], [], [], [0]
        for p in parts:
            t = p["v"][p["f"]]
            V0.append(t[:, 0]); E1.append(t[:, 1] - t[:, 0]); E2.append(t[:, 2] - t[:, 0])
            self.bas.append(self.bas[-1] + len(t))
        self.v0, self.e1, self.e2 = np.vstack(V0), np.vstack(E1), np.vstack(E2)
        self.pi = np.repeat(np.arange(len(parts)), np.diff(self.bas))
        a, b, c = self.v0, self.v0 + self.e1, self.v0 + self.e2
        self.tmin = np.minimum(np.minimum(a, b), c)
        self.tmax = np.maximum(np.maximum(a, b), c)
        self.pmin = np.array([p["bmin"] for p in parts])
        self.pmax = np.array([p["bmax"] for p in parts])

    def sec(self, lo, hi, izin):
        pk = np.nonzero(izin & np.all(self.pmax >= lo, 1) & np.all(self.pmin <= hi, 1))[0]
        if not len(pk):
            return np.zeros(0, np.int64)
        idx = np.concatenate([np.arange(self.bas[k], self.bas[k + 1]) for k in pk])
        m = np.all(self.tmax[idx] >= lo, 1) & np.all(self.tmin[idx] <= hi, 1)
        return idx[m]

    def isin(self, O, D, tmax, idx):
        O = np.atleast_2d(O); D = np.atleast_2d(D)
        n = len(O)
        best = np.full(n, np.inf); kim = np.full(n, -1)
        if len(idx) == 0 or n == 0:
            return best, kim
        CH = max(1, 2_000_000 // max(n, 1))
        for s in range(0, len(idx), CH):
            ii = idx[s:s + CH]
            v0, e1, e2 = self.v0[ii], self.e1[ii], self.e2[ii]
            pv = np.cross(D[:, None, :], e2[None, :, :])
            det = np.einsum("nmk,mk->nm", pv, e1)
            ok = np.abs(det) > 1e-12
            inv = np.where(ok, 1.0 / np.where(ok, det, 1), 0)
            tv = O[:, None, :] - v0[None, :, :]
            u = np.einsum("nmk,nmk->nm", tv, pv) * inv
            ok &= (u >= -1e-9) & (u <= 1 + 1e-9)
            q = np.cross(tv, e1[None, :, :])
            v = np.einsum("nmk,nk->nm", q, D) * inv
            ok &= (v >= -1e-9) & (u + v <= 1 + 1e-9)
            t = np.einsum("nmk,mk->nm", q, e2) * inv
            ok &= (t > 1e-6) & (t <= tmax)
            t = np.where(ok, t, np.inf)
            j = np.argmin(t, 1)
            tj = t[np.arange(n), j]
            better = tj < best
            best[better] = tj[better]
            kim[better] = self.pi[ii[j[better]]]
        return best, kim

    def sayi(self, q, D, idx):
        """q'dan D yönünde bütün çarpmalar (parite için)."""
        v0, e1, e2 = self.v0[idx], self.e1[idx], self.e2[idx]
        pv = np.cross(D, e2); det = np.einsum("mk,mk->m", pv, e1)
        ok = np.abs(det) > 1e-12; inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        tv = q - v0; u = np.einsum("mk,mk->m", tv, pv) * inv
        qq = np.cross(tv, e1); v = (qq @ D) * inv; t = np.einsum("mk,mk->m", qq, e2) * inv
        ok &= (u >= 0) & (u <= 1) & (v >= 0) & (u + v <= 1) & (t > 1e-6) & (t < 160)
        return int(ok.sum())


# ---------------------------------------------------------------- voksel: el bölgesi
def _kesik_mesafe2(occ, R2):
    """Boş vokselden en yakın dolu voksele karesel Öklid uzaklığı (voksel biriminde), R2'de kesik (uint8). Ayrılabilir min-artı:
    eksen başına g[x] = min_k (f[x+k] + k²), |k|² < R2. R2'nin altında kesin (kesik değerler yalnız R2'ye eşit ya da üstü)."""
    R = int(math.ceil(math.sqrt(R2)))
    g = np.where(occ, 0, R2).astype(np.uint8)
    for ax in range(3):
        n = g.shape[ax]
        out = g.copy()
        for k in range(1, R + 1):
            kk = k * k
            if kk >= R2:
                break
            if k >= n:
                break
            sl_a = [slice(None)] * 3; sl_b = [slice(None)] * 3
            sl_a[ax] = slice(k, None); sl_b[ax] = slice(None, n - k)
            ga, gb = g[tuple(sl_a)], g[tuple(sl_b)]                    # ga[i] = g[i+k], gb[i] = g[i]
            # out[x] = min(out[x], g[x+k] + k²) (x = i, sl_b) ve out[x] = min(out[x], g[x-k] + k²) (x = i+k, sl_a)
            o = out[tuple(sl_b)]
            np.minimum(o, np.minimum(ga, R2 - kk) + np.uint8(kk), out=o)
            o = out[tuple(sl_a)]
            np.minimum(o, np.minimum(gb, R2 - kk) + np.uint8(kk), out=o)
        g = out
    return g


def _dis_bagli(M):
    """M (bool, 3B) içinde ızgara sınırına bağlı bileşen (6-komşuluk). z boyunca satırlar (run), komşu satırlarda örtüşen satırlar
    birleşir (örtüşmenin başladığı vokselde bir kenar); birleşim numpy etiket yayma + işaretçi atlamasıyla."""
    X, Y, Z = M.shape
    pad = np.zeros((X, Y, 1), bool)
    onc = np.concatenate([pad, M[:, :, :-1]], 2)
    bas = M & ~onc
    rid = np.cumsum(bas.ravel(), dtype=np.int32).reshape(M.shape) - 1
    n = int(rid.ravel()[-1]) + 1 if M.any() else 0
    if n == 0:
        return M.copy()
    A, B = [], []
    for ax in (0, 1):
        sl0 = [slice(None)] * 3; sl1 = [slice(None)] * 3
        sl0[ax] = slice(None, -1); sl1[ax] = slice(1, None)
        ik = M[tuple(sl0)] & M[tuple(sl1)]
        ikon = np.concatenate([np.zeros(ik.shape[:2] + (1,), bool), ik[:, :, :-1]], 2)
        b = ik & ~ikon
        A.append(rid[tuple(sl0)][b]); B.append(rid[tuple(sl1)][b])
    a = np.concatenate(A).astype(np.int64); b = np.concatenate(B).astype(np.int64)
    lab = np.arange(n, dtype=np.int64)
    for _ in range(100000):                                           # yakınsayana kadar (pratikte < 20 tur)
        la, lb = lab[a], lab[b]
        m = np.minimum(la, lb)
        if np.array_equal(la, lb):
            break
        np.minimum.at(lab, la, m)
        np.minimum.at(lab, lb, m)
        while True:
            nl = lab[lab]
            if np.array_equal(nl, lab):
                break
            lab = nl
    # sınıra değen satırlar: x / y yüzü, z = 0 ya da z = Z-1
    sinir = np.zeros(n, bool)
    for sl in ((0, slice(None), slice(None)), (X - 1, slice(None), slice(None)), (slice(None), 0, slice(None)),
               (slice(None), Y - 1, slice(None)), (slice(None), slice(None), 0), (slice(None), slice(None), Z - 1)):
        mm = M[sl]
        sinir[rid[sl][mm]] = True
    dis_lab = np.unique(lab[sinir])
    ok = np.zeros(n, bool)
    ok[np.isin(lab, dis_lab)] = True
    return M & ok[rid]


class Izgara:
    def __init__(self, parts):
        self.lo = np.min([p["bmin"] for p in parts], 0) - PAY
        hi = np.max([p["bmax"] for p in parts], 0) + PAY
        self.shape = tuple(int(x) for x in np.ceil((hi - self.lo) / H).astype(int) + 1)
        self.vox = []                                                   # parça başına benzersiz voksel (N, 3) int32
        rng = np.random.default_rng(0)
        for p in parts:
            t = p["v"][p["f"]]
            ar = 0.5 * np.linalg.norm(np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]), axis=1)
            n = np.ceil(ar * 2.0 / ORNEK_ARALIK ** 2).astype(int)
            ti = np.repeat(np.arange(len(t)), n)
            a = rng.random(len(ti)); b = rng.random(len(ti)); s = a + b > 1; a[s] = 1 - a[s]; b[s] = 1 - b[s]
            pts = [t[ti, 0] + a[:, None] * (t[ti, 1] - t[ti, 0]) + b[:, None] * (t[ti, 2] - t[ti, 0]), t.reshape(-1, 3)]
            for e0, e1 in ((0, 1), (1, 2), (2, 0)):
                L = np.linalg.norm(t[:, e1] - t[:, e0], axis=1)
                m = np.maximum(1, np.ceil(L / ORNEK_ARALIK).astype(int))
                ei = np.repeat(np.arange(len(t)), m)
                off = np.arange(len(ei)) - np.repeat(np.cumsum(m) - m, m)
                f = (off / np.repeat(m, m))[:, None]
                pts.append(t[ei, e0] + f * (t[ei, e1] - t[ei, e0]))
            ijk = np.floor((np.vstack(pts) - self.lo) / H).astype(np.int32)
            self.vox.append(np.unique(ijk, axis=0))
        self.cache = {}
        self.sure = 0.0
        self.say = 0

    def kirp(self, izin):
        """Engel kümesinin voksel kutusu (+ pay) içinde yerel ızgara: (köşe, boyut)."""
        ks = np.nonzero(izin)[0]
        if not len(ks):
            return None
        lo = np.min([self.vox[k].min(0) for k in ks if len(self.vox[k])], 0)
        hi = np.max([self.vox[k].max(0) for k in ks if len(self.vox[k])], 0)
        p = int(math.ceil(PAY / H))
        lo = np.maximum(lo - p, 0); hi = np.minimum(hi + p, np.array(self.shape) - 1)
        return lo, tuple(int(x) for x in hi - lo + 1)

    def doluluk(self, izin, kose, boy):
        occ = np.zeros(boy, bool)
        for k in np.nonzero(izin)[0]:
            v = self.vox[k] - kose
            occ[v[:, 0], v[:, 1], v[:, 2]] = True
        return occ

    def el(self, izin, anahtar, el_mm):
        """El bölgesi (bool, yerel ızgara) + köşe. Önbellekli."""
        k = (anahtar, el_mm)
        if k in self.cache:
            return self.cache[k]
        t0 = time.time()
        kr = self.kirp(izin)
        if kr is None:
            r = (None, None)
        else:
            kose, boy = kr
            occ = self.doluluk(izin, kose, boy)
            R2 = int(math.floor((el_mm / H) ** 2 - 1e-9)) + 1               # d² ≥ R2 ⇔ d·H ≥ EL (tam sayı d²)
            g = _kesik_mesafe2(occ, R2)
            r = (_dis_bagli(g >= R2), kose)
        self.cache[k] = r
        if len(self.cache) > 8:
            self.cache.pop(next(iter(self.cache)))
        self.sure += time.time() - t0
        self.say += 1
        return r

    def elde(self, E, q):
        M, kose = E
        if M is None:
            return True
        i, j, k = (np.floor((np.asarray(q) - self.lo) / H).astype(int) - kose)
        if not (0 <= i < M.shape[0] and 0 <= j < M.shape[1] and 0 <= k < M.shape[2]):
            return True                                                 # ızgara dışı: engel kutusunun dışında, el bölgesi
        return bool(M[i, j, k])


# ---------------------------------------------------------------- denetim
class Denetim:
    def __init__(self, V, glb_yol, el_mm=EL):
        self.V, self.el_mm = V, el_mm
        self.A = V["adimlar"]
        meshes, nodes = glb_oku(glb_yol)
        PP = {p["id"]: p for p in V["parcalar"]}
        self.P = []
        for name, mi, M in nodes:
            p = dict(PP[name])
            v, f = meshes[mi]
            p["v"] = v @ M[:3, :3].T + M[:3, 3]
            p["f"] = f
            p["bmin"], p["bmax"] = p["v"].min(0), p["v"].max(0)
            self.P.append(p)
        self.N = len(self.P)
        self.ID = {p["id"]: k for k, p in enumerate(self.P)}
        self.a_ = np.array([p["a"] for p in self.P]); self.b_ = np.array([p["b"] for p in self.P])
        self.t_ = np.array([p["t"] or "" for p in self.P])
        self.ref = np.array([p["tur"] == "Referans" for p in self.P])
        self.bag = np.array([p["tur"] == "Baglanti" for p in self.P])
        self.S = Sahne(self.P)
        self.G = Izgara(self.P)

    # ------------------------------------------------ adım içi sıra
    def gruplar(self, s):
        """Adım s'nin grupları: [(ad, tezgah, parça indeksleri)]; satır sırası app.js / rehber_veri ile aynı."""
        st = self.A[s]
        satir = {}
        for i, r in enumerate(st["parcalar"]):
            satir["p:%d" % i] = r["ids"]
        for i, r in enumerate(st["baglantilar"]):
            satir["b:%d" % i] = r.get("ids", [])
        if st.get("sira_grup"):
            # F10d: tezgah = masa birimi anahtarı (eski veride True; "" robotta)
            gr = [(g["ad"], (g.get("tezgah") if isinstance(g.get("tezgah"), str) else ("g%d" % n if g.get("tezgah") else "")),
                   [i for k in g["satir"] for i in satir[k]]) for n, g in enumerate(st["sira_grup"])]
        else:
            gr = [("adım", "", [i for k in satir for i in satir[k]])]
        out = []
        for ad, tz, ids in gr:
            out.append((ad, tz, np.array(sorted(self.ID[i] for i in ids), np.int64)))
        # satıra girmeyen (ısıl gömme dahil her parça bir satırda; Referans hariç) parça kalırsa son gruba
        hepsi = set(int(k) for _, _, m in out for k in m)
        kalan = [k for k in range(self.N) if self.a_[k] == s and not self.ref[k] and k not in hepsi
                 and (not st["tezgah"] or self.t_[k] == st["tezgah"])]
        if kalan:
            ad, tz, m = out[-1]
            out[-1] = (ad, tz, np.array(sorted(list(m) + kalan), np.int64))
        return out

    def taban(self, s):
        """Adım s başında yerinde olanlar (bool): robot adımı b < s + bu adımda bağlanan alt montaj; tezgâh adımı aynı tezgâh a < s."""
        st = self.A[s]
        if st["tezgah"]:
            m = (self.t_ == st["tezgah"]) & (self.a_ < s)
        else:
            m = (self.b_ < s) | ((self.b_ == s) & (self.a_ != s))
        return m & ~self.ref

    def bag_anahtar(self, s):
        """F10d: grup sırası -> robota bağladığı masa birimi anahtarı (sira_grup "bag"); bağlayan grubu olmayan birim kendi yerinde."""
        st = self.A[s]
        return {n: g["bag"] for n, g in enumerate(st.get("sira_grup") or []) if g.get("bag")}

    def durumlar(self, s):
        """Grup başına (ad, tezgah, grubun parçaları, o grubun bağlantıları ölçülürken yerinde olanlar).
        F10d: aynı anahtarlı masa grupları birikir (izin = birimin o ana kadarki parçaları); birim robota "bag" grubunda girer
        (izin = robot + birim). Bağlayan grubu olmayan masa grubu F10c'deki gibi sıradaki yerinde bağlanır."""
        b0 = self.taban(s)
        acc = b0.copy()
        out = []
        bag = self.bag_anahtar(s)
        bagli = set(bag.values())
        birim = collections.defaultdict(lambda: np.zeros(self.N, bool))
        for n, (ad, tz, ids) in enumerate(self.gruplar(s)):
            g = np.zeros(self.N, bool); g[ids] = True
            if tz:
                birim[tz] = birim[tz] | g
                izin = birim[tz].copy()
                if tz not in bagli:
                    acc = acc | g                                         # tezgâh grubu sıradaki yerinde robota bağlanır
            elif n in bag:
                acc = acc | birim[bag[n]]
                izin = acc | g
                acc = acc | g
            else:
                izin = acc | g
                acc = acc | g
            out.append((ad, tz, ids, izin))
        return out

    def birimler(self, s):
        """F10d: robota giren masa birimleri: [(grup sırası, ad, anahtar, birim parçaları, giriş anındaki engel)]."""
        st = self.A[s]
        if not st.get("sira_grup"):
            return []
        dur = self.durumlar(s)
        bag = self.bag_anahtar(s)
        bagli = set(bag.values())
        out = []
        birim = collections.defaultdict(set)
        acc = set(int(k) for k in np.nonzero(self.taban(s))[0])
        for n, (ad, tz, ids, _iz) in enumerate(dur):
            if tz:
                birim[tz] |= set(int(k) for k in ids)
                if tz not in bagli:
                    out.append((n, ad, tz, sorted(birim[tz]), sorted(acc)))
                    acc |= set(int(k) for k in ids)
            elif n in bag:
                out.append((n, ad, bag[n], sorted(birim[bag[n]]), sorted(acc)))
                acc |= birim[bag[n]] | set(int(k) for k in ids)
            else:
                acc |= set(int(k) for k in ids)
        return out

    # ------------------------------------------------ alet (ışın)
    def eksen(self, k):
        p = self.P[k]
        u = np.array(p["u"], float); u /= np.linalg.norm(u)
        v = p["v"]; e1, e2 = dik_taban(u)
        c1 = 0.5 * ((v @ e1).min() + (v @ e1).max()); c2 = 0.5 * ((v @ e2).min() + (v @ e2).max())
        tu = (v @ u).max(); tl = (v @ u).min()
        return e1 * c1 + e2 * c2 + u * tu, u, tu - tl

    def silindir(self, p0, u, r, L, iz):
        e1, e2 = dik_taban(u)
        O = [p0]
        for rr, n in ((r, 12), (0.5 * r, 6)):
            for kk in range(n):
                a = 2 * math.pi * kk / n
                O.append(p0 + rr * (math.cos(a) * e1 + math.sin(a) * e2))
        O = np.array(O) + u * 0.15
        lo = np.minimum(O.min(0), (O + u * L).min(0)) - 1; hi = np.maximum(O.max(0), (O + u * L).max(0)) + 1
        t, kim = self.S.isin(O, np.tile(u, (len(O), 1)), L, self.S.sec(lo, hi, iz))
        j = int(np.argmin(t))
        return float(min(t[j], L)), (int(kim[j]) if np.isfinite(t[j]) else -1)

    def kol_salinim(self, p0, u, s, kisa, iz):
        n = 24
        q = p0 + u * kisa
        serb = []
        for d in dik_yonler(u, n):
            w = np.cross(u, d)
            O = np.array([q + w * a + u * b for a in (-(s + 1) / 2, 0, (s + 1) / 2) for b in (-(s + 1) / 2, 0, (s + 1) / 2)])
            lo = np.minimum(O.min(0), (O + d * 70).min(0)) - 1; hi = np.maximum(O.max(0), (O + d * 70).max(0)) + 1
            t, _ = self.S.isin(O, np.tile(d, (len(O), 1)), 70.0, self.S.sec(lo, hi, iz))
            serb.append(bool(np.all(~np.isfinite(t))))
        en = cur = 0
        for v in serb + serb:
            cur = cur + 1 if v else 0
            en = max(en, min(cur, n))
        return en * 15.0

    def egik(self, p0, u, r, L, iz, aci=25.0):
        say = 0
        for d in dik_yonler(u, 12):
            v = u * math.cos(math.radians(aci)) + d * math.sin(math.radians(aci)); v /= np.linalg.norm(v)
            Lf, _ = self.silindir(p0 + u * 3.0, v, r, L, iz)
            if Lf >= L - 0.01:
                say += 1
        return say

    def alet_olc(self, k, iz):
        ad_, s, r, kisa, uzun = alet(self.P[k]["kod"])
        p0, u, _ = self.eksen(k)
        Lmax = uzun + 20.0
        Lf, kim = self.silindir(p0, u, r, Lmax, iz)
        o = dict(alet=ad_, serbest_mm=round(Lf, 1), engel=kim)
        if Lf >= Lmax - 0.01:
            o["sinif"] = "DUZ"
        elif s and Lf >= kisa + s:
            yay = self.kol_salinim(p0, u, s, kisa, iz)
            o["salinim_derece"] = yay
            o["sinif"] = "L" if yay >= 45.0 else "L_DAR"
            if o["sinif"] == "L_DAR" and self.egik(p0, u, r, uzun, iz) > 0:
                o["sinif"] = "ACILI"
        elif not s and Lf >= kisa:
            o["sinif"] = "DUZ"
        else:
            o["sinif"] = "ACILI" if (s and self.egik(p0, u, r, uzun, iz) > 0) else "YOK"
        return o

    def somun_merkez(self, k):
        p = self.P[k]
        u = np.array(p["u"], float); u /= np.linalg.norm(u)
        v = p["v"]; e1, e2 = dik_taban(u)
        c = (e1 * (0.5 * ((v @ e1).min() + (v @ e1).max())) + e2 * (0.5 * ((v @ e2).min() + (v @ e2).max()))
             + u * (0.5 * ((v @ u).min() + (v @ u).max())))
        return c, u, e1, e2, (v @ u).max() - (v @ u).min()

    def somun_olc(self, k, iz0):
        kod = self.P[k]["kod"]
        ss = [v for k_, v in SOMUN_S.items() if kod.startswith(k_ + " ")]
        s = ss[0] if ss else 7.0
        iz = iz0 & ~self.bag
        c, u, e1, e2, h = self.somun_merkez(k)
        best, bk = 0.0, -1
        for sg in (1, -1):
            Lf, kk = self.silindir(c + u * sg * h / 2, u * sg, 0.58 * s + 2.0, 60.0, iz)
            if Lf > best:
                best, bk = Lf, kk
        kal = 0
        for d in dik_yonler(u, 12):
            w = np.cross(u, d)
            O = np.array([c + d * 9.0 + w * a + u * b for a in (-9, -4.5, 0, 4.5, 9) for b in (-1, 0, 1)])
            lo = np.minimum(O.min(0), (O + d * 51).min(0)) - 1; hi = np.maximum(O.max(0), (O + d * 51).max(0)) + 1
            t, _ = self.S.isin(O, np.tile(d, (len(O), 1)), 51.0, self.S.sec(lo, hi, iz))
            kal += bool(np.all(~np.isfinite(t)))
        o = dict(alet="lokma / açık ağız %.1f" % s, lokma_serbest_mm=round(best, 1), engel=bk, acik_agiz_yon=kal)
        o["sinif"] = "LOKMA" if best >= 12 else ("ACIK_AGIZ" if kal >= 2 else "YOK")
        # altıgen cep: köşe çemberinin 0,97'si üzerindeki noktaların kaçı çevre parçalardan birinin içinde (parça başına parite)
        rc = s / math.sqrt(3) * 0.97
        dd = np.cross(u, e1) * 0.3 + e1; dd /= np.linalg.norm(dd)
        ic = 0
        for a in np.linspace(0, 2 * math.pi, 24, endpoint=False):
            q = c + rc * (math.cos(a) * e1 + math.sin(a) * e2)
            idx = self.S.sec(q - 80, q + 80, iz)
            for pk in np.unique(self.S.pi[idx]):
                if self.S.sayi(q, dd, idx[self.S.pi[idx] == pk]) % 2:
                    ic += 1
                    break
        o["cep_oran"] = round(ic / 24, 2)
        return o, s

    # ------------------------------------------------ el (voksel)
    def demet(self, O0, d, r, L, iz):
        e1, e2 = dik_taban(d)
        O = np.array([O0] + [O0 + r * (math.cos(a) * e1 + math.sin(a) * e2) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)])
        lo = np.minimum(O.min(0), (O + d * L).min(0)) - 1; hi = np.maximum(O.max(0), (O + d * L).max(0)) + 1
        t, _ = self.S.isin(O, np.tile(d, (len(O), 1)), L, self.S.sec(lo, hi, iz))
        return float(min(np.min(t), L))

    def ulas(self, E, p0, u, f, L, s0=10.0):
        for s in np.arange(s0, min(f, L) + 0.01, 1.5):
            if self.G.elde(E, p0 + u * s):
                return float(s)
        return None

    def olc(self, k, izin, anahtar):
        """Bağlantı elemanı k, engel kümesi izin (bool, k dahil olabilir): alet + el + son sınıf."""
        p = self.P[k]
        iz = izin.copy(); iz[k] = False
        E = self.G.el(izin, anahtar, self.el_mm)
        if somun_mu(p["kod"]):
            m, s = self.somun_olc(k, iz)
            izs = iz & ~self.bag
            c, u, e1, e2, h = self.somun_merkez(k)
            lok = None
            for sg in (1, -1):
                f = self.demet(c + u * sg * h / 2, u * sg, 0.58 * s + 2, 150, izs)
                x = self.ulas(E, c + u * sg * h / 2, u * sg, f, 150, s0=3.0)
                if x is not None and (lok is None or x < lok):
                    lok = x
            ag, ny = None, 0
            for d in dik_yonler(u, 12):
                w = np.cross(u, d)
                c0 = c + d * (s / math.sqrt(3) + 0.5)
                O = np.array([c0 + w * a for a in (-3.5, -1.75, 0, 1.75, 3.5)])
                lo = np.minimum(O.min(0), (O + d * 150).min(0)) - 1; hi = np.maximum(O.max(0), (O + d * 150).max(0)) + 1
                t, _ = self.S.isin(O, np.tile(d, (len(O), 1)), 150, self.S.sec(lo, hi, izs))
                f = float(min(t.min(), 150))
                x = self.ulas(E, c0, d, f, 150, s0=3.0)
                if x is not None:
                    ny += 1
                    ag = x if ag is None else min(ag, x)
            el = dict(lokma_el_mm=lok, acik_agiz_el_mm=ag, acik_agiz_yon=ny)
            c_ = m["sinif"]
            if c_ == "LOKMA" and lok is not None:
                son = "LOKMA"
            elif m["cep_oran"] >= 0.4:
                son = "CEP"
            elif ag is not None:
                son = "ACIK_AGIZ" if ny >= 2 else "ACIK_AGIZ_DAR"
            elif lok is not None:
                son = "LOKMA"
            else:
                son = "YOK"
            return dict(alet=m, el=el, sinif=son)
        m = self.alet_olc(k, iz)
        ad_, s, r, kisa, uzun = alet(p["kod"])
        p0, u, _ = self.eksen(k)
        el = {}
        c_ = m["sinif"]
        f = self.demet(p0 + u * 0.15, u, r, uzun + 20, iz)
        el["duz_el_mm"] = self.ulas(E, p0, u, f, uzun + 20)
        if c_ == "DUZ" and el["duz_el_mm"] is not None:
            return dict(alet=m, el=el, sinif="DUZ")
        if not s:                                                         # yıldız tornavida: yalnız düz
            return dict(alet=m, el=el, sinif="YOK", neden="kapalı hacim: aletin tutulacağı yer el bölgesine ulaşmıyor"
                        if c_ == "DUZ" else "eksende alet sığmıyor")
        best = None
        fa = self.demet(p0 + u * 0.15, u, r, kisa + s, iz)
        if fa >= kisa + s - 0.01:
            q = p0 + u * kisa
            for d in dik_yonler(u, 24):
                fd = self.demet(q, d, (s + 1) / 2, uzun, iz)
                x = self.ulas(E, q, d, fd, uzun, s0=15.0)
                if x is not None and (best is None or x < best):
                    best = x
        el["L_el_mm"] = best
        if c_ in ("DUZ", "L") and best is not None:
            return dict(alet=m, el=el, sinif="L")
        bt = None
        for d in dik_yonler(u, 12):
            v = u * math.cos(math.radians(25)) + d * math.sin(math.radians(25)); v /= np.linalg.norm(v)
            fv = self.demet(p0 + u * 3.0, v, r, uzun, iz)
            x = self.ulas(E, p0 + u * 3.0, v, fv, uzun)
            if x is not None and (bt is None or x < bt):
                bt = x
        el["egik_el_mm"] = bt
        if c_ in ("DUZ", "L", "L_DAR", "ACILI") and bt is not None:
            return dict(alet=m, el=el, sinif="ACILI")
        return dict(alet=m, el=el, sinif="YOK", neden="eksende alet sığmıyor" if c_ == "YOK" else
                    "kapalı hacim: alet yerel olarak sığıyor ama tutulacağı yer el bölgesine ulaşmıyor")

    def olcum_mu(self, k):
        p = self.P[k]
        return p["tur"] == "Baglanti" and bool(alet(p["kod"]) or somun_mu(p["kod"]))

    def ad(self, k):
        if k is None or k < 0:
            return None
        q = self.P[k]
        s = q["a"] if q["t"] else q["b"]
        return "%s [%s] (adım %d %s)" % (q["ad"], q["id"], s, self.A[s]["kod"])

    # ------------------------------------------------ poz (G4: rehberdeki S1 / S2 şartı)
    def poz_dene(self, k, izin, s1, s2):
        """Kol pozunu (S1 omuz, X ekseni; S2 göbek, Z ekseni; eksenler horn merkezlerinden, kaba) değiştirip ışın modeliyle yeniden ölç.
        10.11 kontrolündeki poz_g4 yöntemi. Döner: alet ölçümü (yalnız ışın)."""
        p = self.P[k]
        yan = "sag" if p["modul"].endswith("_sag") or "sağ" in p["ad"] else "sol"
        sg = 1 if yan == "sag" else -1
        mod = "omuz_" + yan
        c2s = [q for q in self.P if q["modul"] == mod and q["ad"].startswith("S2 horn") and "disk" in q["ad"]]
        c1s = [q for q in self.P if q["modul"] == mod and q["ad"].startswith("S1 horn") and "disk" in q["ad"]]
        if not c2s or not c1s:
            return None
        c2 = 0.5 * (c2s[0]["bmin"] + c2s[0]["bmax"]); c1 = 0.5 * (c1s[0]["bmin"] + c1s[0]["bmax"]); c1 = np.array([0.0, c1[1], c1[2]])

        def R(ax, ang):
            ax = np.asarray(ax, float); ax /= np.linalg.norm(ax); c, s = math.cos(ang), math.sin(ang); x, y, z = ax
            return np.array([[c + x * x * (1 - c), x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
                             [y * x * (1 - c) + z * s, c + y * y * (1 - c), y * z * (1 - c) - x * s],
                             [z * x * (1 - c) - y * s, z * y * (1 - c) + x * s, c + z * z * (1 - c)]])
        yeni = [dict(q) for q in self.P]
        for q in yeni:
            m = q["modul"]
            if not m.endswith(yan):
                continue
            kol = (m.startswith("omuz") and q["grup"] == "Ust_kol_doner") or m.startswith("dirsek")
            gob = m.startswith("omuz") and q["grup"] == "Omuz_gobegi_doner" and q["a"] >= 37
            v = q["v"]
            if kol:
                v = (v - c2) @ R([0, 0, 1], math.radians(s2 * sg)).T + c2
            if kol or gob:
                v = (v - c1) @ R([1, 0, 0], math.radians(s1)).T + c1
            q["v"] = v; q["bmin"], q["bmax"] = v.min(0), v.max(0)
        S0, P0 = self.S, self.P
        try:
            self.P, self.S = yeni, Sahne(yeni)
            iz = izin.copy(); iz[k] = False
            return self.alet_olc(k, iz)
        finally:
            self.S, self.P = S0, P0

    # ------------------------------------------------ bütün sıra
    def sira(self, adimlar=None):
        t0 = time.time()
        sonuc, adim_ozet = [], []
        for s in range(1, len(self.A)):
            if adimlar and s not in adimlar:
                continue
            st = self.A[s]
            for gi, (gad, tz, ids, izin) in enumerate(self.durumlar(s)):
                for k in ids:
                    if not self.olcum_mu(k):
                        continue
                    r = self.olc(k, izin, ("sira", s, gi))
                    p = self.P[k]
                    rec = dict(id=p["id"], ad=p["ad"], kod=p["kod"], adim=s, adim_kod=st["kod"], grup=gad, grup_tezgah=tz,
                               sinif=r["sinif"], alet=r["alet"]["alet"], alet_sinif=r["alet"]["sinif"],
                               serbest_mm=r["alet"].get("serbest_mm", r["alet"].get("lokma_serbest_mm")),
                               engel=self.ad(r["alet"].get("engel")), el=r["el"])
                    if r.get("neden"):
                        rec["neden"] = r["neden"]
                    if "cep_oran" in r["alet"]:
                        rec["cep_oran"] = r["alet"]["cep_oran"]
                    if r["sinif"] == "YOK" and st.get("poz"):
                        pz = st["poz"]
                        x = self.poz_dene(k, izin, pz["S1"], pz["S2"])
                        if x is not None:
                            rec["poz"] = dict(S1=pz["S1"], S2=pz["S2"], alet_sinif=x["sinif"], serbest_mm=x["serbest_mm"])
                            if x["sinif"] in ("DUZ", "L", "ACILI"):
                                rec["sinif"] = "POZA_BAGLI"
                                rec["neden"] = "ev pozunda kapalı; rehberdeki S1 %g / S2 %g pozunda %s (kaba döndürme)" % (
                                    pz["S1"], pz["S2"], x["sinif"])
                    sonuc.append(rec)
        say = collections.Counter(r["sinif"] for r in sonuc)
        for s in sorted({r["adim"] for r in sonuc}):
            c = collections.Counter(r["sinif"] for r in sonuc if r["adim"] == s)
            adim_ozet.append(dict(adim=s, kod=self.A[s]["kod"], adet=sum(c.values()), **dict(sorted(c.items()))))
        ulasilamaz = [r for r in sonuc if r["sinif"] not in ULASIR]
        return dict(baglanti=len(sonuc), sinif=dict(sorted(say.items())), ulasilamaz=len(ulasilamaz),
                    ulasilamaz_liste=ulasilamaz, dar=[r for r in sonuc if r["sinif"] in ("ACIK_AGIZ_DAR", "ACILI", "POZA_BAGLI")],
                    adim=adim_ozet, olcum=sonuc, sure_s=round(time.time() - t0, 1))

    # ------------------------------------------------ sınama
    def sinama(self):
        out = []

        def kos(ad, ks, izin, anahtar, bek):
            sn = [self.olc(k, izin, anahtar)["sinif"] for k in ks]
            ok = all((x in ULASIR) == (bek == "ulaşılır") for x in sn)
            out.append(dict(ad=ad, beklenen=bek, adet=len(ks), sinif=dict(collections.Counter(sn)), gecti=bool(ok and ks)))
        kod = {a["kod"]: a["i"] for a in self.A}
        e3, e4 = kod["E3"], kod["E4"]
        ks = [k for k in range(self.N) if self.a_[k] == e3 and self.olcum_mu(k)]
        iz = self.durumlar(e3)[-1][3]
        # F10c düzeltme 1: E3'te yanak-horn cıvatalarına horn merkez vidası ve pim de katıldı (adım 30'un alet isteyen bütün bağlantıları)
        kos("E3 cıvataları (yanak-horn, horn merkez vidası, pim), kendi adımında (açık olmalı)", ks, iz, ("sn", 1), "ulaşılır")
        ek = (self.a_ == e4) & ~self.ref & ~self.bag
        kos("E3 cıvataları + E4 parçaları (bilinen kapalı örnek)", ks, iz | ek, ("sn", 2), "ulaşılamaz")
        tb = [k for k in range(self.N) if self.a_[k] == e4 and self.P[k]["ad"].startswith("Tabla cıvatası")]
        kos("E4 tabla cıvataları, düzeltmeden önceki sıra (bütün E4 parçaları yerinde)", tb,
            self.taban(e4) | ((self.a_ == e4) & ~self.ref), ("sn", 3), "ulaşılamaz")
        ac = [k for k in range(self.N) if self.a_[k] in (kod["A1"], kod["B1"]) and self.olcum_mu(k)]
        for s_ in sorted({int(self.a_[k]) for k in ac}):
            kk = [k for k in ac if self.a_[k] == s_]
            kos("%s bağlantıları (bilinen açık örnek)" % self.A[s_]["kod"], kk, self.durumlar(s_)[-1][3], ("sn", 4, s_), "ulaşılır")
        for x in out:
            x["el_mm"] = self.el_mm
        # F10c düzeltme 1 (kontrol B-3): iki bilinen kapalı örnek yalnız 20 mm el payında ayrılıyor. 15 ve 12 mm'de eski sıra da
        # açık görünüyor (el boyun açıklığından sızıyor); bunu her koşuda ölçüp bilgi olarak yaz (geçme şartı değil).
        duy = []
        el0 = self.el_mm
        try:
            for el in (15.0, 12.0):
                if el == el0:
                    continue
                self.el_mm = el
                for ad, ks_, iz_, an in (("E3 cıvataları + E4 parçaları (bilinen kapalı örnek)", ks, iz | ek, ("sn", 2)),
                                         ("E4 tabla cıvataları, düzeltmeden önceki sıra", tb, self.taban(e4) | ((self.a_ == e4) & ~self.ref),
                                          ("sn", 3))):
                    sn = [self.olc(k, iz_, an)["sinif"] for k in ks_]
                    duy.append(dict(ad=ad, el_mm=el, beklenen="ulaşılamaz", sinif=dict(collections.Counter(sn)),
                                    ayirdi=bool(sn) and all(x not in ULASIR for x in sn)))
        finally:
            self.el_mm = el0
        return dict(gecti=all(x["gecti"] for x in out), sonuc=out, el_mm=el0, duyarlilik=duy,
                    not_="Bilinen kapalı örnekler el payı %g mm'de ayrılıyor; duyarlilik: 15 / 12 mm'de ayırıyor mu (bilgi, geçme şartı değil). "
                         "15 mm ve altında eski E4 sırası da açık görünüyor: C5'in eski sıraya üstünlüğü 20 mm el varsayımına dayanıyor" % el0)

    # ------------------------------------------------ giriş yolu (F10c düzeltme 1: E3 kafa, sira_grup "tezgah" grupları)
    def giris(self):
        """Alt montajın robota düz bir yönden girip giremediği (rehber_giris.py; temas ve ESIK'ten sığ dokunma çarpışma değil).
        1) E3: kafa alt montajı (tezgâh "kafa") ↔ E3'ten önce robotta olanlar. 2) sira_grup'ta "tezgah" işaretli her grup (masada
        hazırlanan): grubun parçaları ↔ adım başında yerinde olanlar + adım içi önceki gruplar. Sınır: girilemeyen birim 0.
        Sınama: düzeltmeden önceki E3 sırası (horn kafada, 625ZZ iç bileziği + pim + pul E2'de) +y'de kapalı; aynı kafa yeni sırayla
        +y'de açık; E4'te sol arka kabuk önce takılırsa sağ arka kabuk hiçbir eksenden girmez."""
        import rehber_giris as RG
        t0 = time.time()
        kod = {a["kod"]: a["i"] for a in self.A}
        e3, e4 = kod["E3"], kod["E4"]
        G3 = RG.Giris(self.P, h=0.25)
        G4 = self.G4 = RG.Giris(self.P, h=0.5)
        birim = []

        def ozet(ad, adim, G, H, E, yonler=RG.YONLER6, bek=None):
            r = G.olc(H, E, yonler)
            rec = dict(ad=ad, adim=adim, kod=self.A[adim]["kod"], hareketli=len(H), engel=len(E), serbest_yon=r["serbest_yon"],
                       serbest=bool(r["serbest_yon"]), h_mm=G.h, esik_mm=G.esik, tek_isin=r["tek_isin"], sure_s=r["sure_s"],
                       yon=[dict(yon=x["yon"], serbest=x["serbest"], yol_mm=x["yol_mm"], carpan=x["carpan"][:3], dinlenme=x["dinlenme"][:3])
                            for x in r["yonler"]])
            if bek is not None:
                rec["beklenen"] = bek
                rec["gecti"] = (rec["serbest"] == (bek == "açık"))
            return rec
        kafa = [k for k in range(self.N) if self.t_[k] == "kafa" and not self.ref[k]]
        alt3 = [k for k in range(self.N) if self.b_[k] < e3 and not self.ref[k]]
        birim.append(ozet("E3 kafa alt montajı (E3a) → tilt hornu", e3, G3, kafa, alt3))
        for s in range(len(self.A)):
            # engel = adım başında yerinde olanlar + adım içi o ana kadar robota takılan gruplar (F10d: masa birimi "bag" grubunda girer;
            # yön listesi: 6 eksen + grubun ub'si tam sayıya yuvarlanmışsa o)
            for gi, ad, tz, H, E in self.birimler(s):
                H = [k for k in H if not self.ref[k]]
                hs = set(H)
                E = sorted(k for k in E if k not in hs and not self.ref[k])
                yon = list(RG.YONLER6)
                ub = (self.A[s]["sira_grup"][gi].get("ub") or None)
                if ub:
                    t = tuple(int(round(x)) for x in ub)
                    if any(t) and abs(np.linalg.norm(ub) - 1) < 1e-3 and np.allclose(np.array(t) / np.linalg.norm(t), ub, atol=2e-3) \
                            and t not in yon:
                        yon.append(t)
                rec = ozet("%s: %s" % (self.A[s]["kod"], ad), s, G4, H, E, yon)
                if ub:
                    rec["ub"] = ub
                    t = [x for x in rec["yon"] if np.allclose(np.array(x["yon"], float) / np.linalg.norm(x["yon"]), ub, atol=2e-3)]
                    rec["ub_serbest"] = bool(t and t[0]["serbest"] and not t[0]["dinlenme"])
                    if t:
                        rec["ub_yol"] = dict(serbest=t[0]["serbest"], yol_mm=t[0]["yol_mm"], carpan=t[0]["carpan"][:3],
                                             dinlenme=t[0]["dinlenme"][:3])
                ok = self.A[s]["sira_grup"][gi].get("giris_ok") or {}         # F10d: gerekçeli istisna {desen: gerekçe}
                if ok and (not rec["serbest"] or (ub and not rec.get("ub_serbest"))):
                    rec["istisna"] = next((v for k, v in ok.items() if k in ad or k == "*"), None)
                birim.append(rec)
        # sınama
        sn = []
        adx = lambda *ss: [k for k in range(self.N) if self.P[k]["modul"] == "kafa" and any(self.P[k]["ad"].startswith(x) for x in ss)]
        horn = adx("Tilt horn 25T", "Tilt horn merkez vidası"); pim = adx("625ZZ rulman (iç bilezik)", "Pim pulu M5", "Pim cıvatası M5x12")
        if horn and pim:
            H0 = sorted(set(kafa) - set(pim) | set(horn))
            E0 = sorted((set(alt3) | set(pim)) - set(horn))
            sn.append(ozet("E3 düzeltmeden önceki sıra (horn kafada; 625ZZ iç bileziği, pim, pul E2'de): +y kapalı", e3, G3, H0, E0,
                           [(0, 1, 0)], "kapalı"))
            H1 = sorted(set(kafa) - set(horn) | set(adx("625ZZ rulman (iç bilezik)")))
            E1 = sorted((set(alt3) - set(pim)) | set(adx("Tilt horn 25T")))
            sn.append(ozet("E3 yeni sıra (horn servoda vidasız; 625ZZ kafada; pim, pul, horn vidası sonra): +y açık", e3, G3, H1, E1,
                           [(0, 1, 0)], "açık"))
        sag = [k for k in range(self.N) if self.a_[k] == e4 and self.P[k]["ad"] in ("Arka kafa kabuğu sağ",)]
        sol = [k for k in range(self.N) if self.a_[k] == e4 and self.P[k]["ad"] in ("Arka kafa kabuğu sol",)]
        if sag and sol:
            alt4 = [int(k) for k in np.nonzero(self.taban(e4))[0]]
            sn.append(ozet("E4 sağ arka kabuk, sol arka kabuk takılıyken (yanlış sıra): kapalı", e4, G4, sag, alt4 + sol, RG.YONLER6, "kapalı"))
        girilemez = [b for b in birim if not b["serbest"] and not b.get("istisna")]
        ub_kapali = [b["ad"] for b in birim if b.get("ub") and not b.get("ub_serbest") and not b.get("istisna")]   # F10d: rehberin gösterdiği yön kapalı
        return dict(ub_kapali=ub_kapali,durum="koştu", yontem="rehber_giris.py: üç eksende ışın aralıkları (kapalı mesh, parite), hareketli küme eksen yönlerinde "
                                         "h adımla çekilir; ortak hacim boyu > eşik mm olan ışın çarpışma, temas eden / aynı düzlemdeki "
                                         "yüzler çarpışma değil. Serbest = sınır kutuları ayrılana kadar çarpışma yok ve dinlenmede ortak "
                                         "hacim yok",
                    birim=birim, girilemez=len(girilemez), sinir_girilemez=0, sinama=sn,
                    istisna=[dict(ad=b["ad"], gerekce=b["istisna"], serbest_yon=b["serbest_yon"], ub_yol=b.get("ub_yol"))
                             for b in birim if b.get("istisna")],
                    gecti=bool(not girilemez and not ub_kapali and all(x["gecti"] for x in sn) and len(sn) == 3),
                    e3_kafa_serbest=bool(birim and birim[0]["serbest"]), sure_s=round(time.time() - t0, 1))

    # ------------------------------------------------ uçuş yolu (F10d): alt adımlı adımlarda her satırın patlatma yolu
    @staticmethod
    def tam_yon(u, azami=4):
        """Birim vektöre en yakın küçük tam sayı yön (rehber_giris tam sayı adımla çeker) ve aradaki açı (derece)."""
        u = np.asarray(u, float)
        u = u / (np.linalg.norm(u) or 1.0)
        en = None
        r = range(-azami, azami + 1)
        for a in r:
            for b in r:
                for c in r:
                    if not (a or b or c):
                        continue
                    if math.gcd(math.gcd(abs(a), abs(b)), abs(c)) != 1:
                        continue
                    v = np.array([a, b, c], float)
                    cs = float(v @ u) / np.linalg.norm(v)
                    if en is None or cs > en[0] + 1e-12 or (abs(cs - en[0]) <= 1e-12 and abs(a) + abs(b) + abs(c) < sum(map(abs, en[1]))):
                        en = (cs, (a, b, c))
        return en[1], round(math.degrees(math.acos(max(-1.0, min(1.0, en[0])))), 2)

    def ucus_yolu(self, adimlar=None):
        """Patlatılmış konumdan (taban + u·d) yerine giden düz yol, o satır takılmadan önce yerinde olanlarla çarpışıyor mu
        (rehber_giris.Giris, h 0,5 mm; ortak hacim > ESIK mm çarpışma, temas ve dinlenmede zaten ortak olan çift sayılmaz). Satır =
        rehber paneli / sıralı takma satırı; aynı satırdaki parçalar birlikte uçar (birbirine engel değil). Isıl gömme ev sahibiyle uçar.
        Masa birimi "bag" grubunda ub yönünden, app.js mesafesiyle (max(120, 0,8 × birim köşegeni)). Yön: eksen ya da birim köşegense
        tam sayı ızgarada, değilse uygulamanın yuvarlanmamış yönünde (yon_gercek; düzeltme turu 1, kontrol B-5). Cıvatanın eş dişi
        (es_dis) engel sayılmaz."""
        t0 = time.time()
        G = getattr(self, "G4", None)
        if G is None:
            import rehber_giris as RG
            G = self.G4 = RG.Giris(self.P, h=0.5)
        ev = collections.defaultdict(list)                              # ev sahibi -> ısıl gömmeler
        for k, p in enumerate(self.P):
            if p.get("h") and p["h"] in self.ID:
                ev[self.ID[p["h"]]].append(k)
        hosted = {k for v in ev.values() for k in v}
        out = []
        for s in range(len(self.A)):
            st = self.A[s]
            if not st.get("alt") or (adimlar and s not in adimlar):
                continue
            satir = {}
            for i, r in enumerate(st["parcalar"]):
                satir["p:%d" % i] = r["ids"]
            for i, r in enumerate(st["baglantilar"]):
                satir["b:%d" % i] = r.get("ids", [])
            dur = self.durumlar(s)
            bir = {n: (H, E) for n, _ad, _tz, H, E in self.birimler(s)}
            for n, (gad, tz, ids, izin) in enumerate(dur):
                g = st["sira_grup"][n]
                yer = izin.copy()
                yer[ids] = False
                if g.get("bag") and n in bir:
                    H, E = bir[n]
                    H = [k for k in H if not self.ref[k]]
                    lo = np.min([self.P[k]["bmin"] for k in H], 0); hi = np.max([self.P[k]["bmax"] for k in H], 0)
                    d = max(120.0, 0.8 * float(np.linalg.norm(hi - lo)))
                    out.append(self._yol(G, s, n + 1, gad, "birim", H, [e for e in E if e not in set(H) and not self.ref[e]],
                                         g.get("ub") or [0, 1, 0], d))
                for key in g["satir"]:
                    mv = [self.ID[i] for i in satir[key] if not self.ref[self.ID[i]]]
                    for k in mv:
                        if k in hosted or self.P[k]["d"] <= 0:
                            continue
                        H = [k] + ev.get(k, [])
                        hs = set(H) | set(mv)
                        E = [int(e) for e in np.nonzero(yer)[0] if int(e) not in hs and not self.ref[e]]
                        es = self.es_dis(k, E)
                        if es:
                            E = [e for e in E if e not in set(es)]
                        rec = self._yol(G, s, n + 1, gad, key, H, E, self.P[k]["u"], self.P[k]["d"])
                        if es:
                            rec["es_dis"] = [self.P[e]["ad"] for e in es]
                        out.append(rec)
                    for k in mv:
                        yer[k] = True
                        for j in ev.get(k, []):
                            yer[j] = True
        for r in out:                                                   # gerekçeli istisna: sira grubunda "ucus_ok" {desen: gerekçe}
            if not r["temiz"]:
                ok = self.A[r["adim"]]["sira_grup"][r["alt_adim"] - 1].get("ucus_ok") or {}
                r["istisna"] = next((v for k, v in ok.items() if k in r["ad"]), None)
        carp = [r for r in out if not r["temiz"] and not r.get("istisna")]
        doc = " ".join(x.strip() for x in self.ucus_yolu.__doc__.split("\n"))
        return dict(yontem=doc, h_mm=G.h, esik_mm=G.esik, satir=len(out), carpisan=len(carp), carpisan_liste=carp,
                    istisna=[r for r in out if r.get("istisna")], sinir_carpisan=0, gecti=not carp, olcum=out,
                    sure_s=round(time.time() - t0, 1))

    def es_dis(self, k, E, pay=0.5):
        """Cıvatanın eş dişi: yerindeyken sınır kutusu cıvatanınkiyle kesişen somun / ısıl gömme / perçin somun. Cıvata dişi ona
        sıfır boşlukla oturur; yön tam sayıya yuvarlanınca (açı 0,7–5,9°) gövde deliğin duvarını sıyırır (0,2–1,5 mm), bu yolun
        üstündeki bir engel değil, dişin kendisi. Uçuş yolunda engel sayılmaz, kayıtta "es_dis" listelenir."""
        p = self.P[k]
        if p["tur"] != "Baglanti" or any(x in p["ad"].lower() for x in ("somun", "gömme", "gomme")):
            return []
        out = []
        for e in E:
            q = self.P[e]
            if q["tur"] != "Baglanti" or not any(x in q["ad"].lower() for x in ("somun", "gömme", "gomme")):
                continue
            if np.all(q["bmin"] - pay <= p["bmax"]) and np.all(p["bmin"] - pay <= q["bmax"]):
                out.append(e)
        return out

    def _yol(self, G, s, alt, gad, key, H, E, u, d):
        # F10d düzeltme 1 (kontrol B-5): uygulama parçayı verideki yuvarlanmamış u boyunca uçurur (app.js). u bir eksen ya da birim
        # köşegen yönüyse (tam sayı, bileşenler -1..1; ızgara adımı ≤ h·√3) tam sayı ızgarada çekilir, aynı yol; değilse parça her
        # h adımda u·t kaydırılıp yeniden ışınlanır (yon_gercek): eskiden en yakın küçük tam sayı yöne yuvarlanıyordu (0,7–5,9°),
        # cıvata deliğinin duvarını sıyırıyor görünüyordu (12 "yön yuvarlama" istisnası ölçüm aracından doğuyordu)
        t, aci = self.tam_yon(u)
        if aci <= 0.05 and max(abs(x) for x in t) <= 1:
            r = G.yon(H, E, t, azami_mm=float(d))
            yontem = "tam sayı yön"
        else:
            r = G.yon_gercek(H, E, u, azami_mm=float(d))
            yontem = "gerçek yön (h %g mm)" % G.h
        temiz = bool(r["serbest"] or not r["carpan"])
        rec = dict(adim=s, kod=self.A[s]["kod"], alt_adim=alt, grup=gad, satir=key, id=self.P[H[0]]["id"], ad=self.P[H[0]]["ad"],
                   hareketli=len(H), u=[round(float(x), 3) for x in u], yon=list(t), yon_aci=aci, yontem=yontem,
                   d_mm=round(float(d), 1), temiz=temiz)
        if not temiz:
            rec.update(yol_mm=r["yol_mm"], carpan=r["carpan"][:3])
        return rec

    # ------------------------------------------------ F10d düzeltme 1 (kontrol B-2): ısıl gömme ev sahibi denetimi
    def isil_gomme(self):
        """Her ısıl gömme somun için (bağımsız, mesh üstünde): somunun 0,8 mm dışındaki 24 halka noktasından en çoğunu kapalı
        mesh'inin içinde tutan ana parça (ışın paritesi, eğik yön). Hata: verideki ev sahibi (h) yok, geometrik ev sahibinden farklı,
        ya da somun ev sahibinin adımında / alt montajında değil. Sınır 0."""
        D = np.array([0.5773, 0.5779, 0.5767]); D /= np.linalg.norm(D)

        def icinde(pts, k):
            p = self.P[k]
            T = p["v"][p["f"]]
            v0, e1, e2 = T[:, 0], T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
            h = np.cross(D, e2); a = np.einsum("ij,ij->i", e1, h)
            ok = np.abs(a) > 1e-12
            v0, e1, e2, h, a = v0[ok], e1[ok], e2[ok], h[ok], a[ok]
            f = 1.0 / a
            out = []
            for q in pts:
                s_ = q - v0
                uu = f * np.einsum("ij,ij->i", s_, h)
                qq = np.cross(s_, e1)
                vv = f * (qq @ D)
                tt = f * np.einsum("ij,ij->i", e2, qq)
                n = int(((uu >= 0) & (vv >= 0) & (uu + vv <= 1) & (tt > 1e-9)).sum())
                out.append(n % 2 == 1)
            return out
        ana = [k for k in range(self.N) if not self.bag[k] and not self.ref[k] and not self.P[k].get("renk")]
        out, hata = [], []
        for k, p in enumerate(self.P):
            if not (p["tur"] == "Baglanti" and "ısıl gömme" in p["kod"].lower()):
                continue
            v = p["v"]; c = 0.5 * (p["bmin"] + p["bmax"]); ext = p["bmax"] - p["bmin"]
            ax = int(np.argmax(np.abs(ext - ext.mean())))
            o1, o2 = [i for i in range(3) if i != ax]
            r = v - c
            R = float(np.sqrt(r[:, o1] ** 2 + r[:, o2] ** 2).max())
            pts = []
            for t in (-0.3 * ext[ax], 0.0, 0.3 * ext[ax]):
                for j in range(8):
                    q = c.copy(); q[ax] += t
                    q[o1] += (R + 0.8) * math.cos(2 * math.pi * j / 8); q[o2] += (R + 0.8) * math.sin(2 * math.pi * j / 8)
                    pts.append(q)
            pts = np.array(pts)
            skor = {}
            for e in ana:
                q = self.P[e]
                if np.all(q["bmin"] - 8 <= c) and np.all(c <= q["bmax"] + 8):
                    n = sum(icinde(pts, e))
                    if n:
                        skor[e] = n
            ev = max(skor, key=skor.get) if skor else None
            h = p.get("h")
            rec = dict(id=p["id"], ad=p["ad"], adim=int(p["a"]), ev_veri=h, ev_geo=self.P[ev]["id"] if ev is not None else None,
                       ev_geo_ad=self.P[ev]["ad"] if ev is not None else None, skor=skor.get(ev, 0))
            neden = []
            if ev is None:
                neden.append("geometrik ev sahibi yok")
            if not h:
                neden.append("veride ev sahibi yok")
            elif ev is not None and h != self.P[ev]["id"]:
                neden.append("veri ev sahibi geometrikten farklı (%s)" % self.P[self.ID[h]]["ad"])
            if ev is not None and (p["a"] != self.P[ev]["a"] or (p["t"] or "") != (self.P[ev]["t"] or "")):
                neden.append("somun ev sahibinin adımında değil (somun %d, ev sahibi %d)" % (p["a"], self.P[ev]["a"]))
            if neden:
                rec["hata"] = "; ".join(neden)
                hata.append(rec)
            out.append(rec)
        doc = " ".join(x.strip() for x in self.isil_gomme.__doc__.split("\n"))
        return dict(yontem=doc, toplam=len(out), hata=len(hata), hata_liste=hata, sinir_hata=0,
                    skor_en_dusuk=min((r["skor"] for r in out), default=None), gecti=not hata, olcum=out)

    # ------------------------------------------------ perdelenme
    YONLER = None

    def _yonler(self):
        if Denetim.YONLER is None:
            Y = []
            for x in (-1, 0, 1):
                for y in (-1, 0, 1):
                    for z in (-1, 0, 1):
                        if (x, y, z) != (0, 0, 0):
                            v = np.array([x, y, z], float)
                            Y.append(v / np.linalg.norm(v))
            Denetim.YONLER = Y
        return Denetim.YONLER

    def gorunen(self, izin, yeni):
        """izin: yerinde olanlar; yeni: bakılan parçalar (indeks). Döner: yeni içinden en az bir yönden görünenler (set)."""
        kr = self.G.kirp(izin)
        if kr is None:
            return set()
        kose, boy = kr
        lab = np.full(boy, -1, np.int32)                                 # -1 boş, -2 eski parça, >= 0 yeni parça indeksi
        ys = set(int(k) for k in yeni)
        for k in np.nonzero(izin)[0]:
            if int(k) in ys:
                continue
            v = self.G.vox[k] - kose
            lab[v[:, 0], v[:, 1], v[:, 2]] = -2
        for k in ys:
            v = self.G.vox[k] - kose
            lab[v[:, 0], v[:, 1], v[:, 2]] = k
        ijk = np.argwhere(lab != -1)
        L = lab[ijk[:, 0], ijk[:, 1], ijk[:, 2]]
        gor = set()
        c = ijk.astype(np.float64) + 0.5
        for d in self._yonler():
            e1, e2 = dik_taban(d)
            u = np.floor(c @ e1).astype(np.int64); v = np.floor(c @ e2).astype(np.int64); w = c @ d
            u -= u.min(); v -= v.min()
            hucre = u * (int(v.max()) + 1) + v
            o = np.lexsort((w, hucre))
            hs = hucre[o]
            ilk = np.r_[True, hs[1:] != hs[:-1]]
            gl = L[o][ilk]
            gor.update(int(x) for x in np.unique(gl[gl >= 0]))
        return gor

    def perdelenme(self, adimlar=None):
        t0 = time.time()
        out = []
        for s in range(len(self.A)):
            if adimlar and s not in adimlar:
                continue
            st = self.A[s]
            if not (self.a_ == s).any():                                      # parçasız adım (0: hazırlık): tabloda satırı olsun
                out.append(dict(adim=s, kod=st["kod"], yeni=0, gizli=0, gizli_parca=0, gizli_baglanti=0, gizli_liste=[]))
                continue
            dur = self.durumlar(s)
            yeni_hepsi = np.array([k for _, _, ids, _ in dur for k in ids if self.a_[k] == s], np.int64)
            son_izin = dur[-1][3] if not dur[-1][1] else (self.taban(s) | np.isin(np.arange(self.N), yeni_hepsi))
            if any(tz for _, tz, _, _ in dur):                              # son durum: bütün gruplar robotta
                son_izin = self.taban(s).copy()
                for _, _, ids, _ in dur:
                    son_izin[ids] = True
            gor = self.gorunen(son_izin, yeni_hepsi)
            gizli = [int(k) for k in yeni_hepsi if int(k) not in gor]
            rec = dict(adim=s, kod=st["kod"], yeni=len(yeni_hepsi), gizli=len(gizli),
                       gizli_parca=sum(1 for k in gizli if not self.bag[k]), gizli_baglanti=sum(1 for k in gizli if self.bag[k]),
                       gizli_liste=[dict(id=self.P[k]["id"], ad=self.P[k]["ad"], tur=self.P[k]["tur"]) for k in gizli])
            if st.get("sira_grup"):
                gl = []
                for n, (gad, tz, ids, izin) in enumerate(dur):
                    yn = [int(k) for k in ids if self.a_[k] == s]
                    g2 = self.gorunen(izin, yn)
                    gz = [k for k in yn if k not in g2]
                    x = dict(grup=gad, tezgah=tz, yeni=len(yn), gizli=len(gz),
                             gizli_liste=[dict(id=self.P[k]["id"], ad=self.P[k]["ad"], tur=self.P[k]["tur"]) for k in gz])
                    if st.get("alt"):                                       # F10d: alt adım sınırı (gerekçeli istisna dışında 0)
                        ist = [(k, self.istisna(s, n, k)) for k in gz]
                        x["alt_adim"] = n + 1
                        x["istisna"] = [dict(id=self.P[k]["id"], ad=self.P[k]["ad"], gerekce=g) for k, g in ist if g]
                        x["gizli_istisnasiz"] = [dict(id=self.P[k]["id"], ad=self.P[k]["ad"]) for k, g in ist if not g]
                    gl.append(x)
                rec["grup"] = gl
                if st.get("alt"):
                    rec["alt_gizli_istisnasiz"] = sum(len(x["gizli_istisnasiz"]) for x in gl)
                    rec["alt_istisna"] = sum(len(x["istisna"]) for x in gl)
            out.append(rec)
        alt = [r for r in out if "alt_gizli_istisnasiz" in r]
        return dict(yontem="voksel %g mm, 26 yönden dik izdüşüm; adımın sonunda (sira_grup varsa her grubun sonunda da) adımın yeni "
                           "parçalarından hiçbir yönden görünmeyenler (bağlantı elemanları dahil, ayrı sayılı). F10d: alt adımlı adımlarda "
                           "her alt adımda gerekçesiz tamamen gizli yeni parça sınırı 0 (gerekçeler istisna listesinde); öbür adımlarda "
                           "eşik yok" % H,
                    adim=out, toplam_gizli=sum(r["gizli"] for r in out), sure_s=round(time.time() - t0, 1),
                    alt_adim_gizli_istisnasiz=sum(r["alt_gizli_istisnasiz"] for r in alt),
                    alt_adim_istisna=sum(r["alt_istisna"] for r in alt), alt_sinir=0,
                    gecti=all(r["alt_gizli_istisnasiz"] == 0 for r in alt))

    ISTISNA_GOMME = ("ısıl gömme somun: baskı parçasının boss'unun içinde, baskıdan sonra takılı (hazırlık); ev sahibi parçayla gelir, "
                     "kendi başına görünmesi beklenmez")

    def istisna(self, s, n, k):
        """F10d: tamamen gizli yeni parçanın gerekçesi (yoksa None). Isıl gömme (hazırlıkta takılı) kategorik; öbürleri rehber_metin
        sira grubundaki "gizli_ok" ({desen: gerekçe}; veride sira_grup[n].gizli_ok)."""
        p = self.P[k]
        if p["tur"] == "Baglanti" and "ısıl gömme" in p["kod"].lower():
            return self.ISTISNA_GOMME
        g = (self.A[s].get("sira_grup") or [{}])[n]
        for d, gerekce in (g.get("gizli_ok") or {}).items():
            if d in p["ad"]:
                return gerekce
        return None


def denetle(V=None, glb=None, el_mm=EL, adimlar=None):
    """kontrol.json için iki alan: (sira, perdelenme). numpy yoksa ikisi de durum "atlandı"."""
    if np is None:
        d = dict(durum="atlandı", neden="numpy yok (pip install numpy)", gecti=True)
        return dict(d), dict(d)
    t0 = time.time()
    V = V or json.load(open(os.path.join(VERI, "rehber-veri.json"), encoding="utf-8"))
    D = Denetim(V, glb or os.path.join(VERI, "robot.glb"), el_mm)
    t1 = time.time()
    sn = D.sinama()
    sr = D.sira(adimlar)
    t2 = time.time()
    pr = D.perdelenme(adimlar)
    t3 = time.time()
    try:
        gr = D.giris()
    except Exception as e:                                              # giriş ölçümü çökerse sıra denetimi geçmez
        gr = dict(durum="hata", neden="%s: %s" % (type(e).__name__, e), gecti=False)
    t4 = time.time()
    try:                                                                # F10d: alt adımlı adımlarda uçuş yolu
        ur = dict(durum="koştu", **D.ucus_yolu(adimlar))
    except Exception as e:
        ur = dict(durum="hata", neden="%s: %s" % (type(e).__name__, e), gecti=False)
    t5 = time.time()
    try:                                                                # F10d düzeltme 1 (B-2): ısıl gömme ev sahibi
        ig = dict(durum="koştu", **D.isil_gomme())
    except Exception as e:
        ig = dict(durum="hata", neden="%s: %s" % (type(e).__name__, e), gecti=False)
    sr = dict(durum="koştu", el_mm=el_mm, voksel_mm=H, sinir_ulasilamaz=0, sinama=sn, aciklama=ACIKLAMA, giris=gr, ucus=ur, isil_gomme=ig,
              gecti=bool(sr["ulasilamaz"] == 0 and sn["gecti"] and gr.get("gecti") and ur.get("gecti") and ig.get("gecti")), **sr)
    sr["sure"] = dict(yukleme_s=round(t1 - t0, 1), sira_s=round(t2 - t1, 1), perdelenme_s=round(t3 - t2, 1), giris_s=round(t4 - t3, 1),
                      ucus_s=round(t5 - t4, 1), toplam_s=round(t5 - t0, 1), voksel_alani=D.G.say, voksel_s=round(D.G.sure, 1))
    pr = dict(durum="koştu", **pr)                                     # F10d: gecti = alt adım sınırı (perdelenme())
    return sr, pr


def ozet_yaz(sr, pr):
    if sr.get("durum") != "koştu":
        print("sira denetimi: %s (%s)" % (sr.get("durum"), sr.get("neden")))
        return
    print("sira denetimi: %d baglanti, ulasilamaz %d (sinir 0), siniflar %s, sinama %s; el %g mm, sure %s s" % (
        sr["baglanti"], sr["ulasilamaz"], sr["sinif"], "gecti" if sr["sinama"]["gecti"] else "KALDI", sr["el_mm"], sr["sure"]["toplam_s"]))
    for x in sr["sinama"]["sonuc"]:
        print("  SINAMA %-6s %s (el %g mm): %s" % ("gecti" if x["gecti"] else "KALDI", x["ad"], x.get("el_mm", sr["el_mm"]), x["sinif"]))
    for x in sr["sinama"].get("duyarlilik", []):
        print("  duyarlilik el %g mm %s: %s -> %s" % (x["el_mm"], x["ad"], x["sinif"], "ayirdi" if x["ayirdi"] else "AYIRMADI (eski sira da acik gorunuyor)"))
    gr = sr.get("giris", {})
    if gr.get("durum") == "koştu":
        print("giris yolu: girilemez %d (sinir 0), E3 kafa girisi serbest: %s, sinama %s, %s s" % (
            gr["girilemez"], "evet" if gr["e3_kafa_serbest"] else "HAYIR", "gecti" if all(x["gecti"] for x in gr["sinama"]) else "KALDI",
            gr["sure_s"]))
        for b in gr["birim"] + gr["sinama"]:
            print("  %s %s: serbest yon %s%s" % ("SINAMA " + ("gecti" if b["gecti"] else "KALDI") if "gecti" in b else "giris",
                                               b["ad"], b["serbest_yon"] or "YOK", "" if b["serbest"] else " | " + "; ".join(
                "%s %s mm %s" % (y["yon"], y["yol_mm"], (y["carpan"] or y["dinlenme"] or [{}])[0].get("engel", "")) for y in b["yon"])))
        for b in gr.get("istisna", []):
            print("  ISTISNA giris %s: %s" % (b["ad"], b["gerekce"]))
    else:
        print("giris yolu: %s (%s)" % (gr.get("durum"), gr.get("neden")))
    ur = sr.get("ucus", {})
    if ur.get("durum") == "koştu":
        print("ucus yolu: %d satir, carpisan %d (istisnasiz; sinir 0), gerekceli istisna %d, esik %g mm, %s s" % (
            ur["satir"], ur["carpisan"], len(ur["istisna"]), ur["esik_mm"], ur["sure_s"]))
        print("  es dis (civatanin kendi somunu / isil gommesi engel sayilmadi): %d satir" % sum(1 for r in ur["olcum"] if r.get("es_dis")))
        for r in ur["carpisan_liste"] + ur["istisna"]:
            print("  %s %d.%d %s %s %s yon %s (aci %s) yol %s mm: %s%s" % (
                "ISTISNA" if r.get("istisna") else "CARPAR", r["adim"], r["alt_adim"], r["kod"], r["id"], r["ad"][:40], r["yon"],
                r["yon_aci"], r.get("yol_mm"), "; ".join("%s %s" % (c.get("engel", "")[:40], c.get("derinlik_mm")) for c in r.get("carpan", [])),
                (" | " + r["istisna"][:60]) if r.get("istisna") else ""))
    else:
        print("ucus yolu: %s (%s)" % (ur.get("durum"), ur.get("neden")))
    ig = sr.get("isil_gomme", {})
    if ig.get("durum") == "koştu":
        print("isil gomme ev sahibi: %d somun, hata %d (sinir 0), en dusuk skor %s / 24" % (ig["toplam"], ig["hata"], ig["skor_en_dusuk"]))
        for r in ig["hata_liste"]:
            print("  ISIL GOMME HATA %s %s adim %s: %s" % (r["id"], r["ad"], r["adim"], r["hata"]))
    else:
        print("isil gomme ev sahibi: %s (%s)" % (ig.get("durum"), ig.get("neden")))
    for r in sr["ulasilamaz_liste"]:
        print("  ULASILAMAZ %d %s %s %s: %s" % (r["adim"], r["adim_kod"], r["id"], r["ad"], r.get("neden")))
    for r in sr["dar"]:
        print("  dar/poz %d %s %s %s %s" % (r["adim"], r["adim_kod"], r["id"], r["ad"], r["sinif"]))
    print("perdelenme: %d adim, tamamen gizli yeni parca toplam %d (adim sonunda, esik yok); alt adimlarda gerekcesiz gizli %s "
          "(sinir 0), gerekceli istisna %s" % (len(pr["adim"]), pr["toplam_gizli"], pr.get("alt_adim_gizli_istisnasiz"),
                                               pr.get("alt_adim_istisna")))
    for r in pr["adim"]:
        for x in r.get("grup", []):
            for q in x.get("gizli_istisnasiz", []):
                print("  GIZLI %d.%d %s %s %s" % (r["adim"], x["alt_adim"], r["kod"], q["id"], q["ad"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--el", type=float, default=EL)
    ap.add_argument("--json", default="")
    ap.add_argument("--adimlar", default="")
    ap.add_argument("--veri", default="")
    g = ap.parse_args()
    ad = [int(x) for x in g.adimlar.split(",") if x.strip()] or None
    V = json.load(open(g.veri, encoding="utf-8")) if g.veri else None
    sr, pr = denetle(V, None, g.el, ad)
    ozet_yaz(sr, pr)
    if g.json:
        json.dump(dict(sira=sr, perdelenme=pr), open(g.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(0 if sr.get("gecti") else 1)
