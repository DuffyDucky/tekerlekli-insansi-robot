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
#   sira    : adım içi sıra grupları (F10c; sira_grup_bul): panel satırları, sıralı takma ve rehber_sira.py denetimi bu sırayı izler
#   poz     : bağlantı ancak bu kol pozunda erişilir, ör. dict(S1=-45, S2=90) (F10c; rehber_sira.py POZA_BAGLI ölçer)

# F10d düzeltme 1 (kontrol B-5): "yön yuvarlama" uçuş istisnaları (12) kaldırıldı. Ölçüm aracı (rehber_sira.py ucus_yolu) artık
# uygulamanın uçurduğu yuvarlanmamış eksende süpürüyor; bu satırlar gerçek eksende serbest.

# F10d: perdelenme istisnası. 3 mm voksel ince / küçük parçayı (köpük bant, M3×6 başı) komşu bandın hücresine katıyor; kimlik tamponu
# ölçümü (planlama/d158/F10d-gizli-piksel.json, F10d-dogrula.py --gizli) parçanın gerçekte göründüğünü gösteriyor
# F10d düzeltme 1 (kontrol B-7): eski metin piksel sayısını ve başka kamerayı yazıyordu (eşik > 0, alt adım dışı kamera kabul
# ediliyordu). Artık bütün yeni parçalar kendi alt adım karesinde görünürlük ölçütünü geçiyor (≥ 30 piksel ve ≥ %20; F10d-dogrula
# görünürlük); güncel sayılar planlama/d158/F10d-gizli-piksel.json'da. Argümanlar eski çağrılarla uyum için, metne girmez.
def voksel_ok(px=None, kamera=None):
    return ("perdelenme (3 mm voksel, 26 yön) tamamen gizli sayıyor; kimlik tamponu ölçümünde alt adım karesinde görünür "
            "(≥ 30 piksel ve tek başına çizilişinin ≥ %20'si; F10d-gizli-piksel.json): voksel çözünürlüğü, gerçek örtülme değil")


# F10f düzeltme turu 1 (kontrol F10f-K1): F10f'teki geniş istisna (ad parçası, alt adımın bütün eşleşen parçaları, bütün engeller)
# daraltıldı. Anahtar parça kimliği (o alt adımda o parça); "engel" yolun tamamında çarptığı her parça ve en büyük ortak hacim derinliği
# (ölçülen + 0,5 mm pay = ışın aralığı h). Başka engel ya da daha derin çarpışma istisna sayılmaz (rehber_sira.ucus_yolu). İki sınıf:
#   duruş: rehber kolu modeldeki duruşta (S1 0°, S2 0°) ve düz tek yol çizer; tasarım parçayı başka duruşta / iki parçalı yolla takar,
#          o yol rehberin kendi ölçümüyle temiz (planlama/d158/F10f-gunluk.md, Düzeltme turu 1, F10f-K1)
#   karar: tasarım / montaj sırası kalemi, sıra ve parça ↔ adım ataması bu pakette değişmez (karar kuyruğu; günlükte seçenekli not)
# Pay: PAY_MM. Değerler F10f düzeltme turu 1 ölçümü (veri kopyasında rehber_sira.ucus_yolu, tum süpürme).
PAY_MM = 0.5


# F10f düzeltme 2 (kontrol F10f-kontrol-2 3.1, M8): iki sınıf daha.
#   yol:         F10d'nin giriş yolu ölçümüyle "düz yol yok" gerekçeli istisnası, kol adımında (36) eski tür dize anahtardan dar anahtara
#   ölçüm kaydı: duruşta örtüşen çift artık yol boyunca denetleniyor (rehber_sira.DINLENME_PAY); kol dışı adımlarda bununla ilk kez
#                çıkan satırlar düzeltilmedi (kapsam dışı), dar anahtarla kayıtta (kontrol.json sira.ucus.olcum_kaydi)
SINIF_ONEK = {"duruş": "gerekçeli duruş", "karar": "karar bekliyor (karar kuyruğu)", "yol": "gerekçeli: düz yol yok (F10d giriş yolu ölçümü)",
              "ölçüm kaydı": "ölçüm kaydı: F10f düzeltme 2'de ilk kez ölçüldü, ayrı iş"}


def dar(sinif, gerekce, **engel):
    """Dar uçuş istisnası: engel = {engel parça id: ölçülen en büyük derinlik mm}; pay eklenir."""
    return dict(sinif=sinif, gerekce="%s: %s" % (SINIF_ONEK[sinif], gerekce), engel={k: round(v + PAY_MM, 2) for k, v in engel.items()})


# K56 / K57 (Ahmet, 13.11.2026; planlama/d158/karar-kuyrugu.md, F10g-gunluk.md): F10f'in iki "karar" sınıfı dar istisnası (40.1 kol
# çatalı, 44.1 dirsek çatalı) kalktı. K56 C: 625ZZ tezgâhta kol çatalına preslenir (iki bilezik çatalla gelir), mafsal pulu + mafsal
# cıvatası G3'te çataldan sonra. K57 a: dirsek horn merkez vidası H0c'de, dirsek çatalından sonra. Atama rehber_secici.py'de.
POZ_KAPAK = ("rehber kapağı modeldeki duruşta (S1 0°, S2 0°) düz tek yolla (önden, +z) son yerine getirir; flanşı gövdenin içinden "
             "geçer. Tasarım kapağı önden, flanşı gövdeden x +3,3 mm havada getirir, sonra −x iter (S1-kaset.md K5 adım 7; S2 ≥ 30°). Bu "
             "iki parçalı yol rehberin uçuş yolu ölçümüyle S2 30°'de (S1 0° ve −45°) temiz; S2 0°'de itmede kol çatalına değiyor")
POZ_CIV = ("rehber ψ 200 dikme cıvatasını modeldeki duruşta (S1 0°, S2 0°) çizer; orada yolunda kol çatalı ve üst kol tüpü var. "
           "Tasarım bu cıvatayı S1 −45° / S2 90°'de sıkar (S1-kaset.md K5 adım 8, anahtar erişimi ≥ 8 mm); rehberin uçuş yolu ölçümüyle "
           "S1 −45° / −20° / 0° × S2 90°'de yol temiz")


def gizli(neden):
    return ("perdelenme (26 yön, dik izdüşüm): parça yerindeyken hiçbir yönden görünmez; " + neden + ". Okur onu sıralı takmada "
            "(Boşluk) yerine giderken görür; alt adım karesindeki piksel ölçümü F10f-gunluk.md Düzeltme turu 1")


# F10d düzeltme 1 (kontrol B-1): kabuk alt adımlarında her yeni parça kendi karesinde görünmeli (F10d-dogrula.py görünürlük ölçütü:
# ≥ 30 piksel ve tek başına çizilişinin ≥ %20'si). Isıl gömme bandın boss'unun, dikiş cıvatası bindirmenin, arka dikiş öndeki
# bantların arkasında kalır: o alt adımda bantlar saydam çizilir (saydam = desen; önceki parçalar 0,25, yeni parça 0,4 opaklık).
# Kamera ve saydam seçimi kamera × saydam taramasından (planlama/d158/F10d-gunluk.md bölüm 11).
GOVDE_BANT = ("Gövde alt bandı", "Gövde uzatma bandı", "Gövde orta bandı", "Göğüs bandı", "Omuz bandı")
ETEK_BANT = ("Etek arka", "Etek orta", "Etek ön", "Etek dolgu")
KAFA_KABUK = ("Arka kafa kabuğu", "Yüz kabuğu")


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
                 "BTS7960B ve XL4016 klemens uçları bağlandı, vidaları sıkı; boştaki uçlar etiketli ve bantlı (K1'de bağlanır)",
                 "Kartlar takılmadan tezgâhta (bu adımdan önce): XL4016 A / B 6 V, çevre 5 V'a ayarlandı; akım sınırlı tezgâh kaynağıyla "
                 "12 V giriş, yüksüz, çıkış ölçülerek (K1 kontrolü). PC817 ölçümü de arayüz kartı takılmadan tezgâhta (B6a). Takıldıktan sonra "
                 "ayar vidasına erişim ölçülmedi; bu sıra kaynakta yok, doğrulanmadı"],
        kablo=["Alt kat klemensleri bu adımda bağlanır, üstü açıkken: iki BTS7960B'nin güç girişi ve motor çıkışı (motor uçları B2b'de "
               "plaka üstüne alındı), üç XL4016 kartının (A, B, çevre) giriş ve çıkışı. Güç paneli ve elektronik katı gelince (B5, B6) bu klemenslere el "
               "dar kalır: kart üstünden kata 69 mm, yanda 40–150 mm (K1 erişim notu). Akü ayrık",
               "Öbür ucu henüz yerinde olmayan hat (bara, sigorta kutusu, hat sigortası; K1'de bağlanır): iki ucundan etiketle (kart, "
               "klemens, hat adı), K1'deki yerine yetecek boyda bırak, ucu bantla; hatları kablo bağıyla demetleyip plaka üstünde topla, "
               "kat burçlarının (B4) ve kart üstlerinin yolunu kapatmasın. Bu sıra ve toplama yeri kaynakta yok, doğrulanmadı",
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
        not_=["Bilinen açık konu (K53, karar bekliyor): modelde elektronik katı inerken ön şarj kartının iki ön naylon burcuna "
              "takılıyor; burç katın ön kenarından 0,425 mm taşıyor (`planlama/d158/F10b-olcum.json`). Çözüm seçilmedi (K53 karar bekliyor; "
              "seçenekleri F10b'de ölçüldü, `planlama/d158/F10b-gunluk.md`)"],
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
            "(F1'de etek plakasının altına takılır): ana anahtara gidecek iki uç bırakılır, F1'de bağlanır. Şarj girişi: akü + hattından, "
            "ana anahtardan önce, kapaklı mini sigorta yuvası (şarj 10 A) → XT60 şarj girişi ucu (`planlama/adim3/elektrik.md` sigorta "
            "listesi). Kolu akü XT60'ının robot tarafından, ana hattan al: akü XT60'tan ayrılınca kol da enerjisiz kalır (rehberdeki "
            "\"akü ayrık = enerjisiz\" düzeni buna dayanır). Kaynak yalnız \"akü +, ana anahtar öncesi\" diyor; XT60'ın hangi tarafı "
            "olduğu doğrulanmadı. Şarj girişinin − ucunun bağlanacağı nokta ve kutup işareti kaynakta yok, doğrulanmadı (genel toprak: akü − "
            "→ WAGO yıldız noktası, `planlama/adim3/elektrik.md` blok şema). Uç bantlı bırakılır, F1'de etekteki şarj girişine bağlanır; "
            "sigortası takılmaz (F1 aşama 1). Ana sigortadan önce mi sonra mı bağlanacağı kaynakta yok, doğrulanmadı. Kablo kesiti "
            "`planlama/adim3/elektrik.md`'de yok; sigorta yuvası 16AWG kuyruklu (`planlama/maliyet.json` hat sigortası yuvası), doğrulanmadı.\n"
            "2. F1 20 A → röle K1 → anahtarlı bara. Baradan: iki BTS7960B; hat sigortasıyla XL4016 A ve B (7,5 A), C (5 A).\n"
            "3. F3 kafa hattı (uç direk dibinde bırakılır), F4 XL4016 çevre 5 V, F5 acil stop hattı.\n"
            "Alt kat kartlarının (iki BTS7960B, XL4016 A / B / çevre) klemens uçları B3'te, kat ve güç paneli gelmeden bağlandı: burada "
            "yalnız B3'te etiketli bırakılan öbür uçları bara, sigorta kutusu ve hat sigortalarına bağla. Alt kat klemensine burada uzanma: "
            "kart üstünden elektronik katına 69 mm, yanda 40–150 mm (sıra kontrolü).\n"
            "4. Enkoder ve sonarları bağla (motor uçları B3'te BTS7960B'ye bağlandı). Acil stop ucunu bırak: mantar F1'de takılır.\n"
            "5. Direğe çıkacak hatların taban kısmını da burada bağla (servo A / B / kafa, kafa 12 V, ESP32 USB). Yukarısı K2'de.\n"
            "6. K1'de enerji verilmez: ana anahtar ve acil stop mantarı F1'de takılır. Mantar ve ana anahtar uçları hiçbir zaman "
            "köprülenmez; akü XT60 ayrık kalır, boştaki ana hat uçları gerilimsiz ve bantlı. XL4016 ayarı ve PC817 ölçümü kartlar takılmadan "
            "önce tezgâhta, akım sınırlı tezgâh kaynağıyla yapılır (kontrol; B3, B5a, B6a). İlk enerji iki aşamalı: F1 sonunda kafasız "
            "(aşama 1: ana anahtar, BMS, mantar; F1 takılı değil, anahtarlı bara enerjisiz), devreye alma ve motor yön testi F5'te (aşama 2). "
            "Bu sıra kaynakta yok, doğrulanmadı.",
        baglanti_md="Klemens, kablo pabucu, kablo bağı (adet: kablo listesi henüz yazılmadı)",
        alet="Multimetre, kablo soyucu, pabuç pensesi, tornavida",
        erisim="Kabuk yok. Kat üstü açık (dağıtım kartları, ESP32, arayüz kartı, XL4016 C, sigorta kutusu: el bölgesine uzaklık 6–9 mm, el yakına ulaşıyor). Alt kat "
               "kartlarının klemenslerine el dar: kart üstünden elektronik katına 69 mm, yanda raylara ve komşu karta 40–150 mm "
               "(sıra kontrolü 10.11, 11.11'de yeniden ölçüldü; ışınla, klemens yerleri modelde yok); o uçlar B3'te bağlanır",
        kontrol=[
            "Akü ayrıkken multimetre: artı ile eksi arasında kısa devre yok",
            "B3'te bağlanan alt kat uçlarının etiketleri okunuyor; her biri K1'de öbür ucuna bağlandı, boşta uç kalmadı",
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
        # F10d: horn S1 ekseninde (x) ince disk, rulman kapağının (adım 20) arkasında: servo ekseni boyunca 6808'in deliğinden girer
        # (F10c'ye kadar +y'den uçuyordu). İki yan aynı kareden görünmüyor (iki omuz x ekseninde birbirini örter): sağ / sol alt adım,
        # kapak ve rulman saydam.
        ucus=(1, 0, 0),
        alt=True,
        sira=[dict(ad="Sağ omuz: horn + merkez vidası", yan="sag", desen=("S1 horn",), kamera=(1.0, 0.35, 0.45),
                   saydam=("Rulman kapağı", "6808-2RS rulman"),
                   is_="Sağ omuz: hornu S1 milinin dişlisine rulman kapağının deliğinden geçir, merkez vidası M3×5 (PH1)."),
              dict(ad="Sol omuz: horn + merkez vidası", yan="sol", desen=("S1 horn",), kamera=(-1.0, 0.35, 0.45),
                   saydam=("Rulman kapağı", "6808-2RS rulman"),
                   is_="Sol omuz: aynı iş, aynalı.")],
    ),
    "D1": dict(
        baslik="Omuz gövdesi → travers",
        # F10d düzeltme 1 (kontrol B-12): "travers ucundan kaydırarak sok" ölçülmemişti; ölçülene indirildi
        is_="Çekiç somunları kanala al, omuz gövdesini travers ucuna oturt (giriş yolu ölçülmedi), cıvataları sık. İki omuz da aynı.",
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
        # F10d: horn rulman yuvasının (adım 23) içinde, 6808 deliğinin altında: yukarıdan bakış, yuva ve rulman saydam (kamera tam +y
        # değil: kamera.up +y ile çakışmasın)
        kamera=(0.35, 1.0, 0.45),
        saydam=("Rulman yuvası", "6808-2RS alt rulman", "Servo yuvası"),
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
        # F10c düzeltme 1: tasarımın montaj sırası (tasarim/freecad/kafa/kafa_rapor.py SIRA 5-6): horn burada servoya, vidasız; 625ZZ
        # E3a'da kafa yanağına, pim + pul ve horn merkez vidası E3'te (kafa ancak böyle iner; planlama/d158/F10c-gunluk.md).
        is_="1. Tilt servosunu +X'ten çatalın U kulak plakasına cıvatala (4 × M4×16 + kontra somun).\n"
            "2. Tilt hornunu (25T alüminyum disk) servo orta konumdayken servo miline geçir. Merkez vidasını şimdi takma: kafa E3'te "
            "horna indikten sonra sağ yanağın orta deliğinden takılır (vida burada takılırsa inen kafa iskeleti vida başına "
            "takılıyor, ölçüldü). Orta komutun nasıl verileceği kaynakta yok (doğrulanmadı); kalan ofset yazılımda düzeltilir (Y2).\n"
            "625ZZ ve M5 pim bu adımda yok: 625ZZ E3a'da kafanın sol yanağına, pim + pul E3'te (`tasarim/freecad/kafa/kafa_rapor.py` "
            "montaj sırası).",
        baglanti_md="4 × M4×16 + 4 kontra somun; horn milde, merkez vidası E3'te",
        alet="alyan 3, 7 mm anahtar (kontra somun)",   # F10d: M6'daki "alyan 3 / 4"ün 4'ü pim içindi, pim E3'te (adım 30)
        erisim="Düz. Kontra somunların 2'si cepte, 2'si açık ağızla (Y3 C3)",
        kontrol=["Tilt elle engelsiz", "Horn servo milinde, servo orta konumda; merkez vidası takılmadı (E3'te)"],
        # F10d: servo, mil ve horn servo ekseni (x) boyunca gelir (giriş yolu ölçümü: horn yalnız +x'ten serbest; F10c'ye kadar
        # horn ve mil (0,75, 0, 0,66) yönünden uçuyordu, milin içinden geçiyordu)
        ucus=(1, 0, 0),
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
            "3. 625ZZ rulmanını sol yanağın yuvasına pres et (tek parça; modelde iç ve dış bilezik ayrı çizili). Tilt hornu bu adımda "
            "yok: E2'de servoya takıldı, kafa E3'te ona iner (`tasarim/freecad/kafa/kafa_rapor.py` montaj sırası).\n"
            "Kafa ekranı (10,1\" QLED), tırnaklar, kamera, ReSpeaker, USB ses kartı ve PAM8403 bu adımda takılmaz: kabuklarla birlikte E4'te.",
        baglanti_md="Pi: 4 × M2,5×8 pirinç burç + 4 × M2,5×5 (üst) + 4 × M2,5×8 DIN 912 (alt); D24V50F5, SY8205, TVS: 1 mm çift taraflı "
                    "köpük bant + kablo bağı; 625ZZ pres geçme. M6'daki LCD 4 × M3×6 ve kamera 4 × M2×8 PT bu adımda yok (QLED tırnaklı, kamera E4'te)",
        alet="alyan 2, yan keski",          # F10d: PH1 horn merkez vidası içindi, vida E3'te (adım 30)
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
        is_="Kabuklardan önce: sonra cıvatalar kafa içinde kalır. Sıra `tasarim/freecad/kafa/kafa_rapor.py` montaj tarifinden.\n"
            "1. Kafa alt montajını yukarıdan indir: yanaklar eğme çatalının iki yanından geçer; sol yanaktaki 625ZZ'nin iç bileziği "
            "çatal dayamasına, sağ yanak hornun dış yüzüne oturur. Kafa düz yukarıdan girer (giriş yolu ölçümü: +y serbest; düz "
            "önden +z ve düz arkadan −z de serbest, çapraz ya da kaydırmalı yol ölçülmedi); "
            "horn kafadaysa yukarıdan girmez (giriş yolu ölçümü, sıra denetimi; ölçülen durum: horn kafada, 625ZZ iç bileziği, pim ve "
            "pul E2'de).\n"
            "2. Horn merkez vidası M3×5: sağ yanağın orta deliğinden, PH1.\n"
            "3. Sağ yanağı horna 4 × M3×8 ile cıvatala.\n"
            "4. Pulu M5×12 pime geçir; pimi sol yanağın deliğinden 625ZZ'nin iç bileziğinden geçirip çataldaki M5 ısıl gömmeye sık, "
            "alyan 4. 2 ile 3'ün sırası kaynakta yok (montaj mantığından).",
        baglanti_md="4 × M3×8 yanak–horn; 1 × M3×5 horn merkez vidası (servo ile); 1 × M5×12 + DIN 125 pul (pim)",
        alet="alyan 2,5 ve 4, PH1",
        erisim="Kafa düz yukarıdan iner (giriş yolu ölçümü). Pim sol yanak dışından düz alyan 4 ile (alet yolu 130 mm boş), horn "
               "vidası sağ yanak deliğinden PH1 ile (80 mm boş), yanak-horn cıvataları düz (sıra denetimi, 20 mm el)",
        kontrol=["Kafa tilt ekseninde serbest; Pi kablolarına yük binmiyor", "Pim sıkıyken 625ZZ dönüyor, tilt elle engelsiz",
                 "Horn merkez vidası sıkı"],
        not_=["Bilinen açık konu: yanakların arası 54,4 mm, aradaki yığın (çatal dayaması + servo + horn) da 54,4 mm: kafa iki yanda "
              "sıfır boşlukla iner (modelde ortak hacim 0, yüzler temas ediyor). Baskı toleransında zorlamasız iniş ölçülmedi"],
        # F10c düzeltme 1: sıralı takma metindeki 2-3-4 sırasını izlesin (kafa adımın başında, bağlanan alt montaj olarak iner)
        sira=[dict(ad="Horn merkez vidası", desen=("Tilt horn merkez vidası",)),
              dict(ad="Yanak → horn cıvataları", desen=("Yanak-horn",)),
              dict(ad="Pul + pim (sol yanak)", desen=("Pim pulu", "Pim cıvatası"))],
        ucus_bag=(0, 1, 0),
    ),
    "E4": dict(
        baslik="Kafa kabukları + yüz ekranı, kamera, ses",
        # kafa10_lib.py: QLED vida deliksiz, 4 tırnak (x ±85, üst / alt) M3×6 ISO 7380 + ısıl gömme, 1 mm köpük bant; kamera yüz kabuğu
        # boss'larına 4 × M2×8 PT; ReSpeaker sağ arka kabuk tavan boss'larına 3 × M2×8 PT; ses kartı + PAM8403 sol arka kabuk yan duvarı.
        is_="Kafa robotta, tilt hornunda (E3). Sıra: sağ arka kabuk → sol arka kabuk → tabla cıvataları → yüz kabuğu → kablolar → "
            "dikişler. Yüz kabuğu önce takılırsa tabla cıvatalarına alet sığar ama el kafanın dışından ulaşamaz (sıra denetimi, "
            "`rehber_sira.py`). Kaynakta sıra yok, montaj mantığından ve ölçümden: doğrulanmadı.\n"
            "1. Masada, sağ arka kabuk: ReSpeaker Mic Array v2.0'ı kabuğun tavanındaki boss'lara 3 × M2×8 PT ile vidala (kabuk "
            "kafadayken tavan vidalarına el ulaşmaz). Masada, sol arka kabuk: USB ses kartı ve PAM8403 yan duvara köpük bant + kablo "
            "bağıyla. Kabukları kafanın arkasında tut, kabloları kafanın açık ön tarafından tak: ReSpeaker → Pi USB 1, ses kartı → "
            "Pi USB 2 (uzatma + L dirsek), ses kartı L 3,5 mm → PAM girişi, PAM 5 V → D24V50F5 (varsayım, K10). Önce sağ kabuğu "
            "arkadan (−z) yerine koy, sonra solu (arkadan ya da soldan): dikey dikişte sağ kabuğun bindirmesi solun altında kalır; sol "
            "önce takılırsa sağ hiçbir düz yönden girmiyor (giriş yolu ölçümü).\n"
            "2. Tabla → arka kabuk rafı 4 × M3×10: yüz tarafı açıkken önden, L alyanla.\n"
            "3. Masada, yüz kabuğu sağ + sol: kamerayı (Camera Module 3) ön duvarın içindeki boss'lara 4 × M2×8 PT ile vidala; lens ekranın "
            "üstündeki Ø9 delikte. 10,1\" QLED (vida deliği yok): camı yüz kabuğu ön duvarının iç yüzüne yasla, cep duvarı yerini gösterir. "
            "4 tırnağı (üst ve alt, x ±85) cam şeridine 1 mm köpük bant üstünden arkadan bastır; her tırnak 1 × M3×6 ISO 7380 ile boss'taki "
            "ısıl gömmeye.\n"
            "4. Yüz kabuğunu kafanın önünde tut, kabloları tak: CSI şeridi → Pi; QLED HDMI (30 cm şerit, Pi micro HDMI 0), Power (SY8205 "
            "çıkışı, A ucu kesik micro USB kablo), Touch (Pi USB 4). Touch'ı takmadan önce Notlar'daki ölçümü yap. Sonra yüz kabuğunu önden (+z) yerine koy (giriş yolu: önden serbest).\n"
            "5. Dikişler: boyundan gelen uçlar (kafa 12 V, göğüs HDMI, hub uzatması, hoparlör) K2'de bağlanır: arka kabuğun dikiş "
            "cıvatalarını K2'den sonra sık.",
        baglanti_md="1,58 m: tırnak 4 × M3×6 ISO 7380 → ısıl gömme + 4 köpük bant (1 mm); kamera 4 × M2×8 PT; ReSpeaker 3 × M2×8 PT (vida "
                    "tipi varsayım); ses kartı ve PAM8403 köpük bant + kablo bağı; tabla → arka kabuk rafı 4 × M3×10 DIN 912 → ısıl gömme; "
                    "kabuk dikişi 9 cıvata → ısıl gömme: 7 × M3×6 ISO 7380 + 2 × M3×5 ISO 7380 (havşalı tepe dikişi). M6'daki M3×8 + vizör "
                    "eski, BOM'da vizör yok",
        alet="alyan 2 / 2,5, PH0 / PH1 (M2 PT vidalar), yan keski",
        erisim="Tabla cıvataları: L alyanla önden, yüz tarafı açıkken (alet yolu 63,5 mm boş; 4/4 ulaşılır, el payı 12, 15 ve 20 mm'de). "
               "Eski sırada (yüz kabuğu önce) 20 mm el payında 4/4 kapalı; 15 mm ve altında eski sıra da açık görünüyor, fark 20 mm "
               "el varsayımına dayanıyor. ReSpeaker, kamera ve tırnak vidaları masada, kabuk açıkken düz; "
               "dikiş cıvataları dışarıdan düz (sıra denetimi). Giriş yolu: sağ arka kabuk arkadan, sol arka kabuk arkadan ya da "
               "soldan, yüz grubu önden serbest (temas eden yüzler çarpışma sayılmadı). Servis arka kabuktan (125 cm notu; 1,58 m'de doğrulanmadı)",
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
        # F10c (P10.3): sıra denetimiyle seçildi (planlama/d158/F10c-gunluk.md E4 tablosu). Masa grupları kafaya takılmadan hazırlanır.
        # F10c düzeltme 1: arka kabuklar iki ayrı birim (dikiş cıvataları K2'den sonra): önce sağ, sonra sol (giriş yolu ölçümü).
        # F10d: alt adımlar (sira grubu = alt adım); sıra F10c'deki gibi: sağ arka → sol arka → tabla cıvataları → yüz grubu → kablolar
        # → dikişler. Masa birimleri (masa=...) bağlandıkları alt adımda (bag=...) ub yönünden gelir.
        alt=True,
        sira=[dict(ad="Masada: sağ arka kabuk + ReSpeaker", masa="arka_sag", desen=("Arka kafa kabuğu sağ", "ReSpeaker", "Dizi vidası"),
                   ucus={"ReSpeaker": (0, -1, 1), "*": (0, 0, -1)}, kamera=(0.55, -0.75, 1.0), saydam=("Arka kafa kabuğu sağ",),
                   is_="Masada, sağ arka kabuk: ReSpeaker Mic Array v2.0'ı kabuğun tavanındaki boss'lara alttan 3 × M2×8 PT ile vidala "
                       "(kabuk kafadayken tavan vidalarına el ulaşmaz)."),
              dict(ad="Sağ arka kabuk → kafa", bag="arka_sag", desen=(), ucus_bag=(0, 0, -1), sema=("ReSpeaker USB",), kamera="arka",
                   is_="Kabuğu kafanın arkasında tut, ReSpeaker kablosunu kafanın açık ön tarafından Pi USB 1'e tak. Sonra sağ kabuğu "
                       "arkadan (−z) yerine koy: dikey dikişte sağ kabuğun bindirmesi solun altında kalır; sol önce takılırsa sağ hiçbir "
                       "düz yönden girmiyor (giriş yolu ölçümü)."),
              dict(ad="Masada: sol arka kabuk + USB ses kartı, PAM8403", masa="arka_sol",
                   desen=("Arka kafa kabuğu sol", "USB ses kartı", "PAM8403"), ucus={"Arka kafa kabuğu": (0, 0, -1), "*": (1, 0, 0)},
                   kamera=(-0.85, 0.62, 1.25), saydam=("Arka kafa kabuğu sol", "USB ses kartı", "PAM8403"),
                   gizli_ok={"Köpük bant (USB ses": voksel_ok(74), "Köpük bant (PAM": voksel_ok(41)},
                   is_="Masada, sol arka kabuk: USB ses kartı ve PAM8403'ü yan duvarın iç yüzüne köpük bant + kablo bağıyla tut."),
              dict(ad="Sol arka kabuk → kafa", bag="arka_sol", desen=(), ucus_bag=(0, 0, -1),
                   sema=("Ses kartı uzatması", "Ses: ses kartı", "PAM8403 5 V"), kamera=(-0.85, 0.62, -1.25),
                   is_="Kabloları kafanın açık ön tarafından tak: ses kartı → Pi USB 2 (uzatma + L dirsek), ses kartı L 3,5 mm → PAM "
                       "girişi, PAM 5 V → D24V50F5 (varsayım, K10). Sonra sol kabuğu arkadan yerine koy (giriş yolu ölçümü)."),
              dict(ad="Tabla → arka kabuk rafı cıvataları", desen=("Tabla cıvatası",), kamera=(0.3, 1.0, 0.35), saydam=("Arka kafa kabuğu",),
                   gizli_ok={"Tabla cıvatası M3x10 (sağ z-75)": voksel_ok()},
                   is_="Tabla → arka kabuk rafı 4 × M3×10: yüz tarafı açıkken önden, L alyanla (sıra denetimi: yüz kabuğu önce "
                       "takılırsa alete yer kalır ama el kafanın dışından ulaşmaz)."),
              dict(ad="Masada: yüz kabuğu + kamera", masa="yuz", desen=("Yüz kabuğu", "Kamera"),
                   ucus={"Kamera": (0, 0, -1), "*": (0, 0, 1)}, kamera=(0.6, 0.45, -1.25), saydam=("Yüz kabuğu",),
                   gizli_ok={"Kamera vidası": voksel_ok("95–97")},
                   # F10d düzeltme 1 (kontrol B-4): eski gerekçedeki "3,91 mm ortak hacim" eksen ışınının kirişiydi (K3 geri çekildi)
                   # F10f düzeltme 2 (madde 1b): duruşta örtüşen çift yol boyunca denetlenince bu satıra yüz kabuğu (ön) sağ eklendi (ışın
                   # ölçümü 7,95 mm). Kol dışı adım: düzeltilmedi; eski dize anahtar ("Kamera") aynı gerekçeyle dar anahtara, sınıf ölçüm kaydı
                   ucus_ok={"p0798": dar("ölçüm kaydı",
                                         "duruşta örtüşen çift yol boyunca denetlenince yüz kabuğu (ön) sağ [p0750] ile ışın ölçümü 7,95 mm "
                                         "(h 0,5 mm; aşağıdaki F10d nokta–üçgen ölçümü en çok 1,0 mm diyor, çelişki ölçülmedi). F10d gerekçesi: "
                                         "uçuş yolu ölçümü: −z'de 3 mm sonra ışın ölçümü kafa ön üst dikişinin ısıl gömmesinde 2,91 mm "
                                         "ortak hacim veriyor; gerçek derinlik (nokta–üçgen, yüzey örnekleri) 3–8 mm arasında yüz kabuğu "
                                         "sağ ile en çok 1,0 mm, ısıl gömmeyle 0,24 mm, 10 mm'den sonra 0. Dinlenmede kamera ile yüz kabuğu "
                                         "yalnız temas (derinlik 0). Kart boss'lara otururken kenarı kabuğa 1 mm'ye kadar sürtebilir, "
                                         "elde denenmedi", p0763=2.91, p0750=7.95)},
                   is_="Masada, yüz kabuğu sağ + sol: kamerayı (Camera Module 3) ön duvarın içindeki boss'lara 4 × M2×8 PT ile vidala; "
                       "lens ekranın üstündeki Ø9 delikte."),
              dict(ad="Masada: QLED → yüz kabuğu", masa="yuz", desen=("Yüz ekranı",), ucus={"*": (0, 0, -1)}, kamera=(0.6, 0.45, -1.25),
                   is_="10,1\" QLED (vida deliği yok): camı yüz kabuğu ön duvarının iç yüzüne arkadan yasla, cep duvarı yerini gösterir."),
              dict(ad="Masada: ekran tırnakları", masa="yuz", desen=("Köpük bant (tırnak", "Ekran tırnağı", "Tırnak cıvatası"),
                   ucus={"*": (0, 0, -1)}, kamera=(0.6, 0.45, -1.25), saydam=("Ekran tırnağı",),
                   gizli_ok={"Köpük bant (tırnak alt": voksel_ok() + "; 1 mm bant tırnağın altında, tırnak saydam çizili"},
                   is_="4 tırnağı (üst ve alt, x ±85) cam şeridine 1 mm köpük bant üstünden arkadan bastır; her tırnak 1 × M3×6 ISO 7380 "
                       "ile boss'taki ısıl gömmeye."),
              # F10e: kabuklar ve ekran saydam, yandan bakış: üç kablo şeması (HDMI, Touch, Power) Pi ile QLED arasında görünsün
              # (F10d: şemalar opak yüz kabuğunun arkasında kalıyordu). CSI şeridinin şeması yok (kablolama içeriği değişmedi).
              dict(ad="Kablolar + yüz grubu → kafa", bag="yuz", desen=(), ucus_bag=(0, 0, 1),
                   kamera=(1.0, 0.55, 0.6), saydam=KAFA_KABUK + ("Yüz ekranı",),
                   sema=("Kafa ekranı HDMI", "Kafa ekranı Touch", "Kafa ekranı Power"),
                   is_="Yüz kabuğunu kafanın önünde tut, kabloları tak: CSI şeridi → Pi; QLED HDMI (30 cm şerit, Pi micro HDMI 0), Power "
                       "(SY8205 çıkışı, A ucu kesik micro USB kablo), Touch (Pi USB 4). Touch'ı takmadan önce Notlar'daki ölçümü yap. "
                       "Sonra yüz kabuğunu önden (+z) yerine koy (giriş yolu: önden serbest)."),
              dict(ad="Kabuk dikişi", desen=("Kabuk cıvatası",), kamera=(0.85, 0.62, -1.25), saydam=KAFA_KABUK + ("Kafa iskeleti",),
                   is_="Dikiş cıvatalarını tak (9 cıvata, ısıl gömmeye). Boyundan gelen uçlar (kafa 12 V, göğüs HDMI, hub uzatması, "
                       "hoparlör) K2'de bağlanır: arka kabuğun dikiş cıvatalarını K2'den sonra sık.")],
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
            "3. Acil stop mantarını panel somunuyla tak. Bağlamadan önce mantarı multimetrenin süreklilik kademesinde dene: NC uçları "
            "arasında mantar serbestken bip var, basılıyken yok (akü ayrık; kaynakta yok, doğrulanmadı). Sonra K1'de bırakılan ucu bağla.\n"
            "4. Ana anahtar ASW-A01 gövdesini etek üst plakasının altına, acil stobun karşısına tak (model yeri öneri, ölçü tahmini zarf; "
            "bağlantı elemanı modelde yok, doğrulanmadı). K1'de bırakılan iki ana hat ucunu bağla. Düğme: delik Ø30 tahmini, anahtarı ölç.\n"
            "5. XT60 şarj girişi (panel konnektör): önerilen yer etek üst plakasının arkası, delik modelde yok "
            "(`tasarim/freecad/taban/rapor.html` şarj notu; doğrulanmadı). Delik açıldıysa konnektörü tak, K1'de bırakılan şarj ucunu akü "
            "ayrıkken bağla; açılmadıysa uç bantlı kalır. Şarj 10 A sigortası takılmaz (aşama 1 listesi).",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; braket 6 × M3×14 ISO 7380 dışarıdan + M3 perçin somun (Y3 K2). M6'daki içeriden M3×8 eski",
        alet="alyan 2 (acil stop için ayrıca anahtar)",
        erisim="Düz, dışarıdan",
        kontrol=["Acil stop NP2 BE102: CAD 60 mm; delik gerçek parçayla tutuyor mu bak",
                 "İlk enerji, aşama 1 (F1 sonu, kafasız): ana anahtar ve mantar bağlı. Saat, yüzük, bileklik çıkar "
                 "(`planlama/d158/testler/00-genel.md` kural 8). Akü XT60 ayrık, ana anahtar kapalıyken ana sigortayı (30 A), F4 (5 A, XL4016 "
                 "çevre 5 V: ESP32) ve F5 (2 A, acil stop: mantar, röle bobinleri) tak. F1 (20 A: röle K1 ve ön şarj kolu K2), F3 (5 A, kafa), "
                 "XL4016 hat sigortaları (A 7,5 A, B 7,5 A, C 5 A), göğüs ekranı mini 2 A ve şarj girişi mini 10 A takılı değil "
                 "(`planlama/adim3/elektrik.md` sigorta listesi): anahtarlı bara, kafa ve göğüs ekranı dalı enerjisiz, Pi enerjisiz. Şarj girişi "
                 "ana anahtardan önce akü + hattında: sigortası takılı olsaydı ana anahtar kapalıyken de gerilimli olurdu. Devreye alma komutu Pi'den gelir (E3). ESP32'deki "
                 "program bilinmiyor: K2'yi süren GPIO2 kartın LED pini (E9), LED yakıp söndüren hazır bir program K2'yi açıp kapatabilir. F1 "
                 "takılı olmadığı için röle K1 ve K2'nin kontakları enerjisiz, anahtarlı bara enerjisiz kalır. Tekerlekler yerden kesik (şasi "
                 "takozda, `planlama/d158/testler/T13-rampada-acil-stop.md`); BTS EN = 0. Mantar ölçümü: akü ayrıkken multimetreyi DC V "
                 "kademesine al (20 V aralığı ya da otomatik; akü en çok 14,6 V), kırmızı ucu V soketine tak: 10 A soketinde kalırsa multimetre "
                 "bu noktayı GND'ye bağlar ve F5 2 A atar (`planlama/d158/testler/00-genel.md` multimetre kuralı). Kırmızı ucu arayüz kartındaki "
                 "PC817 #1 giriş klemensinin + ucuna (mantar sonrası düğüm, E3), siyah ucunu güç panelindeki WAGO GND yıldız noktasına "
                 "bağla. Ölçü kıskacını mantar uçlarına takma. Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: BMS kesiyor mu "
                 "gözle (röle K1 açık; F3 takılı olmadığı için yalnız F4 / F5 girişleri, tam açılış aşama 2'de). Mantara basınca PC817 #1 girişi "
                 "0 V, bırakınca akü gerilimi (12,8–14,4 V). Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök. Devreye "
                 "alma, ön şarj ve motor yön testi F5'te (İlk enerji, aşama 2). Bu aşamalar, sigorta sırası, ölçü noktası, klemensin + ucu, "
                 "multimetre aralığı ve \"yerden kesik\" düzeni bu adım için kaynakta yok, doğrulanmadı"],
        kablo=["Etek bandını takarken K1 hatları sıkışmasın"],
        ucus="radyal",
        # F10d: alt adımlar (sira grubu = alt adım). Yönler giriş yolu ölçümünden (planlama/d158/F10d-gunluk.md, F1 tablosu): orta bant
        # yalnız yandan (±x), arka birimler yandan, arka dolgu yukarıdan girer. Ön bantlar ve ön dolgu hiçbir düz yönden girmiyor
        # (sonar ve braket perçin somunu bandın deliklerine farklı eksenlerden giriyor): gerekçeli istisna, karar maddesi.
        alt=True,
        # F10d düzeltme 1 (B-1): orta bantlar sağ / sol ayrı alt adım (tek karede karşı yanın ısıl gömmeleri ve braket cıvatası
        # görünmüyordu: 0 piksel). Isıl gömmeler bandın boss'unda: bant saydam.
        sira=[dict(ad="Orta bant sağ + orta braket", desen=("Etek orta sağ", "(Etek braketi sağ z+0)"),
                   ucus={"*": (1, 0, 0)}, saydam=("Etek orta sağ",),
                   is_="Orta bandın sağını +x'ten braketin üstüne getir (giriş yolu ölçümü: orta bant yalnız yandan girer). Orta "
                       "brakete (z 0) dışarıdan M3×14; L brakette M3 perçin somun (delik Ø5,1). Bandın z ±88 bindirme boss'larındaki "
                       "ısıl gömmeler hazırlıkta takılı (adım 0; bant saydam çizili). Bağlarken akü ayrık (XT60 açık)."),
              dict(ad="Orta bant sol + orta braket", desen=("Etek orta sol", "(Etek braketi sol z+0)"),
                   ucus={"*": (1, 0, 0)}, kamera=(-0.85, 0.62, 1.25), saydam=("Etek orta sol",),
                   is_="Orta bandın solunu −x'ten getir, orta brakete (z 0) dışarıdan M3×14 (perçin somun). Isıl gömmeler sağdaki "
                       "gibi hazırlıkta takılı (bant saydam çizili)."),
              dict(ad="Ön sağ bant", desen=("Etek ön sağ", "(etek z+88 sağ)", "(Etek braketi sağ z+105)"), ucus={"*": (1, 0, 1)},
                   saydam=("Etek ön sağ",),
                   is_="Ön sağ bandı orta bandın önüne getir; z +88 bindirmesini 3 × M3×6 ile bağla, z +105 braketine dışarıdan M3×14. "
                       "Bant düz bir yoldan girmiyor (ölçüm, Notlar).",
                   ucus_ok={"Etek ön sağ": "giriş yolu ölçümü (düzeltme turu 1; ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım; temas sayılmaz): düz yol yok. Çizilen (1, 0, 1) yönünde sonar 1–12 mm; "
                                           "+z'de yalnız braket perçin somunu 1–7 mm, sonra serbest; +x'te sonar 1–73 mm; +y'de sonar 1–81 mm. "
                                           "Karar önerisi F10d-K1"}),
              dict(ad="Ön dolgu şeridi", desen=("Etek dolgu şeridi ön", "(etek x+38 ön)"), ucus={"*": (0, 1, 0)},
                   saydam=("Etek dolgu şeridi ön",),
                   is_="Ön dolgu şeridini yukarıdan indir, son 10 mm'de önden içeri (−z) it (ölçüm: yerinden önce +z 10 mm, sonra "
                       "+y 170 mm serbest; düz yukarı yolda orta sonar 1–82 mm). x +38 ön bindirmesine 2 × M3×6.",
                   ucus_ok={"Etek dolgu şeridi ön": "iki parçalı yol ölçüldü (düzeltme turu 1; ışın aralıkları h 0,5 mm, eşik 0,2 mm): "
                                                    "yerinden +z 10 mm, sonra +y 170 mm serbest; düz +y yolunda orta sonar 1–82 mm. "
                                                    "Rehber düz uçuş çiziyor"}),
              dict(ad="Ön sol bant", desen=("Etek ön sol", "(etek z+88 sol)", "(Etek braketi sol z+105)", "(etek x-38 ön)"),
                   ucus={"*": (1, 0, 1)}, kamera=(-0.85, 0.62, 1.25),
                   is_="Ön sol bandı getir; z +88 sol bindirmesi 3 × M3×6, x −38 ön bindirmesi 2 × M3×6, z +105 braketine M3×14. "
                       "Bant düz bir yoldan girmiyor (ölçüm, Notlar).",
                   ucus_ok={"Etek ön sol": "giriş yolu ölçümü (düzeltme turu 1; ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım; temas sayılmaz): düz yol yok. Çizilen (−1, 0, 1) yönünde sonar 1–11 mm; "
                                           "+z'de yalnız braket perçin somunu 1–7 mm, sonra serbest; −x'te sonar 1–61 mm; +y'de sonar 1–81 mm. "
                                           "Karar önerisi F10d-K1"}),
              dict(ad="Masada: arka sağ bant + acil stop", masa="arka_sag", desen=("Etek arka sağ", "Acil stop"),
                   ucus={"Acil stop mantarı": (0, 0, -1), "Acil stop kontak": (0, -1, 0), "*": (1, 0, 0)}, kamera=(0.85, 0.62, 1.25),
                   saydam=("Etek arka sağ",),
                   is_="Masada: acil stop mantarını bandın deliğine dışarıdan (arkadan) geçir, panel somunuyla sık; kontak gövdesini "
                       "içeriden alttan tak (giriş yolu ölçümü: kontak yalnız alttan girer). Bağlamadan önce mantarı multimetrenin "
                       "süreklilik kademesinde dene: NC uçları arasında mantar serbestken bip var, basılıyken yok (kaynakta yok, "
                       "doğrulanmadı). Bu bandın boss'larında F5'teki etek servis kapaklarının ısıl gömmeleri var (H1 2, H2 4) ve x +38 "
                       "arka dikişininkiler (3): hazırlıkta takılı (adım 0), bant saydam çizili; kapaklar F5'te yalnız cıvatalanır."),
              dict(ad="Arka sağ birimi → robot", bag="arka_sag", desen=("(etek z-88 sağ)", "(Etek braketi sağ z-105)"),
                   ucus_bag=(1, 0, 0), kamera="arka",
                   is_="Arka sağ bandı (mantar takılı) +x'ten getir (giriş yolu ölçümü: yalnız +x serbest). z −88 sağ bindirmesi "
                       "3 × M3×6, z −105 braketine M3×14. K1'de bırakılan acil stop ucunu kontağa bağla."),
              dict(ad="Arka dolgu şeridi", desen=("Etek dolgu şeridi arka", "(etek x+38 arka)"), ucus={"*": (0, 1, 0)}, kamera="arka",
                   is_="Arka dolgu şeridini yukarıdan indir (ölçüm: arka sağ bant takılıyken yalnız yukarıdan girer). x +38 arka "
                       "bindirmesine 3 × M3×6."),
              dict(ad="Masada: arka sol bant + ana anahtar", masa="arka_sol", desen=("Etek arka sol", "Ana anahtar"),
                   ucus={"Ana anahtar": (0, -1, 0), "*": (1, 0, 0)}, kamera=(-0.85, 0.62, 1.25), saydam=("Etek arka sol",),
                   is_="Masada: ana anahtar ASW-A01 gövdesini etek üst plakasının altına alttan tak (model yeri öneri, ölçü tahmini "
                       "zarf; bağlantı elemanı modelde yok, doğrulanmadı). Düğme: delik Ø30 tahmini, anahtarı ölç. Bu bandın "
                       "boss'larında H1 kapağının 2 ısıl gömmesi var: hazırlıkta takılı (adım 0), bant saydam çizili."),
              dict(ad="Arka sol birimi → robot", bag="arka_sol", desen=("(etek z-88 sol)", "(Etek braketi sol z-105)", "(etek x-38 arka)"),
                   ucus_bag=(-1, 0, 0), kamera=(-0.85, 0.62, -1.25),
                   is_="Arka sol bandı (ana anahtar takılı) −x'ten getir (giriş yolu ölçümü). z −88 sol bindirmesi 3 × M3×6, x −38 arka "
                       "bindirmesi 3 × M3×6, z −105 braketine M3×14. K1'de bırakılan iki ana hat ucunu anahtara bağla. XT60 şarj "
                       "girişi (panel konnektör): önerilen yer etek üst plakasının arkası, delik modelde yok (doğrulanmadı); delik "
                       "açıldıysa konnektörü tak, şarj ucunu akü ayrıkken bağla, açılmadıysa uç bantlı kalır. Şarj 10 A sigortası "
                       "takılmaz (aşama 1 listesi).")],
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
        # F10d: alt adımlar (sira grubu = alt adım). Bantlar yandan (±x; giriş yolu ölçümü, planlama/d158/F10d-gunluk.md F2 tablosu);
        # x 0 dikişinin aynı adlı cıvataları bant yüksekliğine göre ayrılır (konum).
        alt=True,
        # F10d düzeltme 1 (B-1): alt / uzatma bantları sağ / sol ayrı alt adım (tek karede karşı yanın braket cıvatası ve arka dikiş
        # 0 piksel). Sol alt adımda x 0 dikişi (ön + arka): bantlar saydam, ısıl gömmeler ev sahibi bantla gelir.
        sira=[dict(ad="Alt bant sağ + y 400 braketi", desen=("Gövde alt bandı sağ", "sağ y400)"), ucus={"*": (1, 0, 0)},
                   saydam=GOVDE_BANT,
                   is_="Gövde alt bandının sağını +x'ten getir, y 400 braketine dışarıdan M5×18 (pulsuz, M5 perçin somuna). Bandın "
                       "bindirme boss'larındaki ısıl gömmeler hazırlıkta takılı (adım 0; bant saydam çizili)."),
              dict(ad="Alt bant sol + y 400 braketi, x 0 dikişi", desen=("Gövde alt bandı sol", "sol y400)", "(gövde x0"),
                   # F10e: kamera (-0,85, 0,62, 1,25) iken bindirme cıvatası p0322 iki saydam bant katmanının arkasında (gizle-fark
                   # 2 px); (-1, 0,2, 0) ile alt adımın bütün yeni parçaları ≥ 30 px ve ≥ 0,2 × yalnız
                   konum={"(gövde x0": {"y": (0, 476.5)}}, ucus={"*": (1, 0, 0)}, kamera=(-1.0, 0.2, 0.0), saydam=GOVDE_BANT,
                   gizli_ok={"(gövde x0 arka)": voksel_ok(161, "arka sağ (0,85, 0,62, −1,25)")},
                   is_="Solunu −x'ten getir. x 0 dikişinin (ön ve arka) bindirmelerini M3×6 ile bağla, y 400 braketine dışarıdan M5×18."),
              dict(ad="Uzatma bandı 1 sağ + y 530 braketi", desen=("Gövde uzatma bandı 1 sağ", "sağ y530)", "(gövde y476"),
                   konum={"(gövde y476": {"x": (0, 1000)}}, ucus={"*": (1, 0, 0)}, kamera=(1.0, 0.35, 0.5),
                   saydam=GOVDE_BANT,
                   is_="Uzatma bandı 1 sağı alt bandın üstüne getir (dikiş y 476,5), y 476,5 bindirmelerini M3×6 ile bağla, y 530 "
                       "braketine M5×18."),
              dict(ad="Uzatma bandı 1 sol + y 530 braketi, x 0 dikişi", desen=("Gövde uzatma bandı 1 sol", "sol y530)", "(gövde y476", "(gövde x0"),
                   # F10e: (-1, 0,35, -0,5) iken bindirme cıvatası p0306 41 / 225 px (gizle-fark, oran 0,18); biraz alçak ve yandan hepsi geçer
                   konum={"(gövde x0": {"y": (476.5, 634)}}, ucus={"*": (1, 0, 0)}, kamera=(-1.0, 0.3, -0.3), saydam=GOVDE_BANT,
                   gizli_ok={"(gövde x0 ön)": voksel_ok("165–206"), "(gövde x0 arka)": voksel_ok("170–215", "arka sağ (0,85, 0,62, −1,25)")},
                   is_="Uzatma bandı 1 solu getir; y 476,5 ve x 0 bindirmelerini bağla, y 530 braketine M5×18."),
              dict(ad="Uzatma bandı 2 sağ + y 688 braketi", desen=("Gövde uzatma bandı 2 sağ", "sağ y688)", "(gövde y634"),
                   konum={"(gövde y634": {"x": (0, 1000)}}, ucus={"*": (1, 0, 0)}, kamera=(1.0, 0.35, 0.5),
                   saydam=GOVDE_BANT, gizli_ok={"(gövde y634 arka)": voksel_ok()},
                   is_="Uzatma bandı 2 sağı getir (dikiş y 634), y 634 bindirmelerini bağla, y 688 braketine M5×18."),
              dict(ad="Uzatma bandı 2 sol + y 688 braketi, x 0 dikişi", desen=("Gövde uzatma bandı 2 sol", "sol y688)", "(gövde y634", "(gövde x0"),
                   # F10e: (-1, 0,35, -0,5) iken bindirme cıvataları p0308 / p0310 34 / 31 px (oran < 0,2); 34.4 ile aynı düzeltme
                   konum={"(gövde x0": {"y": (634, 791.5)}}, ucus={"*": (1, 0, 0)}, kamera=(-1.0, 0.3, -0.3), saydam=GOVDE_BANT,
                   gizli_ok={"(gövde x0 ön)": voksel_ok("167–207"), "(gövde x0 arka)": voksel_ok("171–215", "arka sağ (0,85, 0,62, −1,25)"),
                             "(gövde y634 arka)": voksel_ok("150–192", "arka sağ (0,85, 0,62, −1,25)"),
                             "(gövde y634 yan)": voksel_ok(447, "sol (−1, 0, 0)")},
                   is_="Uzatma bandı 2 solu getir; y 634 ve x 0 bindirmelerini bağla, y 688 braketine M5×18."),
              dict(ad="Masada: orta bant sağ + hoparlör", masa="orta_sag",
                   desen=("Gövde orta bandı sağ", "Hoparlör kabı ön", "Hoparlör 40", "Hoparlör kabı arka", "Köpük ped", "Hoparlör"),
                   # F10e: kamera (-1, 0,45, 0,6) iken kelepçe cıvatası p0440 hoparlörün arkasında kalıyordu (gerçek malzemeyle gizle-fark
                   # 0 px, eşik Σ|Δ| > 24); (-1, 0,45, 0,2) ile 127 px
                   ucus={"Gövde orta bandı": (1, 0, 0), "*": (0, 2, -3)}, kamera=(-1.0, 0.45, 0.2),
                   # F10d düzeltme 1 (B-1): hoparlör grubu iç içe (halka → hoparlör → arka kap → ped → kelepçe) ve ızgara duvarının
                   # arkasında: bant ve grubun parçaları saydam, cıvatalar opak
                   saydam=("Gövde orta bandı sağ", "Hoparlör kabı", "Hoparlör kelepçesi", "Hoparlör 40", "Köpük ped (hoparlör"),
                   gizli_ok={"Köpük ped (hoparlör": voksel_ok()},
                   is_="Masada, orta bant sağın ön duvarında, ızgara deliklerinin arkasında: kabın ön halkasını duvara, hoparlörü "
                       "(40 × 20, 4 Ω, 3 W) içine, flanşlı arka kabı arkasına koy; kelepçeyi köpük pedle 2 × M3×20 ile boss'lardaki ısıl "
                       "gömmeye sık. Bu sıra kaynakta yok, doğrulanmadı. Bandın boss'larındaki ısıl gömmeler (hoparlör 2, y 1005 dikişi, "
                       "F5'teki arka servis kapağının 4'ü) hazırlıkta takılı (adım 0); karede bant ve hoparlör grubu saydam."),
              dict(ad="Orta bant sağ → gövde", bag="orta_sag", desen=("(gövde y792",), konum={"(gövde y792": {"x": (0, 1000)}},
                   ucus_bag=(1, 0, 0), saydam=GOVDE_BANT + ETEK_BANT + ("Hoparlör kabı",),
                   kamera=(-1.0, 0.35, -0.5),   # F10e: varsayılan bakışta bindirme cıvatası p0268 17 px (gizle-fark); bununla hepsi geçer
                   # F10d düzeltme 1 (kontrol B-4): "5,53 mm" eksen ışınının kirişiydi, derinlik değil (K3 geri çekildi)
                   giris_ok={"*": "giriş yolu ölçümü: +x'te 138 mm boyunca çarpışma yok, sonra kutular ayrılıyor. Serbest sayılmamasının "
                                  "tek nedeni dinlenmede orta bant sağ ile uzatma bandı 2 sağın ortak yüzü: ışın ölçümü 5,53 mm kiriş "
                                  "veriyor, gerçek derinlik (nokta–üçgen) en çok 0,28 mm, medyan 0; temas, çarpışma değil"},
                   is_="Bandı takmadan önce K2'de göğüs altında bırakılan hoparlör kablosunu (PAM8403'ten boyundan iner) hoparlöre "
                       "bağla. Sonra orta bant sağı +x'ten getir (dikiş y 791,5), bindirmeleri bağla."),
              dict(ad="Orta bant sol", desen=("Gövde orta bandı sol", "(gövde y792", "(gövde x0"),
                   # F10e: kamera (-0,85, 0,62, 1,25) iken bindirme cıvatası p0270 22 px (gizle-fark); (1, 0,35, -0,5) ile hepsi geçer
                   konum={"(gövde x0": {"y": (791.5, 2000)}}, ucus={"*": (1, 0, 0)}, kamera=(1.0, 0.35, -0.5),
                   saydam=GOVDE_BANT + ETEK_BANT + ("Hoparlör kabı",),
                   gizli_ok={"(gövde y792 arka)": voksel_ok(76, "arka sağ (0,85, 0,62, −1,25)")},
                   is_="Orta bant solu −x'ten getir; y 791,5 ve x 0 dikişlerini bağla. Bandın boss'larındaki ısıl gömmeler (y 1005 "
                       "dikişi ve F5'teki arka servis kapağının 3'ü) hazırlıkta takılı (adım 0; bantlar saydam çizili).")],
    ),
    "F3": dict(
        baslik="Göğüs bantları + göğüs ekranı",
        is_="1. Göğüs bantları sağ + sol, dikiş y 1005. Bindirmeleri bağla (x = 0'da cep altı y 1022,7 ve cep üstü y 1222 dahil), "
            "y 1095 braketine dışarıdan M5×18 tak.\n"
            "2. VESA taşıyıcı (PETG-CF): ekran cebinden direğin ön (+Z) kanalına, 2 × M6×18 + pul + çekiç somun. Yükseklik kanalda ayarlanır; "
            "cıvatalara ekran takılmadan, plakanın ortasından ulaşılır.\n"
            "3. 11,6\" ekranı (kasalı) cebe koy. Akü XT60 ayrık, ana anahtar kapalıyken göğüs ekranı mini 2 A sigortasını tak (F1 aşama "
            "1'de takılı değildi). Dalın girişi K11'e bağlı (`planlama/adim3/elektrik.md` göğüs ekranı dalı). K11 a (varsayılan; ana anahtar "
            "sonrası, röle öncesi): 12 V fişini takmadan önce regülatör çıkışını yeniden ölç. Ölçümden önce saat, yüzük, bileklik çıkar "
            "(`planlama/d158/testler/00-genel.md` kural 8). K2'den gelen 12 V kablosunun ekran ucundaki fiş ölçüm boyunca regülatör "
            "çıkışının 12 V'unu taşır: fişin metal ucunu bantla yalıt, ekran kasasına ve metal parçalara değmesin (genel güvenlik, kaynakta "
            "yok). Akü ayrıkken multimetreyi DC V kademesine al "
            "(20 V aralığı ya da otomatik), kırmızı ucu V soketine tak; kırmızı ucu regülatör çıkışının + klemensine, siyah ucunu çıkışın "
            "− klemensine bağla (kart üstü yazıya göre). Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç, çıkışı oku: 12 V "
            "(K2'de ayarlandı). Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök. Sonra K2'de bırakılan HDMI ve "
            "12 V uçlarını enerjisizken tak (90° fişler). K11 b (anahtarlı bara): dal F5 aşama 2'de devreye alınana kadar enerjisiz, burada "
            "ölçülemez. 12 V fişini bu adımda takma, ucu bantlı kalsın; yalnız HDMI'yi enerjisizken tak. Ölçüm ve 12 V fişi F5 aşama 2'de. "
            "Ölçüm sırası ve ölçü noktası kaynakta yok, doğrulanmadı.\n"
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
                 "K11 a: regülatör çıkışı 12 V okundu, 12 V fişi akü XT60'tan ayrıldıktan sonra takıldı. K11 b: 12 V fişi takılmadı, ucu "
                 "bantlı (F5 aşama 2)",
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
        # F10c (P10.3): iş metnindeki sıra (bant → taşıyıcı → ekran → çerçeve); taşıyıcı M6'sı ekran takılınca kapanır (sıra denetimi)
        # F10d: alt adımlar; bantlar yandan (±x, giriş yolu ölçümü), sağ / sol ayrı (y 1005 dikişinin aynı adlı cıvataları x'e göre)
        alt=True,
        sira=[dict(ad="Göğüs bandı sağ + y 1095 braketi", desen=("Göğüs bandı sağ", "(Gövde braketi sağ", "(gövde y1005"),
                   konum={"(gövde y1005": {"x": (0, 1000)}}, ucus={"*": (1, 0, 0)}, saydam=GOVDE_BANT,
                   kamera=(0.6, 0.45, 1.25),   # F10e: varsayılan bakışta bindirme cıvatası p0280 29 px (gizle-fark); bununla hepsi geçer
                   is_="Göğüs bandı sağı +x'ten getir (dikiş y 1005), bindirmeleri bağla, y 1095 braketine dışarıdan M5×18. "
                       "Bant düz bir yoldan girmiyor (ölçüm, Notlar). Bandın boss'larındaki ısıl gömmeler (y 1198 dikişi ve F5'teki "
                       "üst arka servis kapağının 4'ü) hazırlıkta takılı (adım 0; bantlar saydam çizili).",
                   ucus_ok={"Göğüs bandı sağ": "giriş yolu ölçümü (düzeltme turu 1; ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım; temas sayılmaz): düz yol yok. +x'te orta bant sağ ile 1–159 mm "
                                               "ortak hacim (bindirme dili), 173 mm'de ayrılıyor; +y'de orta bant 1–13 mm; ±z'de orta bant 1–213 mm. "
                                               "Karar önerisi F10d-K1"}),
              dict(ad="Göğüs bandı sol + y 1095 braketi", desen=("Göğüs bandı sol", "(Gövde braketi sol", "(gövde y1005", "(gövde x0"),
                   konum={"(gövde y1005": {"x": (-1000, 0)}}, ucus={"*": (1, 0, 0)}, kamera=(-0.85, 0.62, 1.25), saydam=GOVDE_BANT,
                   is_="Göğüs bandı solu −x'ten getir; bindirmeleri bağla (x = 0'da cep altı y 1022,7 ve cep üstü y 1222 dahil), y 1095 "
                       "braketine M5×18. Bant düz bir yoldan girmiyor (ölçüm, Notlar). Isıl gömmeler (y 1198 dikişi, üst arka servis kapağının "
                       "3'ü) hazırlıkta takılı.",
                   ucus_ok={"Göğüs bandı sol": "giriş yolu ölçümü (düzeltme turu 1; ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım; temas sayılmaz): düz yol yok. −x'te orta bant sol ile 1–135 mm "
                                               "ortak hacim (bindirme dili), 161 mm'de ayrılıyor; +y'de orta bant 1–13 mm ve göğüs bandı sağ 1–19 mm; "
                                               "±z'de orta bant 1–213 mm. Karar önerisi F10d-K1"}),
              dict(ad="VESA taşıyıcı → direk ön kanalı", desen=("VESA taşıyıcı", "Taşıyıcı ", "Çekiç somun M6 (direk ön kanalı)"),
                   kamera=(0.3, 1.0, 0.35), saydam=GOVDE_BANT + ("Göğüs ekranı VESA taşıyıcı", "Göğüs ekranı çerçevesi"),
                   ucus_ok={"Çekiç somun M6": "uçuş yolu ölçümü: düz −z yolu yok (direk kanalının dudağı 2–25 mm); kanal boyunca −y "
                                              "400 mm'de tek engel kendi cıvatası (2–6 mm), +y'de 166 mm'den sonra travers. Döndürerek "
                                              "oturtma ölçülmedi. Rehber düz uçuş çiziyor"},
                   gizli_ok={"Çekiç somun M6": "çekiç somun direğin kanalının içinde, taşıyıcının arkasında (perdelenme tamamen gizli "
                                               "sayıyor); alt adım karesinde taşıyıcı ve bantlar saydam çizili, somun görünür (kimlik tamponu)"},
                   is_="VESA taşıyıcı (PETG-CF): ekran cebinden direğin ön (+z) kanalına, 2 × M6×18 + pul + çekiç somun. Yükseklik kanalda "
                       "ayarlanır; cıvatalara ekran takılmadan, plakanın ortasından ulaşılır."),
              dict(ad="Göğüs ekranı → taşıyıcı (VESA)", desen=("Göğüs ekranı 11", "VESA pulu", "VESA cıvatası"), sema=("Göğüs dokunmatiği",),
                   # F10e: (0,85, 0,62, 1,25) iken VESA pulları p0424 / p0426 48 / 27 px (gizle-fark, oran < 0,2); tam önden hepsi geçer
                   kamera=(0.0, 0.4, 1.0), ucus={"Göğüs ekranı 11": (0, 1, 4), "*": (0, 0, -1)},
                   # F10d düzeltme 1 (B-1): VESA cıvataları ve pulları ekranla taşıyıcının arasında (arkadan bakışta taşıyıcı ve
                   # bantlar, önden bakışta ekran örtüyor): önden bakış, ekran (yeni parça, 0,4), taşıyıcı ve bantlar saydam
                   saydam=GOVDE_BANT + ("Göğüs ekranı VESA taşıyıcı", "Göğüs ekranı çerçevesi", "Göğüs ekranı 11"),
                   is_="11,6\" ekranı (kasalı) cebe önden, yaklaşık 14° yukarıdan koy (giriş yolu ölçümü: bantlar ve taşıyıcı takılıyken "
                       "yalnız bu yön serbest; düz önden 19,5 mm sonra bant). 12 V ölçümü ve fişler için adımın iş metnindeki 3. maddeyi izle (K11 a / b). "
                       "Sonra ekranı taşıyıcıya arkadan 4 × M4×12 + pul ile bağla (VESA 75 × 75): üst arka servis kapağı açık, direğin "
                       "yanından. Dokunmatik USB ucu F5'e kadar boşta, etiketli."),
              dict(ad="Göğüs ekranı çerçevesi", desen=("Göğüs ekranı çerçevesi", "Çerçeve cıvatası"), ucus={"*": (0, 0, 1)},
                   saydam=GOVDE_BANT + ("Göğüs ekranı çerçevesi",),
                   is_="Çerçeve sağ + sol: göğüs bandına dışarıdan, yarı başına 4 × M3×6 ISO 7380, çerçeve flanşındaki ısıl gömmeye. "
                       "Ekran camı çerçevenin 2 mm gerisinde, köşe takozlarına dayalı.",
                   ucus_ok={"Göğüs ekranı çerçevesi": "giriş yolu ölçümü (düzeltme turu 1; ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım; temas sayılmaz): düz yol yok. +z'de göğüs bandı 1–9 mm "
                                                      "(flanş bandın iç yüzünde) ve ekran 3–7 mm; yana (dışa) göğüs bandı 1–151 mm; +y ve −z de kapalı. "
                                                      "Karar önerisi F10d-K1"})],
    ),
    "F4": dict(
        baslik="Omuz bantları",
        is_="1. Omuz bantlarını Ø84 rulman kapağının üstünden geçir; üst kapak boynu sarar. M3×6 ISO 7380 ile bağla.\n"
            "Bundan sonra bant ancak göbek sökülünce çıkar.\n"
            "2. Kol servo uçlarını omuz yarığından dışarı al: K2'de travers arkasında bırakılan uzatma uçlarını, her omuzda ψ 214 "
            "yarığından (12 × 6 mm) dışarı çıkar. Üst arka servis kapağı F5'e kadar açık: elle kapak açıklığından travers arkasına uzan, ucu "
            "yarıktan dışarı it. Dışarıda bekleyen uçlar G2'de (S2 eki göbekte) ve H1'de (dirsek, bilek) eklenir; G3'te tambur bağına, oradan "
            "kola döşenir, G4'te yarıkla tambur bağı arası kasete U-lopu olarak oturur. Elle ulaşılabilirlik ölçüldü (bantlar takılıyken): yolun 5 köşesinin "
            "hepsine elin 0,5–23 mm yakınına kadar engelsiz düz yol var; kablonun kendisi elle denenmedi.",
        baglanti_md="M3×6 ISO 7380",
        kontrol=["Yarık ψ 214 (12 × 6 mm) kablo için açık; Ø84'e açılan anahtar deliği (Y3 K3) temiz",
                 "Bant kapağa sürtmüyor, boyun dönüyor",
                 "Kol servo uzatma uçları iki omuzda da yarıktan dışarıda, etiketli; yarıkta ezilmiyor"],
        kablo=["Geçit: ψ 214 yarığı. Travers arkasındaki kol servo uzatma uçları bu adımda yarıktan dışarı alınır (madde 2); G2, G4 "
               "ve H1 onları dışarıda kullanır"],
        ucus="radyal",
        # F10d: alt adımlar sağ / sol (aynı adlı dikiş cıvataları x'e göre). Yön ölçümü: F10d-gunluk.md F4 tablosu
        alt=True,
        # F10d düzeltme 1 (B-1): bantlar saydam; sol bandın ön ve arka dikişi tek karede görünmüyor (arka dikiş 0 piksel): arka
        # dikiş ayrı alt adım, arkadan kamera
        sira=[dict(ad="Omuz bandı sağ", desen=("Omuz bandı sağ", "(gövde y1198"), konum={"(gövde y1198": {"x": (0, 1000)}},
                   ucus={"*": (1, 0, 0)}, gizli_ok={"(gövde y1198 ön)": voksel_ok(276)}, kamera=(0.3, 1.0, 0.35),
                   # üstten bakışta x 0 arka ısıl gömmeyi kafa örtüyor: kafa kabukları ve iskeleti de saydam
                   saydam=GOVDE_BANT + KAFA_KABUK + ("Kafa iskeleti", "Servo yuvası", "Rulman yuvası", "Boyun", "Eğme çatalı"),
                   is_="Omuz bandı sağı Ø84 rulman kapağının üstünden geçir; üst kapak boynu sarar. y 1198 bindirmelerine M3×6 ISO 7380. "
                       "Bandın boss'larındaki ısıl gömmeler (x 0 dikişi, S1 kaseti) hazırlıkta takılı (adım 0; bantlar saydam çizili).",
                   # F10f düzeltme 2 (kontrol F10f-kontrol-2 M8): kol adımında (36) dize anahtar kabul edilmez; aynı gerekçe dar anahtarla
                   # (engeller ve derinlikler düzeltilmiş denetimle ölçüldü, satır F10d'den beri değişmedi)
                   ucus_ok={"p0215": dar("yol", "giriş yolu ölçümü (düzeltme turu 1; ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım; temas sayılmaz): düz yol yok. +x'te göğüs bandı sağ 1–161 mm "
                                              "(bindirme dili), rulman kapağı 3–99 mm, yuva bağlantı cıvatası 3–29 mm; +y'de 7 mm sonra rulman kapağı "
                                              "7–101 mm; ±z'de göğüs bandı. Karar önerisi F10d-K1",
                                         p0213=75.0, p0078=25.25, p0070=10.0, p0287=2.57, p0289=2.57)}),
              dict(ad="Omuz bandı sol, ön dikiş", desen=("Omuz bandı sol", "(gövde y1198 ön)", "(gövde x0 ön)"),
                   konum={"(gövde y1198 ön)": {"x": (-1000, 0)}}, ucus={"*": (1, 0, 0)}, kamera=(-0.85, 0.62, 1.25), saydam=GOVDE_BANT,
                   gizli_ok={"(gövde y1198 ön)": voksel_ok(308), "(gövde x0 ön)": voksel_ok(257)},
                   ucus_ok={"p0216": dar("yol", "giriş yolu ölçümü (düzeltme turu 1; ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım; temas sayılmaz): düz yol yok. −x'te göğüs bandı sol 1–137 mm "
                                             "(bindirme dili), rulman kapağı 3–99 mm, yuva bağlantı cıvatası 3–29 mm; +y'de 7 mm sonra rulman kapağı "
                                             "7–101 mm; ±z'de göğüs bandı ve omuz bandı sağ. Karar önerisi F10d-K1",
                                        p0214=63.0, p0151=25.25, p0143=10.0, p0291=2.57, p0293=2.57)},
                   is_="Omuz bandı solu aynı biçimde geçir; önde y 1198 ve x 0 dikişlerini M3×6 ile bağla. S1 kaseti ısıl gömmeleri "
                       "hazırlıkta takılı (bantlar saydam çizili)."),
              dict(ad="Omuz arka dikişi", desen=("(gövde y1198 arka)", "(gövde x0 arka)"), kamera=(-0.85, 0.62, -1.25),
                   ucus={"*": (1, 0, 0)}, saydam=GOVDE_BANT,
                   gizli_ok={"(gövde x0 arka)": voksel_ok(435, "arka sağ (0,85, 0,62, −1,25)")},
                   is_="Arkada sol y 1198 ve x 0 dikişlerini M3×6 ile bağla. Bundan sonra bant ancak göbek sökülünce çıkar. Sonra kol "
                       "servo uçlarını omuz yarığından dışarı al (sonraki iki alt adım)."),
              # F10f (P10.5): kol kablo yolu, gövde girişi. Parça yok (desen boş); çizim rehber_kol_kablo.py (KOL_KABLO s1 cikis + govde_ici)
              # "Kablo yolu": yolun iç ucu travers arkasında K2 servo uzatma demetinin (adım 32 kablo parçası) içinde; demet saydam.
              # "Direk-travers": köşe bağlantısı iç ucun önünde (F10f-dogrula ucOrtu: 66,8 mm önde); "Gövde direği": sonra direk (31,1 mm önde)
              dict(ad="Sağ omuz: kol servo uçları yarıktan dışarı", desen=(), kolk=("sag:govde",), kamera=(0.55, 0.75, 0.9),
                   saydam=GOVDE_BANT + ("Rulman kapağı", "Omuz yuvası", "Kablo yolu", "Direk-travers", "Gövde direği"),
                   is_="Sağ omuz: travers arkasında bekleyen 3 uzatma ucunu (dirsek, bilek, S2; K2'de bırakıldı) gövdenin içinden dışa doğru "
                       "götür: travers arkası → omuz eksenine paralel dışa → ψ 214 yarığı (12 × 6 mm) → dışarı. Üst arka servis kapağı "
                       "açıklığından travers arkasına uzan, ucu yarıktan it. Uçlar: gövde tarafı travers arkasındaki demette (K2), kol ucu "
                       "yarığın dışında serbest (G2'de S2 ucu göbeğe, G3'te dirsek ve bilek uçları kola gider; G4'te kaset bu yarığın önüne oturur)."),
              dict(ad="Sol omuz: kol servo uçları yarıktan dışarı", desen=(), kolk=("sol:govde",), kamera=(-0.55, 0.75, 0.9),
                   saydam=GOVDE_BANT + ("Rulman kapağı", "Omuz yuvası", "Kablo yolu", "Direk-travers", "Gövde direği"),
                   is_="Sol omuz: aynı iş, aynalı (yarık sol omuzda ψ 214).")],
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
        is_="1. S2 kablosunu kısalt ve uzatmaya ekle: G2'den yaklaşık 20 mm önce, göbek arka iç şeridinde (lehim + makaron Ø ≤ 4,5, yaklaşık 25 mm, ya da JR çifti; kablo bağı). Yer tahmini, yerinde ölç. S2 uzatması 1700 mm (ekten dağıtım kartına, konnektör payı 30 mm tahmini dahil).\n"
            "2. Servoyu göbeğe cıvatala. Göbeğin karşı tarafındaki mafsal (625ZZ, pul, M5×12) G3'te, kol çatalıyla gelir.",
        # K56 (Ahmet, 13.11.2026, seçenek C): 625ZZ tezgâhta kol çatalına preslenir ve çatalla G3'te gelir; mafsal pulu + M5×12 G3'te
        # çataldan sonra (omuz_rapor.py SIRA 2 ve 9). Eskiden "Karşı tarafa 625ZZ ve M5 pim" (iç bilezik, pul, cıvata burada).
        baglanti_md="Kol başına 4 × M4×16 + 4 kontra somun",
        alet="alyan 3 + 7 mm",
        erisim="Düz. Somunların 2'si cepte, 2'si açık ağızla (Y3 C3)",
        kontrol=["Ek makaronla kaplı, çekince kopmuyor", "S2 ekseni elle dönüyor"],
    ),
    "G3": dict(
        baslik="S2 hornu, kol çatalı, üst kol tüpü",
        is_="1. S2 hornu, merkez vidası.\n"
            "2. Kol çatalı → horn (4 × M3×8). 625ZZ çatalın arka kolunun Ø16 yuvasında: tezgâhta önceden preslenir, iki bileziğiyle "
            "çatalla gelir. Çatal yerindeyken mafsal pulu + M5×12: arka koldan rulmanın iç bileziğinden göbekteki M5 ısıl gömmeye "
            "(iç bileziği göbeğe sıkar, çatal döner).\n"
            "3. Üst kol tüpü → çatal.\n"
            "4. Kablolar (F4'te yarıktan dışarı alınan uzatma uçlarıyla, gövdeden kola doğru): yarıktan tambur bağına (ψ 145): 3 şerit kanala "
            "teğet, 2 ip demetin üstünde düğüm; yarıkla tambur bağı arası gevşek kalır (G4'te U-lopu). Tambur bağından göbek arka iç şeridine (G2).\n"
            "5. Dirsek ve bilek uzatmaları G2'den S2 lopu L 80 mm (2 şerit) → K noktası (çatal arka plakasının arkası, yapışkan taban) → tüp "
            "penceresi. Kol ucu pencerede bekler: H1'de servo kablosuna eklenir.",
        baglanti_md="Kol başına 1 × M3×5 horn; 4 × M3×8 çatal–horn; 1 × M5×12 + pul mafsal (çataldan sonra); 2 × M3×8 tüp → ısıl gömme",
        alet="PH1, alyan 2,5 / 4",                                  # K56: M5×12 mafsal cıvatası G2'den geldi (alyan 4)
        kontrol=["Mafsal cıvatası sıkıyken çatal S2 ekseninde elle dönüyor, 625ZZ yuvasından çıkmadı",
                 "Tüp penceresi arka duvarda: 10 geniş, 14 düz + iki uç 45° (≈ 24 boy). M1 yalnız dişi JR'yi (7,9 × 2,75) denetledi; erkek JR (10,3 × 4) boyuna çevrilerek geçmeli, doğrulanmadı",
                 "Bağ açısı 0 ± 2°, düğüm cerrah + kare, uç 3 mm",
                 "K noktası tabanı CAD'de 10 × 10 (tahmini), v4 taban 28 × 28: sığması doğrulanmadı"],
        kablo=["Bu adımda geçen: tüp penceresi, S2 lobu (L 80), tambur bağı (ψ 145)"],
        # F10f (P10.5): kol kablo yolu alt adımları. Parça grubu önce, sonra kablolar sağ / sol (desen boş; çizim rehber_kol_kablo.py)
        alt=True,
        sira=[dict(ad="S2 hornu, kol çatalı, üst kol tüpü (sağ + sol)",
                   desen=("S2 horn", "Kol çatalı", "625ZZ", "Mafsal", "Üst kol tüpü", "Tüp cıvatası", "Çatal-horn", "Isıl gömme"),
                   # F10f düzeltme 1: horn servo milinin ucuna eksen boyunca (+z), tüp çatalın altından (−y); kol çatalı +x (sol aynalı)
                   ucus={"S2 horn": (0, 0, 1), "Kol çatalı": (1, 0, 0), "Üst kol tüpü": (0, -1, 0)},
                   # F10f düzeltme 2 (madde 1b): 625ZZ dış bilezik çatalla birlikte uçar (omuz_rapor SIRA 2: "625ZZ'yi çatalın arka
                   # koluna bastır"). K56 (Ahmet, 13.11.2026, seçenek C): iç bilezik de G2'den buraya geldi ve çatalla birlikte uçar
                   # (rulman tezgâhta preslenmiş, iki bilezik çatalda); mafsal pulu + M5×12 G2'den geldi, bağlantı satırı olarak çatal
                   # satırından sonra kendi ekseni boyunca takılır (omuz_rapor SIRA 9). F10f'in K1-a dar istisnası (p0121 / p0194) kalktı.
                   birlikte={"625ZZ rulman (dış bilezik)": "Kol çatalı", "625ZZ rulman (iç bilezik)": "Kol çatalı"},
                   # K56: iç bilezik 40.1 sonunda perdelenmede tamamen gizli (G2'de alt adımsız adımdaydı, sınır uygulanmıyordu); 44.1'deki
                   # dirsek 625ZZ ile aynı yapı (F10g-gunluk.md, okur pikseli F10f-dogrula gizli_piksel)
                   gizli_ok={i: gizli("625ZZ rulman iç bileziği kol çatalının arka kolundaki Ø16 yuvada, mafsal pulu ve cıvata başının altında")
                             for i in ("p0116", "p0189")},
                   is_="S2 hornu + merkez vidası; kol çatalı → horn (4 × M3×8): 625ZZ tezgâhta çatalın arka kolunun Ø16 yuvasına "
                       "önceden preslenir, iki bileziğiyle çatalla birlikte gelir. Çatal yerindeyken mafsal pulu + M5×12: arka koldan "
                       "rulmanın iç bileziğinden göbekteki M5 ısıl gömmeye. Üst kol tüpü → çatal (2 × M3×8 → ısıl gömme). Kablolar "
                       "sonraki iki alt adımda."),
              dict(ad="Sağ kol: uzatmalar tüp penceresi → K → S2 lopu → tambur bağı", desen=(), kolk=("sag:uzatma_kol", "sag:lop_s2", "sag:gecis_s1", "sag:bag_k", "sag:bag_tambur"),
                   kamera=(0.9, 0.35, -1.0), saydam=("Kol çatalı", "Omuz göbeği", "S2 horn", "Omuz bandı", "Göğüs bandı"),
                   is_="Sağ kol, gövdeden kola: F4'ten beri ψ 214 yarığının dışında bekleyen 3 uzatmayı (dirsek, bilek, S2) tambur "
                       "bağına (ψ 145) getir: kanala teğet, 2 ip demetin üstünde düğüm. Yarıkla tambur bağı arası gevşek kalır (G4'te kasetin "
                       "U-lopu). Tambur bağından göbek arka iç şeridine (G2; S2 uzatması burada servo kablosuna G2'de eklendi). Dirsek ve "
                       "bilek uzatmaları G2'den L 80 mm S2 lopuyla K noktasına (çatal arka plakasının arkası): kablo bağıyla tabana bağla, "
                       "tüp cıvatasının yanından tüp penceresine. Uçlar: gövde tarafı travers arkasındaki demette (K2); kol tarafında "
                       "dirsek ve bilek uzatmalarının ucu tüp penceresinde bekler (H1'de eklenir), S2 uzatması G2'de göbekte eklendi. Elle dene: S2 5…120° arasında lop gerilmiyor, çatala sürtmüyor. Çizim "
                       "modeldeki duruşta (S2 0°): bu duruş S2 aralığının dışında, lop burada aralıktakinden sıkı çizilir; S2'yi 5°'nin "
                       "altına indirme."),
              dict(ad="Sol kol: uzatmalar tüp penceresi → K → S2 lopu → tambur bağı", desen=(), kolk=("sol:uzatma_kol", "sol:lop_s2", "sol:gecis_s1", "sol:bag_k", "sol:bag_tambur"),
                   kamera=(-0.9, 0.35, -1.0), saydam=("Kol çatalı", "Omuz göbeği", "S2 horn", "Omuz bandı", "Göğüs bandı"),
                   is_="Sol kol: aynı iş, aynalı (S2 0° notu dahil).")],
    ),
    "G4": dict(
        baslik="S1 kablo kaseti",
        # F10e düzeltme 1 (kontrol bulgu 7): "+x'ten kaydırarak takılmaz" yalnız CAD duruşunda ölçüldü (+x üst kol tüpü 5,34 mm, −x omuz
        # bandı); kol duruşunda ölçülmedi. Metin ölçülene indirildi. F10f (F10e devri e): "CAD duruşu" okurun diliyle (kollar düz aşağı,
        # modeldeki duruş); iddia aynı ölçümle sınırlı
        is_="Sırayı bozma. Kaseti yandan kaydırarak takma: kollar düz aşağıdayken (modeldeki duruş) yandan sürülen kaset +x'te üst kol "
            "tüpüne, −x'te omuz bandına değiyor; başka kol duruşunda bu denenmedi. Önden radyal tak.\n"
            "(a) Gövde önden radyal, x ofsetsiz, arka plaka omuz pedine yaslı. Kol: S1 −45 / −20 / 0 × S2 90 ya da S1 −45 × S2 5.\n"
            "(b) U'yu elle kanala koy; dış koşu duvar boyunca, ψ 214'te yarıktan içeri (ψ: arka 90, aşağı 180, ön 270). Lop L 171,4 mm (−5…0 mm), kablo üstünde işaretli.\n"
            "(c) Duvar bağı: 2 ip, ψ 226,5 / 230, düğüm dışarıda; sıkarken demeti −x'e tut.\n"
            "(d) Kapak önden radyal (kol S1 0…135°, S2 ≥ 30°); flanş gövdeden x +3,3…5 mm havada (S1 −45°'de en çok +3,3 mm).\n"
            "(e) Kapağı −x'e it: 2 Ø3 pim (ψ 331 ve kulak ψ 300) girer.\n"
            "(f) 2 dikme cıvatasını S1 −45 / S2 90'da sık (en az 8 mm erişim).",
        baglanti_md="Kol başına 2 × M3×8 dikme; 2 Ø3 pim; 2 Ø0,4 mumlu ip",
        alet="alyan 2,5, makas",
        erisim="Önden radyal; dikmeler yalnız S1 −45 / S2 90'da",
        kontrol=["Yarık 12 × 6 mm: JR erkek geçer", "Kol tam taramada kablo gerilmiyor, kapağa sürtmüyor",
                 "S1 ≥ 120° iken S2 ≤ 117°: bu sınırı aşma"],
        poz=dict(S1=-45, S2=90),                                    # F10c: dikme cıvataları ev pozunda kapalı, bu pozda açık
        kablo=["Geçit: ψ 214 yarığı → travers arkasındaki S1 ucu (K2'de bırakıldı)"],
        # F10f (P10.5): alt adımlar. Kaset gövdesi → U-lop sağ / sol → uç duruş yakın kareleri (yalnız sağ kol; sol aynalı) → kapak
        alt=True,
        sira=[dict(ad="Kaset gövdeleri (sağ + sol)", desen=("S1 kaset gövdesi",),
                   ucus={"S1 kaset gövdesi": (0, 0, 1)},                 # F10f düzeltme 1: önden radyal (metinle aynı)
                   is_="(a) Kaset gövdesini önden radyal tak, x ofsetsiz, arka plaka omuz pedine yaslı (iki omuz). Kol: S1 −45 / −20 / 0° "
                       "× S2 90° ya da S1 −45° × S2 5° (tasarımın duruşu; çizim modeldeki duruşta, S1 0°, S2 0°)."),
              dict(ad="Sağ kol: S1 U-lopu + duvar bağı + yarık", desen=(), kolk=("sag:s1_lop", "sag:s1_cikis"), kenar=("S1 kablo tamburu", "S1 kaset gövdesi"), kamera=(1.0, 0.25, 0.35),
                   saydam=("S1 kaset gövdesi", "Kol çatalı", "Üst kol tüpü", "Omuz göbeği", "S2 horn", "Omuz bandı", "Göğüs bandı"),
                   is_="Sağ kol: (b) 3 kablolu demeti tambur bağından (ψ 145) kanala koy: iç koşu tamburda, U, dış koşu kaset duvarı "
                       "boyunca. Lop L 171,4 mm (−5…0 mm), kablo üstündeki işarete göre. (c) Duvar bağı ψ 226,5 / 230 (2 ip, düğüm dışarıda). "
                       "Duvar boyunca ψ 214'e, orada radyal içe ve arka plaka yarığından içeri. Bu, G3'te gevşek bırakılan, yarıkla "
                       "tambur bağı arasındaki parça: uzatma kesintisiz, ek yok. Uçlar: gövde tarafı yarıktan içeride (F4, K2 demeti); kol "
                       "tarafında dirsek ve bilek uzatmaları G3'ten beri tüp penceresinde, S2 uzatması G2'de göbekte S2 servo kablosuna ekli."),
              dict(ad="Sol kol: S1 U-lopu + duvar bağı + yarık", desen=(), kolk=("sol:s1_lop", "sol:s1_cikis"), kenar=("S1 kablo tamburu", "S1 kaset gövdesi"), kamera=(-1.0, 0.25, 0.35),
                   saydam=("S1 kaset gövdesi", "Kol çatalı", "Üst kol tüpü", "Omuz göbeği", "S2 horn", "Omuz bandı", "Göğüs bandı"),
                   is_="Sol kol: aynı iş, aynalı."),
              # F10f düzeltme 1: ortak kamerada −45° yolunun tambur bağı ucu 625ZZ dış bileziğin arkasında kalıyordu (uç pikseli 0); rulman saydam
              # F10f düzeltme 2 (kontrol B2 3.3): tambur ve duvar kenar çizgili (41.2 gibi); ucun 32,6 mm önündeki mafsal cıvatası (p0118) saydam
              dict(ad="Sağ kol, yakın: S1 −45° uç duruşunda U-lopu", desen=(), kolk=("sag:s1_-45",), iz=("sag:s1_+135",), kenar=("S1 kablo tamburu", "S1 kaset gövdesi"), sema_yalniz=True, kamera=(1.0, 0.12, 0.08),
                   saydam=("S1 kaset gövdesi", "S1 kablo tamburu", "Kol çatalı", "Üst kol tüpü", "Omuz göbeği", "S2 horn", "Omuz bandı",
                           "Göğüs bandı", "625ZZ rulman", "Mafsal cıvatası"),
                   is_="Sağ kol, elle tarama (S1 −45…135°): S1 −45°'de tambur bağı ψ 100'e döner, demet tambura sarılır: iç koşu "
                       "(tamburdaki yay, tambur bağından U'ya) 125,3°, dış koşu (duvar boyunca yay, U'dan duvar bağına) 10,2°, U ψ ≈ 225 "
                       "(yaylar 0,1°'ye, ψ tam dereceye yuvarlı). Kol bu uçta kablo gerilmeden durmalı. Çizim kablonun bu duruştaki yeri; "
                       "parçalar modeldeki duruşta (tambur dönmüş çizilmedi). Soluk iz: S1 +135°'deki U-lopu (sonraki alt adım), "
                       "kamera ve renk iki karede aynı."),
              dict(ad="Sağ kol, yakın: S1 +135° uç duruşunda U-lopu", desen=(), kolk=("sag:s1_+135",), iz=("sag:s1_-45",), kenar=("S1 kablo tamburu", "S1 kaset gövdesi"), sema_yalniz=True, kamera=(1.0, 0.12, 0.08),
                   saydam=("S1 kaset gövdesi", "S1 kablo tamburu", "Kol çatalı", "Üst kol tüpü", "Omuz göbeği", "S2 horn", "Omuz bandı",
                           "Göğüs bandı", "625ZZ rulman", "Mafsal cıvatası"),
                   is_="Sağ kol: S1 +135°'de tambur bağı ψ 280'e döner, demet tamburdan açılıp duvara yatar: iç koşu (tamburdaki yay) "
                       "10,1°, dış koşu (duvar boyunca yay) 74,9°, U ψ ≈ 290 (yaylar 0,1°'ye, ψ tam dereceye yuvarlı). S1 ≥ 120° iken "
                       "S2 ≤ 117°: S2'yi bu sınırın üstüne çıkarma. Soluk iz: S1 −45°'deki U-lopu (önceki alt adım), kamera ve renk iki karede "
                       "aynı. Sol kolda aynı, aynalı."),
              dict(ad="Kapaklar + pimler + dikme cıvataları (sağ + sol)", desen=("S1 kaset kapağı", "Kaset cıvatası"),
                   ucus={"S1 kaset kapağı": (0, 0, 1)},                  # F10f düzeltme 1: önden radyal; −x itme çizilmez (dar istisna)
                   ucus_ok={"p0233": dar("duruş", POZ_KAPAK, p0232=4.2), "p0235": dar("duruş", POZ_KAPAK, p0234=4.2),
                            "p0463": dar("duruş", POZ_CIV, p0121=11.0, p0127=5.46, p0129=2.98, p0128=2.6),
                            "p0467": dar("duruş", POZ_CIV, p0194=11.0, p0200=5.46, p0202=2.98, p0201=2.6)},
                   is_="(d) Kol S1 0…135°, S2 ≥ 30°'deyken kapağı önden radyal getir, flanş gövdeden x +3,3 mm havada; (e) kapağı −x'e it, "
                       "2 Ø3 pim girer; (f) 2 dikme cıvatasını S1 −45° / S2 90°'de sık. Çizim kolu modeldeki duruşta (S1 0°, S2 0°) ve "
                       "kapağı tek düz yolla gösterir: o duruşta ψ 200 cıvatasının yolunu kol çatalı kapatır, −x itme ise kol çatalına değer.")],
    ),
    "H0a": dict(
        baslik="Tezgâh: ön kol + servolar",
        is_="1. Dirsek ve bilek servolarını ön kola cıvatala. Dirsek somunları cepte; dirsek alt iki kulak cıvatası Ø8 erişim deliğinden "
            "(Y3 C2). Bilek somunları cepte değil: 7 mm açık ağızla tek yönden tut (lokma yerel olarak sığıyor ama tutacağına el "
            "ulaşmıyor; sıra denetimi: açık ağız el bölgesine 25,5–36 mm'de ulaşıyor).\n"
            "2. Bilek kablosu: mil ucundan içe, geri, ara duvar çentiği (6 × 5 mm), dirsek servosu arkası, tırnak.\n"
            "3. Dirsek kablosu üstten tırnağa. Tırnakta iki kablo; kablo bağı kanat + demet.",
        baglanti_md="Kol başına 8 × M4×16 + 8 kontra somun",
        erisim="Cıvatalar düz alyanla. Dirsek somunları cepte (8 somun), dirsek alt kulaklar Ø8 delikten (Y3 C2). Bilek somunları "
               "(8 somun) cepte değil: 7 mm açık ağız, tek yönden, dar (anahtar el bölgesine 25,5–36 mm'de ulaşıyor); lokmanın tutacağına el ulaşmıyor "
               "(sıra denetimi, 20 mm el)",
        kontrol=["Çentikte kablo ezilmedi", "Kablo bağı kanadı tırnağı tutuyor"],
        kablo=["Geçit: ara duvar çentiği 6 × 5 mm ve tırnak"],
        # F10f (P10.5): servolar, sonra kablolar sağ / sol (desen boş; çizim rehber_kol_kablo.py, KOL_KABLO yol_bilek_servo / yol_dirsek_servo)
        alt=True,
        sira=[dict(ad="Servolar → ön kol (sağ + sol)", desen=("Ön kol", "Dirsek servosu", "Bilek servosu", "Isıl gömme"),
                   # F10f düzeltme 1: iki ön kol tezgâhta yerinde (sağ tezgâh tabanı, sol da; sağ / sol kulak cıvatası aynı mesafe),
                   # dirsek servosu yuvasına arkadan (−z), bilek mili servosuyla birlikte, kontra somun 15 mm (25 mm'de ön kola giriyordu)
                   ucus={"Ön kol": "yerinde", "Dirsek servosu MG996R": (0, 0, -1)},
                   ucus_d={"Dirsek servosu kontra somunu": 15}, birlikte={"Bilek servosu çıkış mili": "Bilek servosu MG996R"},
                   gizli_ok={i: gizli("dirsek servosu kontra somunu ön kolun cebinde, kulak cıvatasının ucunda") for i in ("p0590", "p0647", "p0649")},
                   is_="Dirsek ve bilek servolarını ön kola cıvatala (madde 1)."),
              dict(ad="Sağ kol: bilek ve dirsek servo kabloları → tırnak", desen=(), kolk=("sag:servo_bilek", "sag:servo_dirsek"),
                   kamera=(1.0, 0.3, -0.75), saydam=("Ön kol",),
                   is_="Sağ kol: bilek servosu kablosu mil ucundan içe, geri, ara duvar çentiğinden (6 × 5 mm, tam mm'ye yuvarlı) geçer, dirsek servosunun "
                       "arkasından tırnağa; dirsek servosu kablosu üstten tırnağa. Tırnakta 2 kablo, kablo bağı kanat + demet. Ucu serbest: "
                       "dirsek lopu H0c'de."),
              dict(ad="Sol kol: bilek ve dirsek servo kabloları → tırnak", desen=(), kolk=("sol:servo_bilek", "sol:servo_dirsek"),
                   kamera=(-1.0, 0.3, -0.75), saydam=("Ön kol",),
                   is_="Sol kol: aynı iş, aynalı.")],
    ),
    "H0b": dict(
        baslik="Tezgâh: dirsek hornu",
        # K57 (Ahmet, 13.11.2026, seçenek a): horn merkez vidası H0c'ye, dirsek çatalından sonraya (eskiden burada, "Çataldan önce";
        # M6 tablosunun erişim sütunu "çataldan önce" diyordu, ezildi). Çatalın dış kolunda vida için Ø9 erişim deliği var (dirsek_parcalar.py).
        is_="Dirsek hornunu servo miline geçir (merkez vidası bu adımda takılmaz: H0c'de, dirsek çatalından sonra).",
        baglanti_md="Kol başına yok (horn merkez vidası M3×5 H0c'de)",
        alet="el",
        erisim="Düz",
        kontrol=["Horn servo milinin dişlisine oturdu"],
        # F10d: horn dirsek servo ekseninde (x) ince disk: servo ekseni boyunca gelir (F10c'ye kadar +y). İki kol x ekseninde
        # birbirini örter: sağ / sol alt adım, kendi yanından bakış.
        ucus=(1, 0, 0),
        alt=True,
        sira=[dict(ad="Sağ kol: dirsek hornu", yan="sag", desen=("Dirsek horn",), kamera=(1.0, 0.4, 0.5),
                   is_="Sağ kol: dirsek hornunu servo miline geçir; merkez vidası H0c'de, çataldan sonra."),
              dict(ad="Sol kol: dirsek hornu", yan="sol", desen=("Dirsek horn",), kamera=(-1.0, 0.4, 0.5),
                   is_="Sol kol: aynı iş, aynalı.")],
    ),
    "H0c": dict(
        baslik="Tezgâh: dirsek çatalı",
        is_="1. 625ZZ'yi tezgâhta çatalın Ø16 yuvasına bastır (rulman çatalla gelir); çatalı horna cıvatala; çatal yerindeyken "
            "dirsek horn merkez vidası M3×5 (PH1), çatalın dış kolundaki erişim deliğinden; M5 pimi yanaktaki ısıl gömmeye tak (robotta "
            "erişilemez: göğüs bandı 8,9 mm).\n"
            "2. Kablo: tırnak → lop L 120 mm → çatal oluğu (6 geniş, 4,5 derin; 2 şerit, sıcak tutkal) → Ø10 delik.",
        baglanti_md="1,58 m: kol başına 4 × M3×12 DIN 912 + 2 × DIN 125-A pul çatal–horn (M6'daki M3×8 eski); 1 × M3×5 horn merkez "
                    "vidası (çataldan sonra); 1 × M5×12 + pul",
        alet="PH1, alyan 2,5 / 4",                                  # K57: horn merkez vidası H0b'den geldi (PH1)
        kontrol=["Horn merkez vidası sıkı, horn servo milinde oturdu",
                 "Dirseği 0…105° arasında elle dene: lop gerilmiyor, oluğa sürtmüyor"],
        kablo=["Geçit: çatal oluğu ve Ø10 delik"],
        # F10f (P10.5): çatal, sonra dirsek lopu sağ / sol (çizim KOL_KABLO dirsek_lop, kablo_yolu.lop_coz, dirsek 0)
        alt=True,
        sira=[dict(ad="Dirsek çatalı + horn merkez vidası + pim (sağ + sol)",
                   desen=("Dirsek çatalı", "625ZZ", "Dirsek horn merkez", "Pim", "Çatal-horn"),
                   # F10f düzeltme 1: çatal +y (ön kolun üstünden); çatal-horn pulu cıvatasıyla birlikte. F10f düzeltme 2 (kontrol B2
                   # 3.1): 625ZZ (iki bilezik) çatalla birlikte uçar: rulman tezgâhta çatalın Ø16 yuvasına önceden bastırılır (dirsek
                   # montaj sırası 2, dirsek_rapor SIRA); ayrı −x uçuşta dış bilezik yuvanın omzundan 1,55 mm geçiyordu.
                   # K57 (Ahmet, 13.11.2026, seçenek a): horn merkez vidası H0b'den buraya, bağlantı satırı olarak çatal satırından sonra
                   # kendi ekseni boyunca (+x sağ / −x sol); F10f'in K1-b dar istisnası (p0562 / p0619) kalktı.
                   ucus={"Dirsek çatalı": (0, 1, 0)},
                   birlikte={"625ZZ rulman (dış bilezik)": "Dirsek çatalı", "625ZZ rulman (iç bilezik)": "Dirsek çatalı",
                             "Çatal-horn pulu": "Çatal-horn cıvatası"},
                   gizli_ok=dict([(i, gizli("625ZZ rulman bileziği çatal yanağının yuvasında, pim pulu ve cıvata başının altında"))
                                  for i in ("p0583", "p0628", "p0640")] +
                                 [(i, gizli("M5 pim pulu pim cıvatasının başının altında, yanakla baş arasında")) for i in ("p0584", "p0641")]),
                   is_="625ZZ'yi önce çatal iç kolunun Ø16 yuvasına, dudağa dayanana kadar bastır (tezgâhta; rulman çatalla birlikte "
                       "gelir). Çatalı horna cıvatala (4 × M3×12 + 2 pul); çatal yerindeyken dirsek horn merkez vidası M3×5 (PH1, çatalın "
                       "dış kolundaki erişim deliğinden); M5 pimi pulla yanaktaki ısıl gömmeye tak (madde 1)."),
              dict(ad="Sağ kol: dirsek lopu → çatal oluğu → Ø10 delik", desen=(), kolk=("sag:lop_dirsek",), kamera=(1.0, 0.3, -0.75),
                   saydam=("Dirsek çatalı", "Ön kol"),
                   is_="Sağ kol: tırnaktan çıkan 2 kabloyla L 120 mm lop bırak, çatal oluğuna (6 geniş, 4,5 derin) yatır, sıcak tutkalla "
                       "tut, Ø10 delikten yukarı it. Elle dene: dirsek 0…105° arasında lop gerilmiyor, oluğa sürtmüyor (çizim dirsek 0°)."),
              dict(ad="Sol kol: dirsek lopu → çatal oluğu → Ø10 delik", desen=(), kolk=("sol:lop_dirsek",), kamera=(-1.0, 0.3, -0.75),
                   saydam=("Dirsek çatalı", "Ön kol"),
                   is_="Sol kol: aynı iş, aynalı.")],
    ),
    "H0d": dict(
        baslik="Tezgâh: bilek hornu",
        is_="Bilek hornu + merkez vidası. Flanştan önce: sonra yalnız 0,3 mm kalır.",
        baglanti_md="Kol başına 1 × M3×5",
        kontrol=["Vida sıkı, horn oturdu"],
        # F10d: bilek hornu servonun altında (y ekseni): alttan gelir (F10c'ye kadar +y'den, servonun içinden), alttan bakış
        ucus=(0, -1, 0),
        kamera=(0.85, -0.62, 1.25),
        # F10d: tek alttan kamerada sağ kolun hornu karede değildi (F10d-dogrula 45: 2 görünmeyen). Sağ / sol alt adım,
        # kendi yanından alttan bakış (H0b gibi).
        alt=True,
        sira=[dict(ad="Sağ kol: bilek hornu + merkez vidası", yan="sag", desen=("Bilek horn",), kamera=(1.0, -0.6, 0.5),
                   is_="Sağ kol: bilek hornunu servo miline alttan geçir, merkez vidası M3×5 (PH1)."),
              dict(ad="Sol kol: bilek hornu + merkez vidası", yan="sol", desen=("Bilek horn",), kamera=(-1.0, -0.6, 0.5),
                   is_="Sol kol: aynı iş, aynalı.")],
    ),
    "H0e": dict(
        baslik="Tezgâh: bilek flanşı",
        is_="Flanşı horna cıvatala. Elden önce: sonra yalnız 1,0 mm kalır.",
        baglanti_md="Kol başına 4 × M3×8",
        kontrol=["Flanş eksende, yalpa yok"],
        kamera=(0.85, -0.62, 1.25),                                  # F10d: flanş alttan takılır, alttan bakış
        # F10d: tek kamerada sağ kolun flanşı ve 4 cıvatası karede değildi (F10d-dogrula 46). Sağ / sol alt adım.
        alt=True,
        sira=[dict(ad="Sağ kol: bilek flanşı + 4 cıvata", yan="sag", desen=("Bilek flanşı", "Flanş-horn"), kamera=(1.0, -0.6, 0.5),
                   saydam=("Bilek flanşı",),
                   is_="Sağ kol: flanşı horna alttan oturt, 4 × M3×8 çapraz sık."),
              dict(ad="Sol kol: bilek flanşı + 4 cıvata", yan="sol", desen=("Bilek flanşı", "Flanş-horn"), kamera=(-1.0, -0.6, 0.5),
                   saydam=("Bilek flanşı",),
                   is_="Sol kol: aynı iş, aynalı.")],
    ),
    "H0f": dict(
        baslik="Tezgâh: el",
        is_="Eli yakasından flanşa cıvatala.",
        baglanti_md="Kol başına 2 × M3×6 ISO 7380 → ısıl gömme",
        kontrol=["El yalpasız; bilek elle dönüyor"],
    ),
    "H1": dict(
        baslik="Dirsek modülü → üst kol tüpü",
        is_="1. Servo kablolarını uzatmalara ekle (uzatmaların kol ucu G3'ten beri tüp penceresinde): dirsek JR birleşimi tüp içinde (y −122…−62 mm, hedef y −105 mm); bilek lehim + makaron (Ø ≤ 4,5, yaklaşık 25 mm) tüp içinde, makaron tüp girişinin üstünde.\n"
            "2. Pim + bileziği tüpe geçir, sık.",
        baglanti_md="Kol başına 2 × M3×20 + 4 pul + 2 kontra somun",
        kontrol=["Kulaklar birbirine değmeden sık (M7 kupon D)", "Bilek kablosunda yaklaşık 0,5 mm artan var: çekme"],
        kablo=["Tüp içi: servo kabloları Ø10 delikten tüpe girer; uzatmalar G3'te döşendi, kol uçları tüp penceresinde"],
        ucus_bag=(0, -1, 0),
        # F10f (P10.5): kablolar tüpün içinden (dirsek modülü 1. alt adımda gelir), sonra bilezik. Çizim KOL_KABLO yol_ustkol + birlesim +
        # yol_uzatma_kol[0:pencere]; ek işaretleri JR boyu / makaron boyu
        # İlk alt adım modülün gelişi (kadrajı iki kolun modülü belirler); kablo alt adımlarında kadraj yalnız kablo yolu, tüp içi okunur
        alt=True,
        sira=[dict(ad="Dirsek modülleri tüpün altına (sağ + sol)", desen=(),
                   is_="Dirsek modülünü (H0a–H0f'de masada kuruldu) üst kol tüpünün altına getir; Ø10 delikten çıkan 2 servo kablosu "
                       "yukarıda. Kabloları tüpe sokmadan modülü oturtma: sonraki iki alt adım."),
              dict(ad="Sağ kol: kablolar tüpün içinden, ekler", desen=(), kolk=("sag:tup_ici", "sag:ek_bilek", "sag:nokta_lehim", "sag:tup_ara", "sag:ek_jr", "sag:nokta_jr", "sag:uzatma_tup"), kenar=("Üst kol tüpü",),
                   kamera=(1.0, 0.15, -0.25), saydam=("Üst kol tüpü", "Dirsek çatalı"),
                   is_="Sağ kol: dirsek modülünü tüpe yaklaştırırken 2 servo kablosunu Ø10 delikten tüpe it. Uzatmalar (dirsek, bilek; "
                       "her biri 1856 mm, birleşimden dağıtım kartına, konnektör payı 30 mm tahmini dahil) G3'te döşendi, kol uçları tüp "
                       "penceresinde bekliyor; tüp içinde pencereden birleşime iner. Dirsek kablosu: servonun dişi JR'si Ø10 delikten ve tüp "
                       "penceresinden geçer (tasarımın geçit denetimi); JR çifti (26 mm, boy tahmini) tüp içinde, S1 ekseninin 105 mm altında "
                       "(y −105 mm; serbest aralık y −122…−62 mm); servo kablosunda 102,4 mm artan kalır. Bilek kablosu: lehim + makaron "
                       "(Ø ≤ 4,5, yaklaşık 25 mm), makaron tüp girişinin üstünde; servo kablosu tüp girişine yaklaşık 0,5 mm artanla ulaşır: "
                       "çekme. Bu alt adımdan sonra iki kablonun iki ucu da bağlı: servo ↔ uzatma ↔ dağıtım kartı."),
              dict(ad="Sol kol: kablolar tüpün içinden, ekler", desen=(), kolk=("sol:tup_ici", "sol:ek_bilek", "sol:nokta_lehim", "sol:tup_ara", "sol:ek_jr", "sol:nokta_jr", "sol:uzatma_tup"), kenar=("Üst kol tüpü",),
                   kamera=(-1.0, 0.15, -0.25), saydam=("Üst kol tüpü", "Dirsek çatalı"),
                   is_="Sol kol: aynı iş, aynalı."),
              dict(ad="Pim + bilezik (sağ + sol)", desen=("Bilezik",),
                   # F10f düzeltme 1: somun tarafındaki pul somunla aynı yönden (cıvatanın tersi), kontra somun 20 mm (25 mm'de göğüs
                   # bandına giriyordu)
                   ucus_ters=("Bilezik pulu M3 (somun)",), ucus_d={"Bilezik kontra somunu": 20},
                   gizli_ok={"p0569": gizli("somun tarafındaki pul bileziğin kulağıyla kontra somun arasında")},
                   is_="Pim + bileziği tüpe geçir, 2 × M3×20 + 4 pul + 2 kontra somunla sık (madde 2).")],
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
            "ve XL4016 hat sigortalarını (A 7,5 A, B 7,5 A, C 5 A) tak (`planlama/adim3/elektrik.md` sigorta listesi). Şarj girişi mini "
            "10 A bu aşamada da takılı değil. K11 b ise (göğüs dalı anahtarlı barada; F3 madde 3): akü ayrıkken multimetreyi F3'teki gibi "
            "göğüs regülatörü çıkışına bağla (DC V; 12 V fişi takılı değil), teli kolların ve tekerlerin erişim alanının dışına çıkar. Tekerlekler yerden "
            "kesik (şasi takozda, `planlama/d158/testler/T13-rampada-acil-stop.md`); BTS EN = 0. Kollar aşağıda başlar: mantara basınca "
            "servo gücü de kesilir ve kollar düşer (E3 DTR / RTS notu). Kolların erişim alanında ve düşme hattında, kafanın ve tekerlerin "
            "erişim alanında kimse yok, bir kişi yalnız mantarda (kural 1 ve 7). Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana "
            "anahtarı aç: BMS kesiyor mu gözle (röle K1 açık; F3 / F4 / F5 girişleri, Pololu dahil; K11 a ise göğüs ekranı dalı da). "
            "Pi açılır; ESP32, Pi seri portu açılınca resetlenmemeli (boot mesajı yok; E3 DTR / RTS). Pi'den devreye al, ESP32 ön şarj "
            "dizisi (E9): ön koşul (mantar serbest, servo hedefleri son konumda, BTS EN = 0 ve PWM = 0) → röle K2 → 300 ms → PC817 #2 LOW "
            "(bara var) → röle K1 → 100 ms sonra K2 bırakılır → PC817 #2 LOW teyidi. K11 b ise regülatör çıkışını erişim alanının "
            "dışından oku: 12 V. Mantara basınca K1 düşer (K2 devreye almadan 100 ms "
            "sonra zaten bırakıldı), anahtarlı bara kesilir (PC817 #2 HIGH), kollar düşer. Mantarı bırak: röle kendiliğinden çekmez, "
            "yeniden devreye alma yalnız Pi komutuyla. "
            "Motor yön testi: her yan ileri komutta ileri döner; dönen tekere el uzatılmaz. Bitince ana anahtarı kapat, aküyü XT60'tan ayır "
            "(`planlama/adim3/elektrik.md` E3, E9). K11 b ise sonra ölçü uçlarını sök ve göğüs 12 V fişini enerjisizken tak (üst arka servis "
            "kapağı açıkken; fişe bu sırada erişim ölçülmedi). Bu adımdaki sıra kaynakta yok, doğrulanmadı.\n"
            "3. Testten sonra kapat: arka servis kapağı, üst arka servis kapağı (hub'la birlikte), etek H1 ve H2.\n"
            "H1 sigorta kutusuna açılır: uç yuvalar yedek, sık değişen F1, F3, F4, F5 ortada (29.10).",
        baglanti_md="1,58 m: arka kapak 7 × M3×6 ISO 7380; üst arka kapak 7 × M3×6 ISO 7380; H1 4 × M3×6 (x ±50); H2 4 × M3×6; hepsi "
                    "ısıl gömmeye. Isıl gömmeler kapaklarda değil, bantların boss'larında: arka kapağınkiler orta bantta (F2), üst arka "
                    "kapağınkiler göğüs bandında (F3), H1 / H2'ninkiler etek arka bantlarında (F1); o adımlarda takılı geldi. Hub: 1 mm "
                    "köpük bant (kapak takozunda). Üst kapak, H2 ve hub M6'da yok",
        alet="alyan 2",
        erisim="Düz. Hub kapağın iç yüzünde: kapak açıkken bağlanır",
        kontrol=["Hub köpük banda oturdu, yan dayamalar arasında; anahtarı açık",
                 "İlk enerji, aşama 2 (madde 2): BMS kesmedi; ön şarj dizisi PC817 #2 teyidiyle bitti; mantara basınca K1 düştü, bara kesildi; "
                 "her yan ileri komutta ileri döndü; sonunda akü XT60'tan ayrıldı",
                 "K11 b ise: göğüs regülatörü çıkışı 12 V okundu, 12 V fişi akü XT60'tan ayrıldıktan sonra takıldı",
                 "Testte ESP32 ve göğüs dokunmatiği hub üzerinden görünüyor",
                 "Kapak açılınca hub'a bağlı üç kablo gerilmiyor (yaklaşık 150 mm söküm payı)",
                 "E7 ve kafa ısı ölçümü kabuk kapalı yapıldı (kafada hesap ≈ 49 °C, ölçülmedi)", "Kapak altında kablo sıkışmadı"],
        kablo=["Hub: Pi USB 3 → boyun → hub (uzatma), Hub 1 → göğüs dokunmatiği, Hub 2 → ESP32. Hub kapanırsa ESP32 ve göğüs dokunmatiği birlikte düşer"],
        not_=["Ön şarj dizisi ESP32 yazılımında (`planlama/adim3/elektrik.md` E9, adım 1–6): yazılım hazır değilse aşama 2 yapılmaz, "
              "röleler elle kapatılmaz (kaynakta yok, doğrulanmadı)",
              "Şarj girişi mini 10 A iki aşamada da takılı değil: şarj girişi ana anahtardan önce akü + hattında (`planlama/adim3/elektrik.md` "
              "sigorta listesi). Sigorta ilk şarjdan önce, akü XT60 ayrıkken takılır; bu sıra kaynakta yok, doğrulanmadı. Uyarı: sigorta "
              "takıldıktan sonra etekteki şarj girişinin (XT60E-M panel erkek, `planlama/maliyet.json`) pimleri, akü XT60'tan ayrılmadıkça "
              "gerilimlidir: ana anahtar da mantar da bu kolu kesmez. Pimlere metal değdirme. Konnektörün cinsi ve kapağı karar taslağında "
              "(KT-F7d-1, `planlama/d158/F7d-kontrol.md`; kuyruğa girmedi); bu uyarı karar verilene kadar geçerli",
              "Hub'ın kapakla birlikte açılması ve 150 mm söküm payı tahmin; testten önce hub bağlantısının yapılması montaj mantığından, "
              "kaynakta sıra yok: doğrulanmadı",
              "Hub girişindeki gerilim ölçülmedi (hub USB'den beslenir)",
              "Altıncı USB cihazı karar bekliyor (K1): şimdilik hub'da 2 port boş"],
        ucus=(0, 0, -1),
        kamera="arka",
        # F10d: alt adımlar: hub üst kapağa masada, test (kapaklar açık), arka kapak, üst kapak hub'la, etek H1 / H2 yukarıdan
        alt=True,
        sira=[dict(ad="Masada: üst arka kapak + hub", masa="ust_kapak", desen=("Üst arka servis kapağı", "Köpük bant (USB Hub", "USB Hub"),
                   ucus={"Üst arka servis kapağı": (0, 0, -1), "*": (0, 0, 1)}, kamera=(0.6, 0.45, 1.25),
                   saydam=("Üst arka servis kapağı", "USB Hub"),
                   gizli_ok={"Köpük bant (USB Hub": voksel_ok(76)},
                   is_="Masada: 4'lü USB hub'ı üst arka servis kapağının iç yüzündeki takoza, iki yan dayamanın arasına 1 mm köpük bantla "
                       "yapıştır. Bağla: hub kablosu ← Pi USB 3'ten boyundan gelen uzatma (K2), Hub 1 → göğüs ekranı dokunmatiği (F3'te "
                       "boşta bırakılan USB), Hub 2 → ESP32 USB (K2'de direk arka yüzünden çıkarılan uç; 1N5819 yönü K2 madde 4). Hub 3 "
                       "ve 4 boş. Hub'ın anahtarı açık kalmalı."),
              dict(ad="İlk enerji, aşama 2 (kapaklar açık)", desen=(),
                   is_="Kapaklar açık, hub bağlı: devreye alma testi adımın iş metnindeki 2. maddeye göre (ön şarj dizisi, mantar, motor "
                       "yön testi). Bitince ana anahtarı kapat, aküyü XT60'tan ayır."),
              dict(ad="Arka servis kapağı", desen=("Arka servis kapağı", "(arka kapak)"), ucus={"*": (0, 0, -1)},
                   gizli_ok={"Bindirme cıvatası M3x6 (arka kapak)": voksel_ok("195–418")},
                   is_="Arka servis kapağını arkadan yerine koy, 7 × M3×6 ISO 7380 → ısıl gömme."),
              # F10e: 49.3 ile aynı bakıştan kare 49.3'ün neredeyse aynısıydı (iki benzer kapak, iki benzer bant); sol-arka-üstten
              dict(ad="Üst arka kapak (hub'la) → gövde", bag="ust_kapak", desen=("(üst arka kapak)",), ucus_bag=(0, 0, -1),
                   kamera=(-0.85, 0.62, -1.25),
                   # F10d düzeltme 1: eski 0,5 mm çarpışma kapakla uçan yanlış ev sahipli ısıl gömmelerdendi (kontrol B-2; somunlar
                   # artık göğüs bandında, F3); "1,5 mm" ışın kirişiydi (B-4, K3 geri çekildi). Uçuş istisnası gerekmiyor.
                   giris_ok={"*": "giriş yolu ölçümü: −z'de 29,5 mm boyunca çarpışma yok, sonra kutular ayrılıyor. Serbest sayılmamasının "
                                  "tek nedeni dinlenmede kapak ile göğüs bandı sağın ortak yüzü: ışın ölçümü 1,5 mm kiriş veriyor, gerçek "
                                  "derinlik (nokta–üçgen) en çok 0,057 mm, medyan 0; temas, çarpışma değil"},
                   is_="Üst arka servis kapağını hub'la birlikte arkadan yerine koy (hub kabloları gerilmesin, yaklaşık 150 mm söküm payı), "
                       "7 × M3×6 ISO 7380."),
              dict(ad="Etek servis kapakları H1 + H2", desen=("Etek servis kapağı",), ucus={"*": (0, 1, 0)}, kamera=(0.3, 1.0, 0.35),
                   saydam=("Etek servis kapağı",),
                   gizli_ok={"Kapak cıvatası M3x6 (Etek servis kapağı H1": voksel_ok()},
                   is_="Etek H1 (sigorta kutusu) ve H2 (ana sigorta) kapaklarını yukarıdan yerine koy, her biri 4 × M3×6. H1 sigorta "
                       "kutusuna açılır: uç yuvalar yedek, sık değişen F1, F3, F4, F5 ortada (29.10).")],
    ),
}

# Y3 (C1–C3, K1–K7) CAD'e işlendi: "M6 CAD sonrası değişecek" bayrağı 125 cm JSON'undan geliyordu, kapalı.
M6_BAYRAK_ACIK = False

# Kablo yolu şemaları: direğe çıkan (y > etek üstü 262 + pay) K2, tabanda kalan K1.
KABLO_K2_Y_ESIK = 300.0


def kablo_kapisi(y_maks):
    return "K2" if y_maks > KABLO_K2_Y_ESIK else "K1"


# F10c (P10.3): adım içi sıra. ADIM[kod]["sira"] = [dict(ad, desen, tezgah?)]: parça görünen adında (tr sonrası) desenlerden biri geçen
# ilk grup kazanır. Gruplar bu sırayla takılır; "tezgah" işaretli grup masada hazırlanır ve sıradaki yerinde robota bağlanır.
# rehber_veri.py satırları bu sırayla dizer ("sira", "sira_grup"); app.js sıralı takma ve rehber_sira.py denetimi bunu kullanır.
# F10d: isteğe bağlı konum / yan koşulu (aynı adlı bağlantı elemanları bantlara göre ayrılsın). "konum" = {desen: {"x" | "y" | "z":
# (alt, üst) mm}}: o desene uyan parçanın sınır kutusu merkezi [alt, üst) içinde olmalı. "yan" = "sag" / "sol": parçanın modülü bu ekle
# bitmeli (iki kollu adımlar).
def sira_grup_bul(sira, ad, merkez=None, modul=""):
    for i, g in enumerate(sira):
        if g.get("yan") and not modul.endswith("_" + g["yan"]):
            continue
        for d in g["desen"]:
            if d not in ad:
                continue
            k = (g.get("konum") or {}).get(d)
            if k and (merkez is None or any(not (k[e][0] <= merkez["xyz".index(e)] < k[e][1]) for e in k)):
                continue
            return i
    return None


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
