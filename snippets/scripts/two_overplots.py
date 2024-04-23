#!/usr/bin/python3

# Import the plotting and math packages
import matplotlib.pyplot as plt
import math

# Define initial constants
f0 = 5.
a0 = 1.
tdecay = 2.

# Create lists for the (x,y) data
time = []
sine_amplitude = []
exp_amplitude = []
product_amplitude = []

# Calculate the data and append to the lists
for i in range(0, 10000, 1):
  t = 0.001 * float(i) 
  a1 = math.cos(2. * math.pi * f0 * t)
  a2 = math.exp(-t/tdecay)
  a = a1*a2
  time.append(t)
  sine_amplitude.append(a1)
  exp_amplitude.append(a2)
  product_amplitude.append(a)

# Create an x-y plot of the data with labeled axes
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title('A Damped Oscillator')
plt.plot(time,exp_amplitude,'r.', label='Exponential')
plt.plot(time,product_amplitude, color='blue', linestyle='solid', marker='None', label='Product', linewidth=1.5)

plt.legend()

plt.minorticks_on()

plt.tick_params(which='major', length=7)
plt.tick_params(which='minor', length=4, color='r')  


# Show the data
plt.show()
