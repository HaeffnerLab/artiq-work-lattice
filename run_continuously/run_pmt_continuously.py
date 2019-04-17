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

    def run(self):
        self.core.reset()
        self.set_dataset("pmt_counts", [0], broadcast=True)
        self.set_dataset("collection_duration", [self.duration])
        self.set_dataset("pmt_counts_866_off", [], broadcast=True)
        self.set_dataset("diff_counts", [], broadcast=True)
        self.set_dataset("pulsed", [False], broadcast=True)
        while True:
            try:
                self.run_pmt()
                #self.core.comm.close()
                self.scheduler.pause()
                self.core.comm.open()
            except TerminationRequested:
                break

    @kernel
    def run_pmt(self):
        self.core.break_realtime()
        while not self.scheduler.check_pause():
            self.core.break_realtime()
            t_count = self.pmt.gate_rising(self.duration*ms)
            pmt_count = self.pmt.count(t_count)
            self.append_to_dataset("pmt_counts", pmt_count)

