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
# doğrulamalı başlatma (kayıp robot, baslatma="dogrulamali"; dayanıklılık turu, geliştirme kümesinde seçildi):
DOG_SURE_S = 1.0          # ilk aday etiketten sonra gövde durur, bu süre boyunca adaylar toplanır
DOG_GELIS = 70.0          # derece: etikete bundan eğik bakılan ölçüm aday olmaz (tasarım 1'de 55: yan duvar
                          # etiketleri 3,5 m içinde çoğunlukla 55°'den eğik, geliştirmede hiç aday çıkmadı)
TAKILMA_S = 2.5           # bu süre boyunca ileri komuta karşın enkoder komutun %25'inden az ilerlerse takılma
KAFA_TARA_S = 6.0         # ilk dönüşten sonra kafa taraması en çok bu kadar
GERI_S = 2.0             # takılmada 0,10 m/s geri (≈ 0,2 m; arkada sensör yok, yalnız az önce geçilen yol)
DOG_POZ_M, DOG_YON = 0.15, math.radians(4.0)    # aday pozların ortancaya uzaklık sınırı
DOG_EN_AZ = 3             # en az bu kadar tutarlı aday (ve adayların %70'i)
DOG_SONAR_M = 0.35        # ön sonar ile haritadan beklenen mesafe farkı sınırı
DOG_BEKLE_S = 1.5         # ret sonrası arama bu süre sürer (başka bakış açısı), sonra yeniden aday toplanır
DOG_SESSIZ_S = 30.0       # rota izlerken bu kadar süre hiç ölçüm kabul edilmezse konum bırakılır, arama yeniden


class SanalRayBeyni:
    def __init__(self, etiketler, K, gorev="ab", koridor=None, baslangic=None, hedef=None, kafa="sabit",
                 konum_ayar=None, izleyici_ayar=None, rota_fn=None, durak_fn=None, baslatma="tek", harita_fn=None):
        """etiketler: {kimlik: {"x","y","z","yaw","boy_m","koridor"}} (bütün koridorların planları; kimlikler tekil).
        K: kamera iç parametresi (işleme çözünürlüğünde). gorev "ab": koridor, baslangic (gövde pozu), hedef (tam durak
        adı) gerekir. "kayip": hedef göreli ("kapi_2"); koridor ilk etiketten. rota_fn(kor, bas_xy, hedef_xy) ve
        durak_fn(kor, ad) -> (tam, xy): gezinme.rota.
        baslatma (yalnız "kayip"): "tek" = 3,5 m içindeki ilk etiket ölçümünden hemen başlat (ilk sürüm);
        "dogrulamali" = gövde durur, DOG_SURE_S boyunca adaylar toplanır; adaylar kendi aralarında tutarlı ve ön sonar
        haritadan beklenen mesafeyle uyumluysa başlatılır, değilse arama sürer. harita_fn(koridor) -> sahte_esp32
        Harita (ön bilgi: bina planı; sonar denetimi için)."""
        self.baslatma = baslatma
        self._harita_fn = harita_fn
        self._haritalar = {}
        self._dog = None
        self._dog_bekle_t = -1e9
        self.dogrulama_ret = 0
        self.dogrulama_nedenler = []
        self.birakma_sayisi = 0
        self._izle_son_kabul_t = None
        self._takilma = []
        self._son_v = 0.0
        self._geri_t = None
        self.takilma_sayisi = 0
        self._ilk_donus_bekliyor = False
        self._kafa_tara = None
        self.kafa_tarama_s = 0.0
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
        if self.baslatma != "dogrulamali" or self.gorev != "kayip":
            return self._adim_ic(t, artim, kare, sonar)
        # takılma denetimi (yalnız enkoder): ileri komut verildiği halde enkoder ilerlemiyorsa (duvara dayanmış; ön
        # sonar eğik duvarda yankı almaz) geri çekil, sonra aramaya dön (izliyorsa konumu bırak)
        ds = math.hypot(artim[0], artim[1])
        self._takilma.append((t, self._son_v, ds))
        while self._takilma and t - self._takilma[0][0] > TAKILMA_S:
            self._takilma.pop(0)
        v, w = self._adim_ic(t, artim, kare, sonar)
        if self._geri_t is not None:
            if t < self._geri_t:
                v, w = -0.10, 0.0
            else:
                self._geri_t = None
                self._takilma = []
                if self.ekf.hazir:
                    self._konumu_birak(t, "takilma")
                elif self._ara is not None:
                    self._ara.update(evre="tara", donulen=0.0, sonar_kayit=[], pan_i=0, tur=0)
                v, w = 0.0, 0.0
        elif (len(self._takilma) > 5 and t - self._takilma[0][0] >= TAKILMA_S - 0.1 and
              all(x[1] >= 0.05 for x in self._takilma[1:]) and
              sum(x[2] for x in self._takilma[1:]) < 0.25 * sum(x[1] for x in self._takilma[1:]) * 0.05):
            self.takilma_sayisi += 1
            self._geri_t = t + GERI_S
            self._olay("takilma: ileri komut, enkoder ilerlemiyor -> geri cekil")
            v, w = -0.10, 0.0
        self._son_v = v
        return v, w

    def _adim_ic(self, t, artim, kare, sonar):
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
                if r <= self.ekf.a.baslat_en_cok_menzil and self.baslatma == "dogrulamali" and self.gorev == "kayip":
                    self._aday_ekle(t, kimlik, r, b, psi)
                    continue
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
                self._izle_son_kabul_t = t
            elif s == "ret":
                self.ret_sayisi += 1
        if self.baslatma == "dogrulamali" and self.gorev == "kayip":
            if self._dog is not None and not self.ekf.hazir and t - self._dog["t0"] >= DOG_SURE_S:
                self._dogrula(t)
            if self.ekf.hazir and (self.ekf.ardisik_ret >= 6 or
                                   (self.mod == "izle" and self._izle_son_kabul_t is not None and
                                    t - self._izle_son_kabul_t > DOG_SESSIZ_S)):
                self._konumu_birak(t, "ardisik ret" if self.ekf.ardisik_ret >= 6 else "uzun sessizlik")
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
            if self._ilk_donus_bekliyor:
                # doğrulamalı: konumlandıktan sonraki ilk yerinde dönüş, dönüş ölçeği henüz öğrenilmemişken yönü
                # bozar (%14 fazla dönüşte 150° dönüşte ≈ 19°); gövde durur, kafa bir etiket kabul edilene dek tarar
                self._ilk_donus_bekliyor = False
                self._kafa_tara = dict(t0=t, i=0, kabul0=self.olcum_sayisi)
                self._olay("ilk donus bitti: kafa taramasi (yon dogrulama)")
        if self._kafa_tara is not None and not self.k.bitti:
            kt = self._kafa_tara
            panlar = (0, -40, 40, -75, 75)
            if self.olcum_sayisi > kt["kabul0"] or kt["i"] >= len(panlar) or t - kt["t0"] > KAFA_TARA_S:
                self._olay("kafa taramasi bitti: %d olcum kabul, %.1f s" % (self.olcum_sayisi - kt["kabul0"], t - kt["t0"]))
                self._kafa_tara = None
                self.pan_istek = 0.0
                self.kafa_tarama_s += t - kt["t0"]
            else:
                self.pan_istek = math.radians(panlar[kt["i"]])
                if self._pan_durgun(0.8):
                    kt["i"] += 1
                self.izleyici._v = self.izleyici._w = 0.0
                return 0.0, 0.0
        if (self.baslatma == "dogrulamali" and self.kafa == "sabit" and self.pan_istek != 0.0 and
                self._kafa_tara is None and self.mod != "ara"):
            self.pan_istek = 0.0
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

    # ------------------------------------------------------------ doğrulamalı başlatma
    def _harita(self, kor):
        if kor not in self._haritalar:
            if self._harita_fn is None:
                from sanalray import etiket as E
                self._harita_fn = E._harita
            self._haritalar[kor] = self._harita_fn(kor)
        return self._haritalar[kor]

    def _aday_ekle(self, t, kimlik, r, b, psi):
        if t < self._dog_bekle_t:
            return
        gelis = abs(sar(psi - (b + math.pi)))
        if gelis > math.radians(DOG_GELIS):
            return
        p = self.ekf.tek_etiketten(kimlik, r, b, psi, self.pan_model)
        if p is None:
            return
        if self._dog is None:
            self._dog = dict(t0=t, aday=[])
            if self.ilk_etiket_t is None:
                self.ilk_etiket_t = t
            self._olay("dogrulama basladi: etiket %d, %.2f m" % (kimlik, r))
        self._dog["aday"].append((kimlik, r, p))

    def sonar_beklenen(self, kor, p):
        """Haritadan ön sonarın beklenen okuması (gövde ön yüzünden, m; yankı yoksa inf). Sensörle aynı varsayım:
        3 ışın ±0,13 rad, 4 m, 60°'den eğik gelen ışın yankı vermez."""
        h = self._harita(kor)
        x, y, th = p
        ox, oy = x + 0.256 * math.cos(th), y + 0.256 * math.sin(th)
        en = None
        for a in (-0.13, 0.0, 0.13):
            r = h.isin(ox, oy, th + a, 4.0)
            if r is None or r[1] > math.radians(60):
                continue
            d = r[0] * math.cos(a)
            en = d if en is None else min(en, d)
        return math.inf if en is None else max(0.0, en - 0.0082)

    def _dogrula(self, t):
        A = self._dog["aday"]
        self._dog = None

        def uz(p, q):
            return math.hypot(p[0] - q[0], p[1] - q[1]) + 0.5 * abs(sar(p[2] - q[2]))
        orta = min(A, key=lambda a: sum(uz(a[2], b[2]) for b in A))[2]
        ic = [a for a in A if math.hypot(a[2][0] - orta[0], a[2][1] - orta[1]) < DOG_POZ_M and
              abs(sar(a[2][2] - orta[2])) < DOG_YON]
        neden = None
        if len(ic) < DOG_EN_AZ or len(ic) < 0.7 * len(A):
            neden = "tutarsiz %d/%d" % (len(ic), len(A))
        else:
            n = len(ic)
            px = sum(a[2][0] for a in ic) / n
            py = sum(a[2][1] for a in ic) / n
            pth = math.atan2(sum(math.sin(a[2][2]) for a in ic), sum(math.cos(a[2][2]) for a in ic))
            kimlik = min(ic, key=lambda a: a[1])[0]
            kor = self.E[kimlik].get("koridor", self.koridor)
            bek = self.sonar_beklenen(kor, (px, py, pth))
            s = self.son_sonar if self.son_sonar is not None else math.inf
            # tasarım 2'de "sonar yankısız ama harita 1,9 m'de duvar bekliyor" da ret sayılıyordu; geliştirmede
            # sonar yakın duvara bakarken bile çoğu kez yankısız döndü (koridor_3 b0: 62 ret, hiç başlatma yok).
            # Tasarım 3: yankısız sonar bilgi vermez; yalnız ölçülen bir mesafe haritayla çelişirse ret.
            if math.isfinite(s) and math.isfinite(bek):
                tutarli = abs(s - bek) < DOG_SONAR_M
            elif math.isfinite(s):
                tutarli = s > 3.3                                   # harita yankı beklemiyor: yankı sınırındaysa belirsiz
            else:
                tutarli = True
            if not tutarli:
                neden = "sonar %.2f, harita %.2f" % (s, bek)
        if neden:
            self.dogrulama_ret += 1
            self.dogrulama_nedenler.append(neden)
            self._olay("dogrulama ret: %s" % neden)
            self._dog_bekle_t = t + DOG_BEKLE_S
            return
        r_ort = sum(a[1] for a in ic) / len(ic)
        ka = self.ekf.a
        sp = ka.s_psi_0 + ka.s_psi_k * r_ort
        sxy = ka.s_menzil_0 + ka.s_menzil_k * r_ort ** 2 + sp * r_ort
        self.ekf.baslat((px, py, pth), std=(sxy, sxy, sp))
        self.ekf.ardisik_ret = 0
        self.lokalize_t = t
        self._izle_son_kabul_t = t
        self._ilk_donus_bekliyor = True
        self.koridor = kor
        self._olay("lokalize (dogrulandi %d/%d aday): etiket %d, koridor %s, %.2f m" % (len(ic), len(A), kimlik, kor, r_ort))

    def _konumu_birak(self, t, neden):
        self.ekf.r = None
        self.ekf.P = None
        self.ekf.ardisik_ret = 0
        self.birakma_sayisi += 1
        self.mod = "ara"
        self._ara = None
        self._dog = None
        self.pan_istek = 0.0
        self._olay("konum birakildi (%s), arama yeniden" % neden)

    def _ara_komut(self, sonar):
        if self._dog is not None:
            return 0.0, 0.0                            # doğrulama: gövde ve kafa dursun
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
