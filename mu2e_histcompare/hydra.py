"""
Method 3: Hydra-style CNN (mu2e-hydra submodule, Python package `hydra_mu2e`)

One small image classifier per histogram, trained beforehand by mu2e-hydra
(python -m hydra_mu2e.realdata run ..., which saves <out>/models/<name>.pt).
Like JLab's Hydra it sees only the input plot, so the reference run is not used.
The output is P(BAD); the verdict is BAD above the threshold.
"""

from functools import lru_cache
from pathlib import Path

import numpy as np
import torch

from hydra_mu2e.model import PlotCNN, predict
from hydra_mu2e.render import SIZE, render

from .result import BAD, GOOD, Result, short_name

THRESHOLD = 0.5


@lru_cache(maxsize=None)
def load_model(path: str) -> PlotCNN:
    model = PlotCNN(size=SIZE)
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    model.eval()
    return model


def model_path(models_dir, path: str) -> Path:
    return Path(models_dir) / f"{short_name(path)}.pt"


def compare(hist, path: str, models_dir, threshold: float = THRESHOLD) -> Result:
    """hist: hist.Hist; models_dir: a mu2e-hydra results/<name>/models directory."""
    mp = model_path(models_dir, path)
    if not mp.exists():
        return Result("hydra", path, None, None, f"no model {mp}")
    counts = np.asarray(hist.values(), dtype=float)
    edges = np.asarray(hist.axes[0].edges, dtype=float)
    img = render(counts, edges)
    p = float(predict(load_model(str(mp)), img[None, None])[0])
    return Result("hydra", path, BAD if p > threshold else GOOD, p, str(mp))
