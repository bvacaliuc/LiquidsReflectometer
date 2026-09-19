# Plan: settings-management (T3)

**Campaign:** `exp-settings-roi` · base `exp` @ `6da473d` (T2 merged, PR#28) ·
charter §4 slug T3 · full design in
`tasking/plan/settings-management/plan.md` (398 ln) — **authoritative source
is `src/lr_reduction/{settings_document,field_spec,reduction_domains}.py` in
the checkout, NOT the design doc** (out-of-tree; the doc is human background)
**Retry attempt:** 6 (bounded, amendment 20 footing, 2026-09-19) — see Revision
history; the v6 source branch is the existing `feature/settings-management` @
`8c7dfbb` with the v5 Integrator todo on top

Review domains (design-plan §10): **design-reviewer (blocking** — the layer
model vs. the organic tangle this slug replaces), **ui-aspects-reviewer
(blocking** — menu/dialog lifecycle, provenance-badge rendering, and the
**active-row trap in the per-run tables** — the campaign's signature widget
bug, present again here), test-reviewer (fixture-tree realism),
security-review (advisory — the global whitelist, read-only `/SNS` scans,
and path fields).

## Symptom / the ask (human, 2026-07-17)

Reduction settings resolve from a muddle of sources with no defined
precedence or provenance (B1). T3 gives that a **layer taxonomy with a
single resolver**: for each field, resolve in preference order **(a)**
user-global → **(b)** pre-run UI override → **(c)** IPTS
`reduce_settings*.json` → **(d)** IPTS `template*.xml` → **(e)** guessed from
the dataset → **(f)** built-in default; every resolved value carries an
auditable origin (NFR-8: silent resolution is how the muddle happened).

## Verified state (against `agentic/exp` @ `6da473d`, 2026-09-10)

- **Clean landing:** `src/lr_reduction/settings_resolver.py` absent
  (resolved home, design §5.4 — Qt-free so scripts/tests import it without a
  GUI-package dependency).
- **T2 interface present** (this slug builds on it):
  `SettingsDocument` (`settings_document.py:45`) with `config` (`:108`),
  `to_dict` (`:119`), `normalize` (`:292`), and **`overrides()`** (`:354`,
  non-default values only — the method a resolution layer needs);
  `field_spec.py` (FIELD_SPEC) and `reduction_domains.py` present. Read
  these in the checkout for the field set and domains — do not re-enumerate.
- **Identity store:** `launcher/app_identity.py` (`ensure_identity`,
  `ORG_NAME`/`APP_NAME`) — the global-settings layer (a) persists into the
  **same** QSettings store (S3 contract; all layers share one store).
- **Mount:** `/SNS/REF_L/**` is read-only and may be down (charter P-5) —
  discovery must degrade, never raise (§5.2).

## Architecture (design §5–§6 — two pieces)

1. **`SettingsResolver`** — `src/lr_reduction/settings_resolver.py`,
   **Qt-free**. Per-field `resolve(field, ctx)` walks (a)→(f) and returns
   **`Resolved(value, source_layer, source_detail)`** (e.g.
   `('c','reduce_settings_up.json')`) — never a bare value; `resolve_all(ctx)
   -> SettingsDocument` maps it over FIELD_SPEC keeping per-angle arrays
   length-consistent (FR-11). `ResolutionContext` carries IPTS id, run(s),
   discovered artifacts, user config, live tab overrides, and a **lazy**
   dataset-analysis hook (layer (e) runs only when consulted). IPTS
   discovery (§5.2): a **read-only** scan of
   `/SNS/REF_L/{ipts}/shared/autoreduce/*` arming layers (c)/(d) if
   `reduce_settings*.json`/`template*.xml` exist; up/down selection reuses
   the existing `get_default_setting_file` helper (do not reimplement).
2. **Global-settings menu/dialog (B2)** — a whitelisted subset of fields
   editable per-user, persisted to the shared QSettings store via
   `app_identity`; a menu-bar entry + dialog; the tab renders a per-field
   **provenance badge** (which layer each value came from; unset = layer (a)
   inactive). Non-whitelisted fields (e.g. `RB_Ymin`) are **rejected** from
   the global layer.

## Lessons carried from T2's cycle (do NOT repeat them)

- **No two-implementations-that-drift.** T2 was rejected three times for
  this (build vs refresh path; declared vs enforced domains). The resolver
  has ONE resolution path; the badge reads the same `Resolved` the document
  was built from — never a parallel re-derivation.
- **Qt-free seam, proven by a subprocess test.** An AST import-grep is
  defeated by a transitive import (T2 C6). Ship **one subprocess test**:
  import `settings_resolver` (+ `settings_document`), assert no Qt in
  `sys.modules`, then exercise `resolve_all`.
- **Path safety** (T2 should-fix): any resolved path field honored as a sink
  gets the same guard T2 applied — reject `..`/absolute where the field is
  base-joined; the read-only `/SNS` scan must not follow into arbitrary
  paths.
- **The active-row trap** (per-run tables render provenance per angle): row
  edits/reads use an explicit index, never `table.currentRow()`; pin it.

## Red-Green seed (model first, Qt-free — design §8; mutate-once per guard, amendment 16)

Pure model (`tests/test_settings_resolver.py`, no Qt) — each guard names the
mutation that must red it:

- `test_per_field_fallthrough`: absent in (a)–(d) → (e) stub; absent
  everywhere → (f). Mutate: skip the (e) probe → the (e) case reds.
- `test_precedence_order_abcdef`: one field in every layer → value AND
  provenance are (a)'s; peel layers off one at a time. Mutate: swap two
  layers' order → the provenance assertion reds (assert the **source_layer**,
  not just the value — a value can coincide across layers).
- `test_json_shadows_xml`: both armed → JSON-defined fields never from XML.
  Mutate: check (d) before (c) → reds.
- `test_updown_selection_shared_helper`: `tthd>0` → `_up.json`, matching
  `get_default_setting_file` on the same fixture tree. Mutate: invert the
  tthd test → reds.
- `test_discovery_missing_mount`: nonexistent IPTS path → empty layers +
  recorded status, **no raise**. Mutate: remove the try-guard → the test
  raises (reds).
- `test_provenance_survives_store_and_save`: store per-run → save JSON →
  reload → user-edited fields identifiable. Mutate: drop `source_layer` from
  the saved record → reds.
- `test_global_whitelist_enforced`: setting a non-whitelisted field
  (`RB_Ymin`) into `global_settings` is rejected. Mutate: bypass the
  whitelist check → reds.

GUI (pytest-qt, offscreen, the harness `no_qmessagebox`/`no_qfiledialog`):
the dialog round-trips a whitelisted field to QSettings; launcher start
loads it; a badge's text matches its `Resolved.source_layer`. Each GUI guard
names its mutation.

## Failure-mode matrix (campaign-critical; full matrix in the design doc)

| Case | Detection | Handling |
|---|---|---|
| `/SNS` mount down (common) | `test_discovery_missing_mount` | layers (c)/(d) empty + status note; resolve from (a)/(b)/(e)/(f); never raise |
| Two layers agree by value, resolver picks wrong one (subtle) | precedence test asserts `source_layer` | provenance-keyed assertions, not value-keyed |
| A resolved value has no origin (the B1 muddle) | every return is `Resolved`, never bare | provenance is structural, not optional |
| Qt import creeps into the resolver (T2 C6 class) | subprocess `sys.modules` test | Qt-free enforced by execution, not grep |
| Non-whitelisted field into the global layer | `test_global_whitelist_enforced` | whitelist rejects; the layer is a *subset* by construction |
| Active-row hidden input in the per-run provenance table | edit-row-0-while-row-2-selected test | explicit index; the trap that recurred all campaign |
| A new guard passes under mutation (vacuous — the campaign's #1 defect) | mutate-once recorded per guard (amendment 16) | commit body: `<mutation> -> N failed` for every guard |
| pixi.lock re-stamp | first line ≠ `version: 6` | amendment 14: restore, never commit |

## Acceptance criteria

- `SettingsResolver` Qt-free (subprocess test proves it); `resolve_all`
  returns a `SettingsDocument` with per-angle arrays length-consistent;
  every field value carries `Resolved(value, source_layer, source_detail)`.
- The (a)→(f) precedence + JSON-shadows-XML + missing-mount + whitelist +
  provenance-survives-save guards all present and each **red under its named
  mutation** (recorded in the commit body — amendment 16, enforced: T2's
  cycle proved selective application fails).
- Global-settings dialog round-trips a whitelisted field through the shared
  `app_identity` QSettings store; provenance badges match `source_layer`.
- `pixi run test-launcher` + `test-reduction` green; pre-commit clean; no
  `pixi.lock` change; path/active-row guards present.
- Draft PR body: deploy consequence (charter §7); non-goals (design §9 — v1
  does NOT unify autoreduce onto the resolver: that changes facility
  behavior and is a later human-gated step); consumes T2's
  `SettingsDocument`/`FIELD_SPEC`/`reduction_domains`.

## Downstream (charter DAG)

T3 **gates T1-A1** (`roi-selector`): T1 consumes the resolved settings for
its JSON output (charter §4). T1-A1 stages after T3's draft PR merges — and
per the charter §4 scope note, the run's target milestone is T1-A1, with the
A2-vs-B decision paused for the scientists' discussion.

## Revision history — v2 (after v1 blocking review; todo @ `6365df4`; attempt 2 of N=3)

Gate green (162 launcher + 265 reduction). Seven blocking clusters; most
collapse into C1. **Confirmed sound — do NOT rework:** no resolved value
reaches `sympify`/Mantid `Formula=`/subprocess (traced 4 ways); the
active-row trap is genuinely absent; the Qt-free subprocess test is honest
and undefeatable; the provenance round-trip through a real file and the
atomic-write guard are the strongest parts; the amendment-16 record is
accurate on 12/13 and the honest survivor-reporting is the best thing in
the commit. The through-line of the defects: **precondition ≠ payoff** (all
the machinery exists, nothing consumes it — C1) and **non-extractable fixes
re-break in the next file** (C3). v2 fixes by wiring + single-sourcing, with
mutate-once enforced on EVERY guard (C5a/C6 show it still wasn't).

### C1 (blocking) — WIRE the resolver; it has zero production callers

42 green tests, nothing in the shipped app calls `resolve_all`/
`discover_ipts_settings`/`save_resolution`/`SettingsResolver`; `set_resolution`
is test-only so `self.provenance` stays `{}` and every badge renders empty;
the muddle T3 was chartered to replace is untouched beside a second unreached
mechanism. **Fix (do this WITH the clusters below, or last — wiring onto
unfixed clusters makes each latent defect live):** the launcher path that
opens the settings tab for an IPTS/run runs `discover_ipts_settings` →
`resolve_all(ctx)` → `set_document(document, provenance)`; the tab's Save
routes through `save_resolution` (provenance-aware, C2a) not bare
`document.save()`. **Mutate-once:** a test that drives the production entry
point and asserts a non-empty provenance map + a populated badge — deleting
the wiring reds it (today nothing does).

### C2 (blocking) — provenance must be readable and must not self-contradict

- **C2a:** `save_resolution` writes `_provenance` at the JSON top level →
  `json_to_config` raises `AttributeError`; if written as
  `reduce_settings*.json` in `shared/autoreduce` it **stops autoreduction
  loading that experiment** (`new_reduce_REF_L.py:112-121`). Fix: sidecar
  file, OR teach the loader to skip `_provenance` — pay the "one file" claim
  on the reader side. Mutate: write `_provenance` inline → a
  `json_to_config(the-written-file)` test reds (the existing test checks the
  *document*, not the file).
- **C2b:** provenance snapshotted before `_equalise_angles` rebinds padded
  lists → two disagreeing copies (55 provenance vs 52 settings). Fix: record
  provenance AFTER equalise, and do not store `value` in `as_record()` (store
  origin only — the value lives in the document, once). Mutate: revert to the
  pre-equalise snapshot → a length-agreement test reds.
- **C2c:** the badge claims a stale layer + names a wrong file after edits
  (`set_document` renders from stale `self.provenance`). Fix structurally:
  provenance travels WITH the document — `set_document(document,
  provenance=None)`; each mutator records `Resolved(value,"b")` and re-badges;
  cover `add_angle`/`remove_selected_angle` (a removal shifts a column the
  header still attributes). Mutate: edit a field, assert its badge flips to
  `[b]` → reds if the mutator doesn't re-record.

### C3 (blocking) — T2's defects recur because its fixes were not extractable

- **C3a:** `global_settings.py:151` renders a list with `str(value)` (T2's
  bug) because T2's fix `_as_text` was a **private static on the Qt tab** —
  unreusable, so the next file re-wrote `str()`. Fix: move to
  **`field_spec.as_text()` (Qt-free)**; both the tab and the dialog call it.
  Mutate: `str(value)` in the dialog → a save/read-back round-trip test reds.
- **C3b:** restart-coercion guards only `isinstance(stored, str)`, but
  QSettings returns a multi-entry list as **list-of-str** → strings enter
  layer (a) (the top) and hit arithmetic. Fix: coerce per element whenever
  `field.is_list` (one shared coercion, not a second copy — C6-style). Mutate:
  a fresh-process load of a multi-entry global field asserts element types →
  reds on the str-branch-only guard.

### C4 (blocking) — precedence + whitelist: one clear bug + one SCIENCE decision (human)

- **C4(i) — unambiguous, fix in v2:** layer (a) is walked before (b), so a
  *this-run override* loses to a standing global — "an override that is
  overridden is not an override." **This-run (b) must beat global (a).** AND
  **single-source the order**: `LAYERS` (`:46`) is inert (reversing it changes
  nothing); drive `resolve()`, `user_chosen()`, and the fall-throughs from ONE
  ordered table so the C4(ii) decision below is a one-line change. Mutate:
  swap two rows in the table → the precedence test reds (assert `source_layer`,
  per-boundary tests, not one blanket test).
- **C4(ii) — SCIENTIFIC-CORRECTNESS DECISION, RESOLVED BY THE HUMAN 2026-09-12
  (fully science-safe option):** `GLOBAL_WHITELIST` included instrument-truth
  geometry (`IncidentTheta, mmpix, dSampDet, dMod, xi_ref, dS1Samp, nx, ny`)
  whose defaults come from the PV/measurement, so a stored global value
  silently beat the measured geometry (identical UI + experiment file →
  different reduced data). **Human decision — implement exactly this:**
  1. **Exclude the instrument-geometry group from the global whitelist
     entirely** — a user preference must never outrank a measured/PV value.
     Add the group to a `GLOBAL_GROUPS` exclusion (or drop it from the derived
     set) so those fields have **no layer (a)** and resolve
     (b)→(c)→(d)→(e)→(f) only. Keep the derive-by-group property (C6a) — the
     exclusion is itself a named, guarded rule.
  2. **Layer (a) sits BELOW the experiment file.** The resolved precedence
     order in the single-source table (C4(i)) is:
     **(b) this-run override → (c) IPTS json → (d) IPTS xml → (a) user-global
     → (e) dataset-guess → (f) default.** Rationale: this-run beats a standing
     preference (C4(i)); the experiment-specific file beats a user-general
     preference (this decision); a user's explicit preference still beats a
     heuristic guess (e) and the built-in default (f) for the non-geometry,
     non-experiment fields it covers.
  **Mutate-once for the decision:** a test that a geometry field
  (`IncidentTheta`) set in the global store does NOT win over a measured (e)
  value (asserts `source_layer` is `e`, not `a`) — reds if geometry is still
  whitelisted; and a non-geometry field defined in both (a) and (c) resolves
  to **(c)** (asserts `source_layer == 'c'`) — reds if (a) is still above (c).
  Update the design doc §4 note (which called (a)-above-(c) "unusual") to
  record that it was resolved to (a)-below-(c). This closes C4(ii); C4(i) +
  this is the complete C4 fix.

### C5 (blocking) — discovery: hidden survivor, inert layer, wrong rule, un-caught raises

- **C5a:** the amendment-16 record's "discovery try-guard removed" bullet
  covers TWO guards; deleting the mount `OSError` guard (`:247-253`) leaves 42
  green — an unreported survivor on the module's headline "never take the
  launcher down when the mount is unavailable." Split the bullet, add the
  test, amend the commit body with both observed reds.
- **C5b:** layer (d) is inert — `ctx.xml_settings = {}` hardcoded (`:281`),
  template never parsed, while badge/docstring/`LAYER_LABELS` present it live.
  Either populate it (repo has `reduction_template_reader` + seven real
  `template*.xml` fixtures) or demote (d) in docstring/badge/test-name.
- **C5c:** template up/down is a second, WRONG copy —
  `sorted(glob("template*.xml"))[0]` → `template_down.xml` always wins. Use
  `template.py get_default_template_file(output_dir, tthd)` (already used by
  both autoreduce entry points). Mutate: a fixture tree with BOTH templates +
  `tthd>0` asserts `_up` → reds on the sorted-glob (no current fixture has
  both — add one).
- **C5d:** "degrades, never raises" is false for `ImportError` (Mantid-free
  launcher — the exact env the lazy import serves) and `RecursionError`
  (nested JSON). Catch both (or `except Exception` with the reason recorded) +
  a `_read_json` size cap. And extract the ~20 pathlib lines so discovery
  does NOT pull Mantid (2.58 s + a network `CheckMantidVersion`) synchronously.

### C6 (blocking) — two headline properties unguarded, one test can't fail

- **C6a:** the whitelist's derive-from-FIELD_SPEC-by-group property is
  unguarded (a hand-list of 4 → 42 green). Assert **per-group exemplars**
  (each `GLOBAL_GROUPS` group contributes ≥1 named field) — reds on a hand-list
  and on a dropped group.
- **C6b:** `test_discovery_missing_mount` is satisfied by the IPTS number in
  the path (status → "loaded every layer" still passes). Assert the outcome
  (`json_settings == {} and xml_settings == {}`) + a status naming the
  condition. (With C5a, the whole "mount unavailable" domain is unpinned.)

### C7 (blocking) — deep-copy at the layer boundary

No `copy` import; the resolved document, layer dict, and *frozen*
`Resolved.value` are one object — mutating the resolved doc rewrote the source
(layer (f) is safe only because `Field.default_value()` copies — the guard T2
built for exactly this caller). Deep-copy at the layer boundary in `resolve()`;
treat `Resolved.value` as a copy. Mutate: mutate a resolved doc, assert the
source is unchanged → reds without the copy.

### v2 should-fix (safety-relevant not optional)

Drive precedence from the one ordered table (kills the inert `LAYERS`);
enforce the whitelist in `resolve()` (the reader) not just the writers — the
`ResolutionContext` constructor is an unguarded third door
(`global_settings={"Sname":"../escape"}` resolves); confine `ipts` join with
`is_relative_to` (an absolute component escapes the `/SNS` root); the layer-(a)
dialog must call `Field.check()` (today `qmax='abc'`, `nx='1e9'`,
`dead_time=-5.0` persist and outrank everything) + editor validators;
`@guarded` on `accept()` (one injected raiser → exit 134); `deleteLater()` in a
`finally` (5 invocations leak 5 dialogs/768 widgets); extract one
`atomic_write_json` (`save_resolution` is a drifted second copy that routes
around T2's symlink refusal); `resolve_all` calls `validate()`; the
type-gate on the whitelist derivation
(`f.type != "path" and (f.type != "str" or f.allowed)`) that keeps a future
`wavelength_resolution_function` out of the top layer (behaviour-preserving
today, 29→29); `UNSET` sentinel so a layer's `None` can mean "derive from
choppers" for `LambdaMin/Max` vs "absent"; the `reseed()` gap
(`changed_vs_seed` reports resolved layers as user edits).

### v2 acceptance (final-gate)

- The resolver is WIRED: the production settings-tab path runs discover →
  resolve_all → set_document(+provenance), Save routes through
  `save_resolution`; a test drives that path and asserts non-empty
  provenance + populated badges.
- Provenance is loader-safe (sidecar or skipped key — a written file
  round-trips `json_to_config`), length-consistent post-equalise, and travels
  with the document (no stale/wrong-file badge after edits or add/remove).
- `field_spec.as_text()` extracted and used by both files; per-element
  coercion shared; C3a/C3b round-trips green.
- C4(i) done (this-run beats global; single ordered table). **C4(ii) applied
  per the 2026-09-12 human decision**: geometry group EXCLUDED from the
  whitelist; precedence (b)→(c)→(d)→(a)→(e)→(f); both C4(ii) mutations red.
- C5a/C6a/C6b/C7 guards present and each RED under its named mutation
  (recorded in the commit body — amendment 16, EVERY guard: v1's hidden
  survivor is why); layer (d) live-or-demoted; template rule uses the shared
  helper; discovery catches ImportError/RecursionError + is Mantid-free.
- `pixi run test-launcher` + `test-reduction` green; no `pixi.lock` change.
- Draft PR body: the C4(ii) science decision as applied; non-goals (design §9)
  unchanged. **This is attempt 2 of 3.**

## Revision history — v3 (after v2 blocking review; todo @ `8abfdce`; attempt 3 of N=3 — **LAST budgeted attempt**)

Gate green (170 launcher + 292 reduction). **v2 is a large, genuine advance —
read "Confirmed FIXED" below BEFORE touching anything; do not rework it.** The
resolver is really wired (a production-path test drives the real button through
a redirected `root=` seam and reds when wiring/global-layer is removed); the
autoreduce refactor is behaviour-identical (1536-case differential, 0
mismatches); B1/B2/B5/B6/B7 fixed; layer (d) honestly demoted; C4(i)+(ii),
deep-copy, reseed, geometry exclusion, path confinement all killed by their
tests. **Eleven residue clusters remain, four through-lines:** (i) machinery
built but **half-wired** (C3 Save normalizes typed input away; C8 sidecar +
layer-(b) *read* side missing); (ii) **recurrence classes not fully closed**
(C4 list-coercion verbatim; C6 combo; C11 nested render); (iii) **guards prove
ONE site of a multi-site behaviour** (C1 three stat sites, C9 6-of-20, C10 one
template) — the amendment-16 granularity failure; (iv) **the human-read
declarations lie** (C2 UI label + docstrings state the pre-C4 order). This is
the last attempt on the retry budget — every cluster below is fully specified,
no discovery left.

### HIGHEST-LEVERAGE FIRST — one realistic fixture tree (test-reviewer)

Every v2 discovery tree is shaped to the assertion it serves — none holds both
templates, both a JSON and an XML, or an unreadable file; the "unreachable
mount" is a `Path.is_dir` shim, not a mount. **Build ONE tree and parametrize
it:** `reduce_settings_up.json` + `reduce_settings_down.json` +
`template_up.xml` + `template_down.xml` + one `chmod 000` file, over
`tthd ∈ {+1, 0, -1}`. It kills C1's injection gap, C10's both halves, the
`tthd == 0` case, and the two-note status path **at once**, and is cheaper than
the five single-purpose trees it replaces. Author this first; C1/C9/C10 guards
below hang off it.

### C1 (blocking) — guard ALL THREE discovery stat sites; prove by injection, not monkeypatch

`settings_resolver.py:417` (the `reduce_settings`/`.json` `select_by_geometry`)
is **unguarded**, while the identical template call at `:434` is wrapped in
`try/except OSError`. `is_dir()` at `:404` succeeds on a `chmod 000` share, so
the *tested* guard never fires and the module's headline degradation ("never
take the launcher down when the mount is unavailable; record `discovery_status`,
populate provenance") is silently **not delivered** — the panel says "unchanged"
while (a)/(e)/(f) were all available. **Two sibling guards also survive
deletion:** the `resolve()` guard (`:391-395`) and the template-scan guard
(`:434-441`). **Fix:** push the guard into `select_by_geometry` (one place, all
callers) OR wrap `:417` like `:434`. **Mutate-once, per SITE (three records):**
inject `OSError` (real `chmod 000`, not a `Path.is_dir` monkeypatch) at `:417`,
`:391`, and `:434` **separately** — each must red its own test AND each must
leave `discovery_status` recorded + provenance populated (degrade, not raise).

### C2 (blocking) — make the precedence prose and the UI label match `LAYER_ORDER`

`LAYER_ORDER = ("b","c","d","a","e","f")` drives the walk correctly (verified) —
but three human-read declarations state the **pre-C4-decision** order, and the
serious one is shown to a scientist:

| site | fix |
|---|---|
| `settings_resolver.py:5-16` (docstring "in preference order", `a…f`) | reorder to `b,c,d,a,e,f`; state (a) is below the experiment file |
| `global_settings.py:96-99` **UI label** — "unless a run, an experiment settings file, **or the data itself** provides a value" | **(a) does NOT yield to the data (e) for the 20 whitelisted fields** — remove "or the data itself"; say the stored preference outranks a dataset guess and the default, and yields to this-run and the experiment file |
| `global_settings.py:141` ("outrank every experiment file") | (c) beats (a) — correct to "yields to an experiment settings file" |

Also `LAYER_ORDER` is one-third inert — `_layer_sources` filters to the four
mapping layers, so (e)/(f) in the tuple are decorative. **Drive (e)/(f) from the
tuple, or state the tuple covers the mapping layers only.** Your own standard
(`:52-53`): *a declaration its implementation ignores is worse than none.*
**Mutate:** assert the UI label text names no layer above (a) that (a) actually
beats → reds on the "or the data itself" wording (a string assertion is fair
here — the label is the artifact under test).

### C3 (blocking) — Save must not silently discard typed input

The wiring routed Save through `save_resolution`, which writes `normalize()` —
but `SettingsDocument.save`'s docstring is the opposite policy verbatim ("the
whole document, **not** `normalize()`… round-tripping must not quietly drop
fields") and the comment at `settings_editor.py:573` claims it writes
"unchanged". Measured loss: `RBnum, LambdaMinUse, LambdaMaxUse` (all
`runtime_owned`); `RBnum` is `per_angle`, in `PER_ANGLE_NAMES`, gets an
**editable table column**, and the editor has **no `runtime_owned` handling** —
so a scientist types run numbers into a column whose help says "supplied by the
reduction, not authored here" and Save drops them with no message. **Fix:** have
`save_resolution` write `make_json_safe(document.to_dict())`, or keep
`document.save(path)` in the slot and write the sidecar beside it — then pick
**one** policy and state it in one place. **Mutate:** write a JSON containing
every `RUNTIME_OWNED_NAMES`, Load, Save, assert `set(out) == set(in)` → reds on
the `normalize()` path.

### C4 (blocking) — coerce unconditionally (per element for lists); the v2-plan fix was not applied

`global_settings.py` `load_global_settings` (~`:50`) is untouched from v1:
`values[name] = fs.get(name).coerce(stored) if isinstance(stored, str) else stored`.
QSettings hands a multi-entry value back as a **list of str** → `else` branch →
strings enter layer (a) (the top for its fields) and are **written to the
settings file**, where `json_to_config` accepts them and the reduction does
arithmetic on strings. The commit's defence ("no whitelisted field is list-typed
today") is hollow: the derivation predicate **`_may_be_a_preference`
(`settings_resolver.py:120`, which builds `GLOBAL_WHITELIST` at `:147` — NB the
todo mis-filed it under `global_settings.py`)** auto-includes any new field in a
`GLOBAL_GROUPS` group and does **not** exclude `is_list`; the guard
(`test_global_settings.py:81-98`) monkeypatches `QSettings.value` to return a
**str** — the one branch that already worked. **Fix:** coerce **unconditionally**,
per element when `field.is_list` (one shared coercion, not a second copy); gate
the editor's file-write (**`save_resolution`** — the path that persists the
settings file) on `document.validate()` (the dialog's `save_global_settings`
already whitelist-guards on write, but does not validate values). **Mutate:** a
fresh-process load with
`QSettings.value` returning a **list** (the real branch), assert element types
are numeric → reds on the str-branch-only guard.

### C5 (blocking) — `_record_edit` on angle add/remove (provenance lies today)

`add_angle` (`:365-372`) and `remove_selected_angle` (`:374-386`) call
`refresh_badges()` and never `_record_edit`, so they **re-draw stale
provenance** (a removed row shifts a column the header still attributes to
`reduce_settings_up.json`). `_on_angle_cell_changed`/`_set_scalar` also lose
`_record_edit` green (test A5: two of three edit sites + both re-badges survive
deletion). The named test asserts the header **before** removal only; `add_angle`
has no test. **Fix:** `_record_edit` every `PER_ANGLE_NAMES` entry on add/remove
(or drop the column badge to `[b]`/blank). **Mutate, per SITE:** delete
`_record_edit` at each of the three edit sites, and each re-badge on add/remove,
separately — assert the header/badge **after** each mutation reds.

### C6 (blocking) — extract the combo renderer; an untouched Save must not delete a preference

`global_settings.py:143-150` uses `setCurrentText` on a **non-editable** combo (a
no-op for unknown text) → an out-of-set stored value (`DetResFn:
'bogus_from_older_version'`) shows blank → `coerce("") → None →
settings.remove(name)`: an **untouched** open+Save **destroys** the stored
preference with no message, reverting to the default (different reduced data).
The fix exists one file over — `SettingsEditorTab._show_in_combo`
(`settings_editor.py:294-308`), whose docstring describes this exact failure. C3
extracted the *renderer* and left the *combo* case duplicated and divergent.
**Fix:** extract/reuse `_show_in_combo` for the dialog's combos, or never
`remove()` a field the user did not touch. **Mutate:** store an out-of-set combo
value, open+Save without touching it, assert it survives → reds on the
`setCurrentText`+blank path.

### C7 (blocking) — discovery I/O off the GUI thread

`settings_editor.py:525` calls `discover_ipts_settings` **synchronously** in the
slot, `root="/SNS/REF_L"` hardcoded, no redirect from the GUI. Measured with a
2 s stub through the real button: the thread blocked 2.00 s, 0 QTimer ticks
delivered, no busy cursor / disabled button / cancel / timeout. A stalled
FUSE/sshfs mount blocks in D-state — it does **not** raise, so `except OSError`
and `@guarded` are irrelevant. First commit in which a button press touches
`/SNS`. (Breadth is bounded — two `exists()` per stem, 4 MB cap; the open axis is
**time**.) **Fix:** worker thread with the button disabled + a status line, or
the SIGALRM/thread deadline from `setup/patterns/network-mounts.md`. Minimum:
busy cursor + `setEnabled(False)`, and narrow the docstring promise to "never
raises" (declare the residual). **Mutate:** a discovery stub that sleeps > a test
deadline, assert the GUI thread stays responsive (a QTimer tick fires) → reds on
the synchronous call.

### C8 (blocking) — wire the sidecar READ side + layer (b) input, or demote them honestly

`load_resolution`/`user_chosen` have **zero non-test callers**; the editor Load
path is `SettingsDocument.from_file`, which ignores the sidecar → Resolve→Save
writes `reduce_settings.provenance.json`, reopening the same file shows blank
badges / 0 provenance entries. v2 ships a persisted round-trip **wired on the
write side only** — v1's rejection sentence at smaller scope (~3 lines in
`load_settings`). **Also layer (b) has no production writer:** `ui_overrides` is
never populated — `resolve_for_experiment` fills (a)/(c) then replaces the
document wholesale, so edits typed before Resolve are **discarded, not ranked
first**, though (b) is the top of the taxonomy. **Fix:** wire the sidecar read in
`load_settings` **and** populate `ui_overrides` from pre-Resolve edits — OR
demote both honestly the way (d) was demoted (`DISCOVERY_LAYERS` + docstring +
test). Pick one; do not ship a third write-only-half. **Mutate:** Resolve→Save→
reopen, assert badges are populated from the sidecar → reds if Load ignores it;
type an edit, Resolve, assert its value ranks as (b) → reds if `ui_overrides`
stays empty.

### C9 (blocking) — pin the whitelist by membership, not per-group exemplars

`test_the_whitelist_is_derived_not_hand_listed:538` asserts **one exemplar per
group**, so a hand-list of 6 survives while the real derived set is **20** — a
regression dropping **14 of 20** preference fields is green; dropping the
`type == "path"`, the free-text, or the `runtime_owned` clause each survive too
(three of five clauses unpinned). `test_the_dialog_offers_exactly_the_whitelist`
can't help — the dialog is *built from* the constant. **Fix:** pin by
**membership** — assert the full derived tuple (all 20), or assert each of the
five clauses with a **counter-example field** (`Sname` free-text; a `path` field;
a `runtime_owned` field). The five clauses live in `_may_be_a_preference`
(`settings_resolver.py:120-145`): excluded-group (`GLOBAL_EXCLUDED_GROUPS`),
in-`GLOBAL_GROUPS`, not `per_angle`/`runtime_owned`, not `type=="path"`, not
free-text `str` (`type=="str" and not allowed`). **Mutate, per CLAUSE (five records):** drop each clause
in turn and the hand-list-of-6, assert the membership test reds for each.

### C10 (blocking) — the `tthd` UI field must reach discovery; pin `tthd == 0`

On the one-tree fixture above: restoring `sorted(glob("template*.xml"))[0]` at
`:435` (**the exact v1 B3 defect**) currently survives (v2 tree writes only
`template_up.xml`); use `template.py get_default_template_file(output_dir, tthd)`
(both autoreduce entry points already do). And hardcoding
`discover_ipts_settings(ipts, tthd=1.0)` at `settings_editor.py:531` — ignoring
the UI field — **survives**, because `_experiment_tree(..., tthd_up=False)` is a
**dead parameter** (no call site passes `False`): a scientist typing `tthd=-1`
silently resolves from the **up** file. **Fix:** pass the real UI `tthd` into
discovery; `tthd == 0` pinned (`tthd > 0` vs `>=` — flipping 0 to *up* must red);
an unparseable/empty `tthd` must not silently default to `1.0` (surface it).
**Mutate, per SITE:** (a) restore the sorted-glob → the both-templates+`tthd>0`
case reds; (b) hardcode `tthd=1.0` in the slot → the `tthd<0` case resolves
*down* test reds; (c) `>` → `>=` → the `tthd==0` case reds.

### C11 (blocking) — `render_value` round-trips every FIELD_SPEC type; delete `Field.render`

`field_spec.py:202-214` and `:356-368` both claim `render_value` inverts
`coerce`; it does for every type **except** `list[list[int]]`:
`render_value([[10,20],[30,40]]) → '[10, 20], [30, 40]'` →
`BkgROI.coerce(...) → [['[10'],['20]'],['[30'],['40]']]` (round-trips False). The
guard (`:369`) pins **flat** `list[float]` only. Unreachable via the tab today,
but C3's whole point was to make the renderer importable so the next file
inherits it — and what it inherits is wrong for the nested case. **Fix:** correct
the nested-list rendering; **delete `Field.render` (`:202`)** — zero callers,
zero tests, an untested second door onto `render_value` (the two-copies shape C3
exists to close). **Mutate:** `assert f.coerce(fs.render_value(v)) == v` over
**every** `FIELD_SPEC` type incl. `list[list[int]]` → reds on the nested type
until fixed.

### v3 should-fix — fold the HIGH-security ones; the rest are named for the reviewer

- **[HIGH, security] `Field.check` accepts `0`, `inf`, `NaN`** — `value <
  minimum` is False for `NaN`; `minimum=0.0` admits `0`/`+inf`; no `isfinite`.
  All three persist through the dialog's gate into layer (a), the cross-experiment
  layer. Blast radius at `nr_tools.log_qvector:74-75`: `dqbin=0`/`qmax=inf` →
  `OverflowError`; `dqbin=1e-12` → a **49.7 TB** `np.arange`; `dqbin=nan` → silent
  NaN in the q-vector. The docstring (`global_settings.py:179-181`) claims this is
  closed. **Reject non-finite; strictly-positive fields get an exclusive minimum.**
  Mutate: feed `0`/`inf`/`NaN`, assert rejected → reds without `isfinite`.
- **`_read_json` reads *through* a symlink** while `atomic_write_json` refuses to
  write through one — the confinement validates the *directory*, then `open()`s a
  link out of root, and the badge asserts "reduce_settings.json" for bytes from
  elsewhere (B5's class in the truthful-provenance module). Use `lstat` +
  `O_NOFOLLOW`.
- **Type confusion in `_read_json`** — size validated, type not; a top-level
  str/list/number makes `resolve()`'s `if name not in mapping` a substring test →
  `TypeError`. Add `isinstance(payload, dict)`. (Same family: NUL in the IPTS,
  symlink-loop root, and `root_path = Path(root).resolve()` at `:390` sitting
  *outside* the mount-guard try.)
- **`save_resolution` is not atomic as a pair** — settings first, sidecar second;
  a symlinked sidecar leaves a saved settings file with a stale sidecar. **Write
  the sidecar first.**
- **Discovery status erased by the first edit** (prepended to the volatile
  report) — give it its own persistent label.
- **A failed resolve reports success** — headline "Resolved IPTS-…" when nothing
  was found; `set_document` overwrites possibly-unsaved edits with no
  `changed_vs_seed()` check. Gate the headline on a non-empty result.
- Lower: every Save writes a sidecar incl. `{}` (litters the facility dir);
  `Resolved.value` dead weight in the sidecar; `settings_resolver.py` is 513 lines
  / five responsibilities (split when convenient); `select_by_geometry`'s `None`
  case untested in production autoreduce (`new_reduce_REF_L.py:110-111` deletion
  survives); the `:141` `if`/`:149` `elif` "looking for template" log that never
  looks; duplicated filename conventions (`settings_file(dir,tthd)` /
  `template_file(dir,tthd)` wrappers).

### v3 mutate-once — per SITE (amendment-16 sharpening)

v2's count reconciled (16 bullets) but hid survivors behind plural nouns: C1's
three guards recorded as "the mount guard", C10's two call sites as "the
sorted-glob", C5's edit sites as "edits not recorded", C9's five clauses as "the
whitelist". **Normative for v3 (charter amendment 16, sharpened): when a guard
names a behaviour with more than one implementation site, mutate EVERY site and
record each verdict on its own line** (`<mutation>@<site> -> N failed`). The
per-site mutation counts named above (C1 ×3, C5 ×5, C9 ×5, C10 ×3) are the
minimum the commit body must show.

### v3 acceptance (final-gate — LAST budgeted attempt)

- All three discovery stat sites guarded; `OSError` injected at each **by real
  `chmod 000`**, each red recorded (C1). One realistic fixture tree in place.
- Precedence prose + the UI label match `LAYER_ORDER`; the "or the data itself"
  wording gone (C2). Save round-trips `RUNTIME_OWNED_NAMES` (C3). Coercion
  unconditional + per-element, proven with `QSettings.value` returning a **list**
  (C4). `_record_edit` on every angle add/remove/edit site (C5). Out-of-set combo
  preference survives an untouched Save (C6).
- Discovery I/O cannot block the GUI thread past a deadline (C7). Sidecar read
  side wired + layer (b) populated, OR both demoted like (d) — no write-only-half
  (C8). Whitelist pinned by membership/clauses, 20 fields (C9). UI `tthd` reaches
  discovery; `tthd==0` and unparseable-`tthd` pinned (C10). `render_value`
  round-trips every type incl. nested; `Field.render` deleted (C11).
- HIGH should-fix folded: `Field.check` rejects `0/inf/NaN`.
- **Mutate-once per SITE** for every multi-site guard, each red on its own line
  in the commit body (amendment 16 sharpened).
- `pixi run test-launcher` + `test-reduction` green; no `pixi.lock` change.
- **Attempt 3 of 3 — the retry budget is exhausted after this.** If the gate
  passes and the blocking clusters are closed, the Integrator opens the draft PR;
  if a further blocking defect is found, the disposition is the human's (cap
  call), as with `check-results-fields`/`settings-editor`.

### Confirmed FIXED in v2 — do NOT rework (Integrator, todo @ `8abfdce`)

The autoreduce refactor (1536-case differential, 0 mismatches; one primitive,
three callers); B1 (reader-side whitelist), B2 (`ipts` confinement), B5
(`set_resolution` removed), B6 (symlink refusal via `atomic_write_json`), B7
(`_provenance` sidecar split — loader-safe); no resolved value reaches
`sympify`/Mantid `Formula=`/subprocess; the resolver wiring (production-path test
on a real seam); layer (d) honestly demoted; the 4 MB cap, `RecursionError`
catch, deep-copy boundary, `reseed`, pre-equalise snapshot, path confinement,
geometry exclusion (mechanism: `apply_config_overrides`
`nr_reduction_calc.py:1151-1163` overrides exactly the seven excluded fields),
optional-list nulls, `HUMAN_LAYERS`, sidecar-missing branch, badge labels, slot
guard; active-row trap absent; sorting pinned; no `.destroy()`; dialog leak
fixed; `accept()` guarded; validators attached. **Read this list before editing —
reworking a landed fix wastes the last attempt.**

## Revision history — v4 (human N=4 cap extension, 2026-09-12; todo @ `ecc1e3b`; attempt 4 of **N=4 extended**)

**The human read `plans/settings-management-escalate.md` and authorized a bounded
N=4 extension for this slug** — driven by C4 (silent science-correctness
regression) and C3 (launcher abort). This is the **final attempt under the
extension**; no discovery remains (the Integrator localized every site). v3 is the
strongest version — read "Confirmed FIXED in v2/v3" before touching anything.
Eight blocking clusters + two HIGH should-fixes below; **v3 source branch =
existing `feature/settings-management` @ `ecc1e3b` with the v3 Integrator todo on
top.** Anchors are v3-tip line numbers; they will drift as you edit — confirm each
by symbol.

### THE PROCESS FIX THAT UNBLOCKS THE ROOT CAUSE (do this first — it is *why* v2 and v3 both failed here)

The per-site granularity defect recurred **twice** because the mutation record
was (a) counted from prose and (b) unauditable. v4 makes it mechanical and
committed:

1. **Enumerate sites from the code, not the sentence** (test-reviewer's
   formulation): for every shared helper/rule below, `grep -c` its call sites (and
   for `_may_be_a_preference`, its **clauses**), and produce **one mutation per
   hit**. The counts you must hit: `_guarded_step` **5**, `_record_edit`-family
   **5**, `_may_be_a_preference` clauses **6**, the validate-or-refuse door **2**.
2. **The mutation ledger lives IN THE REPO, committed at the feature tip** — a
   `## Mutation ledger` section in `todo.md` (or a committed
   `plans/settings-management-mutation-ledger.md`), one line per grep-hit:
   `<helper>@<site-line> : <mutation> -> N failed (<test::name>)`. The commit
   message alone is **not** acceptable (v3's "28 mutations" was unauditable by
   construction — two reviewers independently could not check it). The Integrator
   will audit the ledger against `grep -c` at the feature tip.

### C1 (blocking) — `_guarded_step` catches the wrong exception class; 2 of 5 sites unpinned

`_guarded_step` (`settings_resolver.py:416-421`) catches `except OSError`, but
`Path.resolve()` raises **`RuntimeError`** on ELOOP (a self-referential symlink in
an sshfs/FUSE `/SNS` IPTS `shared/` tree — an ordinary facility condition),
`ValueError` on a NUL byte, `TypeError` on `None`/bytes. Sites `:447` and `:452`
survive unwrapping (suite green); the launcher survives only because
`_DiscoveryWorker.run` catches `BaseException` — every non-GUI caller gets the
raise. **Fix:** `except (OSError, RuntimeError, ValueError)` (or `except Exception`
recording the reason). **Mutate-once, per SITE (5):** unwrap each of the 5 guarded
steps in turn — each reds its own test; `:447`/`:452` inject a real symlink loop
(no monkeypatch).

### C2 (blocking) — resolve status reports success for a failed read and contradicts itself

`_guarded_step` returns `None` for **both** "raised" and "found nothing", so after
a `chmod 000` the caller appends a flat "no reduce_settings*.json" **as the last
word** — a persistent falsehood (`set_status`) the scientist acts on, reducing
from defaults with a layer-(a) value that (c) was meant to outrank. The author
separated the sentinel at the `is_dir` site (`:466-472`) but **not** at the two
scan sites (`:477`/`:496`, where passing `[]` instead of `notes` is green). **Fix:**
a distinguishable sentinel (`(ok, value)` or module-level `_FAILED`); append "no …"
**only** when the scan succeeded; **assert the errno text** (not truthiness — the
chmod-000 test asserts `assert ctx.discovery_status`, content unpinned).

### C3 (blocking) — the discovery worker aborts the launcher (exit 134) on teardown — take the ROBUST form

`_DiscoveryWorker` (`settings_editor.py:68-92`), parented at `:587`, has **no**
`closeEvent`/`wait()`/`quit()`/`deleteLater` — closing the launcher with a resolve
in flight gives `QThread: Destroyed while thread is still running`, **EXITCODE=134
on every teardown path** (measured), in the exact stalled-`/SNS` scenario the
worker was added for (v3 traded v2's freeze for an abort). **Do NOT just add
`wait()`** — a `wait()` on a D-state read blocks as long as the freeze did.
**Robust fix:** leave the worker **unparented**, hold it in
`self._discovery_worker`, connect `finished → deleteLater`; on `closeEvent`
disconnect `finished_with` and drop the reference — the stalled case **leaks one
thread instead of aborting** (the correct trade). Guard `restoreOverrideCursor`
(unreachable if the worker never returns → application-wide wait cursor persists
for the process life). Also fold the should-fix: `_DiscoveryWorker` objects
accumulate one per Resolve (6 presses → 6 live children). **Mutate:** a subprocess
test — close with a resolve in flight, assert clean exit (not 134); it must red if
the teardown handler is removed.

### C4 (blocking, SCIENCE) — two of v3's fixes compose to promote file/sidecar content above the measurement

`load_settings` seeds `self.provenance` from the sidecar (`:645-647`);
`_pre_resolve_overrides` converts **recorded origin → authority** (`:548-551`);
`resolve()` gates only layer (a) on `GLOBAL_WHITELIST`, so a sidecar-sourced `"b"`
is promoted ungated. Result (measured, no typing): geometry fields
(`dSampDet=99999`, `IncidentTheta=88`) — the `GLOBAL_EXCLUDED_GROUPS` set that has
**no layer (a)** precisely so *"a preference must never override a measurement"* —
reach layer (b) "set for this run" and **outrank the experiment file AND the
measurement**. Door 1: a dropped/own sidecar in group-writable `shared/autoreduce`.
Door 2: an "Add angle" click mints `Resolved(...,"b")` for **all 13** per-angle
fields nobody typed. **This defeats the C4(ii) exclusion the human decided.**
**Fix (one root, both doors):** (a) **never seed `ui_overrides` from provenance
read off disk** — in-session edits are already tracked by `_record_edit`; (b) map
a sidecar `"b"` to a **non-authoritative** marker (`"b*"`, label "set for a
previous run") so the badge stays truthful and the value stays non-authoritative;
(c) **separate a structural edit (row-count) from a value edit** — a row-count
change must not mint `Resolved(...,"b")`; clear per-angle overrides when
`ipts_edit` changes. **Mutate:** File→Open a sidecar with a geometry value, Resolve
with no typing, assert the geometry field's `source_layer` is **not** (b) and does
not outrank (e) → reds if the disk seed or the promotion remains; and an Add-angle
between two Resolves must not change a per-angle field's authority.

### C5 (blocking) — Save writes a document the panel already declared invalid

`:677` calls `save_resolution` with **no `validate()` gate**, while
`GlobalSettingsDialog.accept()` **does** gate on `check()` — two doors into one
rule, one guarded (granularity again). `dqbin=0` (which this commit added
`exclusive_minimum` for, reasoning it overflows downstream) writes to the
`shared/autoreduce` file autoreduction runs. **Fix:** ONE shared
validate-or-refuse helper used by **both** doors (not a second per-site copy).
**Mutate, per DOOR (2):** feed an invalid `dqbin=0` through the editor Save and
through the dialog accept — each must refuse; removing the shared gate reds both.

### C6 (blocking) — three re-record sites unpinned, two are the most-used editing paths

Sites/mutation (`_record_edit` → `refresh_badges`): `:358 _set_scalar` **survives**,
`:366 _on_scalar_edited` red, `:388 _on_cell_changed` **survives**, `:399 add_angle`
red, `:414 remove_selected_angle` red. A scientist types into a per-angle cell or
flips a checkbox, the document changes, and the header still attributes the column
to `reduce_settings.json` — full suite green. **Fix:** `_record_edit` at all five;
**Mutate, per SITE (5):** replace `_record_edit`→`refresh_badges` at each, assert
the badge flips to `[b]` after the edit → each reds.

### C7 (blocking) — the whitelist's excluded-group clause is unpinnable as written

`_may_be_a_preference` clause `:149` (`field.group in GLOBAL_EXCLUDED_GROUPS`) is
**unreachable**: `GLOBAL_EXCLUDED_GROUPS=(fs.GEOMETRY,)` but `GEOMETRY ∉
GLOBAL_GROUPS`, so the excluded-group clause can only fire for a group in BOTH
(empty set) — the geometry exclusion actually rides the `not in GLOBAL_GROUPS`
clause, and deleting the *explicit* clause (the one carrying the human decision)
is green. **Fix + Mutate:** the guard test **monkeypatches `GLOBAL_GROUPS` to
include `fs.GEOMETRY`** and asserts a geometry field is **still refused** — this
makes the excluded-group clause the only thing standing between geometry and the
whitelist, so deleting it reds. Count `_may_be_a_preference` as **6 clauses** in
the ledger.

### C8 (blocking) — `add_angle` lacks the guard its sibling documents 33 lines away

`settings_document.py` `add_angle:203` (`list(current) + [values.get(name)]`) has
no guard; `set_angle_field:236` **is** guarded (with a comment on why a `len()`
check was insufficient). Loading a file with a **scalar** per-angle value + Add
angle → `TypeError: 'float' object is not iterable` **mid-loop** → a ragged
document (third angle invisible), a false "unchanged" claim, `refresh_report()`
never re-runs so `validate()` never reports the lengths, and the file is written.
**Fix:** guard `:203` as `:236` is, **and make `add_angle` transactional** — mutate
a copy and commit, so a raise cannot leave a half-grown document; `report_problem`
must not claim "unchanged" unless it knows so. **Mutate:** add-angle onto a scalar
per-angle field, assert the document is unchanged (transaction rolled back) and no
file is written → reds without the guard/transaction. (Pre-existing, byte-identical
v2/v3 — but two clicks from a real file shape.)

### v4 should-fix — the two HIGH ones are FOLDED (science/crash), the rest named

- **[HIGH — FOLD] `qmin` admits `0` and it is the divisor.** v3 added
  `exclusive_minimum` to `dqbin`/`tof_bin`/`DetSigma` and **missed the denominator**:
  `qmin` is whitelisted, so `0` persists into layer (a) and outranks the guess/default
  for every future experiment — `log_qvector(0.0,0.5,0.005) → ZeroDivisionError`,
  `qmax=0 → OverflowError`. Add `exclusive_minimum=0.0` to `qmin` (and `qmax`).
  Mutate: persist `qmin=0`, assert refused.
- **[HIGH — FOLD] the six geometry divisors accept `0` and negative.** `mmpix`,
  `dSampDet`, `dMod`, `dS1Samp`, `nx`, `ny` have no bound: `dSampDet=0 →
  ZeroDivisionError` (`nr_reduction_calc.py:534`); negative → silently mirrored
  geometry; `mmpix=0` zeros the beam-on-detector calc **silently**. Reachable by
  typing, by an experiment file, and — via C4 — by a sidecar. v3 fixed the
  non-finite half; the zero/negative half remains. Add exclusive-positive bounds;
  mutate each.
- Named-not-folded (reviewer's call): `load_resolution` is the unhardened twin of
  `_read_json` on the production Open path (route it through `_read_json`);
  `MAX_SETTINGS_BYTES` bypassable via a FIFO (`st_size=0`; `os.open` on a
  writer-less FIFO blocks the worker forever) — require `stat.S_ISREG`, read
  `MAX+1`; sidecar strings render as **rich text** in the badge + can forge
  `source_layer` — validate against `LAYER_LABELS`, set `Qt.PlainText`; the
  settings/sidecar pair is non-atomic with an **orphan-sidecar** case (an authority
  grant given C4) — write+fsync+rename both, record the settings digest in the
  sidecar; `render_value`'s nested branch is **lossy** (drops/moves an angle on
  `None` padding, which is what `_equalise_angles` produces) — fix before the first
  caller, drop "exact inverse" from the docstring; `show_in_combo` accumulates
  strays; `.dat` admitted as a save suffix the editor's own Load refuses;
  `user_chosen`/`normalize` zero production callers (wire or demote like (d));
  precedence declared **8×** now (`global_settings.py:158` still pre-decision order).

### v4 acceptance (final-gate — LAST attempt under the N=4 extension)

- **Mutation ledger committed at the feature tip**, one line per `grep -c` hit;
  counts `_guarded_step` 5, `_record_edit`-family 5, `_may_be_a_preference` 6,
  validate-door 2 — each with its observed red. (The Integrator audits the ledger
  against `grep -c`; a prose count is a reject.)
- C1 catches `RuntimeError`/`ValueError` at all 5 sites; C2 distinguishable
  sentinel + errno-text assertion; C3 **robust** worker teardown (leak-not-abort),
  subprocess-proven, cursor guarded; **C4 both doors closed** — no disk-seeded or
  click-minted (b) authority, geometry never outranks (c)/(e), badge truthful;
  C5 one shared validate-or-refuse on both doors; C6 all 5 re-record sites pinned;
  C7 excluded-group clause pinned via `GLOBAL_GROUPS` monkeypatch; C8 `add_angle`
  guarded + transactional.
- **HIGH should-fixes folded:** `qmin`/`qmax` and the six geometry divisors reject
  `0`/negative.
- `pixi run test-launcher` + `test-reduction` green; no `pixi.lock` change.
- Draft PR body: C3/C4 as the science/crash fixes that drove the extension; the
  mutation ledger's home; non-goals (design §9) unchanged. **This is attempt 4 of
  the extended N=4 — the retry budget is exhausted after this.**

## Revision history — v5 (SECOND human cap extension to N=5, 2026-09-15; todo @ `ce591fc`; attempt 5 of **N=5 extended**)

The human read the second escalation (`plans/settings-management-escalate.md` @
`ce591fc`) and authorized a **second bounded extension to N=5** — recommendation
(a) accepted **with the resolver invariant** (item 4). The slug is converging:
**the mutation ledger audited clean** (all 18 mutations re-run, zero survivors),
**six clusters and both HIGH folds are closed and MUST NOT be re-litigated**, and
the two real blockers plus B3 have fixes agreed across three domains. **v5 source
branch = existing `feature/settings-management` @ `ce591fc` with the v4 Integrator
todo on top.** Anchors are v4-tip line numbers; confirm each by symbol.

**v5 scope — nothing outside this list (human, 2026-09-15):**

1. **B1 — bind the layer-(b) value at edit time.** `_session_edits` becomes a
   **dict** `{name: value}`; `_pre_resolve_overrides` returns
   `{n: v for n, v in _session_edits.items() if n in fs.BY_NAME}`;
   `_forget_per_angle_edits` pops `PER_ANGLE_NAMES`. **Do NOT clear the set in
   `set_document`** (security's caveat: it also fires after a completed Resolve and
   would drop a scientist's typed override on a second Resolve). **Guard:** add a
   prior `_on_scalar_edited("dSampDet", ...)` to the existing pin test; it must
   still assert `1500.0` at layer `"e"` (verified red at v4).
2. **B2 — worker teardown.** A `_forget_worker` slot connected to the worker's
   `finished` signal; `closeEvent` made defensive; **teardown moved to where it
   runs** (`LauncherWindow.closeEvent` forwarding or `QApplication.aboutToQuit`) —
   the tab's own `closeEvent` never fires on the real quit path; **pin the
   unparenting at `:617` explicitly**; the **window-level subprocess matrix** (idle
   / mid-resolve / stalled / repeated / close-after-completed-resolve) each
   asserting **exit 0 and the override cursor released**.
3. **B3 — sidecar read hardening.** Route the sidecar read through `_read_json`
   with the **regular-file gate**: `O_NONBLOCK` open so the open itself returns
   instead of waiting, `S_ISREG` on the fstat'd fd to refuse the file, then clear
   `O_NONBLOCK`. (Corrected in v6: this said a writer-less FIFO "returns `ENXIO`".
   It does not — `O_RDONLY|O_NONBLOCK` on one **succeeds**; `ENXIO` is the
   write-side behaviour. So `O_NONBLOCK` is what avoids the forever-wait and
   `S_ISREG` is what does the refusing — measured, and stated correctly in
   `settings_resolver._read_json`'s own docstring.) Name the wider
   Load/Save stalled-mount exposure in the **PR body as a follow-up, not in v5**.
4. **THE INVARIANT — the human's science decision (verbatim):** *a
   `GLOBAL_EXCLUDED_GROUPS` (geometry) field never resolves above layer (e) from a
   user-authority layer. Gate BOTH (a) and (b) at `settings_resolver.py:310`, and
   add a standing guard test asserting geometry resolves to (e)/the measurement
   regardless of what any door places in (a) or (b). A deliberate per-run geometry
   override is deferred to a later, explicit, badged feature — it is not a side
   effect of an edit.* (This closes the C4 door-**class**: a hypothetical fourth
   door reds the invariant instead of shipping. The B1-only alternative — keep
   typed geometry overrides, per-door closing — was **not** chosen.)
5. **Advisory item 9 ONLY** — the test closing over an undefined `ipts`: fix the
   identifier so the success path is exercised. **Every other advisory (1–8,
   10–17) is recorded in the draft-PR body, not fixed in v5.**

**Ledger requirement (amendment 16, hardened by the Integrator's frame lesson):**
before writing the ledger, **enumerate the frame** — every shared rule in the diff
(decorators, sentinels, bundled descriptions), not only the helpers changed. **A
ledger row whose description contains "/" is two rows.** Each new or changed guard
records its mutation and observed red, committed at the feature tip.

**Final-gate bar (Integrator):** **PASS when items 1–4 are present and their
mutations red and the subprocess matrix passes.** Item 5 missing is advisory. Any
further finding that is **not a genuinely new correctness defect** goes in the PR
body; **a genuinely new correctness defect escalates to the human — there is no
N=6 without a decision from the human.**

## Revision history — v6 (bounded, amendment 20 footing; 2026-09-19; todo @ `8c7dfbb`; B1 alone)

Human-approved after the v5/N=5 (3rd) escalation — the slug is one narrow,
fully-diagnosed fix from done (findings 8→2→1; v5's ledger audited clean, all 17
mutations red, 3/4 domains clear). **Scope is B1 alone + the record corrections +
three advisories; nothing else.** v6 source = existing `feature/settings-management`
@ `8c7dfbb` + the v5 Integrator todo. Runs on the **amendment 20** footing (criterion
below).

### item 1 (BLOCKING) — B1, the robust per-cell form

v5 defect: `_record_edit` (`settings_editor.py:481`; `_session_edits[name] =
self.document.get(name)` at `:489`) froze the **whole array** for the 13 per-angle
fields, so a later Load or Remove-angle mis-aligned every per-angle column via
`_equalise_angles` padding → wrong reduced data, badged "set for this run".

**Amendment 18 — type domain governed:** `_session_edits` holds BOTH **scalars** and
the **13 per-angle arrays** (`fs.PER_ANGLE_NAMES`). The v5 prescription was
scalar-correct, array-wrong. **Behaviour per type under the fix:**
- **Scalar:** bind the value at edit time (unchanged); a document swap must not lose
  it, a row-count change is irrelevant to it.
- **Per-angle array:** record **per cell** — `_session_edits[(name,row)] = value` as
  a **copy**, reassembled against the *current* row count at resolve time, so a
  Load/Remove between edit and Resolve cannot shift indices.

**Fix:** `_record_edit` records per-cell for `PER_ANGLE_NAMES` (keyed `(name,row)`),
scalars as today; `_pre_resolve_overrides` reassembles per-angle cells against the
current arrays; `_record_structural_change` (`:465`) rebinds/prunes the per-cell
entries on a row-count change (**the strict subset** that fixes Remove-angle alone);
bind a **copy** (`list(...)`/value copy), never the attribute (`SettingsDocument.get`
returns the live object — the `_copy` hazard). **Do NOT clear `_session_edits` in
`set_document`** (security's v5 caveat — it also fires after a completed Resolve and
would drop a typed override).

**Guard (mutate-once):** one fixture that **varies the row count between the edit and
the Resolve**, both triggers, **IPTS set BEFORE the edit** (an `ipts_edit.setText()`
after the edit fires `_forget_per_angle_edits` and pops the snapshot under test):
- **Load:** 2-angle tab, type a per-angle value on angle 2, Load a 3-angle
  experiment, Resolve → the typed value stays on the scientist's angle; the file's
  other angles are intact (not shifted, not `None`-padded over).
- **Remove-angle:** 3 angles, edit, remove angle 1, Resolve → no resurrected/
  mis-aligned array; `save_settings` writes the correct arrays.
- Mutations: `_record_structural_change`→no-op reds Remove-angle; `_pre_resolve_overrides`
  →v4 read-back reds Load; keep-the-live-list (no copy) reds a mutate-the-resolved-doc test.

### item 2 — mandatory record corrections

- **Rename `tests/test_settings_resolver.py:1163`
  `test_the_open_path_reads_through_the_same_gate`** — its name outruns its coverage
  (it calls `load_resolution(fifo)` directly, never `load_settings`/the Open path);
  rename to what it covers (e.g. `test_load_resolution_refuses_a_fifo_sidecar`).
- **Correct two prose items:** the `deleteLater` comment at `settings_editor.py:646-649`
  and the `_PARKED_WORKERS` comment, to match their code.
- **Correct this plan's ENXIO sentence (v5 item 3/B3):** a writer-less FIFO opened
  `O_RDONLY|O_NONBLOCK` **succeeds** — it does NOT return `ENXIO` (ENXIO is the write
  side). `O_NONBLOCK` avoids the blocking wait; `S_ISREG` refuses the file. (Error
  originated in the v4 work order; corrected here.)
- **State the residual plainly + fix ledger row 17's heading:** a local `mkfifo` (not
  merely a stalled mount) still freezes the GUI on Open and hangs autoreduction —
  **pre-existing, follow-up**, in the PR body.

### items 3–5 — the three advisories promoted into scope

- **item 3 (adv-1):** the sidecar half of ledger row 17 gets its **own test** —
  `mkfifo` on the provenance-sidecar path, assert the read is refused/non-blocking
  (the settings-file read was pinned; the sidecar was the unpinned 2nd call site of
  `_read_json`).
- **item 4 (adv-2):** add `--timeout` to the **reduction** pixi task (`pyproject.toml`
  — `test-reduction` arms none; `test-launcher` has 120 s) so the two hang-mode guards
  can red in CI.
- **item 5 (adv-8):** one **`LAYERS` table** mapping each letter → (order, label,
  authority) + a test that **every `LAYER_ORDER` member carries an authority
  classification**. The deferred per-run badged-override feature *is* a new layer and
  the extension is **fail-open** today.

Everything else on the v5 advisory list rides the **PR body**, not the diff.

### ledger + acceptance

- **Mutate-once (amendment 16 as folded):** frame first; **one row per call site** of
  every helper introduced or **re-pointed**; split `/`/"and"/"or" rows; a hang-mode
  mutation needs the `--timeout` item 4 adds. Ledger committed at the feature tip.
- **Harness restore-safety (Developer contract):** chunk under 600 s, per-invocation
  timeout, restore-FIRST, verify by symbol before any commit.

### amendment-20 criterion (in force)

**If v6 is rejected on the same *demonstrate-the-case-you-thought-of* shape at a new
level, DECOMPOSE `settings-management` into single-review-surface slugs (§4 sizing
rule) — do NOT extend the cap.**

### final-gate bar (Integrator)

**PASS when items 1–5 are present and their mutations red.** Anything not a genuinely
new correctness defect rides the PR body; a genuinely new correctness defect
escalates to the human (amendment 20 decides decompose-vs-extend). Draft PR on pass;
merging stays the human's deploy decision (charter §7).
