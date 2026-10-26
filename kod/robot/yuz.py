# Ne yapıyor: pygame ile ekrana robot yüzü çizer; ifade durum makinesindeki duruma göre değişir.
# Yalnız ilkel şekiller; görsel dosyası yok. Altta son söylenen metin; dokunma tetiğinde en altta
# "Konuşmak için dokun" alanı, --gelistirici'de soru yazma kutusu. pygame ana iş parçacığında çalışmak
# zorunda (calistir); konuşma iş parçacığıyla bağ kuyruklar (DokunmaTetik, EkranSTT). pygame yoksa yüz kapalı.

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
DUGME = (28, 52, 90)         # dokunma alanının dolgusu
KUTU = (240, 245, 252)       # metin kutusu zemini
KUTU_YAZI = (20, 30, 50)     # metin kutusundaki yazı

DOKUN_YAZISI = "Konuşmak için dokun"
KUTU_IPUCU = "Sorunuzu yazın, Enter ile gönderin"
AZAMI_HARF = 120             # metin kutusuna en fazla kaç harf yazılabilir

KARE_HIZI = 30               # saniyede çizim sayısı
KIRPMA_ARALIGI = 4.0         # BEKLE'de kaç saniyede bir göz kırpar
KIRPMA_SURESI = 0.15


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
        ekran.blit(yuzey, yuzey.get_rect(center=(o.cx, o.metin_y + i * satir_yuksekligi)))


def dokunma_alani_ciz(ekran, o, yazi_tipi):
    """BEKLE'de en altta büyük, yuvarlak köşeli 'Konuşmak için dokun' düğmesi."""
    kutu = pygame.Rect(alt_alan(o))
    pygame.draw.rect(ekran, DUGME, kutu, border_radius=kutu.h // 2)
    pygame.draw.rect(ekran, VURGU, kutu, 3, border_radius=kutu.h // 2)
    yazi = yazi_tipi.render(DOKUN_YAZISI, True, BEYAZ)
    ekran.blit(yazi, yazi.get_rect(center=kutu.center))


def metin_kutusu_ciz(ekran, o, yazi_tipi, metin, t):
    """DİNLE'de soru yazma kutusu. Boşken ipucu; yazı sığmazsa sondaki kısmı gösterilir."""
    kutu = pygame.Rect(alt_alan(o))
    pygame.draw.rect(ekran, KUTU, kutu, border_radius=12)
    pygame.draw.rect(ekran, VURGU, kutu, 3, border_radius=12)
    if not metin:
        yazi = yazi_tipi.render(KUTU_IPUCU, True, SOLUK)
        ekran.blit(yazi, yazi.get_rect(midleft=(kutu.x + 20, kutu.centery)))
        return
    imlec = "|" if int(t * 2) % 2 == 0 else " "   # yarım saniyede bir yanıp söner
    gorunen = metin
    while len(gorunen) > 1 and yazi_tipi.size(gorunen + imlec)[0] > kutu.w - 40:
        gorunen = gorunen[1:]
    yazi = yazi_tipi.render(gorunen + imlec, True, KUTU_YAZI)
    ekran.blit(yazi, yazi.get_rect(midleft=(kutu.x + 20, kutu.centery)))


def yuz_ciz(ekran, durum, t, yazi_tipi, metin="", alt_alan_var=False):
    """Bir kare çizer. Pencere olmadan da (ör. testte bir Surface üzerine) çağrılabilir.
    Yerleşim ölçülerini (Olcu) döner; alt şeridi Yuz ayrıca çizer."""
    o = Olcu(*ekran.get_size(), alt_alan_var)
    ekran.fill(ARKA)
    CIZICILER[durum](ekran, o, t)
    ekran.blit(yazi_tipi.render(durum.value, True, SOLUK), (16, 12))
    if metin:
        alt_yazi_ciz(ekran, o, yazi_tipi, metin)
    return o


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
        o = yuz_ciz(ekran, durum, t, self.yazi_tipi, self.metin, self.alt_alan_var)
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
        """BEKLE'deyken alt alana dokunulursa konuşma iş parçacığına haber verir."""
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
    """Deneme modunda süreyi beş eşit parçaya bölüp her parçada bir ifade gösterir."""
    durumlar = list(Durum)
    sira = int(gecen / (toplam / len(durumlar)))
    return durumlar[min(sira, len(durumlar) - 1)]
