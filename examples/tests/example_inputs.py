"""
The files each example reads, as paths below the example data folder (examples/example_paths.py).

The tests use this list to skip an example whose inputs are not there, and it is the list of what the example
data of the test-data repository must hold. Printed one path per line, it feeds a copy:

    python examples/tests/example_inputs.py | rsync -a --files-from=- <instrument folder>/ <example data folder>/
"""


def nexus(experiment, *runs):
    return [f"{experiment}/nexus/REF_L_{run}.nxs.h5" for run in runs]


def files(folder, *names):
    return [f"{folder}/{name}" for name in names]


_SHARED = "shared/lr_reduction/new_workflow_test_outputs"
_COMMISSIONING = "IPTS-36119"
_CD_ATTENUATION = files("shared/Cd_transmission", "Cd_mu_2025.dat")

# A clean substrate at three angles, in D2O and in H2O, with the direct beams the automatic reduction used for them.
_DB = files(f"{_COMMISSIONING}/shared/transmission", "DB_Si_3in_A1.dat", "DB_Si_3in_A2.dat", "DB_Si_3in_A3.dat")
_D2O = nexus(_COMMISSIONING, 234162, 234163, 234164)
_H2O = nexus(_COMMISSIONING, 234165, 234166, 234167)
_DIRECT_CONFIG = _DB + _D2O
_FROM_DAT = (
    files(f"{_COMMISSIONING}/shared/autoreduce/new_reduction", "REFL_234162_combined_autoreduction.dat") + _DB + _D2O + _H2O[:2]
)
_FROM_JSON = _FROM_DAT + _H2O  # the settings .json is written by example_from_dat, which these examples run first

_TEMPLATE_DB = files("shared/EBW/Cd_DB_processing/DBs", "A1_air_div1_Cd_DB.dat", "A2_air_div1_Cd_DB.dat", "A3_air_div1_Cd_DB.dat")
_TEMPLATE_RUNS = nexus("IPTS-30101", 211029, 211030, 211031)

INPUTS = {
    "example_direct_beam": {
        # In the test-data repository before the examples were: the Cd series of the maintainers' attenuation tests.
        "example_direct_beam": _CD_ATTENUATION + nexus("IPTS-37787", 232721, 232722, 232723, 232724, 232725, 232726),
        "example_direct_beam_pixel_offset": _CD_ATTENUATION + nexus(_COMMISSIONING, 235850),
    },
    "example_nr_reduction": {
        "example_mean_theta_reduction": _DIRECT_CONFIG,
        "example_constant_tof_reduction": _DIRECT_CONFIG,
        "example_mean_theta_reduction_8col": _DIRECT_CONFIG,
        "example_mean_theta_reduction_savepdf": _DIRECT_CONFIG,
        "example_mean_theta_reduction_savepdf_noshow": _DIRECT_CONFIG,
    },
    "example_nr_reduction_from_file": {
        "example_from_dat": _FROM_DAT,
        "example_from_json": _FROM_JSON,
        "example_wrong_order": _FROM_JSON,
        "example_one_missing": _FROM_JSON,
        "example_with_search": _FROM_JSON,
        "example_with_savepdf": _FROM_JSON,
        "example_with_savepdf_noshow": _FROM_JSON,
        "example_with_search_savepdf": _FROM_JSON,
        "example_with_8col": _FROM_JSON,
        "example_with_8col_search": _FROM_JSON,
        "example_for_autoreduction": files(f"{_COMMISSIONING}/shared/autoreduce", "reduce_settings.json") + _DB + _D2O[2:],
        "example_incidenttheta": files(f"{_COMMISSIONING}/shared/reduced/Aug2026", "REFL_231035_settings.json")
        + files(f"{_COMMISSIONING}/shared/transmission/Aug2026", *(f"A{angle}_div5_Cd.txt" for angle in range(1, 7)))
        + nexus(_COMMISSIONING, 231035),
    },
    "example_nr_from_template": {
        "example_template_reduction": files(_SHARED, "test_template.xml") + _TEMPLATE_DB[:1] + _TEMPLATE_RUNS[:1],
        "example_template_reduction_3ang": files(_SHARED, "test_template_3ang.xml") + _TEMPLATE_DB + _TEMPLATE_RUNS,
        "example_template_reduction_new": files(_SHARED, "REFL_211029_template_new.xml") + _TEMPLATE_DB + _TEMPLATE_RUNS,
    },
}


def all_inputs():
    return sorted({path for examples in INPUTS.values() for paths in examples.values() for path in paths})


if __name__ == "__main__":
    print("\n".join(all_inputs()))
