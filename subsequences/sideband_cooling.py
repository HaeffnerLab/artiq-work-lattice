from artiq.experiment import *


class SidebandCooling():
    line_selection=
    selection_sideband=
    order=
    stark_shift=
    channel_729=
    repump_additional=


    def subsequence(self):
        if SidebandCooling.channel_729 == "729L1":
            dds_729 = self.dds_729L1
            dds_729_SP = self.dds_SP_729L1
        elif SidebandCooling.channel_729 == "729L2":
            dds_729 = self.dds_729L2
            dds_729_SP = self.dds_SP_729L2
        elif SidebandCooling.channel_729 == "729G":
            dds_729 = self.dds_729G
            dds_729_SP = self.dds_SP_729G
        else:
            dds_729 = self.dds_729G
            dds_729_SP = self.dds_SP_729G 