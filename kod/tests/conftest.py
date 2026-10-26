# Testlerin "from robot..." ve "import ana" yazabilmesi için kod/ klasörünü arama yoluna ekler.
# Ortak örnek içerik paketi de burada (dosyadan bağımsız, sonuçları sabit).

import os
import sys

import pytest

KOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, KOD)

from robot.icerik import IcerikPaketi  # noqa: E402

ORNEK = {
    "kurum": "Deneme Okulu",
    "rol": "karşılama robotu",
    "selamlama": "Merhaba, hoş geldiniz!",
    "konular": [
        {"baslik": "Laboratuvar", "anahtarlar": ["laboratuvar", "lab"],
         "cevap": "Laboratuvar ikinci katta.", "jest": "isaret"},
        {"baslik": "Kayıt", "anahtarlar": ["kayıt"], "cevap": "Kayıtlar sekreterlikte yapılır."},
        {"baslik": "Ulaşım", "anahtarlar": ["otobüs", "ulaşım"], "cevap": "Otobüsle gelebilirsiniz."},
    ],
    "yerler": [{"ad": "Kantin", "tarif": "Kantin giriş katında."}],
    "sss": [{"soru": "Internet var mı?", "anahtarlar": ["internet", "wifi"], "cevap": "Evet, kablosuz ağ var."}],
}


@pytest.fixture
def paket():
    return IcerikPaketi(ORNEK, esik=3)
