"""KesifBeyni: bilinmeyen labirentte haritalayarak çıkış arayan beyin (gezinme `Beyin` protokolü).

    from kesif.beyin import KesifBeyni, olustur
    b = olustur("labirent_9x9_t1")     # START çizgisinin yerini sahneden alır (yalnız o)
    b = KesifBeyni()                     # sahnesiz: START çizgisi 0,45 m geride, 1,3 m (VARSAYIM)
    v, w = b.adim(t, tarama, artim);  b.durum()

Döngü (20 Hz denetim, 10 Hz LiDAR):
- odometri + tarama -> HafifSLAM (slam.py)
- ≈ 1 Hz (ve olaylarda) planlama: kaba harita, BFS; önce çıkış (dış alan diski) aranır, yoksa sınır seçimi (histerezis)
- yol `gezinme.izleyici.YolIzleyici` ile sürülür (arka dingile göre saf takip, köşede yerinde dönüş)
- güvenlik: START çizgisine yaklaşan hareket kesilir; öndeki engelde izleyici durur, uzarsa yeniden plan / kurtarma;
  sıkışma (komut var, hareket yok) -> geri çekil; sınır kalmazsa kademeli kurtarma (gevşet -> zayıf duvarları unut ->
  START'ı sanal duvar sayan sağ el duvar izleme).
Mod adları: "baslangic", "kesif", "cikis", "hafiza", "kurtarma", "bak", "duvar_izle", "tukendi".
"""

import copy
import math
import time
from dataclasses import dataclass, field

import numpy as np

from .planla import KabaHarita, PlanAyari, iki_katmanli_bfs, yol_cikar2, yol_uzunlugu
from .robot import VARSAYILAN, gezinmeden_oku
from .sinir import SinirAyari, cikis_bul, hedef_sec, sinirlari_bul
from .slam import HafifSLAM, SlamAyari, birlestir

try:
    from gezinme.izleyici import IzleyiciAyar, YolIzleyici
except ImportError:   # pragma: no cover
    raise


@dataclass
class BeyinAyari:
    v_seyir: float = 0.25
    v_hafiza: float = 0.25           # hafızalı koşu seyir hızı. 0,39 denendi (7x7, 9x9): süre kazancı yok (köşelerde
                                     # yerinde dönüş baskın), 7x7de çarpma; 0,25 bırakıldı
    plan_aralik_s: float = 1.0
    start_dur_m: float = 0.30        # gövde MERKEZİ (hakemin baktığı nokta) START çizgisine bundan yakın olacaksa
                                     # çizgiye doğru hareket yok (başlangıç 0,45 m; yerinde dönüş en çok 0,08 m yaklaştırır)
    start_yan_pay_m: float = 0.40    # sanal duvar / yasak bölge çizgi uçlarından bu kadar taşar
    start_derinlik_m: float = 6.0    # yasak bölgenin çizgi gerisindeki derinliği
    bakis_sure_s: float = 4.0        # bakış noktasında sınır kapanmazsa kara listeye
    kara_liste_s: float = 40.0
    sikisma_s: float = 3.0
    geri_m: float = 0.25
    on_serit_m: float = 0.56         # öndeki engel şeridi genişliği (ayak izi 0,523 + pay)
    engel_bekle_s: float = 1.5
    duvar_izle_s: float = 20.0       # sınır kalmayınca duvar izleme bu kadar sürer, sonra yeniden sınır aranır
    # v2 hız profili (v1'de kapalı). Tanı (sonuc/tani_v1.csv, MuJoCo 33 koşu): sürenin %83'ü düz sürüş, ölçülen düz
    # hız ortalaması 0,21 m/s; 15 dk'yı aşan 17x17_t3'te çözüm 131 m. Önü açıkken ve tarama haritaya iyi oturuyorken
    # v_hizli; engel / köşe yaklaşınca izleyicinin yumuşak varışı ve engel rampası (yavas_hizli_m) yavaşlatır.
    hiz_profili: bool = False
    v_hizli: float = 0.39            # teker azamisi
    hizli_on_m: float = 1.0          # önde bu kadar boşluk yoksa v_seyir
    hizli_yan_pay_m: float = 0.15    # ...ve bu boşluk gövde şeridinin her yanına bu kadar geniş şeritte aranır
                                     # (son tarama, gövde çerçevesi: SLAM poz hatasından bağımsız). İlk denemede
                                     # tek çarpma 0,39 m/s'de yay çizerken duvar ucuna yandan sürtünmeydi (önü 1,07 m açık)
    yavas_hizli_m: float = 0.70      # hızlıyken engel yavaşlama rampasının başı (fren mesafesi 0,39²/2 = 0,08 m)
    hizli_kalite: float = 0.0        # son eşleşme kalitesi bunun altındaysa v_seyir (0: denetim yok)
    hizli_w_maks: float = 0.12       # son açısal komut bundan büyükse (yay / düzeltme) v_seyir
    hizli_donus_sonra_s: float = 1.5  # yerinde dönüş / kurtarma / konumlanmadan sonra bu kadar v_seyir
                                     # (2B denemede çarpmalar dönüşten ~1 s sonra 0,39 m/s yayda: yön henüz oturmamış)
    # akıcı köşe (deneysel, varsayılan kapalı): izleyicinin "köşede dur, yerinde dön" eşiği büyütülür; 90 derecelik
    # köşe saf takip yayıyla dönülür (yerinde dönüş yalnız yön hatası donus_gir_rad'ı aşınca)
    akici_kose: bool = False
    # v3 dışa açık sınır önceliği (v1 / v2'de 0 = kapalı). Tanı (sonuc/tani_dolanma.md): dolanan koşularda FINISH
    # yanındaki sınır yüzlerce saniye önce görülmüş, daha yakın sınır seçilip bırakılmıştı; dönüşsüz ışın oranı (dis)
    # >= 0,3 olan sınır, beynin izinli alanında yalnız FINISH ağzında görüldü (2B 2200 örnek, MuJoCo yeniden oynatma).
    # Bu sınırın maliyeti disa_acik_bonus_m kadar düşer; dis titrediği için görülen yer hatırlanır.
    disa_acik_bonus_m: float = 0.0
    disa_acik_esik: float = 0.3
    disa_acik_hafiza_m: float = 1.5
    # v4 hız zarfı (v1-v3'te kapalı). Tanı (sonuc/hiz_tani_v3.csv, MuJoCo v3 57 koşu): düz sürüş sürenin %81'i, ölçülen
    # düz hız 0,225 m/s; v2 hızlı kipi düz sürenin %22'sinde açık. Engelleyen kapılar (tek başına): 1,0 m ön şerit %71,
    # |w| <= 0,12 %53, 1,5 s bekleme %19. Köşe sonu yumuşak varışının 0,10 m/s altı kuyruğu toplam sürenin %10'u.
    # v4: (1) izleyicide fren zarfı v <= fren_hizi(kalan yol) ve fren_hizi(ön serbest mesafe - dur eşiği); (2) hızlı
    # kip izni sabit zamanlayıcı ve 1,0 m kapı yerine saf takip açısından (alfa0..alfa1 arasında v_seyir'den v_hizli'ya),
    # eğrilikten (teker sınırı |v| + |w| iz / 2 <= v_tavan, |w| <= zarf_w_yay) ve öngörülen yayın süpürdüğü alanın son
    # taramaya ve haritaya karşı denetiminden (ayak izi + zarf_pay_m, ufuk = fren mesafesi + zarf_ufuk_ek_m).
    hiz_zarfi: bool = False
    zarf_a: float = 0.5              # m/s² zarfın varsaydığı yavaşlama (firmware fren 1,8; izleyici 1,0)
    zarf_tepki_s: float = 0.15       # s gecikme (tarama 10 Hz + denetim 20 Hz)
    zarf_alfa0: float = 0.25         # rad saf takip açısı bunun altındaysa tam v_hizli (2B ilk taramada 0,10 / 0,25
    zarf_alfa1: float = 0.50         # rad ...bunun üstündeyse v_seyir (arada doğrusal)   %4-6 daha yavaş, çarpma 0)
    zarf_pay_m: float = 0.05         # m süpürme denetiminde ayak izi payı
    zarf_ufuk_ek_m: float = 0.30     # m fren mesafesine eklenen süpürme ufku
    zarf_w_yay: float = 0.6          # rad/s hızlı kipte yayın açısal hız tavanı
    zarf_hizala: bool = True         # süpürme v_seyir'de de çarpıyorsa ve yön hatası donus_cik_rad'ı aşıyorsa yerinde hizalan
    zarf_v_yavas: float = 0.0        # m/s ...ve hız tavanı (0: yok). 2B'de 0,12 denendi: yavaş yay yine çarptı (20
                                     # koşuda 8 çarpma; kaba sürüm 3), kapalı
    # v5 dönüş / yay güvenliği (v1-v4'te kapalı). Tanı (MuJoCo yeniden koşu, sınama2'deki iki v4 çarpması):
    # (a) 17x17_t11 t1: plan 0,33 m/s'de değişti, izleyici yerinde dönüşe geçti; süpürme denetimi robot henüz frenlerken
    #     (v 0,20) yapıldı, hiçbir dönüş / kayma sığmadı (donus_sigmaz) ve dönüş yine de başladı -> 6,1 s temas.
    # (b) 17x17_t13 t0: yay süpürmesi v_seyir'de 2,2 s boyunca çarpma öngördü, |alfa| < donus_cik_rad olduğu için önlem
    #     yoktu; yol duvar ucunun 0,30 m yanından geçiyordu.
    donus_durunca: bool = False      # yerinde dönüş süpürmesi robot durunca (izleyici hızı <= 0,02) denetlenir
    donus_kay_m: float = 0.60        # dönüş sığmıyorsa düz kayma arama aralığı (v1-v4 0,60)
    donus_sigmaz_geri: bool = False  # hiçbir dönüş / kayma sığmıyorsa körlemesine dönme: önce geri çekil + yeniden planla
    yay_kacin: bool = False          # yay v_seyir'de de çarpıyorsa (hizalanma yoksa) eğriliği çarpmayan en yakın değere it
    yay_kacin_pay_m: float = 0.03    # m kaçınma adaylarının süpürme payı
    kose_esigi_der: float = 100.0
    donus_gir_rad: float = 1.3
    # izleyici: köşede dönme merkezi hücre ortasına gelince ön yüz önündeki duvara ≈ 0,20 m kalır (1,3 m hücre);
    # gezinmenin varsayılan 0,30 m dur eşiği köşeye varmayı engelliyor, bu yüzden 0,12 / 0,18 / 0,50
    izleyici: dict = field(default_factory=lambda: {"dur_mesafe_m": 0.12, "kalk_mesafe_m": 0.18,
                                                     "yavas_mesafe_m": 0.50})
    sinir: SinirAyari = field(default_factory=SinirAyari)
    plan: PlanAyari = field(default_factory=PlanAyari)
    slam: SlamAyari = field(default_factory=SlamAyari)


def surum_ayari(surum="v1"):
    """Sürüm adı -> BeyinAyari. v1: ilk teslim (commit 461216f) davranışı; v2: hız profili; v3: v2 + dışa açık sınır
    önceliği; v4: v3 + hız zarfı."""
    a = BeyinAyari()
    if surum in (None, "", "v1"):
        return a
    if surum == "v2":
        a.hiz_profili = True
        return a
    if surum == "v3":                  # v2 + dışa açık sınır önceliği
        a.hiz_profili = True
        a.disa_acik_bonus_m = 25.0
        return a
    if surum == "v4":                  # v3 + hız zarfı (fren zarfı, ölçüye dayalı hızlanma izni, yay süpürme denetimi)
        a.hiz_profili = True
        a.disa_acik_bonus_m = 25.0
        a.hiz_zarfi = True
        return a
    if surum == "v5":                  # v4 + dönüş / yay güvenliği (durunca denetim, körlemesine dönmeme, yay kaçınma)
        a.hiz_profili = True
        a.disa_acik_bonus_m = 25.0
        a.hiz_zarfi = True
        a.donus_durunca = True
        a.donus_kay_m = 1.0
        a.donus_sigmaz_geri = True
        a.yay_kacin = True
        return a
    if surum == "v2k":                # v2 + akıcı köşe (deneysel)
        a.hiz_profili = True
        a.akici_kose = True
        return a
    raise ValueError("bilinmeyen sürüm %r" % surum)


# Karar (2026-11-25, MuJoCo sınama kümesi 13x13_t4..t8 + 17x17_t4..t8 x 2 tohum): v1 14/20, v2 14/20, çarpma 0 / 0;
# kural "v2 başarısı az değil ve çarpma artmadı" -> v2. Kazanç küçük (süre ~%5 kısa); geliştirme kümesinde v2 27/33,
# v1 28/33. Ayrıntı: BENIOKU.md "v2", sonuc/SONUC.md.
# Karar 2 (2026-11-25 öğle, MuJoCo sınama2 13x13_t9..t13 + 17x17_t9..t13 x 2 tohum): v2 15/20, v3 15/20, çarpma
# 0 / 0 -> kural gereği v3. Sınama2'de fark yok; geliştirmede v3 30/37, v2 27/37 (17x17_t3 üç tohumda çözüldü).
# Karar 3 (2026-11-25 akşam, MuJoCo YENİ sınama3 13x13 / 17x17 t14..t18 x 2 tohum): v3 14/20, v4 17/20, çarpma 1 / 0
# -> kural gereği v4. Geliştirme v3 30/37, v4 33/37, süre oranı ortanca 0,88. UYARI: görülmüş sınama2 gerileme
# denetiminde v4 iki çarpma verdi (17x17_t11 t1 yerinde dönüşte 6,1 s temas; 17x17_t13 t0 yayda 0,05 s; v3 0) ve duvar
# payı < 5 mm koşu arttı.
# Karar 4 (2026-11-25 gece, bağımsız inceleme sonrası): v4'ün iki çarpmasının kök nedeni giderildi (v5). YENİ sınama4
# (13x13 / 17x17 t19..t23 x 2): v3 12/20, v5 12/20, çarpma 0 / 0 (kural sağlandı). Ama geliştirmede v5 bir çarpma verdi
# (17x17_t1 t1, 0,25 s); v3 bütün MuJoCo kümelerinde 0. "Çarpma sıfır" yalnız v3'te kanıtlı -> varsayılan v3'e döndü.
# v4 / v5 seçmeli (surum_ayari). Ayrıntı: BENIOKU.md "v5".
VARSAYILAN_SURUM = "v3"


def _sar(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


class KesifBeyni:
    def __init__(self, ayar=None, start_cizgisi=None, hafiza=None, robot=None, ozellik=None):
        # ayar verilmezse varsayılan sürüm (VARSAYILAN_SURUM; canli.py / kos_mujoco ayarsız kurar)
        self.ayar = a = copy.deepcopy(ayar) if ayar is not None else surum_ayari(VARSAYILAN_SURUM)
        self.robot = robot or gezinmeden_oku(VARSAYILAN)
        izg = None
        if hafiza is not None:
            from .izgara import Izgara
            izg = Izgara.sozlukten(hafiza["izgara"])
        self.slam = HafifSLAM(a.slam, self.robot, ozellik, izgara=izg)
        iz_ayar = dict(v_max=a.v_seyir)
        iz_ayar.update(a.izleyici)
        if a.akici_kose:
            iz_ayar.update(kose_esigi_rad=math.radians(a.kose_esigi_der), donus_gir_rad=a.donus_gir_rad)
        if a.hiz_zarfi:
            from .surus4 import ZarfIzleyici
            self.izleyici = ZarfIzleyici(IzleyiciAyar(**iz_ayar), a_zarf=a.zarf_a, tepki_s=a.zarf_tepki_s)
        else:
            self.izleyici = YolIzleyici(IzleyiciAyar(**iz_ayar))
        if start_cizgisi is None:
            start_cizgisi = ((-0.45, 0.65), (-0.45, -0.65))
        self.start = (tuple(map(float, start_cizgisi[0])), tuple(map(float, start_cizgisi[1])))
        self._maske_anahtar = None
        self._start_maskele()
        if hafiza is None:
            self._baslangic_bos()
        self.hafiza = hafiza
        self.mod = "hafiza" if hafiza is not None else "baslangic"
        self.t = 0.0
        self.t_plan = -1e9
        self.yol = []
        self.hedef = None
        self.hedef_sinir = None
        self.cikis = None
        self.kara_liste = []          # (x, y, bitis_t)
        self.sahte_cikis = []         # (x, y)
        self.gevset = 0
        self.on_mesafe = None
        self._engel_t = None
        self._bakis_t = None
        self._gecmis = []             # (t, x, y, th, v_k, w_k)
        self._kurtarma = None
        self._duvar = None
        self._bak = None
        self._bak_yon = 0.0           # zorunlu dönüş yönü (+1 sola, -1 sağa, 0 kısa yol)
        self._donus_onay = False      # izleyicinin başlattığı yerinde dönüşün süpürmesi denetlendi
        self._kay = None              # dönüş sığmıyorsa düz ileri/geri konumlanma
        self.olaylar = []
        self.sayac = {"plan": 0, "kurtarma": 0, "kara_liste": 0, "start_kesme": 0, "yol_yok": 0, "donus_ters": 0,
                      "donus_kay": 0, "donus_sigmaz": 0}
        self.zaman = {"plan_ms": [], "adim_ms": []}
        self.son_plan = {}
        self.son_sinirlar = []
        self._son_donus_t = -1e9          # v2: son yerinde dönüş / kurtarma / konumlanma anı
        self.disa_acik = []               # v3: dışa açık görülmüş sınır merkezleri (beyin çerçevesi)
        self.son_komut = (0.0, 0.0)

    # ------------------------------------------------------------ START koruması
    def _start_cerceve(self):
        (x1, y1), (x2, y2) = self.start
        tx, ty = x2 - x1, y2 - y1
        L = math.hypot(tx, ty)
        tx, ty = tx / L, ty / L
        nx, ny = -ty, tx                       # içeri (robotun bulunduğu yan) normali
        if (0.0 - x1) * nx + (0.0 - y1) * ny < 0:
            nx, ny = -nx, -ny
        return (x1, y1), (tx, ty), (nx, ny), L

    def _start_maskele(self):
        g = self.slam.izgara
        anahtar = (g.nx, g.ny, g.x0, g.y0)
        if anahtar == self._maske_anahtar:
            return
        self._maske_anahtar = anahtar
        a = self.ayar
        (x1, y1), (tx, ty), (nx, ny), L = self._start_cerceve()
        pad = a.start_yan_pay_m
        # yalnız ilgili kutu
        uc = [(x1 - tx * pad, y1 - ty * pad), (x1 + tx * (L + pad), y1 + ty * (L + pad))]
        xs = [p[0] for p in uc] + [p[0] - nx * a.start_derinlik_m for p in uc]
        ys = [p[1] for p in uc] + [p[1] - ny * a.start_derinlik_m for p in uc]
        g.kapsa(min(xs), min(ys), max(xs), max(ys))
        i0, j0 = g.hucre(min(xs) - 0.2, min(ys) - 0.2)
        i1, j1 = g.hucre(max(xs) + 0.2, max(ys) + 0.2)
        i0, j0 = max(int(i0), 0), max(int(j0), 0)
        i1, j1 = min(int(i1), g.nx - 1), min(int(j1), g.ny - 1)
        II, JJ = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1), indexing="ij")
        cx, cy = g.merkezler(II, JJ)
        u = (cx - x1) * tx + (cy - y1) * ty
        s = (cx - x1) * nx + (cy - y1) * ny
        boy = (u >= -pad) & (u <= L + pad)
        g.yasak[i0:i1 + 1, j0:j1 + 1] |= boy & (s < -0.02) & (s > -a.start_derinlik_m)
        g.sanal[i0:i1 + 1, j0:j1 + 1] |= boy & (np.abs(s) <= 0.06)
        self._maske_anahtar = (g.nx, g.ny, g.x0, g.y0)

    def _baslangic_bos(self):
        """Kural: robot START çizgisinin hemen içinde; çizgi ile robot arası boştur (arka kör sektörde kalır)."""
        (x1, y1), (tx, ty), (nx, ny), L = self._start_cerceve()
        g = self.slam.izgara
        c = g.coz
        us, ss = np.meshgrid(np.arange(0.1, L - 0.1, c / 2), np.arange(0.08, 0.5, c / 2), indexing="ij")
        px = x1 + us * tx + ss * nx
        py = y1 + us * ty + ss * ny
        # yalnız robotun gerisi (gövde merkezinden 0,1 m öne kadar)
        g.bos_yaz(px.ravel(), py.ravel())
        fx, fy = self.slam.ayak_izi_noktalari((0.0, 0.0, 0.0), iceri=0.0)
        g.bos_yaz(fx, fy)

    def _start_uzaklik(self, poz, v=0.0, w=0.0, dt=0.0):
        """Gövde merkezinin START çizgisine işaretli uzaklığı (içeri +), dt sonra öngörülen pozda (çizgi boyunca
        uçlardan 1 m dışarıdaysa 1e9)."""
        (x1, y1), (tx, ty), (nx, ny), L = self._start_cerceve()
        x, y, th = poz
        if dt > 0:
            q = -self.robot.dingil_x_m
            a = (v * dt, 0.0, w * dt)
            # dingil çevresinde hareket
            ax_p = birlestir((x, y, th), (-q, 0.0, 0.0))
            ax_p = birlestir(ax_p, a)
            x, y, th = birlestir(ax_p, (q, 0.0, 0.0))
        u = (x - x1) * tx + (y - y1) * ty
        if -1.0 <= u <= L + 1.0:
            return (x - x1) * nx + (y - y1) * ny
        return 1e9

    def _start_filtre(self, poz, v, w):
        a = self.ayar
        d0 = self._start_uzaklik(poz)
        if d0 > a.start_dur_m + 0.3:
            return v, w
        d1 = self._start_uzaklik(poz, v, w, 0.3)
        if d1 < a.start_dur_m and d1 < d0 - 1e-4:
            self.sayac["start_kesme"] += 1
            return 0.0, 0.0
        return v, w

    # ------------------------------------------------------------ algı yardımcıları
    def _on_mesafe(self):
        nok = getattr(self.slam, "son_noktalar", None)
        if nok is None:
            return None
        x, y = nok
        on = self.robot.on_x
        yari = self.ayar.on_serit_m / 2
        m = (np.abs(y) <= yari) & (x > on - 0.02)
        if not m.any():
            return math.inf
        return float(max(0.0, (x[m] - on).min()))

    def _hizli_serit_acik(self):
        """Son taramada gövde önünde (ön yüzden hizli_on_m) ve yanlarda hizli_yan_pay_m genişletilmiş şerit boş mu."""
        nok = getattr(self.slam, "son_noktalar", None)
        if nok is None:
            return False
        x, y = nok
        on = self.robot.on_x
        yari = self.ayar.on_serit_m / 2 + self.ayar.hizli_yan_pay_m
        m = (np.abs(y) <= yari) & (x > on - 0.02) & (x < on + self.ayar.hizli_on_m)
        return not bool(m.any())

    # ------------------------------------------------------------ protokol
    def adim(self, t, tarama, artim):
        t_a = time.perf_counter()
        self.t = t
        if artim is not None:
            self.slam.odometri(artim, t)
        yeni_tarama = tarama is not None
        if yeni_tarama:
            self.slam.tarama_isle(tarama, t)
            self._start_maskele()
            self.on_mesafe = self._on_mesafe()
        poz = self.slam.poz
        self._gecmis.append((t, poz[0], poz[1], poz[2]) + self.son_komut)
        while self._gecmis and self._gecmis[0][0] < t - 6.0:
            self._gecmis.pop(0)
        if self.slam.tur_sayisi < 3:
            self.mod = "baslangic" if self.hafiza is None else "hafiza"
            return self._cik(0.0, 0.0, t_a)
        if self._kurtarma is not None:
            v, w = self._kurtarma_adim(t, poz)
            return self._cik(v, w, t_a, filtre=False)
        if self._kay is not None:
            v, w = self._kay_adim(t, poz)
            return self._cik(v, w, t_a)
        if self._bak is not None:
            e = _sar(self._bak - poz[2])
            if abs(e) < 0.2:
                self._bak = None
                self._bak_yon = 0.0
                self.t_plan = -1e9
            else:
                if self._bak_yon and e * self._bak_yon < 0 and abs(e) > 0.35:
                    e = e + self._bak_yon * 2 * math.pi        # zorunlu yönde uzun yol
                return self._cik(0.0, max(-0.8, min(0.8, 1.5 * e)) if abs(e) > 0.35 else math.copysign(0.4, e), t_a)
        if self.mod == "duvar_izle":
            if t - self._duvar_t0 > self.ayar.duvar_izle_s:
                # duvar izleme yeni yer açmış olabilir: sınır aramaya dön (kademe korunur)
                self._duvar = None
                self.mod = "kesif"
                self.t_plan = -1e9
                self.olaylar.append((round(t, 1), "duvar_izle_bitti", ""))
                return self._cik(0.0, 0.0, t_a)
            v, w = self._duvar_adim(poz, yeni_tarama)
            return self._cik(v, w, t_a)
        gerek = (t - self.t_plan >= self.ayar.plan_aralik_s) or not self.yol
        if gerek:
            self._planla(t, poz)
        # hafızalı koşuda yol bilinen haritada: tavan hıza kadar (keşifte v_seyir)
        self.izleyici.ayar.v_max = self.ayar.v_hafiza if self.mod == "hafiza" else self.ayar.v_seyir
        if self.ayar.hiz_zarfi:
            self._hiz_ayarla_v4()
        elif self.ayar.hiz_profili:
            self._hiz_ayarla()
        k = self.izleyici.komut(poz, on_mesafe=self.on_mesafe)
        v, w = k.v, k.w
        if k.mod == "yerinde":
            self._son_donus_t = t
        # v5: izleyici yerinde dönüşe geçtiğinde hâlâ frenliyorsa (w 0) denetim duruş pozunda yapılır
        bekle_dur = self.ayar.donus_durunca and abs(getattr(self.izleyici, "_v", 0.0)) > 0.02
        if k.mod == "yerinde" and not self._donus_onay and k.hedef is not None and not bekle_dur:
            if self._donus_karar(poz, k) is not None:
                return self._cik(0.0, 0.0, t_a)
        if k.mod != "yerinde":
            self._donus_onay = False
        if k.durdu:
            if self._engel_t is None:
                self._engel_t = t
            elif t - self._engel_t > self.ayar.engel_bekle_s:
                self._engel_t = None
                self._kurtarma_baslat(t, "on_engel")
        else:
            self._engel_t = None
        if k.bitti:
            self._varis(t, poz)
        if self._sikisti(t):
            self._kurtarma_baslat(t, "sikisma")
        return self._cik(v, w, t_a)

    def _hiz_ayarla(self):
        """v2: önü açık ve eşleşme iyiyse v_hizli, değilse v_seyir; hızlıyken engel rampası erken başlar."""
        a = self.ayar
        iz = self.izleyici.ayar
        acik = (self._hizli_serit_acik() and abs(self.son_komut[1]) <= a.hizli_w_maks
                and self.t - self._son_donus_t >= a.hizli_donus_sonra_s)
        kal = self.slam.son.get("kalite") if isinstance(self.slam.son, dict) else None
        iyi = a.hizli_kalite <= 0 or (kal is not None and kal >= a.hizli_kalite)
        if acik and iyi and self.mod in ("kesif", "cikis", "hafiza"):
            iz.v_max = max(iz.v_max, a.v_hizli)
            iz.yavas_mesafe_m = a.yavas_hizli_m
            self.sayac["hizli"] = self.sayac.get("hizli", 0) + 1
        else:
            iz.yavas_mesafe_m = a.izleyici.get("yavas_mesafe_m", 0.50)

    def _hiz_ayarla_v4(self):
        """v4: v_seyir üstüne çıkış izni ölçüden: saf takip açısı, eğrilik / teker sınırı, yay süpürme denetimi.
        Fren zarfı izleyicide (surus4.ZarfIzleyici). İzin yoksa izleyici v_seyir ile sürer (v3 hız tavanı)."""
        from .surus4 import supurme_carpar, yay_pozlari
        a = self.ayar
        iz = self.izleyici
        ia = iz.ayar
        taban = ia.v_max
        if self.mod not in ("kesif", "cikis", "hafiza") or iz.son.mod != "izle" or iz.son_alfa is None:
            return
        f = (a.zarf_alfa1 - abs(iz.son_alfa)) / max(1e-6, a.zarf_alfa1 - a.zarf_alfa0)
        f = max(0.0, min(1.0, f))
        v = taban + f * (a.v_hizli - taban)
        k = abs(iz.son_kappa)
        v = min(v, self.robot.v_tavan / (1.0 + 0.5 * self.robot.iz_m * k))
        if k > 1e-6:
            v = min(v, a.zarf_w_yay / k)
        tarama = getattr(self.slam, "son_noktalar", None)

        def carpar(vv):
            ufuk = vv * a.zarf_tepki_s + vv * vv / (2.0 * a.zarf_a) + a.zarf_ufuk_ek_m
            P = yay_pozlari(vv, iz._w, iz.son_kappa, self.robot.dingil_x_m, ufuk, a_w=ia.a_w, w_max=ia.w_max)
            return supurme_carpar(P, self.robot, a.zarf_pay_m, tarama_xy=tarama, dolu_mu=self._dolu_mu,
                                  govde_poz=self.slam.poz)
        if v > taban + 0.01 and not carpar(v):
            ia.v_max = v
            self.sayac["hizli"] = self.sayac.get("hizli", 0) + 1
            return
        if v > taban + 0.01:
            self.sayac["zarf_red"] = self.sayac.get("zarf_red", 0) + 1
        # v_seyir'de de süpürme çarpıyorsa (2B: yerinde / bakış dönüşünden sonra yön oturmadan v_seyir'de yayla duvar
        # ucuna sürtünme): yön hatası büyükse önce yerinde hizalan, değilse yavaş sür
        if (a.zarf_hizala or a.zarf_v_yavas > 0) and carpar(taban):
            self.sayac["zarf_yavas"] = self.sayac.get("zarf_yavas", 0) + 1
            iz.hizala_iste = a.zarf_hizala
            if a.zarf_v_yavas > 0:
                ia.v_max = min(taban, a.zarf_v_yavas)
            if a.yay_kacin and not (a.zarf_hizala and abs(iz.son_alfa) > ia.donus_cik_rad):
                # v5: hizalanma yoksa (yön hatası küçük) yayın eğriliğini çarpmayan en yakın değere it (bir adım)
                k0 = iz.son_kappa
                vv = taban
                ufuk = vv * a.zarf_tepki_s + vv * vv / (2.0 * a.zarf_a) + a.zarf_ufuk_ek_m
                for dk in (0.0, 0.15, -0.15, 0.3, -0.3, 0.5, -0.5, 0.8, -0.8):
                    kk = k0 + dk
                    if abs(kk) * vv > ia.w_max:
                        continue
                    P = yay_pozlari(vv, iz._w, kk, self.robot.dingil_x_m, ufuk, a_w=ia.a_w, w_max=ia.w_max)
                    if not supurme_carpar(P, self.robot, a.yay_kacin_pay_m, tarama_xy=tarama, dolu_mu=self._dolu_mu,
                                          govde_poz=self.slam.poz):
                        iz.kappa_iste = kk
                        self.sayac["yay_kacin"] = self.sayac.get("yay_kacin", 0) + 1
                        break
                else:
                    self.sayac["yay_kacin_yok"] = self.sayac.get("yay_kacin_yok", 0) + 1

    def _cik(self, v, w, t_a, filtre=True):
        if abs(v) < 0.02 and abs(w) > 0.05 or self.mod in ("kurtarma", "konumlan", "duvar_izle"):
            self._son_donus_t = self.t
        if filtre:
            v, w = self._start_filtre(self.slam.poz, v, w)
        self.son_komut = (v, w)
        self.zaman["adim_ms"].append((time.perf_counter() - t_a) * 1000.0)
        if len(self.zaman["adim_ms"]) > 20000:
            del self.zaman["adim_ms"][:10000]
        return v, w

    def durum(self):
        g = self.slam.izgara
        return {"poz": tuple(self.slam.poz), "mod": self.mod, "yol": list(self.yol), "hedef": self.hedef,
                "harita": {"cozunurluk_m": g.coz, "orijin": (g.x0, g.y0), "izgara": g.durum_dizisi().T,
                           "dizin": "izgara[satır = y, sütun = x]; -1 bilinmeyen, 0 boş, 100 dolu"},
                "ek": {"cerceve": "baslangic", "slam": dict(self.slam.son), "start_cizgisi": self.start, "cikis": self.cikis,
                       "sayac": dict(self.sayac), "slam_istatistik": dict(self.slam.istatistik),
                       "plan": dict(self.son_plan), "on_mesafe": self.on_mesafe,
                       "k_don": self.slam.k_don, "k_il": self.slam.k_il,
                       "sinirlar": list(self.son_sinirlar),
                       "sinirlar_dizin": "[merkez_x, merkez_y, boy_m, bakis_x, bakis_y, maliyet] (son plan)",
                       "secilen_sinir": None if self.hedef_sinir is None else
                       [round(self.hedef_sinir.merkez[0], 2), round(self.hedef_sinir.merkez[1], 2)],
                       "disa_acik": list(self.disa_acik),
                       "surum": ("v5" if self.ayar.yay_kacin or self.ayar.donus_durunca else "v4")
                       if self.ayar.hiz_zarfi else
                       (("v3" if self.ayar.disa_acik_bonus_m > 0 else "v2") if self.ayar.hiz_profili else "v1")}}

    def hafiza_ver(self):
        """Ek tur için: harita + son poz (benzetici koşu FINISH'te bitince çağırır)."""
        return {"izgara": self.slam.izgara.kopya_sozluk(), "cikis_poz": tuple(self.slam.poz), "cikis": self.cikis}

    # ------------------------------------------------------------ planlama
    def _planla(self, t, poz):
        t0 = time.perf_counter()
        self.t_plan = t
        self.sayac["plan"] += 1
        a = self.ayar
        pa = a.plan
        if self.gevset:
            pa = PlanAyari(**{**pa.__dict__, "r_min": pa.r_min - 0.03})
        kh = KabaHarita(self.slam.izgara, pa)
        dist, d_iyi, d_min = iki_katmanli_bfs(kh, poz[0], poz[1])
        self.kara_liste = [k for k in self.kara_liste if k[2] > t]
        yol = None
        bilgi = {}
        # 1) hafızalı koşu: bilinen çıkışa git
        if self.mod == "hafiza" and self.hafiza is not None:
            hx, hy, hth = self.hafiza["cikis_poz"]
            i, j = kh.hucre(hx, hy)
            if kh.icinde(i, j):
                hi = self._en_yakin_ulasilan(kh, dist, int(i), int(j), 1.0)
                if hi is not None:
                    yol = yol_cikar2(kh, d_iyi, d_min, hi)
            if yol:
                yol = list(yol) + [(hx + 1.0 * math.cos(hth), hy + 1.0 * math.sin(hth))]
                self.hedef = (hx, hy)
                bilgi["hafiza"] = True
            else:
                self.mod = "kesif"
        # 2) çıkış (dış alan)
        if yol is None:
            c, n = cikis_bul(kh, dist, a.sinir)
            bilgi["dis_aday"] = n
            if c is not None and not any(math.hypot(c[1][0] - sx, c[1][1] - sy) < 2.0 for sx, sy in self.sahte_cikis):
                yol = yol_cikar2(kh, d_iyi, d_min, c[0])
                if yol:
                    # dışarı doğru uzat: son parçanın yönünde 1,5 m
                    if len(yol) >= 2:
                        dx, dy = yol[-1][0] - yol[-2][0], yol[-1][1] - yol[-2][1]
                    else:
                        dx, dy = yol[-1][0] - poz[0], yol[-1][1] - poz[1]
                    L = math.hypot(dx, dy) or 1.0
                    uzat = (yol[-1][0] + 1.5 * dx / L, yol[-1][1] + 1.5 * dy / L)
                    if kh.acik_oku(np.array([uzat[0]]), np.array([uzat[1]]))[0] > 0.3:
                        yol = list(yol) + [uzat]
                    if self.cikis is None:
                        self.olaylar.append((round(t, 1), "cikis_goruldu", c[1]))
                    self.cikis = c[1]
                    self.hedef = c[1]
                    self.mod = "cikis"
        # 3) sınır
        if yol is None:
            sinirlar = sinirlari_bul(kh, dist, poz, a.sinir)
            sinirlar = [s for s in sinirlar if not any(math.hypot(s.merkez[0] - kx, s.merkez[1] - ky) < 1.0
                                                       for kx, ky, _ in self.kara_liste)]
            bilgi["sinir"] = len(sinirlar)
            if a.disa_acik_bonus_m > 0:
                self._disa_acik_uygula(sinirlar, bilgi)
            # oynatıcı için (seyrek; kayıt 2 s aralıkla alır): sınır merkezi, boyu, bakış noktası, maliyeti
            self.son_sinirlar = [[round(s.merkez[0], 2), round(s.merkez[1], 2), round(float(s.boy_m), 2),
                                  round(float(s.bakis_xy[0]), 2), round(float(s.bakis_xy[1]), 2),
                                  round(float(s.maliyet), 2)] for s in sinirlar[:40]]
            sec, degisti = hedef_sec(sinirlar, self.hedef_sinir, a.sinir)
            if sec is not None:
                yol = yol_cikar2(kh, d_iyi, d_min, sec.bakis)
                if degisti:
                    self._bakis_t = None
                self.hedef_sinir = sec
                self.hedef = sec.bakis_xy
                self.mod = "kesif"
                bilgi.update({"hedef_maliyet": round(sec.maliyet, 2), "d_yol": round(sec.d_yol_m, 2),
                              "dis": round(sec.dis, 2)})
            else:
                self.hedef_sinir = None
        if yol is None:
            self.sayac["yol_yok"] += 1
            self._tukendi(t, poz)
        else:
            self.yol = yol
            self.izleyici.yol_ver(yol)
        bilgi["ms"] = round((time.perf_counter() - t0) * 1000.0, 1)
        bilgi["kaba"] = (kh.ni, kh.nj)
        self.son_plan = bilgi
        self.zaman["plan_ms"].append(bilgi["ms"])

    def _disa_acik_uygula(self, sinirlar, bilgi):
        """v3: dönüşsüz ışın oranı yüksek (önü sensör menzili ötesine açık) sınırı ve hatırlanan yerini öne al."""
        a = self.ayar
        for s in sinirlar:
            if s.dis >= a.disa_acik_esik and not any(math.hypot(s.merkez[0] - x, s.merkez[1] - y) < 1.0
                                                     for x, y in self.disa_acik):
                self.disa_acik.append((round(s.merkez[0], 2), round(s.merkez[1], 2)))
                self.olaylar.append((round(self.t, 1), "disa_acik_sinir", self.disa_acik[-1]))
        n = 0
        for s in sinirlar:
            if s.dis >= a.disa_acik_esik or any(math.hypot(s.merkez[0] - x, s.merkez[1] - y) < a.disa_acik_hafiza_m
                                                for x, y in self.disa_acik):
                s.maliyet -= a.disa_acik_bonus_m
                n += 1
        bilgi["disa_acik"] = n

    def _en_yakin_ulasilan(self, kh, dist, i, j, yaricap_m):
        r = int(math.ceil(yaricap_m / kh.coz))
        i0, j0, i1, j1 = max(i - r, 0), max(j - r, 0), min(i + r + 1, kh.ni), min(j + r + 1, kh.nj)
        alt = dist[i0:i1, j0:j1]
        ii, jj = np.nonzero(alt >= 0)
        if ii.size == 0:
            return None
        d2 = (ii + i0 - i) ** 2 + (jj + j0 - j) ** 2
        k = int(np.argmin(d2))
        return int(ii[k] + i0), int(jj[k] + j0)

    def _varis(self, t, poz):
        """Yol sonu: sınır bakış noktasında sınır kapanmadıysa sınıra dön, `bakis_sure_s` sonra kara listeye al."""
        if self.mod == "cikis":
            # dış alana geldik ama hakem bitirmedi: sahte çıkış
            if self.cikis is not None:
                self.sahte_cikis.append(self.cikis)
                self.olaylar.append((round(t, 1), "sahte_cikis", self.cikis))
            self.cikis = None
            self.mod = "kesif"
            self.yol = []
            return
        if self.mod == "hafiza":
            self.mod = "kesif"
            self.yol = []
            return
        s = self.hedef_sinir
        if s is None:
            self.yol = []
            return
        if self._bakis_t is None:
            self._bakis_t = t
        if t - self._bakis_t > self.ayar.bakis_sure_s:
            self.kara_liste.append((s.merkez[0], s.merkez[1], t + self.ayar.kara_liste_s))
            self.sayac["kara_liste"] += 1
            self.hedef_sinir = None
            self._bakis_t = None
            self.yol = []
            return
        # sınıra doğru dön (kör sektör arkada)
        yon = math.atan2(s.merkez[1] - poz[1], s.merkez[0] - poz[0])
        if abs(_sar(yon - poz[2])) > 0.6:
            e = _sar(yon - poz[2])
            if not self._supurme_carpar(poz, e):
                self._bak, self._bak_yon = yon, 0.0
            elif not self._supurme_carpar(poz, e - math.copysign(2 * math.pi, e)):
                self._bak, self._bak_yon = yon, -math.copysign(1.0, e)
        self.t_plan = min(self.t_plan, t - self.ayar.plan_aralik_s + 0.3)

    # ------------------------------------------------------------ yerinde dönüş süpürme denetimi
    def _supurme_carpar(self, poz, dth, pay=0.03):
        """Gövde arka dingil çevresinde poz[2]'den dth (işaretli) dönerken haritadaki dolu / sanal hücreye değer mi.
        Ayak izi çevresi 4 cm aralıkla, açı yaklaşık 5 derece adımla örneklenir."""
        r = self.robot
        g = self.slam.izgara
        q = -r.dingil_x_m
        c0, s0 = math.cos(poz[2]), math.sin(poz[2])
        ax, ay = poz[0] - q * c0, poz[1] - q * s0
        if getattr(self, "_cevre", None) is None:
            hx, hy = r.derinlik_m / 2 + pay, r.genislik_m / 2 + pay
            ux = np.arange(-hx, hx + 1e-9, 0.04)
            uy = np.arange(-hy, hy + 1e-9, 0.04)
            px = np.concatenate([ux, ux, np.full(uy.size, -hx), np.full(uy.size, hx)]) + q
            py = np.concatenate([np.full(ux.size, -hy), np.full(ux.size, hy), uy, uy])
            self._cevre = (px, py)
        px, py = self._cevre
        n = max(2, int(math.ceil(abs(dth) / math.radians(5.0))) + 1)
        A = poz[2] + np.linspace(0.0, dth, n)[:, None]
        wx = ax + np.cos(A) * px[None, :] - np.sin(A) * py[None, :]
        wy = ay + np.sin(A) * px[None, :] + np.cos(A) * py[None, :]
        return self._dolu_mu(wx.ravel(), wy.ravel())

    def _dolu_mu(self, wx, wy):
        g = self.slam.izgara
        i, j = g.hucre(wx, wy)
        ic = (i >= 0) & (i < g.nx) & (j >= 0) & (j < g.ny)
        i, j = i[ic], j[ic]
        return bool(((g.L[i, j] > g.esik_dolu) | g.sanal[i, j]).any())

    def _duz_carpar(self, poz, s, pay=0.02):
        """Gövde yönü boyunca s (m, işaretli) düz giderken dolu / sanal hücreye değer mi."""
        r = self.robot
        c, si = math.cos(poz[2]), math.sin(poz[2])
        hx, hy = r.derinlik_m / 2 + pay, r.genislik_m / 2 + pay
        ux, uy = np.meshgrid(np.arange(-hx, hx + 1e-9, 0.04), np.arange(-hy, hy + 1e-9, 0.04), indexing="ij")
        ux, uy = ux.ravel(), uy.ravel()
        for d in np.linspace(0.0, s, max(2, int(abs(s) / 0.05) + 1))[1:]:
            if self._dolu_mu(poz[0] + (ux + d) * c - uy * si, poz[1] + (ux + d) * si + uy * c):
                return True
        return False

    def _donus_karar(self, poz, k):
        """İzleyici yerinde dönmek istiyor. Süpürme sığıyorsa onayla (None); ters yönde sığıyorsa o yönde dön (_bak);
        hiçbiri sığmıyorsa yön boyunca en yakın sığan noktaya düz kay; çözüm yoksa izleyiciye bırak."""
        q = -self.robot.dingil_x_m
        c, s_ = math.cos(poz[2]), math.sin(poz[2])
        rx, ry = poz[0] - q * c, poz[1] - q * s_
        hedef_yon = math.atan2(k.hedef[1] - ry, k.hedef[0] - rx)
        e = _sar(hedef_yon - poz[2])
        yon = math.copysign(1.0, k.w) if abs(k.w) > 1e-6 else math.copysign(1.0, e)
        d1 = e if e * yon >= 0 else e + yon * 2 * math.pi
        d2 = d1 - yon * 2 * math.pi
        if not self._supurme_carpar(poz, d1):
            self._donus_onay = True
            return None
        if not self._supurme_carpar(poz, d2):
            self._bak, self._bak_yon = hedef_yon, -yon
            self.sayac["donus_ters"] += 1
            return "ters"
        km = self.ayar.donus_kay_m
        for sm in sorted(np.arange(-km, km + 0.001, 0.05), key=abs):
            if abs(sm) < 0.04:
                continue
            p2 = (poz[0] + sm * c, poz[1] + sm * s_, poz[2])
            if self._start_uzaklik(p2) < self.ayar.start_dur_m or self._duz_carpar(poz, sm):
                continue
            if not self._supurme_carpar(p2, d1) or not self._supurme_carpar(p2, d2):
                self._kay = {"t0": self.t, "bas": poz, "s": float(sm)}
                self.sayac["donus_kay"] += 1
                self.mod = "konumlan"
                return "kay"
        self.sayac["donus_sigmaz"] += 1
        if self.ayar.donus_sigmaz_geri:
            # v5: körlemesine dönme yerine önce geri çekil ve yeniden planla; aynı yerde (0,3 m) 20 s içinde ikinci kez
            # sığmazsa eski davranış (izleyiciye bırak; v3 / v4'ün takılmama güvencesi)
            son = getattr(self, "_sigmaz_son", None)
            ayni = son is not None and self.t - son[0] < 20.0 and math.hypot(poz[0] - son[1], poz[1] - son[2]) < 0.3
            if not ayni:
                self._sigmaz_son = (self.t, poz[0], poz[1])
                self.sayac["donus_geri"] = self.sayac.get("donus_geri", 0) + 1
                self._kurtarma_baslat(self.t, "donus_sigmaz")
                return "geri"
            self.sayac["donus_kor"] = self.sayac.get("donus_kor", 0) + 1
        self._donus_onay = True
        return None

    def _kay_adim(self, t, poz):
        k = self._kay
        b = k["bas"]
        c, s_ = math.cos(b[2]), math.sin(b[2])
        gidilen = (poz[0] - b[0]) * c + (poz[1] - b[1]) * s_
        kalan = k["s"] - gidilen
        bitti = abs(kalan) < 0.02 or t - k["t0"] > 6.0 or kalan * k["s"] < 0
        if not bitti and k["s"] > 0 and self.on_mesafe is not None and self.on_mesafe < 0.06:
            bitti = True
        if bitti:
            self._kay = None
            self.mod = "kesif"
            self._donus_onay = False
            self.izleyici.yol_ver(self.yol)    # bacakları bu pozdan yeniden kur
            return 0.0, 0.0
        v = math.copysign(min(0.12, 0.6 * abs(kalan) + 0.03), kalan)
        w = max(-0.3, min(0.3, 1.5 * _sar(b[2] - poz[2])))
        return v, w

    # ------------------------------------------------------------ sıkışma / kurtarma
    def _sikisti(self, t):
        g = self._gecmis
        S = self.ayar.sikisma_s
        if not g or g[-1][0] - g[0][0] < S:
            return False
        son = [p for p in g if p[0] >= t - S]
        if len(son) < 5:
            return False
        komut = np.mean([abs(p[4]) for p in son]) > 0.05 or np.mean([abs(p[5]) for p in son]) > 0.3
        x = np.array([p[1] for p in son])
        y = np.array([p[2] for p in son])
        th = np.unwrap(np.array([p[3] for p in son]))
        # pencere başından en büyük uzaklaşma (son noktanın net yer değiştirmesi değil: geri çekil + ileri git
        # döngüsünde net ~0 olur, kurtarma kendini yeniden tetikliyordu; MuJoCo 9x9_t2'de 40 kurtarma). Yol uzunluğu
        # da değil: SLAM pozunun tarama başına titremesi takılı robotu "hareketli" gösterir.
        hareket = (float(np.hypot(x - x[0], y - y[0]).max()) > 0.05
                   or float(np.abs(th - th[0]).max()) > 0.15)
        return komut and not hareket

    def _kurtarma_baslat(self, t, neden):
        self.sayac["kurtarma"] += 1
        self.olaylar.append((round(t, 1), "kurtarma", neden))
        poz = self.slam.poz
        # geri gidilecek yer haritada boş mu (arka kör sektör: yalnız harita)
        kh = KabaHarita(self.slam.izgara, self.ayar.plan)
        c, s = math.cos(poz[2]), math.sin(poz[2])
        geri_ok = True
        for d in (0.1, 0.2, 0.3):
            gx, gy = poz[0] - (d + 0.264) * c, poz[1] - (d + 0.264) * s
            a = kh.acik_oku(np.array([gx]), np.array([gy]))[0]
            i, j = kh.hucre(gx, gy)
            if a < 0.22 or not (kh.icinde(i, j) and kh.bos[i, j]) or self._start_uzaklik(
                    (poz[0] - d * c, poz[1] - d * s, poz[2])) < self.ayar.start_dur_m:
                geri_ok = False
                break
        self._kurtarma = {"t0": t, "baslangic": poz, "geri": geri_ok, "neden": neden}
        self.mod = "kurtarma"
        if self.hedef_sinir is not None and neden == "sikisma":
            s_ = self.hedef_sinir
            self.kara_liste.append((s_.merkez[0], s_.merkez[1], t + self.ayar.kara_liste_s * 0.5))
        self._gecmis.clear()

    def _kurtarma_adim(self, t, poz):
        k = self._kurtarma
        dt = t - k["t0"]
        b = k["baslangic"]
        gidilen = math.hypot(poz[0] - b[0], poz[1] - b[1])
        if k["geri"] and gidilen < self.ayar.geri_m and dt < 4.0:
            return -0.08, 0.0
        self._kurtarma = None
        self.mod = "kesif"
        self.yol = []
        self.t_plan = -1e9
        self._gecmis.clear()           # sıkışma penceresi kurtarmadan sonra yeniden başlar
        return 0.0, 0.0

    # ------------------------------------------------------------ sınır kalmadı
    def _tukendi(self, t, poz):
        """Kademeli: (1) gevşet (r_min - 3 cm, kısa sınırlar), (2) zayıf duvarları unut, (3) duvar izleme."""
        self.yol = []
        self.izleyici.yol_ver([])
        if self.gevset == 0:
            self.gevset = 1
            self.ayar.sinir = SinirAyari(**{**self.ayar.sinir.__dict__,
                                            "min_genislik_m": self.ayar.sinir.min_genislik_m * 0.6})
            self.kara_liste = []
            self.olaylar.append((round(t, 1), "tukendi", "gevset"))
            self.t_plan = t - self.ayar.plan_aralik_s + 0.2
            self.mod = "tukendi"
            return
        if self.gevset == 1:
            self.gevset = 2
            L = self.slam.izgara.L
            zayif = (L > self.slam.izgara.esik_dolu) & (L < 1.6)
            L[zayif] = 0.0
            self.slam.izgara.surum += 1
            self.olaylar.append((round(t, 1), "tukendi", "unut:%d" % int(zayif.sum())))
            self.t_plan = t - self.ayar.plan_aralik_s + 1.0
            self.mod = "tukendi"
            return
        self.olaylar.append((round(t, 1), "tukendi", "duvar_izle"))
        from .taban import SagDuvar
        self._duvar = SagDuvar(self.robot, v=self.ayar.v_seyir * 0.8)
        self._duvar_t0 = t
        self.mod = "duvar_izle"

    def _duvar_adim(self, poz, yeni_tarama):
        nok = getattr(self.slam, "son_noktalar", None)
        if nok is None:
            return 0.0, 0.0
        x, y = nok
        # START sanal duvarını gövde çerçevesinde nokta olarak ekle
        (x1, y1), (x2, y2) = self.start
        ts = np.linspace(-0.3, 1.3, 40)
        wx = x1 + (x2 - x1) * ts
        wy = y1 + (y2 - y1) * ts
        c, s = math.cos(poz[2]), math.sin(poz[2])
        bx = c * (wx - poz[0]) + s * (wy - poz[1])
        by = -s * (wx - poz[0]) + c * (wy - poz[1])
        yakin = np.hypot(bx, by) < 3.0
        x = np.concatenate([x, bx[yakin]])
        y = np.concatenate([y, by[yakin]])
        return self._duvar.komut(x, y)


def olustur(sahne_adi=None, **kw):
    """Fabrika: sahne verilirse START çizgisi (yalnız o) başlangıç gövde çerçevesine çevrilip beyne verilir."""
    if sahne_adi is None:
        return KesifBeyni(**kw)
    from .sahne import beyin_start_cizgisi, sahne_yukle
    s = sahne_yukle(sahne_adi)
    return KesifBeyni(start_cizgisi=beyin_start_cizgisi(s), **kw)
