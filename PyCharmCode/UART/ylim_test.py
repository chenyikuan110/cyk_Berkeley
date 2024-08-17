import matplotlib.pyplot as plt
import numpy as np

# Sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)*3

# Create a plot
fig, ax = plt.subplots()

ax.plot(x, y)

# Set the y-axis limits
ax.set_ylim(-2, 2)  # Setting limits to -2 and 2

# Adding labels and title for clarity
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_title('Sine Wave with Custom Y-axis Limits')

# Show the plot
plt.show()
