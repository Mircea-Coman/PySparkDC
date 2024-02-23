import numpy as np
from DataField import DataField
from Data import Data
import matplotlib.pyplot as plt

file_1 = '/mnt/Mircea/Facultate/PhD/CryoDC/data/cryodc_20240215-092956.dat'
file_2 = '/mnt/Mircea/Facultate/PhD/CryoDC/data/cryodc_20240215-104323.dat'

index_dict = {
    'temp_A':                 [0,   'Temperature CH A',     'K',    'normal'],
    'temp_B':                 [1,   'Temperature CH B',     'K',    'normal'],
    'temp_C':                 [2,   'Temperature CH C',     'K',    'normal'],
    'temp_D':                 [3,   'Temperature CH D',     'K',    'normal'],
    'temp_E':                 [4,   'Temperature CH E',     'K',    'normal'],
    'temp_F':                 [5,   'Temperature CH F',     'K',    'normal'],
    'timestamp':              [21,  'Timestamp',            's',    'normal']
}

data = Data.read_from_files(index_dict, [file_1, file_2])
print(data.temp_A.name, data.temp_A.unit)

plt.figure(figsize = (13, 8))
plt.plot(data.timestamp.values,  data.temp_A.values)
plt.plot(data.timestamp.values,  data.temp_B.values)
plt.plot(data.timestamp.values,  data.temp_C.values)
plt.plot(data.timestamp.values,  data.temp_D.values)
plt.plot(data.timestamp.values,  data.temp_E.values)
plt.plot(data.timestamp.values,  data.temp_F.values)

plt.show()
