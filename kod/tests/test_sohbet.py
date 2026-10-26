# Sohbet hafızası: son N tur bulut modeline mesaj geçmişi olarak gider (sahte istemciyle),
# kural tabanlı yalnız kaydeder; içerik eşleşmesi yoksa da bulutun sohbet cevabı söylenir.

from types import SimpleNamespace

from robot.dil import BILMIYORUM, BulutDilModeli, KuralTabanli, SohbetGecmisi, dil_sec, gemini_icerigi, sistem_istemi


def sahte_anthropic(cevaplar):
    cagrilar = []

    def create(**kw):
        cagrilar.append(kw)
        return SimpleNamespace(content=[SimpleNamespace(text=cevaplar[len(cagrilar) - 1])])
    return SimpleNamespace(messages=SimpleNamespace(create=create)), cagrilar


def test_gecmis_anthropic_mesajlarina_gider(paket):
    istemci, cagrilar = sahte_anthropic(["Merhaba, ben Robot!", "Kantin giriş katında.", "Rica ederim."])
    model = BulutDilModeli("anthropic", "claude-haiku-5-5", paket, istemci=istemci)
    model.cevapla("Merhaba")
    model.cevapla("Kantin nerede?")
    model.cevapla("Teşekkürler")
    assert cagrilar[0]["messages"] == [{"role": "user", "content": "Merhaba"}]
    assert cagrilar[2]["messages"] == [
        {"role": "user", "content": "Merhaba"}, {"role": "assistant", "content": "Merhaba, ben Robot!"},
        {"role": "user", "content": "Kantin nerede?"}, {"role": "assistant", "content": "Kantin giriş katında."},
        {"role": "user", "content": "Teşekkürler"},
    ]


def test_gecmis_n_turla_sinirli(paket):
    istemci, cagrilar = sahte_anthropic([f"cevap {i}" for i in range(5)])
    model = BulutDilModeli("anthropic", "m", paket, istemci=istemci, gecmis_tur=2)
    for i in range(5):
        model.cevapla(f"soru {i}")
    son = cagrilar[-1]["messages"]
    assert len(son) == 2 * 2 + 1                                 # 2 eski tur + yeni soru
    assert son[0] == {"role": "user", "content": "soru 2"}


def test_gecmis_gemini_bicimi(paket):
    gelenler = []

    def generate_content(model, contents, config):
        gelenler.append(contents)
        return SimpleNamespace(text="Tabii, yardımcı olayım.")
    istemci = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    model = BulutDilModeli("gemini", "gemini-flash-latest", paket, istemci=istemci)
    model.cevapla("Merhaba")
    model.cevapla("Bana yardım eder misin?")
    assert gelenler[1] == [
        {"role": "user", "parts": [{"text": "Merhaba"}]},
        {"role": "model", "parts": [{"text": "Tabii, yardımcı olayım."}]},
        {"role": "user", "parts": [{"text": "Bana yardım eder misin?"}]},
    ]


def test_eslesme_yoksa_bulut_sohbete_devam_eder(paket):
    istemci, _ = sahte_anthropic(["Ben de iyiyim, sizi gördüğüme sevindim!"])
    model = BulutDilModeli("anthropic", "m", paket, istemci=istemci)
    cevap = model.cevapla("Bugün hava çok güzel değil mi?")
    assert cevap.metin == "Ben de iyiyim, sizi gördüğüme sevindim!"   # kural tabanlı "bilmiyorum" derdi
    assert cevap.konu is None


def test_bulut_hatasinda_yedek_cevap_da_gecmise_yazilir(paket):
    def create(**kw):
        raise ConnectionError("internet yok")
    model = BulutDilModeli("anthropic", "m", paket, istemci=SimpleNamespace(messages=SimpleNamespace(create=create)))
    model.cevapla("Kantin nerede?")
    assert model.gecmis.mesajlar()[-1] == {"role": "assistant", "content": "Kantin giriş katında."}


def test_kural_tabanli_yalniz_kaydeder(paket):
    k = KuralTabanli(paket, gecmis_tur=3)
    for soru in ("Merhaba", "Uzaylılar var mı?", "Kantin nerede?", "Teşekkürler"):
        k.cevapla(soru)
    assert [s for s, _ in k.gecmis.turlar] == ["Uzaylılar var mı?", "Kantin nerede?", "Teşekkürler"]
    assert k.gecmis.turlar[0][1] == BILMIYORUM
    assert k.cevapla("Kantin nerede?").metin == "Kantin giriş katında."   # geçmiş cevabı değiştirmez


def test_sistem_istemi_sohbet_ve_uydurmama(paket):
    istem = sistem_istemi(paket, "Robot", "merhaba")
    assert "sohbet" in istem and "uydurma" in istem and "görevliye" in istem
    assert "Laboratuvar" in istem                                  # bildiği konular listesi


def test_dil_sec_gecmis_uzunlugu(paket):
    assert dil_sec("kural", paket, gecmis_tur=4).gecmis.turlar.maxlen == 4
    assert SohbetGecmisi(0).mesajlar() == []
    assert gemini_icerigi([]) == []
