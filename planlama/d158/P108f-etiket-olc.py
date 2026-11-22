# P10.8f: parça etiketi ölçümü (rehber_gorunum.etiket_isle → app.js ETK).
# P10.8g düzeltmesi (planlama/d158/P108g-gunluk.md § 6): ölçüm TESLİM EDİLEN karenin çekimiyle yapılır. P10.8f sürümü her konumu
# DevTools çekimiyle ölçüyordu; alt adımlı karede (17.4) bu üretimin çekimiyle aynı, alt adımı olmayan adımda (B5a = adım 12) üretim
# kareyi --screenshot ile çeker ve kadraj farklıdır (P108f-kontrol.md § 10 N4). Şimdi çekim rehber_uret.py ile birebir:
#   alt adım (N.J): rehber_uret.Cdp, Emulation.setDeviceMetricsOverride, ?adim=N.J&cekim=1&sahne=1&tema=light (1200 x 720, yazdırma
#     karesi rehber/goruntu/adim-NN-JJ.png) ve ?adim=N.J&cekim=1 (1400 x 900, planlama/rehber/goruntu/adim-NN-JJ.png); ölçüm
#     RehberTest.etiket() (alt_kontrol ile aynı açma ve bekleme);
#   alt adımı olmayan adım (N): üretim kareyi rehber_uret.ortak_arg + --screenshot ile çeker (sahne_goruntu 1200 x 720, kontrol
#     1400 x 900; JS çağrılamaz). Ölçüldü (P108g-gunluk.md § 6): o çağrıda sayfa önce Chrome'un başlangıç görüntü alanında (--window-size
#     eksi pencere payı; 1200 x 720 → 1182 x 624) yüklenip çizilir, çekimden önce görüntü alanı pencere boyuna büyür, kadraj ve etiketler
#     yeniden çizilir. Aynı çağrının --dump-dom'u büyümeden önceki DOM'u verir (kare değil). Bu yüzden: başlangıç görüntü alanı aynı
#     ortak_arg ile ölçülür (--dump-dom, innerWidth x innerHeight), CDP'de önce o boyutta açılır, sonra pencere boyuna büyütülür, çekilir
#     ve RehberTest.etiket() okunur.
# Her çekim teslim edilen kareyle piksel piksel karşılaştırılır: fark 0 değilse HATA (ölçülen kare teslim edilen kare değil). Bu, iki
# çekim yolunun üretimle aynı olduğunun kanıtı; benzetim tutmazsa araç geçmez.
# Kural (P10.8f'ten): verideki her yazı iki kipte de çizilmeli (cizilmedi boş, DOM g.etk sayısı = veri), kutu güvenli alanın içinde,
# parça etiketi kutuları birbiriyle ve uç etiketi kutularıyla çakışmaz. Yalnız okur; JSON'u verilen yola yazar.
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108f-etiket-olc.py [--rehber DIR --teslimsiz] [--json YOL] [--png DIR]
#   --rehber DIR: başka rehber kopyası (önizleme); teslim edilen kare yoksa --teslimsiz (karşılaştırma yapılmaz, sonuçta yazar)
import argparse, base64, json, os, re, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_uret as RU  # noqa: E402


def konumlar(V):
    for a in V["adimlar"]:
        if a.get("etiket"):
            yield a["i"], 0, a
        for j, g in enumerate(a.get("sira_grup") or [], 1):
            if g.get("etiket"):
                yield a["i"], j, g


def adr(s, j):
    return "%d.%d" % (s, j) if j else str(s)


def ust(a, b):
    return a["x0"] < b["x1"] and b["x0"] < a["x1"] and a["y0"] < b["y1"] and b["y0"] < a["y1"]


def teslim_yolu(s, j, kip):
    ad = "adim-%02d-%02d.png" % (s, j) if j else "adim-%02d.png" % s
    return os.path.join(RU.YAZDIR_GORUNTU if kip == "sahne" else RU.GORUNTU, ad)


def piksel_fark(a, b):
    """İki PNG'nin farklı piksel sayısı (RGB); boyut farklıysa -1. PIL yoksa None."""
    try:
        from PIL import Image, ImageChops
    except ImportError:
        return None
    with Image.open(a) as x, Image.open(b) as y:
        x, y = x.convert("RGB"), y.convert("RGB")
        if x.size != y.size:
            return -1
        d = ImageChops.difference(x, y).convert("L")
        return sum(1 for v in d.getdata() if v)


def degerlendir(olc, V, teslimsiz):
    hata = []
    for s, j, g in konumlar(V):
        ad = adr(s, j)
        bek = sorted(u["t"] for u in g["etiket"])
        for kip in ("sahne", "etk"):
            o = (olc.get(ad) or {}).get(kip) or {}
            if not teslimsiz and o.get("teslim_fark") != 0:
                hata.append("%s %s: ölçülen kare teslim edilen kare değil (farklı piksel %s, %s)" % (ad, kip, o.get("teslim_fark"), o.get("teslim")))
            ciz = o.get("ciz") or []
            if sorted(u["t"] for u in ciz) != bek:
                hata.append("%s %s: çizilen %s, veri %s; çizilmeyen %s" % (ad, kip, sorted(u["t"] for u in ciz), bek,
                                                                         [(u["t"], u["neden"]) for u in o.get("cizilmedi") or []]))
            if o.get("dom") != len(ciz):
                hata.append("%s %s: DOM g.etk %s ≠ çizilen %d" % (ad, kip, o.get("dom"), len(ciz)))
            tv, pb = o.get("tuval") or {}, o.get("png_boyut")
            for u in ciz:
                k, al = u["kutu"], u["alan"]
                if k["x0"] < al["x0"] - 0.5 or k["x1"] > al["x1"] + 0.5 or k["y0"] < al["y0"] - 0.5 or k["y1"] > al["y1"] + 0.5:
                    hata.append("%s %s: %s kutusu güvenli alanın dışında" % (ad, kip, u["t"]))
                # P10.8g: kutu çekilen karenin (PNG) içinde mi (tuval sayfada kaymış olabilir: alt adımsız karede tuval x < 0 ölçüldü)
                if pb and "x" in tv:
                    x0, x1, y0, y1 = k["x0"] + tv["x"], k["x1"] + tv["x"], k["y0"] + tv["y"], k["y1"] + tv["y"]
                    if x0 < -0.5 or y0 < -0.5 or x1 > pb[0] + 0.5 or y1 > pb[1] + 0.5:
                        hata.append("%s %s: %s kutusu karenin dışında (%.0f…%.0f × %.0f…%.0f, kare %d × %d)" % (ad, kip, u["t"], x0, x1, y0, y1, pb[0], pb[1]))
                elif not pb or "x" not in tv:
                    hata.append("%s %s: kare boyutu ya da tuval yeri ölçülmedi" % (ad, kip))
                    break
            for i, u in enumerate(ciz):
                for q in ciz[i + 1:]:
                    if ust(u["kutu"], q["kutu"]):
                        hata.append("%s %s: %s ile %s çakışıyor" % (ad, kip, u["t"], q["t"]))
                for q in o.get("uc_kutu") or []:
                    if ust(u["kutu"], q):
                        hata.append("%s %s: %s uç etiketi %s ile çakışıyor" % (ad, kip, u["t"], q["n"]))
    return hata


class AltCekim:
    """rehber_uret.alt_kontrol'ün açma / bekleme / çekim adımları (aynı Cdp sınıfı, aynı komutlar)."""

    def __init__(self, tb):
        self.c = RU.Cdp(tb)

    def ac(self, u, w, h):
        c = self.c
        c.cmd("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=False)
        c.js("document.body && (document.body.dataset.hazir = '0')")
        c.cmd("Page.navigate", url=u)
        q = u.split("?", 1)[1] if "?" in u else ""
        t = time.time()
        while time.time() - t < 60 and c.js("(location.search.slice(1) === %s && document.body && document.body.dataset.hazir) || ''"
                                            % json.dumps(q)) != "1":
            time.sleep(0.25)
        time.sleep(0.3)

    def cek(self, png):
        ek = self.c.cmd("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        open(png, "wb").write(base64.b64decode(ek["data"]))

    def kapat(self):
        self.c.kapat()


def ilk_alan(tb, boyut):
    """rehber_uret.ortak_arg(tb, boyut) çağrısında sayfanın ilk görüntü alanı (innerWidth, innerHeight); --dump-dom ile ölçülür."""
    u = "data:text/html,<body><script>document.body.setAttribute('data-alan',innerWidth+'x'+innerHeight)</script></body>"
    r = subprocess.run(RU.ortak_arg(tb, boyut) + ["--dump-dom", u], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r'data-alan="(\d+)x(\d+)"', r.stdout or "")
    if not m:
        raise SystemExit("ilk görüntü alanı ölçülemedi (%s)" % (boyut,))
    return int(m.group(1)), int(m.group(2))


def ana_cekim(alt, ilk, boyut, u, png):
    """rehber_uret --screenshot çekiminin benzetimi: ilk görüntü alanında aç, pencere boyuna büyüt, çizimin oturmasını bekle, çek."""
    alt.ac(u, *ilk)
    alt.c.cmd("Emulation.setDeviceMetricsOverride", width=boyut[0], height=boyut[1], deviceScaleFactor=1, mobile=False)
    t = time.time()
    while time.time() - t < 30 and alt.c.js("innerWidth + 'x' + innerHeight") != "%dx%d" % boyut:
        time.sleep(0.1)
    time.sleep(1.0)
    alt.cek(png)
    return alt.c.js("RehberTest.etiket()") or {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehber", default=os.path.join(ROBOT, "rehber"))
    ap.add_argument("--teslimsiz", action="store_true", help="teslim edilen kareyle karşılaştırma (önizleme kopyası için)")
    ap.add_argument("--json")
    ap.add_argument("--png", metavar="DIR", help="iki kipin çekimini DIR/<adres>-{sahne,etk}.png olarak yaz")
    g = ap.parse_args()
    kok = os.path.abspath(g.rehber)
    V = json.load(open(os.path.join(kok, "veri", "rehber-veri.json"), encoding="utf-8"))
    tb = RU.tarayici()
    gec = tempfile.mkdtemp(prefix="p108-etiket-olc-")
    png_dir = g.png or gec
    os.makedirs(png_dir, exist_ok=True)
    olc = {}
    ilk = {b: ilk_alan(tb, b) for b in ((1200, 720), (1400, 900))}
    alt = AltCekim(tb)
    try:
        for s, j, _g in konumlar(V):
            ad = adr(s, j)
            olc[ad] = {}
            for kip, boyut in (("sahne", (1200, 720)), ("etk", (1400, 900))):
                png = os.path.join(png_dir, "%s-%s.png" % (ad.replace(".", "-"), kip))
                ek = "&sahne=1&tema=light" if kip == "sahne" else ""
                if j:
                    alt.ac(RU.url(None, "?adim=%s&cekim=1%s" % (ad, ek), kok=kok), *boyut)
                    alt.cek(png)
                    o = alt.c.js("RehberTest.etiket()") or {}
                    o["cekim"] = "cdp %dx%d (rehber_uret.alt_kontrol)" % boyut
                else:
                    o = ana_cekim(alt, ilk[boyut], boyut, RU.url(s, ek, kok=kok), png)
                    o["cekim"] = "cdp %dx%d -> %dx%d (rehber_uret.%s --screenshot benzetimi)" % (
                        ilk[boyut] + boyut + ("sahne_goruntu" if kip == "sahne" else "kontrol",))
                try:
                    from PIL import Image
                    with Image.open(png) as im:
                        o["png_boyut"] = list(im.size)
                except Exception:                                    # noqa: BLE001  (PNG yok / PIL yok: değerlendirme hata yazar)
                    o["png_boyut"] = None
                if not g.teslimsiz:
                    t = teslim_yolu(s, j, kip)
                    o["teslim"] = os.path.relpath(t, ROBOT).replace("\\", "/")
                    o["teslim_fark"] = piksel_fark(png, t) if os.path.exists(t) and os.path.exists(png) else None
                olc[ad][kip] = o
    finally:
        alt.kapat()
    hata = degerlendir(olc, V, g.teslimsiz)
    r = dict(konum=len(olc), yazi=sum(len(x["etiket"]) for _s, _j, x in konumlar(V)), teslim_karsilastirma=not g.teslimsiz,
             ilk_alan={"%dx%d" % k: v for k, v in ilk.items()}, hata=hata, olcum=olc, gecti=not hata)
    if g.json:
        json.dump(r, open(g.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for ad, o in olc.items():
        for kip in ("sahne", "etk"):
            x = o[kip]
            print("  %-6s %-5s tuval %sx%s @ %s,%s yazi %spx yerlesim %s çizilen %d, çizilmeyen %s; teslim farkı %s" % (
                ad, kip, round(x.get("tuval", {}).get("w", 0)), round(x.get("tuval", {}).get("h", 0)), x.get("tuval", {}).get("x"),
                x.get("tuval", {}).get("y"), x.get("yazi_px"), x.get("yerlesim"),
                len(x.get("ciz") or []), [(u["t"], u["neden"], round(u.get("x", -1)), round(u.get("y", -1))) for u in x.get("cizilmedi") or []],
                "-" if g.teslimsiz else x.get("teslim_fark")))
    for h in hata:
        print("  HATA", h)
    print("parca etiketi: %d konum, %d yazi; teslim karsilastirmasi %s; hata %d -> %s" % (
        r["konum"], r["yazi"], "yok (--teslimsiz)" if g.teslimsiz else "var", len(hata), "GECTI" if not hata else "KALDI"))
    sys.exit(0 if not hata else 2)


if __name__ == "__main__":
    main()
