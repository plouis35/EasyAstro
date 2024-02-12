#!/usr/bin/python3

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# Create a function to fit with
def func(x,a,b):
  return a*x + b

# Import your data into a np array yn for x or ...

# Generate sample data

x = np.linspace(0,10,100)  
y = func(x, 1, 2)

# Add noise to the sample data
yn = y + 0.9 * np.random.normal(size=len(x))

# Call curve_fit
popt, pcov = curve_fit(func, x, yn)

# Best fit values are returned as popt
print(popt)

afit, bfit = popt

# Calculated fitted values for the same x

yfit = func(x, afit, bfit)

# Create an x-y plot with labeled axes
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Sample Curve Fit')
plt.plot(x, yn,   color='red', linestyle='None', marker='.',label='Data')
plt.plot(x, yfit, color='blue', linestyle='solid', marker='None', label='Fit', linewidth=1.5)
plt.legend()
plt.minorticks_on()
plt.show()


exit()
