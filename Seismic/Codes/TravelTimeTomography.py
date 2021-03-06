'''
TRAVEL TIME TOMOGRAPHY: this script will load a '*.sgt' file with first arrival
and generate an inversion for the travel time tomography. 

Follow instructions as they appear on the screen and change parameters in the 
PARAMETERS cetion of the code.
'''
# Import of usefull libraries:
import numpy as np
from matplotlib import pyplot as plt
# Import of PyGimli
import pygimli as pg
from pygimli import meshtools as mt
from pygimli.physics import TravelTimeManager as TTMgr
# Import of TKinker
from tkinter import Tk
from tkinter.filedialog import askopenfilename as askfilename


if __name__ == '__main__':
    root = Tk()
    filename = askfilename(filetypes = (("First-Arrival", "*.sgt"), ("All types", "*.*")))
    root.destroy()
    # Parameters:
    lambdaParam = 10 # Smoothing the model
    depthMax = 50 # Forcing a given depth to the model
    maxCellSize = 2.5 # Forcing a given size for the mesh cells
    zWeightParam = 0.1 # Forcing Horizontal features in the model (smaller than 1) or vertical (larger than 1)
    # Inversion:
    dataTT = pg.DataContainer(filename, 's g t')
    print(dataTT)
    mgr = TTMgr(data=dataTT)
    meshTT = mgr.createMesh(data=dataTT, paraMaxCellSize=maxCellSize, paraDepth=depthMax)
    mgr.invert(data=dataTT, mesh= meshTT, zWeight=zWeightParam, lam=lambdaParam, verbose=True)
    ax,cbar = mgr.showResult(logScale=True)
    mgr.drawRayPaths(ax=ax, color='w', lw=0.3, alpha=0.5)
    plt.show()
    mgr.showCoverage()
    plt.show()