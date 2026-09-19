# Campaign learnings synthesis — `exp-settings-roi`

**Scope.** The 82 numbered lessons across the 13 `plans/*-learning.md` files on
this branch, the escalation record, and the 27 `todo-*.md` in the tasking
register, organised by **recurring defect class** rather than slug.

**Evidence rule (verify-prose).** Every lesson cites a checkable source:
`<slug>-learning.md §N`, a `todo-*.md`, or a SHA. A lesson I could not cite was
dropped rather than rounded up. Where a claim is about the *campaign* rather
than about a file it is marked **[inference]** with its basis — those are the
ones a reviewer should attack first.

---

## A. Vacuous guards — a test that cannot fail

The campaign's most frequent defect, and the only one to recur in every slug
that wrote tests. At least eight distinct surfaces:

| surface | citation |
|---|---|
| a helper that swallows its own failure | `check-results-fields-learning.md` §1 |
| a test that never asks what would break it | `check-results-fields-learning.md` §7 |
| a green suite proving nothing | `port-overplot-axes-refresh-learning.md` §4 |
| a ported test passing without the feature | `port-settings-persistence-learning.md` §2 |
| a test that resets the thing under test | `test-warning-filter-learning.md` §2 |
| a test that writes the config it then reads | `harness-hardening-learning.md` §6 |
| a shim exercising only the site you thought of | `settings-management-learning.md` §9 |
| a guard matching a substring both answers share | `settings-editor-learning.md` §11 |

**What closed it.** Charter **amendment 16** (mutate-once gate): enumerate sites
from the code, one mutation per site, committed ledger, measured observations.
`settings-editor-learning.md` §8 is the earliest statement of the rule; the v6
ledger (`plans/settings-management-mutation-ledger.md` at feature tip `e1c0d63`)
is its current form.

**Residue.** Amendment 16 catches a mutation that *survives*; it does not catch
one that **cannot be distinguished from correct code**. v6 row 5 is the worked
example: with edits at rows 0/1/2 and row 0 removed, keeping the removed row's
own cell and shifting the later rows down produce the *same dict*, because the
neighbour's shift overwrites the stale key. The guard passed for the wrong
reason and only running the mutation showed it
(`settings-management-learning.md` §19; ledger v6 §"One that did not red").
A second residue is open and recorded: this review's own mutation 5 — the
reduction flow ceasing to delegate to `save_config_json` — survives, because
`save_json=True` is exercised by no test.

---

## B. Precondition ≠ payoff — mechanisms nothing calls

Code that is correct and unreachable, which reads as a feature in review.

- a mechanism with no caller is "a second muddle" — `settings-management-learning.md` §5
- a guard wired where the code does *not* run — `settings-management-learning.md` §17
  (the v4 `closeEvent` guard: a tab inside a QTabWidget inside a QMainWindow is
  torn down without one, so the guard never ran where it mattered)
- two whitelist clauses guarding a field that does not exist — `settings-management-learning.md` §10
- honouring a reference before proving it dead — `settings-editor-learning.md` §3
- a restore trap armed before the thing it restores from exists — `pixi-lock-format-guard-learning.md` §4

**What closed it.** No amendment; closed case-by-case by "fix the mechanism,
then find every path that reaches it" (`settings-editor-learning.md` §9).

**Residue. [inference]** This class has no systematic gate, unlike A. Basis:
amendments 15–20 are indexed in the charter and none addresses reachability, and
the class recurred in T3 v4 (§17) after being named in T2 (§5). The nearest
thing to a gate is the test-reviewer domain, which is per-slug and human.

---

## C. One behaviour, two implementations — the divergent copy

A correct implementation and a second copy, with nothing keeping them in step.
The copy is where the bug lives, and it is usually the public-facing one.

- extract the fix, or watch it recur in the next file — `settings-management-learning.md` §6
- a whitelist enforced on one door is not a whitelist — `settings-management-learning.md` §3
- guard every site separately — `settings-management-learning.md` §8
- type dispatch in three places is "a bug with a delay fuse" — `settings-editor-learning.md` §6
- two normalisation points, one covering for the other — `settings-editor-learning.md` §14
- a hand-maintained tuple beside an enumeration is fail-open — `settings-management-learning.md` §20

**Two product defects reached `exp` through this class — the only class that can
say that:**

1. `read_template` had a correct implementation and a divergent fork copy that
   raised `AttributeError` on every run —
   `todo-fork-read-template-attributeerror.md` (fixed, PR #26; the `getattr`
   guard is live on `exp` at `new_reduction_from_template.py:480`).
2. `save_config_json` was the *reusable* saver and broken on every input, while
   the *working* saver was three lines inlined in the reduction flow —
   `todo-save-config-json-inverted.md`. **Closed by this review** (`2136a8f`).

**What closed it.** Deriving rather than duplicating. `field_spec.py` is the
campaign's best artefact here: `PER_ANGLE_NAMES`, `OPTIONAL_LIST_NAMES`,
`RUNTIME_OWNED_NAMES`, `DEFAULT_IF_EMPTY_NAMES` and `GROUPS` are projections of
`FIELD_SPEC`, and `TYPES` is enforced against it **at import**
(`field_spec.py:570`) with a test (`test_settings_document.py:607`) — so a typo
like `"flaot"` fails at import rather than silently producing an unvalidated
text box.

**Residue.** `amend_config` never appends the `datasearch.directories` key to
`modified_keys`, so its backup is dead code and every
`with amend_config(data_dir=...)` leaks the nexus dir onto Mantid's
process-global search path. Adding the missing line produces **14 real test
failures**, because those tests lean on the leak
(`todo-amend-config-restore.md`, measured by the Integrator at `6c34cd7`).
Deliberately not taken here — see "considered and declined".

---

## D. Prescription vs. types — the plan was wrong, not the code

The campaign built a great deal of machinery that checks the *implementation*
against the *prescription*, and nothing that checks the prescription. Named in
`todo-prescription-not-validated-against-types.md`; the stated reason for the T3
v5 rejection (`8c7dfbb`).

The v5 instance: the prescription said to bind the layer-(b) value at edit time.
That is **scalar-correct and array-wrong** — `_session_edits` holds both scalars
and the 13 per-angle arrays, and for an array it froze a positional identity
that any row-count change re-indexes (`settings-management-learning.md` §18).

Related: derive the message from what the function can do, not from the domain
you had in mind (`settings-editor-learning.md` §13); never let a domain be a
hand-copy (`settings-editor-learning.md` §7).

**What closed it.** Charter **amendment 18** — type enumeration in the plan; the
v6 plan enumerates "13 per-angle arrays vs scalars, behaviour each".

**Residue, and it recurred inside v6 itself.** The v6 work order's item 2
prescribed renaming a test to `test_load_resolution_refuses_a_fifo_sidecar` —
but that test passes the FIFO as the **settings file**, not the sidecar, so the
prescribed name was itself inaccurate and would have swapped one wrong name for
another. Caught by checking the prescription against the body (`e1c0d63`;
transcript `D-41`). Amendment 18 enumerates *types*; it does not yet require the
plan's **identifiers** to be checked against the artefacts they name.

---

## E. Prose outrunning evidence

Claims in comments, commit messages and PR bodies the code does not support. On
`check-results-fields`, **all four rejections were about prose, not code**
(`check-results-fields-learning.md` §9) — the most concentrated statement of
this class in the corpus.

- say which number you are quoting — `check-results-fields-learning.md` §8
- scope a claim to the invocation you tested — `harness-hardening-learning.md` §3
- state the guarantee you have, not the one you aimed at — `settings-editor-learning.md` §12
- a comment stating an unfinished measurement as finished outlives the commit
  that admits it — `pixi-lock-format-guard-learning.md` §1
- "seed PR" does not mean "verified against facility data" — `port-overplot-axes-refresh-learning.md` §3
- an inherited guard needs its own justification — `port-settings-persistence-learning.md` §4
- a record only counts if someone else can check it — `settings-management-learning.md` §14

**What closed it.** The **verify-prose gate** (`todo-verify-prose-claims.md`,
adopted into the Analyst plan template and the Integrator checklist).

**Residue.** Two prose defects were still live in `settings_editor.py` at the v5
tip and were corrected only in v6 (`e1c0d63`): a comment describing a
`deleteLater` that **does not exist anywhere in the file**, attributing the
"leak rather than abort" outcome to the very mechanism the module-level comment
640 lines above identifies as what *causes* the abort; and a `_PARKED_WORKERS`
comment saying a parked worker sits "where nothing will collect it" when
`_reclaim_parked` does exactly that. Both were in code the campaign had already
reviewed — the gate catches new prose, not the standing stock.

---

## F. Process-global state and cross-session interference

Test outcomes depending on state outside the test.

- hard-coded `/tmp` paths let concurrent sessions corrupt each other's gate — `port-overplot-axes-refresh-learning.md` §1
- concurrent ports sharing regions — `port-settings-persistence-learning.md` §3
- an unrestored `os.chdir` invalidates **every measurement after it** — `scaling-factor-path-anchor-learning.md` §4
- a gate command that `cd`s hides every cwd-dependent defect behind it — `scaling-factor-path-anchor-learning.md` §1
- co-collection is the same accident, and it caught the author *while verifying
  the fix for the first one* — `scaling-factor-path-anchor-learning.md` §6
- where a process-global default cannot be restored, do not restore it — `harness-hardening-learning.md` §4
- a test spawning a hanging process must own its death — `harness-hardening-learning.md` §5
- worktrees share the tag store, so that is not isolation — `fork-release-tags-learning.md` §2
- `pytest-timeout`'s default `signal` method cannot interrupt native code — `launcher-test-harness-learning.md` §1

**What closed it.** Per-slug fixes plus `--timeout-method=thread` as standard.
v6 armed a timeout on the `test-reduction` task (`e1c0d63`), which had none —
load-bearing, not hygiene: the sidecar-FIFO mutation reds *as a hang*, so
without a timeout the battery wedges instead of reporting.

**Residue.** `amend_config` (class C) is the largest surviving instance.

---

## G. The per-angle trap family — product-specific, three generations

The one class about *this instrument's data model* rather than engineering
discipline, recurring three times in three forms:

1. **active row as hidden input** — using `currentRow()` instead of the signal's
   row writes the edit to whichever row happens to be selected. Guarded in T2
   (`test_editing_a_cell_updates_the_row_that_was_edited_not_the_selected_one`).
2. **`_equalise_angles` padding** — layers resolve independently, so a short
   array silently shifts every later angle by one; the resolver pads rather than
   fails (`settings_resolver.py:392` at the feature tip).
3. **edit-time freeze** — recording the whole per-angle column rather than the
   cell, so a Load or Remove re-indexes it (`settings-management-learning.md`
   §18; rejected at v5 `8c7dfbb`, fixed at v6 `e1c0d63`).

**[inference]** These are one defect wearing three costumes: *a per-angle
value's identity is positional, and every part of the system that holds one must
survive a change to the row count.* Basis: all three misplace a value by index
rather than corrupting it, and all three are invisible to a test that never
changes the row count between write and read. Offered as the unifying reading,
not as a claim any single document makes.

**Residue.** Layer (b) still carries the whole reassembled column after v6, so
resolving against a *different* experiment than the one edited masks that file's
other angles with the current document's values. Narrower than v5 (which also
misaligned them) but not closed; cell-level layer authority is a resolver
change.

---

## H. Liveness and delivery

`todo-campaign-polling-posture.md` (→ amendment 17),
`todo-transcript-numbering-collision.md` (→ amendment 19, per-seat transcripts),
`todo-subagent-destructive-op-stall.md` (→ amendment 15),
`todo-campaign-git-comm-friction.md` (→ amendment 19).

The class the campaign closed most completely: each instance produced an
amendment, and the amendments are in force.

---

## The code change this review warrants

**`save_config_json`** on `feature/learnings-review` (`2136a8f`), for three
reasons the synthesis makes rather than the todo:

1. It is the **class-C shape**, and class C is the only class with two *product*
   defects reaching `exp`.
2. It is a **single review surface**: one function, one delegation, one new test
   file. §4 sizing holds.
3. It is **evidence-backed and re-measured** — both documented failure modes
   were reproduced on this tip before any code was written.

Writing the RED found a defect the todo did not record: `json.dump` raising
part-way left a **truncated file**, so a failed save destroyed the previous
settings. That is itself a small instance of class A — the todo reasoned about
the exception and only running it showed the file damage.

Mutations, 4 of 5 red; the survivor is recorded in the commit message and in
class A's residue rather than papered over with a source-text assertion, which
would be a guard matching a substring both answers share
(`settings-editor-learning.md` §11).

**Considered and declined.** `amend_config` is the larger defect and is
explicitly out of scope: 14 tests lean on the leak, the fix needs a
call-sites-first ordering, and `todo-amend-config-restore.md` itself says it
"needs its own slug with the seriousness B1 got".
`todo-scaling-factor-slit-match-margin.md` needs a scientist's judgement, not an
engineer's. The remaining parked todos are cosmetic, latent, or already closed.

---

## What a reviewer should attack

The two **[inference]** claims (B's "no systematic gate", G's "one defect in
three costumes") are the least defensible statements here by construction: they
are readings of the corpus rather than quotations from it. The table citations
are all single-hop and checkable; if one does not check, treat that lesson as
dropped rather than the table as approximately right.
