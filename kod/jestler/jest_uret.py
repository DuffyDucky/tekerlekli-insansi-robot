"""Jest YAML dosyalarından ESP32 başlıkları üretir: kod/esp32/src/jest_verisi.h ve sinirlar_verisi.h

Ne yapıyor:
  1. kanallar.yaml'dan servo tablosunu okur (kanal no, darbe aralığı, hız, ayna, eklem + eklem_ofset).
     Açı sınırı kod/ortak/eklem_sinirlari.json'dan türetilir (TEK KAYNAK, Ahmet'in CAD betiği üretir):
       robot açısı = eklem açısı + eklem_ofset   ->   min_aci = eklem.min + ofset, max_aci = eklem.max + ofset
     kanallar.yaml'da min_aci/max_aci elle yazılırsa HATA.
  2. Bu klasördeki diğer *.yaml dosyalarını jest olarak okur (her dosya bir jest).
  3. Her jesti denetler (sınır dışı açı, sırasız zaman, bilinmeyen kanal -> HATA, çok hızlı -> UYARI).
     JSON'daki "bagimli" kısıtı (ör. S1 >= 120 iken S2 <= 117, eklem açısıyla) robot açısına çevrilip
     her karede ve kareler arasındaki doğrusal yolda denetlenir; ihlal -> HATA. Kısıtın kanalı jestte
     yoksa (o anki açısı bilinmez) -> UYARI.
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
  6. JSON'daki teker.ivme_sinir_m_s2 dört değerini (duz_surus, duz_fren, rampa_surus, rampa_fren)
     kod/esp32/src/sinirlar_verisi.h'ye yazar (motorlar.cpp kullanır).

Kullanım (depo kökünden):
  py -3 kod/jestler/jest_uret.py            # iki başlığı yazar
  py -3 kod/jestler/jest_uret.py --kontrol  # başlıklardan biri güncel değilse 1 ile çıkar (yazmaz)

Yalnız pyyaml gerekir. Çıktı belirlenimcidir (tarih/saat yazılmaz), aynı girdi aynı dosyayı verir.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

import yaml

KLASOR = Path(__file__).resolve().parent
KANAL_DOSYASI = KLASOR / "kanallar.yaml"
EKLEM_DOSYASI = KLASOR.parent / "ortak" / "eklem_sinirlari.json"
CIKTI = KLASOR.parent / "esp32" / "src" / "jest_verisi.h"
SINIR_CIKTI = KLASOR.parent / "esp32" / "src" / "sinirlar_verisi.h"
IVME_ANAHTARLARI = ("duz_surus", "duz_fren", "rampa_surus", "rampa_fren")   # m/s^2
ARA_ADIM = 10              # bağımlı kısıt: iki kare arası bu kadar parçaya bölünüp denetlenir
BOSTA_ADI = "bosta"
AD_KALIBI = re.compile(r"^[a-z][a-z0-9_]{0,23}$")   # ESP32'de komut adı olarak kullanılır
ACI_YOK = -1.0                                       # "bu jest bu kanala dokunmaz"
# Seri protokoldeki "yon" değerleri; sıra jest_verisi.h YON_ADLARI ve JestTanim dizileriyle aynı.
YONLER = ("sol", "sag", "ileri", "arka")
# kanallar.yaml "ayna_aci": ayna kanala geçerken açı nasıl dönüşür (bkz. AYNA KURALI orada).
AYNA_DONUSUMLERI = {"ayni": lambda a: a, "180-aci": lambda a: 180 - a}


class JestHatasi(Exception):
    pass


def _sayi_mi(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _sade(x):
    """1.0 -> 1 (başlık ve test çıktısı sade kalsın); kesirli değer aynen kalır."""
    return int(x) if float(x).is_integer() else float(x)


def eklem_oku(yol=EKLEM_DOSYASI):
    """kod/ortak/eklem_sinirlari.json -> sözlük (eklemler, bagimli, teker, ...)."""
    try:
        veri = json.loads(Path(yol).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise JestHatasi(f"{yol} yok; git show origin/lale-duzeltme:kod/ortak/eklem_sinirlari.json ile al")
    except json.JSONDecodeError as h:
        raise JestHatasi(f"{Path(yol).name} okunamadı: {h}")
    if not isinstance(veri.get("eklemler"), dict) or not veri["eklemler"]:
        raise JestHatasi(f"{Path(yol).name}: 'eklemler' bölümü yok")
    return veri


def kanallari_oku(yol=KANAL_DOSYASI, sinirlar=None):
    """kanallar.yaml (+ eklem_sinirlari.json) -> (pwm_frekans, [kanal sözlüğü, ...]);
    liste kanal numarasına göre sıralı. min_aci/max_aci JSON'dan ofsetle türetilir.
    sinirlar: eklem_oku() sözlüğü; None ise depodaki JSON okunur."""
    if sinirlar is None:
        sinirlar = eklem_oku()
    eklemler = sinirlar["eklemler"]
    veri = yaml.safe_load(Path(yol).read_text(encoding="utf-8"))
    kanallar = []
    for ad, k in (veri.get("kanallar") or {}).items():
        if not AD_KALIBI.match(ad):
            raise JestHatasi(f"kanallar.yaml: geçersiz kanal adı '{ad}' (küçük harf, rakam, _)")
        elle = [a for a in ("min_aci", "max_aci") if a in k]
        if elle:
            raise JestHatasi(f"kanallar.yaml: {ad} {'/'.join(elle)} elle yazılmaz; sınır "
                             "kod/ortak/eklem_sinirlari.json'dan eklem + eklem_ofset ile türetilir")
        gerekli = ["kanal", "model", "min_us", "max_us", "eklem", "eklem_ofset", "hiz"]
        eksik = [a for a in gerekli if a not in k]
        if eksik:
            raise JestHatasi(f"kanallar.yaml: {ad} için eksik alan: {', '.join(eksik)}")
        if not 0 <= k["kanal"] <= 15:
            raise JestHatasi(f"kanallar.yaml: {ad} kanalı 0-15 olmalı")
        if not 400 <= k["min_us"] < k["max_us"] <= 2600:
            raise JestHatasi(f"kanallar.yaml: {ad} darbe aralığı 400-2600 us içinde ve min<max olmalı")
        eklem = str(k["eklem"])
        if eklem not in eklemler:
            raise JestHatasi(f"kanallar.yaml: {ad} eklemi '{eklem}' eklem_sinirlari.json'da yok "
                             f"({', '.join(eklemler)})")
        e = eklemler[eklem]
        if not (_sayi_mi(e.get("min")) and _sayi_mi(e.get("max")) and e["min"] < e["max"]):
            raise JestHatasi(f"eklem_sinirlari.json: {eklem} min/max sayı olmalı ve min<max")
        if not _sayi_mi(k["eklem_ofset"]):
            raise JestHatasi(f"kanallar.yaml: {ad} eklem_ofset sayı olmalı")
        min_aci = _sade(e["min"] + k["eklem_ofset"])
        max_aci = _sade(e["max"] + k["eklem_ofset"])
        if not 0 <= min_aci < max_aci <= 180:
            raise JestHatasi(f"kanallar.yaml: {ad} türetilen açı sınırı {min_aci}-{max_aci} 0-180 içinde "
                             f"olmalı ({eklem} {e['min']}...{e['max']} + ofset {k['eklem_ofset']}); "
                             "eklem_ofset'i düzelt")
        if k["hiz"] <= 0:
            raise JestHatasi(f"kanallar.yaml: {ad} hızı pozitif olmalı")
        # ayna yazılmamışsa kanal kendi aynasıdır, açı aynen (ör. ortadaki bir kanal)
        kanallar.append(dict(k, ad=ad, eklem=eklem, min_aci=min_aci, max_aci=max_aci,
                             ters=bool(k.get("ters", False)),
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


def bagimli_kurallari(sinirlar, kanallar):
    """JSON 'bagimli' listesi -> robot açısıyla kurallar:
    [{"ad": ..., "kosul": {kanal_adi: (alt, ust)}, "sinir": {kanal_adi: (alt, ust)}}, ...]
    Anlamı: koşuldaki her kanal kendi aralığındaysa, sınırdaki her kanal da kendi aralığında olmalı.
    Eklemi bu kanal tablosunda olmayan kural atlanır (ör. testlerdeki küçük tablolar)."""
    eklemden = {k["eklem"]: k for k in kanallar}
    kurallar = []
    for n, b in enumerate(sinirlar.get("bagimli") or []):
        if not isinstance(b, dict) or not isinstance(b.get("kosul"), dict) or not isinstance(b.get("sinir"), dict):
            raise JestHatasi(f"eklem_sinirlari.json: bagimli[{n}] 'kosul' ve 'sinir' sözlüğü olmalı")
        kural = {"ad": str(b.get("ad", f"bagimli[{n}]")), "kosul": {}, "sinir": {}}
        tabloda = True
        for bolum in ("kosul", "sinir"):
            for eklem, aralik in b[bolum].items():
                if not (isinstance(aralik, list) and len(aralik) == 2 and all(_sayi_mi(x) for x in aralik)
                        and aralik[0] <= aralik[1]):
                    raise JestHatasi(f"eklem_sinirlari.json: bagimli[{n}].{bolum}.{eklem} [alt, ust] olmalı")
                if eklem not in eklemden:
                    tabloda = False
                    continue
                k = eklemden[eklem]
                kural[bolum][k["ad"]] = (float(aralik[0] + k["eklem_ofset"]), float(aralik[1] + k["eklem_ofset"]))
        if tabloda:
            kurallar.append(kural)
    return kurallar


def _aralik_metni(sozluk):
    return ", ".join(f"{ad} {lo:g}-{hi:g}" for ad, (lo, hi) in sozluk.items())


def _bagimli_denetle(satirlar, etiket, kanallar, kurallar):
    """Doldurulmuş kareleri (ve iki kare arasını ARA_ADIM parçada) bağımlı kısıtlara karşı denetler.
    İhlal -> JestHatasi. Koşul sağlanıp sınır kanalı jestte yoksa (açısı bilinmez) -> uyarı listesi.
    Not: ESP32'de her servo kendi hız sınırıyla gider; gerçek yol doğrusal ara değerden biraz sapabilir."""
    sira = {k["ad"]: i for i, k in enumerate(kanallar)}
    uyarilar, uyarilan = [], set()
    pay = 1e-6
    for n, (ms, acilar) in enumerate(satirlar):
        noktalar = [(f"{n + 1}. karede", acilar)]
        if n + 1 < len(satirlar):
            ms1, sonraki = satirlar[n + 1]
            for s in range(1, ARA_ADIM):
                oran = s / ARA_ADIM
                ara = [ACI_YOK if a == ACI_YOK or b == ACI_YOK else a + (b - a) * oran
                       for a, b in zip(acilar, sonraki)]
                noktalar.append((f"{n + 1}.-{n + 2}. kare arası (~{ms + (ms1 - ms) * oran:.0f} ms)", ara))
        for yer, nokta in noktalar:
            for kural in kurallar:
                if not all(nokta[sira[ad]] != ACI_YOK and lo - pay <= nokta[sira[ad]] <= hi + pay
                           for ad, (lo, hi) in kural["kosul"].items()):
                    continue
                for ad, (lo, hi) in kural["sinir"].items():
                    aci = nokta[sira[ad]]
                    if aci == ACI_YOK:
                        if (kural["ad"], ad) not in uyarilan:
                            uyarilan.add((kural["ad"], ad))
                            uyarilar.append(f"{etiket}: {ad} jestte yok; '{kural['ad']}' kısıtı denetlenemedi "
                                            f"({_aralik_metni(kural['kosul'])} iken {ad} {lo:g}-{hi:g} olmalı)")
                    elif not lo - pay <= aci <= hi + pay:
                        raise JestHatasi(f"{etiket}: bağımlı kısıt ihlali ('{kural['ad']}') {yer}: "
                                         f"{_aralik_metni(kural['kosul'])} iken {ad} {lo:g}-{hi:g} olmalı, "
                                         f"{aci:.1f} isteniyor (kod/ortak/eklem_sinirlari.json 'bagimli')")
    return uyarilar


def _kareleri_isle(kareler, etiket, kanallar, kurallar=()):
    """Ham kare listesini denetler, boşlukları doldurur; ([(ms, [açı | ACI_YOK, ...]), ...], uyarilar).
    kurallar: bagimli_kurallari() çıktısı; doldurulmuş kareler bunlara karşı da denetlenir."""
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
    satirlar = [(kare["ms"], satir) for kare, satir in zip(kareler, tablo)]
    uyarilar += _bagimli_denetle(satirlar, etiket, kanallar, kurallar)
    return satirlar, uyarilar


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


def _yonleri_oku(ham, kareler, zamanli, dosya, kanallar, kurallar=()):
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
            z, u = _kareleri_isle(ayna_kareler(kareler, kanallar), etiket, kanallar, kurallar)
            bulunan[yon] = ("ayna", z)
            uyarilar += u
        elif isinstance(tanim, list):
            z, u = _kareleri_isle(tanim, etiket, kanallar, kurallar)
            bulunan[yon] = ("kareler", z)
            uyarilar += u
        else:
            raise JestHatasi(f"{etiket}: 'varsayilan', 'ayna' ya da kare listesi olmalı")
    return {y: bulunan[y] for y in YONLER if y in bulunan}, uyarilar


def jest_oku(yol, kanallar, kurallar=None):
    """Bir jest dosyasını okur, denetler.
    (ad, aciklama, [(ms, [açı | ACI_YOK, ...]), ...], uyarilar, yonler) döner; yonler: _yonleri_oku.
    kurallar: bagimli_kurallari(); None ise depodaki eklem_sinirlari.json'dan kurulur."""
    if kurallar is None:
        kurallar = bagimli_kurallari(eklem_oku(), kanallar)
    veri = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
    ad = veri.get("ad", yol.stem)
    if ad != yol.stem:
        raise JestHatasi(f"{yol.name}: 'ad: {ad}' dosya adıyla aynı olmalı ({yol.stem})")
    if not AD_KALIBI.match(ad):
        raise JestHatasi(f"{yol.name}: geçersiz jest adı '{ad}' (küçük harf, rakam, _; en çok 24)")
    kareler = veri.get("kareler") or []
    zamanli, uyarilar = _kareleri_isle(kareler, yol.name, kanallar, kurallar)
    yonler, u = _yonleri_oku(veri.get("yonler"), kareler, zamanli, yol.name, kanallar, kurallar)
    return ad, str(veri.get("aciklama", "")), zamanli, uyarilar + u, yonler


def jestleri_oku(kanallar, klasor=KLASOR, kurallar=None):
    """-> ([(ad, aciklama, kareler, yonler), ...], bosta_son, uyarilar)"""
    if kurallar is None:
        kurallar = bagimli_kurallari(eklem_oku(), kanallar)
    jestler, uyarilar = [], []
    for yol in sorted(klasor.glob("*.yaml")):
        if yol.name == KANAL_DOSYASI.name:
            continue
        ad, aciklama, kareler, u, yonler = jest_oku(yol, kanallar, kurallar)
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
    s.append("// Kaynak: kod/jestler/kanallar.yaml ve kod/jestler/*.yaml; aci sinirlari")
    s.append("//         kod/ortak/eklem_sinirlari.json (robot acisi = eklem acisi + eklem_ofset)")
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
                 f"{'true' if k['ters'] else 'false'}}},  // {k['model']}, eklem {k['eklem']} "
                 f"{_sade(k['eklem_ofset']):+}, ayna: {k['ayna']} ({k['ayna_aci']})")
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


def ivme_sinirlari(sinirlar):
    """JSON teker.ivme_sinir_m_s2 -> {duz_surus, duz_fren, rampa_surus, rampa_fren} (m/s^2), denetlenmiş."""
    ham = (sinirlar.get("teker") or {}).get("ivme_sinir_m_s2")
    if not isinstance(ham, dict):
        raise JestHatasi("eklem_sinirlari.json: teker.ivme_sinir_m_s2 bölümü yok")
    sonuc = {}
    for a in IVME_ANAHTARLARI:
        deger = ham.get(a)
        if not _sayi_mi(deger) or not 0 < deger <= 5:
            raise JestHatasi(f"eklem_sinirlari.json: teker.ivme_sinir_m_s2.{a} 0-5 m/s^2 arası "
                             f"pozitif sayı olmalı ({deger!r})")
        sonuc[a] = deger
    return sonuc


def sinir_baslik_uret(ivme):
    """sinirlar_verisi.h metni (motorlar.cpp include eder)."""
    aciklama = {"duz_surus": "duz zeminde hizlanma", "duz_fren": "duz zeminde yavaslama / fren (dur, bekci)",
                "rampa_surus": "rampa kipinde hizlanma", "rampa_fren": "rampa kipinde yavaslama / fren"}
    s = ["// OTOMATIK URETILDI: kod/jestler/jest_uret.py -- ELLE DUZENLEME.",
         "// Kaynak: kod/ortak/eklem_sinirlari.json teker.ivme_sinir_m_s2 (Ahmet'in CAD betiginden; karar 29 Ekim 2026)",
         "// Degistirmek icin JSON'u tazele (git show origin/lale-duzeltme:kod/ortak/eklem_sinirlari.json),",
         "// sonra: py -3 kod/jestler/jest_uret.py",
         "// Bu dosya yalniz motorlar.cpp tarafindan include edilir. Birim: m/s^2 (teker cizgisel ivmesi).",
         "#pragma once",
         ""]
    for a in IVME_ANAHTARLARI:
        s.append(f"static constexpr float IVME_{a.upper()} = {float(ivme[a])!r}f;   // {aciklama[a]}")
    return "\n".join(s) + "\n"


def sinir_uret(sinirlar=None):
    return sinir_baslik_uret(ivme_sinirlari(eklem_oku() if sinirlar is None else sinirlar))


def uret():
    pwm, kanallar = kanallari_oku()
    jestler, bosta, uyarilar = jestleri_oku(kanallar)
    return baslik_uret(pwm, kanallar, jestler, bosta), jestler, uyarilar


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kontrol", action="store_true", help="yazma; başlıklar güncel değilse 1 ile çık")
    args = ap.parse_args(argv)
    try:
        metin, jestler, uyarilar = uret()
        sinir_metin = sinir_uret()
    except JestHatasi as h:
        print(f"HATA: {h}", file=sys.stderr)
        return 2
    for u in uyarilar:
        print(f"UYARI: {u}")
    ciktilar = [(CIKTI, metin), (SINIR_CIKTI, sinir_metin)]
    if args.kontrol:
        eski = [yol for yol, m in ciktilar if (yol.read_text(encoding="utf-8") if yol.exists() else "") != m]
        for yol in eski:
            print(f"{yol} güncel değil; py -3 kod/jestler/jest_uret.py çalıştır.")
        if eski:
            return 1
        print("jest_verisi.h ve sinirlar_verisi.h güncel.")
        return 0
    for yol, m in ciktilar:
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(m, encoding="utf-8", newline="\n")
    print(f"{SINIR_CIKTI} yazıldı: ivme sınırları {ivme_sinirlari(eklem_oku())}")
    print(f"{CIKTI} yazıldı: {len(jestler)} jest ({', '.join(j[0] for j in jestler)})")
    yonlu = [f"{j[0]}({','.join(j[3])})" for j in jestler if j[3]]
    if yonlu:
        print(f"Yön varyantları: {' '.join(yonlu)}; ek kare dizileri ~{yon_bellek_bayt(jestler)} bayt flash")
    return 0


if __name__ == "__main__":
    sys.exit(main())
