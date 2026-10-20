"""LR_REDUCTION_LOG_LEVEL: an opt-in console handler for the package's own loggers.

Unset, nothing changes: Python's lastResort handler prints WARNING and above and drops INFO/DEBUG, because no
handler is configured anywhere in the package. Set to a level, one stderr handler on the ``lr_reduction`` logger
prints every ``lr_reduction.*`` record at that level and above, and nothing else.
"""

import logging
import os
import subprocess
import sys

import pytest

import lr_reduction
from lr_reduction import configure_console_logging

HANDLER_NAME = "lr_reduction.console"
FORMAT = "%(levelname)s %(name)s: %(message)s"


def _console_handlers():
    return [h for h in logging.getLogger("lr_reduction").handlers if h.get_name() == HANDLER_NAME]


@pytest.fixture(autouse=True)
def _restore_package_logger():
    """Each test starts and ends with the package logger as an unset environment leaves it."""
    package = logging.getLogger("lr_reduction")

    def reset():
        for handler in _console_handlers():
            package.removeHandler(handler)
        package.setLevel(logging.NOTSET)

    reset()
    yield
    reset()


@pytest.mark.parametrize("value", [None, "", "  "], ids=["none", "empty", "blank"])
def test_unset_or_blank_attaches_nothing(value):
    assert configure_console_logging(value) is None
    assert _console_handlers() == []
    assert logging.getLogger("lr_reduction").level == logging.NOTSET


def test_set_attaches_one_stderr_handler_at_the_level():
    handler = configure_console_logging("INFO")
    assert isinstance(handler, logging.StreamHandler)
    assert handler.get_name() == HANDLER_NAME
    assert handler.stream is sys.stderr
    assert handler.formatter._fmt == FORMAT
    assert _console_handlers() == [handler]
    assert logging.getLogger("lr_reduction").level == logging.INFO


def test_child_logger_info_reaches_stderr_only(capsys):
    configure_console_logging("INFO")
    logging.getLogger("lr_reduction.unit_probe").info("ping")
    out, err = capsys.readouterr()
    assert err.splitlines() == ["INFO lr_reduction.unit_probe: ping"]
    assert out == ""


@pytest.mark.parametrize(
    "value, level",
    [("debug", logging.DEBUG), ("WARNING", logging.WARNING), ("WARN", logging.WARNING), ("10", 10), ("error", logging.ERROR)],
)
def test_level_names_and_integers(value, level):
    configure_console_logging(value)
    assert logging.getLogger("lr_reduction").level == level


def test_invalid_value_uses_info_and_warns_once(capsys):
    configure_console_logging("verbose")
    assert logging.getLogger("lr_reduction").level == logging.INFO
    lines = capsys.readouterr().err.splitlines()
    assert len(lines) == 1, lines
    line = lines[0]
    assert line.startswith("WARNING lr_reduction: ")
    assert "'verbose'" in line
    for accepted in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "integer"):
        assert accepted in line


def test_second_call_updates_the_level_without_a_second_handler():
    configure_console_logging("INFO")
    configure_console_logging("DEBUG")
    assert len(_console_handlers()) == 1
    assert logging.getLogger("lr_reduction").level == logging.DEBUG
    configure_console_logging(None)
    assert len(_console_handlers()) == 1


def test_a_warning_is_printed_once_not_twice(capsys):
    configure_console_logging("INFO")
    logging.getLogger("lr_reduction.unit_probe").warning("w")
    assert capsys.readouterr().err.splitlines().count("WARNING lr_reduction.unit_probe: w") == 1


@pytest.mark.parametrize("level", ["INFO", None], ids=["set", "unset"])
def test_import_time_switch_in_a_fresh_process(level):
    env = {k: v for k, v in os.environ.items() if k != "LR_REDUCTION_LOG_LEVEL"}
    if level is not None:
        env["LR_REDUCTION_LOG_LEVEL"] = level
    # the child imports this checkout's package, whatever an installed copy points at
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(lr_reduction.__file__)))
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [package_root, env.get("PYTHONPATH")]))
    program = "import logging, lr_reduction; logging.getLogger('lr_reduction.probe').info('ping')"
    result = subprocess.run([sys.executable, "-c", program], env=env, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    if level is None:
        assert result.stderr == ""
    else:
        assert "INFO lr_reduction.probe: ping" in result.stderr.splitlines()


def test_other_packages_are_untouched(capsys):
    configure_console_logging("INFO")
    logging.getLogger("not_lr_reduction").info("x")
    assert capsys.readouterr().err == ""
