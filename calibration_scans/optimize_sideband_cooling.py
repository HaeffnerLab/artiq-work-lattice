from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *

class OptimizeSidebandCooling(PulseSequence):
    PulseSequence.accessed_params = {
        "SidebandCooling.amplitude_854",
        "SidebandCooling.att_854",
        "SidebandCooling.stark_shift",
        "SidebandCooling.line_selection",
        "SidebandCooling.amplitude_866",
        "SidebandCooling.att_866",
        "SidebandCooling.amplitude_729",
        "SidebandCooling.att_729",
        "SidebandCooling.selection_sideband",
        "SidebandCooling.optical_pumping_duration",
        "RabiFlopping.amplitude_729",
        "RabiFlopping.att_729",
        "RabiFlopping.duration",
        "RabiFlopping.line_selection",
        "RabiFlopping.selection_sideband",
        "RabiFlopping.order",
        "RabiFlopping.channel_729",
        "StatePreparation.sideband_cooling_enable",
        "StatePreparation.channel_729",
        "SidebandCooling.duration",
        "SidebandCooling.cycles",
        "SidebandCooling.cycle_increase_rate"
    }

    PulseSequence.scan_params["krun"] = [
        ("Current", ("SidebandCooling.amplitude_854", 0.0, 1.0, 20)),
        ("Current", ("SidebandCooling.amplitude_729", 0.0, 1.0, 20)),
        ("Current", ("SidebandCooling.stark_shift", -60*kHz, 60*kHz, 20, "kHz")),
        ("Current", ("SidebandCooling.duration", 0, 2*ms, 20, "ms")),
        ("Current", ("SidebandCooling.cycles", 0, 10, 10)),
        ("Current", ("SidebandCooling.optical_pumping_duration", 0, 1*ms, 10, "ms"))
    ]

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.sidebandcooling = self.add_subsequence(SidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.set_subsequence["krun"] = self.set_subsequence_krun

    @kernel#
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
        self.stateprep.enable_sideband_cooling = 0.0
        self.sidebandcooling.amp_729 = self.get_variable_parameter("SidebandCooling_amplitude_729")
        self.sidebandcooling.amp_854 = self.get_variable_parameter("SidebandCooling_amplitude_854")
        self.sidebandcooling.stark_shift = self.get_variable_parameter("SidebandCooling_stark_shift")
        self.sidebandcooling.duration = self.get_variable_parameter("SidebandCooling_duration")
        self.sidebandcooling.sideband_cooling_cycles = self.get_variable_parameter("SidebandCooling_cycles")
        self.sidebandcooling.optical_pumping_duration = self.get_variable_parameter("SidebandCooling_optical_pumping_duration")

    @kernel
    def krun(self):
        self.stateprep.run(self)
        self.sidebandcooling.run(self)
        self.rabi.run(self)
#