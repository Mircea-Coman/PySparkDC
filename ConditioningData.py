from Data import Data
from default_file_structures import DEFAULT_CONDITIONING_STRUCTURE, LABVIEW_TIMESTAMP_OFFSET
import os
import glob
import pandas as pd
import Utils
import numpy as np

DEFAULT_FILENAME = 'Marx_data.txt'

class ConditioningData(Data):
    def __init__(self, *args, electrode_name = ''):
        self.electrode_name = electrode_name
        super().__init__(*args)
        self.calculate_derived_columns()

    def calculate_derived_columns(self):
        self.df['target_field'] = (self.df['target_voltage'] / self.df['gap'])
        self.add_info_dict_entry('target_field', label = 'Target Field', unit = 'MV/m')

        self.df['field'] = (self.df['output_voltage'] / self.df['gap'])
        self.add_info_dict_entry('field', label = 'Electric Field', unit = 'MV/m')

    def get_run_separators(self, run_id, key = 'run_id'):
        dim = Utils.dim(run_id)
        if len(dim) == 0:
            run_id = [run_id]
        elif len(dim) > 1:
            raise ValueError("Invalid run_id")

        run_separators = np.empty([len(run_id), 2], dtype = int)

        for j in range(0, len(run_id)):
            mask = self.df[key] == run_id[j]
            if any(mask):
                start = np.min(np.argwhere(mask))
                end = np.max(np.argwhere(mask))

                run_separators[j, 0] = start
                run_separators[j, 1] = end
            else:
                run_separators[j, 0] = -9999
                run_separators[j, 1] = -9999


        if len(dim) == 0:
            return run_separators[0]
        else:
            return run_separators


    def plot_standard(self, first_axis = 'field', second_axis = 'BDs', third_axis = 'BDR', plot_third_axis = False, log_third_axis = True,\
     figsize = (20, 8), fontsize = 15, marker = None, markersize = 5, linestyle = '-', linewidth = 2, color = None, labels = None, stripe = True,
     color_runs = None, use_style_dict = True):
        if plot_third_axis:
            list = [[first_axis], [second_axis], [third_axis]]
        else:
            list = [[first_axis], [second_axis]]

        fplot = self.plot(list, x_key = 'all_pulses', figsize = figsize)
        if first_axis == 'field' or first_axis == 'target_field':
            fplot.set_axis_ylabel(0, 'Electic Field [MV/m]')
        elif first_axis == 'output_voltage' or first_axis == 'target_voltage':
            fplot.set_axis_ylabel(0, 'Voltage [V]')

        if second_axis == 'BDs':
            fplot.set_axis_ylabel(1, 'Voltage [V]')

        if third_axis == 'BDR' and plot_third_axis:
            fplot.set_axis_ylabel(2, 'Number of Breakdowns')

        if log_third_axis and plot_third_axis:
            fplot.set_axis_yscale(2, 'log')
            fplot.set_axis_ylim(2, [1E-8, 1E-3])

        fplot.set_xlim_from_data(self, 'all_pulses')

        if stripe: fplot.stripe_files(self, x_key = 'all_pulses')


        if color_runs is not None:
            for color_run in color_runs:
                current_color = color_run['color']
                current_run = color_run['run']
                dim_runs = Utils.dim(current_run)
                if len(dim_runs) == 0:
                    current_run = [current_run]
                elif len(dim_runs) > 1:
                    raise ValueError('Invalid run')

                sep = self.get_run_separators(current_run)
                fplot.stripe_from_data(self, sep[:, 0], sep[:, 1], x_key = 'all_pulses', ax_id = 0, color = current_color)

        fplot.set_fontsize(fontsize)
        fplot.set_xlabel('Number of Pulses')
        fplot.fig.suptitle(f"{self.electrode_name}, Runs {self.df.run_id.min()}-{self.df.run_id.max()}")
        return fplot

    @staticmethod
    def read_from_files(file_paths, header = None, delimiter = '\s+', skiprows = 1, engine ='python', info_dict = DEFAULT_CONDITIONING_STRUCTURE, electrode_name = ''):
        data = Data.read_from_files(file_paths, header = header, delimiter = delimiter, engine = engine, skiprows = skiprows, info_dict = DEFAULT_CONDITIONING_STRUCTURE)
        cond_data = ConditioningData(data.df, data.info_dict)
        return cond_data

    @staticmethod
    def read_runs(data_folder, electrode, runs, header = None, delimiter = '\s+', skiprows = 1, engine ='python', info_dict = DEFAULT_CONDITIONING_STRUCTURE):
        electrode_path = os.path.join(data_folder, electrode)
        files_to_read = []
        for current_run in runs:
            run_path = glob.glob(f"{electrode_path}/*{electrode}*{current_run:03d}")[0]
            file_path = os.path.join(run_path, DEFAULT_FILENAME)
            files_to_read.append(file_path)
        cond_data = ConditioningData.read_from_files(files_to_read, header = header, delimiter = delimiter, skiprows = skiprows, \
        engine = engine, info_dict = info_dict, electrode_name = electrode)
        col_len = cond_data.df.shape[1]

        #make the run_id column, which shows the run number
        cond_data.df.insert(col_len, "run_id", runs[pd.Series.to_numpy(cond_data.df.file_id)], True)
        return cond_data
