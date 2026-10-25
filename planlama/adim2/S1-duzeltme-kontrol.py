# S1 kaseti Y1b duzeltmeleri - tasarim ajaninin KISA yerlesim kontrolu (25 Ekim 2026). Tam bagimsiz kontrol ayri ajanda.
# Yalniz okur (FCStd'ler gecici kopyadan, K2-ortak.py yardimcilari). Cikti: S1-duzeltme-kontrol.json
#   1) K2: tambur baglama ipi <-> omuz govdesi (kapak civatasi, rulman kapagi ...) ve kaset (govde, kapak, civata), S1 -60...180 / 1
#      (olcut >= 0,3); ip <-> tambur ortak hacim; tambur <-> sabit (onceki 0,50 / civata basi 0,709)
#   2) K3: flans pahi (kapak ic kenari x 158,3 / 159,5'te en kucuk r)
#   3) ikinci pim: delik <-> duvar ic yuzu (U'nun suprudugu halka r < 75,2), pim <-> delik; kulak <-> kabuk diger parcalari
#   4) duvar bagi ip delikleri: kaset govdesinde bosluk var mi (radyal isinla)
#   5) kaset (govde + kapak + civata) <-> kol (omuz Kol + dirsek UstKol) S1 -45...135 / 5 x S2 {5, 10, 20, 45, 90, 120}; <-> gobek S1 -60...180 / 5
# Calistir: FC_SCRIPT=<bu dosya> "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import FreeCAD as App
import Part

A, V, log, tasi = O.A, O.V, O.log, O.tasi
t0 = time.time()
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"))
S1 = A.KOL_KABLO["s1"]
OMU = O.ac("omuz/omuz-montaj.FCStd")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd")
OUT["girdi"] = dict(O.GIRDI)
GOB = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Gobek"]
GOV = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Govde" and p["tur"] != "Referans" and "traversi" not in p["ad"]]
KOL = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Kol"] + [(p["ad"], p["shape"]) for p in DIR if p["grup"] == "UstKol"]
KASET = [(p["ad"], p["shape"]) for p in KAB if p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi")]
KG = dict(KASET)
GOVDE, KAPAK = KG["S1 kaset govdesi sag"], KG["S1 kaset kapagi sag"]
KAB_D = [(p["ad"], p["shape"]) for p in KAB if not (p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi"))]
IP = [s for a, s in GOB if a == "S1 tambur baglama ipi"]
TAMBUR = [s for a, s in GOB if a == "S1 kablo tamburu"][0]
log("parca: gobek %d, govde %d, kol %d, kaset %d, ip %d" % (len(GOB), len(GOV), len(KOL), len(KASET), len(IP)))


def en_yakin(a, hedef, pay=5.0):
    bb = a.BoundBox
    bb.enlarge(pay)
    en = (1e9, None)
    for ad, s in hedef:
        if not bb.intersect(s.BoundBox):
            continue
        d = a.distToShape(s)[0]
        if d < en[0]:
            en = (d, ad)
    return en


# ---------------------------------------------------------------- 1) K2 tambur baglama ipi
r = dict(ip_tambur_ortak_mm3=[round(s.common(TAMBUR).Volume, 4) for s in IP])
en_ip = {}
en_tb = {}
for phi in range(-60, 181):
    for k, s in enumerate(IP):
        sm = tasi(s, O.Pp(phi))
        for grp, hed in (("omuz_govde", GOV), ("kaset", KASET)):
            d, ad = en_yakin(sm, hed)
            key = "%s|%s" % (grp, ad)
            if ad and (key not in en_ip or d < en_ip[key][0]):
                en_ip[key] = (round(d, 3), phi, k)
    if phi % 2 == 0:
        tm = tasi(TAMBUR, O.Pp(phi))
        for grp, hed in (("omuz_govde", GOV), ("kaset", KASET)):
            d, ad = en_yakin(tm, hed)
            key = "%s|%s" % (grp, ad)
            if ad and (key not in en_tb or d < en_tb[key][0]):
                en_tb[key] = (round(d, 3), phi)
r["ip_en_yakin"] = dict(sorted(en_ip.items(), key=lambda kv: kv[1][0]))
r["ip_min_mm"] = min(v[0] for v in en_ip.values())
r["ip_olcut_0_3"] = bool(r["ip_min_mm"] >= 0.3)
r["tambur_en_yakin_2derece"] = dict(sorted(en_tb.items(), key=lambda kv: kv[1][0]))
OUT["K2_tambur_ip"] = r
log("K2 ip:", r["ip_min_mm"], list(r["ip_en_yakin"].items())[:4], "tambur:", list(r["tambur_en_yakin_2derece"].items())[:3], "%.0fs" % (time.time() - t0))


# ---------------------------------------------------------------- 2) K3 flans pahi
def r_min_x(sh, x):
    rm = 1e9
    for w in sh.slice(V(1, 0, 0), x):
        for e in w.Edges:
            for q in e.discretize(200):
                rm = min(rm, math.hypot(q.y, q.z))
    return rm


OUT["K3_pah"] = {("x %.2f" % x): round(r_min_x(KAPAK, x), 3) for x in (158.35, 158.9, 159.45)}
log("K3 pah (kapak ic kenari r):", OUT["K3_pah"])

# ---------------------------------------------------------------- 3) ikinci pim + 4) duvar ip delikleri
P2 = S1["duvar"]["pim2"]
c2 = V(155.0, *O.psi_yz(P2["psi"], P2["r"])) if hasattr(O, "psi_yz") else None
if c2 is None:
    a_ = math.radians(P2["psi"])
    c2 = V(155.0, P2["r"] * math.cos(a_), -P2["r"] * math.sin(a_))
duvar_ic = Part.makeCylinder(S1["duvar"]["r"][0], 10.0, V(150.0, 0, 0), V(1, 0, 0))
delik_r = P2["d"] / 2 + 0.1
OUT["pim2"] = dict(merkez_yz=[round(c2.y, 2), round(c2.z, 2)], delik_ic_r=round(P2["r"] - delik_r, 2), duvar_ic_r=S1["duvar"]["r"][0],
                   duvar_dis_r=S1["duvar"]["r"][1], kanal_payi_mm=round(P2["r"] - delik_r - S1["duvar"]["r"][0], 2),
                   govde_kapak_ortak_mm3=round(GOVDE.common(KAPAK).Volume, 4),
                   kulak_kabuk_en_yakin=en_yakin(GOVDE, KAB_D, 2.0), kapak_kabuk_en_yakin=en_yakin(KAPAK, KAB_D, 2.0))
# pim varligi: kapakta x 156 kesitinde pim2 merkezi icinde mi; govdede ayni noktada bosluk (delik)
pp = V(156.5, c2.y, c2.z)
OUT["pim2"]["kapak_pim_var"] = bool(KAPAK.isInside(pp, 1e-6, True))
OUT["pim2"]["govde_delik_bos"] = bool(not GOVDE.isInside(pp, 1e-6, True))
OUT["pim2"]["govde_kulak_var"] = bool(GOVDE.isInside(V(156.5, c2.y * (P2["r"] + 2.5) / P2["r"], c2.z * (P2["r"] + 2.5) / P2["r"]), 1e-6, True))
dl = []
DI = S1["duvar"]["ip"]
for ps in S1["duvar"]["ip_psi"]:
    a_ = math.radians(ps)
    for nm, (x0, x1) in (("arka", DI["arka_x"]), ("ust", DI["ust_x"])):
        q = V(0.5 * (x0 + x1), 76.2 * math.cos(a_), -76.2 * math.sin(a_))
        q2 = V(0.5 * (x0 + x1), 76.2 * math.cos(a_ + 0.03), -76.2 * math.sin(a_ + 0.03))      # deligin 2,3 mm yaninda duvar dolu mu
        dl.append(dict(psi=ps, yer=nm, delik_bos=bool(not GOVDE.isInside(q, 1e-6, True)), yaninda_duvar=bool(GOVDE.isInside(q2, 1e-6, True))))
OUT["duvar_ip_delik"] = dl
log("pim2:", OUT["pim2"], "duvar ip:", dl)

# ---------------------------------------------------------------- 5) kaset <-> kol / gobek
kk = {}
for phi in range(-45, 136, 5):
    for th in (5, 10, 20, 45, 90, 120):
        pl = O.Pp(phi).multiply(O.Pr(th))
        for ad, s in KOL:
            sm = tasi(s, pl)
            d, a2 = en_yakin(sm, KASET, 3.0)
            if a2 and (("%s|%s" % (ad, a2)) not in kk or d < kk["%s|%s" % (ad, a2)][0]):
                kk["%s|%s" % (ad, a2)] = (round(d, 3), phi, th)
OUT["kaset_kol"] = dict(sorted(kk.items(), key=lambda kv: kv[1][0])[:10])
kg = {}
for phi in range(-60, 181, 5):
    for ad, s in GOB:
        if ad in ("S1 kablo tamburu", "S1 tambur baglama ipi"):
            continue
        sm = tasi(s, O.Pp(phi))
        d, a2 = en_yakin(sm, KASET, 5.0)
        if a2 and (("%s|%s" % (ad, a2)) not in kg or d < kg["%s|%s" % (ad, a2)][0]):
            kg["%s|%s" % (ad, a2)] = (round(d, 3), phi)
OUT["kaset_gobek"] = dict(sorted(kg.items(), key=lambda kv: kv[1][0])[:6])
log("kaset-kol:", list(OUT["kaset_kol"].items())[:3], "kaset-gobek:", list(OUT["kaset_gobek"].items())[:3])
OUT["sure_s"] = round(time.time() - t0, 1)
json.dump(OUT, open(os.path.join(HERE, "S1-duzeltme-kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("yazildi S1-duzeltme-kontrol.json %.0fs" % (time.time() - t0))
