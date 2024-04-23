#!/usr/bin/python3

# Import the plotting and math packages
import matplotlib.pyplot as plt
import math

# Define initial constants
f0 = 5.
a0 = 100.
tdecay = 2.

# Create lists for the (x,y) data
time = []
amplitude = []

# Calculate the data and append to the lists
for i in range(0, 10000, 1):
  t = 0.001 * float(i) 
  a = a0 * math.exp(-t/tdecay)*math.cos(2. * math.pi * f0 * t)
  time.append(t)
  amplitude.append(a)

x = tuple(time)
y = tuple(amplitude)

# Create an x-y plot of the data with labeled axes

plt.figure().canvas.set_window_title('Oscillator')
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title('A Damped Oscillator')
#oscillator = plt.plot(time,amplitude)
oscillator = plt.plot(x,y)
plt.xlim(-10.,10.)
plt.ylim(-200.,200.)
#plt.xlim(5.,6.)
plt.setp(oscillator, color='m', linewidth=1.5)
plt.minorticks_on()


# Save the plot
fname = 'oscillator.png'
plt.savefig(fname)
fname = 'oscillator300.png'
plt.savefig(fname,dpi=300)
fname = 'oscillator.pdf'
plt.savefig(fname)

# Show the data
plt.show()


# Exit
exit()



