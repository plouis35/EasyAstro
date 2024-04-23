#!/usr/bin/python3

# Calculate the current Moon

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
  print("Usage: moon.py [jd] ")
  print(" ")
  sys.exit("Calculate the Moon at this moment or optionally at jd\n")


jdstart = round(jdin) - 15. + 0.5
moondates = np.arange(jdstart, jdstart + 29, 1)


# Calculate Moon positions

moonnow = pyasl.moonpos(jdin)
phasenow = pyasl.moonphase(jdin)
moonresults = pyasl.moonpos(moondates)
phaseresults = pyasl.moonphase(moondates)

print(" ")
print("%15s  %8s  %8s  %11s  %8s  %8s %8s" % \
  ("JD", "RA", "DEC", "DIST", "GEOLON", "GEOLAT", "PHASE"))
print("%15s  %8s  %8s  %11s  %8s  %8s  %8s" % \
  ("[d]", "[deg]", "[deg]", "[km]", "[deg]", "[deg]", "   "))
print("%15.4f  %8.4f  %8.4f  %11.4f  %8.4f  %8.4f  %6.2f" % \
  (jdin, moonnow[0], moonnow[1], moonnow[2], moonnow[3], moonnow[4], phasenow))


for i in range(moondates.size):
  print("%15.4f  %8.4f  %8.4f  %11.4f  %8.4f  %8.4f  %6.2f" % \
    (moondates[i], moonresults[0][i], moonresults[1][i], moonresults[2][i], moonresults[3][i], moonresults[4][i], phaseresults[i]))

print(" ")    
exit()    
