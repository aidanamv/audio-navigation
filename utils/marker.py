import numpy as np
import time
import os


def save_markers(markers : list, filename):    
    file_path = os.path.join('data-tracking', filename)
    with open(file_path, mode='w') as f:
        for m in markers:
            output = str(m._identifier) + ','
            output += str(m._timestamp) + ','
            output += ','.join(str(i) for i in m._position) + ','
            output += ','.join(str(i) for row in m._rotation for i in row) + '\n'
            f.write(output)
        f.close()

def load_markers(path) -> list:
    with open(path, mode='r') as f:
        markers = []
        for line in f:
            values = line.strip().split(',')
            assert len(values) == 14
            idx = int(values[0])
            tmp = float(values[1])
            position = np.asarray(values[2:5])
            rotation = np.asarray(values[5:]).reshape(3,3)
            markers.append(Marker(idx, tmp, position, rotation))
        f.close()
    # sort by timestamp
    markers.sort(key=lambda x : x._timestamp)

    # bundle markers with the same timestamp
    result = {}
    for m in markers:
        if m._timestamp in result.keys():
            result[m._timestamp].append(m)
        else:
            result[m._timestamp] = [m]
    return [m for m in result.values()]

class Marker:
    """
    A atracsys.ftk.MarkerData abstraction for tracking position and rotation of markers
    """

    def __init__(self, *args):
        # constructor [ftk_marker]
        if len(args) == 1:
            self._position = np.asarray(args[0].position)
            self._rotation = np.asarray(args[0].rotation)
            self._identifier = args[0].geometry_id
            self._timestamp = time.time()
        # constructor [ftk_marker, timestamp]
        elif len(args) == 2:
            self._position = np.asarray(args[0].position)
            self._rotation = np.asarray(args[0].rotation)
            self._identifier = args[0].geometry_id
            self._timestamp = args[1]
        # constructor [idx, tmp, translation, rotation]
        elif len(args) == 4:
            self._identifier = int(args[0])
            self._timestamp = float(args[1])
            self._position = np.asarray(args[2])
            self._rotation = np.asarray(args[3])
        else:
            raise NotImplementedError        

    def get_pose(self):
        """

        :return: a 4x4 affine transformation matrix as pose
        """
        transform = np.eye(4, dtype=float)
        transform[:3, :3] = self._rotation
        transform[:3, 3] = self._position
        return transform

    def __repr__(self):
        return f'tmp: {self._timestamp}, idx: {self._identifier}, post: {self._position}, rot: {self._rotation}'