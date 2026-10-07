# Ana montajin modul tanimlari (FreeCAD 1.1). ana_montaj.py ve eklem_dogrulama.py bunu kullanir.
#
# Yeni modul eklemek (kabuk, dirsek, kafa, taban):
#   1. Yerlesimini arayuz.MODULLER'e yaz (konum + ayna). Burada hicbir yerlesim sayisi yazilmaz.
#   2. Asagida bir yukleyici yaz ve MODUL_YUKLE'ye, adini SIRA listesine ekle.
#   Yukleyici dict dondurur (koordinatlar modulun YEREL koordinatinda; aynalama ve tasima burada yapilir):
#     parcalar : [dict(ad, grup, shape, kutle, merkez, tur, malzeme, kod, renk, not_, patlat, indeks)]
#     gruplar  : [(grup adi, etiket)]; ilk grup modulun sabit govdesi (baglanti bu gruba kurulur)
#     baglanti : None = zemine sabit (grounded) | dict(modul, grup, nokta (yerel), ref) -> Fixed eklem
#                (ref = ust modulde eklem referansi olarak kullanilacak parca adi oneki)
#     eklemler : [dict(anahtar, ad, etiket, ebeveyn, cocuk, cerceve (yerel App.Placement; Z = donme ekseni),
#                      sinir=(min, max) derece)]
#     beklenen : None | f(poz: {anahtar: derece}, grup) -> yerel App.Placement (modulun kendi kinematigi)
#     haric    : [parca adi oneki], haric_neden
import os, sys
import FreeCAD as App

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (UST, os.path.join(UST, "iskelet"), os.path.join(UST, "omuz")):
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


MODUL_YUKLE = {"iskelet": yukle_iskelet, "omuz_sag": yukle_omuz, "omuz_sol": yukle_omuz}
SIRA = ["iskelet", "omuz_sag", "omuz_sol"]       # sonra: "taban", "kabuk", "kafa", "dirsek_sag", "dirsek_sol"


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
