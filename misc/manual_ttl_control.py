from artiq import *
from artiq.language import *

class change_ttl(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.state = self.get_argument("state", BooleanValue())
        device = self.get_argument("device", StringValue("blue_PIs"))
        self.ttl = self.get_device(device)

    @kernel
    def run(self):
        self.core.reset()
        if self.state:
            self.ttl.on()
        else:
            self.ttl.off()
