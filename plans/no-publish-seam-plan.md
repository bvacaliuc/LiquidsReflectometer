# Plan: no-publish-seam (F1)

**Campaign:** `exp-settings-roi` · charter §4 slug F1 (findings F1; charter §6
cross-repo) · authored against `REF_L/shared`
`wip/enable-exp-parallel-reduction` @ `c4fed3d` and `agentic/exp` @ `2127343`
**Retry attempt:** 1

Review domains: none in the Integrator gate — cross-repo slug, no `qa/{slug}`
tag is produced (charter §6: auto-resolution stops at the facility boundary;
the human's code.ornl.gov review of the pushed branch is the gate).

## Scope correction (correct-and-flag, 2026-08-18)

Charter §4 and todo.md direct: "reinstate the `REF_L/shared` forwarding
(fixing the latent `offset` NameError)". **Both are already done at source** —
reality drifted after the 2026-08-17 audit:

- `wip/enable-exp-parallel-reduction` advanced `16bbfc0` → **`c4fed3d`**
  ("use --no_publish for control of whether to publish", human-authored
  2026-06-06, **already pushed** to origin): the forwarding is reinstated
  (`args.append('--no_publish')`, line 96) and the dead block carrying the
  undefined `offset` was replaced — zero `offset` references remain.
- The exp-side alias `a9af9df` is an ancestor of `dccd093`; the deployed
  facility build `2.10.0.dev20260708155450+gdccd093` already accepts BOTH
  `--no-publish` and `--no_publish`.

What `c4fed3d` also did is flip the **shim's own CLI scan** from the
facility-idiomatic hyphen to snake_case, and gate the forwarding on a
hard-coded constant instead of the caller's flag. The residual scope is the
three trap-removals below — small, but each with facility blast-radius
rationale.

## Symptom (residual)

1. **Silent-publish trap, active today:** `autoreduce/reduce_REF_L.py:44`
   computes `publish` by scanning `sys.argv` for `--no_publish` (snake) ONLY.
   Until `c4fed3d` the shim accepted ONLY `--no-publish` (hyphen) — the
   spelling the KB's own module doc documents for manual re-reduction
   ("Manual `reduce_REF_L.py <nxs> <outdir> --no-publish` is safe",
   module-ref_l-shared.md §How to test safely). A hyphen-habituated caller
   today silently gets `publish=True`: the suppression request is dropped and
   the run publishes to monitor.sns.gov. Facility-visible blast radius.
2. **Publish-against-request trap, latent:** line 95 gates the shadow
   forwarding as `if not new_publish:` — the caller's `publish` does not
   propagate. Harmless today (`new_publish = False` hard-coded ⇒ shadow never
   publishes), but the moment an operator flips `new_publish = True`, a
   re-reduction invoked WITH a no-publish flag still publishes the shadow
   result. Same class as the original F1 (suppression request dropped), one
   knob-flip away.
3. Comment on line 43 names only the snake spelling.

## Verified state (2026-08-18, Analyst)

- `REF_L/shared` @ `c4fed3d`, working tree clean, in sync with
  `origin/wip/enable-exp-parallel-reduction` (clone-2 checkout
  `/media/ssd2/Projects/Claude/2/REF_L/shared`).
- `grep -n offset autoreduce/reduce_REF_L.py` → no matches.
- Production path honors the caller: line 53
  `autoreduce(..., publish=publish)`.
- No in-repo caller passes either spelling to the shim: `batch_reduce.py`
  imports `autoreduce(..., publish=False)` directly (line 74), and the dated
  frozen copies (`_20250904`, `_20251207`, `_Jan2023`) scan no flag at all.
  The spelling contract exists for OUT-of-repo callers (humans, re-reduction
  tooling) — which is exactly why silently narrowing it is a trap.
- The checker (below) is RED against `c4fed3d` on the hyphen case and GREEN
  on a two-line-patched copy — proven during triage.

## Files to change (REF_L/shared, branch `wip/enable-exp-parallel-reduction`)

One file — `autoreduce/reduce_REF_L.py` — three edits:

1. Line 44 →
   `publish=not any([x.startswith('--no-publish') or x.startswith('--no_publish') for x in sys.argv])`
   (accept both spellings — the same both-spellings medicine `a9af9df`
   applied on the exp side, now at the shim boundary; keeps the existing
   `startswith` idiom).
2. Line 95 →
   `if not (publish and new_publish):               # NB: for testing`
   (compose the caller's flag with the operator knob: append `--no_publish`
   unless BOTH permit publishing. Behavior-identical today —
   `new_publish=False` ⇒ always append — and correct at knob-flip).
3. Line 43 comment →
   `# re-reduction may provide '--no-publish' (or legacy '--no_publish') following the above two arguments`

Keep forwarding the snake spelling at line 96: it is accepted by every
deployed exp build, including pre-`a9af9df` ones. Do NOT touch: the
`PIXI_PREFIX` personal path (pixi-deploy seam, out of scope), the
`new_publish` value (operator/deploy decision, human-owned), `CONDA_ENV`
(parsed by the autoreduction harness), the positional-argv handling.

## Cross-repo execution note (charter §6 — OVERRIDES the default feature/qa flow)

`REF_L/shared`'s remote is `code.ornl.gov` — physically read-only to agents
(pre-push guard + deny globs fence it in every permission mode). Therefore:

- NO `feature/no-publish-seam` branch, NO `qa/no-publish-seam` tag on
  `agentic` — there is no `lr_reduction` change, and the Integrator gate does
  not run for this slug.
- Implement in the clone-2 checkout
  (`/media/ssd2/Projects/Claude/2/REF_L/shared`, the Developer's session
  tree): commit locally on `wip/enable-exp-parallel-reduction`, continuing
  its lineage — the human's eventual push is then a plain fast-forward. Read
  `git log -n5` there first (that repo's conventions differ); model-credit
  trailer required. **Never push this repo — do not even `--dry-run` toward
  it.**
- Record in `plans/no-publish-seam-crossrepo.md` on the analysis branch:
  branch + new SHA, the verification transcripts (below), and the
  `needs-human-push` terminal state. Then merge the triage branch into
  analysis, push analysis, delete the triage ref (contract steps 6–9 apply
  unchanged). The Administrator surfaces the crossrepo file; the human
  pushes from a terminal and reviews on code.ornl.gov.

## Red-Green verification (adapted: the shim cannot run locally)

`autoreduce/reduce_REF_L.py` imports `lr_autoreduce` at module level
(line 37) — unresolvable outside the deployed facility env, so no local
end-to-end run exists. The committed checker
`plans/scripts/no-publish-seam-check.py` (this branch) verifies the two
edited behaviors WITHOUT importing the shim: it AST-extracts the `publish`
assignment and the `new_publish` gate and evaluates both against fixed truth
tables.

- RED (before editing):
  `python3 plans/scripts/no-publish-seam-check.py /media/ssd2/Projects/Claude/2/REF_L/shared/autoreduce/reduce_REF_L.py`
  → exit 1: `FAIL: publish scan: argv=['--no-publish'] -> True, want False`.
- GREEN (after the three edits): same command → exit 0 with both OK lines.
  Also run `python3 -m py_compile autoreduce/reduce_REF_L.py`.
- Copy both transcripts into `plans/no-publish-seam-crossrepo.md`.
- What local verification CANNOT prove (stated per detection-complete):
  actual publish suppression on a facility shadow run — that is the human's
  post-push validation (a `batch_reduce.py`-style scratch run or the next
  autoreduction cycle on a test IPTS).

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Manual re-reduction with `--no-publish` (common; KB-documented habit) | today: silently publishes | Edit 1 — both spellings suppress; checker case 3 |
| Caller suppresses while `new_publish=True` (edge, post-knob-flip) | today: shadow publishes against the request | Edit 2 — composed gate; checker truth table |
| Daemon path: two positional args, no flag (common) | n/a | `publish=True`; production publishes; shadow stays knob-gated — behavior unchanged |
| `--no-publish=x` / prefixed forms (edge) | `startswith` idiom | preserved on both spellings, same tolerance as today |
| A local machine runs the shim (pathological) | `ModuleNotFoundError` at line 37, before argv parsing | unchanged; the checker exists precisely because of this |
| Checker finds ≠1 `publish` assignment or ≠1 gate (pathological drift) | checker fails loudly with the count | investigate before editing — the file moved under the plan |

## Acceptance criteria

- The three edits above, committed locally on
  `wip/enable-exp-parallel-reduction` (single commit; trailer; **no push**).
- Checker RED-before/GREEN-after transcripts + `py_compile` clean, recorded
  in `plans/no-publish-seam-crossrepo.md` with branch + SHA.
- No other hunks: `git diff --stat HEAD~1` shows 1 file, ~3 changed lines.
- Analysis branch updated (crossrepo file + triage merge) and the triage ref
  deleted per contract steps 6–9.

## Out of scope (recorded so nobody "helpfully" adds them)

- The `PIXI_PREFIX=/SNS/users/6ov/...` personal-path wart → pixi-deploy seam
  (`module-pixi-deploy.md`), separate decision.
- Flipping `new_publish` to `True` — operator/deploy decision, human-owned.
- Any `lr_reduction:exp` change (`a9af9df` closed that half).
- argv `IndexError` when <2 positional args (pre-existing daemon contract).
