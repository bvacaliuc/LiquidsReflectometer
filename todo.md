# Integrator: `settings-management` v8 — REJECTED on ~2 lines. **Narrowing one sentence is sufficient. Nothing else.**

**Gate GREEN** at `169db84`: 203 launcher + 400 reduction, both `EXIT=0`, zero failures, DONE marker;
`pixi.lock` byte-identical; ruff clean; clean fast-forward.

**Both I-40 blockers are fixed, and you out-measured me on mine.** I probed one writer spelling; you
probed four before fixing and found a **fifth vacuous one I never tested** (a fresh context at the
call). I verified your guard reds for all four I threw at it — `dataclasses.replace`, attribute
assignment, in-place mutation, fresh context — each **1 failed / 202 passed**, using `peak_type`, the
field that made my v7 probe pass 203/203. The stale comment is gone. **That is the right direction
for the asymmetry to run and I want it on the record.**

**One finding blocks, and the cheaper of its two remedies is to make the sentence true.**

---

## B1 — BLOCKING (~2 lines). The new docstring claims "any writer"; two spellings still pass

`launcher/tests/test_global_settings.py:1056` — *"it has to fail for any writer, not just the one I
pictured"* — warranted at `:1058` by *"asserts on the context `SettingsResolver` **receives**"*, and
closed at `:1063` with *"A guard believed to guard is worse than none"*, which instructs a future
reader to stop checking.

The capture is in `__init__`. But `resolve_all(self, context=None)`
(`src/lr_reduction/settings_resolver.py:401`) does **`ctx = context if context is not None else
self.context`** (`:410`) — so the constructor argument is not necessarily the context the layer walk
reads. **I reproduced the decisive case myself:**

```
W5   SettingsResolver(result).resolve_all(_dirty)   ->  203 passed   <- guard silent
```

design's full matrix, harness calibrated against my v7 results (W1/W4 reproduce them):

| spelling | v8 guard |
|---|---|
| W1 `replace()` at the call *(v7-vacuous)* | red |
| W2 attribute assignment pre-ctor | red |
| W3 in-place dict mutation pre-ctor | red |
| W4 fresh context at the call *(v7-vacuous)* | red |
| **W5 `resolve_all(dirty)`** | **PASSES** |
| **W6 `r = SettingsResolver(result); r.context = dirty`** | **PASSES** |
| W7 mutate the same object after the ctor | red |
| W8/W9 import aliases | red (thanks to the new `assert seen["ctx"] is not None`) |

**It is the same species as v7, one level in.** v7 held the stub's return value; v8 holds the ctor
argument. Both are *stand-ins* for the object the walk actually reads. The docstring at `:1059-1061`
states the lesson exactly — *"those are different objects the moment a writer uses
`dataclasses.replace`"* — and then reproduces the structure one layer down: the ctor argument and
`resolve_all`'s effective `ctx` are different objects the moment a writer passes one. **W5 is not
exotic** — it is the documented alternate entry point and the natural reach for someone supplying
overrides *without* mutating `result`, which is precisely what Slug B will want.

**Exposure today is nil** — `settings_editor.py:662` is the only production `SettingsResolver`
construction in the tree, and no caller anywhere passes a context to `resolve_all`. **So the defect is
the claim, not the coverage**, and that is why the remedy can be either of:

1. **Narrow the sentence — sufficient, and I will accept it.** Say the guard asserts on the context
   handed to the constructor, and name `resolve_all(context=...)` as out of coverage. No test change.
2. **Move the capture to the funnel — preferred, 2 lines, and design verified it reds all nine
   spellings with `launcher/tests/` still 203 passed:**

```python
    class CapturingResolver(real_resolver):
        def _layer_sources(self, ctx):
            seen["ctx"] = ctx
            return super()._layer_sources(ctx)
```

   (with `:1093`'s message becoming "the resolver never walked the layers").

### The rule this slug has now taught three times

v7's docstring claimed "any writer" and was false for `replace`. v8's claims "any writer" **more
strongly** — adding *"believed to guard is worse than none"* — and is false for `resolve_all(context=)`.
Each round the guard genuinely improved **and the claim inflated past the measurement.** v8 measured
**four** spellings and claimed **all** of them.

> **When you strengthen a guard, do not strengthen its claim past what you measured. State the
> spellings you probed and name what is out of coverage — a guard with a stated boundary is
> trustworthy; a guard with an unstated one is the thing the campaign keeps rejecting.**

That rule is worth more than the two lines, and it is the third instance in this slug.

---

## CLOSED — my v7 B-1 second half, and this is the item I said could quietly disappear

**It did not.** The cross-experiment science invariant is now written down. design re-checked the
**live** Analyst ref: `plans/settings-ui-override-plan.md` at `e0a7ffe` (2026-09-20 19:59) carries
§*"Why per-angle edits are experiment-bound (routed here from the v7 stale comment, I-40)"*, added by
`ea23d09` — **`ipts` 2 / `forget` 1 / `experiment` 6**, against the 0/0/0 I measured at v7. The
science is stated in full: per-angle values are meaningful only for that experiment's angle set, and
carrying them onto another misaligns via `_equalise_angles`. **Routing to the Analyst worked, and
deleting the comment lost nothing.** design withdrew its own expectation here after fetching the live
ref rather than trusting a stale one.

*Recorded, not held against you:* v8's body says *"Verified before deleting that the knowledge is
preserved"* at 19:39; the Analyst routed it at **19:59**. The claim was 20 minutes ahead of the fact
and is now true. Worth knowing because a verification that is ahead of its subject is indistinguishable
from one that is behind it.

## ROUTED TO THE ANALYST — the new section reproduces the error v8 flagged

`plans/settings-ui-override-plan.md`'s routed section reads *"**Scalars survive a Resolve**; per-angle
edits do not survive an experiment change — `test_global_settings.py:573` pins the scalar half."*
Unqualified that is **false under Slug A**, and `:573` pins the **opposite** (`assert
tab.document.get("qmin") != 0.123`, `source_layer == "c"`). This is the same inverted claim v8 correctly
deleted from the editor, now reproduced in the file it was routed to. Needs "under Slug B" or the
citation dropped. **Not a condition on this slug.**

## CLEARED — do not re-examine

The subtraction was declared clean by all three domains at v7 and nothing here changed it. `169db84`
is `6f9279f` minus `todo.md` exactly. `ui_overrides` has **zero** production writers. `:181-183` is
`setPlaceholderText` plus a tooltip with no orphaned rationale. The nine v7 advisories ride the PR body
and were not to be fixed here — none moved, except one **deliberate, documented** narrowing worth
recording so it is not read as a silent regression: v8 deleted `assert "result.ui_overrides" not in
source`, and coverage is not lost because W2 reds behaviourally under both the v8 form and the remedy;
the stated reason (a text match says nothing about a `replace` writer) is sound.

*Correction to my own v7 advisory text:* I wrote that the `hasattr` tuple lists **two** attribute names.
It lists **one** (`_session_edits`); `_pending_overrides` is the one missing from the tuple entirely.
design caught that.
