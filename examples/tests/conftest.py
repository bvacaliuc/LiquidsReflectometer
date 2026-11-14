"""The examples run as their authors run them, except that no window opens and every result goes to a scratch folder."""

import os
import sys
from pathlib import Path

os.environ["MPLBACKEND"] = "Agg"  # before matplotlib is imported: plot=True must not open a window

import pytest

EXAMPLES = Path(__file__).resolve().parent.parent
for folder in (EXAMPLES, Path(__file__).resolve().parent):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))


def pytest_report_header():
    import example_paths

    chosen = os.environ.get(example_paths.DATA_VARIABLE)
    folder = Path(chosen) if chosen else example_paths.REPOSITORY_DATA
    return f"example data: {folder} ({'found' if folder.is_dir() else 'not there'}; {example_paths.DATA_VARIABLE} chooses it)"


@pytest.fixture
def example_output(tmp_path, monkeypatch):
    """The output folder of one example run; the working folder is a scratch one too, so nothing lands in the tree."""
    import example_paths

    folder = tmp_path / "output"
    monkeypatch.setenv(example_paths.OUTPUT_VARIABLE, str(folder))
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    yield folder
    from matplotlib import pyplot

    pyplot.close("all")
