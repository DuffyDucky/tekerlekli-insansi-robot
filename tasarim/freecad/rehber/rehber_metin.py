# 3B montaj rehberi: adım koduna bağlı elle yazılmış metinler (CAD'den bağımsız; saf Python, FreeCAD'siz import edilir).
# Adımların sırası, iş tanımı, bağlantı elemanı, alet ve erişim notu planlama/adim4/M6-montaj-sirasi.md tablosundan okunur
# (rehber_veri.py). Burada yalnız tablonun vermediği şeyler var: kısa başlık, faz, kontrol listesi, kablo kancası, uçuş yönü,
# süre düzeltmesi. Bir adım burada yoksa rehber yalnız M6 tablosuyla çalışır.
#
# Alanlar (hepsi isteğe bağlı):
#   baslik  : kısa başlık (yoksa M6 "Parça / iş" sütunu)
#   kontrol : kontrol listesi maddeleri
#   kablo   : kablo kancası (bu adımda hangi kanal / geçit / cırt boş bırakılır)
#   ucus    : bu adımın ana parçalarının geliş yönü (sağ taraf için; sol parçalarda X aynalanır). (x, y, z) ya da "radyal"
#   ucus_bag: alt montaj (tezgâh) robota bağlanırken geliş yönü
#   sure_dk : süre (dakika, tahmini); yoksa bağlantı sayısından tahmin edilir
#   not_    : ek uyarılar

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
        "Baskı listesi (`planlama/baski-listesi.md`): 50 parça basıldı, destekler temizlendi",
        "Isıl gömme somunlar havyayla takıldı (M3 / M5; M7 kuponundaki sıcaklık ve derinlik)",
        "Sigma profiller kesildi: 2 uzun ray, 3 ara ray, gövde direği, omuz traversi; uçlar çapaksız, dik",
        "Alt plaka (Al 3 mm) ve iki kontrplak kat lazerden geldi; delikler kumpasla tutuyor",
        "Alet seti: alyan 2 / 2,5 / 3 / 4 / 5 (5 mm uzun küresel uçlu ≥ 150 mm), PH0 / PH1, 5,5 ve 7 mm anahtar, lokma, havya",
        "Bağlantı elemanları bu rehberin adım listelerine göre kutulara ayrıldı (adım başına bir kutu)",
        "Sol omuz ve sol kol parçaları aynalı basıldı (sağ ile karıştırma: üstüne 'SOL' yaz)",
    ],
    kablo=["Henüz kablo yok. Servo kablolarını kesme, kısaltma: uzunlukları kol içi yol için hesaplı (300 mm)."],
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
            "Üst kanalda 2 çekiç somun boyun için şimdiden dursun (14. adım E1)",
        ],
        kablo=["Travers arkası S1 kablo uçları için boş kalsın (G4)"],
        ucus=(0, 1, 0),
    ),
    "B1a": dict(
        baslik="Tezgâh: alt plakaya burçlar ve akü takozu",
        kontrol=[
            "Naylon burçlar alttan, vidalar plakanın altından; burçlar elle sıkı, plastik ezilmesin",
            "Akü ön takozu M3×8 ile ısıl gömme somuna (tork tornavida 0,5 N·m civarı)",
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
        kontrol=[
            "Kabuk takılmadan önce burada dur: taban kabloları bağlanır, ölçülür, test edilir",
            "Akü → XT60 → ana sigorta → ana anahtar → sigorta kutusu → röle → baralar (`planlama/adim3/elektrik.md` blok şema)",
            "Motor + enkoder, sonar, acil stop hattı (mantar etek adımında takılır, uç bırakılır)",
            "Multimetre: kısa devre yok (akü ayrık), XL4016 çıkışları 6 V / 6 V / 5 V'a ayarlandı",
            "Motor yön testi: her yan ileri komutta ileri döner",
        ],
        kablo=["Kablo listesi: C işi, 5. hafta (yer tutucu). Şimdilik güzergâh: taban kablo yolu şemaları (renkli çizgiler)"],
    ),
    "C1": dict(baslik="Gövde braketleri", ucus=(1, 0, 0)),
    "D1": dict(baslik="Omuz gövdesi → travers", ucus_bag=(1, 0, 0)),
    "E1": dict(baslik="Boyun → travers", ucus_bag=(0, 1, 0)),
    "E3": dict(baslik="Kafa → tilt hornu", ucus_bag=(0, 1, 0)),
    "K2": dict(
        baslik="Kablolama kapısı 2: gövde içi",
        kontrol=["Kabuktan ÖNCE: servo uzatmaları, kafa 12 V, Nextion kablosu, sinyal hatları direğe bağlanır",
                 "S1 kablosu G4'te kasetten içeri girer: uç travers arkasında bırakılır"],
        kablo=["Kablo listesi: C işi, 5. hafta (yer tutucu)"],
    ),
    "F1": dict(baslik="Taban eteği", ucus="radyal"),
    "F2": dict(baslik="Gövde alt ve orta bantları", ucus="radyal"),
    "F3": dict(baslik="Göğüs bantları ve Nextion", ucus="radyal"),
    "F4": dict(baslik="Omuz bantları", ucus="radyal"),
    "G1": dict(baslik="Omuz göbeği → S1 hornu", ucus_bag=(1, 0, 0)),
    "H1": dict(baslik="Dirsek modülü → üst kol tüpü", ucus_bag=(0, -1, 0)),
    "F5": dict(baslik="Arka servis kapağı", ucus=(0, 0, -1)),
}

# M6 analizinde "CAD değişikliği isteyen" bağlantılar (rehberde "M6 CAD sonrası değişecek" bayrağı). YOK sınıfı M6 JSON'dan
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
