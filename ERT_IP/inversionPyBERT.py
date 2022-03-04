import pybert as pb

# Read the datafile
tdip=pb.TDIPdata(filename='./data/B52_DDN6.ohm', verbose=True)
data = tdip.data # Extract the data container
mgr = pb.ERTManager(data = tdip.data) # Build a pyBERT manager

# Show the data
tdip.showRhoa()

# Build an inversion mesh
## Parameters list:
##      - paraDepth [m]: depth of the model
##      - quality [/]: quality of the mesh (higher is better)
##      - paraMaxCellSize [m²]: maximum size of a cell in the mesh
##      - paraDX [/]: discretization close to the electrodes
mesh = mgr.createMesh(data, paraDepth = 15, quality = 33.6,
                      paraMaxCellSize = 2, paraDX = 0.6)

# Inversion for resistivity:
## Parameters list:
##      - mesh: mesh build using createMesh (see above)
##      - lam: lambda factor, to optimize for the dataset
##      - robustData: use robust norm on the data?
##      - verbose: display informations on the inversion?
tdip.invertRhoa(mesh=mesh,lam = 10, robustData= False,
                verbose = True)

# Display the results:
tdip.showResistivity(cMap='jet')

# Invert chargeability:
## Parameters list:
##      - lam: lambda factor, to optimize for the dataset
##      - ma: chargeabilty data (mrad)
tdip.invertMa(lam = 10, ma = tdip.data('ip')*0.001)

# Display the results:
tdip.showChargeability(cMap='jet')