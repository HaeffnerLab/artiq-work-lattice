from artiq.experiment import *
from pulse_sequence import get_729_dds


class SidebandCooling():
    line_selection="SidebandCooling.line_selection"
    selection_sideband="SidebandCooling.selection_sideband"
    order="SidebandCooling.order"
    stark_shift="SidebandCooling.order"
    channel_729="StatePreparation.channel_729"
    repump_additional="OpticalPumpingContinuous.optical_pumping_continuous_duration"
    amplitude_729="SidebandCooling.amplitude_729"
    att_729="SidebandCooling.att_729"
    duration="SidebandCoolingContinuous.sideband_cooling_continuous_duration"
    freq_729=220*MHz

    # sequential_


    def subsequence(self):
        # if SidebandCooling.channel_729 == "729L1":
        #     dds_729 = self.dds_729L1
        #     dds_729_SP = self.dds_SP_729L1
        # elif SidebandCooling.channel_729 == "729L2":
        #     dds_729 = self.dds_729L2
        #     dds_729_SP = self.dds_SP_729L2
        # elif SidebandCooling.channel_729 == "729G":
        #     dds_729 = self.dds_729G
        #     dds_729_SP = self.dds_SP_729G
        # else:
        #     dds_729 = self.dds_729G
        #     dds_729_SP = self.dds_SP_729G
        get_729_dds(SidebandCooling.channel_729)

        freq_729 = SidebandCooling.freq_729 + SidebandCooling.stark_shift
        dds_729.set(freq_729, amplitude=SidebandCooling.amplitude_729)
        dds_729.set_att(SidebandCooling.att_729)
        
        with parallel:
            self.dds_729.sw.on()##
            self.dds_729_SP.sw.on()
            self.dds_854.sw.on()
            self.dds_866.sw.on()
        delay(SidebandCooling.duration)
        with parallel:
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
        
        if SidebandCooling.
        
        
        
        delay(SidebandCooling.repump_additional)
        self.dds_854.sw.off()
        delay(SidebandCooling.repump_additional)
        self.dds_866.sw.off()

