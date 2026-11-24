"""konumlama testleri. Koşmak: `py -3 kod\\fizik\\konumlama\\kos.py` (ya da kod\\fizik içinden `python -m konumlama.testler`)."""

import os
import sys

FIZIK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if FIZIK not in sys.path:
    sys.path.insert(0, FIZIK)
