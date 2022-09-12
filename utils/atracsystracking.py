from ctypes import ArgumentError
import os

from utils.marker import load_markers


def exit_with_error(error, tracking_system):
    print(error)
    answer = tracking_system.get_last_error()
    if answer[0] == tracking_ftk.Status.Ok:
        errors_dict = answer[1]
        for level in ['errors', 'warnings', 'messages']:
            if level in errors_dict:
                print(errors_dict[level])
    exit(1)


class AtracsysTracking:
    def __init__(self, config):
        self.geometry_files = [m.geom for _, m in config.markers.items()]
        self.config = config
        self.mode = config.mode            
        self.index = 0
        # stream from atracsys
        if self.mode == 'stream':
            import atracsys.ftk as tracking_ftk
            self.is_initialized = False
            self.tracker = tracking_ftk.TrackingSystem()
            self.last_frame = tracking_ftk.FrameData()
        elif self.mode == 'file':
            # stream from directory
            path = config.tracking
            assert path is not None
            assert os.path.exists(path)
            self.is_initialized = True
            self.markers = load_markers(path)
            self.length = len(self.markers)
        else:
            raise NotImplementedError

    def initialize_tracking_system(self) -> None:
        import atracsys.ftk as tracking_ftk
        # make sure we want to stream
        assert self.mode == 'stream'

        if self.tracker.initialise() != tracking_ftk.Status.Ok:
            exit_with_error(
                "Error, can't initialise the atracsys SDK api.", self.tracker)

        if self.tracker.enumerate_devices() != tracking_ftk.Status.Ok:
            exit_with_error("Error, can't enumerate devices.", self.tracker)

        if self.tracker.create_frame(False, 10, 20, 20, 10) != tracking_ftk.Status.Ok:
            exit_with_error("Error, can't create frame object.", self.tracker)

        answer = self.tracker.get_enumerated_devices()
        if answer[0] != tracking_ftk.Status.Ok:
            exit_with_error("Error, can't get list of enumerated devices", self.tracker)

        print("Tracker with serial ID {0} detected".format(
            hex(self.tracker.get_enumerated_devices()[1][0].serial_number)))

        geometry_path = "data-geometry"

        answer = self.tracker.get_data_option("Data Directory")
        if answer[0] != tracking_ftk.Status.Ok:
            exit_with_error("Error, can't read 'Data Directory' option", self.tracker)

        print(answer[1])

        for geometry in self.geometry_files:
            if self.tracker.set_geometry(
                    os.path.join(os.getcwd(), geometry_path, geometry)) != tracking_ftk.Status.Ok:
                exit_with_error(f"Error, can't load geometry {geometry}.", self.tracker)

        self.is_initialized = True

    def get_current_marker_data(self):
        if not self.is_initialized:
            self.initialize_tracking_system()

        if self.mode == 'stream':
            self.index += 1
            self.tracker.get_last_frame(self.last_frame)
            return self.last_frame.markers
        else:
            frame = self.markers[self.index % self.length]
            self.index = (self.index % self.length) + 1
            return frame
