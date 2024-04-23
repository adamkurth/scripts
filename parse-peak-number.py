import numpy as np
import h5py
import sys
import matplotlib.pyplot as plt
import os

Names = (sys.argv[1], sys.argv[2] , sys.argv[3])     
Name_for_plot = sys.argv[4]

all_results = [] 
for Name in Names:
    h5_Directory = '/bioxfel/user/amkurth/' + str(Name)
    result = []
    counter = 0
    total_peaks=[]


    for filename in os.listdir(h5_Directory):
    #print(filename)
        if filename.endswith('.h5'):
            filepath = os.path.join(h5_Directory, filename)
            with h5py.File(filepath, 'r') as f:
                value_counts = []
                dataset = f['entry']
                data1 = dataset['data']
                data = data1['data']
                array_2d = np.array(data)
                non_zero_values, occurences = np.unique(array_2d[array_2d != 0], return_counts=True)
                value_counts = np.column_stack((non_zero_values, occurences))
                print(non_zero_values, occurences)
                peaks = np.sum(occurences, axis=0)
                total_peaks.append(peaks)
    #print(total_peaks)
    #print(value_counts)
                result = (result, value_counts)
    #print(np.shape(result))
    #result_array = np.array(result, dtype=object)
                counter +=1
    #if counter == 10:
    # print(result_array)
    check = int(np.size(total_peaks))
    print(counter, check)
    #print(check)
    if check < counter:
        num_zeros = counter - check
        total_peaks = np.pad(total_peaks, (0, num_zeros), mode='constant')
    all_results.append(total_peaks)
plt.hist(all_results[0], bins=10, color='blue', alpha=0.5, label='5e5')
plt.hist(all_results[1], bins=10, color='green',alpha=0.5, label='1e6')
plt.hist(all_results[2], bins=10, color='orange',alpha=0.5, label='4e6')
#plt.hist(all_results[3], bins=10, colour='red')
plt.legend()
plt.xlabel("# of peaks")
plt.ylabel("# of images")
plt.title(str(Name_for_plot))
plt.savefig(str(Name_for_plot) + '_numPeaks.png')

plt.show()
#                    break

