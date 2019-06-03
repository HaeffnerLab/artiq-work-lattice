from pulse_sequence import PulseSequence
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from subsequences.bichro_excitation import BichroExcitation
from artiq.experiment import *


class MolmerSorensenGate(PulseSequence):
    PulseSequence.accessed_params = {
        "MolmerSorensen.duration",
        "MolmerSorensen.line_selection",
        "MolmerSorensen.line_selection_ion2",
        "MolmerSorensen.due_carrier_enable",
        "MolmerSorensen.sideband_selection",
        "MolmerSorensen.detuning",
        "MolmerSorensen.amp_red",
        "MolmerSorensen.amp_blue",
        "MolmerSorensen.amplitude",
        "MolmerSorensen.amplitude_ion2",
        "MolmerSorensen.analysis_pulse_enable",
        "MolmerSorensen.SDDS_enable",
        "MolmerSorensen.SDDS_rotate_out",
        "MolmerSorensen.shape_profile",
        "MolmerSorensen.bichro_enable",
        "MolmerSorensen.analysis_duration",
        "MolmerSorensen.analysis_amplitude",
    }

    PulseSequence.scan_params.update(
        MolmerSorensen=[
            ("Molmer-Sorensen", ("MolmerSorensen.duration", 0., 400*us, 20, "us")),
            ("Molmer-Sorensen", ("MolmerSorensen.amplitude", 0., 1., 20)),
            ("Molmer-Sorensen", ("MolmerSorensen.amplitude_ion2", 0., 1., 20)),
            ("Molmer-Sorensen", ("MolmerSorensen.detuning_carrier_1", -10*kHz, 10*kHz, 20, "kHz")),
            ("Molmer-Sorensen", ("MolmerSorensen.detuning_carrier_2", -10*kHz, 10*kHz, 20, "kHz")),
            ("Molmer-Sorensen", ("MolmerSorensen.ms_phase", 0., 360., 20, "deg")),
        ]
    )

    def run_initially(self):
        pass

    @kernel
    def set_subsequence_ms(self):
        pass