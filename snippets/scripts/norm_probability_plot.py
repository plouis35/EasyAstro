#!/usr/bin/python3

import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

# Create a sample sapce
x = np.linspace (-10,10,100)

# Set up the parameters of the distribution
# Here loc makes it center on the origin and scale gives unit scaling
dist = norm(loc=0, scale=1)

pdf = dist.pdf(x)

# Create an plot with labeled axes
plt.xlabel('X')
plt.ylabel('PDF')
plt.title('Sample Normal Distribution')
plt.plot(x, pdf, color='blue', linestyle='-', marker='None', label='Probability', linewidth=1.5)
plt.legend()
plt.minorticks_on()
plt.show()


exit()
