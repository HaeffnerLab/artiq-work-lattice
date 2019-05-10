from artiq.pulse_sequence import PulseSequence
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *


PulseSequence.initialize_parameters()


class pstest(PulseSequence):
    is_ndim = False
    PulseSequence.accessed_params.update(
            {"Spectrum.wait_time_1"}
        )
    # fixed_params = [("StateReadout.pmt_readout_duration", 100*ms)]
    PulseSequence.scan_params.update(
            line1=("Spectrum", 
                [("Spectrum.pulse_duration", 0, 1, 10),
                 ("Spectrum.dummy_detuning", 0, 1, 10)]),
            line2=("Spectrum", 
                [("Spectrum.dummy_detuning", 0, 1, 10)])
        )

    def run_initially(self):
        self.sp = StatePreparation(self)
    
    @kernel
    def line1(self):
        self.calc_frequency("S+1/2D-3/2", 100*kHz, self.aux_axial, 1, "729L1", 
                            bound_param="Spectrum_dummy_detuning")
        self.sp.run(duration=self.Spectrum_wait_time_1)
        param = self.get_variable_parameter("Spectrum_pulse_duration")*ms
        # param = self.Spectrum_wait_time_1
        self.foo(param)
        # self.foo(self.Spectrum_pulse_duration)

    @kernel
    def line2(self):
        self.calc_frequency("S+1/2D-3/2", 100*kHz, self.aux_axial, 1, "729L1", 
                            bound_param="Spectrum_dummy_detuning")
        param = self.get_variable_parameter("Spectrum_dummy_detuning")*ms
        # param = self.Spectrum_wait_time_1
        delay(1*ms)
        self.foo(param)
        #self.foo(self.Spectrum_pulse_duration)

    @kernel
    def foo(self, delay_):
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
