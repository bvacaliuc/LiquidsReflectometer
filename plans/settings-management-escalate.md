# ESCALATION — `settings-management` (T3): extended cap reached (4 of N=4), Analyst decision required (2nd)

> **SUPERSEDED 2026-09-15 — the human authorized a second bounded extension to
> N=5 with the resolver invariant** (recommendation (a) accepted, item 4 adopted:
> geometry never resolves above (e) from a user-authority layer; a deliberate
> per-run geometry override is deferred to a later badged feature). v5 runs from
> the five-item scope in the plan's `### v5` entry;
> `triage/settings-management-v5` dispatched, the
> `review/settings-management-escalate` tag deleted. This file is kept as the
> record of the cap-reached moment.

> This file supersedes the v3/N=3 cap-reached escalation (which recommended, and
> received, the N=4 extension); the prior version is preserved in
> `git log -- plans/settings-management-escalate.md`. It now records the **v4 /
> N=4-exhausted** escalation.

**Terminal state:** attempt 4 of the **extended N=4** rejected → second sanctioned
cap-reached escalation. Rejection todo @ `ce591fc` (feature tip; gate green at
`2be5d04`: **194 launcher + 350 reduction, EXIT=0, `pixi.lock` byte-identical,
ruff clean**). **Code, not infrastructure** — budget genuinely exhausted. The cap
disposition is the **human's**.

## The one thing that changed: the mutation ledger WORKED

v4 adopted the committed, mechanical mutation ledger (amendment 16 hardened). It
is **the first attempt whose author-side record was auditable**, and it audited
**clean**: the Integrator reconciled all four families against `grep -c`
(5/5/6/2) and test-reviewer independently re-ran **all 18 enumerated mutations
with zero survivors**. **The four enumerated families are closed — do not
re-litigate them.** This is the process fix landing exactly as intended.

## Why it still rejected: the defect class moved UP one level

v1–v3 failed on *a shared helper with one test, counted by behaviour not
call-site*. v4 fixed that for the families it enumerated. The two surviving
blockers are the **same shape one level up** — a safety property carried by a line
**no test and no enumeration frame touched**:

- **B1 (C4 — third door, SCIENCE):** `settings_editor.py:121` `_session_edits` is a
  **set of names**; `_pre_resolve_overrides` binds the value **late**
  (`{n: document.get(n)}`); `set_document` (`:493`) replaces the document and never
  clears the set. So an edit authorizes a *name*, and whatever value later occupies
  it inherits (b) authority. Typing `dSampDet` once then File→Open another
  experiment → the **file's** `dSampDet=99999` resolves at layer (b) "set for this
  run", outranking the experiment file (1234) **and** the measurement (1000), badge
  lying `[b]`. **No sidecar; reproduced 4× (design/ui/security/Integrator).** The
  architectural root: `settings_resolver.py:310` whitelist-gates **only (a)**; (b)
  is ungated and sits above (a)/(e), so geometry always has a path to the top. This
  is precisely what the 2026-09-12 exclusion exists to prevent, and it reaches the
  file autoreduction reads. **v4 closed the sidecar→authority door; the
  document→authority door stayed open.**
- **B2 (C3 — load-bearing half unpinned):** the ledger bundled "parent the worker
  **/** drop `closeEvent`" under one red. Split: dropping `closeEvent` → 2 failed ✓;
  **adding `self` as the worker's parent at `:617` (one word) → 194 passed,
  SURVIVOR** — and that survivor is v3's crash verbatim (exit 134). Worse, the tab's
  `closeEvent` **never runs** on the real quit path (Qt delivers `QCloseEvent` only
  to the closed widget; the tab is a child of the `QTabWidget`), so the no-abort
  outcome is delivered **solely** by the untested unparenting at `:617`.
- **B3** (~6 lines, also closes a size-cap bypass) + **A1** (`@guarded` 8/9 sites
  unpinned — advisory, no reachable abort) round out the page.

**The frame lesson (Integrator's, worth keeping):** the mechanical ledger counts
the sites of the helpers you *enumerate*; the next step is to **enumerate the
frame** — before writing the ledger, list every shared rule in the diff
(decorators, sentinels, bundled "X / Y" descriptions), not just the helpers you
changed. *A ledger row whose description contains "/" is two mutations.*

## Attempt synopsis

| Attempt | Feature tip | Outcome |
|---|---|---|
| v1 | `6365df4` | 7 clusters — resolver **unwired** (precondition≠payoff) |
| v2 | `8abfdce` | 11 clusters — guards prove one site of many; recurrence classes open |
| v3 | `ecc1e3b` | 8 clusters — per-site root **recurred**; C3/C4 born from v3's own fixes → **N=3 cap → human extended to N=4** |
| v4 | `ce591fc` | 2 real blockers — **ledger works, 6 clusters + 2 HIGH folds closed**; defect class **moved up a level** (B1/B2) → **N=4 exhausted** |

## Recommendation to the human

**(a) A second bounded extension to N=5 — my recommendation, with one addition
beyond the Integrator's scope.** This is a *converging* slug, not a failing one:
v4 closed six clusters and made the ledger auditable, and the two blockers are
small and cross-domain-agreed (B1 ≈ 4 lines + 1 test line; B2 = a `_forget_worker`
slot + teardown moved to the window + the subprocess matrix the criterion already
required; B3 ≈ 6 lines). **But C4 has now reopened three times through three
different doors** (v3, then v4's sidecar, now v4's document), because the doors are
closed one at a time. The robust v5 scope is therefore **the Integrator's B1/B2/B3
fixes PLUS a resolver-level invariant that closes the door *class*:**

- **B1 exact fix (converged across 3 domains):** bind the value at edit time —
  `_session_edits` becomes a **dict** `{name: value}`; `_pre_resolve_overrides`
  returns `{n: v for n, v in _session_edits.items() if n in fs.BY_NAME}`;
  `_forget_per_angle_edits` pops `PER_ANGLE_NAMES`. **Security's caveat (heed it):**
  do **not** just clear the set in `set_document` — that also fires after a
  completed Resolve and would silently drop a scientist's typed override on a second
  Resolve, trading one bug for another. Guard: add a prior
  `_on_scalar_edited("dSampDet", …)` to the existing pin test; it must still assert
  `1500.0` at layer `"e"` (verified red today).
- **B2:** a `_forget_worker` slot, teardown moved to `LauncherWindow` (not the tab,
  whose `closeEvent` never fires), and the subprocess close-with-resolve-in-flight
  matrix asserting EXIT=0; pin the unparenting at `:617` explicitly.
- **THE ROBUSTNESS ADDITION (mine) — close the C4 door class, not the third door:**
  add a **resolver invariant** that a `GLOBAL_EXCLUDED_GROUPS` (geometry) field can
  never resolve above layer (e) from a user-authority layer. Implement by gating
  **both (a) and (b)** at `settings_resolver.py:310` (not (a) alone), and add a
  standing guard test asserting geometry resolves to (e)/measurement regardless of
  what any door places in (a) or (b). With this, a hypothetical *fourth* door reds
  the invariant instead of shipping — converting C4 from whack-a-mole into a bounded,
  detection-complete guarantee.
  - **Embedded scientific decision for you (like C4(ii)):** the invariant makes
    geometry **never** user-overridable — a scientist could not deliberately type a
    geometry value to beat a bad PV for one run. If a deliberate single-run geometry
    override is a capability you want to keep, we implement **B1 only** (accidental
    promotion prevented; a *typed* geometry value still wins), and accept that C4's
    door-closing stays per-door. My lean, on your robust/detection-complete
    standard, is the invariant — but this is a measurement-vs-operator-judgment call
    that is yours.

**(b) Accept-and-merge — I argue against, with the Integrator.** B1 silently puts a
stored/file number above a measured one in the geometry fields, badge claiming a
person set it — the exact failure the 2026-09-12 exclusion prevents, reaching the
file autoreduction reads. Not shippable on the project's first principle.

**(c) Amend in place** — the Integrator cannot (no feature code); the Analyst writes
plans, not code — so this means **you** apply the B1/B2 fixes directly.

Procedure if you extend: reply with the N=5 extension and your call on the geometry
invariant (both-(a)-and-(b) vs B1-only); I author v5 from this scope, create
`triage/settings-management-v5`, and the cycle resumes.
