import numpy as np
import sys
import labrad
from labrad.units import WithUnit as U
from artiq.experiment import *
import logging
from auto_calibration.parse_yaml import *

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
        self.yaml = load_configuration()

    def run_yaml_job(self, job_name):
        job = self.yaml[YamlKeys.jobs][job_name]

        # first check if the job has existing valid results, and if so, skip it
        # TODO - check valid_for against last job success time
        valid_for = job[YamlKeys.job_valid_time]
        
        # TODO: set any parameters that need to be overridden for this job
        cxn = labrad.connect()
        p = cxn.parametervault
        #old_val = p.get_parameter("RabiFlopping", "detuning")
        #p.set_parameter(["RabiFlopping", "detuning", U(200, 'kHz')])
        cxn.disconnect() 

        scan = job[YamlKeys.job_scan]
        expid = self.get_expid(
            experiment_name=scan[YamlKeys.job_scan_name],
            scan_param_name=scan[YamlKeys.job_scan_parameter],
            start=scan[YamlKeys.job_scan_start],
            stop=scan[YamlKeys.job_scan_stop],
            npoints=scan[YamlKeys.job_scan_n_points])
        self.scheduler.submit("main", expid, priority=100)

        # wait for the job to complete
        while len(self.scheduler.get_status()) > 0:
            time.sleep(1)

        # TODO: reset any parameters that were overridden for this job   
        cxn = labrad.connect()
        p = cxn.parametervault
        #p.set_parameter(["RabiFlopping", "detuning", old_val])
        cxn.disconnect()

    def run(self):
        # TODO: get the job name from some kind of user-supplied parameter
        job_name = "CalibLinesSpectrum-Line1"

        job = self.yaml[YamlKeys.jobs][job_name]
        print("Starting AutoCalibration for job {0}: {1}".format(job_name, job[YamlKeys.job_description]))

        for prerequisite_job_name in job[YamlKeys.job_prerequisites]:
            print("Running job prerequisite {0}".format(prerequisite_job_name))
            self.run_yaml_job(prerequisite)

            # TODO: run the fit for the last run, if it has results, and update auto calibration parameters.

            # TODO: determine the success value from the fit just performed.
            last_run_succeeded = True
            print("last_run_succeeded =", last_run_succeeded)
            if not last_run_succeeded:
                logger.error("Aborting AutoCalibration sequence due to failure in prerequisite job {0}".format(prerequisite_job_name))
                return

        print("Prerequisites completed, running job {0}".format(job_name))
        self.run_yaml_job(job_name)

    def analyze(self):
        pass

    def get_expid(self, experiment_name, scan_param_name, start, stop, npoints):
        class_name = auto_calibration_sequences[experiment_name]["class_name"]
        experiment_file = auto_calibration_sequences[experiment_name]["file"]
        return {
            "arguments": {
                class_name + "-Scan_Selection": scan_param_name,
                class_name + ":" + scan_param_name: self.range_scan_args(start, stop, npoints),
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
