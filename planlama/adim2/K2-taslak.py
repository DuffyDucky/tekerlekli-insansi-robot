# K2 (3. ajan, 25 Ekim 2026): S1 kaseti taslak-170'te (kol x1,25 + DS3235 + dirsek catali 8 mm) ayni mi? Yalniz okur.
#   1) taslak-170.FCStd'den S1 cevresindeki parcalar (omuz govde/gobek/kol, kabuk kaseti + civatalari + omuz bandi + isil gomme,
#      dirsek ust kol) sag omuz yereline (- OY - DY) alinir; modul FCStd'leriyle (omuz/kabuk/dirsek) parca parca kiyaslanir:
#      hacim, sinir kutusu, ortak hacim orani (ayni yerde ayni sekil mi). Sol taraf X aynasiyla.
#   2) Ev pozu (S2 0) cakismalari: 6 cift taslakta yeniden olculur; S2 5 (yazilim ev pozu) ve 3,5 / 4 / 4,5'te kol zinciri
#      S2 ekseni etrafinda dondurulunce kalir mi.
#   3) Kol zinciri (taslak: tup 130, dirsek DY-30) <-> kaset: S1 -45...135 (5) x S2 5...20 (1) + 30...120 (15), dirsek 0 / 52,5 / 105
#      (dirsek/el taslakta uzadi; kaset omuzdan 26 mm yukari tasiyor) -> en kucuk.
# Cikti: K2-taslak.json
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part

A, V, log, tasi = O.A, O.V, O.log, O.tasi
t0 = time.time()
ADIM = os.environ.get("K2_ADIM", "hepsi")
JS = "K2-taslak%s.json" % ("" if ADIM == "hepsi" else "-" + ADIM)
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"))
sys.path.insert(0, os.path.join(O.R, "taslak-170"))
import taslak_ayar as TA
DY = TA.DY
OY = V(*O.OY)
TS = O.ac("taslak-170/taslak-170.FCStd", "K2T")
log("taslak parca", len(TS), "gruplar", sorted(set(p["grup"] for p in TS))[:60])
OUT["taslak_parca"] = len(TS)
OUT["DY"] = DY
YAKIN = App.BoundBox(110, -130, -110, 290, 110, 110)       # sag omuz yereli: S1 cevresi


def yerel(s, sag=True):
    q = s.copy()
    if not sag:
        q = q.mirror(V(0, 0, 0), V(1, 0, 0))
    q.translate(V(-OY.x, -OY.y - DY, -OY.z))
    return q


TY = {}
for sag in (True, False):
    for p in TS:
        s = yerel(p["shape"], sag)
        if s.BoundBox.intersect(YAKIN) and s.BoundBox.XMin > 100:
            TY.setdefault("sag" if sag else "sol", []).append(dict(ad=p["ad"], grup=p["grup"], shape=s))
log("S1 cevresi", {k: len(v) for k, v in TY.items()})
KOLGRUP = {"sag": ("OmuzSag_Kol", "DirsekSag_UstKol", "DirsekSag_OnKol", "DirsekSag_El"),
           "sol": ("OmuzSol_Kol", "DirsekSol_UstKol", "DirsekSol_OnKol", "DirsekSol_El")}
TKOL = {t: [dict(ad=p["ad"], grup=p["grup"], shape=yerel(p["shape"], t == "sag")) for p in TS if p["grup"] in KOLGRUP[t]] for t in ("sag", "sol")}
log("kol zinciri", {k: len(v) for k, v in TKOL.items()})

# modul parcalari (sag omuz yereli)
OMU = O.ac("omuz/omuz-montaj.FCStd")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd")
MOD = [dict(ad=p["ad"], grup="omuz/" + p["grup"], shape=p["shape"]) for p in OMU if p["tur"] != "Referans"] + \
      [dict(ad=p["ad"], grup="kabuk", shape=p["shape"]) for p in KAB] + \
      [dict(ad=p["ad"], grup="dirsek/" + p["grup"], shape=p["shape"]) for p in DIR]
MOD = [m for m in MOD if m["shape"].BoundBox.intersect(YAKIN) and m["shape"].BoundBox.XMin > 100]


def kiyas(taraf):
    """Her modul parcasina taslakta ayni hacim ve ayni yerde (ortak hacim / hacim) bir parca var mi."""
    sat = []
    T = TY[taraf]
    for m in MOD:
        sm = m["shape"]
        if sm.Volume < 1e-6:
            continue
        en = None
        for t in T:
            st = t["shape"]
            if abs(st.Volume - sm.Volume) > max(0.5, 0.002 * sm.Volume):
                continue
            if (st.BoundBox.Center - sm.BoundBox.Center).Length > 0.05:
                continue
            try:
                c = sm.common(st).Volume / sm.Volume
            except Exception:
                c = -1
            if en is None or c > en[1]:
                en = (t["ad"], round(c, 5))
        sat.append(dict(modul_parca=m["ad"], grup=m["grup"], hacim=round(sm.Volume, 2), taslak=en))
    ayni = [q for q in sat if q["taslak"] and q["taslak"][1] > 0.9999]
    farkli = [q for q in sat if not (q["taslak"] and q["taslak"][1] > 0.9999)]
    return dict(modul_parca=len(sat), ayni=len(ayni), farkli=farkli)


if ADIM in ("hepsi", "kiyas"):
    OUT["kiyas"] = {t: kiyas(t) for t in ("sag", "sol")}
    log("kiyas", {t: (v["modul_parca"], v["ayni"], [(q["modul_parca"], q["taslak"]) for q in v["farkli"]]) for t, v in OUT["kiyas"].items()})
    O.kaydet(JS, OUT)

# taslak parcalari, gruplara (S1 ile donen / S2 ile donen) ayir: ad ve modul gruplarina gore (omuz FCStd'deki grup adlari)
G_GOB = set(p["ad"] for p in OMU if p["grup"] == "Gobek")
G_KOL = set(p["ad"] for p in OMU if p["grup"] == "Kol")
G_GOV = set(p["ad"] for p in OMU if p["grup"] == "Govde" and p["tur"] != "Referans")


def taslak_kol(taraf):
    """Taslakta S2 ile donen zincir: omuz Kol grubu (ust kol tupu uzamis) + dirsek/el (taslakta grup adi)."""
    out = [(t["ad"], t["shape"]) for t in TKOL[taraf]]
    return out


if ADIM in ("hepsi", "ev"):
    ev = {}
    for taraf in ("sag", "sol"):
        T = TY[taraf]
        GOBt = [(t["ad"], t["shape"]) for t in T if t["grup"].endswith("_Gobek")]
        KOLt = taslak_kol(taraf)
        KASt = [(t["ad"], t["shape"]) for t in T if t["ad"].startswith("S1 kaset") or t["ad"].startswith("Kaset civatasi")]
        SAB = KASt + [(t["ad"], t["shape"]) for t in T if t["grup"].endswith("_Govde")]
        sat = []
        for th in (0.0, 3.0, 3.5, 3.75, 4.0, 4.5, 5.0):
            kol = [(a, tasi(s, O.Pr(th))) for a, s in KOLt]
            cak = []
            en = (1e9, None, None)
            for a, s in kol:
                for b, q in GOBt + SAB:
                    if not s.BoundBox.intersect(q.BoundBox):
                        bb = App.BoundBox(s.BoundBox)
                        bb.enlarge(3)
                        if not bb.intersect(q.BoundBox):
                            continue
                    d = s.distToShape(q)[0]
                    if d < en[0]:
                        en = (round(d, 3), a, b)
                    if d < 1e-6:
                        v = s.common(q).Volume
                        if v > 1e-3:
                            cak.append((a, b, round(v, 2)))
            sat.append(dict(S2=th, cakisma=cak, en_kucuk=en))
            log(taraf, th, cak, en, "%.0fs" % (time.time() - t0))
        ev[taraf] = dict(kol_parca=[a for a, _ in KOLt], satir=sat)
    OUT["ev_pozu"] = ev
    O.kaydet(JS, OUT)

if ADIM in ("hepsi", "kolkaset"):
    T = TY["sag"]
    KOLt = taslak_kol("sag")
    UST = [(t["ad"], t["shape"]) for t in TKOL["sag"] if t["grup"].endswith(("_Kol", "_UstKol"))]
    ALT = [(t["ad"], t["shape"]) for t in TKOL["sag"] if t["grup"].endswith(("_OnKol", "_El"))]
    KASt = [(t["ad"], t["shape"]) for t in T if t["ad"].startswith("S1 kaset") or t["ad"].startswith("Kaset civatasi")]
    D = A.DIRSEK
    # taslakta dirsek ekseni DY-30 -> sag omuz yerelinde -UST_KOL_UZAMA kaymis
    ey, ez = D["eksen_y"] - TA.UST_KOL_UZAMA, D["eksen_z"]

    def Pe(al):
        return App.Placement(V(0, 0, 0), App.Rotation(V(*D["eksen_yon"]), al), V(0, ey, ez))
    sat = []
    TH = [float(x) for x in range(5, 21)] + [30.0, 45.0, 60.0, 75.0, 90.0, 105.0, 120.0]
    for phi in range(-45, 136, 5):
        kas = [(a, tasi(s, O.Pp(float(phi)).inverse())) for a, s in KASt]      # kaseti gobek cercevesine al (kol hareketli)
        for th in TH:
            for al in (0.0, 52.5, 105.0):
                pl = O.Pr(th)
                hs = [(a, tasi(s, pl)) for a, s in UST] + [(a, tasi(s, pl.multiply(Pe(al)))) for a, s in ALT]
                d, a, b = O.enaz(hs, kas, pay=3)
                sat.append((phi, th, al, round(d, 3), a, b))
        log("kolkaset phi", phi, min((q for q in sat if q[0] == phi), key=lambda q: q[3]), "%.0fs" % (time.time() - t0))
        OUT["kol_kaset"] = dict(en_kucuk=sorted(sat, key=lambda q: q[3])[:12], poz=len(sat),
                                S2_basina=sorted({th: min((q for q in sat if q[1] == th), key=lambda q: q[3]) for th in TH}.items()))
        O.kaydet(JS, OUT)

O.kaydet(JS, OUT)
log("bitti %.0fs" % (time.time() - t0))
