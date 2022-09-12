from ctypes import ArgumentError
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl

def mesh_item_from_data(geom, visible = False):
    kwargs = {
        'meshdata' : geom.data,
        'smooth' : True,
        #'drawEdges' : False,
        'color' : tuple(geom.color),
        'shader' : 'balloon',
        'glOptions' : 'translucent'
    }
    item = gl.GLMeshItem(**kwargs)
    item.setVisible(visible)
    return item

def line_item_from_data(geom, visible = False):
    start = geom.data[0, :3]
    mid = geom.data[0, 3:6]
    if geom.data.shape[1] == 7:
        dir = (mid - start)/np.linalg.norm(mid - start)
        end = start + dir * geom.data[0, 6]
    elif geom.data.shape[1] == 6:
        end = mid
    else:
        raise ArgumentError

    kwargs = {
        'pos' : np.stack([start, end]),
        'color' : tuple(geom.color),
        'width' : 3,
        'antialias' : True,
        'glOptions' : 'additive'
    }
    item = gl.GLLinePlotItem(**kwargs)
    item.setVisible(visible)
    return item

def point_item_from_data(geom, visible = False):
    kwargs = {
        'pos' : geom.data,
        'color' : tuple(geom.color), # RGBA
        'size' : 10,
        'pxMode' : True,
        'glOptions' : 'additive'
    }
    item = gl.GLScatterPlotItem(**kwargs)
    item.setVisible(visible)
    return item

def geom_from_dict(geom):
    if geom.type == 'mesh':
        return mesh_item_from_data(geom)
    elif geom.type == 'line':
        return line_item_from_data(geom)
    elif geom.type == 'point':
        return point_item_from_data(geom)
    else:
        raise NotImplementedError