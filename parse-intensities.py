import numpy as np
import h5py
import sys
import matplotlib.pyplot as plt
import os

Names = str((sys.argv[1]))     
Name_plot = sys.argv[1]

all_results = [] 
for Name in Names:
    h5_Directory = '/bioxfel/user/amkurth' + str(Name)
    non_zero_values = []
#    counter = 0
#    total_peaks=[]
        

    for filename in os.listdir(h5_Directory):
    #print(filename)
        if filename.endswith('.h5'):
            print(filename) 
            filepath = os.path.join(h5_Directory, filename)
            print(filepath) 
            with h5py.File(filepath, 'r') as f:
                value_counts = []
                dataset = f['entry']
                data1 = dataset['data']
                data = data1['data']
                array_2d = np.array(data)
                non_zero_values = np.concatenate((non_zero_values, (array_2d[array_2d != 0])))
    all_results.append(non_zero_values)
    first_array = all_results[0]
    #print(first_array)
plt.hist(all_results[0], bins=10, color='blue', alpha=0.5, label='5e5')
plt.hist(all_results[1], bins=10, color='green',alpha=0.5, label='1e6')
plt.hist(all_results[2], bins=10, color='orange',alpha=0.5, label='4e6')
#plt.hist(all_results[3], bins=10, colour='red')
plt.legend()
plt.xlabel("intensity of peaks")
plt.ylabel("occurences across images")
plt.xscale('log')
plt.yscale('log')
plt.title(str(Name_plot))
plt.savefig(str(Name_plot) + '-intensities.png')

plt.show()
#                    break

