from artiq.pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *

class pstest(PulseSequence):
    rcg_tab = "Rabi"
    show_params = ["StateReadout.pmt_readout_duration"]
    fixed_params = [("StateReadout.pmt_readout_duration", 100*ms)]
    scan_params = {"line1": [("Spectrum.pulse_duration", 0, 1, 10)],
                   "line2": [("Spectrum.pulse_duration", 0, 1, 10)]}


    def sequence(self):
        self.add_sequence(StatePreparation, {"StateReadout.state_readout_duration": 1*ms})
        self.foo()
        
    @kernel
    def foo(self):    
        self.core.break_realtime()
        self.dds_729L1.sw.on()
        delay(self.p.Spectrum.pulse_duration)
        self.dds_729L1.sw.off()
