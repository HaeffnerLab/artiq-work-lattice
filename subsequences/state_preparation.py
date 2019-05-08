from artiq.experiment import *


class StatePreparation(EnvExperiment):
    accessed_params = {"StateReadout.line_1_amplitude"}

    def build(self):
        self.setattr_device("core")
        self.dds_729G = self.get_device("729G")

    @kernel
    def run(self, duration):
        delay(duration)
