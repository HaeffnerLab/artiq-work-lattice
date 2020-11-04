from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from subsequences.setup_single_ion_vaet import SetupSingleIonVAET
from artiq.experiment import *
import numpy as np


class SingleIonVAET(PulseSequence):
    PulseSequence.accessed_params = {
        "SingleIonVAET.line_selection",
        "SingleIonVAET.DP_amp",
        "SingleIonVAET.DP_att",
        "SingleIonVAET.J_amp",
        "SingleIonVAET.J_att",
        "SingleIonVAET.delta_amp",
        "SingleIonVAET.delta_att",
        "SingleIonVAET.RSB_amp",
        "SingleIonVAET.RSB_att",
        "SingleIonVAET.BSB_amp",
        "SingleIonVAET.BSB_att",
        "SingleIonVAET.nu_eff",
        "SingleIonVAET.rotate_in_y",
        "SingleIonVAET.rotate_out_y",
        "SingleIonVAET.duration",
        "SingleIonVAET.selection_sideband",
        "SingleIonVAET.line_selection",
        "SingleIonVAET.phase_implemented_sigmay",
        "SingleIonVAET.measured_J",
        "SingleIonVAET.phase_implemented_delta",
        "Rotation729G.amplitude",
        "Rotation729G.att",
        "Rotation729G.pi_time",
        "Rotation729G.line_selection",
    }

    PulseSequence.scan_params = dict(
        SingleIonVAET=[
            ("vaet_time", ("SingleIonVAET.duration", 0., 1000*us, 20, "us")),
            ("scan_nu_eff", ("SingleIonVAET.nu_eff", 0., 1000*kHz, 20, "kHz"))
        ]
    )

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.basis_rotation = self.add_subsequence(RabiExcitation)
        self.vaet = self.add_subsequence(SetupSingleIonVAET)
        self.set_subsequence["SingleIonVAET"] = self.set_subsequence_single_ion_vaet
        if self.p.SingleIonVAET.phase_implemented_sigmay:
            delta = self.p.SingleIonVAET.delta_amp
            J = self.p.SingleIonVAET.J_amp
            self.implemented_phase = np.arctan(2 * delta / J) / (2 * np.pi)
            self.implemented_amp = np.sqrt(J**2 + delta**2)
        else:
            self.implemented_amp = 0.
            self.implemented_phase = 0.

    @kernel
    def set_subsequence_single_ion_vaet(self):
        self.vaet.duration = self.get_variable_parameter("SingleIonVAET_duration")
        self.vaet.nu_eff = self.get_variable_parameter("SingleIonVAET_nu_eff")
        if self.SingleIonVAET_phase_implemented_sigmay:
            self.vaet.implemented_phase = self.implemented_phase
            self.vaet.implemented_amp = self.implemented_amp
        self.basis_rotation.amp_729 = self.Rotation729G_amplitude
        self.basis_rotation.att_729 = self.Rotation729G_att
        self.basis_rotation.duration = self.Rotation729G_pi_time / 2
        self.basis_rotation.freq_729 = self.calc_frequency(
            self.Rotation729G_line_selection,
            dds="729G"
        )

    @kernel
    def SingleIonVAET(self):
        self.basis_rotation.phase_ref_time = now_mu()
        self.vaet.phase_ref_time = self.basis_rotation.phase_ref_time

        #setting up a ref rf for testing phase
        self.dds_SP_729L1_bichro.set(80.3*MHz, amplitude=0.6, phase=0.314, ref_time_mu=self.basis_rotation.phase_ref_time)
        self.dds_SP_729L1_bichro.set_att(5*dB)

        self.stateprep.run(self)
       
        self.dds_SP_729L1_bichro.sw.on()
         
        if self.SingleIonVAET_rotate_in_y:
            self.basis_rotation.phase_729 = 0.
            self.basis_rotation.run(self)
        self.vaet.run(self)
        if self.SingleIonVAET_rotate_out_y:
            self.basis_rotation.phase_729 = 180.
            self.basis_rotation.run(self)

        self.dds_SP_729L1_bichro.sw.off()