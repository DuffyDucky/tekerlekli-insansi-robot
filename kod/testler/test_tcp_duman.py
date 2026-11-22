"""Gerçek TCP üzerinden duman testleri (sanal seri hat; gerçek zaman). LALE_HEDEF'ten bağımsız hep TCP."""

import socket
import time
import unittest

from sahte_esp32.cekirdek import SahteEsp32
from sahte_esp32.harita import Harita
from sahte_esp32.tcp_sunucu import TcpSunucu
from lale_pi.istemci import Esp32Istemci
from lale_pi.tasima import TcpTasima


class TcpDuman(unittest.TestCase):

    def setUp(self):
        self.cekirdek = SahteEsp32(Harita.dosyadan("oda_bos"))
        self.sunucu = TcpSunucu(self.cekirdek, port=0).baslat()
        self.addCleanup(self.sunucu.durdur)
        self.esp = Esp32Istemci(TcpTasima(port=self.sunucu.port))
        self.esp.baglan()
        self.addCleanup(self.esp.kapat)

    def tearDown(self):
        self.assertEqual(self.esp.sema_hatalari, [])

    def hakem(self):
        with self.sunucu.kilit:
            return self.cekirdek.hakem()

    def test_ping_ve_surum(self):
        """Dayanak: yazilim-plani.md Y0 kabul testi "Pi ile ESP32 hb / st alışverişi yapıyor" (0.5.0: ping / odo)."""
        p = self.esp.ping()
        self.assertTrue(p["ok"])
        self.assertTrue(p["surum"].startswith("0.5.0"))
        odo = self.esp.bekle_kosul(lambda m: m.get("k") == "odo", 1000)
        self.assertIn("sol", odo)

    def test_devreye_al_sur_odo_artar(self):
        """Dayanak: yazilim-plani.md H4 taşı "Pi ↔ ESP32 protokolü çalışıyor"; pin-haritasi.md Y4."""
        olay = self.esp.devreye_al_ve_bekle(3000)
        self.assertEqual(olay["guc"], "devrede")
        self.esp.sur_tut(0.3, 0.0, 1500)
        self.esp.bekle(150)
        self.assertGreater(self.esp.son["odo"]["sol"], 100)
        self.assertGreater(self.hakem()["v"], 0.2)

    def test_bozuk_satir(self):
        """Dayanak: main seri_protokol.cpp (json_bozuk, satir_cok_uzun) gerçek soket üzerinde."""
        c = self.esp.ham_istek(b"{bozuk\n", k=None)
        self.assertEqual(c["hata"], "json_bozuk")
        c = self.esp.ham_istek(b'{"k":"ping","x":"' + b"a" * 300 + b'"}\n', k=None)
        self.assertEqual(c["hata"], "satir_cok_uzun")
        self.assertTrue(self.esp.ping()["ok"])

    def test_soket_kapaninca_durur(self):
        """Dayanak: yazilim-plani.md Y1 kabul testi "kablo çekilince 500 ms içinde duruyor" (gerçek zamanda, pay 150 ms)."""
        self.esp.devreye_al_ve_bekle(3000)
        self.esp.sur_tut(0.3, 0.0, 1200)
        self.esp.sur(0.3, 0.0)
        t0 = time.monotonic()
        self.esp.kapat()
        while self.hakem()["v"] > 0 and time.monotonic() - t0 < 2.0:
            time.sleep(0.005)
        gecen_ms = (time.monotonic() - t0) * 1000
        self.assertEqual(self.hakem()["v"], 0.0)
        self.assertLess(gecen_ms, 500 + 150)
        self.assertGreater(gecen_ms, 500 - 150)

    def test_yeni_baglanti_reset_yapmaz(self):
        """Dayanak: yazilim-plani.md "Seri port DTR/RTS kapalı açılır (E3)": port açılışı kartı resetlemez, güç durumu korunur."""
        self.esp.devreye_al_ve_bekle(3000)
        self.esp.kapat()
        e2 = Esp32Istemci(TcpTasima(port=self.sunucu.port))
        e2.baglan()
        self.addCleanup(e2.kapat)
        p = e2.ping()
        self.assertEqual(p["guc"], "devrede")
        self.assertFalse(any(m.get("k") == "hazir" for _, m in e2.gelen))

    def test_tek_istemci(self):
        """Dayanak: seri hat noktadan noktaya (yazilim-plani.md mimari "USB ... ESP32 CP2102"); yeni bağlantı eskisini kapatır."""
        s2 = socket.create_connection(("127.0.0.1", self.sunucu.port), timeout=2)
        self.addCleanup(s2.close)
        s2.sendall(b'{"k":"ping"}\n')
        s2.settimeout(2)
        veri = b""
        while b'"k":"ping"' not in veri:
            veri += s2.recv(4096)
        self.esp.bekle(100)
        self.assertFalse(self.esp.tasima.acik_mi(), "eski bağlantı kapanmadı")


if __name__ == "__main__":
    unittest.main()
