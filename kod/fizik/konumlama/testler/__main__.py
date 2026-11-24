"""`python -m konumlama.testler` (kod\\fizik içinden) = kos.py."""

import os
import runpy

runpy.run_path(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kos.py"), run_name="__main__")
