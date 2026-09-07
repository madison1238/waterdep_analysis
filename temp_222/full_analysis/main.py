import functions
from plot import * 
import csv
import os


max_n = 40
min_n = 5
sim_dirs = 300
sim_files = [f"../sims/sim_{i+1}/summary/ice_clusters.csv"for i in range(sim_dirs)]


all_results = []

for filename in sim_files:
    if not os.path.exists(filename):
        print(f"File: {filename} not found :(", flush=True)
        continue
    print(f"processing {filename}", flush=True)
    results = functions.process_excursion_simulation(filename,min_n,max_n)
    all_results.append(results)


averaged_results = {}
for n in range(min_n, max_n + 1):
    averaged_results[n] = []
    for block in range(4):
        max_values = []
        min_values = []
        for sim_results in all_results:
            value = sim_results[n][block]
            if value is not None:
                average_max, average_min = value
                max_values.append(average_max)
                min_values.append(average_min)
        if len(max_values) > 0:
            average_max = sum(max_values) / len(max_values)
            average_min = sum(min_values) / len(min_values)
            averaged_results[n].append(
                (average_max, average_min)
            )
        else:
            averaged_results[n].append(None)



plt.figure(figsize=(10, 6))

colors = ['blue', 'green', 'yellow', 'red']
markers = ["o", "s", "^", "D"]
line_styles = ["-", "--", "--", "--"]
labels = ["Block 1 (1-4)","Block 2 (5-8)","Block 3 (9-12)","Block 4 (13-16)"]
for block in range(4):
    x = []
    max_y = []
    min_y = []

    for n in range(min_n, max_n + 1):
        value = averaged_results[n][block]
        if value is not None:
            average_max, average_min = value
            x.append(n)
            max_y.append(average_max)
            min_y.append(average_min)

    plt.plot(
        x,
        max_y,
        marker=markers[block],
        linestyle=line_styles[block],
        label=labels[block],
        color = colors[block]
    )

    plt.plot(
        x,
        min_y,
        marker=markers[block],
        linestyle=line_styles[block],
        #label=labels[block],
        color = colors[block]
    )

x_gray = []
y_gray = []

for n in range(min_n, max_n + 1):
    block_values = averaged_results[n]
    all_values = []
    for value in block_values:
        if value is not None:
            average_max, average_min = value
            all_values.append(average_max)
            all_values.append(average_min)
    if len(all_values) > 0:
        overall_average = sum(all_values) / len(all_values)
        x_gray.append(n)
        y_gray.append(overall_average)
# Plot gray average line
plt.plot(
    x_gray,
    y_gray,
    color="gray",
    linestyle="--",
    linewidth=2,
    alpha=0.5,
    label="Average"
)

plt.xlabel("n")
plt.ylabel(r'$⟨n{e}⟩$')
plt.legend()
plt.tight_layout()
plt.savefig("../summary/blocks_excursion_extremes.png")