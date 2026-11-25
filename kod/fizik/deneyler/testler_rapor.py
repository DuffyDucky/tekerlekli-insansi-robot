"""Altı simülasyon testinin sonuçlarını tek, çevrimdışı açılan bir HTML sayfasında toplar.

Kullanım (bu klasörde):  py -3 testler_rapor.py
Çıktı: testler-rapor.html (aynı klasör). Dış kaynak yok; bütün biçem ve betik gömülü.

Tablolardaki ve üst karar tablosundaki sayılar her koşuda sonuç CSV'lerinden yeniden sayılır.
CSV'de olmayan birkaç sayı (LiDAR'lı taban, devrilme el hesabı gibi) sonuç belgelerinden (SONUC.md) alınır;
betik her birinin ilgili SONUC.md içinde hâlâ geçtiğini denetler, geçmiyorsa durur.
Yalnız standart kütüphane kullanılır.
"""
from __future__ import annotations

import csv
import datetime as _dt
import html
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
        f"<p class='hukum'><strong>Hüküm.</strong> {hukum}</p>"
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

    sonuc_var(U, "düz zeminde 3,68 m/s², 10° inişte 1,93 m/s²", "0,0 mm", "≈ 87 mm", "0,40 m", "XSHUT")

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
        f"<strong>Hız:</strong> sınamada 0,39 m/s'de en küçük pay {sy(r['pay_dar'])} cm (dar açıklık), geniş kenarda "
        f"{sy(r['pay_genis'])} cm. Bu pay sensör gecikmesindeki ya da fren modelindeki birkaç santimlik hatayla "
        f"tükenebilir; gerçek robotta ilk denemeler 0,25 m/s ile.",
        "<strong>Sensörden tasarruf gerekirse:</strong> beşli düzen (ön orta sensörlü) sınamada düşmedi ama geliştirmede "
        f"0,40 m açıklıkta {r['gel_5'][0]} / {r['gel_5'][1]} düştü; ancak en dar açıklık ≈ 0,45 m kabul edilirse "
        "ikinci seçenek. Geri gitme firmware'de yasaksa arka iki sensör çıkarılabilir.",
        f"<strong>Kırılma:</strong> 10° iniş rampasında her fren kipinde robot tam durmuyor, frenden sonra yaklaşık "
        f"{sy(r['inis_kayma'][1], 2)} m/s kaymaya devam ediyor. Rampa dibinde uçurum varsa bu düzen yetmez: "
        "tutma freni gerekir. 100 mm eşik ≈ 87 mm'den sığ düşüşü (tek basamak kaldırım) görmez. LiDAR merdiveni hiç görmüyor "
        "(merdivenli ve merdivensiz tarama arasındaki en büyük fark 0,0 mm).",
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
    mj = oku(H / "mujoco.csv")
    vr = oku(H / "varyant_2b.csv")

    def kosul_say(rows):
        d = {}
        for x in rows:
            t = d.setdefault(x["kosul"], [0, 0, x["etken"], int(x["kademe"]), say(x["deger"])])
            t[0] += 1
            t[1] += dogru(x["basari"])
        return d

    a, k = kosul_say(ab), kosul_say(ky)
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
    ortalamalar.append(("Sıradan okul günü (3 kademe)", 100.0 * sum(v[1] for v in okul.values()) / 36,
                        min(v[1] for v in okul.values()), 12))
    ortalamalar.sort(key=lambda x: x[1])
    r["siralama"] = ortalamalar

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
        aciklama="Sıralama bütün kademeleri koşulmuş A'dan B'ye sonuçlarından. Sonuç belgesindeki ilk sıralama kayıp "
                 "robotta eşit olmayan kademe kapsamına dayandığı için bağımsız inceleme onu sağlam bulmadı; sağlam olan, "
                 "kapı, cam ve menzilin her ölçütte ilk dörtte olması.")
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
        "Kayıp robot 60 koşulun 20'sinde koşuldu; koridor genişliği etkeni kayıpta hiç koşulmadı.",
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
    sonuc_var(S, "24/24", "0,048", "20/20", "0,053", "26,5")

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
    satirlar.append(["LiDAR'lı taban (karşılaştırma)", "24/24", "0,048", "ölçülmedi", "0"])
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
    ksat.append(["LiDAR'lı taban (karar)", "20/20", "-", "26,5", "-", "0"])
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
        "<strong>Zayıflık:</strong> rastgele bırakılmadaki tek başarısızlıkta süzgeç ilk saniyede 2,0 m'deki tek bir "
        f"etiketten başlatıldı; koşu boyunca en büyük konum hatası {sy(say(tb['konum_hata_en_m']) if tb else None)} m. "
        "Hiç ret olmadığı için yeniden başlatma tetiklenmedi ve robot 262 s eğik açıyla duvara dayalı kaldı; ön sonar bunu "
        "durdurmadı. Tek etiketten başlatmaya güvenilmemeli.",
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
    sonuc_var(K, "798 / 874 / 982", "530")
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
        "900 s'ye ancak sınırda sığıyor (ölçülen tempoyla beklenen 798 / 874 / 982 s).",
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
        f"<strong>Karar:</strong> çarpma sıfır hedefi yalnız v3'te tutuyor (geliştirme + sınama 2 + sınama 4, sürüm başına "
        f"{top_c['v3'][1]} koşu: v3 {top_c['v3'][0]}, v4 {top_c['v4'][0]}, v5 {top_c['v5'][0]} çarpma). Varsayılan v3'e döndü; "
        "v4 ve v5 isteğe bağlı.",
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
        "2B'de v4 için de \"çarpma sıfır\" sağlanmadı.",
    ]
    hukum = (f"Hız zarfı (v4) labirenti yaklaşık %{tam(100 * (1 - o_gel))} daha kısa sürede bitirdi ama görülmüş kümede 2 "
             f"çarpma verdi. Onarılmış v5 bu ikisini giderdi ve yeni sınama 4'te v3 kadar "
             f"({r['kume'][('sinama4', 'v5')][0]}/20) çözdü, fakat geliştirmede yeni 1 çarpma verdi. Çarpma sıfır yalnız "
             "v3'te tuttuğu için varsayılan v3'e döndü.")
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
def inceleme(R):
    u, h, t, s, d, k = R
    kartlar = []

    def kart(baslik, kapsam, engel, diger, onarim, acik):
        return (
            f"<article class='kart'><header><h3>{baslik}</h3><span class='rozet uyari'>Hüküm: koşullu</span></header>"
            f"<p class='ince'>{kapsam}</p>"
            "<p class='satir-durum'><span class='rozet iyi'>Sayılar CSV'den yeniden sayıldı: tuttu</span> "
            "<span class='rozet iyi'>Sınama verisinin ayara sızması: bulunmadı</span></p>"
            f"<h4>Engelleyici bulgu</h4>{engel}"
            f"<h4>Diğer sorunlar</h4>{liste(diger)}"
            f"<h4>Onarımda ne değişti</h4>{onarim}"
            f"<h4>İnceleme sonrası açık kalanlar</h4>{liste(acik)}"
            "</article>")

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
         "Sonuç belgesinin zarar sırası (\"dönüşsüz > menzil > kapı\") kayıp robottaki eşit olmayan kademe kapsamından "
         "geliyor; sağlam değil. Bu sayfadaki sıralama bütün kademeleri koşulmuş A'dan B'ye sonuçlarından.",
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
table.karar{font-size:.93rem}
table.karar td:first-child{font-weight:600;white-space:nowrap}
table.karar td:nth-child(2){width:46%}
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
ol.olcum{padding-left:22px}
ol.olcum li{margin-bottom:10px}
.olcum .kaynak{display:inline-block;font-size:.75rem;color:var(--soluk);border:1px solid var(--cizgi);border-radius:999px;
padding:0 8px;margin-left:4px}
footer{color:var(--soluk);font-size:.82rem;margin-top:28px}
code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.86em;background:var(--yuzey2);
padding:1px 5px;border-radius:4px}
@media (max-width:720px){
 h1{font-size:1.55rem} section{padding:16px 14px 10px}
 .iki{grid-template-columns:1fr}
 .g-satir{grid-template-columns:1fr}
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


def sayfa(R, govdeler, ustler):
    u, h, t, s, d, k = R
    bugun = _dt.date.today()
    aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    tarih = f"{bugun.day} {aylar[bugun.month - 1]} {bugun.year}"
    kimlik = ["ucurum", "harita", "tasinma", "sanalray", "deneme", "kose"]
    karar_satir = "".join(
        f"<tr><td><a href='#{kid}'>{e(x['test'])}</a></td><td data-etiket='Hüküm'>{x['hukum']}</td>"
        f"<td data-etiket='Gerçek robotta değiştirdiği karar'>{x['karar']}</td></tr>"
        for kid, x in zip(kimlik, ustler))
    bolumler = "".join(
        f"<section id='{kid}'><span class='bolum-no'>Bölüm 2 · Test {i + 1} / 6</span><h2>{e(x['test'])}</h2>{g}</section>"
        for i, (kid, x, g) in enumerate(zip(kimlik, ustler, govdeler)))
    olcumler = [
        ("Uçurum", "Gerçek VL53L1X ile masada: 120 mm yükseklik, 30° eğim, çapraz yön; parlak, siyah ve halı zeminde ve 3 m "
                   "boşlukta okuma. Hangi mesafe kipinde saniyede kaç örnek alındığı (uzun kip payı yaklaşık 2 cm azaltır)."),
        ("Uçurum", "Etkin rampa freniyle (2,0 m/s²) gerçek durma yolu; ilk denemeler 0,25 m/s ile. 10° inişte frenden sonra "
                   "robotun kayıp kaymadığı: kayıyorsa tutma freni gerekir."),
        ("Uçurum", "Altı sensörün aynı I2C hattında adreslenmesi (sensör başına bir XSHUT ucu), sensörler arası etkileşim ve "
                   "etek pencerelerinin ışını kırpıp kırpmadığı."),
        ("Harita", "Okul koridorunda LiDAR'ın dönüş haritası: rota boyunca taramaları kaydedip yüzey türüne göre (cam kapı, cam "
                   "bölme, koyu / parlak kaplama) dönüş vermeyen ışın oranı ve etkin en uzun menzil."),
        ("Harita", "Haritanın ne kadar eskidiği: haritayı bir kez çıkarıp günün farklı saatlerinde aynı yerlerden tarama; "
                   "haritadan 15 cm'den çok sapan nokta oranı, kapı durumu değişimi ve duvar dibindeki eşya sayısı."),
        ("Harita", "Gerçek zeminde (koridor taşı, eşik, ıslak zemin) ani teker kayması sıklığı ve büyüklüğü, yer işaretlerine "
                   "karşı. Not: bu etkenin simülasyondaki \"kırma\" iddiası sınırdaydı."),
        ("Taşınma", "Robot kaldırılırken tekerin dönüp odometriye sahte yol yazıp yazmadığı; taşınma algısının ve 6 haritalı "
                    "baştan konum aramanın Pi 5'teki süresi."),
        ("Sanal ray", "Gerçek koridor ve gerçek ışıkta 15 cm baskı etiketin algılama menzili; hareket bulanıklığı; Pi 5'te "
                      "algılama süresi; tek etiketten başlatmanın güvenilirliği."),
        ("Labirent", "Teker azami hızı (simülasyonda 0,39 m/s tahmin) ve Pi'den ESP32'ye komut gecikmesi (0,15 s tepki payı "
                     "varsayımı); robotu başlangıca koymadaki gerçek yerleştirme hatası (simülasyonda 3 cm / 2°)."),
    ]
    olcum_html = "<ol class='olcum'>" + "".join(
        f"<li>{m} <span class='kaynak'>{e(kay)}</span></li>" for kay, m in olcumler) + "</ol>"
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
<p class="alt-baslik">Robotun simülasyonda geçtiği altı test: ne bulundu, gerçek robotta hangi kararı değiştiriyor.
Bütün sayılar testlerin sonuç tablolarından (CSV) ve sonuç belgelerinden yeniden sayıldı.</p>
</div>
<button id="tema-dugme" type="button">Koyu tema</button>
</div>
<div class="uyari-kutu"><strong>Hepsi simülasyon.</strong> Bağımsız inceleme dört test hattının dördüne de
<strong>koşullu</strong> dedi: sayılar tutuyor ve sınama verisi ayara sızmamış, ama her testin iyimser varsayımları ve
açık kalan işleri var. Bunlar her test bölümünde ve 3. bölümde gizlenmeden yazılı.</div>
<nav class="icindekiler" aria-label="Bölümler">
<a href="#karar">Karar tablosu</a><a href="#ucurum">Uçurum</a><a href="#harita">Harita eskimesi</a>
<a href="#tasinma">Taşınma</a><a href="#sanalray">Sanal ray</a><a href="#deneme">Yeniden deneme</a>
<a href="#kose">Köşe hızı</a><a href="#inceleme">Bağımsız inceleme</a><a href="#olcum">İlk ölçülecekler</a>
</nav>

<section id="karar">
<span class="bolum-no">Bölüm 1</span>
<h2>Karar tablosu</h2>
<div class="tablo-kap"><table class="karar"><thead><tr><th>Test</th><th>Hüküm (tek cümle)</th>
<th>Gerçek robotta değiştirdiği karar</th></tr></thead><tbody>{karar_satir}</tbody></table></div>
</section>

{bolumler}

<section id="inceleme">
<span class="bolum-no">Bölüm 3</span>
<h2>Bağımsız inceleme: hükümler ve bulunan sorunlar</h2>
<p>Her test hattını, onu yürütmeyen ayrı bir inceleme denetledi: sayıları CSV'lerden yeniden saydı, birkaç koşuyu aynı
tohumla yeniden koştu, sınama verisinin ayara sızıp sızmadığına baktı. Bulduğu sorunlar aşağıda olduğu gibi; onarım
yapıldıysa ne değiştiği ve neyin açık kaldığı da.</p>
{inceleme(R)}
</section>

<section id="olcum">
<span class="bolum-no">Bölüm 4</span>
<h2>Gerçek robotta ilk ölçülecekler</h2>
<p>Testlerin kendi önerilerinden. Simülasyondaki sonuçların çoğu bu ölçümlere dayanan varsayımlarla duruyor; sıra,
güvenliği en çok etkileyenden başlıyor.</p>
{olcum_html}
</section>

<footer>
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
    metin = sayfa(sonuclar, govdeler, ustler)
    CIKTI.write_text(metin, encoding="utf-8")
    if "--sayilar" in sys.argv:
        u, h, t, s, d, k = sonuclar
        print("ucurum", {kk: u[kk] for kk in ("ucurum_kosu", "dustu", "yanlis_kosu", "yanlis_durma", "toplam", "hata",
                                              "pay_dar", "pay_genis", "pay_duz_039", "ilk_kosu", "ilk_dustu")},
              u["dar_toplam"], u["gel_4kose"], u["gel_5"], u["gel_6"], u["inis_kayma"])
        print("harita", h["ab_basari"], h["ab_n"], h["okul"], h["okul_k"], h["bas_n"], h["bas_sicrama"], h["bas_vardim"],
              h["bas_emin"], h["bas_sinirda"], h["mj_ayni"], h["mj_n"])
        print("tasinma", t["ab_v3_yanlis_vardim"], t["algi_fark"], t["algi_n"], t["algi_fark_med"], t["ger"])
        print("sanalray", s["ab_b"], s["ab_n"], s["plan5"], s["varis_ort"], s["kayip"])
        print("deneme", d["deneme_sinama2.csv"]["dag"], d["deneme_gelistirme.csv"]["dag"], d["ilk_ayni"])
        print("kose", k["top_c"], {kk: v for kk, v in k["kume"].items() if len(kk) == 2 and kk[1] in ("v3", "v4", "v5")},
              k["s3_uyusmayan"], k["kume"][("gelistirme", "v4", "oran")])
    print(f"yazıldı: {CIKTI.name} ({CIKTI.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
