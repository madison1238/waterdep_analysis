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





'''frame = 0

os.makedirs(config.output, exist_ok=True)

with open(config.txt_file, 'w') as out:
    out.write("Q6 SUMMARY\n")
    out.write(f"{'=' * 20}\n\n")



with open(config.dump, 'r') as f:

    while True:
        line = f.readline()

        if not line:
            break
        if line.strip() == "ITEM: TIMESTEP":
            timestep = int(f.readline().strip())
            #timesteps.append(timestep)
        
            f.readline()
            num_atoms = int(float(f.readline().strip()))

            f.readline()
            f.readline()
            f.readline()
            f.readline()
            f.readline()

            #lammps_q6_timestep = []
            cluster_ids = []
            #atom_ids = []

            for i in range(num_atoms):
                line = f.readline()

                #atom_id = int(float(line.split()[0]))
                cluster_id = int(float(line.split()[5]))
                #atom_ids.append(atom_id)
                cluster_ids.append(cluster_id)

                #q6 = float(line.split()[6])
                #lammps_q6_timestep.append(q6)



            
            ids, positions, box, labels = load_frame(config.dump, frame, True)


            #CUTOFF
            print("working on q6 with freud cutoff...")
            freud_cutoff = steinhardt_cutoff(box,positions) # calculate all q6s
            cluster_freud_cutoff = average_q6_per_cluster(freud_cutoff,cluster_ids) # make a dictionary for each clusters size and q6
            cutoff_cluster_q6 = {cluster_id: c["avg_q6"]for cluster_id, c in cluster_freud_cutoff.items()} # extract averages (clusters q6)

            #doing the same for q4s
            print("working on q4 with freud cutoff...")
            freud_cutoff_q4 = steinhardt_cutoff(box, positions, l=4)
            cluster_freud_cutoff_q4 = average_q4_per_cluster(freud_cutoff_q4,cluster_ids)
            cutoff_cluster_q4 = {cluster_id: c["avg_q4"]for cluster_id, c in cluster_freud_cutoff_q4.items()}

            pyscal_cutoff = pyscal_steinhardt(positions, box) # calculate all q6s with pyscal
            cluster_pyscal_cutoff = average_q6_per_cluster(pyscal_cutoff,cluster_ids) # make the dictionary
            pyscal_cutoff_cluster_q6 = [c["avg_q6"]for c in cluster_pyscal_cutoff.values()] # extract q6s



            # CUTOFF AVERAGED
            print(f"working on q6 with freud cutoff averaged for timestep {timestep}")
            freud_cutoff_avg = steinhardt_cutoff(box,positions,average=True)
            cluster_freud_cutoff_avg = average_q6_per_cluster(freud_cutoff_avg,cluster_ids)
            #cutoff_cluster_q6 = {cluster_id: c["avg_q6"]for cluster_id, c in cluster_freud_cutoff_avg.items()}

            print("working on q4 with freud cutoff averaged...")
            freud_cutoff_avg_q4 = steinhardt_cutoff(box, positions, l=4, average=True)
            cluster_freud_cutoff_avg_q4 = average_q4_per_cluster(freud_cutoff_avg_q4,cluster_ids)
            cutoff_cluster_avg_q4 = {cluster_id: c["avg_q4"]for cluster_id, c in cluster_freud_cutoff_avg_q4.items()}

            print(f"working on q6 with pyscal cutoff averaged for timestep {timestep}")
            pyscal_cutoff_avg = pyscal_steinhardt(positions, box, averaged=True)
            cluster_pyscal_cutoff_avg = average_q6_per_cluster(pyscal_cutoff_avg,cluster_ids)
            #pyscal_cutoff_avg_cluster_q6 = [c["avg_q6"]for c in cluster_pyscal_cutoff_avg.values()]

            # stuff for plotting largest cluster size vs q6 for freud and pyscal similar to paper
            largest_cluster_id, largest_cluster_data = max(cluster_freud_cutoff_avg.items(),key=lambda item: item[1]["size"])
            largest_cluster_size.append(largest_cluster_data["size"])
            largest_q6_freud.append(cluster_freud_cutoff_avg[largest_cluster_id]["avg_q6"])
            largest_q6_pyscal.append(cluster_pyscal_cutoff_avg[largest_cluster_id]["avg_q6"])




            #VORONOI
            print("working on q6 with freud voronoi...")
            freud_voronoi = steinhardt_voronoi(box,positions)
            cluster_freud_voronoi = average_q6_per_cluster(freud_voronoi,cluster_ids)
            voronoi_cluster_q6 = {cluster_id: c["avg_q6"]for cluster_id, c in cluster_freud_voronoi.items()}

            print("working on q4 with freud voronoi...")
            freud_voronoi_q4 = steinhardt_voronoi(box, positions,l=4)
            cluster_freud_voronoi_q4 = average_q4_per_cluster(freud_voronoi_q4,cluster_ids)
            voronoi_cluster_q4 = {cluster_id: c["avg_q4"]for cluster_id, c in cluster_freud_voronoi_q4.items()}

            pyscal_voronoi = pyscal_steinhardt(positions, box, method='voronoi')
            cluster_pyscal_voronoi  = average_q6_per_cluster(pyscal_voronoi,cluster_ids)
            pyscal_vornoi_cluster_q6 = [c["avg_q6"]for c in cluster_pyscal_voronoi.values()]


            # VORONOI AVERAGED
            print("working on q6 with freud voronoi averaged...")
            freud_voronoi_avg = steinhardt_voronoi(box,positions,average=True)
            cluster_freud_voronoi_avg = average_q6_per_cluster(freud_voronoi_avg,cluster_ids)
            voronoi_avg_cluster_q6 = {cluster_id: c["avg_q6"]for cluster_id, c in cluster_freud_voronoi_avg.items()}

            print("working on q4 with freud voronoi averaged...")
            freud_voronoi_avg_q4 = steinhardt_voronoi(box, positions,average=True, l=4)
            cluster_freud_voronoi_avg_q4 = average_q4_per_cluster(freud_voronoi_avg_q4,cluster_ids)
            voronoi_cluster_avg_q4 = {cluster_id: c["avg_q4"]for cluster_id, c in cluster_freud_voronoi_avg_q4.items()}
            
            pyscal_voronoi_avg = pyscal_steinhardt(positions, box, method='voronoi', averaged=True)
            cluster_pyscal_voronoi_avg  = average_q6_per_cluster(pyscal_voronoi_avg,cluster_ids)
            pyscal_vornoi_avg_cluster_q6 = [c["avg_q6"]for c in cluster_pyscal_voronoi_avg.values()]


            frame += 1

            with open(config.txt_file, 'a') as out:
                out.write(f"Timestep: {timestep}\n\n")

                out.write(f"LAMMPS\n")
                out.write(f"Max: {lammps_q6_maxs[-1]}\n")
                out.write(f"Avg: {lammps_q6_avgs[-1]}\n\n")

                out.write(f"FREUD CUTOFF\n")
                out.write(f"Max: {cutoff_maxs[-1]}\n")
                out.write(f"Avg: {cutoff_avgs[-1]}\n\n")

                out.write(f"PYSCAL CUTOFF\n")
                out.write(f"Max: {max(pyscal_cutoff_cluster_q6)}\n")
                out.write(f"Avg: {sum(pyscal_cutoff_cluster_q6) / len(pyscal_cutoff_cluster_q6)}\n\n")

                out.write(f"FREUD CUTOFF AVERAGED\n")
                out.write(f"Max: {cutoff_avg_maxs[-1]}\n")
                out.write(f"Avg: {cutoff_avg_avgs[-1]}\n\n")

                out.write(f"PYSCAL CUTOFF AVERAGED\n")
                out.write(f"Max: {max(pyscal_cutoff_avg_cluster_q6)}\n")
                out.write(f"Avg: {sum(pyscal_cutoff_avg_cluster_q6) / len(pyscal_cutoff_avg_cluster_q6)}\n\n")

                out.write(f"FREUD VORONOI\n")
                out.write(f"Max: {voronoi_maxs[-1]}\n")
                out.write(f"Avg: {voronoi_avgs[-1]}\n\n")

                out.write(f"PYSCAL VORONOI\n")
                out.write(f"Max: {max(pyscal_vornoi_cluster_q6)}\n")
                out.write(f"Avg: {sum(pyscal_vornoi_cluster_q6) / len(pyscal_vornoi_cluster_q6)}\n\n")

                out.write(f"FREUD VORONOI AVERAGED\n")
                out.write(f"Max: {voronoi_avg_maxs[-1]}\n")
                out.write(f"Avg: {voronoi_avg_avgs[-1]}\n\n")

                out.write(f"PYSCAL VORONOI AVERAGED\n")
                out.write(f"Max: {max(pyscal_vornoi_avg_cluster_q6)}\n")
                out.write(f"Avg: {sum(pyscal_vornoi_avg_cluster_q6) / len(pyscal_vornoi_avg_cluster_q6)}\n\n")

           

#plot_avgs(timesteps,lammps_q6_avgs, cutoff_avgs, cutoff_avg_avgs, voronoi_avgs, voronoi_avg_avgs)
#plot_maxs(timesteps,lammps_q6_maxs, cutoff_maxs, cutoff_avg_maxs, voronoi_maxs, voronoi_avg_maxs)
#plot_cluster_q6_history(cluster_history_4)
#plot_q6_largest_cluster_freud_pyscal(largest_cluster_size, largest_cluster_q6_freud, largest_cluster_q6_pyscal)
#plot_final_q6_vs_q4_color(final_results)
plot_q6_largest_cluster_freud_pyscal(largest_cluster_size,largest_q6_freud,largest_q6_pyscal)'''