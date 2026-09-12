# Integrator: `settings-management` (T3) v3 — REJECTED. RETRY BUDGET EXHAUSTED (3 of N=3).

**Gate is GREEN** at `ab3e13a`: 182 launcher + 325 reduction, `EXIT=0`. Every
finding is invisible to it.

**All three blocking-capable domains blocked** — design 2, ui-aspects 4,
test-reviewer 3 — plus 1 should-block from security. **Read the escalation at the
bottom before dispatching a v4.**

**v3 is the strongest version of this slug and most of it verifies.** The
confirmed-fixed list is long. But it has **one root cause repeated five times**,
and two of its own fixes compose into a new hole.

---

## THE ROOT CAUSE — stated once, because nine findings are instances of it

*test-reviewer's through-line:* **the code got a shared helper, the helper got one
test, and the test count matched the *behaviour* count rather than the *call-site*
count.**

| shared helper / rule | call sites | mutations run | live survivors |
|---|---|---|---|
| `_guarded_step` | **5** | 3 | **2** (`:447`, `:452`) |
| `_record_edit` / `_record_angle_edit` | **5** | 3 | **2** (`:358`, `:388`) |
| `_may_be_a_preference` clauses | **6** | 5 | **1** (excluded-group) |
| `_pre_resolve_overrides` halves | 2 | 1 | 1 (the fallback) |
| the two guard notes | 2 | 0 | 2 |

Extraction was the right instinct — and it moved the defect from "duplicated
logic" to "one implementation, partially tested". The mechanical check that finds
all of these: **`grep -c` the call sites, require one mutation per hit, and derive
the count from the code rather than from the sentence describing it.**

---

## C1 (BLOCKING) — `_guarded_step` catches the wrong exception class, and two of its five sites are unpinned
*design B1-adjacent · test B1 · security S3 — three domains.*

`settings_resolver.py:435` now promises "**Never raises.**" `_guarded_step`
(`:416-421`) catches `except OSError`. `Path.resolve()` converts ELOOP into a
**`RuntimeError`**, which is not an `OSError`. Proven live with real symlinks, no
monkeypatching:

```
facility root is a looping symlink (:447)  -> RuntimeError: Symlink loop from '.../loop'
IPTS dir inside the root loops   (:452)  -> RuntimeError: Symlink loop from '.../autoreduce'
NUL byte in ipts or root                 -> ValueError: embedded null byte
root=None / 12 / b''                     -> TypeError
```

And **neither `.resolve()` site is pinned**: unwrapping each guard entirely leaves
the suite green. The other three sites are red when unwrapped, which is why the
count looked complete.

`/SNS/REF_L` is an sshfs/FUSE mount; a self-referential link in an IPTS `shared/`
tree is case 2. The launcher survives only incidentally, because
`_DiscoveryWorker.run` catches `BaseException` — every non-GUI caller gets the raise.

**Fix:** `except (OSError, RuntimeError, ValueError)` (or `except Exception` with
the type in the note), and pin `:447`/`:452` with a real symlink loop in the tree.

**Integrator note:** I verified "five sites are guarded" and reported it as
reassurance. That was a count, not a semantics check — two of the five guard against
an exception their call cannot raise. My error, and the same shape three times this
cycle (see the corrections section).

---

## C2 (BLOCKING) — the resolve status reports success for a failed read, and contradicts itself
*design B2 · security S4 · test should-fix 1.*

`_guarded_step` returns `None` for **both** "raised" and "found nothing", so the
caller appends a flat denial after the error. Real `chmod 000` tree, file present:

```
STATUS SHOWN TO THE SCIENTIST:
Resolved IPTS-9.
Discovery: settings scan failed: [Errno 13] Permission denied: '.../reduce_settings_up.json';
           no reduce_settings*.json;                    <-- FALSE, and it is the last word
           template scan failed: ...; no template*.xml

qmax resolved to 0.42 from layer a — the experiment file said 0.9 and was unreadable
```

Two falsehoods in one label, and `set_status` now makes it **persistent**, so the
false clause is what a scientist acts on: concludes the experiment has no settings
file and reduces from defaults with a layer-(a) value that (c) is supposed to
outrank. The author *did* separate the sentinel at the `is_dir` site (`:466-472`)
and not at the two scan sites.

Note the chmod-000 test asserts `assert ctx.discovery_status` — truthiness, not
content — and passing `[]` instead of `notes` at `:477`/`:496` is green, so the
note content is unpinned at both new sites.

**Fix:** a distinguishable sentinel (`(ok, value)` or a module-level `_FAILED`),
append "no …" only when the scan succeeded, and assert the errno text.

---

## C3 (BLOCKING) — the new worker aborts the launcher on teardown
*design B1 · ui NB-1 · security S9 — three domains, five teardown paths measured.*

`settings_editor.py:68-92` (`_DiscoveryWorker`), `:587` parented to the tab, and
**no** `closeEvent` / `wait()` / `quit()` / `requestInterruption` / `deleteLater`
anywhere in the file.

```
resolve in flight: True; user closes the launcher
QThread: Destroyed while thread is still running
EXITCODE=134
```

Measured on every path: `tab.close()`, `close()+deleteLater()`+drain,
`closeAllWindows()+quit()`, interpreter exit, real `LauncherWindow.close()` — all
134. **v3 traded the freeze for an abort, in exactly the scenario the worker was
added for**: a stalled `/SNS`, the scientist gives up and quits. It contradicts the
file's own contract at `:49-54`.

The suite is blind because every worker test calls `wait()` first — and the
`isolated_qapp` teardown is itself the abort trigger, so a test that starts a
resolve without draining will abort pytest.

**Fix — and take the robust form, not the simple one.** Do **not** just add
`wait()`: a `wait()` on a D-state read blocks exactly as long as the freeze did.
Leave the worker **unparented**, hold it in `self._discovery_worker`, connect
`finished → deleteLater`, and on `closeEvent` disconnect `finished_with` and drop
the reference. The stalled case then leaks one thread instead of aborting, which is
the correct trade. Also: `restoreOverrideCursor` is unreachable if the worker never
returns, so the application-wide wait cursor persists for the process's life.
Guard it in a subprocess so the abort is an assertion rather than a suite kill.

---

## C4 (BLOCKING) — two of v3's own fixes compose to promote file content above the measurement
*security B1 · ui NB-2 — the same root, two doors.*

`load_settings` now seeds `self.provenance` from the sidecar (`:645-647`);
`_pre_resolve_overrides` converts *recorded origin* into *authority* (`:548-551`);
and `resolve()` gates only layer **(a)** on `GLOBAL_WHITELIST`. Layer (b) has no
gate — correctly, while (b) means "typed into this UI for this run". After this
commit it can also mean "claimed by a file".

**Door 1 — the sidecar.** File→Open then Resolve, with *no typing at all*:

```
dSampDet      = 99999.0  layer b  "set for this run"   (file said 1.83, data said 1.83)
IncidentTheta = 88.0     layer b  "set for this run"   (file said 0.6,  data said 0.6)
```

Those are exactly the `GLOBAL_EXCLUDED_GROUPS` geometry fields that have **no layer
(a) at all** because — in this commit's own words — *"a preference must never
override a measurement."* The sidecar routes around the exclusion, and all seven
reachable keys are the `apply_config_overrides` set that rewrites the instrument
settings feeding the resolution calculation. `shared/autoreduce` is group-writable,
so a colleague's dropped sidecar does it too. No adversary needed either: type
`dSampDet` once, Save, reopen weeks later for a different experiment, Resolve.

**Door 2 — a row-count click.** `_record_angle_edit` attributes **all 13**
per-angle fields to (b), and `_pre_resolve_overrides` promotes every (b) field.
One "Add angle" between two Resolves:

```
AFTER RESOLVING B:  DBname = ['dbA1','dbA2',None] [b]   (B's file says ['dbB1','dbB2'])
                    RBnum  = [1001, 1002, None]   [b]   (B's file says [2001, 2002])
status: 'Resolved IPTS-B.'    badges: "set for this run" — which the user never did
```

Identical typed IPTS, identical visible UI, different reduced data, and the file
looks internally consistent. This is the active-row fingerprint at experiment scale.

**Fix (one root, both doors):** never seed `ui_overrides` from provenance read off
disk — in-session edits are already tracked by `_record_edit`/`_record_angle_edit`.
Map a sidecar `"b"` to a non-authoritative marker (`"b*"`, label "set for a previous
run") so the badge stays truthful and the value stays non-authoritative. And
separate a **structural** edit from a **value** edit: a row-count change must not
mint `Resolved(..., "b")` for 13 arrays nobody typed. Clear per-angle overrides when
`ipts_edit` changes.

---

## C5 (BLOCKING) — Save writes a document the panel has already declared invalid
*ui NB-3.*

`:677` calls `save_resolution` with no `validate()` check anywhere on the path. One
keystroke reproduces it:

```
document dqbin: 0.0
report: - Q bin width (dqbin): 0.0 must be greater than 0.0
file written? True    dqbin in file: 0.0    sidecar written? True
```

This commit **added** `exclusive_minimum` on `dqbin`/`tof_bin`/`DetSigma` reasoning
that `dqbin=0` overflows downstream — then left the only path that persists it
ungated. Meanwhile `GlobalSettingsDialog.accept()` **does** gate on `check()` and
refuse. Two doors into one rule, one guarded — the granularity failure again.

**Fix:** one shared validate-or-refuse helper used by both doors, not a second
per-site copy. A settings file in `shared/autoreduce` is what autoreduction runs.

---

## C6 (BLOCKING) — three re-record sites unpinned, two of them the most-used editing paths
*test B3 · ui NB-2-adjacent.*

| site | mutation | result |
|---|---|---|
| `:358` `_set_scalar` (combo + checkbox) | `_record_edit` → `refresh_badges` | **green** |
| `:366` `_on_scalar_edited` | " | red ×2 |
| `:388` `_on_cell_changed` (per-angle cell) | " | **green** |
| `:399` `add_angle` | " | red |
| `:414` `remove_selected_angle` | " | red |

Runtime probe with both survivors mutated: a scientist types into a per-angle cell
or flips a checkbox, the document changes, and the header still attributes the
column to `reduce_settings.json` — with the **full 182-test launcher suite green**.
v2 had four of five surviving; v3 closed two.

---

## C7 (BLOCKING) — the whitelist's excluded-group clause is unpinnable as written
*test B2.*

The 6-name hand-list is dead (that half is fixed). But `_may_be_a_preference` has
**six** clauses, and the one carrying the human scientific decision survives
deletion:

```
delete `field.group in GLOBAL_EXCLUDED_GROUPS` (:149)  -> green
GLOBAL_EXCLUDED_GROUPS = (fs.GEOMETRY,) -> ()          -> green

GEOMETRY in GLOBAL_GROUPS? False
=> the excluded-group clause can only fire for a group in BOTH tuples: set()
```

So the clause is unreachable, and its "isolating" test
(`tests/test_settings_resolver.py:815`) passes through the `not in GLOBAL_GROUPS`
clause instead. The block carries 12 lines of comment ending *"an exclusion that
only exists as an absent group is an exclusion nobody can see"* — and it can be
emptied with the suite green, making it exactly that.

**Fix:** monkeypatch `GLOBAL_GROUPS` to include `fs.GEOMETRY` and assert a geometry
field is still refused.

---

## C8 (BLOCKING) — `add_angle` lacks the guard its sibling documents 33 lines away
*ui NB-4. Pre-existing in `settings_document.py` (byte-identical across v2/v3), but
two clicks from a file shape this code's own comment cites as real.*

```
add_angle:203        list(current) + [values.get(name)]          <- no guard
set_angle_field:236  if not isinstance(current, (list, tuple))   <- guarded, with a
                     comment explaining why a len() check was insufficient
```

Load a file with a scalar per-angle value, click Add angle:

```
TypeError: 'float' object is not iterable       <- mutation aborts MID-LOOP
after add: n_angles 3, rows 2                   <- the third angle is invisible
per-angle lengths: {DBname:3, RBnum:3, BkgROI:1, tof_min:'scalar 5000.0', ThetaShift:0}
panel claims: "The settings in this tab are unchanged."   <- false
file written? True   json_to_config accepted it
```

Three compounding failures: a **partial** mutation leaving a ragged document (what
`add_angle`'s docstring exists to prevent), a false "unchanged" claim, and
`refresh_report()` never re-running so `validate()` never reports the lengths
before Save.

**Fix:** guard `:203` as `:236` is guarded, **and** make `add_angle` transactional —
mutate a copy and commit, so a raise cannot leave a half-grown document.
`report_problem` must not claim "unchanged" unless it knows that.

---

## Should-fix

- **[HIGH] `qmin` is the divisor in `log_qvector` and still admits `0`.** The commit
  applied `exclusive_minimum` to `dqbin`/`tof_bin`/`DetSigma` and missed the one
  field that is literally the denominator. `qmin` is whitelisted, so `0` persists
  into layer (a) and outranks the guess and the default for every future experiment:
  `log_qvector(0.0, 0.5, 0.005)` → `ZeroDivisionError`; `qmax=0` → `OverflowError`.
  Add `exclusive_minimum=0.0` to both.
- **[HIGH] the six geometry divisors accept `0` and negative.** `mmpix`, `dSampDet`,
  `dMod`, `dS1Samp`, `nx`, `ny` have neither bound. `dSampDet=0` →
  `ZeroDivisionError` at `nr_reduction_calc.py:534`; negative → silently mirrored
  geometry; `mmpix=0` scales the whole beam-on-detector calculation to zero
  **silently**. Reachable by typing, by an experiment file, and — via C4 — by a
  sidecar above the measurement. The non-finite half is fixed; the zero/negative
  half is not.
- **`load_resolution` is the unhardened twin of `_read_json`, now on the production
  path.** `_read_json` got `O_NOFOLLOW`, a 4 MB cap and a dict check;
  `load_resolution` (called on every File→Open) got none: reads through a symlink,
  accepts 6 MB, and raises `AttributeError`/`TypeError`/`KeyError` on malformed
  records where its docstring promises degradation. Route both through `_read_json`
  and validate each record.
- **`MAX_SETTINGS_BYTES` is bypassable via a non-regular file.** `st_size` is 0 for a
  FIFO, so the cap is skipped and `json.load` reads unbounded — and `os.open` on a
  writer-less FIFO **blocks forever** on the discovery worker, leaving the
  application-wide wait cursor set for the process's life. Require
  `stat.S_ISREG`, and read `MAX+1` bytes rather than trusting `st_size`.
- **Sidecar-controlled strings render as rich text in the badge and tooltip.**
  `Qt.mightBeRichText('[<img src=x>]')` is True; a sidecar can also forge
  `source_layer="c"` with a plausible `source_detail` for a value that came from
  nowhere — a forged origin in the one widget whose product is truthful provenance.
  Validate `source_layer` against `LAYER_LABELS` and set `Qt.PlainText`.
- **The settings/sidecar pair is still not atomic**, and the reorder added an
  **orphan sidecar** case: a failed first save leaves a sidecar that
  `provenance_path(path).exists()` will later attach to any file written to that name
  by another route. Given C4, an orphan sidecar is an authority grant. Write both
  temps, fsync both, rename both — and record the settings file's digest in the
  sidecar so a mismatch drops the provenance.
- **`show_in_combo` still accumulates strays** — four Loads → three stray entries
  permanently **selectable** beside the real ones, including after loading a valid
  file. The extraction spread it to both dialogs.
- **`_DiscoveryWorker` objects accumulate** one per Resolve press (6 presses → 6
  live children). Folds into C3's fix.
- **`.dat` is admitted as a save suffix** and produces a file the editor's own Load
  refuses. The comment above the line reasons about exactly this and then permits it.
- **Stale status label after Load** — `set_status` is called only from the resolve
  paths, so after Resolve → Load the label still describes the previous experiment.
- **`render_value`'s nested branch is lossy and has no production caller.**
  `[[120,130], None] → '120, 130; ' → [[120,130]]` — an angle disappears; `[None,[10,20]]`
  **moves** the ROI from angle 2 to angle 1. `None` padding is exactly what
  `_equalise_angles` produces. `check()` returns `''`, so nothing reports it. Fix it
  before the first caller appears, and drop "the *exact* inverse" from the docstring.
- **`user_chosen` still has zero non-test callers** and, unlike layer (d), is not
  demoted — its docstring asserts a consumer that does not exist. `normalize()` is now
  write-only too (zero production callers) with a hazard docstring I traced clean.
  Wire or demote, as (d) was and `Field.render` was.
- Precedence is now declared **eight** times, up from five, and
  `global_settings.py:158` still states the pre-decision order.
- `_pre_resolve_overrides`' `changed_vs_seed` fallback is unpinned; "a resolve that
  found nothing says so" is unpinned; "sidecar FIRST" is unpinned; the
  `failing_stem` parametrization cannot discriminate (`assert victim.name` is a
  tautology); `_experiment_tree`'s `tthd_up` is still a dead parameter; both new
  fixture docstrings claim "an unreadable file" that neither body creates.

---

## Amendment 16: the rule is stated and still not applied

Sharpen it as follows — this is `test-reviewer`'s formulation and it is better than
the one currently recorded:

> **Enumerate the sites from the code before counting mutations, not from the prose
> that describes them.** `grep -c` the helper's call sites and the clause count, and
> require one mutation per hit before the ledger is written.

Run on this commit that produces **5 / 5 / 6 / 2** and finds all three of
test-reviewer's blockers without reading a line of prose. Three of the four ledger
phrases are plural nouns naming a behaviour; two hide a live survivor. A fourth
inverts the vocabulary — `tthd ∈ {+1, 0, -1}` are parametrized *cases*, not sites.

**And the ledger needs to live in the repo.** It is currently the commit message
alone, so "28 mutations" is unauditable by construction — two reviewers independently
concluded the record could not be checked. (That was partly my fault: the plan is on
`agentic/analysis/exp-settings-roi`, and I never told them. Both issues are worth
fixing — my brief, and the ledger's home.)

---

## Confirmed FIXED — do not rework

- **BL-3/Save preserves typed input**: all three `RUNTIME_OWNED_NAMES` survive with
  their values; `RBnum[0]=999999` reaches the file. And the switch is **safe** —
  every runtime-owned field is reassigned before first use in both production entry
  points (traced).
- **BL-5/out-of-set preference survives an untouched open+Save**, and Save now
  refuses with a named reason instead of deleting.
- **BL-1's coercion half**: fresh-process `['0.004','0.005']` → `[0.004, 0.005]`
  **floats**; the reduction no longer does arithmetic on strings.
- **BL-4's core**: **0 → 30 QTimer ticks** during a 2 s stub; `resolve_button.click()`
  returns in 0.000 s; `_discovery_finished` on the GUI thread for all 6 presses;
  cursor push/pop balanced with the restore first in the guarded slot.
- **`render_value` round-trips the flat and nested cases** it is actually called with;
  the `;` separator does **not** reach a per-angle cell, and a pasted whole-column
  form is *reported*, not accepted.
- **A3 and A6 fixed** — the template stem is now red under a `sorted(glob)`
  reinstatement, `tthd == 0` and an UP/DOWN swap are red at both layers, and the
  `tthd=1.0` hardcode is red at three tests.
- **The chmod-000 live case degrades correctly** with the errno recorded, verified
  without monkeypatching.
- **`_read_json` hardened**: `O_NOFOLLOW`, the 4 MB cap, and the not-a-dict check all
  land and are pinned.
- **The seven-key `sympify` allow-list, the production autoreduce selection, and the
  whitelist type gate all re-verified intact.** No new `eval`/`exec`/`pickle`/
  `yaml`/subprocess/network sink; no secrets in 896 lines.
- Active-row trap absent (verified through real widgets, both scalar and `BkgROI`);
  sorting pinned; no `.destroy()`; no double-connects; dialog lifecycle clean over 8
  cycles; layer (b) and the sidecar read are now genuinely wired.

---

## ESCALATION — retry budget exhausted, Analyst decision required

**Attempt 3 of N=3.** Contract §4 routes a blocking review finding to this loop with
no Integrator discretion, and the budget escape covers only *infrastructure*
failures. I rejected per the contract rather than judged proportionality.

What the Analyst should weigh:

- the gate has been green on all three attempts;
- **v3 fixed 5 of 5 of ui-aspects' v2 blockers and 4 of 6 of test-reviewer's**, and
  the production autoreduce refactor was proven identical by a 1536-case differential;
- but **two of v3's own fixes compose into C4**, which promotes file content above a
  measurement — the one thing this module's own documentation says must never happen;
- and **nine findings are one root cause**: a shared helper with one test. The
  mechanical fix (`grep -c` the sites, one mutation per hit) is cheap and would have
  caught them all at authoring time.

Same three options as `check-results-fields` v3: authorize a v4 under an explicit cap
extension; accept-and-merge with the findings recorded; or amend in place, which I
cannot do.

I lean toward **a v4**, for one reason: C4 is not a polish item. A scientist who
types a geometry value once, saves, and reopens the file for a different experiment
weeks later gets that value silently outranking the new experiment's file **and** the
new measurement, with the badge reading "set for this run". Everything else on this
list could ship with a note; that one changes reduced data without telling anyone.
