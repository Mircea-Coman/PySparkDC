import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from dateutil import tz
from zoneinfo import ZoneInfo
import time
import datetime

import Utils
from FancyPlot import FancyPlot
from default_file_structures import DEFAULT_TEMPERATURE_STRUCTURE, DEFAULT_STYLE

class Data:

    def __init__(self, df, info_dict):
        """
        Initializer for the Data Class
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
        self.df = df
        self.info_dict = info_dict


    # def __getattr__(self, key):
    #     if key in self.df.keys():
    #         return self.df[key]
    #     else:
    #         raise AttributeError(f"'Data' object has no attribute '{key}'")


    @property
    def file_separators(self):
        """
        Get the indices corresponding to the start and end of each run. Returns a numpy array of size n_files * 2.

        Returns
        -------
        file_separators: numpy.ndarray
                         file_separators[i, 0] - the index corresponding to the start of data for each file
                         file_separators[i, 1] - the index corresponding to the end of data for each file
        """
        files = self.df.file.unique()
        n_files = len(files)
        file_separators = np.empty([n_files, 2], dtype = int)
        for j in range(0, n_files):
            mask = self.df.file == files[j]
            start = np.min(np.argwhere(mask))
            end = np.max(np.argwhere(mask))
            # if end < start: # check if there is somehow no columns comming from the file
            #     end = start
            file_separators[j, 0] = start
            file_separators[j, 1] = end
        return file_separators

    def plot(self, keys, x_key = 'timestamp', datetime_plot = True, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', \
    fplot = None, ax_id = None, figsize = (13, 8), marker = None, markersize = 5, linestyle = '-', linewidth = 2, color = None, \
    labels = None, fontsize = 12, fontweight = 'normal', use_style_dict = True, style_dict = DEFAULT_STYLE, scaling_x = 1, scaling_y = 1):
        """
        Plots the selected columns from the pandas dataframe of the Data obejct

        Parameters
        ----------
        key:                str, list of str or list of list of str
                            The keys corresponding to the columns to be plotted on the y axis.
                            If str: The data corresponding to the key will be plotted on an axis, corresponding to ax_id
                            If list of str: The data corresponding to all keys will be plotted on a single axis, corresponding to ax_id
                            if list of list of str: The data corresponding to the keys from each sublist will be plotted on different axes, corresponding to ax_id

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
        use_style_dict:     bool,   default: True
                            If true, the proprieties of the plot will be derived from the provided style_dict

        Returns
        -------
        fplot:  FancyPlot
                The FancyPlot on which the data was plotted
        """
        if len(Utils.dim(keys)) == 0:
            n_ax = 0
        else:
            n_ax = Utils.dim(keys)[0]
        if fplot is None:
            fplot = FancyPlot(n_ax = n_ax, figsize = figsize, style_dict = DEFAULT_STYLE, fontweight = fontweight, fontsize = fontsize)
        fplot.plot_data(self, keys,  x_key = x_key, datetime_plot = datetime_plot, date_format = date_format, timezone = timezone, \
                ax_id = ax_id, marker = marker, markersize = markersize, linestyle = linestyle, linewidth = linewidth, color = color, labels = labels, \
                use_style_dict = use_style_dict, scaling_x = scaling_x, scaling_y = scaling_y)
        return fplot




    def remove_data_timestamp_range(self, timestamp_limits):
        """
        Removes data outside the inclusive range timestamp_limits[0], timestamp_limits[1]

        Parameters
        ----------
        timestamp_limits:   {numpy.ndarray, list}
                            The timestamp limits
        """
        self.df = self.df[self.df['timestamp'].between(timestamp_limits[0], timestamp_limits[1])]

    def remove_data_datetime_range(self, datetime_limits, time_format = '%Y%m%d-%H%M%S', timezone = "Europe/Stockholm"):
        """
        Removes data outside the inclusive range datetime_limits[0], datetime_limits[1]

        Parameters
        ----------
        datetime_limits:    {numpy.ndarray, list}
                            The datetime limits

        time_format:        str, default: '%Y%m%d-%H%M%S'
                            The time format used in the datetime limits
        timezone:           str, default: "Europe/Stockholm"
                            The time format used in the datetime limits
        """

        tzinfo = ZoneInfo(timezone)
        timestamp_limit_lower = time.mktime(datetime.datetime.strptime(datetime_limits[0], time_format).replace(tzinfo=tzinfo).timetuple())
        timestamp_limit_upper = time.mktime(datetime.datetime.strptime(datetime_limits[1], time_format).replace(tzinfo=tzinfo).timetuple())
        self.remove_data_timestamp_range([timestamp_limit_lower, timestamp_limit_upper])

    def get_label_of(self, key):
        """
        Returns the full label for a specified key
        Parameters
        ----------
        key:    string
                Key of data column
        Returns
        -------
        label:  string
                The label for a given key
        """

        if key in self.info_dict:
            return self.info_dict[key]['label']
        else:
            raise AttributeError(f"'{key}' is not a valid data field!")

    def get_unit_of(self, key):
        """
        Returns the unit for a specified key
        Parameters
        ----------
        key:    string
                Key of data column
        Returns
        -------
        unit:  string
                The unit for a given key
        """

        if key in self.info_dict:
            return self.info_dict[key]['unit']
        else:
            raise AttributeError(f"'{key}' is not a valid data field!")

    def add_info_dict_entry(self, key, col = -1, label = '', unit = '', concatenation_type = 'normal'):
        subdict = {'col': col, 'label': label, 'unit': unit, 'concatenation_type': concatenation_type}
        self.info_dict[key] = subdict

    @staticmethod
    def read_from_files(file_paths, header = None, delimiter = '\t', engine = 'c', skiprows = 0, info_dict = DEFAULT_TEMPERATURE_STRUCTURE):
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
        info_dict:      dict, optional
                        The info_dict of the file
        engine:         str, default: 'c'
                        Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine.
        skiprows:       int, default: 0
                        Skips the first N rows when reading the file
        Returns
        -------
        data:   Data
                Data object corresponding to the data read from the file_paths
        """
        Data.__check_and_fill_info_dict__(info_dict)

        dfs = [] # create list of dataframes, corresponding to each file

        # if filepaths is just a str, convert to list: [file_paths]
        dim_file_paths = Utils.dim(file_paths)
        if(len(dim_file_paths)) == 0:
            file_paths = [file_paths]

        n_files = len(file_paths)
        i = 0
        prev_file_end_index = 0
        for file_path in file_paths:
            keys = np.array(Utils.get_keys_info_dict(info_dict)) #get the keys from the info_dict
            used_cols = np.array(Utils.get_from_info_dict(info_dict, 'col'))  # get the columns from the info_dict

            # read all the columns
            full_df = pd.read_csv(file_path, engine = engine, index_col=False, header = header, skiprows = skiprows, delimiter = delimiter)

            #   filter and use only the columns from the info_dict
            mask = np.array(used_cols)<full_df.shape[1]
            new_df = full_df.iloc[:, used_cols[mask]]
            new_df.columns = keys[mask]

            # get the additive columns
            additive_columns = Utils.get_concatenation_type_columns(info_dict, 'additive')

            # process the additive columns
            if i != 0 and additive_columns is not []:
                last_values_additive_columns = dfs[i-1][additive_columns].iloc[-1] #the value in the previous file
                new_df[additive_columns] += last_values_additive_columns    #add it to the data from the current file

            # add at the end new columns corresponding to the filename and the number of the file
            col_len = new_df.shape[1]
            new_df.insert(col_len, "file", file_path, True)
            new_df.insert(col_len+1, "file_id", i, True)

            dfs.append(new_df)
            n_points = new_df.shape[0]
            prev_file_end_index = prev_file_end_index + n_points
            i += 1
        df = pd.concat(dfs, axis=0, ignore_index=True) # concatenate the data frames

        return Data(df, info_dict)

    @staticmethod
    def __check_and_fill_info_dict__(info_dict):
        """
        Completes the info_dict, if labels, units or concatenation_type are not available
        Defaults: {label: '', unit: '', concatenation_type: 'normal'}

        Parameters
        ----------
        info_dict:      dict
                        The info_dict of the file
        """
        for item in info_dict.items():
            key = item[0]
            subdict = item[1]
            if 'col' not in subdict:
                raise ValueError(f"'col' not found in info_dict at key {key}")
            if 'label' not in subdict:
                subdict['label'] = ''
            if 'unit' not in subdict:
                subdict['unit'] = ''
            if 'concatenation_type' not in subdict:
                subdict['concatenation_type'] = 'normal'
