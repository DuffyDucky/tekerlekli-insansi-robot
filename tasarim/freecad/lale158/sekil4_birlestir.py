# Lale 1,58 m - sekil4_gorsel.py ciktilarini kirpar, on + yan gorunumu tek PNG yapar (sistem Python'u + Pillow, FreeCAD acmaz) -> gorsel/sekil4-on-yan.png
import os
from PIL import Image, ImageChops

G = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gorsel")


def kirp(ad, pay=40):
    im = Image.open(os.path.join(G, ad)).convert("RGB")
    bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop((max(bb[0] - pay, 0), max(bb[1] - pay, 0), min(bb[2] + pay, im.width), min(bb[3] + pay, im.height)))


on, yan = kirp("sekil4-on.png"), kirp("sekil4-yan.png")
H = max(on.height, yan.height)
c = Image.new("RGB", (on.width + yan.width + 120, H), (255, 255, 255))
c.paste(on, (0, H - on.height))
c.paste(yan, (on.width + 120, H - yan.height))
c.save(os.path.join(G, "sekil4-on-yan.png"))
print(on.size, yan.size, c.size)
