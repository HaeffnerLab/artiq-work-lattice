from artiq.pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *

class pstest(PulseSequence):
    rcg_tab = "Rabi"
    show_params = ["StateReadout.pmt_readout_duration"]
    fixed_params = [("StateReadout", "pmt_readout_duration", 100*ms)]
    x_label = "frequency"


    def sequence(self):
        StatePreparation(self).run()
        # StatePreparation(self).sequence()
        # self.add_sequence(StatePreparation, {"StateReadout.state_readout_duration", 1})
        self.foo()
        
    @kernel
    def foo(self):    
        self.core.break_realtime()
        self.dds_729L1.sw.on()
        delay(1*ms)
        self.dds_729L1.sw.off()
