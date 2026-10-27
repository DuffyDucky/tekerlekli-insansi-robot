# Ne yapıyor: konuşma tetikleyicisi. bekle() kullanıcı konuşmaya başlayana / dokunana / basana kadar bekler.
# SesTetik (varsayılan, düğmesiz) mikrofonda konuşma başlayınca tetikler. DokunmaTetik ekrandaki
# "Konuşmak için dokun" alanını, GpioTetik düğmeyi, KlavyeTetik terminalde Enter'ı bekler (geliştirici).
# zaman_asimli tetikler bekle(zaman_asimi) ile o kadar saniye sonra False döner (ana.py arada bakım moduna bakar);
# tetiklenince True. KlavyeTetik zaman aşımı bilmez (input() kesilemez).

import queue


def kuyrugu_bosalt(kuyruk):
    """Kuyrukta bekleyen eski öğeleri atar (ör. robot konuşurken yapılan dokunmalar)."""
    while True:
        try:
            kuyruk.get_nowait()
        except queue.Empty:
            return


class SesTetik:
    """Düğmesiz: BEKLE'de mikrofonu dinler, konuşma başlayınca tetikler. Konuşmanın başı mikrofonda
    saklanır, STT aynı mikrofondan devam eder (ilk kelime kaybolmaz)."""

    zaman_asimli = True

    def __init__(self, mikrofon):
        self.mikrofon = mikrofon
        self.bekliyor = False       # zaman aşımıyla tekrar tekrar çağrılınca yazı bir kez çıksın

    def bekle(self, zaman_asimi=None):
        if not self.bekliyor:
            print("[Dinliyorum: konuşmaya başlayın]")
            self.bekliyor = True
        tetiklendi = self.mikrofon.konusma_bekle(zaman_asimi)
        if tetiklendi:
            self.bekliyor = False
        return tetiklendi


class KlavyeTetik:
    zaman_asimli = False

    def bekle(self, zaman_asimi=None):
        input("[Konuşmak için Enter'a basın] ")
        return True


class DokunmaTetik:
    """Dokunmatik ekran (ya da fare tıklaması). Yüz ANA iş parçacığında dokunmayı görür ve
    dokunuldu() çağırır; konuşma iş parçacığı bekle() içinde kuyruktan okur.
    İki iş parçacığı arasındaki tek bağ bu kuyruktur (queue.Queue iş parçacığı güvenlidir)."""

    zaman_asimli = True

    def __init__(self):
        self.kuyruk = queue.Queue()
        self.bekliyor = False

    def dokunuldu(self):
        self.kuyruk.put("dokunma")          # yüz çağırır (ana iş parçacığı)

    def bekle(self, zaman_asimi=None):
        if not self.bekliyor:                # beklemenin başı (zaman aşımıyla tekrar çağrılınca değil)
            kuyrugu_bosalt(self.kuyruk)      # önceki turdan kalan dokunmalar sayılmaz
            print("[Konuşmak için ekrandaki alana dokunun]")
            self.bekliyor = True
        try:
            self.kuyruk.get(timeout=zaman_asimi)   # dokunulana kadar (ya da zaman aşımına kadar) bekler
        except queue.Empty:
            return False
        self.bekliyor = False
        return True


class GpioTetik:
    """Düğmenin bir ucu GPIO pinine, diğer ucu GND'ye. Pi'nin iç pull-up direnci kullanılır."""

    zaman_asimli = True

    def __init__(self, pin):
        from gpiozero import Button       # paket yoksa ImportError -> tetik_sec yakalar
        self.dugme = Button(pin, pull_up=True, bounce_time=0.05)
        self.pin = pin
        self.bekliyor = False

    def bekle(self, zaman_asimi=None):
        if not self.bekliyor:
            print(f"[Konuşmak için GPIO{self.pin} düğmesine basın]")
            self.bekliyor = True
        basildi = bool(self.dugme.wait_for_press(timeout=zaman_asimi))
        if basildi:
            self.bekliyor = False
        return basildi


def tetik_sec(saglayici, gpio_pin=17, mikrofon=None):
    """Ayardaki ada göre tetik kurar. 'ses' mikrofon ister; 'dokunma' yüz ister (ana.py denetler)."""
    if saglayici == "ses":
        if mikrofon is not None:
            return SesTetik(mikrofon)
        print("[tetik] Ses tetiği için mikrofon yok.")
    if saglayici == "dokunma":
        return DokunmaTetik()
    if saglayici == "gpio":
        try:
            return GpioTetik(gpio_pin)
        except Exception as hata:   # Windows'ta gpiozero yok; Pi'de pin meşgul olabilir
            print(f"[tetik] GPIO düğmesi kurulamadı ({hata}); klavyeye düşüyorum.")
    return KlavyeTetik()
