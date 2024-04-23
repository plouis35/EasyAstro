#!/usr/bin/python3

# Gaussfit
# Interactive fitting data with a sum of gaussians
#
# Copyright (c) 2014 John Kielkopf
# kielkopf@louisville.edu

# This software is licensed under terms of the MIT License.

# July 24, 2014
# Version 2.0


 # Use true division everywhere

import os
import sys
import numpy as np
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
from   matplotlib.widgets import Slider
from   matplotlib.widgets import RadioButtons
from   matplotlib.widgets import Button

# Set the sensitivity of the sliders

sens = 0.0001

# Use mean values as reference points 

xmean = 0.
ynmean = 0.

# Data are in numpy arrays
# Parameters are manipulated in numpy arrays bnp for background and gnp for Gaussian lineshape
# Parameters passed for fitting only as immutable tuples

# Gaussian fitting function

def fitsumg(x, *p):
  # Use to fit Gaussians for the sum of ng Gaussians on a quadratic baseline
  # x is a numpy array of x values
  # f is a numpy array of y values
  # *p points to a tuple of ng*3 gaussian parameters
  #
  # Requires global numpy array bnp for background parameters
  # Requires ng for number of gaussians
      
  # How many Gaussians?
  # Use length of parameter array rather than common storage
      
  n = len(p)

  f = bnp[0] + bnp[1]*x + bnp[2]*x*x 
    
  for i in range(n):
    f = f + p[3*i]*np.exp(-((x-p[3*i + 1])/p[3*i + 2])**2)
  
  return f
  

# Background fitting function 

def fitbkg(x, *p):
  # Use to fit background for the sum of ng Gaussians on a quadratic baseline
  # x is a numpy array of x values
  # f is a numpy array of y values
  # *p points to a tuple of 3 background parameters
  #
  # Requires global numpy array gnp for Gaussian parameters
  # Requires ng for number of gaussians

  # How many Gaussians?
  # Note that shape returns (nrows, ncols)
      
  n, m = np.shape(gnp)
     
  f = p[0] + p[1]*x + p[2]*x*x
    
  for i in range(n):
    f = f + gnp[i,0]*np.exp(-((x-gnp[i,1])/gnp[i,2])**2)
  
  return f


# Lineshape function 

def lineshape(x):
  # Find the sum of ng Gaussians on a quadratic background
  # x is a numpy array of x values
  # f is a numpy array of y values
  #
  # Requires global numpy arrays bnp for background and gnp for Gaussian
  
  # How many Gaussians?
  # Note that shape returns (nrows, ncols)
      
  n, m = np.shape(gnp)

  # Start with the background 
  
  f = bnp[0] + bnp[1]*x + bnp[2]*x*x 
  
  # Add all the Gaussians
  # Note that numpy arrays are indexed [row, col]
    
  for i in range(n):
    f = f + gnp[i,0]*np.exp(-((x-gnp[i,1])/gnp[i,2])**2)
  
  return f

# Read the command line

if len(sys.argv) == 1:
  print(" ")
  print("Usage: gaussfit.py inspectrum.dat inpar.dat outpar.dat outspectrum.dat")
  print(" ")
  print("Compare spectrum to a sum of gaussians on a quadratic baseline")
  sys.exit("\n")
elif len(sys.argv) == 5:
  spectrumfile = sys.argv[1]
  inparfile = sys.argv[2]
  outparfile = sys.argv[3]
  outspecfile = sys.argv[4]
else:
  print(" ")
  print("Usage: gaussfit.py inspectrum.dat inpar.dat outpar.dat outspectrum.dat")
  print(" ")
  sys.exit("Compare spectrum to a sum of gaussians on a quadratic baseline\n")


# Open the file with input spectrum

spectrumfp = open(spectrumfile, 'r')


# Read all the spectrum line by line into a list

spectrumtext = spectrumfp.readlines()


# Close the input spectrum file

spectrumfp.close()


# Parse the data from in text file

i = 0
xnlist = []
ynlist = []

for line in spectrumtext:

  try:    
    # Treat the case of a plain text comma separated entry
    
    entry = line.strip().split(",")  
    # Get the x,y values for this point 
    xp = float(entry[0])
    yp = float(entry[1])
    xnlist.append((xp))
    ynlist.append((yp))
    i = i + 1    
  except:      
     
    try: 
      # Treat the case of a plane text blank space separated entry
      entry = line.strip().split()
      xp = float(entry[0])
      yp = float(entry[1])
      xnlist.append((xp))
      ynlist.append((yp))
      i = i + 1    
         
    except:   
      pass
      

# How many data points were found?

nnpts = i
if nnpts < 1:
  sys.exit('No data found in %s' % (spectrumfile,))
else:
  print('\n')
  print('Comparing %d points in %s\n\n' % (nnpts, spectrumfile))
     

# Convert the x and y data lists to numpy arrays

xndata = np.array(xnlist, dtype=np.float32)
yndata = np.array(ynlist, dtype=np.float32)
xdata = np.copy(xndata)
npts = nnpts
  

# Open the file with input parameters

inparfp = open(inparfile, 'r')


# Read the parameters line by line

inpartext = inparfp.readlines()


# Close the input parameters file

inparfp.close()

# Separate the parameter text into two lists

i = 0
inbparlist = []
ingparlist = []

for line in inpartext:
  
  try:    
    
    entry = line.strip().split()
    if i < 1 :
      
      # Parse the baseline parameters
      inbparlist.append(float(entry[0]))
      inbparlist.append(float(entry[1]))
      inbparlist.append(float(entry[2]))
    else:
    
      # Parse the Gaussian parameters
      ingparlist.append(float(entry[0]))
      ingparlist.append(float(entry[1]))
      ingparlist.append(float(entry[2]))

    i = i + 1    

  except:      

    pass
      
# Convert the two parameter lists into immutable tuples 
 
inbpar = tuple(inbparlist)
ingpar = tuple(ingparlist)


# How many Gaussians are to be added?

ng = int(len(ingpar)/3)

print("Fitting %d Gaussians ...\n" % ng)

if ng < 1:
  sys.exit('The program requires parameters for the baseline and 1 or more gaussians in %s' % (inparfile,))


# Create numpy arrays from the parameter tuples

# Background has 3 elements and it is properly shaped

bnp0 = np.array(inbpar)

# Gaussian has np*3 parameters and it has to be reshaped

gnp0 = np.array(ingpar)
gnp0.shape = (ng,3)


# Make a working copy of the initial parameter arrays
# We use the initial parameters later for resets when requested

bnp = np.copy(bnp0)
gnp = np.copy(gnp0)


# Calculate a spectrum based on these parameters

ydata = lineshape(xdata)

# Find useful values for scaling
ynmin = np.amin(yndata)
ynmax = np.amax(yndata)
ynmean = np.mean(yndata)
ymin = np.amin(ydata)
ymax = np.amax(ydata)
xmin = np.amin(xdata)
xmax = np.amax(xdata)
xmean = np.mean(xdata)
yndel = ynmax - ynmin
ydel = ymax - ymin
xdel = xmax - xmin


# Create a plot for the input and calculated spectra

thisfig = plt.figure()
thisfig.canvas.set_window_title('Gaussian')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Fit to %d Gaussians' %(ng,))
p, = plt.plot(xndata, yndata, color='blue', linestyle='solid', linewidth=1.5, label='Input')
q, = plt.plot(xdata, ydata, color='red', linestyle='None', marker='.',label='Fit')
plt.legend()
plt.minorticks_on()


# Add controls

plt.subplots_adjust(left=0.15, bottom=0.25) 

nc = int(1)


fba = plt.axes([0.35, 0.12, 0.35, 0.03])
fsa = Slider(fba, 'a', -1.0*sens, 1.*sens, valinit=0.0)
fbb = plt.axes([0.35, 0.07, 0.35, 0.03])
fsb = Slider(fbb, 'b', -1.0*sens, 1.*sens, valinit=0.0)
fbc = plt.axes([0.35, 0.02, 0.35, 0.03])
fsc = Slider(fbc, 'c', -1.0*sens,  1.*sens, valinit=0.0)

ngt = tuple(range(0,ng+1))
fbn = plt.axes([0.02, 0.04, 0.08, 0.12])
frn = RadioButtons(fbn, ngt, active=1)

fbp = plt.axes([0.15, 0.04, 0.1, 0.1])
fpp = Button(fbp, 'Reset')

fbr = plt.axes([0.8, 0.04, 0.1, 0.1])
fpr = Button(fbr, 'Refit')


# Update the plot after changing the "a" parameter

def fa_update(val):
  global bnp, gnp, q, ydata
  if nc == 0:
    # Move the baseline up and down
    bnp[0] = bnp[0] + val*yndel
  else:
    # Change the height of the gaussian
    gnp[nc-1,0] = gnp[nc-1,0] + val*yndel
  ydata = lineshape(xdata)
  q.set_ydata(ydata)
  plt.draw();
  

# Update the plot after changing the "b" parameter

def fb_update(val):
  global bnp, gnp, q, ydata
  if nc == 0:
    # Change the baseline slope
    bnp[1] = bnp[1] + val*yndel/xdel
  else:
    # Change the gaussian width
    gnp[nc-1,1] = abs(gnp[nc-1,1]) + val*xdel
  ydata = lineshape(xdata)
  q.set_ydata(ydata)
  plt.draw();


# Update the plot after changing the "c" parameter

def fc_update(val):
  global bnp, gnp, q, ydata
  if nc == 0:
    # Change the baseline curvature
    bnp[2] = bnp[2] + val*yndel/(xdel*xdel)
  else:
    # Change the gaussian center
    gnp[nc-1,2] =  gnp[nc-1,2] + val*xdel
  ydata = lineshape(xdata)
  q.set_ydata(ydata)
  plt.draw();


# Select a new component

def fn_update(val):
  global nc
  nc = int(val);


# Refit the input data with current parameters

def fr_update(event):
  global bnp, gnp, covar_gnp, covar_bnp, q, ydata
  fsa.reset()
  fsb.reset()
  fsc.reset() 

  # Fit starting with  the latest parameters
  # The fitting code requires tuples and returns numpy arrays
 
  newpar = tuple(bnp)
  neval = 100*(len(xndata) + 1)
  bnp, covarb = curve_fit(fitbkg, xndata, yndata, p0=newpar, maxfev=neval )
  
  n, m = gnp.shape
  gnp.shape  = (n*m)
  newpar = tuple(gnp)
  neval = 100*(len(xndata) + 1)
  gnp, covarg = curve_fit(fitsumg, xndata, yndata, p0=newpar, maxfev=neval )

  
  # Shape the fitted parameter array back to ng_x_3 for use elsewhere
  
  gnp.shape = (n, 3)


  # Calculate the fitted spectrum

  ydata = lineshape(xdata)
  q.set_ydata(ydata)
  plt.draw();
  
  
# Reset the parameters for the selected component to the input values

def fp_update(event):
  global bnp, gnp, p, q, nc
  fsa.reset()
  fsb.reset()
  fsc.reset() 

  if nc == 0:
    bnp[:] = bnp0[:] 
  else:
    gnp[nc,:] = gnp0[nc,:]
  
  # Plot but do not fit to the new parameters
  
  ydata = lineshape(xdata)
  q.set_ydata(ydata)
  plt.draw();
   

fsa.on_changed(fa_update)
fsb.on_changed(fb_update)
fsc.on_changed(fc_update)
frn.on_clicked(fn_update)
fpr.on_clicked(fr_update)
fpp.on_clicked(fp_update)

plt.show()


# We have accepted the last fitting
# Recalculate the fitted spectrum

ydata = lineshape(xdata)


# Open the output spectrum file for overwriting (use 'a' for appending)

outspecfp = open(outspecfile, 'w')

for i in range(npts):
  xp = xdata[i]
  yp = ydata[i]
  outline = "%f  %f\n" % (xp, yp)   
  outspecfp.write(outline)

outspecfp.close()


# Open the output file with the fitting parameters

outparfp = open(outparfile, 'w')

# The first line is the quadratic baseline

parline = "%f  %f  %f\n" % (bnp[0], bnp[1], bnp[2]) 
outparfp.write(parline)

# The remaining lines are the Gaussian parameters

for i in range(ng):
  parline = "%f  %f  %f\n" % (gnp[i,0], gnp[i,1], gnp[i,2]) 
  outparfp.write(parline)

parline = "\n"
outparfp.write(parline)

# Now find the standard deviation for each fitted parameter
# Organize them in the same way that the parameters were written

for j in range(3):  
  stddev = np.sqrt(covarb[j,j])
  parline = "%e  " % (stddev,) 
  outparfp.write(parline)
parline = "\n"
outparfp.write(parline)  

for i in range(ng):
  for j in range(3):  
    k = i*3 + j
    stddev = np.sqrt(covarg[k,k])
    parline = "%e  " % (stddev,) 
    outparfp.write(parline)
  parline = "\n"
  outparfp.write(parline)  

# Close the file

outparfp.close()

exit()
