# -*- coding: utf-8 -*-
"""F9c (P9.3): 1,58 m döngüsünün sonuç raporunu kaynaklardan üretir -> planlama/d158/sonuc-rapor.html

Yalnız okur; tek yazdığı dosya sonuc-rapor.html (ya da --cikti ile verilen yol). FreeCAD gerekmez, git yalnız okuma komutlarıyla (log, show) çağrılır.

    py -3 -B planlama/d158/F9c-uret.py            # raporu üret
    py -3 -B planlama/d158/F9c-uret.py --kuru     # yalnız özet bas, dosya yazma
    py -3 -B planlama/d158/F9c-uret.py --cikti YOL   # sonuc-rapor.html yerine YOL'a yaz (P10.9a; deneme üretimi)

Sayıların bağı (F9c-dogrula.py bunları yeniden hesaplar):
  data-j="dosya|anahtar|biçim"   JSON (ya da git:<commit>:dosya) değeri; anahtar nokta yolu, sonda #say = uzunluk,
                                 '=' ile başlayan anahtar hesaptır (maliyet: README / F9d-tarama.py ile aynı kural)
  data-h="ad"                    plan / karar kuyruğu / dosya sayımı (F9c-dogrula.py kendi ayrıştırmasıyla sayar)
  data-kaynak="dosya dosya"      elle yazılmış ya da kaynaktan alıntılanmış metin; içindeki her sayı bu dosyalardan
                                 en az birinde birebir geçmeli
Kaynaklar: planlama/dongu-158.md (§3 tablolar, §5 günlük), planlama/d158/karar-kuyrugu.md (Özet tablosu),
planlama/d158/regresyon.json (git: döngü başı) ve regresyon-son-kosu.json, README / demo ile aynı JSON'lar,
planlama/proje-plani.md (takvim; JSON karşılığı yok), planlama/d158/F9c-dusukler.json (madde 6), git log.
"""
import html
import importlib.util
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(BURASI, "..", ".."))
CIKTI = os.path.join(BURASI, "sonuc-rapor.html")

DONGU = "planlama/dongu-158.md"
KUYRUK = "planlama/d158/karar-kuyrugu.md"
BRIEF = "planlama/d158/F9c-brief.md"
PLAN = "planlama/proje-plani.md"
DUSUK = "planlama/d158/F9c-dusukler.json"
REG_SON = "planlama/d158/regresyon-son-kosu.json"
REG = "planlama/d158/regresyon.json"
LK = "tasarim/freecad/lale158/lale158-kontrol.json"
MA = "tasarim/freecad/montaj/montaj-analiz.json"
UI = "tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json"
BA = "tasarim/freecad/lale158/baski-analiz.json"
YB = "planlama/y2/Y2b-baski.json"
PT = "planlama/d158/F4c-partiler.json"
RK = "planlama/rehber/kontrol.json"
RV = "rehber/veri/rehber-veri.json"
ML = "planlama/maliyet.json"
SP = "planlama/d158/F8a-siparis.json"
DEMO = "tasarim/Robot-Tasarim-Demosu.html"
# P10.9c (F10 sonu): tam çakışma taraması, F10y kapanış günlüğü, bu paketin günlüğü (F10 tablosundaki Echo sırası)
CS = "tasarim/freecad/carpisma-sonuc.json"
F10Y = "planlama/d158/F10y-gunluk.md"
GUN = "planlama/d158/P109c-gunluk.md"
P109A, P109B = "planlama/d158/P109a-gunluk.md", "planlama/d158/P109b-gunluk.md"
# P10.8f (21.11): sayfa P10.8a–e ve kayıt eşitlemesinden sonra yenilendi; P10.8 satırı ve F10 tablosu bugünkü kayda göre
P108F = "planlama/d158/P108f-gunluk.md"
# P10.8f kayıt eşitlemesi (C, 21.11): bağımsız kontrol (K67 grubu gerekçesi § 2, açık işler § 10)
P108FK = "planlama/d158/P108f-kontrol.md"
# P10.8g kayıt eşitlemesi (C, 22.11): P10.8g günlüğü (K68 seçenekleri § 5, açıklar § 10) ve bağımsız kontrolü (K1–K6 § 4)
P108G, P108GK = "planlama/d158/P108g-gunluk.md", "planlama/d158/P108g-kontrol.md"
# Y0s kayıt eşitlemesi (C, 22.11): sahte ESP32 simülasyonu (döngü paketi değil; K69–K74 kaynağı)
Y0S, Y0SK = "planlama/d158/Y0s-gunluk.md", "planlama/d158/Y0s-kontrol.md"
EMOJI = "✅🟡⛔🔄⏳"


def yol(rel):
    return os.path.join(KOK, *rel.split("/"))


def oku(rel):
    with open(yol(rel), encoding="utf-8") as f:
        return f.read()


def js(rel):
    return json.loads(oku(rel))


def modul(ad, rel):
    spec = importlib.util.spec_from_file_location(ad, yol(rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T = modul("f9d_tarama", "planlama/d158/F9d-tarama.py")   # README ile aynı biçim ve maliyet kuralı


def git(*a):
    r = subprocess.run(["git", *a], cwd=KOK, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr.strip()))
    return r.stdout


# ------------------------------------------------------------------ biçim
def bicim(deger, b):
    """b: '0'..'3' ondalık (Türkçe), 'k2' = /1000 iki ondalık, 'i' tam sayı binlikli, 's' metin."""
    if b == "s":
        return str(deger)
    if b == "i":
        return T._tr(deger)
    if b.startswith("k"):
        return T._s(deger / 1000.0, int(b[1:]))
    return T._s(deger, int(b))


def coz(veri, anahtar):
    say = anahtar.endswith("#say")
    if say:
        anahtar = anahtar[:-4]
    d = veri
    for p in [x for x in anahtar.split(".") if x]:
        d = d[int(p)] if isinstance(d, list) else d[p]
    return len(d) if say else d


def maliyet_hesap(ad):
    md = js(ML)
    m = T._maliyet(md)
    if ad in m:
        return m[ad]
    if ad == "qled":
        q = [s for s in js(SP)["kalemler"] if s.get("ad") == 'Kafa ekranı 10,1" QLED'][0]["birincil"]["fiyat"]
        return (m["ara_elde"] + q) * (1 + md["pay"])
    raise KeyError(ad)


def jdeger(dosya, anahtar):
    if anahtar.startswith("="):
        return maliyet_hesap(anahtar[1:])
    if dosya.startswith("git:"):
        _, c, rel = dosya.split(":", 2)
        return coz(json.loads(git("show", "%s:%s" % (c, rel))), anahtar)
    if dosya == DEMO:
        m = re.search(r'<script id="kaynak"[^>]*>(.*?)</script>', oku(DEMO), re.S)
        return coz(json.loads(m.group(1)), anahtar)
    return coz(js(dosya), anahtar)


def J(dosya, anahtar, b="0", ek=""):
    v = jdeger(dosya, anahtar)
    return '<span data-j="%s|%s|%s">%s%s</span>' % (html.escape(dosya), html.escape(anahtar), b, html.escape(bicim(v, b)), ek)


def H(ad, deger):
    return '<span data-h="%s">%s</span>' % (ad, html.escape(str(deger)))


def md(metin):
    """Markdown parçası -> HTML: `kod`, **kalın**."""
    t = html.escape(metin, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t


def K(metin, *kaynak, etiket="span", sinif=""):
    s = ' class="%s"' % sinif if sinif else ""
    return '<%s%s data-kaynak="%s">%s</%s>' % (etiket, s, " ".join(kaynak), md(metin), etiket)


# ------------------------------------------------------------------ plan
def plan_paketleri():
    faz, fazlar, paket = None, [], []
    for i, l in enumerate(oku(DONGU).splitlines(), 1):
        m = re.match(r"### Faz (F\d+): (.*)", l)
        if m:
            faz = m.group(1)
            fazlar.append((faz, m.group(2).strip()))
            continue
        if l.startswith("## 4."):
            faz = None
        m = re.match(r"\| (P\d+\.\d+[a-z]?) \| ", l)   # P10.4b gibi harfli plan satırı da paket (P10.9a)
        if m and faz:
            h = [c.strip() for c in l.strip().strip("|").split(" | ")]
            durum = h[-1]
            em = next((c for c in durum if c in EMOJI), "?")
            paket.append(dict(kod=h[0], is_=h[1], kabul=h[2], durum=durum, emoji=em, faz=faz, satir=i))
    return fazlar, paket


def paket_kodu(a, b, harf, kodset):
    """P kodunu plan paketine indirger: harfli kod (P10.4b) planda paket ise kalır, değilse harfsiz (P4.5a -> P4.5, P10.7b2d -> P10.7)."""
    k = "P%s.%s" % (a, b)
    return k + harf if harf and kodset is not None and k + harf in kodset else k


def brief_etiketleri(kodset=None):
    """Fxx-brief.md başlığındaki P kodları: {'F1a': ['P1.2', ...]}; P4.5a -> P4.5; F10e -> P10.4b (planda paket)."""
    out = {}
    for ad in sorted(os.listdir(BURASI)):
        m = re.match(r"(F\d+[a-z]?)-brief\.md$", ad)
        if not m or m.group(1) == "F9c":
            continue
        with open(os.path.join(BURASI, ad), encoding="utf-8") as f:
            bas = f.readline()
        out[m.group(1)] = sorted({paket_kodu(a, b, h, kodset) for a, b, h in re.findall(r"P(\d+)\.(\d+)([a-z]?)", bas)})
    return out


# Brief'inde P kodu olmayan iş: F5b panoya ikinci toplu soru, P5.3 "Panoya bilgi + soru olarak gönder" (dongu-158.md §5:
# F5 C "pano #6 açıldı", F5b C "pano #7"). Bu tek eşleme elle; gerekçesi F9c-gunluk.md'de.
EK_ETIKET = {"F5": ["P5.3"], "F5b": ["P5.3"]}


def komitler():
    """Döngü commit'leri: F0 kayıt satırındaki en eski commit'ten HEAD'e."""
    satirlar = [l.split("\t", 1) for l in git("log", "--format=%h\t%s").splitlines() if l]
    hepsi = {h: s for h, s in satirlar}
    f0 = [l for l in oku(DONGU).splitlines() if "**F0 ✅**" in l][0]
    f0h = [h for h in re.findall(r"\b[0-9a-f]{7}\b", f0) if h in hepsi]
    sira = [h for h, _ in satirlar]
    bas = max(sira.index(h) for h in f0h)
    return [(h, hepsi[h]) for h in sira[: bas + 1]], hepsi


PUSH_SOL = re.compile(r"\b[0-9a-f]{7}\.\.(?=[0-9a-f]{7}\b)")   # "push A..B" aralığının sol ucu (F9c-dogrula.py ile aynı)


def kodlar(konu, kodset=None):
    k = set()
    for a, b, h, c in re.findall(r"P(\d+)\.(\d+)([a-z]?)(?:\s*[–-]\s*P\d+\.(\d+))?", konu):
        k.add(paket_kodu(a, b, h, kodset))
        if c:
            for x in range(int(b), int(c) + 1):
                k.add("P%s.%d" % (a, x))
    return k


def etiket(konu):
    m = re.search(r"\((F\d+[a-z]?)\)", konu) or re.match(r"Lale (?:158 )?(?:döngüsü: plan, )?(F\d+[a-z]?)\b", konu)
    return m.group(1) if m else None


def paket_komitleri(paket, etk):
    dongu = oku(DONGU).splitlines()
    kom, hepsi = komitler()
    harita = {p["kod"]: [] for p in paket}
    fazpaket = {}
    for p in paket:
        fazpaket.setdefault(p["faz"], []).append(p["kod"])
    hedef = lambda L: (etk.get(L, []) + EK_ETIKET.get(L, [])) or fazpaket.get(L, [L] if re.match(r"P\d+\.\d+[a-z]?$", L) else [])
    eksik = []
    for h, s in kom:
        ks = set(kodlar(s.split(": ", 1)[0], set(harita)))   # yalnız konu öneki; gövdedeki "(P10.7)" gibi göndermeler değil (P10.9a kontrolü B1)
        L = etiket(s)
        if L:
            ks |= set(hedef(L))
        for k in ks:
            if k in harita and h not in harita[k]:
                harita[k].append(h)
    # §5'te tek bir paket/faz başlığı taşıyan "✅" kayıt satırlarındaki commit'ler ve durum hücresindeki commit'ler
    for l in dongu:
        b = re.findall(r"\b(F\d+[a-z]?|P\d+\.\d+[a-z]?) ✅", l)
        if len(b) == 1 and "**%s ✅" % b[0] in l:
            # "**P10.7a ✅" gibi planda paket olmayan harfli başlık harfsiz pakete iner (P10.7); hash'ler sessizce düşmez (B8)
            b0 = paket_kodu(*re.match(r"P(\d+)\.(\d+)([a-z]?)", b[0]).groups(), set(harita)) if b[0].startswith("P") else b[0]
            # "push A..B": A bir önceki paketin son commit'i, bu satırın değil (B1)
            for h in re.findall(r"\b[0-9a-f]{7}\b", PUSH_SOL.sub("", l)):
                if h in hepsi:
                    hk = hedef(b0)
                    # Faz düzeyindeki satır (ör. "**F0 ✅**"): konu satırında faz etiketi geçmeyen commit fazın tüm paketlerine
                    # değil, yalnız ilk paketine bağlanır (F0: 8dcc4eb … 680b965 P0.1 sınıflandırma grupları; F9c-kontrol D-6).
                    if re.match(r"F\d+$", b[0]) and b[0] not in dict(kom).get(h, "") and hk:
                        hk = hk[:1]
                    for k in hk:
                        if k in harita and h not in harita[k]:
                            harita[k].append(h)
                elif re.search(r"\d", h):
                    eksik.append((b[0], h))
    for p in paket:
        for h in re.findall(r"\b[0-9a-f]{7}\b", p["durum"]):
            if h in hepsi:
                if h not in harita[p["kod"]]:
                    harita[p["kod"]].append(h)
            elif re.search(r"\d", h):
                eksik.append((p["kod"], h))
    sira = [h for h, _ in kom] + [h for h in hepsi if h not in dict(kom)]
    for k in harita:
        harita[k].sort(key=lambda h: sira.index(h), reverse=True)   # eskiden yeniye
    eslesmeyen = [(h, s) for h, s in kom if not any(h in v for v in harita.values())]
    return harita, eksik, eslesmeyen, kom


def raporlar(kod, etk):
    out = []
    for L in sorted(etk):
        if kod in etk[L] + EK_ETIKET.get(L, []):
            r = "%s-rapor.html" % L
            if os.path.exists(os.path.join(BURASI, r)):
                out.append(r)
    if kod in ("P9.3", "P10.9"):   # P10.9: faz sonu yenilemesi aynı sayfa
        out.append("sonuc-rapor.html")
    return out


# ------------------------------------------------------------------ karar kuyruğu
def kararlar():
    out = []
    for l in oku(KUYRUK).splitlines():
        m = re.match(r"\| (K\d+) \| (.+) \|$", l)
        if m:
            h = [c.strip() for c in l.strip().strip("|").split(" | ")]
            if len(h) == 5:
                out.append(dict(k=h[0], karar=h[1], durum=h[2], varsayilan=h[3], bloke=h[4], acik="**açık**" in h[2]))
    return out


def karar_faz(k):
    """Kural: Durum hücresindeki paket etiketi (F8a -> F8, F10b -> F10); yoksa Bloke hücresindeki ilk P kodunun fazı; yoksa Durum
    hücresindeki ilk P kodunun fazı (P10.9a: K62 "P10.7b1"); yoksa F0."""
    m = (re.search(r"\bF(\d+)[a-z]?\b", k["durum"]) or re.search(r"\bP(\d+)\.\d", k["bloke"])
         or re.search(r"\bP(\d+)\.\d", k["durum"]))
    return "F" + m.group(1) if m else "F0"


# Özet tablosunda "Kayıtta yok" yazan maddelerde gövdedeki öneri (karar-kuyrugu.md madde gövdesi, birebir; F9c-kontrol D-5)
VARSAYILAN_EK = {
    "K32": "; F8a önerisi (gövde): alınacaksa S'nin ilk partisinde; stok 1'e düşerse öne alınsın",
    "K36": "; F8a önerisi (gövde): \"ikinci satıcı ya da adet düşürme\"",
    "K45": "; gövde: A'nın taslağı a ile b arasında bırakıyor",
}

# Aciliyet önerisi (F9c A'nın önerisi; karar değil). Gerekçeler karar kuyruğu ve takvimden.
GRUP_AD = {"A": "Sipariş ya da elektrik güvenliği öncesi", "B": "Montaj öncesi (ilgili adımdan ya da kolların ilk hareketinden önce)",
           "C": "Sonra karar verilebilir"}
GRUP = {
    "K4": ("A", "Sipariş listesine koşullu kalem olarak girip girmeyeceği S'den önce belli olmalı."),
    "K9": ("A", "Servo değişimi seçilirse kol servoları siparişte değişir; 100 g sınırı seçilirse sipariş aynı kalır."),
    "K11": ("A", "Elektrik güvenliği: acil stopta göğüs ekranının enerjili kalıp kalmayacağı ve regülatör / 2 A sigorta yeri buna bağlı."),
    "K12": ("A", "30 mm fan seçilirse sipariş satırı eklenir; yarıklar kalırsa sipariş değişmez."),
    "K27": ("A", "Bütçe farkının hangi listeye göre hesaplanacağı K28'i ve sipariş onayını bekletiyor."),
    "K28": ("A", "Sipariş onayı (S = 16.11) bu karara bağlı; kritik yolun ilk kapısı."),
    "K29": ("A", "Durum A takvimi erken kupon alımını bu hafta istiyor; Parti 0 ve Parti 1 buna bağlı."),
    "K30": ("A", "Akü stok 1 ve 7 gün tedarik; taban adım 9 akü ister."),
    "K31": ("A", "Erken alımdaki insert varyantı; Parti 0 kupon C bunu dener."),
    "K32": ("A", "Kafa ekranı satın alınırsa sipariş toplamı ve K28 farkı değişir."),
    "K33": ("A", "M6×16 stoku yetmiyor; sipariş satırının satıcısı ve malzemesi seçilmeli."),
    "K34": ("A", "Baskı hizmeti teklifi S'den önce; K28 toplamını etkiler."),
    "K35": ("A", "Onaylı olmayan satıcıların listede nasıl gideceği sipariş biçimini belirler."),
    "K36": ("A", "PAKET A siparişi stok yetmediği için bekliyor."),
    "K37": ("A", "Varsayılan siparişte (S) yeniden bakmak; karar o gün gerekir."),
    "K42": ("A", "Filament satırı S siparişinde; PETG-CF 1,5 kg yetmiyor."),
    "K43": ("A", "Erken alımdaki insert adedi bu karara bağlı (K29 ile birlikte)."),
    "K50": ("A", "Elektrik güvenliği: ilk şarjdan önce; konnektör seçimi sipariş satırını değiştirir."),
    "K51": ("A", "Elektrik güvenliği: Pi hattının aşırı gerilim koruması; model ve BOM 1 adet eksik (maliyette 2)."),
    "K52": ("A", "Elektrik güvenliği: göğüs dalının sigortası ve regülatörü modelde yok; yeri K11 ile birlikte belirlenir."),
    "K1": ("B", "Sipariş paketi varsayılanla K1'siz verilebiliyor; hub ve kablo montajından önce Efe'nin yanıtı gerekir."),
    "K2": ("B", "Kafa parçaları (Parti 3) basılmadan önce; tilt payı ve regresyon tabanı bu kararla yenilenir."),
    "K6": ("B", "Hoparlör kabı Parti 1 sonunda basılır; varsayılan zaten ölçümden sonra yeniden bakmak."),
    "K10": ("B", "Kafa kablolamasından (K2 adımı) önce; ölçüm T4 ile."),
    "K13": ("B", "Yalnız \"görünsün\" seçilirse baskı parçası değişir; kafa baskısından önce."),
    "K14": ("B", "Boyun demeti kablolamasından önce Efe teyidi."),
    "K38": ("B", "Kolların ilk hareketinden önce yazılımda olmalı (S2 alt bölge hız sınırı)."),
    "K39": ("B", "Omuz montajından önce; DS3235 düşme ölçümü servo gelince."),
    "K40": ("B", "Horn takılışı omuz montajında; sınır metni eklem sınırı dosyasına."),
    "K41": ("B", "Kalibrasyondan önce kod aralığı CAD ile aynı olmalı."),
    "K44": ("B", "Eklem sınırı dosyası kod/'a kollar kalibre edilmeden yazılmalı (Efe'ye bilgi)."),
    "K45": ("B", "K38'i sayısallaştırır; kolların ilk hareketinden önce."),
    "K46": ("B", "Parti 0 kuponundan sonra, Parti 1–2 dilimlemesinden önce."),
    "K3": ("B", "Güvenlik sınırı: elde yükle rampa payı 1,5'in altına iniyor; kolların yüklü ilk hareketinden önce belli olmalı."),
    "K7": ("C", "Yalnız ifade (yer kapandı); belge dilini etkiler."),
    "K18": ("C", "İzlenmeyen klasör; dışlama kararı depo temizliğiyle birlikte."),
    "K19": ("C", "İzlenmeyen klasör; dışlama kararı depo temizliğiyle birlikte."),
    "K20": ("C", "İzlenmeyen klasör; dışlama kararı depo temizliğiyle birlikte."),
    "K21": ("C", "Satıcı dosyaları izlenmiyor; .gitignore kararıyla birlikte."),
    "K22": ("C", "İzlenmeyen klasör; içindeki takma ad satırı girmeden temizlenmeli."),
    "K23": ("C", "Ara çıktılar; F6a'nın yeniden ürettiği 13 kabuk PNG'si de buna bağlı."),
    "K24": ("C", "İzlenmeyen rapor; G4 commit'inden önce temizlenmeli."),
    "K25": ("C", "Herkese açık dalda duruyor; main / Pages birleştirmesinden önce karar önerilir."),
    "K26": ("C", "Hesap adı bağlantılarda; main / Pages birleştirmesinden önce karar önerilir."),
    "K47": ("C", "Bir sonraki rehber turunun git add listesinden önce; depo büyümesi."),
    "K48": ("C", "Silme Ahmet'in onayıyla; git status temizliği."),
    "K49": ("C", "K18–K24 ile birlikte; .gitignore."),
    # F10'da açılanlar: P10.9a ön paketinin TASLAK önerisi (karar değil; orkestratör P10.9'da onaylar ya da değiştirir).
    # Gerekçeler karar-kuyrugu.md Özet tablosunun "Beklettiği" hücresinden; P10.9a-gunluk.md § 3.
    "K53": ("A", "Elektronik katının lazer kesim dosyası bu karara bağlı; lazer teklifi sipariş öncesi."),
    "K54": ("B", "Kafa iskeleti baskısından (Parti kuponu) önce; rehber E3 notu."),
    "K55": ("B", "Kabuk baskısından (Parti kuponu) önce; rehber F1 / F3 / F4 takma metni."),
    # P10.7b2h (F10q-kontrol): K60 17.11'de kapandı (P10.9b); metin K64 / K65 biçiminde güncellendi (yalnız açık kararlarda gösterilir)
    "K60": ("A", "Elektrik güvenliği: elde acil stop; kapandı 17.11, A + köprülü klemens şimdi (demoda mantarın yanında bir kişi)."),
    # K61 B → A (P10.9a kontrolü B4, orkestratör kararı): seçenek a kalemi siparişten çıkarır; K12 ve K32 ile aynı ölçüt.
    "K61": ("A", "Seçenek a kalemi siparişten çıkarır (Bas-konuş düğmesi 76,24 TL); karar S = 16.11 siparişinden önce, b seçilirse kablo ve yer P10.7b kablajında."),
    "K62": ("C", "Kayıt; döngü kuralının yorumu (sonraki paketlerin tur sayımı)."),
    # P10.7b2e kısım 2 (F10m-gunluk.md § 11): K64 kuyruğa açık girdiğinde GRUP'ta yoktu (KeyError 'K64'); ikisi de 16.11'de kapandı
    "K64": ("B", "Fiziksel montajdan önce (B5a güç paneli, K1 17.1 iki bara); kapandı 16.11, a: tutucu CAD paketinde basılır."),
    "K65": ("B", "K1 kablajından ve ilk sürüşten önce (sağ / sol tanımı, kurulum testi); kapandı 16.11, yazılım düzeltmesi Efe'de."),
    # P10.7b2f kısım 2 (F10n-gunluk.md § 8): K66 kuyruğa kapalı girdi; açık olsaydı KeyError vermesin diye (K64 / K65 ile aynı)
    "K66": ("A", "Elektrik güvenliği ve sipariş: ESP32 VIN'e seri 1N5819 (+1 adet); kapandı 16.11, tezgâh denemesine bağlı kabul."),
    # P10.8f (P108f-gunluk.md § 2): K67 21.11 kayıt eşitlemesinde açık girdi, GRUP'ta yoktu (KeyError 'K67', sayfa yeniden üretilemiyordu).
    # Grup A (alım sorusu, GRUP_AD["A"] tanımı): P10.8f taslağı, orkestratör 21.11'de onayladı (P108f-kontrol.md § 2 gerekçesiyle).
    "K67": ("A", "Sipariş listesindeki kart burcu adedi (48; CAD 52): sipariş verilmediyse siparişten önce, verildiyse eksik burçlar ayrı alınır."),
    # P10.8g kayıt eşitlemesi (C, 22.11): K68 kuyruğa açık girdi (KeyError vermesin diye K67 gibi). Grup C TASLAK (yalnız bu sayfanın
    # denetimi; sipariş ve montajı etkilemez, GRUP_AD["C"] tanımı); orkestratör onaylar ya da değiştirir.
    "K68": ("C", "Yalnız bu sayfanın denetimi (F9c'nin yapısal 3 hatası); sipariş ve montajı etkilemez. Onaya kadar commit'ten sonra 3 hata kayıtta açık."),
    # Y0s kayıt eşitlemesi (C, 22.11): K69–K74 kuyruğa açık girdi (simülasyon bulguları; KeyError vermesin diye). Gruplar TASLAK
    # (GRUP_AD tanımlarına göre); orkestratör onaylar ya da değiştirir.
    "K69": ("C", "Odometri doğruluğu (360°'de −5,0°); iz ölçümüyle karar, sipariş ve montajı etkilemez."),
    "K70": ("B", "Sonarla durma / yavaşlama ilk sürüşten önce belli olmalı (firmware'e eklenecek mi, protokolden mi çıkacak)."),
    "K71": ("B", "Kolların ilk hareketinden önce: bağımlı servo sınırında komut kırpılacak mı reddedilecek mi."),
    "K72": ("A", "Arka algılayıcı seçilirse sipariş listesine girer; geri sürüş sınırı seçilirse sipariş aynı kalır."),
    "K73": ("B", "İlk sürüşten önce: engel yakınında yerinde dönüş ve dar açıyla yaklaşmada köşe çarpması."),
    "K74": ("B", "İlk sürüşten önce, K70 ile birlikte: 30–35 cm arasında sürünme istenen davranış mı."),
}


# ------------------------------------------------------------------ metinler (her sayı kaynağında birebir)
PAKET_SONUC = {
    "P0.1": ("Commitlenmemiş dosyalar 9 commit grubuna ayrıldı; bekleyen gruplar G4, G6, G7, G9 karar kuyruğunda.", [DONGU]),
    "P0.2": ("Karar kuyruğu 23 maddeyle açıldı (18 açık); döngü sonunda 52 madde, 47 açık (K51–K52 F9c düzeltmesinde).", [DONGU, KUYRUK]),
    "P0.3": ("`regresyon.py` korunan 10 değeri toplar; ilk koşu 10/10 aynı.", [DONGU]),
    "P1.1": ("Akü 3,0 kg modelde; yüksüz rampa payı 1,517 → 1,519.", [DONGU]),
    "P1.2": ("Modelde ses yükseltici tek (PAM8403 + USB ses kartı); kafa içi çakışma 0.", [DONGU]),
    "P1.3": ("AI HAT+ için iki seçenek çakışma 0; seçim K2'de, tilt payı 3,64 → 3,30 (a) / 3,37 (b).", [DONGU]),
    "P1.4": ("Kablo tüpü çakışması port girintisi varsayımıyla 0 (HDMI 416,4 / 12 V 280,2 / USB 173,6 mm³); ekran gelince yeniden ölçülecek.", [DONGU]),
    "P1.5": ("Kabuk \"Wire is not closed\" 16 → 0 (kesit düzlemi 0,05 mm kaydırıldı).", [DONGU]),
    "P1.6": ("Eski betikler (125 cm, StopIteration) 158'e uyarlandı; ikisi hatasız koşuyor.", [DONGU]),
    "P1.7": ("Hoparlör kelepçesi 4 g, desteksiz, çakışma 0.", [DONGU]),
    "P2.1": ("Omuz durdurucu dişi: temas S2 4,30°, S2 5°'te 0,344 mm boşluk, kol–kabuk 0.", [DONGU]),
    "P2.2": ("Omuz taraması 20261109-033441 tek koşu, 9 bölüm rc 0; omuz 3 sa 25 dk.", [DONGU]),
    "P3.1": ("Her elde 50 g'de rampa payı 1,499 (< 1,5); öneri ≤ 100 g/el düzde (K3).", [DONGU]),
    "P3.2": ("500 g'de S1/S2 0,97, dirsek 0,74; AI HAT+ ile yüksüz rampa 1,515.", [DONGU]),
    "P4.1": ("`elektrik.md` 1,58'e: hub gövdede, boyun demeti 5 kablo; 7 belge güncellendi.", [DONGU]),
    "P4.2": ("11 fiyatsız aday toplam dışı; maliyet genel 102.919,71, koşullu dahil 108.208,77 TL.", [DONGU]),
    "P4.3": ("Baskı listesi 72 parça, 7,60–7,66 kg (F4c); F6b tek analizinden sonra 7.668,9–7.726,7 g.", [DONGU]),
    "P4.4": ("README, `OZET.md` ve `proje-plani.md` 1,58 m'ye; \"1,65 m ana tasarım\" yalnız tarihçede.", [DONGU]),
    "P4.5": ("P4.5a 63 dosyada yalnız ad satırlarını temizledi; kalan izlenen 3 dosya (6 satır) K25, K26 ve K44'e bağlı.", [DONGU, "planlama/d158/F9d-rapor.html"]),
    "P5.1": ("10 servoluk kanal tablosu (yeni kanallar 6–9); kod↔CAD 11 çelişki.", [DONGU]),
    "P5.2": ("Kablo kuralı notu 4 soruyla; pano mesajının son hâli 1.720 karakter.", [DONGU, "planlama/d158/F5-gunluk.md"]),
    "P5.3": ("Pano #6 (10 servo, kablo kuralı) ve #7 (güvenlik ve ses) açıldı, #5 ile birlikte Efe'nin yanıtı bekleniyor.", [DONGU]),
    "P6.1": ("Tam tarama 20261109-084522 tek koşu 0; diş kökü r 1,5; 2 düzeltme turu.", [DONGU]),
    "P6.2": ("Tek analiz 62 tür / 72 adet; kapak 19.667,7 sahte → 5,01 mm²; 7,67–7,73 kg, 160–161 sa.", [DONGU]),
    "P7.1": ("50 adım, 1192 parça tek adımda, konsol 0; 1 düzeltme turu.", [DONGU]),
    "P7.2": ("Yazdırılabilir rehber PDF 50 sayfa, elektrik güvenliği O-1…O-4; 2 düzeltme turu.", [DONGU]),
    "P7.3": ("İlk enerji iki aşamalı; yasak talimat denetimi 43/43, PDF 53 sayfa ≥ 8,1 pt.", [DONGU]),
    "P7.4": ("6 düşük kapandı, şarj girişi uyarısı; denetim 36/36 + 15/15, PDF 54 ≥ 8,1 pt.", [DONGU]),
    "P8.1": ("`maliyet.json` 102.919,71 → 118.666,22 TL; kararlar K27–K37.", [DONGU]),
    "P8.2": ("Parti 1–4: 27/25/9/11 parça; Parti 0 kuponları ≈ 7,3 sa.", [DONGU]),
    "P8.3": ("Ekip için 9 ölçüm ve test kâğıdı (T1–T9); 2 düzeltme turu.", [DONGU, "planlama/d158/F8c-rapor.html"]),
    "P8.4": ("Ek test kâğıtları T10–T13 ve T1/T4 ekleri; GEÇMEZ → 2 tur → GEÇER.", [DONGU]),
    "P9.1": ("Sipariş gününe göre takvim: S = 16.11 + erken alımla demo 10.01; yoksa 20–24.01.", [DONGU]),
    "P9.2": ("Demo 127 JSON anahtarından; 14 karar \"karar bekliyor\"; maliyet 118.666,22 TL.", [DONGU]),
    "P9.4": ("Yerel kullanıcı yolu 48 → 4 satır, yazılabilir alanda 0; README 38 satır = JSON; K47–K49.", [DONGU]),
    # F10: P10.9a TASLAĞI, kaynak dongu-158.md §3 F10 tablosunun Durum hücreleri (16.11 02:39 hâli). Açık paketler "Açık" diye
    # başlar; faz sonu (P10.9) bu satırları günceller. Kalıp ve gerekçe P109a-gunluk.md § 4.
    "P10.1": ("Seçim vurgusu, öncekiler yarı saydam, küçük görünüm, internetsiz açılma; 1 düzeltme turu (yazdırma kareleri 19/50 boştu → 50/50).", [DONGU]),
    # P10.7b2g kapanışı: K53 17.11'de kapandı (P10.9b; a + iii, çentik); model değişikliği sonraki tam taramalı CAD paketinde
    # P10.9c düzeltme turu 1 (orkestratör kararı, Echo, geri alınabilir): P10.2 ✅ 19.11; çentik kabulün dört maddesini sağlıyor
    "P10.2": ("Kapandı 19.11 (orkestratör kararı, Echo): K53 a çentiği P10.7b2j'de modelde; iniş boyunca ortak hacim 0, en küçük boşluk "
              "0,5 mm, taban içi çakışma 0, korunan değerler GEÇER. Girişim önce 3,13 mm³, taşma 0,425 mm idi. b2j'deki parça artışı K51 ve "
              "K64'ten, çentikten değil; burç 2'nin oturması ayrı iş (P10.8 satırında; P10.8d'de kapandı).", [DONGU, "planlama/d158/F10s-gunluk.md"]),
    "P10.3": ("E4 sırası, E3 625ZZ + pim, kalıcı sıra denetimi; 1 düzeltme turu (E3 \"geometrik kilitli\" sonucu yanlıştı); K54 sıfır boşluk.", [DONGU]),
    "P10.4": ("Kabuk adımları alt adımlara bölündü; açık 34 / zor 8 / anlaşılmıyor 0; 1 düzeltme turu (34 somun yanlış yerde); K55 bindirme dilleri.", [DONGU]),
    "P10.4b": ("Gerçek parça rengi, bağlandığı yer vurgusu, cıvata yeri işaretleri; 1 düzeltme turu, ikinci kontrol GEÇER; açık 40 / zor 2.", [DONGU]),
    "P10.5": ("Kol içi kablo yolu rehberde; 2 düzeltme turu, üçüncü bakış GEÇER; 28 şema, alt adım 71, PDF 75 sayfa.", [DONGU]),
    "P10.5b": ("K56 + K57 montaj sırası rehberde; uçuş istisnası 20 → 16, çarpışan 0, PDF 75 sayfa; K56, K57 kapandı.", [DONGU]),
    "P10.6": ("ESP32 pin haritası kararı K58 (`pin-haritasi.md` sürüm 3); üç bağımsız kontrol, üçüncüsü GEÇER; pano #8 mesajını Ahmet gönderecek.", [DONGU]),
    # Kalan: plandaki "Sıradaki: P10.7b2" listesinden b2a–b2c'nin kapattıkları çıkarıldı (P10.9a kontrolü B3);
    # b2d 78d160d ile kapandı, "Sürüyor" listesinden kapalılara geçti (P10.9a commit turu); b2e b5fc255 ile kapandı, K52 kuyrukta
    # kapalı (P10.7b2f bakım; F10n-gunluk.md)
    # P10.9c düzeltme turu 1 (orkestratör kararı, Echo, geri alınabilir): P10.7 ✅ 19.11; "Kalan" adlarıyla P10.8 satırına devredildi.
    # G19 / G20 / G24 / G26 maddesi çıktı: P10.7b2b'de (15.11) eşleme dişleri onaysız yakalanıyor (P109c-kontrol O1).
    "P10.7": ("Kapandı 19.11 (orkestratör kararı, Echo). Kapalı alt paketler: P10.7a (74 kablo tek kaynakta, `kablolar.json`; 16.11 "
              "sipariş listesi genel 120.852,43 TL), "
              "P10.7b1, P10.7b2a (74 / 74 kablo talimatta, PDF 80 sayfa), P10.7b2b, P10.7b2c, P10.7b2d (K1 / K2 demet alt adımları, PDF 84 sayfa), "
              "P10.7b2e (K52 a, K64 a, sağ / sol K65, kare düzeltmeleri; PDF 86 sayfa), "
              "P10.7b2f (Kablo yolu 12 gerilemesi, uç etiketleri; kayıt düzeltmeleri, VIN'e seri Schottky K66), "
              "P10.7b2g (boyun tüneli deneme parçası; rehberde K2 alt adım 5'e bağlandı). "
              "P10.7b2h (17.11 kararlarının rehber metni: K40, K50 b, K51, K55, K60). "
              "P10.7b2i (yol 9 eski kısmı rehberde kırpıldı, U06 şeması ESP32 portuna yeniden çizildi, U06 boyu 1.560), "
              "P10.7b2j (K2 a boss, K53 a çentik, K51 a TVS, K64 a iki bara tutucusu ve dokuz saplama; USB ses kartı modelden çıktı; "
              "tam tarama eklem aralığında 0 çakışma), P10.7b2k (rehber b2j CAD'ine uyduruldu; PDF 87 sayfa). "
              "Devredilen (P10.8 satırına, adlarıyla): kablo boylarının ölçümü, CAD kablo yolu 10 / 11 / 12, göğüs regülatörü kartının "
              "zarfı, K31 insert boyu, rehberin açık işleri.", [DONGU]),
    # P10.9c düzeltme turu 1: P10.7'nin "Kalan"ı ve parça bekleyen işler bu satırda adlarıyla (plan P10.8 Durum hücresiyle aynı)
    # P10.8f (P108f-gunluk.md § 2): P10.8a–e ve kayıt eşitlemesinden sonra; parça beklemeyen işlerin kapananları çıktı, kalanlar adlarıyla
    # (plan P10.8 Durum hücresi ve kuyruğun "P10.8d / P10.8e kapanışından açık iş" bölümüyle aynı). "Kapalı alt paketler:" kalıbı
    # kullanılmadı: P10.8a planda kapalı yazılmıyor (kupon dosyaları hazır, basılmadı)
    # P10.8f kayıt eşitlemesi (C, 21.11; P108f-kontrol.md § 10 N2): "iki yeni kartın gerçek ölçüsü ve burç / vida boyu" P10.8d'de
    # (21.11) doğdu, "Devralınan (19.11)" listesinden kendi başlığına taşındı
    "P10.8": ("Açık: ayrıntılı satın alınan parça modelleri ve fotoğraf kartı parçalar gelince. Parça beklemeyen işler (19.–21.11): "
              "P10.8a kupon dosyaları (hazır, basılmadı), P10.8b–e rehber ve CAD açıkları (kablo yolu 10, 11 ve 12, burç 2, acil stop "
              "düğüm kartı ve dağıtım kartı C modelde, 16 şema tarandı, dikiş ölçümü, 17.11 ve 32.1 kareleri), P10.8f bu sayfanın "
              "yenilemesi ve 17.4 / 17.10 / B5a kareleri, P10.8g 17.1 / 17.5 saplama numaraları, basılı 17.11 şema notu ve "
              "PDF'te parça etiketi yazısı (bu sayfanın yapısal 3 hatası karar oldu: K68). P10.8d'den (21.11), kartlar gelince: iki yeni kartın gerçek ölçüsü ve "
              "burç / vida boyu. Devralınan (19.11), parça ya da ölçüm "
              "bekleyen: kablo boylarının ölçümü, D24V50F5 pin kenarı, ESP32 DevKit portu ve yönü (180° ters kart denetimde yakalanmaz; "
              "ters takılırsa ilk enerjide 5 V bir GPIO pinine gelir), PC817 çıkış jumper'ı, göğüs regülatörü kartının ürünü ve ölçüsü, "
              "RV 5.5 pabuç kalınlığı, M5 bara saplaması başı, kabuk ve etek takılıyken bara somunlarına erişim, boyun tüneli fiş "
              "denemesi, masa denemeleri KT1–KT7 ve K66 tezgâh denemesi, KT2'den sonra AU1 / AU2 ses şeması, fiş boyları ve talimat ↔ "
              "kayıt boyları, G07 bölücü dirençlerinin toleransı; sonraki tam "
              "taramalı CAD paketinde: göğüs regülatörü kartının zarfı ve yeri, K31 insert boyu, CAD kablo yolu 6'nın dağıtım kartı C'ye "
              "inmesi, kafa giriş kartı ve konnektör yerleri (TAHMİN), geniş `TABAN_DISI_BOLGE`, tam çakışma taramasının parça "
              "modellerinden sonra yeniden koşusu. "
              "P10.7b'nin öbür açık işleri kuyruğun \"Karar değil, iş\" bölümünde izlenir. Önerilen sıra (Echo kararı, geri alınabilir) bu "
              "sayfanın F10 tablosunda.", [DONGU, GUN, KUYRUK, P108F, P108FK, P108G]),
    # P10.9c düzeltme turu 1 (D4): P10.9 metni plan durumundan seçilir (commit'te eskiyecek "commit bekliyor" ifadesi yok);
    # kapalı metin uret() içinde (P10_9_KAPALI)
    "P10.9": ("Açık: bu sayfanın F10 yenilemesi (P10.9c, 19.11; günlük `P109c-gunluk.md`); plan durumu kapanınca sayfa yeniden üretilir. "
              "Ön paketler: P10.9a üretici ve denetimi iki basamaklı faza açtı; P10.9b 17.11 kararlarını kuyruğa işledi (22 kapandı).",
              [DONGU, P109A, P109B, GUN]),
}
P10_9_KAPALI = ("Bu sayfa, F10'un faz sonu yenilemesi (P10.9c, 19.11; günlük `P109c-gunluk.md`). Ön paketler: P10.9a üretici ve denetimi "
                "iki basamaklı faza açtı; P10.9b 17.11 kararlarını kuyruğa işledi (22 kapandı).", [DONGU, P109A, P109B, GUN])

FAZ_SONUC = {
    "F0": ("Zemin: 9 commit grubu, karar kuyruğu, korunan 10 değeri toplayan regresyon betiği.", [DONGU]),
    "F1": ("Kafa ve gövde 1,58 m'de tutarlı (akü 3,0 kg, rampa 1,519); P1.4 port girintisi varsayımıyla koşullu.", [DONGU]),
    "F2": ("Omuz durdurucu (temas 4,30°) ve omuz taraması, çakışma 0.", [DONGU]),
    "F3": ("Elde yük önerisi ≤ 100 g/el düzde; 500 g'de dirsek payı 0,74.", [DONGU]),
    "F4": ("Elektrik, belgeler ve baskı listesi (72 parça) 1,58 m'de; takma ad temizliğinin kalan 3 dosyası karara bağlı.", [DONGU]),
    "F5": ("10 servo kanal önerisi, kod↔CAD 11 çelişki; pano #5, #6, #7 Efe'de.", [DONGU]),
    "F6": ("Tam tarama tek koşu 0 çakışma; tek baskı analizi 62 tür / 72 adet.", [DONGU]),
    "F7": ("3B rehber 50 adım / 1192 parça; yazdırılabilir PDF 54 sayfa, elektrik güvenliği denetimi.", [DONGU]),
    "F8": ("Sipariş paketi 136 satır, baskı partileri, T1–T13 test kâğıtları; sipariş verilmedi.", [DONGU]),
    "F9": ("Takvim: S = 16.11 yalnız durum A'da sığar (bir hafta tampon); demo 127 anahtar, depo temizliği; bu rapor son paket.", [PLAN, DONGU]),
    # P10.9c düzeltme turu 1: P10.2 ve P10.7 kapandı (19.11); F10 cümlesi uret() içinde plandaki açık paketlerden tamamlanır
    "F10": ("P10.7'nin a, b1, b2a, b2b, b2c, b2d, b2e, b2f, b2g, b2h, "
            "b2i, b2j, b2k alt paketleri.", [DONGU]),
}

# P10.9c (F10 sonu) kayıt notları; F9 sonu notları (TUTARSIZ) tarihî, olduğu gibi altında
TUTARSIZ_F10 = [
    ("Plan kaydı (P10.9c, Echo kararı, geri alınabilir): P10.7b2j ve P10.7b2k kapanışları `dongu-158.md` P10.7 hücresine işlendi. F10y "
     "kapanışı planı güncellememişti; üretici alt paketleri plandan okuduğu için bu iki paket sayfada görünmüyordu.", [DONGU, F10Y, GUN]),
    ("P10.2 19.11'de kapandı (P10.9c düzeltme turu 1, orkestratör kararı (Echo), geri alınabilir): K53 a çentiği kabulün dört maddesini "
     "sağlıyor (iniş boyunca ortak hacim 0, en küçük boşluk 0,5 mm, taban içi çakışma 0, korunan değerler GEÇER); b2j'deki parça artışı "
     "K51 ve K64'ten, çentikten değil.", [DONGU, "planlama/d158/F10s-gunluk.md"]),
    ("P10.7 19.11'de kapandı (P10.9c düzeltme turu 1, orkestratör kararı (Echo), geri alınabilir): kabul ölçütü 14.11'den beri sağlanıyor, "
     "CAD'li alt paketler bitti; kalan işler parça ya da sonraki tam taramalı CAD paketini beklediği için adlarıyla P10.8 satırına "
     "devredildi. G19 / G20 / G24 / G26 maddesi P10.7b2b'de (15.11) kapanmıştı, listeden çıktı.", [DONGU]),
    ("P10.9 19.11'de kapandı (P10.9c düzeltme turu 2, orkestratör kararı (Echo), geri alınabilir): kabul ölçütü (`F9c-dogrula` 0, "
     "tek tablo özet) sağlandı, iki bağımsız kontrol. Faz 10 açık kalıyor: P10.8 parça bekliyor. Devir taraması (düzeltme turu 2) "
     "kuyruğun \"Karar değil, iş\" bölümündeki P10.7b işlerini P10.8 satırına ekledi.", [DONGU, GUN, "planlama/d158/P109c-kontrol.md"]),
    ("Açık düşükler bölümü F9 sonu (09.11) hâlidir. \"Kapandı\" notu yalnız elle doğrulanan iki satırda (ikinci P6KE6V8A, K11 · K52); "
     "öbür notlar kararın kuyrukta kapandığını söyler, satırdaki ölçümü ya da işi kapatmaz (ör. K10 masa testi, K39 DS3235 düşme ölçümü; "
     "P10.9c düzeltme turu 2).", [GUN, KUYRUK, "planlama/d158/P109c-kontrol.md"]),
    ("F8a sipariş sayacı ve sipariş paketi toplamları 09.11 listesidir (P8.1 satırı, \"Sipariş paketi toplamı\", \"Bütçe farkı\"); güncel "
     "sipariş listesi `maliyet.json`. Sayfada etiketlenmedi, kaldırılmadı (P10.9a § 5.2 sorusu açık).", [P109A]),
    # P10.8f kayıt eşitlemesi (C, 21.11): K67 grubu A orkestratörce onaylandı (P108f-kontrol.md § 2)
    # P10.8g kayıt eşitlemesi (C, 22.11): K68 grubu C taslak
    ("Aciliyet gruplarının F10 taslağı (P10.9a § 3): açık F10 kararları K62 (C), K67 (A; 21.11'de açıldı, grup P10.8f taslağı, "
     "orkestratör 21.11'de onayladı) ve K68 (C; 22.11'de açıldı, grup taslak, orkestratör onaylar); K53, K54, K55, K60, K61 kapandı, "
     "grupları sayfaya girmiyor.", [P109A, KUYRUK, P108F, P108FK, P108G]),
    # Y0s kayıt eşitlemesi (C, 22.11): K69–K74 grupları taslak; Y0s commit'leri döngü paketine bağlanmıyor
    ("K69–K74 (22.11, Y0s sahte ESP32 simülasyonunun bulguları; Ahmet + Efe kararı) gruplarla taslak (K72 A, K70 / K71 / K73 / K74 B, "
     "K69 C), orkestratör onaylar. Bulgular simülasyonda; gerçek kartta denenmedi.", [KUYRUK, Y0S, Y0SK]),
    ("Y0s commit'leri (konu öneki \"Lale Y0s:\", 22.11) bu döngünün paketi değil (`yazilim-plani.md` Y0–Y3'ün donanımsız ön "
     "çalışması), pakete bağlanmıyor; eşleşmeyen commit sayısına girer.", [DONGU, Y0S]),
    ("Pakete bağlanamayan 2 commit (`9145164`, `f658f15`, 13.11 gizlilik denetimi, konu öneki \"Lale:\") paket dışı bırakıldı.", [P109A]),
    ("Tasarım demosu P10.9c'de yeniden üretilmedi (demo P10.7b2j'de üretilmişti); P10.8e'de P10.8d montajıyla yeniden üretildi "
     "(F9b 0).", [GUN, F10Y, DONGU]),
    # P10.8f (P108f-gunluk.md § 2): yenileme kaydı
    ("Sayfa 21.11'de P10.8f'de yeniden üretildi. Sayfa 19.11 hâlinde kalmıştı; P10.8a–e commit'leri ve kayıt eşitlemesinden sonra "
     "`F9c-dogrula` 60 hata veriyordu (P10.8e commit'inde 25): hepsi sayfadaki 19.11 değeri ile bugünkü kaynak farkı (montaj sayıları, "
     "rehber PDF ve parça sayısı, tarama koşusu, commit sayısı ve P10.8 commit hücresi, K67). Üretici K67'yi tanımadığı için sayfa "
     "yeniden üretilemiyordu (GRUP'ta yoktu); K67 A grubuyla eklendi (taslak, orkestratör onayladı), P10.8 satırı ve F10 tablosu "
     "bugünkü kayda göre yazıldı. Sayfa kendi commit'ini taşıyamaz: commit'ten sonra `F9c-dogrula` 3 hata verir (commit sayısı, "
     "eşleşmeyen commit, konu öneki), bir sonraki yenilemede kapanır.", [P108F, DONGU, KUYRUK]),
    # P10.8f kayıt eşitlemesi (C, 21.11): plan ve kuyruk P10.8f commit'ini gösterdi, sayfa aynı commit'te yeniden üretildi
    ("P10.8f commit'inden sonraki kayıt eşitlemesinde (21.11) plan P10.8 hücresi ve kuyruk 17.4, 17.10, B5a ve bu sayfanın "
     "kapanışını P10.8f commit'iyle işaretledi, kuyruğa P10.8f'in açık işleri girdi; sayfa bu kayıtlarla aynı commit'te yeniden "
     "üretildi (sabahki eşitleme sayfayı yeniden üretmediği için 35 hata eklemişti).", [DONGU, KUYRUK, P108F, P108FK]),
    # P10.8g ve kayıt eşitlemesi (C, 22.11): sayfa P10.8g'de (yalnız commit sayısı ve P10.8 commit hücresi) ve kayıt eşitlemesinde yenilendi
    ("Sayfa 22.11'de P10.8g'de (commit sayısı ve P10.8 commit hücresi) ve P10.8g commit'inden sonraki kayıt eşitlemesinde yeniden "
     "üretildi; eşitleme plan P10.8 hücresinde ve kuyrukta P10.8f'in dört açığını P10.8g commit'iyle kapattı, yapısal 3 hatayı K68 "
     "olarak açtı, kuyruğa P10.8g'nin açık işlerini yazdı.", [DONGU, KUYRUK, P108G, P108GK]),
]

# P10.9c düzeltme turu 1 (O5): açık düşüklerin F9 sonu satırlarına F10 notu. Anahtar F9c-dusukler.json "kod" alanı; bu sözlükte
# olmayan satıra kuyrukta kapanmış K kodları için kendiliğinden "kuyrukta kapandı" notu düşer (kaynak karar kuyruğu).
DUSUK_F10 = {
    "O-3 · K51 (KT-F7c-2)": ("F10 sonu: kapandı. K51 a (17.11, Echo); ikinci P6KE6V8A P10.7b2j'de modele ve BOM'a girdi.",
                             [KUYRUK, DONGU]),
    "K11 · K52 (KT-F7c-3)": ("F10 sonu: K11 (14.11) ve K52 (16.11) kapandı: kutunun F6 3 A yuvası, regülatör güç panelinde (rehber "
                             "B5a). Regülatör kartının modeli hâlâ yok (ürün ölçüsü bekliyor; P10.8 satırında).", [KUYRUK, DONGU]),
}

# Orkestratöre giden tutarsızlıklar (F9c-gunluk.md §7 ile aynı; her sayı kaynağında)
TUTARSIZ = [
    ("Brief'teki örnek (P4.5 🔄) eskidi: çalışma ağacındaki `dongu-158.md` P4.5'i ⛔ gösteriyor. Bu güncelleme ve P7.4 ✅, P9.4 ✅, P9.3 🔄 satırları HEAD'de yok (`0089d97` P7.4 ve P9.4'ü 🔄, P9.3'ü ⏳ gösteriyor). Orkestratör kararı: son C ajanı commit'leyecek; rapor çalışma ağacındaki planı esas alır.", [DONGU, BRIEF]),
    ("Çözüldü: `dongu-158.md` §1 rampa metni orkestratörce \"başta 1,517, şimdi 1,519\" diye düzeltildi.", [DONGU, REG_SON]),
    ("P5.3'ün brief'inde P kodu yok (F5 C pano #6'yı açtı, F5b pano #7'yi); eşleme F5 + F5b (orkestratör onayı). F5b'nin raporu yok, kaydı `F5-rapor.html`'de.", [DONGU]),
    ("Çözüldü: KT-F7c-2 ve KT-F7c-3 karar kuyruğunda değildi; orkestratör kararıyla K51 ve K52 olarak eklendi (açık 47 / 52).", ["planlama/d158/F7c-gunluk.md", KUYRUK]),
    ("Çalışma ağacında hiçbir pakete bağlı olmayan değişiklik: 13 kabuk PNG'si (F6a D-5, K23) ve `tasarim/freecad/montaj/yerlesim-kontrol.json`.", ["planlama/d158/F6a-kontrol.md"]),
    ("Demo parmak izi `demo_uret.py` ile yenilendi (127 anahtarın değeri aynı, `F9b-dogrula.py` 0). Ama demonun gösterdiği 14 karar `demo_uret.py` içindeki sabit listeden geliyor; K50, K51, K52 orada yok, bu yüzden demoda görünmüyor. Listeyi değiştirmek bu paketin yazma alanı dışında.", [KUYRUK, DONGU, "tasarim/cad/demo_uret.py"]),
    ("Yanlışlıkla yayımlanan özel sayfanın silinmesi Ahmet'te (adres bu raporda yazılmaz).", [DONGU]),
]


# ------------------------------------------------------------------ HTML
STIL = """:root{
  --bg:#f7f6f3; --panel:#ffffff; --ink:#1f2328; --muted:#5f6670; --line:#dcd9d2;
  --ok:#1f7a45; --ok-bg:#e6f4ea; --wait:#8a5a00; --wait-bg:#fdf1d8; --info:#2457a6; --info-bg:#e7eefb;
  --crit:#a3202f; --crit-bg:#fbe9eb; --accent:#b0304a;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#15171a; --panel:#1e2125; --ink:#e7e9ec; --muted:#a2a9b2; --line:#33383e;
    --ok:#6fd39a; --ok-bg:#183326; --wait:#f0c062; --wait-bg:#3a2f15; --info:#8fb4f2; --info-bg:#1b2a44;
    --crit:#f2899a; --crit-bg:#3a1a20; --accent:#ef7d93;
  }
}
:root[data-theme="dark"]{
  --bg:#15171a; --panel:#1e2125; --ink:#e7e9ec; --muted:#a2a9b2; --line:#33383e;
  --ok:#6fd39a; --ok-bg:#183326; --wait:#f0c062; --wait-bg:#3a2f15; --info:#8fb4f2; --info-bg:#1b2a44;
  --crit:#f2899a; --crit-bg:#3a1a20; --accent:#ef7d93;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 48px}
header{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
h1{font-size:1.5rem;margin:0 0 4px}
h2{font-size:1.1rem;margin:32px 0 10px;padding-bottom:4px;border-bottom:1px solid var(--line)}
h3{font-size:1rem;margin:20px 0 8px}
p{margin:8px 0}
p.sub{color:var(--muted);margin:0 0 20px}
p.note{color:var(--muted);font-size:.88rem}
a{color:var(--info)}
code{font:0.88em ui-monospace,SFMono-Regular,Consolas,monospace;background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:0 4px;overflow-wrap:anywhere}
button.tema{font:inherit;font-size:.85rem;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:5px 12px;cursor:pointer}
nav.ic{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:.88rem;margin:0 0 18px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.card .k{font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.card .v{font-size:1.6rem;font-weight:650;margin:2px 0}
.card .d{font-size:.88rem;color:var(--muted)}
.tag{display:inline-block;font-size:.78rem;font-weight:600;border-radius:999px;padding:1px 9px;white-space:nowrap}
.ok{color:var(--ok);background:var(--ok-bg)}
.wait{color:var(--wait);background:var(--wait-bg)}
.info{color:var(--info);background:var(--info-bg)}
.crit{color:var(--crit);background:var(--crit-bg)}
.tbl{overflow-x:auto;background:var(--panel);border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}
th{font-weight:600;color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.04em}
tr:last-child td{border-bottom:none}
td.kod{font-weight:650;white-space:nowrap}
th.kod,#takvim-tablo th{white-space:nowrap}
td.n{font-variant-numeric:tabular-nums}
@media (min-width:641px){#f10-tablo td:first-child{width:9.5em;overflow-wrap:normal}#paket-tablo td:nth-child(2){min-width:11em;overflow-wrap:normal}th{overflow-wrap:normal}}
ol.list,ul.list{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 16px 12px 34px;margin:0}
ol.list li,ul.list li{margin:4px 0}
.oneri{background:var(--wait-bg);border:1px solid var(--line);border-left:4px solid var(--wait);border-radius:10px;padding:12px 16px;margin:10px 0}
.oneri b{color:var(--wait)}
details{margin:10px 0}
summary{cursor:pointer;font-weight:600}
footer{margin-top:32px;color:var(--muted);font-size:.85rem}
@media (max-width:640px){
  .tbl table.yigin thead{display:none}
  .tbl table.yigin tr{display:block;border-bottom:1px solid var(--line);padding:6px 0}
  .tbl table.yigin td{display:block;border:none;padding:3px 12px}
  .tbl table.yigin td[data-b]::before{content:attr(data-b) ": ";font-weight:600;color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}
}
@media print{button.tema,nav.ic{display:none}}"""

TEMA_JS = """(function(){
  var b=document.getElementById('tema'), r=document.documentElement, s=['sistem','açık','koyu'], i=0;
  try{var k=localStorage.getItem('lale-tema'); if(k){i=s.indexOf(k); if(i<0)i=0;}}catch(e){}
  function uygula(){
    if(s[i]==='açık') r.setAttribute('data-theme','light');
    else if(s[i]==='koyu') r.setAttribute('data-theme','dark');
    else r.removeAttribute('data-theme');
    b.textContent='Tema: '+s[i];
  }
  uygula();
  b.addEventListener('click',function(){i=(i+1)%3; uygula(); try{localStorage.setItem('lale-tema',s[i]);}catch(e){}});
})();"""

ETIKET = {"✅": ("ok", "geçti"), "🟡": ("wait", "koşullu"), "⛔": ("crit", "karar bekliyor"), "🔄": ("info", "çalışıyor"),
          "⏳": ("info", "sırada")}


def durum_tag(em):
    s, a = ETIKET.get(em, ("info", "?"))
    return '<span class="tag %s">%s %s</span>' % (s, em, a)


def faz_durum(ems):
    for e in "🔄⛔🟡⏳":
        if e in ems:
            return e
    return "✅"


def td(icerik, baslik, sinif=""):
    s = ' class="%s"' % sinif if sinif else ""
    return '<td%s data-b="%s">%s</td>' % (s, baslik, icerik)


def uret():
    fazlar, paket = plan_paketleri()
    etk = brief_etiketleri({p["kod"] for p in paket})
    harita, eksik, eslesmeyen, kom = paket_komitleri(paket, etk)
    kr = kararlar()
    acik = [k for k in kr if k["acik"]]
    dus = js(DUSUK)["satirlar"]
    say = {e: sum(1 for p in paket if p["emoji"] == e) for e in EMOJI}
    fk = {}
    for k in acik:
        fk.setdefault(karar_faz(k), []).append(k["k"])
    reg0_c = git("log", "--diff-filter=A", "--format=%h", "--", REG).split()[-1]
    REG0 = "git:%s:%s" % (reg0_c, REG)
    r0, r1 = json.loads(git("show", "%s:%s" % (reg0_c, REG))), js(REG_SON)

    o = []
    w = o.append
    w('<!doctype html>\n<html lang="tr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">')
    w("<title>Lale 1,58 m Sonuç Raporu</title>\n<style>\n%s\n</style>\n</head>\n<body data-hazir=\"1\">\n<main>" % STIL)
    # P10.9c: başlık ve tarih F10 sonuna (F9 sonu sayfası: "(P9.3)", 09.11.2026, Ajan A)
    w('<header>\n<div>\n<h1>%s</h1>' % K("Lale 1,58 m döngüsü: sonuç raporu (F10 sonu, P10.9)", DONGU))
    # P10.8f: yenileme tarihi (faz sonu sayfası P10.9c'nin; P10.8a–e sonrası yenilendi)
    w('<p class="sub">Uygulama ajanı (P10.9c) · %s · dal <code>lale-duzeltme</code> · üretici <code>planlama/d158/F9c-uret.py</code>, denetim '
      '<code>F9c-dogrula.py</code> · kaynaklar: <code>dongu-158.md</code>, <code>karar-kuyrugu.md</code>, paket raporları, '
      'regresyon JSON\'ları, <code>git log</code></p>' % K("19.11.2026; yenileme P10.8f ve kayıt eşitlemesi, 21.11.2026; P10.8g ve "
                                                            "kayıt eşitlemesi, 22.11.2026; Y0s kayıt eşitlemesi, 22.11.2026", GUN, F10Y, KUYRUK,
                                                            P108F, P108G, Y0S))
    w('</div>\n<button class="tema" type="button" id="tema">Tema: sistem</button>\n</header>')
    w('<nav class="ic"><a href="#f10">F10 sonu</a><a href="#ozet">Özet</a><a href="#yapilacak">Ahmet\'in yapacakları</a><a href="#kararlar">Açık kararlar</a>'
      '<a href="#korunan">Korunan değerler</a><a href="#sayilar">Sayılarla robot</a><a href="#takvim">Takvim</a>'
      '<a href="#paketler">Paketler</a><a href="#dusukler">Açık düşükler</a><a href="#tutarlilik">Kayıt notları</a></nav>')

    # kartlar
    w('<div class="cards">')
    w('<div class="card"><div class="k">Paket</div><div class="v">%s</div><div class="d">%s ✅ · %s 🟡 · %s ⛔ · %s 🔄 · %s ⏳</div></div>' % (
        H("paket_sayisi", len(paket)), H("paket_✅", say["✅"]), H("paket_🟡", say["🟡"]), H("paket_⛔", say["⛔"]), H("paket_🔄", say["🔄"]),
        H("paket_⏳", say["⏳"])))
    w('<div class="card"><div class="k">Açık karar</div><div class="v">%s / %s</div><div class="d">%s sipariş / güvenlik öncesi · %s montaj öncesi · %s sonra</div></div>' % (
        H("karar_acik", len(acik)), H("karar_toplam", len(kr)), H("grup_A", sum(1 for k in acik if GRUP[k["k"]][0] == "A")),
        H("grup_B", sum(1 for k in acik if GRUP[k["k"]][0] == "B")), H("grup_C", sum(1 for k in acik if GRUP[k["k"]][0] == "C"))))
    w('<div class="card"><div class="k">Korunan değerler</div><div class="v">%s / %s</div><div class="d">son koşu çıkışı %s; kötüleşen %s</div></div>' % (
        H("reg_ayni", sum(1 for x in r1["karsilastirma"] if x["durum"] == "aynı")), H("reg_sayi", len(r1["degerler"])),
        J(REG_SON, "cikis_kodu"), J(REG_SON, "kotulesen#say")))
    w('<div class="card"><div class="k">Boy · kütle</div><div class="v">%s mm</div><div class="d">ana montaj %s g; kablo payıyla %s g</div></div>' % (
        J(LK, "toplam_boy_mm", "i"), J(MA, "kutle_g", "2"), J(UI, "ev.kutle_g", "1")))
    w('<div class="card"><div class="k">Maliyet</div><div class="v">%s TL</div><div class="d">V3, yazıcı, yedek, pay dahil; siparişin durumu kayıtta yok</div></div>' % (
        J(ML, "=genel", "2")))
    w('<div class="card"><div class="k">Commit</div><div class="v">%s</div><div class="d">döngü boyunca (<code>%s</code> → <code>%s</code>)</div></div>' % (
        H("komit_sayisi", len(kom)), kom[-1][0], kom[0][0]))
    w("</div>")

    # 0. F10 sonu: tek tablo (P10.9c). F9 sonunun kalıbı faz başına özet (aşağıda "Ahmet için özet"); F10 sonu için konu başına
    # bitti / açık iş / Ahmet'in kararı. Sayılar JSON'dan (data-j) ya da sayımdan (data-h), metin kaynağıyla (data-kaynak).
    n_kapali, gA_n = len(kr) - len(acik), sum(1 for k in acik if GRUP[k["k"]][0] == "A")
    # P10.9c düzeltme turu 1: plan durumları plandan (elle yazılmaz; P10.2 ve P10.7 19.11'de kapandı, P10.9 commit'te kapanır)
    f10_durum = ", ".join("%s %s" % (p["kod"], p["emoji"]) for p in paket if p["faz"] == "F10")
    w('<h2 id="f10">%s</h2>' % K("Faz 10 sonu: tek tablo (Ahmet için)", DONGU))
    w('<p class="note">%s Plan durumları (<code>dongu-158.md</code>): %s.</p>' % (K(
        "Konu başına üç sütun: bitenler, açık iş (karar değil, iş) ve Ahmet'in kararını bekleyenler. Kodlar: K = karar kuyruğu maddesi "
        "(`karar-kuyrugu.md`; yanındaki a / b seçilen seçenek), P = plan paketi (`dongu-158.md`; P10.7b2j gibi harfli olanlar alt paket), "
        "17.4 gibi sayılar rehberin alt adımı, E4 / B6a gibi kodlar rehber adımı, G19 / U06 / N02 gibi kodlar kablo kimliği "
        "(`kablolar.json`), KT1–KT7 masa denemeleri. Kapanan kararların sahibi hücrede yazılı: Ahmet ya da orkestratör (Echo); Echo "
        "kararları geri alınabilir. Teknik sıralar Echo kararıdır; alım, bütçe ve sipariş Ahmet'te, tabloda yalnız soru olarak. P10.7 "
        "kapanınca kalan işleri adlarıyla P10.8 satırına devredildi.", DONGU, KUYRUK, GUN), html.escape(f10_durum)))
    w('<div class="tbl"><table class="yigin" id="f10-tablo"><thead><tr><th>Konu</th><th>Bitti</th><th>Açık iş</th>'
      '<th>Ahmet\'in kararı</th></tr></thead><tbody>')
    f10 = [
        ("Montaj rehberi (3B + PDF)",
         K("Adım ", DONGU) + J(RK, "ozet.adim") + K(", alt adım 91; seçim vurgusu, kabuk alt adımları, kol içi kablo yolu, K1 / K2 demet alt "
                                                   "adımları; 74 / 74 kablo bağlama talimatında; rehber b2j CAD'ine uyduruldu (P10.7b2k). PDF ", DONGU)
         + J(RK, "yazdir.pdf_sayfa") + K(" sayfa. Makine denetimi geçti; F10y'de 17.8–17.12, 32.x'in kalanı, B5a / B6 / E3a kareleri ve PDF "
                                        "sayfaları gözle bakılmadı.", DONGU, F10Y)
         # P10.8f: P10.8b–f rehber işleri (plan P10.8 hücresi; P108f-gunluk.md)
         + K(" P10.8b–e: K55 bant metni ölçümden, ESP32 yön denetimi, `--kaynak` CAD adları, D6, iki yeni kart rehberde modelli uç, "
             "17.11'de U06'nın taban bölümü, 32.1 taban bakışı. P10.8f: 17.4 saplama numaraları karede, 17.10'da katın kesiği "
             "çizgiyle, B5a'da acil stop düğüm kartı adıyla.", DONGU, P108F)
         # P10.8g kayıt eşitlemesi (C, 22.11): P10.8g'nin kapattıkları (plan P10.8 hücresi; P108g-gunluk.md § 12)
         + K(" P10.8g: 17.1 ve 17.5 saplama numaraları karede, basılı lejantta 17.11 şema notu, PDF'te parça etiketi ≈ 8,1–8,4 pt "
             "(önce ≈ 2,4–2,5), parça etiketi ölçümü teslim edilen kareyi ölçüyor.", DONGU, P108G, P108GK),
         # P10.8f kayıt eşitlemesi (C, 21.11): P10.8f'in rehber açıkları (kuyruk "P10.8f kapanışından açık iş")
         K("Kuyruğun \"Karar değil, iş\" bölümünde: ölçülmeyen yollar (göğüs bandı sol yanal yol, F2 ve etek arka dikişleri), "
           "`--kaynak` CAD malzeme adlarını görmüyor, `elektrik.md` önerilen boyları kayda bağlı değil; iki yeni kartın zarfı TAHMİN "
           "(kartlar gelince). P10.8g'den: 17.5 basılı karesi dokuz saplamayı tek başına ayırt ettirmiyor; büyük etiket kutusu "
           "17.1 ve 17.4'te saplamayı örtüyor, yerleşimin kusur sayımı örtmeyi ve uç kesişmesini ölçmüyor; uç numaraları ve kare "
           "şeritleri kâğıtta ≈ 2,3–2,5 pt; yazı boyu ölçümü ayarı okuyor ve zincirde değil; F10d alt adımsız karede teslim "
           "edilenden farklı çekimi ölçüyor.", KUYRUK, DONGU, P108G, P108GK),
         "—"),
        ("CAD ve çakışma taraması",
         K("P10.7b2j (Echo kararları: K2 a, K51 a, K53 a 17.11'de Ahmet'in devriyle; K64 a 16.11): K2 a boss, K53 a çentik, K51 a TVS, "
           "K64 a iki bara tutucusu ve dokuz saplama; USB ses kartı modelden çıktı. P10.8d (21.11): CAD kablo yolu 10, 11 ve 12 "
           "düzeltildi, burç 2 yarıktan çıktı, acil stop düğüm kartı ve dağıtım kartı C modelde, 16 şema tarandı. Bugün: parça ",
           DONGU, KUYRUK)
         + J(MA, "parca_sayisi", "i") + K(", kütle ", DONGU) + J(MA, "kutle_g", "k2") + K(" kg, baskı ", DONGU) + J(BA, "toplam.adet")
         + K(" adet, bağlantı elemanı ", DONGU) + J(DEMO, "anahtarlar.p_bag.deger", "i") + K(". Tam tarama tek koşu ", DONGU)
         + J(CS, "bolumler.statik.kosu", "s") + K(" (", DONGU) + J(CS, "bolumler#say") + K(" bölüm): eklem aralığında ", DONGU)
         + J(CS, "toplam.eklem_araliginda") + K(" çakışma; tarama toplamında ", DONGU) + J(CS, "toplam.cakisma")
         + K(" çakışma, hepsi eklem aralığı dışında.", DONGU, "planlama/d158/F10x-gunluk.md"),
         # P10.8f: P10.8d'de kapananlar (yol 10 / 11 / 12, burç 2, dikiş ölçümü, iki kart, 16 şema) çıktı; kalanlar plan P10.8 hücresinden
         K("P10.8 satırında, sonraki tam taramalı CAD paketine: göğüs regülatörü kartının (K52) zarfı ve panel yeri (modelde yok); "
           "K31 insert boyu (`arayuz.py`); CAD kablo yolu 6'nın güç panelindeki dağıtım kartı C'ye inmesi (rehber S09 / S10'un kart "
           "yanını elle bakıldı diye taşıyor); iki yeni kartın gerçek ölçüsü, zarfı ve burç / vida boyu (TAHMİN, kartlar yapılınca); "
           "kafa giriş kartı ve kart üstü konnektör yerleri (TAHMİN); `TABAN_DISI_BOLGE` gövde bölgesi geniş; tam çakışma taraması parça "
           "modellerinden sonra yeniden koşar. Göğüs ekranı port girintisi ekran gelince (P1.4 koşullu).",
           KUYRUK, DONGU),
         K("K2 bütçe yarısı: AI HAT+ okul bütçesinden mi (teknik yarı a, boss modelde).", KUYRUK)),
        ("Elektrik ve kablolama",
         K("74 kablo tek kaynakta (`kablolar.json`); pin haritası K58 (orkestratör, Ahmet'in 13.11 yetkisiyle); K63 talimat boşlukları; "
           "K52 a göğüs regülatörü güç panelinde ve K66 ESP32 VIN'e seri 1N5819 (Echo, 16.11); K60 A (Echo, 17.11, Ahmet'in devriyle): "
           "elde taşınan acil stop yok, köprülü klemens var, demoda mantarın yanında bir kişi durur. Kararlar rehberde.", DONGU, KUYRUK),
         K("P10.8 satırında: kablo boylarının ölçümü (kablolar gelince); ESP32 DevKit yönü: `u06_port_denetle` 180° ters takılmış kartı "
           "yakalamaz, ters takılırsa ilk enerjide 5 V bir GPIO pinine gelir (rehberdeki yön kontrolü tek önlem); kabuk ve etek takılıyken "
           "güç panelindeki bara somunlarına üstten erişim ölçülmedi; PC817 çıkış jumper'ı modül gelince seçilecek; KT2 sonucundan sonra "
           "AU1 / AU2 ses şeması ve kaydı; fiş boyları ve talimat ↔ kayıt boyları (ör. E3a K03) kablolar gelince; G07 bölücü "
           "dirençlerinin toleransı kayıtta yok. P10.7b'nin öbür açık işleri kuyruğun \"Karar değil, iş\" bölümünde. K61 düğmesinin "
           "`maliyet.json`'dan düşülmesi (sipariş kararıyla).", DONGU, KUYRUK),
         K("K50 alım yarısı (XT60E-F dişi panel); K13 ReSpeaker LED'leri görünsün mü.", KUYRUK)),
        ("Kararlar",
         H("karar_kapali", n_kapali) + K(" madde kapandı; 17.11'de 22'si orkestratörce (Echo), Ahmet'in devriyle (P10.9b).", KUYRUK),
         "—",
         H("karar_acik", len(acik)) + " / " + H("karar_toplam", len(kr)) + K(" açık; ", KUYRUK) + H("grup_A", gA_n)
         + K(" madde sipariş ya da güvenlik öncesi. Ortak ön soru: 16.11 siparişi verildi mi, hangi listeyle?", KUYRUK)),
        ("Sipariş ve maliyet",
         K("Güncel liste `maliyet.json`, genel ", ML) + J(ML, "=genel", "2") + K(" TL.", ML),
         K("F8a sipariş paketi satırları (P8.1, sipariş paketi toplamı, bütçe farkı) 09.11 listesidir, güncel değil.", P109A),
         K("K27–K30, K32, K34–K37, K42; K31 / K33 / K43 / K50 alım yarıları; K64 alım kalemleri (M5 saplama başının altıgen olması, "
           "pullar, M3 vidalar); göğüs regülatörü kartının (K52) ürünü ve ölçüsü; N02'nin N01 boyunda alınması; kondansatör yedeği "
           "(sipariş 5, kullanım 5); KT2 geçmezse gereken USB-A uzatma ve L dirsek şimdi mi alınsın; K67 kart burcu adedi (CAD 52, "
           "liste 48).", KUYRUK, "planlama/d158/F10u-gunluk.md")),
        ("Parçalar gelince (P10.8 ve devralınan işler)",
         "—",
         K("Önerilen sıra (Echo kararı, geri alınabilir): 1) parça beklemeden yalnız kupon dosyaları: K54 c ve K55 a kuponları, kupon C "
           "M5 delikleri kupon betiğinde yerel parametreyle (izlenen `arayuz.py`'ye dokunmadan) (yapıldı: P10.8a, basılmadı); 2) Parti 0 ilk gün: tolerans kuponları, "
           "K54 / K55 kuponları, boyun tüneli deneme parçası; 3) gelen parçayı kumpasla teyit et: D24V50F5 pin kenarı, ESP32 DevKit micro "
           "USB portu ve yönü, PC817 çıkış jumper'ı, göğüs regülatörü kartının ölçüsü, RV 5.5 pabuç kalınlığı, M5 saplama başı, göğüs "
           "ekranı portu, AI HAT+ zarfı; 4) boyun tüneli fiş denemesi, kablo boylarının ve fiş boylarının ölçümü (kablolar gelince); 5) masa denemeleri "
           "KT1–KT7 (önce KT1 ve KT2, alımı belirliyorlar; KT2'den sonra AU1 / AU2 şeması) ve K66 tezgâh denemesi; 6) P10.8: satın alınan parça modelleri ve fotoğraf "
           "kartı, tek tam taramalı CAD paketinde şunlarla birlikte: K52 kart zarfı ve yeri, K31 insert boyu (`arayuz.py`), CAD kablo "
           "yolu 6'nın kart C'ye inmesi, iki yeni kartın gerçek ölçüsü, teyitlerden çıkan değişiklikler (CAD kablo yolu 10 / 11 / 12, "
           "burç 2, dikiş ölçümü, iki kartın modeli ve 16 şemanın taraması P10.8d'de yapıldı); ardından bir rehber üretimi; 7) montajda: bara "
           "somunlarına kabuk takılıyken erişim, ölçümler K39, K45, K12, K6.", GUN, DONGU),
         K("Parti 0 değerlendirmesi rulman (6808-2RS, 625ZZ), M3 / M5 ısıl gömme somun ve kupon D vidası ister (K29 erken alım; K31, K43 "
           "insert); CF kuponları PETG-CF'ye bağlı (K42). K54 / K55 kuponları ve boyun tüneli parçası insert istemez.", KUYRUK, GUN, "planlama/d158/F4c-partiler.json")),
        ("Yazılım (Efe'nin alanı)",
         K("Efe'nin iki cevabı (reset DTR / RTS, ReSpeaker 16 kHz) kayıtta; 17.11 kararları pano #7 mesaj #34 ile Efe'ye bildirildi.",
           DONGU, P109B),
         K("K38 / K45 hız sınırları ve kapanma sırası, K41 S1 −45…135, K44 `eklem_sinirlari.json` üretimi, K3 / K9 el yükü kuralı, "
           "K65 sağ / sol yazılım düzeltmesi.", KUYRUK),
         "—"),
        ("Depo, yayın ve kayıt",
         K("P10.7b2j ve P10.7b2k push edildi. Push öncesi kanca iki yanlış alarm verdi (STEP koordinatlarının ondalık kesri, gömülü "
           "resim verisi); orkestratör eklenen satırları kancanın kalıplarıyla kendisi taradıktan sonra iki commit kanca atlanarak "
           "gönderildi (Echo kararı); ardından günlük commit'i `89134d5` kancadan geçti. P10.8a–f commit'leri ve 21.11 sabahki kayıt "
           "eşitlemesi push edildi; P10.8d'den sonra kancaya STEP koordinatı istisnası eklendi (21.11).", F10Y, DONGU),
         # P10.8f kayıt eşitlemesi (C, 21.11): sayfanın yapısal 3 hatası kuyrukta iş olarak
         K("K48 dosyasının depo dışına taşınması, K49 `.gitignore` girdileri, pre-push kancasına gömülü görsel verisi istisnası. Bu "
           "sayfa kendi commit'ini taşıyamaz: her commit'ten sonra `F9c-dogrula` en az 3 hata verir (yapısal, muaf tutulmadı).",
           KUYRUK, F10Y, P108F),
         K("K18–K26 depo içeriği, gizlilik ve hesap adı; `main`'e birleştirme (Pages) onayı; K62 tur sayısı kaydı; `uygulama-notu.md`'deki "
           "kişi adı geçen satırlar.", KUYRUK, DONGU, F10Y)
         # P10.8g kayıt eşitlemesi (C, 22.11): yapısal 3 hata karar oldu
         + K(" K68: bu sayfanın denetimi taban commit'ine göre mi hesaplansın (öneri S1, `F9c-dogrula.py` değişikliği).", KUYRUK, P108G)),
    ]
    for konu, bitti, acik_is, ahmet in f10:
        w('<tr data-f10="1">%s%s%s%s</tr>' % (td("<b>%s</b>" % K(konu, DONGU), "Konu"), td(bitti, "Bitti"), td(acik_is, "Açık iş"),
                                               td(ahmet, "Ahmet'in kararı")))
    w("</tbody></table></div>")

    # 1. Ahmet için özet
    w('<h2 id="ozet">Ahmet için özet</h2>')
    w('<div class="tbl"><table class="yigin"><thead><tr><th>Faz</th><th>Durum</th><th>Ana sonuç</th><th>Açık karar</th></tr></thead><tbody>')
    for f, ad in fazlar:
        ems = [p["emoji"] for p in paket if p["faz"] == f]
        metin, kay = FAZ_SONUC[f]
        if f == "F10":   # P10.9c düzeltme turu 1: açık paketler plandan (P10.9 kapanınca cümle kendiliğinden değişir)
            ack_ = [p["kod"] for p in paket if p["faz"] == "F10" and p["emoji"] != "✅"]
            ACK_AD = {"P10.8": "parçalar gelince; devralınan işlerle", "P10.9": "bu sayfa"}
            kap_ = [p["kod"] for p in paket if p["faz"] == "F10" and p["emoji"] == "✅"]
            metin = "Kapalı: " + ", ".join(kap_) + " ve " + metin
            if ack_:
                metin = "Faz açık. " + metin + " Açık: " + ", ".join("%s (%s)" % (x, ACK_AD.get(x, "plan")) for x in ack_) + "."
        w("<tr>%s%s%s%s</tr>" % (td("<b>%s</b> · %s" % (f, K(ad, DONGU)), "Faz"), td(durum_tag(faz_durum(ems)), "Durum"),
                                 td(K(metin, *kay), "Ana sonuç"),
                                 td('<b>%s</b>%s' % (H("faz_karar_" + f, len(fk.get(f, []))),
                                                     (' <span class="note">· %s</span>' % ", ".join(fk[f])) if fk.get(f) else ""), "Açık karar", "n")))
    w("<tr>%s%s%s%s</tr>" % (td("<b>Toplam</b>", "Faz"), td("", "Durum"),
                             td("%s paket; plan tek doğru kaynak <code>dongu-158.md</code>" % H("paket_sayisi", len(paket)), "Ana sonuç"),
                             td("<b>%s</b>" % H("karar_acik", len(acik)), "Açık karar", "n")))
    w("</tbody></table></div>")
    w('<p class="note">Faz durumu, fazdaki paketlerin en kötüsüdür (🔄 &gt; ⛔ &gt; 🟡 &gt; ⏳ &gt; ✅). Açık kararlar faza şu kuralla '
      'bağlandı: kuyruğun Durum hücresindeki paket etiketi (ör. F8a → F8); yoksa Bloke hücresindeki ilk P kodu; yoksa Durum hücresindeki '
      'ilk P kodu (ör. K62 → F10); yoksa F0. F10 paketleri: %s; bu sayfa P10.9\'un faz sonu yenilemesidir.</p>' % html.escape(f10_durum))

    # 2. Ahmet'in yapacakları
    gA = [k["k"] for k in acik if GRUP[k["k"]][0] == "A"]
    w('<h2 id="yapilacak">Ahmet\'in yapacakları</h2><ol class="list">')
    w("<li><b>Kararlar:</b> %s açık madde; önce sipariş ya da güvenlik öncesi gereken %s madde (%s). Liste ve önerilen varsayılanlar "
      '<a href="#kararlar">aşağıda</a>, ayrıntı <a href="karar-kuyrugu.md">karar kuyruğunda</a>.</li>' % (
          H("karar_acik", len(acik)), H("grup_A", len(gA)), ", ".join(gA)))
    w("<li><b><code>main</code>'e birleştirme (Pages):</b> %s</li>" % K(
        "demo ve rehber yalnız `lale-duzeltme` dalında; birleştirme Ahmet'in onayına bağlı (KT-F9b-1). Birleştirme commit'inde README "
        "demo satırındaki \"bu sürüm `lale-duzeltme` dalında\" ifadesi kaldırılmalı (F9d D-4). Öneri: önce K25 ve K26.", DONGU,
        "planlama/d158/F9d-rapor.html"))
    # P10.9c: üç madde F10 kayıtlarına göre (K47, K48, K49 17.11'de kapandı; K1, K14 14.11'de; Efe'nin iki cevabı kayıtta)
    w("<li><b>Silme gerektirenler:</b> %s</li>" % K(
        "Yanlışlıkla yayımlanan özel sayfanın silinmesi (Ahmet; kayıtta kapanış yok). K48 kapandı (17.11, a: `tasarim/cad/lale158-model.js` "
        "depo dışına taşınır; taşıma açık iş).", KUYRUK, DONGU))
    w("<li><b><code>.gitignore</code> kararları:</b> %s</li>" % K(
        "K47 ve K49 kapandı (17.11, P10.9b); K49'un dört klasör girdisi K18–K21 kararıyla birlikte, onlar Ahmet'te. Uygulaması açık iş.", KUYRUK))
    w("<li><b>Efe'nin alanı:</b> %s</li>" % K(
        "K1 ve K14 kapandı (14.11); Efe'nin iki cevabı (reset DTR / RTS, ReSpeaker 16 kHz) kayıtta. Efe'ye bildirilen iş (pano #7 mesaj #34): "
        "K38 / K45 hız sınırları ve kapanma sırası, K41 S1 −45…135, K44 `eklem_sinirlari.json` üretimi, K3 / K9 el yükü kuralı; ayrıca "
        "K65 sağ / sol yazılım düzeltmesi.", KUYRUK, DONGU, P109B))
    w("<li><b>Ortak ön soru:</b> %s</li>" % K(
        "16.11 siparişi verildi mi, hangi listeyle? Kayıtta yok; K27–K37, K42, K43, K50, K61 ve K67'nin maliyet işi bu cevaba bağlı.", KUYRUK))
    w("</ol>")

    # 3. Açık kararlar
    w('<h2 id="kararlar">Açık kararlar (%s / %s)</h2>' % (H("karar_acik", len(acik)), H("karar_toplam", len(kr))))
    w('<p class="note">Sayım <code>karar-kuyrugu.md</code> Özet tablosundan: Durum hücresinde <b>açık</b> olanlar %s, kapanan %s '
      '(%s). Aciliyet grupları F9c A\'nın önerisidir, karar değildir; varsayılan ve "beklettiği" sütunları kuyruktan birebir.</p>' % (
          H("karar_acik", len(acik)), H("karar_kapali", len(kr) - len(acik)), ", ".join(k["k"] for k in kr if not k["acik"])))
    for g in "ABC":
        ks = [k for k in acik if GRUP[k["k"]][0] == g]
        w("<h3>%s: %s (%s)</h3>" % (g, GRUP_AD[g], H("grup_" + g, len(ks))))
        w('<div class="tbl"><table class="yigin"><thead><tr><th class="kod">Kod</th><th>Karar</th><th>Önerilen varsayılan</th><th>Beklettiği</th><th>Neden bu grupta</th></tr></thead><tbody>')
        for k in ks:
            w('<tr data-karar="%s" data-grup="%s">%s%s%s%s%s</tr>' % (
                k["k"], g, td(k["k"], "Kod", "kod"), td(K(k["karar"], KUYRUK), "Karar"), td(K(k["varsayilan"] + VARSAYILAN_EK.get(k["k"], ""), KUYRUK), "Varsayılan"),
                td(K(k["bloke"], KUYRUK), "Beklettiği"), td(K(GRUP[k["k"]][1], KUYRUK, PLAN, DONGU, "planlama/d158/F6a-kontrol.md"), "Neden")))
        w("</tbody></table></div>")

    # 4. Korunan değerler
    w('<h2 id="korunan">Korunan değerler: döngü başı ↔ son koşu</h2>')
    w('<p class="note">Döngü başı: <code>%s</code> commit\'indeki <code>%s</code> (tarih %s). Son koşu: <code>%s</code> (tarih %s, çıkış %s). '
      'Her değerin kaynak dosyası ve anahtarı regresyon betiğinin kendi kaydından.</p>' % (
          reg0_c, REG, J(REG0, "tarih", "s"), REG_SON, J(REG_SON, "tarih", "s"), J(REG_SON, "cikis_kodu")))
    w('<div class="tbl"><table class="yigin"><thead><tr><th>Değer</th><th>Eşik</th><th>Döngü başı</th><th>Son koşu</th><th>Durum</th><th>Kaynak (dosya · anahtar)</th></tr></thead><tbody>')
    BIC = {"boy_mm": "1", "rampa_yuksuz": "3", "tilt_payi": "2", "pan_payi": "2", "mik_hoparlor_mm": "1"}
    kar = {x["ad"]: x["durum"] for x in r1["karsilastirma"]}
    for ad, v in r1["degerler"].items():
        b = BIC.get(ad, "0")
        d0 = r0["degerler"][ad]["deger"]
        fark = "aynı" if d0 == v["deger"] else ("iyileşti" if (v["yon"] == "buyuk_iyi") == (v["deger"] > d0) else "kötüleşti")
        w('<tr data-reg="%s">%s%s%s%s%s%s</tr>' % (
            ad, td(K(v["etiket"], REG_SON), "Değer"), td(J(REG_SON, "degerler.%s.esik" % ad, b), "Eşik", "n"),
            td(J(REG0, "degerler.%s.deger" % ad, b), "Döngü başı", "n"), td(J(REG_SON, "degerler.%s.deger" % ad, b), "Son koşu", "n"),
            td('<span class="tag %s">%s</span> <span class="note">son koşu: %s</span>' % ("ok" if fark != "kötüleşti" else "crit", fark, html.escape(kar.get(ad, "?"))), "Durum"),
            td("<code>%s</code> · <code>%s</code>" % (html.escape(v["kaynak"]["dosya"]), html.escape(v["kaynak"]["anahtar"])), "Kaynak")))
    w("</tbody></table></div>")
    w('<p class="note">%s</p>' % K("Rampa payı döngüde P1.1 (akü 3,0 kg) ile değişti ve iyileşti; regresyon tabanı o paketten beri bu değerle. "
                                   "Son koşunun karşılaştırma sütunu (aynı) bir önceki tabana göredir.", DONGU))

    # 5. Sayılarla robot
    w('<h2 id="sayilar">%s</h2>' % K("Sayılarla 1,58 m robot", BRIEF))
    w('<p class="note">README ve demo sayfasıyla aynı kaynaklar ve aynı biçim (<code>F9d-tarama.py</code> README denetimi, demo <code>script#kaynak</code>). '
      'Maliyet toplamları <code>maliyet.json</code>\'dan README / demo kuralıyla hesaplanır (V3 satırları, yazıcı, yedek, %s pay).</p>' % (
          J(ML, "pay", "2")))
    w('<div class="tbl"><table class="yigin"><thead><tr><th>Konu</th><th>Değer</th><th>Kaynak (dosya · anahtar)</th></tr></thead><tbody>')

    def sat(konu, deger, kay):
        w("<tr>%s%s%s</tr>" % (td(konu, "Konu"), td(deger, "Değer", "n"), td(kay, "Kaynak")))
    sat("Boy", J(LK, "toplam_boy_mm", "1") + " mm", "<code>%s</code> · <code>toplam_boy_mm</code>" % LK)
    sat("Parça (ana montaj)", J(MA, "parca_sayisi", "i"), "<code>%s</code> · <code>parca_sayisi</code>" % MA)
    # P10.9c: bağlantı elemanı sayısı demo ile aynı kaynaktan (demo anahtarı p_bag = montaj-analiz.json, tür Baglanti)
    sat("Bağlantı elemanı (ana montaj)", J(DEMO, "anahtarlar.p_bag.deger", "i"),
        "<code>%s</code> · <code>script#kaynak</code> <code>p_bag</code> (<code>%s</code>, tür <code>Baglanti</code>)" % (DEMO, MA))
    sat("Kütle, ana montaj", J(MA, "kutle_g", "2") + " g", "<code>%s</code> · <code>kutle_g</code>" % MA)
    # P10.9c: tam çakışma taraması (P10.7b2j, tek koşu)
    sat("Tam çakışma taraması", "koşu %s, %s bölüm, eklem aralığında %s çakışma (toplam %s çakışma, hepsi eklem aralığı dışında); tarama kütlesi %s kg" % (
        J(CS, "bolumler.statik.kosu", "s"), J(CS, "bolumler#say"), J(CS, "toplam.eklem_araliginda"), J(CS, "toplam.cakisma"), J(CS, "kutle_toplam_g", "k2")),
        "<code>%s</code> · <code>bolumler.statik.kosu</code>, <code>bolumler#say</code>, <code>toplam.eklem_araliginda</code>, <code>toplam.cakisma</code>, "
        "<code>kutle_toplam_g</code>" % CS)
    sat("Kütle, ev pozu, kablo payıyla", "%s g (pay %s g)" % (J(UI, "ev.kutle_g", "1"), J(UI, "kablo_payi.kutle_g", "0")),
        "<code>%s</code> · <code>ev.kutle_g</code>, <code>kablo_payi.kutle_g</code>" % UI)
    sat("Servo", "%s (DS3235 %s, MG996R %s)" % (J(DEMO, "anahtarlar.servo.deger", "0"), J(DEMO, "anahtarlar.s_ds.deger", "0"), J(DEMO, "anahtarlar.s_mg.deger", "0")),
        "<code>%s</code> · <code>script#kaynak</code> <code>servo</code>, <code>s_ds</code>, <code>s_mg</code>" % DEMO)
    sat("Baskı: parça", "%s adet, %s tür, %s destekli" % (J(BA, "toplam.adet"), J(BA, "parcalar#say"), J(BA, "toplam.destekli_adet")),
        "<code>%s</code> · <code>toplam.adet</code>, <code>parcalar#say</code>, <code>toplam.destekli_adet</code>" % BA)
    sat("Baskı: filament (destek dahil)", "%s–%s kg (destek %s g)" % (J(BA, "toplam.toplam_g.0", "k2"), J(BA, "toplam.toplam_g.1", "k2"), J(BA, "toplam.destek_g.0", "1")),
        "<code>%s</code> · <code>toplam.toplam_g</code>, <code>toplam.destek_g.0</code>" % BA)
    sat("Baskı: PETG / PETG-CF", "%s kg / %s–%s kg" % (J(YB, "toplam.petg_g.0", "k2"), J(YB, "toplam.cf_g.0", "k2"), J(YB, "toplam.cf_g.1", "k2")),
        "<code>%s</code> · <code>toplam.petg_g.0</code>, <code>toplam.cf_g</code>" % YB)
    sat("Baskı: süre", "%s–%s sa" % (J(BA, "toplam.sure_sa.0", "2"), J(BA, "toplam.sure_sa.1", "2")), "<code>%s</code> · <code>toplam.sure_sa</code>" % BA)
    sat(K("Baskı partileri 0–4 (adet)", PT), " / ".join(J(PT, "partiler.%d.toplam.adet" % i) for i in range(5)),
        "<code>%s</code> · <code>partiler.N.toplam.adet</code>" % PT)
    sat("Maliyet, genel", J(ML, "=genel", "2") + " TL", "<code>%s</code> · hesap <code>genel</code> (README ≈)" % ML)
    sat("Maliyet, koşullularla", J(ML, "=kosullu", "2") + " TL", "<code>%s</code> · hesap <code>kosullu</code>" % ML)
    sat("Maliyet, elimizdekiler düşülürse", J(ML, "=elde_dusulmus", "2") + " TL", "<code>%s</code> · hesap <code>elde_dusulmus</code>" % ML)
    sat("Maliyet, yüz ekranı satın alınırsa (K32)", J(ML, "=qled", "2") + " TL",
        "<code>%s</code> + <code>%s</code> QLED birincil fiyat" % (ML, SP))
    sat(K("Sipariş paketi toplamı: okul bütçesi (parça + hizmet), doğrulanmamış ve K4 dahil × 1,15", "planlama/d158/F8a-siparis.md"),
        "%s TL (kararsız kalemler hariç %s TL)" % (J(SP, "toplamlar.okul_butcesi_dahil_pay15", "2"), J(SP, "toplamlar.kararsiz_haric_pay15", "2")),
        "<code>%s</code> · <code>toplamlar.okul_butcesi_dahil_pay15</code>, <code>toplamlar.kararsiz_haric_pay15</code>" % SP)
    sat("Bütçe farkı, satın alınacaklar (K28)", J(SP, "toplamlar.fark_alinacaklar", "2") + " TL", "<code>%s</code> · <code>toplamlar.fark_alinacaklar</code>" % SP)
    sat("Rehber: adım", "%s (veri %s)" % (J(RK, "ozet.adim"), J(RV, "adimlar#say")), "<code>%s</code> · <code>ozet.adim</code>; <code>%s</code> · <code>adimlar#say</code>" % (RK, RV))
    sat("Rehber: parça", "%s (mesh %s)" % (J(RK, "ozet.parca_rehber", "i"), J(RK, "ozet.parca_mesh", "i")), "<code>%s</code> · <code>ozet.parca_rehber</code>, <code>ozet.parca_mesh</code>" % RK)
    sat("Rehber: PDF", "%s sayfa, en küçük yazı %s pt" % (J(RK, "yazdir.pdf_sayfa"), J(RK, "yazdir.en_kucuk_yazi_pt_pdf", "1")),
        "<code>%s</code> · <code>yazdir.pdf_sayfa</code>, <code>yazdir.en_kucuk_yazi_pt_pdf</code>" % RK)
    sat("Demo: JSON anahtarı", J(DEMO, "anahtarlar#say"), "<code>%s</code> · <code>script#kaynak</code> <code>anahtarlar</code>" % DEMO)
    w("</tbody></table></div>")
    w('<p class="note">Bağlantılar: <a href="../../rehber/index.html">3B montaj rehberi</a> · <a href="../rehber/Lale-montaj-rehberi.pdf">yazdırılabilir rehber (PDF)</a> · '
      '<a href="../../tasarim/Robot-Tasarim-Demosu.html">tasarım demosu</a> · <a href="testler/testler.html">test kâğıtları</a> · '
      '<a href="../../README.md">README</a>.</p>')

    # 6. Takvim
    w('<h2 id="takvim">Takvim (S-göreli)</h2>')
    w('<p class="note">%s Kaynak <code>%s</code> "İki örnek" tablosu, birebir; takvimin JSON karşılığı yok.</p>' % (
        K("S = sipariş günü, S+n = n hafta sonra. Durum A: erken kupon alımı, Parti 1 ≈ S−0,5 → S+1,5, lazer ≤ 1 hf; durum B: bu koşullar yok.", PLAN), PLAN))
    # Tablo: başlık satırından sonraki ayraç satırı atlanır, tablo ilk "|" ile başlamayan satırda biter; boş hücreler korunur.
    satirlar_ = oku(PLAN).splitlines()
    bas = [i for i, l in enumerate(satirlar_) if l.startswith("| Kapı | A göreli")][0]
    hucre = lambda l: [c.strip() for c in l.strip().strip("|").split("|")]
    basliklar = hucre(satirlar_[bas])
    w('<div class="tbl"><table class="yigin" id="takvim-tablo"><thead><tr>%s</tr></thead><tbody>' % "".join("<th>%s</th>" % K(b, PLAN) for b in basliklar))
    for l in satirlar_[bas + 1:]:
        if not l.startswith("|"):
            break
        if re.match(r"\|[-| :]+\|$", l.strip()):
            continue
        h = hucre(l)
        if len(h) != len(basliklar):
            raise SystemExit("takvim satırı %d hücre, başlık %d: %s" % (len(h), len(basliklar), l))
        w("<tr>%s</tr>" % "".join(td(K(c, PLAN), html.escape(basliklar[i])) for i, c in enumerate(h)))
    w("</tbody></table></div>")
    w('<p class="note">%s</p>' % K("Kaynaktaki sonuç: **S = 16.11:** **yalnız durum A'da** sığar (bir hafta tampon). Bunun için erken kupon alımı "
                                   "ve DXF/teklif **bu hafta (H7)** olmalı.", PLAN))
    w('<p class="note">%s</p>' % K("Kritik yol ve hafta tablosu: `proje-plani.md`; rapor P9.1 (F9a). Sipariş 08.11 itibarıyla verilmedi; her hafta gecikme demoyu bir hafta kaydırır.", PLAN, DONGU))
    w('<p class="note">%s</p>' % K("F10 sonu notu: takvim F9 sonu (09.11) hâlidir, F10'da yenilenmedi; 16.11 siparişinin verilip verilmediği "
                                   "kayıtta yok (karar kuyruğunun ortak ön sorusu).", KUYRUK, GUN))

    # 7. Paket envanteri
    w('<h2 id="paketler">Paket envanteri (%s)</h2>' % H("paket_sayisi", len(paket)))
    w('<p class="note">%s</p>' % K(
        "Durum `dongu-158.md` §3 tablolarından (çalışma ağacı), commit'ler `git log`'dan: konu satırındaki P kodu, paket etiketi "
        "(brief başlığındaki P kodlarıyla) ve §5'te tek başlıklı ✅ kayıt satırı. Her paket bu tabloda bir kez.", DONGU))
    w('<div class="tbl"><table class="yigin" id="paket-tablo"><thead><tr><th>Kod</th><th>İş</th><th>Durum</th><th>Sonuç</th><th>Commit</th><th>Rapor</th></tr></thead><tbody>')
    for p in paket:
        is_ = re.split(r"[:(;]", p["is_"], maxsplit=1)[0].strip().rstrip(".")
        if len(is_) > 90:
            is_ = is_[:88].rsplit(" ", 1)[0] + " …"
        if is_.count("`") % 2:   # kesilen kod parçası: açık kalan ` kaldırılır (F9c-kontrol D-7)
            i = is_.rfind("`")
            is_ = is_[:i] + is_[i + 1:]
        if p["kod"] == "P8.1":   # doğrulanan satır sayısı F8a-siparis.json sayacından (F9c-kontrol D-2)
            sy = jdeger(SP, "toplamlar.sayac")
            son = "%s satırın %s'ü tam doğrulandı (%s onaylı + %s onaylı olmayan); %s" % (
                J(SP, "toplamlar.sayac.siparis_satiri"), H("p81_dogrulanan", sy["dogrulandi_onayli"] + sy["dogrulandi_onaysiz"]),
                J(SP, "toplamlar.sayac.dogrulandi_onayli"), J(SP, "toplamlar.sayac.dogrulandi_onaysiz"),
                K(PAKET_SONUC["P8.1"][0], *PAKET_SONUC["P8.1"][1]))
        elif p["kod"] == "P9.3":   # kapalı paket: F9 sonu sayfasının değerleri, canlı sayım değil (P10.9a kontrolü B7)
            son = K("F9 sonu sayfası (09.11): 36 paket, 47 / 52 açık karar, 10 korunan değer; F10 yenilemesi P10.9.", DONGU, BRIEF)
        else:
            m, kay = P10_9_KAPALI if (p["kod"] == "P10.9" and p["emoji"] == "✅") else PAKET_SONUC[p["kod"]]
            son = K(m, *kay)
        hs = '<span data-muaf="komit">%s</span>' % (", ".join("<code>%s</code>" % h for h in harita[p["kod"]]) or "—")
        rp = ", ".join('<a href="%s">%s</a>' % (r, "bu rapor" if r == "sonuc-rapor.html" else r[:-11]) for r in raporlar(p["kod"], etk)) or "—"
        if p["kod"] == "P5.3":  # F5b'nin rapor dosyası yok (orkestratör: belirt)
            rp += " · F5b: rapor yok, kayıt <code>F5-rapor.html</code>'de"
        w('<tr data-paket="%s">%s%s%s%s%s%s</tr>' % (p["kod"], td(p["kod"], "Kod", "kod"), td(K(is_, DONGU), "İş"), td(durum_tag(p["emoji"]), "Durum"),
                                                    td(son, "Sonuç"), td(hs, "Commit"), td(rp, "Rapor")))
    w("</tbody></table></div>")

    # 8. Açık düşükler
    ge = [d for d in dus if d["grup"] == "elektrik"]
    gd = [d for d in dus if d["grup"] != "elektrik"]
    w('<h2 id="dusukler">Açık düşükler ve doğrulanmamış kritik başlıklar (%s)</h2>' % H("dusuk_sayisi", len(dus)))
    w('<p class="note">%s</p>' % K(
        "Kaynak: paketlerin `*-kontrol.md` dosyalarının son hâli (yeniden kontrol bölümleri dahil); veri `F9c-dusukler.json`. Sonraki pakette "
        "kapanan, kayıt ajanının uyguladığı koşullar ve eylemsiz bilgi notları dışarıda; liste ve gerekçe `F9c-gunluk.md` §6. Aynı konudaki "
        "bulgular tek satırda; satır numaraları kontrol dosyasınındır.", "planlama/d158/F9c-gunluk.md"))
    # P10.9c düzeltme turu 1 (O5): bölüm F9 sonu hâli; kayıtla çelişen satırlara F10 notu (DUSUK_F10 ya da kuyrukta kapanan K kodları)
    kkapali = {k["k"] for k in kr if not k["acik"]}
    w('<p class="note">%s</p>' % K(
        "F10 sonu notu: bu bölüm F9 sonu (09.11) itibarıyla; satırlar F10'da yeniden değerlendirilmedi. \"Önerilen sonraki adım\" "
        "hücresindeki F10 notları iki türlü: \"kapandı\" diyen not yalnız elle kayıtla doğrulanan satırda (ikinci P6KE6V8A P10.7b2j'de "
        "modelde; K11 · K52); öbür satırlarda not yalnız ilgili kararın kuyrukta kapandığını söyler, bulgudaki ölçüm ya da iş ayrıca açık "
        "olabilir.",
        GUN, KUYRUK))

    def dusuk_not(d):
        if d["kod"] in DUSUK_F10:
            m_, k_ = DUSUK_F10[d["kod"]]
            return ' <span class="note">%s</span>' % K(m_, *k_)
        ks_ = sorted({x for x in re.findall(r"\bK\d+\b", " ".join((d["kod"], d["cumle"], d["adim"]))) if x in kkapali},
                     key=lambda x: int(x[1:]))
        return (' <span class="note">%s</span>' % K("F10 sonu: karar kuyrukta kapandı (%s); bu satırdaki ölçüm / iş ayrıca açık olabilir, kuyruğa bak." % ", ".join(ks_), KUYRUK)) if ks_ else ""
    for baslik, liste, gid in (("Elektrik ve acil stop güvenliği", ge, "elektrik"), ("Diğer", gd, "diger")):
        w("<h3>%s (%s)</h3>" % (baslik, H("dusuk_" + gid, len(liste))))
        w('<div class="tbl"><table class="yigin"><thead><tr><th>Paket</th><th>Kod</th><th>Tür</th><th>Bulgu</th><th>Önerilen sonraki adım</th></tr></thead><tbody>')
        for d in liste:
            w('<tr data-dusuk="%s">%s%s%s%s%s</tr>' % (gid, td('<span data-satir="%s">%s</span>' % (
                html.escape(d["yer"]), html.escape(d["yer"])), "Paket"),
                                                      td(K(d["kod"], *d["kaynak"]), "Kod"),
                                                      td('<span class="tag %s">%s</span>' % ("crit" if d["tur"] == "doğrulanmadı" else "wait", d["tur"]), "Tür"),
                                                      td(K(d["cumle"], *d["kaynak"]), "Bulgu"), td(K(d["adim"], *d["kaynak"]) + dusuk_not(d), "Sonraki adım")))
        w("</tbody></table></div>")

    # 9. Kayıt notları
    w('<h2 id="tutarlilik">Kayıt notları (orkestratöre)</h2>')
    w('<h3>%s</h3><ol class="list">' % K("F10 sonu (19.11.2026, P10.9c)", GUN, F10Y))
    for m, kay in TUTARSIZ_F10:
        w("<li>%s</li>" % K(m, *kay))
    w('</ol><h3>%s</h3><ol class="list">' % K("F9 sonu (09.11.2026, P9.3; tarihî, olduğu gibi)", BRIEF))
    for m, kay in TUTARSIZ:
        w("<li>%s</li>" % K(m, *kay))
    w("</ol>")
    if eksik or eslesmeyen:
        w('<p class="note">Commit eşlemesi: plandaki bulunamayan hash %s, pakete bağlanamayan döngü commit\'i %s (günlükte).</p>' % (
            H("hash_eksik", len(eksik)), H("komit_eslesmeyen", len(eslesmeyen))))

    # 10. Paket raporları
    w('<h2 id="raporlar">Paket raporları</h2><p>')
    rr = sorted(r for r in os.listdir(BURASI) if r.endswith("-rapor.html"))
    w(" · ".join('<a href="%s">%s</a>' % (r, r[:-11]) for r in rr))
    w('</p><p class="note">Plan: <a href="../dongu-158.md">dongu-158.md</a> · karar kuyruğu: <a href="karar-kuyrugu.md">karar-kuyrugu.md</a> · '
      'regresyon: <a href="regresyon.json">regresyon.json</a>, <a href="regresyon-son-kosu.json">regresyon-son-kosu.json</a> · '
      'brief: <a href="F9c-brief.md">F9c-brief.md</a> · günlük: <a href="F9c-gunluk.md">F9c-gunluk.md</a> · F10 sonu günlüğü: '
      '<a href="P109c-gunluk.md">P109c-gunluk.md</a>.</p>')
    w('<footer>Uygulama ajanı · P10.9c (F10 sonu) · %s · %s paket, %s açık karar, korunan değer %s/%s aynı · Üretici <code>F9c-uret.py</code>, denetim <code>F9c-dogrula.py</code> %s.</footer>' % (
        K("19.11.2026", GUN, F10Y), H("paket_sayisi", len(paket)), H("karar_acik", len(acik)),
        H("reg_ayni", sum(1 for x in r1["karsilastirma"] if x["durum"] == "aynı")), H("reg_sayi", len(r1["degerler"])),
        K("(çıkış 0 = JSON değerleri kaynakla aynı; metin sayıları kaynak dosyada geçiyor; takvim, P8.1 ve düşük satırları kaynağa karşı "
          "ayrıca denetlendi; sınırlı denetimler günlükte)", "planlama/d158/F9c-dogrula.py")))
    w("</main>\n<script>\n%s\n</script>\n</body>\n</html>\n" % TEMA_JS)
    return "\n".join(o), dict(paket=paket, harita=harita, eksik=eksik, eslesmeyen=eslesmeyen, kom=kom, kr=kr, acik=acik, fk=fk, dus=dus, say=say)


def main():
    arg = sys.argv[1:]
    # P10.7b2e düzeltme turu 1 (F10m-kontrol kaza notu): --help / -h ya da tanınmayan bayrak yazmadan durur (eskiden tanınmayan bayrak
    # görmezden gelinip depodaki sonuc-rapor.html'in üzerine yazılıyordu)
    if "-h" in arg or "--help" in arg:
        print(__doc__.split("\n\nSayıların bağı")[0])
        return 0
    bilinmeyen = [a for i, a in enumerate(arg) if a not in ("--kuru", "--cikti") and not (i > 0 and arg[i - 1] == "--cikti")]
    if bilinmeyen or (arg and arg[-1] == "--cikti"):
        print("bilinmeyen bayrak ya da eksik değer: %s (yazılmadı; kullanım için --help)" % (" ".join(bilinmeyen) or "--cikti YOL"),
              file=sys.stderr)
        return 2
    cikti = CIKTI
    if "--cikti" in arg:   # P10.9a: depo dışına deneme üretimi (göreli bağlantılar sayfanın asıl yerine, planlama/d158/'ye göredir)
        cikti = arg[arg.index("--cikti") + 1]
    metin, b = uret()
    print("paket %d (%s); komit %d; plandaki bulunamayan hash %d; eşleşmeyen commit %d" % (
        len(b["paket"]), ", ".join("%s %d" % (e, n) for e, n in b["say"].items() if n), len(b["kom"]), len(b["eksik"]), len(b["eslesmeyen"])))
    for x in b["eksik"]:
        print("  bulunamayan hash:", x)
    for x in b["eslesmeyen"]:
        print("  eşleşmeyen commit:", x[0], x[1][:90])
    for p in b["paket"]:
        print("  %-5s %s %s" % (p["kod"], p["emoji"], " ".join(b["harita"][p["kod"]]) or "-"))
    print("karar: toplam %d, açık %d; faz: %s" % (len(b["kr"]), len(b["acik"]), ", ".join("%s %d" % (f, len(v)) for f, v in sorted(b["fk"].items()))))
    eksik_grup = [k["k"] for k in b["acik"] if k["k"] not in GRUP]
    fazla_grup = [k for k in GRUP if k not in {x["k"] for x in b["acik"]}]
    if eksik_grup:
        print("GRUP uyuşmazlığı: eksik %s" % eksik_grup)
        return 1
    if fazla_grup:   # kapanan kararın grubu sayfaya girmez; bilgi (P10.9a: K1, K10, K11, K14 kapandı 14.11)
        print("bilgi: GRUP'ta kapanmış karar %s" % fazla_grup)
    if "--kuru" in sys.argv:
        return 0
    with open(cikti, "w", encoding="utf-8", newline="\n") as f:
        f.write(metin)
    print("yazıldı:", os.path.abspath(cikti) if cikti != CIKTI else os.path.relpath(CIKTI, KOK).replace("\\", "/"),
          "(%d bayt)" % len(metin.encode("utf-8")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
