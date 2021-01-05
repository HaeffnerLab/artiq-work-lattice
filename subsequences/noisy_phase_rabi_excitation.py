from artiq.experiment import *
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE
import numpy as np


class NoisyPhaseRabiExcitation:
    freq_729="Excitation_729.rabi_excitation_frequency"
    amp_729="Excitation_729.rabi_excitation_amplitude"
    att_729="Excitation_729.rabi_excitation_att"
    phase_729="Excitation_729.rabi_excitation_phase"
    channel_729="Excitation_729.channel_729"
    duration="Excitation_729.rabi_excitation_duration"
    line_selection="Excitation_729.line_selection"
    sp_amp_729="Excitation_729.single_pass_amplitude"
    sp_att_729="Excitation_729.single_pass_att"
    nu_eff="QRM.nu_eff"
    selection_sideband="QRM.selection_sideband"
    delta="QRM.delta"
    noise_list=[0.]  
    noise_parameter="QRM.noise_parameter"
    phase_ref_time=np.int64(-1)

    def setup_noisy_single_pass(pulse_sequence):
        r = NoisyPhaseRabiExcitation
        pulse_sequence.generate_single_pass_noise_waveform(
            mean=0,
            std=0.242,
            freq_noise=True)
    
    def subsequence(self):
        r = NoisyPhaseRabiExcitation
        self.get_729_dds(r.channel_729)
        trap_frequency = self.get_trap_frequency(r.selection_sideband)
        
        self.dds_729.set(r.freq_729,
                        amplitude=r.amp_729,
                        ref_time_mu=r.phase_ref_time)
        self.dds_729.set_att(r.att_729)

        spo = self.get_offset_frequency(r.channel_729)
        sp_freq_729 =        80*MHz + r.delta + spo + trap_frequency - r.nu_eff
        sp_freq_729_bichro = 80*MHz + r.delta + spo - trap_frequency + r.nu_eff
        self.dds_729_SP.set(sp_freq_729, amplitude=r.sp_amp_729, 
                         phase=r.phase_729 / 360., ref_time_mu=r.phase_ref_time)
        self.dds_729_SP_bichro.set(sp_freq_729_bichro, amplitude=r.sp_amp_729, 
                         phase=r.phase_729 / 360., ref_time_mu=r.phase_ref_time)         
        self.dds_729_SP.set_att(r.sp_att_729)
        self.dds_729_SP_bichro.set_att(r.sp_att_729)          
        
        self.start_noisy_single_pass(r.phase_ref_time,
                        freq_noise=True,
                        freq_sp=sp_freq_729, amp_sp=r.sp_amp_729, att_sp=r.sp_att_729,
                        use_bichro=False,)
                        # freq_sp_bichro=freq_red, amp_sp_bichro=b.amp_red, att_sp_bichro=b.att_red)

        with parallel:
            self.dds_729.sw.on()
            self.dds_729_SP.sw.on()
            self.dds_729_SP_bichro.sw.on()
        # start_mu = now_mu()
        # end_mu = start_mu + self.core.seconds_to_mu(r.duration)
        # for epsilon in r.noise_list:
        #     with parallel:
        #         self.dds_729_SP_bichro.set(sp_freq_729, phase=epsilon)
        #         self.dds_729_SP.set(sp_freq_729, phase=-epsilon)
        #     if now_mu() > end_mu:
        #         break
        delay(r.duration)
        with parallel:
            self.dds_729_SP.sw.off()
            self.dds_729_SP_bichro.sw.off()