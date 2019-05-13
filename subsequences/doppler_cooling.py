from artiq.experiment import *


class DopplerCooling(EnvExperiment):
    kernel_invariants = {
        "duration",
        "additional_repump_duration",
        "frequency_397",
        "amplitude_397",
        "att_397",
        "frequency_866",
        "amplitude_866",
        "att_866"
    }
    
    duration="DopplerCooling.doppler_cooling_duration"
    additional_repump_duration="DopplerCooling.doppler_cooling_repump_additional"
    frequency_397="DopplerCooling.doppler_cooling_frequency_397"
    amplitude_397="DopplerCooling.doppler_cooling_amplitude_397"
    att_397="DopplerCooling.doppler_cooling_att_397"
    frequency_866="DopplerCooling.doppler_cooling_frequency_866"
    amplitude_866="DopplerCooling.doppler_cooling_amplitude_866"
    att_866="DopplerCooling.doppler_cooling_att_866"

    def subsequence(self):
        delay(400*us)
        self.dds_397.set(DopplerCooling.frequency_397, amplitude=DopplerCooling.amplitude_397)
        self.dds_397.set_att(DopplerCooling.att_397)
        self.dds_866.set(DopplerCooling.frequency_866, amplitude=DopplerCooling.amplitude_866)
        self.dds_866.set_att(DopplerCooling.att_866)
        with parallel:
            self.dds_397.sw.on()
            self.dds_866.sw.on()
        delay(DopplerCooling.duration)
        self.dds_397.sw.off()
        delay(DopplerCooling.additional_repump_duration)
        self.dds_866.sw.off()