from artiq.experiment import *


class BichroExcitation:
    bichro_enable="MolmerSorensen.bichro_enable"
    due_carrier_enable="MolmerSorensen.due_carrier_enable"
    channel="MolmerSorensen.channel_729"
    shape_profile="MolmerSorensen.shape_profile"
    amp_blue="MolmerSorensen.amp_blue"
    att_blue="MolmerSorensen.att_blue"
    amp_red="MolmerSorensen.amp_red"
    att_red="MolmerSorensen.att_red"
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

    def subsequence(self):
        trap_frequency = self.get_trap_frequency(BichroExcitation.selection_sideband)
        freq_blue = 80*MHz + trap_frequency + BichroExcitation.detuning
        freq_red = 80*MHz - trap_frequency - BichroExcitation.detuning
        if BichroExcitation.channel == "global":
            self.get_729_dds("729G")
            dp_freq = self.calc_frequency(
                BichroExcitation.line_selection,
                dds="729G"
            )
            self.dds_729.set(dp_freq, amplitude=BichroExcitation.amp,
                             phase=BichroExcitation.phase / 360)
            self.dds_729.set_att(BichroExcitation.att)
            if BichroExcitation.bichro_enable:
                self.dds_729_SP.set(freq_blue, amplitude=BichroExcitation.amp_blue)
                self.dds_729_SP.set_att(BichroExcitation.att_blue)
                self.dds_729_SP_bichro.set(freq_red, amplitude=BichroExcitation.amp_red)
                self.dds_729_SP_bichro.set_att(BichroExcitation.att_red)
                with parallel:
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                    self.dds_729_SP_bichro.sw.on()
                delay(BichroExcitation.duration)
                with parallel:
                    self.dds_729.sw.off()
                    self.dds_729_SP.sw.off()
                    self.dds_729_SP_bichro.sw.off()
            else:
                with parallel:
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(BichroExcitation.duration)
                with parallel:
                    self.dds_729.sw.off()
                    self.dds_729_SP.sw.off()

        elif BichroExcitation.channel == "local":
            self.get_729_dds("729L1")
            self.get_729_dds("729L2", i=1)
            dp_freq1 = self.calc_frequency(
                BichroExcitation.line_selection,
                dds="729L1"
            )
            if BichroExcitation.due_carrier_enable:
                dp_freq2 = self.calc_frequency(
                    BichroExcitation.line_selection_ion2,
                    dds="729L2"
                )
            else:
                dp_freq2 = self.calc_frequency(
                    BichroExcitation.line_selection,
                    dds="729L2"
                )
            self.dds_729.set(dp_freq1, amplitude=BichroExcitation.amp,
                             phase=BichroExcitation.phase / 360)
            self.dds_729.set_att(BichroExcitation.att)
            self.dds_7291.set(dp_freq2, amplitude=BichroExcitation.amp_ion2,
                             phase=BichroExcitation.phase / 360)
            self.dds_7291.set_att(BichroExcitation.att_ion2)
            if BichroExcitation.bichro_enable:
                self.dds_729_SP.set(freq_blue, amplitude=BichroExcitation.amp_blue)
                self.dds_729_SP.set_att(BichroExcitation.att_blue)
                self.dds_729_SP_bichro.set(freq_red, amplitude=BichroExcitation.amp_red)
                self.dds_729_SP_bichro.set_att(BichroExcitation.att_red)
                self.dds_729_SP1.set(freq_blue, amplitude=BichroExcitation.amp_blue_ion2)
                self.dds_729_SP1.set_att(BichroExcitation.att_blue_ion_2)
                self.dds_729_SP1_bichro.set(freq_red, amplitude=BichroExcitation.amp_red_ion2)
                self.dds_729_SP1_bichro.set_att(BichroExcitation.att_red_ion2)
                with parallel:
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                    self.dds_729_SP_bichro.sw.on()
                    self.dds_7291.sw.on()
                    self.dds_729_SP1.sw.on()
                    self.dds_729_SP_bichro1.sw.on()
                delay(BichroExcitation.duration)
                with parallel:
                    self.dds_729.sw.off()
                    self.dds_729_SP.sw.off()
                    self.dds_729_SP_bichro.sw.off()
                    self.dds_7291.sw.off()
                    self.dds_729_SP1.sw.off()
                    self.dds_729_SP_bichro1.sw.off()
            else:
                with parallel:
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                    self.dds_7291.sw.on()
                    self.dds_729_SP1.sw.on()
                delay(BichroExcitation.duration)
                with parallel:
                    self.dds_729.sw.off()
                    self.dds_729_SP.sw.off()
                    self.dds_729.sw1.off()
                    self.dds_729_SP1.sw.off()