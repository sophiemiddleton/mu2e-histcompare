"""
Method 1, the standard: Kolmogorov-Smirnov test against the reference run

This is Mu2e/DQM's own dqm.hist.compare. Its default thresholds (0.999 / 0.99) are meant for
comparing a sample with itself, e.g. a validation rerun. Two independent runs need
p-value thresholds, so the defaults here are the ones mu2e-vision's benchmark uses (0.05 / 0.01).
The verdict is GOOD unless the comparison fails; None when it can't be made (e.g. different
binning).
"""

from dqm.hist.compare import ComparePars, CompareStatus, compare_histograms

from .result import BAD, GOOD, Result

TIGHT, LOOSE = 0.05, 0.01


def compare(hist, ref, path: str = "", tight: float = TIGHT, loose: float = LOOSE) -> Result:
    """hist, ref: hist.Hist objects (as dqm.hist.read.HistFile.read returns them)."""
    pars = ComparePars(independent=True, tight=tight, loose=loose)
    cmp = compare_histograms(ref, hist, pars, path=path)
    detail = cmp.status.name + (f": {cmp.note}" if cmp.note else "")
    if cmp.status == CompareStatus.cantCompare:
        verdict = None
    else:
        verdict = GOOD if cmp.ok else BAD
    # cmp.fraction = 1 - largest |difference| of the normalised cumulative sums
    evidence = {"status": cmp.status.name, "ks_probability": float(cmp.kolmogorov),
                "max_cdf_difference": round(1.0 - float(cmp.fraction), 4),
                "tight": tight, "loose": loose, "note": cmp.note}
    return Result("ks", path, verdict, float(cmp.kolmogorov), detail, evidence)
