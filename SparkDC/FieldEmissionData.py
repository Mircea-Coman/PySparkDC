import numpy as np
import pandas as pd

from .Defaults import DEFAULT_FE_STRUCTURE, LABVIEW_TIMESTAMP_OFFSET
from . import Data
from . import FancyPlot

class FieldEmissionData(Data):
    """
    FieldEmissionData Class for SparkDC Data

    Parameters
    ----------
    df:                                 pandas.core.frame.DataFrame
                                        The data frame.
                                        If the argument is not present, the data object is initialized with an empty dataframe
    info_dict:                          dict, optional
                                        Dictionary of labels, unit and concatenation_type for the data
                                        Example of info_dict: {
                                        'temp':       {'col': 0, 'label': 'Temperature',   'unit':   'K',   'concatenation_type': 'normal'},
                                        'all_pulses': {'col': 1, 'label': 'All Pulses',    'unit':   '',    'concatenation_type': 'additive'}}

    gap:                                double, default: 60
                                        The length of the gap between the electrodes in um
    current_limiting_resistor:          double, default: 0
                                        The value of the current limiting resistor used in the measurements.
    """

    def __init__(self, *args, gap = 60, current_limiting_resistor = 0):
        super().__init__(*args)
        self.gap = gap
        self.current_limiting_resistor = current_limiting_resistor
        self.calculate_derived_columns()

    def plot_IV(self, x_key = 'true_field', fplot = None, FN_plot = False, minI = 1E-3, figsize = (13, 8), ax_id = 0, marker = None, markersize = 5, \
    linestyle = '-', linewidth = 2, color = None, label = None, fontweight = 'normal', fontsize = 12):
        """
        Plots the selected columns from the pandas dataframe of the Data obejct

        Parameters
        ----------
        x_key:              ['true_field'|'true_voltage'], default: 'true_field'
                            The key corresponding to the column to be plotted on the x axis
        FN_plot:            bool, default: False
                            If True, plot in the Fowler-Nordheim format
        minI:               double, default: 1E-3
                            If FN_plot = True, the current bellow this value will not be plotted. Units: mA

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
        marker:             matplotlib marker, default: None
        markersize:         int, default: 5
        linestyle:          matplotlib linestyle, default: 'solid'
        linewidth:          int, default: 2
        color:              matplotlib color, default: None (a color is selected from the color cycle)
        label:              str, default: None
                            The labels of the Line2D plot.

        Returns
        -------
        fplot:  FancyPlot
                The FancyPlot on which the data was plotted
        """

        if fplot is None:
            fplot = FancyPlot(n_ax = 1, figsize = figsize, style_dict = None, fontweight = fontweight, fontsize = fontsize)

        if FN_plot:
            mask = self.df.current > minI
            fplot.set_axis_yscale(0, 'log')
            x = 1.0/self.df[x_key][mask]
            y = self.df.current[mask]
            scaling_x = 1000
            if x_key == 'true_field':
                xlabel = '1/E [nm/V]'
            elif x_key == 'true_voltage':
                xlabel = '1000/Voltage [1/V]'
            else:
                raise ValueError(f'Invalid x_key {x_key} in plot_IV()')
        else:
            x = self.df[x_key]
            y = self.df.current
            scaling_x = 1
            if x_key == 'true_field':
                xlabel = 'Eletric Field [MV/m]'
            elif x_key == 'true_voltage':
                xlabel = 'Voltage [V]'
            else:
                raise ValueError(f'Invalid x_key {x_key} in plot_IV()')

        fplot.plot(x, y, datetime_plot = False, ax_id = ax_id, marker = marker, markersize = markersize, \
        linestyle = linestyle, linewidth = linewidth, color = color, label = label, scaling_x = scaling_x, scaling_y = 1E3)
        fplot.set_xlabel(xlabel)
        fplot.set_axis_ylabel(0, 'Current [uA]')
        return fplot

    def calculate_derived_columns(self):
        """
        (Re)calculates the derived columns: 'field', 'true_voltage', 'true_field'
        """
        self.df['field'] = (self.df.voltage / self.gap)
        self.add_info_dict_entry('field', label = 'Electic Field', unit = 'MV/m')

        self.df['true_voltage'] = self.df.voltage - self.df.current * self.current_limiting_resistor * 1E-3
        self.add_info_dict_entry('true_voltage', label = 'Electic Field', unit = 'MV/m')

        self.df['true_field'] = (self.df.true_voltage / self.gap)
        self.add_info_dict_entry('true_field', label = 'Electic Field', unit = 'V')


    @staticmethod
    def read_from_files(file_paths, header = None, delimiter = '\t', engine = 'c', skiprows = 1, info_dict = DEFAULT_FE_STRUCTURE, \
        gap = 60, current_limiting_resistor = 0):
        """
        Reads data from multiple files

        Parameters
        ----------
        file_paths:     str or list
                        The filepaths from where the data will be read
        header:         int, default: None
                        Row number(s) containing column labels and marking the start of the data (zero-indexed).
        delimiter:      char, default: '\t'
                        The delimiter used in the file.
        info_dict:      dict, default: DEFAULT_FE_STRUCTURE
                        The info_dict of the file
        engine:         str, default: 'c'
                        Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine.
        skiprows:       int, default: 0
                        Skips the first N rows when reading the file
        gap:                                double, default: 60
                                            The length of the gap between the electrodes in um
        current_limiting_resistor:          double, default: 0
                                            The value of the current limiting resistor used in the measurements.

        Returns
        -------
        data:   FieldEmissionData
                FieldEmissionData object corresponding to the data read from the file_paths
        """
        data = Data.read_from_files(file_paths, header = header, delimiter = delimiter, engine = engine, skiprows = skiprows, info_dict = info_dict)
        data.df.loc[:, 'timestamp'] = (data.df.loc[:, 'timestamp'] - LABVIEW_TIMESTAMP_OFFSET)
        data.df.loc[:, 'voltage'] = data.df.voltage * 1000
        info_dict['voltage']['unit'] = 'V'
        FE_data = FieldEmissionData(data.df, info_dict, gap = gap, current_limiting_resistor = current_limiting_resistor)
        return FE_data
