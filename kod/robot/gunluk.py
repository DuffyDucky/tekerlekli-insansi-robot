# Ne yapıyor: her soru-cevap turunu CSV dosyasına bir satır olarak yazar (etkileşim günlüğü).
# Dosya: gunlukler/YYYY-MM-DD.csv (her gün yeni dosya). Ölçüm için: tanınan metin, eşleşen konu, süreler.
# Kronometre bir tur içindeki adımların sürelerini milisaniye olarak tutar.
#
# Süreler (ms):  dinleme      = stt.dinle() süresi (konuşma/yazma süresi + tanıma)
#                dusunme      = dil.cevapla() süresi
#                seslendirme  = tts.soyle() süresi (Piper'da ses dosyası üretme + çalma)
#                uctan_uca    = tetik anından seslendirmenin bitişine kadar tüm tur (jest beklemesi dahil)

import csv
import os
import time
from datetime import date, datetime

# Excel'de açılınca sütunlara ayrılsın diye: Türkçe Excel ";" bekler, "utf-8-sig" Türkçe harfleri korur
AYIRAC = ";"
KODLAMA = "utf-8-sig"

ALANLAR = ["zaman", "tetik", "stt", "taninan", "dil", "konu", "puan", "cevap", "jest",
           "dinleme_ms", "dusunme_ms", "seslendirme_ms", "uctan_uca_ms"]


def ms(saniye):
    return round(saniye * 1000)


class Kronometre:
    """Tur başında kurulur; adim('dinleme') önceki adımdan beri geçen süreyi o ada yazar."""

    def __init__(self):
        self.zaman = datetime.now()
        self.baslangic = self.son = time.perf_counter()
        self.sureler = {}

    def adim(self, ad):
        simdi = time.perf_counter()
        self.sureler[ad] = ms(simdi - self.son)
        self.son = simdi

    def toplam(self):
        return ms(time.perf_counter() - self.baslangic)


def bilesen_adi(nesne):
    """Günlükte görünecek ad: sınıf adı; bulut dil modelinde sağlayıcı da yazılır."""
    ad = type(nesne).__name__
    saglayici = getattr(nesne, "saglayici", None)
    if saglayici:
        ad += f"({saglayici})" if getattr(nesne, "calisiyor", True) else f"({saglayici}, kurala düştü)"
    return ad


def tur_satiri(robot, soru, cevap, kronometre):
    """Bir turu CSV satırına (sözlük) çevirir. Soru duyulmadıysa cevap None olur; satır yine yazılır."""
    s = kronometre.sureler
    return {
        "zaman": kronometre.zaman.isoformat(timespec="seconds"),
        "tetik": bilesen_adi(robot.tetik),
        "stt": bilesen_adi(robot.stt),
        "taninan": soru or "",
        "dil": bilesen_adi(robot.dil),
        "konu": (cevap.konu or "") if cevap else "",
        "puan": cevap.puan if cevap else "",
        "cevap": cevap.metin if cevap else "",
        "jest": (cevap.jest or "") if cevap else "",
        "dinleme_ms": s.get("dinleme", ""),
        "dusunme_ms": s.get("dusunme", ""),
        "seslendirme_ms": s.get("seslendirme", ""),
        "uctan_uca_ms": kronometre.toplam(),
    }


class Gunluk:
    def __init__(self, klasor):
        self.klasor = klasor          # klasör ilk yazışta açılır

    def dosya_yolu(self, gun=None):
        gun = gun or date.today()
        return os.path.join(self.klasor, gun.isoformat() + ".csv")

    def yaz(self, satir):
        """Satırı günün dosyasının sonuna ekler; dosya yeniyse önce başlık satırını yazar.
        Yazılamazsa (disk dolu, izin yok) robot durmaz, yalnız uyarı yazılır."""
        try:
            os.makedirs(self.klasor, exist_ok=True)
            yol = self.dosya_yolu()
            yeni = not os.path.exists(yol) or os.path.getsize(yol) == 0
            with open(yol, "a", encoding=KODLAMA, newline="") as dosya:
                yazici = csv.DictWriter(dosya, fieldnames=ALANLAR, delimiter=AYIRAC)
                if yeni:
                    yazici.writeheader()
                yazici.writerow(satir)
        except OSError as hata:
            print(f"[günlük] Yazılamadı: {hata}")
