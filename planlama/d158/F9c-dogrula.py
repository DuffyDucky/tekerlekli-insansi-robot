# -*- coding: utf-8 -*-
"""F9c (P9.3): sonuc-rapor.html denetimi. Yalnız okur (--goruntu verilirse yalnız planlama/d158/F9c-goruntu-*.png yazar).

    py -3 -B planlama/d158/F9c-dogrula.py                 # statik denetimler + headless Chrome (file://, 1400 ve 360 px)
    py -3 -B planlama/d158/F9c-dogrula.py --tarayicisiz   # yalnız statik denetimler
    py -3 -B planlama/d158/F9c-dogrula.py --goruntu       # ek olarak ekran görüntüleri
    py -3 -B planlama/d158/F9c-dogrula.py --sayfa YOL     # sonuc-rapor.html yerine YOL'daki sayfa (P10.9a, deneme üretimi;
                                                          # göreli bağlantılar yine planlama/d158/'ye göre çözülür)

İsteğe bağlı ortam değişkenleri (değerleri hiçbir yere basılmaz): TAKMA_AD (takma ad), SOYADLAR (virgülle ayrılmış soyadlar).

Denetimler (çıkış 0 = hepsi geçti):
  1. data-j: her JSON / git / hesap değeri kaynaktan yeniden okunur, aynı biçimle sayfadaki metinle karşılaştırılır.
  2. data-h: sayımlar bu betiğin kendi ayrıştırmasıyla (plan, karar kuyruğu, regresyon, git log, F9c-dusukler.json).
  3. data-kaynak: metindeki her sayı, listelenen kaynak dosyalarından en az birinde birebir geçer.
  4. Bağsız sayı: <body> metnindeki her sayı data-j / data-h / data-kaynak / data-muaf altında.
  5. Paket envanteri: dongu-158.md §3'teki her paket tabloda tam bir kez; sayı eşit; satırın Durum hücresi plandaki emojiyi taşır.
     Faz özet satırı her faz için bir kez, Durum = paketlerin en kötüsü. F10 ve sonrasının Sonuç metni: "Açık" öneki plan
     durumuyla, "Kapalı alt paketler" / "Sürüyor" listesi plandaki alt paket başlıklarıyla, K kodları kuyrukla tutarlı.
     Plan Durum hücresindeki her hash o paketin commit hücresinde (P10.9a düzeltme turu 1).
  5b. Kaynaktan bağımsız: takvim tablosu proje-plani.md "İki örnek" tablosuyla satır ve hücre hücre; P8.1 doğrulanan satır sayısı
      F8a-siparis.json sayacından ve F8a-rapor.html metninden; düşük satırları sayfa = F9c-dusukler.json (grup grup); kontrol
      dosyalarındaki her KT- kodu açık düşüklerde, karar kuyruğunda ya da günlük §6'da.
  Sınırlı (totolojiye yakın) kalanlar F9c-gunluk.md §12'de: grup sayıları, data-kaynak alt dize eşleşmesi, data-satir yalnız uzunluk,
  maliyet hesabı üreticiyle aynı fonksiyon, hash'in hangi pakete ait olduğu.
  6. Açık kararlar: karar kuyruğunun açık maddelerinin her biri bir kez; kuyruktaki "Açık: N" satırıyla ve KAPANDI başlıklarıyla tutarlı.
  7. Göreli bağlantılar: href / src hedefi var.
  8. Yerel kullanıcı yolu (F9d-tarama.py deseni) sonuc-rapor.html ve F9c-* dosyalarında 0; TAKMA_AD / SOYADLAR verilirse 0.
  9. Tarayıcı: konsol hatası 0, 1400 ve 360 px'te yatay kaydırma 0.
"""
import html.parser
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(BURASI, "..", ".."))
SAYFA = os.path.join(BURASI, "sonuc-rapor.html")
DONGU, KUYRUK = "planlama/dongu-158.md", "planlama/d158/karar-kuyrugu.md"
DEMO, ML, SP = "tasarim/Robot-Tasarim-Demosu.html", "planlama/maliyet.json", "planlama/d158/F8a-siparis.json"
REG_SON, DUSUK = "planlama/d158/regresyon-son-kosu.json", "planlama/d158/F9c-dusukler.json"
SAYI = re.compile(r"(?<![0-9A-Za-z_\-+#.,])\d+(?:[.,]\d+)*(?![0-9A-Za-z_])")
HATA = []
PUSH_SOL = re.compile(r"\b[0-9a-f]{7}\.\.(?=[0-9a-f]{7}\b)")   # "push A..B" aralığının sol ucu (F9c-uret.py ile aynı)


def hata(m):
    HATA.append(m)
    print("  HATA:", m)


def p(rel):
    return os.path.join(KOK, *rel.split("/"))


def oku(rel):
    with open(p(rel), encoding="utf-8") as f:
        return f.read()


def modul(ad, rel):
    s = importlib.util.spec_from_file_location(ad, p(rel))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


T = modul("f9d_tarama", "planlama/d158/F9d-tarama.py")


def git(*a):
    return subprocess.run(["git", *a], cwd=KOK, capture_output=True, text=True, encoding="utf-8", check=True).stdout


# ------------------------------------------------------------------ HTML ağacı
class Agac(html.parser.HTMLParser):
    """Her öğe: (etiket, öznitelikler, metin parçaları); metin parçası: (metin, ata öznitelik listesi)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.yigin, self.ogeler, self.parca, self.baglanti, self.govde = [], [], [], [], False
        self.bos = {"meta", "link", "br", "img", "input", "hr"}

    def handle_starttag(self, t, a):
        a = dict(a)
        if t == "body":
            self.govde = True
        for k in ("href", "src"):
            if k in a:
                self.baglanti.append(a[k])
        if t in self.bos:
            return
        o = dict(t=t, a=a, metin=[])
        self.ogeler.append(o)
        self.yigin.append(o)

    def handle_endtag(self, t):
        if t in self.bos:
            return
        while self.yigin:
            o = self.yigin.pop()
            if o["t"] == t:
                break

    def handle_data(self, d):
        for o in self.yigin:
            o["metin"].append(d)
        if self.govde and not any(o["t"] in ("script", "style") for o in self.yigin):
            self.parca.append((d, [o["a"] for o in self.yigin]))


# ------------------------------------------------------------------ yeniden hesap
def bicim(v, b):
    if b == "s":
        return str(v)
    if b == "i":
        return T._tr(v)
    if b.startswith("k"):
        return T._s(v / 1000.0, int(b[1:]))
    return T._s(v, int(b))


def coz(veri, anahtar):
    say = anahtar.endswith("#say")
    anahtar = anahtar[:-4] if say else anahtar
    for x in [y for y in anahtar.split(".") if y]:
        veri = veri[int(x)] if isinstance(veri, list) else veri[x]
    return len(veri) if say else veri


def jdeger(dosya, anahtar):
    if anahtar.startswith("="):
        md = json.loads(oku(ML))
        m = T._maliyet(md)
        if anahtar == "=qled":
            q = [s for s in json.loads(oku(SP))["kalemler"] if s.get("ad") == 'Kafa ekranı 10,1" QLED'][0]["birincil"]["fiyat"]
            return (m["ara_elde"] + q) * (1 + md["pay"])
        return m[anahtar[1:]]
    if dosya.startswith("git:"):
        _, c, rel = dosya.split(":", 2)
        return coz(json.loads(git("show", "%s:%s" % (c, rel))), anahtar)
    if dosya == DEMO:
        return coz(json.loads(re.search(r'<script id="kaynak"[^>]*>(.*?)</script>', oku(DEMO), re.S).group(1)), anahtar)
    return coz(json.loads(oku(dosya)), anahtar)


def plan():
    paket, faz = [], None
    for l in oku(DONGU).splitlines():
        if l.startswith("### Faz "):
            faz = l.split()[2].rstrip(":")
        if l.startswith("## 4."):
            faz = None
        m = re.match(r"\| (P\d+\.\d+[a-z]?) \|", l)   # P10.4b gibi harfli plan satırı da paket (P10.9a)
        if m and faz:
            son = l.strip().strip("|").split(" | ")[-1]
            paket.append((m.group(1), next((c for c in son if c in "✅🟡⛔🔄⏳"), "?")))
    return paket


def kuyruk():
    t = oku(KUYRUK)
    rows = []
    for l in t.splitlines():
        h = l.strip().strip("|").split(" | ") if l.startswith("| K") else []
        if len(h) == 5 and re.match(r"K\d+$", h[0].strip()):
            rows.append((h[0].strip(), h[1], h[2], h[4], "**açık**" in h[2]))
    m = re.search(r"\*\*Açık: (\d+)\.?\*\*.*?\*\*Kapandı: (\d+)\.?\*\*", t)   # "**Açık: 49.**" biçimi de (P10.9a)
    kapandi_baslik = re.findall(r"^## (K\d+) .*KAPANDI", t, re.M)
    return rows, (int(m.group(1)), int(m.group(2))) if m else None, kapandi_baslik


def tablo(sayfa, kimlik):
    """id'si verilen tablonun satırları: hücre metinleri (etiketsiz, boşluk sadeleşmiş)."""
    i = sayfa.index('id="%s"' % kimlik)
    j = sayfa.index("</table>", i)
    return [[re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", c))).strip()
             for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
            for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", sayfa[i:j], re.S)]


def fazlar():
    """dongu-158.md §3'teki faz başlıkları sırayla (F0 … F10)."""
    return re.findall(r"^### Faz (F\d+):", oku(DONGU), re.M)


def karar_faz(durum, bloke):
    m = re.search(r"\bF(\d+)[a-z]?\b", durum) or re.search(r"\bP(\d+)\.\d", bloke) or re.search(r"\bP(\d+)\.\d", durum)
    return "F" + m.group(1) if m else "F0"


def main():
    global SAYFA
    arg = sys.argv[1:]
    if "--sayfa" in arg:
        SAYFA = os.path.abspath(arg[arg.index("--sayfa") + 1])
    with open(SAYFA, encoding="utf-8") as f:
        sayfa = f.read()
    a = Agac()
    a.feed(sayfa)
    paket = plan()
    rows, ozet, kapandi_baslik = kuyruk()
    acik = [r for r in rows if r[4]]
    reg = json.loads(oku(REG_SON))
    dus = json.loads(oku(DUSUK))["satirlar"]
    satirlar = [l.split("\t", 1) for l in git("log", "--format=%h\t%s").splitlines() if l]
    f0 = [l for l in oku(DONGU).splitlines() if "**F0 ✅**" in l][0]
    sira = [h for h, _ in satirlar]
    bas = max(sira.index(h) for h in re.findall(r"\b[0-9a-f]{7}\b", f0) if h in sira)

    print("[1] data-j (JSON, git, hesap)")
    nj = 0
    for o in a.ogeler:
        if "data-j" in o["a"]:
            nj += 1
            dosya, anahtar, b = o["a"]["data-j"].split("|")
            bek = bicim(jdeger(dosya, anahtar), b)
            if "".join(o["metin"]) != bek:
                hata("data-j %s %s: sayfa %r, kaynak %r" % (dosya, anahtar, "".join(o["metin"]), bek))
    print("    %d değer kaynakla karşılaştırıldı" % nj)

    print("[2] data-h (sayımlar)")
    say = {e: sum(1 for _, x in paket if x == e) for e in "✅🟡⛔🔄⏳"}
    grup = {g: sum(1 for o in a.ogeler if o["t"] == "tr" and o["a"].get("data-grup") == g) for g in "ABC"}
    fk = {}
    for r in acik:
        f = karar_faz(r[2], r[3])
        fk[f] = fk.get(f, 0) + 1
    beklenen = {"paket_sayisi": len(paket), "karar_acik": len(acik), "karar_toplam": len(rows), "karar_kapali": len(rows) - len(acik),
                "reg_sayi": len(reg["degerler"]), "reg_ayni": sum(1 for x in reg["karsilastirma"] if x["durum"] == "aynı"),
                "komit_sayisi": bas + 1, "dusuk_sayisi": len(dus), "dusuk_elektrik": sum(1 for d in dus if d["grup"] == "elektrik"),
                "dusuk_diger": sum(1 for d in dus if d["grup"] != "elektrik"),
                "p81_dogrulanan": (lambda y: y["dogrulandi_onayli"] + y["dogrulandi_onaysiz"])(json.loads(oku(SP))["toplamlar"]["sayac"])}
    # Commit eşleme notu (P10.9a; F9 sonunda eşleşmeyen 0 olduğu için not sayfada yoktu): eşleşmeyen = döngü commit'lerinden
    # sayfanın hiçbir commit hücresinde geçmeyenler; eksik = plan §3 Durum hücrelerinde ve §5 tek başlıklı ✅ satırlarında
    # git log'da olmayan, rakam içeren 7 haneli hash'ler (üreticinin kuralı, bu betiğin kendi ayrıştırmasıyla).
    hucre_h = set()
    for o in a.ogeler:
        if o["a"].get("data-muaf") == "komit":
            hucre_h |= set(re.findall(r"\b[0-9a-f]{7}\b", "".join(o["metin"])))
    plan_h = []
    for l in oku(DONGU).splitlines():
        b_ = re.findall(r"\b(F\d+[a-z]?|P\d+\.\d+[a-z]?) ✅", l)
        if (len(b_) == 1 and "**%s ✅" % b_[0] in l) or (re.match(r"\| P\d+\.\d+[a-z]? \|", l) and any(k == l.split(" | ")[0][2:] for k, _ in paket)):
            alan = l.strip().strip("|").split(" | ")[-1] if l.startswith("| P") else l
            plan_h += [h for h in re.findall(r"\b[0-9a-f]{7}\b", alan) if re.search(r"\d", h) and h not in sira]
    beklenen.update({"komit_eslesmeyen": sum(1 for h in sira[: bas + 1] if h not in hucre_h), "hash_eksik": len(plan_h)})
    beklenen.update({"paket_" + e: n for e, n in say.items()})
    beklenen.update({"grup_" + g: n for g, n in grup.items()})
    beklenen.update({"faz_karar_" + f: fk.get(f, 0) for f in fazlar()})   # plandaki fazlar (F0 … F10), P10.9a
    nh = 0
    for o in a.ogeler:
        if "data-h" in o["a"]:
            nh += 1
            ad = o["a"]["data-h"]
            if ad not in beklenen:
                hata("data-h tanımsız: " + ad)
            elif "".join(o["metin"]) != str(beklenen[ad]):
                hata("data-h %s: sayfa %r, hesap %r" % (ad, "".join(o["metin"]), beklenen[ad]))
    print("    %d sayım; paket %d, açık karar %d / %d, grup A/B/C %d/%d/%d, düşük %d" % (
        nh, len(paket), len(acik), len(rows), grup["A"], grup["B"], grup["C"], len(dus)))

    print("[3] data-kaynak (metindeki sayılar kaynakta)")
    nk = ns = 0
    onbellek = {}
    for o in a.ogeler:
        if "data-kaynak" in o["a"]:
            nk += 1
            dos = o["a"]["data-kaynak"].split()
            metinler = [onbellek.setdefault(d, oku(d)) for d in dos]
            for s in SAYI.findall("".join(o["metin"])):
                ns += 1
                if not any(s in m for m in metinler):
                    hata("data-kaynak %s: %r kaynakta yok (%s)" % (" ".join(dos), s, "".join(o["metin"])[:90]))
    print("    %d öğe, %d sayı" % (nk, ns))

    print("[3b] data-satir (kontrol dosyası satır numaraları var)")
    nsat = 0
    for o in a.ogeler:
        if "data-satir" in o["a"]:
            for parca in o["a"]["data-satir"].split("·"):
                m = re.match(r"\s*(F\d+[a-z]?)\s+(.*)", parca)
                if not m:
                    continue
                rel = "planlama/d158/%s-kontrol.md" % m.group(1)
                n = len(oku(rel).splitlines())
                for a_, b_ in re.findall(r":(\d+)(?:[–-](\d+))?", m.group(2)):
                    for x in (a_, b_):
                        if x:
                            nsat += 1
                            if int(x) > n:
                                hata("data-satir %s:%s dosyada yok (%d satır)" % (rel, x, n))
    print("    %d satır numarası denetlendi" % nsat)

    print("[4] bağsız sayı")
    bagsiz = 0
    for metin, ata in a.parca:
        if any(("data-j" in x or "data-h" in x or "data-kaynak" in x or "data-muaf" in x or "data-satir" in x) for x in ata):
            continue
        for s in SAYI.findall(metin):
            bagsiz += 1
            hata("bağsız sayı %r: %r" % (s, metin.strip()[:90]))
    print("    bağsız %d" % bagsiz)
    nm = 0
    for o in a.ogeler:
        if o["a"].get("data-muaf") == "komit":
            for h in re.split(r"[,\s]+", "".join(o["metin"]).strip()):
                if h and h != "—":
                    nm += 1
                    if h not in sira:
                        hata("commit hücresinde git log'da olmayan hash %r" % h)
    print("    commit hücresi muafiyeti: %d hash, hepsi git log'da olmalı" % nm)

    print("[5] paket envanteri")
    trp = [o["a"]["data-paket"] for o in a.ogeler if o["t"] == "tr" and "data-paket" in o["a"]]
    kod = [k for k, _ in paket]
    for k in kod:
        if trp.count(k) != 1:
            hata("paket %s tabloda %d kez" % (k, trp.count(k)))
    for k in set(trp) - set(kod):
        hata("tabloda plan dışı paket " + k)
    print("    plan %d, tablo %d, tekrar/eksik %d" % (len(kod), len(trp), sum(1 for k in kod if trp.count(k) != 1)))
    # Satır başına durum: plandaki emoji, satırın Durum hücresinde (F9c-kontrol D-1 f)
    pd = dict(paket)
    for kd, satir in re.findall(r'<tr data-paket="(P\d+\.\d+[a-z]?)">(.*?)</tr>', sayfa, re.S):
        hc = re.findall(r'<td[^>]*data-b="Durum"[^>]*>(.*?)</td>', satir, re.S)
        if not hc or pd.get(kd, "?") not in hc[0]:
            hata("paket %s durum hücresi plandaki %s'yi içermiyor" % (kd, pd.get(kd)))
    # Faz özet satırı (P10.9a kontrolü B2): plandaki her faz tabloda bir kez, Durum = fazdaki paketlerin en kötüsü
    fz = {}
    for kd, em in paket:
        fz.setdefault("F" + re.match(r"P(\d+)\.", kd).group(1), []).append(em)
    en_kotu = lambda ems: next((e for e in "🔄⛔🟡⏳" if e in ems), "✅")
    fsat = re.findall(r'<tr><td data-b="Faz"><b>(F\d+)</b>(.*?)</tr>', sayfa, re.S)
    for f in fazlar():
        hs = [s for k, s in fsat if k == f]
        if len(hs) != 1:
            hata("faz %s özet tablosunda %d kez" % (f, len(hs)))
        elif en_kotu(fz.get(f, [])) not in (re.findall(r'<td data-b="Durum">(.*?)</td>', hs[0], re.S) or [""])[0]:
            hata("faz %s durum hücresi plandaki %s'yi içermiyor" % (f, en_kotu(fz.get(f, []))))
    for k in sorted({k for k, _ in fsat} - set(fazlar())):
        hata("özet tablosunda plan dışı faz " + k)
    # Elle yazılmış durum sözcükleri (P10.9a kontrolü B3), F10 ve sonrası: (a) plandaki durum ✅ değilse Sonuç "Açık" ile
    # başlar, ✅ ise başlamaz; (b) "Kapalı alt paketler:" listesindeki her alt paket planda kapalı, "Sürüyor:" listesindeki
    # açık, planda adı geçen her alt paket bu iki listeden birinde; (c) "Açık (Kxx)" ve "Kalan:" içindeki K kodları kuyrukta
    # açık, "Kxx kapandı" kapalı. Alt paket planda kapalı: kalın başlığı "**P10.7a ✅" ya da "**P10.7b2a (…) ✅ …, kapandı**".
    dongu_t = oku(DONGU)
    kacik = {r[0]: r[4] for r in rows}
    alt = {}
    for kd_, gv in re.findall(r"\*\*(P\d+\.\d+[a-z][a-z0-9]*)\b([^*]*)\*\*", dongu_t):
        alt[kd_] = alt.get(kd_, False) or gv.startswith(" ✅") or "kapandı" in gv
    yaz = lambda t: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t))).strip()
    sonuclar = [(kd, yaz((re.findall(r'<td data-b="Sonuç">(.*?)</td>', s, re.S) or [""])[0]))
                for kd, s in re.findall(r'<tr data-paket="(P\d+\.\d+[a-z]?)">(.*?)</tr>', sayfa, re.S)
                if int(re.match(r"P(\d+)", kd).group(1)) >= 10]
    for kd, sn in sonuclar:
        if (pd.get(kd) != "✅") != sn.startswith("Açık"):
            hata("paket %s sonuç metni plandaki %s durumuyla çelişiyor: %s" % (kd, pd.get(kd), sn[:40]))
        kap = re.search(r"Kapalı alt paketler: (.*?)(?: Sürüyor:| Kalan:|$)", sn)
        sur = re.search(r"Sürüyor: (.*?)(?: Kalan:|$)", sn)
        kap_k = re.findall(r"\b(%s[a-z][a-z0-9]*)\b" % re.escape(kd), kap.group(1)) if kap else []
        sur_k = re.findall(r"\b(%s[a-z][a-z0-9]*)\b" % re.escape(kd), sur.group(1)) if sur else []
        for x in kap_k:
            if not alt.get(x):
                hata("paket %s: %s 'kapalı' yazıyor, planda kapanmamış" % (kd, x))
        for x in sur_k:
            if alt.get(x, True):
                hata("paket %s: %s 'sürüyor' yazıyor, planda %s" % (kd, x, "kapandı" if x in alt else "yok"))
        if kap or sur:
            for x in sorted(a_ for a_ in alt if re.match(re.escape(kd) + r"[a-z]", a_) and a_ not in kap_k + sur_k):
                hata("paket %s: planda geçen alt paket %s sayfada yok" % (kd, x))
        kal = re.search(r"Kalan: (.*)", sn)
        for x in re.findall(r"Açık \((K\d+)\)", sn) + (re.findall(r"\bK\d+\b", kal.group(1)) if kal else []):
            if not kacik.get(x):
                hata("paket %s: %s açık yazıyor, kuyrukta %s" % (kd, x, "kapalı" if x in kacik else "yok"))
        for x in re.findall(r"\b(K\d+(?:, K\d+)*) kapandı", sn):
            for y in x.split(", "):
                if kacik.get(y, True):
                    hata("paket %s: %s kapandı yazıyor, kuyrukta %s" % (kd, y, "açık" if y in kacik else "yok"))
    # Faz özet satırı, F10 ve sonrası: "Kapalı:" listesindeki paketler planda ✅, "Açık:" listesindekiler değil, fazın her paketi
    # birinde; "P10.7'nin a, b1 … alt paketleri" planda kapalı, "(b2d sürüyor)" kapanmamış.
    for f, s in fsat:
        if int(f[1:]) < 10:
            continue
        sn = yaz((re.findall(r'<td data-b="Ana sonuç">(.*?)</td>', s, re.S) or [""])[0])
        kap = re.search(r"Kapalı: (.*?)(?: Açık:|$)", sn)
        ack = re.search(r"Açık: (.*)", sn)
        kp = re.findall(r"\bP\d+\.\d+[a-z]?\b", kap.group(1)) if kap else []
        ap = re.findall(r"\bP\d+\.\d+[a-z]?\b", ack.group(1)) if ack else []
        for x in kp:
            if pd.get(x) != "✅" and x not in re.findall(r"(P\d+\.\d+)'nin", kap.group(1)):
                hata("faz %s: %s 'kapalı' yazıyor, planda %s" % (f, x, pd.get(x)))
        for x in ap:
            if pd.get(x) == "✅":
                hata("faz %s: %s 'açık' yazıyor, planda ✅" % (f, x))
        for x in [k for k, _ in paket if "F" + re.match(r"P(\d+)", k).group(1) == f and k not in kp + ap]:
            hata("faz %s: plandaki %s özet cümlesinde yok" % (f, x))
        for ust, liste in re.findall(r"(P\d+\.\d+)'nin (.*?) alt paketleri", sn):
            for x in re.split(r",\s*|\s+ve\s+", liste):
                if x and not alt.get(ust + x):
                    hata("faz %s: %s%s 'kapalı' yazıyor, planda kapanmamış" % (f, ust, x))
        for ust, x in re.findall(r"(P\d+\.\d+) \(([a-z][a-z0-9]*) sürüyor\)", sn):
            if alt.get(ust + x, True):
                hata("faz %s: %s%s 'sürüyor' yazıyor, planda %s" % (f, ust, x, "kapandı" if ust + x in alt else "yok"))
    # Faz satırındaki karar kimlikleri (sayı aynı kalsa da): "· K53, K54 …" kuyruktan hesaplanan faz kümesiyle aynı
    fkk = {}
    for r in acik:
        fkk.setdefault(karar_faz(r[2], r[3]), set()).add(r[0])
    for f, s in fsat:
        hc = (re.findall(r'<td class="n" data-b="Açık karar">(.*?)</td>', s, re.S) or [""])[0]
        if set(re.findall(r"\bK\d+\b", yaz(hc))) != fkk.get(f, set()):
            hata("faz %s açık karar kimlikleri kuyruktan farklı" % f)
    # Rapor bağlantısı: planlama/d158'deki her paket raporu en az bir paket satırında (F9c-rapor.html F9'un ara raporu, satırı yok)
    rlink = set()
    for _, s in re.findall(r'<tr data-paket="(P\d+\.\d+[a-z]?)">(.*?)</tr>', sayfa, re.S):
        rlink |= set(re.findall(r'href="([^"]+)"', (re.findall(r'<td data-b="Rapor">(.*?)</td>', s, re.S) or [""])[0]))
    for r in sorted(os.listdir(BURASI)):
        if r.endswith("-rapor.html") and r != "F9c-rapor.html" and r not in rlink:
            hata("paket raporu %s hiçbir paket satırında bağlı değil" % r)
    # Commit'in paketi (P10.9a kontrolü): plan Durum hücresindeki her hash (git log'da olan) o paketin commit hücresinde.
    # Bir commit'i başka pakete taşıma bozmasını yakalar; F9c-gunluk §12'deki "hash'in hangi pakete ait olduğu" sınırını daraltır.
    hucre_p = {kd: set(re.findall(r"\b[0-9a-f]{7}\b", yaz((re.findall(r'<td data-b="Commit">(.*?)</td>', s, re.S) or [""])[0])))
               for kd, s in re.findall(r'<tr data-paket="(P\d+\.\d+[a-z]?)">(.*?)</tr>', sayfa, re.S)}
    for l in dongu_t.splitlines():
        m = re.match(r"\| (P\d+\.\d+[a-z]?) \|", l)
        if m and m.group(1) in pd:
            for h in re.findall(r"\b[0-9a-f]{7}\b", PUSH_SOL.sub("", l.strip().strip("|").split(" | ")[-1])):
                if h in sira and h not in hucre_p.get(m.group(1), set()):
                    hata("paket %s: plandaki %s commit hücresinde yok" % (m.group(1), h))
    # Konu öneki yalnız P kodlarından oluşan döngü commit'i ("Lale P1.1:", "Lale P7.4/P9.4:", "Lale P2.1–P2.2:") o paketlerin
    # commit hücresinde; planda paket olmayan harfli kod harfsize iner (P10.7b2c -> P10.7, P4.5a -> P4.5).
    for h, s in satirlar[: bas + 1]:
        on = s.split(": ", 1)[0]
        if not re.fullmatch(r"Lale P\d+\.\d+[a-z0-9]*(?:\s*(?:\+|/|–)\s*P\d+\.\d+[a-z0-9]*)*", on):
            continue
        for x in re.findall(r"P\d+\.\d+[a-z0-9]*", on):
            x = x if x in pd else re.match(r"P\d+\.\d+", x).group(0)
            if x in pd and h not in hucre_p.get(x, set()):
                hata("paket %s: konu öneki bu pakette olan %s commit hücresinde yok" % (x, h))

    print("[5b] kaynaktan bağımsız denetimler (takvim, P8.1, düşükler)")
    # Takvim: proje-plani.md "İki örnek" tablosu bu betiğin kendi ayrıştırmasıyla; satır sayısı ve hücreler sayfadaki tabloyla.
    L = oku("planlama/proje-plani.md").splitlines()
    i0 = next(k for k, l in enumerate(L) if l.startswith("| Kapı | A göreli"))
    kay = []
    for l in L[i0:]:
        if not l.startswith("|"):
            break
        if not l.replace("|", "").replace("-", "").replace(":", "").strip():
            continue
        kay.append([re.sub(r"\s+", " ", re.sub(r"\*\*|`", "", c)).strip() for c in l.strip()[1:-1].split("|")])
    rap = tablo(sayfa, "takvim-tablo")
    if len(kay) != len(rap):
        hata("takvim: kaynak %d satır (başlık dahil), sayfa %d" % (len(kay), len(rap)))
    for n, (x, y) in enumerate(zip(kay, rap)):
        if x != y:
            hata("takvim satır %d: kaynak %r ↔ sayfa %r" % (n, x, y))
    print("    takvim: kaynak %d veri satırı, sayfa %d; hücre farkı %d" % (
        len(kay) - 1, len(rap) - 1, sum(1 for x, y in zip(kay, rap) if x != y)))
    # P8.1: doğrulanan satır sayısı F8a-siparis.json sayacından ve F8a-rapor.html metninden
    sy = json.loads(oku(SP))["toplamlar"]["sayac"]
    m = re.search(r'<tr data-paket="P8\.1">(.*?)</tr>', sayfa, re.S)
    t81 = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))) if m else ""
    m81 = re.search(r"(\d+) satırın (\d+)'ü tam doğrulandı \((\d+) onaylı \+ (\d+) onaylı olmayan\)", t81)
    bek81 = (sy["siparis_satiri"], sy["dogrulandi_onayli"] + sy["dogrulandi_onaysiz"], sy["dogrulandi_onayli"], sy["dogrulandi_onaysiz"])
    if not m81 or tuple(int(x) for x in m81.groups()) != bek81:
        hata("P8.1: sayfa %r, kaynak sayaç %s" % (m81.groups() if m81 else t81[:80], bek81))
    if "%d onaylı + %d onaylı olmayan" % bek81[2:] not in oku("planlama/d158/F8a-rapor.html"):
        hata("P8.1: F8a-rapor.html'de '%d onaylı + %d onaylı olmayan' yok" % bek81[2:])
    print("    P8.1: %d satırın %d'ü doğrulandı (sayaç %d + %d; F8a-rapor.html ile aynı)" % bek81)
    # Düşükler: (a) sayfadaki satırlar F9c-dusukler.json ile grup grup; (b) kontrol dosyalarındaki her KT- kodu ya açık düşükte,
    # ya karar kuyruğunda (karar ya da "iş"), ya günlük §6'da (gerekçeyle dışarıda). Kapanmış düşükleri ayırt etmez (sınırlı).
    for g in ("elektrik", "diger"):
        ns_ = len(re.findall(r'<tr data-dusuk="%s">' % g, sayfa))
        nj_ = sum(1 for d in dus if (d["grup"] == "elektrik") == (g == "elektrik"))
        if ns_ != nj_:
            hata("düşük %s: sayfa %d satır, F9c-dusukler.json %d" % (g, ns_, nj_))
    gun = oku("planlama/d158/F9c-gunluk.md")
    g6 = gun[gun.find("## 6."):gun.find("## 7.")]
    dj, kq = oku(DUSUK), oku(KUYRUK)
    kt, ktsay = set(), {"düşük": 0, "kuyruk": 0, "günlük §6": 0}
    for f in sorted(os.listdir(BURASI)):
        if f.endswith("-kontrol.md") and not f.startswith("F9c"):
            kt |= set(re.findall(r"KT-F\d+[a-z]?-\d+", oku("planlama/d158/" + f)))
    for k in sorted(kt):
        yer = "düşük" if k in dj else "kuyruk" if k in kq else "günlük §6" if k in g6 else None
        if yer:
            ktsay[yer] += 1
        else:
            hata("kontrol dosyasındaki %s ne açık düşüklerde, ne kuyrukta, ne günlük §6'da" % k)
    print("    düşük satırları sayfa = JSON (%d); kontrol dosyalarında %d KT kodu: düşükte %d, kuyrukta %d, günlük §6'da %d" % (
        len(dus), len(kt), ktsay["düşük"], ktsay["kuyruk"], ktsay["günlük §6"]))

    print("[6] açık kararlar")
    trk = [o["a"]["data-karar"] for o in a.ogeler if o["t"] == "tr" and "data-karar" in o["a"]]
    for r in acik:
        if trk.count(r[0]) != 1:
            hata("karar %s tabloda %d kez" % (r[0], trk.count(r[0])))
    for k in set(trk) - {r[0] for r in acik}:
        hata("tabloda açık olmayan karar " + k)
    if not ozet or ozet != (len(acik), len(rows) - len(acik)):
        hata("kuyruk 'Açık / Kapandı' satırı %s, sayım %d / %d" % (ozet, len(acik), len(rows) - len(acik)))
    if sorted(kapandi_baslik) != sorted(r[0] for r in rows if not r[4]):
        hata("KAPANDI başlıkları %s ↔ özet tablosu %s" % (kapandi_baslik, [r[0] for r in rows if not r[4]]))
    print("    kuyruk açık %d (satır %s), tablo %d; kapanan başlık %d" % (len(acik), ozet, len(trk), len(kapandi_baslik)))

    print("[7] göreli bağlantılar")
    goreli = [x for x in a.baglanti if not re.match(r"(?i)(https?:|mailto:|#|data:|javascript:)", x)]
    kirik = [x for x in goreli if not os.path.exists(os.path.normpath(os.path.join(BURASI, x.split("#")[0].split("?")[0])))]
    for x in kirik:
        hata("kırık bağlantı " + x)
    capa = [x for x in a.baglanti if x.startswith("#")]
    kimlik = set(re.findall(r'id="([^"]+)"', sayfa))
    for x in capa:
        if x[1:] not in kimlik:
            hata("çapa hedefi yok: " + x)
    print("    göreli %d (benzersiz %d), kırık %d; sayfa içi çapa %d (hedefsiz %d); dış bağlantı %d" % (
        len(goreli), len(set(goreli)), len(kirik), len(capa), sum(1 for x in capa if x[1:] not in kimlik),
        len(a.baglanti) - len(goreli) - len(capa)))

    print("[8] yerel yol, takma ad, soyad")
    dosyalar = [SAYFA] + ["planlama/d158/" + d for d in sorted(os.listdir(BURASI)) if d.startswith("F9c-")
                                                    and os.path.splitext(d)[1] in (".md", ".py", ".json", ".html", ".txt")]
    yol = ad = soy = 0
    takma = os.environ.get("TAKMA_AD", "").strip().lower()
    soyad = [s.strip() for s in os.environ.get("SOYADLAR", "").split(",") if s.strip()]
    for d in dosyalar:
        t = open(d, encoding="utf-8").read() if os.path.isabs(d) else oku(d)
        n = len(T.PY_DESEN.findall(t))
        yol += n
        if n:
            hata("yerel kullanıcı yolu %d: %s" % (n, d))
        if takma:
            n = t.lower().count(takma)
            ad += n
            if n:
                hata("takma ad %d: %s" % (n, d))
        for s in soyad:
            n = len(re.findall(r"\b%s\b" % re.escape(s), t))
            soy += n
            if n:
                hata("soyad %d: %s" % (n, d))
    print("    %d dosya; yerel yol %d; takma ad %s; soyad %s" % (len(dosyalar), yol, ad if takma else "denetlenmedi (TAKMA_AD yok)",
                                                             soy if soyad else "denetlenmedi (SOYADLAR yok)"))

    if "--tarayicisiz" in arg:
        print("[9] tarayıcı: ATLANDI (--tarayicisiz)")
    else:
        F9B = modul("f9b_dogrula", "planlama/d158/F9b-dogrula.py")
        tb = F9B.tarayici()
        if not tb:
            hata("Chrome / Edge bulunamadı")
        else:
            print("[9] tarayıcı:", os.path.basename(tb), "(DevTools; file://)")
            url = "file:///" + SAYFA.replace("\\", "/")
            profil = tempfile.mkdtemp(prefix="f9c-chrome-")
            c = None
            try:
                c = F9B.Cdp(tb, profil)
                for gen, yuk in ((1400, 1000), (360, 800)):
                    c.ac(url, gen, yuk, bekle=20)
                    o = c.js("(function(){var d=document.documentElement;return {iw:window.innerWidth,sw:Math.max(d.scrollWidth,"
                             "document.body.scrollWidth),cw:d.clientWidth,h:d.scrollHeight}})()") or {}
                    kons = c.hatalar()
                    tasan = c.js("(function(){var w=document.documentElement.clientWidth,n=[];document.querySelectorAll('main *')"
                                 ".forEach(function(e){var r=e.getBoundingClientRect();if(r.right>w+0.5&&!e.closest('.tbl'))n.push(e.tagName)});"
                                 "return n.length})()")
                    print("    %d px: innerWidth %s, scrollWidth %s, clientWidth %s, yükseklik %s, konsol hatası %d, taşan öğe %s" % (
                        gen, o.get("iw"), o.get("sw"), o.get("cw"), o.get("h"), len(kons), tasan))
                    if o.get("iw") != gen:
                        hata("%d px: innerWidth %s" % (gen, o.get("iw")))
                    if o.get("sw", 10 ** 6) > o.get("cw", 0):
                        hata("%d px: yatay kaydırma (scrollWidth %s > clientWidth %s)" % (gen, o.get("sw"), o.get("cw")))
                    if tasan:
                        hata("%d px: %s öğe sayfa genişliğini aşıyor" % (gen, tasan))
                    for k in kons:
                        hata("%d px konsol: %s" % (gen, k))
                    if "--goruntu" in arg:
                        for ad_, sec in ((("%d-ust" % gen), None), (("%d-kararlar" % gen), "#kararlar"),
                                         (("%d-takvim" % gen), "#takvim"), (("%d-paketler" % gen), "#paketler"),
                                         (("%d-dusukler" % gen), "#dusukler")):
                            if sec:
                                c.js("document.querySelector('%s').scrollIntoView()" % sec)
                            else:
                                c.js("window.scrollTo(0,0)")
                            png = os.path.join(BURASI, "F9c-goruntu-%s.png" % ad_)
                            c.goruntu(png)
                            print("      görüntü planlama/d158/" + os.path.basename(png))
            except Exception as e:      # noqa: BLE001
                hata("tarayıcı: %s" % e)
            finally:
                if c:
                    c.kapat()

    print("\nSONUÇ: %s (hata %d)" % ("GEÇER" if not HATA else "GEÇMEZ", len(HATA)))
    return 0 if not HATA else 1


if __name__ == "__main__":
    sys.exit(main())
