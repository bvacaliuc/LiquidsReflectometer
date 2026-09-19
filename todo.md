# Integrator: `learnings-review` v1 — REJECTED on record accuracy + two guard gaps. **The code is correct; nothing needs re-doing.**

**Gate is GREEN** at `2136a8f`: 145 launcher + 246 reduction, `REDUCTION_EXIT=0`, zero failures,
DONE marker present; committed `pixi.lock` byte-identical to `exp` with no branch commit touching
it; format v6; ruff clean; clean fast-forward. **Every mechanical acceptance criterion is met.**

## READ THIS FIRST — the synthesis is STALE, not careless

Two of the six blocking findings say the synthesis presents T3 v6 as fixed when it was rejected.
**The author could not have known.** Timestamps: synthesis committed `3fdd403` **12:12:49**, merged
12:13:00; my v6 rejection `d5733af` **12:21:27** — **8 minutes later**. design established this and
flagged it unprompted, and it is the right framing: *"That bears on blame, not on the claim."*

The findings are still blocking, because this document becomes the campaign's reference and is now
wrong on its central product-defect section. But nothing here is a failure of care, and the remedy
is **transcription** — `d5733af` already contains the replacement language. Do not read this
rejection as a criticism of the synthesis's method, which is the best-evidenced document the
campaign has produced.

## The citation audit PASSED, and that deserves stating

The plan made this a blocking gate: *"a lesson whose citation doesn't check is a blocking
finding."* design sampled **72 discrete checkable items across every citation style** and reported
both sample size and hit rate, as asked:

| citation style | checked | result |
|---|---|---|
| `<slug>-learning.md §N` | 42 | **42/42 exist**, headings match the paraphrase; 12 read in full, 11 support |
| `todo-*.md` | 10 | all exist, 6 read in full |
| SHAs | 4 | all resolve, subjects consistent |
| `file.py:line` | 4 | 3 land on the cited construct, 1 on the enclosing method |
| charter amendments 15–20 | — | all mappings check |
| corpus counts (82 lessons / 13 files / 27 todos) | 3 | **all three exact** |

**Zero dangling citations. Semantic hit rate 66/72 ≈ 92 %.** Every failure below is a real
artefact that does not say what the lesson claims — which is a much better failure mode than a
pointer into nothing, and it is only detectable by someone who read the artefacts.

---

## BLOCKING — Group 1: the v6 self-report was taken as record (design B1, B2)

**B1. Section G claims closure for a generation that was rejected, and misses a fourth.** G item 3
reads *"edit-time freeze … rejected at v5 `8c7dfbb`, **fixed at v6 `e1c0d63`**"*, under a header
saying *"three generations"*. v6 was **rejected** (`d5733af`), and generation 4 is B1′: clearing a
`LambdaMin` cell collapses the column to `None`, `_record_edit` neither records nor removes, and
the deleted value is resurrected at layer (b) — with a two-gesture variant reaching
`nr_reduction_calc.py:452` with `LambdaMinUse = None` and **killing the reduction**. v6 is not a fix
of generation 3; it exchanged generation 3 for generation 4.
→ **Remedy (transcription):** G becomes four generations; item 3 reads "attempted at v6, rejected at
`d5733af`"; the residue adopts `d5733af`'s own unifying reading, which is what G's `[inference]` was
reaching for — *`_session_edits` must represent three states … each attempt has handled two of the
three.*

**B2. G's residue restates the exact sentence `d5733af` mandates correcting.** *"Narrower than v5
(which also misaligned them)"* rests on the v6 commit body's *"v5 had the same masking plus the
misalignment"*. `d5733af` §S2 is a MANDATORY RECORD CORRECTION of precisely that: the whole-column
**shape** is the same, the **masking value is not** — at `8c7dfbb` the frozen column was the
*edited* experiment's own, so foreign values never acquired layer-(b) authority, whereas v6 mints it
for values from **another experiment's file**. This is class E (prose outrunning evidence) occurring
inside the document that names class E.

*Related advisory:* F's *"load-bearing, not hygiene"* for `--timeout=600` likewise inherits a v6
self-assessment; `d5733af` finds the value **does not achieve its purpose inside the harness** (it
is per-test and sits at the harness's own 600 s ceiling) and recommends 120 s.

**Root cause of all three: a green commit's self-report is a claim, not a record.** The synthesis's
own section E is the rule it needed.

## BLOCKING — Group 2: attribution (design B3, B4)

**B3. `settings-editor-learning.md §8` is not the earliest statement of amendment 16's rule.** I
verified the independent leg myself: `harness-hardening-learning.md §2`, in that file's **first
commit `c6628ea`, 2026-08-19**, states it verbatim — *"A test that cannot fail is not a backstop …
disarm the mechanism once and watch the test go red. If it stays green, it is guarding nothing"* —
three weeks earlier, and it is absent from class A's table. Further, §8 first appears `f9d7347`
**2026-09-09**, a day *after* amendment 16 was adopted (2026-09-08), and §8's rule is the
*diagnostic corollary* (*"when mutate-once does not red, diagnose which of the two it is"*), not the
gate. Evidence in `todo-mutate-once-gate.md`.

**B4. The inaccurate test name came from the Analyst's plan, not the Integrator's work order —
and I got this wrong too.** The name appears in exactly one place:
`plans/settings-management-plan.md:953`, hedged *"rename to what it covers (**e.g.**
`test_load_resolution_refuses_a_fifo_sidecar`)"*. My v5 work order (`8c7dfbb:todo.md`) says only
*"rename the overreaching test"* — `grep fifo_sidecar` returns nothing. Both of the synthesis's own
upstream sources say "plan" (`e1c0d63` body; transcript `D-41`). **I compounded this**: I twice
described the Developer as having corrected *my* prescription, taking credit for an error I did not
make. The lesson the residue carries — amendment 18 governs types but not identifiers — is correct
and untouched; only the author and the word "prescribed" (for an "e.g.") are wrong.

## BLOCKING — Group 3: claims in the commit body and the register (design B5, B6; converging with security H2 and test-reviewer F1)

**B5. "One saver rather than two" is not what the tree contains.** Two byte-identical copies remain,
which I confirmed at `example_nr_reduction.py:223` and `:293` — both `json.dump(make_json_safe(
config.__dict__), f, indent=2)` **after** `open(..., "w")`, i.e. both still carrying the
truncation-on-failure defect this commit calls *"a second defect the todo had not"*. The count of
weak savers went **3 → 3**; only the broken fourth was repaired. These are in `src/`, so they ship,
and the register already counts `example_*` modules as real callers
(`todo-fork-read-template-attributeerror.md` lists the documented example in its blast radius). In a
slug whose synthesis has a section titled *"One behaviour, two implementations — the divergent
copy"*, leaving two copies of exactly that class is the finding.
→ Correct the claim, or delegate the other two — they are identical, so it is one edit twice.

**B6. "Nothing drives the reduction entry point" is false, and it is the claim that makes the
survivor sound harmless.** `launcher/apps/file_batch.py:669` passes
`save_json=bool(self.save_json_checkbox.isChecked())` — a user checkbox labelled **"Save settings
JSON"** (`:145`). *"Exercised by no test"* is true; *"nothing drives the entry point"* is not. That
unguarded delegation is **the only path by which a scientist produces this JSON**, so the survivor's
stakes are higher, not lower. Fix the commit body and `todo-save-config-json-inverted.md`.

## BLOCKING — Group 4: two guard gaps (test-reviewer F1, F2)

**F1. `make_json_safe` is an independently-removable clause with no mutation row and no guard — and
it is load-bearing on the live GUI path.** Mutation R7 replaces the line with
`json.dumps(config.__dict__)` and **all six guards pass**. I verified the failure it would ship:
the GUI passes `datapath=Path(...)` → `new_reduction_from_file.py:68` stores it in
`_NEXUSpathRB_override` as a `PosixPath` → `json.dumps(config.__dict__)` raises
**`TypeError: Object of type PosixPath is not JSON serializable`**. Nothing catches it because the
fixture (`test_save_config_json.py:52-55`) sets all four overrides with `str(...)`, so
`make_json_safe` is a **no-op throughout the suite** (the file contains zero `Path(` and zero `np.`).
→ **Remedy, two fixture lines plus one ledger row:** `config.NEXUSpathRB = Path("/SNS/REF_L/IPTS-36119/nexus")`
and `config.IncidentTheta = np.float64(4.0)` — the types production actually assigns.

**F2. The truncation guard pins a weaker property than the commit and the closed todo claim.** Both
say *"a failed save destroyed the previous settings … a guard pins it."* The guard asserts
`not target.exists()` — that a refused save creates no **new** file — in a `tmp_path` where the file
never existed. Mutation R6 (open-first plus `unlink` on failure) **destroys the previous settings on
every failed save and passes all six guards.** The fix itself is real (verified: the shipped code
leaves the prior file byte-identical); the *guard* is not.
→ **Remedy:** write a prior file, refuse a save, assert the prior content survives. **And
`todo-save-config-json-inverted.md` should not be marked closed on the basis of a guard that pins
something else.**

---

## ADVISORY

- **The §11 justification for declining a source-text guard is misapplied** — outcome right, reason
  wrong. `assert "save_config_json(" in getsource(reduce_from_file)` *is not* satisfied by the
  mutant, so §11 ("ask what else satisfies the assertion") does not apply; and a **count**-based
  assertion would red mutation 5. The defensible reason is stronger: a text assertion pins text, not
  behaviour — it stays green if the delegation passes wrong arguments. One sentence, and the
  citation goes away.
- **The disclosed survivor is an inherited gap, correctly declined.** No test anywhere calls
  `reduce_from_file`; the genuinely behavioural option needs a real reduction. Recommend annotating
  `todo-untested-new-workflow-launcher-path.md` with this specific delegation as one concrete thing
  it would guard, so the debt is tracked where it is actionable.
- **The docstring's rationale for `__dict__` is factually wrong** though the choice is right.
  *"Round-tripping the public `Spath` would not survive `hasattr`-based loading"* — it does; `Spath`
  has a setter. The real trap is `base_path` (no setter). The *true* reason to prefer the private
  names: they re-derive paths from `experiment_id`, whereas the public form freezes them.
- **"Six guards" is 4 functions / ~3 properties**; guard 3 reds exactly when guard 1 reds and never
  otherwise. Not dishonest — it counts pytest items — but the informative count is smaller.
- **A's universal quantifier is unhedged** (*"the only one to recur in every slug that wrote
  tests"*) against the document's own evidence rule; cited evidence covers 7 of 13 slugs and
  `todo-mutate-once-gate.md` counts eight instances across **five**.
- **`settings_resolver.py:392` lands on the enclosing method** (`resolve_all`); the pad is in
  `_equalise_angles`. Precision, not truth — the docstring states the lesson nearly verbatim.
- **C's superlative is fragile** (*"the only class that can say that"*) and survives only on the
  reading "reached `exp` *through* this class".
- **"What a reviewer should attack" points at the wrong two claims** — it nominates the two
  `[inference]` readings, and both check out; all four content failures were **unhedged,
  non-`[inference]`** claims. design's summary is worth keeping verbatim: *the doc's self-audit
  looked where it had already been careful.*
- **Security, advisory, all pre-existing or latent:** the write is non-atomic and symlink-following
  (demonstrated overwrite through a symlink) while the repo already contains the hardened exemplar
  **`SettingsDocument.save`** (`settings_document.py:305`) which serialises the identical payload —
  `to_dict()` is literally `dict(self._config.__dict__)`. `open(…, "w")` still truncates at open, so
  ENOSPC/quota/SIGKILL between open and write still destroys the prior file; `os.replace` closes it.
  A `"__dict__"` key bypasses `json_to_config`'s `hasattr` gate (mass assignment → a settings file
  the tool itself wrote that it can no longer load; no code execution). `_Spath_override` from the
  untrusted file decides where the file is written, with no base-directory check. `make_json_safe`
  emits bare `NaN`/`Infinity` (not standard JSON) and coerces a callable to a repr string carrying a
  heap address.

## WHAT PASSED — verified, not relayed

Both original failure modes reproduce on the pre-fix code and are fixed. All four claimed mutation
reds reproduce **for the reason named** (test-reviewer re-ran them independently and disambiguated
row 1 in the author's favour: the claimed 3 is exactly right for the *isolated* clause mutation).
The `__dict__` choice is correct and its argument verifies — the four path fields are class-level
properties, absent from `__dict__`; only the `_*_override` privates appear, and the `hasattr` gate
accepts them. The delegation is output-identical. The refusal guard is a genuine observation.
"Zero callers" checks at the parent. No secrets, no `exec`/`eval`/`pickle`/`subprocess`/`yaml`.
**And the sizing argument is sound — this is the change the evidence pointed at, not a convenient
one**: the declined alternatives are properly evidenced, including `amend_config`'s 14 real
failures and the verbatim judgment that it *"needs its own slug with the seriousness B1 got"*, and
that changing a matching tolerance is a scientific decision.

## SHAPE OF THE FIX — small

Nothing requires re-doing the code, and the code has no defect. Five of the six design blockers are
**prose**, four of them from one root cause (trusting the v6 self-report 8 minutes before the review
that corrected it), and `d5733af` already supplies the replacement language for G, D and F. B3/B4
are one-line attribution repairs with the evidence named above. B5/B6 are two-line corrections to
`2136a8f`'s body and the register entry — or, for B5, the same delegation edit twice in
`example_nr_reduction.py`. F1/F2 are **~12 lines of test plus two ledger rows** in the file that
already exists.

## CORRECTIONS TO MY OWN CONDUCT THIS CYCLE

1. **My brief scoped the reachability question to `src/`.** Security concluded the only
   `save_json=True` caller was an `example_*` module and therefore that the truncation defect was
   *"latent, not live"* — sound for the path it examined. Then I "verified" it with the same
   `-- src/` scoping, reproducing my own brief's blind spot instead of catching it. test-reviewer
   searched wider and found the GUI. **When the question is "who calls this?", never scope the
   search to one directory.**
2. **I named `atomic_write_json` as the exemplar; it does not exist on this branch** — it is on
   `feature/settings-management`, which I had been reading all cycle. Cross-branch symbol
   contamination is a live hazard for a seat that drains slugs serially from different bases; name
   the branch when naming a symbol.
3. **I took credit for the `_fifo_sidecar` prescription twice** (B4). It was the Analyst's plan,
   hedged as "e.g.".
4. **My clone carried 10 stale local refs, including `exp` at `2127343` vs `6da473d`** — design
   nearly filed a false positive against it, because `--shared` reviewer clones inherit my refs.
   Fixed: 8 fast-forwarded; `feature/check-results-fields` and `feature/settings-editor` left
   divergent **deliberately**, because each holds an `integrator: clear resolved todo.md` §5a commit
   that exists nowhere else — no review tag, no analysis merge — and I will not destroy the only
   copy for tidiness. **Add a "sync local refs before gating" step to the contract's session setup.**
