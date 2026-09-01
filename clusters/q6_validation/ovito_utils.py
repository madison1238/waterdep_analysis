from ovito.io import import_file
from ovito.modifiers import ChillPlusModifier
import numpy as np
import freud


def load_frame(filename, frame=0, use_chill=False):
    pipeline = import_file(filename)
    if use_chill:
        pipeline.modifiers.append(ChillPlusModifier())

    data = pipeline.compute(frame)

    timestep = data.attributes["Timestep"]
    print(f"Frame {frame} → Timestep {timestep}",flush=True)

    ids = np.asarray(data.particles["Particle Identifier"])
    positions = np.asarray(data.particles["Position"])

    cell = data.cell

    box = freud.box.Box(
        Lx=cell[0,0],
        Ly=cell[1,1],
        Lz=cell[2,2]
    )

    if use_chill:
        labels = np.asarray(data.particles["Structure Type"])
        return ids, positions, box, labels

    return ids, positions, box