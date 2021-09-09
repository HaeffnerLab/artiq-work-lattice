from artiq.experiment import *
from artiq.coredevice.ad9910 import (
        RAM_DEST_ASF, RAM_DEST_FTW, RAM_MODE_BIDIR_RAMP,
        RAM_MODE_CONT_RAMPUP, RAM_MODE_RAMPUP, PHASE_MODE_ABSOLUTE,
        PHASE_MODE_CONTINUOUS, PHASE_MODE_TRACKING, RAM_MODE_CONT_BIDIR_RAMP
    )
import numpy as np

class RAPTest(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.amp_dds = self.get_device("RAP_amp")
        self.freq_dds = self.get_device("RAP_freq")
        self.trigger = self.get_device("trigger")

    def run(self):
        n = 1023
        m = 1024 - n
        T = 500*us
        t_dds = 5*ns
        T = np.ceil(T / (n * t_dds)) * t_dds * 1024
        self.T = T
        self.f_amp = 400*MHz
        self.f_freq = 320*MHz
        sigma = 0.3 * T / np.sqrt(8)
        self.amp_profile_raw = 0.1 * np.sin([0 for i in range(m)] + [np.pi/2  + np.pi * t / (2 * n) for t in range(n-m)])
        # self.amp_profile_raw = [1.0 if i>100 else 0 for i in range(n)]
        self.freq_profile_raw = [0 for i in range(m)] + [self.f_freq + 500e3 * np.cos(np.pi * t / (2 * n)) for t in range(n-m)]
        # self.amp_profile_raw = np.flip(self.amp_profile_raw)
        self.freq_profile_raw = np.flip(self.freq_profile_raw)
        self.amp_profile = [0] * n
        self.freq_profile = [0] * n
        self.step = int((self.T / n) / t_dds / 2)
        print(self.step)
        print(self.step * n * t_dds)
        print("length: ", len(self.amp_profile_raw))
        self.krun()

    @kernel
    def krun(self):
        self.amp_dds.amplitude_to_ram(self.amp_profile_raw, self.amp_profile)
        self.amp_dds.frequency_to_ram(self.freq_profile_raw, self.freq_profile)
        self.core.reset()
        self.amp_dds.cpld.init()
        self.freq_dds.cpld.init()
        self.amp_dds.init()
        self.freq_dds.init()

        self.amp_dds.set_cfr1(ram_enable=0)
        self.amp_dds.cpld.set_profile(0)
        self.freq_dds.set_cfr1(ram_enable=0)
        self.freq_dds.cpld.set_profile(0)

        self.amp_dds.set_profile_ram(
                    start=0,
                    end=len(self.amp_profile) - 1,
                    step=self.step,
                    profile=0,
                    mode=RAM_MODE_CONT_BIDIR_RAMP
        )
        self.amp_dds.cpld.set_profile(0)
        self.amp_dds.cpld.io_update.pulse_mu(8)
        self.amp_dds.write_ram(self.amp_profile)
        delay(1*ms)
        self.amp_dds.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_ASF,
                    phase_autoclear=1
        )
        self.amp_dds.cpld.io_update.pulse_mu(8)
        self.amp_dds.set_frequency(self.f_amp)
        self.amp_dds.set_att(0.0)

        self.freq_dds.set_profile_ram(
                    start=0,
                    end=len(self.freq_profile) - 1,
                    step=self.step * 2,
                    profile=0,
                    mode=RAM_MODE_CONT_RAMPUP
        )
        self.freq_dds.cpld.set_profile(0)
        self.freq_dds.cpld.io_update.pulse_mu(8)
        self.freq_dds.write_ram(self.freq_profile)
        delay(1*ms)
        self.freq_dds.set_cfr1(
                    ram_enable=1,
                    ram_destination=RAM_DEST_FTW,
                    phase_autoclear=1,
                    manual_osk_external=0,
                    osk_enable=1,
                    select_auto_osk=0
        )
        self.freq_dds.cpld.io_update.pulse_mu(8)
        self.freq_dds.set_amplitude(1.0)
        self.freq_dds.set_att(0.0)

        self.core.break_realtime()
        while True:
            delay(10*ms)
            with parallel:
                self.trigger.on()
                self.amp_dds.cpld.io_update.pulse_mu(8)
                # self.freq_dds.cpld.io_update.pulse_mu(8)
                self.amp_dds.sw.on()
                self.freq_dds.sw.on()
            delay(self.T)
            with parallel:
                self.trigger.off()
                self.amp_dds.sw.off()
                self.freq_dds.sw.off()
