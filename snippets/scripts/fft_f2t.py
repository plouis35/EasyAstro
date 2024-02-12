#!/usr/bin/python3

# Compute the real part of the Fourier Transform from frequency to time
# Input real spectrum with uniformly spaced data
# Output real time series data Brigham normalized
# Input file with  pairs of frequency and spectrum
# Output file with pairs of time and amplitude

 # Use true division everywhere

import os
import sys
import numpy as np
import scipy.fftpack 

if len(sys.argv) == 1:
  print(" ")
  print("Usage: fft_f2t.py spectrum.dat amplitude.dat ")
  print(" ")
  sys.exit("Fourier transform a frequency spectrum to a time series amplitude\n")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print(" ")
  print("Usage: fft_f2t.py spectrum.dat amplitude.dat ")
  print(" ")
  sys.exit("Fourier transform a frequency spectrum to a time series amplitude\n")

# Read the data


# Alternative method to read the data uses loadtxt
# It is simpler to program but much much slower for large files
# indata = np.loadtxt(infile)
# freq = indata[:,0]
# spectrum = indata[:,1]


datafp = open(infile, 'r')
datatext = datafp.readlines()
datafp.close()

# How many lines were there?

i = 0
for line in datatext:
  i = i + 1

nlines = i

# Create the arrays for fixed size is much faster than appending on the fly

freq = np.zeros((nlines))
spectrum = np.zeros((nlines))

# Parse the lines into the data

i = 0
for line in datatext:
  try:
    entry = line.strip().split()
    freq[i] = float(entry[0])
    spectrum[i] = float(entry[1])
    i = i + 1
  except:
    pass

# No windowing (apodization)
# Set the first point of the input data

spectrum[0] = 0.5*spectrum[0]

# Find the frequency increment from the input frequency array
freqstep = freq.item(1) - freq.item(0)

# Use an inverse FFT to calculate the time series
amplitude = scipy.fftpack.ifft(spectrum)

# Find the positive times from the scipy fft helper function
time = scipy.fftpack.fftfreq( amplitude.size, d = freqstep )
index = np.where(time >= 0.)

# Scale the amplitudes  and clip  for positive times
clipped_amplitude = amplitude[index].real
anorm = 2.*clipped_amplitude.size
clipped_amplitude = anorm * clipped_amplitude
clipped_amplitude[0] = 0.5 * clipped_amplitude[0]
clipped_time = time[index]

# Save the spectrum as a 2d text file
dataout = np.column_stack((clipped_time,clipped_amplitude))  
np.savetxt(outfile, dataout)

exit()




