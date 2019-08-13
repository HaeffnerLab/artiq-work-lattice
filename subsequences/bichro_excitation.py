from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_RAMPUP, RAM_DEST_ASF
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE
import numpy as np


class BichroExcitation:
    bichro_enable="MolmerSorensen.bichro_enable"
    due_carrier_enable="MolmerSorensen.due_carrier_enable"
    channel="MolmerSorensen.channel_729"
    shape_profile="MolmerSorensen.shape_profile"
    amp_blue="MolmerSorensen.amp_blue"
    att_blue="MolmerSorensen.att_blue"
    amp_blue_ion2="MolmerSorensen.amp_blue_ion2"
    att_blue_ion2="MolmerSorensen.att_blue_ion2"
    amp_red="MolmerSorensen.amp_red"
    att_red="MolmerSorensen.att_red"
    amp_red_ion2="MolmerSorensen.amp_red_ion2"
    att_red_ion2="MolmerSorensen.att_red_ion2"
    amp="MolmerSorensen.amplitude"
    att="MolmerSorensen.att"
    amp_ion2="MolmerSorensen.amplitude_ion2"
    att_ion2="MolmerSorensen.att_ion2"
    phase="MolmerSorensen.phase"
    line_selection="MolmerSorensen.line_selection"
    line_selection_ion2="MolmerSorensen.line_selection_ion2"
    selection_sideband="MolmerSorensen.selection_sideband"
    duration="MolmerSorensen.duration"
    detuning="MolmerSorensen.detuning"
    detuning_carrier_1="MolmerSorensen.detuning_carrier_1"
    detuning_carrier_2="MolmerSorensen.detuning_carrier_2"
    default_sp_amp_729="Excitation_729.single_pass_amplitude"
    default_sp_att_729="Excitation_729.single_pass_att"
    phase_ref_time=np.int64(-1)

    def add_child_subsequences(pulse_sequence):
        b = BichroExcitation

    def subsequence(self):
        b = BichroExcitation
        trap_frequency = self.get_trap_frequency(b.selection_sideband)
        freq_red = 80*MHz - trap_frequency - b.detuning
        freq_blue = 80*MHz + trap_frequency + b.detuning
        if b.channel == "global":
            self.get_729_dds("729G")
            offset = self.get_offset_frequency("729G")
            freq_blue += offset
            freq_red += offset

            # Set double-pass to correct frequency and phase,
            # and set amplitude to zero for now.
            dp_freq = self.calc_frequency(
                b.line_selection,
                detuning=b.detuning_carrier_1,
                dds="729G"
            )
            self.dds_729.set(dp_freq,
                amplitude=0.,
                phase=b.phase / 360,
                ref_time_mu=b.phase_ref_time)

            if b.bichro_enable:
                self.dds_729_SP.set(freq_blue, amplitude=b.amp_blue, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP.set_att(b.att_blue)
                self.dds_729_SP_bichro.set(freq_red, amplitude=b.amp_red, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP_bichro.set_att(b.att_red)
                with parallel:
                    self.dds_729_SP.sw.on()
                    self.dds_729_SP_bichro.sw.on()

                # self.start_noisy_bichro(
                #     freq_blue, b.amp_blue, b.att_blue,
                #     freq_red, b.amp_red, b.att_red)

                self.execute_pulse_with_amplitude_ramp(
                    dds1_att=b.att,
                    dds1_freq=dp_freq)

                # self.stop_noisy_bichro()

                with parallel:
                    self.dds_729_SP.sw.off()
                    self.dds_729_SP_bichro.sw.off()
            else:
                # bichro disabled
                self.dds_729.set_amplitude(b.amp)
                self.dds_729.set_att(b.att)
                sp_freq_729 = 80*MHz + offset
                self.dds_729_SP.set(sp_freq_729, amplitude=b.default_sp_amp_729, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP.set_att(b.default_sp_att_729)
                with parallel:
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(b.duration)
                with parallel:
                    self.dds_729.sw.off()
                    self.dds_729_SP.sw.off()

        elif b.channel == "local":
            self.get_729_dds("729L1")
            self.get_729_dds("729L2", id=1)
            offset1 = self.get_offset_frequency("729L1")
            freq_blue1 = freq_blue + offset1
            freq_red1 = freq_red + offset1
            offset2 = self.get_offset_frequency("729L2")
            freq_blue2 = freq_blue + offset2
            freq_red2 = freq_red + offset2
            dp_freq1 = self.calc_frequency(
                b.line_selection,
                detuning=b.detuning_carrier_1,
                dds="729L1"
            )
            if b.due_carrier_enable:
                dp_freq2 = self.calc_frequency(
                    b.line_selection_ion2,
                    detuning=b.detuning_carrier_2,
                    dds="729L2"
                )
            else:
                dp_freq2 = self.calc_frequency(
                    b.line_selection,
                    dds="729L2"
                )
            self.dds_729.set(dp_freq1,
                             amplitude=b.amp,
                             phase=b.phase / 360,
                             ref_time_mu=b.phase_ref_time)
            self.dds_729.set_att(b.att)
            self.dds_7291.set(dp_freq2,
                             amplitude=b.amp_ion2,
                             phase=b.phase / 360,
                             ref_time_mu=b.phase_ref_time)
            self.dds_7291.set_att(b.att_ion2)
            if b.bichro_enable:
                self.dds_729_SP.set(freq_blue1, amplitude=b.amp_blue, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP.set_att(b.att_blue)
                self.dds_729_SP_bichro.set(freq_red1, amplitude=b.amp_red, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP_bichro.set_att(b.att_red)
                self.dds_729_SP1.set(freq_blue2, amplitude=b.amp_blue_ion2, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP1.set_att(b.att_blue_ion2)
                self.dds_729_SP_bichro1.set(freq_red2, amplitude=b.amp_red_ion2, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP_bichro1.set_att(b.att_red_ion2)
                with parallel:
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                    self.dds_729_SP_bichro.sw.on()
                    self.dds_7291.sw.on()
                    self.dds_729_SP1.sw.on()
                    self.dds_729_SP_bichro1.sw.on()
                delay(b.duration)
                with parallel:
                    self.dds_729.sw.off()
                    self.dds_729_SP.sw.off()
                    self.dds_729_SP_bichro.sw.off()
                    self.dds_7291.sw.off()
                    self.dds_729_SP1.sw.off()
                    self.dds_729_SP_bichro1.sw.off()
            else:
                # bichro disabled
                sp_freq_7291 = 80*MHz + offset1
                self.dds_729_SP.set(sp_freq_7291, amplitude=b.default_sp_amp_729, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP.set_att(b.default_sp_att_729)
                sp_freq_7292 = 80*MHz + offset2
                self.dds_729_SP1.set(sp_freq_7292, amplitude=b.default_sp_amp_729, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP1.set_att(b.default_sp_att_729)
                with parallel:
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                    self.dds_7291.sw.on()
                    self.dds_729_SP1.sw.on()
                delay(b.duration)
                with parallel:
                    self.dds_729.sw.off()
                    self.dds_729_SP.sw.off()
                    self.dds_7291.sw.off()
                    self.dds_729_SP1.sw.off()