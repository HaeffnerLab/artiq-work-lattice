from artiq.experiment import *


class rf_test(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.dds = self.get_device("729G")

    @kernel
    def run(self):
        self.core.reset()
        self.dds.set(220*MHz, amplitude=1.)
        self.dds.set_att(20*dB)
        self.core.break_realtime()
        self.dds.sw.on()
        delay(10*s)
        self.dds.sw.off()
