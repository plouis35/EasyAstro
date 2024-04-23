#!/usr/bin/python3

# Compute a sum of gaussians on a quadratic baseline

 # Use true division everywhere

import os
import sys
import numpy as np


# Select the backend or comment all and use the default
#import matplotlib as mpl
#mpl.use('wx')
#mpl.use('gtkagg')
#mpl.use('gtk3agg')
#mpl.use('tkagg')
#mpl.use('qt4agg')

import matplotlib.pyplot as plt
from   matplotlib.widgets import Slider
from   matplotlib.widgets import RadioButtons
from   matplotlib.widgets import Button


# Sum of baseline and gaussians
def sumgaussians(x,gp,ng):
  # ng is the number of gaussians to add to the baseline
  # gp is the numpy array of function parameters starting the the base line
  # x is the numpy array of data points to be computed
  # returns the numpy array of values for the x points
  sf = gp[0,0] + gp[0,1]*x + gp[0,2]*x**2
  for n in range(1,ng+1):
    h = gp[n,0]
    a = gp[n,1]
    b = gp[n,2]
    f = h*np.exp(-((x-b)/a)**2)
    sf = sf +f
  return sf

if len(sys.argv) == 1:
  print(" ")
  print("Usage: gaussmake.py inpar.dat start stop npts outpar.dat spectrum.dat")
  print(" ")
  print("Make a data set that is the sum of gaussians on a quadratic baseline")
  sys.exit("\n")
elif len(sys.argv) == 7:
  inparfile = sys.argv[1]
  start = int(float(sys.argv[2]))
  stop = int(float(sys.argv[3]))
  npts = int(float(sys.argv[4]))
  outparfile = sys.argv[5]
  outspecfile = sys.argv[6]
else:
  print(" ")
  print("Usage: gaussmake.py inpar.dat start stop npts outpar.dat spectrum.dat")
  print(" ")
  sys.exit("Make a data set that is the sum of gaussians on a quadratic baseline\n")


if (npts < 2):
  print(" ")
  print(" Ask for more than 1 point ")
  exit()

if (stop < start):
  print(" ")
  print(" Starting point must be less than stopping point ")
  exit()

 

# Open the file with input parameters
inparfp = open(inparfile, 'r')


# Read the parameters line by line into a list
inpartext = inparfp.readlines()

# Close the input parameters file
inparfp.close()

i = 0
inparlist= []

for line in inpartext:
  
  try:    
    
    entry = line.strip().split()
    inparlist.append((float(entry[0]), float(entry[1]), float(entry[2])))
    i = i + 1    

  except:      

    pass
      

# How many gaussians are to be added?

ng = i - 1

if ng < 1:
  sys.exit('The program requires parameters for the baseline and 1 or more gaussians in %s' % (inparfile,))
     
# Convert parameter list to numpy floating point arrays

inpar = np.array(inparlist, dtype=np.float32)
outpar = np.copy(inpar)

# Generate the xdata

xdata = np.linspace(start,stop,npts) 

# Calculate the values for each x

ydata = sumgaussians(xdata, inpar, ng)

ymin = np.amin(ydata)
ymax = np.amax(ydata)
xmin = np.amin(xdata)
xmax = np.amax(xdata)
ydel = ymax - ymin
xdel = xmax - xmin

# Create a plot for this sum of gaussians


thisfig = plt.figure()
thisfig.canvas.set_window_title('Gaussian')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Sum of %d Gaussians' %(ng,))
p, = plt.plot(xdata, ydata,   color='red', linestyle='None', marker='.',label='Sum')
plt.legend()
plt.minorticks_on()


# Add controls

# Make space for controls

plt.subplots_adjust(left=0.15, bottom=0.25) 

nc = int(1)


fba = plt.axes([0.35, 0.12, 0.35, 0.03])
fsa = Slider(fba, 'a', 0.0, 1., valinit=0.5)
fbb = plt.axes([0.35, 0.07, 0.35, 0.03])
fsb = Slider(fbb, 'b', 0.0, 1., valinit=0.5)
fbc = plt.axes([0.35, 0.02, 0.35, 0.03])
fsc = Slider(fbc, 'c', 0.,  1., valinit=0.5)

ngt = tuple(range(0,ng+1))
# fbn = plt.axes([0.02, 0.02, 0.04, 0.4])
#fbn = plt.axes([0.02, 0.04, 0.1, 0.15])
fbn = plt.axes([0.02, 0.04, 0.08, 0.12])
frn = RadioButtons(fbn, ngt, active=1)

fbp = plt.axes([0.15, 0.04, 0.1, 0.1])
fpp = Button(fbp, 'Reset')

fbr = plt.axes([0.8, 0.04, 0.1, 0.1])
fpr = Button(fbr, 'Reset\nAll')


def fa_update(val):
  global outpar, p, nc, xdel, ydel
  if nc == 0:
    outpar[nc,0] = (val-0.5)*4.*ydel
  else:
    outpar[nc,0] = val*2.*inpar[nc,0]
  ydata = sumgaussians(xdata, outpar, ng)
  p.set_ydata(ydata)
  plt.draw();

def fb_update(val):
  global outpar, p, nc, xdel, ydel
  if nc == 0:
    outpar[nc,1] = (val-0.5)*4.*ydel/xdel
  else:
    outpar[nc,1] = val*2.*inpar[nc,1]
  ydata = sumgaussians(xdata, outpar, ng)
  p.set_ydata(ydata)
  plt.draw();

def fc_update(val):
  global outpar, p, nc, xdel, ydel
  if nc == 0:
    outpar[nc,2] = (val-0.5)*4.*ydel/(xdel**2)
  else:
    outpar[nc,2] = val*2.*inpar[nc,2]
  ydata = sumgaussians(xdata, outpar, ng)
  p.set_ydata(ydata)
  plt.draw();

def fn_update(val):
  global nc, ng
  nc = int(val);

def fr_update(event):
  global outpar, p, nc, ng
  fsa.reset()
  fsb.reset()
  fsc.reset() 
  outpar = np.copy(inpar)
  ydata = sumgaussians(xdata, outpar, ng)
  p.set_ydata(ydata)
  plt.draw();
  
def fp_update(event):
  global outpar, p, nc, ng
  fsa.reset()
  fsb.reset()
  fsc.reset()  
  outpar[nc,:] = inpar[nc,:]
  ydata = sumgaussians(xdata, outpar, ng)
  p.set_ydata(ydata)
  plt.draw();
   

fsa.on_changed(fa_update)
fsb.on_changed(fb_update)
fsc.on_changed(fc_update)
frn.on_clicked(fn_update)
fpr.on_clicked(fr_update)
fpp.on_clicked(fp_update)


plt.show()


# Open the output spectrum file for overwriting (use 'a' for appending)

ydata = sumgaussians(xdata, outpar, ng)

outspecfp = open(outspecfile, 'w')

for i in range(npts):
  xp = xdata[i]
  yp = ydata[i]
  outline = "%f  %f\n" % (xp, yp)   
  outspecfp.write(outline)

outspecfp.close()

# Open the output parameter file for overwriting

outparfp = open(outparfile, 'w')

for i in range(ng+1):
  outline = "%f  %f %f \n" % (outpar[i,0], outpar[i,1], outpar[i,2])   
  outparfp.write(outline)

outparfp.close()



exit()
