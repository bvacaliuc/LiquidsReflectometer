# -*- coding: utf-8 -*-
"""
Example usage of the reduction from a settings file: a .json of settings, or a reduced .dat whose header holds them

Inputs are read below the example data folder and results are written to the example output folder
(see example_paths). The settings files name the folders of the experiment they were written for, so each example
gives the folders to use (the raw data, the direct beams, the output) and they replace the file's.
Nothing runs on import.
"""

import lr_reduction.new_reduction_from_file as reduction

from example_paths import data_folder, output_folder, run_examples

# The runs of these examples were measured in the instrument's commissioning experiment: one clean substrate at
# three angles, in D2O and then in H2O, with the same slits. The instrument's automatic reduction reduced both sets
# when they were measured, and the examples start from what it wrote.
EXPERIMENT = "IPTS-36119"
D2O = [234162, 234163, 234164]
H2O = [234165, 234166, 234167]


def raw_data(experiment_id=EXPERIMENT):
    return data_folder() / experiment_id / "nexus"


def direct_beams(experiment_id=EXPERIMENT):
    return data_folder() / experiment_id / "shared" / "transmission"


def settings_json():
    """The settings file most examples start from: the one example_from_dat writes, for the D2O set."""
    written = output_folder() / f"REFL_{D2O[0]}_settings.json"
    if not written.is_file():
        example_from_dat()
    return written


def example_from_dat():
    # Five runs of two sets: the D2O set, and the first two angles of the H2O set.
    run_list = D2O + H2O[:2]
    # The settings are in the header of the file the automatic reduction wrote for the D2O set.
    setting_file = data_folder() / EXPERIMENT / "shared" / "autoreduce" / "new_reduction" / f"REFL_{D2O[0]}_combined_autoreduction.dat"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams()}
    output = reduction.reduce_from_file(run_list, setting_file, EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=True)

    return output


def example_from_json():
    run_list = H2O
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams()}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=False)

    return output

def example_wrong_order():
    run_list = [H2O[1], H2O[0], H2O[2]]
    Sname = f"REFL_{H2O[0]}_wrong_order_test"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(), 'Sname': Sname}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=False)

    return output

def example_one_missing():
    run_list = H2O[1:]
    subname = "missing_test"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(), "subname": subname}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=False)

    return output

def example_with_search():
    # check_for_prior looks in the output folder for the other runs of the set, reduced earlier: reduce them first.
    example_one_missing()
    run_list = H2O[:1]
    subname = "missing_test"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(), "subname": subname}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=False, check_for_prior=True)

    return output

def example_with_savepdf():
    run_list = H2O
    Sname = f"REFL_{H2O[0]}_save_test"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(), "Sname": Sname}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=False, save_pdf_summary=True)

    return output

def example_with_savepdf_noshow():
    run_list = H2O
    subname = "save_test_v2"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(), "subname": subname}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=False, save_json=False, save_pdf_summary=True)

    return output

def example_with_search_savepdf():
    # check_for_prior looks in the output folder for the other runs of the set, reduced earlier: reduce them first.
    example_one_missing()
    run_list = H2O[:1]
    subname = "missing_test"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(), "subname": subname}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=False, check_for_prior=True, save_pdf_summary=True)

    return output

def example_with_8col():
    run_list = H2O
    subname = "eight_test"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(), "subname": subname, "save8col": True}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=False, check_for_prior=False, save_pdf_summary=True)

    return output

def example_with_8col_search():
    # check_for_prior looks in the output folder for the other runs of the set, reduced earlier: reduce them first.
    example_with_8col()
    run_list = H2O[1:2]
    subname = "eight_test"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(), "subname": subname, "save8col": True}
    output = reduction.reduce_from_file(run_list, settings_json(), EXPERIMENT, datapath=raw_data(), override_params=override_params, plot=True, save_json=False, check_for_prior=True, save_pdf_summary=True)

    return output

def example_for_autoreduction():
    # One run, as the automatic reduction is given them, with the settings file the experiment keeps for it.
    experiment_id = EXPERIMENT
    run_list = D2O[2:]
    setting_file = data_folder() / experiment_id / "shared" / "autoreduce" / "reduce_settings.json"
    subname = "autoreduction"
    override_params = {'Spath': output_folder(), 'DBpath': direct_beams(experiment_id), "subname": subname}
    output = reduction.reduce_from_file(run_list, setting_file, experiment_id, datapath=raw_data(experiment_id), override_params=override_params, plot=True, save_json=False, check_for_prior=True, save_pdf_summary=False)

    return output

def example_incidenttheta():
    experiment_id = "IPTS-36119"
    run_list = [231035]
    setting_file = data_folder() / experiment_id / "shared" / "reduced" / "Aug2026" / "REFL_231035_settings.json"
    DBpath = data_folder() / experiment_id / "shared" / "transmission" / "Aug2026"
    override_params = {'Spath': output_folder(), 'DBpath': DBpath}
    output = reduction.reduce_from_file(run_list, setting_file, experiment_id, datapath=raw_data(experiment_id), override_params=override_params, plot=True, save_json=False)

    return output

if __name__ == '__main__':
    run_examples([
        example_from_dat,
        example_from_json,
        example_wrong_order,
        example_one_missing,
        example_with_search,
        example_with_savepdf,
        example_with_savepdf_noshow,
        example_with_search_savepdf,
        example_with_8col,
        example_with_8col_search,
        example_for_autoreduction,
        example_incidenttheta,
    ])
