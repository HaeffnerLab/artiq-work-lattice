from artiq.experiment import *


class IdleKernel(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.cpld = self.get_device("urukul0_cpld")
        self.dds_866 = self.get_device("866")
        self.dds_397 = self.get_device("397")

    @kernel
    def run(self):
        #start_time = now_mu() + self.core.seconds_to_mu(500*ms)
        #while self.core.get_rtio_counter_mu() < start_time:
        #    continue
        self.core.reset()
        self.cpld.init()
        self.dds_866.init()
        self.dds_397.init()
        self.core.break_realtime()
        self.dds_866.sw.on()
        self.dds_397.sw.on()
        self.dds_866.set(100*MHz, amplitude=1.0)
        self.dds_397.set(150*MHz, amplitude=1.0)
        self.dds_866.set_att(22*dB)
        self.dds_397.set_att(22*dB)

