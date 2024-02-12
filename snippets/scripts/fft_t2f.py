#!/usr/bin/python3

# Compute the real part of the Fourier Transform from time to frequency
# Input real time series uniformly spaced data
# Output real data Brigham normalized
# Input file with  pairs of time and amplitude
# Output file with pairs of frequency and amplitude

 # Use true division everywhere

import os
import sys
import numpy as np
import scipy.fftpack 

if len(sys.argv) == 1:
  print(" ")
  print("Usage: fft_t2f.py amplitude.dat spectrum.dat ")
  print(" ")
  sys.exit("Fourier transform a time series amplitude to a frequency spectrum\n")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print(" ")
  print("Usage: fft_t2f.py amplitude.dat spectrum.dat ")
  print(" ")
  sys.exit("Fourier transform a time series amplitude to a frequency spectrum\n")

# Read the data

# Alternative method to read the data uses loadtxt
# It is simpler to program but much much slower for large files
# indata = np.loadtxt(infile)
# time = indata[:,0]
# amplitude = indata[:,1]

datafp = open(infile, 'r')
datatext = datafp.readlines()
datafp.close()

# How many lines were there?

i = 0
for line in datatext:
  i = i + 1

nlines = i

# Create the arrays for fixed size is much faster than appending on the fly

time = np.zeros((nlines))
amplitude = np.zeros((nlines))

# Parse the lines into the data

i = 0
for line in datatext:
  try:
    entry = line.strip().split()
    time[i] = float(entry[0])
    amplitude[i] = float(entry[1])
    i = i + 1
  except:
    pass

# Calculate the Fourier Transform

# No windowing (apodization)
# Set the first point of the input data

amplitude[0] = 0.5*amplitude[0]

# Find the time increment from the time array
timestep = time.item(1) - time.item(0)

# Use an FFT to calculate the spectrum of the real amplitude
spectrum = scipy.fftpack.fft(amplitude)

# Find the positive frequencies from the scipy fft helper function
frequency = scipy.fftpack.fftfreq( spectrum.size, d = timestep )
index = np.where(frequency >= 0.)

# Scale the spectrum  and clip  for positive frequencies
clipped_spectrum = spectrum[index].real
anorm = 2. / clipped_spectrum.size
clipped_spectrum = anorm * clipped_spectrum
clipped_spectrum[0] = 0.5 * clipped_spectrum[0]
clipped_frequency = frequency[index]

# Save the spectrum as a 2d text file
dataout = np.column_stack((clipped_frequency,clipped_spectrum))  
np.savetxt(outfile, dataout)

exit()




