# Gürültü provası: sentetik sinüs (konuşma yerine) + beyaz gürültü ile SNR hesabı, uzunluk, kırpmasız int16,
# wav okuma/yazma ve sahte tanıyıcıyla rapor.

import pytest

np = pytest.importorskip("numpy")

from olcum import gurultu_prova as gp  # noqa: E402

HIZ = 16000


def sinus(saniye=1.0, genlik=8000.0, frekans=440.0):
    t = np.arange(int(HIZ * saniye)) / HIZ
    return genlik * np.sin(2 * np.pi * frekans * t)


def beyaz(saniye, tohum=0, sapma=1000.0):
    return np.random.default_rng(tohum).normal(0, sapma, int(HIZ * saniye))


@pytest.mark.parametrize("snr", [20, 10, 5, 0, -5])
def test_snr_tutar(snr):
    konusma = sinus()
    karisim, gurultu = gp.karistir(konusma, beyaz(2.0), snr, np.random.default_rng(1))
    assert gp.snr_db(konusma, gurultu) == pytest.approx(snr, abs=1e-9)
    assert gp.snr_db(konusma, karisim - konusma) == pytest.approx(snr, abs=1e-9)


def test_snr_bilinen_deger():
    # Genliği A olan sinüsün gücü A^2/2; sapması s olan beyaz gürültünün gücü ~s^2
    sinyal, gurultu = sinus(genlik=1000.0), beyaz(1.0, sapma=100.0)
    assert gp.snr_db(sinyal, gurultu) == pytest.approx(10 * np.log10(1000 ** 2 / 2 / 100 ** 2), abs=0.2)
    assert gp.snr_db(sinyal, np.zeros(10)) == float("inf")


def test_uzunluk_kisa_ve_uzun_gurultu():
    konusma = sinus(1.0)
    rastgele = np.random.default_rng(3)
    kisa, _ = gp.karistir(konusma, beyaz(0.3), 10, rastgele)     # art arda eklenir
    uzun, _ = gp.karistir(konusma, beyaz(5.0), 10, rastgele)     # rastgele yerinden kesilir
    assert len(kisa) == len(uzun) == len(konusma)


def test_int16_kirpmasiz_kisma():
    konusma = sinus(genlik=30000.0)
    karisim, _ = gp.karistir(konusma, beyaz(1.0), 0, np.random.default_rng(4))
    ses, oran = gp.int16_yap(karisim)
    assert ses.dtype == np.int16 and len(ses) == len(konusma)
    assert oran < 1 and np.max(np.abs(ses.astype(np.int32))) <= 32767
    sessiz, oran = gp.int16_yap(sinus(genlik=1000.0))
    assert oran == 1.0 and np.max(np.abs(sessiz)) == 1000


def test_wav_oku_yaz_stereo_ve_8khz(tmp_path):
    import wave
    yol = str(tmp_path / "stereo8k.wav")
    ornek = np.round(sinus(0.5, 5000.0)[::2]).astype("<i2")         # 8 kHz'lik 0,5 s
    with wave.open(yol, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(np.repeat(ornek, 2).tobytes())                 # iki kanal aynı
    ses = gp.ses_oku(yol)
    assert len(ses) == 8000                                          # 16 kHz'e çıktı: 0,5 s
    gp.wav_yaz(str(tmp_path / "geri.wav"), np.round(ses).astype(np.int16))
    geri, hiz = gp.wav_oku(str(tmp_path / "geri.wav"))
    assert hiz == HIZ and len(geri) == 8000


class SnrIleBozulan:
    """5 dB ve altında hiçbir şey duymaz; diğerlerinde doğru metni döner."""
    ad = "sahte"

    def tani(self, ses, beklenen, etiket):
        return "" if etiket.split()[-1] in ("5dB", "0dB") else beklenen


def test_prova_ve_rapor(tmp_path, capsys):
    konusma = tmp_path / "konusma"
    gurultu = tmp_path / "gurultu"
    for ad, metin in (("k1", "Kantin nerede?"), ("k2", "Kütüphane kaçta açılıyor")):
        gp.wav_yaz(str(konusma / f"{ad}.wav"), np.round(sinus()).astype(np.int16))
        (konusma / f"{ad}.txt").write_text(metin, encoding="utf-8")
    gp.wav_yaz(str(konusma / "etiketsiz.wav"), np.zeros(100, dtype=np.int16))   # .txt yok: atlanır
    gp.wav_yaz(str(gurultu / "beyaz.wav"), np.round(beyaz(1.5)).astype(np.int16))

    konusmalar = gp.konusmalari_oku(str(konusma))
    assert [k[0] for k in konusmalar] == ["k1", "k2"]
    satirlar = gp.prova(konusmalar, gp.gurultuleri_oku(str(gurultu)), [20, 10, 5, 0], SnrIleBozulan(),
                        np.random.default_rng(1), yazdir=lambda *a: None)
    assert len(satirlar) == 2 * (1 + 4)
    tablo = "\n".join(gp.ana_tablo(satirlar))
    assert "| temiz | 2 | 2/2 %100,0 | %0,0 |" in tablo
    assert "| 10 dB | 2 | 2/2 %100,0 | %0,0 |" in tablo
    assert "| 0 dB | 2 | 0/2 %0,0 | %100,0 |" in tablo
    assert tablo.index("temiz") < tablo.index("20 dB") < tablo.index("0 dB")
    assert "| beyaz | %100,0 | %100,0 | %0,0 | %0,0 |" in "\n".join(gp.gurultu_tablosu(satirlar))

    kod = gp.main(["--stt", "referans", "--etiket", "deneme", "--konusma-klasoru", str(konusma),
                   "--gurultu-klasoru", str(gurultu), "--sonuc-klasoru", str(tmp_path / "s"), "--snr", "10,0"])
    assert kod == 0
    metin = (tmp_path / "s" / "gurultu-deneme.md").read_text(encoding="utf-8")
    assert "## SNR x tanıma" in metin and "| 0 dB | 2 | 2/2 %100,0 |" in metin


def test_kayit_yoksa_cikis_1(tmp_path):
    assert gp.main(["--stt", "referans", "--konusma-klasoru", str(tmp_path / "yok"),
                    "--sonuc-klasoru", str(tmp_path / "s")]) == 1
