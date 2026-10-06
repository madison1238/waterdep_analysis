import csv
import numpy as np
import matplotlib.pyplot as plt

atom_ids = []
pyscal_cn = []
ovito_cn = []

with open("../summary/pyscal_vs_ovito_cn.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        atom_ids.append(int(row["Atom_ID"]))
        pyscal_cn.append(int(row["Pyscal_CN"]))
        ovito_cn.append(int(row["OVITO_CN"]))

atom_ids = np.array(atom_ids)
pyscal_cn = np.array(pyscal_cn)
ovito_cn = np.array(ovito_cn)

difference = pyscal_cn - ovito_cn
mean_cn = np.mean(pyscal_cn)
min_cn = np.min(pyscal_cn)
max_cn = np.max(pyscal_cn)
mean_abs_difference = np.mean(np.abs(difference))
different_atoms = np.sum(difference != 0)

fig, ax = plt.subplots(figsize=(12, 6))

ax.scatter(
    atom_ids,
    pyscal_cn,
    s=10,
    alpha=0.6,
    label="Pyscal"
)

ax.scatter(
    atom_ids,
    ovito_cn,
    s=20,
    facecolors="none",
    edgecolors="black",
    alpha=0.7,
    label="OVITO"
)


ax.set_xlabel("Atom ID")
ax.set_ylabel("Voronoi Coordination Number")
ax.set_title("Atom by Atom Voronoi Coordination Number")
ax.set_ylim(min_cn - 1, max_cn + 1)
ax.grid(alpha=0.2)
ax.legend()

text = (
    f"N = {len(atom_ids):,} atoms\n"
    f"Mean CN = {mean_cn:.2f}\n"
    f"CN range = {min_cn}–{max_cn}\n"
    f"Mean |ΔCN| = {mean_abs_difference:.2f}\n"
    f"Atoms differing = {different_atoms}"
)

ax.text(
    0.02,
    0.97,
    text,
    transform=ax.transAxes,
    verticalalignment="top",
    bbox=dict(boxstyle="round", alpha=0.8)
)
plt.tight_layout()
plt.savefig("../summary/atom_by_atom_voronoi_cn.png", dpi=300)
plt.show()


