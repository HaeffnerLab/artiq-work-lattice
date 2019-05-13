from artiq.experiment import *


class RabiExcitation():
    freq_729="Excitation_729.rabi_excitation_frequency"
    amp_729="Excitation_729.rabi_excitation_amplitude"
    att_729="Excitation_729.rab_excitation_att"
    phase_729="Excitation_729.rabi_excitation_phase"
    channel_729="Excitation_729.channel_729"
    duration="Excitation_729.rabi_excitation_duration"

    def subsequence(self):
        if RabiExcitation.channel_729 == "729L1":
            dds_729 = self.dds_729L1
        elif RabiExcitation.channel_729 == "729L2":
            dds_729 = self.dds_729L2
        elif RabiExcitation.channel_729 == "729G":
            dds_729 = self.dds_729G
        else:
            dds_729 = self.dds_729G