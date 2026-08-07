import matplotlib.pyplot as plt
import config
import os
from ovito.modifiers import ChillPlusModifier

def plot_cluster_q6_history(cluster_history):
    os.makedirs(f"{config.output}/4_largest_q6/", exist_ok=True)

    phase_colors = {
    "Liquid": "blue",
    "Interfacial": "yellow",
    "Ice Ih": "red",
    "Ice Ic": "green"}


    for cid, data in cluster_history.items():
        fig, axes = plt.subplots(2, 2,figsize=(12, 8),sharex=True,sharey=True)
        axes = axes.flatten()
        methods = [
            ("Cutoff", data["cutoff"]),
            ("Cutoff Averaged", data["cutoff_avg"]),
            ("Voronoi", data["voronoi"]),
            ("Voronoi Averaged", data["voronoi_avg"])
        ]
        all_q6 = (
        data["cutoff"] +
        data["cutoff_avg"] +
        data["voronoi"] +
        data["voronoi_avg"])

        ymin = min(all_q6)
        ymax = max(all_q6)


        for ax, (title, q6) in zip(axes, methods):
            used_labels = set()
            ax.plot(data["time"],q6,color="0.7",linewidth=1.5,zorder=1)
            for t, value, phase in zip(data["time"], q6, data["phase"]):

                if phase not in used_labels:
                    ax.scatter(t,value,color=phase_colors[phase],s=35, edgecolors="black",linewidths=0.4,label=phase)
                    used_labels.add(phase)
                else:
                    ax.scatter(t,value,color=phase_colors[phase],s=35,edgecolors="black",linewidths=0.4)
            
                
            ax.legend()
            ax.set_title(title)
            ax.set_xlabel("Time (fs)")
            ax.set_ylabel("Q6")
            ax.set_ylim(ymin, ymax)
            ax.grid(alpha=0.3)

        fig.suptitle(f"Cluster {cid} (Max Size = {max(data['size'])})",fontsize=16)
        plt.tight_layout()
        plt.savefig(f"{config.output}/4_largest_q6/cluster_{cid}.png")
        plt.close(fig)

def plot_q6_largest_cluster_freud_pyscal(size, freud_q6, pyscal_q6):
    fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)
    ax[0].scatter(size,freud_q6,s=20)
    ax[0].set_title("Freud")
    ax[0].set_xlabel("Largest Cluster Size")
    ax[0].set_ylabel("Q6")
    ax[0].grid(alpha=0.3)

    ax[1].set_title("Pyscal")
    ax[1].set_xlabel("Largest Cluster Size")
    ax[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{config.output}/pyscal_freud_q6_vs_lg_cluster")
    plt.close()

def plot_avgs(timesteps, lammps, cutoff,cutoff_avg, voronoi, voronoi_avg):
    femto = [t * 5 for t in timesteps]
    plt.figure(figsize=(8,5))
    
    plt.plot(femto, lammps, label='Lammps', marker="o", color='red')
    plt.plot(femto, cutoff, label='Cutoff (3.5Å)', marker="s", color='orange')
    plt.plot(femto, cutoff_avg, label='Averaged Cutoff (3.5Å)', marker="v", color='green')
    plt.plot(femto, voronoi, label='Voronoi', marker="D", color='blue')
    plt.plot(femto, voronoi_avg, label='Averaged Voronoi', marker="P", color='purple')

    plt.xlabel("Time (fs)")
    plt.ylabel("Average Q6")
    plt.title("Average Q6 Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{config.output}/average_q6.png')
    plt.close()


def plot_maxs(timesteps, lammps, cutoff,cutoff_avg, voronoi, voronoi_avg):
    femto = [t * 5 for t in timesteps]
    plt.figure(figsize=(8,5))
    
    plt.plot(femto, lammps, label='Lammps', marker="o", color='red')
    plt.plot(femto, cutoff, label='Cutoff (3.5Å)', marker="s", color='orange')
    plt.plot(femto, cutoff_avg, label='Averaged Cutoff (3.5Å)', marker="v", color='green')
    plt.plot(femto, voronoi, label='Voronoi', marker="D", color='blue')
    plt.plot(femto, voronoi_avg, label='Averaged Voronoi', marker="P", color='purple')

    plt.xlabel("Time (fs)")
    plt.ylabel("Maximum Q6")
    plt.title("Maximum Q6 Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{config.output}/max_q6.png')
    plt.close()



def plot_final_q6_vs_q4(final_results):
    fig, axs = plt.subplots(2, 2,figsize=(12, 10),sharex=True,sharey=True)
    methods = ["Cutoff","Cutoff Averaged","Voronoi","Voronoi Averaged"]
    axs = axs.flatten()
    for ax, method in zip(axs, methods):
        q4 = final_results[method]["q4"]
        q6 = final_results[method]["q6"]
        ax.scatter(q6,q4,s=4,alpha=0.2,color="blue")
        ax.set_title(method)
    fig.supxlabel("q6")
    fig.supylabel("$q4")
    plt.tight_layout()
    plt.savefig(f"{config.output}/q4_vs_q6.png",)
    plt.close()
