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

    freud_q6 = steinhardt_cutoff_no_self(box,positions,cutoff=3.5,average=True,l=6)[target_index]
    freud_q4 = steinhardt_cutoff_no_self(box,positions,cutoff=3.5,average=True,l=4)[target_index]
    pyscal_q6 = pyscal_steinhardt(positions, box, method='cutoff', averaged=True, cutoff=3.5, param=6)[target_index]
    pyscal_q4 = pyscal_steinhardt(positions, box, method='cutoff', averaged=True, cutoff=3.5, param=4)[target_index]

    print("\n" + "=" * 60)
    print("AVERAGED STEINHARDT VALUES")
    print("=" * 60)

    print("\nFREUD")
    print(f"q4: {freud_q4}")
    print(f"q6: {freud_q6}")

    print("\nPYSCAL")
    print(f"q4: {pyscal_q4}")
    print(f"q6: {pyscal_q6}")

    print("\n" + "=" * 60)
    print("DIFFERENCES")
    print("=" * 60)

    print(f"q4 difference: {freud_q4 - pyscal_q4}")
    print(f"q6 difference: {freud_q6 - pyscal_q6}")

