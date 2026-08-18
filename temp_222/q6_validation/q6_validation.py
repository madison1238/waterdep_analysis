from ovito.io import import_file
from ovito.modifiers import ChillPlusModifier
import config

print("Loading trajectory...", flush=True)

pipeline = import_file(config.dump)

print("Adding CHILL+...", flush=True)

pipeline.modifiers.append(
    ChillPlusModifier()
)

print("Computing frame 0...", flush=True)

data = pipeline.compute(0)

print("CHILL+ successful!", flush=True)

print("Particle properties:", flush=True)

for name in data.particles.keys():
    print(name, flush=True)
