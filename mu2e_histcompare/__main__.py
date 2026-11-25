"""
Compare a run's DQM histograms with a reference run, by any of the three methods

    python -m mu2e_histcompare --input RUN.root --reference REF.root \
        --method ks vision hydra \
        --instructions mu2e-vision/instructions/crv_real_draft.yaml \
        --base-url https://litellm.fnal.gov/v1 --model azure/claude-opus-5-5 \
        --hydra-models ../HistCompare/mu2e-hydra/results/real-006-001-C/models \
        --out results.csv

The histograms come from --hist (paths in the file) or, if --hist is omitted, from the
instructions file (folder/name of every plot in it). Only the vision method needs
the instructions; only hydra needs --hydra-models.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

from dqm.hist.read import open_file

from .result import Result, short_name

METHODS = ("ks", "vision", "hydra")


def run_number(path: str, default: str) -> str:
    m = re.search(r"run(\d+)", Path(path).name)
    return m.group(1) if m else default


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="DQM ROOT file of the run to check")
    ap.add_argument("--reference", required=True, help="DQM ROOT file of the golden run")
    ap.add_argument("--method", nargs="+", choices=METHODS, default=["ks"])
    ap.add_argument("--hist", nargs="*", help="histogram paths, e.g. crvRecoDQM/PEr")
    ap.add_argument("--instructions", help="plot instructions YAML (required for vision)")
    ap.add_argument("--run-type", default="cosmics")
    ap.add_argument("--out", help="write the results as CSV here (default: print a table only)")
    g = ap.add_argument_group("ks")
    g.add_argument("--ks-tight", type=float, default=0.05)
    g.add_argument("--ks-loose", type=float, default=0.01)
    g = ap.add_argument_group("vision")
    g.add_argument("--model", help="e.g. claude-opus-5-5, or azure/claude-opus-5-5 with --base-url")
    g.add_argument("--base-url", help="OpenAI-compatible server, e.g. https://litellm.fnal.gov/v1")
    g.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    g = ap.add_argument_group("hydra")
    g.add_argument("--hydra-models", help="directory of <histogram>.pt models from mu2e-hydra")
    g.add_argument("--hydra-threshold", type=float, default=0.5)
    args = ap.parse_args(argv)

    instructions = {}
    if args.instructions:
        from histcompare.context import load_instructions
        instructions = load_instructions(args.instructions)
    if "vision" in args.method and not (args.instructions and args.model):
        ap.error("--method vision needs --instructions and --model")
    if "hydra" in args.method and not args.hydra_models:
        ap.error("--method hydra needs --hydra-models")
    paths = args.hist or [f"{i.get('folder', '')}/{n}".lstrip("/") for n, i in instructions.items()]
    if not paths:
        ap.error("give --hist or --instructions")

    run, ref_run = run_number(args.input, "input"), run_number(args.reference, "reference")
    if "ks" in args.method:
        from . import ks
    if "vision" in args.method:
        from . import vision
        reviewer = vision.make_reviewer(args.model, args.base_url, args.effort)
    if "hydra" in args.method:
        from . import hydra

    results = []
    with open_file(args.input) as f, open_file(args.reference) as fr:
        for path in paths:
            h, ref = f.read(path), fr.read(path)
            for method in args.method:
                if method == "ks":
                    r = ks.compare(h, ref, path, args.ks_tight, args.ks_loose)
                elif method == "vision":
                    instr = instructions.get(short_name(path))
                    r = (vision.compare(h, ref, path, instr, reviewer, run, ref_run, args.run_type)
                         if instr else Result("vision", path, None, None, "no instruction for this plot"))
                else:
                    r = hydra.compare(h, path, args.hydra_models, args.hydra_threshold)
                results.append(r)
                score = "" if r.score is None else f"{r.score:.4g}"
                print(f"{path:40s} {method:7s} {r.verdict or '-':5s} {score}", flush=True)

    if args.out:
        with open(args.out, "w", newline="") as fo:
            w = csv.DictWriter(fo, fieldnames=["run", "reference", *results[0].row()])
            w.writeheader()
            for r in results:
                w.writerow({"run": run, "reference": ref_run, **r.row()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
