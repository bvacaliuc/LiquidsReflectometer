# Plan: settings-management (T3)

**Campaign:** `exp-settings-roi` · base `exp` @ `6da473d` (T2 merged, PR#28) ·
charter §4 slug T3 · full design in
`tasking/plan/settings-management/plan.md` (398 ln) — **authoritative source
is `src/lr_reduction/{settings_document,field_spec,reduction_domains}.py` in
the checkout, NOT the design doc** (out-of-tree; the doc is human background)
**Retry attempt:** 1

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
