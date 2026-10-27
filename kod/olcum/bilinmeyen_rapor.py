# Ne yapıyor: robotun etkileşim günlüklerinden (gunlukler/*.csv) cevaplayamadığı ("bilmiyorum", konu boş) ve
# zayıf eşleşmeyle cevapladığı (puan < eşik) soruları toplar, benzerlerini gruplar (Türkçe küçük harf, durak
# kelimesiz, 5 harflik kökler) ve sıklığa göre Markdown rapor yazar. İçerik paketini büyütmenin yapılacak listesi.
#
# Örnek (depo kökünden):  py -3 kod/olcum/bilinmeyen_rapor.py --gun 7
#        (Pi, kod/'dan):  python3 olcum/bilinmeyen_rapor.py --gun 30 --esik 5
# Sonuç: kod/olcum/sonuclar/bilinmeyen-YYYY-MM-DD.md  (soru, kaç kez, örnek cümle, en yakın kayıt, içeriğe ekle)

import argparse
import csv
import glob
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, timedelta

OLCUM = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(OLCUM)
sys.path.insert(0, KOD)   # "robot" ve "ana" modülleri kod/ klasöründe

from ana import ayarlari_oku, konsolu_utf8_yap, paket_yolu, yol_coz  # noqa: E402
from robot.gunluk import AYIRAC, KODLAMA                              # noqa: E402
from robot.icerik import DURAK_KELIMELER, IcerikPaketi, kelimeler, kok  # noqa: E402

CEVAPSIZ_KONULAR = {"", "bilmiyorum"}   # günlükte robotun cevap bulamadığı turlar
VARSAYILAN_ESIK = 4     # puan bundan küçükse "zayıf eşleşme" (tek anahtar kelime = 3 puan, yani şans eseri olabilir)
GUNLUK_ADI = re.compile(r"^(\d{4}-\d{2}-\d{2})(_\d+)?\.csv$")   # 2026-10-27.csv ya da 2026-10-27_2.csv


# ---------- günlükleri okuma ----------

def gunluk_dosyalari(klasor, bugun, gun):
    """Son 'gun' güne (bugün dahil) ait günlük dosyaları, tarih sırasıyla."""
    ilk = bugun - timedelta(days=gun - 1)
    secilen = []
    for yol in sorted(glob.glob(os.path.join(klasor, "*.csv"))):
        eslesme = GUNLUK_ADI.match(os.path.basename(yol))
        if eslesme and ilk <= date.fromisoformat(eslesme.group(1)) <= bugun:
            secilen.append(yol)
    return secilen


def satirlari_oku(yollar):
    """Her dosyanın satırlarını sözlük olarak döner (gunluk.py biçimi: ';' ayraç, utf-8-sig)."""
    satirlar = []
    for yol in yollar:
        with open(yol, encoding=KODLAMA, newline="") as dosya:
            satirlar.extend(csv.DictReader(dosya, delimiter=AYIRAC))
    return satirlar


def puan_sayisi(deger):
    try:
        return int(deger)
    except (TypeError, ValueError):
        return None


def tur_bul(satir, esik=VARSAYILAN_ESIK):
    """'cevapsiz', 'dusuk' ya da None (iyi cevap, selam/teşekkür kalıbı, duyulamayan soru)."""
    soru = (satir.get("taninan") or "").strip()
    if not soru:
        return None                                 # duyulamayan soru: bu raporun konusu değil
    konu = (satir.get("konu") or "").strip()
    if konu.lower() in CEVAPSIZ_KONULAR:
        return "cevapsiz"
    if konu.startswith("kalıp:"):
        return None
    puan = puan_sayisi(satir.get("puan"))
    if puan is not None and puan < esik:
        return "dusuk"
    return None


# ---------- gruplama ----------

def normalize(metin):
    """'Kantin, nerede?' -> 'kantin nerede'"""
    return " ".join(kelimeler(metin or ""))


def grup_anahtari(soru):
    """Benzer soruları birleştiren anahtar: anlamlı kelimelerin kökleri (ilk 5 harf), sıralı.
    'Otopark nerede?' ve 'otoparkı nerede' -> aynı grup ('otopa'); 'otoparka nasıl giderim' ayrı ('gider otopa')."""
    kokler = sorted({kok(k) for k in kelimeler(soru) if k not in DURAK_KELIMELER and len(k) > 2})
    return " ".join(kokler) or normalize(soru)


@dataclass
class Grup:
    tur: str                                        # cevapsiz | dusuk
    anahtar: str
    ornek: str                                      # ilk görülen asıl cümle (STT'nin yazdığı gibi)
    sorular: Counter = field(default_factory=Counter)   # normalize soru -> kaç kez
    konular: Counter = field(default_factory=Counter)   # düşük puanlıda robotun verdiği konu -> kaç kez

    @property
    def adet(self):
        return sum(self.sorular.values())

    @property
    def soru(self):
        """Grubun en sık söylenen biçimi."""
        return self.sorular.most_common(1)[0][0]


def grupla(satirlar, esik=VARSAYILAN_ESIK):
    """Cevapsız ve düşük puanlı turları gruplar; en sık sorulan önce."""
    gruplar = {}
    for satir in satirlar:
        tur = tur_bul(satir, esik)
        if tur is None:
            continue
        soru = satir["taninan"].strip()
        anahtar = (tur, grup_anahtari(soru))
        if anahtar not in gruplar:
            gruplar[anahtar] = Grup(tur, anahtar[1], soru)
        grup = gruplar[anahtar]
        grup.sorular[normalize(soru)] += 1
        if satir.get("konu"):
            grup.konular[satir["konu"]] += 1
    return sorted(gruplar.values(), key=lambda g: (-g.adet, g.soru))


def en_yakin_kayit(paket, soru):
    """İçerik paketinde bu soruya en çok benzeyen kayıt (puanı eşiğin altında olsa da); hiç yoksa '-'."""
    if paket is None:
        return "-"
    sirali = paket.siralanmis(soru)
    if not sirali or sirali[0].puan <= 0:
        return "-"
    return f"{sirali[0].kayit.baslik} (puan {sirali[0].puan})"


# ---------- rapor ----------

def hucre(metin):
    """Markdown tablo hücresi: '|' ve satır sonu tabloyu bozmasın."""
    return str(metin).replace("|", "/").replace("\n", " ").strip()


def tablo(gruplar, paket, dusuk=False):
    if not gruplar:
        return ["Yok."]
    ucuncu = "Robotun verdiği konu" if dusuk else "En yakın mevcut kayıt"
    satirlar = [f"| # | Soru | Kaç kez | Örnek cümle | {ucuncu} | İçeriğe ekle |",
                "|---|---|---|---|---|---|"]
    for no, g in enumerate(gruplar, 1):
        kayit = ", ".join(k for k, _ in g.konular.most_common(2)) if dusuk else en_yakin_kayit(paket, g.ornek)
        satirlar.append(f"| {no} | {hucre(g.soru)} | {g.adet} | {hucre(g.ornek)} | {hucre(kayit)} |  |")
    return satirlar


def rapor_metni(gruplar, paket, bilgi, esik=VARSAYILAN_ESIK):
    cevapsiz = [g for g in gruplar if g.tur == "cevapsiz"]
    dusuk = [g for g in gruplar if g.tur == "dusuk"]
    satirlar = [f"# Bilinmeyen sorular: {bilgi['aralik']}", ""]
    for ad, deger in bilgi.items():
        if ad != "aralik":
            satirlar.append(f"- {ad}: {deger}")
    satirlar += ["", f"## Cevapsız sorular (robot \"bilmiyorum\" dedi): {sum(g.adet for g in cevapsiz)} tur", ""]
    satirlar += tablo(cevapsiz, paket)
    satirlar += ["", f"## Zayıf eşleşmeyle cevaplananlar (puan < {esik}): {sum(g.adet for g in dusuk)} tur", "",
                 "Robot cevap verdi ama eşleşme zayıftı; cevap yanlış konu olabilir. Günlükteki cevaba bakın.", ""]
    satirlar += tablo(dusuk, paket, dusuk=True)
    satirlar += ["", "## Nasıl kullanılır", "",
                 "\"İçeriğe ekle\" sütununa karar yazın: yeni kayıt / mevcut kayda anahtar kelime / gerek yok.",
                 "Sonra `icerik/*.yaml` dosyasını düzenleyin ve `py -3 kod/icerik_kontrol.py` çalıştırın.",
                 "Bilgi uydurmayın: bilinmeyen yer \"...\" kalır, doğru bilgiyi bölümden öğrenip yazın.", ""]
    return "\n".join(satirlar)


# ---------- komut satırı ----------

def secenekleri_oku(argv=None):
    p = argparse.ArgumentParser(description="Cevaplanamayan soruların raporu")
    p.add_argument("--gun", type=int, default=7, help="son kaç günün günlüğü (bugün dahil)")
    p.add_argument("--esik", type=int, default=VARSAYILAN_ESIK, help="puan bundan küçükse zayıf eşleşme sayılır")
    p.add_argument("--icerik", help="en yakın kayıt için içerik paketi (varsayılan: ayar dosyası)")
    p.add_argument("--bugun", help="raporun günü YYYY-MM-DD (varsayılan: bugün)")
    p.add_argument("--ayar", default=os.path.join(KOD, "ayarlar.yaml"))
    p.add_argument("--gunluk-klasoru", help="varsayılan: ayarlar.yaml gunluk.klasor")
    p.add_argument("--sonuc-klasoru", default=os.path.join(OLCUM, "sonuclar"))
    return p.parse_args(argv)


def main(argv=None):
    konsolu_utf8_yap()
    sec = secenekleri_oku(argv)
    ayar = ayarlari_oku(sec.ayar)
    bugun = date.fromisoformat(sec.bugun) if sec.bugun else date.today()
    klasor = sec.gunluk_klasoru or yol_coz((ayar.get("gunluk") or {}).get("klasor", "gunlukler"))
    yollar = gunluk_dosyalari(klasor, bugun, sec.gun)
    if not yollar:
        print(f"[rapor] {klasor} içinde son {sec.gun} güne ait günlük yok; rapor yazılmadı.")
        return 1
    paket_adi = sec.icerik or (ayar.get("icerik") or {}).get("paket", "universite")
    paket = IcerikPaketi.dosyadan(paket_yolu(paket_adi), (ayar.get("icerik") or {}).get("esik", 3))
    satirlar = satirlari_oku(yollar)
    gruplar = grupla(satirlar, sec.esik)
    duyulan = sum(1 for s in satirlar if (s.get("taninan") or "").strip())
    bilgi = {"aralik": f"{bugun - timedelta(days=sec.gun - 1)} - {bugun}",
             "Günlük dosyası": f"{len(yollar)} ({', '.join(os.path.basename(y) for y in yollar)})",
             "Soru duyulan tur": duyulan,
             "İçerik paketi": paket_adi}
    yol = os.path.join(sec.sonuc_klasoru, f"bilinmeyen-{bugun.isoformat()}.md")
    os.makedirs(sec.sonuc_klasoru, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as dosya:
        dosya.write(rapor_metni(gruplar, paket, bilgi, sec.esik))
    cevapsiz = sum(g.adet for g in gruplar if g.tur == "cevapsiz")
    print(f"[rapor] {duyulan} tur, {cevapsiz} cevapsız, {len(gruplar)} grup -> {yol}")
    for g in gruplar[:5]:
        print(f"  {g.adet:>3} x  {g.soru}  ({'cevapsız' if g.tur == 'cevapsiz' else 'zayıf'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
