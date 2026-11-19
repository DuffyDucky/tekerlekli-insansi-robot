# K55 a BANT KUPONU (FreeCAD 1.1, Part; P10.8 1. basamak, 19.11.2026). Karar: karar-kuyrugu.md K55 "dört bant için geçici çözüm a
# ('bandı hafifçe esneterek dili alttaki bandın arkasına sok'), baskı kuponunda denenir; kupon zorlarsa b (geometri)".
# Sorun (F10d-gunluk.md §11.5): ust bant alttaki bandin 12 mm bindirme diline (kabuk_parcalar.py:7-11) hicbir duz yoldan girmiyor;
# gogus bandinda dogal yol (+y'den iniş) yalniz son 13 mm'de orta bandin diliyle ortak hacimli (govde yukari genisliyor).
# Kupon: gercek iki bandin dikis dilimi. kabuk-montaj.FCStd'deki GERCEK "Govde orta bandi sag" ∩ KUTU (alt parca: dil ustte) ve
# "Gogus bandi sag" ∩ KUTU (ust parca: dis yari dudagi altta). Ekleme yok, kesilen yok; arayuz.GOVDE_DIKIS / KABUK_BINDIRME'den yalniz
# kutu siniri okunur. Kabuk degisirse kupon da degisir; JSON'daki karsilastirma (kupon <-> kaynak) ve inis olcumu farki yakalar.
# Neden gogus | orta (sag): K55'in dort bandindan duz iniş yolunda yalniz dil engeli olan bant (omuz: rulman kapagi, etek on: percin
# somunu, cerceve: gogus bandi / ekran); dil, bosluk ve duvar butun bantlarda ayni (KABUK_BINDIRME 12, BOSLUK 0,25, KABUK_T 3).
# Kisit: dilim kisa (alt 24, ust 20 mm), gercek banttan esnek; kupon gecerse gercek bant icin kesin degil, kalirsa gercek bant da kalir.
# Baski: bantlarin baski yonunde (dik, alt kenari tablada; kabuk_parcalar BASKI). Cikti: kabuk/stl/bant-kuponu-alt.stl,
# kabuk/stl/bant-kuponu-ust.stl, kabuk/bant-kuponu.json. Kaynaklar yalniz OKUNUR.
# Calistirma: FC_SCRIPT=<bu betik> freecadcmd ~/.robot-cad/run_fc.py  (yalniz kabuk-montaj.FCStd acilir; ~1 dk)
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
FCSTD = os.path.join(HERE, "kabuk-montaj.FCStd")
ALT, USTB = "Govde orta bandi sag", "Gogus bandi sag"
Y_D = A.GOVDE_DIKIS[3]                 # orta | gogus dikisi (GOVDE_BANT: alt, uzatma1, uzatma2, orta, gogus, omuz)
W = A.KABUK_BINDIRME                   # 12: dil boyu
ALT_PAY, UST_PAY = 10.0, 8.0           # mm: dikisin altinda (alt parca) / dilin ustunde (ust parca) tam duvar
TOL = 0.01


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def hat(sh, p0, p1, i):
    """p0 -> p1 hattinin sekil icindeki araliklari, i. koordinata gore [(a, b), ...]."""
    c = sh.common(Part.makeLine(V(*p0), V(*p1)))
    return sorted(tuple(sorted((round(e.Vertexes[0].Point[i], 3), round(e.Vertexes[-1].Point[i], 3)))) for e in c.Edges)


# gogus ekrani cebinin alt kenari (cep, gogus duzleminde; kabuk_parcalar.py:96-98): ust parca cebin altinda kalmali
_c15 = math.cos(math.radians(A.GOGUS_EGIM))
CEP_ALT_Y = A.GOGUS_EKRAN_Y - A.GOGUS_EKRAN["cep"][1] / 2 * _c15
Y0, Y1 = Y_D - ALT_PAY, Y_D + W + UST_PAY
assert Y1 < CEP_ALT_Y - 1.0, (Y1, CEP_ALT_Y)

doc = App.openDocument(FCSTD)
SRC = {}
for ad in (ALT, USTB):
    obj = [o for o in doc.Objects if o.Label == ad and hasattr(o, "Shape") and o.Shape.Volume > 1e-3]
    assert len(obj) == 1, (ad, [o.Label for o in obj])
    SRC[ad] = obj[0].Shape.copy()
KUTU = dict(x=(-200.0, 200.0), y=(Y0, Y1), z=(-200.0, 200.0))
KB = box(KUTU["x"][0], KUTU["x"][1], Y0, Y1, KUTU["z"][0], KUTU["z"][1])
P = {}
for ad in (ALT, USTB):
    s = SRC[ad].common(KB).removeSplitter()
    assert len(s.Solids) == 1, (ad, len(s.Solids))
    P[ad] = s.Solids[0]
    b = P[ad].optimalBoundingBox()
    print(ad, "dilim bb", [round(v, 2) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)], "V", round(P[ad].Volume, 1))

# ---------------------------------------------------------------- olcum: duvar katmanlari (dis yari / dil / bosluk) uc hatta, uc yukseklikte
# yan (z 0, +x yonu), on (x 60, +z) ve arka (x 100, -z; servis kapagi x < 80'de, kapak alt bandin oyugu): her hatta parca araliklari
HATLAR = dict(yan=((0.0, None, 0.0), (200.0, None, 0.0), 0), on=((60.0, None, 0.0), (60.0, None, 200.0), 2),
              arka=((100.0, None, 0.0), (100.0, None, -200.0), 2))
YUK = dict(dikis_alti=Y_D - 5.0, dil_orta=Y_D + W / 2, dil_ustu=Y_D + W + 4.0)


def olc(alt, ust):
    o = {}
    for hk, (p0, p1, i) in HATLAR.items():
        for yk, y in YUK.items():
            a = [list(r) for r in hat(alt, (p0[0], y, p0[2]), (p1[0], y, p1[2]), i)]
            u = [list(r) for r in hat(ust, (p0[0], y, p0[2]), (p1[0], y, p1[2]), i)]
            r_ = dict(alt=a, ust=u)
            if yk == "dil_orta" and a and u:            # dil kalinligi, bosluk (dil dis yuzu ile ust dudak ic yuzu), dudak kalinligi
                da, du = a[-1] if i == 0 or p1[i] > 0 else a[0], u[-1] if i == 0 or p1[i] > 0 else u[0]
                ters = not (i == 0 or p1[i] > 0)
                r_["dil_mm"] = round(da[1] - da[0], 3)
                r_["dudak_mm"] = round(du[1] - du[0], 3)
                r_["bosluk_mm"] = round((da[0] - du[1]) if ters else (du[0] - da[1]), 3)
            o["%s_%s" % (hk, yk)] = r_
    return o


OS_ = olc(SRC[ALT], SRC[USTB])
OK_ = olc(P[ALT], P[USTB])


def fark(a, b):
    if len(a) != len(b):
        return None
    return round(max([0.0] + [max(abs(x[0] - y[0]), abs(x[1] - y[1])) for x, y in zip(a, b)]), 4)


KARS = {k: dict(alt_fark=fark(OS_[k]["alt"], OK_[k]["alt"]), ust_fark=fark(OS_[k]["ust"], OK_[k]["ust"]),
                bosluk_kaynak=OS_[k].get("bosluk_mm"), bosluk_kupon=OK_[k].get("bosluk_mm")) for k in OS_}
kars_ok = all(v["alt_fark"] is not None and v["ust_fark"] is not None and v["alt_fark"] <= TOL and v["ust_fark"] <= TOL for v in KARS.values())
kesilen = {ad: round(SRC[ad].common(KB).Volume - P[ad].Volume, 4) for ad in P}

# ---------------------------------------------------------------- inis (model): ust parca +y'den (yukaridan) iner; d = dinlenmeden yukarida
# kalan boy. Kaynak bantlarla kupon dilimi ayni egriyi vermeli (dilim gercek geometri)
INIS = {}
for d in (0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 13.0, 14.0, 16.0):
    q = P[USTB].copy()
    q.translate(V(0, d, 0))
    INIS["%.1f" % d] = round(q.common(P[ALT]).Volume, 3)
dinlenme = round(P[USTB].common(P[ALT]).Volume, 4)
_ds = sorted(float(k) for k in INIS)
serbest = next((d for d in _ds if all(INIS["%.1f" % e] < 0.01 for e in _ds if e >= d)), None)   # bu d'den yukarisi hep serbest


# girisim (radyal): ust parcanin dudak ic yuzu ile dilin dis yuzu arasi, ust parca d kadar yukaridayken (dudagin alt ucu dil hizasinda)
def girisim(d):
    out = {}
    for hk, (p0, p1, i) in HATLAR.items():
        y = Y_D + d + 1.0                                   # dudagin alt ucunun 1 mm ustu
        a = hat(P[ALT], (p0[0], y, p0[2]), (p1[0], y, p1[2]), i)
        u = hat(P[USTB], (p0[0], y - d, p0[2]), (p1[0], y - d, p1[2]), i)     # ust parca d yukari: kendi y - d yuksekligi
        if not a or not u:
            out[hk] = None
            continue
        ters = not (i == 0 or p1[i] > 0)
        da, du = (a[0], u[0]) if ters else (a[-1], u[-1])
        out[hk] = round((da[0] - du[1]) if ters else (du[0] - da[1]), 3)      # < 0: girisim (dudak dili ezmeli / esnemeli)
    return out


GIRISIM = {"%.0f" % d: girisim(d) for d in (2.0, 6.0, 10.0)}

# rehber yolu (F3 adim 35 "Gogus bandi sagi +x'ten getir"; P10.8a duzeltme 1, 19.11.2026): ust parca dinlenme yuksekliginde (dudagin alt kenari
# alt parcanin dis yari omzunda), dinlenmeden +x'te dx kadar uzakta. Kupon diliminde ayni yol denenebilir (omuz y'yi tutar); F10d 11.5 tam
# bantla +x 1-159 mm ortak hacim, 173 mm'de ayrilma
INIS_X = {}
for dx in (1.0, 2.0, 5.0, 10.0, 20.0, 40.0, 80.0, 120.0, 150.0, 160.0, 170.0, 175.0, 180.0, 200.0):
    q = P[USTB].copy()
    q.translate(V(dx, 0, 0))
    INIS_X["%.0f" % dx] = round(q.common(P[ALT]).Volume, 3)
_dx = sorted(float(k) for k in INIS_X)
serbest_x = next((d for d in _dx if all(INIS_X["%.0f" % e] < 0.01 for e in _dx if e >= d)), None)
print("kars", kars_ok, "inis", INIS, "dinlenme", dinlenme, "girisim", GIRISIM, "inis_x", INIS_X, "serbest_x", serbest_x)


# ---------------------------------------------------------------- baski yonu (+y yukari), cikti, denetim
def yonlu(s):
    q = s.copy()
    q.rotate(V(0, 0, 0), V(1, 0, 0), 90.0)         # (0, 1, 0) -> +z
    b = q.optimalBoundingBox()
    q.translate(V(-(b.XMin + b.XMax) / 2, -(b.YMin + b.YMax) / 2, -b.ZMin))
    return q


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


def cikti(s, ad, yon):
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
    return dict(stl="tasarim/freecad/kabuk/stl/%s.stl" % ad, stl_md5=md5(stl), malzeme="PETG (beyaz; bantlarin malzemesi)", yon=yon,
                olcu_mm=olcu, kati=len(s.Solids), gecerli=s.isValid(), hacim_cm3=round(s.Volume / 1000, 2),
                kutle_100_g=round(s.Volume / 1000 * A.PETG_RHO, 1), kutle_tahmini_g=round(v_eff / 1000 * A.PETG_RHO, 1),
                sure_tahmini_dk=round(v_eff / A.PETG_HACIM_HIZI / 60 * 1.3, 0), tabla_temas_mm2=round(taban, 0), baski=baski_kontrol(s),
                stl_karsilastirma=dict(olcumler=sk, sonuc=sk_ok),
                x2d_sigar=bool(all(a <= b for a, b in zip(sorted(olcu[:2]) + [olcu[2]], sorted(hac[:2]) + [hac[2]]))),
                okul_sigar=bool(max(olcu[:2]) <= A.YAZICI_OKUL["hedef"] and olcu[2] <= A.YAZICI_OKUL["hedef"]),
                tahmin_not="tahmini: 4 cevre + %25 dolgu, arayuz.PETG_HACIM_HIZI x 1,3 (test/m7_kuponlari.py ile ayni yontem); ince duvarda hemen hepsi cevre")


os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
K_ALT = cikti(yonlu(P[ALT]), "bant-kuponu-alt", "dik: dilimin alt kesiti tablada, dil yukari (orta bant gibi)")
K_UST = cikti(yonlu(P[USTB]), "bant-kuponu-ust", "dik: dudagin alt kenari tablada (gogus bandi gibi)")
stl_ok = K_ALT["stl_karsilastirma"]["sonuc"] and K_UST["stl_karsilastirma"]["sonuc"]
SONUC = dict(
    betik="tasarim/freecad/kabuk/bant_kuponu.py", paket="P10.8 1. basamak (kupon dosyalari)", tarih="2026-11-19",
    karar="karar-kuyrugu.md K55 seçenek a (17.11.2026, P10.9b)",
    kaynak=dict(fcstd="tasarim/freecad/kabuk/kabuk-montaj.FCStd", md5=md5(FCSTD), alt=ALT, ust=USTB,
                hacim_mm3={ad: round(SRC[ad].Volume, 2) for ad in SRC}, uretici="kabuk_montaj.py (bantlar: kabuk_parcalar.py:128-165)",
                dikis_y=Y_D, dil_mm=W, bosluk_arayuz_mm=A.KABUK_BINDIRME_BOSLUK, duvar_mm=A.KABUK_T, cep_alt_y=round(CEP_ALT_Y, 2)),
    kutu_mm=KUTU, kesilen_kutu_ici_mm3=kesilen,
    kaynak_olcu=OS_, karsilastirma=dict(tolerans_mm=TOL, olcumler=KARS, sonuc=kars_ok),
    inis=dict(yon="ust parca +y'den iner (d: dinlenmeden yukarida kalan boy, mm)", ortak_hacim_mm3=INIS, dinlenme_ortak_mm3=dinlenme,
              serbest_d_mm=serbest, girisim_mm=GIRISIM,
              not_="girisim < 0: dudak ic yuzu dilin dis yuzunun icinde (dudak disa / dil ice esnemeli); F10d §11.5 gogus bandi +y 1-13 mm ile karsilastir"),
    inis_x=dict(yon="rehber F3 (adim 35) yolu: ust parca dinlenme yuksekliginde, +x'ten gelir (dx: dinlenmeden +x'te kalan boy, mm)",
                ortak_hacim_mm3=INIS_X, serbest_dx_mm=serbest_x,
                not_="F10d §11.5 tam bant +x: orta bant 1-159 mm, 173 mm'de ayrilma; kupon dilimi ayni egriyi vermeli"),
    parcalar=[dict(K_ALT, ad="alt parca (orta bant dilimi, dil)"), dict(K_UST, ad="ust parca (gogus bandi dilimi, dudak)")],
    stl_sonuc=stl_ok, sure_s=round(time.time() - t0, 1))
with open(os.path.join(HERE, "bant-kuponu.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(SONUC, f, ensure_ascii=False, indent=1)
print("karsilastirma", kars_ok, "stl", stl_ok, "alt", K_ALT["olcu_mm"], K_ALT["kutle_tahmini_g"], "g", "ust", K_UST["olcu_mm"], K_UST["kutle_tahmini_g"], "g")
App.closeDocument(doc.Name)
print("bitti %.1f s" % (time.time() - t0))
