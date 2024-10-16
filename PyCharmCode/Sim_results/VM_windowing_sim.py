import numpy as np
import io
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

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

    if data_array.shape[0] > data_array.shape[1]:
        data_array = data_array.transpose()

    return data_array

def read_csv(file_path):
    """Reads amplitude and phase data from a CSV file."""
    amplitude_data = read_data_as_matrix(file_path[0])
    phase_data = read_data_as_matrix(file_path[1])

    amplitude = amplitude_data[1,:]
    amplitude = 10 ** (amplitude/20)
    phase = phase_data[1,:]
    phase = phase*np.pi/180

    amplitude[np.isnan(amplitude)] = 0
    phase[np.isnan(phase)] = 0  
    return amplitude, phase

def interpolate_data(amplitude, phase, N):
    """Interpolates the amplitude and phase to N points."""
    x = np.linspace(0, len(amplitude) - 1, len(amplitude))  # Original x-values
    x_new = np.linspace(0, len(amplitude) - 1, N)  # New x-values for interpolation

    amp_interp = interp1d(x, amplitude, kind='linear')(x_new)
    phase_interp = interp1d(x, phase, kind='linear')(x_new)
    
    return amp_interp, phase_interp

def compute_fft(amplitude, phase):
    """Computes the FFT from amplitude and phase data."""
    # Convert amplitude and phase to a complex signal
    print(phase)
    signal = amplitude * np.exp(1j * np.deg2rad(phase))  # Assuming phase is in degrees
    fft_result = np.fft.fft(signal)
    return fft_result

def plot_results(signal, fft_result, N):
    """Plots the original signal and the FFT result using ax."""
    fig, (ax1, ax3) = plt.subplots(1, 2, figsize=(12, 6))

    # Time-domain signal (Amplitude and phase)
    ax1.plot((np.abs(signal)), label='Amplitude (Linear) Part')
    ax2 = ax1.twinx()

    ax2.plot((np.angle(signal)/np.pi*180), label='Phase Part', color='orange')
    ax1.set_title(f'Time-Domain Signal ({N} Points)')
    ax1.set_xlabel('Samples')
    ax1.set_ylabel('Amplitude')
    ax2.set_ylabel('Phase (deg)')
    ax1.legend(loc='upper center')
    ax2.legend(loc='lower center')
    # Frequency-domain (FFT result)
    # ax3.stem((np.abs(fft_result[0:100])), label='Magnitude')
    ax3.stem((np.abs(fft_result)**2/np.sum(np.abs(fft_result)**2)), label='Power percentage')
    ax3.set_title('FFT Magnitude')
    ax3.set_xlabel('Frequency bin index')
    ax3.set_ylabel('Magnitude')
   
    ax3.legend()

    plt.tight_layout()
    plt.show()

def main(file_path, N):
    # Step 1: Read the amplitude and phase data from the CSV file
    amplitude, phase = read_csv(file_path)
    
    # Step 2: Interpolate the data to N points
    amp_interp, phase_interp = interpolate_data(amplitude, phase, N)
    
    # Step 3: Compute FFT from interpolated amplitude and phase
    fft_result = compute_fft(amp_interp, phase_interp)
    
    # Step 4: Plot the interpolated signal and its FFT result
    signal = amp_interp * np.exp(1j * np.deg2rad(phase_interp))  # Reconstruct complex signal
    plot_results(signal, fft_result, N)

# Example usage:
if __name__ == "__main__":
    file_path = []
    file_path.append(f'../Measurement/Spectrum_Plot/20240823_VM_TX/TraceGain_Leakage_Gain.csv')  
    file_path.append(f'../Measurement/Spectrum_Plot/20240823_VM_TX/TracePhase_Leakage_Phase.csv')
    N = 1024  # Number of points for interpolation and FFT
    main(file_path, N)
