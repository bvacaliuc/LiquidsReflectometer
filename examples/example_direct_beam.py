"""
Example usage of the Direct_Beam class

Inputs are read below the example data folder and the direct beams are written to the example output folder
(see example_paths). Nothing runs on import.
"""

import numpy as np

from lr_reduction.direct_beam_maker import Direct_Beam

from example_paths import data_folder, output_folder, run_examples


def example_direct_beam():
    """A direct beam from four runs with different Cd attenuation"""
    db = Direct_Beam()
    db.savepath = output_folder()  # Set the directory where you want to save the output
    db.NEXUSpath = data_folder() / "IPTS-36119" / "nexus"  # Set the path to your Nexus file
    db.Chop2_cut_fn = [2.077, -16818.0]
    db.DTCcut = 1.25
    db.DTCcut_config1 = 1.8

    run_list = np.arange(225318,225321+1)
    DB_out = db.create_db(run_list=run_list, save_name='direct_beam_test.dat',
                          plot=True, flip_atten=True)
    return DB_out


def example_direct_beam_pixel_offset():
    """A direct beam whose position on the detector is offset: the y pixel range is set"""
    db = Direct_Beam()
    db.savepath = output_folder()  # Set the directory where you want to save the output
    db.NEXUSpath = data_folder() / "IPTS-36119" / "nexus"  # Set the path to your Nexus file
    db.Chop2_cut_fn = [2.077, -16818.0]
    db.DTCcut = 1.25
    db.DTCcut_config1 = 1.8
    db.y_ROI = [200,250]

    run_list = [235850]
    DB_out = db.create_db(run_list=run_list, save_name='direct_beam_test_pixel_offset.dat',
                          plot=True, flip_atten=False)
    return DB_out


def example_direct_beam_atten_as_logged():
    """A direct beam from runs whose Atten log needs no flip"""
    db = Direct_Beam()
    db.savepath = output_folder()  # Set the directory where you want to save the output
    db.NEXUSpath = data_folder() / "IPTS-36119" / "nexus"  # Set the path to your Nexus file
    db.Chop2_cut_fn = [2.077, -16818.0]
    db.DTCcut = 1.25
    db.DTCcut_config1 = 1.8
    DB_out = db.create_db(run_list=[226473,226474,226475,226476], save_name='direct_beam_test_atten_as_logged.dat',
                          plot=True)
    return DB_out


def example_direct_beam_cd_list():
    """Single runs with the Cd attenuator setting given for each, replacing the run's Atten log"""
    db = Direct_Beam()
    db.savepath = output_folder()  # Set the directory where you want to save the output
    db.NEXUSpath = data_folder() / "IPTS-36119" / "nexus"  # Set the path to your Nexus file

    db.DTCcut_config1 = 1.8

    run_list = [231187]
    DB_out = db.create_db(run_list=run_list, save_name='DB_231187_Cd_test.dat',
                          plot=True, cd_list=[[1, 0, 0, 0]])


    run_list = [231189]
    DB_out = db.create_db(run_list=run_list, save_name='DB_231189_Cd_test.dat',
                          plot=True, cd_list=[[0, 1, 0, 0]])

    run_list = [231191]
    DB_out = db.create_db(run_list=run_list, save_name='DB_231191_Cd_test.dat',
                          plot=True, cd_list=[[1, 0, 0, 0]])
    return DB_out


if __name__ == '__main__':
    run_examples([
        example_direct_beam_atten_as_logged,
        example_direct_beam,
        example_direct_beam_pixel_offset,
        example_direct_beam_cd_list,
    ])
