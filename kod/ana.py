# Ne yapıyor: ayarlar.yaml'ı okur, bileşenleri (mikrofon, tetik, stt, dil, tts, seri, yüz) kurar, robotu çalıştırır.
# Konuşma döngüsü: BEKLE -> (konuşma başladı) -> DİNLE -> stt -> DÜŞÜN -> dil -> (JEST) -> KONUŞ -> tts -> BEKLE.
# Robot sesli çalışır; mikrofon yoksa durur. --gelistirici: mikrofonsuz deneme (dokun + ekrana yaz / terminal).
# Yüz (pygame) ana iş parçacığında, konuşma döngüsü ayrı iş parçacığında; aralarında kuyruklar. Her tur
# gunlukler/YYYY-MM-DD.csv dosyasına yazılır (robot/gunluk.py).
#
# Örnek:  python3 ana.py --icerik universite                     (Pi, kod/ klasöründen, mikrofonla)
#         py -3 kod/ana.py --gelistirici --icerik universite      (Windows, mikrofonsuz deneme)

import argparse
import os
import sys
import threading
import time
from dataclasses import dataclass

import yaml

from robot.dil import dil_sec
from robot.durum import Durum, DurumMakinesi
from robot.gunluk import Gunluk, Kronometre, tur_satiri
from robot.icerik import IcerikPaketi
from robot.mikrofon import Mikrofon, MikrofonYok
from robot.seri import seri_sec
from robot.stt import EkranSTT, KlavyeSTT, stt_sec
from robot.tetik import DokunmaTetik, KlavyeTetik, SesTetik, tetik_sec
from robot.tts import tts_sec
from robot.yuz import Yuz

KOD_KLASORU = os.path.dirname(os.path.abspath(__file__))


class SesliModKurulamadi(Exception):
    """Mikrofon/konuşma tanıma kurulamadı ve geliştirici modu kapalı: robot sessiz çalışmaz, durur."""


@dataclass
class Robot:
    durum: DurumMakinesi
    tetik: object
    stt: object
    dil: object
    tts: object
    seri: object
    yuz: Yuz
    jest_suresi: float = 1.0
    gunluk: Gunluk | None = None      # None ise tur kaydı tutulmaz


# ---------- ayarlar ----------

def yol_coz(yol):
    """Göreli yolları kod/ klasörüne göre çözer."""
    if not yol or os.path.isabs(yol):
        return yol
    return os.path.join(KOD_KLASORU, yol)


def paket_yolu(ad):
    """'universite' -> kod/icerik/universite.yaml; .yaml ile biten ad dosya yolu sayılır."""
    if ad.endswith(".yaml"):
        return yol_coz(ad)
    return os.path.join(KOD_KLASORU, "icerik", ad + ".yaml")


def ayarlari_oku(yol):
    with open(yol, encoding="utf-8") as dosya:
        return yaml.safe_load(dosya) or {}


def secenekleri_oku(argv=None):
    p = argparse.ArgumentParser(description="Tekerlekli insansı robot yazılımı")
    p.add_argument("--ayar", default=os.path.join(KOD_KLASORU, "ayarlar.yaml"), help="ayar dosyası")
    p.add_argument("--icerik", help="içerik paketi: universite | tesis | dosya.yaml")
    p.add_argument("--yuz", dest="yuz", action="store_true", default=None, help="yüz penceresini aç")
    p.add_argument("--yuzsuz", dest="yuz", action="store_false", help="yalnız terminal")
    p.add_argument("--tam-ekran", action="store_true", help="yüz tam ekran (Pi'de otomatik başlatmada)")
    p.add_argument("--tetik", choices=["ses", "dokunma", "gpio", "klavye"], help="konuşma tetiği")
    p.add_argument("--gelistirici", action="store_true",
                   help="mikrofonsuz deneme: mikrofon yoksa dokun/Enter + ekrana/terminale yaz")
    p.add_argument("--saglayici", choices=["kural", "gemini", "anthropic"], help="cevap üretici")
    p.add_argument("--stt", choices=["klavye", "vosk", "google"], help="konuşma tanıma")
    p.add_argument("--tts", choices=["yazi", "pyttsx3", "piper"], help="seslendirme")
    p.add_argument("--deneme-saniye", type=float, help="yüz tüm ifadeleri gösterip bu kadar saniye sonra kapanır")
    return p.parse_args(argv)


def secenekleri_uygula(ayar, sec):
    """Komut satırında verilen seçenekler ayar dosyasını ezer."""
    for bolum in ("icerik", "dil", "stt", "tts", "yuz", "tetik", "seri", "robot", "jest", "gunluk", "algilama"):
        ayar.setdefault(bolum, {})
    # Yüz denemesi (--deneme-saniye) de bir geliştirici aracıdır; mikrofon istemez
    ayar["gelistirici"] = bool(sec.gelistirici or sec.deneme_saniye)
    if sec.icerik:
        ayar["icerik"]["paket"] = sec.icerik
    if sec.yuz is not None:
        ayar["yuz"]["etkin"] = sec.yuz
    if sec.tam_ekran:
        ayar["yuz"]["tam_ekran"] = True
    if sec.tetik:
        ayar["tetik"]["saglayici"] = sec.tetik
    if sec.saglayici:
        ayar["dil"]["saglayici"] = sec.saglayici
    if sec.stt:
        ayar["stt"]["saglayici"] = sec.stt
    if sec.tts:
        ayar["tts"]["saglayici"] = sec.tts
    return ayar


# ---------- kurulum ----------

def bilesenleri_kur(ayar):
    robot_adi = ayar["robot"].get("ad", "Robot")
    paket = IcerikPaketi.dosyadan(paket_yolu(ayar["icerik"].get("paket", "universite")),
                                  ayar["icerik"].get("esik", 3))
    d, s, t, y, g = ayar["dil"], ayar["stt"], ayar["tts"], ayar["yuz"], ayar["gunluk"]
    yuz = Yuz(y.get("genislik", 1280), y.get("yukseklik", 800), y.get("tam_ekran", False))
    if not y.get("etkin", True):
        yuz.etkin = False
    mikrofon = mikrofon_kur(ayar)
    tetik = tetik_sec(ayar["tetik"].get("saglayici", "ses"), ayar["tetik"].get("gpio_pin", 17), mikrofon)
    stt = stt_sec(s.get("saglayici", "vosk"), yol_coz(s.get("vosk_model", "")),
                  s.get("azami_saniye", 8), mikrofon)
    tetik, stt = sesli_modu_denetle(ayar, tetik, stt)
    tetik, stt = ekran_girdisini_bagla(yuz, tetik, stt, ayar["gelistirici"])
    robot = Robot(
        durum=DurumMakinesi(),
        tetik=tetik,
        stt=stt,
        dil=dil_sec(d.get("saglayici", "kural"), paket, robot_adi,
                    d.get("gemini_model", "gemini-flash-latest"), d.get("anthropic_model", "claude-haiku-5-5"),
                    d.get("gecmis_tur", 6)),
        tts=tts_sec(t.get("saglayici", "yazi"), t.get("hiz", 170), yol_coz(t.get("piper_model", "")),
                    t.get("piper_komut", "piper"), t.get("ses_cihazi", "")),
        seri=seri_sec(ayar["seri"].get("port", ""), ayar["seri"].get("hiz", 115200)),
        yuz=yuz,
        jest_suresi=ayar["jest"].get("sure", 1.0),
        gunluk=Gunluk(yol_coz(g.get("klasor", "gunlukler"))) if g.get("etkin", True) else None,
    )
    robot.durum.dinleyici_ekle(yuz.durum_degisti)   # yüz her durum değişiminden haberdar olur
    ozet_yaz(robot, paket)
    return robot


def mikrofon_gerekli_mi(ayar):
    return ayar["tetik"].get("saglayici", "ses") == "ses" or ayar["stt"].get("saglayici", "vosk") != "klavye"


def mikrofon_kur(ayar):
    """Ses tetiği ya da mikrofonlu STT seçiliyse ortak mikrofonu açar; olmazsa nedenini yazıp None döner."""
    if not mikrofon_gerekli_mi(ayar):
        return None
    a = ayar["algilama"]
    try:
        return Mikrofon(ayar["stt"].get("mikrofon") or None, a.get("esik", 500),
                        a.get("sessizlik_saniye", 0.8), a.get("vad_duzeyi", 2))
    except MikrofonYok as hata:
        print(f"[mikrofon] {hata}")
        return None


def sesli_modu_denetle(ayar, tetik, stt):
    """Robot sesli çalışır. Ses tetiği ya da konuşma tanıma kurulamadıysa: normalde açık mesajla durur
    (SesliModKurulamadi), geliştirici modunda dokunma/Enter tetiğe ve klavyeyle yazmaya düşer."""
    sorunlar = []
    if ayar["tetik"].get("saglayici", "ses") == "ses" and not isinstance(tetik, SesTetik):
        sorunlar.append("ses tetiği (mikrofon)")
    if ayar["stt"].get("saglayici", "vosk") != "klavye" and isinstance(stt, KlavyeSTT):
        sorunlar.append(f"konuşma tanıma ({ayar['stt'].get('saglayici', 'vosk')})")
    if not sorunlar:
        return tetik, stt
    if not ayar["gelistirici"]:
        raise SesliModKurulamadi(f"Kurulamadı: {', '.join(sorunlar)}. Robot sesli çalışır; mikrofonu ve "
                                 "Vosk modelini kontrol edin (OKU_BENI.md). Mikrofonsuz denemek için: --gelistirici")
    print(f"[ana] GELİŞTİRİCİ modu: {', '.join(sorunlar)} yok; dokunma/Enter ve klavyeyle devam ediyorum.")
    return DokunmaTetik(), KlavyeSTT()


def ekran_girdisini_bagla(yuz, tetik, stt, gelistirici=False):
    """Yüz açıksa dokunma tetiği yüze bağlanır; yüz kapalıysa dokunulacak ekran yok, Enter'a düşülür.
    Ekrandaki metin kutusu yalnız geliştirici modunda (robotun kullanıcısı yazmaz, konuşur)."""
    if isinstance(tetik, DokunmaTetik):
        if yuz.etkin:
            yuz.dokunma_tetik = tetik
        else:
            print("[tetik] Yüz kapalı, dokunma alanı yok; Enter'a düşüyorum.")
            tetik = KlavyeTetik()
    if gelistirici and isinstance(stt, KlavyeSTT) and yuz.etkin:
        stt = EkranSTT()            # soru terminale değil, yüzdeki metin kutusuna yazılır
        yuz.yazi_alici = stt
    return tetik, stt


def ozet_yaz(robot, paket):
    adlar = [type(b).__name__ for b in (robot.tetik, robot.stt, robot.dil, robot.tts, robot.seri)]
    if getattr(robot.dil, "calisiyor", True) is False:
        adlar[2] += " (bağlanamadı, kural tabanlı)"
    print(f"[ana] içerik: {paket.kurum} ({len(paket.kayitlar)} kayıt) | tetik: {adlar[0]} | stt: {adlar[1]} "
          f"| dil: {adlar[2]} | tts: {adlar[3]} | seri: {adlar[4]} | yüz: {'açık' if robot.yuz.etkin else 'kapalı'}")
    if robot.gunluk:
        print(f"[ana] günlük: {robot.gunluk.dosya_yolu()}")


# ---------- konuşma döngüsü ----------

def tek_tur(robot):
    """Bir soru-cevap turu. Durum makinesi geçişleri sırayı zorlar; süreler günlüğe yazılır."""
    robot.tetik.bekle()                       # BEKLE: düğmeye basılana kadar
    sure = Kronometre()                       # süre tetik anından itibaren tutulur
    robot.durum.gec(Durum.DINLE)              # DİNLE'ye yalnız BEKLE'den geçilir (yarım dupleks)
    soru = robot.stt.dinle()
    sure.adim("dinleme")
    if not soru:
        robot.durum.gec(Durum.BEKLE)
        gunluge_yaz(robot, None, None, sure)  # duyulamayan soru da ölçüm için kaydedilir
        return
    robot.durum.gec(Durum.DUSUN)
    robot.yuz.metin_goster(f"“{soru}”")   # duyulanı ekranda göster
    cevap = robot.dil.cevapla(soru)
    sure.adim("dusunme")
    if cevap.jest:
        robot.durum.gec(Durum.JEST)
        robot.seri.jest(cevap.jest)           # kol hareketi ESP32'de başlar
        time.sleep(robot.jest_suresi)
    sure.adim("jest")
    robot.durum.gec(Durum.KONUS)
    robot.yuz.metin_goster(cevap.metin)
    robot.tts.soyle(cevap.metin)              # konuşma bitene kadar burada beklenir; mikrofon kapalı
    sure.adim("seslendirme")
    robot.durum.gec(Durum.BEKLE)
    gunluge_yaz(robot, soru, cevap, sure)


def gunluge_yaz(robot, soru, cevap, sure):
    if robot.gunluk is not None:
        robot.gunluk.yaz(tur_satiri(robot, soru, cevap, sure))


def konusma_dongusu(robot, durdur):
    while not durdur.is_set():
        try:
            tek_tur(robot)
        except (EOFError, KeyboardInterrupt):  # klavye girdisi bitti ya da Ctrl+C
            break
        except Exception as hata:              # bir turdaki hata robotu düşürmesin
            print(f"[ana] Hata: {hata}")
            if robot.durum.durum != Durum.BEKLE:
                robot.durum.gec(Durum.BEKLE)
    durdur.set()


def konsolu_utf8_yap():
    """Windows'ta borudan (pipe) gelen/giden Türkçe karakterler bozulmasın."""
    for akis in (sys.stdin, sys.stdout):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")


def main(argv=None):
    konsolu_utf8_yap()
    sec = secenekleri_oku(argv)
    ayar = secenekleri_uygula(ayarlari_oku(sec.ayar), sec)
    try:
        robot = bilesenleri_kur(ayar)
    except SesliModKurulamadi as hata:
        print(f"[ana] {hata}")
        return 2                     # systemd servisi bu kodla 5 sn sonra yeniden dener (mikrofon takılınca açılır)
    durdur = threading.Event()
    if robot.yuz.etkin:
        # pygame ana iş parçacığında olmak zorunda; konuşma döngüsü arka planda
        konusma = threading.Thread(target=konusma_dongusu, args=(robot, durdur), daemon=True)
        konusma.start()
        robot.yuz.calistir(durdur, sec.deneme_saniye)
    else:
        konusma_dongusu(robot, durdur)
    robot.seri.kapat()
    print("[ana] Robot kapandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
