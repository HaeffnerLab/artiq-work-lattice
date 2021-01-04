from artiq.experiment import *
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE

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
    noise_list=[0.]  
    phase_ref_time=-1

    def subsequence(self):
        r = NoisyPhaseRabiExcitation
        self.get_729_dds(r.channel_729)
        self.dds_729.set(r.freq_729,
                        amplitude=r.amp_729,
                        ref_time_mu=r.phase_ref_time)
        self.dds_729.set_att(r.att_729)
        sp_freq_729 = 80*MHz + self.get_offset_frequency(r.channel_729)
        self.dds_729_SP.set(sp_freq_729, amplitude=r.sp_amp_729, 
                         phase=r.phase_729 / 360.)#, ref_time_mu=r.phase_ref_time)
        self.dds_729_SP_bichro.set(1*MHz, amplitude=r.sp_amp_729, 
                         phase=r.phase_729 / 360.)#, ref_time_mu=r.phase_ref_time)         
        self.dds_729_SP.set_att(r.sp_att_729)
        self.dds_729_SP_bichro.set_att(r.sp_att_729)           
        with parallel:
            self.dds_729.sw.on()
            self.dds_729_SP.sw.on()
            self.dds_729_SP_bichro.sw.on()
        for i in range(0, 100):
            self.dds_729_SP_bichro.set(1*MHz, phase=r.noise_list[i])
        with parallel:
            self.dds_729_SP.sw.off()
            self.dds_729_SP_bichro.sw.off()