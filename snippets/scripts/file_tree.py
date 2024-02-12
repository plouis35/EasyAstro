#!/usr/bin/python3
'''Walk a directory tree and list the files'''

import os
import sys
import fnmatch
import string
import subprocess
import pyfits

if len(sys.argv) != 3:
 print(" ")
 sys.exit("Usage: list_files.py directory pattern\n")

toplevel = sys.argv[1]
pattern = sys.argv[2]

print(toplevel)
print(pattern)


for dirname, dirnames, filenames in os.walk(toplevel):
  for filename in fnmatch.filter(filenames, pattern):
    fullfilename = os.path.join(dirname, filename)
  
    try:    
      print(fullfilename)
        
    except IOError: 
      print('Error opening ', fullfilename)
      break       

exit()
