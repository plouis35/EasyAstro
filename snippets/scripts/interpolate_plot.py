#!/usr/bin/python3

import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# Import your data into a np array yn for x or ...

# Generate sample data
x = np.linspace(0,10.*np.pi,200)  
y = np.cos(x)

# Add noise to the sample data
#yn = y + 0.9 * np.random.normal(size=len(x))

# Function to interpolate the data with a linear interpolator
f_linear = interp1d(x, y, kind='linear')

# Function to interpolate the data with a quadratic interpolator
f_quadratic = interp1d(x, y, kind='quadratic')

# Values of x for sampling inside the boundaries of the original data
x_interpolated = np.linspace(x.min(),x.max(), 1000)

# New values of y for these sample points
y_interpolated_linear = f_linear(x_interpolated)
y_interpolated_quadratic =  f_quadratic(x_interpolated)


# Create an plot with labeled axes
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Sample Interpolation')
plt.plot(x, y,   color='red', linestyle='None', marker='.',markersize=10.,label='Data')
plt.plot(x_interpolated, y_interpolated_linear, color='green', linestyle=':', marker='None', label='Linear', linewidth=1.5)
plt.plot(x_interpolated, y_interpolated_quadratic, color='blue', linestyle='-', marker='None', label='Quadratic', linewidth=1.5)
plt.legend()
plt.minorticks_on()
plt.show()


exit()
