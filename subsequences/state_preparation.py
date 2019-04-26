from artiq.experiment import *


class StatePreparation(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds_729G = self.get_device("729G")


    def run(self):
        self.my_delay(self.p.StateReadout.state_readout_duration)

    @kernel
    def my_delay(self, duration):
        delay(duration)