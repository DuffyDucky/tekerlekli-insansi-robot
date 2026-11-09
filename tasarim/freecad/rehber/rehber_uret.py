# 3B montaj rehberi: TEK KOMUT (sistem Python'u). CAD değişince:
#   python tasarim/freecad/rehber/rehber_uret.py                 # veri + mesh (FreeCAD, ~20 s) + kontrol + ekran görüntüleri
#   python tasarim/freecad/rehber/rehber_uret.py --veri-yok      # FreeCAD'i atla, yalnız tarayıcı kontrolü + görüntüler
#   python tasarim/freecad/rehber/rehber_uret.py --adimlar 1,4,9  # yalnız seçilen adımların görüntüsü (varsayılan: tümü)
# Adımlar:
#   1) rehber_veri.py (freecadcmd, ASCII başlatıcı C:/Users/Victus/.robot-cad/run_fc.py) -> rehber/veri/{rehber-veri.json,.js, robot.glb, robot-glb.js}
#   2) her adım için headless Chrome/Edge: rehber/index.html?adim=N&cekim=1 -> --dump-dom ile <html data-hata> (konsol hatası) ve
#      <body data-hazir> kontrolü; --screenshot -> planlama/rehber/goruntu/adim-NN.png
#   3) özet: planlama/rehber/kontrol.json (adım başına hata / hazır / görüntü; F7a: app.js'in <script id="kontrol-veri"> içine yazdığı
#      yeni görünen parça kimlikleri rehber-veri.json'dan beklenen listeyle karşılaştırılır; tüm adımlar koşulunca her parçanın tam
#      bir adımda yeni göründüğü de denetlenir)
import os, sys, json, subprocess, re, time, urllib.parse, argparse, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
REHBER = os.path.join(ROBOT, "rehber")
GORUNTU = os.path.join(ROBOT, "planlama", "rehber", "goruntu")
LAUNCH = r"C:\Users\Victus\.robot-cad\run_fc.py"
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


def url(adim):
    yol = os.path.join(REHBER, "index.html").replace("\\", "/")
    return "file:///" + urllib.parse.quote(yol, safe="/:") + "?adim=%d&cekim=1" % adim


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


def kontrol(adimlar, boyut=(1400, 900)):
    tb = tarayici()
    os.makedirs(GORUNTU, exist_ok=True)
    V = json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))
    AD = {p["id"]: "%s [%s]" % (p["ad"], p["modul"]) for p in V["parcalar"]}
    ortak = [tb, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--hide-scrollbars",
             "--window-size=%d,%d" % boyut, "--virtual-time-budget=25000", "--no-first-run", "--disable-extensions",
             "--user-data-dir=" + os.path.join(tempfile.gettempdir(), "lale-rehber-chrome")]   # açık Chrome profiline bağlanmasın
    sonuc = []
    simdi_say = {}                                                  # parça -> yeni (simdi) göründüğü adımlar (0 hariç)
    for a in adimlar:
        u = url(a)
        dom = subprocess.run(ortak + ["--dump-dom", u], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        hata = re.search(r'<html[^>]*data-hata="([^"]*)"', dom)
        hazir = 'data-hazir="1"' in dom
        kv = re.search(r'<script type="application/json" id="kontrol-veri">(.*?)</script>', dom, re.S)
        try:
            g = json.loads(kv.group(1)) if kv and kv.group(1).strip() else None
        except ValueError:
            g = None
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
            s.update(beklenen_simdi=len(b_simdi), gorunen_simdi=len(g_simdi), beklenen_alt=len(b_alt), gorunen_alt=len(g_alt),
                     beklenen_hedef=b_hedef, gorunen_hedef=g["hedef"], eksik_mesh=[AD.get(i, i) for i in g["eksik"]],
                     fark=[AD.get(i, i) for i in fark])
            s["gecti"] = bool(hazir and not s["hata"] and not fark and not g["eksik"] and g["hedef"] == b_hedef)
        else:
            s["gecti"] = False
        sonuc.append(s)
        print("  adim %2d %-4s hazir=%s hata=%s yeni %s/%s alt %s/%s %s" % (
            a, s["kod"], hazir, s["hata"] or "-", s.get("gorunen_simdi"), s.get("beklenen_simdi"), s.get("gorunen_alt"),
            s.get("beklenen_alt"), "GECTI" if s["gecti"] else "KALDI"))
    # her parça tam bir adımda (yalnız tüm adımlar koşulduysa anlamlı)
    tum = sorted(adimlar) == list(range(len(V["adimlar"])))
    tek = None
    if tum:
        coklu = {AD[i]: v for i, v in simdi_say.items() if len(v) != 1}
        hic = [AD[p["id"]] for p in V["parcalar"] if p["id"] not in simdi_say]
        tek = dict(gecti=not coklu and not hic and not V.get("atanmamis"), birden_cok_adimda=coklu, hic_gorunmeyen=hic)
    ozet = dict(adim=len(sonuc), gecen=sum(1 for s in sonuc if s["gecti"]), konsol_hatasi=sum(1 for s in sonuc if s["hata"]),
                parca_rehber=len(V["parcalar"]), parca_mesh=V["mesh"]["parca"], atanmamis=V.get("atanmamis", []),
                her_parca_tek_adimda=tek, veri_uretim=V["uretim"], kaynak_cad=V["kaynak"]["cad"])
    json.dump(dict(tarih=time.strftime("%Y-%m-%d %H:%M"), tarayici=os.path.basename(tb), ozet=ozet, sonuc=sonuc),
              open(os.path.join(ROBOT, "planlama", "rehber", "kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    kotu = [s for s in sonuc if not s["gecti"]]
    print("tarayici kontrolu: %d adim, %d gecti, %d sorunlu, konsol hatasi %d; her parca tek adimda: %s" % (
        len(sonuc), ozet["gecen"], len(kotu), ozet["konsol_hatasi"], tek["gecti"] if tek else "-"))
    return not kotu and (tek is None or tek["gecti"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--veri-yok", action="store_true")
    ap.add_argument("--gorsel-yok", action="store_true")
    ap.add_argument("--adimlar", default="")
    g = ap.parse_args()
    if not g.veri_yok:
        veri()
    if not g.gorsel_yok:
        n = len(json.load(open(os.path.join(REHBER, "veri", "rehber-veri.json"), encoding="utf-8"))["adimlar"])
        ad = [int(x) for x in g.adimlar.split(",") if x.strip()] or list(range(n))
        sys.exit(0 if kontrol(ad) else 2)
