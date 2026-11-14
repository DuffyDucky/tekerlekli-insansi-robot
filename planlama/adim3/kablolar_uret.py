"""Kablo tablosunun okunur görünümü: planlama/adim3/kablolar.json -> planlama/adim3/kablolar.md.

FreeCAD gerekmez, yalnız standart kütüphane. Tek kaynak JSON'dur; .md elle düzenlenmez.

    py -3 planlama/adim3/kablolar_uret.py            # .md'yi yazar
    py -3 planlama/adim3/kablolar_uret.py --kontrol  # yazmaz; .md güncel değilse çıkış 1

Çıkış kodları: 0 tamam / güncel, 1 güncel değil (--kontrol), 2 kaynak okunamadı.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parents[2]
TABLO = KOK / "planlama/adim3/kablolar.json"
GORUNUM = KOK / "planlama/adim3/kablolar.md"
MALIYET = KOK / "planlama/maliyet.json"
ELEKTRIK = KOK / "planlama/adim3/elektrik.md"


def sayi(x):
    """1376 -> '1.376', 7.5 -> '7,5' (Türkçe yazım)."""
    if isinstance(x, float) and not x.is_integer():
        return f"{x:g}".replace(".", ",")
    return f"{int(x):,}".replace(",", ".")


def dogal(kimlik):
    m = re.match(r"([A-Z]+)(\d+)", kimlik)
    return (m.group(1), int(m.group(2))) if m else (kimlik, 0)


def hucre(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def boy_metni(r):
    b = r.get("boy")
    if not b:
        t = r.get("boy_tahmin")
        if t:
            ek = f"; uç vekili: {t['vekil']}" if t.get("vekil") else ""
            if t.get("uclar"):
                ek = f"; Manhattan {sayi(t['manhattan_mm'])} mm, `{t['kaynak']}`" + ek
            else:
                ek = f"; {t['yontem']} (`{t['kaynak']}`)" + ek
            return f"**{t['etiket']}:** ≤ {sayi(t['mm'])} mm{ek}. " + r.get("boy_not", "")
        return "— (" + r.get("boy_not", "P10.7b'de ölçülecek") + ")"
    parca = []
    for anahtar, ad in (("yol_mm", "yol"), ("onerilen_mm", "önerilen"), ("gereken_mm", "gereken"), ("liste_mm", "liste boyu")):
        if anahtar in b:
            parca.append(f"{ad} {sayi(b[anahtar])} mm")
    metin = " / ".join(parca) + f" (`{b['kaynak']}`)"
    if b.get("not"):
        metin += "; " + b["not"]
    return metin


def kesit_metni(r):
    k = r.get("kesit")
    if k:
        m = f"{k['awg']} AWG ({sayi(k['mm2'])} mm²)"
        return m + (f"; {r['kesit_not']}" if r.get("kesit_not") else "")
    return "— (" + r.get("kesit_not", "yazılı değil") + ")"


def koruma_metni(r, veri):
    k = r.get("koruma")
    if not k:
        return "—"
    e = veri["koruyucular"].get(k)
    if not e:
        return f"`{k}` (tanımsız)"
    akim = f"{sayi(e['akim_a'])} A" if e["akim_a"] is not None else "akım sınırı belgelenmemiş"
    return f"{e['ad']} (`{k}`, {akim})"


def bolge(veri, r):
    """Kablonun ortam bölgesi: kayıttaki bolge, ucu kafadaki bir parçadaysa kafa, değilse demetin bölgesi."""
    o = veri["kesit_kurali"]["ortam"]
    if r.get("bolge"):
        return r["bolge"]
    if any(u.split(" · ")[0] in o["kafa_parcalari"] for d in r["damarlar"] for u in (d["a"], d["b"])):
        return "kafa"
    return o["demet_bolge"].get(r["demet"], "etek")


def katsayi(veri, sicaklik):
    for k in veri["kesit_kurali"]["ortam"]["katsayilar"]:
        if sicaklik <= k["en_cok_c"]:
            return k["k"]
    return None


def kablo_siniri(veri, r):
    """(bölge, sıcaklık, katsayı, düzeltilmiş tablo sınırı A) ya da kesit yoksa sınır None."""
    b = bolge(veri, r)
    t = veri["kesit_kurali"]["ortam"]["bolgeler"][b]["sicaklik_c"]
    k = katsayi(veri, t)
    kural = {x["awg"]: x["en_cok_koruma_a"] for x in veri["kesit_kurali"]["tablo"]}
    s = round(kural[r["kesit"]["awg"]] * k, 2) if r.get("kesit") and r["kesit"]["awg"] in kural and k else None
    return b, t, k, s


def kablo_boy(r):
    """Malzeme hesabındaki boy (mm): ölçüm / CAD alanlarından ilki, yoksa tahmin."""
    if r.get("boy"):
        for k in ("onerilen_mm", "gereken_mm", "liste_mm", "yol_mm"):
            if r["boy"].get(k):
                return r["boy"][k]
    return (r.get("boy_tahmin") or {}).get("mm")


def malzeme_ihtiyac(v):
    """{(tür, renk): mm}: renkli silikon damar başına (− / GND siyah, gerisi kırmızı), sinyal teli damar başına, servo
    uzatması kablo başına; bara saplamaları arasındaki köprüler (bara-pabuc.kopruler) kendi rengiyle. Hazır kablolar ve
    motorun kendi kablosu hesap dışı."""
    t = {}
    for r in v["kablolar"]:
        m = r.get("malzeme")
        if m not in v["malzeme_turleri"] or v["malzeme_turleri"][m].get("hesap_disi"):
            continue
        mt, L = v["malzeme_turleri"][m], kablo_boy(r) or 0
        if mt.get("renkli"):
            for d in r["damarlar"]:
                k = (m, "siyah" if d["ad"] in ("−", "GND") else "kırmızı")
                t[k] = t.get(k, 0) + L
        elif mt.get("damar_basina") is False:
            t[(m, "hepsi")] = t.get((m, "hepsi"), 0) + L
        else:
            t[(m, "hepsi")] = t.get((m, "hepsi"), 0) + L * len(r["damarlar"])
    # bara saplamaları arasındaki köprüler (klemens_turleri.bara-pabuc.kopruler; O-22 a)
    for dugum, k in (v.get("klemens_turleri", {}).get("bara-pabuc", {}).get("kopruler") or {}).items():
        if not isinstance(k, dict):
            continue
        m = "silikon-%d" % k["awg"]
        if m in v["malzeme_turleri"]:
            t[(m, k["renk"])] = t.get((m, k["renk"]), 0) + k["adet"] * k["boy_mm"]
    return t


def kesit_satirlari(veri):
    """Güç dalları için kablo → kesit → koruyan → ortam düzeltmeli sınır; elektrik.md'deki üretilmiş blok da bunu kullanır."""
    y = ["| Kablo | Dal | Kesit | Koruyan | Bölge | Düzeltilmiş sınır | Durum |", "|---|---|---|---|---|---|---|"]
    for r in sorted(veri["kablolar"], key=lambda r: dogal(r["kimlik"])):
        k, kor = r.get("kesit"), veri["koruyucular"].get(r.get("koruma") or "")
        if not kor or (kor["akim_a"] is not None and kor["akim_a"] < 0.01):
            continue
        b, t, kat, s = kablo_siniri(veri, r)
        kes = f"{k['awg']} AWG" if k else "— (kesit bilinmiyor)"
        sinir = f"{sayi(s)} A" if s is not None else "—"
        if r.get("kesit_istisna"):
            sinir += f" (istisna: {r['kesit_istisna']})"
        elif any(e.startswith("kesit-koruma:") for e in r["eksik"]):
            sinir += " (karara bağlı)"
        y.append(f"| {r['kimlik']} | {hucre(r['dal'])} | {kes} | {hucre(koruma_metni(r, veri))} | {b} {t} °C × {sayi(kat)} | "
                 f"{sinir} | {r['durum']} |")
    return y


EL_BAS = "<!-- kablolar_uret.py: dal başına kesit (üretilmiş, elle düzenlenmez) -->"
EL_SON = "<!-- kablolar_uret.py: blok sonu -->"


def elektrik_blogu(veri):
    y = [EL_BAS, "", "## Ek: dal başına kesit (üretilmiş)", "",
         "Bu blok `planlama/adim3/kablolar.json`'dan `py -3 planlama/adim3/kablolar_uret.py` ile yazılır; tek kaynak tablodur, "
         "burada elle değiştirilmez. Kural, kaynaklar ve istisnalar: `planlama/adim3/kablolar.md` §Kesit ve sigorta kuralı "
         "(O-1 c / O-2 a + b, orkestratör 14.11). Gerilim düşümü boylar ölçülünce (P10.7b) sınanır: en yüksek akımda "
         "düşüm > %3 ise bir kalın kesit.", ""]
    return "\n".join(y + kesit_satirlari(veri) + ["", EL_SON]) + "\n"


def elektrik_yaz(metin, veri):
    blok = elektrik_blogu(veri)
    if EL_BAS in metin:
        return metin[:metin.index(EL_BAS)] + blok
    return metin.rstrip("\n") + "\n\n" + blok


def rehber_metni(r):
    if not r["rehber"]:
        return "—"
    return ", ".join(f"{x['no']} {x['kod']}" + (" (öneri)" if x["tur"] == "öneri" else "") for x in r["rehber"])


def damar_uc(d):
    ek = []
    if "gpio" in d:
        ek.append(f"GPIO{d['gpio']} `{d['pin']}`")
    if "pca_kanal" in d:
        ek.append(f"PCA K{d['pca_kanal']} `{d['pca_ad']}`")
    if "ara" in d:
        ek.append("ara: " + d["ara"])
    if d.get("not"):
        ek.append(d["not"])
    return "; ".join(ek)


def uret(veri, maliyet=None):
    if maliyet is None:
        maliyet = json.loads(MALIYET.read_text(encoding="utf-8"))
    K = veri["kablolar"]
    sira = {d: i for i, d in enumerate(veri["demet_sirasi"])}
    satir = []
    y = satir.append
    y("# Lale: kablo tablosu (okunur görünüm)")
    y("")
    y("> **Bu dosya üretilmiştir, elle düzenlenmez.** Tek kaynak `planlama/adim3/kablolar.json`; görünüm "
      "`py -3 planlama/adim3/kablolar_uret.py` ile, denetim `py -3 planlama/adim3/kablolar_denetim.py` ile.")
    y("")
    y(f"Tablo sürümü {veri['surum']}, tarih {veri['tarih']}. {veri['aciklama']}")
    y("")
    y("## Özet")
    y("")
    dur = Counter(r["durum"] for r in K)
    boylu = sum(1 for r in K if r.get("boy"))
    y(f"- **{len(K)} kablo** (çok damarlı demet ve çiftler tek kayıt; damar sayısı {sum(len(r['damarlar']) for r in K)}).")
    y(f"- Durum: kesin {dur.get('kesin', 0)}, kablajda teyit edilecek {dur.get('kablajda teyit edilecek', 0)}, "
      f"karara bağlı {dur.get('karara bağlı', 0)}.")
    y(f"- Boyu CAD'de tasarlanmış yoldan ya da listeden belli: {boylu}; belli değil: {len(K) - boylu} (bunlarda yalnız "
      f"etiketli kaba üst sınır var, `boy_tahmin`: tahmin, P10.7b'de ölçülecek).")
    ist = [r["kimlik"] for r in K if r.get("kesit_istisna")]
    kk = [r["kimlik"] for r in K if any(e.startswith("kesit-koruma:") for e in r["eksik"])]
    y(f"- Kesit kuralının kayıtlı istisnası: {len(ist)} kablo; kesit ↔ koruma uyuşmazlığı karara bağlı: {len(kk)} "
      f"({', '.join(kk) or '-'}).")
    y(f"- Acil stopta enerjili kalan: {sum(1 for r in K if r['acil_stopta_enerjili'])}; enerjisiz: "
      f"{sum(1 for r in K if not r['acil_stopta_enerjili'])}.")
    y("")
    y("| Demet | Kablo | Karara bağlı | Teyit | Kesin |")
    y("|---|---|---|---|---|")
    for d in veri["demet_sirasi"]:
        rr = [r for r in K if r["demet"] == d]
        c = Counter(r["durum"] for r in rr)
        y(f"| {d} | {len(rr)} | {c.get('karara bağlı', 0)} | {c.get('kablajda teyit edilecek', 0)} | {c.get('kesin', 0)} |")
    y("")
    y("## Renk kuralı")
    y("")
    y(veri["renk_kurali"]["ilke"])
    y("")
    y("| Sınıf | Devre | Uç makaronu | Rehber çizimi |")
    y("|---|---|---|---|")
    for ad, s in veri["renk_kurali"]["siniflar"].items():
        y(f"| {ad} | {hucre(s['devre'])} | {s['makaron']} | `{s['cizim']}` |")
    y("")
    y("## Kesit ve sigorta kuralı")
    y("")
    y(veri["kesit_kurali"]["ilke"])
    y("")
    kk = veri["kesit_kurali"]
    y(kk["yalitim_varsayimi"])
    y("")
    y("Kaynaklar (iki kaynak farklıysa küçük değer alınır):")
    y("")
    for ad, s in kk["kaynaklar"].items():
        y(f"- **{ad}:** {s['ad']}, {s['sutun']} sütunu; <{s['url']}> ({s['okundu']} okundu). {s['not']}")
    y("")
    y("| AWG | mm² | CFR | NFPA 79 | En çok koruma | Not |")
    y("|---|---|---|---|---|---|")
    for t in kk["tablo"]:
        d = t["dayanak"]
        y(f"| {t['awg']} | {sayi(t['mm2'])} | {sayi(d['cfr']) + ' A' if d.get('cfr') is not None else '—'} | "
          f"{sayi(d['nfpa79'])} A | **{sayi(t['en_cok_koruma_a'])} A** | {hucre(t['not'])} |")
    y("")
    o = kk["ortam"]
    y(f"**Ortam sıcaklığı düzeltmesi.** {o['ilke']} Kaynak: {o['kaynak']['ad']} (<{o['kaynak']['url']}>, {o['kaynak']['okundu']} "
      f"okundu; {o['kaynak']['not']})")
    y("")
    for b, x in o["bolgeler"].items():
        y(f"- **{b}:** ≤ {x['sicaklik_c']} °C (`{x['kaynak']}`; {x['not']}); katsayı {sayi(katsayi(veri, x['sicaklik_c']))}.")
    y("")
    for i in kk["istisnalar"]:
        y(f"**Kayıtlı istisna `{i['ad']}`** ({', '.join(i['kapsam'])}; {i['karar']}): {i['gerekce']} **Şart:** {i['sart']}. "
          f"**Kontrol:** {i['kontrol']}.")
        if i.get("beklenen_surekli_a"):
            e = i["beklenen_surekli_a"]
            y("")
            y(f"Beklenen sürekli akım (`{e['kaynak']}`): {e['deger']}; tablodaki 25 A'in **{e['esik_25a']}**. {e['not']}")
        if i.get("beklenen_akim_a"):
            e = i["beklenen_akim_a"]
            y("")
            y(f"Beklenen akım (`{e['kaynak']}`):")
            y("")
            y("| Kablo | Hat | Sürekli (yoğun) | Tepe | Bölge | Düzeltilmiş sınır | Altında |")
            y("|---|---|---|---|---|---|---|")
            for x in e["hatlar"]:
                y(f"| {x['kablo']} | {x['hat']} | {sayi(x['surekli_yogun_a'])} A | {sayi(x['tepe_a'])} A | {x['bolge']} | "
                  f"{sayi(x['duzeltilmis_sinir_a'])} A | {'evet' if x['altinda'] else '**hayır**'} |")
            y("")
            y(e["not"])
        y("")
    g = kk["gerilim_dusumu"]
    y(f"**Gerilim düşümü** ({g['karar']}): {g['kural']}; sınama {g['kontrol']}. Alanı taşıyan kablolar: "
      f"{', '.join(r['kimlik'] for r in K if r.get('gerilim_dusumu_kontrol'))}.")
    y("")
    y("### Dal başına kesit")
    y("")
    y("Koruması olan güç dalları (aynı tablo `elektrik.md` sonunda üretilmiş blok olarak durur).")
    y("")
    for s in kesit_satirlari(veri):
        y(s)
    y("")
    y("### Uç türleri: klemens, bara, lehim, fiş (O-3; düzeltme turu 2: her damar ucunun türü uc_turu alanında)")
    y("")
    y("| Tür | Ne | En kalın kablo | Liste | Not |")
    y("|---|---|---|---|---|")
    for ad, t in veri["klemens_turleri"].items():
        sinir = ("klemens değil" if t.get("klemens_degil") else
                 f"{sayi(t['en_cok_mm2'])} mm²" if t["en_cok_mm2"] is not None else "bilinmiyor")
        kul = sorted({r["kimlik"] for r in K for d in r["damarlar"] for x in (d.get("uc_turu") or {}).values() if x == ad}, key=dogal)
        kay = f"`{t['kaynak']}`" if t.get("kaynak") else "—"
        y(f"| `{ad}` | {hucre(t['ad'])} | {sinir} | {kay} | {hucre(t['not'])} Kullanan: {', '.join(kul) or '-'}. |")
    y("")
    y("## Malzeme özeti (sipariş)")
    y("")
    pay = veri["malzeme_payi"]
    y(f"Boy belliyse CAD / liste boyu, değilse kaba üst sınır tahmini; toplam × {sayi(1 + pay)} (%{int(pay * 100)} pay) "
      "`planlama/maliyet.json` adediyle karşılaştırılır (denetimde `malzeme` sınaması). Tahminler P10.7b'de ölçülecek.")
    y("")
    y("| Tür | Renk | İhtiyaç | × pay | Listede | Kalem |")
    y("|---|---|---|---|---|---|")
    kal = maliyet["kalemler"]
    for (m, renk), mm in sorted(malzeme_ihtiyac(veri).items()):
        mt = veri["malzeme_turleri"][m]
        i = mt["maliyet"].get(renk, mt["maliyet"].get("hepsi"))
        birim = mt.get("birim_m", 1)
        liste = f"{kal[i]['adet']} × {birim} m" if birim != 1 else f"{kal[i]['adet']} m"
        if m == "servo-uzatma":
            liste = f"{kal[i]['adet']} × 1 m"
        fiyat = "" if kal[i].get("tl") is not None else " (fiyat bekliyor)"
        y(f"| {mt['ad']} | {renk} | {sayi(round(mm / 1000, 2))} m | {sayi(round(mm / 1000 * (1 + pay), 1))} m | {liste} | "
          f"{i}: {hucre(kal[i]['ad'])}{fiyat} |")
    y("")
    y("## Orkestratör kararları (14.11)")
    y("")
    y("| Kod | Karar | Metin | Tabloda uygulama | Veren |")
    y("|---|---|---|---|---|")
    for x in veri["kararlar"]:
        y(f"| {x['kod']} | {x['karar']} | {hucre(x['metin'])} | {hucre(x['uygulama'])} | {x['veren']} |")
    y("")
    y("## Acil stop dalları ve besleme zinciri")
    y("")
    y(f"Dal ve acil stop bayrağı her kablonun `besleme_zinciri`nden türetilir (aküden kabloya koruyucular / anahtarlar); zincirde "
      f"{' ya da '.join(veri['zinciri_kesen_turler'])} türünde bir eleman varsa kablo acil stopta enerjisizdir. Denetim zinciri "
      f"devrenin ağlarından yeniden kurar ve `{veri['dallar_kaynak']}` listesiyle karşılaştırır.")
    y("")
    y("| Dal | Tanımlayan eleman | §12'deki ifade | Kablo |")
    y("|---|---|---|---|")
    for ad, d in veri["dallar"].items():
        kk = [r["kimlik"] for r in K if r["dal"] == ad]
        y(f"| {ad} | `{d['eleman']}` | {hucre(d['p12'])} | {len(kk)} |")
    y("")
    y("### Koruyucular ve anahtarlar")
    y("")
    y("| Kimlik | Ne | Tür | Akım sınırı | Giriş ağı → çıkış ağı | Kaynak |")
    y("|---|---|---|---|---|---|")
    for kid, e in list(veri["koruyucular"].items()) + list(veri["anahtarlar"].items()):
        akim = "—" if "akim_a" not in e else (f"{sayi(e['akim_a'])} A" if e["akim_a"] is not None else "belgelenmemiş")
        ek = "; ".join(x for x in (e.get("anma") and "anma: " + e["anma"], e.get("sinir_kaynagi"), e.get("not")) if x)
        y(f"| `{kid}` | {hucre(e['ad'])}{(' (' + hucre(ek) + ')') if ek else ''} | {e['tur']} | {akim} | "
          f"{e['giris'] or 'kök'} → {', '.join(e['cikis'])} | `{e['kaynak']}` |")
    y("")
    for kid, e in veri["koruyucular"].items():
        b = e.get("yuk_butcesi")
        if not b:
            continue
        y(f"**`{kid}` yük bütçesi** ({e.get('karar', '')}; {e.get('yer', '')}). {b['not']}")
        y("")
        y("| Yük | Tipik | Tepe | Kaynak |")
        y("|---|---|---|---|")
        for x in b["kalemler"]:
            y(f"| {hucre(x['yuk'])} | {sayi(round(x['tipik_a'], 4))} A | {sayi(round(x['tepe_a'], 4))} A | {hucre(x['kaynak'])} |")
        y(f"| **Toplam** | **{sayi(b['toplam_tipik_a'])} A** | **{sayi(b['toplam_tepe_a'])} A** | |")
        y("")
        y(f"**Açılış:** {b['acilis']} **Pay:** {b['pay']}")
        y("")
    y("## Demet demet (montaj sırasıyla)")
    y("")
    y("Her kablo: devre, iki uç, damarlar uç uç, kesit, renk, koruma, acil stop, boy, rehber adımı, durum ve kaynak.")
    y("Rehber adımı: bugünkü rehber metninde geçen adım; \"öneri\" yazanlar önerilen adım.")
    for d in veri["demet_sirasi"]:
        rr = sorted((r for r in K if r["demet"] == d),
                    key=lambda r: (min((x["no"] for x in r["rehber"]), default=99), dogal(r["kimlik"])))
        if not rr:
            continue
        y("")
        y(f"### {d} ({len(rr)})")
        for r in rr:
            y("")
            y(f"#### {r['kimlik']} · {r['ad']}")
            y("")
            y(f"- **Devre:** {r['devre']} · **dal:** {r['dal']} · **durum:** {r['durum']}")
            y(f"- **Uçlar:** {r['uc_a']['parca']} ({r['uc_a']['nokta']}) → {r['uc_b']['parca']} ({r['uc_b']['nokta']})")
            y(f"- **Kesit:** {kesit_metni(r)} · **renk:** {r['renk']['iletken']}; makaron {r['renk']['makaron']}")
            y(f"- **Koruma:** {koruma_metni(r, veri)} · **acil stopta:** {'enerjili' if r['acil_stopta_enerjili'] else 'enerjisiz'}")
            y("- **Besleme zinciri:** " + " → ".join("(" + " ∥ ".join(x) + ")" if isinstance(x, list) else x
                                                      for x in r["besleme_zinciri"])
              + (f" · **ortak dönüş:** {', '.join(r['ortak_donus'])}" if r.get("ortak_donus") else ""))
            y(f"- **Boy:** {boy_metni(r)}")
            y(f"- **Rehber adımı:** {rehber_metni(r)} · **sonlandırma:** {r['sonlandirma'] or '—'}")
            ut = sorted({(d.get("uc_turu") or {}).get("a", "?") for d in r["damarlar"]}), sorted({(d.get("uc_turu") or {}).get("b", "?") for d in r["damarlar"]})
            y(f"- **Uç türü (uc_turu):** a: {', '.join(ut[0])} · b: {', '.join(ut[1])}")
            if r.get("hazir_kablo"):
                h = r["hazir_kablo"]
                sart = ""
                if h.get("sart"):
                    sart = "; şart: " + ", ".join(f"{k} {v}" for k, v in h["sart"].items())
                y(f"- **Hazır kablo:** {h['tur']}{sart}" + (f" ({h['liste']})" if h.get("liste") else ""))
            y("")
            y("| Damar | Uç A | Uç B | Pin / kanal / not |")
            y("|---|---|---|---|")
            for dm in r["damarlar"]:
                y(f"| {hucre(dm['ad'])} | {hucre(dm['a'])} | {hucre(dm['b'])} | {hucre(damar_uc(dm))} |")
            y("")
            for e in r["eksik"]:
                y(f"- Eksik: {e}")
            for t in r["teyit"]:
                y(f"- Teyit: {t}")
            if r.get("not"):
                y(f"- Not: {r['not']}")
            y(f"- Kaynak: {', '.join('`' + s + '`' for s in r['kaynak'])} · 10.11 dökümü: {', '.join(r['denetim_62'])}")
    y("")
    y("## 10.11 dökümündeki 62 kabloyla eşleme")
    y("")
    y("Döküm, rehberin 10.11 incelemesindeki kablo listesidir (depo dışı). Bölünen: bir döküm satırı birden çok kayda;"
      " birleşen: birden çok döküm satırı bir kayda.")
    y("")
    esle = {}
    for r in K:
        for n in r["denetim_62"]:
            m = re.match(r"#(\d+)", n)
            if m:
                esle.setdefault(int(m.group(1)), []).append(r["kimlik"])
    y("| Döküm # | Tablodaki karşılığı |")
    y("|---|---|")
    for n in range(1, 63):
        if f"#{n}" in veri["denetim_62_disarida"]:
            y(f"| {n} | {hucre(veri['denetim_62_disarida'][f'#{n}'])} |")
        else:
            y(f"| {n} | {', '.join(sorted(set(esle.get(n, [])), key=dogal)) or '**eşleşmedi**'} |")
    yeni = [r["kimlik"] for r in K if any(x.startswith("yeni") for x in r["denetim_62"])]
    y("")
    y(f"Dökümde karşılığı olmayan yeni kayıtlar: {', '.join(yeni)}.")
    y("")
    y("## Orkestratöre (karar gerekenler)")
    y("")
    for o in veri["orkestratore"]:
        kod = re.compile(r"(?<![\w-])" + re.escape(o["kod"].split(" ")[0]) + r"(?![\w])")
        etk = sorted({r["kimlik"] for r in K if any(kod.search(e) for e in r["eksik"])}, key=dogal)
        y(f"- **{o['kod']}:** {o['konu'].rstrip('.')}." + (f" Etkilenen: {', '.join(etk)}." if etk else ""))
        for s in o["secenekler"]:
            y(f"  - {s}")
    y("")
    return "\n".join(satir)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--kontrol", action="store_true", help="yazma; görünüm güncel değilse çıkış 1")
    ap.add_argument("--tablo", type=Path, default=TABLO)
    ap.add_argument("--gorunum", type=Path, default=GORUNUM)
    a = ap.parse_args()
    try:
        veri = json.loads(a.tablo.read_text(encoding="utf-8"))
    except (OSError, ValueError) as h:
        print(f"kaynak okunamadı: {h}")
        return 2
    metin = uret(veri)
    el_eski = ELEKTRIK.read_text(encoding="utf-8")
    el_yeni = elektrik_yaz(el_eski, veri)
    if a.kontrol:
        try:
            eski = a.gorunum.read_text(encoding="utf-8")
        except OSError:
            eski = None
        kotu = 0
        if eski != metin:
            print("kablolar.md güncel değil: py -3 planlama/adim3/kablolar_uret.py")
            kotu = 1
        if el_eski != el_yeni:
            print("elektrik.md'deki dal başına kesit bloğu güncel değil: py -3 planlama/adim3/kablolar_uret.py")
            kotu = 1
        if not kotu:
            print("kablolar.md ve elektrik.md bloğu güncel")
        return kotu
    a.gorunum.write_text(metin, encoding="utf-8", newline="\n")
    if el_eski != el_yeni:
        ELEKTRIK.write_text(el_yeni, encoding="utf-8", newline="\n")
        print("yazıldı: planlama/adim3/elektrik.md (dal başına kesit bloğu)")
    print(f"yazıldı: {a.gorunum.relative_to(KOK) if a.gorunum.is_relative_to(KOK) else a.gorunum} ({len(veri['kablolar'])} kablo)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
