"""Round-trip guard for `new_reduction_from_file.save_config_json`.

The helper called the LOADER where it needed the SAVER
(`json.dump(json_to_config(config), ...)`), so there was no input for which it
worked: a dict raised `TypeError` (the config it built is not serializable) and
a config raised `AttributeError` (no `.items()`). Nothing called it — the
working saver was three lines inlined in the reduction flow — so the codebase
carried a correct saver that could not be reused and a reusable saver that was
broken, and the broken one was the named public API.

Nothing pinned the round trip, which is why an inverted call could sit in a
public function indefinitely.
"""

import json

import pytest

from lr_reduction.new_reduction_from_file import json_to_config, save_config_json
from lr_reduction.nr_reduction_config import NRReductionConfig


def _config():
    config = NRReductionConfig()
    config.Sname = "round_trip_run"
    config.qmin = 0.008
    config.DBname = ["db_0.nxs", "db_1.nxs"]
    return config


def test_save_config_json_writes_json_its_own_loader_reads_back(tmp_path):
    """The whole contract, and the thing no test asserted."""
    target = tmp_path / "settings.json"
    save_config_json(target, _config())

    restored = json_to_config(json.loads(target.read_text()))

    assert restored.Sname == "round_trip_run"
    assert restored.qmin == 0.008
    assert restored.DBname == ["db_0.nxs", "db_1.nxs"]


def test_the_round_trip_survives_the_override_backed_path_fields(tmp_path):
    """`Spath` and its three siblings are properties over `_*_override`.

    `__dict__` yields the PRIVATE names, and those are what `json_to_config`
    can set again. Round-tripping the public names would not survive the
    `hasattr`-gated load in the same way, so this pins that the saved document
    carries the private form.
    """
    config = _config()
    config._Spath_override = str(tmp_path / "out")
    config._NEXUSpathRB_override = str(tmp_path / "nexus")
    config._DBpath_override = str(tmp_path / "db")
    config._BINpath_override = str(tmp_path / "bin")

    target = tmp_path / "settings.json"
    save_config_json(target, config)
    payload = json.loads(target.read_text())

    for private in (
        "_Spath_override",
        "_NEXUSpathRB_override",
        "_DBpath_override",
        "_BINpath_override",
    ):
        assert private in payload, f"{private} did not survive the save"

    restored = json_to_config(payload)
    assert restored.Spath == (tmp_path / "out")
    assert restored.DBpath == (tmp_path / "db")


def test_save_config_json_is_not_the_loader(tmp_path):
    """Directly pins the inversion: the file must be a settings document.

    Without this, `json.dump(json_to_config(config))` could only be caught by
    the exception it happens to raise, which is a different assertion for each
    input shape and says nothing about what the file should contain.
    """
    target = tmp_path / "settings.json"
    save_config_json(target, _config())

    payload = json.loads(target.read_text())
    assert isinstance(payload, dict)
    assert payload["Sname"] == "round_trip_run"


@pytest.mark.parametrize("bad", [{"Sname": "x"}, "not-a-config", 17])
def test_a_non_config_is_refused_rather_than_writing_a_broken_file(tmp_path, bad):
    """A dict used to raise TypeError from inside json.dump — AFTER the file was
    opened, so it left a truncated file behind. Refuse before opening."""
    target = tmp_path / "settings.json"
    with pytest.raises((TypeError, AttributeError)):
        save_config_json(target, bad)
    assert not target.exists(), "a refused save must not leave a file"
