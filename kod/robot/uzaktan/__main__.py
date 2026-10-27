# Ne yapıyor: telefondan kumandayı robotsuz dener. Sahte seri ve sahte robotla sunucuyu açar, telefonda
# açılacak adresleri yazar; telefondan gelen komutlar terminalde "[seri] {...}" satırı olarak görünür.
#   py -3 -m robot.uzaktan                 (Windows, kod/ klasöründen)
#   python3 -m robot.uzaktan --port 8080 --pin 4821
# Telefon ve bilgisayar aynı Wi-Fi'da olmalı. Windows ilk açılışta güvenlik duvarı izni sorabilir
# ("Özel ağlar" işaretli izin verin). Ctrl+C ile kapanır.

import argparse
import sys
import time

from robot.uzaktan.kopru import RobotKoprusu
from robot.uzaktan.sahte import sahte_robot
from robot.uzaktan.sunucu import UzaktanSunucu


def main(argv=None):
    for akis in (sys.stdout,):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Telefondan kumanda denemesi (sahte robot)")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--pin", default="1234")
    p.add_argument("--saniye", type=float, help="bu kadar saniye sonra kendiliğinden kapan (deneme için)")
    sec = p.parse_args(argv)
    robot = sahte_robot()
    sunucu = UzaktanSunucu(RobotKoprusu(robot), port=sec.port, pin=sec.pin).baslat()
    print("[uzaktan] Sahte robotla kumanda sunucusu açık. Telefonda açın:")
    for adres in sunucu.adresler():
        print(f"    {adres}")
    print(f"[uzaktan] PIN: {sec.pin}   (kapatmak için Ctrl+C)")
    bitis = time.monotonic() + sec.saniye if sec.saniye else None
    try:
        while bitis is None or time.monotonic() < bitis:
            time.sleep(0.2)                  # kısa uykular: Windows'ta Ctrl+C hemen yakalansın
    except KeyboardInterrupt:
        pass
    finally:
        sunucu.kapat()
        print("[uzaktan] Kapandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
