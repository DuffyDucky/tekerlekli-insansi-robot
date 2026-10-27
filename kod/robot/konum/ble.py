# Ne yapıyor: BLE (Bluetooth Low Energy) beacon ile bölge bulur. Her bölgeye ucuz bir beacon konur;
# robot 2 s tarar, bolgeler.yaml 'beaconlar:' tablosundaki (MAC ya da yayın adı -> bölge) cihazlardan
# sinyali (RSSI) en güçlü olanın bölgesini söyler. 'bleak' kütüphanesi yoksa kaynak pasif olur.
#
# Not: RSSI duvar, insan ve robotun kendi gövdesinden çok etkilenir; beaconlar birbirinden en az 8-10 m uzak olsun.

import asyncio

from robot.konum.kaynak import KonumKaynagi, KonumTahmini, sinirla

TARAMA_SURESI = 2.0       # saniye
GUCLU_RSSI = -50.0        # bu ve üstü tam güven
ZAYIF_RSSI = -95.0        # bu ve altı en düşük güven


def rssi_guveni(rssi):
    return sinirla((rssi - ZAYIF_RSSI) / (GUCLU_RSSI - ZAYIF_RSSI), 0.1, 1.0)


def bleak_tara(sure=TARAMA_SURESI):
    """Gerçek tarama: [(mac, ad, rssi), ...]. bleak yoksa ImportError."""
    from bleak import BleakScanner

    async def _tara():
        bulunan = await BleakScanner.discover(timeout=sure, return_adv=True)
        return [(cihaz.address, cihaz.name or reklam.local_name or "", reklam.rssi)
                for cihaz, reklam in bulunan.values()]

    return asyncio.run(_tara())


def en_guclu(gorulenler, beaconlar):
    """Tabloda olan cihazlardan RSSI'si en güçlü olan: (bölge, rssi) ya da (None, None)."""
    en_iyi, en_iyi_rssi = None, None
    for mac, ad, rssi in gorulenler:
        bolge = beaconlar.get(str(mac).upper()) or beaconlar.get(str(ad).upper())
        if bolge and (en_iyi_rssi is None or rssi > en_iyi_rssi):
            en_iyi, en_iyi_rssi = bolge, rssi
    return en_iyi, en_iyi_rssi


class BleKaynagi(KonumKaynagi):
    ad = "ble"

    def __init__(self, bolgeler, agirlik=1.0, aralik=2.0, tarayici=None):
        super().__init__(agirlik, aralik)
        self.bolgeler = bolgeler
        self.tarayici = tarayici          # testte sahte: çağrılınca [(mac, ad, rssi), ...] döner

    def baslat(self):
        if self.tarayici is not None:
            return
        try:
            import bleak  # noqa: F401
        except ImportError:
            self.pasif_yap("'bleak' kurulu değil (pip install bleak)")
            return
        if not self.bolgeler.beaconlar:
            print("[konum/ble] bolgeler.yaml'da beacon yok; tarama yapılır ama bölge çıkmaz.")
        self.tarayici = bleak_tara

    def olc(self):
        bolge, rssi = en_guclu(self.tarayici(), self.bolgeler.beaconlar)
        if bolge is None:
            return None
        return KonumTahmini(bolge=bolge, guven=rssi_guveni(rssi), kaynak=self.ad)

    def ham(self):
        if not self.etkin:
            return f"pasif: {self.pasif_nedeni}"
        gorulenler = sorted(self.tarayici(), key=lambda c: -c[2])
        satirlar = [f"{len(gorulenler)} cihaz görüldü"]
        for mac, ad, rssi in gorulenler[:15]:
            bolge = self.bolgeler.beaconlar.get(str(mac).upper()) or self.bolgeler.beaconlar.get(str(ad).upper())
            satirlar.append(f"    {mac}  {rssi} dBm  {ad}" + (f"  -> {bolge}" if bolge else ""))
        return "\n".join(satirlar)
