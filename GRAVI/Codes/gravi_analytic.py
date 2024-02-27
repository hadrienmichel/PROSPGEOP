import numpy as np
import pygimli as pg
from pygimli.meshtools import createCircle, createWorld, createMesh, createRectangle , createGrid
import matplotlib.pyplot as plt

from pygimli.physics.gravimetry import gradUCylinderHoriz, solveGravimetry

radius = 4.  # [m]
depth = 5.  # [m]
pos = [0., -depth]
dRho = 100

x = np.arange(-20, 20.1, 5
              )
pnts = np.array([x, np.zeros(len(x))]).T

###############################################################################
# Analytical solution first
gz_a = gradUCylinderHoriz(pnts, radius, dRho, pos)[:, 1]

###############################################################################
# Integration for a 2D polygon after :cite:`WonBev1987`
circ = createCircle([0, -depth], radius=radius, marker=2, area=0.1,
                	nSegments=16)
gz_p = solveGravimetry(circ, dRho, pnts, complete=False)

###############################################################################
# Integration for complete 2D mesh after :cite:`WonBev1987`
world = createWorld(start=[-20, 0], end=[20, -20], marker=1)
mesh = createMesh([world, circ])
dRhoC = pg.solver.parseMapToCellArray([[1, 0.0], [2, dRho]], mesh)
z=min(dRhoC)
gc_m = solveGravimetry(mesh, dRhoC, pnts)

plc = world + circ

###############################################################################
# Finishing the plots
fig = plt.figure()

ax1 = pg.plt.subplot(2, 1, 1)
ax1.plot(x, gz_a, '-b', marker='.', label='Analytical')
ax1.plot(x, gz_p, label='Integration: Polygon ')
ax1.plot(x, gc_m, label='Integration: Mesh')
# ax1.plot(x, dudz, label=r'FEM: $\frac{\partial u}{\partial z}$')
ax2 = pg.plt.subplot(2, 1, 2)
pg.show(plc, ax=ax2)
ax2.plot(x, x*0,  'bv')

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

