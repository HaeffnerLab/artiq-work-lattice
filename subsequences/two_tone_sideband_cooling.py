from artiq.experiment import *


class TwoToneSidebandCooling:
    channel_729 ="StatePreparation.channel_729"
    order="SidebandCooling.order"
    selection_sideband="SidebandCooling.selection_sideband"
    freq_854="SidebandCooling.frequency_854"
    freq_866="SidebandCooling.frequency_866"
    amp_866="SidebandCooling.amplitude_866"
    att_866="SidebandCooling.att_866"
    stark_shift="TwoToneSidebandCooling.stark_shift1"
    stark_shift2="TwoToneSidebandCooling.stark_shift2"
    dp_amp="TwoToneSidebandCooling.dp_amp"
    dp_att="TwoToneSidebandCooling.dp_att"
    drive1_amp="TwoToneSidebandCooling.drive1_amp"
    drive1_att="TwoToneSidebandCooling.drive1_att"
    drive2_amp="TwoToneSidebandCooling.drive2_amp"
    drive2_att="TwoToneSidebandCooling.drive2_att"
    amp_854="TwoToneSidebandCooling.amp_854"
    att_854="TwoToneSidebandCooling.att_854"
    duration="TwoToneSidebandCooling.duration"

    def subsequence(self):
        t = TwoToneSidebandCooling
        
        # Calculate 729 set frequencies
        t.freq_729 = self.calc_frequency(
                            "S-1/2D-1/2",
                            sideband=t.selection_sideband,
                            order=t.order,
                            dds=t.channel_729
                        )
        offset = self.get_offset_frequency(t.channel_729)
        sp_freq_7291 = 80*MHz + offset + t.stark_shift1
        sminus = self.calc_frequency("S-1/2D-1/2")
        splus = self.calc_frequency("S+1/2D+1/2")
        sp_freq_7292 = 80*MHz + splus - sminus + t.stark_shift2
        
        # Setup DP
        self.get_729_dds(t.channel_729)
        self.dds_729.set(
                t.freq_729,
                amplitude=t.dp_amp
            )
        self.dds_729.set_att(t.dp_att)
        self.dds_729.sw.on()

        # Setup drive1
        self.dds_729_SP.set(sp_freq_7291, amplitude=t.drive1_amp)
        self.dds_729_SP.set_att(t.drive1_att)
        
        # Setup drive2
        self.dds_729_SP_bichro.set(sp_freq_7292, amplitude=t.drive2_amp)
        self.dds_729_SP_bichro.set_att(t.drive2_att)

        # Setup 854
        self.dds_854.set(t.freq_854, amplitude=t.amp_864)
        self.dds_854.set_att(t.att_854)

        # Setup 866
        self.dds_866.set(t.freq_866, amplitude=t.amp_866)
        self.dds_866.set_att(t.att_866)

        # Run it
        with parallel:
            self.dds_729_SP.sw.on()
            self.dds_729_SP_bichro.sw.on()
            self.dds_854.sw.on()
            self.dds_866.sw.on()
        delay(t.duration)
        with parallel:
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
            self.dds_729_SP_bichro.sw.off()
            self.dds_854.sw.off()
            self.dds_866.sw.off()
