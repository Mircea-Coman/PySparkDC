import copy
import numpy as np
import pandas as pd

def dim(a):
    """
    Gets the dimesion of a python list, a pandas.Series or a numpy.ndarray

    Parameters
    ----------
    a:                  list, pandas.Series, numpy.ndarray
    Returns
    -------
    dim:                list
                        The dimensions of the list/array/Series
    """
    if not type(a) == np.ndarray and not type(a) == pd.core.series.Series:
        if not type(a) == list:
            return []
        return [len(a)] + dim(a[0])
    else:
        return list(a.shape)

def len_of_sublists(list):
    """
    For a list of lists, return the dimension of each sublist

    Parameters
    ----------
    list:               list

    Returns
    -------
    length:             list
                        The dimension of each sublist in list
    """
    length = []
    for i in range(0, len(list)):
        length.append(len(list[i]))
    return length

def duplicate_like(array, item):
    """
    Given a list, it returns a new list with the same shape, but filled with the requested item

    Parameters
    ----------
    array:              list

    Returns
    -------
    new_array:          list
    """
    new_array = copy.deepcopy(array)
    for i in range(0, len(array)):
        sub_array = array[i]
        for j in range(0, len(sub_array)):
            new_array[i][j] = item
    return new_array

def fix_parameter_list(keys, param_array):
    """
    The parameter lists, such as the colors or the linestyles can be given in different formats then the keys corresponding to the data to be plotted.
    This function attemps to cast the parameter array in the same shape as the keys array

    Parameters
    ----------
    keys:              str, list of str, or list of list of str
    param_array:       str, list of str, or list of list of str

    Returns
    -------
    new_param_array:   list of list of str
    """
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


def get_concatenation_type_columns(info_dict, type):
    """
    Returns the keys from info_dict which have the concatenation_type set to a specified type. Warning: It requires a completely filled dictionary!

    Parameters
    ----------
    info_dict:          dict
    type:               ['normal'|'additive']
                        The concatenation type for which we want to obtain the keys
    Returns
    -------
    columns:           list
                       list of columns that have the concatenation_type of the specified type
    """
    columns = []
    for item in info_dict.items():
        key = item[0]
        subdict = item[1]
        if 'concatenation_type' in subdict:
            if subdict['concatenation_type'] == type: columns.append(key)
        else:
            raise ValueError('concatenation_type not found in dictionary!')
    return columns

def get_keys_info_dict(info_dict):
    """
    Returns all the keys from a specified dictionary

    Parameters
    ----------
    info_dict:          dict
    Returns
    -------
    props:             list
                       list of keys from dictionary
    """
    keys = []
    for item in info_dict.items():
        key = item[0]
        subdict = item[1]
        keys.append(key)
    return keys


def get_from_info_dict(info_dict, property):
    """
    Returns the values from a dictionary of subdictionaries

    Parameters
    ----------
    info_dict:          dict
    property:           str

    Returns
    -------
    props:             list
                       list of values
    """

    props = []
    for item in info_dict.items():
        key = item[0]
        subdict = item[1]
        if property in subdict:
            props.append(subdict[property])
        else:
            raise ValueError(f'{property} not find in dictionary!')

    return props


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
        end = file_separators[i, 1]+1
        new_x[start+i:end+i] = x[start:end].flatten()
        if i != n_files - 1:
            if add_nan:
                new_x[end+i] = np.NAN
            else:
                new_x[end+i] = x[end-1]
    return new_x
