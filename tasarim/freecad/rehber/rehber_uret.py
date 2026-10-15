# 3B montaj rehberi: TEK KOMUT (sistem Python'u). CAD değişince:
#   python tasarim/freecad/rehber/rehber_uret.py                 # veri + mesh (FreeCAD, ~20 s) + kontrol + ekran görüntüleri
#   python tasarim/freecad/rehber/rehber_uret.py --veri-yok      # FreeCAD'i atla, yalnız tarayıcı kontrolü + görüntüler
#   python tasarim/freecad/rehber/rehber_uret.py --adimlar 1,4,9  # yalnız seçilen adımların görüntüsü (varsayılan: tümü)
# Adımlar:
#   1) rehber_veri.py (freecadcmd, ASCII başlatıcı C:/Users/Victus/.robot-cad/run_fc.py) -> rehber/veri/{rehber-veri.json,.js, robot.glb, robot-glb.js}
#   2) her adım için headless Chrome/Edge: rehber/index.html?adim=N&cekim=1 -> --dump-dom ile <html data-hata> (konsol hatası) ve
#      <body data-hazir> kontrolü; --screenshot -> planlama/rehber/goruntu/adim-NN.png
#   3) özet: planlama/rehber/kontrol.json (adım başına hata / hazır / görüntü)
import os, sys, json, subprocess, re, time, urllib.parse, argparse

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


def kontrol(adimlar, boyut=(1400, 900)):
    tb = tarayici()
    os.makedirs(GORUNTU, exist_ok=True)
    ortak = [tb, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--hide-scrollbars",
             "--window-size=%d,%d" % boyut, "--virtual-time-budget=25000", "--no-first-run", "--disable-extensions"]
    sonuc = []
    for a in adimlar:
        u = url(a)
        dom = subprocess.run(ortak + ["--dump-dom", u], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        hata = re.search(r'<html[^>]*data-hata="([^"]*)"', dom)
        hazir = 'data-hazir="1"' in dom
        png = os.path.join(GORUNTU, "adim-%02d.png" % a)
        subprocess.run(ortak + ["--screenshot=" + png, u], capture_output=True)
        s = dict(adim=a, hazir=hazir, hata=hata.group(1) if hata else None, goruntu=os.path.relpath(png, ROBOT).replace("\\", "/"))
        sonuc.append(s)
        print("  adim %2d  hazir=%s  hata=%s" % (a, hazir, s["hata"] or "-"))
    json.dump(dict(tarih=time.strftime("%Y-%m-%d %H:%M"), tarayici=os.path.basename(tb), sonuc=sonuc),
              open(os.path.join(ROBOT, "planlama", "rehber", "kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    kotu = [s for s in sonuc if s["hata"] or not s["hazir"]]
    print("tarayici kontrolu: %d adim, %d sorunlu" % (len(sonuc), len(kotu)))
    return not kotu


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
