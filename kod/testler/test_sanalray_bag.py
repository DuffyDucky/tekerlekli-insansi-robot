"""Sanal ray (kod/fizik/sanalray) birim testlerini `kos.py` koşusuna bağlar (yalnız ekleme).

Bu dosya kendi test içermez; `load_tests` ile `sanalray.testler.test_sanalray` ve `test_dayaniklilik` modüllerini
yükler. numpy / cv2 / MuJoCo yoksa o testler kendi `skipUnless` koşullarıyla atlanır; modüller hiç yüklenemezse tek
bir atlanan test görünür, koşu kırılmaz."""

import os
import sys
import unittest

FIZIK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fizik")


def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()
    if FIZIK not in sys.path:
        sys.path.append(FIZIK)
    try:
        from sanalray.testler import test_dayaniklilik, test_sanalray
    except Exception as h:           # noqa: BLE001  (bağlantı testi: yükleme hatası atlanır, gizlenmez)
        neden = "sanalray testleri yüklenemedi: %r" % (h,)

        class SanalrayYuklenemedi(unittest.TestCase):
            def test_sanalray_yuklenemedi(self):
                self.skipTest(neden)
        suite.addTest(SanalrayYuklenemedi("test_sanalray_yuklenemedi"))
        return suite
    for m in (test_sanalray, test_dayaniklilik):
        suite.addTests(loader.loadTestsFromModule(m))
    return suite
