import numpy as np
import matplotlib.pyplot as plt

# Create some data
x = np.arange(0, 10, 0.1)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.exp(x / 10)
y4 = np.log(x + 1)

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# First subplot with two y-axes
ax1.set_xlabel('X-axis')
ax1.set_ylabel('Y1-axis', color='red')
ax1.plot(x, y1, color='red')
ax1.tick_params(axis='y', labelcolor='red')

ax1_twin = ax1.twinx()
ax1_twin.set_ylabel('Y2-axis', color='blue')
ax1_twin.plot(x, y2, color='blue')
ax1_twin.tick_params(axis='y', labelcolor='blue')

# Second subplot with two y-axes
ax2.set_xlabel('X-axis')
ax2.set_ylabel('Y3-axis', color='green')
ax2.plot(x, y3, color='green')
ax2.tick_params(axis='y', labelcolor='green')

ax2_twin = ax2.twinx()
ax2_twin.set_ylabel('Y4-axis', color='purple')
ax2_twin.plot(x, y4, color='purple')
ax2_twin.tick_params(axis='y', labelcolor='purple')

# Adjust layout
plt.tight_layout()
plt.show()
