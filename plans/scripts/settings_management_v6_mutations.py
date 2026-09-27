#!/usr/bin/env python3
"""Mutation battery for settings-management T3 v6.

Amendment 16 (mutate-once): every helper the v6 diff INTRODUCES or RE-POINTS
gets one row per call site, and each row records a MEASURED observation, not a
predicted one. Run from the repo root:

    pixi run python plans/scripts/settings_management_v6_mutations.py

Restore safety (Developer contract, `todo-mutation-harness-restore-safety.md`):
the v5 battery twice hit the 10-minute Bash ceiling mid-mutation and left
mutated source on disk. So here:

* every target file's original bytes are held in memory AND written to a
  mode-600 backup before anything is touched;
* the restore is in a ``finally``, so it runs on exception and on KeyboardInterrupt;
* after each restore the file's sha256 is compared with the original and the
  run ABORTS if it differs — a silent half-restore is the failure mode that
  costs a session;
* each pytest invocation carries its own ``--timeout``, so a hang-mode mutation
  reds instead of wedging the battery.
"""

import hashlib
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EDITOR = os.path.join(REPO, "launcher/apps/settings_editor.py")
RESOLVER = os.path.join(REPO, "src/lr_reduction/settings_resolver.py")

LAUNCHER_TESTS = "launcher/tests/test_settings_editor.py"
GLOBAL_TESTS = "launcher/tests/test_global_settings.py"
RESOLVER_TESTS = "tests/test_settings_resolver.py"

#: (row, description, file, old, new, test-path, -k selector)
MUTATIONS = [
    (1, "_record_edit records the whole column again (per-angle branch)", EDITOR,
     "                self._session_edits[(name, row)] = copy.deepcopy(current[row])",
     "                self._session_edits[name] = copy.deepcopy(current)",
     LAUNCHER_TESTS, "survives_loading_an_experiment or does_not_resurrect"),

    (2, "_record_edit binds the live object (no copy)", EDITOR,
     "            self._session_edits[name] = copy.deepcopy(current)",
     "            self._session_edits[name] = current",
     LAUNCHER_TESTS, "bound_by_copy"),

    (3, "_pre_resolve_overrides drops the reassembly (v5 read-back)", EDITOR,
     "                if 0 <= row < n_angles:\n                    column[row] = value\n                    placed = True",
     "                if False:\n                    column[row] = value\n                    placed = True",
     LAUNCHER_TESTS, "survives_loading_an_experiment or does_not_resurrect"),

    (4, "_record_structural_change ignores removed_row (no rebind)", EDITOR,
     "        if removed_row is not None:\n            self._rebind_cells_after_removal(removed_row)",
     "        if False:\n            self._rebind_cells_after_removal(removed_row)",
     LAUNCHER_TESTS, "does_not_resurrect or reappear_on_a_new_angle"),

    (5, "_rebind_cells_after_removal keeps the removed row's own edit", EDITOR,
     "            if row == removed_row:\n                continue",
     "            if False:\n                continue",
     LAUNCHER_TESTS, "does_not_resurrect or reappear_on_a_new_angle"),

    (6, "_on_cell_changed stops passing the row (call site)", EDITOR,
     "        self._record_edit(name, row=row)",
     "        self._record_edit(name)",
     LAUNCHER_TESTS, "survives_loading_an_experiment or does_not_resurrect"),

    (7, "remove_selected_angle stops passing removed_row (call site)", EDITOR,
     "        self._record_structural_change(removed_row=row)",
     "        self._record_structural_change()",
     LAUNCHER_TESTS, "does_not_resurrect or reappear_on_a_new_angle"),

    (8, "_forget_per_angle_edits blind to tuple keys", EDITOR,
     "            if (key[0] if isinstance(key, tuple) else key) in fs.PER_ANGLE_NAMES",
     "            if key in fs.PER_ANGLE_NAMES",
     GLOBAL_TESTS, "per_angle_edits_do_not_follow"),

    (9, "USER_AUTHORITY_LAYERS stops deriving from LAYERS", RESOLVER,
     '    sorted(key for key, layer in LAYERS.items() if layer.authority == "user")',
     '    sorted(key for key, layer in LAYERS.items() if layer.authority == "nobody")',
     RESOLVER_TESTS, "projections_of_the_table or refuses_layer_a"),

    (10, "LAYER_LABELS stops deriving from LAYERS", RESOLVER,
     "LAYER_LABELS = {key: layer.label for key, layer in LAYERS.items()}",
     'LAYER_LABELS = {key: "?" for key in LAYERS}',
     RESOLVER_TESTS, "projections_of_the_table"),

    (11, "a LAYER_ORDER member loses its LAYERS entry (fail-closed check)", RESOLVER,
     '    "d": Layer("d", "experiment template", "experiment"),\n',
     "",
     RESOLVER_TESTS, "declares_an_authority"),

    (12, "the sidecar read bypasses _read_json (2nd call site)", RESOLVER,
     "        records = _read_json(sidecar)",
     "        import json as _j\n        records = _j.loads(sidecar.read_text())",
     RESOLVER_TESTS, "fifo_sidecar"),
]


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    targets = sorted({m[2] for m in MUTATIONS})
    originals = {}
    backups = {}
    for path in targets:
        with open(path, encoding="utf-8") as fh:
            originals[path] = fh.read()
        fd, backup = tempfile.mkstemp(prefix="v6mut-", suffix=".bak")
        os.close(fd)
        os.chmod(backup, 0o600)
        with open(backup, "w", encoding="utf-8") as fh:
            fh.write(originals[path])
        backups[path] = backup
        print(f"backup {path} -> {backup}")
    clean = {path: sha(path) for path in targets}

    results = []
    try:
        for row, desc, path, old, new, testpath, selector in MUTATIONS:
            source = originals[path]
            if source.count(old) != 1:
                results.append((row, desc, f"SKIPPED anchor x{source.count(old)}"))
                print(f"\n[{row}] ANCHOR MISS ({source.count(old)}) — {desc}")
                continue
            try:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(source.replace(old, new))
                proc = subprocess.run(
                    [sys.executable, "-m", "pytest", "-q", "--no-header", "-p",
                     "no:cacheprovider", "--timeout=75", "--timeout-method=thread",
                     testpath, "-k", selector],
                    cwd=REPO, capture_output=True, text=True, timeout=200,
                )
                tail = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
                observed = tail[-1] if tail else f"exit {proc.returncode}"
            except subprocess.TimeoutExpired:
                observed = "HUNG (harness timeout 200s)"
            finally:
                # Restore FIRST, always, then prove it.
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(originals[path])
                if sha(path) != clean[path]:
                    raise SystemExit(f"ABORT: {path} did not restore cleanly")
            results.append((row, desc, observed))
            print(f"\n[{row}] {desc}\n     {observed}")
    finally:
        for path in targets:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(originals[path])
            state = "OK" if sha(path) == clean[path] else "*** DIRTY ***"
            print(f"restored {path}: {state}")

    print("\n\n=== ledger rows ===")
    for row, desc, observed in results:
        print(f"| {row} | {desc} | {observed} |")


if __name__ == "__main__":
    main()
