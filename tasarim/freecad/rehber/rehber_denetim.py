# 3B montaj rehberi: metin ve parça listesi denetimi (F7b, P7.2). Saf Python; FreeCAD ve tarayıcı istemez.
#   python tasarim/freecad/rehber/rehber_denetim.py            # rehber/veri/rehber-veri.json üzerinde; özet ekrana, çıkış 0 = temiz
# rehber_uret.py her koşuda bunu çağırır ve tarayıcının ekrana bastığı metni (her adımın paneli, yazdir.html) de verir; sonuç
# planlama/rehber/kontrol.json "denetim" alanına yazılır.
#
# 1) ASCII kalıntı: ekranda görünen her metinde Türkçe harfi eksik kalmış kelime (ör. "mantari", "cikis", "govdesi").
#    Kelime: harf dizisi; kod (`...` ve <code>), kesme işaretinden sonraki ek (M6'daki), 3 harften kısa ve CamelCase marka adları atlanır.
#    Kalıntı = (a) rehber_metin TR / TR_EK sözlüğünde Türkçe karşılığı olan ASCII kelime (çeviri uygulanmamış), (b) büyük harfli
#    kelime kısaltma listesinde değilse (TAHMIN gibi), (c) ASCII_TAMAM listesinde olmayan her ASCII kelime (gözden geçirilmemiş).
#    ASCII_TAMAM: Türkçe harfi olmayan doğru Türkçe kelimeler ve teknik / İngilizce terimler (elle gözden geçirildi, F7b).
# 2) Parça listesi gruplama: her satırdaki parçaların adı (sondaki açıklama, FreeCAD eki ve sağ / sol atılınca) tek ve satır adıyla
#    aynı olmalı; adımın her parçası tam bir satırda. Karşılaştırma için eski kural (kod + tür + renk) aynı veride de sayılır.
# 3) Kafa / hoparlör / hub tutarlılığı: bileşenin yeni göründüğü adımın metni bileşeni anıyor mu; eski ifadeler (7", LCD,
#    MAX98357A, ESP32 USB boyundan) yalnız "eski / kalktı / yok" bağlamında mı. Bağlam kelimesi desenin ±60 karakteri içinde
#    aranır; bağlamla affedilen cümleler "affedilen" listesine yazılır (insan gözden geçirsin).
# 4) Zorunlu uyarılar (F7b-kontrol D-1, O-1…O-3): güvenlik talimatı adım metninde duruyor mu (Touch VBUS, köprülenmez, regülatör
#    ayarı, 1N5819 yönü, TVS kutbu, enerjisiz çalışma).
# 5) Bağlantı satırları: adımın her bağlantı elemanı parçası tam bir bağlantı satırında (satır tümden düşerse yakalanır).
# 6) Yasak talimat (F7c, F7b-kontrol D-1'): (4) yalnız uyarının VARLIĞINA bakar; eklenen yasak talimatı yakalamaz. Bu denetim tüm adım
#    metinlerinde yasak kalıpları arar: köprüleme ("köprüle", "köprülenir", "köprü teli"), akü bağlıyken iş ("akü bağlıyken bağla",
#    "akü bağlı olabilir"), enerji varken bağlantı ("enerjiliyken tak", "gerilim altında lehimle"). Olumsuz biçim ("köprülenmez",
#    "köprüleme", "takma") ve olumsuzlama kelimesi ("asla", "hiçbir zaman", "yasak", "değil") istisnadır; istisnalar
#    "yasak_affedilen" listesine yazılır (insan gözden geçirsin). "değilse" olumsuzlama sayılmaz (koşul: "takılı değilse köprüle").
#    F7c düzeltme 1 (F7c-kontrol D-1, D-2): olumsuzlama yalnız eşleşme sonunun yan cümlesinde geçerli ("takılı değil, köprüle" yakalanır);
#    ek kalıplar "devre dışı bırak", "kısa devre et / yap", "yerine tel / kablo", "sigortası / XT60 takılıyken", "gerilim varken",
#    fiil "değiştir", "bağlantı yap"; "akü … takılı" yalnız öznesi akü iken ("Akü ön takozu … takılı" tutmaz).
#    F7d (F7c-kontrol D-6', D-7): köprüleme eş anlamlıları ("mantar NC uçlarını birleştir", "iki ucunu birbirine bağla / lehimle /
#    değdir"; yalnız mantar, acil stop, NC, ana anahtar, sigorta, röle, kontak, 5 / 12 V, artı / eksi bağlamında), "röleyi elle kapat",
#    enerji önekine "ana anahtarı açtıktan sonra", "aküyü taktıktan sonra", "enerji verdikten sonra". Önek ile fiil arasındaki pencere
#    (en çok 120 karakter) yalnız enerjiyi bitiren ifadede ("ana anahtarı kapat", "aküyü ayır", "enerjiyi kes"; olumsuz ekli
#    "ayırmadan", "kesmeden" kesmez) kesilir: "Ana anahtar açıkken … gözle, bitince … ayır ve uçları sök" tutmaz; çıplak sıra bağlacı
#    (F7d düzeltme 1, O-1: "açıkken birkaç saniye sonra … tak" tutar), virgül ve "ve" kesmez (liste içi: "açıkken F1 (20 A), F3 (5 A,
#    kafa) ve hat sigortalarını tak" tutar). "artı" / "eksi" kelime sınırıyla ("artık", "eksik" tutmaz; D-2).
# 7) Görünen parça adında FreeCAD kopya eki (sondaki 0NN; F7b-kontrol D-6) 0 olmalı.
import os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import rehber_metin as RM                                          # noqa: E402
import rehber_deger as _RDG
import rehber_kritik as _RK                                        # noqa: E402  P10.7b1 düzeltme turu 1: yer tutucu çözümleyicisi

KISALTMA = {
    "AWG", "BNO", "BOM", "BTS", "CAD", "CSI", "DIN", "ESP", "GPIO", "HDMI", "ISO", "IBT", "JR", "LCD", "LED", "LM", "MOSFET", "NC", "PC",
    "PCA", "PETG", "PLA", "PT", "PVC", "QLED", "TVS", "USB", "VBUS", "VESA", "VHB", "WAGO", "XT", "XL", "CF", "TPU", "PWM", "EN", "IS",
    "DS", "MG", "SY", "ASW", "NP", "BE", "CP", "PAM", "UART", "IMU", "DC", "AC", "LIPO", "LFP", "PCB", "STEP", "SOL", "TOUCH",
    "IN", "OUT", "GND", "VCC", "VIN", "RGB", "SD", "OK", "ID", "XVF", "MAX", "IMAX", "HP", "CAPQLED", "AA", "AAA", "SMD", "NO",
    "FPC", "AI", "HAT", "KAPI", "ZZ", "RS", "NTC", "IP", "MCB", "SSR", "MP", "ABS", "NPT", "ISB", "NEMA", "DSP", "LPC", "MAH", "JQC",
    "BMS", "KAPAK", "IPS", "JGB", "LOW", "HIGH", "WROOM", "RESPEAKER", "MIC", "DTR", "RTS",
    "VOUT", "SDA",                                                 # P10.7b1 üretim uyumu (S1): kablo tablosu satırlarından
}
# Türkçe harfi olmayan doğru kelimeler ve teknik terimler (küçük harf). Yeni bir ASCII kelime ekrana girerse denetim "bilinmeyen"
# der: ya TR_EK'e karşılığı eklenir ya da gözden geçirilip buraya yazılır. F10f: ilk iki satır kol kablo yolu metinlerinin kelimeleri
# (32 kelime, gözden geçirildi: Türkçe harfi olmayan doğru yazımlar; "voksel" teknik terim). Üçüncü-dördüncü satır F10f düzeltme 1
# metinlerinin 19 yeni kelimesi (gözden geçirildi, hepsi Türkçe harfi olmayan doğru yazım). Beşinci satır F10f düzeltme 2 metin ve şema
# adlarının 8 yeni kelimesi (gözden geçirildi, hepsi doğru yazım). P10.7b1 üretim uyumu (S1): "turuncu … gri" satırı panelin kablo
# tablosundan gösterdiği lejant / kb kelimeleri ve "Birden" (app.js karışık sınıf notu); hepsi Türkçe harfi olmayan doğru yazım.
ASCII_TAMAM = set("""
hepsine elin ekli kolunun dayanana pulla lehimden lehimi
artanla denenmedi ekler ekseninin ekten girdi gerilmeden hepsinden kabloyla kablonun kendisi kuruldu lopu modeldeki orada oturtma
penceresinden pimler servosunun sokmadan somunla sonraki tabana tambura tamburda tamburdan tarama tutkalla voksel yatar yolun dereceye
beri bekler demette eklendi indirme itme kablosuna kasetin kesintisiz lopuyla pencerede penceresinde penceresine servonun soluk
tamburdaki uzatmalara yay yaylar
eksik ilkesi koruyucunun saplamaya zincir
turuncu mor koruma enkoderle okunur kapatma birden besleyen klemensi liste analog beyaz gri
acil active adafruit adapter adaptor adet akim al alet alma alt alttaki alttan alyan alyanla amfi ana anahtar anahtara ancak anot ara
arazi arka arkadan arkaya array artan ay ayak ayar az bak bakar bakma bant bara baradan bas basinca bilek bilezik bileziklerine
bindirme bindirmeleri binmiyor bir birbirine blok bobini bobinine boss boy boyda boynu boyun boyuna boyunca boyunda boyundan bozma
braket braketi braketine braketleri braketlerde braketlerine brakette bu bundan burada buradan buraya burcu cable camera case cebe
cebi cebinden cep ceplerinde cepte cepten cerrah cetvel cooler da daki dan de deki den dene denetledi derin derinlik destek
destekler destekleri devre devreye dibinde dik dikme dikmeler direk direnci dirsek disk diyor diyot diz dokunmatik dolgu dudak dur
dursun duvar duvarda ek ekip ekle eklenir ekran ekrana eksen eksende eksenel ekseni ekseninde eksenine eksi el eldeki elden
elektronik eli elle en engelsiz enkoder enkoderli erkek eski et etek etiketle etiketli ezilmedi ezilmesin ezilmiyor fark flans
gelecek geldi gelince gelir gelmesi gerekir geri gerilimi gerilmiyor gerisinde gibi gidecek gidenler girecekler girer giriyor
girmedi girmesin girmez hafif halka hat hatta havada havya havyayla header hedef her hesap hissi hizada horn horna hornu hornuna
hub iken iki ile ileri ilk ilmek ince inch iner ip ipi iskelet iskeleti iskeletine it kablo kablolar kablolama kablolu kablosu
kablosunda kablosunu kabuk kabuklardan kabuktan kadar kafa kafada kafadaki kafaya kalan kamera kanal kanala kanalda kanaldan kanat
kapak kapakla kapasitesi kapasitif kapat kaplin kaplinler karar kare kart kartlar kasa kasadaki kasaya kaset kasete kaseti kasetine
kat kaynak kaynakta kaynaktaki kenar kesildi kesilir kesim kesit kesitler kesiyor keski kesme klemens klemensleri kod kol kola
kolay kolda kollar komutta komutun kontak kontra kontrol kontrplak konumda kopmuyor koy kulak kulaklar kullanma kumpas kumpasla
kupon kuponundaki kutu kutulara kutuplar kutusu kutusuna lale lazer lazerden lehim lehimle listedeki listelerine listesi
listesinde listesinden lobu lokma lop lu mafsal makaron makaronla makas mantar mantara masada mengeneyle merkez merkezine mic micro
mil mili milin milinden milini mini mm model modelde module montaj motor motordan motorlar mu muadil multimetre mumlu naylon
nextion nin nokta ofset ofsetsiz ohm oku okur olabilir oluk olur omuz omuzda omuzlar onlar onun orta ortada ortaya oturdu oturma
oturt oturur pabucu pan panel panelde panelden panele paneli panelinde paneline paralel ped pedine pencereden penceresi pensesi
pertinaks pim pimi pin plaka plakadaki plakaya plastik pololu polyester port profiller pul pulsuz pulu radyal raspberry ray raya
raylar raylara raylarla referans rehber rehberin renkli resmi robolink robot robota robotta robotu robotun rulman rulmanlar
saplama saplamalar sarar seeed sehpada sehpaya serbest seri servis servo servolar servosu servosundan servosunu servoyu ses set
seti si sigma sigorta silikon simetrik sinyal sinyalleri sok soket sol solu solunda somun somuna somunlar somundan somunu
somunuyla son sonar sonarlar sonra soyucu stobun stop stp su ta taban tabandan tabla tablosu tahmini tak takarken takma takmadan
takoz takozu tam tambur tamburu tarafa taramada te teker tekerden tekerler teki temiz temizlendi ten terazisi ters test testi
testinden teyit tilt toprak tornavida travers traversi traversin tut tutkal tutmazsa tuttur tutucu tutuyor ucu ucundan ucunu uzatma
uzatmalar uzatmaya uzun var ve verir victron vida vidalar vidaya waveshare with ya yaka yalpa yan yana yanak yanaktaki yanda yatay
yaz ye yedek yer yerde yere yeri yerinde yi yok yol yolla yollar yollu yolu yoluna yolunun yu yuva yuvada yuvalar yuvaya zarf
braketin brakete saydam yerinden yolda karede arkada kapaklarda bantta
zeminden zorlarsa
renk
ama bantla banda beslenir besleme besler bekliyor birlikte boylar burca cam cama dahil dahili damar daldan dayamalar delik delikler
delikleri deliklerine deliklerini deliklerinin delikli delikte delikten demet demeti demetin demetine dev direkten dizi dolu duvara
duyulabilirlik elde emas gelen gerilim gider giden gidenlere hepsi hornun hornunda inenler inmesi iskeletinin jeti kablosunun
kabuklarla kabuktaki kama kameraya kapaklar kenarda kesik kutup lens lensi listede multimetreyle notlar notu oradan pedle power
sallanmadan servoya solundan soluna tabanda tabladaki tablaya tahmin takozuna takozunda teyidi tepe testte testten tipi touch
ucunda ucunun veri vidala yanaklar yap yasla yerine yerini yerleri profil yeni rehberi taslak sayfa
beslemez bitince depo diyodu direnciyle enerjili enerjisiz enerjisizken enerjiyi genel gerekmez ikinci kademesiyle kapasite kaynakla
katot kendi kes kontroller kutbunu madde multimetrenin teline tek tutar varsa yazan yeniden
enerji gerilimsiz sonu sonunda takozda tekerlekler verilmez yerden zaman
ver kapanmaz komutu yokken yine tekerlerin kimse mantarda kural portu resetlenmemeli boot dizisi hedefleri almadan zaten
komutuyla tekere kesmedi teyidiyle bitti devam
saat bileklik bobinleri kolu program bilinmiyor pini kapatabilir klemensine siyah panelindeki dal ise
anahtardan etekteki sigortadan kesiti kademesinde serbestken bip gerilimli olurdu multimetreyi kademesine otomatik soketine
soketinde atar klemensinin ucuna klemensin okundu barada teli
hattan rehberdeki buna hangi kuyruklu ucundaki metal pimleri gerilimlidir kesmez pimlere cinsi verilene
klemenslere dar kata olmayan yetecek demetleyip topla yolunu toplama bilinen konu inerken burcuna gelmeden uzanma klemenslerine
karta etiketleri okunuyor biri kabuklar denetimi kafadayken tavan getir uzan bekleyen eki kaba yerel olarak
hornunu konumdayken miline indikten inen milde milinde pres ona tarifinden indir kafadaysa pime aradaki ortak hacim
temas ediyor soldan dikey bindirmesi solun girmiyor grubu eden yani
milinin durum alete bantlar braketler solunu braketlerin yandan braketlere bindirmesini yoldan oturtarak bindirmesine birimi
bindirmelerini esneterek metnindeki maddeyi izle bindirmelerine metni takoza maddeye gerilmesin tabloda birim
preslenir yerindeyken koldan kolundaki
ahmet bekle bekleme beklemeyle beklenir belgede belirler beslemesiz beslenirse bildirildi bilinmeyen birinde bobin bobinlerin boyu cihaz
deneme denemesi denenir derse dolma duran edilir efe eklenmedi firmware geriliminde giren harici hata hesapla jak kablajdan kabukta kabul
kalaylanmadan kalem kapanmadan kapatmadan karara kartta kimlik kimlikler kimlikleri klemense klemensle kollu kordon kurmadan
kurulamayabilir kurulmadan kutudakiler kutunun kutusundan kutusunun kuyruk lehimli lejant makaronlu masa mavi motorun olup ortadaki
oturuyor parantez pedi pedlerinin pinler pinleri plaket renginde reset reseti sesi sigortalar soketin soketinin soru standart stopta
tablo tablodaki tabloya tel telinin telli tepme teslimde toplam ucun verilir yetmez
durur yoksa yerindeki klemenste enerjide denemeleri yanmaz zemin istisna inceyse klemensinden nadiren yuvalarda enkoderler
zincirin teliyle kesitte yerlerde kablosuyla animasyonda gidiyor uygulanmaz
""".split())
# F10g (P10.5b, K56 / K57): "preslenir …" satırı G3 / H0c metinlerinin 4 yeni kelimesi (gözden geçirildi, hepsi Türkçe harfi olmayan
# doğru yazım). P10.7b1: ondan sonraki altı satır elektrik metinlerinin (tek kablo kaynağına bağlanan K1, E3a, E4, K2, F1, F3, F5,
# KABLO_AD, SEMA) 93 yeni kelimesi (gözden geçirildi: Türkçe harfi olmayan doğru yazımlar; "firmware" teknik terim, "Ahmet" / "Efe"
# kişi adı). Düzeltme turu 1: son satır Ö4 köprüsü, teslim maddeleri (T8, K04, KT3), F5 yuva cümlesi ve KABLO_AD metinlerinin 14 yeni
# kelimesi (gözden geçirildi, hepsi Türkçe harfi olmayan doğru yazım). Açık işler turu: "kutuda" çıktı (E4 cümlesinden kalktı); son
# satır Ö4 köprü teli, madde 8 köprü listesi, KT3 ara kablosu ve E4 metinlerinin 8 yeni kelimesi (gözden geçirildi, doğru yazım).

# 3) Kafa / hoparlör / hub: (bileşen anahtarı parça adında, metinde aranacak kelimeler)
BILESEN = [
    ("Yüz ekranı WaveShare", ("QLED",)), ("Ekran tırnağı", ("tırnak",)), ("Kamera Raspberry Pi Camera", ("kamera", "Camera Module")),
    ("ReSpeaker", ("ReSpeaker",)), ("USB ses kartı", ("ses kartı",)), ("PAM8403", ("PAM8403",)), ("Pololu D24V50F5", ("D24V50F5",)),
    ("SY8205", ("SY8205",)), ("TVS P6KE6V8A", ("P6KE6V8A",)), ("Hoparlör 40", ("Hoparlör", "hoparlör")), ("USB Hub", ("hub",)),
]
# Eski ifadeler: cümlede bağlam kelimesi yoksa çelişki sayılır
ESKI = [(r"\b7\s*(?:\"|inç|inch)", "7 inç ekran"), (r"(?<!11\.6inch HDMI )\bLCD\b", "LCD (göğüs ekranı ürün kodu \"11.6inch HDMI LCD\" hariç)"), (r"MAX98357A", "MAX98357A"), (r"\bNextion\b", "Nextion"),
        (r"ESP32 USB[^.;\n]*boyun", "ESP32 USB boyundan"), (r"kafa USB", "ESP32 → kafa USB"),
        (r"(?:^|[^ğ])\bkamera\b[^.;\n]*\btabla", "kamera tablada")]
BAGLAM = ("eski", "kalktı", "yok", "değil", "girmez", "geçmez", "çıktı", "05.11 öncesi", "artık")   # "çıkar" çıktı (D-1)
BAGLAM_PENCERE = 60
# 4) Zorunlu uyarılar: (adım kodu, aranacak desen, ad). Desen adımın is_ + bağlantı + kontrol + kablo + not metninde aranır.
ZORUNLU = [
    ("E3a", r"köprülenmez", "iki 5 V hattı köprülenmez"),
    ("E3a", r"Her iki 5 V çıkışına bir P6KE6V8A", "iki P6KE6V8A (Pi hattındaki modelde yok)"),
    ("E3a", r"katot \(çizgili uç\) \+5 V", "TVS kutbu"),
    ("E3a", r"akım sınırlı tezgâh kaynağıyla", "SY8205 ölçümü akım sınırlı kaynakla"),
    ("E4", r"Touch VBUS", "Touch VBUS ölçümü"),
    ("E4", r"köprülenmez", "iki 5 V hattı köprülenmez"),
    ("K1", r"akü ayrık", "bağlarken akü ayrık"),
    ("K1", r"K1'de enerji verilmez", "K1'de enerjili ölçüm yok (tezgâhta)"),
    ("K1", r"köprülenmez", "mantar / ana anahtar köprülenmez"),
    ("F1", r"Bağlarken akü ayrık", "F1 bağlarken akü ayrık"),
    # F7c (D-10): ilk enerji iki aşamalı; F1'de kafasız (röle kapanmaz), devreye alma / ön şarj / motor yön testi F5'te
    # F7c düzeltme 1 (O-1): aşama 1'de F1 takılı değil (röle kontakları enerjisiz, ESP32 programı bilinmese de); mantar ölçü noktası (O-2)
    ("F1", r"İlk enerji, aşama 1 \(F1 sonu, kafasız\).*röle K1 ve K2'nin kontakları enerjisiz.*BTS EN = 0", "F1 ilk enerji aşama 1 (bara enerjisiz)"),
    ("F1", r"F1 \({a.F1}[^)]*\)[^.]*takılı değil", "F1 aşama 1: F1 ve dal sigortaları takılı değil"),
    # P10.7b1: WAGO kalktı; ölçü noktası yıldız barası (M5 saplama)
    ("F1", r"PC817 #1 giriş klemensinin \+ ucuna.*yıldız barasının.*mantar uçlarına takma", "F1 mantar ölçü noktası"),
    ("F1", r"[Tt]ekerlekler yerden kesik", "F1 tekerlekler yerden kesik"),
    # F7d (F7c-kontrol D-6', D-8, D-10): kademe, uçların takılma / sökülme sırası, şarj girişi
    ("F1", r"akü ayrıkken multimetreyi DC V kademesine al.*kırmızı ucu V soketine", "F1 mantar ölçümü DC V, uç akü ayrıkken"),
    ("F1", r"XT60'tan ayır, sonra ölçü uçlarını sök", "F1 sökme sırası (akü ayrıldıktan sonra uçlar)"),
    # P10.7b1: şarj sigortası (kablolar.json koruyucular.hat-sarj; değer yer tutucudan)
    ("F1", r"şarj kolunun {a.hat-sarj} {bicak.hat-sarj} sigortası takılı değil", "F1 aşama 1: şarj kolu sigortası takılı değil"),
    ("F1", r"süreklilik kademesinde", "F1 mantar NC sürekliliği (akü ayrık)"),
    ("F5", r"İlk enerji, aşama 2.*BTS EN = 0.*ön şarj dizisi.*K1 düşer", "F5 ilk enerji aşama 2 (ön şarj, mantar)"),
    ("F5", r"[Tt]ekerlekler yerden kesik", "F5 tekerlekler yerden kesik"),
    ("F5", r"Akü XT60 ayrık, ana anahtar kapalıyken F1 \({a.F1}\).*tak", "F5 sigortalar akü ayrıkken"),
    ("F5", r"kollar düşer", "F5 mantarda kollar düşer"),
    ("F5", r"Şarj kolunun {a.hat-sarj} {bicak.hat-sarj} sigortası bu aşamada da takılı değil", "F5 şarj kolu sigortası takılı değil"),
    # P10.7b1: E9 ön şarj dizisi (değerler yer tutucudan: elektrik.md E9, pin haritası)
    ("F5", r"{gpio.ROLE_K2_ONSARJ} = 1 \(röle K2\) → en az {ms.onsarj} bekle \(boş aküde {ms.onsarj_bos} önerilir\) → {gpio.BARA_DURUM} "
           r"\(PC817 #2\) LOW teyidi", "F5 E9 ön şarj: en az bekleme, PC817 #2 LOW teyidi"),
    ("F5", r"K2 toplam en çok {s.k2_en_cok}", "F5 E9: K2 en çok süresi"),
    # P10.7b1 düzeltme turu 1 (F10h-kontrol M20, §2-8, §2-9): G22 algı teli sigortası, yedek F2 ve uç yuvalar
    ("F5", r"PC817 #2 algı telinin \(G22\) {a.hat-G22} {bicak.hat-G22} sigortasını tak", "F5 G22 algı teli sigortası takılır"),
    ("F5", r"yedek sigorta F2 \({a.F2} {bicak.F2}; hiçbir dalı beslemez\) ve F6 \({a.F6}, göğüs ekranı, 14\.11; kutunun {yuva.F6}\. yuvası\)",
     "F5 H1: uç yuvalarda F2 yedek ve F6"),
    # F7d düzeltme 1 (F7d-kontrol D-1, O-2): "Kollar aşağıda başlar" kendi satırıyla; sigortadan sonra şarj pimleri gerilimli
    ("F5", r"Kollar aşağıda başlar", "F5 kollar aşağıda başlar"),
    ("F5", r"pimleri, akü XT60'tan ayrılmadıkça gerilimlidir: ana anahtar da mantar da bu kolu kesmez",
     "F5 şarj pimleri sigortadan sonra gerilimli"),
    # F7c (D-12): XL4016 ayarı ve PC817 ölçümü kartların takıldığı adımda da yazar
    ("B3", r"Kartlar takılmadan tezgâhta.*XL4016 A / B", "B3 XL4016 tezgâhta ayar"),
    ("B5a", r"Kartlar takılmadan tezgâhta.*XL4016 C", "B5a XL4016 C tezgâhta ayar"),
    ("B6a", r"Kartlar takılmadan tezgâhta.*PC817", "B6a PC817 tezgâhta ölçüm"),
    ("K2", r"akü XT60 ayrık", "K2 enerjisiz"),
    ("K2", r"1N5819: anot hub \(Pi\)\s+tarafında, katot ESP32", "1N5819 yönü"),
    ("K2", r"regülatörü \(LM2577 \+ LM2596\) ekrana bağlanmadan", "göğüs regülatörü 12 V ayarı"),
    ("F3", r"regülatör çıkışını yeniden ölç", "göğüs 12 V fişten önce ölçüm"),
    # F7d (D-5, D-9): göğüs 2 A akü ayrıkken; ölçüm sırası açık; K11 b'de ölçümsüz fiş yok
    # P10.7b1: göğüs ekranı sigortası F6 3 A standart (K11 a); K11 b dalı kapandı
    ("F3", r"Akü XT60 ayrık, ana anahtar kapalıyken göğüs ekranının F6 {a.F6} sigortasını \({bicak.F6} bıçak, sigorta kutusunun "
           r"{yuva.F6}\. yuvası\) tak", "F3 göğüs F6 akü ayrıkken (değer, tip, yuva)"),          # açık işler turu: fiil desende (B27)
    ("F3", r"Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç", "F3 ölçüm: akü ana anahtar kapalıyken"),
    ("F3", r"Bitince ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök", "F3 ölçüm sonu: ana anahtar, akü, uçlar"),
    ("F3", r"Dal K11 a ile ana anahtar sonrası, röle öncesi.*acil stopta açık kalır", "F3 göğüs dalı K11 a (acil stopta açık)"),
    ("F3", r"12 V fişini takmadan önce regülatör çıkışını yeniden", "F3 12 V fişinden önce ölçüm"),
    ("F3", r"DC V kademesine", "F3 regülatör ölçümü DC V"),
    # F7d düzeltme 1 (F7d-kontrol D-4): K11 a ölçümünden önce takı ve gerilimli fiş ucu
    ("F3", r"Ölçümden önce saat, yüzük, bileklik çıkar", "F3 ölçümden önce saat, yüzük, bileklik"),
    ("F3", r"fişin metal ucunu bantla yalıt", "F3 ölçümde 12 V fiş ucu yalıtılı"),
    # F7d düzeltme 1 (F7d-kontrol O-2): şarj kolu akü XT60'ının robot tarafından
    ("K1", r"Kolu akü XT60'ının robot tarafından, ana hattan al", "K1 şarj kolu XT60'ın robot tarafından"),
    # P10.7b1: tek kaynakla bağlanan uyarılar (planlama/adim3/kablolar.json, kablolama-on-kararlar.md)
    ("K1", r"BC337-40 #1 kollektörü \(A03; {gpio.ROLE_K1} sürer\).*BC337-40 #2 kollektörü \(A05; {gpio.ROLE_K2_ONSARJ} sürer\)",
     "K1 röle sürücüleri"),
    ("K1", r"katot \(bantlı uç\) 86'ya", "K1 1N4007 yönü (K1)"),
    ("K1", r"Teslimde bakılacaklar", "K1 teslimde bakılacaklar"),
    # P10.7b1 düzeltme turu 1 (F10h-kontrol Ü2, M21, M22): Ö4 yeri köprülü; açık kararlar "karar bekliyor"
    ("K1", r"karar verilene kadar zincirin kendi teliyle \(A01, A02\) aynı kesitte \({awg.A01|A02}\) kısa bir tel köprüyle kapalı durur; "
           r"köprü yoksa röle çekmez", "K1 Ö4 yeri köprülü, köprü teli zincirin kesitinde (köprü yoksa röle çekmez)"),
    # açık işler turu (F10h-kontrol-2 §3.3-13): "tek köprü" yerine bu adımda takılan köprülerin açık listesi
    # düzeltme turu 2 (F10h-kontrol-3 §2): "yalnız" çıktı, anahtarlı baranın köprüleri listede; iki bara madde 2'de ayrı ayrı
    ("K1", r"Bu adımda takılan köprüler: Ö4 yerindeki kısa tel köprü \(madde 5\), acil stop düğüm kartındaki "
           r"\(A02, A04\) {kopru.A02} tel köprü \(madde 5\), yıldız barasının saplamaları arasındaki {kopru_adet.yildiz} adet "
           r"{kopru.yildiz} köprü \(madde 2\), anahtarlı baranın saplamaları arasındaki {kopru_adet.bara} adet {kopru.bara} köprü",
     "K1 madde 8: bu adımda takılan köprülerin listesi (iki bara)"),
    ("K1", r"Anahtarlı bara \(\+\) {saplama.bara} M5 saplama: saplamalar {kopru_adet.bara} adet {kopru_renk.bara} {kopru.bara} "
           r"köprüyle", "K1 madde 2: anahtarlı baranın köprüleri (adet, renk, kesit)"),
    ("K1", r"İki baranın köprüleri takılı", "K1 kontrol: iki baranın köprüleri ve süreklilik"),
    ("K1", r"Bunların dışında mantarın kendi uçları ve ana anahtarın uçları hiçbir zaman köprülenmez",
     "K1 köprülenmeyenler: mantar ve ana anahtar uçları"),
    ("K1", r"Ö4 karar bekliyor \(K60\)", "K1 Ö4 karar bekliyor (K60)"),
    ("K1", r"karar bekliyor \(K52\)", "K1 göğüs regülatörü yeri karar bekliyor (K52)"),
    ("K2", r"karar bekliyor \(K52\)", "K2 göğüs regülatörü yeri karar bekliyor (K52)"),
    ("K2", r"karar bekliyor \(K61\)", "K2 konuşma düğmesi karar bekliyor (K61)"),
    ("K2", r"Demeti kurmadan önce basılmış tünel deneme parçasında", "K2 boyun: tünel deneme parçasında fiş denemesi"),
    ("K2", r"Efe'nin iki cevabı", "K2 boyun: demet kapanmadan Efe'nin cevapları"),
    ("K2", r"F6 {a.F6} \({bicak.F6}\)", "K2 göğüs 12 V F6 (değer, tip)"),
    ("E4", r"USB ses\s+kartı kablajdan çıktı", "E4 USB ses kartı yedek, takılmaz"),
    # açık işler turu (F10h-kontrol-2 §3.3-12): çizim / animasyon kartı yerine götürür; metin bunun uygulanmadığını söyler
    ("E4", r"USB ses\s+kartı takılmaz: çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür; bu eski tasarımdan "
           r"kalan görüntüdür, uygulanmaz\. Kartın köpük bandı da yapıştırılmaz; kart yedek parçalarla birlikte saklanır",
     "E4 USB ses kartı takılmaz, çizimdeki yeri uygulanmaz, köpük bant yapıştırılmaz"),
    ("E4", r"10 kΩ / 2,2 kΩ bölücü → PAM8403 sol", "E4 ses yolu ReSpeaker → bölücü → PAM8403"),
]
# P10.7b1 düzeltme turu 1 (F10h-kontrol §2-1, §2-2): ZORUNLU desenleri sabit sayı taşımaz, rehber_metin ile aynı yer tutucuları
# ({a.F6}, {gpio.ROLE_K1}, {ms.onsarj} …) kullanır; denetim öncesi rehber_deger aynı kayıttan doldurur (tablo değişince bayatlamaz).
# ZORUNLU_ALAN: uyarı belirli alanda durmalı (adımın başka alanında geçmesi yetmez: kontrol listesinden silinen madde yakalanır, M27).
ZORUNLU_ALAN = [
    ("K2", "kontrol", r"tünel deneme parçasında fiş denemesi yapıldı", "K2 kontrol: tünel deneme parçasında fiş denemesi"),
    ("K2", "kontrol", r"Efe'nin iki cevabı geldi", "K2 kontrol: demet kapanmadan Efe'nin cevapları"),
    ("K1", "kontrol", r"Ö4 yerindeki 2 pin klemenste kısa tel köprü takılı.*mantar bırakılmışken PC817 #1 \({gpio.ACIL_STOP_DURUM}\) LOW okur",
     "K1 kontrol: Ö4 köprüsü takılı, PC817 #1 mantar bırakılmışken LOW"),
    ("K1", "kontrol", r"K1'de katot 86'ya, K2'de katot bobin \+", "K1 kontrol: iki 1N4007'nin yönü"),
    ("K1", "kontrol", r"T8 E ve E2 tezgâh kısa devre denemeleri yapıldı", "K1 teslim: T8 E / E2 tezgâh denemeleri"),
    ("K1", "kontrol", r"K04'ün \(kafa ekranı Power USB\) üstündeki kesit yazısı okundu", "K1 teslim: K04 kesit yazısı"),
    ("K1", "kontrol", r"Teslimde \(KT3\): sigorta kutusunun yuvaları ortak giriş barasında mı", "K1 teslim: KT3 sigorta kutusu girişi"),
    ("F5", "kontrol", r"Göğüs ekranı ilk açılışta F6 {a.F6}'i attırmadı", "F5 kontrol: göğüs ekranı F6'yı attırmadı"),
]
# ZORUNLU_CUMLE: yön / sıra ifadesi öğesiyle aynı cümlede (cümle . ! ? ve satır sonuyla bölünür; ; bölmez). "öğe" geçen bir cümlede
# "yön" de geçmeli; öğe hiç geçmezse de eksik sayılır. Yer "SEMA <ad>" ise o şemanın metninde aranır (yalnız kaynak modunda).
ZORUNLU_CUMLE = [
    ("K1", r"K1'de soketin 86 / 85", r"katot \(bantlı uç\) 86'ya, anot 85'e", "K1 is_: K1 1N4007 katodu 86'da"),
    ("K1", r"K2'de ön şarj kartında", r"katot bobin \+ ucuna", "K1 is_: K2 1N4007 katodu bobin + ucunda"),
    ("K1", r"Her sürücüde", r"{ohm.seri} seri taban direnci ve {ohm.taban} taban → GND", "K1 is_: sürücü dirençlerinin yeri"),
    ("K1", r"Röle sürücüleri arayüz kartında", r"her birinde {ohm.seri} seri ve {ohm.taban} taban → GND", "K1 kontrol: sürücü dirençlerinin yeri"),
    ("K1", r"Ö4", r"kısa bir tel köprüyle kapalı durur; köprü yoksa röle çekmez", "K1 is_: Ö4 köprüsü"),
    ("K1", r"PC817 #1 girişi düğümden", r"{gpio.ACIL_STOP_DURUM} okur", "K1 is_: PC817 #1'in pini (M2: ; ile ayrılan pin bağlam kuralına girmez)"),
    ("K2", r"VBUS teline seri 1N5819", r"anot hub \(Pi\)\s+tarafında, katot ESP32 tarafında", "K2 is_: 1N5819 yönü"),
    ("SEMA ESP32 USB", r"1N5819", r"anot hub \(Pi\) tarafında, katot ESP32 tarafında", "SEMA ESP32 USB: 1N5819 yönü"),
    ("F5", r"{gpio.ROLE_K2_ONSARJ} = 1 \(röle K2\)", r"en az {ms.onsarj} bekle", "F5 E9: K2'den sonra en az bekleme"),
    ("F5", r"{gpio.ROLE_K1} = 1 \(röle K1\)", r"{ms.k1_sonra} sonra {gpio.ROLE_K2_ONSARJ} = 0", "F5 E9: K1'den sonra K2 bırakılır"),
    # açık işler turu (F10h-kontrol-2 B28): göğüs regülatörünün yeri şemada da açık karar
    ("SEMA 12 V", r"LM2577 \+ LM2596", r"regülatör yeri karar bekliyor, K52\)", "SEMA 12 V: göğüs regülatörü yeri karar bekliyor (K52)"),
]
_CUMLE_BOL = r"(?<=[.!?])\s+|\n"
_CUMLE_GENIS = r"(?<=[!?])\s+|(?<=\D\.)\s+|\n"                      # ; ve sıra sayısından ("6. yuva") sonra bölmez


def _yt_coz(desen, hatalar):
    """Desendeki yer tutucuları kayıttan doldur; çözülemeyen yer tutucu hatalar listesine, desen None. Açık işler turu (F10h-kontrol-2
    §3.1-7): desen tam sözcükle başlar ve biter: "sigortasını tak" deseni "sigortasını takma"yı tutmaz (olumsuzluk eki sözcüğü uzatır)."""
    try:
        return r"(?<!\w)(?:" + _RDG.degerler().desen(desen) + r")(?!\w)"
    except (KeyError, TypeError) as e:
        hatalar.append("ZORUNLU deseni çözülemedi: %s (%s)" % (desen[:60], e))
        return None


def zorunlu_listesi(hatalar=None):
    """ZORUNLU (adım, desen, ad) yer tutucuları doldurulmuş hâliyle."""
    h = hatalar if hatalar is not None else []
    return [(k, _yt_coz(d, h) or r"(?!x)x", ad) for k, d, ad in ZORUNLU]


def zorunlu_alan_listesi(hatalar=None):
    h = hatalar if hatalar is not None else []
    return [(k, alan, _yt_coz(d, h) or r"(?!x)x", ad) for k, alan, d, ad in ZORUNLU_ALAN]


def zorunlu_cumle_listesi(hatalar=None):
    h = hatalar if hatalar is not None else []
    return [(k, _yt_coz(o, h) or r"(?!x)x", _yt_coz(y, h) or r"(?!x)x", ad) for k, o, y, ad in ZORUNLU_CUMLE]


def cumle_denetle(metin_yere, hatalar=None):
    """metin_yere: {yer anahtarı: metin}. Eksik ZORUNLU_CUMLE maddeleri: [dict(yer, uyari, neden)]."""
    out = []
    for k, oge, yon, ad in zorunlu_cumle_listesi(hatalar):
        if k not in metin_yere:
            continue
        cum = [c for c in re.split(_CUMLE_BOL, metin_yere[k]) if re.search(oge, c)]
        if not cum:
            out.append(dict(yer=k, uyari=ad, neden="öğe geçmiyor"))
        elif not any(re.search(yon, c) for c in cum):
            out.append(dict(yer=k, uyari=ad, neden="öğenin cümlesinde yön / sıra ifadesi yok"))
    return out

# Açık işler turu (F10h-kontrol-2 §3.1-6): MOSFET / WAGO / ses kartı geçen cümle yalnız bu listede tam (boşluk normalleştirilmiş)
# hâliyle varsa geçer; pencere ya da sözcük affı yok. Liste onay kaydına dahil (değişmesi kritik değişiklik). Cümle bölmesi
# elektrik_denetle'deki gibi (. ; ! ? ve satır sonu); kaynak metni, CAD ad / kodları (çevrilmiş) ve arayüz metinleri.
TERIM_ISTISNA = [
    "WAGO yok",
    "WAGO yok.",
    "Seçenek: kollu WAGO 221-413 (ince telli alır) alınabilir, karar Ahmet'in;",
    "Kafa ekranı (10,1\" QLED), tırnaklar, kamera, ReSpeaker ve PAM8403 bu adımda takılmaz: kabuklarla birlikte E4'te (USB ses kartı "
    "kablajdan çıktı: yedek, takılmaz;",
    "USB ses kartı takılmaz: çizimde ve animasyonda kart, köpük bandıyla birlikte, PAM8403'ün yanındaki yerine gidiyor görünür;",
    "USB ses kartı takılmadı (yedek), Pi USB 2 boş",
    "USB ses kartı kablajdan çıktı, siparişte kalır, takılmaz (yedek): masa denemesi KT2 geçmezse Pi USB 2'ye takılır ve 04.11 düzeni "
    "geri gelir.",
    "Masada: sol arka kabuk + PAM8403 (USB ses kartı yedek, takılmaz)",
    "eski şema ses kartından çiziliyordu, kaldırıldı).",
    "Köpük bant (yedek USB ses kartı için;",
    "USB ses kartı (yedek, takılmaz)",
    "USB ses kartı: yedek, takılmaz (KT2 geçmezse Pi port 2'ye;",
]
_TERIM_ISTISNA = {_RK.normal(x) for x in TERIM_ISTISNA}
_TERIM = r"MOSFET|WAGO|[Ss]es kart"

# 6) Yasak talimat kalıpları: (ad, desen, olumsuz biçim deseni). Desen cümlede (. ; ! ? ve satır sonuyla bölünür) aranır, büyük / küçük
#    harf duyarsız. Olumsuz biçim deseni eşleşmenin son kelimesine (fiil) uygulanır; tutarsa ya da eşleşmenin ±40 karakterinde ve
#    eşleşme sonunun yan cümlesinde (virgül, iki nokta ya da bağlaçla bölünür; F7c düzeltme 1, D-1) olumsuzlama kelimesi varsa istisna.
_KOK = r"(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|bağlantı\s+yap)"
_FIIL = _KOK + r"\w*"
_FIIL_OLUMSUZ = (r"(?:bağla|tak|lehimle|sök|çıkar|vidala|sık|kes|değiştir|yap)(?:ma|me)(?:z|dan|den|yın|yin|yınız|yiniz|malı|meli)?"
                 r"|(?:bağla|tak|sök|çıkar|kes|değiştir|yap)(?:ıl|il|ul|ül)?(?:maz|mez)")
_OLUMSUZ_GENEL = r"\w+(?:ma|me)(?:z|dan|den|yın|yin|yınız|yiniz|malı|meli)?|\w+(?:maz|mez)"
# F7d (D-7): önek ile fiil arasındaki pencere yalnız enerjiyi bitiren ifadede kesilir (virgül, "ve" kesmez).
# F7d düzeltme 1 (F7d-kontrol O-1): çıplak sıra bağlacı ("sonra", "bitince", "ardından") kesmez ("Ana anahtar açıkken birkaç saniye
# sonra … tak" yakalanır); olumsuz ekli biçim ("ayırmadan", "kapatmadan", "kesmeden") kesmez.
_SINIR = (r"(?:\bana\s+anahtar\w*\s+kapat|\bakü\w*\s+(?:XT60\S*\s+)?ayır|\bXT60\S*\s+ayır|\benerjiyi\s+kes)(?!ma|me)")
_PENCERE = r"(?:(?!" + _SINIR + r")[^.;!?\n]){0,120}?"
# F7d (D-6'): köprüleme eş anlamlıları yalnız anahtarlama / besleme nesnesi bağlamında ("GND uçlarını WAGO'da birleştir" tutmaz)
# F7d düzeltme 1 (F7d-kontrol D-2): "artı" / "eksi" yalnız ad çekim ekleriyle ve kelime sınırıyla ("artık", "eksik" tutmaz)
_KOPRU_NESNE = (r"\b(?:mantar\w*|acil\s+stop\w*|NC|ana\s+anahtar\w*|sigorta\w*|röle\w*|kontak\w*|\d+\s*V|"
                r"(?:artı|eksi)(?:sı|si|sını|sini|yı|yi|ya|ye|nın|nin|ları|leri|lar|ler)?)"
                r"(?![\w])[^.;!?\n]{0,60}?")
YASAK = [
    # düzeltme turu 2: çoğul ad "köprüler / köprüleri / köprülerin …" fiil değil (K1 madde 8 "Bu adımda takılan köprüler")
    ("köprüleme talimatı", r"\bköprüle(?!r(?:i|in|e|de|den|le)?\b)\w*",r"köprüle(?:n)?me(?:z|di|meli|yin|yiniz|den)?|köprülenemez"),
    ("köprü teli / jumper", r"\b(?:köprü|jumper|atlama)\s*(?:kablo|tel)\w*", r"$^"),
    ("köprüleme (birleştir)", _KOPRU_NESNE + r"\bbirleştir\w*", _OLUMSUZ_GENEL),
    ("köprüleme (birbirine bağla)", _KOPRU_NESNE + r"\bbirbirine\s+(?:bağla|değdir|lehimle|tuttur|kıskaçla)\w*", _OLUMSUZ_GENEL),
    ("röleyi elle kapatma", r"\bröle\w*(?:\s+\w+){0,2}?\s+elle\s+(?:kapat|çek|bastır|kapa)\w*", _OLUMSUZ_GENEL),
    # D-2: yalnız öznesi akü olan "akü (XT60) bağlı / takılı" ("Akü ön takozu … takılı", "Akü kayışları takılı" tutmaz)
    ("akü bağlıyken iş", r"\bakü(?:yü|nün|sü)?\s+(?:XT60\S*\s+)?(?:bağlı|takılı)\w*(?:\s+(?:iken|olabilir|kalabilir|kalsın|durumda\w*))?",
     r"$^"),
    ("enerji varken bağlantı", r"\b(?:enerjili(?:yken|ken)?|enerji\s+(?:varken|açıkken|verilmişken|altında)|gerilim\s+(?:altında|varken)|"
                               r"gerilimli(?:yken)?|sigorta\w*\s+takılı(?:yken|\s+iken)|XT60\S*\s+(?:takılı|bağlı)(?:yken|\s+iken)|"
                               r"ana\s+anahtar\s+açıkken|"
                               # F7d (D-6' K5): "açtıktan / taktıktan / verdikten sonra … tak"
                               r"ana\s+anahtar\w*\s+(?:açtıktan\s+sonra|açınca|açıldıktan\s+sonra|açılınca)|"
                               r"akü\w*\s+(?:XT60\S*\s+)?(?:taktıktan\s+sonra|takınca|bağladıktan\s+sonra|bağlayınca)|"
                               r"enerji\s+(?:verdikten\s+sonra|verince|verildikten\s+sonra))\b" + _PENCERE + r"\b" + _FIIL,
     _FIIL_OLUMSUZ),
    # D-1: kalıp dışı anlatımlar
    ("devre dışı bırakma", r"\bdevre\s*dışı\s*bırak\w*", _OLUMSUZ_GENEL),
    ("kısa devre talimatı", r"\bkısa\s*devre\s*(?:et|yap|oluştur|kur)\w*", _OLUMSUZ_GENEL),
    ("sigorta / mantar yerine tel", r"\byerine\s+(?:bir\s+)?(?:tel|kablo|köprü|jumper)\w*(?:\s+\w+)?", _OLUMSUZ_GENEL),
]
OLUMSUZLAMA = r"\b(?:asla|hiçbir zaman|hiçbir şekilde|yasak\w*|gerekmez|gerek yok|değil|değildir)(?!\w)"
OLUMSUZ_PENCERE = 40
YAN_CUMLE = r",(?!\d)|:|\s(?:ve|ama|fakat|ancak|sonra|ardından|veya|ya da|çünkü)\s"   # açık işler turu: ondalık virgül bölmez


def yan_cumle(cumle, i):
    """cumle içinde i konumunu içeren yan cümlenin (bas, son) sınırı (virgül, iki nokta, bağlaç)."""
    bas, son = 0, len(cumle)
    for m in re.finditer(YAN_CUMLE, cumle, re.I):
        if m.end() <= i:
            bas = m.end()
        elif m.start() >= i:
            son = m.start()
            break
    return bas, son


def yasak_tara(V):
    """Adım metinlerinde (iş, bağlantı, alet, erişim, kontrol, kablo, not) yasak talimat: (bulgu, istisna)."""
    bulgu, istisna = [], []
    for a in V["adimlar"]:
        alan = [(k, a.get(k) or "") for k in ("baslik", "is_", "baglanti_md", "alet", "erisim")]
        alan += [(k, t) for k in ("kontrol", "kablo", "not_") for t in (a.get(k) or [])]
        alan += [("alt adım %d %s" % (n + 1, k), g.get(k) or "") for n, g in enumerate(a.get("sira_grup") or []) for k in ("ad", "is_")]   # F10d
        for k, metin in alan:
            for cumle in re.split(r"(?<=[.;!?])\s+|\n", metin):
                for ad, desen, olumsuz in YASAK:
                    for t in re.finditer(desen, cumle, re.I):
                        son = re.findall(r"\w+", t.group(0))[-1].lower()
                        yb, ys = yan_cumle(cumle, t.end() - 1)
                        cevre = cumle[max(yb, t.start() - OLUMSUZ_PENCERE):min(ys, t.end() + OLUMSUZ_PENCERE)]
                        neden = ("olumsuz biçim: " + son) if re.fullmatch(olumsuz, son) else None
                        if not neden:
                            o = re.search(OLUMSUZLAMA, cevre, re.I)
                            neden = ("olumsuzlama: " + o.group(0)) if o else None
                        d = dict(adim=a["kod"], alan=k, yasak=ad, ifade=t.group(0), cumle=cumle[:200])
                        if neden:
                            d["istisna"] = neden
                            istisna.append(d)
                        else:
                            bulgu.append(d)
    return bulgu, istisna


KOPYA_EKI = r"\D0\d\d$"


def kopya_eki(V):
    """Görünen parça adında FreeCAD kopya eki (D-6): sondaki 0NN."""
    return [dict(id=p["id"], ad=p["ad"]) for p in V["parcalar"] if re.search(KOPYA_EKI, p["ad"])]


def gorunen_metinler(V):
    """rehber-veri.json'dan ekranda görünen metinler: (yer, metin)."""
    out = []
    for a in V["adimlar"]:
        y = "adım %d %s" % (a["i"], a["kod"])
        for k in ("baslik", "is_", "baglanti_md", "alet", "erisim", "faz"):
            out.append((y + " " + k, a.get(k) or ""))
        for k in ("kontrol", "kablo", "not_"):
            out += [(y + " " + k, t) for t in (a.get(k) or [])]
        for r in a["parcalar"]:
            out += [(y + " parça", r["ad"]), (y + " parça malzeme", r.get("malzeme") or ""),
                    (y + " parça tür", (V.get("tur_ad") or {}).get(r["tur"], r["tur"]))]
        out += [(y + " bağlantı", r["kod"]) for r in a["baglantilar"]]
        for n, g in enumerate(a.get("sira_grup") or []):                # F10d: alt adım / sıra grubu başlığı ve metni
            out += [(y + " alt adım %d ad" % (n + 1), g.get("ad") or ""), (y + " alt adım %d is_" % (n + 1), g.get("is_") or "")]
    for p in V["parcalar"]:                                          # tıklayınca görünen etiket
        out += [("parça %s ad" % p["id"], p["ad"]), ("parça %s kod" % p["id"], p["kod"]),
                ("parça %s modül" % p["id"], (V.get("modul_ad") or {}).get(p["modul"], p["modul"]))]
    out += [("şema %d" % i, s["ad"]) for i, s in enumerate(V.get("semalar", []))]
    return out


def _sozluk_ascii():
    d = {}
    for k, v in list(RM.TR.items()) + list(RM.TR_EK.items()):
        if k.lower() != v.lower():
            d[k.lower()] = v
    return d


def ascii_kalinti(metinler):
    S = _sozluk_ascii()
    bulgu = collections.OrderedDict()
    for yer, m in metinler:
        m = re.sub(r"`[^`]*`", " ", m or "")
        m = re.sub(r"<code>.*?</code>", " ", m, flags=re.S)
        for t in re.finditer(r"[A-Za-zÇĞİÖŞÜçğıöşüÂâÎîÛû]+", m):
            w = t.group(0)
            if not re.fullmatch(r"[A-Za-z]+", w) or len(w) < 3:
                continue
            if t.start() > 0 and m[t.start() - 1] in "'’":
                continue                                               # kesme işaretinden sonraki ek
            if w.isupper():
                if w not in KISALTMA:
                    bulgu.setdefault(w, yer)
                continue
            if re.search(r"[a-z][A-Z]", w):                             # CamelCase marka / ürün adı (ReSpeaker, WaveShare)
                continue
            k = w.lower()
            if k in S or k not in ASCII_TAMAM:
                bulgu.setdefault(w, yer)
    return [dict(kelime=k, ilk_yer=v, sozlukte=k.lower() in S) for k, v in bulgu.items()]


def tablo_metinleri(V=None):
    """P10.7b1 üretim uyumu (S1): panelin kablo tablosundan gösterdiği metinler (lejant adı, tıklama kartının kb satırları).
    V verilirse veride yazılı olanlar, verilmezse kablolar.json'dan bütün kablolar (FreeCAD'siz ön sınama). Yalnız ASCII sınamasına girer."""
    if V is not None:
        out = [("lejant %s" % k, "Kablo: " + v[1]) for k, v in sorted((V.get("kablo_sinif") or {}).items())]
        for p in V["parcalar"]:
            out += [("parça %s kb" % p["id"], t) for t in p.get("kb") or []]
        for i, s in enumerate(V.get("semalar", [])):
            out += [("şema %d kb" % i, t) for t in s.get("kb") or []]
        return out
    import rehber_kablo as _RKB
    TB = _RKB.Tablo()
    return ([("lejant %s" % k, "Kablo: " + v[1]) for k, v in sorted(TB.lejant().items())] +
            [("kablo %s kb" % k, TB.bilgi_satiri(k)) for k in sorted(TB.K)])


def _norm(ad):
    a = re.sub(r"(\D)0\d\d$", r"\1", ad)
    a = re.sub(r"\s*\((?:[^()]|\([^()]*\))*\)\s*$", "", a).strip()
    a = re.sub(r"\s+", " ", re.sub(r"\b(?:sağ|sol)\b", " ", a)).strip()
    return re.sub(r"\s*\((?:[^()]|\([^()]*\))*\)\s*$", "", a).strip()   # sağ / sol atılınca sonda kalan açıklama (Yüz kabuğu (ön) sağ)


def gruplama(V):
    P = {p["id"]: p for p in V["parcalar"]}
    yanlis, eksik, eski = [], [], []
    for a in V["adimlar"]:
        gor = collections.Counter()
        for r in a["parcalar"]:
            ids = r.get("ids")
            if ids is None:
                yanlis.append(dict(adim=a["kod"], satir=r["ad"], neden="satırda ids yok (eski veri)"))
                continue
            gor.update(ids)
            ad_set = {_norm(P[i]["ad"]) for i in ids}
            satir = _norm(re.sub(r" \(sağ \+ sol\)$", "", r["ad"]))
            if len(ad_set) != 1 or satir not in ad_set or r["adet"] != len(ids):
                yanlis.append(dict(adim=a["kod"], satir="%s ×%d" % (r["ad"], r["adet"]), uyeler=sorted({P[i]["ad"] for i in ids})))
        for r in a["baglantilar"]:
            for i in r.get("ids", []):
                if P[i]["kod"] != r["kod"]:
                    yanlis.append(dict(adim=a["kod"], satir=r["kod"], neden="bağlantı kodu farklı: " + P[i]["kod"]))
        bag_gor = collections.Counter(i for r in a["baglantilar"] for i in r.get("ids", []))
        bag_bek = [p["id"] for p in V["parcalar"] if p["a"] == a["i"] and p["tur"] == "Baglanti"]
        if sorted(bag_gor.elements()) != sorted(bag_bek):
            eksik.append(dict(adim=a["kod"], baglanti_satirda=sum(bag_gor.values()), baglanti_parca=len(bag_bek)))
        beklenen = [p["id"] for p in V["parcalar"] if p["a"] == a["i"] and p["tur"] not in ("Referans", "Baglanti")]
        if sorted(gor.elements()) != sorted(beklenen):
            eksik.append(dict(adim=a["kod"], satirda=sum(gor.values()), parca=len(beklenen)))
        # eski kural (kod + tür + renk) aynı veride: kaç satır farklı adları tek satırda toplardı
        g = collections.defaultdict(set)
        for i in beklenen:
            p = P[i]
            g[(p["kod"], p["tur"], p["r"])].add(_norm(p["ad"]))
        eski += ["%s: %s" % (a["kod"], " | ".join(sorted(v))) for v in g.values() if len(v) > 1]
    return dict(yanlis=yanlis, eksik=eksik, eski_kural_yanlis=len(eski), eski_kural_ornek=eski[:8])


def tutarlilik(V, metinler):
    """Kafa / hoparlör / hub: bileşenin yeni göründüğü adımın metni onu anıyor mu; eski ifadeler bağlamsız geçiyor mu."""
    adim_metin = collections.defaultdict(str)
    for a in V["adimlar"]:
        adim_metin[a["i"]] = "\n".join([a.get("is_") or "", a.get("baglanti_md") or ""] + (a.get("kontrol") or []) + (a.get("kablo") or [])
                                       + (a.get("not_") or []) + [g.get("is_") or "" for g in (a.get("sira_grup") or [])])
    anma = []
    for anahtar, kelimeler in BILESEN:
        for i in sorted({p["a"] for p in V["parcalar"] if p["ad"].startswith(anahtar) or anahtar in p["ad"]}):
            ok = any(k in adim_metin[i] for k in kelimeler)
            anma.append(dict(bilesen=anahtar, adim=V["adimlar"][i]["kod"], metinde=ok))
    celiski, affedilen = [], []
    for yer, m in metinler:
        for cumle in re.split(r"(?<=[.;])\s+|\n", m or ""):
            for desen, ad in ESKI:
                for t in re.finditer(desen, cumle):
                    cevre = cumle[max(0, t.start() - BAGLAM_PENCERE):t.end() + BAGLAM_PENCERE]
                    b = [k for k in BAGLAM if k in cevre]
                    (affedilen if b else celiski).append(dict(ifade=ad, yer=yer, cumle=cumle[:160], baglam=b))
    kod = {a["kod"]: a["i"] for a in V["adimlar"]}
    zh = []                                                         # P10.7b1 düzeltme turu 1: desenler yer tutucuyla, kayıttan doldurulur
    zorunlu = [dict(adim=k, uyari=ad, var=bool(re.search(d, adim_metin[kod[k]]))) for k, d, ad in zorunlu_listesi(zh)]
    A = {a["kod"]: a for a in V["adimlar"]}
    for k, alan, d, ad in zorunlu_alan_listesi(zh):
        t = A.get(k, {}).get(alan)
        t = "\n".join(t) if isinstance(t, list) else (t or "")
        zorunlu.append(dict(adim=k, uyari=ad + " (alan %s)" % alan, var=bool(re.search(d, t))))
    for x in cumle_denetle({k: adim_metin[kod[k]] for k in kod}, zh):
        zorunlu.append(dict(adim=x["yer"], uyari=x["uyari"] + " (" + x["neden"] + ")", var=False))
    zorunlu += [dict(adim="-", uyari=e, var=False) for e in zh]
    return dict(anma=anma, anmayan=[x for x in anma if not x["metinde"]], celiski=celiski, affedilen=affedilen,
                zorunlu=zorunlu, zorunlu_eksik=[x for x in zorunlu if not x["var"]])


# 8) Elektrik iddiaları (P10.7b1): rehber metnindeki sayısal elektrik iddiaları tek kaynakla karşılaştırılır. Kaynak:
#    planlama/adim3/kablolar.json (koruyucular: sigorta akımı ve bıçak türü; kablolar: AWG; ic_baglar / dugumler / anahtarlar: direnç
#    ve diyot metinleri) ve planlama/adim3/pin-haritasi.md §9 JSON (GPIO). Metinde sayı yazmak serbest; yazılan sayı kaynakla
#    çelişirse hata. Kurallar (her biri cümle ya da kısa pencere içinde):
#    GPIO: her "GPIO n" pin haritasında kullanılan bir pin; "röle K1 / K2", "BC337-40 #1 / #2", "PC817 #1 / #2" ile birlikte geçen GPIO
#    o ucun pini (pin haritasındaki "uc" alanından). Sigorta: "F1…F6 n A" kutu sigortasının akımı, kutu sigortası "mini" değil; "ana
#    sigorta n A"; "şarj … n A" (ön şarj hariç) şarj hat sigortası; "göğüs … n A" F6 ve "mini" değil; "mini n A" / "n A mini" listedeki
#    bir mini sigorta akımı. AWG: tablodaki kesitlerden biri (24 yalnız K04'ün kesit kuralında); "kafa 12 V", "ana hat", "şarj kolu",
#    "uzatma" yanındaki AWG o kablonun kesiti. Direnç: değer kaynakta geçen dirençlerden biri (≤ ile yazılan süreklilik eşiği hariç);
#    "BC337-40" yanındaki direnç 270 Ω ya da 2,2 kΩ; "ön şarj" yanındaki direnç ön şarj direnci. Terim: MOSFET yok (sürücü BJT); WAGO
#    yalnız "yok" / "seçenek" bağlamında; "ses kartı" yalnız yedek bağlamında; "Hızlı klemens" yok; USB 3.0 yalnız olumsuz bağlamda;
#    kapanmış kararlar (K1, K10, K11, K14) "karar bekliyor" değil, "varsayım, K10" değil, "K11 b" dalı yok; ön şarj beklemesi "en az
#    300 ms"; hub "harici besleme" yalnız olumsuz.
PIN_HARITASI = os.path.join(ROBOT, "planlama", "adim3", "pin-haritasi.md")
KABLO_TABLO = os.path.join(ROBOT, "planlama", "adim3", "kablolar.json")
_SAYI = r"(\d+(?:,\d+)?)"


def _sayi(s):
    return float(s.replace(",", "."))


def elektrik_kaynak(T=None, PH=None):
    """Kaynaktan beklenen değerler (karşılaştırma tablosu). Kayıtta beklenen anahtar yoksa (ör. koruyucu adı değişti, B22)
    traceback yerine rehber_kritik.KayitHatasi (düzeltme turu 2, F10h-kontrol-3 §3.3-1)."""
    try:
        return _elektrik_kaynak(T, PH)
    except (KeyError, TypeError) as e:
        raise _RK.KayitHatasi("elektrik denetiminin kayıt girdisi okunamadı: %s anahtarı yok (kablolar.json koruyucular / kablolar "
                              "ya da pin haritası değişti mi? rehberdeki yer tutucular ve denetim tabloları birlikte güncellenmeli)" % e)


def _elektrik_kaynak(T=None, PH=None):
    T = T if T is not None else json.load(open(KABLO_TABLO, encoding="utf-8"))
    if PH is None:
        md = open(PIN_HARITASI, encoding="utf-8").read()
        PH = json.loads(md.split("## 9.")[1].split("```json")[1].split("```")[0])
    KOR = T["koruyucular"]
    pin = {k: v["gpio"] for k, v in PH["pinler"].items()}
    uc = {}
    for k, v in PH["pinler"].items():
        u = v.get("uc") or ""
        m = re.search(r"role surucusu #(\d)", u)
        if m:
            uc["K%s" % m.group(1)] = v["gpio"]
            uc["BC337-40 #%s" % m.group(1)] = v["gpio"]
        m = re.search(r"PC817 #(\d)", u)
        if m:
            uc["PC817 #%s" % m.group(1)] = v["gpio"]
    kutu = {k: c["akim_a"] for k, c in KOR.items() if re.fullmatch(r"F\d", k) and c.get("tur") == "sigorta"}
    mini = sorted({c["akim_a"] for c in KOR.values() if c.get("bicak") == "mini"})
    awg = sorted({r["kesit"]["awg"] for r in T["kablolar"] if r.get("kesit") and r["kesit"].get("awg")})
    K = {r["kimlik"]: r for r in T["kablolar"]}
    # dirençler: pin haritası donanım alanları (270R, 2.2k, ...) + tablo metinlerindeki "n Ω" / "n kΩ"
    ohm = set()
    for v in PH["pinler"].values():
        for t in re.findall(r"(\d+(?:\.\d+)?)(R|k)\b", " ".join(str(x) for x in v.values())):
            ohm.add(round(float(t[0]) * (1000 if t[1] == "k" else 1), 3))
    for t in re.findall(_SAYI + r"\s?(k?)Ω", json.dumps(T, ensure_ascii=False)):
        ohm.add(round(_sayi(t[0]) * (1000 if t[1] else 1), 3))
    ana = KOR["ana-sigorta"]["akim_a"]
    sarj = KOR["hat-sarj"]["akim_a"]
    surucu = set()
    for v in PH["pinler"].values():
        if "role surucusu" in (v.get("uc") or ""):
            for t in re.findall(r"(\d+(?:\.\d+)?)(R|k)\b", v.get("donanim") or ""):
                surucu.add(round(float(t[0]) * (1000 if t[1] == "k" else 1), 3))
    on_sarj = {round(_sayi(t), 3) for t in re.findall(_SAYI + r"\s?Ω", T["anahtarlar"]["K2-kontak"]["ad"])}
    # P10.7b1 düzeltme turu 1 (F10h-kontrol §2-1): bağlam kuralları için kimlik başına değerler
    D = _RDG.Degerler(T, PH)
    yer_ohm = {k: round(_sayi(re.sub(r"\s?k?Ω", "", D.deger("ohm", k))) * (1000 if "k" in D.deger("ohm", k) else 1), 3)
               for k in ("seri", "taban")}
    kopru = {int(m) for r in T["kablolar"] for m in re.findall(r"≥ (\d+) AWG tel köprü", r.get("sonlandirma") or "")}
    kopru |= {v["awg"] for v in T["klemens_turleri"]["bara-pabuc"]["kopruler"].values() if isinstance(v, dict) and v.get("awg")}
    return dict(pin=set(pin.values()), bos={int(k) for k in PH.get("bos", {})}, uc=uc, kutu=kutu, mini=mini, awg=awg, ohm=ohm,
                ana=ana, sarj=sarj, gogus=KOR["F6"]["akim_a"], surucu=surucu, on_sarj=on_sarj,
                hat={h: KOR["hat-" + h]["akim_a"] for h in ("A", "B", "C")}, g22=KOR["hat-G22"]["akim_a"], cevre=KOR["hat-cevre"]["akim_a"],
                yer_ohm=yer_ohm, kopru=kopru, onsarj_ms=int(D.deger("ms", "onsarj").split()[0]),
                kimlik_awg={r["kimlik"]: r["kesit"]["awg"] for r in T["kablolar"] if r.get("kesit") and r["kesit"].get("awg")},
                yuva_f6=int(D.deger("yuva", "F6")),
                kesit={"kafa 12 V": K["G17"]["kesit"]["awg"], "ana hat": K["G01"]["kesit"]["awg"],
                       "şarj kol": K["G06"]["kesit"]["awg"], "uzatma": K["S01"]["kesit"]["awg"]})


_UC_DESEN = r"(röle K[12]|K[12]'(?:yi|i|ı)|BC337-40 #[12]|PC817 #[12])"


def _uc_ad(s):
    m = re.search(r"K([12])", s) if not s.startswith(("BC337", "PC817")) else None
    return ("K" + m.group(1)) if m else s


def elektrik_denetle(metinler, E=None):
    """metinler: [(yer, metin)]. Doner [dict(yer, kural, ifade, neden)]."""
    E = E or elektrik_kaynak()
    out = []

    def h(yer, kural, ifade, neden):
        out.append(dict(yer=yer, kural=kural, ifade=ifade[:120], neden=neden))
    for yer, m in metinler:
        m = re.sub(r"`[^`]*`", " ", m or "")
        # düzeltme turu 1: liste ve sıra sayısı içeren kurallar ; ve "6." ile bölünmeyen cümlede
        for c in re.split(_CUMLE_GENIS, m):
            # (M8) F6'nın yuvası (elektrik.md sigorta listesi)
            for t in re.finditer(r"\bF6\b[^.;]{0,90}?\b(\d)\. yuva", c):
                if int(t.group(1)) != E["yuva_f6"]:
                    h(yer, "sigorta", t.group(0), "F6 kutunun %d. yuvasında (elektrik.md sigorta listesi)" % E["yuva_f6"])
            # (M4, M5, M6, M9) hat sigortaları kimlik bağlamıyla (değer listede var mı değil, bu hattın değeri mi)
            if re.search(r"XL4016|hat sigorta", c):
                for t in re.finditer(r"(?:XL4016 |\b)([ABC])(?: ve B)? \(?(?:mini; )?" + _SAYI + r"\s?A\b", c):
                    if abs(_sayi(t.group(2)) - E["hat"][t.group(1)]) > 1e-9:
                        h(yer, "sigorta", t.group(0), "hat %s sigortası tabloda %g A" % (t.group(1), E["hat"][t.group(1)]))
        for c in re.split(r"(?<=[.;!?])\s+|\n", m):
            # GPIO
            for t in re.finditer(r"GPIO ?(\d+)", c):
                n = int(t.group(1))
                if n not in E["pin"] or n in E["bos"]:
                    h(yer, "GPIO", t.group(0), "pin haritasında kullanılan pin değil (%s)" % ("boş pin" if n in E["bos"] else "yok"))
            # düzeltme turu 1 (M2): "PC817 #1 → GPIO5" ok işaretiyle de yakalanır (pencere ok ile bitmez; başka uç adı araya girerse biter)
            for t in re.finditer(_UC_DESEN + r"(?:(?!" + _UC_DESEN.replace("(", "(?:", 1) + r")[^.;:\n)]){0,30}?GPIO ?(\d+)", c):
                u = _uc_ad(t.group(1))
                if u in E["uc"] and int(t.group(2)) != E["uc"][u]:
                    h(yer, "GPIO", t.group(0), "%s pin haritasında GPIO%d" % (u, E["uc"][u]))
            for t in re.finditer(r"GPIO ?(\d+)(?: = [01])? \((?:röle )?(K[12]|PC817 #[12])\)", c):
                u = t.group(2)
                if u in E["uc"] and int(t.group(1)) != E["uc"][u]:
                    h(yer, "GPIO", t.group(0), "%s pin haritasında GPIO%d" % (u, E["uc"][u]))
            # sigorta
            for t in re.finditer(r"\b(F[1-6])\b\s*\(?" + _SAYI + r"\s?A\b", c):
                if t.group(1) in E["kutu"] and abs(_sayi(t.group(2)) - E["kutu"][t.group(1)]) > 1e-9:
                    h(yer, "sigorta", t.group(0), "%s tabloda %g A" % (t.group(1), E["kutu"][t.group(1)]))
            # düzeltme turu 1 (M7): parantez içindeki tip de ("F6 3 A (mini") sayılır
            for t in re.finditer(r"\bF[1-6]\b(?:\s*\(?\d+(?:,\d+)?\s?A)?[^.;,]{0,6}?\bmini\b", c):
                h(yer, "sigorta", t.group(0), "kutu sigortaları standart bıçak (mini yalnız hat yuvalarında)")
            for t in re.finditer(r"(?:G22\b|PC817 #2 algı tel\w*)[^.;\n]{0,60}?" + _SAYI + r"\s?A\b(?=\s+(?:mini|standart|hat|sigorta))", c):
                if abs(_sayi(t.group(1)) - E["g22"]) > 1e-9:
                    h(yer, "sigorta", t.group(0), "G22 algı teli sigortası tabloda %g A" % E["g22"])
            for t in re.finditer(r"[çÇ]evre[^.;\n]{0,60}?" + _SAYI + r"\s?A\s+(?:mini\s+)?hat sigortası", c):
                if abs(_sayi(t.group(1)) - E["cevre"]) > 1e-9:
                    h(yer, "sigorta", t.group(0), "çevre hat sigortası tabloda %g A" % E["cevre"])
            for t in re.finditer(r"[Aa]na sigorta\w*\s*\(?" + _SAYI + r"\s?A\b", c):
                if abs(_sayi(t.group(1)) - E["ana"]) > 1e-9:
                    h(yer, "sigorta", t.group(0), "ana sigorta tabloda %g A" % E["ana"])
            for t in re.finditer(r"(?<![öÖ]n )[Şş]arj[^.;\n]{0,40}?" + _SAYI + r"\s?A\b", c):
                if abs(_sayi(t.group(1)) - E["sarj"]) > 1e-9:
                    h(yer, "sigorta", t.group(0), "şarj hat sigortası tabloda %g A" % E["sarj"])
            for t in re.finditer(r"[Gg]öğüs[^.;\n]{0,70}?\b(mini\s+|standart\s+)?" + _SAYI + r"\s?A\b", c):
                if abs(_sayi(t.group(2)) - E["gogus"]) > 1e-9 or (t.group(1) or "").startswith("mini"):
                    h(yer, "sigorta", t.group(0), "göğüs ekranı sigortası F6 %g A standart" % E["gogus"])
            for t in list(re.finditer(r"\bmini\s+" + _SAYI + r"\s?A\b", c)) + list(re.finditer(_SAYI + r"\s?A\s+mini\b", c)):
                if not any(abs(_sayi(t.group(1)) - v) < 1e-9 for v in E["mini"]):
                    h(yer, "sigorta", t.group(0), "listede bu akımda mini sigorta yok (%s A)" % ", ".join("%g" % v for v in E["mini"]))
            # AWG
            for t in re.finditer(r"(\d+)\s?AWG", c):
                n = int(t.group(1))
                if n not in E["awg"] and not (n == 24 and re.search(r"24 AWG'den|< ?24 AWG", c)):
                    h(yer, "AWG", t.group(0), "tabloda olmayan kesit (%s)" % ", ".join(map(str, E["awg"])))
            for anahtar, desen in (("kafa 12 V", r"[Kk]afa 12 V"), ("ana hat", r"[Aa]na hat"), ("şarj kol", r"(?<![öÖ]n )[Şş]arj kol\w*"),
                                   ("uzatma", r"[Uu]zatma\w*")):
                for t in re.finditer(desen + r"[^.;:\n]{0,25}?(\d+)\s?AWG", c):
                    if int(t.group(1)) != E["kesit"][anahtar]:
                        h(yer, "AWG", t.group(0), "%s tabloda %d AWG" % (anahtar, E["kesit"][anahtar]))
            # düzeltme turu 1 (M13): kablo kimliğinin hemen ardındaki kesit o kablonun kesiti ("G22, 22 AWG"; araya başka kimlik ya da
            # köprü / ara parça sözü girmez, en çok 12 karakter)
            for t in re.finditer(r"(?<![–-])\b([A-Z]{1,2}\d{2})\b(?:[,:]?|\s?\()(?:[^.;\n\dA-Z]{0,8})(\d+)\s?AWG(?!['’]?(?:den|dan|ye|ya)\b)(?! [^.;\n]{0,12}(?:köprü|ara parça))", c):
                k_, n_ = t.group(1), int(t.group(2))
                if k_ in E["kimlik_awg"] and n_ != E["kimlik_awg"][k_]:
                    h(yer, "AWG", t.group(0), "%s tabloda %d AWG" % (k_, E["kimlik_awg"][k_]))
            # düzeltme turu 1 (M14): tel köprü kesiti tablodaki köprülerden biri
            for t in re.finditer(r"≥\s?(\d+)\s?AWG[^.;\n]{0,15}köprü", c):
                if int(t.group(1)) not in E["kopru"]:
                    h(yer, "AWG", t.group(0), "tabloda bu kesitte tel köprü yok (%s)" % sorted(E["kopru"]))
            # direnç
            for t in re.finditer(r"(≤\s?)?" + _SAYI + r"\s?(k?)Ω", c):
                v = round(_sayi(t.group(2)) * (1000 if t.group(3) else 1), 3)
                if not t.group(1) and v not in E["ohm"]:
                    h(yer, "direnç", t.group(0), "kaynakta bu değerde direnç yok")
            for t in re.finditer(r"BC337-40[^.;\n]{0,80}?" + _SAYI + r"\s?(k?)Ω", c):
                v = round(_sayi(t.group(1)) * (1000 if t.group(2) else 1), 3)
                if v not in E["surucu"]:
                    h(yer, "direnç", t.group(0), "röle sürücüsünde 270 Ω seri ve 2,2 kΩ taban direnci")
            for t in re.finditer(r"[öÖ]n şarj[^.;\n]{0,30}?" + _SAYI + r"\s?Ω", c):
                if round(_sayi(t.group(1)), 3) not in E["on_sarj"]:
                    h(yer, "direnç", t.group(0), "ön şarj direnci tabloda %s Ω" % sorted(E["on_sarj"]))
            # düzeltme turu 1 (M15): röle sürücüsünde direncin yeri (seri / taban) pin haritasıyla aynı
            for t in re.finditer(_SAYI + r"\s?(k?)Ω\s+(seri|taban)\b", c):
                v = round(_sayi(t.group(1)) * (1000 if t.group(2) else 1), 3)
                if re.search(r"BC337|sürücü", c) and v != E["yer_ohm"][t.group(3)]:
                    h(yer, "direnç", t.group(0), "röle sürücüsünde %s direnci %g Ω (pin haritası)" % (t.group(3), E["yer_ohm"][t.group(3)]))
            # düzeltme turu 1 (M24): ön şarj beklemesi "en az N ms" E9'daki değer
            for t in re.finditer(r"en az (\d+) ms", c):
                if re.search(r"K2|ön şarj|bekle", c) and int(t.group(1)) != E["onsarj_ms"]:
                    h(yer, "E9", t.group(0), "ön şarj beklemesi en az %d ms (elektrik.md E9)" % E["onsarj_ms"])
            # terimler: açık işler turu (F10h-kontrol-2 §3.1-6): MOSFET / WAGO / ses kartı yalnız TERIM_ISTISNA'daki tam cümlede
            t = re.search(_TERIM, c)
            if t and _RK.normal(c) not in _TERIM_ISTISNA:
                h(yer, "terim", t.group(0), {"MOSFET": "röle sürücüsü BC337-40 (BJT)", "WAGO": "düğümler M5 saplama + halka pabuç ve 5,08 "
                  "mm vidalı klemens (WAGO yok)"}.get(t.group(0), "USB ses kartı kablajdan çıktı (yedek, takılmaz)")
                  + "; istisna yalnız TERIM_ISTISNA tam cümle listesinde")
            # düzeltme turu 1 (M21, M22, M28): açık kararlar (K52, K60, K61) yalnız "karar bekliyor / bağlı" cümlesinde; Ö4 köprüsüz kalmaz
            for t in re.finditer(r"\b(K52|K60|K61)\b", c):
                if not re.search(r"karar\w*\s+bekl|bekliyor|karar verilene kadar|kararına bağlı|karara bağlı", c):
                    h(yer, "karar", t.group(0), "%s açık karar: 'karar bekliyor' yazılmalı" % t.group(1))
            # açık işler turu (F10h-kontrol-2 §3.1-8): "çekmez" sözcüğü Ö4 kuralını affetmez
            if re.search(r"Ö4", c) and re.search(r"köprüsüz|köprü\w*\s+(?:sök|çıkar|takma)", c):
                h(yer, "Ö4", re.search(r"köprüsüz|köprü\w*\s+\w+", c).group(0), "Ö4 yeri karar verilene kadar tel köprüyle kapalı (köprüsüz röle çekmez)")
            if re.search(r"[Hh]ızlı klemens", c):
                h(yer, "terim", "hızlı klemens", "tabloda yok")
            if re.search(r"USB 3\.0", c) and not re.search(r"değil|geçmez|yerine", c):
                h(yer, "terim", "USB 3.0", "hub uzatması USB 2.0")
            for t in re.finditer(r"karar bekliyor", c):
                p = c[max(0, t.start() - 25):t.end() + 25]
                k = re.search(r"\bK(1|10|11|14)\b(?! a)", p)
                if k:
                    h(yer, "karar", p.strip(), "K%s kapandı" % k.group(1))
            if re.search(r"varsayım,?\s*K10\b|\bK11 b\b", c):
                h(yer, "karar", re.search(r"varsayım,?\s*K10\b|\bK11 b\b", c).group(0), "K10 / K11 kapandı (K10 a, K11 a)")
            for t in re.finditer(r"(?<!en az )\b300 ms", c):
                h(yer, "E9", t.group(0), "ön şarj beklemesi 'en az 300 ms' (boş aküde 500 ms önerilir)")
            if re.search(r"harici besleme", c) and not re.search(r"beslemesiz|hayır|yok|değil", c):
                h(yer, "terim", "harici besleme", "hub harici beslemesiz (Ö2)")
    return out


def kaynak_metinler(R=None, ham=False):
    """rehber_metin.py kaynağındaki görünen metinler (FreeCAD'siz, veri üretmeden): (yer, metin). ham: yer tutucular çözülmeden
    (ADIM_HAM / KABLO_AD_HAM / SEMA_HAM; çıplak sayı denetimi için)."""
    R = R or RM
    ADIM, KAD, SEMA = (R.ADIM_HAM, R.KABLO_AD_HAM, R.SEMA_HAM) if ham else (R.ADIM, R.KABLO_AD, R.SEMA)
    out = []
    for kod, a in ADIM.items():
        y = "kaynak %s" % kod
        for k in ("baslik", "is_", "baglanti_md", "alet", "erisim"):
            if isinstance(a.get(k), str):
                out.append((y + " " + k, a[k]))
        for k in ("kontrol", "kablo", "not_"):
            out += [(y + " " + k, t) for t in (a.get(k) or []) if isinstance(t, str)]
        for n, g in enumerate(a.get("sira") or []):
            out += [(y + " alt adım %d %s" % (n + 1, k), g.get(k) or "") for k in ("ad", "is_")]
    out += [("kaynak KABLO_AD %d" % n, v[1]) for n, v in KAD.items()]
    out += [("kaynak SEMA %s" % s[1], s[3]) for s in SEMA]
    return out


# P10.7b1 düzeltme turu 1 (F10h-kontrol Ü1, §2-3): kaynak modunun genişletilmiş kapsamı. (1) CAD parça adları ve kodları:
# tasarim/freecad/montaj/montaj-analiz.json (FreeCAD'in yazdığı parça listesi; FreeCAD istemez), rehberin göstereceği hâliyle
# (rehber_metin.tr: TR sözlüğü + AD_CEVIRI). (2) rehber/app.js ve rehber/yazdir.html içindeki sabit metinler (tırnak içi, en az bir
# boşluklu, harf taşıyan dizgeler; HTML'de etiket dışı metin). (3) rehber_veri.py'nin ürettiği sabit metinler (tırnak içi, boşluklu).
MONTAJ_ANALIZ = os.path.join(ROBOT, "tasarim", "freecad", "montaj", "montaj-analiz.json")
ARAYUZ_DOSYALARI = [os.path.join(ROBOT, "rehber", "app.js"), os.path.join(ROBOT, "rehber", "yazdir.html"), os.path.join(HERE, "rehber_veri.py")]


def cad_ad_metinleri(R=None, yol=MONTAJ_ANALIZ):
    """CAD parça adları / kodları, rehberde görünecek hâliyle: [(yer, metin)]. Dosya yoksa boş liste ve uyarı (çağıran sayar)."""
    R = R or RM
    if not os.path.exists(yol):
        return None
    P = json.load(open(yol, encoding="utf-8"))
    P = P.get("parcalar", P) if isinstance(P, dict) else P
    gor, out = set(), []
    for p in P:
        for k in ("ad", "kod"):
            v = p.get(k)
            if not v or (k, v) in gor:
                continue
            gor.add((k, v))
            out.append(("CAD parça %s %s" % (k, v[:40]), R.tr(v)))
    return out


def arayuz_metinleri(dosyalar=ARAYUZ_DOSYALARI):
    """app.js / yazdir.html / rehber_veri.py sabit metinleri: [(yer, metin)]."""
    out = []
    for yol in dosyalar:
        if not os.path.exists(yol):
            continue
        ad = os.path.basename(yol)
        s = open(yol, encoding="utf-8").read()
        if ad.endswith(".py"):
            s = "\n".join(l for l in s.split("\n") if not l.lstrip().startswith("#"))
        else:
            s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
            s = "\n".join(re.sub(r"(^|\s)//.*$", " ", l) for l in s.split("\n"))
        for t in re.finditer(r"\"((?:[^\"\\\n]|\\.){8,})\"|'((?:[^'\\\n]|\\.){8,})'|`([^`]{8,})`", s):
            m = next(g for g in t.groups() if g is not None)
            if " " in m and re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]{3,}", m):
                out.append(("%s satır %d" % (ad, s.count("\n", 0, t.start()) + 1), m))
        if ad.endswith(".html"):
            for t in re.finditer(r">([^<>{}]*[A-Za-zÇĞİÖŞÜçğıöşü]{3,}[^<>{}]*)<", s):
                if t.group(1).strip():
                    out.append(("%s satır %d (html)" % (ad, s.count("\n", 0, t.start()) + 1), t.group(1).strip()))
    return out


# Çıplak kritik sayı (P10.7b1 düzeltme turu 1, F10h-kontrol §2-1): rehber_metin'in ham metninde yer tutucudan gelmeyen GPIO numarası,
# sigorta bağlamında akım, kesit (AWG), röle sürücüsü / ön şarj bağlamında direnç, ön şarj / röle bağlamında süre, sigorta yuvası
# sırası ve yer tutucunun yanına elle yazılmış bıçak tipi. Bağlam kelimesi sayının 40 karakter önünde ya da 20 karakter ardında,
# aynı cümlede (. ; ! ? satır sonu) aranır. Muaf: CIPLAK_MUAF (cümle deseni + gerekçe; kısa tutulur).
# Açık işler turu (F10h-kontrol-2 §3.1-3, -4, -5): karşılaştırma Türkçe duyarlı küçük harfte (İ / I / ı / i: cümle başı "Ön şarj");
# birimler normalleştirilir (mA, kA, mΩ, kΩ, MΩ, "ohm"; ondalık virgül ya da nokta; sayı ile birim arasında boşluk, dar / bölünmez
# boşluk ya da satır sonu); sözle yazılmış değer (Türkçe sayı sözcüğü + amper / A / ohm / AWG) kritik bağlamda hata. Desenler küçük
# harf metne uygulanır.
_SAYI_SOZ = (r"(?:sıfır|bir|iki|üç|dört|beş|altı|yedi|sekiz|dokuz|on|yirmi|otuz|kırk|elli|altmış|yetmiş|seksen|doksan|yüz|bin|"
             r"buçuk|yarım)")
_SOZ_DEGER = r"\b" + _SAYI_SOZ + r"(?: " + _SAYI_SOZ + r")* "
_SIGORTA_BAGLAM = r"sigorta|\bf[1-6]\b|\bmini\b|standart|bıçak|yuva|koruma"
_DIRENC_BAGLAM = r"bc337|sürücü|taban|\bseri\b|ön şarj"
CIPLAK_KURAL = [
    ("GPIO", r"gpio ?\d+", None),
    ("sigorta akımı", r"(?<![\w{.,])\d+(?:[.,]\d+)? ?[mk]?a\b(?!['’]?(?:wg))", _SIGORTA_BAGLAM),
    ("sigorta akımı (sözle)", _SOZ_DEGER + r"(?:mili|kilo)?(?:amper\w*|a\b)", _SIGORTA_BAGLAM),
    ("kesit", r"(?<![\w{.,])\d+ ?awg", None),
    ("kesit (sözle)", _SOZ_DEGER + r"awg", None),
    ("direnç", r"(?<![\w{.,])\d+(?:[.,]\d+)? ?[mk]?(?:ω|ohm\b)", _DIRENC_BAGLAM),
    ("direnç (sözle)", _SOZ_DEGER + r"(?:kilo|mili|mega)?(?:ohm\w*|ω)", _DIRENC_BAGLAM),
    ("süre", r"(?<![\w{.,])\d+(?:[.,]\d+)? ?(?:ms|s|sn|saniye|milisaniye)\b", r"ön şarj|röle|\bk[12]\b|gpio|\{gpio|bekle|bırakıl"),
    ("yuva", r"\b\d\. yuva", r"\bf[1-6]\b"),
    ("saplama sırası", r"\(\d\.\) saplama|\b\d\. saplama", None),          # açık işler turu (B13): bara saplamasının sırası
    ("bıçak tipi", r"\{a\.[^}]+\}\s*\(?(?:mini|standart)\b", None),
]
# Yük bağlamı muafiyeti (açık iş 5): yalnız aynı yan cümlede yük / çeker / tüketim / varsayım sözcüğü olan VE aynı yan cümlede sigorta
# bağlamı sözcüğü (sigorta, F<n>, koruma, bıçak, mini, standart) olmayan sayı. "sürekli", "anma", "ölç", "sınır" muafiyet değil.
CIPLAK_YUK = r"yük\w*|\bçek(?:er|iyor|tiği)\b|tüketim\w*|varsayı\w*"
CIPLAK_YUK_DEGIL = r"sigorta|\bf[1-6]\b|koruma|bıçak|\bmini\b|standart"
CIPLAK_MUAF_SAYI = 1                                                # açık iş 9: muaf listesinin uzunluğu sabit (bozma denemesi sınar)
CIPLAK_MUAF = [
    (r"24 AWG'den inceyse", "K04 kesit kuralının eşiği (kablolar.json K04 teyit: '24 AWG'den inceyse'), bir kablonun kesiti değil"),
]
# Yük / sınır bağlamı (CIPLAK_YUK) muaf listesi değil kural: "QLED akımı 0,9 A varsayım", "1N5819'un sınırı 1 A", "10 A soketinde"
# (multimetre) gibi sigorta olmayan akımlar sigorta bağlamı kelimesi taşımadıkça zaten sayılmaz.


def _bosluk(m):
    """Dar / bölünmez boşluk ve satır sonu tek boşluk (sayı ile birim ya da etiket ile değer arasında satır sonu kuralı delmesin)."""
    return re.sub(r"[ \t\u00a0\u202f\u2009]*\n[ \t\u00a0\u202f\u2009]*|[\u00a0\u202f\u2009]", " ", m or "")


def ciplak_sayilar(metinler):
    """Ham metinlerde yer tutucudan gelmeyen kritik sayı: [dict(yer, tur, ifade, cumle)]."""
    out = []
    for yer, m in metinler:
        m = _bosluk(re.sub(r"`[^`]*`", " ", m or ""))
        for c in re.split(_CUMLE_GENIS, m):
            if any(re.search(d, c) for d, _ in CIPLAK_MUAF):
                continue
            k = _RK.tr_kucuk(c)
            for tur, desen, baglam in CIPLAK_KURAL:
                for t in re.finditer(desen, k):
                    on, ar = k[max(0, t.start() - 40):t.start()], k[t.end():t.end() + 20]
                    if baglam and not re.search(baglam, on + " " + t.group(0) + " " + ar):
                        continue
                    if tur.startswith("sigorta akımı"):
                        b_, s_ = yan_cumle(k, t.start())
                        yc = k[b_:s_]
                        if re.search(CIPLAK_YUK, yc) and not re.search(CIPLAK_YUK_DEGIL, yc):
                            continue
                    out.append(dict(yer=yer, tur=tur, ifade=c[t.start():t.end()], cumle=c[:160]))
    return out


def muaf_denetle():
    if len(CIPLAK_MUAF) == CIPLAK_MUAF_SAYI:
        return []
    return [dict(yer="rehber_denetim CIPLAK_MUAF", tur="muaf listesi", ifade="%d madde" % len(CIPLAK_MUAF),
                 cumle="CIPLAK_MUAF_SAYI %d; liste değişikliği bağımsız kontrolden geçip ikisi birlikte değişir" % CIPLAK_MUAF_SAYI)]


def bozuk_yer_tutucu(metinler):
    """Çözülmüş metinde kalan '{', '}' ya da '⟦ ⟧' (bozuk yazılmış yer tutucu: "{A.F6}", "{a. F6}"; açık iş 1): [dict(yer, ifade)]."""
    out = []
    for yer, m in metinler:
        for t in re.finditer(r"[{}⟦⟧]", m or ""):
            out.append(dict(yer=yer, ifade=(m or "")[max(0, t.start() - 20):t.end() + 20]))
            break
    return out


def baglam_denetle(metinler):
    """Anahtar ↔ bağlam (açık iş 2): ham metinde her yer tutucunun (grupsa her üyenin) gösterdiği varlığın adı aynı cümlede geçmeli
    (rehber_deger.varlik_adlari, adlar tablodan türer). Doner [dict(yer, yer_tutucu, eksik, cumle)]. İki varlığın birlikte geçtiği
    cümlede yer değiştirmeyi bu kural tutamaz: onu onaylı kritik metin kaydı tutar."""
    D = _RDG.degerler()
    out = []
    for yer, m in metinler:
        for c in re.split(_CUMLE_GENIS, m or ""):
            for t in _RDG.YER_TUTUCU.finditer(c):
                try:
                    e = D.varlik_eksik(t.group(1), t.group(2), c)
                except (KeyError, TypeError) as x:
                    e = ["? %s" % x]
                if e:
                    out.append(dict(yer=yer, yer_tutucu=t.group(0), eksik=e, cumle=c[:160]))
    return out


# ------------------------------------------------------------------ kayıt → rehber tamlığı (düzeltme turu 2, F10h-kontrol-3 §2)
# Öbür denetimler "rehberdeki değer kayıtta doğru mu"ya bakar; bu sınama tersine bakar: kayıttaki (kablolar.json, pin haritası) her
# güvenlik öğesi rehber metninde geçiyor mu. Geçmeyen öğe HATA (anahtarlı baranın köprüleri böyle kaçmıştı). Öğe türleri ve ölçüt:
#   koruyucu        koruyucular'da tür "sigorta" olan her kayıt: ham metinde {a.<koruyucu>} yer tutucusu (değeriyle geçmeli)
#   köprü           bara-pabuc.kopruler'deki her bara: {kopru.<b>} ve {kopru_adet.<b>} (kesit ve adet; eşleme rehber_deger.KOPRU_BARA)
#   saplama düğümü  bara-pabuc.dugumler'deki her bara: {saplama.<b>} (saplama sayısı; rehber_deger.SAPLAMA_DUGUM) ve yerleşimi kayıtlı
#                   her iletken: {saplama.<kimlik>}
#   GPIO rolü       pin haritası § 9'daki her pin: {gpio.<ad>} ya da çözülmüş metinde "GPIO<n>"
#   anahtar         anahtarlar'daki her kayıt (zinciri kesenler hariç): TAMLIK_AD'daki adlardan biri çözülmüş metinde
#   acil stop zinciri  devre türü "acil stop…" olan her kablo (kimliğiyle) ve zinciri kesen her anahtar (zinciri_kesen_turler; adıyla)
# Bilinçli dışarıda bırakılan öğe TAMLIK_MUAF'ta (tür, düzenli ifade, gerekçe); liste onay kaydına dahil. Muaf deseni hiçbir öğeyi
# tutmuyorsa ya da rehberde zaten geçen bir öğeyi tutuyorsa HATA (liste sessizce büyümez / eskimez). Eşlemesi olmayan yeni kayıt
# (yeni bara, yeni anahtar) HATA: tamlık eşlemesi de güncellenmeli. 74 kablonun kimliğiyle geçip geçmediği BİLGİ olarak sayılır.
TAMLIK_AD = {
    "ana-anahtar": ["ana anahtar"],
    "K1-kontak": ["K1 kontağı", "röle K1 kontağı"],
    "K2-kontak": ["K2 kontağı"],
    "mantar": ["mantar"],
    "K1-bobin": ["K1 bobini", "röle K1 bobini"],
    "K2-bobin": ["K2 bobini"],
    "gogus-regulatoru": ["göğüs regülatörü"],
    "esp32-3v3": ["3V3 regülatörü"],
}
TAMLIK_MUAF = [
    ("GPIO rolü", r"SONAR_\w+_ECHO|(SOL|SAG)_(IS|ILERI_PWM|GERI_PWM|ENK_A|ENK_B)|BTS_EN|AKU_ADC",
     "sinyal / ölçüm pini (enkoder, BTS, sonar, akü ölçümü): güç ve acil stop zincirinde değil; pin numarası pin haritasında ve "
     "yazılımda, rehber yazmaz (uçlar kablolar.md'de)"),
    ("GPIO rolü", r"I2C_SDA|I2C_SCL|UART0_TX|UART0_RX", "veri yolu (I2C, CP2102 üzerinden USB): ESP32 kartının sabit ucu; rehber pin "
     "numarası yazmaz (uçlar kablolar.md'de)"),
    ("GPIO rolü", r"DURUM_LED", "kart üstü LED, dışarı bağlanmaz (pin haritası)"),
    ("anahtar", r"esp32-3v3", "ESP32 kartının kendi regülatörü: montajda takılan ya da bağlanan ayrı parça değil"),
]


def tamlik_denetle(ham=None, T=None, PH=None):
    """Kayıt → rehber tamlığı. ham: [(yer, metin)] yer tutucular çözülmeden (varsayılan kaynak_metinler(ham=True)).
    Doner dict(hata=[str], tarandi={tür: n}, muaf=[str], kablo_toplam, kablo_yok=[kimlik])."""
    ham = ham if ham is not None else kaynak_metinler(ham=True)
    D = _RDG.degerler() if (T is None and PH is None) else _RDG.Degerler(T, PH)
    T, PH = D.T, D.PH
    mh = "\n".join(t or "" for y, t in ham)
    yt = {(m.group(1), u) for m in _RDG.YER_TUTUCU.finditer(mh) for u in m.group(2).split("|")}
    coz = _RK.tr_kucuk(D.coz(mh))
    kim = D.cumle_kimlikleri(_RDG.YER_TUTUCU.sub(" ", mh))
    BP = T["klemens_turleri"]["bara-pabuc"]
    hata, muaf_kullanilan, tarandi = [], [], collections.Counter()
    muaf_tuttu = collections.Counter()

    def ad_var(adlar):
        return any(re.search(r"(?<!\w)%s" % re.escape(_RK.tr_kucuk(a)), coz) for a in adlar)

    def oge(tur, ad, var, neden):
        tarandi[tur] += 1
        m = [i for i, (t, d, g) in enumerate(TAMLIK_MUAF) if t == tur and re.fullmatch(d, ad)]
        for i in m:
            muaf_tuttu[i] += 1
        if m and var:
            hata.append("%s %s: muaf listesinde ama rehberde geçiyor (TAMLIK_MUAF'tan çıkar)" % (tur, ad))
        elif m:
            muaf_kullanilan.append("%s %s: %s" % (tur, ad, TAMLIK_MUAF[m[0]][2]))
        elif not var:
            hata.append("%s %s: %s" % (tur, ad, neden))

    for k, v in sorted(T["koruyucular"].items()):
        if v.get("tur") == "sigorta":
            oge("koruyucu", k, ("a", k) in yt, "kayıtta var, rehberde {a.%s} yer tutucusuyla geçmiyor" % k)
    ters_k = {v: k for k, v in _RDG.KOPRU_BARA.items()}
    for b, v in sorted((BP.get("kopruler") or {}).items()):
        if not isinstance(v, dict):
            continue
        a = ters_k.get(b)
        if a is None:
            oge("köprü", b, False, "kayıtta köprü var, rehber_deger.KOPRU_BARA'da yer tutucu eşlemesi yok")
            continue
        eks = [t for t in ("kopru", "kopru_adet") if (t, a) not in yt]
        oge("köprü", b, not eks, "kayıtta %d × %d AWG %s köprü var, rehberde %s yok" % (
            v.get("adet") or 0, v.get("awg") or 0, v.get("renk") or "", " / ".join("{%s.%s}" % (t, a) for t in eks)))
        for n, lst in sorted((v.get("yerlesim") or {}).items()):
            for x in lst:
                kk = x.split("/")[0]
                oge("saplama düğümü", "%s saplama %s: %s" % (b, n, kk), ("saplama", kk) in yt,
                    "yerleşimi kayıtlı, rehberde {saplama.%s} yok" % kk)
    ters_s = {v: k for k, v in _RDG.SAPLAMA_DUGUM.items()}
    for b in sorted(BP.get("dugumler") or {}):
        a = ters_s.get(b)
        oge("saplama düğümü", b, a is not None and ("saplama", a) in yt,
            "kayıtta saplama düğümü var, rehberde saplama sayısı yer tutucusu (%s) yok" % ("{saplama.%s}" % a if a else "eşleme yok"))
    for p, v in sorted(PH["pinler"].items()):
        oge("GPIO rolü", p, ("gpio", p) in yt or bool(re.search(r"gpio%d(?!\d)" % v["gpio"], coz)),
            "pin haritasında var (GPIO%d), rehberde {gpio.%s} ya da GPIO%d geçmiyor" % (v["gpio"], p, v["gpio"]))
    zincir = set(T.get("zinciri_kesen_turler") or [])
    for k, v in sorted(T["anahtarlar"].items()):
        tur = "acil stop zinciri" if v.get("tur") in zincir else "anahtar"
        if k not in TAMLIK_AD:
            oge(tur, k, False, "kayıtta var, TAMLIK_AD'da adı yok (tamlık eşlemesini güncelle)")
            continue
        oge(tur, k, ad_var(TAMLIK_AD[k]), "kayıtta var (%s), rehberde adıyla (%s) geçmiyor" % (v.get("ad"), " / ".join(TAMLIK_AD[k])))
    for r in T["kablolar"]:
        if (r.get("devre") or "").startswith("acil stop"):
            oge("acil stop zinciri", r["kimlik"], r["kimlik"] in kim, "acil stop kablosu, rehberde kimliğiyle geçmiyor")
    for i, (t, d, g) in enumerate(TAMLIK_MUAF):
        if not muaf_tuttu[i]:
            hata.append("TAMLIK_MUAF %s %s: hiçbir öğeyi tutmuyor (listeden çıkar)" % (t, d))
    yok = [r["kimlik"] for r in T["kablolar"] if r["kimlik"] not in kim]
    return dict(hata=hata, tarandi=dict(tarandi), muaf=muaf_kullanilan, kablo_toplam=len(T["kablolar"]), kablo_yok=yok)


# ------------------------------------------------------------------ onaylı kritik metin kaydı (açık işler turu, F10h-kontrol-2 §3.1)
# Kritik girdi: (a) içinde yer tutucu geçen her cümle; (b) bir ZORUNLU / ZORUNLU_ALAN / ZORUNLU_CUMLE deseninin tuttuğu metinle
# çakışan her cümle; (c) KRITIK_SOZ'ü taşıyan her cümle (elektrik, enerji ve sıra: sigorta, akü, gerilim, köprü, katot / anot, GPIO,
# röle, mantar, ölçüm, "karar bekliyor", K52 / K60 / K61, Ö4, MOSFET / WAGO / ses kartı …); (d) kuralların kendisi: ZORUNLU listeleri,
# TERIM_ISTISNA, CIPLAK_MUAF, CIPLAK_KURAL, CIPLAK_YUK, YASAK, OLUMSUZLAMA; (e) rehber_kablo'nun eşleme ve görünüm tabloları
# (CAD_ESLEME, GEO_ISTISNA, GEO_DAL, PARCA_CAD, MODELSIZ_KONUM, KESIT_YARICAP, TEMA_TON, eşikler). Ham metin (yer tutucular çözülmeden)
# özetlenir: {a.F3} ↔ {a.F5}, "tak" ↔ "takma", "katot" ↔ "anot", "önce" ↔ "sonra", K52'nin silinmesi, listeye madde eklenmesi hepsi
# "kritik girdi değişti" olarak durur.
# Düzeltme turu 2 (F10h-kontrol-3 §3.1): kapsam anahtar sözcüğe bağlı değil: kaynak metinlerin BÜTÜN cümleleri kayda girer (neden
# etiketi yalnız bilgi; etiketsiz cümle "metin"). Böylece "uzatılmaz" → "uzatılabilir", "önce" → "sonra", uyarı cümlesinin silinmesi,
# yeni cümle eklenmesi ve iki cümlenin yer değiştirmesi de (alan içi sıra) onay ister. Kayıt tam metni de tutar (fark satırı için).
KRITIK_SOZ = (r"sigorta|akü|gerilim|enerji|köprü|katot|anot|gpio|röle|mantar|acil stop|ana anahtar|xt60|ölç|kısa devre|ters paralel|"
              r"\d+(?:,\d+)? ?v\b|\d+(?:,\d+)? ?a\b|awg|Ω|bobin|diyot|1n4007|1n5819|pc817|bc337|bts|xl4016|vbus|usb|karar bekl|"
              r"karar verilene|\bk5[0-9]\b|\bk6[0-9]\b|ö4|mosfet|wago|ses kart|takılmaz|takılı değil|takmadan|bağlamadan|bağlanmadan|"
              r"enerjisiz|ayrık|yalıt|e9|ön şarj|bara")


def kritik_girdiler(metinler_ham=None, R=None):
    """Bugünkü kritik girdiler: {bolum: [girdi]} (bölümler: metin, liste, kablo)."""
    R = R or RM
    m = metinler_ham if metinler_ham is not None else kaynak_metinler(R, ham=True)
    D = _RDG.degerler()
    zh = []
    desenler = ([(k, d) for k, d, ad in zorunlu_listesi(zh)] + [(k, d) for k, alan, d, ad in zorunlu_alan_listesi(zh)]
                + [(k, x) for k, o, y, ad in zorunlu_cumle_listesi(zh) for x in (o, y)])
    out = {"metin": [], "liste": [], "kablo": []}
    for yer, t in m:
        p = yer.split()
        kod = p[1] if len(p) > 1 and p[0] == "kaynak" else ""
        if kod == "SEMA":
            kod = "SEMA " + " ".join(p[2:])
        cumleler = [c for c in re.split(_CUMLE_GENIS, t or "") if c.strip()]
        coz = [D.coz(c) for c in cumleler]
        alan_coz = D.coz(t or "")
        aralik, poz = [], 0
        for c in coz:
            i = alan_coz.find(c, poz)
            aralik.append((i, i + len(c)) if i >= 0 else (-1, -1))
            if i >= 0:
                poz = i + len(c)
        zor = set()
        for k, d in desenler:
            if k != kod:
                continue
            for z in re.finditer(d, alan_coz):
                for n, (a, b) in enumerate(aralik):
                    if a >= 0 and a < z.end() and z.start() < b:
                        zor.add(n)
        for n, c in enumerate(cumleler):
            neden = []
            if "{" in c:
                neden.append("yer tutucu")
            if n in zor:
                neden.append("zorunlu")
            if re.search(KRITIK_SOZ, _RK.tr_kucuk(c)):
                neden.append("anahtar sözcük")
            out["metin"].append(_RK.girdi(yer, c, ", ".join(neden) or "metin"))
    for ad, lst in (("ZORUNLU", ZORUNLU), ("ZORUNLU_ALAN", ZORUNLU_ALAN), ("ZORUNLU_CUMLE", ZORUNLU_CUMLE),
                    ("TERIM_ISTISNA", TERIM_ISTISNA), ("CIPLAK_MUAF", CIPLAK_MUAF), ("CIPLAK_KURAL", CIPLAK_KURAL), ("YASAK", YASAK),
                    ("TAMLIK_MUAF", TAMLIK_MUAF), ("TAMLIK_AD", sorted(TAMLIK_AD.items()))):
        for x in lst:
            out["liste"].append(_RK.girdi("LISTE " + ad, repr(x), "kural listesi"))
    for ad, x in (("CIPLAK_YUK", CIPLAK_YUK), ("CIPLAK_YUK_DEGIL", CIPLAK_YUK_DEGIL), ("OLUMSUZLAMA", OLUMSUZLAMA),
                  ("KRITIK_SOZ", KRITIK_SOZ), ("CIPLAK_MUAF_SAYI", CIPLAK_MUAF_SAYI)):
        out["liste"].append(_RK.girdi("LISTE " + ad, repr(x), "kural"))
    try:
        import rehber_kablo as _RKB
        out["kablo"] = _RKB.kritik_tablolar()
    except Exception as e:                                           # eşleme modülü okunamazsa kayıt eksik: karşılaştırma hata verir
        out["kablo"] = [_RK.girdi("rehber_kablo", "okunamadı: %s" % e, "hata")]
    return out


def kritik_fark(guncel=None):
    return _RK.karsilastir(_RK.oku(), guncel if guncel is not None else kritik_girdiler())


def yasak_metinler(metinler):
    """YASAK kalıpları serbest metin listesinde (kaynak modu): (bulgu, istisna) — yasak_tara ile aynı kural."""
    V = dict(adimlar=[dict(kod=yer, baslik="", is_=m) for yer, m in metinler])
    return yasak_tara(V)


ELEKTRIK_BOZMA = [
    # (ad, adım kodu, alan, eklenen metin) — her biri elektrik_denetle'de en az bir hata vermeli
    ("eski pin: K2'yi GPIO2 sürer", "F1", "kontrol", "ESP32'deki program bilinmiyor: K2'yi süren GPIO2 kartın LED pini"),
    ("eski şarj sigortası 10 A", "K1", "is_", "Şarj girişi: kapaklı mini sigorta yuvası (şarj 10 A) → XT60 şarj girişi ucu"),
    ("eski göğüs sigortası mini 2 A", "F3", "is_", "Akü XT60 ayrık, ana anahtar kapalıyken göğüs ekranı mini 2 A sigortasını tak"),
    ("MOSFET adı", "K1", "kablo", "Acil stop: F5 → mantar (NC) → röle bobini → MOSFET (arayüz kartı)"),
    ("WAGO düğümü", "B5a", "kablo", "Panelde WAGO yıldız noktası ve sigorta kutusu girişleri erişilebilir kalsın"),
    ("yanlış AWG (kafa 12 V 16 AWG)", "K2", "is_", "Kafa 12 V (16 AWG çift): direk ön yüzü → R62 → boyun"),
    ("tabloda olmayan AWG", "K1", "is_", "Ana hat 10 AWG ile çekilir"),
    ("yanlış direnç (BC337-40 1 kΩ taban)", "K1", "kontrol", "BC337-40 #1 tabanında 1 kΩ seri direnç"),
    ("kaynakta olmayan direnç", "E4", "is_", "Bölücü 10 kΩ / 2,7 kΩ"),
    ("ses kartı yolu", "E4", "kablo", "Ses: ReSpeaker → Pi USB 1, ses kartı → Pi USB 2, ses kartı L 3,5 mm → PAM8403"),
    ("kutu sigortası mini", "F3", "not_", "12 V dalı F6 mini 3 A ile korunur"),
    ("F1 yanlış akım", "K1", "is_", "F1 15 A → röle K1 → anahtarlı bara"),
    ("kapanmış karar 'karar bekliyor'", "F5", "not_", "Altıncı USB cihazı karar bekliyor (K1): şimdilik hub'da 2 port boş"),
    ("ön şarj 300 ms (en az değil)", "F5", "is_", "röle K2 → 300 ms → PC817 #2 LOW (bara var) → röle K1"),
    ("PC817 #2 yanlış pin", "F5", "is_", "GPIO23 (PC817 #2) LOW teyidi"),
    ("hızlı klemens", "K1", "kontrol", "Hızlı klemens en çok 2,5 mm²: 12 AWG ana hatta kullanma"),
    # P10.7b1 düzeltme turu 1: F10h-kontrol §4'te kaçan bozmaların çözülmüş metindeki biçimi (bağlam kuralları)
    ("M2 PC817 #1 ok ile yanlış pin", "K1", "is_", "PC817 #1 girişi → GPIO5"),
    ("M5 çevre hat sigortası 5 A mini", "K1", "is_", "XL4016 çevre → 5 A mini hat sigortası → arayüz kartı"),
    ("M6 G22 sigortası 7,5 A", "K1", "is_", "PC817 #2 algı teli (G22): bara ucunda 7,5 A mini hat sigortası"),
    ("M7 F6 (mini", "K2", "is_", "sigorta kutusunun F6 3 A (mini) yuvasından ayrı dal"),
    ("M8 F6 2. yuva", "F3", "is_", "göğüs ekranının F6 3 A sigortasını (standart bıçak, sigorta kutusunun 2. yuvası) tak"),
    ("M9 XL4016 C 7,5 A", "F5", "is_", "XL4016 hat sigortalarını (mini; A 7,5 A, B 7,5 A, C 7,5 A) tak"),
    ("M10 MOSFET + ilgisiz 'değil'", "K1", "kablo", "Röle sürücüsü MOSFET (arayüz kartı) ve mantar henüz takılı değil"),
    ("M11 WAGO + ilgisiz 'yok'", "B5a", "kablo", "Panelde WAGO yıldız noktası kullanılır ve sigorta kutusunda bu adımda hiç boş yuva yok"),
    ("M13 G22 16 AWG", "K1", "is_", "PC817 #2 algı teli (G22, 16 AWG): bara ucunda"),
    ("M14 tel köprü ≥ 22 AWG", "K1", "is_", "dört ucu kart üstünde ≥ 22 AWG tel köprüyle lehimli"),
    ("M15 dirençler yer değiştirmiş", "K1", "is_", "Her sürücüde 2,2 kΩ seri taban direnci ve 270 Ω taban → GND (BC337-40)"),
    ("M21 K52 kararlaştırılmış gibi", "K1", "is_", "Göğüs regülatörü güç panelinde (K52): G20 oraya gider"),
    ("M22 K61 kararlaştırılmış gibi", "K2", "not_", "Konuşmak için basılan düğme (O-12) göğüs bandında (K61)"),
    ("M24 en az 100 ms", "F5", "is_", "röle K2 → en az 100 ms bekle → PC817 #2 LOW"),
    ("M28 Ö4 köprüsüz", "K1", "is_", "Ö4 için ayrılan iki uçlu yer köprüsüz bırakılır"),
    # açık işler turu (F10h-kontrol-2 B29, B30, B38b): yakın "değil" / "yok" / "çekmez" artık affetmez
    ("B29 MOSFET + yakın 'değil'", "K1", "is_", "Röle sürücüsü (sürücü MOSFET, BC337-40 değil) arayüz kartında"),
    ("B30 WAGO + yakın 'yok'", "K1", "is_", "düğümler WAGO 221 ile, saplama yok"),
    ("B38b Ö4 köprüsüz + 'çekmez'", "K1", "is_", "Ö4 köprüsüz bırakılır; röle çekmez, sorun değil"),
]
# Çıplak sayı bozmaları (ham metin; yer tutucu yerine elle yazılmış değer) ve yakalanmaması gereken yük / sınır cümleleri
CIPLAK_BOZMA = [
    ("çıplak GPIO", "mantar bırakılmışken PC817 #1 (GPIO23) LOW okur", True),
    ("çıplak kutu sigortası", "göğüs ekranının F6 3 A sigortasını tak", True),
    ("çıplak şarj sigortası", "Şarj kolunun 7,5 A mini sigortası bu aşamada da takılı değil", True),
    ("çıplak kesit", "PC817 #2 algı teli (G22, 22 AWG)", True),
    ("çıplak sürücü direnci", "Her sürücüde 270 Ω seri taban direnci", True),
    ("çıplak ön şarj süresi", "röle K2 → en az 300 ms bekle", True),
    ("çıplak yuva", "F6 sigortası kutunun 6. yuvasında", True),
    ("elle bıçak tipi", "F6 {a.F6} (standart) yuvasından", True),
    ("yük varsayımı (yakalanmamalı)", "QLED akımı 0,9 A varsayım, ölçülmedi", False),
    ("diyot sınırı (yakalanmamalı)", "1N5819'un sınırı 1 A: çevre yükleri geri beslenirse aşılabilir", False),
    ("multimetre soketi (yakalanmamalı)", "kırmızı ucu V soketine tak: 10 A soketinde kalırsa multimetre kısa devre olur", False),
    # açık işler turu (F10h-kontrol-2 §3.1-3, -4, -5; B11, B13, B14b, B15, B16, B18, B34)
    ("Türkçe büyük harf (B11)", "Ön şarj direnci (5,6 Ω) panelden yüksekte", True),
    ("saplama sırası (B13)", "akü − → yıldız barasının ortadaki (4.) saplaması", True),
    ("mA (B15)", "F6 5000 mA standart", True),
    ("kA (B16)", "F6 0,005 kA standart", True),
    ("sözle, sözlük içi (B14b)", "F6 dört buçuk A standart", True),
    ("satır sonu", "F6 sigortası\n3 A", True),
    ("'sürekli' muaf değil (B34)", "F5 (sürekli 7,5 A, acil stop)", True),
    ("yük ile sigorta aynı yan cümlede", "hat sigortası 3 A (yük çok az)", True),
    ("yük varsayımı ondalıklı (yakalanmamalı)", "QLED akımı 0,9 A varsayım, sigorta değil: ölçülmedi", False),
]
# açık işler turu: bozuk yer tutucu (B20, B21), anahtar ↔ bağlam (B01, B05, B07, B08), zorunlu tam sözcük (B26, B27)
ACIK_BOZMA = [
    ("bozuk yer tutucu: büyük harf tür (B20)", "bozuk", "F6 {A.F6} standart"),
    ("bozuk yer tutucu: boşluk (B21)", "bozuk", "F6 {a. F6} standart"),
    ("bağlam: F3 cümlesinde {a.F5} (B01)", "baglam", "3. Kafa 12 V (G17, F3 {a.F5}): direk ön yüzü"),
    ("bağlam: G06 cümlesinde {awg.G07} (B05)", "baglam", "Şarj kolu (G06, {awg.G07}): + ucu ana sigortanın yük tarafından"),
    ("bağlam: akü − cümlesinde {saplama.G17} (B07)", "baglam", "2. Toprak (G05): akü − → yıldız barasının ortadaki ({saplama.G17}.) saplaması"),
    ("bağlam: K1 cümlesinde {ms.onsarj_bos} (B08)", "baglam", "Mantara basınca K1 düşer (K2, K1 çektikten {ms.onsarj_bos} sonra bırakılmıştı)"),
    ("grup: üyelerin değeri farklı", "grup", "{awg.G01|G06}"),
]
# düzeltme turu 2: köprüleme fiili yakalanır, çoğul ad ("köprüler") yakalanmaz
YASAK_BOZMA = [
    ("köprüle (emir)", "Mantarın iki ucunu kısa bir telle köprüle", True),
    ("köprülenir (edilgen)", "Ana anahtarın uçları bu adımda köprülenir", True),
    ("köprüleyin", "Sigorta yuvasını köprüleyin", True),
    ("köprüler (çoğul ad, yakalanmamalı)", "Bu adımda takılan köprüler: yıldız barası ve anahtarlı bara", False),
    ("köprüleri (çoğul ad, yakalanmamalı)", "İki baranın köprüleri takılı", False),
]


def elektrik_bozma_denemesi():
    E = elektrik_kaynak()
    temel = elektrik_denetle(kaynak_metinler(), E)
    out = []
    for ad, kod, alan, metin in ELEKTRIK_BOZMA:
        n = len(elektrik_denetle([("bozma %s %s" % (kod, alan), metin)], E))
        out.append(dict(ad=ad, yakalandi=n > 0, hata=n))
    for ad, metin, beklenen in CIPLAK_BOZMA:
        n = len(ciplak_sayilar([("bozma çıplak", metin)]))
        out.append(dict(ad="çıplak: " + ad, yakalandi=(n > 0) == beklenen, hata=n))
    D = _RDG.degerler()
    for ad, tur, metin in ACIK_BOZMA:
        if tur == "bozuk":
            n = len(bozuk_yer_tutucu([("bozma", D.coz(metin, []))]))
        elif tur == "baglam":
            n = len(baglam_denetle([("bozma", metin)]))
        else:
            hz = []
            n = int("⟦" in D.coz(metin, hz)) + len(hz)
        out.append(dict(ad="açık iş: " + ad, yakalandi=n > 0, hata=n))
    # zorunlu desen tam sözcük (B26, B27): bugünkü cümlede "tak" → "takma"
    for kod, eski, yeni in (("F5", "sigortasını tak", "sigortasını takma"), ("F3", "yuvası) tak", "yuvası) takma")):
        metin = "\n".join(t for y, t in kaynak_metinler() if y.split()[:2] == ["kaynak", kod])
        desen = [d for k, d, a in zorunlu_listesi() if k == kod]
        once = all(re.search(d, metin) for d in desen)
        sonra = all(re.search(d, metin.replace(eski, yeni)) for d in desen)
        out.append(dict(ad="açık iş: zorunlu tam sözcük %s '%s'" % (kod, yeni), yakalandi=once and not sonra, hata=int(not sonra)))
    # muaf listesi uzunluğu (B33) ve onay kaydı (kritik cümle değişince fark)
    CIPLAK_MUAF.append((r"göğüs", "bozma"))
    try:
        n = len(muaf_denetle())
    finally:
        CIPLAK_MUAF.pop()
    out.append(dict(ad="açık iş: CIPLAK_MUAF'a madde (B33)", yakalandi=n > 0, hata=n))
    ham = kaynak_metinler(ham=True)
    i = next(i for i, (y, t) in enumerate(ham) if y == "kaynak F5 is_" and "sigortasını tak" in t)
    ham2 = list(ham)
    ham2[i] = (ham[i][0], ham[i][1].replace("sigortasını tak", "sigortasını takma", 1))
    n = len(kritik_fark(kritik_girdiler(ham2)))
    out.append(dict(ad="açık iş: onay kaydı ('tak' → 'takma')", yakalandi=n > 0, hata=n))
    # düzeltme turu 2: yasak fiil / çoğul ad; kayıt → rehber tamlığı (metinden öğe çıkar, kayda öğe ekle)
    for ad, metin, beklenen in YASAK_BOZMA:
        n = len(yasak_metinler([("bozma K1 is_", metin)])[0])
        out.append(dict(ad="yasak: " + ad, yakalandi=(n > 0) == beklenen, hata=n))
    t0 = len(tamlik_denetle(ham)["hata"])
    ham3 = [(y, (t or "").replace("{kopru.bara}", "12 AWG").replace("{kopru_adet.bara}", "3").replace("{kopru.yildiz|bara}", "{kopru.yildiz}"))
            for y, t in ham]
    n = len(tamlik_denetle(ham3)["hata"]) - t0
    out.append(dict(ad="tamlık: anahtarlı bara köprüsü yer tutucusuz", yakalandi=n > 0, hata=n))
    T = json.load(open(KABLO_TABLO, encoding="utf-8"))
    for ad, boz in (("kayda yeni sigorta", lambda T: T["koruyucular"].__setitem__("hat-X", dict(T["koruyucular"]["hat-C"]))),
                    ("kayda yeni bara köprüsü", lambda T: T["klemens_turleri"]["bara-pabuc"]["kopruler"].__setitem__(
                        "Üçüncü bara · +", dict(adet=1, awg=12, renk="kırmızı", boy_mm=50))),
                    ("kayda yeni saplama düğümü", lambda T: T["klemens_turleri"]["bara-pabuc"]["dugumler"].__setitem__("Üçüncü bara · +", 2)),
                    ("kayda yeni zincir anahtarı", lambda T: T["anahtarlar"].__setitem__("K3-kontak", dict(ad="Röle K3 kontağı", tur="kontak"))),
                    ("kayda yeni acil stop kablosu", lambda T: T["kablolar"].append(dict(T["kablolar"][[r["kimlik"] for r in T["kablolar"]].index("A06")],
                                                                                      kimlik="A07")))):
        T2 = json.loads(json.dumps(T))
        boz(T2)
        n = len(tamlik_denetle(ham, T=T2)["hata"]) - t0
        out.append(dict(ad="tamlık: " + ad, yakalandi=n > 0, hata=n))
    return dict(temel_hata=len(temel), deneme=out, yakalanan=sum(1 for x in out if x["yakalandi"]), toplam=len(out))


def denetle(V, ek_metinler=()):
    m = gorunen_metinler(V)
    asc = ascii_kalinti(m + tablo_metinleri(V) + list(ek_metinler))
    gr = gruplama(V)
    tu = tutarlilik(V, m)
    ya, ya_ist = yasak_tara(V)
    ke = kopya_eki(V)
    el = elektrik_denetle(m)                                         # P10.7b1: elektrik iddiaları ↔ kablolar.json / pin haritası
    el += [dict(yer=x["yer"], kural="yer tutucu", ifade=x["ifade"], neden="çözülmüş metinde { } ⟦ ⟧ kaldı (bozuk yer tutucu)")
           for x in bozuk_yer_tutucu(m)]
    return dict(yasak=ya, yasak_sayi=len(ya), yasak_affedilen=ya_ist, kopya_eki=ke[:20], kopya_eki_sayi=len(ke),
                ascii_kalinti=asc, ascii_kalinti_sayi=len(asc), gruplama_yanlis=len(gr["yanlis"]) + len(gr["eksik"]), gruplama=gr,
                tutarlilik_celiski=len(tu["celiski"]) + len(tu["anmayan"]), tutarlilik=tu,
                zorunlu_eksik=len(tu["zorunlu_eksik"]),
                elektrik=el[:60], elektrik_sayi=len(el),
                metin_sayisi=dict(veri=len(m), tarayici=len(ek_metinler)),
                parca=len(V["parcalar"]), sema=len(V.get("semalar", [])),
                gecti=not asc and not gr["yanlis"] and not gr["eksik"] and not tu["celiski"] and not tu["anmayan"]
                and not tu["zorunlu_eksik"] and not ya and not ke and not el)


def kaynak_denetle():
    """FreeCAD'siz, veri üretmeden: rehber_metin.py kaynağında ASCII kalıntı, elektrik iddiaları ve zorunlu uyarılar (P10.7b1)."""
    m = kaynak_metinler()
    asc = ascii_kalinti(m + tablo_metinleri())                     # S1: panelin tablodan gösterdiği metinler de
    # P10.7b1 düzeltme turu 1: elektrik iddiaları CAD parça adları / kodları ve arayüz sabit metinlerinde de (F10h-kontrol Ü1, §2-3)
    cad = cad_ad_metinleri()
    ara = arayuz_metinleri()
    el = elektrik_denetle(m + (cad or []) + ara)
    ya, ya_ist = yasak_metinler(m + ara)
    adim = collections.defaultdict(str)
    alanlar = collections.defaultdict(str)
    for yer, t in m:
        p = yer.split()
        if p[0] == "kaynak" and p[1] in RM.ADIM:
            adim[p[1]] += "\n" + t
            alanlar[(p[1], p[2])] += "\n" + t
    zh = []
    zor = [dict(adim=k, uyari=ad) for k, d, ad in zorunlu_listesi(zh) if k in RM.ADIM and not re.search(d, adim[k])]
    zor += [dict(adim=k, uyari=ad + " (alan %s)" % alan) for k, alan, d, ad in zorunlu_alan_listesi(zh)
            if k in RM.ADIM and not re.search(d, alanlar[(k, alan)])]
    yere = dict(adim)
    yere.update({"SEMA " + s[1]: s[3] for s in RM.SEMA})
    zor += [dict(adim=x["yer"], uyari=x["uyari"] + " (" + x["neden"] + ")") for x in cumle_denetle(yere, zh)]
    zor += [dict(adim="-", uyari=e) for e in zh]
    zor_disari = [k for k, d, ad in ZORUNLU if k not in RM.ADIM]   # metni yalnız M6 tablosunda olan adım: veri denetiminde bakılır
    ham = kaynak_metinler(ham=True)
    cip = ciplak_sayilar(ham)
    cip += muaf_denetle()                                            # açık iş 9: muaf listesi sessizce büyümez
    coz = list(RM.COZUM_HATA)
    boz = bozuk_yer_tutucu(m)                                        # açık işler turu: çözülmüş metinde { } ⟦ ⟧ kalmaz
    bag = baglam_denetle(ham)                                        # anahtar ↔ bağlam
    kg = kritik_girdiler(ham)
    kr = kritik_fark(kg)                                             # onaylı kritik metin kaydı
    tm = tamlik_denetle(ham)                                         # düzeltme turu 2: kayıt → rehber tamlığı
    return dict(ascii_kalinti=asc, elektrik=el, zorunlu_eksik=zor, zorunlu_veride=sorted(set(zor_disari)), metin=len(m),
                cad_metin=None if cad is None else len(cad), arayuz_metin=len(ara), yasak=ya, yasak_affedilen=ya_ist,
                ciplak=cip, cozum_hata=coz, bozuk=boz, baglam=bag, kritik=kr, tamlik=tm,
                kritik_sayi={b: len(v) for b, v in kg.items()},
                gecti=not asc and not el and not zor and not ya and not cip and not coz and cad is not None and not boz and not bag
                and not kr and not tm["hata"])


def ozet_yaz(d):
    print("denetim: ascii kalinti %d, gruplama yanlis %d (eski kural ayni veride %d satir), kafa/hoparlor/hub celiski %d, "
          "zorunlu uyari eksik %d / %d, baglamla affedilen %d; yasak talimat %d (istisna %d), kopya eki %d; parca %d, sema %d" % (
        d["ascii_kalinti_sayi"], d["gruplama_yanlis"], d["gruplama"]["eski_kural_yanlis"], d["tutarlilik_celiski"], d["zorunlu_eksik"],
        len(d["tutarlilik"]["zorunlu"]), len(d["tutarlilik"]["affedilen"]), d["yasak_sayi"], len(d["yasak_affedilen"]),
        d["kopya_eki_sayi"], d["parca"], d["sema"]))
    for x in d["ascii_kalinti"][:60]:
        print("  ASCII %-18s %s%s" % (x["kelime"], x["ilk_yer"], " (sozlukte var)" if x["sozlukte"] else ""))
    for x in d["gruplama"]["yanlis"][:20] + d["gruplama"]["eksik"][:20]:
        print("  GRUP", x)
    for x in d["tutarlilik"]["celiski"][:20] + d["tutarlilik"]["anmayan"][:20] + d["tutarlilik"]["zorunlu_eksik"]:
        print("  TUTARLILIK", x)
    for x in d["yasak"][:20]:
        print("  YASAK", x)
    for x in d["kopya_eki"][:5]:
        print("  KOPYA EKI", x)
    print("elektrik iddiasi (kablolar.json / pin haritasi ile celisen): %d" % d.get("elektrik_sayi", 0))
    for x in d.get("elektrik", [])[:30]:
        print("  ELEKTRIK", x)


def _ana():
    # P10.7b1: --kaynak: rehber_metin.py kaynağı (FreeCAD'siz, veri üretmeden); --bozma-denemesi: elektrik bozmaları
    if "--bozma-denemesi" in sys.argv:
        b = elektrik_bozma_denemesi()
        for x in b["deneme"]:
            print("  %-45s %s" % (x["ad"], "YAKALANDI (%d)" % x["hata"] if x["yakalandi"] else "KACTI"))
        print("elektrik bozma denemesi: %d / %d yakalandi; bozulmamis kaynakta hata %d" % (b["yakalanan"], b["toplam"], b["temel_hata"]))
        sys.exit(0 if b["yakalanan"] == b["toplam"] and b["temel_hata"] == 0 else 1)
    if "--kritik-onay-yenile" in sys.argv:
        # açık işler turu: onay kaydını bilinçli olarak yenile (olağan koşu asla yazmaz); önce farkı göster
        kg = kritik_girdiler()
        fark = kritik_fark(kg)
        for f in fark:
            print("  KRITIK %s %s %s\n      eski: %s\n      yeni: %s" % (f["tur"], f["bolum"], f["yer"], f["eski"] or "-", f["yeni"] or "-"))
        _RK.yaz(kg)
        print("onay kaydı yenilendi: %s (%s); %d fark yazıldı" % (os.path.basename(_RK.ONAY_DOSYASI),
              ", ".join("%s %d" % (b, len(v)) for b, v in sorted(kg.items())), len(fark)))
        print("UYARI: bu değişiklik bağımsız kontrolden geçmeli (kayıt metnin doğru olduğunu kanıtlamaz, yalnız sessiz değişikliği önler)")
        sys.exit(0)
    if "--kaynak" in sys.argv:
        d = kaynak_denetle()
        print("kaynak denetimi: metin %d (+ CAD ad/kod %s, arayuz %d), ascii kalinti %d, elektrik iddiasi %d, zorunlu uyari eksik %d "
              "(yalniz veride bakilan adim: %s), yasak %d (istisna %d), ciplak kritik sayi %d, cozulemeyen yer tutucu %d, "
              "bozuk yer tutucu %d, anahtar-baglam %d, onayli kritik girdi farki %d (kayitta: %s)" % (
            d["metin"], "YOK (montaj-analiz.json okunamadi)" if d["cad_metin"] is None else d["cad_metin"], d["arayuz_metin"],
            len(d["ascii_kalinti"]), len(d["elektrik"]), len(d["zorunlu_eksik"]), ", ".join(d["zorunlu_veride"]) or "-",
            len(d["yasak"]), len(d["yasak_affedilen"]), len(d["ciplak"]), len(d["cozum_hata"]), len(d["bozuk"]), len(d["baglam"]),
            len(d["kritik"]), ", ".join("%s %d" % (b, n) for b, n in sorted(d["kritik_sayi"].items()))))
        for x in d["kritik"][:40]:
            print("  KRITIK %s %s %s\n      eski: %s\n      yeni: %s" % (x["tur"], x["bolum"], x["yer"], x["eski"] or "-", x["yeni"] or "-"))
        tm = d["tamlik"]
        print("tamlik (kayit -> rehber): taranan %d oge (%s), eksik %d, muaf %d; kablo kimligi rehberde %d / %d (gecmeyen, bilgi: %s)" % (
            sum(tm["tarandi"].values()), ", ".join("%s %d" % (k, n) for k, n in sorted(tm["tarandi"].items())), len(tm["hata"]),
            len(tm["muaf"]), tm["kablo_toplam"] - len(tm["kablo_yok"]), tm["kablo_toplam"], ", ".join(tm["kablo_yok"]) or "-"))
        for x in tm["hata"]:
            print("  TAMLIK", x)
        for x in d["bozuk"][:20]:
            print("  BOZUK YER TUTUCU", x)
        for x in d["baglam"][:40]:
            print("  BAGLAM", x)
        for x in d["ascii_kalinti"][:60]:
            print("  ASCII %-18s %s" % (x["kelime"], x["ilk_yer"]))
        for x in d["elektrik"][:60]:
            print("  ELEKTRIK", x)
        for x in d["zorunlu_eksik"]:
            print("  ZORUNLU", x)
        for x in d["yasak"][:30]:
            print("  YASAK", x)
        for x in d["ciplak"][:60]:
            print("  CIPLAK", x)
        for x in d["cozum_hata"]:
            print("  YER TUTUCU", x)
        sys.exit(0 if d["gecti"] else 1)
    yol = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROBOT, "rehber", "veri", "rehber-veri.json")
    d = denetle(json.load(open(yol, encoding="utf-8")))
    ozet_yaz(d)
    sys.exit(0 if d["gecti"] else 1)


if __name__ == "__main__":
    try:
        _ana()
    except _RK.KayitHatasi as e:                                   # düzeltme turu 2: traceback değil düzgün ileti
        print("HATA: %s" % e)
        sys.exit(1)
