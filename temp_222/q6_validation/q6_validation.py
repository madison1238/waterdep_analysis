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
pipeline.modifiers.append(ExpressionSelectionModifier(expression="StructureType == 1 || StructureType == 2"))
pipeline.modifiers.append(ClusterAnalysisModifier(cutoff=3.5,only_selected=True,sort_by_size=True))

frame = 25
data = pipeline.compute(frame)
structure_types = np.asarray(data.particles["Structure Type"])
ice_like_count = np.sum((structure_types == 1) | (structure_types == 2))

print("Timestep:", data.attributes["Timestep"])
print("Ice-like molecules:", ice_like_count)

clusters = data.tables["clusters"]

print("Number of clusters:", data.attributes["ClusterAnalysis.cluster_count"])
print("Largest cluster:", data.attributes["ClusterAnalysis.largest_size"])