from Data import Data
from default_file_structures import DEFAULT_CONDITIONING_STRUCTURE, DEFAULT_STYLE, LABVIEW_TIMESTAMP_OFFSET
import os
import glob
import pandas as pd
import Utils
import numpy as np

DEFAULT_FILENAME = 'Marx_data.txt' # the filename containing the data from the Marx generator

INVALID_RUN_INDEX = -99999

class ConditioningData(Data):
    def __init__(self, *args, electrode_name = ''):
        """
        Initializer for the ConditioningData Class
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

        electrode_name: str, default: ''
                             The name of the electrode
        """
        self.electrode_name = electrode_name
        super().__init__(*args)
        self.calculate_derived_columns()

    def calculate_derived_columns(self):
        """
        (Re)calculates the derived columns: 'target_field' and 'field'
        """
        self.df['target_field'] = (self.df['target_voltage'] / self.df['gap'])
        self.add_info_dict_entry('target_field', label = 'Target Field', unit = 'MV/m')

        self.df['field'] = (self.df['output_voltage'] / self.df['gap'])
        self.add_info_dict_entry('field', label = 'Electric Field', unit = 'MV/m')

    def get_run_separators(self, run_id, key = 'run_id'):
        """
        Get the indices corresponding to the start and end of each run. Returns a numpy array of size len(run_id) * 2.

        Parameters
        ----------
        run_id:     int or list of int

        Returns
        -------
        file_separators: int or numpy.ndarray
                         file_separators[i, 0] - the index corresponding to the start of data for each run
                         file_separators[i, 1] - the index corresponding to the end of data for each run
                         Warning: if the run_id is not found, ConditioningData.INVALID_RUN_INDEX is returned as the index
        """

        # check the run_id and convert it to list if it is not already
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
            else: # if run not found
                run_separators[j, 0] = ConditioningData.INVALID_RUN_INDEX
                run_separators[j, 1] = ConditioningData.INVALID_RUN_INDEX

        if len(dim) == 0:
            return run_separators[0]
        else:
            return run_separators


    def plot_standard(self, first_axis = 'field', second_axis = 'BDs', third_axis = 'BDR', plot_third_axis = False, log_third_axis = True,\
        figsize = (20, 8), fontsize = 15, fontweight = 'normal', marker = None, markersize = 5, linestyle = '-', linewidth = 2, stripe = True,\
        color_runs = None, style_dict = DEFAULT_STYLE, use_style_dict = True):
        """
        Make the standard plot for conditioning

        Parameters
        ----------
        first_axis:         ['voltage'|'target_voltage'|'field'|'target_field'], default: 'field'
                             The key corresponding to the column to be plotted on the first axis.
        second_axis:        str, default: 'BDs'
                             The key corresponding to the column to be plotted on the second axis.
        third_axis:         str, default: 'BDR'
                             The key corresponding to the column to be plotted on the third axis.
        plot_third_axis:    bool, default: False
        log_third_axis:     bool, default: True

        figsize:            tuple, default: (13, 8)
                             The size of the figure in inches. Used only when fplot is None
        fontsize:           int, default: 12
                             Dictionary of units for each data column.
                             If not present, it is created from the structure argument
        fontweight:         ['normal'|'bold'|'heavy'|'light'|'ultrabold'|'ultralight'], default: 'normal'
        marker:             matplotlib marker, default: None
        markersize:         int, default: 5
        linestyle:          matplotlib linestyle, default: 'solid'
        linewidth:          int, default: 2
        stripe:             bool, default: True
                             Make the axvspans corresponding to the files
        color_runs:         list of dict, default: None
                             Make axvspans for the selected runs. Example: [{'color': (1, 0, 0, 0.2), 'run': [1,3]}, {'color': (0, 1, 0, 0.2), 'run': 2}]
        style_dict:         dict,   default: DEFAULT_STYLE
                             The style dictionary used
        use_style_dict:     bool,   default: True
                             If true, the proprieties of the plot will be derived from the provided style_dict

        Returns
        -------
        fplot:  FancyPlot
                The FancyPlot on which the data was plotted
        """
        if plot_third_axis:
            list = [[first_axis], [second_axis], [third_axis]]
        else:
            list = [[first_axis], [second_axis]]

        fplot = self.plot(list, x_key = 'all_pulses', figsize = figsize, fontsize = fontsize, fontweight = fontweight)
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
            fplot.set_axis_ylim(2, [1E-8, 1E-3]) #set the limit for the BDR

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
        """
        Reads data from multiple files
        Parameters
        ----------
        file_paths:     str or list
                        The filepaths from where the data will be read
        header:         int, default: None
                        Row number(s) containing column labels and marking the start of the data (zero-indexed).
        delimiter:      char, default: '\s+'
                        The delimiter used in the file.
        info_dict:      dict, default: DEFAULT_CONDITIONING_STRUCTURE
                        The info_dict of the file
        engine:         str, default: 'python'
                        Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine.
        skiprows:       int, default: 1
                        Skips the first N rows when reading the file
        electrode_name: str, default: ''
                             The name of the electrode
        Returns
        -------
        cond_data:      ConditioningData
                        ConditioningData object corresponding to the data read from the file_paths
        """
        data = Data.read_from_files(file_paths, header = header, delimiter = delimiter, engine = engine, skiprows = skiprows, info_dict = DEFAULT_CONDITIONING_STRUCTURE)
        cond_data = ConditioningData(data.df, data.info_dict, electrode_name = electrode_name)
        return cond_data

    @staticmethod
    def read_runs(data_folder, electrode, runs, header = None, delimiter = '\s+', skiprows = 1, engine ='python', info_dict = DEFAULT_CONDITIONING_STRUCTURE):
        """
        Reads the selected runs from the conditiong data folder
        Parameters
        ----------
        data_folder:    str
                        The path corresponding to the folder containing the conditioning data
        electrode:      str
                        The id of the electrode
        runs:           list of int
                        The run numbers to be read
        delimiter:      char, default: '\s+'
                        The delimiter used in the file.
        info_dict:      dict, default: DEFAULT_CONDITIONING_STRUCTURE
                        The info_dict of the file
        engine:         str, default: 'python'
                        Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine.
        skiprows:       int, default: 1
                        Skips the first N rows when reading the file
        electrode_name: str, default: ''
                             The name of the electrode
        Returns
        -------
        cond_data:      ConditioningData
                        ConditioningData object
        """
        electrode_path = os.path.join(data_folder, electrode)
        files_to_read = []
        for current_run in runs:
            run_path = glob.glob(f"{electrode_path}/*{electrode}*{current_run:03d}")[0] # make the path of the folder containing the .txt file
            file_path = os.path.join(run_path, DEFAULT_FILENAME)
            files_to_read.append(file_path)
        cond_data = ConditioningData.read_from_files(files_to_read, header = header, delimiter = delimiter, skiprows = skiprows, \
        engine = engine, info_dict = info_dict, electrode_name = electrode)
        col_len = cond_data.df.shape[1]

        #make the run_id column, which shows the run number
        cond_data.df.insert(col_len, "run_id", runs[pd.Series.to_numpy(cond_data.df.file_id)], True)
        return cond_data
