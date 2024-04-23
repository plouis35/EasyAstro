#!/usr/bin/python3

# Phidgets IR temperature sensor example program
# Driven by IR sensor change
# Added utc logging 

import sys
import time
from time import gmtime, strftime  # for utc
from time import sleep       # for delays 
from Phidget22.Devices.TemperatureSensor import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *
import tkinter as tk
from tkinter import ttk


#
# Initial parameters
#

global site_longitude
global diagnostics
global time_utc
global temperature_celsius
global polling_flag

diagnostics = False

polling_flag = True


# Greenwich prime meridian
#site_longitude = 0.0

# Moore Observatory near Crestwood, Kentucky USA
site_longitude = 85.5288888888 

# Mt. Kent Observatory  near Toowoomba, Queensland Australia
# site_longitude = -151.855528 

#
# End of initial parameters
#

#
# Time utilities
#

# Coordinated Universal Time

def utcnow():
  t = gmtime()
  year = t.tm_year
  month = t.tm_mon
  day = t.tm_mday
  hour = t.tm_hour
  minute = t.tm_min
  second = t.tm_sec
  yearday = t.tm_yday
  utc = second/3600. + minute/60. + hour
  return(utc)

# Julian day
# Code from aa.usno.navy.mil/faq/docs/JD_Formula.php
# Valid for CE March 1901 through 2099

def jd(year, month, day, utc):
  k = int(year)
  m = int(month)
  i = int(day)
  j1 = float(367*k)
  j2 = -1.*float( int( ( 7*(k + int((m+9)/12) ) )/4 ) )
  j3 = float(int(275*m/9))
  j4 = 1721013.5 + (utc/24.)
  julian = j1 + j2 + j3 +j4
  return(julian)
     

# Map a time in hours to the range 0 to 24     
     
def map24(hour):

  if hour < 0.0:
    n = int(hour/24.0) - 1
    h24 = hour - n*24.0
    return(h24)
  elif hour > 24.0:
    n = (int) (hour / 24.0) 
    h24 = hour - n*24.0
    return(h24)
  else:
    return(hour)  

  
# Fractional part

def frac(x):

  x = x - int(x)
  if x < 0:
    x = x + 1.0  
  return (x)


# Julian day now
# Use system time and compute the Julian day at this moment
# Code from aa.usno.navy.mil/faq/docs/JD_Formula.php
# Valid for CE March 1901 through 2099

def jdnow():
  t = gmtime()
  year = t.tm_year
  month = t.tm_mon
  day = t.tm_mday
  hour = t.tm_hour
  minute = t.tm_min
  second = t.tm_sec
  yearday = t.tm_yday
  utc = second/3600. + minute/60. + hour
  k = int(year)
  m = int(month)
  i = int(day)
  j1 = float(367*k)
  j2 = -1.*float( int( ( 7*(k + int((m+9)/12) ) )/4 ) )
  j3 = float(i + int(275*m/9))
  j4 = 1721013.5 + (utc/24.)
  julian = j1 + j2 + j3 +j4
  return(julian)

# Julian day today
# Use system time and compute the Julian day number for today at 0h UTC
# Code from aa.usno.navy.mil/faq/docs/JD_Formula.php
# Valid for CE March 1901 through 2099

def jdtoday():
  t = gmtime()
  year = t.tm_year
  month = t.tm_mon
  day = t.tm_mday
  utc = 0.
  k = int(year)
  m = int(month)
  i = int(day)
  j1 = float(367*k)
  j2 = -1.*float( int( ( 7*(k + int((m+9)/12) ) )/4 ) )
  j3 = float(i + int(275*m/9))
  j4 = 1721013.5 + (utc/24.)
  julian = j1 + j2 + j3 +j4
  return(julian)


# Local sidereal time

def lstnow():
  jd = jdtoday()
  ut = utcnow()
  tu = (jd - 2451545.0)/36525.0  
  a0 = 24110.54841 / 3600.
  a1 = 8640184.812866 / 3600.0
  a2 = 0.093104 / 3600.0
  a3 = -6.2e-6 / 3600.0
  t = a0 + a1*tu + a2*tu*tu + a3*tu*tu*tu   
  t0 = map24(t)  
  gst = map24(t0 + ut * 1.002737909)
  lst = (gst - site_longitude / 15.0)
  lst = map24(lst)
  return(lst)

#
# End of time utilities
#

#
# Tkinter setup
#



# Define the button press actions

def start_irsensor():
  global temperature_celsius
  global time_utc
  global polling_flag
  polling_flag = True
  tk_temperature_celsius.set(format(temperature_celsius, '3.2f'))
  tk_time_utc.set(format(time_utc, '3.7f'))
  return()

def stop_irsensor():
  global temperature_celsius
  global time_utc
  global polling_flag
  polling_flag = False
  tk_temperature_celsius.set(format(temperature_celsius, '3.2f'))
  tk_time_utc.set(format(time_utc, '3.7f'))
  return()

def exit_irsensor():
  try:
    ch.close()
  except PhidgetException as e:
    print(("Phidget Exception %i: %s" % (e.code, e.details)))
    if diagnostics:
      print("Press Enter to Exit...\n")
      readin = sys.stdin.read(1)
    exit(1) 

  print("Closed TemperatureSensor device")
  exit(0)
  return()
     


# Create the root window

root = tk.Tk()
root.title("IR Temperature Sensor")

# Add a frame to the window

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

# Create Tk strings for displayed information

tk_temperature_celsius = tk.StringVar()
tk_time_utc = tk.StringVar()
tk_temperature_celsius.set('100.')
tk_time_utc.set('0.')

#Add widgets to the grid within the frame

ttk.Label(mainframe, text="IR Sensor").grid(column=2, row=1, sticky=tk.W)
ttk.Label(mainframe, text="Time").grid(column=1, row=2, sticky=tk.W)
ttk.Label(mainframe, textvariable=tk_time_utc).grid(column=2, row=2, sticky=(tk.W, tk.E))
ttk.Label(mainframe, text="hours (UTC)").grid(column=3, row=2, sticky=tk.W)

ttk.Label(mainframe, text="Temperature").grid(column=1, row=3, sticky=tk.W)
ttk.Label(mainframe, textvariable=tk_temperature_celsius).grid(column=2, row=3, sticky=(tk.W, tk.E))
ttk.Label(mainframe, text="Celsius").grid(column=3, row=3, sticky=tk.E)

ttk.Button(mainframe, text="Start", command=start_irsensor).grid(column=2, row=4, sticky=tk.W)
ttk.Button(mainframe, text="Stop", command=stop_irsensor).grid(column=2, row=5, sticky=tk.W)
ttk.Button(mainframe, text="Exit", command=exit_irsensor).grid(column=2, row=6, sticky=tk.W)


# Pad the widgets for appearance

for child in mainframe.winfo_children(): 
  child.grid_configure(padx=5, pady=5)


#
# Sensor functions
#

def TemperatureSensorAttached(self):
  try:
    attached = self
    if diagnostics:
      print("\nAttach Event Detected (Information Below)")
      print("===========================================")
      print(("Library Version: %s" % attached.getLibraryVersion()))
      print(("Serial Number: %d" % attached.getDeviceSerialNumber()))
      print(("Channel: %d" % attached.getChannel()))
      print(("Channel Class: %s" % attached.getChannelClass()))
      print(("Channel Name: %s" % attached.getChannelName()))
      print(("Device ID: %d" % attached.getDeviceID()))
      print(("Device Version: %d" % attached.getDeviceVersion()))
      print(("Device Name: %s" % attached.getDeviceName()))
      print(("Device Class: %d" % attached.getDeviceClass()))
      print("\n")

  except PhidgetException as e:
    print(("Phidget Exception %i: %s" % (e.code, e.details)))    
    if diagnostics:
      print("Press Enter to Exit...\n")
      readin = sys.stdin.read(1)    
    exit(1)   
  
def TemperatureSensorDetached(self):
  detached = self
  try:
    tport = detached.getHubPort()
    tchannel = detached.getChannel()
    if diagnostics:
      print(("\nDetach event on Port %d Channel %d" % (tport, tchannel)))
  except PhidgetException as e:
    print(("Phidget Exception %i: %s" % (e.code, e.details)))
    if diagnostics:
      print("Press Enter to Exit...\n")
      readin = sys.stdin.read(1)
    exit(1)   

def ErrorEvent(self, eCode, description):
  print(("Error %i : %s" % (eCode, description)))

def TemperatureChangeHandler(self, temperature):
  global temperature_celsius
  global time_utc
  global polling_flag
  temperature_celsius = temperature
  time_utc = utcnow()
  if polling_flag:
    tk_temperature_celsius.set(format(temperature_celsius, '3.2f'))
    tk_time_utc.set(format(time_utc, '3.7f'))

      

#
# End of sensor function definitions
#  


# Open a connection to the sensor and assign a channel

try:
  ch = TemperatureSensor()
except RuntimeError as e:
  print(("Runtime Exception %s" % e.details))
  print("Press Enter to Exit...\n")
  readin = sys.stdin.read(1)
  exit(1)

# Establish event handlers

try:
  ch.setOnAttachHandler(TemperatureSensorAttached)
  ch.setOnDetachHandler(TemperatureSensorDetached)
  ch.setOnErrorHandler(ErrorEvent)

  ch.setOnTemperatureChangeHandler(TemperatureChangeHandler)

  # Specify the serial number of the device to attach to.
  # For VINT devices, this is the hub serial number.
  #
  # The default is any device.
  #
  # ch.setDeviceSerialNumber(<YOUR DEVICE SERIAL NUMBER>) 

  # Specify the port the VINT device must be plugged into.
  #
  # The default is any port.
  #
  # ch.setHubPort(0)

  # Specify which channel to attach to.  
  # The channel of the device must be the same class as the channel that is being opened.
  #
  # The default is any channel.
  #
  # ch.setChannel(0)

  # Specify a networked Phidget connected to a Phidget22 network server.
  # Enable  server discovery. Set remote to 1 to only match a network Phidget.
  #
  # Net.enableServerDiscovery(PhidgetServerType.PHIDGETSERVER_DEVICEREMOTE);
  # ch.setIsRemote(1)

  if diagnostics:
    print("Waiting for the Phidget TemperatureSensor Object to be attached...")
  ch.openWaitForAttachment(5000)
except PhidgetException as e:
  print(("Phidget Exception %i: %s" % (e.code, e.details)))
  if diagnostics:
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
  exit(1)



#
# Polling loop within GUI
#

if diagnostics:
  print("Gathering data ...")

# Temperature change handler will provide new data

# Tk standard is to use this blocking method 
root.mainloop()

exit()
           
