import logging
import os
import sys
from datetime import datetime

import labrad
import numpy as np
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
from tinydb import TinyDB, where

from artiq.experiment import *
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

class AutoCalibrationManager:
    def __init__(self):
        db_dir = os.path.join(os.path.expanduser("~"), "data", "calibration")
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, "db.json")

    def save(self, scan, x, y, timestamp):
        with TinyDB(self.db_path) as db:
            db.insert({"scan": scan, "x": list(x), "y": list(y), "timestamp": timestamp.timestamp()})
    
    def from_timestamp(self, timestamp):
        with TinyDB(self.db_path) as db:
            return db.search(where("timestamp") == timestamp.timestamp())

    def most_recent(self):
        with TinyDB(self.db_path) as db:
            *_, last = iter(db)
            return last
    
    def update(self, item):
        with TinyDB(self.db_path) as db:
            db.update(item, where("timestamp") == item["timestamp"])

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

    def run(self):
        # TODO: get the job name from some kind of user-supplied parameter
        job_name = "CalibLinesSpectrum-Line1"

        job = self.yaml[YamlKeys.jobs][job_name]
        print("Starting AutoCalibration for job {0}: {1}".format(job_name, job[YamlKeys.job_description]))

        # Run the prerequisites. The YAML parser has already put them in the correct order.
        for prerequisite_job_name in job[YamlKeys.job_prerequisites]:
            print("Running job prerequisite {0}".format(prerequisite_job_name))
            if not self.run_and_fit(prerequisite_job_name):
                logger.error("Aborting AutoCalibration sequence due to failure in prerequisite job {0}".format(prerequisite_job_name))
                return

        # Now run the job itself.
        print("Prerequisites completed, running job {0}".format(job_name))
        if not self.run_and_fit(job_name):
            logger.error("AutoCalibration sequence failed due to failure in job {0}".format(job_name))
        
        print("AutoCalibration completed successfully for job {0}".format(job_name))

    def analyze(self):
        pass

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
        
        # validate that all the data points were obtained
        succeeded = True
        result = AutoCalibrationManager().most_recent()
        print("result obtained inside run_yaml_job:", result)
        if result["scan"] != scan[YamlKeys.job_scan_name] or len(result["x"]) != scan[YamlKeys.job_scan_n_points]:
            succeeded = False

        # TODO: reset any parameters that were overridden for this job   
        cxn = labrad.connect()
        p = cxn.parametervault
        #p.set_parameter(["RabiFlopping", "detuning", old_val])
        cxn.disconnect()

        return succeeded

    def run_and_fit(self, job_name):
        if not self.run_yaml_job(job_name):
            return False

        job_fit = self.yaml[YamlKeys.jobs][job_name][YamlKeys.job_fit]
        fit_name = job_fit[YamlKeys.job_fit_name]
        fit = self.yaml[YamlKeys.fits][fit_name]
        fit_parameters = fit[YamlKeys.fit_parameters]
        fit_code = fit[YamlKeys.fit_python]

        result = AutoCalibrationManager().most_recent()
        try:
            python_fit_code = get_python_fit_code(fit_name, fit_code, fit_parameters)
            exec(python_fit_code)
            fit_function = locals()[fit_name]

            guesses = [1.0] * len(fit_parameters) # TODO: need to define guesses in the YAML
            popt, pcov = curve_fit(fit_function, result["x"], result["y"], p0=guesses)
            print(popt, pcov)
        except:
            fit_succeeded = False
            logger.error("{0} fit failed for {1}".format(fit_name, job_name), exc_info=True)
            return False

        parameter_source = job_fit[YamlKeys.job_fit_parameter_source]
        parameter_name = job_fit[YamlKeys.job_fit_parameter_name]
        parameter_index = fit_parameters.index(job_fit[YamlKeys.job_fit_parameter_value])
        parameter_value = popt[parameter_index]
        print("Updating {0} with fit parameter {1}={2}".format(
            parameter_source, parameter_name, parameter_value))
        if parameter_source == "DriftTrackerGlobal":
            # TODO: Update DriftTrackerGlobal with specified value
            pass
        elif parameter_source == "ParameterVault":
            # TODO: Update ParameterVault parameter with specified value
            pass
        else:
            logger.error("Unknown fit parameter source: {0}".format(parameter_source))
            return False

        # Save the fit results in the AutoCalibrationManager
        result["job"] = job_name
        result["fit"] = fit_name
        result["fit_values"] = list(popt)
        result["fit_covariance"] = [list(row) for row in pcov]
        # TODO: also include the value that was actually written out to the parameter source
        AutoCalibrationManager().update(result)

        return True

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
