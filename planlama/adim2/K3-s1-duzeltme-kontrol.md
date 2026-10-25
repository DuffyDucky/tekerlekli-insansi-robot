# K3 — S1 kaseti düzeltmeleri (K1–K6) bağımsız kontrol (plan Y1b kontrol)

Kontrol ajanı (bağımsız; modül dosyalarına dokunmaz). Dal `lale-duzeltme`, HEAD `102f246` + çalışma ağacındaki Y1b değişiklikleri.
Girdi: `K2-s1-kontrol.md` (K1–K6), `S1-duzeltme-gunluk.md`. Ölçüm betikleri `planlama/adim2/K3-*.py` (tasarım ajanının
`S1-duzeltme-kontrol.py`'si kullanılmaz). Durum: **kapandı — KOŞULLU GEÇTİ** (26 Ekim 2026; aşağıda "Sonuç").

## Günlük
- 2026-10-25: açıldı. Okundu: CLAUDE.md, dongu.md, K2-s1-kontrol.md, S1-duzeltme-gunluk.md, `git diff` (arayuz, omuz_parcalar,
  kabuk_parcalar, dirsek_montaj, carpisma, carpisma_kos, eklem_sinirlari).
- Betikler: `K3-olcum.py` (adımlar ip | pah | cep | pim2 | duvarip | ev | montaj → `K3-<adım>.json`), `K3-cep-dogrula.py` (cep
  yeniden kurulumu ↔ FCStd), `K3-cep-hesap.py` (K4 varyant HESABI, model dosyasına dokunmaz), `K3-tarama.py` (nokta bulutu taramaları),
  `K3-taslak.py` (taslak-170), `K3-regresyon.py` (sistem Python). K2 kontrolünün `K2-ortak.py` / `K2-u.py` (bağımsız çözücü) kullanılır.
- **Regresyon (`K3-regresyon.json`, HEAD 102f246 ↔ şimdi):** omuz 73 → 75 parça (yalnız +2 ip), kütle farkı yok (tork 4,90 → 4,91);
  kabuk 206 parça, kütle 4.921,5 → 4.922,3 g (kaset gövdesi 8,8 → 9,0, kapak 6,75 → 6,83; zarf 108,8 → 111,4 = kulak); dirsek 53,
  kaset ↔ kol 1,25 → 1,36 (her satırda +0,1…0,7: pah); taslak 1.060 → 1.064 parça, 24.510,5 → 24.511,3 g. Kasıt dışı değişiklik yok.
  `eklem_sinirlari.json` = üretici, `--kontrol` 0; `eklemler` HEAD ile aynı, yalnız `bagimli` (r + l) eklendi; `bagimli`'yi okuyan
  yazılım yok (yalnız üretici). omuz serbest pozlarında (S2 −5/−10, aralık dışı) yeni "kol çatalı ↔ ip" 0,8 / 1,6 mm³ (bilgi).
- **K2 ip (`K3-ip.json`):** ip ↔ tambur ortak 0; ip r 37,10…43,60, x 153,2…158,6. S1 −60…180 / 1°: ip ↔ kaset kapağı **0,600**
  (S1 34), ↔ kapak cıvatası 0,809, ↔ rulman kapağı 1,20, ↔ omuz bandı 1,20 (≥ 0,3 ✔). Düğüm modeli (1,2 küp, demet üstü): ↔ kapak 1,80.
  ip/düğüm ↔ kol (S2 5…120) 4,78; ↔ S2 lopu 19,3; ↔ geçiş (son 8 mm hariç) 7,05; ↔ çıkış 5,50. Düğüm erişimi (Ø4 radyal sonda):
  S1 −60…30 açık (S2 5 ve 90). Tambur ip yolu kesitleri: halka deliği x 153,2…153,65 / 158,15…158,6 (**0,45 mm**), oluk r 37…37,5.
  **Baskı riski:** tambur +X basılıyor → 0,45 mm'lik delik 2 katman (0,2) yüksekliğinde yatay delik; köprü/sarkmayla kapanır.
- **K3 pah / S2 lopu (`K3-pah.json`):** pah iç r x 158,32 → 44,22, 159,48 → 45,38 (1,2 × 45° ✔). S2 lopu ↔ flanş: izinli bölgede
  en az **0,656** (S1 → 120⁻, S2 120; S1 119,5'te 0,739), S1 ≥ 120 × S2 117 **0,892**; yasak bölgede (S1 ≥ 122,5, S2 120) 0,391 /
  dikdörtgen 0,416 → sınır dışında bile temas yok.
- **K4 cep (`K3-cep.json`, `K3-cep-dogrula.py`):** FCStd U ucu engeli ölçümünde eşik **L +2,7 mm / S1 +3,8°** (tasarımcıyla aynı),
  ama sınırlayan **cep duvarı değil, üst uç pimi dikmesi** (ψ 331,3, r 57, post r 3,5): U ucu (ψ 324,3) ↔ pim dikmesi 1,36 mm (φ 135).
  Pim yeri `kabuk_parcalar` kuralında yalnız U'ya bağlı (u_pay'den bağımsız) → u_pay 7,0 eşiği değiştirmez. Varyant hesabı: `K3-cep-hesap.json`.
- **pim2 (`K3-pim2.json`):** kulak gövde 220,8 / kapak 68,0 mm³, r 77,2…83,1; kaset ↔ kabuk ortak 0; pim kapakta, delik boş, delik
  çevresi dolu; gövde ↔ kapak 0,378 mm³ (x 158,30…158,31 modelleme bindirmesi). Kulak ↔ kol (S1 −45…135 / 2,5 × S2 5…120) en az
  **4,13** (S1 120, S2 5, tüp); kulak ↔ göbek > 5.
- **K4 HESAP (`K3-cep-hesap.json`; yeniden kurulum FCStd ile doğrulandı: 6,5 / pim boşluğu 0,5 → eşik L +2,73 / S1 +3,80 = FCStd ölçümü):**

  | varyant (u_pay / pim `bosluk`) | pim ψ | eşik L (duvar / pim) | eşik S1 (duvar / pim) | U ucu ↔ pim (φ 135) | kaset uç ψ | taban y_max |
  |---|---|---|---|---|---|---|
  | 4,5 / 0,5 (eski) | 331,27 | **+0,77** (0,77 / 2,73) | **+1,07°** | 1,36 | 333,72 | 56,38 |
  | **6,5 / 0,5 (mevcut)** | 331,27 | **+2,73** (4,68 / **2,73**) | **+3,80°** (6,52 / **3,80**) | 1,36 | 333,72 | 58,38 |
  | 7,0 / 0,5 | 331,27 | +2,73 (5,65 / 2,73) | +3,80° (7,88 / 3,80) | 1,36 | 333,72 | 58,88 |
  | **6,5 / 1,0** | 331,77 | **+3,73** (4,67 / 3,73) | **+5,19°** (6,52 / 5,19) | 1,85 | 334,18 | 58,38 |
  | 7,0 / 1,0 | 331,77 | +3,73 | +5,19° | 1,85 | 334,18 | 58,88 |
  | 6,5 / 1,5 | 332,27 | +4,66 (duvar) | +6,51° | 2,35 | 334,64 | 58,38 |

  Sonuç: 6,5'te sınırlayan **üst uç pimi dikmesi**; **u_pay 7,0 hiçbir şey kazandırmaz** (yalnız taban +0,5 büyür). Hedef (+3 mm / +4°)
  pim boşluğu 0,5 → 1,0 ile sağlanır (pim ψ +0,5°, kaset ucu ≈ +0,6 mm, y_max değişmez). Aralık içindeki en küçük değer (dış temas
  geçişi, 0,30–0,34) tüm varyantlarda aynı ve u_pay'den bağımsız (tasarım teması bölgesi).
- **Duvar bağı ipi (`K3-duvarip.json`):** ψ 226,5 / 230'da arka yarık ve üst çentik açık, yanlarında duvar dolu. İlmek modeli (Ø0,4 kare):
  gövde / kapak / kabuk ile ortak 0; kapak flanşına 0 (temas), omuz bandına 1,20; demetle 0,168 mm³ (= +x radyal kolda 0,1 mm: eksenel
  toplam boşluk arka plaka ↔ flanş − demet = 1,1, iki ip kolu 0,8 → demet −x'e 0,1 kayar, kalan 0,3). Duvar dışı radyal boşluk omuz
  bandına x 153,6'da 1,6–1,7, x 155,9'da 3,9–4,0, x 157,5'te 5,5; Ø4 radyal sonda x 155,9 / 157,5'te serbest (x 153,6'da banda girer)
  → düğüm duvarın dışında x ≈ 156–158'de atılabilir. İlmek ↔ hareketli (göbek + kol) en az 4,77.
  Ek varyantlar: **6,0 / 1,0 → L +3,69 / S1 +5,15°, y_max 57,88**; 5,75 / 1,0 → +3,21 / +4,47°, y_max 57,63 (duvar sınırlar).
- **Görünüm (`K3-gorunum.py` → `K3-gorunum.json`, S1-gorunum yöntemi, HEAD FCStd ↔ şimdi):** kaset omuz bandı üstünden **26,38 → 28,38 mm**
  (+2,0, u_pay 4,5 → 6,5'in doğrudan sonucu); ön / yan taşma değişmedi (−43,7 / 7,5). Tasarımcının "görünüm uç değerleri değişmez"
  notu (günlük, B9 maddesi) yalnız kulak için doğru; cep büyümesi üst taşmayı 2 mm artırdı (belge düzeltmesi).
- **K6 bağımsız (`K3-ev.json`, 125 modül, kol zinciri Pr(S2)):** S2 0: kol çatalı ↔ tambur 97,87, tüp ↔ tambur 65,01, tüp ↔ kaset
  kapağı **6,42** (önce 7,61; pah azalttı); 3,0: 6,98 / 0,84; 3,5: 0,165; **3,75 / 4 / 5 / 6: 0** (S2 5'te en küçük 0,825 çatal ↔ tambur).
  `carpisma-bolum/statik.json`: S2 5'te 0, S2 0 bilgi 2 (yalnız modüller arası tüp ↔ kapak, sağ/sol; tambur çiftleri modül içi →
  omuz_montaj `statik_s2_0`). `taslak-analiz.json` yerleşim: S2 5'te 0, S2 0 bilgi 4 (tüp ↔ tambur / kapak, iki yan; kol çatalı ↔
  tambur ikisi de "aynı" parça olduğundan kısa kontrol kapsamı dışında). Mantık doğru; sol kol S2 5'te çakışmasız → dönüş yönü dışa.
- **K5 radyal montaj (`K3-montaj.py` → `K3-montaj.json`; nokta bulutu 0,4 + kesin common; yön = parça ψ ortalaması ±15°, s 0…90 mm;
  hedef kabuk + göbek + kol, kapak için gövde):** 6 poz (S1 −45 / −20 / 0 × S2 90, S1 −45 × S2 5, S1 0 × S2 30, S1 45 × S2 90) × 3 yön:
  **gövde x 0: 18/18 çakışmasız** (yalnız omuz bandına kayma teması 0); **kapak x +3,3: 18/18** (gövdeye 0,002–0,007 sıyırma);
  **kapak x +3,5: 18/18** (S1 −45 / −20'de göbeğe 0,004–0,008 → pratikte temas; S1 ≥ 0'da 0,2). Son eksenel adım (3,5 → 0) yalnız
  t 0'da gövde 0,378 mm³ (bilinen kulak bindirmesi). Belgelerdeki sıra (S1 −45'te en çok +3,3) doğru. Not: ilk deneme (`K3-olcum.py
  montaj`, kesin distToShape) çok yavaş olduğu için durduruldu; sonuç `K3-montaj.py`'den.
- **taslak-170 kıyas (`K3-taslak-kiyas.json`):** S1 çevresi 70 modül parçasından **69'u taslakta birebir** (iki yan; ortak hacim oranı
  1,0): tambur, iki ip, kaset gövdesi / kapağı dahil. Farklı yalnız üst kol tüpü (+30, beklenen). **Ev pozu (`K3-taslak-ev.json`):**
  iki yan 125 ile aynı (S2 0: 97,87 / 65,01 / 6,42; 3,5: 0,17; ≥ 3,75: 0; S2 5 en küçük 0,825).
- **Tam poz taramaları (125, `K3-tarama-*.json`; nokta bulutu + en küçük pozlarda kesin):**
  - kaset ↔ kol zinciri (omuz Kol + dirsek UstKol + OnKol + El), S1 −45…135 / 2,5 × S2 5…30 / 0,5 + 35…120 / 5 (5.037 poz), dirsek 0:
    en az **1,358** (S2 5, S1 22,5…130 hepsinde; kapak ↔ üst kol tüpü; önce 1,254 → pah +0,10), S2 5,5 → 1,76, 6 → 2,11, ≥ 10 → ≥ 5,0;
    ön kol / el 25 mm'ye girmiyor. Dirsek 52,5 / 105 adımları süre nedeniyle (≈ 80 dk / açı) durduruldu → taslak taramasıyla ve
    `dirsek-analiz` s1_carpisma (dirsek 0 / 52,5 / 105, 1,36) ile kapsandı.
  - tambur + ip ↔ sabit (omuz gövde, kabuk sağ, kaset), S1 −60…180 / 1°: **0,50** (kaset gövde/kapak; tasarım boşluğu, değişmedi);
    ip'in kesin değeri 0,60 (`K3-ip.json`). tambur + ip ↔ kol: S2 5 **0,842** (bulut) / 0,825 (kesin), 3,75 0,063, 3,5 temas 0,165 mm³.
  - göbek (tambur hariç, ip dahil) ↔ kaset + kabuk, S1 −60…180: en az **0,60** (ip ↔ kaset kapağı, S1 47…71) ✔.
- **taslak-170 kol ↔ kaset (`K3-taslak-kolkaset.json`, S1 −45…135 / 5 × S2 5…20 / 1 + 25…120, dirsek 0 / 52,5 / 105, 2.664 poz):**
  üç dirsek açısında da en az **1,358** (S2 5, kapak ↔ tüp); ön kol / el 25 mm'ye girmiyor. → S1 kaseti çevresinde yeni çakışma yok.

## Sonuç (26 Ekim 2026) — KOŞULLU GEÇTİ (125 ve taslak-170 için aynı)

| # | Madde | Ölçüt | Ölçülen (bağımsız) | Durum |
|---|---|---|---|---|
| K1 | PVC 22 AWG, tel ≤ 1,5 mm | belge | arayuz notu + S1-kaset.md + M6 ✔; S1-kaset.md eski "Açık sorunlar 1" ve `maliyet.json` satır 50 (S2 1.105) hâlâ eski metin | geçti (belge notlu) |
| K2 | tambur bağlama ipi | ip ↔ sabit ≥ 0,3, S1 tam aralık | ip ↔ kapak 0,60, cıvata 0,809, rulman kapağı / bant 1,20; tambur ortak 0; düğüm 1,80; ↔ kol 4,78, S2 lopu 19,3, geçiş 7,05, çıkış 5,50; düğüm erişimi S1 −60…30 | geçti; **baskı riski**: halka deliği eksenel 0,45 mm (+X baskıda 2 katman) |
| K3 | pah + S1 ≥ 120 → S2 ≤ 117 | izinli bölgede ≥ 0,5 | pah 44,22 → 45,38 ✔; izinli en az 0,656 (S1 → 120⁻, S2 120); S1 ≥ 120 × S2 117 0,892; sınır dışı (S2 120) 0,391 > 0; JSON = üretici ✔ | geçti |
| K4 | U ucu payı | ≥ L +3 mm / S1 +4° | **L +2,73 / S1 +3,80°**; sınırlayan üst uç pimi dikmesi (duvar tek başına +4,68 / +6,52°) | **koşul** |
| K5 | önden radyal montaj | çakışma 0 | gövde x 0: 18/18; kapak x 3,3: 18/18; x 3,5: 18/18 (S1 −45/−20'de göbeğe 0,004–0,008); eksenel son adım 0 (kulak 0,378 bindirmesi hariç) | geçti |
| K6 | ev pozu kontrolü S2 5 | S2 5 = 0, S2 0 bilgi | 125 ve taslak: S2 5 0 (en az 0,825), S2 0 üç çift (6,42 kapak), ≥ 3,75 0; carpisma/taslak JSON'ları tutarlı | geçti |
| B9 | ikinci pim + kulak | kabuk / kol çakışmasız | kabuk ortak 0; kol en az 4,13; göbek > 5; pim kapakta, delik boş; gövde ↔ kapak 0,378 mm³ (0,01 mm modelleme bindirmesi) | geçti (notlu) |
| K4b | duvar bağı ipi | delik + montaj | delikler açık; ilmek kabuk/kaset ortak 0; eksenel pay 1,1 − 0,8 = 0,3 (demet 0,1 −x kayar); düğüm x 156–158 dışarıda erişilebilir | geçti |
| B10 | S2 kablosu göbekte ek, uzatma | hesap | 125: 1.541 / 1.541 / 1.385; taslak ≈ 2.006 / 2.038 / 1.820 → iki kol 11,73 m (+%10 12,9) ✔ (göbek ekinin yeri modelde yok, tahmini) | geçti (notlu) |
| R | regresyon | kasıt dışı değişiklik yok | omuz +2 ip; kabuk +0,8 g, kaset zarfı +2,6 (cep + kulak); dirsek yalnız kaset ↔ kol 1,25 → 1,36; taslak 1.064 parça, 24.511,3 g; `dirsek_montaj` istisnası doğru (ip yalnız U / geçiş / çıkış hedefinden çıkarılmış; S2 lopu ipi görüyor, 1,90 değişmedi) | geçti |
| G | görünüm | — | üst taşma 26,38 → **28,38** (+2,0, u_pay); tasarımcının "görünüm değişmez" notu yanlış | belge |
| T | tam tarama (125 + taslak) | yeni çakışma yok | kaset ↔ kol 1,358 (S2 5), tambur 0,50, göbek/ip 0,60 | geçti |

**Koşullar (tasarım ajanına; ikisi de tek parametre, M6/Y2 ilerlemesini durdurmaz):**
- **KZ1 (K4):** `arayuz.KOL_KABLO["s1"]["duvar"]["pim"]["bosluk"]` **0,5 → 1,0**; `u_pay` **6,5 kalır** (7,0 yapılmamalı: pim
  sınırladığı için eşik değişmez, yalnız kaset üstte +0,5 mm büyür). Beklenen (HESAP): L +3,73 / S1 +5,19°, pim ψ 331,3 → 331,8, kaset
  ucu ≈ +0,6 mm (ψ 333,7 → 334,2), y_max / görünüm değişmez, kapak pimi aynı kuralla kayar. İsteğe bağlı: u_pay 6,0 + bosluk 1,0 →
  +3,69 / +5,15°, üst taşma 2,0 yerine 1,5 (duvar ve pim birlikte sınırlar). Yeniden üretimden sonra U ucu eşiği yeniden ölçülmeli.
- **KZ2 (K2 baskı):** tambur ip yolunun halka deliği eksenel genişliği 0,45 → **≥ 0,8** (yalnız kanal altında, x 153,2…154,0 ve
  157,8…158,6; demet halkaya yine oturur). Alternatif: baskıdan sonra Ø0,5 iğne/matkapla açma talimatı (M6 G0).
- **Belge düzeltmeleri:** S1-kaset.md "Açık" satırı "u_pay 7,0" → KZ1; "görünüm değişmez" → +2,0 mm (28,4); eski "Açık sorunlar 1"
  silikon cümlesine ESKİ işareti; duvar ipi için montaj notu "demet −x'e itilir (eksenel pay 0,3)". `maliyet.json` S2 boyu Y2'de.
- Açık (değişmedi): B11 yasak kutu kol koşulu yana [5, 5] (öneri [5, 15]); `bagimli` sınırı yazılım henüz okumuyor (yazılım yok);
  göbek S2 eki CAD'de yok (Y3 M6); M7 kaset + gerçek kablo 10⁴ döngü kuponu.

### Değiştirilen / eklenen dosyalar (yalnız `planlama/adim2/K3-*`)
`K3-s1-duzeltme-kontrol.md` (bu), betikler `K3-olcum.py`, `K3-cep-dogrula.py`, `K3-cep-hesap.py`, `K3-gorunum.py`, `K3-montaj.py`,
`K3-tarama.py`, `K3-taslak.py`, `K3-regresyon.py`; çıktılar `K3-{ip,pah,cep,cep-hesap,pim2,duvarip,ev,gorunum,montaj,regresyon}.json`,
`K3-tarama-{kaset,tambur,gobek}.json`, `K3-taslak-{kiyas,ev,kolkaset}.json`. Modül dosyaları, `arayuz.py`, `montaj/`, `tasarim/cad/`,
demo, `maliyet.json`'a dokunulmadı; commit yok. (HEAD FCStd geçici kopyası scratchpad'de, proje dışında.)
