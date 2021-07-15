from pulse_sequence import PulseSequence
from subsequences.rabi_excitation import RabiExcitation
from subsequences.state_preparation import StatePreparation
from subsequences.setup_single_ion_vaet import SetupSingleIonVAET
from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_RAMPUP, RAM_MODE_CONT_RAMPUP
import numpy as np


class SingleIonVAET(PulseSequence):
    PulseSequence.accessed_params = {
        "SingleIonVAET.line_selection",
        "SingleIonVAET.DP_amp",
        "SingleIonVAET.DP_att",
        "SingleIonVAET.CARR_att",
        "SingleIonVAET.J",
        "SingleIonVAET.delta",
        "SingleIonVAET.RSB_amp",
        "SingleIonVAET.RSB_att",
        "SingleIonVAET.BSB_amp",
        "SingleIonVAET.BSB_att",
        "SingleIonVAET.nu_eff",
        "SingleIonVAET.lorentzian_width",
        "SingleIonVAET.lorentzian_center",
        "SingleIonVAET.noise_rolloff",
        "SingleIonVAET.rotate_in_y",
        "SingleIonVAET.rotate_out_y",
        "SingleIonVAET.duration",
        "SingleIonVAET.selection_sideband",
        "SingleIonVAET.line_selection",
        "Rotation729G.amplitude",
        "Rotation729G.att",
        "Rotation729G.pi_time",
        "Rotation729G.line_selection",
        "SingleIonVAET.with_noise",
        "SingleIonVAET.noise_type",
        "SingleIonVAET.amplitude_noise_depth",
        "SingleIonVAET.frequency_noise_strength"
    }

    PulseSequence.scan_params = dict(
        SingleIonVAET=[
            ("vaet_time", ("SingleIonVAET.duration", 0., 1000*us, 20, "us")),
            ("scan_nu_eff", ("SingleIonVAET.nu_eff", 0., 1000*kHz, 20, "kHz")),
            ("scan_nu_eff", ("SingleIonVAET.delta", 0.05, 0.25, 20)),
        ]
    )

    ###########
    # nu_eff / delta scans currently not working with noise implementation
    ###########

    def run_initially(self):
        self.stateprep = self.add_subsequence(StatePreparation)
        self.basis_rotation = self.add_subsequence(RabiExcitation)
        self.vaet = self.add_subsequence(SetupSingleIonVAET)
        self.set_subsequence["SingleIonVAET"] = self.set_subsequence_single_ion_vaet
        self.vaet.with_noise = bool(self.p.SingleIonVAET.with_noise)

        n = 1024
        m = int(self.p.StateReadout.repeat_each_measurement)
        self.vaet.mod_wf = [np.int32([0])]
        self.vaet.mod_wf2 = [np.int32([0])]
        trap_frequency = self.p.TrapFrequencies[self.p.SingleIonVAET.selection_sideband]
        offset = self.get_offset_frequency("729G")
        nu_eff = self.p.SingleIonVAET.nu_eff
        self.vaet.freq_blue = 80*MHz + trap_frequency + nu_eff + offset
        self.vaet.freq_red = 80*MHz - trap_frequency - nu_eff + offset
        if self.p.SingleIonVAET.with_noise:
            self.setup_noise_waveforms(n, m)

    @kernel
    def set_subsequence_single_ion_vaet(self):
        self.vaet.duration = self.get_variable_parameter("SingleIonVAET_duration")
        self.vaet.nu_eff = self.get_variable_parameter("SingleIonVAET_nu_eff")
        delta = self.get_variable_parameter("SingleIonVAET_delta")
        J = self.SingleIonVAET_J
        self.vaet.CARR_phase = np.arctan(2 * delta / J) / (2 * np.pi)
        self.vaet.CARR_amp = np.sqrt(J**2 + delta**2) / np.sqrt(2.)
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

        if self.vaet.with_noise:
            j = round(self.get_variable_parameter("current_experiment_iteration"))
            if self.vaet.noise_type == "white_delta" or self.vaet.noise_type == "lorentzian_delta":
                self.setup_ram_modulation(
                                    0,  # hard coded to self.dds_729_SP
                                    ram_waveform=self.vaet.mod_wf[j],
                                    modulation_type=self.AMP_PHASE_MOD,
                                    step=self.vaet.step,
                                    ram_mode=RAM_MODE_CONT_RAMPUP
                                )
            else:
                self.setup_ram_modulation(
                                    1,  # hard coded to self.dds_SP_729G_bichro
                                    ram_waveform=self.vaet.mod_wf[j],
                                    modulation_type=self.FREQ_MOD,
                                    step=self.vaet.step,
                                    ram_mode=RAM_MODE_CONT_RAMPUP
                                )
                self.setup_ram_modulation(
                                    2,  # hard coded to self.dds_SP_729L1
                                    ram_waveform=self.vaet.mod_wf2[j],
                                    modulation_type=self.FREQ_MOD,
                                    step=self.vaet.step,
                                    ram_mode=RAM_MODE_CONT_RAMPUP
                                )

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
        self.vaet.step = int(float(noise_time_step) // float(4*ns))
        noise_type = self.p.SingleIonVAET.noise_type
        if "delta" in noise_type:
            self.vaet.amplitude_noise = True
        else:
            self.vaet.amplitude_noise = False

        if self.vaet.amplitude_noise:
            strength = self.p.SingleIonVAET.amplitude_noise_depth
            delta = self.p.SingleIonVAET.delta
            y = self.p.SingleIonVAET.lorentzian_width
            f0 = self.p.SingleIonVAET.lorentzian_center
            rolloff = self.p.SingleIonVAET.noise_rolloff
            J = self.p.SingleIonVAET.J
            for i in range(m):
                ram_wf = [0] * n
                if noise_type == "white_delta":
                    _, _, d = generate_white_noise(
                                            strength, samples=n,
                                            samplerate=1/noise_time_step,
                                            min_value=-delta, max_value=1 - delta,
                                            # min_freq=-250e3, max_freq=250e3,
                                            just_phase=False
                                        )
                elif noise_type == "lorentzian_delta":
                    _, _, d = generate_lorentzian_noise(
                                            strength, f0, y, 
                                            samples=n,
                                            samplerate=1/noise_time_step,
                                            min_value=-delta, max_value=1 - delta,
                                            # min_freq=-250e3, max_freq=250e3,
                                            just_phase=False
                                        )
                elif noise_type == "pink_delta":
                    _, _, d = generate_pink_noise(
                                            strength, amp_rolloff, 
                                            samples=n,
                                            samplerate=1/noise_time_step,
                                            min_value=-delta, max_value=1 - delta,
                                            # min_freq=-250e3, max_freq=250e3,
                                            just_phase=False
                                        )
                elif noise_type == "brown_delta":
                    _, _, d = generate_brown_noise(
                                            strength, amp_rolloff, 
                                            samples=n,
                                            samplerate=1/noise_time_step,
                                            min_value=-delta, max_value=1 - delta,
                                            # min_freq=-250e3, max_freq=250e3,
                                            just_phase=False
                                        )
                d = d + delta
                amp_wf = np.arctan(2 * d / J) / (2 * np.pi)
                phase_wf = np.sqrt(J**2 + d**2) / np.sqrt(2.)
                self.turns_amplitude_to_ram(phase_wf, amp_wf, ram_wf)
                self.vaet.mod_wf.append(np.int32(ram_wf))
        else:  # scans of nu_eff are currently not supported with vu_eff noise
            for i in range(m):
                strength = self.p.SingleIonVAET.frequency_noise_strength
                ram_wf_blue = [0] * n
                ram_wf_red = [0] * n
                frequency_bandwidth = 750*MHz
                if noise_type == "white_nu_eff":
                    _, _, d = generate_white_noise(
                                                strength, samples=n,
                                                samplerate=1/noise_time_step,
                                                min_value=-frequency_bandwidth, 
                                                max_value=frequency_bandwidth,
                                                # min_freq=-750e3, max_freq=750e3,
                                                just_phase=False
                                            )
                    blue_wf = self.vaet.freq_blue + d
                    red_wf = self.vaet.freq_red - d
                elif noise_type == "lorentzian_nu_eff":
                    pass
                elif noise_type == "pink_nu_eff":
                    pass
                elif noise_type == "brown_nu_eff":
                    pass
                self.frequency_to_ram(blue_wf, ram_wf_blue)
                self.frequency_to_ram(red_wf, ram_wf_red)
                self.vaet.mod_wf.append(np.int32(ram_wf_blue))
                self.vaet.mod_wf2.append(np.int32(ram_wf_red))
        # elif noise_type in ["white_nu_eff", "lorentzian_nu_eff"]:
        #     std = self.p.SingleIonVAET.frequency_noise_strength
        #     for i in range(m):
        #         if noise_type == "white_nu_eff":
        #             noise_wf = std * rng.standard_normal(n)
        #             blue_wf = self.vaet.freq_blue + noise_wf
        #             red_wf = self.vaet.freq_red - noise_wf 
        #         elif noise_type == "lorentzian_nu_eff":
        #             blue_wf = self.vaet.freq_blue + std * rng.standard_cauchy(n)
        #             red_wf = self.vaet.freq_red - std * rng.standard_cauchy(n)
        #         ram_wf_blue = [0] * n
        #         self.frequency_to_ram(blue_wf, ram_wf_blue)
        #         ram_wf_red = [0] * n
        #         self.frequency_to_ram(red_wf, ram_wf_red)
        #         self.vaet.mod_wf.append(np.int32(ram_wf_blue))
        #         self.vaet.mod_wf2.append(np.int32(ram_wf_red))


def fftnoise(f, just_phase=False):
    # adapted from frank-zalkow's Stack Overflow answer
    # https://stackoverflow.com/questions/33933842/how-to-generate-noise-in-frequency-range-with-numpy
    assert len(f) % 2 == 0  # let's just work with even sample sizes for now
    f = np.array(np.sqrt(f), dtype="complex")
    Np = (len(f) - 1) // 2
    rng = np.random.default_rng()
    if just_phase:
        phases = np.exp(2j * np.pi * rng.uniform(size=Np))
        f[1:Np+1] *= phases
        f[-1:-(1 + Np):-1] = np.conj(f[1:Np+1])
    else:
        reals = rng.standard_normal(Np) / np.sqrt(2)
        ims = rng.standard_normal(Np) / np.sqrt(2)
        f[1:Np+1] *= (reals + 1j * ims)
        f[Np+1] *= rng.standard_normal() / np.sqrt(2)  # Nyquist frequency must be real for even sample sizes
        f[-1:-(1 + Np):-1] = np.conj(f[1:Np+1])
    fft = np.fft.ifft(f, norm="ortho").real 
    fft[0] = 0 # zero-mean
    return fft

def lorentzian(f, std, f0, y):
    return (std * y)**2 / ((f - f0)**2 + y**2)

def pink(f, std, rolloff=0):
    f1 = np.abs(f)
    indx1 = np.where(f1 <= rolloff)
    indx2 = np.where(f1 > rolloff)
    f1[indx1] = std**2
    f1[indx2] = std**2 * min(f1[indx2]) / (f1[indx2])
    return f1

def brown(f, std, rolloff=0):
    f1 = np.abs(f)
    indx1 = np.where(f1 <= rolloff)
    indx2 = np.where(f1 > rolloff)
    f1[indx1] = std**2
    f1[indx2] = (std * min(f1[indx2]))**2 / (f1[indx2]**2)
    return f1

def prune(array, min_value, max_value):
    idxlow = np.where(array < min_value)[0]
    idxhigh = np.where(array > max_value)[0]
    array[idxhigh] = max_value
    array[idxlow] = min_value
    return array

def generate_lorentzian_noise(
                            s0, f0, y, 
                            min_value=-1e10, max_value=1e10, 
                            samples=1024, samplerate=1/2e-6, 
                            just_phase=False
                        ):
    freqs = np.fft.fftfreq(int(samples), 1/samplerate)
    rfreqs = np.fft.rfftfreq(int(samples), 1/samplerate)
    f = lorentzian(freqs, s0, f0, y)
    return rfreqs, f[:len(rfreqs)], prune(fftnoise(f, just_phase=just_phase), min_value, max_value)

def generate_pink_noise(
                    s0, rolloff=0, 
                    min_value=-1e10, max_value=1e10, 
                    samples=1024, samplerate=1/2e-6, 
                    just_phase=False
                ):
    freqs = np.fft.fftfreq(int(samples), 1/samplerate)
    rfreqs = np.fft.rfftfreq(int(samples), 1/samplerate)
    f = pink(freqs, s0, rolloff=rolloff)
    return rfreqs, f[:len(rfreqs)], prune(fftnoise(f, just_phase=just_phase), min_value, max_value)

def generate_brown_noise(
                        s0, rolloff=0, 
                        min_value=-1e10, max_value=1e10, 
                        samples=1024, samplerate=1/2e-6, 
                        just_phase=False
                    ):
    freqs = np.fft.fftfreq(int(samples), 1/samplerate)
    rfreqs = np.fft.rfftfreq(int(samples), 1/samplerate)
    f = brown(freqs, s0, rolloff=rolloff)
    return rfreqs, f[:len(rfreqs)], prune(fftnoise(f, just_phase=just_phase), min_value, max_value)

def generate_white_noise(
                        s0, 
                        min_value=-1e10, max_value=1e10, 
                        min_freq=-1e-10, max_freq=1e10, 
                        samples=1024, samplerate=1/2e-6, 
                        just_phase=False
                    ):
    freqs = np.fft.fftfreq(int(samples), 1/samplerate)
    rfreqs = np.fft.rfftfreq(int(samples), 1/samplerate)
    f = np.zeros(int(samples))
    idx = np.where(np.logical_and(freqs>=min_freq, freqs<=max_freq))[0]
    f[idx] = (s0 / 2)**2  # because zero-mean
    return rfreqs, f[:len(rfreqs)], prune(fftnoise(f, just_phase=just_phase), min_value, max_value)
