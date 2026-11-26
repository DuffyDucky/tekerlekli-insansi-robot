"""Altı simülasyon testinin sonuçlarını tek, çevrimdışı açılan bir HTML sayfasında toplar.

Kullanım (bu klasörde):  py -3 testler_rapor.py
Çıktı: testler-rapor.html (aynı klasör). Dış kaynak yok; bütün biçem ve betik gömülü.

Her test bölümü iki katmanlı: üstte bu turun (tamamlama turu) sonucu ve "önce / şimdi" karşılaştırması, altta
açılır kutuda önceki turun ayrıntısı. Tablolardaki ve üst karar tablosundaki sayılar her koşuda sonuç CSV'lerinden
(ve seçim JSON'larından) yeniden sayılır. CSV'de olmayan birkaç sayı sonuç belgelerinden (SONUC.md) alınır: bunlar
sayfada † ile işaretlenir ve sayfanın sonunda listelenir; betik her birinin ilgili SONUC.md içinde hâlâ geçtiğini
denetler, geçmiyorsa durur. Yalnız standart kütüphane kullanılır.

Okunan bütün CSV'ler testlerin `sonuc/` klasöründe ve depoda tutulan dosyalardır; git dışı `sonuc/ham/` hiç okunmaz
(`oku` reddeder), bu yüzden betik temiz bir kopyada da çalışır. Keşif beyninin varsayılan sürümü `kesif/beyin.py`'den
okunur. Uçurumda güncel hüküm bağımsız hüküm 3'tür (`hukum3`: beş düzen, `sonuc/hukum3.csv` ve `hukum3_fiz.csv`;
onaylı seçim `secim.json`'dan); görülmüş ızgaradaki 6 / 10 / 14 sensör karşılaştırması (`katmanli`) "önce" olarak kalır.
"""
from __future__ import annotations

import csv
import datetime as _dt
import html
import json
import statistics
import sys
from pathlib import Path

BURASI = Path(__file__).resolve().parent            # kod/fizik/deneyler
FIZIK = BURASI.parent                                # kod/fizik
U = FIZIK / "ucurum" / "sonuc"
H = BURASI / "harita_eskimesi" / "sonuc"
T = BURASI / "tasinma" / "sonuc"
S = FIZIK / "sanalray" / "sonuc"
K = FIZIK / "kesif" / "sonuc"
CIKTI = BURASI / "testler-rapor.html"


# ------------------------------------------------------------------ yardımcılar
def oku(yol: Path) -> list[dict]:
    # yalnız depoda izlenen sonuç dosyaları: sonuc/ham git dışıdır, temiz bir kopyada bulunmaz
    if "ham" in Path(yol).parts:
        raise SystemExit(f"git dışı ham kayıt okunmaz: {Path(yol).name}")
    with open(yol, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def dogru(x) -> bool:
    return str(x).strip().lower() in ("true", "1", "1.0", "evet")


def say(x):
    try:
        if x is None or str(x).strip() == "":
            return None
        return float(x)
    except ValueError:
        return None


def sy(x, n=1) -> str:
    """Türkçe ondalık virgülle."""
    if x is None:
        return "-"
    if round(x, n) == 0:
        x = 0.0
    return f"{x:.{n}f}".replace(".", ",")


def tam(x) -> str:
    return str(int(round(x)))


def medyan(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def ort(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def e(s) -> str:
    return html.escape(str(s), quote=True)


_SONUC_ONBELLEK: dict[Path, str] = {}


def sonuc_var(klasor: Path, *parcalar: str) -> None:
    """SONUC.md'den alınan sayıların belgede hâlâ geçtiğini denetle."""
    yol = klasor / "SONUC.md"
    if yol not in _SONUC_ONBELLEK:
        _SONUC_ONBELLEK[yol] = yol.read_text(encoding="utf-8")
    metin = _SONUC_ONBELLEK[yol]
    for p in parcalar:
        if p not in metin:
            raise SystemExit(f"SONUC.md'de bulunamadı ({yol.parent.parent.name}): {p!r}")


BELGE: list[tuple[str, str]] = []      # (bölüm, açıklama): sayfada † ile işaretli, sonuç belgesinden alınan sayılar


def bel(klasor: Path, bolum: str, gosterim: str, kanitlar, aciklama: str) -> str:
    """SONUC.md'den alınan sayıyı denetle, kaydet ve † ile işaretle."""
    sonuc_var(klasor, *kanitlar)
    if (bolum, aciklama) not in BELGE:
        BELGE.append((bolum, aciklama))
    return f"{gosterim}<sup class='bel' title='Sonuç belgesinden'>†</sup>"


def mn(xs):
    xs = [x for x in xs if x is not None]
    return min(xs) if xs else None


def mx(xs):
    xs = [x for x in xs if x is not None]
    return max(xs) if xs else None


def rz(metin, tur="uyari"):
    return f"<span class='rozet {tur}'>{metin}</span>"


def kesir(b, n, esik=None):
    """b/n; esik verilirse b < esik iken kötü renkli."""
    kotu = (b < esik) if esik is not None else False
    return f"<span class='{'kotu' if kotu else ''}'>{b}/{n}</span>"


# ------------------------------------------------------------------ HTML parçaları
def tablo(basliklar, satirlar, sinif="", not_=""):
    h = ["<div class='tablo-kap'><table class='veri " + sinif + "'><thead><tr>"]
    h += [f"<th>{b}</th>" for b in basliklar]
    h.append("</tr></thead><tbody>")
    for s in satirlar:
        h.append("<tr>" + "".join(f"<td>{c}</td>" for c in s) + "</tr>")
    h.append("</tbody></table></div>")
    if not_:
        h.append(f"<p class='tablo-not'>{not_}</p>")
    return "".join(h)


def cubuk_grafik(baslik, seriler, satirlar, en_buyuk, birim="", aciklama="", esik=None, esik_etiket=""):
    """seriler: [(ad, renk_degiskeni)], satirlar: [(etiket, [deger|None, ...], [metin|None, ...])]."""
    h = [f"<figure class='grafik' role='img' aria-label='{e(baslik)}'>"]
    h.append(f"<figcaption class='g-baslik'>{baslik}</figcaption>")
    if len(seriler) > 1:
        h.append("<div class='g-lejant'>" + "".join(
            f"<span class='lj'><i style='background:var({r})'></i>{ad}</span>" for ad, r in seriler) + "</div>")
    for etiket, degerler, metinler in satirlar:
        h.append(f"<div class='g-satir'><div class='g-etiket'>{etiket}</div><div class='g-cubuklar'>")
        for (ad, renk), d, m in zip(seriler, degerler, metinler):
            if d is None:
                h.append(f"<div class='g-cubuk'><span class='g-yok'>{m or 'koşulmadı'}</span></div>")
                continue
            gen = max(0.0, min(100.0, 100.0 * d / en_buyuk)) if en_buyuk else 0
            esik_html = ""
            if esik is not None:
                esik_html = f"<span class='g-esik' style='left:{100.0 * esik / en_buyuk:.2f}%'></span>"
            h.append(
                f"<div class='g-cubuk' title='{e(ad)}'><span class='g-iz'>{esik_html}"
                f"<span class='g-dolgu' style='width:{gen:.2f}%;background:var({renk})'></span></span>"
                f"<span class='g-deger'>{m if m is not None else sy(d)}{birim}</span></div>")
        h.append("</div></div>")
    if esik is not None and esik_etiket:
        h.append(f"<p class='g-not'><span class='g-esik-ornek'></span>{esik_etiket}</p>")
    if aciklama:
        h.append(f"<p class='g-not'>{aciklama}</p>")
    h.append("</figure>")
    return "".join(h)


def yigin_grafik(baslik, parcalar, satirlar, aciklama=""):
    """parcalar: [(ad, renk)], satirlar: [(etiket, [sayi,...], toplam)]."""
    h = [f"<figure class='grafik' role='img' aria-label='{e(baslik)}'>",
         f"<figcaption class='g-baslik'>{baslik}</figcaption>",
         "<div class='g-lejant'>" + "".join(
             f"<span class='lj'><i style='background:var({r})'></i>{ad}</span>" for ad, r in parcalar) + "</div>"]
    for etiket, sayilar, toplam in satirlar:
        h.append(f"<div class='g-satir'><div class='g-etiket'>{etiket}</div><div class='g-cubuklar'>"
                 "<div class='g-cubuk'><span class='g-iz g-yigin'>")
        for (ad, renk), n in zip(parcalar, sayilar):
            if n:
                h.append(f"<span class='g-parca' title='{e(ad)}: {n}' style='width:{100.0 * n / toplam:.2f}%;"
                         f"background:var({renk})'>{n}</span>")
        h.append(f"</span><span class='g-deger'>{toplam}</span></div></div></div>")
    if aciklama:
        h.append(f"<p class='g-not'>{aciklama}</p>")
    h.append("</figure>")
    return "".join(h)


def liste(maddeler):
    return "<ul>" + "".join(f"<li>{m}</li>" for m in maddeler) + "</ul>"


def bolum_parcalari(olculen, ana, grafik, oneri, iyimser, aciklar, hukum):
    return (
        f"<p class='hukum eski-hukum'><strong>Önceki turun hükmü.</strong> {hukum}</p>"
        f"<h3>Ne ölçüldü</h3>{olculen}"
        f"<h3>Ana tablo</h3>{ana}"
        f"<h3>Grafik</h3>{grafik}"
        f"<h3>Kırılma noktası ve öneri</h3><div class='oneri'>{oneri}</div>"
        "<div class='iki'>"
        f"<div><h3>Simülasyonun iyimser varsayımları</h3>{liste(iyimser)}</div>"
        f"<div><h3>Kalan açıklar</h3>{liste(aciklar)}</div>"
        "</div>"
    )


# ================================================================== 1. UÇURUM
def ucurum():
    s2 = oku(U / "sinama2.csv")
    karsi = oku(U / "sinama2_karsi.csv")
    dar_gel = oku(U / "dar_gelistirme.csv")
    durma = oku(U / "durma.csv")
    ilk = oku(U / "sinama.csv") + oku(U / "sinama_y.csv")

    yanlis = [r for r in s2 if r["alt"].startswith("yanlis_alarm")]
    ucr = [r for r in s2 if not r["alt"].startswith("yanlis_alarm")]
    r = {
        "ucurum_kosu": len(ucr),
        "dustu": sum(dogru(x["dustu"]) for x in ucr),
        "yanlis_kosu": len(yanlis),
        "yanlis_durma": sum(dogru(x["tetik"]) for x in yanlis),
        "toplam": len(s2),
        "hata": sum(1 for x in s2 if (x.get("hata") or "").strip()),
        "pay_dar": min(say(x["pay_min_cm"]) for x in ucr if x["alt"] == "dar"),
        "pay_genis": min(say(x["pay_min_cm"]) for x in ucr if x["alt"] == "ileri"),
        "pay_duz_039": min(say(x["pay_min_cm"]) for x in ucr
                           if x["alt"] == "ileri" and x["sahne"].startswith("merdiven") and say(x["v"]) == 0.39),
        "pay_geri": min(say(x["pay_min_cm"]) for x in ucr if x["alt"] == "geri"),
        "pay_donus": min(say(x["pay_min_cm"]) for x in ucr if x["alt"] == "donus" and say(x["pay_min_cm"]) is not None),
        "pay_yay": min(say(x["pay_min_cm"]) for x in ucr if x["alt"] == "yay"),
        "ilk_kosu": len(ilk), "ilk_dustu": sum(dogru(x["dustu"]) for x in ilk),
        "ilk_pay_039": min(say(x["pay_min_cm"]) for x in ilk
                           if x["alt"] == "ileri" and x["sahne"].startswith("merdiven") and say(x["v"]) == 0.39),
    }
    # dar açıklık: üç düzen
    duzen_ad = {"4OD+2AD_z120_e30": "6 sensör: 4 köşe + önde 2 iç (seçilen)",
                "3KOD+2AD_z120_e30": "5 sensör: 4 köşe + ön orta",
                "2KD+2AD_z120_e30": "4 köşe sensörü (ilk seçim)"}
    duzenler = list(duzen_ad)
    sahne_ad = {"acik_45": "0,45 m açıklık", "acik_55": "0,55 m açıklık", "acik_65": "0,65 m açıklık",
                "acik_75": "0,75 m açıklık", "acik_90": "0,90 m açıklık", "acik_60_sig": "0,60 m, 0,4 m sığ",
                "dar_merdiven_60": "0,60 m dar merdiven", "dar_merdiven_80": "0,80 m dar merdiven"}
    dar = [x for x in s2 if x["alt"] == "dar"] + karsi
    tab = {}
    for x in dar:
        k = (x["yerlesim"], x["sahne"])
        t = tab.setdefault(k, [0, 0, 99.0])
        t[0] += 1
        t[1] += dogru(x["dustu"])
        p = say(x["pay_min_cm"])
        if p is not None:
            t[2] = min(t[2], p)
    toplam_d = {d: [sum(tab[(d, s)][0] for s in sahne_ad), sum(tab[(d, s)][1] for s in sahne_ad),
                    min(tab[(d, s)][2] for s in sahne_ad)] for d in duzenler}
    r["dar_tab"] = tab
    r["dar_toplam"] = toplam_d
    # dar açıklık geliştirmesi
    gel = {}
    for x in dar_gel:
        if x["alt"] != "dar":
            continue
        k = (x["yerlesim"], x["sahne"])
        t = gel.setdefault(k, [0, 0])
        t[0] += 1
        t[1] += dogru(x["dustu"])
    r["gel_4kose"] = (sum(v[1] for k, v in gel.items() if k[0] == "2KD+2AD_z120_e30"),
                      sum(v[0] for k, v in gel.items() if k[0] == "2KD+2AD_z120_e30"))
    r["gel_5"] = (sum(v[1] for k, v in gel.items() if k[0] == "3KOD+2AD_z120_e30"),
                  sum(v[0] for k, v in gel.items() if k[0] == "3KOD+2AD_z120_e30"))
    r["gel_6"] = (sum(v[1] for k, v in gel.items() if k[0] == "4OD+2AD_z120_e30"),
                  sum(v[0] for k, v in gel.items() if k[0] == "4OD+2AD_z120_e30"))
    # durma yolu (düz zemin)
    dy = {}
    for x in durma:
        if x["sahne"] != "duz":
            continue
        ad = {"kes": "Yalnız motor kesme", "fren": "Kısa devre freni"}.get(x["fren"])
        if x["fren"] == "rampa" and say(x["fren_ivme"]) in (1.0, 2.0):
            ad = f"Etkin rampa freni {sy(say(x['fren_ivme']))} m/s²"
        if ad:
            dy.setdefault(ad, {})[say(x["v"])] = say(x["durma_yolu_m"]) * 100
    r["durma"] = dy
    inis = [x for x in durma if x["sahne"] == "rampa_10_inis" and x["fren"] != "kes"]
    kay = [say(x["kayma_hiz_1_2s"]) for x in inis]
    r["inis_kayma"] = (min(kay), max(kay))
    # geniş kenar ileri tablosu
    gen = {}
    for x in ucr:
        if x["alt"] != "ileri":
            continue
        k = ("merdiven" if x["sahne"].startswith("merdiven") else x["sahne"], say(x["v"]))
        t = gen.setdefault(k, [0, 0, 99.0])
        t[0] += 1
        t[1] += dogru(x["dustu"])
        t[2] = min(t[2], say(x["pay_min_cm"]))
    r["genis"] = gen

    b87 = bel(U, "Uçurum", "≈ 87 mm", ["≈ 87 mm"], "100 mm eşiğin göremediği en sığ düşüş ≈ 87 mm (önceki tur)")
    b00 = bel(U, "Uçurum", "0,0 mm", ["0,0 mm"], "LiDAR'ın merdivenli / merdivensiz tarama farkı 0,0 mm (önceki tur)")

    hukum = (f"Önde iki iç sensör eklenmiş altı sensörlü düzen, yeni sınamanın {r['ucurum_kosu']} uçurum koşusunda "
             f"düşme sayısı {r['dustu']}, {r['yanlis_kosu']} yanlış alarm koşusunda boşuna durma sayısı {r['yanlis_durma']}. "
             f"İlk seçilen dört köşe düzeni robottan dar açıklıkta "
             f"{toplam_d['2KD+2AD_z120_e30'][0]} koşunun {toplam_d['2KD+2AD_z120_e30'][1]}'inde düştü; seçim bu yüzden değişti.")

    olculen = (
        "<p>Aşağı inen merdiven, dik boşluk, kuyu, sahanlık köşesi ve robottan dar açıklıkta robotun zamanında durup "
        "durmadığı; aşağı bakan VL53L1X türü mesafe sensörünün sayısı, yeri, eğimi ve eşiği; fren türüne göre durma yolu; "
        "ani frende devrilme; sensör arızaları; LiDAR'ın merdiveni görüp görmediği. Hepsi MuJoCo fizik benzetiminde, "
        "önerilen firmware ve önde omni tekerli robot modeliyle (bugünkü robot değil). Ayar geliştirme koşularında yapıldı, hüküm ayrı "
        f"tohumlu sınamadan: sınama 2'de toplam {r['toplam']} koşu, {r['hata']} yazılım hatası.</p>")

    satirlar = []
    for s, ad in sahne_ad.items():
        hucre = []
        for d in duzenler:
            n, dus, p = tab[(d, s)]
            hucre.append(f"<span class='{'kotu' if dus else 'iyi'}'>{dus} / {n}</span> <span class='ince'>"
                         f"(pay {sy(p)} cm)</span>")
        satirlar.append([ad] + hucre)
    satirlar.append(["<strong>Toplam</strong>"] + [
        f"<strong>{toplam_d[d][1]} / {toplam_d[d][0]}</strong> <span class='ince'>(en küçük pay {sy(toplam_d[d][2])} cm)</span>"
        for d in duzenler])
    ana = tablo(["Dar açıklık (sınama 2)"] + [duzen_ad[d] for d in duzenler], satirlar,
                not_="Hücre: düşen koşu / koşu. Pay: teker temas noktasının kenara en yakın yatay mesafesi; eksi değer "
                     "tekerin boşluğa girdiği anlamına gelir. Seçim bu sınamadan önce, geliştirme koşularıyla yapıldı; "
                     "beşli ve dörtlü düzen burada yalnız karşılaştırma için koşuldu.")
    gtab = []
    for g, ad in (("merdiven", "Merdiven 15×28 ve 19×25 cm"), ("kuyu", "Kuyu (menzil dışı)"), ("kose", "Sahanlık köşesi")):
        gtab.append([ad] + [f"{gen[(g, v)][1]} / {gen[(g, v)][0]} <span class='ince'>(pay {sy(gen[(g, v)][2])} cm)</span>"
                            for v in (0.10, 0.25, 0.39)])
    ana += "<h4>Geniş kenara ileri yaklaşma, seçilen düzen</h4>" + tablo(
        ["Geometri", "0,10 m/s", "0,25 m/s", "0,39 m/s"], gtab,
        not_=f"Geri gitme, yerinde dönüş ve yay koşularında da düşme yok (en küçük pay {sy(r['pay_geri'])} / "
             f"{sy(r['pay_donus'])} / {sy(r['pay_yay'])} cm).")
    dtab = [[ad] + [sy(dy[ad][v]) + " cm" for v in (0.10, 0.25, 0.39)] for ad in
            ("Yalnız motor kesme", "Kısa devre freni", "Etkin rampa freni 1,0 m/s²", "Etkin rampa freni 2,0 m/s²")]
    ana += "<h4>Durma yolu, düz zemin (tetikten sonra)</h4>" + tablo(["Fren", "0,10 m/s", "0,25 m/s", "0,39 m/s"], dtab)

    grafik = cubuk_grafik(
        "Dar açıklıkta düşen koşu (sahne başına 225 koşu)",
        [(duzen_ad["2KD+2AD_z120_e30"], "--c-b"), (duzen_ad["3KOD+2AD_z120_e30"], "--c-c"),
         (duzen_ad["4OD+2AD_z120_e30"], "--c-a")],
        [(ad, [tab[(d, s)][1] for d in ("2KD+2AD_z120_e30", "3KOD+2AD_z120_e30", "4OD+2AD_z120_e30")],
          [str(tab[(d, s)][1]) for d in ("2KD+2AD_z120_e30", "3KOD+2AD_z120_e30", "4OD+2AD_z120_e30")])
         for s, ad in sahne_ad.items()],
        en_buyuk=max(1, max(tab[(d, s)][1] for d in duzenler for s in sahne_ad)),
        aciklama="Dört köşe sensörünün izi açıklığın iki yanındaki zemine düşüyor; çapraz dışa bakan ışın yan duvarı "
                 "yakın görüyor, eşik aşılmıyor ve teker boşluğa iniyor. Ön iç sensörler bu boşluğu kapatıyor.")

    oneri = liste([
        f"<strong>Sensör:</strong> 6 adet, yerden 120 mm, dikeyden 30° eğik. Köşeler çapraz dışa bakar, önde iki iç "
        f"sensör (merkezden ±85 mm) düz öne bakar. Eşik: açılışta ölçülen zemin mesafesi + 100 mm, sensör başına art "
        f"arda 3 örnek. Dönüş alamayan okumada robot önce yavaşlar, art arda 5'te durur.",
        f"<strong>Fren:</strong> yalnız motoru kesmek yetmez: 0,39 m/s'de durma yolu {sy(dy['Yalnız motor kesme'][0.39])} cm. "
        f"Etkin rampa freni 2,0 m/s² ile {sy(dy['Etkin rampa freni 2,0 m/s²'][0.39])} cm.",
        f"<strong>Hız (güncellendi):</strong> o turun sınamasında 0,39 m/s'de en küçük pay {sy(r['pay_dar'])} cm (dar "
        f"açıklık), geniş kenarda {sy(r['pay_genis'])} cm idi. Hız önerisi bu turda tekleşti: 0,25 m/s, dayanağı "
        "yukarıdaki duyarlılık ölçümü.",
        "<strong>Sensörden tasarruf gerekirse:</strong> beşli düzen (ön orta sensörlü) sınamada düşmedi ama geliştirmede "
        f"0,40 m açıklıkta {r['gel_5'][0]} / {r['gel_5'][1]} düştü; ancak en dar açıklık ≈ 0,45 m kabul edilirse "
        "ikinci seçenek. Geri gitme firmware'de yasaksa arka iki sensör çıkarılabilir.",
        f"<strong>Kırılma:</strong> 10° iniş rampasında her fren kipinde robot tam durmuyor, frenden sonra yaklaşık "
        f"{sy(r['inis_kayma'][1], 2)} m/s kaymaya devam ediyor. Rampa dibinde uçurum varsa bu düzen yetmez: "
        f"tutma freni gerekir (güncellendi: bu turda konum tutma eklendi). 100 mm eşik {b87}'den sığ düşüşü (tek basamak "
        f"kaldırım) görmez. LiDAR merdiveni hiç görmüyor (merdivenli ve merdivensiz tarama arasındaki en büyük fark {b00}).",
    ])
    iyimser = [
        "Sensör modeli varsayım: koni, en yakın öbek kuralı, gürültü. Ortam ışığı, cam / ayna / parlak siyah zemin, toz ve "
        "sensörler arası etkileşim yok.",
        "Saniyede 50 örnek ile 4 m menzil birlikte varsayıldı. Gerçek sensörde bu hız yalnız kısa menzil kipinde var; "
        "uzun kipte tetik gecikir ve 0,39 m/s'deki pay yaklaşık 2 cm azalır (koşulmadı).",
        "Firmware zamanlaması kusursuz; altı sensör aynı I2C hattında gecikmesiz ve birbirini etkilemeden okunuyor.",
        "Etek penceresi ışını kırpmıyor; sahne kenarları keskin, zemin düz; teker, sürtünme ve motor değerleri tahmin.",
    ]
    aciklar = [
        "0,40 m'den dar delik sınanmadı. İç ve köşe izleri arasında yaklaşık 0,21 m boşluk var; teker hizasında yaklaşık "
        "0,2 m'lik bir delik hiçbir izin altına girmeyebilir.",
        "Açıklığa yalnız ileri giderek yaklaşıldı; geri giderek ya da yerinde dönerek yaklaşma koşulmadı.",
        "Altı sensörlü düzenle parlak zemin taraması ve köşe sensörü arızası taraması yeniden koşulmadı.",
        "10° inişte tutma freni yok; inişte güvenli fren ivmesi ölçülerek belirlenmedi (1,5 m/s² önerisi ölçümle "
        "desteklenmiyor).",
        "3B gösterim görüntüsü eski dört sensörlü düzenle çekildi; dar açıklık gösterimi pencere açılarak denenmedi.",
    ]
    govde = bolum_parcalari(olculen, ana, grafik, oneri, iyimser, aciklar, hukum)
    ust = {
        "test": "Uçurum ve merdiven",
        "hukum": f"Altı aşağı bakan sensörle {r['ucurum_kosu']} uçurum koşusunda {r['dustu']} düşme, {r['yanlis_kosu']} "
                 f"yanlış alarm koşusunda {r['yanlis_durma']} boşuna durma; ilk seçilen dört köşe sensörü dar açıklıkta "
                 f"{toplam_d['2KD+2AD_z120_e30'][0]} koşunun {toplam_d['2KD+2AD_z120_e30'][1]}'inde düştü.",
        "karar": "Aşağı bakan sensör sayısı 4 değil 6 (120 mm yükseklik, 30° eğim, eşik zemin + 100 mm); yalnız motoru "
                 "kesmek yerine 2,0 m/s² etkin fren; ilk denemelerde hız 0,25 m/s; eğimde tutma freni olmadan uçurum "
                 "durdurmasına güvenilmez.",
    }
    return r, govde, ust


# ================================================================== 2. HARİTA ESKİMESİ
ETKEN = [
    ("kapi", "Kapı durumu değişen oran", lambda d: f"%{tam(d * 100)}"),
    ("cam", "Cam kapı oranı", lambda d: f"%{tam(d * 100)}"),
    ("menzil", "LiDAR'ın en uzun menzili", lambda d: f"{tam(d)} m"),
    ("donussuz", "Dönüş vermeyen yüzey oranı", lambda d: f"%{tam(d * 100)}"),
    ("odo_kayma", "Ani teker kayması", lambda d: f"{sy(d) if d % 1 else tam(d)} / dk"),
    ("esya", "Duvar dibinde eşya (adet / 10 m)", lambda d: sy(d) if d % 1 else tam(d)),
    ("grup", "Duran grup (duvardan içeri)", lambda d: f"{sy(d)} m"),
    ("insan", "Yürüyen insan (kişi / 10 m)", lambda d: sy(d) if d % 1 else tam(d)),
    ("olcek", "Harita ölçek hatası", lambda d: f"%{sy(d * 100) if (d * 100) % 1 else tam(d * 100)}"),
    ("genislik", "Koridor genişlik sapması", lambda d: f"±{sy(d * 100) if (d * 100) % 1 else tam(d * 100)} cm"),
    ("egrilme", "Koridor eğrilmesi (/ 20 m)", lambda d: f"{sy(d) if d % 1 else tam(d)}°"),
    ("gurultu", "LiDAR menzil gürültüsü", lambda d: f"{tam(d * 100)} cm"),
    ("odo_olcek", "Odometri öteleme hatası", lambda d: f"+%{sy(d * 100) if (d * 100) % 1 else tam(d * 100)}"),
    ("odo_donus", "Odometri dönüş hatası (ek)", lambda d: f"+%{tam(d * 100)}"),
]


def harita():
    ab = oku(H / "ab_2b.csv")
    ky = oku(H / "kayip_2b.csv")
    ky_ek = oku(H / "kayip_ek_2b.csv")     # bu tur: kayıp robotta genişlik sapması
    mj = oku(H / "mujoco.csv")
    vr = oku(H / "varyant_2b.csv")

    def kosul_say(rows):
        d = {}
        for x in rows:
            t = d.setdefault(x["kosul"], [0, 0, x["etken"], int(x["kademe"]), say(x["deger"])])
            t[0] += 1
            t[1] += dogru(x["basari"])
        return d

    a, k = kosul_say(ab), kosul_say(ky + ky_ek)
    r = {"ab_n": len(ab), "ab_basari": sum(dogru(x["basari"]) for x in ab)}
    bas = [x for x in ab if not dogru(x["basari"])]
    r["bas_n"] = len(bas)
    r["bas_sicrama"] = sum(1 for x in bas if (say(x["konum_maks_m"]) or 0) > 1.0)
    r["bas_vardim"] = sum(1 for x in bas if x["bitis"] == "beyin")
    r["bas_emin"] = sum(1 for x in bas if (say(x["konum_kesin_yanlis"]) or 0) > 0)
    r["bas_sinirda"] = sum(1 for x in bas if 0.30 <= (say(x["varis_hatasi_m"]) or 9) < 0.35)
    r["temas_ab"] = sum(int(say(x["temas_olay"]) or 0) for x in ab)
    r["temas_ky"] = sum(int(say(x["temas_olay"]) or 0) for x in ky)
    r["ky_n"] = len(ky)
    abi = {(x["kosul"], x["koridor"], x["tohum"], x["hedef"]): dogru(x["basari"]) for x in ab}
    es = [(dogru(x["basari"]), abi.get((x["kosul"], x["koridor"], x["tohum"], x["hedef"]))) for x in mj]
    r["mj_n"] = len(mj)
    r["mj_ayni"] = sum(1 for m, b in es if b is not None and m == b)
    r["mj_uyusmayan_mj_iyi"] = sum(1 for m, b in es if b is not None and m and not b)
    okul = {s: a[f"okul_{s}"][:2] for s in ("hafif", "orta", "agir")}
    okul_k = {s: k[f"okul_{s}"][:2] for s in ("hafif", "orta", "agir")}
    r["okul"], r["okul_k"] = okul, okul_k
    r["taban"] = a["taban"][:2]

    def kirilma(d, et):
        kad = sorted((v[3], v[4], v[0], v[1]) for kk, v in d.items() if v[2] == et)
        for kd, dg, n, b in kad:
            if b < 0.9 * n:
                return kd, dg, kad
        return None, None, kad

    satirlar, ortalamalar = [], []
    r["kir"] = {}
    for et, ad, bic in ETKEN:
        kd, dg, kad = kirilma(a, et)
        kkd, kdg, kkad = kirilma(k, et)
        r["kir"][et] = (dg, [(x[1], x[3], x[2]) for x in kad])
        sinirda = " <span class='ince'>(sınırda)</span>" if et in ("cam", "odo_kayma") and dg is not None else ""
        ortalamalar.append((ad, 100.0 * sum(x[3] for x in kad) / sum(x[2] for x in kad),
                            min(x[3] for x in kad), kad[0][2]))
        hucre_ab = ", ".join(f"<span class='{'kotu' if b < 0.9 * n else ''}'>{bic(dgr)}: {b}/{n}</span>"
                             for _, dgr, n, b in kad)
        hucre_k = (", ".join(f"<span class='{'kotu' if b < 0.9 * n else ''}'>{bic(dgr)}: {b}/{n}</span>"
                             for _, dgr, n, b in kkad) if kkad else "koşulmadı")
        satirlar.append([ad, hucre_ab, f"<strong>{bic(dg)}</strong>{sinirda}" if dg is not None else "kırmadı",
                         hucre_k, (f"<strong>{bic(kdg)}</strong>" if kdg is not None else ("kırmadı" if kkad else "-"))])
    okul_ad = {"hafif": "hafif", "orta": "orta", "agir": "ağır"}
    satirlar.insert(0, ["<strong>Sıradan okul günü</strong> (kapı, cam, eşya, insan birlikte)",
                        ", ".join(f"<span class='{'kotu' if okul[s][1] < 0.9 * okul[s][0] else ''}'>{okul_ad[s]}: "
                                  f"{okul[s][1]}/{okul[s][0]}</span>" for s in okul),
                        "<strong>hafif</strong>",
                        ", ".join(f"<span class='kotu'>{okul_ad[s]}: {okul_k[s][1]}/{okul_k[s][0]}</span>" for s in okul_k),
                        "<strong>hafif</strong>"])
    # Zarar sırası (düzeltilmiş): yalnız tam ızgaralı A'dan B'ye ortalaması, eşitlikte en kötü kademe.
    # Sıradan okul günü karma bir koşul (3 kademe); sıraya girmez.
    ortalamalar.sort(key=lambda x: (round(x[1], 6), x[2] / x[3]))
    r["siralama"] = ortalamalar
    kisa = {"Kapı durumu değişen oran": "kapı", "Cam kapı oranı": "cam", "LiDAR'ın en uzun menzili": "menzil",
            "Dönüş vermeyen yüzey oranı": "dönüşsüz yüzey", "Ani teker kayması": "ani kayma",
            "Duvar dibinde eşya (adet / 10 m)": "eşya", "Duran grup (duvardan içeri)": "grup"}
    parca, onceki = [], None
    for ad, o, mnb, n in ortalamalar:
        if o >= 99.99:
            break
        if onceki is not None:
            parca.append("=" if abs(o - onceki) < 1e-9 else "&gt;")
        parca.append(f"{kisa.get(ad, ad)} (%{tam(o)})")
        onceki = o
    r["sira_metin"] = " ".join(parca) + " &gt; geri kalanı (%100)"
    r["a"] = a

    # izleme seçeneği (ayrı tohumlar)
    vd = {}
    for x in vr:
        t = vd.setdefault((x["varyant"], x["kosul"]), [0, 0])
        t[0] += 1
        t[1] += dogru(x["basari"])
    r["varyant"] = vd
    varyantlar = sorted({x["varyant"] for x in vr})
    r["varyant_adlar"] = varyantlar

    hukum = (f"Koridorun geometrisindeki küçük hatalar, ölçüm gürültüsü, odometri sapması ve yol veren insanlar gezinmeyi "
             f"bozmuyor. Kapıların dörtte biri haritadakinden farklı olunca, kapıların bir bölümü cam olunca, LiDAR'ın "
             f"menzili 4 m'ye inince ya da duvarların dörtte üçü dönüş vermeyince bozuluyor. Sıradan bir okul gününün "
             f"hafif hâlinde A'dan B'ye {okul['hafif'][1]}/12, orta hâlinde {okul['orta'][1]}/12, ağır hâlinde "
             f"{okul['agir'][1]}/12. Bozulma ani ve çoğunlukla fark edilmeden oluyor.")
    olculen = (
        "<p>Robotun haritası ile dünya artık aynı değilken koridor gezinmesi. Konumlayıcı, rota ve izleyici "
        "değiştirilmedi; yalnız dünya bozuldu: kapılar, cam, eşya, insan, harita geometrisi, LiDAR ve odometri hataları, "
        f"her biri 4 kademede, ayrıca karma bir okul günü 3 kademede. 2B benzeticide {r['ab_n']} A'dan B'ye ve "
        f"{r['ky_n']} kayıp robot koşusu (koşul başına 6 koridor × 2 tohum = 12 koşu), MuJoCo'da {r['mj_n']} "
        "doğrulama koşusu. Ana ızgarada hiçbir ayar yapılmadı. Başarı: robotun hedefin 0,3 m içinde durması.</p>")
    ana = tablo(["Etken", "A'dan B'ye: kademe başına başarı", "A'dan B'ye kırılma", "Kayıp robot: ölçülen kademeler",
                 "Kayıp kırılma"], satirlar,
                not_="Kırılma: başarının %90'ın altına indiği (12 koşuda 10 ya da daha az) ilk kademe. 12 koşuyla "
                     "kırılma kademesi ± 1 kademe okunmalı. Kayıp robot ızgarası daraltıldı: çoğu etkende yalnız en ağır "
                     "kademe koşuldu.")
    grafik = cubuk_grafik(
        "A'dan B'ye ortalama başarı, etken başına bütün kademeler (%)",
        [("ortalama başarı", "--c-a")],
        [(ad, [o], [f"%{tam(o)} <span class='ince'>(en kötü {mn}/{n})</span>"]) for ad, o, mn, n in ortalamalar],
        en_buyuk=100, esik=90, esik_etiket="%90 çizgisi",
        aciklama="Sıra (güncellendi): yalnız bütün kademeleri koşulmuş A'dan B'ye ortalaması (etken başına 48 koşu), "
                 "eşitlikte en kötü kademe. Kayıp robot sıraya girmez, çünkü orada etkenlerin ölçülen kademe sayısı eşit "
                 "değil. Sıradan okul günü karma bir koşul olduğu için sıraya girmez (tabloda ayrı satır).")
    vsat = []
    for kos in ("kapi_3", "kapi_4", "cam_4", "donussuz_4", "okul_hafif", "okul_orta", "okul_agir"):
        if ("varsayilan", kos) in vd and ("izleme", kos) in vd:
            vsat.append(kos)
    kos_ad = {"kapi_3": "kapı %50", "kapi_4": "kapı %100", "cam_4": "cam %100", "donussuz_4": "dönüşsüz %75",
              "okul_hafif": "okul günü hafif", "okul_orta": "okul günü orta", "okul_agir": "okul günü ağır"}
    oneri = liste([
        f"<strong>Nasıl bozuluyor:</strong> A'dan B'ye {r['bas_n']} başarısızlığın {r['bas_sicrama']}'ünde konum "
        f"tahmini 1 m'den çok sıçradı (düzenli kapı ritminde benzer bir yere), {r['bas_vardim']}'ünde robot yanlış yerde "
        f"\"vardım\" dedi, {r['bas_emin']}'ünde konumlayıcı yanlış konumundan emindi.",
        f"<strong>Sınırdaki başarısızlıklar:</strong> {r['bas_sinirda']} başarısızlık hedefe 0,30–0,34 m'de durdu. Bunlar "
        "başarı sayılsaydı cam kapının kırılması %25'ten %50'ye kayar, ani teker kayması hiçbir kademede kırmazdı; bu "
        "iki etken \"kıran\" değil \"sınırda\" sayılmalı.",
        "<strong>Ucuz düzeltme önerisi (varsayılan değişmedi):</strong> başlangıcı bilinen gezinmede konumlayıcının "
        "rastgele saçmasını kapatmak (\"izleme\"). Ayrı tohumlarda: " + "; ".join(
            f"{kos_ad[kk]} {vd[('varsayilan', kk)][1]}/12 → {vd[('izleme', kk)][1]}/12" for kk in vsat)
        + ". Bedeli: robot gerçekten başka yere taşınırsa kendini kurtaramaz (bkz. taşınma testi).",
        f"<strong>Temas:</strong> A'dan B'ye {r['ab_n']} koşuda {r['temas_ab']} temas; kayıp robotun keşfinde "
        f"{r['ky_n']} koşuda {r['temas_ky']}, çünkü dönüş vermeyen duvar keşifte boş alan sayılıyor.",
        f"<strong>MuJoCo ile 2B:</strong> aynı tohumlarda {r['mj_n']} koşunun {r['mj_ayni']}'ü aynı sonucu verdi; uyuşmayan "
        f"{r['mj_uyusmayan_mj_iyi']} koşunun hepsinde 2B başarısız, MuJoCo başarılı.",
    ])
    iyimser = [
        "Duvarlar ideal ince levha, ışın sonsuz ince; çoklu yansıma ve geliş açısına bağlı dönüş kaybı yok. Cam yalnız "
        "kapılarda ve yalnız 2B'de.",
        "Kapı kanadı koridora açılmıyor; eşya yolu kapatmıyor; insanlar robota yol veriyor, grup 30 s'de dağılıyor.",
        "Taban harita kusursuz (sahneden üretildi); gerçek haritanın yerel hataları yok.",
        "2B robot kinematik, sonar yok; tek kat, düz zemin; LiDAR eğimi, titreşim ve gecikme yok.",
    ]
    aciklar = [
        "Kayıp robot 60 koşulun 20'sinde koşuldu; koridor genişliği etkeni kayıpta koşulmamıştı (güncellendi: bu turda "
        "4 kademede koşuldu, yukarıda).",
        "MuJoCo'da yalnız A'dan B'ye, koşul başına 3 koşu; cam kapı MuJoCo'da modellenemedi.",
        "İzleme seçeneği yalnız A'dan B'ye için ölçüldü; kayıp robotun karardan sonraki evresi ve kaçırılma algısıyla "
        "birlikte ölçülmedi. Karar proje sahibinin.",
        "Kayıp robotun keşfi dönüş vermeyen duvara çarpıyor; dönüşsüz ışını boş alan saymamak önerildi, ölçülmedi.",
        "Başarısızlıklar iki koridorda toplanıyor; etkin örneklem 6 koridorla sınırlı.",
    ]
    govde = bolum_parcalari(olculen, ana, grafik, oneri, iyimser, aciklar, hukum)
    k25 = next(v[1] for kk, v in a.items() if v[2] == "kapi" and v[3] == 2)
    ust = {
        "test": "Harita eskimesi",
        "hukum": f"Geometri hataları, gürültü, odometri sapması ve yol veren insan kırmıyor; kapıların dörtte biri değişince "
                 f"A'dan B'ye {k25}/12'ye, sıradan okul gününün hafif hâlinde {okul['hafif'][1]}/12'ye, ağır hâlinde "
                 f"{okul['agir'][1]}/12'ye düşüyor ve bozulma ani oluyor.",
        "karar": "Haritaya güvenmeden önce okul koridorunda LiDAR'ın dönüş alamadığı yüzeyler ve haritanın gün içinde ne "
                 "kadar eskidiği ölçülmeli; kapı durumu değişen koridorda harita sık güncellenmeli; bilinen başlangıçta "
                 "rastgele saçmayı kapatma seçeneği değerlendirilmeli.",
    }
    return r, govde, ust


# ================================================================== 3. TAŞINMA
TUR = [("ayni_uzak", "Aynı koridorda uzağa"), ("ters180", "Yerinde 180° çevrilme"),
       ("kucuk", "1–3 m kaydırma"), ("baska_koridor", "Başka koridora")]
YA = [("ya_taban", "bozulmasız"), ("ya_insan_2", "insan 1 / 10 m"), ("ya_esya_2", "eşya 1 / 10 m"),
      ("ya_karma_2", "insan + eşya 1 / 10 m"), ("ya_karma_3", "insan + eşya 2 / 10 m")]


def tasinma():
    t = [x for x in oku(T / "tasinma_2b.csv") if x["kume"] == "sinama"]
    mj = oku(T / "mujoco.csv")
    ger = oku(T / "gerileme.csv")

    def grup(sen, kos, su):
        return [x for x in t if x["senaryo"] == sen and x["kosul"] == kos and x["surum"] == su]

    r = {}
    tas = [x for x in t if not x["kosul"].startswith("ya_")]
    ab_v3 = [x for x in tas if x["senaryo"] == "ab" and x["surum"] == "v3"]
    r["ab_v3_n"] = len(ab_v3)
    r["ab_v3_var"] = sum(dogru(x["basari"]) for x in ab_v3 if x["kosul"] != "baska_koridor")
    r["ab_v3_yanlis_vardim"] = sum(1 for x in ab_v3 if x["bitis"] == "beyin bitti" and not dogru(x["basari"]))
    r["ab_v3_tepki"] = sum(1 for x in ab_v3 if say(x["tepki_s"]) is not None)
    algi = [x for x in tas if x["surum"] == "algi"]
    r["algi_n"] = len(algi)
    r["algi_fark"] = sum(1 for x in algi if say(x["tepki_s"]) is not None)
    r["algi_fark_med"] = medyan([say(x["tepki_s"]) for x in algi])
    r["algi_fark_max"] = max(say(x["tepki_s"]) for x in algi if say(x["tepki_s"]) is not None)
    r["algi_yanlis_vardim"] = sum(1 for x in algi if x["senaryo"] == "ab" and x["bitis"] == "beyin bitti"
                                  and not dogru(x["basari"]))
    r["temas"] = sum(int(say(x["temas_sonra"]) or 0) for x in tas)

    def mm(xs, n=1):
        xs = [say(x) for x in xs if say(x) is not None]
        if not xs:
            return "-"
        return f"{sy(medyan(xs), n)} / {sy(max(xs), n if max(xs) < 10 else 0)}"

    satirlar, gsat = [], []
    for sen, sad in (("ab", "Tek haritalı A'dan B'ye"), ("cok", "6 haritayla konum bulan sürüş")):
        for kos, kad in TUR:
            v3, al = grup(sen, kos, "v3"), grup(sen, kos, "algi")
            bv3, bal = sum(dogru(x["basari"]) for x in v3), sum(dogru(x["basari"]) for x in al)
            fark = [x for x in al if say(x["tepki_s"]) is not None]
            not_ = " <span class='ince'>(güvenli durma)</span>" if (sen == "ab" and kos == "baska_koridor") else ""
            satirlar.append([sad, kad, f"<span class='{'kotu' if bv3 < 0.9 * len(v3) else ''}'>{bv3}/{len(v3)}</span>{not_}",
                             f"{bal}/{len(al)}{not_}",
                             f"{len(fark)}/{len(al)} <span class='ince'>({mm([x['tepki_s'] for x in fark])} s)</span>",
                             f"{mm([x['yanlis_surus_s'] for x in v3])} s", f"{mm([x['yanlis_surus_s'] for x in al])} s"])
            gsat.append((f"{'Tek harita' if sen == 'ab' else '6 harita'}: {kad.lower()}", [bv3, bal],
                         [f"{bv3}/12", f"{bal}/12"]))
            r[(sen, kos)] = (bv3, bal, len(v3))
    ana = tablo(["Sürüş", "Taşıma türü", "Varış: bugünkü (v3)", "Varış: taşınma algılı", "Algılı sürüm fark etti "
                 "(ortanca / en çok)", "Yanlış konumla sürüş, v3 (ortanca / en çok)", "Yanlış konumla sürüş, algılı"],
                satirlar,
                not_="Sınama kümesi, 2B, koşul başına 12 koşu (6 koridor × 2 tohum). Tek haritalı sürüşte başka koridora "
                     "taşımada hedef yok; başarı, robotun yardım bekleyip güvenle durması. İki sürümde de temas "
                     f"{r['temas']}.")
    ysat = []
    for kos, kad in YA:
        sat = [kad]
        for sen in ("ab", "cok"):
            al, v3 = grup(sen, kos, "algi"), grup(sen, kos, "v3")
            n_al = sum(1 for x in al if (say(x["kayboldum"]) or 0) > 0)
            sat += [f"<span class='{'kotu' if n_al else ''}'>{n_al}/{len(al)}</span>",
                    f"{sum(dogru(x['basari']) for x in al)}/{len(al)}", f"{sum(dogru(x['basari']) for x in v3)}/{len(v3)}"]
        ysat.append(sat)
    ana += "<h4>Yanlış alarm (taşıma yok)</h4>" + tablo(
        ["Koşul", "Tek harita: boşuna \"kayboldum\" (koşu)", "Tek harita: varış algılı", "Tek harita: varış v3",
         "6 harita: boşuna \"kayboldum\"", "6 harita: varış algılı", "6 harita: varış v3"], ysat,
        not_="Eşyalı koşullardaki ilk alarmların çoğu, konumlayıcının gerçek konum doğruyken kendi kendine metrelerce "
             "sıçramasından geliyor; v3'ün 6 haritalı sürüşü de aynı koşularda aynı sayıda \"konum sıçradı\" tepkisi "
             "veriyor.")
    grafik = cubuk_grafik("Taşındıktan sonra hedefe varış (12 koşu)",
                          [("bugünkü sürüş (v3)", "--c-b"), ("taşınma algılı sürüm", "--c-a")], gsat, en_buyuk=12,
                          aciklama="Tek haritalı sürüşte başka koridora taşıma için çubuk, güvenle durup yardım "
                                   "beklemeyi gösterir.")
    mjs = {}
    for x in mj:
        kk = (x["kosul"], x["surum"])
        tt = mjs.setdefault(kk, [0, 0])
        tt[0] += 1
        tt[1] += dogru(x["basari"])
    r["mj"] = mjs
    g_algi = sum(int(say(x["yanlis_koridor_kesin_adim_algi"]) or 0) for x in ger)
    g_v3 = sum(int(say(x["yanlis_koridor_kesin_adim_v3"]) or 0) for x in ger)
    r["ger"] = (len(ger), sum(1 for x in ger if (say(x["kayboldum"]) or 0) > 0), g_v3, g_algi,
                sum(dogru(x["son_dogru_algi"]) for x in ger))
    mjm = "; ".join(f"{kad.lower()} v3 {mjs[(kos, 'v3')][1]}/{mjs[(kos, 'v3')][0]}, algılı {mjs[(kos, 'algi')][1]}/"
                    f"{mjs[(kos, 'algi')][0]}" for kos, kad in TUR if (kos, "v3") in mjs)
    hukum = (f"Bugünkü sürüş (v3) robotun kaldırılıp başka yere konduğunu fark etmiyor; tek haritalı sürüş 48 taşımanın "
             f"{r['ab_v3_yanlis_vardim']}'sinde yanlış yerde \"vardım\" dedi ve hiçbirinde kaybolduğunu söylemedi. "
             f"İsteğe bağlı taşınma algılı sürüm {r['algi_n']} taşımanın {r['algi_fark']}'inde ortanca "
             f"{sy(r['algi_fark_med'])} s'de fark etti. Bedeli eşyalı koridorda yanlış alarm.")
    olculen = (
        "<p>Robot rota üzerindeyken hakem onu anlık olarak başka bir yere koydu: aynı koridorda uzağa, yerinde 180°, "
        "1–3 m kaydırma, başka koridora. Odometri değişmedi; beyin yalnız LiDAR taraması ve odometri gördü. İki sürüş "
        "(tek haritalı A'dan B'ye ve 6 haritayla konum bulan sürüş) iki sürümle eşli koşuldu: bugünkü v3 ve taşınma "
        "algısı + durma + baştan konum arama + yavaş keşif ekleyen deneme sürümü. Algının eşikleri geliştirme kümesinde "
        "donduruldu, sınama bir kez koşuldu.</p>")
    oneri = liste([
        "<strong>Kırılma:</strong> v3 için en kötüsü başka koridor (tek haritalı sürüş hiç kurtulamaz) ve aynı koridorda "
        f"uzağa taşıma ({r[('ab', 'ayni_uzak')][0]}/12). Algılı sürüm için en zor tür 180° çevrilme: tarama ters yönde de "
        "haritaya uyuyor, en geç fark edilen ve en geç bulunan tür.",
        "<strong>Bedel:</strong> taşıma yokken bozulmasız ve insanlı koridorda boşuna alarm yok; eşya varken var ve 6 "
        "haritalı sürüşte varışı düşürüyor, çünkü baştan konum arama eşyalı koridorda yine benzer bir yere karar veriyor. "
        "Öneri (ölçülmedi): konum sıçramasıyla gelen alarmda önce durup mevcut tahminin oturmasını beklemek, baştan "
        "aramayı yalnız tarama haritaya hiç uymadığında yapmak.",
        f"<strong>MuJoCo doğrulaması</strong> (5 koşu / koşul): {mjm}.",
        f"<strong>Eski kayıtlarla gerileme denetimi</strong> ({r['ger'][0]} kayıt, sürüşsüz): algı {r['ger'][1]} kez "
        f"tetiklendi; yanlış koridora kesin adım {r['ger'][2]} → {r['ger'][3]}; sonda doğru {r['ger'][4]}/{r['ger'][0]}.",
        "<strong>Karar:</strong> varsayılan v3 kaldı; algılı sürümü gerçek robota almak proje sahibinin kararı.",
    ])
    iyimser = [
        "Taşıma anlık: kaldırırken tekerin havada dönmesi (odometriye sahte yol), LiDAR'ın taşıyan kişiyi görmesi ve "
        "konulduktan sonraki sarsıntı yok.",
        "Taşımalı koşularda dünya bozulmamış; yanlış alarm yalnız insan ve eşyayla ölçüldü.",
        "2B benzetici (önceki testte MuJoCo'ya göre konum hatasında iyimser); gecikme yok; insanlar yol veriyor.",
        "Algının Pi 5'teki süresi ölçülmedi.",
    ]
    aciklar = [
        "Cam, dönüş vermeyen yüzey, kapı değişimi ve kısa menzille algının yanlış alarmı ölçülmedi; bunlar gerçek okulda "
        "yanlış alarmı artırabilir.",
        "Kurtarmadaki yanlış alarm bedeli çözülmedi (yukarıdaki öneri ölçülmedi).",
        "Gerileme denetimi küçültülmüş alt kümede ve sürüşsüz yapıldı; tam koşu yapılmadı.",
        "MuJoCo'da başka koridor ve 6 haritalı sürüş koşulmadı.",
    ]
    govde = bolum_parcalari(olculen, ana, grafik, oneri, iyimser, aciklar, hukum)
    ust = {
        "test": "Çalışırken taşınma",
        "hukum": f"Bugünkü sürüş taşınmayı fark etmiyor (tek haritalı sürüşte 48 taşımanın {r['ab_v3_yanlis_vardim']}'sinde "
                 f"yanlış yerde \"vardım\"); taşınma algılı deneme sürümü {r['algi_n']} taşımanın {r['algi_fark']}'inde "
                 f"ortanca {sy(r['algi_fark_med'])} s'de fark etti, ama eşyalı koridorda boşuna alarm veriyor.",
        "karar": "Taşınma algısını gerçek robota alıp almama kararı; almadan önce cam, açık kapı ve eşyalı koridorda "
                 "yanlış alarm ve kaldırma sırasında tekerin boşa dönmesi ölçülmeli. Bugün varsayılan değişmedi.",
    }
    return r, govde, ust


# ================================================================== 4. SANAL RAY
def sanalray():
    ab = oku(S / "ab_sinama.csv")
    ky = oku(S / "kayip_sinama.csv")
    gv = oku(S / "gorunurluk.csv")
    bt24 = bel(S, "Sanal ray", "24/24", ["24/24", "0,048"], "LiDAR'lı taban A'dan B'ye 24/24, varış hatası 0,048 m (önceki tur)")
    bt048 = bel(S, "Sanal ray", "0,048", ["0,048"], "LiDAR'lı taban A'dan B'ye 24/24, varış hatası 0,048 m (önceki tur)")
    bt20 = bel(S, "Sanal ray", "20/20", ["20/20", "26,5"], "LiDAR'lı taban kayıp robot 20/20, karar süresi 26,5 s (önceki tur)")
    bt265 = bel(S, "Sanal ray", "26,5", ["26,5"], "LiDAR'lı taban kayıp robot 20/20, karar süresi 26,5 s (önceki tur)")

    def grp(rows, anahtar):
        d = {}
        for x in rows:
            d.setdefault(tuple(x[k] for k in anahtar), []).append(x)
        return d

    r = {"ab_n": len(ab), "ab_b": sum(dogru(x["basari"]) for x in ab)}
    g = grp(ab, ("aralik", "donus_fazlasi", "kafa"))
    sira = [(("5", "0.0", "sabit"), "Etiket 5 m arayla, dönüş hatası %0, sabit kafa"),
            (("5", "0.14", "sabit"), "5 m, dönüş hatası %14, sabit kafa"),
            (("5", "0.25", "sabit"), "5 m, dönüş hatası %25, sabit kafa"),
            (("5", "0.25", "tarayan"), "5 m, %25, tarayan kafa"),
            (("8", "0.25", "sabit"), "8 m arayla, %25, sabit kafa"),
            (("kavsak", "0.25", "tarayan"), "Yalnız uç, köşe ve kavşak etiketleri, %25, tarayan kafa")]
    # anahtar biçimini CSV'ye uydur
    anahtarlar = {}
    for kk in g:
        anahtarlar[(kk[0], str(float(kk[1])), kk[2])] = kk
    satirlar = []
    r["plan5"] = [0, 0]
    for kk, ad in sira:
        rows = g[anahtarlar[(kk[0], str(float(kk[1])), kk[2])]]
        b = sum(dogru(x["basari"]) for x in rows)
        if kk[0] == "5" and kk[2] == "sabit":
            r["plan5"][0] += b
            r["plan5"][1] += len(rows)
        va = [say(x["varis_hatasi_m"]) for x in rows]
        ya = [say(x["en_yanal_sapma_m"]) for x in rows]
        satirlar.append([ad, f"<span class='{'kotu' if b < len(rows) else ''}'>{b}/{len(rows)}</span>",
                         f"{sy(ort(va), 3)} / {sy(max(va), 3)}", f"{sy(ort(ya), 3)} / {sy(max(ya), 3)}",
                         str(sum(int(say(x["temas_olay"]) or 0) for x in rows))])
    satirlar.append(["LiDAR'lı taban (karşılaştırma)", bt24, bt048, "ölçülmedi", "0"])
    r["varis_ort"] = ort([say(x["varis_hatasi_m"]) for x in ab
                          if x["aralik"] == "5" and x["kafa"] == "sabit"])
    ana = tablo(["A'dan B'ye koşulu (sınama koridorları)", "Başarı", "Varış hatası ort / en (m)",
                 "Raydan yanal sapma ort / en (m)", "Duvar teması"], satirlar,
                not_="Sınama: 4 koridor, tohum 1, koridor başına 2 hedef. LiDAR'lı taban sayıları sanal ray sonuç "
                     "belgesinden. 5 m planda yanal sapma büyük ölçüde başlangıçtaki sapmadan geliyor; dönüş hatası "
                     "kademelerini ayırt etmiyor.")
    kg = grp(ky, ("kafa",))
    ksat = []
    r["kayip"] = {}
    for kafa, ad in (("sabit", "Sabit kafa (yerinde tur)"), ("tarayan", "Tarayan kafa")):
        rows = kg[(kafa,)]
        b = sum(dogru(x["basari"]) for x in rows)
        r["kayip"][kafa] = (b, len(rows), ort([say(x["ilk_etiket_s"]) for x in rows]),
                            ort([say(x["lokalize_s"]) for x in rows]))
        ksat.append([ad, f"<span class='{'kotu' if b < len(rows) else ''}'>{b}/{len(rows)}</span>",
                     f"{sy(ort([say(x['ilk_etiket_s']) for x in rows]))} / {sy(max(say(x['ilk_etiket_s']) for x in rows))}",
                     f"{sy(ort([say(x['lokalize_s']) for x in rows]))} / {sy(max(say(x['lokalize_s']) for x in rows))}",
                     sy(ort([say(x["sure_s"]) for x in rows])), str(sum(int(say(x["temas_olay"]) or 0) for x in rows))])
    ksat.append(["LiDAR'lı taban (karar)", bt20, "-", bt265, "-", "0"])
    ana += "<h4>Rastgele bırakılma (robot nerede olduğunu bilmeden başlar)</h4>" + tablo(
        ["Kafa", "Başarı", "İlk etiket görülme ort / en (s)", "Konumlanma süresi ort / en (s)", "Toplam süre ort (s)",
         "Temas"], ksat,
        not_="Konumlanma: süzgecin 3,5 m içindeki bir etiketten başlatıldığı an; LiDAR'lı karar süresiyle bu "
             "karşılaştırılır. Yanlış koridor seçilmemesi kurgu gereği: her koridorun etiket kimlikleri ayrı.")
    basarisiz = [x for x in ky if not dogru(x["basari"])]
    r["tek_bas"] = basarisiz[0] if basarisiz else None
    # görünürlük: en uzak güvenilir mesafe (algılama oranı o mesafeye dek kesintisiz >= 0,75)
    q = {}
    for x in gv:
        if x["yukseklik"] == "goz" and x["cozunurluk"] == "1152x648":
            q.setdefault((x["mercek"], x["boy_cm"], x["bozulma"], x["aci_derece"]), []).append(
                (say(x["mesafe_m"]), say(x["algilama_orani"])))

    def uzak(rows):
        en = 0.0
        for m, o in sorted(rows):
            if o is not None and o >= 0.75:
                en = m
            else:
                break
        return en

    acilar = ["0", "30", "50", "65", "75"]
    menzil = {(mr, b, a): uzak(q[(mr, b, "temiz", a)]) for mr in ("std", "genis") for b in ("10", "15", "20")
              for a in acilar}
    r["menzil"] = menzil
    r["bozulma0"] = {bz: max(uzak(q[("std", "15", bz, a)]) for a in acilar)
                     for bz in ("parlama", "kapanma25", "kapanma50")}
    grafik = cubuk_grafik(
        "15 cm etiketin güvenilir algılandığı en uzak mesafe (m), bakış açısına göre",
        [("standart mercek (66°)", "--c-a"), ("geniş açılı mercek (102°)", "--c-b")],
        [(f"{a}°", [menzil[("std", "15", a)], menzil[("genis", "15", a)]],
          [sy(menzil[("std", "15", a)]).replace(",0", ""), sy(menzil[("genis", "15", a)]).replace(",0", "")])
         for a in acilar], en_buyuk=10, birim=" m",
        aciklama="Göz hizası, temiz görüntü, 1152 × 648 işleme. Güvenilir: algılama oranı o mesafeye dek kesintisiz "
                 "0,75 ve üstü. Etiketin kenarı %25 ya da %50 örtülünce ve sert parlama lekesinde her mesafede 0.")
    tb = r["tek_bas"]
    oneri = liste([
        "<strong>Etiket planı:</strong> 15 cm AprilTag 36h11, göz hizasında (1,55 m); her düz hattın iki ucunda, L köşesinde "
        "iki dış duvarda, T kavşağında yan kolun karşısında birer etiket, ayrıca yan duvarlarda 5 m arayla, sırayla sol ve "
        "sağ. Koridor başına 3 ile 8 etiket.",
        f"<strong>Kırılma:</strong> yalnız uç / köşe / kavşak etiketleri yetmedi; 8 m aralık başarılı ama yanal sapma "
        f"0,16 m'ye çıktı; 5 m, yanal sapmayı 0,15 m altında tutan en seyrek aralık.",
        f"<strong>Mercek:</strong> standart mercek (66°), 1152 × 648, saniyede 10 kare. Karşıdan bakışta 15 cm etiket "
        f"standart mercekte {tam(menzil[('std', '15', '0')])} m'de, geniş açılıda {tam(menzil[('genis', '15', '0')])} m'de "
        "algılanıyor. Geniş açılı mercek yalnız görünürlük ölçümünde denendi, gezinmede denenmedi.",
        "<strong>Zayıflık (güncellendi):</strong> rastgele bırakılmadaki tek başarısızlıkta koşu boyunca en büyük konum "
        f"hatası {sy(say(tb['konum_hata_en_m']) if tb else None)} m; robot 262 s eğik açıyla duvara dayalı kaldı ve ön "
        "sonar bunu durdurmadı. O tur bunun nedeni tek etiketten yanlış başlatma sanıldı; bu turun yeniden üretimi "
        "başlangıcın kabaca doğru olduğunu, asıl kusurun takılmanın sezilmemesi olduğunu gösterdi (yukarıda).",
    ])
    iyimser = [
        "Baskı kusursuz, duvar düz ve mat; yansıma ve parlak laminasyon yok; ışık düzgün; insan ve kapı kanadı yok.",
        "Mercek bozulması, yuvarlanan deklanşör, kafa titreşimi ve gövde eğimi yok.",
        "Etiketlerin yeri ve yönü ile kameranın iç parametreleri kusursuz biliniyor; 1–2°'lik montaj hatası yön "
        "düzeltmesine doğrudan biner.",
        "Algılama gecikmesi yok (Pi 5'te 40–55 ms varsayılıyor, modellenmedi); sonar ideal; odometri dönüş hatası sabit.",
    ]
    aciklar = [
        "Etiket yer / yönüne gürültü, kamera parametresine hata ve 50 ms gecikme eklenmiş sınama koşulmadı.",
        "Tek etiketten başlatmayı yakalayan ikinci doğrulama ve eğik duvara dayanmayı durduran yan algı yok.",
        "Daha hafif parlama ve kenarın kısmen örtülmesine dayanıklılık ölçülmedi.",
        "Her koşulda tek tohum; 3 hedeften 2'si; koridor başına 3 bırakma. Pi 5 algılama süresi ölçülmedi.",
        "Sanal ray birim testleri ana test takımına bağlı değil; ayrıca çalıştırılmaları gerekiyor.",
    ]
    hukum = (f"Simülasyonda evet, koşullu. Kafa kamerası, duvar etiketleri, enkoder ve ön sonarla, LiDAR verisi hiç "
             f"kullanılmadan robot sınama koridorlarında {r['ab_n']} A'dan B'ye koşusunun {r['ab_b']}'sında hedefe vardı; "
             f"seçilen 5 m planla {r['plan5'][0]}/{r['plan5'][1]}. Varış hatası ortalama {sy(r['varis_ort'], 2)} m, "
             f"LiDAR'lı tabanda 0,048 m. Gerçek koridorda asıl risk etiketin örtülmesi ve parlama.")
    olculen = (
        "<p>LiDAR'sız gezinme: kafadaki tek kamera (Camera Module 3), duvardaki AprilTag etiketleri, enkoder ve ön sonar. "
        "Etiket planı ve süzgeç ayarları iki geliştirme koridorunda seçildi, sonuç dört ayrı sınama koridorundan. Ayrıca "
        "ayrı bir yapay duvar sahnesinde mercek, etiket boyu, yükseklik, çözünürlük ve bozulmalara göre görünürlük haritası "
        "çıkarıldı.</p>")
    govde = bolum_parcalari(olculen, ana, grafik, oneri, iyimser, aciklar, hukum)
    ust = {
        "test": "LiDAR'sız sanal ray",
        "hukum": f"Kamera, duvar etiketi ve enkoderle {r['ab_n']} koşunun {r['ab_b']}'sında hedefe varış, 5 m planla "
                 f"{r['plan5'][0]}/{r['plan5'][1]}; varış hatası {sy(r['varis_ort'], 2)} m, yani LiDAR'lıdan yaklaşık "
                 "2,5 kat kötü.",
        "karar": "LiDAR'a yedek olarak duvarlara 15 cm etiket, göz hizasında, yan duvarda 5 m arayla; standart mercekli "
                 "kamera; robotu tek etiketten başlatmama, ikinci bir doğrulama isteme.",
    }
    return r, govde, ust


# ================================================================== 5. DENEME ZİNCİRİ
def deneme():
    r = {}
    b798 = bel(K, "Haritayla yeniden deneme", "798 / 874 / 982 s", ["798 / 874 / 982"],
               "en uzun sınama 2 labirentinin ölçülen tempoyla beklenen süresi 798 / 874 / 982 s (önceki tur)")
    satirlar, yig = [], []
    for ad, dosya, ilk_dosya in (("Geliştirme (önceki sürümün 7 başarısızı)", "deneme_gelistirme.csv", "mujoco_v3.csv"),
                                 ("Sınama 2 (20 labirent)", "deneme_sinama2.csv", "mujoco_sinama2_v3.csv")):
        rows = oku(K / dosya)
        zin = {}
        for x in rows:
            zin.setdefault((x["sahne"], x["tohum"]), []).append(x)
        dag = {1: 0, 2: 0, 3: 0, 4: 0, 0: 0}
        top_sure, cozulmeyen = [], []
        for kk, z in zin.items():
            z.sort(key=lambda x: int(x["deneme_no"]))
            cz = [int(x["deneme_no"]) for x in z if x["durum"] == "basari"]
            if cz:
                dag[min(cz)] += 1
                top_sure.append(sum(say(x["sure_s"]) for x in z))
            else:
                dag[0] += 1
                cozulmeyen.append(kk)
        ilk = {(x["sahne"], x["tohum"]): x for x in oku(K / ilk_dosya)}
        ayni = sum(1 for x in rows if x["deneme_no"] == "1" and (x["sahne"], x["tohum"]) in ilk
                   and ilk[(x["sahne"], x["tohum"])]["durum"] == x["durum"]
                   and abs(say(ilk[(x["sahne"], x["tohum"])]["sure_s"]) - say(x["sure_s"])) <= 1.0)
        bilgi = {"zincir": len(zin), "dag": dag, "deneme": len(rows),
                 "carpma": sum(int(say(x["carpma_sayisi"]) or 0) for x in rows),
                 "start": sum(int(say(x["fail_start"]) or 0) for x in rows),
                 "sure_med": medyan(top_sure), "cozulmeyen": cozulmeyen, "ilk_ayni": ayni,
                 "ilk_n": sum(1 for x in rows if x["deneme_no"] == "1")}
        r[dosya] = bilgi
        satirlar.append([ad, str(len(zin)), str(dag[1]), str(dag[2]), str(dag[3]), str(dag[4]),
                         f"<span class='{'kotu' if dag[0] else ''}'>{dag[0]}</span>", tam(bilgi["sure_med"]),
                         str(len(rows)), str(bilgi["carpma"])])
        yig.append((ad, [dag[1], dag[2], dag[3], dag[4], dag[0]], len(zin)))
    s2 = r["deneme_sinama2.csv"]
    gl = r["deneme_gelistirme.csv"]
    r["ilk_ayni"] = (gl["ilk_ayni"] + s2["ilk_ayni"], gl["ilk_n"] + s2["ilk_n"])
    ana = tablo(["Küme", "Zincir", "1. denemede", "2.", "3.", "4.", "4 denemede çözülmedi",
                 "Toplam süre ortanca, çözülen (s)", "Deneme sayısı", "Çarpma"], satirlar,
                not_="Her deneme en çok 900 s, en çok 4 deneme. Robot başarısız denemeden sonra başlangıca konur "
                     "(yerleştirme hatası 3 cm / 2°); harita, sınır hafızası ve sahte çıkış listesi korunur. "
                     f"Birinci denemeler eski ilk giriş koşularıyla {r['ilk_ayni'][0]}/{r['ilk_ayni'][1]} aynı sonucu "
                     "ve süreyi verdi.")
    grafik = yigin_grafik("Labirentin kaçıncı denemede çözüldüğü",
                          [("1. deneme", "--c-c"), ("2. deneme", "--c-a"), ("3. deneme", "--c-a2"),
                           ("4. deneme", "--c-a3"), ("çözülmedi", "--c-b")], yig,
                          aciklama="Geliştirme kümesi yalnız ilk girişte çözülemeyen labirentlerden oluşuyor; bu yüzden "
                                   "orada 1. denemede çözülen yok.")
    cz = ", ".join(f"{s.replace('labirent_', '').replace('_t', ' no. ')} (tohum {t})" for s, t in sorted(s2["cozulmeyen"]))
    oneri = liste([
        f"<strong>Kazanç küçük:</strong> sınama 2'de çözülen {s2['dag'][1]}'ten {s2['dag'][1] + s2['dag'][2] + s2['dag'][3] + s2['dag'][4]}'ya "
        "çıktı. Bu sonuçlar \"hafızalı\" sınıfta; ilk girişte hiç bilgi olmadan çözme ölçüsü değil.",
        f"<strong>Kırılma noktası:</strong> çözülmeyen dört zincir: {cz}. Tanıya göre (sınama 2'ye bakıldıktan sonra, ayar "
        "yapılmadan) iki nedeni var: yeni denemede sınır seçme sırası başlangıca göre, yani robot önceki denemenin "
        "kaldığı yere değil başlangıca yakın sınırlara gidiyor; en uzun labirentin 207 m'lik çözümü harita tam bilinse de "
        f"900 s'ye ancak sınırda sığıyor (ölçülen tempoyla beklenen {b798}).",
        "<strong>Öneri:</strong> yeni denemede önceki denemenin son hedefini ya da son konumuna yakın sınırı öne almak. "
        "Sınama 2 artık görülmüş sayılır; bu değişiklik yeni, görülmemiş bir kümeyle denenmeli.",
        f"<strong>Güvenlik:</strong> başlangıçtan çıkma {s2['start'] + gl['start']}; bir çarpma oldu (sınama 2, 3. deneme, "
        "kurtarmadan sonra yayda duvar ucuna sürtünme; harita kayması değil).",
    ])
    iyimser = [
        "Robot her denemede başlangıca yalnız 3 cm / 2° hatayla konuyor; gerçek hata daha büyük olabilir.",
        "Zemin düz; teker kayması modeli düzeneğinki kadar.",
        "Denemeler arasında haritayı saklamak kural gereği serbest varsayıldı.",
        "Sınama 2 bu testten önce başka bir kararda kullanılmıştı ve başarısız beş koşu biliniyordu; küme tam taze değil.",
    ]
    aciklar = [
        "Sınır seçme sırası değişikliği denenmedi.",
        "Önceki sürümden kalan döngü: dönüş sığmayınca robot kayma ile ileri sürüş arasında gidip geliyor (geliştirmede bir "
        "deneme 60 s hareketsiz kalıp bitti).",
        "Tam haritalı tavan koşusu güvenilir değildi, çıkarıldı; 207 m hükmü ölçülmüş tempoya dayanıyor.",
        "Zincir, taze sınama 3 kümesinde ölçülmedi.",
    ]
    hukum = (f"Başarısız denemenin haritasını sonraki denemeye taşımak sınama 2'de çözülen labirent sayısını "
             f"{s2['dag'][1]}/20'den {20 - s2['dag'][0]}/20'ye çıkardı; kazanç tek labirent (2. denemede). Geliştirme "
             f"kümesindeki {gl['zincir']} zor labirentin hepsi 2. ya da 3. denemede çözüldü. En uzun iki labirent 4 denemede "
             "de çözülmedi.")
    olculen = (
        "<p>Labirentte (MuJoCo, her deneme 900 s) başarısız denemenin haritası sonraki denemeye taşındığında kaçıncı "
        "denemede çıkışın bulunduğu. Robot her yeni denemede başlangıca konur, konumunu sıfırlar ve ilk iki taramayı eski "
        "haritaya oturtur. Geliştirme: önceki sürümün geliştirmede çözemediği 7 koşu. Sınama: 20 koşuluk sınama 2.</p>")
    govde = bolum_parcalari(olculen, ana, grafik, oneri, iyimser, aciklar, hukum)
    ust = {
        "test": "Haritayla yeniden deneme",
        "hukum": f"Haritayı taşımak sınama 2'de çözüleni {s2['dag'][1]}/20'den {20 - s2['dag'][0]}/20'ye çıkardı (kazanç tek "
                 f"labirent, 2. denemede); geliştirmenin {gl['zincir']} zor labirenti 2. ya da 3. denemede çözüldü; en uzun "
                 "ikisi 4 denemede de çözülmedi.",
        "karar": "Kural ikinci denemeye izin veriyorsa haritayı saklamak değer, ama kazanç küçük; büyük kazanç için yeni "
                 "denemede keşfin önceki denemenin kaldığı yerden sürmesi gerekiyor (henüz yapılmadı).",
    }
    return r, govde, ust


# ================================================================== 6. KÖŞE HIZI
KUMELER = [
    ("gelistirme", "Geliştirme", {"v3": "mujoco_v3.csv", "v4": "mujoco_v4.csv", "v5": "mujoco_v5.csv"}),
    ("sinama2", "Sınama 2 (görülmüş)", {"v3": "mujoco_sinama2_v3.csv", "v4": "mujoco_sinama2_v4.csv",
                                         "v5": "mujoco_sinama2_v5.csv"}),
    ("sinama3", "Sınama 3 (yeni; v4 kararı)", {"v3": "mujoco_sinama3_v3.csv", "v4": "mujoco_sinama3_v4.csv"}),
    ("sinama4", "Sınama 4 (yeni; v5 kararı)", {"v3": "mujoco_sinama4_v3.csv", "v4": "mujoco_sinama4_v4.csv",
                                                "v5": "mujoco_sinama4_v5.csv"}),
]


def kose():
    tani = {}
    for f in sorted(K.glob("hiz_tani_*.csv")):
        for x in oku(f):
            tani.setdefault((x["kume"], x["surum"]), {})[(x["sahne"], x["tohum"])] = x
    r = {"kume": {}}
    satirlar, gsat = [], []
    top_c = {"v3": [0, 0], "v4": [0, 0], "v5": [0, 0]}
    for kume, ad, dosyalar in KUMELER:
        veri = {su: {(x["sahne"], x["tohum"]): x for x in oku(K / d)} for su, d in dosyalar.items()}
        for su, rows in veri.items():
            b = sum(1 for x in rows.values() if x["durum"] == "basari")
            c = sum(int(say(x["carpma_sayisi"]) or 0) for x in rows.values())
            ts = sum(say(x["carpma_suresi_s"]) or 0 for x in rows.values())
            bas_sure = medyan([say(x["sure_s"]) for x in rows.values() if x["durum"] == "basari"])
            oran = "-"
            if su != "v3":
                cift = [say(rows[kk]["sure_s"]) / say(veri["v3"][kk]["sure_s"]) for kk in rows
                        if kk in veri["v3"] and rows[kk]["durum"] == "basari" and veri["v3"][kk]["durum"] == "basari"]
                oran = f"{sy(medyan(cift), 3)} <span class='ince'>({len(cift)} çift)</span>"
                r["kume"][(kume, su, "oran")] = medyan(cift)
            td = tani.get((kume, su))
            pay5 = (f"{sum(1 for x in td.values() if say(x['duvar_pay_min_m']) is not None and say(x['duvar_pay_min_m']) < 0.005)}/{len(td)}"
                    if td and len(td) == len(rows) else "-")
            r["kume"][(kume, su)] = (b, len(rows), c, ts)
            if kume != "sinama3":
                top_c[su][0] += c
                top_c[su][1] += len(rows)
            satirlar.append([ad, su, f"{b}/{len(rows)}",
                             f"<span class='{'kotu' if c else ''}'>{c}</span>" + (f" <span class='ince'>({sy(ts, 2)} s)</span>" if c else ""),
                             tam(bas_sure), oran, pay5])
        uy = []
        if "v4" in veri:
            uy = [kk for kk in veri["v3"] if kk in veri["v4"] and
                  (veri["v3"][kk]["durum"] == "basari") != (veri["v4"][kk]["durum"] == "basari")]
        r["kume"][(kume, "uyusmayan_v3_v4")] = uy
        gsat.append((ad, [r["kume"][(kume, su)][0] / r["kume"][(kume, su)][1] if (kume, su) in r["kume"] else None
                          for su in ("v3", "v4", "v5")],
                     [f"{r['kume'][(kume, su)][0]}/{r['kume'][(kume, su)][1]}" + (
                         f" · <span class='kotu'>{r['kume'][(kume, su)][2]} çarpma</span>" if r['kume'][(kume, su)][2] else "")
                      if (kume, su) in r["kume"] else "koşulmadı" for su in ("v3", "v4", "v5")]))
    r["top_c"] = top_c
    hv3 = tani[("gelistirme", "v3")]
    hv4 = tani[("gelistirme", "v4")]

    def agirlikli(td, alan):
        return sum(say(x[alan]) * say(x["duz_s"]) for x in td.values()) / sum(say(x["duz_s"]) for x in td.values())

    r["duz_hiz"] = (agirlikli(hv3, "v_duz_ort"), agirlikli(hv4, "v_duz_ort"))
    r["hizli_pay"] = (agirlikli(hv3, "hizli_pay"), agirlikli(hv4, "hizli_pay"))
    r["kuyruk"] = (sum(say(x["kuyruk_s"]) for x in hv3.values()), sum(say(x["kuyruk_s"]) for x in hv4.values()))
    ana = tablo(["Küme", "Sürüm", "Çözülen", "Çarpma (temas)", "Süre ortanca, çözülen (s)",
                 "Süre oranı / v3 (ortanca, ikisi de çözdüyse)", "Duvara 5 mm'den yaklaşan koşu"], satirlar,
                not_="MuJoCo, 900 s, robot labirent hakkında önceden bilgisiz. v3: bugünkü varsayılan sürüş. v4: fren "
                     "zarfı, ölçüye dayalı hızlanma izni ve yay süpürme denetimi eklenmiş hızlı sürüş. v5: v4 + dönüşü robot "
                     "durunca denetleme, sığmayan dönüşte önce geri çekilme ve çarpacak yaydan kaçınma.")
    grafik = cubuk_grafik("Çözülen labirent ve çarpma, küme ve sürüm başına",
                          [("v3 (varsayılan)", "--c-c"), ("v4 (hız zarfı)", "--c-b"), ("v5 (v4 + dönüş güvenliği)", "--c-a")],
                          gsat, en_buyuk=1,
                          aciklama="Çubuk boyu çözülen koşu oranı (kümeler 37 ve 20 koşu). Kırmızı yazı o kümedeki "
                                   "çarpma olayı.")
    u3 = r["kume"][("sinama3", "uyusmayan_v3_v4")]
    v4lehine = sum(1 for kk in u3 if
                   next(x for x in oku(K / "mujoco_sinama3_v4.csv") if (x["sahne"], x["tohum"]) == kk)["durum"] == "basari")
    r["s3_uyusmayan"] = (len(u3), v4lehine)
    o_gel = r["kume"][("gelistirme", "v4", "oran")]
    oneri = liste([
        f"<strong>Tanı:</strong> v3'te düz sürüşte ölçülen hız {sy(r['duz_hiz'][0], 3)} m/s; köşeye yaklaşırken 0,10 m/s "
        f"altında geçen \"kuyruk\" geliştirmede {tam(r['kuyruk'][0])} s. v4 bunu {tam(r['kuyruk'][1])} s'ye indirdi, "
        f"düz hız {sy(r['duz_hiz'][1], 3)} m/s, süre oranı ortanca {sy(o_gel, 3)}.",
        f"<strong>Kırılma:</strong> görülmüş sınama 2'de v4 iki çarpma verdi (biri yerinde dönüşte "
        f"{sy(r['kume'][('sinama2', 'v4')][3], 2)} s temas). Kök neden: dönüş robot henüz frenlerken denetlendi ve hiçbir "
        "dönüş sığmasa da robot yine döndü; ikincisinde çarpacağı öngörülen yaya karşı önlem yoktu. v5 ikisini giderdi, "
        "ama geliştirmede yeni bir çarpma verdi.",
        f"<strong>İstatistik:</strong> sınama 3'teki {r['kume'][('sinama3', 'v3')][0]} → {r['kume'][('sinama3', 'v4')][0]} "
        f"farkı yalnız {r['s3_uyusmayan'][0]} uyuşmayan labirent çiftinden geliyor (hepsi v4 lehine) ve kazanılanlar 900 s "
        "sınırına çok yakın; \"v4 daha iyi\" anlamlı değil, \"kaybettirmedi ve daha hızlı\" doğru.",
        f"<strong>Karar (o tur):</strong> geliştirme + sınama 2 + sınama 4'te (sürüm başına {top_c['v3'][1]} koşu) çarpma "
        f"v3 {top_c['v3'][0]}, v4 {top_c['v4'][0]}, v5 {top_c['v5'][0]}; o üç kümede sıfır olan yalnız v3'tü. Varsayılan v3'e "
        "döndü; v4 ve v5 isteğe bağlı. Güncellendi: v3 başka kümelerde sıfır değil (toplam 4 temas olayı) ve bu tur "
        "varsayılan v6 oldu (yukarıda).",
    ])
    iyimser = [
        "Teker azami hızı 0,39 m/s bir tahmin; v4 düz sürenin yaklaşık %69'unda hızlı kipte. Gerçek tavan düşükse kazanç ve "
        "sınıra yakın kazanılan koşular kaybolabilir.",
        "Fren zarfı 0,5 m/s² yavaşlama ve 0,15 s tepki payı varsayar; Pi'den ESP32'ye komut bellek üzerinden gidiyor, seri hat "
        "gecikmesi yok.",
        "Süpürme öngörüsü milimetre düzeyinde güvenilir değil: yandaki duvar ucu LiDAR'ın gerisinde kalınca tarama onu eksik "
        "görüyor.",
        "2B benzeticide v5 koşulmadı.",
    ]
    aciklar = [
        "v5'in geliştirmedeki yeni çarpması incelenmedi; yay kaçınmanın orada devrede olup olmadığı bilinmiyor.",
        "v5, v4'ün çözdüğü bir geliştirme labirentini kaybetti; incelenmedi.",
        "Önde engel beklemesi döngüsü (v3'ten kalma) ve sınır seçme sırası sorunu sürüyor.",
        "Yerinde dönüş hızı değiştirilmedi (toplam sürenin yaklaşık %11'i).",
        "2B'de v4'ün çarpması sıfır değildi.",
    ]
    hukum = (f"Hız zarfı (v4) labirenti yaklaşık %{tam(100 * (1 - o_gel))} daha kısa sürede bitirdi ama görülmüş kümede 2 "
             f"çarpma verdi. Onarılmış v5 bu ikisini giderdi ve yeni sınama 4'te v3 kadar "
             f"({r['kume'][('sinama4', 'v5')][0]}/20) çözdü, fakat geliştirmede yeni 1 çarpma verdi. O üç kümede çarpması "
             "sıfır olan yalnız v3 olduğu için varsayılan v3'e döndü.")
    olculen = (
        "<p>Labirentte köşelerde ve düz parçalarda hız kaybının nedeni (v3 kayıtlarının tanısı) ve onu gideren hızlı sürüş "
        "sürümlerinin çözülen labirent, süre ve çarpma üzerindeki etkisi. Kural her sürüm için önceden yazıldı: yeni, "
        "görülmemiş kümede başarı v3'ten az olmayacak ve çarpma artmayacak. v4 için sınama 3, v5 için sınama 4 bu amaçla "
        "üretildi.</p>")
    govde = bolum_parcalari(olculen, ana, grafik, oneri, iyimser, aciklar, hukum)
    ust = {
        "test": "Köşe hızı (v3, v4, v5)",
        "hukum": f"v4 yaklaşık %{tam(100 * (1 - o_gel))} hızlı ama görülmüş kümede 2 çarpma verdi; onarılmış v5 yeni kümede "
                 f"v3 kadar ({r['kume'][('sinama4', 'v5')][0]}/20) çözdü ama geliştirmede 1 çarpma; {top_c['v3'][1]}'şer "
                 f"koşuda çarpma v3 {top_c['v3'][0]}, v4 {top_c['v4'][0]}, v5 {top_c['v5'][0]}.",
        "karar": "Gerçek robotta varsayılan sürüş v3 kalıyor, v5 isteğe bağlı; daha hızlı sürüşe geçmeden önce gerçek teker "
                 "azami hızı (bugün 0,39 m/s tahmin) ve komut gecikmesi ölçülmeli.",
    }
    return r, govde, ust


# ================================================================== İNCELEME
def kart(baslik, kapsam, engel, diger, onarim, acik, rozetler=None, onarim_baslik="Onarımda ne değişti"):
    rozetler = rozetler or rz("Hüküm: koşullu")
    return (
        f"<article class='kart'><header><h3>{baslik}</h3><span>{rozetler}</span></header>"
        f"<p class='ince'>{kapsam}</p>"
        "<p class='satir-durum'><span class='rozet iyi'>Sayılar CSV'den yeniden sayıldı: tuttu</span> "
        "<span class='rozet iyi'>Sınama verisinin ayara sızması: bulunmadı</span></p>"
        f"<h4>Engelleyici bulgu</h4>{engel}"
        f"<h4>Diğer sorunlar</h4>{liste(diger)}"
        f"<h4>{onarim_baslik}</h4>{onarim}"
        f"<h4>İnceleme sonrası açık kalanlar</h4>{liste(acik)}"
        "</article>")


def inceleme_eski(R):
    u, h, t, s, d, k = R
    kartlar = []

    kartlar.append(kart(
        "Uçurum ve merdiven", "Bütün tablolar yeniden sayıldı; dört koşu aynı tohumla yeniden koşuldu ve alan alan aynı çıktı.",
        "<p>Sınanmamış geometri: bütün sahneler robottan geniş düz kenar ya da dış köşeydi. İncelemenin kısa denemesinde "
        "ilk seçilen dört köşe düzeni 0,45–0,70 m genişliğinde aşağı inen dar açıklıkta tetiklemeden düştü, ön orta "
        "sensörlü düzen durdu. \"Dört sensör yeterli\" iddiası yalnız 0,8 m ve üstü kenarlar için geçerliydi.</p>",
        ["Sınamanın üç düz kenar geometrisi aynı kenarı taşıyordu (240 eşli koşunun 238'inde aynı pay); pratikte tek geometri. "
         "Yanlış alarm sınaması da yeni sahne içermiyordu.",
         "10° iniş için önerilen 1,5 m/s² fren belgede \"ölçülmedi\" yazıyordu; oysa ölçülmüştü ve öneriyi desteklemiyor.",
         "Saniyede 50 örnek ile 4 m menzil birlikte iyimser varsayılmış; 0,39 m/s tavanı masa ölçümüne kadar iyimser sayılmalı.",
         "Seçilen politika, ilk sınama sonuçları görüldükten sonra aynı tohumlarla koşulmuştu (dosya zamanları ayar sızıntısı "
         "göstermiyor, ama iz zayıf)."],
        f"<p><strong>Hüküm değişti.</strong> Dar açıklık sahnesi ve açıklığın içinde eksi pay veren hakem eklendi. Geliştirmede "
        f"dört köşe düzeni {u['gel_4kose'][1]} koşunun {u['gel_4kose'][0]}'unda düştü; üç aday karşılaştırıldı ve aynı seçim "
        f"kuralıyla altı sensörlü düzen ({u['gel_6'][0]}/{u['gel_6'][1]} düşme) seçildi; seçim sınamadan önce yazıldı. Yeni "
        f"sınama 2: {u['toplam']} koşu, 8 yeni dar açıklık ve 5 yeni yanlış alarm sahnesiyle; {u['ucurum_kosu']} uçurum "
        f"koşusunda {u['dustu']} düşme, {u['yanlis_kosu']} yanlış alarm koşusunda {u['yanlis_durma']} durma. Geri, dönüş ve yay "
        "bu kez seçilen politikayla koşuldu. Belgelerdeki 1,5 m/s² ve devrilme ifadeleri düzeltildi.</p>",
        ["0,40 m'den dar delik ve izler arasındaki yaklaşık 0,2 m'lik delik sınanmadı; açıklığa geri ya da dönerek yaklaşma "
         "koşulmadı.",
         "Altı sensörle parlak zemin ve köşe sensörü arızası taraması yeniden koşulmadı.",
         "Tutma freni, inişte güvenli fren ivmesi, sensör kipi ve sığ düşüş eşiği açık."]))
    kartlar.append(kart(
        "Harita eskimesi ve çalışırken taşınma", "İki testin bütün ana sayıları yeniden sayıldı; altı koşu aynı tohumla "
        "yeniden koşuldu ve CSV ile birebir aynı çıktı.",
        "<p>Yok.</p>",
        [f"Kırılma noktalarının bir kısmı tek koşuya duyarlı: \"ani kayma 2 / dk'da kırar\" ve \"cam %25'te kırar\" iddiaları "
         f"kademe başına bir kaba başarısızlık ile hedefe 0,30–0,34 m'de bir durmadan oluşuyor ({h['bas_sinirda']} sınırda "
         "başarısızlık). Bunlar \"sınırda\" sayılmalı; bu yüzden ani kaymanın gerçek robotta ölçülecekler listesindeki "
         "gerekçesi zayıf.",
         "Sonuç belgesinin o turki zarar sırası (\"dönüşsüz > menzil > kapı\") kayıp robottaki eşit olmayan kademe "
         "kapsamından geliyordu; sağlam değildi. Güncellendi: bu tur yalnız A'dan B'ye ortalamasıyla düzeltildi "
         f"({h['sira_metin']}).",
         "Taşınmada \"tek haritalı sürüş hiç tepki vermedi\" ölçülmüş bir bulgu değil, yapısal: o sürüşte tepki düzeneği yok.",
         "Algılı sürümün yanlış alarmı yalnız insan ve eşyayla ölçüldü; okul gününün hafif hâlinde bile kapı, cam ve dönüşsüz "
         "yüzey var. Varsayılana almadan önce ölçülmeli.",
         "Gecikme, Pi 5 süresi, yol veren insan, kusursuz taban harita ve anlık taşıma: hepsi iyimser yönde.",
         "Bir zaman işareti dosyası depo dışı bırakılanlar listesinde değil; kayıt sırasında karar verilmeli."],
        "<p><strong>Ayrı bir onarım turu yapılmadı;</strong> engelleyici bulgu yoktu. İnceleme sonuç belgesine sınırdaki "
        "başarısızlıklar ve zarar sırası uyarısını ekledi; taşınma belgesindeki eksik koşul, koşul sayısı ve yeniden üretim "
        "komutları düzeltildi. Algoritma ve sonuç dosyaları değişmedi. Testin kendi özet metni bu düzeltmeler olmadan eski "
        "hâliyle kaldı; bu sayfa düzeltilmiş hâli kullanıyor.</p>",
        ["Kayıp robot ızgarası daraltılmış; MuJoCo'da cam ve kayıp robot yok.",
         "Algılı sürümün kurtarma bedeli ve cam / kapı / dönüşsüz yüzeyde yanlış alarmı ölçülmedi.",
         "Gerileme denetimi küçültülmüş ve sürüşsüz."]))
    kartlar.append(kart(
        "LiDAR'sız sanal ray", "Bütün ana sayılar CSV'lerden yeniden sayıldı; üç koşu aynı tohumla birebir aynı çıktı.",
        f"<p>Rapor tablosunda \"ilk etikete süre / yol\" başlıklı sütunlar aslında konumlanma süresini basıyordu. Gerçek ilk "
        f"görülme ortalama {sy(s['kayip']['sabit'][2])} s (sabit kafa) / {sy(s['kayip']['tarayan'][2])} s (tarayan); bildirilen "
        f"{sy(s['kayip']['sabit'][3])} / {sy(s['kayip']['tarayan'][3])} s konumlanma süresi. Hüküm değişmez.</p>",
        ["Etiket haritası ve kamera iç parametreleri kusursuz biliniyor; algılama gecikmesi yok. Önerilen ek deney: etiket "
         "yerine ±3 cm / ±2° gürültü, kamera parametresine %1 hata ve 50 ms gecikme.",
         "Rastgele bırakılmadaki tek başarısızlıkta yeniden başlatma kancası hiç tetiklenmedi (ret olmadı); bildirilen 1,7 m, "
         "başlangıç hatası değil koşu boyunca görülen en büyük konum hatası.",
         "Yanal sapma ölçütü 5 m planda başlangıç sapmasına doymuş; dönüş hatası kademelerini ayırt etmiyor.",
         "Örneklem küçük ve tek tohumlu; yanlış koridor 0 sonucu kurgu gereği; iki kavşak başarısızlığında hiç etiket ölçümü "
         "kabul edilmedi.",
         "Birim testleri ana test takımına bağlı değil; gösterim görüntüsünde küçük bir yazı kusuru var."],
        "<p><strong>Hüküm değişmedi.</strong> Sütun başlıkları düzeltildi, ilk görülme sütunu eklendi ve tablolar ham kayıtlardan "
        "yeniden üretildi; CSV'ler eskiyle birebir aynı çıktı. Sonuç belgesinde 1,7 m'nin anlamı düzeltildi, kamera "
        "açıklaması düzeltildi, yeni bir birim testi eklendi. Ayar değişmedi, yeni koşu yapılmadı.</p>",
        ["Etiket yeri / kamera parametresi hatası ve gecikmeli sınama koşulmadı.",
         "Tek etiketten yanlış başlatmayı yakalayan düzenek yok; ön sonar eğik dayanmayı durdurmuyor.",
         "Yanal sapma ölçütü düzeltilmedi; örneklem büyütülmedi; birim testleri ana takıma bağlanmadı."]))
    kartlar.append(kart(
        "Labirent: haritayla yeniden deneme ve köşe hızı", "İki testin her ana sayısı yeniden sayıldı; dört koşu yalıtılmış "
        "kopyada yeniden koşuldu ve alan alan aynı çıktı.",
        "<p>v4 varsayılan yapıldı ama \"çarpma sıfır\" hedefini karşılamıyordu: görülmüş sınama 2'de yerinde dönüşte 6,15 s "
        "temaslı bir çarpma ve yayda ikinci bir sürtünme vardı; ikisi de v3'te yok. Gerçek robot için v3'ün korunması "
        "önerildi.</p>",
        [f"Sınama 3'teki fark yalnız {k['s3_uyusmayan'][0]} uyuşmayan çiftten geliyor ve kazanılan koşular 900 s sınırına çok "
         "yakın; istatistik olarak anlamlı sayılmaz.",
         "v4 kodunun dondurulmasından önceki 7 dakikalık aralıkta yalnız v3'ün sınama 3 sonucu görülmüştü; sızıntı kanıtı yok, "
         "ama aralık var.",
         "Deneme koşturucusu sınama 2 zinciri koşarken değişti ve eski sürüm saklanmadı; birinci denemeler eski koşularla "
         f"{d['ilk_ayni'][0]}/{d['ilk_ayni'][1]} aynı, etkisi büyük olasılıkla yok ama kesin doğrulanamıyor.",
         "Sınır mesafeleri gibi bazı tanı sayıları CSV'den sayılamıyor; doğrulanmadı.",
         "\"Dış alana geldik ama hakem bitirmedi\" bilgisi benzetimden çıkarılıyor; gerçek robotta çıkış algısı ne veriyorsa o "
         "kadarı meşru.",
         "Haritayla yeniden deneme görülmüş kümede değerlendirildi; taze sınama 3'te ölçülmedi. Bir rapor tablosuna başka "
         "deneyin satırları karışıyor (sayı doğru)."],
        f"<p><strong>Hüküm değişti.</strong> İki çarpma aynı tohumla yeniden koşulup kök nedenleri bulundu ve v5 yazıldı: "
        "dönüş robot durunca denetleniyor, kayma daha geniş aranıyor, hiçbiri sığmazsa önce geri çekilip yeniden plan, "
        "çarpacak yayda eğrilik çarpmayan en yakın değere itiliyor. v5 kodu dondurulduktan sonra yeni sınama 4 üretildi: "
        f"v3, v4, v5 hepsi {k['kume'][('sinama4', 'v3')][0]}/20, çarpma 0. Ama geliştirmede v5 yeni bir çarpma verdi; "
        f"{k['top_c']['v3'][1]}'şer koşuda çarpma v3 {k['top_c']['v3'][0]}, v4 {k['top_c']['v4'][0]}, v5 {k['top_c']['v5'][0]}. "
        "Bu yüzden varsayılan v4'ten v3'e döndü.</p>",
        ["v5'in geliştirmedeki çarpması ve kaybettiği labirent incelenmedi.",
         "Süpürme öngörüsü yan duvar ucunu eksik görüyor; çözüm adayı denenmedi.",
         "2B'de v5 koşulmadı; sınır seçme sırası ve tam haritalı tavan koşusu açık."]))
    return "".join(kartlar)


# ================================================================== BU TUR (tamamlama turu)
def bolum_yeni(y, eski_govde, eski_baslik):
    os_html = "<div class='os'>" + "".join(
        f"<div class='os-satir'><div class='os-konu'>{k}</div>"
        f"<div class='os-once'><span class='os-et'>Önce</span>{o}</div>"
        f"<div class='os-simdi'><span class='os-et'>Şimdi</span>{s}</div></div>" for k, o, s in y["os"]) + "</div>"
    return (
        f"<p class='hukum'><strong>Hüküm (bu tur).</strong> {y['hukum']}</p>"
        f"<p class='satir-durum'>{y['rozet']}</p>"
        f"<h3>Önce / şimdi</h3>{os_html}"
        f"<h3>Bu turda ne ölçüldü</h3>{y['olculen']}"
        f"<h3>Ana tablo</h3>{y['ana']}"
        f"<h3>Grafik</h3>{y['grafik']}"
        f"<h3>Kırılma noktası ve öneri</h3><div class='oneri'>{liste(y['oneri'])}</div>"
        "<div class='iki'>"
        f"<div><h3>Simülasyonun iyimser varsayımları</h3>{liste(y['iyimser'])}</div>"
        f"<div><h3>Kalan açıklar</h3>{liste(y['aciklar'])}</div>"
        "</div>"
        f"<details class='eski'><summary>{eski_baslik}</summary><div class='eski-ic'>"
        "<p class='ince'>Bu kısım önceki turun ayrıntısıdır. Hüküm, öneri ve açıklar yukarıda güncellendi; çelişen "
        "yerlere \"güncellendi\" notu düşüldü.</p>"
        f"{eski_govde}</div></details>")


UC_GRUP = [
    ("İleri: iki merdiven, kuyu, sahanlık köşesi", ("ileri",)),
    ("Geri, yerinde dönüş, yay (iki merdiven)", ("geri", "donus", "yay")),
    ("Dar açıklığa ileri (8 sahne)", ("dar",)),
    ("Burunlu merdiven ve tek 12 cm basamak", ("yeni_ileri", "yeni_geri")),
    ("0,9 m genişlikte iskele", ("yeni_iskele",)),
    ("8° rampanın ucunda uçurum", ("yeni_rampa_ucurum",)),
    ("Dar açıklığa geri giderek", ("yeni_geri_dar",)),
    ("Dar yarık, 1 m boy", ("yeni_delik",)),
    ("Dar açıklık yanında yerinde dönüş", ("yeni_donus_dar",)),
    ("Kötü koşulların birleşimi (+20 ms, en kötü montaj, µ 0,5, +10 kg)", ("kotu_birlesik",)),
]
DUY_AD = [("K20", "Seçilen kısa kip (20 ms)"), ("U33", "Uzun kip, 33 ms"), ("U50", "Uzun kip, 50 ms"),
          ("U100", "Uzun kip, 100 ms (seçilmeyen)"), ("g20", "Ek gecikme +20 ms"), ("g50", "Ek gecikme +50 ms"),
          ("mu05", "Sürtünme µ 0,5"), ("montaj_kotu", "Montaj hatası, en kötü"), ("montaj_rasgele", "Montaj hatası, rastgele"),
          ("yuk_ust5", "+5 kg yük, üstte"), ("yuk_alt10", "+10 kg yük, altta"), ("gurultu10", "Ölçüm gürültüsü σ 10 mm")]


# Üç düzen yan yana (6 / 10 / 14 sensör), tehlike sınıfına göre. Her hücre CSV'den sayılır:
# hüküm (sınama) koşusu varsa o, yoksa ayar koşusu (tohum 1–2, düzeni seçmek için kullanıldı), yoksa "ölçülmedi".
DUZENLER = [
    ("6", "6 sensör", "dört köşe, önde iki iç; son kabul edilen seçim", "4OD+2AD_z120_e30"),
    ("10", "10 sensör", "önde altı, arkada dört; ilk tamamlama adımının adayı", "6OD+4AD_z120_e30"),
    ("14", "14 sensör", "her teker hizasında iki dar iz, iki yan sensör; ölçütü sağlamayan en iyi aday",
     "8WRD+4AD+2YR40_z120_e30"),
]
DAR_45_70 = {"acik_45", "acik_55", "acik_60_sig", "acik_65", "dar_merdiven_60"}
DAR_75_90 = {"acik_75", "acik_90", "dar_merdiven_80"}


def _yarik(*cm):
    ad = {f"yarik_{c}" for c in cm}
    return (lambda x: x["alt"] == "yeni_delik" and x["sahne"] in ad), (lambda x: x["alt"] == "delik" and x["sahne"] in ad)


def _donus_d(d):
    return ((lambda x: x["alt"] == "yeni_donus_dar" and say(x["d"]) == d),
            (lambda x: x["alt"] == "donus" and x["sahne"].startswith("acik_") and say(x["d"]) == d))


KATMAN_SINIF = [
    # (etiket, hüküm süzgeci, ayar süzgeci ya da None, okul binasındaki karşılığı)
    ("Merdiven başı, sahanlık kenarı ve köşesi, ileri",
     lambda x: x["alt"] in ("ileri", "yeni_ileri") and x["sahne"] != "kuyu", None, "ana"),
    ("Kuyu, ileri", lambda x: x["alt"] == "ileri" and x["sahne"] == "kuyu", None, "ana"),
    ("Dar açıklık 0,45–0,70 m, ileri", lambda x: x["alt"] == "dar" and x["sahne"] in DAR_45_70, None, "ana"),
    ("Dar açıklık 0,75–0,90 m, ileri", lambda x: x["alt"] == "dar" and x["sahne"] in DAR_75_90, None, "ana"),
    ("Geri gidiş, geniş kenar", lambda x: x["alt"] in ("geri", "yeni_geri"), None, "ana"),
    ("Geri gidiş, dar açıklığa", lambda x: x["alt"] == "yeni_geri_dar",
     lambda x: x["alt"] == "geri" and x["sahne"].startswith("acik_"), "ana"),
    ("Yerinde dönüş, geniş kenar", lambda x: x["alt"] == "donus", None, "ana"),
    ("Dar açıklık yanında yerinde dönüş, merkez kenardan 0,35 m", *_donus_d(0.35), "ana"),
    ("… 0,40 m", *_donus_d(0.40), "ana"),
    ("… 0,45 m", *_donus_d(0.45), "ana"),
    ("… 0,50 m", *_donus_d(0.50), "ana"),
    ("Dar yarık 9 cm × 1 m", *_yarik(9), "yarik"),
    ("… 10 cm", *_yarik(10), "yarik"),
    ("… 11 cm", *_yarik(11), "yarik"),
    ("… 12 cm", *_yarik(12), "yarik"),
    ("… 13 cm", *_yarik(13), "yarik"),
    ("… 14 cm", *_yarik(14), "yarik"),
    ("<strong>Dar yarık 9–14 cm, toplam</strong>", *_yarik(9, 10, 11, 12, 13, 14), "toplam"),
    ("Ek: yarık 15 ve 20 cm", *_yarik(15, 20), "ek"),
    ("Ek: yarık 17–28 cm", *_yarik(17, 22, 28), "ek"),
    ("Ek: 0,9 m genişlikte iskele (üç yanı boşluk)", lambda x: x["alt"] == "yeni_iskele", None, "ek"),
    ("Ek: kötü koşulların birleşimi", lambda x: x["alt"] == "kotu_birlesik", None, "ek"),
]


def katmanli():
    """Üç düzenin tehlike sınıfına göre karşılaştırması; bütün hücreler CSV'den."""
    def uc(R):
        return [x for x in R if not x["alt"].startswith("yanlis")]

    def dus(R):
        return sum(dogru(x["dustu"]) for x in R)

    def fiz(x):
        return ((say(x.get("teker_dz_min_mm")) or 0) < -20 or (say(x.get("egim_max_der")) or 0) > 5
                or dogru(x.get("govde_temas")))

    def sec(R, yer):
        return [x for x in R if x["yerlesim"] == yer]

    D6, D10, D14 = (d[3] for d in DUZENLER)
    hk = {"6": oku(U / "sinama2.csv"), "10": oku(U / "t_hukum.csv"), "14": oku(U / "t2_hukum.csv")}
    fz = {"6": [], "10": oku(U / "t_hukum_fiz.csv"), "14": oku(U / "t2_hukum_fiz.csv")}
    ay = {"6": sec(oku(U / "t_delik_gel.csv") + oku(U / "t_yaklasma_gel.csv"), D6),
          "10": sec(oku(U / "t_aday_son.csv") + oku(U / "t2_yarik_gel.csv"), D10),
          "14": sec(oku(U / "t2_donus_gel2.csv"), D14)}
    ay_fz = {"6": sec(oku(U / "t_delik_fiz.csv"), D6), "10": [], "14": []}
    # 14 sensörün yarık ayarı yan sensörsüz öncülüyle koşuldu (yan sensörler yarıkta işe karışmaz)
    ay14_yan_yok = [x for x in oku(U / "t2_yarik_gel2.csv") if x["yerlesim"] == "8WRD+4AD_z120_e30"]
    ru = oku(U / "t_rampa_ucurum.csv")

    def hucre(k, fh, fa):
        H = [x for x in uc(hk[k]) if fh(x)]
        if H:
            d, n = dus(H), len(H)
            p = mn([say(x["pay_min_cm"]) for x in H])
            if d == 0:
                f_txt, f_n = "fiziksel 0", 0
            else:
                F = [x for x in fz[k] if fh(x)]
                f_n = sum(fiz(x) for x in F) if F else None
                f_txt = f"fiziksel {f_n} / {len(F)}" if F else "fiziksel ölçülmedi"
            sinif = "iyi" if d == 0 else ("kotu" if (f_n is None or f_n > 0) else "uyari")
            return {"tur": "H", "d": d, "n": n, "f": f_n, "p": p, "sinif": sinif,
                    "html": f"<span class='{sinif}'>{d} / {n}</span> <span class='ince'>· {f_txt} · pay "
                            f"{sy(p)} cm</span>"}
        if fa is not None:
            A = [x for x in uc(ay[k]) if fa(x)]
            not_ = ""
            if not A and k == "14":
                A = [x for x in ay14_yan_yok if fa(x)]
                not_ = ", yan sensörsüz öncülüyle"
            if A:
                d, n = dus(A), len(A)
                p = mn([say(x["pay_min_cm"]) for x in A])
                F = [x for x in ay_fz[k] if fa(x)]
                if d == 0:
                    f_txt = "fiziksel 0"
                elif F:
                    f_txt = f"fiziksel {sum(fiz(x) for x in F)} / {len(F)}"
                else:
                    f_txt = "fiziksel ölçülmedi"
                return {"tur": "A", "d": d, "n": n, "p": p, "sinif": "ayar",
                        "html": f"<span class='ince'>hükümde ölçülmedi; ayarda{not_}:</span> "
                                f"<span class='{'kotu' if d else ''}'>{d} / {n}</span> <span class='ince'>· {f_txt} · "
                                f"pay {sy(p)} cm</span>"}
        return {"tur": "-", "sinif": "yok", "html": "<span class='ince'>ölçülmedi</span>"}

    satirlar, veri = [], {}
    for etiket, fh, fa, grup in KATMAN_SINIF:
        hs = [hucre(k, fh, fa) for k, *_ in DUZENLER]
        veri[etiket] = hs
        satirlar.append((etiket, [h["html"] for h in hs], grup))
    # rampa ucu: 6 sensör yalnız ayarda (10°), öbürleri hükümde (8°); eğim rampanın kendisi, fiziksel eşik uygulanmaz
    rp = []
    k2 = [x for x in ru if "konum" in x["kosul"] and say(x["fren_ivme"]) == 2.0 and x["yerlesim"] == D6]
    tutmasiz = [x for x in ru if x["kosul"] == "{}" and x["yerlesim"] == D6]
    rp.append(f"<span class='ince'>hükümde ölçülmedi; ayarda (10° rampa), konum tutmayla:</span> "
              f"<span class='{'kotu' if dus(k2) else ''}'>{dus(k2)} / {len(k2)}</span> <span class='ince'>· tutmasız "
              f"{dus(tutmasiz)} / {len(tutmasiz)} düşer</span>")
    for k in ("10", "14"):
        R = [x for x in hk[k] if x["alt"] == "yeni_rampa_ucurum"]
        d = dus(R)
        rp.append(f"<span class='{'kotu' if d else 'iyi'}'>{d} / {len(R)}</span> <span class='ince'>· pay "
                  f"{sy(mn([say(x['pay_min_cm']) for x in R if say(x['v']) == 0.25]))} cm (0,25 m/s)</span>")
    satirlar.insert(len(satirlar) - 2, ("Ek: iniş rampasının ucunda uçurum (hükümde 8°)", rp, "ek"))
    # yanlış durma ve toplam
    yd, top = [], []
    tot = {}
    for k, *_ in DUZENLER:
        Y = [x for x in hk[k] if x["alt"].startswith("yanlis")]
        y = sum(dogru(x["tetik"]) for x in Y)
        yd.append(f"<span class='{'kotu' if y else 'iyi'}'>{y} durma / {len(Y)}</span>")
        Uc = uc(hk[k])
        d = dus(Uc)
        f_n = sum(fiz(x) for x in fz[k]) if d else 0
        tot[k] = (d, len(Uc), f_n, y, len(Y))
        top.append(f"<strong class='{'kotu' if d else 'iyi'}'>{d} / {len(Uc)}</strong> <span class='ince'>· fiziksel "
                   f"{f_n}</span>")
    satirlar.append(("<strong>Yanlış durma</strong> (12 düz zemin sahnesi: derz, eşik, halı, koyu bant, rampa)", yd, "toplam"))
    satirlar.append(("<strong>Uçurum koşuları, hüküm toplamı</strong>", top, "toplam"))
    bas = "".join(f"<th>{ad}<span class='ince th-alt'>{ac}</span></th>" for _, ad, ac, _ in DUZENLER)
    govde = "".join(
        f"<tr class='g-{grup}'><td>{et}</td>" + "".join(
            f"<td data-etiket='{e(DUZENLER[i][1])}'>{c}</td>" for i, c in enumerate(hs)) + "</tr>"
        for et, hs, grup in satirlar)
    html_ = (f"<div class='tablo-kap'><table class='veri katman'><thead><tr><th>Tehlike sınıfı</th>{bas}</tr></thead>"
             f"<tbody>{govde}</tbody></table></div>")
    return html_, veri, tot


# Bağımsız hüküm 3 (taze küme): beş düzen AYNI görev listesinde, tohum ve sahneler yeni. Bütün hücreler
# sonuc/hukum3.csv (hüküm koşusu) ve sonuc/hukum3_fiz.csv (hakemin düşme saydığı koşular, sürdürülerek) dosyalarından.
DUZEN3 = [
    # (CSV'deki düzen, başlık, açıklama, CSV'deki yerleşim)
    ("6", "6 sensör", "dört köşe, önde iki iç; önceki kabul edilen seçim", "4OD+2AD_z120_e30"),
    ("10", "10 sensör", "önde altı, arkada dört", "6OD+4AD_z120_e30"),
    ("14", "14 sensör, iz ±2 cm", "her teker hizasında iki dar iz, iki yan sensör; görülmüş ızgaranın en iyi adayı",
     "8WRD+4AD+2YR40_z120_e30"),
    ("3A", "14 sensör, iz ±2,5 cm", "aynı düzen; yalnız iz çiftinin aralığı genişletildi", "8WRaD+4AD+2YR40_z120_e30"),
    ("3B", "10 sensör + sürüş kuralları", "10 sensörün donanımı; yerinde dönmez, geri yay çizer; şüpheli okumada yavaşlar",
     "6OD+4AD_z120_e30"),
]
H3_SINIF = [
    ("merdiven_ileri", "Merdiven başı ve sahanlık kenarı, ileri"),
    ("kose_ileri", "Sahanlık köşesi, ileri"),
    ("kuyu_ileri", "Kuyu, ileri"),
    ("dar_ileri", "Dar açıklık {acik}, ileri"),
    ("dar_geri", "Dar açıklığa geri gidiş"),
    ("genis_geri", "Geniş kenara geri gidiş"),
    ("donus_genis", "Yerinde dönüş, geniş kenar"),
    ("donus_dar", "Yerinde dönüş, dar açıklık yanında (merkez kenardan {d})"),
    ("yarik_dar", "Dar yarık {yarik}"),
    ("yarik_egik", "Eğik yarık (ekseni {egik} dönük)"),
    ("rampa_ucu", "İniş rampasının ucunda düşüş ({rampa})"),
]


def _sayi_tr(x):
    """8.5 -> '8,5', 16.0 -> '16'."""
    return (f"{x:.2f}".rstrip("0").rstrip(".")).replace(".", ",")


def _pay_tr(p):
    return sy(p, 2 if p is not None and abs(p) < 1 else 1)


def hukum3():
    """Taze kümenin düzen x tehlike sınıfı tablosu ve ön kayıtlı ölçüte göre hüküm; hepsi CSV'den."""
    H3, F3 = oku(U / "hukum3.csv"), oku(U / "hukum3_fiz.csv")

    def hatali(x):
        return bool((x.get("hata") or "").strip())

    def fiz(x):
        # ön kayıtlı tanım (hukum3.fiziksel_dustu ile aynı): rampa ucunda eğim rampanın kendisidir
        if x["alt"] == "rampa_ucu":
            eg = 6.0 if "rampa_6" in x["sahne"] else 9.0
            return (say(x["pay_min_cm"]) or 0) < -6.25 or (say(x["egim_max_der"]) or 0) > eg + 5.0
        return ((say(x["teker_dz_min_mm"]) or 0) < -20 or (say(x["egim_max_der"]) or 0) > 5
                or dogru(x["govde_temas"]))

    Fk = {(x["duzen"], x["taban"]): x for x in F3 if not hatali(x)}
    dz_l = [d[0] for d in DUZEN3]
    R = {k: [x for x in H3 if x["duzen"] == k] for k in dz_l}
    bilinmeyen = sorted({x["duzen"] for x in H3} - set(dz_l))
    if bilinmeyen:
        raise SystemExit(f"Uçurum hüküm 3: tabloda olmayan düzen var: {bilinmeyen}")
    for k, _, _, ys in DUZEN3:
        if {x["yerlesim"] for x in R[k]} != {ys}:
            raise SystemExit(f"Uçurum hüküm 3: düzen {k} için yerleşim beklenenle tutmuyor")

    def gorev(x):
        return (x["taban"], x["alt"], x["sahne"], x["tur"], x["tohum"], x["aci"], x["v"], x["w"], x["d"], x["yanal"])

    g0 = sorted(gorev(x) for x in R[dz_l[0]])
    r = {"ayni_gorev": all(sorted(gorev(x) for x in R[k]) == g0 for k in dz_l), "taban_n": len(g0),
         "kosu_n": len(H3), "fiz_n": len(F3), "fiz_hata": sum(hatali(x) for x in F3),
         "tohum": (min(int(x["tohum"]) for x in H3), max(int(x["tohum"]) for x in H3)),
         "sahne_n": len({x["sahne"] for x in H3}),
         "hizlar": sorted({say(x["v"]) for x in H3 if say(x["v"]) is not None}),
         "kosul": sorted({x["kosul"] for x in H3}),
         "kural": {k: any((x.get("supheli_say") or "").strip() for x in R[k]) for k in dz_l}}

    # sınıf etiketlerindeki aralıklar sahne adlarından
    def sahneler(alt):
        return sorted({x["sahne"] for x in H3 if x["alt"] == alt})

    acik = sorted(int(s.split("_")[2]) / 100 for s in sahneler("dar_ileri"))
    yarik = sorted(int(s.split("_")[2]) / 10 for s in sahneler("yarik_dar"))
    egik = sorted({int(s.split("_")[3]) for s in sahneler("yarik_egik")})
    rampa = sorted({int(s.split("_")[2]) for s in sahneler("rampa_ucu")})
    dd = sorted({say(x["d"]) for x in H3 if x["alt"] == "donus_dar"})
    alan = {"acik": f"{_sayi_tr(acik[0])}–{_sayi_tr(acik[-1])} m", "yarik": f"{_sayi_tr(yarik[0])}–{_sayi_tr(yarik[-1])} cm",
            "egik": f"{egik[0]}–{egik[-1]}°", "rampa": " / ".join(f"{a}°" for a in rampa),
            "d": f"{_sayi_tr(dd[0])}–{_sayi_tr(dd[-1])} m"}

    def hucre(k, alt):
        q = [x for x in R[k] if x["alt"] == alt]
        if not q:
            return {"n": 0, "d": 0, "f": 0, "s": 0, "p": None, "hata": 0,
                    "html": "<span class='uyari'>ölçülmedi</span>"}
        ok = [x for x in q if not hatali(x)]
        hata = len(q) - len(ok)
        dus_ = [x for x in ok if dogru(x["dustu"])]
        p = mn([say(x["pay_min_cm"]) for x in ok])
        F = [Fk[(x["duzen"], x["taban"])] for x in dus_ if (x["duzen"], x["taban"]) in Fk]
        f_n = sum(fiz(z) for z in F)
        if not dus_:
            f_txt = "fiziksel 0"
        else:
            f_txt = f"fiziksel {f_n} / {len(F)}"
            if len(F) < len(dus_):
                f_txt += f" ({len(dus_) - len(F)} koşu sürdürülmedi)"
        h_txt = f" · <span class='kotu'>{hata} hata</span>" if hata else ""
        sinif = "iyi" if not dus_ and not hata else "kotu"
        return {"n": len(q), "d": len(dus_), "f": f_n, "s": len(F), "p": p, "hata": hata, "dusen": dus_,
                "html": f"<span class='{sinif}'>{len(dus_)} / {len(q)}</span> <span class='ince'>· {f_txt} · pay "
                        f"{_pay_tr(p)} cm</span>{h_txt}"}

    kat = {alt: {k: hucre(k, alt) for k in dz_l} for alt, _ in H3_SINIF}
    top = {}
    for k in dz_l:
        uc_ = [x for x in R[k] if x["alt"] != "yanlis_alarm"]
        ya_ = [x for x in R[k] if x["alt"] == "yanlis_alarm"]
        ok = [x for x in uc_ if not hatali(x)]
        dus_ = [x for x in ok if dogru(x["dustu"])]
        F = [Fk[(x["duzen"], x["taban"])] for x in dus_ if (x["duzen"], x["taban"]) in Fk]
        bos = sum(1 for alt, _ in H3_SINIF if kat[alt][k]["n"] == 0) + (0 if ya_ else 1)
        t = {"d": len(dus_), "n": len(uc_), "f": sum(fiz(z) for z in F), "s": len(F),
             "durma": sum(dogru(x["tetik"]) for x in ya_ if not hatali(x)), "ya": len(ya_),
             "surun": sum(1 for x in ya_ if (say(x.get("supheli_say")) or 0) > 0),
             "hata": sum(hatali(x) for x in R[k]), "p": mn([say(x["pay_min_cm"]) for x in ok]), "bos": bos,
             "sensor": int(R[k][0]["sensor_n"]), "pay1": [x for x in ok if (say(x["pay_min_cm"]) or 0) < 1 and
                                                          not dogru(x["dustu"])]}
        # ön kayıtlı ölçüt: uçurum koşularında 0 hakem düşmesi, yanlış alarm koşularında 0 durma; hatalı koşu geçti sayılmaz
        t["gecti"] = t["d"] == 0 and t["durma"] == 0 and t["hata"] == 0 and bos == 0
        top[k] = t
    r["kat"], r["top"], r["alan"] = kat, top, alan
    r["bos"] = sum(t["bos"] for t in top.values())

    def ad(k):
        return next(d[1] for d in DUZEN3 if d[0] == k)

    # tablo 1: ön kayıtlı ölçüte göre
    s1 = []
    for k, baslik, ac, _ in DUZEN3:
        t = top[k]
        s1.append([f"<strong>{baslik}</strong><span class='ince th-alt'>{ac}</span>",
                   f"<span class='{'kotu' if t['d'] else 'iyi'}'>{t['d']} / {t['n']}</span>",
                   f"{t['f']} / {t['s']}" if t["d"] else "0",
                   f"<span class='{'kotu' if t['durma'] else 'iyi'}'>{t['durma']} / {t['ya']}</span>"
                   + (f" <span class='ince'>(yavaşlama {t['surun']})</span>" if t["surun"] else ""),
                   str(t["hata"]), f"{_pay_tr(t['p'])} cm",
                   rz("GEÇTİ", "iyi") if t["gecti"] else rz("GEÇMEDİ", "kotu")])
    b1 = ["Düzen", "Hakem düşmesi (uçurum)", "Fiziksel düşme", "Yanlış durma", "Hata", "En küçük pay", "Ön kayıtlı ölçüt"]
    t1 = ("<div class='tablo-kap'><table class='veri katman olcut'><thead><tr>" + "".join(f"<th>{b}</th>" for b in b1)
          + "</tr></thead><tbody>" + "".join(
              "<tr>" + "".join(f"<td data-etiket='{e(b1[i])}'>{c}</td>" for i, c in enumerate(s)) + "</tr>" for s in s1)
          + "</tbody></table></div>")
    # tablo 2: düzen x tehlike sınıfı
    satirlar = []
    for alt, et in H3_SINIF:
        n = {kat[alt][k]["n"] for k in dz_l}
        n_txt = f" <span class='ince'>· {n.pop()} koşu</span>" if len(n) == 1 else ""
        satirlar.append((et.format(**alan) + n_txt, [kat[alt][k]["html"] for k in dz_l], "ana"))
    yd = []
    for k in dz_l:
        t = top[k]
        yd.append(f"<span class='{'kotu' if t['durma'] else 'iyi'}'>{t['durma']} durma / {t['ya']}</span>"
                  + (f" <span class='ince'>· yavaşlama {t['surun']} / {t['ya']}</span>" if t["surun"] else ""))
    ya_sahne = len({x["sahne"] for x in H3 if x["alt"] == "yanlis_alarm"})
    satirlar.append((f"<strong>Yanlış durma</strong> ({ya_sahne} düz zemin sahnesi: derz, eşik, halı, koyu şerit, parlak "
                     "zemin, iniş rampası)", yd, "toplam"))
    satirlar.append(("<strong>Uçurum koşuları, toplam</strong>",
                     [f"<strong class='{'kotu' if top[k]['d'] else 'iyi'}'>{top[k]['d']} / {top[k]['n']}</strong> "
                      f"<span class='ince'>· fiziksel {top[k]['f']}{f' / ' + str(top[k]['s']) if top[k]['d'] else ''} · "
                      f"{top[k]['hata']} hata</span>"
                      for k in dz_l], "toplam"))
    satirlar.append(("<strong>Ön kayıtlı ölçüte göre</strong>",
                     [rz("GEÇTİ", "iyi") if top[k]["gecti"] else rz("GEÇMEDİ", "kotu") for k in dz_l], "toplam"))
    bas = "".join(f"<th>{b}<span class='ince th-alt'>{a}</span></th>" for _, b, a, _ in DUZEN3)
    govde = "".join(
        f"<tr class='g-{grup}'><td>{et}</td>" + "".join(
            f"<td data-etiket='{e(DUZEN3[i][1])}'>{c}</td>" for i, c in enumerate(hs)) + "</tr>"
        for et, hs, grup in satirlar)
    t2 = (f"<div class='tablo-kap'><table class='veri katman bes'><thead><tr><th>Tehlike sınıfı</th>{bas}</tr></thead>"
          f"<tbody>{govde}</tbody></table></div>")
    r["t1"], r["t2"], r["ad"] = t1, t2, ad
    r["adq"] = lambda k: f"“{ad(k)}”"
    r["gecen"] = [k for k in dz_l if top[k]["gecti"]]
    r["rows"] = H3
    return r


def ucurum_yeni(eu):
    H2, H1 = oku(U / "t2_hukum.csv"), oku(U / "t_hukum.csv")
    F1, F2 = oku(U / "t_hukum_fiz.csv"), oku(U / "t2_hukum_fiz.csv")
    D2, D1 = oku(U / "t2_duyar.csv"), oku(U / "t_duyar.csv")
    K2 = oku(U / "t2_kusur.csv")
    YG = oku(U / "t2_yarik_gel.csv") + oku(U / "t2_yarik_gel2.csv")
    DG = oku(U / "t2_donus_gel.csv") + oku(U / "t2_donus_gel2.csv")
    RU, RF = oku(U / "t_rampa_ucurum.csv"), oku(U / "t_rampa_fren.csv")
    secim = json.loads((FIZIK / "ucurum" / "secim.json").read_text(encoding="utf-8"))

    def uc(R):
        return [x for x in R if not x["alt"].startswith("yanlis")]

    def ya(R):
        return [x for x in R if x["alt"].startswith("yanlis")]

    def dus(R):
        return sum(dogru(x["dustu"]) for x in R)

    def pay(R):
        return mn([say(x["pay_min_cm"]) for x in R if not dogru(x["dustu"])])

    def fiz(x):
        return ((say(x["teker_dz_min_mm"]) or 0) < -20 or (say(x["egim_max_der"]) or 0) > 5
                or dogru(x["govde_temas"]))

    def ozet(R):
        u_, y_ = uc(R), ya(R)
        return {"n": len(R), "uc": len(u_), "dus": dus(u_), "ya": len(y_),
                "durma": sum(dogru(x["tetik"]) for x in y_),
                "hata": sum(1 for x in R if (x.get("hata") or "").strip()),
                "tohum": (min(int(x["tohum"]) for x in R), max(int(x["tohum"]) for x in R)),
                "pay": pay(u_), "sensor": int(R[0]["sensor_n"])}

    r = {"h1": ozet(H1), "h2": ozet(H2)}
    h1, h2 = r["h1"], r["h2"]

    def gorev(x):
        return (x["alt"], x["sahne"], x["tur"], x["aci"], x["v"], x["w"], x["d"], x["yanal"])

    g1 = {gorev(x) for x in H1}
    r["ayni_gorev"] = (sum(gorev(x) in g1 for x in H2), len(H2))
    f2k = [x for x in uc(H2) if x["sahne"] != "rampa_8_ucurum"]
    r["fiz2"] = (sum(fiz(x) for x in f2k), len(f2k))
    r["govde2"] = sum(dogru(x["govde_temas"]) for x in uc(H2))
    r["fiz2s"] = (sum(fiz(x) for x in F2), len(F2))
    f1d = [x for x in F1 if fiz(x)]
    r["fiz1"] = (len(f1d), len(F1))
    r["fiz1_teker"] = (mn([-say(x["teker_dz_min_mm"]) for x in f1d]), mx([-say(x["teker_dz_min_mm"]) for x in f1d]))
    r["fiz1_sahne"] = sorted({x["sahne"] for x in f1d})
    r["fiz1_donus"] = (sum(fiz(x) for x in F1 if x["alt"] == "yeni_donus_dar"),
                       sum(1 for x in F1 if x["alt"] == "yeni_donus_dar"))
    r["h1_yarik"] = dus([x for x in H1 if x["alt"] == "yeni_delik"])
    r["h1_donus"] = dus([x for x in H1 if x["alt"] == "yeni_donus_dar"])
    r["h1_donus_d"] = sorted({say(x["d"]) for x in H1 if x["alt"] == "yeni_donus_dar" and dogru(x["dustu"])})
    dusen = [x for x in uc(H2) if dogru(x["dustu"])]
    r["dusen2"] = dusen
    dz = dusen[0] if dusen else None

    def hucre(R, alts):
        rs = [x for x in R if x["alt"] in alts]
        if not rs:
            return "<span class='ince'>yok</span>"
        d, n, p = dus(rs), len(rs), pay(rs)
        ek = ""
        if "yeni_delik" in alts:
            ek = "; " + " / ".join(str(g) for g in sorted({int(x["sahne"].split("_")[1]) for x in rs})) + " cm"
        if "yeni_donus_dar" in alts:
            ek = "; kenardan " + " / ".join(sy(v, 2) for v in sorted({say(x["d"]) for x in rs})) + " m"
        return f"<span class='{'kotu' if d else 'iyi'}'>{d} / {n}</span> <span class='ince'>(pay {sy(p)} cm{ek})</span>"

    sat = [[ad, hucre(H1, alts), hucre(H2, alts)] for ad, alts in UC_GRUP]
    sat.append(["Yanlış alarm (12 düz zemin sahnesi)",
                f"<span class='iyi'>{h1['durma']} durma / {h1['ya']}</span>",
                f"<span class='iyi'>{h2['durma']} durma / {h2['ya']}</span>"])
    sat.append(["<strong>Uçurum koşuları, toplam</strong>",
                f"<strong class='kotu'>{h1['dus']} / {h1['uc']}</strong> <span class='ince'>({h1['hata']} hata)</span>",
                f"<strong class='kotu'>{h2['dus']} / {h2['uc']}</strong> <span class='ince'>({h2['hata']} hata)</span>"])
    sat.append(["Fiziksel düşme (koşu sürdürülünce)",
                f"<span class='kotu'>{r['fiz1'][0]} / {r['fiz1'][1]}</span> <span class='ince'>(yarık ve dönüş "
                "koşuları sürdürüldü)</span>",
                f"<span class='iyi'>{r['fiz2'][0]} / {r['fiz2'][1]}</span> <span class='ince'>(rampa ucu hariç; düşen "
                f"koşu sürdürülünce {r['fiz2s'][0]} / {r['fiz2s'][1]})</span>"])
    esik_fiz = bel(U, "Uçurum", "teker 20 mm'den çok iner ya da gövde 5°'den çok eğilir",
                   ["teker > 20 mm iner ya da eğim > 5°"], "fiziksel düşme eşiği: teker > 20 mm ya da eğim > 5° (varsayım)")
    # üç düzen yan yana (bağımsız incelemenin üçüncüsünden sonra)
    kat_html, kat, kat_top = katmanli()
    r["kat_top"] = kat_top
    ANA_SINIF = [et for et, _, _, g in KATMAN_SINIF if g in ("ana", "yarik")]
    r["kapsam"] = {k: (sum(1 for et in ANA_SINIF if kat[et][i]["sinif"] == "iyi"), len(ANA_SINIF))
                   for i, (k, *_) in enumerate(DUZENLER)}
    yk = "<strong>Dar yarık 9–14 cm, toplam</strong>"
    d40 = "… 0,40 m"
    y14 = kat["… 14 cm"]
    t6, t10, t14 = kat_top["6"], kat_top["10"], kat_top["14"]
    # metindeki kapsama cümleleri veriyle tutmalı; tutmazsa dur
    ucu_de = ["Merdiven başı, sahanlık kenarı ve köşesi, ileri", "Kuyu, ileri", "Dar açıklık 0,45–0,70 m, ileri",
              "Dar açıklık 0,75–0,90 m, ileri", "Geri gidiş, geniş kenar", "Yerinde dönüş, geniş kenar"]
    donus_dar = [et for et in kat if et.startswith("Dar açıklık yanında") or et in ("… 0,40 m", "… 0,45 m", "… 0,50 m")]
    yarik_s = [et for et in kat if et.startswith("Dar yarık 9") or et in ("… 10 cm", "… 11 cm", "… 12 cm", "… 13 cm",
                                                                         "… 14 cm")]
    if not (all(kat[et][i]["sinif"] == "iyi" for et in ucu_de for i in range(3))
            and [kat["Geri gidiş, dar açıklığa"][i]["sinif"] for i in range(3)] == ["ayar", "iyi", "iyi"]
            and all(kat[et][2]["sinif"] == "iyi" for et in donus_dar)
            and not all(kat[et][1]["sinif"] == "iyi" for et in donus_dar)
            and not any(all(kat[et][i]["sinif"] == "iyi" for et in yarik_s) for i in range(3))
            and (t6[3], t10[3], t14[3]) == (0, 0, 0)):
        raise SystemExit("Uçurum: kapsama cümleleri katmanlı tabloyla tutmuyor; metni güncelleyin.")
    kapsam_html = liste([
        f"<strong>Üçü de kapsıyor</strong> (hükümde 0 hakem düşmesi): merdiven başı, sahanlık kenarı ve köşesi, kuyu, "
        "0,45–0,90 m dar açıklığa ileri yaklaşma, geniş kenarda geri gitme ve yerinde dönüş; düz zeminde yanlış durma "
        f"{t6[3]} / {t10[3]} / {t14[3]}.",
        f"<strong>Dar açıklığa geri gitme:</strong> 10 ve 14 sensör kapsıyor; 6 sensör hükümde ölçülmedi, ayarda "
        f"{kat['Geri gidiş, dar açıklığa'][0]['d']} / {kat['Geri gidiş, dar açıklığa'][0]['n']} düştü.",
        f"<strong>Dar açıklık yanında yerinde dönme:</strong> yalnız 14 sensör kapsıyor (kenardan 0,40 m'de pay "
        f"{sy(kat[d40][2]['p'])} cm, sınırda). 10 sensörde hükümde {kat[d40][1]['d']} / {kat[d40][1]['n']} hakem "
        f"düşmesi, fiziksel {kat[d40][1]['f']}; 6 sensör hükümde ölçülmedi, ayarda {kat[d40][0]['d']} / "
        f"{kat[d40][0]['n']}.",
        f"<strong>9–14 cm dar yarık hiçbir düzenle ölçütü sağlamıyor:</strong> 6 sensör hükümde ölçülmedi (ayarda 10 "
        f"cm'de {kat['… 10 cm'][0]['d']} / {kat['… 10 cm'][0]['n']}); 10 sensörde 14 cm'de {y14[1]['d']} / "
        f"{y14[1]['n']} hakem ve {y14[1]['f']} fiziksel düşme; 14 sensörde {kat[yk][2]['d']} / {kat[yk][2]['n']} "
        f"hakem düşmesi, fiziksel 0, en küçük pay {sy(kat[yk][2]['p'])} cm.",
    ])
    ana_eski = ("<h4>Üç düzen yan yana, tehlike sınıfına göre</h4>"
           "<p class='ince'>Hücre: hakemin saydığı düşme / koşu · fiziksel düşme · en küçük pay (eksi pay: teker merkezi "
           "kenarı o kadar geçti). Hüküm koşusu yoksa ayar koşusu gösterilir (tohum 1–2, düzeni seçmek için kullanıldı; "
           "iyimser okunmalı). Hakem düşmesi 0 ise fiziksel düşme de 0'dır. 6 sensörün hüküm koşuları ilk zamanlama "
           "modeliyle ve konum tutmasız koşulmuştu.</p>" + kat_html + "<h4>Hangi düzen neyi kapsıyor</h4>" + kapsam_html)
    ana_eski += "<h4>10 ve 14 sensörün hüküm koşuları, grup başına</h4>" + tablo(["Hüküm koşusu, grup", f"{h1['sensor']} sensör (bu turun ara adımı; tohum {h1['tohum'][0]}–{h1['tohum'][1]})",
                 f"{h2['sensor']} sensör (ölçütü sağlamayan en iyi aday; tohum {h2['tohum'][0]}–{h2['tohum'][1]})"], sat,
                not_="Hücre: hakemin saydığı düşme / koşu; pay: düşmeyen koşularda teker temas noktasının kenara en yakın "
                     "yatay mesafesi. Hakem kuralı teker merkezinin kenarı geçmesi; değiştirilmedi. Fiziksel düşme: "
                     f"{esik_fiz}, ya da gövde zemine değer. Her iki hükümde düzen hükümden önce donduruldu ve tohumlar "
                     f"daha önce hiç kullanılmamıştı; ama 14 sensörün {r['ayni_gorev'][1]} hüküm görevinden "
                     f"{r['ayni_gorev'][0]} tanesi 10 sensörün hükmüyle aynı sahne ve senaryoydu (yalnız tohum farklı).")
    # ayar: yarık ve dönüş
    YAD = [("6OD+4AD_z120_e30", "10 sensör (ilk aday): tek iz, geniş koni"),
           ("6WD+4AD_z120_e30", "İz teker hizasında (incelemenin 1. önerisi)"),
           ("6WRD+4AD_z120_e30", "İz teker hizasında, dar koni (1. ve 2. öneri)"),
           ("8WRD+4AD_z120_e30", "Her teker hizasında iki dar iz (14 sensörlü adayın ön düzeni)")]
    ysat, ygraf = [], []
    for k, ad in YAD:
        rs = [x for x in YG if x["yerlesim"] == k and x["alt"] == "delik"]
        dar = [x for x in YG if x["yerlesim"] == k and x["alt"] in ("dar", "ileri")]
        d = dus(rs)
        ysat.append([ad, f"<span class='{'kotu' if d else 'iyi'}'>{d} / {len(rs)}</span>",
                     sy(mn([say(x["pay_min_cm"]) for x in rs])) + " cm", f"{dus(dar)} / {len(dar)}"])
        ygraf.append((ad, [d], [f"{d} / {len(rs)}"]))
    r["yarik_ayar"] = ysat
    ana_eski += "<h4>Ayar: dar yarık düzeltmesi (tohum 1–2; 8 / 10 / 12 / 15 / 20 cm yarık)</h4>" + tablo(
        ["Ön düzen", "Yarıkta hakem düşmesi", "En küçük pay", "Dar açıklık ve geniş kenarda düşme"], ysat)
    DAD = [("6WD+4AD_z120_e30", "Yan sensör yok"), ("6WD+4AD+2Y30_z120_e30", "İki yan sensör, dışa 30°, geniş koni"),
           ("6WD+4AD+2Y35_z120_e30", "İki yan sensör, dışa 35°, geniş koni"),
           ("8WRD+4AD+2YR37_z120_e30", "İki yan sensör, dışa 37°, dar koni"),
           ("8WRD+4AD+2YR40_z120_e30", "İki yan sensör, dışa 40°, dar koni (14 sensörlü aday)")]
    dsat = []
    for k, ad in DAD:
        rs = [x for x in DG if x["yerlesim"] == k and x["alt"] == "donus"]
        hh = []
        for dd in (0.35, 0.40):
            q = [x for x in rs if say(x["d"]) == dd]
            dq = dus(q)
            hh.append(f"<span class='{'kotu' if dq else 'iyi'}'>{dq} / {len(q)}</span> "
                      f"<span class='ince'>({sy(mn([say(x['pay_min_cm']) for x in q]))} cm)</span>")
        q = [x for x in rs if say(x["d"]) in (0.45, 0.50)]
        yy = [x for x in DG if x["yerlesim"] == k and x["alt"].startswith("yanlis")]
        dsat.append([ad] + hh + [f"{dus(q)} / {len(q)}",
                                 f"{sum(dogru(x['tetik']) for x in yy)} / {len(yy)}" if yy else "-"])
    ana_eski += ("<h4>Ayar: dar açıklık yanında yerinde dönüş (tohum 1–2; dönme merkezi kenardan d)</h4>" + tablo(
        ["Yan sensör", "d 0,35 m: düşme (en küçük pay)", "d 0,40 m", "d 0,45 / 0,50 m", "Yanlış durma"], dsat))
    # duyarlılık: tek hız önerisinin dayanağı
    def duy(R, kad, v, alts):
        rs = [x for x in R if x["kad"] == kad and say(x["v"]) == v and x["alt"] in alts]
        if not rs:
            return None
        return mn([say(x["pay_min_cm"]) for x in rs]), dus(rs), len(rs)

    A2, A1 = ("ileri", "dar", "delik"), ("ileri", "dar")
    usat, dgraf = [], []
    for kad, ad in DUY_AD:
        hh = []
        for R, v, alts in ((D2, 0.25, A2), (D2, 0.30, A2), (D2, 0.39, A2), (D1, 0.25, A1)):
            q = duy(R, kad, v, alts)
            if q is None:
                hh.append("-")
                continue
            p, d, n = q
            hh.append(f"<span class='{'kotu' if (p is not None and p < 0) or d else ''}'>{sy(p)} cm</span>"
                      + (f" <span class='kotu'>({d}/{n} düştü)</span>" if d else ""))
        usat.append([ad] + hh)
        q2, q1 = duy(D2, kad, 0.25, A2), duy(D1, kad, 0.25, A1)
        dgraf.append((ad, [max(0.0, q1[0]) if q1 else None, max(0.0, q2[0]) if q2 else None],
                      [f"{sy(q1[0])} cm" if q1 else None, f"{sy(q2[0])} cm" if q2 else None]))

    def en_kotu(R, v, alts, haric=("U33", "U50", "U100")):
        c = [(duy(R, kad, v, alts)[0], ad) for kad, ad in DUY_AD if kad not in haric and duy(R, kad, v, alts)]
        return min(c)

    r["k25"], r["k30"] = en_kotu(D2, 0.25, A2), en_kotu(D2, 0.30, A2)
    r["k25_eski"] = en_kotu(D1, 0.25, A1)
    r["secilen25"] = duy(D2, "K20", 0.25, A2)[0]
    r["u100_039"] = duy(D2, "U100", 0.39, A2)
    yd = [x for x in D2 if x["alt"].startswith("yanlis")]
    r["duy_yanlis"] = (sum(dogru(x["tetik"]) for x in yd), len(yd))
    r["hiz"] = secim["hiz_onerisi_m_s"]
    ana_eski += (f"<h4>Duyarlılık: tek hız önerisinin dayanağı (tohum 1; ileri, dar açıklık ve yarık)</h4>" + tablo(
        ["Koşul (14 sensörlü adayın ayarının üstüne)", f"{h2['sensor']} sensör, 0,25 m/s", "0,30 m/s", "0,39 m/s",
         "Önceki 6 sensör, 0,25 m/s"], usat,
        not_=f"Hücre: en küçük pay. Yanlış durma bütün koşullarda {r['duy_yanlis'][0]} / {r['duy_yanlis'][1]}. Önceki 6 "
             "sensörlü düzenin satırları bu turun başında aynı ızgarayla koşulmuştu (yarık olmadan)."))
    # kusur, rampa
    olu = [x for x in K2 if x["alt"].startswith("olu")]
    r["kusur"] = (dus(olu), len(olu), sum(dogru(x["tetik"]) for x in olu))
    pd = {}
    for x in K2:
        if x["alt"] == "parlak" and x["sahne"] == "duz":
            t_ = pd.setdefault(say(x["yok_orani_ayar"]), [0, 0])
            t_[0] += dogru(x["tetik"])
            t_[1] += 1
    r["parlak"] = pd
    tutmasiz = [x for x in RU if x["kosul"] == "{}"]
    k2 = [x for x in RU if "konum" in x["kosul"] and say(x["fren_ivme"]) == 2.0]
    r["rampa"] = (dus(tutmasiz), len(tutmasiz), dus(k2), len(k2),
                  mn([say(x["pay_min_cm"]) for x in k2 if say(x["v"]) == 0.25]),
                  mn([say(x["pay_min_cm"]) for x in k2 if say(x["v"]) == 0.39]))
    rr = [x for x in RF if x["sahne"] != "duz"]
    r["kayma"] = (mx([say(x["kayma_hiz_1_2s"]) for x in rr if x["kosul"] == "{}"]) * 1000,
                  mx([abs(say(x["kayma_hiz_1_2s"])) for x in rr
                      if "konum" in x["kosul"] and say(x["fren_ivme"]) == 2.0]) * 1000)
    ark = {}
    for x in rr:
        ark.setdefault(say(x["fren_ivme"]), []).append(say(x["arka_yuk_min_N"]))
    r["arka_guvenli"] = [a_ for a_, v in sorted(ark.items()) if min(v) > 0]
    r["kotu_birlesik"] = {v: pay([x for x in H2 if x["alt"] == "kotu_birlesik" and say(x["v"]) == v]) for v in (0.25, 0.30)}

    grafik_eski = cubuk_grafik(
        "Ayarda dar yarıkta hakem düşmesi, ön düzen başına (400 koşu)", [("hakem düşmesi", "--c-b")], ygraf,
        en_buyuk=max(1, max(g[1][0] for g in ygraf)),
        aciklama="İncelemenin önerdiği iki düzeltme (izi teker hizasına almak, koniyi daraltmak) düşmeyi azalttı ama "
                 "bitirmedi. Her tekerin iki yanına konan iki dar iz, yarığın kenarı nereden geçerse geçsin birini "
                 "tümüyle boşluğun üstünde bırakıyor.")
    grafik_eski += cubuk_grafik(
        "0,25 m/s'de en küçük pay, koşul başına (cm)",
        [("önceki 6 sensör", "--c-c"), (f"{h2['sensor']} sensörlü aday", "--c-a")], dgraf,
        en_buyuk=max(max(v for v in g[1] if v is not None) for g in dgraf),
        aciklama="Eksi pay sıfırda kesildi; değer yazıda. Uzun kip 100 ms seçilmeyen bir kip, karşılaştırma için.")

    b24 = bel(U, "Uçurum", "≈ 2,4 cm", ["≈ 2,4 cm"],
              "yarığa 10° ile girişte iz sensörünün teker çizgisinden yana kayması ≈ 2,4 cm")
    b070 = bel(U, "Uçurum", "≈ 0,70 N·m", ["0,70 N·m"], "10° inişte konum tutma için teker başına ≈ 0,70 N·m tork")
    b618 = bel(U, "Uçurum", "0,618 N·m", ["0,618, TAHMİN"], "motorun sürekli torku 0,618 N·m (tahmin)")
    b9 = bel(U, "Uçurum", "≈ 9 cm", ["≈ 9 cm'den yakın"], "yan sensörler robotu yan kenar uçuruma ≈ 9 cm'den yakınken durdurur")
    b70 = bel(U, "Uçurum", "≈ 0,70 m", ["0,70 m'den dar şeritte"], "≈ 0,70 m'den dar şeritte robot sürülemez")
    dz_txt = (f"{int(dz['sahne'].split('_')[1])} cm yarığa {dz['aci']}° açıyla, {sy(say(dz['v']), 2)} m/s'de girişte teker "
              f"merkezi kenarı {tam(-10 * say(dz['pay_min_cm']))} mm geçti") if dz else "düşme yok"
    hukum_eski = (f"Önceden konan ölçüte göre <strong>geçmedi</strong>; onaylanmış bir düzen yoktu. En iyi aday olan "
                  f"{h2['sensor']} sensörlü düzen (iz ±2 cm) {h2['uc']} uçurum koşusunda {h2['dus']} hakem düşmesi verdi "
                  f"({dz_txt}); fiziksel düşme {r['fiz2'][0]} / {r['fiz2'][1]}, yanlış durma {h2['durma']} / {h2['ya']}. "
                  f"{h1['sensor']} sensörlü ara adım {h1['dus']} hakem ve {r['fiz1'][0]} fiziksel düşme verdi. Son kabul "
                  f"edilen 6 sensörlü düzen kendi sınamasında {t6[0]} / {t6[1]} düştü, ama o sınamada dar yarık, dar "
                  "açıklığa geri gitme ve dar açıklık yanında dönme yoktu. Bu ızgaranın görevlerinin çoğu daha önce "
                  "koşulmuş sahne ve senaryolardı.")

    # ---------------------------------------------------------- bağımsız hüküm 3 (taze küme): güncel hüküm
    h3 = hukum3()
    r["h3"] = h3
    T3 = h3["top"]
    K3 = h3["kat"]
    ad3, adq = h3["ad"], h3["adq"]
    # onaylı seçim: secim.json'dan (yerleşim + davranış kuralı var mı), CSV'deki düzenle eşlenir
    ys = secim["yerlesim"]
    ys_ad = f"{ys['ad']}_z{round(ys['z'] * 1000)}_e{ys['e']}"
    eslesen = [k for k, _, _, y_ in DUZEN3 if y_ == ys_ad and h3["kural"][k] == bool(secim.get("kural"))]
    if len(eslesen) != 1:
        raise SystemExit("Uçurum: secim.json'daki düzen hüküm 3'ün düzenlerinden birine eşlenemedi.")
    sk = eslesen[0]
    if not secim.get("durum", "").startswith("ONAYLI SECIM"):
        raise SystemExit("Uçurum: secim.json'da 'durum' alanı onaylı seçimi göstermiyor; metni güncelleyin.")
    if h3["gecen"] != [sk] or T3[sk]["sensor"] != int(secim["sensor_n"]):
        raise SystemExit("Uçurum: secim.json'daki onaylı düzen hüküm 3'te ölçütü sağlayan tek düzen değil; metni güncelleyin.")
    if not h3["ayni_gorev"] or h3["bos"] or h3["fiz_hata"]:
        raise SystemExit("Uçurum: hüküm 3'te görev listesi, boş hücre ya da fiziksel koşu hatası beklenenle tutmuyor.")
    hk = secim["hukum_kosul"]
    r["secim3"] = sk
    S = T3[sk]
    kac = sorted(k for k in T3 if k != sk)
    # metindeki "nerede düşüldü" cümleleri veriyle tutmalı; tutmazsa dur
    sifir = [alt for alt, _ in H3_SINIF if all(K3[alt][k]["d"] == 0 for k in T3)]
    if sifir != ["merdiven_ileri", "kuyu_ileri", "dar_ileri", "genis_geri", "donus_genis", "rampa_ucu"]:
        raise SystemExit("Uçurum: hüküm 3'te 'bütün düzenlerde 0 düşme' sınıfları değişti; metni güncelleyin.")
    s3 = list(S["pay1"])
    KISA = {"yarik_dar": "dar yarıkta", "donus_dar": "dar açıklık yanında dönüşte", "yarik_egik": "eğik yarıkta"}
    s3_sinif = {}
    for x in s3:
        s3_sinif[x["alt"]] = s3_sinif.get(x["alt"], 0) + 1
    H3rows = h3["rows"]
    en_ince = min((x for x in H3rows if x["duzen"] == sk and x["alt"] != "yanlis_alarm"), key=lambda x: say(x["pay_min_cm"]))
    ince_txt = (f"{_sayi_tr(int(en_ince['sahne'].split('_')[2]) / 10)} cm yarığa {en_ince['aci']}° açıyla, "
                f"{sy(say(en_ince['v']), 2)} m/s'de") if en_ince["alt"] == "yarik_dar" else en_ince["sahne"]
    d14 = [x for x in H3rows if x["duzen"] == "14" and x["alt"] != "yanlis_alarm" and dogru(x["dustu"])]

    def dusus_txt(x):
        tet = ("tetik yok" if not dogru(x["tetik"]) else
               ("ön köşe sensörü geç tetikledi" if x["tetik_sensor"].startswith("on_s") else "sensör geç tetikledi"))
        return (f"{_sayi_tr(int(x['sahne'].split('_')[2]) / 10)} cm yarık, {x['aci']}°, {sy(say(x['v']), 2)} m/s, {tet}, "
                f"pay {_pay_tr(say(x['pay_min_cm']))} cm")

    b3_yarik = K3["yarik_dar"]["3B"]["dusen"]
    b3_tetiksiz = sum(1 for x in b3_yarik if not dogru(x["tetik"]))
    dd = sorted({say(x["d"]) for x in H3rows if x["alt"] == "donus_dar"})

    def donus_d(k):
        q = K3["donus_dar"][k]["dusen"]
        return " / ".join(f"{sum(1 for x in q if say(x['d']) == d_)}" for d_ in dd)

    hizlar = " / ".join(sy(v_, 2) for v_ in h3["hizlar"])
    b_tohum = bel(U, "Uçurum", "önceki hiçbir sonuç dosyasında geçmiyor", ["38 CSV'nin ve 35 ham kaydın hiçbirinde yok"],
                  "hüküm 3'ün tohumları 211–220 önceki 38 sonuç tablosunun ve 35 ham kaydın hiçbirinde yok")
    b_sahne = bel(U, "Uçurum", "hiçbiri daha önce koşulmamıştı",
                  ["hiçbiri önceki kayıtlarda geçmiyor, hiçbirinin geometrisi eski"],
                  "hüküm 3'ün sahneleri önceki kayıtlarda yok, geometrileri eskilerle aynı değil (parlak zemin sahneleri "
                  "dışında: düz zemin, yeni olan dönüşsüz okuma oranı)")
    b_onkayit = bel(U, "Uçurum", "koşudan önce yazıldı", ["06:27, koşudan önce"],
                    "hüküm 3'ün ölçütü ve görev listesi koşudan önce yazıldı (ön kayıt)")
    b_kose = bel(U, "Uçurum", "1,5 m derinlikteki köşe sensörün menzili dışında",
                 ["(D 1,5 m) sensör menzilinin (1,3 m) dışında"],
                 "hüküm 3'te 1,5 m derin köşe sahnesi sensör menzilinin (1,3 m) dışında: sensör ve hakem için eski köşeyle aynı")
    b_77 = bel(U, "Uçurum", "en çok ≈ 77°", ["en çok ≈ 77° döner (w 0,15 rad/s)"],
               "sürüş kurallı düzen dönüş görevinin süresinde geri yayla en çok ≈ 77° döner (öbürleri 1 rad/s ile döner)")
    b_25 = bel(U, "Uçurum", "±2 cm'den ±2,5 cm'ye", ["±2 cm ile ±2,5 cm"],
               "iki 14 sensörlü düzen yalnız iz çiftinin aralığında ayrılıyor: ±2 cm ve ±2,5 cm")
    b_etek = bel(U, "Uçurum", "9 mm", ["Etek sınırına uzaklık 9 mm"],
                 "onaylı düzende dış iz sensörü etek sınırına 9 mm")
    kosul_ok = h3["kosul"] == [json.dumps(hk, ensure_ascii=False)]
    if not kosul_ok:
        raise SystemExit("Uçurum: hüküm 3'ün ortak koşulu secim.json'daki hüküm koşuluyla tutmuyor.")
    kosul_txt = (f"kısa kip {hk['periyot_ms']} ms, {sy(hk['menzil_m'])} m menzil, enkoderle konum tutma, "
                 f"{sy(secim['fren_ivme'])} m/s² rampa freni")

    hukum = (f"Taze kümede önceden konan ölçüte göre <strong>yalnız {adq(sk)} düzeni geçti</strong> ve onaylı "
             f"seçim oldu. Ölçüt: uçurum koşularında 0 hakem düşmesi, yanlış alarm koşularında 0 durma, bütün hızlar, "
             f"hatalı koşu geçti sayılmaz. Bu düzen {S['n']} uçurum koşusunda {S['d']} hakem düşmesi, {S['ya']} yanlış "
             f"alarm koşusunda {S['durma']} durma verdi; {S['hata']} hata. Öbür dört düzen geçmedi: "
             + "; ".join(f"{adq(k)} {T3[k]['d']} / {T3[k]['n']} hakem ve {T3[k]['f']} fiziksel düşme" for k in
                         ["6", "10", "14", "3B"] if k in kac)
             + f". <strong>Pay ince:</strong> en küçük pay {_pay_tr(S['p'])} cm, {len(s3)} koşuda 1 cm'nin altında. "
               "Bu, simülasyonda ölçütün sağlandığını gösterir; geniş bir güvenlik payı değildir.")
    once_simdi = [
        ("Hüküm",
         f"Görülmüş ızgarada geçmedi, onaylı düzen yoktu. En iyi aday {h2['sensor']} sensör (iz ±2 cm): hakem "
         f"{h2['dus']} / {h2['uc']}, fiziksel {r['fiz2'][0]}. {h1['sensor']} sensör: hakem {h1['dus']} / {h1['uc']}, "
         f"fiziksel {r['fiz1'][0]}. 6 sensörün sınamasında dar yarık yoktu.",
         f"Taze kümede yalnız {adq(sk)} geçti: hakem {S['d']} / {S['n']}, yanlış durma {S['durma']} / "
         f"{S['ya']}, {S['hata']} hata. Aynı görevlerde ±2 cm izli düzen {T3['14']['d']} / {T3['14']['n']}, "
         f"10 sensör {T3['10']['d']}, 6 sensör {T3['6']['d']} hakem düşmesi verdi."),
        ("Sensör düzeni",
         "Karar verilmedi; 6, 10 ve 14 sensör tehlike sınıfına göre yan yana gösterildi.",
         f"Onaylı seçim (seçim dosyasından): {secim['sensor_n']} sensör, her teker hizasında iki dar iz, iki yan "
         f"sensör; tek değişiklik iz çiftinin aralığı {b_25}. Yalnız yazılım kuralı eklenen 10 sensör dönüşü kapattı "
         f"ama dar yarıkta düştü."),
        ("Hüküm verisi",
         f"Tohumlar yeniydi ama 14 sensörün {r['ayni_gorev'][1]} hüküm görevinden {r['ayni_gorev'][0]} tanesi 10 "
         "sensörün hükmüyle aynı sahne ve senaryoydu; düzeltmeyi yönlendiren durumlar aynen yinelendi.",
         f"Tohum {h3['tohum'][0]}–{h3['tohum'][1]} {b_tohum}; {h3['sahne_n']} sahnenin {b_sahne}. Ölçüt "
         f"{b_onkayit}. Beş düzen aynı {h3['taban_n']} görevi koştu (sahne, senaryo ve tohum eşli)."),
        ("Hız önerisi",
         f"Sayfada iki ifade vardı: sınamada 0,39 m/s'de pay {sy(eu['pay_dar'])} cm, ayrıca \"ilk denemeler 0,25 m/s\".",
         f"Tek öneri {sy(secim['hiz_onerisi_m_s'], 2)} m/s (seçim dosyası). Dayanağı ±2 cm izli 14 sensörle yapılan "
         f"duyarlılık ölçümü: 0,25 m/s'de en kötü tekil pay {sy(r['k25'][0])} cm ({r['k25'][1].lower()}). Onaylı "
         "düzenle yinelenmedi."),
        ("Eğimde fren",
         f"10° inişte frenden sonra robot {sy(eu['inis_kayma'][1], 2)} m/s kayıyordu; \"tutma freni gerekir\".",
         f"2,0 m/s² rampa freni ve enkoderle konum tutma: kayma {tam(r['kayma'][0])} mm/s'den en çok "
         f"{sy(r['kayma'][1])} mm/s'ye indi. Taze kümede rampa ucunda ({h3['alan']['rampa']}) beş düzende de "
         f"{sum(K3['rampa_ucu'][k]['d'] for k in T3)} düşme."),
        ("Sensör zamanlaması",
         "Saniyede 50 örnek ile 4 m menzil birlikte varsayılmıştı (veri sayfasıyla çelişiyordu).",
         f"Kısa kip, 20 ms, 1,3 m menzil seçildi. Uzun kip 100 ms 0,39 m/s'de {r['u100_039'][1]} / {r['u100_039'][2]} "
         "koşuda düşüyor."),
    ]
    rozet = (rz("Bağımsız hüküm: geçti", "iyi") + rz("İnceleme: sayılar tuttu, sızıntı yok", "iyi")
             + rz(f"Pay ince: {_pay_tr(S['p'])} cm"))
    olculen = (
        "<p>Görülmüş ızgaradaki hükümler ölçütü sağlamadığı için yeni bir bağımsız hüküm koşuldu. Adaylar koşudan önce "
        f"donduruldu; ölçüt, fiziksel düşme tanımı ve görev listesi {b_onkayit}. Taze küme: tohum {h3['tohum'][0]}–"
        f"{h3['tohum'][1]} ve {h3['sahne_n']} yeni sahne (dar yarık {h3['alan']['yarik']}, eğik yarık, dar açıklık "
        f"{h3['alan']['acik']}, kenardan {h3['alan']['d']}'de dönüş, iki yeni merdiven ve burunlu merdiven, iki köşe, "
        f"dikdörtgen kuyu, {h3['alan']['rampa']} rampa ucu, düz zeminde yanlış alarm sahneleri). Beş düzen aynı "
        f"{h3['taban_n']} görevi koştu: toplam {h3['kosu_n']} koşu, hızlar {hizlar} m/s, {sum(t['hata'] for t in T3.values())} "
        f"hata. Hepsi ortak koşulla: {kosul_txt}. Hakemin düşme saydığı {h3['fiz_n']} koşunun hepsi koşu sürdürülerek "
        f"yeniden koşuldu (fiziksel doğrulama), {h3['fiz_hata']} hata. Hakem: teker merkezi kenarı geçerse düşme. "
        f"Fiziksel düşme: {esik_fiz}, ya da gövde zemine değer (ön kayıtlı tanım). Hepsi MuJoCo, önerilen firmware ve "
        "önde omni tekerli robot modeliyle.</p>")
    ana = ("<h4>Ön kayıtlı ölçüte göre, düzen başına</h4>" + h3["t1"]
           + "<p class='tablo-not'>Ölçüt: uçurum koşularında 0 hakem düşmesi, yanlış alarm koşularında 0 durma; ızgaradaki "
             f"bütün hızlar ({hizlar} m/s) sayılır, hatalı koşu geçti sayılmaz. Fiziksel düşme yalnız hakemin düşme "
             "saydığı koşular sürdürülerek ölçülür (hakem düşmesi 0 ise fiziksel de 0). Pay: koşu boyunca dört teker "
             "merkezinin kenara en küçük yatay uzaklığı; eksi pay, teker merkezinin kenarı o kadar geçtiği anlamına "
             "gelir. Yavaşlama: sürüş kurallı düzende şüpheli okumanın başlattığı kısa sürünme; robot durmaz.</p>"
           + "<h4>Beş düzen yan yana, tehlike sınıfına göre</h4>"
           + "<p class='ince'>Hücre: hakem düşmesi / koşu · fiziksel düşme / sürdürülen koşu · en küçük pay. "
             + ("Bütün hücreler ölçüldü, boş hücre yok." if not h3["bos"] else
                f"<span class='uyari'>{h3['bos']} hücre ölçülmedi.</span>")
             + f" Beş düzen aynı görevleri koştu: aynı sahne, senaryo ve tohum.</p>" + h3["t2"]
           + "<h4>Nerede düşüldü</h4>" + liste([
               "<strong>Bütün düzenlerde 0 düşme:</strong> merdiven başı, kuyu, dar açıklığa ileri yaklaşma, geniş kenara "
               "geri gitme, geniş kenarda yerinde dönüş ve rampa ucu.",
               f"<strong>6 sensör:</strong> dar yarık {K3['yarik_dar']['6']['d']}, eğik yarık {K3['yarik_egik']['6']['d']}, "
               f"dar açıklık yanında dönüş {K3['donus_dar']['6']['d']}, dar açıklığa geri {K3['dar_geri']['6']['d']}, köşe "
               f"{K3['kose_ileri']['6']['d']} hakem düşmesi; fiziksel {T3['6']['f']}.",
               f"<strong>10 sensör:</strong> dar açıklık yanında dönüş {K3['donus_dar']['10']['d']} (fiziksel "
               f"{K3['donus_dar']['10']['f']}), dar yarık {K3['yarik_dar']['10']['d']} (fiziksel "
               f"{K3['yarik_dar']['10']['f']}), eğik yarık {K3['yarik_egik']['10']['d']}. Dönüşte düşmeler kenara yakın "
               f"merkezlerde: d {' / '.join(_sayi_tr(d_) for d_ in dd)} m için 6 sensörde {donus_d('6')}, 10 sensörde "
               f"{donus_d('10')} (her d'de {K3['donus_dar']['10']['n'] // len(dd)} koşu).",
               f"<strong>14 sensör, iz ±2 cm:</strong> dar yarıkta {len(d14)} hakem düşmesi, fiziksel "
               f"{K3['yarik_dar']['14']['f']}: " + "; ".join(dusus_txt(x) for x in d14) + ".",
               f"<strong>10 sensör + sürüş kuralları:</strong> dar açıklık yanında dönüşü kapattı "
               f"({K3['donus_dar']['3B']['d']} / {K3['donus_dar']['3B']['n']}), ama dar yarıkta "
               f"{K3['yarik_dar']['3B']['d']} / {K3['yarik_dar']['3B']['n']} düştü (fiziksel "
               f"{K3['yarik_dar']['3B']['f']}); bu düşmelerin {b3_tetiksiz} tanesinde hiçbir sensör tetiklemedi. Kural "
               f"donanımın görmediği yarığı kapatamaz. Yanlış alarm koşularında yavaşlama {T3['3B']['surun']} / "
               f"{T3['3B']['ya']} koşuda başladı, durma olmadı.",
               f"<strong>Onaylı düzen:</strong> bütün sınıflarda 0 düşme. En küçük pay {_pay_tr(S['p'])} cm ({ince_txt}); "
               f"{len(s3)} koşuda pay 1 cm'nin altında ("
               + ", ".join(f"{n_} {KISA.get(a_, a_)}" for a_, n_ in sorted(s3_sinif.items(), key=lambda t_: -t_[1]))
               + ").",
           ]))
    # grafik: düzen başına düşme; dar yarıkta iki 14 sensörlü düzenin payı
    g1 = [(f"{b_}", [T3[k]["d"], T3[k]["f"]], [f"{T3[k]['d']} / {T3[k]['n']}", f"{T3[k]['f']}"])
          for k, b_, _, _ in DUZEN3]
    grafik = cubuk_grafik(
        f"Uçurum koşularında düşme, düzen başına ({S['n']} koşu)",
        [("hakem düşmesi", "--c-b"), ("fiziksel düşme", "--c-a")], g1,
        en_buyuk=max(1, max(T3[k]["d"] for k in T3)),
        aciklama="Hakem düşmesi ölçütün baktığı sayı. Fiziksel düşme, hakemin düşme saydığı koşu sürdürülünce tekerin "
                 "gerçekten inip inmediği.")
    gen = sorted({int(x["sahne"].split("_")[2]) for x in H3rows if x["alt"] == "yarik_dar"})
    g2 = []
    for g_ in gen:
        vals, txt = [], []
        for k in ("14", sk):
            p_ = mn([say(x["pay_min_cm"]) for x in H3rows if x["duzen"] == k and x["sahne"] == f"h3_yarik_{g_}"])
            vals.append(max(0.0, p_))
            txt.append(f"{_pay_tr(p_)} cm")
            if k == "14":
                p14 = p_
        g2.append((f"{_sayi_tr(g_ / 10)} cm yarık", vals, txt, p14, p_))
    eksi_arti = sum(1 for g in g2 if g[3] < 0 <= g[4])
    yarim_g = [g[0].replace(" cm yarık", "") for g in g2 if g[4] < 1]
    yarim = len(yarim_g)
    yarim_ar = f"{yarim_g[0]}–{yarim_g[-1]} cm" if yarim > 1 else ", ".join(yarim_g) + " cm"
    g2 = [g[:3] for g in g2]
    grafik += cubuk_grafik(
        "Dar yarıkta en küçük pay, yarık genişliğine göre (cm)",
        [("14 sensör, iz ±2 cm", "--c-c"), (ad3(sk), "--c-a")], g2,
        en_buyuk=max(max(v_ for v_ in g[1]) for g in g2),
        aciklama=f"Eksi pay sıfırda kesildi; değer yazıda. İz aralığını yarım santimetre açmak {eksi_arti} genişlikte "
                 f"eksi payı artıya geçirdi; {yarim} genişlikte ({yarim_ar}) pay yine 1 cm'nin altında: kırılma noktası "
                 "bu aralıkta.")
    ana += (f"<details class='eski'><summary>Önce: görülmüş ızgara ({DUZENLER[0][1]}, {DUZENLER[1][1]}, "
            f"{DUZENLER[2][1]}; ayar ve önceki hüküm koşuları)</summary><div class='eski-ic'>"
            f"<p class='hukum eski-hukum'><strong>Önceki hüküm.</strong> {hukum_eski}</p>"
            f"{ana_eski}<h4>Grafik</h4>{grafik_eski}</div></details>")
    oneri = [
        f"<strong>Onaylı seçim:</strong> {adq(sk)} (seçim dosyasından okundu): {secim['sensor_n']} VL53L1X, her "
        f"teker hizasında iki dar iz, iki yanda dışa bakan dar konili sensör. Ortak ayarlar: {kosul_txt}, tek hız önerisi "
        f"{sy(secim['hiz_onerisi_m_s'], 2)} m/s.",
        f"<strong>Kırılma noktası:</strong> dar yarık ve açılı giriş. İz çiftinin aralığı {b_25} açılınca aynı "
        f"görevlerdeki {len(d14)} hakem düşmesi kalktı, ama en küçük pay {_pay_tr(S['p'])} cm. Fark yarım santimetre; "
        "gerçek lastik, sensör konisi, dar koninin sinyal kaybı ya da montaj hatası bu payı yiyebilir.",
        f"<strong>Daha ucuz düzenler:</strong> 6 ve 10 sensör dar yarıkta ve dar açıklık yanında dönüşte düşüyor; 6 sensör "
        f"ayrıca dar açıklığa geri giderken ({K3['dar_geri']['6']['d']} / {K3['dar_geri']['6']['n']}). Yalnız yazılım "
        f"kuralı eklemek dönüşü kapatıyor ama yarığı kapatmıyor. Bunlardan biri kullanılacaksa dar yarıklar ve dar "
        "açıklıklar binada fiziksel olarak kapatılmalı.",
        f"<strong>Bedel:</strong> 14 sensör (6 sensörün 2,3 katı), 6'sında dar koni ayarı, büyük olasılıkla ikinci bir "
        f"I2C hattı, eteğin iki yanında pencere; dış iz sensörü etek sınırına {b_etek}. Yan sensörler robotu yan kenarı "
        f"bir uçuruma {b9} yakınken durdurur, {b70} dar şeritte robot sürülemez.",
        f"<strong>Fren ve eğim:</strong> 2,0 m/s² rampa ve enkoderle konum tutma. Konum tutma teker başına {b070} "
        f"istiyor; motorun sürekli torku {b618} tahmin ediliyor, uzun park için mekanik fren gerekebilir.",
    ]
    iyimser = [
        f"{secim['sensor_n']} sensörün tek I2C hattında 20 ms'de gecikmesiz okunduğu varsayıldı; büyük olasılıkla iki "
        "hat gerekir. Sensörler arası etkileşim yok.",
        "Dar koni (ROI 15°) yalnız koni daraltılarak modellendi; sinyal ve menzil kaybı, gürültü artışı yok.",
        "Kısa kip modelde ilk iyimser modelle aynı örnekleme yolunu izliyor; tek fark 1,3 m menzil.",
        f"Teker ve gövde rijit; hakem teker merkezine bakıyor. Pay yarıkta {_pay_tr(S['p'])} cm'ye iniyor, gerçek "
        "lastik birkaç mm içeri girer.",
        "Kalibrasyon hep düz zeminde; yan sensörün izi başlangıçta boşluğun üstündeyse yanlış beklenen değer alınır "
        "(modellenmedi).",
    ]
    aciklar = [
        f"Pay ince: en küçük {_pay_tr(S['p'])} cm, {len(s3)} koşuda 1 cm'nin altında. Masada doğrulanmadan sahada "
        "güvenlik payı varmış gibi okunmamalı.",
        "Kusur (donmuş ya da hep dönüşsüz sensör) ve duyarlılık ızgaraları onaylı düzenle yinelenmedi; dar koninin sinyal "
        "kaybı, çapraz konuşma ve iki I2C hattı modellenmedi.",
        f"Köşe sahnelerinden biri yeni sayılmaz: {b_kose}; yalnız giriş açıları yeni.",
        f"Sürüş kurallı düzenin dönüşteki {K3['donus_dar']['3B']['d']} / {K3['donus_dar']['3B']['n']}'ü eşit maruziyet "
        f"değil: aynı sürede geri yayla {b_77} dönüyor, öbür düzenler yerinde 1 rad/s ile dönmeye çalışıyor.",
        f"6 sensörlü düzen burada ortak koşulla ({kosul_txt}) ölçüldü; kendi tanımında bu koşul yoktu (ön kayıt "
        "kararı). Rampa ucundaki 0 düşme bu koşulun sonucudur.",
        "Sürülebilir en dar şerit hiçbir düzende ölçülmedi; satın alma ve montaj masada doğrulamadan sonra.",
    ]
    ust = {
        "hukum": f"Taze kümede ölçüte göre <strong>geçti</strong>: yalnız {adq(sk)} düzeni. Hakem {S['d']} / {S['n']}, "
                 f"yanlış durma {S['durma']} / {S['ya']}, {S['hata']} hata. Aynı görevlerde geçmeyenlerin hakem düşmesi: "
                 + "; ".join(f"{adq(k)} {T3[k]['d']}" for k in ["6", "10", "14", "3B"] if k in kac)
                 + f". Pay ince: en küçük {_pay_tr(S['p'])} cm.",
        "once": f"Görülmüş ızgarada ölçüte göre <strong>geçmedi</strong>, onaylı düzen yoktu. En iyi aday "
                f"{h2['sensor']} sensör (iz ±2 cm): hakem {h2['dus']} / {h2['uc']}, fiziksel {r['fiz2'][0]}. "
                f"{h1['sensor']} sensör: hakem {t10[0]} / {t10[1]}, fiziksel {t10[2]}. 6 sensör {t6[0]} / {t6[1]}, ama dar "
                "yarık, dar açıklığa geri ve dar açıklık yanında dönme sınanmamıştı.",
        "rozet": rz("Bağımsız hüküm: geçti", "iyi") + rz("Pay ince"),
        "karar": f"Onaylı seçim (seçim dosyası): {adq(sk)}, yani {secim['sensor_n']} VL53L1X, her teker "
                 f"hizasında iki dar iz, iki yan sensör. Ortak: {kosul_txt}, tek hız önerisi {sy(secim['hiz_onerisi_m_s'], 2)} m/s. "
                 f"Pay ince ({_pay_tr(S['p'])} cm): satın almadan önce masada iki I2C hattı, dar koni ve etek penceresi "
                 "doğrulanmalı.",
    }
    y = {"hukum": hukum, "rozet": rozet, "os": once_simdi, "olculen": olculen, "ana": ana, "grafik": grafik,
         "oneri": oneri, "iyimser": iyimser, "aciklar": aciklar}
    return r, y, ust


def harita_yeni(eh):
    ab = oku(H / "ab_2b.csv")
    ek = oku(H / "kayip_ek_2b.csv")
    ky = oku(H / "kayip_2b.csv")
    kp = [x for x in oku(T / "kipler_2b.csv") if x["kume"] == "sinama"]
    r = {}
    bic = {et: (ad, f) for et, ad, f in ETKEN}
    # sıralama (yalnız tam ızgaralı A'dan B'ye)
    sira = []
    for et, ad, f in ETKEN:
        rs = [x for x in ab if x["etken"] == et]
        if not rs:
            continue
        kad = {}
        for x in rs:
            t_ = kad.setdefault(int(x["kademe"]), [0, 0])
            t_[0] += 1
            t_[1] += dogru(x["basari"])
        b = sum(dogru(x["basari"]) for x in rs)
        yakin = sum(1 for x in rs if not dogru(x["basari"]) and 0.30 <= (say(x["varis_hatasi_m"]) or 9) < 0.35)
        en_kotu = min(v[1] / v[0] for v in kad.values())
        sira.append((b / len(rs), en_kotu, ad, b, len(rs), (b + yakin) / len(rs)))
    sira.sort(key=lambda x: (round(x[0], 9), x[1]))
    r["sira"] = sira
    ssat = []
    i = 0
    for o, ek_, ad, b, n, yk in sira:
        if o >= 0.9999:
            continue
        i += 1
        ssat.append([str(i), ad, f"%{tam(100 * o)} <span class='ince'>({b}/{n})</span>", f"%{tam(100 * ek_)}",
                     f"%{tam(100 * yk)}"])
    kalan = [s[2] for s in sira if s[0] >= 0.9999]
    ssat.append([f"{i + 1}–{i + len(kalan)}", f"Geri kalan {len(kalan)} etken (insan, ölçek, genişlik, eğrilme, "
                 "gürültü, odometri)", "%100", "%100", "%100"])
    ana = tablo(["Sıra", "Etken", "A'dan B'ye ortalama başarı", "En kötü kademe", "Sınırdakiler başarı sayılırsa"],
                ssat, not_="Sıra yalnız bütün kademeleri koşulmuş A'dan B'ye ortalamasından (etken başına 4 kademe × 12 "
                           "koşu), eşitlikte en kötü kademe. Sınırdaki koşu: robot hedefe 0,30–0,34 m'de \"vardım\" deyip "
                           "durdu (başarı ölçütü 0,30 m).")
    # kayıp robotta genişlik
    tb = ort([say(x["konum_ort_m"]) for x in ky if x["kosul"] == "taban"])
    gsat = []
    gek = {}
    for x in ek:
        gek.setdefault(int(x["kademe"]), []).append(x)
    for kd in sorted(gek):
        rs = gek[kd]
        dg = say(rs[0]["deger"])
        gsat.append([f"±{sy(dg * 100) if (dg * 100) % 1 else tam(dg * 100)} cm",
                     kesir(sum(dogru(x["basari"]) for x in rs), len(rs), len(rs)),
                     str(sum(1 for x in rs if x["karar_dogru"] and not dogru(x["karar_dogru"]))),
                     str(sum(int(say(x["temas_olay"]) or 0) for x in rs)),
                     sy(ort([say(x["konum_ort_m"]) for x in rs]), 3)])
    r["gen"] = (sum(dogru(x["basari"]) for x in ek), len(ek),
                ort([say(x["konum_ort_m"]) for x in gek[max(gek)]]), tb)
    ana += "<h4>Kayıp robotta koridor genişlik sapması (yeni, ana ızgarayla aynı tohumlar)</h4>" + tablo(
        ["Genişlik sapması", "Başarı", "Yanlış koridor kararı", "Temas", "Karardan sonra konum hatası ort (m)"], gsat,
        not_=f"Bozulmasız tabanda konum hatası ortalaması {sy(tb, 3)} m. Hata duvar kaymasının yaklaşık yarısı kadar "
             "büyüyor; sıçrama yok.")
    # kip karşılaştırması: eskimiş harita, taşınma yok
    kos_ad = {}
    for x in ab:
        if x["kosul"] not in kos_ad and x["etken"] in bic:
            kos_ad[x["kosul"]] = f"{bic[x['etken']][0]}: {bic[x['etken']][1](say(x['deger']))}"
    kos_ad.update({"okul_hafif": "Okul günü, hafif", "okul_orta": "Okul günü, orta", "okul_agir": "Okul günü, ağır"})
    ESKI = ["okul_hafif", "okul_orta", "okul_agir", "kapi_2", "kapi_3", "cam_2", "donussuz_3"]
    KIP3 = [("v3", "v3 (varsayılan)", "--c-c"), ("izleme", "izleme kipi", "--c-a"), ("algi", "algılı kip", "--c-b")]
    ksat, kgraf = [], []
    r["kip_eski"] = {}
    for kos in ESKI:
        hh, vals, txt = [], [], []
        for kip, _, _ in KIP3:
            rs = [x for x in kp if x["kosul"] == kos and x["kip"] == kip]
            dv = sum(x["sonuc"] == "dogru_varis" for x in rs)
            sh = sum(x["sonuc"] == "sessiz_hata" for x in rs)
            r["kip_eski"][(kos, kip)] = (dv, len(rs), sh)
            hh.append(f"{kesir(dv, len(rs), 0.9 * len(rs))} <span class='ince'>({sh} sessiz hata)</span>")
            vals.append(dv)
            txt.append(f"{dv}/{len(rs)}")
        ksat.append([kos_ad[kos]] + hh)
        kgraf.append((kos_ad[kos], vals, txt))
    top = {kip: [sum(r["kip_eski"][(k_, kip)][i_] for k_ in ESKI) for i_ in range(3)] for kip, _, _ in KIP3}
    r["kip_top"] = top
    ksat.append(["<strong>Toplam</strong>"] + [f"<strong>{top[k][0]}/{top[k][1]}</strong> <span class='ince'>"
                                                f"({top[k][2]} sessiz hata)</span>" for k, _, _ in KIP3])
    ana += "<h4>Eskimiş harita, taşınma yok: kip başına doğru varış (yeni tohumlar 5, 6)</h4>" + tablo(
        ["Koşul"] + [ad for _, ad, _ in KIP3], ksat,
        not_="Sessiz hata: robot yanlış yerde \"vardım\" dedi. Bu turun hakemi daha katı (koşu yalnız beyin \"vardım\" "
             "deyince biter) ve tohumlar yeni; sayılar önceki tablolarla birebir karşılaştırılmaz. Algılı kipin düşük "
             "varışı boşuna \"kayboldum\" deyip durmasından (taşınma bölümü).")
    grafik = cubuk_grafik("Eskimiş haritada doğru varış, kip başına (12 koşu)", [(a_, c_) for _, a_, c_ in KIP3], kgraf,
                          en_buyuk=12, aciklama="Okul günü ağır hâlinde her kip 12 koşuda en çok 2 doğru varış.")
    vd = eh["varyant"]
    sm = eh["sira_metin"]
    hukum = (f"Değişmedi: kapı durumu, cam, menzil ve dönüş vermeyen yüzey kırıyor, bozulma ani. Bu turda zarar sırası "
             f"düzeltildi: {sm}. Kayıp robotta genişlik sapması da kırmıyor ({r['gen'][0]}/{r['gen'][1]}). Yeni tohumlarla "
             f"eskimiş haritada izleme kipi {top['izleme'][0]}/{top['izleme'][1]}, v3 {top['v3'][0]}/{top['v3'][1]} doğru "
             "varış; okul günü ağır hâlinde her kip en çok 2/12.")
    once_simdi = [
        ("Zarar sırası",
         "Sonuç belgesi \"dönüşsüz > menzil > kapı\" diyordu (kayıp robottaki eşit olmayan kapsamdan); bu sayfanın grafiği "
         "okul gününü de sıraya katıyordu.",
         f"Yalnız A'dan B'ye ortalamasıyla, eşitlikte en kötü kademe: {sm}."),
        ("Kayıp robotta genişlik sapması", "Koşulmamıştı.",
         f"±2,5–10 cm'de {r['gen'][0]}/{r['gen'][1]}, yanlış koridor 0, temas 0; konum hatası en çok "
         f"{sy(r['gen'][2], 3)} m."),
        ("İzleme kipi",
         f"Ayrı tohumlarda (3, 4) okul günü orta {vd[('izleme', 'okul_orta')][1]}/12, kapı %50 "
         f"{vd[('izleme', 'kapi_3')][1]}/12.",
         f"Yeni tohumlarda (5, 6), katı hakemle okul günü orta {r['kip_eski'][('okul_orta', 'izleme')][0]}/12, kapı %50 "
         f"{r['kip_eski'][('kapi_3', 'izleme')][0]}/12; eskimiş haritada toplam {top['izleme'][0]}/{top['izleme'][1]} "
         f"(v3 {top['v3'][0]}/{top['v3'][1]})."),
    ]
    rozet = rz("İnceleme: geçer", "iyi") + rz("Engelleyici yok; belgede küçük düzeltmeler", "iyi")
    olculen = ("<p>İncelemenin açık bıraktıkları: zarar sırasının düzeltilmesi, kayıp robotta koridor genişlik sapması "
               f"({len(ek)} koşu) ve izleme kipinin dört kiple aynı koşullarda karşılaştırılması (taşınma bölümündeki "
               "720 koşunun eskimiş harita kısmı). Ana ızgaranın CSV'leri değişmedi; analiz yeniden koşulunca birebir aynı "
               "çıktı.</p>")
    oneri = [
        f"<strong>Sıra:</strong> {sm}. Sınırdaki 5 koşu başarı sayılırsa cam %50'de kırar, ani kayma hiç kırmaz; kapı, cam "
        "ve menzil iki sayımda da ilk üçte.",
        "<strong>Öneri (ölçülmedi, varsayılan değişmedi):</strong> bilinen başlangıçta izleme kipi, \"emin değilim\" "
        "denetimi ve kapı / camda geçiş testi kapatılmış taşınma algısı birlikte. Tam gerileme koşusu olmadığı için "
        "varsayılan v3.",
        "<strong>Gerçekte ilk ölçülecek:</strong> okul koridorunda dönüş vermeyen yüzeyler ve etkin menzil (sıranın 2.–4. "
        "etkenleri buna bağlı), haritanın gün içinde ne kadar eskidiği.",
    ]
    iyimser = [
        "Duvar ideal ince levha, ışın sonsuz ince; cam yalnız kapılarda ve tam saydam (yalnız 2B).",
        "Kapı kanadı koridora açılmıyor; eşya yolu kapatmıyor; insanlar yol veriyor.",
        "Taban harita kusursuz; 2B robot kinematik, sonar yok; tek kat, düz zemin.",
    ]
    aciklar = [
        "Kayıp robot 20 koşulda (genişlik eklendi); MuJoCo'da cam ve kayıp robot yok.",
        "Bu turda 6 haritalı beyin, MuJoCo doğrulaması ve tam gerileme koşusu yapılmadı.",
        "Eşitlikte \"en kötü kademe\" kuralı yalnız dönüşsüz yüzey ile ani kaymayı ayırıyor; 12 koşuda kırılma ± 1 kademe.",
    ]
    ust = {
        "hukum": f"Değişmedi: kapı, cam, menzil ve dönüşsüz yüzey kırıyor, bozulma ani. Zarar sırası düzeltildi ({sm}); "
                 f"kayıp robotta genişlik sapması da kırmıyor ({r['gen'][0]}/{r['gen'][1]}).",
        "rozet": rz("İnceleme: geçer", "iyi"),
        "karar": "Haritaya güvenmeden önce okul koridorunda dönüş vermeyen yüzeyler, etkin menzil ve kapı değişimi ölçülmeli. "
                 "Bilinen başlangıçta izleme kipi eskimiş haritada en çok varışı veriyor, ama taşınmada kendini "
                 "kurtaramıyor; varsayılan v3 kaldı.",
    }
    y = {"hukum": hukum, "rozet": rozet, "os": once_simdi, "olculen": olculen, "ana": ana, "grafik": grafik,
         "oneri": oneri, "iyimser": iyimser, "aciklar": aciklar}
    return r, y, ust


KIP4 = [("v3", "v3 (varsayılan)"), ("izleme", "İzleme"), ("algi", "Algılı"), ("izleme_algi", "İzleme + algı")]


def tasinma_yeni(et):
    kp = [x for x in oku(T / "kipler_2b.csv") if x["kume"] == "sinama"]
    emin = json.loads((T / "emin_secim.json").read_text(encoding="utf-8"))
    ab = oku(H / "ab_2b.csv")
    bic = {e_: (ad, f) for e_, ad, f in ETKEN}
    kos_ad = {"okul_hafif": "Okul günü, hafif", "okul_orta": "Okul günü, orta", "okul_agir": "Okul günü, ağır",
              "taban": "Bozulmasız"}
    for x in ab:
        if x["kosul"] not in kos_ad and x["etken"] in bic:
            kos_ad[x["kosul"]] = f"{bic[x['etken']][0]}: {bic[x['etken']][1](say(x['deger']))}"

    def grup(x):
        k = x["kosul"]
        if k == "taban":
            return "temiz"
        if "+" not in k:
            return "eski"
        return "tas_temiz" if k.startswith("taban+") else "tas_eski"

    def dogru_dv(x):
        return x["sonuc"] == "dogru_varis" or (x["tur"] == "baska_koridor" and x["sonuc"] == "guvenli_durma")

    r = {"g": {}}
    GR = [("temiz", "Temiz harita, taşınma yok", "v3 (varsayılan)"),
          ("eski", "Eskimiş harita, taşınma yok (okul günü 3 hâl, kapı %25 ve %50, cam %50, dönüşsüz %50)",
           "izleme + \"emin değilim\" denetimi"),
          ("agir", "  yalnız okul günü ağır", "hiçbiri iyi değil; zorunluysa algılı"),
          ("tas_temiz", "Taşınma riski, temiz harita (4 taşıma türü)", "algılı"),
          ("tas_eski", "Taşınma + eskimiş harita (kapı %25, cam %50, dönüşsüz %50; 1–3 m taşıma)",
           "iyi seçenek yok: algılı (sessiz hata 0) ya da v3 (daha çok varış)")]
    osat = []
    for g, ad, oner in GR:
        hh = []
        for kip, _ in KIP4:
            rs = [x for x in kp if x["kip"] == kip and (grup(x) == g if g != "agir" else x["kosul"] == "okul_agir")]
            d_ = sum(dogru_dv(x) for x in rs)
            sh = sum(x["sonuc"] == "sessiz_hata" for x in rs)
            gd = sum(x["sonuc"] == "guvenli_durma" for x in rs)
            r["g"][(g, kip)] = (d_, len(rs), sh, gd)
            hh.append(f"{kesir(d_, len(rs), 0.9 * len(rs))}<br><span class='ince'>{sh} sessiz, {gd} durma</span>")
        osat.append([ad.replace("  ", "&nbsp;&nbsp;↳ ")] + hh + [oner])
    ana = tablo(["Koşul"] + [a_ for _, a_ in KIP4] + ["Öneri"], osat,
                not_="Hücre: doğru davranış / koşu (hedefe doğru varış; başka koridora taşımada güvenle durma), altında "
                     "sessiz hata (yanlış yerde \"vardım\") ve güvenli durma sayısı. Sınama, tohum 5 ve 6, 6 koridor, 2B.")
    # algılı kipin yanlış alarmı
    YK = ["taban", "kapi_2", "cam_2", "kapi_3", "donussuz_3", "okul_hafif", "okul_orta", "okul_agir"]
    asat, agraf = [], []
    r["alarm"] = {}
    for kos in YK:
        al = [x for x in kp if x["kip"] == "algi" and x["kosul"] == kos]
        ia = [x for x in kp if x["kip"] == "izleme_algi" and x["kosul"] == kos]
        na = sum(int(x["alarm"]) > 0 for x in al)
        r["alarm"][kos] = (na, len(al))
        asat.append([kos_ad[kos], kesir(na, len(al)) if not na else f"<span class='kotu'>{na}/{len(al)}</span>",
                     f"{sum(x['sonuc'] == 'dogru_varis' for x in al)}/{len(al)}",
                     f"{sum(x['sonuc'] == 'guvenli_durma' for x in al)}/{len(al)}",
                     f"{sum(int(x['alarm']) > 0 for x in ia)}/{len(ia)}"])
        agraf.append((kos_ad[kos], [na], [f"{na}/{len(al)}"]))
    ana += "<h4>Taşınma yokken boşuna \"kayboldum\" (algılı kip)</h4>" + tablo(
        ["Koşul", "Algılı: boşuna alarm verilen koşu", "Algılı: doğru varış", "Algılı: durup yardım bekleme",
         "İzleme + algı: boşuna alarm"], asat,
        not_="Nedeni neredeyse hep aynı: alarm anındaki taramada ışınların bir kısmı haritadaki duvarın arkasına geçiyor "
             "(açılmış kapının ya da camın arkasındaki oda). Dönüş vermeyen yüzey bu oranı büyütmüyor.")
    # fark etme
    tt = [x for x in kp if x["kip"] == "algi" and grup(x) == "tas_temiz"]
    r["fark"] = (sum(x["tepki_s"] != "" for x in tt), len(tt), medyan([say(x["tepki_s"]) for x in tt]))
    TUR_AD = dict(TUR)
    fsat = []
    for tur, tad in TUR:
        q = [x for x in tt if x["tur"] == tur]
        fsat.append([tad, f"{sum(x['tepki_s'] != '' for x in q)}/{len(q)}",
                     sy(medyan([say(x["tepki_s"]) for x in q])) + " s",
                     f"{sum(dogru_dv(x) for x in q)}/{len(q)}"])
    ana += "<h4>Taşınmayı fark etme, algılı kip, temiz harita</h4>" + tablo(
        ["Taşıma türü", "Fark etti", "Fark etme süresi, ortanca", "Doğru davranış"], fsat)
    # emin değilim
    esat = []
    r["emin"] = {}
    for kip, ad in KIP4:
        rs = [x for x in kp if x["kip"] == kip]
        s_ = [x for x in rs if x["sonuc"] == "sessiz_hata"]
        d_ = [x for x in rs if x["sonuc"] == "dogru_varis"]
        onl = sum(x["emin_sonuc"] == "onlenen" for x in rs)
        ger = sum(x["emin_sonuc"] == "gereksiz_durma" for x in rs)
        t1 = sum(1 for x in s_ if say(x["v_u_med"]) is not None and say(x["v_u_med"]) < 0.75)
        t2 = sum(1 for x in d_ if say(x["v_u_med"]) is not None and say(x["v_u_med"]) < 0.75)
        r["emin"][kip] = (onl, len(s_), ger, len(d_), t1, t2)
        esat.append([ad, f"{onl}/{len(s_)}", f"<span class='{'kotu' if ger else ''}'>{ger}/{len(d_)}</span>",
                     f"{t1}/{len(s_)}", f"{t2}/{len(d_)}"])
    gl = emin["gelistirme"]
    esat.append(["Geliştirme (tohum 7, 8; v3 ve izleme)", f"{gl['onlenen']}/{gl['sessiz']}", f"{gl['gereksiz']}/{gl['dogru']}",
                 "-", "-"])
    ger_rows = [x for x in kp if x["emin_sonuc"] == "gereksiz_durma"]
    r["ger_kaynak"] = (sum(1 for x in ger_rows if x["dunya"].startswith("donussuz") and (say(x["v_std_xy"]) or 0) > 0.05),
                       len(ger_rows))
    ana += "<h4>\"Emin değilim, duruyorum\" denetimi (\"vardım\" anında, kayıtlardan)</h4>" + tablo(
        ["Kip", "Seçilen kural: durdurulan sessiz hata", "Boşuna durdurulan doğru varış", "Tek kural (uyum &lt; 0,75): "
         "sessiz hata", "Tek kural: boşuna durma"], esat,
        not_="Seçilen kural geliştirme tohumlarında, sınamadan önce donduruldu: tarama-harita uyumu &lt; 0,75 ya da konum "
             f"belirsizliği &gt; 0,05 m. Geliştirmede boşuna durma sınırı %2 idi; sınamada %5–6. Boşuna durmaların "
             f"{r['ger_kaynak'][0]}/{r['ger_kaynak'][1]}'i dönüşsüz yüzeyde belirsizlik eşiğinden. Tek kural sınamaya "
             "bakıldıktan sonra öne çıktı: hüküm değil, yeni tohumlarla doğrulanacak aday.")
    grafik = cubuk_grafik("Algılı kipin taşınma yokken boşuna alarm verdiği koşu (12 koşuda)",
                          [("boşuna alarm", "--c-b")], agraf, en_buyuk=12,
                          aciklama="Robot güvende kalıyor ama durup yardım bekliyor: eskimiş haritada işe yaramaz.")
    g = r["g"]
    e3, ei = r["emin"]["v3"], r["emin"]["izleme"]
    hukum = (f"Hiçbir kip her koşulda iyi değil; varsayılan v3 değişmedi. Algılı kip temiz haritada taşınmayı "
             f"{r['fark'][0]}/{r['fark'][1]} fark ediyor (ortanca {sy(r['fark'][2])} s) ama taşınma yokken eskimiş "
             f"haritada boşuna \"kayboldum\" diyor: kapı %25'te {r['alarm']['kapi_2'][0]}/12, okul günü ağırda "
             f"{r['alarm']['okul_agir'][0]}/12. \"Emin değilim\" denetimi v3'ün {e3[1]} sessiz hatasından {e3[0]}'ünü "
             f"durdurdu, bedeli {e3[2]}/{e3[3]} doğru varışın boşuna durması.")
    once_simdi = [
        ("Algılı kipin yanlış alarmı",
         "Yalnız insan ve eşyayla ölçülmüştü: bozulmasız ve insanlı koridorda 0; cam, kapı ve dönüşsüz yüzey ölçülmemişti.",
         f"Kapı %25'te {r['alarm']['kapi_2'][0]}/12, cam %50'de {r['alarm']['cam_2'][0]}/12, okul günü hafif / orta / ağır "
         f"{r['alarm']['okul_hafif'][0]} / {r['alarm']['okul_orta'][0]} / {r['alarm']['okul_agir'][0]} koşuda (12'de) "
         "boşuna alarm."),
        ("Taşınmayı fark etme",
         f"Algılı sürüm {et['algi_fark']}/{et['algi_n']} taşımada, ortanca {sy(et['algi_fark_med'])} s.",
         f"Dört kip aynı görevlerde: algılı {g[('tas_temiz', 'algi')][0]}/48 doğru davranış; v3 "
         f"{g[('tas_temiz', 'v3')][0]}/48 ({g[('tas_temiz', 'v3')][2]} sessiz hata); izleme "
         f"{g[('tas_temiz', 'izleme')][0]}/48."),
        ("Sessiz hata önlemi", "Yoktu.",
         f"\"Emin değilim\" denetimi v3'te {e3[0]}/{e3[1]}, izlemede {ei[0]}/{ei[1]} sessiz hatayı durdurdu; boşuna durma "
         f"{e3[2]}/{e3[3]} ve {ei[2]}/{ei[3]}."),
        ("Karar",
         "Algılı sürümü almadan önce cam, açık kapı ve eşyalı koridorda yanlış alarm ölçülmeli.",
         "Ölçüldü: geçiş testi yüzünden algılı kip eskimiş haritada kullanılamaz. Önerilen birleşik kip (izleme + denetim "
         "+ kapı ve camda geçiş testi kapalı) ölçülmedi."),
    ]
    rozet = rz("İnceleme: geçer", "iyi") + rz("Engelleyici yok; belgede 4 düzeltme", "iyi")
    olculen = (f"<p>Dört kip (v3, izleme, algılı, izleme + algı) aynı görevlerde eşli koşuldu: sınamada tohum 5 ve 6, "
               f"{len(kp)} koşu, 15 koşul; geliştirmede tohum 7 ve 8, 168 koşu. Tek haritalı A'dan B'ye, 2B benzetici. "
               "\"Emin değilim\" denetimi robotun \"vardım\" dediği anda yalnız robotun gördükleriyle karar veriyor; "
               "kuralı geliştirmede seçildi, sınamadan önce donduruldu.</p>")
    oneri = [
        "<strong>Seçim:</strong> temiz haritada v3; eskimiş haritada izleme + denetim; taşınma riski varsa algılı. "
        "Taşınma ve eskime birlikteyse iyi seçenek yok.",
        f"<strong>Algılı kipin düzeltmesi (ölçülmedi):</strong> geçiş testini kapı açıklıklarında ve cam olabilecek "
        f"yüzeylerde kapatmak. Bunun fark etmeyi ne kadar düşüreceği bilinmiyor; 180° çevrilme zaten en zor tür "
        f"({TUR_AD['ters180'].lower()}).",
        f"<strong>Denetimin eşiği:</strong> belirsizlik eşiği 0,05 m sıkı çıktı (boşuna durmaların "
        f"{r['ger_kaynak'][0]}/{r['ger_kaynak'][1]}'i). Eşit sonuçlu aday kurallar arasında seçim sözlük sırasıyla yapıldı "
        "ve 0,05 ızgaranın en alt eşiği; tek kural (uyum &lt; 0,75) yeni tohumlarla sınanmalı.",
        "<strong>Gözle görülmeyen:</strong> izleme kipinde taşınmadan sonra kayan tahmin hedefte haritaya iyi uyabiliyor; "
        "bu sessiz hataların bir kısmı uyumla yakalanamaz. Konum sıçraması iyi ve kötüyü ayırmıyor.",
    ]
    iyimser = [
        "2B benzetici; ideal ince duvar; cam yalnız kapılarda ve tam saydam.",
        "Taşıma anlık: kaldırırken teker dönmüyor, taşıyan kişi görünmüyor.",
        "Algının ve denetimin Pi 5'teki süresi ölçülmedi.",
    ]
    aciklar = [
        "Plandaki 29 sınama koşulunun 15'i koşuldu; atılanlar sonuç belgesinde. Yarım kalan 9 cam koşusu tablolara girmedi.",
        "6 haritalı beyin, MuJoCo ve tam gerileme bu turda yok; bu yüzden varsayılan değiştirilemez.",
        "Kural geliştirmede yalnız v3 ve izlemeyle, dönüşsüz yüzey olmadan seçildi; algılı kiplere öyle uygulandı.",
        "Sınama koşarken bir kip dosyası düzenlendi; aynı tohumla üç yeniden koşu birebir aynı çıktı, değişiklik "
        "gösterilemiyor (sürüm geçmişi yok).",
    ]
    ust = {
        "hukum": f"Hiçbir kip her yerde iyi değil. Algılı kip taşınmayı {r['fark'][0]}/{r['fark'][1]} fark ediyor ama "
                 f"eskimiş haritada taşınma yokken boşuna alarm veriyor (kapı %25'te {r['alarm']['kapi_2'][0]}/12); "
                 f"\"emin değilim\" denetimi v3'ün {e3[1]} sessiz hatasından {e3[0]} tanesini durdurdu.",
        "rozet": rz("İnceleme: geçer", "iyi"),
        "karar": "Varsayılan v3 kaldı. Algılı kip, geçiş testi kapı ve camda kapatılıp yeniden ölçülmeden gerçek robota "
                 "alınmamalı; \"emin değilim\" denetiminin eşiği yeni tohumlarla doğrulanmalı.",
    }
    y = {"hukum": hukum, "rozet": rozet, "os": once_simdi, "olculen": olculen, "ana": ana, "grafik": grafik,
         "oneri": oneri, "iyimser": iyimser, "aciklar": aciklar}
    return r, y, ust


SR_AB = [("temiz", "Kusursuz kurulum"), ("konum5", "Etiket yeri ±5 cm"), ("konum20", "Etiket yeri ±20 cm"),
         ("aci5", "Etiket açısı ±5°"), ("odak2", "Odak hatası %2"), ("egim2", "Kamera montaj eğimi ±2°"),
         ("gecikme200", "Algılama gecikmesi 200 ms"), ("dusme50", "Kare düşmesi %50"),
         ("ortulme50", "Zamanın %50'sinde örtülme"), ("parlama_agir", "Zamanın %50'sinde sert parlama"),
         ("bulanik_agir", "33 ms pozlama + titreşim"), ("yirtik_hafif", "Etiketlerin 1/3'ünde köşe %15 yırtık"),
         ("yirtik_agir", "Bütün etiketlerde köşe %25 yırtık"), ("hafif", "Birleşik kurulum, hafif"),
         ("orta", "Birleşik kurulum, orta"), ("agir", "Birleşik kurulum, ağır")]
SR_ROTA = [("temiz", "Kusursuz", "-"), ("kayip1_rota", "1 etiket eksik", "rotada ölçülenlerden"),
           ("kayip1_kritik", "1 etiket eksik", "en çok ölçülen"),
           ("yanlis025_rota", "1 etiket 0,25 m kaymış", "rotada ölçülenlerden"),
           ("yanlis05_rota", "1 etiket 0,5 m kaymış", "rotada ölçülenlerden"),
           ("yanlis1_rota", "1 etiket 1 m kaymış", "rotada ölçülenlerden"),
           ("yanlis1_kritik", "1 etiket 1 m kaymış", "en çok ölçülen")]
SR_KY = [("temiz", "tek", "Kusursuz, tek etiketle başlatma"), ("temiz", "dogrulamali", "Kusursuz, doğrulamalı başlatma"),
         ("hafif", "tek", "Hafif kurulum, tek"), ("orta", "tek", "Orta kurulum, tek"),
         ("orta", "dogrulamali", "Orta kurulum, doğrulamalı"), ("agir", "tek", "Ağır kurulum, tek")]


def sanalray_yeni(es):
    AB, KY, RO = oku(S / "dayaniklilik_ab.csv"), oku(S / "dayaniklilik_kayip.csv"), oku(S / "dayaniklilik_rota_ab.csv")
    r = {}

    def bas(rs):
        return sum(dogru(x["basari"]) for x in rs)

    def temas(rs):
        return sum(int(say(x["temas_olay"]) or 0) for x in rs), sum(say(x["temas_sure_s"]) or 0 for x in rs)

    sat, gr = [], []
    r["ab"] = {}
    for kos, ad in SR_AB:
        rs = [x for x in AB if x["kosul"] == kos]
        b, (to, ts) = bas(rs), temas(rs)
        va = [say(x["varis_hatasi_m"]) for x in rs]
        r["ab"][kos] = (b, len(rs), ort(va))
        sat.append([ad, kesir(b, len(rs), len(rs)), f"{sy(ort(va), 3)} / {sy(max(va), 3)}",
                    sy(max(say(x["yanal_en_arinmis_m"]) for x in rs), 3),
                    f"<span class='{'kotu' if to else ''}'>{to}</span>" + (f" <span class='ince'>({sy(ts)} s)</span>" if to else "")])
        gr.append((ad, [b / len(rs)], [f"{b}/{len(rs)}"]))
    ana = tablo(["A'dan B'ye, kusur (en ağır düzey)", "Başarı", "Varış hatası ort / en (m)",
                 "Yanal sapma, ilk 2 m sonrası en (m)", "Duvar teması"], sat,
                not_="4 sınama koridoru × orta hedef × tohum 1–3 = 12 koşu, kafa sabit. Tek etkenlerde yalnız en ağır düzey "
                     "koşuldu; hepsi 12/12 çıktığı için ara düzeyler geçer varsayıldı (ölçülmedi).")
    # eksik / yanlış yer: robotun gördüğü etiketlerden
    temiz_ab = {(x["koridor"], x["tohum"]): x for x in AB if x["kosul"] == "temiz"}
    alanlar = ("varis_hatasi_m", "etiket_olcum", "etiket_ret", "sure_s", "en_yanal_sapma_m")
    r["etkisiz"] = {}
    for kos in ("kayip1", "yanlis1", "yirtik_hafif"):
        rs = [x for x in AB if x["kosul"] == kos]
        ez = [x for x in rs if all(x[a_] == temiz_ab[(x["koridor"], x["tohum"])][a_] for a_ in alanlar)]
        et = [x for x in rs if x not in ez]
        r["etkisiz"][kos] = (len(ez), bas(et), len(et), bas(rs), len(rs))
    rsat = []
    r["rota"] = {}
    for kos, ad, sec in SR_ROTA:
        rs = [x for x in RO if x["kosul"] == kos]
        r13 = [x for x in rs if int(x["tohum"]) <= 3]
        b, (to, ts) = bas(rs), temas(rs)
        va = [say(x["varis_hatasi_m"]) for x in rs]
        r["rota"][kos] = (b, len(rs), to, ts)
        rsat.append([ad, sec, kesir(bas(r13), len(r13), len(r13)), kesir(b, len(rs), len(rs)),
                     f"{sy(ort(va), 3)} / {sy(max(va), 3)}", sy(max(say(x["en_yanal_sapma_m"]) for x in rs), 3),
                     sy(max(say(x["konum_hata_en_m"]) for x in rs), 3),
                     f"<span class='{'kotu' if to else ''}'>{to}</span>" + (f" <span class='ince'>({sy(ts)} s)</span>" if to else "")])
        if kos != "temiz":
            gr.append((f"{ad}, {sec}", [b / len(rs)], [f"{b}/{len(rs)}"]))
    for kos, ad in (("kayip1", "1 etiket eksik"), ("yanlis1", "1 etiket 1 m kaymış")):
        ez, be, ne, b, n = r["etkisiz"][kos]
        rsat.append([f"{ad} (bu turun ilk ölçümü)", "bütün plandan", f"{b}/{n} <span class='ince'>(etkili {be}/{ne})</span>",
                     "-", "-", "-", "-", "0"])
    ana += "<h4>Eksik ve yanlış yerdeki etiket, robotun rotada ölçtüğü etiketlerden seçilince (onarım)</h4>" + tablo(
        ["Kusur", "Etiket seçimi", "Tohum 1–3", "Tohum 1–6", "Varış hatası ort / en (m)", "Yanal sapma en (m)",
         "Konum hatası en (m)", "Duvar teması"], rsat,
        not_="Aday etiket: aynı koridor, hedef ve tohumun kusursuz koşusunda süzgecin en az bir ölçümünü kabul ettiği "
             f"etiket; aday listesi hakem tarafında, robot görmüyor. İlk ölçümde 12 koşunun "
             f"{r['etkisiz']['kayip1'][0]}'sında etiket robotun görmediği yerdeydi ve sonuç temiz koşuyla birebir aynıydı; "
             + (lambda n_, a_: f"yeni {n_} koşunun hiçbiri temiz koşuyla aynı değil. " if a_ == 0
                else f"yeni {n_} koşunun {a_} tanesi temiz koşuyla aynı. ")(
                 len([x for x in RO if x['kosul'] != 'temiz']),
                 sum(1 for x in RO if x['temizle_ayni'] and dogru(x['temizle_ayni'])))
             + "0,25 m düzeyi, "
             "0,5 m'nin de kırdığı görüldükten sonra eklendi; ayar yapılmadı.")
    # rastgele bırakılma
    ksat = []
    r["ky"] = {}
    for kos, bs, ad in SR_KY:
        rs = [x for x in KY if x["kume"] == "sinama" and x["kosul"] == kos and x["baslatma"] == bs]
        b, (to, ts) = bas(rs), temas(rs)
        bh = [say(x["baslatma_hata_m"]) for x in rs if say(x["baslatma_hata_m"]) is not None]
        lk = [say(x["lokalize_s"]) for x in rs if say(x["lokalize_s"]) is not None]
        r["ky"][(kos, bs)] = (b, len(rs), bh, ort(lk), to, ts)
        ksat.append([ad, kesir(b, len(rs), len(rs)),
                     (f"{sy(ort(bh), 3)} / {sy(max(bh), 3)} <span class='ince'>({len(bh)} koşu)</span>" if bh else "-"),
                     sy(ort(lk)) if lk else "-", sy(ort([say(x["sure_s"]) for x in rs])),
                     f"<span class='{'kotu' if to else ''}'>{to}</span>" + (f" <span class='ince'>({tam(ts)} s)</span>" if to else "")])
    ana += "<h4>Rastgele bırakılma (sınama koridorları, kafa sabit)</h4>" + tablo(
        ["Kurulum ve başlatma", "Başarı", "Başlatma hatası ort / en (m), konumlanan", "Konumlanma ort (s)",
         "Toplam süre ort (s)", "Duvar teması (süre)"], ksat,
        not_="Kusursuz satırlar ayrı bırakma noktalarında (10–13; 16 koşu), kusurlu kurulumlar ilk turun bırakma "
             "noktalarında (12 koşu). Başlatma hatası yalnız konumlanan koşulardan; doğrulamalıda daha az koşu konumlandı.")
    # bedel: eşli başarılı kusursuz koşular
    tk = {(x["koridor"], x["birak"]): x for x in KY if x["kume"] == "sinama" and x["kosul"] == "temiz" and x["baslatma"] == "tek"}
    dk = {(x["koridor"], x["birak"]): x for x in KY if x["kume"] == "sinama" and x["kosul"] == "temiz" and x["baslatma"] == "dogrulamali"}
    cift = [k_ for k_ in tk if k_ in dk and dogru(tk[k_]["basari"]) and dogru(dk[k_]["basari"])]
    r["bedel"] = (ort([say(dk[k_]["lokalize_s"]) - say(tk[k_]["lokalize_s"]) for k_ in cift]),
                  ort([say(dk[k_]["sure_s"]) - say(tk[k_]["sure_s"]) for k_ in cift]), len(cift))
    yan = [x for x in RO if x["kosul"] == "yanlis1_rota" and not dogru(x["basari"])]
    r["yan_sure"] = [x for x in yan if x["bitis"] == "sure"]
    r["yan_bitti"] = [say(x["varis_hatasi_m"]) for x in yan if x["bitis"] == "beyin"]
    adaylar = {}
    for x in RO:
        if x["aday"]:
            adaylar[x["koridor"]] = (len(json.loads(x["aday"])), int(x["etiket_sayisi"]))
    r["adaylar"] = adaylar
    pay_ = {s_: ort([say(x["secilen_temiz_kabul"]) / say(x["temiz_kabul_toplam"]) for x in RO if x["secim"] == s_])
            for s_ in ("rota", "kritik")}
    ik = es["kayip"]
    grafik = cubuk_grafik("A'dan B'ye başarı oranı, kusur başına", [("başarı oranı", "--c-a")], gr, en_buyuk=1,
                          esik=0.9, esik_etiket="%90 çizgisi",
                          aciklama="Tek etkenler 12 koşu, eksik ve yanlış yer etiketi 24 koşu (tohum 1–6).")
    b022 = bel(S, "Sanal ray", "0,22 m ve 6,0°", ["0,22 m", "yön 6,0°"],
               "ilk turun başarısız rastgele bırakılma koşusu yeniden üretildi; başlatma hatası 0,22 m, yön 6,0°")
    b34 = bel(S, "Sanal ray", "34. saniyede", ["34 s'de", "etiket 152"],
              "yanlış yer mekanizması: bir koşuda 34. saniyede süzgeç kaymış etiketin kendisinden yeniden kuruldu")
    rk = r["rota"]
    kyo, kyd = r["ky"][("orta", "tek")], r["ky"][("orta", "dogrulamali")]
    kyt, kytd = r["ky"][("temiz", "tek")], r["ky"][("temiz", "dogrulamali")]
    hukum = (f"Bilinen başlangıçtan A'dan B'ye sürüş kurulum hatalarının çoğuna dayanıklı: köşe yırtığı dışındaki "
             f"tek etkenlerin en ağır düzeyinde 12/12. Kıranlar: bütün etiketlerde köşe yırtığı ({r['ab']['yirtik_agir'][0]}/12) ve yanlış yere "
             f"asılmış tek etiket: 1 m'de {rk['yanlis1_rota'][0]}/24 ve {rk['yanlis1_rota'][2]} koşuda duvar teması, "
             f"0,5 m'de {rk['yanlis05_rota'][0]}/24, 0,25 m'de {rk['yanlis025_rota'][0]}/24. Eksik tek etiket bozmuyor "
             f"({rk['kayip1_rota'][0]}/24). Rastgele bırakılma kırılgan: orta kurulumda {kyo[0]}/{kyo[1]}.")
    once_simdi = [
        ("Asıl risk",
         "Etiketin örtülmesi ve parlama.",
         f"Zamanın %50'sinde örtülme ya da sert parlama A'dan B'yi bozmadı ({r['ab']['ortulme50'][0]}/12, "
         f"{r['ab']['parlama_agir'][0]}/12). Kıranlar köşe yırtığı ve yanlış yere asılmış etiket."),
        ("Eksik / yanlış yer etiketi",
         f"Bu turun ilk ölçümü eksik etikette {r['etkisiz']['kayip1'][3]}/12, yanlış yerde {r['etkisiz']['yanlis1'][3]}/12 "
         f"dedi; ama 12 koşunun {r['etkisiz']['kayip1'][0]}'sında etiket robotun görmediği yerdeydi (etkili koşularda "
         f"{r['etkisiz']['kayip1'][1]}/{r['etkisiz']['kayip1'][2]} ve {r['etkisiz']['yanlis1'][1]}/"
         f"{r['etkisiz']['yanlis1'][2]}).",
         f"Etiket robotun ölçtüklerinden seçilince eksik {rk['kayip1_rota'][0]}/24; yanlış yer 0,25 / 0,5 / 1 m'de "
         f"{rk['yanlis025_rota'][0]} / {rk['yanlis05_rota'][0]} / {rk['yanlis1_rota'][0]} (24'te), 1 m'de "
         f"{rk['yanlis1_rota'][2]} duvar teması (toplam {tam(rk['yanlis1_rota'][3])} s)."),
        ("Rastgele bırakılmadaki başarısızlık",
         "Tek etiketten yanlış başlatma sanıldı: \"tek etiketten başlatmaya güvenilmemeli\".",
         f"Kusursuz dünyada asıl kusur takılmanın sezilmemesi: ilk dönüşten sonra eğik sürüş, eğik duvardan sonar yankısı "
         f"yok. İlk turun başarısız koşusunda başlatma hatası yalnız {b022}. Orta kusurlu kurulumda ise tek etiket "
         f"başlatması gerçekten yanlış: {' ve '.join(sy(v, 2) + ' m' for v in sorted(v for v in kyo[2] if v > 0.5))}."),
        ("İlk etiket süresi",
         f"Tablo konumlanma süresini ({sy(ik['sabit'][3])} / {sy(ik['tarayan'][3])} s) \"ilk etiket\" diye "
         "basıyordu (inceleme düzeltti).",
         f"İlk etiketin görülmesi ortalama {sy(ik['sabit'][2])} s (sabit kafa) / {sy(ik['tarayan'][2])} s (tarayan "
         f"kafa); konumlanma {sy(ik['sabit'][3])} / {sy(ik['tarayan'][3])} s."),
        ("Doğrulamalı başlatma", "Yoktu.",
         f"Kusursuz dünyada {kytd[0]}/{kytd[1]} (tek {kyt[0]}/{kyt[1]}); orta kurulumda {kyd[0]}/{kyd[1]} (tek "
         f"{kyo[0]}/{kyo[1]}), ama konumlanma {sy(kyo[3])} s'den {sy(kyd[3])} s'ye uzadı, temas olayı {kyo[4]}'ten "
         f"{kyd[4]}'ye çıktı. Varsayılan değişmedi."),
    ]
    rozet = rz("İnceleme: koşullu (tek etiketlik etkenlerin yarısı etkisiz)") + rz("Onarımdan sonra: bulgu kapandı", "iyi")
    olculen = (f"<p>Kusurlu dünyada dayanıklılık: harita ve etiket kurulum hataları, kamera hataları, görüntü bozulmaları "
               f"ve birleşik kurulum; A'dan B'ye {len(AB)} koşu, rastgele bırakılmada {len(KY)} koşu. İnceleme eksik ve "
               "yanlış yer etiketinin yarı yarıya etkisiz seçildiğini buldu; onarımda etiket robotun gördüklerinden "
               f"seçildi ve {len(RO)} koşu (tohum 1–6) koşuldu. Ayrıca isteğe bağlı doğrulamalı başlatma denendi; "
               "tasarımı geliştirme koridorlarında iki kez değişti, sınamadan önce donduruldu.</p>")
    oneri = [
        f"<strong>Yanlış yerin mekanizması:</strong> kaymış etiket önce reddediliyor; arka arkaya 6 retten sonra yeniden "
        f"başlatma süzgeci yakındaki etiketten kuruyor ve bu kaymış etiketin kendisi olabiliyor (bir koşuda {b34}). "
        f"1 m'deki başarısızlıkların {len(r['yan_sure'])}'si süre doldurdu ve duvara dayandı, "
        f"{len(r['yan_bitti'])}'sinde robot hedefin {sy(min(r['yan_bitti']), 2)}–{sy(max(r['yan_bitti']), 2)} m uzağında "
        "\"bitti\" dedi. Öneri (uygulanmadı): yeniden başlatma tek etiketi başka bir etiketle ya da sonarla çapraz "
        "denetlemeden kabul etmesin.",
        "<strong>Kırılma noktası:</strong> yanlış yer 0,25 m ile 0,5 m arasında kırıyor; köşe yırtığı etiketlerin "
        "1/3'ünde %15 ile hepsinde %25 arasında.",
        f"<strong>Eksik etiketin bedeli:</strong> başarı ve temas değişmiyor, ama koridorun başındaki etiket kalkınca "
        f"yanal sapma {sy(max(say(x['en_yanal_sapma_m']) for x in RO if x['kosul'].startswith('kayip1')), 2)} m'ye çıkıyor.",
        f"<strong>Doğrulamalı başlatmanın bedeli:</strong> kusursuz dünyada {r['bedel'][2]} eşli başarılı koşuda konumlanma "
        f"+{sy(r['bedel'][0])} s, toplam süre +{sy(r['bedel'][1])} s. Takılmayı enkoder ancak duvara değdikten sonra "
        "seziyor; robot daha çok değiyor ama daha kısa dayanıyor.",
        "<strong>Gerçek koridorda:</strong> etiket yeri ±5 cm ile ölçülsün; kurulumdan sonra robotla bir tur \"etiket ve "
        "harita aynı mı\" denetimi zorunlu; sert levha ya da laminasyon, yıpranan etiket yenilensin; robot bilinen bir "
        "noktadan başlatılsın.",
    ]
    iyimser = [
        "Gecikme sabit, kare düşmesi bağımsız; örtü düz gri, parlama tek leke; ışık düzgün.",
        "Mercek bozulması, yuvarlanan deklanşör ve gövde eğimi yok; sonar ideal (ama eğik yüzeyden yankısız).",
        "Tek etkenlerde ara düzeyler geçer varsayıldı (ölçülmedi).",
    ]
    aciklar = [
        "Rastgele bırakılmada ve tarayan kafada eksik ya da yanlış yerdeki etiket koşulmadı.",
        "Yanlış yerin kırılma noktası 0,25–0,5 m arasında; ara düzey ölçülmedi.",
        "Birleşik ağır kurulumda eksik ve yanlış yer etiketi hâlâ bütün plandan seçiliyor (yırtık belirlediği için "
        "yeniden koşulmadı).",
        "Doğrulamalı başlatmanın bileşenleri tek tek ölçülmedi; takılma denetimi ilk sürüme tek başına eklenip sınanmadı.",
        f"Aday etiket sayısı küçük: " + ", ".join(f"{k_.replace('koridor_', 'koridor ')} {a_}/{n_}"
                                                   for k_, (a_, n_) in sorted(adaylar.items()))
        + f"; seçilen etiket temiz koşudaki kabul edilen ölçümlerin ortalama %{tam(100 * pay_['rota'])}'ını taşıyordu.",
    ]
    ust = {
        "hukum": f"Kurulum hatalarının çoğuna dayanıklı (köşe yırtığı dışındaki tek etkenlerde 12/12). Kıranlar köşe yırtığı "
                 f"({r['ab']['yirtik_agir'][0]}/12) ve yanlış yerdeki tek etiket: 1 m'de {rk['yanlis1_rota'][0]}/24 ve "
                 f"{rk['yanlis1_rota'][2]} duvar teması, 0,25 m'de {rk['yanlis025_rota'][0]}/24. Eksik etiket "
                 f"{rk['kayip1_rota'][0]}/24. Rastgele bırakılma orta kurulumda {kyo[0]}/{kyo[1]}.",
        "rozet": rz("İnceleme: koşullu") + rz("Onarım: kapandı", "iyi"),
        "karar": "Kurulumdan sonra robotla etiket–harita denetimi zorunlu (±25 cm zararsız, 0,5 m bozuyor); etiket yeri ±5 cm "
                 "ile ölçülsün, etiketler sert levha ya da laminasyonlu olsun ve yıpranınca yenilensin; robot bilinen "
                 "noktadan başlatılsın. Doğrulamalı başlatma varsayılan değil.",
    }
    y = {"hukum": hukum, "rozet": rozet, "os": once_simdi, "olculen": olculen, "ana": ana, "grafik": grafik,
         "oneri": oneri, "iyimser": iyimser, "aciklar": aciklar}
    return r, y, ust


ZK = [("gelistirme", "Geliştirme (önceki sürümün 7 başarısızı)", "deneme_gelistirme.csv", "mujoco_v3.csv"),
      ("sinama2", "Sınama 2 (görülmüş)", "deneme_sinama2.csv", "mujoco_sinama2_v3.csv"),
      ("sinama4", "Sınama 4, v3 beyniyle (önceki tur; zincir için o zaman görülmemiş)", "deneme_sinama4.csv",
       "mujoco_sinama4_v3.csv"),
      ("sinama4_v6", "Sınama 4, v6 beyniyle (bu tur; aynı labirent ve tohumlar)", "deneme_sinama4_v6.csv",
       "mujoco_sinama4_v6.csv")]


def lab_ad(sahne, tohum=None):
    s = sahne.replace("labirent_", "").replace("x", "×").replace("_t", " labirent, no. ")
    return f"{s}, tohum {tohum}" if tohum is not None else s


def deneme_yeni(ed):
    r = {}
    sat, yig = [], []
    for kume, ad, dosya, ilk_dosya in ZK:
        rows = oku(K / dosya)
        zin = {}
        for x in rows:
            zin.setdefault((x["sahne"], x["tohum"]), []).append(x)
        dag = {1: 0, 2: 0, 3: 0, 4: 0, 0: 0}
        top_sure, cozulmeyen, sonra = [], [], []
        for kk, z in zin.items():
            z.sort(key=lambda x: int(x["deneme_no"]))
            cz = [int(x["deneme_no"]) for x in z if x["durum"] == "basari"]
            if cz:
                dag[min(cz)] += 1
                ts = sum(say(x["sure_s"]) for x in z)
                top_sure.append(ts)
                if min(cz) > 1:
                    sonra.append((kk, ts, say(z[min(cz) - 1]["sure_s"]), min(cz)))
            else:
                dag[0] += 1
                cozulmeyen.append(kk)
        ilk = {(x["sahne"], x["tohum"]): x for x in oku(K / ilk_dosya) if (x["sahne"], x["tohum"]) in zin}
        bilgi = {"zincir": len(zin), "dag": dag, "deneme": len(rows), "rows": rows,
                 "carpma": sum(int(say(x["carpma_sayisi"]) or 0) for x in rows),
                 "temas": sum(say(x["carpma_suresi_s"]) or 0 for x in rows),
                 "start": sum(int(say(x["fail_start"]) or 0) for x in rows),
                 "kesme": sum(int(say(x["start_kesme"]) or 0) for x in rows),
                 "sure_med": medyan(top_sure), "cozulmeyen": cozulmeyen, "sonra": sonra,
                 "sure_top": sum(say(x["sure_s"]) for x in rows),
                 "ilk_ayni": (sum(1 for x in rows if x["deneme_no"] == "1" and (x["sahne"], x["tohum"]) in ilk
                                  and ilk[(x["sahne"], x["tohum"])]["durum"] == x["durum"]
                                  and abs(say(ilk[(x["sahne"], x["tohum"])]["sure_s"]) - say(x["sure_s"])) <= 1.0),
                              sum(1 for x in rows if x["deneme_no"] == "1")),
                 "ilk_kpi": sum(1 for x in ilk.values() if x["durum"] == "basari"), "ilk_n": len(ilk)}
        r[kume] = bilgi
        sat.append([ad, str(len(zin)), f"{bilgi['ilk_kpi']}/{bilgi['ilk_n']}", str(dag[1]), str(dag[2]), str(dag[3]),
                    str(dag[4]), f"<span class='{'kotu' if dag[0] else ''}'>{dag[0]}</span>", tam(bilgi["sure_med"]),
                    tam(bilgi["sure_top"]), str(len(rows)), (f"{bilgi['carpma']} <span class='ince'>({sy(bilgi['temas'], 2)} s)</span>"
                                     if bilgi["carpma"] else "0"), str(bilgi["start"] + bilgi["kesme"])])
        yig.append((ad, [dag[1], dag[2], dag[3], dag[4], dag[0]], len(zin)))
    s4 = r["sinama4"]
    ana = tablo(["Küme", "Zincir", "İlk giriş (ön bilgisiz)", "1. denemede", "2.", "3.", "4.", "Çözülmedi",
                 "Süre ortanca, çözülen (s)", "Süre toplamı (s)", "Deneme", "Çarpma", "Başlangıçtan çıkma / kesme"],
                sat,
                not_="Hafızalı sınıf: 2. ve sonraki denemelerde robot önceki denemelerin haritasını bilir. İlk giriş "
                     "sütunu aynı kümenin aynı beyinle ön bilgisiz koşuları; ayrı bir ölçü. Her deneme en çok 900 s, en "
                     "çok 4 deneme. Zincir mantığına dokunulmadı, ayar yapılmadı. v6 zinciri dondurulmuş v6 kodunun ayrı "
                     "bir kopyasından koşuldu; tek fark, denemeler arasında v6'nın geçmiş taramalarının sıfırlanması.")
    s6 = r["sinama4_v6"]
    dsat = []
    for beyin, bilgi_ in (("v3", s4), ("v6", s6)):
        rows_ = bilgi_["rows"]
        for no in sorted({int(x["deneme_no"]) for x in rows_}):
            q = [x for x in rows_ if int(x["deneme_no"]) == no]
            pz = [say(x["poz_hata_maks_m"]) for x in q]
            c = sum(int(say(x["carpma_sayisi"]) or 0) for x in q)
            dsat.append([beyin, str(no), str(len(q)), str(sum(x["durum"] == "basari" for x in q)),
                         tam(ort([say(x["sure_s"]) for x in q])),
                         f"<span class='{'kotu' if c else ''}'>{c}</span>", f"{sy(ort(pz), 2)} / {sy(max(pz), 2)}"])
    rows = s4["rows"]
    ana += "<h4>Sınama 4, deneme başına (v3 ve v6 zinciri)</h4>" + tablo(
        ["Beyin", "Deneme", "Koşu", "Çözülen", "Süre ort (s)", "Çarpma", "Poz hatası en büyük: ort / en (m)"], dsat)
    tani6 = oku(K / "tani_zincir_sinama4_v6.csv")
    r["kopuk6"] = (sum(1 for x in tani6 if x["start_bagli_025"] == "0"), len(tani6))
    s6_coz = 20 - s6["dag"][0]
    s4_coz = 20 - s4["dag"][0]
    # zincir kuralı: v6 zinciri v3'ten az çözüyorsa ya da daha çok temas yapıyorsa zincirin varsayılanı açıkça v3 olur
    r["zincir_kural"] = s6_coz >= s4_coz and s6["carpma"] <= s4["carpma"] and s6["zincir"] == s4["zincir"]
    tani = oku(K / "tani_zincir_sinama4.csv")
    kopuk = [x for x in tani if x["start_bagli_025"] == "0"]
    r["kopuk"] = (len(kopuk), len(tani))
    ilk_bas = [x for x in tani if x["deneme_no"] == "1" and x["durum"] != "basari"]
    tempo = bel(K, "Haritayla yeniden deneme", "4,23 / 4,75 s/m", ["3.86 / 4.23 / 4.75 s/m"],
                "bilinen haritada ölçülen tempo 4,23 / 4,75 s/m (ortanca / en kötü)")
    cz = [say(x["cozum_m"]) for x in ilk_bas]
    yc = [say(x["yol_cozum"]) for x in ilk_bas]
    r["ilk_bas"] = (len(ilk_bas), min(cz), max(cz), min(yc), max(yc), max(cz) * 4.75)
    ck = s4["cozulmeyen"][0] if s4["cozulmeyen"] else None
    ckr = sorted([x for x in rows if (x["sahne"], x["tohum"]) == ck], key=lambda x: int(x["deneme_no"])) if ck else []
    ck_coz = say(ckr[0]["cozum_m"]) if ckr else None
    r["ck"] = (ck, ckr)
    temas_t = [x for x in oku(K / "tani_temas_v6.csv") if "deneme_sinama4" in x["kayit"]]
    tt = temas_t[0] if temas_t else None
    sonra = s4["sonra"]
    grafik = yigin_grafik("Labirentin kaçıncı denemede çözüldüğü",
                          [("1. deneme", "--c-c"), ("2. deneme", "--c-a"), ("3. deneme", "--c-a2"),
                           ("4. deneme", "--c-a3"), ("çözülmedi", "--c-b")], yig,
                          aciklama="Geliştirme kümesi yalnız ilk girişte çözülemeyen labirentlerden oluşuyor; bu yüzden "
                                   "orada 1. denemede çözülen yok.")
    s2 = r["sinama2"]
    ck_txt = (f"{lab_ad(ck[0], ck[1])}: 1. deneme süre doldu; sonraki "
              f"{sum(1 for x in ckr if x['durum'] == 'fail_sikisma')} deneme {sy(say(ckr[1]['sure_s']), 0)} s'de "
              "\"sınır kalmadı\" ile sıkışıp bitti") if ck and len(ckr) > 1 else "yok"
    hukum = (f"Sınama 4'te zincir v6 beyniyle {s6_coz}/20 çözdü (1. denemede {s6['dag'][1]}, 2. denemede {s6['dag'][2]}), "
             f"temas {s6['carpma']}; v3 beyniyle {s4_coz}/20 çözmüştü, temas {s4['carpma']}. Bütün denemelerin toplam "
             f"süresi v6'da {tam(s6['sure_top'])} s, v3'te {tam(s4['sure_top'])} s; başlangıçtan çıkma ve kesme v6'da "
             f"{s6['start'] + s6['kesme']}, v3'te {s4['start'] + s4['kesme']}. Önceden yazılan zincir kuralı "
             f"{'sağlandı: zincir de varsayılan v6 ile koşar' if r['zincir_kural'] else 'sağlanmadı: zincirin varsayılanı v3 olmalı'}. "
             "Bu hafızalı sınıf, ilk giriş ölçüsü değil; sınama 4 zincir için artık görülmüş sayılır.")
    once_simdi = [
        ("Zincir beyni",
         f"Zincir yalnız v3 ile koşulmuştu: sınama 4'te {s4_coz}/20, 1 zincir harita kaymasıyla çözülmedi.",
         f"v6 ile de koşuldu: {s6_coz}/20, çözülmeyen yok, temas {s6['carpma']}. v6'nın 1. denemeleri aynı kümenin v6 "
         f"ilk giriş koşularıyla {s6['ilk_ayni'][0]}/{s6['ilk_ayni'][1]} aynı sonuç (süre farkı en çok 1 s). Deneme "
         f"sonu haritalarından {r['kopuk6'][0]} / {r['kopuk6'][1]} tanesinde başlangıç sınırlardan kopuktu (v3'te "
         f"{r['kopuk'][0]} / {r['kopuk'][1]})."),
        ("Kazanç",
         f"Görülmüş sınama 2'de {s2['dag'][1]}/20'den {20 - s2['dag'][0]}/20'ye: \"kazanç küçük, tek labirent\".",
         f"v3 zinciriyle o zaman görülmemiş sınama 4'te {s4['ilk_kpi']}/20'den {20 - s4['dag'][0]}/20'ye; sonradan çözülen "
         f"{len(sonra)} zincirin toplam süresi {tam(min(x[1] for x in sonra))}–{tam(max(x[1] for x in sonra))} s."),
        ("Çözülmeyenin nedeni",
         "Yeni denemede sınır seçme sırası ve en uzun çözüm yolunun 900 s'ye ancak sığması.",
         f"v3 zincirinde harita kayması: {ck_txt}. v6 zincirinde çözülmeyen yok. Bu labirent tam haritayla {tam(ck_coz * 4.23)} / {tam(ck_coz * 4.75)} s'de "
         f"çözülebilirdi (tempo {tempo}). Sınır sırası sorunu sınama 4'te de görüldü ama koşu kaybettirmedi."),
        ("Güvenlik",
         f"Sınama 2'de {s2['carpma']} çarpma ({sy(s2['temas'], 2)} s), başlangıçtan çıkma {s2['start']}.",
         f"Sınama 4'te {s4['carpma']} çarpma ({sy(s4['temas'], 2)} s): yerinde dönüşten "
         f"{sy(say(tt['son_yerinde_s']))} s sonra yayla duvar ucuna sürtünme, o an poz hatası "
         f"{sy(say(tt['poz_hata_m']), 3)} m (harita kayması değil). Başlangıçtan çıkma {s4['start']}. v6 zincirinde "
         f"{s6['deneme']} denemede çarpma {s6['carpma']}, başlangıçtan çıkma {s6['start']}."
         if tt else f"Sınama 4'te {s4['carpma']} çarpma."),
    ]
    rozet = rz("İnceleme: geçer", "iyi") + rz("Engelleyici yok; bir belge sayısı düzeltildi", "iyi")
    olculen = ("<p>Deneme zinciri (başarısız denemenin haritası sonrakine taşınır) önce v3 beyniyle hiç görülmemiş sınama "
               "4 kümesinde, zincir mantığına ve beyne dokunulmadan, ayrı bir kod kopyasından koşuldu. Bu turun ikinci "
               "adımında aynı küme ve tohumlarla v6 beyniyle yinelendi (dondurulmuş v6 kodunun kopyası, en çok 4 deneme). "
               "Kural koşudan önce yazıldı: v6 zinciri v3'ten az zincir çözerse ya da daha çok temas yaparsa zincirin "
               "varsayılan beyni açıkça v3 olacaktı. Birinci denemeler ilk giriş koşularıyla karşılaştırıldı; "
               "çözülmeyen zincirler kayıtlardan tanılandı (yer gerçeği yalnız tanıda).</p>")
    oneri = [
        f"<strong>Sonradan çözülen zincirler</strong> (hepsi 17×17): v3'te {len(sonra)}, çözen deneme "
        f"{tam(min(x[2] for x in sonra))}–{tam(max(x[2] for x in sonra))} s; v6'da {len(s6['sonra'])}, çözen deneme "
        f"{tam(min(x[2] for x in s6['sonra']))}–{tam(max(x[2] for x in s6['sonra']))} s, en geç {max(x[3] for x in s6['sonra'])}. denemede.",
        f"<strong>İlk girişteki {r['ilk_bas'][0]} başarısızlığın hepsi keşif kaynaklı:</strong> çözüm yolu "
        f"{tam(r['ilk_bas'][1])}–{tam(r['ilk_bas'][2])} m, tam haritayla en kötü tempoda ({tempo}) bile en çok "
        f"{tam(r['ilk_bas'][5])} s; yürünen yol / çözüm {sy(r['ilk_bas'][3], 2)}–{sy(r['ilk_bas'][4], 2)}.",
        f"<strong>Hafıza durumu kötüleştirebilir:</strong> v3 zincirinde deneme sonu haritalarından {r['kopuk'][0]} / {r['kopuk'][1]} tanesinde başlangıç "
        "sınırlara bağlı değildi ve sonraki denemelerin hiçbiri ilerleyemedi. Öneri (ölçülmedi): yeni denemede "
        "başlangıçtan hiçbir sınıra yol yoksa boş haritayla başlamak; yeni bir geliştirme kümesinde denenmeli.",
        "<strong>Düzeltme:</strong> görülmüş sınama 2'deki \"104 / 80 / 131 m\" iddiası kayıtlardan 108 / 80 / 135 m "
        "çıktı (testin açıklama belgesinde düzeltildi).",
    ]
    iyimser = [
        "Robot her denemede başlangıca yalnız 3 cm / 2° hatayla konuyor.",
        "Denemeler arasında haritayı saklamak kural gereği serbest varsayıldı.",
        "Bağlantı denetimi yaklaşık: 5 cm eşikli harita ve 0,25 m şişirme; planlayıcının kaba ızgarası birebir değil.",
    ]
    aciklar = [
        "Boş haritayla yeniden başlama önerisi ölçülmedi; sınama 4 artık zincir için de görülmüş sayılır, sonraki "
        "kararlar için hiç görülmemiş bir küme gerekiyor.",
        "Farklar küçük (v6 ile v3 arasında tek zincir); istatistik olarak anlamlı değil.",
        "Hizalama sondası sınama 4'te süre yüzünden koşulmadı.",
        "Önde engel beklemesi döngüsü ve dönüşten hemen sonra yayla sürtünme incelenmedi.",
    ]
    ust = {
        "hukum": f"Sınama 4'te zincir v6 beyniyle {s6_coz}/20 (temas {s6['carpma']}), v3 beyniyle {s4_coz}/20 (temas "
                 f"{s4['carpma']}); ilk girişte {s6['ilk_kpi']}/20. Bütün denemelerin süresi v6'da {tam(s6['sure_top'])} s, "
                 f"v3'te {tam(s4['sure_top'])} s. Zincir kuralı "
                 f"{'sağlandı' if r['zincir_kural'] else 'sağlanmadı'} (hafızalı sınıf).",
        "rozet": rz("İnceleme: geçer", "iyi"),
        "karar": f"Kural ikinci denemeye izin veriyorsa haritayı saklamak değer: sınama 4'te ilk girişte {s6['ilk_kpi']}/20, "
                 f"zincirle {s6_coz}/20. Zincir de varsayılan v6 beyniyle koşar"
                 f"{'' if r['zincir_kural'] else ' (KURAL SAĞLANMADI: v3 olmalı)'}. Yeni denemede başlangıçtan sınıra "
                 "yol yoksa boş haritayla başlamak önerildi (ölçülmedi).",
    }
    y = {"hukum": hukum, "rozet": rozet, "os": once_simdi, "olculen": olculen, "ana": ana, "grafik": grafik,
         "oneri": oneri, "iyimser": iyimser, "aciklar": aciklar}
    return r, y, ust


KUMELER6 = [
    ("gelistirme", "Geliştirme", {"v3": "mujoco_v3.csv", "v5": "mujoco_v5.csv", "v6": "mujoco_v6.csv"}),
    ("sinama2", "Sınama 2 (görülmüş)", {"v3": "mujoco_sinama2_v3.csv", "v5": "mujoco_sinama2_v5.csv",
                                         "v6": "mujoco_sinama2_v6.csv"}),
    ("sinama4", "Sınama 4 (görülmüş)", {"v3": "mujoco_sinama4_v3.csv", "v5": "mujoco_sinama4_v5.csv",
                                         "v6": "mujoco_sinama4_v6.csv"}),
    ("sinama5", "Sınama 5 (yeni; v6'nın ilk kararı)", {"v3": "mujoco_sinama5_v3.csv", "v6": "mujoco_sinama5_v6.csv"}),
    ("sinama3", "Sınama 3 (bu tur; v3'ün temas yaptığı küme, v6 için tam taze değil)",
     {"v3": "mujoco_sinama3_v3.csv", "v6": "mujoco_sinama3_v6.csv"}),
    ("uzatilmis", "Uzatılmış süre (bu tur; kural dışı 1800 s, tohum 0)",
     {"v3": "mujoco_uzatilmis_v3.csv", "v6": "mujoco_uzatilmis_v6.csv"}),
]
V6_2B = ["v6_2b.csv", "v6_2b_t1.csv"]          # 2B: tohum 0 ve tohum 1


def varsayilan_surum() -> str:
    """Keşif beyninin koddaki varsayılan sürümü (beyin.py'den okunur, belgeden değil)."""
    import re
    metin = (FIZIK / "kesif" / "beyin.py").read_text(encoding="utf-8")
    m = re.findall(r'^VARSAYILAN_SURUM\s*=\s*"(v\d+)"', metin, flags=re.M)
    if len(m) != 1:
        raise SystemExit("kesif/beyin.py: VARSAYILAN_SURUM tek bir atama olarak bulunamadı.")
    return m[0]
V3_ILK = ["mujoco_v3.csv", "mujoco_sinama2_v3.csv", "mujoco_sinama3_v3.csv", "mujoco_sinama4_v3.csv",
          "mujoco_sinama5_v3.csv", "mujoco_uzatilmis_v3.csv"]
V3_ZIN = ["deneme_gelistirme.csv", "deneme_sinama2.csv", "deneme_sinama4.csv"]


def kose_yeni(ek_):
    tani = {}
    for f in sorted(K.glob("hiz_tani_*.csv")):
        for x in oku(f):
            tani.setdefault((x["kume"], x["surum"]), {})[(x["sahne"], x["tohum"])] = x
    r = {"k": {}}
    sat, gsat = [], []
    v6_top = [0, 0, 0.0]
    for kume, ad, dosyalar in KUMELER6:
        veri = {su: {(x["sahne"], x["tohum"]): x for x in oku(K / d)} for su, d in dosyalar.items()}
        for su, rows in veri.items():
            b = sum(1 for x in rows.values() if x["durum"] == "basari")
            c = sum(int(say(x["carpma_sayisi"]) or 0) for x in rows.values())
            ts = sum(say(x["carpma_suresi_s"]) or 0 for x in rows.values())
            kur = sum(int(say(x["kurtarma"]) or 0) for x in rows.values())
            oran = "-"
            o_ = None
            if su != "v3":
                cift = [say(rows[kk]["sure_s"]) / say(veri["v3"][kk]["sure_s"]) for kk in rows
                        if kk in veri["v3"] and rows[kk]["durum"] == "basari" and veri["v3"][kk]["durum"] == "basari"]
                o_ = medyan(cift)
                oran = f"{sy(o_, 3)} <span class='ince'>({len(cift)} çift)</span>"
            td = tani.get((kume, su))
            pmin = mn([say(x["duvar_pay_min_m"]) for x in td.values()]) if td else None
            p5 = sum(1 for x in td.values() if say(x["duvar_pay_min_m"]) is not None
                     and say(x["duvar_pay_min_m"]) < 0.005) if td else None
            r["k"][(kume, su)] = (b, len(rows), c, ts, o_, pmin, p5, kur)
            if su == "v6":
                v6_top[0] += len(rows)
                v6_top[1] += c
                v6_top[2] += ts
            sat.append([ad, su, f"{b}/{len(rows)}",
                        f"<span class='{'kotu' if c else 'iyi'}'>{c}</span>" + (f" <span class='ince'>({sy(ts, 2)} s)</span>" if c else ""),
                        oran, ((f"{tam(pmin * 1000)} mm" if round(pmin * 1000) > 0 else "≤ 0 mm")
                               if pmin is not None else "-"),
                        (f"{p5}/{len(rows)}" if p5 is not None else "-"), str(kur)])
        gsat.append((ad, [r["k"][(kume, su)][0] / r["k"][(kume, su)][1] if (kume, su) in r["k"] else None
                          for su in ("v3", "v5", "v6")],
                     [f"{r['k'][(kume, su)][0]}/{r['k'][(kume, su)][1]}" + (
                         f" · <span class='kotu'>{r['k'][(kume, su)][2]} çarpma</span>" if r['k'][(kume, su)][2] else "")
                      if (kume, su) in r["k"] else "koşulmadı" for su in ("v3", "v5", "v6")]))
    r["v6_top"] = v6_top
    ana = tablo(["Küme", "Sürüm", "Çözülen", "Çarpma (temas)", "Süre oranı / v3 (ortanca, ikisi de çözdüyse)",
                 "En küçük duvar payı", "Duvara 5 mm'den yaklaşan koşu", "Kurtarma"], sat,
                not_="MuJoCo, 900 s (uzatılmış kümede 1800 s), robot labirent hakkında önceden bilgisiz. v6 kodu "
                     "dondurulduktan sonra koşuldu, ayar yapılmadı. v6 = v5 + tüm gövde süpürme öngörüsü: son tarama, son 2 s'nin taramaları ve çevredeki "
                     "harita hücreleri; kabul edilen yay yoksa geri çekilip yeniden plan. Duvar payı tanı aracının gövde "
                     "çizimiyle hesaplanıyor, temas sayımı simülatörün temas kaydından; ikisi 1–2 mm farklı olabilir.")
    # v3 tabanı
    vsat = []
    v3 = {"ilk": [0, 0, 0.0], "zin": [0, 0, 0.0]}
    for grup_, dosyalar, ad in (("ilk", V3_ILK, "ilk giriş"), ("zin", V3_ZIN, "hafızalı zincir")):
        for d in dosyalar:
            rows = [x for x in oku(K / d) if x.get("surum", "v3") in ("v3", "")]
            c = sum(int(say(x["carpma_sayisi"]) or 0) for x in rows)
            ts = sum(say(x["carpma_suresi_s"]) or 0 for x in rows)
            v3[grup_][0] += len(rows)
            v3[grup_][1] += c
            v3[grup_][2] += ts
            vsat.append([ad, d.replace(".csv", "").replace("mujoco_", "").replace("deneme_", "zincir, ")
                         .replace("_v3", "").replace("v3", "geliştirme").replace("sinama", "sınama ")
                         .replace("uzatilmis", "uzatılmış süre").replace("gelistirme", "geliştirme"),
                         str(len(rows)), f"<span class='{'kotu' if c else ''}'>{c}</span>", sy(ts, 2)])
    r["v3"] = v3
    vsat.append(["<strong>Toplam</strong>", "", str(v3["ilk"][0] + v3["zin"][0]),
                 f"<strong>{v3['ilk'][1] + v3['zin'][1]}</strong>", f"<strong>{sy(v3['ilk'][2] + v3['zin'][2], 2)}</strong>"])
    ana += "<h4>v3'ün temas tabanı (v3 de sıfır değil)</h4>" + tablo(
        ["Sınıf", "Küme", "Koşu / deneme", "Temas olayı", "Temas (s)"], vsat)
    d2 = [x for d in V6_2B for x in oku(K / d)]
    r["2b"] = {}
    bsat = []
    for su in ("v5", "v6"):
        for tohum in sorted({x["tohum"] for x in d2}) + [None]:
            rs = [x for x in d2 if x["ayar"] == su and (tohum is None or x["tohum"] == tohum)]
            c = sum(int(say(x["carpma_sayisi"]) or 0) for x in rs)
            ts = sum(say(x["carpma_suresi_s"]) or 0 for x in rs)
            b = sum(x["durum"] == "basari" for x in rs)
            tur = sorted({x["durum"] for x in rs if x["durum"] != "basari"})
            if tohum is None:
                r["2b"][su] = (b, len(rs), c, tur, ts)
            bsat.append([f"<strong>{su}</strong>" if tohum is None else su,
                         "toplam" if tohum is None else tohum, f"{b}/{len(rs)}",
                         f"<span class='{'kotu' if c else ''}'>{c}</span>" + (f" <span class='ince'>({sy(ts, 2)} s)</span>"
                                                                            if c else ""),
                         ", ".join({"fail_sure": "süre doldu", "fail_sikisma": "sıkışma"}.get(z, z)
                                   + f" {sum(x['durum'] == z for x in rs)}" for z in tur)])
    ikili = {(x["sahne"], x["tohum"]): x for x in d2 if x["ayar"] == "v5"}
    r["2b_oran"] = (medyan([say(x["sure_s"]) / say(ikili[(x["sahne"], x["tohum"])]["sure_s"]) for x in d2
                            if x["ayar"] == "v6" and x["durum"] == "basari"
                            and ikili.get((x["sahne"], x["tohum"]), {}).get("durum") == "basari"]),
                    sum(1 for x in d2 if x["ayar"] == "v6" and x["durum"] == "basari"
                        and ikili.get((x["sahne"], x["tohum"]), {}).get("durum") == "basari"))
    sik = [x for x in d2 if x["ayar"] == "v6" and x["durum"] == "fail_sikisma"]
    r["2b_sik"] = sik
    ana += "<h4>2B benzetici, 21 geliştirme labirenti, tohum 0 ve 1</h4>" + tablo(
        ["Sürüm", "Tohum", "Çözülen", "Çarpma (temas)", "Başarısızlık türü"], bsat,
        not_=f"v6 / v5 süre oranı, ikisi de çözdüyse: ortanca {sy(r['2b_oran'][0], 3)} ({r['2b_oran'][1]} çift).")
    grafik = cubuk_grafik("Çözülen labirent ve çarpma, küme ve sürüm başına",
                          [("v3", "--c-c"), ("v5", "--c-b"), ("v6 (yeni varsayılan)", "--c-a")], gsat, en_buyuk=1,
                          aciklama="Çubuk boyu çözülen koşu oranı (kümeler 37, 20 ve 9 koşu). Kırmızı yazı o kümedeki "
                                   "çarpma olayı; v5 sınama 3, sınama 5 ve uzatılmış kümede koşulmadı.")
    tt = oku(K / "tani_temas_v6.csv")
    sol = [x for x in tt if x["surum"] in ("v3", "v5") and "sol yan" in x["govde_nokta"]]
    r["sol"] = (len(sol), mn([say(x["son_yerinde_s"]) for x in sol]), mx([say(x["son_yerinde_s"]) for x in sol]))
    k = r["k"]
    s5v3, s5v6 = k[("sinama5", "v3")], k[("sinama5", "v6")]
    s3v3, s3v6 = k[("sinama3", "v3")], k[("sinama3", "v6")]
    uzv3, uzv6 = k[("uzatilmis", "v3")], k[("uzatilmis", "v6")]
    oranlar = [k[(kk, "v6")][4] for kk, _, _ in KUMELER6 if k[(kk, "v6")][4] is not None]
    toplam_v3 = v3["ilk"][1] + v3["zin"][1]
    s_v3 = sy(v3["ilk"][2] + v3["zin"][2], 2)
    n_kume = len(KUMELER6)
    vs = varsayilan_surum()
    r["varsayilan"] = vs
    # tur 2 kuralı (önceden yazıldı, esnetilmedi): v6'nın bütün ilk giriş koşularında temas 0 VE sınama 3'te v6 >= v3
    tam_kosuldu = all(k[(kk, "v6")][1] == k[(kk, "v3")][1] for kk, _, _ in KUMELER6)
    kural = v6_top[1] == 0 and s3v6[0] >= s3v3[0] and tam_kosuldu
    beklenen = "v6" if kural else "v3"
    r["kural2"] = (kural, beklenen, vs)
    uyum = (f"koddaki değer <code>VARSAYILAN_SURUM = \"{vs}\"</code> kuralla uyumlu" if vs == beklenen else
            f"<strong class='kotu'>UYUMSUZ</strong>: kural {beklenen} diyor, koddaki değer {vs}")
    sik = r["2b_sik"]
    sik_txt = (", ".join(f"{lab_ad(x['sahne'], x['tohum'])} ({sy(say(x['sure_s']), 0)} s)" for x in sik)
               if sik else "yok")
    hukum = (f"Varsayılan sürüş {vs}; bu turun kuralıyla da {beklenen} kalıyor ({uyum}). v6'nın {n_kume} MuJoCo "
             f"kümesindeki {v6_top[0]} ilk giriş koşusunun hepsinde temas {v6_top[1]}; sınama 3'te v6 {s3v6[0]}/20, v3 "
             f"{s3v3[0]}/20; uzatılmış sürede v6 {uzv6[0]}/{uzv6[1]}, v3 {uzv3[0]}/{uzv3[1]}. 2B'de v6 "
             f"{r['2b']['v6'][0]}/{r['2b']['v6'][1]}, temas {r['2b']['v6'][2]}. Süre oranı v3'e göre {sy(min(oranlar), 2)}–"
             f"{sy(max(oranlar), 2)}. v3 de sıfır değil: ilk girişte {v3['ilk'][0]} koşuda {v3['ilk'][1]}, zincirde "
             f"{v3['zin'][0]} denemede {v3['zin'][1]} temas olayı. Farklar küçük (sınama 3'te 2, sınama 5'te 1 koşu); "
             "istatistik olarak anlamlı değil.")
    once_simdi = [
        ("Varsayılan sürüş", "v3 (v4 ve v5 çarpma verdiği için).",
         f"{vs}: ilk kararda sınama 5'te {s5v6[0]}/20 (v3 {s5v3[0]}/20); bu turun kuralında sınama 3'te {s3v6[0]}/20 (v3 "
         f"{s3v3[0]}/20) ve {v6_top[0]} koşuda temas {v6_top[1]}."),
        ("\"Çarpma sıfır\"",
         f"Sayfa \"yalnız v3'te tutuyor\" diyordu; o üç kümede (geliştirme, sınama 2, sınama 4; "
         f"{ek_['top_c']['v3'][1]} koşu) v3 {ek_['top_c']['v3'][0]} çarpmaydı.",
         f"v6'nın koştuğu bütün kümelerde sıfır: MuJoCo geliştirme, sınama 2, 3, 4, 5 ve uzatılmış süre ({v6_top[0]} "
         f"koşu), 2B geliştirme tohum 0 ve 1 ({r['2b']['v6'][1]} koşu). v3'ün toplamı {toplam_v3} olay / {s_v3} s; "
         f"sınama 3'te v3 {s3v3[2]}, sınama 5'te {s5v3[2]} temas. 2B'de v5 {r['2b']['v5'][2]} temas verdi."),
        ("Temasın nedeni",
         "Süpürme öngörüsü LiDAR'ın gerisinde kalan duvar ucunu eksik görüyor sanılıyordu.",
         f"İncelenen {r['sol'][0]} temasın hepsi aynı: iç köşede yerinde sola dönüşten {sy(r['sol'][1])}–"
         f"{sy(r['sol'][2])} s sonra sola yay ve gövdenin sol yanı duvar ucunu süpürüyor; duvar ucu taramada ve haritada "
         "vardı. v5'in öngörüsü çarpmayı gördü ama bütün adaylar \"çarpar\" çıktı."),
        ("Hız", f"v4 yaklaşık %{tam(100 * (1 - ek_['kume'][('gelistirme', 'v4', 'oran')]))} daha kısa sürede bitiriyordu.",
         f"v6'nın süre oranı v3'e göre {sy(min(oranlar), 3)}–{sy(max(oranlar), 3)} (ortanca, küme başına); 2B'de "
         f"v5'e göre {sy(r['2b_oran'][0], 3)}."),
    ]
    rozet = (rz("İnceleme: geçer", "iyi") + rz("Ek ölçüm: kural sağlandı", "iyi")
             + rz("Son inceleme: sayılar tuttu, küçük belge düzeltmeleri", "iyi"))
    olculen = (f"<p>Dört temasın kayıttan tanısı, ardından v6. v6 dondurulduktan sonra yeni sınama 5 üretildi ve koşuldu; "
               "geliştirme, sınama 2 ve sınama 4 gerileme denetimi. İlk kural: (a) sınama 5'te v6 başarısı v3'ten az "
               f"olmayacak, (b) o an koşulan kümelerde v6 temas olayı sıfır olacak. İkisi de sağlandı ({s5v6[0]} ≥ "
               f"{s5v3[0]}). Bu turun ikinci adımında kod değişmeden aynı dondurulmuş kopyadan üç ek ölçüm koşuldu: v6 "
               "sınama 3'te ve uzatılmış sürede, deneme zinciri v6 beyniyle (Yeniden deneme bölümü), 2B'de tohum 1. Kural "
               "koşudan önce yazıldı ve esnetilmedi: v6'nın bütün ilk giriş koşularında temas sıfır VE sınama 3'te v6 "
               "başarısı v3'ten az değilse v6 kalır; tek temas ya da daha düşük başarı v3'e döndürür.</p>")
    oneri = [
        f"<strong>Kural:</strong> {v6_top[0]} koşuda temas {v6_top[1]}, sınama 3'te {s3v6[0]} ≥ {s3v3[0]}, kümeler "
        f"{'tam' if tam_kosuldu else 'eksik'} koşuldu → {beklenen}; {uyum}. Deneme zinciri için ayrı kural da "
        "sağlandı (Yeniden deneme bölümü).",
        "<strong>Değişiklik:</strong> v6 süpürme denetimini son taramaya ek olarak son 2 s'nin taramaları, gövdenin 1,6 m "
        "çevresindeki harita hücreleri ve sanal başlangıç noktalarıyla yapıyor; yerinde dönüş denetimi de bu noktaları "
        "kullanıyor. Kabul edilen aday yoksa robot geri çekilip yeniden planlıyor. Izgara, dik açı ya da labirent bilgisi "
        "yok. Bu turda algoritma değişmedi.",
        f"<strong>Duvar payı:</strong> v6'nın {v6_top[0]} koşusunda en küçük pay "
        f"{sy(min(k[(kk, 'v6')][5] for kk, _, _ in KUMELER6) * 1000, 0)} mm, 5 mm altına inen koşu yok; v3'te sınama 2, "
        f"3 ve 5'te {k[('sinama2', 'v3')][6]} / {k[('sinama3', 'v3')][6]} / {k[('sinama5', 'v3')][6]} koşu.",
        f"<strong>2B'de v6'nın sıkışması (düzeltilmedi):</strong> {sik_txt}. Belirlenimci yeniden koşu aynı sonucu "
        "verdi: son dakikada her yeniden planda yolun ilk bacağı değişiyor ve robot yerinde ileri geri dönüp yerinden "
        "çıkamıyor; hakem 60 s hareketsizlikten sonra bitiriyor. Süpürme reddi ya da geri çekilme yok, v6'ya özgü olduğu "
        "gösterilmedi. MuJoCo v6 koşularında sıkışma yok.",
        "<strong>Yeni bulgu (düzeltilmedi):</strong> v3'ün sınama 5 teması başka bir mekanizma: duvar izleme kipinde "
        "yerinde sağa dönüşte sağ ön köşe duvar yüzüne değiyor. v6 bu kipi denetlemiyor.",
    ]
    iyimser = [
        "Teker azami hızı 0,39 m/s bir tahmin; fren zarfı ve komut gecikmesi varsayım.",
        "Geçmiş taramaların konum tahminiyle taşınmasındaki 2 s'lik kayma ölçülmedi.",
        "Pi 5'te v6'nın hesap yükü ölçülmedi (2B'de koşu başına gerçek süre v5'ten yaklaşık %20–30 fazla, gürültülü "
        "ölçüm).",
    ]
    aciklar = [
        "Duvar izleme kipinde yerinde dönüş süpürme denetimi yok (v3'ün sınama 5 temasının nedeni).",
        "Sınama 3 v6 için tam taze değil: v6'nın temas tanısında bu kümenin bir v3 kaydı kullanıldı.",
        "Bundan sonraki varsayılan kararları için hiç görülmemiş yeni bir sınama kümesi gerekiyor; sınama 3, 4 ve 5 artık "
        "görülmüş sayılır.",
        "2B'deki yerinde dönüş ile yeniden plan salınımı düzeltilmedi; denenecekse yeni bir geliştirme kümesinde.",
        "Uzatılmış kümede v3'ün duvar payı tanısı yok (tabloda \"-\").",
    ]
    ust = {
        "test": "Köşe hızı ve çarpmasız sürüş (v3–v6)",
        "hukum": f"Varsayılan {vs} kalıyor; bu turun kuralı sağlandı: v6'nın {v6_top[0]} ilk giriş koşusunda temas "
                 f"{v6_top[1]}, sınama 3'te v6 {s3v6[0]}/20 (v3 {s3v3[0]}/20), uzatılmış sürede {uzv6[0]}/{uzv6[1]} (v3 "
                 f"{uzv3[0]}/{uzv3[1]}); 2B'de {r['2b']['v6'][1]} koşuda temas {r['2b']['v6'][2]}. Süre oranı v3'e göre "
                 f"{sy(min(oranlar), 2)}–{sy(max(oranlar), 2)}. v3'ün kendisi {toplam_v3} temas olayı verdi.",
        "rozet": rz("İnceleme: geçer", "iyi"),
        "karar": f"Gerçek robotta varsayılan sürüş {vs} (koddaki değer). Önce teker azami hızı, komut gecikmesi ve v6'nın "
                 "Pi 5 hesap yükü ölçülmeli; duvar izleme kipindeki yerinde dönüşe süpürme denetimi eklenmeli.",
    }
    y = {"hukum": hukum, "rozet": rozet, "os": once_simdi, "olculen": olculen, "ana": ana, "grafik": grafik,
         "oneri": oneri, "iyimser": iyimser, "aciklar": aciklar}
    return r, y, ust


def inceleme_yeni(Y):
    u, h, t, s, d, k = Y
    kartlar = [kart(
        "Uçurum ve merdiven",
        "Ana sayılar CSV'lerle tuttu; rastgele seçilen 6 koşu aynı tohumla birebir yeniden üretildi. Denetçi yalnız sensör "
        "okumalarını, tutma freni yalnız enkoderi okuyor.",
        "<p>Üç engelleyici. (1) Önceden konmuş \"0 düşme\" ölçütü 10 sensörlü düzenin hükmünde sağlanmamıştı (hakem "
        f"{u['h1']['dus']} düşme, fiziksel {u['fiz1'][0]}); \"koşullu geçer\" kararı hükümden sonra koşulan bir rapor "
        "koşusuna ve varsayımsal bir fiziksel eşiğe dayanıyordu. (2) Hüküm ızgarası geliştirmede bilinen en kötü iki "
        "durumu (kenardan 0,35 m'de dönüş, 8–12 cm yarık) içermiyordu. (3) Kusur ve duyarlılık seçilen düzenle değil, eski "
        "6 sensörlü düzenle koşulmuştu; 0,25 m/s önerisinin gerekçesi eski düzene aitti.</p>",
        ["Tohum aralığı belgede 201–210 yazıyordu, kullanılan 201–205; \"seçimde hiç koşulmamış geometri\" yalnız yeni "
         "gruplar için doğruydu. Düzeltildi.",
         "Hüküm, sınama 2'nin geometri ızgarasını yeni tohumlarla yineledi; yanlış alarm sahnelerinin 7'si geliştirme "
         "sahnesi: bunlar \"görülmemiş veri\" sayılmaz.",
         "Seçim, hükümden önceki son karşılaştırmanın gösterdiği iki zayıflığa rağmen donduruldu; hüküm onları doğruladı.",
         "Kısa kip modelde ilk iyimser modelle aynı örnekleme yolunda; 10 sensörün tek hatta gecikmesiz okunması iyimser."],
        f"<p><strong>Hüküm değişti: geçmedi.</strong> Üç engelleyici de doğru bulundu. Önerilen iki düzeltme kodda denendi "
        f"ve yetmedi; her tekere iki dar iz ve iki yan sensör eklendi ({u['h2']['sensor']} sensör). Yeni hüküm "
        f"{u['h2']['n']} koşu, hiç kullanılmamış tohumlarla, 9 / 11 / 13 cm yarık ve kenardan 0,35 m dönüş dahil: hakem "
        f"{u['h2']['dus']} düşme ({u['h2']['uc']} uçurum koşusunda), {u['h2']['durma']} yanlış durma. Ölçüt yine "
        "sağlanmadı. Kusur ve duyarlılık 14 sensörle yinelendi. Etiket ve belge hataları düzeltildi.</p>"
        "<p><strong>Onarımın incelemesi: geçer.</strong> Sayılar CSV'lerden yeniden sayıldı ve tuttu (hakem "
        f"{u['kat_top']['14'][0]} / {u['kat_top']['14'][1]}, fiziksel {u['kat_top']['14'][2]}, yanlış durma "
        f"{u['kat_top']['14'][3]} / {u['kat_top']['14'][4]}); hüküm görev listeleri bugünkü koddan yeniden üretildi ve ham "
        "kayıtla aynı çıktı; sızıntı yok. Düzeltilenler: belgelerde \"seçilen\" yerine \"ölçütü sağlamayan en iyi aday\" "
        "yazıldı, seçim dosyasına durum notu eklendi, önceki \"koşullu geçer\" hükmü \"geçmedi\" oldu, \"bu tohumlar "
        f"kullanılmadı\" ve \"hiç koşulmamış geometri\" ifadeleri düzeltildi ({u['ayni_gorev'][0]} / "
        f"{u['ayni_gorev'][1]} görev önceki hükümle aynı sahne ve senaryo). Üç düzen tehlike sınıfına göre yan yana "
        "kondu; satın alma kararı verilmedi.</p>"
        f"<p><strong>Bağımsız hüküm ve incelemesi: geçer.</strong> Ardından yeni tohum ({u['h3']['tohum'][0]}–"
        f"{u['h3']['tohum'][1]}) ve hiç koşulmamış sahnelerle beş düzen aynı {u['h3']['taban_n']} görevi koştu; ölçüt "
        f"koşudan önce yazıldı. Yalnız {e(u['h3']['adq'](u['secim3']))} düzeni geçti (hakem "
        f"{u['h3']['top'][u['secim3']]['d']} / {u['h3']['top'][u['secim3']]['n']}, yanlış durma "
        f"{u['h3']['top'][u['secim3']]['durma']} / {u['h3']['top'][u['secim3']]['ya']}). Ayrı bir inceleme sayıları "
        "CSV'den ve ham kayıttan yeniden saydı, hepsi tuttu; görev listesi ham kayıtla aynı çıktı; altı görev aynı "
        "tohumla birebir yeniden üretildi; denetçi ve sürüş kuralları yalnız sensör okumasını ve sürüş komutunu görüyor. "
        "Düzeltilen tek şey bir tablo etiketiydi (sayılar aynı). İki çekince hükmü değiştirmiyor: 1,5 m derin köşe "
        "sahnesi sensör menzilinin dışında, ve sürüş kurallı düzen dönüş görevinde öbürleri kadar dönmüyor.</p>",
        [f"Onaylı düzenin payı ince: en küçük {_pay_tr(u['h3']['top'][u['secim3']]['p'])} cm.",
         "Onaylı düzenle kusur ve duyarlılık ızgaraları koşulmadı.",
         f"{u['h3']['top'][u['secim3']]['sensor']} sensörün donanım gerçekliği (iki I2C hattı, dar koni, yan pencere) "
         "ölçülmedi; yan sensörler dar şeritte sürmeyi engelliyor.",
         "6 sensörlü düzen ortak koşulla ölçüldü, kendi tanımıyla değil."],
        rozetler=rz("İnceleme: koşullu") + rz("Onarım sonrası: geçmedi", "kotu") + rz("Bağımsız hüküm: geçti", "iyi")
        + rz("Son inceleme: geçer", "iyi"),
        onarim_baslik="Onarımda ve bağımsız hükümde ne değişti"),
        kart(
        "Harita eskimesi ve çalışırken taşınma",
        "Ana sayılar CSV'lerden yeniden sayıldı ve tuttu; üç koşu aynı tohumla yeniden koşuldu, bütün alanlar aynı.",
        "<p>Yok.</p>",
        ["Seçilen \"emin değilim\" kuralı, geliştirmede eşit sonuç veren dört aday arasından yalnız aday sözlüğünün "
         "sırasıyla seçildi; belirsizlik eşiği 0,05 m ızgaranın en alt değeri. Sızıntı yok (kural sınamadan önce yazıldı), "
         f"ama boşuna durmaların {t['ger_kaynak'][0]}/{t['ger_kaynak'][1]}'inin nedeni bu keyfî seçim.",
         "Bir kip dosyası sınama koşarken düzenlendi; düzenlemeden önce ve sonraki koşular aynı tohumla yeniden koşulup "
         "aynı çıktı, ama dosyanın geçmişi olmadığı için ne değiştiği gösterilemiyor.",
         "Kural yalnız v3 ve izlemeyle, dönüşsüz yüzey olmadan seçildi; algılı kiplere öyle uygulandı.",
         "\"Uyum &lt; 0,60 hiçbirinde değil\" yalnız algılı kip için doğru; izleme + algıda iki alarm var."],
        "<p><strong>Onarım gerekmedi.</strong> İnceleme taşınma belgesinde dört şeyi düzeltti: atılan koşulların listesi "
        "(14 koşul; eğrilme, gürültü ve odometri planda yoktu), poz sıçraması aralığı (sınamada 0,4–11,8 m), izlemenin "
        "görünmeyen sessiz hatalarının uyum aralığı (0,80–1,00) ve eskimede fark etme oranının yanlış alarm eğilimiyle "
        "karışık olduğu notu.</p>",
        ["Tam gerileme, 6 haritalı beyin ve MuJoCo bu turda yok.", "Tek kural (uyum &lt; 0,75) yeni tohumlarla sınanmalı.",
         "Algılı kipin geçiş testinin düzeltmesi ölçülmedi."],
        rozetler=rz("İnceleme: geçer", "iyi"), onarim_baslik="Onarım"),
        kart(
        "LiDAR'sız sanal ray",
        "Bütün ana sayılar iki CSV'den yeniden hesaplandı; 6 koşu ve ilk turun başarısız koşusu aynı tohumla birebir "
        "yeniden üretildi.",
        f"<p>Tek etiketlik etkenlerin yarısı aslında sınanmamıştı: eksik ve yanlış yer etiketi 12 koşunun "
        f"{s['etkisiz']['kayip1'][0]}'sında robotun görmediği kısımdaydı ve bu koşular temiz koşuyla birebir aynıydı. "
        f"Etkili koşularda eksik etiket {s['etkisiz']['kayip1'][1]}/{s['etkisiz']['kayip1'][2]}, yanlış yer "
        f"{s['etkisiz']['yanlis1'][1]}/{s['etkisiz']['yanlis1'][2]}.</p>",
        ["Başlatma hatası karşılaştırmasında seçim etkisi var: iyileşme yalnız konumlanan koşulardan (11'e karşı 7).",
         "Doğrulamalı başlatma orta kurulumda temas olayını artırıyor; özette yorumlanmamıştı.",
         "İlk tur düzeltmesi bir benzetmeye dayanıyordu; inceleme ilk turun kendi başarısız koşusunu yeniden üretti.",
         "Varsayılanın değişmediğini gösteren bir regresyon testi yoktu.", "Örneklem küçük; farklar tek koşu düzeyinde."],
        f"<p><strong>Bulgu kapandı.</strong> Etiket artık aynı koridor ve tohumun kusursuz koşusunda süzgecin kabul ettiği "
        f"etiketlerden seçiliyor; tohum 1–6 ile koşul başına 24 koşu. Eksik etiket "
        f"{s['rota']['kayip1_rota'][0]}/24; yanlış yer ilk turun dediğinden ağır çıktı (1 m'de "
        f"{s['rota']['yanlis1_rota'][0]}/24 ve {s['rota']['yanlis1_rota'][2]} duvar teması). Süreçler arası bir dosya "
        "yarışı düzeltildi; varsayılan için regresyon testi eklendi.</p>",
        ["Rastgele bırakılmada eksik ve yanlış yer etiketi koşulmadı.", "Yanlış yerin kırılma noktası 0,25–0,5 m arasında.",
         "Yeniden başlatmanın tek etiketi çapraz denetlemesi önerildi, uygulanmadı."],
        rozetler=rz("İnceleme: koşullu") + rz("Onarım: kapandı", "iyi")),
        kart(
        "Labirent: haritayla yeniden deneme ve çarpmasız sürüş",
        "Bütün sayılar CSV'lerden yeniden sayıldı; temas kayıtlardaki temas dizisinden ayrıca doğrulandı; üç koşu aynı "
        "tohumla birebir yeniden üretildi.",
        "<p>Yok.</p>",
        ["v6 sınama 3'te ve uzatılmış kümede koşulmadı; \"temas 0\" yalnız v6'nın koştuğu kümeler için geçerli.",
         "Varsayılan kuralının \"tam koşuldu\" denetimi yalnız MuJoCo'ya bakıyor; 2B yalnız tohum 0 ile koşuldu.",
         "v3'ün sınama 5 sonuçlarından ikisi v6 dondurulmadan önce hazırdı; bakıldığına dair iz yok, risk düşük.",
         "Sonuç belgesinin v5 bölümünde eskimiş \"varsayılan v3\" cümlesi kaldı.",
         "2B'de v6'nın yeni bir sıkışma başarısızlığı belgede yoktu.",
         "Tanı aracı bir temas süresini kayıttan farklı sayıyor (2,35 s'ye karşı 1,50 s); hüküm sayıları tutarlı."],
        "<p><strong>Onarım gerekmedi.</strong> Açıklama belgesinde bir sayı düzeltildi: \"v4/v5'te bu sayı 1–5 koşuydu\" "
        "yerine küme başına v4'te 3–5, v5'te 0–2, v3'te 0–2.</p>"
        "<p><strong>Ek ölçüm ve incelemesi: geçer.</strong> İnceleme açıklarını kapatmak için v6 sınama 3'te, uzatılmış "
        "sürede, deneme zincirinde ve 2B tohum 1'de koşuldu (kod değişmedi). İnceleme bütün sayıları ham CSV'lerden "
        f"yeniden saydı: {k['v6_top'][0]} ilk giriş koşusunda temas {k['v6_top'][1]}, zincirde v6 "
        f"{20 - d['sinama4_v6']['dag'][0]}/20 ve v3 {20 - d['sinama4']['dag'][0]}/20. İki koşu aynı tohumla yeniden "
        "koşuldu ve aynı çıktı; bütün v6 kayıtlarının kod dondurulduktan sonra yazıldığı doğrulandı. Koddaki varsayılan "
        f"{k['varsayilan']}, kuralla tutarlı. Düzeltilenler küçük: 2B sıkışmasında dönüş yönünün tersine dönme aralığı "
        "(her plandan sonra, yaklaşık 1 s) ve belgede birkaç yönlendirme. Sonuç belgesindeki eskimiş \"varsayılan v3\" "
        "cümlesine güncelleme notu kondu.</p>",
        ["Sonraki kararlar için hiç görülmemiş yeni bir sınama kümesi gerekiyor.",
         "Duvar izleme kipindeki dönüş denetimi yok; 2B'deki yerinde dönüş salınımı düzeltilmedi.",
         "Pi 5 hesap yükü ölçülmedi."],
        rozetler=rz("İnceleme: geçer", "iyi") + rz("Ek ölçüm: geçer", "iyi"), onarim_baslik="Onarım")]
    return "".join(kartlar)


# ================================================================== SAYFA
CSS = r"""
:root{--bg:#f6f5f1;--yuzey:#ffffff;--yuzey2:#f0efea;--yazi:#1d1e20;--soluk:#5c5f66;--cizgi:#dddcd5;
--vurgu:#1f56c2;--c-a:#2d6fd8;--c-a2:#5b93e6;--c-a3:#9bbcf0;--c-b:#d4802a;--c-c:#8d929a;
--iyi:#1c7448;--iyi-z:#e4f3ea;--uyari:#94590b;--uyari-z:#fbf0dc;--kotu:#b2271e;--kotu-z:#fbe6e4;--iz:#ebeae4}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#131416;--yuzey:#1c1e21;--yuzey2:#24272b;
--yazi:#ebebe8;--soluk:#a4a8ae;--cizgi:#33363b;--vurgu:#8db2f5;--c-a:#6d9ef0;--c-a2:#4f7fcf;--c-a3:#355a99;--c-b:#e9a35c;
--c-c:#8d939b;--iyi:#6ccf98;--iyi-z:#173325;--uyari:#e9b15a;--uyari-z:#3a2c12;--kotu:#f2867d;--kotu-z:#3c1c1a;--iz:#2a2d31}}
:root[data-theme="dark"]{--bg:#131416;--yuzey:#1c1e21;--yuzey2:#24272b;--yazi:#ebebe8;--soluk:#a4a8ae;--cizgi:#33363b;
--vurgu:#8db2f5;--c-a:#6d9ef0;--c-a2:#4f7fcf;--c-a3:#355a99;--c-b:#e9a35c;--c-c:#8d939b;--iyi:#6ccf98;--iyi-z:#173325;
--uyari:#e9b15a;--uyari-z:#3a2c12;--kotu:#f2867d;--kotu-z:#3c1c1a;--iz:#2a2d31}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--yazi);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,
"Helvetica Neue",Arial,sans-serif;overflow-wrap:break-word}
main{max-width:980px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.9rem;line-height:1.2;margin:0 0 8px;letter-spacing:-.01em}
h2{font-size:1.4rem;line-height:1.25;margin:0 0 12px;letter-spacing:-.005em}
h3{font-size:1.05rem;margin:22px 0 8px}
h4{font-size:.95rem;margin:16px 0 6px;color:var(--soluk)}
p{margin:0 0 10px}
ul{margin:0 0 10px;padding-left:20px}
li{margin:0 0 6px}
a{color:var(--vurgu)}
.ust{display:flex;gap:16px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap}
.alt-baslik{color:var(--soluk);max-width:70ch}
#tema-dugme{font:inherit;font-size:.9rem;background:var(--yuzey);color:var(--yazi);border:1px solid var(--cizgi);
border-radius:999px;padding:6px 14px;cursor:pointer}
#tema-dugme:focus-visible{outline:2px solid var(--vurgu);outline-offset:2px}
.uyari-kutu{background:var(--uyari-z);border:1px solid color-mix(in srgb,var(--uyari) 35%,transparent);border-radius:10px;
padding:12px 14px;margin:16px 0}
nav.icindekiler{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0 4px}
nav.icindekiler a{font-size:.85rem;text-decoration:none;background:var(--yuzey);border:1px solid var(--cizgi);
border-radius:999px;padding:4px 11px;color:var(--yazi)}
section{background:var(--yuzey);border:1px solid var(--cizgi);border-radius:14px;padding:20px 20px 14px;margin:22px 0}
.bolum-no{display:inline-block;font-size:.8rem;color:var(--soluk);margin-bottom:4px}
.hukum{background:var(--yuzey2);border-left:4px solid var(--vurgu);padding:10px 14px;border-radius:0 8px 8px 0}
.tablo-kap{overflow-x:auto;margin:6px 0 4px;border:1px solid var(--cizgi);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--cizgi)}
th{background:var(--yuzey2);font-weight:600;font-size:.82rem;color:var(--soluk)}
tbody tr:last-child td{border-bottom:0}
table.veri td{font-variant-numeric:tabular-nums}
table.veri td:first-child{min-width:150px}
.tablo-not,.g-not{font-size:.82rem;color:var(--soluk);margin:6px 0 10px}
.ince{color:var(--soluk);font-size:.92em}
.kotu{color:var(--kotu);font-weight:600}
.iyi{color:var(--iyi)}
table.karar{font-size:.93rem;table-layout:fixed}
table.karar td:first-child{font-weight:600}
table.karar th:nth-child(1){width:14%}
table.karar th:nth-child(2){width:24%}
table.karar th:nth-child(3){width:33%}
table.karar th:nth-child(4){width:29%}
.grafik{margin:6px 0 4px;padding:14px;border:1px solid var(--cizgi);border-radius:10px}
.g-baslik{font-weight:600;margin-bottom:8px;font-size:.95rem}
.g-lejant{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.82rem;color:var(--soluk);margin-bottom:10px}
.lj{display:inline-flex;align-items:center;gap:6px}
.lj i{display:inline-block;width:12px;height:12px;border-radius:3px}
.g-satir{display:grid;grid-template-columns:minmax(120px,32%) 1fr;gap:4px 12px;align-items:center;padding:5px 0;
border-top:1px solid var(--cizgi)}
.g-satir:first-of-type{border-top:0}
.g-etiket{font-size:.86rem}
.g-cubuklar{display:flex;flex-direction:column;gap:3px;min-width:0}
.g-cubuk{display:flex;align-items:center;gap:8px;min-width:0}
.g-iz{position:relative;flex:1 1 auto;height:14px;background:var(--iz);border-radius:3px;min-width:40px}
.g-dolgu{position:absolute;left:0;top:0;bottom:0;border-radius:3px}
.g-deger{flex:0 0 auto;font-size:.8rem;font-variant-numeric:tabular-nums;min-width:2.2em;max-width:55%}
.g-yok{font-size:.8rem;color:var(--soluk);font-style:italic}
.g-esik{position:absolute;top:-3px;bottom:-3px;width:0;border-left:2px dashed var(--yazi);opacity:.55;z-index:1}
.g-esik-ornek{display:inline-block;width:0;height:12px;border-left:2px dashed var(--yazi);opacity:.55;margin-right:6px;
vertical-align:middle}
.g-yigin{display:flex;height:22px;overflow:hidden}
.g-parca{position:relative;display:flex;align-items:center;justify-content:center;font-size:.75rem;color:#fff;
font-weight:600;font-variant-numeric:tabular-nums;border-right:1px solid var(--yuzey)}
.oneri ul{margin-bottom:6px}
.iki{display:grid;grid-template-columns:1fr 1fr;gap:4px 24px}
.iki ul{font-size:.92rem}
.kart{border:1px solid var(--cizgi);border-radius:12px;padding:14px 16px;margin:14px 0;background:var(--yuzey)}
.kart header{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between}
.kart h3{margin:0}
.kart ul{font-size:.92rem}
.rozet{display:inline-block;font-size:.78rem;font-weight:600;border-radius:999px;padding:3px 10px;margin:2px 4px 2px 0}
.rozet.uyari{background:var(--uyari-z);color:var(--uyari)}
.rozet.iyi{background:var(--iyi-z);color:var(--iyi)}
.rozet.kotu{background:var(--kotu-z);color:var(--kotu)}
sup.bel{color:var(--uyari);font-weight:700;font-size:.72em;margin-left:1px;cursor:help}
p.hukum.eski-hukum{border-left-color:var(--c-c)}
.os{display:flex;flex-direction:column;border:1px solid var(--cizgi);border-radius:10px;margin:6px 0 4px}
.os-satir{display:grid;grid-template-columns:minmax(110px,18%) minmax(0,1fr) minmax(0,1fr);gap:6px 14px;padding:10px 12px;
border-top:1px solid var(--cizgi);font-size:.9rem}
.os-satir:first-child{border-top:0}
.os-konu{font-weight:600}
.os-once{color:var(--soluk)}
.os-et{display:block;font-size:.72rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--soluk);
margin-bottom:2px}
.os-simdi .os-et{color:var(--vurgu)}
details.eski{margin:18px 0 4px;border:1px dashed var(--cizgi);border-radius:10px;padding:8px 12px;background:var(--yuzey2)}
details.eski>summary{cursor:pointer;font-weight:600;font-size:.92rem;color:var(--soluk)}
details.eski[open]>summary{margin-bottom:8px}
.eski-ic .kart,.eski-ic .grafik,.eski-ic .tablo-kap{background:var(--yuzey)}
td.once-hucre{color:var(--soluk);font-size:.9em}
ul.belge{font-size:.82rem}
ol.olcum{padding-left:22px}
ol.olcum li{margin-bottom:10px}
.olcum .kaynak{display:inline-block;font-size:.75rem;color:var(--soluk);border:1px solid var(--cizgi);border-radius:999px;
padding:0 8px;margin-left:4px}
footer{color:var(--soluk);font-size:.82rem;margin-top:28px}
code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.86em;background:var(--yuzey2);
padding:1px 5px;border-radius:4px}
table.katman{table-layout:fixed}
table.katman th:first-child{width:22%}
table.katman td:first-child{min-width:0;font-weight:600}
table.katman .th-alt{display:block;font-weight:400;font-size:.95em;margin-top:2px}
table.katman tr.g-ek td:first-child{font-weight:400;color:var(--soluk)}
table.katman tr.g-toplam td{background:var(--yuzey2)}
.uyari{color:var(--uyari);font-weight:600}
table.katman.bes th:first-child{width:20%}
table.katman.olcut th:first-child{width:26%}
table.katman.olcut td:first-child .th-alt{display:block;font-weight:400;color:var(--soluk);font-size:.85em;margin-top:2px}
@media (max-width:720px){
 table.katman{table-layout:auto}
 table.katman,table.katman tbody,table.katman tr,table.katman td{display:block;width:100%!important}
 table.katman thead{display:none}
 table.katman tr{border-bottom:1px solid var(--cizgi);padding:6px 0}
 table.katman tr:last-child{border-bottom:0}
 table.katman td{border:0;padding:3px 12px}
 table.katman td:not(:first-child)::before{content:attr(data-etiket);display:block;font-size:.75rem;color:var(--soluk);
 font-weight:600}
 h1{font-size:1.55rem} section{padding:16px 14px 10px}
 .iki{grid-template-columns:1fr}
 .g-satir{grid-template-columns:1fr}
 .os-satir{grid-template-columns:1fr}
 table.karar{table-layout:auto}
 table.karar,table.karar tbody,table.karar tr,table.karar td{display:block;width:100%!important}
 table.karar thead{display:none}
 table.karar tr{border-bottom:1px solid var(--cizgi);padding:6px 0}
 table.karar tr:last-child{border-bottom:0}
 table.veri td:first-child{min-width:120px}
 table.karar td{border:0;padding:4px 12px;white-space:normal!important}
 table.karar td:not(:first-child)::before{content:attr(data-etiket);display:block;font-size:.75rem;color:var(--soluk);
 font-weight:600}
}
@media print{#tema-dugme,nav.icindekiler{display:none}section{break-inside:avoid-page}}
"""

JS = r"""
(function(){var k='testler-rapor-tema',r=document.documentElement;
function uygula(t){if(t){r.setAttribute('data-theme',t);}else{r.removeAttribute('data-theme');}}
var h=(location.hash||'').replace('#',''),t=null;
if(h==='koyu'){t='dark';}else if(h==='acik'){t='light';}else{try{t=localStorage.getItem(k);}catch(e){t=null;}}
uygula(t);
function koyuMu(){var a=r.getAttribute('data-theme');if(a){return a==='dark';}
return !!(window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches);}
document.addEventListener('DOMContentLoaded',function(){var b=document.getElementById('tema-dugme');if(!b){return;}
function yaz(){b.textContent=koyuMu()?'Açık tema':'Koyu tema';}
yaz();b.addEventListener('click',function(){var y=koyuMu()?'light':'dark';uygula(y);
try{localStorage.setItem(k,y);}catch(e){}yaz();});});})();
"""


def sayfa(R, govdeler, ustler, Y, yeniler, ustler_yeni):
    bugun = _dt.date.today()
    aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    tarih = f"{bugun.day} {aylar[bugun.month - 1]} {bugun.year}"
    kimlik = ["ucurum", "harita", "tasinma", "sanalray", "deneme", "kose"]
    adlar = [ustler_yeni[i].get("test") or ustler[i]["test"] for i in range(6)]
    karar_satir = "".join(
        f"<tr><td><a href='#{kid}'>{e(ad)}</a></td>"
        f"<td data-etiket='Önce (önceki tur)' class='once-hucre'>{y.get('once') or x['hukum']}</td>"
        f"<td data-etiket='Şimdi (bu tur)'>{y['rozet']}<br>{y['hukum']}</td>"
        f"<td data-etiket='Gerçek robotta karar'>{y['karar']}</td></tr>"
        for kid, ad, x, y in zip(kimlik, adlar, ustler, ustler_yeni))
    bolumler = "".join(
        f"<section id='{kid}'><span class='bolum-no'>Bölüm 2 · Test {i + 1} / 6</span><h2>{e(ad)}</h2>"
        f"{bolum_yeni(y, g, 'Önceki turun ayrıntısı (tablolar, grafikler, öneriler)')}</section>"
        for i, (kid, ad, y, g) in enumerate(zip(kimlik, adlar, yeniler, govdeler)))
    u = Y[0]
    k_vs = e(Y[5]["varsayilan"])
    u_h3 = u["h3"]
    u_gecen = e(u_h3["adq"](u["secim3"]))
    u_pay = _pay_tr(u_h3["top"][u["secim3"]]["p"])
    tork = bel(U, "Uçurum", "≈ 0,70 N·m", ["0,70 N·m"], "10° inişte konum tutma için teker başına ≈ 0,70 N·m tork")
    olcumler = [
        ("Uçurum", f"Onaylı düzenin {u_h3['top'][u['secim3']]['sensor']} VL53L1X'i: tek I2C hattında 20 ms'de yetişiyor mu "
                   "(büyük olasılıkla iki hat gerekir), sensör başına XSHUT ucu, sensörler arası etkileşim, etek "
                   "penceresinin ışını kırpıp kırpmadığı (dış iz etek sınırına çok yakın)."),
        ("Uçurum", f"Dar yarıkta pay: simülasyonda en küçük pay {u_pay} cm. Gerçek lastik, montaj hatası ve dar koninin "
                   "izi masada ölçülmeli; pay buna dayanıyor."),
        ("Uçurum", "Dar koninin (ROI 15°) masada sinyal ve menzil kaybı; kısa kipte 20 ms ve 1,3 m'nin gerçekte tutması; "
                   "parlak, siyah ve halı zeminde dönüşsüz örnek oranı (%20'yi geçerse robot durur)."),
        ("Uçurum", f"10° inişte konum tutma için teker başına gereken tork ({tork}) ve motorun sürekli torku; 2,0 m/s² "
                   "rampa freniyle gerçek durma yolu, 0,25 m/s ile."),
        ("Harita", "Okul koridorunda LiDAR'ın dönüş haritası: yüzey türüne göre (cam kapı, cam bölme, koyu / parlak kaplama) "
                   "dönüş vermeyen ışın oranı ve etkin en uzun menzil; kapı durumunun gün içinde ne kadar değiştiği."),
        ("Taşınma", "Algılı kipin kapı açıklığı ve camda geçiş testi kapatılmış hâli (önce simülasyonda, sonra koridorda); "
                    "robot kaldırılırken tekerin odometriye sahte yol yazıp yazmadığı; algının Pi 5'teki süresi."),
        ("Sanal ray", "Kurulumdan sonra robotla bir tur \"etiket ve harita aynı mı\" denetimi (0,5 m kayma bozuyor); etiket "
                      "yerinin ±5 cm ile ölçülmesi; gerçek ışıkta 15 cm etiketin algılama menzili ve Pi 5'te algılama "
                      "süresi."),
        ("Labirent", "v6'nın Pi 5 hesap yükü; teker azami hızı (simülasyonda 0,39 m/s tahmin) ve Pi'den ESP32'ye komut "
                     "gecikmesi; robotu başlangıca koymadaki gerçek yerleştirme hatası (simülasyonda 3 cm / 2°)."),
    ]
    olcum_html = "<ol class='olcum'>" + "".join(
        f"<li>{m} <span class='kaynak'>{e(kay)}</span></li>" for kay, m in olcumler) + "</ol>"
    inc_yeni = inceleme_yeni(Y)
    inc_eski = inceleme_eski(R)
    belge_html = "<ul class='belge'>" + "".join(
        f"<li><strong>{e(bl)}:</strong> {e(ac)}</li>" for bl, ac in BELGE) + "</ul>"
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Altı Test Sonucu</title>
<style>{CSS}</style>
<script>{JS}</script>
</head>
<body>
<main>
<div class="ust">
<div>
<h1>Altı testin sonucu</h1>
<p class="alt-baslik">Robotun simülasyonda geçtiği altı test, tamamlama turundan sonra: ne bulundu, önceki tura göre ne
değişti, gerçek robotta hangi kararı değiştiriyor. Sayılar testlerin sonuç tablolarından (CSV) yeniden sayıldı.</p>
</div>
<button id="tema-dugme" type="button">Koyu tema</button>
</div>
<div class="uyari-kutu"><p><strong>Hepsi simülasyon.</strong> Bu turda önceki turun açık bıraktığı işler ölçüldü ve her
hattı bağımsız bir inceleme yeniden denetledi. Uçurum testinde görülmüş ızgarada hiçbir düzen önceden konan ölçütü
sağlamamıştı; yeni tohum ve hiç koşulmamış sahnelerle koşulan bağımsız hükümde yalnız {u_gecen} düzeni
<strong>geçti</strong> ve onaylı seçim oldu, ama payı ince (en küçük {u_pay} cm). Labirentte ek ölçümden sonra varsayılan sürüş {k_vs} kaldı. Sanal raydaki
bulgu onarımla kapandı; harita ve taşınma hatları geçer aldı.</p>
<p><sup class='bel'>†</sup> işaretli sayılar CSV'den değil, testin sonuç belgesinden alındı (liste sayfanın sonunda).
Her bölümün sonunda önceki turun ayrıntısı katlanmış duruyor.</p></div>
<nav class="icindekiler" aria-label="Bölümler">
<a href="#karar">Karar tablosu</a><a href="#ucurum">Uçurum</a><a href="#harita">Harita eskimesi</a>
<a href="#tasinma">Taşınma</a><a href="#sanalray">Sanal ray</a><a href="#deneme">Yeniden deneme</a>
<a href="#kose">Köşe hızı</a><a href="#inceleme">Bağımsız inceleme</a><a href="#olcum">İlk ölçülecekler</a>
</nav>

<section id="karar">
<span class="bolum-no">Bölüm 1</span>
<h2>Karar tablosu</h2>
<p class="ince">"Önce" önceki turun hükmü, "şimdi" bu turun. Rozetler bağımsız incelemenin ve onarımın sonucu.</p>
<div class="tablo-kap"><table class="karar"><thead><tr><th>Test</th><th>Önce (önceki tur)</th><th>Şimdi (bu tur)</th>
<th>Gerçek robotta karar</th></tr></thead><tbody>{karar_satir}</tbody></table></div>
</section>

{bolumler}

<section id="inceleme">
<span class="bolum-no">Bölüm 3</span>
<h2>Bağımsız inceleme: hükümler ve bulunan sorunlar</h2>
<p>Bu turda her test hattını, onu yürütmeyen ayrı bir inceleme yeniden denetledi: sayıları CSV'lerden yeniden saydı,
birkaç koşuyu aynı tohumla yeniden koştu, sınama verisinin ayara sızıp sızmadığına baktı. Bulduğu sorunlar aşağıda olduğu
gibi; onarım yapıldıysa ne değiştiği ve neyin açık kaldığı da. Harita eskimesi ve taşınma tek hat olarak incelendi.</p>
{inc_yeni}
<details class="eski"><summary>Önceki turun incelemesi</summary><div class="eski-ic">{inc_eski}</div></details>
</section>

<section id="olcum">
<span class="bolum-no">Bölüm 4</span>
<h2>Gerçek robotta ilk ölçülecekler</h2>
<p>Bu turun önerilerinden. Simülasyondaki sonuçların çoğu bu ölçümlere dayanan varsayımlarla duruyor; sıra, güvenliği en
çok etkileyenden başlıyor.</p>
{olcum_html}
</section>

<footer>
<p><strong><sup class='bel'>†</sup> Sonuç belgesinden alınan sayılar</strong> (betik her birinin belgede hâlâ geçtiğini
denetliyor):</p>
{belge_html}
<p>Bu sayfa <code>kod/fizik/deneyler/testler_rapor.py</code> ile {tarih} tarihinde üretildi. Kaynaklar:
<code>ucurum/sonuc</code>, <code>deneyler/harita_eskimesi/sonuc</code>, <code>deneyler/tasinma/sonuc</code>,
<code>sanalray/sonuc</code>, <code>kesif/sonuc</code> altındaki CSV'ler ve SONUC.md belgeleri. Yeniden üretmek için
betiği aynı klasörde çalıştırın; dış bağlantı yok, sayfa çevrimdışı açılır.</p>
</footer>
</main>
</body>
</html>
"""


def main():
    sonuclar, govdeler, ustler = [], [], []
    for f in (ucurum, harita, tasinma, sanalray, deneme, kose):
        r, g, u = f()
        sonuclar.append(r)
        govdeler.append(g)
        ustler.append(u)
    Y, yeniler, ustler_yeni = [], [], []
    for f, eski in zip((ucurum_yeni, harita_yeni, tasinma_yeni, sanalray_yeni, deneme_yeni, kose_yeni), sonuclar):
        r, y, u = f(eski)
        Y.append(r)
        yeniler.append(y)
        ustler_yeni.append(u)
    metin = sayfa(sonuclar, govdeler, ustler, Y, yeniler, ustler_yeni)
    CIKTI.write_text(metin, encoding="utf-8")
    if "--sayilar" in sys.argv:
        u, h, t, s, d, k = Y
        print("ucurum", u["h1"], u["h2"], u["fiz1"], u["fiz2"], u["fiz2s"], u["k25"], u["k30"], u["k25_eski"],
              u["rampa"], u["kayma"], u["kusur"], u["parlak"], u["kotu_birlesik"], u["arka_guvenli"])
        print("harita", [(x[2], round(x[0], 3), round(x[1], 3)) for x in h["sira"]], h["gen"], h["kip_top"])
        print("tasinma", t["g"], t["alarm"], t["fark"], t["emin"], t["ger_kaynak"])
        print("sanalray", s["ab"], s["rota"], s["etkisiz"],
              {kk: (v[0], v[1], v[3], v[4]) for kk, v in s["ky"].items()}, s["bedel"])
        print("deneme", {kk: (v["dag"], v["ilk_kpi"], v["carpma"]) for kk, v in d.items()
                         if isinstance(v, dict) and "dag" in v}, d["kopuk"], d["ilk_bas"])
        print("kose", k["k"], k["v6_top"], k["v3"], k["2b"], k["sol"])
    print(f"yazıldı: {CIKTI.name} ({CIKTI.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
