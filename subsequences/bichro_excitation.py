from artiq.experiment import *
from artiq.coredevice.ad9910 import RAM_MODE_RAMPUP, RAM_DEST_ASF

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
            dp_freq = self.calc_frequency(
                b.line_selection,
                detuning=b.detuning_carrier_1,
                dds="729G"
            )
            self.dds_729.set(dp_freq, amplitude=b.amp,
                             phase=b.phase / 360)
            self.dds_729.set_att(b.att)
            if b.bichro_enable:

                # TEMP ramping stuff
                n_steps = 100
                amps = [(1./n_steps) * b.amp_blue * (i+1) for i in range(n_steps)]
                write = [0]*n_steps

                self.dds_729_SP.amplitude_to_ram(amps, write)
                #print(write)
                #self.core.break_realtime()
                #self.dds_729_SP.set_cfr1(ram_enable=0)
                #self.dds_729_SP.cpld.io_update.pulse_mu(8)
                self.dds_729_SP.set_profile_ram(
                        start=200, end=200 + n_steps - 1, step=1,
                        profile=2, mode=RAM_MODE_RAMPUP)
                self.dds_729_SP.cpld.set_profile(2)
                #self.dds_729_SP.cpld.io_update.pulse_mu(8)
                #delay(1*ms)
                self.dds_729_SP.write_ram(write)
                self.dds_729_SP.set_cfr1(ram_enable=1, ram_destination=RAM_DEST_ASF)
                self.dds_729_SP.cpld.io_update.pulse_mu(8)
                #delay(1*ms)
                # END TEMP ramping stuff

                self.dds_729_SP.set(freq_blue, amplitude=b.amp_blue, profile=2)
                self.dds_729_SP.cpld.io_update.pulse_mu(8)
                self.dds_729_SP.set_att(b.att_blue)
                self.dds_729_SP_bichro.set(freq_red, amplitude=b.amp_red)
                self.dds_729_SP_bichro.set_att(b.att_red)
                with parallel:
                    self.dds_729_SP.sw.on()
                    self.dds_729_SP_bichro.sw.on()
                    self.dds_729.sw.on()
                delay(b.duration)
                with parallel:
                    self.dds_729_SP.sw.off()
                    self.dds_729_SP_bichro.sw.off()
                    self.dds_729.sw.off()
            else:
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
            self.dds_729.set(dp_freq1, amplitude=b.amp,
                             phase=b.phase / 360)
            self.dds_729.set_att(b.att)
            self.dds_7291.set(dp_freq2, amplitude=b.amp_ion2,
                             phase=b.phase / 360)
            self.dds_7291.set_att(b.att_ion2)
            if b.bichro_enable:
                self.dds_729_SP.set(freq_blue1, amplitude=b.amp_blue)
                self.dds_729_SP.set_att(b.att_blue)
                self.dds_729_SP_bichro.set(freq_red1, amplitude=b.amp_red)
                self.dds_729_SP_bichro.set_att(b.att_red)
                self.dds_729_SP1.set(freq_blue2, amplitude=b.amp_blue_ion2)
                self.dds_729_SP1.set_att(b.att_blue_ion2)
                self.dds_729_SP_bichro1.set(freq_red2, amplitude=b.amp_red_ion2)
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