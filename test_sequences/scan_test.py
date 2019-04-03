from artiq.language import core, scan
from artiq.experiment import *


class scanTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.cpld = self.get_device("urukul0_cpld")
        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")
        self.setattr_argument("scan", scan.Scannable(default=scan.RangeScan(0, 10, 10)))

    def run(self):
        self.core.reset()
        for _ in self.scan:
            try:
                self.scheduler.pause()
                self.kernel_run()
            except core.TerminationRequested:
                break

    @kernel
    def kernel_run(self):
        self.core.break_realtime()
        #self.core.reset()
        self.cpld.init()
        self.dds_397.init()
        self.dds_866.init()
        self.dds_397.set(10*MHz)
        self.dds_866.set(10*MHz)
        self.dds_397.set_att(22*dB)
        self.dds_866.set_att(15*dB)
        with parallel:
            self.dds_397.sw.pulse(1*s)
            self.dds_866.sw.pulse(1*s)

        delay(1*s)

        #self.dds_397.sw.off()
        #self.dds_866.sw.off()

        #delay(1*s)

        self.dds_397.set(100*MHz)
        self.dds_866.set(100*MHz)
        with parallel:
            self.dds_397.sw.pulse(1*s)
            self.dds_866.sw.pulse(1*s)

        delay(1*s)




