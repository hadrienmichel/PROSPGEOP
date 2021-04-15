import obspy
from tkinter import Tk
from tkinter.filedialog import askopenfilename as askfilename
import os

root = Tk()
filename = askfilename(filetypes = (("SEG-Y", "*.sgy"), ("All types", "*.*")))
root.destroy()

data = obspy.read(filename, format='SEG2')

print(data.__str__(extended=True))

data.plot(color='gray',automerge=False)

pass