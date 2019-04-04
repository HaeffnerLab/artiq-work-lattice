from artiq.language import core, scan
from artiq.experiment import *
import labrad


class scanTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.cpld = self.get_device("urukul0_cpld")
        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")
        self.setattr_argument("scan", scan.Scannable(default=scan.RangeScan(0, 10, 10)))

    def prepare(self):
        self.cxn = labrad.connect()
        self.p = self.cxn.parametervault

    def run(self):
        self.core.reset()
        for _ in scan.NoScan(self.p["StateReadout"]["repeat_each_measurement"]):
            try:
                self.scheduler.pause()
                self.kernel_run()
            except core.TerminationRequested:
                break

    @kernel
    def kernel_run(self):
        self.core.break_realtime()
        self.cpld.init()
        self.dds_397.init()
        self.dds_866.init()
        with parallel:
            self.dds_397.set(10*MHz)
            self.dds_866.set(10*MHz)
            self.dds_397.set_att(22*dB)
            self.dds_866.set_att(15*dB)
            self.dds_397.sw.pulse(1*s)
            self.dds_866.sw.pulse(1*s)
        delay(1*s)
        with parallel:
            self.dds_397.set(100*MHz)
            self.dds_866.set(100*MHz)
            self.dds_397.sw.pulse(1*s)
            self.dds_866.sw.pulse(1*s)
        delay(1*s)

    def analyze(self):
        self.cxn.disconnect()
