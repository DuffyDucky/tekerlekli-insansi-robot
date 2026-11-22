"""Sahte ESP32 çekirdeği: Lale tabanının saf, başsız, deterministik modeli.

NE BU: firmware 0.5.0 sözleşmesinin (`origin/main` `kod/esp32/src/`) ve planın güvenlik kurallarının
**çalıştırılabilir şartnamesi**. Gerçek ESP32'nin C++ kodunu SINAMAZ; aynı protokolü konuşan bir model.
Kural gerçek kodla uyuşmuyorsa önce `kod/ortak/protokol.json` ve plan belgesi düzeltilir, sonra iki taraf.

Zaman dışarıdan gelir: `adim(ms)` çekirdeği 10 ms'lik dilimlerle (100 Hz) ilerletir. Duvar saati, `sleep`,
iş parçacığı, rastgelelik yok: aynı girdi + aynı adımlar = aynı çıktı.

Giriş / çıkış (protokol): `bayt_al(veri)` gelen baytları kuyruğa koyar, `cikis_al()` giden satırları (metin, satır
sonu olmadan) boşaltır. Fiziksel dünya (protokol DEĞİL; test "ortam"ı ve hakem kullanır): `mantar`,
`ana_anahtar`, `i2c_saglam`, `konum_ayarla()`, `hakem()`.

Sözlük (firmware dosyaları): guc.cpp, watchdog.cpp, motorlar.cpp, seri_protokol.cpp, servolar.cpp. Hangi
kuralın nereden geldiği her bölümün başında.
"""

import math
import os
import sys

_KOD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ORTAK = os.path.join(_KOD, "ortak")
if _ORTAK not in sys.path:
    sys.path.insert(0, _ORTAK)

import lale_protokol as P  # noqa: E402

DILIM_MS = 10                       # 100 Hz döngü (yazilim-plani.md mimari "100 Hz döngü"; 0.5.0 motoru 50 Hz, Y0s-gunluk Ç7)
SURUM = P.PROTOKOL["surum"]         # "hazir" / "ping" cevabındaki sürüm


def _kirp(x, s):
    return s if x > s else (-s if x < -s else x)


class SahteEsp32:
    """Taban modeli. `harita` (harita.Harita) içinde, robot çerçevesi +x ileri, +y robotun kendi solu."""

    def __init__(self, harita, konum=None, sonar_acik=True, bagimli_sinir_acik=True):
        self.harita = harita
        self.sonar_acik = sonar_acik                 # TASLAK yetenek (0.5.0'da yok)
        self.bagimli_sinir_acik = bagimli_sinir_acik  # TASLAK yetenek (0.5.0'da yok)

        # --- sabitler: tek kaynaktan
        z = P.ZAMAN
        self.bekci_ms = z["bekci"]
        self.sessizlik_ms = z["sessizlik"]
        self.odo_aralik_ms = z["odo_aralik"]
        self.sonar_aralik_ms = z["sonar_aralik"]
        self.onsarj_bekleme_ms = z["onsarj_bekleme"]
        self.k1_sonrasi_ms = z["k1_sonrasi"]
        self.k2_en_cok_ms = z["k2_en_cok"]
        self.v_giris = P.PROTOKOL["sinirlar"]["v_giris"]["deger"]
        self.w_giris = P.PROTOKOL["sinirlar"]["w_giris"]["deger"]
        self.sonar_dur_cm = P.GUVENLIK["sonar_dur_cm"]
        self.sonar_yavas_cm = P.GUVENLIK["sonar_yavas_cm"]
        self.sonar_yavas_en_az = P.GUVENLIK["sonar_yavas_en_az_m_s"]
        self.sonar_histerezis_cm = P.GUVENLIK["sonar_histerezis_cm"]
        iv = P.ivme_sinirlari()
        self.ivme = {"duz": (iv["duz_surus"], iv["duz_fren"]), "rampa": (iv["rampa_surus"], iv["rampa_fren"])}
        self.teker_capi = P.parametre("teker_capi_m")
        self.iz = P.parametre("iz_genisligi_m")                  # fiziksel iz (CAD): robot gerçekte böyle döner
        self.fw_iz = P.parametre("firmware_iz_genisligi_m")      # firmware sabiti: sur (v, w) -> teker hızı (motorlar.cpp)
        self.tik_tur = P.parametre("enkoder_tik_tur")
        self.azami_hiz = P.parametre("teker_azami_hiz_m_s")
        self.taban_g = P.parametre("taban_genislik_m")
        self.taban_d = P.parametre("taban_derinlik_m")
        self.sonarlar = P.parametre("sonarlar")["liste"]
        self.sonar_menzil = P.parametre("sonar_menzil_m")
        self.sonar_yari_aci = P.parametre("sonar_yari_aci_rad")
        self.sonar_isin = P.parametre("sonar_isin_sayisi")
        self.sonar_gelis_siniri = P.parametre("sonar_yanki_gelis_siniri_rad")
        self.sonar_tur_ms = P.parametre("sonar_tur_ms")
        self.aku_v = P.parametre("aku_v")
        self.bara_dolma_ms = P.parametre("bara_dolma_ms")
        self.acilis_ms = P.parametre("acilis_ms")
        self.jest_suresi_ms = P.parametre("jest_suresi_ms")
        self.imu_var = P.parametre("imu_var")
        self.servo_tablo = P.servo_tablosu()
        self.servo_adlari = [s["ad"] for s in self.servo_tablo]
        self.bagimli = P.bagimli_sinirlar()

        # --- fiziksel dünya (protokol dışı)
        self.mantar = False          # True = acil stop mantarı basılı (GPIO23 HIGH)
        self.ana_anahtar = True      # False = akü bağlı değil: ön şarj barayı dolduramaz
        self.i2c_saglam = P.parametre("pca9685_var")
        x, y, a = konum if konum is not None else harita.baslangic
        self.x, self.y, self.aci = float(x), float(y), float(a)
        self.dunya_ms = 0            # açılıştan bağımsız toplam zaman (hakem)
        self.carpisma_sayisi = 0
        self.carpiyor = False
        self.yol_m = 0.0
        self.son_isinlar = {}        # sonar adı -> [(x1, y1, x2, y2, yanki_var)] (görünüm için)
        self._gelen = bytearray()
        self._giden = []
        self._acilis()

    # ================================================================ açılış (setup)

    def _acilis(self):
        """setup(): guc_pinleri_guvenle -> motorlar -> guc -> servolar -> seri ("hazir")."""
        self.ms = 0                              # millis()
        self.calisiyor = True
        self._acilis_bitis = None
        self.guc = "birakik"                     # açılışta ASLA kendiliğinden arm olmaz (guc.cpp guc_baslat)
        self.ariza = None
        self._olay_bekliyor = False
        self._olay_ms = 0
        self.k1 = False
        self.k2 = False
        self.en = False
        self._k2_bas_ms = None
        self._onsarj_adimi = 0
        self._adim_bas_ms = 0
        self._son_komut_ms = 0
        self._i2c_hata = 0
        self._son_i2c_ms = 0
        # motorlar
        self.v_hedef = 0.0
        self.w_hedef = 0.0
        self.hedef = [0.0, 0.0]                  # sol, sağ teker hedef hızı (m/s), komuttan
        self.rampa_hiz = [0.0, 0.0]              # ivme sınırlı hız (motora giden; motor ideal: gerçek hız)
        self._tik_kesir = [0.0, 0.0]
        self.tik = [0, 0]
        self.rampa_elle = False
        # bekçi (watchdog.cpp): açılışta tetikli
        self._son_sur_ms = 0
        self.bekci_tetikli = True
        # servolar
        self.pca_var = self.i2c_saglam
        ev = [float(s["ev"]) for s in self.servo_tablo]
        self.servo_hedef = list(ev)
        self.servo_simdi = list(ev)
        self.jest = None
        self._jest_bitis = 0
        # sonar (TASLAK)
        self.sonar = {ad: None for ad in self.sonarlar}
        self._sonar_sira = 0
        self._son_sonar_tetik = -self.sonar_tur_ms
        self.engel = False
        self._son_odo_ms = 0
        self._son_sonar_ms = 0
        self._gelen.clear()
        hazir = {"k": "hazir", "surum": SURUM, "pca9685": self.pca_var, "guc": self.guc}
        if self.yetenekler():
            hazir["yetenekler"] = self.yetenekler()
        self._yaz(hazir)

    def yetenekler(self):
        y = []
        if self.sonar_acik:
            y.append("sonar")
        if self.bagimli_sinir_acik:
            y.append("bagimli_sinir")
        return y

    # ================================================================ dış arayüz

    def bayt_al(self, veri):
        """Seri hattan gelen baytlar (parça parça gelebilir)."""
        if self.calisiyor:
            self._gelen += veri

    def cikis_al(self):
        """Giden satırları (satır sonsuz metin) boşaltır."""
        c, self._giden = self._giden, []
        return c

    def adim(self, ms):
        """Sanal zamanı `ms` kadar ilerletir (10 ms dilimler; ms 10'un katı olmalı)."""
        if ms % DILIM_MS:
            raise ValueError("adim ms %d'nin katı olmalı" % DILIM_MS)
        for _ in range(ms // DILIM_MS):
            self._dilim()

    def konum_ayarla(self, x, y, aci_rad):
        """Robotu haritada bir yere koy (fiziksel; hakem / test kurulumu)."""
        self.x, self.y, self.aci = float(x), float(y), float(aci_rad)
        self.carpiyor = self._carpar(self.x, self.y, self.aci)

    def hakem(self):
        """Gerçek dünya durumu (protokol DEĞİL; yalnız hakem ve görünüm okur)."""
        v_sol, v_sag = self.rampa_hiz
        return {
            "x": self.x, "y": self.y, "aci": self.aci,
            "v": (v_sol + v_sag) / 2.0, "w": (v_sag - v_sol) / self.iz,
            "teker": [v_sol, v_sag], "carpisma_sayisi": self.carpisma_sayisi, "carpiyor": self.carpiyor,
            "guc": self.guc, "ariza": self.ariza, "en": self.en, "k1": self.k1, "k2": self.k2,
            "bara": self._bara_gerilimli(), "mantar": self.mantar, "bekci_tetikli": self.bekci_tetikli,
            "engel": self.engel, "sonar": dict(self.sonar), "servo": dict(zip(self.servo_adlari, self.servo_simdi)),
            "kollar_guclu": self._bara_gerilimli(), "calisiyor": self.calisiyor,
            "dunya_ms": self.dunya_ms, "ms": self.ms, "yol_m": self.yol_m,
            "on_engel_m": self.on_engel_uzakligi(),
        }

    def on_engel_uzakligi(self):
        """Hakem: orta sonarın ön yüzünden dümdüz ileri en yakın yüzeye uzaklık (m) ya da None."""
        s = self.sonarlar["orta"]
        sx, sy = self._yerel_dunya(s["x_m"], s["y_m"])
        r = self.harita.isin(sx, sy, self.aci + s["aci_rad"], 1000.0)
        return None if r is None else r[0]

    # ================================================================ döngü (loop)

    def _dilim(self):
        self.dunya_ms += DILIM_MS
        if not self.calisiyor:
            # reset sonrası açılış: motorlar ve röleler kapalı, robot fiziksel olarak durur
            self.rampa_hiz = [0.0, 0.0]
            if self.dunya_ms >= self._acilis_bitis:
                self._acilis()
            return
        self.ms += DILIM_MS
        simdi = self.ms
        self._guc_guncelle(simdi)       # main.cpp loop sırası: önce güç
        self._seri_isle(simdi)
        if not self.calisiyor:          # reset komutu geldi
            return
        self._bekci_kontrol(simdi)
        self._sonar_guncelle(simdi)
        self._motor_guncelle()
        self._servo_guncelle(simdi)
        if simdi - self._son_odo_ms >= self.odo_aralik_ms:
            self._son_odo_ms = simdi
            self._yaz({"k": "odo", "sol": self.tik[0], "sag": self.tik[1],
                       "yaw": round(math.degrees(self.aci), 2) if self.imu_var else None, "ms": simdi})
        if self.sonar_acik and simdi - self._son_sonar_ms >= self.sonar_aralik_ms:
            self._son_sonar_ms = simdi
            m = {"k": "sonar"}
            m.update(self.sonar)
            m["ms"] = simdi
            self._yaz(m)

    def _yaz(self, mesaj):
        self._giden.append(P.kodla(mesaj).decode("utf-8")[:-1])

    # ================================================================ güç (guc.cpp; pin-haritasi.md Y4 / Y5; elektrik.md E3 / E9)

    def _role_cekili(self, pin):
        return pin and not self.mantar              # mantar bobin beslemesini keser (donanım)

    def _bara_gerilimli(self):
        if not self.ana_anahtar:
            return False
        if self._role_cekili(self.k1):
            return True
        return bool(self._role_cekili(self.k2) and self._k2_bas_ms is not None
                    and self.ms - self._k2_bas_ms >= self.bara_dolma_ms)

    def _olay(self, simdi):
        self._olay_bekliyor = True
        self._olay_ms = simdi

    def _olay_gonder(self):
        if not self._olay_bekliyor:
            return
        self._olay_bekliyor = False
        self._yaz({"k": "guc", "guc": self.guc, "neden": self.ariza, "ms": self._olay_ms})

    def _cikislari_kapat(self):
        self.en = False
        self._motor_ani_dur()
        self.k1 = False
        self.k2 = False
        self._k2_bas_ms = None

    def _arizaya_gec(self, neden, simdi):
        self._cikislari_kapat()
        self.guc = "ariza"
        self.ariza = neden
        self._olay(simdi)
        self._olay_gonder()

    def _guc_guncelle(self, simdi):
        if self.guc not in ("onsarj", "devrede"):
            return
        if self.mantar:
            return self._arizaya_gec("acil_stop", simdi)
        if self.k1 and not self._bara_gerilimli():
            return self._arizaya_gec("bara_gitti", simdi)
        if self.guc == "onsarj":
            self._onsarj_yurut(simdi)
        else:
            self._devrede_denetle(simdi)

    def _onsarj_yurut(self, simdi):
        # K2 süre sınırı (esp_timer): K2 bundan uzun çekili kalmaz
        if self.k2 and simdi - self._k2_bas_ms >= self.k2_en_cok_ms:
            self.k2 = False
            return self._arizaya_gec("onsarj_sure", simdi)
        gecen = simdi - self._adim_bas_ms
        if self._onsarj_adimi == 0:
            if gecen < self.onsarj_bekleme_ms:
                return
            if not self._bara_gerilimli():
                return self._arizaya_gec("bara_yok", simdi)
            self.k1 = True
            self._onsarj_adimi = 1
            self._adim_bas_ms = simdi
            return
        if gecen < self.k1_sonrasi_ms:
            return
        self.k2 = False
        self._k2_bas_ms = None
        if not self._bara_gerilimli():
            return self._arizaya_gec("bara_gitti", simdi)
        self._son_komut_ms = simdi
        self._i2c_hata = 0
        self._son_i2c_ms = simdi
        self.en = True
        self.guc = "devrede"
        self.ariza = None
        self._olay(simdi)
        self._olay_gonder()

    def _devrede_denetle(self, simdi):
        if simdi - self._son_i2c_ms >= 100:
            self._son_i2c_ms = simdi
            self._i2c_hata = 0 if self.i2c_saglam else self._i2c_hata + 1
            if self._i2c_hata >= 3:
                return self._arizaya_gec("i2c", simdi)
        if self.sessizlik_ms > 0 and simdi - self._son_komut_ms >= self.sessizlik_ms:
            return self._arizaya_gec("sessizlik", simdi)

    def _guc_arm(self, simdi):
        if self.guc == "devrede":
            return "zaten_devrede"
        if self.guc == "onsarj":
            return "mesgul"
        if self.mantar:
            return "acil_stop"
        if not self.pca_var or not self.i2c_saglam:
            return "pca9685_yok"
        self.en = False
        self._motor_ani_dur()
        self.k2 = True
        self._k2_bas_ms = simdi
        self._onsarj_adimi = 0
        self._adim_bas_ms = simdi
        self.guc = "onsarj"
        self.ariza = None
        self._olay(simdi)
        return None

    def _guc_birak(self, simdi):
        self._cikislari_kapat()
        if self.guc in ("onsarj", "devrede"):
            self.guc = "birakik"
            self.ariza = None
            self._olay(simdi)

    # ================================================================ seri (seri_protokol.cpp)

    def _seri_isle(self, simdi):
        islenen = 0
        while islenen < 256 and self._gelen and self.calisiyor:
            i = self._gelen.find(b"\n")
            if i < 0:
                if len(self._gelen) > 4096:          # sonsuz satır: firmware tamponu taşınca atar
                    self._gelen = self._gelen[-(P.EN_COK_BAYT + 1):]
                return
            satir = bytes(self._gelen[:i]).replace(b"\r", b"")
            del self._gelen[:i + 1]
            islenen += i + 1
            if len(satir) > P.EN_COK_BAYT:
                self._yaz({"ok": False, "hata": "satir_cok_uzun"})
                continue
            self._satir_isle(satir, simdi)

    def _satir_isle(self, satir, simdi):
        if not satir:
            return                                   # boş satır: sessizce geç
        try:
            d = P.coz(satir)
        except P.BozukSatir:
            return self._yaz({"ok": False, "hata": "json_bozuk"})
        k = d.get("k") if isinstance(d, dict) else None
        if not isinstance(k, str):
            return self._yaz({"ok": False, "hata": "k_yok"})
        if k not in P.KOMUTLAR:
            return self._yaz({"ok": False, "k": k, "hata": "bilinmeyen_komut"})
        self._son_komut_ms = simdi                   # geçerli komut satırı: sessizlik sayacı
        getattr(self, "_k_" + k)(d, simdi)
        self._olay_gonder()                          # komut gücü değiştirdiyse olay cevaptan SONRA

    def _hata(self, k, hata):
        self._yaz({"ok": False, "k": k, "hata": hata})

    def _ok(self, k, **alanlar):
        m = {"ok": True, "k": k}
        m.update(alanlar)
        self._yaz(m)

    def _rampa_kipi(self):
        return self.rampa_elle                       # IMU yok (0.5.0): yalnız elle

    def _rampa_uygula(self, eski):
        if self._rampa_kipi() and not eski:
            self.jest = None
            self.servo_hedef = [float(s["ev"]) for s in self.servo_tablo]

    def _k_arm(self, d, simdi):
        hata = self._guc_arm(simdi)
        if hata:
            return self._hata("arm", hata)
        self._ok("arm", guc=self.guc)

    def _k_birak(self, d, simdi):
        self._guc_birak(simdi)
        self._ok("birak", ms=simdi)

    def _k_reset(self, d, simdi):
        self._guc_birak(simdi)
        self._ok("reset")
        self._olay_gonder()
        self.calisiyor = False
        self._acilis_bitis = self.dunya_ms + self.acilis_ms
        self._gelen.clear()

    def _k_sur(self, d, simdi):
        if self.guc != "devrede":
            return self._hata("sur", "devrede_degil")
        v, w = d.get("v"), d.get("w")
        if not (P.tur_uyar(v, "sayi") and P.tur_uyar(w, "sayi")):
            return self._hata("sur", "v_w_sayi_olmali")
        rampa = d.get("rampa")
        if rampa is not None and not isinstance(rampa, bool):
            return self._hata("sur", "rampa_bool_olmali")
        if rampa is not None:
            eski = self._rampa_kipi()
            self.rampa_elle = rampa
            self._rampa_uygula(eski)
        self._motor_hedef(float(v), float(w))
        self._son_sur_ms = simdi                     # watchdog_besle
        self.bekci_tetikli = False
        if rampa is None:
            return self._ok("sur")
        self._ok("sur", rampa=self._rampa_kipi())

    def _k_dur(self, d, simdi):
        self.v_hedef = self.w_hedef = 0.0
        self.hedef = [0.0, 0.0]                      # fren sınırıyla durur
        self.jest = None
        self._ok("dur")

    def _k_rampa(self, d, simdi):
        ac = d.get("ac")
        if not isinstance(ac, bool):
            return self._hata("rampa", "ac_bool_olmali")
        eski = self._rampa_kipi()
        self.rampa_elle = ac
        self._rampa_uygula(eski)
        self._ok("rampa", rampa=self._rampa_kipi(), elle=self.rampa_elle, imu=False)

    def _k_servo(self, d, simdi):
        if self._rampa_kipi():
            return self._hata("servo", "rampa_modunda")
        kanal = d.get("kanal")
        if P.tur_uyar(kanal, "tamsayi"):
            sira = next((i for i, s in enumerate(self.servo_tablo) if s["kanal"] == kanal), -1)
        elif isinstance(kanal, str):
            sira = self.servo_adlari.index(kanal) if kanal in self.servo_adlari else -1
        else:
            return self._hata("servo", "kanal_yok")
        if sira < 0:
            return self._hata("servo", "bilinmeyen_kanal")
        aci = d.get("aci")
        if not P.tur_uyar(aci, "sayi"):
            return self._hata("servo", "aci_sayi_olmali")
        if not self.pca_var:
            return self._hata("servo", "pca9685_yok")
        self.jest = None
        uygulanan = self._servo_hedef_ayarla(sira, float(aci))
        self._ok("servo", kanal=self.servo_adlari[sira], aci=uygulanan)

    def _servo_hedef_ayarla(self, sira, aci):
        t = self.servo_tablo[sira]
        aci = min(max(aci, t["min"]), t["max"])      # servolar.cpp sinira_kirp
        self.servo_hedef[sira] = aci
        if self.bagimli_sinir_acik:                  # TASLAK: eklem_sinirlari.json bagimli
            for kosul_ad, kosul_alt, sinir_ad, sinir_ust in self.bagimli:
                ki, si = self.servo_adlari.index(kosul_ad), self.servo_adlari.index(sinir_ad)
                if self.servo_hedef[ki] >= kosul_alt and self.servo_hedef[si] > sinir_ust:
                    if sira == si:
                        aci = sinir_ust
                    self.servo_hedef[si] = sinir_ust
        return aci

    def _k_jest(self, d, simdi):
        ad = d.get("ad")
        if not isinstance(ad, str):
            return self._hata("jest", "ad_yok")
        if self._rampa_kipi() and ad != "bosta":
            return self._hata("jest", "rampa_modunda")
        yon = d.get("yon")
        if yon is not None and (not isinstance(yon, str) or yon not in P.JEST_YONLERI):
            return self._hata("jest", "yon_gecersiz")
        if not self.pca_var:
            return self._hata("jest", "pca9685_yok")
        if ad not in P.JESTLER:
            return self._hata("jest", "bilinmeyen_jest")
        self.jest = ad
        self._jest_bitis = simdi + self.jest_suresi_ms
        if yon is None:
            return self._ok("jest", ad=ad)
        self._ok("jest", ad=ad, yon=yon, yon_uygulandi=ad in P.YONLU_JESTLER)

    def _k_ping(self, d, simdi):
        m = {"ok": True, "k": "ping", "surum": SURUM, "ms": simdi, "pca9685": self.pca_var, "odo": True,
             "rampa": self._rampa_kipi(), "guc": self.guc, "acil": self.mantar, "bara": self._bara_gerilimli(),
             "aku": round(self.aku_v, 2) if self.ana_anahtar else None,   # guc.cpp aku_olc: < 1 V -> null
             "ariza": self.ariza, "jestler": list(P.JESTLER)}
        if self.yetenekler():
            m["yetenekler"] = self.yetenekler()
        if self.sonar_acik:
            m["sonar"] = dict(self.sonar)
            m["engel"] = self.engel
        self._yaz(m)

    def _k_odo_sifirla(self, d, simdi):
        self.tik = [0, 0]
        self._tik_kesir = [0.0, 0.0]
        self._ok("odo_sifirla")

    # ================================================================ bekçi (watchdog.cpp)

    def _bekci_kontrol(self, simdi):
        if not self.bekci_tetikli and simdi - self._son_sur_ms >= self.bekci_ms:
            self._motor_ani_dur()                    # rampasız (0.5.0); K1'e dokunmaz
            self.bekci_tetikli = True

    # ================================================================ motorlar (motorlar.cpp)

    def _motor_hedef(self, v, w):
        self.v_hedef = _kirp(v, self.v_giris)
        self.w_hedef = _kirp(w, self.w_giris)
        self.hedef = self._teker_hedefleri(self.v_hedef, self.w_hedef)

    def _teker_hedefleri(self, v, w):
        # firmware sabitiyle (0,426); fiziksel iz (0,432) yalnız _hareket'te. Fark bilerek görünür (Y0s-gunluk Ç3).
        v_sol = v - w * self.fw_iz / 2.0
        v_sag = v + w * self.fw_iz / 2.0
        en_buyuk = max(abs(v_sol), abs(v_sag))
        if en_buyuk > self.azami_hiz:                # ikisini birlikte küçült (dönüş yarıçapı korunur)
            o = self.azami_hiz / en_buyuk
            v_sol, v_sag = v_sol * o, v_sag * o
        return [v_sol, v_sag]

    def _motor_ani_dur(self):
        self.v_hedef = self.w_hedef = 0.0
        self.hedef = [0.0, 0.0]
        self.rampa_hiz = [0.0, 0.0]

    def _ileri_sinir(self):
        """TASLAK (plan Y3): sonar engel kuralı. İleri hız sınırı (m/s) ya da None (sınır yok)."""
        if not self.sonar_acik:
            return None
        olcum = [v for v in self.sonar.values() if v is not None]
        if not olcum:
            return None
        d = min(olcum)
        if d < self.sonar_dur_cm:
            return 0.0
        if d < self.sonar_yavas_cm:
            oran = (d - self.sonar_dur_cm) / (self.sonar_yavas_cm - self.sonar_dur_cm)
            return max(self.sonar_yavas_en_az, self.azami_hiz * oran)
        return None

    def _motor_guncelle(self):
        dt = DILIM_MS / 1000.0
        if self.guc != "devrede" and (any(self.rampa_hiz) or any(self.hedef)):
            self._motor_ani_dur()                    # savunma: güç yokken hedef olmaz
        hedef = self.hedef
        sinir = self._ileri_sinir()
        if sinir is not None and self.v_hedef > sinir:
            hedef = self._teker_hedefleri(sinir, self.w_hedef)
        surus, fren = self.ivme["rampa" if self._rampa_kipi() else "duz"]
        for i in (0, 1):
            s, h = self.rampa_hiz[i], hedef[i]
            fark = h - s
            if (s > 0 and fark < 0) or (s < 0 and fark > 0):      # yavaşlıyor: fren sınırı
                yeni = s + _kirp(fark, fren * dt)
                if (s > 0 and yeni < 0) or (s < 0 and yeni > 0):
                    yeni = 0.0
            else:
                yeni = s + _kirp(fark, surus * dt)
            self.rampa_hiz[i] = yeni
        self._hareket(dt)

    def _hareket(self, dt):
        """İdeal diferansiyel sürüş (kayma yok, motor dinamiği yok). Çarpışırsa robot ilerlemez."""
        v_sol, v_sag = self.rampa_hiz
        v = (v_sol + v_sag) / 2.0
        w = (v_sag - v_sol) / self.iz
        if v == 0.0 and w == 0.0:
            return
        orta = self.aci + w * dt / 2.0
        nx = self.x + v * math.cos(orta) * dt
        ny = self.y + v * math.sin(orta) * dt
        na = self.aci + w * dt
        if self._carpar(nx, ny, na):
            if not self.carpiyor:
                self.carpisma_sayisi += 1
            self.carpiyor = True
            return                                   # teker döner ama robot ilerlemez: enkoder de saymaz (kilit)
        self.carpiyor = False
        self.yol_m += abs(v) * dt
        self.x, self.y, self.aci = nx, ny, na
        for i, vi in enumerate((v_sol, v_sag)):
            self._tik_kesir[i] += vi * dt / (math.pi * self.teker_capi) * self.tik_tur
            tam = int(self._tik_kesir[i])
            self.tik[i] += tam
            self._tik_kesir[i] -= tam

    def _koseler(self, x, y, a):
        c, s = math.cos(a), math.sin(a)
        yd, yg = self.taban_d / 2.0, self.taban_g / 2.0
        return [(x + c * px - s * py, y + s * px + c * py) for px, py in ((yd, yg), (-yd, yg), (-yd, -yg), (yd, -yg))]

    def _carpar(self, x, y, a):
        return self.harita.cokgen_carpar(self._koseler(x, y, a))

    def _yerel_dunya(self, px, py):
        c, s = math.cos(self.aci), math.sin(self.aci)
        return self.x + c * px - s * py, self.y + s * px + c * py

    # ================================================================ servolar (servolar.cpp, jestler.cpp)

    def _servo_guncelle(self, simdi):
        if self.jest is not None and simdi >= self._jest_bitis:
            self.jest = None
            self.servo_hedef = [float(s["ev"]) for s in self.servo_tablo]   # jest bitince boşta duruş
        dt = DILIM_MS / 1000.0
        for i, t in enumerate(self.servo_tablo):
            adim = t["hiz_derece_s"] * dt
            self.servo_simdi[i] += _kirp(self.servo_hedef[i] - self.servo_simdi[i], adim)

    # ================================================================ sonar (TASLAK; plan Y3, pin-haritasi.md Y9)

    def _sonar_guncelle(self, simdi):
        if not self.sonar_acik:
            return
        aralik = self.sonar_tur_ms // len(self.sonarlar)
        if simdi - self._son_sonar_tetik < aralik:
            return
        self._son_sonar_tetik = simdi
        adlar = list(self.sonarlar)
        ad = adlar[self._sonar_sira % len(adlar)]
        self._sonar_sira += 1
        self.sonar[ad] = self._sonar_olc(ad)
        eski = self.engel
        olcum = [v for v in self.sonar.values() if v is not None]
        en_yakin = min(olcum) if olcum else None
        if not eski and en_yakin is not None and en_yakin < self.sonar_dur_cm:
            self.engel = True
        elif eski and (en_yakin is None or en_yakin >= self.sonar_dur_cm + self.sonar_histerezis_cm):
            self.engel = False
        if self.engel != eski:
            sensor = min((k for k in self.sonar if self.sonar[k] is not None), key=lambda k: self.sonar[k]) \
                if en_yakin is not None else None
            self._yaz({"k": "engel", "var": self.engel, "sensor": sensor, "cm": en_yakin, "ms": simdi})

    def _sonar_olc(self, ad):
        s = self.sonarlar[ad]
        sx, sy = self._yerel_dunya(s["x_m"], s["y_m"])
        yon = self.aci + s["aci_rad"]
        en_az, en_cok = self.sonar_menzil
        n = self.sonar_isin
        en_iyi = None
        isinlar = []
        for i in range(n):
            a = yon - self.sonar_yari_aci + 2.0 * self.sonar_yari_aci * i / (n - 1)
            r = self.harita.isin(sx, sy, a, en_cok)
            if r is None:
                isinlar.append((sx, sy, sx + math.cos(a) * en_cok, sy + math.sin(a) * en_cok, False))
                continue
            t, gelis = r
            yanki = gelis <= self.sonar_gelis_siniri and t >= en_az
            isinlar.append((sx, sy, sx + math.cos(a) * t, sy + math.sin(a) * t, yanki))
            if yanki and (en_iyi is None or t < en_iyi):
                en_iyi = t
        self.son_isinlar[ad] = isinlar
        return None if en_iyi is None else round(en_iyi * 100.0, 1)
