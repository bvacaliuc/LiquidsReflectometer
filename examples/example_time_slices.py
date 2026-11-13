"""
Example usage of time-sliced reduction (new_reduction_time_resolved)

Inputs are read below the example data folder and the slices are written to the example output folder
(see example_paths). Nothing runs on import.
"""

import json

import lr_reduction.new_reduction_time_resolved as reduction

from example_paths import data_folder, output_folder, run_examples

EXPERIMENT = "IPTS-36776"


def raw_data():
    return data_folder() / EXPERIMENT / "nexus"


def settings_json():
    """
    The settings file of the examples, as a copy in the output folder that names the example data's direct beams.

    The settings file names the direct-beam folder of the experiment it was written for, and the time-slice calls
    take the raw data and output folders but not that one.
    """
    source = data_folder() / "shared" / "lr_reduction" / "new_workflow_test_outputs" / "REFL_227158_settings.json"
    settings = json.loads(source.read_text())
    settings["_DBpath_override"] = str(data_folder() / EXPERIMENT / "shared" / "transmission")
    copy = output_folder() / source.name
    copy.write_text(json.dumps(settings, indent=2))
    return copy


def slices_from_json(slices=2):
    run_list = 227164

    output = reduction.reduce_time_slices(run_list, settings_json(), EXPERIMENT, slices,
                                          savepath=output_folder(), plot_time=True, datapath=raw_data())

    return output

def times_from_json(starts=[0,80,120], stops=[80,120,136]):
    run_list = 227164

    output = reduction.reduce_time_list(run_list, settings_json(), EXPERIMENT, starts, stops,
                                        savepath=output_folder(), plot_time=True, subname_input=None, datapath=raw_data())

    return output


def example_two_slices():
    return slices_from_json(slices=2)


def example_five_slices():
    return slices_from_json(slices=5)


def example_time_list():
    return times_from_json()


if __name__ == '__main__':
    run_examples([example_two_slices, example_five_slices, example_time_list])
