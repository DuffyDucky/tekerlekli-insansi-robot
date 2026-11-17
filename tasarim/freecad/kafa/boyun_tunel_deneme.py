# Boyun tuneli DENEME PARCASI (FreeCAD 1.1, Part; P10.7b2g, 17.11.2026). KT4: kablo demeti kurulmadan once fislerin boyun tunelinden
# gecip gecmedigi bu kucuk baskiyla elle denenir (kablolama-on-kararlar.md §4 K14, rehber K14 adimi). Parca montaja GIRMEZ.
# Kaynak: kafa/kafa-montaj.FCStd (kafa_montaj.py ciktisi; 1,58 m Govde + Pan gruplari kafa7_parcalar.py'den aynen) icindeki GERCEK
# "Servo yuvasi" + "Rulman yuvasi" + "Boyun mili" (ev pozu). Kesit elle cizilmez: deneme parcasi = (uc parcanin birlesimi + iki baski
# eki) ∩ KUTU. Tunel uc parcaya yayiliyor: alt cikis + arka kanal + kanal ustu (servo yuvasi) -> kablo odasi (servo yuvasi ustu ile
# rulman yuvasi arasi halka) -> mil penceresi (boyun mili duvari) -> mil ici (parcanin on yuzunden acik cikar).
# Baski ekleri (kablo yoluna girmez, gerekcesi asagida): (1) DOLGU: boyun mili alt diski ile servo yuvasi ustu arasindaki 1,9 mm
# bosluk (horn yeri) r < 20 icinde doldurulur -> mil parcaya baglanir, disk alti askida kalmaz (kanal ustu acikligi uzerinde <= 20 mm
# kopru). 1,9 mm bosluktan kablo gecmez. (2) RULMAN: alt 6808'in yeri (r 20...26, y 64...66) dolu: gercekte kablo odasinin tavani
# rulmandir; parcada da oda tavani kapali olsun (6 mm radyal kopru).
# Baski: kaynak Y ekseni yukari (gercek parcalarin baski yonu; kanal tavani, alt cikis ve mil penceresi ustleri 45 derece), servo yuvasi
# tabani (y = 3) tablada. STL koordinati: (x, y, z) -> (x, -z, y - 3), tabla z = 0.
# Cikti: kafa/stl/boyun-tunel-deneme.stl + kafa/boyun-tunel-deneme.json. Kaynaklar yalniz OKUNUR (model / tarama kaynagi degismez).
# Calistirma: FC_SCRIPT=<bu betik> freecadcmd ~/.robot-cad/run_fc.py  (yalniz kafa-montaj.FCStd acilir; ~10-30 s)
import os, sys, re, math, json, hashlib, time
import FreeCAD as App
import Part
import MeshPart

t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
if UST not in sys.path:
    sys.path.insert(0, UST)
import arayuz as A

V = App.Vector
FCSTD = os.path.join(HERE, "kafa-montaj.FCStd")
KAYNAK = ("Servo yuvasi", "Rulman yuvasi", "Boyun mili")          # basilan parcalar
KOMSU = ("Pan servosu MG996R", "Pan servosu cikis mili", "Pan horn 25T aluminyum disk", "Pan horn merkez vidasi M3",
         "Mil-horn civatasi M3x8")                                 # duz.1 E2: tunelin gercek komsulari (horn r 12,5 basamakta), ayni FCStd'den
# duz.1 E1: kutu mil bolgesinde tam mil capina (z +20) ve mil ustune (flans ustu y 96): fis pencereden Ø32 mil icine girip yukari doner
KUTU = dict(x=(-20.0, 20.0), y=(3.0, 96.0), z=(-31.0, 20.0))
BEKLENEN = dict(kanal=(20.0, 7.8), boy=34.0, pencere=(20.0, 10.0), alt_cikis=(20.0, 12.0))   # kablolama-on-kararlar.md:148-149, rehber_metin.py:676
TOL = 0.05          # mm: kaynak tunel ile parca kesiti arasi (BRep ayni geometri; STL agi icin ayrica)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def tek(sh):
    s = sh.removeSplitter()
    return s


# ---------------------------------------------------------------- kaynak
doc = App.openDocument(FCSTD)
SRC = {}
for ad in KAYNAK + KOMSU:
    obj = [o for o in doc.Objects if re.fullmatch(re.escape(ad) + r"(\d{3})?", o.Label) and hasattr(o, "Shape") and o.Shape.Volume > 1e-3]
    assert obj and (ad in KOMSU or len(obj) == 1), (ad, [o.Label for o in obj])
    sh = obj[0].Shape.copy()
    for o in obj[1:]:
        sh = sh.fuse(o.Shape)
    SRC[ad] = sh
    bb = SRC[ad].BoundBox
    print(ad, len(obj), "bb", [round(v, 2) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)], "V", round(SRC[ad].Volume, 1))
# yerel koordinat dogrulamasi (kafa yereli: servo yuvasi plaka ustunde y 3...46, boyun mili ev pozunda)
bs = SRC["Servo yuvasi"].BoundBox
assert abs(bs.YMin - 3.0) < 1e-6 and abs(bs.YMax - 46.0) < 1e-6, "servo yuvasi yerel degil"
bh = SRC["Pan horn 25T aluminyum disk"].BoundBox
HORN_R = round(bh.XLength / 2, 2)

KB = box(KUTU["x"][0], KUTU["x"][1], KUTU["y"][0], KUTU["y"][1], KUTU["z"][0], KUTU["z"][1])
birlesim = SRC[KAYNAK[0]].fuse([SRC[a] for a in KAYNAK[1:] + KOMSU])
S = tek(birlesim.common(KB))                  # kaynak kesisimi (eksiz, gercek komsularla): olcu karsilastirmasi bunun uzerinde


def cyl(r, y0, y1):
    return Part.makeCylinder(r, y1 - y0, V(0, y0, 0), V(0, 1, 0))


# Baski ekleri (yalniz gercekte bos AMA kablo / fis yolu disinda kalan hacimlere; asagida hacim kesisimiyle olculur):
# (1) dolgu: mil diski alti 1,9 mm bosluk (y 46...47,9), r < 20 ama kanal ustu izinin (x -14...6) DISINDA; izde yalniz gercek horn kalir
#     (r 12,5, KOMSU) -> izde disk alti x'te 20 mm kopru, yanlarda dolgu mili baglar.
# (2) rulman: iki 6808 ve aralari (r 20...26, y 64...82): gercekte rulman; oda tavani ve mil disi kapali.
# (3) servo alti: pan servosu govdesi ile tabla arasi 2 mm (servo cebi y 3...5): gercekte boyun plakasi ustu bosluk, servo govdesi kopru olmasin.
dolgu = cyl(20.0, 46.0, 47.9).cut(box(-14.0, 6.0, 45.0, 49.0, -21.0, 21.0)).common(KB)
rulman = cyl(26.0, 64.0, 82.0).cut(cyl(20.0, 63.0, 83.0)).common(KB)
servo_alti = box(-10.05, 10.05, 3.0, 5.01, -10.4, 20.0).common(KB)
EKLER = dict(dolgu=dolgu, rulman=rulman, servo_alti=servo_alti)
P = tek(S.fuse(list(EKLER.values())))
P = P.Solids[0] if len(P.Solids) == 1 else P
print("parca kati sayisi", len(P.Solids), "gecerli", P.isValid(), "horn r", HORN_R)

# Kablo / fis yolu bolgesi (gercek tunelin bos hacmi, kaynakta olculur): alt cikis + kanal + kanal ustu + basamak (y 44...49) + kablo odasi +
# mil penceresi + mil ici. Eklerin bu bosluga girdigi hacim 0 olmali; P - S yalniz eklerdir, S - P 0 olmali (kesilen yok).
YOL = box(-14.0, 6.0, 6.0, 18.0, -31.0, -19.2).fuse([box(-14.0, 6.0, 6.0, 46.0, -27.0, -10.4), box(-14.0, 6.0, 44.0, 49.0, -27.5, -10.4),
                                                  cyl(27.5, 46.0, 62.0).cut(cyl(20.0, 45.0, 63.0)), box(-10.0, 10.0, 53.0, 63.0, -25.0, 0.0),
                                                  cyl(16.0, 52.9, 96.0)]).common(KB)
YOL_BOS = YOL.cut(S)                           # gercekte fisin girebilecegi bos hacim


# ---------------------------------------------------------------- olcum yardimcilari (nokta iceride mi)
def ic(sh, x, y, z):
    return sh.isInside(V(x, y, z), 1e-4, True)


def bosluk_araligi(sh, sabit, eksen, a0, a1, adim=0.02):
    """sabit noktadan eksen boyunca tara; en uzun bos (malzeme disi) araligi [a, b] dondur."""
    en, cur = None, None
    a = a0
    while a <= a1 + 1e-9:
        p = list(sabit)
        p[eksen] = a
        bos = not ic(sh, *p)
        if bos and cur is None:
            cur = a
        if (not bos or a + adim > a1 + 1e-9) and cur is not None:
            b = a if bos else a - adim
            if en is None or b - cur > en[1] - en[0]:
                en = (cur, b)
            cur = None
        a += adim
    return None if en is None else (round(en[0], 2), round(en[1], 2))


def olc(sh):
    o = {}
    # arka kanal kesiti (y 23, kanal ortasi): x araligi z -23,1'de, z araligi x -4'te
    o["kanal_x"] = bosluk_araligi(sh, (0, 23.0, -23.1), 0, -17.9, 11.9)
    o["kanal_z"] = bosluk_araligi(sh, (-4.0, 23.0, 0), 2, -30.9, -12.1)
    # kanal boyu: kanal ekseninde (x -4, z -23,1) y boyunca bos aralik (alt cikis ve kanal ustu ile birlesir: ayrica sabit kesit boyu)
    o["kanal_y_eksen"] = bosluk_araligi(sh, (-4.0, 0, -23.1), 1, 3.1, 65.9)
    # sabit kesit boyu: kanalin on duvari (z -19,2) var ve kanal (z -26,9...-19,3) bos olan y araligi (alt cikis dahil, kanal ustu haric)
    ys = [round(3.1 + 0.05 * i, 2) for i in range(int((50.0 - 3.1) / 0.05))]
    kes = [y for y in ys if (not ic(sh, -10.0, y, -26.9)) and (not ic(sh, -10.0, y, -19.3)) and ic(sh, -10.0, y, -18.9)]   # x -10: servo kablo yarigi (x -6...4) disi
    o["kanal_sabit_kesit_y"] = (min(kes), max(kes)) if kes else None
    # alt cikis (arka duvar, z -28,75): x araligi y 8'de, y araligi x -4'te
    o["alt_cikis_x"] = bosluk_araligi(sh, (0, 8.0, -28.75), 0, -17.9, 11.9)
    o["alt_cikis_y"] = bosluk_araligi(sh, (-4.0, 0, -28.75), 1, 3.1, 30.0)
    # mil penceresi (boyun mili duvari r 16...20, r 18'de): x araligi y 55'te, y araligi x 0'da
    xs = [round(-15.0 + 0.02 * i, 2) for i in range(1501)]
    bos = set(x for x in xs if not ic(sh, x, 55.0, -math.sqrt(18.0 ** 2 - x * x)))
    if 0.0 in bos:                                  # x 0'i iceren kesintisiz aralik (|x| > 13,4'te r 18 noktasi kutu disina cikar)
        i0 = i1 = xs.index(0.0)
        while i0 > 0 and xs[i0 - 1] in bos:
            i0 -= 1
        while i1 < len(xs) - 1 and xs[i1 + 1] in bos:
            i1 += 1
        o["pencere_x_y55"] = (xs[i0], xs[i1])
    else:
        o["pencere_x_y55"] = None
    o["pencere_y_x0"] = bosluk_araligi(sh, (0.0, 0, -18.0), 1, 48.0, 65.9)
    # kablo odasi (r 20...27,5) x 0'da z araligi y 56'da
    o["oda_z_y56"] = bosluk_araligi(sh, (0.0, 56.0, 0), 2, -30.9, -20.05)
    # duz.1 E2 basamak (kanal ustu -> kablo odasi, y 44...49): z boyunca en uzun bos aralik; y 45 servo yuvasi ustu ici, y 46,95 horn
    # katmani (mil diski alti bosluk), y 48,5 mil diski
    for y_ in (45.0, 46.95, 48.5):
        for x_ in (-10.0, -4.0, 0.0, 4.0):
            o["basamak_y%s_x%s" % (y_, x_)] = bosluk_araligi(sh, (x_, y_, 0), 2, -30.9, 19.9)
    # duz.1 E1 mil donusu: mil ici (r < 16) ve karsi duvar (r 16...20) parcada; y 58'de pencere -> mil ici -> karsi duvar, y 70 / 90 mil ici
    o["mil_donus_y58_x0"] = bosluk_araligi(sh, (0.0, 58.0, 0), 2, -30.9, 19.9)
    o["mil_ici_y70_x0"] = bosluk_araligi(sh, (0.0, 70.0, 0), 2, -30.9, 19.9)
    o["mil_ici_y90_x0"] = bosluk_araligi(sh, (0.0, 90.0, 0), 2, -30.9, 19.9)
    o["mil_ici_y70_z0"] = bosluk_araligi(sh, (0, 70.0, 0.0), 0, -19.9, 19.9)
    return o


OS = olc(S)
MIL = olc(SRC["Boyun mili"])          # mil tek basina (kutusuz): pencere olcusu kutu sinirindan bagimsiz
MIL_PENCERE = dict(x_y55=MIL["pencere_x_y55"], y_x0=MIL["pencere_y_x0"])
OP = olc(P)
print("kaynak", OS)
print("parca ", OP)


def fark(a, b):
    if a is None or b is None:
        return None
    return round(max(abs(a[0] - b[0]), abs(a[1] - b[1])), 3)


KARS = {k: dict(kaynak=OS[k], parca=OP[k], fark_mm=fark(OS[k], OP[k])) for k in OS}
kars_ok = all(v["fark_mm"] is not None and v["fark_mm"] <= TOL for v in KARS.values())
# duz.1 genel ilke: eklerin fis yoluna (gercekte bos YOL_BOS) girdigi hacim ve kaynaktan kesilen hacim (kutu ici) olculur; ikisi de 0 olmali
ek_bosluk = {ad_: dict(hacim_mm3=round(e.Volume, 3), yol_kesisim_mm3=round(e.common(YOL_BOS).Volume, 4)) for ad_, e in EKLER.items()}
_BAS = box(-14.0, 6.0, 44, 49, -31, 20)                 # kanal ustu izi (orkestrator karari: izde gercek geometri)
ek_bosluk["basamak_y44_49"] = dict(yol_bos_kaynak_mm3=round(YOL_BOS.common(_BAS).Volume, 3), yol_bos_parca_mm3=round(YOL.common(_BAS).cut(P).Volume, 3))
# bilgi: izin yanlarinda (x < -14, x > 6) gercekte bos 1,9 mm katmandaki dolgu (orkestrator karari: yanlarda r < 20 kalabilir)
ek_bosluk["bilgi_yan_dolgu_basamak_iz_disi_mm3"] = round(dolgu.common(box(-20, 20, 46.0, 47.9, -27.5, -10.4)).Volume, 3)
ek_bosluk["kesilen_kaynak_eksi_parca_mm3"] = round(S.cut(P).Volume, 4)
ek_bosluk["eklenen_parca_eksi_kaynak_mm3"] = round(P.cut(S).Volume, 3)
ek_bosluk["yol_bos_kaynak_mm3"] = round(YOL_BOS.Volume, 3)
ek_bosluk["yol_bos_parca_mm3"] = round(YOL.cut(P).Volume, 3)
ek_ok = (all(v["yol_kesisim_mm3"] < 0.01 for k, v in ek_bosluk.items() if k in EKLER) and ek_bosluk["kesilen_kaynak_eksi_parca_mm3"] < 0.01
         and abs(ek_bosluk["yol_bos_kaynak_mm3"] - ek_bosluk["yol_bos_parca_mm3"]) < 0.01
         and abs(ek_bosluk["basamak_y44_49"]["yol_bos_kaynak_mm3"] - ek_bosluk["basamak_y44_49"]["yol_bos_parca_mm3"]) < 0.01)
print("ekler", ek_bosluk, ek_ok)


def aralik_boy(r):
    return None if r is None else round(r[1] - r[0], 2)


OLCU = dict(
    kanal_kesit_mm=[aralik_boy(OS["kanal_x"]), aralik_boy(OS["kanal_z"])],
    kanal_sabit_kesit_boy_mm=aralik_boy(OS["kanal_sabit_kesit_y"]),
    kanal_y_eksen_bos_mm=aralik_boy(OS["kanal_y_eksen"]),
    alt_cikis_mm=[aralik_boy(OS["alt_cikis_x"]), aralik_boy(OS["alt_cikis_y"])],
    mil_penceresi_mm=[aralik_boy(OS["pencere_x_y55"]), aralik_boy(OS["pencere_y_x0"])],
    mil_penceresi_kutusuz_mm=[aralik_boy(MIL_PENCERE["x_y55"]), aralik_boy(MIL_PENCERE["y_x0"])],
    kablo_odasi_radyal_mm=aralik_boy(OS["oda_z_y56"]),
    mil_ici_cap_mm=[aralik_boy(OS["mil_ici_y70_z0"]), aralik_boy(OS["mil_ici_y70_x0"])],
    pencere_mil_ici_z_y58=OS["mil_donus_y58_x0"],
    basamak_z_araliklari=dict((k, OS[k]) for k in OS if k.startswith("basamak")),
    horn_r_mm=HORN_R,
)
print("olcu", OLCU)

# ---------------------------------------------------------------- baski yonu ve cikti
Pb = P.copy()
Pb.rotate(V(0, 0, 0), V(1, 0, 0), 90.0)          # y -> z, z -> -y
Pb.translate(V(0, 0, -Pb.optimalBoundingBox().ZMin))
bb = Pb.optimalBoundingBox()                     # duz.1: egri yuzlerde BoundBox gevsek
assert abs(bb.ZMin) < 1e-3


def baski_kontrol(s):
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2)
    alan, gr = 0.0, {}
    for f in m.Facets:
        zc = sum(p[2] for p in f.Points) / 3
        if f.Normal.z < -math.cos(math.radians(44.0)) and zc > 0.05:
            alan += f.Area
            k = round(zc, 1)
            gr[k] = gr.get(k, 0.0) + f.Area
    en = sorted(gr.items(), key=lambda kv: -kv[1])[:6]
    return dict(cikinti_46ustu_mm2=round(alan, 1), en_buyuk_z_mm2=[(z, round(a, 1)) for z, a in en],
                not_="46 derece ustu asagi bakan yuzler (z = kaynak y - 3); gruplar F10o-gunluk.md duzeltme turu 1 bolumunde")


os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
STL = os.path.join(HERE, "stl", "boyun-tunel-deneme.stl")
MeshPart.meshFromShape(Shape=Pb, LinearDeflection=0.01, AngularDeflection=0.1).write(STL)
# STL'den geri okuma: ag hacmi / sinir kutusu BRep ile ayni mi, ag kapali ve manifold mu
import Mesh
ms = Mesh.Mesh(STL)
mb = ms.BoundBox
STL_KARS = dict(hacim_brep_mm3=round(Pb.Volume, 2), hacim_stl_mm3=round(ms.Volume, 2), hacim_fark_yuzde=round(100.0 * abs(ms.Volume - Pb.Volume) / Pb.Volume, 3),
                bb_fark_mm=round(max(abs(a - b) for a, b in zip((mb.XMin, mb.XMax, mb.YMin, mb.YMax, mb.ZMin, mb.ZMax),
                                                                 (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))), 4),
                kapali=bool(ms.isSolid()), manifold_disi=bool(ms.hasNonManifolds()), ucgen=ms.CountFacets)
stl_ok = STL_KARS["hacim_fark_yuzde"] < 0.5 and STL_KARS["bb_fark_mm"] < 0.02 and STL_KARS["kapali"] and not STL_KARS["manifold_disi"]
RHO, HIZ = A.PETG_RHO, A.PETG_HACIM_HIZI
kab = min(Pb.Volume, Pb.Area * 1.6 * 0.5)
v_eff = kab + 0.25 * max(0.0, Pb.Volume - kab)
taban = Pb.common(box(bb.XMin - 1, bb.XMax + 1, bb.YMin - 1, bb.YMax + 1, -0.01, 0.2)).Volume / 0.2          # duz.1 D2: dilim 0,2 mm (z 0...0,2)
SONUC = dict(
    betik="tasarim/freecad/kafa/boyun_tunel_deneme.py", paket="P10.7b2g", tarih="2026-11-17",
    kaynak=dict(fcstd="tasarim/freecad/kafa/kafa-montaj.FCStd", md5=md5(FCSTD), parcalar=list(KAYNAK), komsular=list(KOMSU), horn_r_mm=HORN_R,
                hacim_mm3={k: round(v.Volume, 2) for k, v in SRC.items()}, uretici="kafa_montaj.py (Govde / Pan: kafa7_parcalar.py:138-159, 162-178, 237-249)"),
    kutu_mm=KUTU, baski_ekleri=dict(dolgu="y 46...47,9, r < 20, kanal ustu izi (x -14...6) HARIC: izde yalniz gercek horn", rulman="r 20...26, y 64...82 (iki 6808 + arasi)", servo_alti="servo cebi y 3...5 (pan servosu alti)",
                                   ek_bolge_malzeme=ek_bosluk, ekler_kablo_yoluna_girmiyor=ek_ok),
    olcu=OLCU, beklenen=dict(kanal_kesit_mm=list(BEKLENEN["kanal"]), kanal_boy_mm=BEKLENEN["boy"], mil_penceresi_mm=list(BEKLENEN["pencere"]),
                              alt_cikis_mm=list(BEKLENEN["alt_cikis"]), kaynak="kablolama-on-kararlar.md:148-149, rehber_metin.py:676"),
    donusler=["alt cikis (arka yuz, yatay +z) -> arka kanal (dik, +y): 1. dik donus",
              "kanal ustu -> basamak (horn katmani) -> kablo odasi -> mil penceresi (yatay, +z eksene dogru)",
              "mil penceresi -> O32 mil ici (karsi duvar z +16...20) -> yukari (+y, mil ucu y 96): 2. dik donus"],
    karsilastirma=dict(tolerans_mm=TOL, olcumler=KARS, sonuc=kars_ok),
    stl_karsilastirma=dict(olcumler=STL_KARS, sonuc=stl_ok, olcut="hacim farki < %0,5, sinir kutusu < 0,02 mm, kapali, manifold"),
    parca=dict(stl="tasarim/freecad/kafa/stl/boyun-tunel-deneme.stl", stl_md5=md5(STL), malzeme="PETG (beyaz; tunel olcusu icin; asil servo yuvasi PETG-CF)",
               olcu_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)], kati=len(Pb.Solids), gecerli=Pb.isValid(),
               hacim_cm3=round(Pb.Volume / 1000, 2), kutle_100_g=round(Pb.Volume / 1000 * RHO, 1),
               kutle_tahmini_g=round(v_eff / 1000 * RHO, 1), sure_tahmini_dk=round(v_eff / HIZ / 60 * 1.3, 0),
               tabla_temas_mm2=round(taban, 0), yon="dik: servo yuvasi tabani (kaynak y = 3) tablada, mil ucu yukari",
               baski=baski_kontrol(Pb),
               tahmin_not="tahmini: 4 cevre + %25 dolgu, arayuz.PETG_HACIM_HIZI x 1,3 (test/m7_kuponlari.py ile ayni yontem)"),
    sure_s=round(time.time() - t0, 1))
with open(os.path.join(HERE, "boyun-tunel-deneme.json"), "w", encoding="utf-8") as f:
    json.dump(SONUC, f, ensure_ascii=False, indent=1)
print("karsilastirma", kars_ok, "stl", stl_ok, "ekler", ek_ok, "parca", SONUC["parca"]["olcu_mm"], SONUC["parca"]["kutle_tahmini_g"], "g")
App.closeDocument(doc.Name)
print("bitti %.1f s" % (time.time() - t0))
