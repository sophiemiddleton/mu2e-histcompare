"""Plot instructions for the vision method: mu2e-vision's instructions/*.yaml, bundled.

    from mu2e_histcompare import instructions
    plots = instructions.load("crv_real_draft")      # a bundled name, or a path to a YAML
"""

from pathlib import Path
from typing import Dict, List

import yaml

_HERE = Path(__file__).resolve().parent
# installed wheel: copied next to this package; source checkout or editable: the submodule
_DIRS = (_HERE / "_instructions", _HERE.parent / "mu2e-vision" / "instructions")


def available() -> List[str]:
    """Names of the bundled instruction files."""
    return sorted({p.stem for d in _DIRS if d.is_dir() for p in d.glob("*.yaml")})


def path(name_or_path: str) -> Path:
    """A bundled name (crv_real_draft) or an existing file -> its path."""
    p = Path(name_or_path)
    if p.suffix in (".yaml", ".yml") and p.is_file():
        return p
    for d in _DIRS:
        f = d / f"{p.stem}.yaml"
        if f.is_file():
            return f
    raise FileNotFoundError(f"no instructions {name_or_path!r}; bundled: {available()}")


def load(name_or_path: str) -> Dict[str, dict]:
    """Plot name -> its instruction entry (the `plots` mapping of the YAML)."""
    with open(path(name_or_path)) as f:
        return yaml.safe_load(f)["plots"]
