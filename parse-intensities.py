from pathlib import Path
import numpy as np
import h5py as h5 
import sys
import matplotlib.pyplot as plt
import os
from typing import List
from multiprocessing import Pool

def process_dataset(name: str) -> tuple:
    """
    Process a dataset by accumulating non-zero intensity values from each .h5 file.
    """
    h5_dir = os.path.join(base_dir, name)
    non_zero_intensities = []
    file_count = 0

    try:
        files = [f for f in os.listdir(h5_dir) if f.endswith('.h5')]
        file_count = len(files)
        for filename in files:
            file_path = os.path.join(h5_dir, filename)
            with h5.File(file_path, 'r') as f:
                data = np.array(f['entry/data/data'])
                non_zeros = data[data != 0]
                non_zero_intensities.extend(non_zeros) # add to end of list
    except Exception as e:
        print(f'Failed to process files in {h5_dir}: {str(e)}')
        return name, [], file_count, str(e)
    # return tuple anyways when processing successful
    return name, non_zero_intensities, file_count, None

def plot_combined_hist(base_dir: str, dataset_names: List[str], plot_name: str):
    """
    Plot individual and combined histograms of non-zero intensities from multiple datasets.
    """
    if len(dataset_names) < 1:
        print("Usage: python parse-intensities.py <dataset1> [dataset2 ...] <plot_name>")
        sys.exit(1)
    
    with Pool(processes=len(dataset_names)) as pool:
        results = pool.map(process_dataset, dataset_names)
    
    # Initialize figure for subplots with shared axis scales
    fig, axes = plt.subplots(nrows=len(dataset_names)+1, ncols=1, figsize=(10, 6*len(dataset_names)),
                             sharex=True, sharey=True)

    # Create a color map that is consistent across all plots
    color_map = {name: plt.cm.viridis(i / len(dataset_names)) for i, name in enumerate(dataset_names)}

    # Determine global min and max non-zero intensities
    global_min = min(min(intensities) for _, intensities, _, _ in results if intensities)
    global_max = max(max(intensities) for _, intensities, _, _ in results if intensities)
    
    # Plot individual histograms
    for (name, intensities, file_count, error), ax in zip(results, axes[:-1]):
        if error:
            print(f"Error processing {name}: {error}")
            continue
        color = color_map[name]
        label = f"{Path(name).stem} (Files: {file_count})"
        ax.hist(intensities, bins=100, color=color, alpha=0.5, log=True, label=label)
        ax.legend()
        ax.set_xlim(left=global_min, right=global_max)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("Intensity of Peaks")
        ax.set_ylabel("Occurrences Across Images")

    # Plot combined histogram
    combined_ax = axes[-1]
    for name, intensities, file_count, error in results:
        if error:
            continue
        color = color_map[name]
        label = f"{Path(name).stem} (Files: {file_count})"
        combined_ax.hist(intensities, bins=100, color=color, alpha=0.5, log=True, label=label)

    combined_ax.legend()
    combined_ax.set_xlim(left=global_min, right=global_max)
    combined_ax.set_xscale('log')
    combined_ax.set_yscale('log')
    combined_ax.set_xlabel("Intensity of Peaks")
    combined_ax.set_ylabel("Occurrences Across Images")
    combined_ax.set_title("Combined " + plot_name)

    plt.tight_layout()
    plt.savefig(f"{plot_name}_intensities_combined.png")
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python parse-intensities.py <dataset1> [dataset2 ...] <plot_name>")
        sys.exit(1)

    base_dir = '/bioxfel/user/amkurth/'
    dataset_names = sys.argv[1:-1]
    plot_name = sys.argv[-1]

    plot_combined_hist(base_dir=base_dir, dataset_names=dataset_names, plot_name=plot_name)
