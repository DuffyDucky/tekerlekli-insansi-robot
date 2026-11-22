"""Güvenlik senaryoları. Her testin docstring'inin ilk satırı dayandığı plan maddesidir (dosya ve bölüm).

Testler kartla yalnız protokol üzerinden konuşur. Asıl iddia önce PROTOKOLDEN doğrulanır (cevap / hata, güç olayı, `ping`,
enkoder tikleri: hız `odo` farkından ölçülür); hakem (haritadaki gerçek konum / hız) yalnız EK doğrulamadır ve gerçek kartta
yoksa atlanır (`hakem_varsa`). `LALE_HAKEM=yok` ile bu durum sahte kartta da prova edilir.

Plan değerleri (30 cm, 500 ms, 5 s, 600 ms) burada BİLEREK sabit yazılı: test, tek kaynaktaki değeri değil planı doğrular
(`test_protokol_kaynak` ayrıca tek kaynağın plana eşit olduğunu denetler).
"""

import unittest

from testler.duzenek import FIZIK_DURUS, TIK_M, LaleTesti

PLAN_SONAR_DUR_CM = 30        # yazilim-plani.md Y3 kabul testi
TASLAK_HISTEREZIS_CM = 5      # protokol.json guvenlik.sonar_histerezis_cm (TASLAK; plan belirtmiyor)
PLAN_BEKCI_MS = 500           # yazilim-plani.md mimari "güvenlik 500 ms"; Y1 kabul testi
PLAN_SESSIZLIK_MS = 5000      # main kod/esp32/src/guc.h SESSIZLIK_BIRAK_MS (0.5.0 sözleşmesi)
PLAN_ARM_MS = 500 + 100       # pin-haritasi.md Y4 (ön şarj + K1 sonrası); ön şarj 500: elektrik.md E9, main pinler.json
TEKER_AZAMI = 0.39            # main motorlar.cpp TEKER_AZAMI_HIZ (TAHMİN, kod/ortak/robot_parametreleri.json)
FW_IZ = 0.426                 # main motorlar.cpp IZ_GENISLIGI_M (komut -> teker hızı dönüşümü)
IVME_DUZ, FREN_DUZ, IVME_RAMPA = 0.5, 1.8, 0.1   # eklem_sinirlari.json teker.ivme_sinir_m_s2


def _en_yakin(sonar):
    olcum = [v for v in (sonar.get("sol"), sonar.get("orta"), sonar.get("sag")) if v is not None]
    return min(olcum) if olcum else None


# ====================================================================== sonar (TASLAK yetenek)

class SonarDurma(LaleTesti):
    HARITA = "oda_bos"
    KONUM = (3.0, 2.5, 0.0)        # duvar x = 6 m; orta sonarın önü ≈ 2,74 m

    def setUp(self):
        super().setUp()
        self.yetenek_gerek("sonar")
        self.devreye_al()

    def _duvara_sur(self, v=0.3):
        bas = len(self.esp.gelen)
        self.esp.sur_tut(v, 0.0, 14000, dur_kosul=lambda e: any(
            m.get("k") == "engel" and m.get("var") for _, m in e.gelen[bas:]))
        self.esp.sur_tut(v, 0.0, 1500)          # engel geldikten sonra da ileri istemeye devam et
        return bas

    def test_30cm_esiginde_durur(self):
        """Dayanak: yazilim-plani.md § İş paketleri Y3 kabul testi "30 cm'de engel olunca duruyor"; mimari "sensör 3 × HC-SR04"."""
        bas = self._duvara_sur()
        engel = [m for m in self.esp.mesajlar("engel", bas) if m["var"]]
        self.assertEqual(len(engel), 1, "tek engel olayı bekleniyor")
        self.assertLess(engel[0]["cm"], PLAN_SONAR_DUR_CM)
        # protokol: ileri istenmesine rağmen enkoder sayımı durdu
        odo1 = self.odo_son()
        self.esp.sur_tut(0.3, 0.0, 1000)
        odo2 = self.odo_son()
        self.assertEqual((odo1["sol"], odo1["sag"]), (odo2["sol"], odo2["sag"]), "engel varken teker dönüyor")
        en_yakin = _en_yakin(self.esp.son["sonar"])
        self.assertGreaterEqual(en_yakin, PLAN_SONAR_DUR_CM - 5, "eşiğin çok içinde durdu")
        self.assertLess(en_yakin, PLAN_SONAR_DUR_CM)
        h = self.hakem_varsa()
        if h:
            self.assertEqual(h["carpisma_sayisi"], 0)
            self.assertEqual(h["v"], 0.0)
            self.assertGreater(h["on_engel_m"], 0.25)
            self.assertLess(h["on_engel_m"], 0.30)

    def test_engelde_geri_gidilir_engel_histerezisle_kalkar(self):
        """Dayanak: yazilim-plani.md Y3 ("sonarla yavaşlama ve durma"); geri gitme ve 5 cm histerezis TASLAK (protokol.json guvenlik)."""
        self._duvara_sur()
        bas = len(self.esp.gelen)
        odo1 = self.odo_son()
        self.esp.sur_tut(-0.2, 0.0, 1500)
        odo2 = self.odo_son()
        self.assertLess(odo2["sol"], odo1["sol"], "engel varken geri gidilemedi")
        kalkti = [m for m in self.esp.mesajlar("engel", bas) if not m["var"]]
        self.assertEqual(len(kalkti), 1, "geri gidince engel kalkmalı")
        self.assertGreaterEqual(kalkti[0]["cm"], PLAN_SONAR_DUR_CM + TASLAK_HISTEREZIS_CM)
        # davranış: 30–35 cm arasında ölçüm geldiği halde engel kalkmadı (histerezis)
        ara = 0
        for _, m in self.esp.gelen[bas:]:
            if m.get("k") == "engel":
                break
            if m.get("k") == "sonar":
                d = _en_yakin(m)
                if d is not None and PLAN_SONAR_DUR_CM <= d < PLAN_SONAR_DUR_CM + TASLAK_HISTEREZIS_CM:
                    ara += 1
        self.assertGreater(ara, 0, "histerezis bandında ölçüm yok (test kurgusu)")

    def test_yavaslama_bolgesinde_hiz_azalir(self):
        """Dayanak: yazilim-plani.md Y3 "sonarla yavaşlama"; 60 cm başlangıcı TASLAK (plan belirtmiyor)."""
        self.ortam.konum_ayarla(4.0, 2.5, 0.0)   # orta sonarın önü ≈ 1,74 m
        bas = len(self.esp.gelen)
        self.esp.sur_tut(0.39, 0.0, 6000)
        # her odo penceresi için pencere başındaki (eski = daha uzak = gevşek sınır) orta sonar ölçümü
        son_sonar = None
        onceki = None
        pencereler = []
        for _, m in self.esp.gelen[bas:]:
            if m.get("k") == "sonar":
                son_sonar = m.get("orta")
            elif m.get("k") == "odo":
                if onceki is not None and m["ms"] > onceki[0]["ms"] and onceki[1] is not None:
                    dt = (m["ms"] - onceki[0]["ms"]) / 1000.0
                    v = (m["sol"] - onceki[0]["sol"] + m["sag"] - onceki[0]["sag"]) / 2.0 * TIK_M / dt
                    pencereler.append((onceki[1], v))
                onceki = (m, son_sonar)
        uzak = [v for d, v in pencereler if 70 < d < 95]
        yakin = [(d, v) for d, v in pencereler if 35 < d < 50]
        self.assertTrue(uzak and yakin, pencereler)
        self.assertGreater(min(uzak), TEKER_AZAMI - 0.01, "yavaşlama 60 cm'den önce başladı")
        for d, v in yakin:
            self.assertLessEqual(v, TEKER_AZAMI * (d - PLAN_SONAR_DUR_CM) / 30.0 + 0.03,
                                 "yavaşlama bölgesinde hız azalmadı (d=%.1f)" % d)


class SonarMenzil(LaleTesti):
    HARITA = "acik_alan"           # tek duvar x = 20 m, çevre duvarı yok

    def setUp(self):
        super().setUp()
        self.yetenek_gerek("sonar")

    def test_menzil_disi_null(self):
        """Dayanak: TASLAK (plan belirtmiyor): HC-SR04 2–400 cm dışı / yankı yok = null (protokol.json mesajlar.sonar)."""
        self.ortam.konum_ayarla(15.0, 15.0, 0.0)  # duvar ≈ 4,74 m
        self.esp.bekle(300)
        s = self.esp.son["sonar"]
        self.assertEqual((s["sol"], s["orta"], s["sag"]), (None, None, None))
        self.ortam.konum_ayarla(17.0, 15.0, 0.0)  # duvar ≈ 2,74 m
        self.esp.bekle(300)
        self.assertAlmostEqual(self.esp.son["sonar"]["orta"], 274.4, delta=0.2)

    def test_egik_yuzey_yanki_vermez(self):
        """Dayanak: TASLAK (plan belirtmiyor): 60°'den eğik gelen ışın yankı vermez (robot_parametreleri.json, TAHMİN)."""
        self.ortam.konum_ayarla(19.5, 15.0, 78.0)
        self.esp.bekle(300)
        self.assertIsNone(self.esp.son["sonar"]["orta"])
        self.ortam.konum_ayarla(19.5, 15.0, 0.0)
        self.esp.bekle(300)
        self.assertIsNotNone(self.esp.son["sonar"]["orta"])


# ====================================================================== acil stop ve devreye alma

class AcilStop(LaleTesti):

    def test_acil_stop_kilitler_yeniden_devreye_alma_operatorle(self):
        """Dayanak: yazilim-plani.md § "Donanımdan gelen kurallar" (E3 + E9 dizisi, PC817 #1 HIGH → GPIO4 0 ve kilit); pin-haritasi.md § 5 Y4, Y5; elektrik.md E3."""
        self.devreye_al()
        self.assertGreater(self.sur_olc(0.3, 0.0, 1500)[0], 0.25)
        bas = len(self.esp.gelen)
        self.ortam.mantar_bas()
        olay = self.guc_olayi_bekle("ariza", 50)
        self.assertEqual(olay["neden"], "acil_stop")
        self.esp.bekle(350)
        self.assertTrue(self.enkoder_duruyor(bas, sonra_ms=olay["ms"], durus="bosta"), "acil stop sonrası enkoder sayıyor")
        h = self.hakem_varsa()
        if h:
            self.assertEqual(h["v"], 0.0)
        self.hata_bekle(self.esp.sur(0.3, 0.0), "devrede_degil", "sur")
        p = self.esp.ping()
        self.assertTrue(p["acil"])
        self.assertEqual((p["guc"], p["ariza"]), ("ariza", "acil_stop"))
        # mantar bırakılınca güç kendiliğinden gelmez
        self.ortam.mantar_birak()
        self.esp.bekle(2000)
        p = self.esp.ping()
        self.assertEqual((p["guc"], p["ariza"], p["acil"]), ("ariza", "acil_stop", False))
        # birak kilidi çözmez
        self.assertTrue(self.esp.istek({"k": "birak"})["ok"])
        self.assertEqual(self.esp.ping()["guc"], "ariza")
        # mantar basılıyken arm reddedilir
        self.ortam.mantar_bas()
        self.esp.bekle(20)
        self.hata_bekle(self.esp.arm(), "acil_stop", "arm")
        self.ortam.mantar_birak()
        self.esp.bekle(20)
        # operatör arm'ı: ön şarj → devrede, sonra sürülür
        self.devreye_al()
        self.assertGreater(self.sur_olc(0.2, 0.0, 1000)[0], 0.15)
        tum = [m["guc"] for m in self.esp.mesajlar("guc", bas)]
        self.assertEqual(tum, ["ariza", "onsarj", "devrede"])

    def test_onsarjda_mantar_ariza(self):
        """Dayanak: pin-haritasi.md § 5 Y4 (ön koşul mantar serbest), Y5 (mantar → bırak + kilit)."""
        self.assertEqual(self.esp.arm()["guc"], "onsarj")
        self.esp.bekle(200)
        self.ortam.mantar_bas()
        olay = self.guc_olayi_bekle("ariza", 50)
        self.assertEqual(olay["neden"], "acil_stop")

    def test_devreye_alma_dizisi_zamani(self):
        """Dayanak: pin-haritasi.md § 5 Y4 (K2 → bekleme → bara teyidi → K1 → 100 ms → K2 bırak); elektrik.md E9 (500 ms önerisi); main pinler.json arm."""
        bas = len(self.esp.gelen)
        c = self.esp.arm()
        self.assertEqual((c["ok"], c["guc"]), (True, "onsarj"))
        onsarj = self.guc_olayi_bekle("onsarj", 50, bas=bas)
        self.hata_bekle(self.esp.arm(), "mesgul", "arm")
        devrede = self.guc_olayi_bekle("devrede", 1500)
        self.assertAlmostEqual(devrede["ms"] - onsarj["ms"], PLAN_ARM_MS, delta=max(20, self.tol))
        self.hata_bekle(self.esp.arm(), "zaten_devrede", "arm")

    def test_bara_yoksa_devreye_girmez(self):
        """Dayanak: pin-haritasi.md § 5 Y4 ("5 LOW olmalı (bara var), değilse 19 = 0 ve hata"); elektrik.md E3 "PC817 #2 500 ms içinde LOW olmazsa hata"."""
        self.ortam.ana_anahtar(False)
        self.assertTrue(self.esp.arm()["ok"])
        olay = self.guc_olayi_bekle("ariza", 1500)
        self.assertEqual(olay["neden"], "bara_yok")
        self.hata_bekle(self.esp.sur(0.1, 0.0), "devrede_degil", "sur")

    def test_acilis_ve_reset_guc_kapali(self):
        """Dayanak: yazilim-plani.md § "Donanımdan gelen kurallar" ("ESP32 reseti = güç kapalı", yeniden devreye alma yalnız operatörle); main seri_protokol.h "reset ... ESP32 yeniden başlar (ardından hazir gelir; güç birakik)", seri_protokol.cpp ESP.restart()."""
        p = self.esp.ping()
        self.assertEqual(p["guc"], "birakik")
        self.hata_bekle(self.esp.sur(0.1, 0.0), "devrede_degil", "sur")
        self.devreye_al()
        self.esp.sur_tut(0.3, 0.0, 1000)
        once = self.esp.ping()
        self.assertGreater(self.esp.son["odo"]["sol"], 0)
        odo_once = dict(self.esp.son["odo"])
        bas = len(self.esp.gelen)
        self.assertTrue(self.esp.istek({"k": "reset"})["ok"])
        hazir = self.esp.bekle_kosul(lambda m: m.get("k") == "hazir", 2000, bas=bas)
        self.assertEqual(hazir["guc"], "birakik")
        # yeniden başlama: millis() ve enkoder toplamları sıfırdan (motorlar.cpp toplam = 0)
        sonra = self.esp.ping()
        self.assertLess(sonra["ms"], once["ms"], "reset sonrası kartın saati sıfırlanmadı")
        odo = self.esp.bekle_kosul(lambda m: m.get("k") == "odo", 500)
        if self.ortam.fizik:
            # FIZIK_FARKLARI "reset_odo" / "durus": reset = kart kapalı, EN LOW; robot boşta kayarken sayaç yeniden sayar
            self.surucu_kesik_dogrula("bosta")
            self.assertLess(odo["sol"], odo_once["sol"], "reset sonrası enkoder toplamı sıfırlanmadı")
            self.assertLessEqual(max(odo["sol"], odo["sag"]), FIZIK_DURUS["bosta"]["m"] / TIK_M,
                                 "reset sonrası boşta kayma payından uzun yol")
            self.esp.bekle(FIZIK_DURUS["bosta"]["ms"])
        else:
            self.assertEqual((odo["sol"], odo["sag"]), (0, 0), "reset sonrası enkoder toplamı sıfır değil")
        h = self.hakem_varsa()
        if h:
            self.assertEqual(h["v"], 0.0)
        self.hata_bekle(self.esp.sur(0.1, 0.0), "devrede_degil", "sur")
        self.esp.bekle(3000)
        self.assertEqual(self.esp.ping()["guc"], "birakik", "reset sonrası kendiliğinden devreye girdi")


# ====================================================================== bekçi, sessizlik, bağlantı

class Bekci(LaleTesti):

    def setUp(self):
        super().setUp()
        self.devreye_al()

    def _surup_birak(self):
        """Sür, son sur'u gönder; kartın saatiyle son sur anını (ping ms) döndür."""
        self.esp.sur_tut(0.3, 0.0, 1500)
        self.esp.sur(0.3, 0.0)                     # son sur; cevabı geldi = kart işledi
        return self.esp.ping()["ms"]

    def test_500ms_sur_gelmezse_durur(self):
        """Dayanak: yazilim-plani.md § Mimari "güvenlik: 500 ms Pi'den mesaj gelmezse teker DUR"; Y1 kabul testi; main watchdog.cpp."""
        p_ms = self._surup_birak()
        bas = len(self.esp.gelen)
        self.esp.bekle(PLAN_BEKCI_MS - 30 - self.tol)
        h = self.hakem_varsa()
        if h:
            self.assertGreater(h["v"], 0.25, "bekçi erken tetiklendi")
        self.esp.bekle(30 + 2 * self.tol)
        self.hakem_durdu("fren", "500 ms sonra teker hâlâ dönüyor")
        self.esp.bekle(600)
        # protokol: odo, son sur'dan sonraki ~400 ms boyunca artıyor, 500 + pay ms sonra sabit
        odo = self.esp.mesajlar("odo", bas)
        once = [m["sol"] for m in odo if m["ms"] <= p_ms + PLAN_BEKCI_MS - 100]
        self.assertGreater(len(once), 2)
        self.assertTrue(all(b > a for a, b in zip(once, once[1:])), "bekçiden önce teker durmuş")
        self.assertTrue(self.enkoder_duruyor(bas, sonra_ms=p_ms + PLAN_BEKCI_MS + 20 + self.tol, en_az=3, durus="fren"),
                        "bekçiden sonra enkoder sayıyor")
        # güç bırakılmaz: bekçi yalnız motoru durdurur, yeni sur yeniden sürer
        self.assertEqual(self.esp.ping()["guc"], "devrede")
        self.assertGreater(self.sur_olc(0.2, 0.0, 600)[0], 0.1)

    def test_ping_bekciyi_beslemez(self):
        """Dayanak: main seri_protokol.h ("ping ... bekçiyi beslemez"); yazilim-plani.md ile fark Y0s-gunluk.md § 3 Ç4."""
        p_ms = self._surup_birak()
        bas = len(self.esp.gelen)
        for _ in range(9):
            self.esp.ping()
            self.esp.bekle(100)
        self.assertTrue(self.enkoder_duruyor(bas, sonra_ms=p_ms + PLAN_BEKCI_MS + 20 + self.tol, durus="fren"),
                        "yalnız ping varken teker dönmeye devam ediyor")
        h = self.hakem_varsa()
        if h:
            self.assertEqual(h["v"], 0.0)

    def test_dur_fren_siniriyla_durur(self):
        """Dayanak: eklem_sinirlari.json teker.ivme_sinir_m_s2.duz_fren 1,8 (karar 29.10); main seri_protokol.h "dur: FREN sınırıyla"."""
        self.esp.sur_tut(0.3, 0.0, 1500)
        bas = len(self.esp.gelen)
        self.esp.ham_gonder(b'{"k":"dur"}\n{"k":"ping"}\n')        # aynı turda işlenir: ping ms = dur anı
        p = self.esp.bekle_kosul(lambda m: m.get("k") == "ping" and m.get("ok"), 1000, bas=bas)
        t_dur = p["ms"]
        h = self.hakem_varsa()
        if h:
            self.assertGreater(h["v"], 0.0, "dur anında durdu (fren rampası yok)")
        self.esp.bekle(500)
        odo = [m for m in self.esp.mesajlar("odo") if m["ms"] > 0]
        ilk = [m for m in odo if m["ms"] <= t_dur][-1]
        son = odo[-1]
        self.assertTrue(self.enkoder_duruyor(bas, sonra_ms=t_dur + 300), "dur'dan 300 ms sonra teker dönüyor")
        yol = (son["sol"] - ilk["sol"] + son["sag"] - ilk["sag"]) / 2.0 * TIK_M
        fren_yolu = yol - 0.3 * (t_dur - ilk["ms"]) / 1000.0
        beklenen = 0.3 ** 2 / (2 * FREN_DUZ)                        # 0,025 m
        self.assertGreater(fren_yolu, 0.5 * beklenen, "fren yolu yok: anında durdu")
        pay = 0.005 if self.ortam.fizik else 0.0               # FIZIK_FARKLARI "dur_fren_yolu"
        self.assertLess(fren_yolu, 1.5 * beklenen + 0.3 * self.tol / 1000.0 + pay, "fren 1,8 m/s²'den yavaş")


class Sessizlik(LaleTesti):

    def test_5s_komut_yoksa_guc_birakilir(self):
        """Dayanak: main kod/esp32/src/guc.h SESSIZLIK_BIRAK_MS 5000 (0.5.0 sözleşmesi; plan karşılığı: kalp atışı)."""
        devrede = self.devreye_al()
        olay = self.guc_olayi_bekle("ariza", PLAN_SESSIZLIK_MS + 500)
        self.assertEqual(olay["neden"], "sessizlik")
        self.assertAlmostEqual(olay["ms"] - devrede["ms"], PLAN_SESSIZLIK_MS, delta=max(20, self.tol))

    def test_ping_ile_canli_kalir(self):
        """Dayanak: main seri_protokol.h ping ("Pi devredeyken saniyede bir atar (5 s sessizlik kuralı)")."""
        self.devreye_al()
        for _ in range(8):
            self.esp.ping()
            self.esp.bekle(1000)
        self.assertEqual(self.esp.ping()["guc"], "devrede")


class BaglantiKopmasi(LaleTesti):

    def test_kablo_cekilince_durur_ve_kilitlenir(self):
        """Dayanak: yazilim-plani.md Y1 kabul testi "kablo çekilince 500 ms içinde duruyor"; mimari güvenlik 500 ms; main guc.h sessizlik."""
        self.devreye_al()
        self.esp.sur_tut(0.3, 0.0, 1500)
        self.esp.sur(0.3, 0.0)
        p_ms = self.esp.ping()["ms"]               # son sur'un kart saati (≈)
        odo0 = self.esp.son["odo"]
        self.ortam.kablo_kopar()
        # kopukken Pi komut göndermeye devam etse de karta ulaşmaz
        for _ in range(5):
            try:
                self.esp.gonder({"k": "sur", "v": 0.3, "w": 0.0})
            except (ConnectionError, OSError):
                pass
            self.esp.bekle(100)
        self.hakem_durdu("fren", "kablo çekildikten 500 ms sonra teker dönüyor")
        self.esp.bekle(PLAN_SESSIZLIK_MS)
        self.ortam.kablo_bagla()
        self.esp.bekle(50)
        p = self.esp.ping()
        self.assertEqual((p["guc"], p["ariza"]), ("ariza", "sessizlik"))
        # protokol: kopukken kat edilen yol ≤ son sur'dan 500 ms (+ pay) tam hız
        odo1 = self.esp.bekle_kosul(lambda m: m.get("k") == "odo", 500)
        yol = (odo1["sol"] - odo0["sol"] + odo1["sag"] - odo0["sag"]) / 2.0 * TIK_M
        en_cok = 0.3 * (p_ms - odo0["ms"] + PLAN_BEKCI_MS + 30 + self.tol) / 1000.0
        if self.ortam.fizik:                                   # FIZIK_FARKLARI "kablo_yolu"
            en_cok += FIZIK_DURUS["fren"]["m"]
        self.assertLessEqual(yol, en_cok, "kablo çekildikten sonra 500 ms'den uzun sürdü")
        self.hata_bekle(self.esp.sur(0.3, 0.0), "devrede_degil", "sur")
        self.devreye_al()


# ====================================================================== bozuk / eksik mesaj

class BozukMesaj(LaleTesti):

    def setUp(self):
        super().setUp()
        self.devreye_al()

    def test_bozuk_satirlar_dogru_hata(self):
        """Dayanak: main seri_protokol.cpp satiri_isle / komut işleyicileri (hata adları protokol.json); yazilim-plani.md § İlke "ESP32 sınırları her komutta tekrar kontrol eder"."""
        vakalar = [
            (b"bu json degil\n", "json_bozuk", None),
            (b"\xff\xfe\n", "json_bozuk", None),
            (b"[1,2]\n", "k_yok", None),
            (b'{"v":1}\n', "k_yok", None),
            (b'{"k":5}\n', "k_yok", None),
            (b'{"k":"ucus"}\n', "bilinmeyen_komut", "ucus"),
            (b'{"k":"sur","v":0.1}\n', "v_w_sayi_olmali", "sur"),
            (b'{"k":"sur","v":"hizli","w":0}\n', "v_w_sayi_olmali", "sur"),
            (b'{"k":"sur","v":true,"w":0}\n', "v_w_sayi_olmali", "sur"),
            (b'{"k":"sur","v":0.1,"w":null}\n', "v_w_sayi_olmali", "sur"),
            (b'{"k":"sur","v":0.1,"w":0,"rampa":"evet"}\n', "rampa_bool_olmali", "sur"),
            (b'{"k":"rampa"}\n', "ac_bool_olmali", "rampa"),
            (b'{"k":"jest"}\n', "ad_yok", "jest"),
            (b'{"k":"jest","ad":"takla"}\n', "bilinmeyen_jest", "jest"),
            (b'{"k":"jest","ad":"isaret","yon":"yukari"}\n', "yon_gecersiz", "jest"),
            (b'{"k":"servo","aci":10}\n', "kanal_yok", "servo"),
            (b'{"k":"servo","kanal":12,"aci":10}\n', "bilinmeyen_kanal", "servo"),
            (b'{"k":"servo","kanal":"kuyruk","aci":10}\n', "bilinmeyen_kanal", "servo"),
            (b'{"k":"servo","kanal":"sag_dirsek"}\n', "aci_sayi_olmali", "servo"),
            (b'{"k":"sur","v":0.1,"w":' + b"0" * 200 + b"}\n", "satir_cok_uzun", None),
        ]
        for bayt, hata, k in vakalar:
            with self.subTest(satir=bayt[:40]):
                c = self.esp.ham_istek(bayt, k=k)
                self.hata_bekle(c, hata, k)
        # bozuk satırlar kartı bozmaz
        self.assertEqual(self.esp.ping()["guc"], "devrede")

    def test_nan_reddedilir(self):
        """Dayanak: main seri_protokol.cpp sayi_al (isfinite); NaN JSON değildir. Not: ArduinoJson'un NaN ayrıştırma varsayılanı doğrulanmadı (gerçek kartta hata adı farklı olabilir)."""
        c = self.esp.ham_istek(b'{"k":"sur","v":NaN,"w":0}\n', k="sur")
        self.assertIs(c["ok"], False)
        self.assertIn(c["hata"], ("json_bozuk", "v_w_sayi_olmali"))

    def test_bos_satir_sessiz_crlf_ve_parcali_satir(self):
        """Dayanak: main seri_protokol.cpp seri_isle ("\\r" atılır, boş satır sessiz); yazilim-plani.md mimari "satır başına bir JSON"."""
        bas = len(self.esp.gelen)
        self.esp.ham_gonder(b"\n\n")
        self.esp.bekle(100)
        self.assertEqual(self.esp.mesajlar("cevap", bas), [])
        self.assertTrue(self.esp.ham_istek(b'{"k":"ping"}\r\n', k="ping")["ok"])
        bas = len(self.esp.gelen)
        self.esp.ham_gonder(b'{"k":"pi')
        self.esp.bekle(60)
        self.esp.ham_gonder(b'ng"}\n{"k":"odo_sif')
        self.esp.bekle(60)
        self.esp.ham_gonder(b'irla"}\n')
        self.esp.bekle(60)
        cevaplar = [m["k"] for m in self.esp.mesajlar("cevap", bas)]
        self.assertEqual(cevaplar, ["ping", "odo_sifirla"])

    def test_bozuk_satir_bekciyi_ve_sessizligi_beslemez(self):
        """Dayanak: main seri_protokol.cpp ("sessizlik sayacı yalnız bilinen komutlarla beslenir"), watchdog.cpp; yazilim-plani.md mimari 500 ms."""
        self.esp.sur_tut(0.3, 0.0, 1000)
        self.esp.sur(0.3, 0.0)
        p0 = self.esp.ping()["ms"]                 # son geçerli sur'un kart saati (≈)
        bas = len(self.esp.gelen)
        # geçersiz sur (w yok) bilinen komuttur: sessizliği besler ama bekçiyi beslemez (firmware sırası)
        for _ in range(9):
            self.esp.ham_gonder(b'{"k":"sur","v":0.3}\n{bozuk\n{"k":"ucus"}\n')
            self.esp.bekle(100)
        self.assertTrue(self.enkoder_duruyor(bas, sonra_ms=p0 + PLAN_BEKCI_MS + 20 + self.tol, durus="fren"),
                        "geçersiz sur bekçiyi besledi")
        h = self.hakem_varsa()
        if h:
            self.assertEqual(h["v"], 0.0)
        p_ms = self.esp.ping()["ms"]               # son geçerli komut satırı
        bas = len(self.esp.gelen)
        for _ in range(28):                        # 5,6 s yalnız bozuk JSON ve bilinmeyen komut
            self.esp.ham_gonder(b'{bozuk\n{"k":"ucus"}\n')
            self.esp.bekle(200)
        olaylar = [m for m in self.esp.mesajlar("guc", bas) if m["guc"] == "ariza"]
        self.assertEqual(len(olaylar), 1, "bozuk satırlar sessizlik sayacını besledi")
        self.assertEqual(olaylar[0]["neden"], "sessizlik")
        self.assertAlmostEqual(olaylar[0]["ms"] - p_ms, PLAN_SESSIZLIK_MS, delta=max(20, self.tol))

    def test_istemci_protokol_disi_komutu_gondermez(self):
        """Dayanak: kod/ortak/protokol.json komutlar (Pi tarafı aynı tek kaynaktan denetler)."""
        from lale_pi.istemci import ProtokolHatasi
        for komut in ({"k": "sur", "v": 0.1}, {"k": "sur", "v": "x", "w": 0}, {"k": "ucus"}, {"k": "arm", "zorla": True}):
            with self.subTest(komut=komut):
                with self.assertRaises(ProtokolHatasi):
                    self.esp.gonder(komut)


# ====================================================================== sınır dışı hız ve servo

class SinirDisiHiz(LaleTesti):

    def setUp(self):
        super().setUp()
        self.devreye_al()

    def _ivmeler(self, bas):
        """Ardışık odo pencerelerinin ortalama hızlarından ivme dizisi (m/s²) ve hız dizisi."""
        hiz = [(ms, (a + b) / 2.0) for ms, a, b in self.odo_hizlari(bas)]
        ivme = [(v2 - v1) / ((t2 - t1) / 1000.0) for (t1, v1), (t2, v2) in zip(hiz, hiz[1:])]
        return ivme, [v for _, v in hiz]

    def test_cok_buyuk_v_teker_azamisine_kirpilir(self):
        """Dayanak: yazilim-plani.md § İlke ("ESP32 sınırları her komutta tekrar kontrol eder"); main motorlar.cpp GIRIS_SINIRI, TEKER_AZAMI_HIZ."""
        self.esp.sur_tut(5.0, 0.0, 2500)
        h = self.hakem_varsa()
        if h:
            self.hiz_esit(h["teker"][0], TEKER_AZAMI)
            self.hiz_esit(h["teker"][1], TEKER_AZAMI)
        # protokol: 100 ms'lik odo farkı teker azamisinin üstüne çıkmaz (1980 tik / tur, Ø125; TAHMİN)
        bas = len(self.esp.gelen)
        self.esp.sur_tut(5.0, 0.0, 1000)
        hiz = self.odo_hizlari(bas)
        self.assertTrue(hiz)
        pay = 0.01 if self.ortam.fizik else 0.0               # FIZIK_FARKLARI "hiz_esitligi"
        for _, sol, sag in hiz:
            self.assertLessEqual(max(sol, sag), TEKER_AZAMI + 2 * TIK_M / 0.1 + pay)
        self.assertGreater(hiz[-1][1], TEKER_AZAMI - 2 * TIK_M / 0.1)

    def test_cok_buyuk_w_kirpilir_donus_orani_korunur(self):
        """Dayanak: main motorlar.cpp motorlar_hedef (w ±1'e, iki teker birlikte küçültülür; IZ_GENISLIGI_M 0,426); yazilim-plani.md K1 "yay çizerek dönüş" (0.5.0'da yok, Y0s-gunluk Ç6)."""
        self.esp.sur_tut(0.3, 5.0, 2000)
        bas = len(self.esp.gelen)
        self.esp.sur_tut(0.3, 5.0, 1000)
        odo = self.esp.mesajlar("odo", bas)
        d_sol, d_sag = odo[-1]["sol"] - odo[0]["sol"], odo[-1]["sag"] - odo[0]["sag"]
        beklenen = (0.3 - FW_IZ / 2) / (0.3 + FW_IZ / 2)       # w 1'e kırpılır; oran firmware iziyle
        if self.ortam.fizik:
            # FIZIK_FARKLARI "w_kirpma": kırpmayı firmware'in sürücüye verdiği hedeflerden doğrula; yayın çizilip
            # çizilmediği (enkoder oranı) kızak yönlendirmenin fiziksel sonucudur, firmware doğrulaması değil
            s = self.hakem()["surucu"]
            self.assertTrue(s["suruluyor"])
            self.assertAlmostEqual(s["hedef_m_s"][1], TEKER_AZAMI, places=6)
            self.assertAlmostEqual(s["hedef_m_s"][0] / s["hedef_m_s"][1], beklenen, places=6)
            self.assertAlmostEqual(s["pwm"][0] / s["pwm"][1], beklenen, places=6)
            return
        self.assertAlmostEqual(d_sol / d_sag, beklenen, delta=0.01)
        sag_hiz = self.odo_hizlari(bas)[-1][2]
        self.assertAlmostEqual(sag_hiz, TEKER_AZAMI, delta=2 * TIK_M / 0.1)
        h = self.hakem_varsa()
        if h:
            v_sol, v_sag = h["teker"]
            self.assertAlmostEqual(v_sag, TEKER_AZAMI, places=6)
            self.assertAlmostEqual(v_sol / v_sag, beklenen, places=6)

    def test_ivme_siniri_duz_zemin(self):
        """Dayanak: yazilim-plani.md Y1 "ivme rampası (düz zeminde ≤ 0,5 m/s²)"; eklem_sinirlari.json teker.ivme_sinir_m_s2.duz_surus."""
        bas = len(self.esp.gelen)
        self.esp.sur_tut(0.3, 0.0, 1200)
        ivme, hiz = self._ivmeler(bas)
        self.assertGreater(max(hiz), 0.28, "hedef hıza varmadı")
        self.assertLessEqual(max(ivme), IVME_DUZ + 0.06, "ivme 0,5 m/s²'yi aştı")
        self.assertGreater(max(ivme), IVME_DUZ - 0.1)
        h = self.hakem_varsa()
        if h:
            self.hiz_esit(h["v"], 0.3)

    def test_rampa_kipinde_ivme_ve_kollar(self):
        """Dayanak: yazilim-plani.md § "Donanımdan gelen kurallar" + Y1 ("rampada ≤ 0,1 m/s² ve kollar ev pozunda"); main seri_protokol.h RAMPA KİPİ."""
        c = self.esp.istek({"k": "rampa", "ac": True})
        self.assertTrue(c["rampa"])
        self.hata_bekle(self.esp.istek({"k": "jest", "ad": "selam"}), "rampa_modunda", "jest")
        self.hata_bekle(self.esp.istek({"k": "servo", "kanal": "sag_dirsek", "aci": 60}), "rampa_modunda", "servo")
        self.assertTrue(self.esp.istek({"k": "jest", "ad": "bosta"})["ok"])
        bas = len(self.esp.gelen)
        self.esp.sur_tut(0.3, 0.0, 1500)
        ivme, hiz = self._ivmeler(bas)
        self.assertGreater(max(hiz), 0.05, "rampa kipinde hiç hızlanmadı")
        self.assertLessEqual(max(ivme), IVME_RAMPA + 0.05, "rampa kipinde ivme 0,1 m/s²'yi aştı")
        self.assertLess(max(hiz), IVME_RAMPA * (1.5 + 0.3 + self.tol / 1000.0))
        h = self.hakem_varsa()
        if h:
            self.assertLess(h["v"], IVME_RAMPA * (1.5 + 0.3 + self.tol / 1000.0))


class SinirDisiServo(LaleTesti):

    def test_servo_sinira_kirpilir(self):
        """Dayanak: yazilim-plani.md Y2 kabul testi "Sınır dışı komut kırpılıyor"; kod/ortak/eklem_sinirlari.json (tilt ±13, S2 ≥ +5, dirsek 0–105)."""
        vakalar = [
            ("kafa_tilt", 150, 103.0), ("kafa_tilt", -20, 77.0), ("kafa_tilt", 95, 95.0),
            ("sag_omuz_yan", 0, 5.0), ("sol_omuz_yan", 500, 120.0), ("sol_dirsek", 200, 105.0),
            ("sag_omuz", -10, 0.0), ("kafa_pan", 181, 180.0), (4, 30, 30.0), (9, 0, 77.0),
        ]
        for kanal, aci, beklenen in vakalar:
            with self.subTest(kanal=kanal, aci=aci):
                c = self.esp.istek({"k": "servo", "kanal": kanal, "aci": aci})
                self.assertTrue(c["ok"], c)
                self.assertEqual(c["aci"], beklenen)

    def test_bagimli_sinir(self):
        """Dayanak: kod/ortak/eklem_sinirlari.json bagimli ("S1 >= 120 iken S2 <= 117"); yazilim-plani.md Y2 "Sınır dışı komut kırpılıyor" (kırpma; Y0s-gunluk § 11 B4, Ç11). TASLAK: 0.5.0'da yok."""
        self.yetenek_gerek("bagimli_sinir")
        self.assertEqual(self.esp.istek({"k": "servo", "kanal": "sag_omuz", "aci": 170})["aci"], 170.0)
        self.assertEqual(self.esp.istek({"k": "servo", "kanal": "sag_omuz_yan", "aci": 120})["aci"], 117.0)
        self.assertEqual(self.esp.istek({"k": "servo", "kanal": "sol_omuz_yan", "aci": 120})["aci"], 120.0)
        self.assertEqual(self.esp.istek({"k": "servo", "kanal": "sag_omuz", "aci": 160})["aci"], 160.0)
        self.assertEqual(self.esp.istek({"k": "servo", "kanal": "sag_omuz_yan", "aci": 120})["aci"], 120.0)
        # S1'i koşul bölgesine sokmak S2'yi indirir (hakem; protokolde servo konumu yayımlanmıyor)
        self.esp.istek({"k": "servo", "kanal": "sag_omuz", "aci": 175})
        self.esp.bekle(1500)
        h = self.hakem_varsa()
        if h:
            self.assertLessEqual(h["servo"]["sag_omuz_yan"], 117.0)


if __name__ == "__main__":
    unittest.main()
