from pulse_sequence import PulseSequence
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from subsequences.bichro_excitation import BichroExcitation
from artiq.experiment import *


class VAET(PulseSequence):
    PulseSequence.accessed_params = {
        "VAET.duration",
        "VAET.rotate_out",
        "VAET.rotate_in",
        "SZX.line_selection",
        "SZX.sideband_selection",
        "SZX.bichro_enable",
        "SZX.amplitude",
        "SZX.att",
        "SZX.amp_blue",
        "SZX.att_blue",
        "SZX.amp_red",
        "SZX.att_red",
        "SZX.nu_effective",
        "SZX.carrier_detuning",
        "SZX.post_local_rotation",
        "SZX.calibration_offset",
        "SZX.local_rabi_amp",
        "SZX.local_rabi_att",
        "MolmerSorensen.line_selection",
        "MolmerSorensen.line_selection_ion2",
        "MolmerSorensen.due_carrier_enable",
        "MolmerSorensen.sideband_selection",
        "MolmerSorensen.detuning",
        "MolmerSorensen.amp_red",
        "MolmerSorensen.att_red",
        "MolmerSorensen.amp_blue",
        "MolmerSorensen.att_blue",
        "MolmerSorensen.amplitude",
        "MolmerSorensen.att",
        "MolmerSorensen.amplitude_ion2",
        "MolmerSorensen.att_ion2",
        "MolmerSorensen.analysis_pulse_enable",
        "MolmerSorensen.SDDS_enable",
        "MolmerSorensen.SDDS_rotate_out",
        "MolmerSorensen.bichro_enable",
        "MolmerSorensen.analysis_duration",
        "MolmerSorensen.analysis_amplitude",
        "MolmerSorensen.analysis_att",
        "MolmerSorensen.analysis_amplitude_ion2",
        "MolmerSorensen.analysis_att_ion2",
        "MolmerSorensen.detuning_carrier_1",
        "MolmerSorensen.detuning_carrier_2",
        "MolmerSorensen.ramsey_duration",
        "VAET.ramsey_time"
    }

    PulseSequence.scan_params.update(
        VAET=[
            ("vaet_time", ("VAET.vaet_duration", 0, 50*us, 25, "us")),
            ("vaet_time", ("VAET.rabi_duration", 0, 50*us, 25, "us")),
            ("scan_nu_eff", ("SZX.nu_effective", -10*kHz, 10*kHz, 25, "kHz")),
            ("vaet_time", ("SZX.carrier_detuning", -1*MHz, 1*MHz, 25, "MHz")),
            ("vaet_parity", ("VAET.ramsey_time", 0, 1*ms, 25, "ms"))

        ]
    )

    def run_initially(self):
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opp = self.add_subsequence(OpticalPumpingPulsed)
        self.opc = self.add_subsequence(OpticalPumpingContinuous)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.ms = self.add_subsequence(BichroExcitation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.set_subsequence["VAET"] = self.set_subsequence_vaet

    @kernel
    def set_subsequence_vaet(self):
        pass

    @kernel
    def VAET(self):
        delay(1*ms)
        self.dopplerCooling.run(self)
        if self.StatePreparation_pulsed_optical_pumping:
            self.opp.run(self)
        elif self.StatePreparation_optical_pumping_enable:
            self.opc.run(self)
        if self.StatePreparation_sideband_cooling_enable:
            self.sbc.run(self)
            if self.StatePreparation_pulsed_optical_pumping:
                self.opp.run(self)
            elif self.StatePreparation_optical_pumping_enable:
                self.opc.run(self)