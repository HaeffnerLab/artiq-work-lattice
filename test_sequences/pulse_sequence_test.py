from artiq.pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from susbsequence.optical_pumping_pulsed import OpticalPumpingPulsed
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
            # line2=("Spectrum", 
            #     [("Spectrum.dummy_detuning", 0, 1, 10)])
        )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
    
    @kernel
    def line1(self):
        param = self.get_variable_parameter("Spectrum_dummy_detuning")
        opc_lin3 = self.opc.line_selection
        opc_dds = self.opc.channel_729
        opc_freq_729 = self.calc_frequency(line, 0., self.aux_axial, 0, "729L1")
        delay(800*us)
        self.repump854.duration = param*ms
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.freq_729 = opc_freq_729
        self.opc.run(self)
        # self.foo(1*ms)
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

        
