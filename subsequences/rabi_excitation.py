from artiq.experiment import *


class RabiExcitation:
    freq_729="Excitation_729.rabi_excitation_frequency"
    amp_729="Excitation_729.rabi_excitation_amplitude"
    att_729="Excitation_729.rabi_excitation_att"
    phase_729="Excitation_729.rabi_excitation_phase"
    channel_729="Excitation_729.channel_729"
    duration="Excitation_729.rabi_excitation_duration"
    line_selection="Excitation_729.line_selection"

    def subsequence(self):
        r = RabiExcitation
        self.get_729_dds(r.channel_729)
        self.dds_729.set(r.freq_729, amplitude=r.amp_729,
                    phase=r.phase_729 / 360)
        self.dds_729.set_att(r.att_729)
        with parallel:
            self.dds_729.sw.on()
            self.dds_729_SP.sw.on()
        delay(r.duration)
        with parallel:
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
