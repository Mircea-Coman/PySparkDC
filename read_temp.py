import numpy as np
from Data import Data
from StatusData import StatusData
from default_file_structures import DEFAULT_TEMPERATURE_STRUCTURE, DEFAULT_TEMPERATURE_STYLES, LABVIEW_TIMESTAMP_OFFSET

import matplotlib.pyplot as plt


folder = '/mnt/Mircea/Facultate/PhD/CryoDC/data/'

# data = StatusData.read_from_folder_between_timestamps(folder, [1707985796.0-100, 1708074591.0+100], descending_search = False)
data = StatusData.read_from_folder_between_datetimes(folder, ['20240216-104323', '20240216-130951'], descending_search = False)
# data = StatusData.read_from_folder_between_datetimes(folder, ['20201014-143000', '20201014-153000'], descending_search = True)

# data = StatusData.read_from_files([file_1, file_2])

# print(data.df['file'])
#
fig, ax = data.plot(['temp_A', 'temp_B', 'temp_C', 'temp_D', 'temp_E', 'temp_F'])
ax.set_ylabel('Temperature [K]')
# ax.set_xlabel('Time [s]')
plt.show()
