import matplotlib.pyplot as plt
import numpy as np

# Create some data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create a figure and axis
fig, ax1 = plt.subplots()

# Plot the data on the first x-axis
ax1.plot(x, y, 'b-')
ax1.set_xlabel('Original X-axis')
ax1.set_ylabel('Y-axis')

# Create a second x-axis below the original x-axis
ax2 = ax1.twiny()

# Define a new scale for the second x-axis
# For example, let's say we want to use a scale that is 10 times the original scale
scale_factor = 10
new_x = x * scale_factor

# Set the limits and ticks of the new x-axis
ax2.set_xlim(ax1.get_xlim()[0] * scale_factor, ax1.get_xlim()[1] * scale_factor)
ax2.set_xticks(ax1.get_xticks() * scale_factor)
ax2.set_xticklabels([f'{tick/scale_factor:.2f}' for tick in ax1.get_xticks()])
ax2.set_xlabel('New X-axis with Different Scale')

# Optionally adjust the position of the new x-axis
ax2.spines['bottom'].set_position(('outward', 40))  # Moves the new x-axis downward

plt.show()
