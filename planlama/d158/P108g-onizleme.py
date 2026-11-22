# P10.8g önizleme (FreeCAD'siz; P108f-onizleme.py kalıbı): rehber/ klasörünün geçici kopyasında (sistemin geçici klasörü)
# rehber_gorunum.isle() çalışma ağacındaki kaynakla (rehber_metin / rehber_gorunum) koşar (--veri-yok üretiminin görünüm adımı), sonra
# parça etiketi ölçümü P108f-etiket-olc.py --rehber <kopya> --teslimsiz (üretimle aynı çekim: alt adım CDP, alt adımsız --screenshot)
# ve isteğe bağlı F10d uç etiketi ölçümü (--uc) kopyada. Depodaki rehber/ ve planlama/rehber/ DEĞİŞMEZ.
# Çıktı: P108g-olcum/onizleme/<ad>/ (kareler, etiket-olc.json, uc.json).
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108g-onizleme.py <ad> [--uc] [--kopya-kalsin]
import os, sys, shutil, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_gorunum as RG  # noqa: E402


def main(arg):
    ad = ([a for a in arg if not a.startswith("--")] or ["kaynak"])[0]
    kok = os.path.join(tempfile.gettempdir(), "p108g-onizleme-" + ad)
    if os.path.isdir(kok):
        shutil.rmtree(kok)
    shutil.copytree(os.path.join(ROBOT, "rehber"), kok, ignore=shutil.ignore_patterns("goruntu"))
    RG.VERI_DIR = os.path.join(kok, "veri")
    RG.isle(sessiz=False)
    out = os.path.join(HERE, "P108g-olcum", "onizleme", ad)
    os.makedirs(out, exist_ok=True)
    py = [sys.executable, "-B", "-X", "utf8"]
    r = subprocess.run(py + [os.path.join(HERE, "P108f-etiket-olc.py"), "--rehber", kok, "--teslimsiz", "--json",
                             os.path.join(out, "etiket-olc.json"), "--png", out])
    print("etiket-olc cikis", r.returncode)
    if "--uc" in arg:
        r2 = subprocess.run(py + [os.path.join(HERE, "F10d-dogrula.py"), "--rehber", kok, "--yalniz-uc", os.path.join(out, "uc.json")])
        print("F10d --yalniz-uc cikis", r2.returncode)
    if "--kopya-kalsin" in arg:
        print("kopya:", kok)
    else:
        shutil.rmtree(kok, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:])
