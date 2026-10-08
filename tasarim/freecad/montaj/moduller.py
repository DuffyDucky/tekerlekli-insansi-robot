# Ana montajin modul tanimlari (FreeCAD 1.1). ana_montaj.py ve eklem_dogrulama.py bunu kullanir.
#
# Yeni modul eklemek (iskelet, omuz, kabuk, dirsek, kafa ve taban ekli):
#   1. Yerlesimini arayuz.MODULLER'e yaz (konum + ayna). Burada hicbir yerlesim sayisi yazilmaz.
#   2. Asagida bir yukleyici yaz ve MODUL_YUKLE'ye, adini SIRA listesine ekle.
#   Yukleyici dict dondurur (koordinatlar modulun YEREL koordinatinda; aynalama ve tasima burada yapilir):
#     parcalar : [dict(ad, grup, shape, kutle, merkez, tur, malzeme, kod, renk, not_, patlat, indeks)]
#     gruplar  : [(grup adi, etiket)]; ilk grup modulun sabit govdesi (baglanti bu gruba kurulur)
#     baglanti : None = zemine sabit (grounded) | dict(modul, grup, nokta (yerel), ref) -> Fixed eklem
#                (ref = ust modulde eklem referansi olarak kullanilacak parca adi oneki)
#     eklemler : [dict(anahtar, ad, etiket, ebeveyn, cocuk, cerceve (yerel App.Placement; Z = donme ekseni),
#                      sinir=(min, max) derece | None = sinirsiz (teker))]
#     beklenen : None | f(poz: {anahtar: derece}, grup) -> yerel App.Placement (modulun kendi kinematigi)
#     haric    : [parca adi oneki], haric_neden
#   Istege bagli: ust_kol (zincir: bu modul baska bir hareketli modulun grubuna bagli; beklenen poz o modulun eklem
#   acilarini da alir, ornek dirsek -> omuz), analiz (analiz JSON'unun ../ altindaki yolu; yoksa <modul>/<modul>-analiz.json)
import os, sys
import FreeCAD as App

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (UST, os.path.join(UST, "iskelet"), os.path.join(UST, "omuz"), os.path.join(UST, "kabuk"), os.path.join(UST, "dirsek"),
           os.path.join(UST, "kafa"), os.path.join(UST, "taban")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import arayuz as A


# ====================================================================== yukleyiciler
def _parca(p, k):
    return dict(ad=p["ad"], grup=p["grup"], shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"], tur=p["tur"],
                malzeme=p["malzeme"], kod=p["kod"], renk=p["renk"], not_=p["not_"], patlat=p["patlat"], indeks=k)


def yukle_iskelet():
    import iskelet_parcalar as I
    return dict(parcalar=[dict(_parca(p, k), grup="Iskelet", alt_grup=p["grup"]) for k, p in enumerate(I.P)],
                gruplar=[("Iskelet", "Iskelet (sabit)")], baglanti=None, eklemler=[], beklenen=None,
                haric=[], haric_neden="")


# omuz-montaj.FCStd'deki eklem adlari -> poz anahtari (eksenler ve sinirlar dosyadan okunur, burada sayi yok)
OMUZ_EKLEM = {"OmuzOneArka": ("one_arka", "one-arka (S1)"), "OmuzYanaAcma": ("yana", "yana acma (S2)")}
_OMUZ_EKLEM_CACHE = []


def omuz_eklemleri():
    """Omuz eklemlerini omuz_montaj.py'nin kaydettigi dosyadan okur: eksen cercevesi (Placement1), gruplar, sinirlar."""
    if _OMUZ_EKLEM_CACHE:
        return _OMUZ_EKLEM_CACHE
    onceki = App.ActiveDocument
    d = App.openDocument(os.path.join(UST, "omuz", "omuz-montaj.FCStd"))
    for j in d.Objects:
        if j.Name in OMUZ_EKLEM:
            anahtar, ad = OMUZ_EKLEM[j.Name]
            p1, p2 = App.Placement(j.Placement1), App.Placement(j.Placement2)
            assert p1.isSame(p2, 1e-9), "omuz eklem cerceveleri ev pozunda farkli: %s" % j.Name
            _OMUZ_EKLEM_CACHE.append(dict(
                anahtar=anahtar, ad=ad, ebeveyn=j.Reference1[0].Name, cocuk=j.Reference2[0].Name, cerceve=p1,
                sinir=(float(j.AngleMin), float(j.AngleMax)), sinir_acik=(bool(j.EnableAngleMin), bool(j.EnableAngleMax)),
                kaynak="omuz/omuz-montaj.FCStd: %s (%s)" % (j.Name, j.Label)))
    App.closeDocument(d.Name)
    if onceki is not None:
        App.setActiveDocument(onceki.Name)
    _OMUZ_EKLEM_CACHE.sort(key=lambda e: list(OMUZ_EKLEM.values()).index((e["anahtar"], e["ad"])))
    return _OMUZ_EKLEM_CACHE


def yukle_omuz():
    import omuz_parcalar as O

    def beklenen(poz, g):
        phi, th = poz.get("one_arka", 0.0), poz.get("yana", 0.0)
        if g == "Gobek":
            return O.Pp(phi)
        if g == "Kol":
            return O.Pp(phi).multiply(O.Pr(th))
        return App.Placement()

    return dict(parcalar=[_parca(p, k) for k, p in enumerate(O.P)],
                gruplar=[("Govde", "govde (sabit)"), ("Gobek", "omuz gobegi (one-arka ile doner)"),
                         ("Kol", "ust kol (yana acma ile doner)")],
                baglanti=dict(modul="iskelet", grup="Iskelet", ref="Omuz traversi",
                              nokta=(sum(A.OMUZ_YUVA_X) / 2, 0.0, 0.0),
                              aciklama="omuz yuvasi travers ucunda, 4x M6 + cekic somun (arayuz.OMUZ_YUVA_X)"),
                eklemler=[dict(e) for e in omuz_eklemleri()], beklenen=beklenen,
                haric=["Omuz traversi", "Govde kabugu yan yuzu (referans)"],
                haric_neden="travers iskeletin parcasi (iki kez sayilmaz); kabuk duvari kabuk modulunun yer tutucusu")


def yukle_kabuk():
    import kabuk_parcalar as K
    return dict(parcalar=[dict(_parca(p, k), grup="Kabuk", alt_grup=p["grup"]) for k, p in enumerate(K.P)],
                gruplar=[("Kabuk", "Kabuk (sabit)")],
                baglanti=dict(modul="iskelet", grup="Iskelet", ref="Govde diregi", nokta=(0.0, 600.0, 0.0),
                              aciklama="govde braketleri direk yan kanallarina (4 braket x 2 M6), etek braketleri uzun ray ust "
                                       "kanallarina (6 x M6), cekic somunla (arayuz.KABUK_GOVDE_BRAKET / KABUK_ETEK_BRAKET)"),
                eklemler=[], beklenen=None, haric=[], haric_neden="")


# dirsek-montaj.FCStd'deki eklem adlari -> poz anahtari (eksen cercevesi ve sinirlar dosyadan; dirsek_montaj.py arayuz.DIRSEK'ten kurar)
DIRSEK_EKLEM = {"Dirsek": ("dirsek", "dirsek (MG996R)"), "Bilek": ("bilek", "bilek (MG996R)")}
_DIRSEK_EKLEM_CACHE = []


def dirsek_eklemleri():
    if _DIRSEK_EKLEM_CACHE:
        return _DIRSEK_EKLEM_CACHE
    onceki = App.ActiveDocument
    d = App.openDocument(os.path.join(UST, "dirsek", "dirsek-montaj.FCStd"))
    for j in d.Objects:
        if j.Name in DIRSEK_EKLEM and hasattr(j, "JointType"):
            anahtar, ad = DIRSEK_EKLEM[j.Name]
            p1, p2 = App.Placement(j.Placement1), App.Placement(j.Placement2)
            assert p1.isSame(p2, 1e-9), "dirsek eklem cerceveleri ev pozunda farkli: %s" % j.Name
            _DIRSEK_EKLEM_CACHE.append(dict(
                anahtar=anahtar, ad=ad, ebeveyn=j.Reference1[0].Name, cocuk=j.Reference2[0].Name, cerceve=p1,
                sinir=(float(j.AngleMin), float(j.AngleMax)), sinir_acik=(bool(j.EnableAngleMin), bool(j.EnableAngleMax)),
                kaynak="dirsek/dirsek-montaj.FCStd: %s (%s)" % (j.Name, j.Label)))
    App.closeDocument(d.Name)
    if onceki is not None:
        App.setActiveDocument(onceki.Name)
    _DIRSEK_EKLEM_CACHE.sort(key=lambda e: list(DIRSEK_EKLEM.values()).index((e["anahtar"], e["ad"])))
    # arayuz.DIRSEK ile tutarli mi (eksen noktasi, yonu, sinir)
    D = A.DIRSEK
    for e, (n, y, s) in zip(_DIRSEK_EKLEM_CACHE, ((D["eksen_nokta"], D["eksen_yon"], D["aralik"]),
                                                  (D["bilek_nokta"], D["bilek_yon"], D["bilek_aralik"]))):
        ax = e["cerceve"].Rotation.multVec(V(0, 0, 1))
        assert (e["cerceve"].Base - V(*n)).Length < 1e-9 and (ax - V(*y)).Length < 1e-9 and tuple(e["sinir"]) == tuple(s), e["anahtar"]
    return _DIRSEK_EKLEM_CACHE


def yukle_dirsek(taraf):
    def yukle():
        import dirsek_parcalar as DP

        def beklenen(poz, g):
            return DP.grup_yer(g, poz.get("one_arka", 0.0), poz.get("yana", 0.0), poz.get("dirsek", 0.0), poz.get("bilek", 0.0))

        return dict(parcalar=[_parca(p, k) for k, p in enumerate(DP.P)],
                    gruplar=[("UstKol", "dirsek catali (ust kola sabit)"), ("OnKol", "on kol (dirsek ile doner)"),
                             ("El", "el (bilek ile doner)")],
                    baglanti=dict(modul="omuz_" + taraf, grup="Kol", ref="Ust kol tupu",
                                  nokta=(A.DIRSEK["tup_x"], A.DIRSEK["tup_uc_y"], A.DIRSEK["tup_z"]),
                                  aciklama="dirsek catali ust kol tupunun ucuna: pim + yarikli sikma bilezigi, 2x M3 (arayuz.DIRSEK)"),
                    eklemler=[dict(e) for e in dirsek_eklemleri()], beklenen=beklenen, ust_kol="omuz_" + taraf,
                    analiz=os.path.join("dirsek", "dirsek-analiz.json"), haric=[], haric_neden="")
    return yukle


# kafa-montaj.FCStd'deki eklem etiketinin ilk sozcugu -> poz anahtari (dosyada pan eklemi "Pan001": "Pan" grubun adi);
# kafa_parcalar gruplari ana montajda yeniden adlanir (eklem adlari
# Kafa_Pan / Kafa_Tilt, grup adlari Kafa_Govde / Kafa_Boyun / Kafa_Bas ile cakismasin)
KAFA_EKLEM = {"Pan": ("pan", "pan (MG996R)"), "Tilt": ("tilt", "tilt (MG996R)")}
KAFA_GRUP = {"Govde": "Govde", "Pan": "Boyun", "Kafa": "Bas"}
_KAFA_EKLEM_CACHE = []


def kafa_eklemleri():
    if _KAFA_EKLEM_CACHE:
        return _KAFA_EKLEM_CACHE
    onceki = App.ActiveDocument
    d = App.openDocument(os.path.join(UST, "kafa", "kafa-montaj.FCStd"))
    for j in d.Objects:
        if hasattr(j, "JointType") and j.Label.split(" ")[0] in KAFA_EKLEM:
            anahtar, ad = KAFA_EKLEM[j.Label.split(" ")[0]]
            p1, p2 = App.Placement(j.Placement1), App.Placement(j.Placement2)
            assert p1.isSame(p2, 1e-9), "kafa eklem cerceveleri ev pozunda farkli: %s" % j.Name
            _KAFA_EKLEM_CACHE.append(dict(
                anahtar=anahtar, ad=ad, ebeveyn=KAFA_GRUP[j.Reference1[0].Name], cocuk=KAFA_GRUP[j.Reference2[0].Name], cerceve=p1,
                sinir=(float(j.AngleMin), float(j.AngleMax)), sinir_acik=(bool(j.EnableAngleMin), bool(j.EnableAngleMax)),
                kaynak="kafa/kafa-montaj.FCStd: %s (%s)" % (j.Name, j.Label)))
    App.closeDocument(d.Name)
    if onceki is not None:
        App.setActiveDocument(onceki.Name)
    _KAFA_EKLEM_CACHE.sort(key=lambda e: list(KAFA_EKLEM.values()).index((e["anahtar"], e["ad"])))
    K = A.KAFA      # arayuz.KAFA ile tutarli mi (eksen noktasi, yonu, sinir); assert yerine raise (betik -O ile kosabilir)
    if [e["anahtar"] for e in _KAFA_EKLEM_CACHE] != ["pan", "tilt"]:
        raise RuntimeError("kafa-montaj.FCStd: Pan/Tilt eklemi eksik: %s" % [e["anahtar"] for e in _KAFA_EKLEM_CACHE])
    for e, (n, y, s) in zip(_KAFA_EKLEM_CACHE, ((K["pan_nokta"], K["pan_yon"], K["pan_aralik"]),
                                                (K["tilt_nokta"], K["tilt_yon"], K["tilt_aralik"]))):
        ax = e["cerceve"].Rotation.multVec(V(0, 0, 1))
        if not ((e["cerceve"].Base - V(*n)).Length < 1e-9 and (ax - V(*y)).Length < 1e-9 and tuple(e["sinir"]) == tuple(s)):
            raise RuntimeError("kafa eklemi arayuz.KAFA ile tutarsiz: %s" % e["anahtar"])
    return _KAFA_EKLEM_CACHE


def yukle_kafa():
    import kafa_parcalar as KP
    geri = {v: k for k, v in KAFA_GRUP.items()}

    def beklenen(poz, g):
        return KP.grup_yer(geri.get(g, g), poz.get("pan", 0.0), poz.get("tilt", 0.0))

    return dict(parcalar=[dict(_parca(p, k), grup=KAFA_GRUP.get(p["grup"], p["grup"]), alt_grup=p["grup"]) for k, p in enumerate(KP.P)],
                gruplar=[("Govde", "Kafa govdesi: boyun plakasi + servo/rulman yuvasi + pan servosu (traverse sabit)"),
                         ("Boyun", "Kafa pan grubu: boyun mili + egme catali + tilt servosu (pan ile doner)"),
                         ("Bas", "Kafa: iskelet + kabuklar + LCD + kamera (pan x tilt ile doner)")],
                baglanti=dict(modul="iskelet", grup="Iskelet", ref="Omuz traversi", nokta=(0.0, 0.0, 0.0),
                              aciklama="boyun plakasi traversin ust kanalina 2x M6 + cekic somun (x = +-40, z = 0; arayuz.KAFA boyun_plaka)"),
                eklemler=[dict(e) for e in kafa_eklemleri()], beklenen=beklenen,
                analiz=os.path.join("kafa", "kafa-analiz.json"), haric=["Kablo demeti (gosterim)"],
                haric_neden="kablo demeti gosterimi (Referans grubu, 0 g); kafa analizinin parca sayisina da girmiyor")


# taban: govde (plakalar, motorlar, aku, guc, elektronik, sensorler; iskelete sabit) + her kosede teker grubu (teker + kaplin +
# teker civatasi ve pulu: motor milinde doner). Teker eklemleri: Revolute, sinirsiz (serbest donus), eksen motor mili (+X yonlu:
# pozitif aci = ileri yuvarlanma, tekerin alt noktasi geri gider). Eksen noktasi ve yonu taban_parcalar (X_WH, Z_WH, arayuz.AX)
# ve kaplin-motor mili baglantisinin eksen kontrolunden; taban-montaj.FCStd'de eklem yok (1. asama statik), burada kurulur.
TEKER_KOSE = (("on_sag", 1, 1), ("on_sol", -1, 1), ("arka_sag", 1, -1), ("arka_sol", -1, -1))     # (anahtar eki, sx, sz)


def teker_grup(k):
    """Grup adi: on_sag -> OnSagTeker (ana montajda Taban_OnSagTeker); eklem adi Taban_TekerOnSag ile cakismasin."""
    return "".join(x.capitalize() for x in k.split("_")) + "Teker"


def yukle_taban():
    import taban_parcalar as TP
    kose_ad = {(sx, sz): "%s %s" % (TP.SZ(sz), TP.SX(sx)) for _, sx, sz in TEKER_KOSE}     # (1, 1) -> "on sag" (parca adlarindaki)
    grup_on = {}
    for k, sx, sz in TEKER_KOSE:
        ka = kose_ad[(sx, sz)]
        for on in ("Teker 125 x 58 (%s)" % ka, "Kaplin 12 mm altigen (%s)" % ka, "Pul M4 (teker %s)" % ka, "Civata M4x16 (teker %s)" % ka):
            grup_on[on] = teker_grup(k)

    def grup(p):
        if p["grup"] == "Referans":
            return "Referans"
        return grup_on.get(p["ad"], "Govde")

    eklemler = []
    for k, sx, sz in TEKER_KOSE:
        n = V(sx * TP.X_WH, A.AX, sz * TP.Z_WH)
        eklemler.append(dict(anahtar="teker_" + k, ad="teker %s (JGB37 mili)" % k.replace("_", " "), ebeveyn="Govde",
                             cocuk=teker_grup(k), cerceve=App.Placement(n, App.Rotation(V(0, 0, 1), V(1, 0, 0))), sinir=None,
                             sinir_acik=(False, False),
                             kaynak="taban/taban_parcalar.py: teker merkezi (x = %+.0f, y = %.1f, z = %+.0f), eksen +X (motor mili)" % (
                                 n.x, n.y, n.z)))

    def beklenen(poz, g):
        for k, sx, sz in TEKER_KOSE:
            if g == teker_grup(k):
                return App.Placement(V(0, 0, 0), App.Rotation(V(1, 0, 0), poz.get("teker_" + k, 0.0)),
                                     V(sx * TP.X_WH, A.AX, sz * TP.Z_WH))
        return App.Placement()

    parcalar = []
    for k, p in enumerate(TP.P):
        q = _parca(p, k)
        q["kutle"] = p["kutle"]
        parcalar.append(dict(q, grup=grup(p), alt_grup=p["grup"]))
    return dict(parcalar=parcalar,
                gruplar=[("Govde", "Taban govdesi: plakalar + motorlar + aku + guc + elektronik + sensorler (iskelete sabit)")] +
                        [(teker_grup(k), "Teker %s (teker + kaplin, motor milinde doner)" % k.replace("_", " ")) for k, _, _ in TEKER_KOSE],
                baglanti=dict(modul="iskelet", grup="Iskelet", ref="Sase uzun rayi", nokta=(0.0, A.Y_RAIL0, 0.0),
                              aciklama="alt plaka uzun ve ara raylarin alt kanallarina 14x M6 + cekic somun (arayuz.TABAN plaka_ray_z / "
                                       "plaka_ara_x); motor braketleri plaka uzerinden uzun raylara M4 + cekic somun"),
                eklemler=eklemler, beklenen=beklenen, analiz=os.path.join("taban", "taban-analiz.json"),
                haric=["Kablo yolu", "Ana anahtar dugmesi"],
                haric_neden="kablo yolu semalari ve ana anahtar dugmesi gosterimi (Referans grubu, 0 g); taban analizinin parca sayisina "
                            "girmiyor")


MODUL_YUKLE = {"iskelet": yukle_iskelet, "omuz_sag": yukle_omuz, "omuz_sol": yukle_omuz, "kabuk": yukle_kabuk,
               "dirsek_sag": yukle_dirsek("sag"), "dirsek_sol": yukle_dirsek("sol"), "kafa": yukle_kafa, "taban": yukle_taban}
SIRA = ["iskelet", "omuz_sag", "omuz_sol", "kabuk", "dirsek_sag", "dirsek_sol", "kafa", "taban"]


# ====================================================================== global yerlesim (yalniz arayuz.MODULLER)
def on_ek(ad):
    """Nesne adi oneki: omuz_sag -> OmuzSag."""
    return "".join(s.capitalize() for s in ad.split("_"))


def taraf(ad):
    return ad.rsplit("_", 1)[1] if ad.endswith(("_sag", "_sol")) else ""


def matrisler(ad):
    """(T, aynali): T = yerel orijinin global konumuna tasima; aynali = X aynasi (x -> -x) once uygulanir."""
    (tx, ty, tz), ayna = A.modul_konum(ad)
    T = App.Matrix()
    T.move(V(tx, ty, tz))
    return T, bool(ayna)


def AYNA():
    M = App.Matrix()
    M.A11 = -1.0
    return M


def global_sekil(shape, ad):
    """Gercek geometri: aynali modulde sekil aynalanir (Placement aynalayamaz), sonra kopyalanarak tasinir."""
    T, aynali = matrisler(ad)
    s = shape.mirror(V(0, 0, 0), V(1, 0, 0)) if aynali else shape.copy()
    s.transformShape(T, True)
    return s


def global_nokta(ad, p):
    return V(*A.yerelden_globale(ad, tuple(p)))


def global_cerceve(ad, pl):
    """Eklem cercevesi (Z = donme ekseni). Aynada eksen eksenel vektor gibi doner: a' = -M a; boylece
    pozitif aci aynalanmis hareketi verir ve sinirlar ayni kalir. X ekseni M b (aci sifiri ev pozunda kalir)."""
    T, aynali = matrisler(ad)
    p = global_nokta(ad, pl.Base)
    if not aynali:
        return App.Placement(p, pl.Rotation)
    a = pl.Rotation.multVec(V(0, 0, 1))
    b = pl.Rotation.multVec(V(1, 0, 0))
    a2 = V(a.x, -a.y, -a.z)          # -M a
    b2 = V(-b.x, b.y, b.z)           # M b
    return App.Placement(p, App.Rotation(b2, a2.cross(b2), a2, "ZXY"))


def global_poz(ad, yerel_pl):
    """Yerel grup poz donusumu -> global: T R P R T^-1 (R ayna; sonuc yine kati donusum)."""
    T, aynali = matrisler(ad)
    R = AYNA() if aynali else App.Matrix()
    M = T.multiply(R).multiply(yerel_pl.toMatrix()).multiply(R).multiply(T.inverse())
    return App.Placement(M)


def yukle(ad):
    d = MODUL_YUKLE[ad]()
    d["ad"] = ad
    d["on_ek"] = on_ek(ad)
    d["taraf"] = taraf(ad)
    d["aynali"] = matrisler(ad)[1]
    for p in d["parcalar"]:
        p["haric"] = any(p["ad"].startswith(h) for h in d["haric"])
    return d
