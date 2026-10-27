# Ne yapıyor: kamerayla yer öğrenme ve tanıma. Öğretirken her bölgede birkaç kare çekilir, her kare sabit
# boyutlu bir "özet vektöre" çevrilip konum/gorsel_ornekler/<bölge>/*.npz olarak saklanır. Tanırken yeni
# karenin özeti tüm örneklerle kosinüs benzerliğiyle karşılaştırılır; en benzer örneğin bölgesi söylenir
# (en yakın komşu). Benzerlik eşiğin altındaysa None ("burayı tanımıyorum").
#
# Özet (yalnız OpenCV + numpy, varsayılan "orb" yöntemi), üç parçanın birleşimi:
#   1) 64x48 gri küçük resim (genel düzen; ortalaması çıkarılır, ışık değişimine biraz dayanır)
#   2) HSV renk histogramı (8 renk tonu x 4 doygunluk = 32 kova)
#   3) ORB anahtar nokta tanımlayıcıları: her tanımlayıcının 32 baytı 4'erli 8 gruba bölünür, her grubun ilk
#      baytının üst 3 biti o grup için 8 kovadan birini seçer -> 8 grup x 8 kova = 64 kovalı histogram.
#      k-means (sözlük eğitimi) gerekmez, deterministiktir: aynı kare her zaman aynı özeti verir.
# İsteğe bağlı daha iyi özet ("onnx"): onnxruntime + modeller/mobilenet.onnx varsa MobileNet çıktısı kullanılır.
# İki yöntemin örnekleri birbirine karıştırılmaz (her .npz yöntemini taşır).
#
# Sınırlar: ışık (gündüz/akşam), kalabalık ve dekor değişince tanıma bozulur; her bölgede farklı saatlerde
# ve birkaç yöne bakarak örnek öğretin.

import glob
import os
import time

from robot.konum.bolgeler import KOD_KLASORU, KONUM_KLASORU
from robot.konum.kaynak import KonumKaynagi, KonumTahmini, sinirla

ORNEK_KLASORU = os.path.join(KONUM_KLASORU, "gorsel_ornekler")
MODEL_YOLU = os.path.join(KOD_KLASORU, "modeller", "mobilenet.onnx")
ESIK = 0.75               # kosinüs benzerliği bunun altındaysa tanınmadı
AGIRLIKLAR = (1.0, 1.0, 1.0)   # gri, renk, ORB parçalarının özete katkısı


def birim(v):
    import numpy as np
    v = np.asarray(v, dtype=np.float32).ravel()
    n = float(np.linalg.norm(v))
    return v / n if n > 0 else v


def orb_histogrami(tanimlayicilar):
    """(N, 32) uint8 -> 64 kovalı histogram (8 grup x 8 kova)."""
    import numpy as np
    hist = np.zeros(64, dtype=np.float32)
    if tanimlayicilar is None or len(tanimlayicilar) == 0:
        return hist
    gruplar = tanimlayicilar[:, 0::4] >> 5           # (N, 8): her grubun ilk baytının üst 3 biti (0-7)
    for g in range(8):
        hist[g * 8:(g + 1) * 8] += np.bincount(gruplar[:, g], minlength=8)
    return hist


def orb_ozeti(kare):
    """Yalnız OpenCV ile sabit boyutlu (3072 + 32 + 64 = 3168) özet vektörü."""
    import cv2
    import numpy as np
    gri = kare if kare.ndim == 2 else cv2.cvtColor(kare, cv2.COLOR_BGR2GRAY)
    kucuk = cv2.resize(gri, (64, 48), interpolation=cv2.INTER_AREA).astype(np.float32)
    kucuk -= kucuk.mean()
    renkli = kare if kare.ndim == 3 else cv2.cvtColor(kare, cv2.COLOR_GRAY2BGR)
    hsv = cv2.cvtColor(renkli, cv2.COLOR_BGR2HSV)
    renk = cv2.calcHist([hsv], [0, 1], None, [8, 4], [0, 180, 0, 256])
    orb = cv2.ORB_create(nfeatures=300)
    _, tanimlayicilar = orb.detectAndCompute(cv2.resize(gri, (320, 240)), None)
    g, r, o = AGIRLIKLAR
    return np.concatenate([g * birim(kucuk), r * birim(renk), o * birim(orb_histogrami(tanimlayicilar))])


class OnnxOzetleyici:
    """MobileNet (ImageNet, 224x224) çıktısını özet olarak kullanır."""

    def __init__(self, yol):
        import onnxruntime
        self.oturum = onnxruntime.InferenceSession(yol, providers=["CPUExecutionProvider"])
        self.girdi = self.oturum.get_inputs()[0].name

    def __call__(self, kare):
        import cv2
        import numpy as np
        renkli = kare if kare.ndim == 3 else cv2.cvtColor(kare, cv2.COLOR_GRAY2BGR)
        rgb = cv2.cvtColor(cv2.resize(renkli, (224, 224)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        rgb = (rgb - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        girdi = rgb.transpose(2, 0, 1)[None].astype(np.float32)
        return birim(self.oturum.run(None, {self.girdi: girdi})[0])


def ozetleyici_sec(model_yolu=MODEL_YOLU):
    """('onnx', işlev) model ve onnxruntime varsa; yoksa ('orb', orb_ozeti)."""
    if model_yolu and os.path.exists(model_yolu):
        try:
            return "onnx", OnnxOzetleyici(model_yolu)
        except Exception as hata:          # onnxruntime yok ya da model bozuk
            print(f"[konum/gorsel] ONNX modeli kullanılamadı ({hata}); ORB özetine düşüyorum.")
    return "orb", orb_ozeti


def kosinus(a, b):
    import numpy as np
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    return float(np.dot(a, b) / (na * nb)) if na > 0 and nb > 0 else 0.0


class GorselKaynak(KonumKaynagi):
    ad = "gorsel"

    def __init__(self, kare_al=None, agirlik=1.0, aralik=5.0, esik=ESIK, klasor=ORNEK_KLASORU,
                 model_yolu=MODEL_YOLU):
        super().__init__(agirlik, aralik)
        self.kare_al = kare_al
        self.esik = esik
        self.klasor = klasor
        self.model_yolu = model_yolu
        self.yontem = None
        self.ozetle = None
        self.ornekler = []               # [(bölge, özet vektörü), ...] yalnız bu yöntemin örnekleri
        self.son_benzerlik = None

    def baslat(self):
        try:
            import cv2  # noqa: F401
            import numpy  # noqa: F401
        except ImportError:
            self.pasif_yap("OpenCV/numpy yok (sudo apt install python3-opencv)")
            return
        self.yontem, self.ozetle = ozetleyici_sec(self.model_yolu)
        self.ornekleri_yukle()
        if self.kare_al is None:
            self.pasif_yap("kamera verilmedi")
        elif not self.ornekler:
            print(f"[konum/gorsel] öğretilmiş örnek yok ({self.yontem}); önce: python3 -m robot.konum ogret <bolge>")

    def ornekleri_yukle(self):
        import numpy as np
        self.ornekler = []
        for yol in sorted(glob.glob(os.path.join(self.klasor, "*", "*.npz"))):
            try:
                veri = np.load(yol)
                if str(veri["yontem"]) == self.yontem:
                    self.ornekler.append((str(veri["bolge"]), veri["ozet"]))
            except Exception as hata:
                print(f"[konum/gorsel] {yol} okunamadı ({hata}); atlandı.")

    def ogret(self, bolge, kare):
        """Kareyi özetler, konum/gorsel_ornekler/<bolge>/<zaman>.npz olarak kaydeder. Dosya yolunu döner."""
        import numpy as np
        if self.ozetle is None:
            self.yontem, self.ozetle = ozetleyici_sec(self.model_yolu)
        ozet = self.ozetle(kare)
        klasor = os.path.join(self.klasor, bolge)
        os.makedirs(klasor, exist_ok=True)
        yol = os.path.join(klasor, time.strftime("%Y%m%d_%H%M%S") + f"_{len(self.ornekler):04d}.npz")
        np.savez_compressed(yol, ozet=ozet, bolge=bolge, yontem=self.yontem)
        self.ornekler.append((bolge, ozet))
        return yol

    def tani(self, kare):
        """(bölge, benzerlik) en yakın örnek; örnek yoksa (None, 0)."""
        if not self.ornekler:
            return None, 0.0
        ozet = self.ozetle(kare)
        en_iyi = max(self.ornekler, key=lambda bo: kosinus(ozet, bo[1]))
        return en_iyi[0], kosinus(ozet, en_iyi[1])

    def olc(self):
        if not self.ornekler:
            return None
        kare = self.kare_al()
        if kare is None:
            return None
        bolge, benzerlik = self.tani(kare)
        self.son_benzerlik = benzerlik
        if bolge is None or benzerlik < self.esik:
            return None
        guven = sinirla((benzerlik - self.esik) / (1.0 - self.esik), 0.1, 1.0)
        return KonumTahmini(bolge=bolge, guven=guven, kaynak=self.ad)

    def ham(self):
        if not self.etkin:
            return f"pasif: {self.pasif_nedeni}"
        tahmin = self.oku()
        bolgeler = sorted({b for b, _ in self.ornekler})
        return (f"yöntem {self.yontem}, {len(self.ornekler)} örnek ({', '.join(bolgeler) or '-'}); "
                f"benzerlik {self.son_benzerlik if self.son_benzerlik is None else round(self.son_benzerlik, 3)}; "
                f"tahmin: {tahmin}")
