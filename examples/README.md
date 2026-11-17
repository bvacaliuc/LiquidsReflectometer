# Examples

Scripts that show how the reduction is called. Each file holds several examples, one function each.

| File | Shows |
|---|---|
| `example_nr_reduction.py` | setting up a config object and calling the reduction directly |
| `example_nr_reduction_from_file.py` | reducing from a settings `.json`, or from a reduced `.dat` whose header holds the settings |
| `example_nr_from_template.py` | reducing from an `.xml` template, as autoreduction does |
| `example_direct_beam.py` | making a direct beam file |

## Running

```sh
python examples/example_nr_reduction.py                                  # every example of the file
python examples/example_nr_reduction.py example_constant_tof_reduction   # the ones named
```

## Where the data comes from and where results go

No example names a folder. Two environment variables do (`example_paths.py`):

| Variable | Meaning | When unset |
|---|---|---|
| `LR_REDUCTION_EXAMPLE_DATA` | folder the inputs are read from, laid out as the instrument's folder is (`IPTS-<n>/nexus`, `IPTS-<n>/shared/...`, `shared/...`) | `tests/data/liquidsreflectometer-data/examples` of this repository |
| `LR_REDUCTION_EXAMPLE_OUTPUT` | folder the results are written to; created when missing | `lr_reduction_example_output` in the folder you start from |

At the facility the experiments' own files can be read in place:

```sh
LR_REDUCTION_EXAMPLE_DATA=/SNS/REF_L LR_REDUCTION_EXAMPLE_OUTPUT=<a folder of yours> python examples/example_nr_reduction_from_file.py
```

Elsewhere, fetch the repository's test data: `git submodule update --init && git submodule foreach git lfs pull`.

## The runs the examples use

Every run is from one of the instrument's two commissioning experiments (IPTS-36119, IPTS-30101), except the Cd
series, which the test-data repository held already.

| Examples | Runs | What they are |
|---|---|---|
| `example_direct_beam` | 232721 to 232726 (IPTS-37787) | one direct beam through six thicknesses of Cd; six of the seven runs behind `DB_Si_3in_A2.dat` |
| `example_direct_beam_pixel_offset` | 235850 | a direct beam with the detector moved (`tthd` -1.5) |
| `example_nr_reduction.py`, `example_from_dat`, `example_for_autoreduction` | 234162 to 234164 | a clean substrate in D2O, three angles |
| `example_from_dat` (two angles), `example_from_json` and the eight after it | 234165 to 234167 | the same substrate in H2O, same slits |
| `example_incidenttheta` | 231035 | the first angle of a six-angle series, iridium in air |
| `example_nr_from_template.py` | 211029 to 211031 (IPTS-30101) | three angles measured in 2024, before the `Coordinates` log |

The substrate sets were reduced by the instrument's automatic reduction when they were measured. The examples take
its direct beams (`shared/transmission/DB_Si_3in_A*.dat`), its pixel ranges (`shared/autoreduce/reduce_settings.json`)
and, for `example_from_dat`, the settings in the header of the file it wrote
(`shared/autoreduce/new_reduction/REFL_234162_combined_autoreduction.dat`). Every file an example reads is at the
facility in the folder of the experiment its runs belong to; none was made for the examples. The one file read in
the instrument's own shared folder is the Cd attenuation table (`shared/Cd_transmission/Cd_mu_2025.dat`), which is
the file the reduction's settings name.

Until November 2026 the examples used runs of four more experiments (IPTS-36681, IPTS-36776, IPTS-35331, and
225318 to 225321 of IPTS-36119). They were moved so that the example data holds commissioning measurements only and
is a third of the size. What no longer has an example: `flip_atten=True`, for direct-beam runs of early 2026 whose
log has the attenuators inverted (a comment in `example_direct_beam` says so).

## The examples are tested

`pixi run test-examples` (part of `pixi run test-reduction`, so of CI) calls every example function as it is
written, with the results sent to a scratch folder. Where an example shows a plot and waits for its window to be
closed, the test writes the figure to a file and closes it. A warning raised while an example runs fails its test. An example whose input files are not
on the machine is reported as skipped; the summary at the end of the run names each such example and the first file
it misses, and the first lines of the run name the folder that was searched.

The examples describe how the reduction is meant to be called. A change to the reduction that makes one fail
changes that, and needs the example's author to agree.

When you add an example:

1. Write it as a function named `example_...` that returns its result. Take folders from `data_folder()` and
   `output_folder()`.
2. Add it to the list given to `run_examples` at the end of its file.
3. List the files it reads in `tests/example_inputs.py`. `python examples/tests/example_inputs.py` prints every
   input of every example, one path per line.
