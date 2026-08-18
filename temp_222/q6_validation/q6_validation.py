from ovito.io import import_file
from ovito.modifiers import (
    ChillPlusModifier,
    ExpressionSelectionModifier,
    DeleteSelectedModifier,
    ClusterAnalysisModifier
)
import config


pipeline = import_file(config.dump)
pipeline.modifiers.append(ChillPlusModifier())
data = pipeline.compute(0)
print(data.particles.keys())
