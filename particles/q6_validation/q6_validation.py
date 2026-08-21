from ovito_utils import load_frame
from freud_methods import *
from pyscal_methods import *
from q6_functions import * 
from ovito.modifiers import ChillPlusModifier
from plots import *
from testing import *
import config
import os
import csv



target_frame = 1010
target_id = 4093

ids, positions, box, labels = load_frame(config.dump,1010,True)
compare_neighbors(positions,box,ids,target_id=4093,cutoff=3.5 )


