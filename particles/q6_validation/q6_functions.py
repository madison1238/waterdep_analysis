from ovito.modifiers import ChillPlusModifier
import config
import numpy as np
from freud_methods import *
from pyscal_methods import *


def track_particle_order(positions, box, ids, target_id, cutoff=3.5):
    if target_id not in ids:
        raise ValueError(f"Particle ID {target_id} not found in frame.")
    
    target_index = np.where(ids == target_id)[0][0]

    q4_freud = steinhardt_cutoff(box,positions,cutoff=cutoff,average=True,l=4)
    q6_freud = steinhardt_cutoff(box,positions,cutoff=cutoff,average=True,l=6)
    q4_pyscal = pyscal_steinhardt(positions,box,method='cutoff',averaged=True,cutoff=cutoff,param=4)
    q6_pyscal = pyscal_steinhardt(positions,box,method='cutoff',averaged=True,cutoff=cutoff,param=6)
    

    return {
        "q4_freud": q4_freud[target_index],
        "q6_freud": q6_freud[target_index],
        "q4_pyscal": q4_pyscal[target_index],
        "q6_pyscal": q6_pyscal[target_index],
        "index": target_index
    }


def group_q6_by_phase(q6_values, labels):
    phases = {
        "liquid": [],
        "ice_ih": [],
        "ice_ic": [],
        "interfacial": [],
        "hydrate": [],
        "interfacial_hydrate": []
    }

    for q6, label in zip(q6_values,labels):
        if label == ChillPlusModifier.Type.OTHER:
            phases["liquid"].append(q6)

        elif label == ChillPlusModifier.Type.HEXAGONAL_ICE:
            phases["ice_ih"].append(q6)

        elif label == ChillPlusModifier.Type.CUBIC_ICE:
            phases["ice_ic"].append(q6)

        elif label == ChillPlusModifier.Type.INTERFACIAL_ICE:
            phases["interfacial"].append(q6)

        elif label == ChillPlusModifier.Type.HYDRATE:
            phases["hydrate"].append(q6)

        elif label == ChillPlusModifier.Type.INTERFACIAL_HYDRATE:
            phases["interfacial_hydrate"].append(q6)
    return phases


def find_largest_clusters(filename):
    cluster_sizes = {}
    with open(config.dump, 'r') as f:
        while True:
            line = f.readline()

            if not line:
                break
            if line.strip() == "ITEM: TIMESTEP":
                timestep = int(f.readline().strip())
            
                f.readline()
                num_atoms = int(float(f.readline().strip()))

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()

                cluster_sizes = {}

                for i in range(num_atoms):
                    line = f.readline()
                    cluster_id = int(float(line.split()[4]))
                    cluster_sizes[cluster_id] = (cluster_sizes.get(cluster_id, 0) + 1)
    top4 = sorted(
        cluster_sizes.items(),
        key=lambda x: x[1],
        reverse=True
    )[:4]

    return top4 