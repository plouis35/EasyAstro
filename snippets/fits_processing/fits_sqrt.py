#!/usr/bin/python3

# Take the square root a fits image

import os
import sys
import numpy as np
import astropy.io.fits as pyfits
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print(" ")
  print("Usage: fits_sqrt.py infile.fits outfile.fits")
  print(" ")
  sys.exit("Returns the square root of the original image\n")
elif len(sys.argv) == 3:
  # Correct choice of arguments
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print(" ")
  print("Usage: fits_sqrt.py infile.fits outfile.fits")
  print(" ")
  sys.exit("Returns the square root of the original image\n")

# Set a overwrite flag True so that images can be overwritten
# Otherwise set it False for safety

overwriteflag = True  
  
# Open the fits file readonly by default and create an input hdulist

inlist = pyfits.open(infile) 

# Assign the input header 

inhdr = inlist[0].header

# Assign image data to numpy array and get its size

inimage =  inlist[0].data.astype('float32')
xsize, ysize = inimage.shape

# Use a unit array to assure we treat the whole image in floating point 

fone = np.ones((xsize,ysize))
fimage = fone*inimage

# Transform the image data after changing sign for negative data

outimage = np.sqrt(np.abs(inimage))

# Restore the original signs

outimage = outimage * np.sign(inimage)

# Create the fits object for this image using the header of the first image
# Use float32 for output type

outlist = pyfits.PrimaryHDU(outimage.astype('float32'),inhdr)

# Provide a new date stamp

file_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())


# Update the header

outhdr = outlist.header
outhdr['DATE'] = file_time
outhdr['history'] = 'Image square root by fits_sqrt'
outhdr['history'] = 'Image file '+  infile

# Write the fits file

outlist.writeto(outfile, overwrite = overwriteflag)

# Close the input  and exit

inlist.close()
exit()

