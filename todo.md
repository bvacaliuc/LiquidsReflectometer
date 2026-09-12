# Integrator: `settings-management` (T3) v4 — REJECTED. **N=4 EXHAUSTED — escalated to the human.**

**Gate is GREEN** at `2be5d04`: 194 launcher + 350 reduction, both `EXIT=0`. `pixi.lock`
byte-identical to `exp`. ruff clean. **Every finding below is invisible to the gate**, as
it was for v1, v2 and v3.

**The mutation ledger works.** This is the first attempt where the amendment-16 record was
auditable, and it audits clean. I reconciled all four counts against `grep -c` (5 / 5 / 6 / 2,
def excluded); test-reviewer independently re-ran **all 18 enumerated mutations and found no
survivor**. The ledger even records two mutations that failed to red on first pass, one a real
gap. **Do not re-litigate the four enumerated families — they are closed.**

**There is no v5.** This was attempt 4 of the extended N=4. Contract §4 gives me no
discretion on a blocking finding, and the budget escape covers infrastructure failures only.
So this file is a rejection *and* an escalation: the human chooses between a second cap
extension, accept-and-merge with the findings recorded, or an in-place amendment.
**My recommendation is at the bottom.**

---

## THE ROOT CAUSE — the defect class did not recur, it MOVED UP ONE LEVEL

v1–v3 failed on: *the code got a shared helper, the helper got one test, and the test count
matched the behaviour count rather than the call-site count.* v4 fixed that **for the four
families it enumerated**. Both surviving blockers are the same shape one level up — a
**safety property carried by a line no test touches**, where the ledger's frame does not
reach:

| | shared rule | sites | pinned | the unpinned line |
|---|---|---|---|---|
| B2 | the C3 ledger row bundles **two** code decisions under **one** red | 2 | 1 | unparenting at `:617` — *the only thing preventing exit 134* |
| A1 | `@guarded` | 9 | 1 | 8 survive removal (advisory: no reachable abort demonstrated) |
| B1 | layer-(b) authority is recorded as a **name**; the value is bound later | — | — | `set_document` never clears `_session_edits` |

**So the mechanical rule is right and insufficient: it counts the sites of the helpers you
enumerate. Enumerating the *frame* is the next step** — before writing the ledger, list every
shared rule in the diff (decorators, sentinels, bundled "X / Y" descriptions), not just the
helpers you changed. A ledger row whose description contains "`/`" is two mutations.

---

## B1 — BLOCKING. C4 is not closed: one keystroke and an ordinary File→Open put a *file's*
## geometry value above the measurement

**Reproduced four times independently** — design, ui-aspects, security, and me — with
different values and different baselines. Security reproduced it against **the shipped C4 pin
test's own fixture with one line added**.

`launcher/apps/settings_editor.py:121` `_session_edits = set()` · `:456` `add(name)` ·
`:576-580` `_pre_resolve_overrides` · `:493-499` `set_document` · `:686-723` `load_settings`

`_session_edits` stores **names**. `_pre_resolve_overrides` binds the value **late**:
`{name: self.document.get(name) for name in self._session_edits}`. `set_document` replaces the
whole document and never clears the set. So the person's act authorizes a *name*, and whatever
value later occupies it inherits that authority.

My run — **no sidecar exists at all**:

```
after typing: _session_edits = {'dSampDet'}   overrides = {'dSampDet': 2500.0}   <- the person's value
after load:   _session_edits = {'dSampDet'}   overrides = {'dSampDet': 99999.0}  <- the FILE's value
RESULT dSampDet value=99999.0 layer='b'  badge: [b]
experiment file said 1234.0 ; the DATA measured 1000.0 ; nobody typed 99999.0
```

The resolver makes it unconditional, not incidental — `settings_resolver.py:310`:

```python
if layer == "a" and name not in GLOBAL_WHITELIST:
    continue
```

**Only (a) is whitelist-gated.** (b) is gated on nothing and (e) is consulted only after every
layer misses, so a (b) entry *necessarily* outranks the experiment file and the measurement.
That is precisely what excluding geometry from layer (a) on 2026-09-12 exists to prevent: a
preference must never override a measurement. The badge reads `[b]` / "set for this run" for a
number nobody set this run, and `save_settings` writes it to the file autoreduction reads.

The per-angle variant additionally defeats `_forget_per_angle_edits`, whose entire purpose is
to stop one experiment's per-angle arrays being applied to another's runs — a Load performs
exactly that carry and the guard does not fire. It promotes a `None`-padded array over the
experiment file's complete one, and `refusals` passes it.

**Why v4's own test cannot see it:** `test_a_sidecar_cannot_promote_geometry_above_the_measurement`
(`launcher/tests/test_global_settings.py:676`) builds a **fresh tab** — its docstring premise is
"Nobody typed anything." The defect lives one keystroke before that premise. v4 closed the
sidecar→provenance→authority door and left the document→authority door open.

**Fix — converged across all three domains.** Bind the value at edit time:

```python
# _record_edit                 self._session_edits[name] = self.document.get(name)   # dict, not set
# _pre_resolve_overrides       return {n: v for n, v in self._session_edits.items() if n in fs.BY_NAME}
# _forget_per_angle_edits      for n in fs.PER_ANGLE_NAMES: self._session_edits.pop(n, None)
```

**Security's caveat, which matters: do NOT simply clear the set in `set_document`.** That also
fires after a completed Resolve, and would silently drop the scientist's typed override on a
second Resolve — trading this bug for a different one.

**Guard:** add one prior `_on_scalar_edited("dSampDet", ...)` to the existing pin test; it must
still assert `1500.0` at layer `"e"`. Verified red today.

---

## B2 — BLOCKING. C3's load-bearing half is unpinned, and the guard credited with it never
## runs in the shipped app

Three domains, converging from different directions.

**(a) The one-word survivor.** test-reviewer split the ledger's bundled row
("parent the worker **/** drop `closeEvent`") into its two decisions:

| mutation | full launcher suite |
|---|---|
| drop the `closeEvent` let-go block (`:653-673`) | 2 failed ✓ |
| add `self` as the worker's parent (`:617`) — **one word** | **194 passed — SURVIVOR** |

and the survivor is v3's crash verbatim: `QThread: Destroyed while thread is still running`,
`EXIT=134`, versus `EXIT=0` as shipped.

**(b) Why the other half cannot substitute.** `SettingsEditorTab` is a child of the
`QTabWidget` in `LauncherWindow` (`launcher/new_launcher.py:53`). Qt delivers `QCloseEvent`
only to the widget being closed, so **the tab's `closeEvent` never runs** on the real quit
path. Instrumented independently by design and ui-aspects:

```
closeEvent seen on the settings tab: []
override cursor after closing the window: <QCursor>   # never restored
tab._discovery_worker still held: True                 # never let go
```

So neither the disconnect nor the "wait cursor released exactly once" guarantee applies to the
shipped app, and the no-abort outcome is delivered by the **unparenting at `:617`** — the half
with no test.

**(c) A live abort by a second door.** `_discovery_worker` is never cleared when the worker
finishes, while `finished → deleteLater` destroys the C++ object. `closeEvent` then calls
`isRunning()` on a dead wrapper; an unhandled exception in a PyQt virtual reaches `qFatal()`:

```
RuntimeError: wrapped C/C++ object of type _DiscoveryWorker has been deleted
  File ".../settings_editor.py", line 667, in closeEvent
tabclose_after_done -> exit 134    repeat_min -> exit 134
```

In-process `processEvents()` does not deliver `DeferredDelete`, so the suite cannot see it.
**The two defects mask each other:** this is unreachable from today's launcher *only because*
`closeEvent` is dead. Fixing the reachability — the obvious next edit, since it is also the fix
for the accumulation the commit body names — ships the abort on every close-after-resolve.

**(d) The acceptance criterion is literally unmet.** v4 requires C3 be **"subprocess-proven"**.
There is no subprocess test of any teardown path; exit 134 is only observable out-of-process.
The repo already has the idiom twice (`test_settings_persistence.py:490`, `test_harness.py:211`).

**Fix:** clear the reference on finish (`worker.finished.connect(self._forget_worker)`), make
`closeEvent` defensive, put the teardown where teardown happens (`LauncherWindow.closeEvent`
forwarding, or `QApplication.aboutToQuit`), and add the window-level subprocess matrix: idle /
mid-resolve / stalled resolve / repeated cycles / **close-after-completed-resolve**, each
asserting exit 0, plus the override cursor released.

---

## B3 — BLOCKING (the weakest of the three; security flagged it as such itself). A writer-less
## FIFO sidecar freezes the GUI thread permanently

`src/lr_reduction/settings_resolver.py:588-606`, called at `launcher/apps/settings_editor.py:707`.

`load_resolution` runs **synchronously in the `load_settings` slot, on the GUI thread** — I
confirmed the call site. `provenance_path(path).exists()` returns **True** for a FIFO, so the
gate passes, and opening a writer-less FIFO blocks forever. `@guarded` is irrelevant:
`_DiscoveryWorker`'s own docstring says it — *"a stalled one blocks in D-state — it does not
raise, so `except OSError` and the slot guard are both irrelevant to it."* Recovery is SIGKILL,
which takes every other tab's unsaved state — **the exact consequence the C3 commit message
invokes to justify leak-over-abort.**

The plan deferred this as *"real and none is a science or crash path."* **That basis is false**,
which is why it is blocking rather than advisory: the acceptance was granted on a wrong premise.

**Fix (~6 lines, and it also closes the `MAX_SETTINGS_BYTES` FIFO bypass):** route the sidecar
through `_read_json`, and add the regular-file gate — `O_NONBLOCK` on the `os.open` so a
writer-less FIFO returns ENXIO immediately, then `stat.S_ISREG(os.fstat(fd).st_mode)`, then
clear `O_NONBLOCK`.

*Out of scope but name it in the PR:* the stalled-mount exposure is wider than the sidecar —
`SettingsDocument.from_file` (Load) and `atomic_write_json`'s `mkstemp` (Save) also touch `/SNS`
synchronously on the GUI thread. T3 put a worker on the Resolve door and left Load and Save.
That is the one-guard-two-doors pattern at thread level and belongs in a follow-up, not a v5.

---

## WHAT IS GENUINELY STRONG — do not regress these, and do not re-verify them

Stated because it is true and because it should shape the human's decision. v4 is much the
strongest version of this slug.

- **C1 verified by live hostile injection at all 5 sites** (three domains, independently): real
  ELOOP symlink → `RuntimeError`, NUL → `ValueError`, non-path → `TypeError`, 5000-char →
  `OSError`, `chmod 000` → `PermissionError`, `../../../../etc` and `/etc` → refused by
  `is_relative_to`. **Every case returned normally with a recorded reason; nothing raised.**
- **C2 pinned in both directions** — test-reviewer mutated the *return contract*, not the
  guard's presence: `_FAILED → None` reds 1; returning `None` on error reds 5. All 5 sites check
  `is _FAILED`; the sentinel never reaches `ctx`. The v3 confident falsehood is gone.
- **C7's clause is now load-bearing** (mutation-verified twice): deleting the excluded-group
  clause reds. As written in v3 it was unreachable.
- **All 8 HIGH divisors individually pinned**; whitelist derivation sound (20 fields, no
  geometry / path / per-angle / runtime-owned / free-text `str`), enforced at all three doors
  including the reader.
- **C4's *sidecar* door is genuinely closed** — `ui_overrides` traces only to `_session_edits`.
  B1 is the *document* door.
- **The active-row trap is avoided empirically** (row 2 selected, edit row 0 → writes row 0);
  no `.destroy()` anywhere; 5× dialog open → 0 retained widgets.
- **C8 guarded and transactional** — document byte-identical on refusal, report truthful.
- **No secrets; no `exec`/`eval`/`pickle`/`yaml.load`/`shell=True`/`verify=False`.**
  `atomic_write_json` refuses symlink writes, fsyncs, renames atomically, cleans up on
  `BaseException`. `_read_json`'s `O_NOFOLLOW` genuinely refuses a symlink and fstats the **fd**.

---

## ADVISORY — recorded, not blocking (fix opportunistically or in a follow-up)

1. **`@guarded` is a 9-site shared rule with 1 site pinned** — 8 survive removal; only
   `add_angle` reds. Advisory only because no reachable abort was demonstrated (`coerce` is
   forgiving; the other slots carry inner catches). Same shape as B2 — see the root cause.
2. **`fs.refusals` is a write-side gate only.** `save_resolution` (`settings_resolver.py:559`)
   has none; demonstrated `dqbin=0.0` and `dSampDet=-1.0` landing on disk. And `json_to_config`
   (`new_reduction_from_file.py:441-451`) is a bare `setattr` loop — so the stated motive
   ("`dqbin=0` could be written into the file autoreduction reads") is only half closed:
   the GUI can't *produce* one, autoreduction will still *read* one.
3. **The `b` → `b*` downgrade is at the call site, not in the reader.** `load_resolution` — the
   Qt-free API where `PREVIOUS_RUN_LAYER` is defined — hands back authoritative-looking `"b"`.
   The campaign's own extraction lesson: move it into `load_resolution` or a named
   `read_as_previous_run()`.
4. **Sidecar `source_layer` is unvalidated and rendered as rich text.** `QLabel.textFormat()` is
   `AutoText` (measured); a forged `source_layer` renders as a plausible formatted origin. The
   downgrade is exact-match `== "b"`, so `"b "`, `"B"`, `"b​"` pass through. No authority
   escalation — impact is provenance spoofing on the badge, which is the slug's headline promise.
   Fix: validate against `LAYER_LABELS` + `setTextFormat(PlainText)`.
5. **A malformed sidecar raises mid-render and the panel then makes the C8 false claim** —
   document *was* replaced, badges half-rendered, `refresh_report()` never ran, report says
   "The settings in this tab are unchanged." Same false-unchanged class C8 was rejected for.
6. **`load_resolution` unhardened on every axis but blocking** — follows symlinks (its twin
   refuses), no size cap, no `isinstance(dict)`; `AttributeError`/`KeyError` are outside
   `_guarded_step`'s tuple, so routing it through discovery raises past the guard.
7. **Stale sidecar: a new value badged with an old origin.** `as_record()` carries no digest; the
   plan's own remediation was not implemented. (Orphan-sidecar is benign — exact-name matching.)
8. **`.dat` — and a correction to my own v3/v4 briefs:** I twice relayed "a save suffix the
   editor's own Load refuses." **Load accepts `.dat`** (`:691`). The real defect is worse: Save
   accepts `.dat` (`:739`) and writes **JSON**, Load dispatches on suffix into the `# Config:`
   branch and fails — a successful Save yields an unrecoverable file.
9. **`test_the_wait_cursor_is_released_once` passes through the wrong path** —
   `test_global_settings.py:890` closes over an undefined `ipts` (should be `_ipts`), so the
   worker returns a `NameError` and the success path is never exercised. The restore *is* pinned
   (via the exception branch), but the "exactly once" guard survives removal: Qt's
   `restoreOverrideCursor` is a no-op on an empty stack.
10. **`_record_structural_change` labels this-session columns "set for a *previous* run"** — the
    label contradicts its own detail. Mechanism right, words wrong; needs a sibling layer tag.
11. **Layer (e) has zero production callers** (`dataset_probe` set only in tests), so
    "geometry never outranks (c)/**(e)**" is only testable at (c) in production. Also still
    caller-less: `user_chosen`, `SettingsDocument.normalize`.
12. **`global_settings.py:158` still carries pre-decision precedence** (the 8th declaration);
    `settings_resolver.py:65` misstates who reads `LAYER_ORDER` (only `_layer_sources` does —
    `HUMAN_LAYERS` is a second hand-maintained list beside the declared single source).
13. **`provenance_path` collides on stem** — `foo.json` and `foo.dat` both map to
    `foo.provenance.json`; `foo.0.5deg` → `foo.0.provenance.json`.
14. **Ledger record coarseness:** the HIGH row's "16 failed" can only be produced by dropping
    all 8 bounds at once (all 8 *are* individually pinned — record, not coverage). Rows 4/5
    share one behaviour via a decorative parametrize whose `failing_stem` only feeds an
    always-true assert. `TypeError` is the one member of `_guarded_step`'s tuple with no red.
    `nx`/`ny` at `-1.0` red on the int type check, not the bound.
15. **`dqbin=1e-12` passes** — `field_spec.py:288` names the "49.7 TB arange" hazard in a
    comment; only `0` and non-finite are guarded. No magnitude floor.
16. **`minidom` billion-laughs on untrusted `template*.xml`** — 8 M chars in 2.44 s, measured;
    one more entity level is 800 MB. **XXE refuted** (pyexpat does not resolve external general
    entities here). Pre-existing, outside this diff, and T3 correctly declines to parse layer (d).
17. **`dead_time_tof_step` has `minimum=0.0` not `exclusive_minimum`** and is whitelisted; it is
    a denominator, but unreachable from the config path (`config_to_template` has zero callers).
    Add the bound for consistency; the folded HIGH is substantively complete.

**Not findings against this slug — two things I checked because they were raised:**
`pixi.lock` is **byte-identical** to `exp` and **no commit on this branch touches it**
(criterion met). `f98ec6c` (`IncidentTheta` `4.0 → None`) is an **ancestor of `exp` on both
remotes** — inherited base, not scope creep into this MR. Its consumers do have ~7–11 % coverage,
which is a real gap *in the base*; I am routing that separately rather than charging it here.

---

## ESCALATION — the human's decision, with my recommendation

The retry budget is spent. Three options, as before:

**(a) A second bounded extension to N=5 — my recommendation.** The two real blockers are small
and their fixes are agreed across domains: B1 is ~4 lines plus one line added to an existing
test; B2 is a `_forget_worker` slot, moving teardown to the window, and the subprocess matrix the
criterion already required; B3 is ~6 lines that also close a size-cap bypass. Everything else on
this page is advisory. v4 closed C1, C2, C5, C6, C7, C8 and both HIGH folds *semantically* — this
is not a slug that is failing to converge, it is one whose last two defects are in a layer the
ledger's frame did not cover.

**(b) Accept-and-merge with the findings recorded — I argue against.** B1 silently puts a stored
number above a measured one, in the geometry fields, with a badge that says a person set it. That
is the precise failure the 2026-09-12 exclusion was decided to prevent, and it reaches reduced
data through the file autoreduction reads. I would not ship it.

**(c) Amend in place** — outside my contract; I never write feature code.

Contract §4 routes a blocking finding to the rejection loop with no Integrator discretion, and
the budget escape covers infrastructure failures only. **I rejected per the contract, not on a
judgment of proportionality** — the proportionality call is (a) vs (b), and it is the human's.
