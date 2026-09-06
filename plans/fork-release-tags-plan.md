# Plan: fork-release-tags

**Campaign:** `exp-settings-roi` · base `exp` @ `c14f54b` (#18 merged) ·
mid-effort addition 2026-09-05, human-approved (from
`todo-fork-release-tags.md`; **option (c) scope** — the doc's own Analyst
refinement) · staged **before T2** so T2's base computes an honest version
· DAG-independent
**Retry attempt:** 1

Review domains: design-reviewer (advisory — CI-infra, no product code).

## Symptom

The fork carries **no `v[0-9]*` tags**, so on fork CI
`git describe --match='v[0-9]*'` fails, versioningit falls to
`default-tag 0.0.1`, and `test_computed_version_does_not_regress` (requires
computed release `>= (2,10,0)`) fails. Commit `18578d3` (merged via #16,
now on `exp` @ `.github/workflows/test_and_deploy.yml:56-60`, step *"Ensure
release tags exist"*) papers over it by synthesizing `git tag v2.10.0` when
no tag is reachable — a **hard-coded, frozen** value that also makes HEAD
`describe` as a *clean* release `2.10.0` (distance 0), not a dev build.

## Why option (c), not the doc summary's (b) (verified 2026-09-05)

The `todo-*` first recommended (b) `git push origin 'refs/tags/v*'`. That
is **not** clean: verified against `agentic/exp`, the fork workflow
triggers on **`tags: ["v*"]`** (`test_and_deploy.yml:8`) with Actions
active, so pushing the 67 upstream `v*` tags would fire 67 CI+publish runs
on the old commits they point at (the 2026-08-18 parked hazard). Option
(c) pushes no tags — it makes fork CI **fetch** the real upstream tags each
run, so `describe` finds `v2.9.0rc1-…` → versioningit computes the true
`2.10.0.dev<ts>+g<rev>` (monotonic, honest), the regression test passes
from real tags, and the synthetic hard-coded tag is deleted. Local dev
seats are unaffected (uvdl3 clones already carry the 67 `v*` tags via
provisioning — verified in clone 1; the synthetic tag is *purely* fork-CI
scaffolding).

## Files to change (on `feature/fork-release-tags` from `agentic/exp`)

`.github/workflows/test_and_deploy.yml` — the *"Ensure release tags exist"*
step (~lines 56-60). Replace the synthetic-tag body:

```yaml
      - name: Ensure release tags exist
        run: |
          # The fork carries no v-tags; fetch the real ones from upstream so
          # versioningit computes an honest monotonic dev version. No tag is
          # pushed to the fork (its workflow triggers on tags: [v*]), and this
          # is a no-op when a v-tag is already reachable (e.g. upstream).
          if ! git describe --tags --match='v[0-9]*' HEAD 2>/dev/null; then
            git fetch --quiet https://github.com/neutrons/LiquidsReflectometer.git \
              'refs/tags/v[0-9]*:refs/tags/v[0-9]*' || true
          fi
```

Keep the `if !…` guard so the step is a strict no-op wherever a `v*` tag is
already reachable (upstream, or a fork that later gains tags). Do **not**
touch the `tags: ["v*"]` trigger, the `fetch-tags: true` checkout options,
or versioningit's `default-tag` (the true last-resort floor stays).

**Strip note (load-bearing):** this hunk is `.github/**` and must **never**
reach an upstream PR — upstream has real tags, so the step is dead code
there and, worse, a `describe`-failure path (shallow checkout, pre-tag
race) would fabricate a version. The net-diff extraction for upstream PRs
already excludes `.github/` (§3 / `todo-fork-release-tags.md`); this slug
does not change that, it only makes the fork-side step honest.

## Verification — CI is the real gate; the local gate is necessary-not-sufficient

The defect lives in fork **GitHub Actions**, which the Integrator's local
`pixi run test-reduction` cannot exercise (it uses the seat's local
upstream tags). So:

- **Local (Developer + Integrator gate)**: `pixi run test-reduction` green
  as always — confirms the edit breaks nothing. Additionally, simulate the
  fork-CI condition **in a throwaway worktree, never the seat's clone**
  (deleting `v*` tags is destructive): `git worktree add /tmp/wt-forktags
  HEAD`, in it `git tag -l 'v*' | xargs -r git tag -d`, run the new step's
  body, then `git describe --tags --match='v[0-9]*' HEAD` → expect
  `v2.9.0rc1-…` and `python -m versioningit` → `2.10.0.dev…` (not clean
  `2.10.0`); `git worktree remove`. Record the transcript in the commit
  body.
- **The authoritative proof is the draft PR's own Actions run**: it must go
  green with `test_computed_version_does_not_regress` passing, and the
  computed version in the build log must be a **`…dev…`** string, not
  `2.10.0`. The Integrator notes in the PR that CI-green is the gate here;
  the human confirms the version string on the PR before merge.

## Failure-mode matrix

| Case | Detection | Handling |
|---|---|---|
| Upstream reachability blip in fork CI (the (c) cost) | step's `\|\| true` + the `if !` guard | non-fatal; if no tag results, versioningit falls to `default-tag` and the regression test fails LOUDLY in the `tests` job — a visible CI red. ~~not a bad publish~~ **CORRECTED 2026-09-05 (Integrator gate + Analyst verify): this half is FALSE.** `publish`/`deploy-exp` are `needs: [build]`, NOT `[tests]` (`test_and_deploy.yml`), so a red `tests` job does not gate the artifact — see `todo-fork-publish-not-gated-on-tests.md`. The `\|\| true` is still defensible (option (c) is a strict improvement over the synthetic-tag status quo, and this slug edits only the `tests`-job step), but its safety must not rest on "blocks publish". Verified latent: the fork's `publish` currently fails on every `exp` run (no token), so nothing ships regardless — the publish-gating fix is a separate human deploy decision, not this slug's scope. |
| Someone re-adds `git tag v2.10.0` later | version string is clean `2.10.0` in CI log | PR-body note; the honest-dev-string check catches it |
| Hunk leaks into an upstream PR | `.github/` file in the PR diff | net-diff excludes `.github/`; strip note + reviewer check |
| Local seat clone loses its v-tags during the throwaway sim | sim runs in a `git worktree`, not the clone | explicit worktree instruction above |
| pixi.lock re-stamp | first line ≠ `version: 6` | amendment 14: restore |

## Acceptance criteria

- `pixi run test-reduction` green locally (edit breaks nothing); the
  throwaway-worktree simulation transcript (real describe → dev version)
  in the commit body.
- The draft PR's GitHub Actions run green, with the build-log version a
  `2.10.0.dev…` string (not clean `2.10.0`) — the real acceptance, stated
  for the human on the PR.
- Diff touches exactly `.github/workflows/test_and_deploy.yml` (the one
  step); `18578d3`'s `git tag v2.10.0` is gone; no `pixi.lock` change.
- Draft PR body: fork-CI-only (never upstream), option-(c) rationale, the
  67-tag-push hazard this avoids, and that the actual tag-push-to-fork
  (option b) remains a **separate human deploy decision** behind scoping
  the `v*` trigger.
