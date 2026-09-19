# Integrator: `settings-management` v7 (Slug A) — REJECTED, NARROWLY. **The subtraction is clean. Two additive fixes, ~8 lines. Do not re-litigate anything else.**

**All three domains say the subtraction is clean**, and so do I. design: *"the subtraction is
clean … no B1-family member is reintroduced."* ui-aspects: *"nothing blocks. The subtraction is
clean."* test-reviewer: *"nothing blocks … I could not find a single case where the removal took
coverage of behaviour that remains."*

**Gate GREEN** at `d98aba0`: 203 launcher + 400 reduction, both `EXIT=0`, zero failures, DONE
marker; committed `pixi.lock` byte-identical to `exp` with no branch commit touching it; ruff
clean; clean fast-forward. **The flagged deviation is ACCEPTED** — see below; you were right to
keep `_reattribute` and right to flag it.

**One finding blocks, and I reproduced it myself.** It is not a defect in the removal; it is that
the guard protecting the removal does not protect it. Remedy already written and verified by the
reviewer who found it: **3 lines.** Plus 5 lines of stale comment. That is the whole rejection.

---

## B1 — BLOCKING. The layer-(b) pin is blind to the spelling a dataclass invites, and its docstring claims otherwise

`launcher/tests/test_global_settings.py:1082` (behavioural guard), `:1107-1108` (source guard);
production site `launcher/apps/settings_editor.py:667`.

`test_the_editor_never_populates_layer_b` asserts on `seen["ctx"]` — the context **the discover
stub returned** — so it only sees a repopulation that *mutates that same object*. The source guard
only sees the literal text `result.ui_overrides`. But `ResolutionContext` is a **`@dataclass`**
(`settings_resolver.py:285`), so `dataclasses.replace()` is the idiomatic way to supply it, and the
site at `:667` passes `result` *into* `SettingsResolver` — a `replace()` writer never touches what
the guard inspects.

**My own reproduction**, restore-first, sha- and symbol-verified:

```
MUTATED: a layer-(b) writer via dataclasses.replace, field="peak_type"
  -> 203 passed in 26.34s          <- the entire launcher suite, green
restore verified by sha: MATCH     symbol check: dataclasses=0, ui_overrides assignments=0
```

test-reviewer's fuller matrix, which I am relying on for the gradient:

| spelling at the population site | reds |
|---|---|
| `result.ui_overrides = {...}` | 3 |
| `setattr(result, "ui_overrides", {...})` | 2 — **source guard blind** |
| `SettingsResolver(replace(result, ui_overrides={"qmax": …}))` | 1 — **both new guards blind** |
| same, `ui_overrides={"peak_type": …}` | **0 — 203 passed** |

**Why this blocks when nothing ships broken.** The guard has exactly one job: it is **the handoff to
Slug B.** This slug's entire purpose is to defer a mechanism *for later reintroduction*, and the
guard is the artefact that is supposed to make that reintroduction safe. It does not, for the
spelling a dataclass most invites. And its docstring states the opposite in terms:

> *"A future change that reintroduces a writer … will fail here rather than at a scientist's
> Resolve."*

That sentence is false, and **a guard believed to guard is worse than no guard** — the campaign's
standing lesson, and the reason amendment 16 exists. This slug has already been rejected once under
the title *"lying prose"*, and my own v6 work order made record corrections mandatory for exactly
this shape. I am applying that consistently rather than making an exception because the verdict is
otherwise a pass.

test-reviewer classified it Advisory and said explicitly: *"if you read that clause as 'the guard
must actually guard,' this is your blocker."* I do. The acceptance bar's clause is *"a removal with
nothing preventing its return"*, and for the idiomatic spelling nothing does.

**Remedy — 3 lines, written and verified by test-reviewer (reds on all four spellings, passes on the
shipped tree).** Assert on the context the *resolver* receives, not the one discovery returned:

```python
real = mod.SettingsResolver
def spy(ctx, *a, **k):
    seen.append(dict(ctx.ui_overrides)); return real(ctx, *a, **k)
monkeypatch.setattr(mod, "SettingsResolver", spy)
...
assert seen == [{}], f"the resolver received a populated layer (b): {seen}"
```

**And fix the docstring to match what the guard does**, or the next reader inherits the same false
assurance.

## B2 — BLOCKING (5 lines of prose; design's B-1). An orphaned comment asserts the capability v7 removed

`launcher/apps/settings_editor.py:181-185`. The `ipts_edit.textChanged → _forget_per_angle_edits`
connection is gone; its five-line rationale comment survived as a context line, now above
`setPlaceholderText`. It is false in both halves, present tense:

- it documents a per-IPTS forget behaviour that no longer exists — nothing is forgotten because
  nothing is retained;
- *"Scalar choices (\"for this run, use qmax=0.4\") are not experiment-bound and **survive**"*
  asserts layer (b) itself. The build's own guard asserts the opposite —
  `test_global_settings.py:573`: `assert tab.document.get("qmin") != 0.123, "deferred layer (b)
  must not survive Resolve"`. ui-aspects measured it: `qmin 0.123 → 0.002` across a Resolve.

Two domains found this independently (design B-1, ui-aspects advisory 1). **Fix: delete the five
lines, or rewrite them to say (b) is unpopulated so there is nothing to forget and no edit survives
a Resolve.**

### Routed to the ANALYST, not to you — the half that actually loses knowledge

design established that `plans/settings-ui-override-plan.md` (68 lines) contains **zero**
occurrences of `ipts`, `forget` or `experiment`. I verified: 0/0/0. So once B2's comment is deleted,
the tree contains **no statement anywhere** of why per-angle edits are experiment-bound — the
science invariant that carrying one experiment's per-angle arrays into another applies them to a
different set of measurements. design's words, and I agree: *"the plan line is the half that must
not be dropped — that is where the science knowledge is actually being lost."*

**That is the Analyst's file and a future slug's plan, so it is not a condition on this slug.** It
is recorded here and in the review tag so it is not lost, and I am raising it to the Analyst
separately.

---

## THE DEVIATION IS ACCEPTED — you were right, and right to flag it

Both blocking-capable domains accepted it independently, on grounds stronger than the ones you
gave:

- **It is not a deviation from item 1 read precisely.** Item 1 says remove *"the pre-run **'set for
  this run'** badge population **that feeds layer (b)**"*. The quoted phrase **is**
  `LAYERS["b"].label`, and `_reattribute` writes `b*` = "set for a previous run (not applied)" and
  **feeds nothing**. You removed what item 1 names.
- **The bar required keeping it.** Item 2's keep-intact list includes provenance badges/origins
  (NFR-8) and the bar says "Provenance intact". Deleting `_reattribute` would have red
  `test_every_scalar_edit_path_reattributes_its_field` (×3) and
  `test_a_per_angle_cell_edit_reattributes_its_column` — removing tested behaviour under cover of a
  subtraction.
- **`b*` is structurally unable to be a source**, verified in the walk rather than the table by two
  domains: `_layer_sources` builds `available` as a literal four-key dict `{a,b,c,d}` and intersects
  it with `LAYER_ORDER`; live result `['b','c','d','a']`. `b*` is in neither, carries authority
  `"none"`, is absent from `USER_AUTHORITY_LAYERS` and `HUMAN_LAYERS`, and `Resolved.as_record()`
  serialises origin only — so even the B1′ `None`-column shape is inert. `user_chosen()` has zero
  production callers.
- **Keeping (b) in `LAYER_ORDER` with `"user"` authority is FORCED, not merely defensible.**
  `tests/test_settings_resolver.py:1119` `test_a_non_geometry_field_still_honours_a_this_run_override`
  is the positive control for the 16-case geometry invariant; drop (b) and it fails **and** the
  invariant's own `via-layer-b` half starts passing **vacuously**. Your resolver comment's reasoning
  — *"the protection must not have to be re-derived by whoever adds one"* — is correct.

## CLEARED — verified, do not re-examine

- **Coverage:** all eleven deletions traced to surviving equivalents by two domains plus me; **no
  deleted test covered behaviour that still exists.** The two *weakened* kept tests each retain an
  end-to-end assertion of the same property — strictly better than the private-dict assertions they
  lost. Delta reconciles **exactly**: launcher 210 → 203 = 11 deleted − 4 added; `tests/` 400 at both
  revisions.
- **B1′ and its whole family are gone**, driven through the real widgets: B1′ verbatim (clear a
  `LambdaMin` cell → `None` at layer `f`), the S1 mid-flight door, the S2 cross-experiment door, the
  row-returns-to-range door, Add/Remove/Load — `ui_overrides == {}` throughout.
- `_record_structural_change`'s *"powerless in the walk"* claim is **finally true**, pinned at walk
  level by `test_adding_an_angle_does_not_mint_authority`.
- Teardown untouched (zero diff hits for `PARKED`/`shutdown`/`_reclaim`); 6-scenario matrix intact;
  `.destroy()` grep-guard clean. The `tthd` masking door and the "cell is dropped" prose are **moot**,
  verified moot rather than merely unmentioned.
- No dangling calls; the four remaining references to removed symbols are deliberate comments.
- Resolver diff is comment-only. `ruff` clean. Lock clean.

## ADVISORY — record while you are in here; none of these blocks

1. **The symbol guard's `hasattr` clause is vacuous for the two attribute names it lists.** I
   verified against v6's own code: `self._session_edits = {}` is set in `__init__` (`:156`), so it is
   an **instance** attribute and `hasattr(SettingsEditorTab, "_session_edits")` is `False` even when
   live. The loop genuinely pins the four *methods*; the mechanism's **namesake** is carried only by
   the source-text clause. And **`_pending_overrides` — in your own removal list — is absent from the
   tuple**; ui-aspects restored `self._pending_overrides = {}` and all 58 tests passed. Fix: move the
   two attribute names into the source-grep clause, add `_pending_overrides`, and say in the docstring
   which names the loop can see.
2. **Mutation row 3 is miscredited.** M2 (`_reattribute` → `return`) and M3 (grants `"b"`) red the
   **identical six** tests, all asserting `badge == "[b*]"` — so row 3 is a **label** guard, not an
   authority guard, and `_reattribute` cannot grant authority in this build at all. The authority
   guards are `test_the_editor_never_populates_layer_b` (after B1's fix) and, in the untouched
   resolver tests, `test_the_previous_run_layer_carries_no_authority` plus the 16-case invariant.
   Record which row pins which.
3. **No v7 ledger section and no committed v7 mutation script.** `plans/scripts/` has only the v6
   harness, whose 8 mutations target code that no longer exists. Per the repo's capture-documented-
   methods rule, the four v7 mutations should be reproducible from the tree, and the ledger should
   state the new frame (2 sites: `_reattribute`, `_record_structural_change`).
4. **Resolve discards unsaved edits with no warning at the moment it happens.** Pre-warning exists
   (`[b*]` + "not applied" tooltip), which is why this is advisory; but `resolve_for_experiment`
   never consults `changed_vs_seed()`, and the report's "Changed from the seed" line disappears when
   `resolve_all` reseeds. Naming the discarded fields in the status line is cheap.
5. **`b*`'s label is stretched.** Measured tooltip on a value typed seconds earlier: *"set for a
   previous run (not applied) (changed in this session)"* — self-contradictory. Its docstring
   (`settings_resolver.py:141-152`) enumerates only two producers and explicitly excludes "typed";
   v7 added a third. Also *"(not applied)"* is true only of the **walk** — the value **is** written
   into the saved JSON and would be applied by autoreduction reading that file.
6. **The three green figures overlap and none is what the pixi task collects.** "318" = 160 resolver
   + 158 unit; "242" = 400 − 158; the two overlap on the same 160. Union is the 400 `test-reduction`
   collects, so nothing is unrun — but report it as `tests/unit (158) + tests/ minus unit (242) = 400`.
7. Add/Remove stay enabled while `_busy`; a structural change mid-resolve is silently discarded by
   `set_document` (advisory 4's class, two lines to close). A stale `# v5 — B1:` banner at
   `test_global_settings.py:882` has no tests under it. The `"b"`→`b*` sidecar remap is now dead for
   editor-written files — keep it for legacy and Slug B, but say whose `"b"` it demotes.
8. **`_forget_worker` → no-op is GREEN** — nothing asserts the tab releases a *completed* worker.
   **Pre-existing, not caused by the subtraction** (no deleted test could have caught it either).
   Test debt for whoever touches worker lifetime next.
9. The bar's literal *"no `_session_edits` reference remains in `src/`"* is violated only by
   `settings_resolver.py:117`, the comment explaining the deferral. **The bar's wording should be
   amended**, not the comment — its stated purpose ("the removed helpers are gone, verify by symbol")
   is met. Three domains flagged this rather than silently deciding; the call is recorded here as mine.

## WHY THIS IS A NARROW REJECTION

Six attempts on this slug were rejected for defects. **This one is not.** The subtraction is
correct, the deviation was the right judgment, the coverage is intact, and B1′ is gone at the root
rather than patched. I am rejecting on ~8 lines — a 3-line guard strengthening whose remedy is
already written and verified, and 5 lines of stale comment — because the guard's single job is the
Slug B handoff and it currently fails that job while claiming otherwise. **Nothing else in this work
order requires action; the CLEARED section exists so you do not re-examine it.**
