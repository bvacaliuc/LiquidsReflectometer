"""The direct-beam maker's Cd override (upstream add-time-slicing, intake time-slicing-reconcile, plan T7).

create_db reads each run's attenuator setting (the Atten log: four Cd-foil flags, which _extract_cd_values turns into
a thickness) and reduces the runs in order of increasing Cd. A ``cd_list`` replaces the logged settings, one entry
per run in run order. The physics after that point is not under test: the stand-in for convert_to_binary records
which run is reduced first and stops the call. The NeXus reads are stand-ins too (the files need not exist), and
every path is a tmp_path.
"""

import logging
import re

import numpy as np
import pytest

import lr_reduction.binary_processing as BP
import lr_reduction.direct_beam_maker as dbm

THICK, NONE = [1, 1, 0, 0], [0, 0, 0, 0]  # Atten flags: two foils in, or none
A, B = 240001, 240002
LOGGED = {A: THICK, B: NONE}  # by the logs, B (no Cd) comes first


class StopError(Exception):
    """Raised by the convert_to_binary stand-in once the first run to reduce is known."""


@pytest.fixture
def maker(tmp_path, monkeypatch):
    """A Direct_Beam on tmp_path, whose log reads return LOGGED and whose first reduction is recorded."""
    seen = {"logs": [], "atten": [], "reduced": []}

    def logs(fname):
        run = int(re.search(r"REF_L_(\d+)", str(fname)).group(1))
        seen["logs"].append(run)
        return {"Atten": np.array(LOGGED[run])}

    def convert(fname, *args, **kwargs):  # noqa: ARG001
        seen["reduced"].append(int(re.search(r"REF_L_(\d+)", str(fname)).group(1)))
        raise StopError

    monkeypatch.setattr(BP, "get_log_values", logs)
    monkeypatch.setattr(BP, "convert_to_binary", convert)
    beam = dbm.Direct_Beam(NEXUSpath=str(tmp_path), savepath=str(tmp_path))
    real_extract = beam._extract_cd_values

    def extract(log_values, flip_atten=False):
        seen["atten"].append(list(log_values["Atten"]))
        return real_extract(log_values, flip_atten)

    monkeypatch.setattr(beam, "_extract_cd_values", extract)
    return beam, seen


def test_cd_list_overrides_the_log_and_sorts_runs(maker, caplog):
    """T7a: each run's Cd setting is cd_list's entry for it, in run order, not the log's; the runs are then reduced
    in order of increasing Cd (here A first, the reverse of the logs' order), and the override is logged."""
    beam, seen = maker
    with caplog.at_level(logging.INFO, logger=dbm.__name__), pytest.raises(StopError):
        beam.create_db([A, B], "db", plot=False, cd_list=[NONE, THICK])
    assert seen["atten"] == [NONE, THICK]
    assert seen["reduced"] == [A]
    assert any(record.name == dbm.__name__ and "cd_list" in record.getMessage() for record in caplog.records)


def test_without_cd_list_the_log_values_stand(maker):
    """T7b: without cd_list each run's Cd is its logged setting, and the runs are reduced by increasing Cd, as
    before the intake."""
    beam, seen = maker
    with pytest.raises(StopError):
        beam.create_db([A, B], "db", plot=False)
    assert seen["atten"] == [THICK, NONE]
    assert seen["reduced"] == [B]


@pytest.mark.parametrize("cd_list", [[NONE], [NONE, THICK, NONE]], ids=["one short", "one too many"])
def test_cd_list_of_the_wrong_length_raises(maker, cd_list):
    """T7c: a cd_list that is not one entry per run is a ValueError, before any run is read."""
    beam, seen = maker
    with pytest.raises(ValueError):
        beam.create_db([A, B], "db", plot=False, cd_list=cd_list)
    assert seen == {"logs": [], "atten": [], "reduced": []}
