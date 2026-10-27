# Ne yapıyor: konum test turu. bolgeler.yaml'daki bölgeleri sırayla sorar ("Robotu şu bölgeye götürün"), her
# noktada N tarama yapar; her kaynağın (wifi, gps, ble, aruco, gorsel) tek başına tahminini ve birleştiricinin
# (KonumYoneticisi) birleşik tahminini CSV'ye yazar, sonunda kaynak başına ve bölge başına doğruluk tablosu basar.
# TÜBİTAK 2209-B ölçütü: 10 bölgede doğru bölge oranı >= %90 (tablodaki "birlesik" satırı).
#
# Örnek (Pi, kod/'dan):  python3 olcum/konum_turu.py --etiket kampus-1 --adet 5
#        (Windows):      py -3 kod/olcum/konum_turu.py --etiket ev --kaynaklar wifi --adet 3
# Sonuç: kod/olcum/sonuclar/konum-turu-<etiket>.csv  (bölge, kaynak, tahmin, güven, doğru mu) ve aynı adla .md

import argparse
import csv
import os
import re
import sys
import time
from datetime import datetime

OLCUM = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(OLCUM)
sys.path.insert(0, KOD)   # "robot" ve "ana" modülleri kod/ klasöründe

from ana import ayarlari_oku, konsolu_utf8_yap        # noqa: E402
from robot.gunluk import AYIRAC, KODLAMA               # noqa: E402
from robot.konum.birlestirici import KonumYoneticisi, ayar_birlestir  # noqa: E402

ALANLAR = ["zaman", "bolge", "tarama", "kaynak", "tahmin", "guven", "dogru"]
BIRLESIK = "birlesik"
OLCULEN_KAYNAKLAR = ("wifi", "gps", "ble", "aruco", "gorsel")   # bölge söyleyen kaynaklar
SECILEBILIR = OLCULEN_KAYNAKLAR + ("elle",)        # elle yalnız istenirse (doğruyu zaten bilir)
HEDEF_ORAN = 0.90                                  # TÜBİTAK hedefi: doğru bölge oranı


# ---------- kurulum ----------

def varsayilan_kaynaklar(ayar):
    """Ayarda etkin olan ölçüm kaynakları (elle ve odometri hariç)."""
    birlesik = ayar_birlestir(ayar.get("konum") or {})
    return [ad for ad in OLCULEN_KAYNAKLAR if birlesik[ad]["etkin"]]


def yonetici_kur(ayar, kaynaklar):
    """Yalnız seçilen kaynaklarla KonumYoneticisi kurar (odometri ve seçilmeyenler kapalı)."""
    konum = dict(ayar.get("konum") or {})
    for ad in SECILEBILIR + ("odometri",):
        konum[ad] = {**(konum.get(ad) or {}), "etkin": ad in kaynaklar}
    return KonumYoneticisi.ayarlardan(konum, seri=None)


# ---------- ölçüm ----------

def satir_kur(bolge, tarama, kaynak, tahmin, guven):
    return {"zaman": datetime.now().isoformat(timespec="seconds"), "bolge": bolge, "tarama": tarama,
            "kaynak": kaynak, "tahmin": tahmin or "", "guven": round(guven or 0.0, 3),
            "dogru": int(tahmin == bolge)}


def tarama_yap(yonetici, bolge, tarama):
    """Her etkin kaynağı bir kez okur (kaynak satırları), sonra birleştiricinin sonucunu ekler."""
    satirlar = []
    for ad, kaynak in yonetici.kaynaklar.items():
        if not kaynak.etkin or kaynak is yonetici.odometri:
            continue
        tahmin = kaynak.oku()
        yonetici.tahmin_ekle(kaynak, tahmin)
        satirlar.append(satir_kur(bolge, tarama, ad, tahmin.bolge if tahmin else None,
                                  tahmin.guven if tahmin else 0.0))
    birlesik, guven, _ = yonetici.birlestir()
    satirlar.append(satir_kur(bolge, tarama, BIRLESIK, birlesik, guven))
    return satirlar


def tarama_ozeti(satirlar):
    """Ekrana bir satır: 'wifi=giris-holu+  ble=-  birlesik=giris-holu+'  (+ doğru, x yanlış)."""
    parcalar = []
    for s in satirlar:
        isaret = "+" if s["dogru"] else ("x" if s["tahmin"] else "")
        parcalar.append(f"{s['kaynak']}={s['tahmin'] or '-'}{isaret}")
    return "  ".join(parcalar)


def tur(yonetici, adet=5, aralik=2.0, sor=None, uyu=None, yazdir=print):
    """Bölgeleri sırayla sorar ve ölçer. Ctrl+C ya da girdi sonu turu bitirir; o ana kadarki satırlar döner.
    sor/uyu: testte sahte girdi ve beklemesiz uyku; verilmezse input() ve time.sleep()."""
    sor = sor or input
    uyu = uyu or time.sleep
    bolgeler = list(yonetici.bolgeler.bolgeler.values())
    satirlar = []
    try:
        for sira, bolge in enumerate(bolgeler, 1):
            cevap = sor(f"\n[{sira}/{len(bolgeler)}] Robotu şu bölgeye götürün: {bolge.ad or bolge.kimlik} "
                        f"({bolge.kimlik}). Hazır olunca Enter, atlamak için 'a': ")
            if cevap.strip().lower() in ("a", "atla"):
                continue
            yonetici.tahminleri_temizle()         # önceki noktanın tahmini bu noktaya karışmasın
            for tarama in range(1, adet + 1):
                yeni = tarama_yap(yonetici, bolge.kimlik, tarama)
                satirlar.extend(yeni)
                yazdir(f"  tarama {tarama}/{adet}: {tarama_ozeti(yeni)}")
                if tarama < adet:
                    uyu(aralik)
    except (EOFError, KeyboardInterrupt):
        yazdir("\n[tur] Erken bitirildi; o ana kadarki ölçümler kaydediliyor.")
    return satirlar


# ---------- özet ----------

def yuzde(pay, payda):
    return f"%{100 * pay / payda:.1f}".replace(".", ",") if payda else "-"


def kaynak_tablosu(satirlar):
    """Kaynak başına: ölçüm, doğru, doğruluk, tahmin yok, ortalama güven. Birleşik en altta."""
    adlar = [a for a in dict.fromkeys(s["kaynak"] for s in satirlar) if a != BIRLESIK] + [BIRLESIK]
    tablo = ["| Kaynak | Ölçüm | Doğru | Doğruluk | Tahmin yok | Ort. güven |", "|---|---|---|---|---|---|"]
    for ad in adlar:
        secili = [s for s in satirlar if s["kaynak"] == ad]
        if not secili:
            continue
        dogru = sum(s["dogru"] for s in secili)
        bos = sum(1 for s in secili if not s["tahmin"])
        guven = sum(s["guven"] for s in secili) / len(secili)
        ad_yazi = f"**{ad}**" if ad == BIRLESIK else ad
        guven_yazi = f"{guven:.2f}".replace(".", ",")
        tablo.append(f"| {ad_yazi} | {len(secili)} | {dogru} | {yuzde(dogru, len(secili))} | {bos} | {guven_yazi} |")
    return tablo


def bolge_tablosu(satirlar):
    """Birleşik tahminin bölge başına doğruluğu (hangi bölge zayıf?)."""
    birlesik = [s for s in satirlar if s["kaynak"] == BIRLESIK]
    tablo = ["| Bölge | Ölçüm | Doğru | Doğruluk | En sık yanlış tahmin |", "|---|---|---|---|---|"]
    for bolge in dict.fromkeys(s["bolge"] for s in birlesik):
        secili = [s for s in birlesik if s["bolge"] == bolge]
        dogru = sum(s["dogru"] for s in secili)
        yanlislar = [s["tahmin"] or "(yok)" for s in secili if not s["dogru"]]
        en_sik = max(set(yanlislar), key=yanlislar.count) if yanlislar else "-"
        tablo.append(f"| {bolge} | {len(secili)} | {dogru} | {yuzde(dogru, len(secili))} | {en_sik} |")
    return tablo


def hedef_satiri(satirlar):
    birlesik = [s for s in satirlar if s["kaynak"] == BIRLESIK]
    if not birlesik:
        return "Ölçüm yok."
    oran = sum(s["dogru"] for s in birlesik) / len(birlesik)
    bolge_sayisi = len({s["bolge"] for s in birlesik})
    sonuc = "SAĞLANDI" if oran >= HEDEF_ORAN else "sağlanmadı"
    ek = "" if bolge_sayisi >= 10 else f" (dikkat: {bolge_sayisi} bölge ölçüldü, hedef 10 bölge)"
    return f"Birleşik doğru bölge oranı {yuzde(oran, 1)}; hedef %{HEDEF_ORAN * 100:.0f}: {sonuc}{ek}."


def rapor_metni(satirlar, bilgi):
    satirlar_md = [f"# Konum test turu: {bilgi['Etiket']}", ""]
    satirlar_md += [f"- {ad}: {deger}" for ad, deger in bilgi.items()]
    satirlar_md += ["", "## Kaynak başına doğruluk", ""] + kaynak_tablosu(satirlar)
    satirlar_md += ["", "## Bölge başına (birleşik)", ""] + bolge_tablosu(satirlar)
    satirlar_md += ["", hedef_satiri(satirlar), ""]
    return "\n".join(satirlar_md)


# ---------- dosyalar ----------

def guvenli_etiket(etiket):
    return re.sub(r"[^\w-]+", "_", etiket).strip("_") or "etiketsiz"


def csv_yaz(yol, satirlar):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", encoding=KODLAMA, newline="") as dosya:
        yazici = csv.DictWriter(dosya, fieldnames=ALANLAR, delimiter=AYIRAC)
        yazici.writeheader()
        yazici.writerows(satirlar)


# ---------- komut satırı ----------

def secenekleri_oku(argv=None):
    p = argparse.ArgumentParser(description="Konum test turu (bölge doğruluğu)")
    p.add_argument("--etiket", default="etiketsiz", help='turun adı, ör. "kampus-1", "aksam"')
    p.add_argument("--adet", type=int, default=5, help="her noktada kaç tarama")
    p.add_argument("--kaynaklar", help="virgülle: wifi,gps,ble,aruco,gorsel (varsayılan: ayarda etkin olanlar)")
    p.add_argument("--aralik", type=float, default=2.0, help="taramalar arası bekleme (s)")
    p.add_argument("--ayar", default=os.path.join(KOD, "ayarlar.yaml"))
    p.add_argument("--sonuc-klasoru", default=os.path.join(OLCUM, "sonuclar"))
    return p.parse_args(argv)


def main(argv=None):
    konsolu_utf8_yap()
    sec = secenekleri_oku(argv)
    ayar = ayarlari_oku(sec.ayar)
    kaynaklar = [k.strip() for k in sec.kaynaklar.split(",") if k.strip()] if sec.kaynaklar \
        else varsayilan_kaynaklar(ayar)
    bilinmeyen = [k for k in kaynaklar if k not in SECILEBILIR]
    if bilinmeyen or not kaynaklar:
        print(f"[tur] Bilinmeyen ya da boş kaynak: {', '.join(bilinmeyen) or '-'} "
              f"(seçilebilir: {', '.join(SECILEBILIR)})")
        return 2
    yonetici = yonetici_kur(ayar, kaynaklar)
    yonetici.kaynaklari_baslat()
    print(f"[tur] {len(yonetici.bolgeler.bolgeler)} bölge | {yonetici.ozet()} | her noktada {sec.adet} tarama")
    if not yonetici.bolgeler.bolgeler:
        print("[tur] bolgeler.yaml'da bölge yok.")
        return 1
    satirlar = tur(yonetici, sec.adet, sec.aralik)
    yonetici.kapat()
    if not satirlar:
        print("[tur] Hiç ölçüm yapılmadı; dosya yazılmadı.")
        return 1
    ad = f"konum-turu-{guvenli_etiket(sec.etiket)}"
    csv_yol = os.path.join(sec.sonuc_klasoru, ad + ".csv")
    csv_yaz(csv_yol, satirlar)
    bilgi = {"Etiket": sec.etiket, "Tarih": f"{datetime.now():%Y-%m-%d %H:%M}",
             "Kaynaklar": ", ".join(kaynaklar), "Nokta başına tarama": sec.adet, "CSV": os.path.basename(csv_yol)}
    metin = rapor_metni(satirlar, bilgi)
    with open(os.path.join(sec.sonuc_klasoru, ad + ".md"), "w", encoding="utf-8") as dosya:
        dosya.write(metin)
    print("\n" + metin)
    print(f"[tur] Sonuç: {csv_yol} (+ .md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
