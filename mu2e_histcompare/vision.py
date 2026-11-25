"""
Method 2: vision LLM (mu2e-vision submodule, Python package `histcompare`)

The model gets the reference plot, the input plot, the plot's written instructions
(instructions/*.yaml in mu2e-vision) and the run type, and answers with a GOOD/BAD verdict.
This needs a model: either the Anthropic API directly (--model), or an OpenAI-compatible
server such as Fermilab's LiteLLM gateway (--base-url https://litellm.fnal.gov/v1 --model ...,
key in LITELLM_API_KEY).
"""

from typing import Optional

from histcompare import context
from histcompare.vision import OpenAIReviewer, Reviewer

from .result import Result, short_name


def make_reviewer(model: str, base_url: Optional[str] = None, effort: str = "high"):
    if base_url:
        return OpenAIReviewer(base_url, model)
    return Reviewer(model, effort)


def compare(hist, ref, path: str, instruction: dict, reviewer, run: str = "input",
            ref_run: str = "reference", run_type: str = "cosmics") -> Result:
    """hist, ref: hist.Hist; instruction: this plot's entry from the instructions YAML."""
    name = short_name(path)
    title = instruction.get("title", name)
    xlabel = instruction.get("xlabel") or context.xlabel_for(name)
    image = context.render(hist, f"{title}, run {run}", xlabel, f"run {run}")
    ref_image = context.render(ref, f"{title}, run {ref_run}", xlabel, f"run {ref_run}")
    content = context.user_content(name, run, run_type, ref_run, instruction, image, ref_image)
    text, verdict = reviewer.review(content)
    return Result("vision", path, verdict, None, text)
