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
            #("Rabi", ("RabiFlopping.duration", 0., 100e-6, 20, "us")),
        ])

    def run_initially(self):
        self.set_subsequence["AutoCalibration"] = self.set_subsequence_autocalibration

        calibpitime_expid = {
            "arguments": {
                    "CalibPiTime-Scan_Selection": "RabiFlopping.duration",
                    "CalibPiTime:RabiFlopping.duration": { "ty": "RangeScan", "start": 0.0, "stop": 10.0e-6, "npoints": 20 }
                },
            "class_name": "CalibPiTime",
            "file": "calibration_scans/calib_pi_time.py",
            "priority": 100,
            "log_level": 30,
            "repo_rev": None
        }
        self.scheduler.submit("main", calibpitime_expid, priority=100)

    @kernel
    def set_subsequence_autocalibration(self):
        pass

    @kernel
    def AutoCalibration(self):
        pass

    def run_finally(self):
        pass