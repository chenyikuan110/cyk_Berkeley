import csv
import numpy as np
import matplotlib.pyplot as plt

# Prepare serial read parameters
array_length = 128
bytes_per_number = 2
num_channels = 1
transmit_length = array_length * bytes_per_number * num_channels

# prepare data container and empty plot
plot_length = array_length
fig, ax = plt.subplots(nrows=4, ncols=1)

# For comparison
I_data = np.zeros(array_length)

# print(I_data)
for i in range(array_length):
    I_data[i] = int(np.sin(2 * np.pi * i / array_length /4) * 32767)


for j in range(4):
    ax[j].clear()
    # ax[j].stem(range(0,plot_length,2**j),I_data[range(0,plot_length,2**j)], label='ROM size '+str(int(array_length/2**j)),markerfmt='o')
    ax[j].stem(range(0, int(plot_length/2 ** j)), I_data[range(0, plot_length, 2 ** j)],
               label='ROM size ' + str(int(array_length / 2 ** j)), markerfmt='o')
    ax[j].set_xlim(0, int(plot_length))
    ax[j].set_ylim(-10, 35767)
    ax[j].legend(loc='lower center')

fig.suptitle('ROM size for sine wave')
fig.tight_layout()
plt.show()

# print(I_received_matrix)
# print(Q_received_matrix)
print(">>Done")
