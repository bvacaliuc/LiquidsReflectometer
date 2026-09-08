# Integrator: `settings-editor` (T2) v1 — REJECTED. Two process-abort paths, silent type corruption, three tests that cannot fail.

**Gate is GREEN** at `371fe57`: 128 launcher + 145 reduction, `EXIT=0`. Every
finding below is invisible to it. Attempt 1 of N=3 — budget is fine, and the
work is concrete.

Four reviewers ran (per the plan's Review domains). **Both blocking domains
found blocking defects**, and the two advisory domains independently confirmed
the most severe one. I reproduced the three worst myself before writing this.

Organised by **fix cluster**, not by reviewer — several findings share one root
cause and one repair.

---

## C1 (BLOCKING) — Editing a cell aborts the whole launcher. Two independent triggers.

`launcher/apps/settings_editor.py:227` -> `src/lr_reduction/settings_document.py:153-157`

```python
current = self.get(name)
if current is None:                 # pads only for None ...
    current = [None] * self.n_angles
if not 0 <= index < len(current):   # ... not for a SHORT list
    raise IndexError(f"No angle at index {index} (have {len(current)})")
```

`[]` is not `None`, so a per-angle field shorter than `n_angles` is never
padded. An unhandled exception in a Qt slot under PyQt5 calls `qFatal()` ->
`abort()`. **The whole `ReductionInterface` process dies, taking every other
tab's unsaved state with it.** Reproduced by me, and independently by two
reviewers:

```
IndexError: No angle at index 1 (have 1)
  settings_editor.py:227 -> settings_document.py:157
  EXIT=134   (SIGABRT)
```

**It is reachable from valid, ordinary files — three ways:**

1. **The broadcast idiom.** `n_angles` is the *max* length across per-angle
   fields, and a 1-entry `method_per_run` for N angles is explicitly sanctioned
   by the reducer (`nr_reduction_calc.py:76-78`) and deliberately exempted by
   `validate()` (`settings_document.py:198`). Rows 1..N-1 of that column render
   empty, look unset, and invite the edit that kills the process.
2. **The editor's own output.** `normalize()` drops the runtime-owned fields by
   design, so its round trip is *already* in the crashing state. Verified:
   ```
   n_angles = 2 -> normalize() drops RBnum -> reload gives RBnum: []
   edit row 1 of RBnum -> IndexError: No angle at index 1 (have 0)
   ```
   **Save, reload, edit — a crash cycle using only the editor's own artifacts.**
3. **Following the report's own advice.** Load
   `{"DBname": ["db_a"], "tof_min": [1.0,2.0,3.0]}`; the panel says
   `Direct-beam file (DBname) has 1 entries for 3 angles`; typing the value it
   asks for aborts.

**Second, independent abort path — malformed load.** `validate()` assumes every
per-angle value is a sequence, and `load_settings`' `try` covers only
`from_file`: the `refresh_angles/refresh_scalars/refresh_report` calls at
`settings_editor.py:314-316` are **outside** it, and the catch is only
`(ValueError, OSError)`. Verified:

```
{"tof_min": 5}      -> TypeError: object of type 'int' has no len()   [settings_document.py:198]
{"LambdaMin": 3.5}  -> TypeError: 'float' object is not iterable      [settings_document.py:191]
  -> escapes the slot -> EXIT=134
```
A deeply-nested JSON gives `RecursionError` by the same route. Truncated or
wrong-schema files on shared IPTS dirs are ordinary, not hostile.

**Fix (one cluster):**
- pad in `set_angle_field`: `if current is None or len(current) < self.n_angles`
  — the branch already exists for `None`, extend it to short;
- make `validate()` *report* a non-sequence per-angle value instead of iterating
  it (a wrong type is a reportable problem, not a crash);
- move the three refresh calls inside the `try`, broaden to `except Exception`,
  and give **every** slot (`_on_cell_changed`, `_on_scalar_edited`,
  `add_angle`, `remove_selected_angle`, `load_settings`, `save_settings`) a
  top-level guard that reports into the panel. The existing
  `except (ValueError, OSError)` shows the intent; the table handlers just lack it.

---

## C2 (BLOCKING) — Every `list[...]` field stores a raw string. Silent wrong science.

`launcher/apps/settings_editor.py:192-213` (`_coerce`) branches on `"int"` and
`"float"` only. Every per-angle type is `list[int]` / `list[float]` /
`list[bool]` / `list[list[int]]`, so **no per-angle cell is ever coerced** —
nor are the scalars `data_x_range`, `emission_coefficients`, `LambdaMinUse`,
`LambdaMaxUse`. Verified by me:

```
RB_Ymin   declared=list[int]    stored=['150']    elem=str
tof_min   declared=list[float]  stored=['150']    elem=str
useBS     declared=list[bool]   stored=['False']  elem=str
```

Downstream, against the real consumers:

| consumer | input | result |
|---|---|---|
| `nr_reduction_calc.py:508,971` `if self.config.useBS[i]:` | `"False"` | truthy -> **background subtracted when the scientist turned it off** |
| `new_reduction_from_template.py:224` `useBS[0] == 1` | `"1"` | False -> **the opposite error, same field** |
| `new_reduction_template_reader.py:144` `str(data_x_range[0])` | `"60, 210"` | writes `x_min_pixel=6`, `x_max_pixel=0` |
| `nr_reduction_calc.py:964` `ypix >= RB_Ymin[i]` | str | comparison against a string |
| `save_reduced_data.py:71` | `"1.05"` | a string scale factor in the reduced-data header |

**Detection is zero.** `_check_value` (`settings_document.py:225`) returns `""`
for anything not `int`/`float`, so `validate()` reports *No problems found* — and
the declared `minimum`/`maximum` are therefore never applied to any per-angle
value either. Table cells carry no validator (only scalar `QLineEdit`s do).
The saved file *looks* correctly authored.

**Fix:** `_coerce` must unwrap `list[...]` to its element type, with an explicit
bool parse (`{"true","1","yes"}` — never `bool(str)`); give `data_x_range` a real
two-value editor; and extend `_check_value` to report a value whose Python type
contradicts `field.type`. **Put `coerce()` and `check()` on `Field`** in the
Qt-free module (see C6) rather than adding a third copy in the view.

---

## C3 (BLOCKING) — Three tests cannot fail. Fourth consecutive slug with this exact defect.

**C3a — `test_validation_report_names_the_offending_field`**
(`launcher/tests/test_settings_editor.py:183`). `refresh_report()` emits two
sections, and the second prints the field *name*
(`settings_editor.py:294`). So `set("Qline_threshold", 4.0)` puts the string in
the changed-vs-seed section and the assertion passes before validation is
consulted. Measured:

```
validate() stubbed to []                      -> 15 passed
SettingsDocument.validate() returns [] always -> 15 passed
refresh_report replaced by a hard-coded
  setPlainText("Qline_threshold changed_name") -> 15 passed  <- satisfies BOTH report tests
```
Fix: assert on the *validation line* (`"is above 1.0"`), or that the report
contains every string in `document.validate()`; and drive the refresh through a
gesture — deleting `refresh_report()` from `_on_scalar_edited` also survives,
because both tests call it by hand.

**C3b — `test_normalize_drops_runtime_owned_fields`**
(`tests/unit/lr_reduction/test_settings_document.py:269`) iterates the same
derived tuple that drives the filter it checks. Measured:

```
drop runtime_owned=True from RBnum   -> 30 passed  (and normalize() then emits
                                        an authored RBnum into the reduction —
                                        exactly what the docstring forbids)
RUNTIME_OWNED_NAMES = ()             -> 45 passed
```
Fix: literal assertion — `assert {"RBnum","LambdaMinUse","LambdaMaxUse"}.isdisjoint(normalized)`
— plus a separate pin on the tuple itself.

**C3c — `test_set_angle_field_uses_the_index_it_is_given`**
(`test_settings_document.py:174`) edits index 0, the one index a hard-coded `0`
satisfies. `updated[0] = value` (index ignored) -> 30 model tests passed. Fix:
edit index 1 of 3. (The view-level twin at `test_settings_editor.py:110` **is**
genuinely falsifying — verified.)

**The pattern, stated plainly:** all three have the same shape as the three
prior rejections — *the assertion is satisfied by something other than the code
the test names.* A sibling report section; a tuple derived from the subject; an
index that makes the mutation a no-op. **A standing gate would have caught all
three in under a minute: for every new guard test, mutate the named thing once
and confirm it reds before committing.** Recommend adopting that as a
plan-level requirement for the remaining slugs.

---

## C4 (BLOCKING, security-advisory) — `save()` destroys the previous good file on any failed write

`src/lr_reduction/settings_document.py:256`:

```python
with open(path, "w") as fd:      # truncates immediately, before a byte is produced
    json.dump(make_json_safe(self.to_dict()), fd, indent=2)
```

Confirmed: a mid-dump failure left a file that had held `{"good": "settings"}`
containing a partial, invalid document. Prior content gone, no backup, on a
network mount. Realistic triggers: IPTS quota (ENOSPC), a stalled `/SNS`
sshfs/NFS mount, **or the launcher aborting via C1 while a save is in flight.**

Related, same rewrite: **`save()` follows symlinks** (CWE-59/61) — confirmed,
`link.json -> victim.txt` left the settings JSON in `victim.txt`. The
`QFileDialog` overwrite confirmation fires on the *link's* name, so it conceals
the target. And the file mode is left entirely to umask (observed 0644).

**Fix:** `NamedTemporaryFile(dir=path.parent, delete=False)` -> `flush()` ->
`os.fsync()` -> `os.replace()`. Same-directory temp keeps the rename atomic on
the target filesystem; the fsync matters because `close()` on NFS/FUSE does not
imply durability. Open the temp with `O_EXCL|O_NOFOLLOW` and set the mode
explicitly (0644 is the right value for a file meant to be shared — do **not**
use 600 here). Refuse, or warn naming the resolved target, when
`path.is_symlink()`.

---

## C5 (BLOCKING, design-advisory) — `useCalcTheta` is a checkbox; the reducer wants an enum

`field_spec.py:189-191` declares `type="bool"`. The reducer validates against
`['detector_angle','sample_angle']` and treats `True` as a legacy alias for the
former (`nr_reduction_calc.py:88-96`). Consequences, verified: a loaded
`'sample_angle'` validates clean and renders as a checked box; toggling it
stores `True`, **silently downgrading the config to `detector_angle`**; and
`'sample_angle'` is unreachable from the editor entirely.

The FIELD_SPEC guards compare *defaults* to the class, not domains, so this
passes. Fix: declare `type="str"` with
`allowed=('detector_angle','sample_angle')`.

**Same class, unguarded:** `METHOD_CHOICES` / `DET_RES_CHOICES` /
`PEAK_TYPE_CHOICES` (`field_spec.py:38-44`) hand-mirror bare local lists in
`nr_reduction_calc.py:84,92` with **no** guard test, unlike the
FIELD_SPEC<->NRReductionConfig relationship which has three. Promote those lists
to module constants and **import** them, or add an AST-parsing guard.

---

## C6 — Required before T3 starts (T2 gates T3)

T3's `SettingsResolver` consumes this module's public shape, so these are
interface decisions, not polish:

- **Move `coerce()`/`check()` onto `Field`.** Both are pure `(Field, value)`
  functions with no Qt. Today the type dispatch is *triplicated* —
  `_build_editor` (widget), `_coerce` (text->value), `refresh_scalars`
  (value->widget, keyed on `isinstance` rather than `field.type`), plus
  `_check_value` (validation). `_coerce` and `_check_value` already disagree, and
  **that disagreement is C2.** T3 will otherwise write the third copy.
- **`__init__` never calls `refresh_angles()`** (`settings_editor.py:59`), so
  `SettingsEditorTab(document=doc_with_angles)` renders **zero rows** — and
  `document=` is precisely the injection path T3 needs. Add a `set_document()`
  doing the three refreshes (currently inlined at `:314-316`).
- **Add `overrides()`** — the non-default values only. A resolution stack needs
  what a layer *contributes*; `to_dict()` is everything and `normalize()` is
  everything-minus-runtime-owned.
- **`Field.default` hands out a shared mutable list.** `frozen=True` protects
  the binding, not the list. T3 layering *starts* from defaults; the first
  consumer that mutates one corrupts the table process-wide. Store tuples or
  return a copy.
- **`field_spec.TYPES` is dead** (referenced nowhere) and nothing asserts
  `f.type in TYPES`, so `"flaot"` would silently yield an unvalidated
  `QLineEdit`. Two assertions alongside the existing three close it — and they
  are the guards that would have caught C2's premise.

---

## Should-fix (cheap, same pass)

- **Sorting is one line from re-introducing the row-index bug.**
  `isSortingEnabled()` is False today but `sectionsClickable()` is True and
  nothing pins it. After one `sortItems()`, editing the top row wrote to a
  different document index. Call `setSortingEnabled(False)` explicitly with a
  comment and assert it in the row-isolation test.
- **Validation cries wolf** — a valid 3-angle file reports 9 problems, of which
  6 are false by this codebase's own logic (`RBnum` is `runtime_owned`;
  `ThetaShift`/`useBS`/`ScaleFactor`/`tof_min`/`tof_max` are auto-defaulted at
  `nr_reduction_calc.py:100-109`). `settings_document.py:19-25` names this
  failure mode and then exempts `broadcast_ok` only. Note the two mechanisms
  differ: `method_per_run` broadcasts from len-1, these five default from len-0
  — a `default_if_empty` flag models both honestly. Training the scientist to
  ignore the panel is how C2 stays invisible.
- **Optional-list `None` is a one-way door.** Once any Lambda cell is touched,
  the "derive from choppers" state is unreachable without reloading. Collapse an
  all-`None` optional list back to `None` in `set_angle_field`.
- **`n_angles` is unbounded** — measured ~1100x memory amplification
  (100k angles = 488 KB file -> 675 MB RSS, 8.9 s frozen on the GUI thread).
  Cap rows in the view with a report line.
- **Path fields are unvalidated** and honored verbatim: `experiment_id="/etc/passwd"`
  replaces the base path; `Sname="../../../.bashrc"` redirects
  `save_reduced_data.py:36-44`. The sink is **pre-existing**, but this is the
  first UI making these routinely authorable and `validate()` says clean.
  Reject absolute paths and `..` components for `type=="path"`, and path
  separators in `Sname`.
- **A file saved without an extension cannot be reloaded** —
  `load_from_file` dispatches on suffix and raises `Unsupported file type:`.
  Use `setDefaultSuffix("json")`.
- **A combo silently ignores an out-of-set loaded value**
  (`settings_editor.py:272`) — displays `supergauss` while the document holds
  `sombrero`.
- **Removing an angle can change the method for every remaining angle** — a
  1-entry broadcast list emptied by a remove sends all angles back to the
  reducer's default, and `validate()` stays silent.
- **Untested, each one mutation-confirmed dead:** `angle_row()` (returns row 0
  always -> 45 passed); `save()`'s whole-document contract (`save`->`normalize`
  -> 45 passed); any `minimum` bound (stripping all seven -> 45 passed);
  `ensure_identity()` *ordering* (moving it after `QSettings()` -> 15 passed);
  both file-error paths; the empty-editor-means-`None` decision;
  `editingFinished` vs `textChanged`; the numeric validators;
  `remove_angle`'s bounds check; `SettingsDocument.config` — the actual T3
  handoff, renaming it -> 45 passed.
- **The Qt-free guard is defeated by a transitive import.** Adding
  `from launcher.app_identity import ensure_identity` to `settings_document.py`
  keeps 30 tests passing while genuinely pulling in `PyQt5.QtCore`. The AST
  guard is correct for what it names but sees only that file's own imports.
  **One subprocess test** — import the two model modules, assert no Qt in
  `sys.modules`, then exercise the document — closes this *and* asserts the
  property T3 actually depends on.

---

## Confirmed sound — do not rework these

- **The declared trap is genuinely absent.** The active-row-as-hidden-input bug
  is not present, and both pinning tests are real: breaking
  `_on_cell_changed` to read `currentRow()`, and `remove_selected_angle` to
  hardcode row 0, each makes its named test red. `currentRow()` appears exactly
  once, where the selection *is* the user's input.
- **The FIELD_SPEC<->NRReductionConfig mirror is exemplary** — enumerated, not
  a subset, and catches both directions: a bogus field (10 failed), a removed
  scalar (1), a removed per-angle field (2), a dropped `per_angle` flag (1), a
  wrong default (1), a hard-coded `PER_ANGLE_NAMES` (5).
- **No injection sink is reachable from a settings file.** The one
  code-execution-shaped path (`wavelength_resolution_function` -> `sympify`) is
  fed from the *instrument* settings, and `apply_config_overrides`
  (`nr_reduction_calc.py:1137-1157`) copies only seven numeric geometry keys —
  that key is not among them and is not an `NRReductionConfig` attribute.
  Deserialization is `json.load` only; no pickle/yaml/eval/exec anywhere on the
  path; `json_to_config` gates every key on `hasattr`.
- **Qt lifecycle is clean** — no `.destroy()`, no double-connects (all
  `.connect()` calls are in `_build_*`, invoked once), every widget reparented
  before its builder returns.
- **The checkbox hit-area test is a real measurement**, not a proxy — it asks
  the style for `SE_CheckBoxClickRect` and fails when the size policy is removed.
- **Mock-heaviness is low** — 2 monkeypatches in 213 lines, both replacing a
  modal dialog static. Real widgets, real `QTest` gestures throughout.
- **`ensure_identity()` is called first** in `__init__` (`:39`), before the
  first `QSettings()`, honoring S3's adoption contract deliberately. The
  launcher wiring matches the sibling pattern exactly.

## Integrator correction to my own review brief

I told all four reviewers that the name-coverage guard "uses `json_to_config`
and expects `AttributeError`." **It does not.**
`test_field_spec_names_are_real_config_attributes:25-33` is a
`set(NRReductionConfig().__dict__)` subset check; `json_to_config` appears only
in its docstring as rationale and at `:69` in a different test, and the
`pytest.raises(AttributeError)` at `:61` is on `setattr`. Substantively the real
mechanism is **stricter** than I described (`__dict__` vs `hasattr`), so nothing
downstream is affected — but the docstring at `:26-31` describes a rationale the
body never executes, which is worth tightening while you are in the file.
