"""Jest YAML dosyalarından ESP32 başlığı üretir: kod/esp32/src/jest_verisi.h

Ne yapıyor:
  1. kanallar.yaml'dan servo tablosunu okur (kanal no, darbe aralığı, açı sınırı, hız, ayna).
  2. Bu klasördeki diğer *.yaml dosyalarını jest olarak okur (her dosya bir jest).
  3. Her jesti denetler (sınır dışı açı, sırasız zaman, bilinmeyen kanal -> HATA, çok hızlı -> UYARI).
  4. Her karede her kanalın açısını doldurur (yazılmayan kare = komşu karelerden doğrusal ara değer)
     ve C++ dizisi olarak yazar. ESP32 bu diziyi oynatır.
  5. Jestte isteğe bağlı "yonler:" bölümü varsa yön varyantlarını da üretir (aynı denetimlerle):
       yonler:
         sag: varsayilan      # "kareler" olduğu gibi (başlıkta kopya yok, aynı dizi)
         sol: ayna            # "kareler"in sol/sağ aynası (kanallar.yaml ayna + ayna_aci)
         ileri:               # ya da kendi kare listesi
           - {ms: 0, ...}
     Yön adları: sol, sag, ileri, arka (seri protokoldeki "yon"). Yazılmayan yön için ESP32
     varsayılan kareleri oynatır ve cevaba "yon_uygulandi":false yazar.

Kullanım (depo kökünden):
  py -3 kod/jestler/jest_uret.py            # başlığı yazar
  py -3 kod/jestler/jest_uret.py --kontrol  # başlık güncel değilse 1 ile çıkar (yazmaz)

Yalnız pyyaml gerekir. Çıktı belirlenimcidir (tarih/saat yazılmaz), aynı girdi aynı dosyayı verir.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

KLASOR = Path(__file__).resolve().parent
KANAL_DOSYASI = KLASOR / "kanallar.yaml"
CIKTI = KLASOR.parent / "esp32" / "src" / "jest_verisi.h"
BOSTA_ADI = "bosta"
AD_KALIBI = re.compile(r"^[a-z][a-z0-9_]{0,23}$")   # ESP32'de komut adı olarak kullanılır
ACI_YOK = -1.0                                       # "bu jest bu kanala dokunmaz"
# Seri protokoldeki "yon" değerleri; sıra jest_verisi.h YON_ADLARI ve JestTanim dizileriyle aynı.
YONLER = ("sol", "sag", "ileri", "arka")
# kanallar.yaml "ayna_aci": ayna kanala geçerken açı nasıl dönüşür (bkz. AYNA KURALI orada).
AYNA_DONUSUMLERI = {"ayni": lambda a: a, "180-aci": lambda a: 180 - a}


class JestHatasi(Exception):
    pass


def kanallari_oku(yol=KANAL_DOSYASI):
    """kanallar.yaml -> (pwm_frekans, [kanal sözlüğü, ...]) ; liste kanal numarasına göre sıralı."""
    veri = yaml.safe_load(yol.read_text(encoding="utf-8"))
    kanallar = []
    for ad, k in (veri.get("kanallar") or {}).items():
        if not AD_KALIBI.match(ad):
            raise JestHatasi(f"kanallar.yaml: geçersiz kanal adı '{ad}' (küçük harf, rakam, _)")
        gerekli = ["kanal", "model", "min_us", "max_us", "min_aci", "max_aci", "hiz"]
        eksik = [a for a in gerekli if a not in k]
        if eksik:
            raise JestHatasi(f"kanallar.yaml: {ad} için eksik alan: {', '.join(eksik)}")
        if not 0 <= k["kanal"] <= 15:
            raise JestHatasi(f"kanallar.yaml: {ad} kanalı 0-15 olmalı")
        if not 400 <= k["min_us"] < k["max_us"] <= 2600:
            raise JestHatasi(f"kanallar.yaml: {ad} darbe aralığı 400-2600 us içinde ve min<max olmalı")
        if not 0 <= k["min_aci"] < k["max_aci"] <= 180:
            raise JestHatasi(f"kanallar.yaml: {ad} açı sınırı 0-180 içinde ve min<max olmalı")
        if k["hiz"] <= 0:
            raise JestHatasi(f"kanallar.yaml: {ad} hızı pozitif olmalı")
        # ayna yazılmamışsa kanal kendi aynasıdır, açı aynen (ör. ortadaki bir kanal)
        kanallar.append(dict(k, ad=ad, ters=bool(k.get("ters", False)),
                             ayna=str(k.get("ayna", ad)), ayna_aci=str(k.get("ayna_aci", "ayni"))))
    numaralar = [k["kanal"] for k in kanallar]
    if len(set(numaralar)) != len(numaralar):
        raise JestHatasi("kanallar.yaml: aynı kanal numarası iki kez kullanılmış")
    if not kanallar:
        raise JestHatasi("kanallar.yaml: hiç kanal yok")
    adlar = {k["ad"]: k for k in kanallar}
    for k in kanallar:
        if k["ayna"] not in adlar:
            raise JestHatasi(f"kanallar.yaml: {k['ad']} aynası '{k['ayna']}' tabloda yok")
        if k["ayna_aci"] not in AYNA_DONUSUMLERI:
            raise JestHatasi(f"kanallar.yaml: {k['ad']} ayna_aci '{k['ayna_aci']}' geçersiz "
                             f"({', '.join(AYNA_DONUSUMLERI)})")
    for k in kanallar:
        karsi = adlar[k["ayna"]]
        if karsi["ayna"] != k["ad"] or karsi["ayna_aci"] != k["ayna_aci"]:
            raise JestHatasi(f"kanallar.yaml: ayna karşılıklı değil: {k['ad']} -> {karsi['ad']} ama "
                             f"{karsi['ad']} -> {karsi['ayna']} ({karsi['ayna_aci']})")
    kanallar.sort(key=lambda k: k["kanal"])
    return veri.get("pwm_frekans", 50), kanallar


def _kareleri_isle(kareler, etiket, kanallar):
    """Ham kare listesini denetler, boşlukları doldurur; ([(ms, [açı | ACI_YOK, ...]), ...], uyarilar)."""
    if not isinstance(kareler, list) or not kareler:
        raise JestHatasi(f"{etiket}: hiç kare yok")
    sira = {k["ad"]: i for i, k in enumerate(kanallar)}
    onceki_ms = -1
    for n, kare in enumerate(kareler):
        if not isinstance(kare, dict) or "ms" not in kare:
            raise JestHatasi(f"{etiket}: {n + 1}. karede 'ms' yok")
        if not isinstance(kare["ms"], int) or not 0 <= kare["ms"] <= 65000:
            raise JestHatasi(f"{etiket}: {n + 1}. karede ms 0-65000 arası tam sayı olmalı")
        if kare["ms"] <= onceki_ms:
            raise JestHatasi(f"{etiket}: {n + 1}. kare zamanı bir öncekinden büyük olmalı")
        onceki_ms = kare["ms"]
        for anahtar, aci in kare.items():
            if anahtar == "ms":
                continue
            if anahtar not in sira:
                raise JestHatasi(f"{etiket}: bilinmeyen kanal '{anahtar}' (kanallar.yaml'a bak)")
            k = kanallar[sira[anahtar]]
            if not isinstance(aci, (int, float)) or not k["min_aci"] <= aci <= k["max_aci"]:
                raise JestHatasi(f"{etiket}: {n + 1}. kare {anahtar}={aci} sınır dışı "
                                 f"({k['min_aci']}-{k['max_aci']})")
    if len(kareler) > 255:
        raise JestHatasi(f"{etiket}: en çok 255 kare")

    # Kullanılan her kanal ilk karede olmalı (yoksa jest başında ne yapacağı belirsiz kalır).
    kullanilan = {a for kare in kareler for a in kare if a != "ms"}
    ilk_eksik = sorted(kullanilan - set(kareler[0]))
    if ilk_eksik:
        raise JestHatasi(f"{etiket}: ilk karede eksik kanal: {', '.join(ilk_eksik)} "
                         "(jestte kullanılan her kanal ilk karede yazılmalı)")

    # Her kanal için boşlukları doldur: iki yazılı kare arası doğrusal, son yazılı kareden sonra sabit.
    tablo = [[ACI_YOK] * len(kanallar) for _ in kareler]
    uyarilar = []
    for kanal_ad in sorted(kullanilan):
        i = sira[kanal_ad]
        yazili = [(n, kare["ms"], float(kare[kanal_ad])) for n, kare in enumerate(kareler) if kanal_ad in kare]
        for (n0, t0, a0), (n1, t1, a1) in zip(yazili, yazili[1:]):
            hiz = abs(a1 - a0) / (t1 - t0) * 1000.0
            if hiz > kanallar[i]["hiz"]:
                uyarilar.append(f"{etiket}: {kanal_ad} {t0}->{t1} ms arası {hiz:.0f} der/s isteniyor, "
                                f"sınır {kanallar[i]['hiz']} der/s; servo geride kalır")
            for n in range(n0, n1 + 1):
                t = kareler[n]["ms"]
                tablo[n][i] = a0 + (a1 - a0) * (t - t0) / (t1 - t0)
        n_son, _, a_son = yazili[-1]
        for n in range(n_son, len(kareler)):
            tablo[n][i] = a_son
    return [(kare["ms"], satir) for kare, satir in zip(kareler, tablo)], uyarilar


def ayna_kareler(kareler, kanallar):
    """Ham kare listesinin sol/sağ aynası: her kanal 'ayna'sına taşınır, açısı 'ayna_aci' ile dönüşür.
    Sonuç yine ham kare listesidir; sınır denetimini _kareleri_isle yapar."""
    tablo = {k["ad"]: k for k in kanallar}
    sonuc = []
    for kare in kareler:
        yeni = {"ms": kare["ms"]}
        for anahtar, aci in kare.items():
            if anahtar == "ms":
                continue
            k = tablo[anahtar]
            yeni[k["ayna"]] = AYNA_DONUSUMLERI[k["ayna_aci"]](aci)
        sonuc.append(yeni)
    return sonuc


def _yonleri_oku(ham, kareler, zamanli, dosya, kanallar):
    """'yonler:' bölümü -> ({yon: (tur, zamanli)}, uyarilar); tur: varsayilan | ayna | kareler.
    Sözlük YONLER sırasında; yazılmayan yön sözlükte yoktur."""
    if ham is None:
        return {}, []
    if not isinstance(ham, dict):
        raise JestHatasi(f"{dosya}: 'yonler' bir sözlük olmalı (sol/sag/ileri/arka)")
    bulunan, uyarilar = {}, []
    for yon, tanim in ham.items():
        if yon not in YONLER:
            raise JestHatasi(f"{dosya}: bilinmeyen yön '{yon}' (geçerli: {', '.join(YONLER)})")
        etiket = f"{dosya} yonler.{yon}"
        if tanim == "varsayilan":
            bulunan[yon] = ("varsayilan", zamanli)          # aynı liste: başlıkta aynı dizi
        elif tanim == "ayna":
            z, u = _kareleri_isle(ayna_kareler(kareler, kanallar), etiket, kanallar)
            bulunan[yon] = ("ayna", z)
            uyarilar += u
        elif isinstance(tanim, list):
            z, u = _kareleri_isle(tanim, etiket, kanallar)
            bulunan[yon] = ("kareler", z)
            uyarilar += u
        else:
            raise JestHatasi(f"{etiket}: 'varsayilan', 'ayna' ya da kare listesi olmalı")
    return {y: bulunan[y] for y in YONLER if y in bulunan}, uyarilar


def jest_oku(yol, kanallar):
    """Bir jest dosyasını okur, denetler.
    (ad, aciklama, [(ms, [açı | ACI_YOK, ...]), ...], uyarilar, yonler) döner; yonler: _yonleri_oku."""
    veri = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
    ad = veri.get("ad", yol.stem)
    if ad != yol.stem:
        raise JestHatasi(f"{yol.name}: 'ad: {ad}' dosya adıyla aynı olmalı ({yol.stem})")
    if not AD_KALIBI.match(ad):
        raise JestHatasi(f"{yol.name}: geçersiz jest adı '{ad}' (küçük harf, rakam, _; en çok 24)")
    kareler = veri.get("kareler") or []
    zamanli, uyarilar = _kareleri_isle(kareler, yol.name, kanallar)
    yonler, u = _yonleri_oku(veri.get("yonler"), kareler, zamanli, yol.name, kanallar)
    return ad, str(veri.get("aciklama", "")), zamanli, uyarilar + u, yonler


def jestleri_oku(kanallar, klasor=KLASOR):
    """-> ([(ad, aciklama, kareler, yonler), ...], bosta_son, uyarilar)"""
    jestler, uyarilar = [], []
    for yol in sorted(klasor.glob("*.yaml")):
        if yol.name == KANAL_DOSYASI.name:
            continue
        ad, aciklama, kareler, u, yonler = jest_oku(yol, kanallar)
        jestler.append((ad, aciklama, kareler, yonler))
        uyarilar += u
    adlar = [j[0] for j in jestler]
    if BOSTA_ADI not in adlar:
        raise JestHatasi(f"{BOSTA_ADI}.yaml yok; boşta duruşu bu dosyanın son karesinden alınır")
    bosta_kareleri = next(j[2] for j in jestler if j[0] == BOSTA_ADI)
    bosta_son = bosta_kareleri[-1][1]          # son karenin açı listesi
    if ACI_YOK in bosta_son:
        raise JestHatasi(f"{BOSTA_ADI}.yaml son karesi tüm kanalları yazmalı")
    return jestler, bosta_son, uyarilar


def yon_bellek_bayt(jestler):
    """Yön varyantlarının ek flash maliyeti (bayt, yaklaşık): ayrı kare dizileri.
    ESP32'de sizeof(JestKare) = uint16_t ms + 2 bayt dolgu + SERVO_SAYISI float.
    'varsayilan' varyant kopya değildir (0 bayt). JestTanim'deki sabit ek alanlar dahil değil."""
    bayt = 0
    for _, _, _, yonler in jestler:
        for tur, z in yonler.values():
            if tur != "varsayilan":
                bayt += sum(4 + 4 * len(acilar) for _, acilar in z)
    return bayt


def _c_metin(s):
    """Python metnini C dizgesine çevirir. Adlar zaten ASCII (AD_KALIBI); yine de ASCII dışını kaçışlar."""
    return '"' + s.encode("utf-8").decode("ascii", "backslashreplace").replace('"', "'") + '"'


def _sayi(x):
    return f"{x:.1f}f"


def _dizi_adi(ad, yon=None):
    return f"JEST_{ad.upper()}" + (f"_{yon.upper()}" if yon else "")


def _kare_dizisi(s, dizi, kareler):
    s.append(f"static const JestKare {dizi}[] = {{")
    for ms, acilar in kareler:
        s.append(f"  {{{ms}, {{" + ", ".join("ACI_YOK" if a == ACI_YOK else _sayi(a) for a in acilar) + "}},")
    s.append("};")
    s.append("")


def baslik_uret(pwm_frekans, kanallar, jestler, bosta):
    s = []
    s.append("// OTOMATIK URETILDI: kod/jestler/jest_uret.py -- ELLE DUZENLEME.")
    s.append("// Kaynak: kod/jestler/kanallar.yaml ve kod/jestler/*.yaml")
    s.append("// Degistirmek icin YAML'i duzenle, sonra: py -3 kod/jestler/jest_uret.py")
    s.append("// Bu dosya yalniz servolar.cpp ve jestler.cpp tarafindan include edilir.")
    s.append("#pragma once")
    s.append("#include <stdint.h>")
    s.append("")
    s.append(f"#define SERVO_PWM_FREKANS {int(pwm_frekans)}")
    s.append(f"#define SERVO_SAYISI {len(kanallar)}")
    s.append(f"#define JEST_SAYISI {len(jestler)}")
    s.append(f"#define YON_SAYISI {len(YONLER)}")
    s.append("#define ACI_YOK (-1.0f)   // bu jest bu kanala dokunmaz")
    s.append("")
    s.append("// Seri protokoldeki \"yon\" degerleri; JestTanim.yon_* dizilerinin sirasi.")
    s.append("static const char* const YON_ADLARI[YON_SAYISI] = {"
             + ", ".join(_c_metin(y) for y in YONLER) + "};")
    s.append("")
    s.append("struct ServoTanim {")
    s.append("  const char* ad;      // kanallar.yaml'daki ad (ör. sag_omuz)")
    s.append("  uint8_t kanal;       // PCA9685 cikisi 0-15")
    s.append("  uint16_t min_us;     // servo acisi 0 derecedeki darbe")
    s.append("  uint16_t max_us;     // servo acisi 180 derecedeki darbe")
    s.append("  float min_aci;       // izin verilen robot acisi (alt)")
    s.append("  float max_aci;       // izin verilen robot acisi (ust)")
    s.append("  float hiz;           // en fazla derece/saniye")
    s.append("  bool ters;           // true: servo acisi = 180 - robot acisi")
    s.append("};")
    s.append("")
    s.append("struct JestKare {")
    s.append("  uint16_t ms;                 // jest basindan beri gecen sure")
    s.append("  float aci[SERVO_SAYISI];     // her kanalin robot acisi; ACI_YOK = dokunma")
    s.append("};")
    s.append("")
    s.append("struct JestTanim {")
    s.append("  const char* ad;")
    s.append("  const JestKare* kareler;                    // varsayilan (yon yok ya da varyanti yok)")
    s.append("  uint8_t kare_sayisi;")
    s.append("  const JestKare* yon_kareleri[YON_SAYISI];   // YON_ADLARI sirasi; nullptr = varyant yok")
    s.append("  uint8_t yon_kare_sayisi[YON_SAYISI];")
    s.append("};")
    s.append("")
    s.append("// Dizi sirasi = kanal numarasi sirasi (SERVO_TABLOSU[i].kanal ile PCA9685 cikisi bulunur)")
    s.append("// Ayna (yonlu jest 'sol' varyanti) uretim aninda uygulanir; burada yalniz bilgi icin yazili.")
    s.append("static const ServoTanim SERVO_TABLOSU[SERVO_SAYISI] = {")
    for k in kanallar:
        s.append(f"  {{{_c_metin(k['ad'])}, {k['kanal']}, {k['min_us']}, {k['max_us']}, "
                 f"{_sayi(k['min_aci'])}, {_sayi(k['max_aci'])}, {_sayi(k['hiz'])}, "
                 f"{'true' if k['ters'] else 'false'}}},  // {k['model']}, ayna: {k['ayna']} ({k['ayna_aci']})")
    s.append("};")
    s.append("")
    s.append(f"// Bosta durus: {BOSTA_ADI}.yaml son karesi. Acilista ve her jest bitince servolar buraya doner.")
    s.append("static const float BOSTA_DURUS[SERVO_SAYISI] = {"
             + ", ".join(_sayi(a) for a in bosta) + "};")
    s.append("")
    sutunlar = ", ".join(k["ad"] for k in kanallar)
    for ad, aciklama, kareler, yonler in jestler:
        s.append(f"// {ad}: {' '.join(aciklama.split())}")
        s.append(f"//   sutunlar: {sutunlar}")
        _kare_dizisi(s, _dizi_adi(ad), kareler)
        for yon, (tur, z) in yonler.items():
            if tur == "varsayilan":
                continue
            s.append(f"// {ad} yon={yon} ({'varsayilanin aynasi' if tur == 'ayna' else 'kendi kareleri'})")
            _kare_dizisi(s, _dizi_adi(ad, yon), z)
    s.append(f"// {{ad, varsayilan, kare sayisi, {{{', '.join(YONLER)}}} kareleri, ayni sirada kare sayilari}}")
    s.append("static const JestTanim JEST_TABLOSU[JEST_SAYISI] = {")
    for ad, _, kareler, yonler in jestler:
        isaretciler, sayilar = [], []
        for yon in YONLER:
            if yon not in yonler:
                isaretciler.append("nullptr")
                sayilar.append("0")
                continue
            tur, z = yonler[yon]
            isaretciler.append(_dizi_adi(ad) if tur == "varsayilan" else _dizi_adi(ad, yon))
            sayilar.append(str(len(z)))
        s.append(f"  {{{_c_metin(ad)}, {_dizi_adi(ad)}, {len(kareler)}, "
                 f"{{{', '.join(isaretciler)}}}, {{{', '.join(sayilar)}}}}},")
    s.append("};")
    return "\n".join(s) + "\n"


def uret():
    pwm, kanallar = kanallari_oku()
    jestler, bosta, uyarilar = jestleri_oku(kanallar)
    return baslik_uret(pwm, kanallar, jestler, bosta), jestler, uyarilar


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kontrol", action="store_true", help="yazma; başlık güncel değilse 1 ile çık")
    args = ap.parse_args(argv)
    try:
        metin, jestler, uyarilar = uret()
    except JestHatasi as h:
        print(f"HATA: {h}", file=sys.stderr)
        return 2
    for u in uyarilar:
        print(f"UYARI: {u}")
    if args.kontrol:
        mevcut = CIKTI.read_text(encoding="utf-8") if CIKTI.exists() else ""
        if mevcut != metin:
            print(f"{CIKTI} güncel değil; py -3 kod/jestler/jest_uret.py çalıştır.")
            return 1
        print("jest_verisi.h güncel.")
        return 0
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(metin, encoding="utf-8", newline="\n")
    print(f"{CIKTI} yazıldı: {len(jestler)} jest ({', '.join(j[0] for j in jestler)})")
    yonlu = [f"{j[0]}({','.join(j[3])})" for j in jestler if j[3]]
    if yonlu:
        print(f"Yön varyantları: {' '.join(yonlu)}; ek kare dizileri ~{yon_bellek_bayt(jestler)} bayt flash")
    return 0


if __name__ == "__main__":
    sys.exit(main())
