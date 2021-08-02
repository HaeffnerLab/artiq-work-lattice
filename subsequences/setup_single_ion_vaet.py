from artiq.experiment import *
import numpy as np
from artiq.coredevice.ad9910 import (
        PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING, 
        RAM_MODE_RAMPUP
    )



class SetupSingleIonVAET:
    DP_amp="SingleIonVAET.DP_amp"
    DP_att="SingleIonVAET.DP_att"
    CARR_amp="SingleIonVAET.CARR_amp"
    CARR_att="SingleIonVAET.CARR_att"
    CARR_phase="SingleIonVAET.CARR_phase"
    RSB_amp="SingleIonVAET.RSB_amp"
    RSB_att="SingleIonVAET.RSB_att"
    BSB_amp="SingleIonVAET.BSB_amp"
    BSB_att="SingleIonVAET.BSB_att"
    line_selection="SingleIonVAET.line_selection"
    selection_sideband="SingleIonVAET.selection_sideband"
    nu_eff="SingleIonVAET.nu_eff"
    duration="SingleIonVAET.duration"
    with_noise="SingleIonVAET.with_noise"
    noise_type="SingleIonVAET.noise_type"
    test_phase="SingleIonVAET.test_phase"
    amplitude_noise=False
    phase_ref_time=np.int64(-1)
    freq_blue=0.
    freq_red=0.
    step=1
    mod_wf=[[np.int32(0)]] 
    mod_wf2=[[np.int32(0)]]

    def subsequence(self):
        phase_mode = PHASE_MODE_ABSOLUTE
        s = SetupSingleIonVAET
        offset = self.get_offset_frequency("729G")
        freq_carr = 80*MHz + offset
        dp_freq = self.calc_frequency(
                                    s.line_selection,
                                    dds="729G"
                                )

        # DP is hard-coded to 729G
        self.dds_729.set(
                dp_freq,
                amplitude=s.DP_amp,
                phase_mode=phase_mode,
                # ref_time_mu=s.phase_ref_time
            )
        
        if not s.with_noise or not s.amplitude_noise:
            self.dds_729_SP.set(
                    freq_carr,
                    amplitude=s.CARR_amp,
                    # ref_time_mu=s.phase_ref_time,
                    phase_mode=phase_mode,
                    phase=s.CARR_phase
                )
        if s.with_noise and s.amplitude_noise:
            self.dds_729_SP.set_frequency(freq_carr)
            self.dds_729_SP.set_phase_mode(phase_mode)

        if not s.with_noise or s.amplitude_noise:
            # Hard-coded to SP_729G_bichro
            self.dds_SP_729G_bichro.set(
                    s.freq_blue,
                    amplitude=s.BSB_amp,
                    # ref_time_mu=s.phase_ref_time,
                    phase_mode=phase_mode,
                    phase=0.25
                )

            # Hard-coded to SP_729L2
            self.dds_SP_729L2.set(
                    s.freq_red,
                    amplitude=s.RSB_amp,
                    phase_mode=phase_mode,
                    # ref_time_mu=s.phase_ref_time,
                    phase=-0.25
                )
        
        if s.with_noise and not s.amplitude_noise:
            self.dds_SP_729G.set_phase_mode(phase_mode)
            self.dds_SP_729G_bichro.set_amplitude(s.BSB_amp)
            self.dds_SP_729G_bichro.set_phase(0.75)
            self.dds_SP_729L2.set_phase_mode(phase_mode)
            self.dds_SP_729L2.set_amplitude(s.RSB_amp)
            self.dds_SP_729L2.set_phase(0.25)

        self.dds_729.set_att(s.DP_att)
        self.dds_729_SP.set_att(s.CARR_att)
        self.dds_SP_729G_bichro.set_att(s.BSB_att)
        self.dds_SP_729L2.set_att(s.RSB_att)
        self.dds_test1.set(freq_carr, 
            amplitude=1.0, phase_mode=phase_mode, phase=s.test_phase)
        self.dds_test1.set_att(5.)  # for beat note
        self.dds_test2.set(freq_carr, 
            amplitude=1.0, phase_mode=phase_mode, phase=s.test_phase + 0.25)
        self.dds_test2.set_att(5.)  # for beat note

        self.dds_729.sw.on()
        with parallel:
            self.trigger.on()
            self.dds_test1.sw.on()  # for beat note
            self.dds_test2.sw.on()  # for beat note
            self.dds_729_SP.cpld.io_update.pulse_mu(8)
            self.dds_SP_729G_bichro.cpld.io_update.pulse_mu(8)
            self.dds_SP_729L2.cpld.io_update.pulse_mu(8)
            self.dds_729_SP.sw.on()
            self.dds_SP_729G_bichro.sw.on()
            self.dds_SP_729L2.sw.on()
        
        delay(s.duration)
        
        with parallel:
            self.trigger.off()
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
            self.dds_SP_729G_bichro.sw.off()
            self.dds_SP_729L2.sw.off()
            self.dds_test1.sw.off()  # for beat note
            self.dds_test2 .sw.off()  # for beat note

        self.dds_729.set_cfr1()
        delay(10*us)
        self.dds_729_SP.set_cfr1()
        delay(10*us)
        self.dds_SP_729G_bichro.set_cfr1()
        delay(10*us)
        self.dds_SP_729L2.set_cfr1()
        delay(10*us)
