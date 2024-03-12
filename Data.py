import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from dateutil import tz
from default_file_structures import DEFAULT_TEMPERATURE_STRUCTURE, DEFAULT_TEMPERATURE_STYLES, LABVIEW_TIMESTAMP_OFFSET

class Data:

    def __init__(self, *args, structure = DEFAULT_TEMPERATURE_STRUCTURE):
        """
        Initializer for the Data Class
        Parameters
        ----------
        df: pandas.core.frame.DataFrame
            The main data.
            If the argument is not present, the data object is initialized with an empty dataframe
        label_dict: dict
            Dictionary of labels for each data column.
            If not present, it is creared from the structure argument
        unit_dict: dict
            Dictionary of units for each data column.
            If not present, it is creared from the structure argument
        concatenation_type_dict: dict
            Dictionary of concatenation type for each data column. Valid values: normal, additive.
            If not present, it is creared from the structure argument

        structure: numpy.ndarray, optional
            The structure of the data. For each data field, the structure is the following: [column name, full label, unit, concatenation type]
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
            If not present, it is creared from the structure argument
        unit_dict: dict
            Dictionary of units for each data column.
            If not present, it is creared from the structure argument
        concatenation_type_dict: dict
            Dictionary of concatenation type for each data column. Valid values: normal, additive.
            If not present, it is creared from the structure argument
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
                         file_separators[i, 0] - the index corresponding to the start of data from a specified file
                         file_separators[i, 1] - the index corresponding to the end of data from a specified file
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

    def plot(self, keys, x_data = 'timestamp', plot_datetime = True, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', style_dict = DEFAULT_TEMPERATURE_STYLES):
        file_separators = self.file_separators
        n_files = file_separators.shape[0]
        n_keys = len(keys)

        #get colors
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        colors = []
        linestyles = []
        k = 0
        for i in range(0, n_keys):
            if keys[i] in style_dict: # if the style of the key is specified in style_dict
                colors.append(style_dict[keys[i]][0])
                linestyles.append(style_dict[keys[i]][1])
            else: # otherwise, use the next color from the color cycle
                colors.append(color_cycle[k])
                linestyles.append('dashed')
                k += 1

        #make the plot
        fig, ax = plt.subplots(figsize = (13, 8))
        for i in range(0, n_keys):
            for j in range(0, n_files):
                start = file_separators[j, 0]
                end = file_separators[j, 1]
                if plot_datetime and x_data == 'timestamp':
                    date_formatter = DateFormatter(date_format, tz=tz.gettz(timezone))
                    ax.xaxis.set_major_formatter(date_formatter)
                    plt.subplots_adjust(hspace=0, bottom=0.2)
                    plt.setp( ax.xaxis.get_majorticklabels(), rotation=70 )

                    new_x = mdates.epoch2num(self.df[x_data].iloc[start:end] - LABVIEW_TIMESTAMP_OFFSET)
                    ax.plot_date(new_x,  self.df[keys[i]].iloc[start:end], label = self.label_dict[keys[i]], marker = None, fmt = colors[i], linestyle = linestyles[i])
                else:
                    ax.plot(self.df[x_data].iloc[start:end],  self.df[keys[i]].iloc[start:end], label = self.label_dict[keys[i]], color = colors[i], linestyle = linestyles[i])

        # make legend
        legend_lines = [Line2D([0], [0], color=colors[i], linewidth=1, linestyle=linestyles[i]) for i in range(0, n_keys)]
        legend_labels = [self.label_dict[keys[i]] for i in range(0, n_keys)]
        ax.legend(legend_lines, legend_labels)
        return fig, ax


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
        header:         int, optional
                        The number of header rows in the file. Default: 0
        delimiter:      char, optional
                        The delimiter used in the file. Default: '\t'
        structure:      numpy array, optional
                        The structure of the data. For each data field, the structure is the following: [column name, full label, unit, concatenation type]
        engine:         str, optional
                        Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine. Default: c

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
