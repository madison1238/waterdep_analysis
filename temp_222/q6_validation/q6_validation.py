from ovito.io import import_file
from ovito.modifiers import (
    ChillPlusModifier,
    ExpressionSelectionModifier,
    ClusterAnalysisModifier
)
import config
import numpy as np

pipeline = import_file(config.dump)
pipeline.modifiers.append(ChillPlusModifier())

test_frames = [0, 25, 50, 75, 100, 125, 150, 175, 200]

for frame in test_frames:
    data = pipeline.compute(frame)
    structure_types = np.asarray(data.particles["Structure Type"])
    ih = np.sum(structure_types == 1)
    ic = np.sum(structure_types == 2)
    print(
        f"Frame {frame:3d} | "
        f"Timestep {data.attributes['Timestep']:>10} | "
        f"Ih = {ih:5d} | "
        f"Ic = {ic:5d} | "
        f"Ice-like = {ih + ic:5d}"
    )