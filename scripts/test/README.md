# `scripts/test`

Session diagnostics cited from committed documents or from code comments.

Anything referenced by a committed file has to live in the repository — a
reader on another machine cannot run `/tmp/probe.py`. These scripts are the
measurements behind claims made elsewhere in the tree.

| Script | Answers | Cited from |
|---|---|---|
| `measure_fit_path_dependence.py` | How far do the scaling-factor fit parameters move when only Mantid's minimizer changes, with the input data identical? | `tests/test_scaling_factors_workflow.py`, the `_TOL` rationale for `b` |

## Running them

From the repository root, in the project environment:

```sh
pixi run python scripts/test/measure_fit_path_dependence.py
```

`measure_fit_path_dependence.py` needs the test data submodule at
`tests/data/liquidsreflectometer-data` — the same fixture the suite uses — and
takes a few minutes, since it runs the scaling-factor workflow once per
minimizer.
