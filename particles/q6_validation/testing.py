from ovito_utils import load_frame
from freud_methods import *
from pyscal_methods import *
from q6_functions import * 
from ovito.modifiers import ChillPlusModifier
from plots import *
import config
import os
import csv



def compare_neighbors(positions, box, ids, target_id, cutoff=3.5):
    target_index = np.where(ids == target_id)[0][0]

    print("=" * 60)
    print("TARGET PARTICLE")
    print("=" * 60)
    print(f"Particle ID: {target_id}")
    print(f"Particle index: {target_index}")
    print(f"Position: {positions[target_index]}")
    print(f"Cutoff: {cutoff} Å")

    aq = freud.locality.AABBQuery(box, positions)
    freud_neighbors = aq.query(positions[target_index],{"r_max": cutoff, "exclude_ii": True}).toNeighborList()
    freud_indices = freud_neighbors.point_indices
    freud_distances = freud_neighbors.distances

    atoms = Atoms(symbols=["O"] * len(positions),positions=positions,cell=[box.Lx, box.Ly, box.Lz],pbc=True)
    pyscal.find_neighbors(atoms,method="cutoff",cutoff=cutoff)
    pyscal_indices = atoms.arrays["pyscal_neighbors"][target_index]
    pyscal_distances = atoms.arrays["pyscal_neighbordist"][target_index]
    valid = pyscal_indices >= 0
    pyscal_indices = pyscal_indices[valid]
    pyscal_distances = pyscal_distances[valid]

    print("\n" + "=" * 60)
    print("FREUD")
    print("=" * 60)
    print(f"Number of neighbors: {len(freud_indices)}")
    print("\nID\tIndex\tDistance")
    for index, distance in zip(freud_indices, freud_distances):
        print(f"{ids[index]}\t"f"{index}\t"f"{distance:.6f}")


    print("\n" + "=" * 60)
    print("PYSCAL")
    print("=" * 60)
    print(f"Number of neighbors: {len(pyscal_indices)}")
    print("\nID\tIndex\tDistance")
    for index, distance in zip(pyscal_indices, pyscal_distances):
        print(f"{ids[index]}\t"f"{index}\t"f"{distance:.6f}")

    freud_set = set(freud_indices)
    pyscal_set = set(pyscal_indices)

    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"Same number of neighbors: {len(freud_set) == len(pyscal_set)}")
    print(f"Same neighbors: {freud_set == pyscal_set}")

    print("\nOnly in Freud:")
    for index in sorted(freud_set - pyscal_set):
        print(f"ID: {ids[index]}, "f"Index: {index}")

    print("\nOnly in Pyscal:")
    for index in sorted(pyscal_set - freud_set):
        print(f"ID: {ids[index]}, "f"Index: {index}")
