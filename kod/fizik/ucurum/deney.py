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
    return dict(esik_m=s["esik_m"], onay=s["onay"], politika=politika or s["politika"], fren=s["fren"], fren_ivme=s["fren_ivme"])


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
        s = secim()
        ys, ana = s["yerlesim"], _ana(s)
        G += _sinama_temel(asama, ys, ana)
        G += _dar(asama, ys, ana, DAR_SIN_GEO, DAR_SIN_YANAL, (0, 10, 30), SINAMA_TOHUM[:5])
        from ucurum import sahne as SH
        G += _yanlis_alarm(asama, ys, ana, SH.DENETIM_SINAMA_YENI, SINAMA_TOHUM[:5], alt="yanlis_alarm_yeni")
    elif asama == "sinama2_karsi":
        # yalnız rapor: seçilmeyen iki aday sınama dar açıklıklarında (seçime girmez; seçim dar_gelistirme'den yapıldı)
        s = secim()
        for ad in ("2KD+2AD", "3KOD+2AD"):
            G += _dar(asama, dict(s["yerlesim"], ad=ad), _ana(s), DAR_SIN_GEO, DAR_SIN_YANAL, (0, 10, 30), SINAMA_TOHUM[:5])
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

    def yuzey(x):
        if not egim:
            return 0.0
        return -min(max(x - SH.E, 0.0), 1.5) * egim

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
    elif g["senaryo"].get("yol_m") is not None or g["sahne"] in _denetim_sahneleri():
        from ucurum import sahne as SH
        # denetim sahneleri: özellik x = E; robotun ön tekeri özelliğin 0,6 m gerisinden başlar
        a = math.radians(sen.get("aci", 0))
        baslangic = (SH.E - 0.6 - 0.185 * math.cos(a) - 0.05, 15.0, a)
    golge = [DenetciAyar(**dict(_ayar(), **x)) for x in g.get("golge", [])]
    try:
        r = kosu.kos(g["sahne"], yer, DenetciAyar(**g["ayar"]), sen, tohum=g["tohum"], golgeler=golge,
                     etkin=g.get("etkin", True), kayit=kayit, yuk_olc=kayit, zorla_tetik=zorla, baslangic=baslangic,
                     t_max=t_max, ariza=ariza)
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
