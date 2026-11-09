# -*- coding: utf-8 -*-
"""F4c (P8.2): baski partileri Parti 0-4. Yalniz okur, FreeCAD istemez.
Girdi: planlama/y2/Y2b-baski.json (parca satirlari, parti alani `Y2b-baski.py` parti()), modul analizleri (kaynak anahtari, X2D),
tasarim/freecad/omuz/omuz-baski.json (omuz yonu), tasarim/freecad/test/ (kupon STL hacmi, m7-kupon-sonuc.json).
Cikti: planlama/d158/F4c-partiler.json ve F4c-partiler.md.      py -3 planlama/d158/F4c-partiler.py
Parti numaralari Y2b ile ayni (baski-listesi.md Ozet'i ile tutarli olsun diye); "basim sirasi" notlari (aku takozu one alinir) ayri.
"""
import json, os, re, struct

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(HERE, "..", ".."))
FC = os.path.join(KOK, "tasarim", "freecad")
Y2B = os.path.join(KOK, "planlama", "y2", "Y2b-baski.json")
X2D = (246.0, 246.0, 250.0)          # Bambu Lab X2D tabla (baski-listesi.md); olcu analizdeki baski yonunde
RHO, HIZ, PAY = 1.27, 10.0, 1.3       # kupon suresi: test/README.md yontemi (g/cm3, mm3/s, hareket payi)

# ---------------------------------------------------------------- Turkce gorunen ad / yon (kaynak ASCII; dogrulama katlayarak karsilastirir)
_TRK = {"govde": "gövde", "bandi": "bandı", "sag": "sağ", "gogus": "göğüs", "kapagi": "kapağı", "ust": "üst", "on": "ön",
        "seridi": "şeridi", "ekrani": "ekranı", "cercevesi": "çerçevesi", "tasiyici": "taşıyıcı", "govdesi": "gövdesi",
        "hoparlor": "hoparlör", "kabi": "kabı", "flansli": "flanşlı", "kelepcesi": "kelepçesi", "yuvasi": "yuvası",
        "egme": "eğme", "catali": "çatalı", "yukseltme": "yükseltme", "adaptoru": "adaptörü", "yuz": "yüz", "kabugu": "kabuğu",
        "tirnagi": "tırnağı", "flansi": "flanşı", "gobegi": "göbeği", "tupu": "tüpü", "aku": "akü", "yuzu": "yüzü",
        "kenari": "kenarı", "plakasi": "plakası", "duz": "düz", "flans": "flanş", "yukari": "yukarı", "acik": "açık",
        "avuc": "avuç", "alti": "altı", "havsalar": "havşalar", "kopru": "köprü", "dis": "dış", "tarafi": "tarafı"}


def trk(s):
    def r(m):
        w = m.group(0)
        t = _TRK.get(w.lower())
        if not t:
            return w
        return t[0].upper() + t[1:] if w[0].isupper() else t
    return re.sub(r"[A-Za-z]+", r, s)


def f(x, n=0):
    return ("%.*f" % (n, x)).replace(".", ",")


def aralik(v, n=0, b=1.0):
    a, c = f(v[0] / b, n), f(v[1] / b, n)
    return a if a == c else "%s–%s" % (a, c)


def isaretli(x, n=2):
    return "0" if abs(x) < 0.5 * 10 ** -n else ("+" if x > 0 else "−") + f(abs(x), n)


# ---------------------------------------------------------------- parca basina bagimlilik ve M6 montaj adimi (planlama/adim4/M6-montaj-sirasi.md §2)
# M6 tablosu 125 cm modelinden; 1,58 m'de gogus ekrani, QLED, uzatma bandi, hoparlor ve hub adimlari yok (proje-plani.md "M6 dayanagi notu").
META = {
    "Aku on takozu": ("Akü (K30) gelince ölçü teyidi", "4 (B1a)"),
    "Sonar tutucu sol": ("—", "16 (B7)"), "Sonar tutucu orta": ("—", "16 (B7)"), "Sonar tutucu sag": ("—", "16 (B7)"),
    "Govde alt bandi sag": ("Kupon B/C (ısıl gömme deliği)", "34 (F2)"), "Govde alt bandi sol": ("Kupon B/C", "34 (F2)"),
    "Govde uzatma bandi 1 sag": ("Kupon B/C", "34 (F2) ile; M6'da satırı yok"), "Govde uzatma bandi 1 sol": ("Kupon B/C", "34 (F2) ile; M6'da satırı yok"),
    "Govde uzatma bandi 2 sag": ("Kupon B/C", "34 (F2) ile; M6'da satırı yok"), "Govde uzatma bandi 2 sol": ("Kupon B/C", "34 (F2) ile; M6'da satırı yok"),
    "Govde orta bandi sag": ("Kupon B/C", "34 (F2)"), "Govde orta bandi sol": ("Kupon B/C", "34 (F2)"),
    "Gogus bandi sag": ("Kupon B/C; 11,6\" ekran cebi", "35 (F3)"), "Gogus bandi sol": ("Kupon B/C; 11,6\" ekran cebi", "35 (F3)"),
    "Omuz bandi sag": ("Kupon B/C", "36 (F4)"), "Omuz bandi sol": ("Kupon B/C", "36 (F4)"),
    "Arka servis kapagi": ("—", "F5 (son)"),
    "Ust arka servis kapagi": ("USB hub 4'lü (72 × 25 × 19) ölçüsü: hub takozu", "F5 (son); M6 §4 K4"),
    "Gogus ekrani cercevesi sag": ("11,6\" göğüs ekranı kasası (284,65 × 182,25)", "35 (F3) ile; M6'da 1,58 m adımı yok"),
    "Gogus ekrani cercevesi sol": ("11,6\" göğüs ekranı kasası (284,65 × 182,25)", "35 (F3) ile; M6'da 1,58 m adımı yok"),
    "Gogus ekrani VESA tasiyici": ("11,6\" göğüs ekranı VESA delikleri (yer ve derinlik doğrulanmadı, `arayuz.py:342`)", "35 (F3) ile; M6'da 1,58 m adımı yok"),
    "Hoparlor kabi on halka": ("8 Ω hoparlör (K36 stok, K6 yön); kap ölçüsü VARSAYIM", "34 (F2) öncesi, orta bant sağ; M6'da yok"),
    "Hoparlor kabi arka (flansli)": ("8 Ω hoparlör (K36, K6); VARSAYIM", "34 (F2) öncesi; M6'da yok"),
    "Hoparlor kelepcesi": ("8 Ω hoparlör (K36, K6); VARSAYIM", "34 (F2) öncesi; M6'da yok"),
    "S1 kaset govdesi sag": ("Kablo kalınlığı ≤ 1,4 mm (K1)", "41 (G4)"), "S1 kaset kapagi sag": ("—", "41 (G4)"),
    "S1 kaset govdesi sol": ("Kablo kalınlığı ≤ 1,4 mm (K1)", "41 (G4)"), "S1 kaset kapagi sol": ("—", "41 (G4)"),
    "Etek arka sag": ("E7 havalandırma yarıkları CAD'e; ana anahtar (M6 K7) + XT60 + H1 (K5)", "33 (F1)"),
    "Etek arka sol": ("E7 havalandırma yarıkları CAD'e; ana anahtar (M6 K7) + XT60 + H1 (K5)", "33 (F1)"),
    "Etek orta sag": ("E7 havalandırma kararı", "33 (F1)"), "Etek orta sol": ("E7 havalandırma kararı", "33 (F1)"),
    "Etek on sag": ("E7 havalandırma kararı", "33 (F1)"), "Etek on sol": ("E7 havalandırma kararı", "33 (F1)"),
    "Etek dolgu seridi arka": ("—", "33 (F1)"), "Etek dolgu seridi on": ("—", "33 (F1)"),
    "Etek servis kapagi H1 (sigorta kutusu)": ("—", "33 (F1) / F5 (M6 K5)"), "Etek servis kapagi H2 (ana sigorta)": ("—", "33 (F1) / F5 (M6 K6)"),
    "Servo yuvasi": ("MG996R gövdesi", "23 (E1a)"), "Rulman yuvasi": ("6808-2RS (kupon A)", "23 (E1a)"),
    "Boyun mili": ("Pan horn delik dizilimi", "26 (E2b)"), "Egme catali": ("Tilt horn delik dizilimi", "27 (E2c)"),
    "Boyun yukseltme adaptoru": ("—", "26–27 arası; M6'da satırı yok"),
    "Yuz kabugu (on) sag": ("QLED (K32) + K2 (P6.1)", "31 (E4)"), "Yuz kabugu (on) sol": ("QLED (K32) + K2 (P6.1)", "31 (E4)"),
    "Arka kafa kabugu sag": ("QLED (K32) + K2 (P6.1)", "31 (E4)"), "Arka kafa kabugu sol": ("QLED (K32) + K2 (P6.1)", "31 (E4)"),
    "Kafa iskeleti": ("QLED + kamera delikleri; K2 (P6.1)", "29 (E3a)"),
    "Ekran tirnagi ust sag": ("QLED kasa ölçüsü", "29 (E3a)"), "Ekran tirnagi ust sol": ("QLED kasa ölçüsü", "29 (E3a)"),
    "Ekran tirnagi alt sag": ("QLED kasa ölçüsü", "29 (E3a)"), "Ekran tirnagi alt sol": ("QLED kasa ölçüsü", "29 (E3a)"),
    "Dirsek catali": ("Dirsek horn delik dizilimi; kupon D1/D2", "44 (H0c)"), "On kol govdesi": ("MG996R gövdesi", "42 (H0a)"),
    "Bilek flansi": ("Bilek horn delik dizilimi", "46 (H0e)"), "El": ("—", "47 (H0f)"),
    "Omuz yuvasi": ("DS3235 gövdesi, çekiç somun", "19 (D1a)"), "Rulman kapagi": ("6808-2RS (kupon A)", "20 (D1b)"),
    "Omuz gobegi": ("S1 horn delik dizilimi; kök yarıçapı r 1,5 F6a'da uygulandı (K39 DS3235 düşme ölçümü açık)", "37–38 (G0, G1)"),
    "S1 kablo tamburu": ("Göbekle birlikte", "37 (G0)"), "Kol catali": ("S2 horn delik dizilimi", "40 (G3)"),
    "Ust kol tupu": ("Kupon E (tüp–pim geçmesi)", "40 (G3)"),
}
# destek notu (kaynak: analiz destek_sorun / omuz-baski; 03.11 listesindeki tarifler)
DESTEK = {
    "Gogus bandi sag": "cep üst kenarı, köprü 158 mm", "Gogus bandi sol": "cep üst kenarı, köprü 146 mm",
    "Ust arka servis kapagi": "analizde z 2,5'te 197 cm², nedeni açık (günlük)",
    "Gogus ekrani VESA tasiyici": "arka flanş (28 katman)",
    "Yuz kabugu (on) sag": "dikiş dili (16 mm şerit, ~1,25 mm konsol; karar 29.10)",
    "Arka kafa kabugu sag": "dikiş dili (16 mm şerit, ~1,25 mm konsol; karar 29.10)",
    "Omuz yuvasi": "manşon içi + S1 penceresi", "Omuz gobegi": "flanş altı + diş (5,7 g)",
    "S1 kablo tamburu": "+x dudak altı", "Kol catali": "horn kulağı",
}
PARTI = {
    0: dict(ad="Tolerans kuponları", ne_zaman="İlk gün (S'den önce)",
            bagimlilik="Kupon STL'leri hazır. Değerlendirme için 6808-2RS, 625ZZ, M3/M5 ısıl gömme somun ve kupon D vidaları elde (K29 erken alım; K31 insert varyantı)",
            montaj="Sonuç CAD'e (arayuz.INSERT_DELIK, rulman yuvaları, GECME) → STL dışa aktarma (FreeCAD, açık iş) → Parti 1",
            takvim="S = 16.11 için 9–10.11 (proje-plani.md, Durum A)"),
    1: dict(ad="Hemen", ne_zaman="Hemen (Parti 0 sonucu CAD'e girip STL çıkınca)",
            bagimlilik="Parti 0 sonucu + STL dışa aktarma. Satın alınan parçaya bağlı 7 satır partinin sonunda, ilgili kalem gelip ölçülünce basılır: üst arka kapak (USB hub), hoparlör kabı ve kelepçesi (8 Ω hoparlör, K36/K6), göğüs ekranı çerçevesi sağ/sol ve VESA taşıyıcı (11,6\" göğüs ekranı; VESA delik yeri doğrulanmadı, `arayuz.py:342`; F4c-kontrol B-2)",
            montaj="16 (sonar), 20 (rulman kapağı), 34–36 (bantlar, göğüs ekranı), 40 (üst kol tüpü), F5 (kapaklar)",
            takvim="≈ S−0,5 → S+1,5; akü takozu (Parti 4) bu partinin arasında basılır"),
    2: dict(ad="Servo ve horn gelip ölçülünce", ne_zaman="Servo ve horn gelip kumpasla ölçülünce",
            bagimlilik="DS3235, MG996R, 25T horn (teslim S+1); omuz göbeği kök yarıçapı r 1,5 F6a'da uygulandı (K39 DS3235 düşme ölçümü açık); S1 kaseti kablo kalınlığı (K1)",
            montaj="19–28 (omuz yuvası, boyun), 37–47 (göbek, kol, dirsek, el), 41 (S1 kaseti)",
            takvim="≈ S+1,5 → S+2,3"),
    3: dict(ad="10,1\" QLED yüz ekranı gelip ölçülünce", ne_zaman="QLED gelip ölçülünce",
            bagimlilik="10,1\" QLED (K32: hocadan mı satın alma mı), K2 (AI HAT / boss, P6.1'de kafa modeline)",
            montaj="29–31 (kafa içi, kafa → tilt hornu, kafa kabukları)", takvim="≈ S+2,3 → S+2,8"),
    4: dict(ad="Etek tasarım kararından sonra (M6 CAD)", ne_zaman="E7 havalandırma CAD'e girince; akü takozu akü gelince",
            bagimlilik="E7 etek havalandırma yarıkları (elektrik.md:499); akü (K30) → akü takozu",
            montaj="33 (etek, H1/H2), 4 (akü takozu, öne alınır)", takvim="≈ S+2,8 → S+4–4,5"),
}
ONE_AL = {"Aku on takozu": "Parti 1 arasında basılır (M6 adım 4 taban aşamasında lazım; proje-plani.md kritik yol 4–5)"}
# Parti 1'in sonuna: satin alinan parcaya bagli satirlar (F4c-kontrol B-2); parti numarasi degismez, sirada sona alinir
SONA_NOT = "Parti 1'in sonunda; ilgili kalem gelip ölçülünce basılır"
SONA = ("Ust arka servis kapagi", "Hoparlor kabi on halka", "Hoparlor kabi arka (flansli)", "Hoparlor kelepcesi",
        "Gogus ekrani cercevesi sag", "Gogus ekrani cercevesi sol", "Gogus ekrani VESA tasiyici")

# ---------------------------------------------------------------- Parti 0: kuponlar (test/README.md, m7-kupon-sonuc.json, baski-listesi 03.11 tablosu)


def stl_hacim_cm3(yol):
    b = open(yol, "rb").read()
    n = struct.unpack("<I", b[80:84])[0]
    v = 0.0
    for i in range(n):
        a = struct.unpack("<12f", b[84 + i * 50:84 + i * 50 + 48])
        p, q, r = a[3:6], a[6:9], a[9:12]
        v += (p[0] * (q[1] * r[2] - q[2] * r[1]) - p[1] * (q[0] * r[2] - q[2] * r[0]) + p[2] * (q[0] * r[1] - q[1] * r[0])) / 6.0
    return abs(v) / 1000.0


def sure_sa(g):
    return g / RHO * 1000.0 / HIZ * PAY / 3600.0


def kuponlar():
    T = os.path.join(FC, "test")
    m7 = {k["ad"]: k for k in json.load(open(os.path.join(T, "m7-kupon-sonuc.json"), encoding="utf-8"))["kuponlar"]}
    a100 = round(stl_hacim_cm3(os.path.join(T, "stl", "kupon-a-rulman-O52.stl")) * RHO, 1)
    b100 = round(stl_hacim_cm3(os.path.join(T, "stl", "kupon-b-yuva-mil-somun.stl")) * RHO, 1)
    c, d1, d2, e = (m7["kupon-c-isil-gomme-L1"], m7["kupon-d1-kelepce-kesiksiz"], m7["kupon-d2-kelepce-bosaltmali"], m7["kupon-e-tup-halkasi"])
    K = [
        ("A", "kupon-a-rulman-O52.stl", "PETG-CF", (a100, a100), "6808-2RS dış bileziği: Ø52,0 / 52,1 / 52,2 / 52,3 (omuz rulman kapağı, kafa rulman yuvası)", "STL hacmi × 1,27 (%100; tahmini değer yok)", False),
        ("B", "kupon-b-yuva-mil-somun.stl", "PETG-CF", (60.0, b100), "625ZZ Ø16,0…16,3 · Ø40 mil Ø39,8…40,1 · M3 Ø3,8…4,1 / M5 Ø6,2…6,6 dikey (L + 0,5)", "alt 60 g: 03.11 listesi (kaynağı yazılmamış); üst STL %100", False),
        ("B", "kupon-b-yuva-mil-somun.stl", "PETG", (60.0, b100), "aynı kupon beyaz PETG'de (kabuk ısıl gömme delikleri)", "aynı", False),
        ("C", "kupon-c-isil-gomme-L1.stl", "PETG-CF", (c["kutle_tahmini_g"], c["kutle_100_g"]), "Isıl gömme L + 1: M3 Ø3,9…4,1, M5 Ø6,2…6,6, yatay + dikey", "m7-kupon-sonuc.json", False),
        ("C", "kupon-c-isil-gomme-L1.stl", "PETG", (c["kutle_tahmini_g"], c["kutle_100_g"]), "aynı kupon beyaz PETG'de", "m7-kupon-sonuc.json", False),
        ("D1", "kupon-d1-kelepce-kesiksiz.stl", "PETG-CF", (d1["kutle_tahmini_g"], d1["kutle_100_g"]), "Dirsek kelepçesi (çatal dilimi), kesiksiz", "m7-kupon-sonuc.json", False),
        ("D2", "kupon-d2-kelepce-bosaltmali.stl", "PETG-CF", (d2["kutle_tahmini_g"], d2["kutle_100_g"]), "Dirsek kelepçesi, kökte boşaltmalı (D1 geçerse yalnız karşılaştırma)", "m7-kupon-sonuc.json", True),
        ("E", "kupon-e-tup-halkasi.stl", "PETG", (e["kutle_tahmini_g"], e["kutle_100_g"]), "Üst kol tüpü halkası (tüp–pim / tüp–bilezik geçmesi)", "m7-kupon-sonuc.json", False),
    ]
    out = []
    for kod, stl, mlz, g, ne, kay, kosullu in K:
        out.append(dict(kod=kod, stl="tasarim/freecad/test/stl/" + stl, malzeme=mlz, g=[g[0], g[1]], sa=[round(sure_sa(g[0]), 3), round(sure_sa(g[1]), 3)],
                        denenen=ne, kutle_kaynak=kay, kosullu=kosullu))
    return out


# ---------------------------------------------------------------- kaynak anahtari ve X2D


def kaynaklar():
    """(modul, ad) -> (kaynak anahtari, sigar, baski yonundeki olcu)"""
    d = {}
    for mod in ("taban", "kabuk", "kafa", "dirsek"):
        for i, p in enumerate(json.load(open(os.path.join(FC, mod, mod + "-analiz.json"), encoding="utf-8"))["baski"]):
            d[(mod, p["ad"])] = ("%s/baski[%d]" % (mod, i), bool(p.get("sigar")), p["olcu"], p.get("yon"))
    ob = json.load(open(os.path.join(FC, "omuz", "omuz-baski.json"), encoding="utf-8"))
    for i, p in enumerate(ob["parcalar"]):
        y = p["yonler"][p["secilen_yon"]]
        ty = re.sub(r"(\d)\.(\d)", r"\1,\2", re.sub(r"\.0\b", "", y["tabla_yuzu"].split(" (")[0]))
        d[("omuz", p["ad"])] = ("omuz-baski/parcalar[%d]" % i, bool(y.get("sigar")), y["olcu"], "%s: %s" % (p["secilen_yon"], ty))
    return d


def x2d_sigar(olcu):
    return olcu[0] <= X2D[0] and olcu[1] <= X2D[1] and olcu[2] <= X2D[2]


def satirlar():
    Y = json.load(open(Y2B, encoding="utf-8"))
    K = kaynaklar()
    out = []
    for i, s in enumerate(Y["satirlar"]):
        key, sigar, olcu_b, yon = K[(s["modul"], s["ad"])]
        bagli, adim = META[s["ad"]]
        out.append(dict(y2b=i, modul=s["modul"], ad=s["ad"], ad_tr=trk(s["ad"]), adet=s["adet"], olcu=s["olcu"], g=s["g"], sa=s["sa"],
                        malzeme="PETG-CF" if s["cf"] else "PETG", destekli=not s["desteksiz"], destek_not=DESTEK.get(s["ad"], ""),
                        yon=trk(yon or s.get("yon") or ""), kaynak=key, x2d=bool(sigar and x2d_sigar(olcu_b)), olcu_baski=olcu_b,
                        parti=s["parti"], bagli=bagli, montaj_adimi=adim, basim_notu=ONE_AL.get(s["ad"], "") or (SONA_NOT if s["ad"] in SONA else "")))
    return Y, out


def topla(rows):
    t = dict(adet=0, g=[0.0, 0.0], sa=[0.0, 0.0], petg_g=[0.0, 0.0], cf_g=[0.0, 0.0])
    for r in rows:
        t["adet"] += r["adet"]
        for i in (0, 1):
            t["g"][i] += r["adet"] * r["g"][i]
            t["sa"][i] += r["adet"] * r["sa"][i]
            t["cf_g" if r["malzeme"] == "PETG-CF" else "petg_g"][i] += r["adet"] * r["g"][i]
    for k in ("g", "sa", "petg_g", "cf_g"):
        t[k] = [round(x, 3) for x in t[k]]
    return t


def takvim(partiler, haftalik):
    """Durum A sirasi (proje-plani.md): Parti 1 S-0,5'te baslar, Parti 2 servo S+1'de gelir; tek yazici, partiler sirayla."""
    t, out = -0.5, {}
    for k in (1, 2, 3, 4):
        if k == 2:
            t = max(t, 1.0)          # servo + horn S+1'de gelir, olculur
        sa = partiler[k]["toplam"]["sa"][1] + (1.5 if k == 1 else 0.0) - (1.5 if k == 4 else 0.0)   # aku takozu Parti 1 arasinda
        t += sa / haftalik
        out[k] = round(t, 2)
    return out


def main():
    Y, rows = satirlar()
    P = {}
    for k in (1, 2, 3, 4):
        rr = [r for r in rows if r["parti"] == k]
        rr = [r for r in rr if r["ad"] not in SONA] + [r for r in rr if r["ad"] in SONA]
        P[k] = dict(PARTI[k], parti=k, parcalar=rr, toplam=topla(rr))
        if k == 1:
            P[k]["sona_birakilan"] = dict(topla([r for r in rr if r["ad"] in SONA]), parcalar=[r["ad_tr"] for r in rr if r["ad"] in SONA], not_=SONA_NOT)
    kup = kuponlar()
    k0 = dict(adet=len(kup), g=[round(sum(x["g"][i] for x in kup), 1) for i in (0, 1)], sa=[round(sum(x["sa"][i] for x in kup), 2) for i in (0, 1)],
              cf_g=[round(sum(x["g"][i] for x in kup if x["malzeme"] == "PETG-CF"), 1) for i in (0, 1)],
              petg_g=[round(sum(x["g"][i] for x in kup if x["malzeme"] == "PETG"), 1) for i in (0, 1)],
              d2siz_sa=[round(sum(x["sa"][i] for x in kup if not x["kosullu"]), 2) for i in (0, 1)])
    P[0] = dict(PARTI[0], parti=0, kuponlar=kup, toplam=k0,
                omuz_disi_koku="Kupon yok. K39 (varsayılan d): kök +x iç köşesi r 1,5 yay F6a'da uygulandı (P6.1); öneri: göbeğin kendisi Parti 2'nin ilk işi, S2 5°'te sentille 0,3 mm boşluk kontrolü (F2-gunluk madde 9) + DS3235 düşme ölçümü (K39)")
    liste = topla(rows)
    y2 = Y["toplam"]
    kontrol = dict(adet=liste["adet"] == y2["adet"],
                   g=all(abs(liste["g"][i] - y2["g"][i]) < 1e-6 for i in (0, 1)),
                   sa=all(abs(liste["sa"][i] - y2["sa"][i]) < 1e-6 for i in (0, 1)),
                   cf=all(abs(liste["cf_g"][i] - y2["cf_g"][i]) < 1e-6 for i in (0, 1)),
                   parti_esit=all(P[k]["toplam"]["adet"] == y2["parti"][str(k)]["adet"] and
                                  all(abs(P[k]["toplam"]["g"][i] - y2["parti"][str(k)]["g"][i]) < 1e-6 and abs(P[k]["toplam"]["sa"][i] - y2["parti"][str(k)]["sa"][i]) < 1e-6 for i in (0, 1))
                                  for k in (1, 2, 3, 4)),
                   her_parca_bir_partide=sorted(r["y2b"] for k in (1, 2, 3, 4) for r in P[k]["parcalar"]) == list(range(len(Y["satirlar"]))))
    tk = {"32": takvim(P, 32.0), "40": takvim(P, 40.0), "plan_A": {1: 1.5, 2: 2.3, 3: 2.8, 4: 4.5}}
    out = dict(tarih="2026-11-09", kaynak="planlama/y2/Y2b-baski.json (Y2b-baski.py); parti alanı Y2b parti()", partiler={str(k): P[k] for k in (0, 1, 2, 3, 4)},
               liste_toplam=liste, y2b_toplam={k: y2[k] for k in ("adet", "g", "sa", "petg_g", "cf_g")}, kontrol=kontrol,
               takvim_hafta_sonu=tk, takvim_not="S'ye göre hafta; tek yazıcı; Parti 2 en erken S+1; akü takozu (1,5 sa) Parti 1 arasında")
    json.dump(out, open(os.path.join(HERE, "F4c-partiler.json"), "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    open(os.path.join(HERE, "F4c-partiler.md"), "w", encoding="utf-8", newline="\n").write(md(out))
    print("kontrol", kontrol)
    print("liste", liste)
    print("parti0", k0)
    print("takvim", tk)
    return 0 if all(kontrol.values()) else 1


# ---------------------------------------------------------------- markdown


def md(o):
    P = {int(k): v for k, v in o["partiler"].items()}
    L = o["liste_toplam"]
    k0 = P[0]["toplam"]
    s = ["# F4c baskı partileri (Parti 0–4) — 09.11.2026", "",
         "Üreten: `py -3 planlama/d158/F4c-partiler.py` (bu dosya ve `F4c-partiler.json`). Parça satırları `planlama/y2/Y2b-baski.json`'dan,",
         "parti numaraları `Y2b-baski.py` `parti()` ile aynı (yani `planlama/baski-listesi.md` Özet'i ile aynı). Bağımlılık ve montaj adımı sütunları",
         "elle (`F4c-partiler.py` `META`); montaj adımları `planlama/adim4/M6-montaj-sirasi.md` §2 (125 cm tablosu; 1,58 m'de göğüs ekranı,",
         "QLED, uzatma bandı, hoparlör ve hub adımları henüz yok). Toplamların doğrulaması: `py -3 planlama/d158/F4c-dogrula.py`.", "",
         "## Özet", "",
         "| Parti | Ne zaman | Adet | PETG | PETG-CF | Toplam | Süre | Durum A takvimi (`proje-plani.md`) |", "|---|---|---|---|---|---|---|---|"]
    s.append("| Parti 0 | %s | %d baskı (%d kupon) | %s kg | %s kg | %s kg | ≈ %s sa | %s |" % (
        P[0]["ne_zaman"], k0["adet"], 6, aralik(k0["petg_g"], 2, 1000), aralik(k0["cf_g"], 2, 1000), aralik(k0["g"], 2, 1000), aralik(k0["sa"], 1), P[0]["takvim"]))
    for k in (1, 2, 3, 4):
        t = P[k]["toplam"]
        s.append("| Parti %d | %s | %d | %s kg | %s kg | %s kg | ≈ %s sa | %s |" % (k, P[k]["ne_zaman"], t["adet"], aralik(t["petg_g"], 2, 1000),
                                                                           aralik(t["cf_g"], 2, 1000), aralik(t["g"], 2, 1000), aralik(t["sa"], 1), P[k]["takvim"]))
    s.append("| **Parti 1–4** | | **%d** | **%s kg** | **%s kg** | **%s kg** | **≈ %s sa** | |" % (
        L["adet"], aralik(L["petg_g"], 2, 1000), aralik(L["cf_g"], 2, 1000), aralik(L["g"], 2, 1000), aralik(L["sa"], 1)))
    kt = o["kontrol"]
    s += ["", "Kontrol (betik): Parti 1–4 toplamı = `Y2b-baski.json` `toplam` (adet %s, g %s, sa %s, PETG-CF %s); her parti Y2b `toplam.parti` ile aynı: %s;"
          " her parça tam bir partide: %s. Kuponlar parça toplamına katılmaz." % tuple("evet" if kt[x] else "**HAYIR**" for x in ("adet", "g", "sa", "cf", "parti_esit", "her_parca_bir_partide")), ""]
    # Parti 0
    s += ["## Parti 0 — tolerans kuponları", "", "Bağımlılık: " + P[0]["bagimlilik"] + ".", "Sonrası: " + P[0]["montaj"] + ".", "",
          "| Kupon | STL | Malzeme | Ne denenir | Filament (g) | Süre (sa) | Kütle kaynağı |", "|---|---|---|---|---|---|---|"]
    for x in P[0]["kuponlar"]:
        s.append("| %s%s | `%s` | %s | %s | %s | %s | %s |" % (x["kod"], " (koşullu)" if x["kosullu"] else "", os.path.basename(x["stl"]), x["malzeme"], x["denenen"],
                                                        aralik(x["g"], 1), aralik(x["sa"], 2), x["kutle_kaynak"]))
    s += ["| **Toplam** | | | | **%s** | **%s** | PETG %s g, PETG-CF %s g |" % (aralik(k0["g"], 1), aralik(k0["sa"], 2), aralik(k0["petg_g"], 1), aralik(k0["cf_g"], 1)), "",
          "Süre `tasarim/freecad/test/README.md` yöntemiyle: hacim (g / 1,27) ÷ 10 mm³/s × 1,3; alt değer tahmini kütle, üst değer %%100 dolu. "
          "Dilimleyicinin verdiği esastır. D2 basılmazsa (D1 geçerse) ≈ %s sa. `proje-plani.md`'deki \"≈ 3 sa\" yalnız M7 kuponları (C bir kez, D1, D2, E);"
          " A, B ve iki malzemeli B/C eklenince ≈ %s sa (tahmini kütleyle)." % (aralik(k0["d2siz_sa"], 1), f(k0["sa"][0], 1)), "",
          "**Isıl gömme (K31 açık; A/B/C seçeneğine göre kupon):**", "",
          "| K31 seçeneği | Delik (satıcı kuralı, `F8a-siparis.md` §4.1) | Kupon B / C | Parti 0'a etkisi |", "|---|---|---|---|",
          "| A: Rhino ID3 OD4 L4 (önerilen varsayılan) | Ø3,8–3,9 | B'de Ø3,8 / 3,9 (dikey), C'de Ø3,9 damla | Kupon değişmez; C'nin derinliği 6,7 (L 5,7 + 1) L4 için fazla ama deneme için engel değil |",
          "| B: Rhino ID3 OD5 L6 | Ø4,8–4,9 | Uymaz (Ø3,8–4,1) | B ve C yeniden üretilir (`arayuz.INSERT`, FreeCAD); A, D1, D2, E beklemeden basılır, B/C gecikir |",
          "| C: ruthex RX-M3x5.7 | Ø4,0–4,2 | B'de Ø4,0 / 4,1, C'de Ø4,0 / 4,1 | Kupon değişmez; tedarik takvime yetişmez (K31) |",
          "| M5: Rhino ID5 OD7 L7 | Ø6,7–6,8 | Uymaz (Ø6,2–6,6) | M5 delikleri büyütülür ya da başka ürün (K31, önerilen varsayılan yok) |", "",
          "**Omuz dişi kökü:** " + P[0]["omuz_disi_koku"] + ".", ""]
    # Parti 1-4
    for k in (1, 2, 3, 4):
        t = P[k]["toplam"]
        s += ["## Parti %d — %s" % (k, P[k]["ad"]), "",
              "%d adet · %s kg (PETG %s, PETG-CF %s) · ≈ %s sa. Bağımlılık: %s. Montaj (M6): %s. Takvim: %s." % (
                  t["adet"], aralik(t["g"], 2, 1000), aralik(t["petg_g"], 2, 1000), aralik(t["cf_g"], 2, 1000), aralik(t["sa"], 1), P[k]["bagimlilik"], P[k]["montaj"], P[k]["takvim"]), ""]
        if "sona_birakilan" in P[k]:
            z = P[k]["sona_birakilan"]
            s += ["**Partinin sonuna bırakılan (satın alınan parçaya bağlı):** %d adet, %s g (PETG-CF %s g), ≈ %s sa: %s. Tablonun son satırları;"
                  " parça gelip kumpasla ölçülmeden basılmaz, ölçü tutmazsa CAD düzeltilir (P6.1). Yanlış basılan VESA taşıyıcı KT-F4c-1'deki dar"
                  " PETG-CF payını yer." % (z["adet"], aralik(z["g"], 1), aralik(z["cf_g"], 1), aralik(z["sa"], 2), ", ".join(z["parcalar"])), ""]
        s += [
              "| Modül | Parça | Adet | Malzeme | g/adet | sa/adet | Bağlı olduğu kalem | M6 adımı | Not |", "|---|---|---|---|---|---|---|---|---|"]
        for r in P[k]["parcalar"]:
            s.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s |" % (r["modul"], r["ad_tr"], r["adet"], r["malzeme"], aralik(r["g"]), aralik(r["sa"], 2),
                                                                     r["bagli"], r["montaj_adimi"], r["basim_notu"] or ""))
        s.append("")
    tk = o["takvim_hafta_sonu"]
    s += ["## Takvim kontrolü (paylaşımlı yazıcı, haftada 32–40 sa)", "",
          "Durum A sırası: Parti 1 S−0,5'te başlar, Parti 2 en erken S+1 (servo gelir), partiler tek yazıcıda sırayla; akü takozu Parti 1 arasında.",
          "Değerler S'ye göre hafta (parti bitişi, üst süreyle).", "",
          "| Parti | 40 sa/hf | 32 sa/hf | `proje-plani.md` (Durum A) | Fark (32 sa/hf) |", "|---|---|---|---|---|"]
    for k in (1, 2, 3, 4):
        a, b, p = tk["40"][k], tk["32"][k], tk["plan_A"][k]
        s.append("| %d | S+%s | S+%s | %s | %s hf (≈ %s gün) |" % (k, f(a, 2), f(b, 2), "S+4–4,5" if k == 4 else "S+" + f(p, 1),
                                                            isaretli(b - p), isaretli((b - p) * 7, 0)))
    s += ["", "Okuma: haftada 40 sa'te her parti plandan önce biter. 32 sa'te ara bitişler 1–2 gün kayar (Parti 1 ≈ S+%s, Parti 2 ≈ S+%s, Parti 3 ≈ S+%s),"
          " baskının sonu (≈ S+%s) plandaki ≈ S+4,5 ile aynı kalır; aşama 8'in ilk adımları (S+3) Parti 2'yi beklemez. Plan Parti 1'i ≈ 34,5 sa/hf ile hesaplamış" % (
              f(tk["32"][1], 2), f(tk["32"][2], 2), f(tk["32"][3], 2), f(tk["32"][4], 2)) +
          " (69 sa / 2 hf). Asıl risk sayı değil bağımlılık: Parti 1 STL dışa aktarmaya (FreeCAD, açık iş), Parti 2'nin göbeği DS3235 düşme ölçümüne (K39; kök yarıçapı F6a'da uygulandı),"
          " Parti 3 QLED'e (K32) ve K2'ye (P6.1), Parti 4 E7 havalandırma CAD'ine bağlı. Öneriler günlükte (`F4c-gunluk.md`), `proje-plani.md` değişmedi.", ""]
    return "\n".join(s)


if __name__ == "__main__":
    raise SystemExit(main())
