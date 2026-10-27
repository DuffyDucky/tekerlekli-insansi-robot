# Ne yapıyor: pygame ile ekrana robot yüzü çizer; ifade durum makinesindeki duruma göre değişir.
# Yalnız ilkel şekiller; görsel dosyası yok. Altta son söylenen metin; dokunma tetiğinde en altta
# "Konuşmak için dokun" alanı, --gelistirici'de soru yazma kutusu. pygame ana iş parçacığında çalışmak
# zorunda (calistir); konuşma iş parçacığıyla bağ kuyruklar (DokunmaTetik, EkranSTT). pygame yoksa yüz kapalı.
# İfadeler: BEKLE'de bakış yavaşça gezinir ve gözler 3-6 s'de bir kırpar, DİNLE'de gözler büyük ve kaşlar kalkık,
# DÜŞÜN'de gözler yukarıda kayar + noktalar, KONUŞ'ta ağız metnin harflerine göre açılıp kapanır, BAKIM'da yarı
# kapalı gözler + dönen dişli. Kareler arası animasyon Ifade sınıfında (pygame'siz de çalışır); bakis_hedefi(x, y)
# gözleri bir yöne çevirir (şimdilik dokunulan yere bakar; ileride kamera kişinin yönünü verecek).
# Pi 5'te 30 fps hedefi: yalnız ilkel şekiller, yazı yüzeyleri önbellekte (her karede yeni yüzey yaratılmaz).

import math
import os
import random
import time

from robot.durum import Durum
from robot.icerik import turkce_kucuk

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")   # pygame'in açılış yazısını gizle
try:
    import pygame
except ImportError:          # test ortamında ya da kurulmamışsa
    pygame = None

ARKA = (12, 18, 32)          # koyu lacivert arka plan
BEYAZ = (235, 245, 255)      # göz ve ağız
BEBEK = (20, 30, 50)         # göz bebeği
VURGU = (80, 200, 255)       # açık mavi: simgeler ve noktalar
SOLUK = (110, 120, 140)      # köşedeki durum yazısı
DUGME = (28, 52, 90)         # dokunma alanının dolgusu
KUTU = (240, 245, 252)       # metin kutusu zemini
KUTU_YAZI = (20, 30, 50)     # metin kutusundaki yazı

DOKUN_YAZISI = "Konuşmak için dokun"
KUTU_IPUCU = "Sorunuzu yazın, Enter ile gönderin"
AZAMI_HARF = 120             # metin kutusuna en fazla kaç harf yazılabilir

KARE_HIZI = 30               # saniyede çizim sayısı
KIRPMA_ARALIGI = (3.0, 6.0)  # BEKLE'de göz kırpma aralığı (saniye, her seferinde rastgele)
KIRPMA_SURESI = 0.15
GEZINME_ARALIGI = (2.0, 5.0) # BEKLE'de bakış kaç saniyede bir yeni bir noktaya kayar
GEZINME_GENISLIGI = 0.5      # gezinirken bakış en fazla bu kadar yana kayar (-1..1 ölçeğinde)
BAKIS_HIZI = 3.0             # bakış hedefe ne hızla yaklaşır (1/s; büyük = hızlı)
ELLE_BAKIS_SURESI = 2.5      # bakis_hedefi ile verilen yöne kaç saniye bakılır
HARF_HIZI = 14.0             # KONUŞ'ta ağız animasyonu: saniyede kaç harf (Piper Türkçe için TAHMİNİ)
AGIZ_HIZI = 18.0             # ağız açıklığının harfe yetişme hızı (1/s)
SESLI_HARFLER = set("aeıioöuüâîû")


class Olcu:
    """Ekran boyutuna göre yüzün yerleşimi; her şey ekran oranıyla, piksel sabiti yok.
    alt_alan=True ise en alttaki şerit dokunma alanı / metin kutusuna ayrılır, yüz biraz yukarı kayar."""

    def __init__(self, genislik, yukseklik, alt_alan=False):
        self.w = genislik
        self.h = yukseklik
        self.cx = genislik / 2
        self.goz_ara = genislik * 0.17      # merkezden her göze uzaklık
        self.r = yukseklik * 0.11           # göz yarıçapı
        if alt_alan:
            self.goz_y, self.agiz_y, self.metin_y = yukseklik * 0.30, yukseklik * 0.52, yukseklik * 0.66
        else:
            self.goz_y, self.agiz_y, self.metin_y = yukseklik * 0.38, yukseklik * 0.62, yukseklik * 0.80


def alt_alan(o):
    """En alttaki şerit (x, y, genişlik, yükseklik): dokunma alanı ve metin kutusu burada."""
    return (o.w * 0.10, o.h * 0.84, o.w * 0.80, o.h * 0.12)


def alanda_mi(o, x, y):
    """(x, y) noktası alt şeridin içinde mi? Dokunma ve tıklama için."""
    ax, ay, gen, yuk = alt_alan(o)
    return ax <= x <= ax + gen and ay <= y <= ay + yuk


# ---------- animasyon durumu (pygame gerektirmez) ----------

def sinirla(deger, alt=-1.0, ust=1.0):
    return max(alt, min(ust, deger))


class Ifade:
    """Kareden kareye süren yüz animasyonu: bakışın yönü (BEKLE'de yavaşça gezinir, DÜŞÜN'de yukarıda
    kayar, bakis_hedefi ile bir noktaya bakar), göz kırpma (BEKLE'de 3-6 s'de bir) ve KONUŞ'ta ağız açıklığı.
    Her karede guncelle(t, durum, metin) çağrılır; çizim fonksiyonları yalnız buradaki değerleri okur.
    tohum: testte aynı rastgele sıra."""

    def __init__(self, tohum=None):
        self.rastgele = random.Random(tohum)
        self.bakis = [0.0, 0.0]         # göz bebeğinin yönü: x -1 sol .. +1 sağ, y -1 yukarı .. +1 aşağı
        self.gezinme = (0.0, 0.0)       # BEKLE'de o an bakılan rastgele nokta
        self.sonraki_gezinme = None
        self.sonraki_kirpma = None
        self.kirpma_bitis = -1.0
        self.kirpiyor = False
        self.agiz = 0.0                 # KONUŞ'ta ağız açıklığı 0-1
        self.elle_hedef = None          # bakis_hedefi ile verilen nokta
        self.elle_bitis = 0.0
        self.istenen = None             # başka iş parçacığından gelen bakış isteği (guncelle'de işlenir)
        self.durum = None
        self.durum_baslangic = 0.0
        self.son_t = None

    def bakis_hedefi(self, x, y, sure=ELLE_BAKIS_SURESI):
        """Gözler 'sure' saniye (x, y) yönüne baksın (x -1 sol .. +1 sağ, y -1 yukarı .. +1 aşağı).
        Her iş parçacığından çağrılabilir (yalnız bir değer yazar). İleride kamera kişinin yönünü verecek."""
        self.istenen = (sinirla(x), sinirla(y), sure)

    def guncelle(self, t, durum, metin=""):
        dt = 0.0 if self.son_t is None else max(0.0, min(t - self.son_t, 0.2))   # takılmada sıçramasın
        self.son_t = t
        if durum != self.durum:
            self.durum, self.durum_baslangic = durum, t
        istenen, self.istenen = self.istenen, None
        if istenen is not None:
            self.elle_hedef, self.elle_bitis = istenen[:2], t + istenen[2]
        hedef = self.hedef_sec(t, durum)
        oran = min(1.0, dt * BAKIS_HIZI)        # hedefe yumuşakça yaklaşır (birinci derece süzgeç)
        self.bakis[0] += (hedef[0] - self.bakis[0]) * oran
        self.bakis[1] += (hedef[1] - self.bakis[1]) * oran
        self.kirpma_guncelle(t, durum)
        agiz_hedef = self.agiz_hedefi(t, metin) if durum == Durum.KONUS else 0.0
        self.agiz += (agiz_hedef - self.agiz) * min(1.0, dt * AGIZ_HIZI)

    def hedef_sec(self, t, durum):
        if self.elle_hedef is not None and t < self.elle_bitis:
            return self.elle_hedef
        if durum == Durum.BEKLE:
            if self.sonraki_gezinme is None or t >= self.sonraki_gezinme:
                g = GEZINME_GENISLIGI
                self.gezinme = (self.rastgele.uniform(-g, g), self.rastgele.uniform(-g * 0.6, g * 0.6))
                self.sonraki_gezinme = t + self.rastgele.uniform(*GEZINME_ARALIGI)
            return self.gezinme
        if durum == Durum.DUSUN:
            # Düşünürken gözler yukarıda, yavaşça bir yana bir yana kayar
            return (0.6 * math.sin((t - self.durum_baslangic) * 1.5), -0.7)
        if durum == Durum.BAKIM:
            return (0.0, 0.4)                    # hafif aşağı bakar
        return (0.0, 0.0)                        # DİNLE, KONUŞ, JEST: karşıdaki kişiye bakar

    def kirpma_guncelle(self, t, durum):
        if durum != Durum.BEKLE:
            self.kirpiyor = False
            self.sonraki_kirpma = None           # BEKLE'ye dönünce yeniden kurulur
            return
        if self.sonraki_kirpma is None:
            self.sonraki_kirpma = t + self.rastgele.uniform(*KIRPMA_ARALIGI)
        if t >= self.sonraki_kirpma:
            self.kirpma_bitis = t + KIRPMA_SURESI
            self.sonraki_kirpma = t + self.rastgele.uniform(*KIRPMA_ARALIGI)
        self.kirpiyor = t < self.kirpma_bitis

    def agiz_hedefi(self, t, metin):
        """Metin harf harf okunuyormuş gibi: sesli harfte ağız geniş, ünsüzde dar, boşluk/noktalamada kapalı.
        Metnin tahmini süresi (uzunluk / HARF_HIZI) bitince kapanır."""
        sira = int((t - self.durum_baslangic) * HARF_HIZI)
        if not metin or sira >= len(metin):
            return 0.0
        harf = turkce_kucuk(metin[sira])
        if harf in SESLI_HARFLER:
            return 1.0
        return 0.35 if harf.isalpha() else 0.0


# ---------- yazı önbelleği (her karede yeni yüzey yaratmamak için) ----------

class YaziOnbellegi:
    """render() her çağrıda yeni bir Surface yaratır; aynı yazı her karede yeniden çizilmesin diye
    (yazı tipi, metin, renk) -> yüzey saklanır. Dolunca temizlenir (yazılar az ve kısa)."""

    AZAMI = 64

    def __init__(self):
        self.yuzeyler = {}
        self.bolunmus = {}

    def yuzey(self, yazi_tipi, metin, renk):
        anahtar = (yazi_tipi, metin, renk)
        yuzey = self.yuzeyler.get(anahtar)
        if yuzey is None:
            if len(self.yuzeyler) >= self.AZAMI:
                self.yuzeyler.clear()
            yuzey = self.yuzeyler[anahtar] = yazi_tipi.render(metin, True, renk)
        return yuzey

    def satirlar(self, yazi_tipi, metin, genislik):
        anahtar = (yazi_tipi, metin, genislik)
        satirlar = self.bolunmus.get(anahtar)
        if satirlar is None:
            if len(self.bolunmus) >= self.AZAMI:
                self.bolunmus.clear()
            satirlar = self.bolunmus[anahtar] = satirlara_bol(metin, yazi_tipi, genislik)
        return satirlar


ONBELLEK = YaziOnbellegi()


# ---------- yüz parçaları ----------

def gozler(ekran, o, r, bakis=(0.0, 0.0), kapali=False):
    """İki göz; göz bebeği bakış yönüne kayar (en fazla yarıçapın yarısı, göz dışına taşmaz)."""
    for x in (o.cx - o.goz_ara, o.cx + o.goz_ara):
        if kapali:
            pygame.draw.line(ekran, BEYAZ, (x - r, o.goz_y), (x + r, o.goz_y), 8)
        else:
            pygame.draw.circle(ekran, BEYAZ, (x, o.goz_y), r)
            pygame.draw.circle(ekran, BEBEK, (x + bakis[0] * r * 0.5, o.goz_y + bakis[1] * r * 0.5), r * 0.45)


def kaslar(ekran, o, r):
    """DİNLE'de hafif kalkık kaşlar: gözlerin üstünde ince yaylar."""
    for x in (o.cx - o.goz_ara, o.cx + o.goz_ara):
        kutu = pygame.Rect(x - r * 0.9, o.goz_y - r * 1.75, r * 1.8, r * 0.8)
        pygame.draw.arc(ekran, BEYAZ, kutu, math.pi * 0.15, math.pi * 0.85, 6)


def mutlu_gozler(ekran, o):
    # Yayın üst yarısı: "^ ^" gibi gülen gözler
    for x in (o.cx - o.goz_ara, o.cx + o.goz_ara):
        kutu = pygame.Rect(x - o.r, o.goz_y - o.r * 0.5, o.r * 2, o.r * 1.5)
        pygame.draw.arc(ekran, BEYAZ, kutu, 0, math.pi, 10)


def agiz_duz(ekran, o, genislik=0.8):
    pygame.draw.line(ekran, BEYAZ, (o.cx - o.r * genislik, o.agiz_y), (o.cx + o.r * genislik, o.agiz_y), 8)


def agiz_acik(ekran, o, yukseklik):
    kutu = pygame.Rect(0, 0, o.r * 1.2, yukseklik)
    kutu.center = (o.cx, o.agiz_y)
    pygame.draw.ellipse(ekran, BEYAZ, kutu)


def gulumseme(ekran, o):
    # Yayın alt yarısı: gülümseyen ağız
    kutu = pygame.Rect(o.cx - o.r * 1.4, o.agiz_y - o.r, o.r * 2.8, o.r * 1.6)
    pygame.draw.arc(ekran, BEYAZ, kutu, math.pi, 2 * math.pi, 10)


def mikrofon_simgesi(ekran, o):
    x, y = o.w * 0.88, o.h * 0.15
    pygame.draw.rect(ekran, VURGU, pygame.Rect(x - 15, y - 35, 30, 55), border_radius=15)
    pygame.draw.arc(ekran, VURGU, pygame.Rect(x - 28, y - 20, 56, 50), math.pi, 2 * math.pi, 4)
    pygame.draw.line(ekran, VURGU, (x, y + 30), (x, y + 45), 4)
    pygame.draw.line(ekran, VURGU, (x - 15, y + 45), (x + 15, y + 45), 4)


def disli_simgesi(ekran, o, t):
    """BAKIM'da sağ üstte yavaş dönen dişli: 8 diş, ortası delik."""
    x, y, dis_r = o.w * 0.88, o.h * 0.15, o.h * 0.06
    aci0 = t * 0.6
    noktalar = []
    for i in range(32):                              # her diş 4 nokta: dış, dış, iç, iç
        aci = aci0 + i * math.pi / 16
        yaricap = dis_r if (i // 2) % 2 == 0 else dis_r * 0.75
        noktalar.append((x + yaricap * math.cos(aci), y + yaricap * math.sin(aci)))
    pygame.draw.polygon(ekran, VURGU, noktalar)
    pygame.draw.circle(ekran, ARKA, (x, y), dis_r * 0.3)


def uc_nokta(ekran, o, t):
    adet = int(t * 3) % 4          # 0, 1, 2, 3 nokta sırayla
    for i in range(adet):
        pygame.draw.circle(ekran, VURGU, (o.cx - o.r * 0.6 + i * o.r * 0.6, o.agiz_y), o.r * 0.12)


# ---------- durumlara göre ifadeler ----------

def ciz_bekle(ekran, o, t, ifade):
    gozler(ekran, o, o.r, ifade.bakis, kapali=ifade.kirpiyor)
    agiz_duz(ekran, o)


def ciz_dinle(ekran, o, t, ifade):
    gozler(ekran, o, o.r * 1.25, ifade.bakis)       # "dinliyorum": gözler büyük, kaşlar hafif kalkık
    kaslar(ekran, o, o.r * 1.25)
    agiz_duz(ekran, o, 0.6)
    mikrofon_simgesi(ekran, o)


def ciz_dusun(ekran, o, t, ifade):
    gozler(ekran, o, o.r, ifade.bakis)              # gözler yukarıda bir yana bir yana kayar
    uc_nokta(ekran, o, t)


def ciz_konus(ekran, o, t, ifade):
    gozler(ekran, o, o.r, ifade.bakis)
    agiz_acik(ekran, o, ifade.agiz * o.r * 0.7 + 6)  # açıklık metnin harflerine göre (Ifade.agiz_hedefi)


def ciz_jest(ekran, o, t, ifade):
    mutlu_gozler(ekran, o)
    gulumseme(ekran, o)


def ciz_bakim(ekran, o, t, ifade):
    # Yarı kapalı gözler (alt yarım daire) + düz ağız + dönen dişli
    for x in (o.cx - o.goz_ara, o.cx + o.goz_ara):
        kutu = pygame.Rect(x - o.r, o.goz_y - o.r, o.r * 2, o.r * 2)
        pygame.draw.arc(ekran, BEYAZ, kutu, math.pi, 2 * math.pi, 10)
        pygame.draw.line(ekran, BEYAZ, (x - o.r, o.goz_y), (x + o.r, o.goz_y), 6)
    agiz_duz(ekran, o, 0.5)
    disli_simgesi(ekran, o, t)


CIZICILER = {
    Durum.BEKLE: ciz_bekle,
    Durum.DINLE: ciz_dinle,
    Durum.DUSUN: ciz_dusun,
    Durum.KONUS: ciz_konus,
    Durum.JEST: ciz_jest,
    Durum.BAKIM: ciz_bakim,
}


def satirlara_bol(metin, yazi_tipi, genislik):
    """Metni ekrana sığacak satırlara böler."""
    satirlar, satir = [], ""
    for kelime in metin.split():
        deneme = (satir + " " + kelime).strip()
        if yazi_tipi.size(deneme)[0] <= genislik or not satir:
            satir = deneme
        else:
            satirlar.append(satir)
            satir = kelime
    if satir:
        satirlar.append(satir)
    return satirlar


def alt_yazi_ciz(ekran, o, yazi_tipi, metin):
    satir_yuksekligi = yazi_tipi.get_linesize()
    for i, satir in enumerate(ONBELLEK.satirlar(yazi_tipi, metin, int(o.w * 0.9))[:3]):
        yuzey = ONBELLEK.yuzey(yazi_tipi, satir, BEYAZ)
        ekran.blit(yuzey, yuzey.get_rect(center=(o.cx, o.metin_y + i * satir_yuksekligi)))


def dokunma_alani_ciz(ekran, o, yazi_tipi):
    """BEKLE'de en altta büyük, yuvarlak köşeli 'Konuşmak için dokun' düğmesi."""
    kutu = pygame.Rect(alt_alan(o))
    pygame.draw.rect(ekran, DUGME, kutu, border_radius=kutu.h // 2)
    pygame.draw.rect(ekran, VURGU, kutu, 3, border_radius=kutu.h // 2)
    yazi = ONBELLEK.yuzey(yazi_tipi, DOKUN_YAZISI, BEYAZ)
    ekran.blit(yazi, yazi.get_rect(center=kutu.center))


def metin_kutusu_ciz(ekran, o, yazi_tipi, metin, t):
    """DİNLE'de soru yazma kutusu. Boşken ipucu; yazı sığmazsa sondaki kısmı gösterilir."""
    kutu = pygame.Rect(alt_alan(o))
    pygame.draw.rect(ekran, KUTU, kutu, border_radius=12)
    pygame.draw.rect(ekran, VURGU, kutu, 3, border_radius=12)
    if not metin:
        yazi = ONBELLEK.yuzey(yazi_tipi, KUTU_IPUCU, SOLUK)
        ekran.blit(yazi, yazi.get_rect(midleft=(kutu.x + 20, kutu.centery)))
        return
    imlec = "|" if int(t * 2) % 2 == 0 else " "   # yarım saniyede bir yanıp söner
    gorunen = metin
    while len(gorunen) > 1 and yazi_tipi.size(gorunen + imlec)[0] > kutu.w - 40:
        gorunen = gorunen[1:]
    yazi = ONBELLEK.yuzey(yazi_tipi, gorunen + imlec, KUTU_YAZI)
    ekran.blit(yazi, yazi.get_rect(midleft=(kutu.x + 20, kutu.centery)))


def yuz_ciz(ekran, durum, t, yazi_tipi, metin="", alt_alan_var=False, ifade=None):
    """Bir kare çizer. Pencere olmadan da (ör. testte bir Surface üzerine) çağrılabilir.
    ifade: kareler arası animasyon durumu (Yuz kendi Ifade'sini verir); None ise o kare için yenisi.
    Yerleşim ölçülerini (Olcu) döner; alt şeridi Yuz ayrıca çizer."""
    o = Olcu(*ekran.get_size(), alt_alan_var)
    if ifade is None:
        ifade = Ifade()
    ifade.guncelle(t, durum, metin)
    ekran.fill(ARKA)
    CIZICILER[durum](ekran, o, t, ifade)
    ekran.blit(ONBELLEK.yuzey(yazi_tipi, durum.value, SOLUK), (16, 12))
    if metin:
        alt_yazi_ciz(ekran, o, yazi_tipi, metin)
    return o


def ekrandan_bakis(konum, ekran_boyutu):
    """Ekrandaki bir noktayı (piksel) bakış yönüne (-1..1) çevirir: dokunulan yere bakmak için."""
    w, h = ekran_boyutu
    return sinirla((konum[0] - w / 2) / (w / 2)), sinirla((konum[1] - h * 0.38) / (h / 2))


# ---------- pencere ----------

class Yuz:
    def __init__(self, genislik=1280, yukseklik=800, tam_ekran=False):
        self.boyut = (genislik, yukseklik)
        self.tam_ekran = tam_ekran
        self.etkin = pygame is not None
        self.durum = Durum.BEKLE
        self.metin = ""
        # Ekrandan girdi (ana.py bağlar). İkisi de kuyruklu nesne; yüz yalnız onlara bir şey koyar.
        self.dokunma_tetik = None   # DokunmaTetik: BEKLE'de alt alana dokununca dokunuldu()
        self.yazi_alici = None      # EkranSTT: DİNLE'de metin kutusunda Enter'a basınca gonder(metin)
        self.yazi = ""              # metin kutusunda o an yazılı olan (yalnız ana iş parçacığı değiştirir)
        self.ifade = Ifade()        # bakış, göz kırpma, ağız: kareden kareye süren animasyon

    def bakis_hedefi(self, x, y, sure=ELLE_BAKIS_SURESI):
        """Gözleri (x, y) yönüne çevirir: x -1 sol .. +1 sağ, y -1 yukarı .. +1 aşağı. Her iş parçacığından
        çağrılabilir. Şimdilik dokunulan yere bakmak için; ileride kamera kişinin yönünü buradan verecek."""
        self.ifade.bakis_hedefi(x, y, sure)

    def durum_degisti(self, eski, yeni):
        """Durum makinesinin dinleyicisi. Konuşma iş parçacığından çağrılır; yalnız değer yazar."""
        self.durum = yeni

    def metin_goster(self, metin):
        self.metin = metin

    @property
    def alt_alan_var(self):
        return self.dokunma_tetik is not None or self.yazi_alici is not None

    def pencere_ac(self):
        """pygame'i başlatır, pencereyi açar, ekran yüzeyini döner. ANA iş parçacığında çağrılmalı."""
        pygame.init()
        bayrak = pygame.FULLSCREEN if self.tam_ekran else 0
        ekran = pygame.display.set_mode(self.boyut, bayrak)
        pygame.display.set_caption("Robot yüzü")
        if self.tam_ekran:
            pygame.mouse.set_visible(False)       # dokunmatikte imleç gerekmez
        pygame.key.start_text_input()             # TEXTINPUT olayları: ı, ğ, ş, İ gibi harfler doğru gelir
        pygame.key.set_repeat(400, 40)            # Backspace basılı tutulunca art arda siler
        self.yazi_tipi = pygame.font.SysFont("dejavusans,arial,freesans", int(self.boyut[1] * 0.045))
        return ekran

    def calistir(self, durdur, deneme_saniye=None):
        """ANA iş parçacığında çağrılmalı. ESC ya da pencere kapatma durdur olayını kurar.
        deneme_saniye verilirse yüz tüm ifadeleri sırayla gösterip o kadar saniye sonra kapanır."""
        if not self.etkin:
            return
        ekran = self.pencere_ac()
        saat = pygame.time.Clock()
        baslangic = time.monotonic()
        try:
            while not durdur.is_set():
                self._olaylari_isle(durdur, ekran.get_size())
                gecen = time.monotonic() - baslangic
                durum = self.durum
                if deneme_saniye:
                    if gecen >= deneme_saniye:
                        durdur.set()
                    durum = deneme_durumu(gecen, deneme_saniye)
                self.kare_ciz(ekran, durum, gecen)
                pygame.display.flip()
                saat.tick(KARE_HIZI)
        finally:
            pygame.quit()

    def kare_ciz(self, ekran, durum, t):
        """Yüzü, alt yazıyı ve duruma göre alt şeridi (dokunma alanı ya da metin kutusu) çizer."""
        o = yuz_ciz(ekran, durum, t, self.yazi_tipi, self.metin, self.alt_alan_var, self.ifade)
        if durum == Durum.BEKLE and self.dokunma_tetik is not None:
            dokunma_alani_ciz(ekran, o, self.yazi_tipi)
        elif durum == Durum.DINLE and self.yazi_alici is not None:
            metin_kutusu_ciz(ekran, o, self.yazi_tipi, self.yazi, t)

    # ---------- olaylar (yalnız ana iş parçacığı) ----------

    def _olaylari_isle(self, durdur, ekran_boyutu):
        for olay in pygame.event.get():
            if olay.type == pygame.QUIT:
                durdur.set()
            elif olay.type == pygame.KEYDOWN and olay.key == pygame.K_ESCAPE:
                durdur.set()
            elif olay.type == pygame.MOUSEBUTTONDOWN and not getattr(olay, "touch", False):
                self.dokunma(olay.pos, ekran_boyutu)          # fare tıklaması
            elif olay.type == pygame.FINGERDOWN:
                # Parmak konumu 0-1 arası gelir; piksele çevir
                self.dokunma((olay.x * ekran_boyutu[0], olay.y * ekran_boyutu[1]), ekran_boyutu)
            elif olay.type == pygame.TEXTINPUT:
                self.yazi_ekle(olay.text)
            elif olay.type == pygame.KEYDOWN:
                self.tus(olay.key)

    def dokunma(self, konum, ekran_boyutu):
        """Gözler dokunulan yere bakar. BEKLE'deyken alt alana dokunulursa konuşma iş parçacığına haber verir."""
        self.bakis_hedefi(*ekrandan_bakis(konum, ekran_boyutu))
        if self.dokunma_tetik is None or self.durum != Durum.BEKLE:
            return
        if alanda_mi(Olcu(*ekran_boyutu, True), *konum):
            self.dokunma_tetik.dokunuldu()

    def kutu_acik_mi(self):
        return self.yazi_alici is not None and self.durum == Durum.DINLE

    def yazi_ekle(self, harfler):
        if self.kutu_acik_mi() and len(self.yazi) < AZAMI_HARF:
            self.yazi += harfler

    def tus(self, tus):
        if not self.kutu_acik_mi():
            return
        if tus in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.yazi_alici.gonder(self.yazi)    # soru konuşma iş parçacığına gider
            self.yazi = ""
        elif tus == pygame.K_BACKSPACE:
            self.yazi = self.yazi[:-1]


def deneme_durumu(gecen, toplam):
    """Deneme modunda süreyi durum sayısı kadar eşit parçaya bölüp her parçada bir ifade gösterir."""
    durumlar = list(Durum)
    sira = int(gecen / (toplam / len(durumlar)))
    return durumlar[min(sira, len(durumlar) - 1)]
