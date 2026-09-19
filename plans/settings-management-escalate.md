# ESCALATION — `settings-management` (T3): v6 REJECTED → **DECOMPOSE** (amendment 20); ratify the split

> **This file supersedes the v5 / N=5-exhausted cap-reached escalation** (which
> recommended, and received, the bounded v6 for B1 on amendment-20 footing). Prior
> versions — the v3/N=3, v4/N=4, and v5/N=5 records — are in
> `git log -- plans/settings-management-escalate.md`.

**Terminal state (not a cap-count this time):** v6 was **rejected on a single
finding, B1′**, which is the **same *demonstrate-the-case-you-thought-of* shape at a
new level** — exactly the trigger the v6 `### amendment-20 criterion` names. Per that
criterion **and** amendment 20 (charter §9): **do NOT extend the cap — decompose the
slug into single-review-surface slugs (§4 sizing) and re-dispatch.** The
decompose-vs-extend decision is therefore **already made by the charter**; what
escalates to you (per the v6 final-gate bar: *"a genuinely new correctness defect
escalates to the human"*) is **ratification of the split shape** — descoping what T3
ships is a deploy-adjacent call you reserve (§7). Rejection tag
`review/settings-management` @ `d5733af`; gate was green at `ddb3981` (210 launcher +
400 reduction, EXIT=0; ledger audit clean, 12 rows / 12 mutations). **Code, not
infrastructure.**

## The one finding: B1′ — clearing a per-angle cell to `None` leaves a stale record

Clearing an `optional_list` per-angle cell (`LambdaMin`/`LambdaMax`) **leaves a stale
cell record**, so the deleted value returns at layer (b) badged "set for this run" and
redisplays in the table. `set_angle_field` deliberately collapses the column to `None`
— the sanctioned *derive-from-chopper* state — and **neither arm of `_record_edit`'s
per-angle branch fires**, so it neither records the clear nor removes the prior cell.

**Science impact, twice over:**
- `new_reduction_from_template` forces `lam_range` from `LambdaMin`/`Max`, **overriding
  the chopper-derived wavelength band** the clear was meant to restore;
- a two-gesture variant reaches `LAMBDA >= None` and **kills the reduction**.

**Confirmed five times independently** — design, ui-aspects, test-reviewer, security's
family, and the Integrator's own reproduction. **Attributed by A/B at three revisions:
v4 and v5 both handled this cell correctly, so v6 owns it** (a regression the per-cell
rewrite introduced). **No test in the suite clears a per-angle cell.**

## Why decompose — the fractal recurrence (amendment 20 fires exactly)

This is the **third consecutive attempt where the fix for the previous blocker
introduced the next**, always in the **same two functions** (`_record_edit` /
`_record_structural_change`), always a **value-shape the previous framing missed**:

| step | the shape that escaped |
|---|---|
| v4 → v5 | the value may be a **whole column** (array, not scalar) |
| v5 → v6 | the column may be **absent** — `None`-as-a-real-value |

`_session_edits` must represent **three states** — a **value**, a **whole column**, and
an **absent/`None` column** — and **each attempt has handled two of the three.**
Amendment 18 *worked* (the plan stated the type domain, which is why the array case was
covered) — **but it asks for *types*, not for the *states* a value can occupy, and
`None`-as-a-real-value is what keeps escaping.** A fractal recurrence at a new level is
evidence the slug is **too large for the per-attempt review model**, not that another
cycle converges. (Cross-slug context: the just-delivered
`plans/campaign-learnings-synthesis.md` names this the **per-angle-trap / edit-time
family**.)

## Proposed decomposition — two single-review-surface slugs (§4 sizing)

**Slug A — `settings-management` ships the clean subset (drop the layer-(b) pre-run UI
override path).** The Integrator's evidence that this is a **clean subtraction**, not a
retreat:
- the module already **declares layers it does not populate** — (d) by documented
  design, (e) with **zero production assignments** — so shipping with (b) deferred
  matches the existing pattern;
- **no T3 commit is an ancestor of `exp`**, and `exp` has **no `_session_edits` at
  all** — nothing regresses;
- **everything else in T3 verified clean across v5 and v6.**
  → a small **confirm-the-subtraction-and-ship** review surface (the resolver + layers
  (a),(c),(d),(e),(f), provenance, the record corrections, the three advisories).

**Slug B — pre-run UI override via *cell-level layer authority* (the real fix).** Two
reviewers independently name **cell-level layer authority — a resolver change** — as
the real fix, not another edit-recorder patch. This slug is framed around the **three
value-states enumerated UP FRONT** (value / whole-column / absent-`None`), reviewed as
a **resolver-authority** surface distinct from the UI-editor surface. `None`-as-a-real-
value (derive-from-chopper) is a **first-class state**, not an error case.

## Recommendation to you

1. **Ratify the split** — A ships the clean subset; B becomes a new §4 slug. On your
   go, I author both plans (B with the three states stated up front) and re-dispatch
   `triage/settings-management-*` (subset) and `triage/<B-slug>`. **I will not
   re-dispatch until you ratify** — the final-gate bar routes this to you.
2. **A doctrine gap worth an amendment (I will route it if you agree):** amendment 18
   governs a value's **type**; this finding shows the escaping dimension is the **set
   of states a value can occupy** (notably a sanctioned sentinel like `None`). Proposed
   sibling: *a fix prescription must enumerate the **states** its value can take —
   present, whole-collection, and any sanctioned sentinel/absent — not only its type;
   a reviewer checks the prescription against that state set.* Born from this
   escalation exactly as amendment 18 was born from the v5 one.

## Attempt synopsis

| Attempt | Feature tip | Outcome |
|---|---|---|
| v1 | `6365df4` | 7 clusters — resolver unwired |
| v2 | `8abfdce` | 11 clusters — guards prove one site of many |
| v3 | `ecc1e3b` | 8 clusters — C3/C4 born from v3's fixes → **N=3 → human extended to N=4** |
| v4 | `ce591fc` | 2 blockers — ledger works; C3 abort + C4 3rd door → **N=4 → human extended to N=5 + invariant** |
| v5 | `8c7dfbb` | 1 blocker — invariant + B1/B2/B3 landed; edit-time bind scalar-correct/array-wrong → **N=5 exhausted → bounded v6** |
| v6 | `ddb3981` | **1 blocker — B1′** (`None`-column state unhandled); **3rd fractal recurrence, same two functions** → **amendment 20: DECOMPOSE** |

Procedure on your ratification: reply with **go** (and any change to the split); I
author Slug A + Slug B plans, push analysis, create `triage/settings-management-*` and
`triage/<B-slug>`, and the cycle resumes as two right-sized surfaces.
