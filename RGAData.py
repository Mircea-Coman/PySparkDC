import pandas as pd
import numpy as np
import time
import datetime
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
from Data import Data
from default_file_structures import DEFAULT_RGA_STRUCTURE

TORR_TO_MBAR = 1.33322368

class RGAData(Data):
    def __init__(self, *args, structure = DEFAULT_RGA_STRUCTURE):
        super().__init__(*args, structure = structure)
        self.calculate_derived_columns()

    def get_subset_amu(self, mass):
        mask = (self.df.mass == mass)
        return RGAData(self.df[mask], self.label_dict, self.unit_dict, self.concatenation_type_dict)


    def calculate_derived_columns(self):
        recalculate = 'pressure_mbar' in self.df
        if recalculate:
            self.df.loc[:, 'pressure_mbar'] = (self.df['pressure_torr'] * TORR_TO_MBAR)
        else:
            self.df['pressure_mbar'] = (self.df['pressure_torr'] * TORR_TO_MBAR)
            self.label_dict['pressure_mbar'] = 'Pressure'
            self.unit_dict['pressure_mbar'] = 'mbar'
            self.concatenation_type_dict['pressure_mbar'] = 'normal'

    def plot_masses(self, masses, x_key = 'timestamp', plot_datetime = True, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', \
    ax = None, figsize = (13, 8), linestyle = '-', color_cycle = 'default', scaling_factor_y = 1):
        n_masses = len(masses)
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        if color_cycle == 'default':
            color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        for i in range(0, n_masses):
            color = color_cycle[i%len(color_cycle)]
            subset = self.get_subset_amu(masses[i])
            subset.plot('pressure_mbar', x_key = 'timestamp', plot_datetime = plot_datetime, date_format = date_format, timezone = timezone, \
            ax = ax, marker = None, linestyle = '-', color = color, label = f"{masses[i]} amu", scaling_factor_y = scaling_factor_y)
        return ax

    @staticmethod
    def read_from_file(filename, header = None, delimiter = ',', skiprows = 22, engine ='c', structure = DEFAULT_RGA_STRUCTURE, timezone = "Europe/Stockholm"):
        tzinfo = ZoneInfo(timezone)
        file = open(filename, 'r')
        lines = file.readlines()
        n_lines = len(lines)
        n_data_rows = n_lines-22
        data = np.empty([n_data_rows, 4])
        count = 0
        for line in lines:
            if count == 2:
                date_array = RGAData.__get_data_from_line__(line, [1,3], type = 'str')
                date_string = date_array[0] + ' ' + date_array[1]
                timestamp = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tzinfo).timestamp()
            # elif count == 6:
            #     resolution = __get_data_from_line__(line, [6])[0]
            elif count > 2:
                break
            count += 1
        file.close()
        data = Data.read_from_files([filename], header = header, delimiter = delimiter, engine = engine, skiprows = skiprows, structure = structure)
        data.df['timestamp'] = (data.df['rel_time'] / 1000.0 + timestamp)
        data.label_dict['timestamp'] = 'Timestamp'
        data.unit_dict['timestamp'] = 's'
        data.concatenation_type_dict['timestamp'] = 'normal'
        rga_data = RGAData(data.df, data.label_dict, data.unit_dict, data.concatenation_type_dict)
        return rga_data


    @staticmethod
    def __get_data_from_line__(line, indices, sep = ',', type = 'float'):
        line_split = line.split(sep)
        n = len(indices)
        data = [0]*n
        for i in range(0, n):
             temp = line_split[indices[i]].strip()
             if type == 'str':
                 data[i] = temp
             elif type == 'float':
                 data[i] = float(temp)
        return data
