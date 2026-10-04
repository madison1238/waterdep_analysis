import pyscal3 as pyscal
from ase import Atoms
import numpy as np



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