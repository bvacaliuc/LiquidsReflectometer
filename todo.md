# Integrator: `settings-editor` (T2) v2 — REJECTED. Attempt 2 of N=3.

**Gate is GREEN** at the cleared tip `52bb800`: 140 launcher + 179 reduction,
`EXIT=0` (v1 was 128 + 145, so v2 added 46 tests). Every finding below is
invisible to it.

**Both blocking domains blocked.** `ui-aspects` found 3; `test-reviewer` found 4
across 73 mutations. Both advisory domains independently reached the first
cluster. I reproduced the mechanisms myself before writing this.

**v2 is a large, real improvement** — see "Confirmed fixed" at the bottom, and do
not rework any of it. Seven blocking findings collapse into **four clusters**,
and the first one is a single root cause.

---

## CLUSTER 1 (BLOCKING) — the refresh path was never updated to match the fixes

Every v2 repair landed on the **construction** path (`_build_editor`,
`_show_in_combo`, `_as_text`) and the **model** API (`Field.coerce*`). The
**refresh** path was not. And C6's own fix — `__init__` now calls
`set_document` (`:91`) so an injected document actually renders — routes startup
through `refresh_scalars`, so the stale path now runs on **every tab open**.

`_build_editor` and `refresh_scalars`/`refresh_angles` are two independent
implementations of *"show this value in this widget."* Three symptoms, one cause:

**1a. Scalar list fields corrupt on keyboard traversal alone.**
`:205` renders `_as_text(value)` -> `"50, 200"`. `:360` renders `str(value)` ->
`"[50, 200]"`. Only the first round-trips. And `:206` gates the validator on
`field.type in ("int","float")`, which is **False** for `"list[int]"` — so no
validator, so `hasAcceptableInput()` is always true, so `editingFinished` fires
on bare focus-out. `data_x_range` is the **first scalar editor in tab order**:

```
fresh tab, no edit:  box DISPLAYS '[50, 200]'   (should be '50, 200')
bare FocusOut, no typing:
  document now  ['[50', '200]']
  Problems      NOTHING REPORTED
  saved file    ['[50', '200]']
```

Affects `data_x_range` (always populated), `emission_coefficients`,
`LambdaMinUse`, `LambdaMaxUse`. Downstream:
`new_reduction_template_reader.py:144` emits `<x_min_pixel>[60</x_min_pixel>`.

**1b. `BkgROI` cells corrupt on any edit.** `refresh_angles:344` renders cells
with `str(value)`; for the one nested type (`list[list[int]]`) that is Python
repr, and `coerce_element` splits it on comma/space:

```
cell shows      '[120, 130]'
coerce_element  ['[120', '130]']
check_element   ''              <- reported clean
```
`nr_reduction_calc.py:510 -> :825` then runs `np.sort(BkgROI)` over strings.
Background ROI is the field a scientist tunes per angle.

**1c. After a Load, a combo displays a value the document does not hold.**
`_show_in_combo` (`:219-235`) runs only in `_build_editor`. `refresh_scalars`
(`:356-358`) calls bare `setCurrentText`, a **silent no-op** on a non-editable
combo. The `useCalcTheta` case is fully silent *and* unrecoverable from the UI:

```
load week1 -> combo 'sample_angle', doc 'sample_angle'   agree
load week2 (field omitted) -> combo 'sample_angle', doc False   DISAGREE
scientist re-selects 'sample_angle' to be sure -> doc still False
   (no currentTextChanged: the text never changed)
saved file: useCalcTheta=False
```
The widget says sample angle; the reduction uses the detector angle.

**Why nothing caught it — both guards are the rejected shape again.**
`test_a_scalar_list_edit_stores_a_list` (`launcher/tests/test_settings_editor.py:297`)
calls `editor.clear()` *before* typing, erasing the mis-rendered text before it
can be parsed. `test_a_combo_displays_a_value_outside_its_choices` (`:319`)
passes the document to the **constructor**, where `_show_in_combo` runs — never
the Load path, which is the only path a scientist takes. Neither can fail.

**Fix — one change, ~20 lines.** Collapse `_build_editor`'s and
`refresh_scalars`'s display logic into a single `_show(field, editor, value)`
called by both; render per-angle cells with the same `_as_text`; and make
`Field.check` / `_type_problem` **recurse into list elements** (`field_spec.py:167-181`,
`:287-290`) so the corruption is reportable rather than silent. Fix the two
tests: drop the `clear()`, and drive the combo test through `set_document`.

---

## CLUSTER 2 (BLOCKING) — the domain seam is half-derived, and already diverging

**Only 2 of 4 domains are derived.** `METHOD_CHOICES` and `CALC_THETA_CHOICES`
are (`nr_reduction_calc.py:85,91`). `DET_RES_CHOICES` and `PEAK_TYPE_CHOICES`
are **not wired anywhere** — `nr_tools.py:229,382,390,399` still hard-codes the
literals. So `reduction_domains.py:6-12`'s claim that *"drift is structurally
impossible rather than merely tested for"* is true for two domains and **false
for the two that are already drifting.**

**The divergence is live, and it is cry-wolf — the exact failure the commit says
it fixed:**

```
nr_tools.py:399   "DetResFn must be 'rectangular', 'gaussian', or 'none'"
DET_RES_CHOICES   ('rectangular', 'gaussian')
editor verdict    "'none' is not one of rectangular, gaussian"
```
A settings file the reducer runs perfectly is reported as a problem, and
`'none'` is unreachable from the combo.

**And the module's only logic has zero coverage, on the production path.**
`domains.lowered()` is the sole function in the new module and the reducer calls
it. Break it (`return list(choices)`) and `_validate_config` rejects
`'meantheta'` — **every reduction specifying a `method_per_run` raises
`ValueError`** — with the suite **91/91 green**. Coverage confirms
`reduction_domains.py:21` is `Missing`. Root cause: **no test in the repository
constructs `NR_Reduction` or calls `_validate_config`.** Three more survived:
adding a bogus method, dropping `'gaussian'`, adding `'lorentzian'` — all green.

`test_the_choice_lists_are_the_reducers_own` (`:524`) is a real `is`-identity
pin and does red, so *field_spec cannot re-mirror* — but nothing pins the
**content** against the code that enforces it. And
`test_the_reducer_validates_against_the_shared_domains` (`:534`) is an
`inspect.getsource` **grep**: a hand-copy using double quotes plus a dead
`domains.METHOD_CHOICES` reference passes it.

**Fix:** add `'none'` to `DET_RES_CHOICES` (or exempt it, and say why — note
`nr_reduction_calc._calc_detector_convolution:687-699` binds `pad` only under
`rectangular`/`gaussian`, so `'none'` currently raises `UnboundLocalError` there;
the two consumers disagree and a canonical-domains module must record that rather
than silently pick a side). Wire `nr_tools` to dispatch from `domains` so all
four are single-sourced. Replace the grep with **one behavioural test per
domain** that drives `_validate_config` / `fit_peak` / `calc_beam_on_detector`
with each declared value and asserts acceptance — that is the "both ways" guard.

**Integrator correction:** I told the campaign this fix was "derive-don't-mirror
done properly." That was **half right**. I verified the two domains
`nr_reduction_calc.py` consumes and did not check whether the other two were
wired at all. They are not, and one is already diverging.

---

## CLUSTER 3 (BLOCKING) — `SettingsDocument.config` is still unpinned

`src/lr_reduction/settings_document.py:102-105`. Renaming the property leaves
**91/91 green** (v1: 45/45 — the suite grew, the hole did not close). Zero
consumers repo-wide, tests included. Its own docstring: *"The wrapped config.
The reduction takes this object."* It is the handoff to the reducer and the seam
T3 builds on, and **the v1 rejection named it by name.** `set_document`,
`overrides` and `default_value` *are* now pinned; this one was missed.

**Fix:** one test asserting `doc.config` is the `NRReductionConfig` the reduction
receives, and that edits through `set()` are visible on it.

---

## CLUSTER 4 (BLOCKING) — two NEW tautologies, while fixing tautologies

**4a. `test_save_leaves_no_temporary_file_behind`** (`tests/unit/lr_reduction/test_settings_document.py:456`)
monkeypatches `json.dumps` to raise — which lands at `settings_document.py:318`,
**before** `tempfile.mkstemp` at `:321`. No temp file is ever created, so
`assert list(tmp_path.iterdir()) == []` is true by construction. Deleting the
entire `except BaseException: os.unlink(temporary)` block (`:333-338`) leaves it
green; coverage shows `333-338` `Missing`. **The commit message shows the author
diagnosed this exact reachability problem and re-aimed the sibling test — then
left this one aimed at the unreachable point.** Fix: inject at `os.replace` or
`os.fsync`.

**4b. `test_bounds_apply_to_per_angle_entries_too`** (`:430`) contains **no bound
violation** — it sets `ScaleFactor=1.0` (in range) and asserts `validate() == []`.
Neutering the whole per-angle `check_element` loop (`:247-251`) leaves it green.
This is the named guard for C2's *"the bounds finally apply to per-angle entries
too."* Relatedly `field_spec.py:217` (the `minimum` message) is `Missing` — **no
test exercises a below-minimum bound anywhere.** Fix: use an out-of-range value.

---

## Should-fix (same pass)

- **A partial fix on a shared sink reads as a complete one.** `Sname` correctly
  got `no_separators=True`; its four siblings in the *identical* f-string join —
  `subname`, `DTCsubname`, `BINsubname`, `errBINsubname` — did not. Measured:
  `subname = "/../../../../../../tmp/pwn"` is accepted by `validate()` and the
  sink resolves to `/tmp/pwn.dat` (`nr_reduction_calc.py:196,216,272-274`).
- **The path guard mis-models the fields it guards.** The four `_*_override`
  fields are not joined to a base — they **are** the whole path
  (`nr_reduction_config.py:116-134`). So the guard rejects their only legitimate
  shape (the absolute path `QFileDialog.getExistingDirectory()` returns, which
  `template_batch.py:301` already writes) while accepting relative values that
  resolve against the **process CWD**. Validate existence/writability instead,
  or resolve and check `is_relative_to(base_path)`.
- **`experiment_id = ".."` is accepted** — the field's own comment names `..` as
  the threat, but it is typed `str` so `_path_problem` never runs and
  `no_separators` does not catch a bare `..`.
- **`MAX_TABLE_ROWS` caps the display only.** `validate()` and `refresh_report()`
  are uncapped and on the hot path: a 4.9 MB settings file yields 1,000,003
  messages / a **74.7 MB** report string rebuilt on every edit.
- **`save_settings` builds a `QFileDialog` it never uses** (`:414-421`), then
  calls the **static** `getSaveFileName` — so `setDefaultSuffix("json")` is
  inert, and one dialog leaks per click. The suffix fallback also keys on
  `Path(path).suffix`, so `settings_0.5deg` has suffix `.5` and is not corrected.
- **`set_document` is not `@guarded`** (`:313`) — the one public entry without
  it, and the path T3 injects through.
- **`Field.coerce` and `_coerce_typed` each implement list-splitting**
  independently. C6's rationale was that triplication is what let `_coerce` and
  `_check_value` disagree; v2 collapsed three into two, not one.
- **A string per-angle value is exploded into characters** —
  `settings_document.py:182` guards on `len(current)`, so `"abc"` gives
  `['a','b','c']`. Guard on `isinstance(current, list)`.
- `DEFAULT_IF_EMPTY_NAMES` is exported and consumed by nothing.

---

## Confirmed FIXED — do not rework

- **Both v1 abort paths are closed**, driven to exit 0: the ragged short-column
  edit, and type-confused loads through the real Load button. `except Exception`
  on load plus `@guarded` on all eight slots held against 17 malformed inputs
  including `RecursionError`. Removing `@guarded` produces a real `qFatal`, so
  the guard is load-bearing and pinned.
- **Atomic save verified by fault injection** — `mkstemp` in the target dir,
  `fsync`, `os.replace`, `BaseException`-scoped cleanup, mode 0644 set *before*
  the rename. Pre-write and mid-write `ENOSPC` both left the prior file
  byte-identical with no temp litter. Symlink save refused, naming the real target.
- **Type fidelity through the widget is correct for every flat element type** —
  `False/false/0/no` -> `False`, `"117"` -> `int`, `"12000"` -> `float`, empty ->
  `None`, surviving save/reload. `BkgROI` (1b) is the only exception.
- **The three v1 tautologies are properly dead** — all seven disproof vectors go
  red, and the report test now works for a *structural* reason (`_seed` is seeded
  from the loaded config, so `changed_vs_seed()` is empty on the load path), not
  a re-wording.
- **`nr_reduction_calc.py`'s change is a verified no-op** — the derived lists
  reproduce the previous literals exactly, order-sensitive.
- Sorting pinned (`setSortingEnabled(False)`); `MAX_TABLE_ROWS` maps shown rows
  1:1 to document indices so removal stays correct; no new per-row widget
  surface, no double-connects, no `.destroy()`; the seven-key `sympify`
  allow-list is unwidened; new tests use `tmp_path`, not fixed `/tmp` names.

## Minimal path to green

1. One `_show(field, editor, value)` used by both render paths; `_as_text` for
   per-angle cells; recurse `check`/`_type_problem` into list elements. (Cluster 1)
2. Add `'none'` to `DET_RES_CHOICES` or exempt-and-explain; wire `nr_tools` to
   `domains`; one behavioural test per domain. (Cluster 2)
3. Pin `doc.config`. (Cluster 3)
4. Re-aim the temp-file fault to `os.replace`; put an out-of-range value in the
   bounds test. (Cluster 4)
5. Fix the two tests that cannot fail: drop `editor.clear()`; drive the combo
   test through `set_document`.
