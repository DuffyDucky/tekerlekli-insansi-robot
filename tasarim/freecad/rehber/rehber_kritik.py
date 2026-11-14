# 3B montaj rehberi: onaylı kritik metin kaydı (P10.7b1 açık işler turu, F10h-kontrol-2 §3.1). FreeCAD İSTEMEZ (yalnız standart
# kütüphane: os, re, json, hashlib, difflib).
#
# Amaç: güvenlik açısından kritik her cümlenin / kural listesinin ham hâlinin (yer tutucular çözülmeden) özeti izlenen bir dosyada
# (rehber_kritik_onay.json) tutulur. rehber_denetim.py --kaynak (ve rehber_kablo.py) bugünkü kaynağı bu kayıtla karşılaştırır: değişen,
# silinen ya da eklenen kritik girdi HATA verir ve eski / yeni hâlini yazar. Kayıt yalnız bilinçli bir adımla yenilenir:
# `rehber_denetim.py --kritik-onay-yenile` (çıktısı: "bu değişiklik bağımsız kontrolden geçmeli"). Denetimin olağan koşusu kaydı asla
# yazmaz. Bu, metnin doğru olduğunu kanıtlamaz (onu bağımsız kontrol yapar); kritik bir cümlenin sessizce değişmesini imkânsız kılar.
import os, re, json, hashlib, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
ONAY_DOSYASI = os.path.join(HERE, "rehber_kritik_onay.json")


def tr_kucuk(s):
    """Türkçe duyarlı küçük harf (İ → i, I → ı). Büyük harf Latin kısaltmalar (GPIO, I2C, MOSFET) İngilizce kuralla küçülür."""
    s = re.sub(r"\b[A-Z0-9]*I[A-Z0-9]*\b", lambda m: m.group(0).lower(), s or "")
    return s.replace("İ", "i").replace("I", "ı").lower()


def normal(s):
    """Özet için boşluk normalleştirme (dar / bölünmez boşluk ve satır sonu tek boşluk); harf ve noktalama korunur."""
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ").replace(" ", " ").replace(" ", " ")).strip()


def ozet(s):
    return hashlib.sha256(normal(s).encode("utf-8")).hexdigest()[:16]


def girdi(yer, metin, neden):
    return dict(yer=yer, ozet=ozet(metin), bas=normal(metin)[:60], neden=neden, metin=normal(metin))


class KayitHatasi(Exception):
    """Kayıt (onay kaydı ya da denetimin okuduğu tablo) okunamadı: çağıran düzgün Türkçe ileti yazar ve çıkış 1 verir (traceback yok;
    düzeltme turu 2, F10h-kontrol-3 §3.2)."""


def oku(yol=ONAY_DOSYASI):
    """Kayıt; dosya yoksa None (karşılaştırma "kayıt yok" farkı verir). Bozuk / boş JSON ya da beklenmeyen yapı KayitHatasi."""
    if not os.path.exists(yol):
        return None
    try:
        with open(yol, encoding="utf-8") as f:
            K = json.load(f)
    except (ValueError, UnicodeDecodeError) as e:
        raise KayitHatasi("onay kaydı okunamadı (%s): bozuk ya da boş JSON (%s). Kayıt elle düzenlenmez; depodaki son hâline dön "
                          "(git) ya da bilinçli olarak `rehber_denetim.py --kritik-onay-yenile` ile yenile" % (os.path.basename(yol), e))
    B = K.get("bolumler") if isinstance(K, dict) else None
    if not isinstance(B, dict) or not all(isinstance(v, list) and all(isinstance(g, dict) and "yer" in g and "ozet" in g for g in v)
                                          for v in B.values()):
        raise KayitHatasi("onay kaydı okunamadı (%s): beklenen yapı {\"bolumler\": {bölüm: [{yer, ozet, …}]}} değil"
                          % os.path.basename(yol))
    return K


def yaz(kayit, yol=ONAY_DOSYASI):
    """kayit: {bolum: [girdi]}. Düzeltme turu 2 (F10h-kontrol-3 §3.2): tam metin de yazılır (fark satırı eski hâli bundan gösterir;
    karar yine özetten: metin alanı elle değişirse özet tutmaz ve fark verir)."""
    out = {"aciklama": "Onaylı kritik metin kaydı (rehber_kritik.py). Elle düzenlenmez; yalnız `rehber_denetim.py --kritik-onay-yenile` "
                       "yazar ve her yenileme bağımsız kontrolden geçmelidir.",
           "bolumler": {b: [{k: g[k] for k in ("yer", "ozet", "neden", "metin")} for g in lst] for b, lst in sorted(kayit.items())}}
    with open(yol, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")


def _tam(g):
    """Girdinin tam metni; kayıttaki metin özetle tutmuyorsa (elle değişmiş) bu açıkça yazılır."""
    if not g:
        return ""
    m = g.get("metin")
    if m is None:
        return (g.get("bas") or "") + "… (kayıtta tam metin yok)"
    return m if ozet(m) == g["ozet"] else m + " [UYARI: kayıttaki metin özetle tutmuyor, kayıt elle değişmiş]"


def karsilastir(eski, yeni):
    """eski: dosyadaki {bolum: [girdi]}; yeni: bugünkü {bolum: [girdi]}. Doner [dict(bolum, yer, tur, eski, yeni)].
    Yer başına sıra korunarak karşılaştırılır (difflib): değişen, silinen, eklenen kritik girdi."""
    out = []
    if eski is None:
        return [dict(bolum="-", yer="-", tur="kayıt yok", eski="", yeni="rehber_kritik_onay.json okunamadı")]
    E = eski.get("bolumler", {})
    for b in sorted(set(E) | set(yeni)):
        ye = {}
        for g in E.get(b, []):
            ye.setdefault(g["yer"], []).append(g)
        yy = {}
        for g in yeni.get(b, []):
            yy.setdefault(g["yer"], []).append(g)
        for yer in sorted(set(ye) | set(yy)):
            a, c = ye.get(yer, []), yy.get(yer, [])
            sm = difflib.SequenceMatcher(None, [g["ozet"] for g in a], [g["ozet"] for g in c], autojunk=False)
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == "equal":
                    continue
                tur = {"replace": "değişti", "delete": "silindi", "insert": "eklendi"}[op]
                n = max(i2 - i1, j2 - j1)
                for k in range(n):
                    ge = a[i1 + k] if i1 + k < i2 else None
                    gy = c[j1 + k] if j1 + k < j2 else None
                    out.append(dict(bolum=b, yer=yer, tur=tur if (ge and gy) else ("silindi" if ge else "eklendi"),
                                    eski=_tam(ge), yeni=_tam(gy)))
    return out
