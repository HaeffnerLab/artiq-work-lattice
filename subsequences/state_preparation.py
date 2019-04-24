from artiq.subsequence import subsequence
from artiq.experiment import *


class StatePreparation(subsequence):

    def setup(self):
        pass

    #@kernel
    def sequence(self):
        pass
        #self.parent_sequence.core.break_realtime()
        #self.parent_sequence.dds_729G.sw.on()
        #delay(self.p.StateReadout.state_readout_duration)
        #self.parent_sequence.dds_729G.sw.off()

