"""Pin haritasından ESP32 başlığı üretir: kod/ortak/pinler.json -> kod/esp32/include/pinler.h

Ne yapıyor:
  1. kod/ortak/pinler.json'u okur. Bu dosya pin haritasının TEK KAYNAĞIDIR (sürüm 4, 14.11.2026;
     elektrik tarafının kararı planlama/adim3/pin-haritasi.md, dal lale-duzeltme, §9 önerisinin aynısı).
  2. Denetler (biri tutmazsa HATA, başlık yazılmaz):
       - her pinin "gpio"su ESP32'de gerçekten var olan bir numara (0-39, 20/24/28-31 yok),
       - aynı GPIO iki işe verilmemiş,
       - GPIO 6-11 (modül flaşı) ve 12 (strapping, MTDI; "bos") hiçbir işe verilmemiş,
       - çıkış ("cikis", "pwm") yalnız izinli kümede: rapor Y1'in yedi pini (4, 19, 13, 25, 26, 27, 14)
         + kart üstü LED (2). Yeni bir çıkış gerekiyorsa önce rapor güncellenir, sonra bu küme.
       - 34-39 yalnız giriştir ve dahili pull-up'ı yoktur: "giris_pullup" olamaz,
       - "arm" zamanlaması: ön şarj + K1 sonrası süre, K2'nin en uzun süresinden kısa; K2 en çok 1000 ms
         (rapor Y4) ve ROLE_K2_ONSARJ.en_cok_ms ile aynı,
       - PCA9685 adresi onaltılık sayı, sonar trig kanalları (sonar_sag/orta/sol_trig) tabloda.
  3. kod/esp32/include/pinler.h'yi yazar: PIN_<AD> sabitleri, PCA9685_ADRES, sonar trig kanalları,
     arm zamanlaması (ARM_*_MS) ve PIN_HARITASI_SURUM (firmware yalnız sürüm 4 ile derlenir).

Kullanım (depo kökünden):
  py -3 kod/ortak/pin_uret.py            # pinler.h'yi yazar
  py -3 kod/ortak/pin_uret.py --kontrol  # pinler.h güncel değilse 1 ile çıkar (yazmaz); hata 2

Yalnız standart kütüphane. Çıktı belirlenimcidir (tarih/saat yazılmaz), aynı girdi aynı dosyayı verir.
"""

import argparse
import json
import re
import sys
from pathlib import Path

KLASOR = Path(__file__).resolve().parent
GIRDI = KLASOR / "pinler.json"
CIKTI = KLASOR.parent / "esp32" / "include" / "pinler.h"

# ESP32'de var olan GPIO numaraları (20, 24, 28-31 yok).
GECERLI_GPIO = frozenset(list(range(0, 20)) + [21, 22, 23, 25, 26, 27] + list(range(32, 40)))
FLASH_GPIO = frozenset(range(6, 12))          # modül flaşı: ASLA kullanılmaz
BOS_GPIO = frozenset({12})                    # strapping MTDI: hiçbir şeye bağlanmaz, firmware ayarlamaz
YALNIZ_GIRIS = frozenset(range(34, 40))       # çıkış yok, dahili pull-up / pull-down yok
# Çıkış izni (rapor Y1): röleler 4/19, EN 13, dört PWM 25/26/27/14 + kart üstü LED 2.
CIKIS_IZINLI = frozenset({2, 4, 13, 14, 19, 25, 26, 27})
YONLER = ("analog", "giris", "giris_pullup", "pwm", "cikis", "i2c", "uart")
CIKIS_YONLERI = ("pwm", "cikis")
AD_KALIBI = re.compile(r"^[A-Z][A-Z0-9_]{0,31}$")
SONAR_TRIG = ("sonar_sag_trig", "sonar_orta_trig", "sonar_sol_trig")
ARM_ANAHTARLARI = ("onsarj_bekleme_ms", "k1_sonrasi_ms", "k2_en_cok_ms")
K2_PINI = "ROLE_K2_ONSARJ"
K2_MUTLAK_SINIR_MS = 1000                     # rapor Y4: GPIO19 hiçbir koşulda 1 s'den uzun HIGH kalmaz


class PinHatasi(Exception):
    pass


def _tam_sayi_mi(x):
    return isinstance(x, int) and not isinstance(x, bool)


def pinleri_oku(yol=None):
    """pinler.json -> sözlük (denetlenmemiş). yol None ise depodaki kod/ortak/pinler.json."""
    yol = GIRDI if yol is None else yol
    try:
        return json.loads(Path(yol).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PinHatasi(f"{yol} yok")
    except json.JSONDecodeError as h:
        raise PinHatasi(f"{Path(yol).name} okunamadı: {h}")


def denetle(veri):
    """Pin haritasını denetler; sorun varsa PinHatasi. Denetlenmiş özet sözlük döner:
    {"surum", "pinler": [(ad, tanim), ...], "pca9685": int, "sonar": {ad: kanal}, "arm": {...}}"""
    if not isinstance(veri, dict):
        raise PinHatasi("pinler.json bir nesne (sözlük) olmalı")
    surum = veri.get("surum")
    if not _tam_sayi_mi(surum) or surum < 1:
        raise PinHatasi("'surum' pozitif tam sayı olmalı")
    pinler = veri.get("pinler")
    if not isinstance(pinler, dict) or not pinler:
        raise PinHatasi("'pinler' bölümü yok ya da boş")

    kullanan = {}                       # gpio -> ad (tekrar denetimi)
    for ad, t in pinler.items():
        if not AD_KALIBI.match(ad):
            raise PinHatasi(f"geçersiz pin adı '{ad}' (BÜYÜK harf, rakam, _)")
        if not isinstance(t, dict):
            raise PinHatasi(f"{ad}: tanım bir nesne olmalı")
        gpio, yon = t.get("gpio"), t.get("yon")
        if not _tam_sayi_mi(gpio) or gpio not in GECERLI_GPIO:
            raise PinHatasi(f"{ad}: gpio {gpio!r} ESP32'de yok")
        if gpio in FLASH_GPIO:
            raise PinHatasi(f"{ad}: GPIO{gpio} modül flaşına gider (6-11), kullanılmaz")
        if gpio in BOS_GPIO:
            raise PinHatasi(f"{ad}: GPIO{gpio} strapping (MTDI), boş kalır; hiçbir şeye bağlanmaz")
        if yon not in YONLER:
            raise PinHatasi(f"{ad}: yon {yon!r} bilinmiyor ({', '.join(YONLER)})")
        if gpio in kullanan:
            raise PinHatasi(f"GPIO{gpio} iki kez kullanılmış: {kullanan[gpio]} ve {ad}")
        kullanan[gpio] = ad
        if yon in CIKIS_YONLERI and gpio not in CIKIS_IZINLI:
            raise PinHatasi(f"{ad}: GPIO{gpio} çıkış olamaz; izinli çıkışlar "
                            f"{sorted(CIKIS_IZINLI)} (rapor Y1)")
        if yon == "giris_pullup" and gpio in YALNIZ_GIRIS:
            raise PinHatasi(f"{ad}: GPIO{gpio}'da dahili pull-up yok (34-39); dış direnç + 'giris' yaz")
        if "acilis" in t and t["acilis"] not in (0, 1):
            raise PinHatasi(f"{ad}: acilis 0 ya da 1 olmalı")

    # "bos" bölümünde yazılan pin başka bir işe verilmemiş olmalı (12 zaten yukarıda yakalanır).
    for no in (veri.get("bos") or {}):
        if str(no).isdigit() and int(no) in kullanan:
            raise PinHatasi(f"GPIO{no} 'bos' yazılmış ama {kullanan[int(no)]} kullanıyor")

    adres_metni = str((veri.get("i2c") or {}).get("PCA9685", ""))
    try:
        pca9685 = int(adres_metni, 16)
    except ValueError:
        raise PinHatasi(f"i2c.PCA9685 onaltılık adres olmalı ({adres_metni!r})")
    if not 0x08 <= pca9685 <= 0x77:
        raise PinHatasi(f"i2c.PCA9685 adresi 0x08-0x77 arası olmalı ({adres_metni})")

    kanallar = veri.get("pca9685_kanallar") or {}
    adlar = {}
    for no, ad in kanallar.items():
        if not str(no).isdigit() or not 0 <= int(no) <= 15:
            raise PinHatasi(f"pca9685_kanallar: kanal '{no}' 0-15 olmalı")
        if ad != "yedek" and ad in adlar:
            raise PinHatasi(f"pca9685_kanallar: '{ad}' iki kanalda ({adlar[ad]} ve {no})")
        adlar[ad] = int(no)
    eksik = [a for a in SONAR_TRIG if a not in adlar]
    if eksik:
        raise PinHatasi(f"pca9685_kanallar: eksik sonar trig: {', '.join(eksik)}")

    arm = veri.get("arm")
    if not isinstance(arm, dict):
        raise PinHatasi("'arm' bölümü yok (onsarj_bekleme_ms, k1_sonrasi_ms, k2_en_cok_ms)")
    for a in ARM_ANAHTARLARI:
        if not _tam_sayi_mi(arm.get(a)) or arm[a] <= 0:
            raise PinHatasi(f"arm.{a} pozitif tam sayı (ms) olmalı ({arm.get(a)!r})")
    if arm["k2_en_cok_ms"] > K2_MUTLAK_SINIR_MS:
        raise PinHatasi(f"arm.k2_en_cok_ms en çok {K2_MUTLAK_SINIR_MS} (rapor Y4: GPIO19 1 s'den uzun HIGH kalmaz)")
    if arm["onsarj_bekleme_ms"] + arm["k1_sonrasi_ms"] >= arm["k2_en_cok_ms"]:
        raise PinHatasi("arm: onsarj_bekleme_ms + k1_sonrasi_ms, k2_en_cok_ms'den kısa olmalı "
                        "(yoksa zamanlayıcı K2'yi sıra bitmeden düşürür)")
    k2 = pinler.get(K2_PINI)
    if not isinstance(k2, dict) or k2.get("en_cok_ms") != arm["k2_en_cok_ms"]:
        raise PinHatasi(f"{K2_PINI}.en_cok_ms ile arm.k2_en_cok_ms aynı olmalı")

    return {"surum": surum, "pinler": list(pinler.items()), "pca9685": pca9685,
            "sonar": {a: adlar[a] for a in SONAR_TRIG}, "arm": {a: arm[a] for a in ARM_ANAHTARLARI},
            "kanallar": sorted(((int(n), a) for n, a in kanallar.items()))}


def _ascii(s):
    """Başlık ASCII kalsın (jest_verisi.h gibi); ASCII dışı harf kaçışlanır."""
    return str(s).encode("ascii", "backslashreplace").decode("ascii")


def baslik_uret(veri):
    """Denetlenmiş pinler.json -> pinler.h metni."""
    d = denetle(veri)
    s = [
        "// OTOMATIK URETILDI: kod/ortak/pin_uret.py -- ELLE DUZENLEME.",
        "// Kaynak: kod/ortak/pinler.json (pin haritasi TEK KAYNAK; planlama/adim3/pin-haritasi.md, dal lale-duzeltme)",
        "// Degistirmek icin JSON'u duzenle, sonra: py -3 kod/ortak/pin_uret.py",
        f"// Pin haritasi surum {d['surum']}, tarih {_ascii(veri.get('tarih', '?'))}. "
        f"Cekirdek: {_ascii(veri.get('cekirdek', '?'))}",
        "//",
        "// BU FIRMWARE YALNIZ BU SURUMUN KABLAJINA YUKLENIR (rapor Y1). Eski (0.4.0) firmware yeni kablaja",
        "// yuklenmez; yeni firmware eski kablaja yuklenmez.",
        "//",
        "// Hatirlatma (ayrinti raporda ve kod/esp32/OKU_BENI.md'de):",
        "//  - GPIO 6-11 modul flasi, ASLA kullanilmaz. GPIO12 strapping (MTDI): bos, firmware hic ayarlamaz.",
        "//  - Serial1 / Serial2 / SPI / HSPI varsayilan pinleriyle ACILMAZ (roleler ve motorlar o pinlerde).",
        "//  - 34-39 yalniz giris, dahili pull yok. 4, 19, 13 setup()'in ilk satirlarinda LOW cikis (guc.cpp).",
        "#pragma once",
        "",
        f"#define PIN_HARITASI_SURUM {d['surum']}",
        "",
        "// --- GPIO ---",
    ]
    genislik = max(len(ad) for ad, _ in d["pinler"]) + 4
    for ad, t in d["pinler"]:
        parcalar = [t["yon"]] + [str(t[a]) for a in ("uc", "aktif", "adc", "zayiflatma", "sayac", "donanim", "not")
                                 if a in t]
        tanim = f"#define {('PIN_' + ad).ljust(genislik)} {t['gpio']}"
        s.append(f"{tanim.ljust(genislik + 12)} // {_ascii('; '.join(parcalar))}")
    for no, aciklama in (veri.get("bos") or {}).items():
        s.append(f"// GPIO{no}: BOS -- {_ascii(aciklama)}")
    s.append("")
    s.append("// --- I2C ---")
    s.append(f"#define PCA9685_ADRES 0x{d['pca9685']:02X}")
    for cihaz, adres in (veri.get("i2c") or {}).items():
        if cihaz != "PCA9685":
            s.append(f"// {_ascii(cihaz)}: {_ascii(adres)} (ayni hat, SDA/SCL yukarida)")
    s.append("")
    s.append("// --- PCA9685 kanallari (servo kanallarinin tek kaynagi kod/jestler/kanallar.yaml; burada bilgi) ---")
    s.append("// " + ", ".join(f"{n} {_ascii(a)}" for n, a in d["kanallar"]))
    for ad, kanal in d["sonar"].items():
        s.append(f"#define PCA_KANAL_{ad.upper()} {kanal}")
    s.append("")
    s.append("// --- Devreye alma (arm) zamanlamasi, ms (rapor Y4; guc.cpp) ---")
    aciklama = {"onsarj_bekleme_ms": "K2 (GPIO19) cekildikten sonra bara (GPIO5) LOW beklenir",
                "k1_sonrasi_ms": "K1 (GPIO4) cekildikten sonra K2 birakilir",
                "k2_en_cok_ms": "K2 bundan uzun HIGH kalmaz (esp_timer zorlar)"}
    for a in ARM_ANAHTARLARI:
        s.append(f"#define ARM_{a.upper()} {d['arm'][a]}   // {aciklama[a]}")
    return "\n".join(s) + "\n"


def uret(yol=None):
    return baslik_uret(pinleri_oku(GIRDI if yol is None else yol))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kontrol", action="store_true", help="yazma; pinler.h güncel değilse 1 ile çık")
    args = ap.parse_args(argv)
    try:
        metin = uret()
    except PinHatasi as h:
        print(f"HATA: {h}", file=sys.stderr)
        return 2
    if args.kontrol:
        eski = CIKTI.read_text(encoding="utf-8") if CIKTI.exists() else ""
        if eski != metin:
            print(f"{CIKTI} güncel değil; py -3 kod/ortak/pin_uret.py çalıştır.")
            return 1
        print("pinler.h güncel.")
        return 0
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(metin, encoding="utf-8", newline="\n")
    veri = pinleri_oku()
    print(f"{CIKTI} yazıldı: pin haritası sürüm {veri['surum']}, {len(veri['pinler'])} pin")
    return 0


if __name__ == "__main__":
    sys.exit(main())
