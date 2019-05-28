import labrad
from artiq import *
from artiq.language import *
from artiq.language.core import TerminationRequested

class pmt_collect_continuously(EnvExperiment):

    def build(self):
        cxn = labrad.connect()
        p = cxn.parametervault
        self.duration = p.get_parameter(["PmtReadout", "duration"])["ms"]
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.pmt = self.get_device("pmt")
        self.dataset_length = {}
        cxn.disconnect()

    def run(self):
        self.core.reset()
        self.set_dataset("pmt_counts", [], broadcast=True)
        self.set_dataset("collection_duration", [self.duration])
        self.set_dataset("pmt_counts_866_off", [], broadcast=True)
        self.set_dataset("pulsed", [False], broadcast=True)
        self.set_dataset("clear_pmt_plot", False, broadcast=True)
        while True:
            try:
                self.run_pmt()
                self.core.comm.close()
                self.scheduler.pause()
            except TerminationRequested:
                break

    @kernel
    def run_pmt(self):
        self.core.break_realtime()
        while not self.scheduler.check_pause():
            self.core.break_realtime()
            t_count = self.pmt.gate_rising(self.duration*ms)
            pmt_count = self.pmt.count(t_count)
            self.append("pmt_counts", pmt_count)
            self.append("pmt_counts_866_off", -1)

    @rpc(flags={"async"})
    def append(self, dataset_name, data_to_append):
        if not dataset_name in self.dataset_length.keys():
            self.dataset_length[dataset_name] = 0

        if self.dataset_length[dataset_name] % 1000 == 0:
            self.set_dataset(dataset_name, [], broadcast=True)

        self.append_to_dataset(dataset_name, data_to_append)
        self.dataset_length[dataset_name] += 1

