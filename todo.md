# Integrator review gate — `port-settings-persistence` v2 REJECTED

Supersedes the v1 rejection recorded in this file at `01d7e6f`
(`git log -- todo.md`). **Both v1 blocking findings are resolved**, and
three of the v1 advisories were adopted. The v2 rejection is one new
blocking finding that **both** reviewers reached independently.

**Disposition: blocking, per the plan's own declaration** —
`ui-aspects-reviewer (blocking)` returned it, so no Integrator departure
was needed. The advisory `test-reviewer` found the same defect from a
different direction and quantified it more precisely; that is now the
third consecutive cycle in which the non-gating domain contributed
decisively.

**Gate: green.** `test-launcher` **34 passed** (2 harness + 32 slug),
`test-reduction` **107 passed**, exit 0, 534.61 s, no race this cycle.

**Retry budget:** the plan records attempt 2; charter §1 sets N = 3. A v3
is the last retry before the escalation path.

## v1 findings — RESOLVED (verified by the Integrator)

- **B1 fixed, and completely.** `_apply_ipts_mode()` is split out
  (`direct_beam.py:484-493`) and called explicitly after
  `blockSignals(False)` (`:399`) with a comment naming the invariant; the
  restore default is now **`False`** (`:395`), preserving deployed
  first-launch behavior. The blocking reviewer confirmed `:492-493` are the
  *only* writers of those two enabled states and that every mode-changing
  path reaches the helper; the restore order (`:399` before the `setText`
  at `:400-401`) is correct because `setText` works on disabled widgets.
- **B2 fixed.** The tautological, identity-leaking test is gone, replaced
  by real tests of real code — five distinct mutations of the
  identity/migration module are caught.

**Three v1 advisories were also adopted** — worth naming, because they were
recorded rather than gated and the Developer picked them up anyway: a
shared `launcher/app_identity.py` with importable constants, tab-level
identity establishment for non-GUI entry, and a legacy-store migration.

## B3 — BLOCKING: the identity install orphans ~61 of 63 persisted keys

`main()` now calls `ensure_identity()` before anything constructs a
`QSettings`, which repoints the store for the **entire `new_launcher`
process** — not only the two tabs this slug touches. The accompanying
`migrate_legacy_settings()` carries `LEGACY_KEYS`, which is two names.

Ground truth, measured by the Integrator against `agentic/exp`:

```
distinct QSettings keys written across launcher/apps : 63
modules writing them                                 : 11
keys carried by LEGACY_KEYS                          : 2
```

Both reviewers reproduced the loss end-to-end by seeding a realistic
nameless store and running exactly `ensure_identity(); migrate_legacy_settings()`:
one measured 9 keys lost from an 11-key sample, the other 54 from the
ground-truth key list. The Integrator independently confirmed the two
worst-hit consumers are live `new_launcher` tabs:
`file_batch.py:324-358` reads **11** keys (`settings_runs`,
`settings_experiment_id`, `settings_dir`, `settings_file`,
`settings_datapath`, `settings_DBpath`, `settings_Spath`, …) and
`sld_calculator.py:57-59` reads 2 — added at `new_launcher.py:39`
("Batch file") and `:51` ("SLD calculator").

**User-visible failure.** A scientist upgrades and launches. Direct beam
and Overplot remember — the slug's promise, delivered. The **Batch file**
tab beside them comes up blank: run list, experiment id, settings dir and
file, data path, DB path, save path, all gone. SLD Calculator is back to
`Si`/`1.54`. Seven more tabs lose their templates and output directories.
No error, no warning; the old values still sit in
`Unknown Organization.conf`, which nothing reads any more.
**The slug whose stated symptom is "the deployed GUI forgets typed values"
makes nine of its tabs forget everything, once, on exactly one launch.**

**Honest framing, and it is not a v2 regression in origin.** v1's inline
`setOrganizationName` had the identical radius, and **both v1 reviews and
this Integrator missed it.** It becomes v2's to own because v2 is the cycle
that added a migration, and therefore owns the question *"does the
migration cover what the identity move breaks."* The GREEN commit's
"Everything else starts fresh — PR body states the policy" reads as a
policy only because the fixture holds two keys; stated against 61 it reads
as a regression. The module comment is also factually wrong on ground
truth:

```python
# The pre-identity store had no organization; these are the only keys it held
# that are worth carrying forward.
LEGACY_KEYS = ("overplot_folder", "overplot_xscale")
```

It is not "the only keys it held," and the value judgment is hard to
defend for `reduction_template`, `settings_datapath`, `template_dir`,
`30Hz_template` — long facility paths a scientist types once.

**Fix.** Migrate wholesale (`for k in legacy.allKeys()`) or from an
explicit launcher key list, gated on a **sentinel key**
(`settings_migrated_from_legacy`) rather than inferred from data, so
"one-shot" is recorded rather than guessed. Two cautions from the blocking
reviewer if you take the wholesale route: `Unknown Organization.conf` is
the shared dumping ground for every Qt app on the machine that forgot to
set an organization, so a blind `allKeys()` copy can import a foreign
app's keys — the risk concentrates in the generically-named `output_dir`
(`xrr.py:67,74`) and `db_output_dir` (`quick_reduce.py:98`). Enumerating is
safer. **If the narrow policy is genuinely intended, that is the human's
call on the MR, made against the number 61 — not the number 2.**

Guard test: seed a nameless store with one key per affected module, run the
`main()` prologue, assert every key survives, and assert a second run is a
no-op.

## Advisory — carry into v3

- **`ensure_identity()`'s `or` predicate leaves the org empty when
  `applicationName()` is auto-derived.** Two complementary probes, both
  correct: the Integrator confirmed that with `QApplication([])` — the
  shipped path — both names stay empty and the identity installs properly;
  the blocking reviewer showed that `QCoreApplication(["x/script.py"])`
  auto-fills `applicationName()` from `argv[0]`, so the guard early-returns
  and the org stays empty, resolving to
  `Unknown Organization/script.py.conf`. So the shipped entry points are
  fine, but the module docstring's stated reason for the tab-level call —
  *"a non-GUI entry point (a script…) resolves the same store"* — fails for
  any script using the conventional `QApplication(sys.argv)`, and T2/T3 are
  contractually pointed at this function. Fix: gate on
  `if app.organizationName(): return` only.
- **The two shipped entry points now diverge.** `pyproject.toml` ships both
  `launcher` and `new_launcher`, both include the SLD tab, and
  `launcher/launcher.py:42-46` does not call `ensure_identity()`. After
  this slug, `sld_composition`/`sld_wavelength` resolve to the ORNL store
  under one binary and the nameless store under the other. One line fixes
  it, but land it **with** the B3 migration, since it widens the orphan set.
- **`migrate_legacy_settings()` clears the identity outside its `try`**
  (`app_identity.py:50-60`). If the second or third setter raised, the
  `finally` never runs and the session is left with an empty organization —
  the same process-global mutation surface v1 was rejected on. Open the
  `try` immediately after the capture. Worth a comment that the function is
  not reentrant, and is safe only because `main()` calls it before
  `QApplication` exists.
- **A restored checked toggle can display path text contradicting the IPTS
  in use** (`direct_beam.py:495-501`): `_ipts_toggled` derives paths only on
  a toggle edge, and `ipts_edit.editingFinished` saves without re-deriving.
  `_run_create_db` uses the correct IPTS, so nothing computes wrongly, but
  the greyed field misstates provenance and v2 is the first version where
  that survives a restart.

## Test discrimination — real improvement, one structural gap left

**Closed:** all 18 keys now have a parametrized round-trip (was 5 of 18,
with `run_list` — the most-typed field — uncovered); a genuine
reaches-disk assertion exists and makes `DirectBeamTab.save_settings`'s
`sync()` load-bearing; the identity/migration module has five caught
mutations. 12 of 33 mutation probes are now caught, against near-zero at v1.

**The one that matters most is still open, and it is structural.** No test
crosses a process boundary, so the string→type coercion layer a real
restart depends on is entirely unexercised. Demonstrated: inverting
`_bool`'s string branch leaves **32/32 green**, while a genuine two-process
restart against the same mutated code returns the IPTS toggle and the plot
checkbox **inverted**. Credit where it is due — the same probe against the
*unmutated* code round-trips all 18 keys correctly, including INI-escaped
JSON and the comma-bearing run list: **the production code is right, the
suite simply cannot tell.** The cause is that Qt serves a second in-process
`QSettings()` from the first's cached `QConfFile`, so in-process restart
testing of QSettings is structurally impossible.

One subprocess restart test closes six gaps at once (`_bool`'s string
branch, the float coercion, the non-dict guard, the range clamp, a real
disk round-trip for all 18 keys, and `main()`'s identity wiring). Shape:
spawn `sys.executable -c …` twice with `HOME`/`XDG_CONFIG_HOME` in
`tmp_path`; phase 1 saves, phase 2 constructs a fresh tab and prints the
values as JSON. **Comment why the subprocess is required**, or someone will
"simplify" it back in-process.

Also still open, highest value first:

- **1 of 16 signal→save connections is covered.** Dropping the other 15,
  individually or together, leaves the suite green — and the two
  `save_settings()` calls after the Cd/moderator dialogs are revertible
  too, which matters because they are the *only* persistence path for
  `cd_vals`/`mod_vals`. One table-driven test over
  `(widget, signal, setter, key)` takes this from 1/16 to 16/16 in ~15
  lines.
- **`_ipts_toggled`'s own `_apply_ipts_mode(state)` call is revertible** —
  only the *restore* call site is covered, so the path a scientist actually
  exercises (clicking the toggle) has no test. A regression there
  reproduces B1's symptom from the other direction.
- **`ensure_identity()` in both tab constructors is revertible**, and it is
  not dead code: removed, a directly-constructed tab resolves to the
  nameless store. Uncovered because the fixture always pre-installs an
  identity, so the install branch is never taken where it matters.
- **`test_migrate_legacy_settings_never_overwrites` is order-dependent** —
  with the never-overwrite guard deleted it fails when run with its
  neighbour but **passes when run alone**, because it relies on the
  preceding test's leftover value. Seed its own distinct legacy value.
- **`test_migrate_legacy_settings_copies_and_restores_identity` blanks the
  process-global identity without `try/finally`** — structurally the
  pattern B2 was rejected for. Correct-and-flag on the GREEN commit body:
  it says "that test now restores in a `finally`," which is true of
  `test_ensure_identity_installs_when_unset` but **not** of this one.
- Both identity tests assert Qt statics where `QSettings().fileName()` —
  the user-visible consequence — is available.
- Overplot's `folder`/`xscale` keys and its newly added `sync()` remain
  uncovered.

## Suggested v3 order

1. **B3** — widen the migration with a sentinel gate, and build its fixture
   from the ground-truth key list rather than a hand-picked pair. If the
   narrow policy is intended instead, say so in the PR body against the
   real number and let the human decide on the MR.
2. **The subprocess restart test** — highest leverage remaining; closes six
   gaps and would have caught the `_bool` inversion.
3. `ensure_identity()` org-only predicate; `try` opened before the clears;
   `ensure_identity()` in `launcher/launcher.py` (land with item 1).
4. The 16-connection table test, the live-toggle test, and making
   `never_overwrites` self-contained.
