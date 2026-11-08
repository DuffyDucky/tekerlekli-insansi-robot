# -*- coding: utf-8 -*-
"""Lale 1,58 m: korunan değerlerin regresyon kontrolü (planlama/dongu-158.md bölüm 1).

Yalnız standart kütüphane. Kullanım (depo kökünden ya da herhangi bir yerden):

    py -3 planlama/d158/regresyon.py            # ölç, tabanla karşılaştır, sonucu yaz
    py -3 planlama/d158/regresyon.py --yazma    # ölç ve karşılaştır, hiçbir dosyaya yazma

Dosyalar:
    regresyon.json           kabul edilmiş TABAN. Yalnız çıkış 0 olan koşu günceller; kötüleşen ya da okunamayan
                             koşu tabanı değiştirmez (ikinci koşu kötüleşmeyi "aynı" diye yutmasın).
    regresyon-son-kosu.json  her koşunun sonucu (çıkış kodu ne olursa olsun) buraya yazılır.

Her değer bir JSON dosyasından ve anahtar yolundan okunur; çıktıda ikisi de yazılır.
Değer okunamazsa uydurulmaz: "kaynak yok" yazılır.
Yön: "buyuk_iyi" (azalırsa kötüleşme), "kucuk_iyi" (artarsa kötüleşme), "esit" (hedef ± toleransın dışı kötüleşme;
boy 1.580,0 ± 0,05 mm, iki yönlü).

Çıkış kodu:
    0  her değer okundu, eşikler sağlanıyor, tabana göre kötüleşen yok
    1  en az bir değer tabana göre kötüleşti ya da eşiği sağlamıyor
    2  kötüleşme yok ama en az bir değer okunamadı ("kaynak yok", doğrulanamadı)
"""
import datetime
import hashlib
import json
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.normpath(os.path.join(BURASI, "..", ".."))
CIKTI = os.path.join(BURASI, "regresyon.json")              # kabul edilmiş taban
SON_KOSU = os.path.join(BURASI, "regresyon-son-kosu.json")   # her koşunun sonucu
TOL = 1e-6  # JSON'daki yuvarlanmış değerler için karşılaştırma toleransı


class KaynakYok(Exception):
    pass


def _oku(yol):
    tam = os.path.join(KOK, *yol.split("/"))
    if not os.path.isfile(tam):
        raise KaynakYok("dosya yok: " + yol)
    try:
        with open(tam, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise KaynakYok("okunamadı: %s (%s)" % (yol, e))


def _yol(veri, anahtarlar):
    d = veri
    for a in anahtarlar:
        if isinstance(d, dict) and a in d:
            d = d[a]
        else:
            raise KaynakYok("anahtar yok: " + ".".join(anahtarlar))
    return d


def _sayi(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise KaynakYok("sayı değil: %r" % (x,))
    return float(x)


# --- değer okuyucular: (değer, açıklama) döndürür -------------------------------------------------

def boy(v):
    return _sayi(_yol(v, ["toplam_boy_mm"])), None


def liste_uzunlugu(anahtarlar):
    def f(v):
        x = _yol(v, anahtarlar)
        if not isinstance(x, list):
            raise KaynakYok("liste değil: " + ".".join(anahtarlar))
        return float(len(x)), "liste uzunluğu (çakışan çift sayısı)"
    return f


def rampa_yuksuz(v):
    d = _yol(v, ["izgara_yuk_0g", "a_sinir_pay15"])
    rampa = {k: _sayi(x) for k, x in d.items() if k.startswith("rampa5_")}
    if not rampa:
        raise KaynakYok("rampa5_* anahtarı yok: izgara_yuk_0g.a_sinir_pay15")
    k = min(rampa, key=rampa.get)
    return rampa[k], "rampa5_* en küçüğü: %s" % k


def sayi(anahtarlar):
    def f(v):
        return _sayi(_yol(v, anahtarlar)), None
    return f


def sy8205_usb(v):
    toplam, n = 0.0, 0
    for grup in ("kablo_sy8205", "kafa_ici_qled_kablo"):
        d = _yol(v, [grup])
        if not isinstance(d, dict) or not d:
            raise KaynakYok("boş ya da sözlük değil: " + grup)
        for ad, satir in d.items():
            toplam += _sayi(_yol(satir, ["sy8205_kesisim_mm3"]))
            n += 1
    return toplam, "%d kablonun sy8205_kesisim_mm3 toplamı" % n


# --- korunan değerler (dongu-158.md:23-25, §1 "Korunan değerler") --------------------------------------------------------
# yon: "buyuk_iyi" (artarsa iyi), "kucuk_iyi" (azalırsa iyi) ya da "esit" (esik ± tol); esik: kabul sınırı (dongu-158.md:24-25, §1)
DEGERLER = [
    dict(ad="boy_mm", etiket="Toplam boy, mm", dosya="tasarim/freecad/lale158/lale158-kontrol.json",
         anahtar="toplam_boy_mm", oku=boy, yon="esit", esik=1580.0, tol=0.05),
    dict(ad="cakisma_kafa_ici", etiket="Çakışma, kafa içi", dosya="tasarim/freecad/kafa/kafa-analiz.json",
         anahtar="statik", oku=liste_uzunlugu(["statik"]), yon="kucuk_iyi", esik=0.0),
    dict(ad="cakisma_kabuk_ici", etiket="Çakışma, kabuk içi", dosya="tasarim/freecad/kabuk/kabuk-analiz.json",
         anahtar="cakisma", oku=liste_uzunlugu(["cakisma"]), yon="kucuk_iyi", esik=0.0),
    dict(ad="cakisma_kabuk_x_iskelet", etiket="Çakışma, kabuk × iskelet",
         dosya="tasarim/freecad/kabuk/kabuk-analiz.json", anahtar="iskelet_cakisma",
         oku=liste_uzunlugu(["iskelet_cakisma"]), yon="kucuk_iyi", esik=0.0),
    dict(ad="cakisma_ev_pozu", etiket="Çakışma, ev pozu (tam model)", dosya="tasarim/freecad/carpisma-sonuc.json",
         anahtar="ev_pozu_cakisma", oku=liste_uzunlugu(["ev_pozu_cakisma"]), yon="kucuk_iyi", esik=0.0),
    dict(ad="rampa_yuksuz", etiket="Devrilme payı, yüksüz, rampa 5° (ızgara en kötü)",
         dosya="tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json",
         anahtar="izgara_yuk_0g.a_sinir_pay15.rampa5_* (en küçük)", oku=rampa_yuksuz, yon="buyuk_iyi", esik=1.5),
    dict(ad="tilt_payi", etiket="Tilt servo payı, ±15", dosya="tasarim/freecad/kafa/kafa-analiz.json",
         anahtar="tork.tilt.pay_tilt15", oku=sayi(["tork", "tilt", "pay_tilt15"]), yon="buyuk_iyi", esik=3.0),
    dict(ad="pan_payi", etiket="Pan servo payı", dosya="tasarim/freecad/kafa/kafa-analiz.json",
         anahtar="tork.pan.pay_iki_hane", oku=sayi(["tork", "pan", "pay_iki_hane"]), yon="buyuk_iyi", esik=2.0),
    dict(ad="mik_hoparlor_mm", etiket="Mikrofon-hoparlör, tüm pozlarda en az, mm",
         dosya="tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json",
         anahtar="mic_hoparlor.poz_min_mm", oku=sayi(["mic_hoparlor", "poz_min_mm"]), yon="buyuk_iyi", esik=400.0),
    dict(ad="sy8205_x_usb_mm3", etiket="SY8205 × kafa kabloları (USB dahil, 13 kablo) kesişimi, mm³",
         dosya="tasarim/freecad/lale158/kafa-yerlesim/uygulama-olcum.json",
         anahtar="kablo_sy8205.*.sy8205_kesisim_mm3 + kafa_ici_qled_kablo.*.sy8205_kesisim_mm3",
         oku=sy8205_usb, yon="kucuk_iyi", esik=0.0),
]


def _ozet(dosya):
    tam = os.path.join(KOK, *dosya.split("/"))
    try:
        with open(tam, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        return None


def olc():
    sonuc, onbellek = {}, {}
    for d in DEGERLER:
        kayit = dict(etiket=d["etiket"], kaynak=dict(dosya=d["dosya"], anahtar=d["anahtar"]),
                     yon=d["yon"], esik=d["esik"])
        if "tol" in d:
            kayit["tol"] = d["tol"]
        try:
            if d["dosya"] not in onbellek:
                onbellek[d["dosya"]] = _oku(d["dosya"])
            deger, aciklama = d["oku"](onbellek[d["dosya"]])
            kayit["deger"] = round(deger, 6)
            kayit["kaynak"]["sha256_12"] = _ozet(d["dosya"])
            if aciklama:
                kayit["kaynak"]["not_"] = aciklama
            iyi = _esik_icinde(deger, kayit)
            kayit["esik_durumu"] = "sağlıyor" if iyi else "SAĞLAMIYOR"
        except KaynakYok as e:
            kayit["deger"] = None
            kayit["esik_durumu"] = "kaynak yok"
            kayit["kaynak"]["hata"] = str(e)
        sonuc[d["ad"]] = kayit
    return sonuc


def _esik_icinde(deger, k):
    if k["yon"] == "esit":
        return abs(deger - k["esik"]) <= k.get("tol", TOL) + TOL
    if k["yon"] == "buyuk_iyi":
        return deger >= k["esik"] - TOL
    return deger <= k["esik"] + TOL


def bilgi():
    """Karşılaştırılmayan, yalnız kayda yazılan bağlam (değerlerin hangi koşudan geldiği)."""
    dosya = "tasarim/freecad/carpisma-sonuc.json"
    try:
        v = _oku(dosya)
        b = dict(tek_kosu=v.get("tek_kosu"), birlestirme_notu=v.get("birlestirme_notu"),
                 kosular=sorted({str(x.get("kosu")) for x in (v.get("bolumler") or {}).values() if isinstance(x, dict)}))
    except KaynakYok as e:
        b = dict(hata=str(e))
    return {"carpisma_sonuc": dict(kaynak=dosya + " : tek_kosu, birlestirme_notu, bolumler.*.kosu", **b)}


def karsilastir(simdi, onceki):
    satirlar = []
    for ad, k in simdi.items():
        o = (onceki or {}).get(ad, {})
        od, sd = o.get("deger"), k.get("deger")
        if not onceki:
            durum = "ilk kayıt"
        elif sd is None:
            durum = "kaynak yok"
        elif k["yon"] == "esit":
            durum = "aynı" if (_esik_icinde(sd, k) and abs(sd - od) <= k.get("tol", TOL) + TOL) else "KÖTÜLEŞTİ"
        elif od is None:
            durum = "yeni (önceki kayıtta yok)"
        elif abs(sd - od) <= TOL:
            durum = "aynı"
        else:
            daha_iyi = (sd > od) if k["yon"] == "buyuk_iyi" else (sd < od)
            durum = "iyileşti" if daha_iyi else "KÖTÜLEŞTİ"
        satirlar.append(dict(ad=ad, onceki=od, simdi=sd, durum=durum))
    return satirlar


def _fmt(x):
    if x is None:
        return "kaynak yok"
    s = ("%.3f" % x).rstrip("0").rstrip(".")
    return s.replace(".", ",")


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows konsolunda Türkçe harfler bozulmasın
    except (AttributeError, ValueError):
        pass
    yazma_yok = "--yazma" in argv
    onceki_kayit = None
    if os.path.isfile(CIKTI):
        try:
            with open(CIKTI, encoding="utf-8") as f:
                onceki_kayit = json.load(f)
        except (OSError, ValueError) as e:
            print("Uyarı: taban regresyon.json okunamadı (%s); ilk kayıt gibi davranılıyor." % e)
    onceki = (onceki_kayit or {}).get("degerler")

    simdi = olc()
    kars = karsilastir(simdi, onceki)
    kotu = [s["ad"] for s in kars if s["durum"] == "KÖTÜLEŞTİ"]
    esik = [a for a, k in simdi.items() if k["esik_durumu"] == "SAĞLAMIYOR"]
    yok = [a for a, k in simdi.items() if k["deger"] is None]

    tarih = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    print("Lale 158 regresyon, %s%s" % (tarih, "" if onceki is None else
                                         "; taban " + str(onceki_kayit.get("tarih"))))
    print("%-26s %12s %12s %10s  %-12s %s" % ("değer", "taban", "şimdi", "eşik", "durum", "kaynak (dosya : anahtar)"))
    for s in kars:
        k = simdi[s["ad"]]
        durum = s["durum"] if k["esik_durumu"] != "SAĞLAMIYOR" else s["durum"] + ", EŞİK"
        onc = "-" if onceki is None or s["ad"] not in onceki else _fmt(s["onceki"])
        esik_yazi = _fmt(k["esik"]) + ("±" + _fmt(k["tol"]) if k["yon"] == "esit" else "")
        print("%-26s %12s %12s %10s  %-12s %s : %s" % (s["ad"], onc, _fmt(s["simdi"]), esik_yazi,
                                                     durum, k["kaynak"]["dosya"], k["kaynak"]["anahtar"]))
        if k["kaynak"].get("hata"):
            print("    kaynak yok: " + k["kaynak"]["hata"])

    if kotu:
        print("Kötüleşen: " + ", ".join(kotu))
    if esik:
        print("Eşiği sağlamayan: " + ", ".join(esik))
    if yok:
        print("Kaynak yok (doğrulanamadı): " + ", ".join(yok))
    kod = 1 if (kotu or esik) else (2 if yok else 0)
    print("Sonuç: " + {0: "GEÇER (hepsi okundu, kötüleşen yok)", 1: "GEÇMEZ", 2: "DOĞRULANAMADI"}[kod])

    if not yazma_yok:
        ek = bilgi()
        son = dict(
            aciklama="Son regresyon koşusu (taban değil). Üreten: planlama/d158/regresyon.py",
            tarih=tarih, cikis_kodu=kod, taban_tarih=(onceki_kayit or {}).get("tarih"),
            taban_guncellendi=(kod == 0), degerler=simdi, karsilastirma=kars,
            kotulesen=kotu, esik_disi=esik, kaynak_yok=yok, bilgi=ek,
        )
        _yaz(SON_KOSU, son)
        if kod == 0:
            gecmis = list((onceki_kayit or {}).get("gecmis", []))
            if onceki is not None:
                gecmis.append(dict(tarih=onceki_kayit.get("tarih"),
                                   degerler={a: k.get("deger") for a, k in onceki.items()}))
            taban = dict(
                aciklama="Kabul edilmiş taban: korunan değerler (planlama/dongu-158.md bölüm 1). Yalnız çıkış 0 olan "
                         "koşu günceller. Üreten: planlama/d158/regresyon.py",
                tarih=tarih, cikis_kodu=kod, degerler=simdi, karsilastirma=kars,
                onceki_tarih=(onceki_kayit or {}).get("tarih"), kotulesen=kotu, esik_disi=esik, kaynak_yok=yok,
                bilgi=ek, gecmis=gecmis,
            )
            _yaz(CIKTI, taban)
        else:
            print("Taban değişmedi (çıkış %d): %s" % (kod, os.path.relpath(CIKTI, KOK).replace(os.sep, "/")))
    return kod


def _yaz(yol, veri):
    with open(yol, "w", encoding="utf-8", newline="\n") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("Yazıldı: " + os.path.relpath(yol, KOK).replace(os.sep, "/"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
