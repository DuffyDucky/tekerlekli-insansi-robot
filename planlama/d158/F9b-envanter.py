# -*- coding: utf-8 -*-
"""
F9b envanteri: F9b oncesi demo sayfasindaki (git HEAD:tasarim/Robot-Tasarim-Demosu.html) sayilari sayar.

  py -3 planlama/d158/F9b-envanter.py

Sayilan: (a) HTML govde metni (script/style disi), (b) satir ici betiklerdeki metin sabitleri ("..." ve '...'),
bolume gore. Gomulu model JSON'u (CadQuery parca aglari) ve maliyet JSON'u ayri sayilir; onlar metin degil veridir.
Harfe bitisik sayilar (DS3218, V3, 3B) ad sayilir ve sayilmaz. Gunlukteki envanter tablosu bu sayima dayanir.
"""
import json
import re
import subprocess
import sys
from html.parser import HTMLParser

YOL = "tasarim/Robot-Tasarim-Demosu.html"
SAYI = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*(?![\w])")


def head():
    return subprocess.run(["git", "show", "HEAD:" + YOL], capture_output=True, check=True).stdout.decode("utf-8")


class Metin(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.y, self.govde, self.betik, self.bolum = [], False, [], "ust"
        self.metin = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "body":
            self.govde = True
        if a.get("id") in ("maliyet", "govde-ekrani") or (tag == "footer"):
            self.bolum = a.get("id") or "footer"
        if tag in ("script", "style"):
            self.y.append((tag, a.get("id")))
            self.betik.append([a.get("id"), ""])

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.y:
            self.y.pop()

    def handle_data(self, d):
        if self.y:
            if self.y[-1][0] == "script":
                self.betik[-1][1] += d
            return
        if self.govde:
            self.metin.setdefault(self.bolum, []).append(d)


def main():
    h = head()
    m = Metin()
    m.feed(h)
    print("F9b oncesi sayfa (HEAD), %d bayt" % len(h.encode("utf-8")))
    top = 0
    for b, parca in m.metin.items():
        n = len(SAYI.findall(" ".join(parca)))
        top += n
        print("  HTML metni  %-14s %4d sayi" % (b, n))
    for bid, kod in m.betik:
        if bid == "model":
            md = json.loads(kod)
            print("  model JSON (CadQuery V1-V3): %d parca, C sabitleri %d, check %s" % (
                len(md["parts"]), len(md["C"]), {k: round(v["mass"], 2) for k, v in md["check"].items()}))
            continue
        if bid == "cost":
            cd = json.loads(kod)
            print("  maliyet JSON: %d kalem, tarih %s (planlama/maliyet.json ile ayni mi: %s)" % (
                len(cd["kalemler"]), cd.get("tarih"), cd == json.load(open("planlama/maliyet.json", encoding="utf-8"))))
            continue
        sabit = re.findall(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'', kod)
        n = sum(len(SAYI.findall(s)) for s in sabit)
        top += n
        print("  betik %-12s metin sabitlerinde %4d sayi (%d sabit)" % (bid or "satir-ici", n, len(sabit)))
    print("  TOPLAM (HTML metni + betik sabitleri): %d sayi" % top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
