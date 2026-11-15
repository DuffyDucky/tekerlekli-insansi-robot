# 3B montaj rehberi: rehber metnindeki güvenlik açısından kritik değerlerin tek çözümleyicisi (P10.7b1 düzeltme turu 1). FreeCAD
# İSTEMEZ (standart kütüphane); kayıtları yalnız okur.
#
# rehber_metin.py'de sigorta değeri / tipi, GPIO numarası, kablo kesiti, röle sürücüsü ve ön şarj dirençleri, yıldız barası saplama
# yerleşimi, ön şarj beklemesi elle yazılmaz: adlandırılmış yer tutucu yazılır ve bu modül kayıttan doldurur.
#   {a.<koruyucu>}        akım:   kablolar.json koruyucular[<koruyucu>].akim_a          → "7,5 A"
#   {bicak.<koruyucu>}    tip:    koruyucular[<koruyucu>].bicak                          → "mini" / "standart"
#   {gpio.<pin adı>}      pin:    pin-haritasi.md § 9 JSON pinler[<ad>].gpio            → "GPIO19"
#   {awg.<kablo>}         kesit:  kablolar[<kimlik>].kesit.awg                           → "16 AWG"
#   {kopru.<kablo>}       köprü:  kablolar[<kimlik>].sonlandirma "≥ N AWG tel köprü"     → "≥ 18 AWG"
#   {kopru.yildiz}        yıldız barası saplama köprüsü: bara-pabuc.kopruler["Yıldız barası · GND"].awg → "12 AWG"
#   {kopru.bara}          anahtarlı bara saplama köprüsü: bara-pabuc.kopruler["Anahtarlı bara · +"].awg → "12 AWG"
#   {kopru_adet.yildiz|bara|toplam} / {kopru_renk.yildiz|bara} / {kopru_boy.yildiz|bara} / {kopru_pabuc.toplam}
#                         köprü adedi, rengi, boyu; toplam pabuç = 2 × toplam adet       → "4" / "siyah" / "50 mm" / "14"
#   {ara.<kablo>}         ara parça kesiti: kablolar[<kimlik>].sonlandirma "N cm M AWG … ara parça" → "18 AWG"
#   {ohm.seri|taban}      röle sürücüsü: pin haritası ROLE_K1.donanim "270R seri, 2.2k taban" → "270 Ω" / "2,2 kΩ"
#   {ohm.onsarj}          ön şarj direnci: anahtarlar.K2-kontak.ad "… + 5,6 Ω"         → "5,6 Ω"
#   {saplama.<kablo>}     yıldız barası saplaması: klemens_turleri.bara-pabuc.kopruler["Yıldız barası · GND"].yerlesim → "3"
#   {saplama.sayi}        yıldız barası saplama sayısı (bara-pabuc.dugumler)             → "5"
#   {saplama.bara}        anahtarlı bara saplama sayısı                                  → "4"
#   {saplama.pabuc}       saplama başına en çok pabuç                                    → "4"
#   {ms.onsarj} / {ms.onsarj_bos} / {ms.k1_sonra}   E9 dizisi (elektrik.md "en az N ms bekle (boş akü için M ms önerilir" ve
#                         "(5) N ms sonra GPIO19 = 0")                                    → "300 ms" / "500 ms" / "100 ms"
#   {s.k2_en_cok}         pin haritası ROLE_K2_ONSARJ.en_cok_ms                          → "1 s"
#   {yuva.F6}             sigorta kutusu yuvası: elektrik.md sigorta listesi satırı "kutunun N. yuvası" → "6" (metin ". yuvası" ekler)
#   {a.F2} / {bicak.F2}   koruyucular'da olmayan kutu sigortası (F2 yedek): elektrik.md sigorta listesi "| F2 | 15 A standart |" → "15 A"
#   {awg.G14|G15|G16}     grup: birden çok kabloyu temsil eden yer tutucu; üyelerin değeri eşit değilse hata (açık iş 16)
#   {yeniden.K04}         kesiti bilinmeyen hazır kablonun yeniden yapılma kesiti: kablolar[K04].teyit "yazı yoksa N AWG" → "18 AWG"
# P10.7b2a (kablolar.json şema 4):
#   {ohm.aku_olcum}       akü ölçüm bölücüsünün üst direnci: koruyucular.R-aku-olcum.ad "… 100 kΩ …"  → "100 kΩ"
#   {bsaplama.<kablo>}    anahtarlı bara saplaması: bara-pabuc.kopruler["Anahtarlı bara · +"].yerlesim → "3"
#   {bsaplama.besleme}    anahtarlı baranın besleme saplaması (besleme_saplamasi)            → "3"
#   {saplama.besleme}     yıldız barasının besleme (akü dönüşü) saplaması                    → "3"
#   {kontak.K1|K2}        röle kontağının uçları: anahtarlar.K<n>-kontak.uclar               → "30 → 87" / "COM → NO (NC boş)"
#   {yer.<koruyucu>}      hat sigortası / direncin kablo üstündeki yeri: koruyucular[<k>].yer (ilk ':' öncesi) → "anahtarlı bara ucunda (kaynak ucu)"
#   {yon.<tvs>}           TVS yönü: tvs[<k>].yon                                              → "katot (bantlı uç) +12 V ucuna, anot GND'ye"
#   {yon.kondansator}     elektrolitik kondansatörün yönü: kondansatorler.yon
# Düzeltme turu 1 (F10i-kontrol):
#   {uc.<kablo>:<damar>:<a|b>}  damarın bir ucunun noktası (damar adında boşluk yerine _): kablolar[<k>].damarlar → "3V3", "IN2 +"
#   {kutup.<kablo>}       iki damarlı güç kablosunun kutbu, damarlardan                       → "OUT+ → V+, OUT− → GND"
#   {oran.aku_olcum}      akü ölçüm bölücüsünün oranı alt / (üst + alt): elektrik.md E2 "100 kΩ / 18 kΩ" → "0,1525"
#   {v.aku_aralik}        ölçümde beklenen akü aralığı: elektrik.md "akü 12,8–14,4 V"         → "12,8–14,4 V"
#   {v.aku_olcum}         bölücü orta noktasında beklenen gerilim (aralık × oran, 2 basamak)  → "1,95–2,20 V"
#   {vida.<anahtar>}      saplama ölçüsü: anahtarlar[<k>].saplama.olcu (varsayım; teyit kaydı) → "M5"
# Düzeltme turu 2 (F10i-kontrol-2):
#   {kontak.K2:giris|cikis|bos}  röle kontağının tek ucu: anahtarlar.K<n>-kontak.uclar     → "COM" / "NO" / "NC"
#   {parca.<kablo>:<damar>:<a|b>}  damar ucunun parçası (" · " öncesi): kablolar[<k>].damarlar → "acil stop düğümü (mantar NC çıkışı)"
#   {oran.…} / {v.…}: bölücü çıkışı akü üst sınırında ("14,6 V →") ADC doğrusal sınırını ("≤ 2,45 V") aşarsa KeyError
# Çözülemeyen yer tutucu hata listesine girer (rehber_denetim.kaynak_denetle sayar; rehber_metin içe aktarılırken metin "⟦?…⟧" olur).
import os, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
KABLO_TABLO = os.path.join(ROBOT, "planlama", "adim3", "kablolar.json")
PIN_HARITASI = os.path.join(ROBOT, "planlama", "adim3", "pin-haritasi.md")
ELEKTRIK = os.path.join(ROBOT, "planlama", "adim3", "elektrik.md")
YER_TUTUCU = re.compile(r"\{([a-z_]+)\.([^{}\s]+)\}")
# düzeltme turu 2: yer tutucu anahtarı → bara-pabuc.kopruler / dugumler kaydı (tamlık sınaması da bu eşlemeyi kullanır)
KOPRU_BARA = {"yildiz": "Yıldız barası · GND", "bara": "Anahtarlı bara · +"}
SAPLAMA_DUGUM = {"sayi": "Yıldız barası · GND", "bara": "Anahtarlı bara · +"}


def _sayi_metin(v):
    s = ("%g" % v).replace(".", ",")
    return s


class Degerler:
    def __init__(self, T=None, PH=None, EL=None):
        self.T = T if T is not None else json.load(open(KABLO_TABLO, encoding="utf-8"))
        if PH is None:
            md = open(PIN_HARITASI, encoding="utf-8").read()
            PH = json.loads(md.split("## 9.")[1].split("```json")[1].split("```")[0])
        self.PH = PH
        self.EL = EL if EL is not None else open(ELEKTRIK, encoding="utf-8").read()
        self.K = {r["kimlik"]: r for r in self.T["kablolar"]}
        self.KOR = self.T["koruyucular"]
        self.BP = self.T["klemens_turleri"]["bara-pabuc"]

    def _kopru(self, anahtar):
        k = (self.BP.get("kopruler") or {}).get(KOPRU_BARA[anahtar])
        if not isinstance(k, dict) or not all(k.get(x) for x in ("adet", "awg", "renk", "boy_mm")):
            raise KeyError("bara-pabuc.kopruler[%s] yok ya da adet / awg / renk / boy_mm eksik" % KOPRU_BARA[anahtar])
        return k

    def _liste_satiri(self, anahtar):
        """elektrik.md sigorta listesi satırı: (akım metni, bıçak) ya da None."""
        m = re.search(r"^\| %s \| \**(\d+(?:,\d+)?) A\** (standart|mini)\b" % re.escape(anahtar), self.EL, re.M)
        return (m.group(1), m.group(2)) if m else None

    def deger(self, tur, anahtar):
        """Yer tutucunun metni; bilinmiyorsa KeyError (neden metniyle). Grup anahtarı ("G14|G15|G16"): üyelerin hepsi çözülür, değerleri
        eşit değilse KeyError (açık iş 16: birden çok kabloyu temsil eden yer tutucu sessizce kaymaz)."""
        if "|" in anahtar:
            uye = anahtar.split("|")
            d = [self._deger1(tur, u) for u in uye]
            if len(set(d)) != 1:
                raise KeyError("grup {%s.%s} üyelerinin değeri eşit değil: %s" % (tur, anahtar, ", ".join(
                    "%s %s" % (u, x) for u, x in zip(uye, d))))
            return d[0]
        return self._deger1(tur, anahtar)

    def _deger1(self, tur, anahtar):
        if tur in ("a", "bicak") and anahtar not in self.KOR:
            sat = self._liste_satiri(anahtar)
            if not sat:
                raise KeyError("koruyucu %s ne koruyucular'da ne elektrik.md sigorta listesinde" % anahtar)
            return ("%s A" % sat[0]) if tur == "a" else sat[1]
        if tur == "yuva":
            m = re.search(r"^\| %s \|[^\n]*?kutunun (\d+)\. yuvası" % re.escape(anahtar), self.EL, re.M)
            if not m:
                raise KeyError("elektrik.md sigorta listesinde %s için 'kutunun N. yuvası' yok" % anahtar)
            return m.group(1)
        if tur == "yeniden":
            m = re.search(r"yazı yoksa (\d+) AWG", " ".join(self.K[anahtar].get("teyit") or []))
            if not m:
                raise KeyError("kablo %s teyit listesinde 'yazı yoksa N AWG' yok" % anahtar)
            return "%s AWG" % m.group(1)
        if tur == "a":
            v = self.KOR[anahtar]["akim_a"]
            if v is None:
                raise KeyError("koruyucu %s akımı yok" % anahtar)
            return "%s A" % _sayi_metin(v)
        if tur == "bicak":
            v = self.KOR[anahtar].get("bicak")
            if not v:
                raise KeyError("koruyucu %s bıçak tipi yok" % anahtar)
            return v
        if tur == "gpio":
            return "GPIO%d" % self.PH["pinler"][anahtar]["gpio"]
        if tur == "awg":
            k = self.K[anahtar].get("kesit") or {}
            if not k.get("awg"):
                raise KeyError("kablo %s kesiti yok" % anahtar)
            return "%d AWG" % k["awg"]
        if tur in ("kopru", "kopru_adet", "kopru_renk", "kopru_boy", "kopru_pabuc") and (anahtar in KOPRU_BARA or anahtar == "toplam"):
            # düzeltme turu 2 (F10h-kontrol-3 §2): iki baranın saplama köprüleri bara-pabuc.kopruler'den (adet, kesit, renk, boy)
            if anahtar == "toplam":
                adet = sum(self._kopru(b)["adet"] for b in KOPRU_BARA)
                if tur == "kopru_adet":
                    return str(adet)
                if tur == "kopru_pabuc":                                 # her köprü ucu bir halka pabuç (kopruler.pabuc)
                    return str(2 * adet)
                raise KeyError("{%s.toplam} tanımlı değil" % tur)
            k = self._kopru(anahtar)
            if tur == "kopru":
                return "%d AWG" % k["awg"]
            if tur == "kopru_adet":
                return str(k["adet"])
            if tur == "kopru_renk":
                return k["renk"]
            if tur == "kopru_boy":
                return "%d mm" % k["boy_mm"]
            raise KeyError("{%s.%s} tanımlı değil" % (tur, anahtar))
        if tur == "ara":
            m = re.search(r"\d+ cm (\d+) AWG [^;]*?ara parça", self.K[anahtar]["sonlandirma"])
            if not m:
                raise KeyError("kablo %s sonlandırmasında 'N cm M AWG … ara parça' yok" % anahtar)
            return "%s AWG" % m.group(1)
        if tur == "kopru":
            m = re.search(r"≥ (\d+) AWG tel köprü", self.K[anahtar]["sonlandirma"])
            if not m:
                raise KeyError("kablo %s sonlandırmasında '≥ N AWG tel köprü' yok" % anahtar)
            return "≥ %s AWG" % m.group(1)
        if tur == "ohm":
            if anahtar in ("seri", "taban"):
                d = self.PH["pinler"]["ROLE_K1"]["donanim"]
                d2 = self.PH["pinler"]["ROLE_K2_ONSARJ"]["donanim"]
                m = re.search(r"(\d+(?:\.\d+)?)(R|k) " + anahtar, d)
                m2 = re.search(r"(\d+(?:\.\d+)?)(R|k) " + anahtar, d2)
                if not m or not m2 or m.groups() != m2.groups():
                    raise KeyError("röle sürücüsü %s direnci iki sürücüde aynı değil ya da yok" % anahtar)
                return "%s %sΩ" % (m.group(1).replace(".", ","), "k" if m.group(2) == "k" else "")
            if anahtar == "onsarj":
                m = re.search(r"(\d+(?:,\d+)?) ?Ω", self.T["anahtarlar"]["K2-kontak"]["ad"])
                if not m:
                    raise KeyError("ön şarj direnci anahtarlar.K2-kontak.ad'da yok")
                return "%s Ω" % m.group(1)
            if anahtar == "aku_olcum":                                   # P10.7b2a: G07'nin kaynak ucundaki direnç
                e = self.KOR.get("R-aku-olcum") or {}
                m = re.search(r"(\d+(?:,\d+)?) ?(k?)Ω", e.get("ad") or "")
                if not m or e.get("tur") != "direnc":
                    raise KeyError("koruyucular.R-aku-olcum (direnç) adında 'N kΩ' yok")
                return "%s %sΩ" % (m.group(1), m.group(2))
        if tur == "bsaplama" or (tur == "saplama" and anahtar == "besleme"):   # P10.7b2a: anahtarlı bara yerleşimi (şema 4)
            k = self.BP["kopruler"][KOPRU_BARA["bara" if tur == "bsaplama" else "yildiz"]]
            if anahtar == "besleme":
                if not isinstance(k.get("besleme_saplamasi"), int):
                    raise KeyError("besleme_saplamasi yazılı değil")
                return str(k["besleme_saplamasi"])
            for n, lst in (k.get("yerlesim") or {}).items():
                if any(x.split("/")[0] == anahtar for x in lst):
                    return n
            raise KeyError("kablo %s anahtarlı bara yerleşiminde yok" % anahtar)
        if tur == "kontak":
            a, _, uc = anahtar.partition(":")                           # düzeltme turu 2 (F10i-kontrol-2 B23): tek uç "K2:giris"
            u = (self.T["anahtarlar"].get("%s-kontak" % a) or {}).get("uclar")
            if not isinstance(u, dict) or not u.get("giris") or not u.get("cikis"):
                raise KeyError("anahtarlar.%s-kontak.uclar yok" % a)
            if uc:
                if uc not in ("giris", "cikis", "bos") or not u.get(uc):
                    raise KeyError("anahtarlar.%s-kontak.uclar.%s yok" % (a, uc))
                return u[uc]
            return "%s → %s" % (u["giris"], u["cikis"]) + (" (%s boş)" % u["bos"] if u.get("bos") else "")
        if tur == "parca":                                              # düzeltme turu 2 (F10i-kontrol-2 B18): damar ucunun parçası
            p = anahtar.split(":")
            if len(p) != 3 or p[2] not in ("a", "b"):
                raise KeyError("{parca.%s}: biçim <kablo>:<damar adı, boşluk yerine _>:<a|b>" % anahtar)
            d = [x for x in (self.K.get(p[0]) or {}).get("damarlar", []) if x["ad"] == p[1].replace("_", " ")]
            if len(d) != 1 or " · " not in d[0][p[2]]:
                raise KeyError("kablo %s damarı '%s' yok ya da ucunda 'parça · nokta' yok" % (p[0], p[1].replace("_", " ")))
            s = d[0][p[2]].split(" · ", 1)[0]
            return s[0].lower() + s[1:] if len(s) > 1 and s[1].islower() else s
        if tur == "yer":
            y = (self.KOR.get(anahtar) or {}).get("yer")
            if not y:
                raise KeyError("koruyucu %s yer alanı yok" % anahtar)
            return y.split(":")[0].strip()
        if tur == "yon":
            e = self.T.get("kondansatorler") if anahtar == "kondansator" else (self.T.get("tvs") or {}).get(anahtar)
            if not isinstance(e, dict) or not e.get("yon"):
                raise KeyError("%s yönü kayıtta yok (tvs / kondansatorler.yon)" % anahtar)
            return e["yon"]
        if tur == "uc":                                                 # düzeltme turu 1: damarın bir ucu ("X01:PC817_çıkış_beslemesi:b")
            p = anahtar.split(":")
            if len(p) != 3 or p[2] not in ("a", "b"):
                raise KeyError("{uc.%s}: biçim <kablo>:<damar adı, boşluk yerine _>:<a|b>" % anahtar)
            r = self.K.get(p[0])
            d = [x for x in (r or {}).get("damarlar", []) if x["ad"] == p[1].replace("_", " ")]
            if len(d) != 1:
                raise KeyError("kablo %s damarı '%s' yok" % (p[0], p[1].replace("_", " ")))
            return d[0][p[2]].split(" · ", 1)[-1]
        if tur == "kutup":                                              # düzeltme turu 1: iki damarlı güç kablosunun kutbu, damarlardan
            r = self.K.get(anahtar) or {}
            d = r.get("damarlar") or []
            ar = [x for x in d if x["ad"] in ("+", "V+")]
            ek = [x for x in d if x["ad"] in ("−", "GND")]
            if len(ar) != 1 or len(ek) != 1:
                raise KeyError("kablo %s'de tek + / V+ ve tek − / GND damarı yok" % anahtar)
            n = lambda s: s.split(" · ", 1)[-1]
            return "%s → %s, %s → %s" % (n(ar[0]["a"]), n(ar[0]["b"]), n(ek[0]["a"]), n(ek[0]["b"]))
        if tur in ("oran", "v") and anahtar in ("aku_olcum", "aku_aralik"):   # düzeltme turu 1 (A1, A4): akü ölçüm bölücüsü
            m = re.search(r"\| Akü gerilimi \| (\d+) kΩ / (\d+) kΩ", self.EL)
            m2 = re.search(r"akü (\d+,\d+)–(\d+,\d+) V", self.EL)
            if not m or not m2:
                raise KeyError("elektrik.md E2 'Akü gerilimi | N kΩ / M kΩ' ya da 'akü a–b V' yok")
            ust, alt = float(m.group(1)), float(m.group(2))
            r = alt / (ust + alt)
            a1, a2 = (float(x.replace(",", ".")) for x in m2.groups())
            if ("%s kΩ" % m.group(1)) != self.deger("ohm", "aku_olcum"):
                raise KeyError("elektrik.md E2 üst direnci (%s kΩ) koruyucular.R-aku-olcum ile aynı değil" % m.group(1))
            # düzeltme turu 2 (F10i-kontrol-2 B27): bölücü değişince "beklenen" aralık sessizce ADC sınırını aşmasın. Akü üst
            # sınırı ve ADC doğrusal sınırı aynı satırdan ("14,6 V → …", "doğrusal bölge ≤ 2,45 V"); kablolar_denetim de sınar.
            sat = re.search(r"\| Akü gerilimi \|[^\n]*", self.EL).group(0)
            ust_v = [float(x.replace(",", ".")) for x in re.findall(r"(\d+(?:,\d+)?) V →", sat)]
            sinir = re.search(r"doğrusal bölge ≤ (\d+(?:,\d+)?) V", sat)
            if not ust_v or not sinir:
                raise KeyError("elektrik.md E2 'Akü gerilimi' satırında 'N V →' ya da 'doğrusal bölge ≤ N V' yok")
            if max(ust_v) * r > float(sinir.group(1).replace(",", ".")):
                raise KeyError("akü ölçüm bölücüsü: %g V × %.4f = %.2f V, ADC doğrusal sınırı %s V'u aşıyor" % (
                    max(ust_v), r, max(ust_v) * r, sinir.group(1)))
            yuv = lambda x: ("%.2f" % (int(x * 100 + 0.5) / 100.0)).replace(".", ",")
            if tur == "oran":
                return ("%.4f" % r).replace(".", ",")
            if anahtar == "aku_aralik":
                return "%s–%s V" % (m2.group(1), m2.group(2))
            return "%s–%s V" % (yuv(a1 * r), yuv(a2 * r))
        if tur == "vida":                                               # düzeltme turu 1 (A14): saplama ölçüsü (varsayım, teyitli)
            sp = (self.T["anahtarlar"].get(anahtar) or {}).get("saplama") or {}
            if not sp.get("olcu"):
                raise KeyError("anahtarlar.%s.saplama.olcu yok" % anahtar)
            return sp["olcu"]
        if tur == "saplama":
            if anahtar == "sayi":
                return str(self.BP["dugumler"]["Yıldız barası · GND"])
            if anahtar == "bara":
                return str(self.BP["dugumler"]["Anahtarlı bara · +"])
            if anahtar == "pabuc":
                return str(self.BP["saplama_basina_en_cok_pabuc"])
            y = self.BP["kopruler"]["Yıldız barası · GND"]["yerlesim"]
            for n, lst in y.items():
                if any(x.split("/")[0] == anahtar for x in lst):
                    return n
            raise KeyError("kablo %s yıldız yerleşiminde yok" % anahtar)
        if tur == "ms":
            m = re.search(r"en az (\d+) ms bekle \(boş akü için (\d+) ms önerilir", self.EL)
            m2 = re.search(r"\(5\) (\d+) ms sonra GPIO\d+ = 0", self.EL)
            v = {"onsarj": m and m.group(1), "onsarj_bos": m and m.group(2), "k1_sonra": m2 and m2.group(1)}.get(anahtar)
            if not v:
                raise KeyError("E9 dizisinde %s bulunamadı (elektrik.md)" % anahtar)
            return "%s ms" % v
        if tur == "s" and anahtar == "k2_en_cok":
            return "%s s" % _sayi_metin(self.PH["pinler"]["ROLE_K2_ONSARJ"]["en_cok_ms"] / 1000.0)
        raise KeyError("bilinmeyen yer tutucu türü %s" % tur)

    # ------------------------------------------------------------ anahtar ↔ bağlam (açık iş 2): yer tutucunun gösterdiği varlığın adı
    # Her yer tutucu üyesi için cümlede geçmesi gereken adlar (biri yeter), tablodan türer: kablo kimliği (aralık "G01–G04" ve grup
    # sayılır); koruyucu kimliği (F1–F6; hat-X → X / XL4016 X ve o koruyucuyla korunan kabloların kimlikleri); pin haritasındaki ucun adı
    # ("role surucusu #n" → K<n> / BC337-40 #n, "PC817 #n") ve pin adının parçaları (ONSARJ → ön şarj, ACIL_STOP → acil stop / mantar,
    # BARA → bara); direnç / süre anahtarının adı (seri, taban, ön şarj; E9: en az / bekle, boş, K1; K2).
    _PIN_PARCA = {"ONSARJ": ["ön şarj"], "ACIL_STOP": ["acil stop", "mantar"], "BARA": ["bara"]}
    _KOR_AD = {"sarj": ["şarj"], "cevre": ["çevre"], "sigorta": ["ana sigorta"]}
    _OZEL = {("ohm", "seri"): ["seri"], ("ohm", "taban"): ["taban"], ("ohm", "onsarj"): ["ön şarj"],
             ("ms", "onsarj"): ["en az", "bekle"], ("ms", "onsarj_bos"): ["boş"], ("ms", "k1_sonra"): ["K1"],
             ("s", "k2_en_cok"): ["K2"], ("kopru", "yildiz"): ["yıldız"], ("saplama", "sayi"): ["yıldız barası"],
             ("saplama", "bara"): ["anahtarlı bara"], ("saplama", "pabuc"): ["pabuç"], ("kopru", "bara"): ["anahtarlı bara"]}
    for _t in ("kopru_adet", "kopru_renk", "kopru_boy"):
        _OZEL[(_t, "yildiz")] = ["yıldız"]
        _OZEL[(_t, "bara")] = ["anahtarlı bara"]
    _OZEL[("kopru_adet", "toplam")] = ["köprü"]
    _OZEL[("kopru_pabuc", "toplam")] = ["pabuç"]
    # P10.7b2a: yeni yer tutucuların bağlam adları
    _OZEL[("ohm", "aku_olcum")] = ["akü ölçüm"]
    _OZEL[("bsaplama", "besleme")] = ["anahtarlı bara"]
    _OZEL[("saplama", "besleme")] = ["yıldız"]
    _OZEL[("kontak", "K1")] = ["K1"]
    _OZEL[("kontak", "K2")] = ["K2"]
    _OZEL[("yon", "kondansator")] = ["kondansatör"]
    # düzeltme turu 1
    _OZEL[("oran", "aku_olcum")] = ["bölücü"]
    _OZEL[("v", "aku_olcum")] = ["bölücü"]
    _OZEL[("v", "aku_aralik")] = ["akü"]
    _OZEL[("vida", "ana-anahtar")] = ["ana anahtar", "anahtar"]
    del _t

    def teyit_kaydi(self, tur, anahtar):
        """Yer tutucunun gösterdiği kayıt 'kablajda teyit' işaretliyse teyit metni, değilse None (düzeltme turu 1, F10i-kontrol A6)."""
        e = None
        if tur == "yon":
            e = self.T.get("kondansatorler") if anahtar == "kondansator" else (self.T.get("tvs") or {}).get(anahtar)
        elif tur == "kontak":
            e = (self.T["anahtarlar"].get("%s-kontak" % anahtar.split(":")[0]) or {}).get("uclar")
        elif tur == "vida":
            e = (self.T["anahtarlar"].get(anahtar) or {}).get("saplama")
        t = str((e or {}).get("teyit") or "")
        return t if "kablajda teyit" in t else None

    def varlik_adlari(self, tur, uye):
        if (tur, uye) in self._OZEL:
            return list(self._OZEL[(tur, uye)])
        if tur in ("uc", "kutup", "parca"):                             # düzeltme turu 1: kablonun kimliği (turu 2: parca)
            return [uye.split(":")[0]]
        if tur == "kontak" and ":" in uye:                              # düzeltme turu 2: tek uç ("K2:giris") rölenin adıyla
            return self.varlik_adlari(tur, uye.split(":")[0])
        if tur in ("awg", "saplama", "kopru", "ara", "yeniden", "bsaplama"):
            return [uye]
        if tur == "yon":                                                # TVS: parçanın adı (P6KE18A / P6KE6V8A)
            e = (self.T.get("tvs") or {}).get(uye) or {}
            return [e["parca"]] if e.get("parca") else []
        if tur == "yer":                                                # koruyucunun adları ({a.…} ile aynı)
            return self.varlik_adlari("a", uye)
        if tur in ("a", "bicak", "yuva"):
            if re.fullmatch(r"F\d", uye):
                return [uye]
            ad = uye.split("-", 1)[-1]
            out = self._KOR_AD.get(ad, [ad])
            if re.fullmatch(r"[A-Z]", ad):
                out = ["XL4016 " + ad, "hat " + ad, ad]
            return out + [r["kimlik"] for r in self.T["kablolar"] if r.get("koruma") == uye]
        if tur == "gpio":
            p = self.PH["pinler"].get(uye, {})
            out = []
            m = re.search(r"role surucusu #(\d)", p.get("uc") or "")
            if m:
                out += ["K" + m.group(1), "BC337-40 #" + m.group(1)]
            m = re.search(r"PC817 #(\d)", p.get("uc") or "")
            if m:
                out.append("PC817 #" + m.group(1))
            for k, v in self._PIN_PARCA.items():
                if k in uye:
                    out += v
            return out
        return []

    @staticmethod
    def _kucuk(s):
        return (s or "").replace("İ", "i").replace("I", "ı").lower()

    def cumle_kimlikleri(self, cumle):
        """Cümlede adı geçen kablo kimlikleri; aralıklar ("G01–G04", "SV1–SV3") açılır."""
        k = set(re.findall(r"\b([A-Z]{1,2}\d{1,2})\b", cumle))
        for m in re.finditer(r"\b([A-Z]{1,2})(\d{1,2})\s?[–-]\s?(?:\1)?(\d{1,2})\b", cumle):
            w = len(m.group(2))
            for n in range(int(m.group(2)), int(m.group(3)) + 1):
                k.add("%s%0*d" % (m.group(1), w, n))
        return k

    def varlik_eksik(self, tur, anahtar, cumle):
        """Yer tutucunun (grupsa her üyenin) adı cümlede geçmiyorsa eksik üyeler listesi. Yer tutucuların kendi metni (ör. "{awg.G01}"
        içindeki "G01") ad sayılmaz."""
        cumle = YER_TUTUCU.sub(" ", cumle or "")
        kim = self.cumle_kimlikleri(cumle)
        kc = self._kucuk(cumle)
        eksik = []
        for u in anahtar.split("|"):
            adlar = self.varlik_adlari(tur, u)
            ok = False
            for a in adlar:
                if a in kim:
                    ok = True
                elif re.fullmatch(r"[A-Z]", a):
                    ok = bool(re.search(r"(?<![\w{.])%s(?![\w}])" % a, cumle))
                elif not re.fullmatch(r"[A-Z]{1,2}\d{1,2}", a):
                    ok = bool(re.search(r"(?<!\w)%s" % re.escape(self._kucuk(a)), kc))
                if ok:
                    break
            if not ok:
                eksik.append(u)
        return eksik

    def coz(self, metin, hatalar=None, yer=""):
        """Metindeki yer tutucuları doldur. Çözülemeyen '⟦?tür.anahtar⟧' kalır ve hatalar listesine yazılır."""
        if not metin or "{" not in metin:
            return metin

        def r(m):
            try:
                return self.deger(m.group(1), m.group(2))
            except (KeyError, TypeError) as e:
                if hatalar is not None:
                    hatalar.append("%s: {%s.%s} çözülemedi (%s)" % (yer, m.group(1), m.group(2), e))
                return "⟦?%s.%s⟧" % (m.group(1), m.group(2))
        return YER_TUTUCU.sub(r, metin)

    def desen(self, d):
        """Düzenli ifade desenindeki yer tutucuları (re.escape'li) değerle doldur (ZORUNLU uyarı desenleri için)."""
        return YER_TUTUCU.sub(lambda m: re.escape(self.deger(m.group(1), m.group(2))), d)


_D = None


def degerler():
    global _D
    if _D is None:
        _D = Degerler()
    return _D
