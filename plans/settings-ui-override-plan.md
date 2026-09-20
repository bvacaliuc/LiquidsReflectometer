# Plan: settings-ui-override (Slug B of the T3 decompose) — PARKED, deferred to a subsequent campaign

> **Status: PARKED (human decision, 2026-09-19).** The T3 decompose (charter amendment
> 20) split `settings-management` into Slug A (the clean subset — shipping now) and this
> Slug B (the pre-run UI-override path). The human deferred Slug B to a **subsequent
> campaign** to reach T1 (roi-selector) for the scientists' review sooner. This file
> **preserves the fully-diagnosed root cause and the required design** so the later
> campaign starts from the insight, not from scratch. **Do NOT dispatch** without a
> fresh human go.

## Why this is its own slug (not another settings-management attempt)

Four attempts (v3→v6) each fixed the previous blocker in the **same two functions**
(`_record_edit` / `_record_structural_change`) and introduced the next, because the
per-run UI-override path is **too large for the per-attempt review model** (amendment
20). Two reviewers independently name the real fix as **cell-level layer authority — a
resolver change**, not another edit-recorder patch. Slug B is that resolver-authority
surface, reviewed on its own.

## The root cause, fully stated (so the next campaign does not re-derive it)

`_session_edits` (the layer-(b) store) must faithfully model **three value-states**, and
every prior attempt handled only two of them:

| state | meaning | which attempt missed it |
|---|---|---|
| **a value** | a scalar override typed by the scientist | (handled since v4) |
| **a whole column** | a per-angle array (`fs.PER_ANGLE_NAMES`, 13 fields) | v4→v5 missed it (froze the array at edit time → `_equalise_angles` misalign) |
| **absent / `None`** | a *cleared* per-angle cell — the sanctioned **derive-from-chopper** state | v5→v6 missed it (B1′: neither arm of `_record_edit` fires when `set_angle_field` collapses the column to `None`, so the deleted value returns badged "set for this run") |

**`None`-as-a-real-value is not an error case** — it is a first-class state meaning
"derive this field from the chopper." Amendment 18 (state the *type* domain) was
necessary but insufficient: it governs the value's **type**, not the **set of states**
it can occupy. See `tasking/plan/todo-prescription-not-validated-against-types.md`.

### Why per-angle edits are experiment-bound (routed here from the v7 stale comment, I-40)

A layer-(b) per-angle edit is **bound to the experiment (IPTS) it was typed against**, unlike a
scalar override. Changing the IPTS/experiment (`ipts_edit.setText(...)`) fires
`_forget_per_angle_edits`, dropping the per-angle snapshot — because a per-angle value is only
meaningful for *that experiment's* angle set; carrying it onto a different experiment's angles would
misalign (the same `_equalise_angles` hazard the whole slug exists to prevent). **Scalars survive a
Resolve; per-angle edits do not survive an experiment change** — `test_global_settings.py:573` pins
the scalar half. v7's item-2 comment stated this rationale but had drifted to the opposite claim
after its connection was removed; it was deleted in v8, and the correct statement lives here so Slug
B reintroduces the mechanism with the reason intact. **Slug B's tri-state authority must preserve
this:** a cleared/`None` cell and an experiment change are different transitions, and only the
scalar layer is Resolve-durable.

## Required design (the robust form)

Represent layer-(b) authority **per cell**, resolved at **resolve time** against the
**current** row count, with an explicit tri-state:

- `set(name)` / `set(name,row)` → an explicit override (value present);
- `cleared(name,row)` → an explicit "derive from chopper" (the `None` state), which the
  resolver must honor as an *authoritative* instruction to fall through to the
  chopper-derived value, **not** a stale prior override;
- absent → layer (b) has no opinion; resolve from (c)–(f).

The resolver — not the edit-recorder — owns this authority. The three states are
**enumerated up front** in the Slug B plan and **each gets a mutate-once guard** that
varies the row count between the edit and the Resolve (the class of test no attempt has
had). Bind copies, never the live `SettingsDocument.get` attribute.

## Interaction to check at dispatch time

- **upstream #197** (`tasking/plan/contrib/review-exp-json-settings-builder/**`): an
  upstream JSON-settings-builder variant. Before dispatching Slug B, check whether #197
  already provides pre-run override / per-cell entry functionality — it may fill part of
  this gap or conflict with the resolver-authority design. Reconcile per the T1 stacked-
  contribution approach.
- **T1 (roi-selector)** does **not** depend on Slug B (it consumes the resolver core),
  so this deferral does not block T1. Confirm no T1 code assumes a populated layer (b).

## Acceptance (when the subsequent campaign runs this)

- Layer (b) populated by a resolver-owned tri-state authority; all three states carry a
  row-count-varying mutate-once guard; `_equalise_angles` alignment preserved.
- `new_reduction_from_template` respects a cleared cell (does not force `lam_range` from
  a stale value); no path reaches `LAMBDA >= None`.
- design + ui-aspects + test-reviewer blocking; verify-prose on the state enumeration.
