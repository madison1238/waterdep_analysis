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
from ovito.io import import_file
import numpy as np

path = "../sims/sim_1/dump.mWC2.lammpstrj"

# ASE: read the last frame
original = read(path, index=-1, format="lammps-dump-text")

# OVITO: read the last frame
pipeline = import_file(path)
last_frame = pipeline.source.num_frames - 1
data = pipeline.compute(last_frame)

ovito_positions = np.asarray(data.particles["Position"])

print("ASE atoms:", len(original))
print("OVITO atoms:", len(ovito_positions))
print("Number of frames:", pipeline.source.num_frames)
print("Last frame index:", last_frame)

print("\nASE first 5 positions:")
print(original.positions[:5])

print("\nOVITO first 5 positions:")
print(ovito_positions[:5])

print("\nASE cell:")
print(original.cell)

print("\nOVITO cell:")
print(np.asarray(data.cell.matrix))

'''#original = read("../sims/sim_1/dump.mWC2.lammpstrj",index=-1,format="lammps-dump-text")
ids, positions, box = load_frame("../sims/sim_1/dump.mWC2.lammpstrj", frame=-1)

atoms = Atoms(
    symbols=["O"] * len(positions),
    positions=positions,
    cell=box.to_matrix(),
    pbc=True
)

print("Position range:")
print("OVITO min:", positions.min(axis=0))
print("OVITO max:", positions.max(axis=0))

print("\nASE position range:")
print("ASE min:", atoms.positions.min(axis=0))
print("ASE max:", atoms.positions.max(axis=0))

print("\nBox dimensions:")
print("OVITO:", box.Lx, box.Ly, box.Lz)
print("ASE:", atoms.cell.lengths())

pyscal.find_neighbors(atoms, method="voronoi")
cn = pyscal.coordination_number(atoms)

print("\nCoordination number statistics:")
print("Mean:", np.mean(cn))
print("Min:", np.min(cn))
print("Max:", np.max(cn))



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
print("Max:", np.max(data.particles.positions, axis=0))'''

