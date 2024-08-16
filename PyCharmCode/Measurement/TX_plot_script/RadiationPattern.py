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

plt.style.use(['science','no-latex'])
# plt.rcParams.update({
#     'font.size': 14,  # Base font size
#     'axes.titlesize': 16,  # Title font size
#     'axes.labelsize': 14,  # X and Y label font size
#     'xtick.labelsize': 12,  # X tick label font size
#     'ytick.labelsize': 12,  # Y tick label font size
#     'legend.fontsize': 12,  # Legend font size
# })


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

# angle array
angles = np.linspace(-180, 179.5, 720)

# print(path_loss)

# Load DUT data
my_subdir = "Rad/Theta"

csv_files = glob.glob(os.path.join(my_dir, my_subdir, 'TX_Rad*.csv'))

# Plotting
# plt.figure()

fig_eirp, ax1 = plt.subplots(subplot_kw={'projection': 'polar'})
# Print the file names
curr_max = -100
curr_max_imrr = -100
curr_argmax = 0
curr_argmax_imrr = 0
for i,file in enumerate(list(csv_files)):
    print(os.path.basename(file))

    file_name_parse = os.path.basename(file)
    file_name_parse = split_string(file_name_parse,['_'])

    # file = f'{my_dir}{my_subdir}RX_RF_20240724_1739.csv'
    tmp = pd.read_csv(file).values
    print(tmp.shape)
    if tmp.shape[0] > tmp.shape[1]:
        tmp = tmp.transpose()
    angle_rec_pw = tmp[0, :]
    rec_pw = tmp[1,:]
    print(angle_rec_pw)
    # print(freq_rec_pw, rec_pw)
    # Calculate gain and convert to numpy array
    freq_string = file_name_parse[-2]
    pattern = r'\d+\.?\d*'
    match = re.search(pattern, freq_string)
    if match:
        freq_rec_pw = float(match.group())
    else:
        print("No number found in the string.")
        exit()
    print(freq_rec_pw)
    interp_eirp = interp1d(freq, path_loss, kind='cubic', fill_value="extrapolate")

    gain = rec_pw - interp_eirp(freq_rec_pw) + 3 # 3 dB due to the output balun
    gain = np.array(gain)

    # Calculate smoothed gain with moving average
    window_size = 2
    smoothed_gain = np.convolve(gain, np.ones(window_size)/window_size, mode='same')

    # EIRP
    line_max = smoothed_gain[window_size:len(angle_rec_pw)-window_size].max()
    if line_max > curr_max:
        curr_max = line_max
        curr_argmax = np.argmax(smoothed_gain[window_size:len(angle_rec_pw)-window_size])+window_size

    label_name = f'Radiation at {freq_rec_pw} GHz'
    # ax1.plot(freq_rec_pw, gain, label=f'{label_name}',linewidth=2*2, alpha=1) # non IEEE
    ax1.plot(angle_rec_pw/180*np.pi, gain, label=f'{label_name}', alpha=0.4)  # IEEE
    ax1.plot(angle_rec_pw[0:len(angle_rec_pw)-window_size]/180*np.pi, smoothed_gain[0:len(angle_rec_pw)-window_size], linewidth=2,
     label=f'Smoothed {label_name}')
    # ax2.plot(freq_rec_pw,imrr,label=f'{label_name}',linewidth=2*2, alpha=1)

ax=plt.gca()
bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
# arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=40")
# kw = dict(xycoords='data',textcoords="axes fraction",
#           arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top",fontsize=12*2) # non IEEE
kw = dict(xycoords='data',textcoords="axes fraction",
           bbox=bbox_props, ha="right", va="top",fontsize=20) # IEEE
ax1.annotate(f'Max EIRP = {curr_max:.2f} dB', xy=(angle_rec_pw[curr_argmax], curr_max), xytext=(0.94,0.96), **kw)
print(curr_argmax, curr_max)

ax1.set_ylabel('Transmitter EIRP [dB]',fontsize=20,labelpad=35)
yaxis_range = [-10, curr_max+15]

yticks = np.arange(yaxis_range[0]+10, yaxis_range[1]-10, 5)  # Ticks with a step of 20
ax1.set_yticks(yticks)
ax1.set_yticklabels([str(tick) for tick in yticks], fontfamily='DejaVu Sans',fontsize='20')

ax1.grid(True,linestyle='--',alpha=0.5)
ax1.legend(loc='lower center')
# angle_labels = [f"{int(np.degrees(angle))}\N{DEGREE SIGN}" for angle in ax1.get_xticks()]
# ax1.set_xticklabels(angle_labels)

angle_ticks = np.deg2rad(np.arange(0, 360, 45))  # Ticks every 45 degrees
angle_labels = [f"{int(np.rad2deg(angle))}\N{DEGREE SIGN}" for angle in angle_ticks]

ax1.set_xticks(angle_ticks)
ax1.set_xticklabels(angle_labels, fontfamily='DejaVu Sans',fontsize='20')

plt.show()