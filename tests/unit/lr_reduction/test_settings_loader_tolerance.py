"""The settings loader reads a file written by any version of the code.

A settings JSON, and the ``# Config:`` line of a reduced ``.dat``, are written from ``config.__dict__``: every
attribute the config had when the file was written is a key of the file. A version that has since dropped an
attribute (or has not gained it yet) used to refuse the whole file with ``AttributeError: <key> is not a valid config
parameter``. A key this version does not have is now skipped, with one warning that names the key, its value and the
file. ``override_params`` stays strict: those are typed by the caller in code, and a typo there should fail at once.
"""

import json
import logging

import pytest

import lr_reduction.new_reduction_from_file as nrff
from lr_reduction.nr_reduction_calc import NR_Reduction
from lr_reduction.nr_reduction_config import NRReductionConfig

#: A key no version of NRReductionConfig has had.
UNKNOWN = "a_setting_of_another_version"

LOADER_LOGGER = "lr_reduction.new_reduction_from_file"


def settings(**extra):
    """One sequence position, enough for NR_Reduction to accept the config."""
    return {"Sname": "from_file", "qmin": 0.008, "DBname": ["DB_A1.dat"], "RB_Ymin": [146], "RB_Ymax": [155], **extra}


def write_json(tmp_path, values):
    path = tmp_path / "REFL_1_settings.json"
    path.write_text(json.dumps(values, indent=2))
    return path


def write_dat(tmp_path, values):
    path = tmp_path / "REFL_1_combined.dat"
    path.write_text(f"# NR_runs = [1]\n# Config: {json.dumps(values)}\n# columns = Q, R, dR, dQ (sigma)\n"
                    "0.01 1.0 0.1 0.001\n0.02 0.5 0.05 0.002\n")
    return path


def warnings_of(caplog):
    return [record for record in caplog.records if record.name == LOADER_LOGGER and record.levelno == logging.WARNING]


@pytest.mark.parametrize("write", [write_json, write_dat], ids=["settings json", "dat header"])
def test_a_file_with_a_key_this_version_lacks_loads(tmp_path, caplog, write):
    path = write(tmp_path, settings(**{UNKNOWN: [1, 2]}))
    with caplog.at_level(logging.WARNING, logger=LOADER_LOGGER):
        config = nrff.json_to_config(nrff.load_from_file(path)["config"], source=path)
    assert isinstance(config, NRReductionConfig)
    assert (config.Sname, config.qmin, config.DBname) == ("from_file", 0.008, ["DB_A1.dat"])
    assert not hasattr(config, UNKNOWN)
    (warning,) = warnings_of(caplog)
    message = warning.getMessage()
    assert UNKNOWN in message and "[1, 2]" in message and str(path) in message


def test_each_skipped_key_is_named_once(caplog):
    with caplog.at_level(logging.WARNING, logger=LOADER_LOGGER):
        nrff.json_to_config(settings(first_gone=1, second_gone="two"))
    messages = [record.getMessage() for record in warnings_of(caplog)]
    assert len(messages) == 2
    assert sum("first_gone" in message for message in messages) == 1
    assert sum("second_gone" in message for message in messages) == 1


def test_a_file_of_this_version_loads_without_a_word(caplog):
    with caplog.at_level(logging.WARNING, logger=LOADER_LOGGER):
        config = nrff.json_to_config(dict(NRReductionConfig().__dict__))
    assert config.__dict__ == NRReductionConfig().__dict__
    assert warnings_of(caplog) == []


def test_a_key_that_names_a_read_only_property_is_skipped_too(caplog):
    """``base_path`` passes ``hasattr`` and has no setter: it is a key the config cannot take, like any other."""
    with caplog.at_level(logging.WARNING, logger=LOADER_LOGGER):
        config = nrff.json_to_config(settings(base_path="/elsewhere"))
    assert str(config.base_path) != "/elsewhere"
    (warning,) = warnings_of(caplog)
    assert "base_path" in warning.getMessage()


class StopError(Exception):
    """Raised by the stand-in reducer: the call got as far as reducing."""


@pytest.fixture
def one_group(monkeypatch):
    """reduce_from_file up to the reduction itself, without a NeXus file: one run at sequence position 1."""
    monkeypatch.setattr(nrff, "group_runs", lambda *_args: {"run_nums": [[1]], "seq_nums": [[1]], "seq_ids": [[1]]})
    received = []

    def stand_in(self, *_args, **_kwargs):
        received.append(self.config)
        raise StopError

    monkeypatch.setattr(NR_Reduction, "reduce", stand_in)
    return received


@pytest.mark.parametrize("write", [write_json, write_dat], ids=["settings json", "dat header"])
def test_a_reduction_from_such_a_file_runs_and_names_the_file(tmp_path, caplog, one_group, write):
    path = write(tmp_path, settings(**{UNKNOWN: 3}))
    with caplog.at_level(logging.WARNING, logger=LOADER_LOGGER), pytest.raises(StopError):
        nrff.reduce_from_file([1], path, "IPTS-00001", datapath=tmp_path, plot=False)
    (config,) = one_group
    assert config.qmin == 0.008
    (warning,) = warnings_of(caplog)
    assert UNKNOWN in warning.getMessage() and str(path) in warning.getMessage()


def test_the_time_resolved_folders_resolve_from_such_a_file(tmp_path):
    import lr_reduction.new_reduction_time_resolved as nrtr

    path = write_json(tmp_path, settings(**{UNKNOWN: 3}))
    nexus, out = nrtr.run_folders(path, "IPTS-00001", datapath=tmp_path / "nexus", savepath=tmp_path / "out")
    assert (nexus, out) == (tmp_path / "nexus", tmp_path / "out")


def test_an_override_the_config_lacks_still_raises(tmp_path, one_group):
    """Typed by the caller, in code: a typo fails at once, before anything is reduced."""
    path = write_json(tmp_path, settings())
    with pytest.raises(AttributeError, match=f"{UNKNOWN} is not a valid config parameter"):
        nrff.reduce_from_file([1], path, "IPTS-00001", datapath=tmp_path, plot=False, override_params={UNKNOWN: 3})
    assert one_group == []


def test_the_loader_hands_back_what_it_did_not_use():
    """A caller that shows the settings to someone (the settings editor) has to say what the file held and the
    config does not: the keys skipped, with their values, in the dict it passes as ``unused``."""
    unused = {}
    nrff.json_to_config(settings(first_gone=1, base_path="/elsewhere"), unused=unused)
    assert unused == {"first_gone": 1, "base_path": "/elsewhere"}
    nothing = {}
    nrff.json_to_config(settings(), unused=nothing)
    assert nothing == {}
