"""Lale Pi <-> ESP32 protokolünün Python okuyucusu.

Tek kaynak `kod/ortak/protokol.json`; bu modül yalnız onu okur, kendi başına ad ya da sayı tanımlamaz.
Sahte ESP32 (`kod/araclar/sahte_esp32/`) ve Pi istemcisi (`kod/pi/lale_pi/`) ikisi de bunu kullanır.
ESP32'nin C++ kodu ileride aynı JSON'dan başlık dosyası üretebilir (dilden bağımsız tek kaynak).

Yalnız standart kitaplık.
"""

import json
import math
import os

BURASI = os.path.dirname(os.path.abspath(__file__))
PROTOKOL_YOLU = os.path.join(BURASI, "protokol.json")
PARAMETRE_YOLU = os.path.join(BURASI, "robot_parametreleri.json")
EKLEM_YOLU = os.path.join(BURASI, "eklem_sinirlari.json")


def _oku(yol):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


PROTOKOL = _oku(PROTOKOL_YOLU)
PARAMETRELER = _oku(PARAMETRE_YOLU)
EKLEM = _oku(EKLEM_YOLU)

CERCEVE = PROTOKOL["cerceve"]
EN_COK_BAYT = CERCEVE["en_cok_bayt"]
ZAMAN = {ad: d["deger"] for ad, d in PROTOKOL["zamanlar_ms"].items()}
GUVENLIK = {ad: d.get("deger") for ad, d in PROTOKOL["guvenlik"].items()}
KOMUTLAR = PROTOKOL["komutlar"]
MESAJLAR = PROTOKOL["mesajlar"]
GUC_DURUMLARI = tuple(PROTOKOL["guc_durumlari"]["degerler"])
ARIZA_NEDENLERI = tuple(PROTOKOL["ariza_nedenleri"]["degerler"])
GENEL_HATALAR = tuple(PROTOKOL["genel_hatalar"]["degerler"])
JESTLER = tuple(PROTOKOL["jestler"]["degerler"])
YONLU_JESTLER = tuple(PROTOKOL["jestler"]["yonlu"])
JEST_YONLERI = tuple(PROTOKOL["jestler"]["yonler"])
TASLAK_YETENEKLER = tuple(ad for ad, d in PROTOKOL["yetenekler"].items() if d.get("taslak"))


def parametre(ad):
    """robot_parametreleri.json'daki bir parametrenin değeri (sonarlar için sözlüğün tamamı)."""
    p = PARAMETRELER["parametreler"][ad]
    return p["deger"] if "deger" in p else p


def ivme_sinirlari():
    """eklem_sinirlari.json teker.ivme_sinir_m_s2 (karar 29.10)."""
    return dict(EKLEM["teker"]["ivme_sinir_m_s2"])


def servo_tablosu():
    """Servo listesi; min / maks servo çerçevesinde = eklem sınırı + ofset, [0, 180]'e kırpılmış.

    Sınırlar `eklem_sinirlari.json`'dan hesaplanır, elle yazılmaz (yazilim-plani.md: "Sınırlar elle iki yerde yazılmaz").
    """
    tablo = []
    for s in PROTOKOL["servolar"]["liste"]:
        e = EKLEM["eklemler"][s["eklem"]]
        en_az = max(0.0, e["min"] + s["ofset"])
        en_cok = min(180.0, e["max"] + s["ofset"])
        tablo.append(dict(s, min=en_az, max=en_cok))
    return tablo


def bagimli_sinirlar():
    """eklem_sinirlari.json `bagimli` maddeleri servo çerçevesine çevrilmiş (TASLAK: firmware 0.5.0'da yok).

    Dönen her öğe: (koşul servo adı, koşul alt sınırı, sınırlanan servo adı, sınırlanan üst sınır).
    """
    eklemden = {s["eklem"]: s for s in PROTOKOL["servolar"]["liste"]}
    sonuc = []
    for b in EKLEM.get("bagimli", []):
        (kosul_eklem, (k_alt, _k_ust)), = b["kosul"].items()
        (sinir_eklem, (_s_alt, s_ust)), = b["sinir"].items()
        k = eklemden[kosul_eklem]
        s = eklemden[sinir_eklem]
        sonuc.append((k["ad"], k_alt + k["ofset"], s["ad"], s_ust + s["ofset"]))
    return sonuc


# ---------------------------------------------------------------- satır kodlama


def kodla(mesaj):
    """Sözlüğü boşluksuz tek satır JSON + "\\n" baytlarına çevirir (firmware serializeJson gibi)."""
    return (json.dumps(mesaj, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


class BozukSatir(ValueError):
    pass


def _sabit_reddet(ad):
    raise BozukSatir("JSON'da %s kabul edilmez" % ad)


def coz(satir):
    """Bir satırı (bayt ya da metin, satır sonu olmadan) sözlüğe çevirir; JSON değilse BozukSatir.

    NaN / Infinity reddedilir (JSON standardında yok). Üst düzey nesne değilse de sonuç döner (çağıran 'k'
    alanına bakar: firmware'de dizi gelirse d["k"] boştur -> k_yok).
    """
    if isinstance(satir, bytes):
        try:
            satir = satir.decode("utf-8")
        except UnicodeDecodeError as h:
            raise BozukSatir(str(h))
    try:
        return json.loads(satir, parse_constant=_sabit_reddet)
    except json.JSONDecodeError as h:
        raise BozukSatir(str(h))


# ---------------------------------------------------------------- tür denetimi


def _tur_adi(metin):
    """'bool (yalniz ...)' -> 'bool'; 'sayi|null' -> 'sayi|null'."""
    return metin.split(" ", 1)[0].strip()


def tur_uyar(deger, tur):
    """Tür adı (protokol.json sözlüğü): sayi, tamsayi, metin, bool, liste, nesne, birleşim 'a|b', null."""
    for t in tur.split("|"):
        if t == "null" and deger is None:
            return True
        if t == "bool" and isinstance(deger, bool):
            return True
        if t == "sayi" and isinstance(deger, (int, float)) and not isinstance(deger, bool) and math.isfinite(deger):
            return True
        if t == "tamsayi" and isinstance(deger, int) and not isinstance(deger, bool):
            return True
        if t == "metin" and isinstance(deger, str):
            return True
        if t == "liste" and isinstance(deger, list):
            return True
        if t == "nesne" and isinstance(deger, dict):
            return True
    return False


def komut_denetle(komut):
    """Pi'nin göndermek üzere olduğu komutu protokole göre denetler. Sorun listesi döner (boş = geçerli)."""
    sorun = []
    if not isinstance(komut, dict):
        return ["komut sözlük değil"]
    k = komut.get("k")
    if k not in KOMUTLAR:
        return ["bilinmeyen komut: %r" % (k,)]
    alanlar = KOMUTLAR[k]["alanlar"]
    for ad, tanim in alanlar.items():
        if ad not in komut:
            if tanim.get("zorunlu"):
                sorun.append("%s: zorunlu alan yok: %s" % (k, ad))
            continue
        if not tur_uyar(komut[ad], tanim["tur"]):
            sorun.append("%s.%s türü %s değil: %r" % (k, ad, tanim["tur"], komut[ad]))
    for ad in komut:
        if ad != "k" and ad not in alanlar:
            sorun.append("%s: tanımsız alan: %s" % (k, ad))
    return sorun


def mesaj_turu(mesaj):
    """ESP32'den gelen mesajın türü: 'cevap' ya da mesajlar bölümündeki ad ya da None (tanınmayan)."""
    if not isinstance(mesaj, dict):
        return None
    if "ok" in mesaj:
        return "cevap"
    k = mesaj.get("k")
    return k if k in MESAJLAR and k != "cevap" else None


def mesaj_denetle(mesaj):
    """ESP32'den gelen bir mesajı protokole göre denetler. Sorun listesi döner (boş = uygun).

    Cevaplarda komutun cevap_alanlari'na, olaylarda mesajlar bölümüne bakılır. Tanımsız alan sorun sayılır
    (sözleşme dışı alan = belge eksik demektir).
    """
    tur = mesaj_turu(mesaj)
    if tur is None:
        return ["tanınmayan mesaj: %r" % (mesaj,)]
    sorun = []
    if tur == "cevap":
        if not isinstance(mesaj["ok"], bool):
            sorun.append("ok bool değil")
        k = mesaj.get("k")
        if mesaj["ok"] is False:
            hata = mesaj.get("hata")
            if not isinstance(hata, str):
                sorun.append("ok=false ama hata metni yok")
            elif k is None:
                if hata not in GENEL_HATALAR:
                    sorun.append("k'siz cevapta genel olmayan hata: %s" % hata)
            elif hata not in KOMUTLAR.get(k, {}).get("hatalar", []) and hata not in GENEL_HATALAR:
                sorun.append("%s için belgelenmemiş hata: %s" % (k, hata))
            beklenen = {"ok", "k", "hata"}
        else:
            if k not in KOMUTLAR:
                return sorun + ["ok=true cevapta bilinmeyen k: %r" % (k,)]
            beklenen = {"ok", "k"} | set(KOMUTLAR[k]["cevap_alanlari"])
            for ad, tur_metin in KOMUTLAR[k]["cevap_alanlari"].items():
                if ad in mesaj and not tur_uyar(mesaj[ad], _tur_adi(tur_metin)):
                    sorun.append("%s cevabı %s türü %s değil: %r" % (k, ad, tur_metin, mesaj[ad]))
        for ad in mesaj:
            if ad not in beklenen:
                sorun.append("%s cevabında tanımsız alan: %s" % (k, ad))
        return sorun
    alanlar = MESAJLAR[tur]["alanlar"]
    for ad, tur_metin in alanlar.items():
        if ad in mesaj and not tur_uyar(mesaj[ad], _tur_adi(tur_metin)):
            sorun.append("%s.%s türü %s değil: %r" % (tur, ad, tur_metin, mesaj[ad]))
    for ad in mesaj:
        if ad not in alanlar:
            sorun.append("%s mesajında tanımsız alan: %s" % (tur, ad))
    if tur == "guc" and mesaj.get("guc") not in GUC_DURUMLARI:
        sorun.append("guc olayında bilinmeyen durum: %r" % mesaj.get("guc"))
    if tur == "guc" and mesaj.get("neden") is not None and mesaj.get("neden") not in ARIZA_NEDENLERI:
        sorun.append("guc olayında bilinmeyen neden: %r" % mesaj.get("neden"))
    return sorun
