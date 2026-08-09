from ovito.modifiers import ChillPlusModifier
import config

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