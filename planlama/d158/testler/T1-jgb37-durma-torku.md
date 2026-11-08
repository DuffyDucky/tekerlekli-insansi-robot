# T1 · JGB37-520 durma torku ve akımı

Kâğıt T1 / 13 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

Taban motorunun (JGB37-520, 12 V, 60 dev/dk) mili kilitliyken verdiği en büyük torku (durma torku) ve o andaki akımı ölçmek.
Dört motorun dördü de ölçülür.

## Neden önemli

Dönüş ve rampa hesaplarının hepsi durma torkunu 21 kg·cm kabul ediyor. Bu değer yalnız satıcı etiketi: sayfada "Tork 21KG" yazıyor,
birimi yok, durma mı nominal mi belli değil. Aynı motorun başka bir tablosu benzer oranda yalnız 9 kg·cm diyor. Tork gerçekten
~9 kg·cm ise robot standart tekerle yerinde **dönemez**. Bu yüzden ölçüm **omni teker siparişinden önce** yapılmalı.

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| Durma torku 21 kg·cm | `elektrik.md:124`, `arayuz.py:664`, `taban-analiz.json` `donus.motor.stall_kgcm` | Satıcı etiketi, birimsiz (`elektrik.md:126`) |
| Sürekli tork = durmanın %30'u = 6,3 kg·cm | `elektrik.md:124` | Projedeki ölçüt |
| Durma akımı 2,8 A | `elektrik.md:124`, `arayuz.py:665` | Tahmini |
| Boşta akım 0,08–0,15 A (satıcı), hesapta 0,12 A | `06-aku-secimi.md:15`, `elektrik.md:124` | Satıcı sayfası |
| Risk senaryosu: durma 9 kg·cm / 1,2 A (Aslong tablosu, 1:90 oran) | `elektrik.md:127`, `06-aku-secimi.md:15` | Başka oranın tablosu |
| 9 kg·cm ise standart tekerle yerinde dönüş olmaz | `dongu.md:39`, `elektrik.md:136` | Hesap (`T2_donus_9kg.py`) |
| 1,58 m modelde yerinde dönüş (μ 0,5), en yüklü motor 15,76 kg·cm; ön omniyle 3,16 kg·cm | `taban-analiz.json` `donus.karar` | Hesap, robot 25,911 kg (akü 3,0 kg güncellemesi P1.1 **öncesi** model; +0,2 kg eşiği ~0,1 kg·cm artırır) |
| 5° rampada durmak için motor başına 4,74 kg·cm; 0,25 m/s² ivmede 5,77 kg·cm | `taban-analiz.json` `motor.rampa5_durus`, `motor.rampa5_yavas` | Hesap |
| Ön omniyle yerinde dönüş, en yüklü motor: μ 0,4 / 0,5 / 0,6 için 2,77 / 3,16 / 3,63 kg·cm | `taban-analiz.json` `donus.yerinde_omni` | Hesap |

**Bu kâğıtta türetilen eşikler (hesap, yeni varsayım yok):**
- Rampada izin verilen ivme 0,1 m/s² (`kararlar:7`). 0 ile 0,25 m/s² arasında doğrusal ara değer: 4,74 + (5,77 − 4,74) × 0,1 / 0,25
  = **5,15 kg·cm** motor başına. Sürekli tork bunu taşımalı: durma ≥ 5,15 / 0,30 = **17,2 kg·cm**.
- Ön omniyle yerinde dönüş, sürekli tork bunu taşımalı; eşik zeminin μ'süne bağlı ([T9](T9-zemin-rampa.md) A ölçer):

| Ölçülen μ (T9) | Omniyle dönüş torku | "Ağır" eşiği: durma ≥ |
|---|---|---|
| ≤ 0,4 | 2,77 kg·cm | 2,77 / 0,30 = **9,2 kg·cm** |
| ≤ 0,5 | 3,16 kg·cm | 3,16 / 0,30 = **10,5 kg·cm** |
| ≤ 0,6 | 3,63 kg·cm | 3,63 / 0,30 = **12,1 kg·cm** |

T9 henüz yapılmadıysa en kötü satır (μ 0,6 → **12,1 kg·cm**) kullanılır. μ 0,6'nın üstü hesap aralığı dışındadır (T9 KALIR).

## Gereken alet

- Ayarlı laboratuvar güç kaynağı (12,0 V, akım sınırı ayarlanabilir, en az 5 A)
- Multimetre ×2 (biri motor ucunda gerilim, biri seri akım) ya da kaynağın kendi akım göstergesi (tercih: denemeler kısa, ama 2–5 A geçer)
- Dijital el kantarı (bagaj tartısı), 10 g çözünürlük
- Motor mile takılan **100 mm kol**: düz alüminyum lama ya da sert çıta, mile vidalı göbekle; kolun ucunda ip deliği
- Mengene (yumuşak çeneli) ya da motor braketi + işkence
- Kumpas / çelik cetvel (kol boyu için), kronometre, koruyucu gözlük

## Güvenlik

- **Akü kullanma; laboratuvar kaynağı kullan.** Akım sınırını **5,0 A**'e ayarla. Bu yalnız bu düzeneğin sınırıdır (tahmini durma akımı
  2,8 A'in üstünde pay; `elektrik.md:124`), robottaki sigortayla ilgisi yoktur.
- **Multimetreyle akım:** [00-genel.md](00-genel.md) "Multimetreyle akım ölçümü" kuralı. Kısaca: kırmızı uç 10 A soketine, yalnız seri,
  enerji kapalıyken bağla; iş bitince kırmızı uç V soketine geri; 10 A kademesinin süre sınırına uy.
- **Saat, yüzük, bileklik çıkar.**
- Mil kilitliyken motor hızla ısınır: her durma denemesi **en çok 5 s** (varsayım: kısa tutmak için), denemeler arası en az 1 dk soğuma (varsayım).
- Kol döner: enerji varken **kimse kola, ipe, kantara ya da mile el uzatmaz**; kantar sabit noktaya bağlıdır, elde tutulmaz. El, saç, kablo
  kolun dönme düzleminden uzak. Kantar ipi kopabilir; ipin doğrultusunda durma. Okumayı kantar ekranından, uzaktan yap.
- Motor gövdesi mengeneye sıkı ama ezilmeden bağlanır. Koruyucu gözlük takılır.

## Yöntem

Kaynak yöntem: `elektrik.md:173-175` ("100 mm kol + el kantarı, F × 0,1 m").

1. Motora bir numara ver (M1 ön sol, M2 ön sağ, M3 arka sol, M4 arka sağ). Etiketini kâğıda yaz.
2. **Boşta deneme:** kol takılı değil. Kaynağı 12,0 V'a ayarla, motoru çalıştır. Boşta akımı oku. Milin 30 s'de kaç tur attığını
   say (mile bant işareti koy) → dev/dk = tur × 2.
3. Kolu mile tak. Mil ekseninden ip deliğine kadar olan boyu kumpasla ölç, **L (cm)** olarak yaz (hedef 10,0 cm).
4. Motoru mengeneye sıkıştır. Kantarı ipi kolun ucuna bağla, kantarın öbür ucunu sabit bir noktaya bağla.
   İp kola **dik** (90°) olmalı; kol yatayken ip düşey ya da kol düşeyken ip yatay. **Enerji vermeden önce** kolu elle ipe doğru çevirip
   ipi boşluksuz ger (kantar birkaç on gram göstersin): ip gevşek kalırsa kol hızlanıp ipe çarpar, kantar torku olduğundan büyük gösterir.
5. Kaynağı 12,0 V'a kur, ellerini çek, enerji ver. Motor durur. İlk darbe tepesini değil, **1–2 s sonraki kararlı** kantar değerini, akımı ve
   motor ucundaki gerilimi oku; en çok 5 s içinde enerjiyi kes.
   **Kaynak akım sınırına girdi mi?** Bunu **yalnız kaynağın kendisi** söyler: CC lambası yandıysa ya da kaynağın akım göstergesi **5,0 A**'de
   durduysa bu denemenin torku **geçersizdir** (motor tam gerilim görmedi). Tabloya "CC" yaz ve sonucu aşağıdaki "kaynak sınıra girdi" satırıyla değerlendir.
   **Kaynak CC'de değil ama motor ucundaki gerilim 12,0 V'un altındaysa** bu CC değildir: seri multimetre ve kablolar gerilim düşürür. Enerjiyi
   kes, kaynağın gerilimini biraz artır (en çok 12,8 V, akü nominali `elektrik.md:54`) ve denemeyi tekrarla; motor ucunda **12,0 V** okunana
   kadar böyle ayarla. **Kaynak 12,8 V'a çıktığı hâlde motor ucunda 12,0 V okunmuyorsa seri multimetreyi çıkarmak zorunludur:** enerjiyi
   kes, multimetreyi hattan çıkar (kırmızı ucu V soketine geri tak), kabloyu doğrudan bağla, akımı kaynağın kendi göstergesinden oku ve denemeyi
   tekrarla. Seri multimetre çıkmışken de motor ucu 12,0 V'a ulaşmıyorsa kablo ve bağlantıları (kısa, kalın kablo; sıkı klemens) düzelt;
   düzelene kadar o denemenin torku tabloya "düşük V" notuyla yazılır, değerlendirmeye katılmaz. Bu ayarlarla uğraşmamak için baştan da
   seri multimetresiz çalışabilirsin.
6. Tork (kg·cm) = kantar (kg) × L (cm). L = 10 cm ise kantar × 10.
7. 1 dk bekle, 5–6. adımı iki kez daha yap (3 deneme). Ortalamayı yaz.
8. Dört motor için 1–7'yi tekrarla.
9. İsteğe bağlı: aynı ölçümü akü nominal gerilimi 12,8 V'ta bir kez yap (`elektrik.md:54`).

## Kayıt tablosu

Boşta:

| Motor | Gerilim (V) | Boşta akım (A) | 30 s'de tur | dev/dk |
|---|---|---|---|---|
| M1 | | | | |
| M2 | | | | |
| M3 | | | | |
| M4 | | | | |

Durma (L = ______ cm):

| Motor | Deneme | Gerilim, motor ucu (V) | Kantar, kararlı (kg) | Tork = kantar × L (kg·cm) | Durma akımı (A) | CC? / not |
|---|---|---|---|---|---|---|
| M1 | 1 | | | | | |
| M1 | 2 | | | | | |
| M1 | 3 | | | | | |
| M2 | 1 | | | | | |
| M2 | 2 | | | | | |
| M2 | 3 | | | | | |
| M3 | 1 | | | | | |
| M3 | 2 | | | | | |
| M3 | 3 | | | | | |
| M4 | 1 | | | | | |
| M4 | 2 | | | | | |
| M4 | 3 | | | | | |

| Özet | M1 | M2 | M3 | M4 | En düşük / en yüksek |
|---|---|---|---|---|---|
| Ortalama durma torku (kg·cm) | | | | | |
| Ortalama durma akımı (A) | | | | | |

## Geçer / kalır sınırı

Değerlendirmede **dört motorun en düşük ortalama torku** ve **en yüksek ortalama akımı** kullanılır. "CC" yazan denemeler torka katılmaz.

| Sonuç | Koşul | Anlamı |
|---|---|---|
| **GEÇER** | Tork ≥ **21,0 kg·cm** ve akım ≤ **2,8 A** | Hesap varsayımı doğru. Yalnız ölçülen değerler hesaba girilir |
| **KOŞULLU** | 17,2 ≤ tork < 21,0 kg·cm, ya da 2,8 < akım < 5,0 A | Hesap ölçülen değerle yeniden koşulur; rampa sürekli torku hâlâ yeter |
| **KALIR** | Tork < **17,2 kg·cm** | Rampada (5°, 0,1 m/s²) sürekli tork yetmez |
| **KALIR** | **Kaynak 5,0 A sınırına girdi** (CC lambası ya da kaynak göstergesi 5,0 A; motor ucundaki düşük gerilim tek başına CC sayılmaz) | Durma akımı ≥ 5,0 A: tahminin (2,8 A) ~1,8 katı; 4 motorda ≥ 20 A, motor akım bütçesi (4 × durma 11,2 A, `elektrik.md:319`) yeniden yapılmalı. Tork bu düzenekte ölçülemedi |
| KALIR, ağır | Tork < "ağır" eşiği (yukarıdaki tablo: μ'ye göre 9,2 / 10,5 / 12,1 kg·cm; T9 yoksa 12,1) | Ön omniyle de yerinde dönüş sürekli sınırın üstünde (`elektrik.md:139`: "≤ 10 kg·cm çıkarsa omni tek başına yetmeyebilir") |

Boşta devir ve akım yalnız kayıttır (beklenen 60 dev/dk, 0,08–0,15 A; `elektrik.md:124`, `06-aku-secimi.md:15`).

## Sınır aşılırsa

- **Her sonuçta:** ölçülen tork ve akım tasarım ajanına verilir; `arayuz.py:661-665` içindeki `stall_kgcm_olculen` ve `stall_A_olculen`
  alanlarına yazılır, `taban_montaj.py` yeniden koşulur (`elektrik.md:118-119`). Elle güncellenen yerler: `elektrik.md` E0 tabloları ve
  akım bütçesi (`elektrik.md:319`).
- **KOŞULLU / KALIR:** yeni madde `karar-kuyrugu.md`'ye; karar **Ahmet Yorulmaz**'da. Kaynakta geçen seçenekler: ön omni (K1 a,
  `elektrik.md:159`), daha düşük devirli (yüksek oranlı) JGB37 ya da daha güçlü motor (`elektrik.md:139`). **Omni siparişi bu sonuçtan önce verilmez.**
- Yazılımdaki "> 2,0 A'de dönüşü kes" eşiği (`elektrik.md:170`) bu ölçümden sonra yazılım ekibiyle (Efe) yeniden yazılır (`elektrik.md:137`).

## Sonuç

☐ GEÇER  ☐ KOŞULLU  ☐ KALIR    En düşük tork: ______ kg·cm   En yüksek akım: ______ A

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
