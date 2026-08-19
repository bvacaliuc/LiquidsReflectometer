# Learnings — `port-overplot-axes-refresh` (S2, campaign `exp-settings-roi`)

## 1. Concurrent campaign sessions on one machine corrupt each other's test gate through hard-coded `/tmp` paths

**Rule.** Before treating a data-reduction test failure as a code defect,
check whether another session was running the same suite. A suite that
writes fixed absolute paths is not safe to run twice concurrently on one
host, and the campaign's own design (Developer in clone 2, Integrator in
clone 3, same machine) does exactly that.

**Why.** `tests/test_scaling_factors_workflow.py` sets `output_dir = "/tmp"`
in five tests, and four of them write the **same** file,
`/tmp/sf_197912_Si_test_dt.cfg`, with different parameters — deadtime on/off,
`deadtime_tof_step` 200 vs default, paralyzable vs not (lines 84, 103, 131,
159). Within one pytest session the tests run sequentially and each rewrites
the file before reading it, so the collision is invisible. Across two
sessions the writes interleave, and a test compares another run's output
against its own reference.

Observed on this slug: a full-suite run reported

```
FAILED test_scaling_factors_workflow.py::test_compute_sf_with_deadtime_tof_200
  assert np.float64(7.057973681032683) < 0.02
```

on a branch whose only source change was `launcher/apps/overplot.py`, which no
reduction test imports. `ps` showed the Integrator session running
`pixi run test-reduction` concurrently. Re-run of that test alone: 1 passed.
Re-run of the whole suite with no competing process: 107 passed.

Note the shape of the number. A relative difference of ~7 against a 0.02
tolerance is not a marginal numerical drift — it is a *different computation's*
answer. Per `setup/patterns/numerical-diagnostics.md`, a discrepancy that
large and that clean points at a mundane cause (wrong file) rather than a
subtle one (algorithm change), and the mundane cause is what it was.

**How to apply.** (a) Campaign roles sharing a host should serialize
`test-reduction`; the Integrator already does this by waiting on the other
run's PID before re-running its gate. (b) Never read a gate failure as a
verdict on a diff that cannot reach the failing code — check the blast radius
of the diff first, then the machine's process list. (c) The durable fix is to
give these tests `tmp_path` instead of `/tmp` and per-test filenames; that is
a target-repo defect outside this slug's scope, parked for the campaign to
route as a `todo-*` (charter §9 amendment 8). Until then the hazard is real
for every slug's gate, in both directions.

## 2. A `pixi run` from a subdirectory rewrites `pixi.lock`'s local-package stanza after any commit

**Rule.** On a slug that adds no dependencies, treat *any* `pixi.lock`
modification as churn to discard, and re-check `git status` immediately
before staging — not only after the edits you intended.

**Why.** versioningit derives the local package version from `git describe`,
and the lock records it. After committing, a later `pixi run` re-solved and
rewrote the stanza:

```
-  version: 2.10.0.dev20260610180700+gf5b8e45
-  sha256: c96e2caeff01ea7f7a3784c263ecddb20b1501bc82c5002baf5cd521ef471085
+  version: 2.10.0.dev20260819033130+g8bf1e75
+  sha256: 6781a23362219426acd8a0ac4c0a58e52ee282cc93061a23ebeda8c706d41daa
   requires_python: '>=3.11'
-  editable: true
```

Two distinct hazards: the version/sha lines are machine-and-moment specific
and go stale the moment anyone commits again, and the dropped `editable: true`
is a real semantic change to how the local package installs — neither belongs
in a port slug's diff. This is the same lock surface as S0's v6→v7 finding
(`plans/launcher-test-harness-learning.md`) but a different trigger: that one
was a format upgrade from `pixi lock --check`, this one is a re-solve from an
ordinary `pixi run` issued from `tests/`.

**How to apply.** `git checkout -- pixi.lock` before staging, and stage
explicit paths rather than `git add -A`. Note the plan for this slug already
carried the caveat, which is why it was caught — a plan that names the trap
is worth more than a reviewer who has to notice it.

## 3. "Seed PR" does not mean "verified against facility data"

*Added after the v1 rejection (Integrator todo.md `1c0fc43`); the sections
above are from the v1 cycle.*

**Rule.** When a slug ports logic that parses a *data format*, validate the
ported logic against the repository's real files before calling it green — not
against the seed PR, not against a fixture written by the same PR. A plan that
says "copy verbatim" transfers the seed's defects too.

**Why.** PR #9's `classify_file` scanned a fixed 10-line window for the
reflectivity header marker. Both reduction writers put that marker after a
metadata preamble carrying one line per stitched angle, so in this repo's own
tracked corpus it sits at lines 13, 18, 19, 19 and 20:

```
tests/data/reference_short_nobck.txt        line 13
tests/data/reference_rq_201282.txt          line 18
tests/data/reference_rq.txt, _avg           line 19
tests/data/reference_rq_avg_overlap.txt     line 20
launcher/tests/data/refl_fixture.txt        line 2   <- the only hit
```

Every real reflectivity file classified `unknown`; only the seven-line
synthetic fixture the PR itself shipped classified `reflectivity`. Direct beam
was asymmetric — its marker lands on line 8, inside the window — which is what
made the second defect bite: `_resolve_modes` dropped `unknown` before testing
homogeneity, so one recognized direct-beam file dragged a whole selection of
real R(Q) curves onto `λ [Å]` / `I` axes with no warning.

The user-visible result is the part worth remembering: **the slug made its own
primary case worse than before it existed.** Before, real reflectivity plotted
under `Q`/`R` with `R*Q⁴` working; after, `x`/`y` with `R*Q⁴` greyed out and
silently reset — or, in the mixed case, confidently wrong axis labels on real
measurements. A slug whose stated purpose is "stop the axes lying" shipped
axes that lie differently.

**How to apply.** Three checks, none expensive: (a) if the ported code reads a
file format, find the writer in `src/` and read what it actually emits
(`output.py:236`, `save_reduced_data.py:54-56` here — a *second* writer with a
different marker that no version of the port handled); (b) parametrize the
guard test over the real tracked corpus, listed explicitly — the `REFL_*.txt`
siblings are gitignored test-run byproducts and a glob over them collects zero
cases on a fresh clone or in CI; (c) treat a synthetic fixture as a
convenience for edge cases, never as evidence that the classifier works.

## 4. A green suite can be evidence of nothing — check that the tests can fail

**Rule.** Before claiming a slug green, ask which test would fail if the
feature were reverted. If the answer is "none", the suite is decoration.

**Why.** v1's 15 tests passed while all four blocking defects were live. The
reviewer enumerated partial reverts that keep the whole suite green: revert the
popout labels to `'x'`/`'y'`; swap check-state restore from name-keyed to
index-keyed; drop the filter-honoring rebuild; hardcode `_set_rq4_enabled` to
`False`; delete the entire explicit-override block; delete the `[kind]` legend
suffix; disconnect `refresh_btn.clicked` altogether — no test clicks the
button. And `test_refresh_no_folder` asserted the value it had just set, so it
passed with the guard deleted.

The v1 tests were green because they were written against the same mental model
as the code, using the same synthetic fixture. That is the failure mode: tests
derived from the implementation confirm the implementation.

**How to apply.** For each behaviour a slug adds, write the test so that
deleting the behaviour makes it red, and say so in the commit body. The v2
suite is built this way — twelve tests that fail first, each naming its
finding, plus four written explicitly as guards against reverts the reviewer
named. Where a test lands green at RED, state that plainly instead of letting
a total ("15 passed") imply coverage it does not have.
