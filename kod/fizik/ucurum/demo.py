"""3B pencere gösterimi: robot aşağı inen merdivene yürür, ESP32 uçurum denetçisi Pi'den bağımsız durdurur.

    kod\\ucurum.bat [sahne] [ek seçenekler]       (varsayılan merdiven_17x30; ör. kod\\ucurum.bat kose)
    = gorunum3b.py --eklenti ucurum.demo --sahne ucurum_<sahne> --varyant ONERI --beyin ucurum.demo:YuruBeyni

İçe aktarılınca (gorunum3b `--eklenti`) yalnız bu süreçte üç kanca kurar; ortak dosyalar değişmez:
  - dunya.sahne_xml: `ucurum` alanlı sahnede sonsuz düzlem yerine sonlu kutular (sahne.kur)
  - dunya.sahne_oku: "ucurum_<ad>" adını sahne.py'deki sahneye çevirir (öbür adlar aynı)
  - fizik_esp32.FizikEsp32: uçurum denetçili alt sınıf; yalnız `ucurum` alanlı sahnede sensör + denetçi bağlanır
    (seçilen yerleşim / eşik / fren: secim.json), öbür sahnelerde FizikEsp32 ile aynı davranır.
YuruBeyni "Pi"dir: uçurumu bilmez, hep ileri `v` sürer (`--beyin-arg v=0.39`, `--beyin-arg w=0.3`). Pencerede
F7 baştan (denetçi sıfırlanır, yeniden kalibre edilir). Durum satırındaki "mod" yalnız gösterim içindir (ESP32'nin
durumunu yazar; Beyin'in komutu ona bağlı değildir). UCURUM_EKRAN ortam değişkeni bir PNG yolu ise 9. sanal saniyede
pencerenin ekran görüntüsü oraya yazılır (doğrulama).
"""

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucurum import _yol  # noqa: E402
from ucurum import sahne as S  # noqa: E402
from ucurum import kosu  # noqa: E402
from ucurum import sensor as SN  # noqa: E402
from ucurum.denetci import DenetciAyar, UcurumDenetci  # noqa: E402
import dunya as D  # noqa: E402
import fizik_esp32  # noqa: E402

SON = {"c": None}


def _secim():
    yol = os.path.join(_yol.UCURUM, "secim.json")
    if os.path.exists(yol):
        with open(yol, encoding="utf-8") as f:
            return json.load(f)
    return dict(yerlesim=dict(ad="3KO", z=0.06, e=15), esik_m=0.04, onay=2, politika="ucurum", fren="rampa", fren_ivme=2.0)


S.kur()
_asil_oku = D.sahne_oku


def sahne_oku(ad):
    b = os.path.basename(str(ad))
    if b.endswith(".json"):
        b = b[:-5]
    if b.startswith("ucurum_") and b[len("ucurum_"):] in S.SAHNELER:
        a = b[len("ucurum_"):]
        bas = (S.E - 1.3, S.Y0 - 0.5, math.radians(20.0)) if a == "kose" else (S.E - 1.3, S.Y0, 0.0)
        s = S.sahne_sozlugu(a, bas)
        if s["ucurum"].get("taban_z"):
            s["baslangic"]["x"] = S.E - 1.0
        return s
    return _asil_oku(ad)


D.sahne_oku = sahne_oku
_TABAN = kosu.esp32_sinifi()


class DemoEsp32(_TABAN):
    def __init__(self, harita, konum=None, sonar_acik=True, sahne=None, **kw):
        u = bool(sahne and sahne.get("ucurum"))
        super().__init__(harita, konum=konum, sonar_acik=(False if u else sonar_acik), sahne=sahne, **kw)
        self.demo_acik = u
        if not u:
            return
        import numpy as np
        s = _secim()
        ys = s["yerlesim"]
        self.demo_ayar = DenetciAyar(esik_m=s["esik_m"], onay=s["onay"], politika=s["politika"], fren=s["fren"],
                                     fren_ivme=s["fren_ivme"])
        yer = SN.yerlesim(ys["ad"], ys["z"], ys["e"], ys.get("koni", 27.0))
        self.demo_yer = yer
        sd = SN.SensorDizisi(self.dunya, yer, np.random.default_rng(0))
        self.ucurum_bagla(sd, UcurumDenetci(len(yer), self.demo_ayar))
        self.demo_kal_ms = 0
        SON["c"] = self

    def _dilim(self):
        super()._dilim()
        if getattr(self, "demo_acik", False) and self.u_kal:
            self.demo_kal_ms += 10
            if self.demo_kal_ms >= kosu.KAL_SURE_MS + 30 and all(len(L) >= 20 for L in self.u_den._kal):
                self.u_den.kalibre()
                self.u_kal = False

    def konum_ayarla(self, x, y, aci_rad):
        super().konum_ayarla(x, y, aci_rad)
        if getattr(self, "demo_acik", False):          # baştan: denetçi sıfırlanır, yeniden kalibre edilir
            self.u_den = UcurumDenetci(len(self.demo_yer), self.demo_ayar)
            self.u_kal = True
            self.demo_kal_ms = 0
            self.u_tetik_ms = None

    def demo_metin(self):
        d = self.u_den
        if self.u_kal:
            return "UCURUM: kalibrasyon"
        if d.tetik:
            ad = self.u_sensor.ayarlar[d.tetik_sensor].ad if d.tetik_sensor >= 0 else "?"
            return "UCURUM: DURDU (%s, %s, fren %s)" % (ad, d.neden, d.ayar.fren)
        return "UCURUM: izliyor (%d sensor)" % len(self.demo_yer)


fizik_esp32.FizikEsp32 = DemoEsp32


class YuruBeyni:
    """Pi: uçurumdan habersiz, sabit (v, w) sürer. Gösterim için durum metni ESP32'den okunur."""

    def __init__(self, v=0.25, w=0.0, **_):
        self.v, self.w = float(v), float(w)
        self._foto = os.environ.get("UCURUM_EKRAN")
        self._t0 = None

    def adim(self, t, tarama, artim):
        if self._t0 is None:
            self._t0 = t
        if self._foto and t - self._t0 >= 9.0:
            # adim() görüntüleyici kilidi içinde çağrılır: yakalama ayrı iş parçacığında, kilit bırakıldıktan sonra
            import threading
            ana = sys.modules.get("__main__")
            yakala = getattr(ana, "pencere_yakala", None)
            if yakala is not None:
                threading.Timer(0.5, yakala, args=(self._foto,)).start()
            self._foto = None
        return self.v, self.w

    def durum(self):
        c = SON["c"]
        mod = c.demo_metin() if c is not None and getattr(c, "demo_acik", False) else "-"
        return {"poz": None, "mod": mod, "yol": [], "hedef": None, "harita": None, "ek": {}}
