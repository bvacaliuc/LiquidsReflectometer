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
