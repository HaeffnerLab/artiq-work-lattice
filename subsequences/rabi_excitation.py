from artiq.experiment import *


class RabiExcitation():
    freq_729="Excitation_729.rabi_excitation_frequency"
    amp_729="Excitation_729.rabi_excitation_amplitude"
    att_729="Excitation_729.rabi_excitation_att"
    phase_729="Excitation_729.rabi_excitation_phase"
    channel_729="Excitation_729.channel_729"
    duration="Excitation_729.rabi_excitation_duration"
    line_selection="Excitation_729.line_selection"

    def subsequence(self):
        self.core.wait_until_mu(now_mu())
        if RabiExcitation.channel_729 == "729L1":
            dds_729 = self.dds_729L1
            dds_729_SP = self.dds_SP_729L1
        elif RabiExcitation.channel_729 == "729L2":
            dds_729 = self.dds_729L2
            dds_729_SP = self.dds_SP_729L2
        elif RabiExcitation.channel_729 == "729G":
            dds_729 = self.dds_729G
            dds_729_SP = self.dds_SP_729G
        else:
            dds_729 = self.dds_729G
            dds_729_SP = self.dds_SP_729G

        dds_729.set(RabiExcitation.freq_729, amplitude=RabiExcitation.amp_729,
                    phase=RabiExcitation.phase_729)
        dds_729.set_att(RabiExcitation.att_729)
        with parallel:
            dds_729.sw.on()
            dds_729_SP.sw.on()
        delay(RabiExcitation.duration)
        with parallel:
            dds_729.sw.off()
            dds_729_SP.sw.off()
        self.core.wait_until_mu(now_mu())