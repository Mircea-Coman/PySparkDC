import copy
import numpy as np
import pandas as pd

def dim(a):
    if not type(a) == np.ndarray and not type(a) == pd.core.series.Series:
        if not type(a) == list:
            return []
        return [len(a)] + dim(a[0])
    else:
        return list(a.shape)
def len_of_sublists(array):
    length = []
    for i in range(0, len(array)):
        length.append(len(array[i]))
    return length

def duplicate_like(array, item):
    new_array = copy.deepcopy(array)
    for i in range(0, len(array)):
        sub_array = array[i]
        for j in range(0, len(sub_array)):
            new_array[i][j] = item
    return new_array

def fix_parameter_list(keys, param_array):
    keys_dim = dim(keys)
    param_dim = dim(param_array)
    if len(param_dim) == 0 and len(keys_dim) != 0:
        new_param_array = duplicate_like(keys, param_array)
        return new_param_array
    elif len(param_dim) == 1 and keys_dim[0] == 1:
        return [param_array]
    elif len(keys_dim) == 2 and len(param_dim) and len_of_sublists(keys) == len_of_sublists(param_array):
        new_param_array = param_array
        return new_param_array
    else:
        raise ValueError("The dimensions of the parameter array and the key array are invalid!")
        return -1

def fix_gaps_between_files(data, key, add_nan = True):
    """
    Fixes the data for plotting. It adds n-1 data points in between data corresponding to different files. If add_nan it adds a nan, otherwise it copies the previous data.

    Parameters
    ----------
    key:                str
                        The key corresponding to the column to be plotted on the y axis

    add_nan:            bool, default: True
                        If True, add a NaN value at the end of the data corresponding to each file. Otherwise, copy the previous value
    Returns
    -------
    new_x:              numpy.ndarray
                        The fixed array
    """
    file_separators = data.file_separators
    n_files = file_separators.shape[0]
    x = data.df[key].to_numpy()
    new_x = np.zeros([x.shape[0] + n_files - 1])
    for i in range(0, n_files):
        start = file_separators[i, 0]
        end = file_separators[i, 1]
        new_x[start+i:end+i] = x[start:end].flatten()
        if i != n_files - 1:
            if add_nan:
                new_x[end+i] = np.NAN
            else:
                new_x[end+i] = x[end-1]
    return new_x

# arr = ['a', 'b', 'c']
# duplicate_like(arr, '1')
# arr = [['a', 'b', 'c'], ['d', 'e', 'f', 'g']]
# print(len_of_sublists(arr))
# print(dim(arr))
# print(duplicate_like(arr, '1'))
