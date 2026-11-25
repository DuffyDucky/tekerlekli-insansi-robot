"""Sanal ray Beyni (ALGORİTMA tarafı): yer gerçeğini görmez. Girdi: enkoder artımı (arka dingil), kafa kamerası gri
görüntüsü (10 Hz), ön sonar tek mesafe (gövde ön yüzünden, m). Bilinen ön bilgi: etiket planı (kimlik -> duvardaki yer,
boy) ve koridor rota çizgesi (sahne JSON `orta_hat`; sanal ray). LiDAR yok.

Görev "ab": bilinen başlangıç pozundan hedef durağa. Görev "kayip": konumunu ve koridorunu bilmeden başlar; güvenli arama
(yerinde dönerek ya da kafayı çevirerek tarama, sonra sonarla yavaş ilerleme), ilk etiketle konum + koridor, sonra hedef.

Kafa: "sabit" (pan 0) ya da "tarayan": A'dan B'ye giderken tahmini poza göre görüş alanındaki en uygun etikete bakar;
aramada kafayı -90..+90 tarar. Pan açısını Beyin kendi servo modeliyle izler (90°/s, protokol servo tablosu); ölçüm yalnız
kafa durmuşken kullanılır."""

import math

from sanalray import kamera as KM
from sanalray.konum import Ayar as KonumAyar, EtiketEKF, sar
from gezinme.izleyici import IzleyiciAyar, YolIzleyici

PAN_HIZ = math.radians(90.0)       # rad/s (protokol.json servolar kafa_pan hiz_derece_s)
PAN_SINIR = math.radians(80.0)
DUR_BAK_S = 0.6
# yerinde dönüş tavanı 0,5 rad/s (izleyici varsayılanı 0,8): bulanıklık 0,89 x 0,5 rad/s x 10 ms x 866 px ≈ 3,9 px
IZLEYICI_VARSAYILAN = dict(w_yerinde=0.5)


class SanalRayBeyni:
    def __init__(self, etiketler, K, gorev="ab", koridor=None, baslangic=None, hedef=None, kafa="sabit",
                 konum_ayar=None, izleyici_ayar=None, rota_fn=None, durak_fn=None):
        """etiketler: {kimlik: {"x","y","z","yaw","boy_m","koridor"}} (bütün koridorların planları; kimlikler tekil).
        K: kamera iç parametresi (işleme çözünürlüğünde). gorev "ab": koridor, baslangic (gövde pozu), hedef (tam durak
        adı) gerekir. "kayip": hedef göreli ("kapi_2"); koridor ilk etiketten. rota_fn(kor, bas_xy, hedef_xy) ve
        durak_fn(kor, ad) -> (tam, xy): gezinme.rota."""
        from gezinme import rota as R
        self.rota_fn = rota_fn or R.rota
        self.durak_fn = durak_fn or R.durak_coz
        self.E = etiketler
        self.K = K
        self.gorev = gorev
        self.kafa = kafa
        self.bul = KM.Bulucu()
        self.ekf = EtiketEKF(etiketler, konum_ayar)
        self.izleyici = YolIzleyici(izleyici_ayar or IzleyiciAyar(**IZLEYICI_VARSAYILAN))
        self.koridor = koridor
        self.hedef_ad = hedef
        self.hedef = None
        self.yol = []
        self.k = None
        self.mod = "baslangic"
        self.pan_istek = 0.0
        self.pan_model = 0.0
        self._pan_durdu_t = 0.0
        self._t = 0.0
        self.olaylar = []
        self.olcum_sayisi = 0
        self.ret_sayisi = 0
        self.ilk_etiket_t = None
        self.lokalize_t = None
        self._son_gorulen = {}
        self._gaz_t = -1e9
        self.son_sonar = None
        # arama durumu
        self._ara = None
        if gorev == "ab":
            self.ekf.baslat(baslangic, std=(0.10, 0.10, math.radians(3.0)))
            self._rota_kur()
        else:
            self.mod = "ara"

    # ------------------------------------------------------------ yardımcılar
    def _olay(self, s):
        self.olaylar.append([round(self._t, 2), s])

    def _rota_kur(self):
        tam, hxy = self.durak_fn(self.koridor, self.hedef_ad)
        self.hedef_ad, self.hedef = tam, hxy
        p = self.ekf.govde()
        self.yol = self.rota_fn(self.koridor, p[:2], hxy)
        self.izleyici.yol_ver(self.yol)
        self.mod = "izle"

    def _pan_guncelle(self, dt):
        d = sar(self.pan_istek - self.pan_model)
        adim = PAN_HIZ * dt
        if abs(d) <= adim:
            if self.pan_model != self.pan_istek:
                self._pan_durdu_t = self._t
            self.pan_model = self.pan_istek
        else:
            self.pan_model += math.copysign(adim, d)

    def _pan_durgun(self, sure=0.25):
        return self.pan_model == self.pan_istek and self._t - self._pan_durdu_t >= sure

    def _kare_isle(self, kare):
        """Algıla, poz kestir; dönen: [(kimlik, menzil, kerteriz, psi)] (yalnız planda olan kimlikler)."""
        if kare is None:
            return []
        _, g = kare
        out = []
        for kimlik, kose in self.bul.bul(g):
            e = self.E.get(kimlik)
            if e is None:
                continue
            ps = self.bul.poz(kose, e["boy_m"], self.K)
            if ps is None:
                continue
            r, b, psi = KM.olcum_2b(*ps)
            out.append((kimlik, r, b, psi))
        return out

    # ------------------------------------------------------------ ana döngü
    def adim(self, t, artim, kare, sonar):
        dt = max(0.0, t - self._t) if self._t else 0.05
        self._t = t
        self.son_sonar = sonar
        self._pan_guncelle(dt)
        self.ekf.tahmin(artim)
        if self._ara is not None:
            self._ara_artim(artim)
        olcumler = self._kare_isle(kare) if (kare is not None and self._pan_durgun()) else []
        if olcumler and self.ilk_etiket_t is None:
            self.ilk_etiket_t = t
            self._olay("ilk etiket %s" % [o[0] for o in olcumler])
        for kimlik, r, b, psi in sorted(olcumler, key=lambda o: o[1]):
            if not self.ekf.hazir:
                if r <= self.ekf.a.baslat_en_cok_menzil:
                    self.ekf.baslat_etiketten(kimlik, r, b, psi, self.pan_model)
                    self.lokalize_t = t
                    self.koridor = self.E[kimlik].get("koridor", self.koridor)
                    self._olay("lokalize: etiket %d, koridor %s, %.2f m" % (kimlik, self.koridor, r))
                continue
            s = self.ekf.olcum(kimlik, r, b, psi, self.pan_model, t)
            if s == "kabul":
                self.olcum_sayisi += 1
                self._son_gorulen[kimlik] = t
            elif s == "ret":
                self.ret_sayisi += 1
        # takılı kalmış yanlış konum: kapı arka arkaya reddediyorsa yakın etiketten yeniden başlat
        if self.ekf.hazir and self.ekf.ardisik_ret >= 6 and olcumler:
            k_, r_, b_, p_ = min(olcumler, key=lambda o: o[1])
            if r_ <= self.ekf.a.baslat_en_cok_menzil:
                self.ekf.baslat_etiketten(k_, r_, b_, p_, self.pan_model)
                self.ekf.ardisik_ret = 0
                self._olay("yeniden baslatildi: etiket %d" % k_)
        if self.gorev == "kayip" and self.mod == "ara" and self.ekf.hazir:
            self._ara = None
            self.pan_istek = 0.0
            self._rota_kur()
            self._olay("rota kuruldu -> %s" % self.hedef_ad)
        if self.mod == "ara":
            return self._ara_komut(sonar)
        # rota izleme
        if self.kafa == "tarayan":
            self._bakis_sec()
        on = sonar if (sonar is not None and math.isfinite(sonar)) else None
        onceki = self.k.mod if self.k else ""
        self.k = self.izleyici.komut(self.ekf.govde(), on)
        if self.k.bitti:
            self.mod = "bitti"
        # dur-bak: yerinde dönüş bitince 0,6 s dur (dönüşte kare bulanık; görünürlük haritası 0,89 rad/s'de 3 m ötesi 0)
        if onceki == "yerinde" and self.k.mod == "izle":
            self._bak_t = t + DUR_BAK_S
        if t < getattr(self, "_bak_t", -1.0) and not self.k.bitti:
            self.izleyici._v = self.izleyici._w = 0.0
            return 0.0, 0.0
        return self.k.v, self.k.w

    # ------------------------------------------------------------ tarayan kafa (rota izlerken)
    def _bakis_sec(self):
        if self._t - self._gaz_t < 1.2:
            return
        self._gaz_t = self._t
        p = self.ekf.govde()
        if p is None:
            return
        x, y, th = p
        en = None
        for k, e in self.E.items():
            if e.get("koridor") != self.koridor:
                continue
            dx, dy = e["x"] - x, e["y"] - y
            d = math.hypot(dx, dy)
            if d > 5.5 or d < 0.8:
                continue
            gorus = abs(sar(math.atan2(-dy, -dx) - e["yaw"]))     # etiket normali ile etiketten robota yön
            if gorus > math.radians(60):
                continue
            b = sar(math.atan2(dy, dx) - th)
            if abs(b) > PAN_SINIR:
                continue
            yeni = self._t - self._son_gorulen.get(k, -1e9)
            puan = d + (0.0 if yeni > 2.0 else 3.0)
            if en is None or puan < en[0]:
                en = (puan, b)
        self.pan_istek = max(-PAN_SINIR, min(PAN_SINIR, en[1])) if en else 0.0

    # ------------------------------------------------------------ arama (kayıp robot)
    def _ara_baslat(self):
        self._ara = dict(evre="tara", donulen=0.0, sonar_kayit=[], yon=0.0, ilerlenen=0.0, tur=0, pan_i=0,
                         pan_t=self._t, govde_dondu=0.0)

    def _ara_artim(self, artim):
        a = self._ara
        a["yon"] = sar(a["yon"] + artim[2])
        a["donulen"] += artim[2]
        a["ilerlenen"] += math.hypot(artim[0], artim[1])

    def _ara_komut(self, sonar):
        if self._ara is None:
            self._ara_baslat()
            self._olay("arama basladi (kafa %s)" % self.kafa)
        a = self._ara
        s = sonar if (sonar is not None) else math.inf
        if a["evre"] == "tara":
            a["sonar_kayit"].append((a["yon"], s))
            if self.kafa == "tarayan":
                # gövde durur; kafa -80, -40, 0, 40, 80 (her birinde 0,6 s), sonra gövde 180° döner
                panlar = [-80, -40, 0, 40, 80]
                if a["pan_i"] < len(panlar):
                    self.pan_istek = math.radians(panlar[a["pan_i"]])
                    if self._pan_durgun(0.6):
                        a["pan_i"] += 1
                    return 0.0, 0.0
                self.pan_istek = 0.0
                if a["govde_dondu"] < math.pi * 0.95 and a["tur"] == 0:
                    a["govde_dondu"] += 0.0
                    if abs(a["donulen"]) < math.pi:
                        return 0.0, 0.6
                    a["tur"] = 1
                    a["pan_i"] = 0
                    a["donulen"] = 0.0
                    return 0.0, 0.0
                return self._ara_ilerle_kur()
            # sabit kafa: yerinde yavaş tam tur (bulanıklık için 0,45 rad/s)
            if abs(a["donulen"]) < 2 * math.pi * 1.05:
                return 0.0, 0.45
            return self._ara_ilerle_kur()
        if a["evre"] == "don":
            hata = sar(a["hedef_yon"] - a["yon"])
            if abs(hata) < math.radians(8):
                a["evre"] = "ilerle"
                a["ilerlenen"] = 0.0
                return 0.0, 0.0
            return 0.0, math.copysign(max(0.3, min(0.6, 1.2 * abs(hata))), hata)
        if a["evre"] == "ilerle":
            if self.kafa == "tarayan":
                self.pan_istek = math.radians(55.0) * (1 if int(self._t / 2.0) % 2 == 0 else -1)
            if s < 0.9 or a["ilerlenen"] > 3.0:
                self.pan_istek = 0.0
                a.update(evre="tara", donulen=0.0, sonar_kayit=[], pan_i=0, tur=0)
                self._olay("arama: yeniden tara (ilerlenen %.2f m, sonar %.2f)" % (a["ilerlenen"], s))
                return 0.0, 0.0
            return (0.15 if s > 1.3 else 0.08), 0.0
        return 0.0, 0.0

    def _ara_ilerle_kur(self):
        a = self._ara
        kayit = [k for k in a["sonar_kayit"]]
        if kayit:
            yon, d = max(kayit, key=lambda k: k[1] if math.isfinite(k[1]) else 9.0)
        else:
            yon, d = a["yon"], 0.0
        a.update(evre="don", hedef_yon=yon)
        self._olay("arama: etiket yok, en acik yon %.0f derece (sonar %.2f)" % (math.degrees(yon), d))
        return 0.0, 0.0

    # ------------------------------------------------------------ durum
    def durum(self):
        p = self.ekf.govde()
        st = self.ekf.std()
        return {"poz": p, "mod": self.mod if self.mod != "izle" else (self.k.mod if self.k else "izle"),
                "yol": self.yol, "hedef": self.hedef, "harita": None,
                "ek": {"koridor": self.koridor, "hedef_ad": self.hedef_ad, "on_mesafe": self.son_sonar,
                       "konum_std_m": (round(st[0], 4) if st else None), "yon_std_rad": (round(st[1], 4) if st else None),
                       "olcum": self.olcum_sayisi, "ret": self.ret_sayisi, "pan": round(self.pan_model, 3),
                       "donus_olcegi": (round(self.ekf.olcek(), 4) if self.ekf.hazir else None)}}
