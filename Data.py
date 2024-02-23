import numpy as np
from DataField import DataField
import copy

class Data:

    def __init__(self, data_dict):
        self.data_dict = data_dict

    def __getattr__(self, key):
        if key in self.data_dict:
            return self.data_dict[key]
        else:
            raise AttributeError(f"'Data' object has no attribute '{key}'")


    @staticmethod
    def create_empty(index_dictionary):
        data_dictionary = {}
        for key in index_dictionary:
            index = index_dictionary[key][0]
            name = index_dictionary[key][1]
            unit = index_dictionary[key][2]
            concatenation_type  = index_dictionary[key][3]
            data_dictionary[key] = DataField(np.array([]), name, unit, concatenation_type = concatenation_type)
        return Data(data_dictionary)


    @staticmethod
    def read_from_files(index_dictionary, file_paths, skiprows = 0):
        joined_data = Data.create_empty(index_dictionary)
        for file_path in file_paths:
            data = Data.read_from_file(index_dictionary, file_path, skiprows = skiprows)
            joined_data = Data.concatenate(joined_data, data)
        return joined_data


    @staticmethod
    def read_from_file(index_dictionary, file_path, skiprows = 0):
        data_dictionary = {}
        raw_data = np.loadtxt(file_path, skiprows=skiprows)
        for key in index_dictionary:
            index = index_dictionary[key][0]
            name = index_dictionary[key][1]
            unit = index_dictionary[key][2]
            concatenation_type  = index_dictionary[key][3]
            data_dictionary[key] = DataField(raw_data[:, index], name, unit, concatenation_type = concatenation_type)
        return Data(data_dictionary)

    @staticmethod
    def concatenate(data_1, data_2, deep_copy_first = False):
        if deep_copy_first:
            data_joined = copy.deepcopy(data_1)
        else:
            data_joined = data_1

        for key in data_joined.data_dict:
            data_joined.data_dict[key] = DataField.concatenate(data_joined.data_dict[key], data_2.data_dict[key])
        return data_joined
