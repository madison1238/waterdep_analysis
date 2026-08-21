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

    atoms = Atoms(symbols=["O"] * len(positions),positions=positions,cell=[box.Lx, box.Ly, box.Lz],pbc=True)
    pyscal.find_neighbors(atoms,method="cutoff",cutoff=cutoff)
    pyscal_indices = np.array(atoms[target_index].neighbors)

    print("\n" + "=" * 60)
    print("FREUD")
    print("=" * 60)
    print(f"Number of neighbors: {len(freud_indices)}")
    print("\nID\tIndex")
    for index in freud_indices:
        print(f"{ids[index]}\t{index}")


    print("\n" + "=" * 60)
    print("PYSCAL")
    print("=" * 60)
    print(f"Number of neighbors: {len(pyscal_indices)}")
    print("\nID\tIndex")
    for index in pyscal_indices:
        print(f"{ids[index]}\t{index}")

    freud_set = set(freud_indices)
    pyscal_set = set(pyscal_indices)

    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    print(f"Same number of neighbors: {len(freud_set) == len(pyscal_set)}")
    print(f"Same neighbors: {freud_set == pyscal_set}")

    print("\nOnly in Freud:")
    print([(ids[i], i) for i in sorted(freud_set - pyscal_set)])

    print("\nOnly in Pyscal:")
    print([(ids[i], i) for i in sorted(pyscal_set - freud_set)])
