# Decision request — `landing-l3-launcher`: the suite runs `scripts/test/roi_estimate_mutations.py`, which D-3 excludes

`[Developer, decision-request; filed 2026-10-20 (D-100); for the Analyst to route — D-3 is the human's ("kept if the human wants the mutation batteries upstream")]`

**The conflict.** L3's Declared scope requires (4) "the gate green on its own" and lists `scripts/test/**` as **Explicitly OUT** (D-3's default).
Both cannot hold: #44 (`e7b8524`) shipped `scripts/test/roi_estimate_mutations.py` **with tests that run it** —
`tests/unit/lr_reduction/test_roi_estimate.py:479` (`_BATTERY = … "scripts" / "test" / "roi_estimate_mutations.py"`), `:586`, `:626`.

**Measured** (L3 v1 built locally, tip `320d273`, not pushed; the literal gate command from the tip, 03:31–03:39Z):
launcher **801 passed**; reduction **3 failed**, 1098 passed, exit 1 — exactly
`test_the_battery_table_lists_the_rows_it_runs`, `test_the_mutation_battery_refuses_a_dirty_baseline`,
`test_a_sigterm_during_the_battery_leaves_the_module_restored`, each `FileNotFoundError: …/scripts/test/roi_estimate_mutations.py`.
Everything else holds at `320d273`: P3 (the stack's proof vs R) passes (a) and (b); P4 0 UNASSIGNED; P1, P2, trailers clean.
The other excluded battery, `scripts/test/measure_fit_path_dependence.py`, has no test consumer (one comment names it:
`tests/test_scaling_factors_workflow.py:25`).

## Options (robust first)
**A — keep #44's battery in L3 (recommended).** Replay `scripts/test/roi_estimate_mutations.py` and `scripts/test/README.md` with #44 (D-3's
alternative, applied to the one battery the suite runs). The upstream branch then carries a battery *and the tests that keep it honest*, as the
fork does. Changes: L3's set gains those two paths; the exclusion list (`EXCL` in `landing-purity.sh`, single source) becomes
`.github/workflows/test_and_deploy.yml` + `scripts/test/measure_fit_path_dependence.py`; the sanitize check's `^scripts/test/` artefact rule
narrows to the excluded file. The tip's test files stay the fork's (no behaviour change). Cost: one more file type upstream reviewers see.
**B — drop the three battery tests in L3.** A behaviour change to a replayed file (the plan's "Explicitly OUT: behaviour changes"); L3's
`test_roi_estimate.py` would differ from R, so it joins the exclusion list too. Not recommended: it removes the guard on a tool that stays in the fork.
**C — leave it red.** Breaks "green on its own"; not a PASS.

Either A or B is a plan revision (v1 → v2 of this leaf, or an amendment at build like A-130) plus the script set change; the Developer then
re-runs the driver (`scripts/landing-l3-drive.sh`, 2 min) with the decided pathspecs and continues to `qa/`.
**Advisory either way:** `tests/test_scaling_factors_workflow.py:25`'s comment points at a file the layers do not carry.

## Resolution `[Analyst, 2026-10-20, A-136]` — **A**, as the plan's own amendment; reversible by the human

D-3 was this seat's default ("defaults in force unless the human says otherwise before dispatch"), and its premise — "campaign verification tooling;
upstream has no consumer" — is measured false for `roi_estimate_mutations.py`: the suite consumes it. A default whose premise the build refutes is the
plan author's to correct, not a scope change: A keeps every replayed file equal to R, edits no test, and keeps the fork's guard on its own tool. The
other battery has no consumer and stays excluded. Changed with the ledger commit of A-136: `EXCL` (two paths), the sanitize rule, L3's allow set and
entry 13 (whole), the proof's pathspecs and its strict (b). **If the human wants no battery upstream**, that is B — a scope word ("drop the three
tests") and a v2 of this leaf; nothing pushed changes either way. The Developer re-runs `scripts/landing-l3-drive.sh` with entry 13's pathspec widened
and continues to `qa/`.
