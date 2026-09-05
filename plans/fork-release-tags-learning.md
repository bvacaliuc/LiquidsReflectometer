# Learnings — `fork-release-tags` (campaign `exp-settings-roi`)

## 1. Git refspec wildcards are one `*`, and `|| true` hides the rejection

**Rule.** A refspec pattern supports a single `*` matching one whole component.
Shell-style character classes are rejected outright — and if the fetch is
guarded with `|| true` for resilience, that rejection is silent.

**Why.** The plan prescribed

```
git fetch <url> 'refs/tags/v[0-9]*:refs/tags/v[0-9]*' || true
```

which fails immediately with `fatal: invalid refspec`. The `|| true` — there so
an upstream blip cannot fail the CI step — swallows it, so the step would have
appeared to run forever while fetching nothing, and the fork would have stayed
broken in exactly the way the slug exists to fix. The symptom would have
surfaced far downstream as "versioningit fell back to default-tag", pointing at
versioningit rather than at a typo in a refspec.

The fix is `'refs/tags/v*:refs/tags/v*'`, letting `describe --match='v[0-9]*'`
do the numeric filtering it was already doing.

**How to apply.** Run any new fetch/push refspec once before shipping it —
`fatal: invalid refspec` is instant and unambiguous. Where a command is
deliberately made non-fatal, that is precisely where a smoke test is required,
because the guard converts every failure into silence. Related:
`plans/pixi-lock-format-guard-learning.md` §2, where a guard's own remediation
text was the defect.

## 2. Worktrees share the tag store, so "delete tags in a worktree" is not isolation

**Rule.** `git worktree` isolates the working tree and `HEAD`, not refs. Tags
live in the common git directory, so creating or deleting one inside a linked
worktree changes it for every worktree and for the clone itself.

**Why.** The plan's verification step said to simulate a tagless fork by
deleting the `v*` tags "in a throwaway worktree, never the seat's clone" — the
parenthetical showing the author knew the operation was destructive and believed
the worktree contained it. It does not:

```
$ git -C /tmp/wt-tagcheck rev-parse --git-path refs/tags
/media/ssd2/Projects/Claude/2/.git/modules/lr_reduction/refs/tags
```

That is the *common* directory. Running the instruction would have deleted all
67 provisioned `v*` tags from this seat's clone — the exact outcome it was
written to prevent, and one that would have quietly broken local versioningit
for every later slug on this seat.

The isolation that does work is a clone with its own ref namespace:
`git clone --shared --no-tags <src> <dst>` — cheap, since `--shared` reuses the
object store, and `--no-tags` reproduces the tagless-fork condition directly
rather than by deletion.

**How to apply.** Before trusting a sandbox, ask what it actually isolates:
worktrees isolate the checkout, clones isolate refs, containers isolate the
filesystem. When an instruction pairs a destructive operation with a
reassurance, check the mechanism named in the reassurance — `rev-parse
--git-path` answers this one in a second. And prefer constructing the condition
(`--no-tags`) over destroying state to reach it.
