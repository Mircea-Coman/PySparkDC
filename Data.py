import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from dateutil import tz
from zoneinfo import ZoneInfo
import time
import datetime

from default_file_structures import DEFAULT_TEMPERATURE_STRUCTURE, DEFAULT_TEMPERATURE_STYLES, LABVIEW_TIMESTAMP_OFFSET

class Data:

    def __init__(self, *args, structure = DEFAULT_TEMPERATURE_STRUCTURE):
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
        if len(args) == 0:
            self.label_dict, self.unit_dict, self.concatenation_type_dict = self.__create_dictionaries__(structure)
            self.df =  pd.DataFrame(columns = structure[:, 0])
        elif len(args) == 1:
            self.df = args[0]
            self.label_dict, self.unit_dict, self.concatenation_type_dict = self.__create_dictionaries__(structure)
        elif len(args) == 4:
            self.df = args[0]
            self.label_dict = args[1]
            self.unit_dict = args[2]
            self.concatenation_type_dict =  args[3]

        else:
            raise ValueError("Invalid number of arguments")


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
            file_separators[j, 1] = end + 1 #add one to be able to select data like df[start:end]
        return file_separators

    def plot(self, key, x_key = 'timestamp', plot_datetime = True, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', \
    ax = None, marker = None, linestyle = '-', color = 'k', label = None, scaling_factor_y = 1):
        """
        Plot the data at the selected key. The function returns the matplotlib.axes on which it was ploted

        Parameters
        ----------
        key:                str
                            The key corresponding to the column to be plotted on the y axis

        x_key:              str, default: 'timestamp'
                            The key corresponding to the column to be plotted on the x axis.
        plot_datetime:      boolean, default: True
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
        if ax is None:
            fig, ax = plt.subplots(figsize = (13, 8)) # make the plot if no axes

        # fix gaps between data corresponding to different files. A NaN value is added at the end of the data corresponding to each file.
            # Otherwise, in the plot, a line will brige the gap between the data corresponding to different neighbouring files
        x_data = self.__fix_gaps_between_files__(x_key)
        y_data = self.__fix_gaps_between_files__(key, add_nan = True)

        if plot_datetime and x_key == 'timestamp':
            date_formatter = DateFormatter(date_format, tz=tz.gettz(timezone))
            ax.xaxis.set_major_formatter(date_formatter)
            plt.subplots_adjust(hspace=0, bottom=0.2)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=70 )

            new_x = mdates.epoch2num(x_data)
            ax.plot_date(new_x,  y_data * scaling_factor_y, fmt = color, marker = marker, linestyle = linestyle, label = label)
        else:
            ax.plot(x_data,  y_data * scaling_factor_y, color = color, marker = marker, linestyle = linestyle, label = label)
        return ax

    def __fix_gaps_between_files__(self, key, add_nan = True):
        """
        Fixes the data for plotting. It adds n-1 data points in between data corresponding to different files. If add_nan it adds a nan, otherwise it copies the previous data.

        Parameters
        ----------
        key:                str
                            The key corresponding to the column to be plotted on the y axis

        add_nan:            bool, default: True
                            If True, add a NaN value at the end of the data corresponding to each file. Otherwise, copy the previous value
        Returns
        -------
        new_x:              numpy.ndarray
                            The fixed array
        """
        file_separators = self.file_separators
        n_files = file_separators.shape[0]
        x = self.df[key].to_numpy()
        new_x = np.zeros([x.shape[0] + n_files - 1])
        for i in range(0, n_files):
            start = file_separators[i, 0]
            end = file_separators[i, 1]
            new_x[start+i:end+i] = x[start:end].flatten()
            if i != n_files - 1:
                if add_nan:
                    new_x[end+i] = np.NAN
                else:
                    new_x[end+i] = x[end-1]
        return new_x


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

        if key in self.label_dict:
            return self.label_dict[key]
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

        if key in self.unit_dict:
            return self.unit_dict[key]
        else:
            raise AttributeError(f"'{key}' is not a valid data field!")


    @staticmethod
    def read_from_files(file_paths, header = None, delimiter = '\t', engine = 'c', skiprows = 0, structure = DEFAULT_TEMPERATURE_STRUCTURE):
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
        dfs = []
        n_files = len(file_paths)
        i = 0
        prev_file_end_index = 0
        for file_path in file_paths:
            new_df = pd.read_csv(file_path, engine = engine,  index_col=False, header = header, skiprows = skiprows, delimiter = delimiter, names = structure[:, 0])
            additive_columns = np.where(structure[:, -1] == 'additive')[0]
            if i != 0:
                last_values_additive_columns = dfs[i-1].iloc[-1, additive_columns]
                new_df.iloc[:, additive_columns] += last_values_additive_columns
            col_len = new_df.shape[1]
            new_df.insert(col_len, "file", file_path, True)
            new_df.insert(col_len+1, "file_id", i, True)

            dfs.append(new_df)
            n_points = new_df.shape[0]
            prev_file_end_index = prev_file_end_index + n_points
            i += 1
        df = pd.concat(dfs, axis=0, ignore_index=True)
        return Data(df, structure = structure)
