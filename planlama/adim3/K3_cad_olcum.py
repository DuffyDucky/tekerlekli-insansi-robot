# K3 bagimsiz CAD olcumu (FreeCAD 1.1, freecadcmd). Uretilmis dosyalara YAZMAZ: FCStd'lerin %TEMP%\k3 kopyasini acar,
# taban_parcalar'i yalniz bellekte (TABAN_OMNI=1) kurar. Sonuc: planlama/adim3/K3_cad_sonuc.json
# Calistirma: FC_SCRIPT=<bu dosya> freecadcmd C:\Users\Victus\.robot-cad\run_fc.py
import os, sys, json, math, shutil
import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
FC = os.path.join(ROBOT, "tasarim", "freecad")
TMP = os.path.join(os.environ["TEMP"], "k3")
os.makedirs(TMP, exist_ok=True)
OUT = {}


def kopya_ac(rel, ad):
    dst = os.path.join(TMP, ad)
    shutil.copyfile(os.path.join(FC, rel), dst)
    return App.openDocument(dst)


def sekiller(doc):
    S = {}
    for o in doc.Objects:
        if o.TypeId == "Part::Feature" and not o.Shape.isNull():
            S.setdefault(o.Label, []).append(o.Shape)
    return S


def grubu(doc, grp):
    g = doc.getObject(grp)
    return [o.Label for o in g.Group if o.TypeId == "Part::Feature"]


def ortak(a, b):
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


# ------------------------------------------------------------------ KAFA
kd = kopya_ac("kafa/kafa-montaj.FCStd", "kafa.FCStd")
KS = sekiller(kd)
PI = KS["Raspberry Pi 5 8GB + Active Cooler"][0]
kafa_lab = grubu(kd, "Kafa")
pan_lab = grubu(kd, "Pan")
gov_lab = grubu(kd, "Govde")
pi_kendi = [l for l in kafa_lab if "(Pi " in l or l.startswith("Raspberry")]
yakin = []
for lab in kafa_lab:
    if lab in pi_kendi:
        continue
    for sh in KS[lab]:
        d = PI.distToShape(sh)[0]
        v = ortak(PI, sh) if d < 1e-6 else 0.0
        yakin.append((round(d, 2), lab, round(v, 3)))
yakin.sort()
OUT["kafa_pi_yakin"] = yakin[:8]
OUT["kafa_pi_bb"] = [round(x, 2) for x in (PI.BoundBox.XMin, PI.BoundBox.XMax, PI.BoundBox.YMin, PI.BoundBox.YMax, PI.BoundBox.ZMin, PI.BoundBox.ZMax)]

# tilt + pan taramasi: Pi + cevirici + amfi + Pi burclari (Kafa grubu) <-> Pan ve Govde gruplari
hareketli = [KS[l][0] for l in kafa_lab if l in pi_kendi or l.startswith("5 V cevirici") or l.startswith("MAX98357A")]
pan_sh = [s for l in pan_lab for s in KS[l]]
gov_sh = [s for l in gov_lab for s in KS[l]]
T_N, T_D = V(26.9, 130.0, 25.0), V(1, 0, 0)
P_N, P_D = V(0, 44.6, 0), V(0, 1, 0)
HAR = Part.makeCompound(hareketli)


def bb_bosluk(a, b):
    dx = max(0.0, max(a.XMin - b.XMax, b.XMin - a.XMax))
    dy = max(0.0, max(a.YMin - b.YMax, b.YMin - a.YMax))
    dz = max(0.0, max(a.ZMin - b.ZMax, b.ZMin - a.ZMax))
    return math.sqrt(dx * dx + dy * dy + dz * dz)


aci_min = {}
for th in range(-40, 41, 1):
    s = HAR.copy()
    s.rotate(T_N, T_D, th)
    for ps in (-90, -45, 0, 45, 90):
        s2 = s.copy()
        s2.rotate(P_N, P_D, ps)        # pan: Kafa + Pan birlikte doner, Govde sabit
        for grp, shs in (("Pan", pan_sh), ("Govde", gov_sh)):
            for q in shs:
                q2 = q
                if grp == "Pan":
                    q2 = q.copy()
                    q2.rotate(P_N, P_D, ps)
                if th in aci_min and bb_bosluk(s2.BoundBox, q2.BoundBox) > aci_min[th][0]:
                    continue
                d = s2.distToShape(q2)[0]
                if th not in aci_min or d < aci_min[th][0]:
                    aci_min[th] = (round(d, 2), ps, grp)
en = dict(aci_min=aci_min,
          aralik_m25_p30=min(aci_min[t] + (t,) for t in aci_min if -25 <= t <= 30),
          aralik_m30_p25_ters_isaret=min(aci_min[t] + (t,) for t in aci_min if -30 <= t <= 25),
          serbest_m25_p40=min(aci_min[t] + (t,) for t in aci_min if -25 <= t <= 40))
OUT["kafa_tarama_min"] = en

# SD erisimi: microSD -X ucunda kart altinda; -X yonunde 50 mm cekme yolu
sd = Part.makeBox(50.0, 10.0, 22.0, V(-49.5 - 50.0, 185.0, -38.0))
OUT["kafa_sd_yolu"] = sorted([(lab, round(ortak(sd, sh), 1)) for lab in KS for sh in KS[lab] if sd.BoundBox.intersect(sh.BoundBox) and ortak(sd, sh) > 0.01])

# havalandirma yariklari: her yarik merkezinde duvari kesen 1 x 1 mm cubuk; arka kabukla ortak hacim 0 olmali (acik yarik)
ak = KS["Arka kafa kabugu"][0]
acik, kapali = 0, []
for x0, x1 in ((-45.0, -5.0), (5.0, 45.0)):
    for k in range(5):
        y = 192.0 + 8.0 * k + 1.5
        c = Part.makeBox(1, 1, 8, V(0.5 * (x0 + x1), y - 0.5, -68.0))
        (kapali.append(("giris", x0, y)) if ortak(c, ak) > 1e-6 else None)
        acik += ortak(c, ak) <= 1e-6
for sx in (1, -1):
    for k in range(6):
        y = 198.0 + 9.0 * k + 1.5
        c = Part.makeBox(8, 1, 1, V(sx * 105.0 - 4.0, y - 0.5, -30.5))
        (kapali.append(("cikis", sx, y)) if ortak(c, ak) > 1e-6 else None)
        acik += ortak(c, ak) <= 1e-6
OUT["kafa_yarik"] = dict(acik=int(acik), toplam=22, kapali=kapali)
# yariklarin onu bos mu (5 mm icerisi)
on_g = Part.makeBox(90, 35, 5, V(-45, 192, -62.5))
on_c = [Part.makeBox(5, 51, 40, V(sx * 102.5 - (5 if sx > 0 else 0), 198, -50)) for sx in (1, -1)]
OUT["kafa_yarik_onu"] = sorted({lab for lab in KS for sh in KS[lab] for b in [on_g] + on_c
                                if lab != "Arka kafa kabugu" and b.BoundBox.intersect(sh.BoundBox) and ortak(b, sh) > 0.01})
App.closeDocument(kd.Name)

# ------------------------------------------------------------------ TABAN (kayitli dosya)
td = kopya_ac("taban/taban-montaj.FCStd", "taban.FCStd")
TS = sekiller(td)
yeni = [l for l in TS if l.startswith(("Arayuz karti", "Servo dagitim", "XL4016 servo"))
        or "(Arayuz karti" in l or "(Servo dagitim" in l or "(XL4016 servo 6 V" in l]
cak, yak = [], {}
for l in yeni:
    for s in TS[l]:
        for m in TS:
            if m == l or m.startswith("Kablo yolu"):
                continue
            for q in TS[m]:
                if not s.BoundBox.isValid() or not q.BoundBox.isValid():
                    continue
                bb = App.BoundBox(s.BoundBox)
                bb.enlarge(15)
                if not bb.intersect(q.BoundBox):
                    continue
                v = ortak(s, q)
                if v > 0.01:
                    cak.append((l, m, round(v, 2)))
                if l.startswith(("Arayuz karti", "Servo dagitim")):
                    d = s.distToShape(q)[0]
                    if d > 1e-3 and (l not in yak or d < yak[l][0]):
                        yak[l] = (round(d, 2), m)
OUT["taban_yeni_parca"] = len(yeni)
OUT["taban_yeni_cakisma"] = sorted(set(cak))
OUT["taban_kart_en_yakin"] = yak
OUT["taban_pi_kalinti"] = [l for l in TS if "Raspberry" in l or "MAX98357" in l or "Pi 5" in l]
App.closeDocument(td.Name)

# ------------------------------------------------------------------ OMNI (bellekte; kabuk eteği kopya dosyadan)
os.environ["TABAN_OMNI"] = "1"
for p in (FC, os.path.join(FC, "taban")):
    if p not in sys.path:
        sys.path.insert(0, p)
import taban_parcalar as TP
kb = kopya_ac("kabuk/kabuk-montaj.FCStd", "kabuk.FCStd")
ETEK = [(o.Label, o.Shape) for o in kb.Objects if o.TypeId == "Part::Feature" and o.Label.startswith("Etek")]
om = {}
for p in TP.P:
    if p["ad"].startswith(("Omni teker", "Teker 125")) or "adaptor" in p["ad"].lower():
        best = None
        for lab, sh in ETEK:
            d, pr, _ = p["shape"].distToShape(sh)
            if best is None or d < best[0]:
                best = (round(d, 2), lab, [round(c, 1) for c in pr[0][0]])
        om[p["ad"]] = best
OUT["omni_teker_etek"] = om
OUT["omni_aktif"] = TP.OMNI
App.closeDocument(kb.Name)

json.dump(OUT, open(os.path.join(HERE, "K3_cad_sonuc.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("K3 CAD BITTI")
