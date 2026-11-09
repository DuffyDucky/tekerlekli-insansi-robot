# -*- coding: utf-8 -*-
# F4c (P4.3): planlama/baski-listesi.md'yi F4c-partiler.json'dan kurar; metni F4c-dogrula.py YAMA'li baski_listesi_guncelle.py'den
# (bellekte, gecici kopyada) iki kez gecirip sabit nokta oldugunu dogrular ve yazar. Kaynak betikleri degistirmez. FreeCAD istemez.
# Sira: py -3 planlama/y2/Y2b-baski.py ; py -3 planlama/d158/F4c-partiler.py ; py -3 planlama/d158/F4c-liste.py ; py -3 planlama/d158/F4c-dogrula.py
import importlib.util, json, os, sys

D = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(D, "..", ".."))


def yukle(ad, yol):
    sp = importlib.util.spec_from_file_location(ad, yol)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


FP = yukle("f4cp", os.path.join(D, "F4c-partiler.py"))
DG = yukle("f4cd", os.path.join(D, "F4c-dogrula.py"))
P = json.load(open(os.path.join(D, "F4c-partiler.json"), encoding="utf-8"))
f, ar = FP.f, FP.aralik
L = P["liste_toplam"]
k0 = P["partiler"]["0"]["toplam"]


def kg(v):
    return ar(v, 2, 1000)


def satir(r):
    destek = "**destekli**" + (": " + r["destek_not"] if r["destek_not"] else "") if r["destekli"] else "desteksiz"
    return "| ☐ | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | `%s` · Y2b[%d] | %s |" % (
        r["modul"], r["ad_tr"], r["adet"], " × ".join(f(x) for x in r["olcu"]), ar(r["g"]), ar(r["sa"], 2), r["malzeme"], r["yon"], destek,
        "sığar" if r["x2d"] else "SIĞMAZ", r["kaynak"], r["y2b"], r["bagli"] + (("; " + r["basim_notu"]) if r["basim_notu"] else ""))


BASLIK = ["| ☐ | Modül | Parça | Adet | Ölçü (mm) | Filament (g/adet) | Süre (sa/adet) | Malzeme | Tabla yönü | Destek | X2D | Kaynak (JSON) | Bağlı olduğu kalem |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
cf_alt, cf_ust = L["cf_g"][0] + k0["cf_g"][0], L["cf_g"][1] + k0["cf_g"][1]
d2 = [x for x in P["partiler"]["0"]["kuponlar"] if x["kosullu"]][0]
cf_d2siz = (cf_alt - d2["g"][0], cf_ust - d2["g"][1])

s = []
s += ["# Baskı listesi (1,58 m ana tasarım; 09.11.2026)", "",
      "Önceki sürümler: 125 cm V3 (11 / 15 Ekim 2026, 50 parça), 1,65 m (29 Ekim 2026, 63 parça) ve 1,58 m'nin ilk listesi (03.11.2026, 65 parça;",
      "kafa satırları o gün 7\" modelden). Bu liste 09.11.2026'da güncel ana modele göre yenilendi (F4c / P4.3): 10,1\" QLED kafa, göğüs ekranı",
      "çerçevesi ve VESA taşıyıcı, hub takozlu üst arka kapak, hoparlör kabı ve kelepçesi, omuz göbeği durdurucu dişi.",
      "**Kaynak zinciri:** modül analizleri `tasarim/freecad/<modül>/<modül>-analiz.json` (`baski` alanı; %80 doluluk, 10 mm³/s) ve omuz için",
      "`tasarim/freecad/omuz/omuz-baski.json` (PETG-CF doluluk 0,8–0,9; 09.11.2026 F2 koşusu, göbek dişi dahil) → `planlama/y2/Y2b-baski.py` →",
      "`planlama/y2/Y2b-baski.json` → bu dosya. Kabuk ve kafa satırlarını `tasarim/freecad/lale158/baski_listesi_guncelle.py` yazar; öteki",
      "satırlar, ek sütunlar ve parti planı F4c'den (`planlama/d158/F4c-partiler.md`). Denetim: `py -3 planlama/d158/F4c-dogrula.py` (her satırın",
      "JSON anahtarı, toplamlar, betik çıktısı). Ana montajın BOM'u (`tasarim/freecad/montaj/robot-bom.csv`, `Baski` satırları) aynı 72 parçayı sayıyor.",
      "Yazıcı: Bambu Lab X2D (246 × 246 × 250 mm); **72 parçanın hepsi X2D'ye ve okul tablasına (250³) sığıyor** (en büyük ölçü 235 mm, göğüs",
      "bandı yüksekliği; analizlerdeki `sigar` ve baskı yönündeki ölçü). **14 adet destekli** basılır: omuzda omuz yuvası, omuz göbeği, kol çatalı,",
      "S1 kablo tamburu (ikişer); kafa kabuğunun sağ ön (yüz kabuğu sağ) ve sağ arka parçası (karar 29.10: dikiş dili); göğüs bandı sağ ve sol",
      "(cep üst kenarı); göğüs ekranı VESA taşıyıcı (arka flanş); üst arka servis kapağı (hub takozlu, analiz destek istiyor, aşağıda not). Diğer 58 parça desteksiz.",
      "", "## 158 cm güncellemesi", ""]   # yamali betik bu bolumu yeniden yazar

s += ["## 03.11 → 09.11 farkı", "",
      "| Değişiklik | Parça | Adet | Filament | Süre | Neden ve kaynak |", "|---|---|---|---|---|---|",
      "| Yeni | Hoparlör kabı ön halka, hoparlör kabı arka (flanşlı) | +2 | +10 g | +0,3 sa | 05.11 B + R1 ses yerleşimi (`d26c7e7`); `kabuk/baski[31]`, `[32]` |",
      "| Yeni | Hoparlör kelepçesi | +1 | +5 g | +0,1 sa | F1a P1.7 arka tutucu (`76a5701`); `kabuk/baski[33]` |",
      "| Yeni | Ekran tırnağı üst / alt, sağ / sol (10,1\" QLED tutucu) | +4 | +6,4 g | +0,12 sa | QLED kafa (`bcaa6df`, 04.11); `kafa/baski[10…13]` |",
      "| Değişti | Üst arka servis kapağı: hub takozu (USB hub kapak içinde) | 0 | +5 g | +0,1 sa | 05.11 (`d26c7e7`); kalınlık 3 → 12,5 mm, desteksiz → destekli (`kabuk/baski[13]`) |",
      "| Değişti | Kafa kabukları (QLED ekran yuvası) | 0 | −53,6 g | −1,12 sa | Yüz sağ 119 → 91, yüz sol 110 → 84, arka sağ / sol +0,2 / +0,1 g (QLED `bcaa6df` 04.11, arka sağ B + R1 `d26c7e7` 05.11; `kafa/baski[5…8]`) |",
      "| Değişti | Boyun yükseltme adaptörü | 0 | −3,6 g | −0,08 sa | Yükseklik 62,8 → 58,9 mm (QLED `bcaa6df` 04.11; `kafa/baski[4]`) |",
      "| Değişti | Göğüs ekranı çerçevesi sağ / sol, VESA taşıyıcı | 0 | +4 g / −1 g | 0 | Çerçeve 29 → 31 g (×2), VESA 114 → 113 g ve 64,8 → 63,4 mm (`bcaa6df`, 04.11) |",
      "| Değişti | Omuz göbeği (S2 durdurucu dişi F2, diş kökü r 1,5 F6a) | 0 | +5,4–5,8 g | +0,10–0,12 sa | Ölçü 66 → 77 mm, adet başına 60,6–67,5 → 63,3–70,4 g, destek 5,2 → 5,7 g (`omuz-baski/parcalar[2]`, F2 `ff1c2e9`; kök yayı F6a +0,1 g alt uçta) |",
      "| Malzeme | Göğüs ekranı VESA taşıyıcı | 0 | 0 | 0 | Model PETG-CF (`kabuk_parcalar.py:375-376`, `malzeme=\"PETG-CF\"`) ve `Y2b-baski.py` CF kümesi; eski Renk tablosu beyaz PETG diyordu, düzeltildi |",
      "| **Fark toplamı** | 65 → **72** parça | **+7** | 7,63–7,68 → **7,60–7,66 kg** (−22,4 / −22,0 g) | 158,7–159,9 → **158,2–159,4 sa** (−0,48 / −0,46) | PETG 6,47 → 6,45 kg; PETG-CF 1,16–1,21 → 1,16–1,22 kg |",
      "",
      "Kafa satırlarındaki düşüş, 03.11 listesinin kafa satırlarının 7\" modelden kalmasından: QLED modeli (04–05.11) yüz kabuklarını inceltti.",
      "Parça sayısının 65 → 72 artışı yalnız küçük parçalardan (en büyüğü 7 g); filament ve süre neredeyse aynı kaldı.", ""]

s += ["## Özet", "", "| Parti | Ne zaman | Adet | Filament | Baskı süresi |", "|---|---|---|---|---|",
      "| 0 | İlk gün: tolerans kuponları (toplama katılmaz) | %d baskı | %s kg | ≈ %s sa |" % (k0["adet"], kg(k0["g"]), ar(k0["sa"], 0)),
      "| 1 | x | 0 | 0 kg | ≈ 0 sa |", "| 2 | x | 0 | 0 kg | ≈ 0 sa |", "| 3 | x | 0 | 0 kg | ≈ 0 sa |", "| 4 | x | 0 | 0 kg | ≈ 0 sa |",
      "| **Toplam** | | **0** | **0 kg** | **≈ 0 sa** |", "",
      "| Malzemeye göre | Düz PETG (beyaz) | PETG-CF (siyah) |", "|---|---|---|"]
for k in ("1", "2", "3", "4"):
    t = P["partiler"][k]["toplam"]
    s.append("| Parti %s | %s kg | %s kg |" % (k, kg(t["petg_g"]), kg(t["cf_g"])))
s += ["| **Parçalar** | **%s kg** | **%s kg** |" % (kg(L["petg_g"]), kg(L["cf_g"])),
      "| Parti 0 kuponları | %s kg | %s kg |" % (kg(k0["petg_g"]), kg(k0["cf_g"])),
      "| **Parça + kupon** | **%s kg** | **%s kg** |" % (kg([L["petg_g"][0] + k0["petg_g"][0], L["petg_g"][1] + k0["petg_g"][1]]), kg([cf_alt, cf_ust])), "",
      "Parti ayrıntısı, bağımlılıklar, montaj adımı ve takvim kontrolü: `planlama/d158/F4c-partiler.md`.", "",
      "**Filament:** parçalar net **düz PETG %s kg** + **PETG-CF %s kg** (`Y2b-baski.json`; omuz doluluğu 0,8–0,9, omuz desteği dahil;" % (kg(L["petg_g"]), kg(L["cf_g"])),
      "kabuk ve kafa satırlarında destek malzemesi sayılmadı; VESA taşıyıcının 28 destekli katmanı da). Kuponlar (Parti 0) PETG %s kg, PETG-CF %s kg." % (kg(k0["petg_g"]), kg(k0["cf_g"])),
      "Plan: **9 makara beyaz PETG + 1,5 kg siyah PETG-CF (3 × 0,5 kg)** (`planlama/maliyet.json` `kalemler[107–109]`).",
      "- **PETG yetiyor:** parça + kupon %s kg, 9 kg'de ≈ %s kg pay (≈ %%%s)." % (kg([L["petg_g"][0] + k0["petg_g"][0], L["petg_g"][1] + k0["petg_g"][1]]),
                                                                              ar([9000 - L["petg_g"][1] - k0["petg_g"][1], 9000 - L["petg_g"][0] - k0["petg_g"][0]], 1, 1000),
                                                                              f((9000 - L["petg_g"][0] - k0["petg_g"][1]) / L["petg_g"][0] * 100, 0)),
      "- **PETG-CF 1,5 kg sınırda, yetmiyor sayılmalı:** parça + kupon %s kg; 1,5 kg'de pay %s g (doluluk 0,8 ve kuponların tahmini kütlesiyle) ile %s g"
      % (kg([cf_alt, cf_ust]), f(1500 - cf_alt, 0), FP.isaretli(1500 - cf_ust, 0)),
      "  (doluluk 0,9 ve %%100 kupon). D2 kuponu basılmazsa pay %s–%s g. En büyük CF parçası (kafa servo yuvası) 152 g: tek bir başarısız baskı alt"
      % (f(1500 - cf_d2siz[1], 0), f(1500 - cf_d2siz[0], 0)),
      "  durumdaki payı bitiriyor. Karar taslağı `planlama/d158/F4c-gunluk.md` (KT-F4c-1: +1 makara, 0,5 kg, 1.114,03 TL; %15 payla 1.281,13 TL).", ""]

s += ["## Renk (Ahmet, 11 Ekim 2026: \"Tamamen beyaz\")", "", "| Renk | Parçalar |", "|---|---|",
      "| **Beyaz PETG** | Düz PETG'den basılan her şey: kabuk (gövde, uzatma ve göğüs bantları), etek ve dolgu şeritleri, kafa kabukları, kafa iskeleti, kafa ekranı tırnakları (10,1\" QLED), göğüs ekranı çerçevesi (gövde renginde, 04.11), hoparlör kabı ve kelepçesi, üst kol tüpü, ön kol, el, sonar tutucular, akü takozu, servis kapakları (hub takozlu üst arka kapak dahil), S1 kaseti ve kablo tamburu |",
      "| **Siyah PETG-CF** | Yük taşıyan 12 tür (18 adet). Omuz ve dirsek eklemleri siyah görünür; kafa iç parçaları kabuğun, VESA taşıyıcı göğüs ekranının arkasında kalır |", "",
      "## Malzeme", "", "| Malzeme | Nereye | Neden |", "|---|---|---|",
      "| **PETG** (beyaz) | Yukarıdaki beyaz parçalar | Yükü az, büyük parçalar. PETG tok, kolay basılır (camsı geçiş ≈ 80 °C, tahmini). Etekteki ısı ölçülünce kontrol edilmeli (E7) |",
      "| **PETG-CF** | Servo torkunu, rulman yükünü ya da ekran ağırlığını taşıyan 12 tür (aşağıda) | Düz PETG'den rijit, sıkı geçmede ve vida sıkıştırmasında daha az akma (tahmini) |", "",
      "**PETG-CF ile basılacak parçalar (toplam PETG-CF %s kg):**" % kg(L["cf_g"]), "",
      "| Modül | Parça | Adet | Taşıdığı yük |", "|---|---|---|---|",
      "| omuz | Omuz yuvası | 2 | Bütün kolun momenti; travers ucuna M6 ile bağlı |",
      "| omuz | Rulman kapağı | 2 | 6808-2RS sıkı geçme (Ø52) |",
      "| omuz | Omuz göbeği | 2 | S1 horn torku (DS3235) + rulman mili Ø40; S2 durdurucu dişi (F2) |",
      "| omuz | Kol çatalı | 2 | S2 horn torku (DS3235) + 625ZZ yuvası |",
      "| dirsek | Dirsek çatalı | 2 | Dirsek horn torku; dış kol 8 mm, horn cıvatası M3×12 + 2 pul |",
      "| dirsek | Bilek flanşı | 2 | Bilek horn bağlantısı |",
      "| kafa | Servo yuvası | 1 | Kafanın tamamı bunun üstünde (QLED kafa, kütle `kafa-analiz.json`) |",
      "| kafa | Rulman yuvası | 1 | 6808-2RS yuvası |",
      "| kafa | Boyun mili | 1 | Pan horn torku |",
      "| kafa | Eğme çatalı | 1 | Tilt horn torku (tilt sınırı ±13°, karar 29.10). Montajda tilt servosundan **önce** takılır (M6 C3) |",
      "| kafa | Boyun yükseltme adaptörü | 1 | Pan torku ve kafa ağırlığı (boyun mili ile eğme çatalı arasında; karar 29.10) |",
      "| kabuk | Göğüs ekranı VESA taşıyıcı | 1 | 11,6\" göğüs ekranının ağırlığı (VESA 4 × M4, taşıyıcı 2 × M6); model malzemesi PETG-CF (`kabuk_parcalar.py:375-376`) |", "",
      "**Karar 29.10 (Ahmet):** Y2a'da eklenen **boyun yükseltme adaptörü** (boyun mili ile eğme çatalı arasında, pan torku ve kafa ağırlığı",
      "yolunda) **PETG-CF** ile basılır; CAD'de (`kafa10_lib.py`) malzeme PETG-CF.", "",
      "**Neden PA-CF değil:** Nem çeker, kurutma ister, pahalı. Bu yüklerde (el yükü ≈ 100 g sınırı, jestler) PETG-CF yeterli olmalı (tahmini).", "",
      "**Yazıcı şartı:** Karbon katkılı filament sertleştirilmiş çelik nozul ister (X2D fabrikadan 0,4 mm sertleştirilmiş çelik). Okul",
      "yazıcısında nozulun değiştirilmediğini kontrol edin.", "",
      "**Ayar (PETG-CF):** duvar 5–6, üst/alt 5 katman, doluluk %50–60 gyroid, filament kuru. **Tolerans kuponları (Parti 0) asıl",
      "malzemeyle basılmalı.**", "",
      "**Destekli kafa kabuğu (karar 29.10):** yüz kabuğu (ön) sağ ve arka kafa kabuğu sağ, x = 0 dikiş dilinde (16 mm şerit, iç yarı duvar)",
      "yüzü tablada baskıda ~1,25 mm yükseklikte konsol bırakıyor. Dilimleyicide yalnız bu bölgelere destek (\"support on build plate only\"",
      "yeterli değilse boyalı destek); destek dil yüzünden temizlenmeli, dil 1,3 mm et.", "",
      "**Üst arka servis kapağı (hub takozlu):** analiz (`kabuk/baski[13]`) z 2,5'te 197 cm² destek istiyor (156 mm boy). 3 mm plakanın iç",
      "yüzüne yapışık takozun dış yüzü tablada basılırken destek istemesi beklenmez; neden incelenmedi (FreeCAD gerekiyor), dilimleyicide",
      "bakılmalı ve P6.1'de kesitle doğrulanmalı (`planlama/d158/F4c-gunluk.md`). Listede analizdeki gibi \"destekli\".", "",
      "**Süre:** ≈ %s saat; yazıcı hiç durmazsa ≈ %s gün. Paylaşımlı okul yazıcısında haftada 32–40 sa ile ≈ %s hafta (tahmini). Parti 1 hemen başlamalı."
      % (ar(L["sa"], 0), f(L["sa"][1] / 24, 1), ar([L["sa"][0] / 40, L["sa"][1] / 32], 1)), ""]

s += ["## Sıralama mantığı", "",
      "1. **Parti 0, ilk gün tolerans kuponları** (`tasarim/freecad/test/`, aşağıda). Seçilen ölçü CAD'e girer, büyük parçalar sonra basılır.",
      "2. **Parti 1:** ölçüsü elimizdeki parçaya pek bağlı olmayanlar: gövde, uzatma, göğüs ve omuz bantları, arka servis kapağı, sonar",
      "   tutucular, rulman kapağı, üst kol tüpü. **Partinin sonunda, ilgili kalem gelip ölçülünce:** üst arka servis kapağı (USB hub takozu),",
      "   hoparlör kabı ve kelepçesi (8 Ω hoparlör), göğüs ekranı çerçevesi sağ/sol ve VESA taşıyıcı (11,6\" göğüs ekranı; VESA deliklerinin",
      "   kasadaki yeri ve derinliği doğrulanmadı, `arayuz.py:342`). %d adet, ≈ %s sa; Parti 1 tablosunun son satırları (`F4c-partiler.md`)." % (
          P["partiler"]["1"]["sona_birakilan"]["adet"], ar(P["partiler"]["1"]["sona_birakilan"]["sa"], 1)),
      "3. **Parti 2:** horn delik dizilimi tahmini (25T disk, M3 delikler 8,5 mm yarıçapta) ve servo gövdeleri (DS3235, MG996R). Gelince",
      "   kumpasla ölçülür, CAD güncellenir, sonra basılır. Omuz göbeğinin diş kökü yarıçapı (r 1,5) F6a'da uygulandı; DS3235 düşme ölçümü (K39) açık.",
      "4. **Parti 3:** kafa ekranı 10,1\" QLED 1280×720 (WaveShare, kod 20789). Vida deliği yok, 4 ekran tırnağıyla tutulur; kütle doğrulanmadı.",
      "   Ekran gelip ölçülünce (K32: hocadan mı satın alma mı) ve K2 (AI HAT / boss, P6.1) modele girince kafa iskeleti, kabuklar ve tırnaklar basılır.",
      "5. **Parti 4:** etek ana anahtar deliği (M6 K7) ve H1, H2 servis kapakları (M6 K5, K6) CAD'de; etek havalandırma yarıkları (E7) bekliyor.",
      "   Akü **yerinde** (karar 29.10); akü takozu akü gelince teyit edilip **Parti 1 arasında** basılır (M6 adım 4).", ""]

s += ["## Tolerans (CAD'de)", "", "| Geçme | CAD değeri | Not |", "|---|---|---|",
      "| Vida geçiş delikleri | M3 Ø3,4 · M4 Ø4,5 · M5 Ø5,5 · M6 Ø6,6 (ISO 273 orta) | `arayuz.CLEAR` |",
      "| Servo cepleri | Her yanda +0,2 mm | |",
      "| Omuz yuvası ↔ sigma travers | Her yanda +0,2 mm | |",
      "| Üst kol tüpü ↔ çatal ve dirsek pimi (Ø50,8) | Tüp içi Ø51,3, her yanda 0,25 mm | `arayuz.GECME[\"tup_pim\"]` |",
      "| Isıl gömme somun deliği | M3 Ø4,0 (ruthex M3×5,7), M5 Ø6,4 (tahmini) | `arayuz.INSERT_DELIK`; kuponla doğrulanacak; insert varyantı K31 (A/B/C) açık |",
      "| Kabuk bindirmesi | 0,25 mm boşluk | `arayuz.KABUK_BINDIRME_BOSLUK` |",
      "| Rulman yuvaları (6808 Ø52, 625ZZ Ø16), Ø40 mil | Tam ölçü (sıkı geçme) | **Kupondan sonra** seçilen ölçü uygulanacak |",
      "| Horn delik dizilimi | Tahmini | Horn gelince kumpasla |", "",
      "### Tolerans kuponları (Parti 0)", "",
      "Kuponlar `tasarim/freecad/test/stl/` (A, B: `tolerans_kuponu.py`; C, D1, D2, E: `m7_kuponlari.py`, `test/README.md`). %d baskı:" % k0["adet"],
      "B ve C hem PETG-CF hem beyaz PETG; D2 yalnız D1 geçmezse ya da karşılaştırma için. Toplam PETG %s kg, PETG-CF %s kg, ≈ %s sa"
      % (kg(k0["petg_g"]), kg(k0["cf_g"]), ar(k0["sa"], 1)),
      "(tahmini kütleyle alt, %%100 dolulukla üst değer; D2'siz ≈ %s sa). Kupon tablosu, K31 seçeneğine göre etkisi ve omuz dişi kökü notu: `planlama/d158/F4c-partiler.md`." % ar(k0["d2siz_sa"], 1), "",
      "| Kupon | Malzeme | Ne denenir | Filament (g) |", "|---|---|---|---|"]
for x in P["partiler"]["0"]["kuponlar"]:
    s.append("| %s%s | %s | %s | %s |" % (x["kod"], " (koşullu)" if x["kosullu"] else "", x["malzeme"], x["denenen"], ar(x["g"], 1)))
s += ["",
      "Rulman elle (ya da mengeneyle hafif) bastırınca oturmalı; ısıl gömme somun havyayla düz girmeli, vida sıkınca dönmemeli. Sonuç CAD'e uygulanır ve STL'ler",
      "yeniden çıkarılır.", "",
      "## STL durumu", "",
      "Omuz STL'leri (`tasarim/freecad/omuz/stl/`, 09.11 F2 koşusu; `omuz-gobegi.stl` dişli) ve kuponlar (`tasarim/freecad/test/stl/`) var. Diğer",
      "modüllerin baskı parçaları kupon sonucundan sonra FreeCAD'den toplu dışa aktarılmalı (açık iş; P6.1'de modüller yeniden üretilirken).", "",
      "## Parti tabloları", "",
      "Sütunlar: ölçü analizdeki baskı yönündeki kutu (mm; omuzda `omuz-analiz.json` `baski.olcu`), filament ve süre adet başına (omuz satırlarında aralık",
      "doluluk 0,8–0,9, destek dahil). Malzeme `Y2b-baski.py` CF kümesinden. Kaynak: `<modül>/baski[i]` = `tasarim/freecad/<modül>/<modül>-analiz.json`",
      "→ `baski[i]`; `omuz-baski/parcalar[i]` = `tasarim/freecad/omuz/omuz-baski.json` → `parcalar[i]` (yön `secilen_yon`); `Y2b[i]` =",
      "`planlama/y2/Y2b-baski.json` → `satirlar[i]`. X2D: analizdeki `sigar` ve ölçü ≤ 246 × 246 × 250. Montaj adımları `F4c-partiler.md`'de.",
      "**Eski analiz:** yok. Beş kaynağın hepsi son geometriden (taban, kabuk, omuz, dirsek 09.11; kafa 05.11, F1a'nın 08.11 kaynak değişikliği",
      "geometriyi değiştirmedi: `F1a-kontrol.md` P1.3). Ayrıntı `planlama/d158/F4c-gunluk.md`.", ""]

for k in ("1", "2", "3", "4"):
    p = P["partiler"][k]
    t = p["toplam"]
    s += ["## Parti %s — %s" % (k, p["ad"]), "",
          "%d adet · %s kg filament (PETG %s, PETG-CF %s) · ≈ %s saat. Bağımlılık: %s." % (t["adet"], kg(t["g"]), kg(t["petg_g"]), kg(t["cf_g"]), ar(t["sa"], 1), p["bagimlilik"]), ""]
    s += BASLIK + [satir(r) for r in p["parcalar"]] + [""]

taslak = "\n".join(s).rstrip("\n") + "\n"
a = DG.guncelle(taslak, True)
b = DG.guncelle(a, True)
assert a == b, "sabit nokta degil"
open(os.path.join(KOK, "planlama", "baski-listesi.md"), "w", encoding="utf-8", newline="\n").write(a)
print("yazildi", len(a.splitlines()), "satir")
