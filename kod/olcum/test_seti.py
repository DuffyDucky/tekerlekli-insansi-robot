# Ne yapıyor: STT (konuşma tanıma) test seti ölçümü. Setteki her cümleyi ekrana yazar, kullanıcı söyler,
# seçilen STT dinler. Tanınanı doğru cümleyle karşılaştırır: tam / normalize eşleşme, kelime hata oranı
# (Levenshtein, dış kütüphane yok), konu (niyet) eşleşmesi, dinleme süresi. Özet ekrana ve CSV'ye yazılır.
#
# Örnek (depo kökünden, Windows):  py -3 kod/olcum/test_seti.py --stt klavye --etiket deneme --adet 5
#        (Pi, kod/ klasöründen):   python3 olcum/test_seti.py --stt vosk --etiket lab-45dB
# Sonuç: kod/olcum/sonuclar/YYYY-MM-DD_HHMM_<stt>_<etiket>.csv  (";" ayraçlı, Excel'de açılır)

import argparse
import csv
import os
import re
import statistics
import sys
import time
from datetime import datetime

OLCUM = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(OLCUM)
sys.path.insert(0, KOD)   # "robot" ve "ana" modülleri kod/ klasöründe

from ana import ayarlari_oku, konsolu_utf8_yap, paket_yolu, yol_coz  # noqa: E402
from robot.dil import KuralTabanli                                    # noqa: E402
from robot.gunluk import AYIRAC, KODLAMA, ms                           # noqa: E402
from robot.icerik import IcerikPaketi, kelimeler                      # noqa: E402
from robot.mikrofon import Mikrofon, MikrofonYok                      # noqa: E402
from robot.stt import stt_sec                                         # noqa: E402

ALANLAR = ["no", "referans", "taninan", "tam", "normalize", "kelime", "hata", "kho_yuzde",
           "konu_beklenen", "konu_taninan", "konu_ayni", "dinleme_ms"]


# ---------- karşılaştırma ----------

def normalize(metin):
    """Türkçe küçük harf, noktalama yok, tek boşluk: 'Kantin, nerede?' -> 'kantin nerede'."""
    return " ".join(kelimeler(metin or ""))


def duzenleme_mesafesi(a, b):
    """İki kelime listesi arasındaki en az işlem sayısı (Levenshtein): kelime ekleme, silme, değiştirme.
    Tablo satır satır doldurulur: onceki[j] = a'nın ilk i-1 kelimesini b'nin ilk j kelimesine çevirme maliyeti."""
    onceki = list(range(len(b) + 1))          # boş listeden b'ye: j kelime eklemek
    for i, kelime_a in enumerate(a, 1):
        simdiki = [i]                         # a'nın ilk i kelimesinden boş listeye: i silme
        for j, kelime_b in enumerate(b, 1):
            silme = onceki[j] + 1
            ekleme = simdiki[j - 1] + 1
            degistirme = onceki[j - 1] + (kelime_a != kelime_b)   # aynıysa 0 maliyet
            simdiki.append(min(silme, ekleme, degistirme))
        onceki = simdiki
    return onceki[-1]


def kelime_hata_orani(referans, taninan):
    """KHO (WER) = (değiştirilen + silinen + eklenen kelime) / referanstaki kelime sayısı."""
    ref, tan = normalize(referans).split(), normalize(taninan).split()
    if not ref:
        return 0.0 if not tan else 1.0
    return duzenleme_mesafesi(ref, tan) / len(ref)


def konu_bul(dil, metin):
    """Robot bu cümleyle hangi konuyu cevaplardı? (içerik başlığı, 'kalıp:...' ya da None)"""
    if dil is None or not metin:
        return None
    return dil.cevapla(metin).konu


def satir_degerlendir(no, referans, taninan, dinleme_ms, dil=None):
    taninan = taninan or ""
    ref_kelime = normalize(referans).split()
    hata = duzenleme_mesafesi(ref_kelime, normalize(taninan).split())
    beklenen, bulunan = konu_bul(dil, referans), konu_bul(dil, taninan)
    return {
        "no": no, "referans": referans, "taninan": taninan,
        "tam": int(taninan.strip() == referans.strip()),
        "normalize": int(normalize(taninan) == normalize(referans)),
        "kelime": len(ref_kelime), "hata": hata,
        "kho_yuzde": round(100 * hata / len(ref_kelime)) if ref_kelime else 0,
        "konu_beklenen": beklenen or "", "konu_taninan": bulunan or "",
        "konu_ayni": int(beklenen is not None and beklenen == bulunan),
        "dinleme_ms": dinleme_ms,
    }


# ---------- özet ----------

def yuzde(pay, payda):
    return f"%{100 * pay / payda:.1f}".replace(".", ",") if payda else "-"


def ozet(satirlar):
    """Özet satırları: (ad, değer) listesi. Hem ekrana hem CSV'nin sonuna yazılır."""
    n = len(satirlar)
    kelime = sum(s["kelime"] for s in satirlar)
    hata = sum(s["hata"] for s in satirlar)
    konulu = [s for s in satirlar if s["konu_beklenen"]]     # konusu olmayan cümle sayılmaz
    sureler = [s["dinleme_ms"] for s in satirlar] or [0]
    tam = sum(s["tam"] for s in satirlar)
    norm = sum(s["normalize"] for s in satirlar)
    ayni = sum(s["konu_ayni"] for s in konulu)
    return [
        ("Cümle sayısı", str(n)),
        ("Tam eşleşme", f"{tam}/{n}  {yuzde(tam, n)}"),
        ("Normalize eşleşme", f"{norm}/{n}  {yuzde(norm, n)}"),
        ("Kelime hata oranı", f"{yuzde(hata, kelime)}  ({hata} hata / {kelime} kelime)"),
        ("Konu (niyet) eşleşmesi", f"{ayni}/{len(konulu)}  {yuzde(ayni, len(konulu))}"),
        ("Dinleme süresi ms (ort/medyan/en fazla)",
         f"{round(statistics.mean(sureler))} / {round(statistics.median(sureler))} / {max(sureler)}"),
    ]


def ozet_yazdir(baslik, ozet_satirlari):
    print(f"\n== {baslik} ==")
    for ad, deger in ozet_satirlari:
        print(f"{ad:<40}: {deger}")


# ---------- dosyalar ----------

def seti_oku(yol):
    """Boş satırlar ve '#' ile başlayan açıklamalar atlanır."""
    with open(yol, encoding="utf-8") as dosya:
        satirlar = [s.strip() for s in dosya]
    return [s for s in satirlar if s and not s.startswith("#")]


def sonuc_yolu(klasor, stt_adi, etiket, simdi=None):
    simdi = simdi or datetime.now()
    guvenli = re.sub(r"[^\w-]+", "_", etiket).strip("_") or "etiketsiz"   # dosya adına uygun etiket
    return os.path.normpath(os.path.join(klasor, f"{simdi:%Y-%m-%d_%H%M}_{stt_adi}_{guvenli}.csv"))


def kaydet(yol, satirlar, ozet_satirlari, bilgi):
    """Önce her cümlenin satırı, bir boş satır, sonra ölçüm bilgisi ve özet."""
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", encoding=KODLAMA, newline="") as dosya:
        yazici = csv.writer(dosya, delimiter=AYIRAC)
        yazici.writerow(ALANLAR)
        for s in satirlar:
            yazici.writerow([s[a] for a in ALANLAR])
        yazici.writerow([])
        for ad, deger in list(bilgi.items()) + ozet_satirlari:
            yazici.writerow([ad, deger])


# ---------- ölçüm ----------

def stt_adi(stt):
    """KlavyeSTT -> klavye, VoskSTT -> vosk (kurulamayıp klavyeye düşüldüyse dosya adı bunu gösterir)."""
    return type(stt).__name__.replace("STT", "").lower()


def olc(cumleler, stt, dil=None, enter_bekle=False):
    """Her cümle için: ekrana yaz, (mikrofonda Enter bekle), dinle, değerlendir.
    Ctrl+C ya da girdi sonu ölçümü erken bitirir; o ana kadarki satırlar korunur."""
    satirlar = []
    for no, referans in enumerate(cumleler, 1):
        print(f"\n[{no}/{len(cumleler)}] Söyleyin:  {referans}")
        try:
            if enter_bekle:
                input("  Hazır olunca Enter'a basın, sonra cümleyi söyleyin... ")
            baslangic = time.perf_counter()
            taninan = stt.dinle()
            sure = ms(time.perf_counter() - baslangic)
        except (EOFError, KeyboardInterrupt):
            print("\n[ölçüm] Erken bitirildi.")
            break
        satir = satir_degerlendir(no, referans, taninan, sure, dil)
        print(f"  Tanınan: {satir['taninan'] or '(hiçbir şey)'}  | KHO %{satir['kho_yuzde']} | {sure} ms")
        satirlar.append(satir)
    return satirlar


def secenekleri_oku(argv=None):
    p = argparse.ArgumentParser(description="STT test seti ölçümü")
    p.add_argument("--stt", choices=["klavye", "vosk", "google"], help="konuşma tanıma (varsayılan: ayar dosyası)")
    p.add_argument("--etiket", default="etiketsiz", help='ortam etiketi, ör. "lab-45dB", "koridor-60dB"')
    p.add_argument("--set", default=os.path.join(OLCUM, "test_seti_universite.txt"), help="test seti dosyası")
    p.add_argument("--icerik", help="konu eşleşmesi için içerik paketi (varsayılan: ayar dosyası)")
    p.add_argument("--adet", type=int, help="yalnız ilk N cümle (hızlı deneme)")
    p.add_argument("--ayar", default=os.path.join(KOD, "ayarlar.yaml"))
    p.add_argument("--sonuc-klasoru", default=os.path.join(OLCUM, "sonuclar"))
    return p.parse_args(argv)


def main(argv=None):
    konsolu_utf8_yap()
    sec = secenekleri_oku(argv)
    ayar = ayarlari_oku(sec.ayar)
    s, a = ayar.get("stt") or {}, ayar.get("algilama") or {}
    stt_saglayici = sec.stt or s.get("saglayici", "vosk")
    mikrofon = None
    if stt_saglayici != "klavye":
        try:   # robotla aynı mikrofon ve aynı algılama ayarları (eşik, sessizlik süresi)
            mikrofon = Mikrofon(s.get("mikrofon") or None, a.get("esik", 500),
                                a.get("sessizlik_saniye", 0.8), a.get("vad_duzeyi", 2))
        except MikrofonYok as hata:
            print(f"[mikrofon] {hata}")
    stt = stt_sec(stt_saglayici, yol_coz(s.get("vosk_model", "")), s.get("azami_saniye", 8), mikrofon)
    paket_adi = sec.icerik or (ayar.get("icerik") or {}).get("paket", "universite")
    dil = KuralTabanli(IcerikPaketi.dosyadan(paket_yolu(paket_adi), (ayar.get("icerik") or {}).get("esik", 3)))
    cumleler = seti_oku(sec.set)[:sec.adet] if sec.adet else seti_oku(sec.set)
    print(f"[ölçüm] {len(cumleler)} cümle | stt: {stt_adi(stt)} | etiket: {sec.etiket}")
    satirlar = olc(cumleler, stt, dil, enter_bekle=stt_adi(stt) != "klavye")
    if not satirlar:
        print("[ölçüm] Hiç cümle ölçülmedi; dosya yazılmadı.")
        return 1
    ozet_satirlari = ozet(satirlar)
    ozet_yazdir(f"Özet: {stt_adi(stt)} | {sec.etiket}", ozet_satirlari)
    yol = sonuc_yolu(sec.sonuc_klasoru, stt_adi(stt), sec.etiket)
    bilgi = {"Tarih": f"{datetime.now():%Y-%m-%d %H:%M}", "STT": stt_adi(stt), "Etiket": sec.etiket,
             "Test seti": os.path.basename(sec.set), "İçerik paketi": paket_adi}
    kaydet(yol, satirlar, ozet_satirlari, bilgi)
    print(f"\n[ölçüm] Sonuç dosyası: {yol}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
