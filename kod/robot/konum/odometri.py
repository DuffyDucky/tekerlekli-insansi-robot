# Ne yapıyor: tekerlek enkoderlerinden ölü hesap (dead reckoning). ESP32 saniyede ~10 kez şu satırı yollar:
#   {"k":"odo","sol":<tik>,"sag":<tik>,"yaw":<derece ya da null>,"ms":<ESP32 millis>}
# sol/sag: açılıştan (ya da {"k":"odo_sifirla"} komutundan) beri BİRİKMİŞ tik sayısı (int32, ileri = artı).
# Diferansiyel sürüş: d = (d_sol + d_sag) / 2,  dθ = (d_sag - d_sol) / iz_genişliği.
# yaw (IMU) geliyorsa yön ondan alınır (enkoderin dönüşteki kayması IMU'da yok).
#
# Ölü hesabın hatası yol boyunca birikir (teker kayması, çap hatası): ArUco/GPS ile duzelt() çağrılır.
# Güven son düzeltmeden beri gidilen yolla düşer. Odometri BÖLGE söylemez, yalnız x, y, yön verir.
# Sabitler kod/esp32/src/motorlar.cpp ile aynı (TAHMİNİ; ölçülünce ayarlar.yaml konum.odometri'ye yazın).

import math
import threading

from robot.konum.kaynak import KonumKaynagi, KonumTahmini, sinirla

TIK_TUR = 1980.0          # tekerleğin bir turunda tik (22 x 90, motorlar.cpp TIK_PER_TUR)
TEKER_CAP_M = 0.125       # motorlar.cpp TEKER_CAPI_M
IZ_GENISLIK_M = 0.426     # motorlar.cpp IZ_GENISLIGI_M
GUVEN_YOLU_M = 20.0       # düzeltmeden sonra bu kadar yol gidilince güven en düşüğe iner
AZAMI_ADIM_M = 1.0        # tek mesajda bundan uzun yol = ESP32 yeniden başladı/sıfırlandı; atla


def aci_duzelt(a):
    """Açıyı (-180, 180] aralığına getirir."""
    n = (a + 180.0) % 360.0 - 180.0
    return 180.0 if n == -180.0 else n


def aci_farki(a, b):
    """b - a, -180..180 aralığında (derece)."""
    return (b - a + 180.0) % 360.0 - 180.0


class Odometri(KonumKaynagi):
    ad = "odometri"

    def __init__(self, tik_tur=TIK_TUR, teker_cap_m=TEKER_CAP_M, iz_genislik_m=IZ_GENISLIK_M,
                 agirlik=0.5, aralik=0.5, yaw_isareti=1):
        super().__init__(agirlik, aralik)
        self.yaw_isareti = 1 if yaw_isareti >= 0 else -1   # -1: IMU saat yönünde artıyor (bizde tersi artı)
        self.metre_tik = math.pi * teker_cap_m / tik_tur
        self.iz = iz_genislik_m
        self.kilit = threading.Lock()     # seri okuma iş parçacığı yazar, birleştirici okur
        self.x = self.y = 0.0
        self.yon = 0.0                    # derece
        self.onceki = None                # (sol, sag) son birikmiş tikler
        self.yaw_farki = None             # IMU yaw'ı ile bizim yön arasındaki fark (duzelt ile ayarlanır)
        self.yol_m = 0.0                  # son düzeltmeden beri gidilen yol
        self.mesaj_sayisi = 0

    def isle(self, mesaj):
        """ESP32 satırı (sözlük). 'odo' değilse False. Konumu ilerletir."""
        if not isinstance(mesaj, dict) or mesaj.get("k") != "odo":
            return False
        try:
            sol, sag = int(mesaj["sol"]), int(mesaj["sag"])
            yaw = mesaj.get("yaw")
            yaw = None if yaw is None else self.yaw_isareti * float(yaw)
        except (KeyError, TypeError, ValueError):
            return False
        with self.kilit:
            self.mesaj_sayisi += 1
            onceki, self.onceki = self.onceki, (sol, sag)
            if onceki is None:
                return True                       # ilk mesaj: yalnız başlangıç tikleri
            d_sol = (sol - onceki[0]) * self.metre_tik
            d_sag = (sag - onceki[1]) * self.metre_tik
            if abs(d_sol) > AZAMI_ADIM_M or abs(d_sag) > AZAMI_ADIM_M:
                return True                       # sayaç sıfırlandı ya da taştı: bu adımı sayma
            self._ilerle(d_sol, d_sag, yaw)
        return True

    def _ilerle(self, d_sol, d_sag, yaw):
        d = (d_sol + d_sag) / 2.0
        if yaw is not None:
            if self.yaw_farki is None:
                self.yaw_farki = aci_farki(float(yaw), self.yon)   # ilk yaw: bizim yönle hizala
            yeni_yon = float(yaw) + self.yaw_farki
        else:
            yeni_yon = self.yon + math.degrees((d_sag - d_sol) / self.iz)
        orta = math.radians(self.yon + aci_farki(self.yon, yeni_yon) / 2.0)   # yayın ortasındaki yön
        self.x += d * math.cos(orta)
        self.y += d * math.sin(orta)
        self.yon = aci_duzelt(yeni_yon)
        self.yol_m += abs(d)

    def duzelt(self, x, y, yon=None):
        """Dış kaynağın (ArUco, GPS) verdiği konuma atlar; yön verilirse yön de, IMU farkı da yeniden ayarlanır."""
        with self.kilit:
            self.x, self.y = float(x), float(y)
            if yon is not None:
                self.yon = aci_duzelt(float(yon))
                self.yaw_farki = None
            self.yol_m = 0.0

    def sifirla(self):
        """Yerel sıfırlama (ESP32'ye {"k":"odo_sifirla"} gönderilince de çağrılır)."""
        with self.kilit:
            self.x = self.y = self.yon = 0.0
            self.onceki = None
            self.yaw_farki = None
            self.yol_m = 0.0

    def olc(self):
        with self.kilit:
            if self.mesaj_sayisi == 0:
                return None                       # ESP32'den hiç odo satırı gelmedi
            guven = sinirla(1.0 - self.yol_m / GUVEN_YOLU_M, 0.1, 1.0)
            return KonumTahmini(x=self.x, y=self.y, yon_derece=self.yon, guven=guven, kaynak=self.ad)

    def ham(self):
        if self.mesaj_sayisi == 0:
            return "ESP32'den odo satırı gelmedi (seri port boş ya da firmware eski)"
        return (f"x {self.x:.2f} m, y {self.y:.2f} m, yön {self.yon:.0f}°, düzeltmeden beri {self.yol_m:.1f} m, "
                f"{self.mesaj_sayisi} mesaj")
