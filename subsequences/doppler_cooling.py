from artiq.experiment import *


class DopplerCooling:
    duration="DopplerCooling.doppler_cooling_duration"
    additional_repump_duration="DopplerCooling.doppler_cooling_repump_additional"
    pre_duration="DopplerCooling.pre_duration"
    frequency_397="DopplerCooling.doppler_cooling_frequency_397"
    amplitude_397="DopplerCooling.doppler_cooling_amplitude_397"
    att_397="DopplerCooling.doppler_cooling_att_397"
    frequency_866="DopplerCooling.doppler_cooling_frequency_866"
    amplitude_866="DopplerCooling.doppler_cooling_amplitude_866"
    att_866="DopplerCooling.doppler_cooling_att_866"
    # recrystallize_pulse="DopplerCooling.recrystallize_pulse"

    def subsequence(self):
        d = DopplerCooling
        self.dds_397.set(d.frequency_397, amplitude=d.amplitude_397)
        self.dds_397.set_att(d.att_397)
        self.dds_866.set(d.frequency_866, amplitude=d.amplitude_866)
        self.dds_866.set_att(d.att_866)
        with parallel:
            self.dds_397.sw.on()
            self.dds_866.sw.on()
        # if d.recrystallize_pulse:
        #     self.dds_397.set(60*MHz, amplitude=1.0)
        #     delay(d.pre_duration)
        delay(d.duration)
        self.dds_397.sw.off()
        delay(10*us)
        self.dds_866.sw.off()