#!/usr/bin/python3

# Gaussfittwo
# Interactive fitting data with a Gaussian
#
# Copyright (c) 2014 John Kielkopf
# kielkopf@louisville.edu

# This software is licensed under terms of the MIT License.

# August 1, 2014
# Version 2.1


 # Use true division everywhere

import os
import sys
import numpy as np
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt
from   matplotlib.widgets import Slider
from   matplotlib.widgets import RadioButtons
from   matplotlib.widgets import Button

global bnp, gnp

# Set the sensitivity of the sliders

sens = 0.01

# Data are in numpy arrays
# Parameters are manipulated in numpy arrays 
# Use bnp for background and gnp for Gaussian lineshape
# Parameters individually passed for fitting

# Gaussian fitting function

def fitg(x, g0, g1, g2, g3, g4, g5):
  # Use to fit a Gaussian for a quadratic baseline
  # x is a numpy array of x values
  # f is a numpy array of y values
  #
  # Requires numpy array bnp for background parameters
            
  f = bnp[0] + bnp[1]*x + bnp[2]*x*x 
    
  f = f + g0*np.exp(-((x-g1)/g2)**2) + g3*np.exp(-((x-g4)/g5)**2)
  
  return f
  

# Background fitting function 

def fitb(x, b0, b1, b2):
  # Use to fit background under a Gaussian line
  # x is a numpy array of x values
  # f is a numpy array of y values
  #
  # Requires numpy array gnp for Gaussian parameters
     
  f = b0 + b1*x + b2*x*x
    
  f = f + gnp[0,0]*np.exp(-((x-gnp[0,1])/gnp[0,2])**2)
  f = f + gnp[1,0]*np.exp(-((x-gnp[1,1])/gnp[1,2])**2)
  
  return f


# Lineshape function 

def lineshape(x):
  # Find the sum of a Gaussians on a quadratic background
  # x is a numpy array of x values
  # f is a numpy array of y values
  #
  # Requires numpy arrays bnp for background and gnp for Gaussian
  # Requires ng for number of gaussians

  # Start with the background 
  
  f = bnp[0] + bnp[1]*x + bnp[2]*x*x 
  
  # Add all the Gaussians
  # Note that numpy arrays are indexed [row, col]
    
  f = f + gnp[0,0]*np.exp(-((x-gnp[0,1])/gnp[0,2])**2)
  f = f + gnp[1,0]*np.exp(-((x-gnp[1,1])/gnp[1,2])**2)
  
  return f
  

# Read the command line

if len(sys.argv) == 1:
  print(" ")
  print("Usage: gaussfittwo.py inspectrum.dat inpar.dat outpar.dat outspectrum.dat")
  print(" ")
  print("Compare spectrum to a Gaussian on a quadratic baseline")
  sys.exit("\n")
elif len(sys.argv) == 5:
  spectrumfile = sys.argv[1]
  inparfile = sys.argv[2]
  outparfile = sys.argv[3]
  outspecfile = sys.argv[4]
else:
  print(" ")
  print("Usage: gaussfittwo.py inspectrum.dat inpar.dat outpar.dat outspectrum.dat")
  print(" ")
  sys.exit("Compare spectrum to a Gaussian on a quadratic baseline\n")


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

xndata = np.array(xnlist, dtype=np.float64)
yndata = np.array(ynlist, dtype=np.float64)
xdata = np.copy(xndata)
npts = nnpts
  

# Open the input parameter file

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

# Does the user know this is the one-Gaussian version

if ng <= 1:
  sys.exit('The program requires parameters for the baseline and 2 Gaussians in %s' % (inparfile,))

if ng == 2:
  print("Fitting 2 Gaussians ...\n") 
else:
  print("This program does not support fitting %d Gaussians ...\n" %ng)
  sys.exit()

# Create numpy arrays from the parameter tuples

bnp0 = np.array(inbpar)
gnp0 = np.array(ingpar)
gnp0.shape = (ng,3)

# Make a working copies of the initial parameter arrays
# We use the initial parameters later for resets when requested

bnp = np.copy(bnp0)
gnp = np.copy(gnp0)


# Calculate a spectrum based on these parameters

ydata = lineshape(xdata)


# Find useful values for scaling the interactive plot sliders

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
fittedflag = False

# Create a plot for the input and calculated spectra

thisfig = plt.figure()
thisfig.canvas.set_window_title('Gaussian')
plt.xlabel('X')
plt.ylabel('Y')

if ng == 1:
  plt.title('Fit to %d Gaussian' %(ng,))
else:
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
    bnp[0] = bnp[0] + 10.*val*yndel
  else:
    # Change the height of the Gaussian
    gnp[nc-1,0] = gnp[nc-1,0] + 10.*val*yndel
  ydata = lineshape(xdata)
  q.set_ydata(ydata)
  plt.draw();
  

# Update the plot after changing the "b" parameter

def fb_update(val):
  global bnp, gnp, q, ydata
  if nc == 0:
    # Change the baseline slope
    db = val*yndel/xdel
    bnp[1] = bnp[1] + db
    # Also change the baseline level to keep it within the viewport
    bnp[0] = bnp[0] - db*xmean
  else:
    # Change the gaussian center
    gnp[nc-1,1] = gnp[nc-1,1] + val*xdel
  ydata = lineshape(xdata)
  q.set_ydata(ydata)
  plt.draw();


# Update the plot after changing the "c" parameter

def fc_update(val):
  global bnp, gnp, q, ydata
  
  if nc == 0:
    # Change the baseline curvature
    dc = val*yndel/(xdel*xdel)
    bnp[2] = bnp[2] + dc
    # Also change the baseline level to keep it within the viewport
    bnp[0] = bnp[0] - dc*xmean*xmean   
  else:
    # Change the gaussian width
    gnp[nc-1,2] =  abs(gnp[nc-1,2]) + val*xdel
  ydata = lineshape(xdata)
  q.set_ydata(ydata)
  plt.draw();


# Select a new component

def fn_update(val):
  global nc
  nc = int(val);


# Refit the input data with current parameters

def fr_update(event):
  global bnp, gnp, covarg, covarb, q, ydata, fittedflag
  
  # Set a flag that the data have been fitted
  
  fittedflag = True
  
  fsa.reset()
  fsb.reset()
  fsc.reset() 

  # Fit starting with  the latest parameters
  
  bp0 = bnp[0]
  bp1 = bnp[1]
  bp2 = bnp[2]
  bnp, covarb = curve_fit(fitb, xndata, yndata, p0=(bp0, bp1, bp2))

  gp0 = gnp[0,0]
  gp1 = gnp[0,1]
  gp2 = gnp[0,2]
  gp3 = gnp[1,0]
  gp4 = gnp[1,1]
  gp5 = gnp[1,2]
  gnp, covarg = curve_fit(fitg, xndata, yndata, p0=(gp0, gp1, gp2, gp3, gp4, gp5))
  gnp.shape = (ng,3)
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
    gnp[nc-1:] = gnp0[nc-1:]
  
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


# Open the output spectrum file for overwriting (use 'a' for appending)

outspecfp = open(outspecfile, 'w')

for i in range(npts):
  xp = xdata[i]
  yp = ydata[i]
  outline = "%f  %f\n" % (xp, yp)   
  outspecfp.write(outline)

outspecfp.close()

# Prepare to report the fitting parameters

stddevb = np.zeros(3, dtype=np.float64)
stddevg = np.zeros(3*ng, dtype=np.float64)
stddevg.shape = (ng,3)

if fittedflag is True:
  for j in range(3):
    try:      
      stddevb[j] = np.sqrt(covarb[j,j])
    except (RuntimeError, TypeError):
      pass
  for i in range(ng):
    for j in range(3):
      k = i*3 + j
      try:      
        stddevg[i,j] = np.sqrt(covarg[k,k])
      except (RuntimeError, TypeError):
        pass

# Open the output file with the fitting parameters

outparfp = open(outparfile, 'w')


# Report the background parameters

parline = "%f  %f  %f\n" % (bnp[0], bnp[1], bnp[2]) 
outparfp.write(parline)

print("\nGaussian fitting of %s\n" % spectrumfile)

print("\nRegion from %f to %f with mean %f" % (xmin, xmax, xmean))

print("\nBackground b0: %f +/- %f" % (bnp[0], stddevb[0]))
print("Background b1: %f +/- %f" % (bnp[1], stddevb[1]))
print("Background b2: %f +/- %f" % (bnp[2], stddevb[2]))

background = bnp[0] + bnp[1]*xmean + bnp[2]*xmean*xmean

print("\nBackground local mean: %f" % background)

slope = bnp[1] + 2.*bnp[2]*xmean

print("Background local slope: %f" % slope)

curvature = 2. * bnp[2] / (1. + slope**2)**1.5

print("Background local curvature: %f" % curvature)



# Report the Gaussian parameters

for i in range(ng):
  parline = "%f  %f  %f\n" % (gnp[i,0], gnp[i,1], gnp[i,2]) 
  outparfp.write(parline)
  print("\nGaussian %d:\n" % i)
  print("  Height: %f +/- %f" %        (gnp[i,0], stddevg[i,0]))
  print("  Center: %f +/- %f" %        (gnp[i,1], stddevg[i,1]))
  print("  Width (1/e): %f +/- %f\n" % (gnp[i,2], stddevg[i,2]))
  fwhm = 2.*np.sqrt(2)*np.log(2)*gnp[i,2]
  stddevfwhm = 2.*np.sqrt(2.)*np.log(2.)*stddevg[0,2]
  area = np.sqrt(np.pi)*gnp[i,2]*gnp[i,0]
  arg0 = stddevg[i,0]*gnp[i,2]
  arg1 = stddevg[i,2]*gnp[i,0]
  stddevarea = np.sqrt(np.pi)*np.sqrt(arg0*arg0 + arg1*arg1)
  print("  FWHM: %f +/- %f" % (fwhm, stddevfwhm))
  print("  Area: %f +/- %f\n" % (area, stddevarea))
  outparfp.write(parline)

parline = "\n"
outparfp.write(parline)

# Append standard deviations to the output parameter file

for j in range(3):  
  parline = "%e  " % (stddevb[j],) 
  outparfp.write(parline)
parline = "\n"
outparfp.write(parline)  
for i in range(ng):
  for j in range(3):    
    parline = "%e  " % (stddevg[i,j],) 
    outparfp.write(parline)
  parline = "\n"
  outparfp.write(parline)  

# Close the file

outparfp.close()

exit()
