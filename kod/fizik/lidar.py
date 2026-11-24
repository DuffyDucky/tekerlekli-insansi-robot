"""Sanal 2B LiDAR: Slamtec RPLIDAR C1 taklidi (MuJoCo fizik dünyası). Belge: kod/SIMULASYON.md "Sanal LiDAR".

Sensörün bütün sayıları `kod/fizik/lidar_ozellik.json`'dan okunur (gerekçe: `planlama/lidar-secimi.md`); koda gömülü
sayı yalnız VARSAYIM olanlardır ve `LidarAyar`'da öyle işaretlidir. Gerçek robotta LiDAR Pi'ye USB'den bağlanır, ESP32'ye
değil: bu modül sahte ESP32 protokolüne hiçbir şey eklemez, yalnız fizik dünyasına (`dunya.FizikDunya`) bakar.

Tarama sözleşmesi (konumlama modülüyle ortak, `kod/fizik/konumlama/tarama.py`):
    {"t": saniye, "acilar": [rad, ...], "mesafeler": [m, ...]}
  - açı robot GÖVDE çerçevesinde: 0 = ileri, saat yönünün tersi +; dizi artan sırada, -pi'den başlar
    (konumlama `LidarOzellik.isin_acilari()` ile aynı ızgara: 500 ışın, 0,72 derece)
  - mesafe LiDAR merkezinden (montaj noktası); ölçüm yoksa (menzil dışı, kör sektör, geçersiz) NaN
  - t: taramanın İLK ışınının zamanı (`dunya.zaman_s` saati). Dönen taramada ışın i'nin zamanı t + `zaman_ofseti[i]`.
  - montaj ofseti `SanalLidar.montaj` (x, y, z m, yaw rad; gövde çerçevesinde)

Konum: LiDAR'ın yeri her ışında taban gövdesinin anlık konum / yöneliminden + montaj ofsetiyle hesaplanır; robot modeline
(`model/lale.xml`) site EKLENMEZ ve model yeniden üretilmez (kütle / geometri / sayı özetleri değişmez; montaj JSON'dan
değişince yeniden derleme gerekmez).

Işınlar `dunya.isin`'in altyapısıyla aynı: `mujoco.mj_multiRay`, sahne grubu 0 (duvar / kutu / kolon / zemin). Robotun
çarpışma kutusu (`c_govde`, grup 3) LiDAR'ı içine aldığı için kullanılamaz; robotun kendi gövdesi için CAD'den gelen görsel
ağlar (grup 1) kullanılır (`govde_carpma_analizi`, `oz_govde`).

    %V% kod\\fizik\\lidar.py dogrula            # analitik / gürültü / kör sektör / menzil / dönen tarama / süre
    %V% kod\\fizik\\lidar.py govde              # robotun kendi gövdesine çarpan ışınlar, özellik dosyasıyla fark
    %V% kod\\fizik\\lidar.py gorsel [sahne..]   # kod/fizik/sahneler/gorsel/lidar_<sahne>.png (çizim py -3 + matplotlib)
    %V% kod\\fizik\\lidar.py kayit --sahne koridor_1 --sure 20 --v 0.25 --cikti x.npz   # başsız örnek deney kaydı
"""

import dataclasses
import json
import math
import os
import sys
import time

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(BURASI)
KOK = os.path.dirname(KOD)
for _y in (os.path.join(KOD, "ortak"), os.path.join(KOD, "pi"), os.path.join(KOD, "araclar"), BURASI):
    if _y not in sys.path:
        sys.path.insert(0, _y)

import dunya as D  # noqa: E402

OZELLIK_DOSYASI = os.path.join(BURASI, "lidar_ozellik.json")
GORSEL = os.path.join(BURASI, "sahneler", "gorsel")
KORIDORLAR = ["koridor_%d" % i for i in range(1, 7)]
KAYIT_SURUMU = 1


def ozellik_oku(yol=None):
    with open(yol or OZELLIK_DOSYASI, encoding="utf-8") as f:
        return json.load(f)


def _aci_sar(a):
    """(-pi, pi] aralığına."""
    return np.arctan2(np.sin(a), np.cos(a))


def kor_mu(acilar_rad, sektorler_derece, pay_derece=0.0):
    """Açı (gövde çerçevesi) kör sektörde mi. Sektör [bas, bit] saat yönünün tersine bas -> bit (konumlama ile aynı)."""
    d = np.degrees(np.asarray(acilar_rad, dtype=float))
    kor = np.zeros(d.shape, dtype=bool)
    for bas, bit in sektorler_derece:
        b, e = bas - pay_derece, bit + pay_derece
        kor |= ((d - b) % 360.0) <= ((e - b) % 360.0)
    return kor


@dataclasses.dataclass
class LidarAyar:
    """Sensör ayarları. İlk grup özellik dosyasından gelir (`dosyadan`); ikinci grup VARSAYIM / TAHMİN parametreler.

    Her gerçekçilik etkisi tek tek kapatılabilir: gurultu_sigma_m 0, cozunurluk_m 0, gecersiz_oran 0, kor_maske False,
    donen False (anlık tarama), menzil sınırları için menzil_min_m 0 / menzil_maks_m inf."""
    # --- lidar_ozellik.json
    menzil_min_m: float = 0.05
    menzil_maks_m: float = 12.0
    isin_sayisi: int = 500                 # round(360 / acisal_cozunurluk_derece)
    tarama_hz: float = 10.0
    montaj_x_m: float = 0.19
    montaj_y_m: float = 0.0
    montaj_z_m: float = 0.295
    montaj_yaw_rad: float = 0.0
    kor_sektorler_derece: tuple = ((139.2, 220.8),)
    cozunurluk_m: float = 0.015            # VARSAYIM: veri sayfasının "15 mm çözünürlük"ü çıktının 15 mm'ye yuvarlanması sayıldı
    gecersiz_oran: float = 0.0             # dosyada null (ölçülmedi) -> 0
    # --- VARSAYIM / TAHMİN (dosyada değer yok)
    gurultu_sigma_m: float = 0.010         # VARSAYIM: veri sayfası yalnız ±30 mm sınır veriyor; Gauss, 3 sigma = 30 mm
    kor_pay_derece: float = 5.0            # dosyanın kör sektör açıklamasındaki yazılım maskesi önerisi (her yana +5 -> [134, 226])
    kor_maske: bool = True
    donen: bool = True                     # False: tur başında 500 ışın aynı anda (karşılaştırma için "anlık tarama")
    donus_yonu: str = "saat"               # TAHMİN (dosya `aci_yonu_notu`): ham açı saat yönünde artar, ışınlar o sırayla
    tur_baslangic_derece: float = 0.0      # TAHMİN: turun ilk ışını sensörün 0 derecesinde (gerçek 0 yönü ölçülmedi)
    duzlem_egimi_derece: float = 0.0       # tarama düzleminin öne eğimi (+ = ön aşağı); dosyada aralık [0, 1,5], VARSAYIM 0
    oz_govde: bool = False                 # True: ışınlar robotun kendi görsel ağına da çarpar (maskesiz denemede görünür)
    tohum: object = None                   # numpy Generator tohumu (None = rastgele)
    kaynak: str = ""

    @classmethod
    def dosyadan(cls, yol=None, **degis):
        o = ozellik_oku(yol)
        m = o["montaj"]
        g = o.get("mesafe_gurultu") or {}
        n = int(round(o["gorus_acisi_derece"] / o["acisal_cozunurluk_derece"]))
        if o.get("ornek_hz") and abs(o["ornek_hz"] / o["tarama_hz"] - n) > 1:
            print("UYARI lidar_ozellik: ornek_hz / tarama_hz = %.1f, 360 / cozunurluk = %d" % (o["ornek_hz"] / o["tarama_hz"], n))
        a = cls(menzil_min_m=float(o["menzil_min_m"]), menzil_maks_m=float(o["menzil_maks_m"]), isin_sayisi=n,
                tarama_hz=float(o["tarama_hz"]), montaj_x_m=float(m["x_m"]), montaj_y_m=float(m["y_m"]),
                montaj_z_m=float(m["z_m"]), montaj_yaw_rad=math.radians(float(m.get("yaw_derece", 0.0))),
                kor_sektorler_derece=tuple(tuple(map(float, s)) for s in (o.get("kor_sektorler_derece") or [])),
                cozunurluk_m=float(g.get("cozunurluk_m") or 0.0),
                gecersiz_oran=float(o["gecersiz_olcum_orani"]) if o.get("gecersiz_olcum_orani") is not None else 0.0,
                kaynak=os.path.relpath(yol or OZELLIK_DOSYASI, KOK))
        return dataclasses.replace(a, **degis) if degis else a

    def sozluk(self):
        s = dataclasses.asdict(self)
        s["kor_sektorler_derece"] = [list(x) for x in self.kor_sektorler_derece]
        return s


class SanalLidar:
    """Dönen 2B LiDAR. Kullanım:

        lid = SanalLidar(dunya, gurultu_sigma_m=0.01, tohum=1)   # ayarlar: LidarAyar alanları
        lid.bagla()                       # her fizik adımında ışın dilimi atar (dunya.adim_kaydi zincirine)
        lid.dinleyiciler.append(f)        # f(tarama_sozlugu, ek): her tur bitince
        lid.son_tarama                    # sözleşme sözlüğü
        lid.anlik_tarama()                # şu anki pozdan 500 ışın birden (bağlamadan da)

    `bagla()` dunya.adim_kaydi'na o anda atanmış işlevi zincirler; adim_kaydi sonradan başka işleve atanırsa LiDAR
    kopar (önce öbür kancaları kur, sonra bagla)."""

    def __init__(self, dunya, ayar=None, **degis):
        self.w = dunya
        self.ayar = ayar if ayar is not None else LidarAyar.dosyadan()
        if degis:
            self.ayar = dataclasses.replace(self.ayar, **degis)
        a = self.ayar
        if a.donus_yonu not in ("saat", "ters"):
            raise ValueError("donus_yonu 'saat' ya da 'ters' olmalı: %r" % (a.donus_yonu,))
        N = self.N = int(a.isin_sayisi)
        self.donem_s = 1.0 / a.tarama_hz
        self.isin_araligi_s = self.donem_s / N
        self.montaj = (a.montaj_x_m, a.montaj_y_m, a.montaj_z_m, a.montaj_yaw_rad)
        self._montaj_p = np.array((a.montaj_x_m, a.montaj_y_m, a.montaj_z_m))
        # sensör çerçevesi açı ızgarası (-pi'den, artan); gövde açısı = sensör açısı + montaj yaw'u
        dlt = 2 * math.pi / N
        sensor = -math.pi + np.arange(N) * dlt
        govde = _aci_sar(sensor + a.montaj_yaw_rad)
        if a.montaj_yaw_rad == 0.0:
            govde = sensor.copy()                       # tam ızgara (-pi dahil), konumlama ile bit düzeyinde aynı
        sira = np.argsort(govde, kind="stable")
        self.acilar = govde[sira]                       # çıktı sırası (artan gövde açısı)
        self._acilar_liste = self.acilar.tolist()
        sensor_cikti = sensor[sira]
        cikti_of_sensor = np.empty(N, dtype=int)
        cikti_of_sensor[sira] = np.arange(N)
        j0 = int(round((math.radians(a.tur_baslangic_derece) + math.pi) / dlt)) % N
        adim = -1 if a.donus_yonu == "saat" else 1
        self.zaman_sirasi = cikti_of_sensor[(j0 + adim * np.arange(N)) % N]   # k. ışının çıktı indisi
        self.zaman_ofseti = np.empty(N)
        self.zaman_ofseti[self.zaman_sirasi] = np.arange(N) * self.isin_araligi_s
        # gövde çerçevesinde ışın yönleri (düzlem eğimi: sensörün y ekseni çevresinde, + = ön aşağı)
        eg = math.radians(a.duzlem_egimi_derece)
        yerel = np.stack([np.cos(sensor_cikti) * math.cos(eg), np.sin(sensor_cikti), -np.cos(sensor_cikti) * math.sin(eg)], 1)
        cy, sy = math.cos(a.montaj_yaw_rad), math.sin(a.montaj_yaw_rad)
        self._yon_govde = yerel @ np.array([[cy, -sy, 0.0], [sy, cy, 0.0], [0.0, 0.0, 1.0]]).T
        self.kor = kor_mu(self.acilar, a.kor_sektorler_derece, a.kor_pay_derece) if a.kor_maske else np.zeros(N, bool)
        self._grup = np.array([1, 1 if a.oz_govde else 0, 0, 0, 0, 0], dtype=np.uint8)
        self._kesme = (a.menzil_maks_m if math.isfinite(a.menzil_maks_m) else 1e3) + 1.0
        self.rng = np.random.default_rng(a.tohum)
        self._gid = np.zeros(N, dtype=np.int32)
        self._mesafe = np.zeros(N)
        self.dinleyiciler = []
        self.son_tarama = None
        self.son_ek = None
        self.tarama_sayisi = 0
        self._bagli = None
        self._sifirla_tur()

    # ------------------------------------------------------------ geometri
    def koken_ve_eksen(self):
        """(LiDAR merkezinin dünya konumu (3,), taban dönüş matrisi (3, 3)) - MuJoCo'nun son kinematiğinden."""
        d = self.w.d
        R = d.xmat[self.w.taban].reshape(3, 3)
        return d.xpos[self.w.taban] + R @ self._montaj_p, R

    def _isinla(self, koken, R, idx):
        """idx (çıktı indisleri) ışınları için gerçek mesafe (NaN = çarpma yok) ve dünya yönleri."""
        n = len(idx)
        yon = self._yon_govde[idx] @ R.T
        gid, mes = self._gid[:n], self._mesafe[:n]
        D.mujoco.mj_multiRay(self.w.m, self.w.d, np.ascontiguousarray(koken, dtype=float), np.ascontiguousarray(yon).ravel(),
                             self._grup, 1, -1, gid, mes, None, n, self._kesme)
        g = mes.copy()
        g[g < 0] = np.nan
        return g, yon

    def _isle(self, gercek):
        """Gerçek mesafeden ölçüm: menzil, geçersiz oran, gürültü, çözünürlük, kör sektör. RNG her turda aynı sayıda
        çekilir (maske / menzil sonucu değiştirmez): aynı tohum -> aynı dizi."""
        a = self.ayar
        N = len(gercek)
        m = gercek.copy()
        gecersiz = ~np.isfinite(m) | (m < a.menzil_min_m) | (m > a.menzil_maks_m)
        if a.gecersiz_oran > 0:
            gecersiz |= self.rng.random(N) < a.gecersiz_oran
        if a.gurultu_sigma_m > 0:
            m = m + self.rng.normal(0.0, a.gurultu_sigma_m, N)
        if a.cozunurluk_m > 0:
            m = np.round(m / a.cozunurluk_m) * a.cozunurluk_m
        gecersiz |= self.kor
        m[gecersiz] = np.nan
        return m

    def _poz(self):
        x, y, _, yaw, _, _ = self.w.poz()
        return (x, y, yaw)

    def _tarama_bitir(self, t, gercek, koken, yon, poz_bas, poz_son):
        olcum = self._isle(gercek)
        tarama = {"t": float(t), "acilar": list(self._acilar_liste), "mesafeler": olcum.tolist()}
        ek = TaramaEk(t=float(t), acilar=self.acilar, mesafeler=olcum, gercek=gercek, koken=koken, yon=yon,
                      poz_bas=poz_bas, poz_son=poz_son, donen=self.ayar.donen)
        self.son_tarama, self.son_ek = tarama, ek
        self.tarama_sayisi += 1
        for f in list(self.dinleyiciler):
            f(tarama, ek)
        return tarama

    def anlik_tarama(self, t=None):
        """Şu anki pozdan bütün ışınlar aynı anda. t verilmezse kinematiğin zamanı (dunya.zaman_s)."""
        koken, R = self.koken_ve_eksen()
        idx = np.arange(self.N)
        g, yon = self._isinla(koken, R, idx)
        p = self._poz()
        return self._tarama_bitir(self.w.zaman_s if t is None else t, g, np.repeat(koken[None, :], self.N, 0), yon, p, p)

    # ------------------------------------------------------------ dönen tarama (fizik adımına bağlı)
    def _sifirla_tur(self):
        self._t0 = None          # ilk ışının zamanı (bağlandıktan sonraki ilk adım)
        self._k = 0              # atılmış ışın sayısı (toplam)
        self._adim_say = 0
        self._ham = np.full(self.N, np.nan)
        self._koken_buf = np.zeros((self.N, 3))
        self._yon_buf = np.zeros((self.N, 3))
        self._poz_bas = None

    def bagla(self):
        if self._bagli is not None:
            return
        onceki = self.w.adim_kaydi

        def kanca(w):
            if onceki is not None:
                onceki(w)
            self._adim(w)
        self._bagli = (onceki, kanca)
        self.w.adim_kaydi = kanca
        self._sifirla_tur()

    def ayir(self):
        if self._bagli is None:
            return
        onceki, kanca = self._bagli
        if self.w.adim_kaydi is kanca:
            self.w.adim_kaydi = onceki
        self._bagli = None

    def _adim(self, w):
        dt = w.m.opt.timestep
        t_kin = w.zaman_s - dt                   # mj_step sonrası xpos adımın başındaki durumu gösterir
        if self._t0 is None:
            self._t0 = t_kin
        self._adim_say += 1
        hedef = int(math.floor(self._adim_say * dt / self.isin_araligi_s + 1e-6))   # bu adımın sonuna dek atılacak
        N = self.N
        while self._k < hedef:
            tur, k_tur = divmod(self._k, N)
            t_tur = self._t0 + tur * self.donem_s
            if not self.ayar.donen:              # anlık: tur başında 500 ışın birden, turun kalanı bekler
                if k_tur == 0:
                    self.anlik_tarama(t_tur)
                self._k = min(hedef, (tur + 1) * N)
                continue
            son = min(hedef, (tur + 1) * N)
            idx = self.zaman_sirasi[k_tur:son - tur * N]
            koken, R = self.koken_ve_eksen()
            if k_tur == 0:
                self._poz_bas = self._poz()
            g, yon = self._isinla(koken, R, idx)
            self._ham[idx] = g
            self._koken_buf[idx] = koken
            self._yon_buf[idx] = yon
            self._k = son
            if son == (tur + 1) * N:
                self._tarama_bitir(t_tur, self._ham.copy(), self._koken_buf.copy(), self._yon_buf.copy(),
                                   self._poz_bas, self._poz())
                self._ham[:] = np.nan


@dataclasses.dataclass
class TaramaEk:
    """Sözleşmenin dışında kalan tarama ayrıntıları (numpy): gerçek mesafe, ışınların dünya kökeni / yönü, pozlar."""
    t: float
    acilar: np.ndarray
    mesafeler: np.ndarray       # ölçülen (NaN = yok)
    gercek: np.ndarray          # gürültüsüz, maskesiz MuJoCo mesafesi (NaN = çarpma yok)
    koken: np.ndarray           # (N, 3) her ışının atıldığı andaki LiDAR merkezi (dünya)
    yon: np.ndarray             # (N, 3) dünya yönü
    poz_bas: tuple              # (x, y, yaw) taban, ilk ışın
    poz_son: tuple              # (x, y, yaw) taban, son ışın
    donen: bool

    def noktalar(self, olculen=True):
        """Dünya çerçevesinde isabet noktaları (N, 3); ölçüm yoksa NaN."""
        m = self.mesafeler if olculen else self.gercek
        return self.koken + self.yon * m[:, None]


# ------------------------------------------------------------------ robotun kendi gövdesi
def govde_carpma_analizi(dunya, ayar=None, adim_derece=0.1, egimler_derece=(0.0,), menzil_m=2.0):
    """LiDAR merkezinden robotun KENDİ görsel ağlarına (CAD, grup 1; sahne hariç) ışın: hangi gövde açılarında çarpıyor.

    Döner: {egim: [{"bas": derece, "bit": derece, "en_yakin_m": m, "govdeler": [...]}, ...]} (açılar gövde çerçevesi,
    -180..180 yerine 0..360; bitişik aralık birleşir)."""
    mj = D.mujoco
    a = ayar or LidarAyar.dosyadan()
    m, d = dunya.m, dunya.d
    R = d.xmat[dunya.taban].reshape(3, 3)
    koken = d.xpos[dunya.taban] + R @ np.array([a.montaj_x_m, a.montaj_y_m, a.montaj_z_m])
    n = int(round(360.0 / adim_derece))
    aci = np.arange(n) * math.radians(adim_derece)
    sonuc = {}
    for egim in egimler_derece:
        e = math.radians(egim)
        s = aci - a.montaj_yaw_rad
        yerel = np.stack([np.cos(s) * math.cos(e), np.sin(s), -np.cos(s) * math.sin(e)], 1)
        cy, sy = math.cos(a.montaj_yaw_rad), math.sin(a.montaj_yaw_rad)
        yon = yerel @ np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]]).T @ R.T
        gid = np.zeros(n, np.int32)
        mes = np.zeros(n)
        mj.mj_multiRay(m, d, koken, np.ascontiguousarray(yon).ravel(), np.array([0, 1, 0, 0, 0, 0], np.uint8), 0, -1,
                       gid, mes, None, n, menzil_m)
        vur = mes >= 0
        araliklar = []
        i = 0
        while i < n:
            if not vur[i]:
                i += 1
                continue
            j = i
            while j + 1 < n and vur[j + 1]:
                j += 1
            gov = sorted({mj.mj_id2name(m, mj.mjtObj.mjOBJ_BODY, int(m.geom_bodyid[g])) or str(g) for g in gid[i:j + 1]})
            araliklar.append({"bas": round(float(np.degrees(aci[i])), 3), "bit": round(float(np.degrees(aci[j])), 3),
                              "en_yakin_m": round(float(mes[i:j + 1].min()), 4), "govdeler": gov})
            i = j + 1
        if len(araliklar) > 1 and araliklar[0]["bas"] == 0.0 and vur[-1]:     # 0 dereceden geçen aralığı birleştir
            ilk = araliklar.pop(0)
            araliklar[-1]["bit"] = ilk["bit"] + 360.0
            araliklar[-1]["en_yakin_m"] = min(araliklar[-1]["en_yakin_m"], ilk["en_yakin_m"])
        sonuc[egim] = araliklar
    return sonuc


# ------------------------------------------------------------------ deney kaydı
class DeneyKaydi:
    """Deney kaydı: yer gerçeği, enkoder odometrisi, taramalar; `kaydet(yol)` tek .npz.

    Zaman satırları sahte ESP32'nin 10 ms diliminde (`FizikEsp32.kayitci` zincirine). Odometri Pi'nin yapacağı gibi tik
    toplamlarından (`c.tik`), firmware / Pi sabitleriyle: tik yolu = pi x teker_capi / tik_tur, iz = firmware_iz_genisligi_m
    (0,426; CAD izi 0,432, `SIMULASYON.md` bulgu (e)); başlangıç pozu yer gerçeğinin başlangıcı. Protokolün `odo` mesajı
    10 Hz'tir; burada 100 Hz yazılır (seyrelt). Kayıt sırasında `odo_sifirla` gelirse sıfırlanan tik farkı atlanır."""

    def __init__(self, esp, lidar, sahne=None, not_=None):
        self.c, self.lidar, self.sahne, self.not_ = esp, lidar, sahne, not_
        self.tik_m = math.pi * esp.teker_capi / esp.tik_tur
        self.iz = esp.fw_iz
        x, y, yaw = lidar._poz()
        self.odo = [x, y, yaw]
        self._tik = list(esp.tik)
        self.satir = []          # t, ms, x, y, yaw, odo_x, odo_y, odo_yaw, tik_sol, tik_sag, v, w
        self.tarama = []         # (t, mesafeler, gercek_bas, gercek_son, odo)
        onceki = esp.kayitci

        def kanca(c):
            if onceki is not None:
                onceki(c)
            self._dilim()
        self._kanca = (onceki, kanca)
        esp.kayitci = kanca
        lidar.dinleyiciler.append(self._tarama)
        self._dilim()

    def _dilim(self):
        c, w = self.c, self.c.dunya
        t = w.zaman_s - w.m.opt.timestep
        tik = list(c.tik)
        if tik == [0, 0] and self._tik != [0, 0]:
            self._tik = tik                       # odo_sifirla
        dl = (tik[0] - self._tik[0]) * self.tik_m
        dr = (tik[1] - self._tik[1]) * self.tik_m
        self._tik = tik
        ds, dth = (dl + dr) / 2.0, (dr - dl) / self.iz
        o = self.odo
        o[0] += ds * math.cos(o[2] + dth / 2.0)
        o[1] += ds * math.sin(o[2] + dth / 2.0)
        o[2] = math.atan2(math.sin(o[2] + dth), math.cos(o[2] + dth))
        x, y, _, yaw, _, _ = w.poz()
        v, wz = w.hiz()
        self.satir.append((t, c.ms, x, y, yaw, o[0], o[1], o[2], tik[0], tik[1], v, wz))

    def _tarama(self, tarama, ek):
        self.tarama.append((ek.t, ek.mesafeler.copy(), ek.poz_bas, ek.poz_son, tuple(self.odo)))

    def birak(self):
        onceki, kanca = self._kanca
        if self.c.kayitci is kanca:
            self.c.kayitci = onceki
        if self._tarama in self.lidar.dinleyiciler:
            self.lidar.dinleyiciler.remove(self._tarama)

    def diziler(self):
        S = np.array(self.satir, dtype=float).reshape(-1, 12)
        N = self.lidar.N
        T = self.tarama
        return {
            "t": S[:, 0], "ms": S[:, 1].astype(np.int64), "gercek": S[:, 2:5], "odo": S[:, 5:8],
            "tik": S[:, 8:10].astype(np.int64), "hiz": S[:, 10:12],
            "acilar": self.lidar.acilar.copy(), "zaman_ofseti": self.lidar.zaman_ofseti.copy(),
            "tarama_t": np.array([x[0] for x in T], dtype=float),
            "mesafeler": np.array([x[1] for x in T], dtype=float).reshape(-1, N),
            "tarama_gercek": np.array([x[2] for x in T], dtype=float).reshape(-1, 3),
            "tarama_gercek_son": np.array([x[3] for x in T], dtype=float).reshape(-1, 3),
            "tarama_odo": np.array([x[4] for x in T], dtype=float).reshape(-1, 3),
            "montaj": np.array(self.lidar.montaj, dtype=float),
        }

    def kaydet(self, yol):
        dz = self.diziler()
        meta = {"surum": KAYIT_SURUMU, "sahne": self.sahne, "not": self.not_, "lidar": self.lidar.ayar.sozluk(),
                "odometri": {"tik_m": self.tik_m, "iz_m": self.iz, "kaynak": "c.tik, 10 ms dilim"},
                "cerceve": "dunya x, y = harita (m); yaw rad; acilar govde cercevesi (0 ileri, saat yonu tersi +); "
                           "mesafe LiDAR merkezinden, NaN = olcum yok; montaj = (x, y, z m, yaw rad) govdede",
                "zaman": "dunya.zaman_s (s); tarama_t ilk isinin zamani; isin i zamani = tarama_t + zaman_ofseti[i]; "
                         "gercek / odo satirlari 10 ms; tarama_gercek = ilk isindaki taban pozu, tarama_gercek_son = son isin; "
                         "tarama_odo = tur bitince son odometri",
                "alanlar": {"gercek": "x, y, yaw (taban; yer gercegi)", "odo": "x, y, yaw (enkoder odometrisi)",
                            "tik": "sol, sag toplam tik", "hiz": "v m/s, w rad/s (yer gercegi)",
                            "mesafeler": "(tarama, isin)"}}
        os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
        np.savez_compressed(yol, meta=np.array(json.dumps(meta, ensure_ascii=False)), **dz)
        return yol


def kayit_oku(yol):
    """npz kaydı -> (meta sözlüğü, diziler sözlüğü). `taramalar(kayit)` sözleşme sözlüklerini verir."""
    with np.load(yol, allow_pickle=False) as z:
        dz = {k: z[k] for k in z.files}
    meta = json.loads(str(dz.pop("meta")))
    return meta, dz


def taramalar(dz):
    acilar = dz["acilar"].tolist()
    for t, m in zip(dz["tarama_t"], dz["mesafeler"]):
        yield {"t": float(t), "acilar": list(acilar), "mesafeler": m.tolist()}


class LidarDeneyi:
    """Başsız deney düzeneği: sahne + sahte ESP32 (fizik) + Pi istemcisi (bellek taşıması) + LiDAR + kayıt.
    3B pencerenin kurulumuyla aynı (`gorunum3b.Pencere`), görüntüleyici açılmaz.

        dn = LidarDeneyi("koridor_5", tohum=3)        # LidarAyar alanları anahtar sözcük olarak
        dn.devreye_al(); dn.e.sur_tut(0.25, 0.0, 10000); dn.e.istek({"k": "dur"}); dn.e.bekle(800)
        dn.kayit.kaydet("deney.npz")
    """

    def __init__(self, sahne_ad, konum=None, varyant=None, sonar_acik=True, degis=None, kayit=True, **lidar_ayar):
        from fizik_esp32 import FizikEsp32
        from sahte_esp32.harita import Harita
        from sahte_esp32.tasima import BellekTasima
        from lale_pi.istemci import Esp32Istemci
        self.sahne_ad = sahne_ad
        self.sahne = D.sahne_oku(sahne_ad)
        self.harita = Harita.dosyadan(os.path.join(KOD, "araclar", "haritalar", self.sahne["harita"] + ".json"))
        if konum is None:
            b = self.sahne.get("baslangic", self.harita.veri.get("baslangic"))
            konum = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
        self.c = FizikEsp32(self.harita, konum=konum, sahne=self.sahne, degis=degis, varyant=varyant, sonar_acik=sonar_acik)
        self.w = self.c.dunya
        self.e = Esp32Istemci(BellekTasima(self.c))
        self.e.baglan()
        self.lidar = SanalLidar(self.w, **lidar_ayar)
        self.lidar.bagla()
        self.kayit = DeneyKaydi(self.c, self.lidar, sahne=sahne_ad) if kayit else None

    def devreye_al(self):
        o = self.e.devreye_al_ve_bekle()
        assert o.get("guc") == "devrede", o


# ------------------------------------------------------------------ komutlar
def _yazdir(s):
    print(s, flush=True)


def _dunya(sahne_ad, konum=None):
    from sahte_esp32.harita import Harita
    s = D.sahne_oku(sahne_ad)
    h = Harita.dosyadan(os.path.join(KOD, "araclar", "haritalar", s["harita"] + ".json"))
    if konum is None:
        b = s["baslangic"]
        konum = (float(b["x"]), float(b["y"]), math.radians(float(b.get("aci_derece", 0))))
    return D.FizikDunya(h, s, konum), s, h


def komut_govde():
    o = ozellik_oku()
    w = D.FizikDunya(None, None, (0, 0, 0))
    w.adim(0.3)
    sonuc = govde_carpma_analizi(w, egimler_derece=(0.0, 1.5, -1.5))
    kor = o["kor_sektorler_derece"]
    _yazdir("Robotun kendi gövdesi (görsel CAD ağları, ev pozu), LiDAR (%.3f, %.3f, %.3f) m, 0,1 derece adım:"
            % (o["montaj"]["x_m"], o["montaj"]["y_m"], o["montaj"]["z_m"]))
    for egim, ar in sonuc.items():
        for r in ar:
            _yazdir("  eğim %+.1f der: %.1f - %.1f der (%.1f der), en yakın %.3f m, gövde %s"
                    % (egim, r["bas"], r["bit"], r["bit"] - r["bas"], r["en_yakin_m"], ",".join(r["govdeler"])))
    if sonuc[0.0]:
        r = sonuc[0.0][0]
        for b, e in kor:
            _yazdir("  özellik dosyası kör sektörü %.1f - %.1f: ölçülen başlangıç %+.1f, bitiş %+.1f der fark (+ = ölçülen dar)"
                    % (b, e, r["bas"] - b, e - r["bit"]))
    return sonuc


def _istatistik(x):
    x = np.asarray(x, dtype=float)
    return float(np.nanmean(x)), float(np.nanstd(x))


def komut_dogrula(sessiz=False):
    """Zorunlu doğrulamalar; sonuç sözlüğü döner, yazdırır."""
    out = {}
    say = (lambda s: None) if sessiz else _yazdir
    o = ozellik_oku()
    w, s, h = _dunya("koridor_1")
    w.adim(0.3)
    x, y, _, yaw, _, _ = w.poz()
    kal = w.p["ic_duvar_kalinligi_m"]
    # 1) analitik: koridor_1 duvarları y 5,0 / 7,0 (iç duvar levhası 2 mm, çizgiye ortalı -> yüz 1 mm içeride)
    lid = SanalLidar(w, gurultu_sigma_m=0.0, cozunurluk_m=0.0, kor_maske=False)
    koken, _ = lid.koken_ve_eksen()
    t = lid.anlik_tarama()
    m = np.array(t["mesafeler"])
    i_sol = int(np.argmin(np.abs(lid.acilar - math.pi / 2)))
    i_sag = int(np.argmin(np.abs(lid.acilar + math.pi / 2)))
    i_on = int(np.argmin(np.abs(lid.acilar)))
    bek_sol = (7.0 - kal / 2) - koken[1]
    bek_sag = koken[1] - (5.0 + kal / 2)
    # sola tam dik ışının çarptığı yerde kapı girintisi yoksa duvar 7,0'da; koken x'te üst duvarda kapı var mı bak
    out["analitik"] = dict(koken=koken.tolist(), poz=(x, y, math.degrees(yaw)), sol=float(m[i_sol]), sol_beklenen=bek_sol,
                           sag=float(m[i_sag]), sag_beklenen=bek_sag, sol_hata_mm=1000 * (m[i_sol] - bek_sol),
                           sag_hata_mm=1000 * (m[i_sag] - bek_sag), on=float(m[i_on]))
    a = out["analitik"]
    say("1) analitik, koridor_1 orta hat (taban x %.4f y %.4f yaw %.3f der), LiDAR merkezi (%.4f, %.4f, %.4f):"
        % (x, y, math.degrees(yaw), *koken))
    say("   sol (+90) %.4f m, beklenen %.4f (hata %+.3f mm); sağ (-90) %.4f, beklenen %.4f (hata %+.3f mm); gürültü / çözünürlük kapalı"
        % (a["sol"], bek_sol, a["sol_hata_mm"], a["sag"], bek_sag, a["sag_hata_mm"]))
    # ön uç duvar: x = 31,0 (koridor 1,0 + 30); 12 m ötede -> NaN
    say("   ön (0 der): %s (uç duvar x 31,0'da, LiDAR'dan %.2f m > 12 m: NaN beklenir)"
        % ("NaN" if not np.isfinite(m[i_on]) else "%.3f m" % m[i_on], 31.0 - kal / 2 - koken[0]))
    out["analitik"]["on_uzaklik_m"] = 31.0 - kal / 2 - koken[0]
    # çözünürlük açık, gürültü kapalı: hata <= 7,5 mm
    lid_c = SanalLidar(w, gurultu_sigma_m=0.0, kor_maske=False)
    mc = np.array(lid_c.anlik_tarama()["mesafeler"])
    out["cozunurluk"] = dict(sol=float(mc[i_sol]), sag=float(mc[i_sag]), sol_hata_mm=1000 * (mc[i_sol] - bek_sol),
                             sag_hata_mm=1000 * (mc[i_sag] - bek_sag))
    say("   15 mm yuvarlama açık: sol %.3f (%+.1f mm), sağ %.3f (%+.1f mm); sınır ±7,5 mm"
        % (mc[i_sol], out["cozunurluk"]["sol_hata_mm"], mc[i_sag], out["cozunurluk"]["sag_hata_mm"]))
    # 2) gürültü: 2000 tekrar, sigma 10 mm, çözünürlük kapalı ve açık
    for coz in (0.0, LidarAyar.dosyadan().cozunurluk_m):
        lg = SanalLidar(w, cozunurluk_m=coz, tohum=7)
        olc = np.array([lg.anlik_tarama()["mesafeler"][i_sol] for _ in range(2000)])
        ort, ss = _istatistik(olc)
        out["gurultu_coz_%g" % coz] = dict(ort_hata_mm=1000 * (ort - bek_sol), std_mm=1000 * ss,
                                          en_cok_mm=1000 * float(np.nanmax(np.abs(olc - bek_sol))))
        g = out["gurultu_coz_%g" % coz]
        say("2) gürültü sigma %.0f mm, çözünürlük %.0f mm, 2000 tekrar sol duvar: ortalama hata %+.2f mm, std %.2f mm, en büyük |hata| %.1f mm"
            % (lg.ayar.gurultu_sigma_m * 1000, coz * 1000, g["ort_hata_mm"], g["std_mm"], g["en_cok_mm"]))
    # tohum: aynı tohum aynı dizi
    t1 = SanalLidar(w, tohum=11).anlik_tarama()["mesafeler"]
    t2 = SanalLidar(w, tohum=11).anlik_tarama()["mesafeler"]
    out["tohum_ayni"] = bool(np.array_equal(np.array(t1), np.array(t2), equal_nan=True))
    say("   aynı tohum aynı tarama: %s" % out["tohum_ayni"])
    # 3) kör sektör ve menzil
    lk = SanalLidar(w, gurultu_sigma_m=0.0)
    mk = np.array(lk.anlik_tarama()["mesafeler"])
    d = np.degrees(lk.acilar) % 360.0
    icerde = (d >= 134.0 - 1e-9) & (d <= 226.0 + 1e-9)
    out["kor"] = dict(maske_isin=int(lk.kor.sum()), maske_ici_nan=int(np.isnan(mk[icerde]).sum()), maske_ici=int(icerde.sum()),
                      maske_disi_nan=int(np.isnan(mk[~icerde]).sum()))
    k_ = out["kor"]
    say("3) kör sektör (öneri maskesi [134, 226]): %d ışın maskeli, maske içinde NaN %d / %d; maske dışında NaN %d (uzak uç duvar)"
        % (k_["maske_isin"], k_["maske_ici_nan"], k_["maske_ici"], k_["maske_disi_nan"]))
    lk2 = SanalLidar(w, gurultu_sigma_m=0.0, kor_pay_derece=0.0)
    out["kor"]["pay0_isin"] = int(lk2.kor.sum())
    say("   pay 0 (dosyadaki [139,2, 220,8]): %d ışın maskeli" % lk2.kor.sum())
    # menzil: ön yöndeki ışınlar (uç duvar 29 m) NaN, maske dışı NaN'ların gerçek mesafesi > 12 m mi
    ek = lk.son_ek
    nan_disi = (~icerde) & np.isnan(mk)
    out["menzil"] = dict(nan_gercek_min_m=float(np.nanmin(ek.gercek[nan_disi])) if nan_disi.any() else None,
                         olculen_maks_m=float(np.nanmax(mk)))
    say("   menzil: maske dışındaki NaN ışınların gerçek mesafesi en az %.2f m (> 12); ölçülen en uzak %.3f m"
        % (out["menzil"]["nan_gercek_min_m"], out["menzil"]["olculen_maks_m"]))
    # alt sınır: LiDAR'ı alt duvara (y 5,0; x 1,0-2,6 kapısız) 4 cm yaklaştır, robot -y'ye bakar (gövde duvarla
    # çakışır: yalnız kinematik, fizik adımı atılmaz)
    w2, _, _ = _dunya("koridor_1", konum=(2.0, 5.0 + kal / 2 + 0.04 + o["montaj"]["x_m"], -math.pi / 2))
    l2 = SanalLidar(w2, gurultu_sigma_m=0.0, cozunurluk_m=0.0)
    m2 = np.array(l2.anlik_tarama()["mesafeler"])
    out["menzil"]["yakin_gercek_m"] = float(l2.son_ek.gercek[i_on])
    out["menzil"]["yakin_olcum"] = None if not np.isfinite(m2[i_on]) else float(m2[i_on])
    say("   alt sınır: duvar 0,040 m önde -> gerçek %.4f m, ölçüm %s (0,05 m altı NaN)"
        % (out["menzil"]["yakin_gercek_m"], "NaN" if out["menzil"]["yakin_olcum"] is None else out["menzil"]["yakin_olcum"]))
    # 4) dönen tarama: robot sabit hızla ilerlerken (protokolle sür) anlık ile fark
    out["donen"] = donen_karsilastir(say)
    # 5) süre
    out["sure"] = sure_olc(say)
    return out


def donen_karsilastir(say=_yazdir, v=0.39, sahne="koridor_1", t_tur=3.0):
    """Robot koridorda düz giderken aynı tur için dönen ve anlık taramayı karşılaştır.

    Fizik belirlenimci ve LiDAR fiziğe dokunmuyor: aynı sürüş iki kez koşulur (donen True / False), aynı t'li turlar
    eşlenir; iki koşuda robotun yolu bit düzeyinde aynı. Dönen taramada ışın i, tur başından tau_i = zaman_ofseti[i] sonra,
    o anki pozdan atılır. Gürültü / yuvarlama / maske kapalı, robotun gövdesi ışında yok (arka duvar da görünür).
    Beklenen: yan duvara (x eksenine paralel) düşen ışında mesafe değişmez (yalnız nokta x'te v tau kayar); arka uç
    duvara düşen ışında robot uzaklaştığı için mesafe v tau / |cos aci| artar. Işınlar fizik adımına (1 ms) dilimlendiği
    için etkin tau adımın başıdır (beklenen hesabı da öyle)."""
    tur = {}
    for donen in (True, False):
        dn = LidarDeneyi(sahne, kayit=False, gurultu_sigma_m=0.0, cozunurluk_m=0.0, kor_maske=False, sonar_acik=False,
                         donen=donen)
        top = []
        dn.lidar.dinleyiciler.append(lambda tr, ek, top=top: top.append(ek))
        dn.devreye_al()
        dn.e.sur_tut(v, 0.0, int((t_tur + 0.5) * 1000))
        ek = min(top, key=lambda e: abs(e.t - (top[0].t + t_tur)))
        tur[donen] = (ek, dn)
    ek_d, dn = tur[True]
    ek_a = tur[False][0]
    if abs(ek_a.t - ek_d.t) > 1e-9:
        raise RuntimeError("turlar eşlenemedi: %r / %r" % (ek_d.t, ek_a.t))
    lid = dn.lidar
    dt = dn.w.m.opt.timestep
    tau = np.floor(lid.zaman_ofseti / dt + 1e-6) * dt          # ışının atıldığı adımın başı (tur başından)
    hiz = (ek_d.poz_son[0] - ek_d.poz_bas[0]) / float(tau.max())
    fark = ek_d.gercek - ek_a.gercek
    p_d = ek_d.noktalar(False)
    yan = np.isfinite(fark) & (np.abs(np.abs(p_d[:, 1] - 6.0) - 1.0) < 0.005)          # y 5,0 / 7,0 duvar yüzü
    arka = np.isfinite(fark) & (np.abs(p_d[:, 0] - 1.0) < 0.01)                        # x 1,0 uç duvar
    bek_arka = hiz * tau / np.abs(np.cos(lid.acilar))
    # yan duvarda ışınların çoğu iki taramada aynı yüzeye düşer (fark 0, nokta x'te v tau kayar); kapı kasası kenarına
    # yakın birkaç ışın ise robot ilerlediği için girintiye / duvara geçer (fark = girinti derinliği 0,09 m'ye dek)
    ayni = yan & (np.abs(fark) < 0.001)
    kayma_x = p_d[:, 0] - ek_a.noktalar(False)[:, 0]
    sonuc = dict(t=ek_d.t, v_gercek=hiz, tur_yolu_mm=1000 * (ek_d.poz_son[0] - ek_d.poz_bas[0]),
                 poz_bas_ayni=bool(np.array_equal(ek_d.poz_bas, ek_a.poz_bas)),
                 yan_isin=int(yan.sum()), yan_ayni_yuzey=int(ayni.sum()),
                 yan_ayni_fark_en_cok_mm=1000 * float(np.max(np.abs(fark[ayni]))),
                 yan_kenar_gecen=int((yan & ~ayni).sum()), yan_kenar_fark_en_cok_mm=1000 * float(np.max(np.abs(fark[yan]))),
                 yan_kayma_en_cok_mm=1000 * float(np.max(np.abs(kayma_x[ayni]))),
                 yan_kayma_sapma_en_cok_mm=1000 * float(np.max(np.abs(kayma_x[ayni] - hiz * tau[ayni]))),
                 arka_isin=int(arka.sum()), arka_fark_en_cok_mm=1000 * float(np.max(fark[arka])),
                 arka_sapma_en_cok_mm=1000 * float(np.max(np.abs(fark[arka] - bek_arka[arka]))),
                 gecerli_donen=int(np.isfinite(ek_d.gercek).sum()), gecerli_anlik=int(np.isfinite(ek_a.gercek).sum()))
    say("4) dönen / anlık (koridor_1, protokolle v %.2f m/s komut, ölçülen %.4f m/s, t %.2f s): tur boyunca %.1f mm yol; "
        "tur başı pozu iki koşuda aynı: %s" % (v, hiz, ek_d.t, sonuc["tur_yolu_mm"], sonuc["poz_bas_ayni"]))
    say("   yan duvar ışınları %d: %d'i aynı yüzeyde (mesafe farkı en çok %.3f mm, beklenen 0; isabet noktası x'te en çok %.1f mm "
        "kayık, v x tau'dan sapma en çok %.3f mm); %d'i kapı kasası kenarını geçti (fark en çok %.1f mm)"
        % (sonuc["yan_isin"], sonuc["yan_ayni_yuzey"], sonuc["yan_ayni_fark_en_cok_mm"], sonuc["yan_kayma_en_cok_mm"],
           sonuc["yan_kayma_sapma_en_cok_mm"], sonuc["yan_kenar_gecen"], sonuc["yan_kenar_fark_en_cok_mm"]))
    say("   arka uç duvar ışınları %d: mesafe dönen taramada en çok %.1f mm uzun, beklenen v x tau / |cos| ile sapma en çok %.3f mm"
        % (sonuc["arka_isin"], sonuc["arka_fark_en_cok_mm"], sonuc["arka_sapma_en_cok_mm"]))
    return sonuc


def sure_olc(say=_yazdir, sahne="koridor_4"):
    """Bir anlık tarama kaç ms; bağlı dönen LiDAR simülasyonu ne kadar yavaşlatıyor (başsız, protokolle sürüş)."""
    w, _, _ = _dunya(sahne)
    sonuc = {}
    for oz in (False, True):
        lid = SanalLidar(w, oz_govde=oz)
        lid.anlik_tarama()
        n = 200
        b = time.perf_counter()
        for _ in range(n):
            lid.anlik_tarama()
        sonuc["anlik_ms" + ("_oz_govde" if oz else "")] = 1000 * (time.perf_counter() - b) / n

    def kos(lidar_var, oz=False):
        dn = LidarDeneyi(sahne, kayit=False, oz_govde=oz) if lidar_var else None
        if dn is None:
            dn = LidarDeneyi(sahne, kayit=False)
            dn.lidar.ayir()
        dn.devreye_al()
        b = time.perf_counter()
        dn.e.sur_tut(0.25, 0.0, 5000)
        return 5.0 / (time.perf_counter() - b)
    sonuc["rtf_lidarsiz"] = kos(False)
    sonuc["rtf_lidar"] = kos(True)
    sonuc["rtf_lidar_oz_govde"] = kos(True, True)
    sonuc["yavaslama_orani"] = sonuc["rtf_lidarsiz"] / sonuc["rtf_lidar"]
    say("5) süre (%s, %d geom): anlık tarama (500 ışın) %.2f ms (oz_govde %.2f ms); başsız 5 s sürüş gerçek zamanın %.1f katı LiDAR'sız, "
        "%.1f katı dönen LiDAR'la (oz_govde %.1f): yavaşlama x%.2f"
        % (sahne, w.m.ngeom, sonuc["anlik_ms"], sonuc["anlik_ms_oz_govde"], sonuc["rtf_lidarsiz"], sonuc["rtf_lidar"],
           sonuc["rtf_lidar_oz_govde"], sonuc["yavaslama_orani"]))
    return sonuc


def komut_gorsel(adlar):
    """Her koridor: başlangıç konumunda (yerleşmeden sonra) bir dönen tarama + harita çizgileri -> lidar_<ad>.png."""
    import subprocess
    import tempfile
    veri = []
    for ad in adlar:
        dn = LidarDeneyi(ad, kayit=False, tohum=1)
        dn.e.bekle(400)                      # yerleşme + en az bir tam tur (dönen, robot duruyor)
        ek = dn.lidar.son_ek
        p = ek.noktalar()
        veri.append({"ad": ad, "harita": dn.sahne["harita"], "poz": list(ek.poz_bas), "koken": ek.koken[0].tolist(),
                     "noktalar": [[float(a), float(b)] if np.isfinite(a) else None for a, b in p[:, :2]],
                     "acilar": dn.lidar.acilar.tolist(), "kor": dn.lidar.kor.tolist(),
                     "menzil": [dn.lidar.ayar.menzil_min_m, dn.lidar.ayar.menzil_maks_m],
                     "kor_sektor": [list(x) for x in dn.lidar.ayar.kor_sektorler_derece], "kor_pay": dn.lidar.ayar.kor_pay_derece,
                     "gecerli": int(np.isfinite(ek.mesafeler).sum()), "n": dn.lidar.N,
                     "sigma_mm": dn.lidar.ayar.gurultu_sigma_m * 1000})
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(veri, f)
        yol = f.name
    try:
        try:
            import matplotlib  # noqa: F401
            return ciz(yol)
        except ImportError:                  # sanal ortamda matplotlib yok: çizim sistem Python'unda (py -3)
            komut = ["py", "-3"] if sys.platform == "win32" else ["python3"]
            return subprocess.run(komut + [os.path.abspath(__file__), "ciz", yol]).returncode
    finally:
        os.remove(yol)


def ciz(veri_yolu):
    """matplotlib ile çizim (mujoco gerekmez: `py -3 lidar.py ciz <veri.json>`)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge, Rectangle
    from sahte_esp32.harita import Harita
    with open(veri_yolu, encoding="utf-8") as f:
        veri = json.load(f)
    os.makedirs(GORSEL, exist_ok=True)
    for v in veri:
        h = Harita.dosyadan(os.path.join(KOD, "araclar", "haritalar", v["harita"] + ".json"))
        W, H = h.genislik, h.yukseklik
        fig = plt.figure(figsize=(min(16, 1.2 + W * 0.42), 1.8 + H * 0.42), dpi=130)
        ax = fig.add_axes([0.06, 0.12, 0.9, 0.76])
        for x1, y1, x2, y2 in h.parcalar:
            ax.plot([x1, x2], [y1, y2], color="#222222", lw=1.2, solid_capstyle="butt", zorder=3)
        for cx, cy, r in h.daireler:
            ax.add_patch(plt.Circle((cx, cy), r, fill=False, color="#222222", lw=1.2, zorder=3))
        x, y, yaw = v["poz"]
        ox, oy = v["koken"][0], v["koken"][1]
        rmaks = v["menzil"][1]
        ax.add_patch(plt.Circle((ox, oy), rmaks, fill=False, ls=":", color="#7f7f7f", lw=0.8, zorder=1))
        b, e = v["kor_sektor"][0]
        pay = v["kor_pay"]
        ax.add_patch(Wedge((ox, oy), 1.2, math.degrees(yaw) + b - pay, math.degrees(yaw) + e + pay, facecolor="#bbbbbb",
                           alpha=0.45, edgecolor="none", zorder=2))
        c, s = math.cos(yaw), math.sin(yaw)
        kose = [(-0.26, -0.26), (0.2625, -0.26), (0.2625, 0.26), (-0.26, 0.26)]
        ax.add_patch(plt.Polygon([(x + c * a - s * b_, y + s * a + c * b_) for a, b_ in kose], closed=True, facecolor="#ffd84d",
                                 edgecolor="#8a6d00", lw=1, zorder=6))
        ax.annotate("", xy=(x + 0.55 * c, y + 0.55 * s), xytext=(x, y), arrowprops=dict(arrowstyle="->", color="#8a6d00", lw=1.5),
                    zorder=7)
        P = np.array([p for p in v["noktalar"] if p is not None])
        if len(P):
            ax.scatter(P[:, 0], P[:, 1], s=3, color="#d62728", zorder=8, linewidths=0)
        ax.plot([ox], [oy], marker="o", ms=4, color="#1f77b4", zorder=9)
        ax.set_aspect("equal")
        ax.set_xlim(0, W)
        ax.set_ylim(0, H)
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        ax.grid(True, color="#eeeeee", lw=0.5, zorder=-1)
        ax.set_title("%s - sanal RPLIDAR C1, baslangic konumunda bir donen tarama: %d / %d isin olcum verdi (kirmizi)\n"
                     "gri kama: kor sektor maskesi [%.0f, %.0f] der; noktali cember: %g m menzil; "
                     "gurultu sigma %.0f mm + 15 mm yuvarlama; mavi: LiDAR merkezi"
                     % (v["ad"], v["gecerli"], v["n"], b - pay, e + pay, rmaks, v["sigma_mm"]), fontsize=8, loc="left")
        yol = os.path.join(GORSEL, "lidar_%s.png" % v["ad"])
        fig.savefig(yol, bbox_inches="tight")
        plt.close(fig)
        print(yol)
    return 0


def komut_kayit(a):
    dn = LidarDeneyi(a.sahne, tohum=a.tohum, donen=not a.anlik)
    dn.devreye_al()
    dn.e.sur_tut(a.v, a.w, int(a.sure * 1000))
    dn.e.istek({"k": "dur"})
    dn.e.bekle(800)
    yol = dn.kayit.kaydet(a.cikti)
    meta, dz = kayit_oku(yol)
    _yazdir("%s: %d satır, %d tarama, gerçek son (%.3f, %.3f, %.1f der), odo son (%.3f, %.3f, %.1f der)"
            % (yol, len(dz["t"]), len(dz["tarama_t"]), *dz["gercek"][-1, :2], math.degrees(dz["gercek"][-1, 2]),
               *dz["odo"][-1, :2], math.degrees(dz["odo"][-1, 2])))
    return 0


def main():
    import argparse
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    alt = ap.add_subparsers(dest="is_")
    alt.add_parser("dogrula")
    alt.add_parser("govde")
    alt.add_parser("sure")
    g = alt.add_parser("gorsel")
    g.add_argument("sahneler", nargs="*")
    c = alt.add_parser("ciz")
    c.add_argument("veri")
    k = alt.add_parser("kayit")
    k.add_argument("--sahne", default="koridor_1")
    k.add_argument("--sure", type=float, default=10.0)
    k.add_argument("--v", type=float, default=0.25)
    k.add_argument("--w", type=float, default=0.0)
    k.add_argument("--tohum", type=int, default=1)
    k.add_argument("--anlik", action="store_true")
    k.add_argument("--cikti", required=True)
    a = ap.parse_args()
    if a.is_ == "ciz":
        return ciz(a.veri)
    if not D.FIZIK_VAR:
        print("fizik bağımlılığı (mujoco) yok: %s" % D.FIZIK_HATA)
        return 2
    if a.is_ == "dogrula":
        komut_dogrula()
        return 0
    if a.is_ == "govde":
        komut_govde()
        return 0
    if a.is_ == "sure":
        sure_olc()
        return 0
    if a.is_ == "gorsel":
        return komut_gorsel(a.sahneler or KORIDORLAR)
    if a.is_ == "kayit":
        return komut_kayit(a)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
