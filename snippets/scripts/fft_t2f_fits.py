#!/usr/bin/python3

# Compute the real part of the Fourier Transform from time to frequency
# Input real time series uniformly spaced data
# Output real data Brigham normalized
# Input file with  pairs of time and amplitude
# Output fits file with a spectrum on frequency and time axes  
# Requires numpy version 1.7 or higher for copyto function

 # Use true division everywhere

import os
import sys
import math
import numpy as np  
import scipy.fftpack
import pyfits
from time import gmtime, strftime  # for utc


if len(sys.argv) == 1:
  print(" ")
  print("Usage: fft_t2f_fits.py amplitude.dat spectrum.fits ")
  print(" ")
  sys.exit("Fourier transform a time series amplitude to a frequency spectrum\n")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print(" ")
  print("Usage: fft_t2f_fits.py amplitude.dat spectrum.fits ")
  print(" ")
  sys.exit("Fourier transform a time series amplitude to a frequency spectrum fits image\n")

# Read the data

datafp = open(infile, 'r')
datatext = datafp.readlines()
datafp.close()

# How many lines were there?

i = 0
for line in datatext:
  i = i + 1

# Do not process the data beyond the last power of 2 line

nlines = int(2**(int(math.log(i,2))))
ncols = 4096
nrows = int(nlines/ncols)

# Create the arrays for fixed size 

time = np.zeros((ncols,nrows))
amplitude = np.zeros((ncols,nrows))
count = np.zeros((ncols,nrows))

# Parse the lines into the data

i = 0
j = 0
k = 0
for line in datatext:
  if k < nlines:
    entry = line.strip().split()
    time[i,j] = float(entry[0])
    amplitude[i,j] = float(entry[1])
    count[i,j] = float(k)
    i = i + 1
    k = k + 1
    if i == ncols:
      i = 0
      j = j + 1
  else:
    break
    

# Take the Fourier Transform

transform = scipy.fftpack.fft(amplitude,axis=0)

# Extract the real part with positive frequencies

npos = ncols/2
spectrum = np.zeros((npos,nrows))
np.copyto(spectrum,transform.real[0:npos,:])

timespan = time[ ncols - 1, nrows - 1 ] - time[0,0]
timestep = timespan / (ncols*nrows -1 )

freqspan = 0.5 / timestep
freqstep = freqspan / float(npos - 1) 

# Set a clobber flag True so that images can be overwritten
# Otherwise set it False for safety

clobberflag = True  
  
# Set data type for output

# newdatatype = np.float32  

# Create the output list for this image

#outlist = pyfits.PrimaryHDU(timage.astype(newdatatype))

outlist = pyfits.PrimaryHDU(spectrum)

# Provide a new date stamp and the increments for both axes

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
comment_tstep = "Time step: %f" % ( timestep, )
comment_fstep = "Frequency step: %f" % ( freqstep, )

# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['COMMENT'] = comment_tstep
outhdr['COMMENT'] = comment_fstep
outhdr['history'] = 'FFT created by fft_t2f_fits'
outhdr['history'] = 'Data file ' + infile

# Create, write, and close the output fits file

outlist.writeto(outfile, clobber = clobberflag)


exit()





