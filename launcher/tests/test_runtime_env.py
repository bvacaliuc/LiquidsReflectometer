"""matplotlib's cache kept node-local, outside $XDG_CACHE_HOME, however the launcher is started.

The analysis nodes' login hook sets XDG_CACHE_HOME=/var/tmp/xdgcache-$USER and deletes it on every login shell,
so anything the launcher keeps there is gone when a scientist opens a second terminal. The launcher therefore
chooses matplotlib's cache directory itself (launcher/runtime_env.py), before anything imports matplotlib.

U1-U3 call the deciding function with a mapping and a base under tmp_path. V1 runs the three start paths in a
child interpreter, because the property that matters is the order of imports, which a call cannot show.
"""

import getpass
import logging
import os
import pathlib
import stat
import subprocess
import sys

import pytest

_REPO = pathlib.Path(__file__).resolve().parents[2]
_LOGGER = "launcher.runtime_env"
# Permission checks do not bind root, so the legs that rely on one are skipped there.
_NOT_ROOT = pytest.mark.skipif(os.geteuid() == 0, reason="root is not refused by file modes")


def _prepare(environ, base):
    from launcher.runtime_env import prepare_runtime_env

    return prepare_runtime_env(environ, base=str(base))


def _own_directory(base):
    return base / f"mpl-{getpass.getuser()}"


# --- U1: the types table ------------------------------------------------------------------------------------


@pytest.mark.parametrize("xdg", [None, "xdgcache-u", "elsewhere"], ids=["no-xdg", "hook-xdg", "other-xdg"])
def test_an_unset_cache_directory_is_created_private_under_the_base(tmp_path, xdg):
    """U1, L2: wherever XDG_CACHE_HOME points, or with it unset, MPLCONFIGDIR becomes <base>/mpl-<user>,
    created 0700. Nothing is made under XDG_CACHE_HOME."""
    environ = {} if xdg is None else {"XDG_CACHE_HOME": str(tmp_path / xdg)}

    chosen = _prepare(environ, tmp_path)

    expected = _own_directory(tmp_path)
    assert chosen == str(expected)
    assert environ.get("MPLCONFIGDIR") == str(expected)
    assert expected.is_dir() and not expected.is_symlink()
    assert stat.S_IMODE(expected.lstat().st_mode) == 0o700
    if xdg is not None:
        assert not (tmp_path / xdg).exists()


def test_my_existing_directory_is_reused_and_its_mode_left_alone(tmp_path):
    """U1: present, mine and writable: reused as it is, with no chmod."""
    existing = _own_directory(tmp_path)
    existing.mkdir()
    existing.chmod(0o750)
    environ = {}

    assert _prepare(environ, tmp_path) == str(existing)
    assert environ == {"MPLCONFIGDIR": str(existing)}
    assert stat.S_IMODE(existing.lstat().st_mode) == 0o750


def _make_file(path, _tmp_path):
    path.write_text("not a directory")


def _make_symlink_to_my_directory(path, tmp_path):
    target = tmp_path / "mine"
    target.mkdir(mode=0o700)
    path.symlink_to(target)


def _make_unwritable_directory(path, _tmp_path):
    path.mkdir(mode=0o700)
    path.chmod(0o500)


@pytest.mark.parametrize(
    "make",
    [_make_file, _make_symlink_to_my_directory, pytest.param(_make_unwritable_directory, marks=_NOT_ROOT)],
    ids=["a-file", "a-symlink", "not-writable"],
)
def test_a_path_that_is_not_my_writable_directory_is_refused(tmp_path, caplog, make):
    """U1, L4: a file, a symlink (never followed, even to a directory of mine) or a directory I cannot write:
    nothing is set, one line is logged, and the path is left exactly as it was."""
    path = _own_directory(tmp_path)
    make(path, tmp_path)
    before = path.lstat()
    environ = {"XDG_CACHE_HOME": str(tmp_path / "xdgcache-u")}

    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        assert _prepare(environ, tmp_path) is None

    assert environ == {"XDG_CACHE_HOME": str(tmp_path / "xdgcache-u")}
    assert len([r for r in caplog.records if r.name == _LOGGER]) == 1
    after = path.lstat()
    assert (after.st_mode, after.st_ino, after.st_mtime_ns) == (before.st_mode, before.st_ino, before.st_mtime_ns)


def test_another_users_directory_is_refused(tmp_path, caplog, monkeypatch):
    """U1, L4: a directory at the path owned by someone else is refused (the owner is compared with my uid)."""
    path = _own_directory(tmp_path)
    path.mkdir(mode=0o700)
    real_uid = os.getuid()
    monkeypatch.setattr(os, "getuid", lambda: real_uid + 1)
    environ = {}

    with caplog.at_level(logging.DEBUG, logger=_LOGGER):
        assert _prepare(environ, tmp_path) is None

    assert environ == {}
    assert len([r for r in caplog.records if r.name == _LOGGER]) == 1


@_NOT_ROOT
def test_a_base_that_cannot_be_written_is_refused_without_raising(tmp_path, caplog):
    """U1, L4: mkdir fails under the base: nothing is set, one line is logged, no exception leaves."""
    base = tmp_path / "read-only"
    base.mkdir()
    base.chmod(0o500)
    environ = {}
    try:
        with caplog.at_level(logging.DEBUG, logger=_LOGGER):
            assert _prepare(environ, base) is None
    finally:
        base.chmod(0o700)

    assert environ == {}
    assert not _own_directory(base).exists()
    assert len([r for r in caplog.records if r.name == _LOGGER]) == 1


def test_without_user_variables_the_name_comes_from_the_uid(tmp_path, monkeypatch):
    """U1: $USER (and getpass's other variables) unset: the name is the uid's, with the same outcome."""
    import pwd

    for name in ("LOGNAME", "USER", "LNAME", "USERNAME"):
        monkeypatch.delenv(name, raising=False)
    environ = {}

    expected = tmp_path / f"mpl-{pwd.getpwuid(os.getuid()).pw_name}"
    assert _prepare(environ, tmp_path) == str(expected)
    assert expected.is_dir()


def test_a_user_name_that_is_not_one_path_component_is_refused(tmp_path, caplog, monkeypatch):
    """U1, L4: a name that would leave the base ("a/b", "..") is refused rather than joined."""
    environ = {}
    for name in ("a/b", ".."):
        monkeypatch.setenv("LOGNAME", name)
        with caplog.at_level(logging.DEBUG, logger=_LOGGER):
            assert _prepare(environ, tmp_path) is None
    assert environ == {}
    assert sorted(p.name for p in tmp_path.iterdir()) == []


def test_the_directory_name_is_spelled_in_one_module():
    """U1, L5: the cache directory's name ("mpl-" and the user) appears in launcher/runtime_env.py and in no other
    launcher module, in code or in comments."""
    spelled = sorted(
        str(path.relative_to(_REPO))
        for path in (_REPO / "launcher").rglob("*.py")
        if "tests" not in path.relative_to(_REPO).parts and "mpl-" in path.read_text()
    )
    assert spelled == ["launcher/runtime_env.py"]


# --- U2: a preset MPLCONFIGDIR ---------------------------------------------------------------------------------


def test_an_empty_mplconfigdir_counts_as_unset(tmp_path):
    """U2: matplotlib treats an empty MPLCONFIGDIR as unset, and so does the launcher."""
    environ = {"MPLCONFIGDIR": ""}
    assert _prepare(environ, tmp_path) == str(_own_directory(tmp_path))
    assert environ["MPLCONFIGDIR"] == str(_own_directory(tmp_path))


def test_a_preset_mplconfigdir_is_left_alone(tmp_path):
    """U2, L1: the wrapper's or the user's choice wins. It is returned as the directory in force, the mapping is
    not touched, and neither it nor <base>/mpl-<user> is created."""
    preset = tmp_path / "preset"
    environ = {"MPLCONFIGDIR": str(preset), "XDG_CACHE_HOME": str(tmp_path / "xdgcache-u")}

    assert _prepare(environ, tmp_path) == str(preset)
    assert environ == {"MPLCONFIGDIR": str(preset), "XDG_CACHE_HOME": str(tmp_path / "xdgcache-u")}
    assert not preset.exists() and not _own_directory(tmp_path).exists()


# --- U3: the deciding module stays light ----------------------------------------------------------------------


def test_the_deciding_module_imports_neither_qt_nor_matplotlib():
    """U3, L3: importing launcher.runtime_env loads no Qt binding and no matplotlib, so calling it first can come
    before anything that fixes matplotlib's cache directory."""
    code = (
        "import sys, launcher.runtime_env\n"
        "heavy = {'matplotlib', 'qtpy', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6'}\n"
        "print(sorted(heavy & {name.split('.')[0] for name in sys.modules}))\n"
    )
    result = subprocess.run([sys.executable, "-c", code], cwd=_REPO, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "[]"


# --- V1: the three start paths, in a child interpreter -------------------------------------------------------

# Each leg imports launcher.new_launcher the way its start path does, without calling main(), then prints the
# directory matplotlib fixed. The base is redirected on the deciding module before the start path runs; the
# import is tolerated so that, before the module exists, the probe shows where the cache went.
_PROBE = """
import importlib.metadata, runpy, sys
try:
    import launcher.runtime_env
    launcher.runtime_env.NODE_LOCAL_BASE = sys.argv[2]
except ImportError:
    pass
if sys.argv[1] == "module":
    runpy.run_module("launcher.new_launcher", run_name="__probe__")
elif sys.argv[1] == "script":
    runpy.run_path(sys.argv[3], run_name="__probe__")
else:
    (entry,) = [ep for ep in importlib.metadata.entry_points(group="gui_scripts") if ep.name == "new_launcher"]
    entry.load()
import matplotlib
print("CACHEDIR=" + matplotlib.get_cachedir())
"""


@pytest.mark.parametrize("start", ["module", "script", "entry"])
@pytest.mark.parametrize("state", ["hook-xdg", "preset", "no-xdg"])
def test_every_start_path_fixes_the_cache_outside_the_hooks_directory(tmp_path, start, state):
    """V1, L1-L3: `python -m launcher.new_launcher`, `python launcher/new_launcher.py` and the `new_launcher`
    gui-script each leave matplotlib's cache in <base>/mpl-<user>, not under the hook's XDG_CACHE_HOME; with
    MPLCONFIGDIR preset, in the preset directory."""
    base = tmp_path / "var-tmp"
    base.mkdir()
    (tmp_path / "home").mkdir()
    env = {k: v for k, v in os.environ.items() if k not in ("MPLCONFIGDIR", "XDG_CACHE_HOME")}
    env.update(HOME=str(tmp_path / "home"), QT_QPA_PLATFORM="offscreen")
    if state != "no-xdg":
        env["XDG_CACHE_HOME"] = str(tmp_path / "xdgcache-u")
    if state == "preset":
        env["MPLCONFIGDIR"] = str(tmp_path / "preset")

    result = subprocess.run(
        [sys.executable, "-c", _PROBE, start, str(base), str(_REPO / "launcher" / "new_launcher.py")],
        cwd=_REPO, env=env, capture_output=True, text=True, timeout=100,
    )

    assert result.returncode == 0, result.stderr[-2000:]
    (line,) = [line for line in result.stdout.splitlines() if line.startswith("CACHEDIR=")]
    cachedir = line[len("CACHEDIR="):]
    expected = tmp_path / "preset" if state == "preset" else _own_directory(base)
    assert cachedir == str(expected.resolve())
    assert not (tmp_path / "xdgcache-u" / "matplotlib").exists()
