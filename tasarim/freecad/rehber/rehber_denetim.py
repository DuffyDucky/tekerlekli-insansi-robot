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
import os, re, sys, json, collections, ast

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
    "SCL", "COM", "GLB",                                           # P10.7b2a: I2C saat hattı (B6a), röle ortak ucu (K1), app.js dosya biçimi
}
# Türkçe harfi olmayan doğru kelimeler ve teknik terimler (küçük harf). Yeni bir ASCII kelime ekrana girerse denetim "bilinmeyen"
# der: ya TR_EK'e karşılığı eklenir ya da gözden geçirilip buraya yazılır. F10f: ilk iki satır kol kablo yolu metinlerinin kelimeleri
# (32 kelime, gözden geçirildi: Türkçe harfi olmayan doğru yazımlar; "voksel" teknik terim). Üçüncü-dördüncü satır F10f düzeltme 1
# metinlerinin 19 yeni kelimesi (gözden geçirildi, hepsi Türkçe harfi olmayan doğru yazım). Beşinci satır F10f düzeltme 2 metin ve şema
# adlarının 8 yeni kelimesi (gözden geçirildi, hepsi doğru yazım). P10.7b1 üretim uyumu (S1): "turuncu … gri" satırı panelin kablo
# tablosundan gösterdiği lejant / kb kelimeleri ve "Birden" (app.js karışık sınıf notu); hepsi Türkçe harfi olmayan doğru yazım.
# P10.7b2e kısım 2: "temada koyu" beyaz kablonun yeni lejant adından ("Analog ses (beyaz; açık temada koyu çizilir)"); sonraki satır
# K1 kartlarının yer tarifleri ve B5a K64 a notunun 10 yeni kelimesi; ondan sonraki satır K1 sağ / sol kurulum testi, B6a ve F1 yer
# tariflerinin 12 yeni kelimesi ve app.js küçük görünüm balonundaki "bakana" (gözden geçirildi, hepsi Türkçe harfi olmayan doğru yazım).
ASCII_TAMAM = set("""
hepsine elin ekli kolunun dayanana pulla lehimden lehimi
artanla denenmedi ekler ekseninin ekten girdi gerilmeden hepsinden kabloyla kablonun kendisi kuruldu lopu modeldeki orada oturtma
penceresinden pimler servosunun sokmadan somunla sonraki tabana tambura tamburda tamburdan tarama tutkalla voksel yatar yolun dereceye
beri bekler demette eklendi indirme itme kablosuna kasetin kesintisiz lopuyla pencerede penceresinde penceresine servonun soluk
tamburdaki uzatmalara yay yaylar
eksik ilkesi koruyucunun saplamaya zincir
turuncu mor koruma enkoderle okunur kapatma birden besleyen klemensi liste analog beyaz gri
temada koyu
karedeki baralar dek karesinde katta olan panelin solda yazmaz zamana
okunu kurulum taraf sola saniyede gerekirse ister soldaki tekerleri bekleniyor klemensler komutunu bakana
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
pinine pinlerine pinlerini neden pininde etme makaronu kovan gerginlik giderme pimlerini bul kutbu gerilimliyken almada verme
pinlerinden tutturulu lehimlenmeden klemensinde katottur yoktur klemenslerinden birer soneki kabloyu
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
ayarlanan klemenslerini motoru yandaki notundaki bacak okunmuyorsa kablajda telin zarar dolarken inmeden beslemesi pinli uca direncin
pabucun kalmaz girmeden altta baraya pimlerinin yerlerine enkoderi trig echo klemensli saplamada saplamalardaki pedinde ucudur vishay
tvs anotlar serisi belge tipte pabucunu olursa okunan geriliminin
gerekli kalemden kopya daha tonla vurgulu notuna gizli rengi shift
eritir pensesiyle kovana lehimlenir okuma
bitip lehimin erken kaymaz gerilimini not gerilimidir gerilimiyle beklenen kez bozuk
neresi tema tekrar oynat patlat beklet yerlerini
yinele kalibrasyonunda banttan kusuru kusur bulunmazsa kayda tolerans
maddeden
modelden dokuz yerlerdir kartlara bakarak durumu sinyali
tablosudur pininin denemesine kesin
panelinin
kutbuna
ayarla trimpotun konumunu boya trimpotu tutucusu varsayar paketinde kutudan
rehberde tablosunda bakan soludur adlar
sabit testin testinin testini konusu konusudur senin
sayfada karenin listesindeki
beslenmesin diye diyodun belirlenir iletir iletmez etti pano demete beslenmesini keser mevcut devresiyle kapatabilirsin
dibindeki
""".split())
# P10.7b2g düzeltme turu 2 (F10o-kontrol Y1): son satır K2 alt adım 5 servo kablosu cümlesinin 1 yeni kelimesi ("kanal dibindeki";
# gözden geçirildi: Türkçe harfi olmayan doğru yazım).
# P10.7b2f: sondan bir önceki satır B6a uç etiketi cümlesinin ve F5 kurulum testi göndermesinin 3 yeni kelimesi (gözden geçirildi: Türkçe harfi
# olmayan doğru yazım). Kısım 2 (kayıt düzeltmeleri, K66): son satır B6a VIN diyodu cümlesi ve kontrolü, K2 alt adım 4 / 5 ve kontrol,
# E4 not_ (Efe'nin pano cevabı) metinlerinin 14 yeni kelimesi (gözden geçirildi: Türkçe harfi olmayan doğru yazım).
# P10.7b2e düzeltme turu 1 (F10m-kontrol D1): sondan bir önceki satır adım 0 sağ / sol tanım cümlesinin 5 kelimesi (gözden geçirildi:
# Türkçe harfi olmayan doğru yazım; TR sözlüğünde ASCII karşılıkları yok, gevşetme değil). D2: son satır K1 sağ / sol kurulum testinin
# ve F5 göndermesinin 6 yeni kelimesi ve N13 adım 0 ipucunun "senin"i (gözden geçirildi, aynı ölçüt).
# P10.7b2e (K52 a): son satır B5a göğüs regülatörü paragrafı / kontrolü, bara tutucusu notu (K64) ve K1 G20 cümlesinin 9 yeni
# kelimesi (gözden geçirildi: Türkçe harfi olmayan doğru yazım).
# P10.7b2d düzeltme turu 2 (F10l-kontrol-2 D1): son satır 17.1'deki G05 akü ucu cümlesinin 1 yeni kelimesi (gözden geçirildi: Türkçe
# harfi olmayan doğru yazım, "kutup" → "kutbuna").
# P10.7b2c düzeltme turu 1 (F10k-kontrol D2): son satır K2 kablo listesindeki U06 cümlesinin 1 yeni kelimesi (gözden geçirildi: Türkçe
# harfi olmayan doğru yazım).
# P10.7b2c ikinci yarı (ajan B): son satır bağlantı tablosu ve kafa içi / ses şeması notlarının 4 yeni kelimesi (gözden geçirildi:
# Türkçe harfi olmayan doğru yazım)
# P10.7b2c ön işi (F10j-kontrol-2 A5): kullanılmayan "kayar", "gerilimine", "pimine", "kalibrasyonuyla", "belirgin", "gelene" ile A1 / A2
# metniyle kullanımdan kalkan "maddesinden", "girene" çıkarıldı; sondan ikinci satır A1'in yeni kelimesi ("maddeden"). P10.7b2c: son
# satır taban gösterim şemalarının (SEMA) ve K1 / B3 kablo notlarının 7 yeni kelimesi. Gözden geçirildi: hepsi Türkçe harfi olmayan
# doğru yazım.
# P10.7b2b düzeltme turu 1 (F10j-kontrol D1): son satır F1 G07 karar ağacının 9 yeni kelimesi (gözden geçirildi: hepsi Türkçe harfi
# olmayan doğru yazım).
# P10.7b2b: sondan ikinci satır üç metin kusurunun (K1 G07 makaronu, F1 akü gerilimi) 16 yeni kelimesi; son satır rehber/index.html'in
# görünen metni ve title / aria-label öznitelikleri (ASCII kapsamına yeni girdi, A8: "Robotun neresi", "Tema (T)", "Uçuşu tekrar
# oynat", "Parçaları patlat ve beklet", "Bağlantı elemanı yerlerini işaretle"). Gözden geçirildi: hepsi Türkçe harfi olmayan doğru yazım.
# Düzeltme turu 2 (F10i-kontrol-2): son satır G07 lehim sırası, F1 aralık dışı okuma ve AU3 talimatının 7 yeni kelimesi (gözden
# geçirildi: hepsi Türkçe harfi olmayan doğru yazım).
# P10.7b2a: son üç satır K63 talimat metinlerinin (B3, B5a, B6a, K1, E3a, F1) 43 yeni kelimesi; gözden geçirildi: hepsi Türkçe harfi
# olmayan doğru yazım ("Trig" / "Echo" HC-SR04 pin adı, "Vishay" üretici adı, "tvs" kablolar.json alan adı). Son satır app.js'in görünen dizgelerinin 10 kelimesi (kapsama yeni girdi; doğru yazım, "Shift"
# klavye tuşu); "GLB" KISALTMA'da (dosya biçimi).
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
    # P10.7b2a: yön kayıttan ({yon.<tvs>}: kablolar.json tvs, Vishay veri sayfası "color band denotes cathode end"); "çizgili" → "bantlı"
    ("E3a", r"katot \(bantlı uç\) \+5 V", "TVS kutbu"),
    ("E3a", r"P6KE18A'yı kartın \+ ve − uçları arasına lehimle, katot \(bantlı uç\) \+12 V", "P6KE18A kutbu (kafa giriş kartı)"),
    # düzeltme turu 1 (F10i-kontrol Ü6): kutup ve yön desende yer tutucudan (kayıt değişirse desen de değişir; ters yazım tutmaz)
    ("B5a", r"kondansatörünü V\+ / GND barasına lehimle, yönü {yon.kondansator}", "dağıtım kartı C kondansatör yönü"),
    ("B5a", r"SV3'ü .{0,200}bağla: {kutup.SV3}", "SV3 kutbu (XL4016 C → dağıtım kartı C)"),
    ("B6a", r"her kartın iki 2200 .F kondansatörünü V\+ / GND barasına lehimle, yönü {yon.kondansator}",
     "dağıtım kartı A / B kondansatör yönü"),
    ("K1", r"SV2'yi dağıtım kartı B'nin V\+ / GND giriş klemensine \({kutup.SV1|SV2}\)", "SV1 / SV2 kutbu (XL4016 A / B → dağıtım kartı)"),
    # düzeltme turu 2 (F10i-kontrol-2 §5 G07): kılıf çıkar → makaron → sık → lehim → makaron kovanın üstüne (sıra tek desende)
    # P10.7b2b (F10i-kontrol-3 A5): makaron geçirilir ve lehim yerinden uzakta tutulur → direnç tele → bacak kovana sık + lehim →
    # soğuyunca makaron yerine (sıra tek desende; ZORUNLU_SIRA da ayrı sınar)
    ("K1", r"halka pabucun PVC kılıfını çıkar.{0,260}?makaronu G07'nin teline geçir.{0,200}?Makaronu lehim yerinden uzağa, telin geri "
           r"tarafına it ve iki lehim bitip soğuyana kadar orada tut.{0,120}?Direnci telin ucuna lehimle\. Direncin öbür bacağını pabucun "
           r"kovanına sık \(pabuç pensesiyle\), sonra kovana lehimle.{0,120}?Soğuyunca makaronu direncin ve kovanın üstüne çek",
     "G07 direnci pabuç kovanında: kılıf çıkar, makaron geçir ve uzakta tut, direnç tele, sık, lehimle, makaron (K63)"),
    # P10.7b2b (F10i-kontrol-3 A4): AU3 enerjisiz lehimlenir, kutbu dikişler sıkılmadan önce kontrol edilir
    ("K2", r"dikişleri sıkmadan önce, enerjisizken \(akü XT60 ayrık\): lehimden önce hoparlör kablosunun \(AU3\) \+ damarını iki ucunda "
           r"multimetrenin süreklilik kademesiyle bul.{0,80}?Hoparlör kablosunun \(AU3\) kafa ucunu PAM8403'ün sol kanal çıkışına "
           r"lehimle.{0,260}?Kutup kontrolü, dikişleri sıkmadan önce \(AU3\): işaretli \+ damarı {uc.AU3:+:a} ucunda, öbür damar "
           r"{uc.AU3:−:a} ucunda.{0,60}?Sonra dikişleri\s+sık",
     "K2 AU3: enerjisiz lehim, kutup kontrolü, sonra dikişler"),
    # P10.7b2b düzeltme turu 1 (F10j-kontrol D2): "kafa ucunda bağla" AU3'ü kapsamaz (kapsarsa sonraki AU3 cümlesi sırayı geri sarar)
    ("K2", r"Hoparlör kablosu \(AU3\) dışındaki dört kabloyu \(U03, H02, S10, G17\) kafa ucunda bağla",
     "K2: kafa ucunda bağla yalnız öbür dört kablo (AU3 ayrı cümlede)"),
    # düzeltme turu 1 (F10i-kontrol Ü1, Ü2, Ü3, A1, A2, A13)
    ("B6a", r"PC817 modülünün çıkış besleme ucunu \(çıkış VCC\) ESP32'nin {uc.X01:PC817_çıkış_beslemesi:b} pinine bağla \(X01\): "
            r"5 V'a bağlama", "X01: PC817 çıkış beslemesi ESP32 3V3'te, 5 V'a bağlanmaz"),
    ("B6a", r"PCA9685'in V\+ klemensine ve kanal başlıklarının V\+ pinine tel takma", "P01 / P02: PCA9685 V+ teli takılmaz"),
    ("B6a", r"3 telli hazır servo kablosu kullanırsan V\+ damarını iki ucundan kes, makaronla yalıt", "P01 / P02: 3 telli kabloda V+ kesilir"),
    ("B6a", r"V\+ teli takılırsa üç dağıtım kartının V\+'ı, yani XL4016 A, B ve C'nin çıkışları birbirine paralel girer",
     "P01 / P02: V+ telinin nedeni (dönüştürücüler paralel)"),
    ("K1", r"PCA9685'in V\+ pinine tel takma; 3 telli hazır kablo kullanırsan V\+ damarını iki ucundan kes, makaronla yalıt",
     "P03: PCA9685 V+ teli takılmaz, 3 telli kabloda V+ kesilir"),
    ("K1", r"Bağlamadan önce modülün üstündeki IN2 \+ / IN2 − yazısını oku: ters bağlanan G22'de .{0,260}ters bağlıyken enerji verme",
     "G22: kutup yazısı okunur, ters bağlıyken enerji verilmez"),
    ("K1", r"lehimden önce makaronu G07'nin teline geçir", "G07: makaron lehimden önce geçirilir"),
    ("K1", r"Gerginlik giderme: G07'yi direncin tel tarafında, ana anahtara giden G04'e kablo bağıyla tuttur", "G07: gerginlik giderme"),
    ("K1", r"lehimden önce K2'nin pimlerini bul", "K2 pim yeri 12 AWG lehiminden önce bulunur"),
    # düzeltme turu 2 (F10i-kontrol-2 §5 TVS): "sonu A" muğlaktı (…CA da A ile biter)
    ("E3a", r"sonu yalnız A \(ör\. P6KE18A\) tek yönlüdür, renkli bandı katottur; sonu CA \(ör\. P6KE18CA\) çift yönlüdür, bandı yoktur",
     "TVS: gövde baskısı (sonu yalnız A tek yönlü, sonu CA çift yönlü)"),
    ("E3a", r"CA baskılı ya da bantsız TVS'i takma \(kablajda teyit\)", "TVS: CA baskılı ya da bantsız takılmaz"),
    ("F1", r"çıkış saplamasına G04'ü \(sigorta kutusuna\) ve akü ölçüm telinin pabucunu \(G07", "G07 ana anahtarın çıkışında (K63)"),
    # düzeltme turu 2 (F10i-kontrol-2 B16): alt adım 7'deki mantar talimatı (iş metnindeki ZORUNLU_ALAN F1 is_'te)
    ("F1", r"iki acil stop ucunu mantarın NC kontağına bağla: A01'i NC girişine, A02'yi NC çıkışına",
     "F1 alt adım: mantarın iki ucu ayrı (A01 NC girişi, A02 NC çıkışı)"),
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
    # P10.7b2d-A düzeltme turu 1 (F10l-kontrol D2): "madde N" göndermeleri alt adım numarasına çevrildi (rehber_metin._demet_bol)
    ("K1", r"Bu adımda takılan köprüler: Ö4 yerindeki kısa tel köprü \(alt adım 17\.8\), acil stop düğüm kartındaki "
           r"\(A02, A04\) {kopru.A02} tel köprü \(alt adım 17\.8\), yıldız barasının saplamaları arasındaki {kopru_adet.yildiz} adet "
           r"{kopru.yildiz} köprü \(alt adım 17\.1\), anahtarlı baranın saplamaları arasındaki {kopru_adet.bara} adet {kopru.bara} köprü",
     "K1 madde 8: bu adımda takılan köprülerin listesi (iki bara)"),
    ("K1", r"Anahtarlı bara \(\+\) {saplama.bara} M5 saplama: saplamalar {kopru_adet.bara} adet {kopru_renk.bara} {kopru.bara} "
           r"köprüyle", "K1 madde 2: anahtarlı baranın köprüleri (adet, renk, kesit)"),
    ("K1", r"İki baranın köprüleri takılı", "K1 kontrol: iki baranın köprüleri ve süreklilik"),
    ("K1", r"Bunların dışında mantarın kendi uçları ve ana anahtarın uçları hiçbir zaman köprülenmez",
     "K1 köprülenmeyenler: mantar ve ana anahtar uçları"),
    ("K1", r"Ö4 karar bekliyor \(K60\)", "K1 Ö4 karar bekliyor (K60)"),
    # P10.7b2e (K52 a, 16.11): eski "karar bekliyor (K52)" desenleri yerine kararın kendisi (regülatör B5a'da panelde, G20 panel içinde)
    ("B5a", r"Göğüs ekranı regülatörü \(LM2577 \+ LM2596; K52 a\)", "B5a göğüs ekranı regülatörü güç paneline (K52 a)"),
    # P10.7b2e kısım 2 (Echo kararı 16.11.2026): K64 kapandı (a): tutucu CAD paketinde tasarlanıp basılır
    ("B5a", r"CAD paketinde tasarlanıp basılacak, satın alınmayacak \(K64 a\)", "B5a bara tutucusu CAD paketinde basılır (K64 a)"),
    ("K1", r"regülatörünün girişine \(K52 a\); G20'nin iki ucu da panelde", "K1 G20 panel içinde, regülatör B5a'da (K52 a)"),
    ("K1", r"G20'nin regülatör ucunu regülatörün giriş klemensine bağla \({kutup.G20}", "K1 G20'nin regülatör ucu ve kutbu"),
    ("K2", r"Regülatör B5a'da güç paneline takıldı \(K52 a\)", "K2 göğüs regülatörü B5a'da panelde (K52 a)"),
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
    # düzeltme turu 1 (F10i-kontrol Ü1, Ü2, Ü3, A1): süreklilik kontrolleri ve G07 ölçüm aralığı kontrol listesinde
    ("B6a", "kontrol", r"çıkış VCC ile ESP32 {uc.X01:PC817_çıkış_beslemesi:b} pini arası öter, çıkış VCC ile çevre 5 V arası ötmez",
     "B6a kontrol: X01 çıkış VCC 3V3'te, 5 V'ta değil"),
    # düzeltme turu 2 (F10i-kontrol-2 §5 P01–P03): ölçü noktası kanal başlığının V+ pini (klemens ile ray arasında koruma olabilir)
    ("B6a", "kontrol", r"PCA9685'in kanal başlığının V\+ pini ile dağıtım kartı A'nın ve B'nin V\+ barası arasında süreklilik yok",
     "B6a kontrol: PCA9685 kanal başlığı V+ ile dağıtım kartı A / B V+ arası ötmez"),
    ("K1", "kontrol", r"{uc.G22:−:a} ile yıldız barası arası öter, {uc.G22:+:b} ile yıldız barası arası ötmez", "K1 kontrol: G22 kutbu"),
    ("K1", "kontrol", r"PCA9685'in kanal başlığının V\+ pini ile dağıtım kartı C'nin V\+ barası arasında süreklilik yok",
     "K1 kontrol: PCA9685 kanal başlığı V+ ile dağıtım kartı C V+ arası ötmez (P03)"),
    ("K1", "kontrol", r"direnç, iki bacağı ve pabuç kovanı makaronla tümüyle örtülü \(açıkta bacak yok\)", "K1 kontrol: G07 direnci örtülü"),
    ("F1", "kontrol", r"bölücü oranı \({oran.aku_olcum}\) katıdır: akü {v.aku_aralik} iken bölücünün orta noktasında {v.aku_olcum} okunur",
     "F1 kontrol: G07 ölçüm aralığı (bölücü oranı, kayıttan)"),
    # düzeltme turu 2 (F10i-kontrol-2 B16): mantarın iki ucu ayrı ayrı (A01 NC girişine, A02 NC çıkışına) adımın iş metninde; alt
    # adımdaki aynı talimat ZORUNLU'da ayrı desenle (biri bozulunca öbürü kurtarmasın). Tek pabuçta iki uç mantarı köprüler.
    ("F1", "is_", r"A01'i \(F5 {a.F5} çıkışından gelen\) NC girişine, A02'yi \(acil stop düğümüne giden\) NC çıkışına",
     "F1 iş: mantarın iki ucu ayrı (A01 NC girişi, A02 NC çıkışı)"),
    # düzeltme turu 2 (F10i-kontrol-2 §5 G07): okuma aralık dışındaysa ne yapılacağı
    # P10.7b2b düzeltme turu 1 (F10j-kontrol D1): cümle ayrıldı, bağlam adı ("bölücü") cümlenin kendisinde
    ("F1", "kontrol", r"Bölücü okuması {v.aku_olcum} aralığının altında ya da üstündeyse: ana anahtarı kapat, aküyü XT60'tan ayır",
     "F1 kontrol: G07 okuması aralık dışındaysa akü ayrılır"),
    # P10.7b2b (F10i-kontrol-3 A6): akünün kendi gerilimi de okunur; bölücü okuması ona göre değerlendirilir; aralık dışı yasakları
    # P10.7b2b düzeltme turu 1 (F10j-kontrol D1): "kontağına" (akü XT60'ının cinsi kayıtta yok), iki kısa devre uyarısı da desende
    ("F1", "kontrol", r"Önce akünün kendi gerilimini oku: akü XT60'tan ayrıkken kırmızı ucu akünün XT60'ındaki \(akü tarafı\) \+ "
                      r"kontağına, siyah ucu − kontağına değdir \(bir uç iki kontağa birden değmesin, iki uç birbirine değmesin\)",
     "F1 kontrol: G07 ölçümünde akünün kendi gerilimi (akü ayrıkken, kısa devre uyarılarıyla)"),
    ("F1", "kontrol", r"beklenen bölücü okuması = akü gerilimi × bölücü oranı \({oran.aku_olcum}\); bu açıklamadır, karar ölçütü değildir",
     "F1 kontrol: beklenen = akü × oran yalnız açıklama (karar ölçütü değil)"),
    # P10.7b2b düzeltme turu 1 (F10j-kontrol D1): karar ağacı. Akü aralık dışı → bölücüye geçilmez; akü aralıkta → karar yalnız bantla;
    # bant dışı → bölücü bozuk; kusur bulunmazsa da devam yok
    ("F1", "kontrol", r"Akü gerilimi {v.aku_aralik} dışındaysa burada dur: bölücü ölçümüne geçme, ana anahtarı açma, aşama 2'ye \(F5\) "
                      r"geçme", "F1 kontrol: akü aralık dışındaysa bölücü ölçümüne geçilmez (dur)"),
    ("F1", "kontrol", r"Akü gerilimi {v.aku_aralik} içindeyse: kırmızı ucu arayüz kartındaki akü ölçüm bölücüsünün orta noktasına",
     "F1 kontrol: bölücü ölçümü yalnız akü aralıktayken"),
    ("F1", "kontrol", r"Karar yalnız banttan: okuma {v.aku_olcum} içindeyse bölücü geçer", "F1 kontrol: bölücü kararı yalnız bantla"),
    ("F1", "kontrol", r"Akü gerilimi {v.aku_aralik} içinde olduğu için bölücü bozuk", "F1 kontrol: akü aralıkta, okuma bant dışı → bölücü bozuk"),
    # P10.7b2c ön işi (F10j-kontrol-2 A4): madde sonuna kadar (öğe sonu "\n" ya da metin sonu): arkasına eklenen gevşetme de yakalanır
    ("F1", "kontrol", r"Listedeki yerlerde kusur bulunmazsa da devam etme: akü gerilimini ve bölücü okumasını kayda yaz "
                      r"\(tolerans kaynakta yok\)(?=\n|$)", "F1 kontrol: kusur bulunmazsa da devam edilmez, kayda yazılır"),
    # P10.7b2c ön işi (F10j-kontrol-2 A2): yasak tek anlamlı (yeniden ölçüm ana anahtarı açtırır; "okuma aralığa girene kadar" çelişiyordu)
    ("F1", "kontrol", r"bölücüdeki kusuru düzeltmeden ana anahtarı yeniden açma, ESP32'ye bu bölücüyle enerji verme, "
                      r"aşama 2'ye \(F5\) geçme", "F1 kontrol: aralık dışı okumada ana anahtar, ESP32 ve aşama 2 yasağı"),
    # P10.7b2c ön işi (F10j-kontrol-2 A1, A4): kilitsiz kalan üç cümle
    ("F1", "kontrol", r"Kusuru düzeltince ölçümü baştan, akünün kendi gerilimini okuduğun maddeden yinele\.",
     "F1 kontrol: kusur düzelince ölçüm akünün kendi geriliminden baştan"),
    ("F1", "kontrol", r"akü {v.aku_aralik} aralığına gelince bu maddeyi baştan yinele \(akünün şarjı bu adım için kaynakta yok, "
                      r"doğrulanmadı\)(?=\n|$)", "F1 kontrol: akü aralık dışındaysa aralığa gelince madde baştan"),
    ("F1", "kontrol", r"okuma {v.aku_olcum} içindeyse bölücü geçer; ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını "
                      r"sök(?=\n|$)", "F1 kontrol: bölücü geçerse söküm sırası (ana anahtar, akü, uçlar), bant gevşemez"),
    # P10.7b2c düzeltme turu 1 (F10k-kontrol D2, D3): U06 şemasının yanlış çizilen taban ucu ve dağıtım kartı C'nin yeri
    ("K2", "kablo", r"\"ESP32 USB\" şemasının \(U06\) taban ucu yanlış yerde, güç panelinin üstünde çizili \(şema yeniden çizilecek\): "
                    r"kablonun taban ucu elektronik katındaki ESP32 taşıyıcısında ESP32'nin USB girişine takılır(?=\n|$)",
     "K2 kablo: U06 şemasının taban ucu yanlış çizili, kablo ESP32'nin USB girişine"),
    ("K1", "kablo", r"Dağıtım kartı C \(kafa\): kart güç panelinde, XL4016 C'nin yanında; adındaki \"kafa\" beslediği pan / tilt "
                    r"servolarıdır\.", "K1 kablo: P03 tablosunda dağıtım kartı C'nin yeri (güç paneli)"),
    # P10.7b2d-A (F10l): demet alt adımlı K1 / K2'de uyarılar ana metinde ("is_ana": alt adım metni sayılmaz). Ana metin basılıda alt
    # adım kartlarından önce, ekranda her alt adımın metninin üstünde (rehber/yazdir.html, rehber/app.js)
    ("K1", "is_ana", r"Kabuk takılmadan önce burada dur\. Bağlarken akü ayrık \(XT60 açık\)\.",
     "K1 ana metin: kabuktan önce dur, akü ayrık (alt adımlardan önce)"),
    ("K2", "is_ana", r"Kabuktan önce dur\. Enerjisiz çalış: akü XT60 ayrık, F3 \(kafa\) takılı değil; kafa uçları enerjisiz bağlanır\.",
     "K2 ana metin: kabuktan önce dur, enerjisiz, F3 takılı değil (alt adımlardan önce)"),
]
# P10.7b2b (F10i-kontrol-3 A4, A5, A6): sıra. (adım, alan, önce, sonra, ad): "önce" alanda geçmeli ve "sonra"nın her geçişi "önce"nin
# ilk geçişinden sonra gelmeli (cümleler kalıp yerinde dururken sırası bozulursa yakalanır; tek desenli ZORUNLU bunu tutmaz:
# "sonra dikişleri sık" AU3'ten önceye eklenince desen yine tutar).
# P10.7b2b düzeltme turu 1 (F10j-kontrol D2, açık iş): "sonra" deseni "dikişlerini sık", "dikişleri sıkıp" biçimlerini de görür;
# olumsuz / koşul biçimleri ("sıkmadan", "sıkılmadı", "sıkılmadan") sıkma talimatı sayılmaz
# P10.7b2c ön işi (F10j-kontrol-2 A4): araya bir kelime ("dikiş vidalarını sık", "dikişleri iyice sık") ve büyük harf ("DİKİŞLERİ SIK")
_DIKIS_SIK = r"[dD][iİ][kK][iİ][şŞ]\w*\s+(?:\w+\s+)?[sS][ıI][kK](?!madan|ılmad|MADAN|ILMAD)\w*"
# P10.7b2c ön işi (A4): "önce" None ise satır yasaktır: "sonra" deseni alanda hiç geçmemeli (K2: dört kablodan sonra AU3'ü yeniden
# kafa ucunda bağlatan cümle; dört kablo cümlesinin kendisi "dışındaki dört kabloyu" ile ayrılır)
ZORUNLU_SIRA = [
    ("K2", "is_", None, r"\bAU3\b(?!\) dışındaki dört kabloyu)[^.\n]{0,60}?\bkafa ucunda bağla",
     "K2 AU3: dört kablodan sonra AU3'ü kafa ucunda bağlatan cümle yok"),
    ("K2", "is_", r"Hoparlör kablosunun \(AU3\) kafa ucunu PAM8403'ün sol kanal çıkışına lehimle", _DIKIS_SIK,
     "K2 AU3: dikişler AU3'ün lehiminden sonra sıkılır"),
    ("K2", "is_", r"Kutup kontrolü, dikişleri sıkmadan önce \(AU3\)", _DIKIS_SIK,
     "K2 AU3: dikişler kutup kontrolünden sonra sıkılır"),
    # P10.7b2b düzeltme turu 1 (F10j-kontrol D1): akü aralık dışı kapısı bölücü ölçümünden (aküyü takıp ana anahtarı açmaktan) önce
    ("F1", "kontrol", r"Akü gerilimi {v.aku_aralik} dışındaysa burada dur", r"aküyü XT60'tan tak, sonra ana anahtarı aç: okunan gerilim akü geriliminin",
     "F1 G07: akü aralık dışı kapısı bölücü ölçümünden önce"),
    ("K1", "is_", r"Makaronu lehim yerinden uzağa, telin geri tarafına it", r"Direnci telin ucuna lehimle|sonra kovana lehimle",
     "K1 G07: makaron lehimlerden önce lehim yerinden uzakta"),
    ("K1", "is_", r"lehimden önce makaronu G07'nin teline geçir", r"Direnci telin ucuna lehimle|sonra kovana lehimle",
     "K1 G07: makaron lehimlerden önce tele geçirilir"),
    ("F1", "kontrol", r"Önce akünün kendi gerilimini oku", r"aküyü XT60'tan tak, sonra ana anahtarı aç: okunan gerilim akü geriliminin",
     "F1 G07: akünün kendi gerilimi akü takılmadan önce okunur"),
    # P10.7b2e (K52 a; T7 B): regülatör panele takılmadan, ekran bağlı değilken 12 V'a ayarlanır
    ("B5a", "is_", r"tezgâhta çıkışını multimetreyle 12 V'a ayarla", r"kartı güç paneline\s+tak",
     "B5a göğüs regülatörü panele takılmadan önce 12 V'a ayarlanır"),
]


def zorunlu_sira_listesi(hatalar=None):
    h = hatalar if hatalar is not None else []
    return [(k, alan, None if o is None else (_yt_coz(o, h) or r"(?!x)x"), _yt_coz(s, h) or r"(?!x)x", ad)
            for k, alan, o, s, ad in ZORUNLU_SIRA]


def sira_denetle(alanlar, hatalar=None):
    """alanlar: {(adım, alan): metin}. Eksik / sırası bozuk ZORUNLU_SIRA maddeleri: [dict(adim, uyari)]."""
    out = []
    for k, alan, o, s, ad in zorunlu_sira_listesi(hatalar):
        if k not in RM.ADIM:
            continue
        t = alanlar.get((k, alan), "")
        if o is None:                                               # P10.7b2c: yasak satır
            if re.search(s, t):
                out.append(dict(adim=k, uyari=ad + " (alan %s: yasak biçim var)" % alan))
            continue
        m = re.search(o, t)
        if not m:
            out.append(dict(adim=k, uyari=ad + " (alan %s: önceki öğe yok)" % alan))
        elif any(x.start() < m.end() for x in re.finditer(s, t)):
            out.append(dict(adim=k, uyari=ad + " (alan %s: sıra bozuk)" % alan))
    return out
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
    # P10.7b2f kısım 2 (K66, 16.11): VIN'e seri ikinci 1N5819'un yönü B6a'da (X01)
    ("B6a", r"VIN'e seri 1N5819:", r"anot çevre 5 V tarafında, katot ESP32 VIN tarafında", "B6a is_: VIN'e seri 1N5819 yönü (K66)"),
    # düzeltme turu 1 (F10n-kontrol N8): kontrol maddesindeki ölçüm yönü de zorunlu (silinir / ters çevrilirse yalnız onay kaydı görüyordu)
    ("B6a", r"VIN'e seri 1N5819'un yönü:", r"çevre 5 V → ESP32 VIN yönünde iletir, ters yönde iletmez \(bantlı uç, katot, VIN tarafında\)",
     "B6a kontrol: VIN'e seri 1N5819'un ölçülen yönü (K66)"),
    ("F5", r"{gpio.ROLE_K2_ONSARJ} = 1 \(röle K2\)", r"en az {ms.onsarj} bekle", "F5 E9: K2'den sonra en az bekleme"),
    ("F5", r"{gpio.ROLE_K1} = 1 \(röle K1\)", r"{ms.k1_sonra} sonra {gpio.ROLE_K2_ONSARJ} = 0", "F5 E9: K1'den sonra K2 bırakılır"),
    # açık işler turu (F10h-kontrol-2 B28): göğüs regülatörünün yeri şemada da açık karar
    # P10.7b2e (K52 a, 16.11): karar şemada da (regülatör güç panelinde, B5a)
    ("SEMA 12 V", r"LM2577 \+ LM2596", r"regülatör güç panelinde, B5a, K52 a", "SEMA 12 V: göğüs regülatörü güç panelinde (K52 a)"),
    # düzeltme turu 1 (F10i-kontrol A7, Ü1): iki uçlu kablonun iki ucu da aynı cümlede
    ("K1", r"A06'nın \+ ucunu", r"IN1 \+ klemensine bağla; − ucunu modülün IN1 − klemensinden arayüz kartının GND pedine lehimle",
     "K1 is_: A06'nın iki ucu (+ IN1 +, − IN1 − → GND)"),
    ("K1", r"G22'nin kutbu", r"\+ damarını \(hat sigortasından gelen\) arayüz kartındaki PC817 modülünün {uc.G22:+:b} klemensine, − damarını "
                          r"modülün {uc.G22:−:a} klemensinden yıldız barasına bağla", "K1 is_: G22'nin iki ucu ve kutbu"),
    # düzeltme turu 2 (F10i-kontrol-2 B18): A06'nın + ucu kayıttaki düğümde (kablolar.json A06 + damarının a ucu); başka düğümde
    # (ör. F5 girişi) PC817 #1 mantarı algılamaz, mantar bırakılınca röle komutsuz yeniden çekebilir
    ("K1", r"A06'nın \+ ucunu", r"A06'nın \+ ucunu {parca.A06:+:a} noktasına, yani acil stop düğüm kartında bir klemensin kuyruğuna "
                              r"\(kart altı\) lehimle", "K1 is_: A06'nın + ucu kayıttaki düğümde (acil stop algısı)"),
    # düzeltme turu 2 (F10i-kontrol-2 B23): K2 pim okuması kayıttaki kontak uçlarından (bobin boşta giriş ↔ boş uç öter, giriş ↔
    # çıkış ötmez); ters okuma G10'u yanlış pime götürür (ön şarj baypas edilir ya da hiç kapanmaz)
    ("K1", r"lehimden önce K2'nin pimlerini bul", r"\(bobin boşta\) {kontak.K2:giris} ile {kontak.K2:bos} arası öter, "
                                                  r"{kontak.K2:giris} ile {kontak.K2:cikis} arası ötmez",
     "K1 is_: K2 pim okuması kayıttaki kontak uçlarıyla (COM ↔ NC öter, COM ↔ NO ötmez)"),
]
_CUMLE_BOL = r"(?<=[.!?])\s+|\n"
_CUMLE_GENIS = r"(?<=[!?])\s+|(?<=\D\.)\s+|\n"                      # ; ve sıra sayısından ("6. yuva") sonra bölmez
# P10.7b2b (F10i-kontrol-3 A7): kısaltmadan ("ör.", "vb.", "bkz.") sonra da bölmez (TVS cümlesi onay kaydında üç parçaya ayrılıyordu)
_KISALTMA_ONU = r"(?<!\b[öÖ]r\.)(?<!\b[vV]b\.)(?<!\b[bB]kz\.)"
_CUMLE_GENIS = r"(?<=[!?])\s+|(?<=\D\.)" + _KISALTMA_ONU + r"\s+|\n"


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
    # P10.7b2f (F10m-kare-inceleme § 4.2): 31.4'ün karesindeki yedek kart
    "Karede PAM8403'ün yanındaki ikinci kart yedek USB ses kartıdır: takılmaz (önceki alt adım).",
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
# P10.7b2a (F10h-kontrol-4 §3.5): çoğul ad muafiyeti üç gerçek talimatı kaçırıyordu ("mantarın iki ucunu kısa bir telle köprüler",
# "ana anahtarın iki ucunu baradaki köprülere bağla", "ana anahtarın uçlarına köprüler takılır"; daraltmadan önce de kaçan "mantarın iki
# ucu arasına bir köprü takılır"). Artık köprü sözcüğünün her biçimi (ad, çoğul, fiil) aynı yan cümlede (virgül, iki nokta, cümle sonu
# kesmeden) bir anahtarlama / koruma nesnesiyle (_KOPRU_NESNE_AD) geçerse bulgu; nesnesiz çoğul ad ("Bu adımda takılan köprüler")
# affedilir. Fiil biçimi (köprüle-, köprülen-) nesnesiz de bulgu (eski kural).
_KOPRU_NESNE_AD = (r"\b(?:mantar\w*|acil\s+stop\w*|NC|ana\s+anahtar\w*|sigorta\w*|röle\w*|kontak\w*|"
                   r"(?:artı|eksi)(?:sı|si|sını|sini|yı|yi|ya|ye|nın|nin|ları|leri|lar|ler)?)(?![\w])")
_YAN_PENCERE = r"[^.;!?\n,:→()]{0,60}?"                          # yan cümle: virgül, iki nokta, ok ve parantez de keser
_KOPRU_SOZ = r"\bköprü\w*(?!\w)(?!\s+(?:yoksa|yok|değil)\b)"         # "köprü yoksa röle çekmez" (Ö4 açıklaması) talimat değil
YASAK = [
    # düzeltme turu 2: çoğul ad "köprüler / köprüleri / köprülerin …" fiil değil (K1 madde 8 "Bu adımda takılan köprüler")
    ("köprüleme talimatı", r"\bköprüle(?!r(?:i|in|e|de|den|le)?\b)\w*",r"köprüle(?:n)?me(?:z|di|meli|yin|yiniz|den)?|köprülenemez"),
    ("köprüleme talimatı (nesneyle)", _KOPRU_NESNE_AD + _YAN_PENCERE + _KOPRU_SOZ + "|" + _KOPRU_SOZ + _YAN_PENCERE + _KOPRU_NESNE_AD,
     r"köprüle(?:n)?me(?:z|di|meli|yin|yiniz|den)?|köprülenemez"),
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
    # düzeltme turu 1 (F10i-kontrol Ü3): PCA9685 V+ rayına tel (XL4016 A / B / C çıkışları paralel olur; elektrik.md:226)
    ("PCA9685 V+ bağlama", r"\bPCA9685\S*\s+V\+\s*(?:klemens|pin|uc|ray)\w*[^.;!?\n]{0,60}?\b" + _FIIL, _FIIL_OLUMSUZ),
    # düzeltme turu 1 (F10i-kontrol Ü2): PC817 çıkış beslemesi 5 V'a (ESP32 girişleri en çok 3,6 V; pin haritası D3)
    ("PC817 çıkış beslemesi 5 V", r"\b(?:PC817|çıkış\s+(?:VCC|besleme))\S*[^.;!?\n]{0,120}?\b5\s*V['’](?:a|ya|e|ye)\s+" + _FIIL, _FIIL_OLUMSUZ),
    # düzeltme turu 1 (F10i-kontrol Ü5): ana hat K1'in dinlenmede kapalı ucuna (87a) ya da K2'nin NC'sine (acil stopta bara enerjili kalır)
    ("K1 87a ucuna bağlama", r"\b87a(?:['’]\w+)?\b(?!\s*\)?\s*boş)[^.;!?\n]{0,60}?\b" + _FIIL, _FIIL_OLUMSUZ),
    ("ana hat NC ucuna", r"\bG(?:08|09|10|11)\b(?:['’]\w+)?[^.;!?\n]{0,80}?\bNC\b(?:['’]\w+)?(?!\s*\)?\s*boş)[^.;!?\n]{0,30}?\b" + _FIIL,
     _FIIL_OLUMSUZ),
    # düzeltme turu 1 (F10i-kontrol A5): mantarın / ana anahtarın iki ucu aynı vidada (kontak kısa devre, köprüleme)
    # düzeltme turu 2 (F10i-kontrol-2 B16): "aynı pabuca" ("pabuç\w*" ç ile "pabuca"yı tutmuyordu), "tek / ortak pabuç"
    # P10.7b2b (F10i-kontrol-3 A1): "tek kontak vidası" biçimi de (kontak yalnız A01 / A02 deseninde vardı)
    ("mantar / ana anahtar uçları aynı vidada",
     r"\b(?:mantar\w*|ana\s+anahtar\w*)(?:\s+\w+){0,3}?\s+(?:uç(?:lar|ları)\w*|iki\s+uc\w*|giriş\w*\s+ve\s+çıkış\w*)[^.;!?\n]{0,40}?"
     r"\b(?:aynı|tek|ortak)\s+(?:vida|klemens|saplama|pabu[çc]|kontak)\w*[^.;!?\n]{0,30}?\b" + _FIIL +
     r"|\b(?:aynı|tek|ortak)\s+(?:vida|klemens|saplama|pabu[çc]|kontak)\w*[^.;!?\n]{0,30}?\b(?:mantar\w*|ana\s+anahtar\w*)(?:\s+\w+){0,3}?\s+"
     r"(?:uç(?:lar|ları)\w*|iki\s+uc\w*|giriş\w*\s+ve\s+çıkış\w*)[^.;!?\n]{0,30}?\b" + _FIIL, _FIIL_OLUMSUZ),
    # düzeltme turu 2 (F10i-kontrol-2 B16): mantarın iki teli (A01, A02) tek pabuçta / vidada / klemenste: mantar köprülenir
    ("acil stop telleri tek uçta",
     r"\bA0[12]\b[^.;!?\n]{0,40}?\bA0[12]\b[^.;!?\n]{0,30}?\b(?:aynı|tek|ortak|bir)\s+(?:vida|klemens|saplama|pabu[çc]|uç|uca|kontak)"
     r"\w*[^.;!?\n]{0,30}?\b" + _FIIL, _FIIL_OLUMSUZ),
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
        # P10.7b2d düzeltme turu 2 (üretim çıkış 2, F10l-gunluk § 10.3): "is_ana" kaynak tarafında türetilen alan adı (_alan_anahtarlari);
        # veride demet alt adımlı adımın ana metni adımın kendi "is_" alanıdır (alt adım metinleri sira_grup[..]["is_"]'te).
        t = A.get(k, {}).get("is_" if alan == "is_ana" else alan)
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
#    kapanmış kararlar (K1, K10, K11, K14; P10.7b2e: K52) "karar bekliyor" değil, "varsayım, K10" değil, "K11 b" dalı yok; ön şarj beklemesi "en az
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
            # düzeltme turu 1 (M21, M22, M28): açık kararlar (K60, K61; P10.7b2e: K52 kapandı, K64 açıldı; kısım 2: K64 kapandı, a)
            # yalnız "karar bekliyor / bağlı" cümlesinde; Ö4 köprüsüz kalmaz
            for t in re.finditer(r"\b(K60|K61)\b", c):
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
                k = re.search(r"\bK(1|10|11|14|52|64|65)\b(?! a)", p)        # P10.7b2e: K52 kapandı (a, 16.11); kısım 2: K64 (a); düzeltme turu 1 (N7): K65
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
    # P10.7b2e düzeltme turu 1 (F10m-kontrol D1): adım 0 (HAZIRLIK) da taranır; eskiden yalnız ADIM dolaşıldığı için adım 0'daki
    # sağ / sol cümlesinin ASCII kalıntısı ancak üretim sonundaki veri denetiminde görünüyordu. HAZIRLIK yer tutucu taşımaz (ham = çözülmüş).
    H = getattr(R, "HAZIRLIK", None)
    for kod, a in ([("0", H)] if isinstance(H, dict) else []) + list(ADIM.items()):
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


# P10.7b2a (F10h-kontrol-4 K9 / V4): ASCII sınaması app.js / yazdir.html sabit metinlerini ve kol şemalarının lejant alanını görmüyordu.
# Kod sözcüklerini (sınıf adı, öznitelik, değişken) ayıklamanın temiz yolu: JS dizgelerini belirteçle ayır (yorum ve düzenli ifade
# sabiti atlanır, şablon dizgesinde ${…} boşluk), HTML etiketini / özniteliğini, dosya yolunu ve &…; varlığını sil; kalan dizgede boşluk
# yoksa ya da # . [ ile başlıyorsa (seçici) atla; kullanıcıya görünen metin sayılan dizge: Türkçe harf taşıyan ya da en az iki sözcüğünden
# biri Türkçe sözlükte (ASCII_TAMAM / TR) olan. HTML'de etiket dışı metin (yorum, script ve style dışında) da girer. Kol lejantı:
# rehber_kol_kablo.py'nin LEJANT sözlüğü ve lejant= dizgeleri (ast ile; FreeCAD istemez). Bilinen sınır: hiç Türkçe harfi ve hiç
# bilinen Türkçe sözcüğü olmayan dizge ("parca secili") görünen metin sayılmaz; sınıf adı / seçici / olay adı alan çağrının dizgesi
# (_KOD_DIZGE_ONU) de taranmaz.
ARAYUZ_GORUNEN = [os.path.join(ROBOT, "rehber", "app.js"), os.path.join(ROBOT, "rehber", "yazdir.html"),
                  os.path.join(ROBOT, "rehber", "index.html")]          # P10.7b2b (A8): rehberin giriş sayfası da
KOL_KABLO = os.path.join(HERE, "rehber_kol_kablo.py")


def js_dizgeler(s):
    """JS kaynağındaki dize sabitleri: [(satır, metin, önceki 40 karakter)]. Yorumu ve düzenli ifade sabitini atlar; şablon dizgesinde
    ${…} boşluk olur."""
    out, i, n, onceki = [], 0, len(s), ""
    while i < n:
        c = s[i]
        if s.startswith("//", i):
            j = s.find("\n", i)
            i = n if j < 0 else j
            continue
        if s.startswith("/*", i):
            j = s.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c in "\"'`":
            j, buf, bas = i + 1, [], i
            while j < n:
                d = s[j]
                if d == "\\" and j + 1 < n:
                    buf.append(s[j + 1])
                    j += 2
                    continue
                if c == "`" and s.startswith("${", j):
                    k, derin = j + 2, 1
                    while k < n and derin:
                        derin += {"{": 1, "}": -1}.get(s[k], 0)
                        k += 1
                    buf.append(" ")
                    j = k
                    continue
                if d == c or (d == "\n" and c != "`"):
                    break
                buf.append(d)
                j += 1
            out.append((s.count("\n", 0, bas) + 1, "".join(buf), s[max(0, bas - 40):bas]))
            i, onceki = j + 1, "x"
            continue
        if c == "/" and onceki in ("", "(", ",", "=", ":", "[", "!", "&", "|", "?", "{", "}", ";", "+", "-", "return"):
            j, sinif = i + 1, False                                # düzenli ifade sabiti
            while j < n and s[j] != "\n":
                if s[j] == "\\":
                    j += 2
                    continue
                if s[j] == "[":
                    sinif = True
                elif s[j] == "]":
                    sinif = False
                elif s[j] == "/" and not sinif:
                    break
                j += 1
            i, onceki = j + 1, "x"
            continue
        if c.isspace():
            i += 1
            continue
        m = re.match(r"[A-Za-z_$][\w$]*", s[i:i + 40])
        if m:
            onceki = "return" if m.group(0) in ("return", "typeof", "case") else "x"
            i += len(m.group(0))
            continue
        onceki = c if c in "(,=:[!&|?{};+-" else "x"
        i += 1
    return out


# Kod dizgesi: sınıf adı, seçici, kimlik, öznitelik adı ve olay adı alan çağrıların / atamaların dizgesi (görünmez)
_KOD_DIZGE_ONU = (r"(?:className\s*\+?=|classList\.\w+\(|querySelector(?:All)?\(|getElementById\(|closest\(|matches\(|"
                  r"(?:set|get|has|remove)Attribute\(|addEventListener\(|createElement\(|(?<![\w.])(?:q|qa|\$)\()\s*$")


def _gorunen_dizge(m):
    """Dizgeden görünmeyen parçaları sil: HTML etiketi / özniteliği (parçalı dizgede de), dosya yolu, &…; varlığı."""
    m = re.sub(r"<[^<>]*>", " ", m)
    m = re.sub(r"[\w-]+=\"[^\"]*\"?|[\w-]+='[^']*'?", " ", m)
    m = re.sub(r"^[\w\s\"'=-]*>|<\w[^>]*$", " ", m)
    m = re.sub(r"&\w+;|\S*[/\\]\S*|\b[\w-]+\.(?:js|json|png|html|py|glb|css|md)\b", " ", m)
    return m.strip()


def _gorunen_mu(m):
    if not re.search(r"\s", m) or re.match(r"^[#.\[]", m):
        return False
    if re.search(r"[çğıöşüâîûÇĞİÖŞÜÂÎÛ]", m):
        return True
    S = _sozluk_ascii()
    w = [x.lower() for x in re.findall(r"[A-Za-z]{3,}", m)]
    return len(w) >= 2 and any(x in ASCII_TAMAM or x in S for x in w)


def gorunen_dizgeler(ad, s):
    """Bir app.js / yazdir.html kaynağının kullanıcıya görünen dizgeleri: [(yer, metin)]."""
    if ad.endswith(".html"):
        # satır numarası korunsun: script dışı yalnız satır sonlarına iner
        js = re.sub(r"(?s)^.*?<script[^>]*>|</script>.*?(?:<script[^>]*>|$)", lambda t: "\n" * t.group(0).count("\n"), s)
        d = js_dizgeler(js)
        govde = re.sub(r"(?s)<!--.*?-->|<script[^>]*>.*?</script>|<style[^>]*>.*?</style>", lambda t: "\n" * t.group(0).count("\n"), s)
        d += [(govde.count("\n", 0, t.start()) + 1, t.group(1), "") for t in re.finditer(r">([^<>]+)<", govde)]
    else:
        d = js_dizgeler(s)
    out = [("%s satır %d" % (ad, l), g) for l, m, on in d if not re.search(_KOD_DIZGE_ONU, on)
           for g in [_gorunen_dizge(m)] if _gorunen_mu(g)]
    # P10.7b2a bağımsız kontrolü A8 (P10.7b2b): (1) görünen öznitelik değerleri (title / aria-label / placeholder / alt), tek sözcük de
    # olsa; (2) görünen bir özelliğe atanan tek sözcüklü dizge ("Onceki"). Karşılaştırma / sınıf adı gibi kod dizgesi sayılmaz.
    goz = govde if ad.endswith(".html") else ""
    for l, m, on in d + [(goz.count("\n", 0, t.start()) + 1, t.group(0), "") for t in re.finditer(r"<[^<>]+>", goz)]:
        for t in re.finditer(_GORUNEN_OZNITELIK, m):
            v = (t.group(1) if t.group(1) is not None else t.group(2) or "").strip()
            if re.search(r"[A-Za-zçğıöşüÇĞİÖŞÜ]{3,}", v) and "${" not in v:
                out.append(("%s satır %d öznitelik" % (ad, l), v))
    for l, m, on in d:
        g = _gorunen_dizge(m)
        if re.search(_GORUNEN_ATAMA, on) and not _gorunen_mu(g) and re.search(r"[A-Za-zçğıöşüÇĞİÖŞÜ]{3,}", g) \
                and not re.match(r"^[#.\[]", g):
            out.append(("%s satır %d görünen atama" % (ad, l), g))
    return out


# A8: görünen öznitelik (değer tırnak içinde; parçalı dizgede kapanış tırnağı olmayabilir) ve görünen özelliğe atama (aynı deyimde:
# "x.textContent = a ? "Önceki" : …"; karşılaştırma işleci içeren deyim sayılmaz: "x.title = k === "ust" ? …" ifadesinde "ust" kod)
_GORUNEN_OZNITELIK = r"(?<![\w-])(?:title|aria-label|placeholder|alt)\s*=\s*(?:\"([^\"]*)\"?|'([^']*)'?)"
_GORUNEN_ATAMA = (r"(?:\.(?:textContent|innerText|innerHTML|title|placeholder|ariaLabel|alt)\s*\+?=|"
                  r"setAttribute\(\s*[\"'](?:title|aria-label|placeholder|alt)[\"']\s*,)(?:(?!===|!==|==|!=|[;\n]).)*$")


def kol_lejantlari(kaynak):
    """rehber_kol_kablo.py kaynağındaki lejant dizgeleri (LEJANT sözlüğü, lejant= argümanları): [(yer, metin)]."""
    out = []
    for n in ast.walk(ast.parse(kaynak)):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "LEJANT" for t in n.targets) \
                and isinstance(n.value, ast.Call):
            out += [("rehber_kol_kablo LEJANT %s" % k.arg, k.value.value) for k in n.value.keywords
                    if isinstance(k.value, ast.Constant) and isinstance(k.value.value, str)]
        elif isinstance(n, ast.keyword) and n.arg == "lejant":
            v = n.value.left if isinstance(n.value, ast.BinOp) else n.value
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                out.append(("rehber_kol_kablo satır %d lejant" % n.value.lineno, v.value))
    return out


def arayuz_gorunen_metinler(dosyalar=ARAYUZ_GORUNEN, kol=KOL_KABLO):
    """ASCII sınaması için kullanıcıya görünen arayüz metinleri ve kol lejantları: [(yer, metin)]."""
    out = []
    for yol in dosyalar:
        if os.path.exists(yol):
            out += gorunen_dizgeler(os.path.basename(yol), open(yol, encoding="utf-8").read())
    if os.path.exists(kol):
        out += kol_lejantlari(open(kol, encoding="utf-8").read())
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
_DIRENC_BAGLAM = r"bc337|sürücü|taban|\bseri\b|ön şarj|akü"          # düzeltme turu 1 (F10i-kontrol A4): akü ölçüm direnci
# düzeltme turu 1 (F10i-kontrol A4): akü ölçümü bağlamında gerilim (F1 G07 ölçümü; değerler {oran.…} / {v.…} yer tutucusundan)
# P10.7b2b (F10i-kontrol-3 A2): cümle başındaki "Okuma 1,95–2,20 V aralığının altında …" bağlamı ("okuma") sayının önünde ama
# "akü ölçüm" / "bölücü" yok; "okuma" da bağlam. "aralığ" ve "akü gerilimi" bağlam değil: multimetre kademesi ("20 V aralığı"),
# F1'deki "akü en çok 14,6 V" ve "akü gerilimi (12,8–14,4 V)" bugün çıplak; yer tutucuya almak R9'un işi (paket dışı, F10j-gunluk R6)
_GERILIM_BAGLAM = r"akü ölçüm|bölücü oran|bölücünün orta|bölücüsünün orta|\bokuma\b"
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
    ("gerilim (akü ölçümü)", r"(?<![\w{.,])\d+(?:[.,]\d+)?(?: ?[–-] ?\d+(?:[.,]\d+)?)? ?m?v\b", _GERILIM_BAGLAM),
]
# Yük bağlamı muafiyeti (açık iş 5): yalnız aynı yan cümlede yük / çeker / tüketim / varsayım sözcüğü olan VE aynı yan cümlede sigorta
# bağlamı sözcüğü (sigorta, F<n>, koruma, bıçak, mini, standart) olmayan sayı. "sürekli", "anma", "ölç", "sınır" muafiyet değil.
# Düzeltme turu 2 (F10i-kontrol-2 A4 / R5): bağlam sözcüğü sayıdan önceki CIPLAK_PENCERE karakterde aranır (cümle içinde). 40 karakter
# K1'deki "… akü ölçüm bölücüsünün orta noktası arasını ölç: 100 kΩ'a yakın okunur" cümlesinde "akü"yü görmüyordu (≈ 60 karakter önde).
# Genişleme direnç ve akü ölçümü gerilimi kurallarında; öbürleri 40'ta kalır (süre kuralı 120'de F5 notundaki dolma hesabını
# "0,2–0,5 s", ön şarj değeri değil, "Bekleme" sözcüğünden tutuyordu).
CIPLAK_PENCERE = {"direnç": 120, "direnç (sözle)": 120, "gerilim (akü ölçümü)": 120}
CIPLAK_PENCERE_VARSAYILAN = 40
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
                    p = CIPLAK_PENCERE.get(tur, CIPLAK_PENCERE_VARSAYILAN)
                    on, ar = k[max(0, t.start() - p):t.start()], k[t.end():t.end() + 20]
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
    # P10.7b2c ikinci yarı (ajan B): I2C_SDA / I2C_SCL muaftan çıktı; B6a'daki I01 bağlantı tablosu GPIO numaralarını kayıttan yazar
    # (eski: "I2C_SDA|I2C_SCL|UART0_TX|UART0_RX", "veri yolu (I2C, CP2102 üzerinden USB): …")
    ("GPIO rolü", r"UART0_TX|UART0_RX", "veri yolu (CP2102 üzerinden USB): ESP32 kartının sabit ucu; rehber pin "
     "numarası yazmaz (uçlar kablolar.md'de)"),
    ("GPIO rolü", r"DURUM_LED", "kart üstü LED, dışarı bağlanmaz (pin haritası)"),
    ("anahtar", r"esp32-3v3", "ESP32 kartının kendi regülatörü: montajda takılan ya da bağlanan ayrı parça değil"),
]


# P10.7b2a (K63, F10h-kontrol-4 §5): "rehberde anılıyor" yetmez. Ölçüt TALİMAT MADDESİ: adımın iş metni (is_) ve alt adımların
# iş metni; teslim notu, kontrol / kablo / not listesi, şema ve KABLO_AD sayılmaz. Kablo: kimliği açıkça (aralık "G01–G04"
# sayılmaz) ve aynı cümlede bir bağlama işaretiyle (TALIMAT_FIIL: ok, bağla, tak, lehimle, vidala, gider / gelir …) geçmeli.
# Koruyucu: sigorta {a.<k>}, direnç {ohm.<TAMLIK_DIRENC[k]>} talimatta; cihazın kendi koruması (BMS, çevirici, sürücü) korunan
# kablolarının hepsi talimattaysa geçer. Köprü ({kopru.<b>}, {kopru_adet.<b>}), saplama ({saplama.<b>}, yıldız {saplama.<k>},
# anahtarlı bara {bsaplama.<k>}), TVS ve kondansatör yönü ({yon.<k>}), kontak uçları ({kontak.K1|K2}), koruyucu yeri
# ({yer.<k>}) de talimatta. Bilinçli dışarıda bırakılan kablo TAMLIK_MUAF'ta (tür "kablo"; onay kaydına dahil).
# Düzeltme turu 1 (F10i-kontrol Ü4): eski kalıp ("→", tak\w*, bağla\w*, gider, gelir …) ileri tarihli ve olumsuz cümleleri de talimat
# sayıyordu ("N01, N02 K2'de takılır" geçiyordu). Artık: (1) cümlede EMİR KİPİNDE bir bağlama fiili (TALIMAT_FIIL: tam sözcük "bağla",
# "tak", "lehimle" …; "takılır", "takma", "bağlanacak" değil) olmalı; (2) kimliğin kendi yan cümlesinde (paranteze girmeden virgül,
# noktalı virgül, iki nokta ile bölünür) emir dışı bir fiil biçimi (TALIMAT_ERTELE: edilgen / geniş zaman / gelecek / olumsuz:
# "takılır", "bağlanır", "takma", "bağlama", "gider", "takılacak" …) varsa o kimlik sayılmaz; (3) kablo, kaydının rehber alanında
# "bugün" yazan adımlardan birinin talimatında geçmeli (kayıtta "bugün" adımı yoksa herhangi bir adım).
TALIMAT_FIIL = (r"(?<!\w)(?:bağla|tak|lehimle|vidala|geçir|sık|bağlayın|takın|lehimleyin|vidalayın|geçirin|sıkın)(?!\w)")
TALIMAT_ERTELE = (r"(?<!\w)(?!(?:bağla|tak|lehimle|vidala|geçir|sık|bağlayın|takın|lehimleyin|vidalayın|geçirin|sıkın)(?!\w))"
                  r"(?!bağlantı)(?:bağla|tak|lehimle|vidala|geçir)\w+|(?<!\w)(?:gider|gelir|iner|girer|çıkar|gidecek|gelecek)(?!\w)")
# Düzeltme turu 2 (F10i-kontrol-2 §3): ok kuralı yalnız iki ucu adlandıran "A → B" bağlama şemasını sayar (TALIMAT_OK: okun iki
# yanında ad); liste / sayım cümlesi ("Boyun demeti, 5 kablo (K14 a): …") ok taşısa da talimat değil (TALIMAT_LISTE). AU3 ve H02
# yalnız böyle bir liste cümlesiyle geçiyordu. Emir kipindeki fiil (TALIMAT_FIIL) liste cümlesinde de talimattır.
TALIMAT_OK = r"[\w)'’+−]\s*→\s*[\w(+−]"
# P10.7b2b (F10i-kontrol-3 A3): sayım kalıbı yalnız liste başlığıysa ("5 kablo (K14 a):"; sayım + isteğe bağlı parantez + iki nokta);
# "N tel" geçen gerçek bir "A → B" talimatı artık liste sayılmaz (bugün tek liste cümlesi K2 madde 5, eski ve yeni kalıp aynı tutar)
TALIMAT_LISTE = r"(?<!\w)\d+\s+(?:kablo|tel|hat|uç)\w*(?:\s*\([^()]*\))?\s*:"
TAMLIK_DIRENC = {"R-aku-olcum": "aku_olcum"}
_KIMLIK_ACIK = re.compile(r"(?<![\w{.])([A-Z]{1,2}\d{1,2})(?![\w}])")


def talimat_metinleri(ham):
    """ham [(yer, metin)] içinden talimat maddeleri: adımın is_ alanı ve alt adımların is_ alanı."""
    return [(y, t) for y, t in ham if y.startswith("kaynak ") and y.endswith(" is_")]


def _yan_cumleler(c):
    """Cümleyi parantez dışındaki virgül, noktalı virgül ve iki noktadan böl (parantez içi kimlik listesi bölünmez)."""
    out, bas, der = [], 0, 0
    for i, ch in enumerate(c):
        if ch == "(":
            der += 1
        elif ch == ")":
            der = max(0, der - 1)
        elif ch in ",;:" and der == 0 and not (ch == "," and i + 1 < len(c) and c[i + 1].isdigit()):
            out.append(c[bas:i])
            bas = i + 1
    out.append(c[bas:])
    return out


def talimat_kablolari(ham, kimlikler, adimlar=None):
    """Talimat maddesinde açık kimliği ve emir kipinde bağlama fiiliyle geçen kablolar: {kimlik: ilk yer}. adimlar: {kimlik: {adım
    kodu}} verilirse kablo yalnız o adımların talimatında sayılır."""
    out = {}
    for y, t in talimat_metinleri(ham):
        kod = y.split()[1]
        for c in re.split(_CUMLE_GENIS, _RDG.YER_TUTUCU.sub(" ", t or "")):
            # ok ("A → B") bağlama şemasıdır: yalnız cümlede emir dışı hiçbir fiil biçimi yokken talimat sayılır; düzeltme turu 2:
            # okun iki yanı adlandırılmış olmalı ve cümle liste / sayım cümlesi olmamalı
            ok = (re.search(TALIMAT_OK, c) and not re.search(TALIMAT_ERTELE, c, re.I) and not re.search(TALIMAT_LISTE, c, re.I))
            if not (re.search(TALIMAT_FIIL, c, re.I) or ok):
                continue
            for yc in _yan_cumleler(c):
                if re.search(TALIMAT_ERTELE, yc, re.I):
                    continue
                for k in _KIMLIK_ACIK.findall(yc):
                    if k in kimlikler and (adimlar is None or not adimlar.get(k) or kod in adimlar[k]):
                        out.setdefault(k, y)
    return out


def bugun_adimlari(T):
    """Kablo → kaydın rehber alanında "bugün" yazan adım kodları."""
    return {r["kimlik"]: {x["kod"] for x in (r.get("rehber") or []) if x.get("tur") == "bugün"} for r in T["kablolar"]}


def tamlik_denetle(ham=None, T=None, PH=None):
    """Kayıt → rehber tamlığı. ham: [(yer, metin)] yer tutucular çözülmeden (varsayılan kaynak_metinler(ham=True)).
    Doner dict(hata=[str], tarandi={tür: n}, muaf=[str], kablo_toplam, kablo_yok=[kimlik], kablo_talimat=n)."""
    ham = ham if ham is not None else kaynak_metinler(ham=True)
    D = _RDG.degerler() if (T is None and PH is None) else _RDG.Degerler(T, PH)
    T, PH = D.T, D.PH
    mh = "\n".join(t or "" for y, t in ham)
    yt_her = {(m.group(1), u) for m in _RDG.YER_TUTUCU.finditer(mh) for u in m.group(2).split("|")}
    th = "\n".join(t or "" for y, t in talimat_metinleri(ham))
    yt = {(m.group(1), u) for m in _RDG.YER_TUTUCU.finditer(th) for u in m.group(2).split("|")}   # P10.7b2a: yalnız talimat
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

    kimlikler = {r["kimlik"] for r in T["kablolar"]}
    tk = talimat_kablolari(ham, kimlikler, bugun_adimlari(T))
    for k, v in sorted(T["koruyucular"].items()):
        if v.get("tur") == "sigorta":
            oge("koruyucu", k, ("a", k) in yt, "kayıtta var, talimat maddesinde {a.%s} yer tutucusuyla geçmiyor" % k)
        elif v.get("tur") == "direnc":
            a = TAMLIK_DIRENC.get(k)
            oge("koruyucu", k, a is not None and ("ohm", a) in yt,
                "kayıtta direnç var, talimat maddesinde %s yok" % ("{ohm.%s}" % a if a else "eşleme (TAMLIK_DIRENC)"))
        else:
            kor = sorted(r["kimlik"] for r in T["kablolar"] if r.get("koruma") == k or k in (r.get("besleme_zinciri") or []))
            eks = [x for x in kor if x not in tk]
            oge("koruyucu", k, not eks, "cihaz koruması (%s); koruduğu kablolar talimatta değil: %s" % (v.get("tur"), ", ".join(eks)))
        if v.get("yer"):
            oge("koruyucu yeri", k, ("yer", k) in yt, "kayıtta yeri yazılı, talimat maddesinde {yer.%s} yok" % k)
    for k, v in sorted((T.get("tvs") or {}).items()):
        oge("kutuplu parça", k, ("yon", k) in yt, "TVS yönü kayıtta, talimat maddesinde {yon.%s} yok" % k)
    if T.get("kondansatorler"):
        oge("kutuplu parça", "kondansatör", ("yon", "kondansator") in yt, "kondansatör yönü kayıtta, talimat maddesinde {yon.kondansator} yok")
    for k, v in sorted(T["anahtarlar"].items()):
        if isinstance(v.get("uclar"), dict):
            a = k.split("-")[0]
            oge("kontak ucu", k, ("kontak", a) in yt, "kontak uçları kayıtta, talimat maddesinde {kontak.%s} yok" % a)
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
        st = "bsaplama" if a == "bara" else "saplama"              # P10.7b2a: anahtarlı bara {bsaplama.<k>}, yıldız {saplama.<k>}
        for n, lst in sorted((v.get("yerlesim") or {}).items()):
            for x in lst:
                kk = x.split("/")[0]
                oge("saplama düğümü", "%s saplama %s: %s" % (b, n, kk), (st, kk) in yt,
                    "yerleşimi kayıtlı, talimat maddesinde {%s.%s} yok" % (st, kk))
        if v.get("besleme_saplamasi") is not None:                 # besleme saplaması: yer tutucusu ya da o saplamadaki bir kablonun yeri
            bs = [x.split("/")[0] for x in (v.get("yerlesim") or {}).get(str(v["besleme_saplamasi"]), [])]
            oge("saplama düğümü", "%s besleme saplaması" % b,
                (st, "besleme") in yt or ("saplama", "besleme") in yt or any((st, kk) in yt for kk in bs),
                "besleme saplaması (%s) kayıtlı, talimat maddesinde {%s.besleme} ya da oradaki kablonun saplaması yok" % (
                    v["besleme_saplamasi"], st))
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
        oge("kablo", r["kimlik"], r["kimlik"] in tk,                # P10.7b2a: her kablo bir talimat maddesinde, kimliği ve bağlama işaretiyle
            "talimat maddesinde (is_ / alt adım is_) kimliği ve bağlama işaretiyle aynı cümlede geçmiyor (%s)" % (r.get("ad") or "")[:60])
    for i, (t, d, g) in enumerate(TAMLIK_MUAF):
        if not muaf_tuttu[i]:
            hata.append("TAMLIK_MUAF %s %s: hiçbir öğeyi tutmuyor (listeden çıkar)" % (t, d))
    yok = [r["kimlik"] for r in T["kablolar"] if r["kimlik"] not in tk]
    return dict(hata=hata, tarandi=dict(tarandi), muaf=muaf_kullanilan, kablo_toplam=len(T["kablolar"]), kablo_yok=yok,
                kablo_talimat=len(tk), kablo_anilan=sum(1 for r in T["kablolar"] if r["kimlik"] in kim))


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
    for ad, lst in (("ZORUNLU", ZORUNLU), ("ZORUNLU_ALAN", ZORUNLU_ALAN), ("ZORUNLU_CUMLE", ZORUNLU_CUMLE), ("ZORUNLU_SIRA", ZORUNLU_SIRA),
                    ("TERIM_ISTISNA", TERIM_ISTISNA), ("CIPLAK_MUAF", CIPLAK_MUAF), ("CIPLAK_KURAL", CIPLAK_KURAL), ("YASAK", YASAK),
                    ("TAMLIK_MUAF", TAMLIK_MUAF), ("TAMLIK_AD", sorted(TAMLIK_AD.items()))):
        for x in lst:
            out["liste"].append(_RK.girdi("LISTE " + ad, repr(x), "kural listesi"))
    for ad, x in (("CIPLAK_YUK", CIPLAK_YUK), ("CIPLAK_YUK_DEGIL", CIPLAK_YUK_DEGIL), ("OLUMSUZLAMA", OLUMSUZLAMA),
                  ("KRITIK_SOZ", KRITIK_SOZ), ("CIPLAK_MUAF_SAYI", CIPLAK_MUAF_SAYI),
                  # P10.7b2a: talimat maddesi ölçütü ve arayüz dizgesi ayıklaması da onay ister (gevşetilirse sessiz kalmasın)
                  ("TALIMAT_FIIL", TALIMAT_FIIL), ("TALIMAT_ERTELE", TALIMAT_ERTELE), ("TAMLIK_DIRENC", sorted(TAMLIK_DIRENC.items())), ("KOD_DIZGE_ONU", _KOD_DIZGE_ONU),
                  # düzeltme turu 2 (F10i-kontrol-2): ok kuralının liste / sayım kalıbı ve çıplak değer bağlam penceresi
                  ("TALIMAT_LISTE", TALIMAT_LISTE), ("TALIMAT_OK", TALIMAT_OK), ("CIPLAK_PENCERE", sorted(CIPLAK_PENCERE.items())),
                  ("CIPLAK_PENCERE_VARSAYILAN", CIPLAK_PENCERE_VARSAYILAN),
                  # P10.7b2b: cümle bölücü ve gerilim bağlamı da onay ister (gevşetilirse sessiz kalmasın)
                  ("CUMLE_GENIS", _CUMLE_GENIS), ("GERILIM_BAGLAM", _GERILIM_BAGLAM)):
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
    # P10.7b2e: K52 kapandı (a): eski M21 ("K52 kararlaştırılmış gibi") ters döndü; açık karar artık K64
    ("M21 K52 yeniden 'karar bekliyor' (kapandı)", "K1", "is_",
     "Göğüs regülatörünün panel yeri karar bekliyor (K52): G20'nin uç yeri ve boyu bu karara bağlı"),
    ("M21b K52 'karar bekliyor' şemada (kapandı)", "SEMA 12 V", "ad", "güç paneli (F6 3 A → LM2577 + LM2596; regülatör yeri karar bekliyor, K52)"),
    # P10.7b2e kısım 2: K64 kapandı (a): eski M21c ("K64 kararlaştırılmış gibi") ters döndü
    ("M21c K64 yeniden 'karar bekliyor' (kapandı)", "B5a", "not_", "Bara tutucusunun panelde yeri karar bekliyor (K64)"),
    # düzeltme turu 1 (F10m-kontrol N7): K65 kapandı (Echo, 16.11)
    ("M21d K65 yeniden 'karar bekliyor' (kapandı)", "K1", "not_", "Sağ / sol tanımı karar bekliyor (K65)"),
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
    # düzeltme turu 1 (F10i-kontrol A4): akü ölçümü bağlamında direnç ve gerilim
    ("çıplak akü ölçüm direnci (A4)", "akü ölçüm bölücüsünün 100 kΩ üst direnci kaynak ucunda", True),
    ("çıplak G07 gerilimi 4,23 V (A4)", "akü {v.aku_aralik} iken bölücünün orta noktasında 4,23 V okunur", True),
    ("F1 ölçüm koşulu elle (A4)", "bölücü oranı ({oran.aku_olcum}) katıdır: akü 11,0–12,0 V iken bölücünün orta noktasında {v.aku_olcum} okunur", True),
    ("PC817 3,3 V ölçümü (yakalanmamalı)", "arayüz kartındaki PC817 3,3 V'ta ölçüldü", False),
    ("ses bölücüsü direnci (yakalanmamalı)", "10 kΩ / 2,2 kΩ bölücü → PAM8403 sol", False),
    # düzeltme turu 2 (F10i-kontrol-2 R5): bağlam sözcüğü 40 karakterin dışında kalınca kaçıyordu
    ("R5 K1 G07 direnç ölçümü elle (100 kΩ)", "Pabuç saplamaya girmeden, akü ayrıkken multimetrenin direnç kademesiyle pabuç ile akü ölçüm "
     "bölücüsünün orta noktası arasını ölç: 100 kΩ'a yakın okunur (kontrol).", True),
    ("R5 K1 kontrol direnç ölçümü elle (100 kΩ)", "Akü ölçüm teli (G07): pabuç henüz saplamada değilken, akü ayrık, multimetrenin "
     "direnç kademesinde pabuç ile arayüz kartındaki akü ölçüm bölücüsünün orta noktası arası 100 kΩ'a yakın", True),
    # P10.7b2b (F10i-kontrol-3 A2): bağlam sözcüğü sayıdan sonra / cümle başında
    ("K-3 A2 cümle başı çıplak gerilim", "Okuma 1,95–2,20 V aralığının altında ya da üstündeyse: ana anahtarı kapat", True),
    ("K-3 A2 okuma aralığı elle, bağlam sonra", "Okuma 1,9 V ile 2,2 V arasında değilse bölücü bozuk", True),
    ("K-3 A2 okuma tek değer", "Okuma 2,1 V ise bölücü sağlam", True),
    ("kafa 12 V hattı (yakalanmamalı)", "3. Kafa 12 V (G17, F3 {a.F3}): direk ön yüzü", False),
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
    # P10.7b2a (F10h-kontrol-4 §3.5): daraltılmış kuralın kaçırdığı üç talimat ve daraltmadan önce de kaçan biçim
    ("köprüler (geniş zaman, mantar)", "Mantarın iki ucunu kısa bir telle köprüler", True),
    ("köprülere bağla (ana anahtar)", "Ana anahtarın iki ucunu baradaki köprülere bağla", True),
    ("köprüler takılır (ana anahtar)", "Ana anahtarın uçlarına köprüler takılır", True),
    ("bir köprü takılır (mantar)", "Mantarın iki ucu arasına bir köprü takılır", True),
    ("köprü → sigorta", "Sigorta yuvasının iki ucuna köprü tak", True),
    ("köprü yoksa röle çekmez (yakalanmamalı)", "Ö4 köprü yoksa röle çekmez", False),
    ("köprülenmez (yakalanmamalı)", "Mantarın uçları ve ana anahtarın uçları hiçbir zaman köprülenmez", False),
    ("tel köprü → röle (parantez, yakalanmamalı)", "acil stop düğüm kartı (dört ucu tel köprüyle lehimli) → röle K1 bobini", False),
    # düzeltme turu 1 (F10i-kontrol Ü2, Ü3, Ü5, A5)
    ("PCA9685 V+ klemensine bağla (Ü3)", "PCA9685'in V+ klemensini dağıtım kartının V+ barasına bağla", True),
    ("PCA9685 V+ pinine tel tak (Ü3)", "PCA9685'in V+ pinine tel tak", True),
    ("PCA9685 V+ tel takma (yakalanmamalı)", "PCA9685'in V+ klemensine ve kanal başlıklarının V+ pinine tel takma", False),
    ("PC817 çıkış beslemesi 5 V'a bağla (Ü2)", "PC817 modülünün çıkış besleme ucunu çevre 5 V'a bağla", True),
    ("çıkış VCC 5 V'a tak (Ü2)", "Modülün çıkış VCC ucunu 5 V'a tak", True),
    ("PC817 5 V'a bağlama (yakalanmamalı)", "PC817 modülünün çıkış besleme ucunu (çıkış VCC) ESP32'nin 3V3 pinine bağla (X01): 5 V'a bağlama", False),
    ("K1 87a ucuna bağla (Ü5)", "G09'u röle K1'in 87a ucuna bağla", True),
    ("K1 87a'ya lehimle (Ü5)", "Röle K1 kontağında G08'i 30'a, G09'u 87a'ya lehimle", True),
    ("K1 87a boş (yakalanmamalı)", "röle K1 kontağı 30 → 87 (87a boş): G08'i 30'a bağla", False),
    ("K2 NC ucuna lehimle (Ü5)", "G10'u K2'nin NC ucuna lehimle", True),
    ("K2 NC boş (yakalanmamalı)", "G10'u K2 kontağının COM ucuna lehimle, NO çıkışta (NC boş)", False),
    ("mantar NC uçları aynı vidaya (A5)", "Mantarın NC uçlarını aynı vidaya bağla", True),
    ("ana anahtar giriş ve çıkışı aynı saplamaya (A5)", "Ana anahtarın giriş ve çıkış uçlarını aynı saplamaya tak", True),
    ("aynı vidaya mantarın iki ucu (A5)", "Aynı vidaya mantarın iki ucunu bağla", True),
    # P10.7b2b (F10i-kontrol-3 A1)
    ("mantarın iki ucu tek kontak vidasına (K-3 A1)", "Mantarın iki ucunu tek kontak vidasına sık", True),
    ("tek kontak vidasına ana anahtarın uçları (K-3 A1)", "Tek kontak vidasına ana anahtarın iki ucunu bağla", True),
    ("mantarın her ucu kendi kontak vidasına (yakalanmamalı)", "Mantarın iki ucunu kendi kontak vidalarına ayrı ayrı sık", False),
    ("aynı saplamada iki pabuç (yakalanmamalı)", "Ana anahtarın çıkış saplamasına G04'ü ve G07'nin pabucunu tak", False),
    # düzeltme turu 2 (F10i-kontrol-2 B16): mantarın iki teli tek pabuçta
    ("B16 A01 ve A02 tek pabuca", "A01'i ve A02'yi tek pabuca sıkıp NC girişine tak", True),
    ("B16 A01 ile A02 aynı pabuca", "A01 ile A02'yi aynı pabuca sık", True),
    ("B16 mantarın uçları aynı pabuca", "Mantarın iki ucunu aynı pabuca sıkıp tak", True),
    ("B16 mantarın uçları tek pabuçta", "Mantarın uçlarını tek pabuçla NC girişine bağla", True),
    ("A01 / A02 ayrı uçlarda (yakalanmamalı)", "A01'i NC girişine, A02'yi NC çıkışına bağla", False),
    ("A01 / A02 tek pabuca sıkma (yakalanmamalı)", "A01 ile A02'yi tek pabuca sıkma", False),
]
# Düzeltme turu 1 (F10i-kontrol Ü1, Ü2, Ü3, Ü6, A1, A2, A7, A13): ham metinde bir adımın cümlesi bozulur; ZORUNLU / ZORUNLU_ALAN /
# ZORUNLU_CUMLE desenlerinden en az biri tutmamalı. (ad, adım, eski, yeni); eski ham metinde yoksa deneme kaçmış sayılır.
ZORUNLU_BOZMA = [
    ("K1 SV1 / SV2 ters kutup (Ü6)", "K1", "({kutup.SV1|SV2})", "(OUT− → V+, OUT+ → GND)"),
    ("K1 SV1 / SV2 kutbu silindi (Ü6)", "K1", " ({kutup.SV1|SV2})", ""),
    ("B6a kondansatör ters (Ü6)", "B6a", "yönü {yon.kondansator}", "yönü + bacağı GND barasında"),
    ("B5a kondansatör ters (Ü6)", "B5a", "yönü {yon.kondansator}", "yönü + bacağı GND barasında"),
    ("B5a SV3 ters kutup (Ü6)", "B5a", "bağla: {kutup.SV3}", "bağla: OUT+ → GND, OUT− → V+"),
    ("B6a X01 5 V'a (Ü2)", "B6a", "{uc.X01:PC817_çıkış_beslemesi:b} pinine bağla", "çevre 5 V klemensine bağla"),
    ("B6a X01 '5 V'a bağlama' silindi (Ü2)", "B6a", ": 5 V'a bağlama.", "."),
    ("B6a X01 süreklilik kontrolü silindi (Ü2)", "B6a", ", çıkış VCC ile çevre 5 V arası ötmez", ""),
    ("B6a P01 / P02 V+ uyarısı silindi (Ü3)", "B6a", "PCA9685'in V+ klemensine ve kanal başlıklarının V+ pinine tel takma; ", ""),
    ("B6a 3 telli kabloda V+ kesme silindi (Ü3)", "B6a", "3 telli hazır servo kablosu kullanırsan V+ damarını iki ucundan kes, makaronla yalıt. ", ""),
    ("B6a PCA9685 V+ süreklilik kontrolü silindi (Ü3)", "B6a", "arasında süreklilik yok (ötmemeli;", "arasında süreklilik var ("),
    ("K1 P03 V+ uyarısı silindi (Ü3)", "K1", "PCA9685'in V+ pinine tel takma; ", ""),
    ("K1 P03 süreklilik kontrolü silindi (Ü3)", "K1", "PCA9685'in kanal başlığının V+ pini ile dağıtım kartı C'nin V+ barası arasında süreklilik yok",
     "PCA9685'in kanal başlığının V+ pini ile dağıtım kartı C'nin V+ barası bağlı"),
    # düzeltme turu 2 (F10i-kontrol-2 §5 P01–P03): ölçü noktası klemense dönerse
    ("B6a P01 / P02 ölçü noktası klemens (D2)", "B6a", "PCA9685'in kanal başlığının V+ pini ile dağıtım kartı A'nın",
     "PCA9685'in V+ klemensi ile dağıtım kartı A'nın"),
    ("K1 P03 ölçü noktası klemens (D2)", "K1", "PCA9685'in kanal başlığının V+ pini ile dağıtım kartı C'nin",
     "PCA9685'in V+ klemensi ile dağıtım kartı C'nin"),
    # düzeltme turu 2 (F10i-kontrol-2 B16, B18, B23; §5 G07)
    ("F1 B16 mantarın iki ucu tek pabuçta (iş)", "F1", "A01'i (F5 {a.F5} çıkışından gelen) NC girişine, A02'yi (acil stop düğümüne giden) NC çıkışına.",
     "A01'i ve A02'yi tek pabuca sıkıp NC girişine tak."),
    ("F1 B16 mantarın iki ucu tek pabuçta (alt adım)", "F1", "A01'i NC girişine, A02'yi NC çıkışına.", "A01'i ve A02'yi aynı pabuca sık, NC girişine tak."),
    ("K1 B18 A06 + ucu F5 girişinde", "K1", "A06'nın + ucunu {parca.A06:+:a} noktasına, yani acil stop düğüm kartında bir klemensin kuyruğuna (kart altı) lehimle",
     "A06'nın + ucunu sigorta kutusunun F5 girişine lehimle"),
    ("K1 B18 A06 + ucunun düğümü elle değişti", "K1", "{parca.A06:+:a} noktasına", "sigorta kutusunun F5 girişi noktasına"),
    ("K1 B23 K2 pim okuması ters", "K1", "{kontak.K2:giris} ile {kontak.K2:bos} arası öter, {kontak.K2:giris} ile {kontak.K2:cikis} arası ötmez",
     "COM ile NO arası öter, COM ile NC arası ötmez"),
    ("K1 B23 K2 pim okuması uçlar yer değişti", "K1", "{kontak.K2:giris} ile {kontak.K2:bos} arası öter, {kontak.K2:giris} ile {kontak.K2:cikis} arası ötmez",
     "{kontak.K2:giris} ile {kontak.K2:cikis} arası öter, {kontak.K2:giris} ile {kontak.K2:bos} arası ötmez"),
    ("K1 G07 pabuç kılıfı çıkarma silindi (D2)", "K1", "halka pabucun PVC kılıfını çıkar", "halka pabucunu hazırla"),
    ("K1 G07 kovana sıkmadan lehim (D2)", "K1", "pabucun kovanına sık (pabuç pensesiyle), sonra kovana lehimle", "pabucun kovanına lehimle"),
    ("K1 G07 makaron soğumadan / kovana çekilmedi (D2)", "K1", "Soğuyunca makaronu direncin ve kovanın üstüne çek", "Makaronu direncin üstüne çek"),
    ("F1 G07 aralık dışı talimatı silindi (D2)", "F1", "Bölücü okuması {v.aku_olcum} aralığının altında ya da üstündeyse: ana anahtarı kapat, aküyü XT60'tan ayır",
     "Okuma aralık dışındaysa not al"),
    ("K1 G22 uçları ters (Ü1)", "K1", "{uc.G22:+:b} klemensine, − damarını modülün {uc.G22:−:a}",
     "{uc.G22:−:a} klemensine, − damarını modülün {uc.G22:+:b}"),
    ("K1 G22 ters bağlama uyarısı silindi (Ü1)", "K1", ", ters bağlıyken enerji verme", ""),
    ("K1 G22 kutup kontrolü ters (Ü1)", "K1", "{uc.G22:−:a} ile yıldız barası arası öter, {uc.G22:+:b} ile yıldız barası arası ötmez",
     "{uc.G22:+:b} ile yıldız barası arası öter, {uc.G22:−:a} ile yıldız barası arası ötmez"),
    ("K1 A06 − ucu silindi (A7)", "K1", "; − ucunu modülün IN1 − klemensinden arayüz kartının GND pedine lehimle (makaron)", ""),
    ("K1 G07 makaron lehimden sonra (A1)", "K1", "lehimden önce makaronu G07'nin teline geçir", "lehimden sonra makaronu G07'nin teline geçir"),
    ("K1 G07 gerginlik giderme silindi (A1)", "K1", "Gerginlik giderme: G07'yi", "G07'yi"),
    ("K1 G07 açıkta bacak kontrolü silindi (A1)", "K1", "direnç, iki bacağı ve pabuç kovanı makaronla tümüyle örtülü (açıkta bacak yok), ", ""),
    ("K1 K2 pim bakışı lehimden sonra (A2)", "K1", "lehimden önce K2'nin pimlerini bul", "lehimden sonra K2'nin pimlerini bul"),
    ("F1 G07 ölçüm aralığı elle yazıldı (A4)", "F1", "{v.aku_olcum} okunur", "1,53–2,23 V okunur"),
    ("F1 G07 ölçüm koşulu değişti (A4)", "F1", "akü {v.aku_aralik} iken", "akü 11,0–12,0 V iken"),
    ("E3a CA cümlesi silindi (A13)", "E3a", " CA baskılı ya da bantsız TVS'i takma (kablajda teyit).", ""),
    ("E3a eski 'iki uçta işaret' ölçütü (A13)", "E3a", "sonu CA (ör. P6KE18CA) çift yönlüdür, bandı yoktur", "iki uçta da işaret varsa çift yönlüdür"),
    # düzeltme turu 2 (F10i-kontrol-2 §5 TVS): muğlak eski biçim geri gelirse
    ("E3a TVS muğlak 'sonu A' (D2)", "E3a", "sonu yalnız A (ör. P6KE18A) tek yönlüdür", "P6KE…A (sonu A) tek yönlüdür"),
    # P10.7b2b (F10i-kontrol-3 A4, A5, A6): üç talimat cümlesi geri alınırsa ya da sırası bozulursa
    ("K1 G07 makaronu uzakta tutma silindi (A5)", "K1",
     "Makaronu lehim yerinden uzağa, telin geri tarafına it ve iki lehim bitip soğuyana kadar orada tut (lehimin ısısı yakındaki "
     "makaronu erken büzer, sonra kaymaz). ", ""),
    ("K1 G07 makaronu uzakta tutma lehimden sonra (A5 sıra)", "K1",
     "Makaronu lehim yerinden uzağa, telin geri tarafına it ve iki lehim bitip soğuyana kadar orada tut (lehimin ısısı yakındaki "
     "makaronu erken büzer, sonra kaymaz). Direnci telin ucuna lehimle. ",
     "Direnci telin ucuna lehimle. Makaronu lehim yerinden uzağa, telin geri tarafına it ve iki lehim bitip soğuyana kadar orada "
     "tut (lehimin ısısı yakındaki makaronu erken büzer, sonra kaymaz). "),
    ("K2 AU3 kutup kontrolü silindi (A4)", "K2",
     "Kutup kontrolü, dikişleri sıkmadan önce (AU3): işaretli + damarı {uc.AU3:+:a} ucunda, öbür damar {uc.AU3:−:a} ucunda "
     "(ters ise lehimi şimdi düzelt). ", ""),
    # P10.7b2b düzeltme turu 1 (F10j-kontrol D2): ilk cümle değişti ("kafa ucunda bağla" yalnız öbür dört kablo)
    ("K2 AU3 dikişler lehimden önce sıkıldı (A4 sıra)", "K2", "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). ",
     "kafa ucunda bağla; önce dikişleri sık. "),
    ("K2 AU3 'dikişlerini sık' lehimden önce (D2)", "K2", "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). ",
     "kafa ucunda bağla, sonra arka kabuğun dikişlerini sık. "),
    ("K2 AU3 'dikişleri sıkıp' lehimden önce (D2)", "K2", "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). ",
     "kafa ucunda bağla, arka kabuk dikişleri sıkıp kapat. "),
    ("K2 AU3 yeniden 'kafa ucunda bağla' kapsamında (D2)", "K2",
     "Hoparlör kablosu (AU3) dışındaki dört kabloyu (U03, H02, S10, G17) kafa ucunda bağla",
     "Beş kabloyu (U03, H02, S10, AU3, G17) kafa ucunda bağla"),
    ("K2 AU3 enerjisiz koşulu silindi (A4)", "K2", "dikişleri sıkmadan önce, enerjisizken (akü XT60 ayrık): ", "dikişleri sıkmadan önce: "),
    # P10.7b2b düzeltme turu 1 (F10j-kontrol D1): madde üçe bölündü; akü gerilimi cümlesi ilk maddede
    ("F1 G07 akünün kendi gerilimi silindi (A6)", "F1",
     "Önce akünün kendi gerilimini oku: akü XT60'tan ayrıkken kırmızı ucu akünün XT60'ındaki (akü tarafı) + kontağına, siyah ucu − "
     "kontağına değdir (bir uç iki kontağa birden değmesin, iki uç birbirine değmesin), okunanı not al: bu akü gerilimidir. ", ""),
    ("F1 G07 akü gerilimi akü takıldıktan sonra (A6 sıra)", "F1",
     "Önce akünün kendi gerilimini oku: akü XT60'tan ayrıkken",
     "Ana anahtar kapalıyken aküyü XT60'tan tak, sonra ana anahtarı aç: okunan gerilim akü geriliminin bölücü oranı katıdır. Önce "
     "akünün kendi gerilimini oku: akü XT60'tan ayrıkken"),
    ("F1 G07 beklenen = akü × oran silindi (A6)", "F1",
     "beklenen bölücü okuması = akü gerilimi × bölücü oranı ({oran.aku_olcum}); ", ""),
    # P10.7b2b düzeltme turu 1 (F10j-kontrol D1): yeni karar ağacının cümleleri silinir, gevşer ya da sırası bozulursa
    ("F1 G07 'pimine' geri geldi (D1)", "F1", "+ kontağına, siyah ucu − kontağına", "+ pimine, siyah ucu − pimine"),
    ("F1 G07 kısa devre uyarıları silindi (D1)", "F1", " (bir uç iki kontağa birden değmesin, iki uç birbirine değmesin)", ""),
    ("F1 G07 'iki uç birbirine değmesin' silindi (D1)", "F1", ", iki uç birbirine değmesin)", ")"),
    ("F1 G07 akü aralık dışı kapısı silindi (D1)", "F1",
     "Akü gerilimi {v.aku_aralik} dışındaysa burada dur: bölücü ölçümüne geçme, ana anahtarı açma, aşama 2'ye (F5) geçme; ", ""),
    ("F1 G07 akü aralık dışında bölücüye geçiliyor (D1)", "F1", "dışındaysa burada dur: bölücü ölçümüne geçme,",
     "dışındaysa not al, bölücü ölçümüne geç,"),
    ("F1 G07 akü aralık dışında aşama 2 yasağı silindi (D1)", "F1", "ana anahtarı açma, aşama 2'ye (F5) geçme; akü", "ana anahtarı açma; akü"),
    ("F1 G07 kapı bölücü ölçümünden sonra (D1 sıra)", "F1", "okunanı not al: bu akü gerilimidir. Akü gerilimi",
     "okunanı not al: bu akü gerilimidir. Sonra aküyü XT60'tan tak, sonra ana anahtarı aç: okunan gerilim akü geriliminin bölücü "
     "oranı katıdır. Akü gerilimi"),
    ("F1 G07 bölücü ölçümü koşulsuz (D1)", "F1", "Akü gerilimi {v.aku_aralik} içindeyse: kırmızı ucu", "Sonra kırmızı ucu"),
    ("F1 G07 bant kuralı silindi (D1)", "F1", "Karar yalnız banttan: okuma {v.aku_olcum} içindeyse bölücü geçer; ", ""),
    ("F1 G07 bant yerine sayısız oran ölçütü (D1)", "F1", "Karar yalnız banttan: okuma {v.aku_olcum} içindeyse bölücü geçer",
     "Okuma beklenen bölücü okumasına yakınsa bölücü geçer"),
    ("F1 G07 oran karar ölçütü oldu (D1)", "F1", "; bu açıklamadır, karar ölçütü değildir", "; karar bu orana göre verilir"),
    ("F1 G07 'bölücü bozuk' koşulsuz (D1)", "F1", "Akü gerilimi {v.aku_aralik} içinde olduğu için bölücü bozuk", "Bölücü bozuk"),
    ("F1 G07 kusur bulunmazsa devam (D1)", "F1", "Listedeki yerlerde kusur bulunmazsa da devam etme",
     "Listedeki yerlerde kusur bulunmazsa devam et"),
    # P10.7b2c ön işi (F10j-kontrol-2 A1, A2, A4): F10j-kontrol-2'de yalnız onay kaydının yakaladığı bozmalar ve eski muğlak biçimler
    ("F1 A1 eski muğlak 'akü gerilimi maddesinden'", "F1", "ölçümü baştan, akünün kendi gerilimini okuduğun maddeden yinele",
     "ölçümü akü gerilimi maddesinden baştan yinele"),
    ("F1 A2 eski çelişkili 'okuma aralığa girene kadar'", "F1", "bölücüdeki kusuru düzeltmeden ana anahtarı",
     "bölücü düzelip okuma aralığa girene kadar ana anahtarı"),
    ("F1 A4 'Kusuru düzeltince … yinele' silindi", "F1",
     " Kusuru düzeltince ölçümü baştan, akünün kendi gerilimini okuduğun maddeden yinele.", ""),
    ("F1 A4 kapıda yineleme gevşedi", "F1", "aralığına gelince bu maddeyi baştan yinele",
     "aralığına gelmese de sonraki maddeye geç"),
    ("F1 A4 madde 2 sonunda uçlar enerjiliyken", "F1", "içindeyse bölücü geçer; ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök",
     "içindeyse bölücü geçer; ana anahtarı kapat, aküyü XT60'tan ayır, sonra ölçü uçlarını sök; acele varsa uçları ana anahtar açıkken sök"),
    ("F1 A4 bant gevşedi", "F1", "içindeyse bölücü geçer;", "içindeyse bölücü geçer, bandın biraz dışındaysa da geçer;"),
    ("F1 A4 kusur yoksa aşama 2'ye geç", "F1", "bölücü okumasını kayda yaz (tolerans kaynakta yok)",
     "bölücü okumasını kayda yaz ve aşama 2'ye (F5) geç (tolerans kaynakta yok)"),
    ("F1 A4 kusur cümlesinin arkasına gevşetme", "F1", "kayda yaz (tolerans kaynakta yok)",
     "kayda yaz (tolerans kaynakta yok); bölücü bozuk olabilir, yine de devam et"),
    ("K2 A4 dört kablodan sonra AU3 yeniden bağlandı", "K2", "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). ",
     "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). Hoparlör kablosunu (AU3) da kafa ucunda bağla. "),
    ("K2 A4 'dikiş vidalarını sık' lehimden önce", "K2", "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). ",
     "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). Arka kabuğun dikiş vidalarını sık. "),
    ("K2 A4 'dikişleri iyice sık' lehimden önce", "K2", "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). ",
     "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). Dikişleri iyice sık. "),
    ("K2 A4 'DİKİŞLERİ SIK' lehimden önce", "K2", "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). ",
     "kafa ucunda bağla (E4'te arka kabuk dikişleri sıkılmadı). DİKİŞLERİ SIK. "),
    # P10.7b2c düzeltme turu 1 (F10k-kontrol D2, D3)
    ("K2 U06 taban ucu notu silindi (D2)", "K2",
     "\"ESP32 USB\" şemasının (U06) taban ucu yanlış yerde, güç panelinin üstünde çizili (şema yeniden çizilecek): kablonun taban ucu "
     "elektronik katındaki ESP32 taşıyıcısında ESP32'nin USB girişine takılır", ""),
    ("K2 U06 ucu şemadaki yere (D2)", "K2", "ESP32 taşıyıcısında ESP32'nin USB girişine takılır", "şemadaki yere, güç panelinin üstüne bırakılır"),
    ("K2 U06 'yanlış yerde' gevşedi (D2)", "K2", "taban ucu yanlış yerde, güç panelinin üstünde çizili",
     "taban ucu güç panelinin üstünde çizili"),
    ("K2 U06 notunun arkasına şemaya uy (D2)", "K2", "ESP32'nin USB girişine takılır", "ESP32'nin USB girişine takılır; şüphede şemaya uy"),
    ("K1 P03 dağıtım kartı C'nin yeri silindi (D3)", "K1",
     " Dağıtım kartı C (kafa): kart güç panelinde, XL4016 C'nin yanında; adındaki \"kafa\" beslediği pan / tilt servolarıdır.", ""),
    ("K1 P03 kart kafada (D3)", "K1", "kart güç panelinde, XL4016 C'nin yanında", "kart kafada, tilt servosunun yanında"),
]
# Düzeltme turu 1 (F10i-kontrol A6): "kablajda teyit" ibaresi silinir; teyit_denetle yakalamalı
TEYIT_BOZMA = [
    ("E3a TVS ibaresi silindi (A6)", "E3a", "CA baskılı ya da bantsız TVS'i takma (kablajda teyit).", "CA baskılı ya da bantsız TVS'i takma."),
    ("E3a P6KE18A ibaresi silindi (A6)", "E3a", "madde 2'deki gibi oku (kablajda teyit)", "madde 2'deki gibi oku"),
    ("B5a kondansatör ibaresi silindi (A6)", "B5a", "kondansatörü takma (kablajda teyit)", "kondansatörü takma"),
    ("B6a kondansatör ibaresi silindi (A6)", "B6a", "okunmuyorsa takma (kablajda teyit)", "okunmuyorsa takma"),
]


def _ham_boz(ham, kod, eski, yeni):
    """ham [(yer, metin)] içinde adım kodunun metinlerinde eski → yeni; değişen metin sayısı ile yeni liste."""
    out, n = [], 0
    for y, t in ham:
        p = y.split()
        if len(p) > 1 and p[1] == kod and eski in (t or ""):
            t, n = t.replace(eski, yeni), n + 1
        out.append((y, t))
    return out, n


def _alan_anahtarlari(p):
    """Kaynak yerinin (bölünmüş) ZORUNLU_ALAN / ZORUNLU_SIRA alan anahtarları. P10.7b2d-A: "is_ana" yalnız adımın ana metni; demet
    alt adımlı adımda (rehber_metin.DEMET_ALT) alt adım metinleri sırayla "is_" alanına da girer (metin bölündü, kural aynı yerde)."""
    out = [p[2]]
    if p[2] == "is_":
        out.append("is_ana")
    elif p[2] == "alt" and p[-1] == "is_" and RM.ADIM.get(p[1], {}).get("demet_alt"):
        out.append("is_")
    return out


def _zorunlu_eksik_say(ham):
    """Ham metinden (yer tutucular çözülerek) ZORUNLU + ZORUNLU_ALAN + ZORUNLU_CUMLE eksik sayısı."""
    D = _RDG.degerler()
    adim, alanlar = collections.defaultdict(str), collections.defaultdict(str)
    for yer, t in ham:
        p = yer.split()
        if p[0] == "kaynak" and len(p) > 2 and p[1] in RM.ADIM:
            c = D.coz(t or "", [])
            adim[p[1]] += "\n" + c
            for a in _alan_anahtarlari(p):
                alanlar[(p[1], a)] += "\n" + c
    n = sum(1 for k, d, ad in zorunlu_listesi() if k in RM.ADIM and not re.search(d, adim[k]))
    n += sum(1 for k, alan, d, ad in zorunlu_alan_listesi() if k in RM.ADIM and not re.search(d, alanlar[(k, alan)]))
    n += len(sira_denetle(alanlar))                                  # P10.7b2b: ZORUNLU_SIRA
    return n + len([x for x in cumle_denetle(dict(adim)) if not x["yer"].startswith("SEMA ")])


def _veri_benzetimi():
    """P10.7b2e: rehber_veri.py'nin adım biçiminde (FreeCAD'siz) en küçük veri: rehber_metin.ADIM'dan (yer tutucular çözülmüş) adımın is_ /
    baglanti_md / kontrol / kablo / not_ alanı ve alt adım metinleri sira_grup[..]["is_"]. Demet alt adımlı adımda adımın is_ alanı ana
    metindir; veride "is_ana" adlı anahtar YOKTUR (rehber_veri.py ADIMLAR.append). Parça listesi boş (BILESEN anması bu sınamada aranmaz)."""
    ad = []
    for i, (k, m) in enumerate(RM.ADIM.items()):
        a = dict(i=i, kod=k, is_=m.get("is_") or "", baglanti_md=m.get("baglanti_md") or "", kontrol=list(m.get("kontrol") or []),
                 kablo=list(m.get("kablo") or []), not_=list(m.get("not_") or []))
        if m.get("sira"):
            a["sira_grup"] = [dict(ad=g.get("ad"), **({"is_": g["is_"]} if g.get("is_") else {})) for g in m["sira"]]
        ad.append(a)
    return dict(adimlar=ad, parcalar=[])


def veri_is_ana_bozma_denemesi():
    """P10.7b2e (F10l-gunluk § 10.3, § 10.7): veri modu (tutarlilik) ZORUNLU_ALAN "is_ana"yı veride adımın is_ alanında arar. b2d'nin ilk
    üretimi bu alanı veride var olmayan "is_ana" anahtarında aradığı için düştü (zorunlu eksik 2); FreeCAD'siz sınamalar yalnız kaynak
    modunu koştuğu için görmedi. Kalıcı sınama: veri benzetiminde temel eksik 0 ve is_ana kuralı boş değil; üç uyarı bozması yakalanır;
    uyarı yalnız "is_ana" adlı (veride olmayan) anahtara yazılırsa da yakalanır (kod yeniden o anahtarı okursa bu bozma kaçar)."""
    import copy
    ana = [(k, d) for k, alan, d, a in zorunlu_alan_listesi() if alan == "is_ana"]
    V0 = _veri_benzetimi()

    def say(V):
        return [x for x in tutarlilik(V, [])["zorunlu_eksik"] if "(alan is_ana)" in x["uyari"]]

    t0 = say(V0)
    out = [dict(ad="veri is_ana: bozulmamış benzetimde eksik 0, kural %d" % len(ana), yakalandi=not t0 and len(ana) >= 2, hata=len(t0))]
    A0 = {a["kod"]: a for a in V0["adimlar"]}

    def boz(ad, f):
        V = copy.deepcopy(V0)
        A = {a["kod"]: a for a in V["adimlar"]}
        degisti = f(A)
        n = len(say(V))
        out.append(dict(ad="veri is_ana: " + ad, yakalandi=bool(degisti) and n > 0, hata=n))

    def sil(kod, eski):
        def f(A):
            if eski not in A[kod]["is_"]:
                return False
            A[kod]["is_"] = A[kod]["is_"].replace(eski, "")
            return True
        return f

    def tasi(A):                                                    # K1 uyarısı ana metinden ilk alt adıma
        u = "Bağlarken akü ayrık (XT60 açık)."
        if u not in A["K1"]["is_"] or not A["K1"].get("sira_grup"):
            return False
        A["K1"]["is_"] = A["K1"]["is_"].replace(u, "")
        A["K1"]["sira_grup"][0]["is_"] = u + " " + A["K1"]["sira_grup"][0].get("is_", "")
        return True

    def yanlis_anahtar(A):                                          # uyarılar yalnız veride olmayan "is_ana" anahtarında
        for k in ("K1", "K2"):
            A[k]["is_ana"], A[k]["is_"] = A[k]["is_"], ""
        return True

    boz("K1 ana metinden 'Bağlarken akü ayrık (XT60 açık).' silindi", sil("K1", "Bağlarken akü ayrık (XT60 açık)."))
    boz("K2 ana metinden 'F3 (kafa) takılı değil' silindi", sil("K2", "F3 (kafa) takılı değil"))
    boz("K1 uyarısı ana metinden ilk alt adıma taşındı", tasi)
    boz("uyarılar yalnız 'is_ana' anahtarında (kod o anahtarı okursa kaçar)", yanlis_anahtar)
    if not all(A0[k].get("sira_grup") for k in ("K1", "K2")):
        out.append(dict(ad="veri is_ana: K1 / K2 benzetimde alt adımlı değil", yakalandi=False, hata=1))
    return out


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
    # düzeltme turu 2 (F10i-kontrol-2 B27): bölücünün alt direnci 18 → 33 kΩ; "beklenen" aralık ADC sınırını aşar, yer tutucu çözülmemeli
    EL0 = D.EL
    for ad, eski, yeni, beklenen in (("B27 bölücü 18 → 33 kΩ", "| Akü gerilimi | 100 kΩ / 18 kΩ", "| Akü gerilimi | 100 kΩ / 33 kΩ", True),
                                     ("B27 ADC sınırı satırdan silindi", "doğrusal bölge ≤ 2,45 V", "doğrusal bölge", True),
                                     ("bölücü 18 → 15 kΩ (sınır içinde, yakalanmamalı)", "| Akü gerilimi | 100 kΩ / 18 kΩ",
                                      "| Akü gerilimi | 100 kΩ / 15 kΩ", False)):
        n = 0
        if eski in EL0:
            D2 = _RDG.Degerler(D.T, D.PH, EL0.replace(eski, yeni))
            for tt in ("v", "oran"):
                try:
                    D2.deger(tt, "aku_olcum")
                except KeyError:
                    n += 1
        out.append(dict(ad="bölücü: " + ad, yakalandi=(n > 0) == beklenen and eski in EL0, hata=n))
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
    # P10.7b2a: talimat maddesi ölçütü (K63). Metinden kimlik / yer tutucu çıkar, kimliği talimattan kontrol listesine taşı, kayda öğe ekle.
    def _talimat_boz(f):
        return [(y, f(t or "") if y.endswith(" is_") else t) for y, t in ham]
    for ad, f in (("SV3 kimliği talimattan çıktı", lambda t: re.sub(r"\bSV3\b", "servo hattı", t)),
                  ("G07 kimliği talimattan çıktı (yalnız kontrolde kaldı)", lambda t: t.replace("G07", "akü ölçüm teli")),
                  ("P03 bağlama işaretsiz ('anılıyor')", lambda t: re.sub(r"[^.\n]*\bP03\b[^.\n]*\.?", " Kafa sinyal köprüsü P03 hakkında not.", t)),
                  ("{yon.P6KE18A} çıktı", lambda t: t.replace("{yon.P6KE18A}", "yönüne dikkat et")),
                  ("{yon.kondansator} çıktı", lambda t: t.replace("{yon.kondansator}", "yönüne dikkat et")),
                  ("{kontak.K2} çıktı", lambda t: t.replace("{kontak.K2}", "kontak")),
                  ("{yer.hat-A|hat-B|hat-C} çıktı", lambda t: t.replace("{yer.hat-A|hat-B|hat-C}", "kablo üstünde")),
                  ("{bsaplama.G22} çıktı", lambda t: t.replace("{bsaplama.G22}", "son")),
                  ("{ohm.aku_olcum} çıktı", lambda t: t.replace("{ohm.aku_olcum}", "bir")),
                  ("{a.hat-cevre} yalnız kontrolde", lambda t: t.replace("{a.hat-cevre}", "sigorta")),
                  # düzeltme turu 2 (F10i-kontrol-2 §3): kimlik yalnız K2 madde 5'in liste / sayım cümlesinde kalır (ok kuralı)
                  ("AU3 / H02 yalnız liste cümlesinde (ok kuralı)",
                   lambda t: re.sub(r"\bAU3\b(?!; PAM8403 → hoparlör)", "hoparlör teli", re.sub(r"\bH02\b(?!; Pi micro HDMI 1)", "HDMI", t)))):
        h2 = _talimat_boz(f)
        n = len(tamlik_denetle(h2)["hata"]) - t0 if h2 != ham else 0
        out.append(dict(ad="tamlık (talimat): " + ad, yakalandi=n > 0, hata=n))
    # düzeltme turu 1 (F10i-kontrol Ü4): N01 / N02'nin emri silinir, kimlikler ileri / olumsuz / başka adımdaki cümleye taşınır
    def _n_sil(t):
        return t.replace("enkoderi (N01)", "enkoderi").replace("enkoderi (N02)", "enkoderi")
    for ad, ek, kod in (("N01 / N02 ileri cümle ('K2'de takılır')", " Enkoder kabloları (N01, N02) K2'de takılır.", None),
                        ("N01 / N02 ileri cümle ('bağlanacak')", " Enkoder kabloları N01 ve N02 sonra bağlanacak.", None),
                        ("N01 / N02 olumsuz ('takma')", " N01 ve N02'yi bu adımda takma.", None),
                        ("N01 / N02 olumsuz ('bağlama')", " Enkoder kablolarını (N01, N02) bu adımda bağlama.", None),
                        ("N01 / N02 emri bugün olmayan adımda", " Enkoder kablolarını (N01, N02) bağla.", "F5")):
        h2 = [(y, (_n_sil(t or "") + (ek if (kod is None or y.split()[1] == kod) else "")) if y.endswith(" is_") else t)
              for y, t in ham]
        n = sum(1 for h in tamlik_denetle(h2)["hata"] if re.match(r"kablo N0[12]\b", h))
        out.append(dict(ad="tamlık (talimat): " + ad, yakalandi=n == 2, hata=n))
    n = len(tamlik_denetle([(y, _n_sil(t or "") + (" Enkoder kablolarını (N01, N02) bağla." if y.endswith(" is_") else ""))
                            for y, t in ham])["hata"]) - t0
    out.append(dict(ad="tamlık (talimat): N01 / N02 emir kipinde, bugünkü adımda (yakalanmamalı)", yakalandi=n == 0, hata=n))
    # P10.7b2b (F10i-kontrol-3 A7): cümle bölücü kısaltmada bölmez, cümle sonunda böler
    for ad, metin, parca in (("'ör.' sonrası bölünmez (K-3 A7)", "Sonu CA (ör. P6KE18CA) çift yönlüdür. Bandı yoktur.", 2),
                             ("'vb.' / 'bkz.' sonrası bölünmez (K-3 A7)", "Pabuç, makaron vb. hazır (bkz. E2) olsun. Sonra başla.", 2),
                             ("cümle sonu yine bölünür (K-3 A7)", "Sigortayı çıkar. Aküyü ayır. Sonra başla.", 3)):
        n = len([c for c in re.split(_CUMLE_GENIS, metin) if c.strip()])
        out.append(dict(ad="açık iş: cümle bölücü " + ad, yakalandi=n == parca, hata=n))
    # P10.7b2b (F10i-kontrol-3 A3): "N tel" geçen gerçek ok talimatı sayılır; liste başlığındaki ok sayılmaz
    for ad, metin, beklenen in (("'2 tel' geçen ok talimatı sayılır (K-3 A3)",
                                 "Kafa ekranı besleme (K03): Pi 5 V pini → ekranın 5 V girişi, 2 tel.", True),
                                ("liste başlığı '2 kablo (…):' oku sayılmaz (K-3 A3)",
                                 "Ekran demeti, 2 kablo (K14 a): ekran beslemesi (K03; Pi 5 V → ekran).", False)):
        n = len(talimat_kablolari([("kaynak K2 is_", metin)], {"K03"}))
        out.append(dict(ad="tamlık (talimat): " + ad, yakalandi=(n > 0) == beklenen, hata=n))
    for ad, boz in (("kayda yeni kablo", lambda T: T["kablolar"].append(dict(T["kablolar"][[r["kimlik"] for r in T["kablolar"]].index("X01")],
                                                                          kimlik="X02"))),
                    ("kayda yeni TVS", lambda T: T["tvs"].__setitem__("P6KE6V8A-yeni", dict(T["tvs"]["P6KE6V8A-pi"]))),
                    ("kayda koruyucu yeri", lambda T: T["koruyucular"]["F1"].__setitem__("yer", "sigorta kutusunda: 1. yuva")),
                    ("kayda kontak uçları", lambda T: T["anahtarlar"]["mantar"].__setitem__("uclar", dict(giris="1", cikis="2"))),
                    ("kayda yeni direnç", lambda T: T["koruyucular"].__setitem__("R-yeni", dict(T["koruyucular"]["R-aku-olcum"])))):
        T2 = json.loads(json.dumps(T))
        boz(T2)
        n = len(tamlik_denetle(ham, T=T2)["hata"]) - t0
        out.append(dict(ad="tamlık: " + ad, yakalandi=n > 0, hata=n))
    # P10.7b2a (K9 / V4): ASCII sınaması app.js / yazdir.html görünen dizgelerinde ve kol lejantında; kod dizgesi sayılmaz
    a0 = open(ARAYUZ_GORUNEN[0], encoding="utf-8").read()
    y0 = open(ARAYUZ_GORUNEN[1], encoding="utf-8").read()
    k0 = open(KOL_KABLO, encoding="utf-8").read()
    i0 = open(ARAYUZ_GORUNEN[2], encoding="utf-8").read()
    for ad, ad_dosya, kaynak, ek, beklenen in (
            # P10.7b2b (F10i-kontrol A8): tek sözcük, öznitelik, index.html; karşılaştırma dizgesi kod
            ("app.js tek sözcük textContent (A8)", "app.js", a0, '\nb.textContent = "Onceki";\n', True),
            ("app.js tek sözcük üç terimli (A8)", "app.js", a0, '\nb.textContent = ilk ? "Baslangic" : "Onceki";\n', True),
            ("app.js title özniteliği (A8)", "app.js", a0, "\nx.innerHTML = '<span title=\"Parca secili\">' + n + '</span>';\n", True),
            ("app.js title ataması (A8)", "app.js", a0, '\nx.title = "Parca secili";\n', True),
            ("app.js setAttribute aria-label (A8)", "app.js", a0, '\nx.setAttribute("aria-label", "Onceki");\n', True),
            ("yazdir.html title özniteliği (A8)", "yazdir.html", y0, '\n<button title="Yazdirmadan once bak">x</button>\n', True),
            ("index.html etiket dışı metin (A8)", "index.html", i0, "\n<p>Rehberi acmak icin tikla</p>\n", True),
            ("index.html alt özniteliği (A8)", "index.html", i0, '\n<img src="a.png" alt="Govde gorunumu">\n', True),
            ("app.js karşılaştırma dizgesi (A8, yakalanmamalı)", "app.js", a0, '\nx.title = k === "baglanti" ? a : b;\n', False),
            ("app.js tek sözcük sınıf adı (A8, yakalanmamalı)", "app.js", a0, '\nel.className = "secili";\n', False),
            ("app.js ASCII dizge", "app.js", a0, '\nx.textContent = "Kablo baglantisi kontrol edildi";\n', True),
            ("app.js şablon dizgesi", "app.js", a0, "\nx.innerHTML = `<b>${n}</b> kablo secili, gorunum degisti`;\n", True),
            ("yazdir.html etiket dışı metin", "yazdir.html", y0, "\n<p>Kablolar baglanmadan once sigortalari cikar</p>\n", True),
            ("app.js kod dizgesi (yakalanmamalı)", "app.js", a0, '\nel.className = "kare-baslik secili"; q("#panel .satir");\n', False)):
        t0a = len(ascii_kalinti(gorunen_dizgeler(ad_dosya, kaynak)))
        n = len(ascii_kalinti(gorunen_dizgeler(ad_dosya, kaynak + ek))) - t0a
        out.append(dict(ad="ascii: " + ad, yakalandi=(n > 0) == beklenen, hata=n))
    n = len(ascii_kalinti(kol_lejantlari(k0.replace('servo="Servo kablosu"', 'servo="Servo kablosu (baglanti)"', 1)))) - \
        len(ascii_kalinti(kol_lejantlari(k0)))
    out.append(dict(ad="ascii: kol lejantı", yakalandi=n > 0, hata=n))
    # düzeltme turu 1: zorunlu desen bozmaları (kutup, uç, süreklilik, sıra) ve "kablajda teyit" ibaresi
    z0 = _zorunlu_eksik_say(ham)
    for ad, kod, eski, yeni in ZORUNLU_BOZMA:
        h2, k = _ham_boz(ham, kod, eski, yeni)
        n = _zorunlu_eksik_say(h2) - z0 if k else 0
        out.append(dict(ad="zorunlu: " + ad, yakalandi=n > 0, hata=n))
    y0 = len(teyit_denetle(ham))
    for ad, kod, eski, yeni in TEYIT_BOZMA:
        h2, k = _ham_boz(ham, kod, eski, yeni)
        n = len(teyit_denetle(h2)) - y0 if k else 0
        out.append(dict(ad="teyit: " + ad, yakalandi=n > 0, hata=n))
    # TALIMAT_ERTELE gevşetilirse onay kaydı farkı verir
    global TALIMAT_ERTELE
    eski_e = TALIMAT_ERTELE
    # onay kaydının girdisi değişmeli (kayıt bu kurala göre yenilenmişse fark verir; yenilenmemişse de girdi aynı kalmamalı)
    g0 = [repr(x) for x in kritik_girdiler(ham)["liste"]]
    try:
        TALIMAT_ERTELE = eski_e.replace("|gidecek|gelecek", "")
        n = len(set(repr(x) for x in kritik_girdiler(ham)["liste"]) ^ set(g0))
    finally:
        TALIMAT_ERTELE = eski_e
    out.append(dict(ad="açık iş: onay kaydı (TALIMAT_ERTELE gevşedi)", yakalandi=n > 0, hata=n))
    out += veri_is_ana_bozma_denemesi()                               # P10.7b2e: veri modu is_ana (F10l-gunluk § 10.3)
    out += demet_bozma_denemesi(ham)
    return dict(temel_hata=len(temel), deneme=out, yakalanan=sum(1 for x in out if x["yakalandi"]), toplam=len(out))


def demet_bozma_denemesi(ham=None):
    """P10.7b2d-A: demet alt adımı kurallarının (D1–D5) bozmaları. Her biri beklenen kuralın hatasını artırmalı."""
    import copy
    ham = ham if ham is not None else kaynak_metinler(ham=True)
    yol = demet_yol_adimlari()
    t0 = demet_alt_denetle(ham=ham, yol_adim=yol)["hata"]
    out = [dict(ad="demet: bozulmamış kaynak (hata 0)", yakalandi=not t0, hata=len(t0))]

    def kural_say(r, k):
        return sum(1 for x in r["hata"] if x[0] == k)

    def ham_yer(h, yer, f):
        return [(y, f(t) if y == yer else t) for y, t in h]

    def sira_boz(kod, f):
        s = copy.deepcopy(RM.ADIM_HAM[kod]["sira"])
        f(s)
        return {kod: s}

    def dene(ad, kural, h=None, sira=None):
        r = demet_alt_denetle(ham=h if h is not None else ham, sira=sira, yol_adim=yol)
        n = kural_say(r, kural) - sum(1 for x in t0 if x[0] == kural)
        out.append(dict(ad="demet %s: %s" % (kural, ad), yakalandi=n > 0, hata=n))
    y = "kaynak %s alt adım %d is_"

    # düzeltme turu 1: alt adım sırası ada göre aranır (kart eklenince / bölününce bozmalar sessizce başka karta kaymaz)
    def ki(kod, parca):
        ns = [n for n, g in enumerate(RM.DEMET_ALT[kod]) if parca in g["ad"]]
        assert len(ns) == 1, (kod, parca, ns)
        return ns[0]

    def ky(kod, parca):
        return y % (kod, ki(kod, parca) + 1)
    hm = dict(ham)
    k_bara, k_g07, k_role = ki("K1", "iki bara"), ki("K1", "(G07)"), ki("K1", "Röle K1")
    k_cikis, k_g22, k_kutu, k_acil = ki("K1", "Bara çıkışları"), ki("K1", "(G22)"), ki("K1", "Sigorta kutusu"), ki("K1", "Acil stop")
    k_altkat, k_sonar, k_son = ki("K1", "Alt kat"), ki("K1", "sonar"), ki("K1", "Son kontrol")
    sonar = "Sonarlar: sağ (Q01), orta (Q02) ve sol (Q03) sonarın VCC'sini arayüz"
    t8 = hm.get(ky("K1", "sonar")) or ""
    i8 = t8.find(sonar)
    j8 = t8.find("bağla.", i8) + len("bağla.")
    cumle = t8[i8:j8] if i8 >= 0 else "⁣yok"
    # kablo yanlış alt adımda: sonar cümlesi (Q01–Q03, demet "taban sonar") ilk alt adıma (17.1) taşındı
    h = ham_yer(ham_yer(ham, ky("K1", "sonar"), lambda t: t.replace(cumle + " ", "")), y % ("K1", 1), lambda t: t + " " + cumle)
    dene("sonar cümlesi (Q01–Q03) kendi alt adımından 17.1'e taşındı", "D3", h)
    dene("sonar cümlesi taşındı: metin kendi paragraflarıyla aynı değil", "D1", h)
    dene("sonar alt adımının demetinden \"taban sonar\" silindi (Q01–Q03 demetsiz)", "D3",
         sira=sira_boz("K1", lambda s: s[k_sonar].update(demet=("taban elektronik katı",))))
    dene("K2 madde 1'in demetleri yer değiştirdi (kol sağ → gövde (K2))", "D2",
         sira=sira_boz("K2", lambda s: s[0].update(demet=("gövde (K2)", "kol sol"))))
    dene("kayıtta olmayan demet adı", "D2", sira=sira_boz("K1", lambda s: s[k_role].update(demet=("taban (K3)",))))
    dene("gerekçesiz demet (röle alt adımına \"kafa içi\")", "D2",
         sira=sira_boz("K1", lambda s: s[k_role].update(demet=("taban (K1)", "kafa içi"))))
    dene("demetsiz alt adımın \"genel\" işareti silindi", "D2", sira=sira_boz("K1", lambda s: s[k_son].pop("genel")))
    # madde silindi / yer değiştirdi
    dene("acil stop alt adımının metni silindi", "D1", ham_yer(ham, ky("K1", "Acil stop"), lambda t: ""))
    dene("sıra kaydında acil stop paragrafı yok", "D1", sira=sira_boz("K1", lambda s: s[k_acil].update(paragraf=())))
    a3, a4 = hm[y % ("K1", 3)], hm[y % ("K1", 4)]
    dene("17.3 ile 17.4'ün metni yer değiştirdi", "D1",
         ham_yer(ham_yer(ham, y % ("K1", 3), lambda t: a4), y % ("K1", 4), lambda t: a3))
    dene("sıra kaydında K2 madde 2 ile 3 yer değiştirdi", "D1",
         sira=sira_boz("K2", lambda s: (s[1].update(paragraf=(3,)), s[2].update(paragraf=(2,)))))
    kg = ki("K2", "Göğüs")
    dene("K2 bir paragraf iki alt adımda (yineleme)", "D1",
         sira=sira_boz("K2", lambda s: s[kg].update(paragraf=(kg + 1, kg + 2))))
    # uyarı düştü: alt adım metnindeki uyarı (D1) ve ana metnin uyarısı (D5: ZORUNLU_ALAN is_ana)
    dene("G22 alt adımından \"ters bağlıyken enerji verme\" uyarısı silindi", "D1",
         ham_yer(ham, ky("K1", "(G22)"), lambda t: t.replace(", ters bağlıyken enerji verme", "")))
    z0 = _zorunlu_eksik_say(ham)
    for ad, kod, eski in (("K1 ana metinden \"Bağlarken akü ayrık (XT60 açık).\" silindi", "K1", " Bağlarken akü ayrık (XT60 açık)."),
                          ("K2 ana metinden \"kafa uçları enerjisiz bağlanır\" silindi", "K2", "; kafa uçları enerjisiz bağlanır")):
        h2 = ham_yer(ham, "kaynak %s is_" % kod, lambda t, e=eski: t.replace(e, ""))
        n = _zorunlu_eksik_say(h2) - z0 if h2 != ham else 0
        out.append(dict(ad="demet D5: " + ad, yakalandi=n > 0, hata=n))
    # uyarı ana metinden alt adıma taşındı: ana metinde değil (D5), metin bölünmesi de bozuk (D1)
    w = " Bağlarken akü ayrık (XT60 açık)."
    h2 = ham_yer(ham_yer(ham, "kaynak K1 is_", lambda t: t.replace(w, "")), y % ("K1", 1), lambda t: w.strip() + " " + t)
    n = _zorunlu_eksik_say(h2) - z0
    out.append(dict(ad="demet D5: K1 akü ayrık uyarısı ana metinden 17.1'e taşındı", yakalandi=n > 0, hata=n))
    # ZORUNLU_SIRA demet adımında alt adım metninde de geçerli (G07 makaronu, AU3 dikişleri)
    h2 = ham_yer(ham, ky("K2", "Kafa uçları"), lambda t: t.replace("Hoparlör kablosu (AU3) dışındaki",
                                                                    "Dikişleri sık. Hoparlör kablosu (AU3) dışındaki", 1))
    n = _zorunlu_eksik_say(h2) - z0 if h2 != ham else 0
    out.append(dict(ad="demet ZORUNLU_SIRA: K2 kafa uçları alt adımında dikişler AU3'ten önce sıkılıyor", yakalandi=n > 0, hata=n))
    # şema / kablo yolu tam bir alt adımda
    dene("G19 şeması hiçbir alt adımda değil", "D4", sira=sira_boz("K1", lambda s: s[k_altkat].update(sema=())))
    dene("G19 şeması iki alt adımda (bara çıkışları ve alt kat)", "D4",
         sira=sira_boz("K1", lambda s: s[k_cikis].update(sema=tuple(s[k_cikis].get("sema") or ()) + ("(G19,",))))
    dene("Kablo yolu 9 hiçbir alt adımda değil", "D4", sira=sira_boz("K1", lambda s: s[k_kutu].update(desen=())))
    dene("U06 şeması kablosunu anmayan alt adımda (32.1)", "D4",
         sira=sira_boz("K2", lambda s: (s[3].update(sema=()), s[0].update(sema=("(U06)",)))))
    # P10.7b2e kısım 2 (F10l-kare-inceleme 32.4): Kablo yolu 12 (B01) K2 32.4'ten (sema_ok gerekçesiyle) K1 17.10'a geçti; eski
    # "sema_ok gerekçesi silindi" bozması yerine: yolun deseni 17.10'dan silinince hiçbir alt adımda kalmaz
    dene("Kablo yolu 12 deseni 17.10'dan silindi", "D4",
         sira=sira_boz("K1", lambda s: s[k_sonar].update(desen=tuple(x for x in s[k_sonar]["desen"] if x != "Kablo yolu 12:"))))
    dene("Kablo yolu 12 yeniden 32.4'e (U06 alt adımı) desenlendi", "D4",
         sira=sira_boz("K2", lambda s: s[3].update(desen=("Kablo yolu 12:",))))
    # D8 (P10.7b2e kısım 2, F10l-kare-inceleme 17.11 = 17.12): yeni parçası ve vurgusu olmayan iki alt adımın karesi aynı olamaz
    dene("17.11'in kamerası ve odağı silindi: karesi 17.12 ile aynı (eski hata)", "D8",
         sira=sira_boz("K1", lambda s: (s[k_son - 1].pop("kamera", None), s[k_son - 1].pop("odak", None))))
    dene("32.6'nın şeması silindi, bakışı 32.8'e (son kontrol) kopyalandı", "D8",
         sira=sira_boz("K2", lambda s: (s[5].update(sema=()), s[7].update(kamera=s[5].get("kamera"), saydam=s[5].get("saydam"),
                                                                            odak=s[5].get("odak")))))
    # düzeltme turu 1 (F10m-kontrol N6): neredeyse aynı kamera (1e-6) ve ters sıralı odak da aynı karedir
    dene("32.6'nın şeması silindi, bakışı 32.8'e kamerası 1e-6 kaydırılıp kopyalandı", "D8",
         sira=sira_boz("K2", lambda s: (s[5].update(sema=()), s[7].update(
             kamera=tuple(v + 1e-6 for v in s[5].get("kamera")), saydam=s[5].get("saydam"), odak=s[5].get("odak")))))
    dene("32.6'nın şeması silindi, bakışı 32.8'e saydam / odak ters sırayla kopyalandı", "D8",
         sira=sira_boz("K2", lambda s: (s[5].update(sema=()), s[7].update(
             kamera=s[5].get("kamera"), saydam=tuple(reversed(s[5].get("saydam") or ())),
             odak=tuple(reversed(s[5].get("odak") or ()))))))
    dene("bayat şema deseni", "D4", sira=sira_boz("K1", lambda s: s[k_g07].update(sema=("(G07,", "(G99,"))))
    dene("P03 bağlantı tablosu iki alt adımda", "D4", sira=sira_boz("K1", lambda s: s[k_sonar].update(kablo_sec=("Bağlantı tablosu P03",))))

    # D6 bara uçları (F10l-kontrol D1). uc alanı sira_boz kopyasında yoksa DEMET_ALT'tan ada göre okunur; bozma açıkça yazar.
    def uc_boz(f):
        def g(s):
            for n, x in enumerate(s):
                x["uc"] = tuple(RM.DEMET_ALT["K1"][n].get("uc") or ())
            f(s)
        return sira_boz("K1", g)
    kopru = ("köprü/+", "köprü/−")
    h2 = ham_yer(ham, ky("K1", "Röle K1"), lambda t: t + " Köprüler: {kopru_adet.yildiz} ve {kopru_adet.bara}.")
    dene("bara köprüleri röle alt adımına (17.4) kaydı: G06 bara kurulmadan baraya takılıyor (eski hata)", "D6", h2,
         sira=uc_boz(lambda s: (s[k_bara].update(uc=("G05/−",)), s[k_role].update(uc=s[k_role]["uc"] + kopru))))
    t5 = hm.get(ky("K1", "Bara çıkışları")) or ""
    i16 = t5.find("XL4016 C'yi de")
    i12 = t5.find("G12–G15'in alt kat ucu")
    h2 = ham_yer(ham, ky("K1", "Bara çıkışları"), lambda t: t[:i12] + t[i16:] + " " + t[i12:i16].rstrip()) if min(i16, i12) >= 0 else ham
    dene("G16 cümlesi G12–G15 bağlamasının önüne alındı: 16 AWG pabuç G13'ün altına girer", "D6", h2)
    dene("alt kat alt adımında \"alt adım 17.5'te bağlandı\" göstergesi silindi (G12–G15 iki kartta bağla)", "D6",
         ham_yer(ham, ky("K1", "Alt kat"), lambda t: t.replace(" alt adım 17.5'te,", ",")))
    dene("direk alt adımında G17 / G20 \"alt adım 17.7'de bağlandı\" yerine \"bağla\"", "D6",
         # P10.7b2e: K52 a ile G20 metni "taban ucu ve panel içinde kalan göğüs ekranı dalı (G20) ... bağlandı" oldu
         ham_yer(ham, ky("K1", "Direğe"), lambda t: t.replace("dalı (G20) alt adım 17.7'de bağlandı; ", "dalını (G20) bağla; ")))
    dene("ucun alt adımında saplama yer tutucusu yok (G06 − ucu \"barasına\")", "D6",
         ham_yer(ham, ky("K1", "şarj kolu"), lambda t: t.replace("yıldız barasının {saplama.G06} numaralı saplamasına", "yıldız barasına")))
    dene("bara ucu hiçbir alt adımda değil (G22/−)", "D6",
         sira=uc_boz(lambda s: s[k_g22].update(uc=tuple(x for x in s[k_g22]["uc"] if x != "G22/−"))))
    dene("bir uç iki kartta bağlatılıyor (G17/− kutu ve alt kat alt adımında)", "D6",
         sira=uc_boz(lambda s: s[k_altkat].update(uc=("G17/−",))))
    dene("kayıttaki bara yerleşiminde olmayan uç (G99/+)", "D6", sira=uc_boz(lambda s: s[k_role].update(uc=s[k_role]["uc"] + ("G99/+",))))
    # F10l-kontrol N1: G22 talimatı kendi alt adımından 17.1'e taşındı. D3 demet üyeliğine baktığı için yakalamıyordu; bara uçlu kablo
    # için D6 (saplama yer tutucusu sahip alt adımda değil) yakalar. Bara ucu olmayan kablo için kaba kalır (onay kaydı yakalar).
    t6 = hm.get(ky("K1", "(G22)")) or ""
    dene("N1: G22 talimatı kendi alt adımından 17.1'e taşındı", "D6",
         ham_yer(ham_yer(ham, ky("K1", "(G22)"), lambda t: ""), y % ("K1", 1), lambda t: t + " " + t6))

    # D7 göndermeler (F10l-kontrol D2)
    dene("çözülmeyen gönderme (\"madde 9\" çevrilmeden kaldı)", "D7",
         ham_yer(ham, ky("K1", "(G07)"), lambda t: t + " (madde 9)"))
    dene("var olmayan karta gönderme (alt adım 17.13)", "D7",
         ham_yer(ham, ky("K1", "Son kontrol"), lambda t: t.replace("(alt adım 17.8)", "(alt adım 17.13)", 1)))
    dene("paragraf başında çapa kaldı (\"3. \" kart numarasıyla çelişir)", "D7", ham_yer(ham, ky("K1", "Röle K1"), lambda t: "3. " + t))
    yf = next((a for a, t in ham if a.startswith("kaynak F5") and "alt adım 32.4" in (t or "")), None)
    dene("başka adımda \"K2 madde 4\" çevrilmeden kaldı (F5)", "D7",
         ham_yer(ham, yf, lambda t: t.replace("alt adım 32.4", "K2 madde 4", 1)) if yf else ham)
    kay = [dict(e) for e in RM.GONDERME_KAYIT]
    if kay:
        kay[0]["hedef"] = kay[0]["hedef"] % len(RM.DEMET_ALT[kay[0]["kod"]]) + 1
    r = demet_alt_denetle(ham=ham, yol_adim=yol, gonderme=dict(kayit=kay))
    n = kural_say(r, "D7") - sum(1 for x in t0 if x[0] == "D7")
    out.append(dict(ad="demet D7: gönderme yanlış karta çevrildi (kayıt hedefi kaydı)", yakalandi=n > 0, hata=n))
    kayn = dict(RM.GONDERME_KAYNAK)
    kayn[("K1", "bozma")] = "G05'in üstüne (madde 2)"
    r = demet_alt_denetle(ham=ham, yol_adim=yol, gonderme=dict(kaynak=kayn))
    n = kural_say(r, "D7") - sum(1 for x in t0 if x[0] == "D7")
    out.append(dict(ad="demet D7: kaynakta kayda geçmeyen gönderme var", yakalandi=n > 0, hata=n))
    return out


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


# Düzeltme turu 1 (F10i-kontrol A6): kaydı "kablajda teyit" işaretli yer tutucu (TVS / kondansatör yönü, K1 / K2 kontak uçları, ana
# anahtar saplaması) talimat maddesinde geçiyorsa aynı madde satırında "kablajda teyit" ibaresi de geçmeli (silinirse yakalanır).
def teyit_denetle(ham=None):
    """Ham talimat metinleri: [dict(yer, yer_tutucu, satir)] (ibaresi olmayan madde satırı)."""
    ham = ham if ham is not None else kaynak_metinler(ham=True)
    D = _RDG.degerler()
    out = []
    for y, t in talimat_metinleri(ham):
        for satir in (t or "").split("\n"):
            for m in _RDG.YER_TUTUCU.finditer(satir):
                if any(D.teyit_kaydi(m.group(1), u) for u in m.group(2).split("|")) and "kablajda teyit" not in satir:
                    out.append(dict(yer=y, yer_tutucu=m.group(0), satir=satir[:160]))
    return out


# ------------------------------------------------------------------ P10.7b2d-A: K1 / K2 demet alt adımları (planlama/d158/F10l-gunluk.md)
# rehber_metin.DEMET_ALT. FreeCAD'siz, veri üretmeden. Kurallar:
#   D1 paragraf: alt adımların paragraf sırası 1 … n ardışık, eksiksiz, yinelemesiz; ana metin = paragraf 0; her alt adımın metni kendi
#      paragrafları; ana metin + alt adımlar (sırayla) = adımın tam metni (ALT_TAM_HAM). ham verilirse metinler oradan okunur (bozma).
#   D2 demet: alt adımın demet adları kayıttaki demet_sirasi'nda; her demet adı alt adımın metninde kimliğiyle geçen bir kablonun kayıttaki
#      demetidir (elle demet yok); demetsiz alt adım "genel" işaretli (son kontrol), "genel" alt adımın demeti yok.
#   D3 kablo: adımın alt adım metinlerinde kimliğiyle geçen her kablo, kayıttaki demeti o alt adımın demetlerinde olan bir alt adımda geçer.
#   D4 kare: adımın her şeması (SEMA) ve her CAD kablo yolu (taban-analiz.json, rehber_metin.kablo_kapisi) tam bir alt adımın desenine uyar;
#      o alt adım şemanın kablolarından birini (demeti uyan) anar ya da desen sema_ok'ta gerekçeli; hiçbir şemaya uymayan desen yok;
#      kablo_sec adımın kablo listesinde tam bir maddeye uyar, madde tek alt adımda, maddedeki kimlik alt adımın metninde geçer.
#   D5 (ZORUNLU_ALAN "is_ana"): ana metnin uyarıları ana metinde (alt adım kartlarından önce basılır, ekranda her alt adımın üstünde).
def _demet_kimlikleri(metin, kimlikler):
    s = {k for k in _KIMLIK_ACIK.findall(metin or "") if k in kimlikler}
    for on, a, b in re.findall(r"(?<![\w{.])([A-Z]{1,2})(\d{2})\s*[–-]\s*\1(\d{2})(?![\w}])", metin or ""):
        s |= {"%s%02d" % (on, n) for n in range(int(a), int(b) + 1) if "%s%02d" % (on, n) in kimlikler}
    return s


def demet_yol_adimlari(yol=None):
    """CAD kablo yolu numarası -> adım kodu (rehber_veri.py ile aynı kural: kablo_kapisi(yolun en büyük y'si)); dosya yoksa None."""
    import rehber_kablo as _RKB
    yol = yol or _RKB.GEO_ANALIZ
    if not os.path.exists(yol):
        return None
    A = json.load(open(yol, encoding="utf-8"))
    ky = A.get("kablo_yolu") or []
    # P10.7b2f: rehberin çizdiği (rehber_kablo.CAD_KIRP ile kırpılmış) bölüm; rehber_veri.py kırpılmış gövdenin y'sine bakar
    return {n: RM.kablo_kapisi(max(p[1] for p in _RKB.cad_noktalar(n, A)), n) for n, k in enumerate(ky, 1) if k.get("noktalar")}


# P10.7b2d-A düzeltme turu 1 (F10l-kontrol D1): bara uçları (rehber_metin.DEMET_ALT "uc"; kayıt kablolar.json bara-pabuc yerlesim).
#   U1 kayıttaki her bara ucu (ve iki baranın köprüleri) tam bir alt adımda; kayıtta olmayan uç yok.
#   U2 ucun alt adımının metninde ucun saplama yer tutucusu ({saplama.…Gnn…} yıldız, {bsaplama.…Gnn…} anahtarlı bara, köprü için
#      {kopru_adet.yildiz|bara}): montajcı numarayı başka alt adımda aramaz.
#   U3 aynı saplamada 12 AWG pabuç (köprü uçları dahil) incelerden önce takılır (alt adım sırası, aynı alt adımda metindeki yer):
#      "büyük akımlı (12 AWG) pabuçlar yığının altında" (bara-pabuc.not). Köprüsüz bara olmadığı için bu, bara kurulmadan baraya uç
#      takılmamasını da sınar.
#   U4 ucu başka alt adımda bağlanan kabloyu anan alt adım (yerlesim=True olan yerleşim listesi hariç) o alt adımı numarasıyla anar
#      ("alt adım 17.5'te bağlandı"): aynı uç iki kartta "bağla" diye okunmaz.
def bara_uc_denetle(R, kod, G, metinler, T, h):
    D = _RDG.degerler()
    BP = T["klemens_turleri"]["bara-pabuc"]
    yer = {}
    for bara, isaret in (("Yıldız barası · GND", "−"), ("Anahtarlı bara · +", "+")):
        for s, lst in (BP["kopruler"][bara].get("yerlesim") or {}).items():
            for x in lst:
                yer[x] = (isaret, s)
    kopru_awg = {"+": BP["kopruler"]["Anahtarlı bara · +"]["awg"], "−": BP["kopruler"]["Yıldız barası · GND"]["awg"]}
    kesit = {r["kimlik"]: (r.get("kesit") or {}).get("awg") for r in T["kablolar"]}
    adlar = {g["ad"]: g for g in getattr(R, "DEMET_ALT", {}).get(kod, [])}

    def alan(g, k):
        return g[k] if k in g else (adlar.get(g.get("ad")) or {}).get(k)
    sahip = {}
    for n, g in enumerate(G):
        for u in alan(g, "uc") or ():
            sahip.setdefault(u, []).append(n)
    if not sahip:
        return
    no = getattr(R, "ALT_ADIM_NO", {}).get(kod)
    for u in sorted(set(yer) | {"köprü/+", "köprü/−"}):
        ns = sahip.get(u, [])
        if len(ns) != 1:
            h("D6", "%s %s: bara ucu %d alt adımda bağlatılıyor (tam bir olmalı: %s)" % (kod, u, len(ns),
                                                                                    ", ".join("%d" % (n + 1) for n in ns) or "hiçbiri"))
    for u in sorted(sahip):
        if u not in yer and u not in ("köprü/+", "köprü/−"):
            h("D6", "%s %s: kayıttaki bara yerleşiminde yok" % (kod, u))
    pos = {}
    for u, ns in sorted(sahip.items()):
        if len(ns) != 1:
            continue
        k, isaret = u.split("/")
        if k == "köprü":
            desen = r"\{kopru_adet\.%s\}" % ("bara" if isaret == "+" else "yildiz")
        else:
            desen = r"\{%s\.[^{}\s]*\b%s\b[^{}\s]*\}" % ("bsaplama" if isaret == "+" else "saplama", re.escape(k))
        m = re.search(desen, metinler[ns[0]] or "")
        if not m:
            h("D6", "%s alt adım %d: %s bu alt adımda bağlatılıyor ama metninde saplama yer tutucusu yok" % (kod, ns[0] + 1, u))
        else:
            pos[u] = (ns[0], m.start())
    for isaret, s in sorted(set(yer.values())):
        uclar = [u for u, v in sorted(yer.items()) if v == (isaret, s)] + ["köprü/" + isaret]
        awg = {u: kopru_awg[isaret] if u.startswith("köprü/") else kesit.get(u.split("/")[0]) for u in uclar}
        for a in uclar:
            for b in uclar:
                if awg[a] == 12 and awg[b] != 12 and a in pos and b in pos and pos[a] >= pos[b]:
                    h("D6", "%s %s barası saplama %s: %s (12 AWG) %s'den sonra takılıyor (alt adım %d, %d): büyük akımlı pabuç altta "
                            "olmalı" % (kod, "anahtarlı" if isaret == "+" else "yıldız", s, a, b, pos[a][0] + 1, pos[b][0] + 1))
    kab = {}
    for u, ns in sahip.items():
        if not u.startswith("köprü/"):
            kab.setdefault(u.split("/")[0], set()).update(ns)
    kim = set(kesit)
    for n, g in enumerate(G):
        if alan(g, "yerlesim"):
            continue
        anilan = _demet_kimlikleri(D.coz(metinler[n] or "", []), kim)
        for c in sorted(anilan & set(kab)):
            if n in kab[c]:
                continue
            if not any(("alt adım %s.%d" % (no, k + 1)) in (metinler[n] or "") for k in kab[c]):
                h("D6", "%s alt adım %d (%s): %s'yi anıyor ama ucu alt adım %s'de bağlanıyor ve bu metin o alt adımı anmıyor (aynı uç iki "
                        "kartta \"bağla\" okunur)" % (kod, n + 1, g.get("ad"), c, "/".join("%s.%d" % (no, k + 1) for k in sorted(kab[c]))))


# P10.7b2d-A düzeltme turu 1 (F10l-kontrol D2): alt adım göndermeleri (rehber_metin._demet_bol, gonderme_cevir).
#   D7a çözülemeyen gönderme yok (rehber_metin.GONDERME_HATA).
#   D7b K1 / K2 metinlerinde "madde N" kalmadı (başka adımın maddesi "B6a madde 4" hariç); başka adımlarda "K1 / K2 madde N" kalmadı.
#   D7c paragraf başında çapa ("3. ", "3b. ") kalmadı: kart numarasıyla çelişen ikinci numara yok.
#   D7d her "alt adım S.M" var olan bir kartı gösterir (S alt adımlı bir adımın numarası, 1 ≤ M ≤ alt adım sayısı).
#   D7e her çevrilen gönderme (GONDERME_KAYIT) çapanın paragrafını içeren karta gider (kaynaktan bağımsız yeniden kurulur) ve
#       kaynaktaki gönderme sayısı çevrilen sayıya eşit.
def gonderme_denetle(R, ham, h, kayit=None, kaynak=None):
    kayit = R.GONDERME_KAYIT if kayit is None else kayit
    kaynak = R.GONDERME_KAYNAK if kaynak is None else kaynak
    for e in R.GONDERME_HATA:
        h("D7", "çözülemeyen gönderme: %s" % e)
    kodlar = set(getattr(R, "DEMET_ALT", {}))
    adimlar = set(R.ADIM)

    def kalan(t, kod_bagli):
        out = []
        for m in R._GONDERME.finditer(t or ""):
            on = R._ADIM_ONEKI.search((t or "")[:m.start()])
            if not m.group(1) and on and on.group(1) in adimlar:
                continue
            if m.group(1) or kod_bagli in kodlar:
                out.append(m.group(0))
        return out
    no_kod = {v: k for k, v in getattr(R, "ALT_ADIM_NO", {}).items()}
    sira_say = {i: len(R.ADIM[k].get("sira") or []) for i, k in enumerate(getattr(R, "M6_KODLAR", [])) if k in R.ADIM}
    for y, t in ham:
        p = y.split()
        kod = p[1] if len(p) > 1 else ""
        for x in kalan(t, kod):
            h("D7", "%s: gönderme çevrilmedi: «%s»" % (y, x))
        if kod in kodlar and (y.endswith(" is_")):
            for s in (t or "").split("\n"):
                if R._CAPA.match(s):
                    h("D7", "%s: paragraf başında çapa kaldı (kart numarasıyla çelişen numara): «%s»" % (y, s[:30]))
        for m in re.finditer(r"\balt adım (\d+)\.(\d+)\b", t or ""):
            s, j = int(m.group(1)), int(m.group(2))
            if not (1 <= j <= sira_say.get(s, 0)):
                h("D7", "%s: «%s» var olan bir kartı göstermiyor" % (y, m.group(0)))
    n_kaynak = sum(len(kalan(t, yol[0])) for yol, t in kaynak.items())
    if n_kaynak != len(kayit) + len(R.GONDERME_HATA):
        h("D7", "kaynakta %d gönderme, çevrilen %d, çözülemeyen %d" % (n_kaynak, len(kayit), len(R.GONDERME_HATA)))
    par = {k: R.ALT_KAYNAK_HAM.get(k, "").split("\n") for k in kodlar}
    hm = dict(ham)
    for e in kayit:
        kod, capa, n = e["kod"], e["capa"], e["hedef"]
        bul = [_RCAPA_SIL(R, s) for s in par.get(kod, []) if s.startswith(capa + ". ")]
        kart = hm.get("kaynak %s alt adım %d is_" % (kod, n)) or ""
        if len(bul) != 1 or bul[0] not in kart:
            h("D7", "%s: %s madde %s alt adım %s.%d'e çevrildi, ama çapanın paragrafı o kartta değil" % (
                e["yer"], kod, capa, getattr(R, "ALT_ADIM_NO", {}).get(kod), n))


def _RCAPA_SIL(R, s):
    """Çapası silinmiş kaynak paragrafı, gönderme çevrilmeden önceki biçimiyle karşılaştırılamaz: yalnız çevrilmeyen baş kısmı
    (ilk "madde" göndermesine kadar) aranır."""
    s = R._CAPA.sub("", s, count=1)
    m = R._GONDERME.search(s)
    return (s[:m.start()] if m else s)[:120]


def demet_alt_denetle(R=None, ham=None, sira=None, T=None, yol_adim=None, gonderme=None):
    """Doner dict(hata=[(kural, ileti)], adim={kod: dict(alt, kablo, oge)}). sira: {kod: [grup]} (bozma; varsayılan R.ADIM_HAM).
    gonderme: dict(kayit=…, kaynak=…) D7 bozması için."""
    R = R or RM
    D = _RDG.degerler()
    T = T or D.T
    demet = {r["kimlik"]: r.get("demet") for r in T["kablolar"]}
    kim = set(demet)
    gecerli = set(T.get("demet_sirasi") or [])
    yol_adim = yol_adim if yol_adim is not None else demet_yol_adimlari()
    import rehber_kablo as _RKB
    hm = dict(ham) if ham is not None else None
    hata, ozet = [], {}

    def h(kural, ileti):
        hata.append((kural, ileti))
    for kod in getattr(R, "DEMET_ALT", {}):
        G = (sira or {}).get(kod) or R.ADIM_HAM[kod].get("sira") or []
        tam = R.ALT_TAM_HAM.get(kod, "")
        par = tam.split("\n")
        y = "kaynak %s" % kod
        # D1
        sirali = [j for g in G for j in g.get("paragraf") or ()]
        if sirali != list(range(1, len(par))):
            eks = sorted(set(range(1, len(par))) - set(sirali))
            yin = sorted({j for j in sirali if sirali.count(j) > 1})
            h("D1", "%s: alt adım paragrafları %s, beklenen 1 … %d sırayla (eksik %s, yinelenen %s)" % (kod, sirali, len(par) - 1, eks or "-",
                                                                                              yin or "-"))
        bas = hm.get(y + " is_") if hm is not None else R.ADIM_HAM[kod].get("is_")
        if bas != par[0]:
            h("D1", "%s: ana metin tam metnin ilk paragrafı değil" % kod)
        if hm is not None:
            n_ham = sum(1 for k in hm if k.startswith(y + " alt adım ") and k.endswith(" is_"))
            if n_ham != len(G):
                h("D1", "%s: kaynakta %d alt adım metni, sırada %d alt adım" % (kod, n_ham, len(G)))
        metin = []
        for n, g in enumerate(G):
            t = hm.get("%s alt adım %d is_" % (y, n + 1)) if hm is not None else g.get("is_")
            bek = "\n".join(par[j] for j in (g.get("paragraf") or ()) if 0 < j < len(par))
            if t != bek:
                i = next((i for i, (a, b) in enumerate(zip(t or "", bek)) if a != b), min(len(t or ""), len(bek)))
                h("D1", "%s alt adım %d (%s): metin kendi paragraflarıyla aynı değil (ilk fark %d. karakter: «%s» ↔ «%s»)" % (
                    kod, n + 1, g.get("ad"), i, (t or "")[max(0, i - 20):i + 30], bek[max(0, i - 20):i + 30]))
            metin.append(t or "")
        if "\n".join([bas or ""] + metin) != tam:
            h("D1", "%s: ana metin + alt adımlar (sırayla) adımın tam metniyle aynı değil (madde silinmiş, eklenmiş ya da yer değiştirmiş)" % kod)
        # D2, D3
        anilan = [_demet_kimlikleri(D.coz(t, []), kim) for t in metin]
        for n, g in enumerate(G):
            dm = tuple(g.get("demet") or ())
            ad = "%s alt adım %d (%s)" % (kod, n + 1, g.get("ad"))
            if not dm and not g.get("genel"):
                h("D2", "%s: demeti yok, \"genel\" işareti de yok" % ad)
            if dm and g.get("genel"):
                h("D2", "%s: \"genel\" işaretli ama demeti var %s" % (ad, list(dm)))
            for d in dm:
                if d not in gecerli:
                    h("D2", "%s: demet \"%s\" kayıttaki demet_sirasi'nda yok" % (ad, d))
                elif not any(demet.get(k) == d for k in anilan[n]):
                    h("D2", "%s: demet \"%s\" metinde geçen hiçbir kablonun kayıttaki demeti değil (%s)" % (
                        ad, d, ", ".join(sorted(anilan[n])) or "kimlik yok"))
        for k in sorted(set().union(*anilan) if anilan else set()):
            if not any(k in anilan[n] and demet.get(k) in (G[n].get("demet") or ()) for n in range(len(G))):
                h("D3", "%s: %s (kayıtta demet \"%s\") geçtiği alt adımların (%s) hiçbirinin demeti değil" % (
                    kod, k, demet.get(k), ", ".join("%d" % (n + 1) for n in range(len(G)) if k in anilan[n])))
        # D4
        oge = [("şema", s[3], tuple(s[4]), "sema") for s in R.SEMA if s[2] == kod]
        if yol_adim is None:
            h("D4", "%s: taban-analiz.json okunamadı, CAD kablo yollarının adımı bilinmiyor" % kod)
        else:
            oge += [("kablo yolu", "Kablo yolu %d: %s" % (no, R.KABLO_AD.get(no, ("", ""))[1]), tuple(_RKB.CAD_ESLEME.get(no, ())), "desen")
                    for no, a in sorted(yol_adim.items()) if a == kod]
        kullanilan = set()
        for tur, ad_o, kab, alan in oge:
            uy = [(n, x) for n, g in enumerate(G) for x in (g.get(alan) or ()) if x in ad_o]
            ns = sorted({n for n, x in uy})
            kullanilan |= {(n, alan, x) for n, x in uy}
            if len(ns) != 1:
                h("D4", "%s %s \"%s\": %s alt adımın desenine uyuyor (tam bir olmalı: %s)" % (
                    kod, tur, ad_o[:60], len(ns), ", ".join("%d" % (n + 1) for n in ns) or "hiçbiri"))
                continue
            n = ns[0]
            g = G[n]
            if not any(k in anilan[n] and demet.get(k) in (g.get("demet") or ()) for k in kab) and \
                    not any(x in (g.get("sema_ok") or {}) for n2, x in uy):
                h("D4", "%s %s \"%s\": alt adım %d kablolarından (%s) birini demetiyle anmıyor, sema_ok gerekçesi de yok" % (
                    kod, tur, ad_o[:60], n + 1, ", ".join(kab)))
        for n, g in enumerate(G):
            for alan in ("sema", "desen"):
                for x in g.get(alan) or ():
                    if (n, alan, x) not in kullanilan:
                        h("D4", "%s alt adım %d: %s deseni \"%s\" hiçbir şemaya / kablo yoluna uymuyor (bayat desen)" % (kod, n + 1, alan, x))
            for x in g.get("sema_ok") or {}:
                if x not in tuple(g.get("sema") or ()) + tuple(g.get("desen") or ()):
                    h("D4", "%s alt adım %d: sema_ok \"%s\" alt adımın desenlerinde yok" % (kod, n + 1, x))
        kablo = R.ADIM.get(kod, {}).get("kablo") or []
        secilen = {}
        for n, g in enumerate(G):
            for x in g.get("kablo_sec") or ():
                m = [i for i, t in enumerate(kablo) if x in t]
                if len(m) != 1:
                    h("D4", "%s alt adım %d: kablo_sec \"%s\" kablo listesinde %d maddeye uyuyor (tam bir olmalı)" % (kod, n + 1, x, len(m)))
                    continue
                secilen.setdefault(m[0], []).append(n)
                if not (_demet_kimlikleri(x, kim) & anilan[n]):
                    h("D4", "%s alt adım %d: kablo_sec \"%s\" kimliği alt adımın metninde geçmiyor" % (kod, n + 1, x))
        for i, ns in sorted(secilen.items()):
            if len(ns) > 1:
                h("D4", "%s kablo listesi maddesi %d: %d alt adımda gösteriliyor (bir kez basılmalı)" % (kod, i + 1, len(ns)))
        # D8 (P10.7b2e kısım 2, F10l-kare-inceleme 17.11 = 17.12): yeni parçası (desen) ve vurgusu (sema) olmayan alt adımın karesini
        # yalnız bakışı (kamera, saydam, odak) belirler; iki böyle alt adımın bakışı aynıysa kareleri aynıdır
        # P10.7b2e düzeltme turu 1 (F10m-kontrol N6): kamera 3 ondalığa yuvarlanır (1e-6 farkı aynı kare), saydam / odak sırasız küme
        bakis = {}
        for n, g in enumerate(G):
            if g.get("desen") or g.get("sema"):
                continue
            kam = g.get("kamera")
            if isinstance(kam, (list, tuple)):
                kam = tuple(round(float(v), 3) if isinstance(v, (int, float)) else v for v in kam)
            k = (repr(kam), tuple(sorted(map(str, g.get("saydam") or ()))), tuple(sorted(map(str, g.get("odak") or ()))))
            bakis.setdefault(k, []).append(n)
        for k, ns in sorted(bakis.items(), key=lambda x: x[1]):
            if len(ns) > 1:
                h("D8", "%s alt adım %s: yeni parça ve vurgu yok, bakış (kamera %s, saydam %s, odak %s) aynı: kareleri aynı olur" % (
                    kod, " / ".join("%d" % (n + 1) for n in ns), k[0], list(k[1]) or "-", list(k[2]) or "-"))
        bara_uc_denetle(R, kod, G, metin, T, h)                     # D6 (düzeltme turu 1, F10l-kontrol D1)
        ozet[kod] = dict(alt=len(G), kablo=len(set().union(*anilan)) if anilan else 0, oge=len(oge))
    gonderme_denetle(R, ham if ham is not None else kaynak_metinler(ham=True), h, **(gonderme or {}))   # D7 (F10l-kontrol D2)
    return dict(hata=hata, adim=ozet)


def kaynak_denetle():
    """FreeCAD'siz, veri üretmeden: rehber_metin.py kaynağında ASCII kalıntı, elektrik iddiaları ve zorunlu uyarılar (P10.7b1)."""
    m = kaynak_metinler()
    gor = arayuz_gorunen_metinler()                                # P10.7b2a: app.js / yazdir.html görünen dizgeleri, kol lejantı
    asc = ascii_kalinti(m + tablo_metinleri() + gor)               # S1: panelin tablodan gösterdiği metinler de
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
            for a in _alan_anahtarlari(p):
                alanlar[(p[1], a)] += "\n" + t
    zh = []
    zor = [dict(adim=k, uyari=ad) for k, d, ad in zorunlu_listesi(zh) if k in RM.ADIM and not re.search(d, adim[k])]
    zor += [dict(adim=k, uyari=ad + " (alan %s)" % alan) for k, alan, d, ad in zorunlu_alan_listesi(zh)
            if k in RM.ADIM and not re.search(d, alanlar[(k, alan)])]
    zor += sira_denetle(alanlar, zh)                                 # P10.7b2b: ZORUNLU_SIRA (F10i-kontrol-3 A4–A6)
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
    ty = teyit_denetle(ham)                                          # düzeltme turu 1 (F10i-kontrol A6): "kablajda teyit" ibaresi
    da = demet_alt_denetle(ham=ham)                                  # P10.7b2d-A: K1 / K2 demet alt adımları (D1–D4)
    return dict(ascii_kalinti=asc, elektrik=el, zorunlu_eksik=zor, zorunlu_veride=sorted(set(zor_disari)), metin=len(m),
                cad_metin=None if cad is None else len(cad), arayuz_metin=len(ara), arayuz_gorunen=len(gor), yasak=ya, yasak_affedilen=ya_ist,
                ciplak=cip, cozum_hata=coz, bozuk=boz, baglam=bag, kritik=kr, tamlik=tm, teyit=ty, demet_alt=da,
                kritik_sayi={b: len(v) for b, v in kg.items()},
                gecti=not asc and not el and not zor and not ya and not cip and not coz and cad is not None and not boz and not bag
                and not kr and not tm["hata"] and not ty and not da["hata"])


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
        print("kaynak denetimi: metin %d (+ CAD ad/kod %s, arayuz %d, ASCII'ye giren arayuz gorunen dizge %d), ascii kalinti %d, "
              "elektrik iddiasi %d, zorunlu uyari eksik %d "
              "(yalniz veride bakilan adim: %s), yasak %d (istisna %d), ciplak kritik sayi %d, cozulemeyen yer tutucu %d, "
              "bozuk yer tutucu %d, anahtar-baglam %d, onayli kritik girdi farki %d (kayitta: %s)" % (
            d["metin"], "YOK (montaj-analiz.json okunamadi)" if d["cad_metin"] is None else d["cad_metin"], d["arayuz_metin"],
            d["arayuz_gorunen"],
            len(d["ascii_kalinti"]), len(d["elektrik"]), len(d["zorunlu_eksik"]), ", ".join(d["zorunlu_veride"]) or "-",
            len(d["yasak"]), len(d["yasak_affedilen"]), len(d["ciplak"]), len(d["cozum_hata"]), len(d["bozuk"]), len(d["baglam"]),
            len(d["kritik"]), ", ".join("%s %d" % (b, n) for b, n in sorted(d["kritik_sayi"].items()))))
        for x in d["kritik"][:40]:
            print("  KRITIK %s %s %s\n      eski: %s\n      yeni: %s" % (x["tur"], x["bolum"], x["yer"], x["eski"] or "-", x["yeni"] or "-"))
        tm = d["tamlik"]
        print("tamlik (kayit -> rehber): taranan %d oge (%s), eksik %d, muaf %d; kablo talimat maddesinde %d / %d, rehberde anilan %d "
              "(talimatta olmayan: %s)" % (
            sum(tm["tarandi"].values()), ", ".join("%s %d" % (k, n) for k, n in sorted(tm["tarandi"].items())), len(tm["hata"]),
            len(tm["muaf"]), tm["kablo_talimat"], tm["kablo_toplam"], tm["kablo_anilan"], ", ".join(tm["kablo_yok"]) or "-"))
        for x in tm["muaf"]:
            print("  TAMLIK MUAF", x)
        for x in tm["hata"]:
            print("  TAMLIK", x)
        da = d["demet_alt"]
        print("demet alt adimlari (D1-D8): hata %d; %s" % (len(da["hata"]), ", ".join(
            "%s %d alt adim, %d kablo, %d sema / kablo yolu" % (k, v["alt"], v["kablo"], v["oge"]) for k, v in sorted(da["adim"].items()))))
        for x in da["hata"]:
            print("  DEMET %s %s" % x)
        print("kablajda teyit ibaresi eksik madde: %d" % len(d["teyit"]))
        for x in d["teyit"]:
            print("  TEYIT", x)
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
