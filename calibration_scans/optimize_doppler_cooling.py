from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous
from subsequences.doppler_cooling import DopplerCooling
from artiq.experiment import *


class OptimizeDopplerCooling(PulseSequence):
    PulseSequence.accessed_params = {
        "RabiFlopping.amplitude_729",
        "RabiFlopping.att_729",
        "RabiFlopping.channel_729",
        "RabiFlopping.line_selection",
        "RabiFlopping.duration",
        "DopplerCooling.doppler_cooling_duration",
        "DopplerCooling.doppler_cooling_frequency_397",
        "DopplerCooling.doppler_cooling_att_397",
        "DopplerCooling.doppler_cooling_amplitude_397"
    }

    PulseSequence.scan_params["optimize_doppler_cooling"] = [
        ("Current", ("DopplerCooling.doppler_cooling_frequency_397", 50*MHz, 70*MHz, 20, "MHz")),
        ("Current", ("DopplerCooling.doppler_cooling_amplitude_397", 0., 1., 20)),
        ("Current", ("DopplerCooling.doppler_cooling_duration", 0, 4*ms, 20, "ms")),
    ]

    def run_initially(self):
        self.dopplercooling = self.add_subsequence(DopplerCooling)
        self.opp = self.add_subsequence(OpticalPumpingPulsed)
        self.opc = self.add_subsequence(OpticalPumpingContinuous)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.set_subsequence["optimize_doppler_cooling"] = self.set_subsequence_optimize_doppler_cooling

    @kernel
    def set_subsequence(self):
        self.rabi.duration = self.RabiFlopping_duration
        self.rabi.amp_729 = self.RabiFlopping_amplitude_729
        self.rabi.att_729 = self.RabiFlopping_att_729
        self.rabi.freq_729 = self.calc_frequency(
                                        self.RabiFlopping_line_selection, 
                                        detuning=0.,
                                        dds=self.RabiFlopping_channel_729
                                    )        
        self.dopplercooling.frequency_397 = self.get_variable_parameter("DopplerCooling_doppler_cooling_frequency_397")
        self.dopplercooling.amplitude_397 = self.get_variable_parameter("DopplerCooling_doppler_cooling_amplitude_397")
        self.dopplercooling.duration = self.get_variable_parameter("DopplerCooling_doppler_cooling_duration")


    @kernel
    def optimize_doppler_cooling(self):
        self.dopplercooling.run(self)
        if self.StatePreparation_pulsed_optical_pumping:
            self.opp.run(self)
        else:
            self.opc.run(self)
        self.rabi.run(self)