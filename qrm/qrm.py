from pulse_sequence import PulseSequence
from subsequences.noisy_phase_rabi_excitation import NoisyPhaseRabiExcitation
from subsequences.state_preparation import StatePreparation
from artiq.experiment import *
import numpy as np


class QRM(PulseSequence):
    PulseSequence.accessed_params = {
        "QRM.line_selection",
        "QRM.amplitude_729",
        "QRM.att_729",
        "QRM.channel_729",
        "QRM.duration",
        "QRM.selection_sideband",
        "QRM.delta",
        "QRM.noise_parameter",
        "QRM.nu_eff"
    }

    PulseSequence.scan_params = dict(
        QRM=[
            ("QRM", ("QRM.duration", 0., 100e-6, 20, "us")),
            ("QRM", ("QRM.att_729", 0*dB, 32*dB, 1*dB, "dB"))
        ])

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.qrm = self.add_subsequence(NoisyPhaseRabiExcitation)
        self.qrm.channel_729 = self.p.QRM.channel_729
        self.set_subsequence["QRM"] = self.set_subsequence_qrm
        self.qrm.setup_noisy_single_pass(self)

    def get_random_list(self) -> TList(TFloat):
        rand_list = []
        rand_val = 0
        for _ in range(0, 100):
            rand_val += np.random.randn()
            rand_list.append(rand_val)
        return rand_list

    @kernel
    def set_subsequence_qrm(self):
        self.qrm.duration = self.get_variable_parameter("QRM_duration")
        self.qrm.amp_729 = self.QRM_amplitude_729
        self.qrm.att_729 = self.get_variable_parameter("QRM_att_729")
        self.qrm.freq_729 = self.calc_frequency(
            self.QRM_line_selection, 
            detuning=self.QRM_delta,
            sideband=self.QRM_selection_sideband,
            dds=self.QRM_channel_729
        )
        # self.qrm.noise_list = self.get_random_list()
        # delay(1*ms)
        self.qrm.prepare_noisy(self)

    @kernel
    def QRM(self):
        self.qrm.phase_ref_time = now_mu()
        self.stateprep.run(self)
        self.qrm.run(self)
       

