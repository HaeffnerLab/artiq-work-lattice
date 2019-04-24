from artiq.subsequence import subsequence
from artiq.experiment import *


class StatePreparation(subsequence):

    def setup(self):
        pass

    @kernel
    def sequence(self):
        self.core.break_realtime()
        self.dds_729G.sw.on()
        delay(self.p.StateReadout.state_readout_duration)
        self.dds_729G.sw.off()

