import numpy as np
import pandas as pd
import os
import time
import datetime
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.dates import DateFormatter

from .Defaults import DEFAULT_TEMPERATURE_STRUCTURE, LABVIEW_TIMESTAMP_OFFSET
from . import Data

class StatusData(Data):
    """
    StatusData Class for SparkDC Data

    Parameters
    ----------
    df: pandas.core.frame.DataFrame
        The data frame.
        If the argument is not present, the data object is initialized with an empty dataframe
    info_dict: dict, optional
        Dictionary of labels, unit and concatenation_type for the data
        Example of info_dict: {'temp':       {'col': 0, 'label': 'Temperature',   'unit':   'K',   'concatenation_type': 'normal'},
        all_pulses': {'col': 1, 'label': 'All Pulses',    'unit':   '',    'concatenation_type': 'additive'}}

    """
    def __init__(self, *args):
        super().__init__(*args)


    @staticmethod
    def read_from_files(file_paths, header = None, delimiter = '\t', engine = 'c', skiprows = 0, info_dict = DEFAULT_TEMPERATURE_STRUCTURE):
        """
        Reads data from multiple files

        Parameters
        ----------
        file_paths:     str or list
                        The filepaths from where the data will be read
        header:         int, default: 0
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
        temp_data:      StatusData
                        StatusData object corresponding to the data read from the file_paths
        """
        data = Data.read_from_files(file_paths, header = header, delimiter = delimiter, engine = engine, skiprows = skiprows, info_dict = info_dict)
        temp_data = StatusData(data.df, info_dict)
        temp_data.df.loc[:, 'timestamp'] = (temp_data.df.loc[:, 'timestamp'] - LABVIEW_TIMESTAMP_OFFSET)
        return temp_data

    @staticmethod
    def read_from_folder_between_timestamps(folder_path, timestamp_limits, timezone = "Europe/Stockholm",\
     descending_search = True, header = None, delimiter = '\t', skiprows = 0, engine = 'c', info_dict = DEFAULT_TEMPERATURE_STRUCTURE):
        """
        Reads the status data between specified timestamps from folder

        Parameters
        ----------
        folder_path:        str
                            The path of the folder containing the CryoDC status data
        timestamp_limits:   list of double
                            Read the data between timestamp_limits[0] and timestamp_limits[1]
        timezone:           str, default: 'Europe/Stockholm'
                            The timezone corresponding to the datetime in the name of the files
        header:             int, default: None
                            Row number(s) containing column labels and marking the start of the data (zero-indexed).
        delimiter:          char, default: '\t'
                            The delimiter used in the file.
        info_dict:          dict, default: DEFAULT_TEMPERATURE_STRUCTURE
                            The info_dict of the file
        engine:             str, default: 'c'
                            Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine.
        skiprows:           int, default: 0
                            Skips the first N rows when reading the file

        Returns
        -------
        data:               StatusData
                            StatusData object corresponding to the data read from the file_paths
        """
        files = os.listdir(folder_path) # get all files from specified folder

        n_files = len(files)
        files.sort(reverse = descending_search) # sort files
        # print(files)
        tzinfo = ZoneInfo(timezone) # get time zone
        timestamps = np.empty([n_files]) # array of timestamps corresponding to filenames

        for i in range(0, n_files): # iterate through all file names
            file = files[i]
            time_string = file[7:-4] # remove the 'cryodc_' and '.dat' from the start and end of the filenames
            dt = datetime.datetime.strptime(time_string, "%Y%m%d-%H%M%S").replace(tzinfo=tzinfo)
            timestamp = time.mktime(dt.timetuple()) # get timestamp
            timestamps[i] = timestamp
            if descending_search and timestamp < timestamp_limits[0]: #if descending search, stop searching after we get past the lower limit of timestamps
                break
            if not descending_search and timestamp > timestamp_limits[1]: #if ascending search, stop searching after we get past the upper limit of timestamps
                break
        timestamps = timestamps[:i+1] # we do not check all files, cut array

        # get arguments where the timestamp of the file is in selected range
        valid_file_args = np.where(np.logical_and(timestamps <= timestamp_limits[1], timestamps >= timestamp_limits[0]))[0]

        # but it can happen that the timestamp of the file is not in range, while some data inside it is
        # for example, if timestamp[0] corresponds to 09:30:00 and the file starts at 09:00:00 and ends at 10:00:00 it will be excluded
        # to account for this, add to the list of files to read the first file bellow timestamp_limits[0] and we will remove the unecessary data later
        bool_condition = timestamps <= timestamp_limits[0]
        if descending_search:
            if any(bool_condition):
                min_arg = np.min(np.argwhere(bool_condition))
                valid_file_args = np.append(valid_file_args, min_arg)
        else:
            if any(bool_condition):
                max_arg = np.max(np.argwhere(bool_condition))
                valid_file_args = np.append(valid_file_args, max_arg)

        valid_file_args = np.unique(valid_file_args) #renove duplicates, this can happen when timestamp is exactly timestamp of file

        selected_files = (np.array(files)[valid_file_args]).tolist() # select the files to be read

        selected_files_full_path = [os.path.join(folder_path, file) for file in selected_files] #join path with folder
        selected_files_full_path.sort(reverse = False) # sort in ascending order
        status_data_full = StatusData.read_from_files(selected_files_full_path, header = header, delimiter = delimiter, engine = engine, \
         skiprows = skiprows, info_dict = info_dict) # read the files

        #finally, remove the data outside the required range
        status_data_full.remove_data_timestamp_range(timestamp_limits)
        return status_data_full


    @staticmethod
    def read_from_folder_between_datetimes(folder_path, datetime_limits, time_format = '%Y%m%d-%H%M%S', timezone = "Europe/Stockholm", \
    descending_search = True, header = None, delimiter = '\t', skiprows = 0, engine = 'c', info_dict = DEFAULT_TEMPERATURE_STRUCTURE):
        """
        Reads the status data between specified datetimes from folder

        Parameters
        ----------
        folder_path:        str
                            The path of the folder containing the CryoDC status data
        datetime_limits:    list of str
                            Read the data between datetime_limits[0] and datetime_limits[1]
        time_format:        str, default: '%Y%m%d-%H%M%S'
                            The time format string used to specify the datetime_limits
        timezone:           str, default: 'Europe/Stockholm'
                            The timezone corresponding to the datetime in the name of the files and to the datetimes in datetime_limits
        header:             int, default: None
                            Row number(s) containing column labels and marking the start of the data (zero-indexed).
        delimiter:          char, default: '\t'
                            The delimiter used in the file.
        info_dict:          dict, default: DEFAULT_TEMPERATURE_STRUCTURE
                            The info_dict of the file
        engine:             str, default: 'c'
                            Parser engine to use. The C and pyarrow engines are faster, while the python engine is currently more feature-complete. Multithreading is currently only supported by the pyarrow engine.
        skiprows:           int, default: 0
                            Skips the first N rows when reading the file

        Returns
        -------
        data:               StatusData
                            StatusData object corresponding to the data read from the file_paths
        """
        tzinfo = ZoneInfo(timezone)
        timestamp_limit_lower = time.mktime(datetime.datetime.strptime(datetime_limits[0], time_format).replace(tzinfo=tzinfo).timetuple())
        timestamp_limit_upper = time.mktime(datetime.datetime.strptime(datetime_limits[1], time_format).replace(tzinfo=tzinfo).timetuple())
        timestamp_limits = [timestamp_limit_lower, timestamp_limit_upper]
        return StatusData.read_from_folder_between_timestamps(folder_path, timestamp_limits, timezone = timezone, descending_search = descending_search, \
         header = header, delimiter = delimiter, skiprows = skiprows, engine = engine, info_dict = info_dict)
