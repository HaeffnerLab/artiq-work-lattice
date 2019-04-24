from artiq.experiment import *


class StatePreparation(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds_729G = self.get_device("729G")

    def run(self):
        print(self.p.StateReadout.state_readout_duration)
