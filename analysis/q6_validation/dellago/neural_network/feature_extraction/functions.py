from ovito.io import import_file
from ovito.modifiers import (
    ChillPlusModifier,
    ExpressionSelectionModifier,
    ClusterAnalysisModifier
)
import config
import numpy as np
import csv
import os



def largest_cluster_info(dump, frame):
    #returns largest cluster size n, cluster_ids in largest, num of IC IH, fraction of IC and IH
    pipeline = import_file(dump)
    pipeline.modifiers.append(ChillPlusModifier())
    pipeline.modifiers.append(ExpressionSelectionModifier(expression="StructureType == 1 || StructureType == 2"))
    pipeline.modifiers.append(ClusterAnalysisModifier(cutoff=3.5,only_selected=True,sort_by_size=True))
    
    data = pipeline.compute(frame)
    structure_types = np.asarray(data.particles["Structure Type"])
    cluster_ids = np.asarray(data.particles["Cluster"])
    timestep = int(data.attributes["Timestep"])
    largest_cluster_id = int(data.attribute.get["ClusterAnalysis.largest_cluster"],0)
    largest_cluster_size = int(data.attributes.get["ClusterAnalysis.largest_size"],0)


    ids_in_largest = cluster_ids == largest_cluster_id
    ih = np.sum(structure_types[in_largest] == 1)
    ic = np.sum(structure_types[in_largest] == 2)
    ih_fraction = ih / largest_cluster_size
    ic_fraction = ic / largest_cluster_size

    timestep = int(data.attributes["Timestep"])
    return largest_cluster_size, ids_in_largest, ic, ih, ic_fraction, ih_fraction

