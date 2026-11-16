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
#   8) F10c: rehber_sira.py: her bağlantı elemanına alet (ışın) + el (voksel, 20 mm) erişimi, adım içi sıra (sira_grup) ve poz ile
#      -> kontrol.json "sira" (ulaşılamaz sınırı 0; aşılırsa ya da bilinen kapalı sınama kaçarsa çıkış 2) ve "perdelenme" (adım başına
#      hiçbir yönden görünmeyen yeni parçalar, sayı + liste; eşik yok). numpy yoksa ikisi "atlandı", üretim kırılmaz. ~2 dk
#   --ek-yok: 4–8'i atla.
# F10d: 9) alt adımlar (CDP, tek tarayıcı): ?adim=N.J -> yeni görünenler beklenenle (app.js durum(p, s, j)), konsol, panel metni
#      (denetim), kontrol görüntüsü <çıktı>/goruntu/adim-NN-JJ.png, yazdırma görüntüsü rehber/goruntu/adim-NN-JJ.png (piksel denetimi);
#      her parça kendi adımının tam bir alt adımında yeni -> kontrol.json "alt_adim". Sıra denetimine uçuş yolu (sira.ucus) eklendi;
#      perdelenme alt adım sınırı (gerekçesiz tamamen gizli 0) çıkış koduna girer.
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
    q = ("?adim=%s&cekim=1" % adim if adim is not None else "") + ek
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
            # F10f: sema_yalniz grubunun şeması (G4 uç duruş yakın kareleri) yalnız kendi alt adımında çizilir (app.js SEMA_YALNIZ);
            # ana adım bakışında beklenmez, alt adım denetimi (beklenen_alt) onu kendi alt adımında arar
            yalniz = {i for g_ in (V["adimlar"][a].get("sira_grup") or []) if g_.get("sema_yalniz") for i in (g_.get("sema") or [])}
            b_sema = sorted(i for i, x in enumerate(V.get("semalar", [])) if x["a"] == a and i not in yalniz) if a > 0 else []
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


# P10.7b2a-Y: basılı sayfa tamlığı. DOM'daki metin tam olsa da sayfa kutusu (.ic, overflow:hidden) kestiği yeri PDF'e basmıyordu
# (K1'in is_'i 10029 karakter; son 3645'i hiçbir sayfada yoktu, "zorunlu uyarı" denetimi DOM metnine baktığı için görmedi). Her adımın
# iş metni (is_), alt adım iş metinleri, notları ve kontrol maddeleri o adımın PDF sayfalarında (sayfa_esleme) aranır: boşluk / satır
# sonu / yumuşak tire / satır sonu tiresi ayıklanır, md() işaretleri (** ve `) düşülür. is_ sırayla, sayfa sayfa en uzun bitişik parça
# olarak eşlenir (atlama yok: ortada düşen bir parça kalanın eşlenmesini durdurur); madde metinleri adımın sayfalarında bütün aranır.
TAM_EN_AZ = 20                                                      # sayfa başına en kısa sayılan is_ parçası (normalize karakter)
# P10.7b2b (F10i-kontrol-4 A1, A2): (1) devam sayfasında iş metninin eşleştiği yerden önce, bir önceki sayfada basılmış is_'in son
# TAM_EN_AZ karakteri yinelenmemeli (bölme sınırında yinelenen satır, B4b); (2) madde (not, kontrol, kablo kancası, alt adım is_) ve
# erişim / bağlantı metni adımın sayfalarında tam kaynaktaki kadar geçmeli: PDF'teki sayı, aynı metnin adımın bütün basılan kaynak
# alanlarında (başlık, is_, alt adım adı / is_, not, kontrol, kablo, erişim, bağlantı, alet, parça ve kablo parçası adları) geçme
# sayısını aşarsa yinelenen basım (B5). F10i-kontrol-4'ün 11 bilinen tekrarı (B5 / B6 başlık = is_, F1 / F4 kısa cümle iki kez, E4 / F3
# alt adım is_'i ana is_'te) bu tabanla yanlış alarm değil.


def _tam_say(s, m):
    """m'nin s içinde örtüşmeyen geçme sayısı."""
    return s.count(m) if m else 0


def _tam_kaynak(st, V, s):
    """Adımın basılan kaynak alanları (normalize, md işaretsiz): yineleme tabanı."""
    alan = [st.get("baslik"), st.get("is_"), st.get("erisim"), st.get("baglanti_md"), st.get("alet")]
    alan += list(st.get("not_") or []) + list(st.get("kontrol") or []) + list(st.get("kablo") or [])
    alan += [x for g in (st.get("sira_grup") or []) for x in (g.get("ad"), g.get("is_"))]
    alan += [x.get("ad") for x in (st.get("parcalar") or []) + (st.get("baglantilar") or []) if isinstance(x, dict)]
    alan += [p.get("ad") for p in V.get("parcalar") or [] if p.get("renk") and p.get("a") == s]
    return [_tam_norm(_tam_md(x)) for x in alan if x]


def _tam_norm(s):
    import unicodedata
    s = unicodedata.normalize("NFKC", s or "").replace("­", "").replace("​", "")
    return re.sub(r"\s+", "", s)


def _tam_md(s):
    return re.sub(r"`([^`]+)`", r"\1", re.sub(r"\*\*([^*]+)\*\*", r"\1", s or ""))


def _tam_eslesen(T, i, P):
    """T[i:j] P'de bitişik geçen en büyük j (önek tekdüze: ikili arama)."""
    lo, hi = i, len(T)
    while lo < hi:
        m = (lo + hi + 1) // 2
        if T[i:m] in P:
            lo = m
        else:
            hi = m - 1
    return lo


def pdf_tamlik(pdf, V, esleme, ham=None):
    """Adım başına basılı metin tamlığı. PyMuPDF yoksa olculdu False (kabul geçmez). ham: sayfa metinleri (bozma denemesi; verilirse
    PDF okunmaz)."""
    if ham is None:
        try:
            import fitz
        except ImportError:
            return dict(olculdu=False, neden="PyMuPDF yok", gecti=False)
        with fitz.open(pdf) as doc:
            ham = [p.get_text("text") for p in doc]
    # iki okuma: olduğu gibi ve satır sonu tiresi (tireleme) silinmiş; parça hangisinde uzunsa o
    oku = [(_tam_norm(t), _tam_norm(re.sub(r"[-‐]\n", "", t))) for t in ham]
    adim, eksik, yineleme = [], [], []
    for s, st in enumerate(V["adimlar"]):
        sf = [p for p in esleme.get(s, []) if 1 <= p <= len(oku)]
        T = _tam_norm(_tam_md(st.get("is_")))
        i, parca = 0, []
        for p in sf:
            jj = [_tam_eslesen(T, i, P) for P in oku[p - 1]]
            j = max(jj)
            if j - i < TAM_EN_AZ and j < len(T):                       # sayfadaki rastlantısal kısa eşleşme ("le", "him") sayılmaz
                j = i
            if j > i and i > 0:                                         # P10.7b2b (B4b): devam sayfasında sınırda yinelenen metin
                P = oku[p - 1][jj.index(max(jj))]
                once = P[:P.find(T[i:j])]
                son = T[max(0, i - TAM_EN_AZ):i]
                if son in once:
                    yineleme.append(dict(adim=s, kod=st.get("kod"), yer="is_", sayfa=p, metin=son))
            parca.append([p, j - i])
            i = j
        r = dict(adim=s, kod=st.get("kod"), sayfa=sf, is_karakter=len(T), is_basilan=i, is_eksik=len(T) - i, sayfa_parca=parca)
        if i < len(T):
            g = _tam_md(st.get("is_"))
            # kesilen yer: işaretsiz metinde, eşlenen normalize karakter sayısına karşılık gelen konum
            n, k = 0, 0
            while k < len(g) and n < i:
                n += len(_tam_norm(g[k]))
                k += 1
            eksik.append(dict(adim=s, kod=st.get("kod"), yer="is_", eksik_karakter=len(T) - i, eksik_ham_karakter=len(g) - k,
                              son_sayfa=parca[-1][0] if parca else None, kesilen_once=g[max(0, k - 50):k], kesilen_sonra=g[k:k + 60]))
        madde = [("not_", t) for t in st.get("not_") or []] + [("kontrol", t) for t in st.get("kontrol") or []]
        madde += [("kablo", t) for t in st.get("kablo") or []]          # P10.7b2b (F10i-kontrol-4 A2): kablo kancası, erişim, bağlantı
        madde += [(k, st.get(k)) for k in ("erisim", "baglanti_md") if st.get(k)]
        if st.get("alt"):
            madde += [("alt %d.%d is_" % (s, n + 1), g.get("is_")) for n, g in enumerate(st.get("sira_grup") or []) if g.get("is_")]
        tum = ["".join(x[0] for x in (oku[p - 1] for p in sf)), "".join(x[1] for x in (oku[p - 1] for p in sf))]
        kay = _tam_kaynak(st, V, s)
        r["madde"], r["madde_eksik"], r["madde_fazla"] = len(madde), 0, 0
        goruldu = set()
        for yer, t in madde:
            m = _tam_norm(_tam_md(t))
            if m and not any(m in x for x in tum):
                r["madde_eksik"] += 1
                eksik.append(dict(adim=s, kod=st.get("kod"), yer=yer, eksik_karakter=len(m), metin=t[:80]))
            elif m and m not in goruldu:                                # P10.7b2b (B5): PDF'te kaynaktakinden çok basılan madde
                goruldu.add(m)
                n_pdf, n_kay = max(_tam_say(x, m) for x in tum), sum(_tam_say(x, m) for x in kay)
                if n_pdf > n_kay:
                    r["madde_fazla"] += 1
                    yineleme.append(dict(adim=s, kod=st.get("kod"), yer=yer, pdf=n_pdf, kaynak=n_kay, metin=t[:80]))
        adim.append(r)
    return dict(olculdu=True, adim=len(adim), is_karakter=sum(a["is_karakter"] for a in adim),
                is_eksik_karakter=sum(a["is_eksik"] for a in adim), madde=sum(a["madde"] for a in adim),
                madde_eksik=sum(a["madde_eksik"] for a in adim), madde_fazla=sum(a["madde_fazla"] for a in adim), eksik=eksik,
                yineleme=yineleme, yineleme_sayi=len(yineleme),
                sayfa_parca={str(a["adim"]): a["sayfa_parca"] for a in adim if len(a["sayfa"]) > 1}, gecti=not eksik and not yineleme)


def _tam_sil(t, metin):
    """Sayfa metninden (satır sonu / boşluk esnek) bir metni sil: bozma denemesi."""
    m = _tam_norm(_tam_md(metin))
    d = r"[\s­​‐-]*".join(re.escape(c) for c in m)
    return re.sub(d, "", t, count=1)


def pdf_tamlik_bozma(pdf, V, esleme, sentetik=False):
    """P10.7b2b: pdf_tamlik() bozma denemesi, üretim koşmadan (PDF bir kez okunur, bozma sayfa metninde). Doner [(ad, beklenen, tuttu)].
    Çağrı: rehber_uret modülü içe aktarılıp pdf_tamlik_bozma(pdf, rehber-veri.json, kontrol.json yazdir.sayfa_esleme)."""
    import fitz
    with fitz.open(pdf) as doc:
        ham = [p.get_text("text") for p in doc]
    temiz = pdf_tamlik(pdf, V, esleme, ham=ham)
    out = [("temiz PDF (yakalanmamalı)", False, not temiz["gecti"])]
    s = next((i for i, a in enumerate(V["adimlar"]) if len(esleme.get(i, [])) > 1 and
              (temiz["sayfa_parca"].get(str(i)) or [[0, 0], [0, 0]])[1][1] > 0), None)   # iş metni iki sayfaya bölünen adım (P10.7b2c'de K1)
    if s is None or sentetik:
        # P10.7b2d-A: K1 alt adımlara bölününce iş metni iki sayfaya bölünen adım kalmayabilir. Sentetik bölünme: iki sayfalı, kontrol
        # listeli adımlardan iş metni en uzun olanın ilk sayfadaki son iş metni satırı ikinci sayfanın başına taşınır; bu taban temiz
        # sayılmalı (pdf_tamlik geçer), B4b denemeleri onun üstünde. Taban geçmezse deneme sonucu "yakalanmadı" yazılır (sessiz değil).
        def son_satir(i):                                               # ilk sayfada iş metninin sonu olan satır (yoksa None)
            T_ = _tam_norm(_tam_md(V["adimlar"][i].get("is_")))
            sp = temiz["sayfa_parca"].get(str(i)) or []
            if not sp or sp[0][1] != len(T_):                           # iş metni ilk sayfada bitmiyor: aday değil
                return None
            sat_ = ham[esleme[i][0] - 1].split("\n")
            return next((n for n in range(len(sat_) - 1, -1, -1) if len(_tam_norm(sat_[n])) >= TAM_EN_AZ and
                         T_.endswith(_tam_norm(sat_[n])) and len(_tam_norm(sat_[n])) < len(T_)), None)
        aday = [i for i, a in enumerate(V["adimlar"]) if len(esleme.get(i, [])) > 1 and a.get("kontrol") and son_satir(i) is not None]
        s = max(aday, key=lambda i: len(_tam_norm(_tam_md(V["adimlar"][i]["is_"]))))
        q1, q2 = esleme[s][0], esleme[s][1]
        sat = ham[q1 - 1].split("\n")
        k0 = son_satir(s)
        ham = list(ham)
        tas = sat[k0]
        ham[q1 - 1] = "\n".join(sat[:k0] + sat[k0 + 1:])
        ham[q2 - 1] = tas + "\n" + ham[q2 - 1]
        temiz = pdf_tamlik(pdf, V, esleme, ham=ham)
        out.append(("sentetik bölünme tabanı temiz (%s s%d → s%d; yakalanmamalı)" % (V["adimlar"][s]["kod"], q1, q2), False,
                    not temiz["gecti"] or not (temiz["sayfa_parca"].get(str(s)) or [[0, 0], [0, 0]])[1][1]))
    st = V["adimlar"][s]
    p1, p2 = esleme[s][0], esleme[s][1]
    T = _tam_norm(_tam_md(st["is_"]))
    i1 = temiz["sayfa_parca"][str(s)][0][1]
    satir1 = [x for x in ham[p1 - 1].split("\n") if len(_tam_norm(x)) >= TAM_EN_AZ and _tam_norm(x) in T[:i1]]
    # P10.7b2d-A: önce basılan parçanın sonu olan satır (iş metnindeki bir yol adı kablo listesinde de geçebilir: "kablolar.md")
    sonek = [x for x in satir1 if T[:i1].endswith(_tam_norm(x))]
    son = (sonek or satir1)[-1]                                          # p1'de basılan is_'in son satırı
    satir2 = ham[p2 - 1].split("\n")
    k = next(n for n, x in enumerate(satir2) if len(_tam_norm(x)) >= 6 and _tam_norm(x) in T[i1:])

    def dene(ad, h2, beklenen=True):
        d = pdf_tamlik(pdf, V, esleme, ham=h2)
        out.append((ad, beklenen, not d["gecti"]))

    h = list(ham)
    h[p2 - 1] = "\n".join(satir2[:k] + [son] + satir2[k:])
    dene("B4b: devam sayfasında önceki sayfanın son satırı akış içinde yineleniyor (%s s%d)" % (st["kod"], p2), h)
    h = list(ham)
    h[p2 - 1] = son + "\n" + ham[p2 - 1]
    dene("devam sayfasının en üstünde önceki sayfanın son satırı (%s s%d)" % (st["kod"], p2), h)
    for alan in ("kontrol", "kablo", "not_"):
        a = next(i for i, x in enumerate(V["adimlar"]) if x.get(alan) and esleme.get(i))
        t = V["adimlar"][a][alan][0]
        h = list(ham)
        h[esleme[a][-1] - 1] += "\n" + _tam_md(t)
        dene("B5: %s maddesi iki kez basıldı (%s)" % (alan, V["adimlar"][a]["kod"]), h)
    h = list(ham)
    h[p1 - 1] += "\n" + _tam_md(st["kontrol"][-1])
    dene("B5: kontrol maddesi adımın başka sayfasında ikinci kez (%s s%d)" % (st["kod"], p1), h)
    for alan in ("kablo", "erisim", "baglanti_md"):
        a = next(i for i, x in enumerate(V["adimlar"]) if x.get(alan) and esleme.get(i) and
                 len(_tam_norm(_tam_md(x[alan][0] if alan == "kablo" else x[alan]))) >= TAM_EN_AZ)
        t = V["adimlar"][a][alan][0] if alan == "kablo" else V["adimlar"][a][alan]
        h = list(ham)
        for p in esleme[a]:
            h[p - 1] = _tam_sil(h[p - 1], t)
        dene("A2: %s metni PDF'te yok (%s)" % (alan, V["adimlar"][a]["kod"]), h if h != ham else None)
    return out


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
    # P10.7b2a-Y: basılı metin tamlığı (PDF'te her adımın iş metni, alt adım iş metni, not ve kontrol maddeleri tam mı)
    d["tamlik"] = pdf_tamlik(pdf, json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8")), esleme) \
        if yeni else dict(olculdu=False, neden="PDF yok", gecti=False)
    # kabul (F7c): her adım ≥ 1 sayfa (eşleme sıralı ve kesintisiz), PDF sayfası = HTML sayfası ≥ adım, taşan 0, en küçük yazı ≥ 8 pt;
    # P10.7b2a-Y: basılı metinde eksik karakter 0
    d["gecti"] = bool(yeni and sayfa == d["html_sayfa"] and sayfa >= n_adim and d["esleme_tutarli"] and not d["tasan"]
                      and not d["kucuk_yazi"] and kucuk_ok and d["tamlik"]["gecti"])
    print("yazdirilabilir: pdf %d sayfa (adim %d, devam %d), html %s, esleme %s, tasan %s, en kucuk yazi dom %s / pdf %s pt, %d kB" % (
        sayfa, n_adim, d["devam_sayfasi"], d["html_sayfa"], "tutarli" if d["esleme_tutarli"] else "TUTARSIZ", d["tasan"] or "-",
        d["en_kucuk_yazi_pt_dom"], d["en_kucuk_yazi_pt_pdf"], d["boyut_kb"]))
    tm = d["tamlik"]
    print("yazdir tamlik: %s" % ("%d adim, is_ %d karakter, eksik %d; madde %d, eksik %d; yineleme %d" % (
        tm["adim"], tm["is_karakter"], tm["is_eksik_karakter"], tm["madde"], tm["madde_eksik"], tm["yineleme_sayi"])
        if tm["olculdu"] else "OLCULMEDI (%s)" % tm["neden"]))
    for x in (tm.get("yineleme") or [])[:10]:
        print("  YINELENEN adim %s (%s) %s: %s" % (x["adim"], x["kod"], x["yer"], x["metin"][:70]))
    for x in (tm.get("eksik") or [])[:10]:
        print("  EKSIK adim %s (%s) %s: %d karakter basilmadi%s" % (x["adim"], x["kod"], x["yer"], x["eksik_karakter"],
              ", sayfa %s sonunda kesik: ...%s | %s..." % (x["son_sayfa"], x["kesilen_once"], x["kesilen_sonra"]) if "kesilen_once" in x
              else ": %s" % x["metin"]))
    return d, [("yazdır", gorunen_metin(dom, r'<div id="sayfalar">.*</body>'))]


def beklenen_alt(V, s, j):
    """F10d: app.js durum(p, s, j) kuralı. Alt adım j'de yeni görünenler (simdi: grubun satırları + gösterim parçaları), bağlanan
    masa birimi ya da tezgâh alt montajı (alt) ve yeni şemalar."""
    st = V["adimlar"][s]
    G = st["sira_grup"]
    g = G[j - 1]
    satir = {"p:%d" % i: r["ids"] for i, r in enumerate(st["parcalar"])}
    satir.update({"b:%d" % i: r.get("ids", []) for i, r in enumerate(st["baglantilar"])})
    pg = {}
    for n, x in enumerate(G):
        for k in x["satir"]:
            for i in satir[k]:
                pg[i] = n
        for i in x.get("ref", []):
            pg[i] = n
    simdi = {i for i, n in pg.items() if n == j - 1}
    alt = {i for i, n in pg.items() if g.get("bag") and G[n]["tezgah"] == g["bag"]}
    if j == 1 and not st["tezgah"]:
        alt |= {p["id"] for p in V["parcalar"] if p["b"] == s and p["a"] != s}
    return simdi, alt, set(g.get("sema", []))


def alt_kontrol(tb, V, adimlar):
    """F10d: alt adımlar (CDP, tek tarayıcı): ?adim=N.J&cekim=1 (1400 × 900) -> yeni görünenler beklenenle, konsol hatası, panel metni
    (denetim), kontrol görüntüsü <çıktı>/goruntu/adim-NN-JJ.png; ?adim=N.J&sahne=1 (1200 × 720, açık tema) -> yazdırma görüntüsü
    rehber/goruntu/adim-NN-JJ.png, piksel denetimi (cizim_orani, boşsa CIZIM_TEKRAR kez yeniden). Her parça kendi adımının tam bir alt
    adımında yeni görünmeli."""
    import base64
    AD = {p["id"]: "%s [%s]" % (p["ad"], p["modul"]) for p in V["parcalar"]}
    hedef = [(s, j) for s in adimlar for j in range(1, (V["adimlar"][s].get("alt") or 0) + 1)]
    if not hedef:
        return dict(alt_adim=0, sonuc=[], gecti=True), [], dict(bos=[], eksik=[])
    os.makedirs(GORUNTU, exist_ok=True)
    os.makedirs(YAZDIR_GORUNTU, exist_ok=True)
    sonuc, metin, say, say_sema = [], [], {}, {}
    bos, oran, tekrar = [], {}, {}
    c = Cdp(tb)

    def ac(u, w, h):
        c.cmd("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
        c.js("document.body && (document.body.dataset.hazir = '0')")   # önceki sayfanın hazır işareti sayılmasın
        c.cmd("Page.navigate", url=u)
        q = u.split("?", 1)[1] if "?" in u else ""
        t = time.time()
        while time.time() - t < 60 and c.js("(location.search.slice(1) === %s && document.body && document.body.dataset.hazir) || ''"
                                            % json.dumps(q)) != "1":
            time.sleep(0.25)
        time.sleep(0.3)

    def cek(png):
        ek = c.cmd("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        open(png, "wb").write(base64.b64decode(ek["data"]))
    try:
        for s, j in hedef:
            ad = "%d.%d" % (s, j)
            ac(url(None, "?adim=%s&cekim=1" % ad), 1400, 900)
            o = c.js("(function(){var k=document.getElementById('kontrol-veri'),p=document.querySelector('.panel');var t=[];"
                     "if(p){var w=document.createTreeWalker(p,NodeFilter.SHOW_TEXT),x;while((x=w.nextNode())){if(!x.parentElement.closest('code,script,style'))"
                     "t.push(x.nodeValue);}}return {kv:k?k.textContent:'',h:document.documentElement.dataset.hata||null,"
                     "hz:document.body.dataset.hazir||null,m:t.join(' ')};})()") or {}
            png = os.path.join(GORUNTU, "adim-%02d-%02d.png" % (s, j))
            cek(png)
            try:
                g = json.loads(o.get("kv") or "null")
            except ValueError:
                g = None
            b_simdi, b_alt, b_sema = beklenen_alt(V, s, j)
            d = dict(adim=s, alt_adim=j, kod=V["adimlar"][s]["kod"], hazir=o.get("hz") == "1", hata=o.get("h"),
                     goruntu=os.path.relpath(png, ROBOT).replace("\\", "/"), veri_okundu=g is not None)
            if g is not None:
                gs, ga = set(g["simdi"]), set(g["alt"])
                for i in gs:
                    say.setdefault(i, []).append(ad)
                for i in set(g.get("sema") or []):                        # P10.7b2d-A: şemanın "şimdi" olduğu alt adımlar
                    say_sema.setdefault(i, []).append(ad)
                fark = sorted(gs ^ b_simdi) + sorted(ga ^ b_alt)
                d.update(beklenen_simdi=len(b_simdi), gorunen_simdi=len(gs), beklenen_alt=len(b_alt), gorunen_alt=len(ga),
                         fark=[AD.get(i, i) for i in fark], sema_fark=sorted(set(g.get("sema") or []) ^ b_sema), kadraj=g.get("kadraj"),
                         eksik_mesh=g.get("eksik") or [], konum_dogru=(g.get("adim") == s and g.get("alt_adim") == j))
                d["gecti"] = bool(d["hazir"] and not d["hata"] and not fark and not d["sema_fark"] and not d["eksik_mesh"] and d["konum_dogru"])
            else:
                d["gecti"] = False
            sonuc.append(d)
            metin.append(("tarayıcı alt adım %s" % ad, o.get("m") or ""))
            print("  alt adim %-6s %-4s hazir=%s hata=%s yeni %s/%s alt %s/%s kadraj %s %s" % (
                ad, d["kod"], d["hazir"], d["hata"] or "-", d.get("gorunen_simdi"), d.get("beklenen_simdi"), d.get("gorunen_alt"),
                d.get("beklenen_alt"), d.get("kadraj"), "GECTI" if d["gecti"] else "KALDI"))
            # yazdırma görüntüsü (yalnız 3B, açık tema)
            ypng = os.path.join(YAZDIR_GORUNTU, "adim-%02d-%02d.png" % (s, j))
            for k in range(CIZIM_TEKRAR + 1):
                ac(url(None, "?adim=%s&cekim=1&sahne=1&tema=light" % ad), 1200, 720)
                cek(ypng)
                r = cizim_orani(ypng)
                oran[ad] = None if r is None else round(r, 4)
                if r is None or r >= CIZIM_ESIK:
                    break
                tekrar[ad] = k + 1
            if oran.get(ad) is None or oran[ad] < CIZIM_ESIK:
                bos.append(ad)
    finally:
        c.kapat()
    # her parça (alt adımlı adımlarda) tam bir alt adımda yeni
    tum = sorted(adimlar) == list(range(len(V["adimlar"])))
    tek = tek_s = None                                              # P10.7b2d-A d1 (F10l-kontrol D3): kısmi koşuda (--adimlar) ikisi de yok
    if tum:
        bek = [p["id"] for p in V["parcalar"] if V["adimlar"][p["a"]].get("alt")]
        coklu = {AD[i]: v for i, v in say.items() if len(v) != 1}
        hic = [AD[i] for i in bek if i not in say]
        tek = dict(gecti=not coklu and not hic, parca=len(bek), birden_cok_alt_adimda=coklu, hic_gorunmeyen=hic)
        # P10.7b2d-A: şema karşılığı. Alt adımlı adımın her şeması tam bir alt adımda "şimdi" (vurgulu); hiç vurgulanmayan 0. Parça
        # ölçütü yukarıda değişmeden kalır.
        SA = {i: "%s [adım %s]" % (x.get("ad", "")[:60], x.get("a")) for i, x in enumerate(V.get("semalar") or [])}
        bek_s = [i for i, x in enumerate(V.get("semalar") or []) if V["adimlar"][x["a"]].get("alt")]
        coklu_s = {SA.get(i, i): v for i, v in say_sema.items() if len(v) != 1}
        hic_s = [SA[i] for i in bek_s if i not in say_sema]
        tek_s = dict(gecti=not coklu_s and not hic_s, sema=len(bek_s), birden_cok_alt_adimda=coklu_s, hic_vurgulanmayan=hic_s)
    gecerli = [v for v in oran.values() if v is not None]
    yg = dict(alt_adim=len(hedef), eksik=[], bos=bos, cizim_esik=CIZIM_ESIK, yeniden_cekim=tekrar, en_dusuk_cizim_orani=min(gecerli) if gecerli else None,
              cizim_orani=oran, piksel_denetimi=bool(gecerli) and len(gecerli) == len(oran))
    print("alt adim: %d, gecti %d, her parca tek alt adimda: %s, her sema tek alt adimda: %s%s; yazdir goruntusu bos %s, en dusuk "
          "cizim orani %s" % (len(sonuc), sum(1 for d in sonuc if d["gecti"]), tek["gecti"] if tek else "-", tek_s["gecti"] if tek_s else "-",
                              " (%d sema, birden cok %d, hic %d)" % (tek_s["sema"], len(tek_s["birden_cok_alt_adimda"]),
                                                                    len(tek_s["hic_vurgulanmayan"])) if tek_s else "",
                              bos or "-", yg["en_dusuk_cizim_orani"]))
    for k, v in sorted((tek_s or {}).get("birden_cok_alt_adimda", {}).items())[:10]:
        print("  SEMA birden cok alt adimda: %s %s" % (k, v))
    for k in ((tek_s or {}).get("hic_vurgulanmayan") or [])[:10]:
        print("  SEMA hic vurgulanmadi: %s" % k)
    return dict(alt_adim=len(hedef), gecen=sum(1 for d in sonuc if d["gecti"]), konsol_hatasi=sum(1 for d in sonuc if d["hata"]),
                her_parca_tek_alt_adimda=tek, her_sema_tek_alt_adimda=tek_s, sonuc=sonuc,
                gecti=all(d["gecti"] for d in sonuc) and (tek is None or tek["gecti"]) and (tek_s is None or tek_s["gecti"])), metin, yg


def on_sinama():
    """P10.7b1 düzeltme turu 2 (F10h-kontrol-3 §3.2): üretime başlamadan önce kaynak denetimi (rehber_denetim.kaynak_denetle: ASCII,
    elektrik, zorunlu, yasak, çıplak sayı, yer tutucu, bağlam, kayıt → rehber tamlığı) ve onaylı kritik metin kaydı (rehber_kritik).
    Biri tutmazsa ya da kayıt okunamazsa üretim durur (çıkış 1); FreeCAD ve tarayıcı hiç açılmaz. Standart kütüphane."""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    try:
        import rehber_denetim as RD
        d = RD.kaynak_denetle()
    except Exception as e:                                              # noqa: BLE001  (rehber_kritik.KayitHatasi dahil)
        print("URETIM DURDU: on sinama kosamadi (%s: %s)" % (type(e).__name__, e))
        sys.exit(1)
    if not d["gecti"]:
        n = dict(ascii=len(d["ascii_kalinti"]), elektrik=len(d["elektrik"]), zorunlu=len(d["zorunlu_eksik"]), yasak=len(d["yasak"]),
                 ciplak=len(d["ciplak"]), yer_tutucu=len(d["cozum_hata"]) + len(d["bozuk"]), baglam=len(d["baglam"]),
                 onay_farki=len(d["kritik"]), tamlik=len(d["tamlik"]["hata"]), cad_metin="yok" if d["cad_metin"] is None else "var")
        print("URETIM DURDU: kaynak denetimi / onay kaydi tutmuyor: %s" % ", ".join("%s %s" % kv for kv in n.items()))
        for x in d["kritik"][:10]:
            print("  KRITIK %s %s %s\n      eski: %s\n      yeni: %s" % (x["tur"], x["bolum"], x["yer"], x["eski"] or "-", x["yeni"] or "-"))
        print("Once `rehber_denetim.py --kaynak` temiz olmali; metin bilerek degistiyse bagimsiz kontrolden sonra "
              "`rehber_denetim.py --kritik-onay-yenile`.")
        sys.exit(1)
    print("on sinama: kaynak denetimi gecti, onay kaydi tutuyor (%s)" % ", ".join("%s %d" % kv for kv in sorted(d["kritik_sayi"].items())))


if __name__ == "__main__":
    try:                                                                # F10d: alt adım adlarında "→" var; cp1254 konsolda özet çökmesin
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--veri-yok", action="store_true")
    ap.add_argument("--gorsel-yok", action="store_true")
    ap.add_argument("--ek-yok", action="store_true", help="yazdır görüntüsü, telefon, PDF ve metin denetimini atla")
    ap.add_argument("--adimlar", default="")
    ap.add_argument("--cikti", default="", help="kontrol.json, kontrol görüntüleri ve PDF için klasör (varsayılan planlama/rehber)")
    g = ap.parse_args()
    on_sinama()                                                         # düzeltme turu 2: fark varsa üretim burada durur
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
    if not g.cikti:                                                     # F10e: görünüm verisi (gerçek renk, bağlandığı yer, işaret
        import rehber_gorunum                                           # noktası, rehber_metin alanları); FreeCAD'siz, iki yolda da
        rehber_gorunum.isle()
        import rehber_kol_kablo                                         # F10f: kol içi kablo yolu şemaları (KOL_KABLO + kablo_yolu.py)
        rehber_kol_kablo.isle(yazma=True)
    if not g.gorsel_yok:
        n = len(json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))["adimlar"])
        ad = [int(x) for x in g.adimlar.split(",") if x.strip()] or list(range(n))
        V, tb, sonuc, ozet, metin, tek = kontrol(ad)
        ek = {}
        try:                                                            # F10d: alt adımlar (kontrol + yazdırma görüntüsü)
            ek["alt_adim"], m_alt, yg_alt = alt_kontrol(tb, V, ad)
        except Exception as e:
            ek["alt_adim"], m_alt, yg_alt = dict(durum="hata", neden="%s: %s" % (type(e).__name__, e), gecti=False), [], dict(bos=[], eksik=[])
            print("alt adim kontrolu: HATA", ek["alt_adim"]["neden"])
        metin = metin + m_alt
        ek["alt_adim"]["yazdir_goruntu"] = yg_alt
        if not g.ek_yok:
            import rehber_denetim as RD
            ek["yazdir_goruntu"] = yg = sahne_goruntu(tb, ad)
            # F10d düzeltme 1 (kontrol B-9): yazdırma karelerinin piksel denetimi alt adım karelerini de kapsasın (ana 50 + alt 45)
            yg["ana_adim"], yg["alt_adim"] = yg["adim"], yg_alt.get("alt_adim", 0)
            yg["kare"] = yg["ana_adim"] + yg["alt_adim"]
            yg["bos"] = list(yg["bos"]) + list(yg_alt.get("bos") or [])
            yg["cizim_orani"] = dict(yg["cizim_orani"], **{str(k): v for k, v in (yg_alt.get("cizim_orani") or {}).items()})
            yg["denetlenen"] = sum(1 for v in yg["cizim_orani"].values() if v is not None)
            yg["piksel_denetimi"] = yg["denetlenen"] == yg["kare"]
            _g = [v for v in yg["cizim_orani"].values() if v is not None]
            yg["en_dusuk_cizim_orani"] = min(_g) if _g else None
            print("yazdir goruntusu (ana + alt adim): %d kare, piksel denetimi %d / %d, bos %s, en dusuk cizim orani %s" % (
                yg["kare"], yg["denetlenen"], yg["kare"], yg["bos"] or "-", yg["en_dusuk_cizim_orani"]))
            ek["telefon"], m2 = telefon(tb)
            ek["yazdir"], m3 = yazdir(tb, n)
            ek["denetim"] = RD.denetle(V, metin + m2 + m3)
            RD.ozet_yaz(ek["denetim"])
            import rehber_sira as RS                                    # F10c: 8) sıra (alet + el) ve perdelenme
            try:
                ek["sira"], ek["perdelenme"] = RS.denetle(V)
            except Exception as e:                                      # denetim çökerse üretim sürer, sıra denetimi kalır
                ek["sira"] = dict(durum="hata", neden="%s: %s" % (type(e).__name__, e), gecti=False)
                ek["perdelenme"] = dict(durum="hata", neden=ek["sira"]["neden"], gecti=True)
            RS.ozet_yaz(ek["sira"], ek["perdelenme"])
            import rehber_kol_kablo as RK                               # F10f: kol kablo yolu ↔ kaynak / adım / katı / el / metin
            try:
                ek["kol_kablo"] = RK.denetle(V)
            except Exception as e:
                ek["kol_kablo"] = dict(durum="hata", neden="%s: %s" % (type(e).__name__, e), gecti=False)
                print("kol kablo denetimi: HATA", ek["kol_kablo"]["neden"])
            import rehber_kablo as RKB                                  # P10.7b1: çizilen kablo ↔ planlama/adim3/kablolar.json
            try:
                _tb = RKB.Tablo()
                _h = RKB.kaynak_denetle(_tb)
                _hv, _es = RKB.veri_denetle(V, _tb)
                _hg, _bg = RKB.geometri_denetle(_tb)                    # düzeltme turu 1 (Ü3): CAD yolu ↔ kablo uçları
                _h = _h + _hg
                # P10.7b2c ikinci yarı (ajan B): şema uçları, bağlantı tablosu, şema boyu tazeliği; sayım üç sınıf (cizilen = yol çizimi)
                _h = _h + RKB.sema_geometri_denetle(_tb)[0] + RKB.baglanti_tablosu_denetle(_tb) + RKB.sema_boy_denetle(_tb)
                # P10.7b2c düzeltme turu 1 (F10k-kontrol D1, D3, kaçan 4 / 5): kart boy etiketi, gösterim şeması notu, yer eki
                _h = _h + RKB.sema_boy_etiketi_denetle() + RKB.sema_not_denetle(_tb) + RKB.uc_yer_eki_denetle(_tb)
                _ct = RKB.cizim_tablosu(_tb)
                ek["kablo_esleme"] = dict(hata=_h + _hv, eslesmeyen=_es, tablo=_ct["toplam"], cizilen=_ct["cizilen"],
                                          cizilmeyen=_ct["cizilmeyen"], yol_cizimi=_ct["yol_cizimi"], yol_kaynak=_ct["yol_kaynak"],
                                          baglanti_tablosu=_ct["baglanti_tablosu"], hicbiri=_ct["hicbiri"],
                                          gecti=not (_h or _hv or _es))
            except Exception as e:
                ek["kablo_esleme"] = dict(durum="hata", neden="%s: %s" % (type(e).__name__, e), gecti=False)
            print("kablo esleme: %s" % ("GECTI" if ek["kablo_esleme"]["gecti"] else ek["kablo_esleme"]))
        os.makedirs(CIKTI, exist_ok=True)
        json.dump(dict(tarih=time.strftime("%Y-%m-%d %H:%M"), tarayici=os.path.basename(tb), ozet=ozet, sonuc=sonuc, **ek),
                  open(os.path.join(CIKTI, "kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        kotu = [s for s in sonuc if not s["gecti"]]
        ek_kotu = [k for k in ("telefon", "yazdir", "denetim", "sira", "perdelenme", "alt_adim", "kol_kablo", "kablo_esleme") if k in ek and not ek[k]["gecti"]]
        if ek.get("yazdir_goruntu", {}).get("eksik") or ek.get("yazdir_goruntu", {}).get("bos") or \
                ek.get("yazdir_goruntu", {}).get("piksel_denetimi") is False:
            ek_kotu.append("yazdir_goruntu")
        if yg_alt.get("bos"):
            ek_kotu.append("alt_adim_yazdir_goruntu")
        print("tarayici kontrolu: %d adim, %d gecti, %d sorunlu, konsol hatasi %d; her parca tek adimda: %s; ek kontrol sorunlu: %s" % (
            len(sonuc), ozet["gecen"], len(kotu), ozet["konsol_hatasi"], tek["gecti"] if tek else "-", ek_kotu or "-"))
        sys.exit(0 if not kotu and (tek is None or tek["gecti"]) and not ek_kotu else 2)
