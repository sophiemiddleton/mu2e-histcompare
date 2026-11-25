"""The one result type all three methods return."""

from dataclasses import asdict, dataclass
from typing import Optional

GOOD, BAD = "GOOD", "BAD"


@dataclass
class Result:
    method: str                 # "ks", "vision" or "hydra"
    histogram: str              # path inside the DQM file, e.g. crvRecoDQM/PEr
    verdict: Optional[str]      # GOOD, BAD, or None if the method gave no verdict
    score: Optional[float]      # ks: KS probability; hydra: P(BAD); vision: None
    detail: str = ""            # ks: status name; vision: the model's full answer; hydra: model file

    def row(self) -> dict:
        return asdict(self)


def short_name(path: str) -> str:
    """crvRecoDQM/PEr -> PEr (how instructions and hydra models are keyed)."""
    return path.rstrip("/").rsplit("/", 1)[-1]
