# P10.8d ölçüm betiği (FreeCAD 1.1; FC_SCRIPT=<bu dosya> freecadcmd run_fc.py). Modele dokunmaz; yalnız P108d-olcum/<etiket>.json yazar.
# Etiket: ortam P108D_ETIKET (varsayılan "olcum"); değişiklikten önce "once", sonra "sonra".
# Parçalar: taban = taban_parcalar.py (içe aktarılır, güncel kaynak); öbür modüller = montaj/robot-montaj.FCStd (Modul != taban,
# Tur != Referans; ev pozu, global). Bölümler:
#   yol     : taban CAD kablo yolları 1-12 (Referans tüp r 2,5) x gerçek parçalar: en dar yabancı, izinli temas, yabancıyla ortak hacim
#   gecis   : her yolun alt plaka / kat orta düzlemi geçişi (kablo_yolu_taban.gecis_denetle kuralı: Ø16 delik, ön kat kesiği, akü yarığı)
#   oturma  : güç panelindeki kart burçlarının panel üstüne, alt vida başlarının panel altına oturma alanı (F10b-olcum.py yöntemi)
#   alt_bas : güç paneli altındaki vida başları x akü / akü kayışı en dar boşluk
#   yeni    : adı NOT_YENI ile başlayan parçalar (P10.8d kartları) x kablo yolları
#   sema    : P108d-olcum/sema-girdi.json'daki 16 gösterim şeması (eksen çizgisi) x gerçek parçalar
import os, sys, json, re, time, math
HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
FC = os.path.join(ROBOT, "tasarim", "freecad")
for p in (os.path.join(FC, "taban"), FC, os.path.join(FC, "lale158")):
    if p not in sys.path:
        sys.path.insert(0, p)
import FreeCAD as App
import Part
t0 = time.time()
V = App.Vector
ETIKET = os.environ.get("P108D_ETIKET", "olcum")
CIKTI = os.path.join(HERE, "P108d-olcum")
os.makedirs(CIKTI, exist_ok=True)


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


def ascii_(s):
    return s.encode("ascii", "replace").decode("ascii")


import arayuz as A
import taban_parcalar as TP
import kablo_yolu_taban as KYT
log("taban", len(TP.P))

PRC = []
for p in TP.P:
    PRC.append(dict(ad=p["ad"], modul="taban", tur=p["tur"], s=p["shape"], bb=p["shape"].BoundBox))
doc = App.openDocument(os.path.join(FC, "montaj", "robot-montaj.FCStd"))
for o in doc.Objects:
    if o.TypeId != "Part::Feature" or not hasattr(o, "Tur") or getattr(o, "Modul", "") == "taban" or o.Tur == "Referans":
        continue
    s = o.Shape.copy()
    s.Placement = o.getGlobalPlacement()
    s = s.copy()
    PRC.append(dict(ad=o.Label, modul=getattr(o, "Modul", "?"), tur=o.Tur, s=s, bb=s.BoundBox))
GERCEK = [q for q in PRC if q["tur"] != "Referans"]
log("parca", len(PRC), "gercek", len(GERCEK), "taban disi", sum(1 for q in PRC if q["modul"] != "taban"))

IZIN = {   # F10v-yol-bosluk.py ile aynı; yol 10'un "Acil stop" öneki P10.8d acil stop düğüm kartını (yolun geçtiği kart) da kapsar.
           # Dağıtım kartı C hiçbir yolda izinli değil (yol 6'nın kafa ucu kartın yanına inmiyor; § 7).
    1: r"^(Aku LiFePO4|Ana sigorta|Ana anahtar|Sigorta kutusu)",
    2: r"^(Aku LiFePO4|.*\(yildiz 3\)$|Bara tutucusu yildiz)",
    3: r"^(Sigorta kutusu|Role 12|.*\(anahtarli [123]\)$|.*\(yildiz 1\)$|Bara tutucusu|BTS7960 motor surucu sol$|Motor JGB37-520 \(on sol\)|Motor braketi L 37 mm \(on sol\))",
    4: r"^(.*\((anahtarli|yildiz) 2\)$|Bara tutucusu|BTS7960 motor surucu sag$|Motor JGB37-520 \((on|arka) sag\)|Motor braketi L 37 mm \((on|arka) sag\))",
    5: r"^(.*\((anahtarli|yildiz) 1\)$|Bara tutucusu|XL4016 servo 6 V A|.*Servo dagitim karti A)",
    6: r"^$",
    7: r"^(.*\((anahtarli|yildiz) 1\)$|Bara tutucusu|XL4016 servo 6 V B|.*Servo dagitim karti B)",
    8: r"^(Sigorta kutusu|.*\(yildiz 4\)$|Bara tutucusu yildiz)",
    9: r"^(Sigorta kutusu|.*\(yildiz 4\)$|Bara tutucusu yildiz|XL4016 cevre|ESP32)",
    10: r"^(Sigorta kutusu|Acil stop|Role 12|Arayuz karti)",
    11: r"^(Sonar|Arayuz karti|ESP32)",
    12: r"^(BTS7960 motor surucu sol$|ESP32)",
}
KIRP = {9: 12, 12: 2}      # rehberin çizdiği son nokta (rehber_kablo.CAD_KIRP son)
PAY = 15.0


def yakin(bb, q, pay=PAY):
    return not (bb.XMax + pay < q.XMin or q.XMax + pay < bb.XMin or bb.YMax + pay < q.YMin or q.YMax + pay < bb.YMin
                or bb.ZMax + pay < q.ZMin or q.ZMax + pay < bb.ZMin)


# ---------------------------------------------------------------------------------------------------------------- yol
out = dict(etiket=ETIKET, parca_taban=len(TP.P), parca_taban_gercek=sum(1 for p in TP.P if p["tur"] != "Referans"), yol={}, gecis={})
for n, (devre, renk, pts) in enumerate(TP.YOL, 1):
    for etk, nk in (("tam", None), ("rehber", KIRP.get(n))):
        if etk == "rehber" and nk is None:
            continue
        pp = pts[:nk + 1] if nk is not None else pts
        sh = TP.tup(pp, 2.5)
        iz = re.compile(IZIN[n])
        kayit = []
        for q in GERCEK:
            if not yakin(sh.BoundBox, q["bb"]):
                continue
            d = sh.distToShape(q["s"])[0]
            if d < PAY:
                ok = bool(iz.search(q["ad"]))
                v = 0.0
                if d < 1e-3 and not ok:
                    try:
                        v = sh.common(q["s"]).Volume
                    except Exception:
                        v = -1.0
                kayit.append((round(d, 3), ascii_(q["ad"]), q["modul"], ok, round(v, 3)))
        kayit.sort()
        yab = [k for k in kayit if not k[3]]
        out["yol"]["%d %s" % (n, etk)] = dict(
            devre=ascii_(devre), nokta=len(pp), noktalar=[[round(c, 2) for c in p] for p in pp],
            en_dar_yabanci=yab[:8], en_dar_yabanci_taban=[k for k in yab if k[2] == "taban"][:4],
            yabanci_ortak_hacim_mm3=round(sum(k[4] for k in yab if k[4] > 0), 3),
            yabanci_temas=[k for k in yab if k[0] < 1e-3], izinli_temas=[k for k in kayit if k[3] and k[0] < 0.5][:12])
        log("yol %d %s: en dar yabanci %s" % (n, etk, yab[:3]))
    out["gecis"][str(n)] = [(a, [round(c, 1) for c in m], s) for a, m, s in KYT.gecis_denetle(pts, 2.5)]

# ---------------------------------------------------------------------------------------------------------------- oturma, alt baş
YD0, YD1 = A.Y_DECK0, A.Y_DECK1
PANEL = TP.P[TP.KAT_AR]["shape"]
pan_up = PANEL.copy(); pan_up.translate(V(0, 0.1, 0))
pan_dn = PANEL.copy(); pan_dn.translate(V(0, -0.1, 0))
PANEL_BB = PANEL.BoundBox


def dilim_oran(s, y0, panel):
    bb = s.BoundBox
    dl = s.common(Part.makeBox(bb.XLength + 2, 0.1, bb.ZLength + 2, V(bb.XMin - 1, y0, bb.ZMin - 1)))
    tam = dl.Volume / 0.1
    des = dl.common(panel).Volume / 0.1
    return round(tam, 3), round(des, 3)


oturma = []
for p in TP.P:
    bb = p["shape"].BoundBox
    if bb.ZMin > PANEL_BB.ZMax or bb.XMin < PANEL_BB.XMin - 1 or bb.XMax > PANEL_BB.XMax + 1:
        continue
    if p["ad"].startswith("Burc ") and abs(bb.YMin - YD1) < 0.01:
        tam, des = dilim_oran(p["shape"], YD1, pan_up)
        oturma.append(dict(parca=ascii_(p["ad"]), merkez_xz=[round(bb.Center.x, 2), round(bb.Center.z, 2)], yuz="panel ustu",
                           taban_alani_mm2=tam, panelde_desteklenen_mm2=des, oran=round(des / tam, 3) if tam else None))
    elif p["ad"].startswith("Vida ") and " alt)" in p["ad"] and bb.YMax > YD0 - 0.01 and bb.YMin < YD0:
        tam, des = dilim_oran(p["shape"], YD0 - 0.1, pan_dn)
        oturma.append(dict(parca=ascii_(p["ad"]), merkez_xz=[round(bb.Center.x, 2), round(bb.Center.z, 2)], yuz="panel alti (vida basi)",
                           taban_alani_mm2=tam, panelde_desteklenen_mm2=des, oran=round(des / tam, 3) if tam else None))
out["oturma"] = oturma
log("oturma", len(oturma), [(o["parca"][:40], o["oran"]) for o in oturma if o["oran"] is not None and o["oran"] < 0.999])

AKU = [p for p in TP.P if p["ad"].startswith(("Aku LiFePO4", "Aku kayisi"))]
alt_bas = []
for p in TP.P:
    bb = p["shape"].BoundBox
    if p["tur"] != "Baglanti" or not (bb.YMin < YD0 - 0.01 < bb.YMax + 0.01) or bb.ZMin > PANEL_BB.ZMax or bb.YMax > YD1 + 30:
        continue
    en = None
    for q in AKU:
        if yakin(bb, q["shape"].BoundBox, 10.0):
            d = p["shape"].distToShape(q["shape"])[0]
            if en is None or d < en[0]:
                en = (round(d, 3), ascii_(q["ad"]))
    if en:
        alt_bas.append(dict(parca=ascii_(p["ad"]), merkez_xz=[round(bb.Center.x, 2), round(bb.Center.z, 2)], en_yakin=en))
alt_bas.sort(key=lambda r: r["en_yakin"][0])
out["alt_bas"] = alt_bas[:30]
log("alt bas", len(alt_bas), alt_bas[:4])

# ---------------------------------------------------------------------------------------------------------------- yeni kartlar x yollar
YENI = ("Acil stop dugum karti", "Dagitim karti C")
yeni = []
tuple_ = [(n, TP.tup(pts, 2.5)) for n, (_d, _r, pts) in enumerate(TP.YOL, 1)]
for p in TP.P:
    if YENI[0] not in p["ad"] and YENI[1] not in p["ad"]:
        continue
    r = dict(parca=ascii_(p["ad"]), bb=[round(c, 2) for c in (p["shape"].BoundBox.XMin, p["shape"].BoundBox.XMax, p["shape"].BoundBox.YMin,
                                                           p["shape"].BoundBox.YMax, p["shape"].BoundBox.ZMin, p["shape"].BoundBox.ZMax)], yol=[])
    for n, t in tuple_:
        if yakin(p["shape"].BoundBox, t.BoundBox, 10.0):
            r["yol"].append((n, round(p["shape"].distToShape(t)[0], 3)))
    r["yol"].sort(key=lambda x: x[1])
    yeni.append(r)
out["yeni"] = yeni
log("yeni", [(y["parca"][:30], y["yol"][:2]) for y in yeni])

# ---------------------------------------------------------------------------------------------------------------- şemalar
sg = json.load(open(os.path.join(CIKTI, "sema-girdi.json"), encoding="utf-8"))["semalar"]
sema = []
for s in sg:
    pts = [V(*p) for p in s["noktalar"]]
    w = Part.makePolygon(pts)
    r = s["r_cizim"]
    bbw = w.BoundBox
    kayit = []
    for q in GERCEK:
        if not yakin(bbw, q["bb"], r + 10.0):
            continue
        dd = w.distToShape(q["s"])
        d = dd[0]
        if d >= r + 5.0:
            continue
        pw = dd[1][0][0]
        ilk, son = min((pw - pts[0]).Length, (pw - pts[-1]).Length), None
        yer = "uc" if ilk <= 10.0 else "ara"
        kayit.append(dict(d=round(d, 3), parca=ascii_(q["ad"]), modul=q["modul"], yer=yer, nokta=[round(pw.x, 1), round(pw.y, 1), round(pw.z, 1)],
                          uca_mm=round(ilk, 1)))
    kayit.sort(key=lambda k: k["d"])
    sema.append(dict(kaynak=s["kaynak"], ad=s["ad"], r_cizim=r, nokta=len(pts), en_dar=kayit[0] if kayit else None,
                     eksen_icinde=[k for k in kayit if k["d"] < 1e-3], cizim_icinde=[k for k in kayit if k["d"] < r],
                     cizim_icinde_ara=[k for k in kayit if k["d"] < r and k["yer"] == "ara"], yakin=kayit[:10]))
    log("sema %s/%s: eksen icinde %d, cizim icinde %d (ara %d), en dar %s" % (
        s["kaynak"], s["ad"], len(sema[-1]["eksen_icinde"]), len(sema[-1]["cizim_icinde"]), len(sema[-1]["cizim_icinde_ara"]),
        (kayit[0]["d"], kayit[0]["parca"][:40]) if kayit else None))
out["sema"] = sema
out["sure_s"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(CIKTI, "%s.json" % ETIKET), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("BITTI", os.path.join(CIKTI, "%s.json" % ETIKET))
