# P10.7b2d-A birleşim sınaması (F10l-gunluk.md § 3; düzeltme turu 1: § 9). Depoya yazmaz. FreeCAD istemez.
#   py -3 -B -X utf8 planlama/d158/F10l-birlesim.py [ROBOT] [commit]
# Düzeltme turu 1'den sonra K1 / K2 metni önceki commit'le (1c4e882) birebir aynı değil: çapalar silindi, "madde N" göndermeleri kart
# numarasına çevrildi (F10l-kontrol D2), bara uçları tek karta taşındı ve saplama yer tutucuları eklendi (D1), K2'de bir paragraf
# bölündü (N4), K2'ye bir cümle eklendi (N3). Düzeltme turu 2 (F10l-kontrol-2; § 10): 17.1'e G05 akü ucu cümlesi (D1), 17.4'e
# Kablo yolu 3 cümlesi (D2), dört "N." saplama biçimi "N numaralı" (N2). Sınama üç parça:
#   A  yapı: ana metin + alt adımlar (sırayla) = ALT_TAM_HAM; ALT_TAM_HAM = kaynaktaki çapalı metnin (ALT_KAYNAK_HAM) çapası silinmiş,
#      göndermesi çevrilmiş hâli (paragraf paragraf).
#   B  cümle çokluğu (bütün kaynak metinleri, yer bağımsız, yer tutucular çözülmüş): çapa ve gönderme biçimi eşitlenir (çapa silinir;
#      "madde N", "K2 madde N", "alt adım S.M", "bu alt adımda aşağıda / yukarıda" → §G). Kalan eklenen / silinen cümleler BEKLENEN
#      listesiyle TAM eşit olmalı; listede olmayan fark da, listede olup gerçekleşmeyen fark da hatadır.
#   C  gönderme biçimi eşitlenmeden: çevrilen her gönderme sayılır (rehber_metin.GONDERME_KAYIT), çözülemeyen 0.
import os, sys, re, subprocess, types, collections
ROBOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEAD = sys.argv[2] if len(sys.argv) > 2 else "1d7fb71"          # P10.8b: taban 1d7fb71 (b2k'de 896c9a7) (b2i'de 8bca2f5) (b2h'de 376fe90) (b2g'de 9b019d2) (b2f'de b5fc255, b2e'de 84f1a4a, b2d'de 1c4e882)
RH = os.path.join(ROBOT, "tasarim", "freecad", "rehber")
sys.path.insert(0, RH)
b = subprocess.run(["git", "show", HEAD + ":tasarim/freecad/rehber/rehber_metin.py"], cwd=ROBOT, capture_output=True, check=True).stdout
ESKI = types.ModuleType("rehber_metin_head")                       # dosyaya yazmadan, bellekte
ESKI.__file__ = os.path.join(RH, "rehber_metin.py")
exec(compile(b.decode("utf-8"), HEAD + ":rehber_metin.py", "exec"), ESKI.__dict__)
import rehber_metin as YENI
import rehber_denetim as RD

# Beklenen farklar (norm biçiminde, § 9'da cümle cümle "eski → yeni + gerekçe"). (sınıf, cümle)
_G06 = ("Şarj kolu (G06, 16 AWG): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına gidecek (G03 ile aynı "
        "saplama, mavi M5 halka pabuç, ana anahtarın saplama ölçüsü kablajda teyit; F1'de takılır); 7,5 A mini hat sigortasının kapaklı "
        "yuvası ana anahtar girişindeki ucun dibinde (kaynak ucu), kuyruğuna lehim + makaron; öbür uç etekteki XT60E-M şarj girişine (F1); "
        "− ucu yıldız barası")
_G07 = "Akü ölçüm bölücüsü (G07, 22 AWG): ana anahtar çıkışı (bölücünün üst direnci bu uçta) → güç paneli üstü → kat üstü → arayüz kartı, bölücü orta noktası"
_ALT = "Alt kat kartlarının (iki BTS7960B, XL4016 A / B / çevre) klemens uçları B3'te, kat ve güç paneli gelmeden bağlandı"
_BUR = "Burada B3'te etiketli bırakılan öbür uçları yerlerine bağla: "
_SON = ("G19'u arayüz kartının çevre 5 V / GND klemensine; SV1'i dağıtım kartı A'nın, SV2'yi dağıtım kartı B'nin V+ / GND giriş "
        "klemensine (OUT+ → V+, OUT− → GND).")
_F1 = ("F1 20 A → röle K1 kontağı (30 → 87 (87a boş); soketin kuyruk numaraları kablajda teyit: G08 sigorta kutusundan girişe, G09 "
       "çıkıştan anahtarlı bara%s; 12 AWG); F1 → ön şarj kartı → anahtarlı bara (G10, G11; 12 AWG).")
_G10 = ("Sonra G10'u K2 kontağının girişine lehimle, ön şarj direnci (5,6 Ω) çıkış ucunda, G11 direncin öbür bacağından %s; K2'nin "
        "uçları COM → NO (NC boş) (röle pimlerinin yeri kablajda teyit: röle gövdesindeki şema).")
_G16 = "XL4016 C'yi de mini hat sigortasıyla (5 A) baradan güç panelindeki IN+ / IN− klemensine bağla (G16, 16 AWG)"
_G22 = "PC817 #2 algı teli (G22, 22 AWG): anahtarlı bara ucunda (kaynak ucu) 2 A mini hat sigortası"
_KAFA = "Kafa 12 V (G17), göğüs 12 V (G20) ve ESP32 USB'nin (U06) taban uçlarını bağla."
_TOP = "Toprak (G05, 12 AWG): akü − → yıldız barasının ortadaki %s saplaması."
_G22K = ("G22'nin kutbu + → IN2 +, IN2 − → GND: + damarını (hat sigortasından gelen) arayüz kartındaki PC817 modülünün IN2 + klemensine, "
         "− damarını modülün IN2 − klemensinden yıldız barasına bağla; − damarının yıldız ucu 5 cm 18 AWG siyah ara parçaya lehimli, ara "
         "parça kırmızı pabuçla yıldız barasının %s saplamasına.")
_F1K = ("Kırmızı ucu arayüz kartındaki PC817 #1 giriş klemensinin + ucuna (mantar sonrası düğüm, E3), siyah ucunu güç panelindeki yıldız "
        "barasının (GND, M5 saplama) akü dönüşü saplamasına %s bağla.")
_TES = ("Teslimde bakılacaklar (`planlama/d158/kablo-tablosu-gunluk.md` §16.7, §17.7): alçak profil mini sigortalar (çevre 2 A, şarj "
        "7,5 A) \"Mini/Micro\" yuvaya oturuyor; K1 soketinin kuyruk kesiti okundu, G08 / G09'un 12 AWG teline eklendi; 5,08 mm klemensin "
        "kesit aralığı okundu (A06 / G07 lehimli uçlarına yeniden bakılır); G22'nin yıldız ucu 5 cm 18 AWG ara parça + kırmızı pabuç; akü "
        "dönüşü (G05) yıldızın %s saplamasında; T8 E ve E2 tezgâh kısa devre denemeleri yapıldı "
        "(`planlama/d158/testler/T8-servo-hatlari.md` E: bir servo uzatmasının ucunda ve SV1–SV3'te, servolar sökülü, en çok 2 s, yanmaz "
        "zemin): XL4016 akımı kesiyor ya da düşürüyor, kablo 80 °C'nin altında (kalırsa istisna düşer, tasarıma); K04'ün (kafa ekranı "
        "Power USB) üstündeki kesit yazısı okundu: 24 AWG'den inceyse ya da yazı yoksa 18 AWG + micro B fişle yeniden yapılır.")
BEKLENEN_SILINEN = [
    ("D1 G06 − ucu: saplama numarası, G05'ten sonra", _G06 + "na (mavi pabuç)."),
    ("P10.7b2d-A SEMA G07: cümle ikiye bölündü (eklenen iki cümle)", _G07),
    ("D1 alt kat: bara uçları başka kartta bağlandı göstergesi", _ALT + "."),
    ("D1 alt kat: G12–G15 ve G18 bağlaması bara çıkışları / sigorta kutusu kartına taşındı",
     _BUR + "G12 ve G13'ün + uçlarını anahtarlı baraya, − uçlarını yıldız barasına; G14 ve G15'in + uçlarını hat sigortası yuvasıyla "
     "anahtarlı baraya (§G), − uçlarını yıldız barasına; G18'in + ucunu sigorta kutusunun F4 çıkışına (§G), − ucunu yıldız barasına; " + _SON),
    ("D1 G09 saplama", _F1 % "ya"),
    ("D1 G11 saplama", _G10 % "baraya"),
    ("D1 G16 saplama", _G16 + "."),
    ("D1 G22 + ucu saplama", _G22 + "."),
    ("D1 direk: G17 / G20 taban ucu sigorta kutusu kartında bağlandı", _KAFA),
    # düzeltme turu 2 (F10l-kontrol-2 N2): "N." saplama biçimi → "N numaralı" (değer aynı; F10l-gunluk § 10)
    ("T2 N2 17.1 G05 saplama biçimi", _TOP % "(3.)"),
    ("T2 N2 17.6 G22 saplama biçimi", _G22K % "5."),
    ("T2 N2 F1 kontrol saplama biçimi", _F1K % "(3.)"),
    ("T2 N2 K1 kontrol saplama biçimi", _TES % "3."),
]
BEKLENEN_EKLENEN = [
    ("D1 G06 − ucu: saplama numarası, G05'ten sonra", _G06 + "nın 3 numaralı saplamasına, §G takılan G05'in üstüne (mavi pabuç)."),
    ("P10.7b2d-A SEMA G07", _G07 + "."),
    ("P10.7b2d-A SEMA G07", "Ana anahtar henüz yerinde değil (F1'de etek plakasının altına takılır), karede yok"),
    ("D1 alt kat: bara uçları başka kartta bağlandı göstergesi",
     _ALT + "; G12–G15'in bara uçları §G, G18'in kutu ve yıldız uçları §G bağlandı."),
    ("D1 alt kat: kalan uçlar", _BUR + _SON),
    ("D1 G09 saplama", _F1 % "nın 3 numaralı saplamasına"),
    ("D1 G11 saplama", _G10 % "anahtarlı baranın 3 numaralı saplamasına"),
    ("D1 G16 saplama, G13'ten sonra", _G16 + "; G16'nın + ucu anahtarlı baranın 2 numaralı, − ucu yıldız barasının 2 numaralı saplamasına, "
     "G13'ün üstüne."),
    ("D1 G22 + ucu saplama", _G22 + "; G22'nin yuvasının bara kuyruğu anahtarlı baranın 4 numaralı saplamasına."),
    ("D1 G12–G15 bara uçları (alt kattan taşındı), kalın pabuç altta",
     "G12–G15'in alt kat ucu B3'te bağlandı; burada B3'te etiketli bırakılan bara uçlarını bağla, kalın pabuç altta: önce G12'nin + ucunu "
     "anahtarlı baranın 1 numaralı, G13'ünkünü 2 numaralı saplamasına, − uçlarını yıldız barasının 1 ve 2 numaralı saplamasına; sonra G14 "
     "ve G15'in + uçlarını hat sigortası yuvasıyla anahtarlı baranın 1 numaralı saplamasına, − uçlarını yıldız barasının 1 numaralı "
     "saplamasına (her biri G12'nin üstüne)."),
    ("D1 G17 / G18 / G20 kutu ve yıldız uçları (alt kat ve direk kartından taşındı)",
     "G17, G18, G20 ve A01'in kutu ucunu kendi yuvasının çıkışına bağla (G17 F3, G18 F4, A01 F5, G20 F6); G17, G18 ve G20'nin − ucunu "
     "yıldız barasına: G17 ve G18 4 numaralı, G20 5 numaralı saplamaya (G18'in öbür ucu B3'te XL4016 çevreye bağlandı)."),
    ("D1 direk: G17 / G20 taban ucu sigorta kutusu kartında bağlandı",
     "Kafa 12 V'un (G17) ve göğüs 12 V'un (G20) taban uçları §G bağlandı; ESP32 USB'nin (U06) taban ucunu bağla."),
    ("N3 K2 kol servo uzatmaları: karedeki Kablo yolu 5 / 7'nin K1 kısmı",
     "Karede Kablo yolu 5 ve 7'nin baradan dağıtım kartlarına giden kısmı K1'de bağlandı; burada yalnız uzatmaları tak."),
    # düzeltme turu 2 (F10l-kontrol-2 D1, D2, N2; F10l-gunluk § 10)
    ("T2 D1 17.1 G05'in akü ucu XT60 (kablolar.json G05 uc_a, G01)",
     "G05'in akü ucu XT60'ın robot tarafındaki − ucudur (lehim): akünün kutbuna doğrudan bağlama, akü kutupları bantlı kalır (akü ile "
     "XT60'ın akü tarafı arası G01, §G)."),
    ("T2 D2 17.4 Kablo yolu 3'ün G12 kısmı karede, ucu 17.5'te",
     "Karede Kablo yolu 3'ün baradan sol BTS7960B'ye giden kısmı (G12) da görünür; o uç §G bağlanır."),
    ("T2 N2 17.1 G05 saplama biçimi", _TOP % "(3 numaralı)"),
    ("T2 N2 17.6 G22 saplama biçimi", _G22K % "5 numaralı"),
    ("T2 N2 F1 kontrol saplama biçimi", _F1K % "(3 numaralı)"),
    ("T2 N2 K1 kontrol saplama biçimi", _TES % "3 numaralı"),
]

# P10.7b2e (F10m-gunluk.md): taban 84f1a4a (b2d + P10.9a). Yukarıdaki iki liste b2d'nin kaydıdır (taban 1c4e882, ağaç 78d160d'de
# geçerli); b2e metni değiştiği için 1c4e882 tabanıyla koşu artık b2e farklarını da gösterir. Varsayılan taban b2e'ninki.
BEKLENEN = {"1c4e882": (BEKLENEN_SILINEN, BEKLENEN_EKLENEN)}
_K1M4 = ("Sigorta kutusundan (standart bıçak): F3 5 A kafa hattı (G17, 18 AWG; uç direk dibinde bırakılır), F4 5 A XL4016 çevre (G18, "
         "18 AWG; çevre çıkışı G19, 16 AWG, OUT+ ucunun dibinde 2 A mini hat sigortası), F5 2 A acil stop (A01, 18 AWG; mantar F1'de "
         "takılır, uç bantlı), F6 3 A göğüs ekranı dalı (G20, 18 AWG%s")
_SEMA12 = ("Göğüs ekranı 12 V (G20, G21; 18 AWG): güç paneli (F6 3 A → LM2577 + LM2596; regülatör %s) → direk arka yüzü → direk solu → "
           "ekran; boyundan geçmez")
B2E_SILINEN = [
    ("K52 a K1 madde 4: G20 artık direğe çıkmaz, panelde regülatöre", _K1M4 % "; uç bantlı, K2'de direğe çıkar)."),
    ("K52 a K1: 'karar bekliyor (K52)' cümlesi", "Göğüs regülatörünün panel yeri karar bekliyor (K52): G20'nin uç yeri ve boyu bu karara bağlı."),
    ("K52 a K1 'Direğe' alt adımı: G20 taban ucu", "Kafa 12 V'un (G17) ve göğüs 12 V'un (G20) taban uçları §G bağlandı; ESP32 USB'nin (U06) taban ucunu bağla."),
    ("K52 a K2 madde 7: 'karar bekliyor (K52)'", "Regülatörün panel yeri karar bekliyor (K52): G20'nin uç yeri ve boyu buna bağlı."),
    ("K52 a K2 madde 7: ayar cümlesi yeni cümleye katıldı", "Regülatör ekrana bağlanmadan 12 V'a ayarlanır (kontrol)."),
    ("K52 a K2 not", "LM2577 + LM2596 kartı modelde yok; panel yeri karar bekliyor (K52)"),
    ("K52 a F3 not", "Regülatör kartı modelde yok; panel yeri karar bekliyor (K52)"),
    ("K52 a şema 12 V", _SEMA12 % "yeri karar bekliyor, K52"),
]
B2E_EKLENEN = [
    ("K52 a K1 madde 4: G20 panelde regülatör girişine",
     _K1M4 % "): kutudan, B5a'da güç paneline takılan göğüs ekranı regülatörünün girişine (K52 a); G20'nin iki ucu da panelde, göğüs "
     "regülatörünün direğe çıkan çıkışı K2'de."),
    ("K52 a K1 madde 4: G20'nin regülatör ucu (kutup kayıttan {kutup.G20})",
     "G20'nin regülatör ucunu regülatörün giriş klemensine bağla (F6 çıkışı → IN+, IN− → GND; kart üstü IN+ / IN− yazısına göre)."),
    ("K52 a K1 'Direğe' alt adımı: G20 panel içinde",
     "Kafa 12 V'un (G17) taban ucu ve panel içinde kalan göğüs ekranı dalı (G20) §G bağlandı; ESP32 USB'nin (U06) taban ucunu bağla."),
    ("K52 a K2 madde 7", "Regülatör B5a'da güç paneline takıldı (K52 a): panele takılmadan önce, ekrana bağlanmadan 12 V'a ayarlandı "
     "(kontrol); girişi (G20) K1'de bağlandı."),
    ("K52 a K2 not", "LM2577 + LM2596 kartı güç panelinde (B5a, K52 a); kart ve panel üstündeki yeri modelde yok"),
    ("K52 a F3 not (çıkış klemensine erişim ölçülmedi)", "Regülatör kartı güç panelinde (B5a, K52 a); kart ve panel üstündeki yeri modelde "
     "yok: bu adımda çıkış klemenslerine erişim ölçülmedi, doğrulanmadı"),
    ("K52 a şema 12 V", _SEMA12 % "güç panelinde, B5a, K52 a; modelde yok"),
    ("K52 a B5a paragraf (T7 B)", "Göğüs ekranı regülatörü (LM2577 + LM2596; K52 a): ekrana ve panele bağlamadan, tezgâhta çıkışını "
     "multimetreyle 12 V'a ayarla ve trimpotun konumunu boya noktasıyla işaretle (`planlama/d158/testler/T7-gogus-ekrani-12v.md` B)."),
    ("K52 a B5a paragraf", "Sonra kartı güç paneline tak; giriş (IN+ / IN−) ve çıkış (OUT+ / OUT−) klemensleri erişilebilir kalsın."),
    ("K52 a B5a paragraf: yeri kaynakta yok", "Kart, ölçüsü ve panel üstündeki yeri modelde yok; yeri ve bağlantı elemanı kaynakta yok, "
     "doğrulanmadı."),
    ("K52 a B5a paragraf", "Girişi (G20) K1'de, çıkışı (G21) K2'de bağlanır."),
    ("K52 a B5a kontrol", "Göğüs ekranı regülatörü (LM2577 + LM2596) panelde; panele takılmadan önce tezgâhta, ekran bağlı değilken çıkışı "
     "12 V'a ayarlandı, trimpotu boya noktasıyla işaretli (T7 B)"),
    # P10.7b2e kısım 2: K64 kapandı (a); kısım 1'in "karar bekliyor (K64)" cümlesi B2E_K2_EKLENEN'deki K64 a cümlesiyle değişti
    ("K64 B5a not", "K1'in \"Toprak ve iki bara\" alt adımı iki barayı panelde varsayar"),
    ("K52 a B5a not", "Göğüs ekranı regülatörü (K52 a) modelde yok: karede görünmez, model sonraki tam taramalı CAD paketinde"),
]
# P10.7b2e kısım 2 (F10m-gunluk.md § 8, § 11): kare düzeltmelerinin kart metinleri (yer tarifi, eski çizim uyarısı, göndermeler),
# K64 a, K65 sağ / sol kurulum testi, F1 ölçü noktaları. Düzeltme turu 1'den beri adım 0 (HAZIRLIK) da kaynak_metinler'de.
B2E_K2_SILINEN = [
    ('kısım 2 F1 kontrol: cümleye nokta (ardına yeni cümle)',
     'Bu aşamalar, sigorta sırası, ölçü noktası, klemensin + ucu, multimetre aralığı ve "yerden kesik" düzeni bu adım için kaynakta yok, doğrulanmadı'),
]
B2E_K2_EKLENEN = [
    ('kısım 2 17.7: öbür kabloların karesi',
     "A01'in çizgisi §G'in, G17'ninki §G'ün, göğüs ekranı hattının şeması §G'nin karesinde."),
    ('kısım 2 B6a: BNO055 yön oku karede yok',
     "BNO055'in yön oku karede çizili değil: kartın üstündeki X okunu robotun önüne (yüz tarafı) çevir (kontrol)."),
    ('K64 a B5a not: tutucu CAD paketinde',
     'Bara tutucusu (yıldız barasının ve anahtarlı baranın M5 saplamalarını taşıyan basılmış yalıtkan parça; `planlama/adim3/kablolar.json` bara pabuç kaydı) henüz tasarlanmadı: modelde ve baskı listesinde yok, sonraki tam taramalı CAD paketinde tasarlanıp basılacak, satın alınmayacak (K64 a).'),
    ('kısım 2 17.11: karede vurgu yok, nedeni',
     "Bu alt adımın kabloları karede vurgulu değil: P03'ün çizimi yok (bağlantı tablosu aşağıda), U06'nın şeması §G'ün karesinde."),
    ('kısım 2 F1 kontrol: cümleye nokta (ardına yeni cümle)',
     'Bu aşamalar, sigorta sırası, ölçü noktası, klemensin + ucu, multimetre aralığı ve "yerden kesik" düzeni bu adım için kaynakta yok, doğrulanmadı.'),
    ('K65 K1 kontrol: sağ / sol kurulum testi',
     "Devreye alma adımları ve `sur`'un yalnız w ile davranışı kartta denenmedi (`kod/esp32/OKU_BENI.md`)"),
    ('kısım 2 17.10: U06 göndermesi',
     "ESP32'nin direğe çıkan kablosu ESP32 USB'dir (U06, §G)."),
    ("kısım 2 17.5: G14 / G15 çizgisi 32.1'de",
     "G14 ve G15'in çizgisi Kablo yolu 5 ve 7'nin parçasıdır: §G'in karesinde görünür."),
    ('kısım 2 17.1: baralar modelde yok (K64 a)',
     'Karede görünmez: iki bara ve tutucuları modelde yok (tutucu CAD paketinde gelecek, K64 a); baralar güç panelinde (arka kat, B5a).'),
    ('kısım 2 B6a: kartların yeri',
     'Karede kartların adı yazmaz; yerleri (robota önden bakınca): arayüz kartı solda, ESP32 taşıyıcı sağda, PCA9685 onun önünde sağda, BNO055 ortada; dağıtım kartı A ön kenarda sağda, B solda.'),
    ("kısım 2 17.10: Kablo yolu 12'nin eski kısmı",
     "Karede vurgulu Kablo yolu 12 (B01): direk boyunca yukarı çıkan kısmı eski çizimdir (ESP32'den kafaya giden eski USB yolu), uygulanmaz; B01 tabanda kalır."),
    ("kısım 2 17.7: Kablo yolu 9'un eski kısmı",
     "Karede vurgulu çizgi Kablo yolu 9'dur (G18): XL4016 çevreden sonraki kısmı eski çizimdir (doğrudan ESP32'ye), uygulanmaz; çevre çıkışı G19 §G arayüz kartına bağlanır."),
    ('kısım 2 17.10: yer',
     'Karede yer: ESP32 taşıyıcı ve PCA9685 elektronik katında önden bakınca sağda, arayüz kartı solda; sonarlar ön yüzde.'),
    ('kısım 2 17.6: yer',
     'Karede yer: PC817 modülü arayüz kartının üstünde, arayüz kartı elektronik katında önden bakınca solda; anahtarlı bara karede görünmez (modelde yok, güç panelinde).'),
    ('kısım 2 17.11: yer',
     'Karede yer: PCA9685 ve ESP32 taşıyıcı elektronik katında önden bakınca sağda; dağıtım kartı C güç panelinde (B5a, modelde yok).'),
    ('kısım 2 17.9: yer',
     'Karede yer: XL4016 A alt katta ortada, B solda, çevre sağda; dağıtım kartı A elektronik katının ön kenarında sağda, B solda.'),
    ('kısım 2 17.2: yer',
     "Karede yer: ana sigorta yuvası güç panelinde sağda, sigorta kutusu panelin arka ortasında; ana anahtar karede yok (F1'de sol arka köşeye takılır)."),
    ('kısım 2 17.3: yer',
     "Karede yer: arayüz kartı elektronik katında (ön kat), önden bakınca solda; G07'nin öbür ucu F1'de sol arka köşedeki ana anahtara gider."),
    ('kısım 2 17.5: yer',
     'Karede yer: iki BTS7960B alt katta, sol olan önden bakınca solda, sağ olan sağda; XL4016 A ortada, B solda; XL4016 C güç panelinde (B5a).'),
    ('kısım 2 17.8: yer',
     "Karede yer: röle K1 güç panelinde önden bakınca solda, ön şarj kartı panelin ön kenarında aynı yanda, arayüz kartı elektronik katında solda; acil stop düğüm kartı karede görünmez (modelde yok); mantar F1'de sağ arka köşeye takılır."),
    ('kısım 2 17.4: yer',
     'Karede yer: röle K1 güç panelinde önden bakınca solda, ön şarj kartı panelin ön kenarında aynı yanda.'),
    ('kısım 2 17.1: SV3 çizgisi',
     "Karedeki soluk sarı çizgi B5a'da bağlanan SV3'ün şemasıdır, bu alt adımın kablosu değil."),
    ('K64 a B5a not',
     'O zamana dek rehber panelde yerini ve bağlantı elemanını yazmaz.'),
    ("kısım 2 17.9: SV1 / SV2 çizgisi 32.1'de",
     "SV1 ve SV2'nin çizgisi Kablo yolu 5 ve 7'nin parçasıdır: §G'in karesinde görünür."),
    # düzeltme turu 1 (F10m-kontrol D2): test yön testinden sonra, sayaç ölçütü "hangi sayaç değişiyor"
    ('K65 K1 kontrol: sağ / sol kurulum testi (D2: yön testinden sonra)',
     'Sağ / sol kurulum testi (bağladığın taraf ile yazılımın tarafı aynı mı; bu adımda değil, F5 "İlk enerji, aşama 2"de devreye aldıktan ve motor / enkoder yön testinden (`*_MOTOR_TERS`, `*_ENKODER_TERS`; `kod/esp32/OKU_BENI.md`) sonra yapılır): tekerler yerden kesik (şasi takozda).'),
    ('K65 K1 kontrol: sağ / sol kurulum testi (D2: hangi sayaç değişiyor)',
     'Sonra `odo_sifirla` komutunu gönder ve arka tekerleri tek tek elle çevir: önden bakınca soldaki arka teker `odo` satırında yalnız `sag` sayacını değiştirmeli (`sol` sabit kalır), sağdaki yalnız `sol` sayacını; sayacın artıp azalması bu testin konusu değil, yön testinin konusudur.'),
    ('düzeltme turu 1 (D2) F5 aşama 2: sağ / sol testine gönderme',
     'Yön testinden sonra K1 kontrolündeki sağ / sol kurulum testini yap.'),
    # düzeltme turu 1 (F10m-kontrol D1): kaynak_metinler adım 0'ı (HAZIRLIK) da okuyor; değişmeyen adım 0 cümleleri iki yanda eşit,
    # kısım 2'nin K65 tanım cümleleri ekleme olarak görünür
    ('K65 adım 0: sağ / sol tanımı',
     'Sağ / sol: Bu rehberde ve kablo tablosunda sağ / sol, robota önden bakan kişinin sağı / soludur; robotun kendi sağı / solu değildir.'),
    ('K65 adım 0: örnek',
     "Örnek: acil stop mantarı, robota önden bakınca sağ arka köşededir; üstüne 'SOL' yazılan aynalı kol önden bakınca solda takılır (robotun kendi sağ kolu)."),
    ('K65 adım 0: parça adları ve yazılım',
     "Parça ve kart adlarındaki sağ / sol da bu tanıma göredir; yazılımdaki adlar robotun kendi sağını / solunu kullanır, karşılıkları `planlama/d158/sag-sol-karari.md`'de."),
    ('düzeltme turu 1 (N13) adım 0: arkadan çalışırken',
     'Robotun arkasından çalışırken önden bakanın sağı senin solunda kalır.'),
    ('K65 K1 kontrol: sağ / sol kurulum testi',
     "Ters çıkarsa kabloyu değiştirme: robotu sürme, `planlama/d158/sag-sol-karari.md`'deki yazılım düzeltmesi bekleniyor (Efe)."),
    ('kısım 2 F1 kontrol (E): ölçü noktaları karede görünmez',
     'Ölçü noktaları karede görünmez: PC817 #1 klemensi ve akü ölçüm bölücüsü arayüz kartının üstünde (elektronik katı, robota önden bakınca solda; kart üstü klemensler modelde çizili değil), yıldız barası güç panelinde (arka kat; bara modelde yok)'),
    ('K65 K1 kontrol: sağ / sol kurulum testi',
     'Önce `sur` komutunu v = 0, w = 0,2 ile gönder (w sola +; motorlar yarım saniyede kendiliğinden durur, gerekirse yinele): robot kendi soluna dönmek ister, yani robota önden bakınca soldaki tekerler ileri, sağdakiler geri döner.'),
]
BEKLENEN["84f1a4a"] = (B2E_SILINEN + B2E_K2_SILINEN, B2E_EKLENEN + B2E_K2_EKLENEN)

# P10.7b2f (F10n-gunluk.md § 2, § 3): taban b5fc255 (b2e). Kablo yolu 12'nin eski dikey kısmı rehber verisinde kırpılıyor
# (rehber_kablo.CAD_KIRP), "eski çizim" cümleleri kalktı; uç etiketi cümlesi (B6a); 31.4 yedek ses kartı; sağ / sol tanımı kutuda
# (adım 0, "**…:**" öneki); kurulum testi K1 kontrolünden F5 kontrolüne taşındı; K2'nin "Taban şeması 12" maddesi (N4) kalktı.
_KUR = ("Sağ / sol kurulum testi (bağladığın taraf ile yazılımın tarafı aynı mı; %sdevreye aldıktan ve motor / enkoder yön testinden "
        "(`*_MOTOR_TERS`, `*_ENKODER_TERS`; `kod/esp32/OKU_BENI.md`) sonra yapılır): tekerler yerden kesik (şasi takozda).")
_TANIM = ("Bu rehberde ve kablo tablosunda sağ / sol, robota önden bakan kişinin sağı / soludur; robotun kendi sağı / solu değildir.")
_B6A = ("; yerleri (robota önden bakınca): arayüz kartı solda, ESP32 taşıyıcı sağda, PCA9685 onun önünde sağda, BNO055 ortada; "
        "dağıtım kartı A ön kenarda sağda, B solda.")
B2F_SILINEN = [
    ("madde 1 17.10: eski kısım artık çizilmiyor (CAD_KIRP)",
     "Karede vurgulu Kablo yolu 12 (B01): direk boyunca yukarı çıkan kısmı eski çizimdir (ESP32'den kafaya giden eski USB yolu), "
     "uygulanmaz; B01 tabanda kalır."),
    ("madde 1 KABLO_AD[12]: şema açıklaması", "Şemanın direkten kafaya çıkan kısmı eski (05.11 öncesi ESP32 → kafa USB); ESP32 USB artık "
     "hub'dan: \"ESP32 USB\" şeması"),
    ("N4 K2 kablo listesi: 'Taban şeması 12' maddesi", "Taban şeması 12'nin direkten kafaya çıkan kısmı eski (05.11 öncesi ESP32 → kafa "
     "USB); geçerli yol \"ESP32 USB\" şemasında"),
    ("madde 2 B6a: adlar artık uç etiketinde", "Karede kartların adı yazmaz" + _B6A),
    ("madde 3 adım 0: tanım kutuda", "Sağ / sol: " + _TANIM),
    ("madde 3 kurulum testi K1 → F5", _KUR % "bu adımda değil, F5 \"İlk enerji, aşama 2\"de "),
    ("madde 3 F5 aşama 2: test aynı listede", "Yön testinden sonra K1 kontrolündeki sağ / sol kurulum testini yap."),
]
B2F_EKLENEN = [
    ("madde 1 17.10: yalnız B01'in taban kısmı çizili", "Karede vurgulu Kablo yolu 12 (B01) tabanda kalır: sol BTS7960B'den ESP32 "
     "taşıyıcısına."),
    ("madde 1 KABLO_AD[12]: şema açıklaması", "CAD yolunun 05.11 öncesi ESP32 → kafa USB kısmı rehberde çizilmez; ESP32 USB artık hub'dan: "
     "\"ESP32 USB\" şeması"),
    ("madde 2 B6a: uç etiketleri", "Karede bağlantı kablolarının uç kartları numaralı (etkileşimli sayfada adıyla, basılı sayfada adları "
     "karenin altında)" + _B6A),
    ("madde 3 31.4: yedek USB ses kartı", "Karede PAM8403'ün yanındaki ikinci kart yedek USB ses kartıdır: takılmaz (önceki alt adım)."),
    ("madde 3 adım 0: tanım kutuda (yazdir.html .is.tanim)", "**Sağ / sol tanımı:** " + _TANIM),
    ("madde 3 kurulum testi K1 → F5: K1'de gösterge", "Sağ / sol kurulum testi bu adımda yapılmaz: F5 \"İlk enerji, aşama 2\" kontrol "
     "listesinde (devreye alma ve motor / enkoder yön testinden sonra)"),
    ("madde 3 kurulum testi K1 → F5: F5 kontrolünde", _KUR % "K1'de bağlanan kablolar; "),
    ("madde 3 F5 aşama 2: test aynı listede", "Yön testinden sonra kontrol listesindeki sağ / sol kurulum testini yap."),
]
# P10.7b2f kısım 2 (F10n-gunluk.md § 8): kayıt düzeltmeleri. K66 (VIN'e seri 1N5819, B6a); Efe'nin iki cevabı geldi (pano #7 mesaj
# #28: DTR / RTS reset, ReSpeaker 16 kHz) → K2 alt adım 5 / kontrol ve E4 not_; K2 alt adım 4'ün "geri beslenirse aşılabilir"
# cümlesi K66 ile geçersiz.
B2F_SILINEN += [
    ("kısım 2 K66: K2 alt adım 4 geri besleme notu geçersiz",
     "1N5819'un sınırı 1 A: çevre yükleri USB'den geri beslenirse aşılabilir (teslimde bakılacaklar; Efe'ye soru)."),
    ("kısım 2 pano #28: K2 alt adım 5 bekleme kalktı",
     "Demeti kelepçe / kılıfla kapatmadan önce Efe'nin iki cevabı beklenir (ESP32 bilinçli reseti DTR / RTS ile; ReSpeaker 16 kHz)."),
    ("kısım 2 pano #28: K2 kontrol koşulu kalktı",
     "Demet kapatılmadan: Efe'nin iki cevabı geldi (DTR / RTS reset, ReSpeaker 16 kHz); \"tel gerekir\" derse bükümlü çift eklenir"),
    ("kısım 2 pano #28: E4 not_ soru cevaplandı",
     "Efe'ye soru (demet kapanmadan): ReSpeaker çalma akışı en çok 16 kHz; konuşma sesi için kabul mü, hangi firmware"),
]
B2F_EKLENEN += [
    ("kısım 2 K66: B6a madde 2 diyot yönü", "VIN'e seri 1N5819: anot çevre 5 V tarafında, katot ESP32 VIN tarafında (K66; çevre hat "
     "sigortası atınca çevre yükleri USB'den beslenmesin diye)."),
    ("kısım 2 K66: B6a madde 2 yer açık (kayıtta yok)", "Diyodun takılacağı yer (arayüz kartı üstü ya da X01'in 5 V damarı) kayıtta "
     "yok, kablajda belirlenir."),
    ("kısım 2 K66: B6a kontrol diyot yönü", "VIN'e seri 1N5819'un yönü: multimetrenin diyot kademesinde çevre 5 V → ESP32 VIN yönünde "
     "iletir, ters yönde iletmez (bantlı uç, katot, VIN tarafında)"),
    ("kısım 2 K66: K2 alt adım 4 geri beslemeyi VIN diyodu keser", "1N5819'un sınırı 1 A: çevre yüklerinin USB'den geri beslenmesini "
     "VIN'e seri ikinci 1N5819 keser (B6a, K66)."),
    ("kısım 2 pano #28: K2 alt adım 5 demet kapatılabilir", "Efe'nin iki cevabı geldi (ESP32 bilinçli reseti mevcut DTR / RTS devresiyle; "
     "ReSpeaker 16 kHz kabul): boyundan yeni tel gerekmez, demeti kelepçe / kılıfla kapatabilirsin."),
    ("kısım 2 pano #28: K2 kontrol", "Demet kapatılmadan: Efe'nin iki cevabı geldi (DTR / RTS reset, ReSpeaker 16 kHz); yeni tel yok, "
     "demete bükümlü çift eklenmedi"),
    ("kısım 2 pano #28: E4 not_", "ReSpeaker çalma akışı en çok 16 kHz: Efe konuşma sesi için kabul etti, 1 kanallı firmware (pano "
     "cevabı, 14.11)"),
]
BEKLENEN["b5fc255"] = (B2F_SILINEN, B2F_EKLENEN)
# P10.7b2g (F10o-gunluk.md § 4): taban 9b019d2 (b2f). Boyun tüneli deneme parçası üretildi (tasarim/freecad/kafa/boyun_tunel_deneme.py);
# K2 alt adım 5 (boyun demeti) parçanın adına / dosyasına ve fiş sırasına (kablolar.json U03 / H02 / S10 gecis_sirasi) bağlandı.
# Silinen cümle yok: eski KT4 cümlesi aynen kaldı, üç cümle eklendi (düzeltme turu 1: D1 birikme, N2 pan servo kablosu).
B2G_EKLENEN = [
    ("b2g: K2 alt adım 5 parça adı ve dosyası", "Parça: Boyun tüneli deneme parçası (`tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl`; "
     "baskı listesinde tolerans kuponlarının yanında, beyaz PETG, ≈ 68 g, destek gerekmez)."),
    ("b2g düz.2 Y1: pan servo kablosu yerinde", "Önce bir servo kablosunu alt çıkıştan kanala sok, ucunu kanal dibindeki servo kablo "
     "yarığına it ve yerinde bırak (pan servosunun kendi kablosu robotta bu kanaldan iner)."),
    ("b2g düz.1 D1: fiş sırası ve birikme", "Fişleri parçanın arka yüzündeki alt çıkıştan sok, kanaldan yukarı, kablo odasından mil penceresine, "
     "milin içinde yukarı geçirip mil ucundan çıkar; geçen kabloyu parçada bırak, sonraki fişi onun yanından geçir: önce tünel boşken hub "
     "uzatmasının (U03) USB-A erkek fişi, sonra U03'ün kablosu tünelde yerindeyken HDMI'nin (H02) micro HDMI ucu, sonra iki kablonun yanından "
     "tilt servo kablosunun (S10) 3 pinli fişi; hoparlör (AU3) ve 12 V (G17) fişsiz geçer, deneme gerekmez."),
]
BEKLENEN["9b019d2"] = ([], B2G_EKLENEN)
# P10.7b2h (F10q-gunluk.md § 2): taban 376fe90 (b2g). 17.11 kararlarının rehber metni: K50 b (XT60E-F dişi panel; K1 / F1 / F5),
# K51 a (E3a ikinci TVS), K55 a (dört bant esnetilerek, kupon), K40 a (G3 S2 horn + sentil), K60 A (K1 Ö4 köprüsü kalıcı + demo şartı).
# Liste uygulanan metinden betikle üretildi, etiketler elle denetlendi. Düzeltme turu 1 (F10q-kontrol): G3 sentil F5'e, etek ön perçin
# somunu cümlesi, F1 'alımı açık'; düzeltme turu 2: F5 sentil istisnası + erişim kuralı göndermesi; liste yeniden üretildi.
B2H_SILINEN = [
    ('b2h K50 b', "Delik açıldıysa konnektörü (XT60E-M, erkek panel girişi) tak, K1'de bırakılan şarj ucunu (G06) akü ayrıkken bağla; açılmadıysa uç bantlı kalır."),
    ('b2h K51 a', "Her iki 5 V çıkışına bir P6KE6V8A TVS: SY8205 → QLED hattındaki modelde var, D24V50F5 → Pi hattındaki modelde ve BOM'da yok (ikinci TVS'i ayrıca al)."),
    ('b2h K40 a', 'Kolların erişim alanında ve düşme hattında, kafanın ve tekerlerin erişim alanında kimse yok, bir kişi yalnız mantarda (kural 1 ve 7).'),
    ('b2h K60 A', 'Mantar ile düğüm arasında elde taşınan acil stop için ayrılan iki uçlu yer (Ö4; 2 pin 5,08 mm klemens) karar verilene kadar zincirin kendi teliyle (A01, A02) aynı kesitte (18 AWG) kısa bir tel köprüyle kapalı durur; köprü yoksa röle çekmez.'),
    ('b2h K50 b', 'Pimlere metal değdirme; kapak takılı kalır (K50, teslimde bakılacaklar)'),
    ('b2h K40 a', 'S2 hornu + merkez vidası; kol çatalı → horn (4 × M3×8): 625ZZ tezgâhta çatalın arka kolunun Ø16 yuvasına önceden preslenir, iki bileziğiyle çatalla birlikte gelir.'),
    ('b2h K40 a', 'S2 hornu, merkez vidası.'),
    ('b2h K50 b', "Uyarı: sigorta takıldıktan sonra etekteki şarj girişinin (XT60E-M panel erkek, `planlama/maliyet.json`) pimleri, akü XT60'tan ayrılmadıkça gerilimlidir: ana anahtar da mantar da bu kolu kesmez."),
    ('b2h K50 b', 'XT60 şarj girişi (panel konnektör): önerilen yer etek üst plakasının arkası, delik modelde yok (doğrulanmadı); delik açıldıysa konnektörü (XT60E-M) tak, şarj ucunu (G06) akü ayrıkken bağla, açılmadıysa uç bantlı kalır.'),
    ('b2h K50 b', 'XT60E-M pinleri sigorta takılınca her zaman akü geriliminde (ana anahtar da mantar da kesmez): kapağı takılı kalır.'),
    ('b2h K60 A', 'Ö4 karar bekliyor (K60).'),
    ('b2h K50 b', "Şarj kolu (G06, 16 AWG): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına gidecek (G03 ile aynı saplama, mavi M5 halka pabuç, ana anahtarın saplama ölçüsü kablajda teyit; F1'de takılır); 7,5 A mini hat sigortasının kapaklı yuvası ana anahtar girişindeki ucun dibinde (kaynak ucu), kuyruğuna lehim + makaron; öbür uç etekteki XT60E-M şarj girişine (F1); − ucu yıldız barasının 3 numaralı saplamasına, §G takılan G05'in üstüne (mavi pabuç)."),
    ('b2h K50 b', 'Şarj kolunun 7,5 A mini sigortası takılmaz (aşama 1 listesi); sonra XT60E-M pinleri her zaman gerilimli olacağı için kapağı kapalı kalır.'),
]
B2H_EKLENEN = [
    ('b2h K40 a', '0,3 geçmiyorsa ana anahtarı kapat, aküyü ayır, sonra diş yüzünü zımparala (yalnız enerjisizken) ve sınamayı yinele.'),
    ('b2h K55 a', 'Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('b2h K55 a', 'Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('b2h K55 a', 'Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('b2h K55 a', 'Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('b2h K55 a', 'Bant düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('b2h K55 a', 'Bant düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('b2h K40 a', "Bantlar takılıyken sentil dişle kol arasına düz giremiyorsa sınamayı zorlama; ölçülemedi diye kaydet ve omuz bandını sökmeden önce proje sahibine sor (aralığın kabuk altında erişilebilirliği CAD'de doğrulanmadı)."),
    ('b2h K55 a', 'Bu bantta engel dil değil, z +105 braketinin perçin somunu (ölçüm): kuponda bu bant ayrıca, somun takılıyken denenir.'),
    ('b2h K55 a', 'Bu bantta engel dil değil, z +105 braketinin perçin somunu (ölçüm): kuponda bu bant ayrıca, somun takılıyken denenir.'),
    ('b2h K40 a', 'Bu sınama aşamadaki "kolların erişim alanında kimse yok" kuralının tek istisnasıdır ve yalnız şöyle yapılır: komutu mantardaki kişi verir; S2\'ye 5 komutunu ver, kol durduktan sonra üç saniye bekle; mantardaki kişi bundan sonra kumandaya, telefona ve klavyeye dokunmaz, eli mantarın üstünde kalır.'),
    ('b2h K50 b', "Delik açıldıysa konnektörü (XT60E-F, dişi panel girişi; K50 b: akü tarafı gömük soket, şarj kablosunun ucu erkek XT60; alımı açık, F5 notu) tak, K1'de bırakılan şarj ucunu (G06) akü ayrıkken bağla; açılmadıysa uç bantlı kalır."),
    ('b2h K60 A', 'Elde taşınan acil stop yok (K60 A): köprü kalıcıdır, ileride kumandalı acil stop sökmeden bu yere eklenebilir; demoda mantarın yanında bir kişi durur.'),
    ('b2h K51 a', "Her iki 5 V çıkışına bir P6KE6V8A TVS (satın alma listesinde 2 adet, `planlama/maliyet.json`): SY8205 → QLED hattındaki modelde var, D24V50F5 → Pi hattındaki bugün modelde ve BOM'da yok, sonraki CAD paketinde eklenecek (K51 a)."),
    ('b2h K40 a', 'Kişi elini çekip kolun erişim alanından çıkmadan hiçbir komut verilmez; ikinci kol için aynı sıra.'),
    ('b2h K40 a', 'Kol beklenmedik biçimde kıpırdarsa mantara hemen basılır.'),
    ('b2h K40 a', 'Kolların erişim alanında ve düşme hattında, kafanın ve tekerlerin erişim alanında kimse yok, bir kişi yalnız mantarda (kural 1 ve 7); bu kuralın tek istisnası aşağıdaki S2 sentil sınamasıdır, şartları o cümlede.'),
    ('b2h K50 b', 'Konnektörün alımı açık: siparişte XT60E-M varsa XT60E-F ile değiştirilir (K50, teslimde bakılacaklar)'),
    ('b2h K60 A', 'Mantar ile düğüm arasında elde taşınan acil stop için ayrılan iki uçlu yer (Ö4; 2 pin 5,08 mm klemens) zincirin kendi teliyle (A01, A02) aynı kesitte (18 AWG) kısa bir tel köprüyle kapalı durur; köprü yoksa röle çekmez.'),
    ('b2h K40 a', 'S2 5 komutunda dişle kol arasında 0,3 mm sentil geçiyor, 0,4 mm geçmiyor; iki kolda da (K40 a)'),
    ('b2h K40 a', "S2 hornu + merkez vidası (horn kol dişe dayalıyken, S2 = 4,3°; sentil sınaması F5 aşama 2'de, K40 a); kol çatalı → horn (4 × M3×8): 625ZZ tezgâhta çatalın arka kolunun Ø16 yuvasına önceden preslenir, iki bileziğiyle çatalla birlikte gelir."),
    ('b2h K40 a', 'S2 hornu, merkez vidası: hornu, kol takılınca dişe dayanacağı konumda (S2 = 4,3°) tak (K40 a).'),
    ('b2h K40 a', "S2 sentil sınaması (K40 a; horn G3'te dişe göre takıldı)."),
    ('b2h K40 a', 'S2\'nin sentil sınaması (K40 a) burada yapılmaz: S2 ilk kez F5 "İlk enerji, aşama 2"de sürülür, sınama orada.'),
    ('b2h K50 b', 'Soketlere metal sokma; kapak takılı kalır.'),
    ('b2h K50 b', "Uyarı: sigorta takıldıktan sonra etekteki şarj girişinin (XT60E-F panel dişi, K50 b) soketleri, akü XT60'tan ayrılmadıkça gerilimlidir: ana anahtar da mantar da bu kolu kesmez."),
    ('b2h K50 b', 'XT60 şarj girişi (panel konnektör): önerilen yer etek üst plakasının arkası, delik modelde yok (doğrulanmadı); delik açıldıysa konnektörü (XT60E-F, dişi; K50 b) tak, şarj ucunu (G06) akü ayrıkken bağla, açılmadıysa uç bantlı kalır.'),
    ('b2h K50 b', 'XT60E-F soketleri sigorta takılınca her zaman akü geriliminde (ana anahtar da mantar da kesmez): kapağı takılı kalır.'),
    ('b2h K55 a', 'Çerçeve düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('b2h K40 a', 'Öbür kişi yalnız sentilin ucundan tutarak dişle kol arasına 0,3 mm sentili sokar, parmağını dişle kol arasına sokmaz (sıkışma hattı): 0,3 mm geçmeli, 0,4 mm geçmemeli.'),
    ('b2h K50 b', "Şarj kolu (G06, 16 AWG): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına gidecek (G03 ile aynı saplama, mavi M5 halka pabuç, ana anahtarın saplama ölçüsü kablajda teyit; F1'de takılır); 7,5 A mini hat sigortasının kapaklı yuvası ana anahtar girişindeki ucun dibinde (kaynak ucu), kuyruğuna lehim + makaron; öbür uç etekteki XT60E-F (dişi) şarj girişine (F1); − ucu yıldız barasının 3 numaralı saplamasına, §G takılan G05'in üstüne (mavi pabuç)."),
    ('b2h K50 b', 'Şarj kolunun 7,5 A mini sigortası takılmaz (aşama 1 listesi); sonra XT60E-F soketleri her zaman gerilimli olacağı için kapağı kapalı kalır.'),
]
BEKLENEN["376fe90"] = (B2H_SILINEN, B2H_EKLENEN)
# P10.7b2i (F10r-gunluk.md § 1–2): taban 8bca2f5 (b2h). Yol 9'un eski XL4016 → ESP32 kısmı rehberde kırpıldı (rehber_kablo.CAD_KIRP 9):
# 17.7 ve KABLO_AD[9]'un "eski çizim" cümleleri; U06 şeması yeniden çizildi: K2 "yanlış yerde" maddesi kalktı, taban ucu talimatı K1
# alt adım 17.11'de, K2 önerilen boyu 1.360 → 1.560 (lale158-kontrol.json). Liste uygulanan metinden, etiketler elle.
B2I_SILINEN = [
    ('b2i yol 9 kırpma (KABLO_AD 9)', "Şemanın XL4016 sonrası kısmı eski (doğrudan ESP32'ye); tabloda G19 (16 AWG) 2 A mini hat sigortasıyla arayüz kartına gider, bu şemada çizili değil: kendi gösterim şeması K1'de"),
    ('b2i yol 9 kırpma (17.7)', "Karede vurgulu çizgi Kablo yolu 9'dur (G18): XL4016 çevreden sonraki kısmı eski çizimdir (doğrudan ESP32'ye), uygulanmaz; çevre çıkışı G19 §G arayüz kartına bağlanır."),
    ('b2i U06 taban ucu (17.11)', "Kafa 12 V'un (G17) taban ucu ve panel içinde kalan göğüs ekranı dalı (G20) §G bağlandı; ESP32 USB'nin (U06) taban ucunu bağla."),
    ('b2i U06 "yanlış yerde" kalktı (K2 kablo)', "\"ESP32 USB\" şemasının (U06) taban ucu yanlış yerde, güç panelinin üstünde çizili (şema yeniden çizilecek): kablonun taban ucu elektronik katındaki ESP32 taşıyıcısında ESP32'nin USB girişine takılır"),
    ('b2i U06 önerilen boy (K2 kablo)', "Önerilen boylar (yol × 1,25, hub'a gidenlere + 150 mm; tahmin): HDMI 950, hub uzatması 920, ESP32 USB 1.360, hoparlör 1.030, göğüs 12 V 1.720 mm (`planlama/adim3/elektrik.md`)."),
]
B2I_EKLENEN = [
    ('b2i yol 9 kırpma (KABLO_AD 9)', "CAD yolunun XL4016 sonrası eski kısmı (doğrudan ESP32'ye) rehberde çizilmez; çevre çıkışı G19 (16 AWG) 2 A mini hat sigortasıyla arayüz kartına gider, bu şemada çizili değil: kendi gösterim şeması K1'de"),
    ('b2i yol 9 kırpma (17.7)', "Karede vurgulu çizgi Kablo yolu 9'dur (G18, F4 → XL4016 çevre); çevre çıkışı G19 §G arayüz kartına bağlanır."),
    ('b2i U06 taban ucu (17.11)', "Kafa 12 V'un (G17) taban ucu ve panel içinde kalan göğüs ekranı dalı (G20) §G bağlandı; ESP32 USB'nin (U06) taban ucunu bağla: micro USB fişini ESP32'nin önden bakınca sağ ucundaki portuna tak; kabloyu elektronik katının üstünden, ESP32 taşıyıcısı ile güç panelindeki XL4016 C'nin arasından direğin sağına götür (yukarısı K2'de, direk arka yüzü)."),
    ('b2i U06 önerilen boy (K2 kablo)', "Önerilen boylar (yol × 1,25, hub'a gidenlere + 150 mm; tahmin): HDMI 950, hub uzatması 920, ESP32 USB 1.560, hoparlör 1.030, göğüs 12 V 1.720 mm (`planlama/adim3/elektrik.md`)."),
]
BEKLENEN["8bca2f5"] = (B2I_SILINEN, B2I_EKLENEN)
# P10.7b2k (F10u-gunluk.md): taban 896c9a7 (b2i). CAD'den bağımsız rehber uyumu: B5a bara tutucusu montajı (K64 a), K1 17.1 sıkma ve
# numara yönü, G16 / G22 şeması baradan, B6 K53 a çentiği, E3a iki TVS modelde (K51 a), E4 USB ses kartı modelden çıktı, B6a ESP32 yönü,
# K1'de "Yukarısı K2'de." tekrarı; düzeltme turu 1 (F10u-kontrol 1-4, 8: bara karede, sıkma F1'de, ESP32 yönü, E4 uzatma); turu 2 (T4 / T5, E3a D24V50F5, 17.7 yol 9); turu 3 (yelpaze, akü kayışı, 17.10 kesik). Liste uygulanan metinden (F10l-birlesim'in kendi çıktısı), etiketler elle (b2k_liste: anahtar sözcükle).
B2K_SILINEN = [
    ('b2k K1 G16 / G22 şeması baradan', 'Anahtarlı baranın yeri yaklaşık (modelde yok, röle yanından çizildi).'),
    ('b2k K1 G16 / G22 şeması baradan', 'Bara durumu (G22, 22 AWG): anahtarlı bara (yeri yaklaşık: modelde yok, röle yanından çizildi) → hat sigortası → arayüz kartı, PC817 #2 girişi'),
    ('b2k B5a K64 a tutucu', 'Bara tutucusu (yıldız barasının ve anahtarlı baranın M5 saplamalarını taşıyan basılmış yalıtkan parça; `planlama/adim3/kablolar.json` bara pabuç kaydı) henüz tasarlanmadı: modelde ve baskı listesinde yok, sonraki tam taramalı CAD paketinde tasarlanıp basılacak, satın alınmayacak (K64 a).'),
    ('b2k B6 K53 a çentik', 'Bilinen açık konu (K53, karar bekliyor): modelde elektronik katı inerken ön şarj kartının iki ön naylon burcuna takılıyor; burç katın ön kenarından 0,425 mm taşıyor (`planlama/d158/F10b-olcum.json`).'),
    ('b2k E3a K51 a modelde', "Her iki 5 V çıkışına bir P6KE6V8A TVS (satın alma listesinde 2 adet, `planlama/maliyet.json`): SY8205 → QLED hattındaki modelde var, D24V50F5 → Pi hattındaki bugün modelde ve BOM'da yok, sonraki CAD paketinde eklenecek (K51 a)."),
    ('b2k B5a K64 a tutucu', 'K1\'in "Toprak ve iki bara" alt adımı iki barayı panelde varsayar'),
    ('b2k dt1 K1 17.4 yol 3 saplamada (F10u-kontrol 2)', "Karede Kablo yolu 3'ün baradan sol BTS7960B'ye giden kısmı (G12) da görünür; o uç §G bağlanır."),
    ('b2k E4 ses kartı modelden çıktı', "Karede PAM8403'ün yanındaki ikinci kart yedek USB ses kartıdır: takılmaz (önceki alt adım)."),
    ('b2k K1 17.1 kare notu', 'Karede görünmez: iki bara ve tutucuları modelde yok (tutucu CAD paketinde gelecek, K64 a); baralar güç panelinde (arka kat, B5a).'),
    ('b2k dt2 K1 17.7 yol 9 yıldız saplamasından (F10v)', "Karede vurgulu çizgi Kablo yolu 9'dur (G18, F4 → XL4016 çevre); çevre çıkışı G19 §G arayüz kartına bağlanır."),
    ('b2k dt1 K1 17.6 bara modelde (F10u-kontrol 2)', 'Karede yer: PC817 modülü arayüz kartının üstünde, arayüz kartı elektronik katında önden bakınca solda; anahtarlı bara karede görünmez (modelde yok, güç panelinde).'),
    ('b2k E4 ses kartı modelden çıktı', "Kartın köpük bandı da yapıştırılmaz; kart yedek parçalarla birlikte saklanır (KT2 geçmezse Pi USB 2'ye; `planlama/adim3/kablolama-on-kararlar.md` § 5 Ö1)."),
    ('b2k E4 ses kartı modelden çıktı', "Kartın köpük bandı da yapıştırılmaz; kart yedek parçalarla birlikte saklanır (KT2 geçmezse Pi USB 2'ye; `planlama/adim3/kablolama-on-kararlar.md` § 5 Ö1)."),
    ('b2k E4 ses kartı modelden çıktı', 'Masada: sol arka kabuk + PAM8403 (USB ses kartı yedek, takılmaz)'),
    ('b2k E4 ses kartı modelden çıktı', 'Modelde kart hâlâ çizili.'),
    ('b2k B5a K64 a tutucu', 'O zamana dek rehber panelde yerini ve bağlantı elemanını yazmaz.'),
    ('b2k dt3 K1 17.10 yol 11 / 12 kesik notu (şema adı cümlesi)', "Orta ve sağ sonar (Q01, Q02) bu şemada değil: kendi gösterim şemaları K1'de"),
    ('b2k E3a K51 a modelde', "SY8205 ve QLED hattı P6KE6V8A'sının tabladaki yeri modelde var; Pi hattı P6KE6V8A'sı modelde yok, yeri doğrulanmadı."),
    ('b2k dt3 K1 17.10 yol 11 / 12 kesik notu (şema adı cümlesi)', "Sinyal: BTS7960 sol PWM / EN / IS (B01, 22 AWG) → ESP32. Enkoderler (N01, N02) ve BTS sağ (B02) bu şemada değil: kendi gösterim şemaları K1'de."),
    ('b2k B6a ESP32 yönü (F10r-kontrol B1)', 'Tezgâhta, kat burçlara inmeden: kartları kata tak (arayüz kartı, dağıtım kartı A ve B, PCA9685, BNO055, ESP32 taşıyıcı), sonra kat üstündeki kartlar arası kabloları bağla.'),
    ('b2k E4 ses kartı modelden çıktı', "USB ses kartı takılmaz: çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür; bu eski tasarımdan kalan görüntüdür, uygulanmaz."),
    ('b2k E4 ses kartı modelden çıktı', "USB ses kartı takılmaz: çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür; bu eski tasarımdan kalan görüntüdür, uygulanmaz."),
    ('b2k K1 G16 / G22 şeması baradan', 'XL4016 C girişi (G16, 16 AWG): anahtarlı bara (yeri yaklaşık: modelde yok, röle yanından çizildi) → hat sigortası → XL4016 C IN'),
    ('b2k 17.11 tekrar (F10r-kontrol B1)', "Yukarısı K2'de."),
    ('b2k B6 K53 a çentik', "Çözüm seçilmedi (K53 karar bekliyor; seçenekleri F10b'de ölçüldü, `planlama/d158/F10b-gunluk.md`)"),
    ('b2k dt1 F1 bara tutucusuyla karede (F10u-kontrol 2)', 'Ölçü noktaları karede görünmez: PC817 #1 klemensi ve akü ölçüm bölücüsü arayüz kartının üstünde (elektronik katı, robota önden bakınca solda; kart üstü klemensler modelde çizili değil), yıldız barası güç panelinde (arka kat; bara modelde yok)'),
    ('b2k B5a K64 a tutucu', 'İki bara da M5 saplama üstünde halka pabuç yığını: saplama başına en çok 4 pabuç, büyük akımlı pabuçlar yığının altında, üstte düz pul + yaylı pul; WAGO yok.'),
    ('b2k dt4 E4 kabuk sırası öneri (F10y)', 'Sonra sağ kabuğu arkadan (−z) yerine koy: dikey dikişte sağ kabuğun bindirmesi solun altında kalır; sol önce takılırsa sağ hiçbir düz yönden girmiyor (giriş yolu ölçümü).'),
    ('b2k dt4 E4 kabuk sırası öneri (F10y)', 'Önce sağ kabuğu arkadan (−z) yerine koy, sonra solu (arkadan ya da soldan): dikey dikişte sağ kabuğun bindirmesi solun altında kalır; sol önce takılırsa sağ hiçbir düz yönden girmiyor (giriş yolu ölçümü).'),
]
B2K_EKLENEN = [
    ('b2k B5a K64 a tutucu', 'Altıgen cep baskıda dar çıkabilir: baş girmezse cep ısıyla oturtulur.'),
    ('b2k K1 G16 / G22 şeması baradan', 'Bara durumu (G22, 22 AWG): anahtarlı baranın 4 numaralı saplaması → hat sigortası → arayüz kartı, PC817 #2 girişi'),
    ('b2k K1 17.1 U06 şeridi', "Bara kablolarını panelin üstünde, pabuç yüksekliğinde yatay götür: ESP32 USB (U06, §G) yıldız barasının sağ yarısının önünden direğe çıkar, oradaki kabloları (G05: akü yarığından yıldızın 3 numaralı saplamasına; G17 ve G18: 4 numaralı saplamaya) panelden ≈ 20 mm'den yükseğe kaldırma."),
    ('b2k B5a K64 a tutucu', 'Bara tutucuları (K64 a; baskı listesinde iki PETG parça: yıldız barasınınki 5, anahtarlı barasınınki 4 saplamalı), tezgâhta, panel burçlara inmeden, altı açıkken: önce her tutucunun alt yüzündeki iki deliğe M3 ısıl gömme somunu havyayla göm.'),
    ('b2k B5a K64 a tutucu', "Bara tutucuları P10.7b2j'de modele girdi (K64 a, `planlama/d158/F10s-gunluk.md` § 4; basılır, satın alınmaz)."),
    ('b2k dt2 E3a D24V50F5 pin kenarı (F10v § 3)', "D24V50F5'i pin kenarı TVS'ye bakacak şekilde tak; pin sırası ürün sayfasında yok, ürün gelince kart üstündeki yazıyla doğrula."),
    ('b2k B5a K64 a tutucu', "Dokuz M5×25 altıgen başlı saplamayı alttan tutucunun altıgen ceplerine sok, üstten M5 somununu elle birkaç tur tak (saplama düşmesin; pabuçlar, pul ve yaylı pul K1'de)."),
    ('b2k B6a ESP32 yönü (F10r-kontrol B1)', "ESP32 DevKit'i taşıyıcının başlıklarına micro USB portu robota önden bakınca sağda (WROOM modülü solda) olacak yönde tak: kart başlığa ters yönde de girer; ters takılırsa bütün pinler yer değiştirir: taşıyıcının 5 V hattı bir GPIO pinine gelir ve F1'deki ilk enerjide (F4 takılınca) kart zarar görür (F1'de enerjiden önce yön bakışı var)."),
    ('b2k B6a ESP32 yönü (F10r-kontrol B1)', "ESP32 DevKit'in micro USB portu önden bakınca sağda (taşıyıcının sağ kenarı), WROOM modülü solda"),
    ('b2k B6 K53 a çentik', 'Elektronik katının arka kenarında (güç paneline bakan kenar), robota önden bakınca solda 1,5 mm derin çentik var (K53 a): kat inerken güç panelindeki ön şarj kartının iki ön burcuna takılmaz.'),
    ('b2k dt3 K1 17.10 yol 11 / 12 kesik notu (şema adı cümlesi)', "Enkoderler (N01, N02) ve BTS sağ (B02) bu şemada değil: kendi gösterim şemaları K1'de."),
    ('b2k K1 G16 / G22 şeması baradan', "G16 ve G22'nin şeması anahtarlı baradaki kendi saplamasından başlar (tutucu modelde, B5a); hat sigortaları ve pabuçlar modelde yok."),
    ('b2k E3a K51 a modelde', "Her iki 5 V çıkışına bir P6KE6V8A TVS (satın alma listesinde 2 adet, `planlama/maliyet.json`): SY8205 → QLED hattındaki ve D24V50F5 → Pi hattındaki, ikisi de modelde ve BOM'da var (K51 a)."),
    ('b2k dt1 E4 uzatma + dirsek (F10u-kontrol 8)', "KT2 geçmezse kartla birlikte siparişten çıkarılan ~30 cm USB-A uzatma ve L USB-A dirsek de gerekir (`planlama/adim3/kablolama-on-kararlar.md` § 5, § 17; alımları Ahmet'e sorulacak)."),
    ('b2k dt3 K1 17.10 yol 11 / 12 kesik notu', 'Kablo ön kat kesiğinden geçer; çizimdeki yol kesiğin dışında görünür'),
    ('b2k dt2 F1 ESP32 yön erişim çekincesi (T5)', "Kabuk ve etek takılıyken ESP32'nin üstten görülebildiği ölçülmedi, doğrulanmadı; asıl yön denetimi B6a'da"),
    ('b2k dt1 bara sıkma erişim çekincesi (F10u-kontrol 3)', 'Kabuk ve etek takılıyken güç paneline üstten erişim ölçülmedi, doğrulanmadı.'),
    ('b2k dt1 bara sıkma erişim çekincesi (F10u-kontrol 3)', 'Kabuk ve etek takılıyken panele üstten erişim ölçülmedi, doğrulanmadı'),
    ('b2k dt1 K1 17.4 yol 3 saplamada (F10u-kontrol 2)', "Karede Kablo yolu 3 (G08–G12) anahtarlı baranın 3 numaralı saplamasına gelir; yolun 1 numaralı saplamadan sol BTS7960B'ye giden kısmı (G12) da görünür; o uç §G bağlanır."),
    ('b2k K1 17.1 kare notu', 'Karede iki bara tutucusu saplamaları ve somunlarıyla görünür (B5a, K64 a); pabuçlar ve köprüler modelde yok.'),
    ('b2k dt1 K1 17.1 yol 2 saplamada (F10u-kontrol 1)', "Karede vurgulu çizgi Kablo yolu 2'dir (G05): yıldız barasının 3 numaralı saplamasında biter."),
    ('b2k dt2 K1 17.7 yol 9 yıldız saplamasından (F10v)', "Karede vurgulu çizgi Kablo yolu 9'dur (G18, F4 → XL4016 çevre; yıldız barasının 4 numaralı saplamasından geçer, − damarı orada ayrılır); çevre çıkışı G19 §G arayüz kartına bağlanır."),
    ('b2k dt1 K1 17.6 bara modelde (F10u-kontrol 2)', "Karede yer: PC817 modülü arayüz kartının üstünde, arayüz kartı elektronik katında önden bakınca solda; anahtarlı bara güç panelinde, tutucusuyla karede görünür (B5a); G22'nin şeması onun 4 numaralı saplamasından başlar."),
    ('b2k E4 ses kartı modelden çıktı', "Kart P10.7b2j'de modelden çıkarıldı, çizimde yok; KT2 geçmezse yeri yeniden çizilir."),
    ('b2k E4 ses kartı modelden çıktı', 'Masada: sol arka kabuk + PAM8403'),
    ('b2k dt3 K1 17.10 yol 11 / 12 kesik notu (şema adı cümlesi)', "Orta ve sağ sonar (Q01, Q02) bu şemada değil: kendi gösterim şemaları K1'de."),
    ('b2k B5a K64 a tutucu', 'Panelin altından tutucu başına 2 × ISO 7380 M3×10 ile ısıl gömme somunlara sık.'),
    ('b2k dt3 B3 yol 4 akü kayışı', 'Plaka altından geçen motor kablolarını (Kablo yolu 4) akü kayışıyla plaka arasına sıkıştırma, kayışa bağlama: kayış gerildiğinde kabloyu ezer'),
    ('b2k dt3 K1 17.10 yol 11 / 12 kesik notu', 'Q03 ve B01 elektronik katına ön kat kesiğinden geçer; karedeki Kablo yolu 11 ve 12 kesiğin dışında görünür (çizim kusuru).'),
    ('b2k E3a K51 a modelde', "SY8205'in ve iki P6KE6V8A'nın tabladaki yeri modelde var (Pi hattınınki D24V50F5'in önünde, K51 a); çeviricilerin çıkış uçlarının kart üstündeki yeri modelde yok (kart zarf olarak çizili): lehim yeri kart yazısıyla teyit."),
    ('b2k K1 17.1 numara yönü', 'Saplama numaraları robota önden bakınca soldan sağa (B5a).'),
    ('b2k B5a K64 a tutucu', 'Saplamalar panele değmez, yalıtım tutucudadır; saplama sonradan yalnız tutucu (ve panel) sökülerek değişir.'),
    ('b2k B5a K64 a tutucu', "Saplamalar robota önden bakınca soldan sağa 1'den numaralıdır (yıldız 1–5, anahtarlı 1–4; K1'deki saplama numaraları bu sırayla)."),
    ('b2k B5a K64 a tutucu', 'Saplamanın altıgen başlı olması varsayım: bara saplaması takımının baş tipi kayıtta yok; silindir başlı gelirse altıgen cep dönmeyi tutmaz, tutucu yeniden tasarlanır (siparişte altıgen baş seçilmeli).'),
    ('b2k dt3 K1 17.10 yol 11 / 12 kesik notu', 'Sinyal: BTS7960 sol PWM / EN / IS (B01, 22 AWG) → ESP32; kablo ön kat kesiğinden geçer, çizimdeki yol kesiğin dışında görünür.'),
    ('b2k K1 17.1 bara sıkma (güvenlik)', 'Somunu yaylı pul düzleşene kadar sık (≈ 2–2,5 N·m, tahmin, ölçülmedi; tutucuyu ezecek kadar değil).'),
    ('b2k B6a ESP32 yönü (F10r-kontrol B1)', 'Sonra kat üstündeki kartlar arası kabloları bağla.'),
    ('b2k B5a K64 a tutucu', 'Sonra tutucuyu panelin üstüne koy: yıldız barasınınki akü kablo yarıklarının hemen arkasına, anahtarlı barasınınki onun arkasına, röle hizasına (karede yerleri).'),
    ('b2k dt1 F1 ESP32 yön (F10u-kontrol 4)', 'Ters takılıysa enerji verme: kart 180° dönünce taşıyıcının 5 V hattı bir GPIO pinine gelir, F4 takılınca kart zarar görür.'),
    ('b2k B6a ESP32 yönü (F10r-kontrol B1)', 'Tezgâhta, kat burçlara inmeden: kartları kata tak (arayüz kartı, dağıtım kartı A ve B, PCA9685, BNO055, ESP32 taşıyıcı).'),
    ("b2k dt1 K1 17.1 sıkma F1'e bağlı (F10u-kontrol 3)", 'Tutucu PETG, sıkma altında zamanla gevşer: somunları F1\'de ilk enerjiden önce ("İlk enerji, aşama 1" kontrolünden önceki madde) ve ilk haftanın sonunda yeniden sık; ikisinde de ana anahtar kapalı, akü XT60\'tan ayrık, saat / yüzük çıkarılmış olmalı, lokma anahtarı bir baradan öbürüne değmesin.'),
    ('b2k B5a K64 a tutucu', 'Tutucu başına iki M3×10 ISO 7380 ve iki M3 ısıl gömme somun ile dokuz M5 düz pul satın alma listesinde ayrıca teyit edilir'),
    ('b2k E4 ses kartı modelden çıktı', "USB ses kartı takılmaz, çizimde de yok: kart yedek parçalarla birlikte saklanır (KT2 geçmezse Pi USB 2'ye; `planlama/adim3/kablolama-on-kararlar.md` § 5 Ö1)."),
    ('b2k E4 ses kartı modelden çıktı', "USB ses kartı takılmaz, çizimde de yok: kart yedek parçalarla birlikte saklanır (KT2 geçmezse Pi USB 2'ye; `planlama/adim3/kablolama-on-kararlar.md` § 5 Ö1)."),
    ('b2k K1 G16 / G22 şeması baradan', 'XL4016 C girişi (G16, 16 AWG): anahtarlı baranın 2 numaralı saplaması → hat sigortası → XL4016 C IN'),
    ('b2k dt1 F1 bara tutucusuyla karede (F10u-kontrol 2)', 'Ölçü noktaları karede görünmez: PC817 #1 klemensi ve akü ölçüm bölücüsü arayüz kartının üstünde (elektronik katı, robota önden bakınca solda; kart üstü klemensler modelde çizili değil), yıldız barası güç panelinde (arka kat; tutucusuyla karede, B5a)'),
    ('b2k dt3 K1 pabuç yelpazesi', 'İki bara da M5 saplama üstünde halka pabuç yığını: saplama başına en çok 4 pabuç (yıldızın 1, 2, 3, 4 ve 5, anahtarlının 1, 2, 3 ve 4 numaralı saplamalarında birden çok pabuç: pabuçları yelpaze gibi açarak diz, üst üste aynı yöne bindirme; somunu taktıktan sonra dişin tam kavradığına bak), büyük akımlı pabuçlar yığının altında, üstte düz pul + yaylı pul; WAGO yok.'),
    ('b2k B5a K64 a tutucu', "İki bara tutucusu panelde, panelin altından 2'şer M3×10 ile sıkı; dokuz saplama altıgen ceplerinde, elle döndürünce dönmüyor, üstte somunu elle takılı; yıldız barasınınki önde (akü kablo yarıklarının arkasında), anahtarlı barasınınki arkada (röle hizasında)"),
    ('b2k dt1 F1 ESP32 yön (F10u-kontrol 4)', "İlk enerjiden önce ESP32 DevKit'in yönüne bak: micro USB portu robota önden bakınca sağda, WROOM modülü solda (B6a)."),
    ('b2k dt1 F1 bara sıkma (F10u-kontrol 3)', 'İlk enerjiden önce, akü XT60\'tan ayrık ve ana anahtar kapalıyken: iki baranın dokuz M5 somununu yeniden sık (K1 "Toprak ve iki bara"; tutucu PETG, gevşer); saat / yüzük çıkar, lokma anahtarı iki baraya birden değmesin.'),
    ('b2k dt1 F1 bara sıkma (F10u-kontrol 3)', 'İlk haftanın sonunda aynı koşullarla bir kez daha.'),
    ('b2k B6 K53 a çentik', 'İniş boyunca ortak hacim 0, en küçük boşluk 0,5 mm (`planlama/d158/F10s-K53-olcum.json`; ölçüm düz yukarıdan inişle, eğik iniş ölçülmedi)'),
    ('b2k dt4 E4 kabuk sırası öneri (F10y)', 'Sonra sağ kabuğu arkadan (−z) yerine koy: dikey dikişte sağ kabuğun bindirmesi solun altında kalır, bu yüzden sağı soldan önce takmak kolaydır (sol önce takılırsa sağ yalnız sağdan, +x yönünde girer; giriş yolu ölçümü).'),
    ('b2k dt4 E4 kabuk sırası öneri (F10y)', 'Önce sağ kabuğu arkadan (−z) yerine koy, sonra solu (arkadan ya da soldan): dikey dikişte sağ kabuğun bindirmesi solun altında kalır, bu sırayla takmak kolaydır (sol önce takılırsa sağ yalnız sağdan, +x yönünde girer; giriş yolu ölçümü).'),
]
BEKLENEN["896c9a7"] = (B2K_SILINEN, B2K_EKLENEN)
# P10.8b (P108b-gunluk.md): taban 1d7fb71 (b2k + P10.8a, rehber_metin 3cefae0 ile aynı). K55 bant metni ölçümden (dil alttaki
# bantta; yol: yandan getir, sonra indir / it; "kuponla denenmedi" notu), K2 önerilen boylar kayıttan ({boy.<kimlik>}, F10r-kontrol D6).
# Liste uygulanan metinden (F10l-birlesim'in kendi çıktısı), etiketler elle.
# Düzeltme turu 1 (P108b-kontrol O1, O2, D1, D6): göğüs inişi sıkı geçme (hafifçe kalktı), omuzda dil engeli kalktı, etek ön ve
# omuz için "kupon henüz yok", K1 alt adım 4 saplama numara kuralı; eklenen 25 → 37, silinen 10 aynı.
# Düzeltme turu 2 (P108b-kontrol T2, T3): çerçeve notu "kupon henüz yok"; F1 / F3 çerçeve / F4'te "Oturmazsa zorlama …: tasarım
# kararını (K55 b) bekle."; eklenen 37 → 42.
P108B_SILINEN = [
    ('P10.8b K55 bant (ölçüm)', 'Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('P10.8b K55 bant (ölçüm)', 'Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('P10.8b K55 bant (ölçüm)', 'Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('P10.8b K55 bant (ölçüm)', 'Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('P10.8b K55 bant (ölçüm)', 'Bant düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('P10.8b K55 bant (ölçüm)', 'Bant düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('P10.8b K55 bant (ölçüm)', 'Bu bantta engel dil değil, z +105 braketinin perçin somunu (ölçüm): kuponda bu bant ayrıca, somun takılıyken denenir.'),
    ('P10.8b K55 bant (ölçüm)', 'Bu bantta engel dil değil, z +105 braketinin perçin somunu (ölçüm): kuponda bu bant ayrıca, somun takılıyken denenir.'),
    ('P10.8b K55 bant (ölçüm)', 'Çerçeve düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir).'),
    ('P10.8b D6 {boy.<kimlik>}', "Önerilen boylar (yol × 1,25, hub'a gidenlere + 150 mm; tahmin): HDMI 950, hub uzatması 920, ESP32 USB 1.560, hoparlör 1.030, göğüs 12 V 1.720 mm (`planlama/adim3/elektrik.md`)."),
]
P108B_EKLENEN = [
    ('P10.8b K55 bant (ölçüm)', 'Bandı dikişin 16 mm üstünde yandan (+x) getir, sonra aşağı indir.'),
    ('P10.8b K55 bant (ölçüm)', 'Bandı dikişin 16 mm üstünde yandan (−x) getir, sonra aşağı indir.'),
    ('P10.8b K55 bant (ölçüm)', 'Bandı dikişin 16 mm üstünde yandan getir (bu yol serbest, ölçüm), sonra aşağı indir.'),
    ('P10.8b K55 bant (ölçüm)', 'Bandı dikişin 24 mm üstünde yandan getir (bu yol serbest, ölçüm), sonra aşağı indir.'),
    ('P10.8b K55 bant (ölçüm)', "Bandı yerinin 10 mm önünde yandan (+x) getir (bu yol serbest, ölçüm), sonra önden içeri (−z) it: bu son 10 mm'de engel dil değil, z +105 braketinin perçin somunu (1–8 mm, ölçüm); bandı hafifçe esneterek somunun üstünden geçir (K55 a, geçici)."),
    ('P10.8b K55 bant (ölçüm)', "Bandı yerinin 10 mm önünde yandan (−x) getir (bu yol serbest, ölçüm), sonra önden içeri (−z) it: bu son 10 mm'de engel dil değil, z +105 braketinin perçin somunu (1–8 mm, ölçüm); bandı hafifçe esneterek somunun üstünden geçir (K55 a, geçici)."),
    ('P10.8b K55 bant (ölçüm)', 'Bandın esneyip geçeceği bilinmiyor.'),
    ('P10.8b K55 bant (ölçüm)', 'Bandın esneyip yerine oturup oturmayacağı bilinmiyor; buna kupon karar verir (K55 a, geçici).'),
    ('P10.8b K55 bant (ölçüm)', 'Bandın esneyip yerine oturup oturmayacağı bilinmiyor; buna kupon karar verir (K55 a, geçici).'),
    ('P10.8b K55 bant (ölçüm)', 'Bant düz bir yoldan girmiyor (ölçüm, Notlar).'),
    ('P10.8b K55 bant (ölçüm)', 'Bant düz bir yoldan girmiyor (ölçüm, Notlar).'),
    ('P10.8b K55 bant (ölçüm)', 'Bu geçme denenmedi; bu bant için kupon henüz yok.'),
    ('P10.8b K55 bant (ölçüm)', 'Bu geçme denenmedi; bu bant için kupon henüz yok.'),
    ('P10.8b K55 bant (ölçüm)', 'Bu geçme denenmedi; bu bant için kupon henüz yok.'),
    ('P10.8b K55 bant (ölçüm)', 'Bu geçme denenmedi; bu bant için kupon henüz yok.'),
    ('P10.8b K55 bant (ölçüm)', 'Bu geçme denenmedi; bu bant için kupon henüz yok.'),
    ('P10.8b K55 bant (ölçüm)', 'Bu geçme kuponla denenmedi; kupon sonucu gelince bu adım yeniden yazılabilir.'),
    ('P10.8b K55 bant (ölçüm)', 'Bu geçme kuponla denenmedi; kupon sonucu gelince bu adım yeniden yazılabilir.'),
    ('P10.8b K55 bant (ölçüm)', "Bu yolda engel bant değil, Ø84 rulman kapağı (yanal yolun son 4 mm'si ve inişte dikişin 16–7 mm üstü; ortak hacim en çok ≈ 300 mm³) ve kapak cıvataları (yanal yolun son 6 mm'si, ölçüm): bandın kenarı kapağın üstünden esnetilerek geçmeli (K55 a, geçici)."),
    ('P10.8b K55 bant (ölçüm)', 'Dil göğüs bandında; düz inişte dil engel değil (ölçüm).'),
    ('P10.8b K55 bant (ölçüm)', 'Dil göğüs bandında; y 1198 dikişinde kesit dik, düz inişte dil engel değil (ölçüm).'),
    ('P10.8b K55 bant (ölçüm)', 'Dil orta bantta.'),
    ('P10.8b K55 bant (ölçüm)', 'Dil orta bantta.'),
    ('P10.8b K55 bant (ölçüm)', 'Dil orta bantta: bu bandın z +88 kenarı orta bandın dilinin dışından geçer (ölçüm).'),
    ('P10.8b K55 bant (ölçüm)', 'Dil orta bantta: bu bandın z +88 kenarı orta bandın dilinin dışından geçer (ölçüm).'),
    ('P10.8b K55 bant (ölçüm)', 'Engel sağdaki gibi rulman kapağı ve kapak cıvataları (ölçüm): bandın kenarı kapağın üstünden esnetilerek geçmeli (K55 a, geçici).'),
    ('P10.8b K55 bant (ölçüm)', 'Oturmazsa zorlama (bant kırılabilir): kupon sonucunu ya da tasarım değişikliğini (K55 b) bekle.'),
    ('P10.8b K55 bant (ölçüm)', 'Oturmazsa zorlama (bant kırılabilir): kupon sonucunu ya da tasarım değişikliğini (K55 b) bekle.'),
    ('P10.8b K55 bant (ölçüm)', 'Oturmazsa zorlama (bant kırılabilir): tasarım kararını (K55 b) bekle.'),
    ('P10.8b K55 bant (ölçüm)', 'Oturmazsa zorlama (bant kırılabilir): tasarım kararını (K55 b) bekle.'),
    ('P10.8b K55 bant (ölçüm)', 'Oturmazsa zorlama (bant kırılabilir): tasarım kararını (K55 b) bekle.'),
    ('P10.8b K55 bant (ölçüm)', 'Oturmazsa zorlama (bant kırılabilir): tasarım kararını (K55 b) bekle.'),
    ('P10.8b K55 bant (ölçüm)', 'Oturmazsa zorlama (çerçeve kırılabilir): tasarım kararını (K55 b) bekle.'),
    ('P10.8b K55 bant (ölçüm)', 'Çerçeve düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; ölçüm: çerçeve kenarı göğüs bandının iç yüzünde).'),
    ('P10.8b K55 bant (ölçüm)', 'Ön yüz eğik, arka yüz dik: tek bir itiş ikisini birlikte kurtarmaz.'),
    ('P10.8b K55 bant (ölçüm)', 'Ön yüz eğik, arka yüz dik: tek bir itiş ikisini birlikte kurtarmaz.'),
    ('P10.8b K55 bant (ölçüm)', "İnişin son 12 mm'sinde bandın alt kenarı orta bandın dilinin dışından geçmeli; modelde bu geçme sıkı: orta bantla ortak hacim 1–12 mm boyunca, en çok ≈ 2.100 mm³, ölçüm; dikişe 10 mm kala radyal girişim önde 6,8 mm, ön-yan köşede 7,8 mm (kupon dilimi, ölçüm)."),
    ('P10.8b K55 bant (ölçüm)', "İnişin son 12 mm'sinde bandın alt kenarı orta bandın dilinin dışından geçmeli; modelde bu geçme sıkı: orta bantla ortak hacim 1–12 mm boyunca, en çok ≈ 2.200 mm³, ölçüm; dikişe 10 mm kala radyal girişim önde 6,8 mm, ön-yan köşede 7,8 mm (kupon dilimi, ölçüm)."),
    ('P10.8b K55 bant (ölçüm)', 'İnişte dikişin ısıl gömmeleri ve y 1095 braketinin perçin somunu da kenara değer (1–14 mm, ölçüm).'),
    ('P10.8b K55 bant (ölçüm)', 'İnişte x 0 dikişinde göğüs bandı sağın bindirmesi (1–18 mm), orta bant sağ (1–4 mm), dikişin ısıl gömmeleri ve braketin perçin somunu da değer (ölçüm).'),
    ('P10.8b düzeltme turu 1 17.4 numara', 'Saplama numaraları robota önden bakınca soldan sağa (B5a); karenin kamerası hafif soldan bakar, saplamaları önden bakışa göre say.'),
    ('P10.8b D6 {boy.<kimlik>}', "Önerilen boylar (yol × 1,25, hub'a gidenlere + 150 mm; tahmin): HDMI (H02) 950, hub uzatması (U03) 920, ESP32 USB (U06) 1.560, hoparlör (AU3) 1.030, göğüs 12 V (G21) 1.720 mm (`planlama/adim3/elektrik.md`)."),
]
BEKLENEN["1d7fb71"] = (P108B_SILINEN, P108B_EKLENEN)
BEKLENEN_SILINEN, BEKLENEN_EKLENEN = BEKLENEN.get(HEAD, ([], []))


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


_G = re.compile(r"(?:\b(?:K[12]) )?\bmadde \d+[a-z]?\b(?:'(?:de|da|te|ta)(?:ki)?)?|\balt adım \d+\.\d+\b(?:'(?:de|da|te|ta)(?:ki)?)?|"
                r"\bbu alt adımda (?:aşağıda|yukarıda)")


def esit_bicim(c):
    return _G.sub("§G", re.sub(r"^\d+[a-z]?\. ", "", norm(c)))


hata = []
# A
for kod in YENI.DEMET_ALT:
    a = YENI.ADIM_HAM[kod]
    birlesim = "\n".join([a["is_"]] + [g["is_"] for g in a["sira"]])
    if birlesim != YENI.ALT_TAM_HAM[kod]:
        hata.append("A %s: ana + alt adımlar ALT_TAM_HAM değil" % kod)
    h, p = YENI.capa_haritasi({kod: YENI.ALT_KAYNAK_HAM[kod]})
    kaynak_par = YENI.ALT_KAYNAK_HAM[kod].split("\n")
    tam_par = YENI.ALT_TAM_HAM[kod].split("\n")
    if len(kaynak_par) != len(tam_par):
        hata.append("A %s: paragraf sayısı %d → %d" % (kod, len(kaynak_par), len(tam_par)))
    for j, (k, t) in enumerate(zip(kaynak_par, tam_par)):
        if esit_bicim(k) != esit_bicim(t):
            hata.append("A %s paragraf %d: çapa / gönderme dışında fark" % (kod, j))
    print("A %s: ana + %d alt adım = ALT_TAM_HAM %s; %d paragraf, çapalı kaynakla gönderme dışında aynı %s" % (
        kod, len(a["sira"]), birlesim == YENI.ALT_TAM_HAM[kod], len(tam_par),
        all(esit_bicim(k) == esit_bicim(t) for k, t in zip(kaynak_par, tam_par))))


# B
def cumleler(R):
    out = collections.Counter()
    for y, t in RD.kaynak_metinler(R):
        if re.match(r"kaynak K[12] alt adım \d+ ad$", y):
            continue                                                   # kart adları ayrı sayılır (aşağıda)
        for c in re.split(RD._CUMLE_GENIS, t or ""):
            if c.strip():
                out[esit_bicim(c)] += 1
    return out


ce, cy = cumleler(ESKI), cumleler(YENI)
ekl, sil = cy - ce, ce - cy
bek_e = collections.Counter(c for s, c in BEKLENEN_EKLENEN)
bek_s = collections.Counter(c for s, c in BEKLENEN_SILINEN)
print("\nB cümle (bütün kaynak metinleri, yer bağımsız, çapa / gönderme eşit): eski %d, yeni %d; eklenen %d (beklenen %d), silinen %d "
      "(beklenen %d)" % (sum(ce.values()), sum(cy.values()), sum(ekl.values()), sum(bek_e.values()), sum(sil.values()), sum(bek_s.values())))
for c, n in sorted((ekl - bek_e).items()):
    hata.append("B beklenmeyen ekleme x%d: %s" % (n, c))
for c, n in sorted((bek_e - ekl).items()):
    hata.append("B beklenen ekleme yok x%d: %s" % (n, c))
for c, n in sorted((sil - bek_s).items()):
    hata.append("B beklenmeyen silme x%d: %s" % (n, c))
for c, n in sorted((bek_s - sil).items()):
    hata.append("B beklenen silme yok x%d: %s" % (n, c))
for s, c in BEKLENEN_SILINEN:
    print("  SİLİNDİ [%s] %s" % (s, c[:150]))
for s, c in BEKLENEN_EKLENEN:
    print("  EKLENDİ [%s] %s" % (s, c[:150]))
for kod in YENI.DEMET_ALT:
    e = [g.get("ad") for g in ESKI.ADIM_HAM[kod].get("sira") or []]
    y = [g.get("ad") for g in YENI.ADIM_HAM[kod]["sira"]]
    print("  kart adları %s: %d → %d; yeni: %s; kalkan: %s" % (kod, len(e), len(y), [x for x in y if x not in e] or "-",
                                                             [x for x in e if x not in y] or "-"))
# C
print("\nC gönderme: çevrilen %d, çözülemeyen %d" % (len(YENI.GONDERME_KAYIT), len(YENI.GONDERME_HATA)))
for e in YENI.GONDERME_KAYIT:
    print("  %s: %s madde %s → alt adım %d.%d" % (e["yer"], e["kod"], e["capa"], YENI.ALT_ADIM_NO[e["kod"]], e["hedef"]))
if YENI.GONDERME_HATA:
    hata += ["C " + x for x in YENI.GONDERME_HATA]
for x in hata:
    print("HATA", x)
print("\nbirlesim sinamasi: %s" % ("GECER" if not hata else "KALIR (%d)" % len(hata)))
sys.exit(0 if not hata else 1)
