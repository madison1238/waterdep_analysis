import summary_functions as func
import os
import csv

os.makedirs('../summary', exist_ok=True) 
os.makedirs('../summary/3_cluster_tracking', exist_ok=True)


results = func.analyze_clusters('../dump.cluster_q6.lammpstrj')
timesteps = results["timesteps"]
largest_clusters = results["largest_clusters"]
average_clusters = results["average_clusters"]
cluster_distribution = results["cluster_distribution"]
final_cluster_sizes = results["final_cluster_sizes"]
csv_rows = results["csv_rows"]
largest_cluster_q6s = results['largest_cluster_q6s']
average_clusters_q6 = results['average_clusters_q6']

func.plot_average_q6_vs_timestep(average_clusters_q6, '../summary/average_cluster_q6_vs_time.png')
func.plot_largest_cluster_q6_change(timesteps, largest_cluster_q6s, '../summary/largest_cluster_q6_vs_time.png')

all_timesteps = list(
    cluster_distribution.keys()
)

selected_timesteps = [
    all_timesteps[len(all_timesteps)//4],
    all_timesteps[len(all_timesteps)//2],
    all_timesteps[(len(all_timesteps)//4)*3],
    all_timesteps[-1]
]

func.plot_cluster_dist_hist(
    cluster_distribution,
    selected_timesteps
)


func.plot_cluster_dist_loglog(
    cluster_distribution,
    selected_timesteps
)


selected_q6_distribution = func.get_selected_q6_dist(selected_timesteps, '../dump.cluster_q6.lammpstrj')


func.plot_q6_dist_hist(
    selected_q6_distribution,
    selected_timesteps
)


func.plot_largest(
    timesteps,
    largest_clusters
)

func.plot_average_size(
    timesteps,
    average_clusters
)

with open(
    '../summary/cluster_summary.csv',
    'w'
) as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        'Timestep',
        'Largest Cluster ID',
        'Largest Cluster Size',
        'Average Cluster Size'
    ])

    writer.writerows(csv_rows)

sorted_final_clusters = sorted(
    final_cluster_sizes.items(),
    key=lambda x: x[1],
    reverse=True
)

with open(
    '../summary/largest_ten_cluster.txt',
    'w'
) as f:

    f.write(
        'Top 10 Largest Clusters '
        'at Final Timestep\n'
    )
    f.write('='*30 + '\n\n')

    for cluster_id, size in sorted_final_clusters[:10]:
        f.write(
            f"Cluster {cluster_id}: "
            f"{size} particles\n"
        )

ranking = 1
for cluster_id, size in sorted_final_clusters[:3]:
    sizes, timesteps = func.track_cluster_growth(
        '../dump.cluster_q6.lammpstrj',
        target_cluster_id=cluster_id
    )

    func.plot_cluster_growth(
        timesteps,
        sizes,
        f'../summary/3_cluster_tracking/{ranking}_largest.png',
        ranking
    )
    ranking += 1