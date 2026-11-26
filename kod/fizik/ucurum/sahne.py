"""Uçurum sahneleri: sonlu zemin kutuları + aşağı inen merdiven / dik boşluk / köşe, ve yanlış alarm denetim sahneleri.

Mevcut sahne kurucusu (`dunya.sahne_xml`) zemini SONSUZ düzlem (`zemin_duz`, type="plane") olarak kurar; uçurum
olamaz. Bu modül ortak dosyaya dokunmadan, yalnız kendi sürecinde `dunya.sahne_xml`'i sarmalar (`kur()`): sahne
sözlüğünde `ucurum` alanı varsa düzlem satırı sonlu kutularla değiştirilir; yoksa çıktı birebir aynıdır.

Dünya çerçevesi: `acik_alan` haritası (30 x 30 m, çevre duvarı yok, x = 20'de 1 m yüksek tek duvar). Kenar x = E = 16
çizgisinde (y boyunca), boşluk +x yönünde. Üst zemin yüzü z = 0. Kutu adları `zemin_*` (dunya.zemin_geom; gövde-zemin
teması sayılır). Sahne geom'larının sürtünmesi 0 (dunya.sahne_xml ile aynı kural: temas katsayısı robot tarafından).

Hakem için her sahnenin `kenarlar` listesi: [nx, ny, c] yarı düzlemleri; bir noktanın payı = min_i (c_i - n_i . p),
pozitif = güvenli taraf. Sensör / denetçi bu bilgiyi GÖRMEZ (yalnız hakem).
"""

import math
import re

E = 16.0          # kenar çizgisi x (m)
Y0 = 15.0         # sahne orta hattı y
X_MIN, X_MAX, Y_MIN, Y_MAX = 6.0, 24.0, 5.0, 25.0
HARITA = "acik_alan"
RENK_BASAMAK = "0.78 0.74 0.66 1"
RENK_KOYU = "0.06 0.06 0.06 1"
RENK_HALI = "0.55 0.25 0.25 1"
RENK_ESIK = "0.6 0.45 0.3 1"


def _g(x):
    return "%.6g" % x


def kutu(ad, x0, x1, y0, y1, z0, z1, renk=None, koyu=False):
    return dict(ad=ad, pos=[(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2], size=[(x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2],
                quat=[1.0, 0.0, 0.0, 0.0], renk=renk, koyu=koyu)


def _guvenlik():
    # robot düşerse sonsuza dek düşmesin: 8 m aşağıda yakalama zemini (sensör menzili 4 m: görünmez)
    return kutu("zemin_guvenlik", -10, 40, -10, 40, -8.1, -8.0)


def merdiven(R=0.17, T=0.30, n=6, ad=None):
    """Aşağı inen düz merdiven: üst sahanlık x <= E; basamak i (0..n-1) x [E + iT, E + (i+1)T], yüzü z = -(i+1)R.
    Son basamak alt zemin olarak x_max'a dek uzar. Basamak burnu (çıkıntı) yok."""
    alt = -(n + 1) * R - 0.1
    K = [kutu("zemin_duz", X_MIN, E, Y_MIN, Y_MAX, alt, 0.0)]
    for i in range(n):
        x1 = E + (i + 1) * T if i < n - 1 else X_MAX
        K.append(kutu("zemin_basamak_%d" % i, E + i * T, x1, Y_MIN, Y_MAX, alt, -(i + 1) * R, renk=RENK_BASAMAK))
    K.append(_guvenlik())
    return dict(ad=ad or "merdiven_%dx%d" % (round(R * 100), round(T * 100)), tur="ucurum", kutular=K,
                kenarlar=[[1.0, 0.0, E]], geometri=dict(tur="merdiven", R=R, T=T, n=n))


def bosluk(D=3.0, ad=None):
    """Dik boşluk (sahanlık kenarı / merdiven boşluğu): x > E'de zemin D m aşağıda. D > 4 m ise sensör menzili dışı."""
    K = [kutu("zemin_duz", X_MIN, E, Y_MIN, Y_MAX, -0.3, 0.0)]
    if D < 7.5:
        K.append(kutu("zemin_alt", E, X_MAX, Y_MIN, Y_MAX, -D - 0.1, -D, renk=RENK_BASAMAK))
    K.append(_guvenlik())
    return dict(ad=ad or ("bosluk_%gm" % D if D < 7.5 else "kuyu"), tur="ucurum", kutular=K, kenarlar=[[1.0, 0.0, E]],
                geometri=dict(tur="bosluk", D=D))


def kose(D=3.0, ad="kose"):
    """Sahanlık köşesi: üst zemin yalnız x <= E ve y <= Y0 çeyreği; iki kenar 90 derece dış köşede birleşir."""
    K = [kutu("zemin_duz", X_MIN, E, Y_MIN, Y0, -0.3, 0.0),
         kutu("zemin_alt", X_MIN, X_MAX, Y_MIN, Y_MAX, -D - 0.1, -D, renk=RENK_BASAMAK), _guvenlik()]
    # alt kutu üst zeminin altında da var (görünmez; üst zemin onu örter)
    return dict(ad=ad, tur="ucurum", kutular=K, kenarlar=[[1.0, 0.0, E], [0.0, 1.0, Y0]], geometri=dict(tur="kose", D=D))


ACIK_L = 2.0      # dar açıklığın x boyu (m)


def acik(w, D=3.0, L=ACIK_L, R=None, T=None, ad=None):
    """Robottan dar, aşağı inen açıklık (merdiven boşluğu, döşeme kapağı): zeminde x [E, E + L], y [Y0 - w/2, Y0 + w/2]
    dikdörtgen delik; iki yanında ve ilerisinde zemin. Yan zemin kutuları açıklığın dibine dek iner (boşluğun duvarı).
    R, T verilirse açıklığın içinde aşağı inen merdiven (dar merdiven), yoksa D m derin dik boşluk.
    Hakem kenarı: ["dik", x0, x1, y0, y1] (dikdörtgen delik; pay = deliğe işaretli uzaklık)."""
    y0, y1 = Y0 - w / 2, Y0 + w / 2
    if R is not None:
        n = max(1, int(round(L / T)))
        dip = -(n + 1) * R - 0.1
    else:
        dip = -D - 0.1
    K = [kutu("zemin_duz", X_MIN, E, Y_MIN, Y_MAX, dip, 0.0),
         kutu("zemin_yan_a", E, E + L, Y_MIN, y0, dip, 0.0),
         kutu("zemin_yan_b", E, E + L, y1, Y_MAX, dip, 0.0),
         kutu("zemin_ileri", E + L, X_MAX, Y_MIN, Y_MAX, dip, 0.0)]
    if R is not None:
        for i in range(n):
            x1 = E + (i + 1) * T if i < n - 1 else E + L
            K.append(kutu("zemin_basamak_%d" % i, E + i * T, x1, y0, y1, dip, -(i + 1) * R, renk=RENK_BASAMAK))
        geo = dict(tur="dar_merdiven", w=w, R=R, T=T, n=n, L=L)
    else:
        K.append(kutu("zemin_alt", E, E + L, y0, y1, -D - 0.1, -D, renk=RENK_BASAMAK))
        geo = dict(tur="acik", w=w, D=D, L=L)
    K.append(_guvenlik())
    return dict(ad=ad or "acik_%d" % round(w * 100), tur="ucurum", kutular=K, kenarlar=[["dik", E, E + L, y0, y1]],
                yaklasma=[1.0, 0.0, E], geometri=geo)


def iskele(w=0.90, D=3.0, ad=None):
    """Tamamlama turu, yeni geometri (hüküm): w genişliğinde iskele / köprü şeridi; zemin yalnız x <= E ve
    |y - Y0| <= w/2, iki yanında ve ucunda D m düşüş. Hakem kenarı: uç + iki yan."""
    y0, y1 = Y0 - w / 2, Y0 + w / 2
    K = [kutu("zemin_duz", X_MIN, E, y0, y1, -0.3, 0.0),
         kutu("zemin_alt", X_MIN - 2, X_MAX, Y_MIN, Y_MAX, -D - 0.1, -D, renk=RENK_BASAMAK), _guvenlik()]
    return dict(ad=ad or "iskele_%d" % round(w * 100), tur="ucurum", kutular=K,
                kenarlar=[[1.0, 0.0, E], [0.0, 1.0, y1], [0.0, -1.0, -y0]], yaklasma=[1.0, 0.0, E],
                geometri=dict(tur="iskele", w=w, D=D))


def merdiven_burun(R=0.18, T=0.28, n=6, burun=0.03, ad=None):
    """Tamamlama turu, yeni geometri (hüküm): basamak burunlu (3 cm çıkıntı, 2 cm kalınlık) aşağı inen merdiven.
    Hakem kenarı burnun ucu (x = E + burun)."""
    s = merdiven(R, T, n)
    K = [k for k in s["kutular"] if k["ad"] != "zemin_guvenlik"]
    K.append(kutu("zemin_burun_ust", E, E + burun, Y_MIN, Y_MAX, -0.02, 0.0))
    for i in range(n - 1):
        x = E + (i + 1) * T
        K.append(kutu("zemin_burun_%d" % i, x, x + burun, Y_MIN, Y_MAX, -(i + 1) * R - 0.02, -(i + 1) * R, renk=RENK_BASAMAK))
    K.append(_guvenlik())
    return dict(ad=ad or "merdiven_burun_%dx%d" % (round(R * 100), round(T * 100)), tur="ucurum", kutular=K,
                kenarlar=[[1.0, 0.0, E + burun]], geometri=dict(tur="merdiven_burun", R=R, T=T, n=n, burun=burun))


def rampa_ucurum(egim_derece=10.0, L=2.0, D=3.0, ad=None):
    """Tamamlama turu (ölçüm sahnesi, inişte durma): x = E'den L m aşağı inen rampa, rampanın ucunda D m dik düşüş
    (yükleme rampası ucu). Hakem kenarı rampa ucu x = E + L; z düşüşü ölçütü bu sahnede kapalı (robot rampadan iner)."""
    th = math.radians(egim_derece)
    H = L * math.tan(th)
    Ls = L / math.cos(th)
    k = 0.05
    cx, cz = E + L / 2 - math.sin(th) * k / 2, -H / 2 - math.cos(th) * k / 2
    K = [kutu("zemin_duz", 0.0, E, 0.0, 30.0, -0.3, 0.0),
         dict(ad="zemin_rampa", pos=[cx, Y0, cz], size=[Ls / 2, 10.0, k / 2],
              quat=[math.cos(th / 2), 0.0, math.sin(th / 2), 0.0], renk=RENK_BASAMAK, koyu=False),
         kutu("zemin_alt", E + L, 30.0, 0.0, 30.0, -H - D - 0.1, -H - D), _guvenlik()]
    return dict(ad=ad or "rampa_%d_ucurum" % round(egim_derece), tur="ucurum", kutular=K, kenarlar=[[1.0, 0.0, E + L]],
                z_dusus_yok=True, geometri=dict(tur="rampa_ucurum", egim=egim_derece, L=L, H=H, D=D))


def duz(ad="duz"):
    K = [kutu("zemin_duz", 0.0, 30.0, 0.0, 30.0, -0.3, 0.0), _guvenlik()]
    return dict(ad=ad, tur="denetim", kutular=K, kenarlar=[], geometri=dict(tur="duz"))


def esik(h=0.02, d=0.05, ad=None):
    """Kapı eşiği: x [E, E + d], yükseklik h (yukarı çıkıntı)."""
    K = [kutu("zemin_duz", 0.0, 30.0, 0.0, 30.0, -0.3, 0.0),
         kutu("zemin_esik", E, E + d, Y_MIN, Y_MAX, -0.001, h, renk=RENK_ESIK), _guvenlik()]
    return dict(ad=ad or "esik_%dmm" % round(h * 1000), tur="denetim", kutular=K, kenarlar=[], geometri=dict(tur="esik", h=h, d=d))


def derz(genislik=0.008, derinlik=0.005, adim=0.6, n=5, ad="derz"):
    """Fayans derzi: x = E + k adim (k = 0..n-1) çizgilerinde genişlik x derinlik oluk."""
    K = []
    x = 0.0
    for k in range(n):
        xc = E + k * adim
        K.append(kutu("zemin_duz" if k == 0 else "zemin_parca_%d" % k, x, xc - genislik / 2, 0.0, 30.0, -0.3, 0.0))
        K.append(kutu("zemin_derz_%d" % k, xc - genislik / 2, xc + genislik / 2, 0.0, 30.0, -0.3, -derinlik))
        x = xc + genislik / 2
    K.append(kutu("zemin_parca_son", x, 30.0, 0.0, 30.0, -0.3, 0.0))
    K.append(_guvenlik())
    return dict(ad=ad, tur="denetim", kutular=K, kenarlar=[], geometri=dict(tur="derz", genislik=genislik, derinlik=derinlik, n=n))


def koyu_serit(genislik=0.10, adim=0.6, n=3, ad="koyu_serit"):
    """Zemin düzleminde koyu şerit (bant / koyu fayans): geometri düz, yalnız optik (sensör modelinde koyu yüzey)."""
    K = []
    x = 0.0
    for k in range(n):
        xc = E + k * adim
        K.append(kutu("zemin_duz" if k == 0 else "zemin_parca_%d" % k, x, xc, 0.0, 30.0, -0.3, 0.0))
        K.append(kutu("zemin_koyu_%d" % k, xc, xc + genislik, 0.0, 30.0, -0.3, 0.0, renk=RENK_KOYU, koyu=True))
        x = xc + genislik
    K.append(kutu("zemin_parca_son", x, 30.0, 0.0, 30.0, -0.3, 0.0))
    K.append(_guvenlik())
    return dict(ad=ad, tur="denetim", kutular=K, kenarlar=[], geometri=dict(tur="koyu_serit", genislik=genislik, n=n))


def rampa_inis(egim_derece=10.0, L=1.5, ad=None):
    """x = E'den başlayan aşağı inen rampa (L m yatay), sonra alt zemin."""
    th = math.radians(egim_derece)
    H = L * math.tan(th)
    Ls = L / math.cos(th)
    k = 0.05
    K = [kutu("zemin_duz", 0.0, E, 0.0, 30.0, -0.3, 0.0)]
    # üst yüz (E, 0) -> (E + L, -H); normal (sin, 0, cos); levha merkezi = üst yüz ortası - normal k/2
    cx, cz = E + L / 2 - math.sin(th) * k / 2, -H / 2 - math.cos(th) * k / 2
    K.append(dict(ad="zemin_rampa", pos=[cx, Y0, cz], size=[Ls / 2, 10.0, k / 2],
                  quat=[math.cos(th / 2), 0.0, math.sin(th / 2), 0.0], renk=RENK_BASAMAK, koyu=False))
    K.append(kutu("zemin_alt", E + L, 30.0, 0.0, 30.0, -H - 0.3, -H))
    K.append(_guvenlik())
    return dict(ad=ad or "rampa_%d_inis" % round(egim_derece), tur="denetim", kutular=K, kenarlar=[],
                geometri=dict(tur="rampa", egim=egim_derece, L=L, H=H))


def hali(h=0.010, ad=None):
    """Halı: x <= E'de h kalınlığında; robot halının üstünden başlayıp kenarından iner."""
    K = [kutu("zemin_duz", 0.0, 30.0, 0.0, 30.0, -0.3, 0.0),
         kutu("zemin_hali", 0.0, E, 0.0, 30.0, -0.001, h, renk=RENK_HALI), _guvenlik()]
    return dict(ad=ad or "hali_%dmm" % round(h * 1000), tur="denetim", kutular=K, kenarlar=[], geometri=dict(tur="hali", h=h),
                taban_z=h)


SAHNELER = {
    # geliştirme (ayar) geometrileri
    "merdiven_17x30": lambda: merdiven(0.17, 0.30, 6),
    "bosluk_3m": lambda: bosluk(3.0),
    # sınama (hüküm) geometrileri: geliştirmede hiç kullanılmadı
    "merdiven_15x28": lambda: merdiven(0.15, 0.28, 6),
    "merdiven_19x25": lambda: merdiven(0.19, 0.25, 6),
    "kuyu": lambda: bosluk(99.0),
    "kose": lambda: kose(3.0),
    # robottan dar açıklık (bağımsız denetimden sonra eklendi). Geliştirme genişlikleri:
    "acik_40": lambda: acik(0.40),
    "acik_50": lambda: acik(0.50),
    "acik_60": lambda: acik(0.60),
    "acik_70": lambda: acik(0.70),
    "acik_80": lambda: acik(0.80),
    "acik_100": lambda: acik(1.00),
    # sınama genişlikleri / türleri (geliştirmede hiç koşulmadı)
    "acik_45": lambda: acik(0.45),
    "acik_55": lambda: acik(0.55),
    "acik_65": lambda: acik(0.65),
    "acik_75": lambda: acik(0.75),
    "acik_90": lambda: acik(0.90),
    "acik_60_sig": lambda: acik(0.60, D=0.40),
    "dar_merdiven_60": lambda: acik(0.60, R=0.18, T=0.27),
    "dar_merdiven_80": lambda: acik(0.80, R=0.18, T=0.27),
    # denetim (yanlış alarm)
    "duz": duz,
    "esik_20mm": lambda: esik(0.02),
    "derz": derz,
    "koyu_serit": koyu_serit,
    "rampa_10_inis": lambda: rampa_inis(10.0),
    "hali_10mm": lambda: hali(0.010),
    "hali_5mm": lambda: hali(0.005),
    # yanlış alarm sınaması için yeni sahneler (geliştirmede / eşik seçiminde hiç koşulmadı)
    "esik_25mm": lambda: esik(0.025, 0.04),
    "derz_genis": lambda: derz(0.012, 0.008, 0.45, 6),
    "koyu_genis": lambda: koyu_serit(0.30, 0.9, 2),
    "rampa_8_inis": lambda: rampa_inis(8.0, 1.8),
    "hali_15mm": lambda: hali(0.015),
    # tamamlama turu: ölçüm sahneleri (inişte fren / tutma) ve yeni hüküm geometrileri
    "rampa_10_uzun": lambda: rampa_inis(10.0, 4.0),
    "rampa_10_ucurum": lambda: rampa_ucurum(10.0, 2.0),
    "rampa_8_ucurum": lambda: rampa_ucurum(8.0, 2.5),          # yalnız hüküm (t_hukum)
    "iskele_90": lambda: iskele(0.90),
    "merdiven_burun_18x28": lambda: merdiven_burun(0.18, 0.28),
    "basamak_12": lambda: bosluk(0.12, ad="basamak_12"),
}
# tamamlama turu, görev 1: 0,40 m'den dar delikler. kare_<cm>: w x w kare delik (3 m derin); yarik_<cm>: w genişliğinde
# (y), 1,0 m boyunda (x, gidiş yönünde) yarık. Delik orta hatta (y = Y0); robotun deliğe göre yeri senaryonun yanal kaymasıdır.
KARE_GEL = (4, 6, 8, 10, 12, 15, 20, 25, 30, 35)       # geliştirme / tehlike taraması
KARE_SIN = (14, 17, 22, 28)                            # hüküm (geliştirmede hiç koşulmadı)
for _c in sorted(set(KARE_GEL + KARE_SIN)):
    SAHNELER["kare_%d" % _c] = (lambda w: (lambda: acik(w, L=w, ad="kare_%d" % round(w * 100))))(_c / 100.0)
    SAHNELER["yarik_%d" % _c] = (lambda w: (lambda: acik(w, L=1.0, ad="yarik_%d" % round(w * 100))))(_c / 100.0)
# yarık boyu taraması (tehlike: aynı yandaki iki teker aynı anda boşlukta mı; dingil aralığı 0,37 m)
for _c in (8, 10, 15, 20):
    for _l in (20, 30, 40, 50, 70):
        SAHNELER["yarik_%dx%d" % (_c, _l)] = (lambda w, L: (lambda: acik(w, L=L, ad="yarik_%dx%d" % (round(w * 100), round(L * 100)))))(
            _c / 100.0, _l / 100.0)
# tamamlama 2: hükümde 8-12 cm yarık (bağımsız inceleme: ilk hükümde yoktu). Bu genişlikler hiçbir ayar koşusunda yok.
KARE_SIN2 = (9, 11, 13)
for _c in KARE_SIN2:
    SAHNELER["yarik_%d" % _c] = (lambda w: (lambda: acik(w, L=1.0, ad="yarik_%d" % round(w * 100))))(_c / 100.0)
DENETIM_GELISTIRME =("duz", "esik_20mm", "derz", "koyu_serit", "rampa_10_inis", "hali_10mm", "hali_5mm")
DENETIM_SINAMA_YENI = ("esik_25mm", "derz_genis", "koyu_genis", "rampa_8_inis", "hali_15mm")


def al(ad):
    s = SAHNELER[ad]()
    s["ad"] = ad
    return s


def sahne_sozlugu(ad, baslangic=None):
    """dunya / FizikEsp32 / gorunum3b'nin beklediği sahne sözlüğü (harita adı + ucurum alanı)."""
    u = al(ad)
    b = baslangic or (E - 1.5, Y0, 0.0)
    return {"ad": ad, "aciklama": "ucurum sahnesi %s (kod/fizik/ucurum/sahne.py)" % ad, "harita": HARITA,
            "baslangic": {"x": b[0], "y": b[1], "aci_derece": math.degrees(b[2])}, "ucurum": u}


def geom_xml(u):
    s = []
    for k in u["kutular"]:
        renk = ('rgba="%s"' % k["renk"]) if k.get("renk") else 'material="m_zemin"'
        s.append('<geom name="%s" type="box" pos="%s" size="%s" quat="%s" %s contype="1" conaffinity="2" group="0" '
                 'friction="0 0 0"/>' % (k["ad"], " ".join(map(_g, k["pos"])), " ".join(map(_g, k["size"])),
                                          " ".join(map(_g, k["quat"])), renk))
    return "\n    ".join(s)


_DUZLEM = re.compile(r'<geom name="zemin_duz" type="plane"[^>]*/>')
_KURULDU = {"evet": False}


def kur():
    """dunya.sahne_xml'i bu süreçte sarmala (idempotent). `ucurum` alanı olmayan sahnelerde çıktı aynıdır."""
    import dunya as D
    if _KURULDU["evet"]:
        return
    asil = D.sahne_xml

    def sahne_xml(harita=None, sahne=None, p=None):
        s = asil(harita, sahne, p)
        u = (sahne or {}).get("ucurum")
        if not u:
            return s
        yeni, n = _DUZLEM.subn(geom_xml(u), s, count=1)
        if n != 1:
            raise RuntimeError("zemin_duz düzlem satırı bulunamadı (dunya.sahne_xml değişmiş olabilir)")
        return yeni

    sahne_xml.asil = asil
    D.sahne_xml = sahne_xml
    _KURULDU["evet"] = True


def pay(kenarlar, x, y):
    """Hakem: (x, y) noktasının kenara payı (m), pozitif = güvenli taraf; kenar yoksa +inf.
    Kenar [nx, ny, c] yarı düzlem ya da ["dik", x0, x1, y0, y1] dikdörtgen delik (içeride negatif: en yakın kenara
    uzaklığın eksisi; dışarıda deliğe Öklid uzaklığı)."""
    if not kenarlar:
        return math.inf
    out = math.inf
    for k in kenarlar:
        if k[0] == "dik":
            _, x0, x1, y0, y1 = k
            if x0 <= x <= x1 and y0 <= y <= y1:
                p = -min(x - x0, x1 - x, y - y0, y1 - y)
            else:
                p = math.hypot(max(x0 - x, 0.0, x - x1), max(y0 - y, 0.0, y - y1))
        else:
            nx, ny, c = k
            p = c - (nx * x + ny * y)
        out = min(out, p)
    return out
