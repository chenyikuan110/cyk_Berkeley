import numpy as np
import matplotlib.pyplot as plt

path = "../PuTTY_log/test_20240317182242.hex"
# Assume you have a file named 'sample.hex' with hex values
array_length = 512
bytes_per_number = 2
num_channels = 2
transmit_length = array_length * bytes_per_number * num_channels

# Prepare byte-to-integer conversion
dt = np.dtype(np.int16)
dt = dt.newbyteorder('>')

count = 0
buffer = bytearray(b'x00\x00\x00\x00')
with open(path, 'rb') as hex_file:
    for line in hex_file:
        # Remove any leading/trailing whitespace

        result = np.frombuffer(line, dtype=np.uint8)
        for i, bytes in enumerate(list(line)):
            # bits_string = '{:0{width}b}'.format(line[i], width=8)
            # print(i, bits_string, hex(reader[i]))
            # print(bits_string)
            buffer.append(bytes)
            print(bytes)
        print('end of line', count, i)
        count += 1


print(len(buffer))
len_even = int(int(len(buffer)/2)*2)
print(len_even)
# result = np.frombuffer(buffer[1:len_even+1], dtype=dt)
result = np.frombuffer(buffer[1:len_even+1], dtype=np.uint8)

Q_data = result[0:int(len_even/2):2]
I_data = result[1:int(len_even/2):2]

plot_length = int(len_even/16)

fig, ax = plt.subplots(nrows=1, ncols=1)
ax.plot(I_data[0:plot_length], label='FFT_out_real')
ax.plot(Q_data[0:plot_length], label='FFT_out_imag')

ax.set_title('%d-th frame results I and Q' % count)
ax.legend(loc='lower center')
ax.set_xlim(0, plot_length)

fig.tight_layout()
plt.show()

plt.pause()
print(1)