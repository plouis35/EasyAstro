#!/usr/bin/python3

import sys
from tkinter import *

from math import *

def evaluate(event):
  res.configure(text = "Value: " + str(eval(entry.get())))

root = Tk()
root.wm_title("Calculator")

topframe = Frame(root)
topframe.pack( side = TOP )

Label(topframe, text="Enter a math expression", height=5).pack( side = TOP )
entry = Entry(topframe, width=100)
entry.bind("<Return>", evaluate)
entry.pack()
res = Label(topframe, height=5)
res.pack( side = BOTTOM )

root.mainloop()
