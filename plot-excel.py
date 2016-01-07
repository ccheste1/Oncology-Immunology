import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import shutil

CSV_FILENAME = 'full.csv'
DATA_FRAME = pd.read_csv(CSV_FILENAME)
PHOSPHO_NAMES = list(DATA_FRAME[0:0])  # columns in CSV
STIMULATION_NAMES = ['unstim', 'ifna', 'il10', 'il21', 'il6', 'il7', 'lps', 'pma_iono']
STIMULATION_TOTAL = len(STIMULATION_NAMES)

def status(current_phospho, current_stim, total_images):
    """Utility to print current status of operation."""

    print '-' * 20
    print "Current Phospho: " + current_phospho
    print "Current Stim: " + current_stim
    print "Images: " + str(total_images) + '\n'

def create_dirs():
    """Create new dirs and flush old."""

    if os.path.exists('samples'):
        shutil.rmtree(os.getcwd() + '/samples/')

    os.makedirs('samples')

    for stimulation_dir in STIMULATION_NAMES:
        if not os.path.exists('samples'):
            os.makedirs('samples')

def print_sample(slices, phospho_name, stim_name, total_images):
    """Prints eight error bar standard deviation for current cell slice."""

    fig = plt.figure(figsize=(7,5))
    ax = fig.add_subplot(111)

    # print eight error bars for each single image
    for i in range(len(slices)):
        stimulation_label_length = STIMULATION_TOTAL * 10
        ax.scatter(slices[i]['x_error_bar'], slices[i]['mean'], zorder=1)
        ax.errorbar(slices[i]['x_error_bar'], slices[i]['y_error_bar'], yerr=[ [slices[i]['x_min']], [slices[i]['x_max']] ],
        linestyle='None', elinewidth=1.5, capsize=3, capthick=3,zorder=-1)
        plt.xticks(range(10, stimulation_label_length + 1, 10), STIMULATION_NAMES, size='small')

    plt.title(phospho_name)
    plt.ylabel('arcSine')
    image_name = 'samples/' + phospho_name + '.jpeg'
    fig.set_tight_layout(True)

    # adjust margins
    plot_margin = 3.0
    x0, x1, y0, y1 = plt.axis()
    plt.axis((x0 - plot_margin, x1 + plot_margin, y0, y1))
    plt.ylim([-1,5])

    fig.savefig(image_name)
    plt.close(fig)
    total_images += 1
    return total_images

def process_simulations():
    """Print 26 images for each of the 8 STIMULATION_NAMES (208 plots in total)."""

    total_images = 0
    # innner loop of 207 (209 - two title columns) phosphos
    for phospho in PHOSPHO_NAMES:
        # skip Aliquot and Stimulation columns
        if phospho == 'Aliquot' or phospho == 'Stimulation':
            continue
        else:
            # reset stim indices
            stim_start_idx = 0
            stim_end_idx = 0
            slice_metrics = []
            x_axis_offset = 10

            # process stimulation for each phospho
            for stim in STIMULATION_NAMES:

                stim_start_idx = stim_end_idx + 1  # for example, unstim = DATA_FRAME[1:121]
                stim_end_idx = stim_start_idx + 121

                stim_slice = DATA_FRAME[stim_start_idx:stim_end_idx]
                phospho_slice = stim_slice[phospho]

                result = {
                    "title": phospho,
                    "mean": pd.Series.mean(phospho_slice),
                    "std": np.std(phospho_slice),
                    "x_min": np.std(phospho_slice) - pd.Series.mean(phospho_slice),
                    "x_max": np.std(phospho_slice) + pd.Series.mean(phospho_slice),
                    "x_error_bar": x_axis_offset,
                    "y_error_bar": -0.0009 # TODO: correct y_error_bar
                }

                # list of stimulations; will be printed once we have eight phosphos
                slice_metrics.append(result)
                x_axis_offset += 10

            # print and proceed to next phospho. update total_images
            total_images = print_sample(slice_metrics, phospho, stim, total_images)

    return total_images

def main():
    print 'Creating dirs...'
    create_dirs()

    print 'Creating images in samples/...'
    total_images = process_simulations()

    print 'Finished. Image total: ' + str(total_images)

if __name__ == '__main__':
    main()
