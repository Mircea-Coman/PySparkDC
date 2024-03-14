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
    def __init__(self, *args, figsize = (13, 8), n_ax = 1, fontsize = 12, fontweight = 'normal', colors = 'k', style_dict = DEFAULT_STYLE):
        self.fontsize = fontsize
        self.fontweight = fontweight
        plt.rcParams.update({"font.weight": fontweight, "font.size": fontsize})

        self.color_cycle_counter = 0
        self.style_dict = style_dict

        if len(args) == 0:
            self.fig, ax = plt.subplots(figsize = figsize, layout='constrained')
            self.axs = [ax]
            for i in range(1, n_ax):
                if i == 1:
                    location = 'right'
                else:
                    location = ('left' if i%2 == 1 else 'right')

                self.add_axis(location = location)
            self.set_fontsize(self.fontsize)

        elif len(args) == 1:
            self.fig = args[0]
            self.axs = args[1]

    def add_axis(self, location =  'right', offset = 0.1):
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
        n = min(len(ylabels), len(self.axs))
        for i in range(n):
            self.set_axis_ylabel(i, ylabels[i])


    def set_xlabel(self, xlabel):
        n = len(self.axs)
        for i in range(n):
            self.set_axis_xlabel(i, xlabel)

    def set_axis_xlabel(self, ax_id, xlabel):
        self.axs[ax_id].set_xlabel(xlabel, fontweight = self.fontweight)

    def set_axis_ylabel(self, ax_id, ylabel):
        self.axs[ax_id].set_ylabel(ylabel, fontweight = self.fontweight)

    def set_axis_color(self, ax_id, color):
        location = self.axs[ax_id].yaxis.get_ticks_position()
        self.axs[ax_id].tick_params(axis='y', labelcolor=color)
        self.axs[ax_id].spines[location].set_edgecolor(color)
        self.axs[ax_id].yaxis.label.set_color(color=color)

    def set_axis_yscale(self, ax_id, scale):
        self.axs[ax_id].set_yscale(scale)

    def set_axis_ylim(self, ax_id, lim):
        self.axs[ax_id].set_ylim(lim)

    def set_axis_xlim(self, ax_id, lim):
        self.axs[ax_id].set_xlim(lim)

    def set_xlim(self, lim):
        for ax in self.axs:
            ax.set_xlim(lim)

    def set_xlim_from_data(self, data, x_key):
        min = data.df[x_key].min()
        max = data.df[x_key].max()
        self.set_xlim([min, max])

    def legend(self, ax_id = -1, loc = 'best'):
        h = []
        l = []
        for ax in self.axs:
            h1, l1 = ax.get_legend_handles_labels()
            h += h1
            l += l1
        self.axs[ax_id].legend(h, l, loc=loc, fontsize = self.fontsize)

    def __get_zorder__(self):
        n = len(self.axs)
        zs = np.empty([n])
        for i in range(n):
            zs[i] = self.axs[i].get_zorder()
        return zs

    def send_ax_to_front(self, ax_id):
        zs = self.__get_zorder__()
        self.axs[ax_id].set_zorder(np.max(zs)+1)

    def set_ax_zorder(self, ax_id, zorder):
        self.axs[ax_id].set_zorder(zorder)

    def set_zorder(self, order):
        n = len(self.axs)
        if n != len(order):
            raise ValueError("In set_zorder: length of order array not equal to the number of axes")
        for i in range(n):
            self.set_ax_zorder(i, order[i])
        self.set_patches_invisible()

    def set_patches_invisible(self):
        for ax in self.axs:
            ax.patch.set_visible(False)

    def __get_next_color__(self):
        color = f"C{self.color_cycle_counter}"
        self.color_cycle_counter += 1
        return color

    def stripe_from_data(self, data, start_i, end_i, x_key = 'timestamp', ax_id = 0, color = '0.9', datetime_plot = False, timezone = 'Europe/Stockholm'):
        start = data.df[x_key].iloc[start_i]
        end = data.df[x_key].iloc[end_i]
        self.stripe(start, end, ax_id = ax_id, color = color, datetime_plot = datetime_plot, timezone = timezone)


    def stripe(self, start_x, end_x, ax_id = 0, color = '0.9', datetime_plot = False, timezone = 'Europe/Stockholm'):
        if datetime:
            new_start_x = mdates.epoch2num(start_x)
            new_end_x = mdates.epoch2num(end_x)
        else:
            new_start_x = start_x
            new_end_x  = end_x

        if len(Utils.dim(new_start_x)) == 0 and len(Utils.dim(new_end_x)) == 0:
            new_start_x = np.array([new_start_x])
            new_end_x = np.array([new_end_x])

        if type(new_start_x) == pd.core.series.Series: new_start_x = pd.Series.to_numpy(new_start_x)
        if type(new_end_x) == pd.core.series.Series: new_end_x = pd.Series.to_numpy(new_end_x)

        for i in range(new_start_x.shape[0]):
            self.axs[ax_id].axvspan(new_start_x[i], new_end_x[i], facecolor = color)

    def stripe_files(self, data, x_key = 'timestamp', ax_id = 0, color = '0.9', sec_color = '1.0', datetime_plot = False, timezone = 'Europe/Stockholm'):
        f_sep = data.file_separators

        for i in range(f_sep.shape[0]):
            current_color = color if i%2 else sec_color
            self.stripe_from_data(data, f_sep[i,0], f_sep[i,1], x_key = x_key, ax_id = ax_id, color = current_color, datetime_plot = datetime_plot, timezone = timezone)
            # self.axs[ax_id].axvspan(data.df[x_key].iloc[f_sep[i, 0]], data.df[x_key].iloc[max(0, f_sep[i, 1]-1)], facecolor = current_color)

    # def plot(self, x, y, ax_id = 0, marker = None, markersize = 5, linestyle = '-', linewidth = 2,\
    #  color = None, label = None, scaling_x = 1, scaling_y = 1):
    #     if color is None:
    #         color = self.__get_next_color__()
    #     self.axs[ax_id].plot(scaling_x * x,  y * scaling_y, color = color, marker = marker, markersize = markersize, \
    #         linestyle = linestyle, linewidth = linewidth, label = label)

    def plot(self, x, y, ax_id = 0, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', datetime_plot = False, marker = None, \
    markersize = 5, linestyle = '-', linewidth = 2, color = None, label = None, scaling_x = 1, scaling_y = 1):
        if datetime_plot:
            new_x = mdates.epoch2num(x)

            date_formatter = DateFormatter(date_format, tz=tz.gettz(timezone))
            self.axs[ax_id].xaxis.set_major_formatter(date_formatter)
            plt.setp(self.axs[0].xaxis.get_majorticklabels(), rotation=70)
        else:
            new_x = scaling_x*x
        self.axs[ax_id].plot(new_x,  y * scaling_y, color = color, marker = marker, markersize = markersize, \
                linestyle = linestyle, linewidth = linewidth, label = label)


    def plot_data(self, data, keys, x_key = 'timestamp', datetime_plot = True, date_format = "%m-%d %H:%M:%S", timezone = 'Europe/Stockholm', \
    ax_id = None, marker = None, markersize = 5, linestyle = '-', linewidth = 2, color = None, labels = None, scaling_x = 1, scaling_y = 1, use_style_dict = True):
        """
        Plot the data at the selected keys. The function returns the matplotlib.axes on which it was ploted

        Parameters
        ----------
        key:                str
                            The key corresponding to the column to be plotted on the y axis

        x_key:              str, default: 'timestamp'
                            The key corresponding to the column to be plotted on the x axis.
        datetime_plot:      boolean, default: True
                            Plots formatted datetimes on x axis if x_key is 'timestamp'
        date_format:        boolean, default: '%m-%d %H:%M:%S'
                            Format used to format the datetimes
        timezone:           str, default: 'Europe/Stockholm'
                            Timezone used to format the datetimes
        ax:                 {None, matplotlib.axes}, default: None
                            The matplotlib axes on which to plot. If None, a new figure is created
        marker:             marker style string, default: None
        linestyle:          {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}, default: '-'
        color:              default: 'k'
        label:              str, default: None
                            The label of the plot
        scaling_factor_y:   float, default: 1.0
                            The value plotted on the y axis will be multiplied by this number

        Returns
        -------
        ax: matplotlib.axes
            The matplotlib axes on which the data was plotted
        """
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

        labels_dim = Utils.dim(labels)
        if len(labels_dim) == 0:
            if labels is not None: labels = [[labels]]
        elif len(labels_dim) == 1:
            labels = [labels]
        elif len(labels_dim) > 2:
            raise ValueError("The labels array should be a str, list of str, or list of lists of str!")

        ax_id_dim = Utils.dim(ax_id)
        if len(ax_id_dim) == 0:
            if ax_id is not None:   ax_id = [ax_id]*keys_dim[0]
        elif len(ax_id_dim) == 1:
            ax_id = ax_id
        else:
            raise ValueError("The ax_id array should be a int or list of int")

        marker = Utils.fix_parameter_list(keys, marker)
        linestyle = Utils.fix_parameter_list(keys, linestyle)
        color = Utils.fix_parameter_list(keys, color)
        linewidth = Utils.fix_parameter_list(keys, linewidth)
        markersize = Utils.fix_parameter_list(keys, markersize)

        default_color_index = 0


        # fix gaps between data corresponding to different files. A NaN value is added at the end of the data corresponding to each file.
            # Otherwise, in the plot, a line will brige the gap between the data corresponding to different neighbouring files
        x_data = Utils.fix_gaps_between_files(data, x_key)
        if datetime_plot and x_key == 'timestamp':
            date_formatter = DateFormatter(date_format, tz=tz.gettz(timezone))
            # plt.subplots_adjust(hspace=0, bottom=0.2)
            new_x = mdates.epoch2num(x_data)
        else:
            new_x = x_data

        for i in range(0, n_axes):
            if ax_id is None:
                current_ax = self.axs[i]
                current_ax_id = i
            else:
                current_ax = self.axs[ax_id[i]]
                current_ax_id = ax_id[i]

            if datetime_plot and x_key == 'timestamp':
                current_ax.xaxis.set_major_formatter(date_formatter)
                plt.setp(self.axs[0].xaxis.get_majorticklabels(), rotation=70)

            for j in range(0, len(keys[i])):
                current_color, current_linestyle, current_linewidth, current_marker, current_markersize = \
                    self.__get_style__(keys[i][j], color[i][j], linestyle[i][j], linewidth[i][j], marker[i][j], markersize[i][j], use_style_dict = use_style_dict)
                if labels is None:
                    label = data.info_dict[keys[i][j]]['label']
                else:
                    label = labels[i][j]
                y_data = Utils.fix_gaps_between_files(data, keys[i][j], add_nan = True)
                self.plot(new_x,  y_data, ax_id = current_ax_id, scaling_x = scaling_x, scaling_y = scaling_y, color = current_color, marker = current_marker, \
                    markersize = current_markersize, linestyle = current_linestyle, linewidth = current_linewidth, label = label, datetime_plot = False)

    def __get_style__(self, key, color, linestyle, linewidth, marker, markersize, use_style_dict = True):
        if use_style_dict and self.style_dict is not None:
            if key in self.style_dict:
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
            else:
                color = self.__get_next_color__()
                return color, linestyle, linewidth, marker, markersize
        elif color is None:
            new_color = self.__get_next_color__()
            return new_color, linestyle, linewidth, marker, markersize
        else:
            return color, linestyle, linewidth, marker, markersize
