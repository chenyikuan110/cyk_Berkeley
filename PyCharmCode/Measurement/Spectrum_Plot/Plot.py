import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from pylab import *
import os
import io
import glob
from scipy.interpolate import interp1d
import csv
import re
import itertools

my_dir = ""

# Load DUT data
my_subdir = "20240830_FMCW/compare"
csv_format = 'Trace*.csv'
# csv_format = '*'
sort_regex = r'_(\d+(?:\.\d+)?)'
normalize = False
my_xlabel = f'Target distance [m]'
# plot_name = 'Received Power\n Normalized to Leakage [dB]'
plot_name = 'Measured Power [dBm]'
# plot_name = 'Cancellation [dB]'
font_downscale = 2
legend_loc = 'upper center'
linewidth=2

marker_on = True

plt.rcParams['axes.unicode_minus'] = False
# Initialization
debug = 1
d = 0.32
freq_min = 120
freq_max = 150

line_styles = ['-','-','-']
line_cycle = itertools.cycle(line_styles)

color_styles = ['black','red','blue']
color_cycle = itertools.cycle(color_styles)

def read_data_as_matrix(file_path):
    # Read the file and locate the "DATA" line
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Find the line index with "DATA"
    data_start_index = next(i for i, line in enumerate(lines) if line.strip() == "DATA") + 1

    # Read the data into a pandas DataFrame
    data_lines = lines[data_start_index:]
    data = pd.read_csv(io.StringIO(''.join(data_lines)), header=None)

    # Convert the DataFrame to a NumPy array
    data_array = data.values

    return data_array

def split_string(s, delimiters):
    # Create a regular expression pattern for the delimiters
    pattern = '|'.join(map(re.escape, delimiters))

    # Use re.split to split the string based on the pattern
    return re.split(pattern, s)


def extract_second_number(filename):
    # Find all sequences of digits in the filename, including those with decimal points
    match = re.findall(sort_regex, filename)
    return float(match[0]) #if len(match) > 1 else 0

# Sort the list using the extracted numbers


csv_files = glob.glob(os.path.join(my_dir, my_subdir, csv_format))
# csv_files = sorted(csv_files, key=extract_second_number)

# Plotting
# plt.figure()
plt.style.use(['science','no-latex'])
fig, ax1 = plt.subplots()
# Print the file names
curr_max = -100
curr_max_imrr = -100
curr_argmax = 0
curr_argmax_imrr = 0
i = 0
for i,file in enumerate(list(csv_files)):

    # if i  == len(csv_files)-1:
    #     continue

    print(os.path.basename(file))

    file_name_parse = os.path.basename(file)
    file_name_parse = split_string(file_name_parse,['_','.c'])

    # file = f'{my_dir}{my_subdir}RX_RF_20240724_1739.csv'
    # tmp = pd.read_csv(file).values
    tmp = read_data_as_matrix(file)
    print(tmp.shape)

    if tmp.shape[0] > tmp.shape[1]:
        tmp = tmp.transpose()

    freq_rec_pw = tmp[0,:]
    rec_pw = tmp[1,:]
    print(freq_rec_pw)
    # freq_rec_pw = (freq_rec_pw+125e9)/1e9
    # freq_rec_pw = (freq_rec_pw)/1e9
    freq_rec_pw = (freq_rec_pw - 10e6) / 10e3*0.015

    gain = rec_pw # 3 dB due to the output balun
    gain = np.array(gain)

    # Calculate smoothed gain with moving average
    window_size = 1
    smoothed_gain = np.convolve(gain, np.ones(window_size)/window_size, mode='same')

    line_max = smoothed_gain[window_size:len(freq_rec_pw)-window_size].max()
    if line_max > curr_max:
        curr_max = line_max
        curr_argmax = np.argmax(smoothed_gain[window_size:len(freq_rec_pw)-window_size])+window_size

    label_name = ' '.join(file_name_parse[0:-1])
    offset = -line_max if normalize else 0 # 0 if label_name == 'IQ' else 10

    if marker_on:
        ax1.plot(freq_rec_pw, gain + offset, next(line_cycle),label=f'{label_name}', color=next(color_cycle), linewidth=linewidth, alpha=1) # non IEEE
    else:
        ax1.plot(freq_rec_pw, gain + offset, next(line_cycle),label=f'{label_name}',color=next(color_cycle),linewidth=linewidth, alpha=1) # non IEEE
    # ax1.plot(freq_rec_pw, gain, label=f'{label_name}', alpha=1)  # IEEE


# ax=plt.gca()
# bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
# arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=40")
# kw = dict(xycoords='data',textcoords="axes fraction",
#           arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top",fontsize=12*2) # non IEEE
# # ax1.annotate(f'Max EIRP = {curr_max:.2f} dB', xy=(freq_rec_pw[curr_argmax], curr_max), xytext=(0.94,0.96), **kw)
# print(curr_argmax, curr_max)

# ax1.axhline(y=curr_max, color='r', linestyle='--')
ax1.tick_params(labelsize = 28*2)
ax1.set_xlabel(my_xlabel,fontsize=20*2)
ax1.set_ylabel(plot_name,fontsize=20*2)
ax1.grid(True,linestyle='--', dashes=(5, 10))
ax1.legend(loc=legend_loc, fontsize=14*2*4/(i+1)/font_downscale, facecolor='white', edgecolor='black')

print("curr max is ",curr_max)
xaxis_range = [int(freq_rec_pw[0]), int(freq_rec_pw[-1])]
spacing = np.floor(xaxis_range[1]-xaxis_range[0])/5
# xticks = np.arange(xaxis_range[0], xaxis_range[1]+2, spacing)  # Ticks with a step of 20
xticks = np.arange(xaxis_range[0], xaxis_range[1]+2, spacing)
print("xticks is ",xticks, "spacing is ",spacing)
ax1.set_xticks(xticks)
print(gain[~np.isnan(gain)])
print(np.min(gain[~np.isnan(gain)]))
print(curr_max)
yaxis_range = [np.min([-0, np.min(gain[~np.isnan(gain)])])-10+offset, np.max([-50,curr_max])+5+offset]
yaxis_range = yaxis_range-(np.min(gain[~np.isnan(gain)]) % 10) + 10
yticks = np.arange(yaxis_range[0]+10, yaxis_range[1]-0, 10)  # Ticks with a step of 20
ax1.set_yticks(yticks)
# ax1.set_yticklabels([str(tick) for tick in yticks])
#
ax1.axis([freq_rec_pw[0],freq_rec_pw[-1],yaxis_range[0],yaxis_range[1]])
# print("plotting")
# plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
plt.show()

