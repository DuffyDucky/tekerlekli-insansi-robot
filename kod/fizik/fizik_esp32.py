"""Y0f: sahte ESP32'nin FİZİK dünyası arka ucu.

`SahteEsp32` (firmware 0.5.0 sözleşmesinin modeli: protokol, bekçi, acil stop, güç durumları, rampa / fren sınırları,
servo hız sınırı, TASLAK sonar kuralı) AYNEN kullanılır; yalnız "dünya" kısmı değişir:
  - teker hareketi: 2B ideal diferansiyel sürüş yerine MuJoCo'da motor torku -> teker -> temas (kayma, devrilme dahil);
    PWM oranı firmware'deki gibi u = rampa_hiz / TEKER_AZAMI_HIZ (KP = 0, açık çevrim); EN ve bara durumundan
    fren / boşta ayrımı (`dunya.py` motor modeli)
  - enkoder: tikler fizikteki teker açısından (her yanda ön teker, TAHMİN)
  - sonar: MuJoCo ışın demeti (7 yatay x 3 dikey), yankı kuralı 2B ile aynı
  - kollar ve kafa: servo hedefi çekirdeğin `servo_simdi`'sinden (hız sınırlı) -> eklem konum eyleyicisi; bara
    gerilimsizken servolar güçsüz
  - hakem: fizikteki gerçek konum / hız / çarpışma + `fizik` alanı (eğim, teker yükleri, AM)
Pi istemcisi ve protokol değişmez: istemci karşısında hangi dünyanın olduğunu bilmez.
"""

import math
import os
import sys

_KOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _y in (os.path.join(_KOD, "ortak"), os.path.join(_KOD, "araclar"), os.path.dirname(os.path.abspath(__file__))):
    if _y not in sys.path:
        sys.path.insert(0, _y)

from sahte_esp32.cekirdek import SahteEsp32, DILIM_MS  # noqa: E402
import dunya as D  # noqa: E402


class FizikEsp32(SahteEsp32):
    def __init__(self, harita, konum=None, sonar_acik=True, bagimli_sinir_acik=True, sahne=None, degis=None):
        x, y, a = konum if konum is not None else harita.baslangic
        self.dunya = D.FizikDunya(harita, sahne=sahne, konum=(float(x), float(y), float(a)), degis=degis)
        self._kesir = [0.0, 0.0]
        self._son_aci = None
        self._adimlandi = False
        self._carpisma_onceki = False
        self.kayitci = None                  # ölçüm: her 10 ms dilimin sonunda kayitci(self) çağrılır
        self.pwm_zorla = None                # yalnız ölçüm (olcumler.py dönüş): sürülürken firmware PWM eşlemesi yerine bu [u_sol, u_sag]
        super().__init__(harita, konum=konum, sonar_acik=sonar_acik, bagimli_sinir_acik=bagimli_sinir_acik)
        self.dunya.gerilim(self.aku_v)
        # kollar ve kafa servo "ev" açısında başlar (montaj ev pozu eklem 0; S2 ev 5 derece)
        self.dunya.servo_eklem_ayarla({t["ad"]: math.radians(a - t["ofset"]) for t, a in zip(self.servo_tablo, self.servo_simdi)})
        self._servo_uygula()
        self._enkoder_bas()

    # ------------------------------------------------------------ yardımcılar
    def _enkoder_teker(self):
        """Her yanda enkoderin olduğu teker (TAHMİN: ön): dunya.TEKERLER sırası on_sol, arka_sol, on_sag, arka_sag."""
        return (0, 2) if self.dunya.p["enkoder_teker"] == "on" else (1, 3)

    def _enkoder_bas(self):
        a = self.dunya.teker_acilari()
        i, j = self._enkoder_teker()
        self._son_aci = [a[i], a[j]]

    def _servo_uygula(self):
        hedef = {}
        for t, aci in zip(self.servo_tablo, self.servo_simdi):
            hedef[t["ad"]] = math.radians(aci - t["ofset"])
        self.dunya.servo_hedef(hedef)
        self.dunya.servo_guc(self._bara_gerilimli())

    def _surucu(self):
        """Motor sürücüsünün girişi (firmware çıkışı): (sürülüyor mu: EN HIGH + bara + kart çalışıyor, PWM oranları)."""
        suruluyor = bool(self.en and self._bara_gerilimli() and self.calisiyor)
        u = [max(-1.0, min(1.0, h / self.azami_hiz)) for h in self.rampa_hiz] if suruluyor else [0.0, 0.0]
        if suruluyor:
            # firmware teker_adim: rampa_hiz == 0 ise çıkış 0 (fren)
            u = [0.0 if h == 0.0 else ui for h, ui in zip(self.rampa_hiz, u)]
            if self.pwm_zorla is not None:
                u = list(self.pwm_zorla)
        return suruluyor, u

    def _fizik_adim(self, dt):
        suruluyor, u = self._surucu()
        self._servo_uygula()
        self.dunya.adim(dt, u[0], u[1], suruluyor)
        self._adimlandi = True
        # konum / açı (hakem ve 2B görünüm)
        x, y, _, yaw, _, _ = self.dunya.poz()
        self.yol_m += math.hypot(x - self.x, y - self.y)
        self.x, self.y, self.aci = x, y, yaw
        c = self.dunya.temas_engel()
        if c and not self._carpisma_onceki:
            self.carpisma_sayisi += 1
        self._carpisma_onceki = c
        self.carpiyor = c
        # enkoder (fizikteki teker açısından)
        a = self.dunya.teker_acilari()
        i, j = self._enkoder_teker()
        for k, yeni in enumerate((a[i], a[j])):
            self._kesir[k] += (yeni - self._son_aci[k]) / (2 * math.pi) * self.tik_tur
            tam = int(self._kesir[k])
            self.tik[k] += tam
            self._kesir[k] -= tam
            self._son_aci[k] = yeni
        if self.kayitci is not None:
            self.kayitci(self)

    # ------------------------------------------------------------ çekirdeğin dünya kancaları
    def _hareket(self, dt):
        self._fizik_adim(dt)

    def _dilim(self):
        self._adimlandi = False
        super()._dilim()
        if not self._adimlandi:              # reset sonrası açılış: kart kapalı, motorlar boşta, dünya yine ilerler
            self._fizik_adim(DILIM_MS / 1000.0)

    def _k_odo_sifirla(self, d, simdi):
        super()._k_odo_sifirla(d, simdi)
        self._kesir = [0.0, 0.0]

    def _acilis(self):
        super()._acilis()
        if getattr(self, "dunya", None) is not None:
            self._kesir = [0.0, 0.0]
            self._enkoder_bas()

    def konum_ayarla(self, x, y, aci_rad):
        self.dunya.konum_ayarla(float(x), float(y), float(aci_rad))
        self.x, self.y, self.aci = float(x), float(y), float(aci_rad)
        self.carpiyor = self._carpisma_onceki = self.dunya.temas_engel()
        self._enkoder_bas()

    def _carpar(self, x, y, a):
        return self.dunya.temas_engel()

    def _sonar_olc(self, ad):
        bas, R = self.dunya.sonar_cercevesi(ad)
        en_az, en_cok = self.sonar_menzil
        n = self.sonar_isin
        nd = int(self.dunya.p["sonar_dikey_isin"])
        en_iyi = None
        isinlar = []
        for k in range(nd):
            p = 0.0 if nd == 1 else -self.sonar_yari_aci + 2.0 * self.sonar_yari_aci * k / (nd - 1)
            for i in range(n):
                a = -self.sonar_yari_aci + 2.0 * self.sonar_yari_aci * i / (n - 1)
                yerel = (math.cos(p) * math.cos(a), math.cos(p) * math.sin(a), math.sin(p))
                yon = [sum(R[r][c] * yerel[c] for c in range(3)) for r in range(3)]
                r = self.dunya.isin(bas, yon, en_cok)
                if r is None:
                    if k == nd // 2:
                        isinlar.append((bas[0], bas[1], bas[0] + yon[0] * en_cok, bas[1] + yon[1] * en_cok, False))
                    continue
                t, gelis = r
                yanki = gelis <= self.sonar_gelis_siniri and t >= en_az
                if k == nd // 2:
                    isinlar.append((bas[0], bas[1], bas[0] + yon[0] * t, bas[1] + yon[1] * t, yanki))
                if yanki and (en_iyi is None or t < en_iyi):
                    en_iyi = t
        self.son_isinlar[ad] = isinlar
        return None if en_iyi is None else round(en_iyi * 100.0, 1)

    def on_engel_uzakligi(self):
        bas, R = self.dunya.sonar_cercevesi("orta")
        r = self.dunya.isin(bas, [R[0][0], R[1][0], R[2][0]], 1000.0)
        return None if r is None else r[0]

    def hakem(self):
        h = super().hakem()
        v, w = self.dunya.hiz()
        tv = self.dunya.teker_hizlari()
        rt = self.teker_capi / 2.0
        x, y, z, yaw, pitch, roll = self.dunya.poz()
        # hakem çözünürlüğü 0,1 mm/s (1e-4 rad/s): fizikte duran gövde ~1e-13 m/s titrer; 2B hakem tam 0 verir.
        # Yalnız hakemin (ek doğrulama) sıfır karşılaştırmasını anlamlı kılar; enkoder (protokol) etkilenmez.
        c = lambda z: 0.0 if abs(z) < 1e-4 else z
        # surucu: motor sürücüsünün girişi (osiloskopla ölçülebilir: EN, PWM) ve firmware'in teker hız hedefi. Fizikte
        # "anında durma" yerine "sürücü komutu kesildi + robot payı içinde durdu" doğrulaması bunu okur (testler/duzenek.py).
        sur, u = self._surucu()
        h["surucu"] = dict(suruluyor=sur, pwm=list(u), hedef_m_s=list(self.rampa_hiz))
        h.update(x=x, y=y, aci=yaw, v=c(v), w=c(w),
                 teker=[c((tv[0] + tv[1]) / 2 * rt), c((tv[2] + tv[3]) / 2 * rt)],
                 fizik=dict(z=z, pitch=pitch, roll=roll, egim=self.dunya.egim(), am=self.dunya.am(),
                            teker_yuk_N=self.dunya.teker_yukleri(), teker_hiz_rad_s=tv,
                            govde_zemine_degiyor=self.dunya.govde_zemine_degiyor(),
                            motor_tork_Nm=list(self.dunya.son_tork), zaman_s=self.dunya.zaman_s))
        return h
