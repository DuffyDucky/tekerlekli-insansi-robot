# P10.8f kontrol (B): P108f-etiket-olc.py değerlendiricisinin (degerlendir) bozma sınaması. Tarayıcı açmaz, depoya yazmaz.
# Girdi: B'nin kendi ölçümü P108f-kontrol-olcum/k5-etiket-olc.json. Her bozma ölçümün bellekteki kopyasını bozar;
# değerlendirici hata vermeli (YAKALANDI). Son satırdaki "kapsam dışı" bozmalar aracın bilerek bakmadığı şeyi gösterir (KACAR beklenir).
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108f-kontrol-olcum/B-etiket-olc-bozma.py
import copy, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D158 = os.path.dirname(HERE)
ROBOT = os.path.dirname(os.path.dirname(D158))
spec = importlib.util.spec_from_file_location("p108f_olc", os.path.join(D158, "P108f-etiket-olc.py"))
OLC = importlib.util.module_from_spec(spec)
spec.loader.exec_module(OLC)

V = json.load(open(os.path.join(ROBOT, "rehber", "veri", "rehber-veri.json"), encoding="utf-8"))
R0 = json.load(open(os.path.join(HERE, "k5-etiket-olc.json"), encoding="utf-8"))["olcum"]


def boz(f):
    o = copy.deepcopy(R0)
    f(o)
    return OLC.degerlendir(o, V)


def dusur(o):                       # 17.4 yazdırma karesinde A4 çizilmedi (P10.8f üretim 1'deki gerçek hata)
    x = o["17.4"]["sahne"]
    x["ciz"] = [u for u in x["ciz"] if u["t"] != "A4"]
    x["dom"] = len(x["ciz"])


def disari(o):                      # kutu güvenli alanın dışına
    u = o["17.4"]["etk"]["ciz"][0]
    u["kutu"]["y0"] = u["alan"]["y0"] - 20


def cakis(o):                       # iki parça etiketi üst üste
    a, b = o["17.4"]["sahne"]["ciz"][0], o["17.4"]["sahne"]["ciz"][1]
    b["kutu"] = dict(a["kutu"])


def uc_cakis(o):                    # parça etiketi bir uç etiketinin kutusuna
    x = o["12"]["etk"]
    q = x["uc_kutu"][0]
    x["ciz"][0]["kutu"] = {k: q[k] for k in ("x0", "y0", "x1", "y1")}


def dom(o):                         # DOM'da çizim yok ama liste dolu
    o["12"]["sahne"]["dom"] = 0


def yazi(o):                        # yanlış yazı
    o["17.4"]["etk"]["ciz"][2]["t"] = "A9"


def bos_olcum(o):                   # konum hiç ölçülmemiş
    o.pop("12")


def nokta_takas(o):                 # kapsam dışı: A1 / A2 parça noktaları yer değiştirdi (yanlış saplamaya bağlanmış yazı)
    c = o["17.4"]["etk"]["ciz"]
    for k in ("ax", "ay"):
        c[0][k], c[1][k] = c[1][k], c[0][k]


def uzak(o):                        # kapsam dışı: kutu parçasından 300 px uzakta (güvenli alanda, çakışmasız)
    u = o["12"]["sahne"]["ciz"][0]
    for k in ("x0", "x1"):
        u["kutu"][k] += 300


BOZMA = [("A4 düşmüş (sahne)", dusur, True), ("kutu güvenli alan dışında", disari, True), ("iki yazı üst üste", cakis, True),
         ("yazı uç etiketinin üstünde", uc_cakis, True), ("DOM sayısı 0", dom, True), ("yanlış yazı A9", yazi, True),
         ("konum ölçülmemiş", bos_olcum, True),
         ("kapsam dışı: yazı yanlış saplamaya bağlı", nokta_takas, False), ("kapsam dışı: kutu parçadan uzak", uzak, False)]

if __name__ == "__main__":
    s = OLC.degerlendir(copy.deepcopy(R0), V)
    print("saglam: hata %d" % len(s))
    ok = not s
    for ad, f, bek in BOZMA:
        h = boz(f)
        yak = bool(h)
        print("%s %s -> %s" % ("YAKALANDI" if yak else "KACTI", ad, (h[0] if h else "-")[:150]))
        if bek:
            ok = ok and yak
    n = sum(1 for _a, _f, b in BOZMA if b)
    print("SONUC:", "GECER (kapsamdaki %d bozma yakalandı)" % n if ok else "KALDI")
    sys.exit(0 if ok else 1)
