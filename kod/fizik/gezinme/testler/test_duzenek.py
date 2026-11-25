"""Başsız düzenek uçtan uca testleri (MuJoCo gerekir; yoksa atlanır). ≈ 30-40 s.

    %V% -m unittest gezinme.testler.test_duzenek        (cd kod\\fizik)"""

import math
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from gezinme import _yol  # noqa: E402

try:
    import dunya as D
    FIZIK = D.FIZIK_VAR
except Exception:      # pragma: no cover
    FIZIK = False

fizik_gerekli = unittest.skipUnless(FIZIK, "mujoco yok (kod/SIMULASYON.md 'Fizik simülasyonu')")


class Kaydedici:
    """Beyin'e ne verildiğini kaydeden sarmalayıcı."""

    def __init__(self, ic):
        self.ic, self.cagri, self.tarama = ic, 0, 0
        self.izleyici = getattr(ic, "izleyici", None)

    def adim(self, t, tarama, artim):
        self.cagri += 1
        assert len(artim) == 3
        if tarama is not None:
            self.tarama += 1
            assert set(tarama) >= {"t", "acilar", "mesafeler", "artim_once", "artim_sonra"}
            assert len(tarama["mesafeler"]) == 500
        return self.ic.adim(t, tarama, artim)

    def durum(self):
        return self.ic.durum()


@fizik_gerekli
class Duzenek(unittest.TestCase):
    def test_varsayilan_varyant(self):
        from gezinme.duzenek import varsayilan_varyant
        self.assertEqual(varsayilan_varyant("koridor_5"), "ONERI")
        self.assertEqual(varsayilan_varyant("labirent_9x9_t1"), "ONERI")
        self.assertEqual(varsayilan_varyant("oda_rampa"), "V0")

    def test_odometri_beyni_duz_yol_ve_kayit(self):
        from gezinme.beyinler import OdometriBeyni
        from gezinme.duzenek import Duzenek, HedefHakemi, kayit_oku
        dz = Duzenek("koridor_5", tohum=1)
        self.assertEqual(dz.varyant_ad, "ONERI")
        hedef = (5.0, 6.2)
        b = Kaydedici(OdometriBeyni(dz.baslangic, [(1.8, 6.2), hedef]))
        h = HedefHakemi(hedef)
        yol = os.path.join(tempfile.mkdtemp(), "k.npz")
        s = dz.kos(b, 40.0, hakem=h, kayit=yol)
        self.assertIn(s["bitis"], ("hakem", "beyin"))
        self.assertLess(h.sonuc["hata_m"], 0.3)
        self.assertEqual(s["temas_olay"], 0)
        self.assertGreater(b.tarama, 50)
        self.assertGreater(b.cagri, 2 * b.tarama - 5)          # 20 Hz denetim, 10 Hz tarama
        meta, dzl = kayit_oku(yol)
        for k in ("t", "gercek", "odo", "tahmin", "komut", "olculen", "temas", "mod", "hedef", "tarama_t", "tarama_mm"):
            self.assertIn(k, dzl)
        self.assertEqual(dzl["tarama_mm"].shape[1], 500)
        self.assertEqual(meta["sahne"], "koridor_5")
        self.assertEqual(len(meta["yollar"]), 1)
        # odometri düz yolda yer gerçeğine yakın
        self.assertLess(float(abs(dzl["odo"][-1, 0] - dzl["gercek"][-1, 0])), 0.05)

    def test_engelde_durur_engel_kalkinca_devam(self):
        from gezinme.beyinler import OdometriBeyni
        from gezinme.duzenek import Duzenek, HedefHakemi
        insan = {"tur": "daire", "x": 4.0, "y": 6.2, "r": 0.2}
        dz = Duzenek("koridor_5", tohum=2, ek_engeller=[insan])
        b = OdometriBeyni(dz.baslangic, [(1.8, 6.2), (6.0, 6.2)])
        durum = {"durdu_t": None, "kalkti": None, "en_yakin": 9.0}

        def olay(d, t):
            x = d.gercek_poz()[0]
            if durum["kalkti"] is None:                         # engel yerindeyken ön yüz - engel aralığı
                durum["en_yakin"] = min(durum["en_yakin"], 4.0 - 0.2 - (x + 0.2642))
            if b.k is not None and b.k.durdu and durum["durdu_t"] is None:
                durum["durdu_t"] = t
            if durum["durdu_t"] is not None and durum["kalkti"] is None and t - durum["durdu_t"] > 3.0:
                d.engel_tasi(0, 100.0, 100.0)
                durum["kalkti"] = t
        h = HedefHakemi((6.0, 6.2))
        s = dz.kos(b, 60.0, hakem=h, olay=olay)
        self.assertIsNotNone(durum["durdu_t"])
        self.assertGreater(durum["en_yakin"], 0.15)            # 0,30 m dur mesafesi (gürültü + fren payı)
        self.assertEqual(s["temas_olay"], 0)
        self.assertLess(h.sonuc["hata_m"], 0.3)

    def test_ab_beyni_kisa(self):
        from gezinme import senaryo_ab as A
        s = A.kos(dict(id="test", koridor="koridor_2", hedef="kapi_1", tohum=1))
        self.assertTrue(s["basari"], s["neden"])
        self.assertLess(s["tahmin_hatasi_m"], 0.05)

    @unittest.skipUnless(os.path.exists(os.path.join(_yol.FIZIK, "sahneler", "labirent_5x5_t1.json")) and
                         os.path.exists(os.path.join(_yol.FIZIK, "labirent", "hakem.py")), "labirent yok")
    def test_labirent_start_ve_hakem(self):
        from gezinme.duzenek import Duzenek
        sys.path.insert(0, os.path.join(_yol.FIZIK, "labirent"))
        from hakem import Hakem

        class Ileri:
            def adim(self, t, tarama, artim):
                return 0.25, 0.0

            def durum(self):
                return {"poz": None, "mod": "ileri", "yol": [], "hedef": None, "harita": None, "ek": {}}
        dz = Duzenek("labirent_5x5_t1", sonar_acik=False)
        poz = dz.sahne["labirent"]["start"]["poz"]
        g = dz.gercek_poz()
        self.assertLess(math.hypot(g[0] - poz[0], g[1] - poz[1]), 1e-6)
        self.assertEqual(dz.varyant_ad, "ONERI")
        h = Hakem("labirent_5x5_t1", sure_siniri_s=900.0)
        s = dz.kos(Ileri(), 8.0, hakem=h)
        self.assertGreaterEqual(s["temas_olay"], 1)             # START'tan ileri: duvara dayanır
        self.assertEqual(s["temas_olay"], h.sonuc["carpma_sayisi"])

    @unittest.skipUnless(os.path.exists(os.path.join(_yol.FIZIK, "sahneler", "labirent_5x5_t1.json")) and
                         os.path.exists(os.path.join(_yol.FIZIK, "labirent", "hakem.py")), "labirent yok")
    def test_kayit_zaman_tabani_hakem_sonucu_olaylar(self):
        """Süre sınırında biten koşuda hakem sonucu (durum + döküm) kayda girer; t0_dunya_s iki saati bağlar; Beyin
        olaylarının hepsi (en çok BEYIN_OLAY_EN_COK) meta'da."""
        from gezinme.duzenek import Duzenek, kayit_oku
        sys.path.insert(0, os.path.join(_yol.FIZIK, "labirent"))
        from hakem import Hakem

        class Bekle:
            def __init__(self):
                self.olaylar = []

            def adim(self, t, tarama, artim):
                self.olaylar.append((round(t, 2), "adim", ""))
                return 0.0, 0.0

            def durum(self):
                return {"poz": None, "mod": "bekle", "yol": [], "hedef": None, "harita": None, "ek": {}}
        dz = Duzenek("labirent_5x5_t1")
        dz.e.bekle(600)                                         # dünya saati koşu başından ileride olsun
        h = Hakem("labirent_5x5_t1", sure_siniri_s=4.0)
        b = Bekle()
        yol = os.path.join(tempfile.mkdtemp(), "l.npz")
        s = dz.kos(b, 4.0, hakem=h, kayit=yol)
        self.assertEqual(s["bitis"], "hakem")
        meta, dzl = kayit_oku(yol)
        self.assertEqual(meta["hakem"]["durum"], "fail_sure")
        self.assertIn("puan_dokumu", meta["hakem"])
        self.assertEqual(meta["sonuc"]["hakem"]["durum"], "fail_sure")
        t0 = meta["t0_dunya_s"]
        self.assertGreater(t0, 0.4)
        # ilk tarama, satır saatine t0 eklenince aynı tabanda: koşu içinde
        self.assertGreaterEqual(float(dzl["tarama_t"][0]), t0 - 0.11)
        self.assertLessEqual(float(dzl["tarama_t"][-1]), t0 + float(dzl["t"][-1]) + 1e-6)
        self.assertGreater(len(b.olaylar), 8)
        self.assertEqual(len(meta["beyin_olaylari"]), len(b.olaylar))
        self.assertEqual(meta["beyin_olay_sayisi"], len(b.olaylar))


if __name__ == "__main__":
    unittest.main()
