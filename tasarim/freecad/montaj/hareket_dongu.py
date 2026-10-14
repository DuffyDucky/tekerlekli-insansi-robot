# Ana montaj: robotun hareketini FreeCAD'de sonsuz dongude oynatir (FreeCAD GUI icinde calisir).
# FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>      (montaj_gorsel.py'den SONRA: "Kollari_oynat" simulasyonu dosyada olmali)
# robot-montaj.FCStd'nin %TEMP% kopyasini acar (asil dosya degismez), simulasyonu bir kez cozer, sonra kareleri
# QTimer ile basa sararak oynatir. Belge ya da pencere kapaninca durur. Bosluk tusu: duraklat / devam.
import os, shutil, tempfile
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui

HERE = os.path.dirname(os.path.abspath(__file__))
KOPYA = os.path.join(tempfile.gettempdir(), "robot-hareket-dongu.FCStd")
LOG = os.path.join(tempfile.gettempdir(), "robot-hareket-dongu.log")
open(LOG, "w").close()


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


class Dongu:
    def __init__(self):
        shutil.copyfile(os.path.join(HERE, "robot-montaj.FCStd"), KOPYA)
        self.doc = App.openDocument(KOPYA)
        self.ad = self.doc.Name
        self.asm = self.doc.getObject("Assembly")
        sim = self.doc.getObject("Kollari_oynat")
        if sim is None:
            raise RuntimeError("Kollari_oynat simulasyonu yok: once montaj_gorsel.py calistir")
        self.adim_ms = int(round(sim.cTimeStepOutput.Value * 1000)) if hasattr(sim.cTimeStepOutput, "Value") \
            else int(round(float(sim.cTimeStepOutput) * 1000))
        for o in self.doc.Objects:          # eklem isaretleri hareketi kapatmasin
            if getattr(o, "JointType", None) is not None or o.TypeId == "App::FeaturePython" and hasattr(o, "Proxy") \
                    and type(o.Proxy).__name__ == "GroundedJoint":
                o.ViewObject.Visibility = False
        self.asm.generateSimulation(sim)
        self.n = self.asm.numberOfFrames()
        log("kare", self.n, "adim ms", self.adim_ms)
        v = Gui.getDocument(self.ad).activeView()
        v.viewIsometric()
        v.fitAll()
        self.k = 1
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.kare)
        self.timer.start(max(15, self.adim_ms))
        self.kisayol = QtGui.QShortcut(QtGui.QKeySequence("Space"), Gui.getMainWindow())
        self.kisayol.activated.connect(self.duraklat)

    def duraklat(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start()

    def kare(self):
        if self.ad not in App.listDocuments():
            self.timer.stop()
            return
        try:
            self.asm.updateForFrame(self.k)
        except Exception:
            import traceback
            log(traceback.format_exc())
            self.timer.stop()
            return
        self.k = self.k + 1 if self.k + 1 < self.n else 1      # kare 0 = baslangic montaji; 1..n-1 dongu
        Gui.updateGui()


def basla():
    try:
        App._robot_dongu = Dongu()       # referans tutulmazsa zamanlayici silinir
    except Exception:
        import traceback
        log(traceback.format_exc())


QtCore.QTimer.singleShot(3000, basla)
