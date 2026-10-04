import freud
import pyscal3 as pyscal
from ase import Atoms
import numpy as np


#Freud
def steinhardt_cutoff(box,positions,cutoff=3.5,average=False,l=6):
    aq = freud.locality.AABBQuery(box, positions)
    neighbors = aq.query(positions,dict(r_max=cutoff)).toNeighborList()
    q = freud.order.Steinhardt(l=l, average=average)
    q.compute((box, positions),neighbors=neighbors)
    return q.particle_order

#Pyscal
def pyscal_steinhardt(positions, box, method='cutoff', averaged=False, cutoff=3.5, param=6):
    atoms = Atoms(symbols=["O"] * len(positions), positions=positions, cell=[box.Lx, box.Ly, box.Lz], pbc=True)

    if method == 'cutoff':
        pyscal.find_neighbors(atoms, method='cutoff', cutoff=cutoff)
    elif method == 'voronoi':
        pyscal.find_neighbors(atoms, method='voronoi')
    if averaged == False:
        q=pyscal.steinhardt_parameter(atoms, l=[param])[0]
    else:
        q = pyscal.steinhardt_parameter(atoms, l=[param], averaged=True)[0]
    return q