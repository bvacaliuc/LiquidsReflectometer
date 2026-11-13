"""
Every example runs, start to end, on the example data.

The examples are the published description of how the reduction is called. A change that breaks one of them breaks
what the instrument's users do, so each example function is a test: it is called as written and must return and
write its results. An example whose input files are not on this machine is skipped, and the skip names the file.
"""

import importlib
import inspect
import os
from pathlib import Path

import pytest

import example_paths
from example_inputs import INPUTS

CASES = [(module, function) for module, functions in INPUTS.items() for function in functions]

# Examples that do not run today, each with what stops it. The test still calls them: one that starts to run fails
# the test (strict), so that its entry is removed and the example is held to running from then on.
TEMPLATE_EXAMPLES_FAIL = (
    "ValueError 'Maximum I has calculated negative' (nr_tools, the beam profile on the detector) for run 211029 with "
    "the direct beams found for it; the folder the example named for them no longer exists. For its author to settle."
)
KNOWN_FAILURES = {
    ("example_nr_from_template", "example_template_reduction"): TEMPLATE_EXAMPLES_FAIL,
    ("example_nr_from_template", "example_template_reduction_3ang"): TEMPLATE_EXAMPLES_FAIL,
    ("example_nr_from_template", "example_template_reduction_new"): TEMPLATE_EXAMPLES_FAIL,
}


def data_folder():
    return Path(os.environ.get(example_paths.DATA_VARIABLE) or example_paths.REPOSITORY_DATA)


@pytest.mark.parametrize("module", sorted(INPUTS))
def test_every_example_of_a_file_has_its_inputs_listed(module):
    """A new example gets a test only by being listed: an example that is not listed fails here."""
    written = {
        name
        for name, value in vars(importlib.import_module(module)).items()
        if name.startswith("example_") and inspect.isfunction(value) and value.__module__ == module
    }
    assert written == set(INPUTS[module])


def test_a_known_failure_names_an_example_that_exists():
    assert set(KNOWN_FAILURES) <= set(CASES)


def test_every_example_file_is_listed():
    files = {path.stem for path in Path(example_paths.__file__).parent.glob("example_*.py")} - {"example_paths"}
    assert files == set(INPUTS)


@pytest.mark.datarepo
@pytest.mark.parametrize(("module", "function"), CASES, ids=[f"{module}.{function}" for module, function in CASES])
def test_example_runs(module, function, example_output, request):
    missing = [path for path in INPUTS[module][function] if not (data_folder() / path).is_file()]
    if missing:
        pytest.skip(f"example data not here: {data_folder() / missing[0]} ({len(missing)} of {len(INPUTS[module][function])} files)")
    if (module, function) in KNOWN_FAILURES:
        request.applymarker(pytest.mark.xfail(strict=True, raises=ValueError, reason=KNOWN_FAILURES[module, function]))

    result = getattr(importlib.import_module(module), function)()

    assert result is not None
    written = [path for path in example_output.rglob("*") if path.is_file()]
    assert written, "the example wrote nothing to the output folder"
