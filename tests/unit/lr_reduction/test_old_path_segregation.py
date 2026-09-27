"""The campaign's work stays in the NEW workflow — pinned, not asserted in prose.

The scientists' concern (item 3 of the harden-review-branch order): the settings
model and launcher work must not leak into the old `template.py` /
`reduction_template_reader` reduction path. Reviewing a diff proves that for one
diff; this proves it for every future one.
"""

import subprocess
import sys

import pytest

from lr_reduction import reduction_template_reader

#: The old reduction path. Nothing the campaign built may reach these.
OLD_PATH_MODULES = [
    "lr_reduction.template",
    "lr_reduction.reduction_template_reader",
]

#: What the campaign built. None of it belongs on the old path.
NEW_WORKFLOW_PREFIXES = (
    "lr_reduction.settings_document",
    "lr_reduction.settings_resolver",
    "lr_reduction.field_spec",
    "lr_reduction.roi_estimate",
    "lr_reduction.reduction_domains",
    "launcher",
)


def _transitive_imports(module_name):
    """Every lr_reduction/launcher module reachable from `module_name`.

    Measured in a SUBPROCESS, deliberately. The first version popped modules out
    of this interpreter's `sys.modules` and re-imported, which poisoned the rest
    of the run: `field_spec` held by an already-imported test module and a
    freshly-imported `reduction_domains` became different objects, and
    `test_the_choice_lists_are_the_reducers_own` failed downstream. Measured —
    169 passed without this file, 1 failed with it. Module-table surgery is
    process-global state, and an unrestored global invalidates every measurement
    after it (`scaling-factor-path-anchor-learning.md` #4).

    A clean interpreter also gives the honest answer: what this module pulls in
    on its own, not what happens to be resident already.

    Walked via `sys.modules` after the import rather than by parsing source, so
    a lazy import inside a function body is caught too — which is how a leak
    would actually arrive. The child prints a marker first so a child that
    failed to START is never mistaken for a child that found nothing.
    """
    program = "; ".join(
        [
            "import importlib, sys",
            f"importlib.import_module({module_name!r})",
            'names = [n for n in sys.modules if n.startswith(("lr_reduction", "launcher"))]',
            'print("MODULES:" + ",".join(sorted(names)))',
        ]
    )
    proc = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, timeout=180
    )
    assert proc.returncode == 0, f"importing {module_name} failed:\n{proc.stderr}"
    marker = [ln for ln in proc.stdout.splitlines() if ln.startswith("MODULES:")]
    assert marker, f"child produced no module list for {module_name}:\n{proc.stdout}"
    return set(marker[-1][len("MODULES:"):].split(","))


@pytest.mark.parametrize("module_name", OLD_PATH_MODULES)
def test_the_old_reduction_path_does_not_reach_the_new_workflow(module_name):
    """The boundary the scientists asked us to keep.

    A settings/launcher import appearing here means the campaign's work has
    entered the path they did not want touched — and it would arrive silently,
    because the old path's own tests would keep passing.
    """
    reached = _transitive_imports(module_name)
    leaked = sorted(
        name
        for name in reached
        if name.startswith(NEW_WORKFLOW_PREFIXES)
    )
    assert leaked == [], (
        f"{module_name} now reaches the new-workflow modules {leaked} — the "
        f"campaign's work has leaked into the old reduction path"
    )


def test_the_old_path_template_round_trips_unchanged():
    """Behavioural pin: the old reader's XML round trip is byte-stable.

    A golden value would need updating whenever the old path legitimately
    changes; a round trip pins the property that matters here — that nothing
    this branch did altered how the old path reads or writes a template.
    """
    original = reduction_template_reader.ReductionParameters()
    original.data_peak_range = [140, 150]
    original.norm_peak_range = [141, 151]
    original.subtract_background = True
    original.scaling_factor_file = "/tmp/sf.cfg"

    xml = reduction_template_reader.to_xml([original])
    restored = reduction_template_reader.from_xml(xml)

    assert len(restored) == 1
    assert restored[0].data_peak_range == [140, 150]
    assert restored[0].norm_peak_range == [141, 151]
    assert restored[0].subtract_background is True
    assert restored[0].scaling_factor_file == "/tmp/sf.cfg"

    # Idempotent from the second trip on. NOT byte-stable on the first: the old
    # serialiser normalises some ints to floats (`<dead_time_tof_step>100` ->
    # `100.0`, `<xi_reference>445` -> `445.0`), so trip 1 != trip 2 while
    # trip 2 == trip 3. Measured, pre-existing, and NOT this branch's doing —
    # item 3's scope is zero old-path files, so it is recorded in the PR body
    # rather than fixed here. Pinning idempotence rather than byte-equality
    # keeps the guard honest instead of encoding the drift as expected.
    second = reduction_template_reader.to_xml(restored)
    third = reduction_template_reader.to_xml(reduction_template_reader.from_xml(second))
    assert second == third, "the old serialiser is not idempotent"
