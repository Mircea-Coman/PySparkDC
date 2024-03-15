import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from dateutil import tz
from zoneinfo import ZoneInfo

import Utils
from default_file_structures import DEFAULT_STYLE

class FancyPlot():
    """
    A very fancy plotting tool used for making multiple axes plots
    """

    def __init__(self, *args, figsize = (13, 8), n_ax = 1, fontsize = 12, fontweight = 'normal', style_dict = None):
        """
        Initializer for the FancyPlot Class

        Parameters
        ----------
        fig:    matplotlib.pyplot.figure, optional
                The figure used for plotting
                If the argument is not provided, a new figure is created, along with new n_ax axes
        axs:    list of matplotlib.pyplot.axis, optional
                The axes of the figure
                If the argument is not provided, a new figure is created, along with new n_ax axes

        figsize:    tuple, default: (13, 8)
                    The size of the figure in inches
        fontsize:   int, default: 12
                    Dictionary of units for each data column.
                    If not present, it is created from the structure argument
        fontweight: ['normal'|'bold'|'heavy'|'light'|'ultrabold'|'ultralight'], default: 'normal'

        style_dict: dict, default: None
                    The style dictionary used for choosing the color of the lines, the markers etc.
                    If None, the defaults from the matplotlib color cycle are used.
                    Example of style_dict: {'field': {'color': 'blue', 'linestyle': solid, 'marker': None, ...}, ...}

        """
        self.fontsize = fontsize
        self.fontweight = fontweight
        plt.rcParams.update({"font.weight": fontweight, "font.size": fontsize})

        self.color_cycle_counter = 0 #counts the default colors
        self.style_dict = style_dict

        if len(args) == 0: #no arguments
            self.fig, ax = plt.subplots(figsize = figsize, layout='constrained') #constrained for better layouting while adding new axes
            self.axs = [ax]
            for i in range(1, n_ax): #first axes is left, then right, right, left, right, left, right...
                if i == 1:
                    location = 'right'
                else:
                    location = ('left' if i%2 == 1 else 'right')

                self.add_axis(location = location)
            self.set_fontsize(self.fontsize)
        elif len(args) == 2: #fig and axs
            self.fig = args[0]
            self.axs = args[1]

    def add_axis(self, location =  'right', offset = 0.1):
        """
        Add a new vertical axis to the plot

        Parameters
        ----------
        location:   ['left'|'right'], default:'right'
                    The location of the new axis

        offset:     float, default: 0.1
                    The ofset of all axes, relative to the spine of the previous axis.
                    Warning: All axes will be moved, such that the offset is constant for all axes
        """
        new_ax = self.axs[0].twinx()
        self.axs.append(new_ax)

        new_ax.yaxis.set_ticks_position(location)
        new_ax.yaxis.set_label_position(location)

        self.set_fontsize(self.fontsize)
        self.set_spine_spacing(offset)

        # else:
        #     raise ValueError("Only 'left' and 'right' are valid values for the location argument")

        return 0

    def set_spine_spacing(self, offset):
        """
        Set the spacing between successive y axes

        Parameters
        ----------
        offset:     float
                    The spacing of all axes, relative to the spine of the previous axis.
                    Warning: All axes will be moved, such that the offset is constant for all axes
        """
        i = 0
        for ax in self.axs:
            d_pos = np.floor(i/2) * offset

            location = ax.yaxis.get_ticks_position()
            if location == 'right':
                # self.fig.subplots_adjust(right = 1-d_adjust)
                ax.spines.right.set_position(("axes", 1 + d_pos))
            elif location == 'left':
                # self.fig.subplots_adjust(left = d_adjust)
                ax.spines.left.set_position(("axes", -d_pos))
            i += 1


    def set_fontsize(self, fontsize):
        """
        Set the fontsize

        Parameters
        ----------
        fontsize:   int
        """
        self.fontsize = fontsize
        for ax in self.axs:
            ax.tick_params(axis='both', which='both', labelsize=fontsize)
            ax.xaxis.label.set_size(fontsize)
            ax.yaxis.label.set_size(fontsize)
            ax.title.set_fontsize(fontsize)
            if ax.get_legend() is not None:
                for text in ax.get_legend().get_texts():
                    text.set_fontsize(fontsize)


    def set_ylabels(self, *ylabels):
        """
        Set the y labels for all axes

        Parameters
        ----------
        *ylabels:   str
                    Example: set_ylabels('Electric Field', 'Temperature', 'Number of Breakdowns')
        """
        n = min(len(ylabels), len(self.axs))
        for i in range(n):
            self.set_axis_ylabel(i, ylabels[i])


    def set_xlabel(self, xlabel):
        """
        Set the x label for all axes

        Parameters
        ----------
        xlabel:   str
                  All axes will have the same xlabel
        """
        n = len(self.axs)
        for i in range(n):
            self.set_axis_xlabel(i, xlabel)

    def set_axis_xlabel(self, ax_id, xlabel):
        """
        Set the x label for the specified matplotlib axis

        Parameters
        ----------
        ax_id:      int
                    The index in the axs list of the matplotlib axis for which the xlabel will be changed
        xlabel:     str
        """
        self.axs[ax_id].set_xlabel(xlabel, fontweight = self.fontweight)

    def set_axis_ylabel(self, ax_id, ylabel):
        """
        Set the y label for the specified matplotlib axis

        Parameters
        ----------
        ax_id:      int
                    The index in the axs list of the matplotlib axis for which the ylabel will be changed
        ylabel:     str
        """
        self.axs[ax_id].set_ylabel(ylabel, fontweight = self.fontweight)

    def set_spine_color(self, ax_id, color):
        """
        Sets the color of the spine for a specified matplotlib axis

        Parameters
        ----------
        ax_id:      int
                    The index in the axs list of the matplotlib axis for which the color will be changed
        color:      any matplotlib color
        """
        location = self.axs[ax_id].yaxis.get_ticks_position()
        self.axs[ax_id].tick_params(axis='y', labelcolor=color)
        self.axs[ax_id].spines[location].set_edgecolor(color)
        self.axs[ax_id].yaxis.label.set_color(color=color)

    def set_axis_yscale(self, ax_id, scale):
        """
        Set the scale type for the y scale for a specified matplotlib axis

        Parameters
        ----------
        ax_id:      int
                    The index in the axs list of the matplotlib axis for which the yscale will be set
        scale:      {"linear", "log", "symlog", "logit", ...}
        """
        self.axs[ax_id].set_yscale(scale)

    def set_axis_ylim(self, ax_id, lim):
        """
        Set the limits for the y axis for the specified matplotlib axis

        Parameters
        ----------
        ax_id:      int
                    The index in the axs list of the matplotlib axis for which the ylim will be set
        lim:        [float, float]
        """
        self.axs[ax_id].set_ylim(lim)

    def set_axis_xlim(self, ax_id, lim):
        """
        Set the limits for the x axis for the specified matplotlib axis

        Parameters
        ----------
        ax_id:      int
                    The index in the axs list of the matplotlib axis for which the xlim will be set
        lim:        [float, float]
        """
        self.axs[ax_id].set_xlim(lim)

    def set_xlim(self, lim):
        """
        Set the same xlim for all matplotlib axes

        Parameters
        ----------
        lim:        [float, float]
        """
        for ax in self.axs:
            ax.set_xlim(lim)

    def set_xlim_from_data(self, data, x_key):
        """
        Set the same xlim for all matplotlib axes from a data object. This is equivalent to FancyPlot.set_xlim([data.df[x_key]min(), data.df[x_key]max()])

        Parameters
        ----------
        data:       Data
                    The data object from which the limits will be extracted
        x_key:      str
                    The column used for the x data on the plot

        """
        min = data.df[x_key].min()
        max = data.df[x_key].max()
        self.set_xlim([min, max])

    def legend(self, ax_id = -1, loc = 'best'):
        """
        Make the legend for the plot.

        Parameters
        ----------
        ax_id:      int, default: -1 (last axos)
                    The index in the axs list of the matplotlib axis for which on which the legend will be drawn
        loc:        str or pair of floats, default: rcParams["legend.loc"] (default: 'best')
                    The location of the legend.
        """
        h = []
        l = []
        for ax in self.axs: #   combining all the plots from all axes
            h1, l1 = ax.get_legend_handles_labels()
            h += h1
            l += l1
        self.axs[ax_id].legend(h, l, loc=loc, fontsize = self.fontsize)

    def __get_zorder__(self):
        """
        Get the zorder for all axes

        Returns
        -------
        zs:         list of int
                    The z order for each matplotlib axis in the axs list
        """
        n = len(self.axs)
        zs = np.empty([n])
        for i in range(n):
            zs[i] = self.axs[i].get_zorder()
        return zs

    def send_ax_to_front(self, ax_id):
        """
        Set the specified matplotlib axes to the top of the other axes

        Parameters
        ----------
        ax_id:      int
                    The index in the axs list of the matplotlib axis which will be set on top
        """

        zs = self.__get_zorder__()
        self.axs[ax_id].set_zorder(np.max(zs)+1)

    def set_ax_zorder(self, ax_id, zorder):
        """
        Sets the zorder for a specified matplotlib axis

        Parameters
        ----------
        ax_id:      int
                    The index in the axs list of the matplotlib axis for which the zorder will be changed
        """
        self.axs[ax_id].set_zorder(zorder)

    def set_zorder(self, order):
        """
        Sets the zorder for all axes

        Parameters
        ----------
        oder:       list of int
                    The order for each matplotlib axis in the axs list
        """
        n = len(self.axs)
        if n != len(order):
            raise ValueError("In set_zorder: length of order array not equal to the number of axes")
        for i in range(n):
            self.set_ax_zorder(i, order[i])
        self.set_patches_invisible()

    def set_patches_invisible(self):
        """
        Makes all matplotlib.patches invisible. Useful when changing the order of the axes. It is called automatically when set_zorder() is called
        """
        for ax in self.axs:
            ax.patch.set_visible(False)

    def __get_next_color__(self):
        """
        Returns the next color in the color cycle as CN, where N is a number

        Returns
        -------
        color:      str
        """
        color = f"C{self.color_cycle_counter}"
        self.color_cycle_counter += 1
        return color

    def stripe_from_data(self, data, start_i, end_i, x_key = 'timestamp', ax_id = 0, color = '0.9', datetime_plot = False):
        """
        Adds an axvspan between data.df[x_key].iloc[start_i] and data.df[x_key].iloc[end_i]

        Parameters
        ----------
        data:       Data
                    The data object used in the plot
        start_i:    int
                    The index from which to start the axvspan
        end_i:      int
                    The index at which the axvspan ends

        x_key:          str, default = 'timestamp'
                        The column used for the x axis
        ax_id:          int, default = 0
                        The index of the matplotlib axes in the axs list on which the axvspan will be drawn
        color:          matplotlib color, default: '0.9' (grey)
                        The facecolor of the axvspan
        datetime_plot:  bool, default: False
                        Specified whether the x axis is formated as datetime
        """
        start = data.df[x_key].iloc[start_i]
        end = data.df[x_key].iloc[end_i]
        self.stripe(start, end, ax_id = ax_id, color = color, datetime_plot = datetime_plot)


    def stripe(self, start_x, end_x, ax_id = 0, color = '0.9', datetime_plot = False):
        """
        Adds an axvspan between start and end

        Parameters
        ----------
        data:       Data
                    The data object used in the plot
        start:      np.ndarray or double
                    The start of the axvspan
        end:        np.ndarray or double
                    The end of the axvspan

        ax_id:          int, default = 0
                        The index of the matplotlib axes in the axs list on which the axvspan will be drawn
        color:          matplotlib color, default: '0.9' (grey)
                        The facecolor of the axvspan
        datetime_plot:  bool, default: False
                        Specified whether the x axis is formated as datetime
        """
        if datetime_plot: # convert to mdates if datetime plot
            new_start_x = mdates.epoch2num(start_x)
            new_end_x = mdates.epoch2num(end_x)
        else:
            new_start_x = start_x
            new_end_x  = end_x

        if len(Utils.dim(new_start_x)) == 0 and len(Utils.dim(new_end_x)) == 0: #If start and end are scalar, convert to np.ndarray
            new_start_x = np.array([new_start_x])
            new_end_x = np.array([new_end_x])

        # if pandas.Series, convert to numpy
        if type(new_start_x) == pd.core.series.Series: new_start_x = pd.Series.to_numpy(new_start_x)
        if type(new_end_x) == pd.core.series.Series: new_end_x = pd.Series.to_numpy(new_end_x)

        # finally, create the axvspan
        for i in range(new_start_x.shape[0]):
            self.axs[ax_id].axvspan(new_start_x[i], new_end_x[i], facecolor = color)

    def stripe_files(self, data, x_key = 'timestamp', ax_id = 0, color = '0.9', sec_color = '1.0', datetime_plot = False):
        """
        Makes axvspans that separate data from different files

        Parameters
        ----------
        data:       Data
                    The data object used in the plot

        ax_id:          int, default = 0
                        The index of the matplotlib axes in the axs list on which the axvspan will be drawn
        x_key:          str, default = 'timestamp'
                        The column used for the x axis
        color:          matplotlib color, default: '0.9' (grey)
                        The facecolor of the odd axvspans
        sec_color:      matplotlib color, default: '1.0' (white)
                        The facecolor of the even axvspans
        datetime_plot:  bool, default: False
                        Specified whether the x axis is formated as datetime
        """
        f_sep = data.file_separators

        for i in range(f_sep.shape[0]):
            current_color = color if i%2 else sec_color
            self.stripe_from_data(data, f_sep[i,0], f_sep[i,1], x_key = x_key, ax_id = ax_id, color = current_color, datetime_plot = datetime_plot)

    def plot(self, x, y, ax_id = 0, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', datetime_plot = True, marker = None, \
    markersize = 5, linestyle = 'solid', linewidth = 2, color = None, label = None, scaling_x = 1, scaling_y = 1):
        """
        Plots the specified x and y data on the FancyPlot

        Parameters
        ----------
        x:              np.ndarray or pandas.Series
                        The x data
        y:              np.ndarray or pandas.Series
                        The y data

        ax_id:          int, default = 0
                        The index of the matplotlib axes in the axs list on which the data will be plotted
        date_format:    str, default = '%m-%d %H:%M:%S'
                        The format of the data used if datetime_plot is enabled
        timezone:       str, default = 'Europe/Stockholm'
                        The timezone used if if datetime_plot is enabled
        datetime_plot:  bool, default: True
                        Specified whether the x axis is formated as datetime. If the x data are already mdates, this should be set to False

        marker:         matplotlib marker, default: None
        markersize:     int, default: 5
        linestyle:      matplotlib linestyle, default: 'solid'
        linewidth:      int, default: 2
        color:          matplotlib color, default: None (a color is selected from the color cycle)
        label:          str, default: None
                        The label of the Line2D plot
        scaling_x:      double
                        The x data is multiplied by this number when plotting. Useful when converting units
        scaling_y:      double
                        The y data is multiplied by this number when plotting. Useful when converting units
        """
        if datetime_plot: # convert to mdates
            new_x = mdates.epoch2num(x)
            date_formatter = DateFormatter(date_format, tz=tz.gettz(timezone))
            self.axs[ax_id].xaxis.set_major_formatter(date_formatter)
            plt.setp(self.axs[0].xaxis.get_majorticklabels(), rotation=70)
        else:
            new_x = scaling_x*x # scale the x axis
        new_y = scaling_y * y # scale the y axis
        if color == None: color = self.__get_next_color__() # get next color in the color cycle
        self.axs[ax_id].plot(new_x,  new_y, color = color, marker = marker, markersize = markersize, \
                linestyle = linestyle, linewidth = linewidth, label = label)


    def plot_data(self, data, keys, x_key = 'timestamp', datetime_plot = True, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', \
    ax_id = None, marker = None, markersize = 5, linestyle = '-', linewidth = 2, color = None, labels = None, scaling_x = 1, scaling_y = 1, use_style_dict = True):
        """
        Plots the selected columns from the pandas dataframe of the Data obejct

        Parameters
        ----------
        data:               Data
                            Data object from which data can be extracted
        key:                str, list of str or list of list of str
                            The keys corresponding to the columns to be plotted on the y axis.
                            If str: The data corresponding to the key will be plotted on an axis, corresponding to ax_id
                            If list of str: The data corresponding to all keys will be plotted on a single axis, corresponding to ax_id
                            if list of list of str: The data corresponding to the keys from each sublist will be plotted on different axes, corresponding to ax_id

        x_key:              str, default: 'timestamp'
                            The key corresponding to the column to be plotted on the x axis.
        ax_id:              int or list of int, default = None
                            The index of the matplotlib axes in the axs list on which the data will be plotted. If None, the axis used will be 0, 1, 2, 3...
        date_format:        str, default = '%m-%d %H:%M:%S'
                            The format of the data used if datetime_plot is enabled
        timezone:           str, default = 'Europe/Stockholm'
                            The timezone used if if datetime_plot is enabled
        datetime_plot:      bool, default: True
                            Specified whether the x axis is formated as datetime. If the x data are already mdates, this should be set to False
        marker:             matplotlib marker, default: None
        markersize:         int, default: 5
        linestyle:          matplotlib linestyle, default: 'solid'
        linewidth:          int, default: 2
        color:              matplotlib color, default: None (a color is selected from the color cycle)
        labels:             str or list of str, default: None
                            The labels of the Line2D plot. If None, get the labels from the info_dict of the Data object
        scaling_x:          double
                            The x data is multiplied by this number when plotting. Useful when converting units
        scaling_y:          double
                            The y data is multiplied by this number when plotting. Useful when converting units
        use_style_dict:     bool,   default: True
                            If true, the proprieties of the plot will be derived from the provided style_dict

        """
        # check the dimensions of the key list and convert it to a standard format(list of list of str)
        keys_dim = Utils.dim(keys)
        if len(keys_dim) == 0:
            keys = [[keys]]
            n_axes = 1
        elif len(keys_dim) == 1:
            keys = [keys]
            n_axes = 1
        elif len(keys_dim) == 2:
            n_axes = keys_dim[0]
        else:
            raise ValueError("The keys array should be a str, list of str, or list of lists of str!")
        keys_dim = Utils.dim(keys) #the dimensions changed, recalculate dimensions

        # check the dimensions of the labels and convert it to a standard format (list of str)
        labels_dim = Utils.dim(labels)
        if len(labels_dim) == 0:
            if labels is not None: labels = [[labels]]
        elif len(labels_dim) == 1:
            labels = [labels]
        elif len(labels_dim) > 2:
            raise ValueError("The labels array should be a str, list of str, or list of lists of str!")

        # check the dimensions of the ax_id and convert it to a standard format (list of int)
        ax_id_dim = Utils.dim(ax_id)
        if len(ax_id_dim) == 0:
            if ax_id is not None: ax_id = [ax_id]*keys_dim[0]
        elif len(ax_id_dim) == 1:
            ax_id = ax_id
        else:
            raise ValueError("The ax_id array should be a int or list of int")

        # do the same thing for the other parameters
        marker = Utils.fix_parameter_list(keys, marker)
        linestyle = Utils.fix_parameter_list(keys, linestyle)
        color = Utils.fix_parameter_list(keys, color)
        linewidth = Utils.fix_parameter_list(keys, linewidth)
        markersize = Utils.fix_parameter_list(keys, markersize)


        # fix gaps between data corresponding to different files. A NaN value is added at the end of the data corresponding to each file.
            # Otherwise, in the plot, a line will brige the gap between the data corresponding to different neighbouring files

        x_data = Utils.fix_gaps_between_files(data, x_key)
        if datetime_plot and x_key == 'timestamp': # convert to mdates
            date_formatter = DateFormatter(date_format, tz=tz.gettz(timezone))
            new_x = mdates.epoch2num(x_data)
        else:
            new_x = x_data

        for i in range(0, n_axes): #iterate through all axes
            if ax_id is None: # if ax_id is None, use axs[i], else use axs[ax_id[i]]
                current_ax = self.axs[i]
                current_ax_id = i
            else:
                current_ax = self.axs[ax_id[i]]
                current_ax_id = ax_id[i]

            if datetime_plot and x_key == 'timestamp': # set up the plot for datetime plotting
                current_ax.xaxis.set_major_formatter(date_formatter)
                plt.setp(self.axs[0].xaxis.get_majorticklabels(), rotation=70)

            for j in range(0, len(keys[i])):
                # get style from the  style_dict, if available
                current_color, current_linestyle, current_linewidth, current_marker, current_markersize = \
                    self.__get_style__(keys[i][j], color[i][j], linestyle[i][j], linewidth[i][j], marker[i][j], markersize[i][j], use_style_dict = use_style_dict)

                if labels is None:
                    label = data.info_dict[keys[i][j]]['label']
                else:
                    label = labels[i][j]
                y_data = Utils.fix_gaps_between_files(data, keys[i][j], add_nan = True)
                # datetime_plot is set to False in the following. This is done because x_data is already converted to mdates
                self.plot(new_x,  y_data, ax_id = current_ax_id, scaling_x = scaling_x, scaling_y = scaling_y, color = current_color, marker = current_marker, \
                    markersize = current_markersize, linestyle = current_linestyle, linewidth = current_linewidth, label = label, datetime_plot = False)

    def __get_style__(self, key, color, linestyle, linewidth, marker, markersize, use_style_dict = True):
        """
        Gets the style used for plotting

        Parameters
        ----------
        key:            str
                        The key corresponding to the column to be plotted
        color:          matplotlib color
        linestyle:      matplotlib linestyle
        linewidth:      int, default: 2
        marker:         matplotlib marker, default: None
        markersize:     float, default: 5

        use_style_dict: bool,   default: True
                                If true, the proprieties of the plot will be derived from the provided style_dict
        Returns
        ----------
        color:          matplotlib color
                        If style_dict is not None and is in use and the key is found, the color from the dictionary is used. Otherwise use the colors from the color cycle
        linestyle:      matplotlib linestyle
                        If style_dict is not None and is in use and the key is found, the linestyle from the dictionary is used. Otherwise use the provided linestyle
        linewidth:      int, default: 2
                        If style_dict is not None and is in use and the key is found, the linewidth from the dictionary is used. Otherwise use the provided linewidth
        marker:         matplotlib marker, default: None
                        If style_dict is not None and is in use and the key is found, the marker from the dictionary is used. Otherwise use the provided marker
        markersize:     int, default: 5
                        If style_dict is not None and is in use and the key is found, the markersize from the dictionary is used. Otherwise use the provided markersize
        """
        if use_style_dict and self.style_dict is not None and key in self.style_dict:
                style = self.style_dict[key]
                new_color = style['color']             if 'color'      in style else color
                new_linestyle = style['linestyle']     if 'linestyle'  in style else linestyle
                new_linewidth = style['linewidth']     if 'linewidth'  in style else linewidth
                new_marker = style['marker']           if 'marker'     in style else marker
                new_markersize = style['markersize']   if 'markersize' in style else markersize
                if new_color is None:
                    new_color = f"C{self.color_cycle_counter}"
                    self.color_cycle_counter += 1
                return new_color, new_linestyle, new_linewidth, new_marker, new_markersize
        elif color is None:
            new_color = self.__get_next_color__()
            return new_color, linestyle, linewidth, marker, markersize
        else:
            return color, linestyle, linewidth, marker, markersize
