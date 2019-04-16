import labrad
from artiq import *
from artiq.language import *

class pmt_collect_continuously(EnvExperiment):

    def build(self):
        cxn = labrad.connect()
        p = cxn.parametervault
        self.duration = p.get_parameter(["PmtReadout", "duration"])["ms"]
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.pmt = self.get_device("pmt")
        self.cpld = self.get_device("urukul0_cpld")
        self.dds_866 = self.get_device("866")
        self.dds_397 = self.get_device("397")


    def run(self):
        self.core.reset()
        self.set_dataset("pmt_counts", [0], broadcast=True)
        self.set_dataset("collection_duration", [self.duration])
        self.set_dataset("pmt_counts_866_off", [], broadcast=True)
        self.set_dataset("diff_counts", [], broadcast=True)
        self.set_dataset("pulsed", [False], broadcast=True)
        while True:
            self.run_pmt()
            self.scheduler.pause()


    @kernel
    def run_pmt(self):
        self.core.break_realtime()
        self.cpld.init()
        self.dds_866.init()
        self.dds_397.init()
        with parallel:
            self.dds_866.set(80*MHz)
            self.dds_397.set(75*MHz)
            self.dds_866.set_att(22*dB)
            self.dds_397.set_att(22*dB)
            self.dds_866.sw.on()
            self.dds_397.sw.on()
        while True:
            if self.scheduler.check_pause():
                break
            self.core.break_realtime()
            t_count = self.pmt.gate_rising(self.duration*ms)
            pmt_count = self.pmt.count(t_count)
            self.append_to_dataset("pmt_counts", pmt_count)

