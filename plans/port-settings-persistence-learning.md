# Learnings — `port-settings-persistence` (S3, campaign `exp-settings-roi`)

## 1. A restore that runs after its own save-signals are wired writes defaults back over the stored values

**Rule.** When a widget both restores state from a store and saves on
change, wire the save connections **after** the restore, or block signals
across it. Getting the order wrong produces a bug that looks like "settings
don't persist" while the save path works perfectly.

**Why.** Restoring calls `setText`/`setValue`/`setChecked`, and every one of
those emits the same signal a user edit does. If `save_settings` is already
connected, the restore round-trips: read stored value → set widget → signal →
save. Benign when the value survives the trip, destructive when it does not —
a stored value outside a spin's current range clamps first and then
overwrites the store with the clamped number, and a handler with side effects
does worse. In this slug `ipts_toggle.toggled` rewrites the path fields, so
restoring it unguarded would overwrite the paths that were just loaded; it is
restored under `blockSignals` for exactly that reason, and the whole
`read_settings()` call sits before the defense-in-depth connections.

**How to apply.** Order is `attributes → read_settings() → connect saves`.
Where a specific restore has side effects, `blockSignals(True/False)` around
that one widget as well — belt and braces, since the ordering rule is easy for
a later edit to silently break. A test that only asserts a value round-trips
will not catch a violation: the round trip still succeeds, it just writes
extra times. What catches it is a first-launch test asserting an empty store
yields widget defaults *and* leaves the store empty.

## 2. A ported test can pass without the feature — check what the RED actually proves

**Rule.** In a red-green port, verify that each ported test fails for the
reason you expect *before* implementing. A test that passes at RED is not a
free pass; it is a test that does not cover the behaviour you are about to
add, and it will keep passing if that behaviour regresses.

**Why.** PR #11's `test_isolation_from_legacy_launcher` sets the organization
and application names itself and then compares two `QSettings` filenames. It
passed against unmodified `exp` — it exercises the `isolated_qapp` fixture,
not the launcher. The behaviour the slug introduces, `main()` setting
ORNL / ornl.gov / lr_reduction_new_launcher before `QApplication([])`, was
covered by nothing in the plan's test list, on a slug whose review domain is
blocking specifically because QSettings wiring is the trap area. Its sibling
`test_direct_beam_first_launch_defaults` also passed at RED, though that one
becomes meaningful after GREEN as a guard against inventing values.

Verified by probe instead, which is weaker than a committed test because
nothing re-runs it:

```
3 identity setters at statements [0, 1, 2], QApplication at 3 — ordering correct
after main(): organization='ORNL' domain='ornl.gov' application='lr_reduction_new_launcher'
QSettings store: /home/6ov/.config/ORNL/lr_reduction_new_launcher.conf
```

**How to apply.** Enumerate RED results per test, not as a total, and treat
"passed at RED" as a finding to report rather than a line to skip. The
same gap appeared in S1, where the plan named a test as the detection for a
broken `exec_()` call site and that test never calls `exec_()` — two
instances in three slugs, so it is a pattern in ported test suites, not a
one-off. A plan's failure-mode matrix should cite the test that *fails
without the fix*, and the Developer should check that claim rather than
inherit it.

## 3. Keep concurrent ports out of each other's shared regions

**Rule.** When two slugs edit one file, keep each slug's hunks inside the
regions its plan claims, even at the cost of a small style compromise.

**Why.** S1 and S3 both touch `launcher/apps/direct_beam.py` — S1 rewrites
the two dialog classes, S3 adds `DirectBeamTab` methods. Disjoint, so both PRs
can merge in either order. Moving S3's function-local `import json` up to the
module import block would have been tidier in isolation, but S1 edits that
same import block to add `QDialog`/`QDialogButtonBox`, so the tidier choice
would have manufactured a merge conflict between two otherwise independent
PRs. The import stayed where the PR had it.

**How to apply.** Before a drive-by cleanup, check whether a sibling branch in
flight touches those lines (`git diff <other-feature-branch> -- <file>`).
Cleanups belong in a slug that owns the region, or in a follow-up after both
have merged.
