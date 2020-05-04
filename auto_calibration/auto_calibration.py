import numpy as np
import labrad
from labrad.units import WithUnit as U
from pulse_sequence import PulseSequence, FitError
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *
import logging

logger = logging.getLogger(__name__)

class AutoCalibration(PulseSequence):
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
        AutoCalibration=[
            ("Rabi", ("RabiFlopping.duration", 0., 100e-6, 20, "us")),
        ])

    def run_initially(self):
        self.set_subsequence["AutoCalibration"] = self.set_subsequence_autocalibration

    @kernel
    def set_subsequence_autocalibration(self):
        pass

    @kernel
    def AutoCalibration(self):
        pass

    def run_finally(self):
        pass