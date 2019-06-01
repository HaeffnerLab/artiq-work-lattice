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
from subsequences.sideband_cooling import SidebandCooling
from artiq.experiment import *


class RamseyDriftTracker(PulseSequence):
    PulseSequence.accessed_params = {
        "DriftTrackerRamsey.line_1_amplitude",
        "DriftTrackerRamsey.line_1_pi_time",
        "DriftTrackerRamsey.line_1_att",
        "DriftTrackerRamsey.line_2_amplitude",
        "DriftTrackerRamsey.line_2_pi_time",
        "DriftTrackerRamsey.line_2_att",
        "DriftTrackerRamsey.line_selection_1",
        "DriftTrackerRamsey.line_selection_2",
        "DriftTrackerRamsey.gap_time_1",
        "DriftTrackerRamsey.gap_time_2",
        "DriftTrackerRamsey.submit",
        "DriftTrackerRamsey.no_of_readout_2ions",
        "DriftTrackerRamsey.first_run"
    }