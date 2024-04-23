#!/usr/bin/python

# Process full frame fits images in a directory based on a configuration file
#
# Copyright 2018 John Kielkopf
#
#

import os
import sys
import fnmatch
import pyfits
import string
import subprocess

if len(sys.argv) != 2:
  print " "
  sys.exit("Usage: process_fits.py dir \n")
  exit()

toplevel = sys.argv[-1]

# Define system scripts to run astrometry eo
# subprocess.call(["/usr/local/bin/solve-field-cdk20-2-ra-dec", rahms, decdms, infilename, outfilename])
# subprocess.call(["/usr/local/bin/solve-field-cdk20-2", infilename, outfilename])

astrometry_known_field = "/usr/local/bin/solve-field-cdk20-2-ra-dec"
astrometry_unknown_field = "/usr/local/bin/solve-field-cdk20-2"

# Assign a default for an undefined file

nofile      = ""

# These are typical placeholders for values that will be read from a prefs file

darkfile   = nofile
biasfile   = nofile
flatfile   = nofile
flatfile_default = nofile
flatfile_g = nofile
flatfile_r = nofile
flatfile_i = nofile
flatfile_z = nofile
flatfile_bb = nofile
flatfile_U = nofile
flatfile_B = nofile
flatfile_V = nofile
flatfile_R = nofile
flatfile_I = nofile
flatfile_ha = nofile
flatfile_og = nofile
flatfile_open = nofile


rahms = "12:22:33"
decdms = "+12:34:56"

if len(sys.argv) != 2:
  print " "
  sys.exit("Usage: process_fits.py directory\n")
  exit()

prefsfilename = "process.prefs"
prefsfp = open(prefsfilename,'r')
if not prefsfp:
  print "Edit a process.prefs file for this directory."
  exit(1)

# Parse the prefs file and assign internal variables for various selected options

for newline in prefsfp:
  items = newline.split('=')
  if len(items) !=2:
    pass
  if items[0].strip() == 'dark' :    
    darkfile = items[1].strip()
  if items[0].strip() == 'bias' :
    biasfile = items[1].strip()
  if items[0].strip() == 'flat' :
    flatfile = items[1].strip()
    
  if items[0].strip() == 'flat' :
    flatfile_default = items[1].strip()
  if items[0].strip() == 'flat_g' :
    flatfile_g = items[1].strip()
  if items[0].strip() == 'flat_r' :
    flatfile_r = items[1].strip()
  if items[0].strip() == 'flat_i' :
    flatfile_i = items[1].strip()
  if items[0].strip() == 'flat_z' :
    flatfile_z = items[1].strip()
  if items[0].strip() == 'flat_bb' :
    flatfile_bb = items[1].strip()      
  if items[0].strip() == 'flat_U' :
    flatfile_U = items[1].strip()
  if items[0].strip() == 'flat_B' :
    flatfile_B = items[1].strip()
  if items[0].strip() == 'flat_V' :
    flatfile_V = items[1].strip()
  if items[0].strip() == 'flat_R' :
    flatfile_R = items[1].strip()
  if items[0].strip() == 'flat_I' :
    flatfile_I = items[1].strip()
  if items[0].strip() == 'flat_ha' :
    flatfile_ha = items[1].strip()
  if items[0].strip() == 'flat_og' :
    flatfile_og = items[1].strip()
  if items[0].strip() == 'flat_open' :
    flatfile_open = items[1].strip()           
  if items[0].strip() == 'ra' :
    rahms = items[1].strip()
  if items[0].strip() == 'dec' :
    decdms = items[1].strip()


print 'Preferences for this directory: \n'
print 'Dark file ', darkfile
print 'Bias file ', biasfile
print 'Flat file default', flatfile_default 
print 'Flat file r', flatfile_g  
print 'Flat file r', flatfile_r   
print 'Flat file i', flatfile_i   
print 'Flat file z', flatfile_z   
print 'Flat file U', flatfile_U
print 'Flat file B', flatfile_B
print 'Flat file V', flatfile_V 
print 'Flat file R', flatfile_R
print 'Flat file I', flatfile_I 
print 'Flat file bb', flatfile_bb
print 'Flat file og', flatfile_og  
print 'Flat file ha', flatfile_ha

print 'Field RA ', rahms
print 'Field Dec ', decdms         

print 'Processing ... \n'


# Search for files with this extension
pattern = '*.fits'

for dirname, dirnames, filenames in os.walk(toplevel):
  for filename in fnmatch.filter(filenames, pattern):
    fullfilename = os.path.join(dirname, filename)
    
    try:    
    
      # Open a fits image file
      hdulist = pyfits.open(fullfilename)
      
    except IOError: 
      print 'Error opening ', fullfilename
      break       
    
    # Initialize flags and parameters for this file
    imdark = False        
    imflat = False
    imbias = False
    imwcs = False
    imfilter = ""
    imhistory = ""

    # Get the primary image header
    prihdr = hdulist[0]

    # Set flag if the file has WCS                
    if 'WCSAXES' in prihdr.header:
      imwcsaxes = prihdr.header['WCSAXES']
      imwcs = True
            
    # Set flag if the file has been dark, bias or flat corrected
    if 'HISTORY' in prihdr.header:
      imhistory = prihdr.header['HISTORY']
      for line in imhistory:
        if "Dark" in line:
          imdark = True
        if "Flat" in line:  
          imflat = True
        if "Bias" in line:  
          imbias = True

    # If there is a filter in the header set the flat field file
    # These files were defined by default and modified by the configuration file
    if 'FILTER' in prihdr.header:
      imfilter = prihdr.header['FILTER']
      if "g_" in imfilter:
        flatfile=flatfile_g

      if "r_" in imfilter:
        flatfile=flatfile_r

      if "i_" in imfilter:
        flatfile=flatfile_i

      if "z_" in imfilter:
        flatfile=flatfile_z

      if "bb_" in imfilter:
        flatfile=flatfile_bb

      if "U_" in imfilter:
        flatfile=flatfile_U

      if "B_" in imfilter:
        flatfile=flatfile_B

      if "V_" in imfilter:
        flatfile=flatfile_V

      if "R_" in imfilter:
        flatfile=flatfile_R

      if "I_" in imfilter:
        flatfile=flatfile_I

      if "Halpha_" in imfilter:
        flatfile=flatfile_ha

      if "og_" in imfilter:
        flatfile=flatfile_og

      if "open" in imfilter:
        flatfile=flatfile_open

      if flatfile == nofile:
        flatfile = flatfile_default

    # Act on values of the flags in the header      
                        
    print ' Processing ... '
    
    # Base output file name on input file name adding descriptive codes
    
    infilename = filename
    
    # Dark and bias correct files that have not been been already and are not dark, bias or flat reference files
    
    if not imdark and not imbias  and 'dark' not in filename and 'bias' not in filename and 'flat' not in filename:

      # If there is no bias file then use the dark file alone

      if darkfile != nofile and biasfile == nofile:
        outfilename = os.path.splitext(os.path.basename(infilename))[0]+'_d.fits'
        subprocess.call(["/usr/local/bin/fits_dark.py", infilename, darkfile, outfilename]) 
        imdark = True
        print filename, "dark subtracted to", outfilename
        infilename = outfilename
        
      # If there is a bias file then use a scaled dark regardless of exposure times  
        
      elif darkfile != nofile and biasfile != nofile:  
        print "Using scaled dark for ", filename, " ."
        outfilename = os.path.splitext(os.path.basename(infilename))[0]+'_d.fits'
        subprocess.call(["/usr/local/bin/fits_scaled_dark.py", infilename, darkfile, biasfile, outfilename]) 
        imdark = True
        print filename, "scaled dark subtracted to", outfilename
        infilename = outfilename
        
      # Otherwise do not process  
        
      else:
        print filename, "not processed for bias or dark correction"
        pass  
    
    # Flat correct files that have not been already and are dark corrected
    # The appropriate flatfile was assigned based on the image header and the configuration file
                       
    if not imflat and imdark and 'flat' not in filename and 'dark' not in filename and 'bias' not in filename:          
      if flatfile != nofile:
        outfilename = os.path.splitext(os.path.basename(infilename))[0]+'f.fits' 
        subprocess.call(["/usr/local/bin/fits_flat.py", infilename, flatfile, outfilename]) 
        imflat = True 
        print infilename, "flatfielded to", outfilename
        infilename = outfilename
      else:  
        print filename, "not corrected for flat field response"

    # Add a WCS header to any image file that does not have one and is not a calibration file
        
    if (not imwcs) and ('flat' not in filename) and ('bias' not in filename) and ('dark' not in filename):     
      outfilename = os.path.splitext(os.path.basename(infilename))[0]+'w.fits'
      if rahms == "" or decdms == "": 
        subprocess.call([astrometry_unknown_field, infilename, outfilename]) 
        print ("Processed for WCS", infilename)
      else:
        subprocess.call([astrometry_known_field, rahms, decdms, infilename, outfilename])
        print ("Processed for WCS", infilename)
    else:
      print ("Not processed for WCS", infilename)


# Clean up from the WCS processing using astrometry.net in the event these are left by the scripts
        
os.system("rm *.axy")
os.system("rm *.corr")
os.system("rm *indx.png")
os.system("rm *.rdls")
os.system("rm *.solved")
os.system("rm *.wcs")
os.system("rm *.match")
os.system("rm *.xyls")        
os.system("rm *-objs.png")        



