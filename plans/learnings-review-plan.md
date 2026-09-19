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
