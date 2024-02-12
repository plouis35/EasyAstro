#!/usr/bin/python3

import sys

if len(sys.argv) == 1:
  sys.exit("Usage: ngc_reader.py ngc_object")
  exit()
elif len(sys.argv) == 2:
  test = sys.argv[1]
  if (test[0:3] == 'NGC') | (test[0:3] == 'ngc'):
    ngc_object = test[3:]
  elif (test[0:1] == 'N') | (test[0:1] == 'n'):
    ngc_object = test[1:]
  elif (test[0:2] == 'IC') | (test[0:2] == 'ic'):
    ngc_object = 'I' + test[2:]
  elif (test[0:1] == 'I') | (test[0:1] == 'i'):
    ngc_object = 'I' + test[1:]
  else:
    ngc_object = test       
else:
  sys.exit("Usage: Usage: ngc_reader.py ngc_object")
  exit() 

# Open the catalog
ngc_file = open('ngc2000.dat', 'r')

# Read all the lines at one time into a list
ngc_lines = ngc_file.readlines()

# Close the catalog
ngc_file.close()

# The NGC catalog as missing fields for some entries
# Requires reading the full line and parsing the columns later

# Create a dictionary of the catalog entries with \n removed
i = 0
for entries in ngc_lines:
  if i == 0:
    ngc_catalog = {ngc_lines[i].split()[0] : ngc_lines[i].strip()}
  else:
    ngc_catalog[ngc_lines[i].split()[0]] = ngc_lines[i].strip()
  i = i + 1 


# Find the object in the dictionary
ngc_listing = ngc_catalog.get(ngc_object, None)
if ngc_listing is None:
  print('Could not find ', ngc_object)
  exit()

# Find the entries by column
# This catalog uses blank fields for some entries
ngc_id = ngc_listing[0:5]
ngc_type = ngc_listing[6:9]
ngc_ra_hr = ngc_listing[9:12]
ngc_ra_min = ngc_listing[12:17]
ngc_dec_deg = ngc_listing[17:22]
ngc_dec_min = ngc_listing[22:25]
ngc_constellation = ngc_listing[28:32]
ngc_size_arcmin = ngc_listing[32:38]
ngc_magnitude = ngc_listing[38:43]
ngc_description = ngc_listing[43:96]
  
# Augment the name with NGC or IC if appropriate
if ngc_id[0] != 'I':
  name = 'NGC' + ngc_id
elif ngc_id[0] == 'I':
  name = 'IC'+ngc_id[1:]

# Calculate the RA and Dec
ra = float(ngc_ra_hr) + float(ngc_ra_min)/60.

dec = float(ngc_dec_deg)
if dec < 0.:
  dec = dec - float(ngc_dec_min)/60.
else:
  dec = dec + float(ngc_dec_min)/60.

# Calculate the size in arcseconds if we have data
try:
  size = 60.*float(ngc_size_arcmin)
except:
  size = -99.
  
# Use a numerical magnitude if we have data
try:
  magnitude = float(ngc_magnitude)   
except:
  magnitude = -99.
  
# Description
description = ngc_description

print('Name:',name)
print('RA (h):', '%7.3f' % ra)
print('Dec (deg):', '%7.3f' % dec) 
print('Size (arceconds):', '%4.1f' % size)
print('Integrated magnitude:', '%4.1f' % magnitude)
print('Description:', description)
print('\n')

exit()

