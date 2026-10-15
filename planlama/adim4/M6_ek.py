# M6 ek olcumler (YALNIZ OKUR): (1) etek arkasi sigorta / servis kapagi yer kontrolu, (2) S1 kaseti + O84 halka: kaset
# civatalarinin S1 -45 / 0 / +45'te erisimi, ped yarigi ile O84 arasindaki et, (3) gobek-horn civatalarinin onundeki engel.
# Cikti: planlama/adim4/M6_ek_sonuc.json
import os, sys, math, json
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m6_yukle as Y

A = Y.A
V = App.Vector
P = [p for p in Y.yukle() if p["tur"] != "Referans"]
for p in P:
    p["sbb"] = p["shape"].BoundBox
S = dict()


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def carpan(sh, haric=()):
    bb = sh.BoundBox
    out = []
    for p in P:
        if p["ad"] in haric or not p["sbb"].intersect(bb):
            continue
        v = sh.common(p["shape"]).Volume
        if v > 0.01:
            out.append((p["ad"] + " [" + p["modul"] + "]", round(v, 1)))
    return out


def en_yakin(sh, n=4, haric=()):
    d = []
    for p in P:
        if p["ad"] in haric:
            continue
        bb = p["sbb"]
        if bb.XMin > sh.BoundBox.XMax + 30 or bb.XMax < sh.BoundBox.XMin - 30 or bb.ZMin > sh.BoundBox.ZMax + 30 or \
                bb.ZMax < sh.BoundBox.ZMin - 30 or bb.YMin > sh.BoundBox.YMax + 30 or bb.YMax < sh.BoundBox.YMin - 30:
            continue
        d.append((round(sh.distToShape(p["shape"])[0], 1), p["ad"] + " [" + p["modul"] + "]"))
    return sorted(d)[:n]


# ---------------------------------------------------------------- (1) etek arkasi kapaklar
etek = [p for p in P if p["ad"].startswith("Etek arka")]
yp = max(p["sbb"].YMax for p in etek)
S["etek_ust_y"] = round(yp, 2)
KAP = dict(
    H1=dict(ad="sigorta + servis kapagi", delik=(-44.0, 36.0, -230.0, -175.0), pay=6.0),
    H2=dict(ad="ana sigorta kapagi (yedek secenek)", delik=(94.0, 130.0, -160.0, -100.0), pay=5.0),
)
for k, h in KAP.items():
    x0, x1, z0, z1 = h["delik"]
    pay = h["pay"]
    delik = box(x0, x1, yp - 6.0, yp + 0.1, z0, z1)
    kapak = box(x0 - pay, x1 + pay, yp, yp + 3.0, z0 - pay, z1 + pay)                 # 3 mm kapak, plakanin ustunde
    alti = box(x0, x1, 175.0, yp - 3.0, z0, z1)                                      # delik altindaki hacim (el / pense yolu)
    # delik plakanin tamamen icinde mi: delik kutusu etek parcalarinin plaka bolgesiyle kesisimi ~ tam alan x 3 mm olmali
    plaka_kes = sum(delik.common(p["shape"]).Volume for p in etek)
    h.update(plaka_kesilen_mm3=round(plaka_kes, 0), plaka_tam_mm3=round((x1 - x0) * (z1 - z0) * 3.0, 0),
             kapak_carpan=carpan(kapak, haric=[p["ad"] for p in etek]),
             kapak_en_yakin=en_yakin(kapak, 4, haric=[p["ad"] for p in etek]),
             delik_alti_carpan=carpan(alti, haric=[p["ad"] for p in etek]))
    S[k] = h
print("etek:", json.dumps(S, ensure_ascii=False)[:1500])

# ---------------------------------------------------------------- (2) S1 kaseti, O84 ve ped yarigi
kaset = [p for p in P if "aset" in p["ad"]]
S["kaset_parcalari"] = [(p["ad"], p["modul"], [round(v, 1) for v in (p["sbb"].XMin, p["sbb"].XMax, p["sbb"].YMin, p["sbb"].YMax,
                                                                   p["sbb"].ZMin, p["sbb"].ZMax)]) for p in kaset]
bant = [p for p in P if p["ad"] == "Omuz bandi sag"][0]
# ped duzleminde (x 149,5) psi taramasi: r 40...62 boyunca malzeme var mi (yarik ve O84 nerede)
S1 = A.KOL_KABLO["s1"]
psi_c = S1["cikis"]["psi"]


def psi_nokta(psi, r, x=149.5):
    y = A.S3 + r * math.cos(math.radians(psi))
    z = -r * math.sin(math.radians(psi))
    return V(x, y, z)


prof = {}
for psi in (psi_c - 12, psi_c - 6, psi_c - 3, psi_c, psi_c + 3, psi_c + 6, psi_c + 12):
    dolu = [r for r in [40 + 0.5 * i for i in range(45)] if bant["shape"].isInside(psi_nokta(psi, r), 0.01, True)]
    prof[str(psi)] = [min(dolu), max(dolu)] if dolu else None
S["ped_psi_r_dolu"] = prof
# yarik: psi_c'de dolu olmayan r araligi
r_bos = [40 + 0.5 * i for i in range(45) if not bant["shape"].isInside(psi_nokta(psi_c, 40 + 0.5 * i), 0.01, True)]
S["yarik_psi_c_bos_r"] = r_bos[:3] + ["..."] + r_bos[-3:] if r_bos else []

# kaset civatalari: omuz Gobek + Kol + dirsek gruplari S1 ekseni etrafinda dondurulunce erisim (alyan 2,5, r 2,05)
civ = [p for p in P if p["ad"].startswith("Kaset civatasi") and "sag" in p["ad"]]
hareketli = [p for p in P if p["modul"] in ("omuz_sag", "dirsek_sag") and not p["grup"].startswith("Govde_sabit")]
sabit = [p for p in P if p not in hareketli]


def eksen(s):
    cyl = [f for f in s.Faces if f.Surface.TypeId == "Part::GeomCylinder"]
    f = min(cyl, key=lambda f: (f.Surface.Radius, -f.Area))
    u = V(f.Surface.Axis).normalize()
    c = V(f.Surface.Center)
    ts = [(v.Point - c).dot(u) for v in s.Vertexes]
    t0, t1 = min(ts), max(ts)

    def uc(tu):
        pts = [v.Point for v in s.Vertexes if abs((v.Point - c).dot(u) - tu) < 0.6]
        rr = [((q - c) - u * (q - c).dot(u)).Length for q in pts]
        return (max(rr) if rr else 0.0), len(pts)

    r0, n0 = uc(t0)
    r1, n1 = uc(t1)
    if (r1 > r0 + 0.1) or (abs(r1 - r0) <= 0.1 and n1 > n0):
        return c + u * t1, u
    return c + u * t0, u * -1


S["kaset_civata_erisim"] = []
for phi in (-45.0, 0.0, 45.0, 90.0):
    rot = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), -phi), V(0, A.S3, 0))   # S1 +phi psi yi arttirir = X etrafinda -phi
    eng = [dict(ad=p["ad"], shape=p["shape"]) for p in sabit if p not in civ]
    for p in hareketli:
        s = p["shape"].copy()
        s.Placement = rot.multiply(s.Placement)
        eng.append(dict(ad=p["ad"] + "@" + str(phi), shape=s))
    for c in civ:
        p0, u = eksen(c["shape"])
        cy = Part.makeCylinder(2.05, 110.0, p0 + u * 0.15, u)
        best, kim = 110.0, None
        for e in eng:
            if not e["shape"].BoundBox.intersect(cy.BoundBox):
                continue
            cm = cy.common(e["shape"])
            if cm.Volume > 1e-3:
                t = min((v.Point - p0).dot(u) for v in cm.Vertexes) if cm.Vertexes else 0.0
                if t < best:
                    best, kim = t, e["ad"]
        S["kaset_civata_erisim"].append(dict(phi=phi, civata=c["ad"], eksen=[round(u.x, 2), round(u.y, 2), round(u.z, 2)],
                                             serbest_mm=round(best, 1), engel=kim))
print("kaset:", S["kaset_civata_erisim"])

# ---------------------------------------------------------------- (3) gobek-horn civatalari: onundeki engel (yalniz gobek)
gob = [p for p in P if p["ad"] == "Omuz gobegi" and p["modul"] == "omuz_sag"][0]
S["gobek_horn"] = []
for c in [p for p in P if p["ad"].startswith("Gobek-horn") and p["modul"] == "omuz_sag"]:
    p0, u = eksen(c["shape"])
    cy = Part.makeCylinder(2.05, 60.0, p0 + u * 0.15, u)
    cm = cy.common(gob["shape"])
    if cm.Volume > 1e-3:
        bb = cm.BoundBox
        S["gobek_horn"].append(dict(civata=c["ad"], bas=[round(p0.x, 1), round(p0.y, 1), round(p0.z, 1)],
                                    engel_x=[round(bb.XMin, 1), round(bb.XMax, 1)], hacim=round(cm.Volume, 1)))
    else:
        S["gobek_horn"].append(dict(civata=c["ad"], bas=[round(p0.x, 1), round(p0.y, 1), round(p0.z, 1)], engel_x=None))
print("gobek:", S["gobek_horn"])
with open(os.path.join(HERE, "M6_ek_sonuc.json"), "w", encoding="utf-8") as f:
    json.dump(S, f, ensure_ascii=False, indent=1)
print("bitti")
