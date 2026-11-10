# 3B montaj rehberi: TEK KOMUT (sistem Python'u). CAD değişince:
#   python tasarim/freecad/rehber/rehber_uret.py                 # veri + mesh (FreeCAD, ~20 s) + kontrol + ekran görüntüleri
#   python tasarim/freecad/rehber/rehber_uret.py --veri-yok      # FreeCAD'i atla, yalnız tarayıcı kontrolü + görüntüler
#   python tasarim/freecad/rehber/rehber_uret.py --adimlar 1,4,9  # yalnız seçilen adımların görüntüsü (varsayılan: tümü)
# Adımlar:
#   1) rehber_veri.py (freecadcmd, ASCII başlatıcı: LALE_FC_LAUNCH ortam değişkeni, yoksa ~/.robot-cad/run_fc.py; depo yolu ASCII
#      olmadığı için freecadcmd betiği doğrudan açamıyor) -> rehber/veri/{rehber-veri.json,.js, robot.glb, robot-glb.js}
#   2) her adım için headless Chrome/Edge: rehber/index.html?adim=N&cekim=1 -> --dump-dom ile <html data-hata> (konsol hatası) ve
#      <body data-hazir> kontrolü; --screenshot -> planlama/rehber/goruntu/adim-NN.png
#   3) özet: planlama/rehber/kontrol.json (adım başına hata / hazır / görüntü; F7a: app.js'in <script id="kontrol-veri"> içine yazdığı
#      yeni görünen parça kimlikleri rehber-veri.json'dan beklenen listeyle karşılaştırılır; tüm adımlar koşulunca her parçanın tam
#      bir adımda yeni göründüğü de denetlenir)
# F7b (P7.2) ekleri:
#   4) her adımın yalnız 3B görüntüsü (?sahne=1, açık tema) -> rehber/goruntu/adim-NN.png (yazdırılabilir sürüm bunları kullanır);
#      F10a düzeltme 1: karede model çizili mi pikselden denetlenir, boşsa yeniden çekilir, hâlâ boşsa kontrol.json
#      "yazdir_goruntu.bos" ve çıkış 2
#   5) telefon: 360 px görüntü alanında birkaç adım (DevTools protokolü, Emulation.setDeviceMetricsOverride; Python websockets
#      paketi gerekir; --window-size Chrome'da ~500 px'in altına inmiyor); yatay taşma = belge genişliği - görüntü alanı (0 olmalı) ->
#      <çıktı>/goruntu/telefon-360-adim-NN.png
#   6) yazdırılabilir sürüm rehber/yazdir.html -> headless Chrome --print-to-pdf -> <çıktı>/Lale-montaj-rehberi.pdf; F7c: her adım ≥ 1
#      sayfa (sığmayan adımda "devam" sayfası), PDF sayfası = HTML sayfası, taşan 0, en küçük yazı ≥ 8 pt (DOM + PyMuPDF);
#      adım -> sayfa eşlemesi kontrol.json "yazdir.sayfa_esleme"
#   7) rehber_denetim.py: ASCII kalıntı (veri + tarayıcının bastığı panel ve yazdir metni), parça listesi gruplama, kafa / hoparlör /
#      hub tutarlılığı -> kontrol.json "denetim"
#   --cikti <klasör>: tüm çıktılar o klasöre (bağımsız kontrol depoyu değiştirmeden koşabilsin; F7a-kontrol D-5, F7b-kontrol D-4):
#      kontrol.json, goruntu/ (kontrol + telefon), Lale-montaj-rehberi.pdf ve <klasör>/rehber/ (yazdir.html + veri/rehber-veri.js
#      kopyası + goruntu/adim-NN.png). Depodaki rehber/ yalnız okunur; veri üretimi rehber/veri'ye yazdığı için --veri-yok gerekir.
#   --ek-yok: 4–7'yi atla.
import os, sys, json, subprocess, re, time, urllib.parse, argparse, tempfile, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
REHBER = os.path.join(ROBOT, "rehber")
CIKTI = os.path.join(ROBOT, "planlama", "rehber")                  # --cikti ile değişir (D-5)
GORUNTU = os.path.join(CIKTI, "goruntu")
YAZDIR_KOK = REHBER                                                 # yazdir.html'in okunduğu klasör (--cikti ile kopya)
YAZDIR_GORUNTU = os.path.join(REHBER, "goruntu")                    # yazdir.html'in adım görüntüleri (yalnız 3B)
TELEFON_ADIM = (0, 9, 24, 31, 32, 35, 49)
sys.path.insert(0, HERE)
# ASCII yoldaki FreeCAD başlatıcısı (F7b-kontrol D-5: yerel kullanıcı yolu depoda yazılmaz)
LAUNCH = os.environ.get("LALE_FC_LAUNCH") or os.path.join(os.path.expanduser("~"), ".robot-cad", "run_fc.py")
FCCMD = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "FreeCAD 1.1", "bin", "freecadcmd.exe")
TARAYICI = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]


def veri():
    env = dict(os.environ, FC_SCRIPT=os.path.join(HERE, "rehber_veri.py"))
    t = time.time()
    r = subprocess.run([FCCMD, LAUNCH], env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    satir = [s for s in re.split(r"[\r\n\t]+", out) if s.strip() and "%)" not in s]
    for s in satir:
        if any(k in s for k in ("mesh:", "GLB", "bitti", "M6 bayragi", "UYARI", "Exception", "Error", "rror")):
            print("  " + s.strip())
    if "bitti:" not in out:
        print("HATA: rehber_veri.py bitmedi. Son satirlar:\n" + "\n".join(satir[-15:]))
        sys.exit(1)
    print("veri: %.0f s" % (time.time() - t))


def tarayici():
    for t in TARAYICI:
        if os.path.exists(t):
            return t
    sys.exit("Chrome / Edge bulunamadi")


def url(adim, ek="", sayfa="index.html", kok=None):
    yol = os.path.join(kok or REHBER, sayfa).replace("\\", "/")
    q = ("?adim=%d&cekim=1" % adim if adim is not None else "") + ek
    return "file:///" + urllib.parse.quote(yol, safe="/:") + q


def beklenen(V, s):
    """Veriden (rehber-veri.json) s. adımda yeni görünmesi gereken parçalar: (simdi, alt, hedef sayısı). app.js durum() kuralı:
    tezgâh adımında o alt montajın bu adımda takılanları; robot adımında bu adımda takılanlar (simdi) + bu adımda bağlanan tezgâh alt
    montajları (alt); 0. adımda bitmiş robot (hepsi)."""
    P = V["parcalar"]
    if s == 0:
        return set(), set(), len(P)
    st = V["adimlar"][s]
    if st["tezgah"]:
        return {p["id"] for p in P if p["t"] == st["tezgah"] and p["a"] == s}, set(), 0
    return ({p["id"] for p in P if p["b"] == s and p["a"] == s}, {p["id"] for p in P if p["b"] == s and p["a"] != s}, 0)


def ortak_arg(tb, boyut, sanal=25000):
    return [tb, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--hide-scrollbars",
            "--window-size=%d,%d" % boyut, "--virtual-time-budget=%d" % sanal, "--no-first-run", "--disable-extensions",
            "--user-data-dir=" + os.path.join(tempfile.gettempdir(), "lale-rehber-chrome")]   # açık Chrome profiline bağlanmasın


def dom_al(ortak, u):
    return subprocess.run(ortak + ["--dump-dom", u], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def gorunen_metin(dom, *bolum):
    """DOM dökümünden ekranda görünen metin (kod parçaları ve betikler hariç). bolum: aranacak etiket desenleri."""
    dom = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", dom or "", flags=re.S)   # önce betikler (bölüm deseni içlerine taşmasın)
    parca = []
    for b in bolum:
        parca += re.findall(b, dom, re.S)
    t = " \n ".join(parca) if bolum else dom
    t = re.sub(r"<code>.*?</code>", " ", t, flags=re.S)
    t = re.sub(r"<(?:[^>\"']|\"[^\"]*\"|'[^']*')*>", " ", t)          # etiket (öznitelik değerindeki > dahil)
    return html.unescape(t)


def kontrol(adimlar, boyut=(1400, 900)):
    tb = tarayici()
    os.makedirs(GORUNTU, exist_ok=True)
    V = json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))
    AD = {p["id"]: "%s [%s]" % (p["ad"], p["modul"]) for p in V["parcalar"]}
    ortak = ortak_arg(tb, boyut)
    sonuc = []
    metin = []                                                      # denetim için tarayıcının bastığı panel metni
    simdi_say = {}                                                  # parça -> yeni (simdi) göründüğü adımlar (0 hariç)
    for a in adimlar:
        u = url(a)
        dom = dom_al(ortak, u)
        hata = re.search(r'<html[^>]*data-hata="([^"]*)"', dom)
        hazir = 'data-hazir="1"' in dom
        kv = re.search(r'<script type="application/json" id="kontrol-veri">(.*?)</script>', dom, re.S)
        try:
            g = json.loads(kv.group(1)) if kv and kv.group(1).strip() else None
        except ValueError:
            g = None
        metin.append(("tarayıcı adım %d" % a, gorunen_metin(dom, r'<aside class="panel".*?</aside>', r'<select id="secim".*?</select>',
                                                             r'<div class="lejant".*?</div>')))
        png = os.path.join(GORUNTU, "adim-%02d.png" % a)
        subprocess.run(ortak + ["--screenshot=" + png, u], capture_output=True)
        b_simdi, b_alt, b_hedef = beklenen(V, a)
        s = dict(adim=a, kod=V["adimlar"][a]["kod"], hazir=hazir, hata=hata.group(1) if hata else None,
                 goruntu=os.path.relpath(png, ROBOT).replace("\\", "/"), veri_okundu=g is not None)
        if g is not None:
            g_simdi, g_alt = set(g["simdi"]), set(g["alt"])
            for i in g_simdi:
                if a > 0:
                    simdi_say.setdefault(i, []).append(a)
            fark = sorted(g_simdi ^ b_simdi) + sorted(g_alt ^ b_alt)
            b_sema = sorted(i for i, x in enumerate(V.get("semalar", [])) if x["a"] == a) if a > 0 else []
            s.update(beklenen_simdi=len(b_simdi), gorunen_simdi=len(g_simdi), beklenen_alt=len(b_alt), gorunen_alt=len(g_alt),
                     beklenen_hedef=b_hedef, gorunen_hedef=g["hedef"], eksik_mesh=[AD.get(i, i) for i in g["eksik"]],
                     fark=[AD.get(i, i) for i in fark], sema=len(g.get("sema") or []), sema_fark=sorted(set(g.get("sema") or []) ^ set(b_sema)),
                     kadraj=g.get("kadraj"))
            s["gecti"] = bool(hazir and not s["hata"] and not fark and not g["eksik"] and g["hedef"] == b_hedef and not s["sema_fark"])
        else:
            s["gecti"] = False
        sonuc.append(s)
        print("  adim %2d %-4s hazir=%s hata=%s yeni %s/%s alt %s/%s sema %s kadraj %s %s" % (
            a, s["kod"], hazir, s["hata"] or "-", s.get("gorunen_simdi"), s.get("beklenen_simdi"), s.get("gorunen_alt"),
            s.get("beklenen_alt"), s.get("sema"), s.get("kadraj"), "GECTI" if s["gecti"] else "KALDI"))
    # her parça tam bir adımda (yalnız tüm adımlar koşulduysa anlamlı)
    tum = sorted(adimlar) == list(range(len(V["adimlar"])))
    tek = None
    if tum:
        coklu = {AD[i]: v for i, v in simdi_say.items() if len(v) != 1}
        hic = [AD[p["id"]] for p in V["parcalar"] if p["id"] not in simdi_say]
        tek = dict(gecti=not coklu and not hic and not V.get("atanmamis"), birden_cok_adimda=coklu, hic_gorunmeyen=hic)
    ozet = dict(adim=len(sonuc), gecen=sum(1 for s in sonuc if s["gecti"]), konsol_hatasi=sum(1 for s in sonuc if s["hata"]),
                parca_rehber=len(V["parcalar"]), parca_mesh=V["mesh"]["parca"], atanmamis=V.get("atanmamis", []),
                her_parca_tek_adimda=tek, sema=len(V.get("semalar", [])), veri_uretim=V["uretim"], kaynak_cad=V["kaynak"]["cad"])
    return V, tb, sonuc, ozet, metin, tek


CIZIM_ESIK = 0.01            # F10a düzeltme 1 (B-1): zeminden farklı piksel oranı bunun altındaysa kare boş (model çizilmemiş)
CIZIM_TEKRAR = 3             # boş karede en çok bu kadar yeniden çekim; hâlâ boşsa üretim hata verir


def cizim_orani(png):
    """Karede sahne zemininden (stil.css açık tema --sahne) farklı piksel oranı (4 px adımla örnek). WebGL dışı öğeler sayılmaz: alttaki
    lejant şeridi (yüksekliğin %7'si) ve sağ alttaki küçük görünüm köşesi (genişliğin 1/6'sı x yüksekliğin %36'sı; CSS halka). Boş
    (temizlenmiş) tuvalde oran 0; model çizili karede (zemin ızgarası dahil) 0,02 üstü. PIL yoksa None (denetim geçmez)."""
    try:
        from PIL import Image
    except ImportError:
        return None
    m = re.search(r"--sahne:\s*#([0-9a-fA-F]{6})", open(os.path.join(REHBER, "stil.css"), encoding="utf-8").read())
    z = tuple(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)) if m else (0xec, 0xea, 0xe4)
    with Image.open(png) as im:
        im = im.convert("RGB")
        w, h = im.size
        px = im.load()
        n = f = 0
        x_mini, y_mini, y_lejant = w - w // 6, h - int(h * 0.36), h - int(h * 0.07)
        for y in range(0, y_lejant, 4):
            for x in range(0, w, 4):
                if x >= x_mini and y >= y_mini:
                    continue
                p = px[x, y]
                n += 1
                if abs(p[0] - z[0]) + abs(p[1] - z[1]) + abs(p[2] - z[2]) > 40:
                    f += 1
    return f / max(1, n)


def sahne_goruntu(tb, adimlar):
    """Yazdırılabilir sürüm için yalnız 3B görünüm (açık tema): rehber/goruntu/adim-NN.png. F10a düzeltme 1: her karede modelin
    çizildiği pikselden denetlenir (cizim_orani); boşsa en çok CIZIM_TEKRAR kez yeniden çekilir, hâlâ boşsa "bos" listesine girer."""
    os.makedirs(YAZDIR_GORUNTU, exist_ok=True)
    ortak = ortak_arg(tb, (1200, 720))
    hata, bos, oran, tekrar = [], [], {}, {}
    for a in adimlar:
        png = os.path.join(YAZDIR_GORUNTU, "adim-%02d.png" % a)
        for k in range(CIZIM_TEKRAR + 1):
            t0 = time.time() - 1
            subprocess.run(ortak + ["--screenshot=" + png, url(a, "&sahne=1&tema=light")], capture_output=True)
            if not os.path.exists(png) or os.path.getmtime(png) < t0:
                break                                               # dosya yok ya da eski: eksik (aşağıda)
            r = cizim_orani(png)
            oran[a] = None if r is None else round(r, 4)
            if r is None or r >= CIZIM_ESIK:
                break
            tekrar[a] = k + 1
        if not os.path.exists(png) or os.path.getmtime(png) < time.time() - 120:
            hata.append(a)
        elif oran.get(a) is None or oran[a] < CIZIM_ESIK:
            bos.append(a)
    gecerli = [v for v in oran.values() if v is not None]
    print("yazdir goruntusu: %d adim, eksik %s, bos %s, yeniden cekim %s, en dusuk cizim orani %s" % (
        len(adimlar), hata or "-", bos or "-", tekrar or "-", min(gecerli) if gecerli else "-"))
    return dict(adim=len(adimlar), klasor=os.path.relpath(YAZDIR_GORUNTU, ROBOT).replace("\\", "/"), eksik=hata,
                bos=bos, cizim_esik=CIZIM_ESIK, yeniden_cekim={str(k): v for k, v in sorted(tekrar.items())},
                en_dusuk_cizim_orani=min(gecerli) if gecerli else None, cizim_orani={str(k): v for k, v in sorted(oran.items())},
                piksel_denetimi=bool(gecerli) and len(gecerli) == len(oran))


class Cdp:
    """Headless Chrome'u DevTools protokolüyle sürer (telefon kontrolü). Masaüstü Chrome pencere genişliğini ~500 px'in altına
    indirmediği için 360 px, --window-size ile değil Emulation.setDeviceMetricsOverride ile verilir (gerçek 360 px görüntü alanı)."""

    def __init__(self, tb):
        import websockets.sync.client as WS                        # yalnız telefon kontrolü için gerekir
        prof = os.path.join(tempfile.gettempdir(), "lale-rehber-chrome-cdp")
        os.makedirs(prof, exist_ok=True)
        pf = os.path.join(prof, "DevToolsActivePort")
        t0 = time.time() - 1
        self.p = subprocess.Popen([tb, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--hide-scrollbars",
                                   "--remote-debugging-port=0", "--no-first-run", "--disable-extensions", "--user-data-dir=" + prof,
                                   "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port = None
        for _ in range(150):                                         # DevToolsActivePort bu koşuda yazılana kadar (en çok 30 s)
            if os.path.exists(pf) and os.path.getmtime(pf) >= t0:
                satir = open(pf).read().split()
                if satir:
                    port = int(satir[0])
                    break
            time.sleep(0.2)
        if port is None:
            self.kapat()
            raise RuntimeError("Chrome DevTools portu okunamadi")
        import urllib.request
        hedef = None
        for _ in range(50):
            try:
                hedef = [x for x in json.load(urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port)) if x.get("type") == "page"]
                if hedef:
                    break
            except OSError:
                pass
            time.sleep(0.2)
        self.ws = WS.connect(hedef[0]["webSocketDebuggerUrl"], max_size=None, open_timeout=20)
        self.n = 0

    def cmd(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps(dict(id=self.n, method=method, params=params)))
        while True:
            m = json.loads(self.ws.recv(timeout=60))
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError("%s: %s" % (method, m["error"]))
                return m.get("result", {})

    def js(self, ifade):
        return self.cmd("Runtime.evaluate", expression=ifade, returnByValue=True).get("result", {}).get("value")

    def kapat(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.p.terminate()
        try:
            self.p.wait(15)
        except subprocess.TimeoutExpired:
            self.p.kill()


def telefon(tb, adimlar=TELEFON_ADIM, boyut=(360, 1600)):
    """360 px: yatay taşma (belge genişliği - görüntü alanı) her adımda 0 olmalı; görüntü <çıktı>/goruntu/telefon-360-adim-NN.png."""
    import base64
    os.makedirs(GORUNTU, exist_ok=True)
    sonuc, metin = [], []
    try:
        c = Cdp(tb)
    except Exception as e:                                           # websockets yoksa ya da Chrome açılmazsa kontrol geçmez
        print("telefon kontrolu kosamadi: %s" % e)
        return dict(pencere=list(boyut), sonuc=[], gecti=False, hata=str(e)), []
    try:
        c.cmd("Emulation.setDeviceMetricsOverride", width=boyut[0], height=boyut[1], deviceScaleFactor=1, mobile=True)
        for a in adimlar:
            c.cmd("Page.navigate", url=url(a, "&tema=light"))
            t = time.time()
            while time.time() - t < 60 and c.js("document.body && document.body.dataset.hazir") != "1":
                time.sleep(0.3)
            o = c.js("(function(){var d=document.documentElement,p=document.querySelector('.panel');var o={g:window.innerWidth,"
                     "sw:Math.max(d.scrollWidth,document.body.scrollWidth),cw:d.clientWidth,h:d.dataset.hata||null,"
                     "hz:document.body.dataset.hazir||null,m:''};if(p){var w=document.createTreeWalker(p,NodeFilter.SHOW_TEXT),t=[],x;"
                     "while((x=w.nextNode())){if(!x.parentElement.closest('code,script,style'))t.push(x.nodeValue);}o.m=t.join(' ');}"
                     "return o;})()") or {}                     # metin düğümleri ayrı (yan yana öğeler birleşmesin), kod hariç
            png = os.path.join(GORUNTU, "telefon-360-adim-%02d.png" % a)
            ek = c.cmd("Page.captureScreenshot", format="png", captureBeyondViewport=False)
            open(png, "wb").write(base64.b64decode(ek["data"]))
            d = dict(adim=a, genislik=o.get("g"), belge_genislik=o.get("sw"), tasma_px=(o["sw"] - o["cw"]) if "sw" in o else None,
                     hazir=o.get("hz") == "1", hata=o.get("h"), goruntu=os.path.relpath(png, ROBOT).replace("\\", "/"))
            d["gecti"] = d["genislik"] == boyut[0] and d["tasma_px"] is not None and d["tasma_px"] <= 0 and d["hazir"] and not d["hata"]
            sonuc.append(d)
            metin.append(("telefon adım %d" % a, o.get("m") or ""))
    finally:
        c.kapat()
    print("telefon %d px: %s" % (boyut[0], ", ".join("%d:%s/%s%s" % (d["adim"], d["genislik"], d["tasma_px"], "" if d["hazir"] else " hazir degil")
                                                      for d in sonuc)))
    return dict(pencere=list(boyut), yontem="CDP Emulation.setDeviceMetricsOverride (mobile)", sonuc=sonuc,
                gecti=bool(sonuc) and all(d["gecti"] for d in sonuc)), metin


def pdf_sayfa(yol):
    try:
        from pypdf import PdfReader
        return len(PdfReader(yol).pages)
    except ImportError:
        b = open(yol, "rb").read()
        return len(re.findall(rb"/Type\s*/Page[^s]", b))


YAZI_ALT_PT = 8.0                                                   # F7c (F7b-kontrol D-3): PDF'de en küçük yazı


def pdf_en_kucuk(yol):
    """PDF'deki en küçük yazı boyu (pt; PyMuPDF metin aralıkları, boş aralıklar hariç). PyMuPDF yoksa None (kabul geçmez)."""
    try:
        import fitz
    except ImportError:
        return None
    enk = None
    with fitz.open(yol) as doc:
        for sf in doc:
            for b in sf.get_text("dict")["blocks"]:
                for ln in b.get("lines", []):
                    for sp in ln["spans"]:
                        if sp["text"].strip() and (enk is None or sp["size"] < enk):
                            enk = sp["size"]
    return round(enk, 2) if enk is not None else None


def yazdir(tb, n_adim):
    """rehber/yazdir.html -> <çıktı>/Lale-montaj-rehberi.pdf (A4; adım başına en az bir sayfa, sığmayan adımda "devam" sayfası)."""
    ortak = ortak_arg(tb, (1200, 1700), sanal=15000)
    u = url(None, sayfa="yazdir.html", kok=YAZDIR_KOK)
    dom = dom_al(ortak, u)
    say = re.search(r'<body[^>]*data-sayfa="(\d+)"', dom)
    tas = re.search(r'<body[^>]*data-tasma="([^"]*)"', dom)
    kuc = re.search(r'<body[^>]*data-kucuk="([^"]*)"', dom)
    pdf = os.path.join(CIKTI, "Lale-montaj-rehberi.pdf")
    os.makedirs(CIKTI, exist_ok=True)
    t0 = time.time() - 1
    subprocess.run(ortak + ["--no-pdf-header-footer", "--print-to-pdf-no-header", "--print-to-pdf=" + pdf, u], capture_output=True)
    yeni = os.path.exists(pdf) and os.path.getmtime(pdf) >= t0     # eski PDF sayılmasın
    sayfa = pdf_sayfa(pdf) if yeni else 0
    es = re.search(r'<body[^>]*data-esleme="([^"]*)"', dom)
    enk = re.search(r'<body[^>]*data-en-kucuk-pt="([^"]*)"', dom)
    try:
        esleme = {int(k): v for k, v in json.loads(html.unescape(es.group(1))).items()} if es else {}
    except ValueError:
        esleme = {}
    d = dict(pdf=os.path.relpath(pdf, ROBOT).replace("\\", "/"), pdf_sayfa=sayfa, pdf_yeni=yeni, html_sayfa=int(say.group(1)) if say else None,
             adim=n_adim, tasan=[x for x in (tas.group(1) if tas else "?").split(",") if x],
             kucuk_yazi=[x for x in (kuc.group(1) if kuc else "").split(",") if x],
             boyut_kb=round(os.path.getsize(pdf) / 1024) if yeni else 0,
             # F7c (D-3): adım -> PDF sayfaları (devam sayfaları dahil), en küçük yazı (DOM ve PDF), alt sınır 8 pt
             sayfa_esleme={str(k): esleme[k] for k in sorted(esleme)}, devam_sayfasi=sum(len(v) - 1 for v in esleme.values()),
             en_kucuk_yazi_pt_dom=float(enk.group(1)) if enk else None, en_kucuk_yazi_pt_pdf=pdf_en_kucuk(pdf) if yeni else None,
             yazi_alt_sinir_pt=YAZI_ALT_PT)
    sirali = [p for k in sorted(esleme) for p in esleme[k]]
    d["esleme_tutarli"] = (sorted(esleme) == list(range(n_adim)) and all(len(v) >= 1 for v in esleme.values())
                           and sirali == list(range(1, len(sirali) + 1)) and len(sirali) == d["html_sayfa"])
    kucuk_ok = all(x is not None and x >= YAZI_ALT_PT - 0.01 for x in (d["en_kucuk_yazi_pt_dom"], d["en_kucuk_yazi_pt_pdf"]))
    # kabul (F7c): her adım ≥ 1 sayfa (eşleme sıralı ve kesintisiz), PDF sayfası = HTML sayfası ≥ adım, taşan 0, en küçük yazı ≥ 8 pt
    d["gecti"] = bool(yeni and sayfa == d["html_sayfa"] and sayfa >= n_adim and d["esleme_tutarli"] and not d["tasan"]
                      and not d["kucuk_yazi"] and kucuk_ok)
    print("yazdirilabilir: pdf %d sayfa (adim %d, devam %d), html %s, esleme %s, tasan %s, en kucuk yazi dom %s / pdf %s pt, %d kB" % (
        sayfa, n_adim, d["devam_sayfasi"], d["html_sayfa"], "tutarli" if d["esleme_tutarli"] else "TUTARSIZ", d["tasan"] or "-",
        d["en_kucuk_yazi_pt_dom"], d["en_kucuk_yazi_pt_pdf"], d["boyut_kb"]))
    return d, [("yazdır", gorunen_metin(dom, r'<div id="sayfalar">.*</body>'))]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--veri-yok", action="store_true")
    ap.add_argument("--gorsel-yok", action="store_true")
    ap.add_argument("--ek-yok", action="store_true", help="yazdır görüntüsü, telefon, PDF ve metin denetimini atla")
    ap.add_argument("--adimlar", default="")
    ap.add_argument("--cikti", default="", help="kontrol.json, kontrol görüntüleri ve PDF için klasör (varsayılan planlama/rehber)")
    g = ap.parse_args()
    if g.cikti:
        if not g.veri_yok:
            sys.exit("--cikti ile --veri-yok kullan: veri üretimi depodaki rehber/veri/'ye yazar")
        import shutil
        CIKTI = os.path.abspath(g.cikti)
        GORUNTU = os.path.join(CIKTI, "goruntu")
        YAZDIR_KOK = os.path.join(CIKTI, "rehber")                    # yazdir.html + veri kopyası; görüntüler de burada
        YAZDIR_GORUNTU = os.path.join(YAZDIR_KOK, "goruntu")
        os.makedirs(os.path.join(YAZDIR_KOK, "veri"), exist_ok=True)
        shutil.copy2(os.path.join(REHBER, "yazdir.html"), YAZDIR_KOK)
        shutil.copy2(os.path.join(REHBER, "veri", "rehber-veri.js"), os.path.join(YAZDIR_KOK, "veri"))
    if not g.veri_yok:
        veri()
    if not g.gorsel_yok:
        n = len(json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))["adimlar"])
        ad = [int(x) for x in g.adimlar.split(",") if x.strip()] or list(range(n))
        V, tb, sonuc, ozet, metin, tek = kontrol(ad)
        ek = {}
        if not g.ek_yok:
            import rehber_denetim as RD
            ek["yazdir_goruntu"] = sahne_goruntu(tb, ad)
            ek["telefon"], m2 = telefon(tb)
            ek["yazdir"], m3 = yazdir(tb, n)
            ek["denetim"] = RD.denetle(V, metin + m2 + m3)
            RD.ozet_yaz(ek["denetim"])
        os.makedirs(CIKTI, exist_ok=True)
        json.dump(dict(tarih=time.strftime("%Y-%m-%d %H:%M"), tarayici=os.path.basename(tb), ozet=ozet, sonuc=sonuc, **ek),
                  open(os.path.join(CIKTI, "kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        kotu = [s for s in sonuc if not s["gecti"]]
        ek_kotu = [k for k in ("telefon", "yazdir", "denetim") if k in ek and not ek[k]["gecti"]]
        if ek.get("yazdir_goruntu", {}).get("eksik") or ek.get("yazdir_goruntu", {}).get("bos"):
            ek_kotu.append("yazdir_goruntu")
        print("tarayici kontrolu: %d adim, %d gecti, %d sorunlu, konsol hatasi %d; her parca tek adimda: %s; ek kontrol sorunlu: %s" % (
            len(sonuc), ozet["gecen"], len(kotu), ozet["konsol_hatasi"], tek["gecti"] if tek else "-", ek_kotu or "-"))
        sys.exit(0 if not kotu and (tek is None or tek["gecti"]) and not ek_kotu else 2)
