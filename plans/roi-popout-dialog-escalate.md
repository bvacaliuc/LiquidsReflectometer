# Escalation: `roi-popout-dialog` — rejected three times at the review gate; production right on real data every time; the retry cap is reached

**Campaign:** `exp-review-fixes` · **Leaf:** `roi-popout-dialog` (R2) · **Status:** ESCALATED 2026-10-06 (attempt 3 of N = 3 rejected at
`21a7367`, `review/roi-popout-dialog` @ `ad3558c`, I-50) · **Decision owner:** the human (one cap extension is delegable to a proxy "only
after the Integrator's decompose recommendation has been considered and the reason written in the posture line" — posture §envelope; the
posture declares **no proxy**, so the extension is the human's; a second extension is never delegable) · **Canonical record:** this file (ledger
`plans/roi-popout-dialog-escalate.md`, byte-identical on `analysis/exp-review-fixes`); the annotated tag `review/roi-popout-dialog-escalate` on
the fork points at the rejected tip `ad3558c` · **Plan:** `plans/roi-popout-dialog-plan.md` v3 (`f868c6e`) · **Branch:**
`feature/roi-popout-dialog` @ `ad3558c` (= `21a7367` + the Integrator's `todo.md`), stacked on `feature/roi-popout-data` @ `f424aec` (#44) with
K2's tip `8ca43ce` merged forward · **Human-visible state:** no draft PR exists for this slug; #44 (its base) is open at the human's gate.

## 1. What the human is deciding

Whether to grant **one cap extension** (a v4) for a slug whose **production code the Integrator has found right in all three gates** — the
deployment-shaped acceptance on IPTS-36119 (ledger `scripts/roi-popout-acceptance.py`, 53 checks) matched the stored monitor.sns.gov report
cell for cell at v1, v2 and v3 with identical numbers, the launcher gate 757 + reduction 874 green each time — and whose remaining defect is
**five declared clauses with no test that can fail** (the Integrator's estimate: "roughly six assertions and one byte of fixture, with no
production change"; one commit in the two test files).

## 2. Attempt synopsis

| Attempt | Tip gated | Rejection | What was wrong | Closed by the next attempt? |
|---|---|---|---|---|
| v1 (`791bdbe`, D-60) | `review/` @ `b22c8df`, I-46 | six declared behaviours with no failing-capable test (minor log formatter; `None` peak overlay; `useBS None/[]`; X/TOF drags; Cancel/OK as gestures; log toggle) + a false docstring ("no file is opened for writing") | v1 tests replaced gestures by their effects, read subsets of a domain, and left two states-table cells unpinned; the plan's F2 sentence and author list were wrong (P1, P2) | yes — all seven survivors red at v2 with recorded counts (I-48) |
| v2 (`e017a97`, D-62) | `review/` @ `088686c`, I-48 | two pins: a document save from the slot (E4′'s raising stub swallowed by `@guarded`; E9 wrote a 1 484-byte settings file into the cwd unseen) and `"aspect": "equal"` (Y-TOF box 273 × 1 px); both latent since v1 | a raising test double is blind inside an `except Exception` handler; B3's "aspect" clause had no pin | yes — M30 → 2 failed, M31 → 1 failed at v3 (I-50) |
| v3 (`21a7367`, D-64) | `review/` @ `ad3558c`, I-50 | five pins, all latent since v1, none named in the v1/v2 work orders: (B-1) the lookup writing `RBnum` even on Cancel; (B-2) `Normalize` for `LogNorm`; (B-3) the colorbars removed or swapped; (B-4) the "all angles" label; (B-5) a truncating write to the 0-byte run fixture | each gate sampled the declared clauses and found new latent gaps (7 → 2 → 5); no round audited every clause against its pin | — (the cap) |

The Developer's record is clean at every attempt: plan tests written RED by mutation first, the whole battery re-run and attributed row by row
(136 → 158 → 160 rows), the Integrator's own reproduction commands run against the tree before each `qa/` (v3: M30 → 2, M31 → 1). The failure
is in **the specification side's coverage**, not in the build.

## 3. Why the loop did not converge (the Analyst's reading, agreeing with I-50)

1. **The plan declared behaviours faster than it pinned them.** §3 B1–B12 and the types table name ~40 clauses; §6 named 23 tests. The v2 audit
   "every cell names its test" was run over the *types table* and missed clauses inside the B-rows ("log norm", "colorbar", "labelled 'all
   angles'", "aspect left to the data") and §5's must-nots ("RBnum written"). A clause inside a prose row is a declared behaviour exactly as a
   table cell is.
2. **Each gate sampled.** The Integrator states this plainly (I-50: "this seat should have run a clause-by-clause pin audit at v1"; filed
   `todo-gate-declared-clause-pin-audit.md`). Sampling finds *some* unpinned clauses each round, so a three-round cap is consumed by discovery,
   not by failure to fix.
3. **The two seats fixed exactly what was named, each round.** v2 and v3 closed every named item on the first try. Nothing named was ever
   re-rejected. The cap measures the gap between "clauses declared" and "clauses named in a work order", not the Developer's or the plan's
   ability to close a named gap.

## 4. Clause-by-clause pin audit at `21a7367` (what I would have put in front of v4 — and what v1 should have had)

Read-only, from the test files at `21a7367` (`launcher/tests/test_roi_dialog.py`, `test_settings_editor.py` §Select ROI) and the Integrator's
three work orders. **Pinned** = a test observes the clause through the path a mutation of it breaks; **I-50** = one of the five open blocks;
**unpinned?** = I find no test naming the clause — a candidate for the same treatment, to be confirmed by the mutation, not by reading.

| Clause (§3 / §5 / types) | Pin at `21a7367` | Status |
|---|---|---|
| B1 button placement, enabled iff a current row | `test_select_roi_is_enabled_only_with_a_row_selected`; M6 | pinned |
| B1 row captured at the click | `test_select_roi_writes_the_row_it_was_opened_for`; M1 | pinned |
| B2 file from `RBnum` when set and present; else ask; start dir resolved else last used; cancel does nothing | `test_the_run_file_comes_from_the_row_or_is_asked_for` (legs) | pinned |
| B2 **a cancelled dialog leaves the document unchanged, incl. `RBnum`** (§5 "RBnum written" must-not) | none — E4″/E6 never compare `doc.to_dict()`; E3/E9 stub the lookup | **I-50 B-1** |
| B2 read failure → panel, not fatal, not modal | `test_an_unreadable_run_is_reported_not_fatal`; M5 | pinned |
| B3 two images + three profiles | `test_the_dialog_draws_two_images_and_three_profiles` | pinned |
| B3 arrays unmodified, `origin="lower"`, extent on pixel centres | `test_the_images_are_the_data_layers_arrays`; M14 | pinned |
| B3 **log norm** | none — no test reads `image.norm` | **I-50 B-2** |
| B3 **colorbar per image, beside its own image** | none — the loop body → `pass` survives (5 axes for 7) | **I-50 B-3** |
| B3 aspect left to the data | V2′ (`get_aspect() == "auto"` at open and after a draw); M31 | pinned (v3); I-50 advisory: not after an interaction |
| B3′ Y-TOF x limits = TOF edges; TOF/X profile limits | `test_the_profiles_and_the_ytof_image_open_on_their_data`; M26/M27 | pinned (v2) |
| B4 overlays = `background_bands`; `data_x_range`; TOF window when present; on every plot with the axis | `test_the_background_overlay_is_what_the_reducer_averages` (M7); `test_a_typed_value_moves_its_overlay_on_every_plot`; `test_the_reductions_tof_window_is_drawn_when_the_row_has_one` | pinned |
| B5 unusable background → "not set" + reason; `useBS` off → drawn, "not subtracted"; `None`/`[]` → on | `test_an_unusable_background_is_shown_as_not_set_with_its_reason`; `…does_not_subtract_is_drawn_and_labelled` (5 legs); M19 | pinned (v2) — I-50 advisory: V14 lacks `[]`/3-number/3-4-zero legs |
| B6 Y drag (peak/low/high), X drag, TOF drag | `test_dragging_on_the_y_profile…` (3 legs); `test_dragging_on_the_x_and_tof_profiles…`; M20–M22 | pinned (v2) |
| B6 typed values; Estimate; log toggle | V5; V9/V10; `test_the_log_toggle_switches_every_profile` (M25) | pinned |
| B7 Estimate via the data layer; refusal → message, no value change | `test_an_estimate_refusal_is_a_message_not_a_guess` (M9); `test_estimate_sets_a_background_the_reducer_accepts` | pinned |
| B8 view filter drives the profiles and the XY image; TOF profile + Y-TOF over the full span | `test_each_plot_is_the_data_layers_for_the_ranges_shown`; `test_the_view_filter_is_never_reported` (M8) | pinned |
| B8 **filter starts at the chopper band when the run has a chopper log, else the full span** | no dialog test names `chopper`/`lambda_to_tof` (the editor file mentions them in docstrings only) | **unpinned?** — confirm by mutation (start at the full span regardless) |
| B9 OK reports only what changed; the tab writes exactly those via `set_angle_field`/`set`; refresh × 3 | `test_ok_reports_only_what_changed` (M2); E2 (M3); `test_an_x_range_change_updates_the_scalar_and_its_editor` | pinned — **except the three `refresh_*` calls**: no test names `refresh_angles`/`refresh_scalars`/`refresh_report` (E8 may observe `refresh_scalars` through the editor; `refresh_report` unobserved) — **unpinned?** |
| B9 **"all angles" label on `data_x_range`** | none | **I-50 B-4** |
| B9 untouched `[a, b, 0, 0]` / unset stays byte-for-byte | E2's `[137, 149, 0, 0]` leg; `test_an_edited_background_is_reported_when_the_rows_own_would_draw_otherwise` | pinned |
| B10 OK unavailable for empty/inverted peak or partial background; a written background is four ascending non-zero ints | `test_ok_is_unavailable_for_an_inverted_peak_or_a_partial_background` (M15); `test_a_background_edited_into_one_the_dialog_cannot_write_waits_with_the_reason`; `test_a_reversed_range_is_named_and_ok_waits` | pinned |
| B11 a nudge moves artists, rebuilds nothing; images recomputed only when their inputs change | `test_a_nudge_moves_artists_and_rebuilds_nothing` (M13 → 5/6) | pinned for the rebuild; **"only when their own inputs change"** (e.g. a peak nudge must not recompute the XY image) — no test counts recomputations — **unpinned?** |
| B12 `parse_math=False` on file text; plain formatters on log axes **and colorbars** | `test_file_text_and_log_ticks_never_reach_the_math_parser` (M10, M17, M17b) | pinned for the axes; the colorbar leg is **vacuous while B-3 is open** (I-50) |
| B12 `deleteLater()`, never `destroy()` | `test_the_dialog_is_released_not_destroyed` (M16) | pinned |
| §5 long run sub-sampled, title says so | `test_a_sampled_run_says_so_in_its_titles` | pinned |
| §5 zero events → empty plots, Estimate refuses | `test_a_run_without_events_draws_empty_plots_and_estimate_refuses` | pinned |
| §5 selection moves between click and OK → captured row written | E2 | pinned |
| §5 row index invalid at OK → panel | — (the `@guarded` slot; `test_an_error_inside_a_slot_is_a_status_line_not_an_abort` covers the dialog's slots, not the editor's row-index case) | **unpinned?** |
| §5 matplotlib Qt backend missing → button disabled with a tooltip | `test_select_roi_without_matplotlibs_qt_backend_is_disabled_and_says_why` | pinned |
| F2 no settings/data file written; the one QSettings key; **no truncating write to the chosen run** | E4″ + E9′ (M28, M29, M30) — but the run fixture is 0 bytes, so a truncation is invisible | **I-50 B-5** (one fixture byte, or `(size, mtime_ns)`) |
| F3 no geometry literal | `test_geometry_follows_the_events_not_a_literal` (M12); `test_the_dialog_carries_no_geometry_literal_and_reads_no_file` | pinned |

**Count:** 5 open blocks (I-50) + **4 "unpinned?" candidates** (B8's chopper start, B9's three refreshes, B11's "only when their inputs
change", §5's invalid-row-at-OK) that a v4 should settle by mutation before `qa/` — not by reading. If all four turn out pinned through a test I
did not credit, the table says so and the record is complete; if any survives, v4 pins it in the same commit. **This table is the artefact the
plan lacked at v1**; the Integrator's `todo-gate-declared-clause-pin-audit.md` is the gate-side half of the same fix.

## 5. Options for the human (the robust one first)

| Option | What happens | Risk | Cost |
|---|---|---|---|
| **A — one cap extension; v4 = tests only, scoped by §4's table (recommended)** | the Analyst writes plan v4: §6‴ with the five I-50 pins **and** the four "unpinned?" clauses settled by mutation (each either credited to an existing test or pinned), §7‴ with M32–M40, the two I-50 docstring/aspect advisories folded (cheap); the Developer continues on `feature/roi-popout-dialog` @ `ad3558c`; the Integrator gates with the clause table as its checklist (every row has a verdict, so the gate cannot sample) | a fifth gate finds a clause the table missed — then the table was wrong and the record says where | one Developer round (the three so far: 5.7 h, 4.5 h, ~4 h) + one gate; the Integrator seat is a successor after 07:00 EDT (patch day), which may re-gate once |
| **B — merge-as-is route: the Integrator opens the draft PR on #44 from `21a7367` with the five pins recorded as a follow-up todo** | the dialog scientists can use lands with #44; the five pins become `todo-roi-popout-dialog-missing-pins.md` → a `fix/` slug in the next campaign | I-50: "a later regression in the colour scale, the colorbars, the lookup's writes or the label could land unseen"; the protocol has no "PASS with debt" verdict — this needs a `[human]` line reclassifying the five blocks as advisories (the envelope allows the proxy/human to "reclassify under the termination rule — loosen only for findings outside declared scope" — **these are inside declared scope**, so this is the human's call alone, not a proxy's) | zero build time; a rule exception on the record |
| **C — decompose** (the envelope's decompose check) | split "the five pins" into its own slug `roi-popout-dialog-pins` stacked on `feature/roi-popout-dialog`, dispatched fresh with N = 3 | the same work as A under a new name; the cap is honoured in letter, not in spirit — I do not recommend it, and I-50 recommends no decomposition either ("one commit in the two test files; no production line moves") | one round |
| **D — stop** | the branch stays on the fork unmerged; item 9 of the scientists' requests is not delivered this campaign | the data layer (#44) merges alone and is useful; the dialog waits for the next campaign | none now |

**The decompose check, considered:** the Integrator's recommendation (I-50, "Smallest completion") is that the remaining work is six assertions
and a fixture byte in two test files, with no production change — a decomposition would create a slug smaller than any in the charter and
would not change what has to be written. Reason for the posture line, if the human grants A: *"extension granted: decomposition considered and
declined — the remaining work is tests-only in the slug's own two files (I-50 §Smallest completion); the gate sampled clauses in three rounds
(7 → 2 → 5, all latent since v1) and v4 carries the complete clause table (`plans/roi-popout-dialog-escalate.md` §4) so it cannot sample."*

## 6. What I would have tried next (if the extension is granted — ready to dispatch within the wake it arrives)

Plan v4 = v3 + §4's table as a new §6‴/§7‴: for each I-50 block the Integrator's own fix text (E4″/E6 compare `doc.to_dict()`; V2 asserts
`isinstance(image.norm, LogNorm)`, 7 axes, each colorbar's `ax` beside its image by bbox; E8 asserts "all angles"; the run fixture one byte or a
`(size, mtime_ns)` snapshot), plus the four candidates settled by mutation, plus the I-50 advisories that are one line each (`QTest.qWait(0)`
before the disk asserts; the aspect check repeated after a TOF drag in V4′; the docstring's exact scope). No production line. The Developer's
recipe unchanged: RED by mutation, GREEN, the whole battery, the Integrator's commands against the tree, `qa/`.

## 7. Learnings for the ledger (routed by the Administrator; recorded here first)

- **L10 — declared ≠ pinned; audit the clauses, not the tables.** A plan's §3 is prose; every verb phrase in it is a declared behaviour. The v2
  audit covered the states *table* and missed the B-row clauses that cost v3. The fix is structural: the plan carries a clause → test → mutation
  table (this file's §4 shape) *before* dispatch, and the gate checks the table, not a sample (I-50's `todo-gate-declared-clause-pin-audit.md`).
- **L11 — a cap of three is consumed by discovery when the gate samples.** Three rounds closed every named item first time; the cap was spent
  finding what no round had named. A cap is a measure of specification completeness as much as of build quality.
- **L12 — the right escalation record is a decision table with the audit attached**, so the human's extension decision is informed by *what
  remains* (a finite list) rather than by *how many times it failed*.

## 8. Tag text (`review/roi-popout-dialog-escalate`, annotated, idempotent)

> roi-popout-dialog ESCALATED at the retry cap (v3 @ 21a7367 rejected, review @ ad3558c, I-50): production right on IPTS-36119 three times;
> five declared clauses unpinned (RBnum on Cancel; LogNorm; colorbars; "all angles"; truncating write vs 0-byte fixture) — tests only, ~six
> assertions + one fixture byte. Decision: the human's (one cap extension, delegable only to a proxy — none declared). Record:
> ledger plans/roi-popout-dialog-escalate.md (clause-by-clause pin audit §4; options §5, A recommended).
