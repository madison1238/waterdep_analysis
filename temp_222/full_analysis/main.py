import functions
from plot import * 
import csv
import os


import functions
from plot import * 
import csv
import os


max_n = 40
min_n = 5
sim_dirs = 5
sim_files = [f"../sim_{i+1}/summary/ice_clusters.csv"for i in range(sim_dirs)]


all_results = []

for filename in sim_files:
    if not os.path.exists(filename):
        print(f"File: {filename} not found :(")
        continue
    print(f"processing {filename}", flush=True)
    results = functions.process_simulation_parameters(filename,min_n,max_n)
    all_results.append(results)


averaged_q6 = {}
averaged_q4 = {}
for n in range(min_n, max_n + 1):
    averaged_q6[n] = []
    averaged_q4[n] = []
    for block in range(4):
        q6_values = []
        q4_values = []
        for sim_results in all_results:
            q6_value = sim_results[n]["q6"][block]
            q4_value = sim_results[n]["q4"][block]
            if q6_value is not None:
                q6_values.append(q6_value)
            if q4_value is not None:
                q4_values.append(q4_value)

        if len(q6_values) > 0:
            average_q6 = sum(q6_values) / len(q6_values)
            averaged_q6[n].append(average_q6)
        else:
            averaged_q6[n].append(None)
        if len(q4_values) > 0:
            average_q4 = sum(q4_values) / len(q4_values)
            averaged_q4[n].append(average_q4)
        else:
            averaged_q4[n].append(None)




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

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
ax = axes[0]

colors = ['blue', 'green', 'yellow', 'red']
markers = ["o", "s", "^", "D"]
line_styles = ["-", "--", "--", "--"]
labels = ["Block 1 (1-4)","Block 2 (5-8)","Block 3 (9-12)","Block 4 (13-16)"]


for block in range(4):
    x = []
    y = []
    for n in range(min_n, max_n + 1):
        value = averaged_q6[n][block]
        if value is not None:
            x.append(n)
            y.append(value)

    ax.plot(
        x,
        y,
        marker=markers[block],
        linestyle=line_styles[block],
        label=labels[block],
        color = colors[block]
    )


ax.set_xlabel("n")
ax.set_ylabel("Q6")
ax.set_title("(a)")

ax = axes[1]

for block in range(4):
    x = []
    y = []
    for n in range(min_n, max_n + 1):
        value = averaged_q4[n][block]
        if value is not None:
            x.append(n)
            y.append(value)
    ax.plot(
        x, 
        y,
        marker=markers[block],
        linestyle=line_styles[block],
        color=colors[block],
        label=labels[block]
    )

ax.set_xlabel("n")
ax.set_ylabel("Q4")
ax.set_title("(b)")

handles, labels_legend = axes[0].get_legend_handles_labels()

fig.legend(
    handles,
    labels_legend,
    loc="lower center",
    ncol=4
)
plt.tight_layout()
plt.savefig("../summary/q6_q4_blocks.png", dpi=300)
