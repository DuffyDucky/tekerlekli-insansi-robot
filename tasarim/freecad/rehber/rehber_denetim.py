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
import os, re, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, HERE)
import rehber_metin as RM                                          # noqa: E402

KISALTMA = {
    "AWG", "BNO", "BOM", "BTS", "CAD", "CSI", "DIN", "ESP", "GPIO", "HDMI", "ISO", "IBT", "JR", "LCD", "LED", "LM", "MOSFET", "NC", "PC",
    "PCA", "PETG", "PLA", "PT", "PVC", "QLED", "TVS", "USB", "VBUS", "VESA", "VHB", "WAGO", "XT", "XL", "CF", "TPU", "PWM", "EN", "IS",
    "DS", "MG", "SY", "ASW", "NP", "BE", "CP", "PAM", "UART", "IMU", "DC", "AC", "LIPO", "LFP", "PCB", "STEP", "SOL", "TOUCH",
    "IN", "OUT", "GND", "VCC", "VIN", "RGB", "SD", "OK", "ID", "XVF", "MAX", "IMAX", "HP", "CAPQLED", "AA", "AAA", "SMD", "NO",
    "FPC", "AI", "HAT", "KAPI", "ZZ", "RS", "NTC", "IP", "MCB", "SSR", "MP", "ABS", "NPT", "ISB", "NEMA", "DSP", "LPC", "MAH", "JQC",
    "BMS", "KAPAK", "IPS", "JGB", "LOW", "HIGH", "WROOM", "RESPEAKER", "MIC",
}
# Türkçe harfi olmayan doğru kelimeler ve teknik terimler (küçük harf). Yeni bir ASCII kelime ekrana girerse denetim "bilinmeyen"
# der: ya TR_EK'e karşılığı eklenir ya da gözden geçirilip buraya yazılır.
ASCII_TAMAM = set("""
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
zeminden zorlarsa
ama bantla banda beslenir besleme besler bekliyor birlikte boylar burca cam cama dahil dahili damar daldan dayamalar delik delikler
delikleri deliklerine deliklerini deliklerinin delikli delikte delikten demet demeti demetin demetine dev direkten dizi dolu duvara
duyulabilirlik elde emas gelen gerilim gider giden gidenlere hepsi hornun hornunda inenler inmesi iskeletinin jeti kablosunun
kabuklarla kabuktaki kama kameraya kapaklar kenarda kesik kutup lens lensi listede multimetreyle notlar notu oradan pedle power
sallanmadan servoya solundan soluna tabanda tabladaki tablaya tahmin takozuna takozunda teyidi tepe testte testten tipi touch
ucunda ucunun veri vidala yanaklar yap yasla yerine yerini yerleri profil yeni rehberi taslak sayfa
beslemez bitince depo diyodu direnciyle enerjili enerjisiz enerjisizken enerjiyi genel gerekmez ikinci kademesiyle kapasite kaynakla
katot kendi kes kontroller kutbunu madde multimetrenin teline tek tutar varsa yazan yeniden
enerji gerilimsiz sonu sonunda takozda tekerlekler verilmez yerden zaman
""".split())

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
    ("E3a", r"akım sınırlı tezgâh kaynağı", "SY8205 ölçümü akım sınırlı kaynakla"),
    ("E4", r"Touch VBUS", "Touch VBUS ölçümü"),
    ("E4", r"köprülenmez", "iki 5 V hattı köprülenmez"),
    ("K1", r"akü ayrık", "bağlarken akü ayrık"),
    ("K1", r"K1'de enerji verilmez", "K1'de enerjili ölçüm yok (tezgâhta)"),
    ("K1", r"köprülenmez", "mantar / ana anahtar köprülenmez"),
    ("F1", r"Bağlarken akü ayrık", "F1 bağlarken akü ayrık"),
    ("F1", r"İlk enerji \(F1 sonu\).*BTS EN = 0.*ön şarj", "F1 ilk enerji sırası"),
    ("K2", r"akü XT60 ayrık", "K2 enerjisiz"),
    ("K2", r"1N5819: anot hub \(Pi\)\s+tarafında, katot ESP32", "1N5819 yönü"),
    ("K2", r"regülatörü \(LM2577 \+ LM2596\) ekrana bağlanmadan", "göğüs regülatörü 12 V ayarı"),
    ("F3", r"regülatör çıkışını yeniden ölç", "göğüs 12 V fişten önce ölçüm"),
]


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
                                       + (a.get("not_") or []))
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
    zorunlu = [dict(adim=k, uyari=ad, var=bool(re.search(d, adim_metin[kod[k]]))) for k, d, ad in ZORUNLU]
    return dict(anma=anma, anmayan=[x for x in anma if not x["metinde"]], celiski=celiski, affedilen=affedilen,
                zorunlu=zorunlu, zorunlu_eksik=[x for x in zorunlu if not x["var"]])


def denetle(V, ek_metinler=()):
    m = gorunen_metinler(V)
    asc = ascii_kalinti(m + list(ek_metinler))
    gr = gruplama(V)
    tu = tutarlilik(V, m)
    return dict(ascii_kalinti=asc, ascii_kalinti_sayi=len(asc), gruplama_yanlis=len(gr["yanlis"]) + len(gr["eksik"]), gruplama=gr,
                tutarlilik_celiski=len(tu["celiski"]) + len(tu["anmayan"]), tutarlilik=tu,
                zorunlu_eksik=len(tu["zorunlu_eksik"]),
                metin_sayisi=dict(veri=len(m), tarayici=len(ek_metinler)),
                parca=len(V["parcalar"]), sema=len(V.get("semalar", [])),
                gecti=not asc and not gr["yanlis"] and not gr["eksik"] and not tu["celiski"] and not tu["anmayan"]
                and not tu["zorunlu_eksik"])


def ozet_yaz(d):
    print("denetim: ascii kalinti %d, gruplama yanlis %d (eski kural ayni veride %d satir), kafa/hoparlor/hub celiski %d, "
          "zorunlu uyari eksik %d / %d, baglamla affedilen %d; parca %d, sema %d" % (
        d["ascii_kalinti_sayi"], d["gruplama_yanlis"], d["gruplama"]["eski_kural_yanlis"], d["tutarlilik_celiski"], d["zorunlu_eksik"],
        len(d["tutarlilik"]["zorunlu"]), len(d["tutarlilik"]["affedilen"]), d["parca"], d["sema"]))
    for x in d["ascii_kalinti"][:60]:
        print("  ASCII %-18s %s%s" % (x["kelime"], x["ilk_yer"], " (sozlukte var)" if x["sozlukte"] else ""))
    for x in d["gruplama"]["yanlis"][:20] + d["gruplama"]["eksik"][:20]:
        print("  GRUP", x)
    for x in d["tutarlilik"]["celiski"][:20] + d["tutarlilik"]["anmayan"][:20] + d["tutarlilik"]["zorunlu_eksik"]:
        print("  TUTARLILIK", x)


if __name__ == "__main__":
    yol = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROBOT, "rehber", "veri", "rehber-veri.json")
    d = denetle(json.load(open(yol, encoding="utf-8")))
    ozet_yaz(d)
    sys.exit(0 if d["gecti"] else 1)
