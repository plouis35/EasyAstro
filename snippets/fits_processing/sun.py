#!/usr/bin/python3

# Calculate the current Sun

import sys
import numpy as np
from PyAstronomy import pyasl
from time import gmtime, strftime  # for utc    

# Coordinated universal time

def utcnow():
  t = gmtime()
  year = t.tm_year
  month = t.tm_mon
  day = t.tm_mday
  hour = t.tm_hour
  minute = t.tm_min
  second = t.tm_sec
  yearday = t.tm_yday
  ut = second/3600. + minute/60. + hour
  return(ut)
  

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


if len(sys.argv) == 2:
  jdin = float(sys.argv[1])
elif len(sys.argv) == 1:
  jdin = jdnow()
else:
  print(" ")
  print("Usage: sun.py [jd] ")
  print(" ")
  sys.exit("Calculate the sun at this moment or optionally at jd\n")


jdstart = round(jdin) - 15. + 0.5
jdend = jdstart + 30.
jdsteps = 30

# Calculate sun positions

sunnow = pyasl.sunpos(jdin, full_output=False)

sunresults = pyasl.sunpos(jdstart, jdend, jdsteps, full_output=False)

print(" ")
print("%15s  %8s  %8s" % \
  ("JD", "RA", "DEC"))
print("%15s  %8s  %8s"  % \
  ("[d]", "[deg]", "[deg]"))
print("%15.4f  %8.4f  %8.4f"   % \
  (jdin, sunnow[1], sunnow[2]))
for i in range(len(sunresults[0])):
  print("%15.4f  %8.4f  %8.4f"  % \
    (sunresults[0][i], sunresults[1][i], sunresults[2][i]))

print(" ")    
exit()    
