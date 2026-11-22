"""Görünüm (HTTP) sağlamlığı: kötü istek pilotu öldürmez, yalnız aynı kökenden istek kabul edilir. Gerçek soket, gerçek zaman."""

import http.client
import json
import time
import unittest

from sahte_esp32.cekirdek import SahteEsp32
from sahte_esp32.gorunum import Gorunum
from sahte_esp32.harita import Harita
from sahte_esp32.tcp_sunucu import TcpSunucu


class GorunumSaglamlik(unittest.TestCase):

    def setUp(self):
        self.cekirdek = SahteEsp32(Harita.dosyadan("oda_bos"))
        self.sunucu = TcpSunucu(self.cekirdek, port=0).baslat()
        self.addCleanup(self.sunucu.durdur)
        self.g = Gorunum(self.sunucu, http_port=0).baslat()
        self.addCleanup(self.g.durdur)
        self.port = self.g.http_port

    def istek(self, yontem, yol, govde=None, basliklar=None):
        b = {"Host": "127.0.0.1:%d" % self.port, "Content-Type": "application/json"}
        b.update(basliklar or {})
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            c.request(yontem, yol, body=govde, headers=b)
            r = c.getresponse()
            return r.status, r.read()
        finally:
            c.close()

    def bekle(self, kosul, sure=3.0):
        bitis = time.monotonic() + sure
        while time.monotonic() < bitis:
            if kosul():
                return True
            time.sleep(0.02)
        return False

    def hakem(self):
        with self.sunucu.kilit:
            return self.cekirdek.hakem()

    def test_kotu_surus_istegi_reddedilir_pilot_yasar(self):
        """Dayanak: Y0s-kontrol.md § 3 madde 1 ({"v":1e400} pilot iş parçacığını öldürüyordu) ve madde 3 (float(v) HTTP 500)."""
        kotuler = [b'{"v":1e400,"w":0}', b'{"v":0,"w":-1e400}', b'{"v":NaN,"w":0}', b'{"v":Infinity,"w":0}',
                   b'{"v":"hizli","w":0}', b'{"v":true,"w":0}', b'{"v":null,"w":0}', b'{"v":0.2}', b'{}',
                   b'[0.2,0]', b'"v"', b'{bozuk', b'{"v":[1],"w":0}']
        for govde in kotuler:
            with self.subTest(govde=govde):
                durum, _ = self.istek("POST", "/surus", govde)
                self.assertEqual(durum, 400)
                self.assertTrue(self.g.pilot.canli_mi(), "pilot iş parçacığı öldü")
        # içeriden gelen beklenmedik hata da öldürmez (doğrulamayı atlayıp doğrudan bozuk istek koy)
        with self.g.pilot.kilit:
            self.g.pilot.istek = (float("inf"), 0.0)
            self.g.pilot._son_istek_ms = time.monotonic()
        self.assertTrue(self.bekle(lambda: self.g.pilot.hatalar), "bozuk istek hata üretmedi")
        self.assertTrue(self.g.pilot.canli_mi())
        # sonra her şey çalışır: devreye al, sür, sayfa durumu gelir
        self.assertEqual(self.istek("POST", "/komut", b'{"k":"arm"}')[0], 200)
        self.assertTrue(self.bekle(lambda: self.hakem()["guc"] == "devrede"))
        bitis = time.monotonic() + 2.0
        while time.monotonic() < bitis and self.hakem()["v"] < 0.1:
            self.assertEqual(self.istek("POST", "/surus", b'{"v":5,"w":0}')[0], 200)    # 5 -> 1'e kırpılır
            time.sleep(0.1)
        self.assertGreater(self.hakem()["v"], 0.1)
        durum, govde = self.istek("GET", "/durum")
        self.assertEqual(durum, 200)
        self.assertTrue(json.loads(govde)["pilot"]["canli"])

    def test_yalniz_ayni_koken(self):
        """Dayanak: Y0s-kontrol.md § 3 madde 2 (Origin denetimi yok: başka site /komut'a POST atabilir)."""
        self.assertEqual(self.istek("POST", "/komut", b'{"k":"arm"}', {"Origin": "http://kotu.example"})[0], 403)
        self.assertEqual(self.istek("POST", "/surus", b'{"v":0.2,"w":0}', {"Origin": "null"})[0], 403)
        self.assertEqual(self.istek("POST", "/komut", b'{"k":"arm"}', {"Sec-Fetch-Site": "cross-site"})[0], 403)
        self.assertEqual(self.istek("GET", "/durum", None, {"Host": "kotu.example:%d" % self.port})[0], 403)
        self.assertEqual(self.istek("GET", "/durum", None, {"Host": "127.0.0.1:1"})[0], 403)
        time.sleep(0.3)
        self.assertEqual(self.hakem()["guc"], "birakik", "köken dışı arm uygulandı")
        for koken in ("http://127.0.0.1:%d" % self.port, "http://localhost:%d" % self.port):
            with self.subTest(koken=koken):
                self.assertEqual(self.istek("POST", "/surus", b'{"v":0,"w":0}',
                                            {"Origin": koken, "Sec-Fetch-Site": "same-origin"})[0], 200)
        self.assertEqual(self.istek("GET", "/", None, {"Host": "localhost:%d" % self.port})[0], 200)


if __name__ == "__main__":
    unittest.main()
