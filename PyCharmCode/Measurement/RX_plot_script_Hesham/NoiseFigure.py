import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from pylab import *
import os
import difflib
import glob
import csv
from scipy.interpolate import interp1d

plt.rcParams['axes.unicode_minus'] = False
# Initialization
debug = 1
d = 0.32
freq_min = 110
freq_max = 170
RBW = 1000E3

def find_closest_file(directory, target_file):
    # List all files in the directory
    all_files = os.listdir(directory)

    # Check for an exact match
    if target_file in all_files:
        return os.path.join(directory, target_file)

    # Find the closest match
    closest_matches = difflib.get_close_matches(target_file, all_files, n=1)
    if closest_matches:
        return os.path.join(directory, closest_matches[0])

    return None

my_dir = ""
my_subdir = "0725/NF"

# Define frequency range and interpolate data
# Load received power data
csv_files = glob.glob(os.path.join(my_dir, my_subdir, 'RX_RFNoise_2024*.csv'))

if len(csv_files) == 0:
    print(f"No files found in {my_dir}/{my_subdir}/")
    exit()
# Plotting
plt.figure()
plt.style.use(['science','no-latex'])

# Print the file names
curr_min = 1000
curr_argmin = 0
for i,file in enumerate(list(csv_files)):
    print(os.path.basename(file))

    file_name_parse = os.path.basename(file)
    file_name_parse = file_name_parse.split('_')
    file_attn = 10 if file_name_parse[-1] == '10.csv' else 12 if file_name_parse[-1] == '12.csv' else 14
    file_gain = file_name_parse[-3]

    gain_file = f'{my_dir}{my_subdir}/gain/RX_RFGain_{file_gain}_attn_{file_attn}.csv'
    if file_gain == 'gain31':
        continue
    # print(gain_file)
    dir = os.path.abspath(f'{my_dir}{my_subdir}/gain/')
    all_files = os.listdir(dir)

    result_path = find_closest_file(dir, gain_file)
    print(result_path,1)
    with open(result_path) as file_obj:
        reader_obj = list(csv.reader(file_obj))

        freq_list = np.array(reader_obj[0][1:], dtype=float)
        gain_list = np.array(reader_obj[1][1:], dtype=float)
        # print(freq_list)

    # file = f'{my_dir}{my_subdir}RX_RF_20240724_1739.csv'
    tmp = pd.read_csv(file).values
    print(tmp.shape)
    freq_rec_rx = tmp[0, :]
    rec_rx = tmp[1, :]
    # print(freq_rec_rx, rec_rx)

    # subtract gain
    nf = rec_rx
    for j,freq in enumerate(list(freq_rec_rx)):
        idx = (np.abs(freq_list-freq)).argmin()
        # print(i)
        print(freq, rec_rx[j], gain_list[idx])
        nf[j] = 174 - 10*np.log10(RBW) + rec_rx[j] - gain_list[idx]
    nf = np.array(nf)

    # Calculate smoothed gain with moving average
    window_size = 4
    smoothed_nf = np.convolve(nf, np.ones(window_size)/window_size, mode='same')
    # print(smoothed_gain, smoothed_gain.max())
    line_min = np.nanmin(smoothed_nf[0:len(freq_rec_rx)])
    print(1, line_min)
    if line_min < curr_min and line_min != nan:
        curr_min = line_min
        print(2,line_min)
        curr_argmin = np.nanargmin(smoothed_nf[0:len(freq_rec_rx)])

    # plt.plot(freq_rec_rx, nf, label=f'NF_at_{file_gain}',linestyle='--', alpha=0.7)
    # plt.plot(freq_rec_rx[0:len(freq_rec_rx)-window_size], smoothed_nf[0:len(freq_rec_rx)-window_size], label=f'Smoothed NF at  {file_gain} ')
    plt.plot(freq_rec_rx, nf, label=f'NF',linestyle='--', linewidth=2, alpha=0.7)
    plt.plot(freq_rec_rx[0:len(freq_rec_rx)-window_size], smoothed_nf[0:len(freq_rec_rx)-window_size], linewidth=2, label=f'Smoothed NF')

ax=plt.gca()
bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=100")
kw = dict(xycoords='data',textcoords="axes fraction",
          arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top", fontsize=12)
ax.annotate(f'Min NF = {curr_min:.2f} dB', xy=(freq_rec_rx[curr_argmin], curr_min), xytext=(0.94,0.06), **kw)

plt.tick_params(labelsize = 28)
plt.xlabel('Freq [GHz]',fontsize=30)
plt.ylabel('Receiver Noise Figure [dB] ',fontsize=30)
plt.grid(True,linestyle='--', dashes=(5, 10))
plt.legend(loc="upper center", fontsize = 14*2)
plt.axis([freq_rec_rx[1],freq_rec_rx[-1],0,90])
plt.show()
