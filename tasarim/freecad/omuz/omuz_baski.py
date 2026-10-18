# Sag omuz modulu - BASKI ANALIZI (duzeltme plani M4): 5 baski parcasi (sag + sol = 10 adet; sol X aynasi, sonuc ayni)
# Her parca icin 6 eksen yonu denenir: tablaya sigma, ilk katman temas alani, 45 derece ustu cikinti alani (mesh),
# katman katman destek analizi (kopru / konsol / ada; aciklik geometriden olculur), yuk eksenlerinin katmana gore yonu,
# isil gomme somun deliklerinin yonu. Secilen yonde PETG-CF dolulugu 0,8 / 0,9 ile kutle ve tahmini baski suresi.
# YALNIZ OKUR: omuz modulunu yeniden uretmez, geometriyi degistirmez.
#   Girdi (varsayilan): omuz-montaj.FCStd (Tur == "Baski" Part::Feature'lari). Dosya son 5 s icinde yazildiysa beklenir,
#   gecici kopyadan acilir, zip butunlugu denetlenir; dosya adi, degistirilme zamani ve sha256 sonuca yazilir.
#   OMUZ_BASKI_KAYNAK=parcalar -> omuz_parcalar.py import edilir (FCStd uretilmeden once denemek icin).
# Cikti: omuz-baski.json
# Calistir (yolda "u" oldugu icin ASCII baslaticiyla):
#   FC_SCRIPT=<bu dosya> "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
# Yontem diger modullerle ayni kural (kafa_lib.baski_analiz): onceki katmanin h kadar ofseti (45 derece) destek sayilir,
# 2 mm'den dar serit serbest, 15 mm'den uzun kopru destek ister. Fark: katman 0,5 mm; destekte kalan her bolge
# kopru (iki karsi kenardan tutunan), konsol (tek kenardan) ya da ada (altinda hic malzeme yok) diye ayrilir,
# aciklik ve konsol boyu bolge icindeki nokta orneklerinin tutunma kenarina uzakligindan olculur.
import os, sys, json, math, time, hashlib, shutil, tempfile, datetime, zipfile
import FreeCAD as App
import Part
import numpy as np
import MeshPart

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import arayuz as A

V = App.Vector
t0 = time.time()


def log(*a):
    print(*a, flush=True)


# ====================================================================== parametreler
KATMAN = 0.5          # mm, analiz katmani (45 derece kurali: katman basina KATMAN kadar tasma serbest)
Z0 = 0.23             # ilk kesit yuksekligi: tam/yarim mm yuzleri kesit duzlemiyle cakismasin
INCE = 1.0            # bu yari-genislikten (2 mm serit) dar bolge serbest (diger modullerle ayni)
KONSOL_SINIR = 1.0    # 45 derece payindan sonra kalan tek kenarli tasma bu boydan uzunsa destek (mm)
KOPRU_SINIR = 15.0    # bu acikliktan uzun kopru destek ister (diger modullerle ayni, tahmini)
KOPRU_UYARI = 10.0    # PETG-CF koprusunde sarkma riski bu acikliktan sonra (tahmini)
KARSI_COS = -0.5      # kopru icin karsi tutunma noktasi: en yakin tutunma yonune > 120 derece
DOLULUK = (0.80, 0.90)                      # duzeltme plani M4: PETG-CF parcalarda 0,8-0,9 (etkin doluluk, tahmini)
RHO = {"PETG-CF": 1.27, "PETG": A.PETG_RHO}  # g/cm3; PETG-CF 1,25-1,30 (baski-listesi, tahmini) -> 1,27
HIZ = A.PETG_HACIM_HIZI                      # 10 mm3/s ortalama debi (diger modullerle ayni, tahmini)
HIZ_CF = 7.0                                 # PETG-CF icin yavas senaryo (tahmini: ~%30 dusuk debi)
DESTEK_DOLULUK = 0.15                        # agac/izgara destek etkin dolulugu (tahmini)
YONLER = {"+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0), "-Y": (0, -1, 0), "+Z": (0, 0, 1), "-Z": (0, 0, -1)}
UX, UY, UZ = A.YAZICI["kullanilabilir"]

# baski listesindeki malzeme (planlama/baski-listesi.md, Malzeme bolumu). 15 Ekim 2026'dan beri FCStd'deki Malzeme alani da
# ayni (omuz_parcalar); tabloda olmayan parca (S1 kablo tamburu) modeldeki malzemeyle hesaplanir.
MALZEME = {"Omuz yuvasi": "PETG-CF", "Rulman kapagi": "PETG-CF", "Omuz gobegi": "PETG-CF", "Kol catali": "PETG-CF",
           "Ust kol tupu": "PETG", "S1 kablo tamburu": "PETG"}

# yuk eksenleri: geometriden (silindir yaricapi -> ekseni) ya da tasarimdan (robot ekseni). ister:
#   "dikey" = eksen tablaya dik: delik / yuva cevre cizgileriyle yuvarlak basilir, horn / rulman yuku katman duzleminde kalir
#   "yatay" = eksen katman duzleminde: egilme gerilmesi katmanlari kesmez
YUK = {
    "Omuz yuvasi": [
        dict(ad="manson + kollar: butun kolun momenti X boyunca egilme", eksen=(1, 0, 0), ister="yatay", w=2.0),
        dict(ad="S1 kulak M4 delikleri (servo tork tepkisi)", r=A.CLEAR[4] / 2, ister="dikey", w=1.0),
        dict(ad="kapak M3 isil gomme somunlari", r=A.INSERT_DELIK[3] / 2, ister="dikey", w=0.5)],
    "Rulman kapagi": [
        dict(ad="6808-2RS dis bilezik yuvasi O52 (siki gecme)", r=26.0, ister="dikey", w=2.0),
        dict(ad="kapak M3 civata delikleri", r=A.CLEAR[3] / 2, ister="dikey", w=0.5)],
    "Omuz gobegi": [
        dict(ad="6808 ic bilezik mili O40 (siki gecme)", r=20.0, ister="dikey", w=2.0),
        dict(ad="S1 horn M3 delikleri (kolun tum momenti)", r=A.CLEAR[3] / 2, ister="dikey", w=1.5),
        dict(ad="S2 kulak M4 delikleri", r=A.CLEAR[4] / 2, ister="dikey", w=1.0),
        dict(ad="625ZZ mafsal M5 isil gomme somunu", r=A.INSERT_DELIK[5] / 2, ister="dikey", w=1.0)],
    "Kol catali": [
        dict(ad="S2 horn M3 delikleri (kol torku)", r=A.CLEAR[3] / 2, ister="dikey", w=1.5),
        dict(ad="625ZZ yuvasi O16", r=8.0, ister="dikey", w=1.5),
        dict(ad="tup pimi O50,8 (tupe gecme, yuvarlaklik)", r=A.TUP_PIM_R, ister="dikey", w=1.0),
        dict(ad="tup M3 isil gomme somunlari", r=A.INSERT_DELIK[3] / 2, ister="dikey", w=0.5)],
    "Ust kol tupu": [
        dict(ad="tup ic capi O51,3 (pime gecme, yuvarlaklik)", r=A.TUP_PIM_R + A.GECME["tup_pim"], ister="dikey", w=1.0)],
    "S1 kablo tamburu": [   # S1 kablo kaseti (15 Ekim 2026): halka yuvarlak basilmali (kablo sarilir; kapak M3 basina 0,7 mm)
        dict(ad="tambur halkasi O78 (ic kosu sarilir, yuvarlaklik)", r=A.KOL_KABLO["s1"]["tambur"]["r"][1], ister="dikey", w=2.0),
        dict(ad="gobek M3 delikleri (3 kol)", r=A.CLEAR[3] / 2, ister="dikey", w=0.5)],
}
INSERT_R = {round(A.INSERT_DELIK[d] / 2, 3): "M%d" % d for d in A.INSERT_DELIK}


# ====================================================================== girdi
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def zaman(p):
    return datetime.datetime.fromtimestamp(os.stat(p).st_mtime).isoformat(timespec="seconds")


def fcstd_oku(yol):
    tmp = os.path.join(tempfile.gettempdir(), "omuz_baski_girdi.FCStd")
    son_hata = None
    for deneme in range(40):
        st1 = os.stat(yol)
        if time.time() - st1.st_mtime < 5:          # baska surec yaziyor olabilir
            time.sleep(5)
            continue
        shutil.copy2(yol, tmp)
        st2 = os.stat(yol)
        if (st2.st_mtime, st2.st_size) != (st1.st_mtime, st1.st_size):
            time.sleep(5)
            continue
        try:
            with zipfile.ZipFile(tmp) as z:
                if z.testzip() is not None:
                    raise IOError("zip bozuk")
            doc = App.openDocument(tmp)
        except Exception as e:
            son_hata = repr(e)
            time.sleep(5)
            continue
        parca = []
        for o in doc.Objects:
            if o.TypeId == "Part::Feature" and getattr(o, "Tur", "") == "Baski":
                s = o.Shape.copy()
                s.Placement = o.getGlobalPlacement()
                parca.append(dict(ad=o.Label, shape=s, model_malzeme=getattr(o, "Malzeme", ""),
                                  model_kutle_g=getattr(o, "Kutle_g", None)))
        App.closeDocument(doc.Name)
        bilgi = dict(dosya="omuz/omuz-montaj.FCStd", degistirilme=datetime.datetime.fromtimestamp(st1.st_mtime).isoformat(
            timespec="seconds"), boyut=st1.st_size, sha256=sha(tmp)[:16], deneme=deneme + 1)
        return parca, bilgi
    raise RuntimeError("FCStd okunamadi: %s" % son_hata)


def parcalar_oku():
    import omuz_parcalar as OP
    parca = [dict(ad=p["ad"], shape=p["shape"].copy(), model_malzeme=p["malzeme"], model_kutle_g=round(p["kutle"], 1))
             for p in OP.P if p["tur"] == "Baski"]
    yol = os.path.join(HERE, "omuz_parcalar.py")
    return parca, dict(dosya="omuz/omuz_parcalar.py", degistirilme=zaman(yol), boyut=os.stat(yol).st_size, sha256=sha(yol)[:16])


KAYNAK = os.environ.get("OMUZ_BASKI_KAYNAK", "fcstd")
if KAYNAK == "parcalar":
    PARCA, GIRDI = parcalar_oku()
else:
    PARCA, GIRDI = fcstd_oku(os.path.join(HERE, "omuz-montaj.FCStd"))
GIRDI["yontem"] = KAYNAK
_pp = os.path.join(HERE, "omuz_parcalar.py")
GIRDI["omuz_parcalar_py_degistirilme"] = zaman(_pp)
if KAYNAK != "parcalar" and os.stat(_pp).st_mtime > os.stat(os.path.join(HERE, "omuz-montaj.FCStd")).st_mtime:
    GIRDI["uyari"] = "omuz_parcalar.py FCStd'den yeni: model yeniden uretilmemis olabilir (omuz_montaj.py)"
log("girdi", GIRDI, "baski parcasi", len(PARCA), "%.1fs" % (time.time() - t0))


# ====================================================================== geometri yardimcilari
def silindirler(sh):
    """Silindirik yuzleri eksen cizgisi + yaricapa gore grupla (yarim silindirler birlesir)."""
    gr = []
    for f in sh.Faces:
        srf = f.Surface
        if "Cylinder" not in srf.TypeId:
            continue
        r, ax, c = srf.Radius, V(srf.Axis), V(srf.Center)
        ax.normalize()
        u0, u1, v0, v1 = f.ParameterRange
        um, vm = (u0 + u1) / 2, (v0 + v1) / 2
        p, n = f.valueAt(um, vm), f.normalAt(um, vm)
        rad = p - c - ax * (p - c).dot(ax)
        delik = rad.Length > 1e-9 and n.dot(rad) < 0
        ts = [(c + ax * v0 - c).dot(ax), (c + ax * v1 - c).dot(ax)]
        hit = None
        for g in gr:
            if abs(g["r"] - r) < 0.01 and abs(abs(g["ax"].dot(ax)) - 1) < 1e-6:
                d = c - g["c"]
                if (d - g["ax"] * d.dot(g["ax"])).Length < 0.01:
                    sgn = 1 if g["ax"].dot(ax) > 0 else -1
                    off = d.dot(g["ax"])
                    ts2 = [off + sgn * t for t in ts]
                    if min(ts2) <= g["t"][1] + 0.05 and max(ts2) >= g["t"][0] - 0.05:   # ayni eksende, eksenel olarak bitisik
                        hit = g
                        break
        if hit is None:
            gr.append(dict(r=r, ax=ax, c=c, delik=delik, t=[min(ts), max(ts)], alan=f.Area))
        else:
            hit["t"] = [min(hit["t"] + ts2), max(hit["t"] + ts2)]
            hit["alan"] += f.Area
    for g in gr:   # agiz: eksen ucunun hemen otesi bossa acik
        g["acik"] = []
        if g["delik"]:
            for t, sgn in ((g["t"][0], -1), (g["t"][1], 1)):
                q = g["c"] + g["ax"] * (t + sgn * 0.3)
                if not sh.isInside(q, 0.01, True):
                    g["acik"].append(sgn)
    return gr


def kesit(s, z):
    try:
        ws = s.slice(V(0, 0, 1), z)
        if not ws:
            return None
        f = Part.makeFace(ws, "Part::FaceMakerBullseye")
        return f if f.isValid() and f.Area > 1e-6 else None
    except Exception:
        return None


def ofset(face, d):
    """Yuz basina d kadar disa ofset. makeOffset2D'nin yonu yuzun normaline bagli (dondurulmus parcada ters
    cikabiliyor): iki isaret denenir, alani buyuyen alinir; kurulamazsa ofsetsiz yuz (tutucu)."""
    parca, uyari = [], 0
    for f in face.Faces:
        en = None
        for dd in (d, -d):
            try:
                o = f.makeOffset2D(dd, 0)
                if o.Area > f.Area + 1e-6 and (en is None or o.Area > en.Area):
                    en = o
            except Exception:
                pass
        if en is None:
            uyari += 1
        parca.append(en if en is not None else f)
    if not parca:
        return None, uyari
    s = parca[0]
    if len(parca) > 1:
        s = s.fuse(parca[1:])
    return s, uyari


def dar_mi(f):
    """Bolge 2*INCE'den dar mi: ice ofset (iki isaret denenir, kuculen alinir) bos kaliyorsa dar. Ofset kurulamazsa
    (OCC 'null' hatasi: halka gibi ince bolgelerde) genislik 2*alan/cevre ile tahmin edilir."""
    en = None
    for dd in (-INCE, INCE):
        try:
            a = sum(g.Area for g in f.makeOffset2D(dd, 0).Faces)
            if a < f.Area - 1e-6 and (en is None or a < en):
                en = a
        except Exception:
            pass
    if en is not None:
        return en < 0.01
    L = sum(w.Length for w in f.Wires)
    return 2 * f.Area / max(L, 1e-9) < 2 * INCE


def bolge_olc(f, dest, z):
    """Desteksiz kalan bolge f: tutunma kenarlari (dest sinirinda) ve icinden ornek noktalar ->
    konsol boyu (tek kenardan) ve kopru acikligi (karsi kenarlar arasi)."""
    anchors = []
    for e in f.Edges:
        try:
            m = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
            if dest is not None and dest.distToShape(Part.Vertex(m))[0] < 0.05:
                anchors += [(p.x, p.y) for p in e.discretize(Distance=0.2)]
        except Exception:
            pass
    bb = f.BoundBox
    adim = max(0.25, math.sqrt(f.Area / 3000.0))
    pts = []
    x = bb.XMin + adim / 2
    while x < bb.XMax:
        y = bb.YMin + adim / 2
        while y < bb.YMax:
            if f.isInside(V(x, y, z), 1e-4, True):
                pts.append((x, y))
            y += adim
        x += adim
    if not pts:
        c = f.CenterOfMass
        pts = [(c.x, c.y)]
    P_ = np.array(pts)
    if not anchors:
        return dict(tur="ada", konsol=None, kopru=None, nokta=len(pts), uc=tuple(P_[len(P_) // 2]))
    Q = np.array(anchors)
    D = P_[:, None, :] - Q[None, :, :]                       # nokta - tutunma
    dist = np.sqrt((D ** 2).sum(axis=2))
    i1 = dist.argmin(axis=1)
    d1 = dist[np.arange(len(P_)), i1]
    u = -D[np.arange(len(P_)), i1]                            # noktadan en yakin tutunmaya
    un = u / np.maximum(np.linalg.norm(u, axis=1)[:, None], 1e-9)
    vq = -D                                                   # noktadan her tutunmaya
    cosv = (vq * un[:, None, :]).sum(axis=2) / np.maximum(dist, 1e-9)
    karsi = np.where(cosv < KARSI_COS, dist, np.inf)
    d2 = karsi.min(axis=1)
    kopru_m = np.isfinite(d2)
    konsol = float(d1[~kopru_m].max()) if (~kopru_m).any() else 0.0
    kopru = float((d1 + np.where(kopru_m, d2, 0))[kopru_m].max()) if kopru_m.any() else 0.0
    tur = "kopru" if kopru_m.mean() > 0.5 else "konsol"
    return dict(tur=tur, konsol=round(konsol, 2), kopru=round(kopru, 2), nokta=len(pts), uc=tuple(P_[int(d1.argmax())]))


def katman_analizi(s, inv):
    """s: baski yonune cevrilmis, zmin = 0. Desteksiz kalan bolgeler ve kopruler."""
    zmax = s.BoundBox.ZMax
    kat = []          # (z, yuz) destek yuksekligi icin
    bolgeler, kopruler, uyari, atla = [], [], 0, []
    onceki = None
    k = 0
    while True:
        z = Z0 + k * KATMAN
        if z >= zmax:
            break
        yuz = kesit(s, z)
        if yuz is None:
            atla.append(round(z, 2))
        elif onceki is not None:
            dest, u_ = ofset(onceki, KATMAN)
            uyari += u_
            try:
                dest.translate(V(0, 0, KATMAN))
                acik = yuz.cut(dest)
            except Exception as e:
                acik = None
                bolgeler.append(dict(z=round(z, 2), hata=repr(e)[:80], destek=True, tur="hata"))
            if acik is not None:
                for f in acik.Faces:
                    if f.Area < 0.3:
                        continue
                    if dar_mi(f):
                        continue                              # 2 mm'den dar serit: 45 derece kurali icinde
                    m = bolge_olc(f, dest, z)
                    c = f.CenterOfMass
                    destek = m["tur"] == "ada" or (m["konsol"] or 0) > KONSOL_SINIR or (m["kopru"] or 0) > KOPRU_SINIR
                    # destek kolonu: bolgenin tutunmadan en uzak noktasindan alttaki ilk malzemeye ya da tablaya kadar
                    ux, uy = m["uc"]
                    h, tabla = z, True
                    for (zj, yj) in reversed(kat):
                        if yj is not None and yj.isInside(V(ux, uy, zj), 0.01, True):
                            h, tabla = z - zj, False
                            break
                    rc = inv.multVec(V(c.x, c.y, c.z))
                    r = dict(z=round(z, 2), tur=m["tur"], alan_mm2=round(f.Area, 1), konsol_mm=m["konsol"], kopru_mm=m["kopru"],
                             boyut=[round(f.BoundBox.XLength, 1), round(f.BoundBox.YLength, 1)],
                             merkez_robot=[round(rc.x, 1), round(rc.y, 1), round(rc.z, 1)], destek=destek,
                             kolon_mm=round(h, 1), tablaya=tabla, _bb=(f.BoundBox.XMin, f.BoundBox.XMax, f.BoundBox.YMin, f.BoundBox.YMax))
                    if destek:
                        bolgeler.append(r)
                    elif m["tur"] == "kopru" and m["kopru"] > 2.0:
                        kopruler.append(r)
        kat.append((z, yuz))
        onceki = yuz if yuz is not None else onceki
        k += 1
    return bolgeler, kopruler, uyari, atla, k


def kumele(bolgeler):
    """Ust uste binen (XY kutusu 1 mm buyutulmus, z araligi <= 2 katman) destek bolgelerini birlestir."""
    n = len(bolgeler)
    ana = list(range(n))

    def bul(i):
        while ana[i] != i:
            ana[i] = ana[ana[i]]
            i = ana[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            a, b = bolgeler[i], bolgeler[j]
            if "hata" in a or "hata" in b or abs(a["z"] - b["z"]) > 2 * KATMAN + 1e-6:
                continue
            A_, B_ = a["_bb"], b["_bb"]
            if A_[0] - 1 <= B_[1] and B_[0] - 1 <= A_[1] and A_[2] - 1 <= B_[3] and B_[2] - 1 <= A_[3]:
                ana[bul(i)] = bul(j)
    gr = {}
    for i in range(n):
        gr.setdefault(bul(i), []).append(bolgeler[i])
    out = []
    for g in gr.values():
        if any("hata" in b for b in g):
            out.append(dict(hata=[b.get("hata") for b in g if "hata" in b], z=[g[0]["z"]]))
            continue
        al = sum(b["alan_mm2"] for b in g)
        mx = [sum(b["merkez_robot"][i] * b["alan_mm2"] for b in g) / al for i in range(3)]
        out.append(dict(z_mm=[min(b["z"] for b in g), max(b["z"] for b in g)], katman=len(g), alan_mm2=round(al, 1),
                        turler=sorted(set(b["tur"] for b in g)),
                        konsol_max_mm=max([b["konsol_mm"] or 0 for b in g]), kopru_max_mm=max([b["kopru_mm"] or 0 for b in g]),
                        merkez_robot=[round(v, 1) for v in mx],
                        destek_hacim_mm3=round(sum(b["alan_mm2"] * b["kolon_mm"] for b in g), 0),
                        tablaya=all(b["tablaya"] for b in g)))
    out.sort(key=lambda b: -b.get("alan_mm2", 1e9))
    return out


EGIM_MIN_ALAN = 2.0     # mm2: bundan kucuk egimli cikinti (pah/kenar kirintisi) sayilmaz
KUCUK_DELIK_R = 5.0     # yatay delik O10'a kadar desteksiz basilir (yaygin uygulama, tahmini)


def egim_analizi(s, inv):
    """45 derece ustu egimli (yatay tavan haric) cikinti yuzleri. Yatay eksenli O10'a kadar delikler ayri sayilir."""
    lim = -math.cos(math.radians(45))
    out, kucuk = [], 0.0
    for f in s.Faces:
        srf = f.Surface
        try:
            pts, tris = f.tessellate(0.1)
        except Exception:
            continue
        if not tris:
            continue
        P_ = np.array([[p.x, p.y, p.z] for p in pts])
        T = np.array(tris)
        a, b, c = P_[T[:, 0]], P_[T[:, 1]], P_[T[:, 2]]
        ar = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
        cen = (a + b + c) / 3
        nz = np.empty(len(T))
        for i, q in enumerate(cen):
            try:
                u, v = f.Surface.parameter(V(*q))
                nz[i] = f.normalAt(u, v).z
            except Exception:
                nz[i] = 0.0
        m = (nz < lim) & (nz > -0.985) & (cen[:, 2] > 0.05)
        A_ = float(ar[m].sum())
        if A_ <= 0:
            continue
        if "Cylinder" in srf.TypeId and srf.Radius <= KUCUK_DELIK_R + 1e-6 and abs(V(srf.Axis).z) < 0.01:
            kucuk += A_
            continue
        if A_ < EGIM_MIN_ALAN:
            continue
        k = (cen[m] * ar[m][:, None]).sum(axis=0) / A_
        rc = inv.multVec(V(*k))
        out.append(dict(yuz=srf.TypeId.replace("Part::Geom", ""), alan_mm2=round(A_, 1),
                        izdusum_mm2=round(float((ar[m] * -nz[m]).sum()), 1),
                        en_dik_aci=round(90 - math.degrees(math.acos(min(1.0, float(-nz[m].min())))), 1),
                        z_mm=[round(float(cen[m][:, 2].min()), 1), round(float(cen[m][:, 2].max()), 1)],
                        merkez_robot=[round(rc.x, 1), round(rc.y, 1), round(rc.z, 1)],
                        yaricap=round(srf.Radius, 2) if hasattr(srf, "Radius") else None))
    out.sort(key=lambda e: -e["alan_mm2"])
    return out, kucuk


def yon_analizi(ad, sh, yukari, cyl):
    rot = App.Rotation(V(*yukari), V(0, 0, 1))
    s = sh.copy()
    s.transformShape(App.Placement(V(0, 0, 0), rot).toMatrix(), True)
    zmin = s.BoundBox.ZMin
    s.translate(V(0, 0, -zmin))
    inv = App.Placement(V(0, 0, 0), rot).inverse().multiply(App.Placement(V(0, 0, zmin), App.Rotation()))
    # tablaya yerlesim: Z etrafinda en dar kutu
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.2)
    pts, tris = mesh.Topology
    X = np.array([[p.x, p.y, p.z] for p in pts])
    Tn = np.array(tris)
    en = None
    for th in range(0, 91):
        c_, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        x = X[:, 0] * c_ - X[:, 1] * s_
        y = X[:, 0] * s_ + X[:, 1] * c_
        w, h = x.max() - x.min(), y.max() - y.min()
        w, h = max(w, h), min(w, h)
        if en is None or w * h < en[1] * en[2] - 1e-9:
            en = (th, w, h)
    H = s.BoundBox.ZMax
    sigar = en[1] <= UX and en[2] <= UY and H <= UZ
    # 45 derece ustu cikinti (tabla haric) ve yatay tavan
    a, b, c3 = X[Tn[:, 0]], X[Tn[:, 1]], X[Tn[:, 2]]
    cr = np.cross(b - a, c3 - a)
    alan = 0.5 * np.linalg.norm(cr, axis=1)
    nz = cr[:, 2] / np.maximum(2 * alan, 1e-12)
    zc = (a[:, 2] + b[:, 2] + c3[:, 2]) / 3
    tabla = zc < 0.05
    cik = (nz < -math.cos(math.radians(45))) & ~tabla
    tavan = (nz < -0.985) & ~tabla
    # ilk katman
    ilk = kesit(s, 0.1)
    ilk_alan = ilk.Area if ilk is not None else 0.0
    # egimli cikinti yuzleri (katman analizi yatay tavanlari ve tek katmanlik tasmalari yakalar; surekli dik egim her
    # katmanda 2 mm'den dar serit urettigi icin orada serbest kalir -> yuz yuz ayrica olculur)
    egim, kucuk_delik = egim_analizi(s, inv)
    egim_alan = sum(e["alan_mm2"] for e in egim)
    egim_izdusum = sum(e["izdusum_mm2"] for e in egim)
    # katmanlar
    bolgeler, kopruler, uyari, atla, nkat = katman_analizi(s, inv)
    kume = kumele(bolgeler)
    destek_alan = sum(b["alan_mm2"] for b in bolgeler if "alan_mm2" in b)
    destek_hacim = sum(b["alan_mm2"] * b["kolon_mm"] for b in bolgeler if "alan_mm2" in b)
    kopruler.sort(key=lambda r: -r["kopru_mm"])
    en_kopru = max([r["kopru_mm"] for r in kopruler] + [b.get("kopru_max_mm", 0) for b in kume if "hata" not in b] + [0])
    en_konsol = max([b.get("konsol_max_mm", 0) for b in kume if "hata" not in b] + [0])
    # yuk eksenleri ve isil gomme somunlar
    up = V(*yukari)
    yuk, w_top, w_ok = [], 0.0, 0.0
    for req in YUK.get(ad, []):
        if "eksen" in req:
            axes = [V(*req["eksen"])]
        else:
            axes = [g["ax"] for g in cyl if abs(g["r"] - req["r"]) < 0.02]
        if not axes:
            yuk.append(dict(ad=req["ad"], ister=req["ister"], bulundu=0, uyan=0))
            continue
        uy = sum(1 for ax in axes if (abs(ax.dot(up)) > 0.99 if req["ister"] == "dikey" else abs(ax.dot(up)) < 0.01))
        w_top += req["w"]
        w_ok += req["w"] * uy / len(axes)
        yuk.append(dict(ad=req["ad"], ister=req["ister"], bulundu=len(axes), uyan=uy, agirlik=req["w"]))
    uyum = w_ok / w_top if w_top else 1.0
    somun = []
    for g in cyl:
        key = round(g["r"], 3)
        if g["delik"] and key in INSERT_R:
            d = g["ax"].dot(up)
            if abs(d) > 0.99:
                agiz = []
                for sgn in g["acik"]:
                    agiz.append("yukari" if sgn * d > 0 else "asagi")
                yon = "dikey"
            elif abs(d) < 0.01:
                yon, agiz = "yatay", ["yan"] * len(g["acik"])
            else:
                yon, agiz = "egik", ["egik"] * len(g["acik"])
            somun.append(dict(boy=INSERT_R[key], merkez_robot=[round(v, 1) for v in (g["c"] + g["ax"] * sum(g["t"]) / 2)],
                              eksen_robot=[round(v, 3) for v in g["ax"]], yon=yon, agiz=agiz,
                              derinlik_mm=round(g["t"][1] - g["t"][0], 2)))
    bed_ax = "xyz"[[abs(v) for v in yukari].index(1)]
    bed_val = getattr(sh.BoundBox, ("%sMin" if sum(yukari) > 0 else "%sMax") % bed_ax.upper())
    for b in bolgeler:
        b.pop("_bb", None)
    for b in kopruler:
        b.pop("_bb", None)
    return dict(
        yukari=list(yukari), tabla_yuzu="%s = %.1f yuzu tablada (robot yerel %s%s yukari)" % (bed_ax, bed_val, "+" if sum(yukari) > 0 else "-", bed_ax.upper()),
        olcu=[round(en[1], 1), round(en[2], 1), round(H, 1)], tabla_aci=en[0], sigar=bool(sigar),
        cift_sigar=bool(2 * en[2] + 5 <= UY and en[1] <= UX and H <= UZ),
        ilk_katman_mm2=round(ilk_alan, 1), yukseklik_taban_orani=round(H / math.sqrt(max(ilk_alan, 1e-6)), 2),
        cikinti45_mm2=round(float(alan[cik].sum()), 1), tavan_mm2=round(float(alan[tavan].sum()), 1),
        cikinti45_orani=round(float(alan[cik].sum() / alan.sum()), 4),
        egim_yuz=egim, egim_alan_mm2=round(egim_alan, 1), egim_izdusum_mm2=round(egim_izdusum, 1), kucuk_delik_cikinti_mm2=round(kucuk_delik, 1),
        destek_gerekli=len(bolgeler) > 0 or len(egim) > 0, destek_alan_mm2=round(destek_alan + egim_izdusum, 1),
        destek_katman_alan_mm2=round(destek_alan, 1), destek_hacim_cm3=round(destek_hacim / 1000, 2),
        destek_bolge=kume, destek_bolge_sayi=len(kume), en_buyuk_kopru_mm=round(en_kopru, 1), en_buyuk_konsol_mm=round(en_konsol, 1),
        kopruler=kopruler[:8], yuk_uyum=round(uyum, 3), yuk=yuk, isil_gomme=somun,
        katman_sayisi=nkat, ofset_uyari=uyari, atlanan_kesit=atla[:10])


def yon_sec(sonuc):
    """Oncelik: tablaya sigma > yuk uyumu > destek alani > 45 derece cikinti alani > ilk katman alani (buyuk iyi)."""
    def anahtar(k):
        r = sonuc[k]
        return (0 if r["sigar"] else 1, -round(r["yuk_uyum"], 2), round(r["destek_alan_mm2"], 0), round(r["cikinti45_mm2"], 0),
                -r["ilk_katman_mm2"])
    sira = sorted(sonuc, key=anahtar)
    en_az = sorted(sonuc, key=lambda k: (0 if sonuc[k]["sigar"] else 1, round(sonuc[k]["destek_alan_mm2"], 0),
                                          -round(sonuc[k]["yuk_uyum"], 2), round(sonuc[k]["cikinti45_mm2"], 0)))
    return sira, en_az[0]


# ====================================================================== analiz
sonuclar = []
for p in PARCA:
    ad, sh = p["ad"], p["shape"]
    tp = time.time()
    cyl = silindirler(sh)
    yon = {}
    for k, y in YONLER.items():
        try:
            yon[k] = yon_analizi(ad, sh, y, cyl)
        except Exception as e:
            yon[k] = dict(hata=repr(e)[:200], sigar=False, yuk_uyum=0, destek_alan_mm2=1e9, cikinti45_mm2=1e9, ilk_katman_mm2=0)
        r = yon[k]
        log("  %-14s %s sigar=%s ilk=%.0f cik45=%.0f destek=%.0f mm2 (%d bolge) kopru=%.1f konsol=%.1f uyum=%.2f" % (
            ad, k, r.get("sigar"), r.get("ilk_katman_mm2", 0), r.get("cikinti45_mm2", 0), r.get("destek_alan_mm2", 0),
            r.get("destek_bolge_sayi", -1), r.get("en_buyuk_kopru_mm", -1), r.get("en_buyuk_konsol_mm", -1), r.get("yuk_uyum", 0)))
    sira, en_az = yon_sec(yon)
    sec = sira[0]
    mal = MALZEME.get(ad, p["model_malzeme"] if p["model_malzeme"] in RHO else "PETG")
    hac = sh.Volume
    rho = RHO[mal]
    dol = DOLULUK if mal == "PETG-CF" else (0.80,)
    kutle = {("%.2f" % d): round(hac / 1000 * rho * d, 1) for d in dol}
    dh = yon[sec]["destek_hacim_cm3"] * 1000 * DESTEK_DOLULUK
    sure = {("%.2f" % d): round((hac * d + dh) / HIZ / 3600, 2) for d in dol}
    sure_cf = {("%.2f" % d): round((hac * d + dh) / HIZ_CF / 3600, 2) for d in dol} if mal == "PETG-CF" else None
    sonuclar.append(dict(
        ad=ad, adet=2, adet_notu="sag + sol (sol = X aynasi; yon ve sonuc ayni, dilimleyicide aynalanir)",
        malzeme=mal, model_malzeme=p["model_malzeme"], model_kutle_g=p["model_kutle_g"],
        hacim_cm3=round(hac / 1000, 2), secilen_yon=sec, en_az_destek_yon=en_az, yon_sirasi=sira,
        desteksiz=not yon[sec]["destek_gerekli"], desteksiz_yon_var=[k for k in YONLER if not yon[k].get("destek_gerekli", True)],
        kutle_g=kutle, filament_g={k: round(v * 1.05 + dh / 1000 * rho, 1) for k, v in kutle.items()},
        destek_filament_g=round(dh / 1000 * rho, 1), sure_saat=sure, sure_saat_yavas_cf=sure_cf,
        silindir=[dict(r=round(g["r"], 3), delik=g["delik"], eksen=[round(v, 3) for v in g["ax"]], boy=round(g["t"][1] - g["t"][0], 2))
                  for g in cyl],
        yonler=yon))
    log("%-14s secilen %s (en az destek %s) desteksiz=%s  %.0fs" % (ad, sec, en_az, not yon[sec]["destek_gerekli"], time.time() - tp))

out = dict(
    tarih=datetime.datetime.now().isoformat(timespec="seconds"),
    betik="omuz/omuz_baski.py", girdi=GIRDI, yazici=dict(model=A.YAZICI["model"], kullanilabilir=list(A.YAZICI["kullanilabilir"]),
                                                          nozul="0,4 mm sertlestirilmis celik (baski-listesi; PETG-CF icin sart)"),
    parametreler=dict(katman_mm=KATMAN, aci_derece=45, ince_serit_mm=2 * INCE, konsol_sinir_mm=KONSOL_SINIR, kopru_sinir_mm=KOPRU_SINIR,
                      kopru_uyari_mm=KOPRU_UYARI, doluluk_petg_cf=list(DOLULUK), doluluk_petg=0.80, rho=RHO, hiz_mm3_s=HIZ,
                      hiz_cf_yavas_mm3_s=HIZ_CF, destek_doluluk=DESTEK_DOLULUK,
                      secim="sigma > yuk uyumu (agirlikli) > destek alani > 45 derece cikinti > ilk katman",
                      notlar="kutle/sure tahmini; filament = kutle x 1,05 + destek. Destek hacmi = alan x alttaki malzemeye/tablaya kolon boyu"),
    parcalar=sonuclar,
    ozet=dict(parca_turu=len(sonuclar), adet=2 * len(sonuclar),
              desteksiz_tur=[s["ad"] for s in sonuclar if s["desteksiz"]],
              destekli_tur=[s["ad"] for s in sonuclar if not s["desteksiz"]],
              desteksiz_iddia_tutmayan_adet=2 * sum(1 for s in sonuclar if not s["desteksiz"]),
              kutle_toplam_g={d: round(2 * sum(s["kutle_g"].get(d, s["kutle_g"].get("0.80", 0)) for s in sonuclar), 0) for d in ("0.80", "0.90")},
              sure_toplam_saat={d: round(2 * sum(s["sure_saat"].get(d, s["sure_saat"].get("0.80", 0)) for s in sonuclar), 1) for d in ("0.80", "0.90")}),
    sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "omuz-baski.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("--- ozet")
for s in sonuclar:
    r = s["yonler"][s["secilen_yon"]]
    log("%-14s %-7s yon %s olcu %s ilk %.0f mm2 desteksiz=%s destek %.0f mm2 kopru %.1f konsol %.1f kutle %s sure %s" % (
        s["ad"], s["malzeme"], s["secilen_yon"], r["olcu"], r["ilk_katman_mm2"], s["desteksiz"], r["destek_alan_mm2"],
        r["en_buyuk_kopru_mm"], r["en_buyuk_konsol_mm"], s["kutle_g"], s["sure_saat"]))
log("bitti %.1fs" % (time.time() - t0))
