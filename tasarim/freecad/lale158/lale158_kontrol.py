# Lale 1,58 m - tasarim ajani basit kontrolleri (freecadcmd): toplam boy, zincir, cep, tabla sigmasi, dosya acilisi, ekran parcalari x tum robot (ev pozu), kablo tupu x robot.
# Tam tarama (kol, kafa, devrilme) burada DEGIL: carpisma_kos.py, taban_montaj devrilme, Y2b-ivme (ikinci ajan).
# FC_SCRIPT=<bu dosya> freecadcmd run_fc.py  -> lale158-kontrol.json. montaj/ana_montaj.py'den SONRA.
import os, sys, json, math, time
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for p_ in (HERE, UST):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import arayuz as A
import kablo_yolu_ekran as KY

V = App.Vector
t0 = time.time()
doc = App.openDocument(os.path.join(UST, "montaj", "robot-montaj.FCStd"))
P = []
for o in doc.Objects:
    if o.TypeId == "Part::Feature" and hasattr(o, "Tur"):
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        s = s.copy()
        P.append(dict(ad=o.Label, tur=o.Tur, sh=s, bb=s.BoundBox))
print("parca", len(P), "%.1fs" % (time.time() - t0))
# Toplam boy: BoundBox B-spline kontrol noktalarini da sayar (2-5 mm sisirir); uc parcalarda optimalBoundingBox
_ust = sorted(P, key=lambda p: -p["bb"].YMax)[:12]
_alt = sorted(P, key=lambda p: p["bb"].YMin)[:12]
for p in _ust + _alt:
    p["obb"] = p["sh"].optimalBoundingBox()
ust = max(_ust, key=lambda p: p["obb"].YMax)
ymax = ust["obb"].YMax
ymin = min(p["obb"].YMin for p in _alt)
sonuc = dict(parca=len(P), zemin_y=round(ymin, 3), tepe_y=round(ymax, 3), toplam_boy_mm=round(ymax - ymin, 3), tepe_parca=ust["ad"], hedef_boy=A.BOY,
             boy_tamam=bool(abs((ymax - ymin) - A.BOY) < 1.0),
             zincir=dict(BOY=A.BOY, HEAD_UP=A.HEAD_UP, S3=A.S3, travers_ust=A.S3 + 20, UZAMA=A.UZAMA, uzatma_bant=A.UZAMA / A.UZATMA_BANT, DIREK_Y1=A.DIREK_Y1, DIREK_L=A.DIREK_L,
                         GOVDE_Y1=A.GOVDE_Y1, dikis=list(A.GOVDE_DIKIS), on_dikis=A.GOGUS_ON_DIKIS, duzlem_y=[round(A.GOGUS_ALT_Y, 2), A.GOGUS_UST_Y], cep_merkez_y=round(A.GOGUS_EKRAN_Y, 2),
                         kafa_alt_y=A.KAFA["kafa_alt_y"], kafa_govde=list(A.KAFA["govde_y"]), tilt_y=A.KAFA["tilt_nokta"][1], adaptor_h=round(A.KAFA["adaptor_h"], 3), denge=dict(dy=A.KAFA["denge"]["dy"], zb=A.KAFA["denge"]["zb"]),
                         zincir_metin="BOY %g = S3 %g + travers yarim 20 + HEAD_UP %g (kafa alt 75 + kabuk 215); S3 = 955 + UZAMA %g" % (A.BOY, A.S3, A.HEAD_UP, A.UZAMA)))

# ------------------------------------------------------------ ekran ve yakini: tum parcalara cakisma / en yakin
EKRAN_ON = ("Gogus ekrani", "Cerceve civatasi", "Isil gomme somun M3 (gogus", "VESA", "Tasiyici", "Cekic somun M6 (direk on")
KENDI = [p for p in P if p["ad"].startswith(EKRAN_ON)]
ana = [p for p in KENDI if p["ad"].startswith("Gogus ekrani")]
baska = [p for p in P if p not in KENDI]
cakisma, yakin = [], []
for a in ana:
    bb = App.BoundBox(a["bb"]); bb.enlarge(40)
    for b in baska:
        if bb.intersect(b["bb"]):
            d = a["sh"].distToShape(b["sh"])[0]
            if d < 25.0:
                yakin.append((a["ad"], b["ad"], round(d, 3)))
            if d < 1e-3:
                v = a["sh"].common(b["sh"]).Volume
                if v > 0.5:
                    cakisma.append((a["ad"], b["ad"], round(v, 2)))
yakin.sort(key=lambda r: r[2])
sonuc["ekran_cakisma"] = cakisma
sonuc["ekran_en_yakin"] = yakin[:40]
print("ekran cakisma", len(cakisma), "%.1fs" % (time.time() - t0))

# ------------------------------------------------------------ kablo tupleri (kasa haric)
TUP = {}
for ad, yol in KY.yollar().items():
    r = KY.KABLO[ad][0] / 2
    t = None
    for a_, b_ in zip(yol[:-1], yol[1:]):
        a_, b_ = V(*a_), V(*b_)
        if (b_ - a_).Length < 1e-6:
            continue
        c = Part.makeCylinder(r, (b_ - a_).Length, a_, b_ - a_).fuse(Part.makeSphere(r, b_))
        t = c if t is None else t.fuse(c)
    TUP[ad] = t
sonuc["kablo_ozet"] = KY.ozet()
kablo_cak = {}
for ad, t in TUP.items():
    r_ = []
    tb = t.BoundBox
    for p in P:
        if p["bb"].intersect(tb):
            v = p["sh"].common(t).Volume
            if v > 0.5:
                r_.append((p["ad"], round(v, 1)))
    kablo_cak[ad] = sorted(r_, key=lambda q: -q[1])[:25]
sonuc["kablo_tup_cakisma"] = kablo_cak
sonuc["kablo_tup_notu"] = ("Ev pozu, tek tek kablo tupu x parcalar. Kasa zarfinin ucu (port girintisi) ve kablolarin cekic somun / kablo gosterimi gibi semaya takilan ufak hacimleri beklenir; kablolar arasi temas taranmaz. "
                           "Listede rulman yuvasi, servo yuvasi, mil varsa o kablo gecisi elle bakilmali.")
print("kablo", "%.1fs" % (time.time() - t0))

# ------------------------------------------------------------ baski tablosu (modul analizlerinden)
UX, UY, UZ = A.YAZICI["kullanilabilir"]
tab = []
for mod in ("kabuk", "kafa", "taban", "dirsek", "omuz"):
    yol_ = os.path.join(UST, mod, mod + "-analiz.json")
    if not os.path.exists(yol_):
        continue
    js = json.load(open(yol_, encoding="utf-8"))
    for b in js.get("baski", []):
        ol = b.get("olcu") or []
        tab.append(dict(modul=mod, ad=b["ad"], olcu=ol, sigar=bool(ol and sorted(ol[:2])[1] <= max(UX, UY) and ol[2] <= UZ) if len(ol) == 3 else None, desteksiz=b.get("desteksiz"), destek_sorun=b.get("destek_sorun_sayi"), g=b.get("filament_g"), sa=b.get("sure_saat"), yon=b.get("yon")))
sonuc["baski"] = tab
sonuc["baski_sigmayan"] = [t for t in tab if t["sigar"] is False]
sonuc["tabla"] = [UX, UY, UZ]
ge = json.load(open(os.path.join(UST, "kabuk", "kabuk-analiz.json"), encoding="utf-8")).get("gogus_ekrani")
sonuc["gogus_ekrani"] = ge
sonuc["kafa_denge_olcum"] = json.load(open(os.path.join(UST, "kafa", "kafa-analiz.json"), encoding="utf-8")).get("grup")
sonuc["sure_s"] = round(time.time() - t0, 1)
json.dump(sonuc, open(os.path.join(HERE, "lale158-kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("bitti", sonuc["toplam_boy_mm"], sonuc["boy_tamam"], "sigmayan", len(sonuc["baski_sigmayan"]))
