# Ne yapıyor: ayarlar.yaml'ı okur, bileşenleri (tetik, stt, dil, tts, seri, yüz) kurar ve robotu çalıştırır.
# Konuşma döngüsü: BEKLE -> tetik -> DİNLE -> stt -> DÜŞÜN -> dil -> (JEST) -> KONUŞ -> tts -> BEKLE.
# Yüz (pygame) ana iş parçacığında, konuşma döngüsü ayrı bir iş parçacığında çalışır.
#
# Örnek:  py -3 kod/ana.py --yuzsuz --icerik universite      (Windows, yalnız terminal)
#         python3 ana.py --icerik universite                   (Pi, kod/ klasöründen)

import argparse
import os
import sys
import threading
import time
from dataclasses import dataclass

import yaml

from robot.dil import dil_sec
from robot.durum import Durum, DurumMakinesi
from robot.icerik import IcerikPaketi
from robot.seri import seri_sec
from robot.stt import stt_sec
from robot.tetik import tetik_sec
from robot.tts import tts_sec
from robot.yuz import Yuz

KOD_KLASORU = os.path.dirname(os.path.abspath(__file__))


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
    p.add_argument("--saglayici", choices=["kural", "gemini", "anthropic"], help="cevap üretici")
    p.add_argument("--stt", choices=["klavye", "vosk", "google"], help="konuşma tanıma")
    p.add_argument("--tts", choices=["yazi", "pyttsx3", "piper"], help="seslendirme")
    p.add_argument("--deneme-saniye", type=float, help="yüz tüm ifadeleri gösterip bu kadar saniye sonra kapanır")
    return p.parse_args(argv)


def secenekleri_uygula(ayar, sec):
    """Komut satırında verilen seçenekler ayar dosyasını ezer."""
    for bolum in ("icerik", "dil", "stt", "tts", "yuz", "tetik", "seri", "robot", "jest"):
        ayar.setdefault(bolum, {})
    if sec.icerik:
        ayar["icerik"]["paket"] = sec.icerik
    if sec.yuz is not None:
        ayar["yuz"]["etkin"] = sec.yuz
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
    d, s, t, y = ayar["dil"], ayar["stt"], ayar["tts"], ayar["yuz"]
    yuz = Yuz(y.get("genislik", 1280), y.get("yukseklik", 800), y.get("tam_ekran", False))
    if not y.get("etkin", True):
        yuz.etkin = False
    robot = Robot(
        durum=DurumMakinesi(),
        tetik=tetik_sec(ayar["tetik"].get("saglayici", "klavye"), ayar["tetik"].get("gpio_pin", 17)),
        stt=stt_sec(s.get("saglayici", "klavye"), yol_coz(s.get("vosk_model", "")),
                    s.get("azami_saniye", 8), s.get("mikrofon") or None),
        dil=dil_sec(d.get("saglayici", "kural"), paket, robot_adi,
                    d.get("gemini_model", "gemini-flash-latest"), d.get("anthropic_model", "claude-haiku-5-5")),
        tts=tts_sec(t.get("saglayici", "yazi"), t.get("hiz", 170), yol_coz(t.get("piper_model", "")),
                    t.get("piper_komut", "piper"), t.get("ses_cihazi", "")),
        seri=seri_sec(ayar["seri"].get("port", ""), ayar["seri"].get("hiz", 115200)),
        yuz=yuz,
        jest_suresi=ayar["jest"].get("sure", 1.0),
    )
    robot.durum.dinleyici_ekle(yuz.durum_degisti)   # yüz her durum değişiminden haberdar olur
    ozet_yaz(robot, paket)
    return robot


def ozet_yaz(robot, paket):
    adlar = [type(b).__name__ for b in (robot.tetik, robot.stt, robot.dil, robot.tts, robot.seri)]
    if getattr(robot.dil, "calisiyor", True) is False:
        adlar[2] += " (bağlanamadı, kural tabanlı)"
    print(f"[ana] içerik: {paket.kurum} ({len(paket.kayitlar)} kayıt) | tetik: {adlar[0]} | stt: {adlar[1]} "
          f"| dil: {adlar[2]} | tts: {adlar[3]} | seri: {adlar[4]} | yüz: {'açık' if robot.yuz.etkin else 'kapalı'}")


# ---------- konuşma döngüsü ----------

def tek_tur(robot):
    """Bir soru-cevap turu. Durum makinesi geçişleri sırayı zorlar."""
    robot.tetik.bekle()                       # BEKLE: düğmeye basılana kadar
    robot.durum.gec(Durum.DINLE)              # DİNLE'ye yalnız BEKLE'den geçilir (yarım dupleks)
    soru = robot.stt.dinle()
    if not soru:
        robot.durum.gec(Durum.BEKLE)
        return
    robot.durum.gec(Durum.DUSUN)
    robot.yuz.metin_goster(f"“{soru}”")   # duyulanı ekranda göster
    cevap = robot.dil.cevapla(soru)
    if cevap.jest:
        robot.durum.gec(Durum.JEST)
        robot.seri.jest(cevap.jest)           # kol hareketi ESP32'de başlar
        time.sleep(robot.jest_suresi)
    robot.durum.gec(Durum.KONUS)
    robot.yuz.metin_goster(cevap.metin)
    robot.tts.soyle(cevap.metin)              # konuşma bitene kadar burada beklenir; mikrofon kapalı
    robot.durum.gec(Durum.BEKLE)


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
    robot = bilesenleri_kur(ayar)
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


if __name__ == "__main__":
    main()
