import matplotlib.pyplot as plt
import config
import numpy as np
import csv
from ovito.modifiers import ChillPlusModifier



def plot_phase_summary(methods, titles, filename, txt_file):
    fig, axes = plt.subplots(2,2,figsize=(12,10),sharex=True)
    phases = ["liquid","interfacial","ice_ic", "ice_ih"]
    colors = {"liquid": "blue","interfacial": "orange","ice_ic": "red","ice_ih": "green"}
    phase_labels = {"liquid": "Liquid","interfacial": "Interfacial","ice_ic": "Ice Ic","ice_ih": "Ice Ih"}
    axes = axes.flatten()

    with open(txt_file, 'w') as f:
        f.write('q6 ranges\n\n')


    for ax, phase_data, title in zip(axes, methods, titles):
        with open(txt_file,'a') as f:
                f.write(f"{title}\n")
                f.write(f"{'=' * 20}\n\n")
        for y, phase in enumerate(phases):
        
            values = phase_data[phase]
            if len(values) == 0:
                continue

            minimum = np.min(values)
            maximum = np.max(values)
            low = np.percentile(values, 5)
            high = np.percentile(values, 95)
            mean = np.mean(values)
            color = colors[phase]

            with open(txt_file,'a') as f:
                f.write(f"Phase: {phase}\n")
                f.write(f"minimum: {minimum}\n")
                f.write(f"maximum: {maximum}\n")
                f.write(f"5th percentile:{low}\n")
                f.write(f"95th percentile: {high}\n")
                f.write(f"Mean: {mean}\n\n")

            ax.hlines(y,minimum,maximum,color=color, linewidth=1.5)
            ax.hlines(y,low,high, color=color,linewidth=8)
            ax.scatter(mean,y,color="black", s=35, zorder=5)
        ax.set_title(title)
        ax.set_yticks(range(len(phases)))
        ax.set_yticklabels([f"{phase_labels[p]}\n(n={len(phase_data[p])})"for p in phases])
        ax.grid(axis="x", alpha=0.3)
    
    all_values = []
    for method in methods:
        for phase in phases:
            all_values.extend(method[phase])

    xmin = min(all_values)
    xmax = max(all_values)

    for ax in axes:
        ax.set_xlim(xmin, xmax)
    
    fig.supxlabel("q6 Value")
    fig.supylabel("Phase")
    plt.tight_layout()
    plt.savefig(filename)


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
    phase_colors = {
    "liquid": "blue",
    "ice_ih": "red",
    "ice_ic": "green",
    "interfacial": "gold",
    "hydrate": "purple",
    "interfacial_hydrate": "brown"
    }

    phase_names = {
    "liquid": "Liquid",
    "ice_ih": "Ice Ih",
    "ice_ic": "Ice Ic",
    "interfacial": "Interfacial Ice",
    "hydrate": "Hydrate",
    "interfacial_hydrate": "Interfacial Hydrate"}

    phase_types = {
        "liquid": ChillPlusModifier.Type.OTHER,
        "ice_ih": ChillPlusModifier.Type.HEXAGONAL_ICE,
        "ice_ic": ChillPlusModifier.Type.CUBIC_ICE,
        "interfacial": ChillPlusModifier.Type.INTERFACIAL_ICE,
        "hydrate": ChillPlusModifier.Type.HYDRATE,
        "interfacial_hydrate": ChillPlusModifier.Type.INTERFACIAL_HYDRATE
    }
    fig, axs = plt.subplots(2, 2,figsize=(12, 10),sharex=True,sharey=True)

    methods = ["Cutoff","Cutoff Averaged","Voronoi","Voronoi Averaged"]
    axs = axs.flatten()
    labels = final_results["labels"]
    for ax, method in zip(axs, methods):
        q4 = final_results[method]["q4"]
        q6 = final_results[method]["q6"]
        for phase, phase_label in phase_types.items():
            mask = labels == phase_label

            ax.scatter(q6[mask], q4[mask], s=4, alpha=0.3, color=phase_colors[phase], label=phase_names[phase])
            ax.set_title(method)
    fig.supxlabel("q6", y=0.06)
    fig.supylabel("q4")

    handles, legend_labels = axs[0].get_legend_handles_labels()
    fig.legend(handles,legend_labels,loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=3, fontsize=11, markerscale=3)


    plt.tight_layout(rect=[0.05, 0.12, 1, 1])
    plt.savefig(f"{config.output}/q4_vs_q6.png",  bbox_inches="tight")
    plt.close()

def plot_particle_q4_q6(csv_file, output_file):
    timesteps = []
    q4_freud = []
    q4_pyscal = []
    q6_freud = []
    q6_pyscal = []

    with open(csv_file, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:
            timesteps.append(float(row["timestep"]))

            q4_freud.append(float(row["q4_freud"]))
            q4_pyscal.append(float(row["q4_pyscal"]))

            q6_freud.append(float(row["q6_freud"]))
            q6_pyscal.append(float(row["q6_pyscal"]))
    nanoseconds = [(t * 5) / 1e6 for t in timesteps]
    fig, axes = plt.subplots(1,2,figsize=(12, 5))
    axes[0].plot(nanoseconds,q6_freud,label="Freud",color="blue",linewidth=2)
    axes[0].plot(nanoseconds,q6_pyscal,label="Pyscal",color="orange",linewidth=2)
    axes[0].set_xlabel("Nanoseconds")
    axes[0].set_ylabel("q6")
    axes[0].set_title("q6 vs Time (ns)")
    axes[0].legend()

    axes[1].plot(nanoseconds,q4_freud,label="Freud",color="blue",linewidth=2)
    axes[1].plot(nanoseconds,q4_pyscal,label="Pyscal",color="orange",linewidth=2)
    axes[1].set_xlabel("Nanoseconds")
    axes[1].set_ylabel("q4")
    axes[1].set_title("q4 vs. Time (ns)")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(output_file,dpi=300,bbox_inches="tight")
    plt.close()
