# Liquids Reflectometer

[![CI](https://github.com/neutrons/LiquidsReflectometer/actions/workflows/test_and_deploy.yml/badge.svg)](https://github.com/neutrons/LiquidsReflectometer/actions/workflows/test_and_deploy.yml)
[![codecov](https://codecov.io/gh/neutrons/LiquidsReflectometer/graph/badge.svg?token=H90K5RDGK4)](https://codecov.io/gh/neutrons/LiquidsReflectometer)
[![Documentation](https://readthedocs.org/projects/liquidsreflectometer/badge/?version=latest)](https://lr-reduction.readthedocs.io/latest/)

Reduction scripts for the Liquids Reflectometer. This includes both automated reduction scripts and useful scripts to reprocess data.

## Run Test Suite

The built-in-test suite can be run in several ways:

1. `pixi run test-reduction` - runs the full test suite (requires git-lfs installed and tests/data/liquidsreflectometer-data checked out)
2. `pixi run test-with-report` - full test suite, producing `pytest_report.html` that you can browse
3. `PYTEST_SKIP_NUMERIC_DIFFS=yes pixi run test-with-report` - will skip the (currently 3) known numerical faults

### git-lfs

Install git-lfs on your machine (exercise left to the reader...), then:
```
( cd tests/data/liquidsreflectometer-data && git checkout )
```
