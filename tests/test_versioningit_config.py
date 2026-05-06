import re
import subprocess

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def test_versioningit_match_glob_present():
    """Protocol-internal tag namespace (qa/*, review/*, triage/*, analysis/*)
    must be invisible to versioningit. The robust way is a positive 'match'
    allow-list pinned to release tags; see
    plans/build-versioningit-tag-glob-plan.md on
    analysis/new_workflow-repairs-2026-04 for the rationale.
    """
    with open("../pyproject.toml", "rb") as fh:
        cfg = tomllib.load(fh)
    vcs = cfg["tool"]["versioningit"]["vcs"]
    assert "match" in vcs, (
        "[tool.versioningit.vcs].match is required so versioningit ignores "
        "protocol-internal qa/*, review/*, triage/*, analysis/* tags."
    )
    assert any("v" in g and "[0-9]" in g for g in vcs["match"]), (
        f"Unexpected match glob: {vcs['match']!r}; expected something like ['v[0-9]*']."
    )


def test_versioningit_match_glob_finds_release_tag():
    """Sanity: the configured glob actually matches at least one tag in this
    repo's history. Catches a future glob typo.
    """
    out = subprocess.run(
        ["git", "describe", "--tags", "--match=v[0-9]*", "HEAD"],
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, (
        f"git describe --match='v[0-9]*' failed: {out.stderr!r}. "
        f"Either no v* release tags are reachable from HEAD or the glob is wrong."
    )
    assert re.match(r"^v\d+", out.stdout), f"Unexpected git describe output: {out.stdout!r}"
