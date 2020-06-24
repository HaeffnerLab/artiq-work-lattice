import logging
import os
import sys
from datetime import datetime

import labrad
import numpy as np
from labrad.units import WithUnit as U
from scipy.optimize import curve_fit
from tinydb import TinyDB, where

import artiq.dashboard.drift_tracker.client_config as cl
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
        job_name = "CalibLinesSpectrum"

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
            return
        
        print("AutoCalibration completed successfully for job {0}".format(job_name))

    def analyze(self):
        pass

    def update_parameter_vault(self, cxn, key, value):
        p = cxn.parametervault
        r = cxn.registry
        collection, parameter = key.split(".")
        old_parameter_value = p.get_parameter(collection, parameter)
        if isinstance(old_parameter_value, labrad.units.Value):
            units = old_parameter_value.units
            value = U(value, units)
        r.cd("", "Servers", "Parameter Vault", collection)
        parameter_type, current_registry_value = r.get(parameter)
        new_registry_value = value
        if parameter_type in ["line_selection", "selection_simple"]:
            new_registry_value = (value, current_registry_value[1])
        r.set(parameter, (parameter_type, new_registry_value))
        p.set_parameter([collection, parameter, new_registry_value])        

        return old_parameter_value

    def run_yaml_job(self, job_name):
        job = self.yaml[YamlKeys.jobs][job_name]

        # first check if the job has existing valid results, and if so, skip it
        # TODO - check valid_for against last job in database where valid=True
        valid_for = job[YamlKeys.job_valid_time]
        
        # set any parameters that need to be overridden for this job
        old_parameter_values = {}
        if YamlKeys.job_parameters in job:
            cxn = labrad.connect()
            for key, value in job[YamlKeys.job_parameters].items():
                old_parameter_values[key] = self.update_parameter_vault(cxn, key, value)
            cxn.disconnect()
        
        succeeded = True
        if YamlKeys.job_scan in job:
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
            result = AutoCalibrationManager().most_recent()
            print("result obtained inside run_yaml_job:", result)
            if result["scan"] != scan[YamlKeys.job_scan_name] or len(result["x"]) != scan[YamlKeys.job_scan_n_points]:
                succeeded = False

        # reset any parameters that were overridden for this job   
        cxn = labrad.connect()
        for key, value in old_parameter_values.items():
            self.update_parameter_vault(cxn, key, value)
        cxn.disconnect()

        return succeeded

    def run_and_fit(self, job_name):
        if not self.run_yaml_job(job_name):
            return False

        if YamlKeys.job_fit not in self.yaml[YamlKeys.jobs][job_name]:
            return True

        job_fit = self.yaml[YamlKeys.jobs][job_name][YamlKeys.job_fit]
        fit_name = job_fit[YamlKeys.job_fit_name]
        fit = self.yaml[YamlKeys.fits][fit_name]
        fit_parameters = fit[YamlKeys.fit_parameters]
        fit_code = fit[YamlKeys.fit_python]
        fit_guess_code = fit[YamlKeys.fit_guess]

        result = AutoCalibrationManager().most_recent()
        try:
            python_fit_code = get_python_fit_code(fit_name, fit_code, fit_parameters)
            exec(python_fit_code)
            fit_function = locals()[fit_name]

            x = result["x"]
            y = result["y"]
            guesses = eval(fit_guess_code)
            popt, pcov = curve_fit(fit_function, x, y, p0=guesses)
            print(popt, pcov)
        except:
            fit_succeeded = False
            logger.error("{0} fit failed for {1}".format(fit_name, job_name), exc_info=True)
            return False

        # Update the appropriate parameter source (ParameterVault or DriftTrackerGlobal) with the fit value
        parameter_source = job_fit[YamlKeys.job_fit_parameter_source]
        parameter_name = job_fit[YamlKeys.job_fit_parameter_name]
        parameter_index = fit_parameters.index(job_fit[YamlKeys.job_fit_parameter_value])
        parameter_value = popt[parameter_index]
        print("Updating {0} with fit parameter {1}={2}".format(
            parameter_source, parameter_name, parameter_value))
        if parameter_source == "DriftTrackerGlobal":
            try:
                global_cxn = labrad.connect(cl.global_address, password=cl.global_password, tls_mode="off")
                submission = [(parameter_name, U(parameter_value, "MHz"))]
                global_cxn.sd_tracker_global.set_measurements_with_one_line(submission, cl.client_name)
            except:
                logger.error("Failed to connect to SD tracker global to update line {0}".format(parameter_name), exc_info=True)
                return False
            finally:
                if global_cxn: global_cxn.disconnect()
        elif parameter_source == "ParameterVault":
            try:
                cxn = labrad.connect()
                self.update_parameter_vault(cxn, parameter_name, parameter_value)
            except:
                logger.error("Failed to connect to Parameter Vault to update {0}".format(parameter_name), exc_info=True)
            finally:
                if cxn: cxn.disconnect()
        else:
            logger.error("Unknown fit parameter source: {0}".format(parameter_source))
            return False

        # Save the fit results in the AutoCalibrationManager
        result["job"] = job_name
        result["fit"] = fit_name
        result["fit_values"] = list(popt)
        result["fit_covariance"] = [list(row) for row in pcov]
        result["fit_result"] = parameter_value
        result["valid"] = True
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
