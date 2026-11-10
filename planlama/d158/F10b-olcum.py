# F10b (P10.2) olcum: on sarj karti x elektronik kati, gercek katilarla (FreeCAD).
# Montaj sirasi kontrolu (10.11.2026, mesh sinir kutusu) B6'da elektronik katinin inerken on sarj kartinin iki on burcuna
# 0,5 mm taktigini buldu. Bu betik taban (+ iskelet + kabuk etek braketleri) katilarini yukler, hareketli grubu takili
# konumundan +Y yonunde 0...H mm (0,5 mm adim) kaydirir ve her konumda engellerle ortak hacim + en kucuk boslugu olcer:
#   B6: elektronik kati alt montaji (kat + kartlar) -> engeller: o ana dek takili her sey (guc paneli alt montaji dahil)
#   B5: guc paneli alt montaji (panel + ustundeki kartlar, burc ve vidalari) -> engeller: B1...B4, C0, iskelet
#   B3: alt plaka kartlari (BTS7960 x2, XL4016 A / B / cevre; kart + burc + ust vida) -> engeller: iskelet, plaka, tahrik, diger B3
# Ek: on sarj burclarinin panel ustune oturma alani; secenek degerlendirmesi (karti -z kaydirmak / katta centik) modele
# dokunmadan, katilar bellekte kopyalanarak.
# Calistirma (ASCII baslatici, tasarim/freecad/README.md):
#   FC_SCRIPT=<bu dosya> "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecadcmd.exe" "$USERPROFILE/.robot-cad/run_fc.py"
# Cikti: ayni klasorde F10b-olcum.json. Depoda baska dosya yazmaz.
import os, sys, json, time
import FreeCAD as App
import Part

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FC = os.path.join(ROOT, "tasarim", "freecad")
for _p in (FC, os.path.join(FC, "taban"), os.path.join(FC, "iskelet"), os.path.join(FC, "kabuk")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import arayuz as A

V = App.Vector
ADIM = float(os.environ.get("F10B_ADIM", "0.5"))
H = float(os.environ.get("F10B_H", "60"))          # M5x40 burc boyu + 20
YAKIN = 3.0                                          # bbox araligi bundan buyukse kesin olcum yapilmaz (alt sinir = bbox araligi)
KABUK = os.environ.get("F10B_KABUK", "1") == "1"


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


def ascii_(s):
    return s.encode("ascii", "replace").decode("ascii")


# ---------------------------------------------------------------------- parcalar (global koordinat)
PRC = []


def ekle(modul, p):
    (tx, ty, tz), ayna = A.modul_konum(modul)
    s = p["shape"].copy()
    if ayna:
        s = s.mirror(V(0, 0, 0), V(1, 0, 0))
    if (tx, ty, tz) != (0.0, 0.0, 0.0):
        s.translate(V(tx, ty, tz))
    PRC.append(dict(ad=p["ad"], modul=modul, grup=p.get("grup", ""), tur=p.get("tur", ""), s=s, bb=s.BoundBox))


import taban_parcalar as TP
for p in TP.P:
    ekle("taban", p)
log("taban", len(TP.P))
import iskelet_parcalar as IP
for p in IP.P:
    ekle("iskelet", p)
log("iskelet", len(IP.P))
if KABUK:
    import kabuk_parcalar as KP
    for p in KP.P:
        if p.get("grup") == "Etek braketleri":
            ekle("kabuk", p)
    log("kabuk etek braketleri", sum(1 for q in PRC if q["modul"] == "kabuk"))

YD0 = A.Y_DECK0


def tb(q):
    return q["modul"] == "taban"


def ad_(q, *ss):
    return any(s in q["ad"] for s in ss)


REF = [i for i, q in enumerate(PRC) if q["grup"] == "Referans" or q["tur"] == "Referans"]
SONRA = [i for i, q in enumerate(PRC) if tb(q) and (q["grup"] in ("Sensor", "Sonar") or ad_(q, "Acil", "acil", "Ana anahtar", "HC-SR04"))]
KAT = [i for i, q in enumerate(PRC) if tb(q) and (q["grup"] == "Elektronik" or q["ad"].startswith("Elektronik kati"))]
KAT_CIV_ON = [i for i, q in enumerate(PRC) if tb(q) and ad_(q, "(kat ") and q["bb"].Center.z >= 0]
KAT_CIV_AR = [i for i, q in enumerate(PRC) if tb(q) and ad_(q, "(kat ") and q["bb"].Center.z < 0]
GUC = [i for i, q in enumerate(PRC) if tb(q) and q["grup"] == "Guc" and q["bb"].YMax > YD0 - 0.5 and not ad_(q, "Ana anahtar")
       and i not in REF]
GUC.append([i for i, q in enumerate(PRC) if q["ad"].startswith("Guc paneli")][0])
ONSARJ = [i for i in GUC if ad_(PRC[i], "On sarj karti")]
B4 = [i for i, q in enumerate(PRC) if tb(q) and ad_(q, "Burc M5x40", "Saplama M5", "Cekic somun M5")]
ALT_KART = {}
for i, q in enumerate(PRC):
    if not tb(q) or q["grup"] != "Guc" or i in GUC or " alt)" in q["ad"]:
        continue
    for anah in ("BTS7960 motor surucu sol", "BTS7960 motor surucu sag", "XL4016 servo 6 V B", "XL4016 cevre 5 V", "XL4016 servo 6 V A"):
        if anah in q["ad"]:
            ALT_KART.setdefault(anah, []).append(i)
ETEK = [i for i, q in enumerate(PRC) if q["modul"] == "kabuk"]
log("KAT", len(KAT), "GUC", len(GUC), "ONSARJ", len(ONSARJ), "alt kart", {k: len(v) for k, v in ALT_KART.items()}, "etek", len(ETEK))


def bbgap(a, b):
    """iki BoundBox arasi oklid boslugu (kesisiyorsa 0)."""
    dx = max(0.0, max(a.XMin - b.XMax, b.XMin - a.XMax))
    dy = max(0.0, max(a.YMin - b.YMax, b.YMin - a.YMax))
    dz = max(0.0, max(a.ZMin - b.ZMax, b.ZMin - a.ZMax))
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def bb_kay(bb, dy):
    return App.BoundBox(bb.XMin, bb.YMin + dy, bb.ZMin, bb.XMax, bb.YMax + dy, bb.ZMax)


def sinif_ob(j, sinif):
    return sinif(j)


def supur(hareket, engel, siniflar, oturma=(), H=H, adim=ADIM, ad=""):
    """hareket: parca indeksleri (birlikte +Y kayar); engel: indeksler. siniflar: engel j -> sinif adi.
    oturma: (i, j) tasarim temas ciftleri (yalniz dy = 0'da bosluk hesabindan ayrilir)."""
    # aday ciftler: XZ izdusumu 5 mm icinde ve Y araliginda
    aday = []
    for i in hareket:
        a = PRC[i]["bb"]
        for j in engel:
            b = PRC[j]["bb"]
            if a.XMin - 5 > b.XMax or b.XMin - 5 > a.XMax or a.ZMin - 5 > b.ZMax or b.ZMin - 5 > a.ZMax:
                continue
            if b.YMax < a.YMin - 5 or b.YMin > a.YMax + H + 5:
                continue
            aday.append((i, j))
    log(ad, "aday cift", len(aday))
    kon = []
    n = int(round(H / adim))
    cache = {}
    for k in range(n + 1):
        dy = k * adim
        top_hacim, en_bos, en_cift = 0.0, 1e9, None
        sin = {}
        cak = []
        temas0 = []
        for (i, j) in aday:
            abb = bb_kay(PRC[i]["bb"], dy)
            g = bbgap(abb, PRC[j]["bb"])
            if g > YAKIN:
                d, vol, kesin = g, 0.0, False
            else:
                if i not in cache or cache[i][0] != dy:
                    s = PRC[i]["s"].copy()
                    s.translate(V(0, dy, 0))
                    cache[i] = (dy, s)
                s = cache[i][1]
                vol = 0.0
                if abb.intersect(PRC[j]["bb"]):
                    try:
                        vol = s.common(PRC[j]["s"]).Volume
                    except Exception:
                        vol = -1.0
                try:
                    d = s.distToShape(PRC[j]["s"])[0]
                except Exception:
                    d = -1.0
                kesin = True
            if dy == 0 and (i, j) in oturma:
                if kesin and d < 1e-6:
                    temas0.append([ascii_(PRC[i]["ad"]), ascii_(PRC[j]["ad"])])
                continue
            c = siniflar(j)
            e = sin.setdefault(c, dict(ortak_hacim_mm3=0.0, en_kucuk_bosluk_mm=1e9, cift=None))
            if vol > 1e-4:
                e["ortak_hacim_mm3"] += vol
                top_hacim += vol
                cak.append([ascii_(PRC[i]["ad"]), ascii_(PRC[j]["ad"]), round(vol, 4)])
            if d < e["en_kucuk_bosluk_mm"]:
                e["en_kucuk_bosluk_mm"], e["cift"] = d, [ascii_(PRC[i]["ad"]), ascii_(PRC[j]["ad"])]
            if d < en_bos:
                en_bos, en_cift = d, [ascii_(PRC[i]["ad"]), ascii_(PRC[j]["ad"])]
        for e in sin.values():
            e["ortak_hacim_mm3"] = round(e["ortak_hacim_mm3"], 4)
            e["en_kucuk_bosluk_mm"] = round(e["en_kucuk_bosluk_mm"], 4)
        kon.append(dict(dy_mm=round(dy, 2), ortak_hacim_mm3=round(top_hacim, 4), en_kucuk_bosluk_mm=round(en_bos, 4),
                        en_kucuk_cift=en_cift, sinif=sin, cakisan=cak, tasarim_temasi_dy0=temas0))
        if k % 20 == 0:
            log(ad, "dy", dy, "hacim", round(top_hacim, 3), "bosluk", round(en_bos, 3))
    return dict(aday_cift=len(aday), konumlar=kon,
                ozet=dict(en_buyuk_ortak_hacim_mm3=max(x["ortak_hacim_mm3"] for x in kon),
                          girisimli_konum=[x["dy_mm"] for x in kon if x["ortak_hacim_mm3"] > 1e-4],
                          en_kucuk_bosluk_mm=min(x["en_kucuk_bosluk_mm"] for x in kon),
                          en_kucuk_bosluk_dy=min(kon, key=lambda x: x["en_kucuk_bosluk_mm"])["dy_mm"],
                          en_kucuk_bosluk_cift=min(kon, key=lambda x: x["en_kucuk_bosluk_mm"])["en_kucuk_cift"],
                          bosluk_05_alti_konum=[x["dy_mm"] for x in kon if x["en_kucuk_bosluk_mm"] < 0.5]))


HEPSI = set(range(len(PRC)))
DIS = set(REF) | set(SONRA)

# ---------------------------------------------------------------------- B6: elektronik kati
eng6 = sorted(HEPSI - set(KAT) - set(KAT_CIV_ON) - DIS)
sk6 = lambda j: ("on_sarj_grubu" if j in ONSARJ else "guc_paneli_diger" if j in GUC else "alt_kat_kartlari" if any(j in v for v in ALT_KART.values())
                 else "etek_braket" if j in ETEK else PRC[j]["modul"] + "_diger")
otur6 = [(i, j) for i in KAT for j in B4]       # kat M5x40 burclara oturur
R6 = supur(KAT, eng6, sk6, oturma=otur6, ad="B6")

# ---------------------------------------------------------------------- B5: guc paneli
eng5 = sorted(HEPSI - set(KAT) - set(GUC) - set(KAT_CIV_ON) - set(KAT_CIV_AR) - DIS)
sk5 = lambda j: ("alt_kat_kartlari" if any(j in v for v in ALT_KART.values()) else "etek_braket" if j in ETEK
                 else "burc_M5x40" if j in B4 else PRC[j]["modul"] + "_diger")
otur5 = [(i, j) for i in GUC for j in B4]
# alt vidalar panelin altindan yukari girer (rehberde ayri); B5 inisinde yine de grupla birlikte sayildi
R5 = supur(GUC, eng5, sk5, oturma=otur5, ad="B5")

# ---------------------------------------------------------------------- B3: alt plaka kartlari
R3 = {}
tum_alt = set(v for vv in ALT_KART.values() for v in vv)
for anah, M in ALT_KART.items():
    kendi_alt = set(j for j, q in enumerate(PRC) if tb(q) and anah in q["ad"] and " alt)" in q["ad"])   # alttan, kartla birlikte
    eng3 = sorted(HEPSI - set(M) - kendi_alt - set(KAT) - set(GUC) - set(KAT_CIV_ON) - set(KAT_CIV_AR) - set(B4) - DIS)
    sk3 = lambda j: ("diger_alt_kart" if j in tum_alt else "etek_braket" if j in ETEK else PRC[j]["modul"] + "_" + (PRC[j]["grup"] or ""))
    plaka_alt = [j for j in eng3 if PRC[j]["ad"].startswith("Alt plaka")]
    otur3 = [(i, j) for i in M for j in plaka_alt]
    r = supur(M, eng3, sk3, oturma=otur3, H=28.0, ad="B3 " + anah)
    R3[ascii_(anah)] = dict(ozet=r["ozet"], aday_cift=r["aday_cift"],
                            konum_ozet=[dict(dy_mm=x["dy_mm"], ortak_hacim_mm3=x["ortak_hacim_mm3"], en_kucuk_bosluk_mm=x["en_kucuk_bosluk_mm"],
                                             en_kucuk_cift=x["en_kucuk_cift"]) for x in r["konumlar"]])

# ---------------------------------------------------------------------- on sarj burclari: panel ustune oturma alani
PANEL = [i for i, q in enumerate(PRC) if q["ad"].startswith("Guc paneli")][0]
KAT_ON = [i for i, q in enumerate(PRC) if q["ad"].startswith("Elektronik kati")][0]
YD1 = A.Y_DECK1
pan_up = PRC[PANEL]["s"].copy()
pan_up.translate(V(0, 0.1, 0))


def oturma_alani(i, panel=pan_up):
    s = PRC[i]["s"]
    bb = s.BoundBox
    dilim = s.common(Part.makeBox(bb.XLength + 2, 0.1, bb.ZLength + 2, V(bb.XMin - 1, YD1, bb.ZMin - 1)))
    tam = dilim.Volume / 0.1
    des = dilim.common(panel).Volume / 0.1
    return round(tam, 3), round(des, 3)


oturma = []
for i in GUC:
    q = PRC[i]
    if q["ad"].startswith("Burc ") and abs(q["bb"].YMin - YD1) < 0.01:
        tam, des = oturma_alani(i)
        oturma.append(dict(parca=ascii_(q["ad"]), merkez_xz=[round(q["bb"].Center.x, 2), round(q["bb"].Center.z, 2)],
                           taban_alani_mm2=tam, panelde_desteklenen_mm2=des, oran=round(des / tam, 3) if tam else None))
# alt vidalarin bas oturmasi (panel alt yuzu)
pan_dn = PRC[PANEL]["s"].copy()
pan_dn.translate(V(0, -0.1, 0))
for i in GUC:
    q = PRC[i]
    if " alt)" in q["ad"] and ("On sarj" in q["ad"] or "servo 6 V C" in q["ad"]):
        s = q["s"]
        bb = s.BoundBox
        dilim = s.common(Part.makeBox(bb.XLength + 2, 0.1, bb.ZLength + 2, V(bb.XMin - 1, YD0 - 0.1, bb.ZMin - 1)))
        tam = dilim.Volume / 0.1
        des = dilim.common(pan_dn).Volume / 0.1
        oturma.append(dict(parca=ascii_(q["ad"]), merkez_xz=[round(bb.Center.x, 2), round(bb.Center.z, 2)],
                           taban_alani_mm2=round(tam, 3), panelde_desteklenen_mm2=round(des, 3), oran=round(des / tam, 3) if tam else None,
                           not_="vida basi halkasi panel alt yuzunde"))
log("oturma", len(oturma))


# ---------------------------------------------------------------------- secenekler (bellekte, modele dokunmadan)
def kat_on_bosluk_supur(os_sekiller, kat_sekli, H=30.0, adim=ADIM):
    """on sarj grubu (sekil listesi) x kat on (sekil), kat +Y kayarken: en buyuk ortak hacim, en kucuk bosluk."""
    eb, ev = 1e9, 0.0
    for k in range(int(round(H / adim)) + 1):
        dy = k * adim
        s = kat_sekli.copy()
        s.translate(V(0, dy, 0))
        for o in os_sekiller:
            if bbgap(s.BoundBox, o.BoundBox) > YAKIN:
                continue
            if s.BoundBox.intersect(o.BoundBox):
                ev = max(ev, s.common(o).Volume)
            eb = min(eb, s.distToShape(o)[0])
    return round(ev, 4), round(eb, 4)


def komsu_bosluk(os_sekiller, haric):
    """kaydirilmis on sarj grubu x guc panelinin diger parcalari + aku + direk: en kucuk bosluk (panel haric: oturma)."""
    out = {}
    adaylar = [j for j in (set(GUC) | set(range(len(PRC)))) if j not in haric and j not in REF and j not in KAT and j != PANEL]
    for j in adaylar:
        b = PRC[j]["bb"]
        for o in os_sekiller:
            g = bbgap(o.BoundBox, b)
            if g > 15:
                continue
            d = o.distToShape(PRC[j]["s"])[0]
            k = ascii_(PRC[j]["ad"])
            out[k] = round(min(out.get(k, 1e9), d), 3)
    return dict(sorted(out.items(), key=lambda kv: kv[1])[:8])


SEC = {}
os_ilk = [PRC[i]["s"] for i in ONSARJ]
SEC["mevcut"] = dict(kat_inis=kat_on_bosluk_supur(os_ilk, PRC[KAT_ON]["s"]),
                     komsu=komsu_bosluk(os_ilk, set(ONSARJ)))
for dz in (1.0, 1.5, 2.0):
    sh = []
    for i in ONSARJ:
        s = PRC[i]["s"].copy()
        s.translate(V(0, 0, -dz))
        sh.append(s)
    ot = []
    for i, s in zip(ONSARJ, sh):
        if PRC[i]["ad"].startswith("Burc ") and abs(PRC[i]["bb"].YMin - YD1) < 0.01:
            bb = s.BoundBox
            dilim = s.common(Part.makeBox(bb.XLength + 2, 0.1, bb.ZLength + 2, V(bb.XMin - 1, YD1, bb.ZMin - 1)))
            ot.append(dict(parca=ascii_(PRC[i]["ad"]), taban_alani_mm2=round(dilim.Volume / 0.1, 3),
                           panelde_desteklenen_mm2=round(dilim.common(pan_up).Volume / 0.1, 3)))
        if " alt)" in PRC[i]["ad"]:
            bb = s.BoundBox
            dilim = s.common(Part.makeBox(bb.XLength + 2, 0.1, bb.ZLength + 2, V(bb.XMin - 1, YD0 - 0.1, bb.ZMin - 1)))
            ot.append(dict(parca=ascii_(PRC[i]["ad"]), taban_alani_mm2=round(dilim.Volume / 0.1, 3),
                           panelde_desteklenen_mm2=round(dilim.common(pan_dn).Volume / 0.1, 3)))
    SEC["kaydir_-z_%.1f" % dz] = dict(kat_inis=kat_on_bosluk_supur(sh, PRC[KAT_ON]["s"]), komsu=komsu_bosluk(sh, set(ONSARJ)), oturma=ot)
    log("secenek kaydir", dz, SEC["kaydir_-z_%.1f" % dz]["kat_inis"])
for derin in (1.5,):
    obb = App.BoundBox()
    for i in ONSARJ:
        obb.add(PRC[i]["bb"])
    x0, x1 = obb.XMin - 1.5, obb.XMax + 1.5
    kz0 = TP.KAT_ON_Z0
    cent = Part.makeBox(x1 - x0, A.DECK_T + 2, derin + 0.5, V(x0, YD0 - 1, kz0 - 0.5))
    kat2 = PRC[KAT_ON]["s"].cut(cent)
    SEC["centik_%.1f" % derin] = dict(kat_inis=kat_on_bosluk_supur(os_ilk, kat2), x=[round(x0, 2), round(x1, 2)],
                                      z=[kz0, kz0 + derin], hacim_azalma_mm3=round(PRC[KAT_ON]["s"].Volume - kat2.Volume, 2))
    log("secenek centik", derin, SEC["centik_%.1f" % derin]["kat_inis"])

out = dict(
    paket="F10b (P10.2)", tarih=time.strftime("%Y-%m-%d %H:%M"), betik="planlama/d158/F10b-olcum.py",
    yontem=("FreeCAD katilari (taban_parcalar + iskelet_parcalar + kabuk etek braketleri), hareketli grup takili konumdan +Y "
            "0...%g mm, %g mm adim; aday cift XZ izdusumu 5 mm icinde; bbox araligi > %g mm ise kesin olcum yok (bosluk >= bbox "
            "araligi). Ortak hacim = common().Volume (> 1e-4 mm3 sayilir), bosluk = distToShape. dy = 0'da tasarim oturmasi "
            "(kat / panel -> M5x40 burc, kart -> alt plaka) bosluktan ayrilir." % (H, ADIM, YAKIN)),
    geometri=dict(kat_on_z0=TP.KAT_ON_Z0, guc_paneli_z1=TP.KAT_ARKA_Z1, on_sarj_merkez=list(A.TABAN["on_sarj_karti"]["merkez"]),
                  on_sarj_bb={ascii_(PRC[i]["ad"]): [round(PRC[i]["bb"].XMin, 3), round(PRC[i]["bb"].XMax, 3), round(PRC[i]["bb"].YMin, 3),
                                                   round(PRC[i]["bb"].YMax, 3), round(PRC[i]["bb"].ZMin, 3), round(PRC[i]["bb"].ZMax, 3)]
                              for i in ONSARJ}),
    gruplar=dict(kat=[ascii_(PRC[i]["ad"]) for i in KAT], guc=[ascii_(PRC[i]["ad"]) for i in GUC],
                 alt_kart={ascii_(k): [ascii_(PRC[i]["ad"]) for i in v] for k, v in ALT_KART.items()},
                 etek=len(ETEK), haric_sonra=[ascii_(PRC[i]["ad"]) for i in SONRA]),
    B6_elektronik_kati=R6, B5_guc_paneli=R5, B3_alt_kartlar=R3, on_sarj_oturma=oturma, secenekler=SEC,
    sure_s=round(time.time() - t0, 1))
json.dump(out, open(os.path.join(HERE, "F10b-olcum.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("bitti")
