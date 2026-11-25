"""
mu2e-histcompare: three ways to compare a Mu2e DQM histogram with a golden reference run

  ks      Kolmogorov-Smirnov test, Mu2e/DQM's dqm.hist.compare (the standard method)
  vision  vision LLM with written plot instructions (mu2e-vision submodule)
  hydra   per-histogram CNN on the plot image (mu2e-hydra submodule)

Each module has compare(...) -> Result. The method modules are imported on demand, so
ks works without torch or an LLM client:

    from mu2e_histcompare import ks
"""

from .result import BAD, GOOD, Result  # noqa: F401
