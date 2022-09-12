from PyQt5.QtCore import Qt
from pyqtgraph.Qt import QtGui, QtCore, QT_LIB
import pyqtgraph as pg
from pyqtgraph.Transform3D import Transform3D
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtWidgets
import time
import os
import sys
from modules.MicrophoneRecording import *
from modules.MarkerRecorder import MarkerRecorder
from modules.MarkerAnalyzer import MarkerAnalyzer
from utils.marker import Marker
from utils.loading import *
from utils.atracsystracking import AtracsysTracking
from utils.stats import *
import utils.qt_events as qevents
import threading
import logging

active_vertebra = ''
synched = True

# create marker recorder
marker_recorder = MarkerRecorder()

# create marker analyzer
marker_analyzer = MarkerAnalyzer()

# make sure the config file exists
assert os.path.exists(sys.argv[1]), 'configuration file does not exist'

# load config file
experiment_config = load_config_from_yaml(sys.argv[1])
config = load_config_from_yaml('configs/capture-default.yaml')
defaults = load_config_from_yaml('configs/defaults.yaml')
# load first experiment by default
active_vertebra = list(experiment_config.keys())[0]
config.geometries.update(experiment_config[active_vertebra])
update_dictionary_with_default(config, defaults)
loading_data_into_geometries(config)

# initialize tracking system
tracking_system = AtracsysTracking(config)

# make an app
app = pg.mkQApp("vat-capture")
app.setStyleSheet(
    'QLabel {background-color: black; color : white; border-color : black; padding : 6px}')

# make the window with grid layout
win = QtWidgets.QMainWindow()
win.resize(1200, 600)
win.setWindowTitle('VAT CAPTURE')
cw = QtWidgets.QWidget()
win.setCentralWidget(cw)
layout = QtWidgets.QGridLayout()
cw.setLayout(layout)
win.show()

# make 3d widgets for axial, sagittal, coronal views
posterior_w = gl.GLViewWidget(rotationMethod='quaternion')
axial_w = gl.GLViewWidget(rotationMethod='quaternion')
sagital_w = gl.GLViewWidget(rotationMethod='quaternion')

# add labels
stats0 = QtGui.QLabel()
stats0.setAlignment(Qt.AlignLeft | Qt.AlignTop)
stats1 = QtGui.QLabel()
stats1.setAlignment(Qt.AlignLeft | Qt.AlignTop)
stats2 = QtGui.QLabel()
stats2.setAlignment(Qt.AlignLeft | Qt.AlignTop)
stats3 = QtGui.QLabel()
stats3.setAlignment(Qt.AlignLeft | Qt.AlignTop)
stats4 = QtGui.QLabel()
stats4.setAlignment(Qt.AlignLeft | Qt.AlignTop)
stats5 = QtGui.QLabel()
stats5.setAlignment(Qt.AlignLeft | Qt.AlignTop)
time_stats = QtGui.QLabel()
time_stats.setAlignment(Qt.AlignRight | Qt.AlignTop)

# syncronize events
sync = qevents.Synchronizer([posterior_w, axial_w, sagital_w])
sync.add_event('wheelEvent', qevents.wheelEvent, sync.wheelEvents)
sync.add_event('mouseMoveEvent', qevents.mouseMoveEvent, sync.mouseMoveEvents)
sync.add_event('mousePressEvent', qevents.mouseMoveEvent, sync.mousePressEvents)
sync.toggleActive()

# sync buttons
sync_button = QtGui.QPushButton("SYNC")
sync_button.clicked.connect(sync.toggleActive)
# record button
# microphone=Microphone(active_vertebra)
recording = False
record_button = QtGui.QPushButton("START RECORDING")


def toggle_recording():
    global recording
    if recording:
        record_button.setText('START RECORDING')
        x1 = threading.Thread(target=record_button.setFlat, args=(0,))
        x1.start()
        x2 = threading.Thread(target=marker_recorder.save, args=(active_vertebra, screw_tip_navigation))
        x2.start()



    else:
        record_button.setText('STOP RECORDING')
        x1 = threading.Thread(target=record_button.setFlat, args=(1,))
        x1.start()

    recording = not recording
    print('Started recording' if recording else 'Stopped Recording')


record_button.clicked.connect(toggle_recording)


# combo box vertebrae
def switch_vertebrae(identifier):
    global active_vertebra
    active_vertebra = identifier
    clear_widgets([posterior_w, axial_w, sagital_w])
    config.geometries.update(experiment_config[identifier])
    update_dictionary_with_default(config, defaults)
    loading_data_into_geometries(config)
    add_posterior_copies(config)
    load_items(config)
    add_to_widget(posterior_w, config, posterior=True)
    add_to_widget(axial_w, config)
    add_to_widget(sagital_w, config)
    print('Vertebrae changed to: \t{0}'.format(identifier))


combo_box_vertebrae = QtGui.QComboBox()
for key in experiment_config.keys():
    combo_box_vertebrae.addItem(key)
combo_box_vertebrae.activated[str].connect(switch_vertebrae)

# combo box navigation method
screw_tip_navigation = False


def switch_navigation_method(identifier):
    global screw_tip_navigation, synched
    assert identifier in ['Entry Point', 'Screw Tip']
    screw_tip_navigation = identifier == 'Screw Tip'
    synched = False
    print('Navigation method changed to: \t{0}'.format(identifier))


combo_box_navi = QtGui.QComboBox()
combo_box_navi.addItem('Entry Point')
combo_box_navi.addItem('Screw Tip')
combo_box_navi.activated[str].connect(switch_navigation_method)

# analyze button
analyzing = False
analyzing_button = QtGui.QPushButton("START ANALYZING")


def toggle_analyzing():
    global analyzing
    if analyzing:

        analyzing_button.setText('START ANALYZING')
        analyzing_button.setFlat(0)

        infobox = QtWidgets.QDialog()
        infobox.setWindowTitle('Means')
        QtWidgets.QLabel(marker_analyzer.finalize_analyzation(), infobox).adjustSize()
        infobox.resize(250, 100)
        infobox.exec_()
    else:
        analyzing_button.setText('STOP ANALYZING')
        analyzing_button.setFlat(1)
    analyzing = not analyzing
    print('Started analyzing' if analyzing else 'Stopped Analyzing')


analyzing_button.clicked.connect(toggle_analyzing)

# set camera positions
posterior_w.setCameraPosition(elevation=0, azimuth=0, distance=200)
axial_w.setCameraPosition(elevation=0, azimuth=-90, distance=200)
sagital_w.setCameraPosition(elevation=0, azimuth=0, distance=200)

# add stats
layout.addWidget(stats0, 0, 0)
layout.addWidget(stats1, 0, 1)
layout.addWidget(stats2, 0, 2)
layout.addWidget(stats3, 0, 3)
layout.addWidget(stats4, 0, 4)
layout.addWidget(stats5, 0, 5)
layout.addWidget(time_stats, 0, 5)

# set the spacing to zero
layout.setSpacing(0)
layout.setVerticalSpacing(0)
# add 3d visualizers
layout.addWidget(posterior_w, 1, 0, 1, 2)
layout.addWidget(axial_w, 1, 2, 1, 2)
layout.addWidget(sagital_w, 1, 4, 1, 2)
# make sure the 3d visualizers can stretch
layout.setRowStretch(1, 10)
# add buttons
layout.addWidget(record_button, 2, 0)
layout.addWidget(sync_button, 2, 1)
layout.addWidget(analyzing_button, 2, 2)
# add comboboxes
layout.addWidget(combo_box_vertebrae, 2, 3)
layout.addWidget(combo_box_navi, 2, 4)


# load geometries into widgets
def add_to_widget(widget, config, posterior=False):
    for name, g in config.geometries.items():
        if posterior:
            if name in ['drillsleeve-dir', 'drillsleeve-origin', 'L', 'traj', 'mid', 'screw-tip']:
                continue
        if not posterior and '_' in name:
            continue
        widget.addItem(g.item)


# remove all items from widgets
def clear_widgets(widgets):
    for w in widgets:
        w.clear()


def update_geometry(marker: Marker):
    global synched, screw_tip_navigation
    for name, g in config.geometries.items():
        if g.marker == marker._identifier:
            # update pose
            if hasattr(g, 'item'):
                world_to_marker = Transform3D(marker.get_pose())
                g.item.setTransform(world_to_marker)
                # set visible if not already
                if g.vis and not g.item.visible():
                    g.item.setVisible(True)
                # disable mid and entry point in screw tip navigation
                if screw_tip_navigation and name in ['entry', 'mid']:
                    g.item.setVisible(False)
                # update trajectory if screw tip navigation
                if name == 'traj':
                    if screw_tip_navigation:
                        start = g.item.pos[0, :].flatten()
                        p_end = config.geometries['drillsleeve-tip'].item
                        mid = g.item.mapFromParent(p_end.mapToView(p_end.pos.T))[:, 0].flatten()
                        end = start + (mid - start) / np.linalg.norm(mid - start) * 150
                        g.item.setData(**{'pos': np.stack([start, end])})
                        synched = True
                    elif not synched:
                        start = g.data[0, 0:3]
                        mid = g.data[0, 3:6]
                        dir = (mid - start) / np.linalg.norm(mid - start)
                        end = start + dir * g.data[0, 6]
                        g.item.setData(**{'pos': np.stack([start, end])})
                        synched = True

            # update time
            g.last_seen = time.time()

        # time filter


def time_filter_update():
    for g in config.geometries.values():
        if hasattr(g, 'last_seen'):
            if time.time() - g.last_seen > config.time_filter and g.item.visible():
                g.item.setVisible(False)


def update_views(marker: Marker):
    world_to_marker = Transform3D(marker.get_pose())
    for g in config.geometries.values():
        if g.marker == marker._identifier and g.focus:
            assert g.type == 'mesh'
            c = world_to_marker.map(QtGui.QVector3D(*g.center.tolist()))
            posterior_w.setCameraPosition(pos=c)
            axial_w.setCameraPosition(pos=c)
            sagital_w.setCameraPosition(pos=c)


def update_stats():
    global analyzing
    for name, stat in config.statistics.items():
        args = []
        items = True
        for a in stat.args:
            if hasattr(config.geometries[a], 'item'):
                args.append(config.geometries[a].item)
            else:
                items = False
                break
        if items:
            res = stats_from_dict(name, stat, args)
            widget = globals()['stats' + str(stat.column)]
            widget.setText(res)
            if analyzing:
                marker_analyzer.add_data(name, stats_from_dict_numbers(stat, args))


# animation
def update():
    global tracking_system
    time_stats.setText(f'time\n{tracking_system.index / config.refresh_timeout:.2f}s')
    # get marker
    curr_markers = tracking_system.get_current_marker_data()
    #time_stats.setText(f'time\n{curr_markers[0]._timestamp /1000000000:.2f}s')


    while len(curr_markers) < 1:
        curr_markers = tracking_system.get_current_marker_data()

    # update marker list
    if recording:
        marker_recorder.update_markers(curr_markers)

    # update geometries and views
    for m in curr_markers:
        if not isinstance(m, Marker):
            m = Marker(m)
        update_geometry(m)
        update_views(m)


# load items
add_posterior_copies(config)
load_items(config)
add_to_widget(posterior_w, config, posterior=True)
add_to_widget(axial_w, config)
add_to_widget(sagital_w, config)

# screen update
update_timer = QtCore.QTimer()
update_timer.timeout.connect(update)
update_timer.start(config.refresh_timeout)

# disable unseen objects
filter_timer = QtCore.QTimer()
filter_timer.timeout.connect(time_filter_update)
filter_timer.start(config.time_filter)

# stats update
stats_timer = QtCore.QTimer()
stats_timer.timeout.connect(update_stats)
stats_timer.start(config.stats_timeout)

# main method
if __name__ == '__main__':
    # Start Qt event loop unless running in interactive mode or using
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()