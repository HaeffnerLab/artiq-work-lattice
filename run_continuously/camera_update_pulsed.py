import labrad
from artiq import *
from artiq.language import *
from artiq.language.core import TerminationRequested
import numpy as np

class camera_update_pulsed(EnvExperiment):

    def build(self):
        self.cxn = labrad.connect()
        self.p = self.cxn.parametervault
        self.camera = self.cxn.nuvu_camera_server
        self.setattr_device("core")
        self.dds_866 = self.get_device("866")
        self.setattr_device("scheduler")
        self.dataset_length = {}

    def run(self):
        self.core.reset()
        self.set_dataset("pmt_counts", [], broadcast=True)
        # self.set_dataset("collection_duration", [self.duration])
        self.set_dataset("pmt_counts_866_off", [], broadcast=True)
        self.set_dataset("pulsed", [False], broadcast=True)
        self.set_dataset("clear_pmt_plot", [False], broadcast=True)
        try:
            self.camera.start_live_display()
        except:
            pass
        while True:
            try:
                data = self.camera.get_most_recent_image()
                count = np.sum(data) / 1e7  # arbitrary factor
                self.append("pmt_counts", count)
                self.turn866off()
                data = self.camera.get_most_recent_image()
                count = np.sum(data) / 1e7  # arbitrary factor
                self.append("pmt_counts_866_off", data)
                self.turn866on()
                self.core.comm.close()
                self.scheduler.pause()
            except TerminationRequested:
                break
            # except:
            #     try:
            #         self.camera.start_live_display()
            #     except:
            #         pass
            #     continue

    @kernel
    def turn866on(self):
        self.core.break_realtime()
        self.dds_866.sw.on()
        delay(1*ms)

    @kernel
    def turn866off(self):
        self.core.break_realtime()
        self.dds_866.sw.off()
        delay(1*ms)

    def append(self, dataset_name, data_to_append):
        if dataset_name not in self.dataset_length.keys():
            self.dataset_length[dataset_name] = 0

        if self.dataset_length[dataset_name] % 1000 == 0:
            self.set_dataset(dataset_name, [], broadcast=True)

        self.append_to_dataset(dataset_name, data_to_append)
        self.dataset_length[dataset_name] += 1

    def analyze(self):
        self.cxn.disconnect()
