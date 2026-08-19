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
data = pipeline.compute(0)
structure_types = np.asarray(data.particles["Structure Type"])
selection = np.asarray(data.particles["Selection"])

print("Structure types:")
print(np.unique(structure_types, return_counts=True))
print("Number selected:", np.sum(selection))
print("Number Ih:", np.sum(structure_types == 1))
print("Number Ic:", np.sum(structure_types == 2))