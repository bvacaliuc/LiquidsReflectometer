# Integrator review gate — `port-overplot-axes-refresh` v1 REJECTED

**Disposition: blocking.** Tests are green; this rejection is entirely from
the review gate. Both plan-declared reviewers ran once on the feature diff
and **independently converged on the same defect**; the ui-aspects reviewer
found three more. I verified all four in source myself before rejecting —
each is cited with the evidence below.

## Departure from the plan's declaration, flagged

The plan declares `ui-aspects-reviewer (advisory)` and `test-reviewer
(advisory)`, and I honored exactly that in S0 and S1, where the findings
were quality opinions. I am departing here, deliberately, because what the
reviewers found is not a preference about how the work is written — it is
that **the feature does not do what the slug exists to do on real data**,
and that it introduces two new regressions. Charter §5 ties the blocking
disposition to bug-fix phases, which this is: the slug's stated purpose is
to stop the axes lying, and on every real reflectivity file in this repo
the axes still lie — differently, and in one case worse.

If the Analyst judges the advisory declaration should stand, the override
is cheap and I will not re-litigate it: re-tag `qa/port-overplot-axes-refresh`
at an unchanged SHA and I will open the draft PR with all of this recorded
as advisory notes in the body instead.

## B1 — `classify_file`'s 10-line window misses every real reflectivity file

`launcher/apps/overplot.py:59-72` reads `for _ in range(10)`. Real REF_L
reduced output written by `src/lr_reduction/output.py:236` puts the
`# Q [1/Angstrom] ...` marker *after* the metadata preamble and one
`# <DataRun> <NormRun> ...` line per stitched angle.

Verified by the Integrator against this repo's own data — 1-based line
number of the marker:

```
tests/data/reference_short_nobck.txt              line 13
tests/data/REFL_201282_*_partial.txt  (7 files)   line 14
tests/data/REFL_198382_combined_data_auto.txt     line 14
tests/data/reference_rq_201282.txt                line 18
tests/data/reference_rq.txt / _avg / _fbck        line 19
tests/data/reference_rq_avg_overlap.txt           line 20
launcher/tests/data/refl_fixture.txt              line 2   <- the only hit
```

**Every real reflectivity file classifies `unknown`; only the 7-line
synthetic fixture written for this PR classifies `reflectivity`.** Direct
beam is asymmetric: `direct_beam_maker.py` puts its marker on line 8, inside
the window, so DB *is* detected — which is what makes B2 bite.

User-visible: point Overplot at a real autoreduce directory, check a
`REFL_*.txt`, Plot. Before this branch: axes `Q`/`R`, `R*Q^4` selectable and
working. After: axes `x`/`y`, `R*Q^4` greyed out (`overplot.py:502`) and
silently reset to `None` (`:379-380`). **The primary case is strictly worse
than before the slug.**

Fix: scan the whole leading comment block (`while line.startswith('#')`,
capped) rather than a fixed 10 lines, and match a marker *set* — note
`src/lr_reduction/save_reduced_data.py:54-56` writes
`columns = Q, R, dR, dQ (sigma)`, a second reflectivity writer that
contains neither current marker at any line.

Test that was missing (add it, watch it go red first): parametrize
`classify_file` over the real `tests/data/REFL_*.txt` and `reference_rq*.txt`
and assert `== "reflectivity"`. A synthetic 7-line fixture cannot stand in
for the format the tab actually consumes.

## B2 — one recognized DB file drags a whole mixed selection onto λ/I axes

`overplot.py:400-406`: `kinds = {k for k in per if k != "unknown"}` drops
`unknown` *before* the homogeneity test. Combined with B1 (real
reflectivity → `unknown`, real DB → `direct_beam`), a selection of one real
direct-beam file plus N real reflectivity curves gives `kinds ==
{"direct_beam"}`, `len(kinds) == 1`, so `sel_mode = "direct_beam"` for
**all** of them.

Genuine R(Q) curves are then drawn under `λ [Å]` / `I` (`:507`, `:548-549`).
No warning fires — the override-mismatch dialog (`:490-499`) only runs for an
explicit combo choice, and the `[kind]` legend suffix (`:524`) only fires for
`mixed`. This is worse than B1's `x`/`y`: it is a **confidently wrong axis
label on real reflectivity data**, the exact class of figure a reader takes
at face value.

Fix: treat `unknown` as a kind for the homogeneity test — any heterogeneity,
including unknown-vs-known, must fall back to `x`/`y`.

## B3 — Refresh ignores selection-only rows: stale plot, reported as refreshed

`plot_selected()` plots rows that are checked **or** highlighted
(`:471`), and the list is `MultiSelection` (`:131`), so a plain click
highlights without ticking. `refresh()` snapshots and restores `checkState`
only (`:292-296`, `:310-313`), and the rebuild destroys the items, losing
selection; the replot gate (`:319`) is computed from checks alone.

So: highlight three rows (no boxes ticked) → Plot → three curves → Refresh →
`pre_checked` empty → **no replot**, `dropped` empty → **no dialog** — but
`:315-317` stamps `overplot_last_refresh` and updates the tooltip to
"Last refreshed: <now>". The canvas shows pre-refresh data while the UI
asserts the folder was just re-read. On a live autoreduce directory that is
silently stale science on screen — precisely what PR #10 exists to prevent.

Fix (robust form): make the checkbox the single notion of "chosen" and have
row clicks drive `checkState`, retiring `isSelected()` as a hidden input.
The weaker alternative is to snapshot and restore both and gate the replot
on the union.

## B4 — constructing with an unreachable folder erases the saved folder path

New regression on this branch. `__init__` unconditionally calls
`_on_plot_mode_changed(...)` (`:227`), whose last statement is
`save_settings()` (`:390`). `read_settings` only populates `folder_edit`
when `os.path.isdir(_folder)` (`:230-233`). So if the saved folder is on
`/SNS` and the mount is not up at launch, the field is empty and
`save_settings()` writes `overplot_folder = ""` — **the user's stored path
is destroyed by opening the app before the mount came up**, and remounting
does not bring it back.

On `exp` today `save_settings()` is reachable only from `choose_folder`,
`folder_changed`, and `plot_selected` — all after a valid folder exists.
This branch adds the `__init__` path.

Fix: drop `save_settings()` from `_on_plot_mode_changed` (persist the mode
where the other settings are persisted), or make `save_settings` skip
`overplot_folder` when the field is empty. Note `:246` also stores the
folder unstripped while `:287`, `:355`, `:478` all `.strip()` — worth
aligning in the same pass.

## Test status: green, and that is part of the finding

`pixi run test-launcher` 17 passed (harness 2 + this slug's 15);
`pixi run test-reduction` 107 passed in 540.43 s, exit 0. No test
failures, no infrastructure problems. The suite is green **while B1-B4 are
all live**, which is the second-order finding: the tests do not discriminate.
Named partial reverts that leave all 15 green (test reviewer, verified list):
the popout label path (`:592-593`) can be reverted to `'x'`/`'y'`; check-state
restore can be swapped from name-keyed to index-keyed; the filter-honoring
rebuild (`:307`) can be dropped; `_set_rq4_enabled(...)` can be hardcoded
`False`; the whole explicit-override block can be deleted; the `[kind]`
legend suffix can be deleted; `refresh_btn.clicked.connect` can be removed
entirely (no test clicks the button). `test_refresh_no_folder`
(`test_overplot_refresh.py:31-38`) asserts the value it just set and passes
even if the no-folder guard is deleted.

## Suggested v2 order

1. B1 first — it is the root cause that makes B2 reachable on real data, and
   its guard test (real headers) is the one that would have caught this.
2. B2, B4 — both small and independent.
3. B3 — decide the "chosen" semantics deliberately; it is a design choice,
   not a patch.
4. Then the discrimination gaps above, at least: real-header classification,
   the popout label path, a sort-order-shifting insert for check
   preservation, and a capturing patch in `test_refresh_no_folder`.

## Advisory, not blocking (record, do not gate on these)

`R*Q^4` is silently reset to `None` when disabled and never restored, so a
user's transform choice is consumed by plotting one DB file (`:378-380`) —
this gets worse when S3 lands the `overplot_ytransform` save half, so flag it
to S3. Check state has no memory across a disappear/reappear cycle. The
pyplot fallback path leaks a figure per Refresh (`:555`, no `plt.close`).
`R · Q⁴` carries no unit while the xlabel does. `_last_sel_mode` exists only
for a test assertion. One modal warning fires *per* unreadable file during a
Refresh the user did not expect to be interactive.

## Confirmed clean by the ui-aspects reviewer (no action)

The `folder_label` → `folder_edit` adaptation is complete (zero survivors).
The S3 boundary holds — `overplot_ytransform` is read but never written.
Both label sites were converted. Signals are connected once in `__init__`
with no re-connect on refresh, so no multiply-firing. The embedded path does
`figure.clear()` + `add_subplot(111)`, so axes do not accumulate. No
`.destroy()` anywhere. The RED→GREEN A→GREEN B commit sequence is real and
its messages enumerate the actual failure strings.
