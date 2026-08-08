from ovito_utils import load_frame
from freud_methods import *
from pyscal_methods import *
from q6_functions import *
from plots import *
from ovito.modifiers import ChillPlusModifier
import config
import os




#timesteps = []

'''lammps_q6_timestep = []

lammps_q6_maxs = []
lammps_q6_avgs = []

cutoff_maxs = []
cutoff_avgs = []

cutoff_avg_maxs = []
cutoff_avg_avgs = []

voronoi_maxs = []
voronoi_avgs = []

voronoi_avg_avgs = []
voronoi_avg_maxs = []

largest_cluster_size = []
largest_cluster_q6_freud = []
largest_cluster_q6_pyscal = []'''

final_results = {
    "phase": None,
    "Cutoff": {"q4": None, "q6": None},
    "Cutoff Averaged": {"q4": None, "q6": None},
    "Voronoi": {"q4": None,"q6": None},
    "Voronoi Averaged": {"q4": None,"q6": None}
}


frame = 0

os.makedirs(config.output, exist_ok=True)

with open(config.txt_file, 'w') as out:
    out.write("Q6 SUMMARY\n")
    out.write(f"{'=' * 20}\n\n")




with open(config.dump, 'r') as f:
    #top4 = find_largest_clusters(config.dump)
    #top4_ids = [cid for cid, size in top4]
    #top4_atoms = {}

    #final_cluster_members = get_cluster_members(config.dump)
    #for cid in top4_ids:
        #top4_atoms[cid] = final_cluster_members[cid]

    '''cluster_history_4 = {
    cid: {
        "time": [],
        "size": [],
        "lammps": [],
        "cutoff": [],
        "cutoff_avg": [],
        "voronoi": [],
        "voronoi_avg": [],
        "phase": []
    }for cid in top4_ids}'''

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


            '''current_cluster_members = {}

            for atom_id, cid in zip(atom_ids, cluster_ids):
                if cid not in current_cluster_members:
                    current_cluster_members[cid] = set()
                current_cluster_members[cid].add(atom_id)'''
            
            ids, positions, box, labels = load_frame(config.dump, frame, True)

            #cluster_lammps = average_q6_per_cluster(lammps_q6_timestep,cluster_ids)
            #lammps_cluster_q6 = [c["avg_q6"]for c in cluster_lammps.values()]
            

            #CUTOFF
            freud_cutoff = steinhardt_cutoff(box,positions) # calculate all q6s
            cluster_freud_cutoff = average_q6_per_cluster(freud_cutoff,cluster_ids) # make a dictionary for each clusters size and q6
            cutoff_cluster_q6 = {cluster_id: c["avg_q6"]for cluster_id, c in cluster_freud_cutoff.items()} # extract averages (clusters q6)

            #doing the same for q4s
            freud_cutoff_q4 = steinhardt_cutoff(box, positions, l=4)
            cluster_freud_cutoff_q4 = average_q4_per_cluster(freud_cutoff_q4,cluster_ids)
            cutoff_cluster_q4 = {cluster_id: c["avg_q4"]for cluster_id, c in cluster_freud_cutoff_q4.items()}

            '''pyscal_cutoff = pyscal_steinhardt(positions, box) # calculate all q6s with pyscal
            cluster_pyscal_cutoff = average_q6_per_cluster(pyscal_cutoff,cluster_ids) # make the dictionary
            pyscal_cutoff_cluster_q6 = [c["avg_q6"]for c in cluster_pyscal_cutoff.values()] # extract q6s'''



            # CUTOFF AVERAGED
            freud_cutoff_avg = steinhardt_cutoff(box,positions,average=True)
            cluster_freud_cutoff_avg = average_q6_per_cluster(freud_cutoff_avg,cluster_ids)
            cutoff_avg_cluster_q6 = {cluster_id: c["avg_q6"]for cluster_id, c in cluster_freud_cutoff_avg.items()}

            freud_cutoff_avg_q4 = steinhardt_cutoff(box, positions, l=4, average=True)
            cluster_freud_cutoff_avg_q4 = average_q4_per_cluster(freud_cutoff_avg_q4,cluster_ids)
            cutoff_cluster_avg_q4 = {cluster_id: c["avg_q4"]for cluster_id, c in cluster_freud_cutoff_avg_q4.items()}

            '''pyscal_cutoff_avg = pyscal_steinhardt(positions, box, averaged=True)
            cluster_pyscal_cutoff_avg = average_q6_per_cluster(pyscal_cutoff_avg,cluster_ids)
            pyscal_cutoff_avg_cluster_q6 = [c["avg_q6"]for c in cluster_pyscal_cutoff_avg.values()]'''

            # stuff for plotting largest cluster size vs q6 for freud and pyscal similar to paper
            '''largest_cluster_id, largest_cluster = max(cluster_lammps.items(),key=lambda item: item[1]["size"])
            largest_cluster_size.append(cluster_lammps[largest_cluster_id]["size"])
            largest_cluster_q6_freud.append(cluster_freud_cutoff_avg[largest_cluster_id]["avg_q6"])
            largest_cluster_q6_pyscal.append(cluster_pyscal_cutoff_avg[largest_cluster_id]["avg_q6"])'''


            #VORONOI
            freud_voronoi = steinhardt_voronoi(box,positions)
            cluster_freud_voronoi = average_q6_per_cluster(freud_voronoi,cluster_ids)
            voronoi_cluster_q6 = {cluster_id: c["avg_q6"]for cluster_id, c in cluster_freud_voronoi.items()}

            freud_voronoi_q4 = steinhardt_voronoi(box, positions,l=4)
            cluster_freud_voronoi_q4 = average_q4_per_cluster(freud_voronoi_q4,cluster_ids)
            voronoi_cluster_q4 = {cluster_id: c["avg_q4"]for cluster_id, c in cluster_freud_voronoi_q4.items()}

            '''pyscal_voronoi = pyscal_steinhardt(positions, box, method='voronoi')
            cluster_pyscal_voronoi  = average_q6_per_cluster(pyscal_voronoi,cluster_ids)
            pyscal_vornoi_cluster_q6 = [c["avg_q6"]for c in cluster_pyscal_voronoi.values()]'''


            # VORONOI AVERAGED
            freud_voronoi_avg = steinhardt_voronoi(box,positions,average=True)
            cluster_freud_voronoi_avg = average_q6_per_cluster(freud_voronoi_avg,cluster_ids)
            voronoi_avg_cluster_q6 = {cluster_id: c["avg_q6"]for cluster_id, c in cluster_freud_voronoi_avg.items()}

            freud_voronoi_avg_q4 = steinhardt_voronoi(box, positions,average=True, l=4)
            cluster_freud_voronoi_avg_q4 = average_q4_per_cluster(freud_voronoi_avg_q4,cluster_ids)
            voronoi_cluster_avg_q4 = {cluster_id: c["avg_q4"]for cluster_id, c in cluster_freud_voronoi_avg_q4.items()}
            
            '''pyscal_voronoi_avg = pyscal_steinhardt(positions, box, method='voronoi', averaged=True)
            cluster_pyscal_voronoi_avg  = average_q6_per_cluster(pyscal_voronoi_avg,cluster_ids)
            pyscal_vornoi_avg_cluster_q6 = [c["avg_q6"]for c in cluster_pyscal_voronoi_avg.values()]'''

            '''lammps_q6_maxs.append(max(lammps_cluster_q6))
            lammps_q6_avgs.append(sum(lammps_cluster_q6)/len(lammps_cluster_q6))

            cutoff_maxs.append(max(cutoff_cluster_q6))
            cutoff_avgs.append(sum(cutoff_cluster_q6)/len(cutoff_cluster_q6))

            cutoff_avg_maxs.append(max(cutoff_avg_cluster_q6))
            cutoff_avg_avgs.append(sum(cutoff_avg_cluster_q6)/len(cutoff_avg_cluster_q6))

            voronoi_maxs.append(max(voronoi_cluster_q6))
            voronoi_avgs.append(sum(voronoi_cluster_q6)/len(voronoi_cluster_q6))

            voronoi_avg_maxs.append(max(voronoi_avg_cluster_q6))
            voronoi_avg_avgs.append(sum(voronoi_avg_cluster_q6)/len(voronoi_avg_cluster_q6))'''


            cluster_phases = get_dominant_phase_per_cluster(cluster_ids,labels)
            final_results["phase"] = cluster_phases

            final_results["Cutoff"]["q4"] = cutoff_cluster_q4
            final_results["Cutoff"]["q6"] = cutoff_cluster_q6

            final_results["Cutoff Averaged"]["q4"] = cutoff_cluster_avg_q4
            final_results["Cutoff Averaged"]["q6"] = cutoff_avg_cluster_q6

            final_results["Voronoi"]["q4"] = voronoi_cluster_q4
            final_results["Voronoi"]["q6"] = voronoi_cluster_q6

            final_results["Voronoi Averaged"]["q4"] = voronoi_cluster_avg_q4
            final_results["Voronoi Averaged"]["q6"] = voronoi_avg_cluster_q6




            frame += 1

            with open(config.txt_file, 'a') as out:
                out.write(f"Timestep: {timestep}\n\n")

                '''out.write(f"LAMMPS\n")
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
                out.write(f"Avg: {sum(pyscal_vornoi_avg_cluster_q6) / len(pyscal_vornoi_avg_cluster_q6)}\n\n")'''

            '''for original_cid in top4_ids:
                target_atoms = top4_atoms[original_cid]
                valid_cluster_members = {cid: members for cid, members in current_cluster_members.items() if cid in cluster_lammps}
                matched_cid, overlap = find_matching_cluster(target_atoms,valid_cluster_members)

                if matched_cid is None:
                    continue

                mask = np.array(cluster_ids) == matched_cid
                cluster_labels = labels[mask]

                liquid = np.sum(cluster_labels == 0)
                ih = np.sum(cluster_labels == 1)
                ic = np.sum(cluster_labels == 2)
                interface = np.sum(cluster_labels == 3)

                counts = {
                    "Liquid": liquid,
                    "Ice Ih": ih,
                    "Ice Ic": ic,
                    "Interfacial": interface
                }

                dominant_phase = max(counts, key=counts.get)


                cluster_history_4[original_cid]["time"].append(timestep)
                cluster_history_4[original_cid]["size"].append(cluster_lammps[matched_cid]["size"])

                cluster_history_4[original_cid]["lammps"].append(cluster_lammps[matched_cid]["avg_q6"])
                cluster_history_4[original_cid]["cutoff"].append(cluster_freud_cutoff[matched_cid]["avg_q6"])
                cluster_history_4[original_cid]["cutoff_avg"].append(cluster_freud_cutoff_avg[matched_cid]["avg_q6"])
                cluster_history_4[original_cid]["voronoi"].append(cluster_freud_voronoi[matched_cid]["avg_q6"])
                cluster_history_4[original_cid]["voronoi_avg"].append(cluster_freud_voronoi_avg[matched_cid]["avg_q6"])
                cluster_history_4[original_cid]["phase"].append(dominant_phase)'''

#plot_avgs(timesteps,lammps_q6_avgs, cutoff_avgs, cutoff_avg_avgs, voronoi_avgs, voronoi_avg_avgs)
#plot_maxs(timesteps,lammps_q6_maxs, cutoff_maxs, cutoff_avg_maxs, voronoi_maxs, voronoi_avg_maxs)
#plot_cluster_q6_history(cluster_history_4)
#plot_q6_largest_cluster_freud_pyscal(largest_cluster_size, largest_cluster_q6_freud, largest_cluster_q6_pyscal)
plot_final_q6_vs_q4(final_results)