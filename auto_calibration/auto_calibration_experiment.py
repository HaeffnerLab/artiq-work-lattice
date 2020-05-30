import numpy as np
import sys
import labrad
from labrad.units import WithUnit as U
from artiq.experiment import *
import logging

logger = logging.getLogger(__name__)

auto_calibration_sequences = {
    "RabiFlopping": {
        "file": "auto_calibration/sequences/rabi_flopping.py",
        "class_name": "RabiFlopping",
    },
    "Spectrum": {
        "file": "auto_calibration/sequences/spectrum.py",
        "class_name": "Spectrum",
    },
}

class AutoCalibration(EnvExperiment):
    accessed_params = {
        "IonsOnCamera.ion_number",
    }
    
    def simulate(self):
        # This is the entry point when called in simulation mode
        from simulated_pulse_sequence import SimulationScheduler
        self.scheduler = SimulationScheduler()

        self.prepare()
        self.run()
        self.analyze()

    def prepare(self):
        pass

    def run(self):
        expid = self.get_expid("RabiFlopping", "RabiFlopping.duration", start=0.0, stop=10.0e-6, npoints=3)
        self.scheduler.submit("main", expid, priority=100)

    def analyze(self):
        pass

    def get_expid(self, experiment_name, scan_param_name, start, stop, npoints):
        class_name = auto_calibration_sequences[experiment_name]["class_name"]
        experiment_file = auto_calibration_sequences[experiment_name]["file"]
        return {
            "arguments": {
                class_name + "-Scan_Selection": scan_param_name,
                class_name + ":" + scan_param_name: self.range_scan_args(start, stop, npoints),
                "auto_calibration_manager": self,
            },
            "class_name": class_name,
            "file": experiment_file,
            "priority": 100,
            "log_level": 30,
            "repo_rev": None,
        }

    def range_scan_args(self, start, stop, npoints):
        return { "ty": "RangeScan", "start": start, "stop": stop, "npoints": npoints, "randomize": False, "seed": None }
            
    # stub functions required by PulseSequence / SimulatedPulseSequence
    def __init__(self, managers_or_parent=()): pass
    def set_global_params(): pass
    def set_submission_arguments(self, submission_arguments): pass
