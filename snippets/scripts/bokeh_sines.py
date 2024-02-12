#!/usr/bin/python3

from bokeh.plotting import figure, output_file, show
import math as m

# Create a plot of 1000 points

npoints = 1000

# Create two empty lists to hold x and y values

x = []
y = []

# Define some variables that will determine what you want to plot

f1 = 100.
f2 = 80.
a1 = 5.
a2 = 5.

# Iterate through the points assigning x and y at each one

for i in range(npoints):

  t = float(i)/10000.
  arg1 = 2.*m.pi*f1*t
  arg2 = 2.*m.pi*f2*t
  amplitude = a1*m.sin(arg1) + a2* m.sin(arg2)
  x.append(t)
  y.append(amplitude)
  
# Inform bokeh with the name of the output html file  

output_file("sines.html")

# Create the figure and plot the data

p = figure()
p.line(x, y, line_width=2)

# Show it and also write the file

show(p)

exit()


