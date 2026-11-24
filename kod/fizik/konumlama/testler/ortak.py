"""Test yardımcıları: sentetik koridor haritası, ölçüm kaydı."""

import math

OLCUMLER = []      # (test, ad, değer) — koşucu sonunda tablo olarak yazar


def kaydet(test, ad, deger):
    OLCUMLER.append((test, ad, deger))


def koridor(ad, uzunluk=20.0, genislik=2.4, kapilar=(), nis=0.8, baslangic=(1.5, None, 0.0), engeller=()):
    """Düz koridor (harita sözlüğü). kapilar: [(x_merkez, "alt" | "ust", genislik)], her kapının arkasında
    `nis` derinliğinde kapalı bir girinti. Koridor y = nis .. nis + genislik bandında."""
    y0, y1 = nis, nis + genislik
    duvarlar = [[0.0, y0, 0.0, y1], [uzunluk, y0, uzunluk, y1]]
    for taraf, y, ydis in (("alt", y0, 0.0), ("ust", y1, y1 + nis)):
        bosluklar = sorted((x - g / 2, x + g / 2) for x, t, g in kapilar if t == taraf)
        x = 0.0
        for a, b in bosluklar:
            duvarlar.append([x, y, a, y])
            duvarlar += [[a, y, a, ydis], [a, ydis, b, ydis], [b, ydis, b, y]]
            x = b
        duvarlar.append([x, y, uzunluk, y])
    bx, by, bt = baslangic
    return {"ad": ad, "aciklama": "test koridoru", "boyut_m": [uzunluk, genislik + 2 * nis], "cevre_duvari": False,
            "duvarlar": duvarlar, "engeller": list(engeller),
            "baslangic": {"x": bx, "y": by if by is not None else (y0 + y1) / 2, "aci_derece": math.degrees(bt)}}


def kare_oda(ad="kare_oda", kenar=5.0):
    return {"ad": ad, "boyut_m": [kenar, kenar], "duvarlar": [], "engeller": [],
            "baslangic": {"x": kenar / 2, "y": kenar / 2, "aci_derece": 0}}
