from artiq.experiment import *
import numpy as np


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


    def subsequence(self):
        s = SetupSingleIonVAET
        trap_frequency = self.get_trap_frequency(s.selection_sideband)
        offset = self.get_offset_frequency("729G")
        freq_blue = 80*MHz +trap_frequency + s.nu_eff + offset
        freq_red = 80*MHz - trap_frequency - s.nu_eff + offset
        freq_carr = 80*MHz + offset
        dp_freq = self.calc_frequency(
            s.line_selection,
            dds="729G"
        )

        # Hard-coded to 729G
        self.dds_729.set(
            dp_freq,
            amplitude=s.DP_amp,
            ref_time_mu=s.phase_ref_time
        )

        if not s.phase_implemented_sigmay:
            # Hard-coded to SP_729G
            self.dds_729_SP.set(
                freq_carr,
                amplitude=s.J_amp,
                ref_time_mu=s.phase_ref_time
            )
            if not s.delta_phase: # normal nueff
                # Hard-coded to SP_729G_bichro
                self.dds_729_SP_bichro.set(
                    freq_carr,
                    amplitude=s.delta_amp,
                    ref_time_mu=s.phase_ref_time,
                    phase=0.385  # sigma_y 0.368
                )
                #hard code noise to L1_SP_Bichro or 729 L1
                self.dds_SP_729L1_bichro.set(
                    freq_carr,
                    amplitude=s.noise_amp,
                    ref_time_mu=s.phase_ref_time,
                    phase=0.368   #0.368

                )

                # self.dds_729L1.set(
                #     freq_carr,
                #     amplitude=s.noise_amp,
                #     ref_time_mu=s.phase_ref_time,
                #     phase=0.368

                # )
            else: # negative nueff
                self.dds_729_SP_bichro.set(
                    freq_carr,
                    amplitude=s.delta_amp,
                    ref_time_mu=s.phase_ref_time,
                    phase=0.368+0.5  # sigma_y 0.551
                )

                #hard code noise to L1_SP_Bichro or 729 L1
                self.dds_SP_729L1_bichro.set(
                    freq_carr,
                    amplitude=s.noise_amp,
                    ref_time_mu=s.phase_ref_time,
                    phase=0.368+0.5

                )
                # self.dds_729L1.set(
                #     freq_carr,
                #     amplitude=s.noise_amp,
                #     ref_time_mu=s.phase_ref_time,
                #     phase=0.368+0.5

                # )

        else:
            self.dds_729_SP.set(
                freq_carr,
                amplitude=s.implemented_amp,
                ref_time_mu=s.phase_ref_time,
                phase=s.implemented_phase
            )

            self.dds_729_SP_bichro.set(
                freq_carr,
                amplitude=0.0,
                ref_time_mu=s.phase_ref_time,
            )

        # Hard-coded to SP_729L2
        self.dds_729_SP_line1_bichro.set(
            freq_blue,
            amplitude=s.BSB_amp,
            ref_time_mu=s.phase_ref_time,
            phase=0.75
        )

        # Hard-coded to SP_729L2_bicrho
        self.dds_729_SP_line2_bichro.set(
            freq_red,
            amplitude=s.RSB_amp,
            ref_time_mu=s.phase_ref_time,
            phase=0.25
        )

        self.dds_729.set_att(s.DP_att)
        self.dds_729_SP.set_att(s.J_att)
        self.dds_729_SP_bichro.set_att(s.delta_att)
        self.dds_SP_729L1_bichro.set_att(s.noise_att)
        #self.dds_729L1.set_att(s.noise_att)
        self.dds_729_SP_line1_bichro.set_att(s.BSB_att)
        self.dds_729_SP_line2_bichro.set_att(s.RSB_att)

        with parallel:
            self.dds_729.sw.on()
            self.dds_729_SP.sw.on()
            self.dds_729_SP_bichro.sw.on()
            self.dds_SP_729L1_bichro.sw.on()
            #self.dds_729L1.sw.on()
            self.dds_729_SP_line1_bichro.sw.on()
            self.dds_729_SP_line2_bichro.sw.on()
        delay(s.duration)
        with parallel:
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
            self.dds_729_SP_bichro.sw.off()
            self.dds_SP_729L1_bichro.sw.off()
            #self.dds_729L1.sw.off()
            self.dds_729_SP_line1_bichro.sw.off()
            self.dds_729_SP_line2_bichro.sw.off()