"""jest_uret.py testleri. Çalıştırma (depo kökünden): py -3 -m pytest kod/jestler -q"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jest_uret as ju  # noqa: E402


def _kanallar():
    return ju.kanallari_oku()[1]


def test_depodaki_baslik_guncel():
    # YAML değişip betik çalıştırılmadıysa ESP32 eski jestleri oynar; bunu yakala.
    metin, _, _ = ju.uret()
    assert ju.CIKTI.read_text(encoding="utf-8") == metin


def test_bosta_tum_kanallari_yazar_ve_sinirlar_icinde():
    kanallar = _kanallar()
    _, bosta, _ = ju.jestleri_oku(kanallar)
    for k, aci in zip(kanallar, bosta):
        assert k["min_aci"] <= aci <= k["max_aci"], k["ad"]


def test_ara_kare_dogrusal_doldurulur(tmp_path):
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n"
        "  - {ms: 0, kafa_pan: 60}\n"
        "  - {ms: 500}\n"
        "  - {ms: 1000, kafa_pan: 120}\n", encoding="utf-8")
    _, _, kareler, _ = ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())
    sira = [k["ad"] for k in _kanallar()].index("kafa_pan")
    assert [round(satir[sira], 1) for _, satir in kareler] == [60.0, 90.0, 120.0]
    # jestte geçmeyen kanal "dokunma" olarak kalır
    assert kareler[0][1][0] == ju.ACI_YOK


@pytest.mark.parametrize("icerik, parca", [
    ("ad: deneme\nkareler:\n  - {ms: 0, kafa_tilt: 150}\n", "sınır dışı"),
    ("ad: deneme\nkareler:\n  - {ms: 0, kuyruk: 10}\n", "bilinmeyen kanal"),
    ("ad: deneme\nkareler:\n  - {ms: 500, kafa_pan: 90}\n  - {ms: 100, kafa_pan: 80}\n", "büyük olmalı"),
    ("ad: deneme\nkareler:\n  - {ms: 0, kafa_pan: 90}\n  - {ms: 500, kafa_tilt: 80}\n", "ilk karede eksik"),
    ("ad: baska\nkareler:\n  - {ms: 0, kafa_pan: 90}\n", "dosya adıyla"),
])
def test_hatali_jest_reddedilir(tmp_path, icerik, parca):
    (tmp_path / "deneme.yaml").write_text(icerik, encoding="utf-8")
    with pytest.raises(ju.JestHatasi, match=parca):
        ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())


def test_cok_hizli_hareket_uyarir(tmp_path):
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n  - {ms: 0, kafa_pan: 45}\n  - {ms: 100, kafa_pan: 135}\n", encoding="utf-8")
    _, _, _, uyarilar = ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())
    assert uyarilar and "kafa_pan" in uyarilar[0]
