import copy
import logging
import traceback
import yaml

logger = logging.getLogger("auto_calibration")
log_level = logging.DEBUG
logger.setLevel(log_level)

ch = logging.StreamHandler()
ch.setLevel(log_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class CircularJobInheritanceError(Exception): pass
class CircularJobPrerequisiteError(Exception): pass

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
    if "prerequisites" in all_jobs[job_name]:
        prerequisites = collect_prerequisites(prerequisites, all_jobs[job_name]["prerequisites"], all_jobs)
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
        if "prerequisites" in all_jobs[prerequisite_job_name]:
            # TODO: Fix infinite recursion in some cases
            prerequisites = collect_prerequisites(prerequisites, all_jobs[prerequisite_job_name]["prerequisites"], all_jobs)

    return prerequisites

def resolve_prerequisites(original_job_name, prerequisites, all_jobs):
    assert isinstance(original_job_name, str)
    assert isinstance(prerequisites, list)
    assert isinstance(all_jobs, dict)

    # ensure we don't have a blatant circular dependency
    if original_job_name in prerequisites:
        logger.error("{0} has itself as a prerequisite. Full list of prerequisites: {1}".format(original_job_name, prerequisites))
        raise CircularJobPrerequisiteError()

    # don't modify the original list
    prerequisites = copy.deepcopy(prerequisites)

    # make repeated passes through the list to try to find a good order
    done = False
    pass_count = 0
    while not done:
        pass_count = pass_count + 1

        # Unless we have an enormous number of job definitions, we should never have to make this many passes.
        if pass_count > 1000:
            logger.error("Unable to resolve prerequisites for {0}. Possible circular dependency? Full list of prerequisites: {1}".format(original_job_name, prerequisites))
            raise CircularJobPrerequisiteError()

        # Find any job that is listed before its prerequisites.
        move_to_end = []
        for job_index, job_name in enumerate(prerequisites):
            if "prerequisites" in all_jobs[job_name]:
                for prerequisite_job_name in all_jobs[job_name]["prerequisites"]:
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

def validate_fit(fit_name, fit_properties):
    # TODO: validate types of each parameter (dict vs. list vs. string)
    # TODO: validate that required parameters exist
    # TODO: validate/execute Python fit function?
    pass

def validate_job(job_name, job_properties, available_fit_names):
    # TODO: validate types of each parameter (dict vs. list vs. string)
    # TODO: validate that required parameters exist
    # TODO: validate that specified fit exists for each job
    pass

def validate_resolved_job(job_name, job_properties, available_fit_names):
    validate_job(job_name, job_properties, available_fit_names)
    # TODO: validate types of each parameter (dict vs. list vs. string)
    # TODO: validate that required parameters exist
    # TODO: validate that specified fit exists for each job
    pass

def validate_yaml(y):
    # validate top-level keys
    fits = y["fits"]
    jobs = y["jobs"]
    assert isinstance(fits, dict), "fits must be a dict"
    assert isinstance(jobs, dict), "jobs must be a dict"
    assert len(y) == 2, "Unexpected top-level key found in YAML file"

    # validate properties of each fit
    for name, properties in fits.items():
        validate_fit(name, properties)
        
    # validate properties of each job
    for name, properties in jobs.items():
        validate_job(name, properties, fits.keys())

    # resolve job inheritance
    for job_name in jobs:
        properties = jobs[job_name]
        while "inherits-from" in properties:
            inherits_from = properties.pop("inherits-from")
            if inherits_from == job_name:
                logger.error("{0} inherits from itself".format(job_name))
                raise CircularJobInheritanceError()
            logger.info("Resolving inheritance: {0} <- {1}".format(job_name, inherits_from))
            properties = merged_dict(properties, jobs[inherits_from])
        jobs[job_name] = properties

    # resolve prerequisites
    for job_name in jobs:
        prerequisites = collect_and_resolve_prerequisites(job_name, jobs)
        jobs[job_name]["prerequisites"] = prerequisites

    # validate properties of each fully-resolved job
    for name, properties in jobs.items():
        validate_resolved_job(name, properties, fits.keys())

if __name__ == "__main__":
    try:
        yaml_filename = "auto_calibration.yml"
        logger.info("Loading YAML file: {0}".format(yaml_filename))
        with open(yaml_filename, "r") as yaml_file:
            config_yaml = yaml.safe_load(yaml_file)
    except:
        logger.error("Failed to load YAML file.\n" + traceback.format_exc())
        exit()

    try:
        validate_yaml(config_yaml)
    except:
        logger.error("Failed to validate YAML file.\n" + traceback.format_exc())
        exit()