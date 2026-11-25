"""The one result type all three methods return."""

from dataclasses import dataclass, field
from typing import Optional

GOOD, BAD = "GOOD", "BAD"


@dataclass
class Result:
    method: str                 # "ks", "vision" or "hydra"
    histogram: str              # path inside the DQM file, e.g. crvRecoDQM/PEr
    verdict: Optional[str]      # GOOD, BAD, or None if the method gave no verdict
    score: Optional[float]      # ks: KS probability; hydra: P(BAD); vision: None
    detail: str = ""            # ks: status name; vision: the model's full answer; hydra: model file
    evidence: dict = field(default_factory=dict)   # method-specific numbers behind the verdict

    def row(self) -> dict:
        """One flat CSV row (evidence left out: it differs per method)."""
        return {"method": self.method, "histogram": self.histogram, "verdict": self.verdict,
                "score": self.score, "detail": self.detail}


def short_name(path: str) -> str:
    """crvRecoDQM/PEr -> PEr (how instructions and hydra models are keyed)."""
    return path.rstrip("/").rsplit("/", 1)[-1]
