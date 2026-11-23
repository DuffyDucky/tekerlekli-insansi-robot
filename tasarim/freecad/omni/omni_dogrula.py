# On omni - 2. asama BAGIMSIZ dogrulama (freecadcmd). 1. asamanin omni_kontrol.py'sini kullanmaz; taban_parcalar'i dogrudan okur.
# FC_SCRIPT=<bu dosya> freecadcmd run_fc.py                      -> omni-dogrula.json      (omni kipi)
# OMNI_KIP=lastik FC_SCRIPT=<bu dosya> freecadcmd run_fc.py      -> omni-dogrula-lastik.json (TABAN_OMNI=0 geri donusu)
# Olcer: (1) taban parcalarinin omni oncesi taban-analiz.json (git ONCE_REF, omni oncesi son commit) ile ad + tekrar sirasina gore
# karsilastirmasi (hacim, sinir kutusu, kutle); (2) x zinciri dogrudan sekillerden; (3) donen grup (TEKER_DONEN, kaplin haric)
# eksen etrafinda 0..345 derece (15 derece) dondurulerek statik komsulara distToShape + cakisma (0,5 mm3); (4) omni baglanti sayisi.
import os, sys, json, math, time, subprocess, collections
KIP = os.environ.get("OMNI_KIP", "")
if KIP == "lastik":
    os.environ["TABAN_OMNI"] = "0"
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)
for p in (R, os.path.join(R, "taban")):
    if p not in sys.path:
        sys.path.insert(0, p)
ONCE_REF = os.environ.get("ONCE_REF", "4bc73de")      # origin/lale-duzeltme, omni CAD'inden onceki son commit
import FreeCAD as App
import Part
import arayuz as A
import taban_parcalar as TP
import taban_lib as L
V = App.Vector
t0 = time.time()
P = TP.P
_k = subprocess.run(["git", "show", "%s:tasarim/freecad/taban/taban-analiz.json" % ONCE_REF], cwd=R, capture_output=True)
once = json.loads(_k.stdout.decode("utf-8"))
_say = collections.Counter()
OP = {}
for p in once["parcalar"]:
    OP[(p["ad"], _say[p["ad"]])] = p
    _say[p["ad"]] += 1
out = dict(kip=KIP or "omni", once_ref=ONCE_REF, omni=TP.OMNI, parca=len(P), gercek=sum(1 for p in P if p["tur"] != "Referans"), baglanti=len(TP.BAG),
           kutle=round(sum(p["kutle"] for p in P if p["tur"] != "Referans"), 2))


def bbl(b):
    return [round(x, 2) for x in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)]


# 1) omni oncesi taban analizine gore parca karsilastirmasi (ayni adli parcalar tekrar sirasiyla eslesir)
yeni, fark, ayni = [], [], 0
_s2 = collections.Counter()
GORULEN = set()
for p in P:
    key = (p["ad"], _s2[p["ad"]])
    _s2[p["ad"]] += 1
    GORULEN.add(key)
    o = OP.get(key)
    if o is None:
        yeni.append(p["ad"])
        continue
    f = []
    if abs(o["hacim_mm3"] - p["hacim"]) > 0.15:
        f.append("hacim %.1f -> %.1f" % (o["hacim_mm3"], p["hacim"]))
    if max(abs(a - b) for a, b in zip(o["bb"], bbl(p["bb"]))) > 0.011:
        f.append("bb %s -> %s" % (o["bb"], bbl(p["bb"])))
    if abs(o["kutle_g"] - p["kutle"]) > 0.011:
        f.append("kutle %.2f -> %.2f" % (o["kutle_g"], p["kutle"]))
    if f:
        fark.append((p["ad"], f))
    else:
        ayni += 1
yok = [k[0] for k in OP if k not in GORULEN]
out["once_karsilastirma"] = dict(ayni=ayni, yeni=yeni, farkli=fark, kalkan=yok, once_parca=len(OP))
print("once: ayni", ayni, "yeni", len(yeni), "farkli", len(fark), "kalkan", yok, flush=True)

if TP.OMNI:
    # 2) x zinciri dogrudan sekillerden
    IDX = {p["ad"]: k for k, p in enumerate(P)}
    k = "on sag"
    bb = lambda ad: P[IDX[ad]]["shape"].BoundBox
    om, ad_, kap, mot, br = (bb("Omni teker 127 x 29 (%s)" % k), bb("Omni gobek adaptoru (%s)" % k), bb("Kaplin 12 mm altigen (%s)" % k),
                             bb("Motor JGB37-520 (%s)" % k), bb("Motor braketi L 37 mm (%s)" % k))
    arka = bb("Teker 125 x 58 (arka sag)")
    out["x_zinciri"] = dict(braket_x=[round(br.XMin, 3), round(br.XMax, 3)], kaplin_x=[round(kap.XMin, 3), round(kap.XMax, 3)],
                            adaptor_x=[round(ad_.XMin, 3), round(ad_.XMax, 3)], omni_x=[round(om.XMin, 3), round(om.XMax, 3)],
                            omni_merkez=round((om.XMin + om.XMax) / 2, 3), omni_cap_y=round(om.YLength, 3), omni_cap_z=round(om.ZLength, 3),
                            omni_alt_y=round(om.YMin, 3), arka_merkez=round((arka.XMin + arka.XMax) / 2, 3), arka_alt_y=round(arka.YMin, 3),
                            arayuz_OMNI_X=A.OMNI_X, ON_IZ=A.ON_IZ, ARKA_IZ=A.ARKA_IZ,
                            kaplin_adaptor_kavrama=round(kap.XMax - ad_.XMin, 3))
    print("x", out["x_zinciri"], flush=True)
    # 3) donen grup: TEKER_DONEN (kaplin haric) eksen etrafinda 0..360 (7,5 derece) dondurulur, statik komsulara distToShape
    for key in [(1, 1), (1, -1)]:
        sx, sz = key
        don = TP.TEKER_DONEN[key]
        kap_i = TP.OMNI_I[key]["kaplin"] if key in TP.OMNI_I else None
        grup = [P[i]["shape"] for i in don if i != kap_i]
        merkez = V(sx * (A.OMNI_X if key in TP.OMNI_I else A._X_WH), A.AX, sz * TP.Z_WH)
        gbb = App.BoundBox(Part.makeCompound(grup).BoundBox)
        gbb.enlarge(70)
        statik = [(p["ad"], p["shape"]) for j, p in enumerate(P) if p["tur"] != "Referans" and j not in don and p["bb"].intersect(gbb)]
        en = {}
        cak = []
        for a in [x * 15.0 for x in range(24)]:
            rot = App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), a), merkez)
            g2 = Part.makeCompound([s.copy() for s in grup])
            g2.Placement = rot.multiply(g2.Placement)
            for n, s in statik:
                d = g2.distToShape(s)[0]
                if n not in en or d < en[n][0]:
                    en[n] = (d, a)
                if d < 1e-6:
                    try:
                        v = g2.common(s).Volume
                    except Exception:
                        v = -1
                    if v > 0.5 or v < 0:
                        cak.append((n, a, round(v, 3)))
        sira = sorted(en.items(), key=lambda kv: kv[1][0])[:8]
        out.setdefault("donen", {})["%+d%+d" % key] = dict(statik_aday=len(statik), aci_adim=15.0, cakisma=cak,
                                                         en_yakin=[(n, round(d, 3), a) for n, (d, a) in sira])
        print("donen", key, "cakisma", len(cak), [(n[:30], round(d, 2)) for n, (d, a) in sira[:6]], "%.0fs" % (time.time() - t0), flush=True)
    # 4) baglantilar: on koselerin omni baglantilari
    ob = [b["ad"] for b in TP.BAG if b["ad"].startswith("Omni")]
    out["omni_baglanti"] = dict(sayi=len(ob), adlar=ob)
    # 5) TEKER_DONEN icerigi
    out["teker_donen"] = {"%+d%+d" % k: [P[i]["ad"] for i in v] for k, v in TP.TEKER_DONEN.items()}
out["sure_s"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(HERE, "omni-dogrula-lastik.json" if KIP == "lastik" else "omni-dogrula.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=str)
print("bitti %.0fs" % (time.time() - t0), flush=True)
