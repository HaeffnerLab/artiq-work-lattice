from artiq.language import *


class scanTest(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.cpld = self.get_device("urukul0_cpld")
        self.dds_397 = self.get_device("397")
        self.dds_866 = self.get_device("866")

    def run(self):
        self.set_dataset("pmt_counts", [])
        self.set_dataset("time", [])
        self.cpld.init()
        self.dds_866.init()
        self.dds_397.init()
        while True:
            try:
                self.kernel_run()
            except TerminationRequested:
                break

    @kernel
    def kernel_run(self):
        self.core.break_realtime()

        self.dds_397.set(80*MHz)
        self.dds_866.set(100*MHz)
        self.dds_397.sw.on()
        self.dds_866.sw.on()

        self.core.delay(1*s)

        self.dds_397.sw.off()
        self.dds_866.sw.off()

        self.core.delay(1*s)

        self.dds_397.set(20*MHz)
        self.dds_866.set(20*MHz)
        self.dds_397.sw.on()
        self.dds_866.sw.on()

        self.core.delay(1*s)

        self.dds_397.sw.off()
        self.dds_866.sw.off()




