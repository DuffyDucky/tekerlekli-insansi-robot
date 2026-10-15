# Ana montaj: GUI kurulumu + gorseller + hareket kareleri (FreeCAD GUI icinde calisir)
# FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>      (ana_montaj.py'den SONRA calistir)
# 1) Betikle kaydedilen dosyada gizli gelen montaj/gruplar/parcalari gorunur yapar, renkleri verir, eklemlere gorunum
#    nesnesi (ViewProviderJoint) kurar, "Kollari_oynat" simulasyonunu (Create Simulation nesneleri) ekler ve dosyayi
#    GUI'den yeniden kaydeder: boylece Duffy dosyayi actiginda eklemler gorunur, simulasyon oynatilabilir.
# 2) On, yan, izometrik gorunumler -> gorsel/
# 3) Simulasyonun cozucu karelerinden iki kolun ve kafanin birlikte hareketi (omuz + dirsek + bilek + pan + tilt) -> %TEMP%/robot-montaj-kare/
#    (GIF montaj_rapor.py'de)
# 4) Poz gorselleri: gruplar beklenen poza dogrudan yerlestirilir (recompute yok), dosya kaydedilmez.
import os, sys, math, tempfile
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore
from pivy import coin  # noqa  getCameraNode icin

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:
    sys.path.insert(0, os.path.dirname(HERE))
import arayuz as A          # eklem sinirlari + kafa-kol yasak kutusu (animasyon kontrolu)
Y0 = float(A.OMUZ["yana_aralik"][0])      # omuz yana acma yazilim alt siniri (3 derece, duzeltme plani C1)
OUT = os.path.join(HERE, "gorsel")
KARE = os.path.join(tempfile.gettempdir(), "robot-montaj-kare")      # OneDrive disi
os.makedirs(OUT, exist_ok=True)
os.makedirs(KARE, exist_ok=True)
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22),
        "siyah": (0.13, 0.13, 0.14), "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22),
        "kabuk": (0.85, 0.87, 0.90), "gri": (0.6, 0.6, 0.6)}
# Kollari_oynat simulasyonu (radyan, sure 8 s). Sinirlar icinde: one-arka -34...+103 derece, yana Y0 (3)...69 derece
# (yazilim alt siniri arayuz.OMUZ, 14 Ekim 2026; eskiden 0'dan basliyordu), dirsek 0...103 derece (sinir 0...105), bilek -69...+69 derece (sinir +-90).
# Sag ve sol kol zit fazda one-arka sallanir, ikisi birlikte one kalkip yana acilir; sag dirsek 4 s'de iki kez bukulur,
# sol dirsek 8 s'de bir kez; bilekler zit yonde doner. Kafa pan -46...+46 derece (sinir +-90) saga sola bakar, tilt
# -14...+14 derece (sinir -25...30) iki kez basini egip kaldirir. Tekerler (sinirsiz) 8 s'de bir tur ileri yuvarlanir.
# Her formul t = 0'da 0 (ev pozundan baslar); yana acma t = 0'da Y0 (sinir ici en alt konum). animasyon_kontrol() her karede
# sinirlari ve kafa-kol yasak kutusunu (arayuz.KAFA_KOL_YASAK) denetler; ihlalde betik durur.
SURE, ADIM = 8.0, 0.05
FORMUL = {
    "OmuzSag_OneArka": "0.75*sin(2*pi*time/4) + 0.6*(1 - cos(2*pi*time/8))",
    "OmuzSol_OneArka": "-0.75*sin(2*pi*time/4) + 0.6*(1 - cos(2*pi*time/8))",
    "OmuzSag_Yana": "%.6f + %.6f*(1 - cos(2*pi*time/8))" % (math.radians(Y0), (1.2 - math.radians(Y0)) / 2),   # Y0 ... 1,2 rad
    "OmuzSol_Yana": "%.6f + %.6f*(1 - cos(2*pi*time/8))" % (math.radians(Y0), (1.2 - math.radians(Y0)) / 2),
    "DirsekSag_Dirsek": "0.9*(1 - cos(2*pi*time/4))",
    "DirsekSol_Dirsek": "0.9*(1 - cos(2*pi*time/8))",
    "DirsekSag_Bilek": "1.2*sin(2*pi*time/8)",
    "DirsekSol_Bilek": "-1.2*sin(2*pi*time/8)",
    "Kafa_Pan": "0.8*sin(2*pi*time/8)",
    "Kafa_Tilt": "0.25*sin(2*pi*time/4)",
    "Taban_TekerOnSag": "2*pi*time/8", "Taban_TekerOnSol": "2*pi*time/8",
    "Taban_TekerArkaSag": "2*pi*time/8", "Taban_TekerArkaSol": "2*pi*time/8",
}
KOLON = ("OmuzSag_OneArka", "OmuzSag_Yana", "DirsekSag_Dirsek", "DirsekSag_Bilek",
         "OmuzSol_OneArka", "OmuzSol_Yana", "DirsekSol_Dirsek", "DirsekSol_Bilek", "Kafa_Pan", "Kafa_Tilt")
# poz gorselleri: (dosya, {modul: {eklem anahtari: derece}}, kamera, aciklama)
POZ_GORSEL = [
    ("montaj-poz-selam.png", {"omuz_sag": dict(one_arka=20.0, yana=100.0), "dirsek_sag": dict(dirsek=95.0, bilek=-60.0),
                              "omuz_sol": dict(one_arka=10.0, yana=10.0), "dirsek_sol": dict(dirsek=30.0, bilek=0.0),
                              "kafa": dict(pan=30.0, tilt=-10.0)},
     ((0.35, 0.25, 1.0), 1000, (0, 820, 0))),
    ("montaj-poz-one.png", {"omuz_sag": dict(one_arka=90.0, yana=Y0), "dirsek_sag": dict(dirsek=60.0, bilek=45.0),
                            "omuz_sol": dict(one_arka=90.0, yana=Y0), "dirsek_sol": dict(dirsek=60.0, bilek=45.0),
                            "kafa": dict(pan=0.0, tilt=25.0)},
     ((0.8, 0.45, 1.0), 900, (0, 860, 120))),
    ("montaj-poz-kafa.png", {"kafa": dict(pan=45.0, tilt=20.0), "omuz_sag": dict(one_arka=45.0, yana=20.0),
                             "dirsek_sag": dict(dirsek=60.0, bilek=0.0)},
     ((0.7, 0.35, 1.0), 560, (0, 1090, 30))),
]


LOG = os.path.join(KARE, "montaj_gorsel.log")
open(LOG, "w").close()


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


def formul_deger(f, t):
    return eval(f.replace("time", "(%r)" % t), {"sin": math.sin, "cos": math.cos, "pi": math.pi})


def animasyon_kontrol():
    """Kollari_oynat: her karede (ADIM) her eklem yazilim sinirinda mi, hicbir kol kafa-kol yasak kutusuna giriyor mu (arayuz)."""
    sinir = dict(OneArka=A.OMUZ["one_arka_aralik"], Yana=A.OMUZ["yana_aralik"], Dirsek=A.DIRSEK["aralik"],
                 Bilek=A.DIRSEK["bilek_aralik"], Pan=A.KAFA["pan_aralik"], Tilt=A.KAFA["tilt_aralik"])
    Y = A.KAFA_KOL_YASAK
    hata, uc = [], {}
    n = int(round(SURE / ADIM))
    for i in range(n + 1):
        t = i * ADIM
        d = {ad: math.degrees(formul_deger(f, t)) for ad, f in FORMUL.items() if not ad.startswith("Taban_")}
        for ad, a in d.items():
            s = sinir[ad.split("_")[1]]
            lo, hi = uc.get(ad, (a, a))
            uc[ad] = (min(lo, a), max(hi, a))
            if not s[0] - 1e-9 <= a <= s[1] + 1e-9:
                hata.append("t=%.2f %s %.2f sinir disi %s" % (t, ad, a, s))
        for taraf, kutu in (("Sag", Y["kutu_sag_kol"]), ("Sol", Y["kutu_sol_kol"])):
            kol = dict(one_arka=d["Omuz%s_OneArka" % taraf], yana=d["Omuz%s_Yana" % taraf],
                       dirsek=d["Dirsek%s_Dirsek" % taraf], bilek=d["Dirsek%s_Bilek" % taraf])
            kosul = all(Y["kol_kosulu"][k][0] <= v <= Y["kol_kosulu"][k][1] for k, v in kol.items())
            if kosul and kutu["pan"][0] <= d["Kafa_Pan"] <= kutu["pan"][1] and kutu["tilt"][0] <= d["Kafa_Tilt"] <= kutu["tilt"][1]:
                hata.append("t=%.2f %s kol + kafa yasak kutuda" % (t, taraf))
    return dict(kare=n + 1, uc={k: (round(v[0], 2), round(v[1], 2)) for k, v in uc.items()}, hata=hata)


ANIM = animasyon_kontrol()
log("animasyon kontrolu:", ANIM["kare"], "kare; uclar", ANIM["uc"], "; ihlal", len(ANIM["hata"]), ANIM["hata"][:5])
if ANIM["hata"]:
    raise SystemExit("Kollari_oynat sinir / yasak kutu ihlali: %s" % ANIM["hata"][:3])

doc = App.openDocument(os.path.join(HERE, "robot-montaj.FCStd"))


def kamera(v, eye, h, merkez):
    """Ortografik kamera: eye yonunden bakar, Y yukari, merkez noktasina odaklanir, h gorunen yukseklik (mm)."""
    z = V(*eye).normalize()
    up = V(0, 1, 0) if abs(z.y) < 0.99 else V(0, 0, -1)
    x = up.cross(z).normalize()
    y = z.cross(x)
    # setCameraOrientation animasyonlu (yon bir sonraki kareye kayiyor): yon dogrudan kamera dugumune yazilir
    q = App.Rotation(x, y, z, "ZYX").Q
    cam = v.getCameraNode()
    cam.orientation.setValue(coin.SbRotation(q[0], q[1], q[2], q[3]))
    v.fitAll()
    pos = V(*merkez) + z * cam.focalDistance.getValue()
    cam.position.setValue(pos.x, pos.y, pos.z)
    cam.height.setValue(h)


def kaydet(v, ad, w=1400, h=1000):
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, ad), w, h, "White")


def go():
    gd = Gui.getDocument(doc.Name)
    asm = doc.getObject("Assembly")
    import JointObject, UtilsAssembly
    import CommandCreateSimulation as CS
    # --- 1) gorunurluk, renk, eklem gorunum nesneleri
    for o in doc.Objects:
        if o.TypeId in ("Assembly::AssemblyObject", "App::Part", "Part::Feature"):
            gd.getObject(o.Name).Visibility = True
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    for o in feats:
        gd.getObject(o.Name).ShapeColor = RENK.get(o.Renk, RENK["gri"])
    eklemler = []
    for o in doc.Objects:
        if o.TypeId == "App::FeaturePython" and hasattr(o, "Proxy"):
            if isinstance(o.Proxy, JointObject.GroundedJoint):
                JointObject.ViewProviderGroundedJoint(o.ViewObject).attach(o.ViewObject)
            elif isinstance(o.Proxy, JointObject.Joint):
                JointObject.ViewProviderJoint(o.ViewObject).attach(o.ViewObject)
                o.ViewObject.Proxy.redrawJointPlacements(o)
                eklemler.append(o)
            o.ViewObject.Visibility = True
    # --- simulasyon (Create Simulation nesneleri, GUI'de cift tik + Play ile oynar)
    sg = UtilsAssembly.getSimulationGroup(asm)
    for s in list(sg.Group):          # yeniden calistirmada eski simulasyon ve hareketleri (montajin cocuklari) silinir
        doc.removeObject(s.Name)
    for o in [o for o in doc.Objects if o.Name.startswith("Hareket_")]:
        doc.removeObject(o.Name)
    sim = sg.newObject("App::FeaturePython", "Kollari_oynat")
    CS.Simulation(sim)
    CS.ViewProviderSimulation(sim.ViewObject)
    sim.Label = "Kollari_oynat"
    sim.bTimeEnd = SURE
    sim.cTimeStepOutput = ADIM
    for ad, f in FORMUL.items():
        j = doc.getObject(ad)
        if j is None:
            log("eklem yok, hareket atlandi:", ad)
            continue
        m = asm.newObject("App::FeaturePython", "Hareket_" + ad)
        CS.Motion(m, "Angular", j, f)
        CS.ViewProviderMotion(m.ViewObject)
        m.Label = "Hareket " + j.Label
        sim.Group = sim.Group + [m]
    for gp in [o for o in asm.Group if o.TypeId == "App::Part"]:
        gp.Placement = App.Placement()
    Gui.updateGui()
    doc.save()          # GUI'den kayit: eklem/simulasyon gorunum nesneleri ve gorunurluk dosyaya yazilir
    log("GUI kurulumu kaydedildi: eklem", len(eklemler), "simulasyon", sim.Name, "hareket", len(sim.Group))

    v = gd.activeView()
    # --- 2) gorunumler (eklem isaretleri gizli)
    for j in eklemler:
        j.ViewObject.Visibility = False
    Gui.updateGui()
    kamera(v, (0.85, 0.55, 1.0), 1000, (0, 640, 0))
    kaydet(v, "montaj-izometrik.png", 1000, 1300)
    kamera(v, (0, 0, 1), 790, (0, 635, 0))
    kaydet(v, "montaj-on.png", 800, 1300)
    kamera(v, (1, 0, 0), 790, (0, 635, 0))
    kaydet(v, "montaj-yan.png", 800, 1300)
    kamera(v, (0.7, 0.35, 1.0), 520, (0, 1080, 20))
    kaydet(v, "montaj-kafa.png", 1200, 1000)
    kamera(v, (0.6, 0.35, 1.0), 360, (0, 900, 20))
    kaydet(v, "montaj-omuzlar.png", 1400, 900)
    kamera(v, (0.9, 0.3, 0.6), 420, (150, 790, 0))
    kaydet(v, "montaj-dirsek.png", 1200, 1000)
    # taban yakindan: etek arkasi (acil stop, ana anahtar) ve tekerler; etek parcalari gizlenip ic yerlesim ayrica
    kamera(v, (0.75, 0.55, -1.0), 700, (0, 190, 0))
    kaydet(v, "montaj-taban.png", 1300, 900)
    etek = [o for o in feats if o.Name.startswith("Kabuk_") and o.Label.startswith("Etek")]
    for o in etek:
        gd.getObject(o.Name).Visibility = False
    kamera(v, (0.8, 0.9, 1.0), 640, (0, 170, 0))
    kaydet(v, "montaj-taban-ic.png", 1300, 900)
    for o in etek:
        gd.getObject(o.Name).Visibility = True
    Gui.updateGui()

    # --- 4) poz gorselleri (gruplar beklenen poza; recompute yok)
    try:
        sys.path.insert(0, HERE)
        import moduller as MD
        import omuz_parcalar as OP
        import dirsek_parcalar as DP
        import kafa_parcalar as KP
        for dosya, poz, kam in POZ_GORSEL:
            for gp in [o for o in asm.Group if o.TypeId == "App::Part"]:
                gp.Placement = App.Placement()
            for taraf in ("sag", "sol"):
                o = poz.get("omuz_" + taraf, {})
                dd = poz.get("dirsek_" + taraf, {})
                phi, th = o.get("one_arka", 0.0), o.get("yana", Y0)      # pozda verilmeyen kol: asagida, yana alt sinirda
                yer = {"Omuz%s_Gobek": ("omuz_" + taraf, OP.Pp(phi)), "Omuz%s_Kol": ("omuz_" + taraf, OP.Pp(phi).multiply(OP.Pr(th)))}
                for g in ("UstKol", "OnKol", "El"):
                    yer["Dirsek%s_" + g] = ("dirsek_" + taraf, DP.grup_yer(g, phi, th, dd.get("dirsek", 0.0), dd.get("bilek", 0.0)))
                for ad, (mod, pl) in yer.items():
                    gp = doc.getObject(ad % taraf.capitalize())
                    if gp is not None:
                        gp.Placement = MD.global_poz(mod, pl)
            k = poz.get("kafa", {})
            for ad, g in (("Kafa_Boyun", "Pan"), ("Kafa_Bas", "Kafa")):
                gp = doc.getObject(ad)
                if gp is not None:
                    gp.Placement = MD.global_poz("kafa", KP.grup_yer(g, k.get("pan", 0.0), k.get("tilt", 0.0)))
            Gui.updateGui()
            kamera(v, *kam)
            kaydet(v, dosya, 1200, 1100)
            log("poz gorseli", dosya)
        for gp in [o for o in asm.Group if o.TypeId == "App::Part"]:
            gp.Placement = App.Placement()
        Gui.updateGui()
    except Exception:
        import traceback
        log("poz gorseli hatasi", traceback.format_exc())

    # --- 3) hareket: cozucunun simulasyon kareleri (iki kol birlikte)
    asm.generateSimulation(sim)
    n = asm.numberOfFrames()
    for f in os.listdir(KARE):
        if f.endswith(".png") or f == "pozlar.txt":
            os.remove(os.path.join(KARE, f))
    kamera(v, (0.75, 0.4, 1.0), 1340, (0, 650, 40))      # tam robot (tabanli)
    satir = []
    k_out = 0
    for k in range(1, n, 2):
        asm.updateForFrame(k)
        Gui.updateGui()
        v.saveImage(os.path.join(KARE, "k%03d.png" % k_out), 900, 640, "White")
        t = (k - 1) * ADIM
        ac = [math.degrees(formul_deger(FORMUL[a], t)) if a in FORMUL else 0.0 for a in KOLON]
        satir.append(("%.2f" + " %.1f" * len(ac)) % ((t,) + tuple(ac)))
        k_out += 1
    with open(os.path.join(KARE, "pozlar.txt"), "w") as fh:
        fh.write("\n".join(satir) + "\n")
    log("hareket karesi", k_out, "->", KARE)
    App.closeDocument(doc.Name)       # kareler yerlesimi degistirdi; kaydetmeden kapat
    Gui.getMainWindow().close()


def guvenli():
    try:
        go()
    except Exception:
        import traceback
        log(traceback.format_exc())
        Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
