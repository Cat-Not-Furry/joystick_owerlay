"""Inserta arcade/engine en sys.path para entrypoints en la raíz del repo."""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
_engine = _root / "arcade" / "engine"
_s = str(_engine)
if _s not in sys.path:
	sys.path.insert(0, _s)
