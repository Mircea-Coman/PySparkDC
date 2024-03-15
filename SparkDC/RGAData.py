import pandas as pd
import numpy as np
import time
import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt

from . import Data
from .default_file_structures import DEFAULT_RGA_STRUCTURE
from . import Utils

TORR_TO_MBAR = 1.33322368

class RGAData(Data):
    def __init__(self, *args):
        """
        Initializer for the StatusData Class
        Parameters
        ----------
        df: pandas.core.frame.DataFrame
            The data frame.
            If the argument is not present, the data object is initialized with an empty dataframe
        info_dict: dict, optional
            Dictionary of labels, unit and concatenation_type for the data
            Example of info_dict:
            {
                'temp':       {'col': 0, 'label': 'Temperature',   'unit':   'K',   'concatenation_type': 'normal'},
                'all_pulses': {'col': 1, 'label': 'All Pulses',    'unit':   '',    'concatenation_type': 'additive'},
            }

        """
        super().__init__(*args)
        self.calculate_derived_columns()

    def get_subset_amu(self, mass):
        """
        Returns a new RGAData, containing only the data for a specified mass

        Parameters
        ----------
        mass:           double
                        The mass in amu.

        Returns
        -------
        subset:         RGAData
                        RGAData object corresponding to the data for the specified mass
        """
        mask = (self.df.mass == mass)
        return RGAData(self.df[mask], self.info_dict)


    def calculate_derived_columns(self):
        """
        (Re)calculates the derived columns: 'pressure_mbar'
        """
        recalculate = 'pressure_mbar' in self.df
        if recalculate:
            self.df.loc[:, 'pressure_mbar'] = (self.df['pressure_torr'] * TORR_TO_MBAR)
        else:
            self.df['pressure_mbar'] = (self.df['pressure_torr'] * TORR_TO_MBAR)
            self.add_info_dict_entry('pressure_mbar', label = 'Pressure', unit = 'mbar')

    def plot_masses(self, masses, key = 'pressure_mbar', x_key = 'timestamp', datetime_plot = True, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', \
    ax_id = None, fplot = None, figsize = (13, 8), fontsize = 12, fontweight = 'normal', linestyle = '-', linewidth = 2, \
    color = None, marker = 'None', markersize = 5, scaling_x = 1, scaling_y = 1):
        """
        Plots the data for a specified mass

        Parameters
        ----------
        masses:             double or list of double
                            The masses in amu.

        key:                str, default: 'pressure_mbar'

        x_key:              str, default: 'timestamp'
                            The key corresponding to the column to be plotted on the x axis.
        fplot               FancyPlot, default: None
                            The fancy plot on which the plot will be drawn. If None, a new one will be created with figsize
        figsize:            tuple, default: (13, 8)
                            The size of the figure in inches. Used only when fplot is None
        fontsize:           int, default: 12
                            Dictionary of units for each data column.
                            If not present, it is created from the structure argument
        fontweight:         ['normal'|'bold'|'heavy'|'light'|'ultrabold'|'ultralight'], default: 'normal'
        ax_id:              int or list of int, default = None
                            The index of the matplotlib axes in the axs list on which the data will be plotted. If None, the axis used will be 0, 1, 2, 3...
        date_format:        str, default = '%m-%d %H:%M:%S'
                            The format of the data used if datetime_plot is enabled
        timezone:           str, default = 'Europe/Stockholm'
                            The timezone used if if datetime_plot is enabled
        datetime_plot:      bool, default: True
                            Specified whether the x axis is formated as datetime. If the x data are already mdates, this should be set to False
        marker:             matplotlib marker, default: None
        markersize:         int, default: 5
        linestyle:          matplotlib linestyle, default: 'solid'
        linewidth:          int, default: 2
        color:              matplotlib color, default: None (a color is selected from the color cycle)
        labels:             str or list of str, default: None
                            The labels of the Line2D plot. If None, get the labels from the info_dict of the Data object
        scaling_x:          double
                            The x data is multiplied by this number when plotting. Useful when converting units
        scaling_y:          double
                            The y data is multiplied by this number when plotting. Useful when converting units
        style_dict:         dict,   default: DEFAULT_STYLE
                            The style dictionary used

        Returns
        -------
        fplot:          FancyPlot
                        The plot on which the data was plotted
        """
        dim_masses = Utils.dim(masses)
        if len(dim_masses) == 0: masses = [masses] # if masses is just a scalar
        n_masses = len(masses)
        if fplot is None:
            fplot = FancyPlot(figsize = figsize, n_ax = 1)

        for i in range(0, n_masses):
            mask = (self.df.mass == masses[i])
            fplot.plot(self.df[x_key][mask],  self.df[key][mask], scaling_x = 1, scaling_y = scaling_y, date_format = date_format, timezone = timezone, datetime_plot = datetime_plot, \
             ax_id = ax_id, color = color, marker = marker, markersize = markersize, linestyle = linestyle, linewidth = linewidth, label = f"{masses[i]} amu")

        return fplot

    @staticmethod
    def read_from_files():
        '''
        To be implemented
        '''
        return -1

    @staticmethod
    def read_from_file(filename, header = None, delimiter = ',', skiprows = 22, engine ='c', info_dict = DEFAULT_RGA_STRUCTURE, timezone = "Europe/Stockholm"):
        """
        Reads data from a single file
        Parameters
        ----------
        filename:       str
                        The filepath from where the data will be read
        timezone:       str
                        The timezone used when data was taken. It is needed because the file contains the time when the scan was started
        header:         int, default: None
                        Row number(s) containing column labels and marking the start of the data (zero-indexed).
        delimiter:      char, default: ','
                        The delimiter used in the file.
        info_dict:      dict, default: DEFAULT_RGA_STRUCTURE
                        The info_dict of the file
        engine:         str, default: 'c'
                        Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine.
        skiprows:       int, default: 22
                        Skips the first N rows when reading the file
        Returns
        -------
        data:           RGAData
                        RGAData object corresponding to the data read from the file path
        """
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
                timestamp = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tzinfo).timestamp() #get the time when the scan was started
            elif count > 2:
                break
            count += 1
        file.close()
        data = Data.read_from_files([filename], header = header, delimiter = delimiter, engine = engine, skiprows = skiprows, info_dict = info_dict)
        data.df['timestamp'] = (data.df['rel_time'] / 1000.0 + timestamp) #make the timestamp
        data.add_info_dict_entry('timestamp', label = 'Timestamp', unit = 's')

        rga_data = RGAData(data.df, data.info_dict)
        return rga_data


    @staticmethod
    def __get_data_from_line__(line, indices, sep = ',', type = 'float'):
        """
        Obtains the value found at the columns indexed by the indices from a line
        Parameters
        ----------
        line:           str
                        The line from which to extract the data
        indices:        list of int
                        The indices of the value that will be extracted from line

        sep:            str, default: ','
                        Separator
        type:           str, default: 'float'
                        Type of data

        Returns
        -------
        values:         list
                        The values extracted from the line
        """
        line_split = line.split(sep)
        n = len(indices)
        values = [0]*n
        for i in range(0, n):
             temp = line_split[indices[i]].strip()
             if type == 'str':
                 values[i] = temp
             elif type == 'float':
                 values[i] = float(temp)
        return values
