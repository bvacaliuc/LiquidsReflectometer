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
