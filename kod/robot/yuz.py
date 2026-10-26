# Ne yapıyor: pygame ile ekrana robot yüzü çizer; ifade durum makinesindeki duruma göre değişir.
# Yalnız ilkel şekiller (daire, yay, çizgi, dikdörtgen); görsel dosyası yok. Altta son söylenen metin.
# pygame ana iş parçacığında çalışmak zorunda (calistir). pygame yoksa yüz sessizce kapalı kalır.

import math
import os
import time

from robot.durum import Durum

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

KARE_HIZI = 30               # saniyede çizim sayısı
KIRPMA_ARALIGI = 4.0         # BEKLE'de kaç saniyede bir göz kırpar
KIRPMA_SURESI = 0.15


class Olcu:
    """Ekran boyutuna göre yüzün yerleşimi; her şey ekran oranıyla, piksel sabiti yok."""

    def __init__(self, genislik, yukseklik):
        self.w = genislik
        self.h = yukseklik
        self.cx = genislik / 2
        self.goz_y = yukseklik * 0.38
        self.goz_ara = genislik * 0.17      # merkezden her göze uzaklık
        self.r = yukseklik * 0.11           # göz yarıçapı
        self.agiz_y = yukseklik * 0.62


# ---------- yüz parçaları ----------

def gozler(ekran, o, r, bebek_dy=0, kapali=False):
    for x in (o.cx - o.goz_ara, o.cx + o.goz_ara):
        if kapali:
            pygame.draw.line(ekran, BEYAZ, (x - r, o.goz_y), (x + r, o.goz_y), 8)
        else:
            pygame.draw.circle(ekran, BEYAZ, (x, o.goz_y), r)
            pygame.draw.circle(ekran, BEBEK, (x, o.goz_y + bebek_dy), r * 0.45)


def mutlu_gozler(ekran, o):
    # Yayın üst yarısı: "^ ^" gibi gülen gözler
    for x in (o.cx - o.goz_ara, o.cx + o.goz_ara):
        kutu = pygame.Rect(x - o.r, o.goz_y - o.r * 0.5, o.r * 2, o.r * 1.5)
        pygame.draw.arc(ekran, BEYAZ, kutu, 0, math.pi, 10)


def agiz_duz(ekran, o):
    pygame.draw.line(ekran, BEYAZ, (o.cx - o.r * 0.8, o.agiz_y), (o.cx + o.r * 0.8, o.agiz_y), 8)


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


def uc_nokta(ekran, o, t):
    adet = int(t * 3) % 4          # 0, 1, 2, 3 nokta sırayla
    for i in range(adet):
        pygame.draw.circle(ekran, VURGU, (o.cx - o.r * 0.6 + i * o.r * 0.6, o.agiz_y), o.r * 0.12)


# ---------- durumlara göre ifadeler ----------

def ciz_bekle(ekran, o, t):
    kirpiyor = (t % KIRPMA_ARALIGI) < KIRPMA_SURESI
    gozler(ekran, o, o.r, kapali=kirpiyor)
    agiz_duz(ekran, o)


def ciz_dinle(ekran, o, t):
    gozler(ekran, o, o.r * 1.25)
    agiz_duz(ekran, o)
    mikrofon_simgesi(ekran, o)


def ciz_dusun(ekran, o, t):
    gozler(ekran, o, o.r, bebek_dy=-o.r * 0.45)   # gözler yukarı bakar
    uc_nokta(ekran, o, t)


def ciz_konus(ekran, o, t):
    gozler(ekran, o, o.r)
    agiz_acik(ekran, o, abs(math.sin(t * 12)) * o.r * 0.6 + 6)   # ağız açılıp kapanır


def ciz_jest(ekran, o, t):
    mutlu_gozler(ekran, o)
    gulumseme(ekran, o)


CIZICILER = {
    Durum.BEKLE: ciz_bekle,
    Durum.DINLE: ciz_dinle,
    Durum.DUSUN: ciz_dusun,
    Durum.KONUS: ciz_konus,
    Durum.JEST: ciz_jest,
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
    for i, satir in enumerate(satirlara_bol(metin, yazi_tipi, o.w * 0.9)[:3]):
        yuzey = yazi_tipi.render(satir, True, BEYAZ)
        ekran.blit(yuzey, yuzey.get_rect(center=(o.cx, o.h * 0.80 + i * satir_yuksekligi)))


def yuz_ciz(ekran, durum, t, yazi_tipi, metin=""):
    """Bir kare çizer. Pencere olmadan da (ör. testte bir Surface üzerine) çağrılabilir."""
    o = Olcu(*ekran.get_size())
    ekran.fill(ARKA)
    CIZICILER[durum](ekran, o, t)
    ekran.blit(yazi_tipi.render(durum.value, True, SOLUK), (16, 12))
    if metin:
        alt_yazi_ciz(ekran, o, yazi_tipi, metin)


# ---------- pencere ----------

class Yuz:
    def __init__(self, genislik=1280, yukseklik=800, tam_ekran=False):
        self.boyut = (genislik, yukseklik)
        self.tam_ekran = tam_ekran
        self.etkin = pygame is not None
        self.durum = Durum.BEKLE
        self.metin = ""

    def durum_degisti(self, eski, yeni):
        """Durum makinesinin dinleyicisi. Konuşma iş parçacığından çağrılır; yalnız değer yazar."""
        self.durum = yeni

    def metin_goster(self, metin):
        self.metin = metin

    def calistir(self, durdur, deneme_saniye=None):
        """ANA iş parçacığında çağrılmalı. ESC ya da pencere kapatma durdur olayını kurar.
        deneme_saniye verilirse yüz tüm ifadeleri sırayla gösterip o kadar saniye sonra kapanır."""
        if not self.etkin:
            return
        pygame.init()
        bayrak = pygame.FULLSCREEN if self.tam_ekran else 0
        ekran = pygame.display.set_mode(self.boyut, bayrak)
        pygame.display.set_caption("Robot yüzü")
        if self.tam_ekran:
            pygame.mouse.set_visible(False)
        yazi_tipi = pygame.font.SysFont("dejavusans,arial,freesans", int(self.boyut[1] * 0.045))
        saat = pygame.time.Clock()
        baslangic = time.monotonic()
        try:
            while not durdur.is_set():
                self._olaylari_isle(durdur)
                gecen = time.monotonic() - baslangic
                durum = self.durum
                if deneme_saniye:
                    if gecen >= deneme_saniye:
                        durdur.set()
                    durum = deneme_durumu(gecen, deneme_saniye)
                yuz_ciz(ekran, durum, gecen, yazi_tipi, self.metin)
                pygame.display.flip()
                saat.tick(KARE_HIZI)
        finally:
            pygame.quit()

    def _olaylari_isle(self, durdur):
        for olay in pygame.event.get():
            if olay.type == pygame.QUIT:
                durdur.set()
            elif olay.type == pygame.KEYDOWN and olay.key == pygame.K_ESCAPE:
                durdur.set()


def deneme_durumu(gecen, toplam):
    """Deneme modunda süreyi beş eşit parçaya bölüp her parçada bir ifade gösterir."""
    durumlar = list(Durum)
    sira = int(gecen / (toplam / len(durumlar)))
    return durumlar[min(sira, len(durumlar) - 1)]
