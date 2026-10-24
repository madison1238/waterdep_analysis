from functions import (largest_cluster_info,
                       largest_q6_q4_tetra) 



def main():
   dump = ''
   frame = 0

   largest_cluster_size, ids_in_largest, all_ids, ic, ih, ic_fraction, ih_fraction = largest_cluster_info(dump,frame)
   cluster_q6, cluster_q4, cluster_tetra, = largest_q6_q4_tetra(dump, frame, ids_in_largest, all_ids)
   
   

