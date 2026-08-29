# Learnings — `pixi-lock-format-guard` (campaign `exp-settings-roi`)

## 1. A comment that states an unfinished measurement as finished outlives the commit that admits it

**Rule.** Write into code only what you measured. If a claim is unverified, say
so in the same sentence that makes the claim — and never let a script comment
be more confident than the commit body it ships with.

**Why.** The v1 wrapper's header asserted "Measured on pixi 0.67.2: `pixi lock
--check` UPDATED the lock and exited 0" for the *drift* case. The same commit's
body said plainly that three probe attempts had failed and that the rc under
genuine drift was unverified. Both statements shipped together, and they
contradicted each other. The comment is the one a future reader trusts: it sits
next to the code, it is short, and nothing prompts anyone to go read a commit
message from months earlier to check it.

That asymmetry is the point. A commit body is read when someone is already
suspicious; a comment is read while forming the belief. So an over-confident
comment does more damage than an over-confident commit message, and it is the
place to be most careful.

The honest form, which is what the file now carries: the restamp at exit 0 IS
measured (0.67.2, twice, plus repeated live observation); the rc under drift is
UNVERIFIED, with the three walls named — an unsolvable probe package, a package
already present as a transitive dependency, and a `failed to fetch conda-pypi
mapping` error that fails every re-solve in this environment. And the
uncertainty is then used, not hidden: it is the argument for classifying drift
from file content rather than from the exit code.

**How to apply.** When a probe fails to complete, the finding is "unverified",
not "assume the expected answer". Write the negative result and the reason into
the artifact. Related: `plans/harness-hardening-learning.md` §2 — the same
discipline applied to tests rather than comments.

## 2. A guard that instructs the user must not instruct them into the failure

**Rule.** Read a tool's error messages as part of its behaviour. A remediation
string is executable advice; if following it causes the harm the tool exists to
prevent, the tool is broken however correct its detection is.

**Why.** The v1 drift message ended with "run `pixi lock` and commit the
result". On pixi >= 0.68 — precisely the population the guard exists to catch —
`pixi lock` *is* the v7 rewrite that makes the lock unreadable at the facility.
The check would have detected the problem and then talked the user into
committing it. The v2 message names the pin (`pixi self-update --version
0.67.2`) and says "regenerate under a pixi <= 0.67.x".

Two related failures in the same script, both from assuming the happy
environment: it assumed it ran at the repository root (from a subdirectory it
created a 0-byte `pixi.lock` in the cwd while pixi's parent-directory manifest
search rewrote the real one), and it had no `trap`, so an interrupt during the
network solve left a converted lock with the snapshot orphaned in a temp file.
Both are now injection-tested.

**How to apply.** For every failure path a guard can take, ask what the user
does next, and whether the message sends them somewhere safe. Then inject the
condition and read the output as they would.

## 3. Narrow an ignore-list to what you measured, not to what sounds principled

**Rule.** When a check must tolerate a known-benign mutation, define the
tolerated set from an observed diff. A tighter set derived from principle can
be wrong in the direction that blocks everything.

**Why.** The review directed narrowing the ignored region to the
`version`/`sha256` lines inside the self-package stanza, so that other in-stanza
changes (`requires_dist`, `editable`) would become visible. That is the right
instinct — but applied literally it makes the guard fail on *every* ordinary
push, because `pixi lock --check` removes `editable: true` every time it runs.
Whole-stanza diff on 0.67.2, committed lock vs post-check:

```
- version: 2.10.0.dev20260610180700+gf5b8e45   ->  + …dev20260819073821+g3c1808b
- sha256:  c96e2ca…                            ->  + 6781a23…
- editable: true                                   (removed; env stays editable)
```

Three lines, always the same three. The ignore set is exactly those, and the
comment carries this diff so the next person can see why each entry is there.
Everything else in the stanza stays visible, which was the substance of the
request. Verified on three mutants: benign triple passes; a `requires_python`
change blocks; a removed package blocks.

**How to apply.** Diff the before/after of the operation you are tolerating,
paste it into the code, and let the ignore-list be that list. A tolerance
justified by reasoning alone is a guess about a tool's behaviour; a tolerance
justified by a pasted diff is a record of it.

## 4. Arm a restore trap only after the thing it restores from exists

*Added after the v2 rejection; sections 1-3 are from the v2 cycle.*

**Rule.** A cleanup trap that copies a saved file back is only safe once that
file holds the saved content. Arming it over an empty `mktemp` creates a window
in which any exit destroys the very artifact the script exists to protect.

**Why.** The v2 wrapper did:

```bash
snap=$(mktemp) || exit 1
trap 'cp "$snap" pixi.lock …' EXIT INT TERM   # armed over an EMPTY file
cp pixi.lock "$snap" || exit 1                 # …populated only here
```

If that second `cp` fails — a full disk, a quota, an `ulimit -f` — the EXIT
trap copies zero bytes onto the tracked `pixi.lock`. That is strictly worse
than the fail-open it replaced, and the reason is worth keeping: a *truncated*
lock whose first line still reads `version: 6` passes every tripwire this guard
ships. A guard's own failure mode has to be measured against its own detectors,
not against intuition about what "a broken file" looks like.

Correct order, with the failure path owning its own cleanup:

```bash
snap=$(mktemp) || exit 1
cp pixi.lock "$snap" || { rm -f "$snap"; exit 1; }
restore() { cp "$snap" pixi.lock 2>/dev/null; rm -f "$snap"; }
trap restore EXIT
```

**How to apply.** For any save/restore trap, ask what the handler would do if
fired *right now*, at each line between `mktemp` and the end of the save. If the
answer at any point is "write something wrong", the trap is armed too early.

## 5. A bash INT/TERM handler returns to the script unless it exits

**Rule.** `trap handler INT` does not end the script. After the handler runs,
execution resumes at the interrupted point — so a handler that tears down state
must also exit, and must disarm the EXIT trap so the teardown does not run
twice.

**Why.** v2 shared one handler across `EXIT INT TERM`. On SIGINT it restored the
lock, deleted the snapshot, and then returned into the classifier, which
compared against a file that no longer existed: a fabricated drift accusation
followed by an 8k-line diff. The user-visible result of pressing Ctrl-C was the
guard loudly claiming their lock was broken — precisely the experience that
teaches people to reach for `--no-verify`, which would disable the format
tripwire too.

```bash
trap restore EXIT
trap 'restore; trap - EXIT; exit 130' INT
trap 'restore; trap - EXIT; exit 143' TERM
```

Measured after the fix: SIGINT mid-solve gives exit 130, zero output, a
byte-identical lock and no temp litter.

The pattern to notice: v2's comment claimed "one restore path, and it survives
an interrupt" — a statement about control flow that the control flow did not
support, sitting one line below that same commit's fix for a stated-vs-measured
defect. The class is not limited to measurements; a claim about *what the code
does* deserves the same "did I check?" as a claim about what a tool does.

**How to apply.** Where a script installs signal handlers, exercise them: send
the signal mid-run and read the exit code and the output, not just the final
file state. Note that `setsid` forks, so a probe must signal the script's real
PID — an early version of this very probe signalled a wrapper that had already
exited, and reported a false pass.
