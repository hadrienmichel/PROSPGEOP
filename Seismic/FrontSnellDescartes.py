'''This script solves the Snell-Descarte model for seismic reflection.
It will need in input (via GUI) a .sgt file that contains the first arrival 
for different sources and receivers. 
The script will first display the first arrival in a distance-time graph where
every source (with direction +/-) is displayed independently.
Then, the user will draw the hodochrones one after the other. When all the 
hodochrones are drawn, the script will compute and show the resulting model.
For the theory behind the model: https://www.ifsttar.fr/fileadmin/user_upload/editions/lcpc/GuideTechnique/GuideTechnique-LCPC-AGAP2.pdf
'''
from matplotlib import pyplot as plt
from matplotlib import animation
from tkinter import Tk
from tkinter.filedialog import askopenfilename as askfilename
import os
import re
import numpy as np

nbLayersDef = 2
def Snell():
    def __init__(self,nbLayers:int=nbLayersDef,V_p:np.ndarray=np.asarray([1200,2000]),
        DepthsLeft:np.ndarray=np.asarray([5]),DipAngles:np.ndarray=np.asarray([0])):
        '''MODEL is a class that will model the Snell-Descartes seismic refraction traveltimes
        for a given model described in input.

        INPUTS:
        -------
            - nbLayers (int) : number of layers in the model
            - V_p (np.ndarray) : array with the P-wave velocities for the different layers
            - DepthsLeft (np.ndarray) : array with the depth to the bottom of the layer
            - DipAngles (np.ndarray): array with the dip angles
        
        All units are un SI (meters and seconds). Angles are in radians.
        '''
        self.nbLayers = nbLayers
        self.V_p = V_p
        self.DepthsLeft = DepthsLeft
        self.DipAngles = DipAngles
    
    def Model(SourceX:float=0.0,ReceiversX:np.ndarray=np.linspace(start=0.0, stop=50.0, num=24)):
        if np.count_nonzero(self.DipAngles) > 0:
            print("Not yet implemented with dipping angles!")
            raise Exception("Not Implemented")
        else: # Horizontal layers only
            # 1) Compute the Snell critical angles:
            i_crit = np.arcsin(np.divide(self.V_p[:-2],self.V_p[1:-1]))
            # 2) Compute the travel-times from the source to the receivers
            TravelTimes = np.zeros_like(ReceiversX)
            idx = 0
            for receiver in ReceiversX:
                dist = abs(receiver-SourceX)
                for i in range(self.nbLayers):
                    Times[i] = dist/self.V_p[i]
                    j = i-1
                    while j >= 0:
                        Times[i] += 2*self.DepthsLeft[j]*np.cos(i_crit[j])/self.V_p[j]
                        j -= 1
                TravelTimes[idx] = min(Times)
                idx += 1
        return TravelTimes

    def ShowModel():


if __name__=="__main__":
    # 1) Load a file with the first arrival:
    root = Tk()
    filename = askfilename(filetypes = (("First-Arrival", "*.sgt"), ("All types", "*.*")))
    root.destroy()
    # We retreived a first-arrival file --> geometry of the sensors + first arrivals 
    head_tail = os.path.split(filename)
    path = head_tail[0]
    filename_geom = head_tail[1]
    with open(filename) as f:
        Lines = f.read().splitlines()
    MarkerNbSensors = "# shot/geophone points"
    MarkerMeasurements = "# measurements"
    for line in Lines:
        if line.endswith(MarkerNbSensors):
            nbSensors = int(line[:-len(MarkerNbSensors)])
            Sensors = np.zeros((nbSensors,2))
            idxSensor = 0
        elif line.endswith("#x\ty"):
            pass
        elif idxSensor < nbSensors:
            Sensors[idxSensor,:] = re.split(r'\t+', line)
            idxSensor += 1
        elif line.endswith(MarkerMeasurements):
            nbMeasurements = int(line[:-len(MarkerMeasurements)])
            Measurements = np.zeros((nbMeasurements,3))
            idxMeas = 0
        elif line.endswith('#s\tg\tt'):
            pass
        elif idxMeas < nbMeasurements:
            Measurements[idxMeas,:] = re.split(r'\t+', line)
            idxMeas += 1
    if np.count_nonzero(Sensors[:,1]) > 0:
        print("This dataset cannot be interpreted with the Snell refraction model!")
        raise Exception("Dtataset has topography!")

    
