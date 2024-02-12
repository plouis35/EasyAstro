#!/usr/bin/python3

# Rotate an image 90 degrees 
# Apply successively for 180 and 270 degree rotations

import os
import sys
import argparse

# If math processing is going to be needed add
#import math

import Image as pil

parser= argparse.ArgumentParser(description = 'Rotate a png image 90 degrees')

if len(sys.argv) == 1:
  sys.exit("Usage: png_image_rotate file.png ")
  exit()
elif len(sys.argv) == 2:
  infilename = sys.argv[1]
else:
  sys.exit("Usage: png_image_rotate file.png ")
  exit() 

myimage = pil.open(infilename)

mirror = myimage.transpose(pil.ROTATE_90)
outfilename = os.path.splitext(os.path.basename(infilename))[0]+'_r90.png'
mirror.save(outfilename)

exit()
