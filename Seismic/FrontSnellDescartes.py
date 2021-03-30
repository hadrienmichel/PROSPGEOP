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
import pygimli as pg
from pygimli.frameworks import BlockModelling, MethodManager1d

def getH(H0:float=0.0, DipUp:float=0.0, DipDown:float=0.0, x:float=0.0):
    y0 = x*np.tan(DipUp)
    y1 = H0 + x*np.tan(DipDown)
    H = y1-y0
    return H

nbLayersDef = 2
class Snell():
    def __init__(self,nbLayers:int=nbLayersDef,V_p:np.ndarray=np.asarray([1200,2000]),
        ThickLeft:np.ndarray=np.asarray([5]),DipAngles:np.ndarray=np.asarray([0])):
        '''SNELL is a class that will model the Snell-Descartes seismic refraction traveltimes
        for a given model described in input.

        INPUTS:
        -------
            - nbLayers (int) : number of layers in the model
            - V_p (np.ndarray) : array with the P-wave velocities for the different layers
            - ThickLeft (np.ndarray) : array with the thicknesses of the layer
            - DipAngles (np.ndarray): array with the dip angles
        
        All units are un SI (meters and seconds). Angles are in radians.
        '''
        self.nbLayers = nbLayers
        self.V_p = V_p
        self.ThickLeft = ThickLeft
        self.DipAngles = DipAngles
    
    def Model(self,SourceX:float=0.0,ReceiversX:np.ndarray=np.linspace(start=0.0, stop=100.0, num=101)) -> np.ndarray:
        '''MODEL is a method that computes the forward model for the given SNELL class.

        INPUTS:
        -------
            - SourceX (float) : position of the source along X axis in m (default = 0.0)
            - RevceiversX (np.ndarray) : postions of the receivers along X axis in m
                                        (default = np.linspace(0.0,100.0,num=100))

        OUTPUT:
        -------
            - TravelTimes (np.ndarray) : travel times from sources to receivers in seconds

        '''
        # if np.count_nonzero(self.DipAngles) > 0:
        i_crit = np.arcsin(np.divide(self.V_p[:-1],self.V_p[1:]))
        TravelTimes = np.zeros_like(ReceiversX)
        idx = 0
        for receiver in ReceiversX:
            # dist = abs(receiver-SourceX)
            xL = min(SourceX,receiver)
            xR = max(SourceX,receiver)
            Times = np.zeros((self.nbLayers,))
            for i in range(self.nbLayers):
                dist = abs(receiver-SourceX)
                j = 0
                DipDown = 0
                while j < i:
                    DipUp = DipDown
                    DipDown = self.DipAngles[j]
                    zL = getH(self.ThickLeft[j], DipUp, DipDown, xL)*np.cos(self.DipAngles[j])
                    zR = getH(self.ThickLeft[j], DipUp, DipDown, xR)*np.cos(self.DipAngles[j])
                    seg1 = zL/np.cos(i_crit[j])
                    seg2 = zR/np.cos(i_crit[j])
                    xL += np.sin(i_crit[j]-self.DipAngles[j])*seg1
                    xR -= np.sin(i_crit[j]-self.DipAngles[j])*seg2
                    Times[i] += (seg1+seg2)/self.V_p[j]
                    dist = np.cos(DipDown-DipUp)*dist - np.tan(i_crit[j])*(zL+zR)
                    j += 1
                if dist >= 0:
                    Times[i] += dist/self.V_p[j]
                else:
                    Times[i] = 1e20 # Absurdly high value because spacing too low to reach such deep layer.
            TravelTimes[idx] = min(Times)
            idx += 1
        return TravelTimes

    def ShowModel(self,SourceX:float=0.0,ReceiversX:np.ndarray=np.linspace(start=0.0, stop=100.0, num=101)):
        SourceX = np.asarray(SourceX)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        minX = min(SourceX.min(),ReceiversX.min())
        maxX = max(SourceX.min(),ReceiversX.max())
        meanX = (minX+maxX) / 2
        ax.plot([minX, maxX], [0, 0], 'k') # Draw the soil limit
        i = 0
        while i < self.nbLayers-1:
            minY = self.ThickLeft[:i+1].sum()
            maxY = self.ThickLeft[:i+1].sum() + np.tan(self.DipAngles[i])*(maxX-minX)
            ax.plot([minX, maxX], [minY, maxY],'k')
            ax.text(meanX, ((minY+maxY)/2*0.7), '$V_p$ = {} m/s'.format(self.V_p[i]))
            i += 1
        ax.text(meanX, max(minY,maxY)*1.1, '$V_p$ = {} m/s'.format(self.V_p[i]))
        ax.plot(ReceiversX, np.zeros_like(ReceiversX), 'kv', label='Receivers')
        ax.plot(SourceX, np.zeros_like(SourceX), 'kD',label='Source')
        ax.set_ylim([-5, max(minY,maxY)*1.5])
        ax.invert_yaxis()
        ax.set_xlabel('Distance [m]')
        ax.set_ylabel('Depth [m]')
        ax.set_title('Model display')
        ax.grid()
        fig.show()
    
    def Simulate(self, Sensors:np.ndarray, Measurements:np.ndarray, Graphs:bool=False) -> np.ndarray:
        '''SIMULATE is a method that simulates the measuremensts as performed on a field. 

        INPUTS:
        -------
            - Sensors (np.ndarray) : array containing the sensors positions
            - Measurements (np.ndarray) : array containing the configuration and measures in the form "S R T".

        OUTPUT:
        -------
            - Traveltimes (np.ndarray) : array containing the traveltimes for the configurations in Measurements
        '''
        TravelTimes = np.zeros_like(Measurements[:,-1])
        Sources = np.unique(Measurements[:,0].astype(int))
        for s in Sources:
            idx = np.where(Measurements[:,0].astype(int)==s)
            Receivers = Measurements[idx,1].astype(int)
            sX = Sensors[s-1,0].flatten()
            rX = Sensors[Receivers-1,0].flatten()
            t = self.Model(SourceX=sX, ReceiversX=rX)
            TravelTimes[idx] = t
        if Graphs:
            self.ShowModel(Sensors[Sources-1,0],Sensors[:,0])          
        return TravelTimes

class SnellFOP(pg.Modelling):
    def __init__(self, sensorsX, MeasurementsArray, nlay=2, verbose=False):
        super().__init__()
        self.x = sensorsX
        self.array = MeasurementsArray
        
    
    def response(self, model):
        nbLayers = model[0]
        V_p = model[1]
        ThickLeft = model[3]
        DipLeft = model[4]
        Sensors = self.x[0]
        Measurements = self.x[1]
        return Snell(nbLayers,V_p,ThickLeft,DipLeft).Simulate(Sensors,Measurements)
    
    def createStartModel(self, dataVals):
        return pg.Vector([[2],[1600, 2600],[5],[0.0]])

if __name__=="__main__":
    # 0) Initialization:
    Graphs = True # Show graphs (True) or not (False)
    Automated = True # Automatic hodochrones fitting (True) or manual fitting (False)
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
        print("Use PyGIMLI for the inversion of the traveltime tomography...")
        raise Exception("Dataset has topography!")
    # File has been read!
    print("First arrival times read succesfully!")
    # Get the number of sources in the system:
    Sources = Sensors[np.unique(Measurements[:,0].astype(int))-1,0]
    Receivers = Sensors[np.unique(Measurements[:,1].astype(int))-1,0]
    print("Dataset has {} sources and {} receivers.".format(len(Sources),len(Receivers)))
    if Graphs:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        minX = min(Sources.min(),Receivers.min())
        maxX = max(Sources.max(),Receivers.max())
        meanX = (minX+maxX) / 2
        ax.plot([minX, maxX], [0, 0], 'k') # Draw the soil limit
        ax.plot(Receivers, np.zeros_like(Receivers), 'kv', label='Receivers')
        ax.plot(Sources, np.zeros_like(Sources), 'kD',label='Source')
        ax.set_ylim([-5, 5])
        ax.invert_yaxis()
        ax.set_xlabel('Distance [m]')
        ax.set_ylabel('Depth [m]')
        ax.set_title('Acquisition setup')
        ax.grid()
        ax.legend(loc='upper center',
            ncol=2, fancybox=True, shadow=True)
        fig.show()
    if Automated:
        pass # Inversion of the data to fit the Snell-Descarte model
    else:
        pass # Manual picking of the graphs

    ModelTest = Snell(nbLayers=3,V_p=np.asarray([1600,2200,2800]),ThickLeft=np.asarray([5, 10]),DipAngles=np.asarray([0,0]))
    TravelTimes = ModelTest.Simulate(Sensors,Measurements,Graphs=True)
    HodoFlatUp = ModelTest.Model()
    HodoFlatCenter = ModelTest.Model(SourceX=50.0)
    HodoFlatDown = ModelTest.Model(SourceX=100.0)
    ModelTest = Snell(nbLayers=3,V_p=np.asarray([1600,2200,2800]),ThickLeft=np.asarray([5, 10]),DipAngles=np.asarray([-0.02,0.01]))
    HodoDipUp = ModelTest.Model()
    HodoDipCenter = ModelTest.Model(SourceX=50.0)
    HodoDipDown = ModelTest.Model(SourceX=100.0)
    plt.figure()
    plt.plot(np.linspace(start=0.0, stop=100.0, num=101),HodoFlatUp,'c',label='Flat (Upward)')
    plt.plot(np.linspace(start=0.0, stop=100.0, num=101),HodoFlatCenter,'c--',label='Flat (Center)')
    plt.plot(np.linspace(start=0.0, stop=100.0, num=101),HodoFlatDown,'c',label='Flat (Downward)')
    plt.plot(np.linspace(start=0.0, stop=100.0, num=101),HodoDipUp,'y',label='Dipping (Upward)')
    plt.plot(np.linspace(start=0.0, stop=100.0, num=101),HodoDipCenter,'y--',label='Dipping (Center)')
    plt.plot(np.linspace(start=0.0, stop=100.0, num=101),HodoDipDown,'y',label='Dipping (Downward)')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
    plt.xlabel('Distance [m]')
    plt.ylabel('Time [sec]')
    plt.grid()
    plt.show()
    ModelTest.ShowModel()
    plt.show()

    test = SnellFOP([Sensors, Measurements])
    print(test.createStartModel(Measurements[:,-1]))
    print(test.response(test.createStartModel(Measurements[:,-1])))