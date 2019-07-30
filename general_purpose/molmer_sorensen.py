from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from subsequences.bichro_excitation import BichroExcitation
from subsequences.szx import SZX
import numpy as np
from artiq.experiment import *
#from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE

class MolmerSorensenGate(PulseSequence):
    PulseSequence.accessed_params = {
        "MolmerSorensen.duration",
        "MolmerSorensen.line_selection",
        "MolmerSorensen.line_selection_ion2",
        "MolmerSorensen.due_carrier_enable",
        "MolmerSorensen.selection_sideband",
        "MolmerSorensen.detuning",
        "MolmerSorensen.detuning_carrier_1",
        "MolmerSorensen.detuning_carrier_2",
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
        "MolmerSorensen.override_readout",
        "MolmerSorensen.ms_phase"
    }

    PulseSequence.scan_params.update(
        MolmerSorensen=[
            ("Molmer-Sorensen", ("MolmerSorensen.duration", 0., 400*us, 20, "us")),
            ("Molmer-Sorensen", ("MolmerSorensen.amplitude", 0., 1., 20)),
            ("Molmer-Sorensen", ("MolmerSorensen.amplitude_ion2", 0., 1., 20)),
            ("Molmer-Sorensen", ("MolmerSorensen.detuning_carrier_1", -10*kHz, 10*kHz, 20, "kHz")),
            ("Molmer-Sorensen", ("MolmerSorensen.detuning_carrier_2", -10*kHz, 10*kHz, 20, "kHz")),
            ("Molmer-Sorensen", ("MolmerSorensen.ramsey_duration", 0., 2*ms, 40, "ms")),
            ("Molmer-Sorensen", ("MolmerSorensen.ms_phase", 0., 360., 20, "deg")),
        ]
    )

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.ms = self.add_subsequence(BichroExcitation)
        self.rabi = self.add_subsequence(RabiExcitation)
        self.rabi.channel_729 = "729G"
        self.phase_ref_time = np.int64(-1)
        self.szx = self.add_subsequence(SZX)
        self.set_subsequence["MolmerSorensen"] = self.set_subsequence_ms
        if not self.p.MolmerSorensen.override_readout:#
            ss = self.selected_scan["MolmerSorensen"]
            if self.p.MolmerSorensen.bichro_enable:
                if ss == "MolmerSorensen.ms_phase" or ss == "MolmerSorensen.ramsey_duration":
                    self.p.StateReadout.readout_mode = "camera_parity"
                else:
                    self.p.StateReadout.readout_mode = "camera_states"
            else:
                self.p.StateReadout.readout_mode = "camera"

    @kernel
    def set_subsequence_ms(self):
        self.phase_ref_time = now_mu()
        self.ms.phase_ref_time = self.phase_ref_time
        self.rabi.phase_ref_time = self.phase_ref_time

        self.ms.duration = self.get_variable_parameter("MolmerSorensen_duration")
        self.ms.amp = self.get_variable_parameter("MolmerSorensen_amplitude")
        self.ms.amp_ion2 = self.get_variable_parameter("MolmerSorensen_amplitude_ion2")
        self.ms.detuning_carrier_1 = self.get_variable_parameter("MolmerSorensen_detuning_carrier_1")
        self.ms.detuning_carrier_2 = self.get_variable_parameter("MolmerSorensen_detuning_carrier_2")
        self.rabi.phase_729 = self.get_variable_parameter("MolmerSorensen_ms_phase")
        self.rabi.amp_729 = self.MolmerSorensen_analysis_amplitude
        self.rabi.att_729 = self.MolmerSorensen_analysis_att
        self.rabi.duration = self.MolmerSorensen_analysis_duration
        self.rabi.freq_729 = self.calc_frequency(
            self.MolmerSorensen_line_selection, 
            detuning=self.ms.detuning_carrier_1,
            dds="729G"
        )
    @kernel
    def MolmerSorensen(self):
        self.stateprep.run(self)
        self.ms.run(self)
        if self.MolmerSorensen_analysis_pulse_enable:
            delay(self.get_variable_parameter("MolmerSorensen_ramsey_duration"))
            self.rabi.run(self)

            # self.get_729_dds(self.rabi.channel_729)
            # self.dds_729.set_phase_mode(PHASE_MODE_ABSOLUTE)
            # self.dds_729.set(self.rabi.freq_729,
            #                 amplitude=self.rabi.amp_729,
            #                 phase=self.get_variable_parameter("MolmerSorensen_ms_phase") / 360.)

            # freq_729_SP = 80*MHz + self.get_offset_frequency(self.rabi.channel_729)
            # self.dds_729_SP.set_phase_mode(PHASE_MODE_ABSOLUTE)
            # self.dds_729_SP.set(freq_729_SP, phase=0.)
            
            # with parallel:
            #     self.dds_729.sw.on()
            #     self.dds_729_SP.sw.on()
            # delay(self.rabi.duration)
            # with parallel:
            #     self.dds_729.sw.off()
            #     self.dds_729_SP.sw.off()
            
            # self.dds_729.set_phase_mode(PHASE_MODE_TRACKING)
            # self.dds_729_SP.set_phase_mode(PHASE_MODE_TRACKING)
