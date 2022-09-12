from functools import partial
from tkinter.constants import W
from pyqtgraph.Qt import QtGui, QtCore, QT_LIB

def wheelEvent(w, ev):
    delta = 0
    if QT_LIB in ['PyQt4', 'PySide']:
        delta = ev.delta()
    else:
        delta = ev.angleDelta().x()
        if delta == 0:
            delta = ev.angleDelta().y()
    if (ev.modifiers() & QtCore.Qt.ControlModifier):
        w.opts['fov'] *= 0.999**delta
    else:
        w.opts['distance'] *= 0.999**delta
    w.update()

def orbit(w, azim, elev):
    """Orbits the camera around the center position. *azim* and *elev* are given in degrees."""
    if w.opts['rotationMethod'] == 'quaternion':
        q = QtGui.QQuaternion.fromEulerAngles(elev, -azim, 0) # rx-ry-rz
        q *= w.opts['rotation']
        w.opts['rotation'] = q
    else: # default euler rotation method
        w.opts['azimuth'] += azim
        w.opts['elevation'] += elev
    w.update()

def mousePressEvent(w, ev):
    w.mousePos = ev.pos()

def mouseMoveEvent(w, ev):
    diff = ev.pos() - w.mousePos
    w.mousePos = ev.pos()
    
    if ev.buttons() == QtCore.Qt.LeftButton:
        if (ev.modifiers() & QtCore.Qt.ShiftModifier):
            q = QtGui.QQuaternion.fromEulerAngles(0, 0, diff.y())
            q *= w.opts['rotation']
            w.opts['rotation'] = q
            w.update()
        else:
            orbit(w, -diff.x(), diff.y())

class Synchronizer:
    def __init__(self, widgets):
        self.widgets = widgets
        self.events = {}
        self.active = False
    
    def toggleActive(self):
        for name, ev in self.events.items():
            for w, o in zip(self.widgets, ev['alone']):
                if not self.active:
                    setattr(w, name, ev['synched'])
                else:
                    setattr(w, name, o)
        # toggle state
        self.active = not self.active
        print('Changed synchronization to {0}'.format('True' if self.active else 'False'))

    def mouseMoveEvents(self, ev):
        for w in self.widgets:
            mouseMoveEvent(w, ev)
    
    def mousePressEvents(self, ev):
        for w in self.widgets:
            mousePressEvent(w, ev)
    
    def wheelEvents(self, ev):
        for w in self.widgets:
            wheelEvent(w, ev)

    def add_event(self, name : str, single_event, synched_events):
        old = [partial(single_event, w) for w in self.widgets]
        self.events[name] = { 'alone' : old, 'synched' : synched_events}