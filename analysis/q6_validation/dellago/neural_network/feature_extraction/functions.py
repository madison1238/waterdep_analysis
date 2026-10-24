from ovito.io import import_file
from ovito.modifiers import (
    ChillPlusModifier,
    ExpressionSelectionModifier,
    ClusterAnalysisModifier,
    VoronoiAnalysisModifier
)
import config
import pyscal
import freud
import numpy as np
import csv
import os
from ase import Atoms




def largest_cluster_info(dump, frame):
    #returns largest cluster size n, num of IC IH, fraction of IC and IH, largest_cluster_radii, lambda values
    pipeline = import_file(dump)
    pipeline.modifiers.append(ChillPlusModifier())
    pipeline.modifiers.append(ExpressionSelectionModifier(expression="StructureType == 1 || StructureType == 2"))
    pipeline.modifiers.append(ClusterAnalysisModifier(cutoff=3.5,only_selected=True,sort_by_size=True, compute_gyration=True,))
    
    data = pipeline.compute(frame)
    structure_types = np.asarray(data.particles["Structure Type"])
    cluster_ids = np.asarray(data.particles["Cluster"])
    timestep = int(data.attributes["Timestep"])
   
    clusters = data.particle_systems["clusters"]
    cluster_sizes = np.asarray(clusters["Cluster Size"])
    radii = np.asarray(clusters["Radius of Gyration"])
    gyration_tensors = np.asarray(clusters["Gyration Tensor"])
    largest_cluster_id = int(clusters["Cluster Identifier"][0])
    largest_cluster_size = int(cluster_sizes[0])
    largest_cluster_radius = float(radii[0])
    largest_cluster_tensors = gyration_tensors[0]
    lambda1, lambda2, lambda3 = calculate_eigenvalues(largest_cluster_tensors)

    ids_in_largest = cluster_ids == largest_cluster_id
    ih = np.sum(structure_types[ids_in_largest] == 1)
    ic = np.sum(structure_types[ids_in_largest] == 2)
    ih_fraction = ih / largest_cluster_size
    ic_fraction = ic / largest_cluster_size


    return timestep,largest_cluster_size, ids_in_largest, ic, ih, ic_fraction, ih_fraction, largest_cluster_radius, lambda1, lambda2, lambda3


def largest_q6_q4_tetra(dump, frame, ids_in_largest):
    pipeline = import_file(dump)
    data = pipeline.compute(frame)
    positions = np.asarray(data.particles["Position"])
    cell = data.cell
    box = freud.box.Box(
            Lx=cell[0, 0],
            Ly=cell[1, 1],
            Lz=cell[2, 2]
    )
    q6 = pyscal_steinhardt(positions,box, method='cutoff',averaged=True,cutoff=3.5,param=6)
    q4 = pyscal_steinhardt(positions,box, method='cutoff',averaged=True,cutoff=3.5,param=4)
    tetra = pyscal_tetrahedrality(positions,box)

    cluster_q6 = q6[ids_in_largest]
    cluster_q4 = q4[ids_in_largest]
    cluster_tetra = tetra[ids_in_largest]

    return (
        float(np.mean(cluster_q6)),
        float(np.mean(cluster_q4)),
        float(np.mean(cluster_tetra))
    )

def largest_vol_cn(dump,frame,ids_in_largest):
    pipeline = import_file(dump)
    voro = VoronoiAnalysisModifier(relative_face_threshold=0.02)
    pipeline.modifiers.append(voro)
    data = pipeline.compute(frame)
    coordination = np.asarray(data.particles["Coordination"])
    voronoi_vol = np.asarray(data.particles['Atomic Volume'])

    cluster_cn = coordination[ids_in_largest]
    cluster_vol = voronoi_vol[ids_in_largest]

    mean_cn = np.mean(cluster_cn)
    std_cn = np.std(cluster_cn)

    mean_vol = np.mean(cluster_vol)
    std_vol = np.std(cluster_vol)

    return mean_cn, std_cn, mean_vol, std_vol

def calculate_i_j_k(lamba1, lambda2, lambda3):
    i = calculate_i_anisotropy(lamba1, lambda2, lambda3)
    j = calculate_j_acylindricity(lamba1, lambda2, lambda3)
    k = calculate_k_asphericity(lamba1, lambda2, lambda3)
    return i,j,k



def caluculate_E_1_6(largest_cluster_size, q6,k, Rg, mean_v, std_v, mean_cn, std_sn, ):
    E1 = largest_cluster_size * q6
    E2 = k / (Rg**2)
    E3 = std_v/mean_v
    E4 = std_sn/mean_cn
    E5 = (1+E3 + E4 - q6) / 3
    E6 = largest_cluster_size / (Rg**3)
    return E1,E2,E3,E4,E5,E6

def pyscal_steinhardt(positions, box, method='cutoff', averaged=False, cutoff=3.5, param=6):
    atoms = Atoms(symbols=["O"] * len(positions), positions=positions, cell=[box.Lx, box.Ly, box.Lz], pbc=True)
    if method == 'cutoff':
        pyscal.find_neighbors(atoms, method='cutoff', cutoff=cutoff)
    elif method == 'voronoi':
        pyscal.find_neighbors(atoms, method='voronoi')
    if averaged == False:
        q=pyscal.steinhardt_parameter(atoms, l=[param])[0]
    else:
        q = pyscal.steinhardt_parameter(atoms, l=[param], averaged=True)[0]
    print(
    f"Total Q6 values: {len(q)}, "
    f"NaN Q6 values: {np.isnan(q).sum()}")
    
    return q

def pyscal_tetrahedrality(positions, box, method='cutoff', cutoff=3.5):
    atoms = Atoms(symbols=["O"] * len(positions),positions=positions,cell=[box.Lx, box.Ly, box.Lz],pbc=True)
    if method == 'cutoff':
        pyscal.find_neighbors(atoms, method='cutoff', cutoff=cutoff)
    elif method == 'voronoi':
        pyscal.find_neighbors(atoms, method='voronoi')
    tetrahedrality = pyscal.angular_criteria(atoms)
    return tetrahedrality

def calculate_eigenvalues(tensors):
    xx, yy, zz, xy, xz, yz = tensors
    tensor_matrix = np.array([
        [xx, xy, xz],
        [xy, yy, yz],
        [xz, yz, zz]
    ])

    eigenvalues = np.linalg.eigvalsh(tensor_matrix)
    lambda1, lambda2, lambda3 = eigenvalues
    return lambda1, lambda2, lambda3

def calculate_i_anisotropy(l1, l2, l3):
    total = l1 + l2 + l3
    if total <= 0:
        raise ValueError("Eigenvalue sum must be positive.")
    return (3 / 2) * ((l1**2 + l2**2 + l3**2) / total**2) - (1 / 3)


def calculate_j_acylindricity(l1, l2, l3):
    return l2 - l1


def calculate_k_asphericity(l1, l2, l3):
    return l3 - (l1 + l2) / 2