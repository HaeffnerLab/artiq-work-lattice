import copy
import logging
from numbers import Number
import numpy as np
import os
from scipy.optimize import curve_fit
import traceback
import yaml

logger = logging.getLogger("auto_calibration")
log_level = logging.DEBUG
logger.setLevel(log_level)

console = logging.StreamHandler()
console.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

class YamlKeys:
    fits = "fits"
    fit_parameters = "parameters"
    fit_python = "python"
    fit_guess = "guess"

    jobs = "jobs"
    job_description = "description"
    job_inherits_from = "inherits-from"
    job_prerequisites = "prerequisites"
    job_valid_time = "valid-time"
    job_scan = "scan"
    job_scan_name = "name"
    job_scan_parameter = "parameter"
    job_scan_start = "start"
    job_scan_stop = "stop"
    job_scan_n_points = "n-points"
    job_parameters = "parameters"
    job_fit = "fit"
    job_fit_name = "name"
    job_fit_parameter_source = "parameter-source"
    job_fit_parameter_name = "parameter-name"
    job_fit_parameter_value = "parameter-value"


class CircularJobInheritanceError(Exception): pass
class CircularJobPrerequisiteError(Exception): pass
class InvalidFitPythonCode(Exception): pass

def merged_list(child, parent):
    assert isinstance(child, list)
    assert isinstance(parent, list)

    # return the union of the two lists
    return list(set(child + parent))

def merged_dict(child, parent):
    assert isinstance(child, dict)
    assert isinstance(parent, dict)

    # start with the parent dict
    merged = copy.deepcopy(parent)

    # merge in each of the items from the child dict
    for name, value in child.items():
        if name not in merged:
            # use the child value
            merged[name] = value
        elif isinstance(value, dict):
            # combine the child and parent dicts
            assert isinstance(merged[name], dict)
            merged[name] = merged_dict(value, merged[name])
        elif isinstance(value, list):
            # combine the child and parent lists
            assert isinstance(merged[name], list)
            merged[name] = merged_list(value, merged[name])
        else:
            # overwrite with the child value
            merged[name] = value

    # return the merged dict
    return merged

def collect_and_resolve_prerequisites(job_name, all_jobs):
    assert isinstance(job_name, str)
    assert isinstance(all_jobs, dict)

    prerequisites = []
    if YamlKeys.job_prerequisites in all_jobs[job_name]:
        prerequisites = collect_prerequisites(prerequisites, all_jobs[job_name][YamlKeys.job_prerequisites], all_jobs)
        prerequisites = resolve_prerequisites(job_name, prerequisites, all_jobs)
        logger.info("Resolved prerequisites: {0} <- {1}".format(job_name, prerequisites))
    return prerequisites

def collect_prerequisites(existing_prerequisites, prerequisites_to_add, all_jobs):
    assert isinstance(existing_prerequisites, list)
    assert isinstance(prerequisites_to_add, list)
    assert isinstance(all_jobs, dict)

    prerequisites = copy.deepcopy(existing_prerequisites)

    # collect the prerequisites into a list
    for prerequisite_job_name in reversed(prerequisites_to_add):
        if not prerequisite_job_name in prerequisites:
            prerequisites.insert(0, prerequisite_job_name)
            if YamlKeys.job_prerequisites in all_jobs[prerequisite_job_name]:
                prerequisites = collect_prerequisites(prerequisites, all_jobs[prerequisite_job_name][YamlKeys.job_prerequisites], all_jobs)

    return prerequisites

def resolve_prerequisites(original_job_name, prerequisites, all_jobs):
    assert isinstance(original_job_name, str)
    assert isinstance(prerequisites, list)
    assert isinstance(all_jobs, dict)

    # ensure we don't have a blatant circular dependency
    if original_job_name in prerequisites:
        message = "{0} has itself as a prerequisite. Full list of prerequisites: {1}".format(original_job_name, prerequisites)
        logger.error(message)
        raise CircularJobPrerequisiteError(message)

    # don't modify the original list
    prerequisites = copy.deepcopy(prerequisites)

    # make repeated passes through the list to try to find a good order
    done = False
    pass_count = 0
    while not done:
        pass_count = pass_count + 1

        # Unless we have an enormous number of job definitions, we should never have to make this many passes.
        if pass_count > 1000:
            message = "Unable to resolve prerequisites for {0}. Possible circular dependency? Full list of prerequisites: {1}".format(original_job_name, prerequisites)
            logger.error(message)
            raise CircularJobPrerequisiteError(message)

        # Find any job that is listed before its prerequisites.
        move_to_end = []
        for job_index, job_name in enumerate(prerequisites):
            if YamlKeys.job_prerequisites in all_jobs[job_name]:
                for prerequisite_job_name in all_jobs[job_name][YamlKeys.job_prerequisites]:
                    if not prerequisite_job_name in prerequisites[:job_index]:
                        # This job is missing a prerequisite. Move it to the end.
                        move_to_end.append(job_name)
                        break
        
        # Move any requested jobs to the end of the list
        if move_to_end:
            for job_name in reversed(prerequisites):
                if job_name not in move_to_end:
                    move_to_end.insert(0, job_name)
            prerequisites = move_to_end
        else:
            done = True

    return prerequisites

def validate_type(properties, name, expected_type, required):
    assert isinstance(properties, dict)
    assert isinstance(name, str)
    assert isinstance(expected_type, type)
    assert isinstance(required, bool)

    if name not in properties:
        return not required
    return isinstance(properties[name], expected_type)

def required(properties, name, expected_type):
    assert isinstance(properties, dict)
    assert isinstance(name, str)
    assert isinstance(expected_type, type)

    return validate_type(properties, name, expected_type, required=True)

def optional(properties, name, expected_type):
    assert isinstance(properties, dict)
    assert isinstance(name, str)
    assert isinstance(expected_type, type)

    return validate_type(properties, name, expected_type, required=False)
    
def get_python_fit_code(fit_name, fit_code, fit_parameters):
    return "def {0}(x,{1}):\n\treturn {2}".format(
        fit_name,
        ",".join(fit_parameters),
        fit_code.replace("\n", " ").replace("\r", " "))

def validate_fit(fit_name, fit_properties):
    assert isinstance(fit_name, str)
    assert isinstance(fit_properties, dict)

    # validate parameters and types
    error_message = "Unexpected or missing property in fit {0}".format(fit_name)
    assert required(fit_properties, YamlKeys.fit_parameters, list), error_message
    assert required(fit_properties, YamlKeys.fit_python, str), error_message
    assert required(fit_properties, YamlKeys.fit_guess, str), error_message

    # validate Python fit function
    fit_parameters = fit_properties[YamlKeys.fit_parameters]
    fit_code = fit_properties[YamlKeys.fit_python]
    fit_guess_code = fit_properties[YamlKeys.fit_guess]
    
    try:
        x = list(range(len(fit_parameters)))
        y = list(range(len(fit_parameters)))
        guesses = eval(fit_guess_code)
    except:
        message = "Invalid guesses in Python fit code {0}".format(fit_name)
        logger.error(message)
        raise InvalidFitPythonCode(message)

    try:
        python_fit_code = get_python_fit_code(fit_name, fit_code, fit_parameters)
        exec(python_fit_code)
        fit_function = locals()[fit_name]
        popt, pcov = curve_fit(fit_function, x, y, p0=guesses)
    except:
        message = "Invalid Python fit code in {0}".format(fit_name)
        logger.error(message)
        raise InvalidFitPythonCode(message)

def validate_job(job_name, job_properties, available_fits):
    assert isinstance(job_name, str)
    assert isinstance(job_properties, dict)
    assert isinstance(available_fits, dict)

    # ensure default value and float type for job_valid_time
    if YamlKeys.job_valid_time in job_properties:
        job_properties[YamlKeys.job_valid_time] = float(job_properties[YamlKeys.job_valid_time])
    else:
        job_properties[YamlKeys.job_valid_time] = 0.0

    # validate parameters and types
    error_message = "Unexpected or missing property in job {0}".format(job_name)
    assert required(job_properties, YamlKeys.job_description, str), error_message
    assert required(job_properties, YamlKeys.job_valid_time, float), error_message
    assert optional(job_properties, YamlKeys.job_inherits_from, str), error_message
    assert optional(job_properties, YamlKeys.job_prerequisites, list), error_message
    assert optional(job_properties, YamlKeys.job_scan, dict), error_message
    assert optional(job_properties, YamlKeys.job_parameters, dict), error_message
    assert optional(job_properties, YamlKeys.job_fit, dict), error_message

    if YamlKeys.job_scan in job_properties:
        job_scan = job_properties[YamlKeys.job_scan]

        # convert start and stop to float
        if YamlKeys.job_scan_start in job_scan:
            job_scan[YamlKeys.job_scan_start] = float(job_scan[YamlKeys.job_scan_start])
        if YamlKeys.job_scan_stop in job_scan:
            job_scan[YamlKeys.job_scan_stop] = float(job_scan[YamlKeys.job_scan_stop])

        # validate scan parameters and types
        assert required(job_scan, YamlKeys.job_scan_name, str), error_message
        assert required(job_scan, YamlKeys.job_scan_parameter, str), error_message
        assert required(job_scan, YamlKeys.job_scan_start, float), error_message
        assert required(job_scan, YamlKeys.job_scan_stop, float), error_message
        assert required(job_scan, YamlKeys.job_scan_n_points, int), error_message

    if YamlKeys.job_fit in job_properties:
        job_fit = job_properties[YamlKeys.job_fit]
        
        # validate fit parameters and types
        assert required(job_fit, YamlKeys.job_fit_name, str), error_message
        assert required(job_fit, YamlKeys.job_fit_parameter_source, str), error_message
        assert required(job_fit, YamlKeys.job_fit_parameter_name, str), error_message
        assert required(job_fit, YamlKeys.job_fit_parameter_value, str), error_message

        # validate that specified fit exists
        job_fit_name = job_fit[YamlKeys.job_fit_name]
        assert job_fit_name in available_fits, \
            "Specified fit {0} does not exist for job {1}".format(job_fit_name, job_name)

        # validate that the fit parameter is valid
        job_fit_parameter = job_fit[YamlKeys.job_fit_parameter_value]
        assert job_fit_parameter in available_fits[job_fit_name][YamlKeys.fit_parameters], \
            "Specified fit parameter {0} does not exist in fit {1} for job {1}".format(job_fit_parameter, job_fit_name, job_name)

def validate_yaml(y):
    # validate top-level keys
    fits = y[YamlKeys.fits]
    jobs = y[YamlKeys.jobs]
    assert isinstance(fits, dict), "{0} must be a dict".format(YamlKeys.fits)
    assert isinstance(jobs, dict), "{0} must be a dict".format(YamlKeys.jobs)
    assert len(y) == 2, "Unexpected top-level key found in YAML file"

    # validate properties of each fit
    for name, properties in fits.items():
        validate_fit(name, properties)

    # resolve job inheritance
    for job_name in jobs:
        properties = jobs[job_name]
        while YamlKeys.job_inherits_from in properties:
            inherits_from = properties.pop(YamlKeys.job_inherits_from)
            if inherits_from == job_name:
                message = "{0} inherits from itself".format(job_name)
                logger.error(message)
                raise CircularJobInheritanceError(message)
            logger.info("Resolving inheritance: {0} <- {1}".format(job_name, inherits_from))
            properties = merged_dict(properties, jobs[inherits_from])
        jobs[job_name] = properties

    # resolve prerequisites
    for job_name in jobs:
        prerequisites = collect_and_resolve_prerequisites(job_name, jobs)
        jobs[job_name][YamlKeys.job_prerequisites] = prerequisites

    # validate properties of each fully-resolved job
    for name, properties in jobs.items():
        validate_job(name, properties, fits)

    return y

def load_configuration():
    try:
        yaml_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_calibration.yml")
        logger.info("Loading YAML file: {0}".format(yaml_filename))
        with open(yaml_filename, "r") as yaml_file:
            config_yaml = yaml.safe_load(yaml_file)
    except:
        logger.error("Failed to load YAML file.\n" + traceback.format_exc())
        raise

    try:
        validated_yaml = validate_yaml(config_yaml)
    except:
        logger.error("Failed to validate YAML file.\n" + traceback.format_exc())
        raise

    return validated_yaml

if __name__ == "__main__":
    load_configuration()