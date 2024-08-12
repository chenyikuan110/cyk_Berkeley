from array import array
import numpy as np
import matplotlib.pyplot as plt

# Specify the path to your binary file
path = "7G750M_500M_LinearFM.bin"

# Read the binary file into a NumPy array (dtype='B' for bytes)
num_array = np.fromfile(path, dtype=np.int8)
plot_length = 1024

f_sample = 64e9
f_center = 7.75 # GHz
f_chirp = 500 # MHz

print(num_array.size)
# offset = int(len(num_array)/2)
offset = int(num_array.size * 10 / 11 - plot_length)
print(str(offset/2 * (1 / f_sample) * 1e6) + 'us')

# plot every other number, since the data is I,Q,I,Q,I,Q,I,Q... interleaved and we only have I-channel
a1 = num_array[1:plot_length:2]
a2 = np.zeros(50)
a3 = num_array[(offset + 1):(offset + plot_length):2]

to_plot = np.concatenate([a1, a2, a3])
print(to_plot)

plt.plot(to_plot, color='b')
plt.title('%.2fGHz center, %.2fMHz frequency sweep Linear FM AWG\n first %d sample vs last %d sample' % (
f_center, f_chirp, plot_length / 2, plot_length / 2))
plt.show()
