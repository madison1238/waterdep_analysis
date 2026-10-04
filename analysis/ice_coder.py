import sys
import MDAnalysis as mda
sys.path.append("../Scripts/")
from icecoder import IceCoder

print("Creating IceCoder...")
ic = IceCoder()


print("Loading trajectory...")
u = mda.Universe.empty(n_atoms=524288, trajectory=True)

u.load_new(
    "/scratch/group/p.mch250033.000/madison/water_deposition/temp_200/s_524288/dump.cluster_q6.lammpstrj",
    format="LAMMPSDUMP"
)

print("Atoms:", len(u.atoms))
print("Frames:", len(u.trajectory))

print("Running featurizer...")
ic.featurizer(
    mda_universe=u,
    stop=1,   
    mode="serial"
)


print("Projecting...")
ic.project()

print("Predicting...")
ic.predict()

print("Done!")
print("Number of classifications:", len(ic.ices))
print("First 20 labels:", ic.ices[:20])