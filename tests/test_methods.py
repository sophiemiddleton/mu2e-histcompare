"""The three methods on toy histograms. Vision uses a stand-in reviewer (no model call);
hydra uses an untrained CNN saved to a temporary directory, so only the plumbing is tested."""

import hist
import numpy as np
import pytest
import torch

from mu2e_histcompare import BAD, GOOD, ks


def toy(mu, n=20000, seed=0):
    h = hist.Hist(hist.axis.Regular(50, 0, 100))
    h.fill(np.random.default_rng(seed).normal(mu, 10, n))
    return h


def test_ks_same_shape_is_good():
    r = ks.compare(toy(50, seed=1), toy(50, seed=2), "x/PEr")
    assert r.method == "ks" and r.verdict == GOOD and r.score > 0.05


def test_ks_shifted_is_bad():
    r = ks.compare(toy(60), toy(50, seed=2), "x/PEr")
    assert r.verdict == BAD and r.score < 0.01


def test_vision_uses_reviewer_verdict():
    from mu2e_histcompare import vision

    class Stub:
        def review(self, content):
            self.content = content
            return "Observations: shifted.\nVerdict: BAD", BAD

    stub = Stub()
    instr = {"title": "PE", "instruction": "Peak near 50."}
    r = vision.compare(toy(60), toy(50), "x/PEr", instr, stub, run="2", ref_run="1")
    assert r.verdict == BAD and "Verdict" in r.detail
    assert sum(c["type"] == "image" for c in stub.content) == 2


def test_hydra_scores_with_saved_model(tmp_path):
    from hydra_mu2e.model import PlotCNN
    from mu2e_histcompare import hydra

    torch.save(PlotCNN().state_dict(), tmp_path / "PEr.pt")
    r = hydra.compare(toy(50), "x/PEr", tmp_path)
    assert r.verdict in (GOOD, BAD) and 0.0 <= r.score <= 1.0


def test_hydra_without_model_gives_no_verdict(tmp_path):
    from mu2e_histcompare import hydra

    r = hydra.compare(toy(50), "x/logchi2", tmp_path)
    assert r.verdict is None and "no model" in r.detail


def test_ks_different_binning_gives_no_verdict():
    other = hist.Hist(hist.axis.Regular(25, 0, 100))
    other.fill(np.random.default_rng(3).normal(50, 10, 20000))
    r = ks.compare(toy(50), other, "x/PEr")
    assert r.verdict is None and r.evidence["status"] == "cantCompare"


def test_ks_evidence():
    r = ks.compare(toy(60), toy(50, seed=2), "x/PEr")
    assert r.evidence["status"] == "fail" and 0 < r.evidence["max_cdf_difference"] <= 1
    assert r.row().keys() == {"method", "histogram", "verdict", "score", "detail"}


def test_bundled_instructions():
    from mu2e_histcompare import instructions

    assert "crv_real_draft" in instructions.available()
    plots = instructions.load("crv_real_draft")
    assert "PEr" in plots and plots == instructions.load(str(instructions.path("crv_real_draft")))
