import labrad
from artiq import *
from artiq.language import *
from artiq.language.core import TerminationRequested
import numpy as np

class camera_update(EnvExperiment):

    def build(self):
        self.cxn = labrad.connect()
        self.p = self.cxn.parametervault
        self.camera = self.cxn.nuvu_camera_server
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.dataset_length = {}

    def run(self):
        self.core.reset()
        self.set_dataset("pmt_counts", [], broadcast=True)
        # self.set_dataset("collection_duration", [self.duration])
        self.set_dataset("pmt_counts_866_off", [], broadcast=True)
        self.set_dataset("pulsed", [False], broadcast=True)
        self.set_dataset("clear_pmt_plot", [False], broadcast=True)
        while True:
            try:
                data = self.camera.get_most_recent_image()
                binx, biny, startx, stopx, starty, stopy = self.camera.get_image_region(None)
                pixels_x = (stopx - startx + 1) // binx
                pixels_y = (stopy - starty + 1) // biny
                Data = np.reshape(data, (pixels_y, pixels_x))
                ystart = int(self.p.get_parameter(["PmtReadout", "camera_ystart"]))
                ystop = int(self.p.get_parameter(["PmtReadout", "camera_ystop"]))
                xstart = int(self.p.get_parameter(["PmtReadout", "camera_xstart"]))
                xstop = int(self.p.get_parameter(["PmtReadout", "camera_xstop"]))
                count = sum(Data[ystart:ystop, xstart:xstop].flatten()) / 1e9
                self.append("pmt_counts", count)
                self.append("pmt_counts_866_off", -1)
                self.core.comm.close()
                self.scheduler.pause()
            except TerminationRequested:
                break

    def append(self, dataset_name, data_to_append):
        if dataset_name not in self.dataset_length.keys():
            self.dataset_length[dataset_name] = 0

        if self.dataset_length[dataset_name] % 1000 == 0:
            self.set_dataset(dataset_name, [], broadcast=True)

        self.append_to_dataset(dataset_name, data_to_append)
        self.dataset_length[dataset_name] += 1

    def analyze(self):
        self.cxn.disconnect()
