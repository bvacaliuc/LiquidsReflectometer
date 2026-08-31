# Learnings — `test-tmp-isolation` (campaign `exp-settings-roi`)

## 1. When a race will not reproduce, characterize the mechanism instead of rolling dice

**Rule.** A concurrency defect that resists live reproduction is still fully
diagnosable: place the foreign state by hand and run the real comparator. That
converts "we think this is what happens" into a table, and it costs seconds
rather than repeated multi-minute attempts with an uncertain outcome.

**Why.** This slug's plan asked for a live RED — two tests writing one
`/tmp` path simultaneously until one fails. Two concurrent writers passed; four
concurrent writers, the campaign's actual steady state, also passed. Each
attempt costs about 70 seconds per process, and the window is evidently narrow:
six occurrences across two weeks of gates is not something you summon on demand.

Copying one parameterization's output into the file another test reads, and
calling the suite's own `check_results`, produced this in seconds:

| file placed in the shared path | read by | result |
|---|---|---|
| `sf_..._dt_par_42_200.cfg` | expects 46_200 / 46_300 | passes |
| `sf_..._dt_par_46_200.cfg` | expects 42_200 / 46_300 | passes |
| `sf_..._dt_par_46_300.cfg` | expects 42_200 / 46_200 | passes |
| `sf_197912_Si_auto.cfg` (no deadtime) | expects any deadtime reference | **FAILS** |
| any deadtime reference | expects `sf_197912_Si_auto.cfg` | **FAILS** |
| truncated file (a torn write) | anything | **IndexError** |

That table corrected the plan's causal story. The three deadtime
parameterizations are *mutually indistinguishable* to the comparator, so a
collision among the four tests sharing `_test_dt` cannot by itself produce a
failure — the observed fingerprint needs deadtime and non-deadtime content to
meet, or a torn write. Two clones on different branches writing one path can
produce either; one session cannot.

**How to apply.** Reach for injection when reproduction is expensive or
probabilistic, and say plainly which one you did. Per
`setup/patterns/failure-injection-testing.md`, shims validate the model and live
injection validates the world — here the world had already validated it six
times at gates, so the model was the missing half. And note what makes the fix
defensible without a reproduction: *no shared path exists afterwards*, so every
row in that table becomes unreachable. Verifying an artifact's absence
(`/tmp/sf_197912_Si_test*.cfg`: none produced) is stronger evidence than one
lucky red run.

## 2. "Different hunks" is a claim about text, and text is checkable

**Rule.** When a plan says two in-flight branches touch the same file but merge
cleanly, verify it with `git merge-tree` before repeating it. The answer is one
read-only command and it is either 0 or it is not.

**Why.** This plan stated the overlap with `scaling-factor-path-anchor-v2` was
"different hunks — either order merges cleanly". Both slugs add a fixture to the
same five `def test_*` signature lines, from the same base:

```
base       def test_compute_sf(nexus_dir):
sfpa-v2    def test_compute_sf(nexus_dir, template_dir):
this slug  def test_compute_sf(nexus_dir, tmp_path):
```

`git merge-tree` between the two branches reports **5 conflict hunks**, one per
signature. The resolution is mechanical and identical every time — keep both
fixtures, `(nexus_dir, template_dir, tmp_path)` — which is exactly the sort of
thing worth handing the human *before* they hit it at the merge rather than
after.

**How to apply.** `git merge-tree $(git merge-base A B) A B | grep -c '<<<<<<<'`.
Cheap, read-only, and it upgrades a merge prediction from courtesy to fact. Do
it in a probe, not by checking out branches under a dirty tree — a stash-and-
checkout dance to answer the same question left a conflicted working file here
and had to be unwound.
