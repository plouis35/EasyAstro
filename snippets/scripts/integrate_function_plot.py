#!/usr/bin/python3

import numpy as np
from scipy.integrate import quad
import matplotlib.pyplot as plt

# Define the integrand

global a
a = 10.

def f(x):
  value = a**2 / (a**2 + x**2)  
  return value

# Another way to define f(x) with no arguments other than x
# f = lambda x: a**2 / (a**2 + x**2)


# For a good demonstration use
x0 = -50.
x1 = 50.

# For infinity use
#x0 = -np.inf
#x1 = np.inf


integral, error = quad(f, x0, x1)

# Compare integral to an area under the curve

area = a * np.pi
print(integral, area)

# Generate sample data
x = np.linspace(-100,100.,200)  
y = f(x)

# Create an integration region to show in the plot
index01 = np.where( (x > x0) & (x < x1) )
y_region = y[index01]
x_region = x[index01]



# Create a plot with labeled axes
plt.xlabel('X')
plt.ylabel('F')
plt.title('Sample Integration')
plt.plot(x, y, color='blue', linestyle='-', marker='None', label='Lorentzian', linewidth=1.5)
plt.fill_between(x_region, 0., y_region, color='gray')
plt.legend()
plt.minorticks_on()

# Annotate with area
area_label = 'Area: %f' % integral
print(area_label)
plt.annotate(area_label, xy= (.6,.6), xycoords='axes fraction', color='gray', fontsize=18)
plt.show()


exit()
