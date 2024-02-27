import numpy as np
import pygimli as pg
from pygimli.meshtools import   createGrid
import matplotlib.pyplot as plt

from pygimli.physics.gravimetry import  solveGravimetry
# Measurements points
x = np.arange(-20, 20.1, .5)
pnts = np.array([x, np.zeros(len(x))]).T

# Meshing
x2 = np.arange(-20, 20.1, 1)
y2 = np.arange(0, -10.1, -2)
Grid = createGrid(x2,y2,marker=1)

# delta rho distribution
dRhoRec = pg.solver.parseMapToCellArray([[1, 0.0]], Grid)
dRhoRec[60]=100
dRhoRec[61]=100
gc_rec = -solveGravimetry(Grid, dRhoRec, pnts)

###############################################################################
# Finishing the plots
#fig = plt.figure()
ax1 = pg.plt.subplot(2, 1, 1)
ax1.plot(x, gc_rec, label='Grid')
ax2 = pg.plt.subplot(2, 1, 2)
ax2.plot(x, x*0,  'bv')
pg.show(Grid, dRhoRec, ax=ax2)
pg.wait()

ax1.set_ylabel(r'$\frac{\partial u}{\partial z}$ [mGal]')
ax1.set_xlabel('$x$-coordinate [m]')
ax1.grid()
ax1.legend()

ax2.set_aspect(1)
ax2.set_xlabel('$x$-coordinate [m]')
ax2.set_ylabel('$z$-coordinate [m]')
ax2.set_ylim((-10, 0))
ax2.set_xlim((-20, 20))
plt.tight_layout()

