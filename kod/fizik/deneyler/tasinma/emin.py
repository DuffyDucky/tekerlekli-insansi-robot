""""Emin değilim, duruyorum" ölçütü: beyin "vardım" demeden önce kendi belirsizliğini denetler (yalnız mevcut sensör).

    py -3 emin.py          # geliştirme kümesinde (kipler, tohum 7, 8) aday kurallar -> sonuc/emin_secim.json, ekrana

Girdi, `kipler.Gozlemci`'nin "vardım" anındaki kaydı (yalnız beynin gördüğü: tarama, odometri, kendi tahmini):
  sic_maks  koşu boyunca (algi kurtarmasından sonra sıfırlanır) poz tahmininin odometri öngörüsünden en büyük sapması
            (m): konumlayıcının kendi kendine başka yere atlaması
  u_med     son 10 taramada tahmin pozunda tarama-harita uyumu medyanı (ışın ucu harita yüzeyine < 0,20 m oranı)
  g_med     son 10 taramada "duvarın arkasını görme" oranı medyanı (ölçülen menzil beklenenden > 0,5 m uzun)
  std_xy    konumlayıcının ana modunun xy std'si (m), pay: ana mod payı, kk: `konum_kararsiz`
  rast      rastgele saçma yapılan tarama oranı (artırılmış MCL'nin "harita uymuyor" işareti; izleme kipinde hep 0)
Kural: adaylardan birinin (ya da ikisinin VEYA'sı) eşiği aşılırsa "emin değilim": robot "vardım" demez, durur, yardım
bekler. Vardım anında uygulandığı için gidişi değiştirmez: etkisi çevrimdışı, kaydedilmiş koşular üzerinden tam ölçülür
(sessiz hata -> güvenli durma; doğru varış -> gereksiz durma).

Seçim kuralı (sınama kümesine bakmadan önce yazıldı): geliştirme kümesinde gereksiz durma doğru varışların en çok
%2'si; bu sınırda en çok sessiz hatayı yakalayan kural; eşitlikte tek aday > iki aday, sonra daha az gereksiz durma.
İki adaylı kural ancak en iyi tek adaylıdan en az 2 sessiz hata fazla yakalarsa seçilir. Aynı sonucu veren eşik
aralığından ortadaki eşik alınır (geliştirmenin sınırına yapışmamak için).
"""

import glob
import itertools
import json
import os
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
SECIM = os.path.join(BURASI, "sonuc", "emin_secim.json")
GEREKSIZ_EN_COK = 0.02

ADAYLAR = {
    "sic": ("sic_maks", ">", [0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]),
    "uyum": ("u_med", "<", [0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]),
    "gecis": ("g_med", ">", [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]),
    "std": ("std_xy", ">", [0.05, 0.1, 0.15, 0.2, 0.3]),
    "pay": ("pay", "<", [0.5, 0.6, 0.7, 0.8, 0.9]),
    "kk": ("kk", "=", [True]),
    "rast": ("rast", ">", [0.02, 0.05, 0.1, 0.2, 0.3]),
}


def deger(v, alan):
    if alan == "rast":
        return (v.get("rast_n") or 0) / max(v.get("tarama_n") or 1, 1)
    return v.get(alan)


def tek_kosul(v, ad, esik):
    alan, op, _ = ADAYLAR[ad]
    x = deger(v, alan)
    if x is None:
        return False
    if op == ">":
        return x > esik
    if op == "<":
        return x < esik
    return bool(x) == esik


def emin_degil(v, kural):
    """kural: [(aday, eşik), ...] VEYA. v: Gozlemci "vardım" kaydı (None ise: kayıt yok -> karışmaz)."""
    if not v:
        return False
    return any(tek_kosul(v, ad, e) for ad, e in kural)


def uygula(s, kural):
    """Koşu satırı -> ölçüt uygulanınca sonuç türü: dogru_varis | sessiz_hata | guvenli_durma | gereksiz_durma |
    onlenen (sessiz hata yerine güvenli durma) | sure_doldu."""
    if s.get("beyin_bitti") and emin_degil(s.get("vardim"), kural):
        return "onlenen" if s["sonuc"] == "sessiz_hata" else "gereksiz_durma"
    return s["sonuc"]


def say(satir, kural):
    sh = sum(1 for s in satir if s.get("sonuc") == "sessiz_hata")
    dv = sum(1 for s in satir if s.get("sonuc") == "dogru_varis")
    on = sum(1 for s in satir if uygula(s, kural) == "onlenen")
    gd = sum(1 for s in satir if uygula(s, kural) == "gereksiz_durma")
    return dict(sessiz=sh, dogru=dv, onlenen=on, gereksiz=gd)


def kurallar():
    tek = [[(ad, e)] for ad, (_, _, es) in ADAYLAR.items() for e in es]
    cift = [a + b for a, b in itertools.combinations(tek, 2) if a[0][0] != b[0][0]]
    return tek, cift


def sec(satir):
    tek, cift = kurallar()
    dv = sum(1 for s in satir if s.get("sonuc") == "dogru_varis")
    sinir = GEREKSIZ_EN_COK * dv

    def en_iyi(L):
        uygun = []
        for k in L:
            c = say(satir, k)
            if c["gereksiz"] <= sinir:
                uygun.append((c["onlenen"], -c["gereksiz"], k, c))
        uygun.sort(key=lambda x: (x[0], x[1]), reverse=True)
        return uygun
    def orta(L):
        """Eşit sonuçlu (aynı aday, aynı sayılar) eşik aralığının ortasındaki kural (sınırdaki eşik değil)."""
        bas = L[0]
        es = [x for x in L if (x[0], x[1]) == (bas[0], bas[1]) and [a for a, _ in x[2]] == [a for a, _ in bas[2]]]
        es.sort(key=lambda x: [e for _, e in x[2]])
        return es[len(es) // 2]
    T, C = en_iyi(tek), en_iyi(cift)
    secilen = orta(T)
    if C and C[0][0] >= T[0][0] + 2:
        secilen = orta(C)
    return dict(kural=secilen[2], gelistirme=secilen[3], sinir=sinir, en_iyi_tek=[(x[2], x[3]) for x in T[:8]],
                en_iyi_cift=[(x[2], x[3]) for x in C[:8]])


def oku(kume):
    out = []
    for y in sorted(glob.glob(os.path.join(BURASI, "sonuc", "ham", "kipler", kume, "*.json"))):
        with open(y, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def main():
    G = oku("gelistirme")
    if not G:
        print("gelistirme kumesi yok")
        return 1
    r = sec(G)
    r["kume"] = "gelistirme (kipler, tohum 7, 8; v3 ve izleme kipleri; %d kosu)" % len(G)
    os.makedirs(os.path.dirname(SECIM), exist_ok=True)
    with open(SECIM, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    print(json.dumps(dict(kural=r["kural"], gelistirme=r["gelistirme"], sinir=r["sinir"]), ensure_ascii=False))
    print("en iyi tek:")
    for k, c in r["en_iyi_tek"]:
        print("  ", k, c)
    print("en iyi cift:")
    for k, c in r["en_iyi_cift"]:
        print("  ", k, c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
