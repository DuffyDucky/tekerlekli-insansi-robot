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
        "lazer parçalar gelmiş. Alet seti ve bağlantı elemanları adım adım kutulara ayrılmış.\n"
        # P10.7b2e kısım 2 (Echo kararı 16.11.2026, K65; planlama/d158/sag-sol-karari.md): CAD'de +X = önden bakanın sağı = robotun
        # kendi solu (sınandı: sonarlar +z önde, acil stop x +117 z −200, montaj-yan.png kamerası +X'te robotun solunu görür). Donanım
        # adları korunur; örnekler kayıttan: acil stop mantarı x +117 / z −200 (taban-analiz.json), "SOL" yazılı aynalı kol −X'te
        # P10.7b2f (F10m-kare-inceleme § 5): tanım kalın başlıkla ayrı paragraf; basılı sayfada kutu (yazdir.html "**…:**" ile başlayan paragraf)
        "**Sağ / sol tanımı:** Bu rehberde ve kablo tablosunda sağ / sol, robota önden bakan kişinin sağı / soludur; robotun kendi sağı / solu "
        "değildir. Örnek: acil stop mantarı, robota önden bakınca sağ arka köşededir; üstüne 'SOL' yazılan aynalı kol önden bakınca "
        "solda takılır (robotun kendi sağ kolu). Parça ve kart adlarındaki sağ / sol da bu tanıma göredir; yazılımdaki adlar robotun "
        "kendi sağını / solunu kullanır, karşılıkları `planlama/d158/sag-sol-karari.md`'de. "
        # düzeltme turu 1 (F10m-kontrol N13): arkadan çalışan montajcı için tek ipucu
        "Robotun arkasından çalışırken önden bakanın sağı senin solunda kalır.",
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
        # P10.7b2a: alt kat klemenslerinin kablo kimlikli talimatı (kablolar.json M01–M04, G12–G15, SV1, SV2, G18, G19 uçları)
        is_="Tezgâhta ayarlanan alt kat kartlarını (iki BTS7960B, XL4016 A / B / çevre) burçlara tak, klemenslerini kat gelmeden, üstü "
            "açıkken bağla; akü ayrık:\n"
            "1. Motor uçları (B2b'de plaka üstüne alındı): sol BTS7960B'nin M+ / M− klemensine ön sol motoru (M01) ve arka sol motoru "
            "(M02), sağ BTS7960B'ninkine ön sağ (M03) ve arka sağ motoru (M04) bağla. Aynı yandaki iki motor aynı klemense paralel "
            "girer: iki motorun + ucu M+'ya, − ucu M−'ye.\n"
            "2. BTS7960B güç girişleri ({awg.G12|G13}): sol kartın B+ / B− klemensine G12'yi, sağ kartınkine G13'ü bağla; + ve − "
            "karışmasın (kart üstü yazı).\n"
            "3. XL4016 A ve B: girişlerin IN+ / IN− klemensine G14 (A) ve G15'i (B), çıkışların OUT+ / OUT− klemensine SV1 (A) ve "
            "SV2'yi (B) bağla.\n"
            "4. XL4016 çevre: girişin IN+ / IN− klemensine G18'i, çıkışın OUT+ / OUT− klemensine G19'u bağla; G19'un hat sigortası "
            "yuvası {yer.hat-cevre}, sigortası takılmaz (F1 aşama 1'de takılır).\n"
            "Bu kabloların öbür uçları (bara, yıldız barası, sigorta kutusu, arayüz kartı, dağıtım kartları) K1'de bağlanır: aşağıdaki "
            "kablo notundaki gibi etiketle ve bantla.",
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
               "Akü kayışlarının tokası yanda, kablo yolunun üstünde değil",
               "Arka sol motor hattının (M02) çizimi gösterim şemasıdır (`lale158/kablo_yolu_taban.py`): çarpışma taramasından geçmedi, "
               "parça sayısına girmez, boy ölçümü değildir. Arka kablo deliği ve plaka altı modelden; motor kablosunun motordan çıkışı ve "
               "BTS7960 klemensine gelişi tahmin"],
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
        is_="Tezgâh: güç paneline sigorta kutusu, röle ve ana sigorta yuvası. XL4016 C, ön şarj kartı ve dağıtım kartı C (kafa "
            "servolarının hattı C; XL4016 C'nin yanında) da burada. "
            "Ana anahtar bu panele girmez: etek üst plakasının altına F1'de takılır.\n"
            # P10.7b2a (orkestratör kararı 6, 15.11): dağıtım kartı C güç panelinde; SV3 tezgâhta (kablolar.json SV3, kondansatorler)
            "Dağıtım kartı C, tezgâhta: kartın 2200 µF kondansatörünü V+ / GND barasına lehimle, yönü {yon.kondansator}. Gövdedeki eksi "
            "şeridi okunmuyorsa kondansatörü takma (kablajda teyit). Sonra SV3'ü ({awg.SV3}) XL4016 C'nin OUT+ / OUT− klemensinden "
            "dağıtım kartı C'nin 2 pin 5,08 mm giriş klemensine bağla: {kutup.SV3}. Bağlamadan önce telin iki ucunu "
            "etiketle, XL4016 C'nin ve kartın + / − yazısını karşılaştır: ters bağlanan kondansatör ısınır, kafa servoları zarar görür. Kafa "
            "servolarının sinyal köprüsü (P03) K1'de, uzatmaları (S09, S10) K2'de takılır.\n"
            # P10.7b2e (K52 a, orkestratör kararı 16.11): regülatör güç panelinde; ayar T7 B ile tezgâhta, ekran ve panel bağlı değilken
            # (planlama/d158/testler/T7-gogus-ekrani-12v.md). Kart, ölçüsü, panel üstündeki yeri ve bağlantı elemanı modelde / kayıtta yok.
            "Göğüs ekranı regülatörü (LM2577 + LM2596; K52 a): ekrana ve panele bağlamadan, tezgâhta çıkışını multimetreyle 12 V'a ayarla "
            "ve trimpotun konumunu boya noktasıyla işaretle (`planlama/d158/testler/T7-gogus-ekrani-12v.md` B). Sonra kartı güç paneline "
            "tak; giriş (IN+ / IN−) ve çıkış (OUT+ / OUT−) klemensleri erişilebilir kalsın. Kart, ölçüsü ve panel üstündeki yeri modelde "
            "yok; yeri ve bağlantı elemanı kaynakta yok, doğrulanmadı. Girişi (G20) K1'de, çıkışı (G21) K2'de bağlanır.",
        kontrol=["Sigorta kutusu, röle ve ana sigorta yuvası panele (M4 + naylon somun)",
                 "Göğüs ekranı regülatörü (LM2577 + LM2596) panelde; panele takılmadan önce tezgâhta, ekran bağlı değilken çıkışı 12 V'a "
                 "ayarlandı, trimpotu boya noktasıyla işaretli (T7 B)",
                 "Dağıtım kartı C: kondansatörün eksi şeritli bacağı GND barasında; SV3 bağlandı (XL4016 C OUT+ → kartın V+, OUT− → "
                 "GND). Akü ayrıkken multimetrenin direnç kademesinde kartın V+ ile GND arası sıfırda kalmıyor (kısa devre yok; "
                 "kondansatör dolarken değer yükselir)",
                 "Ön şarj direnci ({ohm.onsarj}) panelden ≥ 5 mm yüksekte, kablo demetine değmez (E9)",
                 "XL4016 C ve ön şarj kartı da bu panelde (Y3 yerleşimi); giriş, çıkış klemensleri erişilebilir",
                 "Sigortaları henüz takma",
                 "Kartlar takılmadan tezgâhta (bu adımdan önce): XL4016 C 6 V'a ayarlandı; akım sınırlı tezgâh kaynağıyla 12 V giriş, yüksüz, "
                 "çıkış ölçülerek (K1 kontrolü). PC817 ölçümü de arayüz kartı takılmadan tezgâhta (B6a). Bu sıra kaynakta yok, doğrulanmadı"],
        kablo=["Panelde yıldız barası (toprak, 5 M5 saplama), anahtarlı bara (4 M5 saplama) ve sigorta kutusu girişleri erişilebilir "
               "kalsın: düğümler saplama üstünde halka pabuçla, saplama başına en çok 4 pabuç (`planlama/adim3/kablolar.md` O-3 r, O-22). "
               "WAGO yok",
               "SV3'ün çizimi gösterim şemasıdır (`lale158/kablo_yolu_taban.py`): çarpışma taramasından geçmedi, parça sayısına girmez, boy "
               "ölçümü değildir. Dağıtım kartı C modelde yok: şemanın o ucunun yeri yaklaşık"],
        # P10.7b2e (F10l-gunluk § 10.7 N3): bara tutucusunun ne olduğu kayıtta var (kablolar.json bara-pabuc, maliyet.json), panele
        # nerede ve nasıl takılacağı, CAD'i ve baskı satırı yok; talimat yazılmadı (K64)
        # P10.7b2e kısım 2 (Echo kararı 16.11.2026, K64 a): tutucu tam taramalı CAD paketinde tasarlanıp basılır, satın alma yok;
        # o zamana dek rehber talimat uydurmaz
        not_=["Bara tutucusu (yıldız barasının ve anahtarlı baranın M5 saplamalarını taşıyan basılmış yalıtkan parça; "
              "`planlama/adim3/kablolar.json` bara pabuç kaydı) henüz tasarlanmadı: modelde ve baskı listesinde yok, sonraki tam "
              "taramalı CAD paketinde tasarlanıp basılacak, satın alınmayacak (K64 a). O zamana dek rehber panelde yerini ve bağlantı "
              "elemanını yazmaz. K1'in \"Toprak ve iki bara\" alt adımı iki barayı panelde varsayar",
              "Göğüs ekranı regülatörü (K52 a) modelde yok: karede görünmez, model sonraki tam taramalı CAD paketinde"],
    ),
    "B5": dict(
        baslik="Güç paneli → burçlar",
        kontrol=["Panel arka burçlara (z < 0); M5×12 + pul"],
        ucus_bag=(0, 1, 0),
    ),
    "B6a": dict(
        baslik="Tezgâh: elektronik katı",
        # P10.7b2a: kat üstü sinyal kablolarının talimatı (kablolar.json X01, I01, I02, P01, P02; kondansatorler)
        is_="Tezgâhta, kat burçlara inmeden: kartları kata tak (arayüz kartı, dağıtım kartı A ve B, PCA9685, BNO055, ESP32 taşıyıcı), "
            "sonra kat üstündeki kartlar arası kabloları bağla. Hepsi dişi uçlu sinyal teli (O-4 r); uçlar ve pinler "
            "`planlama/adim3/kablolar.md` tablolarında, kart üstü yazıya göre bağla:\n"
            "1. Dağıtım kartı A ve B: her kartın iki 2200 µF kondansatörünü V+ / GND barasına lehimle, yönü {yon.kondansator}; "
            "eksi şeridi okunmuyorsa takma (kablajda teyit).\n"
            # düzeltme turu 1 (F10i-kontrol Ü2): PC817 çıkış beslemesi 3V3 (kablolar.json X01 "PC817 çıkış beslemesi"; pin haritası D3)
            "2. Arayüz kartı → ESP32 (X01): bölücü çıkışları, iki röle sürücüsünün taban girişi, PC817 çıkışları, BTS EN düğümü, "
            "çevre 5 V → ESP32 VIN, GND → GND. "
            # P10.7b2f kısım 2 (K66, 16.11): VIN'e seri Schottky; yeri ve bağlantı biçimi kayıtta yok (kablolar.json X01 teyit)
            "VIN'e seri 1N5819: anot çevre 5 V tarafında, katot ESP32 VIN tarafında (K66; çevre hat sigortası atınca çevre "
            "yükleri USB'den beslenmesin diye). Diyodun takılacağı yer (arayüz kartı üstü ya da X01'in 5 V damarı) kayıtta "
            "yok, kablajda belirlenir. PC817 modülünün çıkış besleme ucunu (çıkış VCC) ESP32'nin "
            "{uc.X01:PC817_çıkış_beslemesi:b} pinine bağla (X01): 5 V'a bağlama. Modülün çıkışları PC817 #1 (acil stop, "
            "{gpio.ACIL_STOP_DURUM}) ve PC817 #2 (bara, {gpio.BARA_DURUM}) pinlerine gider; besleme 5 V olursa bu pinler 5 V görür, ESP32 "
            "girişleri en çok 3,6 V'a dayanır (pin haritası D3).\n"
            "3. I2C: ESP32 → PCA9685 giriş başlığı (I01: SDA, SCL, 3V3 → VCC, GND); PCA9685 çıkış başlığı → BNO055 (I02: SDA, SCL, "
            "VCC → VIN, GND). PCA9685'in OE ucunu kart üstünde GND'ye bağla.\n"
            # düzeltme turu 1 (F10i-kontrol Ü3): elektrik.md:226 "PCA9685 V+ klemensi boş kalır" emir kipinde (kablolar.json P01, P02 not)
            "4. Servo sinyalleri, yalnız sinyal teli: PCA9685'in sağ kol kanallarının sinyal pinlerini dağıtım kartı A'nın sinyal "
            "girişlerine (P01), sol kol kanallarınınkini dağıtım kartı B'ninkilere (P02) tek telli dişi uçlarla bağla. PCA9685'in V+ "
            "klemensine ve kanal başlıklarının V+ pinine tel takma; dağıtım kartının sinyal girişindeki V+ pini kartta bağlı değildir. "
            "3 telli hazır servo kablosu kullanırsan V+ damarını iki ucundan kes, makaronla yalıt. Neden: PCA9685'te kanal "
            "başlıklarının V+ pinleri V+ klemensine ortaktır; V+ teli takılırsa üç dağıtım kartının V+'ı, yani XL4016 A, B ve C'nin "
            "çıkışları birbirine paralel girer, dönüştürücüler zarar görebilir (kart içi ortak V+ sırası kablajda teyit). Hangi "
            "kanalın hangi girişe gittiği kablolar.md'de (P01, P02).\n"
            # P10.7b2e kısım 2 (F10l-kare-inceleme B6a): karede kart adı ve BNO055 yön oku yok (etiket düzeneği yok); yer tarifi
            # taban-analiz.json merkezlerinden, sağ / sol önden bakana göre (adım 0 tanımı)
            # P10.7b2f: uç etiketleri (rehber_gorunum.uc_isle; bağlantı tablosu kabloları I01, I02, P01, P02)
            "Karede bağlantı kablolarının uç kartları numaralı (etkileşimli sayfada adıyla, basılı sayfada adları karenin altında); "
            "yerleri (robota önden bakınca): arayüz kartı solda, ESP32 taşıyıcı sağda, PCA9685 onun "
            "önünde sağda, BNO055 ortada; dağıtım kartı A ön kenarda sağda, B solda. BNO055'in yön oku karede çizili değil: kartın "
            "üstündeki X okunu robotun önüne (yüz tarafı) çevir (kontrol).",
        kontrol=["Burçlar alttan, kartlar üstten (arayüz kartı, 2 dağıtım kartı, PCA9685, BNO055, ESP32 taşıyıcı)",
                 "X01, I01, I02, P01 ve P02 bağlandı: her dişi uç kart üstü yazıyla kablolar.md'deki uca eşleşti; dağıtım kartı A ve "
                 "B'de kondansatörlerin eksi şeritli bacağı GND barasında",
                 # P10.7b2f kısım 2 (K66)
                 "VIN'e seri 1N5819'un yönü: multimetrenin diyot kademesinde çevre 5 V → ESP32 VIN yönünde iletir, ters yönde "
                 "iletmez (bantlı uç, katot, VIN tarafında)",
                 # düzeltme turu 1 (F10i-kontrol Ü2, Ü3)
                 "PC817 modülünün çıkış VCC ucu ESP32'nin {uc.X01:PC817_çıkış_beslemesi:b} pininde (X01), 5 V'ta değil: multimetrenin "
                 "süreklilik kademesiyle çıkış VCC ile ESP32 {uc.X01:PC817_çıkış_beslemesi:b} pini arası öter, çıkış VCC ile çevre 5 V "
                 "arası ötmez",
                 # düzeltme turu 2 (F10i-kontrol-2 §5 P01–P03): ölçü noktası kanal başlığının V+ pini (kablolar.json P01, P02 not)
                 "PCA9685 V+ boş: multimetrenin süreklilik kademesiyle PCA9685'in kanal başlığının V+ pini ile dağıtım kartı A'nın ve "
                 "B'nin V+ barası arasında süreklilik yok (ötmemeli; ölçü ucu V+ klemensine değil kanal başlığının V+ pinine: kartta "
                 "klemens ile V+ rayı arasında ters kutup koruması olabilir). Öterse bir V+ teli takılı ya da kartın sinyal girişindeki V+ pini bağlı: o teli "
                 "ya da bağı sök, ölçüm ötmeyene kadar devam etme",
                 "BNO055 yönü: kartın X oku robotun önüne (+z)",
                 "Kartlar takılmadan tezgâhta (bu adımdan önce): arayüz kartındaki PC817 3,3 V'ta ölçüldü: girişe akım sınırlı tezgâh "
                 "kaynağıyla 12 V ver ve kes, çıkış LOW < 0,4 V, HIGH > 2,5 V (`planlama/adim3/elektrik.md` E3 notu; K1 kontrolü). Sıra kaynakta yok, doğrulanmadı"],
        kablo=["Kart konnektörleri erişilebilir; servo dağıtım çıkışları direğe bakar",
               # P10.7b2c ikinci yarı (ajan B): kısa teller 3B çizim değil, bağlantı tablosu (rehber_kablo.BAGLANTI_TABLOSU; satırın
               # metni kayıttan, rehber_deger {bag.<kimlik>}: kablolar.json damarları, GPIO ve kanal adı pin haritasıyla sınanır)
               # P10.7b2d-A (F10k kare bakışı, B6a not sırası): "3B çizim değil" açıklaması tablo satırlarından önce (metin aynı)
               "Bu dört satır (ve K1'deki P03) bağlantı tablosudur, 3B çizim değil: pin ve kanal numaraları kayıttan "
               "(`planlama/adim3/pin-haritasi.md`, `planlama/adim3/kablolar.json`). Başlıklardaki pin sırası ve kart üstündeki yeri "
               "kayıtta yok: kart üstü yazıya göre bağla",
               "Bağlantı tablosu I01 (ESP32 → PCA9685 giriş başlığı, {awg.I01} dişi uçlu tel): {bag.I01}",
               "Bağlantı tablosu I02 (PCA9685 çıkış başlığı → BNO055, {awg.I02} dişi uçlu tel): {bag.I02}",
               "Bağlantı tablosu P01 (yalnız sinyal teli, madde 4, {awg.P01}): {bag.P01}",
               "Bağlantı tablosu P02 (yalnız sinyal teli, madde 4, {awg.P02}): {bag.P02}"],
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
        is_="Kabuk takılmadan önce burada dur. Bağlarken akü ayrık (XT60 açık). Kablo kimlikleri, uçlar, kesit ve sigortalar tek "
            "kaynakta: `planlama/adim3/kablolar.md` (kimlikler aşağıda parantez içinde); sırayla:\n"
            # P10.7b2d-A düzeltme turu 1 (F10l-kontrol D1): bara (köprüler, G05) ilk alt adım: her pabuç köprü uçlarının ve G05'in
            # üstüne gelir (bara-pabuc.not "büyük akımlı (12 AWG) pabuçlar yığının altında"; baralar B5a'da panelde). Paragraf başındaki
            # "N." / "Nb." çapadır: rehber_metin._demet_bol siler, "madde N" göndermelerini alt adım numarasına çevirir.
            # düzeltme turu 2 (F10l-kontrol-2 D1): kart XT60'tan önce geldiği için G05'in akü ucu açıkça (kablolar.json G05 uc_a
            # "XT60 (robot tarafı) · −", lehim; akü ↔ XT60 akü tarafı G01). N2: "(N.)" → "(N numaralı)", değer aynı.
            "2. Toprak (G05, {awg.G05}): akü − → yıldız barasının ortadaki ({saplama.G05} numaralı) saplaması. "
            "G05'in akü ucu XT60'ın robot tarafındaki − ucudur (lehim): akünün kutbuna doğrudan bağlama, akü kutupları bantlı kalır (akü ile "
            "XT60'ın akü tarafı arası G01, madde 1). İki bara da M5 saplama üstünde "
            "halka pabuç yığını: saplama başına en çok {saplama.pabuc} pabuç, büyük akımlı pabuçlar yığının altında, üstte düz pul + yaylı "
            "pul; WAGO yok. Yıldız barası (toprak) {saplama.sayi} M5 saplama: saplamalar {kopru_adet.yildiz} adet {kopru_renk.yildiz} "
            "{kopru.yildiz} köprüyle (≈ {kopru_boy.yildiz}, iki ucu sarı halka pabuç) birbirine zincir bağlanır. Yerleşim: saplama "
            "{saplama.G12|G14|G15} G12 / G14 / G15, {saplama.G13|G16} G13 / G16, {saplama.G05|G06} G05 (akü) / G06, "
            "{saplama.G17|G18} G17 / G18, {saplama.G20|G22} G20 / G22 dönüşleri. Anahtarlı bara (+) {saplama.bara} M5 saplama: "
            "saplamalar {kopru_adet.bara} adet {kopru_renk.bara} {kopru.bara} köprüyle (≈ {kopru_boy.bara}, iki ucu sarı halka pabuç) "
            "birbirine zincir bağlanır; bütün saplamalar köprüyle birbirine bağlı. Anahtarlı bara yerleşimi (kalın pabuç altta): "
            "saplama {bsaplama.G12|G14|G15} G12 / G14 / G15, {bsaplama.G13|G16} G13 / G16, {bsaplama.G09|G11} G09 / G11 (baraya "
            "gelen iki hat: röle K1 ve ön şarj kartı), {bsaplama.G22} G22; saplama başına en çok {saplama.pabuc} pabuç, köprü uçları "
            "dahil (`planlama/adim3/kablolar.json` yerleşim kaydı). "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.1; K64 a): baralar ve tutucu modelde yok; karedeki soluk sarı çizgi SV3 (B5a şeması)
            "Karede görünmez: iki bara ve tutucuları modelde yok (tutucu CAD paketinde gelecek, K64 a); baralar güç panelinde (arka "
            "kat, B5a). Karedeki soluk sarı çizgi B5a'da bağlanan SV3'ün şemasıdır, bu alt adımın kablosu değil.\n"
            "1. Ana hat ({awg.G01|G02|G03|G04}): akü + → XT60 (G01, akü tarafı) → ana sigorta {a.ana-sigorta} ({bicak.ana-sigorta} bıçak, "
            "kablolu yuva; XT60'ın robot tarafından yuvanın girişine G02) → ana anahtar (yuvanın çıkışından G03) → sigorta kutusu "
            "(anahtarın çıkışından kutunun girişine G04). "
            "Ana anahtar henüz yerinde değil (F1'de etek plakasının altına takılır): G03 ve G04'ün anahtar uçlarını halka pabuçlu ve "
            "bantlı bırak; şarj kolunun + ucu (G06) ve akü ölçüm teli (G07) de anahtara gider; dördü F1'de bağlanır. "
            "Şarj kolu (G06, {awg.G06}): + ucu ana sigortanın yük tarafından, ana anahtarın giriş saplamasına gidecek (G03 ile aynı saplama, "
            "mavi {vida.ana-anahtar} halka pabuç, ana anahtarın saplama ölçüsü kablajda teyit; F1'de takılır); {a.hat-sarj} {bicak.hat-sarj} hat sigortasının kapaklı yuvası {yer.hat-sarj}, "
            "kuyruğuna lehim + makaron; öbür uç etekteki XT60E-F (dişi) şarj girişine (F1); − ucu yıldız barasının {saplama.G06} numaralı saplamasına, madde 2'de takılan G05'in üstüne (mavi pabuç). Kolu akü XT60'ının robot tarafından, ana hattan al: akü XT60'tan ayrılınca "
            "kol da enerjisiz kalır (rehberdeki \"akü ayrık = enerjisiz\" düzeni buna dayanır; ana anahtar kapalıyken şarj edilir, karar "
            "O-17). Uç bantlı bırakılır, F1'de etekteki şarj girişine bağlanır; {a.hat-sarj} sigortası takılmaz (F1 aşama 1). "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.2): uçların yeri (taban-analiz.json merkezleri; sağ / sol önden bakana göre)
            "Karede yer: ana sigorta yuvası güç panelinde sağda, sigorta kutusu panelin arka ortasında; ana anahtar karede yok (F1'de "
            "sol arka köşeye takılır).\n"
            # P10.7b2a (K63; orkestratör kararı 5, 15.11): G07 ve kaynak ucundaki direnci (kablolar.json G07, koruyucular.R-aku-olcum)
            "Akü ölçüm teli (G07, {awg.G07}; akü ölçüm bölücüsünün {ohm.aku_olcum} üst direnci kaynak ucunda): arayüz kartı ucunu "
            "bölücünün orta noktası pedine lehimle, makaronla ört. "
            # düzeltme turu 1 (F10i-kontrol A1): makaron lehimden önce, direnç bacağı açıkta değil, gerginlik giderme
            # düzeltme turu 2 (F10i-kontrol-2 §5 G07): yalıtımlı pabucun kovanına lehim PVC kılıfı eritir: kılıf önce çıkar, bacak
            # kovana sıkılır, sonra lehim; makaron soğuyunca kovanın üstüne (kablolar.json G07 uc_kuyrugu; orkestratör kararı 15.11)
            "Öbür uçta (G07'nin ana anahtar ucu), lehimden önce: kırmızı {vida.ana-anahtar} halka pabucun PVC kılıfını çıkar (ana "
            "anahtarın saplama ölçüsü kablajda teyit); yalıtımlı pabucun kovanına lehim kılıfı eritir. Sonra lehimden önce makaronu "
            "G07'nin teline geçir: boyu direnci, iki bacağını ve pabucun kovanını birlikte örtecek kadar (lehimden sonra geçmez). "
            # P10.7b2b (F10i-kontrol-3 A5): makaron lehim yerinden uzakta bekler, ısıdan erken büzülmesin
            "Makaronu lehim yerinden uzağa, telin geri tarafına it ve iki lehim bitip soğuyana kadar orada tut (lehimin ısısı "
            "yakındaki makaronu erken büzer, sonra kaymaz). "
            "Direnci telin ucuna lehimle. Direncin öbür bacağını pabucun kovanına sık (pabuç pensesiyle), sonra kovana lehimle: "
            "direnç ile pabuç arasında tel kalmaz. Soğuyunca makaronu direncin ve kovanın üstüne çek ve ısıtarak büz: direnç, iki "
            "bacağı ve kovan tümüyle örtülü, açıkta bacak kalmaz (G07'nin direnci {yer.R-aku-olcum}). Gerginlik giderme: G07'yi direncin tel tarafında, ana anahtara giden G04'e kablo bağıyla tuttur; "
            "teli çekince yükü kablo bağı taşır, direncin gövdesi ve bacakları değil (bağın yeri kaynakta yok, kablajda teyit). "
            "Pabucu bantlı bırak: F1'de ana anahtarın çıkış saplamasına, G04'ün üstüne takılır. "
            "Pabuç saplamaya girmeden, akü ayrıkken multimetrenin direnç kademesiyle pabuç ile akü ölçüm bölücüsünün orta noktası "
            "arasını ölç: {ohm.aku_olcum}'a yakın okunur (kontrol). "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.3)
            "Karede yer: arayüz kartı elektronik katında (ön kat), önden bakınca solda; G07'nin öbür ucu F1'de sol arka köşedeki ana "
            "anahtara gider.\n"
            "3. F1 {a.F1} → röle K1 kontağı ({kontak.K1}; soketin kuyruk numaraları kablajda teyit: G08 sigorta kutusundan girişe, G09 "
            "çıkıştan anahtarlı baranın {bsaplama.G09} numaralı saplamasına; {awg.G09}); F1 → ön şarj kartı → anahtarlı bara (G10, G11; {awg.G11}). "
            # düzeltme turu 1 (F10i-kontrol A2): K2'nin pim bakışı 12 AWG lehiminden önce
            "Ön şarj kartında, lehimden önce K2'nin pimlerini bul: akü ayrıkken röle gövdesindeki şemaya bak, multimetrenin süreklilik "
            # düzeltme turu 2 (F10i-kontrol-2 B23): pim okuması kayıttaki kontak uçlarından (anahtarlar.K2-kontak.uclar)
            "kademesinde (bobin boşta) {kontak.K2:giris} ile {kontak.K2:bos} arası öter, {kontak.K2:giris} ile {kontak.K2:cikis} "
            "arası ötmez (pim yeri kablajda teyit). Sonra G10'u K2 "
            "kontağının girişine lehimle, ön şarj direnci ({ohm.onsarj}) çıkış ucunda, G11 direncin öbür bacağından anahtarlı baranın "
            "{bsaplama.G11} numaralı saplamasına; K2'nin "
            # düzeltme turu 2 (F10l-kontrol-2 D2): CAD Kablo yolu 3 tek parça (CAD_ESLEME[3] G12 dahil), G12 kısmı bu karede görünür
            "uçları {kontak.K2} (röle pimlerinin yeri kablajda teyit: röle gövdesindeki şema). Karede Kablo yolu 3'ün baradan sol "
            "BTS7960B'ye giden kısmı (G12) da görünür; o uç madde 3b'de bağlanır. Karede yer: röle K1 güç panelinde önden bakınca "
            "solda, ön şarj kartı panelin ön kenarında aynı yanda.\n"
            # P10.7b2d-A düzeltme turu 1 (F10l-kontrol D1, N4): bara çıkışları kendi alt adımında; G12–G15'in bara uçları (eskiden
            # "Alt kat kartlarının öbür uçları"nda) burada, G16'dan önce: saplama 1 ve 2'de 12 AWG pabuç (G12, G13) altta, G14 / G15 /
            # G16'nın 16 AWG yuva kuyruğu üstte (kablolar.json bara-pabuc yerlesim; rehber_denetim bara_uc_denetle U3)
            "3b. Baradan: iki BTS7960B (G12, G13; {awg.G13}); mini hat sigortalarıyla XL4016 A ve B ({a.hat-A|hat-B}; "
            "G14, G15), {awg.G14|G15}. G14, G15 ve G16'nın "
            "hat sigortası yuvası {yer.hat-A|hat-B|hat-C}: yuvanın bir kuyruğu mavi M5 halka pabuçla bara saplamasına, öbür kuyruğu "
            "kablonun teline lehim + makaron; XL4016 ucunda sigorta yok. "
            "G12–G15'in alt kat ucu B3'te bağlandı; burada B3'te etiketli bırakılan bara uçlarını bağla, kalın pabuç altta: önce G12'nin "
            "+ ucunu anahtarlı baranın {bsaplama.G12} numaralı, G13'ünkünü {bsaplama.G13} numaralı saplamasına, − uçlarını yıldız barasının "
            "{saplama.G12} ve {saplama.G13} numaralı saplamasına; sonra G14 ve G15'in + uçlarını hat sigortası yuvasıyla anahtarlı baranın "
            "{bsaplama.G14|G15} numaralı saplamasına, − uçlarını yıldız barasının {saplama.G14|G15} numaralı saplamasına (her biri G12'nin üstüne). "
            # düzeltme turu 1 (tamlık, emir kipi): G16 açık bağlama cümlesi
            "XL4016 C'yi de mini hat sigortasıyla ({a.hat-C}) baradan güç panelindeki IN+ / IN− klemensine bağla (G16, {awg.G16}); "
            "G16'nın + ucu anahtarlı baranın {bsaplama.G16} numaralı, − ucu yıldız barasının {saplama.G16} numaralı saplamasına, G13'ün üstüne. "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.5): G14 / G15 Kablo yolu 5 / 7'nin parçası (rehber_kablo.CAD_ESLEME), K2 32.1'de
            "G14 ve G15'in çizgisi Kablo yolu 5 ve 7'nin parçasıdır: K2 madde 1'in karesinde görünür. Karede yer: iki BTS7960B alt "
            "katta, sol olan önden bakınca solda, sağ olan sağda; XL4016 A ortada, B solda; XL4016 C güç panelinde (B5a).\n"
            "PC817 #2 algı teli (G22, {awg.G22}): {yer.hat-G22} {a.hat-G22} "
            "{bicak.hat-G22} hat sigortası; G22'nin yuvasının bara kuyruğu anahtarlı baranın {bsaplama.G22} numaralı saplamasına. "
            # düzeltme turu 1 (F10i-kontrol Ü1): kart ucu ve kutup (kablolar.json G22 damarları: + → IN2 +, IN2 − → yıldız barası)
            "G22'nin kutbu {kutup.G22}: + damarını (hat sigortasından gelen) arayüz kartındaki PC817 modülünün {uc.G22:+:b} "
            "klemensine, − damarını modülün {uc.G22:−:a} klemensinden yıldız barasına bağla; − damarının yıldız ucu 5 cm {ara.G22} "
            "siyah ara parçaya lehimli, ara parça kırmızı pabuçla yıldız barasının {saplama.G22} numaralı saplamasına. Bağlamadan önce modülün "
            "üstündeki IN2 + / IN2 − yazısını oku: ters bağlanan G22'de giriş LED'i yanmaz, bara gerilimliyken PC817 #2 "
            "({gpio.BARA_DURUM}) LOW'a düşmez ve ESP32 devreye almada hata verir; modülün girişinde ters gerilim koruması olup olmadığı "
            "belgede yok (kablajda teyit), ters bağlıyken enerji verme. "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.6)
            "Karede yer: PC817 modülü arayüz kartının üstünde, arayüz kartı elektronik katında önden bakınca solda; anahtarlı bara "
            "karede görünmez (modelde yok, güç panelinde).\n"
            "4. Sigorta kutusundan (standart bıçak): F3 {a.F3} kafa hattı (G17, {awg.G17}; uç direk dibinde bırakılır), F4 {a.F4} XL4016 çevre (G18, "
            "{awg.G18}; çevre çıkışı G19, {awg.G19}, OUT+ ucunun dibinde {a.hat-cevre} {bicak.hat-cevre} hat sigortası), F5 {a.F5} acil stop (A01, {awg.A01}; mantar F1'de "
            # P10.7b2e (K52 a, 16.11): regülatör B5a'da panelde; G20 panel içinde kalır, direğe G21 çıkar (K2)
            "takılır, uç bantlı), F6 {a.F6} göğüs ekranı dalı (G20, {awg.G20}): kutudan, B5a'da güç paneline takılan göğüs ekranı "
            "regülatörünün girişine (K52 a); G20'nin iki ucu da panelde, göğüs regülatörünün direğe çıkan çıkışı K2'de. "
            # P10.7b2d-A düzeltme turu 1 (F10l-kontrol D1): G17, G18, G20'nin taban uçları tek alt adımda (eskiden 17.7 / 17.9 da bağlatıyordu)
            "G17, G18, G20 ve A01'in kutu ucunu kendi yuvasının çıkışına bağla (G17 F3, G18 F4, A01 F5, G20 F6); G17, G18 ve G20'nin − "
            "ucunu yıldız barasına: G17 ve G18 "
            "{saplama.G17|G18} numaralı, G20 {saplama.G20} numaralı saplamaya (G18'in öbür ucu B3'te XL4016 çevreye bağlandı). "
            "G20'nin regülatör ucunu regülatörün giriş klemensine bağla ({kutup.G20}; kart üstü IN+ / IN− yazısına göre). "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.7, A): vurgulu Kablo yolu 9'un eski kısmı (KABLO_AD[9]) ve öbür kabloların karesi
            "Karede vurgulu çizgi Kablo yolu 9'dur (G18): XL4016 çevreden sonraki kısmı eski çizimdir (doğrudan ESP32'ye), uygulanmaz; "
            "çevre çıkışı G19 alt adım 17.9'da arayüz kartına bağlanır. A01'in çizgisi madde 5'in, G17'ninki K2 madde 3'ün, göğüs "
            "ekranı hattının şeması K2 madde 7'nin karesinde.\n"
            "5. Acil stop ve röle sürücüleri (yeşil, A01–A05 {awg.A01|A02|A03|A04|A05}; E3, E9): mantar NC çıkışı → acil stop düğüm kartı (güç panelinde küçük pertinaks "
            "parçası: iki adet 2 pin 5,08 mm vidalı klemens, dört ucu kart üstünde {kopru.A02} tel köprüyle lehimli) → röle K1 bobini (86; "
            "A02) ve ön şarj kartındaki K2 bobini (+; A04). Bobinlerin − uçları arayüz kartına: K1 85 → BC337-40 #1 kollektörü (A03; "
            "{gpio.ROLE_K1} sürer), K2 − → BC337-40 #2 kollektörü (A05; {gpio.ROLE_K2_ONSARJ} sürer). Her sürücüde {ohm.seri} seri taban direnci ve {ohm.taban} taban → GND. "
            "Geri tepme diyotları 1N4007: K1'de soketin 86 / 85 kuyruklarının üstünde lehim + makaron, katot (bantlı uç) 86'ya, anot "
            "85'e; K2'de ön şarj kartında bobin klemensinin üstünde, katot bobin + ucuna. PC817 #1 girişi düğümden (A06, {awg.A06}; {gpio.ACIL_STOP_DURUM} "
            "okur): A06'nın + ucunu {parca.A06:+:a} noktasına, yani acil stop düğüm kartında bir klemensin kuyruğuna (kart altı) "
            "lehimle, modülün IN1 + klemensine bağla; "
            "− ucunu modülün IN1 − klemensinden arayüz kartının GND pedine lehimle (makaron). Mantar ile düğüm arasında elde taşınan acil stop için ayrılan iki uçlu yer (Ö4; 2 pin 5,08 mm klemens) "
            "zincirin kendi teliyle (A01, A02) aynı kesitte ({awg.A01|A02}) kısa bir tel köprüyle kapalı durur; köprü yoksa "
            "röle çekmez. Elde taşınan acil stop yok (K60 A): köprü kalıcıdır, ileride kumandalı acil stop sökmeden bu yere eklenebilir; demoda mantarın yanında bir kişi durur. "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.8)
            "Karede yer: röle K1 güç panelinde önden bakınca solda, ön şarj kartı panelin ön kenarında aynı yanda, arayüz kartı "
            "elektronik katında solda; acil stop düğüm kartı karede görünmez (modelde yok); mantar F1'de sağ arka köşeye takılır.\n"
            # P10.7b2d-A düzeltme turu 1 (F10l-kontrol D1): G12–G15'in bara uçları madde 3b'de, G18'in uçları madde 4'te (tek yerde)
            "Alt kat kartlarının (iki BTS7960B, XL4016 A / B / çevre) klemens uçları B3'te, kat ve güç paneli gelmeden bağlandı; "
            "G12–G15'in bara uçları madde 3b'de, G18'in kutu ve yıldız uçları madde 4'te bağlandı. Burada "
            "B3'te etiketli bırakılan öbür uçları yerlerine bağla: G19'u arayüz kartının çevre 5 V / GND klemensine; SV1'i "
            "dağıtım kartı A'nın, SV2'yi dağıtım kartı B'nin V+ / GND giriş klemensine ({kutup.SV1|SV2}). Alt kat klemensine burada "
            "uzanma: kart üstünden elektronik katına 69 mm, yanda 40–150 mm (sıra kontrolü). "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.9): SV1 / SV2 Kablo yolu 5 / 7'nin parçası (CAD_ESLEME), K2 32.1'de
            "SV1 ve SV2'nin çizgisi Kablo yolu 5 ve 7'nin parçasıdır: K2 madde 1'in karesinde görünür. Karede yer: XL4016 A alt katta "
            "ortada, B solda, çevre sağda; dağıtım kartı A elektronik katının ön kenarında sağda, B solda.\n"
            # P10.7b2a: sinyal kablolarının kimlikli talimatı (kablolar.json B01, B02, N01, N02, Q01, Q02, Q03)
            "6. Enkoder, BTS sinyal ve sonar kabloları (dişi uçlu sinyal teli, O-4 r; pinler `planlama/adim3/kablolar.md`'de, kart üstü yazıya "
            "göre bağla): arka sol motorun enkoderi (N01) ve arka sağ motorun enkoderi (N02) → ESP32 taşıyıcı başlığı (VCC → 3V3, GND, A, "
            "B). Sol BTS7960B'nin sinyal başlığı (B01) ve sağınki (B02) → ESP32 (IN1, IN2) ve arayüz kartı (EN1 + EN2 → BTS EN düğümü, "
            "IS1 + IS2 → IS bölücüsü, VCC → çevre 5 V, GND). Sonarlar: sağ (Q01), orta (Q02) ve sol (Q03) sonarın VCC'sini arayüz "
            "kartının çevre 5 V'una, Trig'ini PCA9685'e, Echo'sunu arayüz kartındaki sonar bölücüsüne, GND'sini arayüz kartının GND'sine "
            "bağla. Motor uçları B3'te BTS7960B'ye bağlandı. Acil stop ucunu bırak: mantar F1'de takılır. "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.10, A 32.4): Kablo yolu 12 (B01) bu alt adımda.
            # P10.7b2f (F10m-kare-inceleme § 4.1): yolun direğe çıkan eski kısmı rehberde kırpıldı (rehber_kablo.CAD_KIRP), karede yok
            "Karede vurgulu Kablo yolu 12 (B01) tabanda kalır: sol BTS7960B'den ESP32 taşıyıcısına. ESP32'nin direğe çıkan kablosu "
            "ESP32 USB'dir (U06, K2 madde 4). Karede yer: ESP32 "
            "taşıyıcı ve PCA9685 elektronik katında önden bakınca sağda, arayüz kartı solda; sonarlar ön yüzde.\n"
            # P10.7b2a (orkestratör kararı 6): kafa servolarının sinyal köprüsü (kablolar.json P03)
            # düzeltme turu 1 (F10i-kontrol Ü3): P03 yalnız sinyal, V+ teli takılmaz (elektrik.md:226; kablolar.json P03 not)
            "7. Direğe çıkacak hatların taban kısmını da burada bağla. Kafa servolarının sinyal köprüsünü (P03), yalnız sinyal teliyle, "
            "PCA9685'in kafa pan ve tilt kanallarının sinyal pinlerinden dağıtım kartı C'nin pan / tilt sinyal girişlerine bağla. "
            "PCA9685'in V+ pinine tel takma; 3 telli hazır kablo kullanırsan V+ damarını iki ucundan kes, makaronla yalıt (B6a madde 4: "
            "V+ teli XL4016 C'nin çıkışını A ve B'ninkilere paralel bağlar). Kafa 12 V'un (G17) taban ucu ve panel içinde kalan göğüs "
            "ekranı dalı (G20) madde 4'te bağlandı; ESP32 USB'nin (U06) taban ucunu bağla. Servo uzatmaları (A / B / kafa) K2'de dağıtım "
            "kartlarının çıkışına takılır. Yukarısı K2'de. "
            # P10.7b2e kısım 2 (F10l-kare-inceleme 17.11): karede vurgu yok, nedeni ve yer
            "Bu alt adımın kabloları karede vurgulu değil: P03'ün çizimi yok (bağlantı tablosu aşağıda), U06'nın şeması K2 madde 4'ün "
            "karesinde. Karede yer: PCA9685 ve ESP32 taşıyıcı elektronik katında önden bakınca sağda; dağıtım kartı C güç panelinde "
            "(B5a, modelde yok).\n"
            "8. K1'de enerji verilmez: ana anahtar ve acil stop mantarı F1'de takılır. Bu adımda takılan köprüler: Ö4 "
            "yerindeki kısa tel köprü (madde 5), acil stop düğüm kartındaki (A02, A04) {kopru.A02} tel köprü (madde 5), yıldız barasının "
            "saplamaları arasındaki {kopru_adet.yildiz} adet {kopru.yildiz} köprü (madde 2), anahtarlı baranın saplamaları arasındaki "
            "{kopru_adet.bara} adet {kopru.bara} köprü (madde 2) ve KT3 bakışında kutu ayrı girişli çıkarsa yuva girişlerine giden ara "
            "kablolar (kontrol listesi). Bunların dışında mantarın kendi uçları ve ana anahtarın uçları hiçbir zaman köprülenmez; akü XT60 ayrık kalır, boştaki ana hat uçları gerilimsiz ve bantlı. XL4016 ayarı ve PC817 ölçümü kartlar takılmadan "
            "önce tezgâhta, akım sınırlı tezgâh kaynağıyla yapılır (kontrol; B3, B5a, B6a). İlk enerji iki aşamalı: F1 sonunda kafasız "
            "(aşama 1: ana anahtar, BMS, mantar; F1 takılı değil, anahtarlı bara enerjisiz), devreye alma ve motor yön testi F5'te (aşama 2). "
            "Bu sıra kaynakta yok, doğrulanmadı.",
        baglanti_md="M5 halka pabuç (saplama düğümleri), 2 pin 5,08 mm vidalı klemens (acil stop düğüm kartı), lehim + makaron, kablo bağı. "
                    "Yıldız barası ve anahtarlı bara köprüleri: {kopru_adet.toplam} adet {kopru.yildiz|bara} köprü (yıldız "
                    "{kopru_adet.yildiz} {kopru_renk.yildiz}, anahtarlı bara {kopru_adet.bara} {kopru_renk.bara}, her biri ≈ "
                    "{kopru_boy.yildiz|bara}) ve uçlarına {kopru_pabuc.toplam} sarı halka pabuç. "
                    "Kablo listesi ve uç türleri: `planlama/adim3/kablolar.md` (adet ve boy orada)",
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
            "İki baranın köprüleri takılı: yıldız barasında {kopru_adet.yildiz} adet {kopru_renk.yildiz} {kopru.yildiz}, anahtarlı barada "
            "{kopru_adet.bara} adet {kopru_renk.bara} {kopru.bara} köprü, her ucu sarı halka pabuçla. Akü ayrıkken multimetrenin süreklilik "
            "kademesiyle her baranın ilk ve son saplaması arası öter (direnç sıfıra yakın); ötmezse köprü eksik ya da gevşek",
            "Ö4 yerindeki 2 pin klemenste kısa tel köprü takılı (A01 / A02 ile aynı kesit, {awg.A01|A02}; köprü yoksa röle çekmez); ilk enerjide (F1 aşama 1) mantar "
            "bırakılmışken PC817 #1 ({gpio.ACIL_STOP_DURUM}) LOW okur (HIGH = mantar basılı ya da F5 attı; pin haritası)",
            "İki röle bobinine de ters paralel 1N4007 takılı (MAH-112-C-4 dahili diyot yazmıyor): K1'de katot 86'ya, K2'de katot bobin + "
            "ucuna; bantlı uç doğru yerde",
            "Röle sürücüleri arayüz kartında: BC337-40 #1 (K1, {gpio.ROLE_K1}) ve #2 (K2, {gpio.ROLE_K2_ONSARJ}), her birinde {ohm.seri} seri ve {ohm.taban} taban → GND",
            "Ana hat ve toprak düğümleri (G01–G05, {awg.G01|G02|G03|G04|G05}) yalnız M5 saplama + halka pabuçta (saplama başına en çok {saplama.pabuc} pabuç). "
            "Vidalı klemensli (5,08 mm) düğümler: kafa giriş kartı, acil stop düğüm kartı ve arayüz kartının çevre 5 V düğümü "
            "(`planlama/adim3/kablolar.json` klemens yerleri). İnce telli uç vidalı klemense kalaylanmadan, bükülerek girer (yüksük varsa yüksük)",
            # P10.7b2a: K63 kontrol maddeleri (G07, K2 kontağı, hat sigortası yeri, anahtarlı bara yerleşimi)
            "Akü ölçüm teli (G07): pabuç henüz saplamada değilken, akü ayrık, multimetrenin direnç kademesinde pabuç ile arayüz "
            "kartındaki akü ölçüm bölücüsünün orta noktası arası {ohm.aku_olcum}'a yakın; direnç, iki bacağı ve pabuç kovanı makaronla "
            "tümüyle örtülü (açıkta bacak yok), tel direncin yanında G04'e kablo bağıyla tutturulu (çekince direnç gerilmiyor), pabuç "
            "bantlı (F1'de ana anahtarın çıkış saplamasına)",
            "Ön şarj kartında K2'nin uçları {kontak.K2}: G10 girişte, ön şarj direnci çıkışta. Pim yeri G10 lehimlenmeden önce (madde 3) "
            "röle gövdesindeki şemayla ve akü ayrıkken multimetrenin süreklilik kademesiyle bakıldı (bobin boşta: G10'un pimi ile boş "
            "pim arası öter, G10'un pimi ile direncin pimi arası ötmez)",
            # düzeltme turu 1 (F10i-kontrol Ü1, Ü3)
            "G22'nin kutbu: + damarı (hat sigortası tarafı) PC817 modülünün {uc.G22:+:b} klemensinde, − damarı {uc.G22:−:a} "
            "klemensinden yıldız barasında; akü ayrıkken multimetrenin süreklilik kademesiyle {uc.G22:−:a} ile yıldız barası arası öter, "
            "{uc.G22:+:b} ile yıldız barası arası ötmez",
            "PCA9685 V+ boş (P03): akü ayrıkken multimetrenin süreklilik kademesiyle PCA9685'in kanal başlığının V+ pini ile dağıtım "
            "kartı C'nin V+ barası arasında süreklilik yok (ötmemeli; ölçü ucu klemense değil kanal başlığının V+ pinine; B6a'da A ve B "
            "için de bakıldı)",
            "Anahtarlı bara: G14, G15, G16 ve G22'nin hat sigortası yuvaları bara ucunda, sigortaları takılı değil; saplamalardaki "
            "yerleşim madde 2'deki gibi (G09 ve G11 aynı saplamada), her saplamada en çok {saplama.pabuc} pabuç",
            "A06'nın − ucu arayüz kartının GND pedinde; X01, B01, B02, N01, N02, Q01, Q02, Q03 ve P03'ün uçları kart üstü yazıyla "
            "kablolar.md'deki uca eşleşti",
            "Teslimde bakılacaklar (`planlama/d158/kablo-tablosu-gunluk.md` §16.7, §17.7): alçak profil mini sigortalar (çevre {a.hat-cevre}, şarj {a.hat-sarj}) \"Mini/Micro\" "
            "yuvaya oturuyor; K1 soketinin kuyruk kesiti okundu, G08 / G09'un {awg.G08|G09} teline eklendi; 5,08 mm klemensin kesit aralığı okundu (A06 / G07 "
            "lehimli uçlarına yeniden bakılır); G22'nin yıldız ucu 5 cm {ara.G22} ara parça + kırmızı pabuç; akü dönüşü (G05) yıldızın {saplama.G05} numaralı "
            "saplamasında; T8 E ve E2 tezgâh kısa devre denemeleri yapıldı (`planlama/d158/testler/T8-servo-hatlari.md` E: bir servo uzatmasının "
            "ucunda ve SV1–SV3'te, servolar sökülü, en çok 2 s, yanmaz zemin): XL4016 akımı kesiyor ya da düşürüyor, kablo 80 °C'nin altında "
            "(kalırsa istisna düşer, tasarıma); K04'ün (kafa ekranı Power USB) üstündeki kesit yazısı okundu: 24 AWG'den inceyse ya da yazı "
            "yoksa {yeniden.K04} + micro B fişle yeniden yapılır. Seçenek: kollu WAGO 221-413 (ince telli alır) alınabilir, karar Ahmet'in; tablo "
            "vidalı klemensle gider",
            "Teslimde (KT3): sigorta kutusunun yuvaları ortak giriş barasında mı: akü ayrıkken multimetrenin süreklilik kademesiyle kutunun "
            "giriş ucu ile her yuvanın giriş tarafı arasına bak (altısı da öterse ortak bara). Biri ötmezse kutu ayrı girişli: her yuvaya "
            "kutunun üstünde olabildiğince kısa, kutunun giriş kablosuyla (G04) aynı kesitte {awg.G04} ara kablo, hepsi tek giriş klemensinden yıldız (`planlama/adim3/kablolama-on-kararlar.md` "
            "§3, KT3)",
            "BTS7960B kartının pin adları şemadakinden farklı olabilir: kart üstü yazıya göre bağla",
            "İsim karıştırma: burada K1 / K2 röle adıdır; Kablolama kapısı K1 / K2 ayrı şey",
            "Tezgâhta (arayüz kartı takılmadan, B6a öncesi; akım sınırlı tezgâh kaynağıyla): PC817 modülü 3,3 V'ta ölçüldü: LOW < 0,4 V, HIGH > 2,5 V; tutmazsa `elektrik.md` E3'teki yedek devre",
            "Akü ayrıkken: bara kapasitesi multimetrenin kapasite kademesiyle ölçüldü (ön şarj değeri için)",
            "İlk açılış ve BMS gözlemi burada değil: F1 \"İlk enerji, aşama 1\"; devreye alma ve motor yön testi F5 \"İlk enerji, aşama 2\"",
            # P10.7b2e kısım 2 (K65, planlama/d158/sag-sol-karari.md): kablolar CAD adıyla (önden bakanın sağı / solu) bağlanır, ESP32
            # yazılımı robotun kendi sağını / solunu kullanır; kurulumda yakalanır. Komutlar kod/esp32/OKU_BENI.md'den (origin/main
            # 71cf76d, sürüm 0.5.0: "sur" v / w, w rad/s sola +; "odo_sifirla"; "odo" satırı sol / sag tik toplamı)
            # P10.7b2e düzeltme turu 1 (F10m-kontrol D2): test yön kalibrasyonundan (*_MOTOR_TERS / *_ENKODER_TERS, motorlar.cpp,
            # OKU_BENI) sonra; sayaç ölçütü "hangi sayaç değişiyor" (taraf), artıp azalması yön sorusu (ENKODER_TERS).
            # P10.7b2f (F10m-kare-inceleme § 5): test K1'de işaretlenemez (enerji yok); tam metni F5 kontrol listesinde, burada gönderme
            "Sağ / sol kurulum testi bu adımda yapılmaz: F5 \"İlk enerji, aşama 2\" kontrol listesinde (devreye alma ve motor / "
            "enkoder yön testinden sonra)",
        ],
        kablo=["Burada: 12 V ana hat, şarj kolu, toprak, iki motor hattı, çevre 5 V, acil stop, sonar sinyal. Şemada devre sınıfının "
               "renginde (lejant; `planlama/adim3/kablolar.md` renk kuralı); tıklayınca kablo kimliği, iki uç, kesit, sigorta ve acil "
               "stopta enerjili olup olmadığı",
               "Direk boyunca gidenler K2 listesinde; o hatların taban kısmı da bu adımda bağlanır (şema bölünmedi)",
               "Dokuz hattın (G07, G16, G22, G19, B02, N01, N02, Q01, Q02) çizimi gösterim şemasıdır (`lale158/kablo_yolu_taban.py`): "
               "çarpışma taramasından geçmedi, parça sayısına girmez, boy ölçümü değildir. Kat ve alt plaka geçişleri modeldeki "
               "yerlerdir (ön kat kesiği, arka kablo deliği); kart üstündeki klemens yeri ve kartların arasındaki çizgi tahmin. Anahtarlı "
               "baranın yeri yaklaşık (modelde yok, röle yanından çizildi). Kabloyu çizgiye değil, kartlara ve klemenslere bakarak döşe",
               # P10.7b2c ikinci yarı (ajan B): P03 bağlantı tablosu (rehber_kablo.BAGLANTI_TABLOSU)
               # P10.7b2c düzeltme turu 1 (F10k-kontrol D3): kartın yeri (kablolar.json karar P7b2a-6); kayıttaki ad değişmedi
               "Bağlantı tablosu P03 (yalnız sinyal teli, madde 7, {awg.P03}): {bag.P03}. Dağıtım kartı C (kafa): kart güç panelinde, "
               "XL4016 C'nin yanında; adındaki \"kafa\" beslediği pan / tilt servolarıdır. Dağıtım kartı C modelde yok, yeri çizilmez; "
               "kart üstündeki pan / tilt giriş pininin numarası kayıtta yok: kart üstü yazıya göre bağla",
               "Kablo listesi (uçlar, kesit, sigorta, sonlandırma): `planlama/adim3/kablolar.md` (tek kaynak `kablolar.json`); boy için tablodaki tahmin kuralı"],
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
            "Her iki 5 V çıkışına bir P6KE6V8A TVS (satın alma listesinde 2 adet, `planlama/maliyet.json`): SY8205 → QLED hattındaki modelde var, "
            "D24V50F5 → Pi hattındaki bugün modelde ve BOM'da yok, sonraki CAD paketinde eklenecek (K51 a). TVS'ler tek yönlü; gövdedeki renkli bant katot ucudur (Vishay P6KE veri sayfası; "
            "`planlama/adim3/kablolar.json` tvs). Her P6KE6V8A'yı çeviricinin çıkış uçlarına lehimle: D24V50F5'te {yon.P6KE6V8A-pi}, "
            "SY8205'te {yon.P6KE6V8A-ekran}. "
            # düzeltme turu 1 (F10i-kontrol A13): çift yönlü tipte bant yoktur, ayırt etmek için gövde baskısı (Vishay belge 88369)
            # düzeltme turu 2 (F10i-kontrol-2 §5 TVS): "sonu A" muğlaktı (…CA da A ile biter)
            "Takmadan önce gövde baskısını oku: sonu yalnız A (ör. P6KE18A) tek yönlüdür, renkli bandı katottur; sonu CA (ör. P6KE18CA) "
            "çift yönlüdür, bandı yoktur (Vishay P6KE veri sayfası). CA baskılı ya da bantsız TVS'i takma (kablajda teyit).\n"
            "Kafa giriş kartı (P6KE18A üstünde küçük pertinaks parçası): P6KE18A'yı kartın + ve − uçları arasına lehimle, "
            "{yon.P6KE18A}; baskısını ve bandını madde 2'deki gibi oku (kablajda teyit). Üç adet 2 pin 5,08 mm vidalı klemens; + uçları ve − uçları kart "
            "üstünde {kopru.K01} tel köprüyle (K01 sonlandırması) lehimli (delikli plaket pedi F3 {a.F3} akım yolu değil). Girişe K2'de kafa 12 V çifti (G17) gelir. "
            # düzeltme turu 1 (tamlık, emir kipi): kart çıkışları bu adımda bağlanır
            "Kartın çıkış klemenslerinden D24V50F5'in girişine (K01) ve SY8205'in girişine (K02) birer çift bağla, {awg.K02}. "
            "D24V50F5 → Pi USB-C (K03, {awg.K03}). PAM8403'ün 5 V'u da D24V50F5'ten "
            "(K05, E4; karar K10 a, masa denemesi KT1, geçmezse SY8205). İnce telli uç klemense kalaylanmadan, bükülerek girer "
            "(yüksük varsa yüksük).\n"
            "3. 625ZZ rulmanını sol yanağın yuvasına pres et (tek parça; modelde iç ve dış bilezik ayrı çizili). Tilt hornu bu adımda "
            "yok: E2'de servoya takıldı, kafa E3'te ona iner (`tasarim/freecad/kafa/kafa_rapor.py` montaj sırası).\n"
            "Kafa ekranı (10,1\" QLED), tırnaklar, kamera, ReSpeaker ve PAM8403 bu adımda takılmaz: kabuklarla birlikte E4'te (USB ses "
            "kartı kablajdan çıktı: yedek, takılmaz; E4).",
        baglanti_md="Pi: 4 × M2,5×8 pirinç burç + 4 × M2,5×5 (üst) + 4 × M2,5×8 DIN 912 (alt); D24V50F5, SY8205, TVS: 1 mm çift taraflı "
                    "köpük bant + kablo bağı; 625ZZ pres geçme. M6'daki LCD 4 × M3×6 ve kamera 4 × M2×8 PT bu adımda yok (QLED tırnaklı, kamera E4'te)",
        alet="alyan 2, yan keski",          # F10d: PH1 horn merkez vidası içindi, vida E3'te (adım 30)
        kontrol=["v4 listesi burcu 6 mm plastik diyor, tasarım 8 mm pirinç: Pi yüksekliğini kontrol et",
                 "D24V50F5 → Pi USB-C yaklaşık 10 cm; çeviriciler köpük banda tam oturdu, kablo bağı sıkı",
                 "SY8205 çıkışı yük bağlanmadan, akım sınırlı tezgâh kaynağıyla (12 V, sınır 1 A) ölçüldü: 5 V (kafa ekranı hattı). "
                 "SY8205'te ters kutup koruması yazmıyor: kaynağın kutbunu bağlamadan önce kontrol et",
                 "Tabla geçişi (x −50…−37) boş: boyun kabloları K2'de buradan girer",
                 "Üç TVS'in bantlı ucu (katot) artı hatta: P6KE18A kafa giriş kartının +12 V'unda, iki P6KE6V8A çeviricilerin +5 V "
                 "çıkışında; anotlar GND'de"],
        kablo=["Pi micro HDMI 0 (kafa ekranı) ve micro HDMI 1 (göğüs ekranı) fiş yerleri erişilebilir kalsın",
               "Kafa 12 V'u K2'de boyundan gelir: girişte P6KE18A (modelde yok), oradan D24V50F5 ve SY8205",
               # P10.7b2c ikinci yarı (ajan B): lale158/kablo_yolu_kafa.py
               "Üç hattın (K01, K02, K03) çizimi gösterim şemasıdır (`lale158/kablo_yolu_kafa.py`): çarpışma taramasından geçmedi, "
               "parça sayısına girmez, boy ölçümü değildir. Kafa giriş kartının yeri yaklaşık (modelde yok, boyun geçişinin solunda çizildi); çeviricilerin ve "
               "Pi'nin uç yeri tahmin. Kabloyu çizgiye değil, klemens yazısına bakarak döşe"],
        not_=["İki 5 V hattı birbirine köprülenmez: D24V50F5 Pi'yi, SY8205 kafa ekranını besler. Touch USB uyarısı E4'te "
              "(`planlama/adim3/elektrik.md`)",
              "SY8205 ve QLED hattı P6KE6V8A'sının tabladaki yeri modelde var; Pi hattı P6KE6V8A'sı modelde yok, yeri doğrulanmadı. "
              "TVS yönü kayıttan (`planlama/adim3/kablolar.json` tvs): Vishay P6KE serisi veri sayfası (belge 88369) tek yönlü tipte "
              "renkli bandın katot olduğunu, çift yönlü tipte (CA soneki) işaret olmadığını yazıyor. Satın alınan parçaların üreticisi "
              "bilinmiyor: teslimde gövde baskısı (sonu yalnız A ya da CA) ve bant okunur (kablajda teyit)",
              "QLED akımı 0,9 A varsayım, ölçülmedi: ilk açılışta ölçülür (teslimde bakılacaklar, `planlama/d158/kablo-tablosu-gunluk.md` §16.7)",
              "Kafa giriş kartının klemenslerine ve D24V50F5 / SY8205 klemenslerine giren uçlar teslimde takılıp çekilerek denenir (kesit "
              "aralığı belgede yok; `planlama/adim3/kablolar.md` K02, G17 teyit)"],
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
            "kafadayken tavan vidalarına el ulaşmaz). Masada, sol arka kabuk: PAM8403 yan duvara köpük bant + kablo bağıyla. USB ses "
            "kartı takılmaz: çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür; bu eski tasarımdan kalan görüntüdür, "
            "uygulanmaz. Kartın köpük bandı da yapıştırılmaz; kart yedek parçalarla birlikte saklanır (KT2 geçmezse Pi USB 2'ye; "
            "`planlama/adim3/kablolama-on-kararlar.md` § 5 Ö1). Kabukları kafanın arkasında tut, kabloları kafanın "
            "açık ön tarafından tak: ReSpeaker → Pi USB 1 (U01); ses yolu ReSpeaker 3,5 mm jakı → 10 kΩ / 2,2 kΩ bölücü → PAM8403 sol "
            "girişi (AU1, AU2; bölücü PAM giriş pedlerinin dibinde, kablo üstünde, makaronla); PAM 5 V → D24V50F5 (K05; K10 a). Ses "
            "kablosunu bağlamadan önce 3,5 mm fişin kılıfı ile ReSpeaker USB GND arasında süreklilik ölç (≤ 1 Ω; KT2). Pi USB 2 boş "
            "kalır. Önce sağ kabuğu "
            "arkadan (−z) yerine koy, sonra solu (arkadan ya da soldan): dikey dikişte sağ kabuğun bindirmesi solun altında kalır; sol "
            "önce takılırsa sağ hiçbir düz yönden girmiyor (giriş yolu ölçümü).\n"
            "2. Tabla → arka kabuk rafı 4 × M3×10: yüz tarafı açıkken önden, L alyanla.\n"
            "3. Masada, yüz kabuğu sağ + sol: kamerayı (Camera Module 3) ön duvarın içindeki boss'lara 4 × M2×8 PT ile vidala; lens ekranın "
            "üstündeki Ø9 delikte. 10,1\" QLED (vida deliği yok): camı yüz kabuğu ön duvarının iç yüzüne yasla, cep duvarı yerini gösterir. "
            "4 tırnağı (üst ve alt, x ±85) cam şeridine 1 mm köpük bant üstünden arkadan bastır; her tırnak 1 × M3×6 ISO 7380 ile boss'taki "
            "ısıl gömmeye.\n"
            "4. Yüz kabuğunu kafanın önünde tut, kabloları tak: CSI şeridi (C01) → Pi; QLED HDMI (H01; 30 cm şerit, Pi micro HDMI 0), "
            "Power (K04; SY8205 çıkışı, A ucu kesik micro USB kablo), Touch (U04; Pi USB 4). Touch'ı takmadan önce Notlar'daki ölçümü yap. Sonra yüz kabuğunu önden (+z) yerine koy (giriş yolu: önden serbest).\n"
            "5. Dikişler: boyundan gelen uçlar (kafa 12 V, göğüs HDMI, hub uzatması, hoparlör) K2'de bağlanır: arka kabuğun dikiş "
            "cıvatalarını K2'den sonra sık.",
        baglanti_md="1,58 m: tırnak 4 × M3×6 ISO 7380 → ısıl gömme + 4 köpük bant (1 mm); kamera 4 × M2×8 PT; ReSpeaker 3 × M2×8 PT (vida "
                    "tipi varsayım); PAM8403 köpük bant + kablo bağı; tabla → arka kabuk rafı 4 × M3×10 DIN 912 → ısıl gömme; "
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
                 "ReSpeaker ve PAM8403 yerinde; kablo bağları fişleri zorlamıyor; USB ses kartı takılmadı (yedek), Pi USB 2 boş",
                 "Ses kablosu bağlanmadan: 3,5 mm fiş kılıfı ↔ ReSpeaker USB GND sürekliliği ≤ 1 Ω (KT2); bölücü 10 kΩ / 2,2 kΩ PAM giriş "
                 "pedlerinin dibinde, makaronlu",
                 "Kafa pan ve tilt'te kabuğa sürtmüyor",
                 "Dikişler aralıksız, kablo sıkışmadı (dikiş cıvataları K2'den sonra)"],
        kablo=["Kafa içi: HDMI şerit Pi micro HDMI 0 → QLED, Touch Pi USB 4 → QLED, Power SY8205 → QLED, CSI Pi → kamera",
               "Ses: ReSpeaker → Pi USB 1 (U01), ReSpeaker 3,5 mm → 10 kΩ / 2,2 kΩ bölücü → PAM8403 sol girişi (AU1, AU2), PAM 5 V → "
               "D24V50F5 (K05). PAM çıkışından hoparlöre giden kablo (AU3) K2'de boyundan iner",
               "Boyun uçları (kafa 12 V, göğüs HDMI → Pi micro HDMI 1, hub uzatması → Pi USB 3, hoparlör) K2'de bağlanır",
               # P10.7b2c ikinci yarı (ajan B): lale158/kablo_yolu_kafa.py
               "Kamera şeridi (C01) ve ses kablosu (AU1, AU2) çizimi gösterim şemasıdır (`lale158/kablo_yolu_kafa.py`): çarpışma "
               "taramasından geçmedi, boy ölçümü değildir. Ses bölücüsü masa denemesine (KT2) bağlı: yeri ve varlığı kesin değil, "
               "şemada PAM8403'ün dibinde çizildi; ReSpeaker jakının ve kamera konnektörünün yeri tahmin"],
        not_=["İki 5 V hattı birbirine köprülenmez. QLED'in Touch micro USB'si Pi'ye veri için gider; Touch VBUS ekranın içinde Power "
              "girişine bağlıysa Pi'nin 5 V'u ile SY8205 çıkışı Touch kablosu üzerinden birleşir. Bu iç bağ doğrulanmadı: Touch'ı Pi'ye "
              "takmadan multimetreyle Power ile Touch VBUS arasına bak; bağlıysa takma, çözüm o ölçümle seçilir (`planlama/adim3/elektrik.md`)",
              "Montaj sırası kaynakta yok (montaj mantığından), doğrulanmadı. Boyun uçları K2'de geldiği için arka kabuk dikişleri K2'den sonra sıkılır",
              "Ses yolu (14.11, `planlama/adim3/kablolama-on-kararlar.md` §5): ReSpeaker'ın kendi 3,5 mm çıkışı → bölücü → PAM8403; USB ses "
              "kartı kablajdan çıktı, siparişte kalır, takılmaz (yedek): masa denemesi KT2 geçmezse Pi USB 2'ye takılır ve 04.11 düzeni "
              "geri gelir. Modelde kart hâlâ çizili. Alt direnç KT2 ölçümüyle seçilir (başlangıç 2,2 kΩ)",
              "PAM8403'ün 5 V'u D24V50F5'ten (K10 a; KT1 masa denemesi, geçmezse SY8205). PAM8403 ölçüsü tahmini; ReSpeaker vida tipi ve "
              "kütlesi varsayım",
              "ReSpeaker çalma akışı en çok 16 kHz: Efe konuşma sesi için kabul etti, 1 kanallı firmware (pano cevabı, 14.11)",
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
              # P10.7b2e kısım 2 (F10l-kare-inceleme 31.2): arkadan bakışta ReSpeaker USB şeması kabuğun içinde kalıyordu (F10d şema
              # pikseli 0); kablo kafanın açık ön tarafından takılır: önden-alttan bakış (önizleme: şema 2100 px, ReSpeaker oran 0,98)
              dict(ad="Sağ arka kabuk → kafa", bag="arka_sag", desen=(), ucus_bag=(0, 0, -1), sema=("ReSpeaker USB",),
                   kamera=(-0.3, -0.3, 1.25),
                   is_="Kabuğu kafanın arkasında tut, ReSpeaker kablosunu kafanın açık ön tarafından Pi USB 1'e tak. Sonra sağ kabuğu "
                       "arkadan (−z) yerine koy: dikey dikişte sağ kabuğun bindirmesi solun altında kalır; sol önce takılırsa sağ hiçbir "
                       "düz yönden girmiyor (giriş yolu ölçümü)."),
              dict(ad="Masada: sol arka kabuk + PAM8403 (USB ses kartı yedek, takılmaz)", masa="arka_sol",
                   desen=("Arka kafa kabuğu sol", "USB ses kartı", "PAM8403"), ucus={"Arka kafa kabuğu": (0, 0, -1), "*": (1, 0, 0)},
                   kamera=(-0.85, 0.62, 1.25), saydam=("Arka kafa kabuğu sol", "USB ses kartı", "PAM8403"),
                   gizli_ok={"Köpük bant (yedek USB ses": voksel_ok(74), "Köpük bant (PAM": voksel_ok(41)},
                   is_="Masada, sol arka kabuk: PAM8403'ü yan duvarın iç yüzüne köpük bant + kablo bağıyla tut. USB ses kartı "
                       "takılmaz: çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür; bu eski tasarımdan kalan "
                       "görüntüdür, uygulanmaz. Kartın köpük bandı da yapıştırılmaz; kart yedek parçalarla birlikte saklanır (KT2 geçmezse "
                       "Pi USB 2'ye; `planlama/adim3/kablolama-on-kararlar.md` § 5 Ö1)."),
              dict(ad="Sol arka kabuk → kafa", bag="arka_sol", desen=(), ucus_bag=(0, 0, -1),
                   sema=("PAM8403 5 V", "Ses kablosu (AU1"), kamera=(0.55, 0.5, 1.25),
                   # P10.7b2e kısım 2 (F10l-kare-inceleme 31.4): arkadan bakışta (-0.85, 0.62, -1.25) iki şema da opak sol kabuğun
                   # arkasındaydı (K05 şema pikseli 0; lejant karede olmayan mavi kabloyu söylüyordu). Kablolar kafanın açık ön tarafından
                   # takılır: önden, öbür yandan bakış sol kabuğun iç yüzünü gösterir (önizleme: K05 1800 px, AU1/AU2 7900 px, PAM8403
                   # oran 0,94). Eski sema_ortulu (AU1 "sol arka kabuğun arkasında kalır") artık doğru değil, kaldırıldı.
                   # P10.7b2c ikinci yarı (ajan B): ses kablosu şeması kablo_yolu_kafa.py'de çizildi; eski not "Ses kablosunun şeması yok
                   # (ReSpeaker sağ kabukta; eski şema ses kartından çiziliyordu, kaldırıldı)." yerine aşağıdaki (talimat cümleleri aynı)
                   is_="Kabloları kafanın açık ön tarafından tak: ReSpeaker 3,5 mm jakı → 10 kΩ / 2,2 kΩ bölücü → PAM8403 sol girişi "
                       "(AU1, AU2; önce kılıf ↔ ReSpeaker USB GND sürekliliği, KT2), PAM 5 V → D24V50F5 (K05; K10 a). Ses kablosunun "
                       "çizimi gösterim şemasıdır: bölücünün yeri ve varlığı KT2'ye bağlı, ReSpeaker jakının yeri tahmin. Sonra sol "
                       "kabuğu arkadan yerine koy (giriş yolu ölçümü). "
                       # P10.7b2f (F10m-kare-inceleme § 4.2): yedek kart karede ikinci yeşil kart olarak duruyor; 31.3'ün notu burada da
                       "Karede PAM8403'ün yanındaki ikinci kart yedek USB ses kartıdır: takılmaz (önceki alt adım)."),
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
                   sema=("Kafa ekranı HDMI", "Kafa ekranı Touch", "Kafa ekranı Power", "Kamera şeridi"),   # P10.7b2c B: C01
                   is_="Yüz kabuğunu kafanın önünde tut, kabloları tak: CSI şeridi (C01) → Pi; QLED HDMI (H01; 30 cm şerit, Pi micro "
                       "HDMI 0), Power (K04; SY8205 çıkışı, A ucu kesik micro USB kablo), Touch (U04; Pi USB 4). Touch'ı takmadan önce Notlar'daki ölçümü yap. "
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
            # P10.7b2a: uzatmaların kimlikli talimatı ve "hat C" tanımı (kablolar.json S01–S10, SV3)
            "1. Kol servo uzatmaları: kart ucunu dağıtım kartının 3 pinli çıkışına tak: sağ kol dağıtım kartı A'ya (S01 omuz öne-arka, "
            "S02 omuz yana, S03 dirsek, S04 bilek), sol kol dağıtım kartı B'ye (S05 omuz öne-arka, S06 omuz yana, S07 dirsek, S08 "
            "bilek); çıkış numaraları `planlama/adim3/kablolar.md`'de. Yol: dağıtım A / B → etek → direk arka yüzü (z −26) → travers "
            "altı (y ≈ 1215) arkası → omuz. "
            # P10.7b2d-A düzeltme turu 1 (F10l-kontrol N3): Kablo yolu 5 / 7 bu alt adımda çizilir, bara → dağıtım kartı kısmı K1'de
            "Karede Kablo yolu 5 ve 7'nin baradan dağıtım kartlarına giden kısmı K1'de bağlandı; burada yalnız uzatmaları tak.\n"
            "2. Kafa servoları, hat C (XL4016 C → SV3 → dağıtım kartı C, güç panelinde; B5a): kafa pan uzatmasını (S09) dağıtım kartı "
            "C'nin pan çıkışına, kafa tilt uzatmasını (S10) tilt çıkışına tak → direk üstü R62 halkası; tilt kablosu boyundan kafaya.\n"
            "3. Kafa 12 V (G17, {awg.G17} çift, F3 {a.F3}): direk ön yüzü (z +26) → R62 → boyun → kafa giriş kartı (E3a; oradan D24V50F5 ve "
            "SY8205).\n"
            "4. ESP32 USB (U06) boyuna girmez (05.11 kararı): ESP32'den (taban) direk arka yüzü (z −26) boyunca yukarı; ucu "
            "üst arka kapak hizasında (y ≈ 1.085–1.157) hub için bırakılır, F5'te hub'a takılır. VBUS teline seri 1N5819: anot hub (Pi) "
            "tarafında, katot ESP32 tarafında; çevre 5 V hub'a / Pi'ye geri beslemez. ESP32 kartının kendi VBUS→VIN diyodu varsa "
            "gerekmez: multimetreyle bak (doğrulanmadı). 1N5819'un sınırı 1 A: çevre yüklerinin USB'den geri beslenmesini VIN'e "
            "seri ikinci 1N5819 keser (B6a, K66).\n"
            "5. Boyun demeti, 5 kablo (K14 a): hub uzatması (U03; Pi USB 3 → hub), göğüs HDMI (H02; Pi micro HDMI 1), tilt servo (S10), "
            "hoparlör (AU3; PAM8403 → hoparlör), kafa 12 V (G17). Yol: alt çıkış → servo yuvası arka kanalı (20 × 7,8 mm kapalı tünel, "
            "≈ 34 mm, iki dik dönüş) → kablo odası → mil penceresi → Ø32 adaptör → sol yanak dışı → tabla geçişi (x −50…−37). Geçiş "
            "sırası: (1) hub uzatması (USB 2.0, erkek fiş gövdesi ≤ 13 × 7 mm; erkek uç aşağıdan yukarı, tünel boşken), (2) HDMI (Ø ≤ 6 "
            "mm; micro HDMI ucu aşağıdan yukarı, HDMI A ucu gövdede), (3) tilt servo kablosu, (4) hoparlör ve (5) 12 V çifti fişsiz "
            "(uç kontakları / pabuçlar geçirdikten sonra takılır). Demeti kurmadan önce basılmış tünel deneme parçasında (20 × 7,8 mm, "
            # P10.7b2g: deneme parçası üretildi (kafa/boyun_tunel_deneme.py; kesit kafa-montaj.FCStd'nin servo yuvası + rulman yuvası +
            # boyun milinden + gerçek horn / pan servosu), fiş listesi planlama/adim3/kablolar.json U03 / H02 / S10 hazir_kablo şartı ve
            # gecis_sirasi; düzeltme turu 1 (F10o-kontrol D1, N2): kablolar birikir (kablolama-on-kararlar.md:141), pan servo kablosu
            # kafa7_parcalar.py:146 yarığından kanala iner
            "≈ 34 mm, iki dik dönüş, mil penceresi 20 × 10) fişleri elle geçir (KT4; kumpas ölçüsü yetmez). Parça: Boyun tüneli deneme "
            "parçası (`tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl`; baskı listesinde tolerans kuponlarının yanında, beyaz PETG, "
            "≈ 68 g, destek gerekmez). "
            "Önce bir servo kablosunu alt çıkıştan kanala sok, ucunu kanal dibindeki servo kablo yarığına it ve yerinde bırak (pan "
            "servosunun kendi kablosu robotta bu kanaldan iner). "
            "Fişleri parçanın arka yüzündeki alt çıkıştan sok, kanaldan yukarı, kablo odasından mil penceresine, milin içinde yukarı "
            "geçirip mil ucundan çıkar; geçen kabloyu parçada bırak, sonraki fişi onun yanından geçir: önce tünel boşken hub uzatmasının "
            "(U03) USB-A erkek fişi, sonra U03'ün kablosu tünelde yerindeyken HDMI'nin (H02) micro HDMI ucu, sonra iki kablonun yanından tilt "
            "servo kablosunun (S10) 3 pinli fişi; hoparlör (AU3) ve 12 V (G17) fişsiz geçer, deneme gerekmez. Fiş geçmezse sırasıyla: "
            "kablo fişsiz geçirilip yeniden sonlandırılır (USB 2.0'da lehimli USB-A fiş), HDMI için şerit HDMI + uç adaptörleri. "
            # P10.7b2f kısım 2: Efe'nin cevabı pano #7 mesaj #28 (elektrik.md E3)
            "Efe'nin iki cevabı geldi (ESP32 bilinçli reseti mevcut DTR / RTS devresiyle; ReSpeaker 16 kHz kabul): boyundan yeni tel "
            "gerekmez, demeti kelepçe / kılıfla kapatabilirsin.\n"
            # P10.7b2d-A düzeltme turu 1 (F10l-kontrol N4): madde 5'in kafa ucu kısmı ayrı alt adım (yalnız paragraf bölündü)
            # P10.7b2b (F10i-kontrol-3 A4): AU3'ün lehimi ve kutup kontrolü dikişler sıkılmadan önce (sıkıp kafayı yeniden açmak yok)
            # P10.7b2b düzeltme turu 1 (F10j-kontrol D2): "kafa ucunda bağla" yalnız öbür dört kablo; AU3 ayrı cümlede (geri sarma yok)
            "Hoparlör kablosu (AU3) dışındaki dört kabloyu (U03, H02, S10, G17) kafa ucunda bağla (E4'te arka kabuk dikişleri "
            "sıkılmadı). Hoparlör kablosu (AU3) için, dikişleri sıkmadan önce, enerjisizken (akü XT60 ayrık): "
            # düzeltme turu 2 (F10i-kontrol-2 §3 AU3): PAM8403 ucu kayıttan (kablolar.json AU3 damarları: L+ → +, L− → −)
            "lehimden önce hoparlör kablosunun (AU3) + damarını iki ucunda multimetrenin süreklilik kademesiyle bul ve işaretle (iki "
            "ucu da boşta). Hoparlör kablosunun (AU3) kafa ucunu PAM8403'ün sol kanal çıkışına lehimle: + damarını {uc.AU3:+:a} ucuna, − damarını "
            "{uc.AU3:−:a} ucuna; gövde ucunu fişsiz bırak (madde 6), F2'de hoparlöre lehimlenir. Kutup kontrolü, dikişleri sıkmadan "
            "önce (AU3): işaretli + damarı {uc.AU3:+:a} ucunda, öbür damar {uc.AU3:−:a} ucunda (ters ise lehimi şimdi düzelt). Sonra dikişleri "
            "sık.\n"
            "6. Boyundan inenler travers arkasından gövdeye: HDMI direğin solundan ekran arkasına (F3); hub uzatmasının ucu üst arka kapak "
            "hizasında (F5); hoparlör kablosu sağ önden göğüs altına (y ≈ 1.000; F2'de hoparlöre).\n"
            "7. Göğüs ekranı 12 V boyundan geçmez: sigorta kutusunun F6 {a.F6} ({bicak.F6}) yuvasından ayrı dal (K11 a: ana anahtar sonrası, "
            "röle öncesi; acil stopta açık kalır) → LM2577 + LM2596 regülatörü (G20) → ekran 12 V jakı (G21), {awg.G21}. "
            # düzeltme turu 1 (tamlık, emir kipi): G21 bu adımda serilir, jakı F3'te takılır
            "Regülatörün çıkışına ekran 12 V jak kablosunu bağla (G21); kabloyu direğin arka yüzünden, travers altından direğin soluna "
            "geçir ve jak ucunu ekran arkasında boşta bırak (ekrana F3'te takılır). Regülatör B5a'da güç paneline takıldı (K52 a): panele "
            "takılmadan önce, ekrana bağlanmadan 12 V'a ayarlandı (kontrol); girişi (G20) K1'de bağlandı.\n"
            "8. Kablo bağıyla direğe tuttur. S1 uçları travers arkasında kalır: G4'te yarıktan girer.",
        baglanti_md="Kablo bağı. Kablo listesi (uçlar, kesit, sigorta): `planlama/adim3/kablolar.md`",
        alet="Kumpas, yan keski, multimetre",
        erisim="Kabuk yok; arkadan ve önden düz erişim. Kafa uçları arka kabuk dikişleri açıkken",
        kontrol=["Uzatmalar (S01–S10): ince duvarlı PVC düz {awg.S01|S02|S03|S04|S05|S06|S07|S08|S09|S10}, damar ≤ 1,5 mm; kumpasla ölç "
                 "(aynı kesitte silikon tel sığmaz)",
                 "v4 uzatmalar 1 m: dirsek ve bilek 1,86 m, S2 1,70 m gerekir, ek yapılacak. Ek yeri kaynakta yok (doğrulanmadı); ek U kasetine girmesin (3 aynı şerit)",
                 "Pan ve tilt elle tam açıda: boyunda 5 kablo gerilmiyor (boyun yuva kanalı %44,8 dolu, hesap)",
                 "Hub'a gidecek uçlarda (hub uzatması, ESP32 USB) yaklaşık 150 mm kapak söküm payı var",
                 "Demet kurulmadan: tünel deneme parçasında fiş denemesi yapıldı (hub uzatması önce, sonra HDMI; KT4), sonuç yazıldı",
                 "Demet kapatılmadan: Efe'nin iki cevabı geldi (DTR / RTS reset, ReSpeaker 16 kHz); yeni tel yok, demete bükümlü çift eklenmedi",
                 "Kafa uçları bağlandı, arka kabuk dikişleri sıkıldı",
                 "Her hat iki ucundan etiketli, süreklilik ölçüldü",
                 "Göğüs ekranı regülatörü (LM2577 + LM2596) ekrana bağlanmadan, çıkışı multimetreyle 12 V'a ayarlandı: tezgâhta akım "
                 "sınırlı kaynakla (sınır 2 A) ve yük direnciyle (`planlama/adim3/elektrik.md`; `planlama/d158/testler/T7-gogus-ekrani-12v.md`)"],
        kablo=["Burada: servo A, servo B, servo kafa, kafa 12 V, enkoder / BTS sinyalleri (tabanda), boyun demeti, ESP32 USB ve göğüs ekranı "
               "kabloları. Şemada devre sınıfının renginde (lejant); tıklayınca tablodaki kimlik, uçlar, kesit, sigorta",
               "Göğüs ekranı, hub ve ses yolları gösterim şemasıdır (`lale158/kablo_yolu_ekran.py`): parça sayısına girmez; kablo çapı, büküm "
               "yarıçapı ve port yeri doğrulanmadı",
               # P10.7b2c düzeltme turu 1 (F10k-kontrol D2): şema yeniden çizilene kadar (FreeCAD koşusu, karar-kuyrugu.md)
               "\"ESP32 USB\" şemasının (U06) taban ucu yanlış yerde, güç panelinin üstünde çizili (şema yeniden çizilecek): kablonun "
               "taban ucu elektronik katındaki ESP32 taşıyıcısında ESP32'nin USB girişine takılır",
               "Şemada taban kısımları da görünür: onlar K1'de bağlandı",
               "Önerilen boylar (yol × 1,25, hub'a gidenlere + 150 mm; tahmin): HDMI 950, hub uzatması 920, ESP32 USB 1.360, hoparlör 1.030, "
               "göğüs 12 V 1.720 mm (`planlama/adim3/elektrik.md`). Kablo listesi: `planlama/adim3/kablolar.md`"],
        not_=["Boyun demeti K14 a ile kapandı (CAD'deki gibi 5 kablo, şartlarla; `planlama/adim3/kablolama-on-kararlar.md` §4): demet "
              "yazıldığı gibi kurulamayabilir, tünel deneme parçasındaki fiş denemesi belirler",
              "Göğüs ekranı 12 V dalı K11 a ile kapandı: F6 {a.F6} {bicak.F6}, ana anahtar sonrası, röle öncesi; acil stopta açık kalır",
              "LM2577 + LM2596 kartı güç panelinde (B5a, K52 a); kart ve panel üstündeki yeri modelde yok",
              "Hoparlör kablosu (~1,1 m) ve hub uzatması (USB 2.0, ~1 m) listede koşullu kalem; sipariş yine verilir (K4, O-10 b). Hub "
              "harici beslemesiz (Ö2: hayır)",
              "Hub kapanırsa ESP32 bağlantısı ve göğüs dokunmatiği birlikte düşer; hub girişindeki gerilim ölçülmedi (KT5)",
              "Konuşmak için basılan düğme (O-12) karar bekliyor (K61): tabloya kablo eklenmedi"],
    ),
    "F1": dict(
        baslik="Taban eteği",
        is_="Bağlarken akü ayrık (XT60 açık).\n"
            "1. 6 bant + 2 dolgu şeridi: orta → ön → arka (dolgu şeritleri modelde var, M6'da yok; sırası doğrulanmadı). Bindirmeleri bağla.\n"
            "2. Etek braketlerine dışarıdan M3×14 (L brakette M3 perçin somun, delik Ø5,1).\n"
            "3. Acil stop mantarını panel somunuyla tak. Bağlamadan önce mantarı multimetrenin süreklilik kademesinde dene: NC uçları "
            "arasında mantar serbestken bip var, basılıyken yok (akü ayrık; kaynakta yok, doğrulanmadı). Sonra K1'de bırakılan iki ucu "
            "mantarın NC kontağına bağla: A01'i (F5 {a.F5} çıkışından gelen) NC girişine, A02'yi (acil stop düğümüne giden) NC çıkışına.\n"
            "4. Ana anahtar ASW-A01 gövdesini etek üst plakasının altına, acil stobun karşısına tak (model yeri öneri, ölçü tahmini zarf; "
            "bağlantı elemanı modelde yok, doğrulanmadı). Düğme: delik Ø30 tahmini, anahtarı ölç. K1'de bırakılan dört ucu anahtarın "
            "saplamalarına bağla: giriş saplamasına G03'ü (ana sigortadan) ve şarj kolunun + pabucunu (G06), çıkış saplamasına G04'ü "
            "(sigorta kutusuna) ve akü ölçüm telinin pabucunu (G07; {ohm.aku_olcum} akü ölçüm direnci pabucun kovanında). Kalın "
            "pabuç ({awg.G03|G04}; G03, G04) altta, üstte düz pul + yaylı pul; giriş ile çıkışı anahtarın üstündeki işaretten oku (anahtarın saplama "
            "ölçüsü {vida.ana-anahtar} varsayım, kablajda teyit: başka çıkarsa pabuçları o ölçüde al). G07 çıkışta olmalı: girişte olursa bölücü ana anahtar kapalıyken de akım çeker.\n"
            "5. XT60 şarj girişi (panel konnektör): önerilen yer etek üst plakasının arkası, delik modelde yok "
            "(`tasarim/freecad/taban/rapor.html` şarj notu; doğrulanmadı). Delik açıldıysa konnektörü (XT60E-F, dişi panel girişi; K50 b: akü tarafı gömük soket, şarj kablosunun ucu erkek XT60; alımı açık, F5 notu) tak, "
            "K1'de bırakılan şarj ucunu (G06) akü ayrıkken bağla; açılmadıysa uç bantlı kalır. Şarj kolunun {a.hat-sarj} {bicak.hat-sarj} sigortası takılmaz "
            "(aşama 1 listesi). XT60E-F soketleri sigorta takılınca her zaman akü geriliminde (ana anahtar da mantar da kesmez): kapağı "
            "takılı kalır.",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; braket 6 × M3×14 ISO 7380 dışarıdan + M3 perçin somun (Y3 K2). M6'daki içeriden M3×8 eski",
        alet="alyan 2 (acil stop için ayrıca anahtar)",
        erisim="Düz, dışarıdan",
        kontrol=["Acil stop NP2 BE102: CAD 60 mm; delik gerçek parçayla tutuyor mu bak",
                 "İlk enerji, aşama 1 (F1 sonu, kafasız): ana anahtar ve mantar bağlı. Saat, yüzük, bileklik çıkar "
                 "(`planlama/d158/testler/00-genel.md` kural 8). Akü XT60 ayrık, ana anahtar kapalıyken ana sigortayı ({a.ana-sigorta}, standart), F4 ({a.F4}, "
                 "XL4016 çevre 5 V: ESP32; çevre çıkışındaki {a.hat-cevre} {bicak.hat-cevre} hat sigortası da) ve F5 ({a.F5}, acil stop: mantar, röle bobinleri) tak. F1 "
                 "({a.F1}: röle K1 ve ön şarj kolu K2), F3 ({a.F3}, kafa), F6 ({a.F6}, göğüs ekranı), XL4016 hat sigortaları (mini; A {a.hat-A}, B {a.hat-B}, "
                 "C {a.hat-C}), PC817 #2 algı telinin (G22) {a.hat-G22} {bicak.hat-G22} sigortası ve şarj kolunun {a.hat-sarj} {bicak.hat-sarj} sigortası takılı değil (`planlama/adim3/elektrik.md` "
                 "sigorta listesi; kutudakiler standart bıçak, hat yuvalarındakiler mini): anahtarlı bara, kafa ve göğüs ekranı dalı enerjisiz, "
                 "Pi enerjisiz. Şarj kolu ana sigortanın yük tarafında, ana anahtardan önce: sigortası takılı olsaydı ana anahtar kapalıyken de "
                 "gerilimli olurdu. Devreye alma komutu Pi'den gelir (E3). ESP32'deki program bilinmiyor: röleleri süren pinler {gpio.ROLE_K1} (K1) ve "
                 "{gpio.ROLE_K2_ONSARJ} (K2), açılışta LOW ve taban {ohm.taban} ile GND'ye çekili (E9); bilinmeyen bir program bu pinleri sürebilir. F1 "
                 "takılı olmadığı için röle K1 ve K2'nin kontakları enerjisiz, anahtarlı bara enerjisiz kalır. Tekerlekler yerden kesik (şasi "
                 "takozda, `planlama/d158/testler/T13-rampada-acil-stop.md`); BTS EN = 0. Mantar ölçümü: akü ayrıkken multimetreyi DC V "
                 "kademesine al (20 V aralığı ya da otomatik; akü en çok {v.aku_en_cok}), kırmızı ucu V soketine tak: 10 A soketinde kalırsa multimetre "
                 "bu noktayı GND'ye bağlar ve F5 {a.F5} atar (`planlama/d158/testler/00-genel.md` multimetre kuralı). Kırmızı ucu arayüz kartındaki "
                 "PC817 #1 giriş klemensinin + ucuna (mantar sonrası düğüm, E3), siyah ucunu güç panelindeki yıldız barasının (GND, M5 "
                 "saplama) akü dönüşü saplamasına (3 numaralı) bağla. Ölçü kıskacını mantar uçlarına takma. Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: BMS kesiyor mu "
                 "gözle (röle K1 açık; F3 takılı olmadığı için yalnız F4 / F5 girişleri, tam açılış aşama 2'de). Mantara basınca PC817 #1 girişi "
                 "0 V, bırakınca akü gerilimi ({v.aku_aralik}). Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök. Devreye "
                 "alma, ön şarj ve motor yön testi F5'te (İlk enerji, aşama 2). Bu aşamalar, sigorta sırası, ölçü noktası, klemensin + ucu, "
                 "multimetre aralığı ve \"yerden kesik\" düzeni bu adım için kaynakta yok, doğrulanmadı. "
                 # P10.7b2e kısım 2 (F10l-kare-inceleme F1, E): ölçü noktaları modelde yok / kart üstü klemens çizili değil
                 "Ölçü noktaları karede görünmez: PC817 #1 klemensi ve akü ölçüm bölücüsü arayüz kartının üstünde (elektronik katı, "
                 "robota önden bakınca solda; kart üstü klemensler modelde çizili değil), yıldız barası güç panelinde (arka kat; bara "
                 "modelde yok)",
                 # P10.7b2a (K63): G07'nin enerjili kontrolü, aşama 1'in ölçü düzeniyle (değerler elektrik.md E2 tablosundan)
                 # P10.7b2b düzeltme turu 1 (F10j-kontrol D1): üç maddeye bölündü; karar ağacı: akü aralık dışındaysa bölücüye hiç
                 # geçilmez; akü aralıktayken karar yalnız {v.aku_olcum} bandıyla (oran açıklama, karar ölçütü değil). Akü tarafındaki
                 # XT60'ın cinsi kayıtta yok (kablolar.json): "kontağına"
                 "Akü ölçüm teli (G07), aşama 1'de mantar ölçümünden sonra: ana anahtar kapalı, akü XT60'tan ayrıkken multimetreyi DC V "
                 "kademesinde bırak (kırmızı uç V soketinde). Önce akünün kendi gerilimini oku: akü XT60'tan ayrıkken kırmızı ucu akünün "
                 "XT60'ındaki (akü tarafı) + kontağına, siyah ucu − kontağına değdir (bir uç iki kontağa birden değmesin, iki uç birbirine "
                 "değmesin), okunanı not al: bu akü gerilimidir. Akü gerilimi {v.aku_aralik} dışındaysa burada dur: bölücü ölçümüne "
                 "geçme, ana anahtarı açma, aşama 2'ye (F5) geçme; akü {v.aku_aralik} aralığına gelince bu maddeyi baştan yinele (akünün "
                 "şarjı bu adım için kaynakta yok, doğrulanmadı)",
                 # düzeltme turu 1 (F10i-kontrol A1, A4): oran ve beklenen aralık kayıttan (elektrik.md E2 bölücü, akü aralığı)
                 "Akü gerilimi {v.aku_aralik} içindeyse: kırmızı ucu arayüz kartındaki akü ölçüm bölücüsünün orta noktasına (G07'nin kart "
                 "ucu), siyah ucu yıldız barasının akü dönüşü (G05) saplamasına bağla. Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana "
                 "anahtarı aç: okunan gerilim akü geriliminin bölücü oranı ({oran.aku_olcum}) katıdır: akü {v.aku_aralik} iken bölücünün "
                 "orta noktasında {v.aku_olcum} okunur (`planlama/adim3/elektrik.md` E2). Bölücü okumasını not al: not aldığın akü "
                 "gerilimiyle birlikte ESP32'nin bir kez yapılan multimetre kalibrasyonunda kullanılır (E2); beklenen bölücü okuması = "
                 "akü gerilimi × bölücü oranı ({oran.aku_olcum}); bu açıklamadır, karar ölçütü değildir (dirençlerin toleransı kaynakta "
                 "yok, kablajda teyit). Karar yalnız banttan: okuma {v.aku_olcum} içindeyse bölücü geçer; ana anahtarı kapat, aküyü "
                 "XT60'tan ayır, sonra ölçü uçlarını sök",
                 # düzeltme turu 2 (F10i-kontrol-2 §5 G07): aralık dışı okumada ne yapılacağı
                 "Bölücü okuması {v.aku_olcum} aralığının altında ya da üstündeyse: ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü "
                 "uçlarını sök. Akü gerilimi {v.aku_aralik} içinde olduğu için bölücü bozuk: hiç gerilim okunmadıysa G07'nin pabucu, direnci ya da "
                 "kart ucu kopmuş; aralığın üstündeyse bölücünün alt direnci eksik ya da yanlış. Akü ayrıkken bölücüyü kontrol et: G07'nin "
                 "direnci (pabuç ile bölücünün orta noktası arası, K1 kontrolündeki direnç ölçümü), direncin ve G07'nin iki ucundaki lehim, "
                 # P10.7b2c ön işi (F10j-kontrol-2 A1, A2): iki cümle tek anlamlı; değer, sıra ve güvenlik koşulu aynı
                 "bölücünün alt direnci. Bölücünün orta noktası ESP32'nin akü ölçüm pinine bağlı (B6a, X01): bölücüdeki kusuru "
                 "düzeltmeden ana anahtarı yeniden açma, ESP32'ye bu bölücüyle enerji verme, aşama 2'ye (F5) geçme. Kusuru "
                 "düzeltince ölçümü baştan, akünün kendi gerilimini okuduğun maddeden yinele. Listedeki yerlerde kusur bulunmazsa da "
                 "devam etme: akü gerilimini ve bölücü okumasını kayda yaz (tolerans kaynakta yok)"],
        kablo=["Etek bandını takarken K1 hatları sıkışmasın",
               "Burada bağlananlar: ana anahtar (G03, G04; {awg.G04}, halka pabuç; G06'nın + pabucu girişte, G07'nin pabucu çıkışta), "
               "şarj girişi (G06, {awg.G06}), acil stop mantarı (A01 F5 {a.F5} "
               "girişi, A02 NC çıkışı; {awg.A02}). Mantar kontak vidasına giren uçlar teslimde takılıp çekilerek denenir (kesit aralığı belgede "
               "yok); ana anahtarın saplama ölçüsü ve pabucu teslimde"],
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
                       "Bant düz bir yoldan girmiyor (ölçüm, Notlar). Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir). Bu bantta "
                       "engel dil değil, z +105 braketinin perçin somunu (ölçüm): kuponda bu bant ayrıca, somun takılıyken denenir.",
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
                       "Bant düz bir yoldan girmiyor (ölçüm, Notlar). Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir). Bu bantta "
                       "engel dil değil, z +105 braketinin perçin somunu (ölçüm): kuponda bu bant ayrıca, somun takılıyken denenir.",
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
                       "3 × M3×6, z −105 braketine M3×14. K1'de bırakılan iki acil stop ucunu mantarın NC kontağına bağla: A01'i NC "
                       "girişine, A02'yi NC çıkışına."),
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
                       "bindirmesi 3 × M3×6, z −105 braketine M3×14. K1'de bırakılan dört ucu anahtarın saplamalarına bağla: giriş "
                       "saplamasına G03'ü ve şarj kolunun + pabucunu (G06), çıkış saplamasına G04'ü ve akü ölçüm telinin pabucunu (G07); "
                       "kalın pabuç (G03, G04) altta. XT60 şarj "
                       "girişi (panel konnektör): önerilen yer etek üst plakasının arkası, delik modelde yok (doğrulanmadı); delik "
                       "açıldıysa konnektörü (XT60E-F, dişi; K50 b) tak, şarj ucunu (G06) akü ayrıkken bağla, açılmadıysa uç bantlı kalır. Şarj "
                       "kolunun {a.hat-sarj} {bicak.hat-sarj} sigortası takılmaz (aşama 1 listesi); sonra XT60E-F soketleri her zaman gerilimli olacağı için "
                       "kapağı kapalı kalır.")],
    ),
    "F2": dict(
        baslik="Gövde alt ve orta bantları",
        # Hoparlör: kabuk_parcalar.py orta bant sağ duvarı (19 Ø3,5 delik, 2 boss), kap ön halka + flanşlı arka, kelepçe + köpük ped;
        # kablo ucu kelepçe köprüsünün altında, yer VARSAYIM (lale158/kablo_yolu_ekran.py F1a P1.7 notu).
        is_="1. Gövde alt, uzatma 1, uzatma 2 ve orta bantları, sağ + sol, aşağıdan yukarı (uzatmalar M6'da yok; sıra doğrulanmadı). Dikişler y 476,5 / 634 / 791,5.\n"
            "2. Bindirmeleri bağla, sonra y 400, 530,25 ve 687,75 braketlerine dışarıdan M5×18 tak.\n"
            "3. Hoparlör (40 × 20, 4 Ω, 3 W) orta bant sağın ön duvarında, ızgara deliklerinin arkasında: kabın ön halkasını duvara, "
            "hoparlörü içine, flanşlı arka kabı arkasına koy; kelepçeyi köpük pedle 2 × M3×20 ile boss'lardaki ısıl gömmeye sık. Orta bandı "
            # düzeltme turu 2 (F10i-kontrol-2 §3 AU3): hoparlör ucu ve kutbu kayıttan (kablolar.json AU3 damarları)
            "takmadan önce K2'de göğüs altında bırakılan hoparlör kablosunu (AU3; kafa ucu K2'den beri PAM8403'te) hoparlöre lehimle, "
            "kutbu {kutup.AU3}: + damarını hoparlörün {uc.AU3:+:b} ucuna, − damarını {uc.AU3:−:b} ucuna (hoparlörün + işareti "
            "kablajda teyit). Hoparlörün bu sıradaki yeri kaynakta yok, doğrulanmadı.",
        baglanti_md="1,58 m: bindirme M3×6 ISO 7380; braket M5×18 ISO 7380 dışarıdan, pulsuz, M5 perçin somuna (y 400, 530,25, 687,75; Y3 K1). "
                    "Hoparlör kelepçesi 2 × M3×20 DIN 912 → ısıl gömme (boss) + köpük ped. M6'daki içeriden M5×10 eski",
        alet="alyan 2 / 2,5 / 3, havya (hoparlör ucu)",
        erisim="Düz, dışarıdan. Hoparlör orta bant takılmadan, bandın iç yüzünden",
        kontrol=["M5 başı 0,3 mm oturma yuvasında", "Kablo ve bağ uçları bant arkasında sıkışmadı",
                 "Hoparlör kablosu bağlandı, kelepçe köprüsünün altında ezilmiyor; kutup işaretli",
                 "Hoparlör kabı ızgara deliklerine ortalı, kelepçe hoparlörü sallanmadan tutuyor"],
        kablo=["Hoparlör kablosu (AU3, 2 × 0,50 mm² kordon, iki uç lehim): PAM8403 → boyun → travers arkası → sağ ön → göğüs altı (K2'de "
               "bırakıldı); burada hoparlöre bağlanır"],
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
                   is_="Bandı takmadan önce K2'de göğüs altında bırakılan hoparlör kablosunu (AU3) hoparlöre lehimle, kutbu "
                       "{kutup.AU3} (madde 3). Sonra orta bant sağı +x'ten getir (dikiş y 791,5), bindirmeleri bağla."),
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
            "3. 11,6\" ekranı (kasalı) cebe koy. Akü XT60 ayrık, ana anahtar kapalıyken göğüs ekranının F6 {a.F6} sigortasını ({bicak.F6} "
            "bıçak, sigorta kutusunun {yuva.F6}. yuvası) tak (F1 aşama 1'de takılı değildi). Dal K11 a ile ana anahtar sonrası, röle öncesi "
            "(`planlama/adim3/elektrik.md` göğüs ekranı dalı): acil stopta açık kalır. 12 V fişini takmadan önce regülatör çıkışını yeniden "
            "ölç. Ölçümden önce saat, yüzük, bileklik çıkar "
            "(`planlama/d158/testler/00-genel.md` kural 8). K2'den gelen 12 V kablosunun ekran ucundaki fiş ölçüm boyunca regülatör "
            "çıkışının 12 V'unu taşır: fişin metal ucunu bantla yalıt, ekran kasasına ve metal parçalara değmesin (genel güvenlik, kaynakta "
            "yok). Akü ayrıkken multimetreyi DC V kademesine al "
            "(20 V aralığı ya da otomatik), kırmızı ucu V soketine tak; kırmızı ucu regülatör çıkışının + klemensine, siyah ucunu çıkışın "
            "− klemensine bağla (kart üstü yazıya göre). Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç, çıkışı oku: 12 V "
            # düzeltme turu 2 (F10i-kontrol-2 §3 H02): kimlikler talimatta
            "(K2'de ayarlandı). Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök. Sonra K2'de bırakılan HDMI (H02) "
            "ve 12 V (G21) uçlarını enerjisizken ekrana tak (90° fişler; ekranlı ilk açılışta F6 atmamalı, KT3: F5 aşama 2). Ölçüm sırası ve ölçü noktası kaynakta yok, "
            "doğrulanmadı.\n"
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
                 "F6 {a.F6} ({bicak.F6}) takıldı; regülatör çıkışı 12 V okundu, 12 V fişi akü XT60'tan ayrıldıktan sonra takıldı",
                 "Ekran camı çerçeveyle aynı açıda, köşelerde boşluk eşit"],
        kablo=["K2'de bırakılan göğüs ekranı HDMI (H02) ve 12 V (G21, 90° DC jak fişi) uçları burada ekrana takılır; dokunmatik USB "
               "(U05) F5'te hub'a"],
        not_=["Göğüs ekranının montaj sırası kaynakta yok: bant → taşıyıcı → ekran → çerçeve sırası `lale158_rapor.py` erişim "
              "notlarından çıkarıldı, doğrulanmadı",
              "VESA deliklerinin kasadaki yeri ve M4 vida derinliği doğrulanmadı (plaka X yarığı ±8 mm ayar verir; vida 5,2 mm giriyor)",
              "Taşıyıcı direğin ön kanalında; K2'deki kafa 12 V hattı da direk ön yüzünden geçiyor: çakışma doğrulanmadı",
              "Ekran port yeri fotoğraftan tahmini (x ≈ −110, kısa kenar); ekran gelince ölçülecek",
              "HDMI'nin boyundan, dokunmatik USB'nin hub'dan gelmesi CAD'e göre; teyit yok, doğrulanmadı",
              "12 V dalı (F6 {a.F6} {bicak.F6} → LM2577 + LM2596 → ekran; G20, G21, {awg.G21}): K11 a ile ana anahtar sonrası, röle öncesi; acil "
              "stopta açık kalır (`planlama/adim3/elektrik.md` göğüs ekranı dalı)",
              "Regülatör kartı güç panelinde (B5a, K52 a); kart ve panel üstündeki yeri modelde yok: bu adımda çıkış klemenslerine erişim "
              "ölçülmedi, doğrulanmadı"],
        ucus="radyal",
        # F10c (P10.3): iş metnindeki sıra (bant → taşıyıcı → ekran → çerçeve); taşıyıcı M6'sı ekran takılınca kapanır (sıra denetimi)
        # F10d: alt adımlar; bantlar yandan (±x, giriş yolu ölçümü), sağ / sol ayrı (y 1005 dikişinin aynı adlı cıvataları x'e göre)
        alt=True,
        sira=[dict(ad="Göğüs bandı sağ + y 1095 braketi", desen=("Göğüs bandı sağ", "(Gövde braketi sağ", "(gövde y1005"),
                   konum={"(gövde y1005": {"x": (0, 1000)}}, ucus={"*": (1, 0, 0)}, saydam=GOVDE_BANT,
                   kamera=(0.6, 0.45, 1.25),   # F10e: varsayılan bakışta bindirme cıvatası p0280 29 px (gizle-fark); bununla hepsi geçer
                   is_="Göğüs bandı sağı +x'ten getir (dikiş y 1005), bindirmeleri bağla, y 1095 braketine dışarıdan M5×18. "
                       "Bant düz bir yoldan girmiyor (ölçüm, Notlar). Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir). Bandın boss'larındaki ısıl gömmeler (y 1198 dikişi ve F5'teki "
                       "üst arka servis kapağının 4'ü) hazırlıkta takılı (adım 0; bantlar saydam çizili).",
                   ucus_ok={"Göğüs bandı sağ": "giriş yolu ölçümü (düzeltme turu 1; ışın aralıkları h 0,5 mm, ortak hacim eşiği 0,2 mm, 2 mm adım; temas sayılmaz): düz yol yok. +x'te orta bant sağ ile 1–159 mm "
                                               "ortak hacim (bindirme dili), 173 mm'de ayrılıyor; +y'de orta bant 1–13 mm; ±z'de orta bant 1–213 mm. "
                                               "Karar önerisi F10d-K1"}),
              dict(ad="Göğüs bandı sol + y 1095 braketi", desen=("Göğüs bandı sol", "(Gövde braketi sol", "(gövde y1005", "(gövde x0"),
                   konum={"(gövde y1005": {"x": (-1000, 0)}}, ucus={"*": (1, 0, 0)}, kamera=(-0.85, 0.62, 1.25), saydam=GOVDE_BANT,
                   is_="Göğüs bandı solu −x'ten getir; bindirmeleri bağla (x = 0'da cep altı y 1022,7 ve cep üstü y 1222 dahil), y 1095 "
                       "braketine M5×18. Bant düz bir yoldan girmiyor (ölçüm, Notlar). Bandı hafifçe esneterek dilini orta bandın arkasına sok (K55 a, geçici; baskı kuponunda denenir). Isıl gömmeler (y 1198 dikişi, üst arka servis kapağının "
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
                       "yalnız bu yön serbest; düz önden 19,5 mm sonra bant). 12 V ölçümü ve fişler için adımın iş metnindeki 3. maddeyi izle (F6 {a.F6}, K11 a). "
                       "Sonra ekranı taşıyıcıya arkadan 4 × M4×12 + pul ile bağla (VESA 75 × 75): üst arka servis kapağı açık, direğin "
                       "yanından. Dokunmatik USB ucu F5'e kadar boşta, etiketli."),
              dict(ad="Göğüs ekranı çerçevesi", desen=("Göğüs ekranı çerçevesi", "Çerçeve cıvatası"), ucus={"*": (0, 0, 1)},
                   saydam=GOVDE_BANT + ("Göğüs ekranı çerçevesi",),
                   is_="Çerçeve sağ + sol: göğüs bandına dışarıdan, yarı başına 4 × M3×6 ISO 7380, çerçeve flanşındaki ısıl gömmeye. "
                       "Ekran camı çerçevenin 2 mm gerisinde, köşe takozlarına dayalı. Çerçeve düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe "
                       "esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir).",
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
                       "Bandın boss'larındaki ısıl gömmeler (x 0 dikişi, S1 kaseti) hazırlıkta takılı (adım 0; bantlar saydam çizili). Bant düz "
                       "bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir).",
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
                       "hazırlıkta takılı (bantlar saydam çizili). Bant düz bir yoldan girmiyor (ölçüm, Notlar): hafifçe esneterek dilini "
                       "göğüs bandının arkasına sok (K55 a, geçici; baskı kuponunda denenir)."),
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
        is_="1. S2 hornu, merkez vidası: hornu, kol takılınca dişe dayanacağı konumda (S2 = 4,3°) tak (K40 a).\n"
            "2. Kol çatalı → horn (4 × M3×8). 625ZZ çatalın arka kolunun Ø16 yuvasında: tezgâhta önceden preslenir, iki bileziğiyle "
            "çatalla gelir. Çatal yerindeyken mafsal pulu + M5×12: arka koldan rulmanın iç bileziğinden göbekteki M5 ısıl gömmeye "
            "(iç bileziği göbeğe sıkar, çatal döner). S2'nin sentil sınaması (K40 a) burada yapılmaz: S2 ilk kez F5 \"İlk enerji, "
            "aşama 2\"de sürülür, sınama orada.\n"
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
                   is_="S2 hornu + merkez vidası (horn kol dişe dayalıyken, S2 = 4,3°; sentil sınaması F5 aşama 2'de, K40 a); kol çatalı → horn (4 × M3×8): 625ZZ tezgâhta çatalın arka kolunun Ø16 yuvasına "
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
        is_="1. 4'lü USB hub (harici beslemesiz, USB 2.0) üst arka servis kapağının içinde: hub'ı kapağın takozuna, iki yan dayamanın "
            "arasına 1 mm köpük bantla yapıştır. Bağla: hub kablosu ← Pi USB 3'ten boyundan gelen USB 2.0 uzatma (U03, K2), Hub 1 → göğüs "
            "ekranı dokunmatiği (U05; F3'te boşta bırakılan USB), Hub 2 → ESP32 USB (U06; K2'de direk arka yüzünden çıkarılan uç; 1N5819 "
            "yönü K2 madde 4). Hub 3 ve 4 boş. Hub'ın anahtarı açık kalmalı.\n"
            "2. İlk enerji, aşama 2 (devreye alma testi): kapaklar açık, hub bağlı (ESP32 ile Pi hub üzerinden konuşur). Saat, yüzük, "
            "bileklik çıkar (`planlama/d158/testler/00-genel.md` kural 8). Akü XT60 ayrık, ana anahtar kapalıyken F1 ({a.F1}), F3 ({a.F3}, kafa), "
            "XL4016 hat sigortalarını (mini; A {a.hat-A}, B {a.hat-B}, C {a.hat-C}) ve PC817 #2 algı telinin (G22) {a.hat-G22} {bicak.hat-G22} sigortasını tak (`planlama/adim3/elektrik.md` "
            "sigorta listesi; F6 {a.F6} F3'te takıldı). Şarj kolunun {a.hat-sarj} {bicak.hat-sarj} sigortası bu aşamada da takılı değil. Tekerlekler yerden "
            "kesik (şasi takozda, `planlama/d158/testler/T13-rampada-acil-stop.md`); BTS EN = 0. Kollar aşağıda başlar: mantara basınca "
            "servo gücü de kesilir ve kollar düşer (E3 DTR / RTS notu). Kolların erişim alanında ve düşme hattında, kafanın ve tekerlerin "
            "erişim alanında kimse yok, bir kişi yalnız mantarda (kural 1 ve 7); bu kuralın tek istisnası aşağıdaki S2 sentil sınamasıdır, "
            "şartları o cümlede. Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana "
            "anahtarı aç: BMS kesiyor mu gözle (röle K1 açık; F3 / F4 / F5 / F6 girişleri, Pololu ve göğüs ekranı dalı dahil; ekranlı ilk "
            "açılışta F6 atmamalı, KT3). Pi açılır; ESP32, Pi seri portu açılınca resetlenmemeli (boot mesajı yok; E3 DTR / RTS). Pi'den "
            "devreye al, ESP32 ön şarj dizisi (E9): ön koşul (mantar serbest, servo hedefleri son konumda, BTS EN = 0 ve PWM = 0) → {gpio.ROLE_K2_ONSARJ} "
            "= 1 (röle K2) → en az {ms.onsarj} bekle (boş aküde {ms.onsarj_bos} önerilir) → {gpio.BARA_DURUM} (PC817 #2) LOW teyidi (bara var; LOW değilse ön şarj "
            "kolu çalışmıyor: {gpio.ROLE_K2_ONSARJ} = 0, hata) → {gpio.ROLE_K1} = 1 (röle K1) → {ms.k1_sonra} sonra {gpio.ROLE_K2_ONSARJ} = 0 (K2 bırakılır) → {gpio.BARA_DURUM} LOW teyidi. K2 "
            "toplam en çok {s.k2_en_cok} çeker. Mantara basınca K1 düşer (K2, devreye alma sırasında K1 çektikten {ms.k1_sonra} "
            "sonra zaten bırakılmıştı; E9 adım 5), anahtarlı bara kesilir ({gpio.BARA_DURUM} HIGH), kollar düşer; göğüs ekranı dalı (F6) acil stopta açık kalır. "
            "Mantarı bırak: röle kendiliğinden çekmez, yeniden devreye alma yalnız Pi komutuyla. "
            "Motor yön testi: her yan ileri komutta ileri döner; dönen tekere el uzatılmaz. Yön testinden sonra kontrol listesindeki sağ / sol "
            "kurulum testini yap. S2 sentil sınaması (K40 a; horn G3'te dişe göre takıldı). Bu sınama aşamadaki \"kolların erişim "
            "alanında kimse yok\" kuralının tek istisnasıdır ve yalnız şöyle yapılır: komutu mantardaki kişi verir; S2'ye 5 komutunu ver, "
            "kol durduktan sonra üç saniye bekle; mantardaki kişi bundan sonra kumandaya, telefona ve klavyeye dokunmaz, eli mantarın "
            "üstünde kalır. Öbür kişi yalnız sentilin ucundan tutarak dişle kol arasına 0,3 mm sentili sokar, parmağını dişle kol arasına "
            "sokmaz (sıkışma hattı): 0,3 mm geçmeli, 0,4 mm geçmemeli. Kişi elini çekip kolun erişim alanından çıkmadan hiçbir komut "
            "verilmez; ikinci kol için aynı sıra. Kol beklenmedik biçimde kıpırdarsa mantara hemen basılır. Bantlar takılıyken sentil dişle kol "
            "arasına düz giremiyorsa sınamayı zorlama; ölçülemedi diye kaydet ve omuz bandını sökmeden önce proje sahibine sor (aralığın "
            "kabuk altında erişilebilirliği CAD'de doğrulanmadı). 0,3 geçmiyorsa ana anahtarı kapat, aküyü ayır, sonra diş yüzünü "
            "zımparala (yalnız enerjisizken) ve sınamayı yinele. Bitince ana anahtarı kapat, aküyü XT60'tan ayır "
            "(`planlama/adim3/elektrik.md` E3, E9). Bu adımdaki sıra kaynakta yok, doğrulanmadı.\n"
            "3. Testten sonra kapat: arka servis kapağı, üst arka servis kapağı (hub'la birlikte), etek H1 ve H2.\n"
            "H1 sigorta kutusuna açılır: sık değişen F1, F3, F4, F5 ortadaki dört yuvada (29.10). Kutu 1 × 6 dizilişliyse kapak altında "
            "kalan iki uç yuva nadiren değişenlere ayrıldı: yedek sigorta F2 ({a.F2} {bicak.F2}; hiçbir dalı beslemez) ve F6 ({a.F6}, göğüs "
            "ekranı, 14.11; kutunun {yuva.F6}. yuvası). 2 × 3 dizilişte altısı da açıkta (`planlama/adim3/elektrik.md` sigorta listesi, H1 erişimi).",
        baglanti_md="1,58 m: arka kapak 7 × M3×6 ISO 7380; üst arka kapak 7 × M3×6 ISO 7380; H1 4 × M3×6 (x ±50); H2 4 × M3×6; hepsi "
                    "ısıl gömmeye. Isıl gömmeler kapaklarda değil, bantların boss'larında: arka kapağınkiler orta bantta (F2), üst arka "
                    "kapağınkiler göğüs bandında (F3), H1 / H2'ninkiler etek arka bantlarında (F1); o adımlarda takılı geldi. Hub: 1 mm "
                    "köpük bant (kapak takozunda). Üst kapak, H2 ve hub M6'da yok",
        alet="alyan 2",
        erisim="Düz. Hub kapağın iç yüzünde: kapak açıkken bağlanır",
        kontrol=["Hub köpük banda oturdu, yan dayamalar arasında; anahtarı açık",
                 "İlk enerji, aşama 2 (madde 2): BMS kesmedi; ön şarj dizisi en az {ms.onsarj} beklemeyle ve iki {gpio.BARA_DURUM} (PC817 #2) LOW "
                 "teyidiyle bitti, K2 en çok {s.k2_en_cok} çekti; mantara basınca K1 düştü, bara kesildi; her yan ileri komutta ileri döndü; sonunda "
                 "akü XT60'tan ayrıldı",
                 "Göğüs ekranı ilk açılışta F6 {a.F6}'i attırmadı (KT3)",
                 "S2 5 komutunda dişle kol arasında 0,3 mm sentil geçiyor, 0,4 mm geçmiyor; iki kolda da (K40 a)",
                 "Testte ESP32 ve göğüs dokunmatiği hub üzerinden görünüyor",
                 "Kapak açılınca hub'a bağlı üç kablo gerilmiyor (yaklaşık 150 mm söküm payı)",
                 "E7 ve kafa ısı ölçümü kabuk kapalı yapıldı (kafada hesap ≈ 49 °C, ölçülmedi)", "Kapak altında kablo sıkışmadı",
                 # P10.7b2f (F10m-kare-inceleme § 5): K1 kontrol listesinden taşındı (K1'de enerji yok, işaretlenemez)
                 "Sağ / sol kurulum testi (bağladığın taraf ile yazılımın tarafı aynı mı; K1'de bağlanan kablolar; "
                 "devreye aldıktan ve motor / enkoder yön testinden (`*_MOTOR_TERS`, `*_ENKODER_TERS`; `kod/esp32/OKU_BENI.md`) sonra "
                 "yapılır): tekerler yerden kesik (şasi takozda). Önce `sur` komutunu v = 0, w = 0,2 ile gönder (w "
                 "sola +; motorlar yarım saniyede kendiliğinden durur, gerekirse yinele): robot kendi soluna dönmek ister, yani robota önden "
                 "bakınca soldaki tekerler ileri, sağdakiler geri döner. Sonra `odo_sifirla` komutunu gönder ve arka tekerleri tek tek "
                 "elle çevir: önden bakınca soldaki arka teker `odo` satırında yalnız `sag` sayacını değiştirmeli (`sol` sabit kalır), sağdaki "
                 "yalnız `sol` sayacını; sayacın artıp azalması bu testin konusu değil, yön testinin konusudur. Ters "
                 "çıkarsa kabloyu değiştirme: robotu sürme, `planlama/d158/sag-sol-karari.md`'deki yazılım düzeltmesi bekleniyor (Efe). "
                 "Devreye alma adımları ve `sur`'un yalnız w ile davranışı kartta denenmedi (`kod/esp32/OKU_BENI.md`)"],
        kablo=["Hub: Pi USB 3 → boyun → hub (U03, USB 2.0 uzatma), Hub 1 → göğüs dokunmatiği (U05), Hub 2 → ESP32 (U06). Hub kapanırsa "
               "ESP32 ve göğüs dokunmatiği birlikte düşer"],
        not_=["Ön şarj dizisi ESP32 yazılımında (`planlama/adim3/elektrik.md` E9, adım 1–6): yazılım hazır değilse aşama 2 yapılmaz, "
              "röleler elle kapatılmaz (kaynakta yok, doğrulanmadı). Bekleme en az {ms.onsarj}; boş aküde dolma hesapla 0,2–0,5 s, bu yüzden "
              "{ms.onsarj_bos} önerilir (Efe'ye bildirildi; karar yazılım tarafıyla). PC817 #2'nin ({gpio.BARA_DURUM}) LOW olması kondansatörlerin dolduğunu göstermez",
              "Şarj kolunun {a.hat-sarj} {bicak.hat-sarj} sigortası iki aşamada da takılı değil: kol ana sigortanın yük tarafında, ana anahtardan önce "
              "(`planlama/adim3/elektrik.md` sigorta listesi, karar O-17). Sigorta ilk şarjdan önce, akü XT60 ayrıkken takılır; bu sıra "
              "kaynakta yok, doğrulanmadı. Uyarı: sigorta takıldıktan sonra etekteki şarj girişinin (XT60E-F panel dişi, "
              "K50 b) soketleri, akü XT60'tan ayrılmadıkça gerilimlidir: ana anahtar da mantar da bu kolu kesmez. Soketlere "
              "metal sokma; kapak takılı kalır. Konnektörün alımı açık: siparişte XT60E-M varsa XT60E-F ile değiştirilir (K50, teslimde bakılacaklar)",
              "Hub'ın kapakla birlikte açılması ve 150 mm söküm payı tahmin; testten önce hub bağlantısının yapılması montaj mantığından, "
              "kaynakta sıra yok: doğrulanmadı",
              "Hub harici beslemesiz (Ö2: hayır), USB'den beslenir; girişindeki gerilim ölçülmedi (KT5)",
              "USB cihazları 4 (K1 kapandı: altıncı cihaz yok): Pi USB 2 ve hub'da 2 port boş"],
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
                       "kutusuna açılır: sık değişen F1, F3, F4, F5 ortada; uç yuvalarda yedek sigorta F2 ve F6 (göğüs ekranı; madde 3).")],
    ),
}

# Y3 (C1–C3, K1–K7) CAD'e işlendi: "M6 CAD sonrası değişecek" bayrağı 125 cm JSON'undan geliyordu, kapalı.
M6_BAYRAK_ACIK = False

# Kablo yolu şemaları: direğe çıkan (y > etek üstü 262 + pay) K2, tabanda kalan K1.
KABLO_K2_Y_ESIK = 300.0
# P10.7b2e kısım 2 (F10l-kare-inceleme 32.4): Kablo yolu 12 B01'in CAD yoludur (B01 K1 alt adım 10'da bağlanır); direkten kafaya çıkan
# kısmı eski ESP32 USB yolu (05.11 öncesi), y eşiği yüzünden K2'ye düşüp 32.4'te "U06 boyuna girmez" kartıyla çelişiyordu. Yol, kablosunun
# bağlandığı kapıda gösterilir (eski kısmı o kartta yazılı). Parça geometrisi değişmez (CAD dosyası okunur, yazılmaz).
# P10.7b2f (F10m-kare-inceleme § 4.1): yol 12'nin eski kısmı rehberde kırpıldı (rehber_kablo.CAD_KIRP, kesim y 192,5); kırpılmış yol
# eşikle K1'e düşer, istisna gerekmez. Mekanizma kalır (kablosunun kapısı y eşiğinden ayrı düşen yol için).
KABLO_KAPI_ISTISNA = {}


def kablo_kapisi(y_maks, no=None):
    """Kablo yolu şemasının kapısı: no (Kablo yolu numarası) istisnadaysa oradan, yoksa en büyük y'den (direğe çıkan K2)."""
    if no in KABLO_KAPI_ISTISNA:
        return KABLO_KAPI_ISTISNA[no][0]
    return "K2" if y_maks > KABLO_K2_Y_ESIK else "K1"


def kablo_yolu_no(ad):
    """"Kablo yolu 12: …" → 12 (görünen ya da CAD adı); değilse None."""
    import re as _re
    m = _re.match(r"\s*Kablo yolu (\d+):", ad or "")
    return int(m.group(1)) if m else None


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


# P10.7b1 düzeltme turu 1 (kontrol Ü1): CAD parça adı / kodu eski elektrik bilgisi taşıyorsa rehberde görünen ad / kod çevirisi. CAD
# kaynakları (taban_parcalar.py, kafa_lib.py, arayuz.py) değişmez (regresyon referansı, FreeCAD üretimi). Desen tr()'nin Türkçe
# çıktısına uygulanır (tam ad için ^…$). (desen, yerine, kayıt). Listede olmayan ve eski terim taşıyan ad / kod rehber_veri.py'de
# üretimi durdurur (rehber_denetim.elektrik_denetle; sessiz geçiş yok).
AD_CEVIRI = [
    (r"MOSFET \+ 1N4007", "BC337-40 ×2 (röle sürücüleri; 1N4007'ler rölelerin bobin uçlarında)",
     "planlama/adim3/kablolar.json ic_baglar (BC337-40 #1 / #2) ve anahtarlar K1-bobin / K2-bobin geri_tepme_diyodu.yer"),
    (r"röle sürücü MOSFET \+ diyot", "röle sürücüleri BC337-40 ×2", "planlama/adim3/kablolar.json ic_baglar"),
    (r"^USB ses kartı$", "USB ses kartı (yedek, takılmaz)",
     "planlama/adim3/kablolama-on-kararlar.md § 5 Ö1: siparişte kalır, takılmaz; KT2 geçmezse Pi port 2'ye"),
    (r"^USB ses kartı \(PAM8403 girişi; (.*)\)$", r"USB ses kartı: yedek, takılmaz (KT2 geçmezse Pi port 2'ye; \1)",
     "planlama/adim3/kablolama-on-kararlar.md § 5 Ö1"),
    (r"^Köpük bant \(USB ses kartı\)$", "Köpük bant (yedek USB ses kartı için; kart takılmaz, bant yapıştırılmaz)",
     "planlama/adim3/kablolama-on-kararlar.md § 5 Ö1"),
]


def ad_cevir(s):
    """AD_CEVIRI'yi uygula (tr()'nin son adımı; eski veri benzetimi de bunu kullanır)."""
    import re
    if not s:
        return s
    for a, b, _k in AD_CEVIRI:
        s = re.sub(a, b, s)
    return s


def tr(s):
    """CAD'den gelen ASCII metni ekranda Türkçe göster (parça adı, kod, malzeme, kablo adı). Kimlik ve sayım bundan etkilenmez."""
    import re
    if not s:
        return s
    for a, b in TR_IFADE:
        s = re.sub(a, b, s)
    return ad_cevir(re.sub(r"[A-Za-z]+", lambda m: _kelime(m.group(0)), s))


# Taban kablo yolu şemalarının görünen adı (CAD etiketi taban_parcalar.py'de; tarama kaynağı olduğu için orada değiştirilmedi).
# no -> (beklenen CAD etiketi başı, görünen ad). Etiket başı tutmazsa tr(CAD etiketi) gösterilir ve rehber_veri.py uyarı yazar.
KABLO_AD = {
    # P10.7b1: adlar planlama/adim3/kablolar.json ile aynı (kimlikler parantez içinde; eşleme rehber_kablo.py CAD_ESLEME)
    1: ("12 V ana hat", "12 V ana hat (G01–G04, {awg.G04}): akü + → XT60 → ana sigorta {a.ana-sigorta} → ana anahtar → sigorta kutusu"),
    2: ("Toprak", "Toprak (G05, {awg.G05}): akü − → yıldız barası (güç paneli, M5 saplama) → tüm dönüştürücüler"),
    3: ("Motor 12 V: F1", "Motor 12 V (G08–G12, {awg.G12}; M01 motorun kendi kablosu): F1 {a.F1} → röle K1 ∥ ön şarj kolu → anahtarlı "
                          "bara (M5 saplama) → BTS7960 sol → ön sol motor"),
    4: ("Motor 12 V sag", "Motor 12 V sağ (G13, {awg.G13}: anahtarlı bara → BTS7960 sağ; M03, M04 motorun kendi kablosu: ön sağ ve arka "
                          "sağ motor; plaka altından, z 36 deliğinden). Arka sol motor (M02) bu yolda değil: kendi gösterim şeması B3'te"),
    5: ("Servo 6 V A", "Servo 6 V A (G14 {awg.G14} → SV1 {awg.G14}): anahtarlı bara → {a.hat-A} {bicak.hat-A} hat sigortası → XL4016 A (0; 170) → "
                       "dağıtım A (72; 205) → uzatmalar S01–S04: sağ kol"),
    6: ("Servo uzatmalari kafaya", "Servo uzatmaları kafaya (S09, S10; {awg.S10}): pan + tilt (hat C, XL4016 C güç panelinde; direk üstü, "
                                   "R62 halkasından)"),
    7: ("Servo 6 V B", "Servo 6 V B (G15 {awg.G15} → SV2 {awg.G15}): anahtarlı bara → {a.hat-B} {bicak.hat-B} hat sigortası → XL4016 B (−49; 75) → "
                       "dağıtım B (−72; 205) → uzatmalar S05–S08: sol kol"),
    # F7a P7.2 madde 4: CAD adı "kafada 5 V/5,5 A cevirici (Pi 5, LCD)" eski (LCD kalktı; kafada iki 5 V hattı: elektrik.md kafa güç mimarisi)
    8: ("Kafa 12 V", "Kafa 12 V (G17, {awg.G17} çift): F3 {a.F3} → direk ön yüzü → R62 → boyun → kafa giriş kartı (P6KE18A) → Pololu "
                     "D24V50F5 (Pi 5, PAM8403) + SY8205 (10,1\" QLED)"),
    9: ("Cevre 5 V", "Çevre 5 V (G18, {awg.G18}): F4 {a.F4} → XL4016 çevre. Şemanın XL4016 sonrası kısmı eski (doğrudan ESP32'ye); "
                     "tabloda G19 ({awg.G19}) {a.hat-cevre} {bicak.hat-cevre} hat sigortasıyla arayüz kartına gider, bu şemada çizili değil: "
                     "kendi gösterim şeması K1'de"),
    10: ("Acil stop", "Acil stop (A01–A06, {awg.A01}; PC817 teli {awg.A06}): F5 {a.F5} → mantar (NC) → acil stop düğüm kartı → röle K1 ve K2 "
                      "bobinleri → BC337-40 #1 / #2 (arayüz kartı, {gpio.ROLE_K1} / {gpio.ROLE_K2_ONSARJ}); PC817 #1 mantar sonrası gerilimi okur ({gpio.ACIL_STOP_DURUM})"),
    11: ("Sinyal: sonar", "Sinyal: sol sonar (Q03, {awg.Q03}) → arayüz kartı bölücü (4,7 kΩ / 10 kΩ) → ESP32 (X01; ön ara ray üstünden). "
                          "Orta ve sağ sonar (Q01, Q02) bu şemada değil: kendi gösterim şemaları K1'de"),
    # 05.11 B kararı: ESP32 USB hub'dan, direk arka yüzünden (kablo_yolu_ekran.py "ESP32 USB"); bu şemanın geometrisi CAD'de eski yol
    12: ("Sinyal: enkoder", "Sinyal: BTS7960 sol PWM / EN / IS (B01, {awg.B01}) → ESP32. Enkoderler (N01, N02) ve BTS sağ (B02) bu şemada "
                            "değil: kendi gösterim şemaları K1'de. CAD yolunun 05.11 öncesi ESP32 → kafa USB kısmı rehberde çizilmez; ESP32 USB "
                            "artık hub'dan: \"ESP32 USB\" şeması"),
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
# (kaynak işlev, kaynak ad, adım kodu, görünen ad, kablo kimlikleri)
# P10.7b1: son alan renk değil, planlama/adim3/kablolar.json kablo kimlikleri (ilki çizimin rengini ve tüp çapını verir; rehber_kablo.py).
# 14.11 ses yolu kararıyla "Ses karti uzatmasi" (Pi USB 2 → USB ses kartı) ve "3,5 mm -> PAM" (ses kartı → PAM) şemaları kaldırıldı:
# tabloda karşılıkları yok (ses kartı yedek, takılmaz); ReSpeaker 3,5 mm → PAM yolu (AU1, AU2) kablo_yolu_ekran.py'de çizili değil
# (P10.7b2c ikinci yarı: lale158/kablo_yolu_kafa.py "AU1" şemasında; iki eski yol rehber_kablo.SEMA_ESLEMESIZ_MUAF'ta).
SEMA = [
    ("yollar", "HDMI", "K2", "Göğüs ekranı HDMI (H02): Pi micro HDMI 1 → boyun → travers arkası → direk solu → ekran (F3'te takılır)", ("H02",)),
    ("yollar", "Hub uzatmasi", "K2", "Hub uzatması (U03, USB 2.0): Pi USB 3 → boyun → travers arkası → üst arka kapak içi hub (F5)", ("U03",)),
    ("yollar", "ESP32 USB", "K2", "ESP32 USB (U06): hub (Hub 2) → direk arka yüzü → ESP32 (taban); VBUS'ta seri 1N5819: anot hub (Pi) "
     "tarafında, katot ESP32 tarafında; kartın kendi diyodu varsa gerekmez, multimetreyle bak (doğrulanmadı)", ("U06",)),
    ("yollar", "Hoparlor", "K2", "Hoparlör (AU3): PAM8403 → boyun → travers arkası → sağ ön → hoparlör (F2'de bağlanır)", ("AU3",)),
    ("yollar", "12 V", "K2", "Göğüs ekranı 12 V (G20, G21; {awg.G21}): güç paneli (F6 {a.F6} → LM2577 + LM2596; regülatör güç panelinde, B5a, "
                           "K52 a; modelde yok) → direk arka yüzü → direk solu → ekran; boyundan geçmez", ("G21", "G20")),
    ("yollar", "USB dokunmatik", "F3", "Göğüs dokunmatiği (U05, USB): ekran TOUCH → hub (Hub 1); F5'te hub'a takılır", ("U05",)),
    ("yollar", "Dizi USB", "E4", "ReSpeaker USB (U01): Pi USB 1 → ReSpeaker (kısa micro USB)", ("U01",)),
    ("yollar", "PAM 5 V", "E4", "PAM8403 5 V (K05, {awg.K05}): D24V50F5 → PAM (K10 a)", ("K05",)),
    ("kafa_ici_qled", "HDMI (serit, 2 lehimsiz fis)", "E4", "Kafa ekranı HDMI (H01, 30 cm şerit): Pi micro HDMI 0 → QLED", ("H01",)),
    ("kafa_ici_qled", "Touch USB (kutu kablosu)", "E4", "Kafa ekranı Touch (U04): Pi USB 4 → QLED (VBUS uyarısı: Notlar)", ("U04",)),
    ("kafa_ici_qled", "Power USB (30 cm, A ucu kesik)", "E4", "Kafa ekranı Power (K04): SY8205 → QLED (ayrı 5 V hattı)", ("K04",)),
    # P10.7b2c: yolu hiçbir çizimde olmayan taban kabloları (lale158/kablo_yolu_taban.py; kaynak ad = kablo kimliği). Çarpışma
    # taramasından geçmedi (adımın kablo notunda yazılı); modelsiz uç "yeri yaklaşık". Uçlar rehber_kablo.sema_geometri_denetle ile sınanır.
    # P10.7b2d-A (F10k kare bakışı, G07 anahtar ucu): ana anahtarın karede olmadığı, K1 madde 1'in sözcükleriyle
    ("taban", "G07", "K1", "Akü ölçüm bölücüsü (G07, {awg.G07}): ana anahtar çıkışı (bölücünün üst direnci bu uçta) → güç paneli üstü → "
                         "kat üstü → arayüz kartı, bölücü orta noktası. Ana anahtar henüz yerinde değil (F1'de etek plakasının altına "
                         "takılır), karede yok", ("G07",)),
    ("taban", "G16", "K1", "XL4016 C girişi (G16, {awg.G16}): anahtarlı bara (yeri yaklaşık: modelde yok, röle yanından çizildi) → hat "
                         "sigortası → XL4016 C IN", ("G16",)),
    ("taban", "G22", "K1", "Bara durumu (G22, {awg.G22}): anahtarlı bara (yeri yaklaşık: modelde yok, röle yanından çizildi) → hat "
                         "sigortası → arayüz kartı, PC817 #2 girişi", ("G22",)),
    ("taban", "SV3", "B5a", "Kafa servo hattı C (SV3, {awg.SV3}): XL4016 C OUT → dağıtım kartı C (yeri yaklaşık: modelde yok, XL4016 C'nin "
                          "yanında)", ("SV3",)),
    ("taban", "G19", "K1", "Çevre 5 V (G19, {awg.G19}): XL4016 çevre OUT (alt kat) → ön kat kesiği → arayüz kartı, çevre 5 V klemensi",
     ("G19",)),
    ("taban", "M02", "B3", "Arka sol motor (M02, motorun kendi kablosu): BTS7960 sol M+ / M− → arka kablo deliği → plaka altı → arka sol "
                         "motor", ("M02",)),
    ("taban", "B02", "K1", "BTS sağ sinyali (B02, {awg.B02}): BTS7960 sağ sinyal başlığı → ön kat kesiği → ESP32 taşıyıcısı", ("B02",)),
    ("taban", "N01", "K1", "Arka sol enkoder (N01, {awg.N01}): motor → plaka altı → arka kablo deliği → ön kat kesiği → ESP32 taşıyıcısı",
     ("N01",)),
    ("taban", "N02", "K1", "Arka sağ enkoder (N02, {awg.N02}): motor → plaka altı → arka kablo deliği → ön kat kesiği → ESP32 taşıyıcısı",
     ("N02",)),
    ("taban", "Q01", "K1", "Sağ sonar (Q01, {awg.Q01}): pin bloğu → ön ara ray üstü → ön kat kesiği → arayüz kartı (Trig teli PCA9685'e "
                         "gider, o ucu çizilmedi)", ("Q01",)),
    ("taban", "Q02", "K1", "Orta sonar (Q02, {awg.Q02}): pin bloğu → ön ara ray üstü → ön kat kesiği → arayüz kartı (Trig teli PCA9685'e "
                         "gider, o ucu çizilmedi)", ("Q02",)),
    # P10.7b2c ikinci yarı (ajan B): kafa içi ve ses kabloları (lale158/kablo_yolu_kafa.py; kaynak ad = ana kablo kimliği). Çarpışma
    # taramasından geçmedi (adımın kablo notunda yazılı). Modelsiz uçlar: kafa giriş kartı "yeri yaklaşık", ses bölücüsü KT2'ye bağlı.
    ("kafa_ici", "K01", "E3a", "Kafa girişi → D24V50F5 (K01, {awg.K01}): kafa giriş kartı (yeri yaklaşık: modelde yok, boyun geçişinin "
                               "solunda çizildi) → D24V50F5 VIN / GND", ("K01",)),
    ("kafa_ici", "K02", "E3a", "Kafa girişi → SY8205 (K02, {awg.K02}): kafa giriş kartı (yeri yaklaşık) → SY8205 IN+ / IN− (giriş ucu "
                               "kartın sol ucunda varsayıldı)", ("K02",)),
    ("kafa_ici", "K03", "E3a", "Pi 5 beslemesi (K03, {awg.K03}): D24V50F5 VOUT / GND → Pi 5 USB-C (lehimli USB-C ucu)", ("K03",)),
    ("kafa_ici", "C01", "E4", "Kamera şeridi (C01, CSI FPC): Pi CSI → QLED'in üst kenarının üstünden → kamera", ("C01",)),
    ("kafa_ici", "AU1", "E4", "Ses kablosu (AU1, AU2): ReSpeaker 3,5 mm jakı → ses bölücüsü → PAM8403 sol girişi. Bölücü masa denemesine "
                              "(KT2) bağlı: yeri ve varlığı kesin değil, şemada PAM'ın dibinde; jak yeri tahmin", ("AU1", "AU2")),
]


# ---------------------------------------------------------------- P10.7b1 düzeltme turu 1: kritik değerler kayıttan (yer tutucu)
# Metindeki {tür.anahtar} yer tutucuları içe aktarılırken rehber_deger.py ile kablolar.json / pin haritası JSON / elektrik.md E9'dan
# doldurulur. Ham metin ADIM_HAM / KABLO_AD_HAM / SEMA_HAM'da kalır: rehber_denetim.kaynak_denetle orada (a) çözülemeyen yer tutucuyu,
# (b) yer tutucudan gelmeyen çıplak kritik sayıyı arar. Çözülemeyen yer tutucu COZUM_HATA'ya yazılır (metinde "⟦?…⟧" kalır).
import copy as _copy                                                # noqa: E402
import rehber_deger as _RDG                                         # noqa: E402

# ---------------------------------------------------------------- P10.7b2d-A: K1 / K2 demet alt adımları (planlama/d158/F10l-gunluk.md)
# Alt adım = demet (planlama/adim3/kablolar.json demet_sirasi). Metin yeniden yazılmaz: adımın is_ dizgesi yukarıda tek parça durur,
# burada paragraflarına ("\n") bölünür. Ana metin = paragraf 0 (uyarılar: kabuktan önce dur, akü ayrık), alt adımlar = sıradaki
# paragraflar, kaynaktaki sırayla. Tam metin ALT_TAM_HAM'da (rehber_denetim.demet_alt_denetle: başlık + alt adımlar = tam metin,
# paragraflar ardışık ve eksiksiz). Alanlar: paragraf (is_ paragraf sırası), demet (kayıttaki demet adları; metinde geçen kabloların
# demetinden gelmeli: denetim), genel (demetsiz alt adım: "son kontrol"), desen ("Kablo yolu N:" gösterim parçaları), sema (şemanın
# görünen adında geçen desen), sema_ok ({desen: gerekçe}: alt adımın metninde kablosu olmayan şema / parça), kablo_sec (adımın kablo
# listesinde bu alt adımda gösterilen madde, desen; liste adım düzeyinde kalır: rehber_kablo.BAGLANTI_TABLOSU P03'ü orada arar).
import os                                                           # noqa: E402
import re                                                           # noqa: E402
# P10.7b2d-A düzeltme turu 1 (F10l-kontrol D1, D2, N4): uc = bu alt adımda baraya takılan pabuçlar ("G12/+": anahtarlı bara, "G12/−":
# yıldız barası, "köprü/±": saplama köprüleri). Kayıttaki (kablolar.json bara-pabuc yerlesim) her bara ucu tam bir alt adımda; o alt
# adımın metninde saplama yer tutucusu; aynı saplamada 12 AWG pabuç (köprü dahil) incelerden önce; kabloyu anan öbür alt adım ucun
# alt adımını numarasıyla anar ("alt adım 17.5'te bağlandı"); yerlesim=True: yalnız yerleşim listesi (rehber_denetim.bara_uc_denetle).
DEMET_ALT = {
    "K1": [
        dict(ad="Toprak ve iki bara", paragraf=(1,), demet=("taban (K1)",), desen=("Kablo yolu 2:",),
             uc=("köprü/+", "köprü/−", "G05/−"), yerlesim=True),
        dict(ad="Ana hat ve şarj kolu", paragraf=(2,), demet=("taban (K1)", "etek (F1)"), desen=("Kablo yolu 1:",), uc=("G06/−",)),
        dict(ad="Akü ölçüm teli (G07)", paragraf=(3,), demet=("taban (K1)",), sema=("(G07,",)),
        dict(ad="Röle K1 ve ön şarj kartı", paragraf=(4,), demet=("taban (K1)",), desen=("Kablo yolu 3:",), uc=("G09/+", "G11/+"),
             # P10.7b2e kısım 2 (F10l-kare-inceleme 17.4): eski "sağ-önden" bakışta röle ve ön şarj kartı direğin arkasındaydı; ikisi de
             # önden bakanın solunda (x ≈ −112 / −98): sol-ön-üstten bakış. Röle + şarj kartına odak denendi, kare bağlamsız kaldı
             # (yalnız bir kutu ve kablo), kaldırıldı
             kamera=(-0.85, 0.9, 0.5)),
        dict(ad="Bara çıkışları: BTS7960B ve XL4016 A / B / C", paragraf=(5,), demet=("taban (K1)", "taban alt kat"),
             desen=("Kablo yolu 4:",), sema=("(G16,",), kamera=(0.6, 0.9, 0.5), saydam=("Elektronik katı",),
             uc=("G12/+", "G12/−", "G13/+", "G13/−", "G14/+", "G14/−", "G15/+", "G15/−", "G16/+", "G16/−")),
        dict(ad="PC817 #2 algı teli (G22)", paragraf=(6,), demet=("taban (K1)",), sema=("(G22,",), uc=("G22/+", "G22/−")),
        dict(ad="Sigorta kutusu çıkışları", paragraf=(7,), demet=("taban (K1)", "taban alt kat", "boyun", "etek (F1)"),
             desen=("Kablo yolu 9:",), uc=("G17/−", "G18/−", "G20/−")),
        dict(ad="Acil stop ve röle sürücüleri", paragraf=(8,), demet=("taban (K1)", "etek (F1)"), desen=("Kablo yolu 10:",)),
        dict(ad="Alt kat kartlarının öbür uçları", paragraf=(9,), demet=("taban alt kat",), sema=("(G19,",)),
        dict(ad="Enkoder, BTS sinyal ve sonar kabloları", paragraf=(10,), demet=("taban elektronik katı", "taban sonar"),
             desen=("Kablo yolu 11:", "Kablo yolu 12:"), sema=("(B02,", "(N01,", "(N02,", "(Q01,", "(Q02,"),
             # P10.7b2e kısım 2 (F10l-kare-inceleme 17.10, A 32.4): Kablo yolu 12 (B01) bu alt adıma geldi (rehber_metin.kablo_kapisi
             # istisnası); yolun direkten çıkan eski kısmı kadrajı direğin boyuna açıyordu, taban küçük kalıyordu: kadraj tabandaki
             # kartlara / sonarlara odaklanır, elektronik katı saydam (önizleme: B01 oran 0,68, Q03 0,79, şemalar ≥ 1800 px)
             kamera=(-0.6, 0.9, 0.5), saydam=("Elektronik katı",),
             odak=("Elektronik katı", "Sonar HC-SR04", "BTS7960 motor sürücü")),
        dict(ad="Direğe çıkan hatların taban kısmı", paragraf=(11,), demet=("taban elektronik katı", "boyun", "taban (K1)", "gövde (K2)"),
             kablo_sec=("Bağlantı tablosu P03",), kamera=(0.3, 1.0, 0.4),
             odak=("ESP32 taşıyıcı kart", "PCA9685 servo sürücü", "XL4016 servo 6 V C")),
        dict(ad="Son kontrol: K1'de enerji verilmez", paragraf=(12,), demet=(), genel="son kontrol"),
    ],
    "K2": [
        dict(ad="Kol servo uzatmaları", paragraf=(1,), demet=("kol sağ", "kol sol"), desen=("Kablo yolu 5:", "Kablo yolu 7:"),
             kamera="arka"),
        dict(ad="Kafa servoları, hat C", paragraf=(2,), demet=("gövde (K2)", "boyun", "taban (K1)"), desen=("Kablo yolu 6:",),
             kamera="arka", saydam=("Servo yuvası", "Boyun plakası", "Rulman yuvası", "Pan servosu", "Omuz traversi")),
        dict(ad="Kafa 12 V", paragraf=(3,), demet=("boyun",), desen=("Kablo yolu 8:",)),
        # P10.7b2e kısım 2 (F10l-kare-inceleme 32.4, A): B01'in eski yolu (Kablo yolu 12) 17.10'a geçti; karede yalnız U06. Şemanın
        # yanlış yerdeki taban ucu kablo listesi maddesi bu kartta basılır (kablo_sec)
        # P10.7b2f (F10m-kare-inceleme § 4.5): gri hazır USB kablosu gri direğin arka yüzünde zor seçiliyordu; direk saydam (renk
        # tablosu değişmez: hazir-usb tonu öbür sınıflarla ΔE00 eşiğine yakın, rehber_kablo.renk_farki_tablosu)
        dict(ad="ESP32 USB", paragraf=(4,), demet=("gövde (K2)",), sema=("(U06)",), kamera="arka", saydam=("Gövde direği",),
             kablo_sec=("şemasının (U06) taban ucu yanlış yerde",)),
        # P10.7b2e kısım 2 (F10l-kare-inceleme 32.5, 32.6): 32.5'te tünel opak servo yuvasının içindeydi (saydam), 32.6'nın karesinde
        # vurgu yoktu: hoparlör kablosunun (AU3) lehimi ve kutup kontrolü 32.6'nın metninde, şeması da oraya taşındı (32.5'te AU3
        # 281 px idi; 32.6'da ≈ 4800 px). Kafa ucu için arka kabuk saydam, kadraj PAM8403'e ve sol kabuğa odaklı
        dict(ad="Boyun demeti: tünelden geçirme", paragraf=(5,), demet=("boyun",), sema=("(H02)", "(U03,"),
             kamera=(-0.85, 0.5, -0.9), saydam=("Servo yuvası", "Boyun plakası", "Rulman yuvası")),
        dict(ad="Kafa uçları, hoparlör kablosu ve gövdeye inenler", paragraf=(6, 7), demet=("boyun",), sema=("(AU3)",),
             kamera=(-0.85, 0.62, -1.25), saydam=("Arka kafa kabuğu",), odak=("PAM8403 amfi", "Arka kafa kabuğu sol")),
        dict(ad="Göğüs ekranı 12 V", paragraf=(8,), demet=("göğüs", "taban (K1)"), sema=("(G20, G21",), kamera="arka"),
        dict(ad="Son kontrol: direğe tuttur", paragraf=(9,), demet=(), genel="son kontrol"),
    ],
}
# P10.7b2f: uç etiketi karede görünmeyen uçlar (rehber_gorunum.uc_isle). Anahtar (adım kodu, alt adım no; 0 = alt adımı olmayan adımın
# kendi karesi) → {uç kısa adı: neden}. Kaynak: FreeCAD'siz önizleme ölçümü (planlama/d158/F10n-gunluk.md § 5; Kablo yolu 12 kırpılmış
# GLB benzetimi, RehberTest.ucEtiket + gorunurlukFark, 1400 x 900): parça noktası güvenli alanın dışında ("kadrajın dışında") ya da
# parçanın görünen pikseli 0 ("başka parçaların arkasında"). Etiketlenmez; basılı sayfada "Uç karede görünmez" satırında nedeniyle.
# Üretimden sonra F10d uc_etiket denetimi aynı ölçümü yapar: burada olmayan görünmez uç hata, burada olup görünen uç bilgi.
_ARKADA = "bu bakışta başka parçaların arkasında"
_DISARIDA = "bu kadrajın dışında"
UC_ORTULU = {
    ("B3", 0): {"JGB37 arka sol": _ARKADA},
    ("K1", 2): {"Akü": "akü alt plakanın altında, " + _ARKADA},
    ("K1", 3): {"Arayüz kartı": _DISARIDA},
    ("K1", 4): {"BTS7960 sol": _ARKADA},
    ("K1", 6): {"PC817 modülü": _DISARIDA},
    ("K1", 8): {"Röle K1": _ARKADA},
    ("K1", 9): {"XL4016 çevre": "alt katta, " + _ARKADA},
    ("K1", 10): {"JGB37 arka sol": "arka motor tabanın altında, " + _ARKADA, "JGB37 arka sağ": "arka motor tabanın altında, " + _ARKADA},
    ("K2", 2): {"kafa tilt servosu": _DISARIDA},
    ("K2", 7): {"Sigorta kutusu": _DISARIDA},
}
ALT_TAM_HAM = {}          # alt adımlara bölünen tam metin (çapası silinmiş, göndermesi çevrilmiş): ana metin + alt adımlar = bu
ALT_KAYNAK_HAM = {}       # kaynaktaki is_ (çapalı, "madde N" göndermeli): rehber_denetim.gonderme_denetle bağımsız yeniden kurar
GONDERME_KAYNAK = {}      # çeviriden önceki alanlar {(adım, alan yolu): metin}
GONDERME_KAYIT = []       # dict(yer, kod, capa, hedef (1 tabanlı alt adım), metin): her çevrilen gönderme
GONDERME_HATA = []        # çözülemeyen gönderme (denetim D7 hata sayar; metinde "madde N" kalır)


# P10.7b2d-A düzeltme turu 1 (F10l-kontrol D2): alt adım numarası "<adım>.<alt adım>" ekrandaki / basılıdaki kart numarasıdır; adım
# numarası M6 tablosundaki sıradan (rehber_veri.py KODLAR ile aynı kural: "0" + tablo satırları; rehber_veri bunu sınar, uymazsa durur).
def m6_kodlar(yol=None):
    yol = yol or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                              "planlama", "adim4", "M6-montaj-sirasi.md")
    md = open(yol, encoding="utf-8").read()
    bol = md.split("## 2. Montaj sırası")[1].split("\n## ")[0]
    return ["0"] + [m.group(2) for m in (re.match(r"^\|\s*(\d+|—)\s*\|\s*([A-Z]\w*)\s*\|(.*)\|(.*)\|(.*)\|(.*)\|\s*$", ln)
                                         for ln in bol.splitlines()) if m]


M6_KODLAR = m6_kodlar()
ALT_ADIM_NO = {k: M6_KODLAR.index(k) for k in DEMET_ALT}
_CAPA = re.compile(r"^(\d+[a-z]?)\. ")
# "madde N" (isteğe bağlı "K1 " / "K2 " öneki ve -de / -da / -te / -ta (+ ki) eki). Başka adımın maddesi ("B6a madde 4") çevrilmez.
_GONDERME = re.compile(r"(?:\b(K[12]) )?\bmadde (\d+[a-z]?)\b('(?:de|da|te|ta)(?:ki)?)?")
_ADIM_ONEKI = re.compile(r"(\b[A-Z][0-9A-Za-z]*) $")


def _ek(no, ek):
    """Türkçe bulunma eki: alt adım numarasının son bölümünün okunuşuna göre (17.1'de, 17.4'te, 17.6'da, 17.10'da)."""
    if not ek:
        return ""
    n = int(no.split(".")[-1])
    son = n % 10 if n % 10 else n
    sesli = {1: "de", 2: "de", 3: "te", 4: "te", 5: "te", 6: "da", 7: "de", 8: "de", 9: "da", 10: "da", 20: "de", 30: "da",
             40: "ta", 50: "de", 60: "ta", 70: "de", 80: "de", 90: "da"}[son]
    return "'" + sesli + ("ki" if ek.endswith("ki") else "")


def capa_haritasi(tam_metinler, alt=None):
    """{adım: {çapa: (alt adım sırası 0 tabanlı, paragraf)}} ve çapası silinmiş paragraflar {adım: [paragraf]} (saf işlev; denetim de
    kullanır). Aynı çapa iki kez geçerse ikincisi "?<çapa>" olur (çözülmez, hata)."""
    alt = alt or DEMET_ALT
    harita, pars = {}, {}
    for kod, tam in tam_metinler.items():
        par = tam.split("\n")
        h = {}
        for n, g in enumerate(alt[kod]):
            for j in g["paragraf"]:
                m = _CAPA.match(par[j]) if 0 < j < len(par) else None
                if m:
                    h["?" + m.group(1) if m.group(1) in h else m.group(1)] = (n, j)
        harita[kod] = h
        pars[kod] = [_CAPA.sub("", p, count=1) if j else p for j, p in enumerate(par)]
    return harita, pars


def gonderme_cevir(metin, kod_bagli, harita, adim_no, yer="", kart=None, hata=None, kayit=None):
    """metin: K1 / K2 metninde çıplak "madde N" o adımın, her yerde "K1 madde N" / "K2 madde N" o adımın alt adımıdır; kod_bagli:
    metnin adımı (K1 / K2 değilse çıplak gönderme çevrilmez). kart: metin bir alt adımın paragrafıysa (alt adım sırası 0 tabanlı,
    paragraf): kendi alt adımına gönderme "bu alt adımda aşağıda / yukarıda" olur. Çözülemeyen gönderme hataya yazılır, metin
    değişmez (denetim D7 sayar)."""
    hata = hata if hata is not None else []

    def r(m):
        kod = m.group(1) or kod_bagli
        on = _ADIM_ONEKI.search(metin[:m.start()])
        if not m.group(1) and on and on.group(1) in ADIM:          # "B6a madde 4": başka adımın maddesi
            return m.group(0)
        if kod not in harita:
            return m.group(0)
        nj = harita[kod].get(m.group(2))
        if nj is None:
            hata.append("%s: %s madde %s çözülemedi (çapa yok)" % (yer, kod, m.group(2)))
            return m.group(0)
        n, j = nj
        no = "%d.%d" % (adim_no[kod], n + 1)
        if kayit is not None:
            kayit.append(dict(yer=yer, kod=kod, capa=m.group(2), hedef=n + 1))
        if kart is not None and kod == kod_bagli and n == kart[0] and not m.group(3):
            return "bu alt adımda " + ("aşağıda" if j > kart[1] else "yukarıda")
        return "alt adım " + no + _ek(no, m.group(3))
    return _GONDERME.sub(r, metin or "")


def _alanlari_cevir(o, kod_bagli, harita, yol, kart=None):
    if isinstance(o, str):
        GONDERME_KAYNAK[yol] = o
        return gonderme_cevir(o, kod_bagli, harita, ALT_ADIM_NO, yer=" ".join(yol), kart=kart, hata=GONDERME_HATA,
                              kayit=GONDERME_KAYIT)
    if isinstance(o, list):
        return [_alanlari_cevir(x, kod_bagli, harita, yol + (str(i),), kart) for i, x in enumerate(o)]
    return o


def _demet_bol(harita, pars):
    for kod in DEMET_ALT:
        a = ADIM[kod]
        ALT_KAYNAK_HAM[kod] = a["is_"]
        par = list(pars[kod])
        ana = _alanlari_cevir(par[0], kod, harita, (kod, "is_"))
        sira = []
        for n, g in enumerate(DEMET_ALT[kod]):
            t = "\n".join(_alanlari_cevir(par[j], kod, harita, (kod, "alt", str(n + 1), str(j)), kart=(n, j)) for j in g["paragraf"])
            e = {k: v for k, v in g.items() if k not in ("uc", "yerlesim")}
            sira.append(dict(e, is_=t, desen=tuple(g.get("desen") or ()), sema=tuple(g.get("sema") or ())))
        ALT_TAM_HAM[kod] = "\n".join([ana] + [g["is_"] for g in sira])
        a["is_"] = ana
        a["alt"] = True
        a["demet_alt"] = True
        a["sira"] = sira
    for kod, a in ADIM.items():                                      # adım düzeyi alanlar ve başka adımlardan K1 / K2 göndermeleri
        for alan in ("kontrol", "kablo", "not_", "baglanti_md", "erisim") + (() if kod in DEMET_ALT else ("is_",)):
            if alan in a:
                a[alan] = _alanlari_cevir(a[alan], kod, harita, (kod, alan))
        if kod not in DEMET_ALT:
            for n, g in enumerate(a.get("sira") or []):
                if g.get("is_"):
                    g["is_"] = _alanlari_cevir(g["is_"], kod, harita, (kod, "alt", str(n + 1)))


_HARITA, _PARS = capa_haritasi({k: ADIM[k]["is_"] for k in DEMET_ALT})
_demet_bol(_HARITA, _PARS)


def demet_grup_alanlari(g, kablo, kod="", n=0):
    """Veri alanları (rehber_veri.py, rehber_gorunum.py): demet, genel, kablo (adımın kablo listesinde kablo_sec'e uyan maddelerin
    sırası). Uymayan ya da birden çok maddeye uyan kablo_sec üretimi durdurur (sessiz düşüş yok)."""
    e = {}
    if g.get("demet") is not None and "paragraf" in g:
        e["demet"] = list(g.get("demet") or ())
    if g.get("genel"):
        e["genel"] = g["genel"]
    if g.get("kablo_sec"):
        sec = []
        for x in g["kablo_sec"]:
            m = [i for i, t in enumerate(kablo) if x in t]
            if len(m) != 1:
                raise SystemExit("demet alt adimi %s.%d: kablo_sec %r kablo listesinde %d maddeye uyuyor" % (kod, n + 1, x, len(m)))
            sec += m
        e["kablo"] = sec
    return e


def demet_sema_coklu(desenler, ogeler):
    """desenler: alt adım başına desen listesi; ogeler: [(kimlik, görünen ad)]. Tam bir alt adıma uymayan öğeler (ileti listesi)."""
    out = []
    for k, ad in ogeler:
        ns = [n + 1 for n, ds in enumerate(desenler) if any(x in ad for x in ds or ())]
        if len(ns) != 1:
            out.append("%s %s: %s" % (k, (ad or "")[:50], ns or "hicbiri"))
    return out

ADIM_HAM, KABLO_AD_HAM, SEMA_HAM = _copy.deepcopy(ADIM), _copy.deepcopy(KABLO_AD), _copy.deepcopy(SEMA)
COZUM_HATA = []


def _coz(o, yer):
    """Yerinde çözümleme (sözlük / liste aynı nesne kalır); demet ve metin yeniden kurulur."""
    if isinstance(o, str):
        return _RDG.degerler().coz(o, COZUM_HATA, yer)
    if isinstance(o, dict):
        for k in list(o):
            o[k] = _coz(o[k], "%s %s" % (yer, k))
        return o
    if isinstance(o, list):
        for i in range(len(o)):
            o[i] = _coz(o[i], yer)
        return o
    if isinstance(o, tuple):
        return tuple(_coz(x, yer) for x in o)
    return o


_coz(ADIM, "ADIM")
for _n in list(KABLO_AD):
    KABLO_AD[_n] = _coz(KABLO_AD[_n], "KABLO_AD %d" % _n)
SEMA[:] = [_coz(_s, "SEMA %s" % _s[1]) for _s in SEMA]
