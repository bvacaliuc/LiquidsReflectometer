"""The examples run as their authors run them, except that a plot goes to a file and every result to a scratch folder."""

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
    """
    The output folder of one example run; the working folder is a scratch one too, so nothing lands in the tree.

    The examples ask for plots, and the reduction shows each one and waits for its window to be closed. Here nobody
    is there to close it: showing is replaced by writing every open figure to a file and closing it. The plotting
    code runs as it does on a screen, and the figures of the example are kept as files beside its output.
    """
    from matplotlib import pyplot

    import example_paths

    folder = tmp_path / "output"
    monkeypatch.setenv(example_paths.OUTPUT_VARIABLE, str(folder))
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    figures = tmp_path / "figures"
    figures.mkdir()

    def save_and_close(*_args, **_kwargs):
        for number in pyplot.get_fignums():
            pyplot.figure(number).savefig(figures / f"figure_{len(list(figures.iterdir())) + 1:03d}.png", dpi=50)
        pyplot.close("all")

    monkeypatch.setattr(pyplot, "show", save_and_close)
    yield folder
    pyplot.close("all")
