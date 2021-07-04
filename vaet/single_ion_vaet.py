from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from subsequences.setup_single_ion_vaet import SetupSingleIonVAET
from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_RAMPUP
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
        "SingleIonVAET.delta_phase",
        "SingleIonVAET.noise_amp",
        "SingleIonVAET.noise_att",
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
        "SingleIonVAET.test_phase",
        "SingleIonVAET.with_noise",
        "SingleIonVAET.noise_type",
        "SingleIonVAET.amplitude_noise_depth",
        "SingleIonVAET.frequency_noise_strength"
    }

    PulseSequence.scan_params = dict(
        SingleIonVAET=[
            ("vaet_time", ("SingleIonVAET.duration", 0., 1000*us, 20, "us")),
            ("scan_nu_eff", ("SingleIonVAET.nu_eff", 0., 1000*kHz, 20, "kHz")),
            ("scan_nu_eff",("SingleIonVAET.delta_amp", 0.05, 0.25, 20)),
            ("scan_nu_eff",("SingleIonVAET.test_phase", 0, 360, 20)),
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

        n = 1024
        m = int(self.p.StateReadout.repeat_each_measurement)
        self.mod_wf1 = [np.zeros(n) for i in range(m)]
        self.mod_wf2 = [np.zeros(n) for i in range(m)]
        if self.p.SingleIonVAET.with_noise:
            self.setup_noise_waveforms(n, m)

    @kernel
    def set_subsequence_single_ion_vaet(self):
        self.vaet.duration = self.get_variable_parameter("SingleIonVAET_duration")
        self.vaet.nu_eff = self.get_variable_parameter("SingleIonVAET_nu_eff")
        self.vaet.delta_amp = self.get_variable_parameter("SingleIonVAET_delta_amp")
        self.vaet.test_phase = self.get_variable_parameter("SingleIonVAET_test_phase")
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

        trap_frequency = self.get_trap_frequency(self.SingleIonVAET_selection_sideband)
        offset = self.get_offset_frequency("729G")
        nu_eff = self.vaet.nu_eff
        self.vaet.freq_blue = 80*MHz + trap_frequency + nu_eff + offset
        self.vaet.freq_red = 80*MHz - trap_frequency - nu_eff + offset

        self.basis_rotation.phase_ref_time = now_mu()

    @kernel
    def SingleIonVAET(self):
        self.basis_rotation.phase_ref_time = 0
        self.vaet.phase_ref_time = self.basis_rotation.phase_ref_time
        self.stateprep.run(self)
        if self.SingleIonVAET_rotate_in_y:
            self.basis_rotation.phase_729 = 0.
            self.basis_rotation.run(self)
        self.vaet.run(self)
        if self.SingleIonVAET_rotate_out_y:
            self.basis_rotation.phase_729 = 180.
            self.basis_rotation.run(self)

    def run_finally(self):
        self.stop_ram_modulation(self.dds_729_SP)

    def setup_noise_waveforms(self, n, m):
        noise_time_step = 2*us  # 1/sampling rate
        self.vaet.step = round(noise_time_step / 4*ns)
        noise_type = self.p.SingleIonVAET.noise_type
        rng = np.random.default_rng()
        if noise_type in ["white_delta", "lorentzian_delta"]:
            std = self.p.SingleIonVAET.amplitude_noise_depth
            delta = self.p.SingleIonVAET.delta_amp
            J = self.p.SingleIonVAET.J_amp
            for i in range(m):
                if noise_type == "white_delta":
                    d = std * rng.standard_normal(n) + delta
                elif noise_type == "lorentzian_delta":
                    d = std * rng.standard_cauchy(n) + delta
                d[d > 1] = 1.
                d[d < 0] = 0.
                amp_wf = np.arctan(2 * d / J) / (2 * np.pi)
                phase_wf = np.sqrt(J*2 + d**2)
                self.mod_wf1[i] = self.dds_729.amplitude_to_ram(amp_wf.tolist(), [0]*1024)
                self.mod_wf2[i] = phase_wf.tolist()
        elif noise_type in ["white_nu_eff", "lorentzian_nu_eff"]:
            std = self.p.SingleIonVAET.frequency_noise_strength
            for i in range(m):
                if noise_type == "white_nu_eff":
                    noise_wf = std * rng.standard_normal(n)
                    blue_wf = self.vaet.freq_blue + noise_wf
                    red_wf = self.vaet.freq_red - noise_wf
                elif noise_type == "lorentzian_nu_eff":
                    blue_wf = self.vaet.freq_blue + std * rng.standard_cauchy(n)
                    red_wf = self.vaet.freq_red - std * rng.standard_cauchy(n)
                self.mod_wf1[i] = blue_wf.tolist()
                self.mod_wf2[i] = red_wf.tolist()
