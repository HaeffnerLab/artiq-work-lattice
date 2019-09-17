from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_RAMPUP, RAM_DEST_ASF
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE
import numpy as np


class IsingSimulation:
    amp_blue="MolmerSorensen.amp_blue"
    att_blue="MolmerSorensen.att_blue"
    amp_red="MolmerSorensen.amp_red"
    att_red="MolmerSorensen.att_red"
    amp="MolmerSorensen.amplitude"
    att="MolmerSorensen.att"
    phase="MolmerSorensen.phase"
    line_selection="MolmerSorensen.line_selection"
    selection_sideband="MolmerSorensen.selection_sideband"
    detuning="MolmerSorensen.detuning"
    detuning_carrier_1="MolmerSorensen.detuning_carrier_1"
    detuning_carrier_2="MolmerSorensen.detuning_carrier_2"

    local1_amp = "Benchmarking.local1_amp"
    local1_att = "Benchmarking.local1_att"
    local1_phase = "Benchmarking.local1_phase"
    local1_detuning = "Benchmarking.local1_detuning"
    local1_line_selection = "Benchmarking.local1_line_selection"

    default_sp_amp_729="Excitation_729.single_pass_amplitude"
    default_sp_att_729="Excitation_729.single_pass_att"

    duration="Benchmarking.simulation_time"
    noise_fraction="Benchmarking.amplitude_noise_fraction"

    phase_ref_time=np.int64(-1)
    use_ramping=False
    reverse=False
    alternate_basis=False
    disable_global=False
    disable_local=False

    def add_child_subsequences(pulse_sequence):
        s = IsingSimulation

    def setup_noisy_single_pass(pulse_sequence):
        s = IsingSimulation
        # TODO_RYAN - generate the correct noisy waveform here
        pulse_sequence.generate_single_pass_noise_waveform(
            mean=s.amp_blue,
            std=s.noise_fraction * s.amp_blue,
            freq_noise=False)

    @kernel
    def setup_ramping(pulse_sequence):
        s = IsingSimulation
        s.use_ramping = True
        self.get_729_dds("729G")
        self.get_729_dds("729L1", id=1)
        pulse_sequence.prepare_pulse_with_amplitude_ramp(
            pulse_duration=s.duration,
            ramp_duration=1*us,
            dds1_amp=s.amp,
            use_dds2=True, dds2_amp=s.local1_amp)
        pulse_sequence.prepare_noisy_single_pass(freq_noise=False)

    def subsequence(self):
        s = IsingSimulation

        local1_detuning = s.local1_detuning
        if alternate_basis:
            # TODO_RYAN: global z-rotation by pi/2 via AC stark shift

        trap_frequency = self.get_trap_frequency(s.selection_sideband)
        freq_red = 80*MHz - trap_frequency - s.detuning
        freq_blue = 80*MHz + trap_frequency + s.detuning

        self.get_729_dds("729G")
        self.get_729_dds("729L1", id=1)
        offset = self.get_offset_frequency("729G")
        freq_blue += offset
        freq_red += offset

        phase_offset = 180. if s.reverse else 0.

        # Set double-pass to correct frequency and phase,
        # and set amplitude to zero for now.
        dp_freq = self.calc_frequency(
            s.line_selection,
            detuning=s.detuning_carrier_1,
            dds="729G"
        )
        local1_dp_freq = self.calc_frequency(
            s.local1_line_selection,
            detuning=local1_detuning,
            dds="729L1"
        )
        self.dds_729.set(dp_freq, amplitude=0., phase=s.phase / 360, ref_time_mu=s.phase_ref_time)
        self.dds_7291.set(local1_dp_freq, amplitude=0., phase=(s.local1_phase + phase_offset) / 360, ref_time_mu=s.phase_ref_time)

        self.dds_729_SP.set(freq_blue, amplitude=0., phase=phase_offset, ref_time_mu=s.phase_ref_time)
        self.dds_729_SP.set_att(s.att_blue)
        self.dds_729_SP_bichro.set(freq_red, amplitude=0., phase=phase_offset, ref_time_mu=s.phase_ref_time)
        self.dds_729_SP_bichro.set_att(s.att_red)

        phase_blue = 180. if s.alternate_basis else 0.
        self.start_noisy_single_pass(s.phase_ref_time,
            freq_sp=freq_blue, amp_sp=s.amp_blue, att_sp=s.att_blue, phase_sp=phase_blue / 360,
            use_bichro=True,
            freq_sp_bichro=freq_red, amp_sp_bichro=s.amp_red, att_sp_bichro=s.att_red)

        local1_sp_freq = 80*MHz + self.get_offset_frequency("729L1")
        self.start_noisy_single_pass(s.phase_ref_time,
            freq_sp=local1_sp_freq, amp_sp=s.default_sp_amp_729, att_sp=s.default_sp_att_729, id=1)

        if s.use_ramping and not s.disable_global:
            self.execute_pulse_with_amplitude_ramp(
                dds1_att=s.att, dds1_freq=dp_freq,
                use_dds2=not s.disable_local,
                dds2_att=s.local1_att, dds2_freq=local1_dp_freq)
        else:
            self.dds_729.set(dp_freq, amplitude=s.amp, phase=s.phase / 360, ref_time_mu=s.phase_ref_time)
            self.dds_729.set_att(s.att)
            self.dds_7291.set(local1_dp_freq, amplitude=s.local1_amp, phase=s.local1_phase / 360, ref_time_mu=s.phase_ref_time)
            self.dds_7291.set_att(s.local1_att)

            with parallel:
                if not s.disable_global:
                    self.dds_729.sw.on()
                if not s.disable_local:
                    self.dds_7291.sw.on()
            delay(s.duration)
            with parallel:
                self.dds_729.sw.off()
                self.dds_7291.sw.off()

        self.stop_noisy_single_pass(use_bichro=True)

        if alternate_basis:
            # TODO_RYAN: global rotation by -pi/2 via AC stark shift
            pass
