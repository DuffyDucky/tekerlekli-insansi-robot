# Ne yapıyor: içerik paketi (icerik/*.yaml) denetleyicisi. Zorunlu alanları, boş anahtar kelime listelerini
# ve aynı anahtar kelimenin iki kayıtta olmasını HATA sayar; "..." yer tutucularını satır satır listeler.
# Hata varsa çıkış kodu 1 (--siki ile yer tutucu da hata sayılır: demodan önce son kontrol için).
#
# Örnek:  py -3 kod/icerik_kontrol.py                    (icerik/ içindeki tüm paketler)
#         python3 icerik_kontrol.py universite --siki     (Pi'de, kod/ klasöründen)

import argparse
import glob
import os
import sys
from dataclasses import dataclass, field

import yaml

from robot.icerik import kelimeler

KOD_KLASORU = os.path.dirname(os.path.abspath(__file__))

ZORUNLU_UST = ["kurum", "selamlama"]
# Bölüm adı -> (kayıt adının alındığı alan, zorunlu alanlar)
BOLUMLER = {
    "konular": ("baslik", ["baslik", "anahtarlar", "cevap"]),
    "yerler": ("ad", ["ad", "tarif"]),               # yerin adı zaten anahtar kelime sayılır
    "sss": ("soru", ["soru", "anahtarlar", "cevap"]),
}
# Jestlerin tek kaynağı kod/jestler/ klasörü: her jest bir .yaml (kanallar.yaml servo tablosu, bosta duruş)
JEST_KLASORU = os.path.join(KOD_KLASORU, "jestler")
JEST_OLMAYANLAR = {"kanallar", "bosta"}
VARSAYILAN_JESTLER = {"selam", "isaret", "evet", "bosta"}   # jestler/ klasörü yoksa
YER_TUTUCULAR = ("...", "…")


@dataclass
class Rapor:
    hatalar: list = field(default_factory=list)
    uyarilar: list = field(default_factory=list)
    yer_tutucular: list = field(default_factory=list)   # (satır no, satır metni)
    sayilar: dict = field(default_factory=dict)


def bilinen_jestler():
    adlar = {os.path.splitext(os.path.basename(y))[0] for y in glob.glob(os.path.join(JEST_KLASORU, "*.yaml"))}
    return (adlar - JEST_OLMAYANLAR) or VARSAYILAN_JESTLER


def bos_mu(deger):
    return deger is None or (isinstance(deger, str) and not deger.strip())


def anahtar_bicimi(ifade):
    """Karşılaştırma için: Türkçe küçük harf, noktalamasız ('Wi-Fi' ile 'wi fi' aynı sayılır)."""
    return " ".join(kelimeler(str(ifade)))


def kaydi_denetle(bolum, sira, kayit, rapor, anahtar_sahipleri):
    ad_alani, zorunlular = BOLUMLER[bolum]
    if not isinstance(kayit, dict):
        rapor.hatalar.append(f"{bolum}[{sira}]: kayıt bir sözlük değil")
        return
    ad = kayit.get(ad_alani) or f"{bolum}[{sira}]"
    for alan in zorunlular:
        if alan not in kayit:
            rapor.hatalar.append(f"{bolum} / {ad}: '{alan}' alanı yok")
        elif alan != "anahtarlar" and bos_mu(kayit[alan]):
            rapor.hatalar.append(f"{bolum} / {ad}: '{alan}' boş")
    anahtarlar = kayit.get("anahtarlar")
    if "anahtarlar" in kayit and not anahtarlar:     # alan var ama liste boş: [] ya da hiçbir şey
        rapor.hatalar.append(f"{bolum} / {ad}: anahtar kelime listesi boş")
    if anahtarlar and not isinstance(anahtarlar, list):
        rapor.hatalar.append(f"{bolum} / {ad}: 'anahtarlar' bir liste olmalı: [a, b, c]")
        anahtarlar = []
    if bolum == "yerler" and kayit.get("ad"):
        anahtarlar = [kayit["ad"]] + list(anahtarlar or [])
    for ifade in anahtarlar or []:
        anahtari_kaydet(ifade, f"{bolum} / {ad}", rapor, anahtar_sahipleri)
    jest = kayit.get("jest")
    jestler = bilinen_jestler()
    if jest and jest not in jestler:
        rapor.uyarilar.append(f"{bolum} / {ad}: bilinmeyen jest '{jest}' (bilinenler: {', '.join(sorted(jestler))})")


def anahtari_kaydet(ifade, sahip, rapor, anahtar_sahipleri):
    """Her anahtar kelimenin hangi kayıtta olduğunu tutar; ikinci kayıtta görülürse hata."""
    bicim = anahtar_bicimi(ifade)
    if not bicim:
        rapor.hatalar.append(f"{sahip}: boş anahtar kelime")
        return
    onceki = anahtar_sahipleri.setdefault(bicim, sahip)
    if onceki != sahip:
        rapor.hatalar.append(f"'{bicim}' anahtar kelimesi iki kayıtta: {onceki} ve {sahip}")


def yer_tutuculari_bul(satirlar):
    """'#' ile başlayan açıklama satırları hariç, '...' geçen satırlar: (satır no, metin)."""
    return [(no, s.strip()) for no, s in enumerate(satirlar, 1)
            if not s.strip().startswith("#") and any(y in s for y in YER_TUTUCULAR)]


def denetle(metin):
    """YAML metnini denetler, Rapor döner. Dosyadan bağımsız (testler doğrudan metin verir)."""
    rapor = Rapor()
    try:
        veri = yaml.safe_load(metin)
    except yaml.YAMLError as hata:
        rapor.hatalar.append(f"YAML okunamadı: {hata}")
        return rapor
    if not isinstance(veri, dict):
        rapor.hatalar.append("Dosya boş ya da en üstte 'kurum: ...' gibi alanlar yok")
        return rapor
    for alan in ZORUNLU_UST:
        if bos_mu(veri.get(alan)):
            rapor.hatalar.append(f"'{alan}' alanı yok ya da boş")
    if bos_mu(veri.get("rol")):
        rapor.uyarilar.append("'rol' yok; varsayılan 'tanıtım ve karşılama robotu' kullanılır")
    anahtar_sahipleri = {}
    for bolum in BOLUMLER:
        kayitlar = veri.get(bolum) or []
        rapor.sayilar[bolum] = len(kayitlar)
        for sira, kayit in enumerate(kayitlar, 1):
            kaydi_denetle(bolum, sira, kayit, rapor, anahtar_sahipleri)
    if not any(rapor.sayilar.values()):
        rapor.hatalar.append("Hiç kayıt yok: 'konular', 'yerler' ya da 'sss' bölümlerinden en az biri dolu olmalı")
    rapor.sayilar["anahtar kelime"] = len(anahtar_sahipleri)
    rapor.yer_tutucular = yer_tutuculari_bul(metin.splitlines())
    return rapor


def raporu_yazdir(ad, rapor):
    print(f"\n== {ad} ==")
    for hata in rapor.hatalar:
        print(f"  HATA   {hata}")
    for uyari in rapor.uyarilar:
        print(f"  UYARI  {uyari}")
    if rapor.yer_tutucular:
        print("  Doldurulacak yerler ('...'):")
        for no, satir in rapor.yer_tutucular:
            print(f"    satır {no:>3}: {satir}")
    sayilar = ", ".join(f"{ad} {sayi}" for ad, sayi in rapor.sayilar.items())
    print(f"  Özet: {sayilar} | hata {len(rapor.hatalar)}, uyarı {len(rapor.uyarilar)}, "
          f"'...' olan satır {len(rapor.yer_tutucular)}")


def paket_dosyasi(ad):
    """'universite' -> icerik/universite.yaml; .yaml ile biten ad dosya yolu sayılır."""
    return ad if ad.endswith(".yaml") else os.path.join(KOD_KLASORU, "icerik", ad + ".yaml")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # Windows konsolunda Türkçe harfler
    p = argparse.ArgumentParser(description="İçerik paketi denetleyicisi")
    p.add_argument("paketler", nargs="*", help="universite | tesis | dosya.yaml (boşsa icerik/ içindeki hepsi)")
    p.add_argument("--siki", action="store_true", help="'...' yer tutucularını da hata say")
    sec = p.parse_args(argv)
    dosyalar = [paket_dosyasi(a) for a in sec.paketler] or sorted(glob.glob(os.path.join(KOD_KLASORU, "icerik", "*.yaml")))
    hatali = False
    for yol in dosyalar:
        try:
            with open(yol, encoding="utf-8") as dosya:
                rapor = denetle(dosya.read())
        except OSError as hata:
            rapor = Rapor(hatalar=[f"Dosya açılamadı: {hata}"])
        raporu_yazdir(os.path.basename(yol), rapor)
        hatali = hatali or bool(rapor.hatalar) or (sec.siki and bool(rapor.yer_tutucular))
    print("\nSonuç:", "HATA VAR (çıkış kodu 1)" if hatali else "sorun yok")
    return 1 if hatali else 0


if __name__ == "__main__":
    sys.exit(main())
