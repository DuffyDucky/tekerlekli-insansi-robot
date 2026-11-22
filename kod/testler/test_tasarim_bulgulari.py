"""BİLİNEN DAVRANIŞ / TASARIM SORUSU senaryoları (güvenlik testi DEĞİL).

Bu testler bir kuralı doğrulamaz; simülasyonun gösterdiği bir tasarım sonucunu yeniden üretir. GEÇMELERİ SORUNUN VAR OLDUĞUNU
gösterir. Tasarım değişirse (ör. arka sonar eklenir, yerinde dönüş engel varken kısıtlanır) ilgili test kalır ve o zaman
güncellenir ya da silinir. Model bunları gizleyecek biçimde değiştirilmez (Y0s-gunluk.md § 11 E10; kod/SIMULASYON.md
"Simülasyonun gösterdiği tasarım bulguları").

Hep bellek içi sahte kartla koşar (LALE_HEDEF'ten bağımsız): sonuçları hakeme (çarpışma sayısı) dayanır ve belirlenimcidir.
"""

import math
import unittest

from sahte_esp32.cekirdek import SahteEsp32
from sahte_esp32.harita import Harita
from sahte_esp32.tasima import BellekTasima
from lale_pi.istemci import Esp32Istemci
from testler.duzenek import TIK_M

BILINEN_DAVRANIS = True     # kos.py --liste bu dosyayı ayrı başlıkta gösterir


class TasarimBulgusu(unittest.TestCase):

    def kur(self, harita, x, y, aci_derece):
        self.c = SahteEsp32(Harita.dosyadan(harita), konum=(x, y, math.radians(aci_derece)))
        self.esp = Esp32Istemci(BellekTasima(self.c), kayit_boyu=10 ** 5)
        self.esp.baglan()
        self.assertEqual(self.esp.devreye_al_ve_bekle()["guc"], "devrede")

    def engele_sur(self, v=0.3):
        bas = len(self.esp.gelen)
        self.esp.sur_tut(v, 0.0, 14000, dur_kosul=lambda e: any(
            m.get("k") == "engel" and m.get("var") for _, m in e.gelen[bas:]))
        self.esp.sur_tut(v, 0.0, 1000)
        self.assertTrue(self.c.engel, "engel oluşmadı (senaryo kurgusu)")

    def test_a_arkada_sonar_yok_geri_giderken_duvara_carpar(self):
        """Bilinen davranış (a): arkada sonar yok (robot_parametreleri.json sonarlar: üçü de ön); geri sürüşte koruma yok (protokol.json guvenlik.sonar_dur_cm "geri serbest")."""
        self.kur("oda_bos", 1.0, 2.5, 0.0)            # arka yüz x ≈ 0,74; arka duvar x = 0
        bas = len(self.esp.gelen)
        self.esp.sur_tut(-0.2, 0.0, 6000)
        self.assertGreaterEqual(self.c.carpisma_sayisi, 1, "geri giderken çarpmadı (tasarım değişmiş olabilir)")
        self.assertEqual(self.esp.mesajlar("engel", bas), [], "geri giderken engel olayı geldi")
        self.assertEqual(self.esp.ping()["guc"], "devrede", "çarpışma kartça fark edilmiyor (beklenen)")

    def test_b_engel_varken_yerinde_donuste_kose_duvara_carpar(self):
        """Bilinen davranış (b): engel varken yerinde dönüş serbest (protokol.json guvenlik, TASLAK); taban köşesi yarıçapı ≈ 0,37 m > 30 cm durma mesafesi."""
        self.kur("oda_bos", 5.0, 0.8, 68.0)           # doğu duvarına 22° ile yaklaş (sağ sonar durdurur)
        self.engele_sur()
        self.assertEqual(self.c.carpisma_sayisi, 0, "dönmeden önce çarptı (senaryo kurgusu)")
        self.esp.sur_tut(0.0, 0.8, 4000)
        self.assertGreaterEqual(self.c.carpisma_sayisi, 1, "yerinde dönüşte çarpmadı (tasarım değişmiş olabilir)")

    def test_c_engel_varken_30_35_cm_arasinda_surunur(self):
        """Bilinen davranış (c): hız sınırı histerezissiz (d ≥ 30 cm -> en az 0,05 m/s, TASLAK) ama `engel` 35 cm'ye kadar var kalır."""
        self.kur("oda_bos", 3.0, 2.5, 0.0)
        self.engele_sur()
        self.c.konum_ayarla(self.c.x - 0.03, self.c.y, self.c.aci)   # 3 cm geri koy: ölçüm 30–35 cm, engel hâlâ var
        self.esp.bekle(200)
        bas = len(self.esp.gelen)
        self.esp.sur_tut(0.3, 0.0, 1500)
        engel = self.esp.mesajlar("engel", bas)
        self.assertEqual(engel, [], "engel olayı değişti (senaryo kurgusu)")
        self.assertTrue(self.c.engel)
        odo = self.esp.mesajlar("odo", bas)
        yol = (odo[-1]["sol"] - odo[0]["sol"]) * TIK_M
        self.assertGreater(yol, 0.01, "engel varken ilerlemedi (sürünme yok: tasarım değişmiş olabilir)")
        self.assertEqual(self.c.carpisma_sayisi, 0)
        self.assertLess(min(v for v in self.c.sonar.values() if v is not None), 30.0, "sürünme 30 cm'de bitmedi")

    def test_d_yanlamasina_yaklasimda_ilerlerken_kose_surtunur(self):
        """Ek bulgu (d): duvara ~20°'den dar açıyla (neredeyse paralel) yaklaşınca ön sonarlar yankı almaz (> 60° geliş, TAHMİN) ve taban köşesi ileri sürüşte duvara değer."""
        self.kur("oda_bos", 5.0, 0.8, 74.0)
        bas = len(self.esp.gelen)
        self.esp.sur_tut(0.3, 0.0, 12000)
        self.assertGreaterEqual(self.c.carpisma_sayisi, 1, "sürtünmedi (tasarım / model değişmiş olabilir)")
        self.assertFalse([m for m in self.esp.mesajlar("engel", bas) if m["var"]], "engel geldi (senaryo kurgusu)")

    def test_e_iz_farki_odometri_360_derece_gercekte_355(self):
        """Bilinen fark (Ç3): firmware ve Pi odometrisi iz 0,426 m (main motorlar.cpp, ayarlar.yaml), CAD izi 0,432 m. Pi odometrisiyle 360° yerinde dönünce gerçek dönüş ≈ 355°."""
        self.kur("oda_bos", 3.0, 2.5, 0.0)
        a0 = self.c.aci
        o0 = self.esp.son["odo"] if "odo" in self.esp.son else {"sol": 0, "sag": 0}

        def odo_aci():
            o = self.esp.son["odo"]
            return ((o["sag"] - o0["sag"]) - (o["sol"] - o0["sol"])) * TIK_M / 0.426

        while odo_aci() < 2 * math.pi:                # Pi'nin yapacağı gibi: odometri 360° diyene kadar dön
            self.esp.sur(0.0, 0.5)
            self.esp.bekle(100)
        self.esp.istek({"k": "dur"})
        self.esp.bekle(600)
        pi_derece = math.degrees(odo_aci())
        gercek_derece = math.degrees(self.c.aci - a0)
        self.assertAlmostEqual(gercek_derece / pi_derece, 0.426 / 0.432, places=3)
        self.assertAlmostEqual(gercek_derece - pi_derece, -5.0 * pi_derece / 360.0, delta=0.2)
        self.olcum = (pi_derece, gercek_derece)
        print("\n    iz farkı: Pi odometrisi %.1f°, gerçek %.1f° (fark %.1f°)" % (pi_derece, gercek_derece,
                                                                           gercek_derece - pi_derece), end=" ")


if __name__ == "__main__":
    unittest.main()
