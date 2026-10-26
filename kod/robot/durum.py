# Ne yapıyor: robotun o anda hangi durumda olduğunu tutar (BEKLE, DİNLE, DÜŞÜN, KONUŞ, JEST).
# İzinli geçişler tek bir tabloda (GECISLER); tabloda olmayan geçiş hata verir.
# Her geçişte dinleyicilere (yüz, ileride LED) "eski, yeni" durumu haber verir.

from enum import Enum


class Durum(Enum):
    BEKLE = "BEKLE"   # düğmeye basılmasını bekliyor
    DINLE = "DİNLE"   # kullanıcıyı dinliyor (mikrofon yalnız burada açık)
    DUSUN = "DÜŞÜN"   # cevap hazırlanıyor
    KONUS = "KONUŞ"   # robot konuşuyor (mikrofon kapalı: yarım dupleks)
    JEST = "JEST"     # kol/kafa hareketi (kayıtlı servo açıları)


# Hangi durumdan hangi durumlara geçilebilir? Tek tablo, tek yer.
# DİNLE'ye yalnız BEKLE'den geçilir; bu yüzden robot konuşurken mikrofon açılamaz.
GECISLER = {
    Durum.BEKLE: {Durum.DINLE},
    Durum.DINLE: {Durum.DUSUN, Durum.BEKLE},               # hiçbir şey duyulmazsa BEKLE
    Durum.DUSUN: {Durum.KONUS, Durum.JEST, Durum.BEKLE},   # hata olursa BEKLE
    Durum.JEST: {Durum.KONUS, Durum.BEKLE},
    Durum.KONUS: {Durum.BEKLE},
}


class GecersizGecis(Exception):
    """Tabloda olmayan bir geçiş istendiğinde verilen hata."""


class DurumMakinesi:
    def __init__(self):
        self.durum = Durum.BEKLE
        self._dinleyiciler = []

    def dinleyici_ekle(self, fonksiyon):
        """fonksiyon(eski, yeni) her geçişte çağrılır."""
        self._dinleyiciler.append(fonksiyon)

    def gecebilir_mi(self, yeni):
        return yeni in GECISLER[self.durum]

    def gec(self, yeni):
        if not self.gecebilir_mi(yeni):
            raise GecersizGecis(f"{self.durum.value} -> {yeni.value} geçişi tabloda yok")
        eski = self.durum
        self.durum = yeni
        for fonksiyon in self._dinleyiciler:
            fonksiyon(eski, yeni)
