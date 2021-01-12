from obspy import read
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np

st = read("testFile.sg2", 'SEG2')
print(st)
# Set the positions for the geophones and source
nbGeophones = len(st)
geophoneSpacing = 2.5
receiversX = np.arange(0,nbGeophones*geophoneSpacing,geophoneSpacing).T
receivers = np.zeros((len(st),2))
receivers[:,0] = receiversX
source = [nbGeophones-1*geophoneSpacing, 0] # source in exemple file is last geophone
for i in range(len(st)):
    st[i].stats.position = receivers[i,:]
    st[i].stats.source = source
    st[i].stats.distance = np.linalg.norm(st[i].stats.position-st[i].stats.source)
# Computing the xAxes values
beginTime = float(st[0].stats.seg2["DELAY"])
deltaT = float(st[0].stats.seg2["SAMPLE_INTERVAL"])
nbPoints = st[0].stats.npts
time = np.arange(beginTime, beginTime+nbPoints*deltaT, deltaT)
# Picking the traces:
Picks = [None]*len(st)
# Create the interactive Figure:
plt.close('all')
figureMain = plt.figure()
figureMain.suptitle('Seismic picker (quit figure toi end/save)')
axMain = plt.subplot2grid((2,3), (0,0), rowspan=2, colspan=2, fig=figureMain)
axZoom = plt.subplot2grid((2,3), (0,2), fig=figureMain)
# Parameters for interactivity:
MousePosition = 0
currSelect = 0
changedSelect = True # To force plot at first
First = True
# Functions for reactions to keyboard/mouse events:
def changeMouse(event):
    if event.inaxes is not None:
        global MousePosition
        MousePosition = event.xdata
    return 0

def on_key(event):
    global changedSelect, currSelect
    if event.key == "up": # Change i += 1
        currSelect += 1
        if currSelect >= len(st):
            currSelect = 0
        changedSelect = True
    elif event.key == "down": # Change i -= 1
        currSelect -= 1
        if currSelect < 0:
            currSelect = len(st)-1
        changedSelect = True    
    return 0

def on_press(event):
    global Picks, changedSelect
    if event.button == 1: # Left-click only
        Picks[currSelect] = MousePosition
        changedSelect = True
    return 0

def AnimationZoom(i):
    global changedSelect, First
    # Change plot to go at the correct position:
    axZoom.clear()
    axZoom.plot(time,st[currSelect].data,color='k')
    axZoom.autoscale(axis='y')
    z = axZoom.get_ylim()
    axZoom.plot([MousePosition, MousePosition],z,color='r')
    axZoom.set_xlim(left=MousePosition-150*deltaT,right=MousePosition+150*deltaT)
    axZoom.set_frame_on(False)
    axZoom.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        left=False,
        right=False,
        labelleft=False,
        labelbottom=False) # labels along the bottom edge are off
    if changedSelect:
        # Change red graph + pick
        if not(First):
            limitsY = axMain.get_ylim()
            limitsX = axMain.get_xlim()
        axMain.clear()
        i = 0
        for tr in st:
            data = tr.data 
            data = data/(max(data)-min(data))+i
            if i == currSelect:
                axMain.plot(time,data,color='r')
            else:
                axMain.plot(time,data,color='k')
            if Picks[i] is not None:
                axMain.plot([Picks[i], Picks[i]], [i-0.5, i+0.5],color='g')
            i += 1
        if not(First):
            axMain.set_xlim(left=limitsX[0],right=limitsX[1])
            axMain.set_ylim(bottom=limitsY[0],top=limitsY[1])
        First=False
        changedSelect = False
    return 0

plt.connect('motion_notify_event', changeMouse)
plt.connect('key_press_event', on_key)
plt.connect('button_press_event',on_press)
ani = animation.FuncAnimation(figureMain,AnimationZoom,interval=1)

plt.show()

Picks = np.asarray(Picks)
# Saving the picks in a sgt file (for interpretation in PyGimli)
mask = np.not_equal(Picks, None)
receivers = receivers[mask,:]
Picks = Picks[mask]
f = open("DATA.sgt",'w')    # Create a new file called DATA.sgt
nbSensors = receivers.shape[0] # We are only taking into account points that could be picked
sourceOutside = False
if not(any(np.equal(receivers,source).all(1))):# Source position not in receiver array
    sourceOutside = True
    nbSensors += 1
else:
    s = int(np.where(np.all(receivers,source,axis=1))) + 1 #id of source/receiver
f.write('%d # shot/geophone points\n' % nbSensors)
f.write('#x\ty\n')
for i in range(nbSensors):
    if sourceOutside and i==0:
        f.write('%.2f\t%.2f\n' % (source[0], source[1]))
    elif sourceOutside:
        f.write('%.2f\t%.2f\n' % (receivers[i-1,0], receivers[i-1,1]))
    else:
        f.write('%.2f\t%.2f\n' % (receivers[i,0], receivers[i,1]))
nbMeas = len(Picks)
f.write('%d # measurements\n' % nbMeas)
f.write('#s\tg\tt\n')
for i in range(nbMeas):
    if sourceOutside:
        f.write('%d\t%d\t%f\n' % (1, i+2, Picks[i]))
    else:
        f.write('%d\t%d\t%f\n' % (s, i+1, Picks[i]))
f.close()