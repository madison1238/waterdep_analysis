from ovito.io import import_file
import numpy as np
import freud

def read_lammps_q6(filename):
    q6 = {}

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith("ITEM: ATOMS"):
                break
        for line in f:
            if line.startswith("ITEM:"):
                break
            parts = line.split()

            atom_id = int(float(parts[0]))
            lammps_q6 = float(parts[6])

            q6[atom_id] = lammps_q6

    return q6

pipeline = import_file('../dump.cluster_q6.lammpstrj')
data = pipeline.compute(0)

ids = np.asarray(data.particles["Particle Identifier"])
positions = np.asarray(data.particles["Position"])

cell = data.cell

box = freud.box.Box(
    Lx=2464.0,
    Ly=2464.0,
    Lz=2464.0
)

steinhardt = freud.order.Steinhardt(l=6)
steinhardt.compute((box, positions),neighbors={"r_max": 12})

freud_q6 = steinhardt.particle_order

freud_q6_dict = {
    int(atom_id): q6 for atom_id, q6 in zip(ids,freud_q6)
}



lammps_q6 = read_lammps_q6('../dump.cluster_q6.lammpstrj')
with open('../summary/q6_comparison.txt', 'w') as f:
    f.write("Atom ID\tLAMMPS Q6\tCalculated Q6\tDifference\n")

    for atom_id in sorted(lammps_q6):


        lammps_value = lammps_q6[atom_id]
        freud_value = freud_q6_dict[atom_id]

        diff = freud_value - lammps_value

        f.write(
            f"{atom_id}\t"
            f"{lammps_value:.8f}\t"
            f"{freud_value:.8f}\t"
            f"{diff:.8e}\n"
        )
