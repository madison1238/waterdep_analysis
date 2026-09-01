import functions
from plot import * 
import csv
import os


max_n = 12
min_n = 3
sim_dirs = 5
sim_files = [f"../sim_{i+1}/summary/ice_clusters.csv"for i in range(sim_dirs)]


all_results = []

for filename in sim_files:
    if not os.path.exists(filename):
        print(f"File: {filename} not found :(")
        continue
    print(f"processing {filename}", flush=True)
    results = functions.process_simulation(filename,min_n,max_n)
    all_results.append(results)


averaged_results = {}
for n in range(min_n, max_n + 1):
    averaged_results[n] = []
    for block in range(4):
        values = []
        for sim_results in all_results:
            value = sim_results[n][block]
            if value is not None:
                values.append(value)
        if len(values) > 0:
            average = sum(values) / len(values)
            averaged_results[n].append(average)
        else:
            averaged_results[n].append(None)




print("\nMean recurrence times:")
print("n\tBlock 1\tBlock 2\tBlock 3\tBlock 4")
for n in range(min_n, max_n + 1):
    values = averaged_results[n]
    if any(value is not None for value in values):

        print(
            n,
            "\t",
            values[0],
            "\t",
            values[1],
            "\t",
            values[2],
            "\t",
            values[3]
        )

plt.figure(figsize=(10, 6))

colors = ['blue', 'green', 'yellow', 'red']
markers = ["o", "s", "^", "D"]
line_styles = ["-", "--", "--", "--"]
labels = ["Block 1 (1-4)","Block 2 (5-8)","Block 3 (9-12)","Block 4 (13-16)"]
for block in range(4):
    x = []
    y = []
    for n in range(min_n, max_n + 1):
        value = averaged_results[n][block]
        if value is not None:
            x.append(n)
            y.append(value)

    plt.plot(
        x,
        y,
        marker=markers[block],
        linestyle=line_styles[block],
        label=labels[block],
        color = colors[block]
    )


plt.xlabel("n")
plt.ylabel("Mean Recurrence Time(ps)")
plt.legend()
plt.tight_layout()
plt.savefig("../summary/blocks.png")
