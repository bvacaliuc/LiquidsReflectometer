"""Warning hygiene — keep third-party noise out so first-party signal shows.

matplotlib 3.9.4's `_mathtext` / `_fontconfig_pattern` still call pyparsing's
deprecated camelCase API, and pyparsing 3.3.2 warns about it. That is
third-party and there is no matplotlib release that removes it, so the suite
filters the pyparsing category — narrowly, because a bare category ignore would
also hide our own deprecations.

These two tests are the guard: the first fails if the filter stops covering the
noise, the second fails if it is ever widened enough to hide us.

The tests after them guard the first-party sites that used to warn (slug
`test-suite-warnings`, W1-W4). Each runs its site under an "error" filter with an
input that used to warn, and checks the values too, so a fix that silenced a
warning by changing a number would still be red.
"""

import os
import sys
import types
import warnings

import numpy as np
import pytest
import scipy.special


def _reset_warning_registries():
    """Let already-emitted warnings fire again.

    Python records emitted warnings per module and suppresses repeats, so a
    warning triggered by an earlier test would not reappear here and the check
    would pass vacuously. Note this deliberately does NOT use
    `simplefilter("always")`: that replaces the filter list, which would discard
    the very ini configuration under test and make the assertion unfalsifiable.
    """
    import sys

    for module in list(sys.modules.values()):
        registry = getattr(module, "__warningregistry__", None)
        if registry:
            registry.clear()


def _render_mathtext():
    """Render the kind of label the Overplot tab draws (`R·Q⁴`)."""
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    figure = Figure()
    FigureCanvasAgg(figure)
    axes = figure.add_subplot(111)
    axes.set_ylabel(r"$R \cdot Q^4$")
    figure.canvas.draw()


def test_no_pyparsing_warning_from_mathtext():
    """The suite's filterwarnings must actually cover the mathtext noise."""
    pyparsing_warnings = pytest.importorskip("pyparsing.warnings")
    category = pyparsing_warnings.PyparsingDeprecationWarning

    _reset_warning_registries()
    with warnings.catch_warnings(record=True) as caught:
        _render_mathtext()

    leaked = [w for w in caught if issubclass(w.category, category)]
    assert not leaked, (
        f"{len(leaked)} PyparsingDeprecationWarning(s) escaped the ini filter, "
        f"first from {leaked[0].filename}:{leaked[0].lineno}"
    )


def test_first_party_deprecation_still_visible():
    """The filter must not be widened into a bare category ignore.

    If someone replaces the pyparsing-scoped entry with
    `ignore::DeprecationWarning`, our own deprecations vanish with the noise —
    this goes red instead.
    """
    _reset_warning_registries()
    with warnings.catch_warnings(record=True) as caught:
        warnings.warn("first-party probe", DeprecationWarning, stacklevel=1)

    assert any(
        issubclass(w.category, DeprecationWarning) and "first-party probe" in str(w.message) for w in caught
    ), "a first-party DeprecationWarning is being suppressed; the warning filter is too broad"


def _warn_on_lookup(name):
    warnings.warn(f"a module-level __getattr__ ran for {name!r}", DeprecationWarning, stacklevel=2)
    raise AttributeError(name)


def test_resetting_the_registries_runs_no_module_hook(monkeypatch):
    """W4: the reset reads each module's own namespace, so a module-level __getattr__ (PEP 562) never runs.

    mpmath 1.4's deprecated `rational` and `math2` modules warn from theirs. sympy imports mpmath, and the suite
    imports sympy at collection (`lr_reduction.user_defined_function`), so this file's own reset put their two
    DeprecationWarnings in the suite's summary. The reset still clears a registry it finds.
    """
    hooked = types.ModuleType("hygiene_probe_hooked")
    hooked.__getattr__ = _warn_on_lookup
    registered = types.ModuleType("hygiene_probe_registered")
    registered.__warningregistry__ = {("probe", UserWarning, 1): True}
    # Out of sys.modules again before pytest reports: its traceback code reads __file__ from every module.
    with monkeypatch.context() as patch:
        patch.setitem(sys.modules, hooked.__name__, hooked)
        patch.setitem(sys.modules, registered.__name__, registered)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            _reset_warning_registries()
    assert registered.__warningregistry__ == {}


def test_resetting_the_registries_with_mpmath_loaded_warns_nothing():
    """W4, the reported case: with mpmath imported, the reset raises no DeprecationWarning."""
    pytest.importorskip("mpmath")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _reset_warning_registries()


_PIXELS = np.arange(304)
_PEAK = np.round(1000 * np.exp(-((_PIXELS - 140.0) ** 2) / (2 * 3.0**2)))


def _peak_with_fractions_and_a_negative():
    y = _PEAK.copy()
    # Between 0 and 1 the mask decides the weight, not 1/sqrt(y).
    y[[10, 20]] = [0.5, 0.25]
    # No reduction produces a negative sum of counts, but the function takes any array.
    y[30] = -2.0
    return y


@pytest.mark.parametrize(
    "y", [np.zeros(304), _peak_with_fractions_and_a_negative(), _PEAK + 5.0], ids=["all-zero", "mixed", "no-zero"]
)
def test_the_peak_fit_weights_are_computed_without_dividing_by_zero(y):
    """W1, U2: fit_signal_flat_bck weights a pixel 1 where y < 1 and 1/sqrt(y) elsewhere, without computing 1/0
    first. The weights the fit receives equal, element by element, those of the base's two lines (2324e5c,
    peak_finding.py:107-108), evaluated here with their warnings silenced."""
    from lr_reduction import peak_finding

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _, _, fit = peak_finding.fit_signal_flat_bck(_PIXELS, y, x_min=0, x_max=len(y), center=140, sigma=3.0)
    with np.errstate(divide="ignore", invalid="ignore"):
        base = 1 / np.sqrt(y)
    base[y < 1] = 1
    assert np.array_equal(fit.weights, 1 / base)



def _base_background_fit_weights(counts, errors, charge):
    """The base's two lines (2324e5c, background.py:144-147), with their warning silenced."""
    with np.errstate(divide="ignore"):
        weights = 1 / errors
    weights[counts == 0] = charge
    return weights


@pytest.mark.parametrize(
    "counts, errors",
    [
        (np.zeros(5), np.zeros(5)),
        (np.array([0.0, 2e-6, 0.0, 5e-6, 1e-6]), np.array([0.0, 1.4e-6, 0.0, 2.2e-6, 1e-6])),
        (np.array([2e-6, 5e-6, 1e-6]), np.array([1.4e-6, 2.2e-6, 1e-6])),
    ],
    ids=["all-zero", "mixed", "no-zero"],
)
def test_the_background_fit_weights_are_computed_without_dividing_by_zero(counts, errors):
    """W1b, the second origin the census found (background.py:144, the functional background's fit of each bin
    across the background pixels): a pixel with no counts is weighted `charge` without computing 1/0 first, and
    the others 1/error, element by element as at the base."""
    from lr_reduction.background import background_fit_weights

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        weights = background_fit_weights(counts, errors, 12.5)
    assert np.array_equal(weights, _base_background_fit_weights(counts, errors, 12.5))


def test_a_zero_error_with_counts_still_warns_in_the_background_fit():
    """W1b's one case that keeps its warning: counts with a zero error reach the fit as an infinite weight, as
    at the base. That would be a defect upstream, so it stays loud."""
    from lr_reduction.background import background_fit_weights

    counts, errors = np.array([3e-6, 1e-6]), np.array([0.0, 1e-6])
    with pytest.warns(RuntimeWarning, match="divide by zero"):
        weights = background_fit_weights(counts, errors, 12.5)
    assert np.array_equal(weights, _base_background_fit_weights(counts, errors, 12.5))


def test_the_functional_background_warns_nothing_for_pixels_without_counts(nexus_dir, template_dir):
    """W1b through the reduction: run 198409 with the functional background (template_fbck.xml with two
    backgrounds, as tests/test_reduction.py::test_reduce_functional_bck) has background pixels without counts in
    some bins, where the base computed 1/0 (35 times for this run)."""
    import mantid.simpleapi as mtd_api

    from lr_reduction import template
    from lr_reduction.utils import amend_config

    with amend_config(data_dir=nexus_dir):
        ws = mtd_api.Load("REF_L_198409")
    sequence_number = ws.getRun().getProperty("sequence_number").value[0]
    template_data = template.read_template(os.path.join(template_dir, "template_fbck.xml"), sequence_number)
    template_data.two_backgrounds = True
    with amend_config(data_dir=nexus_dir), warnings.catch_warnings():
        warnings.filterwarnings("error", category=RuntimeWarning)
        _, refl, d_refl, _ = template.process_from_template_ws(ws, template_data)
    assert np.all(np.isfinite(refl)) and np.all(np.isfinite(d_refl))

def _base_paralyzable_correction(rate, dead_time, tof_step):
    """The base's arithmetic (2324e5c, dead_time_correction.py:96-101), with its warnings silenced."""
    with np.errstate(divide="ignore", invalid="ignore"):
        true_rate = -scipy.special.lambertw(-rate * dead_time / tof_step).real / dead_time
        corr = true_rate / (rate / tof_step)
    corr[rate == 0] = 1
    return corr


@pytest.mark.parametrize(
    "rate",
    [np.zeros(6), np.array([0.0, 0.25, 0.0, 1.0, 3.0, 0.0]), np.array([0.25, 1.0, 3.0, 0.5])],
    ids=["all-zero", "mixed", "no-zero"],
)
def test_the_paralyzable_correction_is_computed_without_dividing_zero_by_zero(rate):
    """W2, U3: where the rate is zero (no events) the correction is 1, without computing 0/0 first; elsewhere it
    is the base's value, element by element. DeadTime and TOFStep are the algorithm's defaults."""
    from lr_reduction.dead_time_correction import paralyzable_correction

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        corr = paralyzable_correction(rate, 4.2, 100.0)
    assert np.array_equal(corr, _base_paralyzable_correction(rate, 4.2, 100.0))


def test_the_paralyzable_dead_time_algorithm_warns_nothing_for_bins_without_events(nexus_dir):
    """W2 through the algorithm, on tests/test_dead_time.py's run: REF_L_198409 has TOF bins with no events,
    where the base computed 0/0. The correction is finite and at least 1 in every bin, and exactly 1 in some."""
    import mantid.simpleapi as mtd_api

    from lr_reduction.dead_time_correction import SingleReadoutDeadTimeCorrection
    from lr_reduction.utils import amend_config

    with amend_config(data_dir=nexus_dir):
        ws = mtd_api.Load("REF_L_198409")
    algo = SingleReadoutDeadTimeCorrection()
    algo.PyInit()
    algo.setProperty("InputWorkspace", ws)
    algo.setProperty("Paralyzable", True)
    algo.setProperty("OutputWorkspace", "hygiene_dead_time_corr")
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        algo.PyExec()
    corr = algo.getProperty("OutputWorkspace").value.readY(0)
    assert np.all(np.isfinite(corr)) and np.all(corr >= 1)
    assert np.any(corr == 1)


def test_reading_a_result_file_without_data_rows_warns_nothing(tmp_path):
    """W3: read_file no longer hands a file with no data row to np.loadtxt, which warned "input contained no
    data". It still returns four empties and the meta. The warnings are recorded rather than raised: the base's
    bare except swallowed a raised one, and the case passed."""
    from lr_reduction.output import read_file

    path = tmp_path / "empty.txt"
    path.write_text('# Meta:{"run": 1}\n# No data\n')
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = read_file(str(path))
    assert [str(w.message) for w in caught] == []
    assert result == ([], [], [], [], {"run": 1})
