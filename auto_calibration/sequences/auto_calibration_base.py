from pulse_sequence import PulseSequence
from artiq.experiment import *
import logging

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