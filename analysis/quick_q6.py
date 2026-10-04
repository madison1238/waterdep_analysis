# script for the freeze simulation to get a few visuals of q6 in sim
import os
import numpy as np
import matplotlib.pyplot as plt



def plot_avg_q6(avgs, timesteps, output):
    femto = [t * 5 for t in timesteps]
    plt.figure(figsize=(8,5))

    plt.plot(femto, avgs)

    plt.xlabel("Time (fs)")
    plt.ylabel("Average Q6")
    plt.title("Average Q6 vs Time")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

def plot_max_q6(maxs, timesteps, output):
    femto = [t * 5 for t in timesteps]
    plt.figure(figsize=(8,5))

    plt.plot(femto, maxs)

    plt.xlabel("Time (fs)")
    plt.ylabel("Max Q6")
    plt.title("Max Q6 vs Time")
    plt.tight_layout()
    plt.savefig(output)
    plt.close()

def plot_final_q6_histogram(q6_values, output):

    plt.figure(figsize=(8,5))

    plt.hist(
        q6_values,bins=40,)

    plt.xlabel("Q6")
    plt.ylabel("Number of Particles")
    plt.title("Q6 Distribution at Final Timestep")

    plt.tight_layout()
    plt.savefig(output)
    plt.close()



dump_file = "dump.mWC1.lammpstrj"
text_file = "summary/q6_summary.txt"
with open(text_file, 'w') as out:
    out.write("Q6 SUMMARY\n")
    out.write(f"{'=' * 20}\n\n")



timesteps = []
avg_q6 = []
max_q6 = []
final_q6s = []

os.makedirs('summary', exist_ok=True)


with open(dump_file, 'r') as f:
    while True:
        line = f.readline()

        if not line:
            break
        if line.strip() == "ITEM: TIMESTEP":
            timestep = int(f.readline().strip())
            timesteps.append(timestep)
        
            f.readline()
            num_atoms = int(float(f.readline().strip()))

            f.readline()
            f.readline()
            f.readline()
            f.readline()
            f.readline()

            final_q6s = []
            q6_for_timesteps = []

            for i in range(num_atoms):
                line = f.readline()
                q6 = float(line.split()[5])
                q6_for_timesteps.append(q6)
            final_q6s = q6_for_timesteps.copy()


            avg_q6_for_timestep = sum(q6_for_timesteps) / len(q6_for_timesteps)
            avg_q6.append(avg_q6_for_timestep)
            max_q6_for_timestep = max(q6_for_timesteps)
            max_q6.append(max_q6_for_timestep)

            with open(text_file, 'a') as out:
                out.write(f"Timestep: {timestep}\n")
                out.write(f"Avg q6: {avg_q6_for_timestep:.4f}\n")
                out.write(f"Max q6: {max_q6_for_timestep:.4f}\n")
                out.write(f"{'=' * 10}\n\n")



plot_avg_q6(avg_q6, timesteps, 'summary/avg_q6_vs_time.png')
plot_max_q6(max_q6, timesteps, 'summary/max_q6_vs_time.png')
plot_final_q6_histogram(final_q6s, 'summary/final_q6_hist.png')


