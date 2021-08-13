from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from subsequences.sideband_cooling import TwoToneSidebandCooling
from artiq.experiment import *


class OptimizeTwoToneSidebandCooling(PulseSequence):
    PulseSequence.accessed_params = {
        "SidebandCooling.frequency_854",
        "SidebandCooling.frequency_866",
        "SidebandCooling.amplitude_866",
        "SidebandCooling.att_866",
        "SidebandCooling.selection_sideband",
        "SidebandCooling.order",

        "TwoToneSidebandCooling.stark_shift1",
        "TwoToneSidebandCooling.stark_shift2",
        "TwoToneSidebandCooling.dp_amp",
        "TwoToneSidebandCooling.dp_att",
        "TwoToneSidebandCooling.drive1_amp",
        "TwoToneSidebandCooling.drive1_att",
        "TwoToneSidebandCooling.drive2_amp",
        "TwoToneSidebandCooling.drive2_att",
        "TwoToneSidebandCooling.amp_854",
        "TwoToneSidebandCooling.att_854",
        "TwoToneSidebandCooling.duration",

        "RabiFlopping.amplitude_729",
        "RabiFlopping.att_729",
        "RabiFlopping.duration",
        "RabiFlopping.line_selection",
        "RabiFlopping.selection_sideband",
        "RabiFlopping.order",
        "RabiFlopping.channel_729",
        "StatePreparation.sideband_cooling_enable",
        "StatePreparation.enable_two_tone_sideband_cooling"
        "StatePreparation.channel_729",
    
    }

    PulseSequence.scan_params["OptimizeTwoToneSidebandCooling"] = [
        ("Current", ("TwoToneSidebandCooling.amp_854", 0.0, 1.0, 20)),
        ("Current", ("TwoToneSidebandCooling.dp_amp", 0.0, 1.0, 20)),
        ("Current", ("TwoToneSidebandCooling.drive1_amp", 0.0, 1.0, 20)),
        ("Current", ("TwoToneSidebandCooling.drive2_amp", 0.0, 1.0, 20)),
        ("Current", ("TwoToneSidebandCooling.stark_shift1", -60*kHz, 60*kHz, 20, "kHz")),
        ("Current", ("TwoToneSidebandCooling.stark_shift2", -60*kHz, 60*kHz, 20, "kHz")),
        ("Current", ("TwoToneSidebandCooling.duration", 0, 2*ms, 20, "ms")),
    ]

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.sidebandcooling = self.add_subsequence(TwoToneSidebandCooling)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.set_subsequence["OptimizeTwoToneSidebandCooling"] = self.set_subsequence_optimize_two_tone_sideband_cooling


    @kernel
    def set_subsequence_optimize_two_tone_sideband_cooling(self):
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
        self.stateprep.enable_two_tone_sideband_cooling = 0.0
        self.sidebandcooling.amp_854 = self.get_variable_parameter("TwoToneSidebandCooling_amp_854")
        self.sidebandcooling.dp_amp = self.get_variable_parameter("TwoToneSidebandCooling_dp_amp")
        self.sidebandcooling.drive1_amp = self.get_variable_parameter("TwoToneSidebandCooling_drive1_amp")
        self.sidebandcooling.drive2_amp = self.get_variable_parameter("TwoToneSidebandCooling_drive2_amp")
        self.sidebandcooling.stark_shift1 = self.get_variable_parameter("TwoToneSidebandCooling_stark_shift1")
        self.sidebandcooling.stark_shift2 = self.get_variable_parameter("TwoToneSidebandCooling_stark_shift2")
        self.sidebandcooling.duration = self.get_variable_parameter("TwoToneSidebandCooling_duration")


    @kernel
    def OptimizeTwoToneSidebandCooling(self):
        self.stateprep.enable_optical_pumping = 0.0
        self.stateprep.run(self)
        
        self.sidebandcooling.run(self)

        self.stateprep.enable_optical_pumping = 1.0
        self.stateprep.enable_doppler_cooling = 0.0
        self.stateprep.run(self)
        
        self.rabi.run(self)