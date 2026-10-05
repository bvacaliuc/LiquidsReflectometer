# Plan: `editor-ipts-inference` — the header's IPTS follows the file's `experiment_id`, else the run numbers, else the field, else the file's path; an empty IPTS with runs named is a problem; the Load dialog opens where the IPTS's files live

**Campaign:** `exp-review-fixes` · **Leaf:** `editor-ipts-inference` (refs `triage/editor-ipts-inference`, `feature/…`, `qa/…`) ·
**Status:** v2 (attempt 2 of N = 3; v1 rejected at `review/editor-ipts-inference` @ `e0a7e72` — **tests only**: B-1 the runs-before-field order (the human's own flow) and B-2 the remembered-folder write had no failing-capable test; see Revision history) — v1 dispatched 2026-10-05 under the posture's **stacking by file overlap** rule (`ec10742`), on
K1's Integrator PASS (I-39, draft PR #43); v2 continues on `feature/editor-ipts-inference` (the Integrator's `todo.md` on top, @ `e0a7e72`): the plan's files overlap **two** open branches — `feature/editor-notes-and-report-spelling` (K1,
both files) and `feature/editor-sections` (#40, `settings_editor.py`) — and K1's branch **contains** #40's tip, so rule (4) resolves to the
larger overlap, K1, with nothing else to merge forward ·
**Base:** `agentic/feature/editor-notes-and-report-spelling` @ `779f787` — **overlap at dispatch** (`git diff --name-only agentic/exp-review...
agentic/feature/<x>`, tests excluded, `exp-review` @ `5a8742d`): K1 {`settings_document.py`, `settings_editor.py`} ∩ both; #40
{`settings_editor.py`} ∩ (contained in K1); `feature/test-suite-warnings`, `feature/launcher-env-outside-xdg-cache`,
`feature/rereduction-headers-land`, `feature/roi-estimate`: none · **PR target:** `feature/editor-notes-and-report-spelling` on the fork,
**draft** (retargeted down the stack by the human's merges) · **Stack:** #40 → K1 (#43) → **this slug** → `editor-sections-followup` (K3,
when charter-added); the Developer cuts `feature/editor-ipts-inference` `--no-track` from `agentic/feature/editor-notes-and-report-spelling`
and regular-merges it forward before every `qa/` push; the Integrator opens the draft PR `--base feature/editor-notes-and-report-spelling` · **Depends on:** `editor-paths-header` (merged, #39 — the header
and `derived_path` this slug feeds), the editor lane merged, K1 merged · **Review domains:** design, ui-aspects, test (block); security
(advise — a glob over a facility mount) · **Kind:** launcher / settings model — not reduction-path (the reducer's path derivation is read,
not changed) ·
**Sources:** `[human, 2026-10-05: "The Advisor recommended to merge PR#39 but with a follow-on task: ledger/todo-editor-ipts-inference-and-
load-dialog.md. Please schedule that todo following PR#40 as appropriate."]`; the human's PR #39 review (2a–2d, verbatim in the todo);
Advisor V1-29, `plans/review-pr39-observations.md`; charter §3 row.

## Declared scope

**Files in:** `src/lr_reduction/settings_document.py` (IPTS resolution, the source-path record, the `validate()` line, the Load-folder
rule as Qt-free helpers), `launcher/apps/settings_editor.py` (`load_settings`, the header's refresh after Load), their two test modules
(`tests/unit/lr_reduction/test_settings_document.py`, `launcher/tests/test_settings_editor.py`), and one new committed fixture: the human's
from-scratch file (`experiment_id: ""`, three run numbers) under `launcher/tests/data/` or `tests/data/` as the repo's fixture convention has it.

**Behaviours in** (I1–I7, §3). **Explicitly OUT:** the reducer (`nr_reduction_calc.py:325` keeps reading `NEXUSpathRB / REF_L_<run>.nxs.h5`
and raising `FileNotFoundError` at reduction time — unchanged); `reduce_from_file`'s own `experiment_id` substitution (`new_reduction_from_
file.py:62`); `derived_path` and `candidates()` (they follow whatever `experiment_id` holds — this slug decides what it holds); writing an
override (`_NEXUSpathRB_override` stays `None` — P3 of `editor-paths-header`); the `.dat` seed path (`from_file` of a `# Config:` header gets
the same resolution with no file-path inference beyond 2c); any REF_M behaviour (the comment's `REF_M` read as REF_L, per the Advisor).

## 1. Request

The human's PR #39 review (the rule, verbatim in `todo-editor-ipts-inference-and-load-dialog.md`):

> a. *"paths should be set according to the angles and the run numbers referenced … its IPTS is also unique and unambiguous. It is a
> warning if the settings file specifies run numbers from different IPTS paths — choose the 1st IPTS that resolves."*
> b. *"if there are no angles (hence no run numbers known), then the IPTS that was present in the edit field should hold"*
> c. *"if the edit field is empty and the file that was loaded contains no angles, then try to infer the IPTS from the path of the loaded
> file (provided it was loaded from an /SNS/REF_L/{ipts} path)"*
> d. *"otherwise the edit field was already empty so there is no harm in leaving it that way"*

and observation 1: the Load dialog opens at the last-used folder whatever IPTS the header holds, and offers none of the folders where settings
files live.

## 2. Verified facts at `feature/editor-sections` @ `efa1b81`, **re-sealed 2026-10-05 at the base `779f787`** (K1's PASS tip; it contains `efa1b81`): `nr_reduction_config.py`, `nr_reduction_calc.py`, `field_spec.py`, `roi_selector.py` blob-identical; in `settings_document.py` every cited definition is at the same line (`normalise_experiment_id` `:74`, `from_file` `:195`, `derived_path` `:467`, `validate` `:524`) — K1's additions sit after `notes()` (`:630`) and add `file_spelling(field, value, count=None)` at `:825`; in `settings_editor.py` only `load_settings`/`save_settings` moved (F5). **I2/I3's Notes use K1's `notes()` form and `file_spelling` for any value they print** — one renderer, as K1 established.

| # | Fact | Evidence |
|---|---|---|
| F1 | **The reducer finds NeXus files by run number under `NEXUSpathRB`**, which derives from `experiment_id` when no override is set: `base_path = Path("/SNS/REF_L") / experiment_id`, `NEXUSpathRB = base_path / "nexus"`; the file read is `NEXUSpathRB / f"REF_L_{rb_num}.nxs.h5"`, and a missing file raises `FileNotFoundError` **at reduction time**. With `experiment_id == ""` the folder is `/SNS/REF_L/nexus`. | `nr_reduction_config.py:112-113, 126-129`; `nr_reduction_calc.py:325-328`. |
| F2 | **`validate()` says nothing about an empty IPTS.** `experiment_id`'s `Field` is `"str"`, default `""`, `no_separators=True`; `check()` reports separators and `..`; an empty value passes. So a from-scratch file naming three runs (`RBnum == [229197, 229198, 229199]`) with `experiment_id: ""` reads "No problems found" and is unreducible (Advisor, measured at `0cc96e1`). | `field_spec.py:580-582`; `settings_document.py:524-…`; the Advisor's measurement in the todo. |
| F3 | **The document does not know where it was loaded from.** `SettingsDocument.from_file(path)` reads through `load_from_file(Path(path))` and returns `cls.from_dict(values)` — the path is dropped (`settings_document.py:195-207`). 2c needs it. | Read at `efa1b81`. |
| F4 | **The header is fed by `experiment_id` alone.** `_on_ipts_edited` stores `normalise_experiment_id(widget.text())` and refreshes the derived displays (`settings_editor.py:914-923`); `set_document` → `_show_derived_paths` (`:1058`, `:1143`, `:964-969`); `derived_path(name)` answers `None` when `experiment_id` is empty or reported (`settings_document.py:467-481`). | Read at `efa1b81`. |
| F5 | **`load_settings` opens the dialog at the remembered folder** (`self.settings.value("settings_editor_dir", "")`) and remembers the chosen file's parent (`:1186-1205` at `779f787`; `:1181-1200` at `efa1b81`); `save_settings` likewise (`:1208-1228`; was `:1203-1207`). No sidebar URLs; the header's IPTS plays no part. | `settings_editor.py:1181-1207`. |
| F6 | **The IPTS of a run is knowable from the facility tree in two ways** (Advisor, measured on the analysis node 2026-10-04): `glob("/SNS/REF_L/IPTS-*/nexus/REF_L_<run>.nxs.h5")` over 286 IPTS directories returns the one hit in 0.10 s; the NeXus file's `entry/experiment_identifier` holds `IPTS-36119`. The library already reads `experiment_identifier` from a loaded run (`event_reduction.py:552`; `new_reduce_REF_L.py:144, 213`), and `roi_selector.py:658` spells the path `f"/SNS/REF_L/IPTS-{ipts}/nexus/REF_L_{run}.nxs.h5"`. | `git grep` at `efa1b81`; the todo's Evidence. **Not measurable on `uvdl3`** (`/SNS` not mounted) — the glob leg is the Integrator's. |
| F7 | **Where real settings files live:** 101 of 104 real files are under `<IPTS>/shared`, `shared/reduced/…` or `shared/autoreduce`; 94 of 104 carry `experiment_id`, 88 of those under their own IPTS; 10 have none (every from-scratch editor save). | Advisor V1-29 / `plans/review-pr39-observations.md` §Measured. |
| F8 | `normalise_experiment_id(text)` exists (`settings_document.py:74-…`): a bare number → `IPTS-<n>`, `ipts-` → `IPTS-`, empty → `""` never `None`. The per-angle run list is `RBnum` (`list[int]`, `field_spec.py:539`); the angle-defining length is `_defining_length()`. | Read at `efa1b81`. |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| I1 | **One resolution, in the human's order, at Load** — **(v2, design A3 adopted) at `load_settings` only**, never at `set_document`/construction: a document injected by other code resolves nothing (no facility lookup at construction; a re-adoption after a clear does not re-infer — I6); the order is **asserted as an order** (B-1: a held `IPTS-1` with runs that resolve under `IPTS-36119` → `IPTS-36119`, the human's flow): (1) the file's `experiment_id`, when non-empty and clean (`check()` empty) → held as is; (2) else, **if the file names run numbers** (`RBnum` has at least one entry), the IPTS the runs resolve to (2a); (3) else, **if the header's field held an IPTS before the Load** (2b), that IPTS; (4) else, **if the file was loaded from under `/SNS/REF_L/IPTS-<n>/`** (2c), that IPTS; (5) else `""` (2d) — and I4 reports it. The outcome is written into the document's `experiment_id` (so `derived_path`, `candidates()` and Save all follow), and **"Changed from the seed" shows it** when it differs from the file (the human's 2b note: an inferred IPTS is a change the user should see — and can clear). Steps (2)–(4) apply only when (1) yields nothing; the file's own value is never overridden. |
| I2 | **Resolving runs → IPTS (2a):** for each **distinct** run in `RBnum` (bounded: one lookup per distinct run, cached per Load), the IPTS is the single directory `d` such that `/SNS/REF_L/<d>/nexus/REF_L_<run>.nxs.h5` exists (one glob, `/SNS/REF_L/IPTS-*/nexus/REF_L_<run>.nxs.h5`); a run with no hit resolves to nothing. If every resolving run agrees → that IPTS. If they disagree → **the first run's** (the human: "choose the 1st IPTS that resolves") **and a Note** naming the runs and their IPTSs. If none resolves (a run not on this filesystem, no mount, a typo) → nothing, fall through to (3), and the Note says the runs did not resolve. The lookup is a Qt-free helper on the document module, takes the root as a parameter (`root="/SNS/REF_L"`) so tests use a `tmp_path` tree, never touches the network beyond the mount, swallows `OSError` (a stale handle on a facility mount is ordinary — `candidates()`'s precedent). |
| I3 | **The file's own `experiment_id` wins over the runs, with a Note when they disagree:** when (1) holds and the runs resolve elsewhere, the value stays the file's and a **Note** says *"the run numbers resolve under <IPTS-x>, not <experiment_id>"* (the todo's "file wins; a Note that the runs resolve elsewhere"). A Note, not a problem: `reduce_from_file` substitutes the run's IPTS anyway (`new_reduction_from_file.py:62`), and the reducer's path check is the hard stop. |
| I4 | **An empty IPTS with runs named is a problem** (2d, "and say so"): `validate()` reports *"IPTS (experiment_id) is empty and <n> run numbers are set: the reduction would look for REF_L_<run>.nxs.h5 under /SNS/REF_L/nexus and not find it — enter the IPTS, or choose a NeXus path"* whenever `experiment_id` is **empty — `""`, `None` (a file with `null` or no key: 10 of 104 real files) or whitespace only** (v2: one definition of "empty", the test reviewer's row and A7; `None` and spaces made `base_path` raise or misbehave with `validate()` silent — the plan's states listed `""` alone), `RBnum` is non-empty and `_NEXUSpathRB_override` is `None`. **The only production change in v2 is that condition.** An empty IPTS with **no** runs is not a problem (nothing to reduce yet); an override set makes the IPTS irrelevant to NeXus (no problem; the direct-beam path has its own override). |
| I5 | **The Load dialog opens where the IPTS's files live:** with an IPTS in the header (clean, non-empty) the dialog starts at `/SNS/REF_L/<IPTS>/shared` **unless** the remembered folder (`settings_editor_dir`) is already under `/SNS/REF_L/<IPTS>/`, in which case the remembered folder wins (the user's last place in this experiment); without an IPTS, the remembered folder as today. The dialog's **sidebar** offers `<IPTS>/shared`, `<IPTS>/shared/reduced`, `<IPTS>/shared/autoreduce` (those that exist; `QFileDialog.setSidebarUrls`, non-native dialog so the sidebar is honoured — the Developer measures which option is needed and records it). The remembered folder is still written after a Load and a Save. The **Save** dialog follows the same start rule. The start-folder decision is a Qt-free helper (`load_start_folder(ipts, remembered, root)`), tested without a dialog. |
| I6 | **Typing an IPTS in the header stays as it is** (`_on_ipts_edited`, `editor-paths-header` P5): no inference runs on a typed value; the typed value is the user's and overrides every inference until the next Load. Clearing the field → `""` and I4's problem line if runs are named. |
| I7 | **Fail loudly, never silently:** every inference that *changes* the document is visible — in "Changed from the seed" (I1) and, for 2a with disagreeing runs or an unresolvable run, in a Note; nothing is written to the file's `experiment_id` field on disk until the user Saves (as for any edit). The glob never blocks the UI beyond its own duration: one `glob` per distinct run, measured 0.10 s each (F6); a Load of a file with ten distinct runs is ~1 s worst case on the facility tree, acceptable — and the Developer records the measured time on the analysis node in the PR body. |

**Types and states** (per Load): file's `experiment_id` ∈ {clean non-empty, empty, reported (separators/`..`)} × `RBnum` ∈ {empty, one run,
several runs agreeing, several disagreeing, a run with no hit, all without hits} × field before Load ∈ {empty, IPTS} × file path ∈ {under
`/SNS/REF_L/IPTS-n/…`, elsewhere, a `.dat` seed, injected document (no path)} × override ∈ {`None`, set}. A **reported** `experiment_id`
counts as "nothing" for step (1)? — **No**: a reported value is held as loaded (the editor never rewrites a value the file holds — `editor-
load-fidelity` B8) and `validate()` reports it as today; inference does not run (the file *has* a value, a bad one). Stated in §10 A2.

**Operation × state (every cell a required outcome, each named by a test — U1–U6, V1–V6):**

| Load of … | `experiment_id` after | "Changed from the seed" | Notes / Problems | header shows |
|---|---|---|---|---|
| file with `IPTS-36119`, runs under it | `IPTS-36119` (file) | — | none | `IPTS-36119`, derived paths |
| file with `IPTS-36119`, runs resolving under `IPTS-38016` | `IPTS-36119` (file wins, I3) | — | **Note**: runs resolve under `IPTS-38016` | `IPTS-36119` |
| file with `""`, runs all under `IPTS-36119` | `IPTS-36119` (2a) | `experiment_id: "" -> "IPTS-36119"` | none | `IPTS-36119` |
| file with `""`, runs in two IPTSs | the first run's (2a) | shown | **Note**: the runs and their IPTSs | the first run's |
| file with `""`, runs with no hit, field held `IPTS-1` | `IPTS-1` (2b) | shown | **Note**: runs did not resolve | `IPTS-1` |
| file with `""`, no runs, field held `IPTS-1` | `IPTS-1` (2b) | shown | none | `IPTS-1` |
| file with `""`, no runs, field empty, loaded from `/SNS/REF_L/IPTS-7/shared/x.json` | `IPTS-7` (2c) | shown | none | `IPTS-7` |
| file with `""`, no runs, field empty, loaded from `/home/u/x.json` | `""` (2d) | — | none (no runs) | "set an IPTS or type a path" |
| file with `""`, runs with no hit, field empty, path elsewhere | `""` (2d) | — | **Problem** (I4) + Note (unresolved) | placeholder |
| file with `"../x"` (reported) | `"../x"` as loaded | — | Problem (today's) — no inference | as loaded |
| `.dat` seed, `""`, runs resolving | 2a as for `.json` | shown | — | — |
| injected document (no path), `""`, no runs, field empty | `""` | — | none | placeholder |
| **(v2)** injected document naming runs (no Load) | unchanged — **no lookup runs at construction** (I1, A3) | — | Problem (I4) if empty | placeholder |
| **(v2, B-1)** file with `""`, runs all under `IPTS-36119`, **field held `IPTS-1`** | `IPTS-36119` (2a beats 2b) | shown | none | `IPTS-36119` |
| **(v2)** file with `null` / no `experiment_id` key, runs with no hit, field empty, path elsewhere | `""` (held as empty) | — | **Problem** (I4) — not silent | placeholder |
| then: user types `IPTS-9` | `IPTS-9` (I6) | shown | — | `IPTS-9` |
| then: user clears the field, runs named | `""` | **shown only if the seed held a value** (v2 CORRECTION — the test reviewer: after loading a `""` file and clearing, the value equals the seed and nothing is Changed; the Problem is what shows) | **Problem** (I4) | placeholder |
| Load dialog with header `IPTS-36119`, remembered `/home/u` | — | — | — | dialog starts `/SNS/REF_L/IPTS-36119/shared`; sidebar the three |
| Load dialog with header `IPTS-36119`, remembered `/SNS/REF_L/IPTS-36119/shared/reduced` | — | — | — | starts at the remembered folder |
| Load dialog with header empty | — | — | — | starts at the remembered folder (today) |

## 4. Files to change

| File | Change |
|---|---|
| `settings_document.py` | `from_file` records the source path (an attribute, not a config key); `resolve_experiment_id(file_value, runs, field_value, source_path, root=…)` returning `(value, notes)`; `ipts_of_run(run, root)` (one glob, cached per call set); `validate()` gains I4; `notes()` gains I2/I3's lines; `load_start_folder(ipts, remembered, root)` |
| `settings_editor.py` | `set_document` applies the resolution with the field's prior value and the document's source path, then refreshes; `load_settings`/`save_settings` use `load_start_folder` and set the sidebar |
| tests + fixture | §6 |

## 5. Failure-mode matrix

| Class | Case | Required outcome |
|---|---|---|
| common | the scientists' from-scratch flow: new file, runs typed, Save, Load | after Load the header shows the runs' IPTS (2a), "Changed from the seed" shows it; a Save then writes it |
| common | a real autoreduce file | the file's IPTS; no inference; no Note |
| common | Load with an IPTS in the header | the dialog opens under that IPTS's `shared`; the sidebar has the three folders |
| edge | runs from two experiments in one file | the first's IPTS; a Note names both |
| edge | a run number typed wrong (no hit) | the Note says so; no IPTS invented; 2b/2c/2d apply |
| edge | `/SNS` not mounted (a laptop) | the glob returns nothing in milliseconds; 2b/2c/2d; no exception; tests use `tmp_path` |
| edge | a stale FUSE handle during the glob | `OSError` swallowed → "did not resolve"; the slot returns (the `candidates()` precedent) |
| edge | the file's IPTS disagrees with the runs | the file wins; a Note |
| pathological | a run that exists under two IPTS directories (a copied NeXus) | the glob returns two hits → treat as **ambiguous**: the first sorted, and a Note naming both (never silent) |
| pathological | 200 distinct runs in one file | 200 globs ~20 s on the facility tree — **bounded by a cap** (e.g. the first 20 distinct runs are looked up; the Note says the lookup was capped) — the Developer measures and sets the cap in one constant |
| pathological | `experiment_id` reported (`..`) | held as loaded; today's problem; no inference |
| pathological | `QFileDialog` native dialog ignores the sidebar | the start folder still applies; the sidebar leg is skipped with a reason in the test if the platform cannot honour it; the Developer records the measured behaviour |

## 6. Red-Green TDD seed

| # | Test | RED at the base |
|---|---|---|
| U1 | `ipts_of_run(run, root=tmp_path)` with a fabricated `IPTS-*/nexus/REF_L_<run>.nxs.h5` tree: one hit → the IPTS; no hit → `None`; two hits → both, sorted; an unreadable root (`OSError`) → `None` | helper absent |
| U2 | `resolve_experiment_id` × every row of §3's table (fabricated tree, fabricated source paths): the value **and** the Notes text; the file's non-empty value never overridden; a reported value untouched; **(v2, B-1)** the row "runs resolve under `IPTS-36119` **and** the field held `IPTS-1`" → `IPTS-36119` (the order, asserted — a runs↔field swap must red); **(v2)** every row asserts **all three columns** — header, Changed, Problems/Notes (the test reviewer: twelve rows each lacked one); `None` and whitespace-only `experiment_id` rows; the Notes' IPTS names and runs rendered through `file_spelling` (§2) | helper absent |
| U3 | `validate()`: `""` + runs + no override → the I4 line; `""` + no runs → nothing; `""` + runs + override set → nothing; the line names the run and the folder | passes silently today |
| U4 | `from_file` records the source path; `from_dict` records none; the `.dat` seed records its path | no attribute |
| U5 | `load_start_folder` × {IPTS set/empty} × {remembered under the IPTS / elsewhere / empty} × root → the table's folders; sidebar list = the existing three of the IPTS | helper absent |
| U6 | the lookup is bounded: a file with N distinct runs performs ≤ cap lookups (count the glob calls via monkeypatch), and the Note says capped when N > cap | — |
| V1 | the committed from-scratch fixture, loaded on a shown tab with the fabricated tree as root (monkeypatched constant): header `IPTS-36119`, both derived paths, "Changed from the seed" shows `experiment_id`, Save writes it | header `''`, placeholders, "No problems found" |
| V2 | the field held `IPTS-1`, Load a no-runs `""` file → `IPTS-1` kept (2b); **(v2, B-1) the field held `IPTS-1`, Load a `""` file whose runs resolve under `IPTS-36119` → `IPTS-36119` shown, Changed `"" -> "IPTS-36119"`** (through `load_settings`, the dialog monkeypatched); Load from a `/SNS/REF_L/IPTS-7/…` path (the path passed to `from_file`, the tree fabricated) with the field empty → `IPTS-7` (2c); **(v2, A3)** `SettingsEditorTab(SettingsDocument.from_dict({"RBnum": [229197]}))` → the lookup counter stays 0 and `experiment_id` stays `""` | — |
| V3 | the I4 problem appears in the panel after Load of a `""` + runs file with no hits, and after clearing the field on a file with runs; disappears when an IPTS is typed | — |
| V4 | typing an IPTS runs no inference (the glob counter stays 0); the typed value stands after a later `refresh` | — |
| V5 | `load_settings` with `QFileDialog.getOpenFileName` monkeypatched to capture its `dir` argument: header `IPTS-36119` + remembered `/home/u` → `<root>/IPTS-36119/shared`; remembered under the IPTS → the remembered; header empty → the remembered; `save_settings` the same; the sidebar URLs set (where the platform honours a non-native dialog — else skipped with a reason); **(v2, B-2) after a Load and after a Save, `self.settings.value("settings_editor_dir")` equals the chosen file's parent** — read back, not preset | starts at the remembered folder always |
| V6 | the Notes for disagreeing runs and for the file-wins case appear under "Notes:", never under "Problems:" | — |

## 7. Mutate-once gate

| Mutation | Must red |
|---|---|
| step (1) skipped (runs override the file's IPTS) | U2 (file-wins row), V-equivalent |
| 2a resolves to the *last* run's IPTS instead of the first | U2 (disagreeing row) |
| 2b dropped (field ignored) | U2, V2 |
| **(v2, B-1)** the runs block moved below the field block (2b before 2a) | U2 (the held-`IPTS-1`-runs-resolve row), V2 |
| **(v2, B-2)** the `settings_editor_dir` write deleted in `load_settings` / in `save_settings` | V5 (read-back legs, one per slot) |
| **(v2)** I4's condition tests `== ""` only (`None` / spaces slip through) | U3 (`None` and whitespace rows) |
| **(v2, A3)** resolution called from `set_document` again | V2 (injected-document leg: lookup counter 0) |
| 2c dropped (path ignored) / 2c applied although runs exist | U2, V2 |
| I4 line emitted with an override set, or without runs | U3 |
| source path not recorded | U4, V2 (2c leg) |
| glob unbounded | U6 |
| `OSError` escapes the lookup | U1 |
| two hits treated as one silently | U1, U2 (ambiguous row Note) |
| inference run on a typed value | V4 |
| start folder ignores "remembered under the IPTS" | U5, V5 |
| the Note emitted as a problem | V6 |

Frame: one resolver (`resolve_experiment_id`), one lookup (`ipts_of_run`), one start-folder rule, each Qt-free and parameterised by `root`
so no test touches `/SNS`; `set_document` is the single caller of the resolver; `_on_ipts_edited` untouched.

## 8. Acceptance criteria

1. Gate: `pixi run test-reduction` zero from the repository root on the feature tip.
2. §6 RED→GREEN; §7 recorded per row.
3. Deployment-shaped acceptance (Integrator, analysis node, offscreen; **no login shell**): load the human's from-scratch file → header
   `IPTS-36119`, derived paths, the Changed line; load `IPTS-36574/shared/autoreduce/reduce_settings.json` (its `experiment_id` is
   `IPTS-38511`, the file copied from another experiment — F7's class) → the file's IPTS kept and a **Note** that the runs resolve under
   **`IPTS-36970`** (v2 CORRECTION of the Analyst's expectation `IPTS-36574`: the Integrator measured runs 228313–228316 with `ipts_of_run`;
   the file lives under IPTS-36574, its runs under IPTS-36970 — F7's class exactly); a file with runs from two IPTSs (fabricate by editing a copy in scratch) → the first's + Note; measure and quote the glob
   time per run on the facility tree; the Load dialog's start folder and sidebar with `IPTS-36119` in the header (offscreen: capture the
   arguments; a screenshot if the platform shows the sidebar).
4. ui-aspects: the Note wording reads as information, the Problem as a problem; the header's placeholders unchanged.
5. PR body: launcher-only; the human's 2a–2d quoted with the row each maps to; the cap constant and the measured glob time; what the
   scientists see in the from-scratch flow (an IPTS appears after Load, marked as changed).

## 9. Learnings relied on

- `editor-paths-header` (merged, #39): P3/P5/P6 — overrides written only on explicit edit; the derived display; `normalise_experiment_id`;
  "no IPTS" as a placeholder state — this slug decides *when* that state is legitimate (no runs) and when it is a problem (runs named).
- `editor-load-fidelity` B8: the editor never rewrites a value the file holds → step (1) and the reported-value row.
- `candidates()` (`editor-combos`): a facility-mount lookup swallows `OSError`, caches nothing across calls, and is bounded → I2's shape.
- The campaign's standing lesson: every cell of §3's table is named by a test; §7's tests observe through the path the mutation breaks;
  **facts about the facility tree are the Integrator's to measure** (F6 — `/SNS` is not mounted here), and the plan says so.

## 10. Assumptions and open questions

| # | Question | Default |
|---|---|---|
| A1 | Scheduling: after K1 merged (sequential on the same files), or stacked on K1 / in parallel? | **After K1 merged** — the queue keeps lanes file-disjoint and K1 is small; if the human wants both in flight at once, K2 can stack on K1's feature branch with one posture line (the E3–E5 pattern). |
| A2 | A reported `experiment_id` (separators, `..`): infer or hold? | **Hold as loaded** (B8); today's problem line stands; no inference — the file has a value, a bad one. |
| A3 | The glob cap. | A constant (suggested 20 distinct runs); the Developer measures on the facility tree and records the time. |
| A4 | `experiment_identifier` from the NeXus file as a second source. | Not needed when the glob resolves (the directory *is* the IPTS); kept as a documented alternative in the resolver's docstring, not implemented. |
| A5 | Save dialog start folder. | Same rule as Load (I5) — one helper. |

## Revision history

v1 — authored 2026-10-05 against `feature/editor-sections` @ `efa1b81` (the editor content of `exp-review` after #40), **staged** behind
`editor-sections` (#40) and K1 merged (`[human, 2026-10-05: "Please schedule that todo following PR#40 as appropriate."]`; A-63); re-seal at
dispatch. The facility-tree facts (F6, F7) are the Advisor's measurements of 2026-10-04 and the Integrator's to re-measure.
**Dispatched 2026-10-05 stacked on `feature/editor-notes-and-report-spelling` @ `779f787`** (K1's PASS, I-39/PR #43) under the stacking-by-
file-overlap rule (A-69): re-sealed there — four cited files blob-identical, `settings_document.py` definitions at the same lines, F5's
`load_settings`/`save_settings` moved to `:1186-1228`; the Notes adopt K1's `file_spelling`. The human's "following PR #40" holds: the stack
merges #40 → #43 → this. Developer: RED `f4f6a4c`, GREEN `e49fc05`, battery `4374f89` (48 rows; a sidebar-persistence defect found and fixed; D-52).
**Rejected** at `review/editor-ipts-inference` @ `e0a7e72` (the Integrator's `todo.md`) — tests only.

### v2 — 2026-10-05 (attempt 2 of 3; the work order for `triage/editor-ipts-inference-v2`)

**Rejection.** `review/editor-ipts-inference` @ `e0a7e72` — `todo.md` at that commit (Integrator, Claude Opus 5.5): *"Verdict: REJECT — tests
only. The behaviour passes every reviewer and the deployment-shaped acceptance on the real tree; two declared behaviours have no test that
fails when they break, and one of them guards the human's own flow. Stacked on `feature/editor-notes-and-report-spelling` (#43 @ 779f787,
which contains #40). Not infrastructure."* What passed (**the Developer does not redo it**): gate 650 + 789; the Integrator's acceptance on the
real `/SNS/REF_L` tree (the from-scratch file → `IPTS-36119` shown as Changed, Load 0.09 s; the copied `IPTS-36574` file keeps `IPTS-38511`
with a Note that its runs resolve under **`IPTS-36970`**; two-IPTS runs → the first's + a Note; the dialog under the IPTS with the three-folder
sidebar); ui-aspects PASS (I1 2a–2d, I3–I6 driven; the user's saved sidebar byte-identical; an unmounted root → the "not available here" Note);
design PASS; security advisory clean; every §7 row killed.

> **BLOCKING — B-1: I1's order "runs (2a) before the field (2b)" has no test; a faithful swap survives (rule a/b; reachable).** Reproduced:
> moving the `held = _clean_ipts(field_value)` block above the runs block in `resolve_experiment_id` → **1164 passed**. On a fabricated tree
> with runs 229197–229199 under `IPTS-36119`: `from_dict({"experiment_id": "", "RBnum": [229197, 229198, 229199]}).resolve_ipts("IPTS-1",
> root=tree)` → **`IPTS-1`** under the mutant (`IPTS-36119` at 4374f89). No test has runs that resolve **and** a header that held another IPTS.
> **This is the human's flow:** a previous file leaves `IPTS-1` in the header, the from-scratch file is loaded — the mutant keeps `IPTS-1` and
> the reducer cannot find the NeXus files. **Fix (tests; domain = I1's five steps):** a U2 case "runs resolve, field held `IPTS-1` → the
> runs' IPTS" and a V2 leg through Load; a battery row for the runs↔field swap.
>
> **BLOCKING — B-2: "the remembered folder is still written after a Load and a Save" (I5) has no test (rule a).** Deleting
> `self.settings.setValue("settings_editor_dir", …)` survives in `load_settings` (1163 passed) and in `save_settings` (1163 passed); no test
> reads the value back — V5 only presets it. **Fix (tests):** assert `settings_editor_dir` after `_load` and after `save_settings`.

**What the plan missed (the Analyst's defects).** (1) I1 declared an **order** and §6 pinned each step but never a *collision* — the one state
where the order decides (runs resolve **and** the field holds another IPTS) was not a row; the campaign's lesson once more: enumerate the
cells where two rules compete. (2) I5's "the remembered folder is still written" was a declared outcome with no read-back test. (3) The
test reviewer's findings on the plan itself, corrected in v2: §8.3 expected `IPTS-36574` where the runs are under `IPTS-36970`; row 14
("clears the field" → Changed) is wrong when the seed held `""`; the types table listed `""` as the only empty IPTS, while real files hold
`null` or no key (10 of 104) and a spaces-only value is a second definition of empty — with `validate()` silent and `base_path` raising.

**Changes in v2.** (1) U2/V2 gain the collision row through `resolve_experiment_id` **and** through `load_settings` (B-1); a mutation row for
the swap. (2) V5 reads `settings_editor_dir` back after Load and after Save (B-2); a mutation row per slot. (3) I4's "empty" is one definition —
`""`, `None`, whitespace-only — **the only production change in v2** (one condition), with U3 rows. (4) **Design A3 adopted:** resolution runs
in `load_settings` only, never in `set_document`/construction — an injected document with runs does no facility lookup (V2 leg, counter 0),
and a re-adoption cannot re-infer after a clear (I6). (5) U2's rows assert all three columns; the Notes render values through
`file_spelling` (§2). (6) §3 row 14 corrected; §8.3's expected IPTS corrected to `IPTS-36970`. Advisories to the PR body (design A1 — a no-edit
Load → Save now writes the inferred IPTS, the declared intent, stated plainly; A2; A4 cold/warm lookup cost and the cap comment; A5–A7; ui
A1–A6 — the "why the IPTS appeared" line is worth a K3-era follow-up, not this gate; security F1–F4 — F1's quadratic dedup is a
one-line `dict.fromkeys` the Developer may take, F4 a `None` remembered folder tolerated). **Unchanged:** I2, I3, I5's folders, I6, I7, F1–F8,
the base (`feature/editor-notes-and-report-spelling` @ `779f787`; the Developer continues on `feature/editor-ipts-inference` from `e0a7e72`).
**Retry arithmetic:** attempts_done = 1 + 1 = 2 → v2 is attempt 2 of 3; a third rejection escalates.
