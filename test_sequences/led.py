from artiq.experiment import *


class LED(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("led1")
        self.setattr_device("led0")

    @kernel
    def run(self):
        self.core.reset()
        self.led1.off()
        self.led0.off()
