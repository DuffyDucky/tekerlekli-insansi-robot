import icerik_kontrol
from icerik_kontrol import denetle

SAGLAM = """\
# açıklama satırında ... yer tutucu sayılmaz
kurum: "Deneme Okulu"
rol: "karşılama robotu"
selamlama: "Merhaba!"
konular:
  - baslik: Kantin
    anahtarlar: [kantin, yemek]
    cevap: "Kantin giriş katında."
    jest: isaret
yerler:
  - ad: Kütüphane
    tarif: "Kütüphane ... katında."
sss:
  - soru: "Wi-Fi var mı?"
    anahtarlar: [wifi, internet]
    cevap: "Evet."
"""


def test_saglam_paket_hatasiz():
    rapor = denetle(SAGLAM)
    assert rapor.hatalar == [] and rapor.uyarilar == []
    assert rapor.sayilar == {"konular": 1, "yerler": 1, "sss": 1, "anahtar kelime": 5}


def test_yer_tutucular_satir_satir():
    rapor = denetle(SAGLAM)
    assert rapor.yer_tutucular == [(12, 'tarif: "Kütüphane ... katında."')]   # yorum satırı (1) sayılmadı


def test_eksik_alanlar():
    metin = SAGLAM.replace('kurum: "Deneme Okulu"\n', "").replace('    cevap: "Kantin giriş katında."\n', "")
    hatalar = denetle(metin).hatalar
    assert any("'kurum'" in h for h in hatalar)
    assert any("Kantin: 'cevap' alanı yok" in h for h in hatalar)


def test_bos_anahtar_listesi_ve_bos_cevap():
    metin = SAGLAM.replace("[kantin, yemek]", "[]").replace('cevap: "Evet."', 'cevap: ""')
    hatalar = denetle(metin).hatalar
    assert any("Kantin: anahtar kelime listesi boş" in h for h in hatalar)
    assert any("'cevap' boş" in h for h in hatalar)


def test_ayni_anahtar_iki_kayitta():
    metin = SAGLAM.replace("[wifi, internet]", "[wifi, Yemek]")
    hatalar = denetle(metin).hatalar
    assert hatalar == ["'yemek' anahtar kelimesi iki kayıtta: konular / Kantin ve sss / Wi-Fi var mı?"]


def test_yer_adi_anahtar_sayilir():
    metin = SAGLAM.replace("[kantin, yemek]", "[kantin, kütüphane]")
    assert any("'kütüphane'" in h for h in denetle(metin).hatalar)


def test_bilinmeyen_jest_uyari_bozuk_yaml_hata():
    assert "bilinmeyen jest" in denetle(SAGLAM.replace("jest: isaret", "jest: dans")).uyarilar[0]
    assert denetle("kurum: [kapanmayan").hatalar[0].startswith("YAML okunamadı")
    assert denetle("").hatalar


def test_cikis_kodu(tmp_path, capsys):
    iyi = tmp_path / "iyi.yaml"
    iyi.write_text(SAGLAM, encoding="utf-8")
    kotu = tmp_path / "kotu.yaml"
    kotu.write_text(SAGLAM.replace("[kantin, yemek]", "[]"), encoding="utf-8")
    assert icerik_kontrol.main([str(iyi)]) == 0
    assert icerik_kontrol.main([str(iyi), "--siki"]) == 1          # '...' sıkı modda hata
    assert icerik_kontrol.main([str(kotu)]) == 1
    assert "HATA" in capsys.readouterr().out


def test_ornek_paketlerde_hata_yok():
    assert icerik_kontrol.main([]) == 0
