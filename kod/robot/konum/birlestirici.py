# Ne yapıyor: KonumYoneticisi. Ayarlardan konum kaynaklarını kurar, her kaynağı kendi iş parçacığında kendi
# aralığıyla okur (Wi-Fi 15 s, görsel 5 s, GPS/BLE 2 s, ArUco 1 s), ESP32'den gelen odometri satırlarını
# ayrı bir iş parçacığında işler ve hepsini tek bir "robot şu an nerede" cevabında birleştirir.
#
# BİRLEŞTİRME KURALI (ilk sürüm, bilerek basit):
#   puan = ağırlık x güven x tazelik      tazelik = 1 - yaş / tazelik_saniye  (0'ın altına inmez)
#   Aynı bölgeyi söyleyen kaynakların puanları toplanır, en yüksek puanlı bölge seçilir.
#   Güven = min(1, kazanan puan) x (kazanan puan / tüm puanlar): güçlü VE çelişkisiz ise yüksek.
#   Hiç taze tahmin yoksa SON BİLİNEN bölge korunur (sistem hiçbir koşulda durmaz); hiç yoksa None.
# Metrik konum (x, y, yön): odometri; ArUco işaretinde x/y varsa odometri ona çekilir, ArUco yoksa ve GPS
# bölge merkezi (bolgeler.yaml 'yerel') odometriden gps_duzeltme_m'den uzaksa GPS'e çekilir.
#
# SONRAKİ AŞAMA: Kalman filtresi (odometri tahmini + ArUco/GPS ölçümü, belirsizlik matrisiyle) ya da
# parçacık filtresi (Wi-Fi/BLE/görsel gibi bölge düzeyi ölçümleri olasılık olarak katmak için). Bu dosyadaki
# kural, o filtrelerin karşılaştırılacağı taban çizgisidir.

import os
import threading
import time

from robot.konum.bolgeler import KOD_KLASORU, Bolgeler, bolgeleri_oku

# ayarlar.yaml 'konum:' bölümü eksikse kullanılan değerler
VARSAYILAN = {
    "etkin": True,
    "aralik_saniye": 2.0,            # kendi 'aralik'ı olmayan kaynaklar için okuma aralığı
    "tazelik_saniye": 30.0,          # bu kadar eski tahminin puanı sıfıra iner
    "son_bilinen_bolge": None,       # açılışta bölge (ör. robotun durduğu yer); null = bilinmiyor
    "gps_duzeltme_m": 10.0,
    "bolgeler": "konum/bolgeler.yaml",
    "kamera": {"aygit": 0},
    "wifi": {"etkin": True, "agirlik": 1.0, "aralik": 15.0, "parmak_izi": "konum/parmak_izi.yaml",
             "azami_uzaklik": 250.0},
    "gps": {"etkin": True, "agirlik": 1.0, "port": "", "hiz": 9600},     # aralık: aralik_saniye
    "ble": {"etkin": True, "agirlik": 1.0},
    "aruco": {"etkin": False, "agirlik": 2.0, "aralik": 1.0, "iyi_kenar_px": 80.0},
    "gorsel": {"etkin": False, "agirlik": 1.0, "aralik": 5.0, "esik": 0.75},
    "odometri": {"etkin": True, "agirlik": 0.5, "tik_tur": 1980, "teker_cap_m": 0.125, "iz_genislik_m": 0.426,
                 "yaw_isareti": 1},
    "elle": {"etkin": True, "agirlik": 3.0, "bolge": None, "dosya": "konum/bolge.txt"},
}


def ayar_birlestir(ayar):
    """Kullanıcı ayarını varsayılanların üstüne yazar (alt bölümler de tek tek)."""
    sonuc = {}
    ayar = ayar or {}
    for anahtar, varsayilan in VARSAYILAN.items():
        deger = ayar.get(anahtar)
        if isinstance(varsayilan, dict):
            sonuc[anahtar] = {**varsayilan, **(deger or {})}
        else:
            sonuc[anahtar] = varsayilan if deger is None else deger
    return sonuc


def yol(goreli):
    if not goreli or os.path.isabs(goreli):
        return goreli
    return os.path.normpath(os.path.join(KOD_KLASORU, goreli))


def kaynaklari_kur(ayar, bolgeler, kamera=None):
    """Ayarda etkin olan kaynakları kurar (henüz başlatmaz). Kütüphane gerekenler içeride içe aktarılır."""
    from robot.konum.aruco import ArucoKaynagi
    from robot.konum.ble import BleKaynagi
    from robot.konum.elle import ElleKaynak
    from robot.konum.gorsel import GorselKaynak
    from robot.konum.gps import GpsKaynagi
    from robot.konum.odometri import Odometri
    from robot.konum.wifi import WifiKaynagi

    kaynaklar = []
    k = ayar["elle"]
    if k["etkin"]:
        kaynaklar.append(ElleKaynak(k["bolge"], yol(k["dosya"]), k["agirlik"], bilinen_bolgeler=bolgeler.adlar()))
    k = ayar["wifi"]
    if k["etkin"]:
        kaynaklar.append(WifiKaynagi(k["agirlik"], k["aralik"], yol(k["parmak_izi"]), k["azami_uzaklik"]))
    k = ayar["gps"]
    if k["etkin"]:
        kaynaklar.append(GpsKaynagi(bolgeler, k["port"], k["hiz"], k["agirlik"], k["aralik"]))
    k = ayar["ble"]
    if k["etkin"]:
        kaynaklar.append(BleKaynagi(bolgeler, k["agirlik"], k["aralik"]))
    kare_al = kamera.kare_al if kamera is not None else None
    k = ayar["aruco"]
    if k["etkin"]:
        kaynaklar.append(ArucoKaynagi(bolgeler, kare_al, k["agirlik"], k["aralik"], k["iyi_kenar_px"]))
    k = ayar["gorsel"]
    if k["etkin"]:
        kaynaklar.append(GorselKaynak(kare_al, k["agirlik"], k["aralik"], k["esik"]))
    k = ayar["odometri"]
    if k["etkin"]:
        kaynaklar.append(Odometri(k["tik_tur"], k["teker_cap_m"], k["iz_genislik_m"], k["agirlik"],
                                  yaw_isareti=k["yaw_isareti"]))
    return kaynaklar


class KonumYoneticisi:
    def __init__(self, kaynaklar, seri=None, tazelik_saniye=30.0, son_bilinen_bolge=None,
                 gps_duzeltme_m=10.0, bolgeler=None, kamera=None, saat=time.time):
        self.kaynaklar = {k.ad: k for k in kaynaklar}
        self.odometri = self.kaynaklar.get("odometri")
        self.seri = seri
        self.tazelik_saniye = float(tazelik_saniye)
        self.son_bilinen = son_bilinen_bolge
        self.gps_duzeltme_m = float(gps_duzeltme_m)
        self.bolgeler = bolgeler or Bolgeler()
        self.kamera = kamera
        self.saat = saat                          # testte sahte saat verilir
        self.kilit = threading.Lock()
        self.son_tahminler = {}                   # kaynak adı -> son KonumTahmini
        self.son_aruco_zamani = None
        self.durdur = threading.Event()
        self.is_parcaciklari = []
        self.basladi = False

    @classmethod
    def ayarlardan(cls, ayar, seri=None, elle_bolge=None):
        """ayarlar.yaml 'konum:' bölümünden kurar. elle_bolge: ana.py --konum seçeneği."""
        a = ayar_birlestir(ayar)
        if elle_bolge:
            a["elle"]["bolge"] = elle_bolge
        bolgeler = bolgeleri_oku(yol(a["bolgeler"]))
        kamera = None
        if a["aruco"]["etkin"] or a["gorsel"]["etkin"]:
            from robot.konum.kamera import Kamera
            kamera = Kamera(a["kamera"].get("aygit", 0))
        for k in ("wifi", "gps", "ble", "aruco", "gorsel"):
            a[k].setdefault("aralik", a["aralik_saniye"])
        return cls(kaynaklari_kur(a, bolgeler, kamera), seri, a["tazelik_saniye"], a["son_bilinen_bolge"],
                   a["gps_duzeltme_m"], bolgeler, kamera)

    # ---------- çalıştırma ----------

    def kaynaklari_baslat(self):
        if self.basladi:
            return
        for kaynak in self.kaynaklar.values():
            try:
                kaynak.baslat()
            except Exception as hata:
                kaynak.pasif_yap(f"başlatılamadı ({hata})")
        self.basladi = True

    def baslat(self):
        """Kaynakları açar ve arka plan iş parçacıklarını başlatır (daemon: robot kapanınca kendileri biter)."""
        self.kaynaklari_baslat()
        for kaynak in self.kaynaklar.values():
            if kaynak.etkin and kaynak.zaman_asimi_yok:
                self.tahmin_ekle(kaynak, kaynak.oku())   # elle bölge ilk sorudan önce hazır olsun
            if kaynak.etkin and kaynak is not self.odometri:
                self._is_baslat(self._kaynak_dongusu, kaynak)
        if self.odometri is not None and self.seri is not None and hasattr(self.seri, "satir_oku"):
            self._is_baslat(self._seri_dongusu)

    def _is_baslat(self, hedef, *argumanlar):
        t = threading.Thread(target=hedef, args=argumanlar, daemon=True)
        t.start()
        self.is_parcaciklari.append(t)

    def _kaynak_dongusu(self, kaynak):
        while not self.durdur.is_set() and kaynak.etkin:
            self.tahmin_ekle(kaynak, kaynak.oku())
            self.durdur.wait(kaynak.aralik)

    def _seri_dongusu(self):
        """ESP32 satırlarını okur; 'odo' satırları odometriye gider, diğerleri (ok, durum) yoksayılır.
        Seriye YAZMA ana.py'de (jest, dur); pyserial'de okuma ve yazma ayrı iş parçacıklarında güvenli."""
        while not self.durdur.is_set():
            try:
                mesaj = self.seri.satir_oku()
            except Exception as hata:
                print(f"[konum] seri okuma hatası ({hata}); 1 s sonra yeniden.")
                self.durdur.wait(1.0)
                continue
            if mesaj is None:
                self.durdur.wait(0.1)             # SahteSeri ya da sessiz hat: boşuna dönmesin
                continue
            self.odometri.isle(mesaj)

    def bir_kez(self):
        """Her etkin kaynağı sırayla bir kez okur (komut satırı aracı ve testler için; iş parçacığı yok)."""
        self.kaynaklari_baslat()
        for kaynak in self.kaynaklar.values():
            if kaynak.etkin and kaynak is not self.odometri:
                self.tahmin_ekle(kaynak, kaynak.oku())

    def tahmin_ekle(self, kaynak, tahmin):
        with self.kilit:
            if tahmin is None:
                if kaynak.zaman_asimi_yok:        # elle seçim kaldırıldı: eski söz geçersiz
                    self.son_tahminler.pop(kaynak.ad, None)
                return
            self.son_tahminler[kaynak.ad] = tahmin
        self._metrik_duzelt(tahmin)

    def _metrik_duzelt(self, tahmin):
        if self.odometri is None or tahmin.x is None or tahmin.y is None:
            return
        if tahmin.kaynak == "aruco":
            self.odometri.duzelt(tahmin.x, tahmin.y, tahmin.yon_derece)
            self.son_aruco_zamani = tahmin.zaman
            return
        if tahmin.kaynak == "gps":
            aruco_taze = (self.son_aruco_zamani is not None
                          and tahmin.zaman - self.son_aruco_zamani < self.tazelik_saniye)
            uzak = ((self.odometri.x - tahmin.x) ** 2 + (self.odometri.y - tahmin.y) ** 2) ** 0.5
            if not aruco_taze and uzak > self.gps_duzeltme_m:
                self.odometri.duzelt(tahmin.x, tahmin.y)

    def kapat(self):
        self.durdur.set()
        for kaynak in self.kaynaklar.values():
            try:
                kaynak.kapat()
            except Exception:
                pass
        if self.kamera is not None:
            self.kamera.kapat()

    def odometri_sifirla(self):
        """ESP32'ye {"k":"odo_sifirla"} gönderir ve yerel odometriyi sıfırlar."""
        if self.seri is not None:
            self.seri.gonder({"k": "odo_sifirla"})
        if self.odometri is not None:
            self.odometri.sifirla()

    # ---------- birleştirme ----------

    def tazelik(self, kaynak_adi, tahmin, simdi):
        kaynak = self.kaynaklar.get(kaynak_adi)
        if kaynak is not None and kaynak.zaman_asimi_yok:
            return 1.0
        yas = max(0.0, simdi - tahmin.zaman)
        return max(0.0, 1.0 - yas / self.tazelik_saniye)

    def birlestir(self, simdi=None):
        """(bölge, güven, [destekleyen kaynaklar]) ve son bilinen bölgeyi günceller."""
        simdi = self.saat() if simdi is None else simdi
        with self.kilit:
            tahminler = dict(self.son_tahminler)
        puanlar, destek = {}, {}
        for ad, t in tahminler.items():
            if t.bolge is None:
                continue                          # odometri gibi bölgesiz tahminler oy vermez
            kaynak = self.kaynaklar.get(ad)
            agirlik = kaynak.agirlik if kaynak is not None else 1.0
            puan = agirlik * t.guven * self.tazelik(ad, t, simdi)
            if puan <= 0:
                continue
            puanlar[t.bolge] = puanlar.get(t.bolge, 0.0) + puan
            destek.setdefault(t.bolge, []).append(ad)
        if not puanlar:
            return self.son_bilinen, 0.0, (["son-bilinen"] if self.son_bilinen else [])
        bolge = max(puanlar, key=puanlar.get)
        kazanan = puanlar[bolge]
        guven = min(1.0, kazanan) * kazanan / sum(puanlar.values())
        self.son_bilinen = bolge
        return bolge, round(guven, 3), sorted(destek[bolge])

    def metrik(self, simdi):
        """(x, y, yön): önce odometri, yoksa taze bir ArUco/GPS tahmininin x/y'si."""
        if self.odometri is not None:
            t = self.odometri.oku()
            if t is not None:
                return t.x, t.y, t.yon_derece
        with self.kilit:
            adaylar = [t for t in self.son_tahminler.values() if t.x is not None and t.y is not None]
        adaylar = [t for t in adaylar if simdi - t.zaman < self.tazelik_saniye]
        if not adaylar:
            return None, None, None
        t = max(adaylar, key=lambda a: a.zaman)
        return t.x, t.y, t.yon_derece

    def durum(self, simdi=None):
        """{bolge, bolge_adi, guven, kaynak, kaynaklar: {ad: {...}}, x, y, yon}"""
        simdi = self.saat() if simdi is None else simdi
        bolge, guven, destek = self.birlestir(simdi)
        x, y, yon = self.metrik(simdi)
        with self.kilit:
            tahminler = dict(self.son_tahminler)
        kaynaklar = {}
        for ad, kaynak in self.kaynaklar.items():
            t = tahminler.get(ad)
            if not kaynak.etkin:
                kaynaklar[ad] = {"pasif": kaynak.pasif_nedeni}
            elif t is not None:
                kaynaklar[ad] = {"bolge": t.bolge, "guven": round(t.guven, 3), "yas_s": round(simdi - t.zaman, 1)}
            else:
                kaynaklar[ad] = {"bolge": None}
        return {"bolge": bolge, "bolge_adi": self.bolgeler.ad(bolge) if bolge else None, "guven": guven,
                "kaynak": "+".join(destek), "kaynaklar": kaynaklar, "x": x, "y": y, "yon": yon}

    def ozet(self):
        """Açılışta yazılacak tek satır: hangi kaynaklar çalışıyor."""
        etkin = [ad for ad, k in self.kaynaklar.items() if k.etkin]
        pasif = [ad for ad, k in self.kaynaklar.items() if not k.etkin]
        return f"etkin: {', '.join(etkin) or '-'}" + (f" | pasif: {', '.join(pasif)}" if pasif else "")
