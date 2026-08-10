from ovito_utils import load_frame
from freud_methods import *
from pyscal_methods import *
from q6_functions import * 
from ovito.modifiers import ChillPlusModifier
from plots import *
import config
import os
import csv


frame = 0
target_id = 4093
os.makedirs(config.output, exist_ok=True)

output_file = f"{config.output}/single_particle_q4_q6.csv"
with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "timestep",
        "particle_id",
        "phase",
        "q4_freud",
        "q6_freud",
        "q4_pyscal",
        "q6_pyscal"
    ])


    with open(config.dump, 'r') as f:
        while True:
            line = f.readline()

            if not line:
                break
            if line.strip() == "ITEM: TIMESTEP":
                timestep = int(f.readline().strip())
            
                f.readline()
                num_atoms = int(float(f.readline().strip()))

                f.readline()
                f.readline()
                f.readline()
                f.readline()
                f.readline()


                for i in range(num_atoms):
                    line = f.readline()

                    
                
                ids, positions, box, labels = load_frame(config.dump, frame, True)

                particle_values = track_particle_order(positions, box, ids, target_id)
                particle_phase = labels[particle_values["index"]]


                writer.writerow([
                    timestep,
                    target_id,
                    particle_phase,
                    particle_values["q4_freud"],
                    particle_values["q6_freud"],
                    particle_values["q4_pyscal"],
                    particle_values["q6_pyscal"]
                ])

                frame += 1


            '''freud_cutoff = steinhardt_cutoff(box,positions)
            freud_cutoff_q4 = steinhardt_cutoff(box, positions, l=4)
            pyscal_cutoff = pyscal_steinhardt(positions,box)
            cutoff_labels = group_q6_by_phase(freud_cutoff,labels )

            freud_cutoff_avg = steinhardt_cutoff(box,positions,average=True)
            freud_cutoff_avg_q4 = steinhardt_cutoff(box, positions, average=True, l=4)
            pyscal_cutoff_avg = pyscal_steinhardt(positions,box, averaged=True)
            cutoff_avg_labels = group_q6_by_phase(freud_cutoff_avg,labels)

            freud_voronoi = steinhardt_voronoi(box,positions)
            freud_voronoi_q4 = steinhardt_voronoi(box, positions, l=4)
            pyscal_voronoi = pyscal_steinhardt(positions,box, method='voronoi')
            voronoi_labels = group_q6_by_phase(freud_voronoi,labels)

            freud_voronoi_avg = steinhardt_voronoi(box,positions,average=True)
            freud_voronoi_avg_q4 = steinhardt_voronoi(box, positions, average=True, l=4)
            avg_pyscal_voronoi = pyscal_steinhardt(positions,box, method='voronoi', averaged=True)
            voronoi_avg_labels = group_q6_by_phase(freud_voronoi_avg,labels)'''

            '''lammps_q6_maxs.append(max(lammps_q6_timestep))
            lammps_q6_avgs.append(sum(lammps_q6_timestep)/len(lammps_q6_timestep))

            cutoff_maxs.append(max(freud_cutoff))
            cutoff_avgs.append(sum(freud_cutoff)/len(freud_cutoff))

            cutoff_avg_maxs.append(max(freud_cutoff_avg))
            cutoff_avg_avgs.append(sum(freud_cutoff_avg)/len(freud_cutoff_avg))

            voronoi_maxs.append(max(freud_voronoi))
            voronoi_avgs.append(sum(freud_voronoi)/len(freud_voronoi))

            voronoi_avg_maxs.append(max(freud_voronoi_avg))
            voronoi_avg_avgs.append(sum(freud_voronoi_avg)/len(freud_voronoi_avg))'''


            '''final_results["Cutoff"]["q4"] = freud_cutoff_q4
            final_results["Cutoff"]["q6"] = freud_cutoff

            final_results["Cutoff Averaged"]["q4"] = freud_cutoff_avg_q4
            final_results["Cutoff Averaged"]["q6"] = freud_cutoff_avg

            final_results["Voronoi"]["q4"] = freud_voronoi_q4
            final_results["Voronoi"]["q6"] = freud_voronoi

            final_results["Voronoi Averaged"]["q4"] = freud_voronoi_avg_q4
            final_results["Voronoi Averaged"]["q6"] = freud_voronoi_avg

            final_results['labels'] = labels'''

            '''with open(config.txt_file, 'a') as out:
                out.write(f"Timestep: {timestep}\n\n")

                out.write(f"LAMMPS\n")
                out.write(f"Max: {lammps_q6_maxs[-1]}\n")
                out.write(f"Avg: {lammps_q6_avgs[-1]}\n\n")

                out.write(f"FREUD CUTOFF\n")
                out.write(f"Max: {cutoff_maxs[-1]}\n")
                out.write(f"Avg: {cutoff_avgs[-1]}\n\n")

                out.write(f"PYSCAL CUTOFF\n")
                out.write(f"Max: {max(pyscal_cutoff)}\n")
                out.write(f"Avg: {sum(pyscal_cutoff) / len(pyscal_cutoff)}\n\n")

                out.write(f"FREUD CUTOFF AVERAGED\n")
                out.write(f"Max: {cutoff_avg_maxs[-1]}\n")
                out.write(f"Avg: {cutoff_avg_avgs[-1]}\n\n")

                out.write(f"PYSCAL CUTOFF AVERAGED\n")
                out.write(f"Max: {max(pyscal_cutoff_avg)}\n")
                out.write(f"Avg: {sum(pyscal_cutoff_avg) / len(pyscal_cutoff_avg)}\n\n")

                out.write(f"FREUD VORONOI\n")
                out.write(f"Max: {voronoi_maxs[-1]}\n")
                out.write(f"Avg: {voronoi_avgs[-1]}\n\n")

                out.write(f"PYSCAL VORONOI\n")
                out.write(f"Max: {max(pyscal_voronoi)}\n")
                out.write(f"Avg: {sum(pyscal_voronoi) / len(pyscal_voronoi)}\n\n")

                out.write(f"FREUD VORONOI AVERAGED\n")
                out.write(f"Max: {voronoi_avg_maxs[-1]}\n")
                out.write(f"Avg: {voronoi_avg_avgs[-1]}\n\n")

                out.write(f"PYSCAL VORONOI AVERAGED\n")
                out.write(f"Max: {max(avg_pyscal_voronoi)}\n")
                out.write(f"Avg: {sum(avg_pyscal_voronoi) / len(avg_pyscal_voronoi)}\n\n")'''


            


#plot_avgs(timesteps,lammps_q6_avgs, cutoff_avgs, cutoff_avg_avgs, voronoi_avgs, voronoi_avg_avgs)
#plot_maxs(timesteps,lammps_q6_maxs, cutoff_maxs, cutoff_avg_maxs, voronoi_maxs, voronoi_avg_maxs)
'''plot_phase_summary([cutoff_labels,cutoff_avg_labels,voronoi_labels,voronoi_avg_labels],
    ["Freud Cutoff","Freud Cutoff Averaged","Freud Voronoi","Freud Voronoi Averaged"],
    f"{config.output}/phase_summary.png",
    f"{config.output}/phase_summary.txt"
)'''
#plot_final_q6_vs_q4(final_results)