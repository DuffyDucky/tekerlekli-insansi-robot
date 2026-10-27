# Ne yapıyor: konum paketinin ortak parçaları. KonumTahmini = bir kaynağın "robot şu an şurada" demesi.
# KonumKaynagi = bütün kaynakların (Wi-Fi, GPS, BLE, ArUco, görsel, odometri, elle) taban sınıfı.
# Kural: bir kaynak hata verirse oku() None döner, robotu düşürmez; kütüphane/donanım yoksa kaynak pasif olur.

import time
from dataclasses import dataclass, field


@dataclass
class KonumTahmini:
    bolge: str | None = None          # bolgeler.yaml'daki bölge kimliği (ör. "giris-holu"); bilinmiyorsa None
    x: float | None = None            # yerel metrik konum (m); yalnız ArUco/odometri/bölge merkezi verir
    y: float | None = None
    yon_derece: float | None = None   # robotun baktığı yön (derece, 0 = +x, saat yönünün tersi artar)
    guven: float = 0.0                # 0-1: kaynak kendi ölçümüne ne kadar güveniyor
    zaman: float = field(default_factory=time.time)   # ölçüm anı (time.time saniyesi)
    kaynak: str = ""                  # tahmini veren kaynağın adı ("wifi", "gps", ...)


def sinirla(deger, alt=0.0, ust=1.0):
    return max(alt, min(ust, deger))


class KonumKaynagi:
    """Alt sınıf yalnız olc() yazar. oku() hataları yakalar; pasif kaynak hiç ölçmez."""

    ad = "kaynak"
    zaman_asimi_yok = False    # True ise tahmin eskimez (yalnız elle seçim)

    def __init__(self, agirlik=1.0, aralik=2.0):
        self.agirlik = float(agirlik)     # birleştirmede bu kaynağın sözünün ağırlığı
        self.aralik = float(aralik)       # arka plan iş parçacığı kaç saniyede bir okusun
        self.pasif_nedeni = None          # None değilse kaynak çalışmıyor (neden açıkça yazılır)
        self.son_hata = None

    @property
    def etkin(self):
        return self.pasif_nedeni is None

    def pasif_yap(self, neden):
        self.pasif_nedeni = neden
        print(f"[konum/{self.ad}] pasif: {neden}")

    def baslat(self):
        """Donanımı açar (seri port, kamera). Olmazsa pasif_yap() çağrılır."""

    def kapat(self):
        """Açılan donanımı bırakır."""

    def olc(self):
        """Tek ölçüm: KonumTahmini ya da None. Alt sınıf yazar."""
        raise NotImplementedError

    def oku(self):
        """Güvenli ölçüm: pasifse ya da hata olursa None (aynı hata art arda yazılmaz)."""
        if not self.etkin:
            return None
        try:
            tahmin = self.olc()
            self.son_hata = None
            return tahmin
        except Exception as hata:
            metin = f"{type(hata).__name__}: {hata}"
            if metin != self.son_hata:
                print(f"[konum/{self.ad}] okuma hatası ({metin}); bu tur atlandı.")
            self.son_hata = metin
            return None

    def ham(self):
        """'python3 -m robot.konum tara' için okunabilir ham çıktı. Alt sınıf zenginleştirebilir."""
        if not self.etkin:
            return f"pasif: {self.pasif_nedeni}"
        return str(self.oku())
