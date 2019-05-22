from artiq.experiment import *

class DopplerCooling(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.setattr_device("")