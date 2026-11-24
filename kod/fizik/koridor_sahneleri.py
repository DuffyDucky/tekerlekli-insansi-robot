"""Okul koridoru sahneleri (koridor_1 … koridor_6): üret, çiz, doğrula. 2B LiDAR'ın koridorları ayırt etme deneyi için.

    py -3 kod/fizik/koridor_sahneleri.py uret      # -> kod/araclar/haritalar/koridor_N.json + kod/fizik/sahneler/koridor_N.json
    py -3 kod/fizik/koridor_sahneleri.py ciz       # -> kod/fizik/sahneler/gorsel/*.png (matplotlib gerekir)
    "%LALE_SIM_VENV%\\Scripts\\python.exe" kod/fizik/koridor_sahneleri.py dogrula [sahne ...]   # mujoco gerekir

Tek kaynak bu dosyadaki KORIDORLAR tanımıdır; JSON'lar buradan üretilir (elle düzeltme yerine burayı değiştirip `uret`).
Koridor bir çokgen (saat yönü tersine, içi solda); her duvar kenarına özellik eklenir:
  kapali  kapalı kapı: duvarda 0,95 m x 0,09 m kasa girintisi (dışa)
  acik    açık kapı: 0,95 m açıklık, 0,15 m duvar kalınlığı, arkasında kapalı oda (3 x 4 m)
  kolon   duvar dibinde kolon çıkıntısı (içe), yangin  yüzeye monte yangın dolabı çıkıntısı (içe)
Bütün duvarlar 2B haritada çizgi parçası, 3B'de `dunya.sahne_xml` ile ince levha (yükseklik `duvar_yuksekligi_m` = 1,0 m;
LiDAR düzlemi 0,10-0,30 m'yi kapsar). `cevre_duvari` kapalı: sahnenin dış çevresi koridorun kendi çokgenidir (kapalı).
Robotun süreceği yol (`orta_hat`) ve ayırt edici özellikler (`ozellikler`) 3B sahne JSON'unda; yükleyiciler (`dunya.sahne_oku`,
`gorunum3b.Pencere`, `sahte_esp32.harita.Harita`) bilinmeyen anahtarlara bakmaz.
"""

import json
import math
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(BURASI)
HARITALAR = os.path.join(KOD, "araclar", "haritalar")
SAHNELER = os.path.join(BURASI, "sahneler")
GORSEL = os.path.join(SAHNELER, "gorsel")

KAPI_G, KAPI_D = 0.95, 0.09          # kapı kasası genişliği, girinti derinliği (m)
DUVAR_T = 0.15                       # açık kapıda koridor ile oda arasındaki duvar kalınlığı (m)
ODA_D = 4.0                          # açık kapının arkasındaki odanın derinliği (m); boyu her kapıda `oda` ile
BAS_PAY = 0.8                        # başlangıç: uç duvardan uzaklık (robot tabanı 520 x 525 mm)


def K(c0):
    return {"tur": "kapali", "c0": c0}


def A(c0, r0, r1):
    return {"tur": "acik", "c0": c0, "oda": (r0, r1)}


# Koordinatlar yerel çerçevede (kaydırmadan önce); c0 = özelliğin duvar ekseni boyunca başlangıcı (x ya da y, m).
KORIDORLAR = {
    "koridor_1": {
        "aciklama": "Dar ve uzun duz koridor 2,0 x 30 m; iki yanda 1,5 m aralikla sik ve duzenli kapilar (alt ve ust "
                    "duvar 3 m adimla, birbirine gore 1,5 m kaydirili), 2 acik kapi + arkalarinda 3 x 4 m oda.",
        "cokgen": [(0, 0), (30, 0), (30, 2.0), (0, 2.0)],
        "kenar": ["alt", "sag_uc", "ust", "sol_uc"],
        "ozellik": {
            "alt": [K(1.6 + 3 * k) for k in range(9) if k != 4] + [A(13.6, 12.6, 15.6)],
            "ust": [K(3.1 + 3 * k) for k in range(9) if k != 6] + [A(21.1, 20.1, 23.1)],
        },
        "orta_hat": [(BAS_PAY, 1.0), (30 - BAS_PAY, 1.0)],
    },
    "koridor_2": {
        "aciklama": "Genis ve kisa duz koridor 3,5 x 12 m; az kapi (2 kapali, 1 acik + oda), ust duvar dibinde 2 kolon "
                    "cikintisi (0,40 x 0,30 m), alt duvar onunde dolap (1,80 x 0,45 m).",
        "cokgen": [(0, 0), (12, 0), (12, 3.5), (0, 3.5)],
        "kenar": ["alt", "sag_uc", "ust", "sol_uc"],
        "ozellik": {
            "alt": [K(1.8), A(7.0, 6.5, 9.5)],
            "ust": [{"tur": "kolon", "c0": 3.8, "g": 0.40, "d": 0.30}, {"tur": "kolon", "c0": 7.8, "g": 0.40, "d": 0.30},
                    K(9.6)],
        },
        "kutular": [{"ad": "dolap", "x": 3.2, "y": 0.03, "g": 1.80, "d": 0.45}],
        "orta_hat": [(BAS_PAY, 1.75), (12 - BAS_PAY, 1.75)],
    },
    "koridor_3": {
        "aciklama": "L bicimli koridor, genislik 2,4 m; kollar 16 m (x) ve 10 m (y), dis kenardan. Duzensiz aralikli "
                    "kapilar, sag kolun dis duvarinda 1 acik kapi + oda.",
        "cokgen": [(0, 0), (16, 0), (16, 10), (13.6, 10), (13.6, 2.4), (0, 2.4)],
        "kenar": ["kol1_alt", "kol2_dis", "kol2_uc", "kol2_ic", "kol1_ust", "kol1_uc"],
        "ozellik": {
            "kol1_alt": [K(2.2), K(7.4), K(11.0)],
            "kol1_ust": [K(4.6), K(9.0)],
            "kol2_dis": [A(5.0, 4.0, 7.0), K(8.2)],
            "kol2_ic": [K(6.5)],
        },
        "orta_hat": [(BAS_PAY, 1.2), (14.8, 1.2), (14.8, 10 - BAS_PAY)],
        "ozel": [{"tur": "kose", "merkez": (14.8, 1.2), "aciklama": "L donusu (sola 90 derece)"}],
    },
    "koridor_4": {
        "aciklama": "T kavsakli koridor: ana hat 2,6 x 22 m, x = 9,0-11,6 arasindan ust duvara 8 m yan kol (2,6 m). "
                    "Kapilar iki yanda duzensiz, ana hat alt duvarinda 1 acik kapi + oda.",
        "cokgen": [(0, 0), (22, 0), (22, 2.6), (11.6, 2.6), (11.6, 10.6), (9.0, 10.6), (9.0, 2.6), (0, 2.6)],
        "kenar": ["ana_alt", "ana_sag_uc", "ana_ust_sag", "kol_sag", "kol_uc", "kol_sol", "ana_ust_sol", "ana_sol_uc"],
        "ozellik": {
            "ana_alt": [K(2.0), K(5.5), K(10.0), K(14.5), A(19.5, 18.8, 21.8)],
            "ana_ust_sol": [K(3.5), K(6.8)],
            "ana_ust_sag": [K(14.0), K(18.0)],
            "kol_sag": [K(6.0)],
            "kol_sol": [K(7.5)],
        },
        "orta_hat": [(BAS_PAY, 1.3), (22 - BAS_PAY, 1.3)],
        "orta_hat_yan_kol": [(10.3, 1.3), (10.3, 10.6 - BAS_PAY)],
        "ozel": [{"tur": "kavsak", "merkez": (10.3, 1.3), "aciklama": "T kavsagi: yan kol ust duvarda x 9,0-11,6"}],
    },
}

# Benzer çift: aynı dış ölçü 2,4 x 24 m, aynı kapı ritmi (her duvarda 4 m adım, iki duvar birbirine göre 2 m kaydırılı),
# aynı açık kapı + oda. koridor_6'da yalnız iki yerel fark (FARKLAR).
_CIFT_ALT = [K(2.5), A(6.5, 5.5, 8.5), K(10.5), K(14.5), K(18.5)]
_CIFT_UST = [K(4.5), K(8.5), K(12.5), K(16.5), K(20.5)]
FARKLAR = [
    {"id": "fark_1_kapi_kaydirma", "tur": "kapi_kaydirma", "duvar": "ust",
     "koridor_5": "ust duvar 4. kapi (ust_kapi_kapali_4) x 17,50-18,45, y 7,40 (harita)",
     "koridor_6": "ayni kapi 0,60 m ileride: x 18,10-19,05, y 7,40 (harita); kasa 0,95 x 0,09 m"},
    {"id": "fark_2_yangin_dolabi", "tur": "yangin_dolabi", "duvar": "alt",
     "koridor_5": "yok (duz duvar)",
     "koridor_6": "alt duvarda yangin dolabi x 17,60-18,40, duvar y 5,00 -> on yuz y 5,18 (harita); 0,80 x 0,18 m ice cikinti"},
]
for _ad, _ust, _alt_ek, _acik in (
        ("koridor_5", _CIFT_UST, [], "koridor_6 ile benzer cift (fark yok tarafi)"),
        ("koridor_6", [K(4.5), K(8.5), K(12.5), K(17.1), K(20.5)],
         [{"tur": "yangin", "c0": 16.6, "g": 0.80, "d": 0.18}], "koridor_5 ile benzer cift; 2 yerel fark")):
    KORIDORLAR[_ad] = {
        "aciklama": "Benzer cift: duz koridor 2,4 x 24 m, her duvarda 4 m adimla 5 kapi (alt x 2,5 + 4k, ust x 4,5 + 4k), "
                    "alt duvarda 2. kapi acik + oda. " + _acik + ".",
        "cokgen": [(0, 0), (24, 0), (24, 2.4), (0, 2.4)],
        "kenar": ["alt", "sag_uc", "ust", "sol_uc"],
        "ozellik": {"alt": _CIFT_ALT + _alt_ek, "ust": _ust},
        "orta_hat": [(BAS_PAY, 1.2), (24 - BAS_PAY, 1.2)],
        "benzer_cift": {"es": "koridor_6" if _ad == "koridor_5" else "koridor_5"},
    }

TUR_AD = {"kapali": "kapi_kapali", "acik": "kapi_acik", "kolon": "kolon", "yangin": "yangin_dolabi"}


# ------------------------------------------------------------------ geometri

def _r(v):
    return round(float(v) + 0.0, 3) + 0.0


def _kenar_bilgi(p0, p1):
    ux, uy = p1[0] - p0[0], p1[1] - p0[1]
    boy = math.hypot(ux, uy)
    ux, uy = ux / boy, uy / boy
    eksen = 0 if abs(ux) > 0.5 else 1
    isaret = 1.0 if (ux if eksen == 0 else uy) > 0 else -1.0
    return (ux, uy), (uy, -ux), eksen, isaret, boy           # dış normal: saat yönü tersi çokgende sağ taraf


def _s(p0, eksen, isaret, c):
    return (c - p0[eksen]) * isaret


def koridor_kur(tanim):
    """Yerel çerçevede: (nokta listesi = kapalı çevre, özellik kayıtları)."""
    cg = tanim["cokgen"]
    noktalar, kayit = [], []
    for i, p0 in enumerate(cg):
        p1 = cg[(i + 1) % len(cg)]
        ad = tanim["kenar"][i]
        (ux, uy), (nx, ny), eksen, isaret, boy = _kenar_bilgi(p0, p1)
        P = lambda s, d=0.0: (p0[0] + ux * s + nx * d, p0[1] + uy * s + ny * d)
        oz = []
        for f in tanim.get("ozellik", {}).get(ad, []):
            g = f.get("g", KAPI_G)
            a, b = sorted((_s(p0, eksen, isaret, f["c0"]), _s(p0, eksen, isaret, f["c0"] + g)))
            if a <= 0.05 or b >= boy - 0.05:
                raise ValueError("%s: özellik kenar dışında (%s)" % (ad, f))
            oz.append((a, b, f))
        oz.sort(key=lambda t: t[0])
        for (a1, b1, _), (a2, b2, _) in zip(oz, oz[1:]):
            if a2 < b1 + 0.1:
                raise ValueError("%s: özellikler çakışıyor (%.2f-%.2f / %.2f-%.2f)" % (ad, a1, b1, a2, b2))
        noktalar.append(P(0.0))
        for a, b, f in oz:
            tur = f["tur"]
            rec = {"tur": TUR_AD[tur], "duvar": ad, "a": P(a), "b": P(b), "genislik_m": round(b - a, 3)}
            if tur == "acik":
                r0, r1 = sorted((_s(p0, eksen, isaret, f["oda"][0]), _s(p0, eksen, isaret, f["oda"][1])))
                if not (r0 <= a and r1 >= b):
                    raise ValueError("%s: oda açıklığı kapsamıyor" % ad)
                noktalar += [P(a), P(a, DUVAR_T), P(r0, DUVAR_T), P(r0, DUVAR_T + ODA_D), P(r1, DUVAR_T + ODA_D),
                             P(r1, DUVAR_T), P(b, DUVAR_T), P(b)]
                k = [P(r0, DUVAR_T), P(r1, DUVAR_T + ODA_D)]
                rec.update(derinlik_m=DUVAR_T, oda={"x0": min(k[0][0], k[1][0]), "y0": min(k[0][1], k[1][1]),
                                                    "x1": max(k[0][0], k[1][0]), "y1": max(k[0][1], k[1][1])})
            else:
                d = KAPI_D if tur == "kapali" else -f["d"]       # + dışa girinti, - içe çıkıntı
                noktalar += [P(a), P(a, d), P(b, d), P(b)]
                rec["derinlik_m"] = round(abs(d), 3)
                rec["yon"] = "girinti" if d > 0 else "cikinti"
            kayit.append(rec)
    return noktalar, kayit


def _parcalar(noktalar):
    """Kapalı çevreyi parçalara böl; aynı doğrultudaki ardışık parçaları birleştir."""
    n = len(noktalar)
    p = [noktalar[0]]
    for i in range(1, n + 1):
        q = noktalar[i % n]
        if math.hypot(q[0] - p[-1][0], q[1] - p[-1][1]) < 1e-9:
            continue
        p.append(q)
    temiz = [p[0]]
    for i in range(1, len(p)):
        if i + 1 < len(p):
            a, b, c = temiz[-1], p[i], p[i + 1]
            capraz = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            ayni_yon = (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1]) > 0
            if abs(capraz) < 1e-9 and ayni_yon:
                continue
        temiz.append(p[i])
    return [(temiz[i][0], temiz[i][1], temiz[i + 1][0], temiz[i + 1][1]) for i in range(len(temiz) - 1)]


def _izdusum(hat, x, y):
    """Noktanın çoklu doğruya en yakın izdüşümü: (yol boyunca uzaklık s, dik uzaklık)."""
    en, s0 = None, 0.0
    for (ax, ay), (bx, by) in zip(hat, hat[1:]):
        L = math.hypot(bx - ax, by - ay)
        t = max(0.0, min(1.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / (L * L)))
        px, py = ax + t * (bx - ax), ay + t * (by - ay)
        d = math.hypot(x - px, y - py)
        if en is None or d < en[1] - 1e-9:
            en = (s0 + t * L, d)
        s0 += L
    return en


def sahne_kur(ad):
    """(harita sözlüğü, sahne sözlüğü) harita çerçevesinde (bütün koordinatlar >= 0)."""
    t = KORIDORLAR[ad]
    noktalar, kayit = koridor_kur(t)
    kutular = t.get("kutular", [])
    xs = [p[0] for p in noktalar] + [k["x"] for k in kutular] + [k["x"] + k["g"] for k in kutular]
    ys = [p[1] for p in noktalar] + [k["y"] for k in kutular] + [k["y"] + k["d"] for k in kutular]
    dx, dy = math.ceil(-min(xs) + 0.5), math.ceil(-min(ys) + 0.5)
    boyut = [math.ceil(max(xs) + dx + 0.5), math.ceil(max(ys) + dy + 0.5)]
    T = lambda p: [_r(p[0] + dx), _r(p[1] + dy)]
    parca = [[_r(x1 + dx), _r(y1 + dy), _r(x2 + dx), _r(y2 + dy)] for (x1, y1, x2, y2) in _parcalar(noktalar)]
    hat = [T(p) for p in t["orta_hat"]]
    yan = [T(p) for p in t.get("orta_hat_yan_kol", [])]
    bx, by = hat[0]
    ilk = math.degrees(math.atan2(hat[1][1] - by, hat[1][0] - bx))
    baslangic = {"x": bx, "y": by, "aci_derece": round(ilk, 3) + 0.0}

    def konum(x, y):
        s, d = _izdusum(hat, x, y)
        o = {"hat": "orta_hat", "s_m": round(s, 3)}
        if yan:
            s2, d2 = _izdusum(yan, x, y)
            if d2 < d - 1e-9:
                o = {"hat": "orta_hat_yan_kol", "s_m": round(s2, 3)}
        return o

    oz = []
    for r in kayit:
        a, b = T(r["a"]), T(r["b"])
        e = {"id": None, "tur": r["tur"], "duvar": r["duvar"],
             "duvar_cizgisi": a + b, "merkez": [_r((a[0] + b[0]) / 2), _r((a[1] + b[1]) / 2)],
             "genislik_m": r["genislik_m"], "derinlik_m": r["derinlik_m"]}
        if "yon" in r:
            e["yon"] = r["yon"]
        if "oda" in r:
            o = r["oda"]
            e["oda"] = {"x0": _r(o["x0"] + dx), "y0": _r(o["y0"] + dy), "x1": _r(o["x1"] + dx), "y1": _r(o["y1"] + dy)}
        e.update(konum(*e["merkez"]))
        oz.append(e)
    for k in kutular:
        m = [_r(k["x"] + dx + k["g"] / 2), _r(k["y"] + dy + k["d"] / 2)]
        e = {"id": k["ad"], "tur": k["ad"], "kutu": [_r(k["x"] + dx), _r(k["y"] + dy), k["g"], k["d"]], "merkez": m,
             "genislik_m": k["g"], "derinlik_m": k["d"]}
        e.update(konum(*m))
        oz.append(e)
    for z in t.get("ozel", []):
        m = T(z["merkez"])
        e = {"id": z["tur"], "tur": z["tur"], "merkez": m, "aciklama": z["aciklama"]}
        e.update(konum(*m))
        oz.append(e)
    for i, p in ((0, hat[0]), (1, hat[-1])) + (((2, yan[-1]),) if yan else ()):
        e = {"id": "uc_duvar_%d" % (i + 1), "tur": "uc_duvar", "aciklama": "kapali uc; orta hat ucu duvardan %s m" % ("%.1f" % BAS_PAY).replace(".", ","),
             "merkez": p}
        e.update(konum(*p))
        oz.append(e)
    oz.sort(key=lambda e: (e["hat"], e["s_m"]))
    sayac = {}                                          # kimlik: duvar_tur_sıra (sıra robot yolu boyunca, 1'den)
    for e in oz:
        if e["id"] is None:
            k = (e["duvar"], e["tur"])
            sayac[k] = sayac.get(k, 0) + 1
            e["id"] = "%s_%s_%d" % (k[0], k[1], sayac[k])

    harita = {"ad": ad, "aciklama": t["aciklama"] + " Uretici: kod/fizik/koridor_sahneleri.py.",
              "boyut_m": boyut, "cevre_duvari": False, "duvarlar": parca,
              "engeller": [{"tur": "kutu", "x": _r(k["x"] + dx), "y": _r(k["y"] + dy), "g": k["g"], "d": k["d"], "ad": k["ad"]}
                           for k in kutular],
              "baslangic": baslangic}
    sahne = {"ad": ad, "aciklama": "Koridor sahnesi (LiDAR ayirt etme deneyi): %s haritasi. Rampa / esik yok. Orta hat ve "
                                   "ozellikler harita cercevesinde (m); s_m = orta hat boyunca baslangictan uzaklik." % ad,
             "harita": ad, "baslangic": baslangic, "rampalar": [], "esikler": [],
             "kaydirma_m": [dx, dy], "orta_hat": hat}
    if yan:
        sahne["orta_hat_yan_kol"] = yan
    sahne["ozellikler"] = oz
    if "benzer_cift" in t:
        if (dx, dy) != (1, 5):
            raise ValueError("FARKLAR metni harita kaydırması (1, 5) varsayar; metni güncelle")
        farklar = []
        for f in FARKLAR:
            g = dict(f)
            if f["tur"] == "kapi_kaydirma":
                g.update(koridor_5_harita={"duvar_cizgisi": [_r(16.5 + dx), _r(2.4 + dy), _r(17.45 + dx), _r(2.4 + dy)]},
                         koridor_6_harita={"duvar_cizgisi": [_r(17.1 + dx), _r(2.4 + dy), _r(18.05 + dx), _r(2.4 + dy)]},
                         kayma_m=0.6)
            else:
                g.update(koridor_6_harita={"duvar_cizgisi": [_r(16.6 + dx), _r(0 + dy), _r(17.4 + dx), _r(0 + dy)],
                                           "genislik_m": 0.8, "derinlik_m": 0.18})
            g["s_m_araligi"] = None
            farklar.append(g)
        s_kapi = [_izdusum(hat, x + dx, 2.4 + dy)[0] for x in (16.5, 18.05)]
        s_dolap = [_izdusum(hat, x + dx, dy)[0] for x in (16.6, 17.4)]
        farklar[0]["s_m_araligi"] = [round(s_kapi[0], 3), round(s_kapi[1], 3)]
        farklar[1]["s_m_araligi"] = [round(s_dolap[0], 3), round(s_dolap[1], 3)]
        s_bas, s_son = min(s_kapi + s_dolap), max(s_kapi + s_dolap)
        sahne["benzer_cift"] = {"es": t["benzer_cift"]["es"], "farklar": farklar,
                                "fark_bolgesi_s_m": [round(s_bas, 3), round(s_son, 3)],
                                "fark_bolgesi_orani": round((s_son - s_bas) / 24.0, 3),
                                "not": "Fark bolgesi disinda iki koridorun geometrisi birebir ayni."}
    return harita, sahne


# ------------------------------------------------------------------ yazma

def _json_yaz(yol, veri):
    """Okunur JSON: liste içinde sayı listeleri (duvar parçası, nokta) tek satırda."""
    def yaz(v, g):
        bos = "  " * g
        if isinstance(v, dict):
            if not v:
                return "{}"
            ic = ",\n".join("%s  %s: %s" % (bos, json.dumps(k, ensure_ascii=False), yaz(x, g + 1)) for k, x in v.items())
            return "{\n" + ic + "\n" + bos + "}"
        if isinstance(v, list):
            if not v:
                return "[]"
            if all(not isinstance(x, (dict, list)) for x in v):
                return json.dumps(v, ensure_ascii=False)
            if all(isinstance(x, list) for x in v) or (all(isinstance(x, dict) for x in v) and len(json.dumps(v[0])) < 110):
                return "[\n" + ",\n".join(bos + "  " + json.dumps(x, ensure_ascii=False) for x in v) + "\n" + bos + "]"
            return "[\n" + ",\n".join(bos + "  " + yaz(x, g + 1) for x in v) + "\n" + bos + "]"
        return json.dumps(v, ensure_ascii=False)
    with open(yol, "w", encoding="utf-8", newline="\n") as f:
        f.write(yaz(veri, 0) + "\n")


def uret():
    for ad in KORIDORLAR:
        h, s = sahne_kur(ad)
        _json_yaz(os.path.join(HARITALAR, ad + ".json"), h)
        _json_yaz(os.path.join(SAHNELER, ad + ".json"), s)
        print("%s: %d duvar parcasi, %d ozellik, boyut %s m" % (ad, len(h["duvarlar"]), len(s["ozellikler"]), h["boyut_m"]))


# ------------------------------------------------------------------ çizim (matplotlib)

RENK = {"kapi_kapali": "#d9822b", "kapi_acik": "#2e9e4f", "kolon": "#7a4fbf", "yangin_dolabi": "#d62728",
        "dolap": "#1f77b4", "kavsak": "#555555", "kose": "#555555"}


def _oku(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def _ciz_eksen(ax, ad, baslik=None, etiket=True, vurgula=None):
    from matplotlib.patches import FancyArrow, Rectangle
    h = _oku(os.path.join(HARITALAR, ad + ".json"))
    s = _oku(os.path.join(SAHNELER, ad + ".json"))
    for o in s["ozellikler"]:
        if "oda" in o:
            r = o["oda"]
            ax.add_patch(Rectangle((r["x0"], r["y0"]), r["x1"] - r["x0"], r["y1"] - r["y0"], color="#e8f3ea", zorder=0))
            ax.text((r["x0"] + r["x1"]) / 2, (r["y0"] + r["y1"]) / 2, "oda", ha="center", va="center", fontsize=7,
                    color="#2e9e4f", clip_on=True)
    for x1, y1, x2, y2 in h["duvarlar"]:
        ax.plot([x1, x2], [y1, y2], color="#222222", lw=1.3, solid_capstyle="butt", zorder=3)
    for e in h.get("engeller", []):
        if e["tur"] == "kutu":
            ax.add_patch(Rectangle((e["x"], e["y"]), e["g"], e["d"], facecolor="#cfe0f3", edgecolor="#1f77b4", lw=1.2,
                                   zorder=3))
    for o in s["ozellikler"]:
        c = RENK.get(o["tur"])
        if "duvar_cizgisi" in o and c:
            x1, y1, x2, y2 = o["duvar_cizgisi"]
            ax.plot([x1, x2], [y1, y2], color=c, lw=4, alpha=0.75, solid_capstyle="butt", zorder=4)
        if o["tur"] in ("kavsak", "kose"):
            ax.plot(*o["merkez"], marker="+", ms=10, color=c, zorder=5)
    hat = s["orta_hat"]
    ax.plot([p[0] for p in hat], [p[1] for p in hat], ls="--", color="#4a6fa5", lw=1, zorder=2)
    if s.get("orta_hat_yan_kol"):
        yk = s["orta_hat_yan_kol"]
        ax.plot([p[0] for p in yk], [p[1] for p in yk], ls=":", color="#4a6fa5", lw=1, zorder=2)
    b = s["baslangic"]
    a = math.radians(b["aci_derece"])
    ax.add_patch(Rectangle((b["x"] - 0.26, b["y"] - 0.26), 0.52, 0.525, angle=0, facecolor="#ffd84d", edgecolor="#8a6d00",
                           lw=1, zorder=6))
    ax.add_patch(FancyArrow(b["x"], b["y"], 0.9 * math.cos(a), 0.9 * math.sin(a), width=0.06, head_width=0.25,
                            head_length=0.25, color="#8a6d00", zorder=7))
    for v in (vurgula or []):
        x0, y0, x1, y1 = v
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor="#d62728", lw=1.8, ls="-", zorder=8))
    ax.set_aspect("equal")
    W, H = h["boyut_m"]
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.grid(True, color="#eeeeee", lw=0.5, zorder=-1)
    ax.set_title(baslik or ad, fontsize=11, loc="left")
    return h, s


def _olcek(ax, x, y, L=2.0):
    ax.plot([x, x + L], [y, y], color="black", lw=3, solid_capstyle="butt", zorder=9)
    ax.text(x + L / 2, y + 0.15, "%g m" % L, ha="center", va="bottom", fontsize=8, zorder=9)


def _lejant(ax):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    el = [Line2D([], [], color=RENK["kapi_kapali"], lw=4, label="kapali kapi (0,95 x 0,09 m girinti)"),
          Line2D([], [], color=RENK["kapi_acik"], lw=4, label="acik kapi + oda"),
          Line2D([], [], color=RENK["kolon"], lw=4, label="kolon cikintisi"),
          Line2D([], [], color=RENK["yangin_dolabi"], lw=4, label="yangin dolabi"),
          Patch(facecolor="#cfe0f3", edgecolor="#1f77b4", label="dolap (kutu)"),
          Line2D([], [], color="#4a6fa5", ls="--", label="orta hat (robot yolu)"),
          Patch(facecolor="#ffd84d", edgecolor="#8a6d00", label="robot baslangici (520 x 525 mm)")]
    ax.legend(handles=el, loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=7, frameon=False)


OLCU = {"koridor_1": "2,0 x 30 m duz, sik kapi", "koridor_2": "3,5 x 12 m duz, 2 kolon + dolap",
        "koridor_3": "L, 2,4 m; kollar 16 m + 10 m", "koridor_4": "T, ana 2,6 x 22 m + 8 m yan kol",
        "koridor_5": "2,4 x 24 m duz (benzer cift A)", "koridor_6": "2,4 x 24 m duz (benzer cift B: 2 fark)"}


def ciz():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(GORSEL, exist_ok=True)
    for ad in KORIDORLAR:
        h = _oku(os.path.join(HARITALAR, ad + ".json"))
        W, H = h["boyut_m"]
        fig = plt.figure(figsize=(min(16, 1.2 + W * 0.42), 1.6 + H * 0.42 + 0.2), dpi=130)
        ax = fig.add_axes([0.06, 0.12, 0.72, 0.78])
        _ciz_eksen(ax, ad, "%s  -  %s  (ustten gorunum, harita cercevesi)" % (ad, OLCU[ad]))
        _olcek(ax, 0.3, 0.3)
        _lejant(ax)
        yol = os.path.join(GORSEL, ad + ".png")
        fig.savefig(yol, bbox_inches="tight")
        plt.close(fig)
        print(yol)
    # benzer çift karşılaştırması: aynı ölçek, x hizalı üst üste + fark bölgesinin yakın görünümü yan yana
    s6 = _oku(os.path.join(SAHNELER, "koridor_6.json"))
    dx, dy = s6["kaydirma_m"]
    kutu_kapi = (16.4 + dx, 2.4 + dy - 0.25, 18.15 + dx, 2.4 + dy + 0.2)
    kutu_dolap = (16.5 + dx, dy - 0.2, 17.5 + dx, dy + 0.35)
    fig = plt.figure(figsize=(15, 13.5), dpi=130, layout="constrained")
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.05])
    ax5 = fig.add_subplot(gs[0, :])
    ax6 = fig.add_subplot(gs[1, :])
    _ciz_eksen(ax5, "koridor_5", "koridor_5  (2,4 x 24 m)", vurgula=[kutu_kapi, kutu_dolap])
    _ciz_eksen(ax6, "koridor_6", "koridor_6  (2,4 x 24 m)  -  kirmizi cerceve: koridor_5'ten farkli yerler",
               vurgula=[kutu_kapi, kutu_dolap])
    for ax in (ax5, ax6):
        _olcek(ax, 0.3, 0.6)
    zx0, zx1, zy0, zy1 = 14.0 + dx, 20.5 + dx, dy - 0.6, 2.4 + dy + 0.6
    for i, ad in enumerate(("koridor_5", "koridor_6")):
        ax = fig.add_subplot(gs[2, i])
        _ciz_eksen(ax, ad, "%s yakin: x %.1f-%.1f" % (ad, zx0, zx1), vurgula=[kutu_kapi, kutu_dolap])
        ax.set_xlim(zx0, zx1)
        ax.set_ylim(zy0, zy1)
        _olcek(ax, zx0 + 0.2, zy0 + 0.15, 1.0)
    y_ust = 2.4 + dy
    fig.suptitle("Benzer cift koridor_5 / koridor_6 (ayni olcek, x hizali). Tek farklar (koridor_6):\n"
                 "(1) ust duvar 4. kapi +0,60 m: x %.2f-%.2f -> %.2f-%.2f (y = %.2f)   "
                 "(2) alt duvarda yangin dolabi 0,80 x 0,18 m: x %.2f-%.2f (y = %.2f)\n"
                 "Fark bolgesi orta hat boyunca s = %.2f-%.2f m (koridor boyunun %%%.1f'i); disinda geometri birebir ayni."
                 % (16.5 + dx, 17.45 + dx, 17.1 + dx, 18.05 + dx, y_ust, 16.6 + dx, 17.4 + dx, dy,
                    s6["benzer_cift"]["fark_bolgesi_s_m"][0], s6["benzer_cift"]["fark_bolgesi_s_m"][1],
                    100 * s6["benzer_cift"]["fark_bolgesi_orani"]), fontsize=11, x=0.02, ha="left")
    yol = os.path.join(GORSEL, "koridor_5_6_karsilastirma.png")
    fig.savefig(yol, bbox_inches="tight")
    plt.close(fig)
    print(yol)


# ------------------------------------------------------------------ doğrulama (mujoco)

def dogrula(adlar):
    for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), BURASI):
        if _y not in sys.path:
            sys.path.insert(0, _y)
    import dunya as D
    if not D.FIZIK_VAR:
        print("mujoco yok: %s" % D.FIZIK_HATA)
        return 2
    import gorunum3b as G3
    from sahte_esp32.harita import Harita
    tamam = True
    for ad in adlar:
        s = D.sahne_oku(ad)
        p = G3.Pencere(ad)                              # 3B pencerenin kendi kurulumu (görüntüleyici açılmadan)
        w = p.w
        h = p.harita
        bas_temas = w.temas_engel()
        x0, y0, _, yaw0, _, _ = w.poz()
        p.adim(5000)                                    # 5 s sanal: devreye alınmadı, sürüş yok
        x1, y1, z1, yaw1, _, _ = w.poz()
        temas = w.temas_engel()
        kayma = math.hypot(x1 - x0, y1 - y0)
        dyaw = abs(math.degrees(yaw1 - yaw0))
        # LiDAR düzlemi: orta hat boyunca her 0,5 m'de 360 ışın (1°), z = 0,10 / 0,20 / 0,30 m; hepsi bir yüzeye çarpmalı
        hatlar = [s.get("orta_hat", [])] + ([s["orta_hat_yan_kol"]] if s.get("orta_hat_yan_kol") else [])
        W, H = h.genislik, h.yukseklik
        en_cok = math.hypot(W, H) + 1.0
        kacan = kacan2 = n_isin = 0
        en_uzak = 0.0
        for hat in hatlar:
            for (ax_, ay_), (bx_, by_) in zip(hat, hat[1:]):
                L = math.hypot(bx_ - ax_, by_ - ay_)
                for k in range(int(L / 0.5) + 1):
                    px, py = ax_ + (bx_ - ax_) * k * 0.5 / L, ay_ + (by_ - ay_) * k * 0.5 / L
                    for z in (0.10, 0.20, 0.30):
                        for i in range(360):
                            a = math.radians(i)
                            r = w.isin([px, py, z], [math.cos(a), math.sin(a), 0.0], en_cok)
                            n_isin += 1
                            if r is None:
                                kacan += 1
                            else:
                                en_uzak = max(en_uzak, r[0])
                    for i in range(360):                # aynı ışınlar 2B haritada (sahte ESP32 sonar dünyası)
                        if h.isin(px, py, math.radians(i), en_cok) is None:
                            kacan2 += 1
        hp = Harita.dosyadan(s["harita"])
        ok = (not bas_temas) and (not temas) and kayma < 0.005 and dyaw < 0.5 and kacan == 0 and kacan2 == 0
        tamam = tamam and ok
        print("%-14s %s | geom %4d | baslangic temas %s | 5 s sonra temas %s, kayma %.2f mm, yaw %.3f der, z %.3f m | "
              "LiDAR isini 3B %d / kacan %d (en uzak %.1f m), 2B kacan %d | parca %d"
              % (ad, "TAMAM" if ok else "KALDI", w.m.ngeom, bas_temas, temas, kayma * 1000, dyaw, z1, n_isin, kacan,
                 en_uzak, kacan2, len(hp.parcalar)), flush=True)
    return 0 if tamam else 1


if __name__ == "__main__":
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    is_ = sys.argv[1] if len(sys.argv) > 1 else "uret"
    if is_ == "uret":
        uret()
    elif is_ == "ciz":
        ciz()
    elif is_ == "dogrula":
        sys.exit(dogrula(sys.argv[2:] or list(KORIDORLAR)))
    else:
        print(__doc__)
        sys.exit(2)
