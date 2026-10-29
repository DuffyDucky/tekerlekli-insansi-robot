# Y3 (M6 CAD): C1 / C2 / C3 alet erisimi, 1,65 m modul FCStd'lerinde. CAD'i YALNIZ OKUR.
# Olcum modeli planlama/adim4/M6_erisim.py ile birebir (fonksiyonlar o dosyadan okunur: eksen, serbest, kol_salinim, egik,
# somun_erisim, erisim); burada yalniz montaj adimi ve engel kumesi elle secilir (modul yerel koordinati yeterli: engeller ayni modulde).
# Calistir: FC_SCRIPT=<bu dosya> Y3_ETIKET=once|sonra "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
# Cikti: planlama/y3/Y3-erisim-<etiket>.json
import os, sys, json, time, math
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(HERE))
FC = os.path.join(KOK, "tasarim", "freecad")
V = App.Vector
t0 = time.time()

# --- olcum fonksiyonlari: M6_erisim.py'den (alet tablolari + "civata ekseni" ... "erisim" bolumu)
src = open(os.path.join(KOK, "planlama", "adim4", "M6_erisim.py"), encoding="utf-8").read()
bas = src.index("# ---------------------------------------------------------------- aletler")
son = src.index("# ---------------------------------------------------------------- montaj adimlari")
g = {"App": App, "Part": Part, "V": V, "math": math}
exec(src[bas:son], g)
bas = src.index("# ---------------------------------------------------------------- civata ekseni")
son = src.index("for p in P:\n    p[\"sbb\"]")
exec(src[bas:son], g)
erisim, somun_erisim = g["erisim"], g["somun_erisim"]


def yukle(dosya):
    d = App.openDocument(os.path.join(FC, dosya))
    P = []
    for o in d.Objects:
        if o.TypeId != "Part::Feature" or not hasattr(o, "Tur") or o.Tur == "Referans":
            continue
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        gr = [x.Label for x in o.InList if x.TypeId == "App::Part"]
        bb = s.BoundBox
        bb.enlarge(0.01)
        P.append(dict(modul=dosya.split("/")[0], grup=gr[0] if gr else "", ad=o.Label, kod=o.Kod, tur=o.Tur, shape=s, sbb=bb))
    App.closeDocument(d.Name)
    return P


def olc(P, hedef, engel_f, ad):
    engel = [e for e in P if engel_f(e)]
    out = []
    for p in P:
        if not hedef(p):
            continue
        if g["somun_mu"](p["kod"]):
            r = somun_erisim(p["shape"], engel, p, p["kod"])
        else:
            r = erisim(p, engel)
        c = p["shape"].BoundBox.Center
        out.append(dict(ad=p["ad"], kod=p["kod"], merkez=[round(c.x, 1), round(c.y, 1), round(c.z, 1)], sonuc=r))
    say = {}
    for o in out:
        k = (o["sonuc"] or {}).get("sinif")
        say[k] = say.get(k, 0) + 1
    print(ad, say)
    return dict(durum=ad, engel_sayisi=len(engel), sayac=say, baglanti=out)


SONUC = dict(betik="planlama/y3/Y3_erisim.py", model="planlama/adim4/M6_erisim.py fonksiyonlari", olcum=[])
# C1 / C3 omuz: G1 (gobek -> S1 horn; S2 servosu, mafsal, kol yok) ve G2 (S2 servosu + somunlar; kol yok)
P = yukle("omuz/omuz-montaj.FCStd")
yok_g1 = ("S2", "625ZZ", "Mafsal", "M5 (gobekte)")
SONUC["olcum"].append(olc(P, lambda p: p["ad"].startswith("Gobek-horn"),
                          lambda e: e["grup"].startswith("Govde") or (e["grup"].startswith("Omuz_gobegi")
                                                                     and not any(s in e["ad"] for s in yok_g1)),
                          "C1 omuz G1: gobek-horn M3x12 (S2 servosuz)"))
SONUC["olcum"].append(olc(P, lambda p: p["ad"].startswith("S2 kontra") or p["ad"].startswith("S2 kulak"),
                          lambda e: e["grup"].startswith("Govde") or e["grup"].startswith("Omuz_gobegi"),
                          "C3 omuz G2: S2 kulak cıvatasi + kontra somun (kol yok)"))
# C2 dirsek: H0a tezgah (on kol + dirsek / bilek servosu; horn, catal, el yok)
P = yukle("dirsek/dirsek-montaj.FCStd")
SONUC["olcum"].append(olc(P, lambda p: p["grup"].startswith("On_kol") and ("kulak" in p["ad"] or "kontra" in p["ad"]),
                          lambda e: e["grup"].startswith("On_kol") and "horn" not in e["ad"],
                          "C2 dirsek H0a: dirsek / bilek servosu kulak + somun (tezgah)"))
# C3 kafa: E2 (boyun + pan grubu takili; kafa yok)
P = yukle("kafa/kafa-montaj.FCStd")
SONUC["olcum"].append(olc(P, lambda p: p["ad"].startswith("Tilt servosu ku") or p["ad"].startswith("Tilt servosu ko")
                          or p["ad"].startswith("Somun M3 DIN 985 (saplama"),
                          lambda e: e["grup"].startswith("Boyun") or e["grup"].startswith("Pan"),
                          "C3 kafa E2: tilt servosu kulak + kontra somun; adaptor saplama somunlari"))
SONUC["sure_s"] = round(time.time() - t0, 1)
et = os.environ.get("Y3_ETIKET", "once")
with open(os.path.join(HERE, "Y3-erisim-%s.json" % et), "w", encoding="utf-8") as f:
    json.dump(SONUC, f, ensure_ascii=False, indent=1)
print("bitti %.0f s" % (time.time() - t0))
