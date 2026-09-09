#!/usr/bin/env python
"""Measure how far the scaling-factor fit moves when only the minimizer changes.

Why this exists
---------------
`tests/test_scaling_factors_workflow.py` sizes the tolerance for `b` against a
"path-dependence floor" — how much a *converged* fit parameter shifts when the
input data is identical and only the minimizer's route to the answer differs.
That number is the whole justification for `b`'s bar, so it has to be
reproducible from this repository rather than quoted. This script is the
measurement.

`LRScalingFactors` fits `y = a + b*x` with Mantid's `Fit` algorithm, which
defaults to `Levenberg-MarquardtMD`. Swapping the minimizer changes the path to
the optimum without changing the optimum, so any residual difference in the
reported `a`/`b` is exactly the floor a cross-build tolerance has to clear.

Run
---
    pixi run python plan/scripts/measure_fit_path_dependence.py

Needs the test data repo at tests/data/liquidsreflectometer-data (the same
fixture the suite uses); takes a few minutes because it runs the scaling-factor
workflow once per minimizer.
"""

import argparse
import os
import tempfile

import mantid.simpleapi as mtd_api

mtd_api.config["default.facility"] = "SNS"
mtd_api.config["default.instrument"] = "REF_L"

from lr_reduction.scaling_factors import LRScalingFactors  # noqa: E402
from lr_reduction.scaling_factors import workflow as sf_workflow  # noqa: E402
from lr_reduction.utils import amend_config  # noqa: E402

# Mantid's default for Fit is Levenberg-MarquardtMD.
#
# The FLOOR is measured within the Levenberg-Marquardt family only: LM-MD and
# LM reach the SAME optimum by different internal routes, so what is left is
# path dependence and nothing else.
#
# Simplex is included as a CONTROL and deliberately excluded from the floor. It
# is a different algorithm class with looser convergence, not a different route
# to the same answer: it moves `b` by ~59%, which is a statement about Simplex's
# stopping criterion rather than about numerical path dependence. Averaging it
# into the floor would "justify" a tolerance six orders too loose — the exact
# mistake (a real measurement answering the wrong question) that produced this
# slug's v1.
LM_FAMILY = ("Levenberg-MarquardtMD", "Levenberg-Marquardt")
CONTROL = ("Simplex",)
MINIMIZERS = LM_FAMILY + CONTROL

FIELDS = ("a", "b", "error_a", "error_b")


def _rows(path):
    rows = []
    with open(path) as fd:
        for line in fd:
            if line.startswith("#") or not line.strip():
                continue
            rows.append(dict(tok.split("=", 1) for tok in line.split() if "=" in tok))
    return rows


def _run(workspace, minimizer, out_dir):
    """Run the workflow with `Fit` forced onto one minimizer."""
    original = LRScalingFactors.Fit

    def patched(*args, **kwargs):
        kwargs["Minimizer"] = minimizer
        return original(*args, **kwargs)

    LRScalingFactors.Fit = patched
    try:
        sf_workflow.process_scaling_factors(
            workspace, out_dir, use_deadtime=True, deadtime=4.6,
            deadtime_tof_step=200, paralyzable=False, wait=False, postfix="_probe",
        )
    finally:
        LRScalingFactors.Fit = original
    return _rows(os.path.join(out_dir, "sf_197912_Si_probe.cfg"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nexus-dir", default="tests/data/liquidsreflectometer-data/nexus")
    args = parser.parse_args()

    with amend_config(data_dir=os.path.abspath(args.nexus_dir)):
        workspace = mtd_api.Load("REF_L_197912")

    results = {}
    for minimizer in MINIMIZERS:
        with tempfile.TemporaryDirectory() as out_dir:
            results[minimizer] = _run(workspace, minimizer, out_dir)
        print(f"ran {minimizer}: {len(results[minimizer])} rows")

    baseline = MINIMIZERS[0]
    print(f"\nworst relative shift vs {baseline}, over {len(results[baseline])} rows")
    print(f"{'minimizer':<26}" + "".join(f"{f:>13}" for f in FIELDS))
    overall = dict.fromkeys(FIELDS, 0.0)
    for minimizer in MINIMIZERS[1:]:
        worst = dict.fromkeys(FIELDS, 0.0)
        for base_row, other_row in zip(results[baseline], results[minimizer]):
            for field in FIELDS:
                ref = float(base_row[field])
                if ref == 0.0:
                    continue
                delta = abs((float(other_row[field]) - ref) / ref)
                worst[field] = max(worst[field], delta)
                overall[field] = max(overall[field], delta)
        print(f"{minimizer:<26}" + "".join(f"{worst[f]:>13.3e}" for f in FIELDS))

    floor = dict.fromkeys(FIELDS, 0.0)
    for minimizer in LM_FAMILY[1:]:
        for base_row, other_row in zip(results[LM_FAMILY[0]], results[minimizer]):
            for field in FIELDS:
                ref = float(base_row[field])
                if ref == 0.0:
                    continue
                floor[field] = max(floor[field], abs((float(other_row[field]) - ref) / ref))

    print("\nPATH-DEPENDENCE FLOOR (Levenberg-Marquardt family only):")
    for field in FIELDS:
        print(f"  {field:<10} {floor[field]:.3e}")
    print(
        "\nA tolerance below a field's floor would make that comparison sensitive to\n"
        "the minimizer's route rather than to the data. Simplex is reported above as\n"
        "a control and is NOT part of the floor: it is a different algorithm with a\n"
        "looser stopping criterion, not a different path to the same optimum."
    )


if __name__ == "__main__":
    main()
