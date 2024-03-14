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
    def __init__(self, *args):
        super().__init__(*args)
        self.calculate_derived_columns()

    def get_subset_amu(self, mass):
        mask = (self.df.mass == mass)
        return RGAData(self.df[mask], self.info_dict)


    def calculate_derived_columns(self):
        recalculate = 'pressure_mbar' in self.df
        if recalculate:
            self.df.loc[:, 'pressure_mbar'] = (self.df['pressure_torr'] * TORR_TO_MBAR)
        else:
            self.df['pressure_mbar'] = (self.df['pressure_torr'] * TORR_TO_MBAR)
            self.add_info_dict_entry('pressure_mbar', label = 'Pressure', unit = 'mbar')

    def plot_masses(self, masses, key = 'pressure_mbar', x_key = 'timestamp', datetime_plot = True, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', \
    ax_id = None, fplot = None, figsize = (13, 8), linestyle = '-', linewidth = 2, color = None, marker = 'None', markersize = 5, scaling_x = 1, scaling_y = 1):
        n_masses = len(masses)
        if fplot is None:
            fplot = FancyPlot(figsize = figsize, n_ax = 1)

        for i in range(0, n_masses):
            mask = (self.df.mass == masses[i])
            print(masses[i])
            fplot.plot(self.df[x_key][mask],  self.df[key][mask], scaling_x = 1, scaling_y = scaling_y, date_format = date_format, timezone = timezone, datetime_plot = datetime_plot, \
             ax_id = ax_id, color = color, marker = marker, markersize = markersize, linestyle = linestyle, linewidth = linewidth, label = f"{masses[i]} amu")

        return fplot

    @staticmethod
    def read_from_file(filename, header = None, delimiter = ',', skiprows = 22, engine ='c', info_dict = DEFAULT_RGA_STRUCTURE, timezone = "Europe/Stockholm"):
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
        data = Data.read_from_files([filename], header = header, delimiter = delimiter, engine = engine, skiprows = skiprows, info_dict = info_dict)
        data.df['timestamp'] = (data.df['rel_time'] / 1000.0 + timestamp)
        data.add_info_dict_entry('timestamp', label = 'Timestamp', unit = 's')

        rga_data = RGAData(data.df, data.info_dict)
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
