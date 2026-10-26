# Ne yapıyor: "içerik paketi" YAML dosyasını okur (kurum, selamlama, konular, yerler, sık sorulanlar).
# Soruyu Türkçe küçük harfe çevirir, noktalamayı siler, kelimelere böler ve her kaydı puanlar.
# En iyi eşleşmeyi döner; puan eşiğin altındaysa None döner (dış kütüphane yok, yalnız kelime eşleme).

import re
from dataclasses import dataclass, field

import yaml

# Soru kelimeleri ve bağlaçlar her cümlede geçer; puanlamada sayılmaz.
DURAK_KELIMELER = {
    "ne", "neler", "nedir", "nerede", "nereye", "nasıl", "nasil", "kim", "kaç", "hangi",
    "mi", "mı", "mu", "mü", "bir", "ve", "ile", "de", "da", "bu", "şu", "o", "için",
    "var", "yok", "ben", "sen", "biz", "siz", "acaba", "lütfen", "bana", "bize",
}

# Türkçe ekler kelimenin sonuna gelir ("kantinde", "kantine"); ilk 5 harf kök sayılır.
KOK_UZUNLUGU = 5

ANAHTAR_PUANI = 3    # anahtar kelime geçerse
ORTUSME_PUANI = 1    # başlık/cevaptaki bir kelime kökü soruda da varsa


def turkce_kucuk(metin):
    """Türkçe küçük harf: İ -> i, I -> ı. Python'un lower() bunu yanlış yapar."""
    return metin.replace("İ", "i").replace("I", "ı").lower()


def kelimeler(metin):
    """Küçük harfe çevirir, noktalamayı boşluğa çevirir, kelime listesi döner."""
    temiz = re.sub(r"[^\w\s]", " ", turkce_kucuk(metin))
    return temiz.split()


def anlamli_kelimeler(metin):
    """Durak kelimeleri ve 2 harften kısa kelimeleri atar."""
    return [k for k in kelimeler(metin) if k not in DURAK_KELIMELER and len(k) > 2]


def kok(kelime):
    return kelime[:KOK_UZUNLUGU]


def ifade_geciyor_mu(ifade, soru_kelimeleri):
    """Tek kelime: sorudaki bir kelime onunla başlıyorsa (ek almış olabilir) evet.
    Birden çok kelime ("sağ ol"): ifade, sorunun içinde aynen geçiyorsa evet."""
    ifade_kelimeleri = kelimeler(ifade)
    if not ifade_kelimeleri:
        return False
    if len(ifade_kelimeleri) == 1:
        return any(k.startswith(ifade_kelimeleri[0]) for k in soru_kelimeleri)
    return " ".join(ifade_kelimeleri) in " ".join(soru_kelimeleri)


@dataclass
class Kayit:
    """Paketteki aranabilir bir bilgi (konu, yer ya da sık sorulan soru)."""
    baslik: str
    cevap: str
    anahtarlar: list = field(default_factory=list)
    jest: str | None = None


@dataclass
class Eslesme:
    kayit: Kayit
    puan: int


def puanla(kayit, soru_kelimeleri):
    puan = 0
    for anahtar in kayit.anahtarlar:
        if ifade_geciyor_mu(anahtar, soru_kelimeleri):
            puan += ANAHTAR_PUANI
    soru_kokleri = {kok(k) for k in soru_kelimeleri if k not in DURAK_KELIMELER and len(k) > 2}
    kayit_kokleri = {kok(k) for k in anlamli_kelimeler(kayit.baslik + " " + kayit.cevap)}
    puan += ORTUSME_PUANI * len(soru_kokleri & kayit_kokleri)
    return puan


class IcerikPaketi:
    def __init__(self, veri, esik=3):
        self.kurum = veri.get("kurum", "")
        self.rol = veri.get("rol", "tanıtım ve karşılama robotu")
        self.selamlama = veri.get("selamlama", "Merhaba, size nasıl yardımcı olabilirim?")
        self.esik = esik
        self.kayitlar = kayitlari_cikar(veri)

    @classmethod
    def dosyadan(cls, yol, esik=3):
        with open(yol, encoding="utf-8") as dosya:
            veri = yaml.safe_load(dosya) or {}
        return cls(veri, esik)

    def siralanmis(self, soru):
        """Tüm kayıtları puana göre büyükten küçüğe sıralar."""
        soru_kelimeleri = kelimeler(soru)
        eslesmeler = [Eslesme(k, puanla(k, soru_kelimeleri)) for k in self.kayitlar]
        return sorted(eslesmeler, key=lambda e: e.puan, reverse=True)

    def ara(self, soru):
        """En iyi eşleşme; puan eşiğin altındaysa None."""
        sirali = self.siralanmis(soru)
        if not sirali or sirali[0].puan < self.esik:
            return None
        return sirali[0]

    def en_iyiler(self, soru, adet=3):
        """Bulut dil modeline bağlam olarak verilecek en iyi birkaç kayıt (puanı 0 olanlar hariç)."""
        return [e for e in self.siralanmis(soru)[:adet] if e.puan > 0]

    def konu_basliklari(self):
        return [k.baslik for k in self.kayitlar]


def kayitlari_cikar(veri):
    """YAML'daki konular, yerler ve sss bölümlerini tek bir Kayit listesine çevirir."""
    kayitlar = []
    for konu in veri.get("konular") or []:
        kayitlar.append(Kayit(konu["baslik"], konu["cevap"],
                              konu.get("anahtarlar") or [], konu.get("jest")))
    for yer in veri.get("yerler") or []:
        anahtarlar = [yer["ad"]] + (yer.get("anahtarlar") or [])
        kayitlar.append(Kayit(yer["ad"], yer["tarif"], anahtarlar, yer.get("jest", "isaret")))
    for sss in veri.get("sss") or []:
        kayitlar.append(Kayit(sss["soru"], sss["cevap"], sss.get("anahtarlar") or [], sss.get("jest")))
    return kayitlar
