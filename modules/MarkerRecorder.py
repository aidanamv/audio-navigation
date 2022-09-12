from utils.marker import *

class MarkerRecorder:
    def __init__(self):
        self.all_markers = []
        self.recording = False
    
    def update_markers(self, makers : list):
        for m in makers:
            if not isinstance(m, Marker):
                m = Marker(m)
            self.all_markers.append(m)
    
    def clear(self):
        self.all_markers.clear()

    def save(self, identifier : str, screw_tip : bool):
        name = 'screw_tip' if screw_tip else 'entry_point'
        save_markers(self.all_markers, identifier + '-' + name + '-' + str(time.time()).split('.')[0] + '.txt')
        self.clear()