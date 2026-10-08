# Moduller arasi carpisma kontrolu (FreeCAD 1.1). arayuz.MODULLER yerlesimiyle modulleri global koordinata
# koyar, (1) ev pozunda tum modul ciftlerini, (2) her hareketli modulun tum tarama pozlarinda hareketli
# parcalarini diger modullere karsi, (3) henuz cizilmemis modullerin ayrilmis bolgelerini (arayuz.BOLGELER)
# tarar, (4) kol zincirini (omuz S1 x S2 x dirsek x bilek; dirsek modulu omuzun Kol grubuna bagli) iskelet, kabuk, taban,
# ayrilmis bolgeler ve kendi omuzunun govde/gobegine karsi, iki kolu da birbirine karsi tarar, (4b) kafayi (pan x tilt)
# sabit modullere (iskelet, kabuk R62 ust kapak, omuz govdeleri, taban, bolgeler) ve iki kolun pozlarina (omuz + dirsek) karsi
# tarar, (4c) tabani: ev pozunda tum modullere (cakisma, temas, en kucuk bosluk), iki kolun tum pozlarina (acil stop, sonar,
# ana anahtar dugmesi, etek ustu) ve kafaya (sinir kutusu) karsi.
# Yeni modul eklemek: MODUL_YUKLE'ye bir yukleyici ekle (parcalar + hareket + haric listesi).
#
# Bolumlu kosu (bellek): CARPISMA_BOLUM ortam degiskeni hangi bolumlerin bu surecte kosacagini secer:
#   statik | omuz | kol_sag | kol_sol | kolkol | kafa_sabit | kafa_sag | kafa_sol | taban   (virgulle birden cok)
#   kisaltmalar: kol = kol_sag,kol_sol; kafa = kafa_sabit,kafa_sag,kafa_sol; hepsi = tum bolumler tek surecte (eski yol)
# Her bolum yalniz gerektigi modulleri yukler ve sonucunu carpisma-bolum/<bolum>.json'a yazar (kosu zamani, sure, tepe bellek).
# Tam sonuc carpisma-bolum/*.json birlestirilerek uretilir: carpisma_kos.py (sistem Python'u) bolumleri SIRAYLA ayri
# freecadcmd sureclerinde kosar ve sonunda birlestirir -> carpisma-sonuc.json. Tek bolum: CARPISMA_BOLUM=taban ile bu betik,
# ardindan "python carpisma_kos.py birlestir".
# Calistir: FC_SCRIPT=<bu dosya> CARPISMA_BOLUM=<bolum> freecadcmd run_fc.py
import os, sys, json, time, math, gc, datetime
from collections import OrderedDict
import FreeCAD as App
import Part
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def bellek_mb():
    """(tepe calisma kumesi, simdiki calisma kumesi, tepe sayfa dosyasi) MB; Windows disinda None."""
    try:
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [(n, ctypes.c_size_t) for n in (
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage",
                "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
        k32 = ctypes.windll.kernel32
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        ps = ctypes.windll.psapi
        ps.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        c = PMC()
        c.cb = ctypes.sizeof(c)
        ps.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
        return (round(c.PeakWorkingSetSize / 2 ** 20), round(c.WorkingSetSize / 2 ** 20), round(c.PeakPagefileUsage / 2 ** 20))
    except Exception:
        return (None, None, None)


for _p in (HERE, os.path.join(HERE, "iskelet"), os.path.join(HERE, "omuz"), os.path.join(HERE, "kabuk"),
           os.path.join(HERE, "dirsek"), os.path.join(HERE, "kafa"), os.path.join(HERE, "taban")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import arayuz as A
from ortak_lib import V, box
import carpisma_kos as CK

t0 = time.time()
TOL = 0.5   # mm3 (omuz ve iskelet kontrolleriyle ayni)


# ====================================================================== modul yukleyicileri
# Her yukleyici: dict(parcalar=[dict(ad, grup, shape, kutle, merkez)], hareket=None | dict(pozlar, yer(poz, grup) ->
# App.Placement (yerel), sabit_grup, eklem_araligi(poz) -> bool), haric=[parca adi oneki], haric_neden)
def yukle_iskelet():
    import iskelet_parcalar as I
    return dict(parcalar=[dict(ad=p["ad"], grup="sabit", shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"]) for p in I.P],
                hareket=None, haric=[], haric_neden="")


def yukle_omuz():
    import omuz_parcalar as O
    grup = {"Govde": "sabit", "Gobek": "Gobek", "Kol": "Kol"}

    def yer(poz, g):
        phi, th = poz
        if g == "Gobek":
            return O.Pp(phi)
        if g == "Kol":
            return O.Pp(phi).multiply(O.Pr(th))
        return App.Placement()

    return dict(parcalar=[dict(ad=p["ad"], grup=grup[p["grup"]], shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"])
                          for p in O.P],
                hareket=dict(pozlar=[(phi, th) for phi in O.PHIS for th in O.THS], yer=yer,
                             eklem_araligi=lambda poz: -45 <= poz[0] <= 135 and 0 <= poz[1] <= 120,
                             aciklama="omuz_montaj taramasi: one-arka %d...%d, yana %d...%d (5-10 derece adim)" %
                             (min(O.PHIS), max(O.PHIS), min(O.THS), max(O.THS))),
                haric=["Omuz traversi", "Govde kabugu yan yuzu (referans)"],
                haric_neden="travers iskeletin parcasi (arayuz uyumu ayrica kontrol edilir); kabuk duvari kabuk modulunun yer tutucusu")


def yukle_kabuk():
    import kabuk_parcalar as K
    return dict(parcalar=[dict(ad=p["ad"], grup="sabit", shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"]) for p in K.P],
                hareket=None, haric=[], haric_neden="")


def yukle_dirsek(taraf):
    """Dirsek modulu omuzun Kol grubuna bagli: kendi 'hareket'i yok, kol zinciri taramasinda (bolum 4) omuzla birlikte
    surulur (zincir). Generic taramada hedef olarak kullanilmaz (ev pozunda durmaz, kolla birlikte hareket eder)."""
    def yukle():
        import dirsek_parcalar as DP
        return dict(parcalar=[dict(ad=p["ad"], grup=p["grup"], shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"]) for p in DP.P],
                    hareket=None, zincir=dict(omuz="omuz_" + taraf, taraf=taraf), haric=[], haric_neden="")
    return yukle


def yukle_kafa():
    """Kafa: Govde traverse sabit, Pan = Ppan(psi), Kafa = Ppan(psi) Ptilt(th) (kafa_parcalar.grup_yer). Generic taramaya
    (bolum 3) ve kol zinciri hedeflerine girmez; kendi taramasi bolum 4b'de (pan x tilt; sabit moduller ve iki kolun pozlari)."""
    import kafa_parcalar as KP
    return dict(parcalar=[dict(ad=p["ad"], grup=p["grup"], shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"]) for p in KP.P],
                hareket=None, kafa=True, haric=["Kablo demeti (gosterim)"],
                haric_neden="kablo demeti gosterimi (Referans grubu, 0 g); carpisma taramasina girmez")


def yukle_taban():
    """Taban: tum parcalar sabit (yerel = global). Kablo yolu semalari (Referans, 0 g) taramaya girmez. Ana anahtar dugmesi
    gosterimi (Referans; etek plakasinda kabuk deligi gerekir) statik kontrollerde haric (deliksiz kabukla cakisir), ama
    kol x taban taramasinda (bolum 4c) hedef olarak kullanilir (gercekte etek ustune ~22 mm tasar)."""
    import taban_parcalar as TP
    return dict(parcalar=[dict(ad=p["ad"], grup="sabit", shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"], tgrup=p["grup"],
                               tur=p["tur"]) for p in TP.P],
                hareket=None, haric=["Kablo yolu", "Ana anahtar dugmesi"],
                haric_neden="kablo yolu semalari ve ana anahtar dugmesi gosterimi (Referans grubu, 0 g); dugme kol x taban "
                            "taramasinda (bolum 4c) hedef")


MODUL_YUKLE = {"iskelet": yukle_iskelet, "omuz_sag": yukle_omuz, "omuz_sol": yukle_omuz, "kabuk": yukle_kabuk,
               "dirsek_sag": yukle_dirsek("sag"), "dirsek_sol": yukle_dirsek("sol"), "kafa": yukle_kafa, "taban": yukle_taban}
KONTROL = ["iskelet", "omuz_sag", "omuz_sol", "kabuk", "dirsek_sag", "dirsek_sol", "kafa", "taban"]

# ---------------------------------------------------------------------- bolum secimi (bkz. bas not)
BOLUMLER = CK.BOLUMLER
BOLUM = CK.bolum_coz(os.environ.get("CARPISMA_BOLUM") or "hepsi")
GEREK = set()
for _b in BOLUM:
    GEREK |= set(CK.GEREK_MODUL[_b])
# Gelistirme testi: CARPISMA_KISA=1 kafa x kol taramasini yasak bolge cevresine daraltir (kol one >= 120, yana <= 15, dirsek >= 90;
# pan -60...60); sonuc carpisma-bolum/<bolum>-kisa.json'a yazilir, birlestirmeye girmez.
KISA = bool(os.environ.get("CARPISMA_KISA"))
print("bolum:", ",".join(BOLUM), "(KISA test)" if KISA else "", "| moduller:", ",".join(a for a in KONTROL if a in GEREK), flush=True)


def ozel(d):
    """Kendi taramasi olan modul: dirsek (kol zinciri, bolum 4) ve kafa (bolum 4b). Generic hedef listelerine girmez."""
    return bool(d.get("zincir") or d.get("kafa"))


# ====================================================================== global yerlesim
AYNA = App.Matrix()
AYNA.A11 = -1.0


def global_matris(ad):
    (tx, ty, tz), ayna = A.modul_konum(ad)
    T = App.Matrix()
    T.move(V(tx, ty, tz))
    return T, (AYNA if ayna else App.Matrix())


MODUL = {}
for ad in KONTROL:
    if ad not in GEREK:
        continue
    d = MODUL_YUKLE[ad]()
    T, R = global_matris(ad)
    for p in d["parcalar"]:
        s = p["shape"].mirror(V(0, 0, 0), V(1, 0, 0)) if R.A11 < 0 else p["shape"].copy()
        s.transformShape(T, True)
        p["g"] = s
        p["gbb"] = s.optimalBoundingBox()      # B-spline yuzlu buyuk parcalarda BoundBox gevsek; suzgec icin siki kutu
        c = p["merkez"]
        p["gmerkez"] = V(-c.x if R.A11 < 0 else c.x, c.y, c.z) + V(T.A14, T.A24, T.A34)
        p["haric"] = any(p["ad"].startswith(h) for h in d["haric"])
    d["T"], d["R"] = T, R
    MODUL[ad] = d
    print("modul", ad, "parca", len(d["parcalar"]), "haric", sum(p["haric"] for p in d["parcalar"]), "%.1fs" % (time.time() - t0))

# henuz cizilmemis modullerin ayrilmis bolgeleri -> sabit sozde modul
bolge_parca = []
for z in A.bolgeler(haric=KONTROL):
    k = box(*z["kutu"])
    for c in z["bosluk"]:
        k = k.cut(box(*c))
    bolge_parca.append(dict(ad="[%s] %s" % (z["sahip"], z["ad"]), grup="sabit", g=k, gbb=k.BoundBox, haric=False, kutle=0))
MODUL["ayrilmis_bolgeler"] = dict(parcalar=bolge_parca, hareket=None, haric=[], haric_neden="")


def poz_matrisi(ad, poz, g):
    """Global koordinatta bir grubun poz donusumu: T R P R T^-1 (R ayna ise de katı donusum kalir)."""
    d = MODUL[ad]
    Pm = d["hareket"]["yer"](poz, g).toMatrix()
    T, R = d["T"], d["R"]
    return T.multiply(R).multiply(Pm).multiply(R).multiply(T.inverse())


def kesisim(a, b, abb, bbb):
    if not abb.intersect(bbb):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def aktif(d):
    return [p for p in d["parcalar"] if not p["haric"]]


adlar = list(MODUL)


# ====================================================================== 1-2) statik bolum: arayuz uyumu, ev pozu, kutle
def b_statik():
    # ====================================================================== 1) arayuz uyumu: omuzun traversi = iskeletin traversi
    uyum = []
    isk_tr = next(p for p in MODUL["iskelet"]["parcalar"] if p["ad"] == "Omuz traversi")
    for ad in ("omuz_sag", "omuz_sol"):
        o_tr = next(p for p in MODUL[ad]["parcalar"] if p["ad"].startswith("Omuz traversi"))
        ortak = o_tr["g"].common(isk_tr["g"]).Volume
        bbd = max(abs(getattr(o_tr["gbb"], k) - getattr(isk_tr["gbb"], k)) for k in ("XMin", "XMax", "YMin", "YMax", "ZMin", "ZMax"))
        uyum.append(dict(modul=ad, hacim_omuz=round(o_tr["g"].Volume, 3), hacim_iskelet=round(isk_tr["g"].Volume, 3),
                         ortak=round(ortak, 3), sinir_kutusu_fark=round(bbd, 6),
                         ayni=abs(ortak - isk_tr["g"].Volume) < 1e-3 and bbd < 1e-6))
    print("arayuz uyumu:", [(u["modul"], u["ayni"]) for u in uyum])

    # ====================================================================== 2) ev pozunda modul ciftleri
    statik = []
    n_statik = 0
    for i in range(len(adlar)):
        for j in range(i + 1, len(adlar)):
            for a in aktif(MODUL[adlar[i]]):
                for b in aktif(MODUL[adlar[j]]):
                    if a["gbb"].intersect(b["gbb"]):
                        n_statik += 1
                    v = kesisim(a["g"], b["g"], a["gbb"], b["gbb"])
                    if v > TOL or v < 0:
                        statik.append(dict(a=adlar[i], pa=a["ad"], b=adlar[j], pb=b["ad"], hacim=round(v, 2)))
    print("ev pozu: %d cakisma (%d sinir kutusu kesisen cift)" % (len(statik), n_statik), "%.1fs" % (time.time() - t0))
    # toplam kutle ve agirlik merkezi (ev pozu)
    m_top, cg = 0.0, V(0, 0, 0)
    km = {}
    for ad in KONTROL:
        mm = 0.0
        for p in MODUL[ad]["parcalar"]:
            if p["haric"] or p["kutle"] <= 0:
                continue
            m_top += p["kutle"]
            mm += p["kutle"]
            cg = cg + p["gmerkez"] * p["kutle"]
        km[ad] = round(mm, 1)
    cg = cg * (1.0 / m_top)
    print("kutle %.1f g, AM (%.2f, %.2f, %.2f)" % (m_top, cg.x, cg.y, cg.z), flush=True)
    return dict(
        moduller=[dict(ad=ad, konum=list(A.MODULLER[ad]["konum"]), ayna=A.MODULLER[ad]["ayna"], parca=len(MODUL[ad]["parcalar"]),
                       haric=[p["ad"] for p in MODUL[ad]["parcalar"] if p["haric"]], haric_neden=MODUL[ad]["haric_neden"],
                       hareketli=bool(MODUL[ad]["hareket"]) or ozel(MODUL[ad]),
                       bagli=(MODUL[ad].get("zincir") or {}).get("omuz")) for ad in KONTROL],
        ayrilmis_bolge=dict(sayi=len(bolge_parca), sahipler=sorted(set(z["sahip"] for z in A.bolgeler(haric=KONTROL)))),
        arayuz_uyumu=uyum, ev_pozu_cakisma=statik, ev_pozu_kesisen_cift=n_statik,
        kutle_g=km, kutle_toplam_g=round(m_top, 1), agirlik_merkezi=[round(cg.x, 2), round(cg.y, 2), round(cg.z, 2)])


# ====================================================================== 3) hareket taramasi (omuz bolumu)
def b_omuz():
    zarf = {}
    for ad in adlar:
        d = MODUL[ad]
        if not d["hareket"]:
            continue
        gruplar = sorted(set(p["grup"] for p in aktif(d) if p["grup"] != "sabit"))
        bb = None
        for poz in d["hareket"]["pozlar"]:
            for g in gruplar:
                M = poz_matrisi(ad, poz, g)
                for p in aktif(d):
                    if p["grup"] != g:
                        continue
                    s = p["g"].copy()
                    s.transformShape(M)
                    if bb is None:
                        bb = App.BoundBox(s.BoundBox)
                    else:
                        bb.add(s.BoundBox)
        zarf[ad] = bb
        print("zarf", ad, "x %.0f...%.0f y %.0f...%.0f z %.0f...%.0f" % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))

    # uzaklik icin yuz listesi: sabit hedef parcanin hareket zarflarina (30 mm payli) yakin yuzleri ve sinir kutulari. Her
    # pozda yalniz hareketli parcanin 30 mm kutusuna giren yuzlere distToShape: cakismayan iki sekil arasindaki en kucuk uzaklik
    # sinirlarda olculdugu icin sonuc ayni, buyuk (B-spline yuzlu) kabuk parcalarinda tarama cok hizlanir.
    _zarf30 = []
    for _b in zarf.values():
        _z = App.BoundBox(_b)
        _z.enlarge(30)
        _zarf30.append(_z)
    for ad in adlar:
        if MODUL[ad]["hareket"] or ozel(MODUL[ad]):
            continue
        for q in aktif(MODUL[ad]):
            q["yuz"] = [] if not any(z.intersect(q["gbb"]) for z in _zarf30) else             [(f, f.BoundBox) for f in q["g"].Faces if any(z.intersect(f.BoundBox) for z in _zarf30)]
    # kabuk (buyuk sabit kabuk) icin en kucuk bosluk yalniz eklem araligindaki pozlarda olculur; cakisma tum pozlarda
    YALNIZ_ARALIKTA = ("kabuk",)

    tarama = {}
    for ad in adlar:
        d = MODUL[ad]
        if not d["hareket"]:
            continue
        hedef = []          # diger modullerin ev pozu parcalari (hareketli diger modul: zarflar kesisiyorsa ortak tarama)
        ortak_gerekli = []
        for bd in adlar:
            if bd == ad:
                continue
            if MODUL[bd]["hareket"]:
                if zarf[ad].intersect(zarf[bd]):
                    ortak_gerekli.append(bd)
                continue     # zarflar ayriksa hicbir pozda carpisamazlar
            if ozel(MODUL[bd]):
                continue     # dirsek: kolla birlikte hareket eder, kol zinciri taramasinda (bolum 4); kafa: bolum 4b
            hedef += [(bd, p) for p in aktif(MODUL[bd])]
        hareketli = [p for p in aktif(d) if p["grup"] != "sabit"]
        cak = {}
        n_test = 0
        yakin = (1e9, None)     # en kucuk bosluk: 30 mm icindeki adaylar icin distToShape
        ea = d["hareket"]["eklem_araligi"]
        mod_yakin = {}          # hedef modul -> eklem araligindaki en kucuk bosluk
        mod_cak = {}            # hedef modul -> cakisan pozlar
        for poz in d["hareket"]["pozlar"]:
            tasinmis = []
            for p in hareketli:
                s = p["g"].copy()
                s.transformShape(poz_matrisi(ad, poz, p["grup"]))
                tasinmis.append((p, s, s.BoundBox))
            hits = []
            for p, s, sbb in tasinmis:
                bb30 = App.BoundBox(sbb)
                bb30.enlarge(30)
                for bd, q in hedef:
                    if not bb30.intersect(q["gbb"]):
                        continue
                    v = 0.0
                    if sbb.intersect(q["gbb"]):
                        n_test += 1
                        v = kesisim(s, q["g"], sbb, q["gbb"])
                        if v > TOL or v < 0:
                            hits.append((p["ad"], bd, q["ad"], round(v, 1)))
                            mod_cak.setdefault(bd, set()).add(poz)
                    if bd in YALNIZ_ARALIKTA and not ea(poz) and not (v > TOL or v < 0):
                        continue
                    yz = [f for f, fb in q["yuz"] if bb30.intersect(fb)]
                    if yz or v > TOL or v < 0:
                        dd = 0.0 if (v > TOL or v < 0) else s.distToShape(Part.Compound(yz) if len(yz) > 1 else yz[0])[0]
                        if dd < yakin[0]:
                            yakin = (dd, (poz, p["ad"], bd, q["ad"]))
                        if ea(poz) and dd < mod_yakin.get(bd, (1e9,))[0]:
                            mod_yakin[bd] = (dd, (poz, p["ad"], q["ad"]))
            # hareketli diger moduller (zarflari kesisiyorsa): onlarin tum pozlariyla
            for bd in ortak_gerekli:
                for poz2 in MODUL[bd]["hareket"]["pozlar"]:
                    for q in [x for x in aktif(MODUL[bd]) if x["grup"] != "sabit"]:
                        s2 = q["g"].copy()
                        s2.transformShape(poz_matrisi(bd, poz2, q["grup"]))
                        for p, s, sbb in tasinmis:
                            v = kesisim(s, s2, sbb, s2.BoundBox)
                            if v > TOL or v < 0:
                                hits.append((p["ad"], bd + "@%s" % (poz2,), q["ad"], round(v, 1)))
            if hits:
                cak[poz] = hits
            n_poz_bitti = d["hareket"]["pozlar"].index(poz) + 1
            if n_poz_bitti % 125 == 0:
                print("  %s %d/%d poz, %.0fs" % (ad, n_poz_bitti, len(d["hareket"]["pozlar"]), time.time() - t0), flush=True)
        tarama[ad] = dict(poz_sayisi=len(d["hareket"]["pozlar"]), cakisan_poz=len(cak),
                          eklem_araliginda_cakisan=sum(1 for k in cak if ea(k)), kesisim_testi=n_test,
                          ortak_tarama=ortak_gerekli, aciklama=d["hareket"]["aciklama"],
                          en_kucuk_bosluk_mm=round(yakin[0], 2), en_yakin=yakin[1],
                          cakismalar={"%s" % (k,): v for k, v in list(cak.items())[:50]},
                          modul_bosluk_eklem_araliginda={k: [round(v[0], 2), v[1]] for k, v in mod_yakin.items()},
                          modul_cakisan_poz={k: sorted([list(x) for x in v]) for k, v in mod_cak.items()},
                          bosluk_notu="kabuk icin en kucuk bosluk yalniz eklem araligindaki pozlarda olculdu (cakisma tum pozlarda)")
        print("tarama", ad, "%d poz, %d cakisan (eklem araliginda %d), %d kesisim testi, en kucuk bosluk %.1f mm %s" %
              (len(d["hareket"]["pozlar"]), len(cak), tarama[ad]["eklem_araliginda_cakisan"], n_test, yakin[0], yakin[1]),
              "%.1fs" % (time.time() - t0))
    return dict(zarf={k: [round(v.XMin, 1), round(v.XMax, 1), round(v.YMin, 1), round(v.YMax, 1), round(v.ZMin, 1), round(v.ZMax, 1)]
                      for k, v in zarf.items()}, tarama=tarama)


# ====================================================================== 4) kol zinciri taramasi (omuz S1 x S2 x dirsek x bilek)
# Dirsek modulu omuzun Kol grubuna bagli: UstKol = Pp(phi) Pr(th), OnKol = UstKol Pe(dirsek), El = OnKol Pb(bilek)
# (dirsek_parcalar.grup_yer; Pp/Pr omuz_parcalar ile ayni). Hareketli: dirsek parcalari (omuz parcalari 3. bolumde tarandi).
# Hedef: iskelet, kabuk, ayrilmis bolgeler, iki omuzun govdesi (sabit) ve kendi omuzunun gobegi (Pp(phi)). Omuzun Kol grubu
# dirsek ust grubuna sabit; on kol/el ile Kol grubu arasindaki bagil hareket omuz pozundan bagimsiz ve dirsek_montaj.py'de
# tarandi. Yontem: (a) sinir kutusu on elemesi: hareketli parcanin ev pozu kutusunun 8 kosesi poz matrisiyle tasinir
# (tutucu kutu), hedef kutularina bosluk numpy ile hesaplanir; LIM'den uzak ciftler hic olculmez. (b) tutucu boslugu YAKIN
# altindaki her aday tam olculur (distToShape; buyuk kabuk parcalarinda yalniz yakin yuzlere; temas/gomulme suphesinde
# common hacmi). (c) hedef basina en kucuk bosluk: adaylar tutucu bosluga gore siralanir, dal-sinirla (kutu boslugu bulunan
# en kucuk boslugu gecince durur) tam olculur. (d) kaba izgarada cakisan ya da INCE_ESIK altinda bosluk birakan alt
# pozlarin cevresi ince adimla (omuz 5 derece, dirsek 5, bilek 15) yeniden taranir. Alt poz: UstKol (phi, th),
# OnKol (phi, th, dirsek), El (phi, th, dirsek, bilek); tam poz bulgusu ucunun birlesimi.
import itertools
import dirsek_parcalar as DP
import omuz_parcalar as OP

KOL_ARALIK = ((-45.0, 135.0), (0.0, 120.0), tuple(DP.D["aralik"]), tuple(DP.D["bilek_aralik"]))   # phi, th, dirsek, bilek
KABA = (list(range(-45, 136, 15)), list(range(0, 121, 15)), [0, 30, 60, 90, 105], [-90, 0, 90])
DISI_AL, DISI_BE = [0, 60, 105], [-90, 0, 90]       # aralik disi halka: omuz one-arka -60 / 150, yana -10
YAKIN = 5.0          # mm: tutucu kutu boslugu bunun altindaki her aday tam olculur
INCE_ESIK = 5.0      # mm: bunun altinda bosluk (ya da cakisma) olan alt pozun cevresi ince taranir
LIM = 150.0          # mm: kutu on elemesi (bunun otesindeki ciftlerin boslugu "> LIM" sayilir)
GOMULU = 3.0         # mm: bu mesafenin altinda ve hedef kutusu icindeyse gomulme kontrolu (common)
GRUP_UZ = {"UstKol": 2, "OnKol": 3, "El": 4}
ESIK_YUZ = 40        # bundan cok yuzlu hedefte yalniz yakin yuzlerle mesafe


def kol_araliginda(sp):
    return all(KOL_ARALIK[k][0] - 1e-9 <= v <= KOL_ARALIK[k][1] + 1e-9 for k, v in enumerate(sp))


def np_m(M):
    return np.array([[M.A11, M.A12, M.A13, M.A14], [M.A21, M.A22, M.A23, M.A24], [M.A31, M.A32, M.A33, M.A34]])


def bb6(b):
    return np.array([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])


def kose8(b):
    return np.array([[x, y, z, 1.0] for x in (b.XMin, b.XMax) for y in (b.YMin, b.YMax) for z in (b.ZMin, b.ZMax)])


def kutu_tasi(K8, Mn):
    q = K8 @ Mn.T
    return np.concatenate([q.min(0), q.max(0)])


def bosluk_np(b, B):
    d = np.maximum(0.0, np.maximum(B[:, :3] - b[3:], b[:3] - B[:, 3:]))
    return np.sqrt((d * d).sum(1))


def kol_matrisi(ad, g, sp):
    """Global poz matrisi: T R P R T^-1. ad = dirsek_* ya da omuz_*; sp = (phi, th, dirsek, bilek) ya da onun basi."""
    d = MODUL[ad]
    phi, th, al, be = (list(sp) + [0.0, 0.0, 0.0, 0.0])[:4]
    if g in GRUP_UZ:
        Pm = DP.grup_yer(g, phi, th, al, be).toMatrix()
    elif g == "Gobek":
        Pm = OP.Pp(phi).toMatrix()
    elif g == "Kol":
        Pm = OP.Pp(phi).multiply(OP.Pr(th)).toMatrix()
    else:
        Pm = App.Matrix()
    T, R = d["T"], d["R"]
    return T.multiply(R).multiply(Pm).multiply(R).multiply(T.inverse())


def yuz_hazirla(q):
    if "fbb" not in q:
        fs = q["g"].Faces
        q["faces"] = fs
        q["fbb"] = np.array([bb6(f.BoundBox) for f in fs]) if len(fs) > ESIK_YUZ else None


def tam_olc(s, q, B):
    """Hareketli sekil s ile hedef q arasi: (mesafe, cakisma hacmi) ya da B'den uzaksa None."""
    sb = bb6(s.BoundBox)
    if bosluk_np(sb, q["bb"][None, :])[0] >= B:
        return None
    yuz_hazirla(q)
    if q["fbb"] is None:
        hedef_s = q["g"]
    else:
        sec = np.nonzero(bosluk_np(sb, q["fbb"]) < B)[0]
        if len(sec) == 0:
            return None
        hedef_s = q["faces"][sec[0]] if len(sec) == 1 else Part.Compound([q["faces"][i] for i in sec])
    d = s.distToShape(hedef_s)[0]
    v = 0.0
    ic = all(sb[k] >= q["bb"][k] for k in range(3)) and all(sb[k + 3] <= q["bb"][k + 3] for k in range(3))
    if d < 1e-6 or (d < GOMULU and ic and q["g"].Solids):
        v = kesisim(s, q["g"], s.BoundBox, q["gbbF"])
        if v > TOL or v < 0:
            d = 0.0
    return d, v


def kol_tara(taraf):
    om, dr = "omuz_" + taraf, "dirsek_" + taraf
    ts = time.time()
    # --- hedefler: sabit (iskelet, kabuk, bolgeler, iki omuzun govdesi) + kendi omuzunun gobegi (phi ile)
    sabit = []
    for ad in adlar:
        dd = MODUL[ad]
        if ozel(dd):
            continue
        if dd["hareket"]:
            if not ad.startswith("omuz_"):
                continue
            sabit += [dict(mod="%s govde" % ad, ad=q["ad"], g=q["g"], gbbF=q["gbb"], bb=bb6(q["gbb"])) for q in aktif(dd) if q["grup"] == "sabit"]
        else:
            sabit += [dict(mod=ad, ad=q["ad"], g=q["g"], gbbF=q["gbb"], bb=bb6(q["gbb"])) for q in aktif(dd)]
    SB = np.array([q["bb"] for q in sabit])
    gobek_p = [q for q in aktif(MODUL[om]) if q["grup"] == "Gobek"]
    gobek_cache = {}

    def gobek(phi):
        if phi not in gobek_cache:
            M = kol_matrisi(om, "Gobek", (phi,))
            L = []
            for q in gobek_p:
                s = q["g"].copy()
                s.transformShape(M)
                L.append(dict(mod="%s gobek" % om, ad=q["ad"], g=s, gbbF=s.BoundBox, bb=bb6(s.BoundBox)))
            gobek_cache[phi] = (L, np.array([x["bb"] for x in L]))
        return gobek_cache[phi]

    har = [p for p in aktif(MODUL[dr])]
    for p in har:
        p["K8"] = kose8(p["gbb"])
    mcache = {}

    def M_al(g, sp):
        k = (g, sp)
        if k not in mcache:
            mcache[k] = kol_matrisi(dr, g, sp)
        return mcache[k]

    def hedef(hk, sp):
        return sabit[hk[1]] if hk[0] == "s" else gobek(sp[0])[0][hk[1]]

    def tasi(pi, g, sp):
        s = har[pi]["g"].copy()
        s.transformShape(M_al(g, sp))
        return s

    aday = []           # (tutucu bosluk, g, sp, parca indeksi, hedef anahtari)
    islenen = set()

    def aday_topla(altpozlar):
        n0 = len(aday)
        for g, sp in altpozlar:
            if (g, sp) in islenen:
                continue
            islenen.add((g, sp))
            Mn = np_m(M_al(g, sp))
            GL, GB = gobek(sp[0])
            for pi, p in enumerate(har):
                if p["grup"] != g:
                    continue
                cb = kutu_tasi(p["K8"], Mn)
                gs = bosluk_np(cb, SB)
                for j in np.nonzero(gs < LIM)[0]:
                    aday.append((float(gs[j]), g, sp, pi, ("s", int(j))))
                gg = bosluk_np(cb, GB)
                for j in np.nonzero(gg < LIM)[0]:
                    aday.append((float(gg[j]), g, sp, pi, ("g", int(j))))
        return n0

    olcum = {}          # (g, sp, pi, hk) -> (d, v)

    def olc(c, B):
        k = (c[1], c[2], c[3], c[4])
        if k in olcum:
            return olcum[k]
        r = tam_olc(tasi(c[3], c[1], c[2]), hedef(c[4], c[2]), B)
        if r is not None:
            olcum[k] = r
        return r

    def mod_ad(hk):
        return sabit[hk[1]]["mod"] if hk[0] == "s" else "%s gobek" % om

    en_iyi = {}

    def degerlendir(n0):
        yeni = sorted(aday[n0:], key=lambda c: c[0])
        n_tam = 0
        for c in yeni:                          # (b) YAKIN altindakiler hepsi
            if c[0] >= YAKIN:
                break
            r = olc(c, YAKIN)
            n_tam += 1
            if r is not None and r[0] < en_iyi.get(mod_ad(c[4]), (1e9,))[0]:
                en_iyi[mod_ad(c[4])] = (r[0], c)
        for c in yeni:                          # (c) dal-sinir: hedef modul basina en kucuk bosluk
            m = mod_ad(c[4])
            B = en_iyi.get(m, (LIM,))[0]
            if c[0] >= B:
                continue
            r = olc(c, B)
            n_tam += 1
            if n_tam % 500 == 0:
                print("    %s: %d tam olcum, %.0fs" % (taraf, n_tam, time.time() - ts), flush=True)
            if r is not None and r[0] < B:
                en_iyi[m] = (r[0], c)
        return n_tam

    # --- kaba izgara + aralik disi halka
    kaba = [(phi, th, al, be) for phi in KABA[0] for th in KABA[1] for al in KABA[2] for be in KABA[3]]
    disi = [(phi, th, al, be) for phi in (-60, 150) for th in KABA[1] for al in DISI_AL for be in DISI_BE] + \
           [(phi, -10, al, be) for phi in KABA[0] for al in DISI_AL for be in DISI_BE]

    def alt(poz):
        return [(g, tuple(float(x) for x in poz[:n])) for g, n in GRUP_UZ.items()]

    altlar = sorted(set(a for poz in kaba + disi for a in alt(poz)))
    n0 = aday_topla(altlar)
    n_tam = degerlendir(n0)
    print("kol %s: kaba %d + disi %d tam poz, %d alt poz, %d aday, %d tam olcum %.0fs" % (
        taraf, len(kaba), len(disi), len(altlar), len(aday), n_tam, time.time() - ts), flush=True)

    # --- (d) ince adim: cakisan ya da INCE_ESIK altinda kalan alt pozlarin cevresi
    def isaretli():
        return sorted(set((k[0], k[1]) for k, r in olcum.items() if r[0] < INCE_ESIK or r[1] > TOL or r[1] < 0))

    # yalniz eklem araligindaki isaretli alt pozlar incelenir (aralik disi halka yalniz ornek); ince komsuluk aralik icinde kalir
    isa = [x for x in isaretli() if kol_araliginda(x[1])]
    ADIM_I = ((-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-15, 0, 15))
    ince = set()
    for g, sp in isa:
        rng = [[sp[k] + dd for dd in ADIM_I[k]] for k in range(len(sp))]
        for q in itertools.product(*rng):
            q = tuple(float(x) for x in q)
            if kol_araliginda(q):
                ince.add((g, q))
    print("kol %s: isaretli alt poz %d (%s), ince aday alt poz %d" % (
        taraf, len(isa), {gg: sum(1 for x in isa if x[0] == gg) for gg in GRUP_UZ}, len(ince)), flush=True)
    ince = sorted(ince - islenen)
    n0 = aday_topla(ince)
    n_tam2 = degerlendir(n0)
    print("kol %s: ince %d alt poz, %d aday, %d tam olcum %.0fs" % (taraf, len(ince), len(aday) - n0, n_tam2, time.time() - ts), flush=True)

    # --- ozet
    def bulgu(k, r):
        g, sp, pi, hk = k
        q = hedef(hk, sp)
        return dict(grup=g, poz=list(sp), parca=har[pi]["ad"], hedef_modul=q["mod"], hedef=q["ad"], bosluk_mm=round(r[0], 2),
                    hacim_mm3=round(r[1], 1), aralikta=kol_araliginda(sp))

    cak = [bulgu(k, r) for k, r in olcum.items() if r[1] > TOL or r[1] < 0]
    yakin_l = sorted([bulgu(k, r) for k, r in olcum.items() if r[0] < YAKIN and not (r[1] > TOL or r[1] < 0)],
                     key=lambda b: b["bosluk_mm"])

    def tam_poz_cak(pozlar):
        cak_alt = set((b["grup"], tuple(b["poz"])) for b in cak)
        return [poz for poz in pozlar if any(a in cak_alt for a in alt(poz))]

    kaba_cak = tam_poz_cak(kaba)
    disi_cak = tam_poz_cak(disi)
    # hedef modul basina en kucuk bosluk (aralik ici / disi ayri)
    mod_min = {}
    cift_min = {}
    for k, r in olcum.items():
        b = bulgu(k, r)
        anah = (b["hedef_modul"], b["aralikta"])
        if r[0] < mod_min.get(anah, (1e9,))[0]:
            mod_min[anah] = (r[0], b)
        if b["aralikta"]:
            anah = (b["hedef_modul"], b["parca"], b["hedef"])
            if r[0] < cift_min.get(anah, (1e9,))[0]:
                cift_min[anah] = (r[0], b)
    moduller = sorted(set(m for m, _ in mod_min))
    sonuc = dict(
        taraf=taraf, omuz=om, dirsek=dr,
        aralik=dict(one_arka=KOL_ARALIK[0], yana=KOL_ARALIK[1], dirsek=KOL_ARALIK[2], bilek=KOL_ARALIK[3]),
        kaba_izgara=dict(one_arka=KABA[0], yana=KABA[1], dirsek=KABA[2], bilek=KABA[3], tam_poz=len(kaba)),
        aralik_disi_halka=dict(aciklama="omuz one-arka -60 ve 150 (yana 0...120) + yana -10 (one-arka -45...135); dirsek %s; bilek %s"
                               % (DISI_AL, DISI_BE), tam_poz=len(disi)),
        alt_poz=dict(kaba=len(altlar), ince=len(ince)), aday=len(aday), tam_olcum=len(olcum),
        cakisan_tam_poz_aralikta=len(kaba_cak), cakisan_tam_poz_aralik_disi=len(disi_cak),
        cakisan_alt_poz_aralikta=len(set((b["grup"], tuple(b["poz"])) for b in cak if b["aralikta"])),
        cakisan_alt_poz_aralik_disi=len(set((b["grup"], tuple(b["poz"])) for b in cak if not b["aralikta"])),
        cakismalar_aralikta=sorted([b for b in cak if b["aralikta"]], key=lambda b: (b["grup"], b["poz"]))[:200],
        cakismalar_aralik_disi=sorted([b for b in cak if not b["aralikta"]], key=lambda b: (b["grup"], b["poz"]))[:200],
        en_kucuk_bosluk_aralikta={m: mod_min[(m, True)][1] for m in moduller if (m, True) in mod_min},
        en_kucuk_bosluk_aralik_disi={m: mod_min[(m, False)][1] for m in moduller if (m, False) in mod_min},
        en_kucuk_ciftler_aralikta={m: [v[1] for v in sorted([v for kk, v in cift_min.items() if kk[0] == m], key=lambda v: v[0])[:6]]
                                   for m in moduller},
        yakin_aralikta=[b for b in yakin_l if b["aralikta"]][:60], yakin_aralikta_sayi=sum(1 for b in yakin_l if b["aralikta"]),
        bosluk_notu="olculmeyen ciftlerin boslugu >= %d mm (sinir kutusu); YAKIN = %.0f mm altindaki her aday tam olculdu" % (LIM, YAKIN),
        sure_s=round(time.time() - ts, 1))
    for m in moduller:
        if (m, True) in mod_min:
            b = mod_min[(m, True)][1]
            print("  %s -> %-22s en kucuk bosluk %.2f mm %s %s / %s" % (taraf, m, b["bosluk_mm"], b["poz"], b["parca"], b["hedef"]))
    print("kol %s: aralikta cakisan tam poz %d / %d, aralik disi %d / %d, %.0fs" % (
        taraf, len(kaba_cak), len(kaba), len(disi_cak), len(disi), time.time() - ts), flush=True)
    return sonuc


# ---------------------------------------------------------------------- kol <-> kol (iki kol ayni anda)
def kol_parcalari(taraf):
    om, dr = "omuz_" + taraf, "dirsek_" + taraf
    L = [(om, p) for p in aktif(MODUL[om]) if p["grup"] in ("Gobek", "Kol")] + [(dr, p) for p in aktif(MODUL[dr])]
    for ad, p in L:
        if "K8" not in p:
            p["K8"] = kose8(p["gbb"])
    return L


def kol_kol():
    ts = time.time()
    KS, KL = kol_parcalari("sag"), kol_parcalari("sol")
    ciftler = []
    for phi in (-45, 0, 45, 90, 135):                     # simetrik: iki kol ayni poz (aynali hareket)
        for th in (0, 60, 120):
            for al in (0, 60, 105):
                for be in (-90, 90):
                    ciftler.append(("simetrik", (phi, th, al, be), (phi, th, al, be)))
    for (a, b) in (((135, 0), (-45, 0)), ((-45, 0), (135, 0)), ((90, 0), (0, 0)), ((135, 120), (-45, 0)), ((0, 120), (135, 0)),
                   ((90, 30), (-45, 60)), ((45, 0), (-45, 0)), ((120, 0), (-30, 0))):   # zit pozlar
        for al in (0, 105):
            for be in (-90, 90):
                ciftler.append(("zit", (a[0], a[1], al, be), (b[0], b[1], 105 - al, -be)))
    for th in (0, 15, 30):                               # iki kol birlikte one uzanir (omuz one 90)
        for al in (0, 30, 60, 90, 105):
            for be in (-90, 0, 90):
                ciftler.append(("birlikte one", (90, th, al, be), (90, th, al, -be)))
                ciftler.append(("birlikte one (bilek ayni)", (90, th, al, be), (90, th, al, be)))
    for phi in (60, 75, 105, 120, 135):
        for al in (0, 60, 105):
            ciftler.append(("birlikte one", (phi, 0, al, 0), (phi, 0, al, 0)))

    def kutular(KX, poz):
        cb = []
        for ad, p in KX:
            g = p["grup"]
            n = GRUP_UZ.get(g, 2 if g == "Kol" else 1)
            M = kol_matrisi(ad, g, tuple(float(x) for x in poz[:n]))
            cb.append((M, kutu_tasi(p["K8"], np_m(M))))
        return cb

    sonuc = []
    for tip, pr, pl in ciftler:
        cr, cl = kutular(KS, pr), kutular(KL, pl)
        BR = np.array([c[1] for c in cr])
        BL = np.array([c[1] for c in cl])
        G = np.sqrt((np.maximum(0.0, np.maximum(BL[None, :, :3] - BR[:, None, 3:], BR[:, None, :3] - BL[None, :, 3:])) ** 2).sum(2))
        v_cak = []

        def dal_sinir(Gm):
            en = (1e9, None)
            sira = np.dstack(np.unravel_index(np.argsort(Gm, axis=None), Gm.shape))[0]
            for i, j in sira:
                if Gm[i, j] >= en[0]:
                    break
                a = KS[i][1]["g"].copy()
                a.transformShape(cr[i][0])
                b = KL[j][1]["g"].copy()
                b.transformShape(cl[j][0])
                d = a.distToShape(b)[0]
                if d < 1e-6:
                    v = kesisim(a, b, a.BoundBox, b.BoundBox)
                    if (v > TOL or v < 0) and (KS[i][1]["ad"], KL[j][1]["ad"]) not in [x[:2] for x in v_cak]:
                        v_cak.append((KS[i][1]["ad"], KL[j][1]["ad"], round(v, 1)))
                if d < en[0]:
                    en = (d, (KS[i][1]["ad"], KL[j][1]["ad"]))
            return en

        en = dal_sinir(G)
        Gd = G.copy()                                   # yalniz dirsek parcalari (ust kol tupunun altindaki her sey)
        Gd[[i for i, (ad, _) in enumerate(KS) if not ad.startswith("dirsek")], :] = 1e9
        Gd[:, [j for j, (ad, _) in enumerate(KL) if not ad.startswith("dirsek")]] = 1e9
        en_d = dal_sinir(Gd)
        sonuc.append(dict(tip=tip, sag=list(pr), sol=list(pl), bosluk_mm=round(en[0], 1), cift=en[1], cakisma=v_cak,
                          dirsek_bosluk_mm=round(en_d[0], 1), dirsek_cift=en_d[1], kutu_bosluk_min=round(float(G.min()), 1)))
    en = min(sonuc, key=lambda s: s["bosluk_mm"])
    en_d = min(sonuc, key=lambda s: s["dirsek_bosluk_mm"])
    print("kol-kol: %d poz cifti, cakisan %d, en kucuk bosluk %.1f mm %s sag %s sol %s; dirsek parcalari arasi %.1f mm %s sag %s sol %s %.0fs" % (
        len(sonuc), sum(1 for s in sonuc if s["cakisma"]), en["bosluk_mm"], en["cift"], en["sag"], en["sol"],
        en_d["dirsek_bosluk_mm"], en_d["dirsek_cift"], en_d["sag"], en_d["sol"], time.time() - ts), flush=True)
    return dict(poz_cifti=len(sonuc), cakisan=sum(1 for s in sonuc if s["cakisma"]), en_kucuk=en, en_kucuk_dirsek=en_d,
                tip_ozet={t: min([s for s in sonuc if s["tip"] == t], key=lambda s: s["bosluk_mm"]) for t in sorted(set(s["tip"] for s in sonuc))},
                pozlar=sonuc, sure_s=round(time.time() - ts, 1),
                not_="hareketli: iki kolun omuz gobegi + ust kol (omuz) + dirsek parcalari; poz = (one-arka, yana, dirsek, bilek), "
                     "sol kolda ayni acilar aynali hareket")


# ====================================================================== 4b) kafa taramasi (pan x tilt; sabit moduller + iki kol)
# Kafa gruplari: Govde (traverse sabit), Pan = Ppan(psi), Kafa = Ppan(psi) Ptilt(th) (kafa_parcalar.grup_yer). Alt poz: Govde (),
# Pan (psi,), Kafa (psi, th). (a) hareketli kafa parcalari x sabit hedefler (iskelet, kabuk, iki omuzun govdesi, bolgeler):
# kaba pan -180...165 (15 derece, eklem araligi +-90 ayrica) x tilt -25...40 (serbest aralik; eklem araligi -25...30).
# (b) her kol: kol parcalari (omuz gobegi + ust kol, dirsek catali, on kol, el) kol zinciri kaba izgarasinin (1755 poz) + jest
# pozlarinin tum alt pozlarinda x kafanin tum parcalari (Govde dahil) tum kafa alt pozlarinda. Akilli ornekleme: kafanin
# supurdugu zarfa LIM_K'dan uzak kol alt pozlari sinir kutusu on elemesinde duser; kalan ciftler sinir kutusu boslugu sirasiyla
# YAKIN altindakiler hepsi, ustu kategori basina dal-sinirla tam olculur. (c) ince: eklem araliginda cakisan ya da INCE_ESIK
# altinda kalan ciftlerin cevresi 5 derece adimla (kafa pan/tilt +-5/10; kol omuz/dirsek +-5/10, bilek +-15) yeniden taranir.
import kafa_parcalar as KPm

KAFA_KABA = (list(range(-180, 180, 15)), [-25, -10, 0, 10, 20, 30, 40])
KAFA_INCE = ((-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10))
KAFA_GRUP_UZ = {"Govde": 0, "Pan": 1, "Kafa": 2}
LIM_K = 100.0        # mm: kafa taramasi kutu on elemesi
INCE_TUR = 1         # kafa x kol genel ince adim turu (cakisan + INCE_ESIK alti ciftlerin +-10 derece komsulugu)
SINIR_TUR = 40       # yasak bolge siniri: yalniz cakisan ciftlerin eksen komsulari (5 derece, bilek 15), yakinsayana dek
ONBELLEK = 3000      # tasinmis sekil onbellegi (LRU) ust siniri: bellek
JEST = [("ev", (0, 0, 0, 0)), ("selam (montaj gorseli)", (20, 100, 95, -60)), ("selam, kol yukarida", (0, 120, 105, 0)),
        ("selam, yan", (30, 90, 105, 90)), ("kafa kasima", (135, 30, 105, 0)), ("kafa kasima, bilek 90", (135, 45, 105, 90)),
        ("kafa kasima, yana 60", (120, 60, 105, -90)), ("kafa kasima, yana 15", (135, 15, 105, 0)), ("el yuze", (120, 0, 105, 0)),
        ("el yuze, bilek 90", (135, 0, 105, 90)), ("el agiza", (105, 0, 105, 0)), ("kol tepede", (135, 120, 0, 0)),
        ("kol tepede bukuk", (135, 120, 105, 0)), ("kol yana yukari bukuk", (45, 120, 105, 0)), ("eller basta", (120, 90, 105, 0))]


KT_TOL, KT_PAD = 0.2, 0.3     # mm: siki tutucu kutu icin tessellation sapmasi ve pay


def siki_noktalar(p):
    """Parcanin (global sekil) tessellation noktalarinin dis kabugu (Nx4): poz matrisiyle tasinip min/max alininca donmus parcanin
    siki sinir kutusu (+ KT_PAD) cikar; kose8 kutusundan (donmus kutunun kutusu) cok daha dar, hala tutucu."""
    if "KT" not in p:
        pts = np.array([[v.x, v.y, v.z] for v in p["g"].tessellate(KT_TOL)[0]])
        try:
            from scipy.spatial import ConvexHull
            pts = pts[ConvexHull(pts).vertices]
        except Exception:
            pass
        p["KT"] = np.hstack([pts, np.ones((len(pts), 1))])
    return p["KT"]


def kutu_siki(p, Mn):
    b = kutu_tasi(siki_noktalar(p), Mn)
    return b + np.array([-KT_PAD] * 3 + [KT_PAD] * 3)


def bosluk_mat(A_, B_):
    d = np.maximum(0.0, np.maximum(B_[None, :, :3] - A_[:, None, 3:], A_[:, None, :3] - B_[None, :, 3:]))
    return np.sqrt((d * d).sum(2))


def sar180(a):
    return ((a + 180.0) % 360.0) - 180.0


class Kume:
    """Aday cift kumesi: A (hareketli ogeler) x B (hedef ogeler). Ogeler anahtarla eklenir (kutu hesaplanir); ciftler sinir
    kutusu boslugu < LIM_K olanlar. degerlendir(): YAKIN altindaki her aday tam olculur, ustu kategori basina dal-sinir."""

    def __init__(s, kutu_A, kutu_B, olc, kat):
        s.kutu_A, s.kutu_B, s.olc_fn, s.kat = kutu_A, kutu_B, olc, kat
        s.A, s.B, s.Ai, s.Bi, s.AK, s.BK = [], [], {}, {}, [], []
        s.g, s.ia, s.ib = [np.zeros(0)], [np.zeros(0, dtype=np.int64)], [np.zeros(0, dtype=np.int64)]
        s.cift = set()
        s.olcum, s.en, s.n_tam = {}, {}, 0
        s.cak_alt = set()

    def a(s, k):
        if k not in s.Ai:
            s.Ai[k] = len(s.A)
            s.A.append(k)
            s.AK.append(s.kutu_A(k))
        return s.Ai[k]

    def b(s, k):
        if k not in s.Bi:
            s.Bi[k] = len(s.B)
            s.B.append(k)
            s.BK.append(s.kutu_B(k))
        return s.Bi[k]

    def hepsi(s, ia_l, ib_l):
        """ia_l x ib_l tum ciftler (kutu boslugu < LIM_K); once B zarfina uzak A ogeleri duser. Doner: eklenen aday sayisi."""
        AK, BK = np.array([s.AK[i] for i in ia_l]), np.array([s.BK[j] for j in ib_l])
        ia_a, ib_a = np.array(ia_l), np.array(ib_l)
        zarf_b = np.concatenate([BK[:, :3].min(0), BK[:, 3:].max(0)])
        yakin = np.nonzero(bosluk_np(zarf_b, AK) < LIM_K)[0]
        n = 0
        for k in range(0, len(yakin), 128):
            sec = yakin[k:k + 128]
            G = bosluk_mat(AK[sec], BK)
            i, j = np.nonzero(G < LIM_K)
            s.g.append(G[i, j])
            s.ia.append(ia_a[sec[i]])
            s.ib.append(ib_a[j])
            n += len(i)
        return n, len(yakin)

    def ciftler(s, L):
        """Belirli (ia, ib) ciftleri (ince adim)."""
        L = [c for c in L if c not in s.cift]
        if not L:
            return 0
        s.cift.update(L)
        ia_a = np.array([c[0] for c in L])
        ib_a = np.array([c[1] for c in L])
        AK, BK = np.array([s.AK[i] for i in ia_a]), np.array([s.BK[j] for j in ib_a])
        d = np.maximum(0.0, np.maximum(BK[:, :3] - AK[:, 3:], AK[:, :3] - BK[:, 3:]))
        G = np.sqrt((d * d).sum(1))
        m = G < LIM_K
        s.g.append(G[m])
        s.ia.append(ia_a[m])
        s.ib.append(ib_a[m])
        return int(m.sum())

    def degerlendir(s):
        g, ia, ib = np.concatenate(s.g), np.concatenate(s.ia), np.concatenate(s.ib)
        s.g, s.ia, s.ib = [np.zeros(0)], [np.zeros(0, dtype=np.int64)], [np.zeros(0, dtype=np.int64)]
        sira = np.argsort(g, kind="stable")
        ts = time.time()
        for k in sira:
            gk = float(g[k])
            i, j = int(ia[k]), int(ib[k])
            key = (i, j)
            if key in s.olcum:
                continue
            c, alt = s.kat(i, j)
            eb = s.en.get(c, (LIM_K,))[0]
            B = max(YAKIN, eb)
            if gk >= B:
                continue
            if alt in s.cak_alt and eb <= 0.0:
                continue     # bu alt poz cifti zaten cakisiyor, kategori en kucugu 0: ayni pozun diger parca ciftleri atlanir
            r = s.olc_fn(i, j, B)
            s.olcum[key] = r
            s.n_tam += 1
            if s.n_tam % 1000 == 0:
                print("    %d tam olcum, %.0fs" % (s.n_tam, time.time() - ts), flush=True)
            if r is None:
                continue
            if r[1] > TOL or r[1] < 0:
                s.cak_alt.add(alt)
            if r[0] < s.en.get(c, (1e9,))[0]:
                s.en[c] = (r[0], i, j)
        return len(sira)


def olc_iki(sa, sb_, B, fbb=None):
    """Iki hareketli sekil arasi (mesafe, cakisma hacmi); B'den uzaksa None. sb_ cok yuzluyse yalniz yakin yuzlerle."""
    ba = bb6(sa.BoundBox)
    if bosluk_np(ba, bb6(sb_.BoundBox)[None, :])[0] >= B:
        return None
    hedef_s = sb_
    if fbb is not None:
        fs = sb_.Faces
        sec = np.nonzero(bosluk_np(ba, fbb) < B)[0]
        if len(sec) == 0:
            return None
        hedef_s = fs[sec[0]] if len(sec) == 1 else Part.Compound([fs[i] for i in sec])
    d = sa.distToShape(hedef_s)[0]
    v = 0.0
    if d < GOMULU:
        v = kesisim(sa, sb_, sa.BoundBox, sb_.BoundBox)
        if v > TOL or v < 0:
            d = 0.0
    return d, v


class LRU(OrderedDict):
    """Sinirli onbellek: en eski kullanilan oge atilir (tasinmis sekiller bellegi doldurmasin)."""

    def __init__(s, n):
        super().__init__()
        s.n = n

    def al(s, k):
        if k in s:
            s.move_to_end(k)
            return s[k]
        return None

    def koy(s, k, v):
        s[k] = v
        if len(s) > s.n:
            s.popitem(last=False)
        return v


def hafif(sh, M):
    """Tasinmis sekil: geometri paylasilir (copy(False)), yalniz konum (Location) degisir; kati donusumde sonuc ayni."""
    s = sh.copy(False)
    s.transformShape(M)
    return s


def yasak_kurali(yasak):
    """Yasak bolge tablosu: kol (grup, one-arka, yana, dirsek) basina bilek degerleri ve yasak kafa pan / tilt araligi."""
    satir = {}
    for (g, sp), y in yasak.items():
        k = (g,) + tuple(sp[:3])
        r = satir.setdefault(k, dict(kol_grup=g, one_arka=sp[0], yana=sp[1] if len(sp) > 1 else None,
                                     dirsek=sp[2] if len(sp) > 2 else None, bilek=set(), pan=set(), tilt=set(), kafa_tum=False))
        if len(sp) > 3:
            r["bilek"].add(sp[3])
        for x in y["kafa"]:
            if len(x) == 1:
                r["kafa_tum"] = True
            if len(x) > 1:
                r["pan"].add(x[1])
            if len(x) > 2:
                r["tilt"].add(x[2])
    out = []
    for k in sorted(satir):
        r = satir[k]
        out.append(dict(kol_grup=r["kol_grup"], one_arka=r["one_arka"], yana=r["yana"], dirsek=r["dirsek"], bilek=sorted(r["bilek"]),
                        pan=[min(r["pan"]), max(r["pan"])] if r["pan"] else None, pan_degerleri=sorted(r["pan"]),
                        tilt=[min(r["tilt"]), max(r["tilt"])] if r["tilt"] else None, kafa_tum_pozlar=r["kafa_tum"]))
    return out


def kafa_tara(kisimlar=("sabit", "sag", "sol")):
    ts0 = time.time()
    KP_ = aktif(MODUL["kafa"])
    T = MODUL["kafa"]["T"]
    for p in KP_:
        p["K8"] = kose8(p["gbb"])
    _kj = json.load(open(os.path.join(HERE, "kafa", "kafa-analiz.json"), encoding="utf-8"))
    AR = (tuple(A.KAFA["pan_aralik"]), tuple(A.KAFA["tilt_aralik"]))
    SERBEST = tuple(tuple(float(x) for x in e["serbest_aralik"]) for e in _kj["eklemler"])     # pan, tilt (kafa_montaj)

    def k_aralikta(ksp):
        return all(AR[k][0] - 1e-9 <= v <= AR[k][1] + 1e-9 for k, v in enumerate(ksp))

    def k_serbest(ksp):
        return len(ksp) < 2 or SERBEST[1][0] - 1e-9 <= ksp[1] <= SERBEST[1][1] + 1e-9

    kmc = {}

    def k_mat(g, ksp):
        if (g, ksp) not in kmc:
            psi, th = (list(ksp) + [0.0, 0.0])[:2]
            kmc[(g, ksp)] = T.multiply(KPm.grup_yer(g, psi, th).toMatrix()).multiply(T.inverse())
        return kmc[(g, ksp)]

    ksc = LRU(ONBELLEK)

    def k_sekil(pi, ksp):
        k = (pi, ksp)
        r = ksc.al(k)
        if r is None:
            p = KP_[pi]
            s = hafif(p["g"], k_mat(p["grup"], ksp)) if ksp else p["g"]
            fs = s.Faces
            r = ksc.koy(k, (s, np.array([bb6(f.BoundBox) for f in fs]) if len(fs) > ESIK_YUZ else None))
        return r

    def k_kutu(k):
        pi, ksp = k
        p = KP_[pi]
        return bb6(p["gbb"]) if not ksp else kutu_siki(p, np_m(k_mat(p["grup"], ksp)))

    def k_alt(ksp_tam, g):
        return tuple(float(x) for x in ksp_tam[:KAFA_GRUP_UZ[g]])

    kaba_k = [(float(a), float(b)) for a in KAFA_KABA[0] for b in KAFA_KABA[1]]
    if KISA:
        kaba_k = [k for k in kaba_k if -60 <= k[0] <= 60]

    def k_ince(ksp):
        rng = [[ksp[k] + dd for dd in KAFA_INCE[k]] for k in range(len(ksp))]
        out = set()
        for q in itertools.product(*rng):
            q = tuple(float(sar180(x)) if k == 0 else float(x) for k, x in enumerate(q))
            if k_serbest(q) and k_aralikta(q):
                out.add(q)
        return out

    sonuc_sabit = None
    if "sabit" in kisimlar:
        # ------------------------------------------------------------ (a) kafa x sabit hedefler
        sabit = []
        for ad in adlar:
            dd = MODUL[ad]
            if ozel(dd):
                continue
            if dd["hareket"]:
                if ad.startswith("omuz_"):
                    sabit += [dict(mod="%s govde" % ad, ad=q["ad"], g=q["g"], gbbF=q["gbb"], bb=bb6(q["gbb"])) for q in aktif(dd)
                              if q["grup"] == "sabit"]
                continue
            sabit += [dict(mod=ad, ad=q["ad"], g=q["g"], gbbF=q["gbb"], bb=bb6(q["gbb"])) for q in aktif(dd)]
        har_k = list(range(len(KP_)))      # Govde (sabit boyun) de: R62 halkasina ve traverse en kucuk bosluk (alt poz ())

        def gmod(pi, j):
            return sabit[j]["mod"] + (" (kafa govdesi)" if KP_[pi]["grup"] == "Govde" else "")

        def kat_s(i, j):
            pi, ksp = KS.A[i]
            return (gmod(pi, KS.B[j]), k_aralikta(ksp)), (KP_[pi]["grup"], ksp)

        def olc_s(i, j, B):
            pi, ksp = KS.A[i]
            return tam_olc(k_sekil(pi, ksp)[0], sabit[KS.B[j]], B)

        KS = Kume(k_kutu, lambda j: sabit[j]["bb"], olc_s, kat_s)
        ia_l = [KS.a((pi, k_alt(kk, KP_[pi]["grup"]))) for pi in har_k for kk in kaba_k]
        ib_l = [KS.b(j) for j in range(len(sabit))]
        n_aday, _ = KS.hepsi(sorted(set(ia_l)), ib_l)
        KS.degerlendir()
        isa = [(i, j) for (i, j), r in KS.olcum.items() if r and (r[0] < INCE_ESIK or r[1] > TOL or r[1] < 0) and k_aralikta(KS.A[i][1])]
        yeni = []
        for i, j in isa:
            pi, ksp = KS.A[i]
            for q in k_ince(ksp):
                yeni.append((KS.a((pi, q)), j))
        n_ince = KS.ciftler(yeni)
        KS.degerlendir()
        print("kafa x sabit: %d kaba alt poz, %d aday, ince %d, %d tam olcum %.0fs" % (len(set(ia_l)), n_aday, n_ince, KS.n_tam,
                                                                                     time.time() - ts0), flush=True)

        def bulgu_s(i, j, r):
            pi, ksp = KS.A[i]
            q = sabit[KS.B[j]]
            return dict(kafa_grup=KP_[pi]["grup"], kafa_poz=list(ksp), parca=KP_[pi]["ad"], hedef_modul=gmod(pi, KS.B[j]), hedef=q["ad"],
                        bosluk_mm=round(r[0], 2), hacim_mm3=round(r[1], 1), aralikta=k_aralikta(ksp))

        bl = [bulgu_s(i, j, r) for (i, j), r in KS.olcum.items() if r is not None]
        cak_s = [b for b in bl if b["hacim_mm3"] > TOL or b["hacim_mm3"] < 0]
        mm_s = {}
        for b in bl:
            k = (b["hedef_modul"], b["aralikta"])
            if b["bosluk_mm"] < mm_s.get(k, dict(bosluk_mm=1e9))["bosluk_mm"]:
                mm_s[k] = b
        cift_s = {}
        for b in bl:
            if b["aralikta"]:
                k = (b["parca"], b["hedef"])
                if b["bosluk_mm"] < cift_s.get(k, dict(bosluk_mm=1e9))["bosluk_mm"]:
                    cift_s[k] = b
        sonuc_sabit = dict(
            kaba=dict(pan=KAFA_KABA[0], tilt=KAFA_KABA[1], poz=len(kaba_k)), aday=n_aday, ince_cift=n_ince, tam_olcum=KS.n_tam,
            cakisma_aralikta=sorted([b for b in cak_s if b["aralikta"]], key=lambda b: b["kafa_poz"])[:100],
            cakisma_aralik_disi=sorted([b for b in cak_s if not b["aralikta"]], key=lambda b: b["kafa_poz"])[:100],
            cakisan_alt_poz_aralikta=len(set((b["kafa_grup"], tuple(b["kafa_poz"])) for b in cak_s if b["aralikta"])),
            cakisan_alt_poz_aralik_disi=len(set((b["kafa_grup"], tuple(b["kafa_poz"])) for b in cak_s if not b["aralikta"])),
            en_kucuk_aralikta={m: b for (m, a), b in mm_s.items() if a}, en_kucuk_aralik_disi={m: b for (m, a), b in mm_s.items() if not a},
            en_kucuk_ciftler_aralikta=sorted(cift_s.values(), key=lambda b: b["bosluk_mm"])[:12],
            sure_s=round(time.time() - ts0, 1))
        for m, b in sorted(sonuc_sabit["en_kucuk_aralikta"].items()):
            print("  kafa -> %-22s %.2f mm %s %s / %s" % (m, b["bosluk_mm"], b["kafa_poz"], b["parca"], b["hedef"]))
        print("kafa x sabit: aralikta cakisan alt poz %d, aralik disi %d" % (sonuc_sabit["cakisan_alt_poz_aralikta"],
                                                                             sonuc_sabit["cakisan_alt_poz_aralik_disi"]), flush=True)
        ksc.clear()
        gc.collect()

    # ------------------------------------------------------------ (b) kafa x kol (her taraf)
    KOL_KAT = {"Gobek": "omuz", "Kol": "omuz", "UstKol": "dirsek catali", "OnKol": "on kol", "El": "el"}
    kol_alt_uz = {"Gobek": 1, "Kol": 2, "UstKol": 2, "OnKol": 3, "El": 4}
    kaba_kol = [(float(a), float(b), float(c), float(d)) for a in KABA[0] for b in KABA[1] for c in KABA[2] for d in KABA[3]]
    if KISA:
        kaba_kol = [p for p in kaba_kol if p[0] >= 120 and p[1] <= 15 and p[2] >= 90]
    jest_poz = [tuple(float(x) for x in p) for _, p in JEST]
    ADIM_I = ((-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-15, 0, 15))
    kol_sonuc = {}
    for taraf in [t for t in ("sag", "sol") if t in kisimlar]:
        ts = time.time()
        om, dr = "omuz_" + taraf, "dirsek_" + taraf
        AP = [(om, p) for p in aktif(MODUL[om]) if p["grup"] in ("Gobek", "Kol")] + [(dr, p) for p in aktif(MODUL[dr])]
        for _, p in AP:
            if "K8" not in p:
                p["K8"] = kose8(p["gbb"])
        amc, asc = {}, LRU(ONBELLEK)

        def a_mat(ai, sp):
            ad, p = AP[ai]
            k = (ad, p["grup"], sp)
            if k not in amc:
                amc[k] = kol_matrisi(ad, p["grup"], sp)
            return amc[k]

        def a_kutu(k):
            ai, sp = k
            return kutu_siki(AP[ai][1], np_m(a_mat(ai, sp)))

        def a_sekil(ai, sp):
            r = asc.al((ai, sp))
            if r is None:
                r = asc.koy((ai, sp), hafif(AP[ai][1]["g"], a_mat(ai, sp)))
            return r

        def kat_k(i, j):
            ai, sp = KK.A[i]
            pi, ksp = KK.B[j]
            ic = kol_araliginda(sp) and k_aralikta(ksp)
            return (KOL_KAT[AP[ai][1]["grup"]], ic), ((AP[ai][1]["grup"], sp), (KP_[pi]["grup"], ksp))

        def olc_k(i, j, B):
            ai, sp = KK.A[i]
            pi, ksp = KK.B[j]
            s_k, fbb = k_sekil(pi, ksp)
            return olc_iki(a_sekil(ai, sp), s_k, B, fbb)

        KK = Kume(a_kutu, k_kutu, olc_k, kat_k)
        alt_a = set()
        for poz in kaba_kol + jest_poz:
            for ai, (_, p) in enumerate(AP):
                alt_a.add((ai, tuple(poz[:kol_alt_uz[p["grup"]]])))
        ia_l = [KK.a(k) for k in sorted(alt_a)]
        alt_k = set()
        for kk in kaba_k:
            for pi, p in enumerate(KP_):
                alt_k.add((pi, k_alt(kk, p["grup"])))
        ib_l = [KK.b(k) for k in sorted(alt_k)]
        n_aday, n_yakin_a = KK.hepsi(ia_l, ib_l)
        yakin_poz = set()
        if n_aday:
            ia_y = set(int(x) for x in np.concatenate(KK.ia))
            alt_y = set((AP[KK.A[i][0]][1]["grup"], KK.A[i][1]) for i in ia_y)
            for poz in kaba_kol + jest_poz:       # kafaya LIM_K'dan yakin dirsek parcasi (catal, on kol, el) olan tam kol pozu
                if any((g, tuple(poz[:kol_alt_uz[g]])) in alt_y for g in ("UstKol", "OnKol", "El")):
                    yakin_poz.add(poz)
        print("kafa x kol %s: %d kol alt ogesi (%d zarfa yakin), %d kafa ogesi, %d aday, dirsegi kafaya %d mm'den yakin tam kol pozu %d / %d %.0fs" % (
            taraf, len(ia_l), n_yakin_a, len(ib_l), n_aday, LIM_K, len(yakin_poz), len(kaba_kol) + len(jest_poz), time.time() - ts), flush=True)
        KK.degerlendir()
        print("kafa x kol %s: kaba %d tam olcum %.0fs" % (taraf, KK.n_tam, time.time() - ts), flush=True)
        # ince: eklem araliginda cakisan / INCE_ESIK alti ciftlerin cevresi (kafa ve kol ayri ayri komsulanir); yeni isaretli cift
        # kalmayana dek (en cok INCE_TUR tur) tekrarlanir: yasak bolgenin siniri 5 derece adimla izlenir
        genisletilen = set()
        n_ince, n_isa, tur = 0, 0, 0
        while tur < INCE_TUR:
            isa = [(i, j) for (i, j), r in KK.olcum.items()
                   if r and (r[0] < INCE_ESIK or r[1] > TOL or r[1] < 0) and kat_k(i, j)[0][1] and (i, j) not in genisletilen]
            if not isa:
                break
            tur += 1
            genisletilen.update(isa)
            n_isa += len(isa)
            yeni = []
            for i, j in isa:
                ai, sp = KK.A[i]
                pi, ksp = KK.B[j]
                for q in k_ince(ksp):
                    yeni.append((i, KK.b((pi, q))))
                rng = [[sp[k] + dd for dd in ADIM_I[k]] for k in range(len(sp))]
                for q in itertools.product(*rng):
                    q = tuple(float(x) for x in q)
                    if kol_araliginda(q):
                        yeni.append((KK.a((ai, q)), j))
            n_ince += KK.ciftler(yeni)
            KK.degerlendir()
            print("kafa x kol %s: ince tur %d, isaretli %d cift, toplam %d tam olcum %.0fs" % (taraf, tur, len(isa), KK.n_tam,
                                                                                             time.time() - ts), flush=True)
        # yasak bolge siniri: eklem araligindaki cakisan ciftlerin her eksende tek adim komsusu (kafa pan/tilt 5, kol omuz/yana/
        # dirsek 5, bilek 15 derece) olculur; yeni cakisan cift kalmayana dek tekrarlanir. Yakinsayinca bolgenin siniri 5 derece
        # (bilek 15) kesinliginde kapali: her cakisan pozun aralik icindeki tum eksen komsulari olculmus durumda.
        sinir_genis = set()
        s_tur, s_cift, yakinsadi = 0, 0, False
        while s_tur < SINIR_TUR:
            isa = [(i, j) for (i, j), r in KK.olcum.items()
                   if r and (r[1] > TOL or r[1] < 0) and kat_k(i, j)[0][1] and (i, j) not in sinir_genis]
            if not isa:
                yakinsadi = True
                break
            s_tur += 1
            sinir_genis.update(isa)
            yeni = []
            for i, j in isa:
                ai, sp = KK.A[i]
                pi, ksp = KK.B[j]
                for k in range(len(ksp)):
                    for dd in (-5.0, 5.0):
                        q = list(ksp)
                        q[k] += dd
                        q = tuple(float(sar180(x)) if kk == 0 else float(x) for kk, x in enumerate(q))
                        if k_serbest(q) and k_aralikta(q):
                            yeni.append((i, KK.b((pi, q))))
                for k in range(len(sp)):
                    st = 15.0 if k == 3 else 5.0
                    for dd in (-st, st):
                        q = list(sp)
                        q[k] += dd
                        q = tuple(float(x) for x in q)
                        if kol_araliginda(q):
                            yeni.append((KK.a((ai, q)), j))
            s_cift += KK.ciftler(yeni)
            KK.degerlendir()
            print("kafa x kol %s: sinir turu %d, cakisan genisletilen %d cift, toplam %d tam olcum, bellek %s MB %.0fs" % (
                taraf, s_tur, len(isa), KK.n_tam, bellek_mb()[1], time.time() - ts), flush=True)

        def bulgu_k(i, j, r):
            ai, sp = KK.A[i]
            pi, ksp = KK.B[j]
            return dict(kol_grup=AP[ai][1]["grup"], kol_poz=list(sp), parca=AP[ai][1]["ad"], kafa_grup=KP_[pi]["grup"],
                        kafa_poz=list(ksp), kafa_parca=KP_[pi]["ad"], kategori=KOL_KAT[AP[ai][1]["grup"]],
                        bosluk_mm=round(r[0], 2), hacim_mm3=round(r[1], 1), aralikta=kol_araliginda(sp) and k_aralikta(ksp))

        bl = [bulgu_k(i, j, r) for (i, j), r in KK.olcum.items() if r is not None]
        cak = [b for b in bl if b["hacim_mm3"] > TOL or b["hacim_mm3"] < 0]
        mm = {}
        for b in bl:
            k = (b["kategori"], b["aralikta"])
            if b["bosluk_mm"] < mm.get(k, dict(bosluk_mm=1e9))["bosluk_mm"]:
                mm[k] = b
        cift = {}
        for b in bl:
            if b["aralikta"]:
                k = (b["parca"], b["kafa_parca"])
                if b["bosluk_mm"] < cift.get(k, dict(bosluk_mm=1e9))["bosluk_mm"]:
                    cift[k] = b
        # yasak poz bolgeleri: eklem araligindaki cakisan (kol alt pozu, kafa alt pozu) ciftleri, kol alt pozuna gore
        yasak = {}
        for b in cak:
            if not b["aralikta"]:
                continue
            k = (b["kol_grup"], tuple(b["kol_poz"]))
            y = yasak.setdefault(k, dict(kol_grup=b["kol_grup"], kol_poz=b["kol_poz"], parcalar=set(), kafa=set()))
            y["parcalar"].add("%s / %s" % (b["parca"], b["kafa_parca"]))
            y["kafa"].add((b["kafa_grup"],) + tuple(b["kafa_poz"]))
        yasak_l = []
        for k, y in sorted(yasak.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            panlar = sorted(set(x[1] for x in y["kafa"] if len(x) > 1))
            govde = any(len(x) == 1 for x in y["kafa"])
            yasak_l.append(dict(kol_grup=y["kol_grup"], kol_poz=y["kol_poz"], parcalar=sorted(y["parcalar"]),
                                kafa_tum_pozlar=govde, yasak_pan=panlar,
                                yasak_kafa_poz=sorted([list(x[1:]) for x in y["kafa"]])[:60]))
        # yasak bolge ozeti: cakisan kol alt pozlarinin acilari ve cakisan kafa pozlarinin pan/tilt araligi (kol grubu basina)
        yasak_ozet = {}
        for y in yasak.values():
            g = y["kol_grup"]
            o = yasak_ozet.setdefault(g, dict(kol_alt_poz=0, kol_min=[1e9] * len(y["kol_poz"]), kol_max=[-1e9] * len(y["kol_poz"]),
                                              pan=[1e9, -1e9], tilt=[1e9, -1e9], kafa_tum_pozlar=False, parcalar=set()))
            o["kol_alt_poz"] += 1
            o["kol_min"] = [min(a_, b_) for a_, b_ in zip(o["kol_min"], y["kol_poz"])]
            o["kol_max"] = [max(a_, b_) for a_, b_ in zip(o["kol_max"], y["kol_poz"])]
            o["parcalar"].update(y["parcalar"])
            for x in y["kafa"]:
                if len(x) == 1:
                    o["kafa_tum_pozlar"] = True
                if len(x) > 1:
                    o["pan"] = [min(o["pan"][0], x[1]), max(o["pan"][1], x[1])]
                if len(x) > 2:
                    o["tilt"] = [min(o["tilt"][0], x[2]), max(o["tilt"][1], x[2])]
        for o in yasak_ozet.values():
            o["parcalar"] = sorted(o["parcalar"])[:8]
            for k in ("pan", "tilt"):
                if o[k][0] > o[k][1]:
                    o[k] = None
        jest_ozet = []
        for ad_j, poz in JEST:
            poz = tuple(float(x) for x in poz)
            alts = [(g, tuple(poz[:n])) for g, n in kol_alt_uz.items()]
            en = None
            for b in bl:
                if (b["kol_grup"], tuple(b["kol_poz"])) in alts and k_aralikta(tuple(b["kafa_poz"])):
                    if en is None or b["bosluk_mm"] < en["bosluk_mm"]:
                        en = b
            yk = sorted(set(p for (g, sp), y in yasak.items() if (g, sp) in alts for p in [tuple(x[1:]) for x in y["kafa"]]))
            jest_ozet.append(dict(ad=ad_j, poz=list(poz), en_kucuk=en, yakin=(poz in yakin_poz),
                                  cakisan_kafa_poz=[list(x) for x in yk][:40]))
        kol_sonuc[taraf] = dict(
            kol_alt_oge=len(ia_l), zarfa_yakin_alt_oge=n_yakin_a, kafa_oge=len(ib_l), aday=n_aday, ince_aday=n_ince, ince_tur=tur,
            ince_isaretli=n_isa, sinir_tur=s_tur, sinir_aday=s_cift, sinir_yakinsadi=yakinsadi,
            yasak_kural=yasak_kurali(yasak),
            tam_olcum=KK.n_tam, kafaya_yakin_tam_kol_pozu=len(yakin_poz), kol_pozu=len(kaba_kol) + len(jest_poz),
            kafa_pozu=len(kaba_k),
            cakisan_cift_aralikta=len(set(((b["kol_grup"], tuple(b["kol_poz"])), (b["kafa_grup"], tuple(b["kafa_poz"]))) for b in cak if b["aralikta"])),
            cakisan_cift_aralik_disi=len(set(((b["kol_grup"], tuple(b["kol_poz"])), (b["kafa_grup"], tuple(b["kafa_poz"]))) for b in cak if not b["aralikta"])),
            cakismalar_aralikta=sorted([b for b in cak if b["aralikta"]], key=lambda b: (b["kol_grup"], b["kol_poz"], b["kafa_poz"]))[:150],
            cakismalar_aralik_disi=sorted([b for b in cak if not b["aralikta"]], key=lambda b: (b["kol_grup"], b["kol_poz"], b["kafa_poz"]))[:60],
            en_kucuk_aralikta={c: b for (c, a), b in mm.items() if a}, en_kucuk_aralik_disi={c: b for (c, a), b in mm.items() if not a},
            en_kucuk_ciftler_aralikta=sorted(cift.values(), key=lambda b: b["bosluk_mm"])[:12],
            yasak=yasak_l[:200], yasak_sayi=len(yasak_l), yasak_ozet=yasak_ozet, jest=jest_ozet, sure_s=round(time.time() - ts, 1))
        for c, b in sorted(kol_sonuc[taraf]["en_kucuk_aralikta"].items()):
            print("  %s kafa <-> %-14s %.2f mm kol %s %s / kafa %s %s" % (taraf, c, b["bosluk_mm"], b["kol_poz"], b["parca"],
                                                                         b["kafa_poz"], b["kafa_parca"]))
        print("kafa x kol %s: aralikta cakisan cift %d, yasak kol alt pozu %d, %.0fs" % (
            taraf, kol_sonuc[taraf]["cakisan_cift_aralikta"], len(yasak_l), time.time() - ts), flush=True)
        asc.clear()
        ksc.clear()
        gc.collect()
    return dict(aralik=dict(pan=list(AR[0]), tilt=list(AR[1])), serbest=dict(pan=list(SERBEST[0]), tilt=list(SERBEST[1])),
                kaba=dict(pan=KAFA_KABA[0], tilt=KAFA_KABA[1]), ince_adim=list(KAFA_INCE), sinir_adim=dict(kafa=5, omuz=5, yana=5, dirsek=5, bilek=15), sinir_tur_siniri=SINIR_TUR,
                lim_mm=LIM_K, yakin_mm=YAKIN, kisimlar=list(kisimlar),
                jest=[dict(ad=a, poz=list(p)) for a, p in JEST], sabit=sonuc_sabit, kol=kol_sonuc,
                not_="kafa pozu = (pan, tilt); kol pozu = (one-arka, yana, dirsek, bilek); alt poz: kafa Govde (), Pan (pan), Kafa (pan, tilt); "
                     "kol Gobek (one-arka), Kol/UstKol (one-arka, yana), OnKol (+dirsek), El (+bilek). Eklem araligi: kafa pan +-90, tilt "
                     "-25...30 ve kol araligi; aralik disi = kafa pan +-90 disi ya da tilt 40 (serbest -25...40) ya da kol ince komsulugu disi. "
                     "Olculmeyen ciftlerin boslugu >= %d mm (sinir kutusu)." % LIM_K,
                sure_s=round(time.time() - ts0, 1))


# ====================================================================== 4c) taban taramasi
# (a) statik: taban <-> her modul ev pozunda: kutusu kesisen her cift icin cakisma hacmi (common), 1 mm icindeki ciftlerde mesafe
#     (temas = 0 mm, hacim <= TOL), modul basina en kucuk bosluk dal-sinirla.
# (b) kol x taban: iki kolun kol zinciri kaba izgarasi (1755 poz) + aralik disi halka (279) + jest pozlarinin tum alt pozlari
#     (omuz gobegi + ust kol, dirsek catali, on kol, el) x taban parcalari (+ ana anahtar dugmesi gosterimi) ve kabugun etek
#     parcalari. Siki tutucu kutularla (tessellation dis kabugu) bosluk alt siniri; kategori (acil stop, sonar, ana anahtar
#     dugmesi, etek, taban diger) basina en kucuk bosluk dal-sinirla tam olculur; YAKIN altindaki her aday tam olculur
#     (cakisma). En kucuklerin cevresi 5 derece adimla (bilek 15) yeniden taranir.
# (c) kafa x taban: kafanin tum pan x tilt pozlarindaki siki kutularinin en alt noktasi tabanin en ust noktasindan LIM_K'dan
#     uzaksa olculmez (not edilir); degilse olcum gerektigi yazilir.
TABAN_KAT = (("Acil stop", "acil stop"), ("Sonar", "sonar"), ("Ana anahtar dugmesi", "ana anahtar dugmesi"))


def taban_kat(ad, mod):
    if mod != "taban":
        return "etek (kabuk)"
    for on, k in TABAN_KAT:
        if ad.startswith(on):
            return k
    return "taban diger"


def taban_tara():
    ts0 = time.time()
    TB = aktif(MODUL["taban"])
    gost = [p for p in MODUL["taban"]["parcalar"] if p["haric"] and p["ad"].startswith("Ana anahtar dugmesi")]
    TBB = np.array([bb6(p["gbb"]) for p in TB])
    TBq = [dict(mod="taban", ad=p["ad"], g=p["g"], gbbF=p["gbb"], bb=bb6(p["gbb"])) for p in TB]

    # ------------------------------------------------------------ (a) statik (ev pozu)
    statik_t = {}
    for ad in adlar:
        if ad in ("taban", "ayrilmis_bolgeler") or not aktif(MODUL[ad]):
            continue
        H = [dict(mod=ad, ad=q["ad"], g=q["g"], gbbF=q["gbb"], bb=bb6(q["gbb"])) for q in aktif(MODUL[ad])]
        G = bosluk_mat(TBB, np.array([q["bb"] for q in H]))
        cak, temas, olc = [], [], {}
        kes = list(zip(*np.nonzero(G <= 0.0)))
        for i, j in kes:
            v = kesisim(TB[i]["g"], H[j]["g"], TB[i]["gbb"], H[j]["gbbF"])
            if v > TOL or v < 0:
                cak.append(dict(taban=TB[i]["ad"], hedef=H[j]["ad"], hacim_mm3=round(v, 2)))
        for i, j in zip(*np.nonzero(G <= 1.0)):
            r = tam_olc(TB[i]["g"], H[j], 1.0)
            if r is not None:
                olc[(i, j)] = r
                if r[0] < 0.01 and not (r[1] > TOL or r[1] < 0):
                    temas.append("%s / %s" % (TB[i]["ad"], H[j]["ad"]))
        en = min(((r[0], k) for k, r in olc.items()), default=(1e9, None))
        sira = np.dstack(np.unravel_index(np.argsort(G, axis=None), G.shape))[0]
        n_tam = len(olc)
        for i, j in sira:
            if G[i, j] >= en[0]:
                break
            if (i, j) in olc:
                continue
            r = tam_olc(TB[i]["g"], H[j], en[0])
            n_tam += 1
            if r is not None and r[0] < en[0]:
                en = (r[0], (i, j))
        statik_t[ad] = dict(kutu_kesisen=len(kes), cakisma=cak, temas=len(temas), temas_ornek=sorted(temas)[:12],
                            en_kucuk_bosluk_mm=round(en[0], 2) if en[1] else None,
                            en_yakin=[TB[en[1][0]]["ad"], H[en[1][1]]["ad"]] if en[1] else None, tam_olcum=n_tam)
        print("taban <-> %-11s kutu kesisen %d, cakisma %d, temas %d, en kucuk %.2f mm %s %.0fs" % (
            ad, len(kes), len(cak), len(temas), en[0], statik_t[ad]["en_yakin"], time.time() - ts0), flush=True)
        del H
        gc.collect()

    # ------------------------------------------------------------ (b) kol x taban
    hedef = [dict(q, kat=taban_kat(q["ad"], "taban")) for q in TBq] + \
            [dict(mod="taban", ad=p["ad"], g=p["g"], gbbF=p["gbb"], bb=bb6(p["gbb"]), kat=taban_kat(p["ad"], "taban")) for p in gost]
    if "kabuk" in MODUL:
        hedef += [dict(mod="kabuk", ad=q["ad"], g=q["g"], gbbF=q["gbb"], bb=bb6(q["gbb"]), kat="etek (kabuk)")
                  for q in aktif(MODUL["kabuk"]) if q["ad"].startswith("Etek")]
    HB = np.array([q["bb"] for q in hedef])
    KAT = sorted(set(q["kat"] for q in hedef))
    kat_idx = {c: np.array([j for j, q in enumerate(hedef) if q["kat"] == c]) for c in KAT}
    kol_alt_uz = {"Gobek": 1, "Kol": 2, "UstKol": 2, "OnKol": 3, "El": 4}
    kaba = [(float(a), float(b), float(c), float(d)) for a in KABA[0] for b in KABA[1] for c in KABA[2] for d in KABA[3]]
    disi = [(float(phi), float(th), float(al), float(be)) for phi in (-60, 150) for th in KABA[1] for al in DISI_AL for be in DISI_BE] + \
           [(float(phi), -10.0, float(al), float(be)) for phi in KABA[0] for al in DISI_AL for be in DISI_BE]
    jest = [tuple(float(x) for x in p) for _, p in JEST]
    ADIM_I = ((-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-15, 0, 15))
    kol_t = {}
    for taraf in ("sag", "sol"):
        ts = time.time()
        om, dr = "omuz_" + taraf, "dirsek_" + taraf
        AP = [(om, p) for p in aktif(MODUL[om]) if p["grup"] in ("Gobek", "Kol")] + [(dr, p) for p in aktif(MODUL[dr])]
        ogeler, AKl = [], []
        oge_i = {}

        def ekle(L):
            yeni = []
            for k in L:
                if k in oge_i:
                    continue
                ai, sp = k
                ad, p = AP[ai]
                oge_i[k] = len(ogeler)
                ogeler.append(k)
                AKl.append(kutu_siki(p, np_m(kol_matrisi(ad, p["grup"], sp))))
                yeni.append(oge_i[k])
            return yeni

        alt0 = sorted(set((ai, tuple(poz[:kol_alt_uz[p["grup"]]])) for poz in kaba + disi + jest for ai, (_, p) in enumerate(AP)))
        ekle(alt0)
        olcum = {}

        def olc(i, j, B):
            if (i, j) in olcum:
                return olcum[(i, j)]
            ai, sp = ogeler[i]
            ad, p = AP[ai]
            r = tam_olc(hafif(p["g"], kol_matrisi(ad, p["grup"], sp)), hedef[j], B)
            olcum[(i, j)] = r
            return r

        en = {}             # (kat, aralikta) -> (d, i, j)

        def tara(idx):
            """idx (oge indeksleri) x tum hedefler: YAKIN alti hepsi, ustu kategori basina dal-sinir."""
            idx = np.array(idx)
            AK = np.array([AKl[i] for i in idx])
            ic_m = np.array([kol_araliginda(ogeler[i][1]) for i in idx])
            for c in KAT:
                J = kat_idx[c]
                for ic in (True, False):
                    sec = ic_m == ic
                    if not sec.any():
                        continue
                    Ii, AKs = idx[sec], AK[sec]
                    G = np.concatenate([bosluk_mat(AKs[k:k + 2000], HB[J]) for k in range(0, len(Ii), 2000)])
                    sira = np.argsort(G, axis=None)
                    B = en.get((c, ic), (1e9,))[0]
                    for f in sira:
                        a, b = divmod(int(f), len(J))
                        if G[a, b] >= max(B, YAKIN):
                            break
                        i, j = int(Ii[a]), int(J[b])
                        r = olc(i, j, max(B, YAKIN))
                        if r is not None and r[0] < B:
                            B = r[0]
                            en[(c, ic)] = (r[0], i, j)

        tara(list(range(len(ogeler))))
        n_kaba = len(olcum)
        # ince: her kategorinin en kucugu (aralikta) cevresinde 5 derece (bilek 15) komsuluk, ayni parca
        ince = []
        for (c, ic), (d0, i, j) in list(en.items()):
            if not ic:
                continue
            ai, sp = ogeler[i]
            rng = [[sp[k] + dd for dd in ADIM_I[k]] for k in range(len(sp))]
            for q in itertools.product(*rng):
                q = tuple(float(x) for x in q)
                if kol_araliginda(q):
                    ince.append((ai, q))
        yeni = ekle(sorted(set(ince)))
        if yeni:
            tara(yeni)

        def bulgu(i, j, r):
            ai, sp = ogeler[i]
            return dict(kol_grup=AP[ai][1]["grup"], kol_poz=list(sp), parca=AP[ai][1]["ad"], hedef_modul=hedef[j]["mod"],
                        hedef=hedef[j]["ad"], kategori=hedef[j]["kat"], bosluk_mm=round(r[0], 2), hacim_mm3=round(r[1], 1),
                        aralikta=kol_araliginda(sp))

        cak = [bulgu(i, j, r) for (i, j), r in olcum.items() if r is not None and (r[1] > TOL or r[1] < 0)]
        # kolun en alt noktasi (siki kutu alt siniri; tutucu) eklem araliginda
        AKa = np.array(AKl)
        ar = np.array([kol_araliginda(sp) for _, sp in ogeler])
        k_alt = int(np.argmin(np.where(ar, AKa[:, 1], 1e9)))
        kol_t[taraf] = dict(
            poz=dict(kaba=len(kaba), aralik_disi=len(disi), jest=len(jest)), alt_oge=len(alt0), ince_alt_oge=len(yeni),
            tam_olcum=len(olcum), tam_olcum_kaba=n_kaba,
            cakisan_alt_poz_aralikta=len(set((b["kol_grup"], tuple(b["kol_poz"])) for b in cak if b["aralikta"])),
            cakisan_alt_poz_aralik_disi=len(set((b["kol_grup"], tuple(b["kol_poz"])) for b in cak if not b["aralikta"])),
            cakismalar=cak[:100],
            en_kucuk_aralikta={c: bulgu(v[1], v[2], olcum[(v[1], v[2])]) for (c, ic), v in sorted(en.items()) if ic},
            en_kucuk_aralik_disi={c: bulgu(v[1], v[2], olcum[(v[1], v[2])]) for (c, ic), v in sorted(en.items()) if not ic},
            kol_en_alt=dict(y_mm=round(float(AKa[k_alt, 1]), 1), kol_grup=AP[ogeler[k_alt][0]][1]["grup"], kol_poz=list(ogeler[k_alt][1]),
                            parca=AP[ogeler[k_alt][0]][1]["ad"], not_="siki tutucu kutunun alt siniri (gercek nokta en cok ~0,5 mm yukarida)"),
            taban_en_ust_y_mm=round(float(max(HB[kat_idx[c]][:, 4].max() for c in KAT if c != "etek (kabuk)")), 1),
            sure_s=round(time.time() - ts, 1))
        for c, b in sorted(kol_t[taraf]["en_kucuk_aralikta"].items()):
            print("  kol %s <-> %-20s %.1f mm kol %s %s / %s" % (taraf, c, b["bosluk_mm"], b["kol_poz"], b["parca"], b["hedef"]))
        print("kol %s x taban: %d alt oge (+%d ince), %d tam olcum, aralikta cakisan alt poz %d, kol en alt y %.0f %.0fs" % (
            taraf, len(alt0), len(yeni), len(olcum), kol_t[taraf]["cakisan_alt_poz_aralikta"], kol_t[taraf]["kol_en_alt"]["y_mm"],
            time.time() - ts), flush=True)
        gc.collect()

    # ------------------------------------------------------------ (c) kafa x taban (sinir kutusu)
    kafa_t = None
    if "kafa" in MODUL:
        T = MODUL["kafa"]["T"]
        import kafa_parcalar as KPm2
        y_min = (1e9, None)
        for p in aktif(MODUL["kafa"]):
            if p["grup"] == "Govde":
                if p["gbb"].YMin < y_min[0]:
                    y_min = (p["gbb"].YMin, (p["ad"], None))
                continue
            for a_ in KAFA_KABA[0]:
                for b_ in KAFA_KABA[1]:
                    M = T.multiply(KPm2.grup_yer(p["grup"], float(a_), float(b_)).toMatrix()).multiply(T.inverse())
                    y = float(kutu_siki(p, np_m(M))[1])
                    if y < y_min[0]:
                        y_min = (y, (p["ad"], [a_, b_]))
        ust = float(max(TBB[:, 4].max(), max((bb6(p["gbb"])[4] for p in gost), default=-1e9)))
        bos = y_min[0] - ust
        kafa_t = dict(kafa_en_alt_y_mm=round(y_min[0], 1), kafa_en_alt_parca=y_min[1][0], kafa_en_alt_poz=y_min[1][1],
                      taban_en_ust_y_mm=round(ust, 1), kutu_bosluk_mm=round(bos, 1), olculdu=False, gerekli=bos < LIM_K,
                      not_=("kafanin tum pan x tilt pozlarindaki (pan -180...165, tilt -25...40, 15 derece) siki kutularinin en alti "
                            "tabanin en ustunden %.0f mm yukarida (> LIM_K = %.0f mm): kafa x taban olculmedi, carpisma olanaksiz" % (bos, LIM_K))
                      if bos >= LIM_K else "kafa tabana LIM_K'dan yakin: olcum gerekli (bu bolumde yapilmadi)")
        print("kafa x taban: kafa en alt y %.0f, taban en ust y %.0f, kutu boslugu %.0f mm" % (y_min[0], ust, bos), flush=True)

    toplam_kol = sum(k["cakisan_alt_poz_aralikta"] + k["cakisan_alt_poz_aralik_disi"] for k in kol_t.values())
    return dict(statik=statik_t, kol=kol_t, kafa=kafa_t,
                toplam=dict(cakisma=toplam_kol, eklem_araliginda=sum(k["cakisan_alt_poz_aralikta"] for k in kol_t.values()),
                            statik_cakisma=sum(len(v["cakisma"]) for v in statik_t.values()),
                            not_="kol x taban cakisan alt pozlari; statik cakismalar ev_pozu_cakisma'da da sayilir (toplama bir kez girer)"),
                kategoriler=KAT, hedef_sayisi=len(hedef), yakin_mm=YAKIN,
                not_="kol pozu = (one-arka, yana, dirsek, bilek); aralik disi halka omuz -60 / 150, yana -10. Hedef: taban parcalari "
                     "(kablo yolu semalari haric), ana anahtar dugmesi gosterimi, kabuk etek parcalari. Bulunan en kucugun otesindeki "
                     "ciftler olculmedi (siki kutu boslugu alt sinir).",
                sure_s=round(time.time() - ts0, 1))


# ====================================================================== bolum kosucusu
CALISTIR = {"statik": b_statik, "omuz": b_omuz, "kol_sag": lambda: kol_tara("sag"), "kol_sol": lambda: kol_tara("sol"),
            "kolkol": kol_kol, "kafa_sabit": lambda: kafa_tara(("sabit",)), "kafa_sag": lambda: kafa_tara(("sag",)),
            "kafa_sol": lambda: kafa_tara(("sol",)), "taban": taban_tara}
YUKLEME_S = round(time.time() - t0, 1)
os.makedirs(CK.BOLUM_DIZIN, exist_ok=True)
for _b in BOLUM:
    _tb = time.time()
    _bas = datetime.datetime.now().isoformat(timespec="seconds")
    print("==== bolum %s basladi (bellek %s MB)" % (_b, bellek_mb()[1]), flush=True)
    _s = CALISTIR[_b]()
    _bm = bellek_mb()
    _k = dict(bolum=_b, kosu=os.environ.get("CARPISMA_KOSU", "elle"), baslangic=_bas,
              bitis=datetime.datetime.now().isoformat(timespec="seconds"), sure_s=round(time.time() - _tb, 1),
              yukleme_s=YUKLEME_S, tepe_bellek_mb=_bm[0], tepe_sayfa_mb=_bm[2], ayni_surec=BOLUM, pid=os.getpid(),
              moduller=[a for a in KONTROL if a in GEREK], kaynak=CK.kaynak_ozeti(), sonuc=_s)
    json.dump(_k, open(CK.bolum_dosyasi(_b + ("-kisa" if KISA else "")), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("==== bolum %s bitti: %.0f s, tepe bellek %s MB" % (_b, _k["sure_s"], _bm[0]), flush=True)
    del _s
    gc.collect()
if len(BOLUM) == len(BOLUMLER):
    CK.birlestir()
print("bitti %.1fs" % (time.time() - t0), flush=True)
