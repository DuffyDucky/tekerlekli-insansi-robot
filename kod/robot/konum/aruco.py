# Ne yapıyor: duvarlara asılan ArUco işaretlerini (DICT_4X4_50, 0-49 arası kimlik) kamerada arar.
# bolgeler.yaml 'isaretler:' tablosu: kimlik -> bölge ve isteğe bağlı x, y, yön (işareti gören robotun
# yaklaşık konumu). Birden çok işaret görülürse en büyük görüneni (en yakını) seçilir.
# İşaret küçük görünüyorsa (uzak) güven düşer. OpenCV (cv2.aruco, opencv-contrib) ya da kamera yoksa pasif.
#
# İşaret basmak için: python3 -m robot.konum isaret 7   (konum/isaretler/isaret_7.png, A4'e 15 cm basın)

from robot.konum.kaynak import KonumKaynagi, KonumTahmini, sinirla

SOZLUK = "DICT_4X4_50"
IYI_KENAR_PX = 80.0       # işaretin kenarı 640x480 karede bu kadar pikselse tam güven (15 cm işaret ~2 m)


def dedektor_kur(cv2):
    """OpenCV 4.7+ ArucoDetector; Pi OS Bookworm'daki 4.6 için eski işlev arayüzü."""
    sozluk = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, SOZLUK))
    if hasattr(cv2.aruco, "ArucoDetector"):
        dedektor = cv2.aruco.ArucoDetector(sozluk, cv2.aruco.DetectorParameters())
        return dedektor.detectMarkers
    parametre = cv2.aruco.DetectorParameters_create()
    return lambda gri: cv2.aruco.detectMarkers(gri, sozluk, parameters=parametre)


def isaret_resmi(kimlik, kenar_px=400):
    """Basılacak işaret resmi (gri numpy dizisi), beyaz kenar boşluklu."""
    import cv2
    import numpy as np
    sozluk = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, SOZLUK))
    if hasattr(cv2.aruco, "generateImageMarker"):
        resim = cv2.aruco.generateImageMarker(sozluk, int(kimlik), kenar_px)
    else:
        resim = cv2.aruco.drawMarker(sozluk, int(kimlik), kenar_px)
    bosluk = kenar_px // 8
    return np.pad(resim, bosluk, constant_values=255)


def kenar_uzunlugu(koseler):
    """Dört köşeden ortalama kenar uzunluğu (piksel)."""
    k = koseler.reshape(4, 2)
    toplam = 0.0
    for i in range(4):
        dx, dy = k[(i + 1) % 4] - k[i]
        toplam += (dx * dx + dy * dy) ** 0.5
    return toplam / 4


class ArucoKaynagi(KonumKaynagi):
    ad = "aruco"

    def __init__(self, bolgeler, kare_al=None, agirlik=1.0, aralik=1.0, iyi_kenar_px=IYI_KENAR_PX):
        super().__init__(agirlik, aralik)
        self.bolgeler = bolgeler
        self.kare_al = kare_al            # kamera.Kamera().kare_al ya da testte sahte kare veren işlev
        self.iyi_kenar_px = iyi_kenar_px
        self.bul = None
        self.cv2 = None
        self.son_gorulen = []             # ham çıktı için: [(kimlik, kenar_px), ...]

    def baslat(self):
        try:
            import cv2
            if not hasattr(cv2, "aruco"):
                raise ImportError("cv2.aruco yok")
        except ImportError as hata:
            self.pasif_yap(f"OpenCV aruco modülü yok ({hata}); pip install opencv-contrib-python-headless "
                           "ya da sudo apt install python3-opencv")
            return
        if self.kare_al is None:
            self.pasif_yap("kamera verilmedi")
            return
        self.cv2 = cv2
        self.bul = dedektor_kur(cv2)

    def isaretleri_bul(self, kare):
        """[(kimlik, kenar_px), ...] büyükten küçüğe."""
        gri = kare if kare.ndim == 2 else self.cv2.cvtColor(kare, self.cv2.COLOR_BGR2GRAY)
        koseler, kimlikler, _ = self.bul(gri)
        if kimlikler is None:
            return []
        sonuc = [(int(k), kenar_uzunlugu(c)) for k, c in zip(kimlikler.flatten(), koseler)]
        return sorted(sonuc, key=lambda kk: -kk[1])

    def olc(self):
        kare = self.kare_al()
        if kare is None:
            return None
        self.son_gorulen = self.isaretleri_bul(kare)
        for kimlik, kenar in self.son_gorulen:
            isaret = self.bolgeler.isaretler.get(kimlik)
            if not isaret or not isaret.get("bolge"):
                continue                  # tabloda olmayan işaret (başka bir şeyin işareti) yoksayılır
            return KonumTahmini(bolge=isaret["bolge"], x=isaret.get("x"), y=isaret.get("y"),
                                yon_derece=isaret.get("yon"), guven=sinirla(kenar / self.iyi_kenar_px, 0.1, 1.0),
                                kaynak=self.ad)
        return None

    def ham(self):
        if not self.etkin:
            return f"pasif: {self.pasif_nedeni}"
        tahmin = self.oku()
        if tahmin is None and not self.son_gorulen:
            return "işaret görülmedi (ya da kamera kare vermedi)"
        gorulen = ", ".join(f"#{k} {p:.0f}px" for k, p in self.son_gorulen)
        return f"görülen: {gorulen or '-'}; tahmin: {tahmin}"
