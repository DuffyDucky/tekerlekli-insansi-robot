# P10.8g: parça etiketi yazısının basılı (PDF) boyu, ÖLÇÜM. Yalnız okur.
# 1) PDF'teki her görüntü PyMuPDF ile çıkarılır; parça etiketli her yazdırma karesi (rehber/goruntu/adim-NN[-JJ].png) PDF'teki
#    görüntüyle piksel karşılaştırmasıyla eşlenir (en küçük ortalama fark; eşleşme farkı yazılır), sayfası ve basılı genişliği bulunur:
#    ölçek = basılı genişlik (pt) / görüntü genişliği (px).
# 2) Yazı boyu (em): etiket ölçümünün (P108f-etiket-olc.py JSON'u, teslim edilen kare) yazi_px × ölçek.
# 3) Göz için ikinci ölçü: PDF'ten çıkarılan görüntüde her yazı kutusunun içindeki koyu piksellerin (parlaklık < 110) yüksekliği × ölçek
#    (büyük harf / rakam yüksekliği ≈ 0,7 em; "ğ", "ü" gibi harflerde daha büyük). Kutunun görüntüdeki yeri ölçümdeki kutu + tuvalin
#    görüntüdeki kayması (beyaz kutu dolgusuyla aranır, ±40 px).
# Ölçüt (rehber): yazdir.html basılı en küçük yazı 8,1 pt; rehber_uret.py YAZI_ALT_PT = 8 (PDF metni). Yazı (em) ≥ 8,0 pt değilse KALDI.
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108g-yazi-pt.py --olc JSON [--pdf PDF] [--kare DIR] [--json YOL]
import argparse, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
ALT_PT = 8.0


def main():
    import fitz
    from PIL import Image, ImageChops, ImageStat
    ap = argparse.ArgumentParser()
    ap.add_argument("--olc", required=True)
    ap.add_argument("--pdf", default=os.path.join(ROBOT, "planlama", "rehber", "Lale-montaj-rehberi.pdf"))
    ap.add_argument("--kare", default=os.path.join(ROBOT, "rehber", "goruntu"))
    ap.add_argument("--json")
    g = ap.parse_args()
    olc = json.load(open(g.olc, encoding="utf-8"))["olcum"]
    doc = fitz.open(g.pdf)
    gor = []                                                  # (sayfa, bbox, PIL görüntü)
    for pno in range(len(doc)):
        for info in doc[pno].get_image_info(xrefs=True):
            if not info.get("xref"):
                continue
            pm = fitz.Pixmap(doc, info["xref"])
            if pm.n - pm.alpha != 3:
                pm = fitz.Pixmap(fitz.csRGB, pm)
            im = Image.open(io.BytesIO(pm.tobytes("png"))).convert("RGB")
            gor.append((pno + 1, info["bbox"], im))
    sonuc, hata = [], []
    for ad, o in sorted(olc.items()):
        s = o.get("sahne") or {}
        s_, j = (ad.split(".") + ["0"])[:2]
        yol = os.path.join(g.kare, "adim-%02d-%02d.png" % (int(s_), int(j)) if int(j) else "adim-%02d.png" % int(s_))
        kare = Image.open(yol).convert("RGB")
        en = None
        for pno, bb, im in gor:
            if im.size != kare.size:
                continue
            f = sum(ImageStat.Stat(ImageChops.difference(im, kare)).mean) / 3
            if en is None or f < en[0]:
                en = (f, pno, bb, im)
        if en is None:
            hata.append("%s: PDF'te eşleşen görüntü yok" % ad)
            continue
        f, pno, bb, im = en
        olcek = (bb[2] - bb[0]) / im.size[0]
        px = s.get("yazi_px")
        # tuvalin görüntüdeki kayması: beyaz kutu dolgusunun en çok örtüştüğü (dx, dy)
        kutular = [u["kutu"] for u in s.get("ciz") or []]
        gri = im.convert("L")
        P = gri.load()
        W, H = gri.size

        def beyaz(dx, dy):
            n = 0
            for k in kutular:
                for t in range(9):
                    x = int(k["x0"] + 4 + (k["x1"] - k["x0"] - 8) * (t % 3) / 2 + dx)
                    y = int(k["y0"] + 3 + (k["y1"] - k["y0"] - 6) * (t // 3) / 2 + dy)
                    if 0 <= x < W and 0 <= y < H and P[x, y] >= 250:
                        n += 1
            return n
        tv = s.get("tuval") or {}
        if "x" in tv:                                         # P108f-etiket-olc (P10.8g) tuvalin sayfadaki yerini ölçer
            kay = (round(tv["x"]), round(tv["y"]))
        else:
            kay = max(((dx, dy) for dx in range(-40, 41, 2) for dy in range(-40, 41, 2)), key=lambda d: (beyaz(*d), -abs(d[0]) - abs(d[1])))
        yaz = []
        for u in s.get("ciz") or []:
            k = u["kutu"]
            x0, x1 = int(k["x0"] + kay[0] + 3), int(k["x1"] + kay[0] - 3)
            y0, y1 = int(k["y0"] + kay[1] + 3), int(k["y1"] + kay[1] - 3)
            sat = [y for y in range(max(0, y0), min(H, y1)) if any(P[x, y] < 110 for x in range(max(0, x0), min(W, x1)))]
            gy = (max(sat) - min(sat) + 1) if sat else 0
            yaz.append(dict(t=u["t"], koyu_px=gy, koyu_pt=round(gy * olcek, 2)))
        em_pt = round(px * olcek, 2) if px else None
        r = dict(konum=ad, kare=os.path.relpath(yol, ROBOT).replace("\\", "/"), pdf_sayfa=pno, eslesme_ort_fark=round(f, 3),
                 basili_genislik_pt=round(bb[2] - bb[0], 2), basili_genislik_mm=round((bb[2] - bb[0]) / 72 * 25.4, 1),
                 olcek_pt_px=round(olcek, 4), yazi_px=px, yazi_pt=em_pt, kayma=kay, yazilar=yaz)
        sonuc.append(r)
        if em_pt is None or em_pt < ALT_PT:
            hata.append("%s: yazı %s pt < %s pt" % (ad, em_pt, ALT_PT))
        if not yaz or min(y["koyu_px"] for y in yaz) == 0:
            hata.append("%s: kutu içinde yazı pikseli bulunamadı" % ad)
        print("%-5s PDF s.%-3d genislik %.1f mm, %.4f pt/px, esleme farki %.3f; yazi %s px = %s pt; koyu yukseklik %s pt (kayma %s)" % (
            ad, pno, r["basili_genislik_mm"], olcek, f, px, em_pt,
            "/".join("%s:%s" % (y["t"], y["koyu_pt"]) for y in yaz), kay))
    for h in hata:
        print("  HATA", h)
    print("yazi boyu: %d konum; alt sinir %s pt; hata %d -> %s" % (len(sonuc), ALT_PT, len(hata), "GECTI" if not hata else "KALDI"))
    if g.json:
        json.dump(dict(konum=sonuc, hata=hata, alt_sinir_pt=ALT_PT, pdf=os.path.relpath(g.pdf, ROBOT).replace("\\", "/")),
                  open(g.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.exit(0 if not hata else 2)


if __name__ == "__main__":
    main()
