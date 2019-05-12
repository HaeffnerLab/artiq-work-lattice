from artiq.experiment import *
from artiq.pulse_sequence import PulseSequence


PulseSequence.initialize_parameters()


class StatePreparation(PulseSequence):

    def build(self):
        self.setattr_device("core")
        self.dds_729G = self.get_device("729G")

    @kernel
    def run(self, duration):
        delay(duration)
