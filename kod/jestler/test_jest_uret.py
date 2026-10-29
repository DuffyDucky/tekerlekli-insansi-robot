"""jest_uret.py testleri. Çalıştırma (depo kökünden): py -3 -m pytest kod/jestler -q"""

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jest_uret as ju  # noqa: E402


def _kanallar():
    return ju.kanallari_oku()[1]


def _tablo():
    return {k["ad"]: k for k in _kanallar()}


def test_depodaki_baslik_guncel():
    # YAML değişip betik çalıştırılmadıysa ESP32 eski jestleri oynar; bunu yakala.
    metin, _, _ = ju.uret()
    assert ju.CIKTI.read_text(encoding="utf-8") == metin


def test_bosta_tum_kanallari_yazar_ve_sinirlar_icinde():
    kanallar = _kanallar()
    _, bosta, _ = ju.jestleri_oku(kanallar)
    for k, aci in zip(kanallar, bosta):
        assert k["min_aci"] <= aci <= k["max_aci"], k["ad"]


def test_bosta_ev_pozu():
    # ev pozu = her eklem 0 (S2 alt sınırı 5): robot açısı = eklem + ofset
    kanallar = _kanallar()
    _, bosta, _ = ju.jestleri_oku(kanallar)
    ev = {"r_s1": 0, "l_s1": 0, "r_s2": 5, "l_s2": 5, "r_dirsek": 0, "l_dirsek": 0,
          "r_bilek": 0, "l_bilek": 0, "pan": 0, "tilt": 0}
    for k, aci in zip(kanallar, bosta):
        assert aci == ev[k["eklem"]] + k["eklem_ofset"], k["ad"]


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
    ("ad: deneme\nkareler:\n  - {ms: 0, sag_omuz_yan: 4}\n", "sınır dışı"),
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


# --------------------------- 10 servo, sınırlar JSON'dan (29 Ekim 2026) ---------------------------

def test_on_servo_kanal_numaralari():
    tablo = _tablo()
    beklenen = {"sag_omuz": 0, "sag_omuz_yan": 1, "sag_dirsek": 2, "sag_bilek": 3, "kafa_pan": 4,
                "sol_omuz": 5, "sol_omuz_yan": 6, "sol_dirsek": 7, "sol_bilek": 8, "kafa_tilt": 9}
    assert {ad: k["kanal"] for ad, k in tablo.items()} == beklenen
    # 10-12 sonar trig için ayrılmış, kullanılmaz
    assert not {10, 11, 12} & {k["kanal"] for k in tablo.values()}
    for ad in ("sag_omuz", "sag_omuz_yan", "sol_omuz", "sol_omuz_yan"):
        assert tablo[ad]["model"] == "DS3235", ad
    for ad in ("sag_dirsek", "sag_bilek", "sol_dirsek", "sol_bilek", "kafa_pan", "kafa_tilt"):
        assert tablo[ad]["model"] == "MG996R", ad


def test_eklem_sinirlari_jsondan_ofsetle_turetilir():
    tablo = _tablo()
    beklenen = {"omuz": (0, 180), "omuz_yan": (5, 120), "dirsek": (0, 105), "bilek": (0, 180)}
    for taraf in ("sag", "sol"):
        for eklem, (lo, hi) in beklenen.items():
            k = tablo[f"{taraf}_{eklem}"]
            assert (k["min_aci"], k["max_aci"]) == (lo, hi), k["ad"]
    assert (tablo["kafa_pan"]["min_aci"], tablo["kafa_pan"]["max_aci"]) == (0, 180)
    assert (tablo["kafa_tilt"]["min_aci"], tablo["kafa_tilt"]["max_aci"]) == (77, 103)
    assert tablo["sag_omuz"]["eklem"] == "r_s1" and tablo["sag_omuz"]["eklem_ofset"] == 45
    assert tablo["sol_omuz_yan"]["eklem"] == "l_s2" and tablo["sol_omuz_yan"]["eklem_ofset"] == 0


def test_omuz_hizi_insan_yakini_siniri():
    # insan yakınında omuz <= 1,5 rad/s (~86 der/s); tablo 85 ile sınırlı
    tablo = _tablo()
    for ad in ("sag_omuz", "sag_omuz_yan", "sol_omuz", "sol_omuz_yan"):
        assert tablo[ad]["hiz"] <= 85, ad


def _kanal_yaml(tmp_path, satirlar):
    yol = tmp_path / "kanallar_deneme.yaml"
    yol.write_text("kanallar:\n" + "".join(f"  {s}\n" for s in satirlar), encoding="utf-8")
    return yol


def _sinirlar(**degisiklik):
    """Depodaki JSON'un kopyası; degisiklik = {eklem: (min, max)}."""
    s = copy.deepcopy(ju.eklem_oku())
    for eklem, (lo, hi) in degisiklik.items():
        s["eklemler"][eklem]["min"], s["eklemler"][eklem]["max"] = lo, hi
    return s


@pytest.mark.parametrize("satir, parca", [
    ("kafa_pan: {kanal: 4, model: X, min_us: 500, max_us: 2500, hiz: 90, eklem: pan, eklem_ofset: 90,"
     " min_aci: 10}", "elle yazılmaz"),
    ("kafa_pan: {kanal: 4, model: X, min_us: 500, max_us: 2500, hiz: 90, eklem: kuyruk, eklem_ofset: 90}",
     "eklem_sinirlari.json'da yok"),
    ("kafa_pan: {kanal: 4, model: X, min_us: 500, max_us: 2500, hiz: 90, eklem: pan, eklem_ofset: 120}",
     "0-180"),
    ("kafa_pan: {kanal: 4, model: X, min_us: 500, max_us: 2500, hiz: 90, eklem: pan}", "eksik alan"),
])
def test_hatali_eklem_alani_reddedilir(tmp_path, satir, parca):
    with pytest.raises(ju.JestHatasi, match=parca):
        ju.kanallari_oku(_kanal_yaml(tmp_path, [satir]))


def test_jsondaki_sinir_degisince_tablo_izler(tmp_path):
    yol = _kanal_yaml(tmp_path, [
        "kafa_tilt: {kanal: 9, model: X, min_us: 500, max_us: 2500, hiz: 60, eklem: tilt, eklem_ofset: 90}"])
    kanallar = ju.kanallari_oku(yol, _sinirlar(tilt=(-10.0, 12.0)))[1]
    assert (kanallar[0]["min_aci"], kanallar[0]["max_aci"]) == (80, 102)


# --------------------------- bağımlı kısıt (S1 >= 120 iken S2 <= 117) ---------------------------

def test_bagimli_kurallar_robot_acisina_cevrilir():
    kurallar = ju.bagimli_kurallari(ju.eklem_oku(), _kanallar())
    sag = next(k for k in kurallar if "sag_omuz" in k["kosul"])
    assert sag["kosul"] == {"sag_omuz": (165.0, 180.0)}        # eklem 120..135 + ofset 45
    assert sag["sinir"] == {"sag_omuz_yan": (5.0, 117.0)}
    assert any("sol_omuz" in k["kosul"] for k in kurallar)


@pytest.mark.parametrize("kareler", [
    # S1 eklem 125 (robot 170) iken S2 118
    "  - {ms: 0, sag_omuz: 170, sag_omuz_yan: 118}\n",
    # sol kol da denetlenir
    "  - {ms: 0, sol_omuz: 180, sol_omuz_yan: 120}\n",
])
def test_bagimli_ihlali_reddedilir(tmp_path, kareler):
    (tmp_path / "deneme.yaml").write_text("ad: deneme\nkareler:\n" + kareler, encoding="utf-8")
    with pytest.raises(ju.JestHatasi, match="bağımlı kısıt"):
        ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())


def test_bagimli_ara_degerde_de_denetlenir(tmp_path):
    # iki kare de kurala uyar (164 < 165; 117 <= 117) ama aradaki doğrusal yol köşeyi keser
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n"
        "  - {ms: 0, sag_omuz: 164, sag_omuz_yan: 120}\n"
        "  - {ms: 4000, sag_omuz: 180, sag_omuz_yan: 117}\n", encoding="utf-8")
    with pytest.raises(ju.JestHatasi, match="bağımlı kısıt.*arası"):
        ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())


def test_bagimli_sinirda_gecer_ve_yon_varyanti_denetlenir(tmp_path):
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n  - {ms: 0, sag_omuz: 180, sag_omuz_yan: 117}\n", encoding="utf-8")
    ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())          # hata yok
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n  - {ms: 0, sag_omuz: 100, sag_omuz_yan: 118}\n"
        "yonler:\n  ileri:\n    - {ms: 0, sol_omuz: 170, sol_omuz_yan: 118}\n", encoding="utf-8")
    with pytest.raises(ju.JestHatasi, match=r"yonler\.ileri.*bağımlı kısıt"):
        ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())


def test_bagimli_kanal_jestte_yoksa_uyarir(tmp_path):
    (tmp_path / "deneme.yaml").write_text(
        "ad: deneme\nkareler:\n  - {ms: 0, sag_omuz: 170}\n", encoding="utf-8")
    _, _, _, uyarilar, _ = ju.jest_oku(tmp_path / "deneme.yaml", _kanallar())
    assert any("sag_omuz_yan" in u and "denetlenemedi" in u for u in uyarilar)


def test_depodaki_jestler_s2_alt_sinir():
    kanallar = _kanallar()
    jestler, _, _ = ju.jestleri_oku(kanallar)
    s2 = [i for i, k in enumerate(kanallar) if k["eklem"] in ("r_s2", "l_s2")]
    for ad, _, kareler, yonler in jestler:
        for z in [kareler] + [v[1] for v in yonler.values()]:
            for _, acilar in z:
                for i in s2:
                    assert acilar[i] == ju.ACI_YOK or acilar[i] >= 5, ad


# --------------------------- teker ivme sınırları -> sinirlar_verisi.h ---------------------------

def test_ivme_sinirlari_jsondan():
    assert ju.ivme_sinirlari(ju.eklem_oku()) == {
        "duz_surus": 0.5, "duz_fren": 1.8, "rampa_surus": 0.1, "rampa_fren": 0.1}


def test_ivme_eksik_ya_da_hataliysa_hata():
    s = _sinirlar()
    del s["teker"]["ivme_sinir_m_s2"]["rampa_fren"]
    with pytest.raises(ju.JestHatasi, match="rampa_fren"):
        ju.ivme_sinirlari(s)
    s = _sinirlar()
    s["teker"]["ivme_sinir_m_s2"]["duz_fren"] = 0
    with pytest.raises(ju.JestHatasi, match="duz_fren"):
        ju.ivme_sinirlari(s)


def test_sinir_basligi_guncel_ve_icerik():
    metin = ju.sinir_uret()
    assert ju.SINIR_CIKTI.read_text(encoding="utf-8") == metin
    assert "ELLE DUZENLEME" in metin
    for satir in ("IVME_DUZ_SURUS = 0.5f", "IVME_DUZ_FREN = 1.8f", "IVME_RAMPA_SURUS = 0.1f",
                  "IVME_RAMPA_FREN = 0.1f"):
        assert satir in metin


def test_kontrol_iki_basligi_da_denetler(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(ju, "CIKTI", tmp_path / "jest_verisi.h")
    monkeypatch.setattr(ju, "SINIR_CIKTI", tmp_path / "sinirlar_verisi.h")
    assert ju.main([]) == 0
    assert ju.main(["--kontrol"]) == 0
    (tmp_path / "sinirlar_verisi.h").write_text("// eski\n", encoding="utf-8")
    assert ju.main(["--kontrol"]) == 1
    assert "sinirlar_verisi.h güncel değil" in capsys.readouterr().out


# --------------------------- yönlü jestler (27 Ekim 2026) ---------------------------

def _sutun(ad):
    return [k["ad"] for k in _kanallar()].index(ad)


def _kanal_dosyasi(tmp_path, pan_ayna="kafa_pan", sol_ayna="sag_omuz"):
    """Deneme için küçük kanal tablosu (sağ/sol omuz + kafa_pan)."""
    return _kanal_yaml(tmp_path, [
        "sag_omuz: {kanal: 0, model: X, min_us: 500, max_us: 2500, hiz: 85, eklem: r_s1, eklem_ofset: 45,"
        " ayna: sol_omuz, ayna_aci: ayni}",
        "sol_omuz: {kanal: 5, model: X, min_us: 500, max_us: 2500, hiz: 85, eklem: l_s1, eklem_ofset: 45,"
        f" ters: true, ayna: {sol_ayna}, ayna_aci: ayni}}",
        "kafa_pan: {kanal: 4, model: X, min_us: 500, max_us: 2500, hiz: 90, eklem: pan, eklem_ofset: 90,"
        f" ayna: {pan_ayna}, ayna_aci: 180-aci}}"])


def test_depodaki_ayna_esleme_karsilikli():
    tablo = _tablo()
    for eklem in ("omuz", "omuz_yan", "dirsek", "bilek"):
        assert tablo[f"sag_{eklem}"]["ayna"] == f"sol_{eklem}"
        assert tablo[f"sol_{eklem}"]["ayna"] == f"sag_{eklem}"
        assert tablo[f"sag_{eklem}"]["ayna_aci"] == "ayni"
        # sol kol servoları ters takılı (tahmini): robot açısı aynı kalsın diye kol aynası "ayni"
        assert tablo[f"sol_{eklem}"]["ters"] and not tablo[f"sag_{eklem}"]["ters"]
    assert (tablo["kafa_pan"]["ayna"], tablo["kafa_pan"]["ayna_aci"]) == ("kafa_pan", "180-aci")
    assert (tablo["kafa_tilt"]["ayna"], tablo["kafa_tilt"]["ayna_aci"]) == ("kafa_tilt", "ayni")


def test_ayna_kanal_ve_aci_donusumu():
    kanallar = _kanallar()
    ham = [{"ms": 0, "sag_omuz": 70, "sag_omuz_yan": 80, "sag_dirsek": 15, "sag_bilek": 90,
            "kafa_pan": 70, "kafa_tilt": 85}]
    assert ju.ayna_kareler(ham, kanallar) == [
        {"ms": 0, "sol_omuz": 70, "sol_omuz_yan": 80, "sol_dirsek": 15, "sol_bilek": 90,
         "kafa_pan": 110, "kafa_tilt": 85}]
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
        assert a[_sutun("sol_omuz_yan")] == v[_sutun("sag_omuz_yan")]
        assert a[_sutun("sag_omuz")] == ju.ACI_YOK               # sağ kola dokunmaz
        assert a[_sutun("kafa_pan")] == 180 - v[_sutun("kafa_pan")]
    # ileri: iki kol aynı açıda öne (S1 ~135 robot = eklem 90), S2 düşük, kafa düz
    son = yonler["ileri"][1][-1][1]
    assert son[_sutun("sag_omuz")] == son[_sutun("sol_omuz")] >= 120
    assert son[_sutun("sag_omuz_yan")] <= 20 and son[_sutun("kafa_pan")] == 90
    # arka: S1 geriye (robot < 45 = eklem < 0), S2 açık, kafa robotun sağına; omuz üstünden çözüm yok
    son = yonler["arka"][1][-1][1]
    assert son[_sutun("sag_omuz")] <= 20 and son[_sutun("sag_omuz_yan")] > 5
    assert son[_sutun("kafa_pan")] < 90


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
    # kafa_pan eklem -90..30 -> robot 0-120: 50 geçerli ama aynası 130 sınır dışı -> sol reddedilir
    kanallar = ju.kanallari_oku(_kanal_dosyasi(tmp_path), _sinirlar(pan=(-90.0, 30.0)))[1]
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
    # isaret: sol + ileri + arka ayrı dizi (3'er kare), sag kopya değil; kare = 4 + 4*10 = 44 bayt
    assert ju.yon_bellek_bayt(jestler) == 9 * 44
