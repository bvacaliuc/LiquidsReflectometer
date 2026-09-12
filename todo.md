# Integrator: `settings-management` (T3) v2 — REJECTED. Attempt 2 of N=3.

**Gate is GREEN** at `325ae1a`: 170 launcher + 292 reduction, `EXIT=0`. Every
finding is invisible to it.

**Both blocking domains blocked** (design 3, ui-aspects 5); `test-reviewer` found
6 more; `security-review` raised 1 should-block. Many overlap — consolidated into
**11 clusters** below, with the overlaps merged and each finding attributed.

**v2 is a large, genuine advance.** The confirmed-fixed list at the bottom is long
and includes four of six v1 blockers plus the whole production refactor. Read it
before reworking anything.

**Start with C1: it is a live defect, not a test gap.** Then read "one fixture
tree" — a single realistic tree kills five of these clusters at once.

---

## C1 (BLOCKING) — discovery raises where its headline promises it degrades
*design BLOCK-1 · test A1/A2 — found independently, and proven with a real
filesystem injection rather than a monkeypatch.*

`settings_resolver.py:417` is the one stat site in the function with **no guard**,
while the identical template call 18 lines later is wrapped:

```python
settings_path = select_by_geometry(directory, "reduce_settings", ".json", tthd)  # :417 bare
try:                                                                             # :434 guarded
    template_path = select_by_geometry(directory, "template", ".xml", tthd)
except OSError as exc:
```

Proven with `chmod 000` on an IPTS share — an ordinary facility condition, no
patching:

```
is_dir() still True: True
  settings_resolver.py:417 -> autoreduce_paths.py:35  if variant.exists():
PermissionError: [Errno 13] Permission denied: '.../reduce_settings_up.json'
```

`is_dir()` succeeds, so the *tested* guard at `:404` never fires. Observed in the
shipped launcher: `@guarded` catches it, so no crash — but **provenance is not
populated, no `discovery_status` is recorded, and the panel says "The settings in
this tab are unchanged"** while layers (a), (e) and (f) were all available and none
was walked. The degradation the module exists to provide is not provided.

**Two sibling guards also survive deletion** (test A2): the `resolve()` guard
(`:391-395`) and the template-scan guard (`:434-441`) — both raise `[Errno 5]` when
removed, suite green. The test at `test_settings_resolver.py:566` monkeypatches
`Path.is_dir` **only**, which is exactly the one guard the author meant to
demonstrate.

**Fix:** push the guard into `select_by_geometry`, or wrap `:417` like `:434`; then
inject `OSError` at all three sites, not one.

---

## C2 (BLOCKING) — the precedence decision is declared five times; three say the pre-decision order, one of them to the scientist
*design BLOCK-2.*

Applied once, correctly — `LAYER_ORDER = ("b","c","d","a","e","f")` drives the walk
and I verified `b→c→d→a→e→f`. But:

| site | says | correct? |
|---|---|---|
| `settings_resolver.py:5-16` | "six layers **in preference order**", tabulated `a…f` | **wrong** |
| `LAYER_ORDER` `:64` | `b,c,d,a,e,f` | authoritative |
| `global_settings.py:96-99` **UI label** | preferences apply "unless a run, an experiment settings file, or **the data itself** provides a value" | **wrong — (a) beats (e)** |
| `global_settings.py:141` | would "outrank every **experiment file**" | **wrong — (c) beats (a)** |
| `global_settings.py:180-182` | outranks a guess and the default | correct |

**The UI label is the serious one**: it tells a scientist the measurement will
override their stored `qmax`, and for all 20 whitelisted fields it will not. The
C4 fix landed in the constant and not in the prose a human reads. Your own
standard, `:52-53`: *"a declaration that its implementation ignores is worse than
no declaration, because it is believed."*

Also **`LAYER_ORDER` is one-third inert** — `_layer_sources` filters to the four
mapping layers, so the (e)/(f) positions are decorative: declaring (e) first
changes nothing, deleting (e)/(f) changes nothing. Either drive them from the
tuple or say the tuple covers the mapping layers only.

---

## C3 (BLOCKING) — the Save button silently discards input the scientist typed
*design SF-1 · ui BL-3 · security BLOCK — three domains.*

The wiring swapped `document.save(path)` for `save_resolution(...)`, which writes
`normalize()`. `SettingsDocument.save`'s docstring states the opposite policy
verbatim: *"The whole document, **not** `normalize()`: this is the scientist's file
and round-tripping it must not quietly drop fields."* The inline comment at
`settings_editor.py:573` asserts it writes the file "unchanged". Measured:

```
lost by the new Save path: RBnum, LambdaMinUse, LambdaMaxUse   (all runtime_owned=True)
reload: rows still 2 (DBname carries the length), Run numbers column EMPTY
```

**Severity, stated precisely.** These are runtime-owned, so the reduction supplies
them and the *scientific* consequence is nil. But `RBnum` is `per_angle`, sits in
`PER_ANGLE_NAMES`, gets an **editable table column**, and the editor has **no
`runtime_owned` handling at all** — so a scientist can type run numbers into a
column whose own help says "Supplied by the reduction run, not authored here", and
Save discards them with no message. That is reachable loss of typed input, newly
introduced by this diff. The deeper invitation (an editable column for a
runtime-owned field) is pre-existing — flagged in T2 v1 and never fixed.

**Fix:** have `save_resolution` write `make_json_safe(document.to_dict())`, or keep
`document.save(path)` in the slot and write the sidecar beside it. Then pick **one**
policy and state it in one place. Pin it: write a JSON containing every
`RUNTIME_OWNED_NAMES`, Load, Save, assert `set(out) == set(in)`.

---

## C4 (BLOCKING) — the list-coercion defect is unfixed verbatim, and now reaches a written settings file
*ui BL-1.*

`global_settings.py:50` is untouched from v1:

```python
values[name] = fs.get(name).coerce(stored) if isinstance(stored, str) else stored
```

QSettings hands a multi-entry value back as a **list of str**, which takes the
`else` branch. Measured through the real Resolve and Save buttons:

```
fresh process: dead_time ['4.2','9.9']   qmin ['0.001','0.25']
resolve(): dead_time layer=a label='user preference'
panel: "Dead time (us): expected a number, got list ['4.2','9.9']"
WRITTEN FILE: dead_time = ['4.2','9.9']     warnings: []
json_to_config accepted it -> the reduction does arithmetic on strings
```

**Two defects compounding**: the coercion gap, and `save_settings` writing a
document its own panel calls invalid, with no warning.

The commit's defence — "no whitelisted field is list-typed today" — is true but
`_may_be_a_preference` (`:120-144`) is built to **auto-include** any new field in
six groups and does not exclude `is_list`. The guard is hollow:
`test_global_settings.py:81-98` monkeypatches `QSettings.value` to return a **str**,
i.e. only the branch that already worked.

**Fix:** coerce unconditionally (per element for list fields), and gate
`save_settings` on `document.validate()`.

---

## C5 (BLOCKING) — provenance lies for per-angle fields after add/remove
*ui BL-2 · test A5.*

The commit states: *"every mutator re-records `[b]` and re-badges, **including
angle add/remove**."* **That is false** — `add_angle` (`:365-372`) and
`remove_selected_angle` (`:374-386`) call `refresh_badges()` and never
`_record_edit`, so they re-**draw** stale provenance:

```
after Add angle: col header 'Direct-beam file [c]'  tip names reduce_settings_up.json
document DBname = ['db_a.dat','db_b.dat',None]   the named file holds ['db_a.dat','db_b.dat']
after Save: sidecar DBname -> {'source_layer':'c','source_detail':'reduce_settings_up.json'}
```

Deleting either `refresh_badges()` call leaves the suite green, and
`_on_angle_cell_changed` / `_set_scalar` lose `_record_edit` green too (test A5:
two of three sites, plus both re-badges, survive). The test named for it —
`test_removing_an_angle_redraws_the_column_attributions:376` — asserts the header
**before** the removal and only the document after. `add_angle`'s re-badge has no
test at all.

**Fix:** `_record_edit` every `PER_ANGLE_NAMES` entry on add/remove, or drop the
column badge to `[b]`/blank. Assert the header **after** each mutation.

---

## C6 (BLOCKING) — an untouched open+Save *deletes* an out-of-set preference
*ui BL-5.*

`global_settings.py:143-150` uses `setCurrentText` on a non-editable combo, a
no-op for unknown text, leaving the blank entry:

```
stored before: {'DetResFn': 'bogus_from_an_older_version', 'peak_type': 'gauss4'}
combos show '' ; accept() warnings: []
stored after untouched Save: {}
```

Blank → `coerce("") → None` → `settings.remove(name)`. A stored preference is
destroyed with no message and the field reverts to the built-in default — i.e.
different reduced data. **The fix exists one file over**, with a docstring
describing this exact failure: `SettingsEditorTab._show_in_combo`
(`settings_editor.py:294-308`). C3 extracted the *renderer* to end this recurrence
class and left the *combo* case duplicated and divergent.

---

## C7 (BLOCKING) — discovery does unbounded-time `/SNS` I/O on the GUI thread
*ui BL-4 · security.*

`settings_editor.py:525` calls `discover_ipts_settings` synchronously in the slot,
with the default hardcoded `root="/SNS/REF_L"` and no way to redirect it from the
GUI. Measured with a 2 s stub through the real button:

```
click blocked the thread for 2.00s; QTimer ticks delivered during it: 0
```

No busy cursor, no disabled button, no cancel, no timeout anywhere in the chain. A
stalled FUSE/sshfs mount blocks in D-state — it does **not** raise, so both the
`except OSError` guards and `@guarded` are irrelevant. This is the first commit in
which a button press touches `/SNS`.

Credit: it is bounded in **breadth** — `select_by_geometry` does exactly two
`exists()` probes per stem, no glob, no walk, and the read is capped at 4 MB.
Retiring `sorted(glob(...))` removed the enumeration amplification as a side
effect. The open axis is **time**.

**Fix:** worker thread with the button disabled and a status line, or the
SIGALRM/thread deadline from `setup/patterns/network-mounts.md`. Minimum: busy
cursor + `setEnabled(False)`, and narrow the docstring promise to "never raises"
so the residual is declared.

---

## C8 (BLOCKING) — the provenance sidecar is write-only in production
*design BLOCK-3 · security LOW.*

`load_resolution` and `user_chosen` have **zero non-test callers**. The editor's
Load path is `SettingsDocument.from_file`, which knows nothing about the sidecar:

```
Resolve -> Save writes reduce_settings.provenance.json
reopening the same file: badges blank, provenance entries 0
```

So v2 ships a persisted round trip that is tested end-to-end and wired on the
**write side only** — Save deposits a file into `shared/autoreduce` that nothing in
the repo ever reads. This is v1's rejection sentence at smaller scope; it is ~3
lines in `load_settings`. Credit: badges are at least *honest* (blank) after a
Load rather than stale.

Related: **layer (b) also has no production writer.** `ui_overrides` is never
populated — `resolve_for_experiment` fills (a) and (c) and then replaces the
document wholesale, so edits typed before pressing Resolve are **discarded rather
than ranked first**, with no confirmation, even though the taxonomy puts (b) at the
top. `_record_edit` writes (b) as a *label* after the fact; nothing writes it as a
*layer input*. Layer (d) was demoted honestly with `DISCOVERY_LAYERS` and a test —
apply the same standard to (b) and the sidecar read, or wire them.

---

## C9 (BLOCKING) — the whitelist derivation is still a tautology above six names
*test A4.*

| mutation | verdict |
|---|---|
| hand-list of 4 (v1's) | KILLED ✓ |
| **hand-list of 6 — one exemplar per group** | **SURVIVED** (real size is 20) |
| drop the `type == "path"` clause | **SURVIVED** |
| drop the free-text clause | **SURVIVED** |
| drop the `runtime_owned` clause | **SURVIVED** |

`test_the_whitelist_is_derived_not_hand_listed:538` asserts one exemplar per group,
so a regression dropping **14 of 20** preference fields is green — and
`test_the_dialog_offers_exactly_the_whitelist` cannot help, because the dialog is
*built from* the constant. Three of the derivation's five clauses are unpinned.

**Fix:** pin by membership — assert the full derived tuple, or assert each clause
with a counter-example field (`Sname` for free text, a `path` field, a
`runtime_owned` field).

---

## C10 (BLOCKING) — the up/down fix is reinstatable, and the new `tthd` field is never proven to reach discovery
*test A3 · A6.*

Restoring `sorted(glob("template*.xml"))[0]` at `:435` — **the exact v1 B3
defect** — **survives, 377 green**, because `test_settings_resolver.py:343` writes
only `template_up.xml`. A one-template tree cannot distinguish the shared primitive
from the alphabetical copy. (The settings-stem site is killed only by the
`tthd-positive` param; `tthd-negative` passed under sorted-glob because
`reduce_settings_down.json` sorts first — a single-geometry pass would have read as
coverage.)

And hardcoding `discover_ipts_settings(ipts, tthd=1.0)` at `settings_editor.py:531`
— ignoring the UI field entirely — **survives**. `_experiment_tree(..., tthd_up=False)`
is a **dead parameter**: the only call site never passes `False`. A scientist typing
`tthd=-1` would silently resolve from the **up** file — the same silent-wrong-geometry
class that got v1 rejected, now reached through the UI.

Related: `tthd == 0` is unpinned (`tthd > 0` → `>=` survives, flipping 0 to *up*),
and an unparseable/empty `tthd` silently defaults to `1.0`.

---

## C11 (BLOCKING) — the extracted renderer carries the original defect for the nested type
*ui should-fix 1, raised to blocking here because it is the mechanism C3 was
extracted to end.*

```
render_value([[10, 20], [30, 40]])  ->  '[10, 20], [30, 40]'
BkgROI.coerce(that)                 ->  [['[10'], ['20]'], ['[30'], ['40]']]
round-trips: False
```

`field_spec.py:202-214` and `:356-368` both claim `render_value` is the inverse of
`coerce`. It is, for every type except `list[list[int]]` — and the guard
(`test_the_shared_renderer_round_trips_a_list:369`) pins **flat** `list[float]`
only. Unreachable today because the tab uses the element path, but the entire point
of extraction is that anyone may call it: C3's fix made the function importable so
the next file inherits it, and what it inherits is wrong for the nested case.

**Fix:** `assert f.coerce(fs.render_value(v)) == v` over every `FIELD_SPEC` type.
Also delete `Field.render` (`:202`) — zero callers, zero tests, an untested second
door onto `render_value`, which is the two-copies shape C3 exists to close.

---

## Should-fix

- **[HIGH, security] `Field.check` accepts `0`, `inf` and `NaN`.** `value < minimum`
  is False for `NaN`, and `minimum=0.0` admits `0` and `+inf`; there is no
  `isfinite`. All three persist through the dialog's new gate into layer (a), which
  is the cross-experiment layer. Blast radius at `nr_tools.log_qvector:74-75`:
  `dqbin=0` or `qmax=inf` → `OverflowError`; `dqbin=1e-12` → a **49.7 TB**
  `np.arange`; `dqbin=nan` → NaN propagates into the q-vector **silently**. The
  docstring at `global_settings.py:179-181` claims this is closed — `'abc'` and
  `-5.0` are genuinely refused; `0`/`inf`/`NaN` are not. Reject non-finite, and give
  strictly-positive fields an exclusive minimum.
- **`_read_json` reads *through* a symlink while `atomic_write_json` refuses to
  write through one.** The `is_relative_to` confinement validates the *directory*;
  `_read_json` then `open()`s a path that may be a link out of the root. Confirmed:
  layer (c) read from outside the root, **and the badge asserts "experiment settings
  file (reduce_settings.json)" for bytes that came from elsewhere** — B5's class in
  the module whose purpose is truthful provenance. Use `lstat` + `O_NOFOLLOW`.
- **Type confusion in `_read_json`**: size is validated, type is not. A settings
  JSON whose top level is a string/list/number makes `resolve()`'s `if name not in
  mapping` a substring test → `TypeError` out of `resolve_all`. Add
  `isinstance(payload, dict)`. Same family: NUL in the IPTS and a symlink-loop root
  both raise uncaught, and `root_path = Path(root).resolve()` at `:390` sits
  **outside** the try that documents the mount guard.
- **`load_resolution` raises on every malformed sidecar** and has no size cap (both
  `json.load`s are plain). Latent — zero production callers — but route through
  `_read_json` and tolerate an ill-typed record.
- **`save_resolution` is not atomic as a pair** — settings first, sidecar second.
  Confirmed: with the sidecar path a symlink the user is told "Could not save
  settings" while the settings file *was* replaced, leaving a sidecar describing the
  previous contents. Write the sidecar first.
- **The discovery status is erased by the first edit** — it is prepended to the
  volatile report, so after a failed mount one keystroke leaves an all-defaults
  editor with no on-screen trace. Give it its own persistent label.
- **A failed resolve reports success**: the headline says "Resolved IPTS-…" when
  nothing was found, and `set_document` overwrites a document that may hold unsaved
  edits with no confirmation and no `changed_vs_seed()` check.
- **Every Save writes a sidecar, including `{}`** from a never-resolved tab. Not an
  autoreduction hazard (confirmed: no enumerator picks it up), but it litters a
  facility directory.
- **`select_by_geometry`'s `None` case is untested in production autoreduce** —
  deleting the `raise ValueError` at `new_reduce_REF_L.py:110-111` survives. The
  template caller's `None` *is* pinned. While there: `:141`'s `if` / `:149`'s `elif`
  means the logged fallback *"No setting config file found, looking for template."*
  never looks for a template. Pre-existing.
- **`filename conventions are still duplicated**: `("reduce_settings", ".json")`
  appears at `new_reduce_REF_L.py:108` **and** `settings_resolver.py:417`;
  `("template", ".xml")` at `template.py:87` **and** `:435`. The rule is shared; the
  names most likely to change are not. Add `settings_file(dir, tthd)` /
  `template_file(dir, tthd)` wrappers.
- `Resolved.value` is dead weight in the sidecar (`as_record()` drops it, badges
  read only the layer); `{name: (layer, detail)}` is the honest type. And the
  55-vs-52 key asymmetry the fix is named after reappears between sidecar and
  settings.
- `settings_resolver.py` is 513 lines with five responsibilities; the split points
  are clean when convenient.

---

## One fixture tree kills five of these

*test-reviewer's action item, and the highest-leverage single change here.* Every
discovery tree is still shaped to the assertion it serves: **none holds both
templates, none holds both a JSON and an XML, none holds an unreadable file, and
the "unreachable mount" is a `Path.is_dir` shim rather than a mount.** Per
`setup/patterns/failure-injection-testing.md`, a shim on one detection call
validates your model of that call and nothing adjacent — which is mechanically why
C1's siblings and C10 survive.

One realistic tree — `reduce_settings_up.json` + `reduce_settings_down.json` +
`template_up.xml` + `template_down.xml` + one `chmod 000` file, parametrized on
`tthd ∈ {+1, 0, -1}` — **kills C1's injection gap, C10's both halves, the
`tthd == 0` case, and the two-note status path at once**, and is cheaper than the
five single-purpose trees it replaces.

---

## Amendment 16: the count reconciles, the granularity does not

v1's defect was arithmetic — the bullet list yielded 12 against a claimed 13. **That
is fixed**: the list yields 16 and the test counts confirm. But **four of the
sixteen bullets name a *behaviour* and demonstrate *one of its sites*** (C1's three
guards as "the mount guard"; C10's two call sites as "the sorted-glob up/down";
C5's five sites as "edits not recorded"; C9's five clauses as "the whitelist").

**The rule this adds, and it belongs in the amendment:** *when a bullet names a
behaviour with more than one implementation site, mutate every site and list each
verdict separately.* v1's lesson was that a count must reconcile; v2's is that **a
reconciling count can still hide a survivor behind a plural noun.**

---

## Confirmed FIXED — do not rework

- **The production autoreduce refactor is behaviour-identical.** A 1536-case
  differential (16 `tthd` values including `±0.0`, `±inf`, `NaN`, bools; all 8
  subsets of `{_up,_down,unsuffixed}`; 6 filesystem modes including dangling
  symlink and mode-000) found **0 mismatches**. The `tthd > 0` boundary, the
  variant-then-fallback order, the raise and its message are all preserved. One
  primitive, three callers.
- **B1 (whitelist reader-side), B2 (`ipts` confinement), B5 (`set_resolution`
  removed), B6 (symlink refusal restored via `atomic_write_json`), B7 (the
  `_provenance` sidecar split) are all confirmed fixed** — B7 and B2 being the two
  security said it would block on. `json_to_config(json.load(written))` succeeds; no
  enumerator in the tree can pick up the sidecar.
- **No resolved value reaches `sympify`, a Mantid `Formula=`, or a subprocess** —
  traced to the sink twice, by two independent arguments. Demoting layer (d) has a
  security dividend: no XML parser was introduced, so no XXE/billion-laughs surface.
- **The wiring is real and well tested** — the production-path test drives the real
  button with a redirected `root=` (a seam, not a mock) and reds when the wiring or
  the global layer is removed.
- **Layer (d) is honestly demoted** — `DISCOVERY_LAYERS`, both docstrings, the
  status text and the test name all agree it is reported-not-parsed.
- **The 4 MB cap, the `RecursionError` catch, the deep-copy boundary, `reseed`, the
  pre-equalise provenance snapshot, the path confinement, the geometry exclusion,
  the reader-side whitelist, optional-list nulls, `HUMAN_LAYERS`, the
  sidecar-missing branch, badge labels, and the slot guard are each killed by the
  test that names them.** Mantid is **not** imported by the resolver.
- **The geometry exclusion has a concrete mechanism** worth keeping in the guard:
  `apply_config_overrides` (`nr_reduction_calc.py:1151-1163`) overrides instrument
  settings from exactly the seven fields `GLOBAL_EXCLUDED_GROUPS` removes — so
  without the exclusion a stored preference would have overwritten a *measured*
  instrument value at that line.
- Active-row trap absent; sorting pinned with its reasoning comment; no
  `.destroy()`; no double-connects; dialog leak fixed; `accept()` guarded;
  validators attached.

## Integrator corrections to my own briefs

- I told the security reviewer the type gate was "behaviour-preserving today,
  29 → 29 verified". The tree gives **20 → 20** — 29 predates
  `GLOBAL_EXCLUDED_GROUPS`. The property holds; my number was stale. It flagged
  this rather than substituting silently.
- I asked the design reviewer what "layer (g)" costs. There is no layer (g); I meant
  a hypothetical seventh layer and phrased it as if it existed.
- My reviewer brief contained a conflict — "leave your sandbox in place" versus
  leaving no repo state — which `git worktree add` makes unsatisfiable. One reviewer
  surfaced it instead of silently choosing. Future briefs will specify
  `git clone --shared --no-tags` instead of a worktree.
