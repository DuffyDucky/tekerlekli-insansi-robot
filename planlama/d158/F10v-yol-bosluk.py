# F10v (P10.7b2j tasarim turu 2): taban CAD kablo yollari x parca gercek geometri boslugu (FreeCAD; taban_parcalar.py'yi ice aktarir).
# Her "Kablo yolu N" tupu (r 2,5) ile Referans olmayan her parca arasi en kisa mesafe (distToShape; 0 = degiyor / giriyor). Yolun uc
# ve ara parcalari (izinli: kablonun gercekten bagli oldugu ya da icinden gectigi parca) ayri listelenir. Yol 9 ve 12 rehberin cizdigi
# (kirpilmis) bolumle de olculur. Kosu: FC_SCRIPT=<bu dosya> freecadcmd run_fc.py ; cikti F10v-yol-bosluk.json (bu klasorde).
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "tasarim", "freecad")
for p in (os.path.join(FC, "taban"), FC):
    if p not in sys.path:
        sys.path.insert(0, p)
import Part
import FreeCAD as App
import taban_parcalar as TP

IZIN = {
    1: r"^(Aku LiFePO4|Ana sigorta|Ana anahtar|Sigorta kutusu)",
    2: r"^(Aku LiFePO4|.*\(yildiz 3\)$|Bara tutucusu yildiz)",
    3: r"^(Sigorta kutusu|Role 12|.*\(anahtarli [123]\)$|.*\(yildiz 1\)$|Bara tutucusu|BTS7960 motor surucu sol$|Motor JGB37-520 \(on sol\)|Motor braketi L 37 mm \(on sol\))",
    4: r"^(.*\((anahtarli|yildiz) 2\)$|Bara tutucusu|BTS7960 motor surucu sag$|Motor JGB37-520 \((on|arka) sag\)|Motor braketi L 37 mm \((on|arka) sag\))",
    5: r"^(.*\((anahtarli|yildiz) 1\)$|Bara tutucusu|XL4016 servo 6 V A|.*Servo dagitim karti A)",
    6: r"^$",
    7: r"^(.*\((anahtarli|yildiz) 1\)$|Bara tutucusu|XL4016 servo 6 V B|.*Servo dagitim karti B)",
    8: r"^(Sigorta kutusu|.*\(yildiz 4\)$|Bara tutucusu yildiz)",
    9: r"^(Sigorta kutusu|.*\(yildiz 4\)$|Bara tutucusu yildiz|XL4016 cevre|ESP32)",
    10: r"^(Sigorta kutusu|Acil stop|Role 12|Arayuz karti)",
    11: r"^(Sonar|Arayuz karti|ESP32)",
    12: r"^(BTS7960 motor surucu sol$|ESP32)",
}
KIRP = {9: 12, 12: 2}          # rehberin cizdigi son nokta (rehber_kablo CAD_KIRP son; 9: bu turda 3 -> 12)
PAY = 15.0


def tup(pts, r=2.5):
    return TP.tup(pts, r)


def yakin(bb, q):
    return not (bb.XMax + PAY < q.XMin or q.XMax + PAY < bb.XMin or bb.YMax + PAY < q.YMin or q.YMax + PAY < bb.YMin
                or bb.ZMax + PAY < q.ZMin or q.ZMax + PAY < bb.ZMin)


parcalar = [p for p in TP.P if p["tur"] != "Referans"]
out = {}
for n, (devre, renk, pts) in enumerate(TP.YOL, 1):
    for etk, nk in (("tam", None), ("rehber", KIRP.get(n))):
        if etk == "rehber" and nk is None:
            continue
        sh = tup(pts[:nk + 1] if nk is not None else pts)
        iz = re.compile(IZIN[n])
        kayit = []
        for p in parcalar:
            if not yakin(sh.BoundBox, p["shape"].BoundBox):
                continue
            d = sh.distToShape(p["shape"])[0]
            if d < PAY:
                kayit.append((round(d, 2), p["ad"], bool(iz.search(p["ad"]))))
        kayit.sort()
        yab = [k for k in kayit if not k[2]]
        out["%d %s" % (n, etk)] = dict(devre=devre, en_dar_yabanci=yab[:6], izinli_temas=[k for k in kayit if k[2] and k[0] < 0.5][:12])
        print("yol %d %s: en dar yabanci %s" % (n, etk, yab[:3]))
json.dump(out, open(os.path.join(HERE, "F10v-yol-bosluk.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("BITTI")
