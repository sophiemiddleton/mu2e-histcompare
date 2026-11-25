# mu2e-histcompare

Three ways to compare a Mu2e DQM histogram with a golden reference run, behind one interface:

| method   | what it is                                                        | needs                                   | lives in |
|----------|-------------------------------------------------------------------|-----------------------------------------|----------|
| `ks`     | Kolmogorov–Smirnov test, Mu2e/DQM `dqm.hist.compare` (standard)    | Mu2e/DQM                                | this repo (`mu2e_histcompare/ks.py`) |
| `vision` | vision LLM sees reference + input plot + written plot instructions | a model (Anthropic API or LiteLLM)      | submodule `mu2e-vision` (package `histcompare`) |
| `hydra`  | Hydra-style CNN, one per histogram, input plot only                | trained models (`<histogram>.pt`)       | submodule `mu2e-hydra` (package `hydra_mu2e`) |

Each method returns the same `Result(method, histogram, verdict, score, detail)`. The verdict is GOOD/BAD (None if the method can't judge that plot). The score is the KS probability for `ks`, P(BAD) for `hydra`, and None for `vision`. `detail` holds the KS status, the model's full answer, or the model file.

## Setup

```bash
git clone --recursive <this repo>        # or: git submodule update --init
source mu2e-histcompare/setup_env.sh     # cvmfs ana env + Mu2e/DQM (DQM_DIR, ../DQM or ../../DQM)
```

## Command line

```bash
python -m mu2e_histcompare \
    --input  dqm.mu2e.cosmics_crv.run125846.root \
    --reference dqm.mu2e.cosmics_crv.run125026.root \
    --method ks vision hydra \
    --instructions mu2e-vision/instructions/crv_real_draft.yaml \
    --base-url https://litellm.fnal.gov/v1 --model azure/claude-opus-5-5 \
    --hydra-models path/to/mu2e-hydra/results/real-006-001-C/models \
    --out results.csv
```

- Histograms: `--hist crvRecoDQM/PEr ...`, or by default every plot in `--instructions`.
- `ks` only: `--method ks --hist ...` (no model, no torch needed).
- `vision`: needs `--instructions` and `--model`; for LiteLLM, set `LITELLM_API_KEY`.
- `hydra`: needs `--hydra-models`; train them with `python -m hydra_mu2e.realdata run ...` in mu2e-hydra. Plots without a model get no verdict.

## Python

```python
from dqm.hist.read import open_file
from mu2e_histcompare import ks, vision, hydra

with open_file(run) as f, open_file(ref) as fr:
    h, r = f.read("crvRecoDQM/PEr"), fr.read("crvRecoDQM/PEr")
    ks.compare(h, r, "crvRecoDQM/PEr")
    hydra.compare(h, "crvRecoDQM/PEr", models_dir)
    vision.compare(h, r, "crvRecoDQM/PEr", instruction, vision.make_reviewer("azure/claude-opus-5-5", "https://litellm.fnal.gov/v1"))
```

## Tests

```bash
python -m pytest tests      # toy histograms; vision uses a stub reviewer, hydra an untrained CNN
```
