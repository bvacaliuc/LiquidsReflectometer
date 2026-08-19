# Integrator review gate — `port-settings-persistence` v1 REJECTED

**Disposition: blocking, per the plan's own declaration.** This plan
declares `ui-aspects-reviewer (**blocking** — QSettings wiring and
widget-state round-trips are its exact trap list)`, and that reviewer
returned two blocking findings. No interpretation was needed on my part
this time — unlike the S2 rejection, where I had to depart from an
advisory declaration. Calibrating the domain to the risk worked exactly as
intended.

Both blocking findings were verified in source by the Integrator before
rejecting; they are independent of the test outcome.

**Test status — read this before chasing anything.** `test-launcher`
**9 passed** (harness 2 + this slug's 7). `test-reduction` reported
**2 failed, 105 passed**, but **neither failure is attributable to this
branch**: `test_compute_sf_with_deadtime_tof_200` and
`..._tof_200_sort` are the known cross-clone `/tmp` race, the same one
diagnosed in full during the `port-cd-dialog-resize` cycle.
`tests/test_scaling_factors_workflow.py` hardcodes `output_dir = "/tmp"`
and four of its tests share `/tmp/sf_197912_Si_test_dt.cfg`, written
asynchronously (`wait=False`); another clone was running the same suite
concurrently (verified by `ps`, distinct env hash). Both failures carry
the *identical* assertion value (7.057973681032683) across two different
tests with different parameters — the signature of reading one foreign
file, not of numerical drift. This branch touches only `launcher/**` and
cannot affect scaling-factor computation.

**Confirmed:** both tests re-run **serialized** (after waiting for the
competing PID to exit) → **2 passed** in 111.96 s, exit 0, at this same
SHA in an identical environment. The failures are external interference;
they consumed no retry budget and are not part of this rejection.

## B1 — the `blockSignals` guard defends against nothing and causes a real desync

Both reviewers found this independently; the test reviewer supplied the
argument that settles it.

**Mechanism, verified line by line:**

- `launcher/apps/direct_beam.py:227-228` — `ipts_toggle = QCheckBox(...)`
  with no `setChecked`, so the widget's own default is **unchecked**.
- `:348` — `ipts_toggle.toggled.connect(self._ipts_toggled)`, connected
  **before** `read_settings()`.
- `:354` — `read_settings()`.
- `:358-373` — the `save_settings` connections, all **after**
  `read_settings()`. This includes `:360`'s
  `ipts_toggle.toggled.connect(lambda _: self.save_settings())`.
- `:387-393` — restore order is `run_list` → `ipts_edit` → **toggle under
  `blockSignals`, defaulting to `True`** → `nexus_edit` → `savepath_edit`.
- `:476-487` — `_ipts_toggled` is the **only** code that enforces
  `checked ⇒ nexus_edit/savepath_edit disabled`.

The GREEN commit justifies the guard as "its toggled handler rewrites the
path fields, so an unguarded restore would overwrite what it just loaded."
That is not what the ordering does. Without the guard, `_ipts_toggled`
would fire, derive paths from the already-restored `ipts_edit`, *and*
disable the fields — and then `:392-393` would overwrite the derived paths
with the stored values anyway (`setText` works on disabled widgets). The
net effect of **removing** `blockSignals` is: same stored values, plus the
correct enabled state. The only other thing it suppresses is the
`toggled → save_settings` lambda, which is connected *after*
`read_settings()` and therefore does not exist during the restore.

**So the guard protects against nothing that exists, and costs the
invariant.** After restore the checkbox reads "Use IPTS path structure"
while NEXUS path and Save path remain **enabled and editable**.

**User-visible failure.** Fresh install, Direct-beam tab. The toggle is
ticked (the restore default is `True`, flipping the deployed first-launch
behavior, which was unchecked). NEXUS path and Save path look live and
empty. The scientist types `/SNS/REF_L/IPTS-36776/nexus/` and a custom
output directory, enters a run list, clicks **Create DB**. `_run_create_db`
(`:536`) takes the `if self.ipts_toggle.isChecked():` branch, which never
reads those two fields — **both typed paths are silently discarded** and
the direct beam is written to the derived
`/SNS/REF_L/IPTS-<n>/shared/transmission/`. If IPTS happens to be empty
they instead get "Please provide IPTS when using IPTS path structure"
while staring at two filled-in path fields. The desync persists until the
toggle is clicked twice.

**Fix.** Split the handler so the mode can be applied without rewriting
restored values:

```python
def _apply_ipts_mode(self, state):        # enable/disable only
    self.nexus_edit.setEnabled(not state)
    self.savepath_edit.setEnabled(not state)

def _ipts_toggled(self, state):           # derive paths, then apply mode
    if state and self.ipts_edit.text().strip():
        ...  # unchanged derivation
    self._apply_ipts_mode(state)
```

and call `self._apply_ipts_mode(self.ipts_toggle.isChecked())` right after
`blockSignals(False)`. Simply deleting the guard is also correct per the
ordering analysis above, but the split states the intent.

**Also reconsider the `True` default** (`:390`). It is a faithful port —
PR #11 has the identical line — but it changes the first-launch behavior of
a *functional* control on a deployed line. `False` preserves what `exp`
does today. Flagging the inherited choice, not the port.

**Guard tests:** construct with `direct_beam_use_ipts_path_structure=True`
and assert `nexus_edit.isEnabled() is False` and
`savepath_edit.isEnabled() is False`; repeat for `False`. Add
`ipts_toggle.isChecked()` and `nexus_edit.isEnabled()` to
`test_direct_beam_first_launch_defaults` — it currently asserts the IPTS
field and three TOF spins, i.e. every widget *except* the one whose
first-launch semantics this slug changed.

## B2 — a test installs the **production** QSettings identity process-globally and never restores it

`launcher/tests/test_settings_persistence.py:76-84`:

```python
bare = QtCore.QSettings(); bare.setValue("any_key", "legacy_value"); bare.sync()
QtCore.QCoreApplication.setOrganizationName("ORNL")
QtCore.QCoreApplication.setApplicationName("lr_reduction_new_launcher")
new = QtCore.QSettings()
assert new.fileName() != bare.fileName()
```

Two defects in nine lines.

**(a) It leaks the production identity into the rest of the pytest
process.** `organizationName`/`applicationName` are `QCoreApplication`
statics; neither this test nor `conftest.py`'s `isolated_qapp` restores
them. Combined with the harness defect I verified earlier this session —
**Qt caches the settings root at the first `QSettings` construction in a
process**, so `isolated_qapp`'s per-test `XDG_CONFIG_HOME` redirect is a
no-op for every test after the first — this is a reachable path to writing
the developer's **real** `~/.config/ORNL/lr_reduction_new_launcher.conf`,
which is precisely the production store this slug introduces. The
ui-aspects reviewer reproduced the write on this machine (and removed the
file). It does not fire today only because, under `pixi run test-launcher`,
the first `QSettings` happens to be constructed inside a fixture-scoped
test — luck of ordering, not design. Adding `pytest-randomly`, a
fixture-less test, or any module-level widget construction flips it; T2 and
T3 will add more settings tests on this same fixture.

**(b) It does not test what its name claims.** `bare` is constructed under
the *fixture's* `test-org-…`/`test-app-…`, not under the legacy launcher's
org-less identity, so `new.fileName() != bare.fileName()` is a tautology —
two different org/app pairs always yield different files. It asserts Qt's
own org/app→path contract, not this repo's code, and it passes on
unmodified `exp` (the RED commit says so honestly). The real legacy store
is `~/.config/Unknown Organization.conf`.

**Fix.** Delete or rewrite the test — as written it costs an identity leak
and buys nothing. If kept, use `QSettings("ORNL", "lr_reduction_new_launcher")`
explicitly (no global mutation), and compare against a `bare` whose org/app
are cleared to `""`.

**Harness fix that belongs with it** (in `conftest.py`, benefiting every
launcher test file including S1's and S2's): capture and restore
org/app/domain around the `yield`, and make the redirect actually hold with
`QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))`,
which is **not** subject to the cached path hash. Then assert it took:

```python
assert QtCore.QSettings().fileName().startswith(str(tmp_path))
```

That single assertion converts a silent clobber of a developer's real
config into a loud failure, regardless of test ordering.

## What the Developer got RIGHT (verified, worth stating)

The ui-aspects reviewer specifically checked this diff for the three defect
classes that sank S2, and **none is present**:

- **No write-on-construct.** `read_settings()` runs before every save
  connection and there is no `save_settings()` call in either `__init__`.
  The S2 data-loss pattern is absent.
- **Round-trip symmetry is complete** for all 18 `direct_beam_*` keys and
  all 3 `overplot_*` keys — every key both written and read, names matching,
  restoration guarded where the widget has a non-empty default.
- **No restore re-triggers a save** (checked for all seven spins, both
  checkboxes, both combos, six line edits).
- **Scope holds** (charter §3): exactly the four planned files, keys all
  per-tab and prefixed, nothing reaching into the T2/T3 layers.
- The `overplot.py` two-liner is the right fix: `overplot_ytransform` was
  already *read* with an allow-list guard on `exp` but never *written* — a
  dead read. This completes the round-trip, and `sync()` is correct.
- The RED commit's self-audit of its own zero-signal tests is exactly the
  discipline S2's review found missing. Keep doing that.

## Advisory — carry into v2, not gating

- **13 of 18 `direct_beam` keys have no test**, including `run_list` — the
  most-typed field in the tab and the first symptom the plan names — and
  `mod_vals`, the structural twin of the one blob that *is* tested. A
  parametrized round-trip over all 18 keys is ~15 lines.
- **All 16 signal→save connections are untested**: every test calls
  `save_settings()` explicitly, but in production nobody does. Delete
  `:358-373` entirely and all 7 tests stay green. One test that mutates a
  widget and emits `editingFinished` covers the block.
- **No test reaches disk.** A second `QSettings` for the same org/app shares
  the first's in-memory `QConfFile`, so every "restart" here is satisfied
  from memory; `deleteLater()` without an event-loop turn never runs.
  Both `sync()` calls can be deleted with the suite green. One assertion —
  read `tab.settings.fileName()` and grep the key — makes the write path
  load-bearing.
- The identity strings are inline literals in `main()` and re-typed in the
  test, while the plan makes this slug the **source of truth** T2/T3 must
  adopt. Hoist to importable constants (`ORG_NAME`, `ORG_DOMAIN`,
  `APP_NAME`); a typo in a future copy would silently split the store.
- Identity is set only inside `main()`, so any non-GUI entry point that
  constructs a tab resolves to a different store. An idempotent
  `ensure_identity()` called from `main()` and each tab's `__init__` is the
  robust form.
- **Store path moves with no migration**: `exp` users' `overplot_folder`
  and `overplot_xscale` live in the org-less
  `~/.config/Unknown Organization.conf` and will silently vanish on first
  launch after upgrade. Two re-typeable preferences, so low blast radius —
  but decide it now, before T2/T3 add more keys. Either one-shot migrate or
  state the reset in the PR body.
- Three GREEN-commit claims are not test-backed and one is wrong: the
  `_bool` coercion is dead on the tested binding (which returns real
  `bool`s), the range-clamp claim is asserted by nothing, and the
  `blockSignals` justification is contradicted by the ordering (B1).
- Pre-existing on `exp`, not introduced here, but adjacent: `overplot.py`'s
  `save_settings` stores `folder_edit.text()` unstripped while other sites
  compare `.strip()`ed — a trailing space saves fine and then fails
  `isdir` next launch. Worth a follow-up.

## Suggested v2 order

1. B1 — split `_ipts_toggled` / apply the mode after restore, and settle
   the `True` default. Add the enabled-state assertions.
2. B2 — delete or rewrite the identity test; fix `conftest.py` isolation
   (restore org/app, `setPath`, assert the redirect took). The conftest fix
   benefits S1 and S2 as well.
3. Then the advisory coverage gaps, highest value first: one signal-driven
   save test, one disk assertion, the 18-key parametrization, and the
   survives-a-degraded-restore test.
