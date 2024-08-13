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
# plot every other number, since the data is I,Q,I,Q,I,Q,I,Q... interleaved and we only have Q-channel (why)
I_data = num_array[0::2]
Q_data = num_array[1::2]

# offset = int(len(num_array)/2)
offset = int(Q_data.size * 10 / 11 - plot_length/2)
print(str(offset/2 * (1 / f_sample) * 1e6) + 'us')


a1 = Q_data[0:int(plot_length/2)]
a2 = np.zeros(50)
a3 = Q_data[(offset):(offset + int(plot_length/2))]

to_plot = np.concatenate([a1, a2, a3])
print(to_plot)

plt.plot(to_plot, color='b')
plt.title('%.2fGHz center, %.2fMHz frequency sweep Linear FM AWG\n first %d sample vs last %d sample' % (
f_center, f_chirp, plot_length / 2, plot_length / 2))
plt.show()

FFT_result = np.fft.fft(Q_data)/len(Q_data)
N_decimate = 1000
N_cut = 4
N_stop = int(np.floor(len(FFT_result)/N_cut))
print(N_stop)
plot_result = FFT_result[:N_stop:N_decimate]
# plot_result = num_array[0:N_stop:N_decimate]
# plot_result = num_array
print(plot_result[0:1000:100])
fig, ax = plt.subplots()
ax.plot(np.linspace(0,f_sample/N_cut,len(plot_result))/1E9,20*np.log10(np.abs(plot_result)))
# ax.plot(np.linspace(0,f_sample/N_cut,len(plot_result))/1E9,((plot_result)))
ax.set_xlabel('GHz')
plt.title('FFT Results of first 1/%d' % N_cut)
plt.show()
