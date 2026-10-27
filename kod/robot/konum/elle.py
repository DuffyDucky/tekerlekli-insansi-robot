# Ne yapıyor: bölgeyi elle söyletir. İki yol: komut satırında --konum <bolge> (ana.py), ya da
# kod/konum/bolge.txt dosyası (ilk satır bölge adı; her 5 s'de bir yeniden okunur). İleride Nextion ekran
# ya da QR okuyucu bu dosyaya yazacak. En son verilen söz geçerli: dosya program açıldıktan SONRA
# değiştiyse (değişme zamanı açılıştakinden farklıysa) dosya, değilse --konum kazanır. Güven 1.0 ve zaman aşımı yoktur (tahmin hep taze sayılır).

import os

from robot.konum.bolgeler import KONUM_KLASORU
from robot.konum.kaynak import KonumKaynagi, KonumTahmini

BOLGE_DOSYASI = os.path.join(KONUM_KLASORU, "bolge.txt")
OKUMA_ARALIGI = 5.0


class ElleKaynak(KonumKaynagi):
    ad = "elle"
    zaman_asimi_yok = True     # birleştirici bu kaynağın tahminini eskimiş saymaz; None gelirse siler

    def __init__(self, bolge=None, dosya=BOLGE_DOSYASI, agirlik=3.0, aralik=OKUMA_ARALIGI, bilinen_bolgeler=None):
        super().__init__(agirlik, aralik)
        self.komut_bolgesi = bolge or None
        self.dosya = dosya
        self.acilis_zamani = self.degisme_zamani()     # açılışta dosyanın değişme zamanı (yoksa None)
        self.bilinen_bolgeler = set(bilinen_bolgeler or [])
        self.uyarilanlar = set()

    def degisme_zamani(self):
        if not self.dosya or not os.path.exists(self.dosya):
            return None
        return os.path.getmtime(self.dosya)

    def dosyadan_oku(self):
        """(bölge, değişme zamanı) ya da dosya yoksa/boşsa (None, None)."""
        if not self.dosya or not os.path.exists(self.dosya):
            return None, None
        with open(self.dosya, encoding="utf-8") as f:
            satir = f.readline().strip()
        return (satir or None), os.path.getmtime(self.dosya)

    def secili_bolge(self):
        dosya_bolgesi, degisme = self.dosyadan_oku()
        if dosya_bolgesi and (self.komut_bolgesi is None or degisme != self.acilis_zamani):
            return dosya_bolgesi
        return self.komut_bolgesi

    def olc(self):
        bolge = self.secili_bolge()
        if bolge is None:
            return None
        if self.bilinen_bolgeler and bolge not in self.bilinen_bolgeler and bolge not in self.uyarilanlar:
            print(f"[konum/elle] '{bolge}' bolgeler.yaml'da yok; yine de kullanıyorum (yazım hatası mı?).")
            self.uyarilanlar.add(bolge)
        return KonumTahmini(bolge=bolge, guven=1.0, kaynak=self.ad)   # zaman = şimdi: hep taze

    def ham(self):
        dosya_bolgesi, _ = self.dosyadan_oku()
        return f"--konum: {self.komut_bolgesi or '-'}; bolge.txt: {dosya_bolgesi or '-'}; seçili: {self.secili_bolge() or '-'}"
