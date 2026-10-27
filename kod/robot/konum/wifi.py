# Ne yapıyor: Wi-Fi parmak izi ile bölge bulur. Çevredeki erişim noktalarının (BSSID) sinyal gücünü tarar,
# her bölgede önceden kaydedilmiş ölçümlerin ortalamasıyla karşılaştırır, en yakın bölgeyi seçer.
# İnternet ya da ağa bağlanmak GEREKMEZ; yalnız tarama yapılır. Sinyal her iki işletim sisteminde de yüzde (0-100).
#
# Tarama: Linux/Pi  nmcli -t -f BSSID,SIGNAL,CHAN dev wifi list --rescan yes
#         Windows   netsh wlan show networks mode=bssid   (yalnız geliştirici denemesi; Windows kendi önbelleğini
#                   verir, yeniden taramayı zorlayamaz: art arda ölçümler aynı çıkabilir)
# DİKKAT: tarama sırasında Wi-Fi kartı kanalları dolaşır; bağlı bağlantı 1-2 s kesilebilir/yavaşlayabilir.
# Bu yüzden aralık uzun tutulur (ayar: konum.wifi.aralik, varsayılan 15 s). Bulut dil modeli o an yavaşlayabilir.
#
# Eşleme: soru ile bölge ortalaması arasında Öklid uzaklığı; görünmeyen BSSID 0 (%0 sinyal) sayılır.
# Güven = 1 - (en yakın uzaklık / ikinci en yakın uzaklık): iki bölge birbirine benziyorsa güven düşer.

import math
import os
import re
import subprocess
import sys
import time

import yaml

from robot.konum.bolgeler import KONUM_KLASORU
from robot.konum.kaynak import KonumKaynagi, KonumTahmini, sinirla

PARMAK_IZI_DOSYASI = os.path.join(KONUM_KLASORU, "parmak_izi.yaml")
GORUNMEYEN = 0.0          # taramada görünmeyen BSSID'nin sinyali (yüzde)
AZAMI_UZAKLIK = 250.0     # en yakın bölge bundan uzaksa "bu bina değil" denir, None döner
TARAMA_ZAMAN_ASIMI = 20   # saniye

PARMAK_IZI_BASLIGI = """\
# Wi-Fi parmak izi veritabanı (robot/konum/wifi.py). ELLE DÜZENLEMEYİN; şu komutla doldurun:
#   python3 -m robot.konum kaydet <bolge> --adet 5        (kod/ klasöründen, robot o bölgedeyken)
# Biçim: bölge -> ölçüm listesi; her ölçüm {BSSID: sinyal yüzdesi}. Bölge adları konum/bolgeler.yaml ile aynı.
# Bu dosya depoya girer (ekip aynı haritayı kullanır).
"""


# ---------- tarama çıktısını ayrıştırma ----------

def nmcli_ayristir(metin):
    """nmcli -t çıktısı: 'AA\\:BB\\:CC\\:DD\\:EE\\:FF:72:6'. BSSID içindeki ':' ters bölüyle kaçışlıdır."""
    sonuc = {}
    for satir in metin.splitlines():
        parcalar = satir.strip().replace("\\:", "\x00").split(":")
        if len(parcalar) < 2:
            continue
        bssid = parcalar[0].replace("\x00", ":").lower()
        try:
            sonuc[bssid] = float(parcalar[1])
        except ValueError:
            continue
    return sonuc


BSSID_DESENI = re.compile(r"BSSID\s*\d*\s*:\s*([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})")
SINYAL_DESENI = re.compile(r"(\d+)\s*%|%\s*(\d+)")      # İngilizce "90%", Türkçe "%90"


def netsh_ayristir(metin):
    """netsh çıktısı: 'BSSID 1 : 44:12:..' satırından sonraki ilk '..%' satırı o BSSID'nin sinyalidir.
    Dil bağımsız: Türkçe Windows'ta 'Sinyal : %90', İngilizcede 'Signal : 90%' yazar; yalnız '%' aranır."""
    sonuc = {}
    bekleyen = None
    for satir in metin.splitlines():
        eslesme = BSSID_DESENI.search(satir)
        if eslesme:
            bekleyen = eslesme.group(1).lower()
            continue
        if bekleyen:
            sinyal = SINYAL_DESENI.search(satir)
            if sinyal:
                sonuc[bekleyen] = float(sinyal.group(1) or sinyal.group(2))
                bekleyen = None
    return sonuc


def tarama_komutu():
    if sys.platform.startswith("win"):
        return ["netsh", "wlan", "show", "networks", "mode=bssid"], netsh_ayristir
    return ["nmcli", "-t", "-f", "BSSID,SIGNAL,CHAN", "dev", "wifi", "list", "--rescan", "yes"], nmcli_ayristir


def windows_tarama_tetikle(bekle=4.0):
    """Windows'ta netsh yalnız önbellekteki listeyi verir (bağlıyken 1-3 BSSID'ye düşebilir). wlanapi.dll'in
    WlanScan işlevi (yönetici izni gerekmez) taze tarama başlatır; Microsoft taramanın 4 s'de bittiğini yazar.
    Olmazsa sessizce geçilir: netsh yine önbellekle çalışır."""
    import ctypes
    from ctypes import POINTER, Structure, byref, c_int, c_ubyte, c_ulong, c_ushort, c_void_p, c_wchar

    class GUID(Structure):
        _fields_ = [("Data1", c_ulong), ("Data2", c_ushort), ("Data3", c_ushort), ("Data4", c_ubyte * 8)]

    class ArayuzBilgisi(Structure):          # WLAN_INTERFACE_INFO
        _fields_ = [("guid", GUID), ("aciklama", c_wchar * 256), ("durum", c_int)]

    class ArayuzListesi(Structure):          # WLAN_INTERFACE_INFO_LIST
        _fields_ = [("adet", c_ulong), ("sira", c_ulong), ("bilgi", ArayuzBilgisi * 1)]

    try:
        wlan = ctypes.windll.wlanapi
        tutamak, surum = c_void_p(), c_ulong()
        if wlan.WlanOpenHandle(2, None, byref(surum), byref(tutamak)) != 0:
            return
        liste = POINTER(ArayuzListesi)()
        try:
            if wlan.WlanEnumInterfaces(tutamak, None, byref(liste)) != 0:
                return
            adet = liste.contents.adet
            dizi = ctypes.cast(ctypes.addressof(liste.contents.bilgi), POINTER(ArayuzBilgisi * adet)).contents
            for bilgi in dizi:
                wlan.WlanScan(tutamak, byref(bilgi.guid), None, None, None)
            wlan.WlanFreeMemory(liste)
        finally:
            wlan.WlanCloseHandle(tutamak, None)
        if adet:
            time.sleep(bekle)
    except (OSError, AttributeError, ValueError):
        return


def tara():
    """Gerçek tarama: {bssid: sinyal yüzdesi}. Komut yoksa FileNotFoundError yükselir (kaynak pasif olur)."""
    if sys.platform.startswith("win"):
        windows_tarama_tetikle()
    komut, ayristir = tarama_komutu()
    cikti = subprocess.run(komut, capture_output=True, timeout=TARAMA_ZAMAN_ASIMI)
    # Windows konsolu OEM kod sayfası kullanır; BSSID ve % işareti her kod sayfasında aynı, harfler önemsiz
    metin = cikti.stdout.decode("utf-8", errors="replace")
    return ayristir(metin)


# ---------- parmak izi veritabanı ----------

def veritabani_oku(yol=PARMAK_IZI_DOSYASI):
    """{bolge: [ {bssid: sinyal}, ... ]}; dosya yoksa ya da boşsa {}."""
    if not os.path.exists(yol):
        return {}
    with open(yol, encoding="utf-8") as dosya:
        veri = yaml.safe_load(dosya) or {}
    return {str(b): [dict(o) for o in (olcumler or [])] for b, olcumler in veri.items()}


def veritabani_yaz(veritabani, yol=PARMAK_IZI_DOSYASI):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", encoding="utf-8") as dosya:
        dosya.write(PARMAK_IZI_BASLIGI)
        if veritabani:
            yaml.safe_dump(veritabani, dosya, allow_unicode=True, sort_keys=True, default_flow_style=None)
        else:
            dosya.write("{}\n")


def ortalama_iz(olcumler):
    """Bir bölgenin ölçümlerinin ortalaması; bir ölçümde görünmeyen BSSID o ölçümde 0 sayılır."""
    bssidler = {b for o in olcumler for b in o}
    return {b: sum(o.get(b, GORUNMEYEN) for o in olcumler) / len(olcumler) for b in bssidler}


def uzaklik(a, b):
    """İki parmak izi arasında Öklid uzaklığı (görünmeyen BSSID = 0)."""
    bssidler = set(a) | set(b)
    return math.sqrt(sum((a.get(k, GORUNMEYEN) - b.get(k, GORUNMEYEN)) ** 2 for k in bssidler))


def eslestir(soru, veritabani, azami_uzaklik=AZAMI_UZAKLIK):
    """(bölge, güven, {bölge: uzaklık}) ya da hiç ortak BSSID yoksa / çok uzaksa (None, 0, uzakliklar)."""
    izler = {b: ortalama_iz(o) for b, o in veritabani.items() if o}
    uzakliklar = {b: uzaklik(soru, iz) for b, iz in izler.items() if set(iz) & set(soru)}
    if not uzakliklar:
        return None, 0.0, uzakliklar
    sirali = sorted(uzakliklar.items(), key=lambda bu: bu[1])
    bolge, en_yakin = sirali[0]
    if en_yakin > azami_uzaklik:
        return None, 0.0, uzakliklar
    if len(sirali) == 1:
        return bolge, 0.5, uzakliklar        # tek bölge kayıtlı: karşılaştıracak başka yer yok
    ikinci = sirali[1][1]
    guven = 1.0 - en_yakin / ikinci if ikinci > 0 else 0.0
    return bolge, sinirla(guven), uzakliklar


# ---------- kaynak ----------

class WifiKaynagi(KonumKaynagi):
    ad = "wifi"

    def __init__(self, agirlik=1.0, aralik=15.0, veritabani_yolu=PARMAK_IZI_DOSYASI,
                 azami_uzaklik=AZAMI_UZAKLIK, tarayici=None):
        super().__init__(agirlik, aralik)
        self.veritabani_yolu = veritabani_yolu
        self.azami_uzaklik = azami_uzaklik
        self.tarayici = tarayici or tara       # testte sahte tarama verilir
        self.veritabani = {}

    def baslat(self):
        try:
            self.veritabani = veritabani_oku(self.veritabani_yolu)
        except (OSError, yaml.YAMLError) as hata:
            self.pasif_yap(f"{self.veritabani_yolu} okunamadı ({hata})")
            return
        if not self.veritabani:
            print("[konum/wifi] parmak izi kaydı yok; önce: python3 -m robot.konum kaydet <bolge>")

    def tara(self):
        try:
            return self.tarayici()
        except FileNotFoundError:
            komut = tarama_komutu()[0][0]
            self.pasif_yap(f"'{komut}' komutu yok (Pi'de NetworkManager gerekir)")
            return {}

    def olc(self):
        if not self.veritabani:
            return None
        olcum = self.tara()
        if not olcum:
            return None
        bolge, guven, _ = eslestir(olcum, self.veritabani, self.azami_uzaklik)
        if bolge is None:
            return None
        return KonumTahmini(bolge=bolge, guven=guven, kaynak=self.ad)

    def ham(self):
        if not self.etkin:
            return f"pasif: {self.pasif_nedeni}"
        olcum = self.tara()
        satirlar = [f"{len(olcum)} BSSID görüldü"]
        for bssid, sinyal in sorted(olcum.items(), key=lambda bs: -bs[1]):
            satirlar.append(f"    {bssid}  %{sinyal:.0f}")
        if self.veritabani and olcum:
            bolge, guven, uzakliklar = eslestir(olcum, self.veritabani, self.azami_uzaklik)
            yakinlar = ", ".join(f"{b} {u:.0f}" for b, u in sorted(uzakliklar.items(), key=lambda bu: bu[1]))
            satirlar.append(f"    eşleşme: {bolge} (güven {guven:.2f}); uzaklıklar: {yakinlar or '-'}")
        elif not self.veritabani:
            satirlar.append("    parmak izi kaydı yok (kaydet komutu)")
        return "\n".join(satirlar)

    def kaydet(self, bolge, adet=5, bekleme=3.0, yazdir=print):
        """Bu noktada 'adet' tarama yapar, bölgenin ölçüm listesine ekler, dosyaya yazar. Eklenen sayıyı döner."""
        veritabani = veritabani_oku(self.veritabani_yolu)
        eklenen = 0
        for sira in range(1, adet + 1):
            olcum = self.tara()
            if olcum:
                veritabani.setdefault(bolge, []).append({b: round(s) for b, s in olcum.items()})
                eklenen += 1
            yazdir(f"[{sira}/{adet}] {len(olcum)} BSSID")
            if sira < adet:
                time.sleep(bekleme)
        if eklenen:
            veritabani_yaz(veritabani, self.veritabani_yolu)
            self.veritabani = veritabani
        return eklenen
