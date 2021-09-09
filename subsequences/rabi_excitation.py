from artiq.experiment import *
import numpy as np
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE

class RabiExcitation:
    freq_729="Excitation_729.rabi_excitation_frequency"
    amp_729="Excitation_729.rabi_excitation_amplitude"
    att_729="Excitation_729.rabi_excitation_att"
    phase_729="Excitation_729.rabi_excitation_phase"
    channel_729="Excitation_729.channel_729"
    duration="Excitation_729.rabi_excitation_duration"
    line_selection="Excitation_729.line_selection"
    sp_amp_729="Excitation_729.single_pass_amplitude"
    sp_att_729="Excitation_729.single_pass_att"
    stark_shift_att="Excitation_729.stark_shift_att"
    stark_shift_amp="Excitation_729.stark_shift_amplitude"
    stark_shift_detuning="Excitation_729.stark_shift_detuning"
    stark_shift_on="Excitation_729.stark_shift_on"
    
    phase_ref_time=np.int64(-1)
    ramp_has_been_programmed= False  # always initialize to False; gets set to True inside setup_ramping

    # @kernel
    # def setup_ramping(self):
    #     # This function programs the appropriate ramp into the DDS memory.
    #     #
    #     # If a PulseSequence wants to use ramping, call setup_ramping() inside 
    #     # its set_subsequence function.
    #     # To disable ramping for a PulseSequence, the easiest way to do this is
    #     # comment or remove the call to setup_ramping() in the set_subsequence function.
    #     r = RabiExcitation        
    #     self.get_729_dds(r.channel_729)
    #     self.prepare_pulse_with_amplitude_ramp(
    #         pulse_duration=r.duration,
    #         ramp_duration=25.0*us,
    #         dds1_amp=r.amp_729)
    #     r.ramp_has_been_programmed = True
    #     print('is ramp set?')

    def subsequence(self):
        r = RabiExcitation
        self.get_729_dds(r.channel_729)

        # # for testing phase coherence
        # self.dds_729_SP_bichro.set(80*MHz, amplitude=1.0, ref_time_mu=r.phase_ref_time)
        # self.dds_729_SP_bichro.set_att(0.0)
        # self.dds_729_SP_bichro.sw.on()
        
        # if r.ramp_has_been_programmed:
        #     self.dds_729.set(r.freq_729,
        #                     amplitude=0.,
        #                     ref_time_mu=r.phase_ref_time)
        # else:
        self.dds_729.set(r.freq_729,
                        amplitude=r.amp_729,
                        ref_time_mu=r.phase_ref_time)
        self.dds_729.set_att(r.att_729)
        self.dds_729.sw.on()
      
        sp_freq_729 = 80*MHz + self.get_offset_frequency(r.channel_729)
        self.dds_729_SP.set(sp_freq_729, amplitude=r.sp_amp_729, 
                         phase=r.phase_729 / 360., ref_time_mu=r.phase_ref_time)
        self.dds_729_SP.set_att(r.sp_att_729)
        delay(5*us)
        
        # if r.ramp_has_been_programmed:
        #     self.dds_729_SP.sw.on()
        #     self.execute_pulse_with_amplitude_ramp(
        #         dds1_att=r.att_729,
        #         dds1_freq=r.freq_729)
            
        #     #self.dds_729_SP.sw.off()
        # else:
        with parallel:
            # self.trigger.on()
            self.dds_729_SP.sw.on()
        delay(r.duration)
        with parallel:
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
            # self.trigger.off()