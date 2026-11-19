# K54 c YANAK KUPONU (FreeCAD 1.1, Part; P10.8 1. basamak, 19.11.2026). Karar: karar-kuyrugu.md K54 "seçenek c: ilk baskı kuponunda
# yanak + çatal dayaması + horn kalınlığında kısa kupon basılır, iniş elle denenir; zorlarsa b (yanak iç yüzlerine 0,2-0,3 mm pay)".
# Sorun (F10c-gunluk.md D1): kafa iskeletinin iki yanagi arasi 54,4 mm, aradaki yigin (catal dayamasi / 625ZZ ic bilezigi ... tilt
# hornu dis yuzu) da 54,4 mm: kafa iki yanda SIFIR bosluga iner. Parca montaja GIRMEZ; insert istemez.
# Iki baski:
#   (1) yanak kuponu  = kafa-montaj.FCStd'deki GERCEK "Kafa iskeleti" ∩ KUTU (iki yanak + aralarindaki tabla dilimi; ekleme yok, kesilen yok).
#   (2) yigin mastari = olculeri ayni FCStd'den OKUNAN eksenel govde: catal dayamasi (625ZZ ic bilezigine dayanan halka) + catal kolu
#       capinda govde + tilt hornu diski (kalinlik ve cap horn'dan). Genisligi = dayama yuzu ... horn dis yuzu (yigin).
#   Kafa iskeleti ya da catal / horn degisirse kupon da degisir; JSON'daki karsilastirma (kupon <-> kaynak) farki yakalar.
# Baski: yanak kuponu kafa iskeletinin baski yonunde (ters: tabla tablada, yanaklar yukari; kafa7_parcalar.py "Kafa iskeleti" yukari
# (0, -1, 0)). Mastar ekseni dik, horn diski tablada (horn dis yuzu = tabla yuzu).
# Cikti: kafa/stl/yanak-kuponu.stl, kafa/stl/yanak-kuponu-mastar.stl, kafa/yanak-kuponu.json. Kaynaklar yalniz OKUNUR.
# Calistirma: FC_SCRIPT=<bu betik> freecadcmd ~/.robot-cad/run_fc.py  (yalniz kafa-montaj.FCStd acilir; ~10-30 s)
import os, sys, re, math, json, hashlib, time
import FreeCAD as App
import Part
import MeshPart
import Mesh

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
if UST not in sys.path:
    sys.path.insert(0, UST)
import arayuz as A

V = App.Vector
FCSTD = os.path.join(HERE, "kafa-montaj.FCStd")
AD = dict(iskelet="Kafa iskeleti", catal="Egme catali", horn="Tilt horn 25T aluminyum disk", rul_ic="625ZZ rulman (ic bilezik)",
          rul_dis="625ZZ rulman (dis bilezik)")
KENAR = 1.0          # mm: kutu, yanak dis yuzlerinden bu kadar disarida (tabla yanlari); kablo gecisi (x -50...-37) disarida kalir
Z_YARI = 20.0        # mm: kutu z yari genisligi (yanaklar eksen +-16; tabla +-20 diliminde)
TOL = 0.01           # mm: kupon <-> kaynak ayni olcu (BRep ayni geometri)
KONI = 45.0          # derece: mastar govdesinden horn diskine gecis (desteksiz)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def hat_x(sh, y, z, x0=-200.0, x1=200.0):
    """x eksenine paralel hattin (y, z) sekil icindeki araliklari [(a, b), ...] (BRep kesisimi)."""
    c = sh.common(Part.makeLine(V(x0, y, z), V(x1, y, z)))
    out = []
    for e in c.Edges:
        a, b = sorted((e.Vertexes[0].Point.x, e.Vertexes[-1].Point.x))
        out.append((round(a, 3), round(b, 3)))
    return sorted(out)


# ---------------------------------------------------------------- kaynak
doc = App.openDocument(FCSTD)
SRC = {}
for k, ad in AD.items():
    obj = [o for o in doc.Objects if re.fullmatch(re.escape(ad) + r"(\d{3})?", o.Label) and hasattr(o, "Shape") and o.Shape.Volume > 1e-3]
    assert len(obj) == 1, (ad, [o.Label for o in obj])
    SRC[k] = obj[0].Shape.copy()
    bb = SRC[k].BoundBox
    print(ad, "bb", [round(v, 2) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)], "V", round(SRC[k].Volume, 1))
# tilt ekseni: 625ZZ ic bilezigi ve horn ayni eksende (y, z)
bri, bh = SRC["rul_ic"].BoundBox, SRC["horn"].BoundBox
YC, ZC = (bri.YMin + bri.YMax) / 2, (bri.ZMin + bri.ZMax) / 2
assert abs((bh.YMin + bh.YMax) / 2 - YC) < 1e-3 and abs((bh.ZMin + bh.ZMax) / 2 - ZC) < 1e-3, "horn ile 625ZZ ayni eksende degil"

# ---------------------------------------------------------------- kaynak olculeri (hat kesisimi; deliklerin disinda)
# yanaklar: eksenin 12 mm ustunde (tabla ile eksen arasi duz bolge) ve 10 mm altinda (r 16 yarim daire; 625ZZ yuvasi r 8, horn
# civata delikleri eksenden 6 mm'de r 1,7: hatlar ikisinin de disinda)
YANAK_HAT = [(YC + 12.0, ZC), (YC + 12.0, ZC - 10.0), (YC + 12.0, ZC + 10.0), (YC - 10.0, ZC)]


def yanak_olc(sh):
    o = {}
    for (y, z) in YANAK_HAT:
        iv = hat_x(sh, y, z)
        sol = [r for r in iv if r[1] <= 0.0]
        sag = [r for r in iv if r[0] >= 0.0]
        o["y%+.1f_z%+.1f" % (y - YC, z - ZC)] = dict(sol=sol[-1] if sol else None, sag=sag[0] if sag else None,
                                                    aralik_mm=round(sag[0][0] - sol[-1][1], 3) if sol and sag else None)
    return o


OY = yanak_olc(SRC["iskelet"])
ana = OY["y+12.0_z+0.0"]
SOL_DIS, SOL_IC = ana["sol"]
SAG_IC, SAG_DIS = ana["sag"]
# yigin: catal dayamasi (r 4 halka, M5 isil gomme deligi r 3,2 icinde: hat eksenden 3,6 mm'de), catal kolu (eksenden 10 mm'de),
# horn (merkez vidasi deligi disi, 8 mm), 625ZZ ic bilezik (r 2,5 ... 4,1: 3,5 mm)
DAYAMA = hat_x(SRC["catal"], YC, ZC + 3.6)[0][0]
KOL = hat_x(SRC["catal"], YC, ZC + 10.0)[0][0]
HORN_IC, HORN_DIS = hat_x(SRC["horn"], YC, ZC + 8.0)[0]
RUL_IC = hat_x(SRC["rul_ic"], YC, ZC + 3.5)[0]
RUL_DIS = hat_x(SRC["rul_dis"], YC, ZC + 7.0)[0]
_d = SRC["catal"].common(box(DAYAMA - 0.01, (DAYAMA + KOL) / 2, YC - 12, YC + 12, ZC - 12, ZC + 12)).optimalBoundingBox()   # yalniz dayama (taban diski r 30 y 155...158 disarida)
R_DAYAMA = round(max(_d.YMax - YC, YC - _d.YMin, _d.ZMax - ZC, ZC - _d.ZMin), 3)
_k = SRC["catal"].common(box(KOL + 0.5, KOL + 2.0, YC - 1.0, YC + 40, ZC - 40, ZC + 40)).optimalBoundingBox()
R_KOL = round(_k.YMax - YC, 3)                               # catal sol duvari: eksen cevresinde r 15 (kafa7_parcalar.py:261)
R_HORN = round(SRC["horn"].optimalBoundingBox().ZLength / 2, 3)
YIGIN = round(HORN_DIS - DAYAMA, 3)
ARALIK = round(SAG_IC - SOL_IC, 3)
KAYNAK_OLCU = dict(eksen_y=round(YC, 3), eksen_z=round(ZC, 3), yanak=OY, sol_yanak_ic=SOL_IC, sag_yanak_ic=SAG_IC,
                   catal_dayamasi_x=DAYAMA, catal_kolu_dis_x=KOL, horn_x=[HORN_IC, HORN_DIS], rulman_625_ic_bilezik_x=list(RUL_IC),
                   rulman_625_dis_bilezik_x=list(RUL_DIS), r_dayama=R_DAYAMA, r_kol=R_KOL, r_horn=R_HORN,
                   yanak_araligi_mm=ARALIK, yigin_mm=YIGIN, bosluk_mm=round(ARALIK - YIGIN, 3),
                   sol_bosluk_mm=round(DAYAMA - SOL_IC, 3), sag_bosluk_mm=round(SAG_IC - HORN_DIS, 3),
                   rulman_ic_bilezik_dayamada=abs(RUL_IC[1] - DAYAMA) < TOL, rulman_dis_bilezik_yanakla_ayni_duzlemde=abs(RUL_DIS[1] - SOL_IC) < TOL)
print("kaynak", KAYNAK_OLCU)

# ---------------------------------------------------------------- (1) yanak kuponu: iskelet ∩ kutu
bi = SRC["iskelet"].BoundBox
KUTU = dict(x=(round(SOL_DIS - KENAR, 3), round(SAG_DIS + KENAR, 3)), y=(round(bi.YMin - 1.0, 3), round(bi.YMax + 1.0, 3)),
            z=(round(ZC - Z_YARI, 3), round(ZC + Z_YARI, 3)))
KB = box(KUTU["x"][0], KUTU["x"][1], KUTU["y"][0], KUTU["y"][1], KUTU["z"][0], KUTU["z"][1])
P1 = SRC["iskelet"].common(KB).removeSplitter()
assert len(P1.Solids) == 1, len(P1.Solids)
P1 = P1.Solids[0]
OY_K = yanak_olc(P1)

# ---------------------------------------------------------------- (2) yigin mastari: eksenel govde (x boyunca), olculer kaynaktan
ax = V(1, 0, 0)
L_KONI = (R_KOL - R_HORN) / math.tan(math.radians(KONI))     # govde r_kol -> horn r_horn, 45 derece
X_KONI = HORN_IC - L_KONI
m = Part.makeCylinder(R_DAYAMA, KOL - DAYAMA, V(DAYAMA, YC, ZC), ax)                 # catal dayamasi (625ZZ ic bilezigine dayanir)
m = m.fuse(Part.makeCylinder(R_KOL, X_KONI - KOL, V(KOL, YC, ZC), ax))              # catal kolu capinda govde (sol yanaga KOL - SOL_IC)
m = m.fuse(Part.makeCone(R_KOL, R_HORN, L_KONI, V(X_KONI, YC, ZC), ax))             # 45 derece gecis
m = m.fuse(Part.makeCylinder(R_HORN, HORN_DIS - HORN_IC, V(HORN_IC, YC, ZC), ax))   # tilt hornu diski (kalinlik ve cap horn'dan)
P2 = m.removeSplitter()
P2 = P2.Solids[0] if len(P2.Solids) == 1 else P2
M_OLCU = dict(dayama_x=hat_x(P2, YC, ZC + 3.6)[0][0], horn_x=hat_x(P2, YC, ZC + 8.0)[0][1], kol_x=hat_x(P2, YC, ZC + 10.0)[0][0])
M_OLCU["genislik_mm"] = round(M_OLCU["horn_x"] - M_OLCU["dayama_x"], 3)

# ---------------------------------------------------------------- karsilastirma ve inis (model): kupon kaynakla ayni mi, mastar yiginla
# ayni genislikte mi; kupon mastarin uzerine (+y'den) inerken ortak hacim (temas sayilmaz) ve dinlenmede en kisa uzaklik


def fark(a, b):
    return None if a is None or b is None else round(max(abs(a[0] - b[0]), abs(a[1] - b[1])), 4)


KARS = {}
for k in OY:
    KARS[k] = dict(kaynak=OY[k]["aralik_mm"], kupon=OY_K[k]["aralik_mm"], sol_fark=fark(OY[k]["sol"], OY_K[k]["sol"]),
                   sag_fark=fark(OY[k]["sag"], OY_K[k]["sag"]))
KARS["mastar_genislik"] = dict(kaynak=YIGIN, kupon=M_OLCU["genislik_mm"], fark=round(abs(YIGIN - M_OLCU["genislik_mm"]), 4))
KARS["mastar_dayama_x"] = dict(kaynak=DAYAMA, kupon=M_OLCU["dayama_x"], fark=round(abs(DAYAMA - M_OLCU["dayama_x"]), 4))
KARS["mastar_horn_x"] = dict(kaynak=HORN_DIS, kupon=M_OLCU["horn_x"], fark=round(abs(HORN_DIS - M_OLCU["horn_x"]), 4))
kars_ok = (all(v["sol_fark"] is not None and v["sol_fark"] <= TOL and v["sag_fark"] <= TOL for k, v in KARS.items() if k in OY)
           and all(KARS[k]["fark"] <= TOL for k in ("mastar_genislik", "mastar_dayama_x", "mastar_horn_x")))
kesilen = round(SRC["iskelet"].common(KB).Volume - P1.Volume, 4)
INIS = {}
for d in (0.0, 2.0, 5.0, 10.0, 16.0, 20.0, 30.0):
    q = P1.copy()
    q.translate(V(0, d, 0))
    INIS["%.0f" % d] = round(q.common(P2).Volume, 4)
dmin = P1.distToShape(P2)[0]
# mastar govdesi kuponun yanak disi bolumune (tabla alti) degiyor mu: yanak ic yuzleri disindaki en kisa uzaklik
govde = P2.common(box(KOL - 0.01, HORN_IC + 0.01, YC - 40, YC + 40, ZC - 40, ZC + 40))
dmin_govde = P1.distToShape(govde)[0]
inis_ok = all(v < 0.01 for v in INIS.values()) and dmin < 1e-3
print("karsilastirma", KARS, kars_ok, "inis", INIS, "dmin", dmin, "govde", dmin_govde)


# ---------------------------------------------------------------- baski yonu, cikti, denetim
def yonlu(s, rot_eksen, aci):
    q = s.copy()
    q.rotate(V(0, 0, 0), rot_eksen, aci)
    b = q.optimalBoundingBox()
    q.translate(V(-(b.XMin + b.XMax) / 2, -(b.YMin + b.YMax) / 2, -b.ZMin))
    return q


B1 = yonlu(P1, V(1, 0, 0), -90.0)          # (0, -1, 0) -> +z: tabla tablada, yanaklar yukari (kafa iskeletinin baski yonu)
B2 = yonlu(P2, V(0, 1, 0), 90.0)           # (-1, 0, 0) -> +z: horn diski tablada, dayama ustte


def baski_kontrol(s):
    m_ = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2)
    alan, gr = 0.0, {}
    for f in m_.Facets:
        zc = sum(p[2] for p in f.Points) / 3
        if f.Normal.z < -math.cos(math.radians(44.0)) and zc > 0.05:
            alan += f.Area
            k = round(zc, 1)
            gr[k] = gr.get(k, 0.0) + f.Area
    en = sorted(gr.items(), key=lambda kv: -kv[1])[:6]
    return dict(cikinti_46ustu_mm2=round(alan, 1), en_buyuk_z_mm2=[(z, round(a, 1)) for z, a in en],
                not_="46 derece ustu asagi bakan yuzler (tablanin ustunde)")


def cikti(s, ad, malzeme, yon):
    stl = os.path.join(HERE, "stl", ad + ".stl")
    bb = s.optimalBoundingBox()
    assert abs(bb.ZMin) < 1e-3 and s.isValid() and len(s.Solids) == 1, ad
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.1).write(stl)
    ms = Mesh.Mesh(stl)
    mb = ms.BoundBox
    sk = dict(hacim_brep_mm3=round(s.Volume, 2), hacim_stl_mm3=round(ms.Volume, 2), hacim_fark_yuzde=round(100.0 * abs(ms.Volume - s.Volume) / s.Volume, 3),
              bb_fark_mm=round(max(abs(a - b) for a, b in zip((mb.XMin, mb.XMax, mb.YMin, mb.YMax, mb.ZMin, mb.ZMax),
                                                               (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))), 4),
              kapali=bool(ms.isSolid()), manifold_disi=bool(ms.hasNonManifolds()), ucgen=ms.CountFacets)
    sk_ok = sk["hacim_fark_yuzde"] < 0.5 and sk["bb_fark_mm"] < 0.02 and sk["kapali"] and not sk["manifold_disi"]
    kab = min(s.Volume, s.Area * 1.6 * 0.5)
    v_eff = kab + 0.25 * max(0.0, s.Volume - kab)
    taban = s.common(box(bb.XMin - 1, bb.XMax + 1, bb.YMin - 1, bb.YMax + 1, -0.01, 0.2)).Volume / 0.2
    olcu = [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)]
    hac = A.YAZICI["kullanilabilir"]
    return dict(stl="tasarim/freecad/kafa/stl/%s.stl" % ad, stl_md5=md5(stl), malzeme=malzeme, yon=yon, olcu_mm=olcu, kati=len(s.Solids),
                gecerli=s.isValid(), hacim_cm3=round(s.Volume / 1000, 2), kutle_100_g=round(s.Volume / 1000 * A.PETG_RHO, 1),
                kutle_tahmini_g=round(v_eff / 1000 * A.PETG_RHO, 1), sure_tahmini_dk=round(v_eff / A.PETG_HACIM_HIZI / 60 * 1.3, 0),
                tabla_temas_mm2=round(taban, 0), baski=baski_kontrol(s), stl_karsilastirma=dict(olcumler=sk, sonuc=sk_ok),
                x2d_sigar=bool(all(a <= b for a, b in zip(sorted(olcu[:2]) + [olcu[2]], sorted(hac[:2]) + [hac[2]]))),
                okul_sigar=bool(max(olcu) <= A.YAZICI_OKUL["hedef"]),
                tahmin_not="tahmini: 4 cevre + %25 dolgu, arayuz.PETG_HACIM_HIZI x 1,3 (test/m7_kuponlari.py ile ayni yontem)")


os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
K1 = cikti(B1, "yanak-kuponu", "PETG (beyaz; kafa iskeletinin malzemesi)", "ters: tabla dilimi tablada, yanaklar yukari (kafa iskeleti gibi)")
K2 = cikti(B2, "yanak-kuponu-mastar", "PETG (beyaz; catal PETG-CF, horn aluminyum: mastar yalniz olcu tasir)",
           "dik: horn diski tablada, dayama ustte")
stl_ok = K1["stl_karsilastirma"]["sonuc"] and K2["stl_karsilastirma"]["sonuc"]
SONUC = dict(
    betik="tasarim/freecad/kafa/yanak_kuponu.py", paket="P10.8 1. basamak (kupon dosyalari)", tarih="2026-11-19",
    karar="karar-kuyrugu.md K54 seçenek c (17.11.2026, P10.9b)",
    kaynak=dict(fcstd="tasarim/freecad/kafa/kafa-montaj.FCStd", md5=md5(FCSTD), parcalar={k: v for k, v in AD.items()},
                hacim_mm3={k: round(v.Volume, 2) for k, v in SRC.items()},
                uretici="kafa_montaj.py (Kafa iskeleti: kafa10_lib.py:290-315; Egme catali: kafa7_parcalar.py:258-279; X_SAG / X_SOL / X_RUL: kafa7_parcalar.py:64-71)"),
    kaynak_olcu=KAYNAK_OLCU, kutu_mm=KUTU, kesilen_kutu_ici_mm3=kesilen,
    mastar=dict(r_dayama=R_DAYAMA, r_kol=R_KOL, r_horn=R_HORN, koni_derece=KONI, olcu=M_OLCU,
                tarif="dayama r_dayama [dayama_x, kol_x] + govde r_kol [kol_x, horn_ic - koni] + 45 derece koni + horn diski r_horn [horn_ic, horn_x]"),
    karsilastirma=dict(tolerans_mm=TOL, olcumler=KARS, sonuc=kars_ok),
    inis=dict(yon="+y (kafa yukaridan iner; giris yolu F10c D1)", ortak_hacim_mm3=INIS, dinlenme_en_kisa_mm=round(dmin, 4),
              govde_ile_kupon_en_kisa_mm=round(dmin_govde, 3), sonuc=inis_ok,
              not_="modelde temas yuzleri: sol yanak ic yuzu <-> dayama, sag yanak ic yuzu <-> horn; ortak hacim 0, bosluk 0"),
    parcalar=[dict(K1, ad="yanak kuponu"), dict(K2, ad="yigin mastari")],
    stl_sonuc=stl_ok, sure_s=round(time.time() - t0, 1))
with open(os.path.join(HERE, "yanak-kuponu.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(SONUC, f, ensure_ascii=False, indent=1)
print("karsilastirma", kars_ok, "inis", inis_ok, "stl", stl_ok, "kupon", K1["olcu_mm"], K1["kutle_tahmini_g"], "g", "mastar", K2["olcu_mm"], K2["kutle_tahmini_g"], "g")
App.closeDocument(doc.Name)
print("bitti %.1f s" % (time.time() - t0))
