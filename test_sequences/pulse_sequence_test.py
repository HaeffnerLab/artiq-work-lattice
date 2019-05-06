from artiq.pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *

class pstest(PulseSequence):
    accessed_params = {"StateReadout.pmt_readout_duration",
                       "Spectrum.wait_time_1",
                       "StateReadout.use_camera_for_readout",
                       "StateReadout.readout_mode"}
    accessed_params.update(StatePreparation.accessed_params)
    # fixed_params = [("StateReadout.pmt_readout_duration", 100*ms)]
    PulseSequence.scan_params.update(line1=([("Spectrum.pulse_duration", 0, 1, 10)], "Rabi"),
                                     line2=([("Spectrum.dummy_detuning", 0, 1, 10)], "Spectrum"))

    @kernel
    def line1(self):
        # self.add_sequence(StatePreparation, {"StateReadout.state_readout_duration": 1*ms})
        param = self.get_variable_parameter("Spectrum_wait_time_1")
        # param = self.Spectrum_wait_time_1
        self.foo(param)
        # self.foo(self.Spectrum_pulse_duration)

    @kernel
    def line2(self):
        param = self.get_variable_parameter("Spectrum_wait_time_1")
        # param = self.Spectrum_wait_time_1
        self.foo(param)
        #self.foo(self.Spectrum_pulse_duration)

    @kernel
    def foo(self, delay_):
        self.core.break_realtime()
        self.dds_729L1.sw.on()
        delay(delay_)
        self.dds_729L1.sw.off()
        delay(delay_)
        self.dds_729L1.sw.on()
        delay(delay_)
        self.dds_729L1.sw.off()
        # self.foo1()

    @portable
    def foo1(self):
        delay(1*s)
