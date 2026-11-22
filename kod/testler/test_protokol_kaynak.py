"""Tek kaynağın kendisi: protokol.json ↔ plan değerleri ↔ firmware 0.5.0 tablosu ↔ belge ↔ sahte kart kodu."""

import os
import re
import subprocess
import sys
import unittest

import lale_protokol as P

KOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# main kod/esp32/src/jest_verisi.h SERVO_TABLOSU (0.5.0; min, max) — bağımsız tanık olarak elle yazıldı
FIRMWARE_SERVO = {
    "sag_omuz": (0, 180), "sag_omuz_yan": (5, 120), "sag_dirsek": (0, 105), "sag_bilek": (0, 180), "kafa_pan": (0, 180),
    "sol_omuz": (0, 180), "sol_omuz_yan": (5, 120), "sol_dirsek": (0, 105), "sol_bilek": (0, 180), "kafa_tilt": (77, 103),
}


class TekKaynak(unittest.TestCase):

    def test_plan_degerleri(self):
        """Dayanak: yazilim-plani.md mimari (500 ms, 115200, satır başına JSON), Y3 (30 cm); pin-haritasi.md Y4 (100 ms, 1 s)."""
        self.assertEqual(P.ZAMAN["bekci"], 500)
        self.assertEqual(P.GUVENLIK["sonar_dur_cm"], 30)
        self.assertEqual(P.CERCEVE["baud"], 115200)
        self.assertEqual(P.CERCEVE["satir_sonu"], "\n")
        self.assertEqual(P.ZAMAN["k1_sonrasi"], 100)
        self.assertEqual(P.ZAMAN["k2_en_cok"], 1000)
        self.assertEqual(P.ZAMAN["sessizlik"], 5000)   # main guc.h

    def test_her_oge_kaynakli_ve_isaretli(self):
        """Dayanak: brief / Y0s-gunluk § 2 (plandan gelen ile TASLAK ayrılır, her öğenin kaynağı yazılı)."""
        J = P.PROTOKOL
        for bolum in ("zamanlar_ms", "sinirlar", "guvenlik", "komutlar", "mesajlar"):
            for ad, d in J[bolum].items():
                with self.subTest(oge="%s.%s" % (bolum, ad)):
                    self.assertTrue(d.get("kaynak"), "kaynak yok")
                    self.assertIsInstance(d.get("taslak"), bool)
                    if "TASLAK" in d["kaynak"]:
                        self.assertTrue(d["taslak"], "kaynakta TASLAK yazıyor ama işaret yok")
        for bolum in ("cerceve", "guc_durumlari", "ariza_nedenleri", "genel_hatalar", "servolar", "jestler"):
            self.assertTrue(J[bolum].get("kaynak"))
            self.assertIs(J[bolum].get("taslak"), False)

    def test_servo_sinirlari_eklem_kaynagindan_ve_firmware_ile_ayni(self):
        """Dayanak: yazilim-plani.md "Eklem sınırları tek kaynaktan gelir (eklem_sinirlari.json) ... elle iki yerde yazılmaz"."""
        tablo = {t["ad"]: (t["min"], t["max"]) for t in P.servo_tablosu()}
        self.assertEqual(tablo, {k: (float(a), float(b)) for k, (a, b) in FIRMWARE_SERVO.items()})
        self.assertEqual([t["kanal"] for t in P.servo_tablosu()], list(range(10)))

    def test_parametreler_kaynakli_ya_da_tahmin(self):
        """Dayanak: brief "Robot parametreleri ... kaynağı yazsın; bulamadığını TAHMİN diye işaretle"."""
        for ad, p in P.PARAMETRELER["parametreler"].items():
            with self.subTest(parametre=ad):
                self.assertIn(p.get("durum"), ("kaynakli", "TAHMIN"))
                self.assertTrue(p.get("kaynak"))
        iv = P.ivme_sinirlari()
        self.assertEqual(P.parametre("ivme_duz_surus_m_s2"), iv["duz_surus"])
        self.assertEqual(P.parametre("ivme_duz_fren_m_s2"), iv["duz_fren"])
        self.assertEqual(P.parametre("ivme_rampa_surus_m_s2"), iv["rampa_surus"])
        self.assertEqual(P.parametre("ivme_rampa_fren_m_s2"), iv["rampa_fren"])

    def test_sahte_kartin_hata_adlari_protokolde(self):
        """Dayanak: kod/ortak/protokol.json (sahte kart sözleşme dışı hata adı söyleyemez)."""
        kaynak = open(os.path.join(KOD, "araclar", "sahte_esp32", "cekirdek.py"), encoding="utf-8").read()
        for k, hata in re.findall(r'_hata\("(\w+)", "(\w+)"\)', kaynak):
            with self.subTest(k=k, hata=hata):
                self.assertIn(hata, P.KOMUTLAR[k]["hatalar"])
        for hata in re.findall(r'"hata": "(\w+)"', kaynak):
            self.assertIn(hata, P.GENEL_HATALAR)
        for neden in re.findall(r'_arizaya_gec\("(\w+)"', kaynak):
            self.assertIn(neden, P.ARIZA_NEDENLERI)
        for k in P.KOMUTLAR:
            self.assertIn("def _k_%s(" % k, kaynak, "komutun işleyicisi yok: %s" % k)

    def test_belge_guncel(self):
        """Dayanak: kod/ortak/PROTOKOL.md protokol.json'dan üretilir (elle düzenlenmez)."""
        r = subprocess.run([sys.executable, os.path.join(KOD, "ortak", "protokol_belge_uret.py"), "--denetle"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_kodla_coz(self):
        """Dayanak: yazilim-plani.md mimari "satır başına bir JSON mesajı"; main seri.py komut_satiri (boşluksuz)."""
        b = P.kodla({"k": "sur", "v": 0.2, "w": 0.0})
        self.assertEqual(b, b'{"k":"sur","v":0.2,"w":0.0}\n')
        self.assertEqual(P.coz(b[:-1]), {"k": "sur", "v": 0.2, "w": 0.0})
        with self.assertRaises(P.BozukSatir):
            P.coz(b'{"k":"sur","v":NaN}')
        self.assertTrue(P.tur_uyar(1, "sayi"))
        self.assertFalse(P.tur_uyar(True, "sayi"))
        self.assertFalse(P.tur_uyar(float("inf"), "sayi"))


if __name__ == "__main__":
    unittest.main()
