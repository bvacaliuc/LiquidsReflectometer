# Integrator: `settings-management` (T3) v6 — REJECTED. **Recommend DECOMPOSE (amendment 20), not v7.**

**Gate is GREEN** at `ddb3981`: 210 launcher + 400 reduction, both `EXIT=0`, zero failures, zero
real timeouts; committed `pixi.lock` byte-identical to `exp` with **no** commit on the branch
touching it; ruff clean; clean fast-forward. **Every mechanical acceptance criterion is met**, and
the ledger audit the bar assigns me **passes** (12 rows / 12 mutations; site counts reconcile).

**One finding blocks, and it is confirmed five times independently** — design, ui-aspects,
test-reviewer, security's S1/S2 family, and my own reproduction. It is a **new correctness defect
introduced by v6's own fix**, in the type domain amendment 18 exists to govern.

**Three of four domains independently invoke amendment 20's decompose criterion.** So does my
recommendation. See §RECOMMENDATION — this is the substance of the work order, not the bug list.

---

## B1′ — BLOCKING. Clearing an `optional_list` per-angle cell resurrects the deleted value at
## layer (b), and one variant kills the reduction

`launcher/apps/settings_editor.py:534` (the `elif` in `_record_edit`), with
`src/lr_reduction/settings_document.py:269` (`set_angle_field`'s `optional_list` collapse) and
`launcher/apps/settings_editor.py:673-685` (`_pre_resolve_overrides`' unconditional pad).

`set_angle_field` deliberately collapses `LambdaMin`/`LambdaMax` back to `None` when the last
populated cell is cleared — the sanctioned *"derive it from the chopper ranges"* state, which that
code exists specifically to protect (*"without this, touching one Lambda cell is a one-way door
out of that state"*). `_record_edit` then runs with `current is None`, **both arms of the
per-angle branch are False, and it neither records nor removes** — so cells from earlier
keystrokes survive, describing a column that no longer exists. `_pre_resolve_overrides` rebuilds a
length-`n_angles` column and overlays them, and layer (b) — the top of `LAYER_ORDER` — hands the
resolver a materialised list where the document says `None`.

**My own reproduction, through the real cell widget and a real Resolve:**

```
after typing 2.5 : document = [2.5]     _session_edits = {('LambdaMin', 0): 2.5}
after CLEARING   : document = None      _session_edits = {('LambdaMin', 0): 2.5}   <- stale
                   overrides = {'LambdaMin': [2.5]}
AFTER RESOLVE      LambdaMin = [2.5]  layer = b
table cell 0 now shows '2.5'            <- the deleted value is back on screen
```

**Science impact, two ways.** `nr_reduction_config.py:68` documents `LambdaMin = None` as
"calculated from the chopper ranges", and `new_reduction_from_template.py:247-248` forces
`template.lam_range = [LambdaMin[0], LambdaMax[0]]` whenever both are non-`None` — so a
resurrected value **overrides the chopper-derived wavelength band**, changing which wavelengths
enter R(Q), badged `[b] "set for this run"`. And design's two-gesture variant (clear angle 1, then
angle 0 → `[None, None]`) reaches `nr_reduction_calc.py:452`
`mask = (LAMBDA >= config.LambdaMinUse)` with `LambdaMinUse = None` →
**`TypeError: '>=' not supported between instances of 'float' and 'NoneType'`. The reduction
dies.** `fs.refusals` returns `[]` for it, so Save writes it into the file autoreduction reads.

**New in v6 — attributed, not inferred.** Same probe at three revisions:

| | `_session_edits` after the clear | resolved |
|---|---|---|
| v4 `ce591fc` | `{'LambdaMin'}` | `None` ✓ |
| v5 `8c7dfbb` | `{'LambdaMin': None}` | `None` ✓ |
| **v6 `ddb3981`** | `{('LambdaMin',0): 2.5}` | **`[2.5]`** ✗ |

The whole-column form recorded `None` and was correct here; the per-cell form is not.

**Why nothing caught it: no test in the suite clears a per-angle cell.** `setText("")` appears
once in `launcher/tests/`, on an unrelated `folder_edit`; nothing asserts on an `optional_list`
through the editor at all. All 210 launcher tests pass with the defect live.

**Honest mitigator** (design's, and it matters): unlike v5's B1 this is **not silent** — the
validation panel prints *"Lambda min is set for some angles but not angles [0]"* after the
Resolve. That puts it at the low end of blocking. It is still a deleted number re-applied with
user authority, and a crash in the reducer.

**Verified remedy (design's, 17 lines, tested):** take the not-a-list case **first** in
`_record_edit` — drop that field's tuple keys and record the deliberate `None` whole, since it has
no row count to go stale. Both probes return to the v4/v5 outcome with 210 + 264 still green.
**Caveat for whoever lands it:** also pop the whole-column key when a cell is recorded. The
collapse→retype round trip currently yields the right answer only because the cell loop happens to
run after the scalar loop — make the two key shapes mutually exclusive **by construction, not by
loop order**.

---

## RECOMMENDATION — decompose the layer-(b) session-edit mechanism out of this slug

**This is the third consecutive attempt in which the fix for the previous blocker introduced the
next one, always in `_record_edit`/`_pre_resolve_overrides`, always a value-shape the previous
framing did not cover:**

| | the fix | the shape it did not cover |
|---|---|---|
| v4 → v5 | bind the value at edit time | the value may be a **whole column** |
| v5 → v6 | record **per cell** | the column may be **absent** (`None`) |
| v6 → ? | ← B1′, plus security's S1 and S2 | |

`_session_edits` must represent three states — a scalar value, a per-cell value, and *"this column
is not set at all"* — and each attempt has handled two of the three. **Amendment 18 worked**: the
v6 plan did state the type domain and per-type behaviour explicitly, which is why the *array* case
was covered this time. What it did not ask for is the **states a value can occupy**, and
`None`-as-a-real-value is the state that keeps escaping. That is a sharpening of amendment 18, not
a failure of it — and it is the second time this mechanism has taught it.

**Amendment 20 exists for exactly this** — decompose when the same shape recurs at a new level —
and v6 *ran on* that footing while extending anyway. Three domains reached the criterion
independently.

**So: cut the layer-(b) UI-override path out of T3 and ship the rest.** Concretely, `ui_overrides`
is never populated; `_session_edits`, `_record_edit`'s recording duty, `_pre_resolve_overrides`,
`_record_structural_change`'s rebinding and `_forget_per_angle_edits` all go; the badge keeps
reporting the layer that actually won.

**Why this is a clean subtraction and not a hack — verified:**

- **The module already declares layers it does not populate.** `DISCOVERY_LAYERS = ("c",)`, with
  `settings_resolver.py:298` and `:548` explaining why **(d)** is declared-but-unpopulated; and
  **(e)**'s `dataset_probe` has **zero production assignments** (grep: two hits, both in tests).
  Making **(b)** a third declared-but-unpopulated layer is consistent with the design as it
  stands, not a deviation from it.
- **Nothing is lost from `exp`.** No T3 commit is an ancestor of `exp` (I checked all six), and
  `exp`'s `settings_editor.py` contains **no `_session_edits` at all**. There is no UI-override
  behaviour in production to regress.
- **Everything else in T3 verified clean across v5 and v6** and is the part with the value: the
  resolver and its layer walk, the geometry invariant with its 16-case standing guard, the
  `LAYERS` table, the read gate hardened on all three `_read_json` call sites, the worker teardown
  with its six-scenario subprocess matrix, discovery's `_guarded_step`, the badges, the
  validate-or-refuse doors. Six clusters closed semantically, verified by injection.
- **Two reviewers independently name the real fix**, and it is not in this function:
  **cell-level layer authority** — a resolver change. That is a slug of its own, designed once,
  rather than a fourth patch to a mechanism that has failed three times.

**Then make "pre-run UI override (layer b)" its own slug**, with cell-level authority designed in
from the start and the three states enumerated up front. Its acceptance bar should require a guard
that varies **each** of: the row count, the value's presence (`None` collapse), and the document
identity (a Load) — between the edit and the Resolve.

If the human prefers a v7 over decomposition, the minimum is B1′'s 17-line remedy **plus**
security's S1 and S2 below — but that is patch four on this mechanism, and the recurrence table
above is the argument against it.

---

## The other new v6 regressions — fold into whichever path is chosen

**S1 (security, demonstrated) — a removal during an in-flight resolve rebinds cells against a row
count the resolve then restores.** `_pending_overrides` is snapshotted at `:710` *before*
`worker.start()`; `_discovery_finished` consumes that stale snapshot and `set_document` restores
the pre-removal row count, but the keys were already shifted down. Measured end state
`['file0.dat', 'typed.dat', 'typed.dat']` where the file said `file1.dat`, badged as the
scientist's. **Correct at `8c7dfbb`.** Note `remove_angle_button` is **not** disabled while
`_busy` — only `resolve_button` is. Fix: if `self._busy`, `_forget_per_angle_edits()` instead of
rebinding (cells can no longer be attributed to a row), and disable the add/remove buttons
alongside resolve.

**S2 (security, demonstrated) — the cross-experiment path is NEW, and the commit body says it is
inherited.** The green commit discloses *"v5 had the same masking plus the misalignment"*. Half
right: the whole-column **shape** is the same, the **masking value is not.** At `8c7dfbb` the
frozen column was the **edited** experiment's own, so foreign values never acquired layer-(b)
authority; v6 mints it for values from **another experiment's file**, over that experiment's own
record, saveable into `shared/autoreduce`. `load_settings` is the door — it replaces the document
and touches neither `_session_edits` nor `ipts_edit`. **Correct the PR body: this is a new data
path, not an inherited one.**

**Reachability is wider than disclosed (design A2, ui-aspects, security S2 — three domains).**
`tthd_edit` has **no** forgetting wiring, and tthd's sign selects the up/down settings file via
`select_by_geometry` — so the masking is reachable **without an IPTS change**, against a different
settings file for the same experiment. Cheap bounded mitigation entirely inside the editor: wire
`tthd_edit` like `ipts_edit`.

---

## MANDATORY RECORD CORRECTIONS

1. **"A cell whose row no longer exists is dropped" is false** — `:661` docstring *and* the green
   commit body. It is dropped from the *override*, not from `_session_edits`, and **re-applies if
   the index returns to range**. Measured (three domains): 3 angles → edit row 2 → Load a 1-angle
   experiment → Add angle → the destroyed angle's direct-beam file lands on the scientist's fresh
   blank angle at layer (b). Strictly better than v5, so a residual — **but this slug was rejected
   once for prose claiming a property the code lacks.** Fix the prose, or prune on `set_document`.
2. **My ENXIO correction did not land in place.** The correct statement is at
   `plans/settings-management-plan.md:951-953`, but the erroneous sentence **survives verbatim at
   `:871`** — so a reader of item 3 still meets the false claim. That error is mine, from the v4
   work order; supersede it in place rather than appending the correction.
3. **The ledger omits v5's "defensive rather than pinned" note.** Two clauses cannot be killed by
   any mutation — the `row is None` per-angle branch (unreachable, as the body admits) and the
   `0 <= row < len(current)` bound (`set_angle_field` pads first). Neither is a defect; v5's ledger
   declared its equivalent explicitly and v6's does not, so the frame reads as fully pinned when
   two members cannot be.

---

## ADVISORY

**Frame under-enumeration — the next clause of amendment 16.** `_pre_resolve_overrides` is **one**
ledger row but **four** independent rules, and two are live unpinned survivors (full 210-test
suite, measured): the **`None`-pad at `:677-678`** (removing it gives `IndexError` on a sanctioned
short column — caught by `@guarded`, so a failed resolve, not corruption) and the **`placed` flag
at `:684`** (`if placed:` → `if True:` mints `DBname` at layer (b) carrying the *experiment file's
own* value when every recorded cell is out of range — **v4's C4 door-2 class, which v4 did give a
row**). `copy.deepcopy` has 3 sites and 1 row; the per-angle site is defensive-not-live, honestly
classified as ledger debt.
→ **New clause: a block introducing several independent guards is several rows, even at one call
site.** v5's lesson was one row over two *call sites*; this is one row over several *rules*.

**The pad destroys three sanctioned short-column forms, not two** (design A1, pre-existing —
`8c7dfbb` reaches the same end state via `_equalise_angles`). `settings_document.py:338-355`
sanctions `broadcast_ok` at length 1, `default_if_empty` at length 0, and any length for
`runtime_owned`. Measured: a length-1 `method_per_run` broadcast becomes
`['constantQ', None, None]`; an empty `tof_min` becomes `[None, 12000.0, None]` and
`nr_reduction_calc.py:106` then does **not** fill the defaults because the list is truthy — so
**`None` reaches Mantid as a TOF bound** with the panel saying "No problems found." This is the
general statement of the disclosed residual and belongs recorded with it.

**Item 4's `--timeout=600` does not achieve its purpose inside the harness** (test-reviewer). It
is **per test**, and it sits **at the harness's own 600 s command ceiling** — the ceiling that
killed two v5 invocations and motivated `todo-mutation-harness-restore-safety`. A hung test
therefore hits the harness kill at or before pytest-timeout fires, yielding no pytest report:
the outcome item 4 was added to prevent. The guards it protects run in 0.01–0.02 s.
**Recommend 120 s**, matching `test-launcher`. Two corrections to my own brief, from security:
`--timeout-method=thread` **cannot** leave a wedged thread — pytest-timeout 2.4.0 calls
`os._exit(1)`; and 600 s is not "effectively none" in CI, where the workflow sets no
`timeout-minutes` and the fallback is GitHub's 6-hour default. Also: `--timeout-method=thread` on
the CLI duplicates `timeout_method = "thread"` already in `[tool.pytest.ini_options]`.

**Item 5 folded 2 of 5 layer lists.** `LAYER_LABELS` and `USER_AUTHORITY_LAYERS` now derive;
`LAYER_ORDER`, `HUMAN_LAYERS` and `DISCOVERY_LAYERS` remain hand-maintained beside the table, and
`order` — which the plan asked for — was not folded. **`HUMAN_LAYERS` carries the identical
fail-open shape `USER_AUTHORITY_LAYERS` just lost:** a new `"user"` layer would not appear in it,
so `user_chosen()` would not count it. Latent today; the deferred badged override is the layer that
opens it. Also `Layer.key` duplicates the dict key with **zero readers** and nothing asserting
`LAYERS[k].key == k`, so `"e": Layer("f", …)` is undetectable — a third copy of the layer letter
in a change whose purpose was removing drift.

**Two assertions in `test_the_derived_layer_tuples_are_projections_of_the_table` pull against each
other.** `LAYER_LABELS == {k: v.label …}` restates the defining line (not vacuous — row 10 kills
it — but tautological in form). And `USER_AUTHORITY_LAYERS == ("a","b")` re-freezes the literal
the table was introduced to remove: declaring the deferred override as `"user"` **delivers the
protection and reds three tests**. Defensible as a change-detector, but it means "a reviewer must
update three assertions", not "the new layer just works" — say so, or nobody will read those reds
correctly.

**The forgetting guard asserts internal state, not the outcome.** Ledger row 8 is real, but the
assertion is on a private dict's contents; no test drives a **Resolve after an IPTS change** and
checks the resolved column. A key-shape change already silently disabled this behaviour once — the
standing test should be the observable one.

**`Resolved.from_record` admits any layer string from a sidecar** (security S5, pre-existing,
bounded). Forged `source_layer` reaches the badge and `user_chosen()`, never the walk
(`ui_overrides` comes only from `_session_edits`). Validate against `LAYERS` — the table makes it
free — and note `source_detail` reaches `setToolTip`, which Qt renders as rich text.

**Item 4 reds a hang as a run-level abort (`EXIT=1` + stack dump), not a `FAILED`** — valid, and
`thread` is the only method that reaches a thread blocked in `open()`, but the ledger should say so
or the next reader takes it for an infrastructure flake.

**Mutation harness housekeeping** (security S8): `plans/scripts/settings_management_v6_mutations.py`
never deletes its backups and the backup→file mapping exists only in stdout — so after a SIGKILL,
the exact failure mode `todo-mutation-harness-restore-safety` was written for, a reader cannot map
them back. Otherwise clean: list-form `subprocess`, mode-600 backups, restore in `finally` with
sha256 verification and abort-on-mismatch.

---

## CORRECTIONS TO THE REVIEWS — recorded so they do not propagate

- **Security's ship recommendation rests on a false premise.** It argues blocking v6 *"would leave
  a strictly wider defect (the `8c7dfbb` whole-column freeze) in production."* **No T3 commit is
  an ancestor of `exp`** — I checked all six — and `exp`'s `settings_editor.py` has no
  `_session_edits` at all. Both defects are absent from production; rejecting v6 leaves nothing
  there. Its *findings* (S1, S2) stand and are demonstrated; the verdict reasoning does not.
- **Three reviewers reported clone 3's pixi env as stale and warned the gate would abort on
  `--timeout`.** `.pixi/envs/default` **is** stale (missing `sympy`, `pytest-timeout`,
  `periodictable`), but it is **not** the env `pixi run` uses: pixi redirects to a detached env at
  `~/.cache/rattler/cache/envs/…`, where all three are present. My gate's own banner shows
  `timeout-2.4.0` loaded and `test_timeout_backstop_fires` passing. **No `pixi install` is needed**
  and the gate result stands. Reviewers who bypass `pixi run` will keep hitting this; the brief
  should name the detached env.
- **A ` M pixi.lock` in the session tree was attributed to the Developer.** It was **mine** —
  `pixi run` rewrites it (amendment 14) and my probes invoked it. Restored; tree clean.
