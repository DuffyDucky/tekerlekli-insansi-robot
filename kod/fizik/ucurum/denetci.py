"""ESP32 uçurum denetçisi (saf mantık, yalnız standart kütüphane; birim testli).

ESP32'nin sabit döngüsünde (100 Hz, `dongu_ms` 10; 50 Hz için 20) çalışır ve YALNIZ sensör okumalarını görür:
  - kalibrasyon: açılışta robot düz zeminde dururken her sensörün `kalibrasyon_n` örneğinin ortancası = beklenen
    zemin mesafesi (gerçek kartta açılış / ayar adımı; yer gerçeği kullanılmaz).
  - kanıt: okuma - beklenen > `esik_m` (zemin uzaklaştı) ya da okuma yok (politikaya göre).
  - onay: aynı sensörde art arda `onay` kanıt -> tetik (mandallı). Tetik motor çıkışını Pi'den BAĞIMSIZ keser.
  - dönüşsüz örnek (None) politikası: "ucurum" (veri yok = kanıt), "yok_say" (None atlanır, sayaç değişmez),
    "yavasla" (None görülünce 0,5 s hız sınırı `yavas_hiz`; art arda `yavas_yok_n` None -> tetik).
  - donmuş çıktı: aynı mm değeri art arda `donuk_n` kez -> o sensör arızalı sayılır, okumaları None gibi işlenir.
Fren kipi (`fren`): "kes" (EN LOW, motorlar boşta), "fren" (EN HIGH + PWM 0, kısa devre freni, rampasız), "rampa"
(hedef 0, `fren_ivme` m/s² yavaşlama rampası, öneri firmware PI'ı izler; rampa sonunda PWM 0 freni).
"""

import math

POLITIKALAR = ("ucurum", "yok_say", "yavasla")
FREN_KIPLERI = ("kes", "fren", "rampa")


class DenetciAyar:
    def __init__(self, esik_m=0.04, onay=2, politika="ucurum", fren="rampa", fren_ivme=2.0, dongu_ms=10,
                 donuk_n=25, yavas_hiz=0.10, yavas_yok_n=5, kalibrasyon_n=25):
        assert politika in POLITIKALAR and fren in FREN_KIPLERI
        self.esik_m, self.onay, self.politika = float(esik_m), int(onay), politika
        self.fren, self.fren_ivme, self.dongu_ms = fren, float(fren_ivme), int(dongu_ms)
        self.donuk_n, self.yavas_hiz, self.yavas_yok_n = int(donuk_n), float(yavas_hiz), int(yavas_yok_n)
        self.kalibrasyon_n = int(kalibrasyon_n)

    def sozluk(self):
        return dict(self.__dict__)

    def anahtar(self):
        return "e%d_o%d_%s" % (round(self.esik_m * 1000), self.onay, self.politika)


class UcurumDenetci:
    def __init__(self, n_sensor, ayar=None):
        self.n = n_sensor
        self.ayar = ayar or DenetciAyar()
        self.beklenen = [None] * n_sensor
        self._kal = [[] for _ in range(n_sensor)]
        self.sayac = [0] * n_sensor
        self.yok_sayac = [0] * n_sensor
        self.son = [None] * n_sensor
        self.donuk = [0] * n_sensor
        self.arizali = [False] * n_sensor
        self.tetik = False
        self.tetik_t = None
        self.tetik_sensor = None
        self.neden = None
        self.ariza_olay = []          # (t, sensör, neden)
        self._yavas_bitis = -math.inf
        self.ornek_say = 0
        self.yok_say = 0

    # ------------------------------------------------------------ kalibrasyon
    def kalibrasyon_ornegi(self, i, deger):
        if deger is not None:
            self._kal[i].append(deger)

    def kalibre(self):
        """Ortanca. Örneği olmayan sensör (hep None) kalibre edilemez: arızalı sayılır."""
        for i, L in enumerate(self._kal):
            if L:
                s = sorted(L)
                self.beklenen[i] = s[len(s) // 2]
            else:
                self.arizali[i] = True
                self.ariza_olay.append((0.0, i, "kalibrasyon_yok"))
        return list(self.beklenen)

    # ------------------------------------------------------------ döngü
    def hiz_siniri(self, t):
        return self.ayar.yavas_hiz if (self.ayar.politika == "yavasla" and t < self._yavas_bitis) else None

    def isle(self, t, i, deger):
        """t anında (s) i. sensörün yeni okuması (m ya da None). Tetiklenirse True."""
        a = self.ayar
        self.ornek_say += 1
        if deger is not None and not self.arizali[i]:
            if self.son[i] is not None and round(deger, 3) == round(self.son[i], 3):
                self.donuk[i] += 1
                if self.donuk[i] >= a.donuk_n:
                    self.arizali[i] = True
                    self.ariza_olay.append((t, i, "donuk"))
            else:
                self.donuk[i] = 0
        self.son[i] = deger
        if self.arizali[i]:
            deger = None
        if deger is None:
            self.yok_say += 1
            if a.politika == "yok_say":
                return self.tetik
            if a.politika == "yavasla":
                self.yok_sayac[i] += 1
                self._yavas_bitis = t + 0.5
                kanit = self.yok_sayac[i] >= a.yavas_yok_n
                if kanit:
                    return self._tetikle(t, i, "yok")
                return self.tetik
            kanit = True
            neden = "yok"
        else:
            self.yok_sayac[i] = 0
            b = self.beklenen[i]
            kanit = b is not None and (deger - b) > a.esik_m
            neden = "sapma"
        self.sayac[i] = self.sayac[i] + 1 if kanit else 0
        if self.sayac[i] >= a.onay:
            return self._tetikle(t, i, neden)
        return self.tetik

    def _tetikle(self, t, i, neden):
        if not self.tetik:
            self.tetik, self.tetik_t, self.tetik_sensor, self.neden = True, t, i, neden
        return True
