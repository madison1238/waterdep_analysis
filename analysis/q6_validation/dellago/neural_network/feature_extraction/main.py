from functions import (largest_cluster_info,
                       largest_q6_q4_tetra,
                       largest_vol_cn) 



def main():
   dump = ''
   frame = 0

   largest_cluster_size, ids_in_largest, ic, ih, ic_fraction, ih_fraction = largest_cluster_info(dump,frame)
   cluster_q6, cluster_q4, cluster_tetra, = largest_q6_q4_tetra(dump, frame, ids_in_largest)
   cluster_cn, std_cn, cluster_v_vol, std_v_vol =  largest_vol_cn(dump, frame, ids_in_largest)
   

   

