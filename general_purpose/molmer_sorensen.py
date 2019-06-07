from pulse_sequence import PulseSequence
from subsequences.doppler_cooling import DopplerCooling
from subsequences.optical_pumping_pulsed import OpticalPumpingPulsed
from subsequences.optical_pumping_continuous import OpticalPumpingContinuous
from subsequences.rabi_excitation import RabiExcitation
from subsequences.sideband_cooling import SidebandCooling
from subsequences.bichro_excitation import BichroExcitation
from subsequences.szx import SZX
from artiq.experiment import *


class MolmerSorensenGate(PulseSequence):
    PulseSequence.accessed_params = {
        "MolmerSorensen.duration",
        "MolmerSorensen.line_selection",
        "MolmerSorensen.line_selection_ion2",
        "MolmerSorensen.due_carrier_enable",
        "MolmerSorensen.selection_sideband",
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
        "MolmerSorensen.shape_profile",
        "MolmerSorensen.bichro_enable",
        "MolmerSorensen.analysis_duration",
        "MolmerSorensen.analysis_amplitude",
        "MolmerSorensen.analysis_att",
        "MolmerSorensen.analysis_amplitude_ion2",
        "MolmerSorensen.analysis_att_ion2",
        "MolmerSorensen.channel_729",
        "MolmerSorensen.ramsey_duration",
        "MolmerSorensen.override_readout"
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
        self.dopplerCooling = self.add_subsequence(DopplerCooling)
        self.opp = self.add_subsequence(OpticalPumpingPulsed)
        self.opc = self.add_subsequence(OpticalPumpingContinuous)
        self.sbc = self.add_subsequence(SidebandCooling)
        self.ms = self.add_subsequence(BichroExcitation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = self.p.MolmerSorensen.channel_729
        self.szx = self.add_subsequence(SZX)
        self.set_subsequence["MolmerSorensen"] = self.set_subsequence_ms
        if not self.p.MolmerSorensen.override_readout:
            ss = self.selected_scan["MolmerSorensen"]
            if self.p.MolmerSorensen.bichro_enable:
                if ss == "MolmerSorensen.ms_phase":
                    self.p.StateReadout.readout_mode = "camera_parity"
                else:
                    self.p.StateReadout.readout_mode = "camera_states"
            else:
                self.p.StateReadout.readout_mode = "camera"

    @kernel
    def set_subsequence_ms(self):
        self.ms.duration = self.get_variable_parameter("MolmerSorensen_duration")
        self.ms.amp = self.get_variable_parameter("MolmerSorensen_amplitude")
        self.ms.amp_ion2 = self.get_variable_parameter("MolmerSorensen_amplitude_ion2")
        self.ms.detuning_carrier_1 = self.get_variable_parameter("MolmerSorensen_detuning_carrier_1")
        self.ms.detuning_carrier_2 = self.get_variable_parameter("MolmerSorensen_detuning_carrier_2")
        self.rabi.phase_729 = self.get_variable_parameter("MolmerSorensen_ms_phase") / 360.
        self.rabi.amp_729 = self.MolmerSorensen_analysis_amplitude
        self.rabi.att_729 = self.MolmerSorensen_analysis_att

    @kernel
    def MolmerSorensen(self):
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
        self.ms.run(self)
        if self.MolmerSorensen_analysis_pulse_enable:
            delay(self.MolmerSorensen_ramsey_duration)
            self.rabi.run(self)
