# P10.8d madde 7: E4 dikey dikiş bindirmesi ölçümü (FreeCAD 1.1, B-rep; modele dokunmaz, yalnız P108d-olcum/e4.json yazar).
# Soru (kuyruk "Açık (c)", F10c-gunluk.md D2 + F10y güncellemesi): arka kafa kabuklarının dikey dikişteki bindirmesi takma sırasını
# geometriyle zorluyor mu? Yalnız iki kabuk (öbür kafa parçaları yok): biri yerindeyken öbürü 12 düz yönde kendi yerinden uzaklaştırılır
# (çıkış = girişin tersi). Her adımda ortak hacim; eşik ESIK_MM3. Adım H mm (kabuk duvarı 3 mm; iki duvar 2 mm'lik adımda birbirinin
# içinden atlayamaz), ilk çarpışma ikiye bölmeyle 0,25 mm'ye inceltilir. Kutular ayrışınca yön "serbest" (en çok MAX mm).
# Koşu: FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
import os, json, time
import FreeCAD as App
import Part
t0 = time.time()
V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "tasarim", "freecad")
H, MAX, ESIK_MM3 = 2.0, 300.0, 0.5


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


doc = App.openDocument(os.path.join(FC, "montaj", "robot-montaj.FCStd"))
K = {}
for o in doc.Objects:
    if o.TypeId == "Part::Feature" and o.Label in ("Arka kafa kabugu sag", "Arka kafa kabugu sol", "Yuz kabugu (on) sag", "Yuz kabugu (on) sol"):
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        K[o.Label] = s.copy()
log("kabuk", sorted(K), [round(K[k].Volume, 1) for k in sorted(K)], [K[k].isValid() for k in sorted(K)])
SAG, SOL = K["Arka kafa kabugu sag"], K["Arka kafa kabugu sol"]


def bbl(b):
    return [round(v, 2) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)]


# ---------------------------------------------------------------------------------------------------- (a) bindirme geometrisi
bs, bo = SAG.BoundBox, SOL.BoundBox
x0, x1 = max(bs.XMin, bo.XMin), min(bs.XMax, bo.XMax)            # iki kabuğun x'te ortak bandı (dikiş bölgesi)
kutu = Part.makeBox(x1 - x0 + 0.02, bs.YLength + 20, 1000, V(x0 - 0.01, bs.YMin - 10, -500))   # kabuklar global (kafa y ~1290 yukarıda)
dil_sag = SAG.common(kutu)
dil_sol = SOL.common(kutu)
geom = dict(x_ortak_bant=[round(x0, 2), round(x1, 2)], sag_bant=dict(bb=bbl(dil_sag.BoundBox), hacim_mm3=round(dil_sag.Volume, 1)),
            sol_bant=dict(bb=bbl(dil_sol.BoundBox), hacim_mm3=round(dil_sol.Volume, 1)),
            yerinde_ortak_hacim_mm3=round(SAG.common(SOL).Volume, 4), yerinde_en_dar_mm=round(SAG.distToShape(SOL)[0], 4))
# dikiş kesitleri: birkaç y düzeyinde, x bandında iki kabuğun z aralığı (hangisi içte / dışta) ve aralarındaki boşluk
kesit = []
for y in (120.0, 160.0, 200.0, 240.0, 270.0):
    yy = bs.YMin + (y - 73.3)      # y: kafa yerel (kafa-analiz.json'da kabuk y 73,3...291,6); kabuklar global, ev pozunda
    dil = Part.makeBox(x1 - x0 + 0.02, 0.5, 1000, V(x0 - 0.01, yy, -500))
    a, b = SAG.common(dil), SOL.common(dil)
    r = dict(y=round(yy, 1))
    if a.Volume > 1e-6:
        r["sag_z"] = [round(a.BoundBox.ZMin, 2), round(a.BoundBox.ZMax, 2)]
        r["sag_x"] = [round(a.BoundBox.XMin, 2), round(a.BoundBox.XMax, 2)]
    if b.Volume > 1e-6:
        r["sol_z"] = [round(b.BoundBox.ZMin, 2), round(b.BoundBox.ZMax, 2)]
        r["sol_x"] = [round(b.BoundBox.XMin, 2), round(b.BoundBox.XMax, 2)]
    if a.Volume > 1e-6 and b.Volume > 1e-6:
        r["bosluk_mm"] = round(a.distToShape(b)[0], 3)
    kesit.append(r)
geom["kesit"] = kesit
# dikiş kesit haritası (y yerel 200): satır z (arkadan öne), sütun x (-18...+2, 0,5 mm); R sağ kabuk, L sol, X ikisi, . boş
yh = bs.YMin + (200.0 - 73.3)
harita = []
for i in range(25):
    z = -66.0 + 0.25 * i
    harita.append("z %+7.2f " % z + "".join(
        {(1, 0): "R", (0, 1): "L", (1, 1): "X", (0, 0): "."}[(int(SAG.isInside(V(-18.0 + 0.5 * j, yh, z), 1e-4, False)),
                                                              int(SOL.isInside(V(-18.0 + 0.5 * j, yh, z), 1e-4, False)))]
        for j in range(41)))
geom["kesit_haritasi"] = dict(y=round(yh, 1), x_ilk=-18.0, x_adim=0.5, satirlar=harita)
log("harita\n" + "\n".join(harita))
log("geometri", geom)

# ---------------------------------------------------------------------------------------------------- (b) yön süpürmesi
YON = {"+x": (1, 0, 0), "-x": (-1, 0, 0), "+y": (0, 1, 0), "-y": (0, -1, 0), "+z": (0, 0, 1), "-z": (0, 0, -1),
       "+x-z": (1, 0, -1), "-x-z": (-1, 0, -1), "+x+z": (1, 0, 1), "-x+z": (-1, 0, 1), "+y-z": (0, 1, -1), "+x+y": (1, 1, 0)}


def ortak(mov, fix, u, d):
    m = mov.copy()
    m.translate(u * d)
    if not m.BoundBox.intersect(fix.BoundBox):
        return None
    return m.common(fix).Volume


def supur(mov, fix):
    out = {}
    for ad, v in YON.items():
        u = V(*v)
        u.normalize()
        d, ilk = 0.0, None
        while d < MAX:
            d += H
            c = ortak(mov, fix, u, d)
            if c is None:
                break
            if c > ESIK_MM3:
                lo, hi = d - H, d
                while hi - lo > 0.25:
                    mid = 0.5 * (lo + hi)
                    cm = ortak(mov, fix, u, mid)
                    if cm is not None and cm > ESIK_MM3:
                        hi = mid
                    else:
                        lo = mid
                ilk = (round(hi, 2), round(ortak(mov, fix, u, hi), 3))
                break
        out[ad] = dict(sonuc="kapali" if ilk else "serbest", ilk_carpisma_mm=ilk[0] if ilk else None,
                       ortak_hacim_mm3=ilk[1] if ilk else None, kutu_ayrisma_mm=None if ilk else round(d, 1))
        log(ad, out[ad])
    return out


sw = {"sag_hareketli_sol_yerinde": supur(SAG, SOL), "sol_hareketli_sag_yerinde": supur(SOL, SAG)}
serbest = {k: [y for y, r in v.items() if r["sonuc"] == "serbest"] for k, v in sw.items()}
sonuc = dict(soru="dikey dikiş bindirmesi arka kabukların takma sırasını zorluyor mu (yalnız iki kabuk)",
             zorluyor=any(not s for s in serbest.values()), serbest_yonler=serbest)
json.dump(dict(yontem=dict(adim_mm=H, en_cok_mm=MAX, esik_mm3=ESIK_MM3, inceltme_mm=0.25, kaynak="montaj/robot-montaj.FCStd ev pozu"),
               geometri=geom, supurme=sw, sonuc=sonuc, sure_s=round(time.time() - t0, 1)),
          open(os.path.join(HERE, "P108d-olcum", "e4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("BITTI", sonuc)
