from artiq.experiment import *


class OpticalPumpingContinuous:
    frequency_866="DopplerCooling.doppler_cooling_frequency_866"
    amplitude_866="DopplerCooling.doppler_cooling_amplitude_866"
    att_866="DopplerCooling.doppler_cooling_att_866"
    frequency_854="OpticalPumping.optical_pumping_frequency_854"
    amplitude_854="OpticalPumping.optical_pumping_amplitude_854"
    att_854="OpticalPumping.optical_pumping_att_854"
    line_selection="OpticalPumping.line_selection"
    channel_729="StatePreparation.channel_729"
    duration="OpticalPumpingContinuous.optical_pumping_continuous_duration"
    rempump_duration="OpticalPumpingContinuous.optical_pumping_continuous_repump_additional"
    amplitude_729="OpticalPumping.amplitude_729"
    att_729="OpticalPumping.att_729"

    def subsequence(self):
        self.get_729_dds(OpticalPumpingContinuous.channel_729)
        self.dds_866.set(OpticalPumpingContinuous.frequency_866,
                         amplitude=OpticalPumpingContinuous.amplitude_866)
        self.dds_866.set_att(OpticalPumpingContinuous.att_866)
        self.dds_854.set(OpticalPumpingContinuous.frequency_854,
                         amplitude=OpticalPumpingContinuous.amplitude_854)
        self.dds_854.set_att(OpticalPumpingContinuous.att_854)
        freq_729 = self.calc_frequency(
            OpticalPumpingContinuous.line_selection,
            dds=OpticalPumpingContinuous.channel_729
        )
        self.dds_729.set(freq_729, 
                         amplitude=OpticalPumpingContinuous.amplitude_729)
        self.dds_729.set_att(OpticalPumpingContinuous.att_729)
        with parallel:
            self.dds_866.sw.on()
            self.dds_854.sw.on()
            self.dds_729.sw.on()
            self.dds_729_SP.sw.on()
        delay(OpticalPumpingContinuous.duration)
        with parallel:
            self.dds_729.sw.off()
            self.dds_729_SP.sw.off()
        delay(2 * OpticalPumpingContinuous.rempump_duration)
        with parallel:
            self.dds_854.sw.off()
            self.dds_866.sw.off()

