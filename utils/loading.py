import utils.qt_geoms as qgeoms

def load_mesh(path : str):
    from stl import mesh
    from pyqtgraph.opengl.MeshData import MeshData

    m = mesh.Mesh.from_file(path)
    _, cog, _ = m.get_mass_properties()
    return MeshData(vertexes=m.vectors), cog

def load_items(config):
    for m in config.geometries.values():
        if not hasattr(m, 'item'):
            m.item = qgeoms.geom_from_dict(m)            

def load_marker_from_config_o3d(config):
    import open3d as o3d
    import numpy as np
    import os
    mesh_dir = "data-stl"
    markers = {}
    for m in config.markers:
        markers[m.id] = {
            "id" : m.id,
            "name" : m.name,
            "mesh" : o3d.io.read_triangle_mesh(os.path.join(mesh_dir, m.stl)),
            "trans" : np.asarray(m.trans).reshape(4,4) if m.trans else np.eye(4)
        }
    return markers

def update_dictionary_with_default(config, default):
    for key, values in config.items():
        if key in default: # geometries
            for obj in values: # L1
                for k, attr in default[key].items(): # marker : 300
                    if not hasattr(config[key][obj], k):
                        config[key][obj][k] = attr

def loading_data_into_geometries(config):
    import numpy as np
    import os
    data_dir = 'data-stl'
    for k, m in config.geometries.items():
        if m.type == 'mesh' and type(m.data) == str:
            m.data, center = load_mesh(os.path.join(data_dir, m.data))
            m.center = center
        elif m.type == 'line':
            m.data = np.asarray(m.data).reshape(1,-1)
        elif m.type == 'point':
            m.data = np.asarray(m.data).reshape(1,-3)

        m.trans = np.asarray(m.trans).reshape(4,4) if type(m.trans) == list else np.eye(4)

def load_config_from_yaml(path):
    import yaml
    from easydict import EasyDict
    c = yaml.load(open(path), Loader=yaml.FullLoader)
    config = EasyDict(c)
    return config

def add_posterior_copies(config):
    # vertebrae
    cp = config.geometries['L'].copy()
    cp['color'] = (1.0,1.0,1.0,.05)
    config.geometries['L_'] = cp