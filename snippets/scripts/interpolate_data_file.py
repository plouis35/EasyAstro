#!/usr/bin/python3

import sys
import numpy as np
# from scipy.interpolate import interp1d
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt

sfactorflag = True

if len(sys.argv) == 1:
  print(" ")
  print("Usage: interpolate_data.py indata.dat outdata.dat nout [sfactor]")
  print(" ")
  sys.exit("Interpolate data with a univariate spline\n")
elif len(sys.argv) == 4:
  infile = sys.argv[1]
  outfile = sys.argv[2]
  nout = int(sys.argv[3])
  sfactorflag = False
elif len(sys.argv) == 5:
  infile = sys.argv[1]
  outfile = sys.argv[2]
  nout = int(sys.argv[3])
  sfactor = float(sys.argv[4]) 
else:
  print(" ")
  print("Usage: interpolate_data.py indata.dat outdata.dat nout [sfactor]")
  print(" ")
  sys.exit("Interpolate data with a univariate spline\n")
  

# Take x,y coordinates from a plain text file

# Open the file with data
infp = open(infile, 'r')

# Read all the lines into a list
intext = infp.readlines()

# Split data text and parse into x,y values  

# Create empty lists

xdata = []
ydata = []
i = 0

for line in intext:

  try:
    # Treat the case of a plain text comma separated entry
    
    entry = line.strip().split(",") 

    # Get the x,y values for these fields
    xval = float(entry[0])
    yval = float(entry[1])
    xdata.append(xval)
    ydata.append(yval)
    i = i + 1    

  except:      
    
    try: 
      # Treat the case of a plane text blank space separated entry

      entry = line.strip().split()

      xval = float(entry[0])
      yval = float(entry[1])
      xdata.append(xval)
      ydata.append(yval)
      i = i + 1    
         
    except:
      pass
      
      
# How many points found?

nin = i
if nin < 1:
  sys.exit('No objects found in %s' % (infile,))

# Import  data into a np arrays

# Generate sample data
x = np.array(xdata)
y = np.array(ydata)

# Function to interpolate the data with a linear interpolator
# f_interpolated = interp1d(x, y, kind='linear')

# Function to interpolate the data with a univariate cubic spline

if sfactorflag:
  f_interpolated = UnivariateSpline(x, y, k=3, s=sfactor)
else:
  f_interpolated = UnivariateSpline(x, y, k=3)

# Values of x for sampling inside the boundaries of the original data
x_interpolated = np.linspace(x.min(),x.max(), nout)

# New values of y for these sample points
y_interpolated = f_interpolated(x_interpolated)


# Create an plot with labeled axes
plt.figure().canvas.set_window_title(infile)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Interpolation')
plt.plot(x, y,   color='red', linestyle='None', 
 marker='.', markersize=10., label='Data')
plt.plot(x_interpolated, y_interpolated, color='blue', linestyle='-', 
 marker='None', label='Interpolated', linewidth=1.5)
plt.legend()
plt.minorticks_on()
plt.show()

# Open the output file
outfp = open(outfile, 'w')
  
# Write the interpolated data
for i in range(nout):   
  outline = "%f  %f\n" % (x[i],y[i])
  outfp.write(outline)

# Close the output file
outfp.close()

exit()
