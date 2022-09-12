import numpy as np
from pyqtgraph.opengl.items.GLLinePlotItem import GLLinePlotItem
from pyqtgraph.opengl.items.GLScatterPlotItem import GLScatterPlotItem

def distance_2d(pt1 : GLScatterPlotItem, pt2 : GLScatterPlotItem):
    p1 = pt1.mapToView(pt1.pos.T)
    p2 = pt2.mapToView(pt2.pos.T)
    return np.abs(p2 - p1)

def distance_3d(pt1 : GLScatterPlotItem, pt2 : GLScatterPlotItem):
    return np.linalg.norm(distance_2d(pt1, pt2))

def distance_to_trajectory(pt1 : GLScatterPlotItem, traj : GLLinePlotItem):
    # https://onlinemschool.com/math/library/analytic_geometry/p_line/
    p3 = pt1.mapToView(pt1.pos.T)[:, 0]
    line = traj.mapToView(traj.pos.T)
    p1 = line[:, 0]
    p2 = line[:, 1]
    return np.linalg.norm(np.cross(p3-p1, p2-p1))/np.linalg.norm(p2-p1)

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between_vectors(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    cos_alpha = np.dot(v1_u, v2_u)
    if cos_alpha == 0.:
        return 0.0
    else:
        degrees = np.rad2deg(np.arccos(cos_alpha))
        return min(180 - degrees, degrees)

def angle_points_to_trajectory(traj : GLLinePlotItem, 
    orig : GLScatterPlotItem,
    tip : GLScatterPlotItem):

    l1 = traj.mapToView(traj.pos.T)
    v1 = l1[:, 1] - l1[:, 0]

    l2_p1 = orig.mapToView(orig.pos.T)[:, 0]
    l2_p2 = tip.mapToView(tip.pos.T)[:, 0]
    v2 = l2_p2 - l2_p1

    return angle_between_vectors(v1, v2)
    
def angle_trajectory_to_trajectory(traj : GLLinePlotItem, 
    targ : GLScatterPlotItem):

    l1 = traj.mapToView(traj.pos.T)
    v1 = l1[:, 1] - l1[:, 0]

    l2 = targ.mapToView(targ.pos.T)
    v2 = l2[:, 1] - l2[:, 0]

    return angle_between_vectors(v1, v2)

def stats_from_dict_numbers(stat, args):
    return globals()[stat.type](*args)

def stats_from_dict(name, stat, args):
    res = stats_from_dict_numbers(stat, args)
    return format_output(name, res)

def format_output(name, result : np.ndarray):
    values = [round(e.item(), 2) for e in result.flatten()]
    output = name + '\n'
    if len(values) == 1:
        return output + str(values[0])
    elif len(values) == 3:
        output += 'X\t' + str(values[0]) + '\n'
        output += 'Y\t' + str(values[1]) + '\n'
        output += 'Z\t' + str(values[2])
        return output  
    else:
        raise NotImplementedError

