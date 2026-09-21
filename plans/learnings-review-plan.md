# Plan: learnings-review (mid-campaign) — synthesize what the campaign learned, and land the one code change it warrants

**Campaign:** `exp-settings-roi` · base `exp` · **independent of T3** (runs parallel to
settings-management-v6; different surface) · dispatched 2026-09-19 as a **"have fun"
bounded experiment** on the brink of an Analyst compaction (see the experiment note
at the bottom). **Retry attempt:** 1. Expect ≥1 review cycle (verify-prose scrutiny of
the synthesis claims is designed in).

## The ask (human, 2026-09-19)

The campaign has run a very long time. Review **everything** it has learned, using the
new comms (tasking files, self-push, PRs) to engage all seats, and — **if the review
finds code should be adjusted** — land it as a PR on `lr_reduction`.

## Charge (Developer)

1. **Read the corpus** (on analysis unless noted): the ~18 `plans/*-learning.md`; the
   escalations (`plans/settings-management-escalate.md` history); the tasking register
   (`tasking/plan/todo-*.md` with their new `Route:`/`Owner:`) and amendments 11–20;
   the per-slug rejection records (Integrator `todo.md` tips).
2. **Write the synthesis** — `plans/campaign-learnings-synthesis.md` — organised by the
   campaign's recurring **defect classes**, not slug-by-slug: e.g. vacuous guards
   (→ amendment 16), precondition≠payoff (unwired mechanisms), non-extractable-fixes-
   rebreak, prescription-vs-types (→ amendment 18), the per-angle trap family
   (active-row / equalise-angles / edit-time-freeze), liveness/delivery fragility
   (→ amendment 17). For each: what it was, what closed it, what residue remains.
   **verify-prose (amendment 16 sibling): every claimed lesson cites its evidence**
   (slug + SHA or todo file); a lesson without a checkable citation is dropped.
3. **Decide the code question.** From the synthesis + the parked **product-defect**
   todos (Route: slug), determine whether there is a **single-review-surface**
   (§4 sizing), **evidence-backed**, **not-already-done** code adjustment in
   `lr_reduction` that the accumulated learnings most warrant. If yes, implement it on
   `feature/learnings-review` with a **mutate-once-guarded** test (record the mutation
   → red per amendment 16, frame-first). If no, say so explicitly with reasons — the
   synthesis alone is then the deliverable.
4. Keep the diff to the synthesis + at most one small code change. This is a review,
   not a refactor.

## Review domains (Integrator, charter §5)

**design-reviewer (blocking** — is the synthesis a faithful, non-overclaimed account of
the campaign's lessons?); **test-reviewer (blocking if code changed** — is the guard
real, mutate-once honoured?); **verify-prose gate** — spot-check the synthesis's
citations against the record; a lesson whose citation doesn't check is a blocking
finding. security-review advisory.

## Acceptance

- `plans/campaign-learnings-synthesis.md` present; every lesson cited to checkable
  evidence; organised by defect class; residue named.
- Either one small evidence-backed single-surface code change with a mutate-once guard,
  OR an explicit "no code change warranted" with reasons.
- `pixi run test-launcher` + `test-reduction` green if code changed; no `pixi.lock`
  change unless a code change requires it.
- Draft PR on pass — synthesis as the narrative, the code change (if any) as the diff.
  Merging stays the human's deploy decision (charter §7).

## Experiment note (why this slug exists, for the finding)

**Hypothesis:** the campaign machinery + amendment-19 comms + the compaction guards let
a dispatched meta-review run to a PR **autonomously across the Analyst's compaction
boundary** — the Developer/Integrator carry it via their Monitors (independent of the
Analyst session), and a post-compaction Analyst reconciles any review cycle from git
alone (amendment 17 processed-set + reconcile). **What to check afterward:** did v1 get
picked up and reviewed without the Analyst? did any rejection→v2 get handled by the
reconcile routine post-compaction? did it converge to a PR? Record the verdict
(including failure) in the campaign retrospective — a negative result is a valid finding.

## Revision history — v2 (after v1 review; 2026-09-19; review todo @ `30985822`)

v1 gate green at `2136a8f` (145 launcher + 246 reduction, EXIT=0) and the **blocking citation
gate PASSED** (72 items sampled, zero dangling, 92% semantic hit). **The code is correct — the
save-config-json fix stands.** REJECTED on **record accuracy + two guard gaps** (Integrator I-39);
5 of 6 blockers are prose, F1/F2 are ~12 lines of test + 2 ledger rows. Full findings: `todo.md`
at the review tip (`30985822`).

**Fairness (Integrator, recorded):** the synthesis was committed 8 min BEFORE the v6 rejection
landed (12:12:49 vs 12:21:27) — the two staleness blockers are transcription, not care; `d5733af`
(the v6 rejection) already holds the replacement language.

### Prose corrections (transcribe from ground truth — verify-prose, amendment-16 sibling)
1. **Section G:** v6 was **REJECTED → decompose**, not "fixed"; a fourth generation exists.
   Restate per `d5733af`'s mandated correction (the residue currently repeats the wrong sentence).
2. **Two attribution slips:** harness-hardening §2 dates amendment 16's rule three weeks before
   settings-editor §8 existed; the inaccurate test name traces to the Analyst's hedged plan —
   correct both to the record.
3. **Two tree-mismatch claims:** two byte-identical savers still in `src/` → the count is **3→3,
   not 3→2**; "nothing drives the reduction entry point" is **false** (a GUI checkbox does).

### Guard gaps (the two real test additions — amendments 16/18/21)
- **F1:** `make_json_safe` is an **unguarded removable clause that is load-bearing** on the GUI
  path (reproduce the `PosixPath` `TypeError`); add the guard + a mutation-ledger row.
- **F2:** the truncation guard asserts **no NEW file appears** — wrong axis. It must assert the
  **prior file SURVIVES** a failed save (a mutation that destroys previous settings currently
  passes all six guards). Re-point to the state that matters (**amendment 21:** vary the STATE —
  a failed write *over an existing file*).

### Acceptance (v2)
- The three prose groups corrected against ground truth; F1/F2 guards added with mutation-ledger
  rows (mutate → RED); `pixi run test-launcher` + `test-reduction` green; `pixi.lock` untouched.
- Draft PR on pass (synthesis + the standing save-config-json fix). Merging is the human's (§7).

Dispatched as `triage/learnings-review-v2`.

## Revision history — v3 (after v2's review; 2026-09-20; review todo @ `2ce6597`)

v2 REJECTED NARROWLY — "two tokens and four lines" (Integrator); v2's corrections all landed
accurately. Three narrow blockers, each with a finder-verified remedy:

- **B1 (one token):** the B1 correction re-attached `e1c0d63`, whose diff has ZERO
  `_record_edit`/`_session_edits` references — the generation-3→4 attempt is **`3d71164`**. v2
  appended the wrong SHA (from the sentence it replaced) under a "re-verified here" header. Fix the
  SHA `e1c0d63` → `3d71164`.
- **B2 (one token):** `np.float64` is a `float` subclass and JSON-native, so the numpy half of the
  fixture pins nothing (drop `make_json_safe` + revert the one Path anchor to `str` → 9 passed). Use
  a **non-JSON-native numpy type (`np.float32`)** so the fixture actually pins `make_json_safe`.
  (Amendment 16 applied to fixtures: each anchor must red **independently**, not just the aggregate
  — the Integrator records its own v2 verification missed this.)
- **B3 (four lines):** all three bad params raise `AttributeError` on `config.__dict__` **before**
  `json.dumps`, so the parametrisation pins "rejected before open," not the serialise-before-open
  clause. A mutation keeping the gate + removing only that clause → 9 passed while truncating a
  29-byte prior file to 546 bytes. Fix the test: a param that **passes the gate and reaches
  `json.dumps`**, asserting the prior file survives (amendment-21 state axis: failed-write-over-
  existing-file).

### acceptance (v3)
- B1 SHA corrected; B2 fixture pins `make_json_safe` (each anchor reds independently); B3 test
  exercises serialise-before-open (prior file survives). `pixi run test-launcher` + `test-reduction`
  green; `pixi.lock` untouched. Draft PR on pass.

Dispatched as `triage/learnings-review-v3`.
