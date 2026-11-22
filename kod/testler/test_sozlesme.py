"""Firmware 0.5.0 sözleşme ayrıntıları (B kontrolünün bozup hiçbir testin yakalamadığı davranışlar; Y0s-kontrol.md § 2).

Hepsi yalnız protokolden doğrular; fiziksel adım (`self.ortam`) gerçek kartta operatörle yapılır. Dayanaklar `origin/main`
`kod/esp32/src/` dosyalarıdır (plan bu ayrıntıları yazmıyor).
"""

import unittest

from testler.duzenek import LaleTesti

SATIR_UZUNLUGU = 200        # main seri_protokol.cpp SATIR_UZUNLUGU
I2C_YOKLAMA_MS = 100        # main guc.cpp I2C_YOKLAMA_MS
I2C_ARDISIK_HATA = 3        # main guc.cpp I2C_ARDISIK_HATA


class SatirSiniri(LaleTesti):

    def test_200_bayt_kabul_201_red(self):
        """Dayanak: main seri_protokol.cpp SATIR_UZUNLUGU = 200 ("bir komut satırı en çok bu kadar bayt"; satir_boy < 200 iken saklanır, fazlası satir_tasti)."""
        def satir(n):
            bas, son = b'{"k":"ping","x":"', b'"}'
            return bas + b"a" * (n - len(bas) - len(son)) + son
        self.assertEqual(len(satir(SATIR_UZUNLUGU)), SATIR_UZUNLUGU)
        c = self.esp.ham_istek(satir(SATIR_UZUNLUGU) + b"\n", k="ping")
        self.assertIs(c["ok"], True, "200 baytlık satır reddedildi")
        c = self.esp.ham_istek(satir(SATIR_UZUNLUGU + 1) + b"\n", k=None)
        self.hata_bekle(c, "satir_cok_uzun")
        self.assertNotIn("k", c)
        c = self.esp.ham_istek(satir(SATIR_UZUNLUGU) + b"\r\n", k="ping")     # \r sayılmaz
        self.assertIs(c["ok"], True)


class OlaySirasi(LaleTesti):

    def _sira(self, bas, k, guc):
        tur = [(i, m) for i, (_, m) in enumerate(self.esp.gelen[bas:])]
        cevap = next(i for i, m in tur if m.get("k") == k and "ok" in m)
        olay = next(i for i, m in tur if m.get("k") == "guc" and "ok" not in m and m.get("guc") == guc)
        return cevap, olay

    def test_guc_olayi_komut_cevabindan_sonra(self):
        """Dayanak: main seri_protokol.cpp satır 276 "komut gücü değiştirdiyse olay cevaptan SONRA gider"; guc.h guc_olay_gonder; seri_protokol.h GÜÇ OLAYI."""
        bas = len(self.esp.gelen)
        self.esp.arm()
        self.esp.bekle(30)
        cevap, olay = self._sira(bas, "arm", "onsarj")
        self.assertLess(cevap, olay, "onsarj olayı arm cevabından önce geldi")
        self.guc_olayi_bekle("devrede", 1500)
        bas = len(self.esp.gelen)
        self.esp.istek({"k": "birak"})
        self.esp.bekle(30)
        cevap, olay = self._sira(bas, "birak", "birakik")
        self.assertLess(cevap, olay, "birakik olayı birak cevabından önce geldi")


class KorumaArizalari(LaleTesti):

    def test_i2c_kopunca_ariza(self):
        """Dayanak: main guc.cpp "PCA9685 yoklaması (yalnız devredeyken): 100 ms'de bir I2C adres yoklaması, art arda 3 cevapsız -> bırak" (arizaya_gec "i2c")."""
        devrede = self.devreye_al()
        self.esp.ping()
        bas = len(self.esp.gelen)
        t0 = self.esp.ping()["ms"]
        self.ortam.i2c(False)
        olay = self.guc_olayi_bekle("ariza", 1000, bas=bas)
        self.assertEqual(olay["neden"], "i2c")
        gecen = olay["ms"] - t0
        self.assertGreaterEqual(gecen, (I2C_ARDISIK_HATA - 1) * I2C_YOKLAMA_MS - self.tol)
        self.assertLessEqual(gecen, I2C_ARDISIK_HATA * I2C_YOKLAMA_MS + self.tol + 20)
        self.ortam.i2c(True)
        self.assertGreater(olay["ms"], devrede["ms"])
        self.hata_bekle(self.esp.sur(0.1, 0.0), "devrede_degil", "sur")

    def test_devredeyken_bara_gidince_ariza_ve_aku_null(self):
        """Dayanak: main guc.cpp devrede_denetle "k1_cekili && !guc_bara_gerilimli() -> arizaya_gec(bara_gitti)"; aku_olc AKU_YOK_V 1.0 ("ana anahtar kapalı") -> seri_protokol.cpp aku null."""
        self.devreye_al()
        self.assertIsInstance(self.esp.ping()["aku"], (int, float))
        bas = len(self.esp.gelen)
        self.ortam.ana_anahtar(False)
        olay = self.guc_olayi_bekle("ariza", 200, bas=bas)
        self.assertEqual(olay["neden"], "bara_gitti")
        p = self.esp.ping()
        self.assertIsNone(p["aku"], "ana anahtar kapalıyken aku ölçümü var")
        self.assertFalse(p["bara"])
        self.ortam.ana_anahtar(True)
        self.assertIsInstance(self.esp.ping()["aku"], (int, float))


class Odometri(LaleTesti):

    def test_odo_sifirla_tikleri_sifirlar(self):
        """Dayanak: main seri_protokol.h {"k":"odo_sifirla"} "iki enkoder tik toplamını sıfırla"; motorlar.cpp sol_enk.toplam = 0."""
        self.devreye_al()
        self.esp.sur_tut(0.3, 0.0, 1000)
        self.esp.istek({"k": "dur"})
        self.esp.bekle(400)
        once = self.odo_son()
        self.assertGreater(once["sol"], 100)
        self.assertTrue(self.esp.istek({"k": "odo_sifirla"})["ok"])
        odo = self.esp.bekle_kosul(lambda m: m.get("k") == "odo", 300)
        self.assertEqual((odo["sol"], odo["sag"]), (0, 0), "odo_sifirla tikleri sıfırlamadı")
        self.esp.sur_tut(0.2, 0.0, 600)
        sonra = self.odo_son()
        self.assertGreater(sonra["sol"], 0)
        self.assertLess(sonra["sol"], once["sol"])


class JestYonu(LaleTesti):

    def test_yon_uygulandi_yalniz_varyanti_olan_jestte(self):
        """Dayanak: main jestler.h "Jestin o yön için varyantı yoksa varsayılan kareler oynar ve yon_uygulandi = false olur"; jest_verisi.h JEST_TABLOSU (yalnız "isaret" dört yön varyantlı)."""
        for ad, yon, beklenen in (("isaret", "sol", True), ("isaret", "arka", True), ("selam", "sol", False),
                                  ("evet", "ileri", False)):
            with self.subTest(ad=ad, yon=yon):
                c = self.esp.istek({"k": "jest", "ad": ad, "yon": yon})
                self.assertTrue(c["ok"], c)
                self.assertEqual(c["yon"], yon)
                self.assertIs(c["yon_uygulandi"], beklenen)
        c = self.esp.istek({"k": "jest", "ad": "selam"})
        self.assertNotIn("yon_uygulandi", c)


if __name__ == "__main__":
    unittest.main()
