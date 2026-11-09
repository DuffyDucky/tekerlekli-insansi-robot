# -*- coding: utf-8 -*-
"""
F9b (P9.2) dogrulama: demo sayfasindaki her sayi kaynak JSON'la ayni mi?

  py -3 planlama/d158/F9b-dogrula.py              # tum denetimler (headless Chrome dahil); cikis 0 = gecer
  py -3 planlama/d158/F9b-dogrula.py --tarayicisiz  # yalniz statik denetimler (Chrome yoksa)
  py -3 planlama/d158/F9b-dogrula.py --goruntu      # ek olarak planlama/d158/F9b-goruntu-*.png ekran goruntuleri

Uretici (tasarim/cad/demo_uret.py) koduna dayanmaz: sayfaya gomulu <script id="kaynak"> yalniz "hangi dosya, hangi
anahtar, hangi bicim" bilgisini verir; bu betik o dosyayi kendisi acar, anahtari kendi cozucusuyla okur, kendi
bicimleyicisiyle yazar ve sayfadaki metinle karsilastirir. Denetimler:
  1. data-k: her bagli sayi = kaynak JSON degeri (bicimiyle); gomulu deger = kaynak degeri.
  2. Sayi taramasi: sayfa metnindeki (statik HTML ve Chrome'un DOM'u) her sayi data-k / data-mk / data-ui altinda mi?
     (data-ui muafiyeti yalniz "secenek" ve "secim" icin; "eski" / "duzeltme" icindeki sayi data-k'ya bagli olmali.)
     (harfe bitisik sayilar ad sayilir: DS3235, K44, X2D, F9b, 3B.)
  3. Maliyet: gomulu JSON = planlama/maliyet.json; DOM'daki her data-mk sayisi maliyet.json'dan Python'da yeniden hesaplanir.
  4. Model (goreli baglanti, KT-F9b-2 = b): sayfa ../rehber/veri/rehber-veri.js ve robot-glb.js'i <script> ile yukler;
     robot-glb.js icindeki GLB = robot.glb (bayt bayt), rehber-veri.js = rehber-veri.json, her GLB dugumu parcalar'da.
     Dosyalarin o anki hali okunur, sabit sha yok (F7b yeniden uretebilir).
  5. Kararlar: sayfada "karar bekliyor" gorunen her K, karar-kuyrugu.md ozet tablosunda "acik".
  6. Sayfa iddialari: eklem sinirlari kod/ortak/eklem_sinirlari.json ile sayisal ayni; servo toplami = DS3235 + MG996R;
     kafa 10,1" QLED, gogus 11,6", 10 servo ve brief sayilari (farkli ise hata). Maliyet isaretleri (duzeltme turu 1, O-1):
     kalem 33 F9b notu, kalem 36 ve 78 "eski tasarim notu" (gomulu listede ve Chrome'un DOM'unda).
  7. Eski 1,65 aramasi: sayfa, sablon, uretici, model tablosu ve DOM; her eslesmenin gerekcesi yazilir, gerekcesiz eslesme hata.
  8. Tarayici (DevTools): file:// ile acilir, konsol hatasi 0 (olaylardan), <body data-hazir="1">, 360 px (Emulation)te
     scrollWidth <= innerWidth (yatay kaydirma yok).
Standart kutuphane; tarayici denetimi icin websockets paketi (rehber_uret.py ile ayni).
"""
import base64
import hashlib
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from decimal import Decimal, ROUND_HALF_EVEN
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(HERE, "..", ".."))
SAYFA = "tasarim/Robot-Tasarim-Demosu.html"
SABLON = "tasarim/cad/viewer-template.html"
URETICI = "tasarim/cad/demo_uret.py"
MODEL_JS = {"veri": "../rehber/veri/rehber-veri.js", "glb": "../rehber/veri/robot-glb.js"}  # sayfaya (tasarim/) gore
KUYRUK = "planlama/d158/karar-kuyrugu.md"
MALIYET = "planlama/maliyet.json"
GLB = "rehber/veri/robot.glb"
REHBER = "rehber/veri/rehber-veri.json"
EKLEM_ONERI = "planlama/d158/F6a-eklem_sinirlari-oneri.json"
EKLEM_KOD = "kod/ortak/eklem_sinirlari.json"
TARAYICI = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
# O-1: maliyet kalemi -> beklenen isaret (bagimsiz liste; ureticinin KALEM_ISARET'i buna uymali)
ISARET = {33: ("duzeltme", "Yüz ekranı", "F9b notu: K32'ye bağlı; CAD'deki kafa ekranı QLED %s\""),
          36: ("eski", "Ekran kablosu", None), 78: ("eski", "Direnç seti", None)}
UI_SAYILI = {"secenek", "secim"}  # icinde bagsiz sayi olabilecek muafiyetler
UI_NEDEN = {"secenek": "pay seçenekleri (arayüz)", "secim": "tıklanan parçanın adı (model tablosundan)",
            "duzeltme": "maliyet notuna F9b uyarısı", "eski": "eski tasarım notu etiketi"}

HATA = []
# yerel kullanici klasoru yolu deseni; parcalardan kurulur ki bu dosya kendi desenini yakalamasin
YEREL = re.compile("|".join([r"[A-Za-z]:[\\/]+" + "Us" + r"ers[\\/]", "/" + "Us" + "ers/", "App" + r"Data[\\/]"]))


def hata(m):
    HATA.append(m)
    print("  HATA:", m)


def p(rel):
    return os.path.join(KOK, *rel.split("/"))


def oku(rel, kip="r"):
    with open(p(rel), kip, **({} if "b" in kip else {"encoding": "utf-8"})) as f:
        return f.read()


# ---------------------------------------------------------------- bagimsiz cozucu ve bicimleyici
def glb_json(b):
    cl = struct.unpack("<I", b[12:16])[0]
    return json.loads(b[20:20 + cl].decode("utf-8"))


def kaynak_ac(rel):
    if rel.endswith(".glb"):
        return glb_json(oku(rel, "rb"))
    return json.loads(oku(rel))


def coz(obj, ifade):
    islem = None
    if "#" in ifade:
        ifade, islem = ifade.split("#", 1)
    adimlar = re.findall(r"\[[^\]]*\]|[^.\[\]]+", ifade)
    liste_mi = False
    for a in adimlar:
        if a[0] == "[":
            alan, deger = a[1:-1].split("=", 1)
            obj = [x for x in obj if isinstance(x, dict) and str(x.get(alan)) == deger]
            liste_mi = True
            continue
        if liste_mi:
            assert len(obj) == 1, "%s: suzgec %d eleman verdi" % (ifade, len(obj))
            obj, liste_mi = obj[0], False
        obj = obj[int(a)] if isinstance(obj, list) else obj[a]
    if islem == "say":
        return len(obj)
    if liste_mi:
        assert len(obj) == 1, "%s: suzgec %d eleman verdi" % (ifade, len(obj))
        obj = obj[0]
    if islem and islem.startswith("re:"):
        m = re.search(islem[3:], obj)
        assert m, "%s: desen yok" % islem
        return m.group(1)
    assert not islem, "bilinmeyen islem " + str(islem)
    return obj


def tr(v, d):
    """JS toLocaleString('tr-TR') gibi: en kisa ondalik gosterimden yarim-cifte yuvarlama, binlik '.', ondalik ','."""
    q = Decimal(repr(abs(float(v)))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_EVEN)
    s = "{:,.{}f}".format(q, d).replace(",", " ").replace(".", ",").replace(" ", ".")
    return ("−" if v < 0 and s.strip("0,.") else "") + s


def bicim(v, b):
    if b == "s":
        return v
    d, k = (b[0], b[1]) if isinstance(b, list) else (b, 1)
    return tr(float(v) * k, d)


def js_round(x):
    return math.floor(x + 0.5)


# ---------------------------------------------------------------- HTML agaci
BOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Agac(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.yigin, self.parca, self.eleman, self.betik, self.govde = [], [], [], {}, False
        self._betik_id = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "body":
            self.govde = True
        if tag in BOS:
            return
        dugum = {"tag": tag, "a": a, "bas": len(self.parca)}
        self.yigin.append(dugum)
        if tag == "script":
            self._betik_id = a.get("id") or a.get("src") or "satir-ici-%d" % len(self.betik)
            self.betik[self._betik_id] = ""

    def handle_startendtag(self, tag, attrs):
        if tag not in BOS:
            self.handle_starttag(tag, attrs)
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in BOS:
            return
        for i in range(len(self.yigin) - 1, -1, -1):
            if self.yigin[i]["tag"] == tag:
                for d in self.yigin[i:][::-1]:
                    d["metin"] = "".join(t for t, _ in self.parca[d["bas"]:])
                    self.eleman.append(d)
                del self.yigin[i:]
                break
        if tag == "script":
            self._betik_id = None

    def handle_data(self, data):
        if self._betik_id is not None:
            self.betik[self._betik_id] += data
            return
        if not self.govde or any(d["tag"] in ("style", "script", "template", "noscript", "title") for d in self.yigin):
            return
        self.parca.append((data, [d["a"] for d in self.yigin]))


def agac(h):
    t = Agac()
    t.feed(h)
    t.close()
    return t


SAYI = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*(?![\w])")


def sayi_tara(t, ad):
    """Bagli olmayan sayilari dondurur; muafiyet sayimi da."""
    bagsiz, muaf, bagli = [], {}, 0
    for metin, ata in t.parca:
        for m in SAYI.finditer(metin):
            if any("data-k" in a or "data-mk" in a or "data-karar" in a for a in ata):
                bagli += 1
                continue
            ui = [a["data-ui"] for a in ata if "data-ui" in a]
            if ui and ui[-1] not in UI_SAYILI:
                bas = max(0, m.start() - 30)
                bagsiz.append("%s: '%s' data-ui=%s icinde (… %s …)" % (ad, m.group(0), ui[-1], metin[bas:m.end() + 30].strip()))
                continue
            if ui:
                muaf[ui[-1]] = muaf.get(ui[-1], 0) + 1
                continue
            bas = max(0, m.start() - 30)
            bagsiz.append("%s: '%s' (… %s …)" % (ad, m.group(0), metin[bas:m.end() + 30].strip().replace("\n", " ")))
    return bagsiz, muaf, bagli


# ---------------------------------------------------------------- 1. data-k
def kaynak_json(t):
    return json.loads(t.betik["kaynak"])


def denetle_datak(t, kn, ad):
    acik = {}
    n = 0
    for k, a in kn["anahtarlar"].items():
        try:
            v = coz(kaynak_ac(a["dosya"]), a["yol"])
        except Exception as e:
            hata("%s: %s okunamadi: %s" % (k, a["dosya"], e))
            continue
        if v != a["deger"]:
            hata("%s: gomulu deger %r, kaynak %r (%s · %s)" % (k, a["deger"], v, a["dosya"], a["yol"]))
        beklenen = bicim(v, a["bicim"])
        if beklenen != a["metin"]:
            hata("%s: gomulu metin %r, bicimlenmis kaynak %r" % (k, a["metin"], beklenen))
        acik[k] = beklenen
    gorulen = set()
    for e in t.eleman:
        k = e["a"].get("data-k")
        if k is None:
            continue
        n += 1
        gorulen.add(k)
        if k not in acik:
            hata("%s: sayfadaki data-k=%s kaynak tablosunda yok" % (ad, k))
        elif e["metin"] != acik[k]:
            hata("%s: data-k=%s metni %r, kaynak %r" % (ad, k, e["metin"], acik[k]))
    eksik = set(kn["anahtarlar"]) - gorulen
    if eksik:
        print("  bilgi: tabloda olup sayfada kullanilmayan anahtar: %s" % sorted(eksik))
    return n, acik


# ---------------------------------------------------------------- 3. maliyet (Python'da sayfa hesabi)
class Maliyet:
    def __init__(self, md):
        self.md = md
        self.K = md["kur"]
        self.pay_orani = md["pay"]
        baski = md.get("baski") or "yazici"

        def on(it):
            if it.get("secenek") and it["secenek"] != baski:
                return False
            if it.get("g") == "yedek" and False:
                return False
            if it.get("ver") and "v3" not in it["ver"].split(","):
                return False
            return True
        self.items = [i for i, it in enumerate(md["kalemler"]) if on(it)]   # elde dusulmez (varsayilan)
        self.sub, self.by = 0.0, {}
        for i in self.items:
            it = md["kalemler"][i]
            t = it["adet"] * it["tl"]
            self.sub += t
            self.by[it["g"]] = self.by.get(it["g"], 0.0) + t
        self.pay = self.sub * self.pay_orani
        self.tot = self.sub * (1 + self.pay_orani)

    def deger(self, k):
        md, K = self.md, self.K
        AY = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        sabit = {"genel": self.tot, "ara": self.sub, "pay": self.pay, "pay_yuzde": js_round(self.pay_orani * 100),
                 "genel_usd": js_round(self.tot / K), "ara_usd": js_round(self.sub / K), "kur": K,
                 "kalem_sayisi": len(self.items),
                 "dogrulanan": sum(1 for i in self.items if md["kalemler"][i].get("durum") == "dogrulandi"),
                 "stok_yok_sayisi": sum(1 for i in self.items if md["kalemler"][i].get("stok") == "yok"),
                 "stok_yok_adlar": ", ".join(md["kalemler"][i]["ad"] for i in self.items if md["kalemler"][i].get("stok") == "yok"),
                 "kur_kaynak": md["kur_kaynak"], "dipnot": md.get("dipnot", "")}
        sabit["tahmini_sayisi"] = sabit["kalem_sayisi"] - sabit["dogrulanan"]
        y, a, g = md["tarih"].split("-")
        sabit["tarih_uzun"] = "%d %s %s" % (int(g), AY[int(a) - 1], y)
        if k in sabit:
            return sabit[k]
        if ":" in k:
            tur, x = k.split(":", 1)
            if tur == "grup_ad":
                return [gr["ad"] for gr in md["gruplar"] if gr["id"] == x][0]
            if tur == "grup":
                return self.by[x]
            if tur == "grup_yuzde":
                return self.by[x] / self.sub * 100
            it = md["kalemler"][int(x)]
            if tur == "toplam":
                return it["adet"] * it["tl"]
            if tur == "adet":
                d = 1 if it["adet"] % 1 else 0
                return tr(it["adet"], d) + (" " + it["birim"] if it.get("birim") else "")
        return coz(md, k)


def denetle_maliyet(t, md, ad):
    M = Maliyet(md)
    n = 0
    goruldu = set()
    for e in t.eleman:
        k = e["a"].get("data-mk")
        if k is None:
            continue
        n += 1
        try:
            v = M.deger(k)
        except Exception as ex:
            hata("%s: data-mk=%s cozulemedi: %s" % (ad, k, ex))
            continue
        b = e["a"].get("data-b")
        if isinstance(v, str):
            beklenen = v
        elif b is None:
            beklenen = str(js_round(v)) if isinstance(v, float) else str(v)
        elif int(b) == 0:
            beklenen = tr(js_round(v), 0)
        else:
            beklenen = tr(v, int(b))
        if e["metin"] != beklenen:
            hata("%s: data-mk=%s metni %r, maliyet.json'dan %r" % (ad, k, e["metin"], beklenen))
        m = re.match(r"kalemler\.(\d+)\.ad$", k)
        if m:
            goruldu.add(int(m.group(1)))
    if goruldu != set(M.items):
        hata("%s: tablodaki kalemler (%d) sayfa kuralinin kalemleriyle (%d) ayni degil" % (ad, len(goruldu), len(M.items)))
    return n, M


# ---------------------------------------------------------------- 7. eski 1,65 aramasi
DESEN = [r"1650", r"1\.650", r"1,65(?![0-9])", r"1\.65(?![0-9])", r"(?<![0-9.,])165\s*cm", r"(?<![0-9.,])165\s*mm"]
ARA = re.compile("|".join(DESEN))


def ara_165(ad, metin, gerekce):
    """gerekce(konum) -> str ya da None (gerekcesiz)."""
    sonuc = []
    for m in ARA.finditer(metin):
        g = gerekce(m.start())
        bag = metin[max(0, m.start() - 40):m.end() + 40].replace("\n", " ")
        sonuc.append((ad, m.group(0), g, bag))
        if g is None:
            hata("eski sayi '%s' gerekcesiz: %s … %s …" % (m.group(0), ad, bag))
    return sonuc


# ---------------------------------------------------------------- 8. tarayici
def tarayici():
    for t in TARAYICI:
        if os.path.exists(t):
            return t
    return shutil.which("chrome") or shutil.which("msedge")


class Cdp:
    """Headless Chrome, DevTools protokoluyle. Masaustu Chrome penceresi ~500 px'in altina inmedigi icin 360 px
    Emulation.setDeviceMetricsOverride ile verilir (gercek 360 px goruntu alani). Konsol hatalari olaylardan sayilir:
    Runtime.exceptionThrown, Runtime.consoleAPICalled (error / assert), Log.entryAdded (error; yukleme hatalari dahil).
    websockets paketi gerekir (yoksa tarayici denetimi gecmez)."""

    def __init__(self, tb, profil):
        import urllib.request
        import websockets.sync.client as WS
        pf = os.path.join(profil, "DevToolsActivePort")
        self.p = subprocess.Popen([tb, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                   "--hide-scrollbars", "--remote-debugging-port=0", "--no-first-run", "--disable-extensions",
                                   "--user-data-dir=" + profil, "about:blank"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port = None
        for _ in range(200):
            if os.path.exists(pf):
                s = open(pf).read().split()
                if s:
                    port = int(s[0])
                    break
            time.sleep(0.2)
        if port is None:
            self.kapat()
            raise RuntimeError("DevTools portu okunamadi")
        hedef = []
        for _ in range(50):
            try:
                hedef = [x for x in json.load(urllib.request.urlopen("http://127.0.0.1:%d/json/list" % port))
                         if x.get("type") == "page"]
                if hedef:
                    break
            except OSError:
                pass
            time.sleep(0.2)
        self.ws = WS.connect(hedef[0]["webSocketDebuggerUrl"], max_size=None, open_timeout=20)
        self.n, self.olay = 0, []
        for m in ("Runtime.enable", "Log.enable", "Page.enable"):
            self.cmd(m)

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
        return self.cmd("Runtime.evaluate", expression=ifade, returnByValue=True).get("result", {}).get("value")

    def ac(self, url, gen, yuk, bekle=60):
        self.cmd("Emulation.setDeviceMetricsOverride", width=gen, height=yuk, deviceScaleFactor=1, mobile=gen < 600)
        self.olay = []
        self.cmd("Page.navigate", url=url)
        t0 = time.time()
        while time.time() - t0 < bekle:
            if self.js("document.readyState==='complete'&&document.body&&document.body.getAttribute('data-hazir')"):
                break
            time.sleep(0.3)
        time.sleep(0.8)                                     # ilk kare ve maliyet cizimi
        self.js("1")                                        # bekleyen olaylari topla

    def hatalar(self):
        out = []
        for m in self.olay:
            me, pr = m["method"], m.get("params", {})
            if me == "Runtime.exceptionThrown":
                out.append("istisna: " + str(pr.get("exceptionDetails", {}).get("exception", {}).get("description")
                                             or pr.get("exceptionDetails", {}).get("text"))[:300])
            elif me == "Runtime.consoleAPICalled" and pr.get("type") in ("error", "assert"):
                out.append("console.%s: %s" % (pr["type"], " ".join(str(a.get("value", a.get("description", "")))
                                                                      for a in pr.get("args", []))[:300]))
            elif me == "Log.entryAdded" and pr.get("entry", {}).get("level") == "error":
                e = pr["entry"]
                out.append("log: %s %s" % (e.get("text", "")[:240], e.get("url", "")[:120]))
        return out

    def goruntu(self, png, tam=False):
        ek = {}
        if tam:
            lm = self.cmd("Page.getLayoutMetrics")
            cs = lm.get("cssContentSize") or lm["contentSize"]
            ek = dict(captureBeyondViewport=True, clip=dict(x=0, y=0, width=cs["width"], height=cs["height"], scale=1))
        r = self.cmd("Page.captureScreenshot", format="png", **ek)
        with open(png, "wb") as f:
            f.write(base64.b64decode(r["data"]))

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


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # D-6: yonlendirilen cikti (cp1254) "−" / "·" ile cokmesin
    except (AttributeError, ValueError):
        pass
    arg = sys.argv[1:]
    print("F9b dogrulama:", SAYFA)
    h = oku(SAYFA)
    t = agac(h)
    kn = kaynak_json(t)

    print("[1] data-k: bagli sayilar kaynak JSON'la ayni mi")
    n, acik = denetle_datak(t, kn, "statik")
    print("    %d anahtar, sayfada %d bagli eleman" % (len(kn["anahtarlar"]), n))
    for k, a in kn["anahtarlar"].items():
        print("    %-34s %-28s %s · %s" % (k, acik.get(k, "?")[:28], a["dosya"], a["yol"]))
    for rel, sha in kn["dosyalar"].items():
        gercek = hashlib.sha256(oku(rel, "rb")).hexdigest()[:12]
        if gercek != sha:
            print("    bilgi: %s uretimden sonra degisti (%s -> %s); degerler yukarida yeniden okundu" % (rel, sha, gercek))

    print("[2] sayi taramasi (statik HTML)")
    bagsiz, muaf, bagli = sayi_tara(t, "statik")
    for b in bagsiz:
        hata("bagsiz sayi " + b)
    print("    sayi: %d bagli, %d muaf %s, %d bagsiz" % (bagli, sum(muaf.values()), muaf, len(bagsiz)))

    print("[3] maliyet: gomulu JSON = planlama/maliyet.json")
    md = json.loads(oku(MALIYET))
    if json.loads(t.betik["cost"]) != md:
        hata("gomulu maliyet JSON'u planlama/maliyet.json ile ayni degil")
    else:
        M = Maliyet(md)
        print("    ayni (%d kalem); sayfa kurali: %d kalem, ara %s, genel %s TL" % (
            len(md["kalemler"]), len(M.items), tr(M.sub, 2), tr(M.tot, 2)))

    print("[4] model: sayfa rehber dosyalarini goreli yukluyor; o anki halleri tutarli mi")
    for src in MODEL_JS.values():
        if src not in t.betik:
            hata("sayfa %s dosyasini <script src> ile yuklemiyor" % src)
    if "lale158-model.js" in h:
        hata("sayfa eski model kopyasina (lale158-model.js) bagli")
    yol_js = {k: os.path.relpath(os.path.normpath(os.path.join(os.path.dirname(p(SAYFA)), *v.split("/"))), KOK).replace("\\", "/")
              for k, v in MODEL_JS.items()}
    gb = oku(GLB, "rb")
    try:
        gj = oku(yol_js["glb"])
        m3 = re.fullmatch(r"window\.REHBER_GLB='([A-Za-z0-9+/=]+)';\s*", gj)
        if not m3 or base64.b64decode(m3.group(1)) != gb:
            hata("%s icindeki GLB, %s ile bayt bayt ayni degil" % (yol_js["glb"], GLB))
        vj = oku(yol_js["veri"])
        m4 = re.fullmatch(r"window\.REHBER_VERI=(\{.*\});\s*", vj, re.S)
        rv = json.loads(m4.group(1)) if m4 else None
        if rv is None:
            hata("%s okunamadi" % yol_js["veri"])
            rv = {"parcalar": []}
        elif rv != json.loads(oku(REHBER)):
            hata("%s, %s ile ayni degil (sayfanin sayilari .json'dan, modeli .js'ten)" % (yol_js["veri"], REHBER))
        par = {x["id"] for x in rv["parcalar"]}
        dugum = glb_json(gb)["nodes"]
        eksik = [nd["name"] for nd in dugum if nd["name"] not in par]
        if eksik:
            hata("rehber-veri.js parcalar %d GLB dugumunu kapsamiyor: %s" % (len(eksik), eksik[:5]))
        if kn.get("model", {}).get("dugum") != len(dugum):
            hata("gomulu model dugum sayisi %r, GLB %d" % (kn.get("model", {}).get("dugum"), len(dugum)))
        print("    %s: GLB %d bayt = %s (sha256 %s, o anki hali)" % (yol_js["glb"], len(gb), GLB, hashlib.sha256(gb).hexdigest()[:12]))
        print("    %s: %d parca = %s; %d GLB dugumunun hepsi parcalar'da" % (yol_js["veri"], len(par), REHBER, len(dugum)))
    except OSError as e:
        hata("model dosyasi okunamadi: %s" % e)

    print("[5] kararlar: sayfadaki 'karar bekliyor' = kuyrukta acik")
    durum = {}
    for s in oku(KUYRUK).splitlines():
        m = re.match(r"\|\s*(K\d+)\s*\|[^|]*\|\s*([^|]*)\|", s)
        if m and m.group(1) not in durum:
            durum[m.group(1)] = m.group(2).strip()
    sayfa_k = {}
    for e in t.eleman:
        k = e["a"].get("data-karar")
        if k:
            sayfa_k[k] = sayfa_k.get(k, 0) + 1
            if e["metin"] != "karar bekliyor · " + k:
                hata("karar etiketi %s: %r" % (k, e["metin"]))
            if not durum.get(k, "").startswith("**açık**"):
                hata("%s sayfada 'karar bekliyor', kuyrukta: %r" % (k, durum.get(k)))
    print("    %d karar, %d etiket: %s" % (len(sayfa_k), sum(sayfa_k.values()), ", ".join("%s×%d" % kv for kv in sorted(sayfa_k.items(), key=lambda x: int(x[0][1:])))))
    for k in ("K42", "K44", "K45"):
        if k not in sayfa_k:
            hata("brief ornegi %s sayfada yok" % k)

    print("[6] sayfa iddialari")
    on_ = json.loads(oku(EKLEM_ONERI))
    kd = json.loads(oku(EKLEM_KOD))
    fark = [e for e in on_["eklemler"] if (on_["eklemler"][e]["min"], on_["eklemler"][e]["max"]) !=
            (kd["eklemler"].get(e, {}).get("min"), kd["eklemler"].get(e, {}).get("max"))]
    if fark or on_.get("bagimli") != kd.get("bagimli") or on_["teker"]["ivme_sinir_m_s2"] != kd["teker"]["ivme_sinir_m_s2"]:
        hata("eklem sinirlari kod/ ile sayisal ayni degil: %s" % fark)
    else:
        print("    eklem sinirlari: %d eklemin min/max'i, bagimli sinirlar ve teker ivmesi kod/ ile ayni" % len(on_["eklemler"]))
    A = kn["anahtarlar"]
    if A["s_ds"]["deger"] + A["s_mg"]["deger"] != A["servo"]["deger"]:
        hata("servo toplami: %s + %s != %s" % (A["s_ds"]["deger"], A["s_mg"]["deger"], A["servo"]["deger"]))
    zorunlu = {"servo": 10, "kafa_in": "10,1", "gogus_in": "11,6"}
    for k, v in zorunlu.items():
        if A[k]["deger"] != v:
            hata("brief: %s %r bekleniyor, kaynak %r" % (k, v, A[k]["deger"]))
    if "QLED" not in A["kafa_kod"]["deger"]:
        hata("brief: kafa ekrani QLED degil")
    brief = {"boy": 1580.0, "reg_rampa_yuksuz": 1.519, "reg_tilt_payi": 3.64, "reg_pan_payi": 2.21, "reg_mik_hoparlor_mm": 574.3}
    for k, v in brief.items():
        print("    %s: kaynak %s, brief %s%s" % (k, A[k]["deger"], v, "" if A[k]["deger"] == v else "  (HATA: farkli)"))
        if A[k]["deger"] != v:
            hata("brief sayisi farkli: %s kaynak %r, brief %r" % (k, A[k]["deger"], v))
    gom = {z.get("kalem"): z for z in kn.get("kalem_isaret", [])}
    for i, (tur, kad, _m) in sorted(ISARET.items()):
        z = gom.get(i)
        if not z or z.get("tur") != tur:
            hata("maliyet isareti: kalem %d icin '%s' isareti sayfada yok" % (i, tur))
        if md["kalemler"][i].get("ad") != kad:
            hata("maliyet isareti: kalem %d adi %r (beklenen %r; maliyet.json degismis)" % (i, md["kalemler"][i].get("ad"), kad))
    print("    maliyet isaretleri (gomulu): %s" % ", ".join("kalem %d %s" % (i, ISARET[i][0]) for i in sorted(ISARET) if i in gom))
    print("    servo %d = %d DS3235 + %d MG996R; kafa %s\" QLED; gogus %s\"" % (
        A["servo"]["deger"], A["s_ds"]["deger"], A["s_mg"]["deger"], A["kafa_in"]["deger"], A["gogus_in"]["deger"]))
    for rel in (SAYFA, SABLON, URETICI, "planlama/d158/F9b-dogrula.py"):
        icerik = oku(rel)
        if YEREL.search(icerik):
            hata("yerel kullanici klasoru yolu: " + rel)

    print("[7] eski 1,65 aramasi")
    bulunan = []
    ci = h.index('<script id="cost" type="application/json">')
    ce = h.index("</script>", ci)
    bulunan += ara_165(SAYFA, h, lambda i: "maliyet.json gömülü kopyası (dokunulmaz kaynak; kalem ve not metni)" if ci < i < ce else None)
    bulunan += ara_165(SABLON, oku(SABLON), lambda i: None)
    bulunan += ara_165(URETICI, oku(URETICI), lambda i: None)

    tb = tarayici() if "--tarayicisiz" not in arg else None
    if "--tarayicisiz" in arg:
        print("[8] tarayici: ATLANDI (--tarayicisiz)")
    elif not tb:
        hata("Chrome / Edge bulunamadi (--tarayicisiz ile statik denetim)")
    else:
        print("[8] tarayici:", os.path.basename(tb), "(DevTools protokolu; 360 px Emulation ile)")
        url = "file:///" + p(SAYFA).replace("\\", "/")
        profil = tempfile.mkdtemp(prefix="f9b-chrome-")
        c = None
        try:
            c = Cdp(tb, profil)
            for gen, yuk in ((1400, 1000), (360, 800)):
                c.ac(url, gen, yuk)
                o = c.js("(function(){var d=document.documentElement;return {iw:window.innerWidth,sw:Math.max(d.scrollWidth,"
                         "document.body.scrollWidth),cw:d.clientWidth,hz:document.body.getAttribute('data-hazir'),"
                         "ht:d.getAttribute('data-hata')||'',h:d.scrollHeight}})()") or {}
                kons = c.hatalar()
                print("    %d px: innerWidth %s, scrollWidth %s, clientWidth %s, data-hazir=%s, data-hata=%r, konsol hatasi %d" % (
                    gen, o.get("iw"), o.get("sw"), o.get("cw"), o.get("hz"), o.get("ht"), len(kons)))
                if o.get("iw") != gen:
                    hata("%d px: innerWidth %s" % (gen, o.get("iw")))
                if o.get("sw", 10 ** 6) > o.get("cw", 0):
                    hata("%d px: yatay kaydirma var (scrollWidth %s > clientWidth %s)" % (gen, o.get("sw"), o.get("cw")))
                if o.get("ht"):
                    hata("%d px: sayfa hata sayaci: %s" % (gen, o["ht"]))
                for k in kons:
                    hata("%d px konsol: %s" % (gen, k))
                if o.get("hz") != "1":
                    hata("%d px: 3B model hazir degil (data-hazir=%s)" % (gen, o.get("hz")))
                dom = c.js("document.documentElement.outerHTML") or ""
                td = agac("<!doctype html>" + dom)
                n2, _ = denetle_datak(td, kaynak_json(td), "DOM %d" % gen)
                bagsiz, muaf, bagli = sayi_tara(td, "DOM %d" % gen)
                for b in bagsiz:
                    hata("bagsiz sayi " + b)
                nm, M = denetle_maliyet(td, md, "DOM %d" % gen)
                isr = c.js("(function(){var r={};%s.forEach(function(i){var e=document.querySelector('[data-mk=\"kalemler.'+i+'.model\"]'),"
                           "d=e&&e.closest('td'),z=d&&d.querySelector('em[data-isaret=\"'+i+'\"]');r[i]={var:!!d,eski:!!(d&&d.querySelector("
                           "'em.eski[data-ui=\"eski\"]')),duz:z?z.textContent:null,duzk:z?z.querySelectorAll('[data-k]').length:0};});"
                           "return r;})()" % json.dumps(sorted(ISARET))) or {}
                for i, (tur, _kad, metin) in sorted(ISARET.items()):
                    r = isr.get(str(i)) or {}
                    if not r.get("var"):
                        hata("DOM %d: maliyet kalemi %d tabloda yok" % (gen, i))
                    elif tur == "eski" and not r.get("eski"):
                        hata("DOM %d: kalem %d notunda 'eski tasarım notu' isareti yok" % (gen, i))
                    elif tur == "duzeltme":
                        bek = metin % acik["kafa_in"]
                        if r.get("duz") != bek or not r.get("duzk"):
                            hata("DOM %d: kalem %d F9b notu %r (beklenen %r, sayi data-k'ya bagli)" % (gen, i, r.get("duz"), bek))
                print("    %d px: maliyet isaretleri: %s" % (gen, ", ".join("kalem %s %s" % (i, "F9b notu" if v.get("duz") else (
                    "eski tasarım notu" if v.get("eski") else "-")) for i, v in sorted(isr.items(), key=lambda x: int(x[0])))))
                print("    %d px: data-k %d, data-mk %d (maliyet), sayi %d bagli, %d muaf %s, %d bagsiz" % (
                    gen, n2, nm, bagli, sum(muaf.values()), muaf, len(bagsiz)))
                for ui, say in sorted(muaf.items()):
                    print("      muaf %-9s %3d  %s" % (ui, say, UI_NEDEN.get(ui, "NEDENI TANIMSIZ")))
                    if ui not in UI_NEDEN:
                        hata("tanimsiz muafiyet data-ui=" + ui)
                if gen == 1400:
                    # DOM metninde 1,65: yalniz maliyet.json metninden gelen (data-mk) elemanlarda olabilir
                    for metin, ata in td.parca:
                        for mm in ARA.finditer(metin):
                            mk = [a.get("data-mk") for a in ata if "data-mk" in a]
                            g = ("maliyet.json metni (%s)" % mk[-1]) if mk else None
                            bulunan.append(("DOM", mm.group(0), g, metin[max(0, mm.start() - 40):mm.end() + 40]))
                            if g is None:
                                hata("DOM'da gerekcesiz eski sayi: " + metin[max(0, mm.start() - 40):mm.end() + 40])
            if "--goruntu" in arg:
                print("    ekran goruntuleri:")
                for ad, q, (gen, yuk), sec in (("1400-ust", "", (1400, 1000), None),
                                               ("1400-yan-seffaf", "?gorunum=yan&kabuk=seffaf", (1400, 1000), None),
                                               ("1400-modul-on", "?gorunum=on&renk=modul&kabuk=gizli", (1400, 1000), None),
                                               ("1400-korunan-eklem", "", (1400, 1000), "#korunan"),
                                               ("1400-baski-maliyet", "", (1400, 1000), "#baski"),
                                               ("1400-kararlar", "", (1400, 1000), "#takvim"),
                                               ("360-ust", "", (360, 800), None), ("360-model", "", (360, 800), "#vp"),
                                               ("360-eklem", "", (360, 800), "#eklem"), ("360-maliyet", "", (360, 800), "#maliyet")):
                    png = os.path.join(HERE, "F9b-goruntu-%s.png" % ad)
                    c.ac(url + q, gen, yuk)
                    if c.hatalar():
                        hata("goruntu %s: konsol hatasi %s" % (ad, c.hatalar()))
                    if sec:
                        c.js("document.querySelector(%s).scrollIntoView({block:'start'})" % json.dumps(sec))
                        time.sleep(0.6)
                    c.goruntu(png)
                    print("      %s %d KB" % (os.path.relpath(png, KOK).replace("\\", "/"), os.path.getsize(png) // 1024))
        except Exception as e:
            hata("tarayici denetimi kosamadi: %s" % e)
        finally:
            if c:
                c.kapat()
            shutil.rmtree(profil, ignore_errors=True)

    print("    1,65 eslesmeleri: %d" % len(bulunan))
    ozet = {}
    for ad, s, g, bag in bulunan:
        ozet[(ad, g)] = ozet.get((ad, g), 0) + 1
    for (ad, g), n in sorted(ozet.items(), key=lambda x: (x[0][0], str(x[0][1]))):
        print("      %-48s %3d  %s" % (ad, n, g or "GEREKCESIZ"))

    print()
    if HATA:
        print("SONUC: GECMEZ (%d hata)" % len(HATA))
        return 1
    print("SONUC: GECER (hata 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
