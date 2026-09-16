# Integrator: `settings-management` (T3) v5 — REJECTED on ONE finding. **N=5 EXHAUSTED — escalated.**

**Gate is GREEN** at `302116b`: 206 launcher + 396 reduction, both `EXIT=0`; `pixi.lock`
byte-identical to `exp` and untouched by every commit on this branch; ruff clean; clean
fast-forward. **Every mechanical acceptance criterion is met.**

**Three of four domains found nothing blocking.** ui-aspects (blocking domain): *"Nothing
blocks."* security: *"Nothing in the code should block."* test-reviewer: *"nothing blocks."*
**design found one, it is a science-correctness regression introduced by v5, and I reproduced
it independently.** Per the commit body's own rule — *"any genuinely new correctness defect
escalates to the human; there is no N=6 without a decision"* — this is a rejection **and** an
escalation.

**This one is my fault, and the work order says so before it says anything else.** See
"Provenance of the defect" below. The Developer implemented exactly what I prescribed.

---

## B1 — BLOCKING. Per-angle layer-(b) overrides are whole arrays frozen at edit time, so any
## later row-count change misaligns every angle's settings

`launcher/apps/settings_editor.py:489` (`_record_edit`) → `:611` (`_pre_resolve_overrides`),
with `:465` (`_record_structural_change`) and `:461` (`_forget_per_angle_edits`) as the sites
that should invalidate the snapshot.

Item 1 bound the layer-(b) value at edit time. **Correct for scalars. For a per-angle field
`self.document.get(name)` is the whole array**, so the snapshot freezes the row count as it
stood at the keystroke. When the count later changes, `resolve_all` → `_equalise_angles` pads
the short array and every per-angle column aligns to the *old* indices.

**My own reproduction** (`edit → Load → Resolve`, the plan's own sequence, no Add/Remove click).
Experiment file has 3 angles; the scientist has 2 and types a direct beam on their second:

```
experiment file  : RBnum=[900, 901, 902] DBname=['dbA', 'dbB', 'dbC']
typed DBname     : [None, 'db_typed_for_my_2nd_angle']
after Load       : RBnum=[900, 901, 902] DBname=['dbA', 'dbB', 'dbC']
stale (b) STILL  : [None, 'db_typed_for_my_2nd_angle']   <- 2 elements vs 3 angles

AFTER RESOLVE DBname: [None, 'db_typed_for_my_2nd_angle', None]
  angle 0 -> RBnum=900   DBname=None                         [b]
  angle 1 -> RBnum=901   DBname='db_typed_for_my_2nd_angle'  [b]
  angle 2 -> RBnum=902   DBname=None                         [b]
report: No problems found.
```

The experiment file's three direct-beam references are replaced by one misplaced one and two
`None`s, **badged "set for this run"**, with *"No problems found."*

design's second trigger (**Remove angle**) is worse — it resurrects a deleted run:

```
  angle 0 -> RBnum=111   DBname='db_for_222'      <- deleted run resurrected
  angle 1 -> RBnum=222   DBname='db_for_333'      <- wrong direct beam
  angle 2 -> RBnum=333   DBname=None              <- no direct beam at all
```

**Failure path: wrong reduced data.** A reflectivity curve normalised by another angle's direct
beam, or by none at all. `fs.refusals` does not refuse it; design ran `save_settings` and the
resurrected array lands in the file (`SAVED FILE RBnum: [111, 222, 333]`), and `json_to_config`
accepts it. This is the exact defect `_equalise_angles`' own docstring exists to prevent — *"a
short array … silently shifts every later angle's settings by one … which the resolver could
otherwise reintroduce one layer at a time."*

**New in v5 — attributed, not inferred.** I reverted **only** `_pre_resolve_overrides` to v4's
read-back and re-ran the same probe: `DBname: ['dbA','dbB','dbC']`, correct alignment. design
independently checked out `f28bba4~1` and got the same result on the Remove-angle trigger. v4
read the array at resolve time, so a structural change was reflected automatically. **v4 had the
scalar defect item 1 fixed and was safe for arrays; item 1 inverted that.** The trade was a
scalar defect for an array defect, and the array one discards the experiment file's per-angle
references entirely rather than substituting one wrong number.

**Invisible to the gate.** All 206 launcher tests pass with the defect present. The ledger's B1
rows exercise scalars (`qmax`) and the IPTS-change pop; **no row varies the row count between
the edit and the Resolve.** One caution for whoever writes the guard: an `ipts_edit.setText()`
*after* the edit fires `textChanged` → `_forget_per_angle_edits`, which pops the very snapshot
under test. My first probe did that and wrongly read "not reproduced." Set the IPTS first.

### Provenance of the defect — mine

My v4 work order prescribed this fix as *"bind the value at edit time — `_session_edits` becomes
a dict `{name: value}`"* and stated it was **"converged across all three domains."** I relayed
security's caveat *"do NOT simply clear the set in `set_document`"*. The human adopted both
verbatim into the v5 scope. The Developer implemented exactly that.

For the 13 list-typed fields the prescription meant something different than it did for scalars,
and **"bind at edit time" + "never clear on Load" is precisely what freezes a stale row count.**
Four of us signed off without noticing. design states the corollary that matters: **security's
caveat is right for scalars and unsafe for arrays, so the two cases must be separated rather
than governed by one rule.** test-reviewer looked at the same line (A-10) and asked whether the
alias diverges *in content* — it does not — which is why the *length* hazard survived a second
domain's attention.

### Fix

design verified a 6-line minimum in `_record_structural_change`, which already claims this
responsibility in prose (*"the array the experiment file supplied is not the array we now hold"*):

```python
for name in fs.PER_ANGLE_NAMES:
    if name in self._session_edits:
        self._session_edits[name] = self.document.get(name)
    self.provenance[name] = Resolved(...)
```

206 launcher tests still pass with it. **That fixes the Remove-angle trigger only**; the Load
trigger needs the same rebind (or a pop) on the `set_document` path. On the robust standard the
real fix is to record per-angle edits **per cell** — `{(name, row): value}`, reassembled against
the current row count — with the rebind as its strict subset. Also bind a copy, not the live
list (`list(...)`): `SettingsDocument.get` returns the attribute itself, which is the hazard
`_copy` exists for (test-reviewer A-10).

**Guard test must vary the row count between the edit and the Resolve. Nothing in the suite does.**

---

## MANDATORY RECORD CORRECTION (not blocking, but it does not ship uncorrected)

The commit body says item 3 *"closed the FIFO and symlink cases."* **That is false**, and I
measured it:

| | hardened `_read_json` | `SettingsDocument.from_file` (the first read) |
|---|---|---|
| FIFO named `reduce_settings_1.0deg.json` | refused, "not a regular file" | **blocked until timeout** |
| symlink | refused, ELOOP | **followed it** |

`load_settings:759` reads the user-picked file **first and unconditionally** via
`SettingsDocument.from_file` → a bare `open()`; `load_resolution` is only reached at `:766`, and
only when a sidecar exists. The same bare `open()` is the **autoreduction** entry
(`new_reduce_REF_L.py:108` → `new_reduction_from_file.py:52`), where security measured a FIFO in
`shared/autoreduce` **hanging the autoreduction job**.

**This is not an acceptance failure** — v5 delivered exactly the B3 scope I specified (*"route
the sidecar through `_read_json`"*), the wider Load/Save exposure was plan-deferred, and the
readers are untouched by v5 and pre-existing on `exp` (the GUI slot calling `from_file` arrives
with T2, already merged as PR #28). So it is not grounds for the rejection. But three artefacts
assert a property the code lacks: the commit sentence; `tests/test_settings_resolver.py:1163`
named `test_the_open_path_reads_through_the_same_gate` with a docstring saying *"on a file a
user picks"* while it calls `load_resolution(fifo)` directly and never touches `load_settings`;
and ledger row 17 headed *"the read gate, on both paths."* **Rename the test, correct the
heading, and state the residual plainly** — that a local `mkfifo` (not merely a stalled mount)
still freezes the GUI on Open and hangs autoreduction. I am carrying the correction in the PR
body regardless; the tree should not keep a test whose name outruns its coverage.

**Also correct the plan:** item 3 says a writer-less FIFO *"returns `ENXIO`"*. It does not —
`O_RDONLY|O_NONBLOCK` **succeeds**; ENXIO is the write-side. `O_NONBLOCK` is what avoids the
wait and `S_ISREG` is what refuses the file, exactly as the in-code comment says. **That error
is mine** — it entered in my v4 work order and the plan carries it verbatim.

---

## WHAT PASSED — verified, not relayed; do not re-litigate

v5 is a strong attempt and three domains cleared it. Recorded so the escalation is not read as
wider than one finding.

- **The invariant works and is pinned in both directions.** (b) arm alone reds 17; (a) arm alone
  reds 9; removing the gate reds 24. The standing guard is 16 cases (8 geometry fields × both
  doors) asserting the *value* is the measurement, on a directly-constructed context — the
  "third door". Companions pin the (f) fallback and that **the experiment file may still set
  geometry**. The **(a) arm is honestly declared redundant** with `GLOBAL_WHITELIST` and made
  observable by monkeypatching the whitelist to admit the field. design's verdict: **keep it** —
  redundancy that is *stated* and isolation that is *pinned* is defence in depth, not decoration.
- **B2 teardown is correct, load-bearing, and the mechanism is now understood.** Six-scenario
  subprocess matrix, `returncode == 0` plus a positive `"teardown-clean"` assertion. Mutating the
  parking off gives **exit 134** on `mid-resolve` and `stalled`; parenting the worker gives 134.
  **The v4-vs-v5 contradiction was a race, and nobody measured wrong:** ui-aspects showed that
  with *no* delay between `start()` and dropping the last reference the wrapper is sole owner and
  the drop deletes a running `QThread` (134), while after ~0.5 ms the worker's own executing
  `run()` frame holds two references and the drop is a no-op (exit 0). v4's probes slept; v5's
  did not. **v4's fix really was the cause of the abort, and "leak by holding" is right.**
- **B3's gate is correct on every shape security could construct** — FIFO, directory, socket,
  symlink, symlink→FIFO, `/dev/zero`, `/dev/stdin`, top-level list, oversize — every one refused
  with `ValueError`/`OSError` inside the guard's tuple, zero fd leaks. Routing `load_resolution`
  through it closed **four** axes, not the two named (symlink, size cap, `isinstance(dict)`,
  `S_ISREG`).
- **My v4 B1 scalar door is closed twice over** — `_session_edits` binds the value, *and* the
  invariant independently refuses a geometry value from any user layer. Either alone suffices.
- **The ledger audits clean.** Four v4 families still reconcile at the v5 tip (5 / 5 / 6 / 2,
  0 disjuncts). The frame is enumerated citing the amendment-16 refinement, the `/` rule is
  applied (the gate is two rows; the invariant one row per layer), v4's bundled C3 row is now
  **five** rows, and `_forget_worker`'s clearing is declared **"defensive rather than claimed as
  pinned"** instead of being credited a red it lacks. test-reviewer re-ran **all 17 mutations
  live: every one red, observed ≥ claimed.** Three mutations that failed to red on first pass
  were **the author's own tests**, written up rather than quietly fixed.
- **Item 5 genuinely fixed** — at `ce591fc` the test passed with
  `_last_error == "NameError: name 'ipts' is not defined"`; at the tip `_last_error is None`.
- **`_PARKED_WORKERS` is sound**: reclaim works, the worker is collected, 300 consecutive resolve
  cycles leave the list at 0, and holding it under an underscore name does not re-open the abort
  at `Py_Finalize`.
- **The badge does not lie after a Resolve** — a refused geometry edit shows `[e] measured from
  the data`, not `[b]`.
- No secrets, no `exec`/`eval`/`pickle`/`yaml.load`/`shell=True`; `atomic_write_json` unchanged
  and still correct; active-row trap still avoided; no `.destroy()` anywhere.

---

## ADVISORY — grouped; none blocks

**Guard gaps (the frame again, one level finer)**
1. **Ledger row 17 is a bundled row and its other half is a live survivor.** `load_resolution`
   routes **two** reads through the gate — the settings file (`:641`) and the **sidecar**
   (`:646`). Reverting only `:646` to a bare `open()` blocks forever on a FIFO sidecar and reds
   **nothing** (156 + 206 pass). One test fixes it: `os.mkfifo(provenance_path(real_file))`.
   *This is my v4 finding's shape recurring where the bundle was two call sites of one helper
   rather than two decisions in one sentence.*
2. **Both hang-pinned guards live in the only suite with no timeout armed.** `pyproject.toml:181`
   `test-reduction` carries no `--timeout`; `timeout_method = "thread"` arms none by itself. Under
   the `O_NONBLOCK` and Open-path mutations the reduction suite hangs past 150 s while the
   launcher suite passes. The ledger's "caught by a per-invocation `timeout`" is true of the
   author's harness, not of `pixi run test-reduction`. Add `--timeout`, or
   `@pytest.mark.timeout(30)` on the two.
3. **`@guarded`: still 9 sites, 1 pinned** — 8 survive removal, unchanged from v4, and still no
   ledger row. v5's teardown work did not make any of the 8 reachable. New: `shutdown` (`:696`) is
   slot-shaped (connected to `aboutToQuit`, called from `closeEvent`) and is **not** `@guarded`;
   `LauncherWindow.closeEvent` (`new_launcher.py:90`) is an unguarded Qt virtual, where any
   exception aborts. Unreachable today; the `try/except (TypeError, RuntimeError)` at `:715` also
   sits *inside* the loop while the `worker.finished_with` access that would raise sits in the
   loop header.
4. **`test_the_invariant_is_expressed_over_the_layer_class` is tautological and inverted** —
   asserts `set(USER_AUTHORITY_LAYERS) == {"a","b"}`, and adding the future user-authority layer
   its docstring promises to protect is exactly what makes it **fail**. The real property is
   testable: monkeypatching the tuple to `("a","b","c")` flips a (c)-sourced geometry field to
   (e), because the gate reads the tuple at call time.
5. **`_release_busy`'s exactly-once guard still has no red** — replacing `if self._busy:` with
   `if True:` passes 206. Qt's `restoreOverrideCursor` on an empty stack is a no-op, so the
   assertion holds either way. Carried from v4.
6. **The matrix has no scenario firing `closeEvent` *and* `aboutToQuit`** — which is what
   production does. Built, it exits 0 with `shutdown` called twice (so "safe twice" is verified);
   coverage gap only. Worth a seventh parameter.
7. Ledger "observed" column is per-named-test and **undercounts six rows** (all in the safe
   direction) — which is the mechanism by which (1) stayed invisible. Row 18 is a control, not a
   mutation: "18 rows" is 17 + 1, disclosed but worth stating.

**The invariant's edges — for the deferred badged-override design**
8. **`USER_AUTHORITY_LAYERS` is derived over fields and enumerated over layers, and the extension
   is fail-open.** It is the **fourth** hand-maintained layer list beside `LAYER_ORDER`,
   `HUMAN_LAYERS`, `LAYER_LABELS` and `DISCOVERY_LAYERS`. design added a hypothetical 7th layer
   `g` to `LAYER_ORDER` and `_layer_sources` only: `dSampDet` resolved to **layer g, 99999.0**,
   and exactly **one** test red — an exact-tuple equality about *ordering*. Robust form: one
   `LAYERS` table mapping each letter to (order, label, authority), with a test asserting every
   member of `LAYER_ORDER` carries an authority classification. **Fix this before the deferred
   feature, because that feature is precisely a new layer.**
9. **The invariant governs the resolve walk; Save is a second authority channel.** type
   `dSampDet=99999` → Save writes it **plus** a sidecar `{"source_layer": "b"}` → next Resolve
   returns it at layer **(c)** badged as the experiment file, and discovery never reads the
   sidecar, so the on-disk record that *a person typed it* is never shown. Design-consistent —
   the human sanctioned (c)/(d) — but it contradicts the body's *"not something an edit does as a
   side effect"*, and the scientist's outcome depends on **button order**: type→Save honours the
   value, type→Resolve→Save discards it, with no message either way. Decide which is the contract.
10. **A refused geometry edit is silently discarded and remembered forever** — no message
    anywhere, and `_session_edits` keeps it permanently, re-offered and re-refused on every
    Resolve, and it would spring back to life the day the deferred feature relaxes the gate.
    Suggest one report line and dropping the name when the resolver refuses it.
11. **`emission_coefficients` is in `GEOMETRY` but is not a measurement** (no PV, no "unset reads
    the instrument") — the invariant now bars a typed value for a correction-model parameter. And
    both the `GLOBAL_EXCLUDED_GROUPS` docstring and the test's `GEOMETRY_FIELDS` hard-code **8 of
    the group's 9** fields, so the standing guard under-covers the group it names. Derive from
    `fs.fields_in(fs.GEOMETRY)`.
12. **Layer (e) still has zero production callers**, so "geometry resolves to (e)/the measurement"
    is a test-only guarantee; in the shipped app geometry falls to (c) or (f), and the measurement
    arrives because the (f) default `None` means "read the PV downstream". The invariant is sound;
    the sentence naming (e) describes a layer nothing fills.
13. **A bad PV now has no in-GUI correction path**, order-dependently (see 9). Worth a release note.

**Hardening overrun (new in v5)**
14. **Opening a symlinked settings file that has a sidecar now fails outright.** v5 routed
    `load_resolution` through `_read_json`, importing `O_NOFOLLOW` **and** the 4 MB cap onto a
    dialog-picked path. `from_file` succeeds (follows the link), then `load_resolution` raises
    ELOOP, `except Exception` pops "Could not load settings", and `set_document` never runs — the
    whole Load is abandoned for a file v4 opened fine, and **the editor writes a sidecar on every
    Save**, so it bites files the editor itself produced. A facility symlink farm
    (`current.json → reduce_settings_up.json`) is exactly the shape that breaks. Fail-closed and
    the user is told, so advisory — but item 3 asked only for the *sidecar* read, and
    `load_resolution` reads both. **Give `_read_json` a `follow_links`/`max_bytes` parameter:
    refuse for discovery, permit for Open.** Keep `O_NONBLOCK` + `S_ISREG` on both — that is the
    hang gate and what item 3 required. Also: `load_settings` now parses the settings file twice
    and throws the second parse away, so provenance is bound to a read the document did not come
    from.
15. **PySide6 breaks every B2 guarantee, and it is importable in this env.** `qtpy` defaults to
    PyQt5 and nothing pins `QT_API`. Measured under PySide6: drop → 134, parented → 134, **and
    parking → 134** (abort at finalization). The matrix would red wholesale under
    `QT_API=pyside6`. Pin `QT_API` (`launcher/app_identity.py` is the natural home) or record the
    binding dependency in the `_PARKED_WORKERS` comment.

**Prose that no longer matches the code**
16. `settings_editor.py:646-649` still says the mechanism is *"deleting on `finished`"*; v5
    replaced `deleteLater` with `_forget_worker`, which deletes nothing. **This slug was rejected
    once for lying prose.** One-line edit.
17. `_PARKED_WORKERS`' comment describes the **stalled-mount** case, which was already safe
    (measured exit 0 with and without parking). The window parking closes is the sub-millisecond
    pre-`run()` race. Replace with the measured mechanism so nobody "simplifies" the parking away
    after failing to reproduce the stalled abort — or trusts it for the stalled case, where it is
    inert.
18. `aboutToQuit` was **not** wired in v4's `main()` at all; the commit body says it was. The
    ledger's phrasing (an intermediate v5 state) is the accurate one.

**Carried from v4, re-checked against v5 and still open**
19. The `b`→`b*` downgrade is still at the call site (`settings_editor.py:766`), so
    `load_resolution` still hands back authoritative-looking `"b"` — v5 made that function the
    hardened twin without moving the downgrade into it.
20. `fs.refusals` is still write-side only; `json_to_config` is still a bare `setattr` loop, so
    autoreduction still reads an unvalidated file — measured accepting `dqbin=0.0`,
    `dSampDet=-1.0`, `nx=-5`. This matters more now that the invariant is the load-bearing
    control, because it guards a door the untrusted file does not use.
21. Sidecar `source_layer` unvalidated and rendered as **rich text** (`AutoText`), downgrade is
    exact-match `== "b"` so `"b "`/`"B"` pass through — provenance spoofing from a group-writable
    share. Validate against `LAYER_LABELS` + `setTextFormat(PlainText)`.
22. Stale sidecar: a new value wears an old origin; no digest, as the plan's own remediation asked.
23. `.dat` Save writes JSON that Load cannot read — a successful Save yielding an unrecoverable
    file. One-line fix: drop `.dat` from the Save set.
24. `global_settings.py:158` still states pre-decision precedence; `settings_resolver.py:65`
    still says `user_chosen()` reads `LAYER_ORDER` when it reads `HUMAN_LAYERS` — in the comment
    whose own thesis is that a declaration its implementation ignores is worse than none.
25. `provenance_path` still collides on `.stem`; `user_chosen` and `SettingsDocument.normalize`
    still have zero production callers; `dead_time_tof_step` still `minimum=0.0` while whitelisted
    and a denominator; no `gitleaks`/`detect-private-key` hook and `.gitignore` carries only
    `.env`.
26. **Corrections to earlier reviews, recorded so they stop propagating:** security's v4 L2
    implied a poisoned layer-(a) preference outranks the experiment file — `LAYER_ORDER` puts (a)
    **below** (c)/(d), so it does not. security's v4 advisory 6 said `load_resolution`'s
    `AttributeError`/`KeyError` escape the guard — true of `_guarded_step`'s tuple, false in
    production, because `load_settings` catches bare `Exception`. design's v4 note bundling
    `O_NOFOLLOW` with the size cap and type check was wrong on a dialog-picked path (see 14).

---

## ESCALATION — the human's decision

Attempt 5 of the extended N=5. **One blocking finding**, and it is a regression introduced by
the fix I prescribed. Options:

**(a) A bounded v6 for B1 alone — my recommendation.** The scope is one defect with a verified
6-line minimum and a known-better robust form (per-cell recording), plus the mandatory record
corrections (rename the overreaching test, fix the two prose items, correct the plan's ENXIO
sentence). I would additionally fold **advisory 1** (one test) and **advisory 2** (`--timeout` on
the reduction task) because they are the guards that would have caught this class, and
**advisory 8** (the `LAYERS` table) because the feature you deferred *is* a new layer and the
extension is currently fail-open. Nothing else.

**(b) Accept-and-merge with B1 recorded — I argue against.** It silently discards the experiment
file's per-angle direct-beam references and badges the result "set for this run", reaching the
file autoreduction reads. It is the same first-principle failure as v4's B1, one field-type over.

**(c) Amend in place** — outside my contract.

**A process note, offered because it is the real lesson.** The gate did its job at every level
and still missed this: the suite is green, the ledger audits clean, all 17 mutations red, and
three of four domains cleared it. What failed was **the prescription** — a fix I specified, three
domains endorsed, you adopted, and the Developer implemented faithfully, which was wrong for 13
of the fields it governed. The review gate validates implementations against prescriptions; it
has no step that validates a prescription against the *types* it will act on. That is worth a
doctrine amendment independent of what you decide here, and I have filed it.
