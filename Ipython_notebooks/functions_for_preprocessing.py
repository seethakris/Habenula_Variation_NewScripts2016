from numpy import size, shape, mean, shape, convolve, r_, ones
import math
import matplotlib.pyplot as plt
from thunder import Colorize
import seaborn as sns


class class_preprocess_data(object):
    # Create many functions for data analysis of images using thunder

    def __init__(self, time_baseline, stimulus_on_time, stimulus_off_time):

        self.image = Colorize.image
        self.time_baseline = time_baseline
        self.stimulus_on_time = stimulus_on_time
        self.stimulus_off_time = stimulus_off_time

    def load_and_preprocess_data(self, tsc, FileName):

        # Load data and do a bit of preprocessing
        data = tsc.loadImages(FileName, inputFormat='tif')
        data = data.medianFilter(size=4)
        data = data.toTimeSeries()

        return data

    def detrend_data(self, data, detrend_order=10):
        data = data.detrend(method='linear', order=detrend_order)
        return data

    def plotimageplanes(self, fig1, img, plot_title='Habenula', num_subplots=1):

        # If image has more than one plane, calculate number of subplots and plot
        if len(shape(img)) > 2:
            numz = size(img, 2)
            num_subplots = int((math.ceil(numz / 2.) * 2) / 2)
            for ii in xrange(0, numz):
                ax1 = fig1.add_subplot(num_subplots, 2, ii + 1)
                self.image(img[:, :, ii])
                plt.title(plot_title, fontsize=14)

        else:  # If single plane, get user defined subplot number for plotting
            ax1 = fig1.add_subplot(2, 2, num_subplots)
            ax1 = self.image(img)
            plt.title(plot_title, fontsize=14)

    def normalize(self, data, squelch_parameter=80):
        # squelch to remove noisy pixels, normalize using user defined baseline
        print 'Baseline being used for normalizing is ...', self.time_baseline[0], ' to ', self.time_baseline[1]
        zscore_data = data.squelch(squelch_parameter).zscore(axis=1, baseline=self.time_baseline)
        zscore_data.cache()
        # zscore_data.dims

        return zscore_data

    # Performs smoothing using a hanning window on the rdd data
    @staticmethod
    def smooth_func(x, window_len=10):
        s = r_[x[window_len - 1:0:-1], x, x[-1:-window_len:-1]]
        #         w = np.hanning(window_len)
        w = ones(window_len, 'd')
        y = convolve(w / w.sum(), s, mode='valid')
        # print 'Size of y...', shape(y)
        return y[window_len / 2:-window_len / 2 + 1]

    def get_small_subset_for_plotting(self, data, number_samples=100, threshold=3):
        # Find a subset for plotting
        examples = data.subset(nsamples=number_samples, thresh=threshold)
        return examples

    def plot_traces(self, fig1, plotting_data, num_subplots, **kwargs):
        # Data : rows are cells, column is time
        with sns.axes_style('darkgrid'):
            ax1 = fig1.add_subplot(2, 2, num_subplots)
            plt.plot(plotting_data.T)
            plt.plot(mean(plotting_data, 0), 'k', linewidth=2)
            if 'plot_title' in kwargs:
                plt.title(kwargs.values()[0], fontsize=14)
            self.plot_vertical_lines_onset()
            self.plot_vertical_lines_offset()

    def plot_vertical_lines_onset(self):
        for ii in xrange(0, size(self.stimulus_on_time)):
            plt.axvline(x=self.stimulus_on_time[ii], linestyle='-', color='k', linewidth=2)

    def plot_vertical_lines_offset(self):
        for ii in xrange(0, size(self.stimulus_off_time)):
            plt.axvline(x=self.stimulus_off_time[ii], linestyle='--', color='k', linewidth=2)
