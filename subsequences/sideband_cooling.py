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
    duration="SidebandCooling.duration"
    
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
        s = SidebandCooling
        self.get_729_dds(s.channel_729, id="SBCooling")
        freq_729 = self.calc_frequency(
                        s.line_selection,
                        detuning=s.stark_shift,
                        sideband=s.selection_sideband,
                        order=s.order,
                        dds=s.channel_729
                    )
        self.dds_729_SBC.set(freq_729, 
                         amplitude=s.amplitude_729)
        self.dds_729_SBC.set_att(s.att_729)
        self.dds_854.set(s.freq_854, 
                         amplitude=s.amp_854)
        self.dds_854.set_att(s.att_854)
        self.dds_866.set(s.freq_866, 
                         amplitude=s.amp_866)
        self.dds_866.set_att(s.att_866)
        with parallel:
            self.dds_854.sw.on()
            self.dds_866.sw.on()
            self.dds_729_SBC.sw.on()
            self.dds_729_SP_SBC.sw.on()
        delay(s.duration)
        with parallel:
            self.dds_729_SBC.sw.off()
            self.dds_729_SP_SBC.sw.off()
        
        if s.sequential_enable:
            self.get_729_dds(s.sequential_channel_729, id="SeqSBCooling")
            freq_729 = self.calc_frequency( 
                    s.line_selection,
                    detuning=s.stark_shift,
                    sideband=s.sequential_selection_sideband,
                    order=s.sequential_order,
                    dds=s.sequential_channel_729)
            self.dds_729_SeqSBC.set(freq_729, 
                            amplitude=s.amplitude_729)
            self.dds_729_SeqSBC.set_att(s.att_729)
            with parallel:
                self.dds_729_SeqSBC.sw.on()
                self.dds_729_SP_SeqSBC.sw.on()
            delay(s.duration)
            with parallel:
                self.dds_729_SeqSBC.sw.off()
                self.dds_729_SP_SeqSBC.sw.off()

        if s.sequential1_enable:
            self.get_729_dds(s.sequential1_channel_729, id="SeqSBCooling1")
            freq_729 = self.calc_frequency( 
                    s.line_selection,
                    detuning=s.stark_shift,
                    sideband=s.sequential1_selection_sideband,
                    order=s.sequential1_order,
                    dds=s.sequential1_channel_729)
            self.dds_729_SeqSBC1.set(freq_729, 
                            amplitude=s.amplitude_729)
            self.dds_729_SeqSBC1.set_att(s.att_729)
            with parallel:
                self.dds_729_SeqSBC1.sw.on()
                self.dds_729_SP_SeqSBC1.sw.on()
            delay(s.duration)
            with parallel:
                self.dds_729_SeqSBC1.sw.off()
                self.dds_729_SP_SeqSBC1.sw.off()

        if s.sequential2_enable:
            self.get_729_dds(s.sequential2_channel_729, id="SeqSBCooling2")
            freq_729 = self.calc_frequency( 
                    s.line_selection,
                    detuning=s.stark_shift,
                    sideband=s.sequential2_selection_sideband,
                    order=s.sequential2_order,
                    dds=s.sequential2_channel_729)
            self.dds_729_SeqSBC2.set(freq_729, 
                            amplitude=s.amplitude_729)
            self.dds_729_SeqSBC2.set_att(s.att_729)
            with parallel:
                self.dds_729_SeqSBC2.sw.on()
                self.dds_729_SP_SeqSBC2.sw.on()
            delay(s.duration)
            with parallel:
                self.dds_729_SeqSBC2.sw.off()
                self.dds_729_SP_SeqSBC2.sw.off()
        
        delay(3 * s.repump_additional)
        with parallel:
            self.dds_854.sw.off()
            self.dds_866.sw.off()
