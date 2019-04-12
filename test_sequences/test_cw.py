from artiq import *
from artiq.language import *

class change_cw(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.dds = self.get_device("866")
        self.frequency = self.get_argument("amplitude", NumberValue(80, unit="MHz", scale=0.1))
        self.get_argument("frequency", NumberValue(-40, unit="dB", scale=0.1))
        self.get_argument("state", BooleanValue())

    @kernel
    def run(self):
        self.core.break_realtime()
        self.dds.set(self.frequency)
        self.dds.set_att(self.amplitude)
        if self.state:
            self.dds.sw.on()
        else:
            self.dds.sw.off()


