"""Sahte ESP32'yi başlat: `py -3 kod/araclar/sahte_esp32` (ya da `kod/simulasyon.bat`).

Varsayılan: oda_engelli haritası, TCP 127.0.0.1:5760 (sanal seri hat), görünüm http://127.0.0.1:8765 ve tarayıcı açılır.
    --harita oda_bos        başka harita (kod/araclar/haritalar/<ad>.json ya da dosya yolu)
    --port 5760             TCP portu (Pi istemcisi buraya bağlanır)
    --http 8765             görünüm portu
    --gorunum-yok           yalnız TCP sunucusu (başka bir Pi programı bağlanacaksa)
    --tarayici-yok          görünümü başlat ama tarayıcıyı açma
Ctrl+C ile kapanır.
"""

import argparse
import os
import sys
import time
import webbrowser

_ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ARACLAR not in sys.path:
    sys.path.insert(0, _ARACLAR)

from sahte_esp32.cekirdek import SahteEsp32  # noqa: E402
from sahte_esp32.harita import Harita, harita_listesi  # noqa: E402
from sahte_esp32.tcp_sunucu import TcpSunucu  # noqa: E402


def main():
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(prog="sahte_esp32", description="Lale sahte ESP32 (Y0s)")
    ap.add_argument("--harita", default="oda_engelli", help="harita adı: %s" % ", ".join(harita_listesi()))
    ap.add_argument("--port", type=int, default=5760)
    ap.add_argument("--http", type=int, default=8765)
    ap.add_argument("--gorunum-yok", action="store_true")
    ap.add_argument("--tarayici-yok", action="store_true")
    a = ap.parse_args()

    harita = Harita.dosyadan(a.harita)
    cekirdek = SahteEsp32(harita)
    try:
        sunucu = TcpSunucu(cekirdek, port=a.port).baslat()
    except OSError as h:
        print("TCP portu %d açılamadı (%s). Başka bir sahte ESP32 açık olabilir; --port ile başka port ver." % (a.port, h))
        return 2
    print("Sahte ESP32 çalışıyor: harita %s, sanal seri hat tcp://%s:%d" % (harita.ad, sunucu.host, sunucu.port))
    gorunum = None
    if not a.gorunum_yok:
        from sahte_esp32.gorunum import Gorunum
        try:
            gorunum = Gorunum(sunucu, http_port=a.http).baslat()
        except OSError as h:
            print("Görünüm portu %d açılamadı (%s); --http ile başka port ver." % (a.http, h))
            sunucu.durdur()
            return 2
        adres = "http://127.0.0.1:%d/" % gorunum.http_port
        print("Görünüm: %s  (tuşlar: oklar sür, Boşluk mantar, R devreye al, B bırak, X dur)" % adres)
        if not a.tarayici_yok:
            webbrowser.open(adres)
    print("Kapatmak için Ctrl+C.")
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("kapanıyor")
    finally:
        if gorunum is not None:
            gorunum.durdur()
        sunucu.durdur()
    return 0


if __name__ == "__main__":
    sys.exit(main())
