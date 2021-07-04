from artiq.experiment import *
import numpy as np
from artiq.coredevice.ad9910 import (
        PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING, 
        RAM_MODE_RAMPUP
    )



class SetupSingleIonVAET:
    DP_amp="SingleIonVAET.DP_amp"
    DP_att="SingleIonVAET.DP_att"
    J_amp="SingleIonVAET.J_amp"
    J_att="SingleIonVAET.J_att"
    delta_amp="SingleIonVAET.delta_amp"
    delta_att="SingleIonVAET.delta_att"
    delta_phase = "SingleIonVAET.delta_phase"
    noise_amp="SingleIonVAET.noise_amp"
    noise_att="SingleIonVAET.noise_att"
    RSB_amp="SingleIonVAET.RSB_amp"
    RSB_att="SingleIonVAET.RSB_att"
    BSB_amp="SingleIonVAET.BSB_amp"
    BSB_att="SingleIonVAET.BSB_att"
    line_selection="SingleIonVAET.line_selection"
    selection_sideband="SingleIonVAET.selection_sideband"
    nu_eff="SingleIonVAET.nu_eff"
    duration="SingleIonVAET.duration"
    phase_implemented_sigmay="SingleIonVAET.phase_implemented_sigmay"
    J="SingleIonVAET.measured_J"
    delta="SingleIonVAET.phase_implemented_delta"
    phase_ref_time=np.int64(-1)
    implemented_phase=0.
    implemented_amp=0.
    test_phase="SingleIonVAET.test_phase"
    freq_blue=0.
    freq_red=0.
    with_noise="SingleIonVAET.with_noise"
    noise_type="SingleIonVAET.noise_type"
    step=1


    def subsequence(self):
        phase_mode = PHASE_MODE_ABSOLUTE
        s = SetupSingleIonVAET
        offset = self.get_offset_frequency("729G")
        freq_carr = 80*MHz + offset
        dp_freq = self.calc_frequency(
                s.line_selection,
                dds="729G"
            )

        # Hard-coded to 729G
        self.dds_729.set(
                dp_freq,
                amplitude=s.DP_amp,
                phase_mode=phase_mode,
                ref_time_mu=s.phase_ref_time
            )

        if not s.phase_implemented_sigmay:
            return
            # # Hard-coded to SP_729G
            # self.dds_729_SP.set(
            #         freq_carr,
            #         amplitude=s.J_amp,
            #         phase_mode=phase_mode,
            #         ref_time_mu=s.phase_ref_time,
            #         phase=0.0
            #     )
            # if not s.delta_phase: # normal nueff
            #     # Hard-coded to SP_729G_bichro
            #     self.dds_729_SP_bichro.set(
            #             freq_carr,
            #             amplitude=s.delta_amp,
            #             phase_mode=phase_mode,
            #             ref_time_mu=s.phase_ref_time,
            #             phase=0.25  # sigma_y 0.381
            #         )
            #     #hard code noise to L1_SP
            #     self.dds_SP_729L1.set(
            #             freq_carr,
            #             amplitude=s.noise_amp,
            #             phase_mode=phase_mode,
            #             ref_time_mu=s.phase_ref_time,
            #             phase=s.test_phase / 360 #0.25   #0.381
            #         )

            # else: # negative nueff
            #     self.dds_729_SP_bichro.set(
            #             freq_carr,
            #             amplitude=s.delta_amp,
            #             phase_mode=phase_mode,
            #             ref_time_mu=s.phase_ref_time,
            #             phase=0.381+0.5  # sigma_y 0.551
            #         )

            #     #hard code noise to L1_SP_Bichro or 729 L1
            #     self.dds_SP_729L1.set(
            #             freq_carr,
            #             amplitude=s.noise_amp,
            #             phase_mode=phase_mode,
            #             ref_time_mu=s.phase_ref_time,
            #             phase=0.381+0.5
            #         )

        else:
            self.dds_729_SP.set(
                    freq_carr,
                    amplitude=s.implemented_amp,
                    ref_time_mu=s.phase_ref_time,
                    phase_mode=phase_mode,
                    phase=s.implemented_phase
                )

        # Hard-coded to SP_729G_bichro
        self.dds_SP_729G_bichro.set(
                s.freq_blue,
                amplitude=s.BSB_amp,
                ref_time_mu=s.phase_ref_time,
                phase_mode=phase_mode,
                phase=0.75
            )

        # Hard-coded to SP_729L1
        self.dds_SP_729L1.set(
                s.freq_red,
                amplitude=s.RSB_amp,
                phase_mode=phase_mode,
                ref_time_mu=s.phase_ref_time,
                phase=0.25
            )

        self.dds_729.set_att(s.DP_att)
        self.dds_729_SP.set_att(s.J_att)
        self.dds_729_SP_bichro.set_att(s.delta_att)
        self.dds_SP_729L1.set_att(s.noise_att)
        # self.dds_729n_SP_line1_bichro.set_att(s.BSB_att)
        # self.dds_729_SP_line2_bichro.set_att(s.RSB_att)

        # if s.with_noise:
        #     j = round(self.get_variable_parameter("current_experiment_iteration"))
        #     if s.noise_type == "white_delta" or s.noise_type == "lorentzian_delta":
        #         self.setup_ram_modulation(
        #                             0,  # hard coded to self.dds_729_SP
        #                             modulation_waveform=list(self.mod_wf1[j]),
        #                             modulation_waveform2=list(self.mod_wf2[j]),
        #                             modulation_type="phase_and_amp",
        #                             step=s.step,
        #                             ram_mode=RAM_MODE_RAMPUP
        #                         )
        #     else:
        #         self.setup_ram_modulation(
        #                             1,  # hard coded to self.dds_SP_729G_bichro
        #                             modulation_waveform=list(self.mod_wf1[j]),
        #                             modulation_type="frequency",
        #                             step=s.step,
        #                             ram_mode=RAM_MODE_RAMPUP
        #                         )
        #         self.setup_ram_modulation(
        #                             2,  # hard coded to self.dds_SP_729L1
        #                             modulation_waveform=list(self.mod_wf2[j]),
        #                             modulation_type="frequency",
        #                             step=s.step,
        #                             ram_mode=RAM_MODE_RAMPUP
        #                         )   


        self.dds_729.sw.on()
        with parallel:
            self.dds_729_SP.cpld.io_update.pulse_mu(8)
            self.dds_729_SP_bichro.cpld.io_update.pulse_mu(8)
            self.dds_SP_729L1.cpld.io_update.pulse_mu(8)
            self.dds_729_SP.sw.on()
            self.dds_729_SP_bichro.sw.on()
            self.dds_SP_729L1.sw.on()
            # self.dds_729_SP_line1_bichro.sw.on()
            # self.dds_729_SP_line2_bichro.sw.on()
        
        delay(s.duration)
        
        with parallel:
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
            self.dds_729_SP_bichro.sw.off()
            self.dds_SP_729L1.sw.off()
            # self.dds_729_SP_line1_bichro.sw.off()
            # self.dds_729_SP_line2_bichro.sw.off()
