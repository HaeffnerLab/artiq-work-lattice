from artiq.experiment import *
import numpy as np


class SetupSingleIonVAET:
    DP_amp="SingleIonVAET.DP_amp"
    DP_att="SingleIonVAET.DP_att"
    J_amp="SingleIonVAET.J_amp"
    J_att="SingleIonVAET.J_att"
    Δ_amp="SingleIonVAET.Δ_amp"
    Δ_att="SingleIonVAET.Δ_att"
    RSB_amp="SingleIonVAET.RSB_amp"
    RSB_att="SingleIonVAET.RSB_att"
    BSB_amp="SingleIonVAET.BSB_amp"
    BSB_att="SingleIonVAET.BSB_att"
    line_selection="SingleIonVAET.line_selection"
    selection_sideband="SingleIonVAET.selection_sideband"
    ν_eff="SingleIonVAET.ν_eff"
    duration="SingleIonVAET.duration"
    phase_ref_time=np.int64(-1)


    def subsequence(self):
        s = SetupSingleIonVAET
        trap_frequency = self.get_trap_frequency(s.selection_sideband)
        offset = self.get_offset_frequency("729G")
        freq_blue = 80*MHz + trap_frequency - s.ν_eff/2 + offset
        freq_red = 80*MHz - trap_frequency + s.ν_eff/2 + offset
        freq_carr = 80*MHz + offset
        dp_freq = self.calc_frequeny(
            s.line_selection,
            dds="729G"
        )

        # Hard-coded to 729G
        self.dds_729.set(
            dp_freq,
            amplitude=s.DP_amp,
            ref_time_mu=s.phase_ref_time
        )

        # Hard-coded to SP_729G
        self.dds_729_SP.set(
            freq_carr,
            amplitude=s.J_amp,
            ref_time_mu=s.phase_ref_time
        )

        # Hard-coded to SP_729G_bichro
        self.dds_729_SP_bichro.set(
            freq_carr,
            amplitude=s.Δ_amp,
            ref_time_mu=s.phase_ref_time,
            phase=0.25  # sigma_y
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
        self.dds_729_SP_bichro.set_att(s.Δ_att)
        self.dds_729_SP_line1_bichro.set_att(s.BSB_att)
        self.dds_729_SP_line2_bichro.set_att(s.RSB_att)

        with parallel:
            self.dds_729.sw.on()
            self.dds_729_SP.sw.on()
            self.dds_729_SP_bichro.sw.on()
            self.dds_729_SP_line1_bichro.sw.on()
            self.dds_729_SP_line2_bichro.sw.on()
        delay(s.duration)
        self.dds_729.sw.off()