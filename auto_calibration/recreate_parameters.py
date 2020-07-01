import labrad
from parse_yaml import *

def recreate_parameters(auto_calibration_yaml):
    cxn = labrad.connect()
    p = cxn.parametervault
    r = cxn.registry
    r.cd("", "Servers", "Parameter Vault")

    collection_name = "AutoCalibration"
    r.mkdir(collection_name)
    r.cd(collection_name)

    calibration_job_parameter_name = "calibration_job"
    calibration_job_registry_value = ("CalibPiTime729G", [job_name for job_name in auto_calibration_yaml[YamlKeys.jobs]])
    r.set(calibration_job_parameter_name, ("selection_simple", calibration_job_registry_value))
    p.reload_parameters()
    print("Successfully created parameter {0}.{1}".format(collection_name, calibration_job_parameter_name))

    cxn.disconnect()

if __name__ == "__main__":
    auto_calibration_yaml = load_configuration()
    recreate_parameters(auto_calibration_yaml)