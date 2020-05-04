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
        "CalibrationScans.calibrate_sidebands",
        "CalibrationScans.do_rabi_flop_carrier",
        "CalibrationScans.do_rabi_flop_radial1",
        "CalibrationScans.do_rabi_flop_radial2",
        "IonsOnCamera.ion_number"
    }

    PulseSequence.scan_params = dict(
        AutoCalibration=[
            ("Current", ("IonsOnCamera.ion_number", 1., 1., 1, "")),
        ])

    def run_initially(self):
        self.set_subsequence["AutoCalibration"] = self.set_subsequence_autocalibration

        if self.p.CalibrationScans.do_rabi_flop_carrier:
            # Run CalibPiTime for carrier
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
        
        if self.p.CalibrationScans.calibrate_sidebands:
            # TODO - run CalibPiTime for axial sideband

            if self.p.CalibrationScans.do_rabi_flop_radial1:
                # TODO - run CalibPiTime for radial sideband 1
                pass

            if self.p.CalibrationScans.do_rabi_flop_radial2:
                # TODO - run CalibPiTime for radial sideband 1
                pass

    @kernel
    def set_subsequence_autocalibration(self):
        pass

    @kernel
    def AutoCalibration(self):
        pass

    def run_finally(self):
        pass