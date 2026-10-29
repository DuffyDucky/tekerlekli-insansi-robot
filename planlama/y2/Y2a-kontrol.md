# Y2a — 1,65 m taslağın ana montaja taşınması: bağımsız kontrol

Kontrol ajanı (bağımsız; modül dosyalarına, `arayuz.py`'ye, `montaj/`'a dokunmaz). Dal `lale-duzeltme`, HEAD `6594c63` + çalışma ağacındaki
Y2a değişiklikleri (commit'lenmemiş). Girdi: `Y2a-brief.md`, `Y2a-gunluk.md` (tasarım ajanı), `planlama/dongu.md` "1,70 m planı",
`adim2/K3-s1-duzeltme-kontrol.md` (KZ1/KZ2 kaynağı). Durum: **kapandı — KOŞULLU GEÇTİ** (29 Ekim 2026; aşağıda "Sonuç").

## Yöntem
- `tasarim/freecad/` ve `kod/ortak/` scratchpad'e kopyalandı (OneDrive'a çıktı yazılmadı); tüm modül betikleri kopyada **sırayla yeniden
  koşuldu**: iskelet → kabuk → omuz → dirsek → kafa → taban → ana montaj → taban (robot satırları) → yerleşim kontrolü (hepsi rc 0; kabuk 690 s).
- Kopyanın çıktıları projedekilerle karşılaştırıldı (JSON derin fark, tarih/süre alanları hariç; BOM CSV bayt bayt).
- Bağımsız ölçüm betikleri (bu klasörde, proje kökünden çalışır; çıktılar yanında):
  `Y2a-K-olcum.py` → `Y2a-K-olcum.json` (boy, direk, tekerler, akü +75 çakışması, tambur ip deliği, kafa × sağ kol çapraz tarama),
  `Y2a-K-devrilme.py` → `Y2a-K-devrilme.json` (parça kütle merkezlerinden robot AM'si ve devrilme; 520 poz × 2 kip ızgara),
  `Y2a-K-tilt.py` → `Y2a-K-tilt.json` (kafa tilt sınırı 0,5° adımla). KZ1 için K3 `K3-olcum.py` `cep` adımı (değiştirilmeden) kopyada
  → `Y2a-K-kz1-cep.json`.

## Günlük
- 2026-10-29 ~02:57: açıldı. Okundu: brief, tasarım günlüğü, CLAUDE.md, dongu.md, K3 raporu, `git diff` (arayuz, iskelet_montaj, kabuk_lib /
  _parcalar / _montaj, omuz_parcalar, dirsek_lib / _parcalar / _montaj, kafa_montaj, taban_parcalar / _montaj, donus_hesap, ana_montaj,
  moduller, eklem_sinirlari_uret, S1-kaset.md, freecad README). Kopya koşusu başladı.
- ~03:22: koşu bitti (oturum sınırı arası). 06:41 devam: karşılaştırma, ölçümler, devrilme (orkestratör ek isteği), tilt.

## Bulgular
- **Yeniden üretim:** iskelet, kabuk, omuz, dirsek, kafa, taban, montaj analiz JSON'ları ve `yerlesim-kontrol.json` → **fark 0**; 6 BOM CSV
  (`robot-bom.csv` dahil) bayt bayt aynı. Proje çıktıları betiklerle tutarlı (montaj 02:43'te kabuktan önce koşmuş olsa da sonuç aynı).
- **Modül sonuçları (kendi koşum):** iskelet 59 parça, çakışma 0, bağlantı 12/12, bölge 0 ihlal, 6.548,1 g, kesim planı [2000, 1000, 1000]
  artık [113,5; 99; 805]; kabuk 291 (25 baskı), iç / iskelet çakışma 0, bölge 0, braket 14/14, vida 79/79, kaset 4/4, bindirme boşluğu ≥ 0,188,
  **25/25 desteksiz, 25/25 okul tablasına sığar**, 6.074,6 g; omuz S2 5 statik 0; dirsek ev 0, bağlantı 22/22, 4/4 baskı desteksiz
  (El dahil), 399,7 g; kafa ev 0, bağlantı 29/29, 2.043,0 g; taban bağlantı 119/119, iskelet/kabuk 0.
- **Ana montaj:** 1.073 parça (iskelet 59, omuz 73+73, kabuk 291, dirsek 57+57, kafa 147, taban 316), 22 grup, 22 eklem, solve 0,
  çözücü sapması 0, STEP 1.073 katı, geçersiz 0, **24.396,08 g**, AM **(−0,203; 527,432; −12,385)** ✔.
- **Boy:** tüm parçaların optimal sınır kutusu y 0,000 … **1.650,000** (en üst: dört kafa kabuğu parçası) ✔. Direk y 134,5 … 1.320,0,
  **L 1.185,5** ✔; `arayuz` BOY 1650 → S3 1340, UZAMA 385, dikişler 476,5 / 669 / 861,5 / 1075 / 1268, braketler 400 / 547,75 / 740,25 / 1165,
  arka kapak 885…1075 (betiklerde sabit 955/975/985/935/800,5/1235 artığı yok; yalnız `kafa7_parcalar.py` 7. satır yorumu "975").
- **Taban 520:** teker merkezleri x **±216**, z ±185 → **iz genişliği 432 mm** (orkestratör özetindeki "216" yarım iz), robot zarfı x ±261,7;
  etek 2 × 260 ✔.
- **Nextion:** kabukta ekran / boss / pencere / konnektör bölgesi yok; `NEXTION` ve `ekran_noktasi` arayuzden silinmiş; kalan "ekran" parçaları
  kafadaki 10,1" yüz ekranı ✔. Artık metin yalnız `kabuk_rapor.py` (A.NEXTION → çalışmaz), `kabuk_gorsel.py`, `rehber/rehber_metin.py`
  (rapor / görsel / rehber; Y2b–Y5, tasarımcı da not etmiş).
- **Akü 75 mm öne (uygulanamaz iddiası) DOĞRULANDI:** akü y 94,5…171,5, z −205…−29 (yerinde çakışma 0). z +75'te ortak hacim:
  orta ara ray **131,5 cm³**, gövde direği **26,9 cm³**, iki direk-ray köşe bağlantısı 16,7 cm³ (+ M6 takımları), orta iç köşe bağlantıları,
  plaka M6'ları, takoz ısıl gömmeleri (toplam 30 parça); kayış ve takoz da çakışır. Seçenekler (günlük a/b/c) Duffy kararı.
- **KZ1 (pim boşluğu 1,0):** `arayuz` `pim.bosluk` 1,0, `u_pay` 6,5 ✔. K3 `cep` ölçümü (kendi koşum FCStd'leri): L taraması U_duvar
  +3,5 → 0,113 / +4,0 → −0,135 ⇒ **L +3,73 mm**; S1 taraması 140 → 0,069 / 141 → −0,293 ⇒ **S1 +5,19°** (hedef +3 / +4 ✔). Pim dikmesi S1
  135'te 3,75 (önce 3,26). Tasarımcının sayıları birebir.
- **KZ2 (tambur ip deliği ≥ 0,8):** tamburda ψ 148 / 156 ipi yönünde r 37,5 / 38 / 38,5 dilimlerinde (0,01 mm örnekleme) boşluk
  x **153,21…153,99** ve **157,81…158,59** → eksenel **0,79–0,80** (nominal 0,8; örnekleme çözünürlüğü) ✔.
- **S1-kaset.md:** K3 listesi (ESKİ işareti, 28,38 görünüm, duvar ipi −x notu, u_pay 7,0 satırı → KZ1) ve Y2a bölümü eklendi ✔.
- **Yerleşim kontrolü (`yerlesim_kontrol.py`, yeniden koşuldu):** ev pozu S2 5 modül çiftleri 2.394 bb çifti, **çakışma 0**; sağ kol kaba
  40 poz **0**; kafa pan ±90 × tilt ±15 (15 poz) **0**, 15 mm içinde komşu yok ✔. Kapsam notu: modül içi çiftler modül kontrollerinde;
  tam tarama Y4.
- **Kafa × sağ kol (bağımsız, yasak kutu `aktif=False` dayanağı):** S1 60/90/120/135 × S2 5…117/120 × dirsek 0/52,5/80/105 × pan 0/30/45/90 ×
  tilt ±15/0: **çakışma 0**, en küçük **26,4 mm** (El ↔ yüz kabuğu, S1 135 / S2 5 / dirsek 105 / pan 30 / tilt −15) ✔.
- **Kafa tilt sınırı (bağımsız, 0,5° adım):** ±17'ye kadar (−16,5) çakışma yok; **ilk çakışma +18° (yüz kabuğu sağ ↔ rulman yuvası) ve
  −17° (arka kafa kabuğu sağ ↔ rulman yuvası)**. Yazılım sınırı ±15 → pay **+2…2,5° / −1,5…2°**. `kafa_montaj` 5° adımla "+20'de ekran ↔
  boyun mili" diyor; ilk temas daha erken ve başka çift. → KZ3.
- **Baskı:** dirsek El (45° koni) ve boyun adaptörü (45° koni) artık desteksiz ✔. `dirsek_lib` / `kabuk_montaj` destek hesabı düzeltmesi
  incelendi: ofseti kurulamayan yüzün **ofsetsiz** kullanılması çıkıntıyı büyütür (tutucu), 0,98 / 1,02 yeniden denemesi yalnız OCC
  hatasında devreye girer → gizleme değil ✔. Açık: kafa kabuğu SAĞ ön / arka parçaları desteksiz değil (çıkıntı 26,1 / 52,3 cm²) → KZ4.
- **Servo payı (bağımsız el hesabı):** S1 yüklü = yüksüz 10,94 + 0,5 kg × 40,69 cm = 31,3 kg·cm / stall 30,4 → **0,97**; dirsek 2,42 +
  0,5 × 20,39 = 12,6 / 9,4 → **0,74** ✔ (tasarımcıyla aynı). `arayuz.DIRSEK.yuk_g` 500 tasarım yükü sağlanmıyor → KZ2.
- **Devrilme (orkestratör ek isteği; bağımsız):** robot 24.796,1 g (montaj + 400 g kablo payı, taban_parcalar varsayımı), ev AM
  (−0,20; 521,39; −13,15). Formül a = g (d cos θ − h sin θ) / h, d teker merkez hattına (z ±185, x ±216), pay = a / 1,5 (fren varsayımı
  1,5 m/s², tahmini), ölçüt pay ≥ 1,5:

  | Poz | düz geri / ileri / yan (m/s²) | rampa 5° geri | rampa 5° ileri | pay (rampa, en küçük) |
  |---|---|---|---|---|
  | ev (S2 5) | 3,23 / 3,73 / 4,06 | **2,37** | 2,86 | 1,58 ✔ |
  | iki kol geride S1 −45 | 3,10 / 3,83 / 4,04 | **2,23** | 2,96 | **1,49 ✘** |
  | ızgara en kötüsü (S1 75, S2 120, dirsek 0, iki kol) | — | **2,22** | — | **1,48 ✘** |
  | iki kol önde S1 90 | 3,35 / 3,50 / 3,99 | 2,48 | 2,63 | 1,65 ✔ |
  | önde + elde 2 × 0,5 kg | — | 2,57 | **2,16** | **1,44 ✘** (ileri) |
  | ev, akü +75 (varsayımsal) | 3,40 / 3,56 | 2,53 | 2,69 | 1,69 ✔ |
  | S1 −45, akü +75 (varsayımsal) | — | 2,40 | 2,79 | 1,60 ✔ |

  Tasarımcının 2,23 m/s² (S1 −45) değeri **teyit edildi** (fark < 0,01); ama tasarımcının 6 pozu en kötüyü kaçırıyor: ızgarada S1 75 / S2 120
  2,22. **Akü yerinde kalırsa rampada 5° ölçüt 1,5 ev pozunda sağlanır (1,58), kollar geride / yanda-yukarıda sağlanmaz (1,48–1,49),
  elde yükle ileri yönde de sağlanmaz (1,44).** Akü 75 mm önde olsaydı geri yön 1,60'a çıkardı (ama geometrik olarak olmuyor). Açık kalan
  kural (`yazilim-notu-stowent-170.md` 3: rampada kollar ev pozunda, ivme ≤ 0,1 m/s²) bu durumu yazılımla kapatıyor → KZ1.
- **Kapsam (git diff):** brief dışı üretim yok. `kod/ortak/eklem_sinirlari.json` + `_uret.py` (brief'te Y2b) arayüz değişince üretici
  kontrolü için zorunlu; `--kontrol` "güncel" ✔, kabul. Taslak-170, `tasarim/cad/`, `maliyet.json`, kök README dokunulmamış ✔.
  **İzlenmeyen ve Y2a'ya ait olmayan:** `tasarim/solidworks/` (29 Ekim 02:25; kaynağı bu oturumun scratchpad'indeki `step_renkli.py`) ve
  `tasarim/WhatsApp Image 2026-10-27 ….jpeg` → Y2a commit'ine **girmemeli** (orkestratör karar verir).
- **Belge / metin hataları (küçük):** günlük başlığı ve görev satırı hâlâ "1,70 m … gövde direği 1.235,5"; günlükteki 03:05–03:35 zaman
  damgaları gerçek dosya zamanlarından ileri (tüm çıktılar ≤ 02:55); günlükte iskelet sehimi 0,336, JSON 0,371 mm; `eklem_sinirlari_uret.py`
  yorumu "1,70 m"; `kafa7_parcalar.py` yorumu "975"; kafa10 cıvatalarının ısıl gömme kavrama ölçüsü kontrol edilmemiş (tasarımcı
  "kontrol ajanına" notu; bu kontrolde de ölçülmedi → Y3/Y4).

## Sonuç (29 Ekim 2026) — KOŞULLU GEÇTİ

| # | İddia | Ölçülen (bağımsız) | Durum |
|---|---|---|---|
| 1 | Boy 1650, uzatma 385, direk 1.185,5 tek parça 2 m | ymax 1.650,000; direk L 1.185,5; kesim [2000, 1000, 1000] | ✔ |
| 2 | Uzatma bantları tablaya sığar | 2 × 192,5 (+12 dil 204,5); 25/25 okul 250³'e sığar | ✔ |
| 3 | Nextion kaldırıldı | parça / bölge / pencere yok; rapor/görsel/rehber metinleri eski (Y2b–Y5) | ✔ (notlu) |
| 4 | Taban 520 | teker x ±216 (iz 432), etek 520, teker–etek 12,0 | ✔ ("iz 216" ifadesi yanlış) |
| 5 | Akü 75 öne uygulanamadı | z +75'te orta ara ray 131,5 cm³, direk 26,9 cm³ + 28 parça daha | ✔ iddia doğru (karar açık) |
| 6 | KZ1 | L +3,73 / S1 +5,19° | ✔ |
| 7 | KZ2 | delik 0,79–0,80 (nominal 0,8) | ✔ |
| 8 | S1-kaset.md | K3 listesi işlenmiş | ✔ |
| 9 | Modüller + ana montaj, çakışma 0, bağlantılar tam; 1.073 / 22 / 24.396,1 g / AM | yeniden koşum = proje çıktıları (fark 0); sayılar birebir | ✔ |
| 10 | Yerleşim: ev S2 5 + 40 kol + 15 kafa çakışma 0 | yeniden 0; kafa × kol ek tarama 0 (en az 26,4) | ✔ |
| 11 | El yakası / boyun adaptörü 45° koni, destek hesabı düzeltmesi | desteksiz; düzeltme tutucu | ✔ |
| 12 | Devrilme rampa 5° (ek istek) | ev 1,58 ✔; S1 −45 1,49, en kötü 1,48, yüklü ileri 1,44 ✘ | **koşul** |

**Koşullar (tasarım / karar; Y2a commit'ini durdurmaz):**
- **KZ1 (devrilme, akü kararı):** akü yerinde kalırsa rampa 5°'de pay ölçütü 1,5 kollar geride / yukarıda-yanda (1,48–1,49) ve elde yükle
  ileri (1,44) sağlanmıyor. Duffy kararı (günlük a/b/c) gelene kadar `yazilim-notu-stowent-170.md` 3. kural (rampada kollar ev pozunda,
  ivme ≤ 0,1 m/s²) **zorunlu** ve "1,65 m / akü yerinde" diye güncellenmeli (Y2b). `taban_montaj` poz listesine ızgara en kötüsü eklenmeli.
- **KZ2 (servo payı):** 0,5 kg el yükünde S1 / S2 0,97, dirsek 0,74 (< 1). `DIRSEK.yuk_g` 500 → 2× pay için ≤ ~100 g ya da servo değişimi;
  karar Duffy, yazılım notuna yük sınırı (Y2b).
- **KZ3 (kafa tilt payı):** çakışma +18° / −17°'de başlıyor; ±15 yazılım sınırına pay 1,5–2,5°. Öneri: yazılım ±13 (ya da kafa kabuğu ↔
  rulman yuvası boşluğu); `kafa_montaj` tilt taraması 1° adımla sınırı raporlamalı.
- **KZ4 (baskı):** kafa kabuğu sağ ön / arka dikiş dili desteksiz değil (tasarımcının açık sorusu) — destekli baskı ya da dikiş biçimi kararı.
- **Belge:** günlük başlığı (1,70 m / 1.235,5), zaman damgaları, sehim 0,336 → 0,371, iki yorum satırı; orkestratör özetinde "teker iz
  genişliği 216" → "teker merkezi x ±216 (iz 432)".

**Commit'e uygunluk:** Y2a dosyaları (çalışma ağacındaki `tasarim/freecad/` değişiklikleri + yeni `kafa10_lib.py`, `kafa7_parcalar.py`,
`montaj/robot-bom.csv`, `yerlesim_kontrol.py`, `yerlesim-kontrol.json`, `kod/ortak/eklem_sinirlari*`, `S1-kaset.md`, `planlama/y2/`)
**commit'e uygun**; `tasarim/solidworks/` ve WhatsApp görseli bu commit'e alınmamalı.

### Değiştirilen / eklenen dosyalar (yalnız `planlama/y2/Y2a-K*`)
`Y2a-kontrol.md` (bu), `Y2a-K-olcum.py` / `.json`, `Y2a-K-devrilme.py` / `.json`, `Y2a-K-tilt.py` / `.json`, `Y2a-K-kz1-cep.json`.
Modül dosyaları, `arayuz.py`, `montaj/`, `tasarim/cad/`, `maliyet.json`'a dokunulmadı; commit yok. Kopya koşu scratchpad'de (proje dışında).
