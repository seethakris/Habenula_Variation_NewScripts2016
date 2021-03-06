from numpy import newaxis, size, where, array, mean, zeros, round, reshape, float16, delete, transpose, max, min, \
    repeat, shape
from scipy import stats
from numpy import asarray
import matplotlib.pyplot as plt
import seaborn as sns
from thunder import PCA
from thunder import Colorize
from mpl_toolkits.mplot3d import axes3d


class class_PCA(object):
    def __init__(self, pca_components, data, img_raw, num_pca_colors, num_samples, thresh_pca, color_map, color_mat,
                 stimulus_on_time, stimulus_off_time):

        self.pca_components = pca_components
        self.data = data
        self.num_pca_colors = num_pca_colors
        self.num_samples = num_samples
        self.thresh_pca = thresh_pca
        self.color_map = color_map
        self.color_mat = color_mat
        self.stimulus_on_time = stimulus_on_time
        self.stimulus_off_time = stimulus_off_time
        self.image = Colorize.image
        self.reference = mean(img_raw, 0)

    def run_pca(self, required_pcs):
        model = PCA(k=self.pca_components).fit(self.data)
        imgs = model.scores.pack()

        if required_pcs == 0:
            new_imgs = imgs
        else:
            if len(imgs.shape) == 3:
                new_imgs = imgs[required_pcs, :, :]
            else:
                new_imgs = imgs[required_pcs, :, :, :]

        return model, new_imgs

    # Make maps and scatter plots of the pca scores with colormaps for plotting
    def make_pca_maps(self, pca, imgs, required_pcs):

        maps = Colorize(cmap=self.color_map, scale=self.num_pca_colors).transform(imgs, background=self.reference,
                                                                                  mixing=1)
        pts = pca.scores.subset(self.num_samples, thresh=self.thresh_pca, stat='norm')

        if required_pcs == 0:
            pca_pts = list()
            for ii in xrange(0, size(pca.comps.T, 1)):
                pca_pts.append(pts[:, ii][:, newaxis])
            clrs = Colorize(cmap=self.color_map, scale=self.num_pca_colors).transform(pca_pts).squeeze()
        else:
            pca_pts = list()
            for ii in xrange(0, size(required_pcs)):
                pca_pts.append(pts[:, required_pcs[ii]][:, newaxis])
            clrs = Colorize(cmap=self.color_map, scale=self.num_pca_colors).transform(pca_pts).squeeze()

        # Reconstruct the scores using the pca components
        if required_pcs == 0:
            recon = asarray(
                map(lambda x: (x[0] * pca.comps[0, :] + x[1] * pca.comps[1, :] + x[2] * pca.comps[2, :]).tolist(), pts))
        else:
            pts_list = pts.tolist()
            recon = zeros((size(pts_list, 0), size(pca.comps, 1)))
            for ii in range(0, size(pts_list, 0)):
                for jj in range(0, size(required_pcs)):
                    recon[ii, :] += pts_list[ii][required_pcs[jj]] * pca.comps[required_pcs[jj], :]

        # Count number of unique colors in the images
        # Get number of planes based on map dimensions
        if len(maps.shape) == 3:
            num_planes = 1
        else:
            num_planes = size(maps, 2)
        num_time = size(pca.comps.T, 0)

        # Get specific color matches across animals and get mean and standard deviation
        array1 = [map(int, single_dim) for single_dim in clrs]  # Convert the colors to RGB integers
        new_array = [tuple(row) for row in array1]
        unique_clrs = list(set(new_array))  # Get unique combination of colors
        unique_clrs.remove((0, 0, 0))
        matches = [where((array(array1) == match).all(axis=1)) for match in
                   unique_clrs]  # Match the colors with the original rows

        matches_black = [where((array(array1) == match).all(axis=1)) for match in [0]]
        pts_nonblack = delete(pts, matches_black, axis=0)
        clrs_nonblack = delete(clrs, matches_black, axis=0)

        # From maps get number of pixel matches with color for each plane
        array_maps = round(maps.astype(float16))
        matched_pixels = zeros((size(unique_clrs, 0), num_planes))
        array_maps_plane = reshape(array_maps, (size(array_maps, 0) * size(array_maps, 1), 3))
        matched_pixels[:, 0] = [size(where((array(array_maps_plane) == match).all(axis=1))) for match in
                                unique_clrs]

        # Find stats based on the color - but only use the subset of pixels in recon
        matched_signals = [structtype() for i in range(size(matches, 0) * num_planes)]

        mean_signal = zeros((size(matches, 0), num_planes, num_time))
        sem_signal = zeros((size(matches, 0), num_planes, num_time))
        for ii in xrange(0, size(matches, 0)):
            temp_ele = array(matches[ii])
            matched_signals[ii].clr_grped_signal = [array(recon[ele]) for ele in temp_ele[0, :]]
            mean_signal[ii, :] = mean(matched_signals[ii].clr_grped_signal, axis=0)
            sem_signal[ii, :] = stats.sem(matched_signals[ii].clr_grped_signal, axis=0)

        return maps, pts_nonblack, clrs_nonblack, recon, unique_clrs, matched_pixels, \
               matched_signals

    def plot_vertical_lines_onset(self):
        for ii in xrange(0, size(self.stimulus_on_time)):
            plt.axvline(x=self.stimulus_on_time[ii], linestyle='-', color='k', linewidth=2)

    def plot_vertical_lines_offset(self):
        for ii in xrange(0, size(self.stimulus_off_time)):
            plt.axvline(x=self.stimulus_off_time[ii], linestyle='--', color='k', linewidth=2)

    def plot_pca_components(self, fig1, gs, pca_components, required_pcs, plot_title='Habneula', gridspecs='[0,0]'):
        ax1 = eval('fig1.add_subplot(gs' + gridspecs + ')')
        with sns.axes_style('darkgrid'):
            for ii in range(size(pca_components, 1)):
                if ii in required_pcs:
                    plt.plot(pca_components[:, ii], '-', linewidth=5, label=str(ii))
                else:
                    plt.plot(pca_components[:, ii], '--', label=str(ii))

            plt.title(plot_title, fontsize=14)
            sns.axlabel("Time (seconds)", "a.u")
            plt.locator_params(axis='y', nbins=4)
            sns.axlabel("Time (seconds)", "a.u")
            ax1.legend(prop={'size': 14}, loc='center left', bbox_to_anchor=(1, 0.5), ncol=1, fancybox=True,
                       shadow=True)
            plt.axhline(y=0, linestyle='-', color='k', linewidth=1)
            ax1.locator_params(axis='y', pad=50, nbins=2)
            plt.ylim((min(pca_components) - 0.0001, max(pca_components) + 0.0001))
            self.plot_vertical_lines_onset()
            self.plot_vertical_lines_offset()

    def plot_stimulus_in_3d(self, fig1, gs, pca_components, required_pcs, z_direction, gridspecs='[0,0]'):
        with sns.axes_style('darkgrid'):
            ax1 = eval('fig1.add_subplot(gs' + gridspecs + ', projection="3d")')

            # Plot Baseline at beginning
            ax1.plot(pca_components[0:self.stimulus_on_time[0], required_pcs[0]],
                     pca_components[0:self.stimulus_on_time[0], required_pcs[1]],
                     pca_components[0:self.stimulus_on_time[0], required_pcs[2]], zdir=z_direction, color='#808080',
                     linewidth=2)

            # Plot light on times
            for ii in xrange(0, size(self.stimulus_on_time)):
                ax1.plot(pca_components[self.stimulus_on_time[ii]:self.stimulus_off_time[ii], required_pcs[0]],
                         pca_components[self.stimulus_on_time[ii]:self.stimulus_off_time[ii], required_pcs[1]],
                         pca_components[self.stimulus_on_time[ii]:self.stimulus_off_time[ii], required_pcs[2]],
                         zdir=z_direction, color=self.color_mat[ii], linewidth=5)

            ## Plot Baseline at end of stimulus
            ax1.plot(pca_components[self.stimulus_off_time[ii] + 20:, required_pcs[0]],
                     pca_components[self.stimulus_off_time[ii] + 20:, required_pcs[1]],
                     pca_components[self.stimulus_off_time[ii] + 20:, required_pcs[2]], zdir=z_direction,
                     color='#000000', linewidth=2)

            # Plot light off times
            for ii in xrange(0, size(self.stimulus_on_time)):
                if ii == size(self.stimulus_on_time) - 1:
                    ax1.plot(
                        pca_components[self.stimulus_off_time[ii]:self.stimulus_off_time[ii] + 20, required_pcs[0]],
                        pca_components[self.stimulus_off_time[ii]:self.stimulus_off_time[ii] + 20, required_pcs[1]],
                        pca_components[self.stimulus_off_time[ii]:self.stimulus_off_time[ii] + 20, required_pcs[2]],
                        zdir=z_direction, color=self.color_mat[ii], linewidth=5, linestyle='--')
                else:

                    ax1.plot(pca_components[self.stimulus_off_time[ii]:self.stimulus_on_time[ii + 1], required_pcs[0]],
                             pca_components[self.stimulus_off_time[ii]:self.stimulus_on_time[ii + 1], required_pcs[1]],
                             pca_components[self.stimulus_off_time[ii]:self.stimulus_on_time[ii + 1], required_pcs[2]],
                             zdir=z_direction,
                             color=self.color_mat[ii], linewidth=5, linestyle='--')

            self.plot_axis_labels_byzdir(ax1, z_direction, required_pcs)
            self.legend_for_2d_plot(ax1)

            ax1.locator_params(axis='x', pad=50, nbins=2)
            ax1.locator_params(axis='y', pad=50, nbins=2)
            ax1.locator_params(axis='z', pad=50, nbins=2)
            ax1.set_ylim((min(pca_components), max(pca_components)))
            ax1.set_xlim((min(pca_components), max(pca_components)))
            ax1.set_zlim((min(pca_components), max(pca_components)))

    @staticmethod
    def plot_axis_labels_byzdir(ax1, z_direction, required_pcs):
        if z_direction == 'y':
            ax1.set_xlabel('PC' + str(required_pcs[0]), linespacing=10, labelpad=200)
            ax1.set_ylabel('PC' + str(required_pcs[2]), linespacing=10, labelpad=200)

            ax1.zaxis.set_rotate_label(False)  # disable automatic rotation
            ax1.set_zlabel('PC' + str(required_pcs[1]), rotation=90, linespacing=10, labelpad=200)

        elif z_direction == 'z':
            ax1.set_xlabel('PC' + str(required_pcs[0]), linespacing=10, labelpad=200)
            ax1.set_ylabel('PC' + str(required_pcs[1]), linespacing=10, labelpad=200)

            ax1.zaxis.set_rotate_label(False)  # disable automatic rotation
            ax1.set_zlabel('PC' + str(required_pcs[2]), rotation=90, linespacing=10, labelpad=200)

        elif z_direction == 'x':
            ax1.set_xlabel('PC' + str(required_pcs[1]), linespacing=10, labelpad=200)
            ax1.set_ylabel('PC' + str(required_pcs[2]), linespacing=10, labelpad=200)

            ax1.zaxis.set_rotate_label(False)  # disable automatic rotation
            ax1.set_zlabel('PC' + str(required_pcs[0]), rotation=90, linespacing=10, labelpad=200)

    def legend_for_2d_plot(self, ax1):
        A = []
        A.append('Start')
        for ii in xrange(0, size(self.stimulus_off_time)):
            A.append(str(ii))
        A.append('End')
        ax1.legend(A, loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=3, fancybox=True, framealpha=0.5)

    def plot_scores(self, fig1, gs, matched_signals, unique_clrs, plot_title='Habenula', gridspecs='[0,0]'):
        with sns.axes_style('dark'):
            ax1 = eval('fig1.add_subplot(gs' + gridspecs + ')')
            for ind in range(0, size(unique_clrs, 0)):
                sns.tsplot(array(matched_signals[ind].clr_grped_signal), linewidth=5, ci=95, err_style="ci_band",
                           color=unique_clrs[ind])
                ax1.locator_params(axis='y', nbins=4)
                sns.axlabel("Time (seconds)", "a.u")
                plt.title(plot_title, fontsize=14)
                self.plot_vertical_lines_onset()
                self.plot_vertical_lines_offset()
                plt.axhline(y=0, linestyle='-', color='k', linewidth=1)

    def plotimageplanes(self, fig1, gs, img, plot_title='Habenula', gridspecs='[0, 0]'):

        ax1 = eval('fig1.add_subplot(gs' + gridspecs + ')')
        ax1 = self.image(img)
        plt.title(plot_title, fontsize=14)

    @staticmethod
    def plot_eigenvalues(fig1, gs, pca_eigenvalues, gridspecs='[0, 0]'):

        # Plot eigenvalues
        ax1 = eval('fig1.add_subplot(gs' + gridspecs + ')')
        plt.plot(pca_eigenvalues, '*-')
        plt.title('Eigenvalues')
        ax1.locator_params(axis='x', nbins=size(pca_eigenvalues))
        ax1.locator_params(axis='y', nbins=2)

    @staticmethod
    def plot_matchedpixels(fig1, gs, matched_pixels, unique_clrs, gridspecs=[0, 0]):
        ax1 = eval('fig1.add_subplot(gs' + gridspecs + ')')
        with sns.axes_style("darkgrid"):
            for ii in xrange(0, size(matched_pixels, 0)):
                plt.plot(ii + 1, transpose(matched_pixels[ii, :]), 'o', color=unique_clrs[ii], markersize=10)
                plt.xlim([0, size(matched_pixels, 0) + 1])

            for ii in range(0, size(unique_clrs, 0)):
                plt.plot(repeat(ii + 1, size(matched_pixels, 1)), transpose(matched_pixels[ii, :]), 's',
                         color=unique_clrs[ii], markersize=10, markeredgecolor='k', markeredgewidth=2)

            x = range(0, size(unique_clrs, 0) + 1)
            labels = [str(e) for e in x]

            plt.xticks(x, labels, rotation='vertical')
            sns.axlabel("Colors", "Number of Pixels")
            sns.despine(offset=10, trim=True)


class structtype():
    pass
