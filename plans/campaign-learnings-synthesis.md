# Campaign learnings synthesis — `exp-settings-roi`

**Scope.** The 82 numbered lessons across the 13 `plans/*-learning.md` files on
this branch, the escalation record, and the 27 `todo-*.md` in the tasking
register, organised by **recurring defect class** rather than slug.

**v2 (2026-09-19).** Corrected after review `3098582`, which passed the citation
audit (72 items sampled, zero dangling, 92 % semantic) and blocked on six
accuracy findings. Four share one root cause worth naming at the top, because it
is this document's own section E turned on itself: **a green commit's
self-report is a claim, not a record.** v1 built section G and parts of A/C/F
from the v6 commit body; v6 was rejected eight minutes after this file was
committed, and two of its self-assessments were wrong independently of that.
Every correction below is transcribed from `d5733af` and re-verified here.

**Evidence rule (verify-prose).** Every lesson cites a checkable source:
`<slug>-learning.md §N`, a `todo-*.md`, or a SHA. A lesson I could not cite was
dropped rather than rounded up. Where a claim is about the *campaign* rather
than about a file it is marked **[inference]** with its basis — those are the
ones a reviewer should attack first.

---

## A. Vacuous guards — a test that cannot fail

The campaign's most frequent defect. The cited evidence covers 7 of the 13
slugs, and `todo-mutate-once-gate.md` counts eight instances across five — v1
claimed "every slug that wrote tests", which this document's own evidence rule
does not support. At least nine distinct surfaces:

| surface | citation |
|---|---|
| a helper that swallows its own failure | `check-results-fields-learning.md` §1 |
| a test that never asks what would break it | `check-results-fields-learning.md` §7 |
| a green suite proving nothing | `port-overplot-axes-refresh-learning.md` §4 |
| a ported test passing without the feature | `port-settings-persistence-learning.md` §2 |
| a test that resets the thing under test | `test-warning-filter-learning.md` §2 |
| a test that writes the config it then reads | `harness-hardening-learning.md` §6 |
| a shim exercising only the site you thought of | `settings-management-learning.md` §9 |
| disarm the mechanism and watch the test go red | `harness-hardening-learning.md` §2 |
| a guard matching a substring both answers share | `settings-editor-learning.md` §11 |

**What closed it.** Charter **amendment 16** (mutate-once gate): enumerate sites
from the code, one mutation per site, committed ledger, measured observations.

The earliest statement is **`harness-hardening-learning.md` §2**, first
committed `c6628ea` **2026-08-19** — *"disarm the mechanism once and watch the
test go red. If it stays green, it is guarding nothing."* v1 credited
`settings-editor-learning.md` §8, which is three weeks later (`f9d7347`,
2026-09-09) and in fact a day *after* amendment 16 was adopted (2026-09-08); §8
states the **diagnostic corollary** — when a mutation does not red, work out
whether the test is vacuous or the mutation missed — not the gate. Evidence:
`todo-mutate-once-gate.md`.

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

**Two product defects reached `exp` through this class** — on the reading
"reached `exp` *through* this class"; v1's flat "the only class that can say
that" is more than the evidence carries:

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

**Residue, and it recurred inside v6 itself.** The name
`test_load_resolution_refuses_a_fifo_sidecar` was **suggested in the Analyst's
plan** (`plans/settings-management-plan.md:953`, hedged *"rename to what it
covers (**e.g.** …)"*) — not prescribed in a work order. That test passes the
FIFO as the **settings file**, not the sidecar, so the suggested name would have
swapped one wrong name for another; it was corrected at `e1c0d63` and the
sidecar name went to the genuinely-sidecar test. Amendment 18 enumerates
*types*; it does not yet require a plan's **identifiers** to be checked against
the artefacts they name — which is the lesson, and it is unchanged.

*Correcting v1:* v1 called this "the v6 work order's item 2 prescribed". Both of
v1's own sources say *plan* (`e1c0d63` body; transcript `D-41`), `grep
fifo_sidecar` finds nothing in `8c7dfbb:todo.md`, and "e.g." is a suggestion, not
a prescription. The review notes it made the mirror-image error in the other
direction; the misattribution is worth recording in both directions because the
lesson only lands if it points at the artefact that actually carried the name.

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
v6 armed a timeout on the `test-reduction` task (`e1c0d63`), which had none.

*Correcting v1:* v1 called that value "load-bearing, not hygiene", inheriting the
v6 commit's own assessment. `d5733af` finds the **600 s** figure does not achieve
its purpose inside the harness — it is per-test and sits at the harness's own
600 s ceiling, so the wedge it is supposed to prevent is not prevented — and
recommends 120 s. Arming a timeout is right; the value shipped is not, and
calling it load-bearing was a self-report taken as a record.

**Residue.** `amend_config` (class C) is the largest surviving instance.

---

## G. The per-angle trap family — product-specific, FOUR generations

The one class about *this instrument's data model* rather than engineering
discipline, recurring four times in four forms:

1. **active row as hidden input** — using `currentRow()` instead of the signal's
   row writes the edit to whichever row happens to be selected. Guarded in T2
   (`test_editing_a_cell_updates_the_row_that_was_edited_not_the_selected_one`).
2. **`_equalise_angles` padding** — layers resolve independently, so a short
   array silently shifts every later angle by one; the resolver pads rather than
   fails (`settings_resolver._equalise_angles`; v1 cited line 392, which lands on
   the enclosing `resolve_all`).
3. **edit-time freeze** — recording the whole per-angle column rather than the
   cell, so a Load or Remove re-indexes it (`settings-management-learning.md`
   §18; rejected at v5 `8c7dfbb`, **attempted at v6 `e1c0d63` and rejected at
   `d5733af`** — v6 did not fix generation 3, it exchanged it for generation 4).
4. **absent-`None` as a real state** — clearing an `optional_list` cell makes
   `set_angle_field` collapse the whole column back to `None`, the sanctioned
   "derive it from the chopper ranges" state. v6's per-cell recorder then ran
   with `current is None`, matched **neither** arm of its per-angle branch, and
   so neither recorded nor removed — the deleted value came back at layer (b)
   badged as the scientist's own, and a two-gesture variant reaches
   `nr_reduction_calc.py:452` with `LambdaMinUse = None` and kills the
   reduction. B1′, `d5733af`, confirmed 5× (`settings-management-learning.md`
   §21).

**The unifying reading, now stated rather than inferred.** `d5733af` supplies
it from the rejection side and it is better than v1's guess: `_session_edits`
must represent **three value-states — a value, a whole column, and
absent-`None`** — and each attempt handled two of the three (v4→v5 missed
whole-column; v5→v6 missed absent-`None`). Amendment 18 governs a value's
*type*; `None`-as-a-real-value is a *state* the type does not distinguish, which
is why it escaped three attempts and five sign-offs. v1 offered "positional
identity" as an `[inference]`; that is a property of generations 1–3 only, and it
does not explain generation 4.

**Residue.** The whole layer-(b) pre-run override was **removed** by the
amendment-20 decompose (Slug A, `157821f`) and deferred to Slug B
(`plans/settings-ui-override-plan.md`), which owes it cell-level layer
authority. So the residue is not a narrowed defect but an absent feature.

*Correcting v1 here specifically:* v1 wrote that v6's masking was "narrower than
v5 (which also misaligned them)", inheriting the v6 commit body's "v5 had the
same masking plus the misalignment". `d5733af` makes correcting exactly that a
mandatory record correction: the whole-column **shape** is the same, the
**masking value is not**. At `8c7dfbb` the frozen column was the *edited*
experiment's own, so foreign values never acquired layer-(b) authority; v6 minted
it for values from **another experiment's file**. That is wider, not narrower.
This was class E occurring inside the document that names class E.

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

**Corrected in v2, and the corrections are themselves class C and class E:**

- v1 said the fix left "one saver rather than two". It did not.
  `example_nr_reduction.py:222` and `:292` held two more byte-identical copies,
  **both still open-then-dump**, i.e. both still carrying the very truncation
  defect the same commit announced finding. The weak-saver count went 3 → 3 and
  only the broken fourth was repaired — leaving two copies of the divergent-copy
  class inside the slug whose synthesis names that class. Both now delegate
  (`0f35b83`); the count is 1.
- v1 said "nothing drives the reduction entry point", which made the disclosed
  mutation survivor sound harmless. `launcher/apps/file_batch.py:669` passes
  `save_json=` from a user checkbox labelled "Save settings JSON" (`:145`).
  "Exercised by no test" is true; "nothing drives it" is false — and that
  unguarded delegation is **the only path by which a scientist produces this
  JSON**, so the survivor's stakes are higher, not lower.
- Two guards were weaker than the claims they backed. `make_json_safe` had no
  mutation row and no guard, and the fixture set every override with `str()`, so
  it was a no-op across the whole file and deleting it passed all six guards —
  while the live GUI hands in a `PosixPath`. And the truncation guard asserted
  only that a refused save creates no **new** file, in a `tmp_path` where none
  existed, so an open-first-then-`unlink` implementation destroyed prior settings
  and passed. Both closed in `0f35b83`, each proven by re-running the mutation
  that had passed.

Mutations, 4 of 5 red at v1; the survivor is recorded rather than papered over
with a source-text assertion. v1 justified that by `settings-editor-learning.md`
§11 (a guard matching a substring both answers share), which does not apply —
the mutant genuinely fails such an assertion, and a count-based one would red it.
The defensible reason is simpler: **a text assertion pins text, not behaviour**,
and stays green if the delegation passes the wrong arguments.

**Considered and declined.** `amend_config` is the larger defect and is
explicitly out of scope: 14 tests lean on the leak, the fix needs a
call-sites-first ordering, and `todo-amend-config-restore.md` itself says it
"needs its own slug with the seriousness B1 got".
`todo-scaling-factor-slit-match-margin.md` needs a scientist's judgement, not an
engineer's. The remaining parked todos are cosmetic, latent, or already closed.

---

## What a reviewer should attack

**v1 pointed here at the wrong two claims, and that is the most useful finding in
the whole review.** It nominated its two `[inference]` readings as the weakest
statements — and both checked out. All four content failures were **unhedged,
non-`[inference]` claims**: the ones inherited from a green commit's self-report
and never re-derived. The reviewer's summary is worth keeping verbatim: *the
doc's self-audit looked where it had already been careful.*

So the standing instruction is inverted. Attack the sentences this document
states **flatly**, particularly any that describe the outcome of a slug —
"fixed at", "narrower than", "load-bearing", "one saver rather than two". Each
of those was true of what a commit *claimed* and false of what the tree
*contained*. The hedged readings are comparatively safe precisely because
hedging them forced the author to check them.

The citation audit is the part that held: 72 items sampled across every style,
zero dangling pointers, 92 % semantic hit rate, all three corpus counts exact.
A pointer into nothing is not this document's failure mode; a pointer into a real
artefact that does not say what the sentence claims is.
