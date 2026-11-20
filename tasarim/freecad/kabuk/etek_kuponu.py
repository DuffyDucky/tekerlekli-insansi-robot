# K55 ETEK ON BANDI KUPONU (FreeCAD 1.1, Part; P10.8c, 19.11.2026; planlama/d158/P108c-gunluk.md § 4).
# Sorun: rehber F1 (adim 33, "On sag bant") etek on bandini "yerinin 10 mm onunde yandan (+x) getir, sonra onden iceri (-z) it" diye
# takar; son 10 mm'de engel z +105 L braketinin M3 percin somunu flansi (B-rep 1-8 mm, ~9 mm3; planlama/d158/P108b-olcum/brep-yol.json).
# Rehber "bu bant icin kupon henuz yok" diyor (P10.8a O2: bant_kuponu.py kalibiyla cikmiyordu: braketin basili esi yok, percin somunu
# PETG'ye alüminyumdaki gibi oturmaz, iki parcali yol olculmedi).
# Kupon: GERCEK parcalarin dilimi (kabuk-montaj.FCStd; ekleme yalniz asagida adiyla yazili tasiyicilar):
#   ust parca = "Etek on sag" ∩ KUTU_UST: dudak (z +88 dikisinin dis yarisi), z +105 boss'u ve percin somunu flans cebi, Ø3,4 gecis;
#   alt parca = "Etek orta sag" ∩ KUTU_ALT (dil: dikisin ic yarisi) + "Etek braketi sag z+105" ∩ KUTU_ALT (2 mm dik ayak, Ø5,1 percin
#               somunu deligi) + TASIYICI (ayagin arkasinda sertlik blogu, Ø10 percin bosluklu; ustte ikisini birlestiren plaka).
#   alt parca iki bicimde: (a) delikli: gercek M3 percin somunu (duz flansli, 2 mm Al icin) ayaga percinlenir; (b) flansli: percin
#   somununun CAD sekli (flans Ø7 x 0,8 + govde) ayakla tek parca basilir (percin aleti / somun yoksa; engel ayni olcude).
# Yol (modelde): rehberin iki parcali yolu: ust parca dinlenmeden (dx, 0, +10)'dan yana bacakla (dx -> 0), sonra (0, 0, dz) dz 10 -> 0.
# Ayni yol tam bantla (gercek "Etek on sag" ve gercek engellerle) da olculur; kupon ayni ortak hacim egrisini vermeli.
# Kisit (P10.8c duzeltme turu 1, P108c-kontrol O3): dilim kisa (y 106-136) ve gercek banttan sert; tasiyici gercek braketten sert.
# Elde serbest tutulan dilim flansin ustunden dondurulerek gecirilebilir, gercek bant (234 x 175 mm, z +88 dikisine bagli) gecirilemez:
# "gecti" yalniz hareket kisitliyken (DENEME: once yalniz x, sonra yalniz -z, ust parca dondurulmeden) gercek bant icin kanit sayilir.
# "Gecmedi" gercek bant icin kesin degil (bant esneyebilir): belirsiz, K55 b. Metin JSON'da (sinir, deneme) ve test/README.md'de.
# Malzeme: kuponda percin somunu PETG ayaga takilir (gercekte 2 mm Al): ezilebilir, flans yuksekligi gercektekinden farkli olabilir;
# ilk deneme flansli bicimle (alet istemez).
# Baski: parcalar bantlar gibi ters (dunya -y yukari): ust parcanin ust kesiti, alt parcanin ust plakasi tablada.
# Cikti: kabuk/stl/etek-kuponu-ust.stl, etek-kuponu-alt.stl, etek-kuponu-alt-flansli.stl, kabuk/etek-kuponu.json. Kaynaklar yalniz OKUNUR.
# Calistirma: FC_SCRIPT=<bu betik> freecadcmd ~/.robot-cad/run_fc.py  (yalniz kabuk-montaj.FCStd acilir)
import os, sys, math, json, hashlib, time
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
EB = A.KABUK_ETEK_BRAKET
EM3 = A.M6["etek_braket_m3"]
PC = EM3["percin"]
ZB = EB["z"][2]                                   # 105: on braket
assert ZB > A.ETEK_DIKIS_Z, (ZB, A.ETEK_DIKIS_Z)
XI = EB["x_ic"]                                   # 252: braket dik ayaginin dis yuzu = boss yuzu
YM = EB["m3_y"]                                   # 121: M3 ekseni
ZD = A.ETEK_DIKIS_Z                               # 87,5: on | orta dikisi
W = A.KABUK_BINDIRME                              # 12: dil boyu
AD = dict(ust="Etek on sag", alt="Etek orta sag", braket="Etek braketi sag z+105", somun="Percin somun M3 (Etek braketi sag z+105)",
          civata="Civata M3x14 ISO 7380 (Etek braketi sag z+105)")
TOL = 0.01


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# dilim kutulari: y'de braketin dik ayagi (106,5 ... 136,5) ve M3 ekseni (121) icinde; z +88 boss'lari (y 60 / 85) disarida.
# x'te duvar (257 ... 260) ve boss (252 ... 257) + tasiyici (244 ... 250). z'de dikisin 10 mm alti ... boss'un 19,5 mm ustu.
Y0, Y1 = 106.5, 136.5
KUTU_UST = dict(x=(240.0, 270.0), y=(Y0, Y1 - 0.5), z=(ZD - 10.0, ZB + 25.0))      # ust parca alt plakaya 0,5 mm kala biter
KUTU_ALT = dict(x=(240.0, 270.0), y=(Y0, Y1), z=(ZD - 10.0, ZB + 25.0))
TAS = dict(blok_x=(XI - 8.0, XI - 2.0), percin_bosluk_d=10.0, plaka_y=(Y1, Y1 + 3.0), plaka_x=(240.0, 260.0))   # P10.8c d.t.1 (P108c-kontrol D2): plaka x 240'tan (braket dilimi x 240-244 desteksiz kaliyordu)

doc = App.openDocument(FCSTD)
SRC = {}
for k, ad in AD.items():
    obj = [o for o in doc.Objects if o.Label == ad and hasattr(o, "Shape") and o.Shape.Volume > 1e-3]
    assert len(obj) == 1, (ad, [o.Label for o in obj])
    s = obj[0].Shape.copy()
    s.Placement = obj[0].getGlobalPlacement()
    SRC[k] = s
# z +88 dikis isil gomme somunlari (orta bandin dil boss'unda; dikiste sabit engel adayi) ve on bandin dusuk kopya ekli adlari
ISIL = [o.Shape.copy() for o in doc.Objects if o.Label.startswith("Isil gomme somun M3 (etek z+88 sag)") and hasattr(o, "Shape")]


def kutu_sekil(K):
    return box(K["x"][0], K["x"][1], K["y"][0], K["y"][1], K["z"][0], K["z"][1])


KU, KA = kutu_sekil(KUTU_UST), kutu_sekil(KUTU_ALT)


def tek(s, ad):
    s = s.removeSplitter()
    assert len(s.Solids) == 1, (ad, len(s.Solids))
    return s.Solids[0]


P_UST = tek(SRC["ust"].common(KU), "ust")
P_ORTA = tek(SRC["alt"].common(KA), "orta")
P_BRK = SRC["braket"].common(KA).removeSplitter()
bb_ = P_BRK.BoundBox
assert abs(bb_.XMax - XI) < 1e-6 and bb_.XMin < XI - 1.9, ("braket dilimi", bb_)
# tasiyici: dik ayagin arkasinda (x XI-8 ... XI-2) blok, percin somunu govdesinin ve percin aletinin cokertme bosluguna Ø10 delik;
# ustte (y 136,5 ... 139,5) orta bant dilimini ve braketi birlestiren plaka. Ust parcanin yoluna girmez (yol x >= XI, y <= 136).
blok = box(TAS["blok_x"][0], TAS["blok_x"][1], Y0, Y1, EB["z"][2] - EB["en"] / 2, EB["z"][2] + EB["en"] / 2)
blok = blok.cut(Part.makeCylinder(TAS["percin_bosluk_d"] / 2, 20.0, V(XI - 15.0, YM, ZB), V(1, 0, 0)))
plaka = box(TAS["plaka_x"][0], TAS["plaka_x"][1], TAS["plaka_y"][0], TAS["plaka_y"][1], KUTU_ALT["z"][0], KUTU_ALT["z"][1])
P_ALT = tek(P_ORTA.fuse([P_BRK, blok, plaka]), "alt")
somun = SRC["somun"].copy()
P_ALT_F = tek(P_ALT.fuse(somun), "alt flansli")
for ad, s in (("ust", P_UST), ("orta", P_ORTA), ("alt", P_ALT), ("alt_f", P_ALT_F)):
    b = s.BoundBox
    print(ad, "bb", [round(v, 2) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)], "V", round(s.Volume, 1))


# ---------------------------------------------------------------- olcum: katmanlar (dudak / dil / bosluk) ve boss / cep, kaynak <-> kupon
def hat(sh, p0, p1, i):
    c = sh.common(Part.makeLine(V(*p0), V(*p1)))
    return sorted(tuple(sorted((round(e.Vertexes[0].Point[i], 3), round(e.Vertexes[-1].Point[i], 3)))) for e in c.Edges)


OLC_Z = dict(dikis_alti=ZD - 5.0, dil_orta=ZD + W / 2, boss_alt=ZB - 4.5, cep=ZB - 3.0, boss_ust=ZB + 4.5, boss_ustu=ZB + 10.0)
OLC_Y = (Y0 + 4.0, YM, Y1 - 4.0)


def olc(ust, alt):
    o = {}
    for y in OLC_Y:
        for zk, z in OLC_Z.items():
            o["y%.1f_%s" % (y, zk)] = dict(ust=[list(r) for r in hat(ust, (240.0, y, z), (270.0, y, z), 0)],
                                          alt=[list(r) for r in hat(alt, (240.0, y, z), (270.0, y, z), 0)])
    return o


OS_ = olc(SRC["ust"], SRC["alt"].fuse(SRC["braket"]))
OK_ = olc(P_UST, P_ORTA.fuse(P_BRK))


def fark(a, b):
    if len(a) != len(b):
        return None
    return round(max([0.0] + [max(abs(x[0] - y[0]), abs(x[1] - y[1])) for x, y in zip(a, b)]), 4)


KARS = {k: dict(ust_fark=fark(OS_[k]["ust"], OK_[k]["ust"]), alt_fark=fark(OS_[k]["alt"], OK_[k]["alt"])) for k in OS_}
kars_ok = all(v["ust_fark"] is not None and v["alt_fark"] is not None and v["ust_fark"] <= TOL and v["alt_fark"] <= TOL for v in KARS.values())
_dil = OK_["y%.1f_dil_orta" % YM]
DIKIS = dict(dudak_mm=round(_dil["ust"][-1][1] - _dil["ust"][-1][0], 3), dil_mm=round(_dil["alt"][-1][1] - _dil["alt"][-1][0], 3),
             bosluk_mm=round(_dil["ust"][-1][0] - _dil["alt"][-1][1], 3), arayuz_bosluk_mm=A.KABUK_BINDIRME_BOSLUK)
kesilen = round(SRC["ust"].common(KU).Volume - P_UST.Volume, 4)


# ---------------------------------------------------------------- yol: rehberin iki parcali yolu, kuponda ve tam modelde
def ortak(hareketli, engeller, ofs):
    h = hareketli.copy()
    h.translate(ofs)
    hb = h.BoundBox
    out = {}
    for ad, e in engeller:
        if not hb.intersect(e.BoundBox):
            continue
        v = h.common(e).Volume
        if v > 1e-3:
            out[ad] = round(v, 3)
    return out


Z_ADIM = [10.0 - 0.5 * i for i in range(21)]                         # z bacagi: dz 10 -> 0 (iceri itme)
X_ADIM = [240.0, 160.0, 80.0, 40.0, 20.0, 10.0, 6.0, 4.0, 2.0, 1.0, 0.0]   # yan bacak: dx -> 0, z +10'da
ENG_K = [("alt parca (orta bant dilimi + braket ayagi + tasiyici)", P_ALT), ("percin somunu (CAD)", somun)] + \
        [("isil gomme z+88 #%d" % i, s) for i, s in enumerate(ISIL)]
ENG_T = [("Etek orta sag (tam)", SRC["alt"]), ("Etek braketi sag z+105 (tam)", SRC["braket"]), ("percin somunu (CAD)", somun)] + \
        [("isil gomme z+88 #%d" % i, s) for i, s in enumerate(ISIL)]


def yol(hareketli, engeller):
    yan = {"%.0f" % dx: ortak(hareketli, engeller, V(dx, 0, 10.0)) for dx in X_ADIM}
    ic = {"%.1f" % dz: ortak(hareketli, engeller, V(0, 0, dz)) for dz in Z_ADIM}
    return dict(yan_bacak_z10=yan, z_bacagi=ic)


YOL_K = yol(P_UST, ENG_K)
YOL_T = yol(SRC["ust"], ENG_T)


def ozet(y, anahtar):
    """z bacaginda engelin goruldugu dz araligi (mm) ve en buyuk ortak hacim."""
    zs = [float(k) for k, v in y["z_bacagi"].items() if any(anahtar in a for a in v)]
    vs = [v for d in y["z_bacagi"].values() for a, v in d.items() if anahtar in a]
    return dict(dz_ilk=min(zs) if zs else None, dz_son=max(zs) if zs else None, en_cok_mm3=max(vs) if vs else 0.0)


Z_SOMUN_K, Z_SOMUN_T = ozet(YOL_K, "percin"), ozet(YOL_T, "percin")
# kupon ile tam model: her adimda percin somunuyla ortak hacim ayni mi; kuponda baska engel (dil, tasiyici) yok mu
egri_ayni = all(abs(YOL_K["z_bacagi"][k].get("percin somunu (CAD)", 0.0) - YOL_T["z_bacagi"][k].get("percin somunu (CAD)", 0.0)) < 0.01
                for k in YOL_K["z_bacagi"])
kupon_baska = sorted({a for part in ("yan_bacak_z10", "z_bacagi") for d in YOL_K[part].values() for a in d if "percin" not in a})
tam_baska = sorted({a for part in ("yan_bacak_z10", "z_bacagi") for d in YOL_T[part].values() for a in d if "percin" not in a})
yan_serbest_k = all(not d for d in YOL_K["yan_bacak_z10"].values())
dinlenme = dict(kupon=ortak(P_UST, ENG_K, V(0, 0, 0)), tam=ortak(SRC["ust"], ENG_T, V(0, 0, 0)))
# alt parca (a) delikli: percin somunu yokken yol serbest olmali (engel yalniz somun); (b) flansli: alt parca ile ayni egri
YOL_KD = yol(P_UST, [("alt parca delikli (somunsuz)", P_ALT)])
YOL_KF = yol(P_UST, [("alt parca flansli", P_ALT_F)])
delikli_serbest = all(not d for p in YOL_KD.values() for d in p.values())
flansli_egri = all(abs(YOL_KF["z_bacagi"][k].get("alt parca flansli", 0.0) - YOL_K["z_bacagi"][k].get("percin somunu (CAD)", 0.0)) < 0.01
                   for k in YOL_K["z_bacagi"])
print("kars", kars_ok, "dikis", DIKIS, "somun kupon", Z_SOMUN_K, "tam", Z_SOMUN_T, "egri_ayni", egri_ayni, "kupon_baska", kupon_baska,
      "tam_baska", tam_baska, "yan_serbest", yan_serbest_k, "dinlenme", dinlenme, "delikli_serbest", delikli_serbest, "flansli_egri", flansli_egri)


# ---------------------------------------------------------------- baski yonu (bant gibi ters: dunya -y yukari), cikti
def ters(s):
    q = s.copy()
    q.rotate(V(0, 0, 0), V(1, 0, 0), 90.0)          # (0, -1, 0) -> +z: dunya -y baski yukari
    q.rotate(V(0, 0, 0), V(1, 0, 0), 180.0)
    b = q.BoundBox
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


def cikti(s, ad, yon, malz):
    stl = os.path.join(HERE, "stl", ad + ".stl")
    bb = s.BoundBox
    assert abs(bb.ZMin) < 1e-3 and s.isValid() and len(s.Solids) == 1, ad
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.1).write(stl)
    ms = Mesh.Mesh(stl)
    mb = ms.BoundBox
    sk = dict(hacim_brep_mm3=round(s.Volume, 2), hacim_stl_mm3=round(ms.Volume, 2),
              hacim_fark_yuzde=round(100.0 * abs(ms.Volume - s.Volume) / s.Volume, 3),
              bb_fark_mm=round(max(abs(a - b) for a, b in zip((mb.XMin, mb.XMax, mb.YMin, mb.YMax, mb.ZMin, mb.ZMax),
                                                               (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))), 4),
              kapali=bool(ms.isSolid()), manifold_disi=bool(ms.hasNonManifolds()), ucgen=ms.CountFacets)
    sk_ok = sk["hacim_fark_yuzde"] < 0.5 and sk["bb_fark_mm"] < 0.02 and sk["kapali"] and not sk["manifold_disi"]
    kab = min(s.Volume, s.Area * 1.6 * 0.5)
    v_eff = kab + 0.25 * max(0.0, s.Volume - kab)
    taban = s.common(box(bb.XMin - 1, bb.XMax + 1, bb.YMin - 1, bb.YMax + 1, -0.01, 0.2)).Volume / 0.2
    olcu = [round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)]
    return dict(stl="tasarim/freecad/kabuk/stl/%s.stl" % ad, stl_md5=md5(stl), malzeme=malz, yon=yon, olcu_mm=olcu, kati=len(s.Solids),
                gecerli=s.isValid(), hacim_cm3=round(s.Volume / 1000, 2), kutle_100_g=round(s.Volume / 1000 * A.PETG_RHO, 1),
                kutle_tahmini_g=round(v_eff / 1000 * A.PETG_RHO, 1), sure_tahmini_dk=round(v_eff / A.PETG_HACIM_HIZI / 60 * 1.3, 0),
                tabla_temas_mm2=round(taban, 0), baski=baski_kontrol(s), stl_karsilastirma=dict(olcumler=sk, sonuc=sk_ok),
                tahmin_not="tahmini: 4 cevre + %25 dolgu, arayuz.PETG_HACIM_HIZI x 1,3 (test/m7_kuponlari.py ile ayni yontem)")


ok_yol = (kars_ok and egri_ayni and not kupon_baska and yan_serbest_k and not dinlenme["kupon"] and delikli_serbest and flansli_egri
          and Z_SOMUN_K["en_cok_mm3"] > 0)
if not ok_yol:
    raise SystemExit("HATA: kupon rehber yolunu tam modelle ayni denemiyor: kars %s egri %s kupon_baska %s yan %s dinlenme %s delikli %s "
                     "flansli %s somun %s" % (kars_ok, egri_ayni, kupon_baska, yan_serbest_k, dinlenme["kupon"], delikli_serbest,
                                              flansli_egri, Z_SOMUN_K))
os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
# P10.8c duzeltme turu 1 (P108c-kontrol O3, D2, D3): sinir, deneme yontemi ve kabul olcutu, malzeme notu (README ile ayni metin)
SINIR = ("Dilim kısa (y 106,5–136) ve gerçek banttan serttir; taşıyıcı gerçek braketten serttir. Elde serbest tutulan dilim flanşın üstünden "
         "döndürülerek geçirilebilir, gerçek bant (234 × 175 mm, z +88 dikişine bağlı) geçirilemez. Bu yüzden 'geçti' yalnız aşağıdaki "
         "kısıtlı hareketle gerçek bant için kanıt sayılır. 'Geçmedi' gerçek bant için kesin değildir (gerçek bant esneyebilir): belirsiz, "
         "K55 b. Kupon sağ banttan kesildi; sol bant için sonuç ayna çıkarımıdır.")
MALZEME_NOTU = ("Kuponda perçin somunu PETG ayağa takılır, gerçek parçada ayak 2 mm alüminyumdur: sıkınca ayak ezilebilir ya da çatlayabilir, "
                "flanş yüksekliği gerçektekinden farklı olabilir. İlk deneme flanşlı biçimle (alet istemez); delikli biçim perçin somunu ve "
                "aleti gelince, flanşın ayak üstündeki yüksekliği kumpasla ölçülerek (tasarım %.1f mm)." % PC["flans_t"])
DENEME = dict(
    hazirlik=["Alt parça (ilk deneme flanşlı biçim) üst plakası alta gelecek şekilde mengeneye ya da masaya kıskaçla sabitlenir; dil ve braket "
              "ayağı serbest kalır.",
              "Üst parçanın dış yüzü (dudak yüzü) düz bir takoza (cetvel ya da tahta blok) bant / yapıştırıcıyla tutturulur; üst parça yalnız "
              "takozdan itilir, elle eğilmez, döndürülmez. Takoz yüzü alt parçanın dış duvarına paralel tutulur."],
    hareket=["1. Üst parçayı yerinin 10 mm önünde (dikişten 10 mm uzakta) alt parçanın +x yanına koy; yalnız x ekseninde (−x yönünde) "
             "kaydırarak duvar hizasına getir. Model: bu bacak serbest.",
             "2. Yalnız −z yönünde (dikişe doğru) 10 mm it; takoz duvara paralel kalır, üst parça dönmez. Model: dz %s–%s mm arasında perçin "
             "somunu flanşı ile en çok %s mm³ ortak hacim." % (str(Z_SOMUN_K["dz_ilk"]).replace(".", ","), str(Z_SOMUN_K["dz_son"]).replace(".", ","),
                                                              str(round(Z_SOMUN_K["en_cok_mm3"], 1)).replace(".", ","))],
    gecti="Elle itişle (alet ve çekiç yok) dudak dikişe oturur: dikiş aralığı ≤ 0,5 mm (sentil), boss deliği somunla eksenli (M3×14 elle "
          "girer); flanşta, boss'ta ve dudakta beyaz iz, çatlak ya da kalıcı eğilme yok. Üç kez sök-tak, aynı sonuç.",
    gecmedi="Elle itişle oturmaz, ancak üst parça döndürülerek / eğilerek geçer, ya da beyazlama / çatlak çıkar. Sonuç belirsiz sayılır "
            "(gerçek bant esneyebilir): K55 b ya da tam bantla deneme.",
    kayit="tasarim/freecad/test/README.md 'K55 etek ön bandı kuponu' bölümündeki tabloya: tarih, malzeme, biçim (flanşlı / delikli), "
          "hareket 1 ve 2 sonucu, takıldığı dz (mm), dikiş aralığı, iz / çatlak, not.",
    karar="Geçti: K55 a etek ön için kalır; rehber F1 'kuponla denenmedi' notu 'kuponla denendi (tarih)' olarak yeniden yazılır. "
          "Geçmedi: belirsiz; K55 b (tasarım değişikliği) ya da gerçek bantla deneme, karar Ahmet'te.",
    baski="PETG, bant yönünde (ters). Üst parçanın tablaya teması dar (3 × ≈ 36 mm, boy 29,5 mm): brim (≥ 5 mm) önerilir.")
MALZ = "PETG (beyaz; bantlarin malzemesi)"
K_UST = cikti(ters(P_UST), "etek-kuponu-ust", "ters: dilimin ust kesiti tablada (etek bantlari gibi ust plaka tarafi asagi)", MALZ)
K_ALT = cikti(ters(P_ALT), "etek-kuponu-alt", "ters: ust plaka tablada", MALZ)
K_ALTF = cikti(ters(P_ALT_F), "etek-kuponu-alt-flansli", "ters: ust plaka tablada; percin somunu esi tek parca", MALZ)
stl_ok = all(k["stl_karsilastirma"]["sonuc"] for k in (K_UST, K_ALT, K_ALTF))
SONUC = dict(
    betik="tasarim/freecad/kabuk/etek_kuponu.py", paket="P10.8c (kupon dosyasi; basilmadi)", tarih="2026-11-19",
    karar="karar-kuyrugu.md K55 secenek a; rehber F1 (adim 33) On sag bant iki parcali yolu",
    kaynak=dict(fcstd="tasarim/freecad/kabuk/kabuk-montaj.FCStd", md5=md5(FCSTD), parcalar=AD,
                hacim_mm3={k: round(s.Volume, 2) for k, s in SRC.items()}, uretici="kabuk_montaj.py (etek: kabuk_parcalar.py, braket K2)",
                dikis_z=ZD, dil_mm=W, braket_z=ZB, braket_x_ic=XI, m3_y=YM, percin=PC, cep_pay=EM3["cep_pay"]),
    kutu_mm=dict(ust=KUTU_UST, alt=KUTU_ALT), tasiyici=TAS, kesilen_kutu_ici_mm3=kesilen,
    kaynak_olcu=OS_, karsilastirma=dict(tolerans_mm=TOL, olcumler=KARS, sonuc=kars_ok, dikis=DIKIS),
    yol=dict(tanim="rehber F1 'On sag bant': yerinin 10 mm onunde yandan (+x) getir, sonra onden iceri (-z) it. Ust parca dinlenmeden "
                   "(dx, 0, +10) -> (0, 0, +10) -> (0, 0, 0); ortak hacim > 0,001 mm3 sayilir (B-rep)",
             kupon=YOL_K, tam_model=YOL_T, somun_kupon=Z_SOMUN_K, somun_tam=Z_SOMUN_T, egri_ayni=egri_ayni, kupon_baska_engel=kupon_baska,
             tam_baska_engel=tam_baska, yan_bacak_serbest=yan_serbest_k, dinlenme=dinlenme,
             alt_delikli_somunsuz_serbest=delikli_serbest, alt_flansli_ayni_egri=flansli_egri,
             p108b_brep="planlama/d158/P108b-olcum/brep-yol.json etek_on_sag: kalk (+z) somun 1-8 mm, 9,4 mm3; yan bacak serbest",
             not_="kupon ve tam model ayni egri: kupon rehberin yolunu dener (P10.8a bant kuponunun yaptigi hata burada yok)"),
    parcalar=[dict(K_UST, ad="ust parca (Etek on sag dilimi: dudak, z +105 boss'u, flans cebi)"),
              dict(K_ALT, ad="alt parca delikli (Etek orta sag dilimi: dil; braket dik ayagi Ø%.1f; tasiyici)" % PC["delik"]),
              dict(K_ALTF, ad="alt parca flansli (delikli + percin somunu CAD sekli tek parca)")],
    sinir=SINIR, deneme=DENEME, malzeme_notu=MALZEME_NOTU,
    gerekenler=["M3 percin somunu, duz flansli (2 mm Al icin; flans Ø%.1f x %.1f) + percin aleti: alt parca delikli icin" % (PC["flans_d"], PC["flans_t"]),
                "M3x14 ISO 7380 (oturdu mu: boss -> somun)", "kumpas (flansin ayak ustundeki yuksekligi; tasarim %.1f mm)" % PC["flans_t"]],
    stl_sonuc=stl_ok, sure_s=round(time.time() - t0, 1))
with open(os.path.join(HERE, "etek-kuponu.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(SONUC, f, ensure_ascii=False, indent=1)
print("karsilastirma", kars_ok, "stl", stl_ok, "ust", K_UST["olcu_mm"], K_UST["kutle_tahmini_g"], "g", "alt", K_ALT["olcu_mm"],
      K_ALT["kutle_tahmini_g"], "g")
App.closeDocument(doc.Name)
print("bitti %.1f s" % (time.time() - t0))
