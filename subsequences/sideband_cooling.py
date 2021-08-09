from artiq.experiment import *
from subsequences.optical_pumping import OpticalPumping

class SidebandCooling:
    line_selection="SidebandCooling.line_selection"
    selection_sideband="SidebandCooling.selection_sideband"
    order="SidebandCooling.order"
    stark_shift="SidebandCooling.stark_shift"
    channel_729="SidebandCooling.channel_729"
    repump_additional="OpticalPumpingContinuous.optical_pumping_continuous_repump_additional"
    amplitude_729="SidebandCooling.amplitude_729"
    att_729="SidebandCooling.att_729"
    duration="SidebandCooling.duration"
    sp_amp_729="Excitation_729.single_pass_amplitude"
    sp_att_729="Excitation_729.single_pass_att"
    
    freq_866="SidebandCooling.frequency_866"
    amp_866="SidebandCooling.amplitude_866"
    att_866="SidebandCooling.att_866"
    
    freq_854="SidebandCooling.frequency_854"
    amp_854="SidebandCooling.amplitude_854"
    att_854="SidebandCooling.att_854"

    sideband_cooling_cycles="SidebandCooling.sideband_cooling_cycles"

    sequential_enable="SequentialSBCooling.enable"
    sequential_channel_729="SequentialSBCooling.channel_729"
    sequential_selection_sideband="SequentialSBCooling.selection_sideband"
    sequential_order="SequentialSBCooling.order"

    sequential1_enable="SequentialSBCooling1.enable"
    sequential1_channel_729="SequentialSBCooling1.channel_729"
    sequential1_selection_sideband="SequentialSBCooling1.selection_sideband"
    sequential1_order="SequentialSBCooling1.order"

    sequential2_enable="SequentialSBCooling2.enable"
    sequential2_channel_729="SequentialSBCooling2.channel_729"
    sequential2_selection_sideband="SequentialSBCooling2.selection_sideband"
    sequential2_order="SequentialSBCooling2.order"

    op_frequency_866="DopplerCooling.doppler_cooling_frequency_866"
    op_amplitude_866="DopplerCooling.doppler_cooling_amplitude_866"
    op_att_866="DopplerCooling.doppler_cooling_att_866"
    op_frequency_854="OpticalPumping.optical_pumping_frequency_854"
    op_amplitude_854="OpticalPumping.optical_pumping_amplitude_854"
    op_att_854="OpticalPumping.optical_pumping_att_854"
    op_line_selection="OpticalPumping.line_selection"
    op_channel_729="StatePreparation.channel_729"
    op_duration="OpticalPumpingContinuous.optical_pumping_continuous_duration"
    op_rempump_duration="OpticalPumpingContinuous.optical_pumping_continuous_repump_additional"
    op_amplitude_729="OpticalPumping.amplitude_729"
    op_att_729="OpticalPumping.att_729"
    op_sp_amp_729="Excitation_729.single_pass_amplitude"
    op_sp_att_729="Excitation_729.single_pass_att"

    freq_729=0.0
    sp_freq_729=0.0
    op_freq_729=0.0
    op_sp_freq_729=0.0
    freq_729_sequential=0.0
    freq_729_sequential1=0.0
    freq_729_sequential2=0.0
    sp_freq_729_sequential=0.0
    sp_freq_729_sequential1=0.0
    sp_freq_729_sequential2=0.0

    def add_child_subsequences(pulse_sequence):
        s = SidebandCooling


    def subsequence(self):
        s = SidebandCooling
        num_cycles = int(s.sideband_cooling_cycles)
        i = 0
        
        s.freq_729 = self.calc_frequency(
                            s.line_selection,
                            detuning=s.stark_shift,
                            sideband=s.selection_sideband,
                            order=s.order,
                            dds=s.channel_729
                        )
        s.sp_freq_729 = 80*MHz + self.get_offset_frequency(s.channel_729)
        
        s.op_freq_729 = self.calc_frequency(
                                s.op_line_selection,
                                dds=s.op_channel_729
                            )
        s.op_sp_freq_729 = 80*MHz + self.get_offset_frequency(s.op_channel_729)
       
        if s.sequential_enable:
            s.freq_729_sequential = self.calc_frequency(
                                s.line_selection,
                                detuning=s.stark_shift,
                                sideband=s.sequential_selection_sideband,
                                order=s.sequential_order,
                                dds=s.sequential_channel_729
                            )
            s.sp_freq_729_sequential = 80*MHz + self.get_offset_frequency(s.sequential_channel_729)
        if s.sequential1_enable:
            s.freq_729_sequential1 = self.calc_frequency(
                                s.line_selection,
                                detuning=s.stark_shift,
                                sideband=s.sequential1_selection_sideband,
                                order=s.sequential1_order,
                                dds=s.sequential1_channel_729
                            )
            s.sp_freq_729_sequential1 = 80*MHz + self.get_offset_frequency(s.sequential1_channel_729)
        if s.sequential2_enable:
            s.freq_729_sequential2 = self.calc_frequency(
                                s.line_selection,
                                detuning=s.stark_shift,
                                sideband=s.sequential2_selection_sideband,
                                order=s.sequential2_order,
                                dds=s.sequential2_channel_729
                            )
            s.sp_freq_729_sequential2 = 80*MHz + self.get_offset_frequency(s.sequential2_channel_729)

        for i in range(num_cycles):

#####################################################################################################
# SBC            ####################################################################################
#####################################################################################################
            channel = s.channel_729
            freq_729 = s.freq_729
            sp_freq_279 = s.sp_freq_729
            self.get_729_dds(channel)
            self.dds_729.set(freq_729, amplitude=s.amplitude_729)
            self.dds_729.set_att(s.att_729)
            self.dds_729_SP.set(sp_freq_729, amplitude=s.sp_amp_729)
            self.dds_729_SP.set_att(s.sp_att_729)
            self.dds_854.set(s.freq_854, amplitude=s.amp_854)
            self.dds_854.set_att(s.att_854)
            self.dds_866.set(s.freq_866, amplitude=s.amp_866)
            self.dds_866.set_att(s.att_866)
            delay(10*us)
            with parallel:
                self.dds_854.sw.on()
                self.dds_866.sw.on()
                self.dds_729.sw.on()
                self.dds_729_SP.sw.on()
            delay(s.duration)
            with parallel:
                self.dds_854.sw.off()
                self.dds_866.sw.off()
                self.dds_729.sw.off()
                #self.dds_729_SP.sw.off()  keep SP on all the time 2/24/2020
            
            # fast op
            self.get_729_dds(s.op_channel_729)
            self.dds_729.set(
                            s.op_freq_729, 
                            amplitude=s.op_amplitude_729
                        )
            self.dds_729.set_att(s.op_att_729)
            self.dds_729_SP.set(s.op_sp_freq_729, amplitude=s.op_sp_amp_729)
            self.dds_729_SP.set_att(s.op_sp_att_729)
            delay(10*us)
            with parallel:
                self.dds_866.sw.on()
                self.dds_854.sw.on()
                self.dds_729.sw.on()
                self.dds_729_SP.sw.on()
            delay(30*us)
            self.dds_729.sw.off()
            with parallel:
                self.dds_854.sw.off()
                self.dds_866.sw.off()

#####################################################################################################
# SBC  sequential  ##################################################################################
#####################################################################################################
            if s.sequential_enable:
                channel = s.sequential_channel_729
                freq_729 = s.freq_729_sequential
                sp_freq_279 = s.sp_freq_729_sequential
                self.get_729_dds(channel)
                self.dds_729.set(freq_729, amplitude=s.amplitude_729)
                self.dds_729.set_att(s.att_729)
                self.dds_729_SP.set(sp_freq_729, amplitude=s.sp_amp_729)
                self.dds_729_SP.set_att(s.sp_att_729)
                self.dds_854.set(s.freq_854, amplitude=s.amp_854)
                self.dds_854.set_att(s.att_854)
                self.dds_866.set(s.freq_866, amplitude=s.amp_866)
                self.dds_866.set_att(s.att_866)
                delay(10*us)
                with parallel:
                    self.dds_854.sw.on()
                    self.dds_866.sw.on()
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(s.duration)
                with parallel:
                    self.dds_854.sw.off()
                    self.dds_866.sw.off()
                    self.dds_729.sw.off()
                    #self.dds_729_SP.sw.off()  keep SP on all the time 2/24/2020
                
                # fast op
                self.get_729_dds(s.op_channel_729)
                self.dds_729.set(
                                s.op_freq_729, 
                                amplitude=s.op_amplitude_729
                            )
                self.dds_729.set_att(s.op_att_729)
                self.dds_729_SP.set(s.op_sp_freq_729, amplitude=s.op_sp_amp_729)
                self.dds_729_SP.set_att(s.op_sp_att_729)
                delay(10*us)
                with parallel:
                    self.dds_866.sw.on()
                    self.dds_854.sw.on()
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(30*us)
                self.dds_729.sw.off()
                with parallel:
                    self.dds_854.sw.off()
                    self.dds_866.sw.off()

#####################################################################################################
# SBC  sequential1   ################################################################################
#####################################################################################################

            if s.sequential1_enable:
                channel = s.sequential1_channel_729
                freq_729 = s.freq_729_sequential1
                sp_freq_279 = s.sp_freq_729_sequential1
                self.get_729_dds(channel)
                self.dds_729.set(freq_729, amplitude=s.amplitude_729)
                self.dds_729.set_att(s.att_729)
                self.dds_729_SP.set(sp_freq_729, amplitude=s.sp_amp_729)
                self.dds_729_SP.set_att(s.sp_att_729)
                self.dds_854.set(s.freq_854, amplitude=s.amp_854)
                self.dds_854.set_att(s.att_854)
                self.dds_866.set(s.freq_866, amplitude=s.amp_866)
                self.dds_866.set_att(s.att_866)
                delay(10*us)
                with parallel:
                    self.dds_854.sw.on()
                    self.dds_866.sw.on()
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(s.duration)
                with parallel:
                    self.dds_854.sw.off()
                    self.dds_866.sw.off()
                    self.dds_729.sw.off()
                    #self.dds_729_SP.sw.off()  keep SP on all the time 2/24/2020
                
                # fast op
                self.get_729_dds(s.op_channel_729)
                self.dds_729.set(
                                s.op_freq_729, 
                                amplitude=s.op_amplitude_729
                            )
                self.dds_729.set_att(s.op_att_729)
                self.dds_729_SP.set(s.op_sp_freq_729, amplitude=s.op_sp_amp_729)
                self.dds_729_SP.set_att(s.op_sp_att_729)
                delay(10*us)
                with parallel:
                    self.dds_866.sw.on()
                    self.dds_854.sw.on()
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(30*us)
                self.dds_729.sw.off()
                with parallel:
                    self.dds_854.sw.off()
                    self.dds_866.sw.off()

#####################################################################################################
# SBC  sequential2       ############################################################################
#####################################################################################################

            if s.sequential2_enable:
                channel = s.sequential2_channel_729
                freq_729 = s.freq_729_sequential2
                sp_freq_279 = s.sp_freq_729_sequential2
                self.get_729_dds(channel)
                self.dds_729.set(freq_729, amplitude=s.amplitude_729)
                self.dds_729.set_att(s.att_729)
                self.dds_729_SP.set(sp_freq_729, amplitude=s.sp_amp_729)
                self.dds_729_SP.set_att(s.sp_att_729)
                self.dds_854.set(s.freq_854, amplitude=s.amp_854)
                self.dds_854.set_att(s.att_854)
                self.dds_866.set(s.freq_866, amplitude=s.amp_866)
                self.dds_866.set_att(s.att_866)
                delay(10*us)
                with parallel:
                    self.dds_854.sw.on()
                    self.dds_866.sw.on()
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(s.duration)
                with parallel:
                    self.dds_854.sw.off()
                    self.dds_866.sw.off()
                    self.dds_729.sw.off()
                    #self.dds_729_SP.sw.off()  keep SP on all the time 2/24/2020
                
                # fast op
                self.get_729_dds(s.op_channel_729)
                self.dds_729.set(
                                s.op_freq_729, 
                                amplitude=s.op_amplitude_729
                            )
                self.dds_729.set_att(s.op_att_729)
                self.dds_729_SP.set(s.op_sp_freq_729, amplitude=s.op_sp_amp_729)
                self.dds_729_SP.set_att(s.op_sp_att_729)
                delay(10*us)
                with parallel:
                    self.dds_866.sw.on()
                    self.dds_854.sw.on()
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(30*us)
                self.dds_729.sw.off()
                with parallel:
                    self.dds_854.sw.off()
                    self.dds_866.sw.off()

#####################################################################################################
# Finally            ################################################################################
#####################################################################################################
            
        self.dds_854.set(80*MHz, amplitude=1.0)
        self.dds_854.set_att(5.0)
        self.dds_866.set(80*MHz, amplitude=1.0)
        self.dds_866.set_att(5.0)
        with parallel:
            self.dds_854.sw.on()
            self.dds_866.sw.on()
        delay(s.repump_additional)
        with parallel:
            self.dds_854.sw.off()
            self.dds_866.sw.off()

        
