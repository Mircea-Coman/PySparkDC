import numpy as np
from Data import Data
from StatusData import StatusData
from ConditioningData import ConditioningData
from RGAData import RGAData
from FancyPlot import FancyPlot

from default_file_structures import DEFAULT_TEMPERATURE_STRUCTURE, DEFAULT_CONDITIONING_STRUCTURE, LABVIEW_TIMESTAMP_OFFSET

import matplotlib.pyplot as plt

status_folder = '/mnt/Mircea/Facultate/PhD/CryoDC/data/'
file_RGA_1 = '/mnt/Mircea/Facultate/PhD/process_FE/Field_Emission_Nb/process_RGA/231101_heat_FE.csv'
range = ['20231101-120000', '20231101-163000']
rga_data = RGAData.read_from_file(file_RGA_1)
rga_data.remove_data_datetime_range(range)

# status_data = StatusData.read_from_folder_between_datetimes(status_folder, range)
# print(type(status_data.df))
# print(status_data.df['timestamp'].min())
# fplot = FancyPlot(n_ax = 2, fontsize = 15)
# status_data.plot(['temp_A', 'temp_B'], labels = ['Cathode Temperature', 'Anode Temperature'], fplot = fplot, ax_id = 1, color = 'k', linestyle = ['solid', 'dotted'], use_style_dict = False)
# rga_data.plot_masses([2, 18], key = 'pressure_mbar', ax_id = 0, fplot = fplot, scaling_y = 1E9)
# fplot.add_axis()
# fplot.set_ylabels(r'Partial Pressure [$10^{-9} mbar$]', 'Temperature [K]', 'Cos')
# fplot.legend(loc='upper center')
# fplot.set_zorder([2, 1, 0])
# print(fplot.__get_zorder__())
# plt.show()

folder = '/media/mircea/AAAAAAAAAAA/conditioning data/'
electrode  = '066_RFQ_Nb_rm1'
runs = np.arange(1, 11)
cond_data = ConditioningData.read_runs(folder, electrode, runs)
cplot = cond_data.plot_standard(color_runs = [{'color': (1, 0, 0, 0.2), 'run': [1,3]}, {'color': (0, 1, 0, 0.2), 'run': 2}], stripe=True)
plt.show()

# fplot = cond_data.plot([['target_field'], ['BDs'], ['BDR']], x_key = 'all_pulses', figsize = (20, 10))
# fplot.set_ylabels('Electic Field [MV/m]', 'BD #', 'BDR')
# fplot.set_axis_yscale(2, 'log')
# fplot.set_axis_ylim(2, [1E-8, 1E-3])
# fplot.set_fontsize(15)
# plt.show()

# data = StatusData.read_from_folder_between_datetimes(status_folder, ['20240215-104323', '20240216-130951'], descending_search = False)
# data.plot_status(['temp_A', 'temp_B', 'temp_C', 'temp_D', 'temp_E', 'temp_F', 'setpoint'])
# plt.show()

# file_1 = '/media/mircea/AAAAAAAAAAA/conditioning data/066_RFQ_Nb_rm1/2023_06_21_066_RFQ_Nb_rm1_009/Marx_data.txt'
# file_2 = '/media/mircea/AAAAAAAAAAA/conditioning data/066_RFQ_Nb_rm1/2023_06_26_066_RFQ_Nb_rm1_010/Marx_data.txt'
# folder = '/media/mircea/AAAAAAAAAAA/conditioning data/'
# electrode  = '061_RFQ_Soft_Cu'
# runs = np.arange(1, 11)
#
# structure = DEFAULT_CONDITIONING_STRUCTURE
# # data = ConditioningData.read_from_files([file_1, file_2], header = None, skiprows = 1)
# data = ConditioningData.read_runs(folder, electrode, runs)
# print(data.df.run_id)
#
# fig, ax = plt.subplots(figsize = (13, 8))
# ax.plot(data.df.all_pulses, data.df.field, 'k.')
# ax2 = ax.twinx()
# ax2.plot(data.df.all_pulses, data.df.BDs, 'r.')
# ax.set_ylabel('Out Voltage [V]')
# ax.set_xlabel('Pulses')
# plt.show()
#

# folder = '/mnt/Mircea/Facultate/PhD/CryoDC/data/'
#
# # data = StatusData.read_from_folder_between_timestamps(folder, [1707985796.0-100, 1708074591.0+100], descending_search = False)
# data = StatusData.read_from_folder_between_datetimes(folder, ['20240216-104323', '20240216-130951'], descending_search = False)
# # data = StatusData.read_from_folder_between_datetimes(folder, ['20201014-143000', '20201014-153000'], descending_search = True)
#
# # data = StatusData.read_from_files([file_1, file_2])
#
# # print(data.df['file'])
# #
# fig, ax = data.plot(['temp_A', 'temp_B', 'temp_C', 'temp_D', 'temp_E', 'temp_F'])
# ax.set_ylabel('Temperature [K]')
# # ax.set_xlabel('Time [s]')
# plt.show()
