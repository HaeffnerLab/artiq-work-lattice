from artiq.language import *
from artiq.experiment import *


class scanTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.cpld = self.get_device("urukul0_cpld")
        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")

    def run(self):
        self.core.reset()
        #self.set_dataset("pmt_counts", [])
        #self.set_dataset("time", [])
        for _ in self.scan.NoSCan(0, 5):
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
        self.dds_397.set(10*MHz, profile=0)
        self.dds_866.set(10*MHz, profile=0)
        self.dds_397.set_att(22*dB)
        self.dds_866.set_att(15*dB)
        self.dds_397.sw.on()
        self.dds_866.sw.on()

        delay(1*s)

        self.dds_397.sw.off()
        self.dds_866.sw.off()

        delay(1*s)

        self.dds_397.set(100*MHz, profile=0)
        self.dds_866.set(100*MHz, profile=0)
        self.dds_397.sw.on()
        self.dds_866.sw.on()

        delay(1*s)

        self.dds_397.sw.off()
        self.dds_866.sw.off()




