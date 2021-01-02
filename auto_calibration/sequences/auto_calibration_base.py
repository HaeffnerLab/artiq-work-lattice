import logging

from artiq.experiment import *
from auto_calibration.auto_calibration_experiment import AutoCalibrationManager
from pulse_sequence import PulseSequence

logger = logging.getLogger(__name__)

###############################################################
# Base pulse sequence for AutoCalibration jobs
###############################################################

class AutoCalibrationSequence(PulseSequence):

    def run_finally(self):
        scan_name = list(PulseSequence.scan_params.keys())[0]
        x = self.data[scan_name].x
        y = self.data[scan_name].y[-1]
        logger.info("x: {0}".format(x))
        logger.info("y: {0}".format(y))

        AutoCalibrationManager().save(scan_name, x, y, self.start_time)
