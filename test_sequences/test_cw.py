from artiq import *
from artiq.language import *

class change_cw(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("scheduler")
        self.dds = self.get_device("866")
        self.get_argument("amplitude")
        self.get_argument("frequency")
        self.get_argument("state")

    @kernel
    def run(self):
        self.core.break_realtime()
        self.dds.set(self.frequency)
        self.dds.set_att(self.amplitude)
        if self.state:
            self.dds.sw.on()
        else:
            self.dds.sw.off()


