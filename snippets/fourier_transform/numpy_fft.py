#!/usr/bin/python3

# Generate data, Fourier Transform and plot on the screen

import matplotlib.pyplot as plt
import numpy as np

f0 = 5.
a0 = 100.
tdecay = 2.
timestep = 0.002
timemax = 100.

# Create the oscillator
time = np.arange(0,timemax,timestep)
amplitude = a0*np.exp(-time/tdecay)*np.cos(2.*np.pi*f0*time)

# Use an FFT to calculate its spectrum
spectrum = np.fft.fft(amplitude)

# Find the positive frequencies
frequency = np.fft.fftfreq( spectrum.size, d = timestep )
index = np.where(frequency >= 0.)

# Scale the FFT and clip the data
clipped_spectrum = timestep*spectrum[index].real
clipped_frequency = frequency[index]

# Create a figure
fig = plt.figure()

# Adjust white space between plots
fig.subplots_adjust(hspace=0.5)

# Create x-y plots of the amplitude and transform with labeled axes

data1 = fig.add_subplot(2,1,1)
plt.xlabel('Time')
plt.ylabel('Amplitude')
plt.title('Damping')
data1.plot(time,amplitude, color='red', label='Amplitude')
plt.legend()
plt.minorticks_on()
plt.xlim(0., 10.)

data2 = fig.add_subplot(2,1,2)
plt.xlabel('Frequency')
plt.ylabel('Signal')
plt.title('Spectrum of a Damped Oscillator')
data2.plot(clipped_frequency,clipped_spectrum, color='blue', linestyle='solid', marker='None', label='FFT', linewidth=1.5)
plt.legend()
plt.minorticks_on()
plt.xlim(3., 7.)

# Show the data
plt.show()

exit()




