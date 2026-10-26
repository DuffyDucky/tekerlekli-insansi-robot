# Ne yapıyor: konuşma tetikleyicisi. bekle() kullanıcı konuşmaya başlayana / dokunana / basana kadar bekler.
# SesTetik (varsayılan, düğmesiz) mikrofonda konuşma başlayınca tetikler. DokunmaTetik ekrandaki
# "Konuşmak için dokun" alanını, GpioTetik düğmeyi, KlavyeTetik terminalde Enter'ı bekler (geliştirici).

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

    def __init__(self, mikrofon):
        self.mikrofon = mikrofon

    def bekle(self):
        print("[Dinliyorum: konuşmaya başlayın]")
        self.mikrofon.konusma_bekle()


class KlavyeTetik:
    def bekle(self):
        input("[Konuşmak için Enter'a basın] ")


class DokunmaTetik:
    """Dokunmatik ekran (ya da fare tıklaması). Yüz ANA iş parçacığında dokunmayı görür ve
    dokunuldu() çağırır; konuşma iş parçacığı bekle() içinde kuyruktan okur.
    İki iş parçacığı arasındaki tek bağ bu kuyruktur (queue.Queue iş parçacığı güvenlidir)."""

    def __init__(self):
        self.kuyruk = queue.Queue()

    def dokunuldu(self):
        self.kuyruk.put("dokunma")          # yüz çağırır (ana iş parçacığı)

    def bekle(self):
        kuyrugu_bosalt(self.kuyruk)          # önceki turdan kalan dokunmalar sayılmaz
        print("[Konuşmak için ekrandaki alana dokunun]")
        self.kuyruk.get()                    # dokunulana kadar burada bekler


class GpioTetik:
    """Düğmenin bir ucu GPIO pinine, diğer ucu GND'ye. Pi'nin iç pull-up direnci kullanılır."""

    def __init__(self, pin):
        from gpiozero import Button       # paket yoksa ImportError -> tetik_sec yakalar
        self.dugme = Button(pin, pull_up=True, bounce_time=0.05)
        self.pin = pin

    def bekle(self):
        print(f"[Konuşmak için GPIO{self.pin} düğmesine basın]")
        self.dugme.wait_for_press()


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
