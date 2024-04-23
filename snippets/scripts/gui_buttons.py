#!/usr/bin/python3

import sys
from tkinter import *


lastwords='You can start this program again and I will come back.'

def saygoodbye():
   print('Well, if you are  going to act that way I am leaving.')
   print(lastwords)
   sys.exit()


root = Tk()
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

blackbutton = Button(bottomframe, text="Black", fg="black")
blackbutton.pack( side = LEFT)

byebutton = Button(bottomframe, text="Exit", fg="magenta", command=saygoodbye )
byebutton.pack( side = RIGHT)
root.mainloop()
