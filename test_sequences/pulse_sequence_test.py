from artiq.pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from artiq.experiment import *


# PulseSequence.initialize_parameters()


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
        self.repump854 = self.add_subsequence(RepumpD)
    
    @kernel
    def line1(self):
        param = self.get_variable_parameter("Spectrum_dummy_detuning")
        self.calc_frequency("S+1/2D-3/2", param, self.aux_axial, 0, "729L1", 
                            bound_param="Spectrum_dummy_detuning")
        self.core.break_realtime()
        self.repump854()
        # param = self.get_variable_parameter("Spectrum_pulse_duration")*ms
        # param = self.Spectrum_wait_time_1
        self.foo(1*ms)
        # self.foo(self.Spectrum_pulse_duration)

    @kernel
    def line2(self):
        param = self.get_variable_parameter("Spectrum_dummy_detuning")
        self.calc_frequency("S+1/2D-3/2", param, self.aux_axial, 1, "729L1", 
                            bound_param="Spectrum_dummy_detuning")
        # param = self.Spectrum_wait_time_1
        delay(200*us)
        self.foo(1*ms)
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
