# ESCALATION — `settings-management` (T3): extended cap reached (5 of N=5), Analyst decision required (3rd)

> **SUPERSEDED 2026-09-19 — the human approved a bounded v6 for B1 alone** on the
> charter §9 amendment-20 footing (decompose-don't-extend if the same shape recurs at
> a new level). v6 runs from the five-item scope in the plan's `### v6` entry;
> `triage/settings-management-v6` dispatched, the `review/settings-management-escalate`
> tag deleted. This file is kept as the record of the 3rd cap-reached moment.

> This file supersedes the v4/N=4 cap-reached escalation (which recommended, and
> received, the N=5 extension with the resolver invariant); prior versions are in
> `git log -- plans/settings-management-escalate.md`. It now records the **v5 /
> N=5-exhausted** escalation.

**Terminal state:** attempt 5 of the **extended N=5** rejected on **ONE** finding
→ third sanctioned escalation, per the v5 final-gate bar you set (*"a genuinely
new correctness defect escalates to me — there is no N=6 without a decision from
me"*). Rejection todo @ `8c7dfbb` (feature tip; gate green at `302116b`: **206
launcher + 396 reduction, EXIT=0, `pixi.lock` byte-identical, ruff clean, clean
fast-forward**). **Code, not infrastructure.**

## The slug is converging — this is not a failing slug

Findings per attempt: **v3 = 8 blocking · v4 = 2 blocking · v5 = 1 blocking.**
v5 landed everything you scoped — B1 (edit-time bind), B2 (worker teardown at the
window), B3 (sidecar FIFO gate), **and the resolver invariant** — and **three of
four domains found nothing blocking** (ui-aspects, security, test-reviewer all
explicitly clear). The mutation ledger audited clean; all 17 mutations red. One
domain (design) found one defect, reproduced independently.

## The one finding: B1 — item 1's edit-time bind freezes the per-angle row count

**`_session_edits[name] = self.document.get(name)` captures the *whole array* for
the 13 per-angle fields**, frozen at the row count as it stood at the keystroke.
When the count later changes, `resolve_all → _equalise_angles` pads the short
array and aligns every per-angle column to the **old** indices. Two triggers, no
Add/Remove click needed for the first:

- **Load** (the plan's own `edit → Load → Resolve`): a scientist with 2 angles
  types a direct beam on their 2nd; the experiment file has 3. After Resolve the
  file's three direct-beam references become one misplaced value + two `None`,
  badged `[b]` "set for this run", **"No problems found."**
- **Remove angle** (worse): resurrects a deleted run's array — wrong direct beam
  per angle, or none — and `save_settings` writes it to the file autoreduction
  reads; `json_to_config` accepts it. This is the exact hazard `_equalise_angles`'
  docstring exists to prevent.

**Failure path: wrong reduced data** (a reflectivity curve normalised by another
angle's direct beam, or none), silent, badged as the scientist's own input.

**Attributed, not inferred:** reverting **only** `_pre_resolve_overrides` to v4's
read-back restores correct alignment. **v4 read the array at *resolve* time, so a
structural change was reflected automatically; item 1 froze it at *edit* time and
inverted that.** The trade was a scalar defect (v4) for an array defect (v5) — and
the array one is worse: it discards the experiment file's per-angle references
entirely rather than substituting one wrong scalar.

**Why the gate could not see it:** all 206 launcher tests pass with the defect
present; the ledger's B1 rows exercise **scalars** (`qmax`) and the IPTS-change
pop — **no row varies the row count between the edit and the Resolve.**

## Provenance — shared, and I own my share

The Integrator states it is theirs: their v4 work order prescribed *"bind the
value at edit time — `_session_edits` becomes a dict `{name: value}`"* as
*"converged across all three domains,"* with security's *"do not clear on Load"*
caveat. **That prescription flowed through my v4 plan and my v5 plan transcription;
you adopted it verbatim; the Developer implemented it faithfully; three review
domains endorsed it.** For the 13 list-typed fields it meant something different
than for scalars, and **"bind at edit time" + "never clear on Load" is precisely
what freezes a stale row count.** Five parties — the Integrator, three domains,
and me (the plan author) — signed off without separating the scalar and array
cases. As the Analyst I should have flagged that a fix written for "a value" is
not type-safe for per-angle arrays; I did not.

## The fix (design-verified)

- **Robust form (the user's standard):** record per-angle (b) edits **per cell** —
  `{(name, row): value}`, reassembled against the current row count — type-correct
  for both scalars and arrays; cannot misalign.
- **6-line subset** (verified, 206 pass): in `_record_structural_change` rebind
  `for name in fs.PER_ANGLE_NAMES: if name in self._session_edits: self._session_edits[name] = self.document.get(name)`.
  Fixes **Remove-angle only**; the **Load** trigger needs the same rebind (or a
  pop) on the `set_document` path.
- **Bind a copy, not the live list** (`list(...)`): `SettingsDocument.get` returns
  the attribute itself — the hazard `_copy` exists for (test-reviewer A-10).
- **Guard test must vary the row count between the edit and the Resolve** — nothing
  in the suite does. (Caution: an `ipts_edit.setText()` *after* the edit fires
  `_forget_per_angle_edits` and pops the snapshot — set the IPTS **first**, or the
  probe wrongly reads "not reproduced.")

## Attempt synopsis

| Attempt | Feature tip | Outcome |
|---|---|---|
| v1 | `6365df4` | 7 clusters — resolver unwired |
| v2 | `8abfdce` | 11 clusters — guards prove one site of many |
| v3 | `ecc1e3b` | 8 clusters — C3/C4 born from v3's fixes → **N=3 → human extended to N=4** |
| v4 | `ce591fc` | 2 blockers — ledger works; C3 abort + C4 3rd door → **N=4 → human extended to N=5 + invariant** |
| v5 | `8c7dfbb` | **1 blocker** — invariant + B1/B2/B3 all landed, 3/4 domains clear; **item 1's edit-time bind is scalar-correct, array-wrong** → **N=5 exhausted** |

## Recommendation to the human

**(a) A bounded v6 for B1 alone — my recommendation, with the Integrator.** This is
the tightest possible final scope: one fully-diagnosed defect, a design-verified
6-line minimum and a known-better robust form (per-cell recording), on a slug that
has gone 8 → 2 → 1. The Integrator would fold, and I concur: the **mandatory
record corrections** (rename an over-reaching test, fix two prose items, and
**correct my v5 plan's ENXIO sentence** — item 3, flagged for factual review);
**advisory 1** (a test) and **advisory 2** (`--timeout` on the reduction task) —
the guards that would have caught this class; and **advisory 8** (the `LAYERS`
table — the deferred per-run-geometry feature *is* a new layer and the extension
is currently fail-open). Nothing else.

**(b) Accept-and-merge — I argue against, with the Integrator.** B1 silently
discards the experiment file's per-angle direct-beam references and badges the
result "set for this run", reaching the file autoreduction reads — the same
first-principle failure as v4's B1, one field-type over.

**(c) Amend in place** — the Integrator cannot (no feature code); the Analyst
writes plans, not code — so this means **you** apply the per-cell fix directly.

## The real lesson (a doctrine gap, worth an amendment)

The gate did its job at every level and still missed this: green suite, clean
ledger, 17 mutations red, three of four domains clear. **What failed was the
prescription** — correct for scalars, wrong for the 13 arrays it governed. **The
review gate validates *implementations against prescriptions*; it has no step that
validates a *prescription against the types it will act on.*** The Integrator has
filed a doctrine amendment for this; I endorse it and will route it. For the
Analyst specifically: a plan step that prescribes a fix for "a value" must state,
and a reviewer must check, whether it is type-correct for **per-angle arrays** as
well as scalars — the campaign's per-angle fields are a standing trap
(active-row, equalise-angles, and now edit-time-freeze are the same family).

Procedure if you extend: reply with the N=6 decision (and per-cell vs 6-line
subset, though per-cell is the robust default); I author v6 from this scope,
create `triage/settings-management-v6`, and the cycle resumes.
