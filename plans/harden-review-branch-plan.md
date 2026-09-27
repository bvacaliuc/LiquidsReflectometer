# Plan: harden-review-branch — make `exp-review-with-197-with-fixes` safe for the user (F2 + mathtext + segregation guard)

**Campaign:** `exp-settings-roi` · close-out safety slug (human decision 2026-09-27). **Retry
attempt:** 1. **Base + PR target:** `agentic/exp-review-with-197-with-fixes` (NOT `exp`) — this is
the branch the scientists made available for weekend evaluation; the fixes must land *there* before
the user gets it. **New-workflow / launcher only — the old `template.py`/`reduction_template_reader`
reduction path is NOT touched** (that segregation is item 3, and it is guarded).

**Termination rule (adopted 2026-09-27):** the three items below are **demonstrated harm / a
user-visible embarrassment** → in declared scope. Anything a reviewer finds about the *corrections'*
prose/pins/coverage rides the PR body and does **not** re-open the slug. A finding of new
demonstrated reachable harm still blocks.

## item 1 (BLOCKING — data loss) — #197's settings builder truncate-writes the live file
`launcher/apps/json_settings_builder.py:1406` does `with open(file_path, "w") as handle: ...` — a
**truncating write** to the settings JSON, and #197 defaults the target to the live
`<IPTS>/shared/autoreduce/reduce_settings.json` the moment an IPTS is typed. A failed/interrupted
save (or a crash mid-write) **destroys the file autoreduction reads** — the F2 finding from the
pre-analysis, verified present on the branch this turn.
**Fix:** write atomically — serialize to a string first, write to a temp file in the same
directory, `os.replace(tmp, path)` (atomic on POSIX); add a **shared-path confirmation** before
writing under `shared/autoreduce`. (This is T2's `SettingsDocument.save` pattern; the *full*
re-seating on `SettingsDocument` is next-campaign — here, just the atomic write + confirm.)
**Guard (mutate-once):** a test that a save which raises part-way (patch `os.replace`/`json.dumps`
to raise) leaves the **prior file byte-intact** (amendment-21 state axis: failed-write-over-existing).

## item 2 (BLOCKING — console-spew / embarrassing) — matplotlib mathtext RecursionError on plot draw
`~/Desktop/todo-exp-review-with-197-traceback-1.txt`: `RecursionError: maximum recursion depth
exceeded` in matplotlib 3.9.4's mathtext (`_mathtext.py:_get_glyph`, repeated 872×), thrown from
`_draw_idle` while laying out a **tick/text label** — the GUI survives but spews on every redraw.
Cause: launcher plot text built from **dynamic NeXus data** is handed to matplotlib, which parses
`$…$` as math; a run title / label containing a `$` or a mathtext-pathological char recurses. Live
sites (all dynamic): `json_settings_builder.py:393` `set_title(f"{title} …")` (NeXus run title —
prime suspect), `:576` `set_xlabel(label)`; `overplot.py:611/655` `set_{x,y}label(xlabel/ylabel)`.
**Fix (class-level):** render **all plot text built from dynamic/user data with `parse_math=False`**
(matplotlib ≥3.7 accepts it on `set_title`/`set_xlabel`/`set_ylabel`/`Text`/tick labels), so
arbitrary strings never reach the mathtext parser. Keep intentional math labels (e.g. `$Q$
($\mathrm{\AA}^{-1}$)`) as static, well-formed literals. **Reproduce first:** run `new_launcher` →
Settings builder → load a run whose title contains a literal `$` (or synthesize one) → confirm the
recursion, then confirm `parse_math=False` silences it.
**Guard:** a headless test that sets a plot title/label to a `$`-bearing string and calls
`figure.canvas.draw()` (or `get_window_extent`) **without** raising `RecursionError`.

## item 3 (segregation guard — the scientists' concern, A) — prove the old path is untouched
The scientists want the campaign work confined to the **new** workflow. Verified this turn: the
settings model (`SettingsDocument`/`field_spec`/editor/builder/`reduce_settings.json`) is read only
by the launcher + the `new_`-prefixed reduction; the old `template.py`/`reduction_template_reader`
path reads none of it. **Add a guard that pins this boundary:** a test that reduces a fixture
through the **old** `template.py` path and asserts its output is **unchanged** by this branch (a
golden-value or a `reduction_template_reader.from_xml` round-trip), so any future settings/launcher
change that leaks into the old path reds. Document in the PR body: this slug's diff touches only
`launcher/**` + (item 1) the builder — **zero** old-path files.

## Out of scope (explicit)
- **The chopper 22.9% Q_max divergence** — it lives in `event_reduction.py` (shared, old+new) and
  changes R(Q); it goes to the **scientists** with the old/new-path question (does the −0.15 Å shift
  scale with chopper speed?), not into this slug. See `todo-chopper-bandwidth-four-values.md`.
- The full #197 re-seating on `SettingsDocument` (F1 array model, F4 `DetResFn='none'`), and F5 field
  coverage — **next campaign** (`settings-builder-on-document`). Item 1 fixes only the F2 data-loss.

## Acceptance
- Items 1–3 each with a mutate-once guard (fail → red on the real reproduction); `pixi run
  test-launcher` + `test-reduction` green; `pixi.lock` untouched. Diff touches launcher/builder
  only. **Draft PR targeting `exp-review-with-197-with-fixes`** on pass; merging is the human's.

Dispatched as `triage/harden-review-branch-v1`.
