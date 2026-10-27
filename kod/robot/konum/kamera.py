# Ne yapıyor: kameradan tek kare alır (BGR numpy dizisi). Pi'de Picamera2 (CSI kamera) varsa onu, yoksa
# OpenCV VideoCapture(0) (USB kamera / dizüstü kamerası) kullanır. ArUco ve görsel tanıma AYNI kamerayı
# paylaşır; aynı anda iki iş parçacığı kare istemesin diye kilit vardır. Kamera yoksa kare_al() None döner.
#
# Testlerde kamera yerine kare_al=lambda: sahte_kare verilir (aruco.py, gorsel.py).

import threading

GENISLIK, YUKSEKLIK = 640, 480


class Kamera:
    def __init__(self, aygit=0):
        self.aygit = aygit
        self.kilit = threading.Lock()
        self.picam = None
        self.yakalayici = None
        self.acildi = False
        self.hata = None          # açılamadıysa nedeni

    def ac(self):
        """Kamerayı bir kez açar. Başarılıysa True."""
        if self.acildi:
            return True
        if self.hata:
            return False          # bir kez açılamadıysa her karede yeniden denenmez (yavaş)
        try:
            from picamera2 import Picamera2
            self.picam = Picamera2()
            # Picamera2'de "RGB888" biçimi bellekte B, G, R sırasıyla gelir: OpenCV'nin beklediği BGR
            self.picam.configure(self.picam.create_still_configuration(
                main={"size": (GENISLIK, YUKSEKLIK), "format": "RGB888"}))
            self.picam.start()
            self.acildi = True
            return True
        except Exception:
            self.picam = None
        try:
            import cv2
        except ImportError:
            self.hata = "OpenCV yok (sudo apt install python3-opencv ya da pip install opencv-contrib-python-headless)"
            return False
        yakalayici = cv2.VideoCapture(self.aygit)
        if not yakalayici.isOpened():
            self.hata = f"kamera {self.aygit} açılamadı (takılı mı, başka program kullanıyor mu?)"
            return False
        yakalayici.set(cv2.CAP_PROP_FRAME_WIDTH, GENISLIK)
        yakalayici.set(cv2.CAP_PROP_FRAME_HEIGHT, YUKSEKLIK)
        self.yakalayici = yakalayici
        self.acildi = True
        return True

    def kare_al(self):
        with self.kilit:
            if not self.ac():
                return None
            if self.picam is not None:
                return self.picam.capture_array()
            tamam, kare = self.yakalayici.read()
            return kare if tamam else None

    def kapat(self):
        with self.kilit:
            if self.picam is not None:
                self.picam.stop()
                self.picam.close()
            if self.yakalayici is not None:
                self.yakalayici.release()
            self.picam = self.yakalayici = None
            self.acildi = False
