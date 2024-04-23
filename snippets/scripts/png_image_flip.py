#!/usr/bin/python3

# Flip an image left-right

import os
import sys
import argparse

# If math processing is going to be needed add
#import math

import Image as pil

parser= argparse.ArgumentParser(description = 'Flip a png image left-to-right')

if len(sys.argv) == 1:
  sys.exit("Usage: png_image_flip file.png ")
  exit()
elif len(sys.argv) == 2:
  infilename = sys.argv[1]
else:
  sys.exit("Usage: png_image_flip file.png ")
  exit() 

myimage = pil.open(infilename)

mirror = myimage.transpose(pil.FLIP_LEFT_RIGHT)
outfilename = os.path.splitext(os.path.basename(infilename))[0]+'_flip.png'
mirror.save(outfilename)

exit()
