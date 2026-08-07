import freud
import numpy as np

def steinhardt_cutoff(box,positions,cutoff=3.5,average=False,l=6):
    aq = freud.locality.AABBQuery(box, positions)
    neighbors = aq.query(positions,dict(r_max=cutoff)).toNeighborList()

    counts = np.bincount(neighbors.query_point_indices,
                     minlength=len(positions))
    #print("Average neighbors:", counts.mean())
    #print("Minimum neighbors:", counts.min())
    #print("Maximum neighbors:", counts.max())

    q = freud.order.Steinhardt(l=l, average=average)
    q.compute((box, positions),neighbors=neighbors)
    return q.particle_order


def steinhardt_voronoi(box,positions,average=False,l=6):
    vor = freud.locality.Voronoi()
    vor.compute((box, positions))

    counts = np.bincount(vor.nlist.query_point_indices,
                     minlength=len(positions))

    #print("Average Voronoi neighbors:", counts.mean())
    

    q = freud.order.Steinhardt(l=l,average=average)
    q.compute((box, positions),neighbors=vor.nlist)
    return q.particle_order