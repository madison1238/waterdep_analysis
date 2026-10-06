from ovito.io import import_file
from ovito.modifiers import VoronoiAnalysisModifier
from ase import Atoms
import pyscal
import numpy as np
import csv


filename = "../sims/sim_1/dump.mWC2.lammpstrj"

#OVITO
pipeline = import_file(filename)
frame = pipeline.source.num_frames - 1
data = pipeline.compute(frame)
ids = np.asarray(data.particles["Particle Identifier"])
positions = np.asarray(data.particles["Position"])
cell = np.asarray(data.cell.matrix)
box_lengths = [
    cell[0, 0],
    cell[1, 1],
    cell[2, 2]
]
print("Atoms:", len(ids))
print("Frame:", frame)
print("Box:", box_lengths)


pipeline.modifiers.append(VoronoiAnalysisModifier())
data = pipeline.compute(frame)
ovito_cn = np.asarray(data.particles["Coordination"])
print("\nOVITO CN:")
print("Mean:", np.mean(ovito_cn))
print("Min:", np.min(ovito_cn))
print("Max:", np.max(ovito_cn))


#PYSCAL
atoms = Atoms(
    symbols=["O"] * len(positions),
    positions=positions,
    cell=box_lengths,
    pbc=True
)


pyscal.find_neighbors(atoms,method="voronoi")
pyscal_cn = np.asarray(pyscal.coordination_number(atoms))
print("\nPyscal CN:")
print("Mean:", np.mean(pyscal_cn))
print("Min:", np.min(pyscal_cn))
print("Max:", np.max(pyscal_cn))

difference = pyscal_cn - ovito_cn

print("\nComparison:")
print("Mean difference:", np.mean(difference))
print("Mean absolute difference:", np.mean(np.abs(difference)))
print("Maximum absolute difference:", np.max(np.abs(difference)))
print(
    "Atoms with different CN:",
    np.sum(difference != 0)
)



with open("../summary/pyscal_vs_ovito_cn.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Atom_ID",
        "Pyscal_CN",
        "OVITO_CN",
        "Difference"
    ])
    for atom_id, p_cn, o_cn, diff in zip(
        ids,
        pyscal_cn,
        ovito_cn,
        difference
    ):
        writer.writerow([
            atom_id,
            p_cn,
            o_cn,
            diff
        ])
print("\nSaved: pyscal_vs_ovito_cn.csv")


