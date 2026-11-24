"""Koridor karışıklık deneyinin ortak parçaları: yollar, düzenek (insan engelleriyle), sürücü, MCL koşusu, ölçütler.

Mevcut modüller DEĞİŞTİRİLMEDİ; yalnız kullanıldı:
  - kod/fizik/lidar.py          SanalLidar, DeneyKaydi (LidarDeneyi'nin kurulumu burada kopyalandı: haritaya bellekte
                                insan silindiri eklemek için; dosyalar değişmez)
  - kod/fizik/konumlama/        CokHaritaliMCL (varsayılan ayarlar), tek_taramadan_sinifla, karar_ani, goreli
  - kod/fizik/varyantlar.py     sürüş varyantı (aşağıda SURUS_VARYANTI)

Sürümler (etiket): v1 = konumlayıcı c34618b (sonuçlar `ham/`, `sonuc/`, `gorsel/`; commit b2bcbfd / 72002ec, artık
yeniden üretilmez); v2 = düzeltilmiş konumlayıcı, aynı tasarım ve tohumlar (`ham_v2/`, `sonuc_v2/`, `gorsel_v2/`);
v2_360 = v2 + kör sektör yok (sanal LiDAR `kor_maske=False`, konumlayıcıda kör sektör listesi boş; robot gövdesi
ışını kesmez, `oz_govde=False` varsayılanı: VARSAYIM, taban ile gövde arasında açık LiDAR boşluğunun üst sınırı).
v2 ve v2_360 aynı fizik koşusundan çıkar: LiDAR 360° kaydedilir, v2 taraması sanal LiDAR'ın kendi maskesi
(`lidar.kor_mu`, dosyanın sektörü + 5° pay) sonradan uygulanarak elde edilir. Sanal LiDAR gürültü RNG'sini maske ne
olursa olsun her turda aynı sayıda çektiği için bu, maskeli taramayla birebir aynıdır (kos.py v1 ile karşılaştırır).

Tarihçe: v1'de D bölümü için deneyin kendi eki `baslat_poz_cok_harita` vardı; c34618b'de `baslat_poz` çok haritada
IndexError veriyordu (mcl.py 326, boş `sec` dizisinde sec[-1]). v2'de modülün kendi `baslat_poz(...,
diger_haritalar=True)`'su kullanılıyor; ek kaldırıldı.
"""

import json
import math
import os
import sys
import time

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
FIZIK = os.path.dirname(os.path.dirname(BURASI))
KOD = os.path.dirname(FIZIK)
if FIZIK not in sys.path:
    sys.path.insert(0, FIZIK)

HAM = os.path.join(BURASI, "ham")          # v1


def ham_dizini(etiket):
    return os.path.join(BURASI, "ham" if etiket == "v1" else "ham_" + etiket)
KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
KISA = {k: "K%d" % (i + 1) for i, k in enumerate(KORIDORLAR)}
HIZ = 0.25                      # m/s, sürüş hızı
ILERI_BAKIS = 0.7               # m, saf izleme (pure pursuit) ileri bakış
W_EN_COK = 1.0                  # rad/s, firmware w giriş sınırı
W_YERINDE = 0.8                 # rad/s, yerinde dönüş komutu
KONTROL_MS = 100                # sürücü döngüsü
# Bugünkü robot (V0) modelde dönemiyor (SIMULASYON.md "Dönüş", "Hareket hâlinde dönüş"): L / T dönüşü ve U dönüşü
# için Ahmet'in 23.11.2026 kararının modeli kullanıldı: öneri firmware + ön omni (küre modeli, VARSAYIM).
SURUS_VARYANTI = "ONERI"
ESIK_KONUM_YANLIS = 0.5         # m: doğru haritada konum "kesin" (konum_kararsiz False) ama hata bundan büyük


def sahne(ad):
    with open(os.path.join(FIZIK, "sahneler", ad + ".json"), encoding="utf-8") as f:
        return json.load(f)


def harita_veri(ad):
    with open(os.path.join(KOD, "araclar", "haritalar", ad + ".json"), encoding="utf-8") as f:
        return json.load(f)


def sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


# ------------------------------------------------------------------ yollar
def _ara(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def cizgi_boyu(noktalar):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(noktalar, noktalar[1:]))


def cizgide_nokta(noktalar, s):
    """Çoklu çizgi üzerinde baştan s metre ilerideki nokta."""
    for a, b in zip(noktalar, noktalar[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if s <= L:
            return _ara(a, b, s / L if L else 0.0)
        s -= L
    return tuple(noktalar[-1])


def yollar(kor):
    """Koridor başına üç başlangıç: 'bas' (başlangıç ucu), 'son' (öbür uç, ters yön), 'orta' (ortadan).

    Dönüş: {ad: noktalar}. Ardışık iki bacak arasında yön > 100° değişirse sürücü orada yerinde döner (U dönüşü)."""
    s = sahne(kor)
    oh = [tuple(p) for p in s["orta_hat"]]
    if kor == "koridor_3":                       # L: A -> B (köşe) -> C
        A, B, C = oh
        M = cizgide_nokta(oh, cizgi_boyu(oh) / 2)
        return {"bas": [A, B, C], "son": [C, B, A], "orta": [M, B, C, B, A]}
    if kor == "koridor_4":                       # T: ana hat S -> E, yan kol J -> Y
        S, E = oh
        J, Y = [tuple(p) for p in s["orta_hat_yan_kol"]]
        M = ((S[0] + E[0]) / 2, S[1])
        return {"bas": [S, E], "son": [E, J, Y], "orta": [M, E, J, Y]}
    P0, P1 = oh
    M = ((P0[0] + P1[0]) / 2, (P0[1] + P1[1]) / 2)
    return {"bas": [P0, P1], "son": [P1, P0], "orta": [M, P1, P0]}


def bacaklara_bol(noktalar, esik_derece=100.0):
    """U dönüşü noktalarında böl: [[p...], [p...]]."""
    bolum = [noktalar[0]]
    sonuc = []
    for i in range(1, len(noktalar)):
        bolum.append(noktalar[i])
        if i + 1 < len(noktalar):
            a = math.atan2(noktalar[i][1] - noktalar[i - 1][1], noktalar[i][0] - noktalar[i - 1][0])
            b = math.atan2(noktalar[i + 1][1] - noktalar[i][1], noktalar[i + 1][0] - noktalar[i][0])
            if abs(sar(b - a)) > math.radians(esik_derece):
                sonuc.append(bolum)
                bolum = [noktalar[i]]
    sonuc.append(bolum)
    return sonuc


def izdusum(noktalar, x, y, s_alt=-1e9, s_ust=1e9):
    """(x, y)'nin çoklu çizgiye en yakın izdüşümü, s aralığı içinde: (s, uzaklık)."""
    en = (None, 1e18)
    s0 = 0.0
    for a, b in zip(noktalar, noktalar[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        L = math.sqrt(L2)
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / L2))
        s = s0 + t * L
        if s_alt <= s <= s_ust:
            d = math.hypot(a[0] + t * dx - x, a[1] + t * dy - y)
            if d < en[1]:
                en = (s, d)
        s0 += L
    return en


# ------------------------------------------------------------------ insan engelleri (C)
def insan_yerlestir(kor, yol, rng, sayi=3, r=0.2):
    """Yolun düz bacaklarına, duvar tarafına `sayi` duran insan (silindir, çap 2r).

    Yanal konum: koridor yarı genişliği - 0,35 m (robot kenarıyla en az ≈ 0,19 m açıklık). Köşe / U dönüşü / uçlardan
    en az 1,5 m uzak, birbirinden en az 2,5 m aralıklı."""
    gen = {"koridor_1": 2.0, "koridor_2": 3.5, "koridor_3": 2.4, "koridor_4": 2.6, "koridor_5": 2.4, "koridor_6": 2.4}[kor]
    yan = gen / 2 - 0.35
    adaylar = []
    for a, b in zip(yol, yol[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 3.2:
            continue
        for s in np.arange(1.5, L - 1.5, 0.1):
            adaylar.append((a, b, L, float(s)))
    secilen = []
    for _ in range(2000):
        if len(secilen) == sayi:
            break
        a, b, L, s = adaylar[int(rng.integers(len(adaylar)))]
        p = _ara(a, b, s / L)
        if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 2.5 for q in secilen):
            continue
        secilen.append(p + ((b[0] - a[0]) / L, (b[1] - a[1]) / L))
    insanlar = []
    for (px, py, tx, ty) in secilen:
        k = 1.0 if rng.random() < 0.5 else -1.0          # sol / sağ duvar
        insanlar.append({"tur": "daire", "x": round(px - k * ty * yan, 3), "y": round(py + k * tx * yan, 3), "r": r})
    return insanlar


# ------------------------------------------------------------------ düzenek
class Duzenek:
    """lidar.LidarDeneyi'nin kurulumu (sahne + sahte ESP32 fizik + Pi istemcisi + LiDAR + kayıt), tek farkla:
    `ek_engeller` (haritada olmayan insanlar) fizik dünyasının haritasına BELLEKTE eklenir. Konumlayıcı özgün haritayı görür."""

    def __init__(self, kor, konum, lidar_tohum, ek_engeller=(), varyant=SURUS_VARYANTI, kor_maske=True):
        import lidar as L                      # yol eklemeleri (ortak, pi, araclar) lidar.py'de
        import varyantlar as VR
        from fizik_esp32 import FizikEsp32
        from sahte_esp32.harita import Harita
        from sahte_esp32.tasima import BellekTasima
        from lale_pi.istemci import Esp32Istemci
        self.kor = kor
        self.sahne = sahne(kor)
        veri = harita_veri(self.sahne["harita"])
        if ek_engeller:
            veri = dict(veri)
            veri["engeller"] = list(veri.get("engeller", [])) + list(ek_engeller)
        self.harita = Harita(veri, ad=kor + ("+insan" if ek_engeller else ""))
        self.c = FizikEsp32(self.harita, konum=konum, sahne=self.sahne, varyant=VR.al(varyant))
        self.w = self.c.dunya
        self.e = Esp32Istemci(BellekTasima(self.c))
        self.e.baglan()
        self.lidar = L.SanalLidar(self.w, tohum=lidar_tohum, kor_maske=kor_maske)
        self.lidar.bagla()
        self.kayit = L.DeneyKaydi(self.c, self.lidar, sahne=kor)
        o = self.e.devreye_al_ve_bekle()
        assert o.get("guc") == "devrede", o


def poz_ara(t_dizi, pozlar, t):
    """10 ms satırlardan t anındaki poz (doğrusal ara değer, yön sarılarak)."""
    i = int(np.searchsorted(t_dizi, t))
    if i <= 0:
        return tuple(pozlar[0])
    if i >= len(t_dizi):
        return tuple(pozlar[-1])
    a, b = pozlar[i - 1], pozlar[i]
    u = (t - t_dizi[i - 1]) / max(t_dizi[i] - t_dizi[i - 1], 1e-9)
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + sar(b[2] - a[2]) * u)


def sur(dz, yol, hiz=HIZ, ek_sure_s=40.0):
    """Saf izleme sürücüsü (yer gerçeğini kullanır; deneyin konusu değil). U dönüşünde yerinde döner.

    Dönüş: dict(sure_s, temas, sonar_yavaslama_s, bitti)."""
    e, w = dz.e, dz.w
    bacaklar = bacaklara_bol(yol)
    sinir = cizgi_boyu(yol) / hiz * 1.6 + ek_sure_s
    t_bas = w.zaman_s
    temas = False
    yavas = 0.0
    son_ping = -1e9
    bitti = False
    for bi, bacak in enumerate(bacaklar):
        L = cizgi_boyu(bacak)
        s_son = 0.0
        # bacağın başında yön farkı büyükse önce yerinde dön
        while True:
            x, y, _, yaw, _, _ = w.poz()
            if w.zaman_s - t_bas > sinir:
                break
            s, _ = izdusum(bacak, x, y, s_son - 0.5, s_son + 1.5)
            s = s if s is not None else s_son
            s_son = max(s_son, s)
            if s_son >= L - 0.05:
                break
            hx, hy = cizgide_nokta(bacak, min(L, s_son + ILERI_BAKIS))
            if L - s_son < ILERI_BAKIS:          # bacak sonunda hedefi çizginin uzantısına taşı (yavaşlamadan bitsin)
                a, b = bacak[-2], bacak[-1]
                ux, uy = (b[0] - a[0]) / math.hypot(b[0] - a[0], b[1] - a[1]), (b[1] - a[1]) / math.hypot(b[0] - a[0], b[1] - a[1])
                ek = ILERI_BAKIS - (L - s_son)
                hx, hy = b[0] + ux * ek, b[1] + uy * ek
            alfa = sar(math.atan2(hy - y, hx - x) - yaw)
            if abs(alfa) > 1.0:
                v, om = 0.0, math.copysign(W_YERINDE, alfa)
            else:
                v = hiz
                om = max(-W_EN_COK, min(W_EN_COK, 2.0 * hiz * math.sin(alfa) / ILERI_BAKIS))
            e.sur(round(v, 3), round(om, 3))
            if e.zaman_ms - son_ping >= 1000:
                e.ping()
                son_ping = e.zaman_ms
            e.bekle(KONTROL_MS)
            temas = temas or w.temas_engel()
            if v > 0 and abs(w.hiz()[0]) < 0.1:
                yavas += KONTROL_MS / 1000.0
        if bi + 1 < len(bacaklar):              # U dönüşü: dur, yeni bacağın yönüne dön
            e.istek({"k": "dur"})
            e.bekle(600)
            nb = bacaklar[bi + 1]
            hedef = math.atan2(nb[1][1] - nb[0][1], nb[1][0] - nb[0][0])
            while w.zaman_s - t_bas <= sinir:
                yaw = w.poz()[3]
                d = sar(hedef - yaw)
                if abs(d) < math.radians(8):
                    break
                e.sur(0.0, math.copysign(W_YERINDE, d))
                if e.zaman_ms - son_ping >= 1000:
                    e.ping()
                    son_ping = e.zaman_ms
                e.bekle(KONTROL_MS)
                temas = temas or w.temas_engel()
        else:
            bitti = s_son >= L - 0.05
    e.istek({"k": "dur"})
    e.bekle(800)
    return dict(sure_s=w.zaman_s - t_bas, temas=bool(temas), sonar_yavaslama_s=round(yavas, 2), bitti=bool(bitti))


def kayittan_akis(dz):
    """Kayıttan konumlayıcı girdisi: her tur için (tarama, odo pozu, gerçek poz, gerçek yol).

    Pozlar tur ortasında (t + 0,05 s; dönen tarama 100 ms sürer). Odometri DeneyKaydi'nin enkoder odometrisi (Pi'nin
    yapacağı gibi tiklerden, iz 0,426 m)."""
    dzl = dz.kayit.diziler()
    t = dzl["t"]
    ger, odo = dzl["gercek"], dzl["odo"]
    yol = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(ger[:, 0]), np.diff(ger[:, 1])))])
    yarim = 0.5 / dz.lidar.ayar.tarama_hz
    acilar = dzl["acilar"].tolist()
    akis = []
    for tt, m in zip(dzl["tarama_t"], dzl["mesafeler"]):
        tm = float(tt) + yarim
        g = poz_ara(t, ger, tm)
        o = poz_ara(t, odo, tm)
        i = min(int(np.searchsorted(t, tm)), len(t) - 1)
        akis.append(({"t": float(tt), "acilar": acilar, "mesafeler": m.tolist()}, o, g, float(yol[i])))
    return akis


# ------------------------------------------------------------------ konumlayıcı
_HARITALAR = None


def haritalar():
    """6 koridor haritası (Harita2B), bir kez hazırlanır (ızgaralar önbellekte; MCL ve sınıflama aynı anahtarla)."""
    global _HARITALAR
    if _HARITALAR is None:
        from konumlama.harita2b import haritalari_yukle
        _HARITALAR = haritalari_yukle(KORIDORLAR)
        for h in _HARITALAR:
            h.hazirla(0.05, 0.20, erisilebilir=True)
    return _HARITALAR


def ozellik(kor=True):
    """Konumlayıcının LiDAR özelliği; kor=False: kör sektör listesi boş (v2_360)."""
    import dataclasses
    from konumlama import LidarOzellik
    oz = LidarOzellik.varsa_dosyadan()
    return oz if kor else dataclasses.replace(oz, kor_sektorler_derece=[])


def lidar_kor_maskesi(acilar):
    """Sanal LiDAR'ın varsayılan kör maskesi (LidarAyar: dosyanın sektörü + kor_pay_derece), açılar gövde çerçevesi rad."""
    global _KOR_AYAR
    import lidar as L
    if _KOR_AYAR is None:
        a = L.LidarAyar.dosyadan()
        _KOR_AYAR = (a.kor_sektorler_derece, a.kor_pay_derece)
    return L.kor_mu(np.asarray(acilar, dtype=float), *_KOR_AYAR)


_KOR_AYAR = None


def maskele(tarama):
    """360° taramaya sanal LiDAR'ın kör maskesini sonradan uygula (kör ışın -> NaN, sanal LiDAR'ın kendisi gibi)."""
    kor = lidar_kor_maskesi(tarama["acilar"])
    m = [float("nan") if k else v for v, k in zip(tarama["mesafeler"], kor)]
    return dict(tarama, mesafeler=m)


def mcl_kos(akis, dogru, tohum, bilinen_bas=None, kor=True):
    """Konumlayıcıyı akış boyunca koştur (yalnız odometri artımı + tarama). -> adım kayıtları listesi.
    kor=False: konumlayıcıda kör sektör yok (v2_360). Bilinen başlangıç: modülün baslat_poz(..., diger_haritalar=True)."""
    from konumlama import CokHaritaliMCL
    from konumlama.benzet import goreli
    mcl = CokHaritaliMCL(haritalar(), ozellik=ozellik(kor), tohum=tohum)
    if bilinen_bas is not None:
        mcl.baslat_poz(dogru, *bilinen_bas, diger_haritalar=True)
    adimlar = []
    onceki = None
    sure = 0.0
    for i, (tar, o, g, yol) in enumerate(akis):
        artim = goreli(onceki, o) if onceki is not None else None
        onceki = o
        t0 = time.perf_counter()
        tah = mcl.guncelle(tar, artim=artim)
        sure += time.perf_counter() - t0
        ex, ey = tah.x - g[0], tah.y - g[1]
        c, s = math.cos(g[2]), math.sin(g[2])
        adimlar.append(dict(
            i=i, t=round(tar["t"], 3), yol=round(yol, 3), gx=round(g[0], 3), gy=round(g[1], 3), gth=round(g[2], 4),
            p=[round(tah.olasiliklar[k], 5) for k in KORIDORLAR], en=tah.en_olasi, kararsiz=tah.kararsiz,
            fark=round(tah.fark, 4), x=round(tah.x, 3), y=round(tah.y, 3), th=round(tah.theta, 4),
            konum_kararsiz=tah.konum_kararsiz, konum_payi=round(tah.konum_payi, 3),
            ileri=round(ex * c + ey * s, 3), yan=round(-ex * s + ey * c, 3), isl=tah.olcum_islendi,
            tav=round(tah.tavlama, 3), rast=round(tah.rastgele_oran, 3)))
    return adimlar, mcl.gecmis, sure


# ------------------------------------------------------------------ ölçütler
YOL_NOKTALARI = (2.0, 5.0, 10.0, 15.0)


def durum(a, dogru):
    if a["kararsiz"]:
        return "kararsiz"
    return "dogru" if a["en"] == dogru else "yanlis"


def olcutler(adimlar, gecmis, dogru, donem_s=0.1):
    from konumlama import karar_ani
    ka = karar_ani(gecmis, dogru_harita=dogru)
    karar_yol = adimlar[ka["sira"]]["yol"] if ka else None
    ilk_dogru = next((a for a in adimlar if durum(a, dogru) == "dogru"), None)
    yanlis = [a for a in adimlar if durum(a, dogru) == "yanlis"]
    yanlis_haritalar = sorted(set(a["en"] for a in yanlis))
    # yanlış dilimleri (ardışık adımlar)
    dilimler = []
    for a in yanlis:
        if dilimler and a["i"] == dilimler[-1]["son_i"] + 1 and a["en"] == dilimler[-1]["harita"]:
            dilimler[-1]["son_i"] = a["i"]; dilimler[-1]["son_yol"] = a["yol"]; dilimler[-1]["adim"] += 1
        else:
            dilimler.append(dict(harita=a["en"], ilk_i=a["i"], son_i=a["i"], ilk_yol=a["yol"], son_yol=a["yol"], adim=1,
                                 en_buyuk_p=0.0))
        dilimler[-1]["en_buyuk_p"] = max(dilimler[-1]["en_buyuk_p"], a["p"][KORIDORLAR.index(a["en"])])
    yol_durum = {}
    for d in YOL_NOKTALARI:
        a = next((a for a in adimlar if a["yol"] >= d), None)
        yol_durum["%g" % d] = durum(a, dogru) if a is not None else None
    # karar sonrası konum hatası (doğru harita en olası iken)
    sonra = [a for a in adimlar[(ka["sira"] if ka else len(adimlar)):] if a["en"] == dogru]
    ileri = np.array([a["ileri"] for a in sonra]) if sonra else np.zeros(0)
    yan = np.array([a["yan"] for a in sonra]) if sonra else np.zeros(0)
    xy = np.hypot(ileri, yan) if sonra else np.zeros(0)
    konum_yanlis = [a for a in adimlar if a["en"] == dogru and not a["kararsiz"] and not a["konum_kararsiz"]
                    and math.hypot(a["ileri"], a["yan"]) > ESIK_KONUM_YANLIS]

    def ist(v):
        if v.size == 0:
            return None
        return dict(ort_mutlak=round(float(np.mean(np.abs(v))), 3), rms=round(float(np.sqrt(np.mean(v * v))), 3),
                    p95=round(float(np.percentile(np.abs(v), 95)), 3), en_cok=round(float(np.max(np.abs(v))), 3))
    son = adimlar[-1]
    return dict(
        karar_yol_m=karar_yol, karar_t_s=(round(ka["t"] - adimlar[0]["t"], 2) if ka else None),
        ilk_dogru_yol_m=(ilk_dogru["yol"] if ilk_dogru else None),
        yanlis_adim=len(yanlis), yanlis_sure_s=round(len(yanlis) * donem_s, 2), yanlis_haritalar=yanlis_haritalar,
        yanlis_dilimler=dilimler, yol_durum=yol_durum,
        konum_ileri=ist(ileri), konum_yan=ist(yan), konum_xy=ist(xy),
        konum_yanlis_adim=len(konum_yanlis),
        son_dogru=(son["en"] == dogru), son_durum=durum(son, dogru), son_p_dogru=son["p"][KORIDORLAR.index(dogru)],
        toplam_yol_m=son["yol"], adim_sayisi=len(adimlar))
