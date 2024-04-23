#!/usr/bin/python3

# Convert sky coordinates to pixel coordinates

import os
import sys
import numpy as np
import astropy.io.fits as pyfits
from astropy.wcs import WCS
from time import gmtime, strftime  # for utc

if len(sys.argv) == 1:
  print(" ")
  print("Usage: fits_sky_to_pix.py infile.fits skycoords.txt pixels.txt ")
  print(" ")
  sys.exit("Convert sky coordinates to pixel coordinates\n")
elif len(sys.argv) == 4:
  infile = sys.argv[1]
  skyfile = sys.argv[2]
  pixfile = sys.argv[3]
else:
  print(" ")
  print("Usage: fits_sky_to_pix.py wcsfile.fits skycoords.txt pixels.txt ")
  print(" ")
  sys.exit("Convert sky coordinates to pixel coordinates\n")

# Take sky coordinates from a ds9 regions file or a plain text file
# Use the wcs header of an image file for the celestial coordinate conversion parameters
# Calculate and export corresponding pixel coordinates

# Set this True for verbose output

verboseflag = False

# Open the file with pixel coordinates
skyfp = open(skyfile, 'r')

# Read all the lines into a list
skytext = skyfp.readlines()

# Close the pixel file
skyfp.close()

# Create an sky objects counter and an empty sky objects list
i = 0
sky = []

# Split sky text and parse into ra and dec strings  
# We try various formats looking for one with a valid entry and take the first one we find
# This searches ds9 box and circle regions, comma separated, and space separated

# Region in ds9 shows a string in hr:min:sec and deg:min:sec but wcs requires both in decimal degrees

for line in skytext:

  if 'circle' in line:
    # Treat the case of a ds9 circle region
    
    # Remove the leading circle( descriptor
    line = line.replace("circle(", '')

    # Remove the trailing )
    line = line.replace(")", '')

    # Remove the trailing \n and split into text fields
    entry = line.strip().split(",")
    rastr = entry[0]
    decstr = entry[1]
    rahrstr, raminstr, rasecstr = rastr.split(":")
    decdegstr, decminstr, decsecstr = decstr.split(":")
     
    # Convert the text fields into decimal degrees for wcs
    rahr = abs(float(rahrstr))
    ramin = abs(float(raminstr))
    rasec = abs(float(rasecstr))
    if float(rahrstr) < 0:
      rasign = -1.
    else:
      rasign = +1.
          
    decdeg = abs(float(decdegstr))
    decmin = abs(float(decminstr))
    decsec = abs(float(decsecstr))
    if float(decdegstr) < 0:
      decsign = -1.
    else:
      decsign = +1.
   
    ra = rasign*(rahr + ramin/60. + rasec/3600.)*15.
    dec = decsign*(decdeg + decmin/60. + decsec/3600.)

    # Append to the sky list and update the counter
    sky.append((ra, dec))
    i = i + 1

  elif 'box' in line:
    # Treat the case of a ds9 box region
    
    # Remove the leading box( descriptor
    line = line.replace("box(", '')

    # Remove the trailing )
    line = line.replace(")", '')

    # Remove the trailing \n and split into text fields
    entry = line.strip().split(",")
    rastr = entry[0]
    decstr = entry[1]
    rahrstr, raminstr, rasecstr = rastr.split(":")
    decdegstr, decminstr, decsecstr = decstr.split(":")
     
    # Convert the text fields into decimal degrees for wcs
    rahr = abs(float(rahrstr))
    ramin = abs(float(raminstr))
    rasec = abs(float(rasecstr))
    if float(rahrstr) < 0:
      rasign = -1.
    else:
      rasign = +1.
          
    decdeg = abs(float(decdegstr))
    decmin = abs(float(decminstr))
    decsec = abs(float(decsecstr))
    if float(decdegstr) < 0:
      decsign = -1.
    else:
      decsign = +1.
   
    ra = rasign*(rahr + ramin/60. + rasec/3600.)*15.
    dec = decsign*(decdeg + decmin/60. + decsec/3600.)

    # Append to the sky list and update the counter
    sky.append((ra, dec))
    i = i + 1
       
  elif ':' in line:

    # Try to remove the trailing \n and split into text fields depending on separator
    
    try:    
      # Treat the case of a plain text comma separated entry      
      entry = line.strip().split(",")  
      # Get the x,y values for these fields
      rastr = entry[0]
      decstr = entry[1]
      rahrstr, raminstr, rasecstr = rastr.split(":")
      decdegstr, decminstr, decsecstr = decstr.split(":")
     
      # Convert the text fields into decimal degrees for wcs
      rahr = abs(float(rahrstr))
      ramin = abs(float(raminstr))
      rasec = abs(float(rasecstr))
      if float(rahrstr) < 0:
        rasign = -1.
      else:
        rasign = +1.
          
      decdeg = abs(float(decdegstr))
      decmin = abs(float(decminstr))
      decsec = abs(float(decsecstr))
      if float(decdegstr) < 0:
        decsign = -1.
      else:
        decsign = +1.
   
      ra = rasign*(rahr + ramin/60. + rasec/3600.)*15.
      dec = decsign*(decdeg + decmin/60. + decsec/3600.)
      
      sky.append((ra, dec))
      i = i + 1    

    except:      
      
      try: 
        # Treat the case of plane text entries separated by blank space
        entry = line.strip().split()
        rastr = entry[0]
        decstr = entry[1]
        rahrstr, raminstr, rasecstr = rastr.split(":")
        decdegstr, decminstr, decsecstr = decstr.split(":")
         
        # Convert the text fields into decimal degrees for wcs
        rahr = abs(float(rahrstr))
        ramin = abs(float(raminstr))
        rasec = abs(float(rasecstr))
        if float(rahrstr) < 0:
          rasign = -1.
        else:
          rasign = +1.
              
        decdeg = abs(float(decdegstr))
        decmin = abs(float(decminstr))
        decsec = abs(float(decsecstr))
        if float(decdegstr) < 0:
          decsign = -1.
        else:
          decsign = +1.
       
        ra = rasign*(rahr + ramin/60. + rasec/3600.)*15.
        dec = decsign*(decdeg + decmin/60. + decsec/3600.)

        sky.append((ra, dec))
        i = i + 1    
           
      except:
        pass
        

  else:
    # Treat the cases of plain text sky coordinates assuming decimal ra hours and dec degrees
    # Try to remove the trailing \n and split into text fields
    
    try:    
      # Treat the case of a plain text comma separated entry      
      entry = line.strip().split(",")  
      # Get the x,y values for these fields
      ra = 15.*float(entry[0])
      dec = float(entry[1])
      sky.append((ra, dec))
      i = i + 1    
    except:      
      
      try: 
        # Treat the case of a plane text blank space separated entry
        entry = line.strip().split()
        ra = 15.*float(entry[0])
        dec = float(entry[1])
        sky.append((ra, dec))
        i = i + 1    
           
      except:
        pass
        

      
# How many sky objects found?

nsky = i
if nsky < 1:
  sys.exit('No objects found in %s' % (skyfile,))
  

# Read the wcs fits reference file and create the reference to the WCS data

inlist = pyfits.open(infile)
inhdr = inlist[0].header
inwcs = WCS(inhdr)

# Conversion is based on "1" pixel origin used in ds9 and aij
# Uses http://stsdas.stsci.edu/astrolib/pywcs/examples.html
# Convert sky list to numpy floating point array

sky_coord = np.array(sky, dtype=np.float32)
pix_coord = inwcs.wcs_world2pix(sky_coord, 1)

# Inverse transformation
#sky_coord = inwcs.wcs_pix2world(pix_coord,1)

# Close in the image file
inlist.close()

# Unpack the pix_coord numpy array
npix, nxy = pix_coord.shape

# Test that there are coordinates to write
if npix < 1:
  sysexit("No coordinates found. ")

# Open the output file for appending 
pixfp = open(pixfile, 'a')
  
for i in range(npix):
  x = pix_coord[i,0]
  y = pix_coord[i,1]
  if verboseflag:
    print(x, y)
  pixline = "%7.2f  %7.2f \n" % (x, y)   
  pixfp.write(pixline)

# Close the output file
pixfp.close()

exit()

