"""Uçurum deneylerinin koşucusu (aşamalar, kaldığı yerden sürer, en çok 2 süreç).

    %V% kod\\fizik\\ucurum\\deney.py durma        # 3: durma mesafesi + 5: devrilme (düz / 10° iniş), fren kipleri
    %V% kod\\fizik\\ucurum\\deney.py denetim      # 1: yanlış alarm (gölge denetçilerle eşik x onay taraması)
    %V% kod\\fizik\\ucurum\\deney.py gelistirme   # 4: ana ızgara (geliştirme tohumları 1-3, geliştirme geometrileri)
    %V% kod\\fizik\\ucurum\\deney.py kusur        # 6: sensör kusurları + dönüşsüz örnek politikaları
    %V% kod\\fizik\\ucurum\\deney.py sinama       # 8: ilk seçim (SECIM_1), AYRI tohumlar (101+) ve yeni geometriler
    %V% kod\\fizik\\ucurum\\deney.py dar_gelistirme   # dar açıklık: aday yerleşimler, geliştirme tohumları
    %V% kod\\fizik\\ucurum\\deney.py sinama2      # secim.json ile sınama: ilk sınama + dar açıklık + yeni yanlış alarm
    seçenekler: --surec 3 (en çok 3), --sinir N (ilk N görev; deneme)

Ham sonuç sonuc/ham/<aşama>.jsonl (git dışı; satır başına bir koşu), tablo sonuc/<aşama>.csv (koşu başına bir satır),
gölge denetçiler sonuc/<aşama>_golge.csv (koşu x denetçi ayarı başına bir satır). Seçim (geliştirmeden sınamaya
geçen yerleşim / eşik / fren) `secim.json` (analiz sonrası elle yazılır, gerekçesi SONUC.md'de)."""

import csv
import json
import math
import os
import sys
import time

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_k] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucurum import _yol  # noqa: E402

BURASI = _yol.UCURUM
SECIM = os.path.join(BURASI, "secim.json")

# ------------------------------------------------------------------ ortak ızgara değerleri
HIZLAR = (0.10, 0.25, 0.39)
ACILAR = (0, 15, 30, 45, 60, 80)
YERLESIM_ADLARI = ("2K", "2I", "3KO", "4O")
YUKSEKLIKLER = (0.06, 0.12)
EGIMLER = (0, 15, 30)
GELISTIRME_TOHUM = (1, 2, 3)
SINAMA_TOHUM = tuple(range(101, 111))
GELISTIRME_GEO = ("merdiven_17x30", "bosluk_3m")
SINAMA_GEO = ("merdiven_15x28", "merdiven_19x25", "kuyu", "kose")
GOLGE_ESIK = (0.015, 0.02, 0.03, 0.04, 0.06, 0.08)
GOLGE_ONAY = (1, 2, 3)
ANA_ESIK, ANA_ONAY = 0.04, 2       # geliştirme ızgarasının etkin denetçisi (denetim aşamasından seçildi; SONUC.md)
SUREC_TAVAN = 3                    # aynı anda en çok bu kadar işçi süreci (işlemci sınırı)

# İlk seçim (dar açıklık düzeltmesinden önce). `kusur`, `sinama`, `sinama_y` bununla koşuldu; yeniden üretim için donduruldu
# (secim.json artık yeni seçimi taşır). `sinama` politika `ucurum` ile, `sinama_y` `yavasla` ile koşuldu.
SECIM_1 = {"yerlesim": {"ad": "2KD+2AD", "z": 0.12, "e": 30, "koni": 27.0}, "esik_m": 0.1, "onay": 3, "politika": "ucurum",
           "fren": "rampa", "fren_ivme": 2.0, "sensor_n": 4, "on_n": 2}
# İkinci seçim (dar açıklık düzeltmesi; `sinama2`, `sinama2_karsi` bununla koşuldu). Tamamlama turunda secim.json değişti
# (6OD+4AD); sınama 2'nin yeniden üretimi için donduruldu. Tamamlama aşamalarından t_aday_son ve t_hukum dışındakiler de
# bununla koşuldu (o an secim.json buydu).
SECIM_2 = {"yerlesim": {"ad": "4OD+2AD", "z": 0.12, "e": 30, "koni": 27.0}, "esik_m": 0.1, "onay": 3, "politika": "yavasla",
           "fren": "rampa", "fren_ivme": 2.0, "sensor_n": 6, "on_n": 4}
# dar açıklık (bağımsız denetimden sonra eklendi)
DAR_GEL_GEO = ("acik_40", "acik_50", "acik_60", "acik_70", "acik_80", "acik_100")
DAR_SIN_GEO = ("acik_45", "acik_55", "acik_65", "acik_75", "acik_90", "acik_60_sig", "dar_merdiven_60", "dar_merdiven_80")
DAR_GEL_YANAL = (-0.20, -0.10, 0.0, 0.10, 0.20)
DAR_SIN_YANAL = (-0.15, -0.05, 0.05, 0.15, 0.25)
DAR_ADAYLAR = ("2KD+2AD", "3KOD+2AD", "4OD+2AD")


def secim():
    with open(SECIM, encoding="utf-8") as f:
        return json.load(f)


def _ana(s, politika=None):
    a = dict(esik_m=s["esik_m"], onay=s["onay"], politika=politika or s["politika"], fren=s["fren"], fren_ivme=s["fren_ivme"])
    if s.get("kural"):                  # aday 3B: davranış kuralları (eski seçimlerde alan yok: görevler aynı)
        a["kural"] = dict(s["kural"])
    return a


def _sinama_temel(asama, ys, ana, tohumlar=SINAMA_TOHUM):
    """İlk sınamanın ızgarası (geniş kenar geometrileri + yedi denetim sahnesi)."""
    G = []
    for geo in SINAMA_GEO:
        for aci in (0, 10, 22, 37, 52, 68, 80, 85):
            for v in HIZLAR:
                for t in tohumlar:
                    sen = dict(tur="ileri", aci=aci, v=v)
                    if geo == "kose":
                        sen["yanal"] = [-0.9, -0.3]
                    G.append(dict(asama=asama, alt="ileri", sahne=geo, ys=ys, ayar=ana, senaryo=sen, tohum=t))
    for geo in ("merdiven_15x28", "merdiven_19x25"):
        for t in tohumlar[:5]:
            for aci in (0, 25, 50):
                for v in (0.10, 0.25):
                    G.append(dict(asama=asama, alt="geri", sahne=geo, ys=ys, ayar=ana, senaryo=dict(tur="geri", aci=aci, v=v), tohum=t))
            for d in (0.35, 0.45, 0.55):
                for w in (-1.0, 1.0):
                    G.append(dict(asama=asama, alt="donus", sahne=geo, ys=ys, ayar=ana, senaryo=dict(tur="donus", d=d, w=w), tohum=t))
            for w in (0.4, 0.8):
                G.append(dict(asama=asama, alt="yay", sahne=geo, ys=ys, ayar=ana,
                              senaryo=dict(tur="yay", aci=-50, d=0.9, v=0.25, w=w, t=12.0), tohum=t))
    G += _yanlis_alarm(asama, ys, ana, ("duz", "esik_20mm", "derz", "koyu_serit", "rampa_10_inis", "hali_10mm", "hali_5mm"),
                       tohumlar[:5])
    return G


def _yanlis_alarm(asama, ys, ana, sahneler, tohumlar, alt="yanlis_alarm"):
    G = []
    for sahne in sahneler:
        for v in HIZLAR:
            for aci in (0, 20, 40):
                for t in tohumlar:
                    G.append(dict(asama=asama, alt=alt, sahne=sahne, ys=ys, ayar=ana, etkin=True,
                                  senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.6), tohum=t))
    return G


def _dar(asama, ys, ana, geolar, yanallar, acilar, tohumlar, alt="dar"):
    """Dar açıklığa ileri yaklaşma: açıklığın orta hattına göre yanal kayma (± 2 cm tohumla oynar), açı yakın kenara göre."""
    G = []
    for geo in geolar:
        for aci in acilar:
            for o in yanallar:
                for v in HIZLAR:
                    for t in tohumlar:
                        G.append(dict(asama=asama, alt=alt, sahne=geo, ys=ys, ayar=ana, tohum=t,
                                      senaryo=dict(tur="ileri", aci=aci, v=v, yanal=[o - 0.02, o + 0.02], yanal_ad=o)))
    return G


def _ys(ad, z, e, koni=27.0):
    return dict(ad=ad, z=z, e=e, koni=koni)


def _ayar(**k):
    a = dict(esik_m=ANA_ESIK, onay=ANA_ONAY, politika="ucurum", fren="rampa", fren_ivme=2.0)
    a.update(k)
    return a


# ------------------------------------------------------------------ tamamlama turu (bağımsız incelemenin açık bıraktıkları)
# Ayar (geliştirme) koşuları tohum 1-3 ve geliştirme sahneleri; hüküm koşuları (`t_hukum`) tohum 201-205 (201-210 ayrılmıştı;
# 206-210 tamamlama 2 hükmünde, `t2_hukum`) ve yeni sahneler.
TAM_DELIK_YREL = (0.0, 0.10, 0.15, 0.19, 0.216, 0.25, 0.30)     # deliğin robota göre y'si (sol yarı; simetrik)
TAM_ADAYLAR = ("4OD+2AD", "4TD+2AD", "6OD+2AD")
# sensör zamanlaması (görev 5; VL53L1X veri sayfası DS12385 Rev 8, 3.5.1 / 3.5.2, Tablo 5, 17-19)
ZAMAN = {
    "taban": {},                                                              # ilk model: 50 Hz + 4 m (iyimser birleşim)
    "K20": dict(periyot_ms=20, butce_ms=20, menzil_m=1.30),                   # kısa kip, 20 ms (yalnız kısada), 1,3 m
    "U33": dict(periyot_ms=33, butce_ms=33, menzil_m=3.60),                   # uzun kip, en kısa bütçe 33 ms, 3,6 m (karanlık)
    "U33G": dict(periyot_ms=33, butce_ms=33, menzil_m=0.73),                  # uzun kip, güçlü ortam ışığı: 0,73 m
    "U50": dict(periyot_ms=50, butce_ms=50, menzil_m=3.60),
    "U100": dict(periyot_ms=100, butce_ms=100, menzil_m=3.60),                # uzun kip, tablo koşulu (TB 100 ms)
}
DUYAR = dict(ZAMAN, **{
    "g20": dict(gecikme_ms=20), "g50": dict(gecikme_ms=50),
    "mu05": dict(degis={"teker_zemin_surtunme": 0.5}),
    "montaj_kotu": dict(montaj="kotu"), "montaj_rasgele": dict(montaj="rasgele"),
    "yuk_ust5": dict(ek_kutle=(5.0, (0.10, 0.0, 0.90))),                      # +5 kg tepside (gövde merkezinin 10 cm önü, 0,9 m)
    "yuk_alt10": dict(ek_kutle=(10.0, (0.0, 0.0, 0.15))),                     # +10 kg altta (taşıma yükü)
    "gurultu10": dict(sigma_taban_m=0.010),                                   # veri sayfası menzil hatası ±20 mm ≈ 2σ
    "a15": dict(fren_ivme=1.5), "a10": dict(fren_ivme=1.0),
})


def _tam_g(asama, alt, sahne, ys, ana, sen, t, **k):
    g = dict(asama=asama, alt=alt, sahne=sahne, ys=ys, ayar=ana, senaryo=sen, tohum=t)
    g.update(k)
    return g


def _tam_secim(asama=None):
    """t_hukum / t_aday_son dışındaki tamamlama aşamaları SECIM_2 ile (koşuldukları anki seçim; yeniden üretim).
    t_hukum / t_hukum_karsi (ve t_hukum_fiz) tamamlama 2'de secim.json değişince SECIM_3 ile (donduruldu)."""
    s = SECIM_3 if asama in ("t_hukum", "t_hukum_karsi") else SECIM_2
    return s, s["yerlesim"], _ana(s)


# Üçüncü seçim (tamamlama turu; `t_hukum` bununla koşuldu). Tamamlama 2'de secim.json değişti; yeniden üretim için donduruldu.
SECIM_3 = {"yerlesim": {"ad": "6OD+4AD", "z": 0.12, "e": 30, "koni": 27.0}, "esik_m": 0.1, "onay": 3, "politika": "yavasla",
           "fren": "rampa", "fren_ivme": 2.0, "sensor_n": 10, "on_n": 6, "hiz_onerisi_m_s": 0.25,
           "hukum_kosul": {"periyot_ms": 20, "butce_ms": 20, "menzil_m": 1.3, "tutma": ["konum", 40.0, 100.0]}}

# ------------------------------------------------------------------ tamamlama 2 (bağımsız incelemenin engelleyicileri)
# Ayar koşuları (t2_yarik_gel, t2_donus_gel, t2_kusur, t2_duyar): tohum 1-3, geliştirme sahneleri. Hüküm (t2_hukum):
# tohum 206-210 (hiçbir koşuda kullanılmadı), sınama geometrileri + yeni yarık genişlikleri (9 / 11 / 13 cm) ve yeni y'ler.
# Geçme ölçütü hükümden ÖNCE yazıldı: uçurum koşularında hakem 0 düşme, yanlış alarm koşularında 0 durma.
T2_YARIK_ADAY = ("6OD+4AD", "6WD+4AD", "6WRD+4AD")
T2_YAN_ADAY = ("6WD+4AD", "6WD+4AD+2Y30", "6WD+4AD+2Y35")
T2_YARIK_Y_GEL = (0.0, 0.10, 0.15, 0.19, 0.205, 0.216, 0.23, 0.25, 0.27, 0.30)
T2_YARIK_Y_HUK = (0.035, 0.08, 0.13, 0.175, 0.21, 0.225, 0.24, 0.26, 0.285)
T2_DUYAR = ("K20", "U33", "U50", "U100", "g20", "g50", "mu05", "montaj_kotu", "montaj_rasgele", "yuk_ust5", "yuk_alt10",
            "gurultu10")


def _t2_kosul(temel, kad):
    """Duyarlılık koşulu: seçimin `hukum_kosul`'u üstüne DUYAR[kad]; zamanlama kipi temeldeki zamanlamanın yerine geçer."""
    ek = dict(DUYAR[kad])
    ks = dict(temel)
    if any(k in ek for k in ("periyot_ms", "butce_ms", "menzil_m")):
        for k in ("periyot_ms", "butce_ms", "menzil_m"):
            ks.pop(k, None)
    ks.update(ek)
    return ks


# ------------------------------------------------------------------ aday 3 (dondurma 3; iki zayıf sınıf: dar yarık, dar açıklık yanında dönüş)
# Ayar koşuları yalnız geliştirme tohumları 1-3 ve daha önce kullanılmış sahnelerle (t3_a_gel, t3_b_gel). Hüküm burada YOK
# (başka bir koşuda, yeni tohum ve sahneyle). Adaylar sonuc/dondurma_3.md'de donduruldu.
T3_A_ADAY = ("8WRD+4AD+2YR40", "8WRaD+4AD+2YR40", "8WLD+4AD+2YR40", "8WLaD+4AD+2YR40")
T3_B_KURAL = {
    "yok": None,
    "yay30": dict(donus_yay_r=0.30, donus_w_tavan=0.5, geri_tavan=0.15, supheli_esik_m=0.02, surunme_hiz=0.05, supheli_s=1.0),
    "yay50": dict(donus_yay_r=0.50, donus_w_tavan=0.5, geri_tavan=0.15, supheli_esik_m=0.02, surunme_hiz=0.05, supheli_s=1.0),
    # t3_b_gel'in ilk sonucundan sonra eklendi (yay30 / yay50 dönüş yönündeki iç tekerleri görmüyor): büyük yarıçap, hız ≈ 0,25
    "yay80": dict(donus_yay_r=0.80, donus_w_tavan=0.30, geri_tavan=0.15, supheli_esik_m=0.02, surunme_hiz=0.05, supheli_s=1.0),
    "yay100": dict(donus_yay_r=1.00, donus_w_tavan=0.25, geri_tavan=0.15, supheli_esik_m=0.02, surunme_hiz=0.05, supheli_s=1.0),
    # ikinci sonuçtan sonra eklendi (ileri yay, dönülen yandaki kenarı teğet geçiyor): GERİ yay (r < 0), arka sensörler önde
    "geri50": dict(donus_yay_r=-0.50, donus_w_tavan=0.5, geri_tavan=0.15, supheli_esik_m=0.02, surunme_hiz=0.05, supheli_s=1.0),
    "geri100": dict(donus_yay_r=-1.00, donus_w_tavan=0.25, geri_tavan=0.15, supheli_esik_m=0.02, surunme_hiz=0.05, supheli_s=1.0),
}
T3_YARIK_GEN = (9, 10, 11, 12, 13, 15)
T3_YARIK_Y = tuple(round(0.025 * i, 3) for i in range(13))        # 0 .. 0,30


# DONDURMA 3 (sonuc/dondurma_3.md; t3_a_gel / t3_b_gel ayarından sonra, hükümden ÖNCE). Bu andan sonra değişmez.
# 3A (donanım): 14 sensörlü düzenin tek değişikliği iz çifti ±2 cm -> ±2,5 cm (y ±0,191 / ±0,241). Gerisi secim.json'la aynı.
SECIM_3A = {"yerlesim": {"ad": "8WRaD+4AD+2YR40", "z": 0.12, "e": 30, "koni": 27.0}, "esik_m": 0.1, "onay": 3,
            "politika": "yavasla", "fren": "rampa", "fren_ivme": 2.0, "sensor_n": 14, "on_n": 8, "hiz_onerisi_m_s": 0.25,
            "hukum_kosul": {"periyot_ms": 20, "butce_ms": 20, "menzil_m": 1.3, "tutma": ["konum", 40.0, 100.0]}}
# 3B (pratik): on sensör 6OD+4AD (SECIM_3 donanımı) + firmware davranış kuralları (denetci.KURAL_ALANLARI): yerinde dönüş
# r 1,0 m GERİ yaya çevrilir (|w| <= 0,25), geri hız tavanı 0,15 m/s, +20 mm şüpheli okumada 1 s 0,05 m/s sürünme.
SECIM_3B = {"yerlesim": {"ad": "6OD+4AD", "z": 0.12, "e": 30, "koni": 27.0}, "esik_m": 0.1, "onay": 3, "politika": "yavasla",
            "fren": "rampa", "fren_ivme": 2.0, "sensor_n": 10, "on_n": 6, "hiz_onerisi_m_s": 0.25,
            "hukum_kosul": {"periyot_ms": 20, "butce_ms": 20, "menzil_m": 1.3, "tutma": ["konum", 40.0, 100.0]},
            "kural": {"donus_yay_r": -1.00, "donus_w_tavan": 0.25, "geri_tavan": 0.15, "supheli_esik_m": 0.02,
                      "surunme_hiz": 0.05, "supheli_s": 1.0}}


def _t3_ortak(asama, ys, ana, ks, kad, yarik_y, yarik_aci, yarik_t, donus_t):
    """Aday 3 ayar ızgarası (bir aday için): dar yarık, dar açıklık yanında dönüş, geri (dar), ileri (dar / geniş), geniş
    kenar dönüşü, yanlış alarm (geliştirme + daha önce kullanılmış yanlış alarm sahneleri)."""
    from ucurum import sahne as SH
    G = []
    for c in T3_YARIK_GEN:
        for yr in yarik_y:
            for aci in yarik_aci:
                for v in (0.25, 0.39):
                    for t in yarik_t:
                        G.append(_tam_g(asama, "yarik", "yarik_%d" % c, ys, ana, dict(tur="ileri", aci=aci, v=v,
                                        yanal=[-yr - 0.01, -yr + 0.01], yanal_ad=yr), t, kosul=ks, kad=kad))
    for geo in ("acik_40", "acik_50", "acik_60", "acik_80", "acik_100"):
        for d in (0.35, 0.40, 0.45, 0.50):
            for w in (-1.0, 1.0):
                for o in (-0.3, 0.0, 0.3):
                    for t in donus_t:
                        G.append(_tam_g(asama, "donus_dar", geo, ys, ana, dict(tur="donus", d=d, w=w, yanal=[o - 0.02, o + 0.02],
                                        yanal_ad=o), t, kosul=ks, kad=kad))
    for geo in ("acik_40", "acik_50", "acik_60"):
        for o in (-0.2, 0.0, 0.2):
            for aci in (0, 30):
                for t in (1, 2):
                    G.append(_tam_g(asama, "geri_dar", geo, ys, ana, dict(tur="geri", aci=aci, v=0.25, yanal=[o - 0.02, o + 0.02],
                                    yanal_ad=o), t, kosul=ks, kad=kad))
    G += [dict(g, alt="dar", kosul=ks, kad=kad) for g in _dar(asama, ys, ana, ("acik_40", "acik_50"), DAR_GEL_YANAL, (0, 20), (1,))]
    for geo in GELISTIRME_GEO:
        for aci in (0, 30, 60):
            for v in HIZLAR:
                G.append(_tam_g(asama, "ileri", geo, ys, ana, dict(tur="ileri", aci=aci, v=v), 1, kosul=ks, kad=kad))
        for aci in (0, 30):
            G.append(_tam_g(asama, "geri", geo, ys, ana, dict(tur="geri", aci=aci, v=0.25), 1, kosul=ks, kad=kad))
    for d in (0.30, 0.35, 0.45):
        for w in (-1.0, 1.0):
            for t in (1, 2):
                G.append(_tam_g(asama, "donus_genis", "merdiven_17x30", ys, ana, dict(tur="donus", d=d, w=w), t, kosul=ks, kad=kad))
    for sh in SH.DENETIM_GELISTIRME + SH.DENETIM_SINAMA_YENI:
        for v in (0.25, 0.39):
            for aci in (0, 30, 45):
                G.append(dict(asama=asama, alt="yanlis_alarm", sahne=sh, ys=ys, ayar=ana, etkin=True, tohum=1, kosul=ks, kad=kad,
                              senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.2)))
    return G


def _aday3(asama):
    s = secim()                                     # 14 sensörlü aday (t2_hukum'daki değerler; secim.json değişmez)
    ks = dict(s["hukum_kosul"])
    G = []
    if asama == "t3_a_gel":
        for ad in T3_A_ADAY:
            G += _t3_ortak(asama, dict(s["yerlesim"], ad=ad), _ana(s), ks, ad, T3_YARIK_Y, (-10, 0, 10, 15), (1, 2), (1,))
    elif asama == "t3_b_gel":
        s3 = SECIM_3                                # 10 sensör 6OD+4AD, donanım aynı; yalnız davranış kuralı değişir
        for kad, kural in T3_B_KURAL.items():
            ana = dict(_ana(s3), kural=kural) if kural else _ana(s3)
            G += _t3_ortak(asama, s3["yerlesim"], ana, dict(s3["hukum_kosul"]), kad, T3_YARIK_Y[::2], (0, 10), (1,), (1, 2))
    else:
        raise SystemExit("bilinmeyen aşama: %s" % asama)
    return G


def _tamamlama2(asama):
    G = []
    if asama in ("t2_yarik_gel", "t2_yarik_gel2", "t2_donus_gel", "t2_donus_gel2"):
        s = SECIM_3                                 # ayar: seçimin geri kalanı t_hukum'daki gibi
    else:
        s = secim()
    ys0, ana0 = s["yerlesim"], _ana(s)
    ks = dict(s["hukum_kosul"])
    if asama in ("t2_yarik_gel", "t2_yarik_gel2"):
        # t2_yarik_gel2: t2_yarik_gel'den sonra eklenen aday (çift iz sensörü), aynı ızgara
        for ad in (T2_YARIK_ADAY if asama == "t2_yarik_gel" else ("8WRD+4AD",)):
            ys = dict(ys0, ad=ad)
            for c in (8, 10, 12, 15, 20):
                for yr in T2_YARIK_Y_GEL:
                    for aci in (0, 15):
                        for v in (0.25, 0.39):
                            for t in (1, 2):
                                G.append(_tam_g(asama, "delik", "yarik_%d" % c, ys, ana0, dict(tur="ileri", aci=aci, v=v,
                                                yanal=[-yr - 0.01, -yr + 0.01], yanal_ad=yr), t, kosul=ks))
            G += [dict(g, alt="dar", kosul=ks) for g in _dar(asama, ys, ana0, ("acik_40", "acik_50"), DAR_GEL_YANAL, (0, 20), (1,))]
            for geo in GELISTIRME_GEO:
                for aci in (0, 30, 60):
                    for v in HIZLAR:
                        G.append(_tam_g(asama, "ileri", geo, ys, ana0, dict(tur="ileri", aci=aci, v=v), 1, kosul=ks))
    elif asama in ("t2_donus_gel", "t2_donus_gel2"):
        # t2_donus_gel2: t2_donus_gel'den sonra eklenen adaylar (çift iz sensörü + ROI 15° yan sensör, 37° / 40°; 2YK ışını tekere çarptığı için koşulmadı), aynı ızgara
        from ucurum import sahne as SH
        for ad in (T2_YAN_ADAY if asama == "t2_donus_gel" else ("8WRD+4AD+2YR37", "8WRD+4AD+2YR40")):
            ys = dict(ys0, ad=ad)
            for geo in ("acik_40", "acik_50", "acik_60", "acik_80", "acik_100"):
                for d in (0.35, 0.40, 0.45, 0.50):
                    for w in (-1.0, 1.0):
                        for o in (-0.3, 0.0, 0.3):
                            for t in (1, 2):
                                G.append(_tam_g(asama, "donus", geo, ys, ana0, dict(tur="donus", d=d, w=w, yanal=[o - 0.02, o + 0.02],
                                                yanal_ad=o), t, kosul=ks))
            for d in (0.30, 0.35, 0.45):
                for w in (-1.0, 1.0):
                    for t in (1, 2):
                        G.append(_tam_g(asama, "donus_genis", "merdiven_17x30", ys, ana0, dict(tur="donus", d=d, w=w), t, kosul=ks))
            for geo in GELISTIRME_GEO:
                for aci in (0, 30, 60):
                    for v in HIZLAR:
                        G.append(_tam_g(asama, "ileri", geo, ys, ana0, dict(tur="ileri", aci=aci, v=v), 1, kosul=ks))
            if "+2Y" in ad:
                for sh in SH.DENETIM_GELISTIRME:
                    for v in (0.25, 0.39):
                        for aci in (0, 30, 45):
                            for t in (1, 2):
                                G.append(dict(asama=asama, alt="yanlis_alarm", sahne=sh, ys=ys, ayar=ana0, etkin=True, tohum=t,
                                              kosul=ks, senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.2)))
    elif asama == "t2_kusur":
        # görev 3, seçilen düzenle: her sensör tek tek ölü (donmuş / hep dönüşsüz) + dönüşsüz örnek oranı; tohum 1
        n_on, n = s["on_n"], s["sensor_n"]
        n_arka = 4
        geo_l = ("merdiven_17x30", "bosluk_3m", "acik_50", "acik_70")
        for ariza in [None] + [{str(i): k} for i in range(n_on) for k in ("sabit", "yok")]:
            for geo in geo_l:
                for aci in (0, 30):
                    for v in (0.25, 0.39):
                        sen = dict(tur="ileri", aci=aci, v=v)
                        if geo.startswith("acik"):
                            sen.update(yanal=[-0.12, 0.12], yanal_ad=0.0)
                        G.append(_tam_g(asama, "olu_on", geo, ys0, ana0, sen, 1, ariza=ariza, kosul=ks))
            for geo in ("yarik_15",):
                for yr in (0.19, 0.23):
                    G.append(_tam_g(asama, "olu_on_yarik", geo, ys0, ana0, dict(tur="ileri", aci=0, v=0.25, yanal=[-yr - 0.01, -yr + 0.01],
                                    yanal_ad=yr), 1, ariza=ariza, kosul=ks))
        for ariza in [None] + [{str(i): k} for i in range(n_on, n_on + n_arka) for k in ("sabit", "yok")]:
            for geo in geo_l[:3]:
                for aci in (0, 30):
                    sen = dict(tur="geri", aci=aci, v=0.25)
                    if geo.startswith("acik"):
                        sen.update(yanal=[-0.12, 0.12], yanal_ad=0.0)
                    G.append(_tam_g(asama, "olu_arka", geo, ys0, ana0, sen, 1, ariza=ariza, kosul=ks))
        for ariza in [None] + [{str(i): k} for i in range(n_on + n_arka, n) for k in ("sabit", "yok")]:
            for d in (0.35, 0.40):
                for w in (-1.0, 1.0):
                    G.append(_tam_g(asama, "olu_yan", "acik_50", ys0, ana0, dict(tur="donus", d=d, w=w, yanal=[-0.02, 0.02], yanal_ad=0.0),
                                    1, ariza=ariza, kosul=ks))
        for yok in (0.0, 0.05, 0.20, 0.50):
            for geo in geo_l[:3] + ("duz",):
                for aci in (0, 30):
                    for v in (0.25, 0.39):
                        sen = dict(tur="ileri", aci=aci, v=v) if geo != "duz" else dict(tur="ileri", aci=aci, v=v, yol_m=4.0)
                        G.append(_tam_g(asama, "parlak", geo, ys0, ana0, sen, 1, yok=yok, kosul=ks))
    elif asama == "t2_duyar":
        # görev 5 + 6, seçilen düzenle: her tekil koşul seçimin hukum_kosul'u üstüne; tohum 1, geliştirme sahneleri
        for kad in T2_DUYAR:
            kk = _t2_kosul(ks, kad)
            for v in (0.25, 0.30, 0.39):
                for geo in GELISTIRME_GEO:
                    for aci in (0, 30, 60):
                        G.append(_tam_g(asama, "ileri", geo, ys0, ana0, dict(tur="ileri", aci=aci, v=v), 1, kosul=kk, kad=kad))
                for geo in ("acik_40", "acik_50", "acik_60"):
                    for o in (-0.2, 0.0, 0.2):
                        for aci in (0, 20):
                            G.append(_tam_g(asama, "dar", geo, ys0, ana0, dict(tur="ileri", aci=aci, v=v, yanal=[o - 0.02, o + 0.02],
                                            yanal_ad=o), 1, kosul=kk, kad=kad))
                for geo in ("yarik_10", "yarik_15"):
                    for yr in (0.19, 0.23):
                        G.append(_tam_g(asama, "delik", geo, ys0, ana0, dict(tur="ileri", aci=0, v=v, yanal=[-yr - 0.01, -yr + 0.01],
                                        yanal_ad=yr), 1, kosul=kk, kad=kad))
                if v <= 0.25:
                    G.append(_tam_g(asama, "geri", "merdiven_17x30", ys0, ana0, dict(tur="geri", aci=0, v=v), 1, kosul=kk, kad=kad))
                    for d in (0.30, 0.40):
                        for w in (-1.0, 1.0):
                            G.append(_tam_g(asama, "donus", "merdiven_17x30", ys0, ana0, dict(tur="donus", d=d, w=w), 1, kosul=kk, kad=kad))
                    for d in (0.35, 0.40):
                        for w in (-1.0, 1.0):
                            G.append(_tam_g(asama, "donus_dar", "acik_50", ys0, ana0, dict(tur="donus", d=d, w=w, yanal=[-0.02, 0.02],
                                            yanal_ad=0.0), 1, kosul=kk, kad=kad))
            for sh in ("duz", "rampa_10_inis", "esik_20mm", "koyu_serit"):
                for v in (0.25, 0.39):
                    for aci in (0, 30):
                        G.append(dict(asama=asama, alt="yanlis_alarm", sahne=sh, ys=ys0, ayar=ana0, etkin=True, tohum=1, kosul=kk,
                                      kad=kad, senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.2)))
    elif asama == "t2_hukum":
        G += _hukum2(asama, s, ys0, ana0)
    elif asama == "t2_hukum_fiz":
        # hükümden SONRA, yalnız rapor: t2_hukum'da hakemin düşme saydığı tek durumun (yarik_11, y 0,285) bütün görevleri
        # (2 açı x 3 hız x 2 tohum), koşu hakemden sonra da sürer; seçim değişmez
        for g in gorevler("t2_hukum"):
            if g["alt"] == "yeni_delik" and g["sahne"] == "yarik_11" and g["senaryo"]["yanal_ad"] == 0.285:
                G.append(dict(g, asama=asama, surdur=True, t_max=12.0 / g["senaryo"]["v"] * 0.25 + 6.0))
    else:
        raise SystemExit("bilinmeyen aşama: %s" % asama)
    return G


def _hukum2(asama, s, ys0, ana0):
    """Tamamlama 2 hükmü: secim.json (+ hukum_kosul), tohum 206-210 (hiç kullanılmadı). İlk hükmün ızgarası + incelemenin
    istediği en kötü durumlar: yerinde dönüş d 0,35 / 0,45 ve 8-13 cm yarık (yeni genişlik 9 / 11 / 13, yeni y'ler)."""
    from ucurum import sahne as SH
    ks = dict(s.get("hukum_kosul") or {})
    ana = dict(ana0)
    T = tuple(range(206, 211))
    G = []
    for g in _sinama_temel(asama, ys0, ana, T):
        g["kosul"] = ks
        G.append(g)
    for g in _dar(asama, ys0, ana, DAR_SIN_GEO, DAR_SIN_YANAL, (0, 10, 30), T[:3]):
        g["kosul"] = ks
        G.append(g)
    for g in _yanlis_alarm(asama, ys0, ana, SH.DENETIM_SINAMA_YENI, T, alt="yanlis_alarm_yeni"):
        g["kosul"] = ks
        G.append(g)
    for geo in ("merdiven_burun_18x28", "basamak_12"):
        for aci in (0, 10, 22, 37, 52, 68, 80):
            for v in HIZLAR:
                for t in T:
                    G.append(_tam_g(asama, "yeni_ileri", geo, ys0, ana, dict(tur="ileri", aci=aci, v=v), t, kosul=ks))
        for aci in (0, 25):
            for v in (0.10, 0.25):
                for t in T:
                    G.append(_tam_g(asama, "yeni_geri", geo, ys0, ana, dict(tur="geri", aci=aci, v=v), t, kosul=ks))
    for aci in (0, 4, 8):
        for o in (-0.12, 0.0, 0.12):
            for v in HIZLAR:
                for t in T:
                    G.append(_tam_g(asama, "yeni_iskele", "iskele_90", ys0, ana, dict(tur="ileri", aci=aci, v=v,
                                    yanal=[o - 0.02, o + 0.02], yanal_ad=o), t, kosul=ks))
    for c in SH.KARE_SIN2 + SH.KARE_SIN:
        for yr in T2_YARIK_Y_HUK + ((0.23,) if c == 14 else ()):     # 0,23: ilk hükmün düşen durumu (artık görülmüş)
            for aci in (0, 10):
                for v in HIZLAR:
                    for t in T[:2]:
                        G.append(_tam_g(asama, "yeni_delik", "yarik_%d" % c, ys0, ana, dict(tur="ileri", aci=aci, v=v,
                                        yanal=[-yr - 0.01, -yr + 0.01], yanal_ad=yr), t, kosul=ks))
    for geo in ("acik_45", "acik_55", "acik_65", "acik_75", "acik_90"):
        for o in (-0.15, 0.05, 0.15):
            for t in T[:3]:
                if geo in ("acik_45", "acik_55", "acik_75"):
                    for aci in (0, 10, 30):
                        G.append(_tam_g(asama, "yeni_geri_dar", geo, ys0, ana, dict(tur="geri", aci=aci, v=0.25,
                                        yanal=[o - 0.02, o + 0.02], yanal_ad=o), t, kosul=ks))
                for d in (0.35, 0.40, 0.45, 0.50):
                    for w in (-1.0, 1.0):
                        G.append(_tam_g(asama, "yeni_donus_dar", geo, ys0, ana, dict(tur="donus", d=d, w=w, yanal=[o - 0.02, o + 0.02],
                                        yanal_ad=o), t, kosul=ks))
    kb = dict(ks, gecikme_ms=20, montaj="kotu", degis={"teker_zemin_surtunme": 0.5}, ek_kutle=(10.0, (0.0, 0.0, 0.15)))
    for v in (0.25, 0.30):
        for geo in ("merdiven_15x28", "kuyu", "kose"):
            for aci in (0, 22, 37):
                for t in T[:3]:
                    sen = dict(tur="ileri", aci=aci, v=v)
                    if geo == "kose":
                        sen["yanal"] = [-0.9, -0.3]
                    G.append(_tam_g(asama, "kotu_birlesik", geo, ys0, ana, sen, t, kosul=kb))
        for geo in ("acik_45", "acik_60_sig", "dar_merdiven_60"):
            for o in (-0.15, 0.05, 0.25):
                for aci in (0, 10):
                    for t in T[:2]:
                        G.append(_tam_g(asama, "kotu_birlesik", geo, ys0, ana, dict(tur="ileri", aci=aci, v=v, yanal=[o - 0.02, o + 0.02],
                                        yanal_ad=o), t, kosul=kb))
        for geo in ("yarik_11", "yarik_14"):
            for yr in (0.21, 0.24):
                G.append(_tam_g(asama, "kotu_birlesik", geo, ys0, ana, dict(tur="ileri", aci=0, v=v, yanal=[-yr - 0.01, -yr + 0.01],
                                yanal_ad=yr), T[0], kosul=kb))
    for geo in ("acik_45", "acik_55"):
        for w in (-1.0, 1.0):
            for o in (-0.15, 0.15):
                G.append(_tam_g(asama, "kotu_birlesik", geo, ys0, ana, dict(tur="donus", d=0.35, w=w, yanal=[o - 0.02, o + 0.02],
                                yanal_ad=o), T[0], kosul=kb))
    for v in (0.10, 0.20, 0.25, 0.39):
        for aci in (0, 15):
            for t in T:
                G.append(_tam_g(asama, "yeni_rampa_ucurum", "rampa_8_ucurum", ys0, ana, dict(tur="ileri", aci=aci, v=v), t,
                                baslangic=(SH.E - 0.8, SH.Y0, math.radians(aci)), kosul=ks, t_max=3.8 / v + 8.0, durdu_bekle_s=3.0))
    return G


def _tamamlama(asama):
    G = []
    s, ys0, ana0 = _tam_secim(asama)
    from ucurum import sahne as SH
    if asama == "t_delik_tehlike":
        # görev 1a: hangi delik boyu tehlikeli? Denetçi KAPALI (etkin False), robot deliğin üstünden geçer; hakem ölçer.
        for tur in ("kare", "yarik"):
            for c in SH.KARE_GEL:
                for yr in (0.216, 0.0):
                    for v in (0.25, 0.39):
                        L = c / 100.0 if tur == "kare" else 1.0
                        G.append(_tam_g(asama, tur, "%s_%d" % (tur, c), ys0, ana0, dict(tur="ileri", aci=0, v=v,
                                        yanal=[-yr - 0.005, -yr + 0.005], yanal_ad=yr), 1, etkin=False, surdur=True,
                                        t_max=(1.2 + L + 0.8) / v))
    elif asama == "t_delik_boy":
        # görev 1a devamı: yarığın BOYU (gidiş yönünde) ne kadar olunca tehlikeli? Denetçi kapalı; tohum 1-3, açı 0 (±2° tohumla)
        for c in (8, 10, 15, 20):
            for l in (20, 30, 40, 50, 70):
                for v in (0.25, 0.39):
                    for aci in (0,):
                        for t in (1, 2, 3):
                            G.append(_tam_g(asama, "yarik_boy", "yarik_%dx%d" % (c, l), ys0, ana0, dict(tur="ileri", aci=aci, v=v,
                                            yanal=[-0.221, -0.211], yanal_ad=0.216), t, etkin=False, surdur=True,
                                            t_max=(1.2 + l / 100.0 + 0.8) / v))
    elif asama == "t_donus_w":
        # görev 2 devamı (geliştirme): dar açıklık yanında yerinde dönüş 1 rad/s'de düşüyor; dönüş hızı tavanı (firmware) adayı
        for geo in ("acik_40", "acik_50", "acik_60", "acik_80", "acik_100"):
            for d in (0.35, 0.40, 0.50):
                for w in (-0.5, 0.5, -0.7, 0.7):
                    for o in (-0.3, 0.0, 0.3):
                        for t in (1, 2):
                            G.append(_tam_g(asama, "donus", geo, dict(ys0, ad="4OD+4AD"), ana0,
                                            dict(tur="donus", d=d, w=w, yanal=[o - 0.02, o + 0.02], yanal_ad=o), t, t_max=12.0))
    elif asama == "t_aday_son":
        # seçim öncesi son geliştirme denetimi: 6OD+4AD (ön iz sensörleri + arka iç sensörler, 10 sensör), kısa kip K20 zamanlaması,
        # konum tutma. Dar açıklık yanında dönüş, yanlış alarm, yeni sensör arızası, ileri / dar hız taraması. Tohum 1-2.
        ys = dict(ys0, ad="6OD+4AD")
        ks = dict(ZAMAN["K20"], tutma=("konum", 40.0, 100.0))
        for geo in ("acik_40", "acik_50", "acik_60", "acik_80", "acik_100"):
            for d in (0.35, 0.40, 0.50):
                for w in (-1.0, 1.0):
                    for o in (-0.3, 0.0, 0.3):
                        for t in (1, 2):
                            G.append(_tam_g(asama, "donus", geo, ys, ana0, dict(tur="donus", d=d, w=w, yanal=[o - 0.02, o + 0.02],
                                            yanal_ad=o), t, kosul=ks))
        for sh in SH.DENETIM_GELISTIRME:
            for v in (0.25, 0.39):
                for aci in (0, 30, 45):
                    for t in (1, 2):
                        G.append(dict(asama=asama, alt="yanlis_alarm", sahne=sh, ys=ys, ayar=ana0, etkin=True, tohum=t, kosul=ks,
                                      senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.2)))
        for i in (1, 4):                                      # on_iz_sol, on_iz_sag
            for k in ("sabit", "yok"):
                for geo in ("acik_50", "yarik_15", "bosluk_3m"):
                    for v in (0.25, 0.39):
                        G.append(_tam_g(asama, "kusur", geo, ys, ana0, dict(tur="ileri", aci=0, v=v, yanal=[-0.02, 0.02], yanal_ad=0.0),
                                        1, ariza={str(i): k}, kosul=ks))
        for v in (0.25, 0.30, 0.39):
            for geo in GELISTIRME_GEO:
                for aci in (0, 30, 60):
                    G.append(_tam_g(asama, "ileri", geo, ys, ana0, dict(tur="ileri", aci=aci, v=v), 1, kosul=ks))
            for geo in ("acik_40", "acik_50", "acik_60"):
                for o in (-0.2, 0.0, 0.2):
                    for aci in (0, 20):
                        G.append(_tam_g(asama, "dar", geo, ys, ana0, dict(tur="ileri", aci=aci, v=v, yanal=[o - 0.02, o + 0.02],
                                        yanal_ad=o), 1, kosul=ks))
            for geo in ("yarik_10", "yarik_15", "yarik_20"):
                for yr in TAM_DELIK_YREL:
                    G.append(_tam_g(asama, "delik", geo, ys, ana0, dict(tur="ileri", aci=0, v=v, yanal=[-yr - 0.01, -yr + 0.01],
                                    yanal_ad=yr), 1, kosul=ks))
    elif asama == "t_hukum_fiz":
        # hükümden SONRA, yalnız rapor: hükümde hakemin düşme saydığı iki sahne türünün bütün görevleri (aynı tohum / sahne,
        # seçim değişmez), koşu hakemden sonra da sürer: gerçekten düşüyor mu
        for g in gorevler("t_hukum"):
            if (g["alt"] == "yeni_delik" and g["sahne"] == "yarik_14") or g["alt"] == "yeni_donus_dar":
                e = dict(g, asama=asama, surdur=True)
                if g["senaryo"].get("v"):
                    e["t_max"] = 12.0 / g["senaryo"]["v"] * 0.25 + 6.0
                G.append(e)
    elif asama == "t_delik_fiz":
        # t_delik_gel'in yarık görevleri, hakem "düştü" dese de koşu sürer (surdur): durdu mu, gerçekten devrildi / oturdu mu
        for g in gorevler("t_delik_gel"):
            if g["alt"] == "delik" and g["sahne"].startswith("yarik") and g["ys"]["ad"] in ("4OD+2AD", "6OD+2AD"):
                G.append(dict(g, asama=asama, surdur=True, t_max=12.0 / g["senaryo"]["v"] * 0.25 + 6.0))
    elif asama == "t_delik_gel":
        # görev 1b (geliştirme / aday seçimi): tehlikeli boylarda algılama ve durma; üç aday, tohum 1-2
        # kare delikler 0,35 m'ye dek fiziksel olarak tehlikesiz çıktı (t_delik_tehlike): yalnız en büyüğü + yarıklar
        sahneler = ["yarik_%d" % c for c in (10, 15, 20)] + ["kare_35"]
        for ad in TAM_ADAYLAR:
            ys = dict(ys0, ad=ad)
            for sh in sahneler:
                for yr in TAM_DELIK_YREL:
                    for aci in (0, 15):
                        for v in (0.25, 0.39):          # 0,10 atıldı (süre; en yavaş hız en kolay durum)
                            for t in (1, 2):
                                G.append(_tam_g(asama, "delik", sh, ys, ana0, dict(tur="ileri", aci=aci, v=v,
                                                yanal=[-yr - 0.01, -yr + 0.01], yanal_ad=yr), t))
            # robottan dar açıklık (seçimin gerekçesi bozulmasın: 0,40 / 0,50 m, dar_gelistirme yanalları)
            G += [dict(g, alt="dar") for g in _dar(asama, ys, ana0, ("acik_40", "acik_50"), DAR_GEL_YANAL, (0, 20), (1, 2))]
            # geniş kenar ileri (geliştirme sahneleri)
            for geo in GELISTIRME_GEO:
                for aci in (0, 30, 60):
                    for v in HIZLAR:
                        G.append(_tam_g(asama, "ileri", geo, ys, ana0, dict(tur="ileri", aci=aci, v=v), 1))
    elif asama == "t_yaklasma_gel":
        # görev 2 (geliştirme): açıklığa GERİ giderek ve kenarın yanında yerinde dönerek yaklaşma; arka iç sensör adayı
        for ad in ("4OD+2AD", "4OD+4AD"):
            ys = dict(ys0, ad=ad)
            for geo in ("acik_40", "acik_50", "acik_60", "acik_80", "acik_100", "merdiven_17x30", "bosluk_3m"):
                dar = geo.startswith("acik")
                for aci in (0, 30):
                    for v in (0.10, 0.25):
                        for o in (DAR_GEL_YANAL if dar else (None,)):
                            for t in (1, 2):
                                sen = dict(tur="geri", aci=aci, v=v)
                                if o is not None:
                                    sen.update(yanal=[o - 0.02, o + 0.02], yanal_ad=o)
                                G.append(_tam_g(asama, "geri", geo, ys, ana0, sen, t))
                for d in (0.40, 0.50):
                    for w in (-1.0, 1.0):
                        for o in ((-0.3, 0.0, 0.3) if dar else (None,)):
                            for t in (1, 2):
                                sen = dict(tur="donus", d=d, w=w)
                                if o is not None:
                                    sen.update(yanal=[o - 0.02, o + 0.02], yanal_ad=o)
                                G.append(_tam_g(asama, "donus", geo, ys, ana0, sen, t))
    elif asama == "t_kusur6":
        # görev 3: altı sensörün her biri tek tek ölü (donmuş / hep menzil dışı) + dönüşsüz örnek oranı; politika yavasla
        ys = ys0
        on = range(4)
        geo_l = ("merdiven_17x30", "bosluk_3m", "acik_50", "acik_70")
        for ariza in [None] + [{str(i): k} for i in on for k in ("sabit", "yok")]:
            for geo in geo_l:
                for aci in (0, 30):
                    for v in (0.25, 0.39):
                        for t in GELISTIRME_TOHUM[:2]:
                            sen = dict(tur="ileri", aci=aci, v=v)
                            if geo.startswith("acik"):
                                sen.update(yanal=[-0.12, 0.12], yanal_ad=0.0)
                            G.append(_tam_g(asama, "olu_on", geo, ys, ana0, sen, t, ariza=ariza))
        for ariza in [None] + [{str(i): k} for i in (4, 5) for k in ("sabit", "yok")]:
            for geo in geo_l[:3]:
                for aci in (0, 30):
                    for t in GELISTIRME_TOHUM[:2]:
                        sen = dict(tur="geri", aci=aci, v=0.25)
                        if geo.startswith("acik"):
                            sen.update(yanal=[-0.12, 0.12], yanal_ad=0.0)
                        G.append(_tam_g(asama, "olu_arka", geo, ys, ana0, sen, t, ariza=ariza))
        for yok in (0.0, 0.05, 0.20, 0.50):
            for geo in geo_l[:3] + ("duz",):
                for aci in (0, 30):
                    for v in (0.25, 0.39):
                        for t in GELISTIRME_TOHUM[:2]:
                            sen = dict(tur="ileri", aci=aci, v=v) if geo != "duz" else dict(tur="ileri", aci=aci, v=v, yol_m=4.0)
                            G.append(_tam_g(asama, "parlak", geo, ys, ana0, sen, t, yok=yok))
    elif asama == "t_rampa_fren":
        # görev 4a: 10° inişte (4 m rampa) ve düzde zorla tetik; fren ivmesi taraması; tutma freni yok / konum / mekanik
        for sahne in ("rampa_10_uzun", "duz"):
            for a in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
                for v in (0.10, 0.20, 0.25, 0.39):
                    for tut in ((None, ("konum", 40.0, 100.0), ("mekanik", 2.0)) if sahne != "duz" else (None,)):
                        for t in (1,):
                            G.append(dict(asama=asama, alt="fren", sahne=sahne, ys=_ys("2K", 0.06, 15), tohum=t, zorla=True,
                                          ayar=_ayar(esik_m=50.0, fren="rampa", fren_ivme=a), senaryo=dict(tur="ileri", aci=0, v=v),
                                          kosul=dict(tutma=tut) if tut else {}, t_max=(1.45 / v) + 7.0, durdu_bekle_s=6.0))
    elif asama == "t_rampa_ucurum":
        # görev 4b: 10° iniş rampasının ucunda 3 m düşüş; seçilen sensörlerle gerçek tetik. Fren ivmesi x tutma x hız.
        for a in (1.0, 1.5, 2.0):
            for tut in (None, ("konum", 40.0, 100.0)):
                for v in (0.10, 0.15, 0.20, 0.25, 0.39):
                    for aci in (0, 20):
                        for t in (1,):
                            G.append(_tam_g(asama, "rampa_ucurum", "rampa_10_ucurum", ys0, dict(ana0, fren_ivme=a),
                                            dict(tur="ileri", aci=aci, v=v), t, baslangic=(SH.E - 0.8, SH.Y0, math.radians(aci)),
                                            kosul=dict(tutma=tut) if tut else {}, t_max=3.6 / v + 8.0, durdu_bekle_s=3.0))
    elif asama == "t_duyar":
        # görev 5 + 6: zamanlama kipleri ve duyarlılık; geliştirme sahneleri, tohum 1-2, hız 0,25 / 0,30 / 0,39
        for kad, ks in DUYAR.items():
            ana = dict(ana0, fren_ivme=ks.get("fren_ivme", ana0["fren_ivme"]))
            ks = {k: v for k, v in ks.items() if k != "fren_ivme"}
            for v in (0.25, 0.30, 0.39):
                for t in (1,):                  # süre: tohum 1 (koşular tohum dışında deterministik; gürültü / faz tohumla)
                    for geo in GELISTIRME_GEO:
                        for aci in (0, 30, 60):
                            G.append(_tam_g(asama, "ileri", geo, ys0, ana, dict(tur="ileri", aci=aci, v=v), t, kosul=ks, kad=kad))
                    for geo in ("acik_40", "acik_50", "acik_60"):
                        for o in (-0.2, 0.0, 0.2):
                            for aci in (0, 20):
                                G.append(_tam_g(asama, "dar", geo, ys0, ana, dict(tur="ileri", aci=aci, v=v, yanal=[o - 0.02, o + 0.02],
                                                yanal_ad=o), t, kosul=ks, kad=kad))
                    if v <= 0.25:
                        G.append(_tam_g(asama, "geri", "merdiven_17x30", ys0, ana, dict(tur="geri", aci=0, v=v), t, kosul=ks, kad=kad))
                        for d in (0.30, 0.40):
                            for w in (-1.0, 1.0):
                                G.append(_tam_g(asama, "donus", "merdiven_17x30", ys0, ana, dict(tur="donus", d=d, w=w), t,
                                                kosul=ks, kad=kad))
            for sh in ("duz", "rampa_10_inis", "esik_20mm", "koyu_serit"):
                for v in (0.25, 0.39):
                    for aci in (0, 30):
                        G.append(dict(asama=asama, alt="yanlis_alarm", sahne=sh, ys=ys0, ayar=ana, etkin=True, tohum=1, kosul=ks,
                                      kad=kad, senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.2)))
    elif asama in ("t_hukum", "t_hukum_karsi"):
        G += _hukum(asama, s, ys0, ana0)
    else:
        raise SystemExit("bilinmeyen aşama: %s" % asama)
    return G


def _hukum(asama, s, ys0, ana0):
    """Görev 7: hüküm koşuları. Tohum aralığı 201-210 ayrıldı, KULLANILAN 201-205 (dar açıklık / yarık / geri-dönüş /
    kötü birleşim 201-203); seçim SECIM_3 (koşulduğu anki secim.json, + `hukum_kosul`: sensör zamanlaması, tutma); sınama
    geometrileri + yeni geometriler (iskele, burunlu merdiven, tek basamak, yeni boy dar delikler, 8° rampa ucu).
    Tamamlama 2 hükmü 206-210 ile `_hukum2`'de."""
    from ucurum import sahne as SH
    ks = dict(s.get("hukum_kosul") or {})
    ana = dict(ana0)
    T = tuple(range(201, 211))
    G = []
    if asama == "t_hukum_karsi":                     # yalnız rapor: zamanlama iyimser ilk modelle (karşılaştırma)
        ks = {k: v for k, v in ks.items() if k not in ("periyot_ms", "butce_ms", "menzil_m")}
    for g in _sinama_temel(asama, ys0, ana, T[:5]):     # süre: geniş kenar ızgarası tohum 201-205
        g["kosul"] = ks
        G.append(g)
    for g in _dar(asama, ys0, ana, DAR_SIN_GEO, DAR_SIN_YANAL, (0, 10, 30), T[:3]):
        g["kosul"] = ks
        G.append(g)
    for g in _yanlis_alarm(asama, ys0, ana, SH.DENETIM_SINAMA_YENI, T[:5], alt="yanlis_alarm_yeni"):
        g["kosul"] = ks
        G.append(g)
    # yeni geometriler
    for geo in ("merdiven_burun_18x28", "basamak_12"):
        for aci in (0, 10, 22, 37, 52, 68, 80):
            for v in HIZLAR:
                for t in T[:5]:
                    G.append(_tam_g(asama, "yeni_ileri", geo, ys0, ana, dict(tur="ileri", aci=aci, v=v), t, kosul=ks))
        for aci in (0, 25):
            for v in (0.10, 0.25):
                for t in T[:5]:
                    G.append(_tam_g(asama, "yeni_geri", geo, ys0, ana, dict(tur="geri", aci=aci, v=v), t, kosul=ks))
    for aci in (0, 4, 8):
        for o in (-0.12, 0.0, 0.12):
            for v in HIZLAR:
                for t in T[:5]:
                    G.append(_tam_g(asama, "yeni_iskele", "iskele_90", ys0, ana, dict(tur="ileri", aci=aci, v=v,
                                    yanal=[o - 0.02, o + 0.02], yanal_ad=o), t, kosul=ks))
    for c in SH.KARE_SIN:
        for tur in ("yarik",):                       # kare delik 0,35 m'ye dek fiziksel tehlikesiz (t_delik_tehlike)
            for yr in (0.05, 0.12, 0.17, 0.205, 0.23, 0.27):
                for aci in (0, 10):
                    for v in HIZLAR:
                        for t in T[:3]:
                            G.append(_tam_g(asama, "yeni_delik", "%s_%d" % (tur, c), ys0, ana, dict(tur="ileri", aci=aci, v=v,
                                            yanal=[-yr - 0.01, -yr + 0.01], yanal_ad=yr), t, kosul=ks))
    for geo in ("acik_45", "acik_55", "acik_75"):              # görev 2'nin hüküm kısmı: geri ve yerinde dönüş, sınama açıklıkları
        for o in (-0.15, 0.05, 0.15):
            for t in T[:3]:
                for aci in (0, 10, 30):
                    G.append(_tam_g(asama, "yeni_geri_dar", geo, ys0, ana, dict(tur="geri", aci=aci, v=0.25, yanal=[o - 0.02, o + 0.02],
                                    yanal_ad=o), t, kosul=ks))
                for d in (0.40, 0.50):
                    for w in (-1.0, 1.0):
                        G.append(_tam_g(asama, "yeni_donus_dar", geo, ys0, ana, dict(tur="donus", d=d, w=w, yanal=[o - 0.02, o + 0.02],
                                        yanal_ad=o), t, kosul=ks))
    # kötü durumların birleşimi (önerilen hız 0,25 ve bir üstü 0,30): +20 ms gecikme, en kötü montaj, µ 0,5, +10 kg yük
    kb = dict(ks, gecikme_ms=20, montaj="kotu", degis={"teker_zemin_surtunme": 0.5}, ek_kutle=(10.0, (0.0, 0.0, 0.15)))
    for v in (0.25, 0.30):
        for geo in ("merdiven_15x28", "kuyu", "kose"):
            for aci in (0, 22, 37):
                for t in T[:3]:
                    sen = dict(tur="ileri", aci=aci, v=v)
                    if geo == "kose":
                        sen["yanal"] = [-0.9, -0.3]
                    G.append(_tam_g(asama, "kotu_birlesik", geo, ys0, ana, sen, t, kosul=kb))
        for geo in ("acik_45", "acik_60_sig", "dar_merdiven_60"):
            for o in (-0.15, 0.05, 0.25):
                for aci in (0, 10):
                    for t in T[:2]:
                        G.append(_tam_g(asama, "kotu_birlesik", geo, ys0, ana, dict(tur="ileri", aci=aci, v=v, yanal=[o - 0.02, o + 0.02],
                                        yanal_ad=o), t, kosul=kb))
    for v in (0.10, 0.20, 0.25, 0.39):                       # 8° iniş rampasının ucunda düşüş (yeni)
        for aci in (0, 15):
            for t in T[:5]:
                G.append(_tam_g(asama, "yeni_rampa_ucurum", "rampa_8_ucurum", ys0, ana, dict(tur="ileri", aci=aci, v=v), t,
                                baslangic=(SH.E - 0.8, SH.Y0, math.radians(aci)), kosul=ks, t_max=3.8 / v + 8.0, durdu_bekle_s=3.0))
    return G


def gorevler(asama):
    G = []
    if asama == "durma":
        for sahne in ("duz", "rampa_10_inis"):
            for v in HIZLAR:
                kipler = [("kes", 0.0), ("fren", 0.0)] + [("rampa", a) for a in (1.0, 1.5, 1.8, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0)]
                for fren, a in kipler:
                    for t in (1, 2):
                        G.append(dict(asama=asama, sahne=sahne, ys=_ys("2K", 0.06, 15), ayar=_ayar(esik_m=50.0, fren=fren, fren_ivme=a or 1.8),
                                      senaryo=dict(tur="ileri", aci=0, v=v), tohum=t, zorla=True))
    elif asama == "denetim":
        sahneler = ("duz", "esik_20mm", "derz", "koyu_serit", "rampa_10_inis", "hali_10mm", "hali_5mm")
        golge = [dict(esik_m=e, onay=o) for e in GOLGE_ESIK for o in GOLGE_ONAY]
        for sahne in sahneler:
            for ad in ("2K", "3KO"):          # yanlış alarm yerleşimin y konumuna değil yükseklik / eğime bağlı: 2 düzen
                for z in YUKSEKLIKLER:
                    for e in EGIMLER:
                        for v in HIZLAR:
                            for aci in (0, 30):
                                for t in GELISTIRME_TOHUM[:2]:
                                    G.append(dict(asama=asama, sahne=sahne, ys=_ys(ad, z, e), ayar=_ayar(), etkin=False,
                                                  golge=golge, senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=1.8), tohum=t))
    elif asama == "rampa_ayrinti":
        # denetimde 10° iniş rampasına çapraz (30°) girişte yanlış alarm çıktı: açı ve yüksek eşiklerle ayrıntı
        golge = [dict(esik_m=e, onay=o) for e in (0.06, 0.08, 0.10, 0.12, 0.14) for o in (2, 3)]
        for ad in ("2K", "3KO"):
            for z in YUKSEKLIKLER:
                for e in EGIMLER:
                    for v in (0.25, 0.39):
                        for aci in (0, 15, 30, 45, 60):
                            G.append(dict(asama=asama, sahne="rampa_10_inis", ys=_ys(ad, z, e), ayar=_ayar(), etkin=False,
                                          golge=golge, senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.2), tohum=1))
    elif asama == "gelistirme2":
        # geliştirme 1'den sonra: ön köşe + arka köşe (geri için şart), köşeler düz ileri mi çapraz dışa mı (D), eşik 4 cm / 10 cm
        # (10 cm: rampaya çapraz girişte yanlış alarmı sıfırlayan en küçük eşik, rampa_ayrinti). Yalnız geliştirme sahneleri, tohum 1-2.
        for ad in ("2K+2A", "2KD+2AD"):
            for z in YUKSEKLIKLER:
                for e in (15, 30):
                    for es, on in ((0.04, 2), (0.10, 3)):
                        ay = _ayar(esik_m=es, onay=on)
                        for geo in GELISTIRME_GEO:
                            for aci in ACILAR:
                                for v in HIZLAR:
                                    G.append(dict(asama=asama, alt="ileri", sahne=geo, ys=_ys(ad, z, e), ayar=ay,
                                                  senaryo=dict(tur="ileri", aci=aci, v=v), tohum=1))
                        for aci in (0, 30, 60):
                            for v in (0.10, 0.25):
                                G.append(dict(asama=asama, alt="geri", sahne="merdiven_17x30", ys=_ys(ad, z, e), ayar=ay,
                                              senaryo=dict(tur="geri", aci=aci, v=v), tohum=1))
                        for t in GELISTIRME_TOHUM[:2]:
                            for d in (0.30, 0.40, 0.50, 0.60):
                                for w in (-1.0, 1.0):
                                    G.append(dict(asama=asama, alt="donus", sahne="merdiven_17x30", ys=_ys(ad, z, e), ayar=ay,
                                                  senaryo=dict(tur="donus", d=d, w=w), tohum=t))
                        for w in (0.3, 0.6):
                            G.append(dict(asama=asama, alt="yay", sahne="merdiven_17x30", ys=_ys(ad, z, e), ayar=ay,
                                          senaryo=dict(tur="yay", aci=-60, d=1.0, v=0.25, w=w, t=12.0), tohum=1))
    elif asama == "denetim2":
        # çapraz (D) köşe yerleşiminin yanlış alarmı; denetim sahneleri, gölge eşikleri 4-14 cm
        golge = [dict(esik_m=e, onay=o) for e in (0.04, 0.06, 0.08, 0.10, 0.12) for o in (2, 3)]
        for sahne in ("duz", "esik_20mm", "derz", "koyu_serit", "rampa_10_inis", "hali_10mm", "hali_5mm"):
            for z in YUKSEKLIKLER:
                for e in (15, 30):
                    for v in (0.25, 0.39):
                        for aci in (0, 30, 45):
                            G.append(dict(asama=asama, sahne=sahne, ys=_ys("2KD", z, e), ayar=_ayar(), etkin=False,
                                          golge=golge, senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.2), tohum=1))
    elif asama == "sinama_y":
        # kusur aşamasından (geliştirme tohumları) "yavasla" politikası daha iyi çıktı; sınama yeniden, aynı sınama
        # geometrileri, tohum 101-105 (yarıya indirildi: süre), yalnız ileri yaklaşma + yanlış alarm
        for g in gorevler("sinama"):
            if g["alt"] in ("ileri", "yanlis_alarm") and g["tohum"] <= 105:
                G.append(dict(g, asama=asama, ayar=dict(g["ayar"], politika="yavasla")))
    elif asama == "gelistirme":
        for fren, a in (("rampa", 2.0), ("fren", 0.0)):
            for geo in GELISTIRME_GEO:
                for ad in YERLESIM_ADLARI:
                    for z in (YUKSEKLIKLER if fren == "rampa" else (0.06,)):
                        for e in EGIMLER:
                            for aci in ACILAR:
                                for v in HIZLAR:
                                    for t in (GELISTIRME_TOHUM[:2] if fren == "rampa" else GELISTIRME_TOHUM[:1]):
                                        G.append(dict(asama=asama, sahne=geo, ys=_ys(ad, z, e), ayar=_ayar(fren=fren, fren_ivme=a or 1.8),
                                                      senaryo=dict(tur="ileri", aci=aci, v=v), tohum=t))
        # geri, yerinde dönüş, dönüşlü yörünge (yalnız merdiven; ön yerleşimler + arka sensörlü sürümleri)
        for fren, a in (("rampa", 2.0),):
            for ad in ("2K", "3KO", "2K+2A", "3KO+2A"):
                for z in YUKSEKLIKLER:
                    for e in EGIMLER:
                        for t in GELISTIRME_TOHUM[:2]:
                            for aci in (0, 30, 60):
                                for v in (0.10, 0.25):
                                    G.append(dict(asama=asama, sahne="merdiven_17x30", ys=_ys(ad, z, e), ayar=_ayar(fren=fren, fren_ivme=a),
                                                  senaryo=dict(tur="geri", aci=aci, v=v), tohum=t))
                            for d in (0.30, 0.40, 0.50, 0.60):
                                for w in (-1.0, 1.0):
                                    G.append(dict(asama=asama, sahne="merdiven_17x30", ys=_ys(ad, z, e), ayar=_ayar(fren=fren, fren_ivme=a),
                                                  senaryo=dict(tur="donus", d=d, w=w), tohum=t))
                            for w in (0.3, 0.6):
                                G.append(dict(asama=asama, sahne="merdiven_17x30", ys=_ys(ad, z, e), ayar=_ayar(fren=fren, fren_ivme=a),
                                              senaryo=dict(tur="yay", aci=-60, d=1.0, v=0.25, w=w, t=12.0), tohum=t))
    elif asama == "dar_gelistirme":
        # bağımsız denetim: robottan dar açıklıkta 2KD+2AD düşüyordu. Geliştirme tohumları 1-2, geliştirme genişlikleri.
        # Adaylar: 2KD+2AD (eski seçim), 3KOD+2AD (+ ön orta, düz öne 30°), 4OD+2AD (+ ön iç ±0,085). Denetçi secim'deki.
        ana = _ana(SECIM_1, "yavasla")
        for ad in DAR_ADAYLAR:
            ys = dict(SECIM_1["yerlesim"], ad=ad)
            G += _dar(asama, ys, ana, DAR_GEL_GEO, DAR_GEL_YANAL, (0, 20, 40), GELISTIRME_TOHUM[:2])
        for ad in DAR_ADAYLAR:
            ys = dict(SECIM_1["yerlesim"], ad=ad)
            # geniş kenarda ek sensör bir şeyi bozuyor mu (gelistirme2 ile aynı ızgara, politika yavasla)
            for geo in GELISTIRME_GEO:
                for aci in ACILAR:
                    for v in HIZLAR:
                        G.append(dict(asama=asama, alt="ileri", sahne=geo, ys=ys, ayar=ana, senaryo=dict(tur="ileri", aci=aci, v=v), tohum=1))
            for aci in (0, 30, 60):
                for v in (0.10, 0.25):
                    G.append(dict(asama=asama, alt="geri", sahne="merdiven_17x30", ys=ys, ayar=ana, senaryo=dict(tur="geri", aci=aci, v=v), tohum=1))
            for t in GELISTIRME_TOHUM[:2]:
                for d in (0.30, 0.40, 0.50, 0.60):
                    for w in (-1.0, 1.0):
                        G.append(dict(asama=asama, alt="donus", sahne="merdiven_17x30", ys=ys, ayar=ana, senaryo=dict(tur="donus", d=d, w=w), tohum=t))
            for w in (0.3, 0.6):
                G.append(dict(asama=asama, alt="yay", sahne="merdiven_17x30", ys=ys, ayar=ana,
                              senaryo=dict(tur="yay", aci=-60, d=1.0, v=0.25, w=w, t=12.0), tohum=1))
            # yanlış alarm (geliştirme denetim sahneleri, etkin denetçi)
            for sahne in ("duz", "esik_20mm", "derz", "koyu_serit", "rampa_10_inis", "hali_10mm", "hali_5mm"):
                for v in (0.25, 0.39):
                    for aci in (0, 30, 45):
                        for t in GELISTIRME_TOHUM[:2]:
                            G.append(dict(asama=asama, alt="yanlis_alarm", sahne=sahne, ys=ys, ayar=ana, etkin=True,
                                          senaryo=dict(tur="ileri", aci=aci, v=v, yol_m=2.2), tohum=t))
        # ek ön sensör ölüyse (donmuş / hep dönüşsüz) dar açıklıkta ne olur
        for ad, i in (("3KOD+2AD", 1), ("4OD+2AD", 1), ("4OD+2AD", 2)):
            ys = dict(SECIM_1["yerlesim"], ad=ad)
            for k in ("sabit", "yok"):
                for geo in ("acik_50", "acik_70"):
                    for v in (0.25, 0.39):
                        for t in GELISTIRME_TOHUM[:2]:
                            G.append(dict(asama=asama, alt="kusur", sahne=geo, ys=ys, ayar=ana, ariza={str(i): k}, tohum=t,
                                          senaryo=dict(tur="ileri", aci=0, v=v, yanal=[-0.02, 0.02], yanal_ad=0.0)))
    elif asama == "sinama2":
        # dar açıklık düzeltmesinden sonraki seçimle (secim.json) sınama: ilk sınamanın bütün ızgarası + dar açıklık
        # (yeni genişlikler, sığ açıklık, dar merdiven, yeni yanal kaymalar) + yeni yanlış alarm sahneleri. Tohum 101-110.
        s = SECIM_2
        ys, ana = s["yerlesim"], _ana(s)
        G += _sinama_temel(asama, ys, ana)
        G += _dar(asama, ys, ana, DAR_SIN_GEO, DAR_SIN_YANAL, (0, 10, 30), SINAMA_TOHUM[:5])
        from ucurum import sahne as SH
        G += _yanlis_alarm(asama, ys, ana, SH.DENETIM_SINAMA_YENI, SINAMA_TOHUM[:5], alt="yanlis_alarm_yeni")
    elif asama == "sinama2_karsi":
        # yalnız rapor: seçilmeyen iki aday sınama dar açıklıklarında (seçime girmez; seçim dar_gelistirme'den yapıldı)
        s = SECIM_2
        for ad in ("2KD+2AD", "3KOD+2AD"):
            G += _dar(asama, dict(s["yerlesim"], ad=ad), _ana(s), DAR_SIN_GEO, DAR_SIN_YANAL, (0, 10, 30), SINAMA_TOHUM[:5])
    elif asama.startswith("t_"):
        G += _tamamlama(asama)
    elif asama.startswith("t2_"):
        G += _tamamlama2(asama)
    elif asama.startswith("t3_"):
        G += _aday3(asama)
    elif asama in ("kusur", "sinama"):
        s = SECIM_1                     # donmuş ilk seçim (yeniden üretim)
        ys = s["yerlesim"]
        ana = dict(esik_m=s["esik_m"], onay=s["onay"], politika=s["politika"], fren=s["fren"], fren_ivme=s["fren_ivme"])
        if asama == "kusur":
            n = s["sensor_n"]
            # (a) ölü sensör: her ön sensör sırayla sabit / yok; uçuruma her açıdan; politikalar
            for pol in ("ucurum", "yok_say", "yavasla"):
                # yalnız ön sensörler (ileri yaklaşmada arka sensör arızası sonucu değiştirmez)
                for ariza in [None] + [{str(i): k} for i in range(s.get("on_n", n)) for k in ("sabit", "yok")]:
                    for geo in GELISTIRME_GEO:
                        for aci in (0, 30, 60):
                            for v in (0.25, 0.39):
                                for t in GELISTIRME_TOHUM:
                                    G.append(dict(asama=asama, alt="olu", sahne=geo, ys=ys, ayar=dict(ana, politika=pol), ariza=ariza,
                                                  senaryo=dict(tur="ileri", aci=aci, v=v), tohum=t))
                # (b) parlak zemin: dönüşsüz örnek oranı; uçurum (kaçırma) ve düz zemin (yanlış durma)
                for yok in (0.0, 0.05, 0.20, 0.50):
                    for geo in GELISTIRME_GEO + ("duz",):
                        for aci in (0, 30, 60):
                            for v in (0.25, 0.39):
                                for t in GELISTIRME_TOHUM:
                                    sen = dict(tur="ileri", aci=aci, v=v) if geo != "duz" else dict(tur="ileri", aci=aci, v=v, yol_m=4.0)
                                    G.append(dict(asama=asama, alt="parlak", sahne=geo, ys=ys, ayar=dict(ana, politika=pol), yok=yok,
                                                  senaryo=sen, tohum=t))
        else:
            G += _sinama_temel(asama, ys, ana)
    else:
        raise SystemExit("bilinmeyen aşama: %s" % asama)
    for i, g in enumerate(G):
        g["kimlik"] = "%s-%05d" % (asama, i)
    return G


# ------------------------------------------------------------------ işçi
def _isci_kur():
    _yol.dusuk_oncelik()


def _durma_olcu(r, sahne):
    """Fren / devrilme ölçüleri (hakem satırlarından)."""
    import math as m
    S = r.pop("_hakem")
    r.pop("_okuma", None)
    t0 = r.pop("_t0")
    if r.get("tetik_t") is None:
        return r
    tt = t0 + r["tetik_t"]
    from ucurum import sahne as SH
    egim = math.tan(math.radians(10.0)) if sahne.startswith("rampa") else 0.0
    L_r = SH.al(sahne)["geometri"].get("L", 1.5) if egim else 1.5

    def yuzey(x):
        if not egim:
            return 0.0
        return -min(max(x - SH.E, 0.0), L_r) * egim
    # tamamlama: durduktan sonraki kayma (koşu uzun tutulduysa): tetikten 2 s sonrası ile son arası yol, son 1 s hız
    if S and S[-1][0] - tt >= 3.0:
        def _p(t):
            s = min(S, key=lambda q: abs(q[0] - t))
            return s[1], s[2]
        a2, b2 = _p(tt + 2.0), _p(S[-1][0])
        son1 = [abs(s[4]) for s in S if s[0] >= S[-1][0] - 1.0]
        r.update(kayma_2s_son_mm=round(math.hypot(b2[0] - a2[0], b2[1] - a2[1]) * 1000, 2),
                 v_son1s_mm_s=round(sum(son1) / len(son1) * 1000, 3), sure_tetik_son_s=round(S[-1][0] - tt, 2),
                 toplam_yol_tetik_m=round(math.hypot(S[-1][1] - [s for s in S if s[0] < tt][-1][1],
                                                     S[-1][2] - [s for s in S if s[0] < tt][-1][2]), 4))

    on = [s for s in S if tt - 0.2 <= s[0] < tt]
    hep = [s for s in S if s[0] >= tt]
    son = [s for s in hep if s[0] <= tt + 0.6]          # fren evresi (rampa sonundaki zemin geçişi karışmasın)
    if not on or not son:
        return r
    kay = [s[4] for s in hep if tt + 1.0 <= s[0] <= tt + 2.0]
    r.update(v_min_06=round(min(s[4] for s in son), 4), kayma_hiz_1_2s=round(sum(kay) / len(kay), 4) if kay else None,
             durma_yolu_06_m=round(math.hypot(son[-1][1] - on[-1][1], son[-1][2] - on[-1][2]), 4),
             arka_yuk_once_min_N=round(min(s[7] for s in on), 1))
    son_d = son
    son = son_d
    p0 = sum(s[5] for s in on) / len(on)
    F0 = sum(s[7] for s in on) / len(on)
    c0 = sum(s[9] - yuzey(s[10]) for s in on) / len(on)
    v0 = on[-1][4]
    dur_t = next((s[0] for s in hep if abs(s[4]) < 0.005), None)
    ivme = 0.0
    for a, b in zip(son, son[2:]):
        ivme = max(ivme, -(b[4] - a[4]) / max(b[0] - a[0], 1e-6))
    sifir = sum(1 for s in son if s[7] < 1.0) * 0.01
    r.update(v_once=round(v0, 4), durma_sure_s=round(dur_t - tt, 3) if dur_t else None,
             tepe_yavaslama=round(ivme, 3), pitch_tepe_der=round(max(s[5] for s in son) - p0, 3),
             arka_yuk_once_N=round(F0, 1), arka_yuk_min_N=round(min(s[7] for s in son), 1),
             arka_sifir_s=round(sifir, 3), arka_kalkma_mm=round((max(s[9] - yuzey(s[10]) for s in son) - c0) * 1000, 2))
    return r


def _denetim_sahneleri():
    from ucurum import sahne as SH
    return SH.DENETIM_GELISTIRME + SH.DENETIM_SINAMA_YENI


def gorev_kos(g):
    from ucurum import kosu, sensor
    from ucurum.denetci import DenetciAyar
    ys = g["ys"]
    yer = sensor.yerlesim(ys["ad"], ys["z"], ys["e"], ys.get("koni", 27.0))
    ks = g.get("kosul") or {}              # tamamlama turu koşulları (yoksa davranış aynı)
    if ks.get("montaj"):
        import numpy as np
        yer = sensor.montaj_bozu(yer, np.random.default_rng(50_000 + g["tohum"]), kotu=(ks["montaj"] == "kotu"))
    for a in yer:
        if ks.get("menzil_m"):
            a.menzil_maks_m = float(ks["menzil_m"])
        if ks.get("sigma_taban_m"):
            a.sigma_taban_m = float(ks["sigma_taban_m"])
    if g.get("yok"):
        for a in yer:
            a.yok_orani = g["yok"]
    ariza = {int(k): v for k, v in (g.get("ariza") or {}).items()}
    sen = dict(g["senaryo"])
    t_max = None
    if "yol_m" in sen:
        vn = abs(sen["v"]) * math.cos(math.radians(sen.get("aci", 0)))
        t_max = sen["yol_m"] / max(abs(sen["v"]), 0.01) + 1.0
    zorla = None
    kayit = False
    baslangic = None
    if g.get("zorla"):
        kayit = True
        from ucurum import sahne as SH
        if g["sahne"] == "duz":
            baslangic = (12.0, 15.0, 0.0)
            zorla = lambda c: c.dunya.poz()[0] >= 13.5
        else:
            baslangic = (SH.E - 0.6, 15.0, 0.0)
            zorla = lambda c: c.dunya.poz()[0] >= SH.E + 0.85
        t_max = 1.6 / max(sen["v"], 0.05) + 4.0
    elif g.get("baslangic"):
        baslangic = tuple(g["baslangic"])
    elif g["senaryo"].get("yol_m") is not None or g["sahne"] in _denetim_sahneleri():
        from ucurum import sahne as SH
        # denetim sahneleri: özellik x = E; robotun ön tekeri özelliğin 0,6 m gerisinden başlar
        a = math.radians(sen.get("aci", 0))
        baslangic = (SH.E - 0.6 - 0.185 * math.cos(a) - 0.05, 15.0, a)
    if g.get("t_max"):
        t_max = float(g["t_max"])
    golge = [DenetciAyar(**dict(_ayar(), **x)) for x in g.get("golge", [])]
    try:
        r = kosu.kos(g["sahne"], yer, DenetciAyar(**g["ayar"]), sen, tohum=g["tohum"], golgeler=golge,
                     etkin=g.get("etkin", True), kayit=kayit, yuk_olc=kayit, zorla_tetik=zorla, baslangic=baslangic,
                     t_max=t_max, ariza=ariza, degis=ks.get("degis"), ek_kutle=ks.get("ek_kutle"),
                     periyot_ms=ks.get("periyot_ms"), butce_ms=ks.get("butce_ms"), gecikme_ms=ks.get("gecikme_ms", 0),
                     tutma=ks.get("tutma"), dusunce_dur=not g.get("surdur"), durdu_bekle_s=g.get("durdu_bekle_s", 0.3))
        if g.get("zorla"):
            r = _durma_olcu(r, g["sahne"])
        r["hata"] = None
    except Exception as h:  # başarısız koşu saklanır ve sayılır
        import traceback
        r = dict(hata="%s: %s" % (type(h).__name__, h), iz=traceback.format_exc()[-800:])
    r["kimlik"] = g["kimlik"]
    r["gorev"] = {k: v for k, v in g.items() if k not in ("golge",)}
    r["yerlesim"] = sensor.yerlesim_adi(ys["ad"], ys["z"], ys["e"], ys.get("koni", 27.0))
    return r


# ------------------------------------------------------------------ yazım
def _duz_satir(r):
    g = r.get("gorev", {})
    s = dict(kimlik=r["kimlik"], alt=g.get("alt"), yerlesim=r.get("yerlesim"), fren=g.get("ayar", {}).get("fren"),
             fren_ivme=g.get("ayar", {}).get("fren_ivme"), esik_m=g.get("ayar", {}).get("esik_m"), onay=g.get("ayar", {}).get("onay"),
             politika=g.get("ayar", {}).get("politika"), ariza=json.dumps(g.get("ariza")) if g.get("ariza") else "",
             yok_orani_ayar=g.get("yok", 0.0), etkin=g.get("etkin", True), yanal=g.get("senaryo", {}).get("yanal_ad"))
    if g.get("kosul") is not None or g.get("kad") is not None:       # tamamlama turu aşamaları
        s.update(kad=g.get("kad"), kosul=json.dumps(g.get("kosul") or {}, ensure_ascii=False))
    for k, v in r.items():
        if k in ("gorev", "golge", "kimlik", "yerlesim") or k.startswith("_"):
            continue
        s[k] = json.dumps(v) if isinstance(v, (list, dict)) else v
    return s


def csv_yaz(asama):
    ham = os.path.join(_yol.HAM, asama + ".jsonl")
    R = [json.loads(x) for x in open(ham, encoding="utf-8")]
    R.sort(key=lambda r: r["kimlik"])
    satir = [_duz_satir(r) for r in R]
    alanlar = []
    for s in satir:
        for k in s:
            if k not in alanlar:
                alanlar.append(k)
    with open(os.path.join(_yol.SONUC, asama + ".csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=alanlar)
        w.writeheader()
        w.writerows(satir)
    G = [dict(kimlik=r["kimlik"], sahne=r.get("sahne"), yerlesim=r.get("yerlesim"), v=r.get("v"), aci=r.get("aci"),
              tohum=r.get("tohum"), **x) for r in R for x in (r.get("golge") or [])]
    if G:
        with open(os.path.join(_yol.SONUC, asama + "_golge.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(G[0]))
            w.writeheader()
            w.writerows(G)
    return len(R), sum(1 for r in R if r.get("hata"))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("asama")
    ap.add_argument("--surec", type=int, default=2)
    ap.add_argument("--sinir", type=int, default=None)
    a = ap.parse_args()
    _yol.dusuk_oncelik()
    os.makedirs(_yol.HAM, exist_ok=True)
    G = gorevler(a.asama)
    if a.sinir:
        G = G[:a.sinir]
    ham = os.path.join(_yol.HAM, a.asama + ".jsonl")
    bitti = set()
    if os.path.exists(ham):
        for x in open(ham, encoding="utf-8"):
            try:
                bitti.add(json.loads(x)["kimlik"])
            except Exception:
                pass
    kalan = [g for g in G if g["kimlik"] not in bitti]
    ns = max(1, min(a.surec, SUREC_TAVAN))
    _yol.durum_yaz("%s basladi: %d gorev, %d kalan, %d surec" % (a.asama, len(G), len(kalan), ns))
    t0 = time.time()
    n = 0
    with open(ham, "a", encoding="utf-8") as f:
        if ns <= 1:
            it = map(gorev_kos, kalan)
            havuz = None
        else:
            import multiprocessing as mp
            havuz = mp.Pool(ns, initializer=_isci_kur)
            it = havuz.imap_unordered(gorev_kos, kalan, chunksize=4)
        for r in it:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
            if n % 200 == 0:
                f.flush()
                _yol.durum_yaz("%s %d / %d (%.0f s)" % (a.asama, n, len(kalan), time.time() - t0))
        if havuz is not None:
            havuz.close()
            havuz.join()
    toplam, hata = csv_yaz(a.asama)
    _yol.durum_yaz("%s bitti: %d kosu, %d hata, %.0f s" % (a.asama, toplam, hata, time.time() - t0))
    print("%s: %d kosu, %d hata, %.0f s" % (a.asama, toplam, hata, time.time() - t0))


if __name__ == "__main__":
    main()
