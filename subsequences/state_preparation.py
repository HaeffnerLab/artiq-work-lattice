from artiq.subsequence import subsequence
from artiq.experiment import *


class StatePreparation(EnvExperiment):

    def build(self):
        self.setattr_device("core")
        self.dds_729G = self.get_device("729G")

    #def setup(self):
    #    print("\n"*10, "something", "\n"*10)
    #    #self.setattr_device("core")

    @kernel
    def run(self):
        self.core.break_realtime()
        self.dds_729G.sw.on()
        #delay(self.p.StateReadout.state_readout_duration)
        self.dds_729G.sw.off()
        #pass

