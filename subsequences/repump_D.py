from artiq.experiment import *
from artiq.pulse_sequence import PulseSequence

class RepumpD(EnvExperiment):
    duration="RepumpD_5_2.repump_d_duration"
    frequency_854="RepumpD_5_2.repump_d_frequency_854"
    amplitude_854="RepumpD_5_2.repump_d_amplitude_854"
    att_854="RepumpD_5_2.repump_d_att_854"
    frequency_866="DopplerCooling.doppler_cooling_frequency_866"
    amplitude_866="DopplerCooling.doppler_cooling_amplitude_866"
    att_866="DopplerCooling.doppler_cooling_att_866"
    
    def subsequence(self):
        pass
        # self.dds_854.init()
        # self.dds_866.init()
        delay(500*us)
        self.dds_854.set(RepumpD.frequency_854, amplitude=RepumpD.amplitude_854)
        self.dds_854.set_att(RepumpD.att_854)
        self.dds_866.set(RepumpD.frequency_866, amplitude=RepumpD.amplitude_866)
        self.dds_866.set_att(RepumpD.att_866)
        with parallel:
            self.dds_854.sw.on()
            self.dds_866.sw.on()
        delay(RepumpD.duration)
        with parallel:
            self.dds_854.sw.off()
            self.dds_866.sw.off()




