print("Python started", flush=True)

from ovito.io import import_file

print("OVITO import successful", flush=True)

import config

print("Config import successful", flush=True)

print("Dump path:", config.dump, flush=True)

pipeline = import_file(config.dump)

print("Dump import successful", flush=True)

print("Frames:", pipeline.source.num_frames, flush=True)

data = pipeline.compute(0)

print("Frame computed", flush=True)

print(data.particles.keys(), flush=True)
