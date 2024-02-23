import numpy as np
import pandas as pd

class Data:

    def __init__(self, *args):
        if len(args) == 0:
            self.label_dict = {}
            self.unit_dict = {}
            self.concatenation_type_dict = {}
            self.df =  pd.DataFrame()

        elif len(args) == 1:
            structure = args[0]
            self.label_dict, self.unit_dict, self.concatenation_type_dict = self.__create_dictionaries__(structure)
            self.df =  pd.DataFrame(columns = value_structure[:, 0])
        elif len(args) == 2:
            structure = args[0]
            self.df = args[1]
            self.label_dict, self.unit_dict, self.concatenation_type_dict = self.__create_dictionaries__(structure)
        elif len(args) == 4:
            self.label_dict = args[0]
            self.unit_dict = args[1]
            self.concatenation_type_dict =  args[2]
            self.df = args[3]

        else:
            raise ValueError("Invalid number of arguments")


    def __getattr__(self, key):
        if key in self.df.keys():
            return self.df[key]
        else:
            raise AttributeError(f"'Data' object has no attribute '{key}'")


    def __create_dictionaries__(self, structure):
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

    def get_label_of(self, key):
        if key in self.label_dict:
            return self.label_dict[key]
        else:
            raise AttributeError(f"'{key}' is not a valid data field!")

    def get_unit_of(self, key):
        if key in self.unit_dict:
            return self.unit_dict[key]
        else:
            raise AttributeError(f"'{key}' is not a valid data field!")


    @staticmethod
    def read_from_files(structure, file_paths, header = 0, delimiter = '\t'):
        dfs = []
        for file_path in file_paths:
            dfs.append(pd.read_csv(file_path, delimiter=delimiter, names = structure[:, 0]))
        df = pd.concat(dfs, axis=0, ignore_index=True)
        return Data(structure, df)


    @staticmethod
    def read_from_file(index_dictionary, file_path, skiprows = 0):
        pd_data = pd.read_csv(file_path, delimiter=delimiter, names = structure[:, 0])
        return Data(structure, pd_data)

    @staticmethod
    def concatenate(data_1, data_2):
        new_df = pd.concat([data_1.df, data_2.df], axis=0, ignore_index=True)
        return Data(new_df, data_1.label_dict, data_1.unit_dict, data_1.concatenation_type_dict)
