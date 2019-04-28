from artiq.pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *

class pstest(PulseSequence):
    rcg_tab = "Rabi"
    accessed_params = {"StateReadout.pmt_readout_duration",
                       "Spectrum.wait_time_1"}
    accessed_params.update(StatePreparation.accessed_params)
    # fixed_params = [("StateReadout.pmt_readout_duration", 100*ms)]
    scan_params = {"line1": [("Spectrum.pulse_duration", 0, 1, 10)]}
                #    "line2": [("Spectrum.pulse_duration", 0, 1, 10)]}

    @kernel
    def line1(self):
        # self.add_sequence(StatePreparation, {"StateReadout.state_readout_duration": 1*ms})
        self.foo(self.Spectrum_wait_time_1)
        self.foo(self.Spectrum_pulse_duration)
    
    def line2(self):
        print("yo")
        
    @kernel
    def foo(self, delay_):
        self.core.break_realtime()  
        self.dds_729L1.sw.on()
        delay(delay_)
        self.dds_729L1.sw.off()
        delay(delay_)
        # self.foo1()

    @portable
    def foo1(self):
        delay(1*s)
