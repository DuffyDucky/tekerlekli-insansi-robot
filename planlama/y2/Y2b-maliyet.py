# -*- coding: utf-8 -*-
"""Y2b (29 Ekim 2026): planlama/maliyet.json'i 1,65 m ana tasarima gore gunceller. BIR KEZ kosar (ikinci kosuda durur).
Kaynaklar: tasarim/freecad/montaj/robot-bom.csv (1.073 parca), planlama/y2/Y2b-baski.json (63 baski parcasi),
tasarim/freecad/taslak-170/maliyet-farki.md + kol-analiz/NOTLAR.md (DS3235), dirsek/dirsek-analiz.json kablo.s1_boy (uzatma),
main: raporlar/mikrofon-secimi.md (Efe, 26 Ekim: XVF3800 + yonlu mikrofon), CNC Marketi sigma sayfasi (29 Ekim 2026).
V3 satirlari = guncel ana tasarim; tasarima ozgu eski satirlar silinmez, ver "v1,v2" ile arsive alinir (demo V1/V2).
  py -3 planlama/y2/Y2b-maliyet.py   ardindan   py -3 planlama/adim5/maliyet_toplam.py ; python tasarim/cad/demo_uret.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
YOL = os.path.join(HERE, "..", "maliyet.json")
d = json.load(open(YOL, encoding="utf-8"))
K = d["kalemler"]
if any(it.get("adim") == "Y2b" for it in K):
    sys.exit("maliyet.json zaten Y2b ile guncel; cikiliyor")


def bul(ad, model_bas=None, ver=None):
    r = [i for i, it in enumerate(K) if it["ad"] == ad and (model_bas is None or it["model"].startswith(model_bas))
         and (ver is None or it.get("ver") == ver)]
    assert len(r) == 1, (ad, model_bas, ver, r)
    return r[0]


def guncelle(ad, model_bas=None, ver=None, **alan):
    it = K[bul(ad, model_bas, ver)]
    it.update(alan)
    it["adim"] = "Y2b"
    return it


def arsivle_ve_yeni(ad, model_bas, yeni):
    i = bul(ad, model_bas)
    K[i]["ver"] = "v1,v2"
    y = dict(K[i]); y.pop("alt", None); y.update(yeni); y["ver"] = "v3"; y["adim"] = "Y2b"
    K.insert(i + 1, y)
    return y


def sil(ad, model_bas=None, ver=None):
    del K[bul(ad, model_bas, ver)]


d["tarih"] = "2026-10-29"

# --- servo: DS3235 (4 + 1 yedek)
DS = dict(model="DS3235, 35 kg·cm (7,4 V) / 32 (6 V), 180°", tl=1171.5, satici="Robocombo",
          url="https://www.robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4148", durum="dogrulandi", stok="var",
          not_="1,65 m (kol ×1,25). Fiyat 24 Ekim 2026: indirimli 1.171,50, liste 1.255, stok 134 (taslak-170/kol-analiz/NOTLAR.md). "
               "Açıklamada 'RDS3235' geçiyor: model ve kulak deliği satıcıya sorulacak")
DS["not"] = DS.pop("not_")
arsivle_ve_yeni("Omuz servosu", "DS3218MG", dict(DS, adet=4))
arsivle_ve_yeni("Yedek omuz servosu", "DS3218MG", dict(DS, ad="Yedek omuz servosu", adet=1))

# --- sigma: 1,65 m direk 1.185,5 tek parca
arsivle_ve_yeni("Sigma profil", "40 × 40", dict(
    model="40 × 40 ağır, kanal 10; satıcı ölçüye keser (ücretsiz): 1.185,5 · 2 × 500 · 200 · 3 × 190 mm = 2.955,5 mm (10 cm'ye yuvarlanır → 3,0 m)",
    adet=3.0, birim="m", tl=934.08, durum="dogrulandi", stok="var",
    not_="1,65 m: gövde direği 1.185,5 tek parça. Fiyat 29 Ekim 2026 (metre 934,08, liste 1.514,70), stok 120,9 m, tek parça ≤ 6.000 mm, "
         "2.500 mm üstü ambarla. Kendimiz kesersek 2 m + 2 × 1 m stok (iskelet-analiz.json kesim planı, artık 113,5 / 99 / 805)"))
K[bul("Sigma profil", ver="v3")]["not"] = K[bul("Sigma profil", ver="v3")].pop("not_")

# --- goguste Nextion yok; yuz ekrani 10,1" (hoca verecek); 10" kafada akrilik yuz paneli yok
sil("Göğüs ekranı", "Nextion")
sil("Yüz paneli", "3 mm parlak siyah akrilik")
i7 = bul("Yüz ekranı", "Waveshare 7")
K[i7]["ver"] = "v1"
K.insert(i7 + 1, dict(g="ses", ad="Yüz ekranı", model="Waveshare 10.1\" HDMI LCD (B) kasalı, 1280 × 800 IPS, kapasitif (CAD'deki tahmini model)",
                      adet=1, tl=12424.5, satici="Robotsepeti",
                      url="https://www.robotsepeti.com/waveshare-101inch-dokunmatik-lcd-b-kasali-1280x800-ips-ekran", elde=True,
                      durum="dogrulandi", stok="var", ver="v3", adim="Y2b",
                      not_="1,65 m kafa 10,1\". Hoca verecek (21 Ekim 2026): 'elimizdekiler düş' ile toplamdan çıkar; verilmezse bu fiyat "
                           "(2 Ekim 2026, V2 kaydı). Ekran gelince ölçülür (baskı Parti 3). 5 V ≈ 0,75 A, Pi USB-A'dan"))
K[i7 + 1]["not"] = K[i7 + 1].pop("not_")

# --- mikrofon: Efe karari (26 Ekim 2026)
im = bul("Mikrofon", "ReSpeaker Lite")
K[im]["ver"] = "v1,v2"
K.insert(im + 1, dict(g="ses", ad="Mikrofon dizisi", model="Seeed reSpeaker XVF3800 USB 4-Mic Array, kasalı, XIAO'suz (AEC, NS, hüzme, yön; UAC2)",
                      adet=1, tl=5500.0, satici="RobotShop EU (65,88 €, ön sipariş; ithal)",
                      url="https://eu.robotshop.com/products/respeaker-xmos-xvf3800-w-case-ai-powered-4-mic-array-for-clear-voice-in-noise",
                      durum="tahmini", stok="belirsiz", ver="v3", adim="Y2b",
                      **{"not": "Efe kararı 26 Ekim 2026 (main: raporlar/mikrofon-secimi.md). Ürün ≈ 3.670 TL; kargo ve gümrükle ≈ 5.500 TL "
                                "(tahmini). Türk satıcıda yok. Almadan önce Pi 5 sıcak yeniden başlatma hatası ve akımı doğrulanmalı. CAD'de yeri yok"}))
K.insert(im + 2, dict(g="ses", ad="Yönlü mikrofon kolu", model="Kardioid shotgun mikrofon (ör. Boya BY-MM1) + USB ses kartı + kürk rüzgâr kılıfı",
                      adet=1, tl=2000.0, satici="n11 (BY-MM1 1.334,11 TL) + tahmin", url="", durum="tahmini", stok="belirsiz", ver="v3", adim="Y2b",
                      **{"not": "Efe kararı 26 Ekim 2026: XVF3800 ile karşılaştırma kolu, ikisi de alınacak. Ses kartı ve kılıf fiyatı "
                                "doğrulanmadı; toplam ≈ 2.000 TL (tahmini, mikrofon-secimi.md). Robottaki yeri belirsiz"}))

# --- kablo: 1,65 m uzatma boylari
guncelle("Servo uzatma kablosu", model="22 AWG, 3 damar, JR, 100 cm (10 hat: kollar ≈ 11,2 m + S1 × 2, pan, tilt ≈ 5,8 m)", adet=19,
         **{"not": "Y2b (1,65 m): dirsek-analiz.json s1_boy dirsek / bilek 1.926 mm, S2 (göbek eki B10) ≈ 1.770 → kol başına 5,62 m, iki kol "
                   "11,24 m; S1 × 2, pan, tilt 125 cm'deki ≈ 4,3 m + 4 × 0,385 (gövde uzaması) ≈ 5,8 m (tahmini). 17,1 m + %10 → 19. "
                   "Kablo K1: ince duvarlı PVC düz 22 AWG, damar ≤ 1,4–1,5 mm, almadan önce ölçülür. Fiyat doğrulanmadı"})
guncelle("ESP32 – Pi USB kablosu", model="USB-A → micro USB, 2 m, veri",
         **{"not": "1,65 m: Pi kafada, ESP32 tabanda; 125 cm'deki 1,25 m + 0,385 gövde uzaması ≈ 1,64 m → 1,5 m yetmez, 2 m. "
                   "VBUS teline seri 1N5819. Fiyat doğrulanmadı"})

# --- uretim: baski (Y2b-baski.json), lazer, braket, baglanti (robot-bom.csv)
guncelle("PETG filament", "Microzey HS PETG beyaz", ver="v3", adet=8,
         **{"not": "Duffy 11 Ekim 2026: tamamen beyaz. Y2b (1,65 m): düz PETG parçalar 6,75 kg (63 parça, planlama/y2/Y2b-baski.json); "
                   "8 + 1 (kupon + pay) makara = %31 pay. Fiyat 11 Ekim 2026"})
guncelle("PETG filament (kupon + pay)", **{"not": "PETG kuponlar (B, C, E) ≈ 0,1 kg + fire payı; 9. makara (ihtiyaç 6,85 kg, 9 kg). Fiyat 11 Ekim 2026"})
guncelle("PETG-CF filament (eklem parçaları)",
         **{"not": "Y2b: CF parçalar 0,97–1,03 kg (16 adet; omuz destekli, doluluk 0,8–0,9) + CF kuponlar ≈ 0,2–0,3 kg → 3 × 0,5 kg = 1,5 kg "
                   "(%13–28 pay). Fiyat 11 Ekim 2026 (havale 1.077,11); stok sorulmalı"})
guncelle("3D baskı hizmeti", ver="v3", model="PETG + PETG-CF, ≈ 7,7 kg parça (1,5 TL/g)", adet=7.7,
         **{"not": "Y2b: 1,65 m baskı listesi 63 parça, 7,71–7,77 kg (planlama/y2/Y2b-baski.json). Türkiye'de 0,5–2 TL/g"})
guncelle("Alüminyum lazer kesim", model="3 mm alt plaka 346 × 500 (520 taban) + boyun plakası",
         **{"not": "Y2b: taban 520 → alt plaka 346 × 500 (önce 270 × 500; robot-bom.csv). Aralık 1.000–2.000 TL, fiyat aynı tahmin; DXF ile teklif al"})
guncelle("Alüminyum bükme braket", model="Gövde U braketi 3 mm × 8 + etek taşıyıcı L braketi 2 mm × 6 (lazer + abkant)", adet=14,
         **{"not": "Y2b: 1,65 m CAD kabuk 8 + 6 (gövde braketleri y 400 / 547,75 / 740,25 / 1165, iki yanda). Fiyat doğrulanmadı"})
guncelle("T-somun", adet=60, **{"not": "Y2b: CAD 58 (iskelet, kabuk, omuz, taban 56 + kafa 2; robot-bom.csv) + 2 yedek. Fiyat 15 Ekim 2026 (3,79 TL)"})
sil("Tırtıllı somun M4")   # 520 tabanda motor braketi M4'leri plaka ustunde DIN 985 (asagida fiberli somun)
guncelle("İmbus civata M3", model="DIN 912 A2: M3×6 × 80, ×8 × 74, ×10 × 10, ×12 × 26, ×20 × 5", adet=195,
         **{"not": "Y2b: CAD 174 (6 × 72, 8 × 66, 10 × 8, 12 × 24 — dirsek çatalı horn M3×12 dahil —, 20 × 4; robot-bom.csv) + pay. "
                   "Kategori taban fiyatı 15 Ekim 2026"})
guncelle("Bombe başlı imbus M3", "ISO 7380 A2: M3×6", model="ISO 7380 A2: M3×5 × 3, M3×6 × 100, M3×8 × 5", adet=108,
         **{"not": "Y2b: CAD 96 (5 × 2, 6 × 90, 8 × 4). Kategori taban fiyatı 15 Ekim 2026"})
guncelle("İmbus civata M5", model="DIN 912 A2: M5×10 × 9, M5×12 × 15", adet=24, **{"not": "Y2b: CAD 21 (10 × 8, 12 × 13). Kategori taban fiyatı 15 Ekim 2026"})
guncelle("İmbus civata M6 (14 / 20)", model="DIN 912 A2: M6×14 × 40, M6×20 × 2", adet=42,
         **{"not": "Y2b: CAD M6×14 36 + M6×20 2 (M6×16 ayrı satırda, CNC Marketi). Kategori taban fiyatı 15 Ekim 2026"})
guncelle("Fiberli somun M3 / M4", model="DIN 985 A2: M3 × 10 + M4 × 52", adet=62,
         **{"not": "Y2b: CAD M3 8 + M4 47 (36 kontra + 11 naylon: güç paneli 3 + 520 tabanda motor braketi 8, önce çekiç somun). "
                   "Kategori taban fiyatı 15 Ekim 2026"})
guncelle("Pul", model="DIN 125 A2: M3 × 36, M4 × 16, M5 × 23, M6 × 18", adet=93,
         **{"not": "Y2b: CAD M3 32 (16 + dirsek çatalı horn cıvatası altında 2 × 8), M4 15, M5 21, M6 16 (+ pay). Kategori taban fiyatı 15 Ekim 2026"})
guncelle("Isıl gömme somun M3", adet=160,
         **{"not": "Y2b: CAD 142 (robot-bom.csv) + pay. Fiyat 15 Ekim 2026 (adet; KDV ibaresi yok). Varyant dış çapı kupon C ile seçilir"})
guncelle("Isıl gömme somun M5", adet=16, **{"not": "Y2b: CAD 13 + pay. Fiyat M3 sayfasındaki bağlantıdan (6,27), ölçü doğrulanmadı"})
ip = bul("Isıl gömme somun M5")
K.insert(ip + 1, dict(g="uretim", ad="Saplama M3 (kafa)", model="M3 DIN 976 A2 dişli çubuk, 4 × 73 mm kesilir", adet=1, tl=40.0,
                      satici="Tahmin", url="", durum="tahmini", stok="belirsiz", ver="v3", adim="Y2b",
                      **{"not": "Y2b: CAD kafa 4 saplama (robot-bom.csv; DIN 985'i +1 mm geçer). Fiyat doğrulanmadı"}))

# --- notlar
for n in d["notlar"]:
    if n["b"].startswith("Göğüs ekranı Nextion"):
        n["b"] = "Göğüs ekranı yok (1,65 m, 25 Ekim 2026)."
        n["t"] = ("Nextion kaldırıldı; eldeki Nextion NX1060P101 bu tasarımda kullanılmıyor. Yüz ekranı 10,1\" HDMI'yı hoca verecek; "
                  "verilmezse Waveshare 10.1\" (B) satırı geçerli (\"Elimizdekileri düş\" seçilince toplamdan çıkar).")
d["notlar"].insert(0, {"b": "V3 satırları = 1,65 m ana tasarım (29 Ekim 2026).",
                       "t": "FreeCAD ana montajı (1.073 parça, montaj/robot-bom.csv), 1,65 m baskı listesi, omuz DS3235, XVF3800 mikrofon dizisi "
                            "(Efe, 26 Ekim). Demodaki 3B model eski CadQuery V3 (125 cm); V1/V2 satırları arşiv."})
# yaz: adim5/maliyet_duzelt.py ile ayni bicim (her kalem tek satir, gruplar arasinda bos satir)
def s(x):
    return json.dumps(x, ensure_ascii=False)


out = ["{"]
for k in d:
    if k not in ("gruplar", "notlar", "kalemler"):
        out.append("  %s: %s," % (json.dumps(k), s(d[k])))
for k in ("gruplar", "notlar"):
    out.append('  "%s": [' % k)
    out.append(",\n".join("    " + s(x) for x in d[k]))
    out.append("  ],")
out.append('  "kalemler": [')
rows, prev = [], None
for x in K:
    if prev is not None and x["g"] != prev:
        rows.append("")
    rows.append("    " + s(x) + ",")
    prev = x["g"]
rows[-1] = rows[-1].rstrip(",")
out.extend(rows)
out += ["  ]", "}"]
with open(YOL, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
json.load(open(YOL, encoding="utf-8"))
print("yazildi", YOL, len(K), "kalem")
