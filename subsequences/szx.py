from artiq.experiment import *
import numpy as np
from artiq.coredevice.ad9910 import RAM_MODE_RAMPUP, RAM_DEST_ASF
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE

class SZX:
    channel = "SZX.channel_729"
    bichro_enable = "SZX.bichro_enable"
    nu_effective = "SZX.nu_effective"
    amp_blue = "SZX.amp_blue"
    amp_red = "SZX.amp_red"
    att_blue = "SZX.att_blue"
    att_red = "SZX.att_red"
    car_amp = "SZX.carrier_amplitude"
    car_amp_L1 = "SZX.local_rabi_amp"
    car_att = "SZX.att"
    car_att_L1 = "SZX.local_rabi_att"
    sideband_selection = "SZX.sideband_selection"
    line_selection = "SZX.line_selection"
    carrier_detuning = "SZX.carrier_detuning"
    carrier_detuning_L1 = "SZX.carrier_detuning_L1"
    phase = "SZX.phase"
    phase_ref_time=np.int64(-1)
    sp_amp_729L1 = "Excitation_729.single_pass_amplitude"
    sp_att_729L1 = "Excitation_729.single_pass_att"
    AC_stark_local = "SZX.AC_stark_local"
    use_ramping = False
    use_single_pass_freq_noise = False

    def subsequence(self):
        s = SZX
        trap_frequency = self.get_trap_frequency(s.sideband_selection)
        freq_red = 80*MHz - trap_frequency*0.5 
        freq_blue = 80*MHz + trap_frequency*0.5 + s.nu_effective
        if s.channel == "729global":
            offset = self.get_offset_frequency("729G")
            freq_blue += offset
            freq_red += offset
            
            #if not s.sp_due_enable:
                
            self.get_729_dds("729G", id=0)
                
            # Set double-pass to correct frequency and phase,
            # and set amplitude to zero for now.
            dp_freq = self.calc_frequency(
                s.line_selection,
                detuning=s.carrier_detuning,
                dds="729G"
            )

            # amplitude need to start from 0 when ramping is on
            self.dds_729.set(dp_freq,
                amplitude=0.,
                phase=s.phase / 360,
                ref_time_mu=s.phase_ref_time)

            if s.bichro_enable:
                self.dds_729_SP.set(freq_blue, amplitude=s.amp_blue, ref_time_mu=s.phase_ref_time)
                self.dds_729_SP.set_att(s.att_blue)
                self.dds_729_SP_bichro.set(freq_red, amplitude=s.amp_red, ref_time_mu=s.phase_ref_time)
                self.dds_729_SP_bichro.set_att(s.att_red)

                self.start_noisy_single_pass(s.phase_ref_time,
                    freq_noise=s.use_single_pass_freq_noise,
                    freq_sp=freq_blue, amp_sp=s.amp_blue, att_sp=s.att_blue,
                    use_bichro=True,
                    freq_sp_bichro=freq_red, amp_sp_bichro=s.amp_red, att_sp_bichro=s.att_red)

                if s.AC_stark_local:
                    offset_L1 = self.get_offset_frequency("729L1")
                    dp_freq2 = self.calc_frequency(
                        s.line_selection,
                        detuning=s.carrier_detuning_L1,
                        dds="729L1"
                    )
                    self.dds_729L1.set(dp_freq2,
                        amplitude=s.car_amp_L1,
                        phase=s.phase / 360,
                        ref_time_mu=s.phase_ref_time)
                    
                    self.dds_729L1_SP.set(80*MHz+offset_L1, amplitude=s.sp_amp_729L1, ref_time_mu=s.phase_ref_time)
                    self.dds_729L1_SP.set_att(s.sp_att_729L1)
                    
                    self.dds_729.set(dp_freq,
                            amplitude=s.car_amp,
                            phase=s.phase / 360,
                            ref_time_mu=s.phase_ref_time)
                    self.dds_729.set_att(s.car_att)

                    with parallel:
                        self.dds_729.sw.on()
                        self.dds_729_SP.sw.on()
                        self.dds_729L1.sw.on()
                        self.dds_729L1_SP.sw.on()
                    delay(s.duration)
                    with parallel:
                        self.dds_729.sw.off()
                        #self.dds_729.sw.off()
                        self.dds_729L1.sw.off()
                        self.dds_729L1_SP.sw.off()


                else:

                    if s.use_ramping:
                        self.execute_pulse_with_amplitude_ramp(
                            dds1_att=s.att,
                            dds1_freq=dp_freq)
                    else:
                        self.dds_729.set(dp_freq,
                            amplitude=s.car_amp,
                            phase=s.phase / 360,
                            ref_time_mu=s.phase_ref_time)
                        self.dds_729.set_att(s.car_att)
                        self.dds_729.sw.on()
                        # self.dds_729_SP.sw.on()
                        # self.dds_729_SP_bichro.sw.on()
                        delay(s.duration)
                        self.dds_729.sw.off()

                self.stop_noisy_single_pass(use_bichro=True)

            else:
                # bichro disabled
                self.dds_729.set_amplitude(b.amp)
                self.dds_729.set_att(b.att)
                sp_freq_729 = 80*MHz + offset
                self.dds_729_SP.set(sp_freq_729, amplitude=b.default_sp_amp_729, ref_time_mu=b.phase_ref_time)
                self.dds_729_SP.set_att(b.default_sp_att_729)
                with parallel:
                    self.dds_729.sw.on()
                    self.dds_729_SP.sw.on()
                delay(b.duration)
                with parallel:
                    self.dds_729.sw.off()
                    self.dds_729_SP.sw.off()
                        
        elif s.channel == "729local":
            offset = self.get_offset_frequency("729L1")
            freq_blue += offset
            freq_red += offset

            self.get_729_dds("729L1", id=0)
            dp_freq = self.calc_frequency(
                    s.line_selection,
                    detuning=s.carrier_detuning,
                    dds="729L1"
                )
            self.dds_729.set(dp_freq,
                amplitude=0.,
                phase=s.phase / 360,
                ref_time_mu=s.phase_ref_time)
        
            if s.bichro_enable:
                self.dds_729_SP.set(freq_blue, amplitude=s.amp_blue, ref_time_mu=s.phase_ref_time)
                self.dds_729_SP.set_att(s.att_blue)
                self.dds_729_SP_bichro.set(freq_red, amplitude=s.amp_red, ref_time_mu=s.phase_ref_time)
                self.dds_729_SP_bichro.set_att(s.att_red)

                self.start_noisy_single_pass(s.phase_ref_time,
                    freq_noise=s.use_single_pass_freq_noise,
                    freq_sp=freq_blue, amp_sp=s.amp_blue, att_sp=s.att_blue,
                    use_bichro=True,
                    freq_sp_bichro=freq_red, amp_sp_bichro=s.amp_red, att_sp_bichro=s.att_red)

                if b.use_ramping:
                    self.execute_pulse_with_amplitude_ramp(
                        dds1_att=s.att,
                        dds1_freq=dp_freq)
                else:
                    self.dds_729.set(dp_freq2,
                        amplitude=b.amp,
                        phase=b.phase / 360,
                        ref_time_mu=b.phase_ref_time)
                    self.dds_729.set_att(b.att)
                    self.dds_729.sw.on()
                    # self.dds_729_SP.sw.on()
                    # self.dds_729_SP_bichro.sw.on()
                    delay(b.duration)
                    self.dds_729.sw.off()

                self.stop_noisy_single_pass(use_bichro=True)