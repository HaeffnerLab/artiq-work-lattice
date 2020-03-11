from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from subsequences.bichro_excitation import BichroExcitation
from subsequences.szx import SZX
from artiq.experiment import *

class VAET(PulseSequence):
    PulseSequence.accessed_params = {
        "VAET.vaet_duration",
        "VAET.rabi_duration",
        "VAET.rotate_out",
        "VAET.rotate_in",
        "SZX.one_ion_vaet",
        "SZX.line_selection",
        "SZX.sideband_selection",
        "SZX.bichro_enable",
        "SZX.AC_stark_local",
        "SZX.amplitude_L2",
        "SZX.att_L2",
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
        self.stateprep = self.add_subsequence(StatePreparation)
        self.ms = self.add_subsequence(BichroExcitation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.szx = self.add_subsequence(SZX)
        self.set_subsequence["VAET"] = self.set_subsequence_vaet

    @kernel
    def set_subsequence_vaet(self):
        self.szx.duration = self.get_variable_parameter("VAET_vaet_duration")
        self.ms.duration = self.get_variable_parameter("VAET_rabi_duration")
        self.szx.nu_effective = self.get_variable_parameter("SZX_nu_effective")
        self.szx.carrier_detuning = self.get_variable_parameter("SZX_carrier_detuning")
        #self.vaet.parity = self.get_variable_parameter("VAET_ramsey_time")
        
        # Comment out this line of code to disable ramping for VAET
        #self.szx.setup_ramping(self)

        # "SZX.amplitude",
        # "SZX.att",
        # "SZX.amp_blue",
        # "SZX.att_blue",
        # "SZX.amp_red",
        # "SZX.att_red",
        # "SZX.nu_effective",
        # "SZX.carrier_detuning",
        # "SZX.post_local_rotation",
        # "SZX.calibration_offset",
        # "SZX.local_rabi_amp",
        # "SZX.local_rabi_att",
        # "MolmerSorensen.detuning",
        # "MolmerSorensen.amp_red",
        # "MolmerSorensen.att_red",
        # "MolmerSorensen.amp_blue",
        # "MolmerSorensen.att_blue",
        # "MolmerSorensen.amplitude",
        # "MolmerSorensen.att",
        # "MolmerSorensen.amplitude_ion2",
        # "MolmerSorensen.att_ion2",
        # "MolmerSorensen.analysis_pulse_enable",
        # "MolmerSorensen.SDDS_enable",
        # "MolmerSorensen.SDDS_rotate_out",
        # "MolmerSorensen.bichro_enable",
        # "MolmerSorensen.analysis_duration",
        # "MolmerSorensen.analysis_amplitude",
        # "MolmerSorensen.analysis_att",
        # "MolmerSorensen.analysis_amplitude_ion2",
        # "MolmerSorensen.analysis_att_ion2",
        # "MolmerSorensen.detuning_carrier_1",
        # "MolmerSorensen.detuning_carrier_2",
        # "MolmerSorensen.ramsey_duration",
        # "VAET.ramsey_time"
        

    @kernel
    def VAET(self):
        self.stateprep.run(self)
        self.szx.run(self)
        