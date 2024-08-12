import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from pylab import *
import os
import glob
from scipy.interpolate import interp1d
import csv
import re

plt.rcParams['axes.unicode_minus'] = False
# Initialization
debug = 1
d = 0.32
freq_min = 120
freq_max = 150


def split_string(s, delimiters):
    # Create a regular expression pattern for the delimiters
    pattern = '|'.join(map(re.escape, delimiters))

    # Use re.split to split the string based on the pattern
    return re.split(pattern, s)

my_dir = ""
my_subdir = "VDI_mixer_30cm\\"

# Load calibration receiver power
lo_freq = [135]
freq_rec_power = []
rec_power = []
for index in lo_freq:
    # Construct file paths
    file_lo = f'{my_dir}{my_subdir}RX_IF_LI_{index}.csv'
    file_hi = f'{my_dir}{my_subdir}RX_IF_HI_{index}.csv'

    # Read CSV files into DataFrames and convert to numpy arrays
    tmp_lo = pd.read_csv(file_lo, header=None).values.T
    tmp_hi = pd.read_csv(file_hi, header=None).values.T

    # Calculate freq_rec_power and rec_power and append to lists
    freq_rec_power_temp = np.concatenate([-1 * np.flip(tmp_lo[0, :]), tmp_hi[0, :]])
    freq_rec_power_temp += index  # Adding index to each element

    rec_power_temp = np.concatenate([np.flip(tmp_lo[1, :]), tmp_hi[1, :]])

    # Append results to lists
    freq_rec_power.append(freq_rec_power_temp)
    rec_power.append(rec_power_temp)

# Convert lists to numpy arrays if needed
# Convert lists to numpy arrays and then flatten to 1D arrays
freq_rec_power = np.concatenate(freq_rec_power).flatten()
rec_power = np.concatenate(rec_power).flatten()

# Load reference power data
file = f'{my_dir}{my_subdir}extender_power.xlsx'
tmp = pd.read_excel(file).values.T
freq_ref_power_course = tmp[0, :]
ref_power_course = tmp[1, :]

# Load OE gain data
file = f'{my_dir}{my_subdir}OE_gain.csv'
tmp = pd.read_csv(file).values.T
freq_oe_gain = tmp[0, :]
oe_gain_smooth = tmp[1, :]
oe_gain_actual = tmp[2, :]

# Load horn gain data
file = f'{my_dir}{my_subdir}horn_gain.csv'
tmp = pd.read_csv(file).values.T
freq_horn_gain = tmp[0, :]
horn_gain_smooth = tmp[1, :]
horn_gain_actual = tmp[2, :]

# Define frequency range and interpolate data
freq = np.arange(freq_min, freq_max, 0.25)
fspl = -20 * np.log10(d * freq * 10 * 4 * np.pi / 3)

interp_rec_power = interp1d(freq_rec_power, rec_power, kind='cubic', fill_value="extrapolate")
rec_power = interp_rec_power(freq)

interp_ref_power = interp1d(freq_ref_power_course, ref_power_course, kind='cubic', fill_value="extrapolate")
ref_power = interp_ref_power(freq)

interp_oe_gain = interp1d(freq_oe_gain, oe_gain_actual, kind='cubic', fill_value="extrapolate")
oe_gain = interp_oe_gain(freq)

interp_horn_gain = interp1d(freq_horn_gain, horn_gain_actual, kind='cubic', fill_value="extrapolate")
horn_gain = interp_horn_gain(freq)

path_loss = rec_power - (ref_power + oe_gain)

# print(path_loss)

# Load DUT data
my_subdir = ""

csv_files = glob.glob(os.path.join(my_dir, my_subdir, 'TX_RF_2024*.csv'))

# Plotting
# plt.figure()
plt.style.use(['science','ieee','no-latex'])
fig_eirp, ax1 = plt.subplots()
fig_imrr, ax2 = plt.subplots()
# Print the file names
curr_max = -100
curr_max_imrr = -100
curr_argmax = 0
curr_argmax_imrr = 0
for i,file in enumerate(list(csv_files)):
    print(os.path.basename(file))

    file_name_parse = os.path.basename(file)
    file_name_parse = split_string(file_name_parse,['_','.'])

    # file = f'{my_dir}{my_subdir}RX_RF_20240724_1739.csv'
    tmp = pd.read_csv(file).values
    print(tmp.shape)
    if tmp.shape[0] > tmp.shape[1]:
        tmp = tmp.transpose()
    print(tmp[4, :])
    print(tmp[5, :])
    freq_rec_pw = tmp[0, :]
    rec_pw_lo = tmp[4, :]
    rec_pw_hi = tmp[5, :]
    rec_pw = 10*np.log10(10**(rec_pw_hi/10)+10**(rec_pw_lo/10))
    imrr = np.abs(rec_pw_hi - rec_pw_lo)
    print(rec_pw)
    # print(freq_rec_pw, rec_pw)
    # Calculate gain and convert to numpy array

    interp_eirp = interp1d(freq, path_loss, kind='cubic', fill_value="extrapolate")

    gain = rec_pw - interp_eirp(freq_rec_pw) + 3 # 3 dB due to the output balun
    gain = np.array(gain)

    # Calculate smoothed gain with moving average
    window_size = 1
    smoothed_gain = np.convolve(gain, np.ones(window_size)/window_size, mode='same')

    print(file_name_parse)
    file_name_write = '_'.join(file_name_parse[3:-1])
    my_subdir = 'eirp'
    os.makedirs(f'{my_dir}{my_subdir}', exist_ok=True)
    csv_name = f'TX_RFGAIN_{file_name_write}.csv'
    csv_path = os.path.join(my_dir, my_subdir, csv_name)

    with open(csv_path, 'w', newline='') as csvfile:
        print(csv_path)
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['freq']+ freq_rec_pw[0:len(freq_rec_pw)].tolist())
        csv_writer.writerow(['eirp']+ smoothed_gain[0:len(freq_rec_pw)].tolist())

    # EIRP
    line_max = smoothed_gain[window_size:len(freq_rec_pw)-window_size].max()
    if line_max > curr_max:
        curr_max = line_max
        curr_argmax = np.argmax(smoothed_gain[window_size:len(freq_rec_pw)-window_size])+window_size

    line_max_imrr = imrr.max()
    if line_max_imrr > curr_max_imrr:
        curr_max_imrr = line_max_imrr
        curr_argmax_imrr = np.argmax(imrr)

    label_name = ' '.join(file_name_parse[3:-1])
    # ax1.plot(freq_rec_pw, gain, label=f'{label_name}',linewidth=2*2, alpha=1) # non IEEE
    ax1.plot(freq_rec_pw, gain, label=f'{label_name}', alpha=1)  # IEEE
    # ax1.plot(freq_rec_pw[0:len(freq_rec_pw)-window_size], smoothed_gain[0:len(freq_rec_pw)-window_size], linewidth=2,
    # label=f'Smoothed {file_name_parse[-3]}')
    # ax2.plot(freq_rec_pw,imrr,label=f'{label_name}',linewidth=2*2, alpha=1)
    ax2.plot(freq_rec_pw, imrr, label=f'{label_name}', alpha=1) # IEEE

ax=plt.gca()
bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=40")
# kw = dict(xycoords='data',textcoords="axes fraction",
#           arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top",fontsize=12*2) # non IEEE
kw = dict(xycoords='data',textcoords="axes fraction",
          arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top",fontsize=6) # IEEE
ax1.annotate(f'Max EIRP = {curr_max:.2f} dB', xy=(freq_rec_pw[curr_argmax], curr_max), xytext=(0.94,0.96), **kw)
print(curr_argmax, curr_max)

# ax1.axhline(y=curr_max, color='r', linestyle='--')
# ax1.tick_params(labelsize = 28*2)
# ax1.set_xlabel('Freq [GHz]',fontsize=30*2)
# ax1.set_ylabel('Transmitter EIRP [dB]',fontsize=30*2)
# ax1.grid(True,linestyle='--', dashes=(5, 10))
# ax1.legend(loc='lower center', fontsize=14*2)
ax1.axhline(y=curr_max, linestyle='--')
ax1.set_xlabel('Freq [GHz]')
ax1.set_ylabel('Transmitter EIRP [dB]')
ax1.grid(True,linestyle='--',alpha=0.5)
ax1.legend(loc='lower center')

xaxis_range = [int(freq_rec_pw[0]), int(freq_rec_pw[-1])]
xticks = np.arange(xaxis_range[0], xaxis_range[1], 5)  # Ticks with a step of 20
ax1.set_xticks(xticks)
yaxis_range = [-60, curr_max+20]

yticks = np.arange(yaxis_range[0]+10, yaxis_range[1]-10, 20)  # Ticks with a step of 20
ax1.set_yticks(yticks)
ax1.set_yticklabels([str(tick) for tick in yticks])

ax1.axis([freq_rec_pw[0]-2,freq_rec_pw[-1]+2,yaxis_range[0],yaxis_range[1]])

# ax2 = ax1.twiny()
# scale_factor = 18
# new_x = freq_rec_pw / scale_factor

# Set the limits and ticks of the new x-axis
# ax2.set_xlim(ax1.get_xlim()[0] * scale_factor, ax1.get_xlim()[1] * scale_factor)
# ax2.set_xticks(ax1.get_xticks() * scale_factor)
# ax2.set_xticklabels([f'{tick/scale_factor:.2f}' for tick in ax1.get_xticks()],fontsize=28)
# ax2.set_xlabel('LO subharmonic frequency at input [GHz]',fontsize=30)

plt.show(block=False)

ax2=plt.gca()
# kw2 = dict(xycoords='data',textcoords="axes fraction",
#           arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top",fontsize=12*2)
kw2 = dict(xycoords='data',textcoords="axes fraction",
          arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top",fontsize=6)
ax2.annotate(f'Max IMRR = {curr_max_imrr:.2f} dB', xy=(freq_rec_pw[curr_argmax_imrr], curr_max_imrr), xytext=(0.94,0.96), **kw2)
print(curr_argmax_imrr, curr_max_imrr)

# ax2.axhline(y=curr_max_imrr, color='r', linestyle='--')
# ax2.tick_params(labelsize = 28*2)
# ax2.set_xlabel('Freq [GHz]',fontsize=30*2)
# ax2.set_ylabel('Transmitter IMRR [dB]',fontsize=30*2)
# ax2.grid(True,linestyle='--', dashes=(5, 10))
# ax2.legend(loc='lower center', fontsize=14*2)
ax2.axhline(y=curr_max_imrr, linestyle='--')
ax2.set_xlabel('Freq [GHz]')
ax2.set_ylabel('Transmitter IMRR [dB]')
ax2.grid(True,linestyle='--',alpha=0.5)
ax2.legend(loc='lower center')

xaxis_range = [int(freq_rec_pw[0]), int(freq_rec_pw[-1])]
xticks = np.arange(xaxis_range[0], xaxis_range[1], 5)  # Ticks with a step of 20
ax2.set_xticks(xticks)
yaxis_range = [-40, curr_max_imrr+20]

yticks = np.arange(yaxis_range[0]+10, yaxis_range[1]-10, 20)  # Ticks with a step of 20
ax2.set_yticks(yticks)
ax2.set_yticklabels([str(tick) for tick in yticks])

ax2.axis([freq_rec_pw[0]-2,freq_rec_pw[-1]+2,yaxis_range[0],yaxis_range[1]])

plt.show()
