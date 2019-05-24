import numpy as np
import labrad
import artiq.dashboard.drift_tracker.client_config as cl
from labrad.units import WithUnit as U 
from scipy.optimize import curve_fit
from pulse_sequence import PulseSequence, FitError
from subsequences.repump_D import RepumpD
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.rabi_excitation import RabiExcitation
from artiq.experiment import *


class CalibAllSidebands(PulseSequence):
    PulseSequence.accessed_params.update(
        {"CalibrationScans.calibration_channel_729",
         "CalibrationScans.sideband_calibration_amp",
         "CalibrationScans.sideband_calibration_att",
         "Spectrum.manual_excitation_time",
         "CalibrationScans.sideband_calibration_line",
         "Display.relative_frequencies",
         "CalibrationScans.readout_mode"}
    )

    def run_initially(self):
        pass