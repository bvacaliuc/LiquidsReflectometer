"""Save-path safety for #197's settings builder (close-out hardening, F2).

The builder defaults its target to `<IPTS>/shared/autoreduce/reduce_settings.json`
— the live file autoreduction reads — and wrote it with a truncating
`open(path, "w")`. A save that raises part-way therefore destroyed the file
rather than leaving it alone. Same class as the `save_config_json` truncation
shipped in PR #30; this is its third instance in the campaign.
"""

import json
from pathlib import Path

import pytest

from launcher.apps.json_settings_builder import atomic_write_settings, is_shared_autoreduce_path

pytestmark = pytest.mark.usefixtures("isolated_qapp", "no_qmessagebox")


def test_a_save_that_fails_part_way_leaves_the_prior_file_byte_intact(tmp_path, monkeypatch):
    """The property the truncating write did not have.

    Amendment-21 state axis: failed-write-OVER-AN-EXISTING-file, which is the
    state that matters and the one no test covered.
    """
    target = tmp_path / "reduce_settings.json"
    target.write_text('{"Sname": "the_previous_run"}')
    before = target.read_bytes()

    def boom(*_a, **_k):
        raise ValueError("serialisation blew up part-way")

    monkeypatch.setattr(json, "dumps", boom)

    with pytest.raises(ValueError):
        atomic_write_settings(target, {"Sname": "new"})

    assert target.exists(), "the failed save destroyed the previous settings"
    assert target.read_bytes() == before, "the failed save rewrote the previous settings"


def test_a_failed_replace_leaves_no_temp_file_behind(tmp_path, monkeypatch):
    """A crash between write and rename must not litter shared/autoreduce."""
    import os as _os

    target = tmp_path / "reduce_settings.json"
    target.write_text("{}")
    def _no_replace(*_a, **_k):
        raise OSError("replace failed")

    monkeypatch.setattr(_os, "replace", _no_replace)

    with pytest.raises(OSError):
        atomic_write_settings(target, {"Sname": "new"})

    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "reduce_settings.json"]
    assert leftovers == [], f"temp files left behind: {leftovers}"


def test_a_successful_save_round_trips(tmp_path):
    target = tmp_path / "reduce_settings.json"
    atomic_write_settings(target, {"Sname": "written", "qmax": 0.42})
    assert json.loads(target.read_text()) == {"Sname": "written", "qmax": 0.42}


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/SNS/REF_L/IPTS-1234/shared/autoreduce/reduce_settings.json", True),
        ("/SNS/REF_L/IPTS-1234/shared/autoreduce/sub/x.json", True),
        ("/home/user/scratch/reduce_settings.json", False),
        ("/SNS/REF_L/IPTS-1234/shared/other/reduce_settings.json", False),
    ],
)
def test_the_shared_autoreduce_path_is_recognised(path, expected):
    """The confirmation only means something if it fires on the right paths.

    Writing here changes what autoreduction does for the whole experiment, so
    it is worth a deliberate second look — but a guard that misfires on a
    scratch directory trains the user to click through it.
    """
    assert is_shared_autoreduce_path(Path(path)) is expected
