__author__ = 'seetha'
import matplotlib.pyplot as plt
from numpy import size
import seaborn as sns

class FormatForPlotting(object):
    """
    Many functions for efficient plotting. Call them as decorators or
    separate functions. Mainly suited for a black background
    """

    def __init__(self, stimulus_on_time, stimulus_off_time):
        self.stimulus_on_time = stimulus_on_time
        self.stimulus_off_time = stimulus_off_time

    def heatmapplotting(self, ax1, xlabel='Time(seconds)', ylabel='Pixels', **kwargs):
        """
        Plot formatted heatmaps. Fix axis labels, font size, x and y limits, font color etc

        Parameters:
        ax1 : axis instance
        xlabel : x axis label
        ylabel : y axis label

        Optional Arguments:
        xlim_input : x limit
        ylim_input : y limit
        num_bins : number of tick locations

        """

        for key, value in kwargs.iteritems():
            if key == 'xlim_input':
                ax1.set_xlim(value)
            if key == 'num_bins':
                ax1.locator_params(axis='y', nbins=value)
            if key == 'ylim_input':
                ax1.set_ylim(value)

        ax1.title.set_color('white')
        ax1.grid('off')
        ax1.yaxis.label.set_color('white')
        ax1.xaxis.label.set_color('white')
        ax1.tick_params(axis='both', colors='white',
                        direction='out', labelsize=15)
        ax1.get_xaxis().tick_bottom()
        ax1.get_yaxis().tick_left()
        ax1.set_xlabel(xlabel, fontsize=15)
        ax1.set_ylabel(ylabel, fontsize=15)

        self.plot_vertical_lines_onset()
        self.plot_vertical_lines_offset()


    def linegraphplotting(self, ax1, xlabel='Time(seconds)', ylabel='Average Raw Trace', **kwargs):
        """
        Plot formatted line plots. Fix axis labels, font size, x and y limits, font color etc

        Parameters:
        ax1 : axis instance
        xlabel : x axis label
        ylabel : y axis label

        Optional Arguments:
        xlim_input : x limit
        ylim_input : y limit
        num_bins : number of tick locations

        """
        current_palette = sns.color_palette()
        ax1.set_color_cycle(current_palette)

        for key, value in kwargs.iteritems():
            if key == 'xlim_input':
                ax1.set_xlim(value)
            if key == 'num_bins':
                ax1.locator_params(axis='y', nbins=value)
            if key == 'ylim_input':
                ax1.set_ylim(value)

        for loc, spine in ax1.spines.items():
            spine.set_color('white')
            spine.set_linewidth(0.5)

        ax1.title.set_color('white')
        ax1.yaxis.label.set_color('white')
        ax1.xaxis.label.set_color('white')
        ax1.tick_params(axis='both', colors='white',
                        direction='out', labelsize=15)
        ax1.get_xaxis().tick_bottom()
        ax1.get_yaxis().tick_left()

        ax1.set_xlabel(xlabel, fontsize=15)
        ax1.set_ylabel(ylabel, fontsize=15)

        self.plot_vertical_lines_onset()
        self.plot_vertical_lines_offset()


    def plot_vertical_lines_onset(self):
        for ii in xrange(0, size(self.stimulus_on_time)):
            plt.axvline(x=self.stimulus_on_time[ii], linestyle='-', color='k', linewidth=2)

    def plot_vertical_lines_offset(self):
        for ii in xrange(0, size(self.stimulus_off_time)):
            plt.axvline(x=self.stimulus_off_time[ii], linestyle='--', color='k', linewidth=2)
