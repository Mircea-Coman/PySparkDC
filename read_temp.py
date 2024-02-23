import numpy as np
from Data import Data
import matplotlib.pyplot as plt
from default_file_structures import DEFAULT_TEMPERATURE_FILE

file_1 = '/mnt/Mircea/Facultate/PhD/CryoDC/data/cryodc_20240215-092956.dat'
file_2 = '/mnt/Mircea/Facultate/PhD/CryoDC/data/cryodc_20240215-104323.dat'


data = Data.read_from_files(DEFAULT_TEMPERATURE_FILE, [file_1, file_2])

plt.figure(figsize = (13, 8))
plt.plot(data.df.timestamp,  data.df.temp_A)
plt.plot(data.df.timestamp,  data.df.temp_B)
plt.plot(data.df.timestamp,  data.df.temp_C)
plt.plot(data.df.timestamp,  data.df.temp_D)
plt.plot(data.df.timestamp,  data.df.temp_E)
plt.plot(data.df.timestamp,  data.df.temp_F)

plt.show()
