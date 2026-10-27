# Ne yapıyor: telefondan gelen kumandayı robotun bileşenlerine güvenle iletir (RobotKoprusu).
# Web sunucusu (sunucu.py) yalnız bu sınıfı çağırır; robotun içine doğrudan dokunmaz.
#   durum()          -> {durum, bolge, son_soru, son_cevap, bakim, seri_turu, calisma_suresi, ...}
#   sur(v, w)        -> hız seri.py'deki EN_FAZLA_V/W'ye kırpılır; sürülürken ESP32'ye 150 ms'de bir yinelenir
#   dur()            -> hemen {"k":"dur"}
#   jest(ad, yon)    -> selam, evet, isaret (+ sol/sag/ileri/arka)
#   soyle(metin)     -> robot BEKLE'deyse hemen söyler, değilse reddeder (cevapta nedeni yazar)
#   bolge_sec(ad)    -> kod/konum/bolge.txt (elle konum kaynağı okur); boş ad dosyayı siler
#   bakim(ac)        -> kod/bakim.txt oluşturur/siler (bakım modunu ana.py uygular)
# ÖLÜ ADAM: son "sur" isteğinden 400 ms geçerse köprü kendisi dur() der (telefon düşerse robot durur).
# ESP32 watchdog'u 500 ms'dir; Pi sürerken "sur"u 150 ms'de bir yineler, böylece robot takılmadan gider.

import math
import os
import threading
import time

from robot.durum import Durum
from robot.seri import EN_FAZLA_V, EN_FAZLA_W, sinirla

KOD_KLASORU = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BAKIM_DOSYASI = os.path.join(KOD_KLASORU, "bakim.txt")
JESTLER = ("selam", "evet", "isaret")
YONLER = ("sol", "sag", "ileri", "arka")
OLU_ADAM_SANIYE = 0.4          # son sur isteğinden bu kadar sonra robot durdurulur
YINELEME_SANIYE = 0.15         # sürülürken ESP32'ye sur bu aralıkla yinelenir (watchdog 500 ms)
EN_UZUN_METIN = 300            # söyletilecek metnin en fazla karakter sayısı
KONUSMA_SONRASI_SUSMA = 0.5    # söyletilen cümle bitince bu kadar süre tetik yok sayılır (yankı)


class KopruHatasi(Exception):
    """Telefona 'yapılamadı' diye dönecek hata; mesaj Türkçe ve kullanıcıya gösterilir."""

    def __init__(self, mesaj, kod=400):
        super().__init__(mesaj)
        self.kod = kod


class SusturulanTetik:
    """Robotun tetiğini sarar: uzaktan söyletilen cümle sürerken gelen tetikler yok sayılır.
    Yoksa robot kendi sesini duyup 'soru geldi' sanar ve kendi cümlesini dinlemeye başlar."""

    def __init__(self, ic, kopru):
        self.ic = ic
        self.kopru = kopru

    def bekle(self):
        while True:
            self.ic.bekle()
            if not self.kopru.konusma_suruyor():
                return
            print("[uzaktan] Söyletilen cümle sürerken gelen tetik yok sayıldı.")
            self.kopru.konusma_bitti.wait(10)

    def __getattr__(self, ad):         # mikrofon, kuyruk vb. alanlar asıl tetikten okunur
        return getattr(self.ic, ad)


class RobotKoprusu:
    def __init__(self, robot, bolge_dosyasi=None, bakim_dosyasi=BAKIM_DOSYASI, saat=time.monotonic,
                 olu_adam=OLU_ADAM_SANIYE, yineleme=YINELEME_SANIYE):
        self.robot = robot
        self.bolge_dosyasi = bolge_dosyasi or self._elle_dosyasi()
        self.bakim_dosyasi = bakim_dosyasi
        self.saat = saat                     # testte sahte saat verilir
        self.olu_adam = olu_adam
        self.yineleme = yineleme
        self.acilis = saat()
        self.kilit = threading.Lock()        # sürüş alanları ve seri yazımı için
        self.suruluyor = False
        self.hedef = (0.0, 0.0)
        self.son_istek = 0.0
        self.son_gonderim = 0.0
        self.konusma_kilidi = threading.Lock()
        self.konusma_bitti = threading.Event()
        self.konusma_bitti.set()
        self.son_konusma_bitisi = None
        self._durdur = threading.Event()
        self._is_parcacigi = None
        self._asil_tetik = None

    # ---------- yardımcılar ----------

    def _elle_dosyasi(self):
        """Elle konum kaynağının okuduğu dosya; konum kapalıysa varsayılan kod/konum/bolge.txt."""
        konum = getattr(self.robot, "konum", None)
        elle = getattr(konum, "kaynaklar", {}).get("elle") if konum is not None else None
        if elle is not None and getattr(elle, "dosya", None):
            return elle.dosya
        from robot.konum.elle import BOLGE_DOSYASI
        return BOLGE_DOSYASI

    def _bolgeler(self):
        konum = getattr(self.robot, "konum", None)
        if konum is not None and getattr(konum, "bolgeler", None) is not None:
            return konum.bolgeler
        from robot.konum.bolgeler import bolgeleri_oku
        return bolgeleri_oku()

    def son_tur(self):
        """(son soru, son cevap): önce robot.son_tur, yoksa dil modelinin sohbet geçmişi."""
        tur = getattr(self.robot, "son_tur", None)
        if tur:
            return tur
        gecmis = getattr(getattr(self.robot, "dil", None), "gecmis", None)
        turlar = getattr(gecmis, "turlar", None)
        if turlar:
            return turlar[-1]
        return (None, None)

    def konusma_suruyor(self):
        if not self.konusma_bitti.is_set():
            return True
        bitis = self.son_konusma_bitisi
        return bitis is not None and self.saat() - bitis < KONUSMA_SONRASI_SUSMA

    # ---------- okuma ----------

    def durum(self):
        konum = {}
        if getattr(self.robot, "konum", None) is not None:
            try:
                konum = self.robot.konum.durum()
            except Exception as hata:
                print(f"[uzaktan] Konum okunamadı ({hata}).")
        soru, cevap = self.son_tur()
        return {
            "durum": self.robot.durum.durum.value,
            "bolge": konum.get("bolge"),
            "bolge_adi": konum.get("bolge_adi"),
            "son_soru": soru,
            "son_cevap": cevap,
            "bakim": os.path.exists(self.bakim_dosyasi),
            "seri_turu": type(self.robot.seri).__name__,
            "calisma_suresi": int(self.saat() - self.acilis),
            "suruluyor": self.suruluyor,
            "konusuyor": not self.konusma_bitti.is_set(),
            "sinirlar": {"v": EN_FAZLA_V, "w": EN_FAZLA_W},
        }

    def bolge_listesi(self):
        b = self._bolgeler()
        return [{"kimlik": k, "ad": b.ad(k)} for k in b.adlar()]

    # ---------- sürüş ----------

    def sur(self, v, w):
        try:
            v, w = float(v), float(w)
        except (TypeError, ValueError):
            raise KopruHatasi("v ve w sayı olmalı.")
        if not (math.isfinite(v) and math.isfinite(w)):
            raise KopruHatasi("v ve w sonlu sayı olmalı.")
        v, w = round(sinirla(v, EN_FAZLA_V), 3), round(sinirla(w, EN_FAZLA_W), 3)
        with self.kilit:
            simdi = self.saat()
            self.hedef = (v, w)
            self.son_istek = simdi
            self.son_gonderim = simdi
            self.suruluyor = True
            self.robot.seri.sur(v, w)
        return v, w

    def dur(self):
        with self.kilit:
            self.suruluyor = False
            self.robot.seri.dur()

    def adim(self, simdi=None):
        """Arka plan döngüsünün bir adımı: ölü adam ve yineleme. Ne yaptığını döner (test için)."""
        with self.kilit:
            if not self.suruluyor:
                return None
            simdi = self.saat() if simdi is None else simdi
            if simdi - self.son_istek > self.olu_adam:
                self.suruluyor = False
                self.robot.seri.dur()
                print("[uzaktan] Telefondan komut gelmiyor; robot durduruldu (ölü adam).")
                return "dur"
            if simdi - self.son_gonderim >= self.yineleme:
                self.robot.seri.sur(*self.hedef)
                self.son_gonderim = simdi
                return "sur"
        return None

    # ---------- jest, söz, bölge, bakım ----------

    def jest(self, ad, yon=None):
        if ad not in JESTLER:
            raise KopruHatasi(f"Bilinmeyen jest: {ad!r} (olanlar: {', '.join(JESTLER)}).")
        if yon in ("", None):
            yon = None
        elif ad != "isaret" or yon not in YONLER:
            raise KopruHatasi(f"Yön yalnız işaret jestinde ve {', '.join(YONLER)} olabilir.")
        with self.kilit:
            self.robot.seri.jest(ad, yon)
        return {"ad": ad, "yon": yon}

    def soyle(self, metin):
        metin = " ".join(str(metin or "").split())
        if not metin:
            raise KopruHatasi("Söylenecek metin boş.")
        if len(metin) > EN_UZUN_METIN:
            raise KopruHatasi(f"Metin en fazla {EN_UZUN_METIN} karakter olabilir.")
        durum = self.robot.durum.durum
        if durum != Durum.BEKLE:
            raise KopruHatasi(f"Robot şu an {durum.value}; BEKLE'ye dönünce yeniden deneyin.", 409)
        if not self.konusma_kilidi.acquire(blocking=False):
            raise KopruHatasi("Robot zaten bir cümle söylüyor; bitince yeniden deneyin.", 409)
        self.konusma_bitti.clear()
        threading.Thread(target=self._konus, args=(metin,), daemon=True).start()
        return {"metin": metin, "durum": "söyleniyor"}

    def _konus(self, metin):
        try:
            yuz = getattr(self.robot, "yuz", None)
            if yuz is not None:
                yuz.metin_goster(metin)
            self.robot.tts.soyle(metin)
        except Exception as hata:
            print(f"[uzaktan] Söyletilemedi ({hata}).")
        finally:
            self.son_konusma_bitisi = self.saat()
            self.konusma_bitti.set()
            self.konusma_kilidi.release()

    def bolge_sec(self, ad):
        """ad doluysa bolge.txt'ye yazar; boş/None ise dosyayı siler (bölge yeniden otomatik bulunur)."""
        ad = (ad or "").strip()
        bilinen = [b["kimlik"] for b in self.bolge_listesi()]
        if ad and bilinen and ad not in bilinen:
            raise KopruHatasi(f"Bilinmeyen bölge: {ad!r}.")
        if ad and any(c in ad for c in "\r\n\t/\\"):
            raise KopruHatasi("Bölge adında geçersiz karakter var.")
        if ad:
            os.makedirs(os.path.dirname(self.bolge_dosyasi), exist_ok=True)
            with open(self.bolge_dosyasi, "w", encoding="utf-8") as f:
                f.write(ad + "\n")
        elif os.path.exists(self.bolge_dosyasi):
            os.remove(self.bolge_dosyasi)
        uyari = self._elle_kaynagi_tazele()
        return {"bolge": ad or None, "dosya": self.bolge_dosyasi, "uyari": uyari}

    def _elle_kaynagi_tazele(self):
        """Elle kaynak 5 s'de bir okur; beklemeden yeni bölgeyi birleştiriciye verir."""
        konum = getattr(self.robot, "konum", None)
        elle = getattr(konum, "kaynaklar", {}).get("elle") if konum is not None else None
        if elle is None:
            return "Elle konum kaynağı kapalı; bölge dosyası yazıldı ama robot şu an okumuyor."
        try:
            konum.tahmin_ekle(elle, elle.oku())
        except Exception as hata:
            print(f"[uzaktan] Bölge hemen uygulanamadı ({hata}); 5 s içinde okunur.")
        return None

    def bakim(self, ac):
        if ac:
            with open(self.bakim_dosyasi, "w", encoding="utf-8") as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S") + " telefondan açıldı\n")
        elif os.path.exists(self.bakim_dosyasi):
            os.remove(self.bakim_dosyasi)
        return {"bakim": os.path.exists(self.bakim_dosyasi)}

    # ---------- çalıştırma ----------

    def baslat(self):
        """Ölü adam/yineleme döngüsünü başlatır ve robotun tetiğini yankıya karşı sarar."""
        tetik = getattr(self.robot, "tetik", None)
        if tetik is not None and not isinstance(tetik, SusturulanTetik):
            self._asil_tetik = tetik
            self.robot.tetik = SusturulanTetik(tetik, self)
        self._durdur.clear()
        self._is_parcacigi = threading.Thread(target=self._dongu, name="uzaktan-surus", daemon=True)
        self._is_parcacigi.start()

    def _dongu(self):
        while not self._durdur.wait(0.05):
            try:
                self.adim()
            except Exception as hata:          # seri hatası döngüyü düşürmesin
                print(f"[uzaktan] Sürüş döngüsü hatası: {hata}")

    def kapat(self):
        self._durdur.set()
        if self._is_parcacigi is not None:
            self._is_parcacigi.join(1)
        if self.suruluyor:
            self.dur()
        if self._asil_tetik is not None and isinstance(self.robot.tetik, SusturulanTetik):
            self.robot.tetik = self._asil_tetik
        self._asil_tetik = None
