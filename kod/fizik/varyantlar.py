"""Y0f: dönüş için karşılaştırma VARYANTLARI ("ya şöyle olsaydı"). Hepsi VARSAYIM; varsayılan (V0) bugünkü firmware 0.5.0
ve bugünkü mekaniktir. Testler, `olcumler.py` ve sayı özeti yalnız V0 ile koşar; varyant yalnız açıkça istenince
(`olcum_varyantlar.py`, `gorunum3b.py --varyant` / `simulasyon3b.bat <sahne> <varyant>`) devreye girer.

Anahtarlar:
  fw_w_giris        firmware `w` giriş tavanı (rad/s; 0.5.0'da 1). 3 ile yerinde dönüşte iki yan teker azamisine (±0,39 m/s)
                    ölçeklenir: PWM ±1 (açık çevrim).
  fw_kapali_cevrim  firmware teker hızı denetimi: u = hedef / 0,39 + kp (hedef - ölçülen) + ki ∫(hedef - ölçülen), |u| ≤ 1,
                    doyumda integral durur (anti-windup). Ölçülen = o yanın enkoderli tekeri. Kazançlar TAHMİN.
                    (main motorlar.cpp'de KP / KI / KD sabitleri var, 0.5.0'da KP = 0: bu varyant onların sıfırdan büyük hâli.)
  on_teker          "omni": ön iki teker yanal serbest (top teker modeli, aşağıda), tahrikli.
                    "sarhos": ön iki teker yanal ve boyuna serbest, tahriksiz (bilyalı sarhoş teker; dönen çatallı
                    sarhoş tekerin çatal dinamiği yok), tahrik ve enkoder arka tekerlerde.

Ön teker modeli (omni / sarhoş): ön teker gövdesi tabana yanal ekseni robotun x'i olan pasif bir menteşeyle ("makara",
sönüm 0,001 N·m·s/rad) bağlanır; tekerin kendi ekseni (y) bu menteşenin içinde. Temas geometrisi aynı yarıçapta küre (silindir
yerine), merkezi iki eksenin kesişiminde: yanal kayma yerine küre x ekseni çevresinde yuvarlanır, yanal direnç ≈ 0; boyuna
yönde tutuş ve normal yük değişmez. Makara açısı her fizik adımından sonra 0'a döner (`dunya.adim`): küre kendi merkezi
çevresinde simetrik olduğundan temas geometrisi değişmez, teker ekseni yatay kalır ("hep alttaki makara"), makara hızı korunur.
Bu sıfırlama olmadan makara dönerken teker ekseni yatırılıyor ve tahrik çekişi kayboluyordu (ilk denemede görüldü). Doğru verdiği: ön aksta yanal direncin yokluğu (dönme momenti gereksinimi, yan eğimde ön
aksın kayması, frende yönsel kararlılık kaybı). Kaba verdiği: gerçek omni tekerin ayrık makaraları (titreşim, makara
yuvarlanma direnci, sert zeminde düşük boyuna tutuş), temas yaması (tek nokta), makaranın kendi sürtünmesi; sarhoş tekerde
çatal izi ve dönme gecikmesi. Görsel ağ "makara" gövdesinde durur (dönmez).
"""

VARYANTLAR = {
    "V0": dict(ad="V0 bugunku robot", aciklama="firmware 0.5.0 + dört lastik teker (varsayılan)"),
    "V1": dict(ad="V1 firmware w tavani 3 rad/s", aciklama="w girişi 3'e dek; yerinde dönüşte PWM ±1 (açık çevrim)",
               fw_w_giris=3.0),
    "V2": dict(ad="V2 firmware kapali cevrim PI", aciklama="enkoderden teker hızı PI (kp 2, ki 10; TAHMİN), PWM doyuma dek",
               fw_kapali_cevrim=dict(kp=2.0, ki=10.0)),
    "V3": dict(ad="V3 on tekerler omni", aciklama="ön iki teker yanal serbest, tahrikli", on_teker="omni"),
    "V4": dict(ad="V4 onde sarhos teker", aciklama="ön iki teker serbest (bilyalı sarhoş), yalnız arka iki teker tahrikli",
               on_teker="sarhos"),
    "V1+V3": dict(ad="V1+V3 w tavani 3 + on omni", aciklama="V1 ve V3 birlikte", fw_w_giris=3.0, on_teker="omni"),
    "V2+V3": dict(ad="V2+V3 kapali cevrim + on omni", aciklama="V2 ve V3 birlikte", fw_kapali_cevrim=dict(kp=2.0, ki=10.0),
                  on_teker="omni"),
}
SIRA_V = list(VARYANTLAR)   # karşılaştırma varyantları (olcum_varyantlar.py; donus-varyantlar.md)

# Öneri firmware (ayrı dal oneri/donus-omni, kod/esp32/src/motorlar.cpp). Sabitler oradakiyle AYNI olmalı; değiştirirken ikisini
# birlikte değiştir. TAHMİN: kp, ki (simülasyonda seçildi, masada ayarlanacak).
ONERI_FW = dict(
    kp=4.0,               # KP, PWM / (m/s)
    ki=20.0,              # KI, PWM / m
    integral_siniri=0.6,  # INTEGRAL_SINIRI: integralin PWM katkısı en çok (0.5.0: 0,3; 9 kg·cm yavaş dönüş için 0,6)
    w_giris=1.0,          # W_GIRIS_SINIRI (protokol değişmez)
    dt_ms=20,             # DT (motorlar_guncelle aralığı)
    integral_rampada=False,  # hızlanma rampasında integral durur (RAMPA_BITTI_M_S): rampa sonunda hız aşması olmasın
    duzeltme_orani=1.0,   # DUZELTME_ORANI: PI düzeltmesi <= oran x |ileri besleme| + taban (enkoder arızası katmanı 1); None = koruma yok
    duzeltme_tabani=0.3,  # DUZELTME_TABANI
    kusku_hiz=0.02,       # KUSKU_HIZ_M_S (katman 2, makullük)
    kusku_adim=25,        # KUSKU_SURE_MS 500 / DT 20
)
# Not: C++'ta PI ilk yüklemede kapalıdır (ONERI_PI_ACIK 0 -> KP = KI = 0); model ONERI_PI_ACIK 1'i (masada açıldıktan sonrasını) modeller.
MAKARA_MU_YAN = 0.05      # omni makaralarının eşdeğer yanal sürtünmesi (TAHMİN; duyarlılık 0 / 0,05 / 0,15)
VARYANTLAR["ONERI"] = dict(ad="ONERI firmware oneri + on omni", aciklama="öneri firmware (kapalı çevrim PI, doyum ölçeklemesi) + "
                           "ön iki teker omni (makara yanal sürtünmesi 0,05, TAHMİN)", fw_oneri=ONERI_FW, on_teker="omni",
                           makara_mu_yan=MAKARA_MU_YAN)
VARYANTLAR["ONERI-T"] = dict(ad="ONERI-T firmware oneri + bugunku tekerler", aciklama="öneri firmware + dört lastik teker "
                             "(bugünkü mekanik)", fw_oneri=ONERI_FW)
# Aday omni teker (SEÇİLMEDİ): Nexus 14075 çift sıra, Ø127 x 29 mm, 22 makara, 480 g (ürün sayfası; tasarim/freecad/arayuz.py
# TABAN omni). Aks yeri aynı, teker iç yüzü aynı yerde: merkez (58 - 29) / 2 = 14,5 mm içeri. Firmware TEKER_CAPI_M 0,125 kalır
# (enkoder ön omni tekerde: ölçülen hız ve odometri %1,6 eksik); duyarlılıkta 0,127.
ADAY_TEKER = dict(on_teker_r=0.0635, on_teker_kutle_kg=0.480, on_teker_y_iceri_m=0.0145)
VARYANTLAR["ONERI-ADAY"] = dict(VARYANTLAR["ONERI"], ad="ONERI-ADAY oneri + aday omni (Nexus 127 mm)",
                                aciklama="ONERI, ön teker aday ölçüleriyle (Ø127 x 29 mm, 480 g; seçilmedi)", **ADAY_TEKER)
SIRA = list(VARYANTLAR)


def oneri_varyanti(**degis):
    """Duyarlılık için ONERI kopyası: fw_* anahtarları ONERI_FW'ye, öbürleri varyanta (makara_mu_yan, on_teker)."""
    v = dict(VARYANTLAR["ONERI"])
    fw = dict(ONERI_FW)
    for k, d in degis.items():
        if k in fw:
            fw[k] = d
        else:
            v[k] = d
    v["fw_oneri"] = fw
    return v


def al(ad):
    """Varyant sözlüğü; None / "V0" -> None (bugünkü robot: hiçbir kod yolu değişmez)."""
    if ad in (None, "", "V0"):
        return None
    if ad not in VARYANTLAR:
        raise ValueError("bilinmeyen varyant %r (seçenekler: %s)" % (ad, ", ".join(SIRA)))
    return VARYANTLAR[ad]


def on_teker_xml(x, tur, r=0.0625, kutle_kg=None, y_iceri_m=0.0):
    """lale.xml metninde ön iki tekeri "makara" menteşeli küre tekere çevirir (omni / sarhoş). Başka hiçbir şeye dokunmaz.
    Aday teker ölçüleri için: r (temas küresi yarıçapı; aks yeri aynı kalır, ön uç r - 0,0625 kadar yükselir), kutle_kg
    (teker kütlesi; atalet aynı oranla), y_iceri_m (dar teker: iç yüzü aynı yerde, merkezi içeri kayar)."""
    import math
    import re
    for yan in ("sol", "sag"):
        ad = "teker_on_" + yan
        m = re.search(r'( *)<body name="%s" pos="([^"]+)">(.*?)\n\1</body>' % ad, x, flags=re.S)
        if m is None:
            raise RuntimeError("lale.xml'de %s gövdesi bulunamadı" % ad)
        girinti, pos, ic = m.group(1), m.group(2), m.group(3)
        if y_iceri_m:
            px, py_, pz = (float(t) for t in pos.split())
            pos = "%.6g %.6g %.6g" % (px, py_ - math.copysign(y_iceri_m, py_), pz)
        if kutle_kg is not None:
            mi = re.search(r'mass="([^"]+)" fullinertia="([^"]+)"', ic)
            k = kutle_kg / float(mi.group(1))
            ic = ic.replace(mi.group(0), 'mass="%.6g" fullinertia="%s"' % (
                kutle_kg, " ".join("%.6g" % (float(t) * k) for t in mi.group(2).split())))
        gorsel = re.search(r'\n *<geom class="gorsel"[^>]*/>', ic).group(0)
        ic = ic.replace(gorsel, "")
        ic = re.sub(r'(<geom name="c_%s" class="teker_carpisma") type="cylinder" size="[^"]+" pos="0 0 0" quat="[^"]+"' % ad,
                    r'\1 type="sphere" size="%.6g"' % r, ic)
        yeni = ('%s<body name="makara_on_%s" pos="%s">\n'
                '%s  <inertial pos="0 0 0" mass="0.001" diaginertia="1e-6 1e-6 1e-6"/>\n'
                '%s  <joint name="makara_on_%s" type="hinge" axis="1 0 0" damping="0.001" armature="0"/>%s\n'
                '%s  <body name="%s" pos="0 0 0">%s\n%s  </body>\n%s</body>'
                % (girinti, yan, pos, girinti, girinti, yan, gorsel.replace("\n", "\n  "), girinti, ad,
                   ic.replace("\n", "\n  "), girinti, girinti))
        x = x[:m.start()] + yeni + x[m.end():]
    return x
