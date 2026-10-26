# Ne yapıyor: bas-konuş tetikleyicisi. bekle() kullanıcı düğmeye basana kadar bekler.
# KlavyeTetik terminalde Enter'ı bekler (düğme yokken, varsayılan).
# GpioTetik Pi'nin GPIO pinine bağlı düğmeyi bekler (gpiozero); paket/pin yoksa klavyeye düşer.


class KlavyeTetik:
    def bekle(self):
        input("[Konuşmak için Enter'a basın] ")


class GpioTetik:
    """Düğmenin bir ucu GPIO pinine, diğer ucu GND'ye. Pi'nin iç pull-up direnci kullanılır."""

    def __init__(self, pin):
        from gpiozero import Button       # paket yoksa ImportError -> tetik_sec yakalar
        self.dugme = Button(pin, pull_up=True, bounce_time=0.05)
        self.pin = pin

    def bekle(self):
        print(f"[Konuşmak için GPIO{self.pin} düğmesine basın]")
        self.dugme.wait_for_press()


def tetik_sec(saglayici, gpio_pin=17):
    if saglayici == "gpio":
        try:
            return GpioTetik(gpio_pin)
        except Exception as hata:   # Windows'ta gpiozero yok; Pi'de pin meşgul olabilir
            print(f"[tetik] GPIO düğmesi kurulamadı ({hata}); klavyeye düşüyorum.")
    return KlavyeTetik()
