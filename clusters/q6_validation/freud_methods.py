import freud
import numpy as np
from collections import defaultdict

def average_q6_per_cluster(q6_values, cluster_ids):
    min_size = 3

    clusters = defaultdict(list)

    for q6, cluster in zip(q6_values, cluster_ids):
        clusters[cluster].append(q6)

    averages = {}
    for cluster, values in clusters.items():
        if len(values) < min_size:
            continue

        averages[cluster] = {
            "size": len(values),
            "avg_q6": np.mean(values)
        }

    return averages

def average_q4_per_cluster(q4_values, cluster_ids):
    min_size = 3

    clusters = defaultdict(list)

    for q6, cluster in zip(q4_values, cluster_ids):
        clusters[cluster].append(q6)

    averages = {}
    for cluster, values in clusters.items():
        if len(values) < min_size:
            continue

        averages[cluster] = {
            "size": len(values),
            "avg_q4": np.mean(values)
        }

    return averages


def steinhardt_cutoff(box,positions,cutoff=3.5,average=False,l=6):
    aq = freud.locality.AABBQuery(box, positions)
    neighbors = aq.query(positions,dict(r_max=cutoff)).toNeighborList()
    q = freud.order.Steinhardt(l=l, average=average)
    q.compute((box, positions),neighbors=neighbors)
    return q.particle_order


def steinhardt_voronoi(box,positions,average=False,l=6):
    vor = freud.locality.Voronoi()
    vor.compute((box, positions))

    #counts = np.bincount(vor.nlist.query_point_indices, minlength=len(positions))
    #print("Average Voronoi neighbors:", counts.mean())
    
    q = freud.order.Steinhardt(l=l,average=average)
    q.compute((box, positions),neighbors=vor.nlist)
    return q.particle_order




