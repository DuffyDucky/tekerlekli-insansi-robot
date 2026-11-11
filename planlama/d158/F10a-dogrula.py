# F10a (P10.1) doğrulama: rehber arayüzü (seçim vurgusu, ağsız açılış, kadraj, küçük görünüm) başsız tarayıcıda ölçülür.
#   py -3 -X utf8 planlama/d158/F10a-dogrula.py              # tümü -> planlama/d158/F10a-dogrula.json (+ F10a-goruntu-*.png)
#   py -3 -X utf8 planlama/d158/F10a-dogrula.py --goruntu-yok   # (= --kanit-yok) kanıt kareleri yazılmaz; --json <yol> sonuç başka yere
# F10d: alt adımlar. → tuşu sınaması gezinme sırasındaki bir sonraki konumu (RehberTest.konum) bekler; ölçülenler değişmedi.
# Yöntem: Chrome DevTools protokolü (rehber_uret.py'deki gibi; websockets paketi). Sayfa file:// ile açılır.
#   1) kadraj: 50 adımın her birinde (?cekim=1, 1400 x 900, açık tema) yeni parçaların bütün köşe noktaları (vertex) kamerayla
#      izdüşürülür; ekran kutusu (kareye kırpılmış) / kare alanı = oran; bir noktası karenin dışında ya da kameranın arkasında kalan
#      yeni parça = taşan. "Önce" F10a öncesi (ONCE, varsayılan 749627b~1; F10c düzeltme 1: eskiden HEAD, F10a commit'inden beri
#      HEAD'de importmap yok) rehber/app.js + index.html + stil.css (geçici klasöre kopya; three.js aynı 0.160 yerel
#      paketten, tek ek satır kamerayı okumak için), "sonra" çalışma ağacındaki rehber/.
#   2) küçük görünüm: 50 adımda 1400 x 900 ve 360 px'te (mobil öykünme) çizildi mi (küçük görünüm alanında arka plandan farklı ve
#      vurgu renginde piksel), 360 px'te yatay taşma ve panelle kesişme.
#   3) seçim: 6 adımda gerçek fare tıklaması (Input.dispatchMouseEvent). Vurgu, görünür mesh'lerin malzeme renginden (ana #7cfc00,
#      kopya #cdf7a6) kimlik kümesi olarak okunur (düzeltme 1, B-3): bir parçaya -> ana = tıklanan, kopyalar = satırın görünen öbür
#      ids'i; bir panel satırına -> vurgulu küme = satırın görünen ids kümesi; boş alana -> 0; yeniden seçip → tuşu -> 0. Ek: Esc,
#      önceki adımdan parça, kablo şeması, patlat / tak kısayolları, tak bitince sıkı kadraj (B-4).
#   7) yazdırma kareleri (düzeltme 1, B-1): rehber/goruntu/adim-NN.png 50 karede ve PDF'teki 3B görüntülerde model çizili mi
#      (zeminden farklı piksel oranı >= 0,01, lejant ve küçük görünüm köşesi hariç).
#   4) ağsız: Network.emulateNetworkConditions(offline) + setBlockedURLs(http, https); dış alan adına istek, konsol hatası, model.
#   5) rehber/ içinde CDN bağlantısı (html, js, css; vendor dahil yalnız CDN alan adları).
#   6) görüntüler: adım 12, 17, 31, 33, 44 açık / koyu, önce / sonra; 31 ve 33 saydam + patlat; seçim vurgulu iki kare.
import os, sys, json, time, re, subprocess, tempfile, shutil, base64, argparse, statistics, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
REHBER = os.path.join(ROBOT, "rehber")
CIKTI = os.path.join(HERE, "F10a-dogrula.json")
TARAYICI = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
V = json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))
NA = len(V["adimlar"])
PARV = {p["id"]: p for p in V["parcalar"]}
ONCE = os.environ.get("F10A_ONCE", "749627b~1")                  # "önce" sayfasının git sürümü (F10a öncesi)


class Cdp:
    def __init__(self, tb, ad):
        import websockets.sync.client as WS
        prof = os.path.join(tempfile.gettempdir(), "lale-f10a-" + ad)
        os.makedirs(prof, exist_ok=True)
        pf = os.path.join(prof, "DevToolsActivePort")
        t0 = time.time() - 1
        self.p = subprocess.Popen([tb, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--hide-scrollbars",
                                   "--remote-debugging-port=0", "--no-first-run", "--disable-extensions", "--user-data-dir=" + prof,
                                   "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port = None
        for _ in range(150):
            if os.path.exists(pf) and os.path.getmtime(pf) >= t0:
                s = open(pf).read().split()
                if s:
                    port = int(s[0]); break
            time.sleep(0.2)
        if port is None:
            self.kapat(); raise RuntimeError("DevTools portu yok")
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
        self.olay = []

    def cmd(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps(dict(id=self.n, method=method, params=params)))
        while True:
            m = json.loads(self.ws.recv(timeout=120))
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError("%s: %s" % (method, m["error"]))
                return m.get("result", {})
            if "method" in m:
                self.olay.append(m)

    def js(self, ifade):
        r = self.cmd("Runtime.evaluate", expression=ifade, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            raise RuntimeError("js: %s" % json.dumps(r["exceptionDetails"])[:400])
        return r.get("result", {}).get("value")

    def bekle(self, ifade, sure=90):
        t = time.time()
        while time.time() - t < sure:
            try:
                if self.js(ifade):
                    return True
            except RuntimeError:
                pass
            time.sleep(0.25)
        return False

    def git(self, u, cekim=True):
        self.cmd("Page.navigate", url=u)
        time.sleep(0.3)
        if cekim:
            ok = self.bekle("document.body && document.body.dataset.hazir === '1' && !!window.RehberTest")
        else:
            ok = self.bekle("!!(window.RehberTest && RehberTest.hazir() && !RehberTest.anim())")
        time.sleep(0.15)
        return ok

    def tikla(self, x, y):
        for t in ("mouseMoved", "mousePressed", "mouseReleased"):
            self.cmd("Input.dispatchMouseEvent", type=t, x=x, y=y, button="left" if t != "mouseMoved" else "none",
                     buttons=1 if t == "mousePressed" else 0, clickCount=1)
        time.sleep(0.15)

    def tus(self, key, code, vk, shift=False):
        mod = 8 if shift else 0
        self.cmd("Input.dispatchKeyEvent", type="keyDown", key=key, code=code, windowsVirtualKeyCode=vk, modifiers=mod,
                 text=key if len(key) == 1 else "")
        self.cmd("Input.dispatchKeyEvent", type="keyUp", key=key, code=code, windowsVirtualKeyCode=vk, modifiers=mod)
        time.sleep(0.15)

    def boyut(self, w, h, mobil=False):
        self.cmd("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=mobil)

    def goruntu(self, yol):
        d = self.cmd("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        open(yol, "wb").write(base64.b64decode(d["data"]))

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


def tarayici():
    for t in TARAYICI:
        if os.path.exists(t):
            return t
    sys.exit("Chrome / Edge bulunamadi")


def url(kok, q):
    return "file:///" + urllib.parse.quote(os.path.join(kok, "index.html").replace("\\", "/"), safe="/:") + q


def head_kopya():
    """F10a öncesi (ONCE) rehber sayfası (önce): geçici klasöre; veri ve three.js paketi çalışma ağacından (veri değişmedi; three aynı 0.160)."""
    tmp = tempfile.mkdtemp(prefix="lale-f10a-head-")
    kok = os.path.join(tmp, "rehber")
    os.makedirs(os.path.join(kok, "veri")); os.makedirs(os.path.join(kok, "vendor"))
    for f in ("index.html", "app.js", "stil.css"):
        b = subprocess.run(["git", "show", ONCE + ":rehber/" + f], cwd=ROBOT, capture_output=True).stdout
        open(os.path.join(kok, f), "wb").write(b)
    for f in ("rehber-veri.js", "robot-glb.js"):
        shutil.copy2(os.path.join(REHBER, "veri", f), os.path.join(kok, "veri", f))
    shutil.copy2(os.path.join(REHBER, "vendor", "three-0.160.0-paket.min.js"), os.path.join(kok, "vendor"))
    h = open(os.path.join(kok, "index.html"), encoding="utf-8").read()
    h2 = re.sub(r'<script type="importmap">.*?</script>\s*<script type="module">.*?</script>',
                '<script src="vendor/three-0.160.0-paket.min.js"></script><script>window.RehberBaslat(window.LALE_UC);</script>', h, flags=re.S)
    a = open(os.path.join(kok, "app.js"), encoding="utf-8").read()
    a2 = a.replace("sonKutu = k;", "sonKutu = k; window.RehberTest = { THREE, kamera, tuval, PAR, SEMA_OBJ };", 1)
    assert h2 != h and a2 != a, "%s kopyası yamanamadı" % ONCE
    open(os.path.join(kok, "index.html"), "w", encoding="utf-8").write(h2)
    open(os.path.join(kok, "app.js"), "w", encoding="utf-8").write(a2)
    return tmp, kok


OLC_JS = r"""(function(){
 const T=window.RehberTest, THREE=T.THREE, kv=JSON.parse(document.getElementById('kontrol-veri').textContent||'{}');
 const obj=[];
 if (kv.adim===0) { for (const id in T.PAR){const o=T.PAR[id].obj; if(o&&o.visible) obj.push(o);} T.SEMA_OBJ.forEach(o=>{if(o&&o.visible) obj.push(o);}); }
 else { (kv.simdi||[]).concat(kv.alt||[]).forEach(id=>{const o=T.PAR[id]&&T.PAR[id].obj; if(o) obj.push(o);}); (kv.sema||[]).forEach(i=>{const o=T.SEMA_OBJ[i]; if(o) obj.push(o);}); }
 const k=T.kamera; k.updateMatrixWorld(true); const v=new THREE.Vector3(), w=new THREE.Vector3();
 const c=T.tuval.getBoundingClientRect();
 const ortuR=[]; ['.sahne-arac','#mini','#lejant'].forEach(s=>{const e=document.querySelector(s); if(e&&e.offsetParent&&!e.hidden){const r=e.getBoundingClientRect(); if(r.width>0) ortuR.push(r);}});
 let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9,tasan=0,ortulen=0,nokta=0;
 for (const o of obj){ o.updateMatrixWorld(true); const pos=o.geometry.attributes.position; let dis=false, ort=false;
   for (let i=0;i<pos.count;i++){ v.fromBufferAttribute(pos,i).applyMatrix4(o.matrixWorld); w.copy(v).applyMatrix4(k.matrixWorldInverse);
     nokta++;
     if (w.z>-k.near){dis=true; continue;}
     v.project(k);
     if (v.x<-1||v.x>1||v.y<-1||v.y>1) dis=true;
     if (v.x<x0)x0=v.x; if(v.x>x1)x1=v.x; if(v.y<y0)y0=v.y; if(v.y>y1)y1=v.y;
     if (!ort && ortuR.length){ const px=c.left+(v.x+1)/2*c.width, py=c.top+(1-v.y)/2*c.height;
       for (const r of ortuR) if (px>=r.left&&px<=r.right&&py>=r.top&&py<=r.bottom){ort=true;break;} } }
   if(dis) tasan++; if(ort) ortulen++; }
 const a=Math.max(0,Math.min(1,x1)-Math.max(-1,x0))*Math.max(0,Math.min(1,y1)-Math.max(-1,y0))/4;
 return {n:obj.length, nokta:nokta, oran:Math.round(a*10000)/10000, tasan:tasan, ortulen:ortulen,
   kutu:[x0,x1,y0,y1].map(x=>Math.round(x*1000)/1000), kare:[Math.round(c.width),Math.round(c.height)], hata:document.documentElement.dataset.hata||null};
})()"""


def kadraj_olc(c, kok, ek=""):
    out = []
    for a in range(NA):
        ok = c.git(url(kok, "?adim=%d&cekim=1&tema=light%s" % (a, ek)))
        d = c.js(OLC_JS) if ok else None
        d = d or {}
        d["adim"] = a; d["kod"] = V["adimlar"][a]["kod"]; d["hazir"] = ok
        out.append(d)
    return out


def mini_olc(c, kok, mobil):
    out = []
    for a in range(NA):
        ok = c.git(url(kok, "?adim=%d&cekim=1&tema=light" % a))
        m = c.js("RehberTest.miniOlc()") if ok else {}
        lay = c.js("""(function(){const d=document.documentElement,m=document.getElementById('mini'),s=document.getElementById('sahne'),
          p=document.getElementById('panel');const r=m.getBoundingClientRect(),q=s.getBoundingClientRect(),t=p.getBoundingClientRect();
          const kes=Math.max(0,Math.min(r.right,t.right)-Math.max(r.left,t.left))*Math.max(0,Math.min(r.bottom,t.bottom)-Math.max(r.top,t.top));
          return {tasma:Math.max(d.scrollWidth,document.body.scrollWidth)-d.clientWidth, genislik:innerWidth,
            sahne_icinde: r.left>=q.left-0.5&&r.right<=q.right+0.5&&r.top>=q.top-0.5&&r.bottom<=q.bottom+0.5, panel_kesisim_px2:Math.round(kes),
            mini:[Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)], hata:d.dataset.hata||null};})()""") if ok else {}
        d = dict(adim=a, hazir=ok, **(m or {}), **(lay or {}))
        d["cizildi"] = bool(ok and m and m.get("acik") and m.get("dolu", 0) > 200 and m.get("vurgu", 0) > 0)
        if mobil:
            d["gecti"] = d["cizildi"] and d.get("tasma") == 0 and d.get("sahne_icinde") and d.get("panel_kesisim_px2") == 0 and not d.get("hata")
        else:
            d["gecti"] = d["cizildi"] and not d.get("hata")
        d.pop("kutu", None)
        out.append(d)
    return out


# F10a düzeltme 1 (B-3): vurgu sayfanın VURGU nesnelerinden değil, sahnedeki görünür mesh'lerin gerçek malzeme renginden okunur
# (ana #7cfc00, kopya #cdf7a6) ve kimlik kümesi olarak karşılaştırılır.
VURGU_JS = r"""(function(){const T=RehberTest; const ana=[], kopya=[];
 const bak=(o,ad)=>{ if(!o||!o.visible||!o.material||!o.material.color) return; const h=o.material.color.getHexString();
   if(h==='7cfc00') ana.push(ad); else if(h==='cdf7a6') kopya.push(ad); };
 for (const id in T.PAR) bak(T.PAR[id].obj, id); T.SEMA_OBJ.forEach((o,i)=>bak(o, 'sema'+i));
 return {ana:ana.sort(), kopya:kopya.sort(), ids:ana.concat(kopya).sort(), sayi:ana.length+kopya.length};})()"""


def vurgu(c):
    return c.js(VURGU_JS)


def gorunen(c, ids):
    """Satırın sahnede görünen kimlikleri (sayfa gizli kopyayı vurgulamaz; beklenen küme bu)."""
    return sorted(c.js("(function(ids){const T=RehberTest; return ids.filter(id=>T.PAR[id]&&T.PAR[id].obj&&T.PAR[id].obj.visible);})(%s)" % json.dumps(ids)) or [])


def satirlar(st):
    r = [("p", i, x["ids"], x["ad"]) for i, x in enumerate(st["parcalar"])] + [("b", i, x["ids"], x["kod"]) for i, x in enumerate(st["baglantilar"])]
    return sorted(r, key=lambda x: -len(x[2]))


def secim_sina(c, kok, a):
    st = V["adimlar"][a]
    d = dict(adim=a, kod=st["kod"], tur="tezgah" if st["tezgah"] else ("kablolama" if st["kablolama"] else "robot"))
    c.git(url(kok, "?adim=%d&tema=light&mini=1" % a), cekim=False)
    # a) parçaya tıkla
    hedef = None
    for tur, i, ids, ad in satirlar(st):
        for pid in ids:
            n = c.js("JSON.stringify(RehberTest.tikNoktasi(%s))" % json.dumps(pid))
            if n and n != "null":
                hedef = (pid, json.loads(n), tur, i, ids, ad); break
        if hedef:
            break
    if not hedef:                                                   # satırı olmayan parçalar (K1 kabloları)
        for p in V["parcalar"]:
            if p["a"] == a:
                n = c.js("JSON.stringify(RehberTest.tikNoktasi(%s))" % json.dumps(p["id"]))
                if n and n != "null":
                    hedef = (p["id"], json.loads(n), None, None, [p["id"]], p["ad"]); break
    if hedef:
        pid, nk, tur, i, ids, ad = hedef
        bek = gorunen(c, ids)
        g0 = vurgu(c)
        c.tikla(nk["x"], nk["y"])
        g = vurgu(c)
        et = c.js("document.getElementById('etiket').hidden ? '' : document.getElementById('etiket').textContent")
        kopya_bek = [x for x in bek if x != pid]
        d["parca"] = dict(id=pid, ad=ad, satir=None if tur is None else "%s:%d" % (tur, i), satir_ids=len(ids), beklenen=len(bek),
                          gizli_kopya=len(ids) - len(bek), vurgulu=g["sayi"], ana=g["ana"], kopya_sayi=len(g["kopya"]),
                          once_vurgulu=g0["sayi"], ana_tiklanan=g["ana"] == [pid], kopya_kume_esit=g["kopya"] == kopya_bek,
                          fazla=sorted(set(g["ids"]) - set(bek)), eksik=sorted(set(bek) - set(g["ids"])),
                          etikette_ad=PARV[pid]["ad"] in (et or ""))
        d["parca"]["gecti"] = (g0["sayi"] == 0 and g["ana"] == [pid] and g["kopya"] == kopya_bek and g["ids"] == bek
                               and PARV[pid]["ad"] in (et or ""))
    else:
        d["parca"] = dict(gecti=False, neden="tıklanabilir nokta bulunamadı")
    # b) panel satırına tıkla (en çok kopyalı satır; satır yoksa kablo kancası satırı)
    sat = satirlar(st)
    if sat:
        tur, i, ids, ad = sat[0]
        sec = "#panel [data-satir='%s:%d']" % (tur, i); bek = gorunen(c, ids); sids = len(ids)
    else:
        kab = [p for p in V["parcalar"] if p.get("renk") and p["a"] == a]
        sec = "#kablo [data-kid='%s']" % kab[0]["id"] if kab else None; ad = kab[0]["ad"] if kab else None
        bek = gorunen(c, [kab[0]["id"]]) if kab else []; sids = 1
    if sec:
        r = c.js("(function(){const e=document.querySelector(%s); if(!e) return null; e.scrollIntoView({block:'center'}); const r=e.getBoundingClientRect();"
                 " return {x:r.left+Math.min(40,r.width/2), y:r.top+r.height/2};})()" % json.dumps(sec))
        time.sleep(0.2)
        r = c.js("(function(){const e=document.querySelector(%s); const r=e.getBoundingClientRect(); return {x:r.left+Math.min(40,r.width/2), y:r.top+r.height/2};})()" % json.dumps(sec))
        c.tikla(r["x"], r["y"])
        g = vurgu(c)
        isaret = c.js("!!document.querySelector(%s + '.secili')" % json.dumps(sec))
        # panel satırı: satırın görünen bütün kopyaları birlikte vurgulu (kablo satırında tek parça ana renkte)
        d["panel"] = dict(secici=sec, ad=ad, satir_ids=sids, beklenen=len(bek), vurgulu=g["sayi"], satir_isaretli=isaret,
                          fazla=sorted(set(g["ids"]) - set(bek)), eksik=sorted(set(bek) - set(g["ids"])),
                          gecti=bool(bek) and g["ids"] == bek and isaret)
    else:
        d["panel"] = dict(gecti=False, neden="satır yok")
    # c) boş alana tıkla
    b = c.js("RehberTest.bosNokta()")
    if b:
        c.tikla(b["x"], b["y"])
        g = vurgu(c)
        d["bos"] = dict(vurgulu=g["sayi"], etiket_gizli=c.js("document.getElementById('etiket').hidden"), gecti=g["sayi"] == 0)
    else:
        d["bos"] = dict(gecti=False, neden="boş nokta yok")
    # d) yeniden seç, → ile adım değiştir
    if hedef:
        nk = c.js("RehberTest.tikNoktasi(%s)" % json.dumps(hedef[0]))
        if nk:
            c.tikla(nk["x"], nk["y"])
    once = vurgu(c)["sayi"]
    c.tus("ArrowRight", "ArrowRight", 39)
    c.bekle("!RehberTest.anim()", 10)
    g = vurgu(c)
    # F10d: → gezinme sırasında bir sonraki konuma gider: alt adımlı adımda (a, 0) -> (a, 1), öbürlerinde (a + 1, 0). Ölçülen aynı:
    # → sonrası konum değişti ve vurgu temizlendi
    bek = [a, 1] if V["adimlar"][a].get("alt") else [a + 1, 0]
    kon = c.js("RehberTest.konum ? RehberTest.konum() : [RehberTest.su(), 0]")
    d["adim_degisti"] = dict(once=once, sonra=g["sayi"], yeni_adim=c.js("RehberTest.su()"), yeni_konum=kon, beklenen_konum=bek,
                             gecti=once > 0 and g["sayi"] == 0 and kon == bek)
    d["hata"] = c.js("document.documentElement.dataset.hata || null")
    d["gecti"] = all(d[k]["gecti"] for k in ("parca", "panel", "bos", "adim_degisti")) and not d["hata"]
    return d


def ek_sinama(c, kok):
    """Esc, önceki adımdan (gri) parça, kablo şeması, patlat / tak / geri al, öncekiler kısayolu, küçük görünüm kısayolu."""
    e = {}
    # Esc (adım 31)
    c.git(url(kok, "?adim=31&tema=light"), cekim=False)
    n = c.js("RehberTest.tikNoktasi('p0781')") or c.js("RehberTest.tikNoktasi('p0750')")
    if n:
        c.tikla(n["x"], n["y"])
    o = vurgu(c)["sayi"]
    c.tus("Escape", "Escape", 27)
    o2 = vurgu(c)["sayi"]
    e["esc"] = dict(once=o, sonra=o2, gecti=o > 0 and o2 == 0)
    # önceki adımdan parça (adım 33: gri parçalar)
    c.git(url(kok, "?adim=33&tema=light"), cekim=False)
    sec = c.js("""(function(){const T=RehberTest; const ids=Object.keys(T.PAR).filter(id=>T.PAR[id].obj&&T.PAR[id].obj.visible&&T.PAR[id].obj.userData.d==='onceki');
      for (const id of ids.slice(0,400)){ const n=T.tikNoktasi(id); if(n) return {id:id,n:n}; } return null;})()""")
    if sec:
        p = PARV[sec["id"]]; st = V["adimlar"][p["a"]]
        row = gorunen(c, next((x["ids"] for x in st["parcalar"] + st["baglantilar"] if sec["id"] in x["ids"]), [sec["id"]]))
        c.tikla(sec["n"]["x"], sec["n"]["y"])
        g = vurgu(c)
        e["onceki_parca"] = dict(id=sec["id"], ad=p["ad"], adim=p["a"], beklenen=len(row), vurgulu=g["sayi"],
                                 gecti=g["ana"] == [sec["id"]] and g["ids"] == row)
    else:
        e["onceki_parca"] = dict(gecti=False)
    # kablo şeması (adım 32)
    c.git(url(kok, "?adim=32&tema=light"), cekim=False)
    sm = [i for i, s in enumerate(V["semalar"]) if s["a"] == 32]
    ok = None
    for i in sm:
        n = c.js("RehberTest.tikNoktasi({sema:%d})" % i)
        if n:
            c.tikla(n["x"], n["y"]); ok = i; break
    if ok is not None:
        g = vurgu(c)
        et = c.js("document.getElementById('etiket').textContent")
        e["sema"] = dict(sema=ok, ad=V["semalar"][ok]["ad"], vurgulu=g["sayi"], etikette=V["semalar"][ok]["ad"] in (et or ""),
                         gecti=g["ids"] == ["sema%d" % ok] and V["semalar"][ok]["ad"] in (et or ""))
    else:
        e["sema"] = dict(gecti=False, neden="şemaya tıklanacak nokta yok")
    # patlat / tak / geri al / öncekiler / küçük görünüm (adım 31, klavye)
    c.git(url(kok, "?adim=31&tema=light"), cekim=False)
    c.tus("p", "KeyP", 80); c.bekle("!RehberTest.anim()", 10)
    s0 = c.js("RehberTest.sira()")
    for _ in range(3):
        c.tus(" ", "Space", 32); c.bekle("!RehberTest.anim()", 10)
    s3 = c.js("RehberTest.sira()"); v3 = vurgu(c)
    c.tus(" ", "Space", 32, shift=True)
    s2 = c.js("RehberTest.sira()")
    st = V["adimlar"][31]
    sat = [x["ids"] for x in st["parcalar"]] + [x["ids"] for x in st["baglantilar"]]
    if st.get("sira"):                       # F10c düzeltme 1: sıralı takma veri satır sırasını değil st.sira'yı izler (app.js siraKur)
        sk = {"p:%d" % i: x["ids"] for i, x in enumerate(st["parcalar"])}
        sk.update({"b:%d" % i: x["ids"] for i, x in enumerate(st["baglantilar"])})
        sat = [sk[k] for k in st["sira"]]
    u3 = c.js("(function(ids){const T=RehberTest; return ids.filter(id=>T.PAR[id]&&T.PAR[id].obj&&T.PAR[id].obj.userData.d==='simdi').sort();})(%s)"
              % json.dumps(sat[2]))
    o1 = c.js("RehberTest.onceki()"); c.tus("o", "KeyO", 79); o2 = c.js("RehberTest.onceki()"); c.tus("o", "KeyO", 79); o3 = c.js("RehberTest.onceki()")
    c.tus("o", "KeyO", 79)
    m1 = c.js("RehberTest.miniAcik()"); c.tus("m", "KeyM", 77); m2 = c.js("RehberTest.miniAcik()"); c.tus("m", "KeyM", 77)
    c.tus("p", "KeyP", 80)
    s_top = c.js("RehberTest.sira()")
    e["patlat_tak"] = dict(patlat=s0, uc_tak=s3, ucuncu_satir_vurgu=v3["sayi"], ucuncu_satir_ids=len(u3), geri=s2, topla=s_top,
                           gecti=bool(s0 and s0["n"] == 0 and s3["n"] == 3 and s2["n"] == 2 and s_top is None and v3["ids"] == u3))
    e["kisayol"] = dict(onceki=[o1, o2, o3], mini=[m1, m2], gecti=[o1, o2, o3] == ["opak", "saydam", "gizli"] and m1 != m2)
    # B-4 (düzeltme 1): patlat -> bütün satırlar takılınca kamera adım açılışındaki sıkı kadraja döner; Shift+Boşluk patlak kadraja
    e["tak_kadraj"] = []
    for a in (33, 31, 12):
        c.git(url(kok, "?adim=%d&tema=light" % a), cekim=False)
        d0 = (c.js("RehberTest.kadraj()") or {}).get("D")
        c.tus("p", "KeyP", 80); c.bekle("!RehberTest.anim()", 10)
        d1 = (c.js("RehberTest.kadraj()") or {}).get("D")
        n = (c.js("RehberTest.sira()") or {}).get("toplam", 0)
        for _ in range(n):
            c.tus(" ", "Space", 32); c.bekle("!RehberTest.anim()", 10)
        time.sleep(0.2)
        s_son = c.js("RehberTest.sira()"); d2 = (c.js("RehberTest.kadraj()") or {}).get("D")
        c.tus(" ", "Space", 32, shift=True); c.bekle("!RehberTest.anim()", 10)
        d3 = (c.js("RehberTest.kadraj()") or {}).get("D")
        e["tak_kadraj"].append(dict(adim=a, satir=n, D_acilis=d0, D_patlak=d1, D_hepsi_takili=d2, D_geri_al=d3, sira_son=s_son,
                                    gecti=bool(d0 and d1 and d2 and s_son and s_son["n"] == n and d1 > d0 * 1.05
                                               and abs(d2 - d0) <= 0.05 * d0 and abs(d3 - d1) <= 0.05 * d1)))
    e["tak_kadraj"] = dict(adimlar=e["tak_kadraj"], gecti=all(x["gecti"] for x in e["tak_kadraj"]))
    e["hata"] = c.js("document.documentElement.dataset.hata || null")
    return e


def agsiz(c, kok):
    c.cmd("Network.enable"); c.cmd("Runtime.enable"); c.cmd("Log.enable")
    c.cmd("Network.emulateNetworkConditions", offline=True, latency=0, downloadThroughput=-1, uploadThroughput=-1)
    c.cmd("Network.setBlockedURLs", urls=["http://*", "https://*", "ws://*", "wss://*"])
    c.olay.clear()
    sonuc = []
    for q in ("?adim=31", "?adim=0&tema=dark", "?adim=17&cekim=1"):
        ok = c.git(url(kok, q), cekim="cekim" in q)
        c.tus("p", "KeyP", 80); c.tus(" ", "Space", 32); c.bekle("!RehberTest.anim()", 10)
        model = c.js("(function(){const T=window.RehberTest; if(!T) return 0; let n=0; for(const id in T.PAR) if(T.PAR[id].obj) n++; return n;})()")
        sonuc.append(dict(url=q, hazir=ok, model_mesh=model, hata=c.js("document.documentElement.dataset.hata || null")))
    istek = [m["params"]["request"]["url"] for m in c.olay if m["method"] == "Network.requestWillBeSent"]
    dis = sorted({u for u in istek if not u.startswith(("file:", "data:", "blob:", "about:"))})
    kons = [m for m in c.olay if (m["method"] == "Runtime.consoleAPICalled" and m["params"]["type"] == "error")
            or m["method"] == "Runtime.exceptionThrown" or (m["method"] == "Log.entryAdded" and m["params"]["entry"]["level"] == "error")]
    kons_ozet = [json.dumps(m["params"], ensure_ascii=False)[:300] for m in kons]
    c.cmd("Network.setBlockedURLs", urls=[])
    c.cmd("Network.emulateNetworkConditions", offline=False, latency=0, downloadThroughput=-1, uploadThroughput=-1)
    yerel = [u for u in istek if u.startswith("file:")]
    return dict(sayfa=sonuc, istek=len(istek), yerel_istek=len(yerel), dis_istek=len(dis), dis_ornek=dis[:10], konsol_hatasi=len(kons),
                konsol=kons_ozet, vendor_yuklendi=any("vendor/three-0.160.0-paket.min.js" in u for u in yerel),
                gecti=not dis and not kons and all(s["hazir"] and s["model_mesh"] == len(V["parcalar"]) - 0 and not s["hata"] for s in sonuc))


YAZDIR_ESIK = 0.01                                                  # zeminden farklı piksel oranı; boş (temizlenmiş) tuval 0


def _zemin():
    m = re.search(r"--sahne:\s*#([0-9a-fA-F]{6})", open(os.path.join(REHBER, "stil.css"), encoding="utf-8").read())
    return tuple(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)) if m else (0xec, 0xea, 0xe4)


def _oran(w, h, piksel, z, n_kanal):
    """piksel: bayt dizisi (RGB ya da RGBA); 4 px adımla zeminden farklı (> 40) piksel oranı. WebGL dışı öğeler sayılmaz: alttaki
    lejant şeridi (%7) ve sağ alttaki küçük görünüm köşesi (1/6 x %36; CSS halka)."""
    n = f = 0
    x_mini, y_mini, y_lejant = w - w // 6, h - int(h * 0.36), h - int(h * 0.07)
    for y in range(0, y_lejant, 4):
        for x in range(0, w, 4):
            if x >= x_mini and y >= y_mini:
                continue
            k = (y * w + x) * n_kanal
            n += 1
            if abs(piksel[k] - z[0]) + abs(piksel[k + 1] - z[1]) + abs(piksel[k + 2] - z[2]) > 40:
                f += 1
    return f / max(1, n)


def yazdir_kareleri():
    """B-1 (düzeltme 1): teslim edilen yazdırma kareleri rehber/goruntu/adim-NN.png ve PDF'teki 3B görüntüler gerçekten çizili mi.
    Ölçü: sahne zemininden (stil.css --sahne) farklı piksel oranı, lejant ve küçük görünüm köşesi hariç; eşik 0,01 (boş tuvalde 0)."""
    from PIL import Image
    z = _zemin()
    kare = []
    for a in range(NA):
        y = os.path.join(REHBER, "goruntu", "adim-%02d.png" % a)
        if not os.path.exists(y):
            kare.append(dict(adim=a, var=False, oran=None, cizili=False)); continue
        with Image.open(y) as im:
            im = im.convert("RGB"); w, h = im.size
            r = _oran(w, h, im.tobytes(), z, 3)
        kare.append(dict(adim=a, var=True, oran=round(r, 4), boyut_kb=round(os.path.getsize(y) / 1024, 1), cizili=r >= YAZDIR_ESIK))
    bos = [k["adim"] for k in kare if not k["cizili"]]
    pdf = dict(olculdu=False)
    try:
        import fitz
        yol = os.path.join(ROBOT, "planlama", "rehber", "Lale-montaj-rehberi.pdf")
        sf = []
        with fitz.open(yol) as d:
            for i, p in enumerate(d):
                for im in p.get_images(full=True):
                    pm = fitz.Pixmap(d, im[0])
                    if pm.width < 600:
                        continue
                    if pm.n != 3 or pm.alpha:
                        pm = fitz.Pixmap(fitz.csRGB, pm, 0)
                    sf.append(dict(sayfa=i + 1, oran=round(_oran(pm.width, pm.height, pm.samples, z, pm.n), 4)))
            pdf = dict(olculdu=True, sayfa=d.page_count if not d.is_closed else None)
        pdf.update(goruntu=len(sf), bos_sayfa=[x["sayfa"] for x in sf if x["oran"] < YAZDIR_ESIK],
                   en_dusuk=min((x["oran"] for x in sf), default=None))
    except ImportError:
        pdf["neden"] = "PyMuPDF yok"
    return dict(esik=YAZDIR_ESIK, kare=kare, cizili=NA - len(bos), bos=bos, en_dusuk=min((k["oran"] or 0) for k in kare), pdf=pdf,
                gecti=not bos and pdf.get("olculdu") and pdf.get("goruntu", 0) >= NA and not pdf.get("bos_sayfa"))


def cdn_tara():
    bulgu = []
    for kok, _, dosyalar in os.walk(REHBER):
        if os.path.relpath(kok, REHBER).split(os.sep)[0] == "veri":
            continue
        for f in dosyalar:
            if not f.endswith((".html", ".js", ".css")):
                continue
            yol = os.path.join(kok, f); t = open(yol, encoding="utf-8", errors="replace").read()
            vendor = "vendor" in os.path.relpath(yol, REHBER).split(os.sep)
            desen = r"cdn\.jsdelivr|unpkg\.com|cdnjs\.|esm\.sh|skypack|importmap" if vendor else r"https?://|importmap|cdn\.jsdelivr|unpkg|cdnjs"
            for m in re.finditer(desen, t):
                bulgu.append("%s:%d %s" % (os.path.relpath(yol, ROBOT).replace("\\", "/"), t[:m.start()].count("\n") + 1, m.group(0)))
    return dict(bulgu=bulgu, gecti=not bulgu)


def goruntuler(c, head, yeni):
    c.boyut(1400, 900)
    liste = []
    for a in (12, 17, 31, 33, 44):
        for tema, ad in (("light", "acik"), ("dark", "koyu")):
            for kok, sur in ((head, "once"), (yeni, "sonra")):
                c.git(url(kok, "?adim=%d&cekim=1&tema=%s" % (a, tema)))
                y = os.path.join(HERE, "F10a-goruntu-%02d-%s-%s.png" % (a, ad, sur)); c.goruntu(y); liste.append(os.path.basename(y))
    for a, tak in ((31, 4), (33, 3)):
        c.git(url(yeni, "?adim=%d&cekim=1&tema=dark&onceki=saydam&patlat=1&tak=%d" % (a, tak)))
        y = os.path.join(HERE, "F10a-goruntu-%02d-koyu-saydam-patlat.png" % a); c.goruntu(y); liste.append(os.path.basename(y))
    # B-4: bütün satırlar takılınca sıkı kadraj
    c.git(url(yeni, "?adim=33&cekim=1&tema=dark&onceki=saydam&patlat=1&tak=99"))
    y = os.path.join(HERE, "F10a-goruntu-33-koyu-saydam-tak-son.png"); c.goruntu(y); liste.append(os.path.basename(y))
    # seçim vurgulu: 31 koyu QLED camı, 44 açık panel satırı (rulmanlar)
    c.git(url(yeni, "?adim=31&cekim=1&tema=dark&onceki=saydam"))
    n = c.js("RehberTest.tikNoktasi('p0781')") or c.js("RehberTest.tikNoktasi('p0750')")
    if n:
        c.tikla(n["x"], n["y"])
    y = os.path.join(HERE, "F10a-goruntu-31-koyu-secim.png"); c.goruntu(y); liste.append(os.path.basename(y))
    c.git(url(yeni, "?adim=44&cekim=1&tema=light"))
    r = c.js("(function(){const e=document.querySelector(\"#panel [data-satir='p:1']\")||document.querySelector('#panel [data-satir]'); const r=e.getBoundingClientRect(); return {x:r.left+30,y:r.top+r.height/2};})()")
    c.tikla(r["x"], r["y"])
    y = os.path.join(HERE, "F10a-goruntu-44-acik-secim.png"); c.goruntu(y); liste.append(os.path.basename(y))
    return liste


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goruntu-yok", "--kanit-yok", dest="goruntu_yok", action="store_true",
                    help="kanıt karelerini (F10a-goruntu-*.png) yazma; ölçümler aynı (F10d)")
    ap.add_argument("--json", default="", help="sonuç JSON'u bu yola (varsayılan planlama/d158/F10a-dogrula.json; F10d)")
    g = ap.parse_args()
    global CIKTI
    if g.json:
        CIKTI = os.path.abspath(g.json)
    tb = tarayici()
    t0 = time.time()
    tmp, head = head_kopya()
    sonuc = dict(tarih=time.strftime("%Y-%m-%d %H:%M"), tarayici=os.path.basename(tb), adim=NA,
                 yontem="CDP (Chrome DevTools protokolü), file://; önce = %s rehber sayfası geçici kopyada (three.js aynı 0.160 yerel paket)" % ONCE)
    c = Cdp(tb, "a")
    try:
        c.boyut(1400, 900)
        print("kadraj: once (%s)" % ONCE); once = kadraj_olc(c, head)
        print("kadraj: sonra"); sonra = kadraj_olc(c, REHBER)
        oo = [x.get("oran", 0) for x in once]; so = [x.get("oran", 0) for x in sonra]
        dusuk = [dict(adim=x["adim"], kod=x["kod"], oran=x["oran"], baslik=V["adimlar"][x["adim"]]["baslik"]) for x in sonra if x.get("oran", 0) < 0.05]
        sonuc["kadraj"] = dict(kare="1400 x 900 pencere, sahne alanı (panel hariç)", once_ortanca=round(statistics.median(oo), 4),
                               sonra_ortanca=round(statistics.median(so), 4), once_ortalama=round(statistics.mean(oo), 4),
                               sonra_ortalama=round(statistics.mean(so), 4), once_tasan_adim=sum(1 for x in once if x.get("tasan")),
                               sonra_tasan_adim=sum(1 for x in sonra if x.get("tasan")), sonra_tasan_parca=sum(x.get("tasan", 0) for x in sonra),
                               once_tasan_parca=sum(x.get("tasan", 0) for x in once),
                               sonra_ortulen_adim=sum(1 for x in sonra if x.get("ortulen")), buyuyen_adim=sum(1 for a, b in zip(oo, so) if b > a + 1e-4),
                               kuculen_adim=[dict(adim=i, once=a, sonra=b) for i, (a, b) in enumerate(zip(oo, so)) if b < a - 1e-4],
                               oran_005_alti=dusuk,
                               adimlar=[dict(adim=a["adim"], kod=a["kod"], once=a.get("oran"), sonra=b.get("oran"), once_tasan=a.get("tasan"),
                                             sonra_tasan=b.get("tasan"), sonra_ortulen=b.get("ortulen"), yeni_parca=b.get("n"),
                                             hazir=a["hazir"] and b["hazir"], hata=b.get("hata")) for a, b in zip(once, sonra)])
        k = sonuc["kadraj"]
        k["gecti"] = k["sonra_tasan_adim"] == 0 and k["sonra_ortanca"] > k["once_ortanca"] and all(x["hazir"] for x in k["adimlar"])
        print("  ortanca %.4f -> %.4f, tasan adim %d -> %d, <0.05: %s" % (k["once_ortanca"], k["sonra_ortanca"], k["once_tasan_adim"],
                                                                        k["sonra_tasan_adim"], [x["adim"] for x in dusuk]))
        print("mini 1400")
        m1 = mini_olc(c, REHBER, False)
        print("secim")
        sec = [secim_sina(c, REHBER, a) for a in (12, 17, 31, 33, 44, 34)]
        for s in sec:
            print("  adim %d %s: parca %s/%s panel %s/%s bos %s adim %s -> %s" % (s["adim"], s["tur"], s["parca"].get("vurgulu"), s["parca"].get("beklenen"),
                  s["panel"].get("vurgulu"), s["panel"].get("beklenen"), s["bos"].get("vurgulu"), s["adim_degisti"].get("sonra"), "GECTI" if s["gecti"] else "KALDI"))
        ek = ek_sinama(c, REHBER)
        print("  ek:", {k2: v.get("gecti") for k2, v in ek.items() if isinstance(v, dict)})
        print("agsiz")
        ag = agsiz(c, REHBER)
        print("  dis istek %d, konsol %d, gecti %s" % (ag["dis_istek"], ag["konsol_hatasi"], ag["gecti"]))
        gor = [] if g.goruntu_yok else goruntuler(c, head, REHBER)
    finally:
        c.kapat()
    c = Cdp(tb, "m")
    try:
        c.boyut(360, 1600, mobil=True)
        print("mini 360")
        m3 = mini_olc(c, REHBER, True)
    finally:
        c.kapat()
    shutil.rmtree(tmp, ignore_errors=True)
    tur = {s["tur"] for s in sec}
    sonuc["secim"] = dict(sinama=sec, gecen=sum(1 for s in sec if s["gecti"]), toplam=len(sec), turler=sorted(tur), ek=ek,
                          gecti=all(s["gecti"] for s in sec) and len(sec) >= 6 and {"tezgah", "kablolama"} <= tur and any(s["adim"] in (31, 33, 34) for s in sec)
                          and all(v.get("gecti") for v in ek.values() if isinstance(v, dict)) and not ek.get("hata"))
    sonuc["agsiz"] = ag
    sonuc["cdn"] = cdn_tara()
    sonuc["yazdir_kareleri"] = yazdir_kareleri()
    sonuc["mini"] = dict(masaustu=dict(cizilen=sum(1 for x in m1 if x["cizildi"]), gecen=sum(1 for x in m1 if x["gecti"]), adim=m1),
                         telefon_360=dict(cizilen=sum(1 for x in m3 if x["cizildi"]), gecen=sum(1 for x in m3 if x["gecti"]),
                                          tasma_max=max((x.get("tasma") or 0) for x in m3),
                                          panel_kesisim=sum(1 for x in m3 if x.get("panel_kesisim_px2")), adim=m3))
    sonuc["mini"]["gecti"] = sonuc["mini"]["masaustu"]["gecen"] == NA and sonuc["mini"]["telefon_360"]["gecen"] == NA
    sonuc["goruntu"] = gor
    # bilgi alanı (F10c düzeltme 1): veriyi yeniden üreten her pakette tanım gereği false; kabul ölçütü değil
    sonuc["veri_degismedi"] = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "rehber/veri"], cwd=ROBOT).returncode == 0
    sonuc["sure_s"] = round(time.time() - t0)
    sonuc["gecti"] = all(sonuc[k]["gecti"] for k in ("kadraj", "secim", "agsiz", "cdn", "mini", "yazdir_kareleri"))
    json.dump(sonuc, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    yk = sonuc["yazdir_kareleri"]
    print("yazdirma kareleri: cizili %d/%d (en dusuk oran %.4f), pdf goruntu %s, bos sayfa %s; tak kadraj %s" % (
        yk["cizili"], NA, yk["en_dusuk"], yk["pdf"].get("goruntu"), yk["pdf"].get("bos_sayfa"),
        [(x["adim"], x["D_acilis"], x["D_patlak"], x["D_hepsi_takili"], x["D_geri_al"]) for x in ek["tak_kadraj"]["adimlar"]]))
    print("secim %d/%d, agsiz dis %d konsol %d, kadraj ortanca %.4f -> %.4f tasan %d, mini %d/%d masaustu %d/%d 360 (tasma %d), cdn %d, veri %s -> %s" % (
        sonuc["secim"]["gecen"], sonuc["secim"]["toplam"], ag["dis_istek"], ag["konsol_hatasi"], sonuc["kadraj"]["once_ortanca"],
        sonuc["kadraj"]["sonra_ortanca"], sonuc["kadraj"]["sonra_tasan_adim"], sonuc["mini"]["masaustu"]["gecen"], NA,
        sonuc["mini"]["telefon_360"]["gecen"], NA, sonuc["mini"]["telefon_360"]["tasma_max"], len(sonuc["cdn"]["bulgu"]),
        "degismedi" if sonuc["veri_degismedi"] else "degisti (bilgi)", "GECTI" if sonuc["gecti"] else "KALDI"))
    sys.exit(0 if sonuc["gecti"] else 2)


if __name__ == "__main__":
    main()
