import numpy as np
import pandas as pd
import os
import time
import datetime
from zoneinfo import ZoneInfo
from default_file_structures import DEFAULT_TEMPERATURE_STRUCTURE, DEFAULT_TEMPERATURE_STYLES, LABVIEW_TIMESTAMP_OFFSET
from Data import Data

class StatusData(Data):
    def __init__(self, *args, structure = DEFAULT_TEMPERATURE_STRUCTURE):
        super().__init__(*args, structure = structure)

    @staticmethod
    def read_from_files(file_paths, header = 0, delimiter = '\t', structure = DEFAULT_TEMPERATURE_STRUCTURE):
        data = Data.read_from_files(file_paths, header = header, delimiter = delimiter, structure = DEFAULT_TEMPERATURE_STRUCTURE)
        temp_data = StatusData(data.df, data.label_dict, data.unit_dict, data.concatenation_type_dict)
        return data

    @staticmethod
    def read_from_folder_between_timestamps(folder_path, timestamp_limits, timezone = "Europe/Stockholm", descending_search = True, header = 0, delimiter = '\t', structure = DEFAULT_TEMPERATURE_STRUCTURE):
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
        status_data_full = StatusData.read_from_files(selected_files_full_path, header = header, delimiter = delimiter, structure = structure) # read the files

        #finally, remove the data outside the required range
        status_data_full.df = status_data_full.df[status_data_full.df['timestamp'].between(timestamp_limits[0] + LABVIEW_TIMESTAMP_OFFSET, timestamp_limits[1] + LABVIEW_TIMESTAMP_OFFSET)]
        return status_data_full


    @staticmethod
    def read_from_folder_between_datetimes(folder_path, datetime_limits, time_format = '%Y%m%d-%H%M%S', timezone = "Europe/Stockholm", descending_search = True, header = 0, delimiter = '\t', structure = DEFAULT_TEMPERATURE_STRUCTURE):
        tzinfo = ZoneInfo(timezone)
        timestamp_limit_lower = time.mktime(datetime.datetime.strptime(datetime_limits[0], time_format).replace(tzinfo=tzinfo).timetuple())
        timestamp_limit_upper = time.mktime(datetime.datetime.strptime(datetime_limits[1], time_format).replace(tzinfo=tzinfo).timetuple())
        timestamp_limits = [timestamp_limit_lower, timestamp_limit_upper]
        print(timestamp_limits)
        return StatusData.read_from_folder_between_timestamps(folder_path, timestamp_limits, timezone = timezone, descending_search = descending_search, header = header, delimiter = delimiter, structure = structure)