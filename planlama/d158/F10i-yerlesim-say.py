# F10i (P10.7b2a) düzeltme turu 1: anahtarlı bara yerleşim sayımı (F10i-kontrol A10). FreeCAD İSTEMEZ; kayıtları yalnız okur,
# hiçbir dosyaya yazmaz.
#
# Sayılan: anahtarlı baraya (Anahtarlı bara · +) giden iletkenlerin 4 saplamaya dağılışı. Kısıtlar kablolar_denetim.kopru_akimlari
# ile aynı: saplama başına en çok saplama_basina_en_cok_pabuc pabuç, köprü uçları dahil (uç saplamada 1, ortadakilerde 2); besleme
# saplamasında baraya gelen bir hat (damarın b ucu bu düğüm: G09, G11) bulunur. Saplama içindeki sıra (kalın pabuç altta) sayıyı
# değiştirmez: sıra kayıtta kuraldır, seçenek değildir. İki sayı verilir: (1) besleme saplaması seçilmeden, yalnız iletkenlerin
# saplamalara dağılışı; (2) her dağılış × kuralı sağlayan besleme saplaması seçenekleri. Her yerleşimin en kötü köprü akımı
# kablolar_denetim.kopru_akimlari ile hesaplanır.
#
# Koşu: py -3 -B -X utf8 planlama/d158/F10i-yerlesim-say.py
import collections, copy, itertools, json, os, sys

ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROBOT, "planlama", "adim3"))
import kablolar_denetim as KD                                         # noqa: E402

DUGUM = "Anahtarlı bara · +"


def main():
    v = json.load(open(os.path.join(ROBOT, "planlama", "adim3", "kablolar.json"), encoding="utf-8"))
    bp = v["klemens_turleri"]["bara-pabuc"]
    k = bp["kopruler"][DUGUM]
    n = bp["dugumler"][DUGUM]
    m = bp.get("saplama_basina_en_cok_pabuc", 4)
    iletken = sorted(f"{r['kimlik']}/{d['ad']}" for r in v["kablolar"] for d in r["damarlar"] for u in (d["a"], d["b"]) if u == DUGUM)
    besleme = {f"{r['kimlik']}/{d['ad']}" for r in v["kablolar"] for d in r["damarlar"] if d["b"] == DUGUM}
    kapasite = [m - ((1 if i in (1, n) else 2) if n > 1 else 0) for i in range(1, n + 1)]
    kid = KD.sinirlayan(v, v["dugumler"][DUGUM]["ag"])
    dagilis, yerlesim = 0, 0
    en_kotu = collections.Counter()
    for atama in itertools.product(range(1, n + 1), repeat=len(iletken)):
        say = collections.Counter(atama)
        if any(say[i] > kapasite[i - 1] for i in range(1, n + 1)):
            continue
        dagilis += 1
        yer = {str(i): [x for x, a in zip(iletken, atama) if a == i] for i in range(1, n + 1)}
        for bs in range(1, n + 1):
            if not any(x in besleme for x in yer[str(bs)]):
                continue
            yerlesim += 1
            k2 = copy.deepcopy(k)
            k2["yerlesim"], k2["besleme_saplamasi"] = yer, bs
            h = []
            out = KD.kopru_akimlari(v, h, DUGUM, k2, n, kid)
            en_kotu[max(a for _, _, a in out)] += 1
    print("anahtarlı bara: %d iletken (%s), %d saplama, saplama başına en çok %d pabuç (köprü uçları dahil; boş yer %s); "
          "besleme hattı %s" % (len(iletken), ", ".join(iletken), n, m, kapasite, ", ".join(sorted(besleme))))
    print("iletken dağılışı (besleme saplaması seçilmeden): %d" % dagilis)
    print("geçerli yerleşim (dağılış × besleme hattı taşıyan besleme saplaması): %d" % yerlesim)
    print("en kötü köprü akımı dağılımı: %s" % ", ".join("%g A: %d" % (a, c) for a, c in sorted(en_kotu.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
