#!/usr/bin/python3

import os
import sys
import fnmatch
import string
import csv

if len(sys.argv) == 1:
  print("")
  print("Usage: csv_to_txt.py infile.csv outfile.txt")
  print("")
  sys.exit("Read a csv spreadsheet and output as text\n")
elif len(sys.argv) == 3:
  infile = sys.argv[1]
  outfile = sys.argv[2]
else:
  print("")
  print("Usage: csv_to_txt.py infile.csv outfile.txt")
  sys.exit("Read a csv spreadsheet and output as text\n")

outfp = open(outfile, 'w')
infp = open(infile, 'r')

reader = csv.reader(infp)
nrow = 1

for newrow in reader:
  print(newrow)
  newline = ','.join(newrow)+'\n'       
  print(nrow, newline)
  outfp.write(newline)
  nrow = nrow +1
  
outfp.close()
infp.close()
exit()

