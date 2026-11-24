"""Labirent hakemi: yalnız yer gerçeğine (gövde merkezi pozu + temas bayrağı) bakar, robota hiçbir şey söylemez.

    from hakem import Hakem                 # kod/fizik/labirent sys.path'te
    h = Hakem("labirent_9x9_t1")            # ya da 3B sahne sözlüğü; sure_siniri_s=900.0, ayar={...}
    her denetim adımında: h.guncelle(t, (x, y, th), dunya.temas_engel())
    h.bitti -> True olunca h.sonuc

Kurallar (eşiklerin gerekçesi BENIOKU.md "Hakem"):
- basari: gövde merkezi FINISH çizgisini içeriden dışarı geçer (çizginin `histerezis_m` dışına çıkınca onaylanır).
- fail_start: gövde merkezi START çizgisini içeriden dışarı geçer (aynı histerezis). Robot START'ta çizginin 0,45 m içinde,
  içeri bakarak başlar; arka dingil etrafında yerinde dönüş merkezi çizgiye en çok 0,08 m yaklaştırır: yanlış tetik yok.
- fail_sure: t - t0 >= sure_siniri_s (t0 = ilk guncelle çağrısının t'si). Aynı adımda FINISH geçişi önce gelir.
- fail_sikisma: (a) hareketsiz: son `sikisma_pencere_s` boyunca arka dingil noktası pencere başındaki yerinden
  `sikisma_yaricap_m`'den fazla uzaklaşmadı (yerinde dönüp durmak, duvara dayanıp teker çevirmek dahil); ya da
  (b) ilerlemesiz: `ilerlemesiz_s` boyunca yeni hücreye girilmedi.
- Çarpma: temas_var False -> True geçişi bir olay; önceki temasın bitişinden `carpma_birlestir_s` içinde yeniden başlayan
  temas aynı olayın devamı (sürekli sürtünme tek olay). Temas süresi örnekler arası dt ile toplanır.
Sonuç sözlüğü ve puan: puan.py (formülün tek yeri).
"""

import importlib.util
import json
import math
import os

BURASI = os.path.dirname(os.path.abspath(__file__))
SAHNELER = os.path.join(os.path.dirname(BURASI), "sahneler")


def _yukle(ad):
    spec = importlib.util.spec_from_file_location("lale_labirent_" + ad, os.path.join(BURASI, ad + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


U = _yukle("uretici")
P = _yukle("puan")

AYAR = {
    "histerezis_m": 0.05,            # çizginin bu kadar dışına çıkınca geçiş onaylanır
    "cizgi_uc_payi_m": 0.10,         # açıklık çizgisinin uçlarından yana tolerans
    "sikisma_pencere_s": 60.0,
    "sikisma_yaricap_m": 0.20,
    "ilerlemesiz_s": 300.0,
    "carpma_birlestir_s": 1.0,
    "ornek_aralik_s": 0.25,          # sıkışma penceresi için örnekleme
    "arka_dingil_m": U.ARKA_DINGIL_M,
}


def sahne_yukle(sahne):
    if isinstance(sahne, dict):
        return sahne
    yol = sahne if os.path.isabs(sahne) else os.path.join(SAHNELER, sahne if sahne.endswith(".json") else sahne + ".json")
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


class Hakem:
    def __init__(self, sahne, sure_siniri_s=900.0, ayar=None):
        self.sahne = sahne_yukle(sahne)
        if "labirent" not in self.sahne:
            raise ValueError("sahnede `labirent` alanı yok: %s" % self.sahne.get("ad"))
        self.ayar = dict(AYAR, **(ayar or {}))
        bilinmeyen = set(ayar or {}) - set(AYAR)
        if bilinmeyen:
            raise KeyError("bilinmeyen hakem ayarı: %s" % sorted(bilinmeyen))
        self.T = float(sure_siniri_s)
        L = self.L = self.sahne["labirent"]
        self.lab, self.yer = U.labirent_sahneden(self.sahne)
        self.h = L["hucre_m"]
        self.toplam_hucre = L["satir"] * L["sutun"]
        self.cozum_m = L["cozum_uzunlugu_m"]
        # jeodezik uzaklık alanı: hücre -> FINISH hücresine adım. Her hücrenin iskeleti: merkezden her açık kenarın ortasına
        # yarım kenar; FINISH'e giden yarım kenar "cikis", öbürleri (çocuk dallar, START açıklığı) "dal".
        self.d_hucre = self.lab.mesafeler(self.lab.finish[1])
        self.iskelet = {}
        fhc = self.lab.finish[1]
        fbit = U.KENAR_BIT[self.lab.finish[0]]
        for hc, d in self.d_hucre.items():
            r, c = hc
            yk = []
            for bit, (dr, dc) in U.YON.items():
                if not self.lab.acik[r][c] & bit:
                    continue
                u = (float(dc), float(-dr))                 # satır aşağı = -y
                n = (r + dr, c + dc)
                cikis = (hc == fhc and bit == fbit) or (n in self.d_hucre and self.d_hucre[n] == d - 1)
                yk.append((u, cikis))
            self.iskelet[hc] = yk
        self.cizgi = {}
        for k in ("start", "finish"):
            (ax, ay), (bx, by) = L[k]["cizgi"]
            n = L[k]["ic_normal"]
            self.cizgi[k] = ((ax + bx) / 2, (ay + by) / 2, n[0], n[1], -n[1], n[0], math.hypot(bx - ax, by - ay) / 2)
        sx, sy, _ = L["start"]["poz"]
        self.g0 = self.jeodezik(sx, sy)
        # durum
        self.bitti = False
        self._durum = None
        self.t0 = self.t_son = None
        self.t_bitis = None
        self.poz_son = None
        self.yol_m = 0.0
        self.carpma_sayisi = 0
        self.carpma_suresi_s = 0.0
        self._temas = False
        self._temas_bitis_t = None
        self.ziyaret = set()
        self.t_yeni_hucre = None
        self.p_en = 0.0
        self._ornek = []
        self._son_ornek_t = None
        self._sinir_disi = False
        self.sikisma_sebebi = None
        self.olaylar = []

    # ------------------------------------------------------------ geometri
    def jeodezik(self, x, y):
        """FINISH çizgisine labirent içinden uzaklık (m). Labirent dışı: FINISH önündeyse 0, değilse g0 (ilerleme yok)."""
        hc = self.yer.hucre(x, y)
        if hc is None:
            fx, fy, nx, ny, tx, ty, yari = self.cizgi["finish"]
            if (x - fx) * nx + (y - fy) * ny <= 0 and abs((x - fx) * tx + (y - fy) * ty) <= yari + self.ayar["cizgi_uc_payi_m"]:
                return 0.0
            return getattr(self, "g0", float("inf"))
        cx, cy = self.yer.merkez(hc)
        en = None
        for (ux, uy), cikis in self.iskelet[hc]:            # en yakın yarım kenara izdüşüm
            s = max(0.0, min(self.h / 2, (x - cx) * ux + (y - cy) * uy))
            e = math.hypot(x - cx - ux * s, y - cy - uy * s)
            if en is None or e < en[0] - 1e-12:
                en = (e, s, cikis)
        _, s, cikis = en
        return self.d_hucre[hc] * self.h + self.h / 2 + (-s if cikis else s)

    def _isaretli(self, k, x, y):
        """(çizgiye işaretli uzaklık, + içeri; yanal konum)."""
        cx, cy, nx, ny, tx, ty, yari = self.cizgi[k]
        return (x - cx) * nx + (y - cy) * ny, (x - cx) * tx + (y - cy) * ty, yari

    def _gecti(self, k, x, y):
        s, u, yari = self._isaretli(k, x, y)
        return s < -self.ayar["histerezis_m"] and abs(u) <= yari + self.ayar["cizgi_uc_payi_m"]

    # ------------------------------------------------------------ güncelleme
    def _olay(self, t, tur, **ek):
        e = {"t": round(t - self.t0, 3), "tur": tur}
        e.update(ek)
        self.olaylar.append(e)

    def _bitir(self, t, durum, **ek):
        self.bitti = True
        self._durum = durum
        self.t_bitis = t
        self._olay(t, durum, **ek)

    def guncelle(self, t, gercek_poz, temas_var):
        if self.bitti:
            return
        x, y, th = float(gercek_poz[0]), float(gercek_poz[1]), float(gercek_poz[2])
        t = float(t)
        if self.t0 is None:
            self.t0 = self.t_son = t
            self.poz_son = (x, y)
            self.t_yeni_hucre = t
            self._olay(t, "baslangic", x=round(x, 3), y=round(y, 3))
        dt = max(0.0, t - self.t_son)
        self.yol_m += math.hypot(x - self.poz_son[0], y - self.poz_son[1])
        # çarpma
        if temas_var:
            self.carpma_suresi_s += dt if self._temas else 0.0
            if not self._temas:
                if self._temas_bitis_t is None or t - self._temas_bitis_t > self.ayar["carpma_birlestir_s"]:
                    self.carpma_sayisi += 1
                    self._olay(t, "carpma", n=self.carpma_sayisi, x=round(x, 3), y=round(y, 3))
            self._temas = True
        else:
            if self._temas:
                self.carpma_suresi_s += dt
                self._temas_bitis_t = t
            self._temas = False
        self.t_son = t
        self.poz_son = (x, y)
        # hücre ve ilerleme
        hc = self.yer.hucre(x, y)
        if hc is not None and hc not in self.ziyaret:
            self.ziyaret.add(hc)
            self.t_yeni_hucre = t
        self.p_en = max(self.p_en, 1.0 - self.jeodezik(x, y) / self.g0)
        if hc is None and not self._sinir_disi:
            if not any(abs(self._isaretli(k, x, y)[1]) <= self._isaretli(k, x, y)[2] + 0.5 for k in self.cizgi):
                self._sinir_disi = True
                self._olay(t, "sinir_disi_uyari", x=round(x, 3), y=round(y, 3),
                           not_="govde merkezi aciklik disinda labirent disinda (duvar delinmis olabilir)")
        # sonuç kuralları (öncelik: FINISH, START, süre, sıkışma)
        if self._gecti("finish", x, y):
            self._bitir(t, "basari")
            return
        if self._gecti("start", x, y):
            self._bitir(t, "fail_start")
            return
        if t - self.t0 >= self.T:
            self._bitir(t, "fail_sure")
            return
        a = self.ayar
        if self._son_ornek_t is None or t - self._son_ornek_t >= a["ornek_aralik_s"] - 1e-9:
            ax, ay = x - a["arka_dingil_m"] * math.cos(th), y - a["arka_dingil_m"] * math.sin(th)
            self._ornek.append((t, ax, ay))
            self._son_ornek_t = t
            while len(self._ornek) > 1 and t - self._ornek[1][0] >= a["sikisma_pencere_s"]:
                self._ornek.pop(0)
            t_ilk, x_ilk, y_ilk = self._ornek[0]
            if t - t_ilk >= a["sikisma_pencere_s"] - 1e-9:
                r = max(math.hypot(px - x_ilk, py - y_ilk) for _, px, py in self._ornek)
                if r < a["sikisma_yaricap_m"]:
                    self.sikisma_sebebi = "hareketsiz"
                    self._bitir(t, "fail_sikisma", sebep="hareketsiz", pencere_s=a["sikisma_pencere_s"],
                                en_cok_uzaklasma_m=round(r, 3))
                    return
        if t - self.t_yeni_hucre >= a["ilerlemesiz_s"]:
            self.sikisma_sebebi = "ilerlemesiz"
            self._bitir(t, "fail_sikisma", sebep="ilerlemesiz", yeni_hucresiz_s=round(t - self.t_yeni_hucre, 2))

    # ------------------------------------------------------------ sonuç
    @property
    def sure_s(self):
        if self.t0 is None:
            return 0.0
        return (self.t_bitis if self.bitti else self.t_son) - self.t0

    @property
    def sonuc(self):
        """Bitince kesin sonuç; bitmeden çağrılırsa ara durum (`durum` None, puan o anki fail_sure varsayımıyla)."""
        durum = self._durum
        p_durum = durum or "fail_sure"
        toplam, dokum = P.puan(p_durum, self.sure_s, self.p_en, self.carpma_sayisi, self.carpma_suresi_s, T=self.T)
        return {
            "durum": durum,
            "sure_s": round(self.sure_s, 3),
            "yol_m": round(self.yol_m, 3),
            "carpma_sayisi": self.carpma_sayisi,
            "carpma_suresi_s": round(self.carpma_suresi_s, 3),
            "kesfedilen_hucre": len(self.ziyaret),
            "toplam_hucre": self.toplam_hucre,
            "cozum_uzunlugu_m": self.cozum_m,
            "yol_verimi": round(min(1.0, self.cozum_m / self.yol_m), 4) if self.yol_m > 1e-9 else 0.0,
            "p_en": round(self.p_en, 4),
            "sikisma_sebebi": self.sikisma_sebebi,
            "puan": round(toplam, 2),
            "puan_dokumu": {k: round(v, 2) for k, v in dokum.items()},
            "olaylar": list(self.olaylar),
            "sahne": self.sahne.get("ad"),
        }
