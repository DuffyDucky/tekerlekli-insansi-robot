"""Lale labirent keşif beyni: hafif SLAM (log-odds ızgara + tarama-harita eşleştirme), sınır tabanlı keşif,
BFS / dalga cephesi planlama ve hızlı 2B benzetici. Yalnız numpy + standart kitaplık. Ayrıntı: BENIOKU.md.

Gezinme düzeneği için: `kesif.beyin:KesifBeyni` (parametresiz kurulur) ya da `kesif.beyin.olustur(sahne_adi)`.
"""
from . import _yol  # noqa: F401  (kod/fizik sys.path'te olsun: konumlama içe aktarılabilsin)
