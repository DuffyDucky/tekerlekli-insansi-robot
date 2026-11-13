# 3B montaj rehberi, A: adım verisi + hafif mesh. CAD'i YALNIZ OKUR (modül FCStd'leri), hiçbir CAD dosyasına yazmaz.
# Çalıştırma (README başlatıcısı; tek komut için rehber_uret.py bunu çağırır):
#   FC_SCRIPT=<bu dosya> "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/freecadcmd.exe" ~/.robot-cad/run_fc.py
#   (başlatıcı ASCII yolda; rehber_uret.py önce LALE_FC_LAUNCH ortam değişkenine bakar)
# Çıktı (Robot/rehber/veri/):
#   rehber-veri.json  adımlar (M6 tablosu + rehber_metin.py), parçalar (adım, alt montaj, uçuş yönü, bayrak), mesh düğüm adları
#   robot.glb         tüm parçalar; aynı geometri tek mesh, parça başına bir düğüm (ad = parça kimliği "p0001")
#   robot-glb.js      aynı GLB base64 (file:// altında fetch çalışmadığı için <script> ile yüklenir)
#   rehber-veri.js    aynı JSON (window.REHBER_VERI)
#
# Yöntem
# - Adım ataması: tasarim/freecad/rehber/rehber_secici.py (1,58 m seçicileri, F7a). Adım kodları M6 tablosundaki kodlardır;
#   seçicide olmayan kod tabloda yoksa betik durur. Atanamayan parça "atanmamis" listesine yazılır (kontrol bunu hata sayar).
# - Adım metinleri: M6-montaj-sirasi.md 2. bölüm tablosu (ayrıştırılır) + rehber_metin.py.
# - Mesh: parça şekli modül yerelinde üçgenlenir. Aynı şekiller (hacim, alan, asal momentler, asal çerçevede sınır kutusu) tek
#   mesh; düğüm matrisi = modül yerleşimi (sol = X aynası) · kütle merkezi · asal çerçeve. Normaller tarayıcıda hesaplanır.
# - Uçuş yönü (parça yerine nereden gelir): cıvata = eksen (baş dışarı), pul aynı, somun / çekiç somun ters; ana parça =
#   rehber_metin "ucus" ya da o adımda başı parçanın içinde kalan cıvataların ortalama ekseni, yoksa radyal / yukarı.
import os, sys, re, json, math, time, base64, struct, collections
import FreeCAD as App
import Part
import MeshPart

V = App.Vector
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.dirname(HERE)                                   # tasarim/freecad
ROBOT = os.path.dirname(os.path.dirname(FC))
ADIM4 = os.path.join(ROBOT, "planlama", "adim4")
CIKTI = os.path.join(ROBOT, "rehber", "veri")
os.makedirs(CIKTI, exist_ok=True)
sys.path.insert(0, HERE)
sys.path.insert(0, FC)
import rehber_metin as RM
import arayuz as A


def log(*a):
    print(*a, "(%.0f s)" % (time.time() - t0))
    sys.stdout.flush()


# ------------------------------------------------------------------ adım seçicileri (tek kaynak: rehber_secici.py, 1,58 m; F7a 09.11.2026)
# Önceden planlama/adim4/M6_erisim.py ADIMLAR exec ediliyordu (125 cm seçicileri); neden ayrıldığı rehber_secici.py başında.
import rehber_secici as RS
sys.path.insert(0, ADIM4)
import m6_yukle as Y                                          # modül dosyaları, hariç tutma, global yerleşim (yalnız okur)


# ------------------------------------------------------------------ M6 tablosu (Markdown)
def m6_tablo():
    md = open(os.path.join(ADIM4, "M6-montaj-sirasi.md"), encoding="utf-8").read()
    bol = md.split("## 2. Montaj sırası")[1].split("\n## ")[0]
    out = []
    for ln in bol.splitlines():
        m = re.match(r"^\|\s*(\d+|—)\s*\|\s*([A-Z]\w*)\s*\|(.*)\|(.*)\|(.*)\|(.*)\|\s*$", ln)
        if not m:
            continue
        hucre = [re.sub(r"\s+", " ", c.replace("<br>", "\n").strip()) if "<br>" not in c else
                 "\n".join(x.strip() for x in c.split("<br>") if x.strip()) for c in m.groups()[2:]]
        out.append(dict(no=m.group(1), kod=m.group(2), is_=hucre[0], baglanti=hucre[1], alet=hucre[2], erisim=hucre[3]))
    return out


TABLO = m6_tablo()
log("M6 tablosu: %d satir" % len(TABLO))
KODLAR = ["0"] + [r["kod"] for r in TABLO]
KOD_IDX = {k: i for i, k in enumerate(KODLAR)}
TEZGAH_KOD = dict(RS.TEZGAH)
BAGLANIR = dict(RS.BAGLANIR)
_bilinmeyen = [k for k, _t, _f in RS.ADIMLAR if k not in KOD_IDX]
if _bilinmeyen:
    raise SystemExit("rehber_secici kodu M6 tablosunda yok: %s" % _bilinmeyen)


# ------------------------------------------------------------------ yükleme (m6_yukle ile aynı kural, yerel şekil de tutulur)
def mod_matris(ad):
    (tx, ty, tz), ayna = A.modul_konum(ad)
    M = App.Matrix()
    if ayna:
        M.A11 = -1.0
    T = App.Matrix()
    T.move(V(tx, ty, tz))
    return T.multiply(M)


P = []
acik = {}
for mod in Y.DOSYA:
    yol = os.path.join(FC, Y.DOSYA[mod])
    if yol not in acik:
        acik[yol] = App.openDocument(yol)
    d = acik[yol]
    Mm = mod_matris(mod)
    for o in d.Objects:
        if o.TypeId != "Part::Feature" or not hasattr(o, "Tur"):
            continue
        if any(o.Label.startswith(h) for h in Y.HARIC.get(mod, ())):
            continue
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        g = [x.Label for x in o.InList if x.TypeId == "App::Part"]
        P.append(dict(modul=mod, grup=g[0] if g else "", ad=o.Label, kod=o.Kod, tur=o.Tur, malzeme=o.Malzeme,
                      dosya=Y.DOSYA[mod], yerel=s, shape=Y._global(s, mod), M=Mm))
for d in acik.values():
    App.closeDocument(d.Name)
for p in P:
    b = p["shape"].BoundBox
    p["bb"] = (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)
log("yuklendi: %d parca (referans dahil)" % len(P))


# ------------------------------------------------------------------ adım ataması
def tezgah_mi(kod):
    return TEZGAH_KOD.get(kod)


ATANMAMIS = []
for p in P:
    if p["tur"] == "Referans":
        if p["modul"] == "taban" and p["ad"].startswith("Kablo yolu"):
            p["kodr"], p["kablo"] = RM.kablo_kapisi(p["bb"][3]), True
        elif p["modul"] == "kafa":
            p["kodr"], p["kablo"] = "E3a", True
        else:
            p["kodr"] = "F1"                                       # ana anahtar düğmesi gösterimi (etek deliği K7)
        continue
    kod = RS.adim_bul(p)
    if kod is None:
        log("UYARI atanamadi:", p["ad"], p["modul"])
        ATANMAMIS.append("%s [%s]" % (p["ad"], p["modul"]))
        p["kodr"] = "F5"                                           # görünür kalsın; kontrol.json bunu hata sayar
        continue
    p["kodr"] = kod
for p in P:
    p["a"] = KOD_IDX[p["kodr"]]
    tz = tezgah_mi(p["kodr"])
    p["t"] = tz
    p["b"] = KOD_IDX[BAGLANIR[tz]] if tz else p["a"]


# ------------------------------------------------------------------ cıvata ekseni (M6_erisim.eksen ile aynı)
def eksen(s):
    cyl = [f for f in s.Faces if f.Surface.TypeId == "Part::GeomCylinder"]
    if not cyl:
        return None
    f = min(cyl, key=lambda f: (f.Surface.Radius, -f.Area))
    u = V(f.Surface.Axis).normalize()
    c = V(f.Surface.Center)
    ts = [(v.Point - c).dot(u) for v in s.Vertexes]
    t0_, t1_ = min(ts), max(ts)

    def uc(tu):
        pts = [v.Point for v in s.Vertexes if abs((v.Point - c).dot(u) - tu) < 0.6]
        rr = [((q - c) - u * (q - c).dot(u)).Length for q in pts]
        return (max(rr) if rr else 0.0), len(pts)

    r0, n0 = uc(t0_)
    r1, n1 = uc(t1_)
    bas_ust = (r1 > r0 + 0.1) or (abs(r1 - r0) <= 0.1 and n1 > n0)
    if bas_ust:
        return c + u * t1_, u, t1_ - t0_, c + u * t0_
    return c + u * t0_, u * -1, t1_ - t0_, c + u * t1_


def civata_mi(p):
    k = p["kod"]
    return p["tur"] == "Baglanti" and any(x in k for x in ("DIN 912", "ISO 7380", "DIN 913", "horn vidasi", "PT vida"))


def somun_tipi(p):
    a = (p["ad"] + " " + p["kod"]).lower()
    if "cekic somun" in a:
        return "cekic"
    if "pul" in a.split() or a.startswith("pul") or " pul " in a:
        return "pul"
    if "isil gomme" in a:
        return "gomme"
    if "somun" in a:
        return "somun"
    return None


CIV = []
for p in P:
    if civata_mi(p):
        e = eksen(p["shape"])
        if e:
            p["bas"], p["u"], p["boy"], p["uc"] = e[0], e[1], e[2], e[3]
            CIV.append(p)
log("civata ekseni: %d" % len(CIV))


def en_yakin_civata(p):
    c = p["shape"].BoundBox.Center
    best, kim = 1e9, None
    for q in CIV:
        if q["modul"] != p["modul"]:
            continue
        w = c - q["uc"]
        t = w.dot(q["u"])
        if t < -25 or t > q["boy"] + 25:
            continue
        r = (w - q["u"] * t).Length
        if r < best:
            best, kim = r, q
    return kim if best < 2.5 else None


# ------------------------------------------------------------------ M6 CAD bayrakları (19 + 10)
m6j = json.load(open(os.path.join(ADIM4, "M6_erisim_sonuc.json"), encoding="utf-8"))
IC_C = {23: "C1", 25.61: "C2", 24: "C3", 15: "C3"}
YOK = {(b["modul"], b["ad"]): IC_C.get(b["adim"]) for b in m6j["baglanti"]
       if b["montajda"].get("sinif") == "YOK" and b["adim"] != 25.5}
for p in P:
    f = YOK.get((p["modul"], p["ad"]))
    if f:
        p["m6"] = f
    elif p["modul"] == "kabuk" and civata_mi(p) and p["grup"].startswith("Govde_braket") and "M5" in p["kod"]:
        p["m6"] = "K1"
    elif p["modul"] == "kabuk" and civata_mi(p) and p["grup"].startswith("Etek_braket") and "M3x8" in p["kod"]:
        p["m6"] = "K2"
if not RM.M6_BAYRAK_ACIK:                                   # Y3 C1-C3 / K1-K7 CAD'e islendi; bayrak 125 cm JSON'undan
    for p in P:
        p.pop("m6", None)
M6SAY = collections.Counter(p.get("m6") for p in P if p.get("m6"))
log("M6 bayragi:", dict(M6SAY), sum(M6SAY.values()))


# ------------------------------------------------------------------ uçuş yönü
def birim(v):
    v = V(*v) if not isinstance(v, App.Vector) else V(v)
    return v.normalize() if v.Length > 1e-9 else V(0, 1, 0)


def ayna_x(v, p):
    return V(-v.x, v.y, v.z) if p["modul"].endswith("_sol") else v


def siki_kutu(p):
    """F10d: eğri yüzlü parçada BoundBox gevşek (etek panelinde köşegen ~750 mm, gerçek ~375 mm); patlatma mesafesi ve radyal yön
    sıkı kutudan (optimalBoundingBox, üçgenlemeyle). Olmazsa BoundBox."""
    if "_sk" not in p:
        try:
            p["_sk"] = p["shape"].optimalBoundingBox(True, False)
        except Exception:
            p["_sk"] = p["shape"].BoundBox
    return p["_sk"]


def radyal(p):                                                     # F10d: sıkı kutu merkezi
    c = siki_kutu(p).Center
    r = V(c.x, 0, c.z)
    return r.normalize() if r.Length > 5 else V(0, 1, 0)


def metin(kod):
    return RM.ADIM.get(kod, {})


ADIM_CIV = collections.defaultdict(list)
for q in CIV:
    ADIM_CIV[q["a"]].append(q)
taban_adim = {}                                                    # tezgâh grubunun ilk adımında en büyük parça yerinde durur
for p in P:
    if p["t"] and not civata_mi(p) and p["tur"] != "Baglanti":
        k = p["t"]
        bv = p["shape"].BoundBox.DiagonalLength
        if k not in taban_adim or (p["a"], -bv) < (taban_adim[k]["a"], -taban_adim[k]["shape"].BoundBox.DiagonalLength):
            taban_adim[k] = p


# F10d: patlatma mesafesi parça boyuyla orantılı: ana parça max(40, UCUS_ORAN × sıkı köşegen). F10c'ye kadar 1,1 × gevşek köşegendi
# (etek panelleri 630–830 mm uzağa gidiyordu). Cıvata 2,5 × boy (eksen boyunca, alet yolu rehber_sira.py'de bu eksenden).
UCUS_ORAN = 0.5
for p in P:
    bbx = p["shape"].BoundBox
    diag = siki_kutu(p).DiagonalLength
    kod = p["kodr"]
    u, dist = None, max(40.0, UCUS_ORAN * diag)
    if p.get("u") is not None:                                     # cıvata
        u, dist = p["u"], max(25.0, 2.5 * p["boy"])
    elif p["tur"] == "Baglanti":
        tip = somun_tipi(p)
        q = en_yakin_civata(p)
        if q is not None:
            u = q["u"] if tip == "pul" else q["u"] * -1
        dist = 25.0
    if u is None:
        mt = metin(kod).get("ucus")
        if p["t"] and taban_adim.get(p["t"]) is p:
            u, dist = V(0, 0, 0), 0.0
        elif mt == "radyal":
            u = radyal(p)
        elif mt:
            u = ayna_x(birim(mt), p)
        else:
            bb = V(bbx.XMin - 2, bbx.YMin - 2, bbx.ZMin - 2), V(bbx.XMax + 2, bbx.YMax + 2, bbx.ZMax + 2)
            ic = [q["u"] for q in ADIM_CIV[p["a"]] if all(bb[0][i] <= q["bas"][i] <= bb[1][i] for i in range(3))]
            if ic:
                s = V(0, 0, 0)
                for x in ic:
                    s = s + x
                u = birim(s)
            else:
                u = radyal(p) if not p["t"] else V(0, 1, 0)
    p["ucus"] = [round(u.x, 3), round(u.y, 3), round(u.z, 3)]
    p["ucus_mm"] = round(dist, 1)
    if p["b"] != p["a"]:                                           # alt montaj robota bağlanırken
        mt = metin(KODLAR[p["b"]]).get("ucus_bag", (0, 1, 0))
        ub = ayna_x(birim(mt), p)
        p["ucus_bag"] = [round(ub.x, 3), round(ub.y, 3), round(ub.z, 3)]


# ------------------------------------------------------------------ F10d: alt adım grubunun uçuş yönü + ısıl gömmenin ev sahibi
# rehber_metin "sira" grubunda ucus = {desen: (x, y, z) ya da "radyal"}: grubun ana parçalarının (cıvata değil; cıvatanın u'su alet
# ekseni, rehber_sira.py) geliş yönü. Vektör sağ taraf içindir; görünen adında "sol" kelimesi geçen parçada X aynalanır. Yönler giriş
# yolu ölçümüyle seçildi (planlama/d158/F10d-gunluk.md).
def gorunen(p):
    return RM.tr(RM.kopya_eki_sil(p["ad"], p["kod"]))


def merkez_(p):                                                    # sira grubunun konum koşulu için (rehber_metin.sira_grup_bul)
    c = p["shape"].BoundBox.Center
    return (c.x, c.y, c.z)


def yan_sol(p):
    return bool(re.search(r"\bsol\b", gorunen(p))) or p["modul"].endswith("_sol")


for p in P:
    if p["tur"] in ("Baglanti", "Referans") or p.get("kablo"):
        continue
    sira_ = metin(p["kodr"]).get("sira") or []
    g = RM.sira_grup_bul(sira_, gorunen(p), merkez_(p), p["modul"])
    uc = (sira_[g].get("ucus") or {}) if g is not None else {}
    v = next((uc[k] for k in uc if k in gorunen(p)), uc.get("*"))
    if v is None:
        continue
    if v == "yerinde":                                             # F10f düzeltme 1: tezgâhta yerinde duran ikinci taban (sol ön kol)
        p["ucus"], p["ucus_mm"] = [0.0, 0.0, 0.0], 0.0
        continue
    u = radyal(p) if v == "radyal" else birim(v)
    if v != "radyal" and yan_sol(p):
        u = V(-u.x, u.y, u.z)
    p["ucus"] = [round(u.x, 3), round(u.y, 3), round(u.z, 3)]
    if p["t"] and taban_adim.get(p["t"]) is p:                    # tezgâh tabanı yerinde durur
        p["ucus"], p["ucus_mm"] = [0.0, 0.0, 0.0], 0.0


# Isıl gömme somun baskıdan sonra takılıdır (hazırlık): kendi başına uçmaz, ev sahibi parçayla gelir (aynı u, d) ve adım içi sırada
# onun grubundadır. F10d düzeltme turu 1 (kontrol B-2): ev sahibi geometriyle, BÜTÜN ana parçalar arasından bulunur: somunun dış
# yüzünün 0,8 mm dışındaki halka noktalarının (eksen boyunca 3 yükseklik × 8 açı = 24 nokta) en çoğu hangi parçanın malzemesinin
# içindeyse (Part isInside) ev sahibi odur. Eskiden yalnız somunun seçicideki adımının parçaları aranıyordu (sınır kutusu): somun içteki
# (önceki adımın) bandın boss'undaysa doğru parça aday listesinde yoktu (34 somun yanlış parçada ya da ev sahipsizdi). Somun ev
# sahibinin takıldığı adıma (ve alt montajına) taşınır: rehberin öbür ısıl gömmeleri gibi o adımın hazırlık satırında sayılır.
def gomme_mi(p):
    return p["tur"] == "Baglanti" and "isil gomme" in p["kod"].lower()


def gomme_halka(p):
    """Isıl gömmenin dışındaki 24 örnek nokta (eksen: en küçük yarıçaplı silindir yüzü; yoksa sınır kutusunun tek boyutu)."""
    s = p["shape"]
    e = eksen(s)
    c = s.BoundBox.Center
    if e:
        u = V(e[1]).normalize()
    else:
        b = s.BoundBox
        L = [b.XLength, b.YLength, b.ZLength]
        m = sum(L) / 3.0
        k = max(range(3), key=lambda i: abs(L[i] - m))
        u = V(*[1.0 if i == k else 0.0 for i in range(3)])
    ts = [(v.Point - c).dot(u) for v in s.Vertexes]
    R = max(((v.Point - c) - u * (v.Point - c).dot(u)).Length for v in s.Vertexes)
    a1 = u.cross(V(1, 0, 0)) if abs(u.x) < 0.9 else u.cross(V(0, 1, 0))
    a1.normalize()
    a2 = u.cross(a1)
    out = []
    for t in (min(ts) * 0.6, 0.0, max(ts) * 0.6):
        for k in range(8):
            f = 2 * math.pi * k / 8
            out.append(c + u * t + a1 * ((R + 0.8) * math.cos(f)) + a2 * ((R + 0.8) * math.sin(f)))
    return out


ANA = [q for q in P if q["tur"] not in ("Baglanti", "Referans") and not q.get("kablo")]
ISIL = dict(yontem="ev sahibi: somunun 0,8 mm dışındaki 24 halka noktasından en çoğunu malzemesinin içinde tutan ana parça (Part "
                   "isInside, bütün ana parçalar aday; somunun sınır kutusu merkezine 8 mm'den yakın kutulu olanlar). Somun ev "
                   "sahibinin adımına ve alt montajına taşınır.", toplam=0, ev_sahipli=0, evsiz=[], tasinan=[], skor_alt=None)
_tg = time.time()
for p in P:
    if not gomme_mi(p):
        continue
    ISIL["toplam"] += 1
    c = p["shape"].BoundBox.Center
    nok = gomme_halka(p)
    aday = []
    for q in ANA:
        b = q["shape"].BoundBox
        if b.XMin - 8 <= c.x <= b.XMax + 8 and b.YMin - 8 <= c.y <= b.YMax + 8 and b.ZMin - 8 <= c.z <= b.ZMax + 8:
            n = sum(1 for x in nok if q["shape"].isInside(x, 0.01, True))
            if n:
                aday.append((n, q))
    if not aday:
        ISIL["evsiz"].append(p)
        log("UYARI isil gomme ev sahipsiz:", p["ad"], p["kodr"])
        continue
    aday.sort(key=lambda x: -x[0])
    n, h = aday[0]
    p["_h"], p["_h_skor"] = h, n
    ISIL["ev_sahipli"] += 1
    ISIL["skor_alt"] = n if ISIL["skor_alt"] is None else min(ISIL["skor_alt"], n)
    if (h["a"], h["t"]) != (p["a"], p["t"]):
        ISIL["tasinan"].append((p, p["kodr"], p["a"]))
        p["kodr"], p["a"], p["t"], p["b"] = h["kodr"], h["a"], h["t"], h["b"]
    p["ucus"], p["ucus_mm"] = list(h["ucus"]), h["ucus_mm"]
    if h.get("ucus_bag"):
        p["ucus_bag"] = list(h["ucus_bag"])
    else:
        p.pop("ucus_bag", None)
log("isil gomme ev sahibi: %d / %d, ev sahipsiz %d, adim degistiren %d, en dusuk skor %s / 24 (%.0f s)" % (
    ISIL["ev_sahipli"], ISIL["toplam"], len(ISIL["evsiz"]), len(ISIL["tasinan"]), ISIL["skor_alt"], time.time() - _tg))
for p, k0, a0 in ISIL["tasinan"]:
    log("  isil gomme tasindi: %s [%s] %s (%d) -> %s (%d), ev sahibi %s" % (p["ad"], p["modul"], k0, a0, p["kodr"], p["a"], p["_h"]["ad"]))

# F10d düzeltme 1 (kontrol B-11): alt adımlı adımda cıvatanın başı aynı alt adımda gelen (d > 0) bir ana parçanın kutusundaysa (2 mm
# pay) ve aynı yöne uçuyorsa cıvata patlatmada o parçadan az uzağa gitmesin: d = max(kendi d, parçanın d + 25). Eskiden max(25, 2,5 × boy): 49.5'te kapak
# 45–64 mm, cıvatası 25 mm, patlatılmış cıvata kapağın içinden geçiyor görünüyordu.
CIV_UZAT = []
for q in CIV:
    sira_ = metin(q["kodr"]).get("sira") or []
    if not metin(q["kodr"]).get("alt") or not sira_:
        continue
    gq = RM.sira_grup_bul(sira_, gorunen(q), merkez_(q), q["modul"])
    if gq is None:
        continue
    en = None
    for m in ANA:
        if m["a"] != q["a"] or m["t"] != q["t"] or m["ucus_mm"] <= 0:
            continue
        b = m["shape"].BoundBox
        x = q["bas"]
        if not (b.XMin - 2 <= x.x <= b.XMax + 2 and b.YMin - 2 <= x.y <= b.YMax + 2 and b.ZMin - 2 <= x.z <= b.ZMax + 2):
            continue
        if RM.sira_grup_bul(sira_, gorunen(m), merkez_(m), m["modul"]) != gq:
            continue
        # yalnız parçayla aynı yöne uçan cıvata (açı < 60°): ters yöne uçan cıvata (ör. 35.4 VESA, ekran önden, cıvata arkadan)
        # parçanın içinden geçmez; uzatılırsa patlatmada arkadaki banda girer
        if sum(a * b for a, b in zip(q["ucus"], m["ucus"])) < 0.5:
            continue
        if en is None or m["ucus_mm"] > en["ucus_mm"]:
            en = m
    if en is not None and en["ucus_mm"] + 25 > q["ucus_mm"]:
        CIV_UZAT.append((q, q["ucus_mm"], en))
        q["ucus_mm"] = round(en["ucus_mm"] + 25.0, 1)
log("civata patlatma mesafesi ev parcasina gore uzatildi: %d" % len(CIV_UZAT))
for q, d0, m in CIV_UZAT:
    log("  civata d %s: %.0f -> %.0f mm (ev %s, d %.0f)" % (q["ad"], d0, q["ucus_mm"], m["ad"], m["ucus_mm"]))

# F10f düzeltme 1 (kontrol F10f-K1): alt adım grubunda bağlantı elemanı ve parça için üç alan (rehber_metin "sira" grubu), yollar
# rehberin uçuş yolu ölçümüyle seçildi (planlama/d158/F10f-gunluk.md, Düzeltme turu 1):
#   ucus_d = {desen: mm}: patlatma mesafesi (somun 25 mm'de göğüs bandına / ön kola giriyordu; kısa yol temiz)
#   ucus_ters = (desen, ...): yön ters (somun tarafındaki pul en yakın cıvatanın yönünü alıyordu, cıvatanın başı tarafına uçuyordu)
#   birlikte = {desen: ev deseni}: parça aynı adımdaki en yakın ev parçasıyla birlikte uçar (veride h; servo mili servoyla, rulmanın
#              iç bileziği dış bileziğiyle, çatal-horn pulu cıvatasıyla); sıralı takmada ev sahibinin satırıyla yerine gelir
BIRLIKTE = []
for p in P:
    if p["tur"] == "Referans" or p.get("kablo"):
        continue
    sira_ = metin(p["kodr"]).get("sira") or []
    g = RM.sira_grup_bul(sira_, gorunen(p), merkez_(p), p["modul"])
    if g is None:
        continue
    gr = sira_[g]
    dd = next((v for k, v in (gr.get("ucus_d") or {}).items() if k in gorunen(p)), None)
    if dd is not None:
        p["ucus_mm"] = float(dd)
    if any(k in gorunen(p) for k in gr.get("ucus_ters") or ()):
        p["ucus"] = [-x for x in p["ucus"]]
    ev_ = next((v for k, v in (gr.get("birlikte") or {}).items() if k in gorunen(p)), None)
    if ev_:
        c = p["shape"].BoundBox.Center
        ad_ = [q for q in P if q["a"] == p["a"] and q is not p and ev_ in gorunen(q)]
        if not ad_:
            log("UYARI birlikte ev sahibi yok:", p["ad"], ev_)
            continue
        h = min(ad_, key=lambda q: (q["shape"].BoundBox.Center - c).Length)
        p["_h"] = h
        BIRLIKTE.append((p, h))
for p, h in BIRLIKTE:                                              # ev sahibinin son yönü / mesafesi (ucus_d / ters sonrası)
    p["ucus"], p["ucus_mm"] = list(h["ucus"]), h["ucus_mm"]
    if h.get("ucus_bag"):
        p["ucus_bag"] = list(h["ucus_bag"])
log("birlikte ucan: %d" % len(BIRLIKTE))
for p, h in BIRLIKTE:
    log("  %s [%s] -> %s" % (p["ad"], p["modul"], h["ad"]))


# ------------------------------------------------------------------ mesh: kanonik çerçeve + örnekleme
def cerceve(s):
    if len(s.Solids) != 1:
        return None
    so = s.Solids[0]
    try:
        pp = so.PrincipalProperties
    except Exception:
        return None
    com = so.CenterOfMass
    ax = sorted(zip(pp["Moments"], [V(pp["FirstAxisOfInertia"]), V(pp["SecondAxisOfInertia"]), V(pp["ThirdAxisOfInertia"])]), key=lambda t: t[0])
    m = [t[0] for t in ax]
    e = [t[1].normalize() for t in ax]
    sc = max(abs(x) for x in m) or 1.0
    esit = [abs(m[0] - m[1]) / sc < 1e-4, abs(m[1] - m[2]) / sc < 1e-4]
    pts = [v.Point - com for v in so.Vertexes]
    L = max(so.BoundBox.DiagonalLength, 1.0)

    def skew(ev):
        return sum((q.dot(ev) / L) ** 3 for q in pts)

    if all(esit):
        return None
    if not any(esit):
        for i in (0, 1):
            if skew(e[i]) < -1e-9:
                e[i] = e[i] * -1
        e[2] = e[0].cross(e[1])
    else:
        k = 2 if esit[0] else 0                                   # tekil eksen
        ek = e[k]
        if skew(ek) < -1e-9:
            ek = ek * -1
        best = None
        for q in pts:
            r = q - ek * q.dot(ek)
            key = (round(r.Length, 3), round(q.dot(ek), 3))
            if best is None or key > best[0]:
                best = (key, r)
        if best is None or best[1].Length < 1e-6:
            return None
        ea = V(best[1]).normalize()
        eb = ek.cross(ea)
        e = [ea, eb, ek]
    R = App.Matrix(e[0].x, e[1].x, e[2].x, 0, e[0].y, e[1].y, e[2].y, 0, e[0].z, e[1].z, e[2].z, 0, 0, 0, 0, 1)
    T = App.Matrix()
    T.move(com)
    F = T.multiply(R)                                              # kanonik -> yerel
    Fi = F.inverse()
    cp = [Fi.multVec(v.Point) for v in so.Vertexes]
    bb = tuple(round(f(c[i] for c in cp), 1) for i in range(3) for f in (min, max))
    key = (round(so.Volume, 1), round(so.Area, 1), tuple("%.4g" % x for x in m), bb)
    return F, key


def ucgenle(s, F, kablo=False):
    """MeshPart: dogrusal sapma parca boyuyla, acisal 0,5 rad; ucgen butcesini asarsa kabalasir. Kaynaklanmis (welded) mesh;
    tarayici kenarlari kirisim acisiyla (toCreasedNormals) keskin tutar."""
    diag = s.BoundBox.DiagonalLength
    tol = 3.0 if kablo else min(2.0, max(0.08, diag * 0.004))
    ang = 0.8 if kablo else 0.5
    for _ in range(4):
        m = MeshPart.meshFromShape(Shape=s, LinearDeflection=tol, AngularDeflection=ang, Relative=False)
        pts, tris = m.Topology
        if len(tris) <= 5000:
            break
        tol *= 1.8
        ang = min(1.2, ang * 1.4)
    Fi = F.inverse()
    pts = [Fi.multVec(V(q)) for q in pts]
    return pts, tris, tol


MESH = []                       # (positions list, tris)
MESH_KEY = {}
MESH_AD = []
I = App.Matrix()
for i, p in enumerate(P):
    p["id"] = "p%04d" % i
    s = p["yerel"]
    fr = cerceve(s)
    if fr:
        F, key = fr
        key = (p["dosya"],) + key
    else:
        F, key = I, (p["dosya"], p["ad"], "tek")
    if key not in MESH_KEY:
        pts, tris, tol = ucgenle(s, F, kablo=bool(p.get("kablo")))
        MESH_KEY[key] = len(MESH)
        MESH.append((pts, tris))
        MESH_AD.append(p["ad"])
    p["mesh"] = MESH_KEY[key]
    p["mat"] = p["M"].multiply(F)
for k in sorted(range(len(MESH)), key=lambda k: -len(MESH[k][1]))[:12]:
    print("  agir mesh %6d ucgen  %s" % (len(MESH[k][1]), MESH_AD[k]))
log("mesh: %d benzersiz / %d parca, %d ucgen" % (len(MESH), len(P), sum(len(m[1]) for m in MESH)))


# ------------------------------------------------------------------ GLB yaz
def glb_yaz(yol):
    bin_ = bytearray()
    views, accs, meshes = [], [], []

    def ekle(data, target):
        while len(bin_) % 4:
            bin_.append(0)
        off = len(bin_)
        bin_.extend(data)
        views.append(dict(buffer=0, byteOffset=off, byteLength=len(data), target=target))
        return len(views) - 1

    for pts, tris in MESH:
        flat = [c for q in pts for c in (q.x, q.y, q.z)]
        pv = ekle(struct.pack("<%df" % len(flat), *flat), 34962)
        mn = [min(q[i] for q in ((a.x, a.y, a.z) for a in pts)) for i in range(3)]
        mx = [max(q[i] for q in ((a.x, a.y, a.z) for a in pts)) for i in range(3)]
        accs.append(dict(bufferView=pv, componentType=5126, count=len(pts), type="VEC3", min=mn, max=mx))
        pa = len(accs) - 1
        idx = [k for t in tris for k in t]
        big = len(pts) > 65535
        iv = ekle(struct.pack("<%d%s" % (len(idx), "I" if big else "H"), *idx), 34963)
        accs.append(dict(bufferView=iv, componentType=5125 if big else 5123, count=len(idx), type="SCALAR"))
        meshes.append(dict(primitives=[dict(attributes=dict(POSITION=pa), indices=len(accs) - 1, mode=4)]))
    nodes = []
    for p in P:
        M = p["mat"]
        mat = [M.A11, M.A21, M.A31, M.A41, M.A12, M.A22, M.A32, M.A42, M.A13, M.A23, M.A33, M.A43, M.A14, M.A24, M.A34, M.A44]
        nodes.append(dict(name=p["id"], mesh=p["mesh"], matrix=[round(x, 6) for x in mat]))
    while len(bin_) % 4:
        bin_.append(0)
    gl = dict(asset=dict(version="2.0", generator="Lale rehber_veri.py (FreeCAD 1.1)"), scene=0,
              scenes=[dict(nodes=list(range(len(nodes))))], nodes=nodes, meshes=meshes, accessors=accs,
              bufferViews=views, buffers=[dict(byteLength=len(bin_))])
    js = json.dumps(gl, separators=(",", ":")).encode("utf-8")
    while len(js) % 4:
        js += b" "
    out = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_))
    out += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(bin_), 0x004E4942) + bytes(bin_)
    open(yol, "wb").write(out)
    return out


glb = glb_yaz(os.path.join(CIKTI, "robot.glb"))
with open(os.path.join(CIKTI, "robot-glb.js"), "w", encoding="ascii") as f:
    f.write("window.REHBER_GLB='" + base64.b64encode(glb).decode("ascii") + "';\n")
log("GLB: %.2f MB" % (len(glb) / 1e6))


# ------------------------------------------------------------------ adım verisi
def renk_sinifi(p):
    if p.get("kablo"):
        return "kablo"
    if p["tur"] == "Referans":
        return "ref"
    if p["tur"] == "Baglanti":
        return "baglanti"
    if p["tur"] == "Baski":
        return "cf" if "CF" in (p["malzeme"] or "") else "baski"
    if "sigma" in p["ad"].lower() or "rayi" in p["ad"].lower() or p["ad"] in ("Govde diregi", "Omuz traversi"):
        return "profil"
    return {"Lazer": "lazer", "Imalat": "imalat"}.get(p["tur"], "satin")


def kablo_rengi(ad):
    a = ad.lower()
    for k, r in (("toprak", "#222222"), ("acil", "#2e9e4f"), ("motor", "#e67e22"), ("servo", "#e2b714"), ("5 v", "#2f86d4"),
                 ("sinyal", "#8e44ad"), ("12 v", "#d63031")):
        if k in a:
            return r
    return "#c0392b"


tr = RM.tr                                                          # F7b: görünen metin katmanı rehber_metin.py'de (TR + TR_EK + TR_IFADE)


def temiz_ad(ad):
    """Grup adı için: sondaki parantezli açıklama ve FreeCAD kopya eki (001…099) atılır. F7b: eski kural sondaki her 3 haneyi
    atıyordu ("Govde braketi sag y400" -> "... y"); yalnız 0 ile başlayan ek atılır."""
    a = re.sub(r"(\D)0\d\d$", r"\1", ad)
    a = re.sub(r"\s*\((?:[^()]|\([^()]*\))*\)\s*$", "", a).strip()
    return a or ad


def yan_sil(ad):
    """Gruplama kökü: "sag" / "sol" kelimesi atılır (sağ ve sol parça aynı satırda, satır adında "(sağ + sol)")."""
    return re.sub(r"\s+", " ", re.sub(r"\b(?:sag|sol)\b", " ", ad)).strip() or ad


def yanlar(ps):
    y = set()
    for p in ps:
        a = temiz_ad(p["ad"])                                        # parantezli açıklamadaki "sag" sayılmaz
        if re.search(r"\bsag\b", a) or p["modul"].endswith("_sag"):
            y.add("sağ")
        if re.search(r"\bsol\b", a) or p["modul"].endswith("_sol"):
            y.add("sol")
    return y


KABLO_UYARI = []


def gorunen_ad(p):
    if p.get("kablo") and p["modul"] == "taban":
        ad, uy = RM.kablo_ad(p["ad"])
        if uy:
            KABLO_UYARI.append(uy)
            log("UYARI", uy)
        return ad
    return tr(RM.kopya_eki_sil(p["ad"], p["kod"]))                  # F7c (D-6): FreeCAD 0NN eki tıklama etiketinde görünmez


PARCA = []
for p in P:
    d = dict(id=p["id"], ad=gorunen_ad(p), modul=p["modul"], grup=p["grup"], kod=tr(p["kod"]), tur=p["tur"], malzeme=tr(p["malzeme"]),
             r=renk_sinifi(p), a=p["a"], b=p["b"], t=p["t"], u=p["ucus"], d=p["ucus_mm"])
    if p.get("ucus_bag"):
        d["ub"] = p["ucus_bag"]
    if p.get("m6"):
        d["m6"] = p["m6"]
    if p.get("_h"):                                                 # F10d: ısıl gömmenin ev sahibi (birlikte uçar)
        d["h"] = p["_h"]["id"]
    if p.get("kablo"):
        d["renk"] = kablo_rengi(p["ad"])
    PARCA.append(d)


def faz(kod):
    for on, ad in RM.FAZ:
        if kod.startswith(on):
            return ad
    return ""


ADIMLAR = []
satir = {r["kod"]: r for r in TABLO}
for i, kod in enumerate(KODLAR):
    mt = metin(kod)
    if kod == "0":
        h = RM.HAZIRLIK
        r = dict(no="0", is_=h["is_"], baglanti="", alet="", erisim="")
        mt = h
    else:
        r = satir[kod]
    ps = [p for p in P if p["a"] == i]
    parca = collections.OrderedDict()
    bag = collections.OrderedDict()
    uye = collections.defaultdict(list)
    # F10c (P10.3): adım içi sıra. rehber_metin "sira" grupları varsa satır anahtarının başına grup sırası girer (aynı kodlu bağlantı
    # iki gruptaysa iki satır olur), satırlar grup sırasıyla dizilir; adım verisine "sira" (app.js sıralı takma) ve "sira_grup"
    # (rehber_sira.py denetimi) yazılır. Grup eşleşmesi görünen adla (tr); hiçbir gruba uymayan parça son gruba ve UYARI.
    sira = mt.get("sira")

    def grup_i(p):
        if not sira:
            return 0
        if p.get("_h") is not None and p["_h"]["a"] == p["a"]:      # F10d: ısıl gömme ev sahibinin grubunda
            return grup_i(p["_h"])
        g = RM.sira_grup_bul(sira, tr(RM.kopya_eki_sil(p["ad"], p["kod"])), merkez_(p), p["modul"])
        if g is None:
            log("UYARI sira grubu yok:", kod, p["ad"])
            return len(sira) - 1
        return g
    for p in ps:
        if p["tur"] == "Referans":
            continue
        gi = grup_i(p)
        if p["tur"] == "Baglanti":
            k = (gi, p["kod"])
            e = bag.setdefault(k, dict(kod=tr(p["kod"]), adet=0, m6=0, ids=[],
                                       onceden=("isil gomme" in p["kod"].lower())))   # D-1: ısıl gömme baskıdan sonra takılı (hazırlık)
            e["adet"] += 1
            e["m6"] += 1 if p.get("m6") else 0
            e["ids"].append(p["id"])
        else:
            # F7b (P7.2 madde 5, F7a-kontrol D-3): anahtar kod + ad. Eskiden (kod, tür, renk) idi: aynı koddaki farklı parçalar
            # ilk parçanın adıyla tek satırda toplanıyordu (F2 "Gövde alt bandı sağ ×11"). Sağ / sol aynı satırda kalır.
            k = (gi, p["kod"], p["tur"], renk_sinifi(p), yan_sil(temiz_ad(p["ad"])))
            parca.setdefault(k, dict(kod=tr(p["kod"]), tur=p["tur"], malzeme=tr(p["malzeme"]), r=k[3], adet=0, ids=[]))
            parca[k]["adet"] += 1
            parca[k]["ids"].append(p["id"])
            uye[k].append(p)
    if sira and mt.get("alt"):                                     # F10d: alt adımlı adımda grup içinde desen sırası (panel = takma)
        def desen_i(kv):
            ds = sira[kv[0][0]].get("desen") or ()
            ad_ = gorunen(uye[kv[0]][0])
            return (kv[0][0], next((j for j, d in enumerate(ds) if d in ad_), len(ds)))
        parca = collections.OrderedDict(sorted(parca.items(), key=desen_i))
        bag = collections.OrderedDict(sorted(bag.items(), key=lambda kv: (kv[0][0], not kv[1]["onceden"])))   # ısıl gömme (hazırlık) önce
    elif sira:                                                     # satırlar grup sırasıyla (grup içinde model sırası)
        parca = collections.OrderedDict(sorted(parca.items(), key=lambda kv: kv[0][0]))
        bag = collections.OrderedDict(sorted(bag.items(), key=lambda kv: kv[0][0]))
    for k, e in parca.items():
        ps_ = uye[k]
        tam = {p["ad"] for p in ps_}
        if len(tam) == 1:
            ad = next(iter(tam))
            yn = yanlar(ps_) if ps_[0]["modul"].endswith(("_sag", "_sol")) else set()
        else:
            ad = k[4] if len({temiz_ad(p["ad"]) for p in ps_}) > 1 else temiz_ad(ps_[0]["ad"])
            yn = yanlar(ps_)
        e["ad"] = tr(ad) + (" (sağ + sol)" if len(yn) == 2 else (" " + next(iter(yn)) if yn and next(iter(yn)) not in tr(ad) else ""))
    nciv = sum(1 for p in ps if civata_mi(p))
    nsom = sum(1 for p in ps if p["tur"] == "Baglanti" and not civata_mi(p))
    sure = mt.get("sure_dk") or int(round(5 + 1.0 * nciv + 0.3 * nsom + 0.8 * sum(e["adet"] for e in parca.values())))
    m6not = sorted(set(p["m6"] for p in ps if p.get("m6")))
    ek = {}
    if sira:
        pk, bk = list(parca), list(bag)
        # F10d: alt adım alanları (tek kaynak: sira grubu = alt adım). tezgah: masa birimi anahtarı ("" robotta); F10c'nin
        # tezgah=True grubu kendi anahtarıyla ("g<n>") sıradaki yerinde bağlanır. bag: o anahtarlı birimi robota bağlayan grup
        # (kendi satırı yok), ub: bağlanırken geliş yönü. is_ / kamera / saydam / sema: alt adımın metni, kamera yönü, saydam çizilen
        # parçalar (desen; bu adımda ve öncekilerde), gösterilen şemalar (desen, aşağıda SEMALAR'dan).
        sg = []
        for n, g in enumerate(sira):
            e = dict(ad=g["ad"], tezgah=g.get("masa") or ("g%d" % n if g.get("tezgah") else ""), bag=g.get("bag") or "",
                     satir=["p:%d" % j for j, kk in enumerate(pk) if kk[0] == n] + ["b:%d" % j for j, kk in enumerate(bk) if kk[0] == n])
            if g.get("is_"):
                e["is_"] = g["is_"]
            if g.get("kamera"):
                e["kamera"] = list(g["kamera"]) if not isinstance(g["kamera"], str) else g["kamera"]
            if g.get("ucus_bag"):
                ub = birim(g["ucus_bag"])
                e["ub"] = [round(ub.x, 3), round(ub.y, 3), round(ub.z, 3)]
            if g.get("saydam"):
                e["saydam"] = [q["id"] for q in P if q["a"] <= i and q["tur"] != "Referans" and any(d in gorunen(q) for d in g["saydam"])]
            if g.get("kenar"):                                      # F10f düzeltme 1: kenar çizgisi alan parçalar (desen)
                e["kenar"] = [q["id"] for q in P if q["a"] <= i and q["tur"] != "Referans" and any(d in gorunen(q) for d in g["kenar"])]
            if g.get("sema"):
                e["_sema"] = tuple(g["sema"])
            if g.get("gizli_ok"):
                e["gizli_ok"] = dict(g["gizli_ok"])
            if g.get("ucus_ok"):
                e["ucus_ok"] = dict(g["ucus_ok"])
            if g.get("giris_ok"):
                e["giris_ok"] = dict(g["giris_ok"])
            if g.get("piksel_ok"):                                  # F10d düzeltme 1: görünürlük ölçütü istisnası {desen: gerekçe}
                e["piksel_ok"] = dict(g["piksel_ok"])
            sg.append(e)
        ek = dict(sira=[x for g in sg for x in g["satir"]], sira_grup=sg)
        if mt.get("alt"):
            ek["alt"] = len(sg)
            for p in ps:                                            # gösterim parçası (satırı yok) desenine uyan alt adımda görünür
                if p["tur"] == "Referans":
                    sg[grup_i(p)].setdefault("ref", []).append(p["id"])
    if mt.get("poz"):
        ek["poz"] = mt["poz"]
    if mt.get("saydam"):                                            # F10d: adım düzeyinde saydam çizilen önceki parçalar (desen)
        ek["saydam"] = [q["id"] for q in P if q["a"] < i and q["tur"] != "Referans" and any(d in gorunen(q) for d in mt["saydam"])]
    ADIMLAR.append(dict(
        i=i, kod=kod, no=r["no"], faz=faz(kod), baslik=mt.get("baslik") or r["is_"].split(":")[0][:60],
        is_=mt.get("is_") or r["is_"], baglanti_md=mt.get("baglanti_md") or r["baglanti"], alet=mt.get("alet") or r["alet"],
        erisim=mt.get("erisim") or r["erisim"], tezgah=TEZGAH_KOD.get(kod),
        baglanir=KOD_IDX[BAGLANIR[TEZGAH_KOD[kod]]] if TEZGAH_KOD.get(kod) else None,
        parcalar=list(parca.values()), baglantilar=list(bag.values()),
        kontrol=mt.get("kontrol", []), kablo=mt.get("kablo", []), not_=mt.get("not_", []), kamera=mt.get("kamera"),
        m6=[dict(kod=k, not_=RM.M6_CAD_NOT[k], adet=sum(1 for p in ps if p.get("m6") == k)) for k in m6not],
        sure_dk=sure, sure_tahmini=not mt.get("sure_dk"),
        kablolama=kod in ("K1", "K2"), **ek))


# ------------------------------------------------------------------ gösterim şemaları (F7b, P7.2 madde 4): lale158/kablo_yolu_ekran.py
# Parça DEĞİL: GLB'ye ve "parcalar"a girmez, parça sayısı modeldeki gibi kalır. app.js çizgi tüp olarak çizer (kendi adımında renkli,
# sonra saydam). Kaynak yalnız okunur (import; dosya değişmez).
sys.path.insert(0, os.path.join(FC, "lale158"))
import kablo_yolu_ekran as KYE                                     # noqa: E402
_yol, _qi = KYE.yollar(), KYE.kafa_ici_qled()
_K = A.KAFA
_Y0, _YT, _ZT = A.S3 + A.SG / 2, _K["tilt_nokta"][1], _K["tilt_nokta"][2]


def _bas(q):                                                       # kafa_ici_qled: tilt ekseni çerçevesi -> global (yollar() bas() ile aynı)
    return (q[0], _Y0 + _YT + q[1], _ZT + q[2])


SEMALAR = []
for kaynak, ad_k, kod, ad, renk in RM.SEMA:
    pts = _yol.get(ad_k) if kaynak == "yollar" else ([_bas(q) for q in _qi[ad_k][0]] if ad_k in _qi else None)
    if not pts:
        raise SystemExit("SEMA yolu bulunamadi: %s / %s (lale158/kablo_yolu_ekran.py)" % (kaynak, ad_k))
    boy = sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))
    SEMALAR.append(dict(ad=ad, kaynak="%s:%s" % (kaynak, ad_k), a=KOD_IDX[kod], renk=renk, boy_mm=round(boy),
                        pts=[[round(c, 1) for c in q] for q in pts]))
log("gosterim semasi: %d (kablo_yolu_ekran.py)" % len(SEMALAR))
# F10d: alt adımlı adımda her şema bir alt adımda (grup "sema" deseni şemanın görünen adında); hiçbir gruba düşmeyen son gruba + UYARI
for a in ADIMLAR:
    if not a.get("sira_grup"):
        continue
    kalan = {k for k, s in enumerate(SEMALAR) if s["a"] == a["i"]}
    for g in a["sira_grup"]:
        d = g.pop("_sema", ())
        g["sema"] = [k for k in sorted(kalan) if any(x in SEMALAR[k]["ad"] for x in d)]
        kalan -= set(g["sema"])
    if kalan and a.get("alt"):
        log("UYARI sema alt adimi yok:", a["kod"], sorted(kalan))
        a["sira_grup"][-1]["sema"] = sorted(set(a["sira_grup"][-1]["sema"]) | kalan)
    for g in a["sira_grup"]:
        if not g["sema"]:
            g.pop("sema")

VERI = dict(
    surum=1, uretim=time.strftime("%Y-%m-%d %H:%M"), betik="tasarim/freecad/rehber/rehber_veri.py",
    kaynak=dict(m6="planlama/adim4/M6-montaj-sirasi.md (adım sırası ve tablo metni)",
                secici="tasarim/freecad/rehber/rehber_secici.py (parça -> adım, 1,58 m)",
                sema="tasarim/freecad/lale158/kablo_yolu_ekran.py (gösterim şemaları; parça değil)",
                cad={m: time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(os.path.join(FC, f))))
                     for m, f in Y.DOSYA.items() if not m.endswith("_sol")}),
    koordinat="mm; +X sag, +Y yukari, +Z ileri (yuz)",
    m6_bayrak=dict(M6SAY), mesh=dict(benzersiz=len(MESH), parca=len(P), ucgen=sum(len(m[1]) for m in MESH),
                                     glb_mb=round(len(glb) / 1e6, 2)),
    atanmamis=ATANMAMIS, kablo_ad_uyari=KABLO_UYARI, tur_ad=RM.TUR_AD, modul_ad=RM.MODUL_AD, semalar=SEMALAR,
    # F10d düzeltme 1 (B-2): ısıl gömme ev sahibi (geometri) ve adım değiştiren somunlar; rehber_sira.py bağımsız denetler
    isil_gomme=dict(yontem=ISIL["yontem"], toplam=ISIL["toplam"], ev_sahipli=ISIL["ev_sahipli"], skor_alt=ISIL["skor_alt"],
                    evsiz=[dict(id=p["id"], ad=p["ad"], adim=p["kodr"]) for p in ISIL["evsiz"]],
                    tasinan=[dict(id=p["id"], ad=gorunen_ad(p), modul=p["modul"], eski_kod=k0, eski_adim=a0, kod=p["kodr"], adim=p["a"],
                                  ev=p["_h"]["id"], ev_ad=gorunen_ad(p["_h"])) for p, k0, a0 in ISIL["tasinan"]],
                    skor={p["id"]: p["_h_skor"] for p in P if p.get("_h_skor")}),
    adimlar=ADIMLAR, parcalar=PARCA)
js = json.dumps(VERI, ensure_ascii=False, separators=(",", ":"))
open(os.path.join(CIKTI, "rehber-veri.json"), "w", encoding="utf-8").write(json.dumps(VERI, ensure_ascii=False, indent=0))
open(os.path.join(CIKTI, "rehber-veri.js"), "w", encoding="utf-8").write("window.REHBER_VERI=" + js + ";\n")
for a in ADIMLAR:
    print("ADIM %2d %-4s %-22s parca %3d baglanti %3d m6 %s" % (
        a["i"], a["kod"], a["faz"], sum(x["adet"] for x in a["parcalar"]), sum(x["adet"] for x in a["baglantilar"]),
        ",".join("%s%d" % (m["kod"], m["adet"]) for m in a["m6"])))
log("bitti: %d adim" % len(ADIMLAR))
