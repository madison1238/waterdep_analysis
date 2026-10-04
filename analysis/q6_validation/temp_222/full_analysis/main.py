'''from functions import calculate_pyscal_cn
from plot import * 
import csv
import os


sims = 1
sim_files = [f"../sims/sim_{i+1}/summary/ice_clusters.csv" for i in range(sims) ]
min_n = 5
max_n = 60
timestep_inteveral = 5'''

from ase.io import read
from ase import Atoms
import pyscal
import numpy as np
from functions import load_frame
from ovito.io import import_file

original = read("../sims/sim_1/dump.mWC2.lammpstrj",index=-1,format="lammps-dump-text")

ids, positions, box = load_frame("../sims/sim_1/dump.mWC2.lammpstrj",frame=-1)
ovito_atoms = Atoms(symbols=["O"] * len(positions),positions=positions,cell=[box.Lx, box.Ly, box.Lz],pbc=True)


print("Positions identical:",np.array_equal(original.positions, ovito_atoms.positions))
print("Cells identical:",np.array_equal(original.cell.array, ovito_atoms.cell.array))
print("PBC identical:",np.array_equal(original.pbc, ovito_atoms.pbc))


# Pyscal - original
pyscal.find_neighbors(original,method="voronoi")
original_cn = pyscal.coordination_number(original)

# Pyscal - OVITO
pyscal.find_neighbors(ovito_atoms,method="voronoi")
ovito_cn = pyscal.coordination_number(ovito_atoms)

position_diff = np.abs(original.positions - ovito_atoms.positions)
print("Maximum position difference:", np.max(position_diff))
print("Mean position difference:", np.mean(position_diff))
different_positions = np.where(np.any(original.positions != ovito_atoms.positions, axis=1))[0]
print("Number of atoms with different positions:",len(different_positions))
print("First 10 differing indices:", different_positions[:10])


print("Original cell:")
print(original.cell.array)
print("\nOVITO cell:")
print(ovito_atoms.cell.array)
print("\nCell difference:")
print(original.cell.array - ovito_atoms.cell.array)

print("Original PBC:", original.pbc)
print("OVITO PBC:", ovito_atoms.pbc)


print("\nOriginal CN:")
print("Mean:", np.mean(original_cn))
print("Min:", np.min(original_cn))
print("Max:", np.max(original_cn))

print("\nOVITO CN:")
print("Mean:", np.mean(ovito_cn))
print("Min:", np.min(ovito_cn))
print("Max:", np.max(ovito_cn))

print("\nMaximum CN difference:",
      np.max(np.abs(original_cn - ovito_cn)))


pipeline = import_file("../sims/sim_1/dump.mWC2.lammpstrj")
data = pipeline.compute(pipeline.source.num_frames - 1)
print("OVITO cell matrix:")
print(np.asarray(data.cell))
print("\nOVITO cell volume:")
print(data.cell.volume)
print("\nOVITO cell origin:")
print(data.cell[:, 3])
print("\nOVITO particle position range:")
print("Min:", np.min(data.particles.positions, axis=0))
print("Max:", np.max(data.particles.positions, axis=0))

