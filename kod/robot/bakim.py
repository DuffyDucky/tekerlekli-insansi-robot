# Ne yapıyor: bakım modu. Açıkken robot bir kez "Şu an bakımdayım, birazdan dönerim." der, sonra susar;
# yüzde bakım ifadesi, mikrofon/tetik kapalı, ESP32'ye "dur" gider. İki yolla açılır: ana.py --bakim ya da
# ayarlar.yaml bakim.etkin (yeniden başlatana kadar), ya da kod/bakim.txt dosyası (varken bakım, silinince çıkar).
# Dosyayı ileride telefon uygulaması yazıp silecek; elle de olur:  touch kod/bakim.txt  /  rm kod/bakim.txt
# Durum geçişleri ana.py'de (bakim_denetle): BEKLE -> BAKIM -> BEKLE; konuşma turu yarıda kesilmez.

import os
import time

KOD_KLASORU = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAKIM_DOSYASI = os.path.join(KOD_KLASORU, "bakim.txt")
BAKIM_SOZU = "Şu an bakımdayım, birazdan dönerim."
DENETIM_ARALIGI = 1.0       # saniye: bakım dosyasına ne sıklıkla bakılır


class Bakim:
    """etkin: komut/ayarla açılan kalıcı bakım. dosya: varlığı bakımı açan dosya (None = dosyaya bakılmaz).
    uyu: testte beklemesiz sahte uyku verilir."""

    def __init__(self, etkin=False, dosya=BAKIM_DOSYASI, aralik=DENETIM_ARALIGI, uyu=time.sleep):
        self.etkin = bool(etkin)
        self.dosya = dosya
        self.aralik = float(aralik)
        self.uyu = uyu

    def acik_mi(self):
        if self.etkin:
            return True
        return bool(self.dosya) and os.path.exists(self.dosya)

    def bekle(self):
        """Bakımdayken bir sonraki denetime kadar sessizce bekler."""
        self.uyu(self.aralik)

    def neden(self):
        return "--bakim / ayarlar.yaml" if self.etkin else f"{self.dosya} var"
