# 3B montaj rehberi: adım koduna bağlı elle yazılmış metinler (CAD'den bağımsız; saf Python, FreeCAD'siz import edilir).
# Adımların sırası, iş tanımı, bağlantı elemanı, alet ve erişim notu planlama/adim4/M6-montaj-sirasi.md tablosundan okunur
# (rehber_veri.py). Burada tablonun vermediği şeyler var: kısa başlık, faz, kontrol listesi, kablo kancası, uçuş yönü, süre düzeltmesi.
# M6 tablosu 125 cm ve Y3 öncesi: C1 ve sonrasında iş metni, bağlantı, alet ve erişim buradan ezilir (04.11.2026). Kaynak: arayuz.py,
# BOM'lar, planlama/y1, y2, y3, adim3/elektrik.md, v4 malzeme listesi. Sayılar kol / omuz başına; toplam adet CAD parça listesinden gelir.
# M6_erisim 1,58 m'de koşulmadı; erişim mesafeleri 125 cm'den, Y3_erisim 1,65 m modülünden. Bir adım burada yoksa rehber yalnız M6 tablosuyla çalışır.
#
# Alanlar (hepsi isteğe bağlı):
#   baslik  : kısa başlık (yoksa M6 "Parça / iş" sütunu)
#   kontrol : kontrol listesi maddeleri
#   kablo   : kablo kancası (bu adımda hangi kanal / geçit / cırt boş bırakılır)
#   ucus    : bu adımın ana parçalarının geliş yönü (sağ taraf için; sol parçalarda X aynalanır). (x, y, z) ya da "radyal"
#   ucus_bag: alt montaj (tezgâh) robota bağlanırken geliş yönü
#   sure_dk : süre (dakika, tahmini); yoksa bağlantı sayısından tahmin edilir
#   not_    : ek uyarılar (app.js şu an göstermiyor)
#   is_, baglanti_md, alet, erisim : M6 tablosundaki aynı sütunu ezer

FAZ = [  # (kod öneki, faz adı); ilk eşleşen kazanır
    ("0", "Hazırlık"), ("A", "İskelet"), ("B", "Taban"), ("C0", "Taban"), ("K1", "Kablolama kapısı"), ("C1", "Kabuk braketleri"),
    ("D", "Omuzlar"), ("E", "Kafa"), ("K2", "Kablolama kapısı"), ("F5", "Son"), ("F", "Kabuk ve etek"), ("G", "Kollar"),
    ("H", "Kollar"),
]

HAZIRLIK = dict(
    kod="0", baslik="Hazırlık: parçalar, ısıl gömme somunlar, alet seti",
    is_="Baskı parçaları basılmış, destekleri temizlenmiş ve ısıl gömme somunları takılmış olmalı. Profiller kesilmiş, "
        "lazer parçalar gelmiş. Alet seti ve bağlantı elemanları adım adım kutulara ayrılmış.",
    kontrol=[
        "Baskı listesi (`planlama/baski-listesi.md`): 65 parça basıldı, destekler temizlendi",
        "Isıl gömme somunlar havyayla takıldı (M3 / M5; M7 kuponundaki sıcaklık ve derinlik)",
        "Sigma profiller kesildi: 2 uzun ray, 3 ara ray, gövde direği, omuz traversi; uçlar çapaksız, dik",
        "Alt plaka (Al 3 mm) ve iki kontrplak kat lazerden geldi; delikler kumpasla tutuyor",
        "Alet seti: alyan 2 / 2,5 / 3 / 4 / 5 (5 mm uzun küresel uçlu ≥ 150 mm), PH0 / PH1, 5,5 ve 7 mm anahtar, lokma, havya",
        "Bağlantı elemanları bu rehberin adım listelerine göre kutulara ayrıldı (adım başına bir kutu)",
        "Sol omuz ve sol kol parçaları aynalı basıldı (sağ ile karıştırma: üstüne 'SOL' yaz)",
        "Perçin somun pensesi hazır (ekip ayarlıyor): M5 gövde U braketleri Ø7,1, M3 etek L braketleri Ø5,1. Braket takılmadan tezgâhta çakmak kolay olur; kaynakta sıra yok, doğrulanmadı",
    ],
    kablo=["Henüz kablo yok. Servo kablolarını şimdi kesme: S2 kablosu G2'de kısaltılıp eklenir, bilek kablosu H1'de lehimle eklenir, diğerleri olduğu gibi kalır."],
    sure_dk=60,
)

ADIM = {
    "A1": dict(
        baslik="Şase çerçevesi",
        kontrol=[
            "Raylar düz bir masada; çerçeveyi gönyeyle kare tut, köşegenleri ölç (eşit olmalı)",
            "İç köşe bağlantıları kanala oturt, set vidaları önce hafif sık; kare doğrulanınca tam sık",
            "Ara rayların üst yüzü uzun raylarla aynı düzlemde (cetvel üstten geçsin)",
        ],
        kablo=["Uzun rayların üst kanalı boş kalsın: 11. adımda etek braketleri, 5. adımda plaka çekiç somunları buraya girer"],
        ucus="radyal",
    ),
    "A2": dict(
        baslik="Gövde direği",
        kontrol=[
            "Çekiç somunları cıvatayı takmadan önce kanala yerleştir (sonra kanal kapanır)",
            "Direk şaseye dik: iki yönden gönye ile kontrol et, sonra sık",
        ],
        kablo=["Direğin ön yüzü (z +) ve arka yüzü (z −) kablo için boş: K2'de servo uzatmaları ve kafa 12 V buradan çıkar"],
        ucus=(0, 1, 0),
    ),
    "A3": dict(
        baslik="Omuz traversi",
        kontrol=[
            "Travers direğe dik ve yatay (su terazisi)",
            "Travers uçları direğe göre simetrik: iki uçtan direk eksenine ölç, fark ≤ 1 mm",
            "Üst kanalda 2 çekiç somun boyun için şimdiden dursun (24. adım E1)",
        ],
        kablo=["Travers arkası S1 kablo uçları için boş kalsın (G4)"],
        ucus=(0, 1, 0),
    ),
    "B1a": dict(
        baslik="Tezgâh: alt plakaya burçlar ve akü takozu",
        kontrol=[
            "Naylon burçlar alttan, vidalar plakanın altından; burçlar elle sıkı, plastik ezilmesin",
            "Akü ön takozu M3×8 ile ısıl gömme somuna (sıkma hissi: M7 kupon C)",
        ],
        kablo=["Plakadaki motor kablo deliklerini (ön ve arka, z ±36) boş bırak: 7. ve 17. adımda motor kabloları buradan geçer"],
    ),
    "B1": dict(
        baslik="Alt plaka → şase",
        kontrol=[
            "Robotu yan yatır ya da sehpaya koy: cıvatalar alttan takılır",
            "14 çekiç somunu önce raylara diz, plakayı üstüne koy, cıvataları çaprazlama sık",
        ],
        kablo=["Plakanın kablo delikleri ve ray kanalları boş"],
        ucus_bag=(0, -1, 0),
    ),
    "B2a": dict(
        baslik="Motor braketleri",
        kontrol=["Braketleri motordan ÖNCE tak: motor takılınca braket M4'üne yalnız 3,2 mm kalır",
                 "Braket flanşı plaka kenarına paralel; teker ekseni x ±178'de"],
        ucus=(0, -1, 0),
    ),
    "B2b": dict(
        baslik="Motorlar → braket",
        kontrol=["Motorları tekerden ÖNCE tak: teker takılınca motor cıvatasına 11,5 mm kalır",
                 "Motor kablo çıkışı içe (robot merkezine) baksın"],
        kablo=["Motor ve enkoder kablolarını şimdi bağlama; uçları plaka üstüne al ve etiketle (ön sol, ön sağ, arka sol, arka sağ)"],
        ucus=(1, 0, 0),
    ),
    "B2": dict(
        baslik="Kaplinler ve tekerler",
        kontrol=["Kaplin set vidası milin düz yüzüne", "Teker eksenel vidası sıkılınca teker elle serbest dönmeli, yalpa yok"],
        ucus=(1, 0, 0),
    ),
    "B3": dict(
        baslik="Alt kat kartları ve akü",
        kontrol=["BTS7960 ve XL4016'lar burçlara üstten; kartın altı plakaya değmiyor (8 mm burç)",
                 "Akü kutupları güç paneline bakar; kayışları sık, akü kaymasın",
                 "Aküyü şimdi BAĞLAMA: XT60 uçları ayrık, kutuplar bantlı"],
        kablo=["XL4016 giriş/çıkış klemensleri erişilebilir kalsın (17. adım K1)",
               "Akü kayışlarının tokası yanda, kablo yolunun üstünde değil"],
        ucus=(0, 1, 0),
    ),
    "B4": dict(
        baslik="Kat burçları",
        kontrol=["8 saplama + çekiç somun; burçlar dik ve aynı boyda (40 mm)"],
        ucus=(0, 1, 0),
    ),
    "C0": dict(
        baslik="Etek braketleri (önce!)",
        kontrol=["Etek braketleri güç paneli ve elektronik katından ÖNCE: sonra M6 başına yalnız 30 mm kalır",
                 "Braket ayakları dışa baksın; z −105 / 0 / +105 hizası"],
        ucus=(0, 1, 0),
    ),
    "B5a": dict(
        baslik="Tezgâh: güç paneli",
        kontrol=["Sigorta kutusu, röle, ana sigorta yuvası ve ana anahtar panele (M4 + naylon somun)",
                 "Ön şarj direnci (5,6 Ω) panelden ≥ 5 mm yüksekte, kablo demetine değmez (E9)",
                 "XL4016 C ve ön şarj kartı da bu panelde (Y3 yerleşimi); giriş, çıkış klemensleri erişilebilir",
                 "Sigortaları henüz takma"],
        kablo=["Panelde WAGO yıldız noktası ve sigorta kutusu girişleri erişilebilir kalsın"],
    ),
    "B5": dict(
        baslik="Güç paneli → burçlar",
        kontrol=["Panel arka burçlara (z < 0); M5×12 + pul"],
        ucus_bag=(0, 1, 0),
    ),
    "B6a": dict(
        baslik="Tezgâh: elektronik katı",
        kontrol=["Burçlar alttan, kartlar üstten (arayüz kartı, 2 dağıtım kartı, PCA9685, BNO055, ESP32 taşıyıcı)",
                 "BNO055 yönü: kartın X oku robotun önüne (+z)"],
        kablo=["Kart konnektörleri erişilebilir; servo dağıtım çıkışları direğe bakar"],
    ),
    "B6": dict(
        baslik="Elektronik katı → burçlar",
        kontrol=["Kat ön burçlara (z > 0)"],
        ucus_bag=(0, 1, 0),
    ),
    "B7": dict(
        baslik="Sonarlar",
        kontrol=["3 sonar ön ara raya; sensör yüzleri dışa ve yere paralel"],
        kablo=["Sonar pin blokları içe baksın; kabloları K1'de bağlanır"],
        ucus=(0, 0, 1),
    ),
    "K1": dict(
        baslik="Kablolama kapısı 1: taban",
        is_="Kabuk takılmadan önce burada dur. Akü ayrık kalır; sırayla:\n"
            "1. Ana hat (12 AWG): XT60 → 30 A ana sigorta → ana anahtar → sigorta kutusu.\n"
            "2. F1 20 A → röle K1 → anahtarlı bara. Baradan: iki BTS7960B; hat sigortasıyla XL4016 A ve B (7,5 A), C (5 A).\n"
            "3. F3 kafa hattı (uç direk dibinde bırakılır), F4 XL4016 çevre 5 V, F5 acil stop hattı.\n"
            "4. Motor + enkoder ve sonarları bağla. Acil stop ucunu bırak: mantar F1'de takılır.\n"
            "5. Direğe çıkacak hatların taban kısmını da burada bağla (servo A / B / kafa, kafa 12 V, ESP32 USB). Yukarısı K2'de.",
        baglanti_md="Klemens, kablo pabucu, kablo bağı (adet: kablo listesi henüz yazılmadı)",
        alet="Multimetre, kablo soyucu, pabuç pensesi, tornavida",
        erisim="Kabuk yok; her yana düz erişim",
        kontrol=[
            "Akü ayrıkken multimetre: artı ile eksi arasında kısa devre yok",
            "XL4016 A / B / C 6 V, çevre 5 V'a ayarlandı (yükten önce, çıkış ölçülerek)",
            "Röle bobinine ters paralel 1N4007 takılı (MAH-112-C-4 dahili diyot yazmıyor)",
            "Hızlı klemens en çok 2,5 mm²: 12 AWG ana hatta kullanma",
            "BTS7960B kartının pin adları şemadakinden farklı olabilir: kart üstü yazıya göre bağla",
            "İsim karıştırma: burada K1 / K2 röle adıdır; Kablolama kapısı K1 / K2 ayrı şey",
            "Motor yön testi: her yan ileri komutta ileri döner",
            "PC817 modülü 3,3 V'ta ölçüldü: LOW < 0,4 V, HIGH > 2,5 V; tutmazsa `elektrik.md` E3'teki yedek devre",
            "Bara kapasitesi ölçüldü (ön şarj değeri için); ilk açılışta BMS kesiyor mu gözlendi",
        ],
        kablo=["Burada: 12 V ana hat, toprak, iki motor hattı, çevre 5 V, acil stop, sonar sinyal. Şemada renkli",
               "Direk boyunca gidenler K2 listesinde; o hatların taban kısmı da bu adımda bağlanır (şema bölünmedi)",
               "Kablo listesi (boy + kesit) henüz yazılmadı: kesitler `planlama/adim3/elektrik.md` blok şemasından"],
    ),
    "C1": dict(
        baslik="Gövde braketleri",
        is_="Direğin ±X kanallarına 8 U braket: y 400 / 530,25 / 687,75 / 1095, sağ ve sol (y zeminden).\n"
            "Her braket: önce 2 çekiç somunu kanala sür, braketi koy, cıvatayı elle başlat, yüksekliği ölç, sonra sık.\n"
            "M5 perçin somunlar (Ø7,1 delik) braketlerde. Tezgâhta, braket takılmadan çakmak kolay olur; kaynakta sıra yok, doğrulanmadı.",
        baglanti_md="1,58 m: 16 × M6×14 DIN 912, pulsuz + 16 çekiç somun (braket başına 2). M6'daki 4 braket / y 780 eski",
        alet="alyan 5, L",
        erisim="L (125 cm ölçümü 80 mm; 1,58 m'de ölçülmedi)",
        kontrol=["8 braket yerinde, aynı y'de sağ ve sol aynı hizada: kabuk M5'leri buraya gelecek",
                 "Perçin somunlar oturdu, cıvata elle dönüyor"],
        kablo=["Direğin ön (z +26) ve arka (z −26) yüzü boş kalsın: K2 hatları"],
        ucus=(1, 0, 0),
    ),
    "D1a": dict(
        baslik="Tezgâh: omuz yuvası + S1 servosu",
        is_="S1 servosunu omuz yuvasına oturt, kulaklarından cıvatala. Sağ ve sol ayrı ayrı; sol parça aynalı, karıştırma.",
        baglanti_md="Omuz başına 4 × M4×16 + 4 × M4 kontra somun",
        kontrol=["Somunu 7 mm açık ağızla tut (3 yönden girer), cıvatayı alyanla sık", "Servo yuvada boşluksuz, kablosu sıkışmıyor"],
    ),
    "D1b": dict(
        baslik="Tezgâh: S1 rulmanı + kapak",
        is_="6808-2RS rulmanı yuvaya bastır, rulman kapağını üstüne koy, cıvatala.",
        baglanti_md="Omuz başına 4 × M3×12 → yuvada ısıl gömme",
        kontrol=["Rulman elle ya da mengeneyle hafif girer; zorlarsa kupon ölçüsüne bak, çekiçleme",
                 "Sıkınca rulman hâlâ serbest dönüyor"],
    ),
    "D1c": dict(
        baslik="Tezgâh: S1 ortaya, horn",
        is_="S1 servosunu ortaya al, hornu tak, merkez vidasını sık. Orta komutun nasıl verileceği kaynakta yok (doğrulanmadı); kalan ofset yazılımda düzeltilir (Y2).",
        baglanti_md="Omuz başına 1 × M3×5 horn vidası",
        kontrol=["Horn merkez vidası sıkı, servo orta konumda"],
    ),
    "D1": dict(
        baslik="Omuz gövdesi → travers",
        is_="Çekiç somunları kanala al, omuz gövdesini travers ucundan kaydırarak sok, cıvataları sık. İki omuz da aynı.",
        baglanti_md="Omuz başına 4 × M6×16 + 4 çekiç somun",
        erisim="Omuz başına düz 3, L 1 (alttaki 141 mm). Servis: üst cıvata kabuk üst kapağındaki Ø14 delikten, L 85 mm",
        kontrol=["İki omuz travers ortasına eşit uzaklıkta", "Alttaki cıvata için uzun L anahtar hazır"],
        kablo=["S1 kablosunu travers arkasına al, uç boşta: G4'te kasete girer"],
        ucus_bag=(1, 0, 0),
    ),
    "E1a": dict(
        baslik="Tezgâh: boyun",
        is_="1. Pan servosunu servo yuvasına cıvatala.\n2. Rulman yuvasına 2 × 6808 rulmanı oturt, yuvayı cıvatala.\n3. Boyun plakasını tak.",
        baglanti_md="Pan servo 4 × M3×8 + pul → ısıl gömme; rulman yuvası 4 × M3×10 → ısıl gömme",
        kontrol=["Rulmanlar serbest dönüyor"],
        kablo=["Servo yuvasının arka kanalı (20 × 7,8) ve alt çıkışı (20 × 12) boş kalsın: boyun kablo yolu"],
    ),
    "E1": dict(
        baslik="Boyun → travers",
        is_="Boyun plakasını traversin üst kanalındaki 2 çekiç somuna (A3'te bırakıldı) cıvatala.",
        baglanti_md="2 × M6×20 + pul + 2 çekiç somun",
        kontrol=["Boyun traversin ortasında ve dik"],
        kablo=["Alt kablo çıkışı arkaya, direğe erişilebilir"],
        ucus_bag=(0, 1, 0),
    ),
    "E2a": dict(
        baslik="Pan servosu ortaya, horn",
        is_="Pan servosunu ortaya al, hornu tak, merkez vidasını sık. Boyun milinden önce: sonra vidaya ulaşılmaz.",
        kontrol=["Horn merkez vidası sıkı"],
    ),
    "E2b": dict(
        baslik="Boyun mili",
        is_="Boyun milini 6808 iç bileziklerine geçir, mili horna cıvatala. Eğme çatalından önce.",
        baglanti_md="4 × M3×8 mil–horn",
        kontrol=["Mil elle iki yana dönüyor, sürtmüyor"],
        kablo=["Milin içi Ø32 ve arka penceresi (20 × 10) kablo yolu: boş kalsın"],
    ),
    "E2c": dict(
        baslik="Boyun adaptörü + eğme çatalı",
        is_="1,58 m'de boyun yükseldi (Y2a): milin üstüne 62,8 mm yükseltme adaptörü (PETG-CF), onun üstüne eğme çatalı gelir. "
            "4 M3 saplamanın alt ucu mil flanşındaki ısıl gömmeye 5,5 mm vidalanır; üstte çatal tabanı + pul + somun.\n"
            "Tilt servosundan önce. Sıra M6 dışı: doğrulanmadı.",
        baglanti_md="1,58 m: 4 × M3 saplama DIN 976, 77 mm (kesilir) + pul + DIN 985. M6'daki 4 × M3×8 eski",
        alet="5,5 mm lokma ya da anahtar (M3 somun)",
        kontrol=["Saplamalar eşit boyda kesildi, uçlar temiz", "Somundan yaklaşık 1 mm taşma var, kablo yoluna değmiyor"],
        kablo=["Adaptörün içi Ø32: kablolar buradan geçer, boş kalsın"],
    ),
    "E2": dict(
        baslik="Tilt servosu",
        is_="Tilt servosunu çatala cıvatala. Karşı yanağa 625ZZ ve M5 pimi tak.",
        baglanti_md="4 × M4×16 + 4 kontra somun; 1 × M5×12 + pul",
        erisim="Düz. Kontra somunların 2'si cepte, 2'si açık ağızla (Y3 C3)",
        kontrol=["Tilt elle engelsiz, pim sıkıyken 625ZZ dönüyor"],
    ),
    "E3a": dict(
        baslik="Tezgâh: kafa içi",
        is_="Kafa iskeletine sırayla: Pi 5 (burç üstüne), kamera, D24V50F5 ve amfi (köpük bant + kablo bağı), tilt hornu.\n"
            "Kafa ekranı burada yazılmadı: model 7\", karar 10,1\" QLED; listedeki LCD satırına bakma (`planlama/rehber/R-gunluk.md`).",
        baglanti_md="Pi 4 × M2,5×8 burç + 4 × M2,5×5; kamera 4 × M2×8 PT; horn 1 × M3×5",
        alet="alyan 2, PH0, PH1",
        kontrol=["v4 listesi burcu 6 mm plastik diyor, tasarım 8 mm pirinç: Pi yüksekliğini kontrol et",
                 "Kamera FPC'si (300 mm) kırılmadan Pi'ye ulaşıyor; D24V50F5 → Pi USB-C yaklaşık 10 cm",
                 "Amfi CAD'de MAX98357A görünür; karar PAM8403"],
        kablo=["SY8205, 4'lü hub, USB ses kartı ve P6KE TVS'lerin kafadaki yeri modelde yok: doğrulanmadı, yer açık bırak"],
    ),
    "E3": dict(
        baslik="Kafa → tilt hornu",
        is_="Kafa alt montajını tilt hornuna, yanağından cıvatala. Kabuklardan önce: sonra cıvatalar kafa içinde kalır.",
        baglanti_md="4 × M3×8 yanak–horn",
        kontrol=["Kafa tilt ekseninde serbest; Pi kablolarına yük binmiyor"],
        ucus_bag=(0, 1, 0),
    ),
    "E4": dict(
        baslik="Kafa kabukları",
        is_="Yüz kabuğu sağ + sol ve arka kabuk sağ + sol. Önce kafa içi uçlar bağlanmalı (mantıksal sıra, doğrulanmadı): K2'deki 12 V ve USB gelince kabuk kapanır.",
        baglanti_md="1,58 m: dikiş M3×6 ISO 7380 (havşalı yerde M3×5); tabla → arka kabuk rafı 4 × M3×10 → ısıl gömme. M6'daki M3×8 + vizör eski, BOM'da vizör yok",
        alet="alyan 2 / 2,5",
        erisim="Düz. Servis arka kabuktan (125 cm'den; doğrulanmadı)",
        kontrol=["Dikişler aralıksız, kablo sıkışmadı", "Kafa pan ve tilt'te kabuğa sürtmüyor"],
    ),
    "K2": dict(
        baslik="Kablolama kapısı 2: gövde içi",
        is_="Kabuktan önce dur. Taban ucu K1'de bağlandı; burada direk boyunca çıkar:\n"
            "1. Kol servo uzatmaları: dağıtım A / B → etek → direk arka yüzü (z −26) → travers altı (y ≈ 1215) arkası → omuz.\n"
            "2. Kafa servoları: hat C → direk üstü R62 halkası.\n"
            "3. Kafa 12 V (18 AWG) ve ESP32 USB (VBUS'ta 1N5819): direk ön yüzü (z +26) → boyun.\n"
            "4. Boyun yolu: alt çıkış → servo yuvası arka kanalı → kablo odası → mil penceresi → Ø32 adaptör → sol yanak dışı → tabla geçişi (x −50…−37).\n"
            "5. Kablo bağıyla direğe tuttur. S1 uçları travers arkasında kalır: G4'te yarıktan girer.\n"
            "Göğüs ekranı kabloları bu adımda yazılmadı (`planlama/rehber/R-gunluk.md`).",
        baglanti_md="Kablo bağı (adet: kablo listesi henüz yazılmadı)",
        alet="Kumpas, yan keski, multimetre",
        erisim="Kabuk yok; arkadan ve önden düz erişim",
        kontrol=["Uzatma: ince duvarlı PVC düz 22 AWG, damar ≤ 1,5 mm; kumpasla ölç (silikon 22 AWG sığmaz)",
                 "v4 uzatmalar 1 m: dirsek ve bilek 1,86 m, S2 1,70 m gerekir, ek yapılacak. Ek yeri kaynakta yok (doğrulanmadı); ek U kasetine girmesin (3 aynı şerit)",
                 "Pan ve tilt elle tam açıda: boyunda kablo gerilmiyor",
                 "Her hat iki ucundan etiketli, süreklilik ölçüldü"],
        kablo=["Burada: servo A, servo B, servo kafa, kafa 12 V, enkoder / BTS sinyalleri + ESP32 → kafa USB. Şemada renkli",
               "Şemada taban kısımları da görünür: onlar K1'de bağlandı",
               "Kablo listesi (boy + kesit) henüz yazılmadı"],
    ),
    "F1": dict(
        baslik="Taban eteği",
        is_="1. 6 bant + 2 dolgu şeridi: orta → ön → arka (dolgu şeritleri modelde var, M6'da yok; sırası doğrulanmadı). Bindirmeleri bağla.\n"
            "2. Etek braketlerine dışarıdan M3×14 (L brakette M3 perçin somun, delik Ø5,1).\n"
            "3. Acil stop mantarını panel somunuyla tak, K1'de bırakılan ucu bağla.\n"
            "4. Ana anahtar düğmesi: delik Ø30 tahmini, anahtarı ölç.",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; braket 6 × M3×14 ISO 7380 dışarıdan + M3 perçin somun (Y3 K2). M6'daki içeriden M3×8 eski",
        alet="alyan 2 (acil stop için ayrıca anahtar)",
        erisim="Düz, dışarıdan",
        kontrol=["Acil stop NP2 BE102: CAD 60 mm; delik gerçek parçayla tutuyor mu bak", "Mantara basınca röle düşüyor"],
        kablo=["Etek bandını takarken K1 hatları sıkışmasın"],
        ucus="radyal",
    ),
    "F2": dict(
        baslik="Gövde alt ve orta bantları",
        is_="Gövde alt, uzatma 1, uzatma 2 ve orta bantları, sağ + sol, aşağıdan yukarı (uzatmalar M6'da yok; sıra doğrulanmadı). Dikişler y 476,5 / 634 / 791,5.\n"
            "Bindirmeleri bağla, sonra y 400, 530,25 ve 687,75 braketlerine dışarıdan M5×18 tak.",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; braket M5×18 ISO 7380 dışarıdan, pulsuz, M5 perçin somuna (y 400, 530,25, 687,75; Y3 K1). M6'daki içeriden M5×10 eski",
        alet="alyan 2 / 3",
        erisim="Düz, dışarıdan",
        kontrol=["M5 başı 0,3 mm oturma yuvasında", "Kablo ve bağ uçları bant arkasında sıkışmadı"],
        ucus="radyal",
    ),
    "F3": dict(
        baslik="Göğüs bantları",
        is_="Göğüs bantları sağ + sol, dikiş y 1005. Bindirmeleri bağla, y 1095 braketine dışarıdan M5×18 tak.\n"
            "Nextion kalktı. 11,6\" göğüs ekranı, çerçeve ve VESA taşıyıcının montajı ve kablosu bu adımda yazılmadı (`planlama/rehber/R-gunluk.md`).",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; y 1095 M5×18 ISO 7380 + M5 perçin somun. M6'daki Nextion DIN 912'leri eski",
        alet="alyan 2 / 3",
        erisim="Düz, dışarıdan",
        kontrol=["Cep üst kenarı köprü: destek temiz alındı, kenar kırık değil"],
        ucus="radyal",
    ),
    "F4": dict(
        baslik="Omuz bantları",
        is_="Omuz bantlarını Ø84 rulman kapağının üstünden geçir; üst kapak boynu sarar. M3×6 ISO 7380 ile bağla.\n"
            "Bundan sonra bant ancak göbek sökülünce çıkar.",
        baglanti_md="M3×6 ISO 7380",
        kontrol=["Yarık ψ 214 (12 × 6) kablo için açık; Ø84'e açılan anahtar deliği (Y3 K3) temiz",
                 "Bant kapağa sürtmüyor, boyun dönüyor"],
        kablo=["S1 uçlarına erişim kalmalı: G4'te yarıktan girecekler"],
        ucus="radyal",
    ),
    "G0": dict(
        baslik="Tezgâh: göbek + S1 tamburu",
        is_="Tamburu göbeğe −x yüzünden cıvatala. Önceden 2 Ø0,4 mumlu ipi bağlama yoluna geçir: halka altı oluk → iki dudak cebi, uçlar yaklaşık 80 mm yukarıda serbest.",
        baglanti_md="Kol başına 3 × M3×8 → göbekte ısıl gömme",
        kontrol=["2 ip geçti, uçlar serbest", "Dudak ceplerinde çapak yok"],
        kablo=["Tambur kablo kanalı boş: G3'te 3 şerit buraya oturur"],
    ),
    "G1": dict(
        baslik="Omuz göbeği → S1 hornu",
        is_="Göbeği S1 hornuna, 6808 iç bileziğinin üstüne cıvatala. S2 servosundan önce: sonra yalnız 13 mm kalır.",
        baglanti_md="Kol başına 4 × M3×12 göbek–horn",
        erisim="z+6 tarafındaki 2 cıvata ve alyan Ø6 kanaldan (Y3 C1); diğerleri düz",
        kontrol=["Göbek omuzda boşluksuz ve S1 ile dönüyor"],
        ucus_bag=(1, 0, 0),
    ),
    "G2": dict(
        baslik="S2 servosu → göbek",
        is_="1. S2 kablosunu kısalt ve uzatmaya ekle: G2'den yaklaşık 20 mm önce, göbek arka iç şeridinde (lehim + makaron Ø ≤ 4,5, yaklaşık 25 mm, ya da JR çifti; kablo bağı). Yer tahmini, yerinde ölç.\n"
            "2. Servoyu göbeğe cıvatala.\n3. Karşı tarafa 625ZZ ve M5 pim.",
        baglanti_md="Kol başına 4 × M4×16 + 4 kontra somun; 1 × M5×12 + pul",
        alet="alyan 3 / 4 + 7 mm",
        erisim="Düz. Somunların 2'si cepte, 2'si açık ağızla (Y3 C3)",
        kontrol=["Ek makaronla kaplı, çekince kopmuyor", "S2 ekseni elle dönüyor"],
    ),
    "G3": dict(
        baslik="S2 hornu, kol çatalı, üst kol tüpü",
        is_="1. S2 hornu, merkez vidası.\n2. Kol çatalı → horn.\n3. Üst kol tüpü → çatal.\n"
            "4. Kablolar: K noktası (çatal arka plakasının arkası, yapışkan taban) → S2 lobu L 80 (2 şerit) → tüp penceresi.\n"
            "5. G2 → tambur bağı (ψ 145): 3 şerit kanala teğet, 2 ip demetin üstünde düğüm.",
        baglanti_md="Kol başına 1 × M3×5 horn; 4 × M3×8 çatal–horn; 2 × M3×8 tüp → ısıl gömme",
        kontrol=["Tüp penceresi arka duvarda: 10 geniş, 14 düz + iki uç 45° (≈ 24 boy). M1 yalnız dişi JR'yi (7,9 × 2,75) denetledi; erkek JR (10,3 × 4) boyuna çevrilerek geçmeli, doğrulanmadı",
                 "Bağ açısı 0 ± 2°, düğüm cerrah + kare, uç 3 mm",
                 "K noktası tabanı CAD'de 10 × 10 (tahmini), v4 taban 28 × 28: sığması doğrulanmadı"],
        kablo=["Bu adımda geçen: tüp penceresi, S2 lobu (L 80), tambur bağı (ψ 145)"],
    ),
    "G4": dict(
        baslik="S1 kablo kaseti",
        is_="Sırayı bozma; +x'ten kaydırarak takılmaz.\n"
            "(a) Gövde önden radyal, x ofsetsiz, arka plaka omuz pedine yaslı. Kol: S1 −45 / −20 / 0 × S2 90 ya da S1 −45 × S2 5.\n"
            "(b) U'yu elle kanala koy; dış koşu duvar boyunca, ψ 214'te yarıktan içeri (ψ: arka 90, aşağı 180, ön 270). Lop L 171,4 mm (−5…0), kablo üstünde işaretli.\n"
            "(c) Duvar bağı: 2 ip, ψ 226,5 / 230, düğüm dışarıda; sıkarken demeti −x'e tut.\n"
            "(d) Kapak önden radyal; flanş gövdeden x +3,3…5 havada (S1 −45'te en çok +3,3).\n"
            "(e) Kapağı −x'e it: 2 Ø3 pim (ψ 331 ve kulak ψ 300) girer.\n"
            "(f) 2 dikme cıvatasını S1 −45 / S2 90'da sık (en az 8 mm erişim).",
        baglanti_md="Kol başına 2 × M3×8 dikme; 2 Ø3 pim; 2 Ø0,4 mumlu ip",
        alet="alyan 2,5, makas",
        erisim="Önden radyal; dikmeler yalnız S1 −45 / S2 90'da",
        kontrol=["Yarık 12 × 6: JR erkek geçer", "Kol tam taramada kablo gerilmiyor, kapağa sürtmüyor",
                 "S1 ≥ 120 iken S2 ≤ 117: bu sınırı aşma"],
        kablo=["Geçit: ψ 214 yarığı → travers arkasındaki S1 ucu (K2'de bırakıldı)"],
    ),
    "H0a": dict(
        baslik="Tezgâh: ön kol + servolar",
        is_="1. Dirsek ve bilek servolarını ön kola cıvatala. Bilek somunu cepte; dirsek alt iki kulak cıvatası Ø8 erişim deliğinden, somunu cepte (Y3 C2).\n"
            "2. Bilek kablosu: mil ucundan içe, geri, ara duvar çentiği (6 × 5), dirsek servosu arkası, tırnak.\n"
            "3. Dirsek kablosu üstten tırnağa. Tırnakta iki kablo; kablo bağı kanat + demet.",
        baglanti_md="Kol başına 8 × M4×16 + 8 kontra somun",
        erisim="Düz; somunlar cepte, dirsek alt kulaklar Ø8 delikten (Y3 C2)",
        kontrol=["Çentikte kablo ezilmedi", "Kablo bağı kanadı tırnağı tutuyor"],
        kablo=["Geçit: ara duvar çentiği 6 × 5 ve tırnak"],
    ),
    "H0b": dict(
        baslik="Tezgâh: dirsek hornu",
        is_="Dirsek hornu + merkez vidası. Çataldan önce.",
        baglanti_md="Kol başına 1 × M3×5",
        kontrol=["Vida sıkı, horn oturdu"],
    ),
    "H0c": dict(
        baslik="Tezgâh: dirsek çatalı",
        is_="1. Çatalı horna cıvatala; 625ZZ ve M5 pimi yanaktaki ısıl gömmeye tak (robotta erişilemez: göğüs bandı 8,9 mm).\n"
            "2. Kablo: tırnak → lop L 120 → çatal oluğu (6 geniş, 4,5 derin; 2 şerit, sıcak tutkal) → Ø10 delik.",
        baglanti_md="1,58 m: kol başına 4 × M3×12 DIN 912 + 2 × DIN 125-A pul çatal–horn (M6'daki M3×8 eski); 1 × M5×12 + pul",
        kontrol=["Dirseği 0…105 arasında elle dene: lop gerilmiyor, oluğa sürtmüyor"],
        kablo=["Geçit: çatal oluğu ve Ø10 delik"],
    ),
    "H0d": dict(
        baslik="Tezgâh: bilek hornu",
        is_="Bilek hornu + merkez vidası. Flanştan önce: sonra yalnız 0,3 mm kalır.",
        baglanti_md="Kol başına 1 × M3×5",
        kontrol=["Vida sıkı, horn oturdu"],
    ),
    "H0e": dict(
        baslik="Tezgâh: bilek flanşı",
        is_="Flanşı horna cıvatala. Elden önce: sonra yalnız 1,0 mm kalır.",
        baglanti_md="Kol başına 4 × M3×8",
        kontrol=["Flanş eksende, yalpa yok"],
    ),
    "H0f": dict(
        baslik="Tezgâh: el",
        is_="Eli yakasından flanşa cıvatala.",
        baglanti_md="Kol başına 2 × M3×6 ISO 7380 → ısıl gömme",
        kontrol=["El yalpasız; bilek elle dönüyor"],
    ),
    "H1": dict(
        baslik="Dirsek modülü → üst kol tüpü",
        is_="1. Kabloları tüp içinden G2'ye yolla: dirsek JR birleşimi tüp içinde (y −122…−62, hedef y −105); bilek lehim + makaron (Ø ≤ 4,5, yaklaşık 25 mm) tüp içinde, makaron tüp girişinin üstünde.\n"
            "2. Pim + bileziği tüpe geçir, sık.",
        baglanti_md="Kol başına 2 × M3×20 + 4 pul + 2 kontra somun",
        kontrol=["Kulaklar birbirine değmeden sık (M7 kupon D)", "Bilek kablosunda yaklaşık 0,5 mm artan var: çekme"],
        kablo=["Tüp içi: dirsek ve bilek kabloları G3'teki pencereden çıkar"],
        ucus_bag=(0, -1, 0),
    ),
    "F5": dict(
        baslik="Servis kapakları (test sonrası)",
        is_="Devreye alma testinden sonra kapat: arka servis kapağı, üst arka servis kapağı, etek H1 ve H2.\n"
            "H1 sigorta kutusuna açılır: uç yuvalar yedek, sık değişen F1, F3, F4, F5 ortada (29.10).",
        baglanti_md="1,58 m: arka kapak 7 × M3×6 ISO 7380; H1 4 × M3×6 (x ±50); üst kapak ve H2 parça listesinden (M6'da yok)",
        alet="alyan 2",
        erisim="Düz",
        kontrol=["E7 ve kafa ısı ölçümü kabuk kapalı yapıldı (kafada hesap ≈ 49 °C, ölçülmedi)", "Kapak altında kablo sıkışmadı"],
        ucus=(0, 0, -1),
    ),
}

# Y3 (C1–C3, K1–K7) CAD'e işlendi: "M6 CAD sonrası değişecek" bayrağı 125 cm JSON'undan geliyordu, kapalı.
M6_BAYRAK_ACIK = False

# Kablo yolu şemaları: direğe çıkan (y > etek üstü 262 + pay) K2, tabanda kalan K1.
KABLO_K2_Y_ESIK = 300.0


def kablo_kapisi(y_maks):
    return "K2" if y_maks > KABLO_K2_Y_ESIK else "K1"


# Tarihsel: M6 analizinin CAD değişikliği istediği bağlantılar (Y3'te işlendi; yalnız M6_BAYRAK_ACIK True iken görünür). YOK sınıfı M6 JSON'dan
# okunur (G4 kaset dikmeleri hariç: S1 −45°'de takılır, CAD istemez); K1/K2 el-kabuk-içi bağlantıları seçiciyle.
M6_CAD_NOT = {
    "C1": "Göbek–horn cıvatası göbek duvarında kapalı: hiç takılamaz (M6 CAD C1)",
    "C2": "Dirsek servosu kulak cıvatası / kontra somunu erişilemez (M6 CAD C2)",
    "C3": "Kontra somun anahtarla tutulamıyor (M6 CAD C3: altıgen cep ya da M4 ısıl gömme)",
    "K1": "Gövde braketi M5: alet yolu var ama el kabuğun içinde (M6 CAD K1: dışarıdan M5 + perçin somun)",
    "K2": "Etek braketi M3: içeriden, robot yatırılınca (M6 CAD K2: dışarıdan M3)",
}

# CAD etiketleri ASCII; rehberde gösterirken sık kelimeler Türkçeleştirilir (yalnız görüntü, kimlik değişmez).
TR = {
    "Sase": "Şase", "rayi": "rayı", "Ic": "İç", "kose": "köşe", "baglanti": "bağlantı", "Baglanti": "Bağlantı", "Govde": "Gövde",
    "govde": "gövde", "diregi": "direği", "Aku": "Akü", "aku": "akü", "kayisi": "kayışı", "Burc": "Burç", "burc": "burç",
    "surucu": "sürücü", "Arayuz": "Arayüz", "karti": "kartı", "dagitim": "dağıtım", "kati": "katı", "cevre": "çevre",
    "Guc": "Güç", "guc": "güç", "Cekic": "Çekiç", "cekic": "çekiç", "civata": "cıvata", "Civata": "Cıvata", "civatasi": "cıvatası",
    "Gogus": "Göğüs", "gogus": "göğüs", "bandi": "bandı", "gobegi": "göbeği", "Gobek": "Göbek", "catali": "çatalı",
    "Catal": "Çatal", "Egme": "Eğme", "on": "ön", "On": "Ön", "sag": "sağ", "Sag": "Sağ", "yuz": "yüz", "Yuz": "Yüz",
    "kabugu": "kabuğu", "Kabugu": "Kabuğu", "Isil": "Isıl", "gomme": "gömme", "Tutucu": "Tutucu", "tutucusu": "tutucusu",
    "Ust": "Üst", "ust": "üst", "tupu": "tüpü", "flansi": "flanşı", "Bilek": "Bilek", "Dirsek": "Dirsek", "dugmesi": "düğmesi",
    "Acil": "Acil", "Sigorta": "Sigorta", "Role": "Röle", "role": "röle", "Teker": "Teker", "Kaplin": "Kaplin", "altigen": "altıgen",
    "Kopuk": "Köpük", "cevirici": "çevirici", "Kafa": "Kafa", "iskeleti": "iskeleti", "Vizor": "Vizör", "siyah": "siyah",
    "kapagi": "kapağı", "Kapak": "Kapak", "yuvasi": "yuvası", "Rulman": "Rulman", "dis": "dış", "ic": "iç", "bilezik": "bilezik",
    "mili": "mili", "Boyun": "Boyun", "plakasi": "plakası", "braketi": "braketi", "etegi": "eteği", "Etek": "Etek", "ekrani": "ekranı",
    "yatik": "yatık", "Pul": "Pul", "kontra": "kontra", "somunu": "somunu", "Saplama": "Saplama", "agir": "ağır", "uzatma": "uzatma",
}
