"""kod/ortak/protokol.json -> kod/ortak/PROTOKOL.md (okunur belge). Elle düzenleme: JSON'u değiştir, bunu koş.

    py -3 kod/ortak/protokol_belge_uret.py            # yazar
    py -3 kod/ortak/protokol_belge_uret.py --denetle  # belge güncel değilse çıkış 1 (testler de denetler)
"""

import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import lale_protokol as P  # noqa: E402

BELGE = os.path.join(BURASI, "PROTOKOL.md")


def _isaret(d):
    return "**TASLAK**" if d.get("taslak") else "0.5.0"


def _h(metin):
    return str(metin).replace("|", "\\|").replace("\n", " ")


def uret():
    J = P.PROTOKOL
    s = []
    a = s.append
    a("# Lale Pi ↔ ESP32 seri protokolü (sürüm %s)" % J["surum"])
    a("")
    a("> **Bu belge üretilir, elle düzenlenmez.** Tek kaynak `kod/ortak/protokol.json`; üretici "
      "`py -3 kod/ortak/protokol_belge_uret.py`. Tarih %s." % J["tarih"])
    a("")
    a("Taban sözleşme: firmware **%s** (`origin/main` `kod/esp32/src/seri_protokol.h`, Efe; derlendi, kartta denenmedi). "
      "Kaynak: %s" % (J["taban_surum"], _h(J["kaynak"])))
    a("")
    a("**İşaretler:** \"0.5.0\" = firmware 0.5.0 sözleşmesinde aynen olan (planla bağı Kaynak sütununda; planda olmayan "
      "0.5.0 kuralı da bu işareti taşır, ör. 5 s sessizlik). **TASLAK** = plan istiyor ama "
      "ayrıntıyı vermiyor ya da 0.5.0'da yok; Y0s paketinde (sahte ESP32) karar verildi, gerçek firmware'e girmeden önce "
      "Efe / Ahmet onayı ister. Sahte ESP32 bunları uygular; gerçek kartta yoksa ilgili testler \"yetenek yok\" diye atlanır.")
    a("")
    a("**Dürüstlük notu:** sahte ESP32 bu sözleşmenin çalıştırılabilir modelidir; gerçek ESP32'nin C++ kodunu sınamaz. "
      "İkisi ayrışırsa önce bu belge (JSON) düzeltilir.")
    a("")
    a("## 1. Çerçeve")
    a("")
    c = J["cerceve"]
    a("| Ne | Değer |")
    a("| --- | --- |")
    for ad in ("baud", "satir_sonu", "atilan_bayt", "en_cok_bayt", "kodlama", "bos_satir", "uzun_satir",
               "json_olmayan_gelen_satir_pi", "port_acilisi"):
        a("| %s | %s |" % (ad, _h(repr(c[ad]) if ad in ("satir_sonu", "atilan_bayt") else c[ad])))
    a("")
    a("Kaynak: %s." % _h(c["kaynak"]))
    a("")
    a("## 2. Zamanlar (ms)")
    a("")
    a("| Ad | Değer | Ne | Kaynak | İşaret |")
    a("| --- | --- | --- | --- | --- |")
    for ad, d in J["zamanlar_ms"].items():
        a("| `%s` | %s | %s | %s | %s |" % (ad, d["deger"], _h(d["aciklama"]), _h(d["kaynak"]), _isaret(d)))
    a("")
    a("## 3. Sınırlar ve güvenlik kuralları")
    a("")
    a("| Ad | Değer | Ne | Kaynak | İşaret |")
    a("| --- | --- | --- | --- | --- |")
    for bolum in ("sinirlar", "guvenlik"):
        for ad, d in J[bolum].items():
            a("| `%s` | %s | %s | %s | %s |" % (ad, d.get("deger", "—"), _h(d.get("aciklama", "")), _h(d["kaynak"]),
                                              _isaret(d)))
    iv = P.ivme_sinirlari()
    a("")
    a("İvme sınırları (`eklem_sinirlari.json` `teker.ivme_sinir_m_s2`, m/s²): düz sürüş %s, düz fren %s, rampa sürüş %s, "
      "rampa fren %s. Bekçi ve güç bırakma **ani** durdurur (0.5.0), `dur` fren sınırıyla." %
      (iv["duz_surus"], iv["duz_fren"], iv["rampa_surus"], iv["rampa_fren"]))
    a("")
    a("## 4. Güç durumları, arıza nedenleri, genel hatalar")
    a("")
    g = J["guc_durumlari"]
    a("Durumlar: %s. %s (Kaynak: %s.)" % (", ".join("`%s`" % x for x in g["degerler"]), _h(g["aciklama"]), _h(g["kaynak"])))
    a("")
    a("Arıza nedenleri (`guc` olayı `neden`, ping `ariza`): %s." % ", ".join("`%s`" % x for x in J["ariza_nedenleri"]["degerler"]))
    a("")
    a("| Genel hata | Ne |")
    a("| --- | --- |")
    for ad, ne in J["genel_hatalar"]["degerler"].items():
        a("| `%s` | %s |" % (ad, _h(ne)))
    a("")
    a(_h(J["genel_hatalar"]["not_"]))
    a("")
    a("## 5. Komutlar (Pi → ESP32)")
    a("")
    a("Her komut tek satır: `{\"k\":\"<ad>\", ...}`. Her komuta bir cevap gelir: `{\"ok\":true,\"k\":\"<ad>\",...}` ya da "
      "`{\"ok\":false,\"k\":\"<ad>\",\"hata\":\"...\"}`.")
    a("")
    a("| Komut | Alanlar | Cevaptaki ek alanlar | Hatalar | Ne | Kaynak | İşaret |")
    a("| --- | --- | --- | --- | --- | --- | --- |")
    for ad, d in J["komutlar"].items():
        alan = ", ".join("`%s` %s%s" % (n, t["tur"], "" if t.get("zorunlu") else " (isteğe bağlı)")
                         for n, t in d["alanlar"].items()) or "—"
        cev = ", ".join("`%s` %s" % (n, t) for n, t in d["cevap_alanlari"].items()) or "—"
        hat = ", ".join("`%s`" % h for h in d["hatalar"]) or "—"
        a("| `%s` | %s | %s | %s | %s | %s | %s |" % (ad, _h(alan), _h(cev), hat, _h(d["aciklama"]), _h(d["kaynak"]),
                                                       _isaret(d)))
    a("")
    a("## 6. Mesajlar (ESP32 → Pi)")
    a("")
    a("| Mesaj | Alanlar | Örnek | Ne | Kaynak | İşaret |")
    a("| --- | --- | --- | --- | --- | --- |")
    for ad, d in J["mesajlar"].items():
        alan = ", ".join("`%s` %s" % (n, t) for n, t in d["alanlar"].items())
        a("| `%s` | %s | `%s` | %s | %s | %s |" % (ad, _h(alan), _h(d["ornek"]), _h(d["aciklama"]), _h(d["kaynak"]),
                                                  _isaret(d)))
    a("")
    a("Yetenekler (TASLAK; `hazir` ve `ping` cevabında `yetenekler` listesi; 0.5.0'da alan yok = hiçbiri): %s." %
      "; ".join("`%s` %s" % (ad, _h(d["aciklama"])) for ad, d in J["yetenekler"].items()))
    a("")
    a("## 7. Servolar")
    a("")
    a(_h(J["servolar"]["aciklama"]) + " Kaynak: " + _h(J["servolar"]["kaynak"]) + ".")
    a("")
    a("| Kanal | Ad | Eklem | Ofset | En az | En çok | Hız (°/s) | Ev |")
    a("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for t in P.servo_tablosu():
        a("| %d | `%s` | `%s` | %+d | %g | %g | %g | %g |" % (t["kanal"], t["ad"], t["eklem"], t["ofset"], t["min"],
                                                               t["max"], t["hiz_derece_s"], t["ev"]))
    a("")
    a("Kanal 10 / 11 / 12 sonar tetiği, 13–15 yedek (`pin-haritasi.md` § 9): `servo` komutunda `bilinmeyen_kanal`.")
    a("")
    for kad, kalt, sad, sust in P.bagimli_sinirlar():
        a("- **TASLAK** bağımlı sınır: `%s` ≥ %g iken `%s` ≤ %g (servo çerçevesi; `eklem_sinirlari.json` `bagimli`)." %
          (kad, kalt, sad, sust))
    a("")
    j = J["jestler"]
    a("Jestler: %s; yönlü: %s (%s). Kaynak: %s." % (", ".join("`%s`" % x for x in j["degerler"]),
                                                   ", ".join(j["yonlu"]), "/".join(j["yonler"]), _h(j["kaynak"])))
    a("")
    a("## 8. Eskimiş taslak (`yazilim-plani.md` \"Seri protokol (ilk taslak)\")")
    a("")
    a(_h(J["eskimis_taslak"]["aciklama"]))
    a("")
    a("| Plan taslağı | Bu protokol |")
    a("| --- | --- |")
    for eski, yeni in J["eskimis_taslak"]["esleme"].items():
        a("| `%s` | %s |" % (_h(eski), _h(yeni)))
    a("")
    a("## 9. TASLAK öğelerin listesi (onay bekler)")
    a("")
    for bolum in ("zamanlar_ms", "sinirlar", "guvenlik", "komutlar", "mesajlar", "yetenekler"):
        for ad, d in J[bolum].items():
            if isinstance(d, dict) and d.get("taslak"):
                a("- `%s.%s`: %s" % (bolum, ad, _h(d.get("aciklama", ""))))
    a("")
    return "\n".join(s)


def main():
    metin = uret()
    if "--denetle" in sys.argv:
        with open(BELGE, encoding="utf-8") as f:
            guncel = f.read() == metin
        print("PROTOKOL.md %s" % ("güncel" if guncel else "GÜNCEL DEĞİL: py -3 kod/ortak/protokol_belge_uret.py"))
        return 0 if guncel else 1
    with open(BELGE, "w", encoding="utf-8", newline="\n") as f:
        f.write(metin)
    print("yazıldı: %s (%d satır)" % (BELGE, metin.count("\n") + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
