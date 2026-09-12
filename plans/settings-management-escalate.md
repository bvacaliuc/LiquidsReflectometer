# ESCALATION — `settings-management` (T3): retry cap reached (3 of N=3), Analyst decision required

**Terminal state:** attempt 3 of N=3 (charter §1) rejected → sanctioned
cap-reached escalation. Rejection todo @ `ecc1e3b` (feature tip; gate green at
`ab3e13a`: **182 launcher + 325 reduction, EXIT=0**). **Code, not
infrastructure** — the budget is genuinely exhausted (infra failures don't
consume it; this is production/test code). The cap disposition is the **human's**
(as with `check-results-fields` and `settings-editor`), not the Analyst's or
Integrator's.

## What the slug does (why it matters)

T3 gives reduction-settings resolution a **layer taxonomy with a single
resolver** ((a) user-global → (b) this-run → (c) IPTS json → (d) IPTS xml → (e)
dataset-guess → (f) default, resolved order **b→c→d→a→e→f** per the 2026-09-12
human C4(ii) decision), with per-field provenance and a whitelisted global-prefs
editor. It replaces the organic settings muddle (B1) that had no defined
precedence and no provenance.

## Attempt synopsis

| Attempt | Feature tip | Did | Blocked on |
|---|---|---|---|
| **v1** | `6365df4` | resolver + taxonomy + global editor; provenance round-trip | 7 clusters; through-line **precondition≠payoff** — 42 green tests, **zero production callers** (the resolver was unwired) |
| **v2** | `8abfdce` | wired the resolver (production-path test on a real seam); autoreduce refactor proven identical (1536-case differential); B1/B2/B5/B6/B7; layer-(d) demotion; C4(i)+(ii); deep-copy; geometry exclusion | 11 clusters; through-line **guards prove one site of a multi-site behaviour** + **recurrence classes not fully closed** |
| **v3** | `ecc1e3b` | fixed **5/5** ui-aspects v2 blockers + **4/6** test-reviewer; Save preserves runtime-owned input; unconditional per-element coercion; discovery off the GUI thread (0→30 QTimer ticks); `render_value` nested; A3/A6; `_read_json` hardened (`O_NOFOLLOW`, cap, not-a-dict); sidecar read + layer (b) wired | **8 clusters** — the per-site root **recurred**, and **two of v3's own fixes composed into new holes** (C3, C4) |

Every prior-attempt finding is confirmed fixed and not re-litigated. The
confirmed-fixed list at `ecc1e3b:todo.md` is long and includes the
science-critical BL-1/BL-3/BL-4/BL-5 fixes, the `sympify` allow-list, and the
whitelist type gate — all re-verified intact.

## The v3 blocking set (8 clusters; full detail at `ecc1e3b:todo.md`)

**One root cause, nine instances (test-reviewer's through-line):** *a shared
helper got one test, and the test count matched the **behaviour** count rather
than the **call-site** count.* `_guarded_step` 5 sites/3 mutations/**2 survivors**
(`:447`,`:452`); `_record_edit`/`_record_angle_edit` 5/3/**2** (`:358`,`:388`);
`_may_be_a_preference` 6 clauses/5/**1** (excluded-group); the two guard notes
0 mutations. **This recurred despite the v3 plan sharpening amendment 16 to
"per site"** — the Developer applied it partially. The Integrator's mechanical
fix: **`grep -c` the call sites, require one mutation per hit, derive the count
from the code, not from the sentence describing it.**

| # | Cluster | Severity |
|---|---|---|
| **C1** | `_guarded_step` catches `except OSError`, but `Path.resolve()` raises **`RuntimeError`** on ELOOP (symlink loop on the sshfs/FUSE `/SNS` mount) + `ValueError`/`TypeError` on NUL/None — 2 of 5 sites unpinned; every non-GUI caller gets the raise | correctness (FUSE-real) |
| **C2** | resolve status **reports success for a failed read and contradicts itself** — persistent false "no reduce_settings*.json" after a `chmod 000`; scientist reduces from defaults with a layer-(a) value (c) was meant to outrank; test asserts truthiness not content | provenance-integrity |
| **C3** | the new discovery worker **aborts the launcher (exit 134)** on every teardown path while a resolve is in flight — QThread destroyed while running; **v3 traded v2's freeze for an abort in the exact stalled-`/SNS` scenario the worker was added for** | crash regression |
| **C4** | **two of v3's own fixes compose to promote file/sidecar content above the measurement** — geometry (`dSampDet`,`IncidentTheta`,…, the `apply_config_overrides` set) reaches layer (b) "set for this run" with **no typing**, outranking both the experiment file AND the measurement; badge lies; `shared/autoreduce` is group-writable. **Defeats the C4(ii) exclusion you decided** | **science-correctness (silent wrong reduced data)** |
| **C5** | Save writes a document the panel has already declared invalid (no `validate()` gate on the persist path) | data-integrity |
| **C6** | three re-record sites unpinned, two of them the most-used editing paths | test-vacuity |
| **C7** | the whitelist's excluded-group clause is unpinnable as written | test-vacuity |
| **C8** | `add_angle` lacks the guard its sibling documents 33 lines away | correctness |

## Why accept-and-merge (option 2) is OFF the table

**C4 alone forecloses it.** A scientist types a geometry value once, Saves,
reopens the file for a **different** experiment weeks later, Resolves — and that
stale value silently outranks the new experiment's settings file **and** the new
measurement, with the badge reading "set for this run" (which they never did).
Identical typed IPTS, identical visible UI, **different reduced data, no
warning.** That is precisely the failure the C4(ii) geometry exclusion exists to
prevent, reached through a side door (the sidecar read, and a row-count click).
Shipping it violates the project's first principle — reduced data must never be
silently corrupted. **C3** (a hard abort on the stalled-mount path) independently
blocks a merge. Everything else could ship with a note; these two cannot.

## What I would do in a v4 (fully specified — no discovery left)

The Integrator localized every site with a fix; a v4 is bounded, not open-ended.
~3 root fixes + mechanical per-site test discipline:

- **C1:** `_guarded_step` catches `(OSError, RuntimeError, ValueError)` (or
  `except Exception` recording the reason); mutate **all 5** sites.
- **C2:** distinguishable sentinel (`(ok, value)` or module-level `_FAILED`);
  append "no …" **only** when the scan succeeded; assert the errno **text**.
- **C3 (robust form, not `wait()`):** leave the worker **unparented**, hold it in
  `self._discovery_worker`, `finished → deleteLater`; on `closeEvent` disconnect
  and drop the reference (leak one thread on a D-state read rather than abort);
  guard `restoreOverrideCursor`. Prove in a subprocess so the abort is an
  assertion, not a suite kill.
- **C4 (one root, both doors):** never seed `ui_overrides` from provenance read
  off disk (in-session edits are already tracked by `_record_edit`); map a
  sidecar `"b"` to a **non-authoritative** marker (`"b*"`, "set for a previous
  run"); separate a **structural** edit (row-count) from a **value** edit so a
  click can't mint `Resolved(...,"b")` for 13 untyped arrays; clear per-angle
  overrides when `ipts_edit` changes.
- **C5–C8:** gate Save on `validate()`; pin the 3 re-record sites and the
  excluded-group clause; give `add_angle` the sibling guard.
- **ROOT (mechanical, not principled):** the v4 plan requires the commit body to
  show **one mutation line per `grep -c` call-site hit** for every shared
  helper/rule — the count derived from the code. This is amendment 16 hardened
  from "mutate every site" (a principle the Developer under-applied twice) to a
  mechanical grep-count check.

## Recommendation to the human

**Authorize a bounded v4 under an explicit cap extension (N=4 for this slug)** —
the Integrator's lean, and mine, primarily on **C4** (a silent
science-correctness regression that accept-and-merge would ship) and **C3** (a
crash on the stalled-mount path). The remaining work is fully specified and the
clusters share ~3 roots, so a v4 is proportionate — the same shape that justified
the `check-results-fields` and `settings-editor` N=4 extensions. If you prefer
not to extend, the only safe alternative is **amend-in-place yourself** (the
Integrator cannot touch feature code, the Analyst writes plans not code) — **not**
accept-and-merge, which C4/C3 forbid.

Procedure if you extend (as before): reply with the cap extension + authoritative
scope (this file's "What I would do in a v4" is drop-in), and I author v4, create
`triage/settings-management-v4`, and the cycle resumes on the normal
Developer→Integrator path.

## Durable lesson (route post-campaign)

Two attempts (v2, v3) blocked on the **same** shape — a shared helper tested by
behaviour-count, not call-site-count — and the second recurrence happened
**after** the plan explicitly required per-site mutation. The principled form of
amendment 16 was insufficient; the **mechanical** form (`grep -c` sites → one
mutation line per hit in the commit body) is what actually closes it. Candidate
for `setup/patterns/scientific-regression-testing.md` and a further amendment-16
sharpening. Second lesson: **wiring a read-side (C8 v2→v3) can convert a
"recorded origin" into "authority" (C4)** — when you add a reader for provenance,
prove the read cannot promote a layer; origin is not authority.
