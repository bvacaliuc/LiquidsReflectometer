# Mutation ledger — `settings-management` (T3) v4

One row per site, **enumerated from the code** and each verified by running the
mutation. A prose count in a commit message is what made v3's record
unauditable: two reviewers independently could not check "28 mutations", because
nothing said which 28 or where. This is checkable against `grep -c` at this tip.

## Site counts, as counted

```
_guarded_step call sites       5   grep -c '_guarded_step(' src/lr_reduction/settings_resolver.py  (6, minus the def)
_record_edit-family sites      5   grep -cE 'self\._record_edit\(|self\._record_structural_change\(' launcher/apps/settings_editor.py
_may_be_a_preference clauses   6   sed -n '/def _may_be_a_preference/,/^GLOBAL_WHITELIST/p' ... | grep -c 'return False'
validate-or-refuse doors       2   grep -c 'fs\.refusals(' launcher/apps/settings_editor.py launcher/apps/global_settings.py
```

18 sites, 18 rows.

## `_guarded_step` — unwrap each site in turn (5)

The two `resolve()` sites are injected with a **real symlink loop**, not a
monkeypatch: the shim used in v3 could only exercise the site already wrapped.

| # | site | mutation | observed |
|---|---|---|---|
| 1 | facility-root resolve | unwrap | **1 failed** `test_a_symlink_loop_in_the_facility_root_degrades` |
| 2 | experiment-path resolve | unwrap | **1 failed** `test_a_symlink_loop_in_the_experiment_path_degrades` |
| 3 | `is_dir` | unwrap | **1 failed** `test_discovery_survives_an_unreachable_mount` |
| 4 | settings scan | unwrap | **2 failed** `test_a_permission_denied_share_degrades_rather_than_raising` |
| 5 | template scan | unwrap | **2 failed** `test_a_permission_denied_share_degrades_rather_than_raising` |

## `_record_edit` family — replace with `refresh_badges` at each site (5)

| # | site | mutation | observed |
|---|---|---|---|
| 1 | `_set_scalar` (checkbox / combo) | drop record | **2 failed** `test_every_scalar_edit_path_reattributes_its_field` |
| 2 | `_on_scalar_edited` (line edit) | drop record | **1 failed** `test_every_scalar_edit_path_reattributes_its_field` |
| 3 | `_on_cell_changed` (per-angle cell) | drop record | **1 failed** `test_a_per_angle_cell_edit_reattributes_its_column` |
| 4 | `add_angle` | drop record | **2 failed** `test_adding_an_angle_reattributes_the_columns` |
| 5 | `remove_selected_angle` | drop record | **1 failed** `test_removing_an_angle_redraws_the_column_attributions` |

## `_may_be_a_preference` — drop each clause in turn (6)

Clause 1 is pinned by monkeypatching `GLOBAL_GROUPS` to include `GEOMETRY`,
which makes the exclusion the only thing standing between a measurement and the
preference layer. As written it was unreachable, so deleting the clause carrying
the human's decision was green.

| # | clause | mutation | observed |
|---|---|---|---|
| 1 | `group in GLOBAL_EXCLUDED_GROUPS` | drop | **1 failed** `test_the_geometry_exclusion_holds_even_if_the_group_is_included` |
| 2 | `group not in GLOBAL_GROUPS` | drop | **1 failed** `test_each_whitelist_clause_rejects_in_isolation[not-in-groups-clause]` |
| 3 | `per_angle` | drop | **1 failed** `test_each_whitelist_clause_rejects_in_isolation[per-angle-clause]` |
| 4 | `runtime_owned` | drop | **1 failed** `test_each_whitelist_clause_rejects_in_isolation[runtime-owned-clause]` |
| 5 | `type == "path"` | drop | **1 failed** `test_each_whitelist_clause_rejects_in_isolation[path-clause]` |
| 6 | free-text `str` | drop | **1 failed** `test_each_whitelist_clause_rejects_in_isolation[free-text-clause]` |

## Validate-or-refuse — bypass each door (2)

| # | door | mutation | observed |
|---|---|---|---|
| 1 | editor Save (`settings_editor`) | bypass gate | **1 failed** `test_the_editor_refuses_to_save_an_invalid_divisor` |
| 2 | preference dialog `accept` (`global_settings`) | bypass gate | **1 failed** `test_the_dialog_refuses_an_invalid_divisor` |

## Cluster mutations outside the four enumerated rules

| cluster | mutation | observed |
|---|---|---|
| C4 door 1 | seed `ui_overrides` from disk provenance | **1 failed** `test_a_sidecar_cannot_promote_geometry_above_the_measurement` |
| C4 door 2 | mint `Resolved(...,"b")` on a row-count change | **1 failed** `test_adding_an_angle_does_not_mint_authority` |
| C3 | parent the worker / drop `closeEvent` | **1 failed** `test_closing_the_tab_with_a_resolve_in_flight_does_not_abort` |
| C8 | remove the `add_angle` guard | **1 failed** `test_add_angle_refuses_a_scalar_per_angle_value_and_changes_nothing` |
| HIGH | drop `exclusive_minimum` from a divisor | **16 failed** `test_a_divisor_rejects_zero_and_negative` |

## Two that did not red on the first pass

Recorded because a ledger that only lists successes is the prose count again.

- **`add_angle` re-record** — anchor drift in the harness, not a live survivor;
  re-aimed at the current text, **2 failed**.
- **clause 2 (`group not in GLOBAL_GROUPS`)** — a real gap. Every synthetic
  field in the isolation test used an *included* group, so dropping the clause
  changed nothing. A counter-example in a non-included group
  (`group=NAMING`, numeric, scalar) now isolates it: **1 failed**.

---

# v5

Frame enumerated before the run, per the Integrator's lesson: every shared rule
in the diff, and **a row whose description contains "/" is two rows** — so the
`O_NONBLOCK`/`S_ISREG` gate is listed as two, and the invariant is listed once
per layer it covers rather than once as a class.

Two mutations do not produce a test failure but a **hang**. That is the defect
itself: a blocking `open()` on a writer-less FIFO never returns, on the worker
thread that exists so the GUI does not block. Recorded as observed, with the
per-invocation `timeout` that caught them.

## THE INVARIANT — geometry never resolves above (e) from a user layer

| # | mutation | observed |
|---|---|---|
| 1 | gate layer (a) only — drop (b) from the class | **8 failed** `...[via-layer-b]` |
| 2 | gate layer (b) only — drop (a) from the class | **8 failed** `test_the_invariant_refuses_layer_a_even_if_the_whitelist_admits_it` |
| 3 | remove the gate entirely | **8 failed, 8 passed** `...never_resolves_above_the_measurement` |

Row 2 needed a new test. The `(a)` arm is **not independently observable** with
the existing guards, because geometry is already refused at layer (a) by
`GLOBAL_WHITELIST` — so dropping the invariant's (a) half changed nothing and
every test stayed green. The isolating guard monkeypatches `GLOBAL_WHITELIST` to
*admit* the field, which leaves the invariant as the only thing standing. Same
unreachable-clause shape as v4's C7.

## B1 — the layer-(b) value is bound at edit time

| # | mutation | observed |
|---|---|---|
| 4 | value not bound at edit time (`= None`) | **1 failed** `test_a_typed_override_survives_a_second_resolve` |
| 5 | `_pre_resolve_overrides` re-reads the document | **1 failed** `test_a_typed_override_is_not_rewritten_by_an_intervening_load` |
| 6 | `_forget_per_angle_edits` no longer pops | **1 failed** `test_per_angle_edits_do_not_follow_a_change_of_experiment` |

Row 5 needed a new test too. A second Resolve alone does **not** expose it: for a
non-geometry field layer (b) wins, so the document still holds what was typed and
re-reading returns the same value. The isolating sequence is
**edit → Load → Resolve**, where `set_document` has swapped the document
underneath and re-reading hands back the loaded file's value as though the
scientist had typed it.

## B2 — worker teardown

| # | mutation | observed |
|---|---|---|
| 7 | worker parented to the tab | **1 failed** `test_the_worker_is_unparented` |
| 8 | `shutdown` drops instead of parking | **1 failed** `...tears_down_cleanly[stalled]` |
| 9 | window `closeEvent` does not forward | **1 failed** `...tears_down_cleanly[stalled]` |
| 10 | `aboutToQuit` not connected | **1 failed** `...tears_down_cleanly[quit-signal]` |
| 11 | a finished parked worker is never reclaimed | **1 failed** `test_a_parked_worker_is_reclaimed_if_it_finishes` |

Row 10 needed the `quit-signal` scenario: `aboutToQuit` is wired in `main()`,
which no test calls, so the connection was unpinned. The wiring is now a
factored `install_shutdown_hooks(app, window)` the test installs itself.

Row 11 was **dead code** when first written — `shutdown` disconnected `finished`
before parking, so nothing could ever take a worker off the list. Parked workers
now reconnect a reclaim slot, which makes the removal both reachable and useful:
a merely-slow worker that completes after teardown is released rather than held
for the life of the process.

Not a row: `_forget_worker`'s clearing of `self._discovery_worker`. Deleting it
changes no observable behaviour, because `resolve_for_experiment` overwrites the
attribute on every run and `shutdown` clears it. Recorded as defensive rather
than claimed as pinned.

## B3 — the read gate, on both paths

| # | mutation | observed |
|---|---|---|
| 12 | `O_NONBLOCK` removed | **HUNG** (`timeout 75`) `test_a_fifo_is_refused_rather_than_waited_on` |
| 13 | `S_ISREG` removed | **1 failed** `test_a_directory_is_refused` |
| 14 | `O_NOFOLLOW` removed | **1 failed** `test_a_symlinked_settings_file_is_not_read_through` |
| 15 | size cap removed | **1 failed** `test_discovery_refuses_an_oversized_settings_file` |
| 16 | not-an-object check removed | **1 failed** `test_a_settings_file_that_is_not_an_object_is_reported` |
| 17 | Open path bypasses `_read_json` | **HUNG** (`timeout 75`) `test_the_open_path_reads_through_the_same_gate` |

## Item 5

| # | mutation | observed |
|---|---|---|
| 18 | (control) the fixed test exercises the success path | **passes**; before the fix it closed over an undefined `ipts` and never reached the assertion |

## Three that did not red on the first pass

Recorded because a ledger of only successes is the prose count wearing a table.
All three were **my tests, not the code** — and two of them revealed that the
behaviour they named was unobservable as written:

1. invariant (a) arm — hidden behind the whitelist; isolating guard added.
2. B1 re-read — invisible without an intervening Load; sequence-specific guard added.
3. `aboutToQuit` — wired in `main()`, which no test calls; wiring factored out so a test can install it.
