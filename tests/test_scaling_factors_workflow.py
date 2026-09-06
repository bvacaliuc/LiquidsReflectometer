import os

import mantid.simpleapi as mtd_api
import numpy as np
import pytest

mtd_api.config["default.facility"] = "SNS"
mtd_api.config["default.instrument"] = "REF_L"

from lr_reduction.scaling_factors import workflow as sf_workflow
from lr_reduction.utils import amend_config

# Relative tolerances, per field, measured rather than inherited.
#
# The old helper carried a single 0.02 bar that only ever ran against `error_b`.
# These come from the actual agreement of this suite against its references —
# 45 row-comparisons (9 rows x 5 tests), worst case per field:
#
#   LambdaRequested, S1H, S2iH   0.0       (45/45 bit-exact)
#   S1W, S2iW                    0.0       (45/45 bit-exact once the stale row
#                                            in sf_197912_Si_auto.cfg is repaired)
#   a        5.6e-05      error_a  3.0e-05
#   b        6.7e-04      error_b  2.3e-05
#
# Instrument metadata is copied verbatim from the run logs, so it must
# round-trip; 1e-12 rather than exact equality only so a one-ulp difference
# from another Mantid build is not a failure. A physically meaningful change
# is caught nine orders of magnitude before that bar — the 0.04 mm stale-slit
# discrepancy this slug found is 2e-03.
#
# The fitted parameters get roughly an order of magnitude of headroom over the
# worst observed delta. `b` is looser because it is a near-zero slope
# (~1e-06 against a ~1-9), where relative error is inherently noisier.
#
# If CI on another platform exceeds one of these, widen it from a MEASUREMENT
# and say so — never to turn a red suite green.
_METADATA_TOL = 1e-12
_TOL = {
    "LambdaRequested": _METADATA_TOL,
    "S1H": _METADATA_TOL,
    "S2iH": _METADATA_TOL,
    "S1W": _METADATA_TOL,
    "S2iW": _METADATA_TOL,
    "a": 1e-3,
    "error_a": 1e-3,
    "error_b": 1e-3,
    "b": 5e-3,
}
# A field nobody anticipated is held to the fitted-parameter bar rather than
# skipped, so adding one to the writer cannot quietly go unchecked.
_DEFAULT_TOL = 1e-3


def _parse_cfg(path):
    """
    Parse a scaling-factor cfg into one dict of {field: value-string} per row,
    skipping comments and blank lines.
    """
    rows = []
    with open(path, "r") as fd:
        for line in fd:
            if line.startswith("#") or not line.strip():
                continue
            rows.append(dict(tok.split("=", 1) for tok in line.split() if "=" in tok))
    return rows


def check_results(data_file, reference):
    """
    Check every field of a scaling factor file against its reference.

    Numeric fields are compared by relative delta against the per-field bar in
    `_TOL`; non-numeric fields (IncidentMedium) are compared exactly. The row
    count and the field set of each row are checked too, so a truncated file or
    a vanished field fails instead of silently comparing a prefix.
    """
    cfg_data = _parse_cfg(data_file)
    cfg_ref = _parse_cfg(reference)

    assert len(cfg_data) == len(cfg_ref), (
        f"{data_file} has {len(cfg_data)} data rows, reference {reference} has {len(cfg_ref)}"
    )

    for i, (row, ref) in enumerate(zip(cfg_data, cfg_ref)):
        assert set(row) == set(ref), (
            f"row {i}: field set differs from the reference; "
            f"missing={sorted(set(ref) - set(row))} unexpected={sorted(set(row) - set(ref))}"
        )
        for key, ref_str in ref.items():
            value_str = row[key]
            try:
                v_ref = float(ref_str)
            except ValueError:
                assert value_str == ref_str, f"row {i} {key}: {value_str!r} != reference {ref_str!r}"
                continue
            try:
                v_calc = float(value_str)
            except ValueError:
                raise AssertionError(
                    f"row {i} {key}: {value_str!r} is not numeric but the reference {ref_str!r} is"
                )
            tol = _TOL.get(key, _DEFAULT_TOL)
            delta = np.fabs(v_calc - v_ref) if v_ref == 0.0 else np.fabs((v_ref - v_calc) / v_ref)
            assert delta < tol, (
                f"row {i} {key}: {v_calc!r} vs reference {v_ref!r} "
                f"(delta {delta:.3e}, tolerance {tol:.0e})"
            )


# --------------------------------------------------------------------------
# Helper-level guards for check_results itself.
#
# These exist because the helper silently stopped comparing anything: a bare
# rebind in its token loop kept only the LAST token of each row, and the
# comparison index was unused, so every assertion was error_b against itself.
# Nine of the ten fields — including `a`, which multiplies every R(Q) produced
# from this path — were never checked. A test helper that cannot fail is worse
# than no test, because the suite reports assurance it does not have; so the
# helper now has tests of its own.
# --------------------------------------------------------------------------

_REF_ROWS = [
    "IncidentMedium=Si LambdaRequested=9.74 S1H=0.391 S2iH=0.25 S1W=20.005 S2iW=20.0 "
    "a=1.1051209892255538 b=-5.536686634970115e-07 error_a=0.046673303933524965 error_b=1.3017622676214164e-06",
    "IncidentMedium=Si LambdaRequested=7.043 S1H=0.39 S2iH=0.25 S1W=19.952 S2iW=19.95 "
    "a=6.624303827034047 b=1.9231042128909928e-05 error_a=0.23125978138549352 error_b=9.279372359246127e-06",
]


def _write_cfg(path, rows):
    with open(path, "w") as fd:
        fd.write("# y=a+bx\n#\n")
        fd.writelines(row + "\n" for row in rows)
    return str(path)


def _mutated(row, key, value):
    """Return `row` with `key` set to `value`, preserving field order."""
    toks = []
    for tok in row.split():
        k, _, v = tok.partition("=")
        toks.append(f"{k}={value}" if k == key else f"{k}={v}")
    return " ".join(toks)


def test_check_results_accepts_an_identical_file(tmp_path):
    """Positive control: the guards below must fail for the right reason."""
    ref = _write_cfg(tmp_path / "ref.cfg", _REF_ROWS)
    data = _write_cfg(tmp_path / "data.cfg", _REF_ROWS)
    check_results(data, ref)


@pytest.mark.parametrize(
    "key, value",
    [
        # Gross corruption. Every one of these went UNDETECTED before this fix.
        pytest.param("a", "999999.0", id="a-the-scaling-factor-itself"),
        pytest.param("b", "999999.0", id="b-the-slope"),
        pytest.param("error_a", "999999.0", id="error_a-uncertainty-on-a"),
        pytest.param("LambdaRequested", "999.0", id="LambdaRequested-the-row-s-wavelength"),
        pytest.param("S1W", "999.0", id="S1W-slit-width"),
        # float() would raise on this one rather than compare it.
        pytest.param("IncidentMedium", "Air", id="IncidentMedium-non-numeric"),
        # Subtle, and the reason the tolerances were measured rather than
        # inherited: a 1% error in `a` passes the old 0.02 bar even if `a` had
        # been compared at all.
        pytest.param("a", "6.690546865304387", id="a-1pc-high-under-the-old-0.02-bar"),
        # 0.04 mm on a 20 mm slit: the exact discrepancy that exposed the stale
        # row in sf_197912_Si_auto.cfg. Metadata is copied from the run logs, so
        # this must fail, not be absorbed by a fitted-parameter tolerance.
        pytest.param("S1W", "19.992", id="S1W-0.04mm-the-stale-reference-delta"),
    ],
)
def test_check_results_detects_mutation(tmp_path, key, value):
    ref = _write_cfg(tmp_path / "ref.cfg", _REF_ROWS)
    mutated = [_REF_ROWS[0], _mutated(_REF_ROWS[1], key, value)]
    data = _write_cfg(tmp_path / "data.cfg", mutated)
    with pytest.raises(AssertionError):
        check_results(data, ref)


def test_check_results_detects_a_missing_field(tmp_path):
    """A field that vanishes from the output is a regression, not a pass."""
    ref = _write_cfg(tmp_path / "ref.cfg", _REF_ROWS)
    dropped = " ".join(t for t in _REF_ROWS[1].split() if not t.startswith("error_a="))
    data = _write_cfg(tmp_path / "data.cfg", [_REF_ROWS[0], dropped])
    with pytest.raises(AssertionError):
        check_results(data, ref)


def test_check_results_detects_a_truncated_file(tmp_path):
    """Fewer rows than the reference must fail, not silently compare a prefix."""
    ref = _write_cfg(tmp_path / "ref.cfg", _REF_ROWS)
    data = _write_cfg(tmp_path / "data.cfg", _REF_ROWS[:1])
    with pytest.raises(AssertionError):
        check_results(data, ref)


def test_compute_sf(nexus_dir, template_dir, tmp_path):
    """
    Test the computation of scaling factors
    """
    with amend_config(data_dir=nexus_dir):
        ws = mtd_api.Load("REF_L_197912")

    output_dir = str(tmp_path)

    # We are passing the first run of the set. For the autoreduction,
    # we would be missing runs from the complete set so we will want to
    # wait for the whole set to be acquired.
    output = sf_workflow.process_scaling_factors(ws, output_dir, use_deadtime=False, wait=True, postfix="_test")
    assert output is False

    output_cfg = os.path.join(output_dir, "sf_197912_Si_test.cfg")
    if os.path.isfile(output_cfg):
        os.remove(output_cfg)

    output = sf_workflow.process_scaling_factors(ws, output_dir, use_deadtime=False, wait=False, postfix="_test")
    assert output is True

    check_results(output_cfg, os.path.join(template_dir, "sf_197912_Si_auto.cfg"))


def test_compute_sf_with_deadtime(nexus_dir, template_dir, tmp_path):
    """
    Test the computation of scaling factors
    """
    with amend_config(data_dir=nexus_dir):
        ws = mtd_api.Load("REF_L_197912")

    output_dir = str(tmp_path)

    output_cfg = os.path.join(output_dir, "sf_197912_Si_test_dt.cfg")
    if os.path.isfile(output_cfg):
        os.remove(output_cfg)

    output = sf_workflow.process_scaling_factors(ws, output_dir, use_deadtime=True, wait=False, postfix="_test_dt")
    assert output is True

    check_results(output_cfg, os.path.join(template_dir, "sf_197912_Si_dt_par_42_200.cfg"))


def test_compute_sf_with_deadtime_tof_300(nexus_dir, template_dir, tmp_path):
    """
    Test the computation of scaling factors
    """
    with amend_config(data_dir=nexus_dir):
        ws = mtd_api.Load("REF_L_197912")

    output_dir = str(tmp_path)

    output_cfg = os.path.join(output_dir, "sf_197912_Si_test_dt.cfg")
    if os.path.isfile(output_cfg):
        os.remove(output_cfg)

    output = sf_workflow.process_scaling_factors(
        ws,
        output_dir,
        use_deadtime=True,
        deadtime=4.6,
        deadtime_tof_step=300,
        paralyzable=False,
        wait=False,
        postfix="_test_dt",
    )
    assert output is True

    check_results(output_cfg, os.path.join(template_dir, "sf_197912_Si_dt_par_46_300.cfg"))


def test_compute_sf_with_deadtime_tof_200(nexus_dir, template_dir, tmp_path):
    """
    Test the computation of scaling factors
    """
    with amend_config(data_dir=nexus_dir):
        ws = mtd_api.Load("REF_L_197912")

    output_dir = str(tmp_path)

    output_cfg = os.path.join(output_dir, "sf_197912_Si_test_dt.cfg")
    if os.path.isfile(output_cfg):
        os.remove(output_cfg)

    output = sf_workflow.process_scaling_factors(
        ws,
        output_dir,
        use_deadtime=True,
        deadtime=4.6,
        deadtime_tof_step=200,
        paralyzable=False,
        wait=False,
        postfix="_test_dt",
    )
    assert output is True

    check_results(output_cfg, os.path.join(template_dir, "sf_197912_Si_dt_par_46_200.cfg"))


def test_compute_sf_with_deadtime_tof_200_sort(nexus_dir, template_dir, tmp_path):
    """
    Test the computation of scaling factors
    """
    with amend_config(data_dir=nexus_dir):
        ws = mtd_api.Load("REF_L_197912")

    output_dir = str(tmp_path)

    output_cfg = os.path.join(output_dir, "sf_197912_Si_test_dt.cfg")
    if os.path.isfile(output_cfg):
        os.remove(output_cfg)

    output = sf_workflow.process_scaling_factors(
        ws,
        output_dir,
        order_by_runs=False,
        use_deadtime=True,
        deadtime=4.6,
        deadtime_tof_step=200,
        paralyzable=False,
        wait=False,
        postfix="_test_dt",
    )
    assert output is True

    check_results(output_cfg, os.path.join(template_dir, "sf_197912_Si_dt_par_46_200.cfg"))
