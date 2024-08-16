import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Sample data (incomplete coverage of angles)
angles = np.linspace(0, np.pi, 180)  # Angles from 0 to 180 degrees in radians
radiation_pattern = np.abs(np.sin(angles))  # Sample radiation pattern


def interpolate_data(angles, radiation_pattern, num_points=360):
    """
    Interpolates the given data to cover the full range of angles from 0 to 2π radians.

    Parameters:
    - angles (1D array): Array of angles in radians.
    - radiation_pattern (1D array): Array of radiation pattern values.
    - num_points (int): Number of points to interpolate over.

    Returns:
    - full_angles (1D array): Interpolated angles from 0 to 2π radians.
    - full_pattern (1D array): Interpolated radiation pattern values.
    """
    interp_func = interp1d(angles, radiation_pattern, kind='linear', fill_value='extrapolate')
    full_angles = np.linspace(0, 2 * np.pi, num_points)
    full_pattern = interp_func(full_angles)
    return full_angles, full_pattern


def plot_radiation_pattern(angles, radiation_pattern):
    """
    Plots the radiation pattern on a polar plot.

    Parameters:
    - angles (1D array): Array of angles in radians.
    - radiation_pattern (1D array): Array of radiation pattern values.
    """

    # Interpolate data to cover full range of angles
    full_angles, full_pattern = interpolate_data(angles, radiation_pattern)

    # Create polar plot
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # Plot data
    ax.plot(full_angles, full_pattern, label='Radiation Pattern')

    # Set angle ticks and labels with degree symbol
    angle_labels = [f"{int(np.degrees(angle))}\N{DEGREE SIGN}" for angle in ax.get_xticks()]
    ax.set_xticklabels(angle_labels)

    # Add labels and title
    ax.set_xlabel('Angle (degrees)')
    ax.set_ylabel('Radiation Pattern')
    ax.set_title('Radiation Pattern vs. Angle')
    ax.legend()

    # Show plot
    plt.show()


# Example usage
plot_radiation_pattern(angles, radiation_pattern)
