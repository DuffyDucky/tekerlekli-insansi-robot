# 3B montaj rehberi, A: adım verisi + hafif mesh. CAD'i YALNIZ OKUR (modül FCStd'leri), hiçbir CAD dosyasına yazmaz.
# Çalıştırma (README başlatıcısı; tek komut için rehber_uret.py bunu çağırır):
#   FC_SCRIPT=<bu dosya> "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
# Çıktı (Robot/rehber/veri/):
#   rehber-veri.json  adımlar (M6 tablosu + rehber_metin.py), parçalar (adım, alt montaj, uçuş yönü, bayrak), mesh düğüm adları
#   robot.glb         tüm parçalar; aynı geometri tek mesh, parça başına bir düğüm (ad = parça kimliği "p0001")
#   robot-glb.js      aynı GLB base64 (file:// altında fetch çalışmadığı için <script> ile yüklenir)
#   rehber-veri.js    aynı JSON (window.REHBER_VERI)
#
# Yöntem
# - Adım ataması: planlama/adim4/M6_erisim.py içindeki ADIMLAR seçicileri (dosyanın "yukle" işaretine kadarki kısmı exec edilir).
#   İç kod -> rehber kodu: E4a -> E4; kafa "Yanak-horn" cıvataları E3a -> E3 (M6 tablosunda E3 ayrı adım).
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


# ------------------------------------------------------------------ M6 adım seçicileri (tek kaynak)
_m6 = os.path.join(ADIM4, "M6_erisim.py")
_src = open(_m6, encoding="utf-8").read().split("# ---------------------------------------------------------------- yukle")[0]
NS = {"__file__": _m6, "__name__": "m6_secici"}
exec(compile(_src, _m6, "exec"), NS)
Y = NS["Y"]
IC_ADIM = {a[0]: (a[1], a[4]) for a in NS["ADIMLAR"]}         # ic no -> (kod, tezgah)


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
TEZGAH_KOD = {kod: tz for _no, (kod, tz) in IC_ADIM.items() if tz}
TEZGAH_KOD.pop("E4a", None)
BAGLANIR = {"plaka": "B1", "guc": "B5", "kat": "B6", "omuz": "D1", "boyun": "E1", "kafa": "E3", "gobek": "G1", "dirsek": "H1"}


def rehber_kodu(p, ic_no):
    kod = IC_ADIM[ic_no][0]
    if kod == "E4a":
        return "E4"
    if kod == "E3a" and "Yanak-horn" in p["ad"]:
        return "E3"
    return kod


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


for p in P:
    if p["tur"] == "Referans":
        if p["modul"] == "taban" and p["ad"].startswith("Kablo yolu"):
            p["kodr"], p["kablo"] = "K1", True
        elif p["modul"] == "kafa":
            p["kodr"], p["kablo"] = "E3a", True
        else:
            p["kodr"] = "F1"                                       # ana anahtar düğmesi gösterimi (etek deliği K7)
        continue
    ic = NS["adim_bul"](p)
    if ic not in IC_ADIM or IC_ADIM[ic][0] == "X":
        log("UYARI atanamadi:", p["ad"], p["modul"])
        p["kodr"] = "F5"
        continue
    p["kodr"] = rehber_kodu(p, ic)
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
M6SAY = collections.Counter(p.get("m6") for p in P if p.get("m6"))
log("M6 bayragi:", dict(M6SAY), sum(M6SAY.values()))


# ------------------------------------------------------------------ uçuş yönü
def birim(v):
    v = V(*v) if not isinstance(v, App.Vector) else V(v)
    return v.normalize() if v.Length > 1e-9 else V(0, 1, 0)


def ayna_x(v, p):
    return V(-v.x, v.y, v.z) if p["modul"].endswith("_sol") else v


def radyal(p):
    c = p["shape"].BoundBox.Center
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
for p in P:
    bbx = p["shape"].BoundBox
    diag = bbx.DiagonalLength
    kod = p["kodr"]
    u, dist = None, max(40.0, 1.1 * diag)
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


def tr(ad):
    return re.sub(r"[A-Za-z]+", lambda m: RM.TR.get(m.group(0), m.group(0)), ad)


def temiz_ad(ad):
    a = re.sub(r"\s*\((?:[^()]|\([^()]*\))*\)\s*$", "", ad)
    a = re.sub(r"(\D)\d{3}$", r"\1", a).strip()
    return a or ad


PARCA = []
for p in P:
    d = dict(id=p["id"], ad=tr(p["ad"]), modul=p["modul"], grup=p["grup"], kod=p["kod"], tur=p["tur"], malzeme=p["malzeme"],
             r=renk_sinifi(p), a=p["a"], b=p["b"], t=p["t"], u=p["ucus"], d=p["ucus_mm"])
    if p.get("ucus_bag"):
        d["ub"] = p["ucus_bag"]
    if p.get("m6"):
        d["m6"] = p["m6"]
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
    for p in ps:
        if p["tur"] == "Referans":
            continue
        if p["tur"] == "Baglanti":
            k = p["kod"]
            e = bag.setdefault(k, dict(kod=k, adet=0, m6=0))
            e["adet"] += 1
            e["m6"] += 1 if p.get("m6") else 0
        else:
            k = (p["kod"], p["tur"], renk_sinifi(p))
            e = parca.setdefault(k, dict(ad=p["ad"], kod=p["kod"], tur=p["tur"], malzeme=p["malzeme"], r=k[2], adet=0))
            e["adet"] += 1
            if e["adet"] > 1:
                e["ad"] = temiz_ad(e["ad"])
    for e in parca.values():
        e["ad"] = tr(e["ad"])
    nciv = sum(1 for p in ps if civata_mi(p))
    nsom = sum(1 for p in ps if p["tur"] == "Baglanti" and not civata_mi(p))
    sure = mt.get("sure_dk") or int(round(5 + 1.0 * nciv + 0.3 * nsom + 0.8 * sum(e["adet"] for e in parca.values())))
    m6not = sorted(set(p["m6"] for p in ps if p.get("m6")))
    ADIMLAR.append(dict(
        i=i, kod=kod, no=r["no"], faz=faz(kod), baslik=mt.get("baslik") or r["is_"].split(":")[0][:60],
        is_=r["is_"], baglanti_md=r["baglanti"], alet=r["alet"], erisim=r["erisim"], tezgah=TEZGAH_KOD.get(kod),
        baglanir=KOD_IDX[BAGLANIR[TEZGAH_KOD[kod]]] if TEZGAH_KOD.get(kod) else None,
        parcalar=list(parca.values()), baglantilar=list(bag.values()),
        kontrol=mt.get("kontrol", []), kablo=mt.get("kablo", []), not_=mt.get("not_", []),
        m6=[dict(kod=k, not_=RM.M6_CAD_NOT[k], adet=sum(1 for p in ps if p.get("m6") == k)) for k in m6not],
        sure_dk=sure, sure_tahmini=not mt.get("sure_dk"),
        kablolama=kod in ("K1", "K2")))

VERI = dict(
    surum=1, uretim=time.strftime("%Y-%m-%d %H:%M"), betik="tasarim/freecad/rehber/rehber_veri.py",
    kaynak=dict(m6="planlama/adim4/M6-montaj-sirasi.md + M6_erisim.py (ADIMLAR) + M6_erisim_sonuc.json",
                cad={m: time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(os.path.join(FC, f))))
                     for m, f in Y.DOSYA.items() if not m.endswith("_sol")}),
    koordinat="mm; +X sag, +Y yukari, +Z ileri (yuz)",
    m6_bayrak=dict(M6SAY), mesh=dict(benzersiz=len(MESH), parca=len(P), ucgen=sum(len(m[1]) for m in MESH),
                                     glb_mb=round(len(glb) / 1e6, 2)),
    adimlar=ADIMLAR, parcalar=PARCA)
js = json.dumps(VERI, ensure_ascii=False, separators=(",", ":"))
open(os.path.join(CIKTI, "rehber-veri.json"), "w", encoding="utf-8").write(json.dumps(VERI, ensure_ascii=False, indent=0))
open(os.path.join(CIKTI, "rehber-veri.js"), "w", encoding="utf-8").write("window.REHBER_VERI=" + js + ";\n")
for a in ADIMLAR:
    print("ADIM %2d %-4s %-22s parca %3d baglanti %3d m6 %s" % (
        a["i"], a["kod"], a["faz"], sum(x["adet"] for x in a["parcalar"]), sum(x["adet"] for x in a["baglantilar"]),
        ",".join("%s%d" % (m["kod"], m["adet"]) for m in a["m6"])))
log("bitti: %d adim" % len(ADIMLAR))
