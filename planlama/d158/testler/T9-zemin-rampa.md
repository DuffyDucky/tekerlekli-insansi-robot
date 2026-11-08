# T9 · Zemin sürtünmesi ve rampa denemesi

Kâğıt T9 / 9 · Lale 1,58 m · sürüm 08.11.2026

| Tarih | Ölçen | Yazan | Kontrol eden | Alet markası/modeli |
|---|---|---|---|---|
| | | | | |

## Amaç

**A** Robotun kullanılacağı her zeminde teker ile zemin arasındaki yanal sürtünme katsayısını (μ) ölçmek.
**B** Robotu 5°'lik bir rampada, kollar ev pozunda, yazılımın ivme sınırıyla sürüp ivmenin 0,1 m/s²'yi geçmediğini ve hiçbir tekerin
kalkmadığını görmek.

## Neden önemli

- **Sürtünme:** yerinde dönüşte motorların ne kadar zorlanacağı μ'ye bağlı; hesap 0,4 / 0,5 / 0,6 senaryolarıyla yapıldı, ölçüm yok.
  "μ ≥ 0,4 çıkarsa ön iki teker omni" önerisi bu ölçüme bağlı (`elektrik.md:159`, `elektrik.md:173-174`).
- **Rampa:** akü yerinde kaldı; bunun şartı rampada kolların ev pozunda olması ve taban ivmesinin **≤ 0,1 m/s²** olması
  (`kararlar:7`). Rampada fren de 0,1 m/s² ile sınırlı (`kararlar:77`). 5° rampada ev pozu devrilme payı 1,61, ölçüt ≥ 1,5
  (`uygulama-notu.md:35`); yüksüz ızgarada 1,517 (`dongu-158.md:24`). Pay küçük: yazılım sınırı tutmazsa robot devrilebilir.

### Doğruladığı varsayım

| Değer | Kaynak | Durum |
|---|---|---|
| μ senaryoları 0,4 / 0,5 / 0,6; ölçülen değer yok | `taban-analiz.json` `donus.varsayim.mu_senaryo`, `mu_olculen: null` | Hesap varsayımı |
| μ ≥ 0,4 → ön omni önerisi | `elektrik.md:159` | Öneri (K1 a) |
| Robot kütlesi 25,911 kg (400 g kablo payı dahil) | `taban-analiz.json` `donus.kutle_kg`, `uygulama-notu.md:7` | Model; akü 3,0 kg güncellemesi (P1.1) henüz işlenmedi |
| Rampa açısı 5° | `kararlar:8` | Tasarımın denetlediği eğim |
| Rampada sürüş ve fren ivmesi ≤ 0,1 m/s², kollar ev pozunda | `kararlar:7`, `kararlar:77`, `eklem_sinirlari.json:108-109` | Karar 29.10 |
| Rampada devrilme payı: ev pozu 1,61, yüksüz ızgara 1,517 (ölçüt ≥ 1,5) | `uygulama-notu.md:35-36`, `dongu-158.md:24` | Hesap; korunan değer |
| Düz zeminde fren ≤ 1,8 m/s², düz sürüş ≤ 0,5 m/s² | `kararlar:78`, `eklem_sinirlari.json:106-107` | Karar 29.10 |
| Motor hızı (en yüksek) 0,393 m/s | `taban-analiz.json` `motor.hiz_m_s` | Hesap |
| Acil stopta motorlar boşa düşer; rampada kayma bu sınırla kapanmaz | `kararlar:83` | Açık risk |
| Elde yükle rampa yasak (500 g'da pay 1,327 < 1,5) | `karar-kuyrugu.md` K9 | Hesap |

## Gereken alet

- Dijital el kantarı (bagaj tartısı), ip; banyo baskülü (robotu tartmak için; ya da robot parça parça)
- 1 m düz çıta, su terazisi, şerit metre (rampa eğimi)
- **Hız ölçümü (ana yöntem):** yazılım arka teker enkoderlerinden hız kaydı verebiliyorsa o kayıt (enkoderler `elektrik.md:450-451`).
  Veremiyorsa: rampanın yanına zemine boylu boyunca yapıştırılmış **şerit metre** (cm bölmeli), tabanın yanına dik bir bant işareti,
  tripodda telefonla yandan video (en az 30 kare/s)
- Telefon ivmeölçer uygulaması (ör. phyphox), bant: **yalnız yardımcı** (adım 11)
- **İki emniyet ipi** (200 kg taşıyan; taban ipi en az **rampa boyu + dayanaktan ipi tutan kişiye mesafe + 1 m**, devrilme ipi en az 3 m): tabana (şasiye) bağlanan **taban ipi** ve gövdeye omuz altından kayışla
  bağlanan **devrilme ipi**; rampanın üst tarafında taban ipinin geçeceği **sabit, sağlam bir dayanak** (ağır tezgâh ayağı, duvar halkası; kapı kolu değil)

## Güvenlik

- **Devrilme (A):** robot 1,58 m ve ~26 kg. A'da yanlamasına çekerken ipi **taban yüksekliğinde** (olabildiğince alçak) bağla. Robot kapalı,
  kollar ev pozunda. İkinci kişi robotun çekilme doğrultusunun dışında (önünde ya da arkasında) durur, gövdeyi itmeden yalnız hafifçe tutar.
- **Rampada acil stop robotu durdurmaz.** Acil stopta motorlar boşa düşer (`kararlar:83`), robot rampadan aşağı yuvarlanır. Rampada robotu
  durduran şey **taban ipidir**; acil stop yalnız motor ve servo gücünü keser.
- **İki ayrı ip (B):**
  - **Taban ipi** (kayma ve yuvarlanma için): tabanın şasisine, teker aksı yüksekliğine bağlanır, rampanın üstündeki sabit dayanaktan geçer.
    İpi tutan kişi robot ilerledikçe boşluğu alır ya da verir; **boşluk her an en çok 10 cm**.
  - **Devrilme ipi**: gövdeye omuz altından kayışla bağlanır, ikinci kişi tutar; **boşluk en çok 10 cm**. Bu ip yalnız devrilmeyi tutar,
    robotu çekmek için kullanılmaz.
- **Düşme hattı:** robotun rampa boyunca önü ve arkası ile çevresinde robot boyu kadar (**1,6 m**, varsayım: robot 1,58 m, devrilirse tepesi
  bu kadar uzağa düşer) alan. İpleri tutanlar, video çeken kişi ve robotu süren / acil stopu tutan kişi bu alanın **dışında**, rampanın yanında ve robottan yukarıda (yan çaprazda) durur; hiç kimse robotun tam arkasında ya da rampanın alt ucunda
  durmaz. Taban ipi dayanaktan geçtiği için ipi tutan kişi robotla aynı doğrultuda durmak zorunda değildir.
- **Hareket varken kimse robota, tekerlere, kollara ya da iplerin robot ucuna el uzatmaz.** Ölçüm aletleri (telefon, bant işareti) enerji
  yokken ve robot düz zemindeyken takılır; deneme sırasında düzeltilmez. Bir şey gevşerse: ipler gerilir, acil stop, robot ipler gergin
  tutularak düz zemine indirilir, sonra düzeltilir.
- **İlk deneme ölçüm için değildir:** en düşük hızla, kısa mesafe; ipleri, sesli komutları ("dur", "ip") ve acil stopu dener.
- Elde yük yok (`karar-kuyrugu.md` K9). Robotun üstüne ya da eline hiçbir şey koyma.
- B, [T1](T1-jgb37-durma-torku.md) sonucu bilinmeden yapılmaz: motor torku yetmezse robot rampada duramaz. T1 KALIR ise B yapılmaz.
- Akü: ana sigorta ve F1 takılı. Motor sürücü ve servo gücü yalnız deneme sırasında açık. Saat, yüzük, bileklik çıkar.

## Yöntem

**A. Zemin sürtünmesi (`elektrik.md:174` yöntemi)**

1. Robotu (ya da eşit yüklü tabanı) tart, kütleyi **m (kg)** olarak yaz. Robot kapalı, tekerler serbest değil (motorlar bağlı, enerji yok).
2. İpi tabana, teker aks yüksekliğine yakın ve robotun **yan** tarafından yatay bağla; kantarı ipe tak.
3. Kantarı yatay tutarak kuvveti yavaşça artır. Robot yana **kaymaya başladığı andaki** en yüksek değeri (F_başlangıç) yaz. Robot yavaşça
   kayarken okunan değeri (F_kayma) yaz.
4. μ = F (kg) ÷ m (kg). (Kantar kg gösterdiği için g sadeleşir.)
5. Her zeminde 3 kez yap; robotun öbür yanından da bir kez çek. Zeminler: sınıf, koridor ve robotun kullanılacağı her yer.

**B. Rampa**

6. Rampanın eğimini ölç: 1 m çıtayı rampaya koy, alçak ucunu su terazisiyle yataya getirecek yüksekliği (h, cm) ölç. Eğim açısı ≈ h ÷ 100 × 57,3°
   (küçük açı). 5° için h = **8,7 cm** (tan 5° × 100).
7. Yazılım ayarlarını kontrol et: `eklem_sinirlari.json` içinde `rampa_surus` 0,1, `rampa_fren` 0,1, `duz_fren` 1,8 (`eklem_sinirlari.json:105-109`).
   Kollar ev pozunda.
8. **Robot düz zemindeyken, enerji yokken:** iki ipi bağla, taban ipini dayanaktan geçir; şerit metreyi rampanın yanına yapıştır, tabana bant
   işareti koy; tripodu düşme hattının dışına kur, kamerayı şeride dik tut. Telefon kullanılacaksa tabana bantla. Adım 13 yapılacaksa
   kantarı da şimdi, taban ipinin dayanak tarafına tak. Herkes yerine geçer, ipler ≤ 10 cm boşlukta.
9. **Hatırlatma: acil stop rampada robotu durdurmaz, taban ipi durdurur.** İlk deneme (düşük hız, kısa) ipleri ve komutları dener. Sonra
   ölçüm denemesi: rampanın altından kalkış → yukarı çıkış → rampada dur (5 s bekle) → aşağı in → düzde dur. 3 kez tekrarla.
   Sabit hız **en az 0,1 m/s** olmalı (adım 10'daki yöntemin şartı); hesapta en yüksek motor hızı 0,393 m/s (`taban-analiz.json` `motor.hiz_m_s`).
10. **İvmeyi hızdan bul (ana yöntem):**
    - **Enkoder kaydı varsa:** hız–zaman kaydından her kalkış ve duruşta a = Δv ÷ Δt, 0,5 s'lik aralıklarla; en büyük değeri yaz.
    - **Video ile:** her kalkışta hareketin başladığı kareyi bul; **1,0 s sonra** (30 kare/s'de 30 kare) bant işaretinin aldığı yolu şeritten
      oku (cm). Her duruşta robotun durduğu kareyi bul; **1,0 s önceki** konumdan durduğu yere kadar olan yolu oku (cm). Sabit kısımda
      20 cm'yi geçme süresinden hızı yaz (v = 0,20 m ÷ süre).
    - Yöntemin dayanağı: durarak başlayan sabit ivmeli harekette 1 s'de alınan yol d = ½ · a · (1 s)²; a = 0,10 m/s² ise **d = 5,0 cm**.
      Sabit hız en az 0,1 m/s ise d ≤ 5,0 cm ancak a ≤ 0,10 m/s² iken olur (ivme daha büyükse robot 1 s dolmadan o hıza ulaşır, yol en az
      v ÷ 2 ≥ 5 cm olur). Duruş için aynı hesap tersinden geçerlidir. Okuma 4–6 cm arasındaysa (varsayım: kare ve şerit okuma payı) sonuç
      sınırdadır: denemeyi tekrarla ya da enkoder kaydı iste.
    - Bu yöntem ivmenin 1 s içinde aşağı yukarı sabit olduğunu kabul eder. Videoda kalkış yumuşak başlayıp sonra sertleşiyorsa (S eğrili
      kalkış) ya da duruş sona doğru sertleşiyorsa **enkoder kaydı esastır**; video sonucu yalnız not olarak yazılır.
11. **Telefon ivmesi yalnız yardımcıdır:** "doğrusal ivme" yerçekimini çıkarırken eğimdeki küçük açı hatasını ivme sanar (1° hata ≈
    9,81 × sin 1° ≈ 0,17 m/s²); bu, 0,10 m/s² sınırından büyüktür, rampa kararında kullanılmaz. Düz zemindeki duruş (sınır 1,8 m/s²) için
    yeterlidir: en büyük mutlak değeri 0,5 s kayan ortalamayla yaz (varsayım: titreşimi süzmek için).
12. **Teker kalkması:** videodan, her tekerin altında zeminle teker arasında boşluk görünüyor mu, kare kare bak.
13. İsteğe bağlı, **yalnız taban ipi boşluksuz gerili ve herkes düşme hattının dışındayken**: robot rampanın ortasında dururken motor gücünü
    kes (PWM 0, sürücü kapalı) ve ipin taşıdığı yükü, adım 8'de dayanak tarafına takılan kantardan alan dışından oku; sonra aynısını acil stop düğmesiyle yap.
    Robot ipe asılı kalır, serbest bırakılmaz. (Kayıt içindir; `kararlar:83` riskini ölçer.)

## Kayıt tablosu

**A. Sürtünme** Robot kütlesi m = ______ kg

| Zemin | Deneme | Yön | F_başlangıç (kg) | F_kayma (kg) | μ_başlangıç = F ÷ m | μ_kayma = F ÷ m |
|---|---|---|---|---|---|---|
| | 1 | sağ | | | | |
| | 2 | sağ | | | | |
| | 3 | sol | | | | |
| | 1 | sağ | | | | |
| | 2 | sağ | | | | |
| | 3 | sol | | | | |
| | 1 | sağ | | | | |
| | 2 | sağ | | | | |
| | 3 | sol | | | | |

**B. Rampa** Rampa yeri: ______  h = ______ cm  Eğim ≈ ______ °  `rampa_surus` = ______ `rampa_fren` = ______ `duz_fren` = ______

Hız yöntemi: ☐ enkoder kaydı  ☐ video + şerit metre

Tablo 1: rampada ivme (video: 1 s'de alınan yol, cm; enkoder: en büyük ivme, m/s²)

| Deneme | Sabit hız v (m/s) | Alttan kalkış | Rampada duruş | Rampadan kalkış (iniş) | Video dosyası |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

Tablo 2: düz zemin ve teker

| Deneme | Düzde duruş, telefon en büyük (m/s²) | Teker kalktı mı (video) |
|---|---|---|
| 1 | | ☐ hayır ☐ evet |
| 2 | | ☐ hayır ☐ evet |
| 3 | | ☐ hayır ☐ evet |

| İsteğe bağlı (taban ipi gerili) | İpteki yük, kantar (kg) |
|---|---|
| Motor gücü kesik | |
| Acil stop | |

## Geçer / kalır sınırı

| Ölçüt | GEÇER | Kaynak |
|---|---|---|
| A: μ_kayma her zeminde (3 denemenin ortalaması) | **0,4 ≤ μ ≤ 0,6** (hesabın senaryo aralığı) | `taban-analiz.json` `donus.varsayim.mu_senaryo` |
| B: rampa eğimi | **≤ 5°** (h ≤ 8,7 cm / 1 m) | `kararlar:8` |
| B: sabit hız (yöntemin şartı) | **≥ 0,1 m/s**; değilse video ölçümü geçersiz, enkoder kaydı gerekir | Bu kâğıdın yöntemi (adım 10) |
| B: rampada her kalkış ve duruşta ivme | **≤ 0,10 m/s²**: video ile 1 s'de alınan yol **≤ 5,0 cm**, enkoder ile Δv ÷ Δt ≤ 0,10 | `kararlar:7`, `kararlar:77` |
| B: düz zeminde duruş (telefon) | **≤ 1,8 m/s²** | `kararlar:78`, `eklem_sinirlari.json:107` |
| B: teker kalkması | **0** (3 denemede de) | `uygulama-notu.md:35` (pay ≥ 1,5 varsayımı) |

μ aralık dışında çıkarsa: μ < 0,4 hesap iyimser yönde yeniden koşulur (kalır sayılmaz, **KOŞULLU**); μ > 0,6 **KALIR** (dönüş yükü hesap aralığının
üstünde). İsteğe bağlı ip yükü ölçümünün kaynakta sınırı yok: yalnız kayıt.

## Sınır aşılırsa

- **μ:** her sonuçta değer `arayuz.py` `TABAN['donus']['mu_olculen']` alanına yazılmak üzere tasarım ajanına verilir (`arayuz.py:661-663`,
  `elektrik.md:173-175`). Omni kararı (K1 a) ve [T1](T1-jgb37-durma-torku.md) motor sonucu birlikte **Ahmet Yorulmaz**'a gider.
- **Rampa > 5°:** o rampa tasarımın dışında; robot o rampada kullanılmaz, Ahmet Yorulmaz'a bilgi.
- **İvme > 0,1 m/s²:** denemeyi durdur. Yazılım ekibine (Efe): ivme sınırı uygulanmıyor ya da yanlış (`eklem_sinirlari.json:105-109`).
- **Teker kalktı:** hemen durdur, robotu indir. Devrilme hesabı (`tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json`, `uygulama-notu.md:35-36`) tasarım ajanında yeniden;
  karar Ahmet Yorulmaz'da.
- İp yükü ölçüldüyse sonuç `kararlar:83` notuna (dinamik fren isteğe bağlı) veri olarak eklenir.
- **Düzde duruş > 1,8 m/s²:** yazılım ekibine (Efe), `eklem_sinirlari.json:107`.

## Sonuç

A ☐ GEÇER ☐ KOŞULLU ☐ KALIR  (μ en düşük ______ / en yüksek ______)   B ☐ GEÇER ☐ KALIR  (rampada en büyük: ______ cm / 1 s ya da ______ m/s²)

Ölçen imza: ____________  Kontrol eden imza: ____________

Kaynak dosyalar için kısaltma tablosu: [00-genel.md](00-genel.md).
