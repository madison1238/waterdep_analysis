from ovito_utils import load_frame
from freud_methods import *
from pyscal_methods import *
from q6_functions import *
from plots import *
from ovito.modifiers import ChillPlusModifier
import config
import os



final_timestep,final_frame = find_last_timestep(config.dump)

final_clusters = find_largest_clusters(config.dump,final_timestep)
for rank, (cluster_id, cluster_data) in enumerate(final_clusters.items(), start=1):
    print(
        f"Rank {rank} "
        f"Cluster {cluster_id}, "
        f"Size {cluster_data['size']}"
    )

for rank, (cluster_id, cluster_data) in enumerate(final_clusters.items(),start=1):

    final_cluster_size = cluster_data["size"]
    final_cluster_particles = cluster_data["particle_ids"]

    print("\n" + "=" * 60)
    print(f"Tracking final cluster rank {rank}")
    print(f"Cluster ID: {cluster_id}")
    print(f"Cluster size: {final_cluster_size}")
    print(f"Number of particle IDs:{len(final_cluster_particles)}")
    print("=" * 60)


    output_csv = (f"{config.output}/cluster_q6_tracking_rank{rank}_cluster{cluster_id}.csv")

    track_cluster_q6(
        filename=config.dump,
        final_timestep=final_timestep,
        final_frame=final_frame,
        final_cluster_id=cluster_id,
        final_cluster_particles=final_cluster_particles,
        final_cluster_size=final_cluster_size,
        final_cluster_rank=rank,
        interval=10000,
        output_csv=output_csv
    )
