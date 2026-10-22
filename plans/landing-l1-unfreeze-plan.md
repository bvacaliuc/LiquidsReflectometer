# Plan: `landing-l1-unfreeze` — L1 changes once: #60 fast-forwarded, then one "unfreeze" commit whose tree is `7f0a4ad`'s plus the rename and K12's two reviewed tests, gated once; one Phase 2 against `R-final` with K6's `EXCL`; then L2–L4 staged upstream in order

**Campaign:** `exp-review-fixes` · **Leaf:** `landing-l1-unfreeze` (K21; refs `triage/landing-l1-unfreeze`, `qa/landing-l1-unfreeze`; the slug amends `feature/landing-l1-core` by a commit on top — no
rewrite; Phase 2 re-tags the stack with `-v5` names) · **Status:** **v2 DISPATCHED 2026-10-22 (A-210) — attempt 1 of N = 3 (a third rejection escalates) — on the human's word, couriered verbatim by the Advisor (V1-102; appended to `requests/l1-final-k12-unfreeze-one-phase2.md`, addressed to the Analyst): `[human, 2026-10-22 (to the Advisor, for the Analyst): "tell the Analyst to Dispatch K21 v2 (requests/l1-final-k12-unfreeze-one-phase2.md): the freeze leaves; keep K12's reviewed tests; K14 keeps its anchor with a rewritten guard; Phase 2 gating as normal."]`, confirmed to the Analyst in session (*"it is my word, act upon it"*); the four choices decided (D-7); Phase 0 folded into the Developer's delivery push (D-9); `triage/landing-l1-unfreeze` at the analysis commit carrying this plan; the Developer builds Phase 1 first (the unfreeze commit on `35f5489`, delivered as `qa/landing-l1-unfreeze`), Phase 2 after Phase 1's PASS; the overnight arrangement (V1-102): no seat pushes upstream or opens/closes a PR — upstream #219's fast-forward and #59's closure are the human's morning packet** — was: STAGED — v2 re-scoped 2026-10-22 (A-209) to the Advisor's request `requests/l1-final-k12-unfreeze-one-phase2.md` (V1-100,
written at the human's ask; audience: the human to decide, the Analyst to plan and dispatch on the word), not dispatched; the attempt count starts at 1 on the word** — "dispatch K21"
(or the route by name) addressed to the Analyst dispatches Phase 1 once Phase 0 (the human's #60 fast-forward) is visible on the fork; the request's four choices (§10 D-7) and D-5's
confirmations are read from the word · **Base:** L1⁗ = **`35f5489`** (#60's head, I-156) after Phase 0 · **PRs:** #60 merged by the fast-forward; #54 and upstream #219 fast-forward to
L1-final (the human pushes); #51/#52/#53/#55/#56 fast-forward in Phase 2; **#57 re-cut** (its guard); **#59 closes** (redundant); #58 forward-merged from L4-final; upstream #222 fast-forwards
to K10⁵ · **Reviews:** design, test (block) on the unfreeze commit's gate (the tree is gated content: `7f0a4ad` I-115, the rename I-13x/K17, K12's tests I-156 — their *combination* is
the unmeasured part); numerical-diagnostics n/a · **Gate:** Phase 1 — G at L1-final (the count it reports, against I-115's 172 at `7f0a4ad` and K12's nine; no warnings line; `pre-commit
run --all-files` green with every file linted), P1, P2 (`Restores:`/`Keeps:` accepted at dispatch); Phase 2 — per layer against `R-final` with K6's `EXCL` (§10 D-3), the gating form per
D-7(c).

Campaign: exp-review-fixes

## Declared scope

**Phase 0 (folded into Phase 1's delivery — D-9):** the Developer's delivery push fast-forwards `feature/landing-l1-core` `2ab688f..<tip>` through `35f5489` (the practice since
D-118: L1 is fast-forwarded at delivery, before the gate); #60 is merged by that push (its head becomes an ancestor of its base). No human act precedes the build. Upstream #219's
fast-forward and #59's closure are the human's morning packet (V1-102).
**Phase 1 (the Developer; one commit on `35f5489`, "unfreeze"):** the tree = **`7f0a4ad`'s tree + the rename (`69f9617`, `cca2986`) + K12's `tests/test_warning_hygiene.py` and
`tests/unit/lr_reduction/test_output.py` as at `35f5489`**. Measured (A-209, plumbing in this clone, matching V1-100): 27 files against `35f5489`; 2 files against `7f0a4ad` + the rename
(the two tests); no frozen entry left in `.pre-commit-config.yaml`; no `reduction_domains` reference in `src/`. K11's freeze, K17's template reverts and K19's scaling-factor reverts are
thereby undone by one forward commit (never a reset: #222 stacks on `2ab688f`); L1 again carries #14's ruff fixes, #41's fixes (now K12's, with K12's reviewed tests in place of #41's
originals), #49's noqa edits, #23/#26's `template.py` fixes with `new_reduction_from_template.py`, their tests and seven XMLs, #21/#27's scaling-factor fix and references; the freeze
lists (`.pre-commit-config.yaml`'s hook exclude, `tests/test_noqa_tags.py`'s guard) as at `7f0a4ad`. Provenance `Restores: 7f0a4ad`, `Keeps: 69f9617 cca2986 35f5489`, `Supersedes:` the
three slugs' entries. **Gated once:** G + pre-commit + P1/P2; the combination of K12's two tests with `7f0a4ad`'s suite is the one unmeasured thing (each green on its own tree) — the
gate decides. #54 follows the delivery push; upstream `exp-landing-l1-core` (#219) fast-forwards to L1-final in the human's morning packet. K12's upstream carry is inside #219.
**Phase 2 (one follow; gated tips only, in order):** **`R-final`** = R-3 `da5c3e2` (`exp-review` `c7741b2` on upstream `exp` `c4d20e4` + the rename) + the L2 amendment's three
lines as R-6 carries them (`binary_processing.py`, `direct_beam_maker.py`; D-159) — equivalently R-6 `1adda06` with R-4's template freeze and R-5's scaling-factor reverts undone; a new
immutable branch `feature/landing-reference-7`; **`EXCL` returns to K6's two entries** (`^\.github/workflows/test_and_deploy\.yml$|^scripts/test/measure_fit_path_dependence\.py$`,
`e52e3e8~1`). L2⁵ = L2⁗ `69b4ae3` + merge of L1-final; L3⁵ = L3⁗ `fd34875` + merge; L4⁵ = L4⁗ `a304657` + merge; K10⁵ = #55 `89ac4ef` + merge; K9 #56 fast-forwarded (clean) — all
measured clean on the probe (A-209, V1-100). **K14 #57 re-cut:** its anchor commit kept (`7f0a4ad` has the unanchored `exclude` — the bug is pre-freeze), its guard in
`tests/test_noqa_tags.py` re-written for the unfrozen config (the only conflict, measured). **K8 #58** forward-merged from L4-final (its own merge, as before). **#59 closes** (its three
files conflict as duplicates: the `.cfg` files identical, `test_scaling_factors_workflow.py` carrying #23's hunk that L1-final restores — measured). Each tip gated alone on its host
per D-7(c): (a) as now — G at every tip, L2⁵'s harness vs `R-final` identical ×9, L3⁵ P3 and L4⁵ `--move` vs `R-final` rc 0 with K6's `EXCL`, the must-fail vs R-6 rc 1, P5; or (b) G at
L4⁵ and K10⁵ only with the static proofs at L2⁵/L3⁵ — the human's charter word. `-v5` tag names.
**Phase 3 (the human's; the Advisor's scripts):** L2–L4 staged upstream in order, each on the previous (`exp-landing-l2-reduction` on `exp-landing-l1-core`, then L3, then L4) with
`scripts/upstream-draft-pr.sh` and `scripts/upstream-pr-test-reports.sh`; the siblings (#56, #57, #55/#222, #58) stacked as now; #222 fast-forwarded to K10⁵.
**Closures at the word:** #59 (redundant); K22 `landing-l1-hygiene-merge` stays staged as the "freeze stays" alternative (its Phase 1 = this plan's Phase 0); V1-98's incremental path
withdrawn (V1-100). K12's record stands (its content lands inside #219).
**Out:** resetting any upstream branch; K16 (held), K18 (proposed), K20 (staged; the `next` series is upstream `next`'s), K13 (tabled — the freeze was its motive).

## 0. Build recipe for Phase 1 (one way; the plumbing form produced the same tree here — B2 lets the Developer choose)

```sh
# in the Developer's subject clone
git fetch agentic feature/legacy-reduction-hygiene-v2 feature/landing-l1-core
git checkout -B feature/landing-l1-core 35f5489        # L1⁗ = #60's head; 2ab688f is its ancestor
git read-tree -m -u 7f0a4ad && git commit -q -m 'wip'   # the worktree and index become 7f0a4ad's tree (local wip, never pushed)
git cherry-pick 69f9617 cca2986                         # the rename: clean on this tree (measured)
git checkout 35f5489 -- tests/test_warning_hygiene.py tests/unit/lr_reduction/test_output.py && git commit -q -m 'wip'
git reset --soft 35f5489 && git commit                  # ONE commit on 35f5489; the wip commits were never published
```

Checks before delivery (T2): `git diff --name-only 35f5489 HEAD | wc -l` = 27; `git grep -c reduction_domains HEAD -- src` empty; `.pre-commit-config.yaml` with no frozen entry;
`tests/test_noqa_tags.py` as at `7f0a4ad`. Plumbing alternative (no hooks until the gate's `pre-commit run --all-files`): `merge-tree --write-tree --merge-base 69f9617~1 7f0a4ad 69f9617`,
then the same for `cca2986` on that tree, `read-tree` into a temporary index, `update-index --cacheinfo` for the two test blobs from `35f5489`, `write-tree`, `commit-tree -p 35f5489`.

**The message** (the subject's own terms — PR numbers and SHAs; no campaign words, P2): subject `landing-l1-core: the review's freeze leaves — L1 restored to its pre-freeze tree
(7f0a4ad) with the reduction_choices rename and the reviewed warning-hygiene tests`; body: what returns (#14's ruff fixes, #41's warning fixes and #49's noqa edits in the 12 legacy
files; #23/#26's template fixes with their tests and seven XMLs; #21/#27's scaling-factor fix and references; the hook's exclude list and the noqa guard as at 7f0a4ad), what is kept
(the rename 69f9617/cca2986; the reviewed tests from 35f5489 in place of #41's originals), what is undone (the freeze 4d5d93e..81acc87, the template reverts 756ece7..dc28545, the
scaling-factor reverts 31b1fd9/2ab688f) and why (the #219 review's agreement to return to the pre-freeze state); trailers `Restores: 7f0a4ad`, `Keeps: 69f9617 cca2986 35f5489`,
`Supersedes: 4d5d93e..2ab688f`, then the model trailer.

## 1. Request and symptom

The human, to the Advisor (V1-100; verbatim in the request): *"I would like to see the plan for running the K12 into #219 in the requests. I would like to understand the ramifications
of the freeze machinery staying or leaving. Also, you say the stack will have to regate a bunch of stuff and again in Phase 2 - that seems like quite some work. I'd really like to get
to staging L2 thru L4 properly. The ultimate goal is to get to where we left upstream:exp-review plus then new things that we have learned along the way this week. What would be the
best way to get there, in your opinion?"* — on the context of V1-97 (*"we agreed to revert upstream#219 to its state when landing-l1-core was finalized and before the freeze mandate
was issued … upstream:7f0a4ad"*). The Advisor's answer: the re-gating cost is per L1 change, so change L1 once (#60's fast-forward, then one unfreeze commit, gated once), run one Phase 2
against one `R-final` with K6's `EXCL`, close #59, re-write K14's guard, then stage L2–L4 upstream in order; the freeze leaves (the scientist's agreement removed its value); V1-98's
incremental path withdrawn. The target made precise: the fork's `exp-review` `c7741b2` (ahead of upstream's `62e21d1` by `1bffee1` and #49) on upstream `exp` `c4d20e4`, plus this week's
work (K10 v4 with the L2 amendment, K8, K9, K14, K15's pins, K17's rename, K12's tests; the K17 `next` series is upstream `next`'s).

## 2. Verified facts (2026-10-22 22:3xZ; this clone, plumbing only — a probe tree and commit never pushed; V1-97, V1-98, V1-100)

| # | Fact | Evidence |
|---|---|---|
| V1 | `7f0a4ad..2ab688f` first-parent is 13 commits: K11's five, K17's six (incl. the rename), K19's two; `35f5489` = `2ab688f` + K12's one commit (fast-forwardable) | `git log`; `merge-base --is-ancestor` |
| V2 | the rename's two commits cherry-pick cleanly on `7f0a4ad` (rc 0 ×2, plumbing) | A-206, A-209 |
| V3 | L1-final's tree (`7f0a4ad` + rename + K12's two tests) is 27 files from `35f5489`, 2 from `7f0a4ad` + rename; 0 frozen entries in `.pre-commit-config.yaml`; 0 `reduction_domains` references in `src/` | A-209 (`abcf98e`), V1-100 |
| V4 | onto L1-final: L2⁗ `69b4ae3`, L3⁗ `fd34875`, L4⁗ `a304657`, K10 v4 `89ac4ef`, K9 `e62aeb3`, K8 `0108214` merge clean (rc 0 ×6); K14 `63d46b6` conflicts in `tests/test_noqa_tags.py` only; #59 `ded5b1f` conflicts in `tests/test_scaling_factors_workflow.py` only (its `.cfg` files identical) | `merge-tree --write-tree` ×8 |
| V5 | R-2 `b3f9c75` = `exp-review` `c7741b2` merged onto upstream `exp` `c4d20e4` (D-122); R-3 = R-2 + the rename; R-4/R-5 add the template freeze and the scaling-factor reverts; R-6 = R-5 + the L2 amendment — so `R-final` = R-3 + the L2 amendment | `plans/stratified-landing-plan.md` |
| V6 | K6's `EXCL` was the two original entries; today's carries K11's 14 | `e52e3e8~1`; `landing-purity.sh:18` |
| V7 | K10 v4 PASS (I-155), K12 v2 PASS at #60 (I-156/I-158); upstream #222 (K10) at `1fbc900` on `2ab688f` — a reset would break it | I-155, I-158 |
| V8 | upstream `exp-review` `62e21d1`; the fork's `c7741b2` ahead by `1bffee1` (the human's test fix) and #49; the stack's reference has always been the fork's tip | V1-100 (unmeasured here) |
| V9 | P1 (`landing-l1-core`, `35f5489..<probe>`) clean with today's `EXCL` and with K6's two entries — the 27 paths are all in L1's declared set | A-210 |

## 3. Design — behaviours

| # | Behaviour |
|---|---|
| B1 | **Phase 0 folded into the delivery push (D-9):** the Developer fast-forwards `feature/landing-l1-core` to the tip at delivery (through `35f5489`; #60 merged by it); the Analyst flags if L1 is found at any SHA other than `2ab688f`, `35f5489` or the delivered tip. |
| B2 | **One forward commit** on `35f5489` with the declared tree (the Developer names the mechanics: `read-tree` of `7f0a4ad`, the two cherry-picks, the two test blobs from `35f5489` — or the equivalent); `git diff --name-only 35f5489 <tip>` = 27 paths; vs `7f0a4ad` + rename = the two tests; the lists at `7f0a4ad`'s form. |
| B3 | **Gated once:** G alone (the count reported and reconciled against I-115's 172 and K12's nine), no warnings line, `pre-commit run --all-files` rc 0 with ruff over every file, `test_noqa_tags.py` as at `7f0a4ad`; P1 (L1's set), P2 with `Restores:`/`Keeps:`/`Supersedes:` accepted. |
| B4 | **One Phase 2** against `R-final` with K6's `EXCL`; the proofs exact; the must-fail vs R-6 rc 1 stated; the gating form per D-7(c); `-v5` names. |
| B5 | **K14 re-cut, #59 closed, K8 forward-merged** as declared; #56 fast-forwarded. |
| B6 | **The human's carries:** `exp-landing-l1-core` → L1-final (#219 then = the pre-freeze L1 + the rename + K12's tests); #222 → K10⁵; Phase 3's upstream PRs in order. |

## 4. Files to change

| File | Change |
|---|---|
| the 27 files of V3 | B2 (L1) |
| `feature/landing-reference-7` (`R-final`) | B4 |
| L2⁵/L3⁵/L4⁵/K10⁵ merge commits; #57's re-cut; #58's forward merge | B4, B5 |
| ledger `scripts/landing-purity.sh` (`EXCL` → K6's two entries), `scripts/landing-sanitize-check.sh` (`Restores:`/`Keeps:`/`Supersedes:`) | at dispatch |

## 5. Failure-mode matrix

| # | Case | Expected | Covered by |
|---|---|---|---|
| 1 | common: Phase 0, the unfreeze commit, one follow | L1-final gated; the stack at `-v5` tips; #219 at L1-final | T1–T4 |
| 2 | pathological: the rename dropped | L3/L4 import failure — T2's `git grep`, T4's G at L3⁵ | T2, T4 |
| 3 | edge: K12's tests clash with `7f0a4ad`'s suite (unmeasured) | the gate REJECTs → v(N+1) resolves the clash (the human's D-7(b) alternative: `7f0a4ad`'s originals) | B3 |
| 4 | edge: the human excepts a part of the restore (D-5) | the commit excludes those hunks; v3 before dispatch | D-5 |
| 5 | pathological: a reset of an upstream branch | forbidden (B2 forward; #222's stacking); the carries are fast-forwards | D-2 |
| 6 | pathological: P3 against R-6 with K6's `EXCL` | red on the restored files; the reference of the day is `R-final` | D-3's must-fail |
| 7 | edge: the human merges #60 with the button before the delivery | L1's tip is an ungated merge M (tree `35f5489`'s); the delivery push would not fast-forward (the guard refuses it, loudly) — the Developer re-cuts the unfreeze commit on M (same tree) and pushes; recorded | B1, the push guard |
| 8 | edge: the human chooses (b) gating | L2⁵/L3⁵ carry static proofs only; a test failing at L2 and fixed by L3 would hide — stated in the record; upstream CI runs each layer's PR | D-7(c) |
| 9 | edge: the freeze stays after all | K22 instead; this plan stays staged | D-7(a) |

## 6. Red-Green seed

- **T1** (at delivery) `ls-remote` L1 = the delivered tip; `gh pr view 60` merged; #54's head the tip.
- **T2** `git diff --name-only 35f5489 <tip>` = 27 paths; `git diff --name-only <7f0a4ad+rename> <tip>` = the two tests; `git grep reduction_domains <tip> -- src` empty; `.pre-commit-config.yaml` with no frozen entry.
- **T3** G alone at the tip (`install --locked`, the lock check, `test-reduction`; the count reported; no warnings line); `pre-commit run --all-files` rc 0; P1, P2 clean over `35f5489..<tip>`.
- **T4** (Phase 2) at L2⁵, L3⁵, L4⁵, K10⁵, K14″, K8′: per D-7(c) — G (or the static proofs), `git grep reduction_domains` empty, L2⁵'s harness vs `R-final` identical ×9, L3⁵ P3 / L4⁵ `--move` vs `R-final` rc 0 with K6's `EXCL` and vs R-6 rc 1, P5; #56 `MERGEABLE`; #59 closed.

## 7. Mutate-once gate

| Mutation | Caught by |
|---|---|
| one frozen file left at upstream's content | T2 (the diff from `7f0a4ad` + rename grows past two) |
| the rename's importers not applied | T2's `git grep`, T4 |
| `EXCL` left at K11's set | T4's must-fail vs R-6 passes instead of failing |
| K12's tests left as #41's originals | T2 (the two-file diff vanishes) |

## 8. Acceptance criteria

1. Phase 1: T1–T3, the Integrator's PASS; #54 at the tip; the human pushes L1-final to `exp-landing-l1-core` (#219) in the morning packet.
2. Phase 2: T4 at each tip; #51/#52/#53/#55/#56 fast-forwarded; #57 and #58 at their re-cut tips; `R-final` named in the group plan; #59 closed; #222 fast-forwarded by the human.
3. Phase 3 (the human's): upstream L2–L4 PRs open in order.

## 9. Learnings relied on

V1-97/V1-98/V1-100 (the impact, the alternative, the route; the request); I-115 (`7f0a4ad` gated); I-156/I-158 (K12 v2 gated, #60); K17/K19's in-place-leaf shape and reference rule; K19 D-8 (gates alone); A-201 D-v2-1 (tag names); V1-100's probe lesson (plumbing, or `-c core.hooksPath=/dev/null`, in seat clones).

## 10. Decisions

- **D-1 — keep the rename** (V1-97 (1)): without it L3/L4 break silently; the human's own V1-70(b) asked for it.
- **D-2 — forward, never reset** (V1-97 (2)): one commit on the fork's L1; the upstream branches fast-forward.
- **D-3 — `R-final` = R-3 + the L2 amendment**, with K6's `EXCL` — the proof exact; the must-fail vs R-6 shows the reduction is live. (v1 called it R-7; the content is the same.)
- **D-4 — stop the redundant work at the word:** #59 closed; the records stay. (v1 also closed K12 v2 without a verdict; overtaken — K12 passed and is at #60, and this route keeps its tests.)
- **D-5 — confirmed by the human's concurrence with the request** (*"Ok, I've read your plan and I concur"*, 2026-10-22), whose freeze table lists #59's fix, the `next`-only template fixes and the #14/#49 cosmetics as "already in L1-final": #27's reference-file changes and #23/#26's `template.py` fixes return to #219 with the rest.
- **D-6 — K14's anchor survives, its freeze-era guard is re-written** (the request's default).
- **D-7 — the request's four choices, decided by the human (2026-10-22, verbatim in the request: *"remove the freeze, use K12s reviewed files, phase 2 let the full gate operate, its going to be all night and there is no rush. Keep K14's anchor and rewrite the guard."*):** (a) the freeze **leaves**; (b) **K12's reviewed tests**; (c) Phase 2 gating **(a) as now — full G at each layer** (no charter change); (d) K14 **keeps its anchor, its guard rewritten**.
- **D-9 — Phase 0 folded into Phase 1's delivery push** (the practice since D-118: the Developer fast-forwards `feature/landing-l1-core` at delivery, before the gate); #60 is merged by it; upstream #219's fast-forward and #59's closure are the human's morning packet (V1-102: no seat pushes upstream or opens/closes a PR overnight). The build therefore waits on nothing.
- **D-8 — L1 changes once:** Phase 0 then Phase 1 before any Phase 2 tip is cut (the request's principle); a later L1 change would be its own slug with its own follow.

## Revision history

- **v1 — 2026-10-22 (A-206):** staged from V1-97 (input); not dispatched. Sealed against L1‴ `2ab688f`, `7f0a4ad`, L2⁗/L3⁗/L4⁗ `69b4ae3`/`fd34875`/`a304657`, K10 v4 `89ac4ef`, R-6 `1adda06`; V2/V3 measured in a scratch worktree of this clone, removed after. Shape: one restore commit on `2ab688f` (tree = `7f0a4ad` + the rename), Phase 2 against R-7 with the pre-K11 `EXCL`, K12 v2 (then at the gate) and #59 closed. Preserved in `git log -- plans/landing-l1-unfreeze-plan.md`.
- **v2 — 2026-10-22 (A-209), re-scoped before dispatch to `requests/l1-final-k12-unfreeze-one-phase2.md` (V1-100):** Phase 0 = #60's fast-forward (K12 v2 passed and is at its PR — v1's closure of K12 overtaken); Phase 1's tree now carries K12's two reviewed tests (2 files from `7f0a4ad` + rename; 27 from `35f5489` — measured here, matching V1-100); the one Phase 2 against `R-final` (= v1's R-7) with K6's `EXCL`; K14 re-cut, K8 forward-merged, #59 closed; Phase 3 the human's upstream staging with the Advisor's scripts; the request's four choices as D-7; the gating variant (b) carried as the human's charter choice. Sealed additionally against `35f5489`, the probe `abcf98e`/`72508a8` (local only), R-2 `b3f9c75`, R-3 `da5c3e2`.
- **v2 dispatched — 2026-10-22 (A-210):** on the human's word couriered verbatim by the Advisor (V1-102) and confirmed in session; the four choices decided (D-7); D-5 confirmed by the concurrence; D-9 folds Phase 0 into the delivery push; §0 gives the build recipe and the message form; V9 (P1 clean on the probe with both `EXCL` forms); the ledger tools changed at dispatch: `landing-sanitize-check.sh` accepts `Restores:`/`Keeps:`/`Supersedes:`, `landing-purity.sh`'s `EXCL` returns to K6's two entries (Phase 2's P3 against `R-final`). `triage/landing-l1-unfreeze` at the analysis commit carrying this plan.
