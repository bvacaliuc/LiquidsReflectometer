# Cross-repo hand-off — `no-publish-seam` (F1)

**Terminal state: `needs-human-push`.** Charter §6: ref-based orchestration
runs only on `lr_reduction` via `agentic`; `REF_L/shared` lives on
`code.ornl.gov`, which is physically read-only to agents. The change below is
committed locally and waits for a human push and review. Detection is
complete; auto-resolution stops at the facility boundary.

## What to push

| Field | Value |
|---|---|
| Repo | `REF_L/shared` (`git@code.ornl.gov:ref_l/shared.git`) |
| Working copy | `/media/ssd2/Projects/Claude/2/REF_L/shared` (clone 2, the Developer's session tree) |
| Branch | `wip/enable-exp-parallel-reduction` |
| Base | `c4fed3d` — the branch tip, and in sync with `origin/wip/enable-exp-parallel-reduction` at the time of writing |
| New commit | **`a8e2eb9`** "accept both --no-publish spellings; compose the shadow gate with the caller's flag" |
| Shape of push | plain fast-forward (`c4fed3d..a8e2eb9`), one commit, no force |
| Files | `autoreduce/reduce_REF_L.py` only — 1 file, 3 insertions, 3 deletions |

No `feature/no-publish-seam` branch and no `qa/no-publish-seam` tag exist on
`agentic` by design (plan §"Cross-repo execution note"): there is no
`lr_reduction` change in this slug, so the Integrator gate does not run. The
human's review on code.ornl.gov is the gate.

## The change

Three edits, exactly as planned:

1. `publish` argv scan (line 44) now accepts **both** `--no-publish` and
   `--no_publish` as suppression requests. Before this, a caller using the
   kebab-case spelling — the one this shim's own documentation tells operators
   to use for manual re-reduction — silently got `publish=True` and the run
   published to monitor.sns.gov. Active facility-visible trap.
2. The shadow-forwarding gate (line 95) is now
   `if not (publish and new_publish):`, composing the caller's flag with the
   operator knob. Behavior-identical today (`new_publish = False` ⇒ the flag
   is always appended); correct at knob-flip, where the old form would have
   published the shadow result against an explicit suppression request.
3. The line-43 comment names both spellings.

The forwarded flag stays snake_case deliberately — every deployed `exp` build
accepts it, including those predating `a9af9df`.

## Verification transcripts

The shim cannot be imported off a facility node (module-level
`lr_autoreduce` import), so verification is the campaign's committed AST
checker, `plans/scripts/no-publish-seam-check.py` on this branch, which
extracts the `publish` assignment and the `new_publish` gate and evaluates
each against a fixed truth table.

RED — against `c4fed3d`, before the edits:

```
$ python3 plans/scripts/no-publish-seam-check.py \
      /media/ssd2/Projects/Claude/2/REF_L/shared/autoreduce/reduce_REF_L.py
FAIL: publish scan: argv=['--no-publish'] -> True, want False
$ echo $?
1
```

GREEN — against `a8e2eb9`, after the edits:

```
$ python3 plans/scripts/no-publish-seam-check.py \
      /media/ssd2/Projects/Claude/2/REF_L/shared/autoreduce/reduce_REF_L.py
OK: publish scan suppresses on both spellings
OK: shadow gate composes caller publish with new_publish knob
GREEN: no-publish seam checks pass
$ echo $?
0

$ python3 -m py_compile autoreduce/reduce_REF_L.py
$ echo $?
0

$ git diff --stat HEAD~1
 autoreduce/reduce_REF_L.py | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)
```

## What local verification cannot prove

Actual publish suppression on a facility shadow run. No local end-to-end path
exists. After the push, validate on a test IPTS — a `batch_reduce.py`-style
scratch run, or the next autoreduction cycle — that a re-reduction invoked
with `--no-publish` produces no monitor.sns.gov publication.

## Out of scope (deliberately untouched)

The `PIXI_PREFIX=/SNS/users/6ov/...` personal path (pixi-deploy seam), the
`new_publish` value (operator/deploy decision), `CONDA_ENV`, the positional
argv handling and its pre-existing `IndexError` on fewer than two arguments.
