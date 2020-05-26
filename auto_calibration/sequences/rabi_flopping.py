from auto_calibration.sequences.auto_calibration_base import AutoCalibrationSequence
from pulse_sequence import PulseSequence
from artiq.experiment import *
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation

###############################################################
# RabiFlopping pulse sequence for AutoCalibration jobs
###############################################################

class RabiFlopping(AutoCalibrationSequence):
    PulseSequence.accessed_params = {
        "RabiFlopping.line_selection",
        "RabiFlopping.amplitude_729",
        "RabiFlopping.att_729",
        "RabiFlopping.channel_729",
        "RabiFlopping.duration",
        "RabiFlopping.selection_sideband",
        "RabiFlopping.order",
        "RabiFlopping.detuning",
    }

    PulseSequence.scan_params = dict(
        RabiFlopping=[
            ("Rabi", ("RabiFlopping.duration", 0., 100e-6, 20, "us"))
        ])

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.RabiFlopping.channel_729
        self.rabi.amp_729 = self.p.RabiFlopping.amplitude_729
        self.rabi.att_729 = self.p.RabiFlopping.att_729
        self.set_subsequence["RabiFlopping"] = self.set_subsequence_rabiflopping

    @kernel
    def set_subsequence_rabiflopping(self):
        self.rabi.duration = self.get_variable_parameter("RabiFlopping_duration")
        self.rabi.freq_729 = self.calc_frequency(
            self.RabiFlopping_line_selection, 
            detuning=self.RabiFlopping_detuning,
            sideband=self.RabiFlopping_selection_sideband,
            order=self.RabiFlopping_order, 
            dds=self.RabiFlopping_channel_729
        )

    @kernel
    def RabiFlopping(self):
        self.stateprep.run(self)
        self.rabi.run(self)
