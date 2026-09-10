# Integrator: `settings-management` (T3) v1 — REJECTED. Attempt 1 of N=3.

**Gate is GREEN** at `0fe640d`: 162 launcher + 265 reduction, `EXIT=0`. Every
finding below is invisible to it.

**Both blocking domains blocked** (`design-reviewer`, `ui-aspects-reviewer`), and
`test-reviewer` found five more including an **unreported survivor in the
amendment-16 record**. `security-review` found 0 should-block and says why:
*"the reason is structural, not luck: the resolver has no production caller."*

14 blocking findings across three domains, organised below by **cluster**. Most
collapse into C1.

---

## C1 (BLOCKING) — nothing in the shipped application calls the resolver

```
grep -rn 'discover_ipts_settings|resolve_all|save_resolution|SettingsResolver' \
     launcher/ src/ scripts/ --include=*.py | grep -v /tests/
  -> global_settings.py: imports GLOBAL_WHITELIST and NotWhitelistedError (constants only)
  -> settings_resolver.py: its own definitions
```

`set_resolution` is test-only, so `self.provenance` stays `{}` and **every badge
renders empty in the shipped launcher**. Layer (a) is written by the new menu item
and read by nobody but the dialog that wrote it. Layers (c)/(d) are never
discovered. The one Save a user can press calls `document.save()`, which drops
provenance; `save_resolution` has no caller.

T3 was chartered to replace "a muddle of sources with no defined precedence". The
muddle is untouched, with a second, unreached mechanism beside it — **42 green
tests and zero consumers.** A taxonomy nothing consults has not replaced anything.

**This is also why the other clusters are latent rather than live.** Wiring it
without fixing them turns each into a live defect, so C1 must be fixed *last*, or
together with the rest.

---

## C2 (BLOCKING) — the provenance record is unreadable, and it contradicts itself

**C2a — the file every other door refuses.** `save_resolution` writes
`PROVENANCE_KEY = "_provenance"` at the **top level** of a reduction settings JSON
(`settings_resolver.py:294,310-314`). Verified:

```
json_to_config({'_provenance': {}, 'qmin': 0.01})
  -> AttributeError: _provenance is not a valid config parameter
SettingsDocument.from_dict / from_file -> ValueError, same cause
```

`save_resolution` takes an arbitrary path, and nothing stops it being
`reduce_settings.json` / `_up` / `_down` — the three names
`lr_autoreduce/new_reduce_REF_L.py:112-121` reads. **Drop one in
`shared/autoreduce` and the autoreduction stops loading that experiment.** The
existing test asserts `json_to_config(document.normalize())` — the *document*,
never the *file that was written*. Put provenance in a sidecar, or teach the
loader to skip the key; the docstring's "one file" argument has to be paid for on
the reader side.

**C2b — provenance goes stale inside `resolve_all` itself.**
`settings_resolver.py:201-207` snapshots provenance, builds the document, *then*
calls `_equalise_angles`, which rebinds padded lists the snapshot never sees:

```
document   RB_Ymin : [100, 110, None]
provenance RB_Ymin : [100, 110]
file carries TWO disagreeing copies of one datum
```

Storing `value` in `as_record()` at all creates the persisted version of the
two-implementations-of-one-answer defect this commit congratulates itself on
closing. Also asymmetric: 55 provenance entries vs 52 settings — provenance
asserts an origin for `RBnum`, which `normalize()` drops.

**C2c — the badge keeps claiming a layer after the value changes, and names a
specific wrong file.** Mutators call `refresh_report()` only; `set_document`
(public, wired to the Load button) renders badges from whatever `self.provenance`
still holds:

```
after the user types 0.25 : shown='0.25' held=0.25 badge='[a]' "Value came from: user preference"
after Load someone_else.json:
  qmin shown='0.004' badge='[c]' tooltip names reduce_settings_up.json   <- wrong file
```

`set_resolution`'s own docstring says setting document and provenance separately
"is how a display and the thing it describes drift" — and `set_document` is
exactly that separate setter, left public. Fix structurally: make provenance
travel *with* the document (`set_document(document, provenance=None)`), have each
mutator record `Resolved(value, "b")` and re-badge, and cover
`add_angle`/`remove_selected_angle` (a removal shifts a column the header still
attributes).

---

## C3 (BLOCKING) — T2's defects recur verbatim in the new file

**C3a — the `str()` renderer is back.** `global_settings.py:151` renders a list
with `str(value)`, ~100 lines from this commit's own written account of that exact
failure in `settings_editor.py:231-245`. Verified, **zero typing** — open the
dialog and press Save:

```
held        : [1.5, 2.5, 3.5]
dialog shows: '[1.5, 2.5, 3.5]'
read back   : ['[1.5', 2.5, '3.5]']      <- corrupted
_as_text would have shown '1.5, 2.5, 3.5' -> reads back [1.5, 2.5, 3.5]
```

**The structural cause matters more than the bug: T2's fix was `_as_text`, a
private static on the Qt tab.** `global_settings.py` could not reuse it even if
the author had remembered, so the only available path was to write `str(value)`
again. **A fix that is not extractable gets re-broken by the next file.** Move it
to `field_spec.as_text()` (Qt-free) and have both call it.

**C3b — the restart-coercion fix landed on the `str` branch only.**
`global_settings.py:50` guards `isinstance(stored, str)`, but QSettings hands a
multi-entry list back as a **list of str**:

```
ini: emission_coefficients=1.5, 2.5, 3.5
SAME PROCESS : [1.5, 2.5, 3.5]   floats
FRESH PROCESS: ['1.5','2.5','3.5']  strings -> enter layer (a), the highest
```

Destination is arithmetic (`nr_reduction_calc.py:444`). This is the same blind
spot as the commit's own honest survivor, one type over — the insight was found
and then not generalised. Coerce per element whenever `field.is_list`.

---

## C4 (BLOCKING) — layer (a) outranks "set for this run", the experiment file, and the measurement

`settings_resolver.py:174-175` walks `("a", global_settings)` before
`("b", ui_overrides)`. Verified:

```
global(a)=0.9  this-run override(b)=0.25          -> winner 0.9  layer 'a'
global(a)=0.9  experiment file(c)=0.31            -> winner 0.9  layer 'a'
global(a) IncidentTheta=4.0 vs measured(e)=0.6    -> winner 4.0  layer 'a'
```

An override that is overridden is not an override. Every other layer is ordered
specific-wins. And `GLOBAL_WHITELIST` includes the **instrument-truth geometry**
set — `IncidentTheta`, `mmpix`, `dSampDet`, `dMod`, `xi_ref`, `dS1Samp`, `nx`,
`ny` — whose documented defaults read *"Unset reads it from the instrument
settings"* / *"Unset reads the PV"*. Those are the instrument's answer, not a
person's preference, and a stored QSettings key silently beats the measurement.

**Consequence: identical visible UI plus an identical experiment settings file can
produce different reduced data.** This is a scientific-correctness decision, not a
code style one — it wants the human's judgment on where (a) belongs, and the
answer may be "below (c), or excluded from the geometry group entirely".

---

## C5 (BLOCKING) — discovery: an unreported survivor, an inert layer, and a wrong rule

**C5a — the amendment-16 record has an unreported second survivor.** The bullet
*"discovery's try-guard removed"* covers **two** distinct guards in
`discover_ipts_settings`, and only one reds. Deleting the mount `OSError` guard
(`settings_resolver.py:247-253`) so `OSError(116, "Stale file handle")` propagates:
**all 42 tests still pass.** That is the guard the module docstring foregrounds
(*"a resolver that raised when the mount was unavailable would take the launcher
with it"*). The enumerated list also yields 12 mutations, not 13, unless that
bullet counts as two — which is the reading where one is an unreported green.
**Split the bullet, add the test, amend the commit body with both observed
failures.** The rest of the record is accurate on 12 of 13 and the survivor's
`bool('false')` account is correct — I reproduced it independently.

**C5b — layer (d) is inert.** `settings_resolver.py:281` hardcodes
`ctx.xml_settings = {}`; the template is never parsed. So the advertised six-layer
taxonomy is five layers plus a filename, while `LAYER_LABELS`, the badge and the
docstring all present (d) as live. `test_discovery_arms_the_template_layer`
asserts only `xml_detail` and passes unchanged if layer (d) is deleted. Either
populate it (the repo has `reduction_template_reader` and seven real
`template*.xml` fixtures) or demote it in the docstring, the badge and the test
name.

**C5c — the template up/down rule is a second, *wrong* copy.**
`settings_resolver.py:279` takes `sorted(glob("template*.xml"))[0]` — alphabetical,
so `template_down.xml` **always** wins:

```
tthd=+1.0  json_detail=reduce_settings_up.json   xml_detail=template_down.xml   <- wrong
```

`template.py:79 get_default_template_file(output_dir, tthd)` already implements
this, is used by both autoreduce entry points, and has its own test. The commit
body's principle — *"reuses the autoreduction's own helper rather than a second
copy of the rule"* — is true for the settings helper and false for this one,
undisclosed. No test catches it because **no fixture tree contains both
templates.**

**C5d — "degrades, never raises" is false in two more ways.** `ImportError` from
the lazy `lr_autoreduce` import is not in the except list, so a Mantid-free
launcher — the environment the lazy import exists to serve — gets
`ModuleNotFoundError` out of discovery. And a deeply-nested JSON raises
`RecursionError`. Add both (or `except Exception` with the reason recorded) and a
size cap on `_read_json`. Note also: the import costs **2.58 s and pulls Mantid,
including a network `CheckMantidVersion` call**, synchronously — extract the
twenty lines of pathlib as the commit itself suggests.

---

## C6 (BLOCKING) — two headline properties are unguarded, one test cannot fail

**C6a — the whitelist's derivation is unguarded.** Replacing it with a hand-list
of four names → **42 passed**. The commit's claim is *"derived from FIELD_SPEC by
group, not a hand-list — so a new field is covered without anyone remembering"*;
that is exactly the property with no guard, because every consumer test reads the
same constant. Assert **per-group exemplars** (each group in `GLOBAL_GROUPS`
contributes at least one named field), which reds on both a hand-list and a
dropped group.

**C6b — `test_discovery_missing_mount` cannot fail for its stated reason.** Its
only semantic assertion is satisfied by the IPTS number appearing inside the
*path*. Replacing the status with `"loaded every layer successfully from …"` →
**42 passed**. Assert the outcome (`json_settings == {} and xml_settings == {}`)
plus a status assertion naming the condition. Combined with C5a, the entire
"mount unavailable" domain — the module's stated reason to exist — is unpinned.

---

## C7 (BLOCKING) — no deep copy anywhere; the frozen record is mutable

There is no `copy` import in `settings_resolver.py`. Verified: the resolved
document, the layer dict, and the *frozen* `Resolved.value` are one object, and
mutating the resolved doc rewrote the source document. Layer (f) is safe only
because `Field.default_value()` already copies — the guard T2 built **for this
consumer**, whose docstring says *"a resolution stack starts from defaults, so the
first such caller is likely rather than hypothetical"*. T3 is that caller. Deep-copy
at the layer boundary in `resolve()`, and treat `Resolved.value` as a copy.

---

## Should-fix (from all four domains)

- **Precedence is declared in three places and the declaration is inert.** `LAYERS`
  (`:46`) has **zero consumers**; order lives in the literal tuple sequence inside
  `resolve()` plus two hardcoded fall-throughs plus `user_chosen()`'s `("a","b")`.
  Reversing `LAYERS` changes nothing and reds only its own tautological pin. Layer
  (g) costs five edits, three silently optional. Drive `resolve()` from one ordered
  table.
- **The whitelist is enforced on the writers, never on the reader**, and the
  `ResolutionContext` constructor is an unguarded third door — verified:
  `ResolutionContext(global_settings={"Sname": "../escape"})` resolves. Filter in
  `resolve()`, where it cannot be bypassed.
- **`ipts` is joined into the `/SNS` root unvalidated** — an absolute component
  replaces the base (verified: layer (c) read from outside the root). Confine with
  `resolve()` + `is_relative_to`.
- **The layer-(a) dialog validates nothing**: `qmax='abc'`, `nx='1e9'`,
  `dead_time=-5.0` all persist and outrank everything. `Field.check()` already
  produces every message; the dialog never calls it. No validator on the editors
  either, unlike its sibling.
- **`save_resolution` routes around T2's symlink refusal** and is a second copy of
  `SettingsDocument.save`'s body that has **already drifted**. Extract one
  `atomic_write_json`.
- **`load_resolution` crashes on a malformed provenance block** (`TypeError`,
  `AttributeError` verified).
- **One dialog + 77 widgets leak per menu invocation** (5 invocations → 5 live
  dialogs, 768 child widgets). `deleteLater()` in a `finally`.
- **`accept()` catches one exception type**; anything else aborts the launcher
  (demonstrated exit 134 with an injected raiser). Use `@guarded`, as its sibling does.
- **Out-of-set combo: shown blank, held elsewhere, and Save deletes it.** Reuse
  `_show_in_combo`, which already solves this.
- **`resolve_all` never calls `validate()`** — a headless consumer gets an
  unvalidated document silently. T2's path guards *do* still fire on layer values
  (verified); nothing invokes them.
- **`changed_vs_seed()` reports resolved layers as user edits** (2 fields on a
  freshly resolved document) — the `reseed()` gap, now load-bearing.
- **`None` in a layer is treated as absent**, so no layer can unset a lower one —
  but for `LambdaMin`/`LambdaMax`, `None` means "derive from the choppers" and is a
  valid configuration. Needs an `UNSET` sentinel.
- **Deriving the whitelist by group auto-widens the top layer** — and is the
  mechanism by which the `sympify` sink would become reachable if
  `wavelength_resolution_function` were ever added to `FIELD_SPEC`, since it would
  land naturally in one of exactly those groups. A type gate
  (`f.type != "path" and (f.type != "str" or f.allowed)`) is **behaviour-preserving
  today, 29 → 29 verified**.
- No timeout on any mount access; unknown keys in a real settings file are silently
  dropped with no status note; `LAYERS`/`test_layer_order_is_the_declared_one`
  tautology; the restart test never calls the production loader; four one-line
  per-pair precedence tests would name the boundary instead of "the precedence test".

## Confirmed sound — do not rework

- **No resolved value can reach `sympify`, a Mantid `Formula=`, or a subprocess** —
  traced end-to-end with four independent breaks. `wavelength_resolution_function`
  is not in `FIELD_SPEC`, layer (d) never parses XML, layer (c) carries the key but
  never installs it, and the seven-key sink is numbers-only. No new
  `eval`/`exec`/`pickle`/`yaml`/subprocess sink in 1237 lines; no secrets.
- **The declared active-row trap is genuinely absent** — mutating `_on_cell_changed`
  to prefer `currentRow()` reds exactly its named test.
- **Qt-free is verified at the honest level** — the subprocess test is correctly
  constructed and could not be defeated.
- **The provenance round trip through a real file is the strongest part of the
  suite**, and the atomicity guard is real (an in-place `open(path,"w")` reds the
  named test).
- **The amendment-16 record is accurate on 12 of 13**, and the survivor's
  `bool('false')` account is correct and independently reproduced. Reporting that
  survivor honestly rather than tuning the test is the best thing in this commit —
  the gap is that the same rigour was not applied to the second guard hiding inside
  one bullet.
- Extra keys from a layer are inert by construction; `source_detail` is
  basename-only; T2's `no_separators`/`_path_problem` guards still fire on
  layer-supplied values; the enumerated-key QSettings discipline is clean.
