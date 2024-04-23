#!/usr/bin/python3

""" Interactively plot data using matplotlib pyplot within a Tk root window
  """
# pyplot_data
# Interactively plot data using matplotlib pyplot within a Tk root window
# Copyright (c) 2015 John Kielkopf
# MIT License

# February 10, 2015
# Version 1.0

# The usual suspects

import sys     
import numpy as np

# Add mpl and tell it to use Tk

import matplotlib as mpl
#import matplotlib.pyplot as plt
mpl.use('TkAgg')

# Needed for backend operation

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler

# Bring in the Figure 

from matplotlib.figure import Figure

# Import Tk differently in Python 2 and Python 3

if sys.version_info[0] < 3:
  import tkinter as Tk
  from tkinter.filedialog import askopenfilename
else:
  import tkinter as Tk
  from tkinter.filedialog import askopenfilename


def load_file(newfile):
  
  # Take x,y coordinates from a plain text file
  # Open the file with data

  global x
  global y
  global nin
  
  try:
    infp = open(newfile, 'r')
     
  except:
    return(0)
    
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
    sys.exit('No objects found in %s\n' % (infile,))

  # Import  data into a np arrays

  x = np.array(xdata)
  y = np.array(ydata)

  return(nin)


fileflag = True

if len(sys.argv) == 1:
  fileflag = False
elif len(sys.argv) == 2:
  fileflag = True
  infile = sys.argv[1]
else:
  print(" ")
  print("Usage: pyplot_data.py [indata.dat]")
  print(" ")
  sys.exit("\nUse pyplot to display a data file\n")

if not fileflag:
  root = Tk.Tk()
  infile = askopenfilename()
  root.quit()
  root.destroy() 

npts = load_file(infile)

if npts <= 0:
  print("Could not find data in  %s \n" % (infile,))
  exit()
  

# Create the root/toplevel window with title

root = Tk.Tk()
root.wm_title("PyPlot")

# Create numpy data arrays to plot

# Use this for HD sized display
#f = Figure(figsize=(16,9), dpi=100)

# Use this for smaller sized displays
f = Figure(figsize=(7,5), dpi=200)
a = f.add_subplot(111)
p, = a.plot(x,y)
a.set_title(infile)
a.set_xlabel('X')
a.set_ylabel('Y')

# Create tk.DrawingArea with mpl figure

canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# Optionally add the toolbar (comment out to disable)

toolbar = NavigationToolbar2TkAgg( canvas, root )
toolbar.update()

# Pack the canvas

canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

# Add keypress event handler

def on_key_event(event):
  print(('You pressed %s'%event.key))
  key_press_handler(event, canvas, toolbar)

canvas.mpl_connect('key_press_event', on_key_event)

# Add Quit button

def mpl_quit():

  # Stop mainloop
  root.quit()
  
  # Prevent error running on Windows OS
  root.destroy()  
  
button = Tk.Button(master=root, text='Quit', command=mpl_quit)
button.pack(side=Tk.RIGHT)

# Add File button


def mpl_file():
  infile = askopenfilename()
  npts = load_file(infile)
  if npts > 0:
    p.set_xdata(x)
    p.set_ydata(y)
    canvas.show()
  return
  
button  = Tk.Button(master=root, text='File', command=mpl_file)
button.pack(side=Tk.LEFT)

# Run the loop

Tk.mainloop()
