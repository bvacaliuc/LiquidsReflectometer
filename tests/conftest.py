# standard imports
from pathlib import Path

# third-party imports
import pytest

_DATAREPO_PATH = Path(__file__).parent.parent / "tests/data/liquidsreflectometer-data"
_NEXUS_PATH = _DATAREPO_PATH / "nexus"
_DATAREPO_MISSING_REASON = (
    "Test data repository not available (DATA_READ_TOKEN may not be set for this run)"
)


@pytest.fixture(scope="session")
def datarepo_dir() -> str:
    r"""Absolute path to the liquidsreflectometer-data repository.

    Skips the test when the data repository has not been populated via LFS.
    """
    if not any(_DATAREPO_PATH.iterdir()):
        pytest.skip(_DATAREPO_MISSING_REASON)
    return str(_DATAREPO_PATH)


@pytest.fixture(scope="session")
def nexus_dir() -> str:
    r"""Absolute path to the event nexus files.

    Skips the test when the data repository has not been populated via LFS.
    """
    if not _NEXUS_PATH.exists() or not any(_NEXUS_PATH.iterdir()):
        pytest.skip(_DATAREPO_MISSING_REASON)
    return str(_NEXUS_PATH)


@pytest.fixture(scope="session")
def template_dir() -> str:
    r"""Absolute path to reduction/data/ directory"""
    return str(Path(__file__).parent / "data")
