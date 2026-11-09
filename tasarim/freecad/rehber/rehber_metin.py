# 3B montaj rehberi: adım koduna bağlı elle yazılmış metinler (CAD'den bağımsız; saf Python, FreeCAD'siz import edilir).
# Adımların sırası, iş tanımı, bağlantı elemanı, alet ve erişim notu planlama/adim4/M6-montaj-sirasi.md tablosundan okunur
# (rehber_veri.py). Burada tablonun vermediği şeyler var: kısa başlık, faz, kontrol listesi, kablo kancası, uçuş yönü, süre düzeltmesi.
# M6 tablosu 125 cm ve Y3 öncesi: C1 ve sonrasında iş metni, bağlantı, alet ve erişim buradan ezilir (04.11.2026). Kaynak: arayuz.py,
# BOM'lar, planlama/y1, y2, y3, adim3/elektrik.md, v4 malzeme listesi. Sayılar kol / omuz başına; toplam adet CAD parça listesinden gelir.
# M6_erisim 1,58 m'de koşulmadı; erişim mesafeleri 125 cm'den, Y3_erisim 1,65 m modülünden. Bir adım burada yoksa rehber yalnız M6 tablosuyla çalışır.
# F7a (09.11.2026): parça ataması 1,58 m'ye göre rehber_secici.py'de; F3'e göğüs ekranı, K2'ye göğüs ekranı uçları eklendi.
# F7b (09.11.2026, P7.2): kafa (E3a, E4: 10,1" QLED, tırnaklar, kamera, ReSpeaker, USB ses kartı, PAM8403), hoparlör (F2), hub (F5) ve
# K2 (05.11 B kararı: ESP32 USB hub'dan) metinleri; taban kablo şemalarının görünen adları (KABLO_AD); göğüs ekranı / ses / hub kablo
# yolları gösterim şeması olarak (SEMA, lale158/kablo_yolu_ekran.py); TR sözlüğü (ekranda ASCII kalıntı 0, rehber_denetim.py).
# Kaynaklar: kafa/kafa10_lib.py, arayuz.py SES_USB, lale158/kafa-yerlesim/uygulama-notu.md, planlama/adim3/elektrik.md,
# planlama/d158/karar-kuyrugu.md (K1, K6, K10, K11, K14, K16, K17). Ayrıntı planlama/d158/F7b-gunluk.md.
#
# Alanlar (hepsi isteğe bağlı):
#   baslik  : kısa başlık (yoksa M6 "Parça / iş" sütunu)
#   kontrol : kontrol listesi maddeleri
#   kablo   : kablo kancası (bu adımda hangi kanal / geçit / cırt boş bırakılır)
#   ucus    : bu adımın ana parçalarının geliş yönü (sağ taraf için; sol parçalarda X aynalanır). (x, y, z) ya da "radyal"
#   ucus_bag: alt montaj (tezgâh) robota bağlanırken geliş yönü
#   sure_dk : süre (dakika, tahmini); yoksa bağlantı sayısından tahmin edilir
#   not_    : ek uyarılar, doğrulanmamış bilgiler (app.js "Notlar" kutusunda gösterir; F7a)
#   kamera  : "arka" ise görünüm arkadan (yeni parçalar robotun arkasındaysa; F7a)
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
        "Baskı listesi (`planlama/baski-listesi.md`): 72 parça basıldı, destekler temizlendi",
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
                 "Aküyü şimdi BAĞLAMA: XT60 uçları ayrık, kutuplar bantlı",
                 "Kartlar takılmadan tezgâhta (bu adımdan önce): XL4016 A / B 6 V, çevre 5 V'a ayarlandı; akım sınırlı tezgâh kaynağıyla "
                 "12 V giriş, yüksüz, çıkış ölçülerek (K1 kontrolü). PC817 ölçümü de arayüz kartı takılmadan tezgâhta (B6a). Takıldıktan sonra "
                 "ayar vidasına erişim ölçülmedi; bu sıra kaynakta yok, doğrulanmadı"],
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
        # M6 tablosu "ana anahtar" da diyor; 1,58 m modelinde gövde etek plakasının altında, F1'de (F7a-kontrol O-2).
        is_="Tezgâh: güç paneline sigorta kutusu, röle ve ana sigorta yuvası. XL4016 C ve ön şarj kartı da burada. "
            "Ana anahtar bu panele girmez: etek üst plakasının altına F1'de takılır.",
        kontrol=["Sigorta kutusu, röle ve ana sigorta yuvası panele (M4 + naylon somun)",
                 "Ön şarj direnci (5,6 Ω) panelden ≥ 5 mm yüksekte, kablo demetine değmez (E9)",
                 "XL4016 C ve ön şarj kartı da bu panelde (Y3 yerleşimi); giriş, çıkış klemensleri erişilebilir",
                 "Sigortaları henüz takma",
                 "Kartlar takılmadan tezgâhta (bu adımdan önce): XL4016 C 6 V'a ayarlandı; akım sınırlı tezgâh kaynağıyla 12 V giriş, yüksüz, "
                 "çıkış ölçülerek (K1 kontrolü). PC817 ölçümü de arayüz kartı takılmadan tezgâhta (B6a). Bu sıra kaynakta yok, doğrulanmadı"],
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
                 "BNO055 yönü: kartın X oku robotun önüne (+z)",
                 "Kartlar takılmadan tezgâhta (bu adımdan önce): arayüz kartındaki PC817 3,3 V'ta ölçüldü: girişe akım sınırlı tezgâh "
                 "kaynağıyla 12 V ver ve kes, çıkış LOW < 0,4 V, HIGH > 2,5 V (`planlama/adim3/elektrik.md` E3 notu; K1 kontrolü). Sıra kaynakta yok, doğrulanmadı"],
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
        is_="Kabuk takılmadan önce burada dur. Bağlarken akü ayrık (XT60 açık); sırayla:\n"
            "1. Ana hat (12 AWG): XT60 → 30 A ana sigorta → ana anahtar → sigorta kutusu. Ana anahtar henüz yerinde değil "
            "(F1'de etek plakasının altına takılır): ana anahtara gidecek iki uç bırakılır, F1'de bağlanır.\n"
            "2. F1 20 A → röle K1 → anahtarlı bara. Baradan: iki BTS7960B; hat sigortasıyla XL4016 A ve B (7,5 A), C (5 A).\n"
            "3. F3 kafa hattı (uç direk dibinde bırakılır), F4 XL4016 çevre 5 V, F5 acil stop hattı.\n"
            "4. Motor + enkoder ve sonarları bağla. Acil stop ucunu bırak: mantar F1'de takılır.\n"
            "5. Direğe çıkacak hatların taban kısmını da burada bağla (servo A / B / kafa, kafa 12 V, ESP32 USB). Yukarısı K2'de.\n"
            "6. K1'de enerji verilmez: ana anahtar ve acil stop mantarı F1'de takılır. Mantar ve ana anahtar uçları hiçbir zaman "
            "köprülenmez; akü XT60 ayrık kalır, boştaki ana hat uçları gerilimsiz ve bantlı. XL4016 ayarı ve PC817 ölçümü kartlar takılmadan "
            "önce tezgâhta, akım sınırlı tezgâh kaynağıyla yapılır (kontrol; B3, B5a, B6a). İlk enerji iki aşamalı: F1 sonunda kafasız "
            "(aşama 1: ana anahtar, BMS, mantar; F1 takılı değil, anahtarlı bara enerjisiz), devreye alma ve motor yön testi F5'te (aşama 2). "
            "Bu sıra kaynakta yok, doğrulanmadı.",
        baglanti_md="Klemens, kablo pabucu, kablo bağı (adet: kablo listesi henüz yazılmadı)",
        alet="Multimetre, kablo soyucu, pabuç pensesi, tornavida",
        erisim="Kabuk yok; her yana düz erişim",
        kontrol=[
            "Akü ayrıkken multimetre: artı ile eksi arasında kısa devre yok",
            "Tezgâhta (kart takılmadan, B3 / B5a öncesi; B3 ve B5a kontrolünde de var): XL4016 A / B / C 6 V, çevre 5 V'a ayarlandı; akım sınırlı tezgâh kaynağıyla "
            "12 V giriş, yüksüz, çıkış ölçülerek",
            "Mantar ve ana anahtar uçları köprülenmedi; boştaki ana hat uçları bantlı, akü XT60 ayrık",
            "Röle bobinine ters paralel 1N4007 takılı (MAH-112-C-4 dahili diyot yazmıyor)",
            "Hızlı klemens en çok 2,5 mm²: 12 AWG ana hatta kullanma",
            "BTS7960B kartının pin adları şemadakinden farklı olabilir: kart üstü yazıya göre bağla",
            "İsim karıştırma: burada K1 / K2 röle adıdır; Kablolama kapısı K1 / K2 ayrı şey",
            "Tezgâhta (arayüz kartı takılmadan, B6a öncesi; akım sınırlı tezgâh kaynağıyla): PC817 modülü 3,3 V'ta ölçüldü: LOW < 0,4 V, HIGH > 2,5 V; tutmazsa `elektrik.md` E3'teki yedek devre",
            "Akü ayrıkken: bara kapasitesi multimetrenin kapasite kademesiyle ölçüldü (ön şarj değeri için)",
            "İlk açılış ve BMS gözlemi burada değil: F1 \"İlk enerji, aşama 1\"; devreye alma ve motor yön testi F5 \"İlk enerji, aşama 2\"",
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
        baslik="Tezgâh: kafa içi (Pi 5, 5 V çeviriciler)",
        # 1,58 m (kafa10_lib.py): tablada Pi 5 + D24V50F5 + SY8205 + TVS; QLED, tırnaklar, kamera, ReSpeaker, ses kartı, PAM8403 E4'te.
        is_="Kafa iskeletinin (tabla + yanaklar) üstüne, tezgâhta:\n"
            "1. Pi 5'i 4 pirinç burca tak: burç alttan M2,5×8, Pi üstten M2,5×5. Kablo kenarı öne: micro HDMI 0 kafa ekranına, "
            "micro HDMI 1 göğüs ekranına, CSI kameraya gidecek.\n"
            "2. Tablaya 1 mm köpük bant + kablo bağıyla: Pololu D24V50F5 (Pi'nin 5 V'u) ve SY8205 (kafa ekranının ayrı 5 V hattı). "
            "Her iki 5 V çıkışına bir P6KE6V8A TVS: SY8205 → QLED hattındaki modelde var, D24V50F5 → Pi hattındaki modelde ve BOM'da yok "
            "(ikinci TVS'i ayrıca al). TVS tek yönlü: katot (çizgili uç) +5 V'a, anot GND'ye.\n"
            "3. Sol yanağa 625ZZ dış bileziği; tilt hornu (25T alüminyum disk) ve merkez vidası bu adımın listesinde (M6 tablosu). "
            "Hornun önce servoya mı yanağa mı takılacağı kaynakta yok, doğrulanmadı.\n"
            "Kafa ekranı (10,1\" QLED), tırnaklar, kamera, ReSpeaker, USB ses kartı ve PAM8403 bu adımda takılmaz: kabuklarla birlikte E4'te.",
        baglanti_md="Pi: 4 × M2,5×8 pirinç burç + 4 × M2,5×5 (üst) + 4 × M2,5×8 DIN 912 (alt); D24V50F5, SY8205, TVS: 1 mm çift taraflı "
                    "köpük bant + kablo bağı; horn 1 × M3×5. M6'daki LCD 4 × M3×6 ve kamera 4 × M2×8 PT bu adımda yok (QLED tırnaklı, kamera E4'te)",
        alet="alyan 2, PH1, yan keski",
        kontrol=["v4 listesi burcu 6 mm plastik diyor, tasarım 8 mm pirinç: Pi yüksekliğini kontrol et",
                 "D24V50F5 → Pi USB-C yaklaşık 10 cm; çeviriciler köpük banda tam oturdu, kablo bağı sıkı",
                 "SY8205 çıkışı yük bağlanmadan, akım sınırlı tezgâh kaynağıyla (12 V, sınır 1 A) ölçüldü: 5 V (kafa ekranı hattı). "
                 "SY8205'te ters kutup koruması yazmıyor: kaynağın kutbunu bağlamadan önce kontrol et",
                 "Tabla geçişi (x −50…−37) boş: boyun kabloları K2'de buradan girer"],
        kablo=["Pi micro HDMI 0 (kafa ekranı) ve micro HDMI 1 (göğüs ekranı) fiş yerleri erişilebilir kalsın",
               "Kafa 12 V'u K2'de boyundan gelir: girişte P6KE18A (modelde yok), oradan D24V50F5 ve SY8205"],
        not_=["İki 5 V hattı birbirine köprülenmez: D24V50F5 Pi'yi, SY8205 kafa ekranını besler. Touch USB uyarısı E4'te "
              "(`planlama/adim3/elektrik.md`)",
              "SY8205 ve QLED hattı P6KE6V8A'sının tabladaki yeri modelde var; Pi hattı P6KE6V8A'sı modelde yok, yeri doğrulanmadı. "
              "TVS kutup yönü (katot +5 V'a) tek yönlü TVS'in genel bağlanışı; depo kaynağında yazmıyor, veri sayfasıyla doğrulanmadı",
              "QLED akımı 0,9 A varsayım, ölçülmedi"],
    ),
    "E3": dict(
        baslik="Kafa → tilt hornu",
        is_="Kafa alt montajını tilt hornuna, yanağından cıvatala. Kabuklardan önce: sonra cıvatalar kafa içinde kalır.",
        baglanti_md="4 × M3×8 yanak–horn",
        kontrol=["Kafa tilt ekseninde serbest; Pi kablolarına yük binmiyor"],
        ucus_bag=(0, 1, 0),
    ),
    "E4": dict(
        baslik="Kafa kabukları + yüz ekranı, kamera, ses",
        # kafa10_lib.py: QLED vida deliksiz, 4 tırnak (x ±85, üst / alt) M3×6 ISO 7380 + ısıl gömme, 1 mm köpük bant; kamera yüz kabuğu
        # boss'larına 4 × M2×8 PT; ReSpeaker sağ arka kabuk tavan boss'larına 3 × M2×8 PT; ses kartı + PAM8403 sol arka kabuk yan duvarı.
        is_="Kafa robotta, tilt hornunda (E3). Sıra kaynakta yok, montaj mantığından çıkarıldı: doğrulanmadı.\n"
            "1. Yüz kabuğu sağ + sol: kamerayı (Camera Module 3) ön duvarın içindeki boss'lara 4 × M2×8 PT ile vidala; lens ekranın üstündeki "
            "Ø9 delikte. CSI şeridini Pi'ye tak.\n"
            "2. 10,1\" QLED (vida deliği yok): camı yüz kabuğu ön duvarının iç yüzüne yasla, cep duvarı yerini gösterir. 4 tırnağı (üst ve alt, "
            "x ±85) cam şeridine 1 mm köpük bant üstünden arkadan bastır; her tırnak 1 × M3×6 ISO 7380 ile boss'taki ısıl gömmeye.\n"
            "3. QLED kabloları: HDMI (30 cm şerit, Pi micro HDMI 0), Power (SY8205 çıkışı, A ucu kesik micro USB kablo), Touch (Pi USB 4). "
            "Touch'ı takmadan önce Notlar'daki ölçümü yap.\n"
            "4. Arka kabuk sağ + sol: ReSpeaker Mic Array v2.0 tavanın altına, sağ arka kabuktaki boss'lara 3 × M2×8 PT. USB ses kartı ve "
            "PAM8403 sol arka kabuğun yan duvarına köpük bant + kablo bağıyla. Bağla: ReSpeaker → Pi USB 1, ses kartı → Pi USB 2 (uzatma + "
            "L dirsek), ses kartı L 3,5 mm → PAM girişi, PAM 5 V → D24V50F5 (varsayım, K10).\n"
            "5. Kabukları yerine koy, tabla → arka kabuk rafı 4 × M3×10. Boyundan gelen uçlar (kafa 12 V, göğüs HDMI, hub uzatması, "
            "hoparlör) K2'de bağlanır: arka kabuğun dikiş cıvatalarını K2'den sonra sık.",
        baglanti_md="1,58 m: tırnak 4 × M3×6 ISO 7380 → ısıl gömme + 4 köpük bant (1 mm); kamera 4 × M2×8 PT; ReSpeaker 3 × M2×8 PT (vida "
                    "tipi varsayım); ses kartı ve PAM8403 köpük bant + kablo bağı; tabla → arka kabuk rafı 4 × M3×10 DIN 912 → ısıl gömme; "
                    "kabuk dikişi 9 cıvata → ısıl gömme: 7 × M3×6 ISO 7380 + 2 × M3×5 ISO 7380 (havşalı tepe dikişi). M6'daki M3×8 + vizör "
                    "eski, BOM'da vizör yok",
        alet="alyan 2 / 2,5, PH0 / PH1 (M2 PT vidalar), yan keski",
        erisim="Düz. Kamera, tırnaklar ve QLED kabloları arka kabuk takılmadan kafanın içinden. Servis arka kabuktan (125 cm notu; "
               "1,58 m'de doğrulanmadı)",
        kontrol=["QLED camı ön duvarın iç yüzüne her kenarda dayalı; tırnak cama bastırıyor (cıvata tırnağı boss'a tutar), camı zorlamıyor",
                 "Kamera lensi Ø9 deliğin ortasında; CSI şeridi kırılmadan Pi'ye ulaşıyor",
                 "Touch takılmadan ölçüldü: QLED Power ile Touch VBUS arasında bağ var mı (Notlar)",
                 "ReSpeaker, ses kartı ve PAM8403 yerinde; kablo bağları fişleri zorlamıyor",
                 "Kafa pan ve tilt'te kabuğa sürtmüyor",
                 "Dikişler aralıksız, kablo sıkışmadı (dikiş cıvataları K2'den sonra)"],
        kablo=["Kafa içi: HDMI şerit Pi micro HDMI 0 → QLED, Touch Pi USB 4 → QLED, Power SY8205 → QLED, CSI Pi → kamera",
               "Ses: ReSpeaker → Pi USB 1, ses kartı → Pi USB 2, ses kartı L 3,5 mm → PAM8403, PAM 5 V → D24V50F5 (varsayım, K10). "
               "PAM çıkışından hoparlöre giden kablo K2'de boyundan iner",
               "Boyun uçları (kafa 12 V, göğüs HDMI → Pi micro HDMI 1, hub uzatması → Pi USB 3, hoparlör) K2'de bağlanır"],
        not_=["İki 5 V hattı birbirine köprülenmez. QLED'in Touch micro USB'si Pi'ye veri için gider; Touch VBUS ekranın içinde Power "
              "girişine bağlıysa Pi'nin 5 V'u ile SY8205 çıkışı Touch kablosu üzerinden birleşir. Bu iç bağ doğrulanmadı: Touch'ı Pi'ye "
              "takmadan multimetreyle Power ile Touch VBUS arasına bak; bağlıysa takma, çözüm o ölçümle seçilir (`planlama/adim3/elektrik.md`)",
              "Montaj sırası kaynakta yok (montaj mantığından), doğrulanmadı. Boyun uçları K2'de geldiği için arka kabuk dikişleri K2'den sonra sıkılır",
              "PAM8403'ün 5 V besleme noktası karar bekliyor (K10; varsayılan D24V50F5). Ses kartı ve PAM8403 ölçüsü tahmini; ReSpeaker vida "
              "tipi ve kütlesi varsayım",
              "Kafa ekranının kütlesi (600 g) ve akımı (0,9 A) varsayım, ölçülmedi"],
    ),
    "K2": dict(
        baslik="Kablolama kapısı 2: gövde içi",
        # 05.11 B kararı (karar-kuyrugu.md K5 / K17; lale158/kablo_yolu_ekran.py:6; elektrik.md "Boyun demeti" ve USB tablosu):
        # ESP32 USB ve göğüs dokunmatiği gövdedeki hub'dan çıkar, boyundan geçmez. Boyunda 5 kablo: kafa 12 V, tilt, göğüs HDMI, hub uzatması, hoparlör.
        is_="Kabuktan önce dur. Enerjisiz çalış: akü XT60 ayrık, F3 (kafa) takılı değil; kafa uçları enerjisiz bağlanır. "
            "Taban uçları K1'de bağlandı; burada direk ve boyun boyunca çıkar:\n"
            "1. Kol servo uzatmaları: dağıtım A / B → etek → direk arka yüzü (z −26) → travers altı (y ≈ 1215) arkası → omuz.\n"
            "2. Kafa servoları: hat C → direk üstü R62 halkası; tilt kablosu boyundan kafaya.\n"
            "3. Kafa 12 V (18 AWG çift): direk ön yüzü (z +26) → R62 → boyun → kafa girişi (D24V50F5 ve SY8205).\n"
            "4. ESP32 USB boyuna girmez (05.11 kararı): ESP32'den (taban) direk arka yüzü (z −26) boyunca yukarı; ucu "
            "üst arka kapak hizasında (y ≈ 1.085–1.157) hub için bırakılır, F5'te hub'a takılır. VBUS teline seri 1N5819: anot hub (Pi) "
            "tarafında, katot ESP32 tarafında; çevre 5 V hub'a / Pi'ye geri beslemez. ESP32 kartının kendi VBUS→VIN diyodu varsa "
            "gerekmez: multimetreyle bak (doğrulanmadı).\n"
            "5. Boyun demeti, 5 kablo: kafa 12 V, tilt servo, göğüs HDMI (Pi micro HDMI 1), hub uzatması (Pi USB 3 → hub), hoparlör (PAM8403 → "
            "hoparlör). Yol: alt çıkış → servo yuvası arka kanalı → kablo odası → mil penceresi → Ø32 adaptör → sol yanak dışı → tabla "
            "geçişi (x −50…−37). Kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı), sonra dikişleri sık.\n"
            "6. Boyundan inenler travers arkasından gövdeye: HDMI direğin solundan ekran arkasına (F3); hub uzatmasının ucu üst arka kapak "
            "hizasında (F5); hoparlör kablosu sağ önden göğüs altına (y ≈ 1.000; F2'de hoparlöre).\n"
            "7. Göğüs ekranı 12 V boyundan geçmez: tabandan ayrı daldan (mini 2 A → LM2577 + LM2596, 12 V) direk arka yüzünden çıkar, "
            "travers altında direğin soluna geçer, ekran arkasında bırakılır (F3). Regülatör ekrana bağlanmadan 12 V'a ayarlanır (kontrol).\n"
            "8. Kablo bağıyla direğe tuttur. S1 uçları travers arkasında kalır: G4'te yarıktan girer.",
        baglanti_md="Kablo bağı (adet: kablo listesi henüz yazılmadı)",
        alet="Kumpas, yan keski, multimetre",
        erisim="Kabuk yok; arkadan ve önden düz erişim. Kafa uçları arka kabuk dikişleri açıkken",
        kontrol=["Uzatma: ince duvarlı PVC düz 22 AWG, damar ≤ 1,5 mm; kumpasla ölç (silikon 22 AWG sığmaz)",
                 "v4 uzatmalar 1 m: dirsek ve bilek 1,86 m, S2 1,70 m gerekir, ek yapılacak. Ek yeri kaynakta yok (doğrulanmadı); ek U kasetine girmesin (3 aynı şerit)",
                 "Pan ve tilt elle tam açıda: boyunda 5 kablo gerilmiyor (boyun yuva kanalı %44,8 dolu, hesap)",
                 "Hub'a gidecek uçlarda (hub uzatması, ESP32 USB) yaklaşık 150 mm kapak söküm payı var",
                 "Kafa uçları bağlandı, arka kabuk dikişleri sıkıldı",
                 "Her hat iki ucundan etiketli, süreklilik ölçüldü",
                 "Göğüs ekranı regülatörü (LM2577 + LM2596) ekrana bağlanmadan, çıkışı multimetreyle 12 V'a ayarlandı: tezgâhta akım "
                 "sınırlı kaynakla (sınır 2 A) ve yük direnciyle (`planlama/adim3/elektrik.md`; `planlama/d158/testler/T7-gogus-ekrani-12v.md`)"],
        kablo=["Burada: servo A, servo B, servo kafa, kafa 12 V, enkoder / BTS sinyalleri (tabanda), boyun demeti, ESP32 USB ve göğüs ekranı "
               "kabloları. Şemada renkli",
               "Göğüs ekranı, hub ve ses yolları gösterim şemasıdır (`lale158/kablo_yolu_ekran.py`): parça sayısına girmez; kablo çapı, büküm "
               "yarıçapı ve port yeri doğrulanmadı",
               "Taban şeması 12'nin direkten kafaya çıkan kısmı eski (05.11 öncesi ESP32 → kafa USB); geçerli yol \"ESP32 USB\" şemasında",
               "Şemada taban kısımları da görünür: onlar K1'de bağlandı",
               "Önerilen boylar (yol × 1,25, hub'a gidenlere + 150 mm; tahmin): HDMI 950, hub uzatması 920, ESP32 USB 1.360, hoparlör 1.030, "
               "göğüs 12 V 1.720 mm (`planlama/adim3/elektrik.md`). Kablo listesi (boy + kesit) henüz yazılmadı"],
        not_=["Göğüs HDMI'si ve hub uzatmasının boyundan inmesi CAD'e göre; ekip teyidi bekliyor (K14), doğrulanmadı",
              "Göğüs ekranı 12 V dalının giriş noktası ve acil stop davranışı karar bekliyor (K11, `planlama/adim3/elektrik.md`)",
              "LM2577 + LM2596 kartı ve mini 2 A sigorta modelde yok; takılacakları yer (şemada güç paneli) doğrulanmadı",
              "Hoparlör kablosu (~1,1 m) ve hub uzatması (~1 m USB-A) robot için listede yok",
              "Hub kapanırsa ESP32 bağlantısı ve göğüs dokunmatiği birlikte düşer; hub girişindeki gerilim ölçülmedi"],
    ),
    "F1": dict(
        baslik="Taban eteği",
        is_="Bağlarken akü ayrık (XT60 açık).\n"
            "1. 6 bant + 2 dolgu şeridi: orta → ön → arka (dolgu şeritleri modelde var, M6'da yok; sırası doğrulanmadı). Bindirmeleri bağla.\n"
            "2. Etek braketlerine dışarıdan M3×14 (L brakette M3 perçin somun, delik Ø5,1).\n"
            "3. Acil stop mantarını panel somunuyla tak, K1'de bırakılan ucu bağla.\n"
            "4. Ana anahtar ASW-A01 gövdesini etek üst plakasının altına, acil stobun karşısına tak (model yeri öneri, ölçü tahmini zarf; "
            "bağlantı elemanı modelde yok, doğrulanmadı). K1'de bırakılan iki ana hat ucunu bağla. Düğme: delik Ø30 tahmini, anahtarı ölç.",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; braket 6 × M3×14 ISO 7380 dışarıdan + M3 perçin somun (Y3 K2). M6'daki içeriden M3×8 eski",
        alet="alyan 2 (acil stop için ayrıca anahtar)",
        erisim="Düz, dışarıdan",
        kontrol=["Acil stop NP2 BE102: CAD 60 mm; delik gerçek parçayla tutuyor mu bak",
                 "İlk enerji, aşama 1 (F1 sonu, kafasız): ana anahtar ve mantar bağlı. Saat, yüzük, bileklik çıkar "
                 "(`planlama/d158/testler/00-genel.md` kural 8). Akü XT60 ayrık, ana anahtar kapalıyken ana sigortayı (30 A), F4 (5 A, XL4016 "
                 "çevre 5 V: ESP32) ve F5 (2 A, acil stop: mantar, röle bobinleri) tak. F1 (20 A: röle K1 ve ön şarj kolu K2), F3 (5 A, kafa), "
                 "XL4016 hat sigortaları (A 7,5 A, B 7,5 A, C 5 A) ve göğüs ekranı mini 2 A takılı değil (`planlama/adim3/elektrik.md` sigorta "
                 "listesi): anahtarlı bara, kafa ve göğüs ekranı dalı enerjisiz, Pi enerjisiz. Devreye alma komutu Pi'den gelir (E3). ESP32'deki "
                 "program bilinmiyor: K2'yi süren GPIO2 kartın LED pini (E9), LED yakıp söndüren hazır bir program K2'yi açıp kapatabilir. F1 "
                 "takılı olmadığı için röle K1 ve K2'nin kontakları enerjisiz, anahtarlı bara enerjisiz kalır. Tekerlekler yerden kesik (şasi "
                 "takozda, `planlama/d158/testler/T13-rampada-acil-stop.md`); BTS EN = 0. Mantar ölçümü: akü ayrıkken multimetrenin kırmızı ucunu "
                 "arayüz kartındaki PC817 #1 giriş klemensine (mantar sonrası düğüm, E3), siyah ucunu güç panelindeki WAGO GND yıldız noktasına "
                 "bağla. Ölçü kıskacını mantar uçlarına takma. Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: BMS kesiyor mu "
                 "gözle (röle K1 açık; F3 takılı olmadığı için yalnız F4 / F5 girişleri, tam açılış aşama 2'de). Mantara basınca PC817 #1 girişi "
                 "0 V, bırakınca akü gerilimi (12,8–14,4 V). Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök. Devreye "
                 "alma, ön şarj ve motor yön testi F5'te (İlk enerji, aşama 2). Bu aşamalar, sigorta sırası, ölçü noktası ve \"yerden kesik\" "
                 "düzeni bu adım için kaynakta yok, doğrulanmadı"],
        kablo=["Etek bandını takarken K1 hatları sıkışmasın"],
        ucus="radyal",
    ),
    "F2": dict(
        baslik="Gövde alt ve orta bantları",
        # Hoparlör: kabuk_parcalar.py orta bant sağ duvarı (19 Ø3,5 delik, 2 boss), kap ön halka + flanşlı arka, kelepçe + köpük ped;
        # kablo ucu kelepçe köprüsünün altında, yer VARSAYIM (lale158/kablo_yolu_ekran.py F1a P1.7 notu).
        is_="1. Gövde alt, uzatma 1, uzatma 2 ve orta bantları, sağ + sol, aşağıdan yukarı (uzatmalar M6'da yok; sıra doğrulanmadı). Dikişler y 476,5 / 634 / 791,5.\n"
            "2. Bindirmeleri bağla, sonra y 400, 530,25 ve 687,75 braketlerine dışarıdan M5×18 tak.\n"
            "3. Hoparlör (40 × 20, 4 Ω, 3 W) orta bant sağın ön duvarında, ızgara deliklerinin arkasında: kabın ön halkasını duvara, "
            "hoparlörü içine, flanşlı arka kabı arkasına koy; kelepçeyi köpük pedle 2 × M3×20 ile boss'lardaki ısıl gömmeye sık. Orta bandı "
            "takmadan önce K2'de göğüs altında bırakılan hoparlör kablosunu (PAM8403'ten boyundan iner) hoparlöre bağla. Hoparlörün bu sıradaki "
            "yeri kaynakta yok, doğrulanmadı.",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; braket M5×18 ISO 7380 dışarıdan, pulsuz, M5 perçin somuna (y 400, 530,25, 687,75; Y3 K1). "
                    "Hoparlör kelepçesi 2 × M3×20 DIN 912 → ısıl gömme (boss) + köpük ped. M6'daki içeriden M5×10 eski",
        alet="alyan 2 / 2,5 / 3, havya (hoparlör ucu)",
        erisim="Düz, dışarıdan. Hoparlör orta bant takılmadan, bandın iç yüzünden",
        kontrol=["M5 başı 0,3 mm oturma yuvasında", "Kablo ve bağ uçları bant arkasında sıkışmadı",
                 "Hoparlör kablosu bağlandı, kelepçe köprüsünün altında ezilmiyor; kutup işaretli",
                 "Hoparlör kabı ızgara deliklerine ortalı, kelepçe hoparlörü sallanmadan tutuyor"],
        kablo=["Hoparlör kablosu: PAM8403 → boyun → travers arkası → sağ ön → göğüs altı (K2'de bırakıldı); burada hoparlöre bağlanır"],
        not_=["Hoparlör ekseni duvara paralel (yatayın 35° altı); kama kararı açık (K6), duyulabilirlik ölçülmedi",
              "Hoparlör kabı, kulakları, ızgarası ve kelepçesi varsayım: ürün elde görülmeden kesinleşmez (`kabuk_parcalar.py`), doğrulanmadı",
              "Hoparlör kablosunun ucunun yeri ve bağlantı biçimi (lehim tırnağı) varsayım: ürün elde yok, doğrulanmadı"],
        ucus="radyal",
    ),
    "F3": dict(
        baslik="Göğüs bantları + göğüs ekranı",
        is_="1. Göğüs bantları sağ + sol, dikiş y 1005. Bindirmeleri bağla (x = 0'da cep altı y 1022,7 ve cep üstü y 1222 dahil), "
            "y 1095 braketine dışarıdan M5×18 tak.\n"
            "2. VESA taşıyıcı (PETG-CF): ekran cebinden direğin ön (+Z) kanalına, 2 × M6×18 + pul + çekiç somun. Yükseklik kanalda ayarlanır; "
            "cıvatalara ekran takılmadan, plakanın ortasından ulaşılır.\n"
            "3. 11,6\" ekranı (kasalı) cebe koy. Akü XT60 ayrık, ana anahtar kapalıyken göğüs ekranı mini 2 A sigortasını tak (F1 aşama "
            "1'de takılı değildi; dal girişi K11'in varsayılanı a: ana anahtar sonrası, röle öncesi; b seçilirse bu ölçüm F5 aşama 2'ye "
            "kalır, doğrulanmadı). 12 V fişini takmadan önce regülatör çıkışını yeniden ölç: 12 V (K2'de ayarlandı; "
            "ölçünce enerjiyi kes). Sonra K2'de bırakılan HDMI ve 12 V uçlarını enerjisizken tak (90° fişler).\n"
            "4. Ekranı taşıyıcıya arkadan 4 × M4×12 + pul ile bağla (VESA 75 × 75): üst arka servis kapağı açık, direğin yanından.\n"
            "5. Çerçeve sağ + sol: göğüs bandına dışarıdan, yarı başına 4 × M3×6 ISO 7380, çerçeve flanşındaki ısıl gömmeye. "
            "Ekran camı çerçevenin 2 mm gerisinde, köşe takozlarına dayalı.\n"
            "Nextion kalktı. Bu sıra kaynaktaki erişim notlarından çıkarıldı, doğrulanmadı.",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; y 1095 M5×18 ISO 7380 + M5 perçin somun. Ekran: taşıyıcı 2 × M6×18 DIN 912 + pul + "
                    "çekiç somun; kasa 4 × M4×12 DIN 912 + DIN 125 pul; çerçeve 8 × M3×6 ISO 7380 → ısıl gömme. M6'daki Nextion DIN 912'leri eski",
        alet="alyan 2 / 3 / 5",
        erisim="Bant, çerçeve: düz, dışarıdan. Taşıyıcı M6: cepten, ekran takılmadan. VESA M4: arkadan, üst arka kapak açıkken "
               "direk yanından (`lale158/lale158_rapor.py` bağlantı tablosu; 1,58 m'de alet erişimi ölçülmedi)",
        kontrol=["Cep üst kenarı köprü: destek temiz alındı, kenar kırık değil",
                 "Ekran kasası direğe değmiyor (modelde ≥ 20 mm), göğüs bandına sürtmüyor",
                 "HDMI ve 12 V fişleri kasaya ezilmiyor; dokunmatik USB ucu F5'e kadar boşta, etiketli",
                 "Ekran camı çerçeveyle aynı açıda, köşelerde boşluk eşit"],
        kablo=["K2'de bırakılan göğüs ekranı HDMI ve 12 V uçları burada ekrana takılır; dokunmatik USB F5'te hub'a"],
        not_=["Göğüs ekranının montaj sırası kaynakta yok: bant → taşıyıcı → ekran → çerçeve sırası `lale158_rapor.py` erişim "
              "notlarından çıkarıldı, doğrulanmadı",
              "VESA deliklerinin kasadaki yeri ve M4 vida derinliği doğrulanmadı (plaka X yarığı ±8 mm ayar verir; vida 5,2 mm giriyor)",
              "Taşıyıcı direğin ön kanalında; K2'deki kafa 12 V hattı da direk ön yüzünden geçiyor: çakışma doğrulanmadı",
              "Ekran port yeri fotoğraftan tahmini (x ≈ −110, kısa kenar); ekran gelince ölçülecek",
              "HDMI'nin boyundan, dokunmatik USB'nin hub'dan gelmesi CAD'e göre; teyit yok, doğrulanmadı",
              "12 V dalı (mini 2 A → LM2577 + LM2596): giriş noktası ve acil stop davranışı karar bekliyor (`planlama/adim3/elektrik.md` K11)",
              "Regülatör kartı ve mini 2 A sigorta modelde yok; yerleri doğrulanmadı"],
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
        # Hub: arayuz.py SES_USB hub (y 1.085–1.157), kabuk_parcalar.py üst arka kapak hub takozu + 2 yan dayama + köpük bant;
        # port dağılımı elektrik.md USB tablosu (Hub 1 göğüs dokunmatiği, Hub 2 ESP32, Hub 3-4 boş; K1).
        is_="1. 4'lü USB hub üst arka servis kapağının içinde: hub'ı kapağın takozuna, iki yan dayamanın arasına 1 mm köpük bantla yapıştır. "
            "Bağla: hub kablosu ← Pi USB 3'ten boyundan gelen uzatma (K2), Hub 1 → göğüs ekranı dokunmatiği (F3'te boşta bırakılan USB), "
            "Hub 2 → ESP32 USB (K2'de direk arka yüzünden çıkarılan uç; 1N5819 yönü K2 madde 4). Hub 3 ve 4 boş. Hub'ın anahtarı açık kalmalı.\n"
            "2. İlk enerji, aşama 2 (devreye alma testi): kapaklar açık, hub bağlı (ESP32 ile Pi hub üzerinden konuşur). Saat, yüzük, "
            "bileklik çıkar (`planlama/d158/testler/00-genel.md` kural 8). Akü XT60 ayrık, ana anahtar kapalıyken F1 (20 A), F3 (5 A, kafa) "
            "ve XL4016 hat sigortalarını (A 7,5 A, B 7,5 A, C 5 A) tak (`planlama/adim3/elektrik.md` sigorta listesi). Tekerlekler yerden "
            "kesik (şasi takozda, `planlama/d158/testler/T13-rampada-acil-stop.md`); BTS EN = 0. Kollar aşağıda başlar: mantara basınca "
            "servo gücü de kesilir ve kollar düşer (E3 DTR / RTS notu). Kolların erişim alanında ve düşme hattında, kafanın ve tekerlerin "
            "erişim alanında kimse yok, bir kişi yalnız mantarda (kural 1 ve 7). Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana "
            "anahtarı aç: BMS kesiyor mu gözle (röle K1 açık; F3 / F4 / F5 girişleri, Pololu dahil; K11 a ise göğüs ekranı dalı da). "
            "Pi açılır; ESP32, Pi seri portu açılınca resetlenmemeli (boot mesajı yok; E3 DTR / RTS). Pi'den devreye al, ESP32 ön şarj "
            "dizisi (E9): ön koşul (mantar serbest, servo hedefleri son konumda, BTS EN = 0 ve PWM = 0) → röle K2 → 300 ms → PC817 #2 LOW "
            "(bara var) → röle K1 → 100 ms sonra K2 bırakılır → PC817 #2 LOW teyidi. Mantara basınca K1 düşer (K2 devreye almadan 100 ms "
            "sonra zaten bırakıldı), anahtarlı bara kesilir (PC817 #2 HIGH), kollar düşer. Mantarı bırak: röle kendiliğinden çekmez, "
            "yeniden devreye alma yalnız Pi komutuyla. "
            "Motor yön testi: her yan ileri komutta ileri döner; dönen tekere el uzatılmaz. Bitince ana anahtarı kapat, aküyü XT60'tan ayır "
            "(`planlama/adim3/elektrik.md` E3, E9). Bu adımdaki sıra kaynakta yok, doğrulanmadı.\n"
            "3. Testten sonra kapat: arka servis kapağı, üst arka servis kapağı (hub'la birlikte), etek H1 ve H2.\n"
            "H1 sigorta kutusuna açılır: uç yuvalar yedek, sık değişen F1, F3, F4, F5 ortada (29.10).",
        baglanti_md="1,58 m: arka kapak 7 × M3×6 ISO 7380; üst arka kapak 7 × M3×6 ISO 7380; H1 4 × M3×6 (x ±50); H2 4 × M3×6; hepsi "
                    "ısıl gömmeye. Hub: 1 mm köpük bant (kapak takozunda). Üst kapak, H2 ve hub M6'da yok",
        alet="alyan 2",
        erisim="Düz. Hub kapağın iç yüzünde: kapak açıkken bağlanır",
        kontrol=["Hub köpük banda oturdu, yan dayamalar arasında; anahtarı açık",
                 "İlk enerji, aşama 2 (madde 2): BMS kesmedi; ön şarj dizisi PC817 #2 teyidiyle bitti; mantara basınca K1 düştü, bara kesildi; "
                 "her yan ileri komutta ileri döndü; sonunda akü XT60'tan ayrıldı",
                 "Testte ESP32 ve göğüs dokunmatiği hub üzerinden görünüyor",
                 "Kapak açılınca hub'a bağlı üç kablo gerilmiyor (yaklaşık 150 mm söküm payı)",
                 "E7 ve kafa ısı ölçümü kabuk kapalı yapıldı (kafada hesap ≈ 49 °C, ölçülmedi)", "Kapak altında kablo sıkışmadı"],
        kablo=["Hub: Pi USB 3 → boyun → hub (uzatma), Hub 1 → göğüs dokunmatiği, Hub 2 → ESP32. Hub kapanırsa ESP32 ve göğüs dokunmatiği birlikte düşer"],
        not_=["Ön şarj dizisi ESP32 yazılımında (`planlama/adim3/elektrik.md` E9, adım 1–6): yazılım hazır değilse aşama 2 yapılmaz, "
              "röleler elle kapatılmaz (kaynakta yok, doğrulanmadı)",
              "Hub'ın kapakla birlikte açılması ve 150 mm söküm payı tahmin; testten önce hub bağlantısının yapılması montaj mantığından, "
              "kaynakta sıra yok: doğrulanmadı",
              "Hub girişindeki gerilim ölçülmedi (hub USB'den beslenir)",
              "Altıncı USB cihazı karar bekliyor (K1): şimdilik hub'da 2 port boş"],
        ucus=(0, 0, -1),
        kamera="arka",
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
    # F7a (1,58 m parçaları)
    "Cerceve": "Çerçeve", "cercevesi": "çerçevesi", "Tasiyici": "Taşıyıcı", "tasiyici": "taşıyıcı", "kasali": "kasalı",
    "Hoparlor": "Hoparlör", "hoparlor": "hoparlör", "kabi": "kabı", "kelepcesi": "kelepçesi", "kelepce": "kelepçe", "seridi": "şeridi",
    "tirnagi": "tırnağı", "Tirnak": "Tırnak", "tirnak": "tırnak", "yukseltme": "yükseltme", "adaptoru": "adaptörü", "Percin": "Perçin",
    "percin": "perçin", "ici": "içi", "rafi": "rafı",
}

# ---------------------------------------------------------------- F7b (P7.2): görünen metin katmanı (yalnız görüntü; kimlik, kod ve sayım değişmez)
# CAD etiketleri ASCII. TR_EK küçük harf anahtarlıdır; tr() büyük harfle başlayan kelimeyi de çevirir (Türkçe büyük harf: i -> İ).
# Ekranda ASCII kalıntı denetimi: tasarim/freecad/rehber/rehber_denetim.py (rehber_uret.py her koşuda çağırır).
TR_EK = {
    "acma": "açma", "adaptoru": "adaptörü", "agir": "ağır", "aku": "akü", "altigen": "altıgen", "altindan": "altından",
    "aluminyum": "alüminyum", "arayuz": "arayüz", "ayirici": "ayırıcı", "ayri": "ayrı", "baglama": "bağlama", "baglanti": "bağlantı",
    "bas": "baş", "baski": "baskı", "bicak": "bıçak", "blogu": "bloğu", "bolucu": "bölücü", "bukum": "büküm", "burc": "burç",
    "catal": "çatal", "catalda": "çatalda", "catali": "çatalı", "cekic": "çekiç", "celik": "çelik", "cerceve": "çerçeve",
    "cercevesi": "çerçevesi", "cevre": "çevre", "cevirici": "çevirici", "cift": "çift", "cikis": "çıkış", "cirt": "cırt",
    "deligi": "deliği", "deliginden": "deliğinden", "direnc": "direnç", "direncler": "dirençler", "disi": "dişi", "dokum": "döküm",
    "donusturuculer": "dönüştürücüler", "dugum": "düğüm", "dusurucu": "düşürücü", "duz": "düz", "duzeni": "düzeni", "egme": "eğme",
    "ekrani": "ekranı", "flans": "flanş", "flansi": "flanşı", "flansli": "flanşlı", "flansta": "flanşta", "fotograftan": "fotoğraftan",
    "genis": "geniş", "girisi": "girişi", "gobegi": "göbeği", "gobek": "göbek", "gobekte": "göbekte", "gomme": "gömme",
    "gosterim": "gösterim", "govde": "gövde", "govdesi": "gövdesi", "guc": "güç", "halkasindan": "halkasından", "hattinda": "hattında",
    "havsada": "havşada", "hoparlor": "hoparlör", "ic": "iç", "icin": "için", "imalat": "imalat", "isil": "ısıl", "kanali": "kanalı",
    "kapagi": "kapağı", "kapakli": "kapaklı", "karti": "kartı", "kati": "katı", "kaucuk": "kauçuk", "kayis": "kayış", "kopuk": "köpük",
    "kose": "köşe", "mantari": "mantarı", "noktasi": "noktası", "olcu": "ölçü", "olculecek": "ölçülecek", "on": "ön", "one": "öne",
    "percin": "perçin", "pirinc": "pirinç", "plakasi": "plakası", "regulatorunden": "regülatöründen", "role": "röle", "rolesi": "rölesi",
    "sag": "sağ", "sarj": "şarj", "satin": "satın", "satir": "satır", "sensorler": "sensörler", "sigortasi": "sigortası",
    "sonrasi": "sonrası", "tarafli": "taraflı", "tasiyici": "taşıyıcı", "tekerlegi": "tekerleği", "tirnagi": "tırnağı", "tum": "tüm",
    "tup": "tüp", "tupu": "tüpü", "ust": "üst", "ustu": "üstü", "ustunden": "üstünden", "uzatmalari": "uzatmaları", "vidasi": "vidası",
    "yerlesim": "yerleşim", "yildiz": "yıldız", "yukseltme": "yükseltme", "yuvasi": "yuvası", "yuz": "yüz", "yuzu": "yüzü",
    "olculer": "ölçüler", "dis": "dış", "kelepce": "kelepçe",
}
# Kelime düzeyinde çevrilemeyenler (büyük harfli Türkçe, birleşik yazım, çap işareti, ok). Sıra önemli; tr() önce bunları uygular.
TR_IFADE = [
    (r"(\d+(?:,\d+)?) ?in\b", r'\1"'),               # 10,1in -> 10,1"
    (r"\bO(\d)", r"Ø\1"),                              # O0,4 / O32 -> Ø
    (r"\bone-arka\b", "ön-arka"), (r"\b4 lu\b", "4'lü"), (r"\bVARSAYIM\b", "varsayım"), (r"\bTAHMINI\b", "tahmini"), (r"\bTAHMIN\b", "tahmin"),
    (r"\bDOGRULANMADI\b", "doğrulanmadı"), (r" ?-> ?", " → "), (r"\bpsi (\d)", r"ψ \1"), (r"\btas diren[cç]", "taş direnç"),
]
TUR_AD = {"Baski": "Baskı", "Satin": "Satın alınan", "Lazer": "Lazer kesim", "Imalat": "İmalat", "Baglanti": "Bağlantı elemanı",
          "Referans": "Gösterim"}
MODUL_AD = {"iskelet": "iskelet", "omuz_sag": "sağ omuz", "omuz_sol": "sol omuz", "kabuk": "kabuk", "dirsek_sag": "sağ dirsek",
            "dirsek_sol": "sol dirsek", "kafa": "kafa", "taban": "taban"}


def _buyuk(s):
    return ("İ" if s[0] == "i" else "I" if s[0] == "ı" else s[0].upper()) + s[1:]


def _kelime(w):
    if w in TR:
        return TR[w]
    k = w.lower()
    v = TR_EK.get(k) or TR.get(k)
    if v is None:
        return w
    if w == k:
        return v
    if w[0].isupper() and w[1:] == w[1:].lower():
        return _buyuk(v)
    return w


def kopya_eki_sil(ad, kod=""):
    """D-6 (F7c): FreeCAD aynı etiketi ikinci kez verince sondaki sayıyı atıp 3 haneli ek koyar ("... M3x8" -> "... M3x001",
    "... M4" -> "... M001"). Görünen ad için ek atılır; ekle birlikte düşen ölçü parçanın kodundan geri yazılır (kod "M3x8 DIN 912" ->
    "M3x8"). Kimlik, kod ve sayım değişmez; yalnız görünen ad (tıklama etiketi)."""
    import re
    m = re.match(r"^(.*\D)0\d\d$", ad or "")
    if not m:
        return ad
    a = m.group(1)
    k = re.match(r"(M\d+(?:,\d+)?)(?:x(\d+(?:,\d+)?))?\b", kod or "")
    if k and k.group(2) and a.endswith(k.group(1) + "x"):
        a += k.group(2)
    elif k and re.search(r"\bM$", a):
        a += k.group(1)[1:]
    return a


def tr(s):
    """CAD'den gelen ASCII metni ekranda Türkçe göster (parça adı, kod, malzeme, kablo adı). Kimlik ve sayım bundan etkilenmez."""
    import re
    if not s:
        return s
    for a, b in TR_IFADE:
        s = re.sub(a, b, s)
    return re.sub(r"[A-Za-z]+", lambda m: _kelime(m.group(0)), s)


# Taban kablo yolu şemalarının görünen adı (CAD etiketi taban_parcalar.py'de; tarama kaynağı olduğu için orada değiştirilmedi).
# no -> (beklenen CAD etiketi başı, görünen ad). Etiket başı tutmazsa tr(CAD etiketi) gösterilir ve rehber_veri.py uyarı yazar.
KABLO_AD = {
    1: ("12 V ana hat", "12 V ana hat: akü + → XT60 → ana sigorta 30 A → ana anahtar → sigorta kutusu"),
    2: ("Toprak", "Toprak: akü − → WAGO yıldız noktası (güç paneli) → tüm dönüştürücüler"),
    3: ("Motor 12 V: F1", "Motor 12 V: F1 20 A → röle → WAGO → BTS7960 sol / sağ → motor kablo delikleri → 4 motor"),
    4: ("Motor 12 V sag", "Motor 12 V sağ kol + arka motorlar (plaka altından, z 36 deliğinden)"),
    5: ("Servo 6 V A", "Servo 6 V A (E1): röle → WAGO → 7,5 A hat sigortası → XL4016 A (0; 170) → 16 AWG → dağıtım A (72; 205) → uzatmalar: sağ kol"),
    6: ("Servo uzatmalari kafaya", "Servo uzatmaları kafaya: pan + tilt (hat C, XL4016 C güç panelinde; direk üstü, R62 halkasından)"),
    7: ("Servo 6 V B", "Servo 6 V B (E1): röle → WAGO → 7,5 A hat sigortası → XL4016 B (−49; 75) → 16 AWG → dağıtım B (−72; 205) → sol kol"),
    # F7a P7.2 madde 4: CAD adı "kafada 5 V/5,5 A cevirici (Pi 5, LCD)" eski (LCD kalktı; kafada iki 5 V hattı: elektrik.md kafa güç mimarisi)
    8: ("Kafa 12 V", "Kafa 12 V (K4 / E4): F3 5 A → 18 AWG çift → direk ön yüzü → R62 → boyun → kafa girişi → Pololu D24V50F5 "
                     "(Pi 5; PAM8403 varsayım, K10) + SY8205 (10,1\" QLED)"),
    9: ("Cevre 5 V", "Çevre 5 V: F4 5 A → XL4016 çevre → ESP32 / sensörler / PCA ve BNO 3V3 (ESP32 regülatöründen)"),
    10: ("Acil stop", "Acil stop (E3): F5 → mantar (NC) → röle bobini → MOSFET (arayüz kartı, ESP32 \"devreye al\"); PC817 mantar sonrası gerilimi okur"),
    11: ("Sinyal: sonar", "Sinyal: sonar ×3 → arayüz kartı bölücü (4,7k / 10k) → ESP32 (ön ara ray üstünden)"),
    # 05.11 B kararı: ESP32 USB hub'dan, direk arka yüzünden (kablo_yolu_ekran.py "ESP32 USB"); bu şemanın geometrisi CAD'de eski yol
    12: ("Sinyal: enkoder", "Sinyal: enkoder + BTS PWM / EN / IS → ESP32. Şemanın direkten kafaya çıkan kısmı eski (05.11 öncesi "
                            "ESP32 → kafa USB); ESP32 USB artık hub'dan: \"ESP32 USB\" şeması"),
}


def kablo_ad(cad_ad):
    """Taban kablo şeması için görünen ad: (ad, uyarı ya da None)."""
    import re
    m = re.match(r"Kablo yolu (\d+): (.*)$", cad_ad)
    if not m or int(m.group(1)) not in KABLO_AD:
        return tr(cad_ad), None
    bas, ad = KABLO_AD[int(m.group(1))]
    if not m.group(2).startswith(bas):
        return tr(cad_ad), "KABLO_AD %s: CAD etiketi beklenenle tutmuyor: %s" % (m.group(1), cad_ad)
    return "Kablo yolu %s: %s" % (m.group(1), ad), None


# Gösterim şemaları: lale158/kablo_yolu_ekran.py yolları (global, ev pozu; kafa_ici_qled tilt ekseni çerçevesinde, rehber_veri.py
# çevirir). Parça değil: rehber-veri.json "semalar"; parça sayısı ve kontrol.json parça denetimi bundan etkilenmez.
# (kaynak işlev, kaynak ad, adım kodu, görünen ad, renk)
SEMA = [
    ("yollar", "HDMI", "K2", "Göğüs ekranı HDMI: Pi micro HDMI 1 → boyun → travers arkası → direk solu → ekran (F3'te takılır)", "#6c5ce7"),
    ("yollar", "Hub uzatmasi", "K2", "Hub uzatması (USB): Pi USB 3 → boyun → travers arkası → üst arka kapak içi hub (F5)", "#00a3a3"),
    ("yollar", "ESP32 USB", "K2", "ESP32 USB: hub (Hub 2) → direk arka yüzü → ESP32 (taban); VBUS'ta seri 1N5819: anot hub (Pi) tarafında, katot ESP32 "
     "tarafında; kartın kendi diyodu varsa gerekmez, multimetreyle bak (doğrulanmadı)", "#00a3a3"),
    ("yollar", "Hoparlor", "K2", "Hoparlör: PAM8403 → boyun → travers arkası → sağ ön → hoparlör (F2'de bağlanır)", "#e84393"),
    ("yollar", "12 V", "K2", "Göğüs ekranı 12 V: güç paneli (mini 2 A → LM2577 + LM2596) → direk arka yüzü → direk solu → ekran; "
                           "boyundan geçmez", "#d63031"),
    ("yollar", "USB dokunmatik", "F3", "Göğüs dokunmatiği (USB): ekran TOUCH → hub (Hub 1); F5'te hub'a takılır", "#00a3a3"),
    ("yollar", "Dizi USB", "E4", "ReSpeaker USB: Pi USB 1 → ReSpeaker (kısa micro USB)", "#00a3a3"),
    ("yollar", "Ses karti uzatmasi", "E4", "Ses kartı uzatması: Pi USB 2 → L dirsek → USB ses kartı", "#00a3a3"),
    ("yollar", "3,5 mm -> PAM", "E4", "Ses: ses kartı L 3,5 mm → PAM8403 girişi", "#e84393"),
    ("yollar", "PAM 5 V", "E4", "PAM8403 5 V: D24V50F5 → PAM (besleme noktası varsayım, K10)", "#2f86d4"),
    ("kafa_ici_qled", "HDMI (serit, 2 lehimsiz fis)", "E4", "Kafa ekranı HDMI (30 cm şerit): Pi micro HDMI 0 → QLED", "#6c5ce7"),
    ("kafa_ici_qled", "Touch USB (kutu kablosu)", "E4", "Kafa ekranı Touch: Pi USB 4 → QLED (VBUS uyarısı: Notlar)", "#00a3a3"),
    ("kafa_ici_qled", "Power USB (30 cm, A ucu kesik)", "E4", "Kafa ekranı Power: SY8205 → QLED (ayrı 5 V hattı)", "#2f86d4"),
]
