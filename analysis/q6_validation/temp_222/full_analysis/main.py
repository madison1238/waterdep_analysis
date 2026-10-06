import csv
import numpy as np
import matplotlib.pyplot as plt



pyscal_cn = []
ovito_cn = []
with open("pyscal_vs_ovito_cn.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pyscal_cn.append(int(row["Pyscal_CN"]))
        ovito_cn.append(int(row["OVITO_CN"]))
pyscal_cn = np.array(pyscal_cn)
ovito_cn = np.array(ovito_cn)

plt.figure(figsize=(7, 7))
plt.scatter(
    pyscal_cn,
    ovito_cn,
    alpha=0.4,
    s=20
)


min_cn = min(pyscal_cn.min(), ovito_cn.min())
max_cn = max(pyscal_cn.max(), ovito_cn.max())
plt.plot(
    [min_cn, max_cn],
    [min_cn, max_cn],
    linestyle="--",
    label="Perfect agreement"
)

plt.xlabel("Pyscal Voronoi coordination number")
plt.ylabel("OVITO Voronoi coordination number")
plt.title("Pyscal vs. OVITO Voronoi Coordination Number")
plt.xlim(min_cn - 1, max_cn + 1)
plt.ylim(min_cn - 1, max_cn + 1)
plt.gca().set_aspect("equal", adjustable="box")
plt.legend()
difference = pyscal_cn - ovito_cn
mean_cn = np.mean(pyscal_cn)
mean_abs_difference = np.mean(np.abs(difference))
different_atoms = np.sum(difference != 0)

text = (
    f"N = {len(pyscal_cn):,} atoms\n"
    f"Mean CN = {mean_cn:.2f}\n"
    f"CN range = {min_cn}–{max_cn}\n"
    f"Mean |ΔCN| = {mean_abs_difference:.2f}\n"
    f"Atoms differing = {different_atoms}"
)


plt.text(
    0.05,
    0.95,
    text,
    transform=plt.gca().transAxes,
    verticalalignment="top",
    bbox=dict(boxstyle="round", alpha=0.8))
plt.tight_layout()
plt.savefig("../summary/pyscal_vs_ovito_cn.png",)


