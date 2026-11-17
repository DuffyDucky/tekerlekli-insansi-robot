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
HEAD = sys.argv[2] if len(sys.argv) > 2 else "b5fc255"          # P10.7b2f: taban b5fc255 (b2e'de 84f1a4a, b2d'de 1c4e882)
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
