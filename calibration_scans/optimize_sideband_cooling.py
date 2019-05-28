from pulse_sequence import PulseSequence
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *



class OptimizeSidebandCooling(PulseSequence):
    PulseSequence.accessed_params.update(
        {"SidebandCooling.amplitude_854",
         "SidebandCooling.att_854",
         "SidebandCooling.stark_shift",
         "SidebandCooling.line_selection",
         "SidebandCooling.amplitude_866",
         "SidebandCooling.att_866",
         "SidebandCooling.amplitude_729",
         "SidebandCooling.att_729",
         "RabiFlopping.amplitude_729",
         "RabiFlopping.att_729",
         "RabiFlopping.duration",
         "RabiFlopping.line_selection",
         "RabiFlopping.selection_sideband",
         "RabiFlopping.order",
         "RabiFlopping.channel_729"}
    )

    PulseSequence.scan_params["krun"] = ("Current",
        [("SidebandCooling.amplitude_854", 0., 1., 25),
         ("SidebandCooling.att_854", 5., 32.5, 15, "dB"),
         ("SidebandCooling.stark_shift", -60*kHz, 60*kHz, 20, "kHz")]    
    )

    def run_initially(self):
        self.repump854 = self.add_subsequence(RepumpD)
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opc = self.add_subsequence(OpticalPumpingPulsed)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["krun"] = self.set_subsequence_krun

    @kernel
    def set_subsequence_krun(self):
        self.rabi.duration = self.RabiFlopping_duration
        self.rabi.amp_729 = self.RabiFlopping_amplitude_729
        self.rabi.att_729 = self.RabiFlopping_att_729
        self.rabi.freq_729 = self.calc_frequency(
            self.RabiFlopping_line_selection, 
            detuning=0.,
            sideband=self.RabiFlopping_selection_sideband,
            order=self.RabiFlopping_order, 
            dds=self.RabiFlopping_channel_729
        )
        self.sbc.amp_854 = self.get_variable_parameter("SidebandCooling_amplitude_854")
        self.sbc.att_854 = self.get_variable_parameter("SidebandCooling_att_854")
        self.sbc.stark_shift = self.get_variable_parameter("SidebandCooling_stark_shift")
    
    @kernel
    def krun(self):
        delay(1*ms)
        self.repump854.run(self)
        self.dopplerCooling.run(self)
        self.opc.run(self)
        self.sbc.run(self)
        self.rabi.run(self)
