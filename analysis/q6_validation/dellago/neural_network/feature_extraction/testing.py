from functions import (largest_cluster_info,
                       largest_q6_q4_tetra,
                       largest_vol_cn,
                       calculate_i_j_k,
                       caluculate_E_1_6)
import csv




def main():
   dump = '../dump.mWC2.lammpstrj'
   frame = 2015
   features_file = 'features.csv'

   timestep, largest_cluster_size, ids_in_largest, ic, ih, ic_fraction, ih_fraction,largest_cluster_radius, lambda1, lambda2, lambda3 = largest_cluster_info(dump,frame)
   cluster_q6, cluster_q4, cluster_tetra, = largest_q6_q4_tetra(dump, frame, ids_in_largest)
   cluster_cn, std_cn, cluster_v_vol, std_v_vol =  largest_vol_cn(dump, frame, ids_in_largest)
   i,j,k = calculate_i_j_k(lambda1,lambda2,lambda3)
   E1,E2,E3,E4,E5,E6= caluculate_E_1_6(largest_cluster_size, cluster_q6,k, largest_cluster_radius, cluster_v_vol, std_v_vol, cluster_cn, std_cn )

   with open(features_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
      "dump path",
      "frame",
      "timestep",
      "Largest CLuster Size (n)",
      "Q6",
      "Q4",
      "Tetrahedrality",
      "nih",
      "nic",
      "nih/n",
      "nic/n",
      'Coordination Number (CN)',
      "CN Standard Deviation",
      'Voronoi Volume',
      "Voronoi Volume Standard Deviation",
      "Radius of Gyration (Rg)",
      "lambda 1",
      "lambda 2",
      "lambda 3",
      "Anisotropy (I)",
      "Acylindricity (J)",
      "Asphericity (K)",
      "E1",
      "E2",
      "E3",
      "E4",
      "E5",
      "E6"
    ])

    writer.writerow([
      dump,
      frame,
      timestep,
      largest_cluster_size,
      cluster_q6,
      cluster_q4,
      cluster_tetra,
      ih,
      ic,
      ih_fraction,
      ic_fraction,
      cluster_cn,
      std_cn,
      cluster_v_vol,
      std_v_vol,
      largest_cluster_radius,
      lambda1,
      lambda2,
      lambda3,
      i,
      j,
      k,
      E1,
      E2,
      E3,
      E4,
      E5,
      E6,

    ])


if __name__ == "__main__":
    main()