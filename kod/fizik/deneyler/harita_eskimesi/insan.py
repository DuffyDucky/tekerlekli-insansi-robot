"""Koridordaki insanlar: LiDAR düzleminde (z 0,295 m) bacak çifti olarak görünür (iki daire, r 0,06 m).

- Yürüyen: orta hatta paralel bir şeritte 0,9-1,4 m/s, uçta döner. Robota yol verir: robot önündeki 2 m içinde
  ve şeridine yakınsa yana kayar (en çok duvardan 0,35 m'ye dek); yine de robot gövdesine 0,35 m'den yaklaşacaksa
  durur; 2 s takılı kalırsa geri döner (yürüyen insan robota çarpmaz; robot insana çarpabilir).
- Duran: duvar dibinde (duvardan 0,3-0,5 m), hiç kımıldamaz.
- Grup (yolu kısmen kapatan): 3-4 kişi, bir noktada duvardan `girinti` m içeri dek yan yana durur; robot gruba ilk kez
  3 m yaklaştıktan 30 s sonra dağılır (kaldırılır).
Hepsi harita çerçevesinde yürür; dünyaya `Donusum` ile çevrilir. Rastgelelik tohumlu (numpy Generator)."""

import math

import numpy as np

SURUM = 2                 # 2: robot önünde 2 s takılan yürüyen insan geri döner (1'de kilitlenme: insan da robot da bekliyordu)

BACAK_R = 0.06
BACAK_ARA = 0.10          # her bacak gövde ortasından yana (m)
ADIM_GENLIK = 0.15        # yürürken bacakların öne / arkaya salınımı (m)
YARI_GENISLIK = {"koridor_1": 1.0, "koridor_2": 1.75, "koridor_3": 1.2, "koridor_4": 1.3, "koridor_5": 1.2,
                 "koridor_6": 1.2}


class _Hat:
    def __init__(self, P):
        self.P = [tuple(p) for p in P]
        self.L = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(self.P, self.P[1:])]
        self.boy = sum(self.L)

    def nokta(self, s, yan):
        s = max(0.0, min(self.boy, s))
        for (a, b), L in zip(zip(self.P, self.P[1:]), self.L):
            if s <= L + 1e-9:
                ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                return a[0] + ux * s - uy * yan, a[1] + uy * s + ux * yan, (ux, uy)
            s -= L
        a, b = self.P[-2], self.P[-1]
        L = self.L[-1]
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        return b[0] - uy * yan, b[1] + ux * yan, (ux, uy)


def _govdeye_uzaklik(px, py, poz, hx=0.264, hy=0.2615):
    x, y, th = poz
    c, s = math.cos(th), math.sin(th)
    lx = c * (px - x) + s * (py - y)
    ly = -s * (px - x) + c * (py - y)
    qx = max(-hx, min(hx, lx))
    qy = max(-hy, min(hy, ly))
    return math.hypot(lx - qx, ly - qy), lx, ly


class Kalabalik:
    def __init__(self, sahne, kor, yogunluk=0.0, grup_girinti=0.0, rng=None, engel_uzaklik=None):
        """yogunluk: kişi / 10 m orta hat (%60 yürüyen, %40 duran); grup_girinti > 0: rota ortasında bir grup.
        engel_uzaklik(x, y) -> m: dünya geometrisine (harita çerçevesinde) uzaklık; insan duvara / eşyaya konmasın."""
        self.rng = rng if rng is not None else np.random.default_rng(0)
        self.hw = YARI_GENISLIK[kor]
        self.hatlar = [_Hat(sahne["orta_hat"])]
        if sahne.get("orta_hat_yan_kol"):
            self.hatlar.append(_Hat(sahne["orta_hat_yan_kol"]))
        self.kisiler = []
        top = sum(h.boy for h in self.hatlar)
        n = int(round(yogunluk * top / 10.0))
        uz = engel_uzaklik or (lambda x, y: 9.0)
        for i in range(n):
            for _ in range(200):
                hi = int(self.rng.integers(len(self.hatlar))) if len(self.hatlar) > 1 else 0
                h = self.hatlar[hi]
                s = float(self.rng.uniform(0.5, h.boy - 0.5))
                yuruyen = self.rng.random() < 0.6
                if yuruyen:
                    yan = float(self.rng.uniform(-(self.hw - 0.6), self.hw - 0.6))
                else:
                    yan = float(self.rng.choice([-1, 1]) * (self.hw - self.rng.uniform(0.3, 0.5)))
                x, y, _ = h.nokta(s, yan)
                if uz(x, y) < 0.25:
                    continue
                self.kisiler.append(dict(h=hi, s=s, yan=yan, yan0=yan, yuruyen=yuruyen, takili=0.0,
                                         v=float(self.rng.uniform(0.9, 1.4)), yon=float(self.rng.choice([-1, 1])),
                                         faz=float(self.rng.uniform(0, 2 * math.pi)), aktif=True, grup=False))
                break
        self.grup_basi = None
        if grup_girinti > 0:
            h = self.hatlar[0]
            s = h.boy * float(self.rng.uniform(0.35, 0.55))
            taraf = float(self.rng.choice([-1, 1]))
            k = 3 if grup_girinti < 1.0 else 4
            for j in range(k):
                # duvardan 0,25 m'den girinti'ye dek yan yana
                d = 0.25 + (grup_girinti - 0.25) * (j / max(k - 1, 1))
                yan = taraf * (self.hw - d)
                self.kisiler.append(dict(h=0, s=s + float(self.rng.uniform(-0.25, 0.25)), yan=yan, yan0=yan, takili=0.0,
                                         yuruyen=False, v=0.0, yon=1.0, faz=0.0, aktif=True, grup=True))
            self.grup_merkez = h.nokta(s, taraf * (self.hw - grup_girinti / 2))[:2]
        self.dagilma_t = None

    def adim(self, t, dt, robot_poz):
        """robot_poz: harita çerçevesinde gövde merkezi (hakem tarafı bilgisi; insanların davranışı için)."""
        if self.grup_basi is None and hasattr(self, "grup_merkez"):
            if math.hypot(robot_poz[0] - self.grup_merkez[0], robot_poz[1] - self.grup_merkez[1]) < 3.0:
                self.grup_basi = t
        if self.grup_basi is not None and self.dagilma_t is None and t - self.grup_basi >= 30.0:
            self.dagilma_t = t
            for k in self.kisiler:
                if k["grup"]:
                    k["aktif"] = False
        for k in self.kisiler:
            if not (k["aktif"] and k["yuruyen"]):
                continue
            h = self.hatlar[k["h"]]
            x, y, (ux, uy) = h.nokta(k["s"], k["yan"])
            # robot önümde mi (yürüme yönünde 2 m içinde, şeride 0,8 m'den yakın)
            dx, dy = robot_poz[0] - x, robot_poz[1] - y
            ileri = (dx * ux + dy * uy) * k["yon"]
            yanal = -dx * uy + dy * ux               # robot bana göre hangi yanda (+ hattın solu)
            hedef_yan = k["yan0"]
            if 0 < ileri < 2.5 and abs(yanal) < 0.9:
                # robotun öbür yanına kay
                hedef_yan = k["yan"] + (-0.6 if yanal > 0 else 0.6)
            hedef_yan = max(-(self.hw - 0.35), min(self.hw - 0.35, hedef_yan))
            dyan = max(-0.6 * dt, min(0.6 * dt, hedef_yan - k["yan"]))
            yeni_s = k["s"] + k["yon"] * k["v"] * dt
            yeni_yan = k["yan"] + dyan
            nx, ny, _ = h.nokta(yeni_s, yeni_yan)
            if _govdeye_uzaklik(nx, ny, robot_poz)[0] < 0.35:
                # yalnız yana kayarak geçebiliyorsa ilerleme
                nx2, ny2, _ = h.nokta(k["s"], yeni_yan)
                if _govdeye_uzaklik(nx2, ny2, robot_poz)[0] >= 0.35:
                    k["yan"] = yeni_yan
                k["takili"] += dt
                if k["takili"] >= 2.0:          # robotun önünde takıldı: geri dön
                    k["yon"] = -k["yon"]
                    k["takili"] = 0.0
                continue
            k["takili"] = 0.0
            k["s"], k["yan"] = yeni_s, yeni_yan
            k["faz"] += 2 * math.pi * 0.9 * dt * (k["v"] / 1.1)
            if k["s"] <= 0.3 or k["s"] >= h.boy - 0.3:
                k["yon"] = -k["yon"]
                k["s"] = max(0.3, min(h.boy - 0.3, k["s"]))

    def bacaklar(self):
        """-> (n, 3) dizi (x, y, r) harita çerçevesinde."""
        out = []
        for k in self.kisiler:
            if not k["aktif"]:
                continue
            h = self.hatlar[k["h"]]
            x, y, (ux, uy) = h.nokta(k["s"], k["yan"])
            fx, fy = ux * k["yon"], uy * k["yon"]
            if k["yuruyen"]:
                a = ADIM_GENLIK * math.sin(k["faz"])
            else:
                a = 0.0
            for isaret in (-1, 1):
                out.append((x - fy * BACAK_ARA * isaret + fx * a * isaret,
                            y + fx * BACAK_ARA * isaret + fy * a * isaret, BACAK_R))
        return np.array(out, dtype=float).reshape(-1, 3)

    def sayi(self):
        return dict(surum=SURUM, yuruyen=sum(1 for k in self.kisiler if k["yuruyen"]),
                    duran=sum(1 for k in self.kisiler if not k["yuruyen"] and not k["grup"]),
                    grup=sum(1 for k in self.kisiler if k["grup"]))
