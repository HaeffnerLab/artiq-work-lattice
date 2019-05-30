from artiq.experiment import *


class SidebandCooling:
    line_selection="SidebandCooling.line_selection"
    selection_sideband="SidebandCooling.selection_sideband"
    order="SidebandCooling.order"
    stark_shift="SidebandCooling.stark_shift"
    channel_729="StatePreparation.channel_729"
    repump_additional="OpticalPumpingContinuous.optical_pumping_continuous_repump_additional"
    amplitude_729="SidebandCooling.amplitude_729"
    att_729="SidebandCooling.att_729"
    duration="SidebandCoolingContinuous.sideband_cooling_continuous_duration"
    
    freq_866="SidebandCooling.frequency_866"
    amp_866="SidebandCooling.amplitude_866"
    att_866="SidebandCooling.att_866"
    
    freq_854="SidebandCooling.frequency_854"
    amp_854="SidebandCooling.amplitude_854"
    att_854="SidebandCooling.att_854"

    sequential_enable="SequentialSBCooling.enable"
    sequential_channel_729="SequentialSBCooling.channel_729"
    sequential_selection_sideband="SequentialSBcooling.selection_sideband"
    sequential_order="SequentialSBCooling.order"

    sequential1_enable="SequentialSBCooling1.enable"
    sequential1_channel_729="SequentialSBCooling1.channel_729"
    sequential1_selection_sideband="SequentialSBcooling1.selection_sideband"
    sequential1_order="SequentialSBCooling1.order"

    sequential2_enable="SequentialSBCooling2.enable"
    sequential2_channel_729="SequentialSBCooling2.channel_729"
    sequential2_selection_sideband="SequentialSBcooling2.selection_sideband"
    sequential2_order="SequentialSBCooling2.order"

    def subsequence(self):
        delay(1*ms)
        self.get_729_dds(SidebandCooling.channel_729)
        freq_729 = self.calc_frequency(
                        SidebandCooling.line_selection,
                        detuning=SidebandCooling.stark_shift,
                        sideband=SidebandCooling.selection_sideband,
                        order=SidebandCooling.order,
                        dds=SidebandCooling.channel_729
                    )
        self.dds_729.set(freq_729, 
                         amplitude=SidebandCooling.amplitude_729)
        self.dds_729.set_att(SidebandCooling.att_729)
        self.dds_854.set(SidebandCooling.freq_854, 
                         amplitude=SidebandCooling.amp_854)
        self.dds_854.set_att(SidebandCooling.att_854)
        self.dds_866.set(SidebandCooling.freq_866, 
                         amplitude=SidebandCooling.amp_866)
        self.dds_866.set_att(SidebandCooling.att_866)
        with parallel:
            self.dds_854.sw.on()
            self.dds_866.sw.on()
            self.dds_729.sw.on()
            self.dds_729_SP.sw.on()
        delay(SidebandCooling.duration)
        with parallel:
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
        
        if SidebandCooling.sequential_enable:
            self.get_729_dds(SidebandCooling.sequential_channel_729)
            freq_729 = self.calc_frequency( 
                    SidebandCooling.line_selection,
                    detuning=SidebandCooling.stark_shift,
                    sideband=SidebandCooling.sequential_selection_sideband,
                    order=SidebandCooling.sequential_order,
                    dds=SidebandCooling.channel_729)
            with parallel:
                self.dds_729.sw.on()
                self.dds_729_SP.sw.on()
            delay(SidebandCooling.duration)
            with parallel:
                self.dds_729.sw.off()
                self.dds_729_SP.sw.off()

        if SidebandCooling.sequential1_enable:
            self.get_729_dds(SidebandCooling.sequential1_channel_729)
            freq_729 = self.calc_frequency( 
                    SidebandCooling.line_selection,
                    detuning=SidebandCooling.stark_shift,
                    sideband=SidebandCooling.sequential1_selection_sideband,
                    order=SidebandCooling.sequential1_order,
                    dds=SidebandCooling.channel_729)
            with parallel:
                self.dds_729.sw.on()
                self.dds_729_SP.sw.on()
            delay(SidebandCooling.duration)
            with parallel:
                self.dds_729.sw.off()
                self.dds_729_SP.sw.off()

        if SidebandCooling.sequential2_enable:
            self.get_729_dds(SidebandCooling.sequential2_channel_729)
            freq_729 = self.calc_frequency( 
                    SidebandCooling.line_selection,
                    detuning=SidebandCooling.stark_shift,
                    sideband=SidebandCooling.sequential2_selection_sideband,
                    order=SidebandCooling.sequential2_order,
                    dds=SidebandCooling.channel_729)
            with parallel:
                self.dds_729.sw.on()
                self.dds_729_SP.sw.on()
            delay(SidebandCooling.duration)
            with parallel:
                self.dds_729.sw.off()
                self.dds_729_SP.sw.off()
        
        # delay_time = 3 * SidebandCooling.repump_additional
        delay_time = 100*us
        delay(delay_time)
        self.dds_854.sw.off()
        self.dds_866.sw.off()
        delay(delay_time)
