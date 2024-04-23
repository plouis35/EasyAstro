#!/usr/bin/python3

########################################################################
#
# wave - This is a simple example of how to add Slider controls to a
# Python/numpy/matplotlib program.   More examples of Slider and other
# useful controls can be found at:
#
#     http://matplotlib.org/examples/widgets/
#
# Written: Michael Tague, April 2013, for Phys 650 class
#
########################################################################

import matplotlib.pyplot as plt
import numpy as np
from  matplotlib.widgets import Slider     ## <- Import the controls you want to use

f = 4   #Default Fequency HZ
d = 0   #Default Decay rate

#Create a series of time values: 0.000, 0.001, 0.002, ..., 1.000

t = np.arange(0, 1, 0.001)

#Apply our Sin*Exp function to get a series of y values

y = np.sin(2*np.pi*t*f)/np.exp(t*d)  #a series of y values

p, = plt.plot(t, y)               #p is used to refer to this plot later

#You could stop here with a "plt.show()" command and be done, but if you 
#want to add controls to make your matplotlib interactivce, proceed ...

plt.subplots_adjust(bottom=0.25)  #Touch up the bottom of the plot 25%, make some room

#The Frequency Slider
#How it works:
#  1.  Make a suitably sized axes area on the screen: 25% from left, 14% from bottom
#      with a width of 50% of window and height of 3%.
#  2.  Put a Slider control in that axes area.  Values 0 to 10, initial value of f (the default)
#  3.  Indicate that whenever the Slider changes, call the f_update function.  Note: in 
#      Python we have define the function before we can reference it.
#  4.  f_update will change the global value of "f", rerun the formula, fix the plot values
#      using p.set_y_data(y), and then redraw it on the screen.

fax = plt.axes([0.25, 0.14, 0.5, 0.03])
fs = Slider(fax, 'Freq', 0.0, 10.0, valinit=f)

def f_update(val):
    global f, p
    f = val
    y = np.sin(2*np.pi*t*f)/np.exp(t*d)
    p.set_ydata(y)
    plt.draw();

fs.on_changed(f_update)

#The Decay Slider (same as above, but for the decay, d, variable and moved down a bit)

dax = plt.axes([0.25, 0.07, 0.5, 0.03])
ds = Slider(dax, 'Decay', 0.0, 10.0, valinit=d)

def d_update(val):
    global d
    d = val
    y = np.sin(2*np.pi*t*f)/np.exp(t*d)
    p.set_ydata(y)
    plt.draw();

ds.on_changed(d_update)

#This causes the plot window to be displayed and only returns when it is closed.
#Typically this is the last line in this kind of program.

plt.show()
