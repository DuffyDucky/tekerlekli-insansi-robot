"""Deneme zinciri: başarısız denemenin haritasını sonraki denemeye taşı (hafızalı sınıf; ilk giriş KPI'sı DEĞİL).

Kural: robot START'ta hiçbir bilgi olmadan başlar; 900 s'de çıkamazsa (fail_sure / fail_sikisma) başarısızdır ve yeni
deneme yine START çizgisinden başlar. Bu modül yeni denemede beyni sıfırlamadan şunları yapar:

    from kesif.deneme import zincir_hazirla, yeni_deneme
    b = KesifBeyni()                 # 1. deneme: ön bilgisiz, varsayılan sürüm (davranış aynı)
    z = zincir_hazirla(b)            # sınır ayarının ilk hâlini saklar, SLAM'i hizalayabilen alt sınıfa çevirir
    ... 1. deneme koşar, başarısız ...
    yeni_deneme(b, z, hizala=True)   # 2. deneme: harita korunur, poz START'a döner, saat 0'dan

Korunan: ızgara (doluluk, isabet ortalaması, dönüşsüz ışın sayacı, START yasak / sanal duvar), dışa açık sınır
hafızası (v3), sahte çıkış listesi, öğrenilmiş odometri ölçekleri (k_don, k_il), sayaçlar (birikimli).
Sıfırlanan: poz (kural gereği robot START'tadır: harita çerçevesinde START pozu = (0, 0, 0), çünkü çerçeve 1. denemenin
başlangıç gövde merkezidir), zaman (yeni deneme saati 0'dan), yol / hedef / kurtarma / bakış / sıkışma durumları, kara
liste (süreye bağlı), sınır gevşetme kademesi, izleyici.

Yeniden hizalama (`hizala=True`): yeni denemenin ilk iki taraması (robot duruyorken) geniş aramayla (±0,20 m,
±8°, zayıf önsel) eski haritaya oturtulur. Gerekçe: robotu START'a bir insan koyar; konum birkaç cm, yön birkaç derece
şaşar. Varsayılan eşleştirmenin açı araması ±3°, önseli 0,01 rad std'dir; büyük yön hatasını bir taramada düzeltemez ve
o arada yanlış pozla haritaya yazar. Hizalama yalnız START çevresindeki poz hatasını giderir; haritanın uzak
bölgelerindeki birikmiş kayma (döngü kapatma yok) olduğu gibi taşınır.

Beyin START'ta olduğunu yalnız kuraldan bilir; yer gerçeği (yerleştirme hatası) beyne verilmez.
"""

import copy
import dataclasses
import math

import numpy as np

from .slam import HafifSLAM


class HizalaliSLAM(HafifSLAM):
    """HafifSLAM + yeni denemenin ilk taramalarında geniş arama. `hizala_kalan` 0 iken HafifSLAM ile birebir aynı."""

    hizala_kalan = 0
    hizala_oteleme_m = 0.20
    hizala_aci_der = 8.0
    hizala_st_m = 0.15             # zayıf önsel std (konum)
    hizala_sth_rad = 0.10          # zayıf önsel std (yön)

    def _omega(self):
        if getattr(self, "_zayif_onsel", False):
            return np.diag([1 / self.hizala_st_m ** 2, 1 / self.hizala_st_m ** 2, 1 / self.hizala_sth_rad ** 2])
        return HafifSLAM._omega(self)

    def tarama_isle(self, tarama, t_simdi):
        if self.hizala_kalan <= 0:
            return HafifSLAM.tarama_isle(self, tarama, t_simdi)
        self.hizala_kalan -= 1
        eski = self.ayar
        a = copy.copy(eski)
        a.eslestirme = dataclasses.replace(eski.eslestirme, kaba_oteleme_m=self.hizala_oteleme_m,
                                           kaba_aci_taban_der=self.hizala_aci_der)
        once = tuple(self.poz)
        self.ayar = a
        self._zayif_onsel = True
        try:
            r = HafifSLAM.tarama_isle(self, tarama, t_simdi)
        finally:
            self.ayar = eski
            self._zayif_onsel = False
        if not hasattr(self, "hizala_kaydi"):
            self.hizala_kaydi = []
        self.hizala_kaydi.append({"durum": r.get("durum"), "kalite": r.get("kalite"),
                                  "duzeltme": [round(float(self.poz[0] - once[0]), 4),
                                               round(float(self.poz[1] - once[1]), 4),
                                               round(float(self.poz[2] - once[2]), 5)]})
        return r


@dataclasses.dataclass
class Zincir:
    sinir0: object                 # 1. deneme öncesi SinirAyari (gevşetme kademesi geri alınır)
    deneme_no: int = 1
    bilinen_m2: list = dataclasses.field(default_factory=list)   # her denemenin sonunda bilinen alan


def zincir_hazirla(beyin):
    """1. denemeden ÖNCE çağrılır. SLAM nesnesinin sınıfını HizalaliSLAM yapar (hizala_kalan = 0: davranış aynı)."""
    if not isinstance(beyin.slam, HizalaliSLAM):
        beyin.slam.__class__ = HizalaliSLAM
    return Zincir(sinir0=copy.deepcopy(beyin.ayar.sinir))


def bilinen_alan_m2(beyin):
    g = beyin.slam.izgara
    return float((g.bos() | g.dolu()).sum()) * g.coz * g.coz


def yeni_deneme(beyin, zincir, hizala=True, hizala_tarama=2):
    """Başarısız denemeden sonra: harita korunur, poz START'a (0, 0, 0), saat 0. Bkz. modül açıklaması."""
    from gezinme.izleyici import YolIzleyici
    b = beyin
    zincir.bilinen_m2.append(bilinen_alan_m2(b))
    zincir.deneme_no += 1
    s = b.slam
    if not isinstance(s, HizalaliSLAM):
        s.__class__ = HizalaliSLAM
    # SLAM: poz ve odometri zinciri START'a; harita, ölçekler aynı
    s.poz = (0.0, 0.0, 0.0)
    s.odo_poz = (0.0, 0.0, 0.0)
    s.gecmis.clear()
    s.t = 0.0
    s._son_poz_tarama = (0.0, 0.0, 0.0)
    s._odo_son = (0.0, 0.0, 0.0)
    s._odo_son_c = (0.0, 0.0, 0.0)
    s.alan = None                       # eşleştirme alanı START çevresinde yeniden kurulsun
    s._alan_tur = 0
    s.ardisik_red = 0
    s.w_tahmin = 0.0
    s.son_noktalar = None
    # beyin bekleme kipi `tur_sayisi < 3`: 1'e çekilince yeni denemede iki tarama durarak işlenir ve ikisi de
    # eşleştirilir (0 olsaydı ilk tarama eşleştirmesiz, (0, 0, 0) pozuyla haritaya yazılırdı)
    s.tur_sayisi = 1
    s.hizala_kalan = int(hizala_tarama) if hizala else 0
    s.hizala_kaydi = []
    # beyin: denemeye bağlı durumlar
    b.t = 0.0
    b.t_plan = -1e9
    b.yol = []
    b.hedef = None
    b.hedef_sinir = None
    b.cikis = None
    b.kara_liste = []
    b.gevset = 0
    b.ayar.sinir = copy.deepcopy(zincir.sinir0)
    b.on_mesafe = None
    b._engel_t = None
    b._bakis_t = None
    b._gecmis = []
    b._kurtarma = None
    b._duvar = None
    b._bak = None
    b._bak_yon = 0.0
    b._donus_onay = False
    b._kay = None
    b._son_donus_t = -1e9
    b.son_komut = (0.0, 0.0)
    b.son_plan = {}
    b.hafiza = None
    b.mod = "baslangic"
    if type(b.izleyici) is YolIzleyici:
        b.izleyici = YolIzleyici(copy.deepcopy(b.izleyici.ayar))
    else:                                   # v4 ZarfIzleyici: aynı sınıf ve zarf parametreleri
        b.izleyici = type(b.izleyici)(copy.deepcopy(b.izleyici.ayar), a_zarf=b.izleyici.a_zarf,
                                      tepki_s=b.izleyici.tepki_s)
    b.olaylar.append((0.0, "deneme", zincir.deneme_no))
    return b


def yerlestirme_hatasi(sahne_ad, tohum, deneme_no, std_m=0.03, std_der=2.0, kirp_m=0.06, kirp_der=4.0):
    """İnsanın robotu START'a koyarken yaptığı hata (yer gerçeği tarafı; beyin görmez): START gövde çerçevesinde
    (ileri, sol, yön rad). 1. deneme 0 (harita çerçevesi o pozla tanımlı). Tohum: sahne adı + tohum + deneme no."""
    if deneme_no <= 1 or (std_m <= 0 and std_der <= 0):
        return (0.0, 0.0, 0.0)
    import zlib
    rng = np.random.default_rng([zlib.crc32(sahne_ad.encode()), int(tohum), int(deneme_no)])
    dx, dy = np.clip(rng.normal(0.0, std_m, 2), -kirp_m, kirp_m) if std_m > 0 else (0.0, 0.0)
    dth = float(np.clip(rng.normal(0.0, std_der), -kirp_der, kirp_der)) if std_der > 0 else 0.0
    return (float(dx), float(dy), math.radians(dth))


def dunya_baslangic(start_poz, hata):
    """START pozu (dünya) + gövde çerçevesinde hata -> Duzenek baslangic (x, y, th)."""
    sx, sy, sth = start_poz
    dx, dy, dth = hata
    c, s = math.cos(sth), math.sin(sth)
    return (sx + c * dx - s * dy, sy + s * dx + c * dy, sth + dth)
