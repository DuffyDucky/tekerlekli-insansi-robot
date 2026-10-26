import sys
from types import SimpleNamespace

from robot.dil import BILMIYORUM, BulutDilModeli, KuralTabanli, dil_sec, sistem_istemi


def test_selam_kalibi(paket):
    cevap = KuralTabanli(paket).cevapla("Merhaba!")
    assert cevap.metin == "Merhaba, hoş geldiniz!"
    assert cevap.jest == "selam"


def test_tesekkur_ve_veda(paket):
    k = KuralTabanli(paket)
    assert "Rica" in k.cevapla("Çok teşekkürler").metin
    assert "Rica" in k.cevapla("sağ ol").metin
    veda = k.cevapla("Hoşça kal")
    assert "Hoşça" in veda.metin and veda.jest == "el_salla"


def test_kimsin_kalibi(paket):
    assert "Robotçuk" in KuralTabanli(paket, "Robotçuk").cevapla("Sen kimsin?").metin


def test_icerik_cevabi_kaliptan_once(paket):
    cevap = KuralTabanli(paket).cevapla("Merhaba, laboratuvar nerede?")
    assert cevap.metin == "Laboratuvar ikinci katta."
    assert cevap.jest == "isaret"


def test_bilinmeyen_soru_gorevliye_yonlendirir(paket):
    assert KuralTabanli(paket).cevapla("Uzaylılar var mı?").metin == BILMIYORUM


def test_anahtar_yoksa_kurala_duser(paket, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    model = BulutDilModeli("anthropic", "claude-haiku-5-5", paket)
    assert not model.calisiyor
    assert model.cevapla("merhaba").metin == "Merhaba, hoş geldiniz!"


def test_paket_yoksa_kurala_duser(paket, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "sahte")
    monkeypatch.setitem(sys.modules, "google", None)   # "from google import genai" ImportError verir
    model = BulutDilModeli("gemini", "gemini-flash-latest", paket)
    assert not model.calisiyor
    assert model.cevapla("Kantin nerede?").metin == "Kantin giriş katında."


def test_anthropic_sahte_istemci(paket):
    cagrilar = []

    def create(**kw):
        cagrilar.append(kw)
        return SimpleNamespace(content=[SimpleNamespace(text="Laboratuvar ikinci kattadır.")])

    istemci = SimpleNamespace(messages=SimpleNamespace(create=create))
    model = BulutDilModeli("anthropic", "claude-haiku-5-5", paket, istemci=istemci)
    cevap = model.cevapla("Laboratuvar nerede?")
    assert cevap.metin == "Laboratuvar ikinci kattadır."
    assert cevap.jest == "isaret"                      # jest içerik paketinden gelir
    assert cagrilar[0]["model"] == "claude-haiku-5-5"
    assert "Laboratuvar ikinci katta." in cagrilar[0]["system"]   # bağlam istemde


def test_gemini_sahte_istemci(paket):
    def generate_content(model, contents, config):
        assert "Türkçe" in config["system_instruction"]
        return SimpleNamespace(text="Otobüsle gelebilirsiniz.")

    istemci = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    model = BulutDilModeli("gemini", "gemini-flash-latest", paket, istemci=istemci)
    assert model.cevapla("ulaşım?").metin == "Otobüsle gelebilirsiniz."


def test_bulut_hatasinda_kurala_duser(paket):
    def create(**kw):
        raise ConnectionError("internet yok")

    istemci = SimpleNamespace(messages=SimpleNamespace(create=create))
    model = BulutDilModeli("anthropic", "claude-haiku-5-5", paket, istemci=istemci)
    assert model.cevapla("Kantin nerede?").metin == "Kantin giriş katında."


def test_sistem_istemi_kisa_ve_baglamli(paket):
    istem = sistem_istemi(paket, "Robot", "laboratuvar ve kayıt")
    assert "1-2" in istem and "Deneme Okulu" in istem
    assert "Kayıtlar sekreterlikte" in istem


def test_dil_sec_varsayilan_kural(paket):
    assert isinstance(dil_sec("kural", paket), KuralTabanli)
    assert isinstance(dil_sec("bilinmeyen", paket), KuralTabanli)
