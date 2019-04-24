from artiq.subsequence import subsequence
from artiq.experiment import *


class StatePreparation(subsequence):

    def setup(self):
        self.setattr_device("core")

    @kernel
    def sequence(self):
        self.parent_sequence.core.break_realtime()
        self.parent_sequence.dds_729G.sw.on()
        delay(self.p.StateReadout.state_readout_duration)
        self.parent_sequence.dds_729G.sw.off()

