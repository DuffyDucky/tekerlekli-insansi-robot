# Ne yapıyor: konum paketinin komut satırı aracı (kod/ klasöründen çalıştırın):
#   python3 -m robot.konum tara                     tüm kaynakların ham okumaları (--hepsi: kamera dahil)
#   python3 -m robot.konum kaydet <bolge> --adet 5  bu noktada Wi-Fi parmak izi topla
#   python3 -m robot.konum ogret <bolge> --adet 5   kameradan görsel örnek öğret
#   python3 -m robot.konum nerede                   birleştirici sonucu (bir kez)
#   python3 -m robot.konum izle                     sürekli konum (Ctrl+C ile çık)
#   python3 -m robot.konum bolgeler                 bolgeler.yaml listesi + kayıt sayıları
#   python3 -m robot.konum sifirla-odometri         ESP32'ye {"k":"odo_sifirla"}
#   python3 -m robot.konum isaret 7                 ArUco işareti PNG'si (basmak için)
# Windows'ta: py -3 -m robot.konum tara  (Wi-Fi netsh ile; robot servisi çalışıyorsa seri port meşgul olur).

import argparse
import os
import sys
import time

import yaml

from robot.konum.birlestirici import KonumYoneticisi, ayar_birlestir, yol
from robot.konum.bolgeler import KOD_KLASORU, KONUM_KLASORU, bolgeleri_oku

AYAR_DOSYASI = os.path.join(KOD_KLASORU, "ayarlar.yaml")


def ayarlari_oku(yol_):
    if not os.path.exists(yol_):
        return {}
    with open(yol_, encoding="utf-8") as dosya:
        return yaml.safe_load(dosya) or {}


def seri_ac(ayar):
    from robot.seri import seri_sec
    s = ayar.get("seri") or {}
    return seri_sec(s.get("port", ""), s.get("hiz", 115200))


def yonetici_kur(ayar, hepsi=False, seri=None):
    konum = dict(ayar.get("konum") or {})
    if hepsi:
        for ad in ("wifi", "gps", "ble", "aruco", "gorsel", "odometri", "elle"):
            konum[ad] = {**(konum.get(ad) or {}), "etkin": True}
    return KonumYoneticisi.ayarlardan(konum, seri)


def odometri_dinle(yonetici, sure=1.5):
    """Seri porttan 'sure' saniye satır okuyup odometriye verir (tek seferlik komutlar için)."""
    if yonetici.odometri is None or yonetici.seri is None:
        return
    bitis = time.monotonic() + sure
    while time.monotonic() < bitis:
        mesaj = yonetici.seri.satir_oku()
        if mesaj is None and type(yonetici.seri).__name__ == "SahteSeri":
            return
        if mesaj is not None:
            yonetici.odometri.isle(mesaj)


def durum_yaz(d):
    bolge = f"{d['bolge']} ({d['bolge_adi']})" if d["bolge"] else "bilinmiyor"
    print(f"Bölge: {bolge} | güven {d['guven']:.2f} | kaynak: {d['kaynak'] or '-'}")
    if d["x"] is not None:
        yon = f", yön {d['yon']:.0f}°" if d["yon"] is not None else ""
        print(f"Konum: x {d['x']:.2f} m, y {d['y']:.2f} m{yon}")
    for ad, bilgi in d["kaynaklar"].items():
        if "pasif" in bilgi:
            print(f"  {ad:9} pasif: {bilgi['pasif']}")
        elif bilgi.get("bolge"):
            print(f"  {ad:9} {bilgi['bolge']} (güven {bilgi['guven']:.2f}, {bilgi['yas_s']} s önce)")
        else:
            print(f"  {ad:9} -")


# ---------- komutlar ----------

def k_tara(ayar, sec):
    seri = seri_ac(ayar)
    yonetici = yonetici_kur(ayar, sec.hepsi, seri)
    yonetici.kaynaklari_baslat()
    odometri_dinle(yonetici)
    kapali = [ad for ad in ("wifi", "gps", "ble", "aruco", "gorsel", "odometri", "elle")
              if ad not in yonetici.kaynaklar]
    for ad, kaynak in yonetici.kaynaklar.items():
        print(f"== {ad} (ağırlık {kaynak.agirlik:g}, aralık {kaynak.aralik:g} s) ==")
        print("    " + kaynak.ham())
    if kapali:
        print(f"Ayarda kapalı: {', '.join(kapali)} (hepsini denemek için: tara --hepsi)")
    yonetici.kapat()
    seri.kapat()
    return 0


def k_kaydet(ayar, sec):
    from robot.konum.wifi import WifiKaynagi, eslestir
    a = ayar_birlestir(ayar.get("konum"))
    bolgeler = bolgeleri_oku(yol(a["bolgeler"]))
    if bolgeler.adlar() and sec.bolge not in bolgeler.adlar():
        print(f"UYARI: '{sec.bolge}' bolgeler.yaml'da yok (var olanlar: {', '.join(bolgeler.adlar())}). "
              "Yine de kaydediyorum; tarifler bu adla eşleşmez.")
    wifi = WifiKaynagi(veritabani_yolu=yol(a["wifi"]["parmak_izi"]))
    wifi.baslat()
    print(f"'{sec.bolge}' için {sec.adet} Wi-Fi taraması (aralarında {sec.bekle:g} s). Robotu kıpırdatmayın.")
    eklenen = wifi.kaydet(sec.bolge, sec.adet, sec.bekle)
    if not eklenen:
        print("Hiç BSSID görülmedi; kayıt yapılmadı. (Wi-Fi açık mı? Windows 11'de konum izni gerekebilir.)")
        return 1
    toplam = len(wifi.veritabani.get(sec.bolge, []))
    print(f"Kaydedildi: {eklenen} ölçüm ('{sec.bolge}' toplam {toplam}) -> {wifi.veritabani_yolu}")
    olcum = wifi.tara()
    if olcum:
        bolge, guven, _ = eslestir(olcum, wifi.veritabani)
        print(f"Şimdiki tarama eşleşmesi: {bolge} (güven {guven:.2f})")
    return 0


def k_ogret(ayar, sec):
    from robot.konum.gorsel import GorselKaynak
    from robot.konum.kamera import Kamera
    a = ayar_birlestir(ayar.get("konum"))
    kamera = Kamera(a["kamera"].get("aygit", 0))
    gorsel = GorselKaynak(kamera.kare_al, esik=a["gorsel"]["esik"])
    gorsel.baslat()
    try:
        for sira in range(1, sec.adet + 1):
            kare = kamera.kare_al()
            if kare is None:
                print(f"Kamera kare vermedi: {kamera.hata or 'bilinmeyen neden'}")
                return 1
            print(f"[{sira}/{sec.adet}] {gorsel.ogret(sec.bolge, kare)}")
            if sira < sec.adet:
                time.sleep(sec.bekle)
    finally:
        kamera.kapat()
    print(f"Yöntem: {gorsel.yontem}. Robotu biraz döndürüp/kaydırıp tekrar öğretmek tanımayı güçlendirir.")
    return 0


def k_nerede(ayar, sec):
    seri = seri_ac(ayar)
    yonetici = yonetici_kur(ayar, False, seri)
    yonetici.bir_kez()
    odometri_dinle(yonetici)
    durum_yaz(yonetici.durum())
    yonetici.kapat()
    seri.kapat()
    return 0


def k_izle(ayar, sec):
    seri = seri_ac(ayar)
    yonetici = yonetici_kur(ayar, False, seri)
    yonetici.baslat()
    print(f"[konum] {yonetici.ozet()}. Çıkmak için Ctrl+C.")
    aralik = ayar_birlestir(ayar.get("konum"))["aralik_saniye"]
    try:
        while True:
            time.sleep(aralik)
            d = yonetici.durum()
            xy = f" x {d['x']:.2f} y {d['y']:.2f} yön {d['yon']:.0f}" if d["x"] is not None and d["yon"] is not None else ""
            print(f"{time.strftime('%H:%M:%S')} {d['bolge'] or '-'} güven {d['guven']:.2f} [{d['kaynak'] or '-'}]{xy}")
    except KeyboardInterrupt:
        pass
    finally:
        yonetici.kapat()
        seri.kapat()
    return 0


def k_bolgeler(ayar, sec):
    from robot.konum.wifi import veritabani_oku
    a = ayar_birlestir(ayar.get("konum"))
    b = bolgeleri_oku(yol(a["bolgeler"]))
    try:
        izler = veritabani_oku(yol(a["wifi"]["parmak_izi"]))
    except Exception:
        izler = {}
    ornek_klasoru = os.path.join(KONUM_KLASORU, "gorsel_ornekler")
    if not b.bolgeler:
        print(f"Bölge yok: {yol(a['bolgeler'])}")
    for kimlik, bolge in b.bolgeler.items():
        gps = f"GPS {bolge.lat}, {bolge.lon} r={bolge.yaricap_m:g} m" if bolge.gps_var else "GPS yok"
        yerel = f"yerel ({bolge.x:g}, {bolge.y:g})" if bolge.x is not None and bolge.y is not None else "yerel yok"
        klasor = os.path.join(ornek_klasoru, kimlik)
        gorsel = len([f for f in os.listdir(klasor) if f.endswith(".npz")]) if os.path.isdir(klasor) else 0
        print(f"{kimlik:24} {bolge.ad:24} Wi-Fi {len(izler.get(kimlik, [])):3} ölçüm, görsel {gorsel:3} örnek, "
              f"{gps}, {yerel}")
    for kimlik in sorted(set(izler) - set(b.bolgeler)):
        print(f"{kimlik:24} (bolgeler.yaml'da yok) Wi-Fi {len(izler[kimlik])} ölçüm")
    print(f"ArUco işaretleri: {len(b.isaretler)} | BLE beaconları: {len(b.beaconlar)}")
    return 0


def k_sifirla(ayar, sec):
    seri = seri_ac(ayar)
    seri.gonder({"k": "odo_sifirla"})
    print(f"Gönderildi: {{\"k\":\"odo_sifirla\"}} ({type(seri).__name__})")
    seri.kapat()
    return 0


def k_isaret(ayar, sec):
    import cv2
    from robot.konum.aruco import isaret_resmi
    klasor = os.path.join(KONUM_KLASORU, "isaretler")
    os.makedirs(klasor, exist_ok=True)
    yol_ = os.path.join(klasor, f"isaret_{sec.kimlik}.png")
    cv2.imwrite(yol_, isaret_resmi(sec.kimlik, sec.kenar))
    print(f"{yol_} yazıldı. Basın (siyah kare kenarı ~15 cm), duvara robot kamerası yüksekliğinde asın,")
    print(f"bolgeler.yaml 'isaretler:' altına '{sec.kimlik}: <bolge>' ekleyin.")
    return 0


def secenekleri_oku(argv=None):
    p = argparse.ArgumentParser(prog="python3 -m robot.konum", description="Robot konum aracı")
    p.add_argument("--ayar", default=AYAR_DOSYASI, help="ayar dosyası (varsayılan kod/ayarlar.yaml)")
    alt = p.add_subparsers(dest="komut", required=True)
    t = alt.add_parser("tara", help="tüm kaynakların ham okumaları")
    t.add_argument("--hepsi", action="store_true", help="ayarda kapalı kaynakları da (kamera dahil) dene")
    for ad, yardim, bekle in (("kaydet", "Wi-Fi parmak izi topla", 3.0), ("ogret", "kameradan görsel örnek", 1.0)):
        k = alt.add_parser(ad, help=yardim)
        k.add_argument("bolge")
        k.add_argument("--adet", type=int, default=5)
        k.add_argument("--bekle", type=float, default=bekle, help="ölçümler arası saniye")
    alt.add_parser("nerede", help="birleştirici sonucu bir kez")
    alt.add_parser("izle", help="sürekli konum (Ctrl+C)")
    alt.add_parser("bolgeler", help="bolgeler.yaml listesi")
    alt.add_parser("sifirla-odometri", help="ESP32 odometri sayaçlarını sıfırla")
    i = alt.add_parser("isaret", help="ArUco işaret resmi üret")
    i.add_argument("kimlik", type=int)
    i.add_argument("--kenar", type=int, default=400, help="işaretin piksel kenarı")
    return p.parse_args(argv)


KOMUTLAR = {"tara": k_tara, "kaydet": k_kaydet, "ogret": k_ogret, "nerede": k_nerede, "izle": k_izle,
            "bolgeler": k_bolgeler, "sifirla-odometri": k_sifirla, "isaret": k_isaret}


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sec = secenekleri_oku(argv)
    return KOMUTLAR[sec.komut](ayarlari_oku(sec.ayar), sec)


if __name__ == "__main__":
    sys.exit(main())
