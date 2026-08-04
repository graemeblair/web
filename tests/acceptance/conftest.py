import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent

# The acceptance helpers are plain scripts, importable as siblings.
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
