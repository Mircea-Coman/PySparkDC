from Data import Data
from default_file_structures import DEFAULT_CONDITIONING_STRUCTURE, LABVIEW_TIMESTAMP_OFFSET
import os
import glob
import pandas as pd

DEFAULT_FILENAME = 'Marx_data.txt'

class ConditioningData(Data):
    def __init__(self, *args, structure = DEFAULT_CONDITIONING_STRUCTURE):
        if len(args) == 0:
            df = args[0]
            label_dict, unit_dict, concatenation_type_dict = self.__create_dictionaries__(structure)
            df =  pd.DataFrame(columns = structure[:, 0])
        elif len(args) == 1:
            df = args[0]
            super().__init__(df, structure = structure)
        elif len(args) == 4:
            df = args[0]
            label_dict = args[1]
            unit_dict = args[2]
            concatenation_type_dict =  args[3]
        else:
            raise ValueError("Invalid number of arguments")

        super().__init__(df, label_dict, unit_dict, concatenation_type_dict, structure = structure)
        self.calculate_derived_columns()

    def calculate_derived_columns(self):
        self.df['target_field'] = (self.df['target_voltage'] / self.df['gap'])
        self.label_dict['target_field'] = 'Target Electric Field'
        self.unit_dict['target_field'] = 'MV/m'
        self.concatenation_type_dict['target_field'] = 'normal'

        self.df['field'] = (self.df['output_voltage'] / self.df['gap'])
        self.label_dict['field'] = 'Electric Field'
        self.unit_dict['field'] = 'MV/m'
        self.concatenation_type_dict['field'] = 'normal'


    @staticmethod
    def read_from_files(file_paths, header = None, delimiter = '\s+', skiprows = 1, engine ='python', structure = DEFAULT_CONDITIONING_STRUCTURE):
        data = Data.read_from_files(file_paths, header = header, delimiter = delimiter, engine = engine, skiprows = skiprows, structure = DEFAULT_CONDITIONING_STRUCTURE)
        cond_data = ConditioningData(data.df, data.label_dict, data.unit_dict, data.concatenation_type_dict)
        return cond_data

    @staticmethod
    def read_runs(data_folder, electrode, runs, header = None, delimiter = '\s+', skiprows = 1, engine ='python', structure = DEFAULT_CONDITIONING_STRUCTURE):
        electrode_path = os.path.join(data_folder, electrode)
        files_to_read = []
        for current_run in runs:
            run_path = glob.glob(f"{electrode_path}/*{electrode}*{current_run:03d}")[0]
            file_path = os.path.join(run_path, DEFAULT_FILENAME)
            files_to_read.append(file_path)
        cond_data = ConditioningData.read_from_files(files_to_read, header = header, delimiter = delimiter, skiprows = skiprows, \
        engine = engine, structure = structure)
        col_len = cond_data.df.shape[1]

        #make the run_id column, which shows the run number
        cond_data.df.insert(col_len, "run_id", runs[pd.Series.to_numpy(cond_data.df.file_id)], True)
        return cond_data
