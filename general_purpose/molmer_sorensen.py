from pulse_sequence import PulseSequence
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from subsequences.bichro_excitation import BichroExcitation
from artiq.experiment import *


class MotionalAnalysisSpectrum(PulseSequence):
    PulseSequence.accessed_params = {}