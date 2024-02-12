#!/usr/bin/python3

import sys
from tkinter import *


lastwords='You can start this program again and I will come back.\n'

def saygoodbye():
  print('\nWell, if you are  going to act that way I am leaving.')
  print(lastwords)
  sys.exit()

def sayname():
  firstname = fnentry.get()
  print('Hello %s\n' % firstname)
  return

def retname(event):
  firstname = fnentry.get()
  print('\nHello %s\n' % firstname)
  return


   
root = Tk()
root.wm_title("Button Demonstrator")

topframe = Frame(root)
topframe.pack( side = TOP )

bottomframe = Frame(root)
bottomframe.pack( side = BOTTOM )

redbutton = Button(topframe, text="Red", fg="red")
redbutton.pack( side = LEFT)

greenbutton = Button(topframe, text="Brown", fg="brown")
greenbutton.pack( side = LEFT )

bluebutton = Button(topframe, text="Blue", fg="blue")
bluebutton.pack( side = LEFT )


fnlabel = Label(bottomframe, text="First Name: ", fg="green")
fnlabel.pack( side = LEFT )

fnentry = Entry(bottomframe)
fnentry.bind("<Return>", retname)
fnentry.pack( side = LEFT)

fnok = Button(bottomframe, text="Enter", fg="green", command=sayname)
fnok.pack( side = LEFT )

byebutton = Button(bottomframe, text="Exit", fg="magenta", command=saygoodbye )
byebutton.pack( side = RIGHT )
root.mainloop()
