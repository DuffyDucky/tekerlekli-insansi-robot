"""pin_uret.py testleri. Çalıştırma (depo kökünden): py -3 -m pytest kod/ortak -q"""

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pin_uret as pu  # noqa: E402


def _veri():
    return copy.deepcopy(pu.pinleri_oku())


def test_depodaki_baslik_guncel():
    # pinler.json değişip betik çalıştırılmadıysa firmware eski pinlerle derlenir; bunu yakala.
    assert pu.CIKTI.read_text(encoding="utf-8") == pu.uret()


def test_kontrol_guncelken_0_doner():
    assert pu.main(["--kontrol"]) == 0


def test_kontrol_eskiyse_1_doner(tmp_path, monkeypatch):
    eski = tmp_path / "pinler.h"
    eski.write_text("// eski\n", encoding="utf-8")
    monkeypatch.setattr(pu, "CIKTI", eski)
    assert pu.main(["--kontrol"]) == 1
    assert eski.read_text(encoding="utf-8") == "// eski\n"        # --kontrol yazmaz


def test_hatali_json_2_doner(tmp_path, monkeypatch):
    bozuk = tmp_path / "pinler.json"
    bozuk.write_text("{", encoding="utf-8")
    monkeypatch.setattr(pu, "GIRDI", bozuk)
    assert pu.main(["--kontrol"]) == 2


def test_baslik_icerigi():
    metin = pu.uret()
    for satir in ("#define PIN_HARITASI_SURUM 4", "#define PCA9685_ADRES 0x40",
                  "#define PCA_KANAL_SONAR_SAG_TRIG 10", "#define PCA_KANAL_SONAR_ORTA_TRIG 11",
                  "#define PCA_KANAL_SONAR_SOL_TRIG 12", "#define ARM_ONSARJ_BEKLEME_MS 500",
                  "#define ARM_K1_SONRASI_MS 100", "#define ARM_K2_EN_COK_MS 1000"):
        assert satir in metin
    # rapor §2 kesin tablosundaki ana pinler
    beklenen = {"ROLE_K1": 4, "ROLE_K2_ONSARJ": 19, "BTS_EN": 13, "SOL_ILERI_PWM": 25, "SOL_GERI_PWM": 26,
                "SAG_ILERI_PWM": 27, "SAG_GERI_PWM": 14, "ACIL_STOP_DURUM": 23, "BARA_DURUM": 5,
                "SOL_ENK_A": 18, "SOL_ENK_B": 17, "SAG_ENK_A": 16, "SAG_ENK_B": 15,
                "SOL_IS": 32, "SAG_IS": 33, "AKU_ADC": 36}
    for ad, gpio in beklenen.items():
        assert any(s.split()[:3] == ["#define", f"PIN_{ad}", str(gpio)] for s in metin.splitlines()), ad
    assert metin.isascii()
    assert "GPIO12: BOS" in metin


def test_cikti_belirlenimci():
    assert pu.uret() == pu.uret()


@pytest.mark.parametrize("degistir, parca", [
    (lambda v: v["pinler"]["SOL_ENK_A"].update(gpio=17), "iki kez"),
    (lambda v: v["pinler"]["SOL_ENK_A"].update(gpio=7), "flaş"),
    (lambda v: v["pinler"]["SOL_ENK_A"].update(gpio=12), "strapping"),
    (lambda v: v["pinler"]["SOL_ENK_A"].update(gpio=24), "ESP32'de yok"),
    (lambda v: v["pinler"]["SOL_ENK_A"].update(yon="cikis"), "çıkış olamaz"),
    (lambda v: v["pinler"]["SONAR_SOL_ECHO"].update(yon="pwm"), "çıkış olamaz"),
    (lambda v: v["pinler"]["SONAR_SOL_ECHO"].update(yon="giris_pullup"), "pull-up yok"),
    (lambda v: v["pinler"]["SOL_ENK_A"].update(yon="cift"), "bilinmiyor"),
    (lambda v: v["pinler"].update(kucuk_ad={"gpio": 0, "yon": "giris"}), "geçersiz pin adı"),
    (lambda v: v["i2c"].update(PCA9685="kirk"), "onaltılık"),
    (lambda v: v["pca9685_kanallar"].pop("11"), "sonar_orta_trig"),
    (lambda v: v["arm"].update(k2_en_cok_ms=1500), "en çok 1000"),
    (lambda v: v["arm"].update(onsarj_bekleme_ms=950), "kısa olmalı"),
    (lambda v: v["arm"].update(k1_sonrasi_ms=0), "pozitif"),
    (lambda v: v["pinler"]["ROLE_K2_ONSARJ"].update(en_cok_ms=900), "aynı olmalı"),
    (lambda v: v.pop("arm"), "'arm' bölümü yok"),
])
def test_denetim_hatalari(degistir, parca):
    veri = _veri()
    degistir(veri)
    with pytest.raises(pu.PinHatasi, match=parca):
        pu.denetle(veri)


def test_role_pinleri_izinli_ciktida():
    # Röleler ve EN yalnız açılışta kendiliğinden LOW kalan, varsayılan çevre biriminin sürmediği pinlerde.
    veri = _veri()
    for ad in ("ROLE_K1", "ROLE_K2_ONSARJ", "BTS_EN"):
        assert veri["pinler"][ad]["gpio"] in pu.CIKIS_IZINLI
        assert veri["pinler"][ad]["acilis"] == 0
