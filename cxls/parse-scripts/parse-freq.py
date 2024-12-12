from pathlib import Path
import numpy as np
import h5py as h5
import sys
import matplotlib.pyplot as plt
import os
from typing import List
from multiprocessing import Pool

def process_dataset(name:str) -> tuple:
    """
    Process a dataset by calculating the total number of peaks in each file.

    Args:
        name (str): The name of the dataset.

    Returns:
        tuple: A tuple containing the name of the dataset, a list of total peaks for each file,
               the total number of files processed, and an error message if any.
    """
    h5_dir = os.path.join(base_dir, name)
    total_peaks = []
    file_count = 0

    try:
        files = [f for f in os.listdir(h5_dir) if f.endswith('.h5')]
        file_count = len(files)
        for filename in files:
            file_path = os.path.join(h5_dir, filename)
            with h5.File(file_path, 'r') as f:
                data = np.array(f['entry/data/data'])
                _, freq = np.unique(data[data != 0], return_counts=True)
                total_peaks.append(np.sum(freq))
    except Exception as e:
        print(f'Failed to process files in {h5_dir}: {str(e)}')
        return name, total_peaks, file_count, str(e)

    return name, total_peaks, file_count, None

def plot_combined_hist(base_dir: str, dataset_names: List[str], plot_name: str):
    """
    Plot a combined histogram of the frequency of peaks in multiple datasets.

    Args:
        base_dir (str): The base directory where the datasets are located.
        dataset_names (List[str]): A list of dataset names.
        plot_name (str): The name of the plot.

    Returns:
        None
    """
    if len(dataset_names) < 1:
        print("Usage: python parse-freq.py <dataset1> [dataset2 ...] <plot_name>")
        sys.exit(1)
    
    with Pool(processes=len(dataset_names)) as pool:
        results = pool.map(process_dataset, dataset_names)
    
    all_results, labels = [], []
    plt.figure(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(dataset_names)))

    for result, color in zip(results, colors):
        name, total_peaks, file_count, error = result
        if error:
            continue
        all_results.append(total_peaks)
        labels.append(f"{Path(name).stem} (Files: {file_count})")
        plt.hist(total_peaks, bins=10, color=color, alpha=0.5, label=Path(name).stem + f" (Files: {file_count})")

    plt.legend()
    plt.xlabel("Frequency of Peaks")
    plt.ylabel("Frequency of Images")
    plt.title(plot_name)
    plt.savefig(f"{plot_name}_combined_histogram.png")
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python parse-freq.py <dataset1> [dataset2 ...] <plot_name>")
        sys.exit(1)
    base_dir = '/bioxfel/user/amkurth/'
    dataset_names = sys.argv[1:-1]
    plot_name = sys.argv[-1]

    plot_combined_hist(base_dir=base_dir, dataset_names=dataset_names, plot_name=plot_name)
