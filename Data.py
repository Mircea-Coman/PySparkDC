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
        label_dict: dict, optional
            Dictionary of labels for each data column.
            If not present, it is creared from the structure argument
        unit_dict: dict, optional
            Dictionary of units for each data column.
            If not present, it is created from the structure argument
        concatenation_type_dict: dict, optional
            Dictionary of concatenation type for each data column. Valid values: normal, additive.
            If not present, it is creared from the structure argument

        structure: numpy.ndarray, optional
            The structure of the data. For each data field, the structure is the following: [column name, full label, unit, concatenation type]
            If label_dict, unit_dict, and concatenation_type_dict are present, this argument is ignored
        """
        self.df = df
        self.info_dict = info_dict


    # def __getattr__(self, key):
    #     if key in self.df.keys():
    #         return self.df[key]
    #     else:
    #         raise AttributeError(f"'Data' object has no attribute '{key}'")


    def __create_dictionaries__(self, structure):
        """
        Creates the dictionaries from the structure array
        Parameters
        ----------
        structure: numpy.ndarray
            The structure of the data. For each data field, the structure is the following: [key, full label, unit, concatenation type]

        Returns
        -------
        label_dict: dict
            Dictionary of labels for each data column.
        unit_dict: dict
            Dictionary of units for each data column.
        concatenation_type_dict: dict
            Dictionary of concatenation type for each data column. Valid values: normal, additive.
        """

        unit_dictionary = {}
        label_dictionary = {}
        concatenation_type_dictionary = {}
        for i in np.arange(structure.shape[0]):
            key = structure[i, 0]
            label = structure[i, 1]
            unit = structure[i, 2]
            concatenation_type = structure[i, 3]
            label_dictionary[key] = label
            unit_dictionary[key] = unit
            concatenation_type_dictionary[key] = concatenation_type
        return label_dictionary, unit_dictionary, concatenation_type_dictionary

    @property
    def file_separators(self):
        """
        Returns a numpy array of size n_files * 2.

        Returns
        -------
        file_separators: numpy.ndarray
                         file_separators[i, 0] - the index corresponding to the start of data for each file
                         file_separators[i, 1] - the index corresponding to the end of data for each file
                         Warning: Data from a file is contained until file_separators[i, 1] - 1. It is done like this in order to be able to select data like df[start:end]
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
    labels = None, fontsize = 12, fontweight = 'normal', use_style_dict = True, style_dict = DEFAULT_STYLE, scaling_y = 1):
        """
        Plot the data at the selected key. The function returns the matplotlib.axes on which it was ploted

        Parameters
        ----------
        key:                str
                            The key corresponding to the column to be plotted on the y axis

        x_key:              str, default: 'timestamp'
                            The key corresponding to the column to be plotted on the x axis.
        datetime_plot:      boolean, default: True
                            Plots formatted datetimes on x axis if x_key is 'timestamp'
        date_format:        boolean, default: '%m-%d %H:%M:%S'
                            Format used to format the datetimes
        timezone:           str, default: 'Europe/Stockholm'
                            Timezone used to format the datetimes
        ax:                 {None, matplotlib.axes}, default: None
                            The matplotlib axes on which to plot. If None, a new figure is created
        marker:             marker style string, default: None
        linestyle:          {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}, default: '-'
        color:              default: 'k'
        label:              str, default: None
                            The label of the plot
        scaling_factor_y:   float, default: 1.0
                            The value plotted on the y axis will be multiplied by this number

        Returns
        -------
        ax: matplotlib.axes
            The matplotlib axes on which the data was plotted
        """
        if fplot is None:
            fplot = FancyPlot(n_ax = Utils.dim(keys)[0], figsize = figsize, style_dict = DEFAULT_STYLE, fontweight = fontweight, fontsize = fontsize)
        fplot.plot_data(self, keys,  x_key = x_key, datetime_plot = datetime_plot, date_format = date_format, timezone = timezone, \
                ax_id = ax_id, marker = marker, markersize = markersize, linestyle = linestyle, linewidth = linewidth, color = color, labels = labels, \
                use_style_dict = use_style_dict, scaling_y = scaling_y)
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
        file_paths:     list
                        The filepaths from where the data will be read
        header:         int, default: 0
                        Row number(s) containing column labels and marking the start of the data (zero-indexed).
        delimiter:      char, default: '\t'
                        The delimiter used in the file.
        structure:      numpy array, optional
                        The structure of the data. For each data field, the structure is the following: [column name, full label, unit, concatenation type]
        engine:         str, default: 'c'
                        Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine.
        skip_rows:      int, default: 0
                        Skips the first N rows when reading the file
        Returns
        -------
        data:   Data
                Data object corresponding to the data read from the file_paths
        """
        Data.__check_and_fill_info_dict__(info_dict)
        dfs = []
        n_files = len(file_paths)
        i = 0
        prev_file_end_index = 0
        for file_path in file_paths:
            keys = np.array(Utils.get_keys_info_dict(info_dict))
            used_cols = np.array(Utils.get_from_info_dict(info_dict, 'col'))

            full_df = pd.read_csv(file_path, engine = engine, index_col=False, header = header, skiprows = skiprows, delimiter = delimiter)

            mask = np.array(used_cols)<full_df.shape[1]
            new_df = full_df.iloc[:, used_cols[mask]]
            new_df.columns = keys[mask]

            additive_columns = Utils.get_concatenation_type_columns(info_dict, 'additive')

            if i != 0 and additive_columns is not []:
                last_values_additive_columns = dfs[i-1][additive_columns].iloc[-1]
                new_df[additive_columns] += last_values_additive_columns
            col_len = new_df.shape[1]
            new_df.insert(col_len, "file", file_path, True)
            new_df.insert(col_len+1, "file_id", i, True)

            dfs.append(new_df)
            n_points = new_df.shape[0]
            prev_file_end_index = prev_file_end_index + n_points
            i += 1
        df = pd.concat(dfs, axis=0, ignore_index=True)

        return Data(df, info_dict)

    @staticmethod
    def __check_and_fill_info_dict__(info_dict):
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
