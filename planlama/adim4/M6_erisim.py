# M6 (duzeltme plani, 4. adim): montaj sirasi + alet erisimi. CAD'i YALNIZ OKUR (modul FCStd'leri), hicbir modul dosyasina yazmaz.
# Cikti: planlama/adim4/M6_erisim_sonuc.json. Calistirma (README baslaticisi):
#   FC_SCRIPT=<bu dosya> "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
#
# Yontem
# - Tum moduller ev pozunda global koordinata yuklenir (m6_yukle.py; sol = X aynasi). Her parca bir montaj ADIMINA atanir
#   (ADIMLAR, adim_bul). Bir baglanti elemaninin erisimi, o adimda takili olan (adim no <= kendi adimi) tum parcalar engel
#   sayilarak olculur; ayrica "servis" durumunda (robot tam kapali, tum parcalar) yeniden olculur.
# - Civata ekseni sekilden (silindirik yuzler), bas ucu uclardaki yaricap/kose sayisindan bulunur. Alet: bas ustunden disari,
#   eksen boyunca r = 0,58 s + 0,6 mm silindir (alyan kose yaricapi + el payi). Serbest boy = ilk engele eksenel uzaklik.
# - Sinif: DUZ (serbest >= uzun kol + 20: tornavida tipi alyan/bits), L (serbest >= kisa kol ve kisa kol ucunda uzun kolun
#   donecegi >= 45 derece serbest yay), ACILI (kisa kol sigmiyor ama 25 derece egik kuresel uclu uzun kol serbest), YOK.
#   Somunlar (DIN 934/985): eksenel lokma (r = 0,58 s + 2) ya da yandan acik agiz (12 yon, somun duzleminde).
import os, sys, math, json, time
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m6_yukle as Y

V = App.Vector
t0 = time.time()

# ---------------------------------------------------------------- aletler (ISO 2936 L alyan yaklasik olculeri; tahmini)
ALYAN_S = {"M2,5x": 2.0, "M2x": None, "M3x": 2.5, "M4x": 3.0, "M5x": 4.0, "M6x": 5.0}
ISO7380_S = {"M3x": 2.0, "M6x": 4.0}
DIN913_S = {"M6x": 3.0, "M5x": 2.5}
KISA_KOL = {1.5: 14.0, 2.0: 16.0, 2.5: 18.0, 3.0: 20.0, 4.0: 25.0, 5.0: 28.0}
UZUN_KOL = {1.5: 75.0, 2.0: 80.0, 2.5: 90.0, 3.0: 100.0, 4.0: 110.0, 5.0: 125.0}
SOMUN_S = {"M3": 5.5, "M4": 7.0, "M5": 8.0, "M6": 10.0}


def alet(kod):
    """kod -> (alet adi, s, r_alet, kisa, uzun) | None (alet gerekmez)."""
    k = kod
    if "DIN 912" in k:
        for pre, s in ALYAN_S.items():
            if k.startswith(pre) and s:
                return ("alyan %.1f" % s, s, 0.58 * s + 0.6, KISA_KOL[s], UZUN_KOL[s])
    if "ISO 7380" in k:
        for pre, s in ISO7380_S.items():
            if k.startswith(pre):
                return ("alyan %.1f" % s, s, 0.58 * s + 0.6, KISA_KOL[s], UZUN_KOL[s])
    if "DIN 913" in k:
        for pre, s in DIN913_S.items():
            if k.startswith(pre):
                return ("alyan %.1f" % s, s, 0.58 * s + 0.6, KISA_KOL[s], UZUN_KOL[s])
    if "horn vidasi" in k:
        return ("yildiz PH1", 0, 3.0, 60.0, 60.0)          # duz tornavida: kisa kol yok, en az 60 mm duz
    if "PT vida" in k:
        return ("yildiz PH0", 0, 2.5, 50.0, 50.0)
    return None


def somun_mu(kod):
    return ("DIN 985" in kod or "DIN 934" in kod) and "somun" in kod


# ---------------------------------------------------------------- montaj adimlari (rehber sirasi)
# (no, kod, baslik, secici). Secici parca dict'i alir (m, g, ad, kod, tur); ilk eslesen adim kazanir. Sol/sag ayni adimda.
def _m(*mods):
    return lambda p: p["modul"] in mods


def _ad(*parcalar):
    return lambda p: any(s in p["ad"] for s in parcalar)


def _ve(*f):
    return lambda p: all(x(p) for x in f)


def _veya(*f):
    return lambda p: any(x(p) for x in f)


def _g(*gr):
    return lambda p: any(p["grup"].startswith(x) for x in gr)



# Tezgah alt montajlari ve adim ici sira: listede once gelen secici kazanir; bunlar genel adimlardan once denenir.
# 5. eleman = tezgah anahtari: o adimdaki bir baglantinin engelleri yalniz ayni anahtarli (ve no <= kendi) parcalardir.
_O = _m("omuz_sag", "omuz_sol")
_D = _m("dirsek_sag", "dirsek_sol")
ONCE = [
    (3.9, "B1a", "Tezgah: alt plakaya kart burclari (alttan) + aku takozu", _ve(_m("taban"), _veya(
        _ve(_g("Guc_aku"), _ad("naylon burc", " alt)")), _ad("takoz", "Isil gomme"), _ad("Alt plaka"))), "plaka"),
    (4.6, "B2a", "Motor braketleri -> alt plaka (M4 + cekic somun)", _ve(_m("taban"), _g("Tahrik"), _veya(
        _ad("braketi", "(braket", "Cekic somun M4"), lambda p: p["ad"].startswith("Pul M4")))),
    (4.7, "B2b", "Motorlar -> braket (6 x M3x6)", _ve(_m("taban"), _g("Tahrik"), _ad("Motor JGB", "(motor"))),
    (7.5, "C0", "Etek braketleri -> uzun ray ust kanali (M6; guc paneli ve elektronik katindan ONCE)", _ve(_m("kabuk"),
        _g("Etek_braket"), lambda p: "M3x8" not in p["kod"])),
    (7.9, "B5a", "Tezgah: guc paneline sigorta kutusu, role, ana sigorta, ana anahtar", _ve(_m("taban"), _veya(
        _ad("Guc paneli", "Sigorta", "sigorta", "Role", "role", "Ana anahtar ASW", "Somun M4"),
        lambda p: p["ad"].startswith("Pul M4") and p["grup"].startswith("Guc"))), "guc"),
    (8.9, "B6a", "Tezgah: elektronik katina burclar (alttan) + kartlar (ustten)", _ve(_m("taban"), _veya(
        _g("Elektronik"), _ad("Elektronik kati"))), "kat"),
    (12.1, "D1a", "Tezgah: omuz yuvasi + S1 servo (4 x M4 + kontra)", _ve(_O, _veya(
        _ad("Omuz yuvasi", "S1 servo", "S1 kulak", "S1 kontra"))), "omuz"),
    (12.2, "D1b", "Tezgah: 6808 + rulman kapagi (4 x M3x12, yuvada isil gomme)", _ve(_O, _g("Govde_sabit"), _ad(
        "6808", "Rulman kapagi", "Kapak civatasi", "Isil gomme somun M3 (yuvada)")), "omuz"),
    (12.3, "D1c", "Tezgah: S1 horn + merkez vidasi (servo ortada)", _ve(_O, _ad("S1 horn")), "omuz"),
    (13.9, "E1a", "Tezgah: boyun (servo yuvasi, pan servosu, rulman yuvasi, rulmanlar, boyun plakasi)", _ve(_m("kafa"),
        _g("Boyun"), lambda p: "Boyun civata" not in p["ad"] and "Cekic somun" not in p["ad"]), "boyun"),
    (14.5, "E2a", "Pan horn + merkez vidasi", _ve(_m("kafa"), _ad("Pan horn"))),
    (14.6, "E2b", "Boyun mili + rulman ic bilezikleri, mil-horn 4 x M3x8", _ve(_m("kafa"), _g("Pan"), _ad(
        "Boyun mili", "ic bilezik", "Mil-horn"))),
    (14.7, "E2c", "Egme catali, catal-mil 4 x M3x8", _ve(_m("kafa"), _g("Pan"), _ad("Egme catali", "Catal-mil",
                                                                                   "Isil gomme somun M3"))),
    (15.9, "E3a", "Tezgah: kafa ici (iskelet, LCD, Pi 5, kamera, cevirici, amfi, tilt horn)", _ve(_m("kafa"), _g("Kafa_tilt"),
        lambda p: not any(s in p["ad"] for s in ("Yuz kabugu", "Arka kafa", "Vizor", "Kabuk civatasi"))), "kafa"),
    (16.9, "E4a", "Tezgah: kafa kabuklari + vizor", _ve(_m("kafa"), _g("Kafa_tilt")), "kafa"),
    (22.5, "G0", "Tezgah: gobek + S1 kablo tamburu (3 x M3x8, -x yuzden)", _ve(_O, _ad("Omuz gobegi", "S1 kablo tamburu",
        "Tambur civatasi", "Isil gomme somun M3 (gobekte)")), "gobek"),
    (25.5, "G4", "S1 kablo kaseti (kabuk): 2 dikme M3x8 + ust kulak", _ve(_m("kabuk"), _ad("aset", "Kaset"))),
    (25.61, "H0a", "Tezgah: on kol + dirsek ve bilek servolari (8 x M4 + kontra)", _ve(_D, _veya(
        _ad("On kol govdesi", "Dirsek servosu", "Bilek servosu")), lambda p: "horn" not in p["ad"]), "dirsek"),
    (25.62, "H0b", "Tezgah: dirsek horn + merkez vidasi", _ve(_D, _ad("Dirsek horn")), "dirsek"),
    (25.63, "H0c", "Tezgah: dirsek catali (catal-horn 4 x M3x8, 625ZZ, M5 pim)", _ve(_D, _veya(
        _g("Dirsek_ust"), _g("On_kol")), lambda p: "Bilezik" not in p["ad"]), "dirsek"),
    (25.64, "H0d", "Tezgah: bilek horn + merkez vidasi", _ve(_D, _ad("Bilek horn")), "dirsek"),
    (25.65, "H0e", "Tezgah: bilek flansi (flans-horn 4 x M3x8)", _ve(_D, _ad("Bilek flansi", "Flans-horn")), "dirsek"),
    (25.66, "H0f", "Tezgah: el (yaka 2 x M3x6 ISO 7380)", _ve(_D, _g("El")), "dirsek"),
]

ADIMLAR = [
    (1, "A1", "Sase cercevesi: 2 uzun + 3 ara ray, 8 ic kose baglanti (set vida)", _ve(_m("iskelet"), _g("Sase"))),
    (2, "A2", "Govde diregi + direk-ray kose baglantilari", _ve(_m("iskelet"), _g("Govde_diregi"))),
    (3, "A3", "Omuz traversi + direk-travers kose baglantilari", _ve(_m("iskelet"), _g("Omuz_traversi"))),
    (4, "B1", "Alt plaka (tezgahta alt yuzune kart burclari) -> sase, alttan M6", _ve(_m("taban"), _veya(
        _ad("Alt plaka", "(plaka,"), _ve(_g("Guc_aku"), _ad("naylon burc", " alt)")), _ad("takoz", "Isil gomme")))),
    (5, "B2", "Kaplinler + tekerler (motorlardan sonra)", _ve(_m("taban"), _g("Tahrik"))),
    (6, "B3", "Alt plaka kartlari (2 x BTS7960, 3 x XL4016) + aku + kayislar", _ve(_m("taban"), _g("Guc_aku"), _veya(
        _ad("BTS7960", "XL4016", "Aku"), _ad(" ust)")), lambda p: "kutusu" not in p["ad"] and "Role" not in p["ad"])),
    (7, "B4", "Kat burclari M5x40 (saplama + cekic somun)", _ve(_m("taban"), _ad("Burc M5x40", "Saplama", "Cekic somun M5"))),
    (8, "B5", "Guc paneli (tezgahta: sigorta kutusu, role, ana sigorta, ana anahtar) -> burclara", _ve(_m("taban"), _veya(
        _ad("Guc paneli", "Sigorta", "sigorta", "Role", "role", "Ana anahtar ASW", "Somun M4", "Pul M4 ("),
        _ve(_ad("(kat "), lambda p: _z_kat(p) < 0)))),
    (9, "B6", "Elektronik kati (tezgahta: burclar alttan, kartlar ustten) -> burclara", _ve(_m("taban"), _veya(
        _g("Elektronik"), _ve(_ad("(kat "), lambda p: _z_kat(p) >= 0)))),
    (10, "B7", "Sonar tutuculari + sonarlar (on ara ray)", _ve(_m("taban"), _g("Sonar"), lambda p: "Acil" not in p["ad"])),
    (11, "K1", "Kablolama kapisi 1: taban (aku, guc, motor, kartlar)", lambda p: False),
    (12, "C1", "Kabuk braketleri: 4 govde braketi -> direk (M6), 6 etek braketi -> uzun ray (M6)", _ve(_m("kabuk"), _g(
        "Govde_braket", "Etek_braket"), lambda p: not ("M5" in p["kod"] or "M3x8" in p["kod"]))),
    (13, "D1", "Omuz govdesi (tezgahta: yuva, S1 servo, rulman kapagi, S1 horn) -> travers ucu, 4 x M6", _veya(
        _ve(_m("omuz_sag", "omuz_sol"), _g("Govde_sabit")), _ve(_m("omuz_sag", "omuz_sol"), _ad("S1 horn")))),
    (14, "E1", "Kafa boynu (tezgahta: servo yuvasi, pan servosu, rulman yuvasi) -> travers ustu, 2 x M6", _ve(_m("kafa"),
                                                                                                       _g("Boyun"))),
    (15, "E2", "Pan grubu: boyun mili, egme catali, tilt servosu", _ve(_m("kafa"), _g("Pan"))),
    (16, "E3", "Kafa ici (tezgahta): iskelet, LCD, Pi 5, kamera, cevirici, amfi", _ve(_m("kafa"), _g("Kafa_tilt"), lambda p:
                                                                                     not any(s in p["ad"] for s in (
                                                                                         "Yuz kabugu", "Arka kafa", "Vizor",
                                                                                         "Kabuk civatasi"))
                                                                                     )),
    (17, "E4", "Kafa kabuklari + vizor", _ve(_m("kafa"), _g("Kafa_tilt"))),
    (18, "K2", "Kablolama kapisi 2: govde ici (servo uzatmalari, kafa 12 V, Nextion, sinyal) - KABUKTAN ONCE", lambda p: False),
    (19, "F1", "Taban etegi: 6 bant + acil stop + ana anahtar dugmesi (etek braketi M3 iceriden)", _veya(
        _ve(_m("kabuk"), _veya(_g("Taban_etegi"), _ve(_g("Etek_braket"), lambda p: "M3x8" in p["kod"])),
            ), _ve(_m("taban"), _ad("Acil stop")))),
    (20, "F2", "Govde alt + orta bantlari (govde braketi M5 iceriden)", _ve(_m("kabuk"), _veya(
        _ad("Govde alt bandi", "Govde orta bandi"), _ve(_g("Govde_braket"), lambda p: "M5" in p["kod"] and _y(p) < 690.0),
        lambda p: p["grup"] == "Govde_kabugu" and p["tur"] == "Baglanti" and _y(p) < 690.0 and not _arka_kapak(p)))),
    (21, "F3", "Gogus bantlari + Nextion (ekran civatalari iceriden)", _ve(_m("kabuk"), _veya(
        _ad("Gogus bandi"), _g("Gogus_ekrani"), _ve(_g("Govde_braket"), lambda p: "M5" in p["kod"]),
        lambda p: p["grup"] == "Govde_kabugu" and p["tur"] == "Baglanti" and _y(p) < 883.0 and not _arka_kapak(p)))),
    (22, "F4", "Omuz bantlari (O84 rulman kapagini gecer; ust kapak boyunu sarar)", _ve(_m("kabuk"), _veya(
        _ad("Omuz bandi"), lambda p: p["grup"] == "Govde_kabugu" and p["tur"] == "Baglanti" and "Arka" not in p["ad"]
        and not _arka_kapak(p)))),
    (23, "G1", "Omuz gobegi + tambur -> S1 horn (gobek-horn M3x12; S2 servosu henuz yok)", _ve(_m("omuz_sag", "omuz_sol"),
                                                                                           _g("Omuz_gobegi"), lambda p: not any(
            s in p["ad"] for s in ("S2", "625ZZ", "Mafsal", "M5 (gobekte)")))),
    (24, "G2", "S2 servosu gobege + mafsal (625ZZ, M5 pim)", _ve(_m("omuz_sag", "omuz_sol"), _g("Omuz_gobegi"))),
    (25, "G3", "Kol catali (S2 horn) + ust kol tupu", _ve(_m("omuz_sag", "omuz_sol"), _g("Ust_kol"))),
    (26, "H1", "Dirsek modulu (tezgahta: on kol, servolar, el) -> tupe, bilezik 2 x M3x20", _m("dirsek_sag", "dirsek_sol")),
    (27, "F5", "Arka servis kapagi (son)", _m("kabuk")),
    (28, "X", "kalan (atanmamis)", lambda p: True),
]
ADIMLAR = [a if len(a) == 5 else a + (None,) for a in ONCE + ADIMLAR]
TEZGAH = {a[0]: a[4] for a in ADIMLAR}


def _z_kat(p):
    return 0.5 * (p["bb"][4] + p["bb"][5])


def _y(p):
    return 0.5 * (p["bb"][2] + p["bb"][3])


def _arka_kapak(p):
    b = p["bb"]
    AK = Y.A.ARKA_KAPAK
    return b[5] < -70 and abs(0.5 * (b[0] + b[1])) < AK["x"] + 15 and AK["y0"] - 15 < _y(p) < AK["y1"] + 15


def adim_bul(p):
    for no, kod, bas, f, _k in ADIMLAR:
        if f(p):
            return no
    return 99


# ---------------------------------------------------------------- yukle
P = [p for p in Y.yukle() if p["tur"] != "Referans"]
for p in P:
    b = p["shape"].BoundBox
    p["bb"] = (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)
for p in P:
    p["adim"] = adim_bul(p)
print("yuklendi: %d parca, %.0f s" % (len(P), time.time() - t0))


# ---------------------------------------------------------------- civata ekseni ve bas ucu
def eksen(s):
    cyl = [f for f in s.Faces if f.Surface.TypeId == "Part::GeomCylinder"]
    if not cyl:
        return None
    f = min(cyl, key=lambda f: (f.Surface.Radius, -f.Area))           # en ince silindir: govde (sap)
    u = V(f.Surface.Axis).normalize()
    c = V(f.Surface.Center)
    ts = [(v.Point - c).dot(u) for v in s.Vertexes]
    t0_, t1_ = min(ts), max(ts)

    def uc(tu):
        pts = [v.Point for v in s.Vertexes if abs((v.Point - c).dot(u) - tu) < 0.6]
        rr = [((q - c) - u * (q - c).dot(u)).Length for q in pts]
        return (max(rr) if rr else 0.0), len(pts)

    r0, n0 = uc(t0_)
    r1, n1 = uc(t1_)
    bas_ust = (r1 > r0 + 0.1) or (abs(r1 - r0) <= 0.1 and n1 > n0)
    if bas_ust:
        return c + u * t1_, u                                        # bas ucu t1, alet +u yonunde disari
    return c + u * t0_, u * -1


def serbest(p0, u, r, L, engel, haric):
    """p0'dan u yonunde r yaricapli silindirin ilk engele eksenel uzakligi (L'ye kadar) ve engel adi."""
    cy = Part.makeCylinder(r, L, p0 + u * 0.15, u)
    bb = cy.BoundBox
    best, kim = L, None
    for e in engel:
        if e is haric or not e["sbb"].intersect(bb):
            continue
        try:
            c = cy.common(e["shape"])
        except Exception:
            continue
        if c.Volume > 1e-3:
            pts = [v.Point for v in c.Vertexes]
            for ed in c.Edges:
                try:
                    pts += ed.discretize(12)
                except Exception:
                    pass
            t = min((q - p0).dot(u) for q in pts) if pts else 0.0
            if t < best:
                best, kim = max(0.0, t), e["ad"] + " [" + e["modul"] + "]"
    return best, kim


def dik_yonler(u, n):
    a = V(1, 0, 0) if abs(u.x) < 0.9 else V(0, 1, 0)
    e1 = (a - u * a.dot(u)).normalize()
    e2 = u.cross(e1)
    return [e1 * math.cos(2 * math.pi * k / n) + e2 * math.sin(2 * math.pi * k / n) for k in range(n)]


def kol_salinim(p0, u, s, kisa, engel, haric):
    """Kisa kol ucunda uzun kolun (70 mm, s x s) donebilecegi 15 derecelik yonler; en uzun ardisik serbest yay (derece)."""
    n = 24
    q = p0 + u * kisa
    serb = []
    for d in dik_yonler(u, n):
        # kol: q'dan d yonunde 70 mm, kesit s+1
        w = u.cross(d)
        o = q - w * ((s + 1) / 2) - u * ((s + 1) / 2)
        kol = Part.makeBox(70.0, s + 1, s + 1, V(0, 0, 0))
        kol.Placement = App.Placement(App.Matrix(d.x, w.x, u.x, o.x, d.y, w.y, u.y, o.y, d.z, w.z, u.z, o.z, 0, 0, 0, 1))
        bb = kol.BoundBox
        ok = True
        for e in engel:
            if e is haric or not e["sbb"].intersect(bb):
                continue
            try:
                if kol.common(e["shape"]).Volume > 1e-3:
                    ok = False
                    break
            except Exception:
                pass
        serb.append(ok)
    en, cur = 0, 0
    for v in serb + serb:
        cur = cur + 1 if v else 0
        en = max(en, min(cur, n))
    return en * 15.0, sum(serb)


def egik(p0, u, r, L, engel, haric, aci=25.0):
    """Kuresel uclu uzun kol: 12 yonde aci kadar egik silindir; serbest olan yon sayisi."""
    k = 0
    for d in dik_yonler(u, 12):
        v = (u * math.cos(math.radians(aci)) + d * math.sin(math.radians(aci))).normalize()
        Lf, _ = serbest(p0 + u * 3.0, v, r, L, engel, haric)
        if Lf >= L - 0.01:
            k += 1
    return k


def somun_erisim(sh, engel, haric, kod=""):
    ss = [v for k_, v in SOMUN_S.items() if kod.startswith(k_ + " ")]
    r_lokma = 0.58 * (ss[0] if ss else 7.0) + 2.0
    ex = eksen(sh)
    out = dict()
    if ex is None:
        return dict(sinif="?")
    # somunda iki uc ayni: iki yone de lokma dene
    c = sh.BoundBox.Center
    u = ex[1]
    best = 0.0
    for sgn in (1, -1):
        ts = [(v.Point - c).dot(u * sgn) for v in sh.Vertexes]
        p0 = c + u * sgn * max(ts)
        Lf, kim = serbest(p0, u * sgn, r_lokma, 60.0, [e for e in engel if e["tur"] != "Baglanti"], haric)
        if Lf > best:
            best, out["lokma_engel"] = Lf, kim
    out["lokma_serbest_mm"] = round(best, 1)
    # yandan acik agiz: somun duzleminde 12 yon, 60 mm, genislik 1,8 s
    kal = 0
    for d in dik_yonler(u, 12):
        w = u.cross(d)
        h = 2.0                                       # agiz kalinligi somun boyunun ortasinda (pul / yuzeye degmesin)
        o = c - w * 9.0 - u * (h / 2)
        kol = Part.makeBox(60.0, 18.0, h)
        kol.Placement = App.Placement(App.Matrix(d.x, w.x, u.x, o.x, d.y, w.y, u.y, o.y, d.z, w.z, u.z, o.z, 0, 0, 0, 1))
        kol = kol.cut(Part.makeCylinder(9.0, 20, c - u * 10, u))
        bb = kol.BoundBox
        ok = True
        for e in engel:
            if e is haric or not e["sbb"].intersect(bb):
                continue
            try:
                if e["tur"] != "Baglanti" and kol.common(e["shape"]).Volume > 1e-3:
                    ok = False
                    break
            except Exception:
                pass
        kal += ok
    out["acik_agiz_yon"] = kal
    out["sinif"] = "LOKMA" if best >= 12 else ("ACIK_AGIZ" if kal >= 2 else "YOK")
    if out["sinif"] == "YOK":
        # altigen cep mi: somun ekseni etrafinda 30 derece donunce cevredeki parcaya giriyorsa somun cepte tutulur (anahtar gerekmez)
        r = sh.copy()
        r.rotate(c, u, 30.0)
        bb = r.BoundBox
        for e in engel:
            if e is haric or not e["sbb"].intersect(bb) or "civata" in e["ad"].lower():
                continue
            try:
                v0 = sh.common(e["shape"]).Volume
                v1 = r.common(e["shape"]).Volume
            except Exception:
                continue
            if v1 - v0 > 0.3:
                out["sinif"] = "CEP"
                out["cep_parca"] = e["ad"]
                break
    return out


def erisim(p, engel):
    a = alet(p["kod"])
    if a is None:
        return None
    ex = eksen(p["shape"])
    if ex is None:
        return dict(sinif="?", not_="eksen bulunamadi")
    p0, u = ex
    ad_, s, r, kisa, uzun = a
    Lmax = uzun + 20.0
    Lf, kim = serbest(p0, u, r, Lmax, engel, p)
    out = dict(alet=ad_, serbest_mm=round(Lf, 1), engel=kim, eksen=[round(u.x, 3), round(u.y, 3), round(u.z, 3)],
               bas=[round(p0.x, 1), round(p0.y, 1), round(p0.z, 1)])
    if Lf >= Lmax - 0.01:
        out["sinif"] = "DUZ"
    elif s and Lf >= kisa + s:
        yay, nserb = kol_salinim(p0, u, s, kisa, engel, p)
        out["salinim_derece"] = yay
        out["sinif"] = "L" if yay >= 45.0 else "L_DAR"
        if out["sinif"] == "L_DAR" and egik(p0, u, r, uzun, engel, p) > 0:
            out["sinif"] = "ACILI"
    elif not s and Lf >= kisa:
        out["sinif"] = "DUZ"
    else:
        out["sinif"] = "ACILI" if (s and egik(p0, u, r, uzun, engel, p) > 0) else "YOK"
    return out


for p in P:
    p["sbb"] = p["shape"].BoundBox
    p["sbb"].enlarge(0.01)

SONUC = dict(betik="planlama/adim4/M6_erisim.py", adimlar=[dict(no=n, kod=k, baslik=b, tezgah=t) for n, k, b, _, t in sorted(ADIMLAR, key=lambda a: a[0])], baglanti=[])
sayac = {}
for p in P:
    if p["tur"] != "Baglanti":
        continue
    a = alet(p["kod"])
    somun = somun_mu(p["kod"])
    if a is None and not somun:
        continue
    tk = TEZGAH.get(p["adim"])
    engel_adim = [e for e in P if e["adim"] <= p["adim"] and (tk is None or TEZGAH.get(e["adim"]) == tk)]
    if somun:
        r_ad = somun_erisim(p["shape"], engel_adim, p, p["kod"])
        r_sv = somun_erisim(p["shape"], P, p, p["kod"])
    else:
        r_ad = erisim(p, engel_adim)
        r_sv = erisim(p, P)
    kayit = dict(modul=p["modul"], grup=p["grup"], ad=p["ad"], kod=p["kod"], adim=p["adim"], montajda=r_ad, serviste=r_sv)
    SONUC["baglanti"].append(kayit)
    k = (p["adim"], r_ad.get("sinif"))
    sayac[k] = sayac.get(k, 0) + 1
print("olculdu: %d baglanti, %.0f s" % (len(SONUC["baglanti"]), time.time() - t0))

# ozet
oz = {}
for b in SONUC["baglanti"]:
    a = oz.setdefault(b["adim"], {})
    a[b["montajda"].get("sinif")] = a.get(b["montajda"].get("sinif"), 0) + 1
SONUC["ozet_montajda"] = {str(k): v for k, v in sorted(oz.items())}
oz2 = {}
for b in SONUC["baglanti"]:
    oz2[b["serviste"].get("sinif")] = oz2.get(b["serviste"].get("sinif"), 0) + 1
SONUC["ozet_serviste"] = oz2
SONUC["parca_adim"] = {}
for p in P:
    if p["tur"] != "Baglanti":
        SONUC["parca_adim"].setdefault(str(p["adim"]), []).append("%s [%s]" % (p["ad"], p["modul"]))
SONUC["sure_s"] = round(time.time() - t0, 1)
with open(os.path.join(HERE, "M6_erisim_sonuc.json"), "w", encoding="utf-8") as f:
    json.dump(SONUC, f, ensure_ascii=False, indent=1)
for k, v in sorted(oz.items()):
    print("adim", k, v)
print("servis:", oz2)
print("bitti %.0f s" % (time.time() - t0))
