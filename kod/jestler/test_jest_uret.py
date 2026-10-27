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
    _, _, kareler, _, _ = ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())
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
    _, _, _, uyarilar, _ = ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())
    assert uyarilar and "kafa_pan" in uyarilar[0]


# --------------------------- yönlü jestler (27 Ekim 2026) ---------------------------

def _sutun(ad):
    return [k["ad"] for k in _kanallar()].index(ad)


def _kanal_dosyasi(tmp_path, pan_max=135, pan_ayna="kafa_pan", sol_ayna="sag_omuz"):
    """Deneme için küçük kanal tablosu (sağ/sol omuz + kafa_pan)."""
    yol = tmp_path / "kanallar_deneme.yaml"
    yol.write_text(
        "kanallar:\n"
        "  sag_omuz: {kanal: 0, model: X, min_us: 500, max_us: 2500, min_aci: 0, max_aci: 160, hiz: 90,"
        " ayna: sol_omuz, ayna_aci: ayni}\n"
        "  sol_omuz: {kanal: 2, model: X, min_us: 500, max_us: 2500, min_aci: 0, max_aci: 160, hiz: 90,"
        f" ters: true, ayna: {sol_ayna}, ayna_aci: ayni}}\n"
        f"  kafa_pan: {{kanal: 4, model: X, min_us: 500, max_us: 2500, min_aci: 45, max_aci: {pan_max},"
        f" hiz: 90, ayna: {pan_ayna}, ayna_aci: 180-aci}}\n", encoding="utf-8")
    return yol


def test_depodaki_ayna_esleme_karsilikli():
    tablo = {k["ad"]: k for k in _kanallar()}
    assert tablo["sag_omuz"]["ayna"] == "sol_omuz" and tablo["sol_omuz"]["ayna"] == "sag_omuz"
    assert tablo["sag_dirsek"]["ayna"] == "sol_dirsek" and tablo["sol_dirsek"]["ayna"] == "sag_dirsek"
    assert (tablo["kafa_pan"]["ayna"], tablo["kafa_pan"]["ayna_aci"]) == ("kafa_pan", "180-aci")
    assert (tablo["kafa_tilt"]["ayna"], tablo["kafa_tilt"]["ayna_aci"]) == ("kafa_tilt", "ayni")
    # sol kol servoları ters takılı: robot açısı aynı kalsın diye kol aynası "ayni" olabiliyor
    assert tablo["sol_omuz"]["ters"] and not tablo["sag_omuz"]["ters"]


def test_ayna_kanal_ve_aci_donusumu():
    kanallar = _kanallar()
    ham = [{"ms": 0, "sag_omuz": 10, "sag_dirsek": 15, "kafa_pan": 70, "kafa_tilt": 85}]
    assert ju.ayna_kareler(ham, kanallar) == [
        {"ms": 0, "sol_omuz": 10, "sol_dirsek": 15, "kafa_pan": 110, "kafa_tilt": 85}]
    # iki kez ayna = kendisi
    assert ju.ayna_kareler(ju.ayna_kareler(ham, kanallar), kanallar) == ham


def test_isaret_yon_varyantlari():
    kanallar = _kanallar()
    jestler, _, _ = ju.jestleri_oku(kanallar)
    _, _, varsayilan, yonler = next(j for j in jestler if j[0] == "isaret")
    assert list(yonler) == ["sol", "sag", "ileri", "arka"]       # YONLER sırası
    assert yonler["sag"] == ("varsayilan", varsayilan)
    tur, sol = yonler["sol"]
    assert tur == "ayna" and len(sol) == len(varsayilan)
    for (ms_v, v), (ms_s, a) in zip(varsayilan, sol):
        assert ms_v == ms_s
        assert a[_sutun("sol_omuz")] == v[_sutun("sag_omuz")]
        assert a[_sutun("sag_omuz")] == ju.ACI_YOK               # sağ kola dokunmaz
        assert a[_sutun("kafa_pan")] == 180 - v[_sutun("kafa_pan")]
    # ileri: iki kol aynı açıda öne, kafa düz
    son = yonler["ileri"][1][-1][1]
    assert son[_sutun("sag_omuz")] == son[_sutun("sol_omuz")] and son[_sutun("kafa_pan")] == 90
    # arka: kafa pan geriye dönemez, sınıra gider
    pan = next(k for k in kanallar if k["ad"] == "kafa_pan")
    assert yonler["arka"][1][-1][1][_sutun("kafa_pan")] in (pan["min_aci"], pan["max_aci"])


def test_yonsuz_jestte_yalniz_varsayilan():
    jestler, _, _ = ju.jestleri_oku(_kanallar())
    for ad, _, _, yonler in jestler:
        if ad != "isaret":
            assert yonler == {}, ad
    metin, _, _ = ju.uret()
    assert '{"evet", JEST_EVET, 6, {nullptr, nullptr, nullptr, nullptr}, {0, 0, 0, 0}},' in metin
    assert "{JEST_ISARET_SOL, JEST_ISARET, JEST_ISARET_ILERI, JEST_ISARET_ARKA}" in metin
    assert "JEST_ISARET_SAG" not in metin                          # varsayılan kopyalanmaz
    assert 'YON_ADLARI[YON_SAYISI] = {"sol", "sag", "ileri", "arka"}' in metin


def test_yon_varyantinda_sinir_denetimi(tmp_path):
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n  - {ms: 0, kafa_pan: 90}\n"
        "yonler:\n  ileri:\n    - {ms: 0, kafa_tilt: 150}\n", encoding="utf-8")
    with pytest.raises(ju.JestHatasi, match=r"yonler\.ileri.*sınır dışı"):
        ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())


def test_ayna_sinir_disina_cikarsa_hata(tmp_path):
    # kafa_pan sınırı 45-120: 50 geçerli ama aynası 130 sınır dışı -> sol varyant reddedilir
    kanallar = ju.kanallari_oku(_kanal_dosyasi(tmp_path, pan_max=120))[1]
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n  - {ms: 0, kafa_pan: 50}\nyonler:\n  sol: ayna\n", encoding="utf-8")
    with pytest.raises(ju.JestHatasi, match=r"yonler\.sol.*kafa_pan=130 sınır dışı"):
        ju.jest_oku(tmp_path / "deneme.yaml", kanallar)


@pytest.mark.parametrize("yonler, parca", [
    ("  yukari: ayna\n", "bilinmeyen yön"),
    ("  sol: aynala\n", "kare listesi olmalı"),
    ("  - sol\n", "sözlük olmalı"),
])
def test_hatali_yonler_reddedilir(tmp_path, yonler, parca):
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n  - {ms: 0, kafa_pan: 90}\nyonler:\n" + yonler, encoding="utf-8")
    with pytest.raises(ju.JestHatasi, match=parca):
        ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())


@pytest.mark.parametrize("ayar, parca", [
    ({"sol_ayna": "kafa_pan"}, "karşılıklı değil"),
    ({"pan_ayna": "kuyruk"}, "tabloda yok"),
])
def test_hatali_ayna_tablosu_reddedilir(tmp_path, ayar, parca):
    with pytest.raises(ju.JestHatasi, match=parca):
        ju.kanallari_oku(_kanal_dosyasi(tmp_path, **ayar))


def test_yon_bellek_tahmini():
    jestler, _, _ = ju.jestleri_oku(_kanallar())
    # isaret: sol + ileri + arka ayrı dizi (3'er kare), sag kopya değil; kare = 4 + 4*6 = 28 bayt
    assert ju.yon_bellek_bayt(jestler) == 9 * 28
