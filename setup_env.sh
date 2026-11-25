# Environment for mu2e-histcompare on a Mu2e gpvm.
# mu2e-hydra's setup sources mu2e-vision's (cvmfs ana env + Mu2e/DQM, found via DQM_DIR,
# ../DQM or ../../DQM relative to mu2e-vision), then this adds the wrapper package.
#
#   git submodule update --init      # first time only
#   source mu2e-histcompare/setup_env.sh

_MH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export MU2E_VISION_DIR="${MU2E_VISION_DIR:-$_MH/mu2e-vision}"
if [ -f "$_MH/mu2e-hydra/setup_env.sh" ]; then
    source "$_MH/mu2e-hydra/setup_env.sh"
else
    echo "WARNING: submodules missing; run: git -C $_MH submodule update --init"
fi
export PYTHONPATH="$_MH${PYTHONPATH:+:$PYTHONPATH}"
unset _MH
