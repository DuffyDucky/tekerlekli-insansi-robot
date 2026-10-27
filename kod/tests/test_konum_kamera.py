# Kamerayla konum: ArUco işareti (sahte kareye çizilmiş işaret) ve görsel yer tanıma (numpy ile sentetik
# sahneler). OpenCV yoksa bu testler atlanır (pytest.importorskip); kamera hiç açılmaz.

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from robot.konum.aruco import ArucoKaynagi, isaret_resmi, kenar_uzunlugu  # noqa: E402
from robot.konum.bolgeler import veriden  # noqa: E402
from robot.konum.gorsel import GorselKaynak, orb_histogrami, orb_ozeti  # noqa: E402

if not hasattr(cv2, "aruco"):
    pytest.skip("cv2.aruco yok (opencv-contrib gerekir)", allow_module_level=True)

BOLGELER = veriden({"isaretler": {7: "giris-holu", 3: {"bolge": "bahce", "x": 1.5, "y": 2.0, "yon": 90}}})


def isaretli_kare(kimlik, kenar, sol=200, ust=100):
    kare = np.full((480, 640, 3), 255, np.uint8)
    resim = isaret_resmi(kimlik, kenar)
    h, w = resim.shape
    kare[ust:ust + h, sol:sol + w] = resim[:, :, None]
    return kare


def aruco(kare):
    k = ArucoKaynagi(BOLGELER, kare_al=lambda: kare)
    k.baslat()
    return k


def test_isaret_bolge_ve_konum():
    t = aruco(isaretli_kare(3, 200)).oku()
    assert t.bolge == "bahce" and (t.x, t.y, t.yon_derece) == (1.5, 2.0, 90.0)
    assert t.guven == 1.0 and t.kaynak == "aruco"


def test_kucuk_isaret_dusuk_guven():
    t = aruco(isaretli_kare(7, 48)).oku()               # 48 px'lik resmin içindeki işaret ~40 px
    assert t.bolge == "giris-holu" and 0.1 <= t.guven < 0.7


def test_tabloda_olmayan_isaret_ve_bos_kare():
    assert aruco(isaretli_kare(12, 200)).oku() is None
    assert aruco(np.full((480, 640, 3), 255, np.uint8)).oku() is None
    assert ArucoKaynagi(BOLGELER, kare_al=lambda: None).oku() is None   # baslat yok: pasif değil ama kare yok


def test_kamera_yoksa_pasif():
    k = ArucoKaynagi(BOLGELER, kare_al=None)
    k.baslat()
    assert not k.etkin


def test_kenar_uzunlugu():
    assert kenar_uzunlugu(np.array([[0, 0], [10, 0], [10, 10], [0, 10]], np.float32)) == 10.0


# ---------- görsel yer tanıma ----------

def sahne(tohum):
    """Rastgele renkli dikdörtgen ve çizgilerden oluşan 640x480 'oda'."""
    rng = np.random.default_rng(tohum)
    kare = np.full((480, 640, 3), rng.integers(0, 255, 3), np.uint8)
    for _ in range(40):
        x, y = rng.integers(0, 600), rng.integers(0, 440)
        w, h = rng.integers(10, 120, 2)
        renk = tuple(int(c) for c in rng.integers(0, 255, 3))
        cv2.rectangle(kare, (int(x), int(y)), (int(x + w), int(y + h)), renk, -1)
    for _ in range(30):
        p1 = tuple(int(c) for c in rng.integers(0, 640, 2))
        p2 = tuple(int(c) for c in rng.integers(0, 480, 2))
        cv2.line(kare, p1, p2, (0, 0, 0), 2)
    return kare


def biraz_degistir(kare, tohum):
    """Aynı sahne: 4 px kaydırma + gürültü + biraz parlaklık (robot tam aynı yerde durmaz)."""
    rng = np.random.default_rng(tohum)
    kaymis = np.roll(kare, 4, axis=1).astype(np.int16) + 10
    return np.clip(kaymis + rng.integers(-12, 12, kare.shape), 0, 255).astype(np.uint8)


def test_ozet_deterministik_ve_sabit_boyutlu():
    a, b = orb_ozeti(sahne(1)), orb_ozeti(sahne(1))
    assert np.array_equal(a, b)
    assert a.shape == (3072 + 32 + 64,) and orb_ozeti(sahne(2)).shape == a.shape
    assert orb_ozeti(np.zeros((480, 640, 3), np.uint8)).shape == a.shape   # ORB nokta bulamasa da


def test_orb_histogrami_kovalar():
    tanim = np.zeros((2, 32), np.uint8)
    tanim[0, 0] = 0b11100000                     # 1. grubun ilk baytı: üst 3 bit = 7
    hist = orb_histogrami(tanim)
    assert hist.sum() == 2 * 8 and hist[7] == 1 and hist[0] == 1
    assert orb_histogrami(None).sum() == 0


def test_ayni_sahne_ayni_bolgeye(tmp_path):
    g = GorselKaynak(kare_al=None, klasor=str(tmp_path), model_yolu=None)
    g.baslat()                                   # kamera yok: pasif, ama öğretme/tanıma işlevleri çalışır
    for i in range(2):
        g.ogret("giris-holu", biraz_degistir(sahne(1), 10 + i))
        g.ogret("kantin-onu", biraz_degistir(sahne(2), 20 + i))
    assert len(list(tmp_path.glob("*/*.npz"))) == 4
    assert g.tani(biraz_degistir(sahne(1), 99))[0] == "giris-holu"
    assert g.tani(biraz_degistir(sahne(2), 98))[0] == "kantin-onu"

    # Kaydedilen örnekler yeni bir kaynağa yüklenir; oku() eşik üstünde bölge döner
    kare = biraz_degistir(sahne(2), 97)
    yeni = GorselKaynak(kare_al=lambda: kare, klasor=str(tmp_path), model_yolu=None)
    yeni.baslat()
    assert yeni.yontem == "orb" and len(yeni.ornekler) == 4
    t = yeni.oku()
    assert t.bolge == "kantin-onu" and t.kaynak == "gorsel" and t.guven > 0


def test_tanimadigi_sahne_esik_altinda(tmp_path):
    kare = sahne(3)
    g = GorselKaynak(kare_al=lambda: kare, klasor=str(tmp_path), model_yolu=None, esik=0.95)
    g.baslat()
    assert g.oku() is None                       # örnek yok
    g.ogret("giris-holu", sahne(1))
    assert g.oku() is None and g.son_benzerlik < 0.95
