# Ne yapıyor: gürültü provası. Konuşma kayıtlarını (olcum/ses/konusma/<ad>.wav + doğru metni <ad>.txt) gürültü
# kayıtlarıyla (olcum/ses/gurultu/*.wav) belirlenen SNR'larda (ör. 20, 10, 5, 0 dB) karıştırır, Vosk ile tanır ve
# test_seti.py'nin ölçütleriyle (normalize eşleşme, kelime hata oranı) SNR x tanıma oranı tablosu yazar.
# Yalnız numpy + wave (scipy yok). Vosk/model yoksa: --stt klavye (karışımı dinleyip yazarsınız: insan tabanı)
# ya da --stt referans (doğru metni döner; yalnız boru hattı denemesi).
#
# Örnek (Pi, kod/'dan):  python3 olcum/gurultu_prova.py --etiket kantin --snr 20,10,5,0
#        (Windows):      py -3 kod/olcum/gurultu_prova.py --stt referans --etiket deneme
# Sonuç: kod/olcum/sonuclar/gurultu-<etiket>.md
#
# SNR (sinyal/gürültü oranı, dB) = 10 log10(konuşma gücü / gürültü gücü); güç = örneklerin karelerinin ortalaması.
# Bütün kayıt üzerinden hesaplanır (cümle aralarındaki sessizlik dahil): kayıtların başını/sonunu kısa kesin.

import argparse
import glob
import json
import os
import re
import sys
import wave
from datetime import datetime

import numpy as np

OLCUM = os.path.dirname(os.path.abspath(__file__))
KOD = os.path.dirname(OLCUM)
sys.path.insert(0, KOD)   # "robot", "ana" ve "olcum" kod/ klasöründe

from ana import ayarlari_oku, konsolu_utf8_yap, yol_coz                       # noqa: E402
from olcum.test_seti import duzenleme_mesafesi, normalize, yuzde             # noqa: E402
from robot.mikrofon import ORNEKLEME                                         # noqa: E402

INT16_AZAMI = 32767
SES_KLASORU = os.path.join(OLCUM, "ses")


# ---------- wav dosyaları ----------

def wav_oku(yol):
    """16 bit PCM wav -> (float örnekler, örnekleme hızı). Çok kanallıysa kanalların ortalaması (mono)."""
    with wave.open(yol, "rb") as w:
        kanal, genislik, hiz = w.getnchannels(), w.getsampwidth(), w.getframerate()
        ham = w.readframes(w.getnframes())
    if genislik != 2:
        raise ValueError(f"{yol}: yalnız 16 bit PCM wav okunur (bu dosya {8 * genislik} bit)")
    ornek = np.frombuffer(ham, dtype="<i2").astype(np.float64)
    if kanal > 1:
        ornek = ornek.reshape(-1, kanal).mean(axis=1)
    return ornek, hiz


def wav_yaz(yol, ornek_int16, hiz=ORNEKLEME):
    os.makedirs(os.path.dirname(yol) or ".", exist_ok=True)
    with wave.open(yol, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(hiz)
        w.writeframes(np.asarray(ornek_int16, dtype="<i2").tobytes())


def yeniden_ornekle(ornek, hiz, hedef=ORNEKLEME):
    """Örnekleme hızını değiştirir (Vosk 16 kHz ister). Azaltırken önce kaba alçak geçiren (kayan ortalama)
    uygulanır, sonra doğrusal ara değer. Hız aynıysa dokunmaz."""
    if hiz == hedef or len(ornek) == 0:
        return ornek
    if hiz > hedef:
        pencere = int(round(hiz / hedef))
        if pencere > 1:
            ornek = np.convolve(ornek, np.ones(pencere) / pencere, mode="same")
    adet = int(round(len(ornek) * hedef / hiz))
    return np.interp(np.arange(adet) / hedef, np.arange(len(ornek)) / hiz, ornek)


def ses_oku(yol):
    ornek, hiz = wav_oku(yol)
    return yeniden_ornekle(ornek, hiz)


# ---------- karıştırma ----------

def guc(x):
    """Ortalama güç: örneklerin karelerinin ortalaması."""
    return float(np.mean(np.square(x))) if len(x) else 0.0


def snr_db(sinyal, gurultu):
    pg = guc(gurultu)
    return float("inf") if pg == 0 else 10 * np.log10(guc(sinyal) / pg)


def gurultu_parcasi(gurultu, uzunluk, rastgele):
    """Gürültüyü konuşma uzunluğuna getirir: kısaysa art arda eklenir, uzunsa rastgele bir yerinden kesilir."""
    if len(gurultu) == 0:
        raise ValueError("gürültü kaydı boş")
    if len(gurultu) < uzunluk:
        gurultu = np.tile(gurultu, -(-uzunluk // len(gurultu)))     # yukarı yuvarlanmış tekrar sayısı
    bas = int(rastgele.integers(0, len(gurultu) - uzunluk + 1))
    return gurultu[bas:bas + uzunluk]


def karistir(konusma, gurultu, snr, rastgele):
    """konuşma + k x gürültü. k, 10 log10(P_konuşma / P_(k x gürültü)) = snr olacak şekilde seçilir:
    k = karekök(P_konuşma / (P_gürültü x 10^(snr/10))). Dönen: (karışım, ölçeklenmiş gürültü); ikisi de
    konuşmayla aynı uzunlukta, float (henüz int16'ya çevrilmedi)."""
    parca = gurultu_parcasi(gurultu, len(konusma), rastgele)
    pk, pg = guc(konusma), guc(parca)
    if pg == 0:
        return konusma.copy(), np.zeros_like(konusma)
    k = np.sqrt(pk / (pg * 10 ** (snr / 10)))
    olcekli = parca * k
    return konusma + olcekli, olcekli


def int16_yap(karisim):
    """int16'ya çevirir. Tepe 32767'yi aşarsa bütün karışım aynı oranda kısılır: kırpma (bozulma) olmaz,
    konuşma ve gürültü birlikte kısıldığı için SNR değişmez. Dönen: (int16 dizi, kısma oranı <= 1)."""
    tepe = float(np.max(np.abs(karisim))) if len(karisim) else 0.0
    oran = 1.0 if tepe <= INT16_AZAMI else INT16_AZAMI / tepe
    return np.round(karisim * oran).astype(np.int16), oran


# ---------- tanıyıcılar: tani(ses_int16, beklenen, etiket) -> metin ----------

class VoskTaniyici:
    ad = "vosk"

    def __init__(self, model_yolu):
        try:
            import vosk
        except ImportError:
            raise RuntimeError("'vosk' paketi gerekli: pip install vosk")
        if not os.path.isdir(model_yolu):
            raise RuntimeError(f"Vosk modeli bulunamadı: {model_yolu}")
        vosk.SetLogLevel(-1)
        self.vosk = vosk
        self.model = vosk.Model(model_yolu)

    def tani(self, ses, beklenen, etiket):
        tanima = self.vosk.KaldiRecognizer(self.model, ORNEKLEME)
        veri = ses.tobytes()
        for i in range(0, len(veri), 8000):          # 0,25 s'lik parçalar (mikrofondaki gibi akış)
            tanima.AcceptWaveform(veri[i:i + 8000])
        return json.loads(tanima.FinalResult()).get("text", "").strip()


class KlavyeTaniyici:
    """İnsan dinleyici: karışımı wav olarak yazar, kişi dinleyip anladığını yazar (insan tanıma tabanı)."""
    ad = "klavye"

    def __init__(self, klasor):
        self.klasor = klasor

    def tani(self, ses, beklenen, etiket):
        yol = os.path.join(self.klasor, re.sub(r"[^\w-]+", "_", etiket).strip("_") + ".wav")
        wav_yaz(yol, ses)
        return input(f"  Dinleyin: {yol}\n  Duyduğunuzu yazın: ").strip()


class ReferansTaniyici:
    """Doğru metni döner: yalnız betiğin çalıştığını denemek için (sonuç hep %100)."""
    ad = "referans"

    def tani(self, ses, beklenen, etiket):
        return beklenen


def taniyici_kur(ad, model_yolu, klavye_klasoru):
    if ad == "referans":
        return ReferansTaniyici()
    if ad == "vosk":
        try:
            return VoskTaniyici(model_yolu)
        except RuntimeError as hata:
            print(f"[prova] Vosk kurulamadı ({hata}); klavyeye düşüyorum (dinleyip yazarsınız).")
    return KlavyeTaniyici(klavye_klasoru)


# ---------- prova ----------

def konusmalari_oku(klasor):
    """[(ad, ses, beklenen metin)]; .txt'si olmayan wav atlanır (uyarıyla)."""
    liste = []
    for yol in sorted(glob.glob(os.path.join(klasor, "*.wav"))):
        txt = os.path.splitext(yol)[0] + ".txt"
        if not os.path.exists(txt):
            print(f"[prova] {os.path.basename(yol)}: doğru metin dosyası yok ({os.path.basename(txt)}); atlandı.")
            continue
        with open(txt, encoding="utf-8") as dosya:
            beklenen = dosya.read().strip()
        liste.append((os.path.splitext(os.path.basename(yol))[0], ses_oku(yol), beklenen))
    return liste


def gurultuleri_oku(klasor):
    return [(os.path.splitext(os.path.basename(y))[0], ses_oku(y))
            for y in sorted(glob.glob(os.path.join(klasor, "*.wav")))]


def deneme_satiri(konusma, gurultu, snr, beklenen, taninan, kisma):
    ref = normalize(beklenen).split()
    return {"konusma": konusma, "gurultu": gurultu, "snr": snr, "beklenen": beklenen, "taninan": taninan,
            "eslesme": int(normalize(taninan) == normalize(beklenen)), "kelime": len(ref),
            "hata": duzenleme_mesafesi(ref, normalize(taninan).split()), "kisma": kisma}


def prova(konusmalar, gurultuler, snrler, taniyici, rastgele, yazdir=print):
    """Her konuşma: önce temiz (gürültüsüz) taban, sonra her gürültü x her SNR. Ctrl+C erken bitirir."""
    satirlar = []
    try:
        for ad, ses, beklenen in konusmalar:
            denemeler = [("temiz", None, ses)]
            for g_ad, g_ses in gurultuler:
                for snr in snrler:
                    denemeler.append((g_ad, snr, karistir(ses, g_ses, snr, rastgele)[0]))
            for g_ad, snr, karisim in denemeler:
                ses16, kisma = int16_yap(karisim)
                etiket = f"{ad} temiz" if snr is None else f"{ad} {g_ad} {snr:g}dB"
                taninan = taniyici.tani(ses16, beklenen, etiket) or ""
                satir = deneme_satiri(ad, g_ad, snr, beklenen, taninan, kisma)
                satirlar.append(satir)
                yazdir(f"  {etiket:<40} {'+' if satir['eslesme'] else 'x'}  {taninan or '(hiçbir şey)'}")
    except (EOFError, KeyboardInterrupt):
        yazdir("\n[prova] Erken bitirildi; o ana kadarki denemeler yazılıyor.")
    return satirlar


# ---------- rapor ----------

def snr_adi(snr):
    return "temiz" if snr is None else f"{snr:g} dB"


def snr_sirasi(satirlar):
    """Önce temiz, sonra SNR büyükten küçüğe."""
    snrler = sorted({s["snr"] for s in satirlar if s["snr"] is not None}, reverse=True)
    return ([None] if any(s["snr"] is None for s in satirlar) else []) + snrler


def ana_tablo(satirlar):
    tablo = ["| SNR | Deneme | Normalize eşleşme | Kelime hata oranı |", "|---|---|---|---|"]
    for snr in snr_sirasi(satirlar):
        secili = [s for s in satirlar if s["snr"] == snr]
        eslesme = sum(s["eslesme"] for s in secili)
        kelime, hata = sum(s["kelime"] for s in secili), sum(s["hata"] for s in secili)
        tablo.append(f"| {snr_adi(snr)} | {len(secili)} | {eslesme}/{len(secili)} {yuzde(eslesme, len(secili))} | "
                     f"{yuzde(hata, kelime)} |")
    return tablo


def gurultu_tablosu(satirlar):
    """Gürültü türü x SNR: normalize eşleşme oranı (hangi gürültü daha zor?)."""
    snrler = [s for s in snr_sirasi(satirlar) if s is not None]
    turler = list(dict.fromkeys(s["gurultu"] for s in satirlar if s["snr"] is not None))
    if not turler:
        return ["Gürültülü deneme yok."]
    tablo = ["| Gürültü | " + " | ".join(snr_adi(s) for s in snrler) + " |", "|---|" + "---|" * len(snrler)]
    for tur in turler:
        hucreler = []
        for snr in snrler:
            secili = [s for s in satirlar if s["gurultu"] == tur and s["snr"] == snr]
            hucreler.append(yuzde(sum(s["eslesme"] for s in secili), len(secili)))
        tablo.append(f"| {tur} | " + " | ".join(hucreler) + " |")
    return tablo


def ayrinti_tablosu(satirlar):
    tablo = ["| Konuşma | Gürültü | SNR | Tanınan | Hata/kelime | Kısma |", "|---|---|---|---|---|---|"]
    for s in satirlar:
        taninan = (s["taninan"] or "(hiçbir şey)").replace("|", "/")
        tablo.append(f"| {s['konusma']} | {s['gurultu']} | {snr_adi(s['snr'])} | {taninan} | "
                     f"{s['hata']}/{s['kelime']} | {s['kisma']:.2f} |")
    return tablo


def rapor_metni(satirlar, bilgi):
    md = [f"# Gürültü provası: {bilgi['Etiket']}", ""] + [f"- {a}: {d}" for a, d in bilgi.items()]
    md += ["", "## SNR x tanıma", ""] + ana_tablo(satirlar)
    md += ["", "## Gürültü türüne göre (normalize eşleşme)", ""] + gurultu_tablosu(satirlar)
    md += ["", "SNR bütün kayıt üzerinden (sessizlik dahil). \"Kısma\" < 1: karışım taşmasın diye bütünüyle "
           "kısıldı (SNR değişmez).", "", "## Ayrıntı", ""] + ayrinti_tablosu(satirlar) + [""]
    return "\n".join(md)


# ---------- komut satırı ----------

def secenekleri_oku(argv=None):
    p = argparse.ArgumentParser(description="Gürültü provası: SNR x konuşma tanıma oranı")
    p.add_argument("--etiket", default="etiketsiz", help='ör. "kantin", "koridor-fan"')
    p.add_argument("--snr", default="20,10,5,0", help="virgülle SNR değerleri (dB)")
    p.add_argument("--stt", choices=["vosk", "klavye", "referans"], default="vosk")
    p.add_argument("--konusma-klasoru", default=os.path.join(SES_KLASORU, "konusma"))
    p.add_argument("--gurultu-klasoru", default=os.path.join(SES_KLASORU, "gurultu"))
    p.add_argument("--adet", type=int, help="yalnız ilk N konuşma kaydı")
    p.add_argument("--tohum", type=int, default=1, help="gürültünün kesildiği yer için rastgele tohum")
    p.add_argument("--ayar", default=os.path.join(KOD, "ayarlar.yaml"))
    p.add_argument("--sonuc-klasoru", default=os.path.join(OLCUM, "sonuclar"))
    return p.parse_args(argv)


def main(argv=None):
    konsolu_utf8_yap()
    sec = secenekleri_oku(argv)
    try:
        snrler = [float(s) for s in sec.snr.split(",") if s.strip()]
    except ValueError:
        print(f"[prova] SNR listesi sayı olmalı: {sec.snr}")
        return 2
    konusmalar = konusmalari_oku(sec.konusma_klasoru)[:sec.adet] if sec.adet else konusmalari_oku(sec.konusma_klasoru)
    gurultuler = gurultuleri_oku(sec.gurultu_klasoru)
    if not konusmalar:
        print(f"[prova] {sec.konusma_klasoru} içinde .wav + .txt çifti yok (16 bit wav, aynı adlı .txt doğru metin).")
        return 1
    if not gurultuler:
        print(f"[prova] {sec.gurultu_klasoru} içinde gürültü .wav yok; yalnız temiz kayıtlar denenecek.")
    etiket = re.sub(r"[^\w-]+", "_", sec.etiket).strip("_") or "etiketsiz"
    stt = (ayarlari_oku(sec.ayar).get("stt") or {}) if os.path.exists(sec.ayar) else {}
    taniyici = taniyici_kur(sec.stt, yol_coz(stt.get("vosk_model", "")),
                            os.path.join(sec.sonuc_klasoru, f"gurultu-{etiket}-sesler"))
    print(f"[prova] {len(konusmalar)} konuşma x ({len(gurultuler)} gürültü x {len(snrler)} SNR + temiz) | "
          f"tanıyıcı: {taniyici.ad}")
    satirlar = prova(konusmalar, gurultuler, snrler, taniyici, np.random.default_rng(sec.tohum))
    if not satirlar:
        print("[prova] Hiç deneme yapılmadı; dosya yazılmadı.")
        return 1
    bilgi = {"Etiket": sec.etiket, "Tarih": f"{datetime.now():%Y-%m-%d %H:%M}", "Tanıyıcı": taniyici.ad,
             "Konuşma kaydı": len(konusmalar), "Gürültü": ", ".join(a for a, _ in gurultuler) or "-",
             "SNR (dB)": ", ".join(f"{s:g}" for s in snrler), "Tohum": sec.tohum}
    metin = rapor_metni(satirlar, bilgi)
    yol = os.path.join(sec.sonuc_klasoru, f"gurultu-{etiket}.md")
    os.makedirs(sec.sonuc_klasoru, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as dosya:
        dosya.write(metin)
    print("\n" + "\n".join(ana_tablo(satirlar)))
    print(f"\n[prova] Sonuç: {yol}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
